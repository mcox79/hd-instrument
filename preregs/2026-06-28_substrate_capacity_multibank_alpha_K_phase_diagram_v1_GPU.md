# Prereg: substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU

**Date:** 2026-06-28
**Author:** exp_dev (sibling chunk cells: seeds 7, 13, 19)
**Cells:**
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_7.py`
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_13.py`
- `experiments/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_19.py`
**Anchors (per seed):** `substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_<7|13|19>`

## Scientific question

WM K-cliff v3 (chain-grade, commit 7274bafb) characterized the K_per_bank x num_banks x N axes at the FIXED loading regime where items_per_bank == K_per_bank (i.e. each bank fully utilized, M = K_per_bank * B).

Capacity multi-bank alpha=4 K=4 reference cell (`exp_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu`) is chain-grade at ONE phase point (alpha_N=4.0, K=4) at N=8192.

**v1 alpha-K phase diagram (this cell)** fills the gap by sweeping the LOADING axis alpha (item density = M / N) across multi-bank configs at SMALL K_per_bank (slot count per bank). Mechanism: each bank stores K_per_bank slots (slot tags); total M = round(alpha * N) items distributed across B banks; each bank gets ~M/B items; multiple items per slot overflow into shared slot.

Phase coverage status (BACKUP UPDATE #25): Capacity multi-bank alpha=4 K=4 is CHAIN-GRADE at 70% completeness with phase coverage MID (one alpha point at one K point). This cell extends MID -> HIGH by mapping the (alpha, K_per_bank, B, N) phase manifold across the cliff structure.

**Theoretical prediction:** at fixed K_per_bank, total bank capacity = K_per_bank * B slots. Cliff at M > K_per_bank * B (every slot overflows). Multi-bank advantage: distributing M across B banks means each bank handles M/B items; if M/B <= K_per_bank, multi-bank fully resolved while single-bank (all M in one slot-set of size K_per_bank) cliffs at much lower alpha. Cliff per B: alpha_cliff(B) = K_per_bank * B / N.

## Sweep axes (full grid)

- **alpha (loading factor, PRIMARY):** {0.05, 0.10, 0.25, 0.50, 1.0, 2.0} - 6 points - brackets above/below predicted cliffs
- **K_per_bank (SECONDARY, slot count per bank):** {4, 16, 64} - 3 points - fixed-small bank size sweep
- **N (TERTIARY, substrate dim):** {2048, 4096, 8192} - 3 points - GPU-eligible
- **B (num_banks, QUATERNARY):** {1, 4, 16} - 3 points - orthogonal axis

Full grid per seed: 6 x 3 x 3 x 3 = **162 points**. Skip cells where M = round(alpha*N) > CODEBOOK_SIZE=16384 (M_max at alpha=2, N=8192 is 16384, fits exactly). No skips.

Arms per point: 3 (MULTI_BANK_BIND, SINGLE_BANK_BASELINE, RANDOM_FLOOR). **EXPECTED_N_UNITS per seed (full) = 486 units.**

## Smoke corners (per seed, CPU)

6 corner points x 3 arms = 18 units. Calibrated for CPU runtime < 60s.

| alpha | K_per_bank | B | N    | M    | items_per_bank (M/B) | role / predicted                                                                |
| ----- | ---------- | - | ---- | ---- | -------------------- | ------------------------------------------------------------------------------- |
| 0.05  | 4          | 1 | 2048 | 102  | 102                  | SINGLE-CLIFF: M >> K_per_bank=4 in 1 bank -> SINGLE collapses; MULTI same (B=1) |
| 0.05  | 4          | 16| 2048 | 102  | 6                    | DISCRIMINATOR FIRES: M/B=6 ~ K_per_bank=4 -> MULTI resolves, SINGLE collapses   |
| 0.05  | 16         | 4 | 2048 | 102  | 26                   | DISCRIMINATOR FIRES: MULTI better than SINGLE                                   |
| 0.10  | 16         | 4 | 4096 | 410  | 103                  | MID regime: M/B=103 >> K=16; both arms struggle                                 |
| 0.05  | 64         | 1 | 4096 | 205  | 205                  | DISCRIMINATOR FIRES at K=64: MULTI vs SINGLE both store M=205, B=1 collapse     |
| 0.50  | 4          | 16| 2048 | 1024 | 64                   | FLOOR: M/B=64 >> K=4 -> both cliff (sanity floor)                               |

**Smoke discriminator FIRES if:** at least 2 of 4 discriminator-firing corners show MULTI - SINGLE > 0.30.
**Smoke saturation check:** at least 1 corner shows MULTI >= 0.40 (low-load resolved).
**Smoke floor check:** at least 1 corner shows both arms at floor (overload sanity).

## CRLB pre-validation

Cleanup-1 SNR per dim: `1 / sqrt(items_per_bank - 1)`.
- items_per_bank=4:   SNR_dim = 0.577 (high; bank resolves easily)
- items_per_bank=16:  SNR_dim = 0.258
- items_per_bank=64:  SNR_dim = 0.126
- items_per_bank=205: SNR_dim = 0.070
- items_per_bank=1024: SNR_dim = 0.031 (cliff regime)

At items_per_bank=4 with K_per_bank=4 slots, every slot has exactly 1 item -> recall ~1.0.
At items_per_bank=64 with K_per_bank=4 slots, each slot has 16 items binding -> heavy interference.

Bank-routing SNR (CUE_COS=0.70): `0.70 * sqrt(N) / sqrt(B)` - healthy at all sweep points (>=14 at N=2048,B=16).

## VRAM pre-validation

Estimated eval peak (fp16, CB=16384):
- Worst point N=8192, K=64, B=16, M=16384: ~3.2 GB
- All 162 points fit within 12 GB GPU budget; HP_VRAM_PROBE_FRACTION=0.85 safety belt.

## PASS bands (HARD_PASS, per seed)

**HARD_PASS:** MULTI - SINGLE > 0.30 at >= 30 of 162 grid points, AND:
- discriminator_survives_scale: >= 8 of the 30 PASS points at N=8192 (full scale)
- corridor saturation: alpha=0.05 / K=64 / B=1 / N=8192 MULTI >= 0.95 (low-load rail)
- arms_differ_sha256 distinct at all B>=2 points; RANDOM hash distinct everywhere
- cliff observable: cliff_per_B reports monotone alpha_cliff(B) increasing with B at fixed (K, N)

## MIDDLE_BAND

- MULTI - SINGLE > 0.30 at 15-29 grid points (partial coverage), OR
- Cliff structure coherent (monotone in alpha) but absolute MULTI recall in [0.30, 0.50)

## HARD_FAIL bands

- `HARD_FAIL_CARDINALITY_BREACH` (META_RULE_H): observed != EXPECTED_N_UNITS (smoke=18; full=486).
- `HARD_FAIL_UNIT_EXCEPTION` (META_RULE_AN): any unit raises; no silent except.
- `HARD_FAIL_GPU_MEMORY_OOM`: real CUDA OOM (NOT probe denial).
- `HARD_FAIL_ARMS_IDENTICAL` (META_RULE_AF): at B>=2, MULTI and SINGLE arms have identical sha256.
- `HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE`: < 15 of 162 points with margin > 0.30.
- `HARD_FAIL_SATURATION_ONLY`: every point at MULTI >= 0.995.
- `HARD_FAIL_FLOOR_ONLY`: every point at MULTI <= RANDOM + 0.05.
- `HARD_FAIL_LLM_CALL`: substrate-only gate broken.
- `HARD_FAIL_GPU_UNDERUTIL` (Fix #24, FULL only): gpu_util_p50 < 0.50.

## Smoke gate (must pass BEFORE full dispatch)

1. All 6 corners run; cardinality_ok=True; n_units=18.
2. >= 2 of 4 discriminator-firing corners show margin > 0.30.
3. >= 1 corner saturates (MULTI >= 0.40 at low-load).
4. >= 1 corner shows floor (overload).
5. arms_differ_sha256 distinct at B>=2; RANDOM distinct everywhere.
6. GPU util p50 >= 50% gate DEFERRED to remote GPU smoke; local CPU smoke skips.

## Disciplines (load-bearing)

- META_RULE_AE: pre-reg bands LOCKED at module init.
- META_RULE_AF: arms must differ (B>=2 case).
- META_RULE_AG: corpus_provenance + allow_synthetic recorded in metrics.
- META_RULE_AH: atomic-write partials via _seed_checkpoint.
- META_RULE_AN: no silent except; record + halt OR re-raise.
- META_RULE_H: CARDINALITY_OK field; HARD_FAIL_CARDINALITY_BREACH on mismatch.
- Discriminator-must-survive-scale (USER 2026-06-26): smoke 6 corners + FULL requires >=8 of 30 PASS at N=8192.
- Smoke fires discriminator (three-smoke-disciplines #2).
- Band-floor MIDDLE_BAND not HARD_PASS (three-smoke-disciplines #3).
- Fix #24 GPU mandate at FULL.

## Functional-requirement decomposition

- F1 mechanism end-to-end: 6 smoke corners all run (cardinality_ok=True).
- F2 discriminator: MULTI > SINGLE > RANDOM at >=2 expected-cliff corners.
- F3 cliff observable: at least 1 saturation + 1 floor corner.
- F4 substrate-only: `_LLM_CALL_COUNTER[0] == 0`.
- F5 GPU utilization (FULL only): gpu_util_p50 >= 50%; DEFERRED to remote-GPU smoke.
- F6 phase-coherence: in full, alpha_cliff(B) monotone in B at fixed K.

## Output schema (`metrics.json`)

- `per_unit`: `{seed, alpha, K_per_bank, num_banks, N_DIM, M_total, items_per_bank, regime, recall, route_acc, arm_sha256, peak_mem_mb, wall_s, ...}`.
- `phase_map`: per (alpha, K, B, N) tuple with multi/single/random recall and margin.
- `headline`: `n_pass`, `n_pass_at_full_N`, `cliff_per_B` (per-B critical alpha).

## Dispatch plan

- **Smoke:** CPU local (N=2048; 6 corners; 18 units); seed_7 only; timeout 600s. Local has no CUDA; smoke verifies mechanism FIRES at small N.
- **Full (3 sibling cells, each 1 seed x 162 points x 3 arms = 486 units):** dispatch via Orchestrator to `overnight_queue` GPU. Per-seed timeout 14400s (4h; 162 points avg ~50s).
- GPU is currently IDLE (cortex_hippo / WM v3 / PC v2.2 completed); ready for this cell.

## Promotion criteria

If 3-seed envelope HARD_PASS:
- Promotes Capacity multi-bank alpha=4 K=4 phase coverage MID -> HIGH (per BACKUP UPDATE #25).
- Adds atoms: alpha-cliff scaling alpha_cliff(B) ~ K_per_bank * B / N for fixed bank-slot count.
- Cross-references: chain-grade WM K-cliff v3 (commit 7274bafb); chain-grade capacity v2c rail.
