# Live demos: sampling, voting, and self-refinement

For the corrected-prompt, matched-seed comparison with 30 samples per mode, see the [October 27 Abraham experiment](../README.md#abraham-experiment-october-27-2026). The selected live demos below are older runs.

Run these commands from the repository root.

## Suggested order

1. **Akiva**: show how prompting changes the answer distribution and flips the majority.
2. **Hillel**: a second clear distribution shift.
3. **Abraham**: Amathlai appears under reasoning but not in the selected direct batch; explanations can still be unreliable.
4. **Shabbat refinement**: watch carrying change to kindling a fire in round 3.

Use one selected response live when time is tight, then replay the saved full-batch distribution. A selected successful seed illustrates behavior; it does not estimate its frequency. Full-batch commands below reproduce the original sample counts.

## Setup and output

```sh
cd /Users/yon/projects/self_consistency_playground
python -m pip install -r requirements.txt
ollama list
```

The saved model is `llama3.1:latest`, Llama 3.1 8B Q4_0, an ordinary chat model. `--mode reason` requests written reasoning; `--thinking off` is used throughout. Ollama must be running for live commands. Rich formats verbose text in panels and distributions as tables. `--plain` restores plain output; `NO_COLOR=1` suppresses colors while retaining panels. Model text is displayed literally, including any bracketed text.

The exact question wording—including old typos—is intentional. Commands preserve the saved temperature, token/context budgets, mode, seeds, and logprob setting. New results get new timestamped files; original runs are never overwritten. Aliases only group votes after generation and do not change the prompt.

A fixed seed is a reproduction aid, not a guarantee across model files, Ollama versions, hardware, or backend changes. Prompt strings in these saved runs were checked against the current program. No new sampling was performed to select these examples.

## At a glance

Target counts use **all attempts**, including abstentions and malformed answers. The terminal also shows percentages among valid votes; those have a different denominator.

| Target | Direct | Reasoning | Seed comparison |
|---|---:|---:|---|
| Akiva: 40 | 0/30 (0%) | 23/30 (76.7%) | Different seed ranges |
| Hillel: Shammai / Shamai | 7/30 (23.3%) | 26/30 (86.7%) | Different seed ranges |
| Abraham: exact Amathlai answer | 0/30 (0%) | 5/30 (16.7%) | Different, selected seed ranges |
| Explicit Shabbat fire prohibition | 1/30 (3.3%) | 6/30 (20%) | Different seed ranges; exploratory |

These selected runs show observed shifts under a reasoning prompt. They do not isolate response length as the cause or establish a general advantage on all questions. Voting can concentrate on a wrong answer. Correct final retrieval does not validate the explanation.

## Rabbi Akiva: a wrong majority becomes a correct majority

### Direct

[Saved run](../runs/20261011T163951981371Z.json) · seeds **1028498544–1028498573** · target **0/30** · saved generation time about **5 seconds**.

```sh
python main.py 'Accroding to tradition, at what age did R Akiva start learing Torah?' \
  --model llama3.1:latest --mode direct -n 30 --seed 1028498544 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/akiva-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261011T163951981371Z.json --aliases demos/akiva-aliases.json
```

### Reason

[Saved run](../runs/20261011T164004145264Z.json) · seeds **270350594–270350623** · target **23/30** · saved generation time about **117 seconds**.

```sh
python main.py 'Accroding to tradition, at what age did R Akiva start learing Torah?' \
  --model llama3.1:latest --mode reason -n 30 --seed 270350594 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/akiva-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261011T164004145264Z.json --aliases demos/akiva-aliases.json
```

### Short live illustration

Selected saved sample **6**, seed **270350599**, final **40.**. This is a chosen success, not a new frequency comparison.

```sh
python main.py 'Accroding to tradition, at what age did R Akiva start learing Torah?' \
  --model llama3.1:latest --mode reason -n 1 --seed 270350599 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/akiva-aliases.json --verbose
```

Exact saved response as a fallback:

```sh
python replay_run.py runs/20261011T164004145264Z.json --sample 6 --verbose
```

**What to point out:** direct answers group into age 3 (29) and age 5 (1). Reasoning yields age 40 (23), age 3 (3), age 13 (3), and age 18 (1). This is a shift from a wrong majority to a correct majority. Reference: [Avot DeRabbi Natan 6:2](https://www.sefaria.org/Avot_DeRabbi_Natan.6.2). Some successful explanations still invent stories; see [the explanation review](../runs/three-question-review/report.md).

## Hillel’s peer: Shammai becomes dominant

### Direct

[Saved run](../runs/20261012T152110726958Z.json) · seeds **152597361–152597390** · target **7/30** · saved generation time about **11 seconds**.

```sh
python main.py 'Who was the peer of Hillel?' \
  --model llama3.1:latest --mode direct -n 30 --seed 152597361 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/hillel-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261012T152110726958Z.json --aliases demos/hillel-aliases.json
```

### Reason

[Saved run](../runs/20261012T152145651599Z.json) · seeds **125595393–125595422** · target **26/30** · saved generation time about **141 seconds**.

```sh
python main.py 'Who was the peer of Hillel?' \
  --model llama3.1:latest --mode reason -n 30 --seed 125595393 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/hillel-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261012T152145651599Z.json --aliases demos/hillel-aliases.json
```

### Short live illustration

Selected saved sample **1**, seed **125595393**, final **Shammai.**. This is a chosen success, not a new frequency comparison.

```sh
python main.py 'Who was the peer of Hillel?' \
  --model llama3.1:latest --mode reason -n 1 --seed 125595393 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/hillel-aliases.json --verbose
```

Exact saved response as a fallback:

```sh
python replay_run.py runs/20261012T152145651599Z.json --sample 1 --verbose
```

**What to point out:** count Shamai as a spelling of Shammai; do not count “Shammaites” (the school) as the named peer. Direct has 4 Shammai + 3 Shamai; reasoning has 26 Shammai. The direct plurality is Shemaiah and Avtalion (11 after spelling grouping), while reasoning has a Shammai majority. Reference: [Pirkei Avot 1:12](https://www.sefaria.org/Pirkei_Avot.1.12), which pairs Hillel and Shammai and names their predecessors.

## Abraham’s mother: no direct hits in a selected 30-sample batch

### Direct

[Saved run](../runs/20261013T053242494010Z.json) · seeds **842617000–842617029** · exact Amathlai answers **0/30**.

```sh
python main.py 'Who was the Abraham'"'"'s mom according to Jewish tradition?' \
  --model llama3.1:latest --mode direct -n 30 --seed 842617000 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --logprobs --aliases demos/abraham-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261013T053242494010Z.json --aliases demos/abraham-aliases.json
```

### Reason

[Saved run](../runs/20261013T053309169796Z.json) · seeds **842617054–842617083** · exact Amathlai answers **5/30** (plus qualified mentions described below).

```sh
python main.py 'Who was the Abraham'"'"'s mom according to Jewish tradition?' \
  --model llama3.1:latest --mode reason -n 30 --seed 842617054 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --logprobs --aliases demos/abraham-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261013T053309169796Z.json --aliases demos/abraham-aliases.json
```

### Short live illustration

Selected saved sample **55**, seed **842617054**, final **Amathlai.**. This is a chosen success, not a new frequency comparison.

```sh
python main.py 'Who was the Abraham'"'"'s mom according to Jewish tradition?' \
  --model llama3.1:latest --mode reason -n 1 --seed 842617054 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --logprobs --aliases demos/abraham-aliases.json --verbose
```

Exact saved response as a fallback:

```sh
python replay_run.py runs/abraham-fresh-60/reason.json --sample 55 --verbose
```

**What to point out:** both live commands use 30 samples. This selected direct batch gives no Amathlai answers. The reasoning batch gives **5/30 exact-name answers** (ignoring case and final punctuation), plus two qualified answers naming Amathlai and one ambiguous “Amathlai or Amalek” answer. These additional mentions are not merged into the exact-name count or the alias-based voting table. Amathlai is not the voting winner in this batch.

Thirty samples keeps the live demonstration shorter and gives both modes the same number of attempts; it is not a statistical power calculation. These are selected illustrations using **different seed ranges**, not a controlled matched-seed comparison. Zero hits here does not mean direct mode cannot retrieve Amathlai: the earlier 60-sample direct run had 3 hits. For the stronger matched comparison, retain the original [60-sample analysis](../runs/abraham-fresh-60/report.md): 3/60 direct versus 18/60 strict reasoning (20/60 with the documented alternate spellings). Correct final names do not validate the generated explanations; see the [explanation review](../runs/abraham-fresh-60/explanation-review.md). Reference: [Bava Batra 91a](https://www.sefaria.org/Bava_Batra.91a).

## Optional: fire appears more often, but the evidence is weaker

### Direct

[Saved run](../runs/20261011T165211453642Z.json) · seeds **87388049–87388078** · target **1/30** · saved generation time about **13 seconds**.

```sh
python main.py 'which of the 39 Melachot forbidden on Shabbat is mentioned explicitly in the Torah' \
  --model llama3.1:latest --mode direct -n 30 --seed 87388049 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/melachot-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261011T165211453642Z.json --aliases demos/melachot-aliases.json
```

### Reason

[Saved run](../runs/20261011T165236131510Z.json) · seeds **586203622–586203651** · target **6/30** · saved generation time about **199 seconds**.

```sh
python main.py 'which of the 39 Melachot forbidden on Shabbat is mentioned explicitly in the Torah' \
  --model llama3.1:latest --mode reason -n 30 --seed 586203622 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/melachot-aliases.json --verbose
```

Replay the saved distribution without generating:

```sh
python replay_run.py runs/20261011T165236131510Z.json --aliases demos/melachot-aliases.json
```

### Short live illustration

Selected saved sample **12**, seed **586203633**, final **Kindling a fire.**. This is a chosen success, not a new frequency comparison.

```sh
python main.py 'which of the 39 Melachot forbidden on Shabbat is mentioned explicitly in the Torah' \
  --model llama3.1:latest --mode reason -n 1 --seed 586203633 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --aliases demos/melachot-aliases.json --verbose
```

Exact saved response as a fallback:

```sh
python replay_run.py runs/20261011T165236131510Z.json --sample 12 --verbose
```

**What to point out:** the direct run also contains a clear fire answer without a FINAL marker, so manual content recovery gives 2/30 versus 6/30. “Working with fire” is kept separate as vague. This is weaker evidence than the first three examples. The broad wording can admit other readings (plowing and harvest are mentioned in Exodus 34:21); call this the **fire-target retrieval rate**, not exhaustive accuracy. See the [detailed review](../runs/three-question-review/report.md).

## Self-refinement: carrying → kindling a fire

[Original complete run](../runs/20261012T211032886271Z.json). Initial seed **706754937**, one chain, five rounds, reasoning mode. All stages were completed. The saved chain took about **129 seconds** of generation.

```sh
python main.py 'which of the forbidden works on Shabbat is explicitly mentioned in the Torah?' \
  --model llama3.1:latest --mode reason -n 1 --seed 706754937 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --self-refine 5 --critique-max-tokens 512 --verbose
```

| Stage | Generation seed | Extracted answer |
|---|---:|---|
| Initial | 706754937 | Hotza (carrying). |

| Round 1 revision (critique seed 706754938) | 706754939 | Hotza (carrying). |

| Round 2 revision (critique seed 706754940) | 706754941 | Hotza (carrying). |

| Round 3 revision (critique seed 706754942) | 706754943 | Kindling a fire. |

| Round 4 revision (critique seed 706754944) | 706754945 | Kindling a fire. |

| Round 5 revision (critique seed 706754946) | 706754947 | Kindling a fire. |


The first change happens at **round 3**, revision seed **706754943**. Rounds 4–5 retain fire. A shorter live version can use `--self-refine 3` with the same command: for this one-chain run, the initial and first three round seeds/prompts are unchanged. Keep `-n 1`; changing the sample count changes refinement-stage seeds.

The current procedure accepts every parseable revision without quality scoring. This is an example of successful self-refinement, not evidence that a probability score selected the right answer. The direct prohibition on kindling appears in [Exodus 35:3](https://www.sefaria.org/Exodus.35.3); the broad wording of the question should still be acknowledged.

Reliable on-stage fallback (saved text; no model call):

```sh
python replay_run.py runs/20261012T211032886271Z.json --verbose
```

## Other runs: useful counterexamples, not headline successes

- **David’s mother:** Nitzevet appears in reasoning, but the matched direct run also retrieves “Nitzebet”; this does not establish reasoning-only access. [Earlier comparison](../runs/david-mother-reason-vs-direct.md).
- **Tree of knowledge:** the grape output was rare and later recovery attempts did not reproduce it reliably. The fresh 100-per-mode comparison found no grape in either mode. [Report](../runs/tree-fresh-100/report.md). Avoid presenting it as a dependable live success.
- **Merav’s husband:** the saved completed pairs retrieve Adriel in 20/30 direct and 22/30 reasoning responses; the difference is small compared with Akiva and Hillel.
- **Akiva self-refinement:** another saved run stays at the wrong age 3 through two revisions. Replay `runs/self-refinement-akiva-smoke.json` to demonstrate that refinement can fail.

## Reproduction details

The batch seed is the seed of sample 1; sample i uses `batch_seed + i - 1`. For self-refinement, stage seeds also depend on the number of chains and requested rounds. Individual selected responses are demonstrations, not replacements for the complete distribution.

The aliases in this folder make grouping explicit and reviewable. Approximate unrelated Abraham names and “Shammaites” are intentionally not mapped to the target. Raw answers stay unchanged in the JSON. Grouping affects voting only; it is not a correctness verifier. [manifest.json](manifest.json) records the selected source files, commands, and every target-hit seed.

For a one-hour talk, run one or two short examples and the three-round Shabbat chain live; use saved replays for the 30/60-sample comparisons. Recorded runtimes are observations from the original machine, not promises for a new run.
