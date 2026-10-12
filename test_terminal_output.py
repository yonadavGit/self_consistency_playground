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

    def test_missing_rich_falls_back(self):
        with patch.object(terminal_output, 'Console', None):
            self.assertFalse(terminal_output.generation({}, 'Example'))
            self.assertFalse(terminal_output.summary({}))


if __name__ == '__main__':
    unittest.main()
