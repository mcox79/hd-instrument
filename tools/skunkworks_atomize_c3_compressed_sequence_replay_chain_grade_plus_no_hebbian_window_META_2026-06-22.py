"""Deferred c3 atomization bundle (post-3-seed-remote-land follow-on to 29b7aff6).

c3 = exp_c3_compressed_sequence_replay_v1 (brain-drill #5 SWR sleep-replay)
Cell commit: a27939c5
3-seed remote_cpu metrics: data/exp_c3_compressed_sequence_replay_v1/metrics.json
  verdict=HARD_PASS  n_seeds=3 (7,17,23)  run_mode=full
  NONE@d5=0.000/cv=0.0
  COMPRESSED@d5=1.000/cv=0.0
  UNORDERED@d5=0.017/cv=0.7071  (order-discriminator fires; well under bar)
  ONLINE_NO_GAP@d5=1.000/cv=0.0  (software no-Hebbian-window honest-scope control)
  delta(B-A)@d5=1.000 >= HP bar 0.50
  order_delta(B-C)@d5=0.983 >= HP bar 0.30
  substrate_only_ok=True  W_unchanged_by_sleep_all_arms=True  zero_llm_calls=True
  elapsed=67s total

Two atoms (bundled):

ATOM 1 -- c3 chain-grade ratification (CERT 585 -> 586 against LIVE PRE state):
  id math::T3/EXP_c3_compressed_sequence_replay_v1
  kind EXPERIMENT_RECORD  corpus MATH  tier TIER_3_ALGORITHM
  pq CERT_CHAIN_GRADE  cert_class pre_reg_pass  verdict HARD_PASS  delta=+1

ATOM 2 -- META no-Hebbian-window honest-scope discipline (CERT-neutral):
  id META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing
  kind AUDIT_LESSON  corpus META  tier TIER_METHODOLOGY  algebra=None
  pq None  cert_class discipline_meta  delta=0

LIVE PRE state reconciled by Skunkworks against brief (brief said CERT 587; LIVE = 585; bundle
intent + LIVE-pinned post-state used; no overclaim):
  atoms 177277 -> 177279 (+1 chain-grade +1 META)
  CERT 585 -> 586 (chain-grade only; META is delta=0)
  ledger 647 -> 649 (+2 rows)
  axiom 206 preserved  cap_pres 6/6 preserved

A5 discipline:
  - PRE snapshot + idempotency-pre-check (no duplicate IDs)
  - foreground sequential execution (NOT run_in_background; deadlock risk on teardown)
  - Store add_atom auto-flush; re-load post-write to catch NULL-seam
  - cert_ledger row append with stable hash; path-scoped commit (no -A)
"""
from __future__ import annotations
import sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore, Atom
from backend.substrate_index.schema import Corpus, Tier, AtomKind
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    LEDGER_PATH,
    _read_ledger,
)


# =========================================================================
# A5 invariants (mirror cert_ledger_writer pattern)
# =========================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )


def _axiom_count(store):
    return sum(
        1 for a in store.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def _cap_pres_ok():
    import importlib
    return all(
        hasattr(importlib.import_module(m), s) for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


# =========================================================================
# Atom 1 -- c3 chain-grade experiment_record
# =========================================================================

C3_ATOM_ID = 'T3/EXP_c3_compressed_sequence_replay_v1'  # stored id (qualified id = math::<this>)
C3_ATOM_QID = 'math::T3/EXP_c3_compressed_sequence_replay_v1'
C3_ATOM_NAME = 'c3 compressed-sequence-replay v1 (brain-drill #5 SWR)'

C3_DESCRIPTION = (
    'Compressed sleep-replay sequence-binding test (brain-drill #5 sharp-wave-ripple). '
    'Tests whether a SEPARATE sequence-matrix S (ordered-pair offline replay) binds '
    'sequences over a content-store W, with W unchanged by the sleep pass. Synthetic-bipolar '
    'disjoint-key sequences at N_DIM=4096, K=20, N_SEQ=10, depths=[1,3,5,7,10]. Four arms: '
    'NONE (no sleep), COMPRESSED (offline ordered-pair replay through S), UNORDERED (shuffled '
    'pair order; order-discriminator control), ONLINE_NO_GAP (continuous online presentation; '
    'biological-Hebbian-window control). 3 seeds (7, 17, 23) on remote_cpu run_mode=full. '
    'Result: COMPRESSED@d5=1.000 (cv=0.0), NONE@d5=0.000, UNORDERED@d5=0.017 (well under bar), '
    'ONLINE_NO_GAP@d5=1.000. delta(B-A)=1.000 >= 0.50 HP bar; order_delta(B-C)=0.983 >= 0.30 HP '
    'bar. substrate_only_ok=True, W_unchanged_by_sleep_all_arms=True, zero_llm_calls=True. '
    'HARD_PASS. NOTE: ARM D (ONLINE_NO_GAP) matches ARM B EXACTLY -- software substrate has no '
    'Hebbian STDP temporal window, so the biological compression-schedule motivation does NOT '
    'transfer in silico; the architectural win is the SEPARATE S MATRIX (ordered-pair + W-vs-S '
    'separation), not the temporal-compression schedule (see sibling META atom).'
)

C3_ATOM_METADATA = {
    'provenance_quality': 'CERT_CHAIN_GRADE',
    'verdict': 'HARD_PASS',
    'relevance_tier': 'HIGH',
    'run_mode': 'full',
    'era': '2026-06-22',
    'config_version': (
        'c3-compressed-sequence-replay-v1: K=20 N_SEQ=10 N_DIM=4096 '
        'arms=NONE,COMPRESSED,UNORDERED,ONLINE_NO_GAP depths=[1, 3, 5, 7, 10]; '
        'bands HP_B@d5=0.80 delta=0.50 order_delta=0.30 compression_ratio=20 '
        'sleep_pass_count=1 run_mode=full'
    ),
    'experiment_path': 'experiments/exp_c3_compressed_sequence_replay_v1.py',
    'metrics_path': 'data/exp_c3_compressed_sequence_replay_v1/metrics.json',
    'prereg_path': 'notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md',
    'dispatch_note': 'notes/c3_compressed_sequence_replay_v1_dispatched_2026-06-22.md',
    'cross_check_note': 'notes/c3_honest_scope_software_has_no_hebbian_window_META_proposal_2026-06-22.md',
    'cell_sha': 'a27939c5',
    'remote_queue': 'remote_cpu',
    'corpus_provenance': 'synthetic_bipolar_keys_sequences',
    'n_seeds': 3,
    'seeds': [7, 17, 23],
    'arms_tested': ['NONE', 'COMPRESSED', 'UNORDERED', 'ONLINE_NO_GAP'],
    'metric_headline': (
        'COMPRESSED@d5=1.000 cv=0.000 ; NONE@d5=0.000 ; UNORDERED@d5=0.017 cv=0.7071 ; '
        'ONLINE_NO_GAP@d5=1.000 cv=0.000 ; delta=1.000 ; order_delta=0.983'
    ),
    'substrate_only_ok': True,
    'W_unchanged_by_sleep_all_arms': True,
    'zero_llm_calls_at_inference': True,
    'cv_NONE_at_d5': 0.0,
    'cv_COMPRESSED_at_d5': 0.0,
    'elapsed_s': 67.32985091209412,
    'honest_scope': (
        'Compressed-replay sequence-binding test on synthetic-bipolar disjoint-key sequences '
        'at N_DIM=4096, K=20, N_SEQ=10. The biological compression motivation does NOT '
        'directly transfer to software (no Hebbian STDP window); arm D (ONLINE_NO_GAP) is '
        'the explicit honest-scope control. Substrate-only-decode gate enforced (n_llm=0). '
        'W matrix unchanged by sleep pass (asserted at every arm x seed).'
    ),
    'related_meta_atoms': [
        'META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing',
    ],
    'related_primitives': [
        'hdlab.sequence_memory.SequenceMatrix',
    ],
    'atomized_by': 'skunkworks_c3_deferred_post_3seed_land_bundle_2026-06-22',
    'atomized_ts_marker': '2026-06-22',
    'session_authored': 'exp_dev_c3_brain_drill_5',
    'brain_drill_number': 5,
    'brain_drill_theme': 'hippocampal_SWR_sleep_replay',
    'pre_reg_direction_honored': True,
    'cited_numbers_reproduce_from_metrics_json': True,
}


# =========================================================================
# Atom 2 -- META no-Hebbian-window honest-scope discipline
# =========================================================================

META_ATOM_ID = 'META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing'
META_ATOM_NAME = 'Software substrate has no Hebbian window -- sequence binding is architecture not timing'

META_DESCRIPTION = (
    'CONFIRMED by the c3 3-seed full run (data/exp_c3_compressed_sequence_replay_v1/metrics.json): '
    'ARM D (ONLINE_NO_GAP) reproduces ARM B (COMPRESSED) EXACTLY -- recall_nn=1.000 at every depth '
    '(cv=0.0 across seeds 7,17,23). The software substrate has NO Hebbian spike-timing-dependent '
    'plasticity (STDP) temporal window, so the biological compression-schedule discriminator '
    '(replay during sharp-wave-ripples compresses experience by ~20x relative to wake-time) '
    'collapses in silico. The substrate-side architectural win for sequence binding is the '
    'SEPARATE S MATRIX (offline-pass + ordered-pair update + W-vs-S separation; sequence_memory.'
    'SequenceMatrix primitive), NOT the temporal-compression schedule. '
    'OPERATIONAL RULE: cells motivated by biological replay-or-timing arguments must include '
    'a NULL-DISCRIMINATOR control arm (e.g. ONLINE_NO_GAP for "compression matters" claims) '
    'to verify the biological-motivation discriminator is REAL on the software substrate. If the '
    'null-discriminator control reproduces the headline arm, the substrate win is ARCHITECTURE '
    '(structure of the update / separation of stores) not TIMING (replay schedule). '
    'Cross-cell load-bearing: any future SWR / sleep-replay / temporal-compression-motivated cell '
    'must surface this null-discriminator + the architectural separation it isolates. '
    'Composes with: META_smoke_VET_must_disaggregate_harness_vs_mechanism (Fix #16 sibling), '
    'cell-author-time-estimate-must-be-MEASURED-not-quoted, verify-the-referent family. '
    'Substrate primitive carrying this honest-scope in its docstring: hdlab.sequence_memory.'
    'SequenceMatrix.'
)


def main():
    ts_now = float(time.time())

    print('=' * 72)
    print('Skunkworks deferred c3 atomize: chain-grade EXP_RECORD + no-Hebbian-window META')
    print('=' * 72)

    # ----- A5 PRE -----
    ps = PartitionedStore(REPO / 'data' / 'substrate_index')
    pre_cert = _cert_count(ps)
    pre_ax = _axiom_count(ps)
    pre_cap = _cap_pres_ok()
    pre_n = sum(1 for _ in ps.all_atoms())
    pre_ledger_rows = len(_read_ledger(LEDGER_PATH))
    print(
        f'\n[A5 PRE] CERT={pre_cert} axiom={pre_ax} '
        f'cap_pres={"6/6" if pre_cap else "FAIL"} atoms={pre_n} '
        f'ledger_rows={pre_ledger_rows}'
    )
    # LIVE PRE state (NOT the brief's quoted 587 -- brief was stale; we pin to LIVE)
    # Accept either the unmodified PRE state (585) OR post-first-write state (586) for
    # idempotent re-run after a partial first-pass that landed atoms but failed at the
    # ledger step (script is whole-pipeline idempotent: add_atom replaces same-id,
    # ledger writer skips structurally-identical rows modulo ts).
    LIVE_EXPECTED_CERT_PRE = 585
    LIVE_EXPECTED_CERT_POST_FIRST_PASS = 586  # if c3 atom already landed
    assert pre_cert in (LIVE_EXPECTED_CERT_PRE, LIVE_EXPECTED_CERT_POST_FIRST_PASS), (
        f'A5-PRE CERT mismatch vs live-expected: {pre_cert} not in '
        f'({LIVE_EXPECTED_CERT_PRE}, {LIVE_EXPECTED_CERT_POST_FIRST_PASS}) '
        f'(brief quoted 587 but live is 585; live wins per verify-the-referent)'
    )
    # If we are mid-resume (c3 already landed), pre_cert==586 and expected_atom_delta will be 0
    # for both atoms (they already exist). The downstream expected_cert_post computation handles
    # this correctly because it uses (c3_new ? 1 : 0).
    assert pre_ax == 206, f'A5-PRE axiom drift: {pre_ax} != 206'
    assert pre_cap, 'A5-PRE cap_pres FAIL'

    # Pre-check for collisions (idempotency-guard before any mutation)
    existing_ids = {a.id for a in ps.all_atoms()}
    c3_new = C3_ATOM_ID not in existing_ids
    meta_new = META_ATOM_ID not in existing_ids
    if not c3_new:
        print(f'[IDEMPOTENT] c3 atom {C3_ATOM_ID} already in store; will replace in place')
    if not meta_new:
        print(f'[IDEMPOTENT] META atom {META_ATOM_ID} already in store; will replace in place')

    # ----- Build atom 1: c3 chain-grade -----
    c3_atom = Atom(
        id=C3_ATOM_ID,
        name=C3_ATOM_NAME,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        description=C3_DESCRIPTION,
        kind=AtomKind.EXPERIMENT_RECORD,
        aliases=(
            'c3_compressed_sequence_replay_v1',
            'brain_drill_5_SWR_compressed_replay',
            'EXP_c3_compressed_sequence_replay_v1',
            'compressed_sequence_replay_v1_chain_grade',
        ),
        algebra=None,  # experiment_records canonical algebra=None per existing tool
        metadata=C3_ATOM_METADATA,
    )
    print(f'\n[BUILD] c3 chain-grade atom: {C3_ATOM_ID}')
    print(f'        corpus=MATH tier=TIER_3_ALGORITHM kind=EXPERIMENT_RECORD')
    print(f'        pq=CERT_CHAIN_GRADE verdict=HARD_PASS')
    print(f'        description={len(C3_DESCRIPTION)} chars')

    # ----- Build atom 2: META no-Hebbian-window -----
    meta_atom = Atom(
        id=META_ATOM_ID,
        name=META_ATOM_NAME,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        description=META_DESCRIPTION,
        kind=AtomKind.AUDIT_LESSON,
        aliases=(
            'no_hebbian_window_in_software_substrate',
            'sequence_binding_is_architecture_not_timing',
            'biological_timing_motivation_needs_null_discriminator_control_arm',
            'sleep_replay_substrate_arch_separation_not_schedule',
        ),
        algebra=None,
        metadata={
            'provenance_quality': None,
            'atom_kind': 'discipline_meta',
            'atomized_by': 'skunkworks_c3_deferred_post_3seed_land_bundle_2026-06-22',
            'atomized_ts': ts_now,
            'instance_number': 1,
            'confirmed_or_candidate': 'CONFIRMED',
            'first_witness': C3_ATOM_QID,
            'lesson_class': 'biological_motivation_needs_null_discriminator_control_arm',
            'rule_class': 'substrate_design_discipline',
            'composes_with': [
                'META_smoke_VET_must_disaggregate_harness_vs_mechanism',
                'cell_author_time_estimate_must_be_MEASURED_not_quoted',
                'verify_the_referent_arrives',
                'pre_reg_direction_must_honor_intent',
                'discriminating_regime_required_for_pull_ups',
            ],
            'memory_references': [
                'feedback_autonomous_arc_fixes_14_to_19_2026-06-22',
                'feedback_autonomous_arc_7_fixes_disciplines_2026-06-22',
            ],
            'witness_summaries': [
                {
                    'tag': 'c3_compressed_sequence_replay_v1_3seed_full_2026_06_22',
                    'date': '2026-06-22',
                    'caught_by': 'skunkworks_cross_check_pre_atomization',
                    'cell_commit': 'a27939c5',
                    'metrics_path': 'data/exp_c3_compressed_sequence_replay_v1/metrics.json',
                    'summary': (
                        'ARM D ONLINE_NO_GAP reproduces ARM B COMPRESSED EXACTLY at every '
                        'depth (recall_nn=1.000 cv=0.0 across seeds 7,17,23). The biological '
                        'compression-schedule discriminator collapses in silico because the '
                        'substrate has no STDP temporal window. The substrate-side architectural '
                        'win is the SEPARATE S MATRIX (W-vs-S separation + ordered-pair update), '
                        'NOT the temporal-compression schedule. W_unchanged_by_sleep_all_arms=True '
                        'at every arm x seed independently verifies the W/S separation.'
                    ),
                },
            ],
            'operational_rule': (
                'For any future cell motivated by biological replay/timing arguments (SWR, sleep '
                'replay, STDP, compression schedules, etc.), the SCHEMA-VET pre-reg must include a '
                'NULL-DISCRIMINATOR control arm (e.g. ONLINE_NO_GAP for compression-schedule '
                'claims; SHUFFLED_TIMING for STDP claims). If the null-discriminator control arm '
                'reproduces the headline arm, the substrate win is ARCHITECTURE (structure of '
                'update / separation of stores) not TIMING (schedule of presentation). '
                'Architecture-class wins are valid substrate findings; timing-class wins on '
                'software substrate require explicit STDP-window primitive (which we do not have).'
            ),
            'eleventh_rule_clean': True,
            'symmetric_bidirectional': True,
            'cross_cell_load_bearing': True,
            'substrate_primitive_carrying_honest_scope': 'hdlab.sequence_memory.SequenceMatrix',
        },
    )
    print(f'\n[BUILD] META atom: {META_ATOM_ID}')
    print(f'        corpus=META tier=TIER_METHODOLOGY kind=AUDIT_LESSON algebra=None')
    print(f'        description={len(META_DESCRIPTION)} chars')

    # ----- WRITE Atom 1 (c3 chain-grade) -----
    ps.add_atom(c3_atom)
    print(f'\n[ADD] c3 chain-grade atom appended/replaced')

    # ----- WRITE Atom 2 (META) -----
    ps.add_atom(meta_atom)
    print(f'[ADD] META atom appended/replaced')

    # ----- A5 POST (re-load to catch NULL-seam) -----
    ps2 = PartitionedStore(REPO / 'data' / 'substrate_index')
    post_cert = _cert_count(ps2)
    post_ax = _axiom_count(ps2)
    post_cap = _cap_pres_ok()
    post_n = sum(1 for _ in ps2.all_atoms())
    print(
        f'\n[A5 POST] CERT={post_cert} axiom={post_ax} '
        f'cap_pres={"6/6" if post_cap else "FAIL"} atoms={post_n}'
    )

    # Verify CERT delta = +1 (chain-grade adds; META does not)
    expected_cert_post = pre_cert + (1 if c3_new else 0)
    assert post_cert == expected_cert_post, (
        f'A5-POST CERT mismatch: pre={pre_cert} post={post_cert} '
        f'expected={expected_cert_post} (c3_new={c3_new})'
    )
    assert post_ax == 206, f'A5-POST axiom drift: {post_ax} != 206'
    assert post_cap, 'A5-POST cap_pres FAIL'

    # Atom count delta
    expected_atom_delta = (1 if c3_new else 0) + (1 if meta_new else 0)
    assert post_n == pre_n + expected_atom_delta, (
        f'atom count delta off: pre={pre_n} post={post_n} '
        f'expected_delta={expected_atom_delta}'
    )

    # Both atoms round-trip
    c3_loaded = next((a for a in ps2.all_atoms() if a.id == C3_ATOM_ID), None)
    assert c3_loaded is not None, f'c3 atom {C3_ATOM_ID} not loadable post-write'
    assert (c3_loaded.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE', \
        'c3 atom pq missing CERT_CHAIN_GRADE after round-trip'
    assert (c3_loaded.metadata or {}).get('verdict') == 'HARD_PASS', \
        'c3 atom verdict not HARD_PASS after round-trip'
    print(f'        c3 atom round-trips OK; pq=CERT_CHAIN_GRADE verdict=HARD_PASS')

    meta_loaded = next((a for a in ps2.all_atoms() if a.id == META_ATOM_ID), None)
    assert meta_loaded is not None, f'META atom {META_ATOM_ID} not loadable post-write'
    assert meta_loaded.algebra is None, f'META atom algebra must be None; got {meta_loaded.algebra}'
    assert (meta_loaded.metadata or {}).get('provenance_quality') is None, \
        'META atom must have provenance_quality=None (CERT-neutral)'
    print(f'        META atom round-trips OK; algebra=None; pq=None (CERT-neutral)')

    # ----- Write cert_ledger row #1 (chain-grade c3) -----
    print(f'\n[LEDGER] writing cert_ruling row for c3 chain-grade (delta=+1)')
    c3_row = build_chain_grade_ruling_row(
        atom_id=C3_ATOM_QID,
        cell_commit='a27939c5',
        verdict='HARD_PASS',
        notes_path='notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md',
        metrics_path='data/exp_c3_compressed_sequence_replay_v1/metrics.json',
        cv=0.0,  # cv_COMPRESSED@d5 = 0.0 (headline arm)
        cert_class='pre_reg_pass',
        atomized_by='skunkworks_c3_deferred_post_3seed_land_bundle_2026-06-22',
        note=(
            'c3_brain_drill_5_SWR_compressed_sequence_replay_3seed_remote_cpu_HARD_PASS_'
            'B_d5=1.000_A_d5=0.000_delta=1.000_order_delta=0.983_C_d5=0.017_D_d5=1.000_'
            'cv_B=0.000_cv_A=0.000_substrate_only_W_unchanged_zero_llm_at_inference_'
            'seeds_7_17_23_run_mode_full_elapsed_67s_chain_grade_ratified_per_pre_reg_bands'
        ),
        ts=ts_now,
    )
    # NOTE: at this point the Store add_atom() ALREADY moved CERT from pre_cert -> expected_cert_post
    # (chain-grade atom landed before the ledger row is written). The cert_ledger_writer's strict-A5
    # PRE check reads LIVE Store, so we pass the post-Store-write CERT for BOTH pre and post (the
    # ledger write itself does not change CERT N; it only records the event). The delta=+1 in the
    # row body documents the cert-increment intent; the live CERT was already moved by add_atom.
    rh_c3 = append_cert_ledger_row(
        c3_row,
        expected_cert_n_pre=expected_cert_post,
        expected_cert_n_post=expected_cert_post,
        strict_a5=True,
    )
    print(f'         c3 cert_ruling row_hash = {rh_c3}')

    # ----- Write cert_ledger row #2 (META no-Hebbian-window) -----
    print(f'\n[LEDGER] writing cert_ruling row for META no-Hebbian-window discipline (delta=0)')
    meta_row = {
        'ts': ts_now + 0.001,  # 1ms after c3 row to preserve ordering
        'op': 'cert_ruling',
        'atom_id': f'meta::{META_ATOM_ID}',
        'cert_status': 'measured_mechanism',  # META discipline = MM characterization at substrate-design level
        'cert_class': 'discipline_meta',
        'verified_off_data': True,  # confirmed from c3 metrics.json (ARM D == ARM B exact)
        'atomized_by': 'skunkworks_c3_deferred_post_3seed_land_bundle_2026-06-22',
        'cell_commit': 'a27939c5',
        'verdict': 'HARD_PASS',  # the c3 cell verdict from which this META was confirmed
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': 'notes/c3_honest_scope_software_has_no_hebbian_window_META_proposal_2026-06-22.md',
            'metrics_path': 'data/exp_c3_compressed_sequence_replay_v1/metrics.json',
            'atom_qualified_id': f'meta::{META_ATOM_ID}',
        },
        'supersedes': None,
        'note': (
            'META_software_substrate_no_hebbian_window_sequence_binding_is_architecture_not_timing_'
            'CONFIRMED_by_c3_3seed_full_ARM_D_ONLINE_NO_GAP_reproduces_ARM_B_COMPRESSED_exact_'
            'recall_nn_1.000_cv_0_at_every_depth_substrate_no_STDP_window_'
            'architectural_win_is_SEPARATE_S_MATRIX_not_temporal_compression_schedule_'
            'operational_rule_biological_timing_cells_must_include_null_discriminator_control_arm_'
            'composes_with_smoke_VET_disaggregate_harness_vs_mechanism_Fix16_sibling'
        ),
    }
    rh_meta = append_cert_ledger_row(
        meta_row,
        expected_cert_n_pre=expected_cert_post,  # c3 row already moved CERT to expected_cert_post
        expected_cert_n_post=expected_cert_post,  # META delta=0 keeps it there
        strict_a5=True,
    )
    print(f'         META cert_ruling row_hash = {rh_meta}')

    # ----- Final ledger tail verification -----
    rows_final = _read_ledger(LEDGER_PATH)
    tail = rows_final[-1]
    second_last = rows_final[-2]
    assert second_last['atom_id'] == C3_ATOM_QID, (
        f'second-to-last ledger row mismatch: expected {C3_ATOM_QID} got {second_last["atom_id"]}'
    )
    assert tail['atom_id'] == f'meta::{META_ATOM_ID}', (
        f'tail ledger row mismatch: expected meta::{META_ATOM_ID} got {tail["atom_id"]}'
    )
    print(
        f'\n[LEDGER TAIL]'
        f'\n   second-last: op={second_last["op"]} status={second_last["cert_status"]} '
        f'delta={second_last["cert_increment_delta"]} hash={rh_c3}'
        f'\n   tail:        op={tail["op"]} status={tail["cert_status"]} '
        f'delta={tail["cert_increment_delta"]} hash={rh_meta}'
    )
    print(
        f'[LEDGER ROWS] {len(rows_final)} '
        f'(pre={pre_ledger_rows}, delta=+{len(rows_final) - pre_ledger_rows})'
    )

    print(f'\n[DONE]')
    print(f'  - c3 chain-grade atom: {C3_ATOM_QID} (atoms {pre_n} -> {post_n}, CERT {pre_cert} -> {post_cert})')
    print(f'  - META atom: meta::{META_ATOM_ID} (CERT-neutral)')
    print(f'  - cert_ledger: {rh_c3} (chain-grade, delta=+1)')
    print(f'  - cert_ledger: {rh_meta} (META, delta=0)')
    print(f'  - axiom: {post_ax} (preserved at 206)')
    print(f'  - cap_pres: {"6/6" if post_cap else "FAIL"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
