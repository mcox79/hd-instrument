# Pre-registration: adversarial_aqsim_path_d_compose_v5_k2_n16384

Date: 2026-06-01
Anchor: adversarial_aqsim_path_d_compose_v5_k2_n16384
Queue: overnight_queue (GPU)
Script: experiments/exp_adversarial_aqsim_path_d_compose_v5_k2_n16384.py
HDLAB_EXP_NAME: 7d39e13
PROT-018: _n16384 binds N = 16384 (verified: N_FULL = 16384 in script)
PROT-019: timeout_s = 21600 (PROT-018 _n16384 floor; run > 2h flagged)
PROT-020: device=cuda
PROT-021: per-seed checkpointing (5 seeds: 7, 17, 23, 31, 41)

## Hypothesis

The K=2 production op-point (validated at N=4096 by K2PROD v1 HARD_PASS) holds
at N=16384 with M=4096 (M/N=0.25). Specifically:
- defense_activation_rate >= 0.90 on adversarial subthreshold probes
- path_d_acc_gated_compressed >= 0.95 (Path D accuracy with K=2 on compressed W)
- comp_delta <= 0.05 (|acc_gated_comp - acc_gated_uncomp| < 5pp)

Cross-N context: v2 (N=4096 K=100) HARD_PASS, K2PROD v1 (N=4096 K=2) HARD_PASS.
v5 extends both to N=16384.

## Design

- N = 16384 (log2=14, EVEN; Kerdock OK per PROT-022)
- M = 4096 (M/N = 0.25; halved from v4's 0.5 to fit VRAM)
- K_paths = 2 (production op-point, key delta from v4's K=100)
- depth = 5
- alpha = 0.45 (subthreshold collision pressure, same as v2/v3/v4)
- n_adv = 90, n_leg = 10 (90/10 defense pressure, same as v4)
- Seeds: [7, 17, 23, 31, 41] (5-seed standard)
- device = cuda

## Pre-registered bands

### HARD-PASS
ALL of the following in 4/5+ seeds (HP_MIN_SEEDS=4):
- defense_activation_rate >= 0.90
- acc_path_d_gated_compressed >= 0.95
- comp_delta_gated <= 0.05 (|acc_gated_comp - acc_gated_uncomp|)

Strategic target: 5/5 unanimous matching K2PROD v1 and v2 numbers.

### HARD-FAIL
ANY of the following in majority of seeds (>= 3/5):
- defense_activation_rate < 0.50
- acc_path_d_gated_compressed < 0.50
OR: special verdict DEFENSE_STILL_UNNECESSARY if all seeds have def_act < 0.10.

### MIDDLE-BAND
Otherwise: characterizable degradation (e.g., one seed barely fails one metric,
or M/N=0.25 introduces a systematic accuracy drop at cross-N regime).

## Outcome plan

- HARD_PASS: compositional sub-row lifts "N=4096 only" caveat to
  "N=4096 + N=16384"; sub-row score 0.75-0.90 -> 0.80-0.95.
  First cross-N evidence for K=2 production op-point.
- HARD_FAIL at accuracy: investigate M/N=0.25 sub-saturation at N=16384.
  Consider rehab with M/N=0.50 (M=8192) but using K=2 (much smaller memory
  than v4's K=100 + M=8192 which OOMed).
- HARD_FAIL at defense: adversarial construction validity check;
  investigate alpha scaling with N.
- MIDDLE_BAND: characterize which axis failed; iterate.

## Memory budget

W_base (float32): N * M * 4 = 16384 * 4096 * 4 = 268,435,456 bytes = 256 MB
K_paths=2 path storage: ~negligible vs K=100
Total expected peak: ~1.0-1.5 GB (well under 6 GB threshold)
Smoke verified: instrumentation selftest prints peak_vram_mb at runtime.
Multi-scale smoke (N=1024 + N=4096): both PASS def_act=1.000, acc_gated_comp=1.000.

## Timeout estimate

Formula: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))
- smoke_wall_s = 0.03s on CPU (K=2 very fast; GPU will be faster)
- Reference: K2PROD v1 elapsed estimate: ~300s for 5 seeds at N=4096 on GPU
- FULL_N / smoke_N = 16384 / 4096 = 4x (using K2PROD as reference baseline)
- scaling_exp = 1.5 (vector ops, O(N*M) not O(N^2))
- ceil(1.5 * 60 * 4^1.5 * 5) = ceil(1.5 * 60 * 8 * 5) = ceil(3600) = 3600s
- PROT-018 _n16384 floor: 21600s. timeout_s = 21600.
- Note: run > 2h (7200s) -- flagged for visibility. PROT-019 floor mandates this.

## PROT-022 note (informational)

PROT-022 log2-parity hypothesis FALSIFIED by this turn's analysis.
v3 failed at N=8192 (log2=13, ODD) -- originally attributed to PROT-022 BSC guard.
v4 OOM at N=16384 (log2=14, EVEN, Kerdock OK) confirms: the actual failure mode
is GPU memory cost at large N (K_paths=100 x M=8192), NOT codebook precondition.
PROT-022 BSC guard trigger at N=8192 was a genuine instrumentation issue but
separate from the cross-N scale limit.

## Formula self-tests (verified in _instrumentation_selftest())

1. N=16384, log2=14 (EVEN) -> Kerdock OK. PASS.
2. M/N = 4096/16384 = 0.25. PASS.
3. W_base bytes = 268MB << 6 GB. PASS.
4. Compression max_err = 0.0147 (< max_val / 10). PASS.
5. K_PATHS=2 (1 positive + 1 decoy). PASS.
6. Probe max_sim = 0.450 (~alpha=0.45). PASS.
7. Verdict gates HP/HF/STILL_UNNEC: all correct. PASS.
8. Live smoke: def_act=1.000, acc_gated_comp=1.000, comp_delta=0.000. PASS.
9. 4x-smoke (N=4096, M=1024): def_act=1.000, acc_gated_comp=1.000. PASS.

## Smoke gate result

PASS. Wall time: 0.03s (CPU). All metrics non-null, non-sentinel.
Effect size: maximal (d >> 1.0; def_act=1.000 >> HF=0.50; acc=1.000 >> HF=0.50).
Walk-back gate: not triggered (smoke vastly exceeds hard-pass thresholds).
