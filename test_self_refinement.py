import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import main


def response(text, done_reason='stop'):
    return {'done': True, 'done_reason': done_reason, 'message': {'content': text}}


class RefinementTests(unittest.TestCase):
    def run_cli(self, responses, flags=()):
        requests = []
        sequence = iter(responses)

        def fake_api(host, endpoint, payload, timeout):
            if endpoint == 'show':
                return {'capabilities': ['completion']}
            requests.append(payload)
            result = next(sequence)
            if isinstance(result, BaseException):
                raise result
            return result

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'run.json'
            argv = ['main.py', 'Example question?', '-n', '1', '--seed', '42',
                    '--mode', 'direct', '--output', str(output), *flags]
            with patch('sys.argv', argv), patch('main.api', fake_api), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = main.main()
            return code, json.loads(output.read_text()), requests

    def test_two_rounds_use_current_draft_and_preserve_stages(self):
        code, report, calls = self.run_cli([
            response('FINAL: A'), response('Check the name.'), response('FINAL: B'),
            response('B is correct.'), response('FINAL: B'),
        ], ['--self-refine', '2', '--verbose'])
        self.assertEqual(code, 0)
        sample = report['samples'][0]
        self.assertEqual(sample['answer'], 'B')
        self.assertEqual(sample['refinement']['initial']['answer'], 'A')
        self.assertIn('Draft answer:\nFINAL: B', calls[3]['messages'][0]['content'])
        self.assertIn('Critique:\nCheck the name.', calls[2]['messages'][0]['content'])
        self.assertEqual([c['options']['seed'] for c in calls], [42, 43, 44, 45, 46])
        self.assertEqual(sample['seed'], 42)
        self.assertEqual(sample['selected_generation_seed'], 46)
        self.assertEqual(report['initial_summary']['votes'], {'a': 1})
        self.assertEqual(report['summary']['votes'], {'b': 1})
        self.assertEqual(len(sample['refinement']['rounds']), 2)
        self.assertTrue(all(s['accepted'] for s in sample['refinement']['rounds']))

    def test_malformed_revision_retains_draft_but_excludes_incomplete_chain(self):
        code, report, calls = self.run_cli([
            response('FINAL: A'), response('Review A'), response('B without marker'),
        ], ['--self-refine', '2'])
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 3)
        self.assertEqual(report['samples'][0]['answer'], 'A')
        self.assertEqual(report['summary']['valid_samples'], 0)
        self.assertEqual(report['samples'][0]['refinement']['stop_reason'], 'revision_unparseable')

    def test_truncated_critique_stops_before_revision(self):
        code, report, calls = self.run_cli([
            response('FINAL: A'), response('Partial critique', 'length'),
        ], ['--self-refine', '1', '--critique-max-tokens', '17'])
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1]['options']['num_predict'], 17)
        self.assertEqual(report['samples'][0]['refinement']['stop_reason'], 'critique_truncated')

    def test_interrupt_preserves_completed_critique(self):
        code, report, calls = self.run_cli([
            response('FINAL: A'), response('Saved critique'), KeyboardInterrupt(),
        ], ['--self-refine', '1'])
        self.assertEqual(code, 1)
        self.assertTrue(report['interrupted'])
        self.assertFalse(report['complete'])
        step = report['samples'][0]['refinement']['rounds'][0]
        self.assertEqual(step['critique']['raw_response']['message']['content'], 'Saved critique')
        self.assertNotIn('revision', step)
        self.assertEqual(report['summary']['valid_samples'], 0)

    def test_unknown_revision_is_accepted_and_excluded_from_votes(self):
        code, report, _ = self.run_cli([
            response('FINAL: A'), response('Insufficient information.'), response('FINAL: UNKNOWN'),
        ], ['--self-refine', '1'])
        self.assertEqual(code, 1)  # completed, but no usable final vote
        self.assertEqual(report['completed_chains'], 1)
        self.assertEqual(report['samples'][0]['status'], 'abstained')
        self.assertTrue(report['samples'][0]['refinement']['rounds'][0]['accepted'])

    def test_request_failure_saved(self):
        code, report, _ = self.run_cli([
            response('FINAL: A'), RuntimeError('offline'),
        ], ['--self-refine', '1'])
        self.assertEqual(code, 1)
        self.assertEqual(report['samples'][0]['refinement']['rounds'][0]['critique']['error'], 'offline')

    def test_initial_parse_failure_can_be_repaired(self):
        code, report, _ = self.run_cli([
            response('A without final marker'), response('Use the requested format.'), response('FINAL: A'),
        ], ['--self-refine', '1', '--logprobs'])
        self.assertEqual(code, 0)
        self.assertEqual(report['initial_summary']['valid_samples'], 0)
        self.assertEqual(report['summary']['valid_samples'], 1)
        self.assertIn('logprob_error', report['samples'][0])

    def test_existing_mode_still_uses_one_call(self):
        code, report, calls = self.run_cli([response('FINAL: A')])
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(report['summary']['votes'], {'a': 1})
        self.assertNotIn('refinement', report['samples'][0])


if __name__ == '__main__':
    unittest.main()
