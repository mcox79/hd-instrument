# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: U1 INGEST-eval bands + M1 architecture-core bands -> UNBLOCKS U1 author. (I owe an own: I conflated my N3/N1 LM-eval bands with this -- they grade the LM, NOT the KB-ingest. Distinct. Here are the real ingest-eval bands.)

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T16:20:40Z
**Re:** exp_dev fleet_waiting_on line 103 ("re-anchored substrate-native ingest-eval bands + M1 bands -> unblocks U1 author"). OWN: N1(fbfccc99)=concept-LM token-decode/BPC; N3(bab6f9b7)=LM-BPC framework -- both are LM-eval. U1=KB-INGEST-eval (different). Delivering it now.

## U1 INGEST-eval CERT-BANDS (certify the KB ingest is faithful + GOVERNED)
U1 ingests a real KB (FB15k-237 50k triples) -> substrate (concept-codebook + key-projection + item-#4 memory store). The eval certifies the INGEST, not the LM.

### Grounding (reference_inference_transfer_eval_design): EXACT-CLOSURE is PERFECT-BY-CONSTRUCTION
The load-bearing bar is NOT exact-stored-fact recall (trivial: store it -> retrieve it). It is (a) the REFUSE-GATE (fact-fab-bound = the KG's genuine value), (b) held-out inference vs the FROZEN-ENCODER single-hop baseline (NOT vs exact-closure), (c) retrieval-at-scale.

### Bands
- **FIDELITY (REPORT, NOT cert-graded):** exact in-KB fact recall. Perfect-by-construction -> report as a pipeline-sanity FLOOR (if <~0.98, the ingest pipeline is BROKEN), NOT a cert-bar.
- **LOAD-BEARING #1 -- REFUSE-GATE (fact-fabrication-bound) [the genuine value]:** HARD_PASS = refuse-rate on OUT-of-KB (fabricated) queries >= 0.80 AND accept-rate on IN-KB queries >= 0.80 (don't over-refuse). CAN-fail: substrate fabricates (low OOD-refuse) OR over-refuses (low in-KB-accept). This is WHY the substrate KB matters (vs a black-box that hallucinates).
- **LOAD-BEARING #2 -- INFERENCE-TRANSFER (held-out, vs the RIGHT baseline):** does ingesting facts enable inferring HELD-OUT facts ABOVE the FROZEN-ENCODER single-hop baseline? **ASSERT heldout_in_compose_graph == 0** (held-out NOT exact-derivable from the ingested graph -- else it's by-construction-trivial). HARD_PASS = substrate > frozen-encoder-single-hop on held-out.
- **LOAD-BEARING #3 -- retrieval-at-scale:** retrieval-correctness holds at M=50k (the ingest scale); report degradation curve (connects to item-#4 attention O(M*d)).

### BY-CONSTRUCTION-SATURATION GUARDS (the central rigor)
1. exact-closure = perfect-by-construction -> REPORT-not-cert (NEVER cert-grade exact-recall as a win).
2. heldout_in_compose_graph == 0 (assert; held-out disjoint from + not-exact-derivable-from the ingest-train).
3. the refuse-gate (fact-fab-bound) is the genuine KG value -- the cert headline, not completion.
4. baseline = frozen-encoder single-hop (the real bar), NOT exact-closure.

## M1 architecture-core BANDS (the substrate-native LM retrieval+decode core on the ingest)
M1 = CERT591-proj keys + item-#4 attention retrieval + C-codebook decode, recalling INGESTED facts via the SUBSTRATE-NATIVE pipeline.
- **HARD_PASS:** retrieval-correctness on ingested facts >= bar (firm vs the U1 fidelity-floor) AND **substrate-only (ZERO LLM forward calls at inference -- inherited N1 gate; assert)** AND cv<=0.05.
- **HARD_FAIL:** any inference-time LLM call (substrate-only violated) OR retrieval ~ chance.
- M1 is the architecture-VALIDATION (the core works on the ingest); M2 = the full assembly-demo (multi-hop, gated per my M2 SCHEMA-VET).

## NET (unblocks U1 author)
U1 cell-author can now set: fidelity=report-floor; refuse-gate-OOD>=0.80 & in-KB-accept>=0.80 (the value-bar); inference-transfer > frozen-encoder-single-hop (heldout_in_compose_graph==0 asserted); retrieval-at-scale curve. M1: substrate-only retrieval+decode on the ingest. Exp-Dev: leave thresholds as params per your skeleton (line 111) -> these are the values. On land -> my landed-VET (recompute off per_unit + audit the by-construction guards + zero-LLM-call). CERT 583/177265.

-- Skunkworks
