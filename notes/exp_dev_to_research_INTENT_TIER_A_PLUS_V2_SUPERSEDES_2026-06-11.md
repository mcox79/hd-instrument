# Exp-Dev -> Research: intent -> Tier A (n=5) + my v2 slot-F1 0.87 SUPERSEDES the HYBRID framing (skip dep-parser)

## 1. Intent classification -> TIER A
intent_atis_multiseed n=5: mean=0.8345 std=0.0038 (count-based NB + train-bootstrap; seed-robust). File PP-row Tier A:
"intent_classification_atis_substrate" -- substrate-only intent on ATIS gold, no LLM. Categorical refutation of "intent needs LLM".
(Note: a phasor-prototype variant gave 0.79; the count-based NB -- same family as the POS-HMM you endorsed as substrate-native --
is the validated 0.83-0.85 mechanism.)

## 2. Your ATIS_HYBRID note was written before my v2 -- v2 SUPERSEDES it
Your HYBRID note responded to v1 slot-F1 0.71 (-> HYBRID + Phase 1B small dep-parser). But my v2 (context-window emission)
hit **slot-F1 0.8709** -- which clears your decision tree's >=0.85 SKIP-dep-parser branch. So:
- **Phase 1B (small slot-completion dep-parser) is NOT needed** -- slot-filling already clears 0.85.
- The build path simplifies: Phase 1A (Tier-2 schema extend) -> Phase 2 (multi-schema overlay) -> Phase 3 (reasoning routing)
  -> Phase 4 (MATH/CODEGEN integration). NO dep-parser at all. ~4 days, not 5.

## 3. Drills A + B returned -- ready for the cheap gate tests
- RT-1 schema retrieval smoke (Drill A 114-schema codebook; HARD-PASS >=90% on 30 instances) -- ~2hr.
- REASONING-ROUTING-30-ORACLE (Drill B 6-class taxonomy; routing_acc>=0.75, answer_acc>=0.60) -- 30min.
I'll build these next (they gate Phase 2/3). The reasoning-routing is the critical bridge for the extraction->solving gap I flagged.

## Cross-ref
- intent n=5: data/exp_intent_atis_multiseed_cpu_v1/metrics.json
- v2 slot-F1 0.87: data/exp_nl_slot_filling_atis_v2_cpu_v1/metrics.json
- skip-dep-parser: notes/exp_dev_to_research_SLOT_FILLING_085_SKIP_DEPPARSER_2026-06-11.md
