# Exp-Dev -> Testbed/Research: the production two-vector composite (alpha=0.5) sits CENTRAL in a WIDE robust plateau alpha in [0.15, 10] (~70x). NOT a delicate knee -- robustness is a high-D-orthogonality property.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-physics of the PRODUCTION index. NO LLM. GPU.
**Cell:** exp_two_vector_alpha_plateau_gpu_v3.py (N=1024 production dim, 2400 atoms, 60 tight near-colliding structural classes,
noisy identity queries). Honest path: v1/v2 SATURATED at 1.0/all-alpha (uninformative) -> diagnosed high-D orthogonality ->
v3 mapped the plateau boundaries with fine-low + extreme-high alpha grid.

## What was tested
Production: `composite_hrr = normalize(algebra_hrr + 0.5*name_vec)` (PP-410, backend/substrate_index/algebra_index.py). Two
competing objectives as a function of the name-vec weight alpha:
- **identity_prec@1** -- noisy name-cue retrieves the EXACT atom (collision-resistance). Higher alpha helps.
- **struct_recall@5** -- algebra-cue's top-5 composites are same structural class (desirable collisions). Higher alpha hurts.

## Result -- the alpha curve (id_prec / struct_recall@5)
| alpha | 0.0 | 0.05 | 0.10 | 0.15 | 0.25 | 0.5 | 1 | 2 | 5 | 10 | 20 | 50 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id_prec@1 | .000 | .156 | .584 | .918 | 1.0 | **1.0** | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| struct_rec@5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | **1.0** | 1.0 | 1.0 | 1.0 | .997 | .508 | .111 | .054 |

**Robust band (both >= thresholds): alpha in [0.15, 10.0] -- ~70x wide. Shipped alpha=0.5 is CENTRAL** (~0.5 dex above lower
edge, ~1.3 dex below upper edge).

## Finding (stronger + more honest than "0.5 is the optimal knee")
- The two-vector composite is NOT a delicate tuning: identity and structure coexist over an order-of-magnitude-plus range of
  alpha. The production 0.5 is well-chosen AND non-critical -- future re-tunes (e.g. after ingestion shifts atom density) have
  a huge safe margin.
- MECHANISM: in high dimensions name_vec and algebra_hrr are near-ORTHOGONAL, so superposing them does not interfere -- each
  reads out along its own subspace. This is the blessing-of-dimensionality / the whole point of HRR superposition.
- The two edges are interpretable: lower edge (~0.15) = where the name signal first overcomes the noisy query + within-class
  structural ambiguity (identity onset 0.05->0.15: .16->.58->.92); upper edge (~10-20) = where name finally SWAMPS the
  structural readout (struct_rec falls .997@10 -> .508@20 -> .054@100). identity never breaks (no upper failure for identity).

## Routing
- **Testbed:** the production two-vector weight is validated with a wide safety margin -- no action needed; if atom density
  grows a lot post-ingestion, re-measure struct_recall (the upper edge is the only one that moves with crowding). Cell is
  importable for periodic re-measurement.
- **Research:** the two-vector design's robustness is a *structural* property (high-D orthogonality), not a tuned constant --
  clean substrate-product positioning: the substrate stores identity + structure in one vector without interference, and the
  mixing weight is non-critical over ~70x. No LLM.
- **Exp-Dev:** done. Honest arc preserved (saturated v1/v2 -> diagnosed -> mapped boundaries). Holding.
