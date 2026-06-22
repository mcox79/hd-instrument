"""Phase C immediate-debt backfill: 5 post-seed honest-negatives / MM characterizations.

Per the Phase B window-1 completion note Section 5c, these 5 cells are NOT in the Phase A
seed (they atomized as honest-negative / MIDDLE_BAND / MEASURED_MECHANISM, not as
CERT_CHAIN_GRADE, OR landed after the Phase A snapshot, OR never atomized as a cert-event):

  1. n2_capacity_scaling_v1 (efd3d3e6, MIDDLE_BAND, pre_reg_miss_proven_bound; verified-off-data
     per the 2026-06-22 landed-VET note; 5 anchor numbers re-derived from per_seed)
  2. n1_concept_lm (MIDDLE_BAND, beats unigram NOT bigram, sub-only PASS)
  3. dense_KV_whitening_revival_v1_gpu (MM honest-negative; ruled 03452c77)
  4. anisotropy_rescue_4arm_sweep_v1_gpu (MIDDLE_BAND at CLASS-level; tag-retrieval works,
     specific WTA interchangeable)
  5. sparse-#2-reframe a3f473dd (MEASURED_MECHANISM; 8x@f0.10 / 20x@f0.02 Willshaw super-capacity;
     atomize note already states verified-off-data)

For each, write a FRESH `cert_ruling` row (NOT relabel; no Phase-A row to supersede):
- cert_status = honest_negative (pre-reg-miss) OR measured_mechanism (MM)
- cert_class per the proposal taxonomy
- verified_off_data = TRUE for those with explicit VET-note off-data assertion; else NULL
- cert_increment_delta = 0 (all CERT-neutral)
- referent_pointer.notes_path = the committed landed-VET note

A5-gated via tools.cert_ledger_writer.append_cert_ledger_row. Run from project root with .venv:
    .venv/Scripts/python.exe tools/cert_ledger_phase_c_5_backfill.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


# ============================================================================
# The 5 backfills, each manually-curated per the named landed-VET note.
# verified_off_data: TRUE only when the note explicitly says off-data / re-derived /
# independent recompute / re-derived from per_unit (conservative-default per Section 6).
# ============================================================================

BACKFILLS = [
    # (1) n2_capacity_scaling_v1 -- honest pre-reg-miss MIDDLE_BAND with ALL 5 cited numbers
    #     re-derived from data/exp_n2_capacity_scaling_v1/metrics.json per_seed (3 seeds).
    #     Anchor 5.29 (n4096_k1=5.2875); alpha monotone 2.013->1.007->0.503; sub_bpc monotone
    #     5.288->5.131->4.959 (K=1); ceiling sanity 2.049<=15.612; bigram-beat FAILS (4.959 vs
    #     3.844 gap=1.115); unigram-beat PASSES (4.959 vs 6.326 margin=1.367). Note explicitly:
    #     "All numbers re-derived from data/exp_n2_capacity_scaling_v1/metrics.json per_seed
    #     (3 seeds: 7, 17, 23). Re-derived locally via .venv python statistics.mean / stdev."
    {
        'kind': 'honest_negative',
        'atom_id': 'math::T3/EXP_n2_capacity_scaling_v1',
        'cell_commit': 'efd3d3e6',
        'verdict': 'MIDDLE_BAND',
        'cert_class': 'pre_reg_miss_proven_bound',
        'notes_path': 'notes/skunkworks_to_research_cc_all_LANDED_VET_n2_capacity_scaling_MIDDLE_BAND_3way_knot_META_2026-06-22.md',
        'metrics_path': 'data/exp_n2_capacity_scaling_v1/metrics.json',
        'verified_off_data': True,
        'note': 'phase_c_backfill_n2_pre_reg_bar_miss_4p96_vs_bigram_3p84_5_anchors_redrived_from_per_seed',
    },

    # (2) n1_concept_lm v3.1 -- substrate-native LM, proven-bound MIDDLE_BAND
    #     Beats unigram NOT bigram (sub-only PASS); honest pre-reg-miss.
    #     Note: SCHEMA_VET; cell pq=MIDDLE_BAND; verified-off-data ambiguous in this note (it's
    #     a SCHEMA VET, not the landed-VET); conservatively NULL.
    {
        'kind': 'honest_negative',
        'atom_id': 'math::T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_1',
        'cell_commit': None,
        'verdict': 'MIDDLE_BAND',
        'cert_class': 'pre_reg_miss_proven_bound',
        'notes_path': 'notes/skunkworks_to_orch_expdev_research_SCHEMA_VET_N1_concept_lm_token_decode_bands_2026-06-21.md',
        'metrics_path': 'data/exp_n1_concept_lm_substrate_native_token_decode_v3_1/metrics.json',
        'verified_off_data': None,
        'note': 'phase_c_backfill_n1_concept_lm_v3p1_proven_bound_substrate_beats_unigram_NOT_bigram_sub_only_pass',
    },

    # (3) dense_KV_whitening_revival_v1_gpu -- MM honest-negative; ruled 03452c77
    #     Per the orchestrator MIDDLE_BAND landed-VET note; revives anisotropy 4-arm.
    {
        'kind': 'measured_mechanism',
        'atom_id': 'math::T3/EXP_dense_KV_whitening_revival_v1_gpu',
        'cell_commit': '03452c77',
        'verdict': 'MIDDLE_BAND',
        'notes_path': 'notes/research_to_skunkworks_orch_cc_all_WHITENING_LANDED_MIDDLE_BAND_director_4layer_cross_check_2026-06-21.md',
        'metrics_path': 'data/exp_dense_KV_whitening_revival_v1_gpu/metrics.json',
        'note': 'phase_c_backfill_dense_kv_whitening_mm_honest_negative_4layer_cross_check_revives_anisotropy_4arm',
    },

    # (4) anisotropy_rescue_4arm_sweep_v1_gpu -- MIDDLE_BAND at CLASS-level; tag-retrieval
    #     works, specific WTA mechanism interchangeable.
    {
        'kind': 'honest_negative',
        'atom_id': 'math::T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu',
        'cell_commit': None,
        'verdict': 'MIDDLE_BAND',
        'cert_class': 'pre_reg_miss_proven_bound',
        'notes_path': 'notes/orchestrator_to_skunkworks_anisotropy_4arm_MIDDLE_BAND_tag_retrieval_class_works_2026-06-21.md',
        'metrics_path': 'data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json',
        'verified_off_data': None,
        'note': 'phase_c_backfill_anisotropy_4arm_middle_band_at_class_level_tag_retrieval_works_specific_wta_interchangeable',
    },

    # (5) sparse-#2-reframe a3f473dd -- MEASURED_MECHANISM characterization.
    #     8x@f0.10 / 20x@f0.02 Willshaw super-capacity; raw P.T@P, N-independent 2048-16384.
    #     Atomize note (skunkworks_to_expdev_orch_research_SPARSE2_ATOMIZED) explicitly:
    #     "offdata_verified MEASURED_MECHANISM; CERT592 unchanged".
    {
        'kind': 'measured_mechanism',
        'atom_id': 'math::T3/EXP_substrate_sparse_recall_capacity_a3f473dd',
        'cell_commit': 'a3f473dd',
        'verdict': 'MEASURED_MECHANISM',
        'notes_path': 'notes/skunkworks_to_expdev_orch_research_SPARSE2_ATOMIZED_offdata_verified_MEASURED_MECHANISM_a3f473dd_CERT592_unchanged_2026-06-20.md',
        'metrics_path': 'data/exp_substrate_sparse_recall_capacity_a3f473dd/metrics.json',
        'note': 'phase_c_backfill_sparse2_reframe_8x_f0p10_20x_f0p02_willshaw_super_capacity_raw_PT_at_P_n_indep_2048_16384',
    },
]


def main():
    print('=' * 72)
    print('Phase C immediate-debt 5-backfill (honest-negatives + MM characterizations)')
    print('=' * 72)

    # Capture pre-state
    sys.path.insert(0, '.')
    from backend.substrate_index.partition import PartitionedStore
    from tools.cert_ledger_writer import _cert_count, _axiom_count, _cap_pres_ok, _read_ledger, LEDGER_PATH

    ps_pre = PartitionedStore(Path('data/substrate_index'))
    pre_cert = _cert_count(ps_pre)
    pre_ax = _axiom_count(ps_pre)
    pre_cap = _cap_pres_ok()
    pre_n = sum(1 for _ in ps_pre.all_atoms())
    pre_ledger = _read_ledger(LEDGER_PATH)

    print(f'\n[PRE]')
    print(f'  CERT N            = {pre_cert}')
    print(f'  axiom_count       = {pre_ax}')
    print(f'  cap_pres          = {"6/6" if pre_cap else "FAIL"}')
    print(f'  atom_count        = {pre_n}')
    print(f'  ledger rows       = {len(pre_ledger)}')
    assert pre_ax == 206, f'A5-PRE axiom drift {pre_ax}'
    assert pre_cap, 'A5-PRE cap_pres FAIL'

    print(f'\n[BACKFILL]')
    written_hashes = []
    skipped = 0
    for i, entry in enumerate(BACKFILLS, 1):
        kind = entry['kind']
        atom_id = entry['atom_id']
        print(f'\n  ({i}/5) {atom_id}  [{kind}]')

        if kind == 'honest_negative':
            row = build_honest_negative_row(
                atom_id=atom_id,
                cell_commit=entry['cell_commit'],
                verdict=entry['verdict'],
                notes_path=entry['notes_path'],
                metrics_path=entry['metrics_path'],
                cert_class=entry['cert_class'],
                atomized_by='skunkworks_phase_c_5_backfill',
                note=entry['note'],
                verified_off_data=entry.get('verified_off_data', True),
            )
        elif kind == 'measured_mechanism':
            row = build_measured_mechanism_row(
                atom_id=atom_id,
                cell_commit=entry['cell_commit'],
                verdict=entry['verdict'],
                notes_path=entry['notes_path'],
                metrics_path=entry['metrics_path'],
                atomized_by='skunkworks_phase_c_5_backfill',
                note=entry['note'],
            )
        else:
            raise ValueError(f'unknown kind: {kind!r}')

        # Append: all 5 are CERT-neutral so expected_pre == expected_post == pre_cert
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=pre_cert,
            expected_cert_n_post=pre_cert,  # delta=0
        )
        written_hashes.append((atom_id, h))
        print(f'        ledger row appended; hash = {h}')

    # POST verification
    print(f'\n[POST]')
    ps_post = PartitionedStore(Path('data/substrate_index'))
    post_cert = _cert_count(ps_post)
    post_ax = _axiom_count(ps_post)
    post_cap = _cap_pres_ok()
    post_n = sum(1 for _ in ps_post.all_atoms())
    post_ledger = _read_ledger(LEDGER_PATH)

    print(f'  CERT N            = {post_cert}  (delta from pre: {post_cert - pre_cert})')
    print(f'  axiom_count       = {post_ax}')
    print(f'  cap_pres          = {"6/6" if post_cap else "FAIL"}')
    print(f'  atom_count        = {post_n}  (delta from pre: {post_n - pre_n})')
    print(f'  ledger rows       = {len(post_ledger)}  (delta from pre: {len(post_ledger) - len(pre_ledger)})')

    assert post_cert == pre_cert, f'CERT delta != 0 (5-backfill is CERT-neutral)'
    assert post_ax == 206, f'A5-POST axiom drift'
    assert post_cap, 'A5-POST cap_pres FAIL'
    assert post_n == pre_n, f'atom-count drift (should be 0; ledger does not write Store atoms)'
    # Idempotency-safe: re-running this script returns existing-row hashes, so the row
    # delta may be 0 (idempotent re-run) OR len(BACKFILLS) (first run). Verify all 5
    # atom_ids are findable in the post ledger -- that's the real correctness check.
    delta = len(post_ledger) - len(pre_ledger)
    assert delta in (0, len(BACKFILLS)), (
        f'ledger row delta unexpected: {delta} (expected 0 idempotent OR {len(BACKFILLS)} fresh)'
    )
    post_atom_ids = {r.get('atom_id') for r in post_ledger}
    for entry in BACKFILLS:
        assert entry['atom_id'] in post_atom_ids, (
            f'backfill target missing from post-ledger: {entry["atom_id"]}'
        )
    if delta == 0:
        print(f'\n  (Re-run idempotent: all 5 rows already present; no new appends)')
    else:
        print(f'\n  (First-run: {delta} new rows appended)')

    print(f'\n[SUMMARY]')
    for aid, h in written_hashes:
        print(f'  {aid:60} hash={h}')
    print(f'\n  5 fresh cert_ruling rows appended; CERT N unchanged at {post_cert}')
    print('=' * 72)
    print('Phase C 5-backfill COMPLETE.')
    print('=' * 72)


if __name__ == '__main__':
    raise SystemExit(main())
