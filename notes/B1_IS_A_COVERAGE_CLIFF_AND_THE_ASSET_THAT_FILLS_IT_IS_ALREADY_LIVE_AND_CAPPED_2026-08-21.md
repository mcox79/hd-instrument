> # 🚫🚫 **THIS ENTIRE NOTE'S HEADLINE IS WITHDRAWN. DO NOT QUOTE THE TIER TABLE BELOW.**
> **`0.931 / 0.304 / 0.002` ARE NOT THREE VOCABULARY STRATA. They are `cos_syn` / `cos_rel` /
> `cos_unrel` -- similarity to a SYNONYM, to a TOPICALLY RELATED word, and to an UNRELATED word.**
> **A LOW TIER-3 IS THE GOAL: `vessel` vs `anger` SHOULD read ~0. Ours reads 0.002 (correct);
> distributional counting reads 0.830 (an organ that thinks everything resembles everything -- its
> whole range is 0.0285 against our 0.9287).** *So "we collapse where counting holds" is INVERTED,
> and **"the bar is 0.830" is VOID -- it targets the baseline's PATHOLOGY.** The real comparator is
> `ordered_frac`: ours **0.966**, window **0.379**.* **Coverage is `29/29` for ALL arms -- every
> triple is INSIDE the lexicon, so no tier here measures out-of-lexicon behaviour at all.**
> **What survives: the cell's OWN `coverage_scope` disclosure (86 hand-authored concepts;
> open-vocabulary explicitly NOT claimed) -- a narrow demonstration of something that WORKS.**
> ➡️ `notes/WITHDRAWN_the_B1_cliff_was_me_misreading_three_similarity_levels_as_three_vocabulary_strata_2026-08-21.md`

# ~~**B1 IS A COVERAGE CLIFF -- 0.931 → 0.304 → 0.002 -- AND THE ASSET THAT WOULD FILL IT IS ALREADY LIVE, ALREADY BETTER THAN A 121M-TOKEN ENCODER, AND DELIBERATELY CAPPED**~~ **(HEADLINE WITHDRAWN, above)**

**Two things found separately tonight. `ORGAN_MAP` itself says of the first: *"the cell measured it
and nobody set the two beside each other."* This sets them beside each other.**

---

## 1. THE CLIFF, IN THE ORGAN MAP'S OWN WORDS

`exp_n11c_shared_feature_lexical_similarity_v1` is a **`HARD_PASS`** on the headline:
**`ordered_frac` 0.966** vs `WINDOW` distributional **0.379**, `HASH_RANDOM` 0.103, `SCRAMBLE` 0.310
-- *and the scramble collapses the gain, so it is earned.*

**BUT THE TIER BREAKDOWN THE HEADLINE HIDES:**

| | tier 1 | tier 2 | **tier 3** |
|---|---|---|---|
| **shared_feature (ours)** | **0.931** | 0.304 | **0.002** |
| window (distributional) | 0.859 | 0.852 | **0.830** |

> **`ORGAN_MAP`: "HONEST TIER: not a HARD_PASS for the organ. **It is a cliff.** 0.931 -> 0.304 ->
> 0.002 is the ~230-concept hand lexicon **becoming visible as a measurement**."**

*And its companion arm is a warning about reading headlines: `exp_n11b_symmetric_pattern_...`
**`HARD_FAIL`**, sym 0.207 vs window 0.379, **and the scramble did NOT collapse (0.207 = 0.207) -- that
arm's signal was an artifact.***

## 2. WHY THE CLIFF EXISTS -- B1'S OWN `GAP` LINE

> *"the feature inventory is a hand-built lexicon of **~230 concepts**, not learned, and it is
> **unweighted**. Concretely: **there is no frequency statistic anywhere in this organ, so
> distinctiveness cannot be computed even in principle**."*

**And the brain-fidelity line is blunter still:** brain **SHAPE** is *"dense, graded, low effective
dimensionality (~4 group PCs, Huth 2012); **distinctive (few-concept) features privileged**"*, while
**OURS** is *"an **unweighted** hand-authored `CONCEPT_FEATURES` frozenset -- **the precise inverse of
the distinctiveness privilege**."*

**The map's `BLOCKS` line had already predicted the cliff** -- *"any judgement over the ~99.4% of
vocabulary outside the hand lexicon"* -- **and the cell then measured it.**

## 3. ⚡ **AND THE OTHER HALF, FOUND SEPARATELY TONIGHT**

`hdlab/grounded_similarity.py` exists **precisely because of this gap**. Its own docstring:

> *"the LIVE concept-similarity path (`lexical_similarity.concept_similarity`) **only judges the ~230
> hand-typed concepts** in `CONCEPT_FEATURES` -- every other word returns `None` ('cannot judge')."*

| | B1's hand lexicon | the norms asset |
|---|---|---|
| coverage | **~230 concepts** | **36,810 words -- 60.4% of TOKENS** |
| weighting | **unweighted frozenset** | **z-scored, 12 continuous dimensions** |
| frequency statistic | **none, even in principle** | Brysbaert concreteness + 11 Lancaster sensorimotor |
| measured quality | **tier-3 0.002** | **rho 0.2701, +0.1653 over the incumbent, CI [0.0159, 0.3084]** -- beating a **121M-token encoder** |

**➡️ THE ASSET IS ALREADY LIVE AND ALREADY LOADED -- AND `GROUNDED_CAP = 0.45` MAKES ITS OUTPUT
EFFECTIVELY TWO-VALUED, SO IT CAN NEVER INFLUENCE A DECISION.** *`sofa/couch` = `dog/cat` = 0.45.
**The cap is CORRECT for its job** -- it prevents a false same-idea merge -- **but the arm that won
used the RAW 12-dim vectors, which almost nothing consumes.***

## 4. WHAT THIS IS AND IS NOT

**IS:** *the clearest brain-foundational match found tonight -- a measured gap (`0.002` on 99.4% of
vocabulary, from an unweighted 230-concept inventory) and an owned, live, graded, 36,810-word asset
whose feature space is a **direct behavioural measurement** of what the brain-side citation says the
hub aggregates.*

**IS NOT:** *evidence that connecting them works.* **The spoke was already scored on this kind of
task and NEVER beat `TOP_COOCCURRENT`** (3 seeds, 40k sentences each). *And note the cliff's own
lesson: on tier 3 the **distributional** baseline holds **0.830** while our organ collapses -- so
counting is again the thing to beat, not random.*

## TLDR

Two things I found separately tonight turn out to be the same problem and its candidate solution, and
our own documentation says of the first: *"the cell measured it and nobody set the two beside each
other."*

**The problem:** the part of the system that judges whether two concepts are related works *very*
well on the roughly 230 concepts someone typed in by hand — and scores **essentially zero (0.002)**
on everything else, where plain word-counting still scores **0.830**. Our own notes call this a
**cliff** rather than a pass, and had *predicted* it before it was measured.

**The reason is stated plainly in the same document:** the concept list is hand-built, unlearned, and
**unweighted** — and there's no frequency information anywhere in that component, so it *cannot* tell
a distinctive feature from a common one **even in principle**. The brain does the opposite: it
privileges rare, distinctive features.

**The candidate solution is already in the system.** A set of **36,810 words** rated by humans on
eleven sensory and motor dimensions plus concreteness — graded numbers, not a yes/no list — covering
about 60% of running text. It beats a model trained on 121 million tokens at judging word similarity.
**It's loaded and running right now.** And its output is deliberately flattened to two values, so it
can't affect any decision.

**The flattening is correct for its current job** — stopping the system wrongly declaring two words
identical. It just means the good part is unavailable to everything else.

**What I'm not claiming: that connecting them works.** A closely related attempt was already tested
on three runs of forty thousand sentences and never beat simple word-counting. **And the cliff makes
the same point — the thing to beat isn't random, it's counting.**

## QUESTIONS

None.

## NEXT STEPS

1. **This is the best-evidenced brain-foundational gap/asset pairing in the archive** -- both halves
   measured, both already on disk, neither connected.
2. **Any attempt must beat `TOP_COOCCURRENT`**, not random -- the tier-3 baseline is **0.830**.
3. *`ORGAN_MAP`'s own remark applies to me too: the pieces were measured separately and nobody set
   them beside each other.*
