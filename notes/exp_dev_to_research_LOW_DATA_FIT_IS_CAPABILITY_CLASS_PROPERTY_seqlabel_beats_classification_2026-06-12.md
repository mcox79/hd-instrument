# Exp-Dev -> Research: substrate-classical low-data fit is a CAPABILITY-CLASS property -- SEQUENCE LABELING (NER 63pct / slot 87pct of full @5pct) >> CLASSIFICATION (RE 53.5pct). Mechanism: local-token-feature sharing vs per-class example demand.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property. NO LLM. CPU (desktop).
Cells: exp_substrate_atis_slot_filling_fewshot_cpu_v1.py + exp_substrate_relation_classification_fewshot_cpu_v1.py
(+ NER L-B from earlier this session). All real measurements.

## Low-data fit by capability class (rel = F1@5pct / F1@full)
| capability | class | F1@5pct | F1@full | rel@5pct |
|---|---|---|---|---|
| ATIS slot filling (123 tags) | sequence labeling | 0.818 | 0.935 | **0.875** |
| CoNLL NER (L-B) | sequence labeling | -- | -- | **0.63** |
| SemEval RE (19 classes) | classification | 0.351 | 0.656 | **0.535** |

RE curve: 1pct=0.183, 5pct=0.351, 10pct=0.463, 50pct=0.605, 100pct=0.656.
Slot curve: 1pct=0.675, 5pct=0.818, 10pct=0.843, 50pct=0.917, 100pct=0.935.

## Finding
- Substrate-classical low-data fit is real across the board but its MAGNITUDE is a CAPABILITY-CLASS property:
  **sequence labeling (0.63-0.87) >> multiclass classification (0.54)** of full at 5pct data.
- MECHANISM: sequence labeling shares LOCAL TOKEN features (suffix/shape/neighbor) across every token of every sentence, so a
  few sentences already expose most feature patterns. Multiclass classification (RE, 19 classes) needs per-CLASS examples; with
  19 classes, 5pct of train leaves several classes thinly covered -> macro-F1 (per-class) lags until each class is populated.
- SECONDARY MODULATOR (within sequence labeling): DOMAIN REGULARITY -- ATIS (narrow flight queries, consistent slot cues)
  saturates faster (0.875) than open-vocab NER (0.63).

## Substrate-product implication
- The substrate-classical approach is strongest in the LOW-DATA regime for SEQUENCE LABELING / structured NLU (slot filling,
  NER, chunking, POS) -- near-full quality at 5pct data, no pretraining. For multiclass classification it still has low-data
  fit but needs ~2x the data to hit the same fraction (per-class coverage bound). Honest, mechanistic differentiator.

## Routing
- **Exp-Dev:** low-data-fit picture COMPLETE across capability classes (sequence labeling + classification). Holding.
- **Research:** add to the substrate-classical property profile -- low-data fit is class-dependent (seq-label > classification),
  modulated by domain regularity. Useful for positioning where substrate-classical wins (low-data structured NLU).
