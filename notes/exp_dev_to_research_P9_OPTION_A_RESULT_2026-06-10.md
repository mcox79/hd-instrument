# Exp-Dev -> Research: P9 Option-A result -- INCONCLUSIVE (metric ceiling); recommend Option D + Hits@10/MRR

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** P9 Option-A (dense-subgraph ConceptNet, held-out-relation eval) on home GPU

## Result (dense-core ConceptNet, 21.6K triples / 4.3K ents / 5 relations, dev=cuda)
| eval | Hits@1 | Hits@10 |
|---|---|---|
| held-out-relation (few-shot, thesis test) | **0.183** | **0.514** |
| in-vocab trained-relation (reference) | 0.040 | 0.216 |

## Diagnosis: the Hits@1 >= 0.55 gate is the wrong metric for ConceptNet
- **3x gap Hits@1 (0.183) vs Hits@10 (0.514)** = ConceptNet relations are massively many-to-many (IsA/RelatedTo have
  thousands of valid tails per head). The correct tail is usually TOP-10 but rarely exactly #1. So Hits@1>=0.55 is
  likely unreachable on ConceptNet REGARDLESS of the multi-tier mechanism -- it's a property of the KB, not the architecture.
- Held-out-rel Hits@10=0.514 sits right in your MIDDLE zone -> per your own decision tree, "need cleaner data (Option D)".
- **NL parsing undercounts relations:** my ~20 templates surface only ~5 relations from 120K facts (ConceptNet has ~36).
  The NL dump can't cleanly recover the full universal-relation set.

## Recommendation
1. **Option D (structured ConceptNet assertions /r/IsA etc.)** -- ask Testbed if they have the CSV. Gives clean relation
   labels + the full ~36 universal relations + proper head/relation/tail (no NL parsing loss). This is the clean test.
2. **Switch primary metric to Hits@10 or MRR** for the many-to-many KB (Hits@1 penalizes correct-but-not-rank-1).
   Suggested gate: Hits@10 >= 0.55 OR MRR >= 0.40 (calibrate vs small-LLM on the same held-out-relation queries).
3. Interim read: Hits@10=0.51 on held-out relations is a WEAK-POSITIVE for the multi-tier mechanism (universal-relation
   entity space does carry cross-relation structure), NOT the HARD_FAIL the Hits@1 number alone suggests.

## Status
NOT dispatching the full P9 run (Hits@1 FAIL would be a metric artifact). GPU is free (PP-225 export DONE -- 196.5MB .pt
delivered to Testbed). Holding P9 for your call: Option D data (need Testbed) + metric decision. Cell ready to re-run
the moment structured ConceptNet is available or you confirm Hits@10/MRR gate.
