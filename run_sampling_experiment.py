"""Compare direct/reason prompts using a saved run's question/settings."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from main import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--seed', type=int, required=True, help='Starting seed for a fresh shared seed range')
    parser.add_argument('--target-names', nargs='+', default=[], help='Optional outcome labels for the experiment manifest; never sent to the model')
    args = parser.parse_args()
    if args.samples < 1:
        parser.error('Samples must be positive.')
    if args.output_dir.exists():
        parser.error('Choose a new output directory to preserve existing results.')
    source = json.loads(args.source.read_text())
    settings = source['settings']
    args.output_dir.mkdir(parents=True)
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(),
                'source': str(args.source.resolve()), 'question': source['question'],
                'model': source['model'], 'seed_start': args.seed, 'samples_per_condition': args.samples,
                'temperature': settings['temperature'],
                'conditions': [], 'complete': False,
                'predefined_target_groups': args.target_names,
                'notes': ['Scoring rules should be defined separately before inspecting results; target labels are metadata only.',
                          'A target final answer does not certify the generated explanation.',
                          'Same seeds standardize runs but do not mean equivalent semantic random paths across prompts.',
                          'Prompt mode changes instructions and length together; this does not isolate length alone.',
                          'Fresh seeds are used for this follow-up; one question does not establish general superiority.']}
    manifest_path=args.output_dir/'manifest.json'
    def save():
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    save()
    for mode in ['direct', 'reason']:
        output=args.output_dir/f'{mode}.json'
        print(f'\nSTART CONDITION: mode={mode}',flush=True)
        result=run(argparse.Namespace(question=source['question'],model=source['model'],
            samples=args.samples,temperature=settings['temperature'],seed=args.seed,
            max_tokens=settings['max_tokens'],num_ctx=settings['num_ctx'],mode=mode,
            thinking='off',logprobs=True,verbose=False,aliases=None,output=output,
            host='http://127.0.0.1:11434',timeout=600))
        condition=json.loads(output.read_text())
        manifest['conditions'].append({'mode':mode,'file':output.name,'exit_code':result})
        save()
        if not condition['complete']:
            print('Stopped after interrupted condition.',flush=True)
            return 1
    manifest['complete']=True
    save()
    return 0


if __name__=='__main__':
    raise SystemExit(main())
