# Pre-reg: hrr_depth_budget_curve_v1 (A2 scope; Frady-Sommer M_max crossover / Donoho-Tanner probe)

Date: 2026-07-01
Author: exp_dev
Cell: `experiments/exp_hrr_depth_budget_curve_v1.py`
Anchor: `hrr_depth_budget_curve_v1`
Queue: `remote_cpu_queue` (timeout 43200s = 12h)

## Motivation

Closes 2026-06-23 research drill open item (HRR capacity-vs-depth budget envelope) with
Director's A2 scope directive (2026-07-01): extend beyond the M ≤ 16 ceiling regime
found in A1 smoke into the genuine noise regime by pushing M_bundle to the
Frady-Sommer M_max = N/(4·log V) crossover.

The M-bundle superposition in HRR is structurally equivalent to K-sparse L1-recovery
under Donoho-Tanner phase boundary at K/M ≈ 0.20 ± 0.03 with M/N ≈ 0.14
(`notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`).
Per-layer cleanup is the AMP-analog denoiser. This cell probes whether that analogy
holds empirically on the substrate.

## Grid (TWO_TIER; A2 scope)

- N_DIM = 8192
- V_CLEANUP ∈ {100, 1000}
  - M_max(V=100)  = 8192 / (4·ln 100)  ≈ **444.7**
  - M_max(V=1000) = 8192 / (4·ln 1000) ≈ **296.4**
- BIND_VARIANTS = {ELEM_BIPOLAR, FHRR_CC}
- CLEANUP ∈ {OFF, ON}
- Cheap tier: k ∈ {1, 5, 10, 15, 20} × M ∈ {1, 5, 16}   (well below M_max both V)
- Expensive tier: k ∈ {1, 10, 20} × M ∈ {64, 256}       (mid-fraction to wall)
- Cells per (V, variant, cleanup) = 5·3 + 3·2 = 21
- Cells per seed = 21 · 2 · 2 · 2 = **168**
- SEEDS ∈ {7, 13, 19}
- Total units = **504** (CARDINALITY_OK gate: hard-fail if breach)

## Mechanism (per m4_nested distinct-slot-role precedent; validated A1 smoke)

Per layer l:
1. Build M_bundle distinct `slot_roles[l, m]` role vectors (bipolar or FHRR complex).
2. Slot 0 wraps chain-continuation: `bind(slot_roles[l, 0], prev_state)`.
3. Slots 1..M-1 wrap distractor atoms drawn from V-book (distinct from target).
4. Bundle all M slots via linear sum (bipolar sum-then-cleanup-later; FHRR sum+renorm).
5. If `cleanup=ON` and M>1: preserve slot-0 (nested state), unbind each slot m≥1 by
   its `slot_roles[l, m]`, argmax against V-book to snap atom-component to nearest
   codebook row, rebundle. Complexity O((M-1)·V·N) per layer.
   If M=1: no-op (nothing to denoise on pure chain).
6. Unwind: reverse layer order, apply `unbind(state, slot_roles[l, 0])`.
7. Final argmax cleanup against V-book. Correct iff argmax == target.

## Pre-reg discriminator bands (regime-aware per Director A2 directive)

### Positive controls (must fire)

- **HP_INVOLUTIVE**: recall@1(ELEM_BIPOLAR, V=100, k=20, M=1, OFF) ≥ **0.99**
  - Validates drill's involutive-bind prediction; must hold for cell mechanism to be sound.
- **HP_CEILING_SAFE**: recall@1(ELEM_BIPOLAR, V=100, k=20, M=16, ON) ≥ **0.95**, cv ≤ 0.05
  - Below-wall regime holds; A1 already showed 1.000 (this is a stability check).

### A2 novel discriminator (Donoho-Tanner wall probe)

- **HP_CLEANUP_GAP_WALL**: recall@1(ELEM_BIPOLAR, V=1000, k=10, M=256, ON)
   − recall@1(ELEM_BIPOLAR, V=1000, k=10, M=256, OFF) ≥ **0.20**
  - M=256 sits at 0.86·M_max(V=1000); AMP-analog denoiser should provide substantial lift.

### Secondary (reported, not gating)

- shallow_wide_lift: recall@1(V=1000, k=1, M=256, ON) − recall@1(V=1000, k=20, M=16, ON) ≥ 0.10
- wall_gap_k20: same probe at k=20 (deep-chain behavior at wall)
- FHRR_CC comparison at V=100 involutive + V=1000 wall (Plate CC norm-decay confirmation)

### HARD_FAIL

- **HF_INVOLUTIVE_BROKEN**: recall@1(ELEM_BIPOLAR, V=100, k=20, M=1, OFF) ≤ **0.95**
  → implementation bug / sign-quantize collision.
- **HF_SAFE_REGIME_COLLAPSE**: recall@1(ELEM_BIPOLAR, V=100, k=10, M=5, ON) ≤ **0.70**
  → base regime broken; below-wall should hold.
- **CARDINALITY_BREACH**: observed_n_units ≠ 504.

### Regime-aware exclusions

- Cleanup-gap discriminator applies **only at M ≥ M_max/2** (past-crossover regime).
  Ceiling at M ≤ 16 is expected substrate behavior, NOT MIDDLE_BAND.
- FHRR_CC failures at wall are informative (Plate CC has known norm-decay) but do
  NOT gate ELEM_BIPOLAR verdict.

## Timing budget

Per-cell cost dominated by cleanup-ON when M is large:
- Cheap tier (M ≤ 16, V=100): ~4 s/cell (matches A1 smoke)
- Cheap tier (M ≤ 16, V=1000): ~40 s/cell
- Expensive tier (M=64, V=1000, ON): ~50 s/cell
- Expensive tier (M=256, V=1000, ON): ~200 s/cell

Full estimate per seed: 60 cheap·V=100 (~4s) + 60 cheap·V=1000 (~40s) + 24 exp·V=100 (~30s) + 24 exp·V=1000 (~120s avg)
≈ 240 + 2400 + 720 + 2880 = **~6240 s ≈ 1.75 h/seed**. Three seeds ≈ **5.25 h**.

Timeout: **43200 s (12h)** with 2x buffer over compute estimate.

## Cross-references

- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (drill open item + PC1 predictions)
- `notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md`
  (Donoho-Tanner K/M ≈ 0.20 ± 0.03 at M/N ≈ 0.14; AMP-analog)
- `data/exp_m4_nested/metrics.json` (prior FHRR at N=1024; d1-d5 100/100/100/100/97)
- `data/exp_nesting_depth_cpu_v1/metrics.json` (prior smoke at N=2048; d4/d8 = 1.0)
- `data/exp_hrr_depth_budget_sparse_bipolar_v2/metrics.json`
  (W-free Hopfield direct recall; different paradigm — no M_bundle × V grid overlap)
- `data/exp_hrr_depth_budget_curve_v1_smoke/metrics.json` (A1 smoke; ceiling at M ≤ 16)

## Substantive answer this cell provides

Whether substrate's HRR bind + bundle + per-layer cleanup can host **grammatical
composition at usable context depths** (k=10-20 tokens) in the noise regime relevant
to real language workloads (V=1000+ vocabulary, M=256+ bundle width). If HARD_PASS
fires on all three primary gates, the substrate is chain-grade-eligible for M3
compositional cortex integration WITHOUT needing multi-substrate composition primitives.
If MIDDLE_BAND or HARD_FAIL, characterizes the exact wall geometry for M3
architecture decisions.

## Discipline observed

- Substrate-KB queried for prior work; overlap-check with sparse_bipolar_v2 completed
- CARDINALITY_OK stamped (504 units expected; hard-fail if breach)
- DISCRIMINATOR_SURVIVES_SCALE: smoke uses same N=8192 as full; TR reduced (20 vs 200);
  A2 grid guaranteed to produce measurable gap at (V=1000, M=256) — smoke verifies pre-dispatch
- No silent except (trial exceptions re-raised with variant/k/M/V/cleanup context)
- Regime-aware verdict logic (no false-MIDDLE_BAND from below-wall ceilings)
- Broken-PC via involutive baseline (V=100, k=20, M=1, OFF must fire ≥0.99)
