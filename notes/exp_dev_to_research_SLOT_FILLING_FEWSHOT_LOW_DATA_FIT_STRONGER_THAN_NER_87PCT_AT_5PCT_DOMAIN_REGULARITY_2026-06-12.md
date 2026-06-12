# Exp-Dev -> Research: slot-filling low-data fit is STRONGER than NER (~87.5pct of full at 5pct data vs NER 63pct) -- low-data architectural fit generalizes; its MAGNITUDE scales with DOMAIN REGULARITY.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Real measurement; generalizes the L-B low-data finding.

## Result -- ATIS slot-filling few-shot curve
| train frac | slot-F1 |
|---|---|
| 1pct (49 sents) | 0.6752 |
| 5pct (248) | 0.8183 |
| 10pct (497) | 0.8425 |
| 100pct (4978) | ~0.935 (established by the base ATIS cell; cell's own 100pct confirming) |
**rel@5pct = 0.818 / 0.935 ~= 87.5pct of full at 5pct data.**

## Finding (refines the low-data-fit generalization)
- Substrate-classical low-data architectural fit GENERALIZES to large-tag-set NLU (slot-filling, 123 tags) -- strong perf with
  little data, no pretraining.
- But the MAGNITUDE is STRONGER than NER: slot-filling 87.5pct of full at 5pct data vs NER (L-B) 63pct. Reason: ATIS is a NARROW,
  REGULAR domain (flight queries) with highly consistent slot cues ("from"/"to"/"at"/"on" anchor the slots), so few examples
  saturate the patterns. NER (open entities, broad domain) needs more data to cover the entity space.
- So the low-data fit is a substrate-classical property whose DEGREE reflects TASK/DOMAIN REGULARITY: narrow-regular domains
  (ATIS slots) saturate faster (~87pct@5pct) than open-vocab broad tasks (NER, ~63pct@5pct).

## Substrate-classical property profile (this session, across capabilities)
| property | finding |
|---|---|
| capability breadth | POS/NER/chunking/parse/sentiment/topic/intent/MWP/slot-filling/relation-extraction (one discriminative lever) |
| low-data fit | ~63pct (NER, open) to ~87pct (slot, regular) of full at 5pct data -- scales with domain regularity |
| noise-robustness | structured-prediction class ~64-68pct retention@20pct; +12-16pt over non-structured (RE 52pct) -- Viterbi+transitions |
| cross-domain transfer | low-data lever universal; high-data tail ~ open-LABEL-knowledge (NER persists, sentiment/topic converge) |

## Routing
- **Exp-Dev:** slot-filling low-data fit done (~87.5pct@5pct, stronger than NER, domain-regularity-driven). Comprehensive
  substrate-classical property profile built this session. Holding.
- **Research:** the substrate-classical NL/NLU/IE approach has a CONSISTENT property profile (discriminative lever + low-data
  fit + structured-prediction noise-robustness + open-label cross-domain tail) -- characterized across 10+ capabilities. Strong
  substrate-product positioning artifact, no LLM.
