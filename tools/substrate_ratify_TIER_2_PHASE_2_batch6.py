"""TIER-2 PHASE-2 batch 6 ratify -- 1 atom RULE_gap_driven_promotion_loop CANDIDATE."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind


def main():
    label = 'TIER-2-PHASE-2(b6)'
    src_tag = 'PHASE_2_batch_6_RULE_gap_driven_promotion_loop_CANDIDATE_2_witnesses_user_origin_by_name_flagged_number'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    new_id = 'RULE_gap_driven_promotion_loop'
    if meta_store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: meta::{new_id} already exists')
        return 1

    atom = Atom(
        id=new_id,
        name='Methodology rule (CANDIDATE; 2 witnesses; by-name per DECISION 236/238): gap-driven promotion loop',
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        kind=AtomKind.METHODOLOGY_RULE,
        description=(
            "The gap-driven promotion loop -- the USER concept 'use successful results to form the foundation' made "
            'operational END-TO-END substrate-internal (no LLM, no external truth). Architecture: a Validated win '
            '(scorecard HARD_PASS) + a Documented gap (F1/F2/...) + a Skunkworks audit signature + the 3-of-3 '
            'PROMOTION GATE (cap_pres=1.0 + re-expressibility-as-composition + load-bearing) + the 4-gate pre-check '
            '(forward-walk + corpus-monotone + axiom-term + dangling) + Testbed atomic ratify => a LOAD-BEARING '
            'substrate atom (pre-certified material grows the core). FORM-A (closes-a-gap) vs FORM-P (serves-a-'
            'capability-with-MEASURED-utility) distinction prevents over-claim across promotion forms. Empirically '
            'operational: 2 PROMOTIONS executed substrate-internal.'
        ),
        metadata=dict(
            rule_scheme='METHODOLOGY_EPISTEMIC',
            rule_number_provenance=(
                "informally referenced as '15th methodology' in Skunkworks batch-status; the canonical source "
                'substrate_USER_gap_driven_loop_empirically_operational assigns NO canonical number. Atomized BY '
                'NAME per DECISION 236/238 numbering convention; canonical number UNCONFIRMED (do-not-fabricate).'
            ),
            rule_class='SUBSTRATE_DERIVED',
            user_origin=True,
            user_origin_quote="USER: 'use successful results to form the foundation'",
            confirmed_or_candidate='CANDIDATE',
            witnesses_count=2,
            frozen=False,
            NOT_load_bearing_until_3_witnesses=True,
            term_class='PROCESS_KNOWLEDGE_NON_MATH',
            prose_source='substrate_USER_gap_driven_loop_empirically_operational 2026-06-15/16',
            first_witness='PROMOTION #1 kgram_context_binding (closes F1; commit 6615e7a5)',
            witness_2='PROMOTION #2 theta_burst_write (closes multi-step recall; commit 1e2df579)',
            witness_atoms_in_math_corpus_not_COMPOSES='cross_corpus_witness_link_not_methodology_composition_avoids_questionable_edge',
            natural_composes_targets_unatomized='3_of_3_promotion_gate_rule_plus_4_gate_pre_check_rule_consumer_pull_deferred',
            eleventh_rule_clean=True,
            substrate_internal_verified=True,
            source=src_tag,
        ),
        solution_history=tuple(),
    )
    meta_store.add_atom(atom, source=src_tag, note='gap-driven promotion loop CANDIDATE user-origin')
    print(f'[{label}]   +meta::{new_id} [CANDIDATE; 2 witnesses; user_origin]', flush=True)

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels
        and meta_store.get_atom(new_id) is not None
    )
    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)
    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1
    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 1 methodology_rule CANDIDATE; 2 witnesses (USER-origin)')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
