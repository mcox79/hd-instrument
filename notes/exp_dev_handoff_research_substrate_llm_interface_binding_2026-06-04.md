# exp_dev hand-off -- research: substrate-LLM interface compositional structure preservation

Filed-by: research sub-agent (2026-06-04)
Trigger: notes/research_drill_substrate_llm_interface_compositional_structure_preservation_2x_2026-06-04.md

Pause state: check data/orchestrator_paused.flag before dispatching any anchor.
Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the anchor sweep, grid,
threshold formulas, and queue choice autonomously. This file hands TASK + WHY + CONTRACT only.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIORITY): Bridge D vs Bridge A -- analogical reasoning at small LM
Why now: the algebraic argument (MHN = attention identity) predicts bridge D achieves >= 1.5x
  lift over text injection on VSA-encoded analogical triples. No empirical test exists.
  This is the cheapest decisive gate for the two-bridge hybrid product architecture.
  If bridge D fails (HF: accuracy ratio <= 1.0), the product architecture collapses to
  bridge A only (text injection), which is the conservative fallback already validated.
Substrate-product reading: two-bridge hybrid (A for factual, D for analogical/relational)
  unlocks relational reasoning as a substrate-native product feature, not just factual retrieval.
Tier hint: GPU smoke at Pythia-160M scale; no cloud needed.
Anchor pointer: bridge D = inject bipolar substrate retrieval as K/V pairs into ONE attention
  head of Pythia-160M at an intermediate layer. Compare to bridge A (text decode + prepend).
  Task: 50 VSA-encoded analogical triples (A:B::C:?). Metric: accuracy(D) / accuracy(A).
  HARD-PASS: >= 1.5x. HARD-FAIL: <= 1.0x.

### Anchor 2: Bridge C injection depth -- 0.4 vs 0.7 of L_max for compositional chains
Why now: MemLong injects at L=0.7*L_max; research drill predicts L=0.4*L_max is better
  for compositional chain depth K>=4 because more transformer layers can process the chain.
  The two depths are a minimal A/B test (1 extra condition above MemLong's validated point).
Substrate-product reading: if 0.4*L_max is confirmed, revise all bridge C injection targets.
  SQ2 K=12 chain transmission should use 0.4*L_max for maximum compositional depth.
Tier hint: CPU or GPU (Pythia-160M, K=4 compositional chains, 20 test cases).
Anchor pointer: vary injection layer depth (L=0.4 vs L=0.7 of L_max=24 for Pythia-160M).
  Metric: chain completion accuracy on 20 K=4 sequential binding chains.
  HARD-PASS: 0.4*L_max accuracy >= 1.2x 0.7*L_max. HARD-FAIL: ratio <= 1.05x.

### Anchor 3: Bridge B at concept vocabulary V_c=256
Why now: algebraic analysis shows bridge B IS viable when N >> V (N=8192, V_c=256).
  This would make bridge B the lowest-cost binding bridge (no attention layer modification).
  Connects directly to EX-CONCEPT-1 design space already in the pipeline.
Substrate-product reading: if bridge B works at concept vocab, the architecture is:
  substrate -> VQ concept codebook -> logit injection -> LLM. No attention surgery needed.
Tier hint: CPU; extends EX-CONCEPT-1 setup directly.
Anchor pointer: extend EX-CONCEPT-1 to test binding structure preservation in concept logit
  space. Encode 20 VSA concept triples; measure whether bridge B recovers them vs text injection.
  HARD-PASS: concept binding accuracy >= text +10%. HARD-FAIL: <= 0% improvement.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_llm_interface_compositional_structure_preservation_2x_2026-06-04.md
- Prior drill (communication, concept training): d:/AI/hd-instrument/notes/research_drill_substrate_llm_communication_and_native_concept_training_2x_2026-06-04.md
- D-RIP unified drill: d:/AI/hd-instrument/notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md
- VSA binding references: Ramsauer 2021 (arXiv:2008.02217), GHRR 2024 (arXiv:2405.09689),
  Attention-as-Binding 2025 (arXiv:2512.14709), Structure-Aware Attention (openreview zET0Zg71WT)
- MemLong injection layer data: arXiv:2408.16967 (L=13 memory layer, retrieval at L=14-26)

---

## Contract

exp_dev reads this file as a task brief. exp_dev designs anchor names, sweep grids, threshold
formulas, queue choice, and ETA autonomously. The WHY and the HP/HF bands above are guidance
from research -- exp_dev may revise bands based on cost/risk analysis.

If Anchor 1 (bridge D) returns HARD-FAIL, exp_dev flags to orchestrator and does NOT proceed
to Anchor 2 or 3 under the same session -- let orchestrator decide.

If Anchor 1 returns HARD-PASS or MIDDLE-BAND, proceed to Anchor 2 independently.

Anchor 3 can run in parallel with Anchor 1 if CPU capacity allows (no dependency).

## Autonomy declaration

exp_dev has full autonomy on implementation details, anchor naming, queue routing, and
ETA estimation. Do not encode sweep grids or numerical threshold formulas here per
[[feedback-no-experiment-design-in-prompts]].
