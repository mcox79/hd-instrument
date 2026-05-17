# Progress

## Current phase

**Week 8 capacity-scaling fit complete.** Bundle-capacity exponent alpha = 1.003 +/- ~0.01, R^2 = 0.99999734 across N in {1024, 4096, 8192, 16384}. Empirical scaling: `k_50%(N) ~= N / 4.84` for pool_size=200. Pre-registered prediction (alpha = 1.0) confirmed cleanly. First quantitatively-fit empirical scaling law from the instrument.

## Next milestone

**Week 8 follow-ups:**
1. BSC scaling - does alpha stay at 1.0 with the binary substrate?
2. Depth scaling - fit alpha for `depth_50%(N)`.
3. Pool-size scaling - confirm `k_50% ~ N / log(pool)`.

Each adds another exponent to the empirical scaling story. Then Week 9 (release) and Week 10+ (continual-learning case study).

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
| Week 8 - Scaling-law (FHRR capacity) | done | alpha = 1.003, R^2 = 0.999997 across 16x N range |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
