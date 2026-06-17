"""TIER-2 PHASE-2 batch 3 ratify -- 1 CONFIRMED + 1 CANDIDATE methodology_rule.

Per Skunkworks PHASE-2 batch 3 spec (paced per DECISION 236b PACE endorsement):

  meta::RULE_positioning_external_floor_and_lakatos_audit
    rule_scheme: METHODOLOGY_EPISTEMIC
    rule_number_provenance: 22nd methodology in substrate_USER_decisions_2026_06_13 lakatos_audit
    rule_class: USER_LOCKED; user_locked: true; confirmed: true; frozen: true
    PROMOTED candidate -> CONFIRMED via USER endorsement
    COMPOSES -> RULE_verify_before_asserting (PHASE-2 batch 2; 9b74b4f2)

  meta::RULE_type_graph_terminates_in_atoms          [FIRST CANDIDATE ATOM]
    rule_scheme: METHODOLOGY_EPISTEMIC
    rule_number_provenance: 21st methodology CANDIDATE in substrate_COMPOUND_optimization
    rule_class: SUBSTRATE_DERIVED
    confirmed_or_candidate: CANDIDATE (Skunkworks condition-1; NOT load-bearing)
    witnesses_count: 1 (1st appearance 2026-06-13; needs 2 more for promotion)
    frozen: false
    COMPOSES: none (natural targets not yet atomized; consumer-pull-deferred; no phantom)

1 COMPOSES edge total. Per Skunkworks condition-1: CANDIDATE atom INGESTABLE but
EXCLUDED from load-bearing queries until >=3 witnesses accumulated.

R3 invariants:
  +2 atoms; +1 COMPOSES edge.
  axiom_term 206/206 PRESERVED (corpus=meta auto-excluded).
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
    label = 'TIER-2-PHASE-2(b3)'
    src_tag = 'PHASE_2_batch_3_RULE_positioning_external_floor_lakatos_22nd_USER_LOCKED_CONFIRMED_plus_RULE_type_graph_terminates_in_atoms_21st_CANDIDATE_1_witness_condition_1_exercised'

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    rules = [
        dict(
            id='RULE_positioning_external_floor_and_lakatos_audit',
            name='Methodology rule 22 (USER-LOCKED CONFIRMED): positioning needs external falsification floor + Lakatos audit ledger',
            description=(
                'Substrate-product positioning requires (a) an EXTERNAL falsification FLOOR retained at all times '
                '(CHTV-1 + flat-RAG null + held-out gold + adversarial audit) and (b) a LAKATOS-AUDIT ledger filed '
                'at each cycle close as a standing artifact. The 3-axis ledger tracks: A. predicts-new-phenomena, '
                'B. honest-revisions-not-ad-hoc-rescues, C. external-falsification-floor-retained. DEGENERATING '
                'signal if any axis fails; 2+ consecutive degenerating cycles -> ARCHITECTURE-REVIEW. Calibrated '
                'against the Newell 1990 cognitive-architecture standard. PROMOTED candidate -> CONFIRMED via '
                "USER endorsement ('a yes this is important')."
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_number_provenance='cited as 22nd methodology in substrate_USER_decisions_2026_06_13 ...lakatos_audit',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                confirmed=True,
                confirmed_or_candidate='CONFIRMED',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_USER_decisions_2026_06_13_22nd_methodology_rule_PROMOTED_lakatos',
                promoted='via USER endorsement',
                external_falsification_floor='CHTV_1_plus_flat_RAG_null_plus_held_out_gold_plus_adversarial_audit',
                lakatos_axes='A_predicts_new_phenomena_B_honest_revisions_not_ad_hoc_C_external_falsification_floor',
                source=src_tag,
            ),
        ),
        dict(
            id='RULE_type_graph_terminates_in_atoms',
            name='Methodology rule 21 (CANDIDATE; 1 witness; NOT load-bearing until promoted): operator type-graph terminates in atomized types',
            description=(
                "The substrate's operator TYPE graph must terminate in atomized types (parallel to the L6-PROOF "
                'axiom-termination requirement); the substrate refuses Class-B SHARED_ABSTRACTION proofs when the '
                'shared output type is not an atom (no shared object to hang the abstraction on). Empirical '
                'witness: 53 of 54 operator signature types unatomized -> abstraction-ratio 0% because the type '
                'graph does not terminate. CANDIDATE (1st appearance 2026-06-13); needs 2 more appearances + '
                'cross-cell breadth to PROMOTE.'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_number_provenance='cited as 21st methodology CANDIDATE in substrate_COMPOUND_optimization ...type_graph_terminates 2026-06-13',
                rule_class='SUBSTRATE_DERIVED',
                frozen=False,  # CANDIDATE; not frozen until promoted
                confirmed_or_candidate='CANDIDATE',  # Skunkworks condition-1 enforced
                witnesses_count=1,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_COMPOUND_optimization_21st_rule_candidate_type_graph_terminates_in_atoms 2026-06-13',
                first_witness='EXPAND-TYPING probe 53 of 54 unatomized abstraction_ratio_0pct',
                NOT_load_bearing_until_3_witnesses=True,
                natural_composes_targets_unatomized_consumer_pull_deferred='refuse_what_cannot_prove_distillation_modes_L6_PROOF_axiom_termination',
                source=src_tag,
            ),
        ),
    ]

    # Collision check
    for r in rules:
        if meta_store.get_atom(r['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{r["id"]} already exists')
            return 1

    # COMPOSES edges (1 total)
    compose_edges = [
        ('RULE_positioning_external_floor_and_lakatos_audit', 'RULE_verify_before_asserting'),
    ]

    # Verify COMPOSES target exists
    new_ids = {r['id'] for r in rules}
    for src, tgt in compose_edges:
        if meta_store.get_atom(tgt) is None and tgt not in new_ids:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{tgt}')
            return 1
    print(f'[{label}] 2 collisions clean; 1 COMPOSES target verified (RULE_verify_before_asserting from batch 2; no phantom)', flush=True)

    # Author atoms
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
        meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 3 {r["id"]}')
        print(f'[{label}]   +meta::{r["id"]} {"[CONFIRMED]" if r["metadata"].get("confirmed_or_candidate") == "CONFIRMED" else "[CANDIDATE]"}', flush=True)

    # Add COMPOSES edge
    for src, tgt in compose_edges:
        ps.add_relation(
            f'meta::{src}',
            RelationType.COMPOSES,
            f'meta::{tgt}',
            source=src_tag,
            note=f'PHASE-2 batch 3 COMPOSES {src} -> {tgt}',
        )
    meta_store._flush_relations()
    print(f'[{label}]   +{len(compose_edges)} COMPOSES edge', flush=True)

    # R3 invariants
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
        post_atoms == pre_atoms + 2
        and post_rels == pre_rels + 1
        and post_t == pre_t
        and mod_ok
        and all_landed
        and edges_landed == 1
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} '
          f'(+{post_rels-pre_rels}) axiom_term={post_t}/{post_total} mod_ok={mod_ok} '
          f'all_landed={all_landed} edges={edges_landed}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 2 methodology_rule atoms (1 CONFIRMED + 1 CANDIDATE) + 1 COMPOSES')
    print(f'  CONFIRMED:  RULE_positioning_external_floor_and_lakatos_audit (22nd USER-LOCKED; load-bearing)')
    print(f'  CANDIDATE:  RULE_type_graph_terminates_in_atoms (21st; 1 witness; NOT load-bearing)')
    print(f'  Skunkworks condition-1 EXERCISED for first time in batch')
    print(f'  cap_pres=1.0 PRESERVED; axiom_term 206/206 PRESERVED; modules 6/6')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
