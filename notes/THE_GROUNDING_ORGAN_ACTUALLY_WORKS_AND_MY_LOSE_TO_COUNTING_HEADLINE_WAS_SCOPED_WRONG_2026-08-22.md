# **THE GROUNDED SEMANTIC ORGAN SCORES `0.962`-`1.000` WHERE BAG-OF-WORDS SITS AT CHANCE ON THE SAME ITEMS. MY "WE LOSE TO COUNTING EVERYWHERE" HEADLINE WAS SCOPED WRONG -- AND THE REAL SAMPLE SIZES ARE 21, 12, 8 AND 2.**

**Both plans of record now read. This is the state of the program, and it corrects what I told the
owner four turns ago.**

---

## 1. ✅ WHAT IS ACTUALLY BUILT AND PASSING

| cell | verdict | the numbers |
|---|---|---|
| `exp_bridge1_governor_grounding_v1` | **HARD_PASS** | differential grounding **`0.967`**, unseen-concept **`0.956`**, **`bow_control 0.517`**, scrambled `0.500`, per-form table `0.500` |
| `exp_bridge1_confirmation_test_v1` | **RULING_CONFIRMED** | local governor `0.962` **but event-differing `0.500` and discourse-decisive `0.500`** -- *the predicted failure happened, validating the correction* |
| `exp_bridge1_twostage_event_situation_v2` | **HARD_PASS** | **B `1.000` vs governor `0.500`; C `1.000` vs governor `0.500`; `B_bow 0.517`, `C_bow 0.500`** |
| `exp_bridge1_event_assembly_open_vocab_v1` | **PARTIAL_WITH_BODYPART_GAP** | open-vocab B **`1.000`** vs scrambled `0.400`, bow `0.500`; **but body-part stratum `0.500`, lift `-0.033`** |

> ### **THE BAG-OF-WORDS CONTROL SITS AT `0.500`-`0.517` ON EVERY SUBSET, ON THE SAME ITEMS, WHILE THE ORGAN SCORES `0.962`-`1.000`.** *That control is prescribed by the plan and it is meant to fail. It does.*

## 2. 🎯 **THE DESIGN IS A DOUBLE DISSOCIATION, AND I NEARLY MISREPORTED IT AS A DEFECT**

*I first saw scramble controls reading `1.000` on the generalisation subsets and started to write it up
as a control failure. **It is the opposite -- each subset has a MATCHED scramble that must degrade and
an UNMATCHED one that must not:***

| subset | **matched** scramble | **unmatched** scramble | two-stage |
|---|---|---|---|
| **B** -- event-differing | scrambled-**EVENT** `0.583` ✅ degrades | scrambled-discourse `1.000` ✅ unaffected | **`1.000`** |
| **C** -- discourse-decisive | scrambled-**DISCOURSE** `0.650` ✅ degrades | scrambled-event `1.000` ✅ unaffected | **`1.000`** |

**Destroying the structure the subset depends on breaks it; destroying the other structure does not.**
*That is a stronger control than a single scramble, and reading only the numbers without asking which
control matched which subset would have produced a false accusation.*

## 3. 🔻 **AND THE SCALE, WHICH THE SUMMARY LINES DO NOT SHOW**

| subset | n |
|---|---|
| A (local governor) | **21** |
| B (event-differing) | **12** |
| C (discourse-decisive) | **12** |
| B generalisation | **8** |
| **C generalisation** | 🔻 **2** |
| open-vocab B | 12 |
| body-part gap | 6 |
| collision pairs | 6 |

***`Cgen_two_stage = 1.000` IS TWO ITEMS. At n=2 with a 0.5 baseline, perfect scores happen by chance
one time in four. THAT NUMBER CARRIES NOTHING and must not be quoted.*** *The n=12 subsets at `1.000`
against a `0.500` baseline are a different matter -- that is roughly 1 in 4,000 by chance, and it is
real.*

## 4. 🔻 **THE CORRECTION I OWE THE OWNER**

**Four turns ago I wrote: *"a 1970s term-weighting baseline still beats it everywhere we have
looked"* and listed sixteen measures.** *Every one of those sixteen is on the **word-similarity
channel** -- SimLex, SimVerb, norm-dimension decoding, seed propagation.*

> ### **THE PLANS OF RECORD SAY THAT CHANNEL IS NOT THE MEANING SIGNAL, AND MEASURED IT: bag-of-words scored `0.5167` = CHANCE with a supervised classifier HANDED THE GOLD SENSE.** *So "counting beats us" is true of a component the architecture had already ruled out -- **not of the grounding organ, where counting sits at chance and the organ does not.***

***THE SIXTEEN MEASURES STAND AS MEASUREMENTS. THE WORD "EVERYWHERE" WAS WRONG.***

## 5. ⚠️ WHAT THIS DOES **NOT** CHANGE

1. **The commercial assessment stands.** *These are 12-to-21-item constructed sets. `1.000` on 12 items
   is a mechanism proof, not a product.*
2. **Open vocabulary degrades it:** *closed-lexicon generalisation `1.000` -> real open-vocab `0.750`,
   and the **body-part stratum is at chance with a NEGATIVE lift (`-0.033`)**.*
3. **The real-prose wall is untouched.** *`PLAN_B`: on real prose the teaching signal does not carry
   (scramble fails to collapse, gap `-0.03`, primary `0.472` < floor `0.639`).* **These cells are
   constructed collision pairs, not prose.**
4. **I have still not re-run any of them.** *Numbers read off `metrics.json`; no recompute.*
5. ⚠️ *`PLAN_grounded_semantic_organ_build` warns that the appraisal-sim's synthetic `1.000` is a HAND
   MAP and **"NOT a text number"**. I have not established whether the charter's separate `1.000`
   (transfer_to_text arm_a) is that same number or a different one. **Until I have, I should not lean
   on either.***

## TLDR

I have now read both design documents properly, and **the picture I gave you four turns ago was wrong
in one important way.**

I said a simple word-counting method beats us everywhere we have looked. **That is true of one
component — matching words to human similarity ratings — and both plans had already ruled that
component out as the wrong place to look, with a test showing it performs at chance even when handed
the answer.**

**Where the real work is, the picture is much better.** The grounding organ decides that "hit hard"
means harm and "studied hard" does not, at 96–100% — while the counting method sits at chance on the
very same examples. And when an earlier version failed on harder cases, the fix was designed, built,
and now scores 100% on exactly those cases.

**The design quality is genuinely high.** Each hard case has two sabotage tests: wreck the structure it
depends on and it breaks; wreck a different structure and it does not. That is a much stronger check
than the single control I have been using, and I nearly misread it as a failure.

**But the sizes are small and I want to be blunt about it.** These are sets of twelve to twenty-one
examples. **One of the headline perfect scores is on two items, which is worth nothing** — at that size
you get a perfect score by luck one time in four. And on realistic open vocabulary it drops from 100%
to 75%, with one category still at chance.

**So: the commercial answer does not change.** Small hand-built demonstrations that work are not a
product, and the wall on real prose is untouched. **What changes is where the promise is** — and it is
not where I spent last night.

## QUESTIONS

None.

## NEXT STEPS

1. **Correct the owner assessment in place** *-- the word "everywhere" is wrong there.*
2. **The live frontier is OPEN VOCABULARY** *(`1.000` closed -> `0.750` real, body-part stratum at
   chance with negative lift), and after it, REAL PROSE.*
3. **Re-run at least one BRIDGE-1 cell** *before anything is built on these numbers (limit 4).*
4. *Method note: **asking which control matched which subset turned an apparent defect into the
   strongest design evidence in the file.** Reading the numbers alone would have produced a false
   accusation against good work.*
