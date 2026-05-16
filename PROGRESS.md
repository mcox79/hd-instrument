# Progress

## Current phase

**Week 0 - Repo scaffolded.** Module skeletons, verification harness, CI in place. No production code yet.

## Next milestone

**Week 1**: substrate (atoms, binding, bundling, memory) for both FHRR and HRR + trace bus, with algebraic verification passing.

## Open questions

- HRR depth limit at N=1024 - empirical, expect to set after Week 1.
- Trace bus overhead under sustained load - target <10%.
- Storage choice: DuckDB vs SQLite for trace persistence - currently DuckDB.

## Phase status

| Phase | Status | Notes |
|---|---|---|
| Week 0 - Scaffold | done | Repo, deps, CI, stubs |
| Week 1 - Substrate + trace (FHRR + HRR) | pending | |
| Week 2 - Modulators | pending | |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments | pending | |
