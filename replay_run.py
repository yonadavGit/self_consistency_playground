"""Display a saved experiment in the terminal without calling Ollama."""
import argparse
import json
from pathlib import Path
from main import print_sample, print_summary, normalize, summarize
from self_refinement import print_stage
import terminal_output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--sample', type=int, help='Show one saved sample index; summary then covers only that sample')
    parser.add_argument('--aliases', type=Path)
    parser.add_argument('--plain', action='store_true')
    args = parser.parse_args()
    terminal_output.configure(args.plain)
    run = json.loads(args.run.read_text())
    samples = run['samples']
    if args.sample is not None:
        samples = [s for s in samples if s['index'] == args.sample]
        if not samples:
            parser.error('That sample index is not present in the saved run.')
    aliases = json.loads(args.aliases.read_text()) if args.aliases else run.get('aliases', {})
    aliases = {normalize(k): normalize(v) for k, v in aliases.items()}
    print(f"SAVED REPLAY — no generation\n{run['question']}\n{args.run}\n")
    if args.sample is not None:
        print('Showing one selected sample; this is not the full-run distribution.')
    for sample in samples:
        history = sample.get('refinement')
        if history:
            print_stage('initial', 0, history['initial'], args.verbose)
            for step in history['rounds']:
                for stage in ('critique', 'revision'):
                    if stage in step:
                        print_stage(stage, step['round'], step[stage], args.verbose)
            print(f"Retained answer: {sample.get('answer')} | complete: {history['complete']}")
        elif args.verbose:
            print_sample(sample, len(run['samples']), verbose=True)
    if any('refinement' in s for s in samples):
        print('\nBEFORE SELF-REFINEMENT')
        print_summary(summarize([s.get('refinement', {}).get('initial', s) for s in samples], aliases))
        print('\nAFTER SELF-REFINEMENT')
    print_summary(summarize(samples, aliases))


if __name__ == '__main__':
    main()
