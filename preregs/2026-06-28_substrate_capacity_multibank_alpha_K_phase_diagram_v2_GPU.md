# Prereg: substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU

**Date:** 2026-06-28
**Author:** exp_dev (sibling chunk cells: seeds 7, 13, 19)
**Cells:**
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7.py`
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_13.py`
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_19.py`
**Anchors (per seed):** `substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_<7|13|19>`

## v1 -> v2 chain-grade revival rationale

v1 landed 3-seed MIDDLE_BAND. Mechanism CONFIRMED across seeds 7/13/19
(n_pass=23 per seed, cardinality_ok=True, arms_differ 162/162, gpu_util_p50
range 38-98). Multi-bank advantage MASSIVE at B=16 (K=64 alpha=0.05 MULTI=1.000
vs SINGLE=0.139-0.151, ~7x absolute / ~85x relative at alpha=0.5).

**Why v1 stayed at MIDDLE_BAND:**
1. **n_pass_at_full_N = 5 / 162** (need >=8 for HARD_PASS). Discriminator-PASS
   region was concentrated at N<=4096 because K_per_bank capped at 64 — at
   N=8192 M scales up faster than K can absorb.
2. **rail_ok = False** at all 3 seeds: rail config was (alpha_min=0.05, K=64,
   B=1, N=8192) -> M=410 items in 64 slots in 1 bank => recall = 0.13-0.14.
   This is a BY-CONSTRUCTION saturation (M >> K_per_bank * B), not mechanism
   failure. Rail was anchored to a pre-K-extension regime.
3. **cliff_per_B narrow:** B=16 cliff_frac=0.5, B=4 cliff_frac=0.1, B=1
   cliff_frac=0 (collapsed). K_per_bank axis capped discriminator headroom.

**Skunkworks revival recommendations (3 options; this cell does (a) + (b)):**
- (a) Extend K_per_bank axis to >=128 — DONE: K_per_bank in {16, 64, 128, 256}.
- (b) Drop B=1 baseline arm (degenerate; MULTI ~ SINGLE) — DONE: B in {4, 16, 64}.
- (c) Lower HP threshold — NOT TAKEN; keep HP_MULTI_PASS_RECALL=0.50 per band-
  floor=MIDDLE_BAND-not-HARD_PASS discipline.

## v2 deltas explicit

| Axis | v1 values | v2 values | Why |
|------|----------|-----------|-----|
| K_per_bank | {4, 16, 64} | {16, 64, 128, 256} | K=4 saturates everywhere (M>>K immediately); K=128, K=256 add resolution headroom |
| num_banks B | {1, 4, 16} | {4, 16, 64} | B=1 is degenerate (MULTI~SINGLE); B=64 adds discrimination orthogonality |
| alpha | {0.05, 0.10, 0.25, 0.50, 1.0, 2.0} | UNCHANGED | brackets cliffs cleanly |
| N_DIM | {2048, 4096, 8192} | UNCHANGED | GPU-eligible band |
| HP_HARD_PASS_MIN_GRID | 30 | 50 | n_pass scales 23*216/162=31 baseline + K=128/256 expansion ~20+ more passes |
| HP_HARD_PASS_MIN_FULLN | 8 | 12 | chain-grade threshold per spawn brief |
| HP_DISCRIM_DOES_NOT_FIRE | 15 | 20 | raised proportionally with grid size |
| Rail config | (alpha_min, K=64, B=1, N=FULL_N) | (alpha_min, K=256, B=4, N=FULL_N) | M=410, M/B=102 in K=256 -> clean resolution (predicted ~1.0) |

## Scientific question (unchanged from v1)

Sweep alpha (loading factor) x K_per_bank x num_banks x N at FIXED codebook
size CB=16384. Mechanism: each bank stores K_per_bank slot-tags; total M =
round(alpha * N) items distributed across B banks; each bank gets ~M/B items;
multiple items per slot overflow into shared slot.

**Theoretical prediction (unchanged):** at fixed K_per_bank, total bank capacity
= K_per_bank * B slots. Cliff at M > K_per_bank * B (every slot overflows).
Multi-bank advantage: distributing M across B banks means each bank handles
M/B items; if M/B <= K_per_bank, multi-bank fully resolved while single-bank
(all M in one slot-set of size K_per_bank) cliffs at much lower alpha.
alpha_cliff(B) = K_per_bank * B / N.

## Sweep axes (full grid)

- **alpha (loading factor, PRIMARY):** {0.05, 0.10, 0.25, 0.50, 1.0, 2.0} -- 6 pts
- **K_per_bank (SECONDARY):** {16, 64, 128, 256} -- 4 pts (v1 was 3 pts {4,16,64})
- **N (TERTIARY):** {2048, 4096, 8192} -- 3 pts
- **B (num_banks, QUATERNARY):** {4, 16, 64} -- 3 pts (v1 was 3 pts {1,4,16})

Full grid per seed: 6 x 4 x 3 x 3 = **216 points**. M_max = round(2.0 * 8192)
= 16384 = CB; no skips. Arms per point: 3 (MULTI_BANK_BIND, SINGLE_BANK_BASELINE,
RANDOM_FLOOR). **EXPECTED_N_UNITS per seed (full) = 648 units** (v1 was 486).

## Smoke corners (per seed, 8 corners x 3 arms = 24 units)

Includes **2 full-N=8192 preview corners** per discriminator-must-survive-scale
(USER 2026-06-26 Option C). Local CPU smoke may be slow on N=8192 K=256 — use
HDLAB_SMOKE_TIMEOUT_S override if gate timeout breached (default 180s, ceiling
3600s).

| alpha | K_per_bank | B | N    | M     | M/B  | role                                                        |
| ----- | ---------- | - | ---- | ----- | ---- | ----------------------------------------------------------- |
| 0.05  | 16         | 16| 2048 | 102   | 6    | DISCRIM-low: M/B=6<<K=16 -> MULTI ~1.0; SINGLE M=102/K=16 collapse |
| 0.05  | 64         | 4 | 2048 | 102   | 26   | DISCRIM: M/B=26<K=64 -> MULTI clean; SINGLE struggle             |
| 0.05  | 128        | 4 | 4096 | 205   | 52   | DISCRIM: M/B=52<K=128 -> MULTI clean; SINGLE struggle            |
| 0.05  | 256        | 4 | 8192 | 410   | 103  | FULL-N RAIL PREVIEW: M/B=103<K=256 -> MULTI ~1.0 (predicts rail_ok) |
| 0.10  | 256        | 4 | 8192 | 819   | 205  | FULL-N DISCRIM: M/B=205<K=256 -> MULTI marginal; SINGLE collapse |
| 0.25  | 64         | 16| 2048 | 512   | 32   | DISCRIM: M/B=32<K=64 -> MULTI clean; SINGLE collapse             |
| 0.50  | 128        | 64| 2048 | 1024  | 16   | DISCRIM: M/B=16<<K=128 -> MULTI clean; SINGLE collapse           |
| 2.0   | 16         | 16| 2048 | 4096  | 256  | FLOOR sanity: M/B=256>>K=16 -> BOTH collapse (overload floor)    |

**Smoke discriminator FIRES if:**
- at least 4 of 6 discriminator-firing corners show MULTI - SINGLE > 0.30, AND
- at least 1 of 2 full-N=8192 corners fires (discriminator-must-survive-scale)
**Smoke rail preview:** alpha=0.05, K=256, B=4, N=8192 MULTI recall >= 0.85.
**Smoke floor check:** at least 1 corner shows both arms at floor (alpha=2.0
K=16 B=16).
**Smoke arms-differ check:** META_RULE_AF on all 24 units.

## CRLB pre-validation (v2 regimes)

Cleanup-1 SNR per dim: `1 / sqrt(items_per_bank - 1)`.
- items_per_bank=6 (K=16 alpha=0.05 B=16): SNR_dim = 0.447 (clean)
- items_per_bank=26 (K=64 alpha=0.05 B=4): SNR_dim = 0.200 (clean)
- items_per_bank=52 (K=128 alpha=0.05 B=4): SNR_dim = 0.140 (clean)
- items_per_bank=103 (K=256 alpha=0.05 B=4): SNR_dim = 0.099 (marginal)
- items_per_bank=205 (K=256 alpha=0.10 B=4): SNR_dim = 0.070 (cliff regime)
- items_per_bank=256 (K=16 alpha=2.0 B=16): SNR_dim = 0.063 (cliff floor)

Bank-routing SNR (CUE_COS=0.70): `0.70 * sqrt(N) / sqrt(B)`. At v2 worst
(N=2048, B=64): 0.70 * sqrt(2048) / sqrt(64) = 3.96 — still routable; lower
than v1 worst (B=16 -> 14) but bank-route accuracy stays acceptable per
T8 selftest validation.

## VRAM pre-validation

Estimated eval peak (fp16, CB=16384):
- Worst v2 point N=8192, K=256, B=64, M=16384: ~3.7 GB
- All 216 points fit within 12 GB GPU budget; HP_VRAM_PROBE_FRACTION=0.85
  safety belt.

## PASS bands (HARD_PASS, per seed)

**HARD_PASS:** MULTI - SINGLE > 0.30 at >= 50 of 216 grid points, AND:
- discriminator_survives_scale: >= 12 of the 50 PASS points at N=8192 (full scale)
- corridor saturation: alpha=0.05 / K=256 / B=4 / N=8192 MULTI >= 0.95 (rail)
- arms_differ_sha256 distinct at all 216 points; RANDOM hash distinct everywhere
- cliff observable: cliff_per_B reports monotone alpha_cliff(B) increasing with B at fixed (K, N)

## MIDDLE_BAND

- MULTI - SINGLE > 0.30 at 20-49 grid points (partial coverage), OR
- n_pass >= 50 but n_pass_at_full_N < 12 (full-N discriminator fails), OR
- rail_recall < 0.95 (rail still saturates -> mechanism scale-limited)

## HARD_FAIL bands

- `HARD_FAIL_CARDINALITY_BREACH` (META_RULE_H): observed != EXPECTED_N_UNITS (smoke=24; full=648).
- `HARD_FAIL_UNIT_EXCEPTION` (META_RULE_AN): any unit raises; no silent except.
- `HARD_FAIL_GPU_MEMORY_OOM`: real CUDA OOM (NOT probe denial).
- `HARD_FAIL_ARMS_IDENTICAL` (META_RULE_AF): MULTI/SINGLE/RANDOM identical hash.
- `HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE`: < 20 of 216 points with margin > 0.30.
- `HARD_FAIL_SATURATION_ONLY`: every point at MULTI >= 0.995.
- `HARD_FAIL_FLOOR_ONLY`: every point at MULTI <= RANDOM + 0.05.
- `HARD_FAIL_LLM_CALL`: substrate-only gate broken.
- `HARD_FAIL_GPU_UNDERUTIL` (Fix #24, FULL only; SKUNKWORKS audit): gpu_util_p50 < 0.50.

## Smoke gate (must pass BEFORE full dispatch)

1. All 8 corners run; cardinality_ok=True; n_units=24.
2. >= 4 of 6 discriminator-firing corners show margin > 0.30.
3. >= 1 of 2 full-N=8192 corners fires (discriminator-must-survive-scale).
4. Rail preview: alpha=0.05 K=256 B=4 N=8192 MULTI >= 0.85.
5. >= 1 corner shows floor (overload).
6. arms_differ_sha256 distinct at all 8 phase points.
7. GPU util p50 >= 50% gate DEFERRED to remote GPU smoke; local CPU smoke skips.

## Disciplines (load-bearing)

- META_RULE_AE: pre-reg bands LOCKED at module init.
- META_RULE_AF: arms must differ across all (MULTI/SINGLE/RANDOM) at every point.
- META_RULE_AG: corpus_provenance + allow_synthetic recorded in metrics.
- META_RULE_AH: atomic-write partials via _seed_checkpoint.
- META_RULE_AN: no silent except; record + halt OR re-raise.
- META_RULE_H: CARDINALITY_OK field; HARD_FAIL_CARDINALITY_BREACH on mismatch.
- Discriminator-must-survive-scale (USER 2026-06-26): smoke includes 2 full-N
  preview corners; FULL requires >=12 of 50 PASS at N=8192.
- Smoke fires discriminator (three-smoke-disciplines #2).
- Band-floor MIDDLE_BAND not HARD_PASS (three-smoke-disciplines #3).
- Fix #24 GPU mandate at FULL.
- PROT-018: anchor has no _n<N> suffix (capability-test sibling chunk).
- PROT-019: timeout floors don't apply (no _n<N> suffix in anchor).
- PROT-020: cells import torch (GPU queue routing justified).
- PROT-021: cells import _seed_checkpoint (checkpointed partial writes).

## CARDINALITY_OK (META_RULE_H discipline)

- Smoke EXPECTED_N_UNITS = 1 seed * 8 phase_points * 3 regimes = **24**
- Full EXPECTED_N_UNITS = 1 seed * 216 phase_points * 3 regimes = **648**
- HARD_FAIL_CARDINALITY_BREACH triggered if (n_units + n_probe_cliffs) < expected

## Functional-requirement decomposition

- F1 mechanism end-to-end: 8 smoke corners all run (cardinality_ok=True).
- F2 discriminator: MULTI > SINGLE > RANDOM at >=4 expected-cliff corners + >=1 full-N corner.
- F3 cliff observable: at least 1 saturation + 1 floor corner.
- F4 substrate-only: `_LLM_CALL_COUNTER[0] == 0`.
- F5 GPU utilization (FULL only): gpu_util_p50 >= 50%; DEFERRED to remote-GPU smoke.
- F6 phase-coherence: in full, alpha_cliff(B) monotone in B at fixed K.
- F7 rail validation: alpha=0.05 K=256 B=4 N=8192 MULTI >= 0.95.

## Output schema (`metrics.json`)

- `per_unit`: `{seed, alpha, K_per_bank, num_banks, N_DIM, M_total, items_per_bank, regime, recall, route_acc, arm_sha256, peak_mem_mb, wall_s, ...}`.
- `phase_map`: per (alpha, K, B, N) tuple with multi/single/random recall and margin.
- `headline`: `n_pass`, `n_pass_at_full_N`, `cliff_per_B`, `rail_alpha_min_K256_B4_fullN_observed`.

## Dispatch plan

- **Smoke (this cell):** CPU local for seed_7 (N=2048..8192; 8 corners; 24 units);
  HDLAB_SMOKE_TIMEOUT_S=1800 if 180s default insufficient. Local has no CUDA;
  smoke verifies mechanism FIRES at small N + 2 full-N preview corners.
- **Full (3 sibling cells, each 1 seed x 216 points x 3 arms = 648 units):**
  dispatch via Orchestrator to `overnight_queue` GPU. Per-seed timeout estimate:
  v1 wall ~80s on GPU at 162 pts -> v2 at 216 pts with K=256 (more matmul) =
  ~150-200s pure compute. Add overhead + safety margin -> **timeout 1800s/seed**
  (well below PROT-019 14400s _n>=4096 floor; anchor has no _n<N> suffix so no
  PROT-019 trigger).
- GPU expected free for this work (queue depth verified by Orchestrator pre-dispatch).

## Promotion criteria

If 3-seed envelope HARD_PASS:
- Promotes Capacity multi-bank chain-grade phase-diagram CONTINUOUS (was MM v1).
- Adds atoms: alpha-cliff scaling alpha_cliff(B) ~ K_per_bank * B / N validated
  across 4 K x 3 B x 3 N grid.
- Cross-references: chain-grade WM K-cliff v3 (commit 7274bafb); chain-grade
  capacity v2c rail; v1 MM (this is its chain-grade revival).

If 3-seed envelope MIDDLE_BAND:
- Skunkworks audits per-arm to identify regime-of-failure: (i) discriminator
  fails at full-N -> mechanism scale-limited; (ii) rail fails -> M/B too high
  for K=256 -> need K_per_bank=512+; (iii) bank-routing breakdown at B=64 with
  small N -> need higher N floor.
