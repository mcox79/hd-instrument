# Exp-Dev -> Testbed/Research: BOTH weak axes (A-content 0.27 + E-methodology 0.495) are CUE-ALIGNED, not cue-bound. The bge cue puts the gold atom at the TOP (A rank ~0.5, E rank ~0.0; recall@10=1.0 both). The qa_self_knowledge weak-axis bottleneck is downstream SELECTION on small gold sets -- NOT the encoder.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: A-route/E-route mechanics. bge = embedding model (NO generative LLM). GPU.
**Cells:** exp_qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1 + exp_qa_self_knowledge_E_cue_alignment_diagnosis_gpu_v1.

## Cue alignment of BOTH weak axes (bge cosine of query -> gold atom)
| axis | F1 | n (gold-in-index) | median best-gold cos | recall@3 | recall@10 | median gold rank /1743 |
|---|---|---|---|---|---|---|
| A (content) | 0.27 | 12 | 0.771 | 0.92 | 1.00 | 0.5 |
| E (methodology) | 0.495 | 7 | 0.813 | 0.86 | 1.00 | 0.0 |

## Unified finding
- For BOTH weak axes the bge cue is EXCELLENT -- the gold atom is the top (E) or near-top (A) semantic hit, and recall@10=1.0.
  So NEITHER weak axis is query-encoding/cue-limited. The bge encoder is NOT the qa_self_knowledge bottleneck (measured, 2 axes).
- The A/E residual is DOWNSTREAM of the cue: SELECTION on small gold sets (which top-k / fusion policy turns the excellent
  ranking into the returned set). For A this was confirmed actionable: bge-top-5 (drop keyword) lifted A-F1 +0.043 / macro
  +0.0096 (validated full-stack, no regression).
- IMPLICATION for E: E-gold is at bge rank ~0.0 (even better than A) -- if the current E-route does not already lean on bge
  semantic selection, adding a bge-top-k E-route is a candidate lever (E has more headroom than A, 0.495 vs 0.27). Next cell.

## Honest note
- This generalizes + confirms the A-axis self-correction: the two-vector trilogy predicted the free-text paths would be
  cue/query-SNR-bound; MEASUREMENT on BOTH weak axes refutes that -- the bge cue is so strong the binding constraint is
  downstream selection, not the cue. Encoder work is NOT the lever for A or E.

## Routing
- **Testbed/Research:** stop considering encoder/cue improvements for A and E -- both measured cue-aligned (gold at top). The
  lever is the SELECTION policy (top-k / fusion) on small gold sets. A: ship bge-top5 (validated). E: test a bge-top-k route.
- **Exp-Dev:** both weak axes diagnosed at the cue level (cue excellent, selection-bound). Building the E bge-route lever next.
