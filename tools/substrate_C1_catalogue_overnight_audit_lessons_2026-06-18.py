"""C1 (Skunkworks solo): catalogue the 4 overnight audit-discipline lessons.

Per Amendment-3 (COMPOSE-don't-proliferate) + no-double-counting (each witness at its
SINGLE most-precise parent):
  (c) GATE-0-plausibility-per-cell-workload-fast-not-fake = NEW atom (instance 92; CONFIRMED;
      3 cross-witnesses A4/A1/A3). The SYMMETRIC counterpart to run-mode-smoke family.
  (a) cron-LISTED != cron-FIRED -> WITNESS to 81 (monitor-must-watch / producer-liveness-
      false-green; exact match). 81 w 2->3.
  (b) Store DROPS relation metadata on flush -> WITNESS to 80 (verify-the-referent; set !=
      persisted). 80 w 7->8.
  (d) A1 metric-conflation (t_sparse vs net_speedup) -> WITNESS to 83 (metric-mismatch /
      test-mechanism-on-claimed-benefit; precise+confirmed). 83 w 3->4.
  (75 unchanged: overlaps 83; same A1 observation would double-count.)

Net: +1 NEW atom (47->48) + 3 witness-strengthenings. NOT +4 (the plan's ~51 assumed all-new).
Gated: axiom_term 206/206 + cap_pres 6/6 HARD-FAIL gate (pre+post). Serial; fresh-load.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


NEW_ATOM = {
    'id': 'AUDIT_gate0_plausibility_per_cell_workload_fast_not_fake',
    'name': 'Audit lesson (CONFIRMED; instance 92; verify): gate0-plausibility-per-cell-workload-fast-not-fake',
    'description': (
        "GATE-0 plausibility is PER-CELL-WORKLOAD, not a universal wall-time threshold. A fast completion "
        "is a TELL to CHECK (structural: n_cells_emitted == n_cells_declared + run_mode==full + "
        "metrics_source==measured_* + elapsed plausible FOR THIS CELL'S declared workload), NOT a gate "
        "(a wall-time floor REJECTS legitimate fast-real-full runs). The SYMMETRIC COUNTERPART to the "
        "run-mode-smoke family: those guard against OVER-claiming from smoke; this guards against the "
        "OPPOSITE error -- rejecting a fast-but-real full run as fake. Verify the per-cell REFERENT "
        "(actual emitted cells + measured fields), never the clock. Witnesses: A4 stall-misframe "
        "(queue-status=completed read as stalled vs runner-log authoritative), A1 8s-confusion (21-cell "
        "ms-profiler legitimately ~8s), A3 35s-overspec (80-cell x 3-seed measured legitimately 35s; the "
        "cert-owner's OWN elapsed>>120 GATE-0 condition was WRONG and self-corrected). Composes with "
        "degenerate-regime-not-refutation (79) + run-mode-discipline family + verify-the-referent (80)."
    ),
    'lesson_class': 'verify',
    'instance_number': 92,
    'witnesses_count': 3,
    'witnesses': [
        'A4 stall-misframe (queue.json status=completed read as stalled; runner-log is the authoritative did-it-run referent)',
        'A1 8s-confusion (21-cell ms-attribution-profiler legitimately ~8s; flagged-then-cleared via runner-log-first)',
        'A3 35s-overspec (80-cell x 3-seed measured envelope legitimately 35s; cert-owner OWN elapsed>>120 condition WRONG, self-corrected: wall-time is a TELL not a GATE)',
    ],
    'composes_with': [
        'AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict',
        'run_mode_smoke_discipline_family_48_49_51_63',
        'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
    ],
    'source': (
        'C1_catalogue_overnight_2026_06_18_skunkworks_solo_symmetric_counterpart_run_mode_smoke_'
        'fast_not_fake_gate_on_per_cell_workload_structural_not_walltime_3_witnesses_a4_a1_a3'
    ),
}

# witness additions: each at its SINGLE most-precise parent (no double-counting)
WITNESS_UPDATES = {
    'AUDIT_monitor_must_watch_authoritative_source_not_derived_log_producer_liveness_false_green': {
        'inc': 1,
        'witness': (
            'cron LISTED in CronList != cron FIRED (USER-caught ~7h hourly-check-in gap 2026-06-18; the '
            'cron object persisted/alive in CronList but the scheduler never fired post-compaction; '
            'durable:true did not persist either; watch the OUTPUT [check-in notes actually sent] not the '
            'derived signal [CronList existence] -- producer-listed != delivered)'
        ),
    },
    'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer': {
        'inc': 1,
        'witness': (
            'Store DROPS relation metadata on flush (store.py:115-126 _flush_relations rebuilds every '
            'Relation from _all_relations, a set of (src,rel_type,tgt) 3-TUPLES with no metadata -> a '
            'write/set succeeding != the data PERSISTING; typed-edge sub-roles strengthens/mechanism_for '
            'silently dropped; verify the PERSISTED form has what you set, 2026-06-18 Skunkworks)'
        ),
    },
    'AUDIT_metric_mismatch_test_mechanism_on_its_claimed_benefit_switch_metrics_once_principled_pre_registered': {
        'inc': 1,
        'witness': (
            'A1 8a attribution measured t_sparse (ABSOLUTE) but the canonical 8a non-monotonicity is in '
            'net_speedup (the RATIO t_dense/t_sparse) -> measured the WRONG quantity; t_sparse-monotone '
            'says nothing about net_speedup-non-monotonicity; test the mechanism on ITS claimed metric '
            '(2026-06-18 Skunkworks + Exp-Dev converged independently)'
        ),
    },
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
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL.'); return 1

    by_id = {a.id: a for a in ps.all_atoms()}

    # --- 1. witness updates (serial; each at single most-precise parent) ---
    for aid, upd in WITNESS_UPDATES.items():
        a = by_id.get(aid)
        if a is None:
            print(f'  WARN: target not found, skipping: {aid}'); continue
        md = dict(a.metadata or {})
        old_wc = int(md.get('witnesses_count', 0))
        md['witnesses_count'] = old_wc + upd['inc']
        lst = list(md.get('added_witnesses_2026_06_18_skunkworks', []))
        lst.append(upd['witness'])
        md['added_witnesses_2026_06_18_skunkworks'] = lst
        new = Atom(id=a.id, name=a.name, description=a.description, kind=a.kind,
                   tier=a.tier, corpus=a.corpus, algebra=a.algebra, metadata=md)
        ps.add_atom(new, source='C1_catalogue_overnight_2026_06_18', note=f'witness +{upd["inc"]} (w {old_wc}->{md["witnesses_count"]})')
        print(f'  ~ witness +{upd["inc"]}: {aid[:50]}  w {old_wc}->{md["witnesses_count"]}')

    # --- 2. new atom (lesson c) ---
    new_id = NEW_ATOM['id']
    if new_id in by_id:
        print(f'  SKIP new (already present): {new_id}')
    else:
        meta = {
            'lesson_class': NEW_ATOM['lesson_class'],
            'confirmed_or_candidate': 'CONFIRMED',
            'witnesses_count': NEW_ATOM['witnesses_count'],
            'witnesses': NEW_ATOM['witnesses'],
            'instance_number': NEW_ATOM['instance_number'],
            'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
            'NOT_load_bearing_until_3_witnesses': False,
            'prose_source': 'skunkworks_to_testbed_research_C1_audit_lesson_compose_vs_new_rulings_1_new_3_witnesses_not_4_2026-06-18.md',
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'composes_with': NEW_ATOM['composes_with'],
            'verify_the_referent_family': True,
            'symmetric_counterpart_of': 'run_mode_smoke_family',
            'source': NEW_ATOM['source'],
        }
        atom = Atom(id=new_id, name=NEW_ATOM['name'], description=NEW_ATOM['description'],
                    kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META,
                    algebra=None, metadata=meta)
        ps.add_atom(atom, source='C1_catalogue_overnight_2026_06_18', note='NEW CONFIRMED 3 witnesses A4/A1/A3')
        print(f'  + NEW: {new_id} (CONFIRMED; instance 92; 3 witnesses)')

    # --- post gates ---
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    gate_ok = post_axiom == 206 and post_mod
    print('=' * 72)
    print(f'POST: atoms={post_n} (delta +{post_n - pre_n})  axiom_term={post_axiom}  cap_pres={post_mod}  -> {"OK" if gate_ok else "HARD_FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: axiom_term or cap_pres changed. INVESTIGATE.'); return 2
    print('C1 catalogue COMPLETE: +1 NEW (gate0-per-cell-workload) + 3 witnesses (80,81,83); axiom_term 206/206 + cap_pres PRESERVED.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
