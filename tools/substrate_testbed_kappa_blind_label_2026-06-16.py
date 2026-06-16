"""Testbed blind labels for bilateral kappa ITEM 1 (DECISION 147d / Skunkworks 56-edge sample).

Per 110a/129a discipline: NO peek at sealed file; labels assigned independently from
atom-pair + relation + textbook semantics ONLY.

Allowed labels (3-cat):
  STRUCTURALLY_VALID -- rel_type textbook-correct for this directed pair
  UNDECIDABLE_or_PLAUSIBLE -- defensible but not strict (field-membership, representable-as)
  NOT_VALID -- wrong direction / wrong rel_type / spurious

Decision criteria applied per edge:
  - SPECIALIZES: src is a specific case of tgt family/concept
  - DEPENDS_ON: src REQUIRES tgt (tier-monotone downward preferred); reversed = NOT_VALID
  - USES: src invokes tgt as a subprocedure/primitive
  - technique --DEPENDS_ON--> field-name (CS/PHYS/SCHOOL): UNDECIDABLE_or_PLAUSIBLE or
    NOT_VALID (strict: techniques don't DEPEND_ON the field they belong to; field USES techniques)

Mandatory disclosure: same-LLM-family bilateral kappa carries ~50-60% representation-level
self-preference residual per Li 2025 / Wataoka 2024 / Caliskan-Islam.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

BLIND_SAMPLE = Path('data/audit/bilateral_kappa_BLIND_for_testbed_2026-06-16.jsonl')
OUT = Path('data/audit/testbed_kappa_labels_2026-06-16.jsonl')

LABELS = {
    # SPECIALIZES into binders/algebraic_binding family (T2 -> T2_FAM): textbook-correct
    0: ('STRUCTURALLY_VALID', 'tensor_product_representation IS a binder; SPECIALIZES binders family'),
    1: ('UNDECIDABLE_or_PLAUSIBLE', 'q-learning has historical lineage to optimal control LQR but DEPENDS_ON is loose'),
    2: ('STRUCTURALLY_VALID', 'TPR specific case of algebraic_binding family'),
    3: ('UNDECIDABLE_or_PLAUSIBLE', 'resonator_network is computational; theta_gamma is BIO inspiration not formal dep'),
    4: ('STRUCTURALLY_VALID', 'prims_mst is a graph_traversal algorithm; SPECIALIZES family'),
    5: ('UNDECIDABLE_or_PLAUSIBLE', 'zca_whitening is a linear transform; SPECIALIZES transformers family is plausible if family-name covers linear-transformer class'),
    6: ('UNDECIDABLE_or_PLAUSIBLE', 'Collins structured perceptron belongs to structured-prediction school; DEPENDS_ON SCHOOL direction defensible but field-membership not strict dep'),
    7: ('STRUCTURALLY_VALID', 'kalman_filter applies bayes_rule recursively; USES textbook-correct'),
    8: ('UNDECIDABLE_or_PLAUSIBLE', 'tw_edge_z is a spectral observer; family covers; mid-band'),
    9: ('STRUCTURALLY_VALID', 'cascade_hmm_pipeline USES viterbi_decoding (T4->T3 tier-monotone)'),
    10: ('STRUCTURALLY_VALID', 'cascade_hmm_pipeline USES hmm_transition (T4->T3 tier-monotone)'),
    11: ('UNDECIDABLE_or_PLAUSIBLE', 'DFT is a linear transform; SPECIALIZES transformers family ambiguity'),
    12: ('NOT_VALID', 'REVERSED: RL USES MDP; MDP does not DEPEND_ON RL field; technique-vs-instance backwards'),
    13: ('UNDECIDABLE_or_PLAUSIBLE', 'MDP relates to dynamical_systems but DEPENDS_ON PHYS is field-membership not strict'),
    14: ('STRUCTURALLY_VALID', 'mp_bulk_kl IS a spectral observer'),
    15: ('STRUCTURALLY_VALID', 'context_binding IS a specific algebraic_binding'),
    16: ('UNDECIDABLE_or_PLAUSIBLE', 'gram_schmidt is basis transformer; SPECIALIZES transformers family ambiguity'),
    17: ('STRUCTURALLY_VALID', 'MDP DEPENDS_ON probability_space foundation; T3->T1 correct'),
    18: ('UNDECIDABLE_or_PLAUSIBLE', 'markov_chain_property_lemma is a derived result; same-tier DEPENDS_ON suspect'),
    19: ('NOT_VALID', 'REVERSED: ML USES SGD; SGD does not DEPEND_ON ML field; technique-vs-field backwards'),
    20: ('STRUCTURALLY_VALID', 'circular_convolution IS the HRR binder'),
    21: ('NOT_VALID', 'REVERSED: structured_prediction USES viterbi; viterbi predates structured_prediction school'),
    22: ('STRUCTURALLY_VALID', 'convex_optimization USES lagrange_multiplier for constraints; textbook-correct'),
    23: ('STRUCTURALLY_VALID', 'chu_liu_edmonds is a graph_traversal algorithm'),
    24: ('UNDECIDABLE_or_PLAUSIBLE', 'q-learning function-approximation may use chain_rule but not core Q-learning'),
    25: ('STRUCTURALLY_VALID', 'fhrr_bind IS a binder'),
    26: ('NOT_VALID', 'REVERSED: gradient_descent USES limit_of_function; T1 should not DEPEND_ON T3'),
    27: ('STRUCTURALLY_VALID', 'q-learning with function approx uses SGD; same-tier DEPENDS_ON acceptable'),
    28: ('UNDECIDABLE_or_PLAUSIBLE', 'MDP solved by DP but DEPENDS_ON capability concept is weak'),
    29: ('UNDECIDABLE_or_PLAUSIBLE', 'pca_whitening is data transform; transformers family ambiguity'),
    30: ('STRUCTURALLY_VALID', 'spectral_gap IS a spectral observer'),
    31: ('NOT_VALID', 'REVERSED: RL contains policy_gradient as technique; PG does not DEPEND_ON RL field'),
    32: ('NOT_VALID', 'REVERSED: gradient_descent USES derivative; T1 should not DEPEND_ON T3'),
    33: ('STRUCTURALLY_VALID', 'role_filler_binding IS a binder'),
    34: ('NOT_VALID', 'REVERSED: ML USES discriminative_perceptron; perceptron does not DEPEND_ON ML field'),
    35: ('STRUCTURALLY_VALID', 'cascade_hmm_pipeline USES hmm_emission'),
    36: ('STRUCTURALLY_VALID', 'mutual_information defined via shannon_entropy; same-tier T1 DEPENDS_ON correct'),
    37: ('STRUCTURALLY_VALID', 'MDP uses probabilistic_inference family; T3->T2_FAM tier-monotone'),
    38: ('NOT_VALID', 'REVERSED: count_nb USES bayes_rule; T1 should not DEPEND_ON T3'),
    39: ('STRUCTURALLY_VALID', 'attention_mechanism USES inner_product; textbook-correct'),
    40: ('NOT_VALID', 'REVERSED: bayes_rule_synthesis derives FROM bayes_rule; T1 should not DEPEND_ON T3'),
    41: ('NOT_VALID', 'REVERSED: RL USES bellman_equation; bellman_equation does not DEPEND_ON RL field'),
    42: ('STRUCTURALLY_VALID', 'MDP solving uses bellman_equation; same-tier DEPENDS_ON acceptable'),
    43: ('UNDECIDABLE_or_PLAUSIBLE', 'MDP can be cast as PGM but DEPENDS_ON CS field framework is loose'),
    44: ('STRUCTURALLY_VALID', 'adam_optimizer USES gradient'),
    45: ('NOT_VALID', 'REVERSED: RL contains q_learning as technique; q_learning does not DEPEND_ON RL field'),
    46: ('STRUCTURALLY_VALID', 'MDP applies bayes_rule for belief updates; T3->T1 OK'),
    47: ('STRUCTURALLY_VALID', 'q-learning function-approx uses gradient_based_optimizer family'),
    48: ('UNDECIDABLE_or_PLAUSIBLE', 'mutual_information defined in information_theory; field-membership not strict dep'),
    49: ('NOT_VALID', 'REVERSED: ML USES count_nb; count_nb does not DEPEND_ON ML field'),
    50: ('STRUCTURALLY_VALID', 'context_binding IS a binder'),
    51: ('STRUCTURALLY_VALID', 'kronecker_product IS a binder operation (TPR uses it); SPECIALIZES family acceptable despite tier reversal'),
    52: ('UNDECIDABLE_or_PLAUSIBLE', 'lyapunov_stability built within dynamical_systems but field-membership not strict dep'),
    53: ('UNDECIDABLE_or_PLAUSIBLE', 'q-learning historical from optimal_control_LQR; DEPENDS_ON loose'),
    54: ('STRUCTURALLY_VALID', 'variational_inference minimizes kl_divergence; USES textbook-correct'),
    55: ('STRUCTURALLY_VALID', 'MDP solved by dynamic_programming; same-tier DEPENDS_ON acceptable'),
}


def main():
    # Read JSONL blind sample
    edges = []
    with open(BLIND_SAMPLE) as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))

    assert len(edges) == 56, f'expected 56 edges, got {len(edges)}'
    assert set(LABELS.keys()) == set(range(56)), f'label keys mismatch'

    # Compose output (JSONL of labels per edge, matching --compute expected format)
    OUT.parent.mkdir(exist_ok=True, parents=True)
    with open(OUT, 'w') as f:
        for e in edges:
            eid = e['edge_id']
            label, rationale = LABELS[eid]
            row = {
                'edge_id': eid,
                'src': e['src'],
                'tgt': e['tgt'],
                'rel_type': e['rel_type'],
                'src_tier': e['src_tier'],
                'tgt_tier': e['tgt_tier'],
                'testbed_label': label,
                'testbed_rationale': rationale,
            }
            f.write(json.dumps(row) + '\n')

    # Print distribution
    from collections import Counter
    cnt = Counter(v[0] for v in LABELS.values())
    print(f'Wrote {len(LABELS)} blind labels to {OUT}')
    print(f'Distribution: {dict(cnt)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
