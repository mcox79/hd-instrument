# Pre-registration: cortex_hippo_dense_beta_sweep_v3_query_noise

**Date:** 2026-07-01
**Anchor base:** cortex_hippo_dense_beta_sweep_v3_query_noise_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_substrate_cortex_hippo_dense_beta_sweep_v3_query_noise_core.py (shared)
- experiments/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_13.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_19.py

**Queue:** local_cpu_queue for smoke ONLY (USER-locked 2026-07-01: no FULL to
local). FULL runs -> remote_cpu_queue via hdi_orchestrator push (numpy cell;
no GPU required).

## Parent + prior work (substrate-KB verified)

- **v1 (parent MM; Atom 3):** preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md
  Ran 1-seed HP smoke at M=4096, N_c=4096 with beta in {5,8,13,20,32}. All
  arms saturated at recall=1.000. Skunkworks 2026-07-01 verdict: MIDDLE_BAND
  (META_RULE_L band-floor at ceiling + META_RULE_Q universal saturation);
  Atom 3 flagged MM. Skunkworks-declared revival criterion: M>=32768 OR
  correlated keys.

- **v2 (correlated-keys revival; HARD_FAIL smoke; PROBE DISCOVERED NOISE AXIS):**
  preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v2_correlated_keys.md
  Smoke landed at data/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_7_smoke/
  metrics.json. All 6 arms (INDEP, CORR_SUB512, CORR_SUB256) x (beta=5, beta=13)
  saturated at recall=1.000 despite cos_margin dropping from 0.982 (INDEP) to
  0.950 (SUB256). Verdict: HARD_FAIL (META_RULE_AF cross-class bit-identity).
  **Root cause identified during v2 probe:** `queries = keys` trivially wins
  argmax under Gaussian vals regardless of attention sharpness (beta), so
  key correlation ALONE cannot break saturation. Same probe on 30-triple
  (M, d_sub, noise_std) grid discovered the actually-discriminating axis:
  **QUERY NOISE**. At N_c=2048, M=1000, noise_std=0.1:
    INDEP:  r(b=5)=0.494 vs r(b=13)=1.000  |delta|=0.506
    SUB512: r(b=5)=0.435 vs r(b=13)=1.000  |delta|=0.565
    SUB256: r(b=5)=0.246 vs r(b=13)=1.000  |delta|=0.754

- **Director APPROVED v3 pivot 2026-07-01.** v3 uses INDEPENDENT keys
  (v1 regime) and sweeps QUERY NOISE.

- **Substrate-KB adjacent prior (cosine 0.30-0.33):**
  - `notes/strategy_decisions_2026-06-08.md::chunk150` — PP-135 n1d
    "noise_robust HP" annotated as broken by cell reviewer because
    "anchor labeled noise_robust but no noise dimension in metrics; result
    is baseline-equivalent". v3 EXPLICITLY sweeps noise_std, addressing
    that critique with per-arm noise_std field in metrics.json.
  - `preregs/2026-05-21_wave14zm_noise_robust.md` + `wave14zr_extreme_noise.md`
    — prior noise-robustness preregs on DIFFERENT mechanisms (Kerdock
    encoder). Named verdict fields template; different primitive. Not
    a rediscovery.
  - `notes/research_to_exp_dev_CYCLE_200_FOLLOWUPS_2026-06-09.md` —
    PP-215 noise robustness MID rescue precedent. Direct architectural
    precedent for this v3 MM->HP rescue via explicit noise sweep.
  Novel primitive under test: cortex dense-Hopfield READ-REPLACE
  noise-robustness via beta axis.

## Hypothesis (v3 QUERY-NOISE REVIVAL)

Under exact queries (query = stored key), attention argmax trivially recovers
target index regardless of beta -> universal saturation (v1 + v2 finding).
Under noisy queries (query = key + eps, eps ~ N(0, noise_std)), attention
must discriminate stored keys from perturbed queries; **beta controls
attention sharpness = noise robustness**.

**Predicted structural finding (v2 probe direct evidence):**
- noise_std=0.0: both beta arms saturate at recall >= 0.95 (v1 regime
  reproduction; positive control).
- noise_std=0.1: beta=5 recall in [0.30, 0.70]; beta=13 recall in [0.90, 1.00].
  |delta| >= 0.30 -> **HP fires**.
- noise_std=0.3: BOTH beta arms crumble (recall < 0.7 per v2 probe;
  possibly both < 0.20 at N_c=8192 M=4000).

If HP fires 3-of-3 seeds AND cross-seed cv(delta_noise_0p1) < 15%:
**CHAIN_GRADE_BETA_NOISE_ROBUSTNESS**. Supersedes Atom 3 MM. Stage 1
characterization: beta is a real substrate lever governing noise-robust
attention (the M3-relevant property).

## Design

**Cell-arms (6 per seed):**
- ARM_BETA_5_NOISE_0P0   (query=key exactly;  beta=5;  ceiling PC)
- ARM_BETA_13_NOISE_0P0  (query=key exactly;  beta=13; ceiling PC)
- ARM_BETA_5_NOISE_0P1   (query=key+N(0,0.1); beta=5;  discriminating)
- ARM_BETA_13_NOISE_0P1  (query=key+N(0,0.1); beta=13; discriminating)
- ARM_BETA_5_NOISE_0P3   (query=key+N(0,0.3); beta=5;  crumble edge)
- ARM_BETA_13_NOISE_0P3  (query=key+N(0,0.3); beta=13; crumble edge)

**Scale (FULL):** N_c=8192, M=4000. Alpha = M / N_c ~= 0.49 (sub-critical).
**Scale (SMOKE):** N_c=2048, M=1000. Alpha = M / N_c ~= 0.49 (matched ratio).
**Keys/vals:** INDEPENDENT Gaussian, l2-normalized (v1 regime; correlation
    is orthogonal to the finding per v2 probe).
**Query construction:** query = l2norm(key + N(0, noise_std)); noise drawn
    per-arm from independent RNG (decoupled from key draw).
**Beta values:** {5, 13} (v1 top-2 arms).
**Backend:** numpy (CPU). No GPU required.
**Seeds:** 7, 13, 19 (dispatched sequentially: seed_7 smoke first).

**Discriminator sanity (encoded in selftest):**
- noise_std=0.0 produces exact query (max|q-k| < 1e-12; asserted).
- noise_std=0.1 produces perturbed query (cos(q,k) in (0.5, 0.999); asserted).
- Tiny-world discriminator: N_c=256 M=200 noise_std=0.3, beta=5 vs beta=13
  yield |delta| >= 0.10 (asserted; validates beta axis wired to noise-robust
  attention at any scale where noise breaks near-saturation).

## Discriminator gates

**HP (per seed):**
- HP_NOISE_0_SATURATES:
    recall(ARM_BETA_5_NOISE_0P0)  >= 0.95 AND
    recall(ARM_BETA_13_NOISE_0P0) >= 0.95
  (positive control reproduces v1 Atom 3 MM saturation; broken-PC gate)
- HP_BETA_DISCRIMINATES_UNDER_NOISE:
    |recall(ARM_BETA_5_NOISE_0P1) - recall(ARM_BETA_13_NOISE_0P1)| >= 0.30
  (beta axis IS discriminating under query noise; v2 probe predicts ~0.5)

Both must hold for HP.

**HF (per seed):**
- HF_CRUMBLE: any noise_0P0 or noise_0P1 arm recall < 0.20 (unexpected;
  noise_0P3 arms exempt from this — crumbling is the PREDICTED behavior)
- HF_NOISE_0_DIDNT_SATURATE: either NOISE_0P0 arm < 0.95 (broken-PC:
  v1 regime not reproduced; can't trust noise-axis deltas)
- HF_CRUMBLE_AT_HIGH_NOISE: BOTH NOISE_0P3 arms > 0.70 (crumble-edge
  prediction wrong; means noise=0.3 isn't crumble edge as v2 probe indicated)
- HF_META_RULE_AF: any arm-pair bit-identical (ceiling-tie exempt for
  same noise_class at 1.000 only; floor-pair exempt for same noise_class
  both < 0.02)
- HF_CARDINALITY: n_arms != 6

**MB (per seed):**
- max_noise_0p1_delta in [0.15, 0.30) at noise=0.1: partial discrimination
  (queue v4 with finer noise grid)
- MB_NO_NOISE_DISCRIM: max_noise_0p1_delta < 0.15 AND NOISE_0P0 saturates
  (noise axis did NOT fire discriminator; possible if effective noise
  differs at FULL scale; would trigger v4 with larger noise_std)

**Chain-grade promotion (Skunkworks aggregation across 3 seeds):**
3-of-3 seeds HARD_PASS AND cross-seed cv(delta_noise_0p1) < 15%.

## Pre-registered fairness disciplines

1. Same M=4000 for all 6 arms per seed.
2. Same N_c=8192 for all 6 arms per seed.
3. Same INDEPENDENT-Gaussian keys+vals regime for all arms; ONLY noise_std
   varies (isolates the noise effect to attention-input distribution).
4. Per-arm RNG seeded (seed + hash(arm_name)); no cross-arm aliasing.
5. Query noise RNG SEPARATE from key/val RNG (avoids co-variance):
   noise_rng = RandomState(seed + arm_offset + 100003).
6. Beta values FIXED per arm (no adaptive computation); logged in metrics.
7. META_RULE_AF: bit-identical arm pairs auto-HF (ceiling-tie exempt only
   for same noise_class pairs at 1.000; floor-pair exempt for same
   noise_class pairs both < 0.02).
8. NOISE_0P0 arms serve as positive control (broken-PC): if they don't
   saturate, HARD_FAIL — comparison to noisy regimes is invalidated.

## Pre-reg fields (SCHEMA-VET)

- expected_n_units = 6 (per seed cell FULL); 6 in smoke (same arm count).
- cardinality_ok mandatory.
- HARD_FAIL_CARDINALITY_BREACH when n_arms != 6.
- HARD_FAIL_META_RULE_AF_BIT_EXACT (any arm-pair recall identical outside
  ceiling-tie / floor-pair exemption above).
- HARD_FAIL_CRUMBLE when any noise_0P0 or noise_0P1 arm < 0.20.
- HARD_FAIL_NOISE_0_DIDNT_SATURATE when either NOISE_0P0 arm < 0.95.
- HARD_FAIL_CRUMBLE_AT_HIGH_NOISE when BOTH NOISE_0P3 arms > 0.70.
- discriminator_survives_scale: True (v2 probe already ran at scaled-up
  N_c=2048; FULL uses 4x N_c and 4x M with same alpha; noise cosine
  drop scales with sqrt(N) => stronger discrimination at larger N).
- CRLB fields (computed):
  - crlb_floor_computed_M = sqrt(0.25 / M) = sqrt(0.25/4000) = 0.00790
  - discriminator_reachability = True (HP delta 0.30 >> CRLB 0.008; ratio ~38x)
- calibration_check = "query_noise_beta_axis_discrimination".
- sec 13 patterns: start_marker + crash_diagnostic + per-seed ckpt + heartbeat.
- arms_differ_verified: True (META_RULE_AF gate in verdict).
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH).
- positive_control_arms: ARM_BETA_5_NOISE_0P0 + ARM_BETA_13_NOISE_0P0 (broken-PC).
- parent_atom_3_mm: "cortex_hippo_dense_beta_sweep_v1_seed_7_universal_saturation_2026-07-01".
- parent_v2_correlated_hf: "cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_7_smoke_HF_2026-07-01".
- revival_criterion: "V2_PROBE_DISCOVERED_QUERY_NOISE_AXIS_DIRECTOR_APPROVED_v3_PIVOT".
- noise_dimension_in_metrics: True (each arm records noise_std + noise_class).

## Smoke config

- N_c=2048, M=1000 (matched alpha=0.49).
- All 6 arms (full arm cardinality).
- Numpy backend on local_cpu_queue.
- Expected smoke wall: ~1-3 min per arm x 6 arms = 6-18 min budget;
  probe measurements showed ~5.5s at same scale in v2 (single seed).
- Discriminator MUST FIRE at smoke to justify FULL dispatch:
  - NOISE_0P0 arms both saturate (recall >= 0.95).
  - At noise=0.1, |beta=5 recall - beta=13 recall| >= 0.30 at smoke
    (matches HP; v2 probe found |delta|=0.506 at this exact scale).

## FULL config (per seed, if smoke HP)

- N_c=8192, M=4000, all 6 arms.
- Numpy backend on remote_cpu_queue via hdi_orchestrator push.
- Per-seed timeout: 1800s (30 min) — Director-specified. Attention matmul
  per arm at (4000, 8192) x (4000, 8192)^T = ~130 GFLOPS. At 4 GFLOPS/sec
  numpy ~= 33s per arm; 6 arms = ~200s per seed; wide margin.

## Cap-map rows (proposed; on 3-of-3 HP across seeds)

- Cortex dense-Hopfield READ-REPLACE beta axis IS discriminating under
  query noise (noise_std=0.1 with independent Gaussian keys, alpha ~ 0.5).
- Beta ~ noise-robustness axis: higher beta -> sharper attention peaks ->
  higher recall under bounded query noise.
- Universal saturation (v1 finding) IS a regime-locked property of exact
  queries; the M3-relevant property (noise-robustness) DOES discriminate
  along the beta axis. Supersedes Atom 3 MM.

## Coordination

- Cell-author: exp_dev (this dispatch; seed_7 smoke first via local_cpu).
- Push+FULL dispatch: hdi_orchestrator (harness-DENIED push for exp_dev;
  routes to remote_cpu_queue via SSH after commit-and-push).
- Landed-VET: skunkworks (3-seed aggregation + delta_noise_0p1 audit;
  cross-seed cv gate).

## Risk + mitigations

- **Effective noise scales with sqrt(N)**: noise_std=0.1 at N_c=2048 has
  cosine drop ~= 0.1/sqrt(2048)*sqrt(2048)=0.1 relative to key norm 1.0.
  At N_c=8192, noise contribution scales the SAME way (each dim
  contributes independently). Cosine similarity of noisy query to true
  key: ~= 1/sqrt(1 + noise_std^2) ~= 0.995 at noise=0.1 regardless of N_c.
  BUT the softmax gap between right-key and wrong-key at higher N_c
  concentrates faster (larger effective margin). Net effect: v3 FULL
  should discriminate AT LEAST as strongly as smoke.
- **noise=0.3 may crumble too hard at FULL**: if BOTH noise_0P3 arms
  crumble to < 0.02, they'll tie under META_RULE_AF floor-pair; my
  verdict exempts same noise_class floor-pair from AF, so this is safe.
- **noise=0.3 may NOT crumble at FULL** (if larger N_c helps more than
  larger M hurts): would fire HF_CRUMBLE_AT_HIGH_NOISE. In that case,
  v4 pivots to noise_std={0.1, 0.3, 0.5} to find the crumble edge.
- **Per-seed runtime**: 30 min timeout. Expected ~5-10 min; wide margin.

## Differences from v2

- v2: correlated keys via subspace (d_sub axis); INDEP + CORR_SUB512 +
  CORR_SUB256 at exact queries; sweeps beta {5, 13}. Smoke HARD_FAIL
  (queries=keys trivially wins argmax; correlation insufficient).
- v3 (this): INDEPENDENT keys (v1 regime); sweeps QUERY NOISE
  {0.0, 0.1, 0.3} at beta {5, 13}. Directly targets v2-probe-discovered
  discriminating axis.

## Milestone significance

If HP (all 3 seeds pass): **CG on beta_sweep under query noise**. Stage 1
100% close per USER directive. Adds substrate primitive: "beta selects
attention sharpness = noise robustness in cortex dense-Hopfield READ".
Supersedes Atom 3 MM (universal saturation at exact queries is a
regime-locked artifact; the mechanism DOES discriminate along the beta
axis in the noise-robustness regime).

If MB (partial): beta discriminates weakly (|delta| in [0.15, 0.30)); queue
v4 with finer noise grid or larger noise_std.

If HF (NOISE_0P0 didn't saturate): v1 regime not reproduced; encoder or
setup broken; requeue after diagnosis.

If HF (CRUMBLE_AT_HIGH_NOISE): noise=0.3 doesn't crumble at FULL scale;
pivot to noise_std={0.1, 0.3, 0.5} in v4.

## Citations

- Ramsauer et al. (2021) "Hopfield Networks is All You Need" ICLR 2021.
  Beta = attention temperature -> pattern completion robustness.
- Provably Optimal Capacity for Modern Hopfield (2024) arxiv/2410.23126.
- v2 probe direct evidence (this session; recorded in v3 core module docstring).

## Reference prior cells

- v1 (parent MM): experiments/exp_cortex_hippo_dense_beta_sweep_v1_seed_*.py
- v1 prereg: preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md
- v2 (correlated-keys HF): experiments/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_*.py
- v2 prereg: preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v2_correlated_keys.md
- v2 smoke metrics: data/exp_cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_7_smoke/metrics.json
