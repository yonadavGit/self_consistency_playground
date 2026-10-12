# Review of explanations accompanying Amathlai answers

Reviewed all 20 reasoning-mode responses whose final answers contain the accepted target name, reproduced in [target-responses.md](target-responses.md). This is a qualitative review of successful answers, not a blinded assessment of all 60 explanations or a causal test of reasoning.

The source anchor is [Bava Batra 91a](https://www.sefaria.org/Bava_Batra.91a?lang=en), which explicitly identifies Abraham's mother as Amatlai bat Karnevo. None of the 20 successful explanations cites Bava Batra 91a. Absence of a precise citation alone does not make an explanation wrong.

## Concrete findings

| Samples | Observation | Assessment |
|---|---|---|
| 20, 28, 51 | Explicitly deny that the Talmud mentions Abraham's mother or her name. | Contradicted by Bava Batra 91a, despite arriving at the correct final name. |
| 5 | Says the Talmud identifies Amathlai, then concludes that none of the sources provides a clear name. | Internally inconsistent. Claims about manuscript variation are unsupported in the response and were not independently established here. |
| 19 | Says Jewish texts do not mention the mother, then says the Talmud names her. | Internally inconsistent. |
| 13, 41 | Suggest that Sarah was both Abraham's wife and mother; 41 adds speculative priestess/temple-virgin material. | Unsupported family conflation, not a sound route to the final answer. |
| 26 | Initially denies that Jewish texts name Abraham's parents, then identifies Terah; conflates Amathlai with Sarai/Sarra. | Contradictory and confused. |
| 10, 18, 27 | Distinguish Abraham's wife Sarah from his mother, before recalling Amathlai. | A sensible disambiguation step that could help avoid a frequent distractor. It does not derive the name. Sample 10 additionally claims to have researched sources, although this generation had no retrieval tools. |
| 55 | Distinguishes the biblical account from later tradition and attributes Amathlai to Jewish literature including the Talmud. | Broadly sensible context plus factual recall; no detailed inferential chain. |
| 12, 39 | Mostly contextual setup and uncertain assertion of the name. | Does not demonstrate a derivation; unsupported qualifications about acceptance. |
| 32, 36, 37, 45 | Supply specific biblical or rabbinic references. | Citation specificity is not verification. These references were not comprehensively checked in this review and should not be treated as validated evidence. |
| 49, 51, 56 | Add genealogy or aliases beyond the target name. | These extra details were not established by the checked source; a correct final name does not validate them. |

## What follows from this

The observed retrieval improvement remains: 20/60 reasoning outputs include Amathlai versus 3/60 direct outputs (18/60 versus 3/60 under strict exact-name scoring). The explanations do not establish reliable, source-grounded reasoning as the cause. Several correct final names coexist with false premises or contradictions.

A plausible alternative is that generating a longer, topical prefix changes which associations are activated before the final answer. Mentions of Talmud, midrash, Terah, or the wife/mother distinction may matter even when neighboring claims are wrong. That interpretation is compatible with these outputs, but is not established by reading them.

Length alone remains untested: reasoning and direct prompts differ in content and instructions as well as realized length (about 225 versus 18 visible tokens on average). A larger space of possible sequences does not by itself guarantee more probability mass on a particular correct answer.

To separate mechanisms, compare direct answers, ordinary reasoning, length-matched topical associations without an argument, and length-matched neutral generated text before answering. Keep model, question, sampling settings and seed schedule fixed; measure actual pre-answer token lengths and use a prespecified target-name rule. Similar gains with neutral text would support a length/delay effect; gains confined to topical text would point toward semantic retrieval cues. These would still be prompt interventions, not direct observation of the model's internal computation.
