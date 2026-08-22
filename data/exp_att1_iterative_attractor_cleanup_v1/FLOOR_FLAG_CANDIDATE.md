# CANDIDATE: this cell's own floor beats its own treatment

**cell:** `exp_att1_iterative_attractor_cleanup_v1`
**recorded verdict:** `MIDDLE_BAND`
**margin (floor minus treatment):** `+0.0646`

|  | key | value |
|---|---|---|
| strongest floor found | `detail.by_arm_agg.ARGMAX_BASELINE.frac_converged_harder_mean` | `1.0` |
| best treatment found | `detail.by_arm_agg.ATT1_HIGH_TEMP.recall_harder_cv` | `0.9354` |

## THIS IS A CANDIDATE, NOT A VERDICT

It means one thing only: **inside this cell's own `metrics.json`, the largest floor-shaped number is
larger than the largest treatment-shaped number, and the two are commensurable** -- same metric
block, same `per_seed`/`per_condition` index, not a `max_` against a `mean_`.

**It does NOT mean the result is withdrawn.** Nobody has yet read whether that floor is the RIGHT
floor for this cell's question. A floor can be the strongest number present and still be the wrong
comparison for the claim actually made.

## HOW TO DISCHARGE IT

1. Read the claim this cell's write-up actually makes.
2. Decide whether `detail.by_arm_agg.ARGMAX_BASELINE.frac_converged_harder_mean` is the floor that claim must clear.
3. If it is -- the claim needs correcting, and it must be corrected wherever it is quoted.
   If it is not -- record WHICH floor is right and why, then delete this marker.

## PROVENANCE

Produced by `tools/adjudicate_floor_flags.py` on 2026-08-22, re-adjudicating the flags behind the
standing OP1 item (board Q112) about results whose claim might not survive the measurement bar.
**286 cells were flagged; 207 (72.4%) compare numbers that may not be compared; 43 are UPHELD;
35 -- including this one -- are candidates.**

Full reasoning: `notes/THE_238_OVERSTATED_RESULTS_WERE_NEVER_238_SEVENTY_TWO_PERCENT_ARE_INVALID_COMPARISONS_2026-08-22.md`
Reproduce: `python tools/adjudicate_floor_flags.py`
