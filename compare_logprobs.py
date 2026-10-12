"""Replay a saved run and compare mean token logprob of entire visible responses."""
import argparse
import json
from pathlib import Path

from main import api, extract
from logprob_metrics import score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--host', default='http://127.0.0.1:11434')
    args = parser.parse_args()
    source = json.loads(args.source.read_text())
    if source.get('procedure') == 'self_refinement':
        parser.error('Refinement chains cannot be replayed as independent samples. '
                     'Use --logprobs during self-refinement to score each generation in its own context.')
    if args.output.exists():
        parser.error('Output already exists; choose a new path.')
    report = {'source_run': str(args.source.resolve()), 'metric': 'Mean natural-log probability per generated token across the entire visible response, including reasoning and FINAL line, excluding unreturned stop tokens.',
              'note': 'Ollama-reported probabilities. Different responses condition on different prefixes. This is not correctness confidence.',
              'samples': [], 'complete': False}
    settings = source['settings']
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        tmp = args.output.with_suffix('.tmp')
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        tmp.replace(args.output)

    save()
    try:
        for sample in source['samples']:
            request = {'model': source['model'], 'stream': False, 'logprobs': True,
                       'messages': [{'role': 'user', 'content': source['prompt']}],
                       'options': {'temperature': settings['temperature'], 'seed': sample['seed'],
                                   'num_predict': settings['max_tokens'], 'num_ctx': settings['num_ctx']}}
            if 'thinking' in source.get('model_info', {}).get('capabilities', []):
                request['think'] = settings.get('thinking') == 'on'
            response = api(args.host, 'chat', request, 600)
            identical = response['message']['content'] == sample['raw_response']['message']['content']
            measurement = score(response)
            item = {'index': sample['index'], 'seed': sample['seed'],
                    'original_answer': sample.get('answer'),
                    'replay_answer': extract(response['message']['content'])[1],
                    'identical_response': identical, **measurement, 'raw_response': response}
            report['samples'].append(item)
            save()
            print(f"[{sample['index']}] {item['replay_answer']} | exact replay={identical} | tokens={item['token_count']} | mean logprob={item['mean_token_logprob']:.6f}", flush=True)
        report['complete'] = True
    finally:
        save()
    print('\nRanked by mean token logprob (highest first):')
    for item in sorted(report['samples'], key=lambda item: item['mean_token_logprob'], reverse=True):
        print(f"#{item['index']:2} {str(item['replay_answer']):15} {item['token_count']:4} tokens  {item['mean_token_logprob']:.6f}  exact={item['identical_response']}")


if __name__ == '__main__':
    main()
