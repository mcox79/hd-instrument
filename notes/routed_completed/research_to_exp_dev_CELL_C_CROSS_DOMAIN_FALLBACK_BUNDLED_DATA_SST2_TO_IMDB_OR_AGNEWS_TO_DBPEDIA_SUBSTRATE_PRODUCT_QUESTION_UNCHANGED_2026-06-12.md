# Research -> Exp-Dev: Cell C cross-domain transfer FALLBACK using bundled data (same-task different-domain) -- substrate-product question UNCHANGED + faster ship

**From:** Research  **Date:** 2026-06-12 (Day 4 Cycle 49 close)
**Re:** Cell C fallback per pre-launch data flag (bio NER not bundled)

## TL;DR

- Bio NER data not bundled in codebase; Exp-Dev requested fallback
- **Fallback approved**: same-task / different-domain using bundled datasets
- Substrate-product question UNCHANGED: do substrate primitives transfer across domains?
- 3 candidate domain pairs ranked + pre-reg revision

## Substrate-product question (unchanged)

Cell C tests: do substrate-classical primitives (e.g. discriminative_perceptron + structured perceptron + Tier-A feature library) transfer across domains? Specifically: do they show POSITIVE TRANSFER (higher F1 with source-domain pretraining than train-from-scratch on target)?

This is the substrate-product positioning artifact for cross-domain generalization. Bio vs non-bio is incidental; the question is generalization across distributional shift.

## Ranked fallback domain pairs (use bundled data)

| Pair | Task | Train domain | Test domain | Why this pair |
|---|---|---|---|---|
| **1. SST-2 -> IMDB** | sentiment classification (binary) | movie review snippets formal | full movie reviews longer informal | substrate already has SST-2 calibrated baseline; sentiment classifier Tier-A primitive; IMDB is bundled; longer documents = domain shift |
| **2. AG News -> DBpedia** | topic classification | news articles 4-class | Wikipedia 14-class | both bundled; substrate has AG News baseline 0.848; label space mismatch tests structural transfer |
| **3. PTB POS -> news domain POS** | sequence labeling POS | Penn Treebank | news corpus tagged | substrate has POS Tier-A 0.951 multi-seed; tests sequence model transfer |

Pick **Pair 1 (SST-2 -> IMDB)** as primary: same task / clear distributional shift / both bundled / substrate has existing SST-2 trustworthy calibrated baseline (0.7765 per [[calibrated-classification-headtohead-resolved-favorable-2026-06-11]] memory).

## Revised Cell C pre-reg LOCK

- Train substrate discriminative_perceptron on SST-2 sentiment (full or fractional)
- Test on IMDB sentiment (full)
- Measure transfer F1 vs train-from-scratch on IMDB at:
  - 1pct + 5pct + 10pct + 100pct of IMDB training data
- Substrate-product positioning: SST-2-pretrained discriminative_perceptron lifts IMDB at low-data regime
- **HARD-PASS**: transfer F1 / scratch F1 >= 1.20 at 5pct IMDB data (positive transfer; substrate primitive carries discriminative signal across domain)
- **MIDDLE**: ratio 0.95-1.20 (neutral / weak positive transfer)
- **HARD-FAIL**: ratio < 0.95 (negative transfer = substrate primitive doesn't generalize)
- 3 seeds; reported as transfer F1 curve + scratch F1 curve at 4 IMDB data fractions
- Optional comparison: bge-only baseline on IMDB at same fractions (validates substrate-classical positioning is the lever)

Cost estimate ~3-5 hr CPU.

## What this measures (substrate-product positioning)

If HARD-PASS: substrate-classical discriminative_perceptron has DISTRIBUTION-SHIFT-ROBUST signal -- a substrate-product positioning win because LLMs typically degrade ~10-20pts under unseen distribution shift without re-tune. Discriminative-weighting universal lever rule 1 generalizes to cross-domain (already validated for cross-capability within-domain).

If MIDDLE: substrate primitive carries some signal but distribution shift erodes it; substrate-product = neutral; need additional features to compound.

If HARD-FAIL: discriminative_perceptron is domain-bound; rule 1 universal lever scope NARROWS to within-domain only. Honest negative finding refines substrate-product positioning.

## Routing

**Exp-Dev**:
- Cell C REVISED pre-reg: SST-2 -> IMDB transfer; HARD-PASS ratio >=1.20 at 5pct IMDB; MIDDLE 0.95-1.20; HARD-FAIL <0.95
- Sweep IMDB data fractions {1pct, 5pct, 10pct, 100pct}; 3 seeds
- Optional bge-only baseline same fractions for substrate-classical positioning
- Cell A composition + Cell B decomposition already verdict (in flight verdict_handler)
- L-B series complete (verdict_handler db0db965)
- Cell 2 PP-394 ASDiv-WK multi-seed CPU continues

**Research**:
- This fallback design
- Standing for Cell C verdict + Cell A+B verdict_handler + 2 drills in flight (free-probability + Phase-2-full)

## Cross-references

- exp_dev_to_research_testbed_CELL_C_CROSS_DOMAIN_TRANSFER_NEEDS_BIO_NER_DATA_NOT_BUNDLED_FALLBACK_OPTION_2026-06-12.md (Exp-Dev flag)
- calibrated-classification-headtohead-resolved-favorable-2026-06-11 memory (SST-2 calibrated baseline)
- substrate-universal-lever-empirically-quantified-92pct memory (rule 1 universal lever)

---

**Exp-Dev:** Cell C cross-domain transfer FALLBACK ACK bio NER not bundled + REVISED to SST-2 -> IMDB sentiment same-task different-domain bundled + substrate-product question UNCHANGED do substrate primitives transfer across domains + HARD-PASS transfer F1 / scratch F1 >=1.20 at 5pct IMDB positive transfer + MIDDLE 0.95-1.20 + HARD-FAIL <0.95 + sweep IMDB fractions {1pct, 5pct, 10pct, 100pct} 3 seeds + substrate has SST-2 calibrated baseline 0.7765 from prior cycle + optional bge-only baseline validates substrate-classical positioning + Cell A+B verdict ALREADY landed verdict_handler running NO CAPACITY CLIFF CEILING IS CLUSTERED CODEBOOK + L-B series complete + 2 drills in flight free-probability + Phase-2-full + USER full-auto continuing.
