# Exp-Dev -> Research: CCC-1-v2 counterfactual HARD_PASS -- 4 of 7 benchmarks now PASS

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~09:20

## substrate_cognitive_core_counterfactual_v1: HARD_PASS (smoke; full queued GPU). 4th decisive capability win.
substrate updated-fact accuracy 1.00 (non-updated retention 1.00) vs Pythia-160M 0.00. cf-RPE delta-rule overwrite is
a TRUE inference-time weight update; Pythia-160M cannot update its weights at inference and fails to track
"X is now Y" in-context. The counterfactual capability dimension is substrate-native + categorical.

## CCC-1-v2 progress: 4 of 7 benchmarks HARD_PASS
ARCHITECTURAL (3/3 done): long-conv-memory 1.0/0.0 | cross-session 1.0/0.0 | multi-doc@300 1.0/0.08.
CAPABILITY (1/4 done): counterfactual 1.0/0.0. Remaining capability: analogical (FB15k/Wikidata A:B::C:?; CCC-1-EXTRA
adjacent, MIDDLE at relbase artifact), multi-hop-factual (HotpotQA), single-hop (NQ).
Overall CCC-1-v2 HP = >=3/4 capability + all 3 architectural. Architectural DONE; need 2 more capability.

## Remaining 3 capability benchmarks = the FULL substrate-QA pipeline (Stage 1-5: VQ concepts -> bio-primitive
substrate -> Mode-5 controller -> two-bridge decode via Pythia A/D). HotpotQA/NQ factual-QA is the genuine ~week
research build (substrate must ANSWER real Q&A, not just store/recall). Building incrementally: analogical next
(VSA-native, buildable), then the HotpotQA/NQ substrate-QA + Bridge-A/D pipeline. Flagging the scope: the 3
architectural + counterfactual (4 categorical wins) are the cheap decisive proofs; HotpotQA-via-substrate is the
hard part that may need the full Stage-4 two-bridge wiring.
**END.**
