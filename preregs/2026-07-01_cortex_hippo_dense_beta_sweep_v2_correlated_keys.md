# Pre-registration: cortex_hippo_dense_beta_sweep_v2_correlated_keys

**Date:** 2026-07-01
**Anchor base:** cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_substrate_cortex_hippo_dense_beta_sweep_v2_correlated_keys_core.py (shared)
- experiments/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_7.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_13.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_19.py

**Queue:** local_cpu_queue for smoke ONLY (USER-locked 2026-07-01: no FULL to
local). FULL runs -> remote_cpu_queue via hdi_orchestrator push (numpy cell;
no GPU required).

**Parent + prior work (substrate-KB verified):**
- v1 beta_sweep (parent MM Atom 3): preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md
  Ran 1-seed HP smoke at M=4096, N_c=4096 with beta in {5,8,13,20,32}. All
  arms saturated at recall=1.000. Skunkworks 2026-07-01 verdict: MIDDLE_BAND
  (META_RULE_L band-floor at ceiling + META_RULE_Q universal saturation);
  Atom 3 flagged MM.
- Skunkworks-declared revival criterion (Atom 3 Wave 1 2026-07-01):
    "M >= 32768 at N_c=4096 OR correlated keys (subspace-drawn)."
- This cell = Path B (correlated keys). Path A (M=32768) risks Windows GPU
  8GB VRAM cliff already seen on Cell D N-sweep earlier this session.
- Substrate-KB concept-query at authoring time returned max cosine=0.249;
  no prior "beta-sweep + correlated-keys" cell in substrate. Adjacent prior:
  preregs/2026-05-20_wave14h_alpha_sweep_v2.md tested alpha-axis on
  correlated keys, NOT beta-axis. Genuinely novel.

## Hypothesis (v2 CORRELATED-KEYS REVIVAL)

Under independent-Gaussian keys at N_c=4096, M=4096, the beta axis is
NOT discriminating: all beta in {5, 8, 13, 20, 32} produce recall=1.000
(universal saturation; Atom 3 v1 MM). The prediction: when keys are drawn
from a d_sub-dimensional subspace of R^{N_c} with d_sub << N_c, off-diagonal
similarity grows from ~1/sqrt(N_c) to ~1/sqrt(d_sub), forcing attention to
discriminate under correlation. At high d_sub/N_c ratio (correlated regime),
smaller beta values should suffer confusion (low recall) while larger beta
values should retain sharper attention peaks (higher recall).

**Predicted structural finding:**
- INDEP (d_sub=None): both beta arms saturate at recall >= 0.95 (positive
  control; reproduces v1 MM).
- CORR_SUB512: beta=5 recall in [0.60, 0.90); beta=13 recall in [0.90, 1.00).
  |delta| >= 0.10 (partial discrimination).
- CORR_SUB256: beta=5 recall in [0.30, 0.70); beta=13 recall in [0.80, 1.00).
  |delta| >= 0.15 (clear discrimination) -> **HP fires**.

If HP fires 3-of-3 seeds: **CHAIN_GRADE_BETA_AXIS_DISCRIMINATES_CORRELATED**.
Supersedes Atom 3 MM. Stage 1 characterization: beta is a real substrate
lever when keys have correlation structure (the M3 real-world regime).

## Design

**Cell-arms (6 per seed):**
- ARM_BETA_5_INDEP           (independent keys; beta=5;  d_sub=None)
- ARM_BETA_13_INDEP          (independent keys; beta=13; d_sub=None)
- ARM_BETA_5_CORR_SUB512     (subspace d_sub=512; beta=5)
- ARM_BETA_13_CORR_SUB512    (subspace d_sub=512; beta=13)
- ARM_BETA_5_CORR_SUB256     (subspace d_sub=256; beta=5)
- ARM_BETA_13_CORR_SUB256    (subspace d_sub=256; beta=13)

**Scale (FULL):** N_c=8192, M=4000. Alpha = M / N_c ~= 0.49 (sub-critical).
**Scale (SMOKE):** N_c=2048, M=1000. Alpha = M / N_c ~= 0.49 (matched ratio).
**Beta values:** {5, 13} — v1 top-2 arms (BETA_LO below clamp; BETA_HI at
    log2(M)/margin sweet spot).
**Backend:** numpy (CPU). No GPU required.
**Seeds:** 7, 13, 19 (dispatched sequentially: seed_7 smoke first).

**Correlated-key generation (algorithm):**
1. Draw B_raw ~ N(0, 1) shape (N_c, d_sub).
2. QR decompose: Q shape (N_c, d_sub), orthonormal columns.
3. Draw coeffs ~ N(0, 1) shape (M, d_sub).
4. keys_raw = coeffs @ Q^T  shape (M, N_c) but confined to span(Q).
5. keys = l2-normalize(keys_raw).
Values are ALWAYS independent Gaussian (only keys carry correlation).

**Discriminator sanity (encoded in selftest):**
- INDEP keys at N_c=2048 have off-diag |sim| ~ 1/sqrt(2048) ~= 0.022 (asserted <0.05).
- CORR_SUB256 keys at N_c=2048 have off-diag |sim| ~ 1/sqrt(256) ~= 0.062,
  which is >= 1.5x INDEP (asserted).
- Tiny-world (d_sub=32, n_c=256, m=64) beta=1 vs beta=50 must yield
  different recalls (asserted); guarantees beta axis wired into computation.

## Discriminator gates

**HP (per seed):**
- HP_INDEP_REPRODUCES_SATURATION:
    recall(ARM_BETA_5_INDEP) >= 0.95 AND
    recall(ARM_BETA_13_INDEP) >= 0.95
  (positive control reproduces v1 Atom 3 MM saturation)
- HP_BETA_DISCRIMINATES_CORRELATED:
    max(|recall(ARM_BETA_5_CORR_SUB512) - recall(ARM_BETA_13_CORR_SUB512)|,
        |recall(ARM_BETA_5_CORR_SUB256) - recall(ARM_BETA_13_CORR_SUB256)|)
    >= 0.15
  (beta axis IS discriminating in at least one correlated regime)

Both must hold for HP.

**HF (per seed):**
- HF_CRUMBLE: any arm recall < 0.20 (mechanism broken; encoder failed)
- HF_INDEP_DIDNT_SATURATE: either INDEP arm < 0.95 (broken-PC:
  parent Atom 3 regime not reproduced; can't trust delta comparisons)
- HF_META_RULE_AF: any arm-pair bit-identical
  (ceiling-tie exempt: both at 1.000 AND same subspace_class)
- HF_CARDINALITY: n_arms != 6

**MB (per seed):**
- max_corr_delta in [0.05, 0.15) at any correlated regime (partial;
  HP not fully fired)
- HF_STILL_SATURATED_CORR: max_corr_delta < 0.05 AND INDEP saturated
  (correlation did NOT break saturation; Atom 3 MM stands; need
  higher M or smaller d_sub)

**Chain-grade promotion (Skunkworks aggregation across 3 seeds):**
3-of-3 seeds HARD_PASS AND cross-seed cv(delta_corr_sub256) < 15% at
CORR_SUB256.

## Pre-registered fairness disciplines

1. Same M=4000 for all 6 arms per seed.
2. Same N_c=8192 for all 6 arms per seed.
3. Values ALWAYS independent Gaussian; ONLY keys carry correlation
   structure (isolates the correlation effect to attention denominator).
4. Per-arm RNG seeded (seed + hash(arm_name)); no cross-arm aliasing.
5. Beta values FIXED per arm (no adaptive computation); logged in metrics.
6. META_RULE_AF: bit-identical arm pairs auto-HF (ceiling-tie exempt
   only for same subspace_class pairs at 1.000; e.g., two SUB512 arms
   both at 1.000 is legit substrate-saturation-within-regime, but SUB256
   vs SUB512 at 1.000 is a red flag).
7. INDEP arms serve as positive control (broken-PC): if they don't
   saturate, HARD_FAIL — comparison to correlated is invalidated.

## Pre-reg fields (SCHEMA-VET)

- expected_n_units = 6 (per seed cell FULL); 6 in smoke (same arm count).
- cardinality_ok mandatory.
- HARD_FAIL_CARDINALITY_BREACH when n_arms != 6.
- HARD_FAIL_META_RULE_AF_BIT_EXACT (any arm-pair recall identical
  outside ceiling-tie exemption above).
- HARD_FAIL_CRUMBLE when any arm < 0.20.
- HARD_FAIL_INDEP_DIDNT_SATURATE when either INDEP arm < 0.95.
- discriminator_survives_scale: True (smoke uses same alpha ratio; no
  full-N preview needed since single M cell).
- CRLB fields (computed):
  - crlb_floor_computed_M = sqrt(0.25 / M) THEORETICAL@sqrt(0.25/4000) = 0.00790
  - discriminator_reachability = True (HP delta 0.15 >> CRLB 0.008; ratio ~19x)
- calibration_check = "correlated_key_beta_axis_discrimination".
- sec 13 patterns: start_marker + crash_diagnostic + per-seed ckpt + heartbeat.
- arms_differ_verified: True (META_RULE_AF gate in verdict).
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH).
- positive_control_arms: ARM_BETA_5_INDEP + ARM_BETA_13_INDEP (broken-PC).
- parent_atom_3_mm: "cortex_hippo_dense_beta_sweep_v1_seed_7_universal_saturation_2026-07-01".
- revival_criterion: "SKUNKWORKS_CRITERION_B_correlated_keys_path".

## Smoke config

- N_c=2048, M=1000 (smaller; alpha ratio matched at 0.49).
- All 6 arms (full arm cardinality).
- Numpy backend on local_cpu_queue.
- Discriminator MUST FIRE at smoke to justify FULL dispatch:
  - INDEP arms must saturate (recall >= 0.95): reproduces v1 saturation
    at scaled-down regime.
  - At CORR_SUB256, |beta=5 recall - beta=13 recall| must be >= 0.10
    at smoke (relaxed from 0.15 for smoke-scale allowance). If smoke
    delta < 0.10, correlation regime doesn't discriminate at this
    scale — REJECT full dispatch and pivot to Path A (M=32768).
- Expected smoke wall: ~1-3 min per arm x 6 arms = 6-18 min budget.

## FULL config (per seed, if smoke HP)

- N_c=8192, M=4000, all 6 arms.
- Numpy backend on remote_cpu_queue.
- Per-seed timeout: 2400s (40 min). Attention matmul per arm at (4000, 8192)
  x (4000, 8192)^T = 4000*4000*8192 ~= 130 GFLOPS. At 4 GFLOPS/sec
  numpy ~= 33s per arm; 6 arms = ~200s per seed; wide margin.

## Cap-map rows (proposed; on 3-of-3 HP across seeds)

- Cortex dense-Hopfield READ-REPLACE beta axis IS discriminating in
  correlated-key regime (subspace-drawn keys with d_sub <= 512).
- Correlation structure of keys IS a real substrate lever; universal
  saturation is a regime-locked property of independent-Gaussian keys,
  NOT a general property of the mechanism.
- Atom 3 MM supersedes -> CG on beta_sweep under correlated keys.

## Coordination

- Cell-author: exp_dev (this dispatch; seed_7 smoke first via local_cpu).
- Push+FULL dispatch: hdi_orchestrator (harness-DENIED push for exp_dev;
  routes to remote_cpu_queue via SSH after commit-and-push).
- Landed-VET: skunkworks (3-seed aggregation + delta_corr_sub256 audit).

## Risk + mitigations

- **QR decomposition at N_c=8192 x d_sub=512**: O(N_c * d_sub^2) ~= 2e9 ops.
  ~5-10s in numpy; encoded ONCE per (seed, arm). Acceptable.
- **Fully-independent keys may not saturate at N_c=8192, M=4000**: at
  alpha=0.49 (sub-critical), theory says recall should still be at ceiling.
  If INDEP arms fail to saturate, broken-PC HF fires (design working as
  intended).
- **Correlation may drive ALL arms to crumble**: if d_sub=256 is too
  aggressive, both beta=5 and beta=13 could collapse to < 0.20. HF_CRUMBLE
  fires; pivot to less-aggressive d_sub={1024, 512} on rerun.

## Differences from v1

- v1: independent keys; sweeps beta {5,8,13,20,32} at M {4096, 8192, 16384};
  M-scaling of adaptive beta formula.
- v2 (this): correlated keys via subspace; sweeps beta {5, 13} at 3 d_sub
  values {None, 512, 256} at fixed M=4000, N_c=8192; probes discrimination
  under correlation.
- v2 is a REVIVAL cell, not a supersession of v1: v1 characterized the
  independent-key regime (universal saturation was the finding); v2 asks
  whether correlated-key regime restores beta-axis discrimination.

## Milestone significance

If HP (all 3 seeds pass): **CG on beta_sweep under correlated keys**. Stage 1
100% close per USER directive. Adds substrate primitive: "beta selects
attention sharpness in proportion to key-correlation density".

If MB (partial): beta discriminates in one correlated regime but not both;
suggests d_sub needs finer sweep; queue v3 with d_sub in {128, 256, 512, 1024}.

If HF (INDEP didn't saturate): the smoke-vs-full scale mismatch is broken;
reduce N_c/M ratio in FULL to match smoke; requeue.

If HF (crumble): d_sub too aggressive; requeue with d_sub={1024, 512, 256}.

## Citations

- Ramsauer et al. (2021) "Hopfield Networks is All You Need" ICLR 2021.
- Provably Optimal Capacity for Modern Hopfield (2024) arxiv/2410.23126.
- Substrate-KB adjacent (correlated glass systems / KWW):
  notes/research_drill_online_continual_real_3x_2026-06-10.md::chunk027
  (cosine=0.249; adjacent theory on correlation-density-dependent decay).

## Reference prior cells

- v1 (parent): experiments/exp_cortex_hippo_dense_beta_sweep_v1_seed_*.py
- v1 prereg: preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md
- Wave 14h alpha_sweep_v2 (adjacent; correlated-keys but alpha-axis):
  preregs/2026-05-20_wave14h_alpha_sweep_v2.md
