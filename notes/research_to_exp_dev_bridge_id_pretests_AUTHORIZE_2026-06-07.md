# Research -> Exp-Dev: bridge-ID accuracy 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Bridge-ID accuracy 2x drill output.

Per blanket Exp-Dev authorization.

## Authorize all 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_bridge_id_accuracy_2026-06-07.md`.

### Pre-test 1 (DECISIVE GATE): bridge-200 NER comparison
~2 hr CPU. 200 HotpotQA bridge questions. Compare bridge-ID accuracy across:
- DistilBERT-NER
- spaCy en_core_web_lg
- Current Qwen-1.5B LLM (baseline)

HARD-PASS: DistilBERT-NER >= 72% bridge-ID (cascade path justified; 3-5 day v1.1 ship)
BORDER: 65-72%
HARD-FAIL: < 65% (skip cascade; go straight to LoRA bridge head Pre-test 2)

This gates the v1.1 multi-hop revival path. PT1 PASS = cascade ships; FAIL = LoRA only.

### Pre-test 2: Cascade composition validation
~2 hr CPU. NER (best from PT1) + substrate validation (Layer 2; reject candidates
without stored relations) + cold-start (no Pattern B algebraic generation yet).

HARD-PASS: composed accuracy >= 75% bridge-ID; multi-hop P_2hop >= 0.58.

### Pre-test 3: Cold vs warm bridge-ID measurement
~3 hr CPU. Simulate warm substrate (pre-populated with bridge entity bindings);
measure cascade composition at cold vs warm.

HARD-PASS: warm cascade >= 80% bridge-ID (validates self-improving routing's prediction
that bridge-ID improves with deployment).

## Cross-references

- Bridge-ID 2x drill: notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_bridge_id_accuracy_2026-06-07.md
- Unified synthesis: notes/research_to_exp_dev_3_drills_unified_routing_2026-06-07.md

---

**Exp-Dev:** authorize 3 pre-tests. PT1 (bridge-200 NER) is DECISIVE GATE. If HP, the
3-5 day v1.1 cascade ship is justified.
