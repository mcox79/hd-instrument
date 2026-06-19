# Prereg: ner_4type_conll_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research Action 1 (research_to_exp_dev_NER_PATH1_REFUTED_FEATURES_NEXT_2026-06-11).

## Motivation
Decisive on whether the 0.58 18-type NER F1 was largely 18-way difficulty (apples-to-oranges vs CoNLL-2003 4-type 0.65 target)
or a genuine feature gap. Collapse OntoNotes 18-type -> CoNLL-2003 coarse scheme (PER/ORG/LOC/MISC) and re-run the same
structured-perceptron Viterbi.

## Mapping (verified conll2012_ontonotesv5 tag order; type_id=(tag-1)//2)
- PER  <- PERSON
- ORG  <- ORG
- LOC  <- GPE, LOC, FAC
- MISC <- NORP, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE
- O (dropped) <- DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL (numeric/temporal; not in CoNLL-2003)

NOTE: dropping numeric/temporal types is correct for CoNLL-equivalence, but those types are EASY in OntoNotes and may have
inflated the 18-type aggregate -- so the CoNLL-equivalent named-entity F1 could land BELOW 0.58 (= genuine feature gap, not rescue).

## Pre-registered verdict (diagnostic; NO defeat)
- HARD_PASS F1 >= 0.70: much of 0.58 was 18-way difficulty; CoNLL-equivalent competitive; re-baseline.
- MIDDLE_BAND 0.62-0.70: coarsening helps but a real feature gap remains; proceed Path 2.
- HARD_FAIL < 0.62: genuine feature gap; build Path 2 substrate Brown-cluster features.

Companion: ner_singletype_boundary (full boundary-F1=0.664; type-confusion cost +0.082).
