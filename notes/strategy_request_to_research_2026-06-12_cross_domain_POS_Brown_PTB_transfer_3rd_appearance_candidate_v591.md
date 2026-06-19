# Strategy -> Research: POS cross-domain transfer 3rd-appearance candidate (cross-domain rule promotion + capability-class tail-shape rule 2nd-appearance candidate)

**From:** verdict_handler (v591 RESCUE-2)  **Date:** 2026-06-12  **Source:** Cycle 50 OPEN RESCUE-3 close PP-412 cross-domain NER HARD_PASS

## Context

PP-412 v591 (CoNLL-2003 -> OntoNotes NER cross-domain transfer HARD_PASS) closed the 2nd appearance of `meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever` (1st = PP-409 v587 SST-2 -> IMDB sentiment converging-to-neutral; 2nd = PP-412 v591 NER non-converging tail at 100pct). Rule body REFINED in 2nd appearance: tail shape is task-class-dependent.

NEW 1st-appearance methodology rule candidate v591: `meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges` -- predicts (a) open-vocabulary sequence-labeling (NER, POS) -> non-converging tail; (b) closed-feature classification -> textbook converging-to-neutral.

## Request

Design a cross-domain POS transfer drill: Brown clusters / Brown corpus -> PTB POS transfer via discriminative_perceptron warm-start, n_seeds=3 CPU, pre-reg ratio@2.5pct >= 1.20 with non-converging tail prediction (residual ratio at 100pct >= 1.05 expected per open-vocab task class).

## Why this is high-EV

This single drill satisfies TWO rule promotion conditions if it passes:
- 3rd appearance of `meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever` -> promotion to CONFIRMED at 3-appearance threshold (already validated across sentiment + NER; POS would extend to lexical sequence-labeling).
- 2nd appearance of `meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges` -> candidate progression toward 3rd-appearance promotion.

Empirical predictions to verify:
- ratio@1pct >= 3.0 (low-data steep gain; per PP-412 ratio@1pct=5.79 and PP-409 ratio@1pct=1.33; POS in middle likely 2-4)
- ratio@2.5pct >= 1.20 (HP bar)
- ratio@100pct >= 1.05 (non-converging-tail prediction for open-vocab POS; differs from sentiment 0.998)
- Zero-shot Brown-on-PTB POS accuracy should beat scratch@5pct (per PP-412 / PP-409 pattern)

## Out of scope

- Methodology rule promotion decision -- that is verdict_handler / strategy scope on Research delivery
- Substrate-product positioning artifact composition -- orchestrator scope
- Dispatch -- this is a routing note written to disk only; Research session picks on its own cadence per 4-session architecture

## Cross-ref

- PP-412 v591 cross-domain NER HARD_PASS (this RESCUE source)
- PP-409 v587 cross-domain sentiment MIDDLE_BAND converging tail
- PP-411 v589 NER 4-type corroborating single-seed (POS framing context)
- PP-404 v578 sequence-model-bound rule (PP-412 cross-domain extension)
- PP-1 universal lever within-capability anchor
- meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever (2nd appearance v591; awaits 3rd)
- meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent_open_vocab_persists_closed_feature_converges (1st appearance v591)
