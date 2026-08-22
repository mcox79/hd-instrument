# 🚨 **THE RE-LAND CHANGED THE DIAGNOSIS: RANDOM CREDIT ASSIGNMENT NOW BEATS THE REAL MECHANISM**

The goal-bearing cell's landed record was measured on 2026-08-06, in a configuration where the
structural cascade fired **zero** times. Re-landed at HEAD today. **The `HARD_FAIL` verdict stands,
but what it means has changed.**

---

## 1. THE THREE ARMS HAVE SEPARATED, AND OURS CAME LAST

| arm | landed 2026-08-06 | **re-landed at HEAD** |
|---|---|---|
| **RANDOM credit assignment** | `0.1667` | 🔻 **`0.5278`** |
| SCRAMBLED labels | `0.1667` | `0.3556` |
| 🔻 **THE REAL MECHANISM** | `0.1667` | 🔻 **`0.3056`** |
| *the floor it must clear* | `0.6389` | `0.6389` |

> ### **RANDOM CREDIT BEATS THE REAL MECHANISM BY `+0.2222`. SCRAMBLED LABELS BEAT IT BY `+0.0500`. OURS IS THE WORST OF THE THREE.**

**In the stale run all three arms read `0.1667` -- IDENTICAL.** With the cascade firing zero times
there was nothing to tell them apart, so the comparison could not have been informative. **The
separation is new, and it went the wrong way.**

🚫 **NOTHING HERE CLEARS THE FLOOR.** `0.5278` is a defeat for the mechanism, not a result for random
credit -- the majority floor is `0.6389` and every arm is under it.

## 2. THE VERDICT IS DECISIVE RATHER THAN BORDERLINE -- THREE INDEPENDENT GATES

Verified on disk in `metrics.json`, not taken from the report:

| gate | fires |
|---|---|
| `HF_primary<=floor` | `True` (`0.3056` vs `0.6389`) |
| **`HF_scramble_within_0.08`** | `True` — real `0.3056` vs scrambled `0.3556`, **the gap is negative** |
| `HF_noise>=2` | `True` — `2` of 8 noise-canary verbs falsely consolidated (`sit`, `speak` -> POS) |

*`learnable_subset_accuracy = 0.1667` on `n_learnable = 4` (below the `6` the gate wants).*
**No gate was touched or weakened.**

## 3. ✅ WHAT THE RE-LAND CONFIRMED, AND ONE PREDICTION THAT CAME TRUE

- **The stale record was genuinely stale:** empty-overlay `congruence_with_lexicon_fallback` reads
  `0.3889` (14/36) at HEAD against the landed `0.1667`. `26/36` still abstain; of the 10 items where
  a newer tier fires, **9 are correct**.
- **The flip was NOT one commit:** four `goal_typing.py` commits landed 2026-08-07
  (`509607e52`, `2747fac9a`, `9d76c4179`, `50c0e5ab4`), which is consistent with the archive's
  "the exact commit was never identified".
- 🎯 **`AMBIGUOUS` NOW BITES, EXACTLY AS PREDICTED.** It is absent under the empty overlay (`0/36`)
  but appears **3 times** under the LEARNED overlay (`befriend`, `find`, `come`) — **all scored
  WRONG by `_score`'s omission**, which never mentions the token. *The brief predicted this would
  stop being latent; it has. `ambiguous_pred_count = 3` now ships in `metrics.json`.*
- ✅ **Corpus arithmetic checked at FULL size before the expensive step:** `total_sents = 22,197`,
  `goal_fire = 1,659`, `n_windows = 1,655`, `exclusion_integrity_violations = 0`. No empty split.
- ✅ **`per_item_predictions` and `scored_population_n` now persist**, so every re-analysis of this
  cell is free from here on.
- **The stale run was preserved by RENAME, not copy-then-delete**, at
  `..._LANDED_2026-08-06_STALE/`.

## 4. ⚠️ ONE DISCLOSURE THAT MUST TRAVEL WITH THIS

**THE MANDATORY CERT GATE DID NOT COMPLETE.** `verification/run_certification.py` stalled — CPU flat
at `371.4s -> 371.5s` for 11+ minutes while resident — and was killed after ~20 minutes having
collected only 33 items with one `F`. **That is INCONCLUSIVE: not a pass, not a failure.**

*The only code change was additive fields in the experiment script (`per_item_predictions`,
`scored_population_n`, `ambiguous_pred_count`); `hdlab/` was not touched, so the gate's stated
rationale — protecting the production write-back path — does not strictly apply.* **But no fresh
baseline was obtained, and this note says so rather than letting a green-looking re-land imply one.**

---

## TLDR

We had a test result on file from two weeks ago that no longer described the code. It's been re-run.

The system still fails, and it fails harder than the old record suggested — but the informative part
is the comparison. We run two deliberately stupid versions alongside the real one: one that assigns
credit **at random**, and one fed **scrambled labels**. Both now score better than the real
mechanism. Random guessing beats it by a wide margin.

In the old record all three scored identically, so the comparison told us nothing. They have now
pulled apart, and ours came last.

None of them passes. Random credit isn't good either — it's just less bad than the thing we built,
which is the useful and unwelcome fact.

One caveat I'm keeping visible: the mandatory pre-flight check hung and was killed, so it neither
passed nor failed. Nothing here should be read as having cleared it.

## QUESTIONS

None.

## NEXT STEPS

1. **`_score` counts `AMBIGUOUS` as a wrong answer by omission, and it is now live (3 items).** That
   is an `experiments/` edit and belongs to a cell author, not here.
2. **The cert gate stall needs explaining before anything leans on this re-land.** A gate that hangs
   is not a gate.
3. 🚫 **Do not quote `0.5278` as evidence for random credit.** Every arm is below the `0.6389` floor;
   it is a statement about our mechanism, not about randomness.
