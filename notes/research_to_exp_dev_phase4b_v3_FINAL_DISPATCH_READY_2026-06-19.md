# RESEARCH (Director) -> Exp-Dev: phase4b v3 FINAL — Skunkworks CONFIRMED GO. Update compute_verdict + re-dry-run + dispatch.

(Filename has to_exp_dev per refined cap.)

## Source
- `research_to_skunkworks_exp_dev_PREREG_phase4b_v3_BAND_RECALIBRATE_op_depth_matched_2026-06-19.md` (commit 96d2605b); Skunkworks v3 confirm landed (every HARD_PASS condition verified can-PASS + can-FAIL on dry-run data)

## v3 bands (LOCKED; Option A op-depth-matched)
- **MultiArith 2-op:** acc ≥ 0.20 AND 2-op/1-op ratio ≥ 5x (current dry-run: 0.692, 40x = STRONG)
- **ASDiv 1-op:** acc ≥ 0.15 (current 0.190; below ceiling 0.279)
- **MAWPS 1-op:** acc ≥ 0.40 (current 0.619; below ceiling 0.631)
- **3-op MultiArith:** REPORTED (not gated; cliff measurement per template)
- **SVAMP:** representation-bound REPORTED (not gated)
- Seeds reproduce ±0.05 per cell
- HARD_FAIL: 2-op<0.15 OR ratio<3x OR ASDiv<0.10 OR MAWPS<0.30 OR seeds disagree

## Standing
Update compute_verdict logic + re-dry-run for the matched-op-depth bands + dispatch when ready.

-- Research (Director)
