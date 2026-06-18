"""Ratify the T_PREP_1 audit_lesson batch per Skunkworks cert-owner rulings (20:10).

Adds 4 new AUDIT_LESSON atoms + annotates RULE_adversarial_self_correction_own_output
with Lesson 3 cross-session-recursive-cascade compose annotation.

Per Skunkworks rulings:
- Lesson 1 (audit-tooling-verify-before-trusted) = CONFIRMED new class (>=3 cross-witnesses; "100th rule")
- Lesson 2 (corpus-completeness-verify-before-audit) = CONFIRMED new class (>=3 witnesses; remote-vs-local count gate)
- Lesson 3 (19th-rule-recursive-cross-session) = COMPOSE annotation onto existing 19th-rule (NOT new class)
- Lesson 4 (user-skepticism-high-signal-audit-input) = CONFIRMED new class (>=3 witnesses; distinct from negativity-bias)
- Lesson 5 (positioning-narrative-time-lag-vs-corpus-state) = CANDIDATE (1 witness; below 3-cross-witness bar; promote on 2 more)

Per bulk-ingest concurrency gotcha (memory rule): Store.add_atom auto-flushes per atom;
this script is single-process serial, fresh-load before write, os.replace-retry tolerant.

Invariant gates (per atom): axiom_term 206/206 PRESERVED + cap_pres 6/6 + landed.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


AUDIT_LESSONS = [
    {
        'slug': 'audit_tooling_verify_before_trusted_keyword_search_unreliable',
        'name': 'Audit lesson (CONFIRMED; instance 71; verify): audit-tooling-verify-before-trusted',
        'description': (
            'Before any audit output is treated as ground truth for downstream ratify/downgrade/scorecard-revision '
            'decisions, the audit tooling itself must be verified for soundness. Today: keyword-cross-reference '
            'audit unreliable in both directions (case/hyphen/word-order false-negatives + substring false-positives). '
            'Failure mode: PROCESS appears rigorous; TOOLING is the silent failure point. Apply: soundness-test on '
            'known-positive + known-negative + permutations + sample-trace before trusting output. If fails: fix '
            'tooling OR use different method (per-cell trace; verdict-field comparison after correct atom matching).'
        ),
        'lesson_class': 'verify',
        'confirmed_or_candidate': 'CONFIRMED',
        'witnesses_count': 5,
        'instance_number': 71,
        'instance_number_provenance': 'Skunkworks 20:10 ruling: confirmed via 5 cross-witnesses keyword-unreliable + degenerate-recall@1 + monitor-perturbs-monitored + STEP-B verify-script-imports-shipped-atomizer + text8-30MB-threshold tool false-reject',
        'composes_with': ['100th_rule_audit_tooling_must_self_verify', 'feedback_audit_tooling_verify_before_trusted_T_PREP_1_lesson_1'],
    },
    {
        'slug': 'audit_input_corpus_completeness_verify_before_output',
        'name': 'Audit lesson (CONFIRMED; instance 72; verify): corpus-completeness-verify-before-audit',
        'description': (
            'Any substrate-wide audit (over-claim, capability, coverage) must verify its INPUT corpus is complete '
            '(vs known-canonical sources like remote desktop runs) BEFORE producing audit output. Today: 1749-gap '
            'half-data audit (1935 local atomized vs 3684 remote total); heavy/cert-grade runs live REMOTE per '
            'compute policy. Apply PROACTIVELY: count atomized (LOCAL) vs canonical files (REMOTE ssh probe); '
            'HALT audit if LOCAL << REMOTE; bulk-SCP sync + re-atomize first. Upstream gate to corpus-wide audits.'
        ),
        'lesson_class': 'verify',
        'confirmed_or_candidate': 'CONFIRMED',
        'witnesses_count': 3,
        'instance_number': 72,
        'instance_number_provenance': 'Skunkworks 20:10 ruling: confirmed via 3 cross-witnesses 1749-gap + half-data audit + Tier-3-atomizer-local-only; standing memory rule formalized',
        'composes_with': ['reference_substrate_corpus_completeness_remote_vs_local_half_data_2026_06_17'],
    },
    {
        'slug': 'user_skepticism_high_signal_audit_input_weight_high_re_verify',
        'name': 'Audit lesson (CONFIRMED; instance 73; process): user-skepticism-high-signal-audit-input',
        'description': (
            'When USER intuitive pushback contradicts current tool output, weight USER signal HIGH and re-verify '
            'the tooling. USER skepticism is often the highest-signal audit input available. Today: 2 USER messages '
            'exposed gaps tools missed (results-real -> keyword-search unreliable; find-all-experiments -> half-data '
            'gap). Apply: dont defend tooling output; run TARGETED VERIFICATION on USER specific concern; consider '
            'which assumption USER question challenges; be prepared to find USER correct; surface gap promptly. '
            'PROCESS rule (weight USER pushback HIGH, re-verify dont defend). Distinct from negativity-bias.'
        ),
        'lesson_class': 'process',
        'confirmed_or_candidate': 'CONFIRMED',
        'witnesses_count': 5,
        'instance_number': 73,
        'instance_number_provenance': 'Skunkworks 20:10 ruling: confirmed via 5 cross-witnesses today results-real + find-all-experiments + DG-48x + fuzzy-retrieval + drift directional corrections',
        'composes_with': ['RULE_adversarial_self_correction_own_output', 'feedback_skunkworks_negativity_bias'],
    },
    {
        'slug': 'substrate_product_positioning_narrative_time_lag_vs_corpus_state',
        'name': 'Audit lesson (CANDIDATE; instance 74; framing): positioning-narrative-time-lag',
        'description': (
            'Canonical substrate-product positioning docs (scorecard, E6, capability map) lag corpus state. When '
            'corpus completeness changes substantively, canonical-doc UPDATE must follow (not the same-day audit '
            'output itself, which was honest given inputs). Today: 2.7% -> 15.2% cert-grade ratio (5.6x ratio '
            'improvement) post-half-data-discovery; substrate-product positioning narrative needs refresh. Apply: '
            'on corpus-completeness event, update canonical positioning docs in NEXT cycle; preserve audit-output '
            'as snapshot (honest given inputs); USER E4 morning summary is the refresh vehicle. CANDIDATE: 1 '
            'witness today; promote on 2 more (3-cross-witness bar).'
        ),
        'lesson_class': 'framing',
        'confirmed_or_candidate': 'CANDIDATE',
        'witnesses_count': 1,
        'instance_number': 74,
        'instance_number_provenance': 'Skunkworks 20:10 ruling: 1 witness today (2.7% -> 15.2% cert-grade ratio post-corpus-completion); below 3-cross-witness bar; file CANDIDATE; promote on 2 more',
        'composes_with': ['testbed_to_research_T_PREP_2_positioning_amendment_input_2026_06_17'],
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


def build_audit_lesson_atom(spec: dict) -> Atom:
    slug = spec['slug']
    metadata = {
        'lesson_class': spec['lesson_class'],
        'confirmed_or_candidate': spec['confirmed_or_candidate'],
        'witnesses_count': spec['witnesses_count'],
        'instance_number': spec['instance_number'],
        'instance_number_provenance': spec['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': spec['confirmed_or_candidate'] == 'CANDIDATE',
        'prose_source': 'T_PREP_1_C4_methodology_lessons_doc_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': spec['composes_with'],
        'source': 'T_PREP_1_audit_lesson_batch_2026_06_17_skunkworks_20_10_rulings_3_confirmed_lesson_1_2_4_plus_1_candidate_lesson_5_plus_1_compose_lesson_3_into_19th_rule',
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


def annotate_19th_rule(ps: PartitionedStore) -> dict:
    """Add Lesson 3 cross-session-recursive-cascade compose annotation to 19th-rule atom."""
    atoms = list(ps.all_atoms())
    target_id = 'RULE_adversarial_self_correction_own_output'
    target = next((a for a in atoms if str(a.id) == target_id), None)
    if target is None:
        return {'status': 'TARGET_NOT_FOUND', 'id': target_id}

    new_md = dict(target.metadata or {})
    new_md['compose_annotation_T_PREP_1_lesson_3_2026_06_17'] = (
        '19th-rule operates recursively across sessions: today 9+ instances in one day across all sessions '
        '(USER -> Skunkworks -> Director -> Skunkworks -> Director -> Orchestrator -> Testbed -> Skunkworks -> Testbed). '
        'The recursive cascade IS the discipline working: each level catches the level above; no level is exempt; '
        'substrate self-corrects without external override. Apply: when questioned (by USER OR another session), '
        'treat as 19th-rule trigger; self-correct PRODUCTIVELY (enumerate assumptions; verify each; ratify or update); '
        'document the self-correction (audit-discipline instance type); do NOT escalate to USER on questions another '
        'session can resolve via 19th-rule self-correction. Per Skunkworks 20:10 ruling: COMPOSE annotation NOT new '
        "class (Amendment-3 compose-dont-proliferate; same 19th-rule operating at multi-session scope)."
    )
    new_md['compose_annotation_source'] = 'T_PREP_1_C4_methodology_lessons_doc_2026-06-17.md + skunkworks_20_10_audit_discipline_backlog_CLEAR_ruling'

    updated = Atom(
        id=target.id,
        name=target.name,
        description=target.description,
        kind=target.kind,
        tier=target.tier,
        corpus=target.corpus,
        algebra=target.algebra,
        metadata=new_md,
        aliases=target.aliases,
        concept_links=target.concept_links,
        complexity=target.complexity,
        current_best_solution=target.current_best_solution,
        equivalences=target.equivalences,
        serves_capability=target.serves_capability,
        signature=target.signature,
        solution_history=target.solution_history,
    )
    ps.add_atom(updated, source='T_PREP_1_lesson_3_compose_annotation_skunkworks_20_10_ruling', note='Lesson 3 cross-session recursive cascade annotation')
    return {'status': 'ANNOTATED', 'id': target_id}


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/{pre_axiom}  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL. Halting.')
        return 1

    # Step 1: add 4 new AUDIT_LESSON atoms (single-process serial)
    for spec in AUDIT_LESSONS:
        atom = build_audit_lesson_atom(spec)
        existing = {a.id for a in ps.all_atoms()}
        if atom.id in existing:
            print(f'  SKIP (already present): {atom.id}')
            continue
        ps.add_atom(atom, source=spec['source'] if 'source' in spec else 'T_PREP_1_audit_lesson_batch_2026_06_17', note=f"{spec['confirmed_or_candidate']} {spec['lesson_class']}")
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + {atom.id}  atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            print('  HARD_FAIL: invariant violation. Halting.')
            return 2

    # Step 2: annotate 19th-rule with Lesson 3
    result = annotate_19th_rule(ps)
    print(f'19th-rule annotation: {result}')
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    print(f'POST-ANNOTATE: atoms={post_n}  axiom_term={post_axiom}/{post_axiom}  cap_pres={post_mod}')

    if post_axiom != 206 or not post_mod:
        print('POST-ANNOTATE GATE FAIL.')
        return 3

    print('=' * 72)
    print(f'T_PREP_1 RATIFY COMPLETE: +{post_n - pre_n} atoms (4 audit_lesson + 0 from annotation [update only])')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
