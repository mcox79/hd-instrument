# exp_dev hand-off -- research: minimal nonlinearity for replay consolidation

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_minimal_nonlinearity_for_replay_consolidation_2x_2026-06-04.md
Date: 2026-06-04

Per [[feedback-no-experiment-design-in-prompts]]: this file hands task + why + contract + autonomy
to exp_dev. It does NOT specify anchor names, sweep grids, threshold formulas, numerical bounds,
or queue assignments. exp_dev designs those.

## Pause state

Check data/orchestrator_paused.flag before dispatching. If paused, hold this handoff.

---

## Why this matters

B5 empirical result (2026-06-04): linear additive W palimpsest gives none > random > ordered
retention (0.836 > 0.748 > 0.738 > 0.694). This is algebraically necessary -- linear outer-product
updates commute, so replay order is provably irrelevant. The substrate needs a nonlinearity for
ordered > random consolidation to be achievable.

Research drill found:
1. Bounded/clipped weights (saturation nonlinearity) is the ALGEBRAICALLY CLEANEST and
   BEST-LIT-SUPPORTED candidate (Lazaro et al. 2025, direct Hopfield precedent).
2. B2 sparse k-WTA + bounded W combination is the cheapest compositional test.
3. P_deflated for "B2+bounded W, ordered >= 1.3x vs no-replay" = 0.45.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
- Pointer: B5 palimpsest replay + bounded weight clipping (W_max)
- Substrate-product reading: does adding a W_max clip to the B5 palimpsest update
  rule create the saturation nonlinearity required for ordered > random > no-replay?
- Tier hint: small-scale CPU smoke first (rung 1-2, per small-scale-first methodology)
- Why now: lit precedent is direct (Lazaro 2025), algebraic mechanism is clean, cheapest
  engineering path (single clip() call added to existing B5 update rule)

### Anchor 2 (SECOND PRIORITY)
- Pointer: B2 sparse k-WTA architecture + B5 replay protocol (composition)
- Substrate-product reading: does the state-dependent completion nonlinearity in B2's
  k-WTA forward pass during replay create order-dependence at moderate-to-high load?
- Tier hint: CPU smoke, moderate load (M near sparse capacity), multiple seeds
- Why now: B2 is already HP validated; composition with B5 is the cheapest test of
  whether k-WTA nonlinearity alone suffices (before adding bounded W complexity)
- Note: research predicts 3-8% order benefit at low load, not 1.5x -- test at higher M

### Anchor 3 (IF 1+2 FAIL)
- Pointer: B2 sparse + bounded W combination
- Substrate-product reading: synergy of two nonlinearities -- sparse code reduces
  synapse overlap, bounded W creates saturation priority for ordered replay
- Tier hint: CPU smoke first, then GPU depth if smoke shows signal

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_minimal_nonlinearity_for_replay_consolidation_2x_2026-06-04.md
- B5 empirical result: see orchestrator_status_log.jsonl entry for 2026-06-04 (B5 verdict)
- B2 HP validation: cap_map row B2 (sparse k-WTA, HP)

---

## Contract

exp_dev autonomy on: anchor names, sweep parameters, threshold formulas, queue routing,
seed counts, W_max sweep range, load (M) selection.

exp_dev must: pre-reg HP/MID/HF bands before queuing; verify B2 baseline before composition;
smoke at rung-1 CPU before scaling.

Orchestrator must confirm: cap_map implications of PASS or FAIL before closing this handoff.
