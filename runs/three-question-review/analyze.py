"""Reproduce descriptive counts for the three-question review; no inference calls."""
import collections
import json
import math
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[2]
FILES = {
    'akiva': ['20261011T163951981371Z.json', '20261011T164004145264Z.json'],
    'melachot': ['20261011T165211453642Z.json', '20261011T165236131510Z.json'],
    'abraham': ['abraham-fresh-60/direct.json', 'abraham-fresh-60/reason.json'],
}

def label(question, answer):
    if answer is None:
        return '[missing FINAL]'
    a = answer.lower().strip().rstrip('.')
    if question == 'akiva':
        return {'three': '3', 'three years old': '3', '3 years old': '3', 'five': '5'}.get(a, a)
    if question == 'melachot':
        return {
            'making a fire': 'kindling fire', 'kindling a fire': 'kindling fire',
            'lighting a fire': 'kindling fire', 'binyan': 'building',
            'shechita': 'slaughtering', 'shochet': 'slaughtering',
            "hotza'ah": 'carrying', 'plowing a field': 'plowing',
        }.get(a, a)
    if re.search(r'\b(amathlai|amatlai|amtelai)\b', a):
        return 'amathlai (accepted name)'
    if a.startswith('keziah'):
        return 'keziah'
    if a in ["terah's wife", 'the wife of terah']:
        return "terah's wife"
    return a

def wilson(k, n):
    z = 1.95996398454
    p = k/n
    center = (p + z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/(1+z*z/n)
    return [center-half, center+half]

def fisher(a, b, n):
    total = a+b
    def prob(x):
        return math.comb(n, x)*math.comb(n, total-x)/math.comb(2*n, total)
    observed = prob(a)
    return sum(prob(x) for x in range(max(0,total-n), min(n,total)+1)
               if prob(x) <= observed*(1+1e-12))

results = {}
for question, paths in FILES.items():
    results[question] = {}
    for mode, path in zip(['direct', 'reason'], paths):
        data = json.loads((ROOT/'runs'/path).read_text())
        samples = data['samples']
        target = {'akiva':'40', 'melachot':'kindling fire', 'abraham':'amathlai (accepted name)'}[question]
        rows = [{'index':s['index'], 'seed':s['seed'], 'status':s['status'],
                 'answer':s['answer'], 'group':label(question,s['answer'])} for s in samples]
        hits = [r['index'] for r in rows if r['group'] == target]
        results[question][mode] = {
            'file':path, 'question':data['question'], 'model':data['model'],
            'model_details':data['model_info']['details'], 'settings':data['settings'],
            'seed_start':data['seed'], 'n':len(samples),
            'statuses':dict(collections.Counter(s['status'] for s in samples)),
            'grouped_final_answers':dict(collections.Counter(r['group'] for r in rows)),
            'target':target, 'target_hits':hits, 'target_rate':len(hits)/len(samples),
            'target_wilson95':wilson(len(hits), len(samples)),
            'mean_generated_tokens_ollama_eval_count':statistics.mean(s['raw_response']['eval_count'] for s in samples),
            'samples':rows,
        }

results['melachot']['sensitivity'] = {
    'manual_recovery_direct_sample4':'Clear lighting-fire answer, missing FINAL marker; raises direct count from 1 to 2.',
    'reason_sample8':'Working with fire is vague; including it raises reason count from 6 to 7.',
    'plowing':'Direct sample21 and reason samples24,30 say plowing, defensible under the broad wording (Exodus 34:21). Not counted as fire.',
    'fire_target_counts_strict_final':[1,6],
    'fire_target_counts_manual_clear':[2,6],
    'fire_target_counts_manual_including_vague':[2,7],
    'fisher_two_sided_strict_final':fisher(1,6,30),
    'fisher_two_sided_manual_clear':fisher(2,6,30),
    'fisher_two_sided_manual_including_vague':fisher(2,7,30),
}
out = pathlib.Path(__file__).with_name('summary.json')
out.write_text(json.dumps(results, indent=2)+'\n')
for q in FILES:
    for mode in ['direct','reason']:
        r=results[q][mode]
        print(q,mode,len(r['target_hits']), '/',r['n'],r['grouped_final_answers'])
print('melachot sensitivity',results['melachot']['sensitivity'])
