# 🚫 **WITHDRAWN: "B1 IS A COVERAGE CLIFF, 0.931 → 0.304 → 0.002, WHERE COUNTING HOLDS 0.830"**
# **THE THREE NUMBERS ARE SYNONYM / RELATED / UNRELATED SIMILARITY. 0.002 IS THE *CORRECT* ANSWER, AND 0.830 IS THE *DEFECT*.**

**I stated this in three committed documents and twice in chat. It is wrong in the most complete way
a reading can be wrong: not imprecise, INVERTED. Withdrawing it before anything is built on it.**

---

## 1. WHAT I CLAIMED

> *"the part of the system that judges whether two concepts are related works very well on the
> roughly 230 concepts someone typed in by hand, and scores **essentially zero on everything else**
> — where plain word-counting still scores 0.83."*

**I read `tier_means = [0.9307, 0.3041, 0.0020]` as three VOCABULARY STRATA** -- common words, less
common, rare -- and therefore read `0.002` as *"our organ returns nothing outside its lexicon."*

## 2. WHAT THE THREE NUMBERS ACTUALLY ARE

**Recomputed from the cell's own saved triples** (`per_unit[0].shared_feature.per_triple`, n=29,
which reproduces the reported means EXACTLY):

| | tier 1 | tier 2 | tier 3 |
|---|---|---|---|
| **field name** | **`cos_syn`** | **`cos_rel`** | **`cos_unrel`** |
| **meaning** | anchor vs its **SYNONYM** | anchor vs a **TOPICALLY RELATED** word | anchor vs an **UNRELATED** word |
| example row | `vessel`/`ship` **0.7982** | `vessel`/`dock` **0.2787** | `vessel`/`anger` **-0.0024** |

**The cell's own `verdict_msg` says it in the same sentence I lifted the numbers from:**

> *"shared-feature FHRR bundles **separate genuine synonymy from mere topical relatedness**...
> tier1/2/3 shared_feature=(0.931,0.304,0.002) window=(0.859,0.852,0.830)"*

***I quoted the tail of a sentence whose head defined its terms.***

## 3. ⚡ **SO THE COMPARISON INVERTS**

**A LOW score on tier 3 is the GOAL.** Tier 3 is `vessel` vs `anger`. Scoring **0.002** there is
**correct**; scoring **0.830** is **an organ that thinks everything resembles everything.**

| arm | syn | rel | unrel | **separation (t1 − t3)** |
|---|---|---|---|---|
| **shared_feature (ours)** | 0.9307 | 0.3041 | **0.0020** | **0.9287** |
| window (distributional counting) | 0.8586 | 0.8515 | **0.8301** | **0.0285** |

**The distributional baseline is nearly FLAT -- its whole range is 0.0285, THIRTY-THREE TIMES
narrower than ours.** *That is exactly why its ordered fraction is **0.379** against our **0.966**,
and why the headline `HARD_PASS` was earned.* **The number I called "the bar to beat" is the
baseline's WORST property.**

## 4. AND THE "230-CONCEPT LEXICON BECOMING VISIBLE" READING IS NOT SUPPORTED EITHER

**`coverage` in the same file reads `29/29` for ALL FOUR ARMS.** *Every triple is INSIDE the
lexicon.* **Tier 3 is not "words we don't have" -- it is unrelated words we DO have.** *No tier of
this cell measures out-of-lexicon behaviour at all.*

## 5. ✅ WHAT SURVIVES, ON ITS OWN EVIDENCE

**The coverage limitation is REAL -- but the cell states it itself, and declines to claim otherwise:**

> `coverage_scope`: *"mechanism-proof on **86 hand-authored concepts** covering exactly the words in
> n11b's probe; **general open-vocabulary feature coverage (inducing features for arbitrary words) is
> a separate, missing-LEARNING follow-up, NOT claimed here**."*

**So the honest position is the OPPOSITE of a cliff: the mechanism WORKS WELL and is DEMONSTRATED
NARROWLY.** *That is a `missing-LEARNING` route (route 4 of the error-flavour rule) -- extend
feature induction to open vocabulary -- and it was already named, before I arrived, by the cell.*

**Also unaffected, because it comes from `ORGAN_MAP` and not from these numbers:** B1's `GAP` line
that the inventory is *"unweighted... no frequency statistic anywhere in this organ, so
distinctiveness cannot be computed even in principle."* **I have NOT independently verified that,
and it is NOT evidenced by the tier means.** *Do not quote it as measured.*

## 6. 🔻 **WHAT IS VOID, EXPLICITLY**

1. **"B1 is a coverage cliff"** -- VOID as an inference from the tier means.
2. **"Ours scores 0.002 where counting scores 0.830"** -- VOID, and **inverted in meaning**.
3. **"Any attempt must beat counting at 0.830"** -- **VOID, AND THE MOST DANGEROUS OF THE THREE: it
   sets a target that is the baseline's PATHOLOGY.** *The real comparator on this task is
   `ordered_frac`: ours **0.966**, window **0.379**, scramble **0.310**, hash **0.103**.*
4. *`n11b` HARD_FAIL, the 12-dim norms asset, and the `GROUNDED_CAP=0.45` flattening are all
   unaffected -- they were measured elsewhere and are not part of this retraction.*

## 6b. ➕ **TWO MORE ERRORS IN THE SAME SOURCE BULLET, FOUND WHEN I WENT TO FIX IT**

**I went to correct `ORGAN_MAP` L1797 and found the misreading was not alone.**

**(a) THE LEXICON SIZE MATCHES NEITHER CANDIDATE.** The bullet blames *"the ~230-concept hand
lexicon"*. **The cell scored on its OWN authored inventory -- `n_concepts = 86`, `n_feature_tags =
76`** -- **not** on the live organ's `CONCEPT_FEATURES`, which measures **359 words / 168 tags**
(*corroborated independently*: `STATUS_LESSONS.md` `hand_lexicon_baseline = 359`, and
`word_concept_bridge_scope_2026-08-13.md` *"len(CONCEPT_FEATURES) == 359 MEASURED"*). **"~230" is
neither number, and the organ blamed was not the organ measured.**

**(b) 🚨 THE "CHEAP FLOOR TEST" QUEUED UNDER IT COULD NEVER HAVE RUN.** It asked to stratify n11c
*"by whether both words are in `CONCEPT_FEATURES`"* with the can-fail condition *"if the OUT stratum
does not lose to WINDOW, the coverage story is wrong."* **MEASURED: the OUT stratum is EMPTY -- 0 of
86 distinct probe words fall outside, 29/29 triples have all four words inside.**

> **A STRATIFICATION WITH AN EMPTY STRATUM IS NOT A CAN-FAIL TEST -- IT IS UNTESTABLE (discipline
> 18). THE MISREADING HAD ALREADY GENERATED A DOWNSTREAM TASK THAT COULD NOT HAVE PRODUCED A
> RESULT**, and it was sitting in the map labelled *"still needed, and it is cheap."*

*Corrected in place at the source, so the next session does not inherit what I inherited.*
**Enumerated, not searched: the interpretive claim appears in exactly 5 files -- `ORGAN_MAP.md`
(source, now corrected), `OVERNIGHT_PLAN`, `BUILD_PLAN`, the B1 note and this one. Verified 0
uncorrected instances remain.**

## 7. 🎯 THE LESSON, AND IT IS NOT "READ MORE CAREFULLY"

**I did not invent this reading -- I inherited it.** `ORGAN_MAP` says *"It is a cliff. 0.931 -> 0.304
-> 0.002 is the ~230-concept hand lexicon becoming visible as a measurement."* **I quoted that as
authority and propagated it into three documents in one night without opening the metrics file.**

> **A DOCUMENT'S INTERPRETATION IS NOT EVIDENCE. The standing rule is "DISK-VERIFY agent claims
> before propagating" -- THIS EXTENDS TO OUR OWN NOTES, INCLUDING THE ORGAN MAP. A number and the
> sentence explaining what it measures must be read TOGETHER, from the SOURCE.**

*Cost if it had stood: a build aimed at raising a score whose LOW value was the success criterion,
gated on a bar that rewards the failure mode we avoid.*

**AND THE NEAR-MISS IS THE INSTRUCTIVE PART: what caught it was asking a question about the FIX
rather than the FINDING** -- *"does the norms table actually cover the tier-3 words?"* -- **which
forced me to open the item list. Nothing about re-reading my own note would have caught it.**
***ASKING WHETHER THE PROPOSED FIX COULD EVEN REACH THE PROBLEM IS ALSO A CHECK ON WHETHER THE
PROBLEM IS REAL.***

## TLDR

Yesterday I reported that one of our components scores almost zero on most words while crude
word-counting scores 0.83, called it a cliff, and wrote it into three planning documents. **It is
wrong, and not slightly -- backwards.**

Those three numbers are not three groups of words from common to rare. They are **three degrees of
relatedness**: how similar the system rates a word to its **synonym**, to a **loosely related**
word, and to a **completely unrelated** word. Ours reads **0.93 / 0.30 / 0.002**.

**So scoring nearly zero on the third one is exactly right.** `vessel` and `anger` **should** score
zero. Our component gets that right, and the word-counting method scores those same unrelated pairs
at **0.83** — it thinks essentially everything resembles everything. Its entire range from synonym
to unrelated is **0.03**, where ours is **0.93**.

**The number I told you we had to beat is the other method's single worst behaviour.**

I did not misread this from scratch — I took the interpretation from one of our own summary
documents and repeated it without opening the underlying results file. The explanation was sitting
in the same sentence I copied the numbers out of.

**There is still a real limitation here, but the experiment states it plainly itself:** it was only
ever run on 86 hand-written concepts and explicitly says extending to arbitrary words is separate
work it is not claiming. That is an honest, narrow demonstration of something that **works** — the
opposite of a cliff.

**What caught it was luck of a useful kind.** I went to check whether the fix I was proposing could
even reach the problem, and that forced me to open the actual data. Re-reading my own write-up
would never have caught it.

## QUESTIONS

None.

## NEXT STEPS

1. **Corrections applied to all three documents that carried the claim** -- the B1 note, the
   overnight plan, and the build plan -- rather than only recorded here.
2. **The comparator for anything built on this cell is `ordered_frac` (ours 0.966 / window 0.379),
   NOT the 0.830.**
3. **The open-vocabulary route is still live and is a `missing-LEARNING` route** -- but it now rests
   on the cell's own `coverage_scope` disclosure, not on a cliff that does not exist.
