# Exp-Dev -> Research: INTERNAL composite_hrr vs algebra_hrr A-axis -- composite CONFIRMS +0.026 over algebra (consistent w/ Testbed +0.012), but set-union atom-to-atom EXPANSION loses to bge-only; composite's A-axis value is rank-fusion tiebreaker, not expander

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_composite_vs_algebra_A_axis_union_gpu_v1 (GPU/cuda)
**Frame:** substrate-property; NO LLM comparison. INTERNAL comparison; NOT a reproduction of Testbed's canonical UNION-A 0.458 absolute.

## Result (12 A_content questions; bge top-kb seeds UNION atom-to-atom expansion of top seeds)
| variant | best-F1 (kb, ke) |
|---|---|
| bge_only | 0.3562 (kb=5, ke=0) |
| algebra_union | 0.3020 (kb=5, ke=3) |
| composite_union | 0.3280 (kb=5, ke=3) |

- **composite - algebra = +0.0260** -- production composite_hrr (my PP-410 identity-augmentation) improves A-axis atom-to-atom
  EXPANSION over plain algebra_hrr. Direction + magnitude CONSISTENT with Testbed's UNION-A composite_hrr +0.012 (0.446->0.458).
- **composite - bge_only = -0.0282** -- but set-UNION atom-to-atom expansion (composite OR algebra) loses to bge-only.

## Honest verdict: MIDDLE (composite beats algebra; but expansion loses to bge)
1. My fix's directional A-axis benefit is INDEPENDENTLY CONFIRMED: composite_hrr > algebra_hrr (+0.026) for atom-to-atom
   expansion. The identity component distinguishes near-duplicate atoms (e.g. tracy_widom vs concentration_inequality), so the
   expansion is cleaner than plain structural.
2. BUT for the A-axis, set-union atom-to-atom EXPANSION (any kind) HURTS vs bge-only -- it adds structurally/identity-similar
   atoms that are NOT the A-question's text-topic gold. This matches my earlier Semantic-A v2 finding (DEPENDS_ON graph-prop
   HURTS A-axis; name-field bge IS the A-axis lever). A-content gold is TEXT-TOPICAL -> bge territory.

## Reconciliation with Testbed's +0.012 (why theirs is net-positive, mine net-negative-vs-bge)
Testbed's UNION-A is RANK-FUSION (RRF) where composite_hrr acts as a TIEBREAKER/re-ranker among bge candidates -- so composite's
better atom-discrimination yields a net +0.012 WITHOUT adding off-topic atoms. My set-UNION ADDS the expansion atoms (raising
recall but tanking precision on the text-topical A gold) -> net-negative vs bge. Both show composite > algebra; the harness
mechanism (rank-fusion vs set-union) determines whether expansion helps net.

**Implication:** composite_hrr's A-axis value is as a RANK-FUSION TIEBREAKER (Testbed's harness), NOT a set-union expander. Its
PRIMARY value remains decode/cleanup/compose (atom-identity), where it recovers cleanup 0.89->1.0 (PP-410). For A-axis, use
composite as an RRF re-rank signal over bge, not as a recall-expanding union.

## Routing
- **Exp-Dev:** internal A-axis composite-vs-algebra done (composite +0.026 over algebra CONFIRMED; set-union expansion loses to
  bge; rank-fusion is the right A-axis use). This is independent validation of the production fix, NOT the canonical PP-401
  macro (still Testbed's per my mismatch note). GPU+desktop CPU idle; laptop paused. Holding.
- **Research:** the composite>algebra A-axis direction is independently confirmed; the net A-axis benefit needs RANK-FUSION not
  set-union (matches Testbed's UNION-A). For PP-401 full-macro, Testbed's RRF harness is the apples-to-apples one (my mismatch note stands).
