# Self-consistency playground


This folder selects the dedicated `self-consistency-playground` pyenv environment (Python 3.13.2) through `.python-version`. With your existing pyenv shell setup, `python`, `python3`, and `python -m pip` automatically use that environment while you are in this folder; no manual activation is needed. The environment lives under `~/.pyenv/versions/`, and the selection is local to this project. To recreate it on another machine with pyenv and pyenv-virtualenv installed:

```sh
pyenv install -s 3.13.2
pyenv virtualenv 3.13.2 self-consistency-playground
pyenv local self-consistency-playground
```

For an IDE that selects its interpreter separately, use `/Users/yon/.pyenv/versions/self-consistency-playground/bin/python`.

Sample an ordinary Ollama chat model repeatedly with a step-by-step reasoning prompt, extract each final answer, then vote. Requires Python 3.9+ and a running Ollama server; no model downloads are needed for your installed `llama3.1:latest`. Install the terminal formatting dependency with `python -m pip install -r requirements.txt`; generation still works with plain output if Rich is unavailable.

```sh
python3 main.py 'Who wrote the Mishneh Torah?' -n 5 --aliases aliases.example.json
python3 main.py 'Who wrote the Mishneh Torah?' -n 30 --temperature 0.8 --aliases aliases.example.json
```

The default is Llama 3.1 8B with temperature 0.8. Each sample starts a fresh conversation and uses a different seed. Generated reasoning is ordinary output text, followed by `FINAL: <short answer>`. Full responses, extracted reasoning and answers, seeds, timings, model metadata, generation counts, and vote totals are saved to `runs/`. Requests run sequentially. Each completed sample is saved immediately, including before a Ctrl+C interruption.

Compare prompted reasoning, sampled direct answers, and a greedy direct baseline:

```sh
python3 main.py 'Who wrote the Mishneh Torah?' -n 10 --seed 42 --mode reason --aliases aliases.example.json
python3 main.py 'Who wrote the Mishneh Torah?' -n 10 --seed 42 --mode direct --aliases aliases.example.json
python3 main.py 'Who wrote the Mishneh Torah?' -n 1 --temperature 0 --mode direct
```

Use `--model` to choose another installed model. A native reasoning model is optional:

```sh
python3 main.py 'Who wrote the Mishneh Torah?' --model deepseek-r1:latest --thinking on --max-tokens 4096 --num-ctx 8192
```

`--thinking` controls Ollama's native thinking channel; `--mode` controls the written prompt. Ordinary chat models receive no thinking flag. Models advertising thinking receive an explicit on/off flag; Ollama may reject controls unsupported by a particular model. See [Ollama thinking](https://docs.ollama.com/capabilities/thinking) and [chat API](https://docs.ollama.com/api/chat).

## Self-refinement

The local `Build_a_Reasoning_Model_(From_Scratch).pdf`, chapter 5 sections 5.7–5.8 (printed pages 167–176), describes a sequential procedure:

1. Generate an initial draft.
2. Give the same model the question and draft; request a short critique and fix plan.
3. Give it the question, current draft, and critique; generate a revised answer.
4. Repeat the critique/revision pair for a fixed number of rounds.

Enable this procedure with `--self-refine ROUNDS` (default `0`, disabled):

```sh
# One draft, two critique/revision rounds: five model calls in total.
python main.py 'According to tradition, at what age did R Akiva start learning Torah?' \
  -n 1 --mode direct --self-refine 2 --verbose

# Ten independent chains, each with one refinement round, then vote on final answers.
python main.py "Who was Abraham's mother according to Jewish tradition?" \
  -n 10 --mode reason --self-refine 1 --seed 12345 --verbose --logprobs
```

`-n` is the number of independent chains. Each uses up to `1 + 2 * ROUNDS` model calls. `--mode direct` requests short initial and revised answers; critiques still occur in separate calls. `--mode reason` asks for written reasoning in initial and revised answers. No specialized reasoning model or model training is needed. Each stage is a fresh request carrying the relevant question, current draft and, for revision, critique; earlier rounds do not accumulate into a growing chat history.

The console shows initial and revised answers, and both before/after voting distributions. `--verbose` adds the full drafts, critiques, revisions, and any native thinking. `--critique-max-tokens` defaults to 512; `--max-tokens` controls each draft/revision. Raise the critique budget if a critique truncates, and choose `--num-ctx` large enough for the question, draft, critique, and next output together.

This implements the book's **unscored** variant: the latest well-formed revision is retained, even if it changes the answer or abstains with `UNKNOWN`. There is no independent truth check or early stopping on unchanged answers. Critiques can be wrong, and refinement can damage a correct answer. Our prompts adapt the math-focused review to factual questions and use `FINAL:` instead of a boxed result.

The book also supports optional score-gated acceptance (its code accepts an equal or higher score). That variant is not implemented here. In particular, its average-logprob scorer re-scores each complete candidate against the **same original prompt**. Our Ollama generation logprobs condition each response on its own stage prompt, so `--logprobs` records diagnostic full-response scores for each call but **does not use them to select revisions**. The book's table 5.1 also finds that scoring does not consistently improve accuracy; its base-model unscored one-round result exceeds its two-round result.

JSON files retain `samples[].refinement.initial` and every round's draft, critique, revision, prompts, seeds, status, and acceptance decision. Top-level sample answer/response fields refer to the last retained answer. `sample.seed` remains the initial seed; `selected_generation_seed` records the final revision's seed. Initial seeds are `seed + sample_index` (zero-based), matching ordinary sampling; critique/revision seeds occupy a separate consecutive range after the initial seeds. JSON includes `initial_summary`, the final `summary`, and `completed_chains`.

Each completed stage is checkpointed immediately. An error, empty/truncated critique, or malformed/truncated revision stops that chain and preserves its previous draft and partial history. Incomplete chains are excluded from final voting, remain in the attempted denominator, and yield a nonzero exit code. A malformed initial answer can still be repaired if it has response text. Ctrl+C preserves the completed stages but does not automatically resume a run. Completed `UNKNOWN` answers are excluded from voting as usual. `compare_logprobs.py` does not replay refinement chains; collect stage scores with `--logprobs` during the run.

## Interpreting results

Use `-v` or `--verbose` to display each complete response in a separated terminal block, including the written reasoning and final-answer line, any separate native thinking, the extracted answer, voting status, and (with `--logprobs`) its score:

```sh
python main.py 'Who was the mom of king david' -n 10 --verbose --logprobs
```

This also works with `--mode direct`. Responses appear as each sample finishes, not token by token. Full text is displayed even for truncated or unparseable responses. Without the flag, the compact output remains the default. Display mode does not change the prompt or generation settings.

The terminal prints each sample's extracted final answer as it completes, then an answer distribution table with vote counts and percentages of valid votes, followed by the majority answer (or a tie/plurality notice). The saved JSON retains the machine-readable distribution and full responses.

Extraction uses an explicit marker: the prompt asks for exactly one final line, `FINAL: <short answer>`. The parser accepts that line only when it is the last nonblank line and the marker occurs on exactly one line. Everything before it is saved as reasoning. There is no second LLM call to infer the answer; responses that do not follow the format are excluded from voting.

- The unique largest answer group is the plurality. A strict majority requires more than half of valid votes. Ties produce no winner.
- `UNKNOWN`, malformed/missing final lines, truncated responses, and request errors are excluded and counted separately. Both valid-sample and all-attempted vote shares are reported.
- Normalization handles case, whitespace, surrounding punctuation, and Hebrew vowel marks. Supply explicit aliases for synonyms and transliterations; semantic equivalence is not inferred. Map variants directly to the same canonical name.
- `--max-tokens` defaults to 1024. Increase it if responses truncate; native thinking also uses this budget. `--num-ctx` defaults to 4096. Keep questions short enough to fit with generation.
- Nonzero temperature encourages variation but does not guarantee different answers. Seeds aid repeatability without guaranteeing identical results across hardware or versions.
- Agreement is not probability of truth. Samples can repeat the same misconception, and reasoning can introduce errors. Generated reasoning text is not proof of the model's internal computation.

To measure improvement, prepare many questions with independently verified accepted answers and aliases. Compare accuracy, excluded outputs, and generation cost across the three conditions and different sample counts. For Jewish learning, specify relevant texts or traditions and distinguish disputed interpretations from questions with one accepted factual answer. A smoke test verifies the pipeline, not an accuracy benefit.

```sh
python3 -m unittest -v
```

## Compare full-response log probabilities

To run a controlled direct-versus-reasoning comparison from a saved run:

```sh
python run_sampling_experiment.py runs/20261011T145131709506Z.json --output-dir runs/my-sampling-experiment --samples 100 --seed 731204000
python analyze_sampling_experiment.py runs/my-sampling-experiment
```

Use a new output directory for each experiment. The runner copies the source question, model, temperature, context size, and output budget. `--seed` selects a fresh starting seed; each condition uses the same seed range and records log probabilities. The analyzer is specific to the Tree of Knowledge question: it groups simple fruit-name variants and counts grape/vine, fig, and wheat as the predefined target groups. Its report includes all attempted samples, full-response diversity, token costs, and target-response texts. Etrog and other answers are retained separately; counting the three target groups is not a general correctness judgment. Use a new seed range for follow-up experiments rather than repeatedly replaying a known successful sample.

For new runs, add `--logprobs` to save probabilities during generation and print each response's mean log probability. For a controlled prompt comparison, keep the question, model, temperature, seed range, and limits identical:

```sh
python main.py 'Who was the mom of king david' --model llama3.1:latest -n 10 --temperature 0.8 --seed 308921333 --mode reason --logprobs
python main.py 'Who was the mom of king david' --model llama3.1:latest -n 10 --temperature 0.8 --seed 308921333 --mode direct --logprobs
```

The completed comparison is in `runs/david-mother-reason-vs-direct.md`. Include abstentions in the denominator when comparing target-answer rates. Full-response mean log probabilities are sensitive to writing style and the different prefixes in each condition, even after dividing by token count; they are not accuracy scores.

Replay a saved run with the original prompts, seeds, and generation settings:

```sh
python compare_logprobs.py runs/20261011T104712285208Z.json --output runs/logprob-comparison.json
```

Choose a new output path each time. This requests Ollama token log probabilities and computes their sum divided by the number of tokens across the **entire visible response**, including reasoning and the final-answer line. It verifies that returned token bytes reconstruct the text and records whether each replay exactly matches the original response. A nonmatching replay scores the new text, not the original. Results include raw responses, individual token log probabilities, mean log probability, and perplexity; completed samples are saved as they finish.

Higher mean log probability (closer to zero) means more probable wording under the API-reported distribution. It is not a probability that the answer is correct. Length normalization makes different lengths easier to compare, but fluent boilerplate and repeated misconceptions can still score highly. Scores exclude stop tokens not returned by Ollama and are conditional on each response's own preceding tokens. This comparison currently requires logprob bytes to match the visible response exactly; responses with separate native thinking may not satisfy that condition.

## Terminal output

`--verbose` now uses Rich panels for full model responses and refinement stages, with a vote table at the end. Add `--plain` for the original text output, or set `NO_COLOR=1` for panels without colors. Formatting does not change prompts, sampling, or saved JSON.

Use `python replay_run.py PATH_TO_RUN.json --verbose` to present a saved run without calling Ollama. Add `--sample INDEX` for one response or `--aliases PATH` for explicit vote grouping. The replay labels itself as saved output. See [the demo guide](demos/README.md) for ready-to-run examples.
