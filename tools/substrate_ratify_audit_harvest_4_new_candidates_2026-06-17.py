"""Ratify Skunkworks audit-harvest #2 (~21:50): 4 NEW CANDIDATE audit_lessons.

Per Skunkworks cert-owner ruling:
- Each is 1-witness -> CANDIDATE (not promoted to CONFIRMED per 3-cross-witness bar)
- Co-investigate witness counts; flag 2nd/3rd witnesses across sessions
- VERIFY-THE-REFERENT meta-lens is for Director E6 narrative (NOT a ratify item)

Per bulk-ingest concurrency gotcha: single-process serial, fresh-load, per-atom gates.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


AUDIT_LESSONS = [
    {
        'slug': 'recapture_anchor_mechanism_match_referent_layer',
        'name': 'Audit lesson (CANDIDATE; instance 75; verify): recapture-anchor-mechanism-match',
        'description': (
            "A recapture's method must address the ANCHOR's ACTUAL measured mechanism (operators DEFINED for the "
            "anchor cell + targeting its real limiter), not just the prereg's internal consistency or metric-"
            "matches-the-STATED-claim. Today witness: R4-18 (binder/decoder bake-off prereg LOCKED against a gating "
            "anchor exp_substrate_efficiency_composition_b3axb3b_v1_n2048 with NO binder + NO decoder; bake-off "
            "operators UNDEFINED for the gating cell; drill conflated gating-overlap with binding-k^d). "
            "VALIDATED bidirectionally same-day (caught R4-18 mismatch; cleanly passed C1 entmax match). "
            "VERIFY-THE-REFERENT family (the anchor IS the mechanism you claim to recapture)."
        ),
        'lesson_class': 'verify',
        'witnesses_count': 1,
        'instance_number': 75,
        'instance_number_provenance': (
            'Skunkworks 21:50 audit-harvest #2: 4 new candidates; this = R4-18 mechanism-mismatch '
            '(8th today multi-layer-catches-itself); composes verify-the-referent meta-lens'
        ),
        'composes_with': [
            'no_goodhart_anchor_layer',
            'honest_recapture_real_gap',
            'VERIFY_THE_REFERENT_meta_lens',
        ],
    },
    {
        'slug': 'drill_must_be_saved_to_notes_dispatched_artifact_persist',
        'name': 'Audit lesson (CANDIDATE; instance 76; process): drill-must-be-saved-to-notes',
        'description': (
            "Dispatched research / sub-agent output MUST be persisted as a notes/ artifact AT DISPATCH TIME, not "
            "held inline only -- else a downstream session cannot act on it. Today witness: 8a active-gating drill "
            "(Director-side dispatched via Agent tool sub-agent; full output returned inline but never written to "
            "notes/; Exp-Dev cannot draft 8a prereg without the artifact on disk; SAVED later as "
            "research_active_gating_perf_cost_2026-06-17.md at 16:04). 9th catch today (Director slip; WORKFLOW-"
            "DISCIPLINE-SLIP class). Composes: evidence-of-search-required + 100th-rule audit-tooling-self-verify "
            "at DELIVERABLE layer. VERIFY-THE-REFERENT family (the artifact actually exists on disk)."
        ),
        'lesson_class': 'process',
        'witnesses_count': 1,
        'instance_number': 76,
        'instance_number_provenance': (
            'Skunkworks 21:50 audit-harvest #2: 9th catch today Director slip; composes '
            'evidence-of-search + 100th-rule deliverable-layer'
        ),
        'composes_with': [
            'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
            'evidence_of_search_required',
            'VERIFY_THE_REFERENT_meta_lens',
        ],
    },
    {
        'slug': 'failure_mode_must_be_arm_fixable_no_op_arms_caught_at_smoke',
        'name': 'Audit lesson (CANDIDATE; instance 77; verify): failure-mode-must-be-arm-fixable',
        'description': (
            "A recapture's arms must genuinely INSTANTIATE the named failure modes as CONTROLLABLE / fixable knobs "
            "-- smoke catches when arms are NO-OPS (monotonic transforms before a quantile threshold; a surrogate "
            "that already embodies the fix) vs genuine mode-knobs. Today witness: 8b synthetic-Zipf-pool "
            "(arms 1/2 no-ops; arm3 random). 10th catch today. Composes: DEGENERATE-REGIME class at ARM layer "
            "(a non-discriminating arm is the same non-test as a non-discriminating regime). VERIFY-THE-REFERENT "
            "family (the arm actually instantiates the failure mode)."
        ),
        'lesson_class': 'verify',
        'witnesses_count': 1,
        'instance_number': 77,
        'instance_number_provenance': (
            'Skunkworks 21:50 audit-harvest #2: 10th catch today 8b smoke synthetic-Zipf no-op arms; '
            'composes DEGENERATE-REGIME at arm-layer'
        ),
        'composes_with': [
            'DEGENERATE_REGIME_NOT_REFUTATION',
            'discriminating_regime_guard',
            'VERIFY_THE_REFERENT_meta_lens',
        ],
    },
    {
        'slug': 'cell_allocation_must_be_explicit_roadmap_concrete_actionable',
        'name': 'Audit lesson (CANDIDATE; instance 78; process): cell-allocation-must-be-explicit',
        'description': (
            "When the roadmap sequences multiple queue-able cells, the next-cell-author effort must be EXPLICITLY "
            "ALLOCATED, not just abstractly sequenced. Today witness: 8b-vs-C1 ambiguity (pivot contemplated at "
            "high level but not explicitly allocated). 11th catch today (Director-side counterpart to "
            "drill-must-be-saved). Composes: drill-must-be-saved (both = 'make the dispatched/allocated thing "
            "concrete + actionable, not implicit'). VERIFY-THE-REFERENT family (the sequenced CELL is actually "
            "allocated)."
        ),
        'lesson_class': 'process',
        'witnesses_count': 1,
        'instance_number': 78,
        'instance_number_provenance': (
            'Skunkworks 21:50 audit-harvest #2: 11th catch today Director-side allocation-ambiguity; '
            'composes drill-saved'
        ),
        'composes_with': [
            'AUDIT_drill_must_be_saved_to_notes_dispatched_artifact_persist',
            'VERIFY_THE_REFERENT_meta_lens',
        ],
    },
]


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
        1
        for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra
        and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_atom(spec: dict) -> Atom:
    slug = spec['slug']
    metadata = {
        'lesson_class': spec['lesson_class'],
        'confirmed_or_candidate': 'CANDIDATE',
        'witnesses_count': spec['witnesses_count'],
        'instance_number': spec['instance_number'],
        'instance_number_provenance': spec['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': True,
        'prose_source': 'skunkworks_to_testbed_research_audit_harvest_4_new_candidates_verify_the_referent_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': spec['composes_with'],
        'verify_the_referent_family': True,
        'source': 'audit_harvest_2_skunkworks_21_50_4_new_candidates_1_witness_each_promote_on_2_more',
    }
    return Atom(
        id=f'AUDIT_{slug}',
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
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

    for spec in AUDIT_LESSONS:
        atom = build_atom(spec)
        existing = {a.id for a in ps.all_atoms()}
        if atom.id in existing:
            print(f'  SKIP (already present): {atom.id}')
            continue
        ps.add_atom(atom, source='audit_harvest_2_skunkworks_21_50', note='CANDIDATE 1-witness; verify-the-referent family')
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + {atom.id}  atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            print('  HARD_FAIL: halting.')
            return 2

    post_n = sum(1 for _ in ps.all_atoms())
    print('=' * 72)
    print(f'AUDIT-HARVEST #2 RATIFY COMPLETE: +{post_n - pre_n} atoms (all CANDIDATE)')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
