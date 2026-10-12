# Three-question review: generated reasoning, factual retrieval, and voting

This is a retrospective analysis of saved runs, not a new sampling experiment. All primary comparisons use llama3.1:latest (8B, Q4_0), temperature 0.8, 1024 maximum output tokens, context 4096, and native thinking off. The question text is identical within each pair; the instruction changes between direct and step-by-step answers. Akiva and melachot use different seed schedules between conditions; the fresh Abraham comparison uses the same 60-seed schedule. Log probabilities were not collected for the Akiva and melachot pairs.

## Main counts

Every attempted sample remains in the denominator, including abstentions and formatting failures. These are target-answer retrieval rates, not endorsements of the entire response.

| Question / target | Direct | Reasoning | Interpretation |
|---|---:|---:|---|
| Rabbi Akiva began Torah study at 40 | 0/30 (0%) | 23/30 (76.7%) | Strong observed shift; changes an overwhelmingly wrong vote into a correct majority. |
| Explicit Shabbat prohibition: kindling fire, parsed FINAL only | 1/30 (3.3%) | 6/30 (20%) | Direction favors reasoning, but small counts and scoring issues. |
| Same fire target, recovering a clear answer without FINAL | 2/30 (6.7%) | 6/30 (20%) | Fairer content comparison; a seventh reasoning answer says only “working with fire.” |
| Abraham's mother: accepted Amathlai name | 3/60 (5%) | 20/60 (33.3%) | Strong observed increase; correct plurality after grouping names, not a majority of attempts. |

Abraham's strict exact-name rule gives 18/60 reasoning versus 3/60 direct. The two additional accepted outputs explicitly include Amathlai alongside another spelling.

The traditional age 40 is stated in [Avot DeRabbi Natan 6:2](https://www.sefaria.org/Avot_DeRabbi_Natan.6.2?lang=bi&with=all). The fire prohibition is explicit in [Exodus 35:3](https://www.sefaria.org/Exodus.35.3?with=Commentary+ConnectionsList). Abraham's mother is named Amatlai bat Karnevo in [Bava Batra 91a](https://www.sefaria.org/Bava_Batra.91a?lang=en).

## Rabbi Akiva: strongest contrast

Direct answers: age 3 in 29/30, age 5 in 1/30. Reasoning answers: 40 in 23/30, 3 in 3/30, 13 in 3/30, 18 in 1/30. All answers parsed successfully.

This is stronger than discovering one rare correct answer: reasoning makes the correct answer dominant. Conversely, 29/30 agreement on a wrong direct answer shows that self-consistency is not factual verification or calibrated confidence. Zero correct direct samples does not imply that the probability of a correct direct response is zero.

The explanations remain mixed. Sample 6 recalls the traditional unlearned shepherd and late start; sample 24 sensibly distinguishes the typical young starting age from Akiva's exceptional biography. But successful sample 8 introduces sheep arguing about Torah interpretation; sample 30 introduces death and revival by the angel of death. These stories are unsupported by the checked source and should not be accepted just because the final age is right. Many successful responses state 40 early and then elaborate, so their visible text does not demonstrate a derivation of the number.

## Melachot: retrieval and selection can come apart

Clear final fire answers occur in reasoning samples 5, 6, 12, 16, 27, 28; sample 8's “working with fire” is vague and is reported separately. Direct sample 22 has a valid final fire answer; sample 4 also says lighting a fire but lacks the required FINAL marker. Excluding sample 4 measures formatting compliance as well as knowledge.

Grouping making, lighting, and kindling fire gives the reasoning plurality (6 clear answers, or 7 with the vague response); building has 3 and carrying 2. Direct outputs are highly scattered, including numerous malformed or unrelated terms. Without semantic grouping, surface spellings split equivalent votes. The generic status “valid” means the FINAL format parsed, not that the answer is factually valid.

Some explanations actively discard useful information. Reasoning sample 4 correctly mentions the fire prohibition and Exodus 35:3 but rejects it through an incoherent distinction between lighting and kindling and concludes building. Sample 7 mentions the same prohibition but claims it is not among the 39 and abstains. Sample 22 mentions it, then finishes with “Yakor.” Thus the useful answer can appear in the generated candidate text and be lost before FINAL.

Successful sample 5 attributes the prohibition to Exodus 35:25; that verse concerns women spinning, not the fire prohibition ([text](https://www.sefaria.org/Exodus.35.25?lang=bi&with=Steinsaltz)). Samples 12, 27, 28 do cite the relevant Exodus 35:3, while mixing in other questionable claims. Correct final answer and reliable explanation remain separate outcomes.

There is a wording ambiguity: “mentioned explicitly in the Torah” is broader than “singled out by a direct prohibition on kindling.” [Exodus 34:21](https://www.sefaria.org/Exodus.34?lang2=en&with=Translations) explicitly mentions plowing and harvest. Direct sample 21 and reasoning samples 24 and 30 answer plowing; those final answers should not simply be classified as false under the broad wording, although their explanations require separate checking. The table therefore measures retrieval of the fire target, not comprehensive accuracy on every defensible reading. Future runs should fix an accepted-answer rubric before sampling.

The small fire counts do not establish a stable effect by themselves. Exploratory two-sided Fisher exact p-values are 0.103 for parsed 1 versus 6, 0.254 for manually recovered 2 versus 6, and 0.145 for 2 versus 7. These are descriptive retrospective checks, not preregistered evidence across a representative question set.

## Abraham: strong retrieval gain, limited explanation quality

Use the fresh 60-per-condition comparison as the primary evidence. Grouped direct answers are Keziah 23, Sarah 22, Jochebed 6, Amathlai 3, other named answers 2, abstentions 2, and missing finals 2. Reasoning gives Amathlai 20, Sarah 17, abstentions 14, Terah's wife 2, five other names, and missing finals 2. The target becomes the plurality but not a majority. More reasoning also increases abstention here.

The [prior explanation review](../abraham-fresh-60/explanation-review.md) found both sensible wife/mother disambiguation and serious contradictions: successful samples 20, 28, 51 deny that the Talmud names the mother despite Bava Batra 91a. Samples 13 and 41 conflate Sarah's roles. Sample 55 offers broadly reasonable biblical-versus-rabbinic context. The retrieval gain does not establish reliable chains of inference.

Earlier runs are not pooled: the older “Who was the mom of Abraham” run used temperature 0.6 and different wording (0/30 accepted names); the later reasoning run was interrupted at 11 responses (1 accepted name) while its exploratory direct run had 2/30. Different wording, temperature, seeds, and stopping conditions make those weaker comparisons. The fresh matched experiment is the relevant replication.

## Cross-question conclusions

1. The step-by-step prompt changes the final-answer distribution substantially. Akiva and Abraham show strong increases in the target's probability; melachot is suggestive. It is inaccurate to say that a fact which fails to appear in direct samples cannot be surfaced through a reasoning prompt.
2. This is not merely increased diversity. Akiva becomes concentrated on the correct answer. Direct melachot answers are already diverse but mostly unhelpful. The important quantity is probability mass on useful answers, not the number of different strings generated.
3. Correct retrieval does not require the visible explanation to be wholly correct. Unsupported narrative and wrong citations coexist with correct final facts. The traces do not identify the internal causal mechanism.
4. A plausible explanation is that intermediate, topical text changes the context and activates different associations before the final answer. This fits the data, but so could a combination of prompt framing, disambiguation, and additional computation. Length alone has not been isolated.
5. Voting helps only when the prompted distribution favors the truth. Akiva shows a correct majority; Abraham and melachot give correct pluralities under stated grouping rules. A highly consistent false answer remains possible, as Akiva direct illustrates.
6. Candidate generation and selection should be measured separately. Count correct FINAL answers, correct candidates mentioned anywhere, and source-supported explanations as different metrics. Mentioning the answer only as a rejected possibility must not count as answering correctly. Melachot samples show why an independent verifier could help.
7. These three selected questions do not establish general accuracy gains across Jewish learning. Sampling uncertainty within a question and generalization across questions are different issues. Do not pool all samples into a universal accuracy estimate.

## Length and cost

Mean generated tokens reported by Ollama (eval_count, not logprob-reconstructed visible-token counts): Akiva direct 9.7 versus reasoning 216.5; melachot 24.1 versus 359.5; Abraham 18.6 versus 225.6. These comparisons match numbers of samples, not compute/token budgets. They cannot establish cost efficiency or that “more tokens” alone produces the gain. Average sequence logprob would not validate explanations, and is unavailable in the Akiva/melachot runs.

A useful next experiment would use Akiva as the clearest case, comparing direct answers, step-by-step explanations, length-matched topical associations without an argument, and length-matched neutral generated prefixes. Measure actual pre-answer length, preserve a predetermined scoring rule, and include a separate fixed-compute comparison if efficiency is the question. No new runs were launched for this review.

## Reproducibility

[analyze.py](analyze.py) produces [summary.json](summary.json), including exact input paths, settings, sample indices, normalization rules, Wilson intervals, and the melachot scoring sensitivity. Raw data are unchanged. Source citations support the reference answers and selected checks; this is not a complete scholarly audit of every statement in every trace.
