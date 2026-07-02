# Pre-reg: hrr_depth_budget_curve_v2_gpu_batched (A2 scope; GPU-batched refactor of v1)

Date: 2026-07-02
Author: hdi_orchestrator (Director-authored follow-up per USER-locked GPU-batching discipline)
Cell: `experiments/exp_hrr_depth_budget_curve_v2_gpu_batched.py`
Anchor: `hrr_depth_budget_curve_v2_gpu_batched`
Queue: `overnight_queue` (GPU-heavy at 168-phase-point tensor)
Timeout: 3600s (10x safety margin over 30-minute estimate)

## Compute architecture

**Class: batched-GPU (default for grids per USER discipline 2026-07-02).**

All 168 phase points × 3 seeds × TR=200 trials are executed on `torch.cuda`.
Substrate primitives (bind = elementwise mul, bundle = sum, cleanup = matmul +
argmax) are trivially data-parallel across the trial axis. Per-cell memory
budget bounded to 2 GB (chunked trials when k×M×N×4 bytes exceeds).

## Predecessor

Follow-up to v1 (`hrr_depth_budget_curve_v1`) which was numpy-sequential.
v1 ran ~8h44m before USER-authorized kill at cell 167/504 (33% grid coverage,
seed_7 only). Salvage: `data/exp_hrr_depth_budget_curve_v1/partial_metrics.json`.

## Motivation

Same as v1: close 2026-06-23 research drill open item (HRR capacity-vs-depth
budget envelope) with Director's A2 scope directive — probe the
Frady-Sommer M_max crossover / Donoho-Tanner phase boundary at (V=1000, M=256).

v2 exists solely to unblock the pipeline: v1's sequential CPU compute was
36+ hrs for a payload that vectorizes to ~30 min on GPU. Wall-time waste of
this magnitude on a repeatable primitive is a USER-locked discipline breach.

## Grid (identical to v1)

- N_DIM = 8192
- V_CLEANUP ∈ {100, 1000}
  - M_max(V=100)  = 8192 / (4·ln 100)  ≈ 444.7
  - M_max(V=1000) = 8192 / (4·ln 1000) ≈ 296.4
- BIND_VARIANTS = {ELEM_BIPOLAR, FHRR_CC}
- CLEANUP ∈ {OFF, ON}
- Cheap tier: k ∈ {1, 5, 10, 15, 20} × M ∈ {1, 5, 16}
- Expensive tier: k ∈ {1, 10, 20} × M ∈ {64, 256}
- Cells per seed = 168
- SEEDS ∈ {7, 13, 19}
- **CARDINALITY_OK gate: 504 units expected (hard-fail if breach).**

Grid enumeration order matches v1._grid_cells() exactly — per-arm outputs
align 1:1 for direct comparison with v1 seed_7 salvage.

## Mechanism (same as v1, batched over trials)

Per trial (batched B trials in parallel on GPU):
1. Build per-trial V-book of atoms + (k, M, N) slot_roles.
2. Target atom index t drawn uniformly.
3. Layer l: slot 0 = bind(role[l, 0], prev_state); slots 1..M-1 = bind(role[l, m], distractor).
4. Bundle M slots via linear sum (bipolar) or sum+renorm (FHRR).
5. If cleanup=ON and M>1: preserve slot-0 contribution, unbind each m≥1 slot
   from bundle, argmax-cleanup to nearest book row, rebundle.
6. Unwind: reverse layer order, apply unbind(state, slot_roles[l, 0]).
7. Final argmax cleanup against V-book. hit ↔ argmax == t.

**Distractor sampling parity note:** v1 uses numpy.choice with `replace=True`
when M-1 > V-1. v2 uses `torch.randint(0..V)` with target-collision reroll (up
to 4 passes; residual mismatch mass ~ 1/V⁴ ≪ 1). Semantics are equivalent.

## Pre-reg discriminator bands (identical to v1)

### Positive controls (must fire)
- **HP_INVOLUTIVE**: recall(ELEM_BIPOLAR, V=100, k=20, M=1, OFF) ≥ **0.99**
- **HP_CEILING_SAFE**: recall(ELEM_BIPOLAR, V=100, k=20, M=16, ON) ≥ **0.95**, cv ≤ 0.05

### A2 Donoho-Tanner wall probe
- **HP_CLEANUP_GAP_WALL**: recall(V=1000, k=10, M=256, ON) − recall(V=1000, k=10, M=256, OFF) ≥ **0.20**

### HARD_FAIL
- HF_INVOLUTIVE_BROKEN: recall(V=100, k=20, M=1, OFF) ≤ 0.95
- HF_SAFE_REGIME_COLLAPSE: recall(V=100, k=10, M=5, ON) ≤ 0.70
- CARDINALITY_BREACH: observed_n_units ≠ 504

## v1 reproduction ship-critical self-test

`test_v1_reproduction` runs 6 salvage-covered arms at seed=7 with TR=50 and
compares against v1 log-recovered recalls:

- (ELEM_BIPOLAR, V=100, k=20, M=1, OFF)  — involutive baseline
- (ELEM_BIPOLAR, V=100, k=20, M=16, ON)  — safe-regime ceiling
- (ELEM_BIPOLAR, V=100, k=10, M=5, ON)   — base regime health
- (ELEM_BIPOLAR, V=1000, k=10, M=256, ON)  — wall cleanup
- (ELEM_BIPOLAR, V=1000, k=10, M=256, OFF) — wall no-cleanup
- (FHRR_CC, V=100, k=20, M=1, OFF)       — FHRR involutive

**Tolerance:** cliff regions (v1 recall ≤ 0.05 or ≥ 0.95) tolerance 0.05;
mid-band regions tolerance 0.20 (SEM at TR=50 is 1/√50 ≈ 0.14; 0.20 covers
1.4× SEM).

**RNG parity note:** v1 uses numpy PRNG; v2 uses torch.Generator. Streams
differ → per-arm recalls will NOT be bit-exact. Cliff-location agreement
(k-M plane cliff geometry) is the actual ship-critical property, not identical
Monte-Carlo estimates. Self-test emits per-arm gap + tolerance without gating
the cell (mismatches noted; do not hard-fail).

## Timing budget

Approx per-cell cost on GPU (RTX-class):
- Small phase points (M≤16, V=100): ~0.05s/cell
- Cheap V=1000: ~0.15s/cell
- Expensive M=64, V=1000: ~0.3s/cell
- Expensive M=256, V=1000, cleanup ON, k=20: ~1s/cell (M-slot unbind loop)

Full estimate per seed: 168 cells averaging 0.3s = ~50s/seed. 3 seeds ~2.5 min.
Practical wall (kernel launch overhead + Python-loop overhead + chunk memory):
~10-30 min for 3-seed FULL.

**Timeout: 3600s** (10× safety margin).

## Cross-references

- `experiments/exp_hrr_depth_budget_curve_v1.py` (mechanism reference)
- `data/exp_hrr_depth_budget_curve_v1/partial_metrics.json` (salvage source, 167 arms seed_7)
- `preregs/2026-07-01_hrr_depth_budget_curve_v1.md` (v1 pre-reg)
- `memory/feedback_gpu_batching_mandatory_when_speedup_available_USER_LOCKED_2026-07-02.md` (discipline root)
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md`
- `notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`

## Substantive answer this cell provides

Same as v1: whether substrate HRR bind + bundle + per-layer cleanup can host
grammatical composition at k=10-20 depths in the noise regime (V=1000+ vocab,
M=256+ bundle width). Additionally: **wall-time proof of the batched-GPU
discipline** — same 504-arm grid, ~30 min vs 36 hrs on numpy.

## Discipline observed

- Compute architecture: batched-GPU declared in cell + this pre-reg (mandatory per USER 2026-07-02)
- CARDINALITY_OK: 504 units (identical to v1)
- DISCRIMINATOR_SURVIVES_SCALE: smoke uses same N=8192 as full; TR reduced
- No silent except (cell-level exceptions re-raised with variant/k/M/V/cleanup context)
- Regime-aware verdict logic (identical to v1)
- v1 reproduction self-test with SEM-aware tolerance
- Memory-chunked per-cell tensor build (bounded to 2 GB per chunk)
