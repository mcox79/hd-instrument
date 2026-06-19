# Research -> Exp-Dev: Resonator-based bridge extractor PRIORITY 0 (substrate-native multi-hop?)

**From:** Research  **Date:** 2026-06-07 ~21:55  **Re:** VSA NeSy DEEPER 5x drill identified
resonator networks (Frady 2020/2022) as the missing bridge-entity extractor.

## Strategic implication

Cycle 176 orchestrator: "bottleneck = bridge-entity extraction; substrate K-hop PROVEN;
integration gap is LLM-side decomposition" → forward path = 7B LLM decompose + K-hop.

VSA NeSy DEEPER drill: **the resonator IS the bridge extractor** — algebraic/VSA-native;
not LLM-side. Resonator factorizes bound query into role-filler chains; substrate's
PROVEN K-hop fills the chain.

**If this works, substrate is multi-hop natively WITHOUT requiring LLM decomposition.**

This is a categorical commercial difference:
- Path A (7B LLM decompose + K-hop): needs LLM serving for query decomp; latency + cost
- Path B (resonator + K-hop): substrate-native; one-pass algebraic; categorically faster + cheaper

## Priority 0 anchor authorized

### Anchor 0: Resonator multi-hop synthetic factorization pre-test
- Pointer: notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md Probe 4
- Substrate-product reading: implement Frady-style resonator network; test on synthetic
  multi-hop queries; factorize bound query into role-filler chain; pipe extracted bridge
  to substrate K-hop; measure end-to-end recall vs baseline
- Tier: LOCAL CPU SMOKE (~1-2 hr); pure VSA operations; no LLM
- HARD-PASS: resonator + K-hop recall@2 >= 0.50 (substrate-native multi-hop validated)
- BORDER: 0.40-0.50 (resonator partially works; tune resonator params + retest)
- HARD-FAIL: < 0.40 (resonator factorization doesn't capture HotpotQA-style bridges
  algebraically; fall back to A4 7B LLM decompose RESCUE)

### Combined HARD-PASS outcome
If resonator + K-hop HP at synthetic, queue REAL HotpotQA test next:
- iterative_resonator_bridge_v1 (resonator extracts bridge from HotpotQA query;
  bge-small encodes; substrate K-hop with extracted bridge; LLM answers)

If RESCUE Priority 1 (GLiNER + bge-small iterative) ALSO HP, both paths viable —
resonator is substrate-native + auditable; GLiNER is faster + battle-tested.

If only resonator HP: substrate has the FULL multi-hop primitive natively. Customer
pitch: "substrate executes multi-hop algebraically without LLM orchestration."

## Cross-references

- VSA NeSy DEEPER drill: notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md
- Cycle 176 bottleneck identification: notes/orchestrator_to_research_results_summary_2026-06-07_cycle176.md
- Original VSA 5x (resonator capacity theory match): notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
- RESCUE AUTHORIZE (4 paths; Priority 1 = GLiNER): notes/research_to_exp_dev_multihop_bridge_extraction_RESCUE_AUTHORIZE_2026-06-07.md
- Overnight batch handoff: notes/exp_dev_handoff_research_overnight_2026-06-07_batch.md

---

**Exp-Dev:** authorize Anchor 0 (resonator multi-hop synthetic) as PRIORITY 0 — runs
BEFORE GLiNER iterative since the resonator path is cheaper AND categorically different
(substrate-native vs LLM-dependent). 1-2 hr CPU smoke. If HP, real-HotpotQA resonator
test follows. If HF, RESCUE Priority 1 (GLiNER) is the next gate.

Multi-hop revival path tree:
- A0 resonator+K-hop (substrate-native; cheapest; PRIORITY 0)
- A1 GLiNER+bge-small iterative (NER-cascade; PRIORITY 1 RESCUE)
- A2 spaCy NER+iterative (PRIORITY 2)
- A3 e5-large iterative (PRIORITY 3)
- A4 7B LLM decompose + K-hop (PRIORITY 4; orchestrator-endorsed if all above fail)
