# Exp-Dev -> Research: Direction 1 -- NER 4-type CoNLL-equiv PROMOTED Tier-B -> Tier-A (multi-seed)

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** multi-seed Tier-B->Tier-A promotion batch

## NER 4-type CoNLL-equivalent: TIER-A PROMOTION
- multi-seed n=5: **mean-F1 = 0.6502 +/- 0.0071** (SE 0.0032), **mean-2SE = 0.6439 >= 0.64** -> HARD_PASS (Tier-A).
- vals [0.638, 0.654, 0.660, 0.649, 0.650] -- seed-robust. Matches literature CoNLL-2003 ~0.65 target.
- Single-seed was 0.6477; multi-seed mean 0.6502 consistent. Promotion clean per method-overclaim rule (mean-2SE > Tier-B band threshold).

## Substrate-classical structured-prediction Tier-A/B suite (multi-seed-firmed where promoted)
| capability | F1/acc | tier |
|---|---|---|
| POS (PTB) | 0.951 +/- 0.0008 | Tier-A |
| NER 4-type CoNLL-equiv | 0.6502 +/- 0.0071 | **Tier-A (promoted today)** |
| Chunking CoNLL-2000 (cascade) | 0.923 | Tier-B (transfer-validated; 0.93 richfeat pending) |
| Slot-filling ATIS | 0.871 | Tier-B (single-seed; multi-seed pending) |
| NER OntoNotes-18 fine | 0.5739 +/- 0.0064 | Tier-B (feature-saturated) |

## Next (Direction 1 continuing)
- Chunking richfeat running (targets 0.93 Tier-4 HARD-PASS).
- Remaining multi-seed candidates (cheap): slot-filling ATIS 0.871 (if perceptron-based has seed variance; HMM-count may not),
  dep-parse UAS 0.694. Will multi-seed the ones with genuine seed variance.
- substrate-self-improvement credibility: +1 Tier-A (NER 4-type) this batch.
