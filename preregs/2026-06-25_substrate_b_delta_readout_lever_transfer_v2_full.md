# Pre-registration: substrate_b_delta_readout_lever_transfer_v2_full

**Date:** 2026-06-25
**Anchor:** substrate_b_delta_readout_lever_transfer_v2_full
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent)
**N_DIM:** 1024 (full), 256 (smoke)
**M_LIST:** [64, 128, 256, 512, 1024] (full); [16, 128] (smoke)
**NOISE:** 0.15 (scaled by 1/sqrt(N) per Skunkworks B-delta-HALT fix)

## Promotion context AND nuance correction

USER 2026-06-25 task: "Cell 5 (CPU): b_delta readout lever transfer full re-dispatch. Headline: nonlinear-readout lever
TASK-GENERAL; lifts capacity +53pp clustered @M256, +100pp uniform @M64."

**EXP_DEV CAUGHT (Fix #28 honest re-read of stale metrics.json):** the headline "clustered/uniform +53/+100pp" is from
the STALE 2026-06-18 metrics.json in `data/exp_b_delta_readout_lever_transfer_v1_smoke/metrics.json`. Since then, the
source `experiments/exp_substrate_b_delta_readout_lever_transfer_v1.py` has been REWRITTEN per Skunkworks B-delta-HALT
ruling:
- old v1 was NON_TEST (noise model bug: noise*randn(N) >> key norm -> linear floored at ALL M -> no cliff)
- corrected v1: noise/sqrt(N) (cos(noisy,key)~0.99 -> linear works low-M, cliffs high-M)
- old v1 framed tasks as "clustered (interference-limited) vs uniform (capacity-limited)"
- corrected v1 framed tasks as "bipolar values vs continuous values (BOTH uniform keys; both capacity-limited)" -> the
  generality axis is now VALUE-TYPE not KEY-DISTRIBUTION

The "+100pp uniform @M64" number in stale metrics had lin=0.0 at M=64 (the noise bug). That linear baseline = DEGENERATE
-> "lift" was DENOISING not capacity-lever. The corrected v1 mechanism is the load-bearing one.

v2 INHERITS the corrected v1 mechanism + runs 3 seeds with prospective bands tuned to the corrected regime.

## Strategic significance (under the corrected mechanism)

If chain-grade: nonlinear-readout (modern Hopfield softmax) lifts capacity past the linear (classic Hopfield raw-dot)
cliff on BOTH value-type tasks (bipolar + continuous). Task-general capacity lever in the value-type axis. Composes
with audit-device pipeline (a recall-time readout choice).

Honest scope: VALUE-TYPE generality only. KEY-DISTRIBUTION generality (clustered vs uniform) is a separate study (the
old framing; deferred per Skunkworks B-delta-HALT).

## Mechanism (corrected v1)

Per task in {bipolar, continuous}:
- Keys: M random unit-norm Gaussian vectors (UNIFORM iid; capacity-limited)
- Values: M x N bipolar (task=bipolar) or Gaussian continuous (task=continuous)
- Queries: keys + (noise/sqrt(N)) * randn (cos~0.99; not over-noisy)
- Score: S = Q @ keys.T
- LINEAR readout: cleanup(S @ V); cleanup=sign(bipolar) or identity(continuous)
- NONLINEAR readout: cleanup(softmax(beta*S) @ V)
- recall_acc = fraction of queries with cosine(recall, true value) >= 0.90

Per task, beta tuned PER SEED on nonlinear arm to discriminating spread sweet-spot, frozen across arms.

CAPACITY check per task (Skunkworks discrimination self-check):
- linear works low-M: recall_lin(M_low) > WORKS (0.5)
- linear cliffs high-M: recall_lin(M_high) < recall_lin(M_low) - CLIFF_DROP (0.2)
- If NOT both -> NON_TEST (degenerate; no capacity-curve to extend)

Extension per task:
- extension = recall_nl(M_high) - recall_lin(M_high)

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE
- extension mean >= 0.40 on BOTH tasks (across 3 seeds)
- cv across seeds <= 0.07 on each task
- all 3 seeds must satisfy capacity discrimination (linear cliffs) on BOTH tasks

### HARD_PASS_PARTIAL (= MIDDLE_BAND)
- extension >= 0.30 on at least one task

### HARD_FAIL
- extension < 0.20 on BOTH tasks

### NON_TEST (UNKNOWN tier)
- linear baseline does NOT cliff (lin_low <= WORKS OR lin_high >= lin_low - CLIFF_DROP) in any seed on at least one task

## Q-discipline

The stale v1 reported lifts of +0.53 / +1.00 with linear=0.0 at ALL M (degenerate). The corrected v1 mechanism should give:
- linear ~ 0.7-0.9 at M=64 (works); ~ 0.1-0.3 at M=1024 (cliffs)
- nonlinear ~ 0.5-0.7 at M=1024 (extends past cliff but not all the way)
- extension ~ 0.3-0.5 typically

If extension > 0.95 in any seed/task, suspect saturation (the corrected mechanism shouldn't give near-perfect extension;
that would suggest noise/keys aren't actually competing).

## Cross-cell discipline

- ASCII only
- Substrate-only (no LLM forward calls; pure torch only)
- Per-arm metrics in verdict_msg per Fix #28 (per-seed extension on each task, per-seed cliff booleans)
- Bands locked at module init via assert
- Seeds [11, 13, 19]
- META_M6: NAIVE baseline = LINEAR readout (classic Hopfield raw-dot) recall at the SAME (N, M, noise, values) = the
  capacity-cliff DERIVED in-cell, not copied.

## Smoke-vs-full discipline

Smoke (N=256, M=[16,128], 1 seed) vs full (N=1024, M=[64,128,256,512,1024], 3 seeds). The N change is REGIME-RELEVANT
(capacity cliff scales with N: ~0.14N -> 36 at N=256 vs 143 at N=1024). The user's "smoke-vs-full at regime matching"
discipline IS satisfied here because:
- mechanism identical (linear vs nonlinear readout; cosine score; cleanup)
- noise/sqrt(N) preserves cue_cos~0.99 at any N
- M_LIST is scaled to span the capacity cliff at each N (M ~ 0.06N to 1.0N)

The smoke is a smaller version of the same regime, not a different regime. No sign-flip expected.

## Timeout estimate

Smoke wall (N=256, 2 M values, 2 tasks, 1 seed): ~1s (per v1 timing).
formula: timeout_s = ceil(1.5 * 1 * (1024/256)^2 * (3/1) * (5/2)) = ceil(1.5 * 1 * 16 * 3 * 2.5) = 180s
Plus tune_beta overhead per seed per task: +10s
Plus checkpoint: **timeout_s = 600** (10min; conservative).

## PROT compliance

- PROT-018, 019, 020: do not apply.
- PROT-021: timeout < 14400s.

## Symmetric verify rail

Verdict reports:
- per-seed extension on each task
- per-seed cliff boolean on each task (the discrimination rail)
- per-seed tuned beta on each task (the regime rail)
- mean + cv across seeds for each task (the stability rail)
- both_cliff aggregate (the NON_TEST guard)

## Honest negatives possible

- One or both tasks may fail capacity discrimination at some seed (linear doesn't cliff cleanly) -> NON_TEST tier
- cv may exceed 0.07 if seed-tuned betas pick different operating points
- Extension may be small (~0.20-0.30) on continuous task if Gaussian value cleanup is harder than bipolar sign
