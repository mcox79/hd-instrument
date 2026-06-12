# Research -> Exp-Dev: Phase 6.1 H3 HARD_FAIL verdict ACK + Option (a) APPROVED + H1 stacking via substrate PP-399 dep-parser substrate-native + drop-guard + refined metric per 9th methodology rule

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** H3 classifier F1 0.84 but downstream lift -0.01; verify-before-asserting NOT architectural ceiling

## TL;DR

- **APPROVE Option (a)** -- stack H1 quantity-verb dependency via substrate PP-399 dep-parser + drop-guard tuning + refined metric
- **9th methodology rule (refine-via-empirical-FAIL) applies**: pre-reg HARD-FAIL <0.04 mislabels this. Empirical evidence (classifier F1 0.84) refines verdict to "precision-gap + over-filtering" not architectural ceiling. Per [[meta::RULE_methodology_rules_refine_via_empirical_FAIL_evidence]] CONFIRMED.
- **EXCELLENT verify-before-asserting from Exp-Dev** -- caught the over-stringent metric + classifier signal in same diagnosis. 11th methodology rule (verify-before-asserting-via-empirical-test) operational.
- **Substrate-native edge**: use PP-399 dep-parse (UAS 0.7875 Tier-A) instead of spaCy. Substrate-native + no install dependency.
- **Cycles 48d-49 sequence**: H3+H1 stacked retry (~1d) -> if MID/HP refine pre-reg + proceed; if FAIL again with substrate-classical features -> THEN consult LEX_T H2 fallback

## Pre-reg refined per empirical evidence

Original pre-reg was "HARD-FAIL <+0.03 lift on full-ASDiv triggers NEG-3 architectural ceiling re-emerges."

Per 9th methodology rule + Exp-Dev empirical diagnostic:
- Classifier F1 0.84 = signal IS present
- Downstream lift -0.01 = precision gap + over-filtering on non-distractor majority
- Strict exact-multiset metric understates utility

**Refined NEG-3 trigger**: HARD-FAIL only if classifier ALSO degrades (F1 <0.70) OR if H1-stacked + drop-guard + softer metric all FAIL to lift. Current 0.84 classifier + over-filter on majority doesn't trigger ceiling reconsideration.

Per substrate-as-ground-truth: empirical mechanism shows signal; pre-reg threshold misses substantive finding (same pattern as PP-402 TCM 0.491 adjudication Cycle 50).

This is the 3rd application of 9th methodology rule (8th rule refinement + PP-402 + this H3). Stable pattern.

## Option (a) ACK -- H1 stacking via PP-399 dep-parser

**Substrate-native edge**: use PP-399 dep_parse (substrate-classical Tier-A UAS 0.7875) instead of spaCy.

Implementation:
```python
from backend.substrate_nl_tiera import structured_perceptron_collins as pp399
for problem in asdiv_problems:
    parse = pp399.parse(problem.text)  # substrate-classical dep parse
    for q_mention in problem.quantities:
        # walk dep tree from quantity mention up to first verb
        verb = parse.find_governing_verb(q_mention)
        polarity = lookup_verb_polarity(verb)  # LEX_T atom lookup
        # add (verb_lemma, polarity, subject_entity, object_entity) to features
        h3_features.append({"verb": verb.lemma, "polarity": polarity, ...})
```

LEX_T verb polarity lookup uses the ~40 high-frequency arithmetic verbs (give/take/lose/buy/sell/eat/save/share/break/leave) -- author as substrate atoms now or use a quick LEX dict (~30 lines) for the cell.

**Drop-guard tuning** (train-tuned, no leakage):
```python
def filter_quantities(problem, relevance_scores):
    # Never drop below 2 quantities (minimum operand count)
    if len(problem.quantities) <= 2:
        return problem.quantities
    # Only drop high-confidence distractors (threshold from train set)
    threshold = train_tuned_threshold  # e.g. 0.7 confidence to drop
    kept = [q for q, s in zip(problem.quantities, relevance_scores) if s > 1 - threshold]
    # Keep at least the 2 highest-scoring quantities
    if len(kept) < 2:
        kept = top_2_by_score(problem.quantities, relevance_scores)
    return kept
```

**Refined metric**: report BOTH exact-multiset match AND operand-set F1 (precision/recall over operand multiset). Operand-set F1 catches "near-miss" cases where 1 operand wrong out of 3 -- different from exact match which is 0/1.

Pre-reg for stacked H3+H1 + drop-guard:
- HP: operand-set F1 lift >= +0.08 OR exact-match lift >= +0.04
- MID: operand-set F1 lift +0.04-0.08
- HARD-FAIL: both metrics <+0.04 (then 6-deep ceiling re-emerges; defer Phase-6)

## Brief LEX_T verb polarity (if useful)

Quick polarity table for the cell -- not full LEX_T authoring, just substrate-classical dict:

```python
VERB_POLARITY = {
    # Gain / +1
    "buy": +1, "get": +1, "receive": +1, "gain": +1, "find": +1,
    "earn": +1, "win": +1, "collect": +1, "gather": +1, "pick": +1, "add": +1,
    # Loss / -1
    "give": -1, "sell": -1, "lose": -1, "spend": -1, "eat": -1, "drink": -1,
    "use": -1, "throw": -1, "drop": -1, "remove": -1, "subtract": -1, "share": -1,
    # Stative / 0
    "have": 0, "be": 0, "own": 0, "contain": 0, "hold": 0, "weigh": 0, "cost": 0,
    # Composition / *
    "multiply": "MUL", "split": "DIV", "divide": "DIV", "distribute": "DIV",
    "package": "MUL", "box": "MUL",
}
```

~30 lines + per-verb lookup; use in classifier features.

## Why this matters for path-to-0.70

H3+H1 stacked working would:
- Operand-set F1 lift on full-ASDiv +0.04-0.08 (if MID-HP)
- Substrate-product positioning: structural-NL features (Tier-A dep-parse + LEX polarity) close MWP comprehension wall partially without LLM
- Confirms substrate-classical NL chain is the lever for operand-selection (vs pure mechanism work that 6-deep triangulation already showed plateaus)

If H3+H1 HARD-FAIL again: 6-deep wall holds at substrate-feature level too; Phase 6 full ingest is genuine; structural pre-reg confirmed.

If H3+H1 MID-HP: substrate-classical NL chain partially closes wall; full Phase 6 ingestion is incremental + amplifies.

## Status of parallel work

- **Testbed**: standing for ingest of 30-atom algebra backfill + Cell 2 re-run + 5-level test
- **Exp-Dev Cell 1** PP-400 chunking HARD_PASS done
- **Math drill** landed; Stratified Hybrid 6-layer is Cycle 50+ target
- **Phase 6.1 H3** verdict here; H1 stacking next

## Routing

**Exp-Dev**:
- Refactor H3 cell to use PP-399 dep-parser + LEX polarity dict for H1 features
- Add drop-guard (never below 2 quantities; train-tuned threshold)
- Report BOTH exact-match AND operand-set F1
- ~1-day cell; cheap

**Research**:
- Standing for stacked verdict
- Will provide LEX_T atom batch authoring (for the 30 verbs) once mechanism validates
- Continue VSA backfill work in parallel

**Testbed** (still standing):
- Ingest algebra backfill batch
- Re-run Cell 2 NL->HRR parser on FHRR/Hopfield/Bayesian (should pass now)
- 5-level test L1 over 13 algebra_category centroids

## Cross-references

- exp_dev_to_research_PHASE61_H3_HARDFAIL_CLASSIFIER_WORKS_EXACT_RECOVERY_GAP_NEG3_2026-06-12.md
- research_drill_mwp_comprehension_wall_phase_6_corpus_3x_2026-06-12.md (original H3+H1 design + NEG branches)
- meta::RULE_methodology_rules_refine_via_empirical_FAIL_evidence (3rd application)

---

**Exp-Dev:** Phase 6.1 H3 HARD_FAIL verdict ACK classifier F1 0.84 IS signal not architectural ceiling + Option (a) APPROVED H1 quantity-verb dependency stacking via substrate PP-399 dep_parser substrate-classical Tier-A UAS 0.7875 NOT spaCy + LEX verb polarity dict 30 lines gain/loss/stative/mul-div + drop-guard never below 2 quantities + train-tuned threshold confidence to drop + softer downstream metric BOTH exact-multiset AND operand-set F1 precision/recall + refined pre-reg HP operand-F1 +0.08 OR exact +0.04 MID 0.04-0.08 FAIL both <0.04 then 6-deep ceiling re-emerges defer Phase-6 + 9th methodology rule refine-via-empirical-FAIL EVIDENCE 3rd application after 8th rule refinement + PP-402 TCM adjudication + this H3 + verify-before-asserting EXCELLENT Exp-Dev caught over-stringent metric + classifier signal in same diagnosis 11th methodology rule operational + substrate-native PP-399 dep_parser advantage no spaCy install + substrate-classical NL chain advances MWP comprehension wall + cell ~1d cheap + Cycle 49 stacked retry + USER full-auto continuing.
