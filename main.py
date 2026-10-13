"""Self-consistency and optional self-refinement with ordinary Ollama chat models."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import time
import unicodedata
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from logprob_metrics import score
from self_refinement import refine, print_stage
import terminal_output


def api(host, endpoint, payload, timeout):
    request = Request(host.rstrip('/') + '/api/' + endpoint,
                      data=None if payload is None else json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f'Ollama HTTP {exc.code}: {exc.read().decode()}') from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f'Cannot reach Ollama: {exc}') from exc
    if result.get('error'):
        raise RuntimeError(result['error'])
    return result


def model_identity(args):
    """Snapshot the local tag; registry links are references, not digest pins."""
    name = args.model if ':' in args.model.rsplit('/', 1)[-1] else args.model + ':latest'
    result = {'requested_model': args.model, 'resolved_name': name}
    try:
        models = api(args.host, 'tags', None, args.timeout).get('models', [])
        match = next((m for m in models if name in (m.get('name'), m.get('model'))), None)
        if match:
            result.update(match)
        else:
            result['error'] = 'Requested model not found in local tag listing; digest unavailable.'
    except RuntimeError as exc:
        result['error'] = str(exc)
    # Custom local names do not necessarily have a registry page.
    if name.split(':')[0] == 'llama3.1':
        result['reference_url'] = 'https://ollama.com/library/' + quote(name, safe=':')
    try:
        result['ollama_version'] = api(args.host, 'version', None, args.timeout).get('version')
    except RuntimeError as exc:
        result['version_error'] = str(exc)
    return result


def normalize(answer):
    text = unicodedata.normalize('NFKC', answer).casefold()
    text = ''.join(c for c in text if not ('\u0591' <= c <= '\u05c7' and unicodedata.combining(c)))
    return ' '.join(text.split()).strip(' .,!?:;\"\'׳״')


def extract(content):
    matches = list(re.finditer(r'^\s*FINAL:[ \t]*([^\n]+)$', content, re.MULTILINE))
    if len(matches) != 1 or content[matches[0].end():].strip():
        return content, None
    match = matches[0]
    return content[:match.start()].strip(), match.group(1).strip()


def summarize(samples, aliases):
    votes = Counter()
    for sample in samples:
        if sample.get('status') == 'valid' and sample.get('refinement', {}).get('complete', True):
            key = normalize(sample['answer'])
            votes[aliases.get(key, key)] += 1
    total = sum(votes.values())
    leaders = [key for key, count in votes.items() if count == max(votes.values())] if votes else []
    winner = leaders[0] if len(leaders) == 1 else None
    count = votes[winner] if winner else 0
    return {'votes': dict(votes.most_common()), 'valid_samples': total,
            'attempted_samples': len(samples), 'excluded_samples': len(samples) - total,
            'plurality_answer': winner, 'tied_answers': leaders if len(leaders) > 1 else [],
            'majority_answer': winner if count > total / 2 else None,
            'winner_share_of_valid': count / total if total and winner else None,
            'winner_share_of_attempted': count / len(samples) if samples and winner else None}


def print_summary(summary):
    if terminal_output.summary(summary):
        return
    valid = summary['valid_samples']
    print('\nFinal answer distribution (grouped answers)')
    print(f"{valid} valid votes / {summary['attempted_samples']} responses; "
          f"{summary['excluded_samples']} excluded")
    if not valid:
        print('No valid final answers to vote on.')
        return
    width = max(len('Answer'), *(len(answer) for answer in summary['votes']))
    print(f"{'Answer':<{width}}  {'Votes':>5}  {'% of valid':>10}")
    print('-' * (width + 19))
    for answer, count in summary['votes'].items():
        print(f'{answer:<{width}}  {count:>5}  {count / valid:>9.1%}')
    if summary['majority_answer']:
        print(f"Majority answer: {summary['majority_answer']}")
    elif summary['tied_answers']:
        print('No majority; tied leaders: ' + ', '.join(summary['tied_answers']))
    else:
        print(f"No strict majority. Plurality answer: {summary['plurality_answer']}")
    print('Percentages measure agreement among valid votes, not factual confidence.')


def print_sample(sample, total, verbose=False):
    if verbose and terminal_output.generation(sample, f"SAMPLE {sample['index']}/{total}", voting=sample['status'] == 'valid' and sample.get('refinement', {}).get('complete', True)):
        return
    if verbose:
        rule = '=' * min(100, shutil.get_terminal_size(fallback=(80, 24)).columns)
        print(f'\n{rule}')
        print(f"SAMPLE {sample['index']}/{total}  |  Seed: {sample['seed']}  |  "
              f"{sample['status']}  |  {sample['elapsed_seconds']:.1f}s")
        print(rule)
        if sample.get('native_thinking'):
            print('\nNATIVE THINKING\n')
            print(sample['native_thinking'])
        content = sample.get('raw_response', {}).get('message', {}).get('content', '')
        print('\nFULL RESPONSE (including any written reasoning)\n')
        print(content if content else '[No response text returned]')
        print('\n' + '-' * len(rule))
        print(f"Extracted final answer: {sample.get('answer') or '[No final answer extracted]'}")
        eligible = sample['status'] == 'valid' and sample.get('refinement', {}).get('complete', True)
        print(f"Included in voting: {'yes' if eligible else 'no (invalid answer or incomplete chain)'}")
        if sample.get('error'):
            print(f"Error: {sample['error']}")
    else:
        print(f"[{sample['index']}/{total}] {sample['status']}: "
              f"{sample.get('answer') or sample.get('error', 'no final answer')} "
              f"({sample['elapsed_seconds']:.1f}s)")
    if 'logprob_metrics' in sample:
        metrics = sample['logprob_metrics']
        print(f"  Full-response mean logprob: {metrics['mean_token_logprob']:.6f} ({metrics['token_count']} tokens)")
    elif 'logprob_error' in sample:
        print(f"  Logprobs unavailable: {sample['logprob_error']}")
    if verbose:
        print(rule + '\n')
    sys.stdout.flush()


def prompt(question, mode):
    instruction = ('Think through the question step by step before answering. Consider relevant facts '
                   'and resolve possible ambiguities. Write your reasoning, then your final answer.'
                   if mode == 'reason' else 'Answer directly without writing reasoning.')
    return (instruction + '\nUse the language of the question. End with exactly one line in this '
            'format: FINAL: <short answer only>. Do not put explanations or citations on that '
            'line. If you cannot answer, use FINAL: UNKNOWN.\n\nQuestion:\n' + question)


def generate_sample(args, native, text, seed, index, max_tokens=None, critique=False):
    request = {'model': args.model, 'stream': False,
               'messages': [{'role': 'user', 'content': text}],
               'options': {'temperature': args.temperature, 'seed': seed,
                           'num_predict': max_tokens or args.max_tokens, 'num_ctx': args.num_ctx}}
    if native:
        request['think'] = args.thinking == 'on'
    if args.logprobs:
        request['logprobs'] = True
    sample = {'index': index, 'seed': seed, 'prompt': text, 'request': request}
    if getattr(args, 'verbose', False):
        terminal_output.request_details(request, critique=critique)
    start = time.monotonic()
    try:
        response = api(args.host, 'chat', request, args.timeout)
        body = response.get('message', {}).get('content', '')
        reasoning, answer = (body, None) if critique else extract(body)
        status = 'valid'
        if response.get('done_reason') == 'length' or not response.get('done'):
            status = 'truncated'
        elif critique and not body.strip():
            status = 'unparseable'
        elif not critique:
            if not answer or not normalize(answer):
                status = 'unparseable'
            elif normalize(answer) == 'unknown':
                status = 'abstained'
        sample.update(status=status, reasoning=reasoning, answer=answer,
                      native_thinking=response.get('message', {}).get('thinking', ''), raw_response=response)
        if args.logprobs:
            try:
                sample['logprob_metrics'] = score(response)
            except ValueError as exc:
                sample['logprob_error'] = str(exc)
    except RuntimeError as exc:
        sample.update(status='error', error=str(exc))
    sample['elapsed_seconds'] = round(time.monotonic() - start, 3)
    return sample


def run(args):
    terminal_output.configure(getattr(args, 'plain', False))
    rounds = getattr(args, 'self_refine', 0)
    critique_tokens = getattr(args, 'critique_max_tokens', 512)
    aliases = {}
    if args.aliases:
        mapping = json.loads(args.aliases.read_text())
        if not isinstance(mapping, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()):
            raise ValueError('Aliases must map answer strings to canonical strings.')
        aliases = {normalize(k): normalize(v) for k, v in mapping.items()}
    info = api(args.host, 'show', {'model': args.model}, args.timeout)
    identity = model_identity(args)
    native = 'thinking' in info.get('capabilities', [])
    if args.thinking == 'on' and not native:
        raise ValueError('Model does not advertise native thinking. Use --thinking off for prompted reasoning.')
    output = args.output or Path('runs') / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError(f'Refusing to overwrite {output}')
    seed = args.seed if args.seed is not None else secrets.randbelow(2**30)
    report = {'question': args.question, 'model': args.model,
              'created_at': datetime.now(timezone.utc).isoformat(),
              'settings': {key: getattr(args, key) for key in ['samples', 'temperature', 'max_tokens', 'num_ctx', 'mode', 'thinking', 'logprobs']},
              'seed': seed, 'prompt': prompt(args.question, args.mode), 'aliases': aliases,
              'model_info': info, 'model_identity': identity, 'samples': [], 'complete': False}
    if rounds:
        report['settings'].update(self_refine=rounds, critique_max_tokens=critique_tokens,
                                  refinement_scorer='none')
        report['procedure'] = 'self_refinement'

    def save():
        report['summary'] = summarize(report['samples'], aliases)
        if rounds:
            report['initial_summary'] = summarize(
                [s.get('refinement', {}).get('initial', s) for s in report['samples']], aliases)
            report['completed_chains'] = sum(s.get('refinement', {}).get('complete', False)
                                             for s in report['samples'])
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(output)

    save()
    print(f'Model: {args.model} | mode: {args.mode} | temperature: {args.temperature}', flush=True)
    print(f'Saving samples to {output.resolve()}', flush=True)
    if args.verbose:
        terminal_output.model_details(identity, info)
        terminal_output.request_details({'messages': [{'role': 'user', 'content': report['prompt']}]})
    if rounds:
        print(f'Self-refinement: {rounds} rounds per chain; no quality scorer; '
              f'up to {args.samples * (1 + 2 * rounds)} generation calls.', flush=True)
    try:
        for index in range(args.samples):
            sample = generate_sample(args, native, report['prompt'], seed + index, index + 1)
            report['samples'].append(sample)
            if rounds:
                print(f'\nCHAIN {index + 1}/{args.samples}', flush=True)

                def generate_stage(text, number, stage):
                    stage_seed = seed + args.samples + index * 2 * rounds + 2 * (number - 1)
                    stage_seed += stage == 'revision'
                    return generate_sample(args, native, text, stage_seed, index + 1,
                                           critique_tokens if stage == 'critique' else args.max_tokens,
                                           critique=stage == 'critique')

                refine(sample, args.question, args.mode, rounds, generate_stage, save,
                       lambda stage, number, result: print_stage(stage, number, result, args.verbose))
                print(f"Chain {index + 1}: {sample['refinement']['initial'].get('answer')} -> "
                      f"{sample.get('answer')} | {sample['refinement']['stop_reason']}", flush=True)
                sample['chain_elapsed_seconds'] = round(
                    sample['refinement']['initial']['elapsed_seconds'] + sum(
                        step[stage]['elapsed_seconds'] for step in sample['refinement']['rounds']
                        for stage in ('critique', 'revision') if stage in step), 3)
                save()
            else:
                save()
                print_sample(sample, args.samples, verbose=args.verbose)
        report['complete'] = True
    except KeyboardInterrupt:
        report['interrupted'] = True
        print('\nInterrupted; completed samples are saved.', file=sys.stderr)
    finally:
        save()
    if rounds:
        print('\nBEFORE SELF-REFINEMENT')
        print_summary(report['initial_summary'])
        print(f"\nAFTER SELF-REFINEMENT ({report['completed_chains']}/{len(report['samples'])} complete chains)")
        print('Only complete chains contribute final votes; partial histories are saved.')
    print_summary(report['summary'])
    terminal_output.logprob_ranking(report['samples'], enabled=args.logprobs)
    complete = report['complete'] and (not rounds or report['completed_chains'] == args.samples)
    return 0 if complete and report['summary']['valid_samples'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question')
    parser.add_argument('--model', default='llama3.1:latest')
    parser.add_argument('-n', '--samples', type=int, default=5)
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--max-tokens', type=int, default=1024)
    parser.add_argument('--num-ctx', type=int, default=4096)
    parser.add_argument('--mode', choices=['reason', 'direct'], default='reason')
    parser.add_argument('--self-refine', type=int, default=0, metavar='ROUNDS',
                        help='Critique and revise each sample for ROUNDS iterations (default: disabled)')
    parser.add_argument('--critique-max-tokens', type=int, default=512,
                        help='Token budget for each critique (default: 512)')
    parser.add_argument('--thinking', choices=['off', 'on'], default='off')
    parser.add_argument('--logprobs', action='store_true', help='Save token log probabilities and report the full-response mean')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display model identity, exact prompts, complete responses, thinking, and extracted answers')
    parser.add_argument('--plain', action='store_true', help='Use the original plain terminal output (no Rich panels or colors)')
    parser.add_argument('--aliases', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--host', default='http://127.0.0.1:11434')
    parser.add_argument('--timeout', type=float, default=600)
    args = parser.parse_args()
    if args.samples < 1 or args.max_tokens < 1 or args.num_ctx < 1 or args.timeout <= 0:
        parser.error('Samples, token limits, context size, and timeout must be positive.')
    if args.self_refine < 0 or args.critique_max_tokens < 1:
        parser.error('Self-refinement rounds must be nonnegative and critique tokens positive.')
    if not 0 <= args.temperature <= 2:
        parser.error('Temperature must be between 0 and 2.')
    if args.mode == 'direct' and args.thinking == 'on':
        parser.error('Direct mode requires --thinking off.')
    try:
        return run(args)
    except (RuntimeError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
