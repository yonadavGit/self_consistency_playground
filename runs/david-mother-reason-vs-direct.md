# Prompted reasoning versus direct answers

Model: `llama3.1:latest` (ordinary Llama 3.1 8B chat model). Temperature: 0.8.
Question (verbatim): Who was the mom of king david

Ten samples per condition, same seeds, token limit (1024), context (4096), model metadata, and answer-format instruction. Only the opening reasoning/direct instruction differs. The reasoning responses were reused from the original run, with exact-match replays supplying logprobs. The direct responses were generated with logprobs enabled.

## Answer distribution

All counts use all ten attempts, including abstentions. No request failures or malformed/truncated outputs occurred.

| Raw answer (normalized) | Reasoning | Direct |
|---|---:|---:|
| bathsheba | 0/10 | 3/10 |
| jesse | 0/10 | 2/10 |
| jesse's wife | 2/10 | 0/10 |
| nishmat | 1/10 | 0/10 |
| nitza | 1/10 | 0/10 |
| nitzebet | 0/10 | 1/10 |
| nitzevet | 1/10 | 0/10 |
| unknown | 5/10 | 4/10 |

Nitzevet appeared once with reasoning; Nitzebet appeared once without it. If Nitzebet is accepted as a spelling variant, target retrieval is 1/10 in both conditions. Nitza and Nishmat are retained as distinct answers. This small experiment does not show that step-by-step prompting was necessary or improved target retrieval.

Among non-abstentions, the reasoning plurality is Jesse’s wife (2/5); the direct plurality is Bathsheba (3/6). Neither has a strict majority. Thus ordinary voting did not select the target in either condition.

## Full-response mean token log probability

Natural logarithms, including all visible reasoning and FINAL-line tokens, excluding unreturned stop tokens. Higher (closer to zero) means more probable wording. Condition-level scores below weight each response equally.

| Condition | Average of response means | Mean tokens per response |
|---|---:|---:|
| reason | -0.553719 | 299.2 |
| direct | -0.539370 | 6.4 |

| Sample | Reasoning answer | Tokens | Mean logprob | Direct answer | Tokens | Mean logprob |
|---|---|---:|---:|---|---:|---:|
| 1 | Nitza | 356 | -0.698444 | UNKNOWN | 3 | -0.675084 |
| 2 | Nitzevet | 397 | -0.421179 | Jesse | 11 | -0.461880 |
| 3 | UNKNOWN | 209 | -0.485507 | Bathsheba | 5 | -0.301113 |
| 4 | UNKNOWN | 546 | -0.755476 | Nitzebet | 15 | -0.705972 |
| 5 | Jesse's wife | 257 | -0.517041 | UNKNOWN | 3 | -0.674661 |
| 6 | UNKNOWN. | 230 | -0.557280 | Jesse | 11 | -0.623442 |
| 7 | Nishmat | 365 | -0.781957 | Bathsheba | 5 | -0.301113 |
| 8 | UNKNOWN | 131 | -0.327058 | UNKNOWN | 3 | -0.674661 |
| 9 | UNKNOWN | 160 | -0.592242 | UNKNOWN | 3 | -0.674661 |
| 10 | Jesse's wife | 341 | -0.401009 | Bathsheba | 5 | -0.301113 |

Ten samples on one selected question; not evidence of general accuracy improvement. Full-response logprobs compare different prefixes and very different response lengths/styles, not probability of correctness. Direct means no written step-by-step instruction, not absence of internal computation.

A stronger follow-up would predefine accepted answer aliases and test both prompts on a larger, independently scored question set. More samples of this question would estimate its target-retrieval rate more precisely, but would not establish a general benefit.

## Files

- Original reasoning run: `20261011T104712285208Z.json`
- Exact reasoning replays and logprobs: `david-mother-full-response-logprobs.json`
- Matched direct run and logprobs: `david-mother-direct-matched-logprobs.json`
- Machine-readable comparison: `david-mother-reason-vs-direct.json`

The earlier `david-mother-direct-logprobs.json` used a capitalized “King” and is deliberately excluded from this controlled comparison.
