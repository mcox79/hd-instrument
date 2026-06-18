"""Ratify A4 Lean SCHEMA-VET discipline as 3 METHODOLOGY_RULE atoms per Skunkworks spec (19:00).

Composes 6 design sections into 3 load-bearing rules per Amendment-3 (no-proliferate):
1. M_LEAN_semantics_match_necessary (sections 1-2,4): Lean-PASS necessary-not-sufficient for T0_PROVEN_FORMAL
2. M_LEAN_no_algebra_structural_guard (section 3): no algebra by default; promotion to axiom_term explicit USER PHASE III+
3. M_LEAN_failure_mode_coverage (sections 5-6): 3 false-positive modes (semantics-mismatch + vacuous + build-error-false-green)

PHASE-2 expansion (DISTINCT from FROZEN-24 baseline; ratified expansion lane).
NO algebra (methodology atoms excluded from axiom_term); per-atom HARD-FAIL gates.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


METHODOLOGY_RULES = [
    {
        'slug': 'M_LEAN_semantics_match_necessary_lake_pass_necessary_not_sufficient_T0_PROVEN_FORMAL',
        'name': 'Methodology rule (M_LEAN; semantics-match): Lean PASS NECESSARY-NOT-SUFFICIENT for T0_PROVEN_FORMAL',
        'description': (
            "A Lean PASS is NECESSARY-NOT-SUFFICIENT for T0_PROVEN_FORMAL. Promotion requires a SEMANTICS-MATCH "
            "VET: the proposition Lean proved (P_lean) must be the SAME claim the substrate makes (P_substrate) "
            "-- not a weaker/different/vacuous statement. lake-PASS + semantics-match -> T0_PROVEN_FORMAL "
            "(confirmed_by the proof-record); lake-FAIL -> REFUTED + KEEP (negative knowledge; disproof valuable). "
            "Composes with VERIFY-THE-REFERENT family (the formal-layer instance: the proposition Lean verified "
            "actually IS what we claim) + no-Goodhart (the proof measures the claimed thing) + 100th-rule "
            "(audit-tooling-verify-before-trusted at proof-verification layer)."
        ),
        'rule_scheme': 'METHODOLOGY_LEAN_SCHEMA_VET',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': (
            'Skunkworks 19:00 A4 substrate-build spec; composes design sections 1-2,4 of Director-RATIFIED Lean '
            'SCHEMA-VET discipline; PHASE-2 expansion (DISTINCT from FROZEN-24 baseline; deliberate ratified '
            'expansion for new formal-proof capability)'
        ),
        'methodology_phase': 'PHASE-2',
        'composes_with': [
            'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
            'no_goodhart_metric_measures_claimed_thing',
            'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
        ],
    },
    {
        'slug': 'M_LEAN_no_algebra_structural_guard_axiom_term_promotion_PHASE_III_USER_authority',
        'name': 'Methodology rule (M_LEAN; structural-guard): no algebra default + axiom_term promotion PHASE III USER authority',
        'description': (
            "A Lean-verified atom carries NO algebra field BY DEFAULT -> queryable PROVEN-FORMAL knowledge, "
            "excluded from axiom_term. Promotion of a formal-proven IDENTITY into axiom_term (the proven-math "
            "core) is a SEPARATE, EXPLICIT cert-owner step, USER-architectural-authority (PHASE III+), NEVER "
            "automatic on a lake-PASS. So a Lean-PASS-but-semantics-mismatch can never corrupt axiom_term "
            "(correctness-by-construction). Composes with RESEARCH_FINDING no-algebra structural guard (same "
            "conservative pattern; trust-tier T0-T3 architecture preserves load-bearing core safety) + the "
            "structural-guard discipline empirically validated today (STEP-B 1229 RF atoms with 0-algebra)."
        ),
        'rule_scheme': 'METHODOLOGY_LEAN_SCHEMA_VET',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': (
            'Skunkworks 19:00 A4 substrate-build spec; composes design section 3 of Director-RATIFIED Lean '
            'SCHEMA-VET discipline; PHASE-2 expansion; safety guard mirroring RESEARCH_FINDING structural guard'
        ),
        'methodology_phase': 'PHASE-2',
        'composes_with': [
            'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
            'research_finding_no_algebra_structural_guard',
            'trust_tier_T0_T3_architecture',
        ],
    },
    {
        'slug': 'M_LEAN_failure_mode_coverage_3_false_positive_modes_semantics_vacuous_build_error',
        'name': 'Methodology rule (M_LEAN; failure-mode coverage): 3 false-positive modes + staleness re-verify',
        'description': (
            "Lean SCHEMA-VET must cover 3 false-positive modes: (a) SEMANTICS-MISMATCH (P_lean != P_substrate; "
            "addressed via semantics-match VET); (b) VACUOUS/TRIVIAL PASS (proved a true-but-irrelevant "
            "statement; confirm P_lean is the non-trivial claim); (c) BUILD-ERROR-AS-FALSE-GREEN (a lake build "
            "that errored mis-read as PASS; verify exit-code + that the TARGET theorem -- not a placeholder -- "
            "was built; READ the output, don't tail-pipe it). Plus STALENESS GUARD: re-verify on lean-toolchain "
            "or mathlib version change (analog of completeness-guard recurrence-detector). Composes with 100th-"
            "rule (audit-tooling-self-verify) + tail-buffers-to-EOF tooling lesson (read output don't tail-pipe; "
            "applies the lesson from .venv process-integrity finding) + VERIFY-THE-REFERENT (verify the build "
            "verified what we think)."
        ),
        'rule_scheme': 'METHODOLOGY_LEAN_SCHEMA_VET',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': (
            'Skunkworks 19:00 A4 substrate-build spec; composes design sections 5-6 of Director-RATIFIED Lean '
            'SCHEMA-VET discipline; PHASE-2 expansion; 100th-rule application at proof-verification layer with '
            '3 false-positive modes + staleness guard'
        ),
        'methodology_phase': 'PHASE-2',
        'composes_with': [
            'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
            'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
            'tail_buffers_to_EOF_tooling_lesson',
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
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_atom(spec: dict) -> Atom:
    slug = spec['slug']
    metadata = {
        'rule_scheme': spec['rule_scheme'],
        'rule_class': spec['rule_class'],
        'rule_number_provenance': spec['rule_number_provenance'],
        'methodology_phase': spec['methodology_phase'],
        'frozen': True,
        'confirmed': True,
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'prose_source': 'skunkworks_to_testbed_research_SUBSTRATE_BUILD_A4_lean_methodology_atom_spec_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': spec['composes_with'],
        'verify_the_referent_family': True,
        'lean_schema_vet_discipline_part': True,
        'source': 'A4_substrate_build_skunkworks_19_00_spec_lean_schema_vet_discipline_PHASE_2_expansion_DISTINCT_frozen_24_baseline_amendment_3_compose_6_sections_into_3_atoms_USER_substrate_build_directive_autonomy_path',
    }
    return Atom(
        id=f'RULE_{slug}',
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.METHODOLOGY_RULE,
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

    for spec in METHODOLOGY_RULES:
        atom = build_atom(spec)
        existing = {a.id for a in ps.all_atoms()}
        if atom.id in existing:
            print(f'  SKIP (already present): {atom.id}')
            continue
        ps.add_atom(atom, source='A4_substrate_build_lean_schema_vet_PHASE_2_expansion', note=f"{spec['rule_scheme']} {spec['methodology_phase']}")
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

    post_n = sum(1 for _ in ps.all_atoms())
    print('=' * 72)
    print(f'A4 M_LEAN methodology ratify COMPLETE: +{post_n - pre_n} atoms')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
