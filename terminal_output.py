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


def configure(plain=False):
    global _plain
    _plain = plain


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
