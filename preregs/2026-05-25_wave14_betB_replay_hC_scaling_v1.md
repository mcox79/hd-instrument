# Pre-registration: wave14_betB_replay_hC_scaling_v1

**Filed:** 2026-05-25 by exp_dev  
**Trigger:** REPLAY axis locked 🟢 v206; H-C mechanism needs dedicated probe  
**Script:** experiments/exp_wave14_betB_replay_hC_scaling_v1.py  

---

## Hypothesis under test

H-C (effective-N-doubling): replay effectively doubles the number of training examples,
so retention curves at (1x data + replay_frac=0.5) should MATCH retention curves at
(2x data + replay_frac=0.0). If true, this means replay has the same effect as
collecting more fresh training data -- it is purely a data-augmentation mechanism.

H-A/H-B alternative: replay provides MORE than N-doubling (consolidation or
interference-reduction effects that pure data augmentation cannot replicate).

Null: data quantity (2x) strictly outperforms replay (N matters more than replay rate).

---

## Design

Three conditions per seed:
1. REPLAY: Phase A/B/C with 1x bytes (BYTES_PER_CORPUS=150000) + replay_frac=0.5
2. 2X_NOREPLAY: Phase A/B/C with 2x bytes (300000) + replay_frac=0.0
3. 1X_NOREPLAY: Phase A/B/C with 1x bytes (150000) + replay_frac=0.0 (baseline)

All conditions evaluated on the SAME held-out test set (from the 1x corpus).
This ensures comparison is fair: retention reflects what the substrate remembered
from Phase A given different training regimes for Phase B/C.

Key metrics:
- diff = retention_A_replay - retention_A_2x
- replay_lift = retention_A_replay - retention_A_1x_noreplay

---

## Pre-registered thresholds

**HC_HARD_PASS (H-C CONFIRMED: replay = effective N-doubling):**
- |diff| < 0.04 AND replay_lift >= 0.10
(replay matches 2x data closely; within 4pp tolerance)

**HC_REPLAY_EXCEEDS_2X (H-C REFUTED: replay > N-doubling):**
- diff > 0.08 AND replay_lift >= 0.10
(replay provides MORE than 2x data; H-A or H-B dominates; replay is NOT just data aug)

**HC_2X_EXCEEDS_REPLAY (H-C REFUTED: N > replay):**
- -diff > 0.08 AND replay_lift >= 0.10
(2x data strictly better than replay; true fresh data beats replay; N-scaling matters more)

**HC_INCONCLUSIVE:**
- replay_lift < 0.10 (replay mechanism not active at scale)

**HC_MIDDLE_BAND:**
- diff in (-0.08, 0.08) but abs(diff) >= 0.04 (ambiguous; re-run at higher N)

---

## Effect size note

M_sweep smoke (exp_wave14_betB_M_sweep_v1) found N-scaling gives only +2.7pp retention
lift (N=1024 -> N=4096, same corpus). This suggests H-C is unlikely to hold because
2x data should behave similarly to 2x N, which barely moves retention. Prediction:
HC_REPLAY_EXCEEDS_2X is most likely outcome.

Smoke scale (N=1024, 1 epoch) expected wall time ~15-25 min CPU.
Full run: N=4096, 5 seeds, 5 epochs; expected ~4-6 hours GPU.

---

## Pre-commit cap_map outcome mapping

- HC_HARD_PASS: annotate REPLAY row "H-C effective-N-doubling CONFIRMED; replay
  equivalent to 2x fresh data; mechanism is data augmentation, not consolidation"
- HC_REPLAY_EXCEEDS_2X: annotate REPLAY row "H-C REFUTED: replay exceeds 2x data;
  mechanism provides qualitative benefit beyond data augmentation (H-A or H-B dominant)"
- HC_2X_EXCEEDS_REPLAY: annotate REPLAY row "H-C REFUTED: true data scaling
  outperforms replay; replay is a weak substitute for fresh data; N-scaling is key lever"

---

## Self-test cells (formula verification)

compute_verdict self-test cases (verified in _instrumentation_selftest):
- retention_replay=0.83, retention_2x=0.81, 1x_noreplay=0.68 -> HC_HARD_PASS
- retention_replay=0.86, retention_2x=0.77, 1x_noreplay=0.68 -> HC_REPLAY_EXCEEDS_2X
- retention_replay=0.75, retention_2x=0.85, 1x_noreplay=0.68 -> HC_2X_EXCEEDS_REPLAY
- retention_replay=0.70, retention_2x=0.85, 1x_noreplay=0.68 -> HC_INCONCLUSIVE
