# Progress

## Current phase

**Week 4 - Observability stack complete.** Every public op records `elapsed_ns` via `time.perf_counter_ns` (Windows monotonic_ns was 15ms-coarse, useless). Events persist to DuckDB and round-trip byte-equivalent. **Trace replay reconstructs Hebbian weights identical to the original session within 1e-9** — the gating test for the whole observability story. Streamlit dashboard module loads cleanly with panels for modulator timeline, op frequency, per-op latency, Hebbian trajectories, and recent events. 32 verification tests passing, 3 skipped (Weeks 5 + 7).

## Next milestone

**Week 5**: declarative experiment harness, cross-machine reproducibility (same seed -> bit-identical results), and the go/no-go review. End of Week 5 the platform is locked; experiments (atomic / molecule / scaling) start Week 6.

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
| Week 4 - Observability | done | DuckDB store, perf_counter timing, replay reconstructs state, Streamlit panels load |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
