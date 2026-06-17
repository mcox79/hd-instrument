"""TIER-2 PHASE-2 batch 8 ratify -- 2 USER-LOCKED-framing rules CONFIRMED."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def main():
    label = 'TIER-2-PHASE-2(b8)'
    src_tag = 'PHASE_2_batch_8_RULE_always_reconsider_frameworks_7th_USER_LOCKED_CONFIRMED_RULE_never_go_passive_12th_USER_LOCKED_CONFIRMED_glob_re_check_self_correction'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    rules = [
        dict(
            id='RULE_always_reconsider_frameworks',
            name='Methodology rule 7 (USER-LOCKED CONFIRMED): always reconsider frameworks; do not lock in prematurely',
            description=(
                'Every architectural framework + methodology rule + substrate-product positioning claim MUST be '
                'periodically RECONSIDERED. Convergence FEELING right is NOT evidence of truth -- it can be '
                'confirmation bias + authoring momentum. At each cycle close: file an explicit alternatives-not-'
                'yet-considered entry. After any major architectural commit: dispatch a deep drill on alternatives '
                "with 'convergence might be confirmation bias' framing; cross-check 3+ alternatives + report "
                'honestly which is more faithful + what to retain. Do NOT commit to schema migrations / KP '
                'operator additions / methodology-rule promotions without alternatives considered + verdict filed. '
                "USER verbatim 2026-06-13 (after catching the 3-axis architecture shipped in rapid momentum-"
                "convergence): 'make sure we're reconsidering this as we go - we don't want to get locked into "
                "something and overlook potentially more useful frameworks.'"
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='cited as 7th USER-LOCKED behavioral rule in feedback_always_reconsider_frameworks 2026-06-13',
                rule_class='USER_LOCKED',
                user_locked=True,
                confirmed_or_candidate='CONFIRMED',
                confirmed=True,
                frozen=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_always_reconsider_frameworks_dont_lock_in_prematurely_USER_LOCKED 2026-06-13',
                source=src_tag,
            ),
            composes=['RULE_verify_before_asserting'],
        ),
        dict(
            id='RULE_never_go_passive',
            name='Methodology rule 12 (USER-LOCKED CONFIRMED): a session NEVER goes passive; 13th + 14th operationalize this',
            description=(
                'A session NEVER goes passive. Even when monitors catch no new inbox events, work constantly on '
                'own-lane outputs (tracking-doc updates, formal specs, memory entries, methodology grading, drill '
                'dispatches, check-in routing to other sessions). STANDING IS NOT THE ANSWER when there is own-lane '
                'work to do. ONLY actually stand when working+checking would be wasteful (e.g. brief wait '
                'immediately after dispatching, before results land). Originally Research-scoped; generalized to '
                "all sessions. USER verbatim 2026-06-13 (after catching ~1h passive window): 'you should always "
                "be working. there are probably other sessions waiting on you.' Operationalized by the 13th "
                'active-state-check + the 14th no-stand-default.'
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='cited as 12th USER-LOCKED rule in feedback_research_never_goes_passive 2026-06-13',
                rule_class='USER_LOCKED',
                user_locked=True,
                confirmed_or_candidate='CONFIRMED',
                confirmed=True,
                frozen=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_research_never_goes_passive_USER_LOCKED 2026-06-13',
                operationalized_by='13th_active_state_check_plus_14th_no_stand_default',
                parent_of_family='operationalization_family_13th_14th_state_waiting_cycle_check',
                source=src_tag,
            ),
            composes=['RULE_active_state_check', 'RULE_no_stand_default'],
        ),
    ]

    # Collision + COMPOSES checks
    for r in rules:
        if meta_store.get_atom(r['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{r["id"]} already exists')
            return 1
    targets = set()
    for r in rules:
        targets.update(r['composes'])
    for t in targets:
        if meta_store.get_atom(t) is None:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{t}')
            return 1
    print(f'[{label}] 2 collisions clean; {len(targets)} COMPOSES targets verified', flush=True)

    n_edges = 0
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
        meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 8 {r["id"]}')
        print(f'[{label}]   +meta::{r["id"]} [CONFIRMED + USER_LOCKED]', flush=True)
        for tgt in r['composes']:
            ps.add_relation(
                f'meta::{r["id"]}',
                RelationType.COMPOSES,
                f'meta::{tgt}',
                source=src_tag,
                note=f'PHASE-2 batch 8 COMPOSES {r["id"]} -> {tgt}',
            )
            n_edges += 1
    meta_store._flush_relations()
    print(f'[{label}]   +{n_edges} COMPOSES edges', flush=True)

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    invariants_ok = (
        post_atoms == pre_atoms + 2
        and post_rels == pre_rels + n_edges
        and all(meta_store.get_atom(r['id']) is not None for r in rules)
    )
    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)
    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1
    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 2 USER-LOCKED CONFIRMED methodology atoms + 3 COMPOSES')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
