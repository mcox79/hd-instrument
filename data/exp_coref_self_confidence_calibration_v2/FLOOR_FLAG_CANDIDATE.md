# CANDIDATE: this cell's own floor beats its own treatment

**cell:** `exp_coref_self_confidence_calibration_v2`
**recorded verdict:** `MIDDLE_BAND_PRONOUN`
**margin (floor minus treatment):** `+0.0693`

|  | key | value |
|---|---|---|
| strongest floor found | `results.combined_powered.baseline.pronoun_subset.auc_ncompatible_predicts_error` | `0.7244897959183674` |
| best treatment found | `results.g5g6_only.strict_cb.name_subset.auc_ncompatible_predicts_error` | `0.6551638530287984` |

## THIS IS A CANDIDATE, NOT A VERDICT

It means one thing only: **inside this cell's own `metrics.json`, the largest floor-shaped number is
larger than the largest treatment-shaped number, and the two are commensurable** -- same metric
block, same `per_seed`/`per_condition` index, not a `max_` against a `mean_`.

**It does NOT mean the result is withdrawn.** Nobody has yet read whether that floor is the RIGHT
floor for this cell's question. A floor can be the strongest number present and still be the wrong
comparison for the claim actually made.

## HOW TO DISCHARGE IT

1. Read the claim this cell's write-up actually makes.
2. Decide whether `results.combined_powered.baseline.pronoun_subset.auc_ncompatible_predicts_error` is the floor that claim must clear.
3. If it is -- the claim needs correcting, and it must be corrected wherever it is quoted.
   If it is not -- record WHICH floor is right and why, then delete this marker.

## PROVENANCE

Produced by `tools/adjudicate_floor_flags.py` on 2026-08-22, re-adjudicating the flags behind the
standing OP1 item (board Q112) about results whose claim might not survive the measurement bar.
**286 cells were flagged; 207 (72.4%) compare numbers that may not be compared; 43 are UPHELD;
35 -- including this one -- are candidates.**

Full reasoning: `notes/THE_238_OVERSTATED_RESULTS_WERE_NEVER_238_SEVENTY_TWO_PERCENT_ARE_INVALID_COMPARISONS_2026-08-22.md`
Reproduce: `python tools/adjudicate_floor_flags.py`
