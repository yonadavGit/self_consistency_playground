"""Metrics for Ollama token log probabilities, checked against visible text."""
import math


def score(response):
    entries = response.get('logprobs')
    if not entries:
        raise ValueError('Ollama returned no token log probabilities.')
    content = response['message']['content'].encode('utf-8')
    reconstructed = b''.join(bytes(entry['bytes']) for entry in entries)
    if reconstructed != content:
        raise ValueError('Token bytes do not exactly match the visible response; refusing to mislabel its score.')
    total = sum(entry['logprob'] for entry in entries)
    mean = total / len(entries)
    return {'token_count': len(entries), 'sum_logprob': total,
            'mean_token_logprob': mean, 'geometric_mean_token_probability': math.exp(mean),
            'perplexity': math.exp(-mean)}

