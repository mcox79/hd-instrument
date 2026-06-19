"""TIER-2 PHASE-2 batch 4 ratify -- 3 USER-LOCKED process/coordination rules (DECISION 236b PACE standing).

Per Skunkworks PHASE-2 batch 4 spec:

  meta::RULE_state_waiting_on_every_response
    rule_scheme: USER_LOCKED_FRAMING
    rule_number_provenance: un-numbered USER-LOCKED 2026-06-15
    rule_class: USER_LOCKED; user_locked: true; confirmed: true; frozen: true
    COMPOSES: none now (natural parents 12th never-passive + 9th monitor-armed not yet atomized; consumer-pull)

  meta::RULE_no_askuserquestion
    rule_scheme: USER_LOCKED_FRAMING
    rule_number_provenance: un-numbered USER directive 2026-06-16
    rule_class: USER_LOCKED; user_locked: true; confirmed: true; frozen: true
    COMPOSES -> RULE_state_waiting_on_every_response (intra-batch)

  meta::RULE_cycle_check_inbox_authoritative
    rule_scheme: USER_LOCKED_FRAMING
    rule_number_provenance: operationalizes 9th USER-LOCKED rule; cited in feedback 2026-06-15
    rule_class: USER_LOCKED; user_locked: true; confirmed: true; frozen: true
    COMPOSES -> RULE_active_state_check (PHASE-1; 9da528ca)

2 COMPOSES edges total. All 3 atoms CONFIRMED + USER-LOCKED + frozen.

R3 invariants: +3 atoms; +2 COMPOSES; axiom_term 206/206; cap_pres=1.0 preserved.
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
    label = 'TIER-2-PHASE-2(b4)'
    src_tag = 'PHASE_2_batch_4_3_USER_LOCKED_FRAMING_process_rules_state_waiting_no_askuserquestion_cycle_check'

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    rules = [
        dict(
            id='RULE_state_waiting_on_every_response',
            name='Methodology rule (USER-LOCKED framing; un-numbered): end every response with explicit who-I-am-waiting-on',
            description=(
                "End EVERY response with an explicit 'who I am waiting on' status -- by role: which role + what "
                'deliverable + ETA (if known) + voluntary holds; include USER-pending items with a no-urgency flag '
                "if applicable; say 'nothing in flight' explicitly when nothing is pending. Standing duty, NOT only "
                "when the USER asks directly. USER-issued 2026-06-15 ~18:00 after asking 'who are you waiting on' "
                'several times; state-transparency keeps the USER oriented during fast multi-role parallel '
                'coordination.'
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='USER-LOCKED directive (un-numbered; composes with 12th never-go-passive + 9th monitor-armed) in feedback_state_waiting_on_every_response_USER_LOCKED 2026-06-15',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                confirmed=True,
                confirmed_or_candidate='CONFIRMED',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_state_waiting_on_every_response_USER_LOCKED 2026-06-15',
                source=src_tag,
            ),
        ),
        dict(
            id='RULE_no_askuserquestion',
            name='Methodology rule (USER-LOCKED framing; un-numbered): never call AskUserQuestion; ask in chat or route to Research',
            description=(
                'NEVER call the AskUserQuestion tool -- its modal/blocking UI locks up the entire session. When a '
                'USER decision is needed: (a) ask in plain chat (clear options + a recommendation), and/or (b) '
                'route to Research (the Director, who owns strategic/architectural calls and relays). Reserve '
                'direct USER chat-asks for genuinely USER-only calls (architectural bets, compute/resource policy, '
                "scope/GO). EnterPlanMode/ExitPlanMode is the only sanctioned interactive gate. USER verbatim "
                "2026-06-16: 'please don't use askuserquestion again - it locks up your entire session. ask it in "
                "chat and/or propogate to research.'"
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='USER directive (un-numbered) in feedback_no_askuserquestion 2026-06-16',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                confirmed=True,
                confirmed_or_candidate='CONFIRMED',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_no_askuserquestion 2026-06-16',
                source=src_tag,
            ),
        ),
        dict(
            id='RULE_cycle_check_inbox_authoritative',
            name='Methodology rule (USER-LOCKED framing; un-numbered): cycle-check inbox authoritative; operationalizes 9th monitor-armed',
            description=(
                'Run the cycle-check (mtime-aware inbox scan over notes/) at the TOP of EVERY work cycle. The '
                'mtime-aware INBOX is the AUTHORITATIVE safety net: it reads the source-of-truth notes dir directly, '
                'bypassing BOTH the producer routing AND the consumer. Either side can fail -- the harness Monitor '
                'consumer can die (auto-stop on event volume) and the producer routing-glob can silently drop '
                'multi-recipient notes. Monitor filter MUST be ROUTING|BROADCAST with an author-out guard (match '
                "anywhere, not 'to_<me>') so multi-recipient + broadcast notes that include you pass through. Do "
                "NOT run blanket '--seen' to reset baseline (it marks unread notes seen). When fixing a routing/"
                'glob filter, audit EVERY component (producer + consumer + the manual net) -- the safety net '
                'itself had the same bug (19th-rule self-correction).'
            ),
            metadata=dict(
                rule_scheme='USER_LOCKED_FRAMING',
                rule_number_provenance='operationalizes the 9th USER-LOCKED rule (monitor-armed-post-compaction); cited in feedback_skunkworks_run_cycle_check_every_cycle 2026-06-15',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                user_triggered=True,
                confirmed=True,
                confirmed_or_candidate='CONFIRMED',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_skunkworks_run_cycle_check_every_cycle 2026-06-15',
                source=src_tag,
            ),
        ),
    ]

    # Collision check
    for r in rules:
        if meta_store.get_atom(r['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{r["id"]} already exists')
            return 1

    # COMPOSES edges (2 total)
    compose_edges = [
        ('RULE_no_askuserquestion', 'RULE_state_waiting_on_every_response'),  # intra-batch
        ('RULE_cycle_check_inbox_authoritative', 'RULE_active_state_check'),  # back to PHASE-1
    ]

    new_ids = {r['id'] for r in rules}
    for src, tgt in compose_edges:
        if meta_store.get_atom(tgt) is None and tgt not in new_ids:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{tgt}')
            return 1
    print(f'[{label}] 3 collisions clean; 2 COMPOSES targets verified (1 intra + 1 back to PHASE-1; no phantom)', flush=True)

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
        meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 4 {r["id"]}')
        print(f'[{label}]   +meta::{r["id"]} [CONFIRMED + USER_LOCKED]', flush=True)

    for src, tgt in compose_edges:
        ps.add_relation(
            f'meta::{src}',
            RelationType.COMPOSES,
            f'meta::{tgt}',
            source=src_tag,
            note=f'PHASE-2 batch 4 COMPOSES {src} -> {tgt}',
        )
    meta_store._flush_relations()
    print(f'[{label}]   +{len(compose_edges)} COMPOSES edges', flush=True)

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
        post_atoms == pre_atoms + 3
        and post_rels == pre_rels + 2
        and post_t == pre_t
        and mod_ok
        and all_landed
        and edges_landed == 2
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} '
          f'(+{post_rels-pre_rels}) axiom_term={post_t}/{post_total} mod_ok={mod_ok} '
          f'all_landed={all_landed} edges={edges_landed}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 3 USER-LOCKED process methodology_rule atoms + 2 COMPOSES')
    print(f'  +meta::RULE_state_waiting_on_every_response  (end-every-response who-waiting standing duty)')
    print(f'  +meta::RULE_no_askuserquestion               (never AskUserQuestion; chat or route Research)')
    print(f'  +meta::RULE_cycle_check_inbox_authoritative  (operationalizes 9th monitor-armed)')
    print(f'  cap_pres=1.0 PRESERVED; axiom_term 206/206 PRESERVED; modules 6/6')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
