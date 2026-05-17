# Progress

## Current phase

**Week 5 - Platform locked. GO to Week 6.** Declarative `ExperimentSpec` + `experiment.run(spec, workload)` harness handles seed/trace/persist/PDF/log in one call. Diagnostic refactored to use it. Reproducibility tests confirm same-seed determinism in process; cross-machine bit-equality will fall out of CI on `ubuntu-latest`. Go/No-Go review in [notes/week5_go_no_go.md](notes/week5_go_no_go.md). 38 verification tests passing, 2 skipped (Week 7 placeholders).

## Next milestone

**Week 6 - Atomic experiments.** A1: 50 atoms + exact-match query. A2: cleanup robustness under Gaussian noise. A3: attention sweep produces clean P/R curves. A4: Hebbian learning over repeated queries lifts recall on frequent atoms. This is the first week the dashboard reads as a finding rather than a heartbeat.

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
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
