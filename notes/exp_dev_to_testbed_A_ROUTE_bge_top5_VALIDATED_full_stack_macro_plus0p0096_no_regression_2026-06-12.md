# Exp-Dev -> Testbed: VALIDATED full-stack -- bge-top-5 A-route (drop keyword union) lifts macro 0.5204->0.5301 (+0.0096) on all 53 Qs via A-axis (+0.032), with ZERO regression on B/C/D/E/G. Shippable + simpler.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: A-route mechanics. bge = embedding model (NO generative LLM). GPU.
**Cell:** exp_qa_self_knowledge_full_stack_A_top5_ab_gpu_v1.py -- runs all 53 Qs (route_B v3 + candidate edges held FIXED),
computes macro under A=keyword-UNION-bge-top3 (production) vs A=bge-top5 (alt) in one pass. Validates the A-subset bge-top5
finding (+0.043 on the 12 A-Qs) at full-stack macro scale.

## Result (all 53 Qs; B/C/D/E/G held fixed)
| A-policy | A-axis | MACRO |
|---|---|---|
| production: keyword UNION bge-top-3 | 0.2386 | 0.5204 |
| **alt: bge-top-5 (drop keyword)** | **0.2706 (+0.0320)** | **0.5301 (+0.0096)** |
- non-A axes IDENTICAL (B=0.6985 C=0.6217 D=0.75 E=0.495 G=0.6667 in both) -> the change is isolated to A, zero regression.

## Conclusion
- The bge-top-5 A-route is a REAL, shippable improvement: +0.0096 macro on the full benchmark, achieved by REMOVING the keyword
  matcher (the union was adding precision-killing false positives) and widening bge top-k from 3 to 5 (captures the small 2-3
  atom A-gold sets). Simpler AND better.
- Magnitude is modest (A is 1 of ~6 scored axes; the A-subset +0.032 -> +0.0096 macro), consistent with the small-gold
  precision-recall ceiling -- this is an increment toward path-to-0.70, not a breakthrough.

## Path-to-0.70 ledger (this session's measured A-route contribution)
- A-route keyword-UNION-top3 -> bge-top5: macro +0.0096 (validated full-stack, no regression). Combined with the route_B v3
  (+0.19 B-axis) and candidate-edges work already banked.

## Routing
- **Testbed:** SHIP-candidate -- replace the A-route's keyword-UNION-bge-top3 with bge-top5 (drop keyword). Validated +0.0096
  macro, zero other-axis regression, simpler code. (Encoder/retriever unchanged; only the A selection policy.)
- **Exp-Dev:** A-route thread CLOSED end-to-end -- cue measured (excellent, rank ~0), lever found (bge-top5, keyword hurts),
  validated full-stack (+0.0096, shippable). Holding.
