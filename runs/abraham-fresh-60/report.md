# Abraham’s mother: fresh 60-sample comparison

Question: Who was the Abraham's mom according to Jewish tradition?

Llama 3.1 8B, temperature 0.8, seeds 842617000–842617059, 1024-token output budget, 4096-token context. Both modes ran 60 fresh samples. Question, model metadata, seed ranges, and all non-mode generation settings were verified equal.

## Main result

| Scoring rule | Direct | Reasoning |
|---|---:|---:|
| Final answer explicitly includes an accepted name | 3/60 (5.0%) | 20/60 (33.3%) |
| Final answer is exactly Amathlai, ignoring case/punctuation | 3/60 (5.0%) | 18/60 (30.0%) |

Reasoning produced 18 plain Amathlai answers plus “Amethlai (or Amathlai)” and “Amathlai/Amithlai.” Direct produced three plain Amathlai answers. Approximate names such as Ammilat, Amithai, Ammilah, Aminah, and Ameth were not counted. All 60 attempts remain in the denominator, including abstentions and malformed responses.

The effect is present even under exact-name scoring. This supports a higher retrieval rate for this question, model, temperature, and prompt comparison. It does not show that the explanations are sound or that extra length alone is the mechanism.

## Sampling uncertainty

- direct: approximate 95% Wilson interval 1.7%–13.7%.
- reason: approximate 95% Wilson interval 22.7%–45.9%.

Paired accepted-name outcomes by seed: {'reason_only': 18, 'direct_only': 1, 'both': 2, 'neither': 39, 'exact_mcnemar_two_sided_p': 7.62939453125e-05}
Paired exact-name outcomes by seed: {'reason_only': 16, 'direct_only': 1, 'both': 2, 'neither': 41, 'exact_mcnemar_two_sided_p': 0.000274658203125}

The exact McNemar calculation tests the discordant paired binary outcomes under a symmetric null. It is a within-question result, not evidence about all Jewish knowledge questions; the hypothesis/question was selected following exploratory work.

## Complete distributions

### direct

| Extracted answer | Count |
|---|---:|
| sarah | 22 |
| keziah | 21 |
| jochebed | 6 |
| amathlai | 3 |
| unknown | 2 |
| [missing] | 2 |
| hagar | 1 |
| keziah, daughter of kenaz | 1 |
| keziah, daughter of jethro | 1 |
| amram's wife | 1 |

Statuses: {'valid': 56, 'abstained': 2, 'unparseable': 2}
Mean generated visible tokens: 17.6. Mean of response-level mean logprobs: -0.5789.

### reason

| Extracted answer | Count |
|---|---:|
| amathlai | 18 |
| sarah | 17 |
| unknown | 14 |
| [missing] | 2 |
| ammilat | 1 |
| the wife of terah | 1 |
| amithai | 1 |
| amethlai (or amathlai) | 1 |
| ammilah | 1 |
| amathlai/amithlai | 1 |
| aminah | 1 |
| ameth | 1 |
| terah's wife | 1 |

Statuses: {'abstained': 14, 'valid': 44, 'unparseable': 2}
Mean generated visible tokens: 224.6. Mean of response-level mean logprobs: -0.5906.

## Interpretation

Both modes can retrieve Amathlai. Reasoning retrieved it substantially more frequently in this fresh batch (33.3% versus 5.0%; 30.0% versus 5.0% under strict exact-name scoring). It still did not achieve a strict majority across all attempts. With accepted-name variants grouped, Amathlai is the reasoning plurality; Sarah is the direct plurality if unrelated names are not collapsed. Keziah becomes the direct plurality if its two extra-descriptive answers are also grouped. None of these plurality distinctions changes target frequency.

Generated explanations can be incorrect even when the final name is right. See `target-responses.md` for all hits and the original JSON files for every response.
