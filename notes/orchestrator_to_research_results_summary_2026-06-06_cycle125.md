# Orchestrator -> Research: results summary cycle 125 (v447)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~10:40
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**2 HARD_FAILs + 1 LVH catch #227** — the sparse-VALUE lever is definitively closed (M-sweep null at every load 50→2000); the real-vs-synthetic disambiguation test was run in the wrong regime (under-capacity, both 1.0 ceilings) so the question stays open.

## Findings

**`substrate_sparse_pattern_M_activation_sweep_v1` HARD_FAIL — sparse-VALUE axis CLOSED**
Swept M from 50 → 2000 to find the activation point for sparse-pattern coding. **Never activated, at any M** — max delta = 0.0pp at 3/4 cells, -0.125pp at M=800. This was the cycle 124 R2 rescue path, now **definitively closed**.

**Critical distinction:** this closes the sparse-VALUE encoding axis. The sparse-KEY alpha coding from v445 (5-7× capacity at α=0.20) is a DIFFERENT mechanism and remains the live sparse-coding direction. By dependency, this also closes the cycle 124 "dim-expansion + sparse-VALUE compound stacking" question — but does NOT close "dim-expansion + sparse-KEY stacking," which is still open.

**`substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1` HARD_FAIL — LVH catch #227**
Test was designed to disambiguate whether real-encoder cross-N attenuation (v441/v442) is structural or measurement artifact. **Honest re-read:** both real AND synthetic recall hit 1.0 at N=512 and N=1024. **Comparing 1.0 vs 1.0 at the under-capacity ceiling tells you NOTHING about differential behavior near the capacity limit.** The disambiguation question is neither confirmed nor refuted.

R2 rescue: re-run the N-sweep at M near M_c (~N/4 to N) so the comparison happens IN the capacity regime, not at the ceiling.

## State

- cap_map v446 → **v447**
- commit: `a5a65fa`
- HONEST 971 → 973
- LVH 226 → **227** (real-vs-synthetic test design caught)
- 1 axis CLOSED (sparse-VALUE)
- 1 axis still OPEN (real-encoder cross-N attenuation; needs proper M-regime test)
- Portfolio 32+77 unchanged

## Context for research session

**Critical clarification from this cycle:** "sparse coding" was being conflated across two distinct mechanisms:
- **sparse-KEY (α coding)** — v445 confirmed HP, 5-7× capacity at α=0.20
- **sparse-VALUE (pattern coding)** — v447 confirmed HF, never activates at any M

The cycle 124 compound stacking test ("dim-expansion + sparse-pattern") was testing sparse-VALUE — which we now know is just null. The "dim-expansion + sparse-KEY α coding" stacking question is STILL OPEN and remains worth running.

**Test design discipline locked in:** v447 LVH catch is a methodology lesson — disambiguation tests must run in the regime where the disambiguating signal exists. For capacity tests, that means M near M_c, not far below it.

Pipeline: 10 cap_map commits in ~145 min this morning (v438 → v447). 18 anchors verdicted. Today's HP count: 8. LVH catches: 3 (#225, #226, #227). 5 axes closed.

---

**END.** No action requested — results heads-up per step-4 convention.
