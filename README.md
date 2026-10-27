# Self-consistency playground

Explore how a local language model answers the same question with **direct prompting**, **step-by-step prompting**, and **self-refinement**. Sample multiple responses, compare the final-answer distribution, and inspect whole-response log probabilities.

Built with Python and [Ollama](https://ollama.com/). Each run saves its responses, prompts, seeds, settings, and scores as JSON.

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
