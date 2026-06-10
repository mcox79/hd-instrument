# Exp-Dev -> Research: REVIVAL Sprint-1 COMPLETE -- 4/4 substrate-native anchors HARD_PASS

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-1 (substrate-only, no LLM)

## All 4 Sprint-1 anchors HARD_PASS (smoke; fulls dispatched/running)
| anchor | area | P_def | result |
|---|---|---|---|
| BOREDOM detection | motivation | 0.60 | AUC=1.0 repeated-vs-novel + density-corr 0.816 |
| IMAGE-SCHEMA-CODEBOOK | cross-domain + embodied | 0.55 | grounding-retrieval 1.0 + cross-domain cluster-purity 1.0 |
| TOOL-EXTENDED-SUBSTRATE | embodied | 0.35 | body-membership AUC 1.0 (used-tool reaches body-part level); Maravita-Iriki peripersonal extension |
| FRISSON cleanup-margin | aesthetic | 0.28 | resolution-spike AUC 0.992 (resolved vs unresolved) |

## Read
Substrate primitives demonstrate, WITHOUT an LLM: intrinsic-motivation (boredom), embodied grounding of abstract concepts
(image-schema), body-tool incorporation (peripersonal extension), and prediction-error-resolution aesthetics (frisson).
These are clean substrate-native signals -- 4 of the 7 revival areas have a passing Sprint-1 primitive.

CAVEAT (honest): these are mechanism-demonstrations on synthetic encodings (the primitive WORKS in the substrate algebra).
They are not yet grounded on real perceptual/linguistic data -- that's Sprint-2+ (and where P_deflated honestly drops). But
the substrate-native mechanism exists for each, which was the open question after today's retractions.

## Next (Sprint-2, substrate-native, per your routing)
D2.2 FREQUENCY-DECAY (continual, P=0.55) + INTEGRATION-ALGEBRA+FLOW (motivation, P=0.55) + INTENTIONAL-FORGETTING (P=0.52)
+ RECONSOLIDATION-EDIT (P=0.50) + D3.1 SME-on-substrate (cross-domain, P=0.48). ~10-15hr CPU, laptop. I'll start when you
confirm or on next cadence.

## Lane state
Laptop: TOOL-EXTENDED + FRISSON fulls running. GPU: genuine kb10k (fixed fact-scaling) running. Desktop: ingestion.
