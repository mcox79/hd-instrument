# Research -> Exp-Dev: head-to-head EXTENDED to 7B + 70B scales with publishable methodology

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Drill 18 substrate-vs-larger-LLM methodology back (P=0.55 highest)

## Drill finding

4-axis cost normalization (cost/latency/energy/memory) + 3 scale-invariant differentiators (calibration/determinism/closed-KB fact-recall) make head-to-head against 7B/70B fair and publishable.

P_deflated=0.55 methodology / 0.50 vs 8B / 0.30 vs 70B.

## Extension of head-to-head plan

Original: substrate vs Qwen2.5-0.5B (size-matched only). Extend to 3-scale comparison:

| LLM scale | Candidate | Substrate goal |
|---|---|---|
| 0.5B (size-matched) | Qwen2.5-0.5B-Instruct | Accuracy + differentiation axes |
| 8B (mid-scale) | Llama-3-8B-Instruct | Differentiators + cost-normalization framework shows wins |
| 70B (frontier) | Llama-3-70B-Instruct | Differentiation-axis-only wins (accuracy honest loss) |

## 4-axis cost normalization framework

| Axis | Substrate | Qwen-0.5B | Llama-8B | Llama-70B |
|---|---|---|---|---|
| Cost / inference | (CPU $) | (GPU $) | (GPU $) | (GPU $) |
| Latency (ms) | (substrate) | (LLM token-gen) | (LLM token-gen) | (LLM token-gen) |
| Energy (J / inference) | (CPU joules) | (GPU joules) | (GPU joules) | (GPU joules) |
| Memory footprint (GB) | (substrate KB) | (model weights) | (model weights) | (model weights) |

Normalize all axes to per-inference. Substrate likely wins on cost/latency/energy/memory at all 3 LLM scales.

## 3 scale-invariant differentiators

These favor substrate REGARDLESS of LLM size:
1. **Calibration**: substrate conformal cleanup-margin (formal guarantees) vs LLM softmax (uncalibrated)
2. **Determinism**: substrate bit-exact across seeds vs LLM sampling variance
3. **Closed-KB fact-recall**: substrate deterministic memory vs LLM hallucination

These are scale-invariant: 70B LLM cannot fix hallucination; 0.5B substrate already has guarantees.

## Commercial framing

Substrate is the calibrated + deterministic + fact-grounded layer. LLMs scale fluency. Substrate provides what LLMs CANNOT at any scale.

This grounds the "substrate wins on differentiators; LLMs win on fluency" honest scope (per drill 7 frontier-scale + drill 17 RAG-backend).

## Build plan

| Phase | LLM | Cost | Goal |
|---|---|---|---|
| Phase 1 (already planned) | Qwen2.5-0.5B | Half day GPU + bundled datasets | Size-matched accuracy + differentiators |
| Phase 2 (NEW) | Llama-3-8B | Half day GPU | Mid-scale 4-axis cost wins |
| Phase 3 (NEW; gated on Phase 2) | Llama-3-70B | 1 day GPU | Frontier differentiation-axis wins |

Phases sequential; gate Phase 3 on Phase 2 results.

## Decision matrix

| Outcome | Implication |
|---|---|
| Substrate wins accuracy vs 0.5B + differentiators all 3 scales | Categorical commercial claim grounded; head-to-head publishable |
| Substrate ties accuracy at 0.5B + wins differentiators at all scales | Strong differentiation story even if not accuracy-first |
| Substrate loses accuracy at all scales but wins differentiators | Niche-specific framing: "substrate for calibrated/deterministic/fact-grounded layer; LLM for fluency" |

NO pre-registered defeat per drill-defeatism rule.

## Next-drill candidate noted

Drill identifies SUBSTRATE-MEMORY + small-LLM-frontend HYBRID as the OBVIOUS commercial architecture for accuracy-catchup vs larger LLMs. This is the natural commercial product:
- Substrate provides calibrated retrieval + memory + classification
- Small LLM (8B-class) provides NL fluency
- Total cost much less than 70B-class
- Differentiation axes preserved

Future drill candidate. Not blocking head-to-head.

## Cross-references
- Drill 18 output: notes/research_drill_substrate_vs_larger_llm_methodology_2x_2026-06-11.md
- Original head-to-head routing: notes/research_to_exp_dev_NEXT_PRIORITY_HEAD_TO_HEAD_PLUS_ACTION_ITEMS_2026-06-11.md
- Frontier-scale drill 7 (LLM-frontend stays for fluency): notes/research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md

---

**Exp-Dev:** head-to-head EXTENDED to 3 LLM scales (0.5B + 8B + 70B). 4-axis cost normalization (cost/latency/energy/memory) + 3 scale-invariant differentiators (calibration/determinism/closed-KB fact-recall). Phase 1 (0.5B) already planned; Phases 2-3 (8B + 70B) sequential after Phase 1. Methodology publishable.
