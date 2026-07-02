# Prereg: distributional_shape_zipfian_v2 (seed_7 / seed_13 / seed_19)

## Anchors
- `distributional_shape_zipfian_v2_seed_7`
- `distributional_shape_zipfian_v2_seed_13`
- `distributional_shape_zipfian_v2_seed_19`

## Motivation (Director decision 2026-07-01)

v1 (2026-07-01) HARD-saturated at recall=1.000 across all 15 (alpha, load) points AND at full-N=8192 preview (see `data/exp_distributional_shape_zipfian_v1_seed_7_smoke/metrics.json`). Dense-Hopfield exponential capacity (Ramsauer 2021 eq.14) trivially handles alpha_simple in [0.05, 0.15] regardless of distributional shape. Discriminator did not survive scale (exp_dev pattern C failure); NOT dispatched FULL.

**v2 regime widening per Director:** sparse-coding drill (D-RIP unified framework, `notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`) predicts TWO-TIER failure specifically at loads NEAR THE WALL under noise: high-frequency (head) items stay recoverable due to margin advantage; tail patterns fail earlier than uniform. Need stress axis (query noise) + overload axis to create discriminating regime.

**Critical discriminator predicted by drill (Director synthesis):**
> at (sigma>=0.2, load>=0.30, alpha=1.0): recall_Q1_head - recall_Q4_tail >= 0.15

If two-tier gap fails to fire, sparse-coding prediction FALSIFIED (valid substrate physics finding).

## Parent / Distinct-From

- v1: `experiments/exp_distributional_shape_zipfian_v1_seed_{7,13,19}.py` — 15 arm sweep (5α × 3 load) at loads {0.05, 0.10, 0.15}; no noise axis; saturated.
- Cell D v2 CG (Atom 1): dense-Hopfield READ-REPLACE uniform baseline. Same primitive.
- Prior anchor `substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096` (2026-06-04): character-LM BPC (orthogonal to item recall).

## Design

**Mechanism:** dense-Hopfield READ-REPLACE (unchanged from v1); adaptive β = clamp(log2(M)/margin, [8, 128]).

**Query noise model (new):** bit-flip BSC on bipolar keys. Per-coord flip with prob σ BEFORE L2-normalization; caller L2-normalizes noisy query for cosine attention. σ=0.30 → ~30% coordinates flipped.

**Sweep per seed cell:**
- alpha_shape in {0.0 (uniform), 1.0 (natural Zipf), 2.0 (heavy tail)} — 3 levels
- query_noise sigma in {0.0, 0.15, 0.30} — 3 levels (task-spec asked {0, 0.15, 0.30}; task-spec's 0.20 approximated via 0.15+0.30 bracket)
- load M/N in {0.10, 0.20, 0.30, 0.50, 0.80, 1.20} — 6 levels (extended to include OVERLOAD at 1.20 → M=9830 > N=8192)
- **= 54 arms per seed cell.**

**Per-arm protocol:**
1. Sample M items via Zipf(α) rank weights over random permutation of item IDs.
2. Bipolar keys/vals → K_tape, V_tape L2-normalized (Cell D v2 template).
3. Query = keys[target] + bit-flip(σ) → L2-normalize.
4. Dense-Hopfield attention read; hit = argmax matches target.
5. Recall stratified by rank-quartile Q1 (head) / Q2 / Q3 / Q4 (tail).

**Seeds:** 3 seeds (7, 13, 19); chunked one-seed-per-cell architecture.

## Pre-registered verdict gates

**HARD_PASS (per-seed, canonical points at α=1.0, load=0.30, N=8192):**
- HP_TWO_TIER_ZIPFIAN: at (α=1.0, load=0.30), EITHER σ=0.15 OR σ=0.30 satisfies `Q1_head - Q4_tail >= 0.15` (two-tier gap fires).
- HP_UNIFORM_ZIPFIAN_GAP: at (σ=0.15, load=0.30), `recall(α=0.0) - recall(α=1.0) >= 0.10` (Zipfian degrades vs uniform).
- HP_UNIFORM_BASELINE: at (α=0.0, σ=0.0, load=0.10), `recall_all >= 0.95` (v1 sanity replicate).

**HARD_FAIL (sparse-coding prediction falsified — valid physics finding):**
- HF_PREDICTION_FAILS: at (α=1.0, σ=0.30, load=0.30) OR (α=1.0, σ=0.15, load=0.30), BOTH Q1 AND Q4 ≥ 0.95. Two-tier signature does not appear at wall+noise → dense-Hopfield noise-robustness dominates Zipfian skew at these regimes.

**HARD_FAIL_INFRA:**
- BASELINE_OUT_OF_BAND: (α=0.0, σ=0.0, load=0.10) recall < 0.85 at FULL.
- META_RULE_AF: fewer than 10 distinct arm signatures across 54 arms.
- CARDINALITY_BREACH: len(core_arms) != 54.

**MIDDLE_BAND:** partial two-tier signature (some HP fires but not all).

**CHAIN_GRADE_TWO_TIER_ZIPFIAN:** requires HP_TWO_TIER + HP_UNIFORM_ZIPFIAN_GAP + HP_BASELINE cross-seed (post-VET seed_7/13/19).

## Substrate-KB check

Rerun query. v1 report top hit cosine=0.3477 sub-threshold. v2 adds noise+overload — same substrate-KB status; no direct prior cited above 0.30 threshold. Distinct-from prior work still documented via v1 cross-reference.

## Discipline gates satisfied

- CARDINALITY_OK: EXPECTED_N_UNITS = 54 (verdict gates cardinality first).
- DISCRIMINATOR_SURVIVES_SCALE: smoke includes full-N=8192 preview at critical discriminator (α=1.0, σ=0.30, load=0.30). If BOTH Q1 AND Q4 >= 0.95 at preview, HALT + report HF_PREDICTION_FAILS.
- META_RULE_AG baseline_in_band: (α=0.0, σ=0.0, load=0.10) must satisfy recall >= 0.85 at FULL.
- META_RULE_AF arms_differ: 54 distinct signatures required.
- META_RULE_AH atomicity: metrics.json.tmp + os.replace.
- META_RULE_L strict-band: HP thresholds strict (>=) not floor.
- META_RULE_M calibration: adaptive_with_discriminator_gate (β = log2(M)/margin).
- META_RULE_AC number provenance: CRLB THEORETICAL@binomial-CLT (0.0158 all; 0.032 stratified); HP thresholds HYPOTHESIZED@Director_synthesis_from_D_RIP_drill; sparse-coding drill CITED@`notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`.
- Chunked architecture (§13): one seed per cell; start-marker + crash-diagnostic + heartbeat all inline.

## Scale
- N=8192; M in {819, 1638, 2458, 4096, 6554, 9830} across loads.
- alpha_simple in [0.10, 1.20]; spans Amit-Gutfreund wall (~0.138 Hebbian classical) and into Ramsauer exponential regime.
- Backend: numpy CPU.
- Route: **remote_cpu_queue** × 3 seeds.
- Timeout: 21600s per PROT-019 floor (single-seed chunked; each cell ~ minutes-tens-of-minutes expected wallclock).

## Queue
- Smoke: local_cpu_queue (USER 2026-07-01 rule).
- FULL: remote_cpu_queue × 3 (seed_7, seed_13, seed_19); route via hdi_orchestrator (harness-DENIED push).
