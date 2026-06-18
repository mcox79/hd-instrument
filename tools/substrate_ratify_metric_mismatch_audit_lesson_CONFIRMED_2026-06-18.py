"""Ratify metric-mismatch audit_lesson as CONFIRMED per Skunkworks A5 FINAL verdict-VET ruling (2026-06-18).

Skunkworks's cert-owner flag (post-A5 exemplification end-to-end):
"test a mechanism on ITS claimed benefit; switch metrics once, principled + pre-registered +
switch-once; a metric non-discriminating FOR THE CLAIM is a NON_TEST not a refutation."

Witnesses (>=3 cross-witness bar met):
  1. A5 capacity-curve disfavored binary codes (caught by no-noise control; switched ONCE to
     mechanism's own metric noise-robustness on principled + pre-registered + HARD_FAIL final)
  2. Refuse-gate NON_TEST (the gap-refuse claim measured on mechanism's claimed-benefit metric;
     self-dominance wall caught at DEGENERATE-REGIME level)
  3. DEGENERATE-REGIME-NOT-REFUTATION class precedent (sibling; same root: non-discriminating
     metric for the claim is non-test)

Composes (cross-links): anchor-mechanism-match + DEGENERATE-REGIME-NOT-REFUTATION + no-Goodhart
+ VERIFY-THE-REFERENT (the metric verifies the actual mechanism claim).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


SPEC = {
    'slug': 'metric_mismatch_test_mechanism_on_its_claimed_benefit_switch_metrics_once_principled_pre_registered',
    'name': 'Audit lesson (CONFIRMED; instance 83; verify): metric-mismatch test-mechanism-on-its-claimed-benefit',
    'description': (
        "Test a mechanism on ITS claimed benefit. If the chosen metric is non-discriminating FOR THE CLAIM, "
        "it is a NON_TEST not a refutation. Discipline: (1) switch metrics ONCE, principled (cite mechanism's "
        "own benefit-claim + research design-intent), pre-registered, no result-chasing; (2) HARD_FAIL on the "
        "switched-to metric is FINAL (no third metric); (3) capacity-curve disfavored by construction is "
        "caught by the no-noise control before scoring. Today witnesses: (a) A5 ARCH-A 2x2 ablation -- "
        "capacity-curve disfavored binary codes (caught no-noise control) -> switched ONCE to noise-robustness "
        "(mechanism's own claimed benefit per Dasgupta-Tosh; principled + pre-registered commit 122496f4) -> "
        "HARD_FAIL accepted as B-FINAL = ARCH-A MIDDLE_BAND closure RE-AFFIRMED honestly; (b) Refuse-gate "
        "NON_TEST 2026-06-17 -- gap-refuse on real held-out caught self-dominance wall; readout-swap is NON_TEST "
        "for the recapture claim; (c) DEGENERATE-REGIME-NOT-REFUTATION class precedent (CONFIRMED; same root "
        "discipline at the regime-discrimination layer). Composes verify-the-referent parent (the metric "
        "verifies the actual mechanism claim) + no-Goodhart + DEGENERATE-REGIME + anchor-mechanism-match."
    ),
    'lesson_class': 'verify',
    'witnesses_count': 3,
    'instance_number': 83,
    'witnesses': [
        'A5 ARCH-A 2x2 ablation 2026-06-18: capacity-curve disfavored binary codes caught by no-noise control; switched ONCE to noise-robustness (Dasgupta-Tosh-claimed benefit; principled + pre-registered commit 122496f4); HARD_FAIL B-FINAL; ARCH-A MIDDLE_BAND closure RE-AFFIRMED. Exp-Dev held + refused to metric-shop throughout = no-Goodhart in real time.',
        'Refuse-gate NON_TEST 2026-06-17: gap-refuse metric on real held-out q54-q65 caught self-dominance wall; nonlinear-readout-swap is NON_TEST for the recapture claim (the metric was right; the regime was non-discriminating for the readout-swap claim).',
        'DEGENERATE-REGIME-NOT-REFUTATION CONFIRMED class precedent (instance 79; 7 witnesses): same root discipline at regime-discrimination layer; metric/control cannot discriminate -> non-test not refutation.',
    ],
    'instance_number_provenance': (
        'Skunkworks A5 FINAL verdict-VET 2026-06-18 ruled "EXEMPLIFIED end-to-end -> candidate for ratify to '
        'CONFIRMED"; CONFIRMED-grade at 3-cross-witness bar; composes with sibling DEGENERATE-REGIME-NOT-'
        'REFUTATION + no-Goodhart + anchor-mechanism-match via verify-the-referent parent'
    ),
    'composes_with': [
        'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
        'AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict',
        'AUDIT_recapture_anchor_mechanism_match_referent_layer',
        'no_goodhart_metric_measures_claimed_thing',
    ],
    'verify_the_referent_parent': 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
}


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/{pre_axiom}  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL.')
        return 1

    metadata = {
        'lesson_class': SPEC['lesson_class'],
        'confirmed_or_candidate': 'CONFIRMED',
        'witnesses_count': SPEC['witnesses_count'],
        'witnesses': SPEC['witnesses'],
        'instance_number': SPEC['instance_number'],
        'instance_number_provenance': SPEC['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': False,
        'prose_source': 'skunkworks_to_all_A5_FINAL_verdict_VET_PASS_expansion_HARD_FAIL_valid_readout_C1_atomize_GO_convergent_finding_2026-06-18.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': SPEC['composes_with'],
        'verify_the_referent_family': True,
        'verify_the_referent_parent': SPEC['verify_the_referent_parent'],
        'exemplified_end_to_end_at_A5': True,
        'source': 'metric_mismatch_audit_lesson_CONFIRMED_skunkworks_A5_FINAL_verdict_VET_exemplification_end_to_end_3_cross_witness_bar_met_A5_refuse_gate_DEGENERATE_REGIME_sibling',
    }
    atom = Atom(
        id=f"AUDIT_{SPEC['slug']}",
        name=SPEC['name'],
        description=SPEC['description'],
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
    )

    existing = {a.id for a in ps.all_atoms()}
    if atom.id in existing:
        print(f'  SKIP (already present): {atom.id}')
        return 0

    ps.add_atom(atom, source='metric_mismatch_CONFIRMED_skunkworks_A5_FINAL_2026_06_18', note='CONFIRMED 3 witnesses; exemplified end-to-end')
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    gate_ok = post_axiom == 206 and post_mod
    status = 'OK' if gate_ok else 'HARD_FAIL'
    print(f'  + {atom.id}')
    print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
    if not gate_ok:
        return 2

    print('=' * 72)
    print(f'metric-mismatch CONFIRMED ratify COMPLETE: +1 atom (instance 83)')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
