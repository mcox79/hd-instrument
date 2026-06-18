"""Ratify DEGENERATE-REGIME-NOT-REFUTATION as CONFIRMED (Skunkworks 3rd batch; 21:30).

Skunkworks self-corrected per 19th-rule (2nd VERIFY-THE-REFERENT catch on catalogue):
catalogue showed ~95 CONFIRMED but Store-authoritative = 42 atomized / 7 CONFIRMED.
RETRACTED ledger-vs-Store conflation; DEGENERATE-REGIME ratified TO Store.

7 witnesses (well above 3-cross-witness bar):
  (1) ARCH-A over-capacity M-grid (experiment-design)
  (2) ARCH-A empirical-cliff zero-zone (experiment-design)
  (3) ARCH-B softmax-saturation 1.0->16xN (experiment-design)
  (4) D-ECR eviction both-policies-1.000 (experiment-design)
  (5) C1 self-dominance one-hot clean-cue (experiment-design)
  (6) 8b synthetic-Zipf no-op arms (arm-layer)
  (7) text8 30MB-threshold false-reject (infra-tool layer)

Cross-layer annotation: same class, three contexts (experiment-design + arm-layer + infra-tool).
Single discipline: "a measurement is a test only if its discriminating range covers reality."

Per per-atom HARD-FAIL gate discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


SPEC = {
    'slug': 'degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict',
    'name': 'Audit lesson (CONFIRMED; instance 79; verify): degenerate-regime-not-refutation',
    'description': (
        "A test run whose metric/control CANNOT DISCRIMINATE (saturated / under-stressed / over-capacity / "
        "one-hot / collapsed) is a NON-TEST, not a refutation -- confirm the regime is DISCRIMINATING "
        "(reference point measurably > floor AND < ceiling) BEFORE reading any verdict. Single discipline "
        "across 3 layers: 'a measurement is a test only if its discriminating range covers reality.' "
        "Layers: experiment-design (degenerate regime); arm-layer (no-op arms); infra-tool (uncalibrated "
        "threshold). Composes with verify-the-referent family + no-Goodhart + discriminating-regime guards "
        "now in C1/8a/8b/refuse-gate preregs."
    ),
    'lesson_class': 'verify',
    'witnesses_count': 7,
    'instance_number': 79,
    'instance_number_provenance': (
        'Skunkworks 21:30 self-correction 3rd-batch CONFIRMED ratify (was ledger-only; now Store-ratified); '
        '7 witnesses well above 3-cross-witness bar; cross-layer annotation experiment-design + arm-layer + infra-tool'
    ),
    'witnesses': [
        'ARCH-A over-capacity M-grid (experiment-design)',
        'ARCH-A empirical-cliff zero-zone (experiment-design)',
        'ARCH-B softmax-saturation 1.0->16xN (experiment-design)',
        'D-ECR eviction both-policies-1.000 (experiment-design)',
        'C1 self-dominance one-hot clean-cue iid (experiment-design)',
        '8b synthetic-Zipf no-op arms (arm-layer; composes failure-mode-must-be-arm-fixable)',
        'text8 30MB-threshold false-reject (infra-tool layer; composes audit-tooling-verify)',
    ],
    'cross_layer_annotation': {
        'experiment_design': ['ARCH-A over-capacity', 'ARCH-A empirical-cliff', 'ARCH-B softmax-saturation', 'D-ECR both-1.000', 'C1 self-dominance'],
        'arm_layer': ['8b synthetic-Zipf no-op arms'],
        'infra_tool': ['text8 30MB-threshold false-reject (also double-witnesses Lesson 1 audit-tooling-verify)'],
    },
    'composes_with': [
        'VERIFY_THE_REFERENT_meta_lens',
        'no_goodhart',
        'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
        'AUDIT_failure_mode_must_be_arm_fixable_no_op_arms_caught_at_smoke',
        'discriminating_regime_guard_C1_8a_8b_refuse_gate_preregs',
    ],
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
        'cross_layer_annotation': SPEC['cross_layer_annotation'],
        'instance_number': SPEC['instance_number'],
        'instance_number_provenance': SPEC['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': False,
        'prose_source': 'skunkworks_to_testbed_research_CATALOGUE_self_correction_store_authoritative_DEGENERATE_ratify_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': SPEC['composes_with'],
        'verify_the_referent_family': True,
        'cross_layer_class': True,
        'source': 'DEGENERATE_REGIME_NOT_REFUTATION_3rd_batch_skunkworks_self_correction_19th_rule_catalogue_vs_store_2nd_verify_the_referent_catch_on_own_bookkeeping_7_witnesses_well_above_3_cross_witness_bar',
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

    ps.add_atom(atom, source='DEGENERATE_REGIME_3rd_batch_skunkworks_self_correction', note='CONFIRMED 7 witnesses; cross-layer')
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    gate_ok = post_axiom == 206 and post_mod
    status = 'OK' if gate_ok else 'HARD_FAIL'
    print(f'  + {atom.id}')
    print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
    if not gate_ok:
        print('  HARD_FAIL: halting.')
        return 2

    print('=' * 72)
    print(f'DEGENERATE-REGIME ratify CONFIRMED COMPLETE: +1 atom; Store CONFIRMED 7 -> 8')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
