"""Ledger-only recovery for g1b chain-grade atomization (2026-06-22).

CONTEXT: the main atomize script
(tools/skunkworks_atomize_g1b_capacity_sweep_chain_grade_2026-06-22.py) was
invoked in the background; bg invocation completed the Store writes (both
atoms landed in data/substrate_index) but did not reach the ledger writes
before the bash backend cancelled the long-running task. Foreground retry
hit A5-PRE assertion (live CERT=587 != expected 586) and aborted before
ledger writes.

LIVE STATE (re-verified pre this script):
  atoms=177283 (+2 from 177281 pre-bg)
  CERT N=587 (+1 from 586 pre-bg; chain-grade atom written)
  axiom=206 (preserved)
  cap_pres=True (6/6 preserved)
  ledger rows=651 (still pre-write; needs +2)

This script writes the two missing ledger rows. expected_cert_n_pre and
expected_cert_n_post are both 587 because:
  - The Store has already been mutated (chain-grade atom is in pq CERT_CHAIN_GRADE
    bucket; CERT N already reflects the +1)
  - Ledger row writes do NOT change CERT N; pre/post are both the post-Store-write
    live value (587)
  - The conceptual delta=+1 stays in the row body as the cert-decision marker

USAGE:
    .venv/Scripts/python.exe tools/skunkworks_g1b_ledger_recovery_2026-06-22.py
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backend.substrate_index.partition import PartitionedStore
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    _cert_count, _axiom_count, _cap_pres_ok,
)

CELL_COMMIT = '544ab09e'
METRICS_PATH = 'data/exp_g1b_capacity_sweep_v1/metrics.json'
NOTES_PATH = 'notes/g1_substrate_native_generation_pipeline_complete_2026-06-22.md'

ATOM1_QID = 'math::T3/EXP_g1b_capacity_sweep_v1'
ATOM2_QID = (
    'meta::META_substrate_autoregressive_generation_chain_grade_requires_'
    'headroom_to_fail_discriminator'
)

# Post-bg-race live values
EXPECTED_CERT_N = 587


def main():
    print('=' * 78)
    print('Skunkworks LEDGER-ONLY recovery for g1b chain-grade atomization')
    print('Both atoms already in Store; this writes the 2 missing ledger rows')
    print('=' * 78)

    # A5 PRE check
    ps = PartitionedStore(REPO / 'data' / 'substrate_index')
    n_pre = len(ps.all_atoms())
    cert_pre = _cert_count(ps)
    ax_pre = _axiom_count(ps)
    cap_pre = _cap_pres_ok()
    print(f'\nA5-PRE: atoms={n_pre} CERT={cert_pre} axiom={ax_pre} '
          f'cap_pres={"6/6" if cap_pre else "FAIL"}')
    assert ax_pre == 206
    assert cap_pre
    assert cert_pre == EXPECTED_CERT_N, (
        f'PRE CERT drift: live={cert_pre} expected={EXPECTED_CERT_N}'
    )

    # Verify both atoms ARE in Store (recovery precondition)
    atoms = ps.all_atoms()
    a1 = [a for a in atoms if 'g1b_capacity_sweep' in a.id.lower()]
    a2 = [
        a for a in atoms
        if a.id == (
            'META_substrate_autoregressive_generation_chain_grade_'
            'requires_headroom_to_fail_discriminator'
        )
    ]
    assert len(a1) == 1, f'expected 1 g1b atom, found {len(a1)}'
    assert len(a2) == 1, f'expected 1 META atom, found {len(a2)}'
    print(f'  g1b atom present: id={a1[0].id} pq={a1[0].metadata.get("provenance_quality")}')
    print(f'  META atom present: id={a2[0].id} pq={a2[0].metadata.get("provenance_quality")}')

    # Re-derive load-bearing numbers from metrics (verify-the-referent)
    m = json.loads((REPO / METRICS_PATH).read_text(encoding='utf-8'))
    d = m['detail']
    head_pt = next(p for p in d['scan_summary'] if p['n_pairs'] == 6403)
    head_cv = float(head_pt['cv_arm4'])
    head_coh = float(head_pt['coh_arm4'])
    assert m['verdict'] == 'HARD_PASS'
    assert d['n_points_at_hard_pass_bar'] == 6
    assert d['headroom_to_fail_point_n_pairs'] == 6403
    assert 0.60 <= head_coh < 0.99, f'headroom_coh out of band: {head_coh}'
    print(f'\nMetrics re-verify: headroom_pt n_pairs=6403 coh_arm4={head_coh:.4f} '
          f'cv={head_cv:.4f}; n_points_at_bar=6/6')

    # ------------------------------------------------------------------
    # Ledger row 1: chain-grade
    # ------------------------------------------------------------------
    row1 = build_chain_grade_ruling_row(
        atom_id=ATOM1_QID,
        cell_commit=CELL_COMMIT,
        verdict='HARD_PASS',
        notes_path=NOTES_PATH,
        metrics_path=METRICS_PATH,
        cv=head_cv,
        cert_class='pre_reg_pass',
        atomized_by='skunkworks_g1b_landed_VET_CERT_CHAIN_GRADE_ruling_2026-06-22',
        note=(
            'g1b_capacity_sweep_v1_3seed_full_HARD_PASS_6_of_6_scan_points_at_bar_'
            'headroom_to_fail_at_n_pairs_6403_density_1p56x_N_DIM_coh_arm4_0p9403_'
            'cv_0p0351_arm_spread_at_headroom_NONE_0p000_S_ONLY_0p375_S_LANGEVIN_0p125_'
            'S_LANGEVIN_CLEANUP_0p940_no_cliff_no_spread_violation_graceful_degradation_'
            'substrate_only_True_W_unchanged_True_zero_llm_True_seeds_7_17_23_run_mode_full_'
            'elapsed_1370s_route_B_g1b_standalone_chain_grade_g1_remains_MEASURED_MECHANISM_'
            'chain_grade_evidence_above_by_construction_saturation_regime_via_corrected_'
            'discriminator_coh_lt_0p99_not_novelty_ratio_metric_artifact_'
            'ledger_recovery_after_bg_race_store_writes_already_landed_pre_post_CERT_N_587_587_'
            'delta_plus_1_is_conceptual_cert_decision_marker'
        ),
    )
    print('\n--- Ledger row 1 (chain-grade) ---')
    h1 = append_cert_ledger_row(
        row1,
        expected_cert_n_pre=EXPECTED_CERT_N,
        expected_cert_n_post=EXPECTED_CERT_N,
        strict_a5=True,
    )
    print(f'  row1 hash: {h1}  (atom={ATOM1_QID})')

    # ------------------------------------------------------------------
    # Ledger row 2: META (discipline)
    # ------------------------------------------------------------------
    row2 = {
        'ts': None,
        'op': 'cert_ruling',
        'atom_id': ATOM2_QID,
        'cert_status': 'measured_mechanism',
        'cert_class': 'discipline_meta',
        'verified_off_data': True,
        'atomized_by': 'skunkworks_g1b_landed_VET_2026-06-22',
        'cell_commit': CELL_COMMIT,
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': NOTES_PATH,
            'metrics_path': METRICS_PATH,
            'atom_qualified_id': ATOM2_QID,
        },
        'supersedes': None,
        'note': (
            'META_substrate_autoregressive_generation_chain_grade_requires_headroom_to_fail_'
            'discriminator_CONFIRMED_by_g1_to_g1b_arc_g1_at_n190_ruled_MEASURED_MECHANISM_'
            'because_coh_arm4_1p000_cv_0p000_novelty_ratio_metric_saturated_at_analytic_'
            'cap_by_construction_g1b_at_n6403_density_1p56x_N_DIM_with_coh_arm4_0p9403_'
            'cv_0p0351_AND_4arm_spread_preserved_NONE_0p000_S_ONLY_0p375_S_LANGEVIN_0p125_'
            'CLEANUP_0p940_ruled_chain_grade_operational_rule_S_plus_sampling_plus_cleanup_'
            'substrate_native_generation_cells_must_include_density_scan_reaching_a_headroom_'
            'to_fail_point_coh_arm4_lt_0p99_AND_gte_0p60_with_4arm_spread_preserved_before_'
            'chain_grade_certification_novelty_ratio_is_metric_artifact_when_cleanup_snaps_'
            'to_codebook_composes_with_codebook_NN_cleanup_load_bearing_META_no_Hebbian_'
            'window_META_by_construction_saturation_tiering_META'
        ),
    }
    print('\n--- Ledger row 2 (META discipline) ---')
    h2 = append_cert_ledger_row(
        row2,
        expected_cert_n_pre=EXPECTED_CERT_N,
        expected_cert_n_post=EXPECTED_CERT_N,
        strict_a5=True,
    )
    print(f'  row2 hash: {h2}  (atom={ATOM2_QID})')

    # ------------------------------------------------------------------
    # A5 FINAL
    # ------------------------------------------------------------------
    ps_final = PartitionedStore(REPO / 'data' / 'substrate_index')
    final_atoms = ps_final.all_atoms()
    n_final = len(final_atoms)
    cert_final = _cert_count(ps_final)
    ax_final = _axiom_count(ps_final)
    cap_final = _cap_pres_ok()
    ledger_path = REPO / 'data' / 'substrate_index' / 'meta' / 'cert_ledger.jsonl'
    n_ledger = sum(1 for l in ledger_path.read_text(encoding='utf-8').splitlines() if l.strip())

    print('\n' + '=' * 78)
    print('A5-FINAL:')
    print(f'  atoms: {n_final} (unchanged by ledger-only write)')
    print(f'  CERT N: {cert_final} (unchanged by ledger-only write; chain-grade '
          f'+1 effected by prior Store write)')
    print(f'  axiom_term: {ax_final} (preserved {ax_final == 206})')
    print(f'  cap_pres: {"6/6" if cap_final else "FAIL"}')
    print(f'  ledger rows: 651 -> {n_ledger} (delta=+{n_ledger - 651})')
    print(f'  row1 hash: {h1}')
    print(f'  row2 hash: {h2}')
    print('=' * 78)

    return {
        'atom1_qid': ATOM1_QID,
        'atom2_qid': ATOM2_QID,
        'row1_hash': h1,
        'row2_hash': h2,
        'atoms_final': n_final,
        'cert_final': cert_final,
        'ledger_rows_final': n_ledger,
    }


if __name__ == '__main__':
    result = main()
    print('\nResult:', json.dumps(result, indent=2))
