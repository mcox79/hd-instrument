# Progress

## Current phase

**Week 8 complete -- three scaling laws fit:**

- **FHRR capacity**: `k_50% ~ N^1.003` (R^2 = 0.99999734)
- **BSC capacity**: `k_50% ~ N^1.004` (R^2 = 0.9999), FHRR/BSC ratio constant at 2.52x
- **Nesting depth**: `depth_50% = 0.717 * log2(N) - 0.629` (R^2 = 0.973, slightly sub-linear)

Headline: both substrates scale linearly with N, BSC trades 2.5x capacity for 8x storage (= 3.2x bytes-per-capacity better) with no scaling-exponent penalty. Depth scales sub-linearly in log(N) -- one prediction falsified, mechanism identified. Full summary in [notes/week8_scaling_summary.md](notes/week8_scaling_summary.md).

## Next milestone

**Week 9 - Standalone release.** Publish `hd-instrument` v0.1.0 to PyPI, MIT-licensed; MkDocs site with the scaling-law plots embedded; quickstart notebook that runs the diagnostic.

Then **Week 10+ - Case study**: continual learning on Split-CIFAR-10 with substrate behaviour empirically mapped.

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
| Week 8 - Scaling-law (FHRR + BSC + depth) | done | FHRR a=1.003, BSC a=1.004, depth beta=0.717; see week8_scaling_summary.md |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
