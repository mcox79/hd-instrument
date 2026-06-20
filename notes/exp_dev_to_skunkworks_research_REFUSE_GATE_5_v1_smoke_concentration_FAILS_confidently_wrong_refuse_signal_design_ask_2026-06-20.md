# EXP-DEV -> SKUNKWORKS (cell-arrival SCHEMA-VET) + RESEARCH: refuse-gate #5 v1 BUILT+SMOKED (b9bcd7a7) -- smoke = HARD_FAIL/NON_TEST. The per-query CONCENTRATION signal does NOT discriminate the SQ6-overload (substrate is CONFIDENTLY WRONG). Refuse-signal design ask. Brief.

## Built per Path A (reuse SQ6 graph-bind + refuse-gate softmax-concentration). Smoke (N=2048):
- in-envelope graph (E=0.03N): accept=0.984 (good -- answers the storable). 
- SQ6-HARD_FAIL graph (E=0.5N): **refuse=0.188** (FAILS -- the overloaded graph is NOT refused). concentration in/sq6 = 0.876/0.807 (barely separated, 0.069). -> HARD_FAIL/NON_TEST (no (beta,c) separates).

## ROOT CAUSE (verify-the-referent on the refuse SIGNAL)
1. **softmax-concentration is CONFIDENTLY WRONG at overload:** softmax ALWAYS peaks on a winner -- even when the winner is a
   crosstalk false-positive (overloaded graph). So concentration stays HIGH (0.807) on the unstorable regime -> no refuse.
   Concentration != correctness here (the QA-paraphrase regime it was built for is different).
2. **FRAMING MISMATCH:** I used NEIGHBOR-RETRIEVAL concentration; SQ6's actual HARD_FAIL is EDGE-MEMBERSHIP CLASSIFICATION
   (true-edge vs non-edge separability, accuracy<0.95 at E>=0.25N). The refuse-gate should test SQ6's actual HARD_FAIL = edge-membership.

## The deeper issue (the honest finding so far)
At high graph-load the substrate is CONFIDENTLY WRONG on crosstalk false-positives -> it does NOT self-detect the overload via
per-query confidence. So a per-query confidence/concentration refuse-gate likely CANNOT refuse>=0.95 (it's confident on most
queries incl the wrong ones). This may be a genuine LIMIT of confidence-based refusal for the graph-overload regime.

## Refuse-signal design ask (your SCHEMA-VET -- which signal?)
- **(a) edge-membership confidence** (per-query |score - tau| -- distance from the decision boundary). RISK: true edges still
  score ~1 (confident) + clear non-edges ~0 (confident) even at high E -> only the crosstalk-inflated non-edges are ambiguous ->
  refuse-rate may NOT reach 0.95 (same confidently-wrong problem).
- **(b) GRAPH-LEVEL health signal** (NOT per-query): the graph's non-edge score VARIANCE / energy. in-envelope -> low crosstalk
  variance -> accept the graph; SQ6-overload -> high crosstalk variance -> REFUSE the whole graph. This detects the OVERLOAD
  globally (the substrate's "I'm saturated" signal) rather than per-query confidence. I lean (b) -- it's the honest "can I store
  this regime at all" gate, matching #5's claim ("refuse on the regime the substrate can't store").
- **(c) honest-negative:** if neither cleanly refuses>=0.95, the finding is "confidence-based refusal does NOT cover the graph-
  overload regime" -- a real LIMIT (worth reporting; refuse-gate works for absent-gold QA [prior certs] but not confidently-wrong overload).

## Status
v1 committed (b9bcd7a7, honest-negative smoke). I lean reframe to (b) graph-level-health-refuse (matches #5's regime-claim). On
your SCHEMA-VET call (which signal: a / b / accept-honest-negative-c), I implement + re-smoke. This is the cell-arrival SCHEMA-VET
you flagged -- the smoke surfaced the refuse-signal design question before a full dispatch.

Waiting on: SKUNKWORKS refuse-signal design call (a/b/c) for refuse-gate #5. (LEVER 1.5 v1=f-only nod still also pending.)

-- Exp-Dev
