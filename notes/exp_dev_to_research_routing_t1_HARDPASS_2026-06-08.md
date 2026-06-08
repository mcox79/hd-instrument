# Exp-Dev -> Research: LLM-ROUTING-T1 HARD_PASS -- capability separation via tool-use is viable (Recipe 6.1)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** llm_capability_separation handoff anchor #1 (run-first gate)

Qwen-2.5-3B-Instruct routes structured-vs-language queries at 0.833 zero-shot (balanced: ROUTE-recall 0.83, DIRECT-recall 0.83,
n=12 smoke; full set 30). HARD_PASS (>=0.70). Validates the V1 product thesis: LLM = language layer, substrate = knowledge layer,
coupled by TOOL-USE -- the LLM correctly decides when to call the substrate. This is Recipe 6.1 (no architecture surgery, highest
confidence, V1-ready) and is exactly what Panel A already does -- so this empirically de-risks the shipping demo's routing layer.
Few-shot prompting would likely push it higher; zero-shot 0.83 is already past the gate. Contrast with Tier-5b (in-WEIGHTS
injection) which is hard R&D: the tool-use path is the pragmatic V1 separation, in-weights is the v2.0 upgrade. Downstream
routing anchors (3B knowledge-grounded answer quality with substrate facts in-context) are the natural follow-ons, pause-gated.
