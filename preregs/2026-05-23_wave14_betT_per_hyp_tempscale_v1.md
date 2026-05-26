# Prereg: wave14_betT_per_hyp_tempscale_v1

**Date**: 2026-05-23
**Experiment name**: wave14_betT_per_hyp_tempscale_v1
**Script**: experiments/exp_wave14_betT_per_hyp_tempscale_v1.py
**Queue**: local_cpu_queue
**Trigger**: URGENT pipeline refill after ONLINE_W_NOISE_ENVELOPE_NARROW verdict; Research rescue sketch #2 (P_deflated=0.45) from notes/research_betT_rescue_sketches_2026-05-23.md

---

## Hypothesis

Bet T cycle-101 BET_T_PARTIAL min_acc=0.689 is a calibration artifact from shared beta=32,
which is 4x too large at N=4096 (optimal beta = c/N = 32768/4096 = 8, measured cycle 100 v100).
Per-hypothesis TEMPSCALE beta_h at or near the optimal value will lift min_acc above 0.85.

This is the Sagawa-Ueda analog for Bet T: the metric/parameter choice masked a real signal.

## Protocol

- N=4096, 8 hypotheses, 30 facts/hypothesis, 200 entities, 20 relations, 3 seeds {17, 23, 31}
- Sweep beta_h in {4, 8, 16} (bracketing the optimal c/N = 8)
- Per hypothesis: compute accuracy (correct/total) and ECE (|mean_confidence - accuracy|)
  using softmax(beta_h * cosine_scores) as the confidence estimate
- Report min_acc, mean_acc, ECE_max across hypotheses for each beta_h
- Select best beta_h by min_acc (tie-break: ECE_max)

## Predictions (pre-registered)

**HARD PASS**: at best beta_h, min_acc >= 0.85 AND mean_acc >= 0.90 AND ECE_max_h <= 0.10
Verdict: BET_T_TEMPSCALE_PASS

**HARD FAIL**: at ALL beta_h, min_acc < 0.70 (no improvement over cycle 101's 0.689)
Verdict: BET_T_TEMPSCALE_KILL

**Partial**: min_acc in [0.70, 0.85) -- improvement shown but HARD PASS not met
Verdict: BET_T_TEMPSCALE_PARTIAL

## Memory budget

- entity_atoms: 200 x 4096 x float32 = 3.2 MB
- relation_atoms: 20 x 4096 x float32 = 0.32 MB
- hyp_atoms: 8 x 4096 x float32 = 0.13 MB
- M_joint (BSC): 4096 x float32 = 16 KB
- Total peak: < 4 MB. Trivially within any CPU limit.

## Substrate-product axis

Cap class 3 (provenance / self-knowledge): Bet T parallel hypothesis tracking
If PASS: substrate maintains 8 parallel hypotheses with calibrated per-hypothesis confidence.
Connection to Cap 1 Crooks: each hypothesis's provenance is erasable independently.
Connection to Cap 3 streaming: per-hypothesis streaming posterior is the natural extension.

## Runtime estimate

At N=4096, 3 seeds x 3 beta_h x 8 hyp x 30 facts = 2160 forward passes.
Estimated < 5 min CPU. Timeout: 600 s.

## Baseline

cycle-101 BET_T_PARTIAL: min_acc=0.689, mean_acc ~ 0.83 (estimated from partial),
shared beta=32 (4x above optimal at N=4096). This experiment applies the calibration fix.

## References

- Research rescue sketch #2: notes/research_betT_rescue_sketches_2026-05-23.md
- cycle-100 v100: beta=c/N=32768 measured empirically (c=32768)
- cycle-101 v101: BET_T_PARTIAL min_acc=0.689
- Guo et al. ICML 2017: temperature scaling for calibration
- Kuleshov & Liang NIPS 2015: per-class temperature scaling
