# Self-consistency playground

Explore how a local language model answers the same question with **direct prompting**, **step-by-step prompting**, and **self-refinement**. Sample multiple responses, compare the final-answer distribution, and inspect whole-response log probabilities.

Built with Python and [Ollama](https://ollama.com/). Each run saves its responses, prompts, seeds, settings, and scores as JSON.

- [Experiment overview](#experiment-overview) — comparisons, refinement examples, and unsuccessful follow-ups.
- [Self-refinement experiments](#self-refinement-experiments) — answer progressions, successful correction, and failures.
- [Featured experiment: Abraham’s mother](#abraham-experiment-october-27-2026) — commands, results, and saved evidence.
- [Live demos](demos/README.md) — selected examples with exact commands and seeds.
- [Detailed usage](docs/usage.md) — refinement, extraction, scoring, and reproducibility.

## Quick start

Requires Python 3.9+ and Ollama. From the repository root, create an environment and install dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The repository includes a `.python-version` for the original author's pyenv environment. If pyenv reports that it is missing, use `PYENV_VERSION=system python3 -m venv .venv` for the first command, or follow the [pyenv setup](docs/usage.md#setup-and-general-usage).

Start Ollama and make the model available locally (`ollama pull llama3.1:latest` if needed). Then run:

```sh
python main.py 'Who wrote the Mishneh Torah?' -n 5 --mode reason --verbose
```

Use `--mode direct` for short answers. Add `--logprobs` to see a second table ranking individual responses by their mean token log probability.

| Option | Purpose |
|---|---|
| `-n 30` | Generate 30 independent samples |
| `--mode direct` / `--mode reason` | Short answer / explanation before the answer |
| `--seed 42` | Start a consecutive range of sample seeds |
| `--temperature 0.8` | Set sampling variability |
| `--verbose` | Show complete responses and the exact shared prompt |
| `--logprobs` | Record and rank whole-response token scores |
| `--self-refine 2` | Critique and revise each draft twice |
| `--aliases PATH` | Group explicitly listed answer variants for voting |
| `--plain` | Use plain terminal output |

Run `python main.py --help` for all options. New runs are saved in `runs/`; saved runs can be replayed without calling a model.

## Experiment overview

The repository includes several questions and follow-up experiments—not just Abraham’s mother. The table summarizes the saved results; links lead to the commands, seeds, full distributions, or original responses.

**Direct → reasoning** counts below use all attempted samples. They measure the named target answer, not whether the entire explanation is correct. Some early comparisons use different seed ranges; the linked reports spell out the settings and counting rules.

| Experiment | Observed result | Details and evidence |
|---|---|---|
| **Rabbi Akiva’s age when he began learning Torah** | Age 40: **0/30 → 23/30**. A wrong direct majority becomes a correct reasoning majority; different seed ranges. | [Commands and seeds](demos/README.md#rabbi-akiva-a-wrong-majority-becomes-a-correct-majority) · [Explanation review](runs/three-question-review/report.md) |
| **Hillel’s peer** | Shammai/Shamai: **7/30 → 26/30**; different seed ranges. | [Commands and seeds](demos/README.md#hillels-peer-shammai-becomes-dominant) |
| **Abraham’s mother: fresh 60-sample comparison** | Exact Amathlai: **3/60 → 18/60**, or 20/60 reasoning with the documented alternate spellings; matched seeds. | [Full report](runs/abraham-fresh-60/report.md) · [Explanation review](runs/abraham-fresh-60/explanation-review.md) |
| **Abraham’s mother: selected live-demo batches** | Exact Amathlai: **0/30 → 5/30**; deliberately selected, different seed ranges. The zero-hit batch is not representative of all direct runs. | [Commands and seeds](demos/README.md#abrahams-mother-no-direct-hits-in-a-selected-30-sample-batch) |
| **Abraham’s mother: October 27 comparison** | Exact Amathlai: **3/30 → 11/30**; matched seeds and corrected question wording. Also compares response logprobs. | [Commands and results below](#abraham-experiment-october-27-2026) |
| **Explicit Shabbat prohibition** | Parsed fire answers: **1/30 → 6/30**. Recovering a direct answer missing its final marker gives 2/30. Different seeds; broad question wording makes this a target-retrieval comparison. | [Commands and seeds](demos/README.md#optional-fire-appears-more-often-but-the-evidence-is-weaker) · [Review](runs/three-question-review/report.md) |
| **David’s mother** | Nitzevet/Nitzebet: **1/10 in each mode**, accepting the spelling variant. Reasoning was not necessary to retrieve the name. | [Distributions and logprobs](runs/david-mother-reason-vs-direct.md) |
| **Merav’s husband** | Adriel: **20/30 → 22/30**, a much smaller observed difference. | [Direct run](runs/20261012T093658316134Z.json) · [Reasoning run](runs/20261012T093713864122Z.json) |
| **Tree of Knowledge: initial grape result** | One reasoning grape answer in 30 samples, none in direct mode. Historical top-p settings of 0.9 and 0.95 produced identical responses within each mode. | [Original comparison](runs/tree-sampling-experiment/report.md) |
| **Tree of Knowledge: fresh follow-up** | **No grape final answers in either 100-sample mode**. Seven reasoning responses mentioned grapes in their explanation. | [Report](runs/tree-fresh-100/report.md) · [Grape mentions](runs/tree-fresh-100/grape-mentions.md) |
| **Tree of Knowledge: “name one option” wording** | Changing the question changed the distribution, but neither 30-sample reasoning condition produced a grape final answer. The preceding interrupted recovery run had no grape final answers in 64 samples. | [Wording comparison](runs/tree-one-option-comparison.md) |

## Self-refinement experiments

Here the model **drafts → critiques → revises**, repeatedly updating one answer. These runs test whether revision retrieves a better answer, rather than whether sampling produces more votes for it.

| Completed chain | Initial seed | Answer progression | Outcome |
|---|---:|---|---|
| **Shabbat prohibition**, 5 rounds | 706754937 | Carrying → carrying → carrying → **kindling a fire** → fire → fire | Retrieves the fire target at round 3. |
| **Rabbi Akiva**, 2 rounds, direct mode | 912400 | 3 → 3 → 3 | Repeats the wrong answer. |
| **Rabbi Akiva**, 2 rounds, reasoning mode | 1059670022 | 1 → 7 → 7 | Changes the answer, but never reaches 40. |
| **Rabbi Akiva**, 5 rounds, reasoning mode | 1036232012 | 13 → 13/15 variants → 13 → “unclear due to conflicting Talmudic sources” | Elaborates the initial mistake without reaching 40. |

**[All refinement commands, seeds, saved replays, and partial runs](demos/refinement.md)**

There are also six interrupted chains: two for Hillel and four for Akiva. The Akiva drafts already say 40, but no revisions completed; they do not demonstrate successful refinement. The guide lists these separately.

These are selected single-chain observations, not an estimate of refinement’s success rate. Revisions are accepted without factual quality scoring; logprobs do not choose which revision wins.

These results include successes, small differences, and failed recovery attempts. They do not establish that reasoning always helps or that longer responses alone cause an improvement. Correct final answers can also come with invented or irrelevant explanations.

Browse the [complete saved-run archive](runs/) for exploratory runs beyond these comparisons. To inspect any ordinary run or refinement chain without new sampling:

```sh
python replay_run.py PATH_TO_RUN.json --verbose
```

## Abraham experiment: October 27, 2026

**Can asking an ordinary chat model to reason before answering change which factual answers it produces?** This experiment asks: “Who was Abraham's mother according to Jewish tradition?” The reference answer is Amathlai / Amatlai (אמתלאי בת כרנבו), explicitly identified in [Bava Batra 91a:14](https://www.sefaria.org/Bava_Batra.91a.14).

We generated 30 direct responses and 30 prompted-reasoning responses with the **same 30 seeds, 927410000–927410029**, temperature 0.8, and the same local **Llama 3.1 8B, Q4_0** artifact. This is a general-purpose instruction-tuned chat model, not a dedicated native-thinking model. No retraining or external retrieval was used. `--thinking off` disables native thinking; `--mode reason` requests written reasoning in ordinary response text.

### Commands

Run from the repository root with Python dependencies installed (`python -m pip install -r requirements.txt`) and Ollama running with the model available locally. New runs save to automatically named JSON files in `runs/`.

**Direct answers:**

```sh
python main.py "Who was Abraham's mother according to Jewish tradition?" \
  --model llama3.1:latest --mode direct -n 30 --seed 927410000 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --logprobs --aliases demos/abraham-aliases.json --verbose
```

**Reasoning before answering:**

```sh
python main.py "Who was Abraham's mother according to Jewish tradition?" \
  --model llama3.1:latest --mode reason -n 30 --seed 927410000 \
  --temperature 0.8 --max-tokens 1024 --num-ctx 4096 --thinking off \
  --logprobs --aliases demos/abraham-aliases.json --verbose
```

### Observed results

| Measure | Direct | Prompted reasoning |
|---|---:|---:|
| Exact “Amathlai” final answers | 3/30 (10%) | 11/30 (36.7%) |
| “Sarah” final answers | 16/30 | 6/30 |
| Abstentions | 1 | 5 |
| Unparseable final answers | 0 | 1 |
| Most frequent extracted answer | Sarah | Amathlai |

Exact-name counts ignore case and trailing punctuation, but do not merge spelling variants or mixed answers. These are not exhaustive semantic accuracy scores: e.g., “Amathla” in direct mode and “Amatlai” in reasoning mode are separate entries. All percentages above use **all 30 attempts**. Amathlai is the reasoning run’s **plurality**, not a strict majority (11 of 24 eligible votes).

### What the logprobs show

The highest-ranked eligible answer is Amathlai in **both** runs. The score is the **mean token log probability of the entire response**, including any written explanation and final-answer marker—not the probability of the final name alone.

| Run | Top eligible samples | Final answer | Mean token logprob |
|---|---|---|---:|
| Direct | 2, 22, 25 (tie) | Amathlai | −0.185074 |
| Reasoning | 24 | Amathlai | −0.464490 |

“Eligible” means parseable, non-abstaining, complete answers. Reasoning sample **21**, an excluded `UNKNOWN` response, scores higher (**−0.434133**) than sample 24. Therefore, the correct claim is “highest among eligible answers,” not “highest among every response.” Scores are ranked **within each mode**, not compared as accuracy measures across the different prompts. The next two eligible reasoning responses are “Ammilat” and “His sister,” so this is not evidence of a generally reliable correctness detector.

### A correct name with an unreliable explanation

Reasoning sample **24**, seed **927410023**, gets the final name right but says:

> According to a passage in the Talmud (Bava Metzia 87a), Abraham's mother is identified as Amathlai.

That attribution is incorrect: the explicit identification is in **Bava Batra 91a:14**. The response also includes historical background that does not establish the name. [Read the complete response](demos/abraham-2026-10-27-sample-24.md).

This illustrates that a correct final answer—even one selected by the logprob ranking—can come with an unreliable explanation. It does **not** establish that the explanation played no useful causal role, or that extra length alone caused the improved answer frequency. This is one question with 30 samples per condition, not a general benchmark. The two conditions also have different token costs.

### Saved evidence and replay

- [Direct run: all 30 responses, requests, scores, and metadata](runs/20261027T100624295150Z.json)
- [Reasoning run: all 30 responses, requests, scores, and metadata](runs/20261027T101213336869Z.json)
- [Readable full text of reasoning sample 24](demos/abraham-2026-10-27-sample-24.md)

Replay the recorded results without Ollama or new sampling:

```sh
python replay_run.py runs/20261027T100624295150Z.json
python replay_run.py runs/20261027T101213336869Z.json
python replay_run.py runs/20261027T101213336869Z.json --sample 24 --verbose
```

Both recorded runs used Ollama **0.40.0** and manifest digest:

```text
42182419e9508c30c4b1fe55015f06b65f4ca4b9e28a744be55008d21998a093
```

The mutable `llama3.1:latest` tag may now resolve to a different artifact. These commands do not pin it. Check the digest in verbose output; model/runtime/hardware changes can affect reproducibility despite fixed seeds. Use the saved replays to inspect exactly the evidence behind this result.

## How to read the output

The prompt requests a final line in the form `FINAL: <short answer>`. The program extracts that line and groups matching answers into a voting table. Aliases can merge known spelling variants; the program does not infer semantic equivalence.

- **Most frequent is not necessarily correct.** A plurality is the largest answer group; a majority requires more than half of eligible votes.
- **Check exclusions.** Abstentions, malformed answers, truncations, and errors are counted separately. Compare target-answer rates using all attempts.
- **Logprob is not confidence in correctness.** It measures how probable the response’s wording was under the model. The score covers the entire response, including any explanation.
- **A seed is not a guarantee.** Model files, runtime versions, hardware, and prompts can affect results. Saved replays preserve the original evidence.

## Self-refinement

Generate a draft, ask the model to critique it, then ask it to revise. Repeat for a chosen number of rounds:

```sh
python main.py 'According to tradition, at what age did R Akiva start learning Torah?' \
  -n 1 --mode direct --self-refine 2 --verbose
```

Two rounds use up to five model calls per sample: one draft and two critique/revision pairs. The latest well-formed revision is retained; logprobs do not select revisions. Refinement can improve an answer or make it worse. See [the full procedure and failure handling](docs/usage.md#self-refinement).

## Tests

```sh
python -m unittest discover -q
```
