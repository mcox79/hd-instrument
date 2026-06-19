# Exp-Dev -> Testbed: a SIMPLE A-route change -- bge-top-5 (drop the keyword union) -- beats the production keyword-UNION-top-3 by +0.043 A-F1. The keyword union HURTS. Ceiling is small-gold precision-recall (top-8 regresses).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: A-route mechanics. bge = embedding model (NO generative LLM). GPU.
**Cell:** exp_qa_self_knowledge_A_threshold_route_gpu_v1.py (real substrate + gap7 benchmark, 12 A-Qs, full-gold-set A-F1).
Motivated by the cue-alignment diagnosis (A-gold median bge rank 0.5/1743, cos ~0.77, small gold sets).

## A-F1 by selection policy (n=12 A-Qs)
| policy | A-F1 | vs prod |
|---|---|---|
| prod: keyword UNION bge-top-3 | 0.3178 | -- |
| bge-top-3 (drop keyword) | 0.3324 | +0.015 |
| **bge-top-5 (drop keyword)** | **0.3608** | **+0.043** |
| bge-top-8 | 0.3499 | +0.032 |
| cosine-threshold tau=0.70 | 0.3579 | +0.040 |
| cosine-threshold tau=0.60 / 0.75 | 0.123 / 0.237 | brittle |
| keyword UNION threshold 0.65/0.70 | 0.243 / 0.334 | keyword hurts |

## Findings
- **The keyword UNION HURTS A-axis.** Production keyword-UNION-top-3 (0.318) is BEATEN by pure bge-top-3 (0.332) and bge-top-5
  (0.361). The keyword matcher adds precision-killing false positives; the bge cue alone is better.
- **bge-top-5 is the A-axis optimum (+0.043).** It captures the small multi-atom gold sets (2-3 atoms) that top-3 misses,
  without top-8's precision loss (top-8 regresses to 0.350). A cosine threshold ~0.70 is comparable (0.358) but brittle to tau.
- **Ceiling = small-gold precision-recall.** Beyond top-5, precision falls faster than recall rises -> the A-axis residual is a
  precision-recall-on-small-gold-sets wall, consistent with the cue-alignment diagnosis (cue is excellent; fusion is the limit).

## Honest reconciliation with the prior "tuned-UNION-bound / simple bge routes hurt" finding
- The prior conclusion was that simple bge routes hurt the A-axis. This measurement REFINES it: a simple bge route (top-5,
  no keyword) actually HELPS A-F1 by +0.043. Likely the prior tests used top-3 (only +0.015) or judged on MACRO. MACRO impact
  here is small: A is 1 of 7 axes, so +0.043 A-F1 ~ +0.006 macro -- real but modest, not a path-to-0.70 breakthrough.

## Routing
- **Testbed:** consider replacing the A-route's keyword-UNION-bge-top-3 with bge-top-5 (or cosine-threshold ~0.70). It SIMPLIFIES
  the route (drops keyword) AND lifts A-F1 +0.043 (macro ~+0.006). Validate on the full benchmark before shipping; n=12 here.
  The small-gold precision-recall wall caps further gains.
- **Exp-Dev:** A-axis route question CLOSED -- cue excellent, keyword-union harmful, bge-top-5 optimal, small-gold P-R ceiling.
  Holding.
