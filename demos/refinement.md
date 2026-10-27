# Self-refinement experiments

[Back to the overview](../README.md#self-refinement-experiments)

A chain starts with one draft. Each round asks the same model to critique the current draft, then revise it. The program retains the latest parseable revision without checking its factual quality. Logprobs, when collected, do not select revisions.

These are exploratory single-chain runs, not a benchmark or a controlled comparison of round counts. Four tracked chains completed; six were interrupted. An interrupted run retaining its initial correct answer is not evidence that refinement preserved correctness through all requested rounds.

## Completed chains

| Question | Initial seed | Rounds | Answer progression | Saved run |
|---|---:|---:|---|---|
| According to tradition, at what age did R Akiva start learning Torah? | 1059670022 | 2 | one. → 7. → 7. | [JSON](../runs/20261012T210540939103Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 1036232012 | 5 | 13 → 13 (or possibly 15, based on alternative Talmudic source) → 13 or 15 years old → 13 or 15 years old → 13 years old → The exact age at which R Akiva started learning Torah is unclear due to conflicting Talmudic sources. | [JSON](../runs/20261012T210908313446Z.json) |
| which of the forbidden works on Shabbat is explicitly mentioned in the Torah? | 706754937 | 5 | Hotza (carrying). → Hotza (carrying). → Hotza (carrying). → Kindling a fire. → Kindling a fire. → Kindling a fire. | [JSON](../runs/20261012T211032886271Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 912400 | 2 | 3 → 3 → 3 | [JSON](../runs/self-refinement-akiva-smoke.json) |

The Shabbat chain retrieves kindling a fire at round 3 and retains it through round 5. The three completed Akiva chains never reach the target age of 40: one repeats 3, one changes 1 to 7, and one elaborates a supposed conflict between ages 13 and 15. Revising an explanation can reinforce its original mistake.

## Commands and exact saved replays

Run from the repository root after [setup](../README.md#quick-start). These commands use the saved settings. A new generation may differ across model artifacts, runtimes, or hardware; replay displays the recorded evidence without calling Ollama.

### Seed 1059670022: According to tradition, at what age did R Akiva start learning Torah?

```sh
python main.py 'According to tradition, at what age did R Akiva start learning Torah?' \
  --model llama3.1:latest --mode reason -n 1 --seed 1059670022 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --self-refine 2 --critique-max-tokens 512 --verbose

python replay_run.py runs/20261012T210540939103Z.json --verbose
```

### Seed 1036232012: According to tradition, at what age did R Akiva start learning Torah?

```sh
python main.py 'According to tradition, at what age did R Akiva start learning Torah?' \
  --model llama3.1:latest --mode reason -n 1 --seed 1036232012 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --self-refine 5 --critique-max-tokens 512 --verbose

python replay_run.py runs/20261012T210908313446Z.json --verbose
```

### Seed 706754937: which of the forbidden works on Shabbat is explicitly mentioned in the Torah?

```sh
python main.py 'which of the forbidden works on Shabbat is explicitly mentioned in the Torah?' \
  --model llama3.1:latest --mode reason -n 1 --seed 706754937 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --self-refine 5 --critique-max-tokens 512 --verbose

python replay_run.py runs/20261012T211032886271Z.json --verbose
```

### Seed 912400: According to tradition, at what age did R Akiva start learning Torah?

```sh
python main.py 'According to tradition, at what age did R Akiva start learning Torah?' \
  --model llama3.1:latest --mode direct -n 1 --seed 912400 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --self-refine 2 --critique-max-tokens 512 --verbose --logprobs

python replay_run.py runs/self-refinement-akiva-smoke.json --verbose
```

## Interrupted chains

These are partial records. “Completed revisions” counts accepted revisions, not critiques or started rounds. They should not be counted as completed refinement outcomes.

| Question | Initial seed | Requested rounds | Completed revisions | Initial → retained answer | Saved run |
|---|---:|---:|---:|---|---|
| Who was the peer of Hillel? | 895499276 | 2 | 1 | Shammai → Shammai | [JSON](../runs/20261012T210437136233Z.json) |
| Who was the peer of Hillel? | 975235390 | 2 | 0 | Shammai → Shammai | [JSON](../runs/20261012T210459242590Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 30705197 | 5 | 0 | 40 → 40 | [JSON](../runs/20261012T210627556144Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 984253655 | 5 | 0 | 40. → 40. | [JSON](../runs/20261012T210635717616Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 713306997 | 5 | 0 | 40. → 40. | [JSON](../runs/20261012T210643232569Z.json) |
| According to tradition, at what age did R Akiva start learning Torah? | 363380335 | 5 | 0 | 40. → 40. | [JSON](../runs/20261012T210859713051Z.json) |

Use `python replay_run.py PATH_TO_RUN.json --verbose` to inspect any partial record. Changing the requested round count alongside the seed is not a controlled test of whether more rounds help.
