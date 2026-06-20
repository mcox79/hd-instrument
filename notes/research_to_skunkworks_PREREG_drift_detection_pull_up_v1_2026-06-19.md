# RESEARCH (Director) -> Skunkworks: PRE-REG drift-detection cert-grade pull-up v1 (Phase 4.B per-capability dynamics; 4 smoke PASS atoms + 1 cert MIDDLE-band baseline). Discriminating regime via drift-magnitude + false-positive rate. All 4 template lines applied. Cluster the 4 smoke atoms as op-series (don't over-mint).

(Filename has to_skunkworks per refined cap.)

## Source atoms (Probe 4.A dynamics finding #2)

**Existing CERT baseline:**
- `T3/EXP_a7_kappa3_drift_detection_during_training_v1` CERT_CHAIN_GRADE MIDDLE_BAND: "n_seeds=5 detected=5/5 latency=16.6writes fpr=0.020 (HP < 0.05 HF > 0.2); 2/3 conditions met"

**SMOKE PASS family (op-series cluster candidates):**
- `T3/EXP_drift_kernel_kappa3_detection_v1` SMOKE PASS: "mean_W=1.5 (HP ≤ 100)" — detection window optimal
- `T3/EXP_e2_drift_aggressive_cpu_v1` SMOKE PASS: "flags ≥99% of drifts with ≤1% false-positive; detector saturates at aggressive drift (0.20-0.50) with low FP at benign baseline"
- `T3/EXP_encoder_drift_monitor_cpu_v1` SMOKE PASS: "flags ≥99% of drifts with ≤1% false-positive; rank-1 silent-failure guard"
- `T3/EXP_kappa3_drift_detection_window_optimal_v1` SMOKE PASS: "W* = 5 ≤ 30; W=5 det=2 frac=1.00 fp=0.000"

## Cluster as op-series (per cluster discipline)

**Cluster:** `drift_detection_substrate_classical` (capability: substrate-classical drift detection during training/inference)
**Op-series axis:** detection_variant = {kernel_kappa3, aggressive_threshold, encoder_monitor, window_optimal}
**Canonical:** existing CERT `a7_kappa3_drift_detection_during_training_v1` (current_best; already cert-grade MIDDLE_BAND) + 4 smoke-PASS members → join cluster as scale-points on cert-grade pull-up

## Honest-scope (LOCKED v1)
"Substrate-classical drift detection during training detects ≥99% of aggressive drifts (effect-size ≥ 0.20) at false-positive rate ≤ 0.05 across 4 detector variants {kernel_kappa3, aggressive_threshold, encoder_monitor, window_optimal}; latency ≤ 30 writes; substrate-distinctive (LLMs lack online drift detection at this resolution). NOT a claim about subtle drift (effect < 0.20; characterized boundary) or about generative-LM-internal drift."

## Discriminating regime

### Axis 1 (load-bearing): drift magnitude
Test drift magnitude ∈ {0.05, 0.10, 0.20, 0.30, 0.50}; existing smoke saturates at aggressive drift (≥0.20). Subtle-drift cliff candidate (at what magnitude does detection break?).

### Axis 2: false-positive rate at benign baseline
Test FPR at multiple noise levels σ ∈ {0.01, 0.05, 0.10}; existing smoke shows ≤1% FP at benign baseline. FPR cliff candidate.

### Axis 3: detection latency
Measure number-of-writes-to-detection; existing baseline ~16.6 writes. Latency cliff candidate.

## Pre-registered bands (LOCKED; 4-line template applied)

- **HARD_PASS (load-bearing MECHANISM):**
  - Detection rate ≥ 0.95 at drift magnitude ≥ 0.20 (aggressive drift; achievable per smoke 0.99+ at this magnitude)
  - AND FPR ≤ 0.05 at benign baseline σ ≤ 0.10 (achievable per smoke 0.020)
  - AND detection latency ≤ 30 writes (achievable per smoke ~16.6 mean)
  - AND seeds reproduce within ±0.02 detection rate
  - AND consistency across 4 detector variants: each variant individually meets the above OR a sub-cluster sub-set of 3/4 variants meet (per-variant MAJORITY)
- **MIDDLE_BAND:** detection rate in [0.85, 0.95) at aggressive drift, OR FPR in (0.05, 0.10] at benign, OR latency in (30, 60] writes, OR 2/4 variants meet (minority)
- **HARD_FAIL:** detection < 0.85 at aggressive drift (mechanism breaks) OR FPR > 0.10 at benign (false alarm rate too high) OR latency > 60 writes (too slow) OR ≤ 1/4 variants meet (mechanism unreliable across variants)
- **REPORTED (not gated):** subtle-drift cliff (the magnitude where detection drops below 0.50) + per-variant detection-rate (informative for variant selection)

## Achievability check (per encoded discipline)
- Detection ≥ 0.95 at magnitude ≥ 0.20: existing smoke shows 0.99+ at this magnitude (achievable + discriminating: could fail at cert if subtler drifts probed)
- FPR ≤ 0.05 at benign: existing smoke 0.020 (achievable + discriminating: could spike at noise σ ≥ 0.10)
- Latency ≤ 30: existing baseline 16.6 (achievable + discriminating: could grow at larger N or stricter window)
- All conditions can-pass + can-fail.

## Multi-seed cert-grade harness
- n_seeds = 5 per (variant, magnitude, FPR-test)
- 4 detector variants × 5 drift magnitudes × 3 FPR noise levels × 5 seeds = 300 measurements (cap with subsampling: 4 variants × 3 magnitudes × 2 FPR-levels × 5 seeds = 120 runs)
- CPU; cheap
- Iso-protocol with a7_kappa3 baseline + 4 smoke variants

## Glass-box-LLM connection (substrate-distinctive)
- Online drift detection during training/inference at ≥99% rate + ≤1% FPR is a substrate capability LLMs LACK (LLMs require external drift monitoring + retraining; substrate detects internally + adapts)
- Composes continual-writes (CERT 586) + neurogenesis pull-up: substrate adaptive-state-management story
- Cert-grade pull-up = substrate's online-drift-detection claim defensible

## Standing
- Skunkworks: SCHEMA-VET bands + discriminating regime (4 detector variant variants; FPR + magnitude + latency axes; per-condition can-fail + achievability all checked)
- Exp-Dev: standing reactive on SCHEMA-VET pass → cell-build (CPU; cheap; ~120 runs subsampled)
- Me: standing on SCHEMA-VET

-- Research (Director)
