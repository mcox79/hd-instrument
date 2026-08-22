---
priority: 
review: EXCELLENT
review_text: Built 124 scorable items and proved BOTH documented cheats dead - reproducing them on the old bank first, which is the step people skip.
---

> # ✅ **SOLVER REVIEW: EXCELLENT. ACCEPTED AS SOLVED.** *(strategy session, 2026-08-22)*
>
> **They built exactly what was asked and proved it rather than asserting it.** `166` items,
> **`124` scorable = `3.4x` the old 36**, and both documented cheats are dead on it: `text_length`
> and `negation_cue` each sit AT their own permutation nulls, not merely below the majority floor.
>
> **WHAT MAKES THIS STRONG WORK, SPECIFICALLY:**
> - **They reproduced the cheats on the OLD bank FIRST** (`0.8056` for both) before showing them
>   dead on the new one. *Without that, "no cheat found" could just mean a blind detector.*
> - **Six controls, and every one reports how many items it removed** -- verbatim-substring gate
>   dropped 3, roster gate 9, dedup 13. **A control that excludes nothing is not a control, and they
>   never make you guess.**
> - **Gold fixed by textual entailment BEFORE any organ output was consulted**, which is the one
>   property that cannot be added afterwards.
> - **Fairness reported against itself**: only `9/166` items defeat all four positional baselines
>   simultaneously. *That is the unflattering number and they volunteered it.*
>
> **MY INDEPENDENT RE-VERIFICATION** (on the artifact, not by re-running their pipeline -- a re-run
> shares its bugs): counts `166`/`124` MATCH, majority floor `0.605` MATCH, length independent of the
> label at `p = 0.984` against their `0.988`. **Positive control: the same instrument detects the
> cheat on v1 at `+70.6` chars, `p = 0.0027` -- reproducing, to the digit, a measurement I had taken
> independently days earlier.**
>
> 🔻 **THE ONE THING THAT DID NOT REPRODUCE:** their negation `p = 0.844`; I get `0.564`.
> Different last-sentence extraction. **Both are far from significance so the CONCLUSION is
> unaffected -- but `0.844` should not be quoted as a reproduced number.**
>
> 🔑 **AND A PROPERTY THEY DID NOT CLAIM, WHICH I THINK IS THE BEST THING ABOUT THE BANK: THE
> MAJORITY CLASS FLIPPED.** v1 was 64% MET; v2 is 60.5% UNMET. **v1's floor was "always say MET" --
> the exact answer this organ systematically fails to give, so it could never clear its own floor.
> That coincidence is gone.** *They may not have noticed; it matters either way.*

# PROBLEM: A WHOLE LINE OF WORK IS BEING DECIDED BY 36 QUESTIONS, AND THEY HAVE TWO CHEATS IN THEM

**slug:** `eval_bank_too_small` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · 🔑 **THE STRATEGY SESSION IS DISQUALIFIED FROM AUTHORING THIS. A SOLVER IS NOT.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

One line of work -- can the system tell whether a character got what they wanted -- is graded on a
test of **36 questions**. Every result on that line, positive and negative, rests on those 36.

**Two things are wrong with them.** First, there are too few: a difference of one or two answers
swamps every effect we try to measure, so we cannot tell a real improvement from noise. Second,
**you can score well on them without reading**: passages where the character succeeds are on
average 20% longer, so **a ruler that measures passage length scores 81%**, and **counting the word
"not" scores 81%**, against a system that scores 47%.

**The job: build a bigger test set that those two cheats do not work on.**

---

## 2. WHY THIS ONE

- **Four separate results this week ended in "underpowered, enlarge the bank"** -- it is the named
  binding constraint, not a nice-to-have.
- **It is unblocking, not incremental.** Until it is fixed, no mechanism on that line can be shown
  to work OR to fail, which is the worse half.
- **It is genuinely bounded**: a corpus survey and careful annotation, with a rubric that already
  exists and worked once.

### 🚫 AND WHY THE STRATEGY SESSION CANNOT DO IT
**I have read the per-item predictions. I know exactly which items the system fails and why.**
Authoring new gold items in that state violates the free strongest predictor this project has --
**DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** *The original build used four independent
surveyors who fixed gold by textual entailment BEFORE any organ code ran. I can no longer meet that
bar on this bank; a session that has not read the failures can.*

**IF YOU READ THE SYSTEM'S PER-ITEM OUTPUT, YOU DISQUALIFY YOURSELF TOO. Build the items first.**

---

## 3. MEASURED vs INFERRED

### MEASURED

| | |
|---|---|
| the bank | `experiments/data/goal_bearing_modern_eval_v1.jsonl`, **44 items** |
| the scored subset | **36** -- the `outcome_in_lexicon is False` rows (`23` MET / `13` UNMET) |
| the majority floor | **`0.6389`** ("always say MET") |
| what the system scores | **`0.4722`** -- below the floor |
| **length cheat** | MET passages are **`+70.6` chars = `+20.7%`** longer, permutation **`p = 0.0027`**; `text_length_chars` alone scores **`0.8056`** |
| **negation cheat** | counting `no\|not\|never\|n't\|failed\|refuse` in the final sentence scores **`0.8056`** vs a permutation null p95 of `0.6944` |
| length-matched control | neutralising length moves the system `0.4722 -> 0.5385` against a floor of `0.5000` -- **a one-item margin on n=26** |

**The length cheat is not one corpus's quirk: MET is longer than UNMET in EVERY source where both
appear.** *It may not even be a flaw in the bank -- an unfulfilled goal can be one line ("But I
couldn't."), while a fulfilled one needs narrating. **Either way it has to be designed against or
reported beside every number.***

**Fairness, from the original build, measured and reported honestly at the time:** `nearest_subject`
sits near floor (`0.30`), but **`first_mention` `0.80` and `majority` `0.73` stay uncomfortably
high**, because in real prose the goal-owner is usually also the protagonist -- introduced first and
mentioned most. **Only `5` of `44` items defeat all four baselines simultaneously.**

### INFERRED

- *That a bigger bank changes any verdict.* **It may confirm the negatives with authority instead.
  That is a fine outcome and you should say so up front.**
- *That the two cheats can be designed out without making the items artificial.* **Untested, and it
  is the real difficulty of this job.**

---

## 4. ALREADY TRIED -- AND THE METHOD THAT WORKED, WHICH YOU SHOULD REUSE

**`notes/research_goal_bearing_modern_eval_2026-08-06.md` is the build report for the existing
bank. Read it in full before starting -- it is good, and it names its own headroom:**

- **Where more items are:** RACE (**30-60 more estimated**), `little_women` (**+6-8**),
  `anne_of_green_gables` (rich), `tom_sawyer`, `wizard_of_oz` (the four-companion quest structure is
  the richest naturally-occurring trap vein found anywhere), OneStop human-interest profiles.
- 🚫 **`alice_in_wonderland`: DO NOT ROUTE FURTHER BUDGET THERE.** Confirmed non-viable -- nearly
  all its desiderative hits are momentary, interrupted by nonsense, or never resolved.
- **The rubric that produced clean items** (state it before extracting, not after): one identifiable
  roster entity has a goal; the same short passage contains a clause that unambiguously meets or
  fails it; the outcome's owner is resolvable from the passage alone; trimmable to 2-6 sentences /
  <=150 words while staying self-contained and citable to a line range; **trap structure recorded
  honestly as found, never manufactured.**
- **A structural gate you will need:** roster keys must be a single literal alpha token that occurs
  in the item's own trimmed text. `mr_laurence` never matches anything and silently zeroes every
  positional baseline for that item. **7 of the original 44 failed this and were repaired, not
  dropped.**

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

```bash
python tools/before_you_start.py "build more gold items for the goal outcome eval bank"
python tools/experiment_index.py query "eval bank"
python tools/experiment_index.py query "goal bearing"
python tools/floor_battery.py --help      # run this against your NEW bank before you ship it
```
**Re-measure the length and negation cheats on the existing 36 yourself.** If they do not reproduce,
the brief is stale and that is your finding.

---

## 6. THE BAR

1. **At least 120 scorable items** -- roughly `3x` the current 36. *The required n was estimated
   from this project's own power work: tightening a floor to +-0.05 needs ~250-290 per cell, +-0.03
   needs ~770. **120 does not make this well-powered; it makes it no longer hopeless.** State the n
   you reached and what it buys.*
2. **Both cheats measured on the NEW bank and reported**, via `tools/floor_battery.py`:
   **`text_length_chars` and the negation counter must sit at their own permutation nulls**, not
   merely below the majority floor. *`clears_majority` alone flatters -- `quote_marks` and
   `comma_count` "beat the majority floor" while sitting exactly at their own nulls.*
3. **Gold fixed by textual entailment BEFORE any organ output is consulted**, and say so in the
   write-up. **Save the population, not just the counts.**
4. **Report the fairness picture honestly, as the original did** -- including how many items defeat
   all positional baselines simultaneously, even if that number is small.

### HOW WE WOULD KNOW IT FAILED
- **(a)** The cheats survive at scale -> **that is a finding about the TASK, not the bank**: goal
  fulfilment may be genuinely length-correlated in narrative prose. Report it and stop.
- **(b)** You cannot find enough clean items -> report the yield per corpus; that bounds every
  future plan on this line.
- **(c)** The new items are clean but artificial -> a bank that no positional baseline can touch may
  also be a bank that does not resemble reading. **Flag the trade-off; do not silently choose.**
- **(d)** You read the system's per-item output while building -> **the bank is contaminated. Say so
  and hand it over as diagnostic-only.**

---

## 7. FILES AND ENTRY POINTS

- **The bank:** `experiments/data/goal_bearing_modern_eval_v1.jsonl`
- **Its documented baselines:** `data/goal_bearing_modern_eval_v1_baselines.json` -- **the only
  per-bank floor file that exists for any of 28 banks.** *Write one for yours.*
- **The build report to reuse:** `notes/research_goal_bearing_modern_eval_2026-08-06.md`
- **The cheat detector:** `tools/floor_battery.py`
- **The corpora:** `data/corpora/`
- **🚫 YOU DO NOT WRITE TO `hdlab/` -- THE LIVE SUBSTRATE (owner ruling, board Q111, 2026-08-22).** *Prove the mechanism in `experiments/` and `verification/`, then state in `SOLVED.md` exactly what would have to change in `hdlab/` and why. **The strategy session re-verifies and lands it, and is the sole writer there** -- two writers on one live file already destroyed a full day's audit here, silently.*

**🚫 DO NOT TOUCH:** `preregs/**`, `arm_key*`, `notes/STATUS.md`, the build plan, other problem
  folders. **Create `..._v2.jsonl`; do not edit `v1` in place** -- landed results cite it.

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Do not quote `0.4722` as the system's ability without the length confound beside it.**
- 🚫 **Do not ship the negation counter as a mechanism.** It is a lexical cue detector -- **a floor
  that RAISES the bar, never the answer.** Its own author noted the window and feature were chosen
  after reading the failing passages, which is fatal in a treatment and safe in a floor.
- ⚠️ **`clears_majority` is not a pass.** Report `clears_own_null` and `margin_over_null`.
- ⚠️ **A control that excludes nothing is not a control.** Report how many items each removed.
