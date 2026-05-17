# Progress

## Current phase

**Week 7 complete.** Seven molecule experiments + Hebbian density sweep + FHRR-vs-BSC comparison done. Major findings overturned simplistic capacity models in M2 (real bundle capacity is ~3-4x higher than sqrt(N)), M4 (nested structures survive 5 levels deep, not 2-3), and surfaced temporal-aliasing in the lazy Hebbian decay (M7). M5 demonstrated learning actually augments cleanup (+6.7 pp at N=256 in the brittle regime). M6 gave the first quantitative FHRR-vs-BSC tradeoff: BSC has 2.5x lower capacity but 8x smaller atoms = ~3.5x better bytes-per-capacity for memory-bound workloads.

## Next milestone

**Week 8 - Scaling-law experiment.** With substrate behaviour empirically mapped, fit the scaling exponents:
- capacity vs N at fixed pool, FHRR and BSC separately
- depth-recovery vs N
- precision/recall curve shape vs N
- predicted thresholds vs empirical (e.g., does the sqrt(N) Plate knee hold up at large N?)

Pre-registered predictions in notes/exp_scaling.md before running.

## Open questions

- HRR inverse fidelity at low N - test currently asserts sim > 0.5 at N>=1024; tighten after collecting empirical distribution.
- Trace bus overhead at micro-bench scale is dominated by Python call overhead; Week 4 batched/sampled tracing should bring it under 10% on representative workloads.
- Storage choice: DuckDB vs SQLite for trace persistence - currently DuckDB.
- Recency uses geometric decay (1-r)^(k-1-i); alternative is exponential weighting. Reassess after molecule experiments in Week 7.

## Phase status

| Phase | Status | Notes |
|---|---|---|
| Week 0 - Scaffold | done | Repo, deps, CI, stubs |
| Week 1 - Substrate + trace (FHRR + HRR) | done | 15 verification tests passing |
| Week 2 - Modulators | done | attention + recency wired; reward/arousal/gating staged for Week 3+ |
| Week 3 - Learning | done | reward-modulated Hebbian, lazy decay, steady-state matches theory within 1% |
| Week 4 - Observability | done | DuckDB store, perf_counter timing, replay reconstructs state, PDF + Streamlit dashboards |
| Week 5 - Harness + go/no-go | done | Declarative ExperimentSpec, harness, same-seed determinism, GO decision |
| Week 6 - Atomic experiments | done | A1-A4 + A5 envelope; substrate cliff at sigma=pi |
| Week 7 - Molecule experiments | done | M1-M7; capacity 3-4x higher than predicted; learning boost; BSC tradeoff |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
