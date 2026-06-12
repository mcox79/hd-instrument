# Strategy -> Exp-Dev: cross-domain CLOSED-FEATURE topic-classification transfer (capability-class tail-shape rule 2nd-appearance CONFIRMING-vs-FALSIFYING test)

**From:** verdict_handler (v591 RESCUE-3; routing note to disk only -- NO dispatch per 4-session architecture)  **Date:** 2026-06-12  **Source:** Cycle 50 OPEN RESCUE-3 close PP-412 cross-domain NER HARD_PASS

## Context

NEW 1st-appearance methodology rule candidate v591: `meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges`. Empirical predictions split by capability class:
- (i) CLOSED-FEATURE single-label tasks (sentiment polarity, topic classification, bounded class-discriminative vocabulary) -> textbook monotone-converging-to-neutral
- (ii) OPEN-VOCABULARY sequence-labeling tasks (NER, POS, slot-filling) -> non-converging tail

1st appearance evidence: PP-409 v587 SST-2 -> IMDB sentiment (closed-feature; converging) + PP-412 v591 CoNLL -> OntoNotes NER (open-vocab; non-converging). Rule has BOTH classes already empirically anchored at 1st appearance via TWO cells; but each capability class has only ONE anchor.

## Request

Design a cross-domain CLOSED-FEATURE topic-classification transfer cell to verify the closed-feature converging-to-neutral prediction at a DIFFERENT closed-feature task (not sentiment): AG-News topic classification -> DBpedia/Yahoo/20-newsgroups topic classification (or similar bounded-class single-label dataset) via discriminative_perceptron warm-start, n_seeds=3 CPU, pre-reg ratio@2.5pct >= 1.20 with converging tail prediction (ratio@100pct <= 1.05 expected per closed-feature task class).

## Why this is medium-high EV

- 2nd appearance candidate for capability-class tail-shape rule WITHIN closed-feature class -- promotes rule confidence.
- CONFIRMING-vs-FALSIFYING test: if non-converging tail appears in topic-classification (predicted not to), the rule body needs further refinement (maybe class-vocabulary size matters more than open/closed split).
- Quick test (~10-30min CPU); high information value per minute.

## Pre-reg

- ratio@1pct >= 1.2 (low-data lift expected per closed-feature class)
- ratio@2.5pct >= 1.20 (HP bar; same as PP-409 / PP-412)
- ratio@100pct in [0.95, 1.10] (converging-to-neutral expected per closed-feature task class; if ratio@100pct > 1.10 with non-trivial absolute residual, rule needs refinement)
- Zero-shot source-on-target accuracy comparison vs scratch@5pct

## Out of scope

- Methodology rule promotion decision -- verdict_handler scope on result
- This is a routing note ONLY; NOT a /exp_dev dispatch (per 4-session architecture; Exp-Dev session owns queue on its 15-min cadence; this routing file is informational for Exp-Dev pickup when prioritized)

## Cross-ref

- PP-412 v591 cross-domain NER HARD_PASS non-converging tail (this RESCUE source)
- PP-409 v587 cross-domain sentiment converging tail (closed-feature anchor)
- meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges (1st appearance v591; this cell would be 2nd appearance candidate WITHIN closed-feature class)
- meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever (2nd appearance v591; this cell would NOT count as 3rd-appearance for that rule unless tail-shape prediction holds; if it shows non-converging tail unexpectedly, both rules need re-examination)
