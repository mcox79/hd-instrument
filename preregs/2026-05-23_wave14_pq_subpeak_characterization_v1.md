# Pre-registration: wave14_pq_subpeak_characterization_v1

**Date**: 2026-05-23
**Queue**: local_cpu_queue (pure CPU; <5 min; all dependencies local)
**Axis probed**: Substrate-physics — P(q) multi-scale structure after PQ_OTHER_CARDINALITY
**Trigger**: wave14_pq_high_resolution_v1 FULL = PQ_OTHER_CARDINALITY (7 outer × ~8.5 sub-peaks = ~60 total peaks at N=16384); active_priorities.md "15-peak P(q) substructure — mechanism unknown after 15->28 hierarchy refuted"
**Script**: experiments/exp_wave14_pq_subpeak_characterization_v1.py
**Peak memory**: ~50 MB CPU (codebooks at N=4096 × 200 float32)
**Expected elapsed**: ~3-5 min

---

## Scientific question

The FULL pq_high_resolution run at N=16384 (200 seeds, 500 bins) produced PQ_OTHER_CARDINALITY: approximately 7 outer peaks × 8.5 sub-peaks per outer = ~60 total peaks. This refutes:
  1. PQ_FLAT_15 hypothesis (15 simple peaks; no sub-structure)
  2. PQ_HIERARCHICAL_28 hypothesis (28-cardinality endpoint-partition hierarchy)

The 60-peak multi-scale structure needs mechanistic classification:
  - Arithmetic spacing (uniform inter-peak gap) → spin-glass-like uniform RSB structure
  - Geometric / non-uniform spacing → RSB cascade (Parisi-style replica symmetry breaking levels) or heterogeneous multi-scale structure (materials science: spin-glass with multiple distinct free-energy valleys at irregular positions)

This experiment measures the coefficient of variation (CV) of inter-outer-peak gaps across N in {512, 1024, 2048, 4096} to classify the spacing structure.

---

## Design

- **N sweep**: [512, 1024, 2048, 4096] (CPU-feasible sizes; 60 seeds per N)
- **n_starts**: 30 (endpoint sampling per seed)
- **depth**: 25 (chain length for q-overlap measurement)
- **Peak detection**: outer at 50 bins + fine at 500 bins (same algorithm as pq_high_resolution_v1)
- **Spacing metric**: CV = std(inter-peak gaps) / mean(inter-peak gaps)
- **Primary verdict basis**: largest N in sweep (N=4096)
- **N-stability check**: n_outer range across N values (stable if max-min <= 3)

---

## Falsifiable predictions

### HARD PASS flavors

- **PQ_SUBPEAK_ARITHMETIC** (CV <= 0.30): outer peaks uniformly spaced → spin-glass-like RSB with equidistant free-energy barriers.
- **PQ_SUBPEAK_GEOMETRIC** (CV > 0.30): outer peaks non-uniformly spaced → Parisi RSB cascade or heterogeneous structure.
- **PQ_SUBPEAK_SINGLE_CLUSTER** (n_outer < 3): insufficient outer structure (possible at small N).

### Pre-registered expectation

The FULL result showed 7 outer peaks consistently. At N=4096 (smaller than the N=16384 FULL) expect 5-9 outer peaks with similar q_mean range (~0.14-0.20). P(GEOMETRIC) = 0.55 (the materials-science spin-glass analogy suggests irregular free-energy landscape with cascading RSB; also consistent with the "nearly-degenerate eigenspectrum" finding at v145). P(ARITHMETIC) = 0.30. P(SINGLE_CLUSTER) = 0.15 (small N artifacts).

The N-stability check tests whether the 7-outer-peak structure is N-invariant (scale-free substrate physics) or N-dependent (finite-size effect that would wash out at large N).

---

## Substrate-product interpretation

- GEOMETRIC → the substrate's free-energy landscape has an irregular multi-scale structure. From the crystal/spin-glass math perspective (feedback_materials_science_probe.md): this maps to a spin-glass with multiple distinct thermodynamic phases at different temperatures, not a single-level RSB. Operationally: the 28-element endpoint partition may correspond to a specific energy level within the multi-scale cascade.

- ARITHMETIC → uniform spin-glass RSB with equidistant barriers. Simpler model; easier to characterize analytically.

- Either outcome is a substrate-PHYSICS finding only; does not directly change the substrate-PRODUCT portfolio (which remains at 11 demonstrated capabilities).

---

## PROT compliance

Not a closure; no PROT-004/006 required. Substrate-physics characterization experiment. PROT-001 (exp_dev_decisions log entry) paired.
