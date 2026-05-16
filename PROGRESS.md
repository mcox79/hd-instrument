# Progress

## Current phase

**Week 2 - Modulators wired & tested.** Five named scalars (attention, reward, arousal, recency, gating) live in `ModulatorState`. Attention gates cleanup threshold; recency drives geometric-decay bundling. Reward/arousal/gating remain state-only until Week 3+. 20 verification tests passing, 7 skipped (Week 3-7 placeholders).

## Next milestone

**Week 3**: reward-modulated Hebbian learning over a sparse atom-association matrix. Dynamics must match closed-form steady-state predictions; reward sign controls weight growth vs decay; arousal scales the global learning rate.

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
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
