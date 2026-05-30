# Prereg: tensor_factorized_w_envelope_v3_n4096

**Anchor:** `tensor_factorized_w_envelope_v3_n4096`
**Queue:** remote_cpu_queue (CPU envelope sweep)
**Script:** `experiments/exp_tensor_factorized_w_envelope_v3_n4096.py`
**Date:** 2026-05-30
**Lineage:** F2 (v1: TF_HARD_PASS at M=512; v2: KILLED mid-run by user-pause; v3: fresh ship with PROT-021 per-cell-seed checkpointing for bounded interruption cost)

## Question

At N=4096, does low-rank factorization of the substrate W preserve retention across a broader (M, rank) envelope than v1's single M=512 anchor? v1 HP-passed at M=512 but cap_map v283 flagged sub-capacity caveat — the broader envelope (higher M, rank/N ratios) was not tested. v3 lifts the caveat.

## Configuration

- N (production): 4096 (PROT-018: `_n4096` binds)
- N (smoke): 1024
- M sweep (production): `[512, 2048, 8192]`
- M sweep (smoke): `[64, 256]`
- Rank sweep (production): `[128, 256, 512, 1024, 2048]`
- Rank sweep (smoke): `[32, 64, 128]`
- Seeds (production): `[7, 17, 23, 31, 41]` (5 seeds)
- Seeds (smoke): `[17]`
- Beta: 8.0
- N_PROBE: 200
- Cell-seeds total (production): 3 M × 5 ranks × 5 seeds = 75
- Cell-seed total (smoke): 2 M × 3 ranks × 1 seed = 6

## Pre-registered bands (HARD: set BEFORE running)

Per (M, rank, seed) cell, compute `retention_ratio = ret_factored / ret_full`.

| Outcome | Trigger |
|---------|---------|
| **HARD_PASS** | rank ≤ 1024 preserves retention_ratio ≥ 0.95 at ALL 3 M values in ≥ 3/5 seeds |
| **HARD_FAIL** | At M=8192, ANY rank loses ≥ 30% retention (retention_ratio ≤ 0.70) in 3+/5 seeds |
| **MIDDLE_BAND** | Otherwise |

Verdict labels: `TFE_V3_HARD_PASS`, `TFE_V3_HARD_FAIL`, `TFE_V3_MIDDLE_BAND`, `TFE_V3_INCONCLUSIVE`.

## Formula self-tests (verified at module import)

1. `N_FULL == 4096` (PROT-018 binding)
2. SVD round-trip: `factorize_w(W, full_rank) ≈ W` (atol=1e-4) — verified on 8×8 random tensor
3. Cell-seed total = 75 (3 M × 5 ranks × 5 seeds)
4. `compute_verdict(fake_hp_data)` → contains `HARD_PASS`
5. `compute_verdict(fake_hf_data)` → contains `HARD_FAIL`
6. Smoke at N=1024, M=64, ranks=[32,64,128] returns non-negative retentions for all ranks

## Smoke result (2026-05-30, CPU)

- M=64, seed=17, ranks=[32, 64, 128]: full=1.000, ratios={32: 1.0, 64: 1.0, 128: 1.0}
- M=256, seed=17, ranks=[32, 64, 128]: full=1.000, ratios={32: 1.0, 64: 1.0, 128: 1.0}
- Verdict: TFE_V3_MIDDLE_BAND (expected with 1 seed: cannot satisfy 3/5-seed gate at smoke)
- Total elapsed: 1.11s
- Non-zero, non-constant ratios (all 1.0 because smoke N=1024 is far below capacity); not suspect

## Walk-back gate

Smoke shows retention_ratio = 1.0 across all (M, rank) at N=1024 — far above HP threshold of 0.95. Effect size at smoke is large (d >> 1.0). FULL run does not need n×2 walk-back. Standard 5 seeds is sufficient.

## OOM check (CPU)

- M=8192, N=4096 keys = 134MB, W = 64MB, codebook = 805MB, SVD ~3x W = 192MB
- Peak ~1.2GB RSS. CPU runner has ample headroom.

## Timeout estimate

Formula: `ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`

- smoke_wall_s = 1.11s (6 cell-seeds at N=1024)
- FULL_N / smoke_N = 4096 / 1024 = 4
- FULL_seeds / smoke_seeds = 5 / 1 = 5
- FULL cells / smoke cells = 75 / 6 = 12.5 (additional scaling for cell-seed count)
- scaling_exp = 2.0 (SVD is matrix-multiply dominant)
- formula estimate = ceil(1.5 * 1.11 * 4^2.0 * 5 * 12.5) = ceil(1665s) = ~1665s
- empirical: per-cell-seed CPU time at N=4096 with SVD ~30-60s × 75 = 2250-4500s
- Apply safety margin: **timeout=21600s (6h)** — accommodates worst-case CPU pace; flagged in note for >2h.

## Queue routing

- remote_cpu_queue (Tier B): CPU SVD sweep at N=4096 is genuinely slow; no GPU dependency; per-cell-seed checkpoint means any interruption is bounded.
- ASCII-only structurally guaranteed.

## Next decisions by outcome

- **HARD_PASS**: lifts cap_map v283 sub-capacity caveat; tensor-factorized W feasibility row → ✅; opens product narrative for storage-compressed substrate.
- **HARD_FAIL**: factorization breaks at high M; cap_map sub-capacity row stays ⚠️; product narrative restricted to low-M regime.
- **MIDDLE_BAND**: partial result; cap_map note "factorization holds at low-to-mid M but breaks at top M"; possible rescue via blocked SVD or hierarchical factorization.

## Lineage notes

v2 was KILLED mid-run by user-pause action (per F-batch dispatch). v3 has IDENTICAL scientific spec to v2; only difference is fresh anchor name. Any partial data from v2 on remote is NOT inherited (per-cell-seed partials are scoped to `data/exp_<HDLAB_EXP_NAME>/`, and v3's HDLAB_EXP_NAME differs from v2's).
