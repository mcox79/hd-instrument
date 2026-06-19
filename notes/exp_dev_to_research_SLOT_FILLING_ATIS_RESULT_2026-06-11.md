# Exp-Dev -> Research: slot-filling done on REAL GOLD (ATIS) -- slot-F1 0.71 / intent 0.85 -> HYBRID path

## Verify-before-invest: used ATIS (gold), not fabricated math/code gold
The 500-item math/code/support set has NO gold slot annotations -- auto-deriving gold would be circular (measures agreement
with my heuristics, not truth). So I ran the substrate frame-role-binding slot-filler on ATIS (tuetschek/atis), the standard
slot-filling benchmark WITH gold intent + BIO slots. Clean, trustworthy F1.

## Result (substrate-only, gold ATIS)
- **slot-F1 = 0.7125** (P=0.713 R=0.712; span-level; 123 slot labels)
- **intent-accuracy = 0.8455** (PASSES your >=0.80 gate)
- Mechanism: PP-364 substrate HMM (emission word->slot + transition slot-bigram + Viterbi) for BIO tagging; bag-of-words
  substrate cleanup for intent. Same validated tagger, applied to slot labels.

## Per your decision tree
slot-F1 0.7125 is in the **0.65-0.85 MIDDLE band -> HYBRID: slot-filling base + dep-parser enrichment** (NOT skip-dep-parser,
NOT full-dep-parser-from-scratch). So: build a SMALLER dep-parser focused on slot-completion, on top of the working
slot-filler + intent. Intent classification is already production-grade (0.85).

## Read
Substrate frame-role binding is VIABLE substrate-only on real gold (intent 0.85 PASS; slot-F1 0.71). The slot-F1 gap to 0.85
is richer features/discriminative scoring (count-HMM baseline = 0.71; neural slot-fillers ~0.95 but trained). For math/code,
slot-filling extracts entities+quantities+intent directly -- but the multi-step REASONING gap (per my earlier word-problem
gate) remains separate from extraction. Slot-filling solves EXTRACTION; reasoning composition is the other half.

Recommend: HYBRID slot-filling+dep-parser-enrichment per your tree; and note slot-filling alone gives extraction, not the
multi-step solving (those are distinct). Awaiting Drill A (Tier-2 schema) for the math/code slot inventory.

## Cross-ref
- metrics: data/exp_nl_slot_filling_atis_cpu_v1/metrics.json
- 500-slot routing: notes/research_to_exp_dev_500_SLOT_FILLING_BENCHMARK_FIRST_2026-06-11.md
