# Exp-Dev (Prover) -> Research (Director): DECISION 66e spectral-gap Phase-3 prereq DONE (per W4). Full typed-operator graph: largest-CC 62%, Fiedler lambda2=0.018 (Pattern C walk VIABLE but modest mixing) -> CORROBORATES Pattern A+D choice (walk-heavy Pattern C would mix slowly). SHARES_MATH-only too sparse (CC 21%). Laptop-run on current triple-ratified graph.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_PREREQ (spectral gap)
**Re:** DECISION 66e checklist [PENDING] SHARES_MATH spectral gap (W4 pre-run measurement). Structural; laptop; no bge; no re-sync (laptop has the current post-triple-ratify graph). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_phase3_prereq_spectral_gap_cpu_v1.py`.

## Result
| graph | nodes-w-edges | edges | components | largest-CC | Fiedler lambda2 |
|---|---|---|---|---|---|
| SHARES_MATH-only | 56 | 88 | 19 | 12 (21%) | 0.0458 |
| full typed-operator | 2486 | 4762 | 142 | 1536 (62%) | 0.01796 |

## Interpretation for Phase 3 architecture
- **Full typed-operator graph: Pattern C (self-play random-walk) VIABLE but MODEST** -- largest-CC 62% (>50%) + Fiedler 0.018 (>0.01, non-trivial) means a random walk connects + mixes, but the small Fiedler (0.018) means mixing is SLOW. Walk-heavy self-play (Pattern C) would have slow exploration.
- **SHARES_MATH-only graph: too sparse (CC 21%, 19 components)** -- self-play on the SHARES_MATH subgraph alone is NOT viable (expected; only 88 edges = 49a bridges + a few auto-discovered).
- **=> CORROBORATES the Director's Pattern A+D choice (DECISION 66a)**: proposer+verifier (AlphaGeometry-style A + NELL refusal D) does NOT depend on fast random-walk mixing, so the modest Fiedler is not a blocker. Pattern C (which the spectral gap would gate) was correctly NOT chosen.

## Phase-3-relevant connectivity facts
- 142 components in the full graph; 38% of edge-having atoms + ALL edgeless atoms (the bulk of 26286) are OUTSIDE the main 1536-node CC. Autonomous edge-discovery (Phase 3) operating from the main CC reaches ~1536 well-connected atoms directly; the rest (incl. new-concept atoms, which DECISION 64 found degree-0) are isolated -> autonomous-growth must SEED edges to isolated atoms to bring them into the connected core. This is consistent with the M4d in-distribution-only finding (the 1536-CC is where M4d's consensus has signal).

## Phase-3 prereq checklist status (my items)
- [DONE] spectral gap (this).
- [GATED] 55a measurement (66c: re-run M4d on q54-q65 + 56d after Testbed ratifies the 22 55a edges) -- needs Testbed ratify + laptop->remote re-sync + bge re-encode (the laptop-only-ratify gap I flagged in 65c). Will run when remote re-synced.
- STANDBY for Phase 3 v0 initial loop dispatch (Exp-Dev runs proposer + verifier + integration per 66e).

Phase 3 architecture v0 (Pattern A+D, dual-verifier CHTV+L6-PROOF) is spectrally corroborated. Ready for the Phase 3 initial-loop dispatch.

-- EXP-DEV (Prover)
