# **THE FRONTIER I WAS ABOUT TO WORK -- CREDIT-ASSIGNMENT -- WAS TRIED ON 2026-08-07 AND `HARD_FAIL`ED. BUT IT WAS TRIED IN THE *LOCAL-WINDOW* FORM, AND THE CHARTER PRESCRIBES REPLACING THE LOCAL WINDOW ENTIRELY. THOSE ARE DIFFERENT EXPERIMENTS.**

**So the lever is not closed -- one form of it is. Getting that distinction right is the whole value of
this turn.**

---

## 1. THE WALL, AS THE CELLS THEMSELVES STATE IT

*`exp_noise_robust_learn_from_exposure_snorkel_v1` (commit `fc21752f3`), Director-VET'd:*

| | |
|---|---|
| real primary accuracy | **`0.4722`** |
| scrambled | **`0.5000`** -- ***the scramble does NOT collapse, so there is NO real signal*** |
| majority floor | `0.6389` -- **primary is BELOW it** |
| **coverage** | ✅ **NOT the problem** -- *the AND-gate teacher fires on **439 / 1655** real windows* |

**DIAGNOSED CAUSE: CREDIT-ASSIGNMENT PRECISION.** *`_credit_targets` attributes a window's whole-window
consequence to **every** OOV outcome-verb whose local-clause referent links to the goal referent
anywhere across the goal-plus-three-sentences window -- so on real prose it credits co-occurring LIGHT
verbs and, empirically, some morphological-heuristic non-verb noun-stems.*

## 2. 🔻 **THE FIX WAS BUILT THE SAME DAY AND HARD_FAILED**

*`exp_sharpened_credit_assignment_v1`, 2026-08-07 -- clause-anchored + selectional-weighted:*

```
primary 0.4167 vs floor 0.6389  (delta -0.2222)
scrambled 0.400, lift 0.0167    (HARD_PASS needs >=0.1; NO-SIGNAL is <=0.05)
attribution_precision  0.4676 -> 0.4941
n_registered           23 -> 6
reason: SCRAMBLE_STILL_DOES_NOT_COLLAPSE_signal_still_does_not_carry
```

> ### **SHARPENING MOVED ATTRIBUTION PRECISION BY `+0.027` -- FROM CHANCE TO CHANCE -- WHILE CUTTING COVERAGE FOUR-FOLD, AND THE SIGNAL STILL DID NOT CARRY.** *`lift 0.0167` sits inside the cell's own NO-SIGNAL band.*

**That is a properly closed negative: real floor, scramble control, a discriminator-fires gate, and an
arms-differ digest check.** *It is not a weak experiment.*

## 3. 🔑 **BUT IT IS NOT THE EXPERIMENT THE CHARTER ASKS FOR**

| | |
|---|---|
| **what was TRIED** | *sharpen the rule **inside** the local window -- clause-anchor it, weight it by selectional fit* |
| **what `SUBSTRATE_CHARTER` PRESCRIBES** | *"feed the maintained **SituationModel + coref** as the extraction context into the proven grounded reasoning organ, **REPLACING THE LOCAL WINDOW**"* |
| **what `PLAN_B` PRESCRIBES** | *"target CREDIT-ASSIGNMENT (**goal-linked** consequence, **NOT window co-occurrence**)"* |

***BOTH DOCUMENTS SAY REPLACE THE WINDOW. THE CELL SHARPENED IT.*** **A sharper rule over the same
window is still window co-occurrence, which is the thing both documents name as the defect.**

⚠️ **AND THE RESULT IS CONSISTENT WITH THAT READING:** *precision went `0.4676 -> 0.4941` -- if the
window is the wrong unit, no amount of sharpening within it reaches a usable precision, and a `+0.027`
gain bought with a `4x` coverage loss is what that looks like.* **I am stating this as the natural
reading, NOT as demonstrated.**

## 4. ⚠️ **WHAT I HAVE *NOT* ESTABLISHED, AND WILL NOT CLAIM**

***I did NOT establish that the situation-model form is unattempted.***

| query | result |
|---|---|
| `"situation model extraction"`, `"maintained situation"`, `"coref extraction context"` | **0 each** |
| ✅ positive control `"pattern separation"` | **12** -- *the tool works* |
| 🔻 but `"situation"` alone | **55 cells** |
| 🔻 and `"coref"` alone | **106 cells** |

**161 cells I have not enumerated.** *The phrase-zeros are genuine as phrases and mean nothing about
whether the work exists under another name.* ***An absence claim here requires enumerating those 161,
which I have not done -- and this project's own rule is that a search is not an enumeration.***

## 5. ⚠️ LIMITS

1. **Numbers READ from `metrics.json`, not reproduced.**
2. **The two cells' primaries differ** (`0.4722` in the parent, `0.4167` in the sharpened run) --
   *different arms/populations; I did not reconcile them and they must not be blended.*
3. **Section 3's reading is an interpretation of a design difference, not a measurement.**
4. **161 unenumerated cells (section 4).**

## TLDR

The next thing to build, according to both design documents, is getting the system to attach a story's
consequence to the *right* verb. **I checked, and it was built on the 7th of August and failed.**

The failure is well documented: the teaching signal does not survive on real prose, the check that
should have collapsed did not, and coverage was explicitly ruled out as the cause — **the teacher fires
on 439 of 1655 passages, so there is plenty of data; it is just attaching the lesson to the wrong
word about half the time.** Sharpening the rule moved that from 47% to 49% — chance to chance — while
throwing away three quarters of the examples.

**But here is the distinction that matters, and it took reading both documents to see it.** The
experiment sharpened the rule *within* a fixed window of nearby sentences. **Both design documents say
the window itself is the problem and should be replaced** with the system's running model of the
situation and who is being referred to. **A sharper rule over the same window is still the thing they
called the defect.**

**What I will not claim is that nobody has tried the replacement.** My searches for it came back empty,
but there are 161 experiments mentioning situations or reference-tracking that I have not read, and
this project's own rule is that failing to find something is not evidence it is absent.

## QUESTIONS

None.

## NEXT STEPS

1. **ENUMERATE the 161 `situation` / `coref` cells before proposing the replacement build.** *That is
   the honest precondition, and every time I have skipped it tonight the work already existed.*
2. **If it is genuinely unattempted, it is the best-motivated build available** -- *named by two
   independent documents, with the local-window alternative now closed by a clean HARD_FAIL.*
3. *Method note: **"the lever failed" and "one form of the lever failed" are different conclusions**,
   and only reading the cell against the documents that prescribed it distinguishes them.*
