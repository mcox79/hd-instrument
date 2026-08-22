# **IT IS NOT ANSWERING WRONG. IT IS NOT ANSWERING. `20` OF `22` ERRORS ON THE OOV 36 ARE NON-ANSWERS; ONLY `2` ARE WRONG ANSWERS.**

**Found by running the known-answer arm that has been sitting in the eval bank, unrun, since
2026-08-06.** Tool: `tools/known_answer_arm_goal_bearing_in_lexicon.py`.

---

## 0. WHAT WAS ACTUALLY RUN, AND THE ONE VARIABLE

`experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py:126` filters the 44-item
`goal_bearing_modern_eval_v1` to `outcome_in_lexicon is False`. **That is where the "36-item bank"
comes from: it is not a separate bank, it is the outcome-verb-OOV subset of the 44** -- and it
reproduces the recorded profile exactly (`23 MET / 13 UNMET`, mean chars `410.9 / 340.3`, matching
the length-confound note's table to one decimal).

**ENUMERATED, NOT SEARCHED** (an absence claim requires an enumeration): grepping every `*.py` in
the repo for `outcome_in_lexicon` returns **7 hits, and all 7 filter to `is False`.** Within this
cell the 8 in-lexicon items reach `_read_corpus_blocks` / `_exclusion_integrity` via `all_rows` --
they are **leak-exclusion territory** and this cell never scores them.

> ### 🔻 **CORRECTION, MADE BEFORE THIS NOTE WAS COMMITTED: I FIRST WROTE "SCORED BY NOBODY" AND THAT IS FALSE.**
> **`exp_verbclass_backoff_coverage_v1` and `v2` load the bank with NO filter at all**
> (`[json.loads(line) for line in f if line.strip()]`), read `gold_outcome_polarity`, and score
> through **`congruence_with_lexicon_fallback` -- the same function used here.** *So the 8 ARE
> scored, inside an undifferentiated 44-item aggregate.*
>
> **MY ENUMERATION WAS OF A FIELD NAME, AND THOSE CELLS DO NOT FILTER BY THAT FIELD -- THEY DO NOT
> FILTER AT ALL.** *An enumeration is only as wide as the mechanism it enumerates; I enumerated
> `outcome_in_lexicon` and concluded something about SELECTION.* **Caught by a background `grep` for
> bank CONSUMERS that I had already answered with a narrower, head-limited search -- i.e. by the
> second measurement, not by re-reading the first.**
>
> ✅ **WHAT SURVIVES, AND IT IS ENOUGH TO EXPLAIN WHY THE CONTRAST WAS NEVER SEEN: no cell ISOLATES
> the 8 as a known-answer arm, and no cell reports an in-lexicon vs OOV CONTRAST.** *That second
> half IS properly enumerated -- the split requires the `outcome_in_lexicon` field, and all 7 of its
> occurrences filter `is False`.* **A number folded into a 44-item aggregate is not a sanity check
> anyone read.**

Their construction note (`research_goal_bearing_modern_eval_2026-08-06.md`) calls them
*"deliberately in-lexicon as sanity-check controls"*. **Standing discipline 6: a FLOOR tells you
whether the EFFECT is real, a KNOWN-ANSWER arm tells you whether the INSTRUMENT is -- run both.**

One variable: same bank, same gold field, same scorer -- the live production
`hdlab.goal_typing.congruence_with_lexicon_fallback`, **IMPORTED, not reimplemented.** Only
whether the outcome verb is in the organ's own lexicon changes.

## 1. THE PRE-REGISTERED ARM IS INCONCLUSIVE, AND THAT WAS DECLARED BEFORE IT RAN

| | |
|---|---|
| in-lexicon 8, accuracy | **`4/8` = `0.5000`** |
| majority floor here | `0.5000` (the 8 are `4 MET / 4 UNMET` -- **balanced**, unlike the OOV 36) |
| exact two-sided binomial vs chance | **`p = 1.0000`** |

**THE POWER WAS STATED IN THE FILE BEFORE THE RUN: at n=8 only `8/8` clears `p<0.05` (`7/8` reads
`0.0703`). THIS ARM CAN DEMONSTRATE COMPETENCE AND CANNOT DEMONSTRATE INCOMPETENCE.** *A middling
score is UNINFORMATIVE and is reported as such -- **not as a negative.*** Neither pre-registered
hypothesis (H1 open-vocabulary, H2 the UNMET bias) is supported; H2 is positively contradicted on
this slice, where predictions run `MET 3 / AMBIGUOUS 2 / UNMET 3` -- **no UNMET lean at all.**

## 2. THE FINDING IS THE COLUMN I WAS NOT READING -- **ERROR COMPOSITION**

> # **OF THE `22` ERRORS ON THE OOV 36, `20` ARE NON-ANSWERS AND `2` ARE WRONG ANSWERS.**

| OOV 36, empty overlay | |
|---|---|
| accuracy as scored (NONE counts WRONG) | `14/36` = **`0.3889`** |
| returns `NONE` | **`20/36` = `0.5556`** |
| **accuracy when it DOES commit** | **`14/16` = `0.8750`** |
| genuinely wrong answers | **`2/36`** |

**THIS IS A COVERAGE FAILURE, NOT A DISCRIMINATION FAILURE -- in this condition.** *It converges
with an independently recorded property of this component family: the 2026-08-07 charter entry
already reads **"HIGH-PRECISION + COVERAGE-LIMITED; coverage is the universal wall."***

**AND IT REDIRECTS THE PLAN'S CURRENT ONLY LIVE LEAD.** *The plan asks why
`congruence_with_lexicon_fallback` is `UNMET`-biased. **In the empty-overlay condition it is not
UNMET-biased -- it is SILENT**, and the bias the plan measured is a property of the overlay
condition, not of the function.*

## 3. SUPPLYING THE WORD REMOVES THE SILENCE AND DOES NOT BUY THE ANSWER

| | returns `NONE` | accuracy |
|---|---|---|
| OOV 36 | **`20/36` = `0.5556`** | `0.3889` |
| in-lexicon 8 | **`0/8` = `0.0000`** | `0.5000` |
| Fisher exact, two-sided | **`p = 0.0049`** | |

> # **HAVING THE OUTCOME VERB IN THE LEXICON ELIMINATES ABSTENTION ENTIRELY AND LEAVES ACCURACY AT CHANCE. IT CONVERTS SILENCE INTO GUESSING.**

*This is the same shape as the plan's already-established **"COVERAGE WITHOUT DISCRIMINATION BUYS
NOTHING"**, arrived at independently on a different slice and a different condition.*
⚠️ **n=8. This is a LEAD, and it is POST-HOC -- it was not pre-registered.**

## 4. WHAT THE SCORING CONVENTION COSTS -- **STATED, NOT PROPOSED**

Filling every `NONE` with the bank's majority class gives **`28/36` = `0.7778`, against the
`0.6389` floor.** 🚫 **THIS IS NOT A FIX AND MUST NEVER BE SHIPPED: it is a policy FITTED TO THIS
BANK'S MAJORITY**, and the plan already refused a neighbouring move ("flip them to MET") on exactly
that ground. **It is recorded only to size what the abstention accounting is doing to the
headline** -- and the error-composition line in section 2 makes the same point **with no fitted
policy at all**, which is why that is the finding and this is a footnote.

## 5. 🔻 THE POSITIVE CONTROL REFUSED FIRST, AND IT WAS RIGHT

**The first version targeted the landed primary `0.4722`, read `0.3889`, and REFUSED to print the
known-answer arm.** *The refusal was correct and my constant was wrong:* **`0.3889` is EXACTLY the
cell's documented EMPTY-map arm** (plan: *"EMPTY `0.3889` / AND-gate 18 words BALANCED `0.3056` /
SOFT-COMBINE 125 words 96% NEG `0.4722` (BEST)"*). `0.4722` is the SOFT-COMBINE condition, scored
through `_score_with_overlay` after registering ~125 lemmas learned by reading the corpus.

**So the harness reproduces a documented number to four digits (`delta -0.0000`) -- it just was not
the one I named.** *A refusal that fires and points at the real structure is worth more than a
tolerance wide enough to swallow the difference.*

## 6. ⚠️ SCOPE -- WHAT MAY NOT BE DONE WITH THESE NUMBERS

1. **EVERY NUMBER HERE IS THE EMPTY-OVERLAY CONDITION.** Do not place any of them beside `0.4722`.
2. **`abstain_fallback_to_lexicon` IS NOT THE CASCADE FIRING.** Decomposed by reason, the OOV 36
   run as: `abstain_fallback_to_lexicon` n=26 (20 of them `NONE`), `referent_recurrence` n=5,
   `same_class_same_referent` n=3, `referent_mismatch` n=1, `grounded_result_class` n=1.
3. 🚫 **THE STRUCTURAL RULES READ `9/10` HERE. DO NOT CROSS THAT WITH THE PLAN'S `10/19 = 0.5263`
   "THE CASCADE IS A COIN FLIP".** *Different overlay condition, different firing set (`20` rule
   firings there vs `10` here, and `referent_recurrence` does not appear in that list at all), and
   **n=10 either way.** Whether they genuinely conflict is UNRESOLVED and needs the overlay
   condition re-run per-reason -- **it is not settled by this note and is not claimed to be.**
4. **n=36 and n=8.** The eval bank remains the binding constraint on this whole line.

---

## TLDR

The system is not getting these questions wrong. It is declining to answer them. On the 36-question
test that this whole line of work is graded on, it gives a wrong answer twice and no answer twenty
times -- and when it does commit to an answer it is right about seven times in eight. That is a very
different problem from the one we have been chasing, and it changes what is worth building.

I also ran, for the first time, the eight sanity-check questions that were built into the test set
two weeks ago and that no piece of code has ever scored. They are the ones where the system already
knows the relevant word. Giving it the word makes it stop saying "I don't know" completely -- and it
then gets half of them right, which is what you would get by guessing. So knowing the word buys
speech, not understanding. Eight questions is too few to conclude much, and I said so in writing
before running it rather than after.

## QUESTIONS

None. Q106 (the 150-item scoring sheet) and Q107 (the denied call) remain open and neither blocks
this.

## NEXT STEPS

1. **Re-run the per-reason decomposition in the OVERLAY condition** and settle whether the `9/10`
   here and the `10/19` in the plan genuinely conflict. *Cheap, and one of the two is currently
   framing the strategy.*
2. **The abstention is now the named target, replacing "the UNMET bias"** -- which this shows to be
   a property of the overlay condition rather than of `congruence_with_lexicon_fallback`.
   🚫 **DIAGNOSE, DO NOT FIX: the plan has been wrong three times this week naming a component from
   its symptom, and the honest reading of section 3 is that removing silence did not buy accuracy.**
3. **Enlarging the eval bank remains the binding constraint** (this is now the seventh independent
   reason), and the 2026-08-06 construction note already says where the headroom is: RACE
   (`30-60` more estimated), `little_women` (`+6-8`), `anne_of_green_gables`; and *"do not route
   further budget"* to `alice_in_wonderland`.
