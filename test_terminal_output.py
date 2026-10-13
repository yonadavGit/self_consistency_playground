import contextlib
import io
import unittest
from unittest.mock import patch
import terminal_output
from main import print_sample


class TerminalTests(unittest.TestCase):
    def tearDown(self):
        terminal_output.configure(False)

    def test_literal_response_and_error_are_not_rich_markup(self):
        if terminal_output.Console is None:
            self.skipTest('Rich is optional')
        sample = {'index': 1, 'seed': 42, 'status': 'valid', 'elapsed_seconds': 1,
                  'answer': '[red]literal[/red]',
                  'raw_response': {'message': {'content': 'Reason [bold]literal[/bold]\nFINAL: [red]literal[/red]'}},
                  'logprob_error': '[link=bad]unavailable[/link]'}
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            print_sample(sample, 1, verbose=True)
        output = stream.getvalue()
        self.assertIn('[bold]literal[/bold]', output)
        self.assertIn('[red]literal[/red]', output)
        self.assertIn('[link=bad]unavailable[/link]', output)
        self.assertNotIn('\x1b[', output)

    def test_plain_mode_uses_original_output(self):
        terminal_output.configure(True)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            print_sample({'index': 1, 'seed': 42, 'status': 'valid', 'elapsed_seconds': 1,
                          'answer': '40', 'raw_response': {'message': {'content': 'FINAL: 40'}}}, 1, True)
        self.assertIn('FULL RESPONSE', stream.getvalue())
        self.assertNotIn('╭', stream.getvalue())

    def test_prompt_is_literal_in_rich_and_plain(self):
        for plain in (False, True):
            terminal_output.configure(plain)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                terminal_output.request_details({'model': 'test', 'messages': [
                    {'role': 'user', 'content': 'Question: [red]literal[/red]\nFINAL: <answer>'}]})
            self.assertIn('[red]literal[/red]', stream.getvalue())
            self.assertIn('FINAL: <answer>', stream.getvalue())

    def test_identical_prompts_print_once_per_run(self):
        terminal_output.configure(True)
        stream = io.StringIO()
        request = {'messages': [{'role': 'user', 'content': 'Unique shared prompt'}]}
        with contextlib.redirect_stdout(stream):
            terminal_output.request_details(request)
            terminal_output.request_details(request)
            terminal_output.request_details({'messages': [{'role': 'user', 'content': 'Changed critique'}]})
        self.assertEqual(stream.getvalue().count('Unique shared prompt'), 1)
        self.assertIn('Changed critique', stream.getvalue())
        terminal_output.configure(True)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            terminal_output.request_details(request)
        self.assertIn('Unique shared prompt', stream.getvalue())

    def test_logprob_ranking_order_exclusions_and_duplicates(self):
        samples = [{'index': i, 'status': 'valid', 'answer': answer,
                    'logprob_metrics': {'mean_token_logprob': score, 'token_count': 10}}
                   for i, answer, score in [(1, 'Low', -2), (2, 'High', -.1), (3, 'High', -.2),
                                             (4, 'Invalid', float('nan'))]]
        samples.append({'index': 5, 'status': 'valid', 'answer': 'Unscored'})
        samples.append(dict(samples[0], index=6, answer='Partial', refinement={'complete': False}))
        for plain in (True, False):
            terminal_output.configure(plain)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                terminal_output.logprob_ranking(samples)
            output = stream.getvalue()
            self.assertLess(output.index('High'), output.index('Low'))
            self.assertEqual(output.count('High'), 3)  # two rows plus “Higher” caption
            self.assertIn('3 ranked / 6 samples', output)
            self.assertNotIn('Partial', output)
            self.assertNotIn('Unscored |', output)

    def test_logprob_ranking_absent_or_unavailable(self):
        terminal_output.configure(True)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            terminal_output.logprob_ranking([])
        self.assertEqual(stream.getvalue(), '')
        with contextlib.redirect_stdout(stream):
            terminal_output.logprob_ranking([], enabled=True)
        self.assertIn('No eligible scored answers', stream.getvalue())

    def test_missing_rich_falls_back(self):
        with patch.object(terminal_output, 'Console', None):
            self.assertFalse(terminal_output.generation({}, 'Example'))
            self.assertFalse(terminal_output.summary({}))


if __name__ == '__main__':
    unittest.main()
