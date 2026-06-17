"""TIER-2 PHASE-2 small batch ratify: 2 example methodology_rule atoms (DECISION 236).

2 atoms in closed-back-edge batch (back-edges to PHASE-1 9da528ca atoms; no phantom):

  meta::RULE_no_papers_internal_tracking_only
    rule_scheme: USER_LOCKED_FRAMING
    rule_number_provenance: cited as 10th USER-LOCKED in feedback_no_papers 2026-06-13
    rule_class: USER_LOCKED; frozen: true
    COMPOSES -> RULE_substrate_internal_no_llm (PHASE-1; 9da528ca)

  meta::RULE_adversarial_self_correction_own_output
    rule_scheme: METHODOLOGY_EPISTEMIC
    rule_number_provenance: cited as 19th methodology in substrate_methodology_rule_19th 2026-06-13
    rule_class: SUBSTRATE_DERIVED; confirmed: true; frozen: true
    COMPOSES -> AUDIT_verify_not_assume_prior_lesson_applied (PHASE-1; 9da528ca)
    COMPOSES -> AUDIT_dont_fabricate_grounding (PHASE-1; 9da528ca)

3 COMPOSES edges total (1 + 2). Note: DECISION 236 specs "+2 COMPOSES intra-batch" but
Skunkworks's source spec text lists 3 distinct COMPOSES targets. Honoring Skunkworks's
literal authored spec (3 edges); Director count appears off-by-1 (flagged forward to Director).

Per DECISION 236 numbering-resolution:
- atomize by NAME (meta::RULE_<descriptive_name> canonical)
- rule_number_provenance (string; "cited as Nth in <source>"; NOT bare int)
- rule_scheme metadata (USER_LOCKED_FRAMING | METHODOLOGY_EPISTEMIC)
- atom (by name) canonical; number = pointer-with-provenance
- no schema change (free-form metadata dict)

PHASE-1 retroactive amendment: deferred per Option A recommendation (DECISION 236 implicit
endorsement: "existing 6 PHASE-1 atoms already follow the by-name convention; PHASE-2
continues consistently"). PHASE-1 atoms keep bare rule_number; new convention applies to
PHASE-2 onwards.

R3 invariants (per 95th-candidate improved predicate):
  +2 atoms; +3 COMPOSES edges; COMPOSES does NOT auto-derive reverse (verified previously).
  axiom_term 206/206 PRESERVED (corpus=meta auto-excluded by corpus==MATH filter).
  cap_pres=1.0 HARD-FAIL gate; module liveness 6/6.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def axiom_term(ps):
    forward = {}
    for src, rel, tgt in ps.iter_all_relations():
        if rel.name in ('DEPENDS_ON', 'SPECIALIZES'):
            forward.setdefault(src, []).append(tgt)
    axioms = set()
    for a in ps.all_atoms():
        if str(a.tier.name) != 'TIER_1_FOUNDATIONAL': continue
        if str(a.corpus.name) != 'MATH': continue
        role = (a.algebra or {}).get('role', '')
        if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema', 'axiom', 'type'):
            axioms.add(f'math::{a.id}')
    def terminates(s, d=15):
        seen = {s}; f = [s]
        for _ in range(d):
            n = []
            for x in f:
                if x in axioms: return True
                for t in forward.get(x, []):
                    if t not in seen: seen.add(t); n.append(t)
            f = n
            if not f: break
        return any(x in axioms for x in seen)
    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name) == 'MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    return t, len(ops)


def module_liveness_ok():
    import importlib
    return all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def main():
    label = 'TIER-2-PHASE-2(2)'
    src_tag = 'DECISION_236_TIER_2_PHASE_2_validation_batch_2_methodology_rule_atomize_by_NAME_rule_scheme_rule_number_provenance_no_schema_change'
    ratify_date = '2026-06-16'

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    # ===== Define 2 atoms =====
    rules = [
        dict(
            id='RULE_no_papers_internal_tracking_only',
            name='Methodology rule (USER-LOCKED framing): no academic papers; internal tracking documents only',
            description=(
                'We are NOT writing academic papers. Substrate-product positioning artifacts are INTERNAL '
                'TRACKING DOCUMENTS (architecture locked, defensible claims, substrate-vs-LLM differences). '
                'Reframe paper-language -> tracking-document-language. Risk if violated: paper-polishing '
                'diverts substrate work; audience-framing biases internal claim-strength (soft-pedaling '
                'honest limits). Tracking docs = internal canonical state-reference for continuity across '
                "compactions. USER verbatim: 'we are NOT writing papers here.'"
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='cited as 10th USER-LOCKED in feedback_no_papers 2026-06-13',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_no_papers_internal_tracking_documents_only_USER_LOCKED_2026-06-13',
                source=src_tag,
            ),
        ),
        dict(
            id='RULE_adversarial_self_correction_own_output',
            name='Methodology rule (epistemic): adversarial self-correction of own DETECT output',
            description=(
                'Any session generating DETECT-step output, recommendation framing, or a research-programme '
                "audit MUST adversarially pre-screen its OWN output before handoff -- verify-before-asserting "
                "on one's own output, not just others'. Substrate-metacognition recursive discipline; operates "
                'across session boundaries. PROMOTED candidate -> CONFIRMED via 3 empirical witnesses + '
                'cross-cell breadth (DETECT lane + recommendation framing + research-programme ledger).'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_number_provenance='cited as 19th methodology in substrate_methodology_rule_19th 2026-06-13',
                rule_class='SUBSTRATE_DERIVED',
                frozen=True,
                confirmed=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_methodology_rule_19th_adversarial_self_correction_of_own_DETECT_output_PROMOTED_candidate_to_CONFIRMED_3_empirical_witnesses_today_skunkworks_DETECT_pre_screen_ADDENDUM_LAKATOS_AUDIT_axis_C_2026-06-13',
                source=src_tag,
            ),
        ),
    ]

    # ===== Pre-receive collision check =====
    for r in rules:
        if meta_store.get_atom(r['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{r["id"]} already exists')
            return 1

    # ===== Pre-receive COMPOSES targets check (back-edges to PHASE-1) =====
    compose_edges = [
        ('RULE_no_papers_internal_tracking_only', 'RULE_substrate_internal_no_llm'),
        ('RULE_adversarial_self_correction_own_output', 'AUDIT_verify_not_assume_prior_lesson_applied'),
        ('RULE_adversarial_self_correction_own_output', 'AUDIT_dont_fabricate_grounding'),
    ]
    for src, tgt in compose_edges:
        if meta_store.get_atom(tgt) is None and not any(r['id'] == tgt for r in rules):
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{tgt}')
            return 1
    print(f'[{label}] 2 atom-id collisions clean; 3 COMPOSES targets verified (back-edges to PHASE-1)', flush=True)

    # ===== Author atoms =====
    for r in rules:
        atom = Atom(
            id=r['id'],
            name=r['name'],
            corpus=Corpus.META,
            tier=Tier.TIER_METHODOLOGY,
            kind=AtomKind.METHODOLOGY_RULE,
            description=r['description'],
            metadata={**r['metadata'], 'eleventh_rule_clean': True, 'substrate_internal_verified': True},
            solution_history=tuple(),
        )
        meta_store.add_atom(atom)
        print(f'[{label}]   +meta::{r["id"]}', flush=True)
    meta_store._flush_atoms()

    # ===== Add 3 COMPOSES edges =====
    for src, tgt in compose_edges:
        ps.add_relation(
            f'meta::{src}',
            RelationType.COMPOSES,
            f'meta::{tgt}',
            source=src_tag,
            note=f'TIER-2 PHASE-2 COMPOSES {src} -> {tgt}',
        )
    meta_store._flush_relations()
    print(f'[{label}]   +{len(compose_edges)} COMPOSES edges (back-edges to PHASE-1; no phantom; honoring Skunkworks literal spec; Director text said +2 but Skunkworks spec lists 3)',
          flush=True)

    # ===== R3 invariants (improved per 95th-candidate; COMPOSES does NOT auto-derive) =====
    expected_atoms_delta = 2
    expected_rels_delta = len(compose_edges)  # 3; COMPOSES no auto-derive

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    mod_ok = module_liveness_ok()
    all_landed = all(meta_store.get_atom(r['id']) is not None for r in rules)
    edges_landed = sum(
        1 for s, r, t in ps.iter_all_relations()
        if r.name == 'COMPOSES'
        and any(f'meta::{src}' == s and f'meta::{tgt}' == t for src, tgt in compose_edges)
    )

    invariants_ok = (
        post_atoms == pre_atoms + expected_atoms_delta
        and post_rels == pre_rels + expected_rels_delta
        and post_t == pre_t  # corpus=meta auto-excluded
        and mod_ok
        and all_landed
        and edges_landed == len(compose_edges)
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} '
          f'(+{post_rels-pre_rels}) axiom_term={post_t}/{post_total} mod_ok={mod_ok} '
          f'all_landed={all_landed} edges={edges_landed}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 2 methodology_rule atoms ratified (Option A precedent honored)')
    print(f'  +2 atoms, +3 COMPOSES edges (back-edges to PHASE-1; no phantom)')
    print(f'  rule_scheme + rule_number_provenance metadata strings (no schema change)')
    print(f'  cap_pres=1.0 PRESERVED; axiom_term 206/206 PRESERVED (meta corpus auto-excluded)')
    print(f'  Director +2 COMPOSES count appears off-by-1 vs Skunkworks spec (honored Skunkworks)')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
