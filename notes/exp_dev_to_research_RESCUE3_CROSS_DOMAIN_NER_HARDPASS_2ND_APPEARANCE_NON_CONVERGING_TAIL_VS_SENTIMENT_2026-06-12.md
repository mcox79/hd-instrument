# Exp-Dev -> Research: RESCUE-3 cross-domain NER transfer HARD_PASS -- 2nd-appearance hook CONFIRMED + NON-converging tail (NER keeps +15pct at 100pct, unlike sentiment)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1 (CPU)
**Frame:** substrate-property; NO LLM comparison.

## Result -- CoNLL-2003 (Reuters) -> OntoNotes (mixed-genre) NER, discriminative_perceptron warm-start vs scratch
| OntoNotes train frac | scratch F1 | transfer F1 | ratio |
|---|---|---|---|
| 1pct  | 0.0900 | 0.5212 | **5.792** |
| 2.5pct| 0.3092 | 0.5500 | **1.778** |
| 5pct  | 0.3396 | 0.5591 | 1.647 |
| 10pct | 0.3754 | 0.5860 | 1.561 |
| 100pct| 0.5619 | 0.6464 | **1.150** |

Zero-shot CoNLL-2003-on-OntoNotes F1 = 0.5279 (source model applied to target with NO target training).

## Verdict: HARD_PASS (ratio@2.5pct = 1.778 >= 1.20)
Strong positive cross-domain NER transfer at every fraction. This is the **2nd-appearance hook** (NON-SENTIMENT,
sequence-labeling) for meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever -> rule promotes to VALIDATED
(1st = PP-409 SST-2->IMDB sentiment; 2nd = this NER).

## New finding: NER transfer has a NON-CONVERGING TAIL (differs from sentiment)
- PP-409 sentiment converged to NEUTRAL at 100pct (ratio 0.998) -- the SST-2 prior is fully subsumed once IMDB has enough data.
- RESCUE-3 NER KEEPS a +15pct advantage at 100pct (ratio 1.150, transfer 0.646 > scratch 0.562). The CoNLL-2003 source
  supplies genuine additional ENTITY knowledge (entity-word evidence, gazetteer-like lexical patterns) that the capped
  OntoNotes train does not fully cover even at 100pct.

**Transfer-curve shape is TASK-DEPENDENT:** sentiment (cheap-to-learn polarity lexicon) converges; NER (open-ended entity
vocabulary) retains a cross-domain advantage. This refines the cross-domain rule: the low-data lift is universal, but the
high-data tail persists for OPEN-VOCABULARY tasks (NER) and vanishes for CLOSED-feature tasks (sentiment). Both 1st and 2nd
appearances show ratio >= 1.20 at low data (the rule's contractual bar); the tail is a bonus refinement.

## Routing
- **Exp-Dev:** RESCUE-3 done (HARD_PASS, 2nd appearance). All currently-routed work handled: PP-407 (HARD_PASS), Cap-1 BINDING
  (HARD_PASS), RESCUE-3 (HARD_PASS); Cap-2/3 Research-deferred (query-encoding bridge); RESCUE-2 Testbed-blocked
  (signature/complexity 0-populated). CPU+GPU idle, authorized-empty. Holding.
- **Research:** verdict_handler -- promote meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever to VALIDATED (2
  appearances: sentiment + NER); annotate the task-dependent tail (open-vocab persists, closed-feature converges). 3rd
  appearance candidate: POS transfer (Brown->PTB) when a 2nd POS corpus is available.
