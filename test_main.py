import unittest
from main import extract, normalize, summarize
from logprob_metrics import score


class VotingTests(unittest.TestCase):
    def test_full_response_logprob(self):
        response = {'message': {'content': 'ab'}, 'logprobs': [
            {'bytes': [97], 'logprob': -0.5}, {'bytes': [98], 'logprob': -1.5}]}
        result = score(response)
        self.assertEqual(result['mean_token_logprob'], -1.0)
        self.assertEqual(result['sum_logprob'], -2.0)
        self.assertEqual(result['token_count'], 2)
        response['message']['content'] = 'mismatched'
        with self.assertRaises(ValueError):
            score(response)
        with self.assertRaises(ValueError):
            score({'message': {'content': 'ab'}})

    def test_explicit_final(self):
        self.assertEqual(extract('Maybe A, but B.\nFINAL: B'), ('Maybe A, but B.', 'B'))
        for text in ['I think B', 'FINAL: A\nFINAL: B', 'FINAL: B\nmore explanation', 'FINAL:']:
            self.assertIsNone(extract(text)[1])

    def test_aliases_and_exclusions(self):
        samples = [{'status': 'valid', 'answer': v} for v in ['Rambam', 'Maimonides.', 'Rashi']]
        samples.append({'status': 'truncated', 'answer': 'Rashi'})
        result = summarize(samples, {'rambam': 'maimonides'})
        self.assertEqual(result['majority_answer'], 'maimonides')
        self.assertEqual(result['valid_samples'], 3)
        self.assertEqual(result['winner_share_of_attempted'], 0.5)

    def test_tie_plurality_empty(self):
        def vote(values):
            return summarize([{'status': 'valid', 'answer': v} for v in values], {})
        self.assertIsNone(vote(['a', 'b'])['plurality_answer'])
        self.assertEqual(vote(['a', 'a', 'b', 'c'])['plurality_answer'], 'a')
        self.assertIsNone(vote(['a', 'a', 'b', 'c'])['majority_answer'])
        self.assertIsNone(vote([])['majority_answer'])

    def test_normalization(self):
        self.assertEqual(normalize(' MAIMONIDES. '), 'maimonides')
        self.assertEqual(normalize('שָׁלוֹם'), 'שלום')
        self.assertNotEqual(normalize('1.2'), normalize('12'))


if __name__ == '__main__':
    unittest.main()
