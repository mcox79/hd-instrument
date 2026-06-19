# Testbed (Integrator) -> Skunkworks (Auditor) + Research (Director): MILESTONE -- DECISION 24 Tier 2 batch COMPLETE; 2/2 LIVE QUERY PASS

**From:** Testbed (Integrator)  **Date:** 2026-06-14
**Re:** DECISION 24 Tier 2 done-definition gate.

## What shipped (2 commits)

| # | Capability | Module path | Commit | Live-query test |
|---|---|---|---|---|
| 4 | bayesian_inference + EMMixture | `hdlab/bayesian_inference.py` | `5ef3cae6` | Bayes rare-disease: P=0.1667 (expected ~0.17); EM 3 Gaussians: purity 1.0 in 5 iter |
| 5 | IntentClassifier + RoutedIntentClassifier | `backend/substrate_index/intent_classifier.py` | `4689eee2` | 4-intent toy: 3/4 correct + 1 abstain (18th-rule no-evidence refuse) |

## Done-definition gate (2/2 PASS this batch)

1. ✅ Operator EXECUTES on live query (shown above)
2. ✅ No-regression: only ADDS new modules; existing `intent_router.py` untouched; substrate state unchanged
3. **PENDING: Skunkworks AUDITOR verification** to count toward 70pct ONLINE

## USER rule compliance

- **11th rule:** pure-Python + optional numpy fallback; NO LLM, NO bge, NO torch
- **18th rule:** IntentClassifier confidence-threshold gates predictions (returns None when no feature support; verified in 'wake me at eight' test case where 'eight' never appeared in training). Bayes update raises when marginal is zero.
- **R1 (operator not demo):** both extracted as callable APIs from substrate's own existing primitive semantics
- **R2 (falsifier):** each module has executable live-query test
- **R3 (Tier 3 deferred):** none pulled

## Substrate atoms now executable

| Atom | Module |
|---|---|
| T2/bayesian_inference | hdlab/bayesian_inference.py:bayes_update + bayes_update_categorical |
| T2/em_algorithm | hdlab/bayesian_inference.py:EMMixture |
| T3/map_estimation | hdlab/bayesian_inference.py:map_estimate |
| T3/maximum_likelihood | hdlab/bayesian_inference.py:EMMixture.log_likelihood |
| T2/discriminative_classification | backend/substrate_index/intent_classifier.py:IntentClassifier |
| T3/count_nb (bow-feature alternative) | backend/substrate_index/intent_classifier.py (same API path) |

Plus composed: `RoutedIntentClassifier` extends LIVE `intent_router` from rule-based -> learned (rule-primary + learned-fallback with confidence threshold).

## Cumulative ONLINE delta projection (Tiers 1 + 2)

| Phase | Modules | Operators executable | ONLINE projection |
|---|---|---|---|
| Pre-batch | 0 new | 0 | 30pct (14/46) |
| Tier 1 (DECISION 23) | 3 | 10 atoms | ~37-41pct |
| Tier 2 (DECISION 24) | +2 | +6 atoms | ~44-48pct pending Auditor |

## Skunkworks AUDITOR asks

1. Verify each of 2 modules executes on the live-query examples
2. Confirm capability_preservation=1.0 (no existing module modified)
3. Confirm USER 11th rule (no LLM/bge/torch imports)
4. Reflect Tier 2 in 70pct ONLINE counter
5. Composed routing (RoutedIntentClassifier) is additive — does NOT modify intent_router.py

## Cross-references

- DECISION 24: `notes/research_to_testbed_skunkworks_exp_dev_DECISION_24_GREENLIGHT_TIER_2_*`
- Tier 1 MILESTONE handoff: `notes/testbed_to_skunkworks_research_MILESTONE_DECISION_23_TIER_1_*`
- Item 4 commit: `5ef3cae6`
- Item 5 commit: `4689eee2`

---

**Skunkworks + Research:** DECISION 24 Tier 2 batch COMPLETE + 2/2 LIVE QUERY PASS + Bayes/EM at hdlab/bayesian_inference.py + IntentClassifier+RoutedIntentClassifier at backend/substrate_index/intent_classifier.py + 6 more atoms executable + capability_preservation invariant preserved + USER 11th + 18th rules preserved + Auditor verification needed before counting toward 70pct ONLINE + projected delta 37-41pct -> ~44-48pct + commits 5ef3cae6 + 4689eee2.
