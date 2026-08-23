---
priority: 8
review:
review_text:
---

# PROBLEM: ON THE NEW TEST SET THE ORGAN DOES NOT ANSWER TWO-THIRDS OF THE TIME

**slug:** `organ_abstains_on_two_thirds_of_v2` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **evidence is first-hand and verified on disk, not relayed**

> **PRIORITY NOTE, and the call is not mine:** filed at `9` because I did not want to re-rank a list
> another session maintains. **It may deserve far higher.** It is the CURRENT blocker on the
> goal-bearing line, the evidence is a few hours old, and the failure is a *refusal to answer* rather
> than a wrong answer — which is usually the more tractable kind. *Re-rank it if you agree.*

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine. "The number probably didn't change" is not yours to decide silently.*

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

We ask the system, about a passage: **did the thing the character wanted actually happen?** Three
answers are possible — yes, no, or *I don't know*.

On the new 124-question test set it says **"I don't know" 82 times out of 124.**

It is not getting them wrong. It is not answering. **Those need completely different repairs, and we
have been treating this line as an accuracy problem.**

## 2. WHY THIS ONE

- **It is the live blocker on the goal-bearing line.** The organ scores `0.2339` where always
  guessing the commonest answer scores `0.6048`. **Two-thirds of that gap is silence, not error.**
- **A refusal is more diagnosable than a mistake.** Something upstream declines to produce a
  candidate; that something can be found and named. A wrong answer could come from anywhere.
- 🔑 **AND THE OBVIOUS EXPLANATION IS ALREADY RULED OUT.** The new bank flipped the majority class
  (v1 was 64% MET, v2 is 60.5% UNMET), so a bias-alignment artifact was the thing to suspect. **It is
  not that: MET recall `10/49` and UNMET recall `19/75` are BOTH low.** *That check is done; do not
  redo it.*

## 3. MEASURED vs INFERRED

**MEASURED** — `data/exp_goal_bearing_organ_v2_bank_score_v1/metrics.json`, verified on disk by the
strategy session rather than taken from a report:

| | |
|---|---|
| organ accuracy on v2's 124 scorable | **`0.2339`** |
| v2's own majority floor (class `unmet`) | **`0.6048`** |
| MET recall | `10/49` (`0.2041`) |
| UNMET recall | `19/75` (`0.2533`) |
| **non-committal predictions** | 🔻 **`82/124` = `66%`** (`NONE` 80, `AMBIGUOUS` 2) |
| baselines clearing their OWN null, on v2 | **NONE of 12** (`strongest_that_clears_its_own_null: None`) |

*Floors were recomputed on v2's own population, never imported from v1. Positional baselines on the
124: `recency 0.6371 / first_mention 0.7419 / nearest_subject 0.3065 / majority 0.6935`.*

**INFERRED, NOT MEASURED:**

- 🔻 **That the cause is pattern coverage on the new prose** (`find_desired_state` failing to match
  Sherlock Holmes-era constructions it never saw). **Plausible and untested — this is the hypothesis
  to attack, not a finding.**
- 🔻 **That fixing the abstention would raise accuracy.** It might convert 82 silences into 82 wrong
  answers. **Nothing here says the organ knows the answer and is withholding it.**

## 4. ALREADY TRIED

- **The majority-alignment confound: checked and ruled out** (see §2). Both class recalls are low.
- **A `CONTAMINATION_RISK` arm exists and is not usable as evidence:** re-registering v1's learned
  18-lemma overlay lifts accuracy to `0.2984` and cuts abstention to `60/124` — **but it was trained
  on the same four novels v2 draws its new items from, at line ranges never excluded.** *The agent
  that produced it flagged this unprompted. Do not quote `0.2984`.*
- **On v1's 36-item bank the same function abstained `20/36`** under the empty overlay. ⚠️ **DO NOT
  set that beside the `66%`** — different population, different bank, and the two have not been
  reconciled. *A third measurement described v1 abstention as "~8%", which contradicts both; that
  number is unexplained and should not be used either.*

## 5. VERIFY BEFORE YOU START

1. **Re-run the measurement cell** — `experiments/exp_goal_bearing_organ_v2_bank_score_v1.py` — and
   confirm `0.2339` / `82` still hold. *Notes here go stale within hours.*
2. **Read `per_item_predictions`** in that cell's `metrics.json`. It persists which items abstained;
   **the 82 are enumerable, so enumerate them rather than sampling.**
3. **Look at the 42 it DID commit on before the 82 it did not.** *What is present in those passages
   and absent from the rest is the whole question.*
4. `python tools/before_you_start.py "why does the goal organ abstain"` and read every row.

## 6. THE BAR

**NAME THE MECHANISM THAT PRODUCES THE SILENCE, WITH THE LINE THAT DOES IT.** This is a diagnosis
problem first; a fix is only meaningful once the cause is identified.

- **A CANDIDATE CAUSE MUST BE SHOWN FIRING**, at runtime, on specific items from the 82. *Static
  reading is not enough — this repo's own rule is that grep gets reachability wrong in both
  directions, and it has done so on this exact module.*
- **PARTITION THE 82.** If they have more than one cause, say how many fall to each. *"It is
  pattern coverage" is not an answer unless it accounts for a stated number of them.*
- 🚨 **IF YOU THEN FIX IT, THE DECIDING CONTROL IS WHETHER THE CONVERTED ITEMS ARE RIGHT.** Turning
  silence into noise is not progress: report accuracy **on the converted subset alone**, against the
  same-class base rate. **A fix that converts 82 abstentions into 82 wrong answers must be reported
  as a failure, and it will look like a large accuracy change either way.**
- **Recompute any floor on the population you actually score.** Nothing on v2 clears its own null,
  so a "beats the majority" claim is not a cleared floor.

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the measurement + `per_item_predictions` | `data/exp_goal_bearing_organ_v2_bank_score_v1/metrics.json` |
| the cell that produced it | `experiments/exp_goal_bearing_organ_v2_bank_score_v1.py` |
| the organ under test | `hdlab/goal_typing.py` — `congruence_with_lexicon_fallback` |
| the likely upstream suspect | `find_desired_state` / the structural cascade tiers |
| the bank | `experiments/data/goal_bearing_modern_eval_v2.jsonl` (166 items, 124 scorable) |
| the v1 re-land, for context only | `notes/RANDOM_CREDIT_BEATS_THE_REAL_MECHANISM_ON_THE_RE_LANDED_CELL_2026-08-22.md` |

## 8. DO NOT QUOTE

- 🚫 **`0.2984`** — the contaminated overlay arm.
- 🚫 **`66%` against "v1's ~8%"** — unreconciled, and a third measurement says `20/36`.
- 🚫 **`0.2339` as evidence the organ is worse than it was.** It is the FIRST measurement on this
  bank; v1 and v2 are different populations with different majority classes and **no number crosses
  between them.**
- 🚫 **"beats the majority floor"** as a cleared floor. On v2 nothing clears its own null.
