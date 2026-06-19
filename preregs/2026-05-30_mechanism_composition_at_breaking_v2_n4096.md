# Prereg: mechanism_composition_at_breaking_v2_n4096

**Date:** 2026-05-30
**Anchor:** mechanism_composition_at_breaking_v2_n4096
**Script:** experiments/exp_mechanism_composition_at_breaking_v2_n4096.py
**Queue:** overnight_queue
**Timeout:** 14400s

## Why this anchor

Q2 v1 mechanism-composition was ceiling-bound: all individual paths {B, D, E}
hit 1.000 at moderate (M, depth) so composition couldn't show improvement.
v2 re-runs at HARDER regime where individuals degrade, leaving room for
composition to demonstrate error-correction or noise-introduction.

## Hard-regime cells

Per user spec (cells chosen a priori, NOT contingent on R1 outcome):
- cell-1 = (M=16384, depth=15) -- at M_c, deep multi-hop
- cell-2 = (M=24576, depth=10) -- past M_c, moderate depth

This is an accepted risk: if R1 shows these are not actually hard cells, R2
will be inconclusive too. Sequential dispatch (wait for R1 before designing
R2) would slow throughput.

## Composition designs

- **cA = INTERSECTION**: argmax(B), pred(D top-1), pred(E top-1) must ALL agree.
  Sharp filter.
- **cB = WEIGHTED VOTE**: combined score = 0.5 * D_norm + 0.5 * E_norm + 0.5 * B_bonus
  where B_bonus = 1.0 to any candidate whose target equals B's argmax. Argmax of
  combined score selects predicted target.
- **cC = CONSENSUS / MAJORITY**: each of B, D, E votes a target index. Majority
  wins; tie broken by combined score from cB.

## Sweep grid

- N = 4096 (PROT-018 _n4096 binding).
- Cells: [(16384, 15), (24576, 10)].
- K_paths = 500.
- 3 individual mechanisms (B, D, E) + 3 composition mechanisms (cA, cB, cC).
- Seeds: {7, 17, 23, 31, 41}.
- Per-cell-seed checkpoint.
- Cells: 2 (M, depth) x 5 seeds x 6 mechanisms (computed in one pass) = 10 row writes.

## Pre-registered bands

- **HARD_PASS (HP)** = at least one composition design's accuracy improves by
  >= 0.15 over the best individual path at cell-1 (the hardest cell) in
  >= 3/5 seeds. Reading: "composition demonstrates error-correction."
- **HARD_FAIL (HF)** = ALL composition designs perform WORSE than best individual
  at BOTH cells in >= 4/5 seeds. Reading: "composition introduces noise."
- **MIDDLE_BAND (MB)** = otherwise. Reading: "composition neutral or mixed."

## Outcome plan

| Verdict | Action |
|---|---|
| HARD_PASS | Composition is a productive cap_map node; promote to follow-on cells; ship cap class entry. |
| HARD_FAIL | Composition is the wrong abstraction at multi-hop; revisit single-path optimization. |
| MIDDLE_BAND | Identify which composition shows the strongest signal (cA / cB / cC), iterate on that design. |

## Closed-form self-tests in the script

- `compute_verdict(fake_hp)` -> HARD_PASS when cB improves >= 0.15 over best individual at cell-1 in all 5 seeds.
- `compute_verdict(fake_hf)` -> HARD_FAIL when all compositions < all individuals at both cells.
- `compute_verdict(fake_mb)` -> MIDDLE_BAND for mixed deltas.

## Timeout estimate

smoke_wall_s = 1.2s (N=1024, M=512, depth=3, K=20, 1 seed, 6 mechs).
FULL: N 1024->4096 (4x; exp=1.5 for vector + filter), M 512->24576 storage
dominates (proportional), depth 3->15 (5x), K 20->500 (25x but only D affected),
seeds 1->5 (5x), cells 1->2 (2x).
Per-cell-seed estimate ~40-60s at hardest cell.
60 cell-seeds * 6 mechs (computed jointly) = effective ~2400-3600s expected.

**Timeout: 14400s** (per user spec, 4h buffer).

## PROT-018 _n4096 binding

`N = 4096` is a module-level constant. Verified.

## Dependency check

- experiments/_metric_battery.py (make_substrate) -- exists
- experiments/_relation_graph.py -- exists
- experiments/_seed_checkpoint.py -- exists
- No upstream data files required.
