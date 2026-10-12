"""Summarize the Tree of Knowledge sampling experiment without another model call."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
from statistics import mean

from main import normalize


def group(answer):
    if answer is None:
        return '[missing]'
    answer=re.sub(r'^(?:a|an|the)\s+', '', normalize(answer))
    aliases={'apples':'apple','grapes':'grape','grapevine':'grape','grape vine':'grape','vine':'grape',
             'figs':'fig','fig tree':'fig','wheat plant':'wheat'}
    return aliases.get(answer,answer)


def wilson_interval(hits, total):
    """Approximate 95% interval for a binomial proportion across sampled seeds."""
    z = 1.959963984540054
    p = hits / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half_width = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0, center - half_width), min(1, center + half_width)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    manifest=json.loads((args.directory/'manifest.json').read_text())
    if not manifest['complete']:
        parser.error('Experiment is not yet complete.')
    baseline=json.loads(Path(manifest['source']).read_text())
    reports=[]
    for condition in manifest['conditions']:
        path=args.directory/condition['file']
        data=json.loads(path.read_text())
        assert data['complete'] and len(data['samples'])==manifest['samples_per_condition']
        assert data['question']==manifest['question'] and data['model']==manifest['model']
        assert data['settings']['temperature']==manifest['temperature']
        assert data['model_info']==baseline['model_info'], 'Model metadata changed'
        assert [s['seed'] for s in data['samples']]==list(range(manifest['seed_start'],manifest['seed_start']+manifest['samples_per_condition']))
        for setting in ['max_tokens','num_ctx','thinking']:
            assert data['settings'][setting]==baseline['settings'][setting]
        counts=Counter(group(s.get('answer')) if s['status'] in ['valid','abstained'] else '['+s['status']+']' for s in data['samples'])
        n=len(data['samples'])
        metrics=[s['logprob_metrics'] for s in data['samples'] if 'logprob_metrics' in s]
        raw_text=[s.get('raw_response',{}).get('message',{}).get('content','') for s in data['samples']]
        grape_mentions = [s['index'] for s, text in zip(data['samples'], raw_text)
                          if re.search(r'\b(?:grapes?|grapevines?|vines?)\b', text, re.IGNORECASE)]
        item={'mode':condition['mode'],'file':condition['file'],
              'counts':dict(counts),'samples':n,'target_hits':sum(counts[t] for t in ['grape','fig','wheat']),
              'grape_rate':counts['grape']/n, 'grape_rate_wilson_95':wilson_interval(counts['grape'], n),
              'grape_mention_anywhere_sample_indices':grape_mentions,
              'distinct_answer_groups_including_abstention':len(counts),
              'answer_entropy_bits':-sum(c/n*math.log2(c/n) for c in counts.values()),
              'distinct_response_texts':len(set(raw_text)),
              'mean_tokens':mean(m['token_count'] for m in metrics) if metrics else None,
              'total_visible_tokens':sum(m['token_count'] for m in metrics),
              'mean_of_response_mean_logprobs':mean(m['mean_token_logprob'] for m in metrics) if metrics else None,
              'raw_answer_counts':dict(Counter(s.get('answer') for s in data['samples'])),
              'target_samples':[{'index':s['index'],'seed':s['seed'],'answer':s['answer'],
                                'mean_logprob':s.get('logprob_metrics',{}).get('mean_token_logprob'),
                                'response':s['raw_response']['message']['content']}
                               for s in data['samples'] if s['status']=='valid' and group(s.get('answer')) in ['grape','fig','wheat']]}
        reports.append(item)
    summary={'manifest':manifest,'conditions':reports}
    (args.directory/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    lines=['# Tree of Knowledge: reasoning versus direct, fresh seeds','',
           f"Question: {manifest['question']}",
           f"Model: {manifest['model']}. Temperature: {manifest['temperature']}. {manifest['samples_per_condition']} samples per condition.",
           f"Seeds: {manifest['seed_start']}–{manifest['seed_start']+manifest['samples_per_condition']-1}.",'',
           'Model metadata, question, seed range, context size, and token budget were verified equal. Top-k and other unspecified model/server defaults were left unchanged. Native thinking was off; reasoning is ordinary generated text. All runs requested logprobs.','',
           '## Answer distributions','',
           'Case, punctuation, and leading articles are normalized; fig-tree and grape/vine variants are grouped. No model judge was used. Target means grape, fig, or wheat; etrog is retained separately and is not declared incorrect by this grouping. Counts include all attempted samples.','',
           '| Mode | Apple | Grape | Fig | Wheat | Pomegranate | Etrog | UNKNOWN | Other/excluded | Target hits |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in reports:
        c=r['counts']; keys=['apple','grape','fig','wheat','pomegranate','etrog','unknown']
        vals=[str(c.get(k,0)) for k in keys]
        other=sum(v for k,v in c.items() if k not in keys)
        lines.append('| '+ ' | '.join([r['mode']]+vals+[str(other),f"{r['target_hits']}/{r['samples']}"])+' |')
    lines+=['','## Primary outcome: grape frequency','',
            '| Mode | Grape responses | Frequency | Approximate 95% Wilson interval |',
            '|---|---:|---:|---:|']
    for r in reports:
        low, high = r['grape_rate_wilson_95']
        lines.append(f"| {r['mode']} | {r['counts'].get('grape',0)}/{r['samples']} | {r['grape_rate']:.1%} | {low:.1%}–{high:.1%} |")
    lines+=['','Intervals describe sampling uncertainty under a binomial approximation for this question and these settings; they do not establish general accuracy or prove impossibility when no grapes appear.']
    lines+=['','## Secondary observation: grape mentioned anywhere','',
            'This counts an explicit grape/vine mention anywhere in the response, even when the final answer chooses something else. It is separate from final-answer frequency and does not validate the surrounding claims.']
    for r in reports:
        indices = r['grape_mention_anywhere_sample_indices']
        lines.append(f"- {r['mode']}: {len(indices)}/{r['samples']} responses; sample indices: {indices}.")
    lines+=['','## Diversity, length, and scores','',
            '| Mode | Distinct answer groups | Distinct full texts | Mean tokens | Mean response score |','|---|---:|---:|---:|---:|']
    for r in reports:
        lines.append(f"| {r['mode']} | {r['distinct_answer_groups_including_abstention']} | {r['distinct_response_texts']} | {r['mean_tokens']:.1f} | {r['mean_of_response_mean_logprobs']:.4f} |")
    lines+=['','Mean response score is the average of per-response mean token log probabilities over all visible text. It is not correctness confidence. It is affected by differing styles and prefixes.']
    lines+=['','## Interpretation limits','']+['- '+note for note in manifest['notes']]
    lines+=['- Zero occurrences in a finite sample do not show an answer is impossible under that condition.',
            '- More diverse text is not itself better target retrieval; longer runs also spend more generation tokens. Equal sample count is not equal compute.',
            '- A length-only hypothesis needs additional prefix/length controls, because reason versus direct changes semantic instructions as well as length.',
            '', '## Target response texts','']
    for r in reports:
        for s in r['target_samples']:
            lines += [f"### {r['mode']}, sample {s['index']}: {s['answer']}",'',s['response'],'']
    (args.directory/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'conditions':[{k:v for k,v in r.items() if k not in ['raw_answer_counts','target_samples']} for r in reports]},indent=2))


if __name__=='__main__':
    main()
