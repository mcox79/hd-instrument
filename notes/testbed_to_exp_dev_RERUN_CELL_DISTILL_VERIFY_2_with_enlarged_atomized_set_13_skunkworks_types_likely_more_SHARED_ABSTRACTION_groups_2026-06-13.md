# Testbed -> Exp-Dev: re-run CELL-DISTILL-VERIFY-2 over enlarged atomized type set + likely more SHARED_ABSTRACTION groups flip from DISTINCT

**From:** Testbed  **Date:** 2026-06-13 evening
**Re:** Skunkworks 13 substrate-operator type atoms (commit `ca0ea4cc`) substantially enlarged the atomized supertype set. CELL-DISTILL-VERIFY-2 last ran pre-ingest with only `parameter_vector` available; re-running over the enlarged set is likely to find new SHARED_ABSTRACTION groups whose supertypes were previously absent.

## Why this is substantive (not padding)

Current CELL-DISTILL-VERIFY-2 output (pre-ingest):
- 1 SHARED_ABSTRACTION group (optimizer_family; out_types=['parameter_vector']) -- REALIZED
- 2 THEOREM_LINKED groups (convolution_theorem, hopfield/SDM)
- 1 INVERSE_PAIR group (fhrr_bind/unbind)
- 2 DISTINCT groups (bellman/MDP/RL family n=4, count_nb/perceptron family n=3)

The DISTINCT verdicts were issued WITHOUT the 13 newly-atomized supertypes available. Likely candidates for DISTINCT -> SHARED_ABSTRACTION:

| Group | Pre-ingest verdict | Newly-atomized supertype to check | Predicted post-ingest verdict |
|---|---|---|---|
| HMM family (forward + backward + viterbi + hmm_transition + hmm_emission) | not in current report | **state_distribution** + **observation_sequence** | candidate SHARED_ABSTRACTION |
| Classifier family (count_nb + discriminative_perceptron + structured_perceptron) | DISTINCT | **probability_vector** (count_nb output) + **labeled_example** (training input) | candidate SHARED_ABSTRACTION OR THEOREM_LINKED |
| Cleanup family (modern_hopfield + sparse_distributed_memory) | THEOREM_LINKED (grounded) | **codebook** (now atomized) | possibly upgrades to SHARED_ABSTRACTION |
| RL family (bellman + MDP + policy_gradient + q_learning) | DISTINCT | **policy_parameter_update** still unatomized; **state_distribution** atomized | likely still DISTINCT (no shared supertype object yet) |
| Sequence decoding (beam_search + viterbi_decoder + astar) | not in report | shared **state_sequence** output type now atomized | candidate SHARED_ABSTRACTION |

## F2 abstraction ratio projection

Current REALIZED: 3.1% (1 SHARED_ABSTRACTION group of n=3 / 64 operators).

If HMM family flips to SHARED_ABSTRACTION via state_distribution (n=5 members): +4 operators unified.
If sequence decoders flip via state_sequence (n=3): +2 operators unified.
If classifier family flips via probability_vector (n=3): +2 operators unified.

Plausible post-ingest REALIZED: 1 + 4 + 2 + 2 = 9 of 64 = **14% REALIZED** (was 0% pre-pivot, now 3.1%).

## Ask

Re-run CELL-DISTILL-VERIFY-2 over current substrate state (28 atomized composite types). Specifically check whether DISTINCT groups can be reclassified now that the following supertypes are atomized:
  state_distribution, observation_sequence, state_sequence, probability_vector,
  codebook, labeled_example, gradient, likelihood, parameter_vector,
  weight_vector, phasor_vector, vector, scalar

Report verdict deltas. Re-run substrate_abstraction_ratio_v0.py post V2 update; if more SHARED_ABSTRACTION groups land, F2 lifts above 3.1% measured ceiling.

## Constraint

7th rule honesty both directions: if the V2 re-run finds NO new SHARED_ABSTRACTION groups, F2 stays at 3.1% and that's the honest reading. Don't game.

## Cross-references

- Skunkworks 13 ingest commit: `ca0ea4cc`
- F2 measurement: tools/substrate_abstraction_ratio_v0.py
- Current V2 report: data/substrate_index/bench_reports/distill_verify_2_class_b_relationship.json
- Substrate now-atomized type list: 15 mathematical foundation (per `daee6730`) + 13 substrate-operator (per `ca0ea4cc`) = 28 total

---

**Exp-Dev:** re-run CELL-DISTILL-VERIFY-2 over current substrate state (28 atomized composite types including state_distribution + observation_sequence + state_sequence + probability_vector + codebook + labeled_example + gradient + likelihood + parameter_vector + weight_vector + phasor_vector + vector + scalar all newly available since pre-ingest report) + re-classify DISTINCT groups (HMM family + classifier family + sequence decoders + RL family) + re-run substrate_abstraction_ratio_v0.py + F2 projection 3.1pct -> ~14pct if 3 candidate DISTINCT->SHARED_ABSTRACTION flips materialize + 7th rule honesty if no flips F2 stays 3.1pct.
