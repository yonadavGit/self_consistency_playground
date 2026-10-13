"""Rich presentation only; never alters model requests or saved responses."""
import os
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    Console = None

_plain = False
_printed_prompts = set()


def configure(plain=False):
    global _plain
    _plain = plain
    _printed_prompts.clear()


def console():
    if _plain or Console is None:
        return None
    return Console(highlight=False, markup=False, no_color='NO_COLOR' in os.environ)


def generation(sample, title, verbose=True, critique=False, voting=None):
    c = console()
    if c is None:
        return False
    status = sample.get('status', 'unknown')
    color = 'cyan' if status == 'valid' else 'yellow' if status == 'abstained' else 'red'
    meta = f"seed {sample.get('seed')} · {status} · {sample.get('elapsed_seconds', 0):.1f}s"
    c.rule(Text(title, style='bold ' + color), align='left')
    c.print(Text(meta, style='dim'))
    if verbose:
        if sample.get('native_thinking'):
            c.print(Panel(Text(sample['native_thinking']), title='Native thinking', border_style='magenta'))
        body = sample.get('raw_response', {}).get('message', {}).get('content', '')
        c.print(Panel(Text(body or '[No response text returned]'),
                      title='Critique and fix plan' if critique else 'Full response · generated text',
                      border_style=color, padding=(1, 2)))
    if not critique:
        c.print(Panel(Text(sample.get('answer') or '[No final answer extracted]', style='bold'),
                      title='Extracted final answer · not fact-checked', border_style=color))
    if voting is not None:
        c.print(Text('Included in voting: ' + ('yes' if voting else 'no (invalid answer or incomplete chain)'), style='dim'))
    if sample.get('error'):
        c.print(Text('Error: ' + sample['error'], style='red'))
    metrics = sample.get('logprob_metrics')
    if metrics:
        c.print(Text(f"Generation mean logprob: {metrics['mean_token_logprob']:.6f} · {metrics['token_count']} tokens", style='dim'))
    elif sample.get('logprob_error'):
        c.print(Text('Logprobs unavailable: ' + sample['logprob_error'], style='yellow'))
    c.print()
    return True


def summary(data):
    c = console()
    if c is None:
        return False
    valid, attempted = data['valid_samples'], data['attempted_samples']
    c.rule('Final answer distribution', style='cyan', align='left')
    c.print(f"{valid} valid votes / {attempted} responses; {data['excluded_samples']} excluded")
    if not valid:
        c.print('No valid final answers to vote on.')
        return True
    table = Table(expand=True, header_style='bold cyan')
    for name, justify in [('Answer', 'left'), ('Votes', 'right'), ('% valid', 'right'), ('% all', 'right')]:
        table.add_column(name, justify=justify)
    for answer, count in data['votes'].items():
        table.add_row(Text(answer), str(count), f'{count/valid:.1%}', f'{count/attempted:.1%}')
    c.print(table)
    if data['majority_answer']:
        outcome = 'Majority answer: ' + data['majority_answer']
    elif data['tied_answers']:
        outcome = 'No majority; tied leaders: ' + ', '.join(data['tied_answers'])
    else:
        outcome = 'No strict majority. Plurality answer: ' + data['plurality_answer']
    c.print(Text(outcome, style='bold cyan'))
    c.print(Text('Agreement is not factual confidence. “Valid” means parseable, not correct.', style='dim'))
    return True


def text_panel(title, body):
    c = console()
    if c is None:
        print('\n' + title.upper() + '\n' + body, flush=True)
    else:
        c.print(Panel(Text(body), title=title, border_style='blue'))


def model_details(identity, info):
    details = info.get('details', {})
    lines = [f"Model: {identity['resolved_name']}",
             f"{details.get('parameter_size', 'unknown')} parameters · {details.get('quantization_level', 'unknown')}",
             f"Digest: {identity.get('digest', 'unavailable')}"]
    if identity.get('reference_url'):
        lines.append(identity['reference_url'])
    if identity.get('error'):
        lines.append('Identity warning: ' + identity['error'])
    text_panel('Model identity', '\n'.join(lines))


def request_details(request, critique=False):
    for message in request['messages']:
        key = (message['role'], message['content'])
        if key not in _printed_prompts:
            text_panel('Exact prompt sent · ' + message['role'], message['content'])
            _printed_prompts.add(key)


def logprob_ranking(samples, enabled=False):
    """Rank individual complete, parseable answers by full-response mean logprob."""
    import math
    if not enabled and not any('logprob_metrics' in s or 'logprob_error' in s for s in samples):
        return
    rows = []
    for sample in samples:
        value = sample.get('logprob_metrics', {}).get('mean_token_logprob')
        if (sample.get('status') == 'valid' and sample.get('answer')
                and sample.get('refinement', {}).get('complete', True)
                and isinstance(value, (int, float)) and math.isfinite(value)):
            rows.append((sample, value))
    rows.sort(key=lambda row: row[1], reverse=True)
    title = 'Final answers ranked by full-response mean logprob'
    caption = (f'{len(rows)} ranked / {len(samples)} samples. '
               'Unscored, invalid, abstained, or incomplete samples excluded.\n'
               'Higher (closer to zero) is better. Scores cover the entire response, not just the final answer; they do not measure correctness.')
    if any('refinement' in s for s in samples):
        caption += '\nRetained answers only; generation contexts differ across refinement chains. These are not shared-prompt rescoring results.'
    c = console()
    headers = ['Sample', 'Final answer', 'Mean logprob', 'Tokens']
    values = [(str(s['index']), s['answer'], f'{v:.6f}',
               str(s['logprob_metrics'].get('token_count', '—'))) for s, v in rows]
    if c is None:
        print('\n' + title)
        widths = [max(len(headers[i]), *(len(row[i]) for row in values)) for i in range(4)] if values else list(map(len, headers))
        print(' | '.join(h.ljust(w) for h, w in zip(headers, widths)))
        for row in values:
            print(' | '.join(value.ljust(w) for value, w in zip(row, widths)))
        if not rows:
            print('No eligible scored answers.')
        print(caption)
        return
    c.rule(title, style='cyan', align='left')
    table = Table(expand=True, header_style='bold cyan')
    for header in headers:
        table.add_column(header, justify='left' if header == 'Final answer' else 'right')
    for row in values:
        table.add_row(*(Text(value) for value in row))
    c.print(table)
    if not rows:
        c.print('No eligible scored answers.')
    c.print(Text(caption, style='dim'))
