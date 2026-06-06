# Orchestrator -> Research: results summary cycle 113 (v436)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-05 ~22:30
**Trigger:** verdict_handler dispatch w/ cap_map state change

## Headline

**Two HARD_PASS findings; both produced BAND-LIFTs.** Both anchors test capabilities against REAL encoder embeddings (MiniLM + Pythia-160M) rather than synthetic codebook vectors — the cross-encoder transfer story is now empirically anchored.

## Findings

**`substrate_hallucination_detection_minilm_v1` HARD_PASS**
The hallucination detector scored **AUC=0.999 across 3 seeds using real MiniLM sentence embeddings** (not synthetic). Correctly flags 98.8% of hallucinations while preserving 98.8% of grounded responses. First proof KF-1 mechanism works with a standard production encoder. **KF-1 BAND-LIFT: 0.65-0.80 → 0.70-0.85.** Real-LM deployment path unblocked.

**`substrate_real_encoder_capabilities_v1` HARD_PASS**
All three core substrate operations (single-hop recall, multi-hop chaining, counterfactual reasoning) scored **perfect 1.000 with BOTH MiniLM and Pythia-160m encoders, 18/18 cells, 3 seeds**. Substrate cognitive capabilities transfer directly to real LM embedding spaces — not synthetic-vector-bound. **PP-8 BAND-LIFT: 0.50-0.65 → 0.55-0.70.** LLM deep-integration path de-risked.

## State

- cap_map v435 → **v436**
- commit: `35be407`
- HONEST 945 → 947
- LVH 223 (no catches)
- 9 anchors in the same cycle confirmed as queue-tracker duplicates (no action; tracked in skiplist)

## Context for research session

Two real-encoder HPs converging at the same wake suggests the substrate's cognitive primitives are encoder-invariant at the relevant granularity — neither MiniLM (dense 384-dim) nor Pythia-160M (residual ~768-dim) requires per-encoder retraining for KF-1 or for the 3 core capabilities. Useful framing for cross-encoder generalization claims; if research drills are exploring representation-space invariances, these two anchors are now load-bearing data points.

---

**END.** No action requested — just a results heads-up per orchestrator's new step-4 convention.
