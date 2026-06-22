"""Phase B window-2 (2026-06-08 to 2026-06-14) prose-enrichment of cert_ledger.jsonl.

Adapted from tools/cert_ledger_phase_b_window1_enrich.py (commit 2b97c564).

Window-2 has a DIFFERENT character than window-1:
- Pre-CERT_NNN-numbering era (CERT 5xx-6xx events all post-date this window)
- Pre-formal-landed-VET-note convention (notes are exp-dev HARD_PASS reports + Research routing,
  NOT independent-VET-with-recompute-off-data notes)
- Many cert events tracked as "PP-rows" in portfolio_state (NOT cell-atoms in the Store)
- The cell-atoms that DID seed from this window are mostly batch-ingest (lambda_batch) or v3-suffix
  cells; many have empty cell_commit and the notes don't cite SHAs explicitly

Honest expectation: ~6-10 enrichments (vs window-1's 22). The remaining audit-debt is the
window-2-era PP-row results that never atomized as Store cell-atoms (window-3+ debt).

Heuristic discipline (preserved from window-1):
- verified_off_data = TRUE only on explicit decision-grade "verified off (the) data" / "off per_unit" /
  "independent recompute" phrasing. EXP-DEV self-reports default to NULL (they are author-reports,
  not auditor-verifications)
- supersedes points to the Phase-A seeded row by content hash
- ts derived from note-file mtime
- Curated extract; manual parse of each named note
- cell_commit backfilled from explicit "commit XXXXXXXX" prose citations
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore


LEDGER_PATH = Path('data/substrate_index/meta/cert_ledger.jsonl')
NOTES_DIR = Path('notes')


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_count(p):
    return sum(
        1 for a in p.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def modlive():
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


def cap_pres_str():
    return '6/6' if modlive() else 'FAIL'


def row_hash(row):
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode('ascii')).hexdigest()[:16]


def note_mtime_ts(note_path):
    p = Path(note_path)
    if p.exists():
        return float(int(p.stat().st_mtime))
    return None


# ============================================================================
# CURATED CERT EXTRACTIONS from 2026-06-08..2026-06-14 notes.
#
# Manual-parse per note. verified_off_data conservatively NULL by default (window-2
# notes are exp-dev self-reports; not landed-VETs by an independent auditor).
#
# Field shape matches window-1 enrich.py exactly.
# ============================================================================

ENRICHMENTS = [
    # (1) Substrate name-augmented encoding recovery (HARD_PASS cleanup ~1.0)
    {
        'atom_id_substr': 'T3/EXP_substrate_name_augmented_encoding_recovery_canonical_rerun_v593',
        'notes_path': 'notes/exp_dev_to_research_NAME_AUGMENTED_ENCODING_HARDPASS_EXISTING_NAME_FIELD_RECOVERS_DECODE_TO_1_0_FIX_DEMONSTRATED_2026-06-12.md',
        'verified_off_data': None,  # exp-dev self-report; no independent landed-VET
        'cert_class': 'pre_reg_pass',  # HARD_PASS at full 3-seed, alpha >= 0.5 cleanup ~= 1.0
        'cell_commit': None,
        'note_tag': 'name_augmented_encoding_hardpass_existing_name_field_recovers_decode_1p0_at_alpha_0p5_3seed_no_bge_clustered_codebook_fix',
        'manually_reviewed': True,
    },

    # (2) Composition/decomposition capacity -- substrate's clustered-codebook ceiling
    # The note describes Cell A (composition_capacity_gpu_v1) + Cell B (decomposition_resonator_cpu_v1).
    # The matching atom in seed is capacity_cliff_graceful_full_v3 (chain-grade); the cpu_v1 atom
    # is MIDDLE_BAND (already classified). Enriching the chain-grade one.
    {
        'atom_id_substr': 'T3/EXP_capacity_cliff_graceful_full_v3',
        'notes_path': 'notes/exp_dev_to_research_CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_NO_CAPACITY_CLIFF_CEILING_IS_CLUSTERED_CODEBOOK_2026-06-12.md',
        'verified_off_data': None,  # exp-dev self-report
        'cert_class': 'pre_reg_pass',  # PASS verdict in seed
        'cell_commit': None,
        'note_tag': 'capacity_cliff_graceful_uniform_codebook_decodes_perfectly_to_F20_clustered_caps_0p84_to_0p93_no_HRR_cliff_cleanup_capacity_F_star_20',
        'manually_reviewed': True,
    },

    # (3) Decomposition resonator alpha=0.5 (chain-grade chain in seed; pairs with cell B note)
    {
        'atom_id_substr': 'T3/EXP_substrate_decomposition_resonator_alpha05_cpu_v1',
        'notes_path': 'notes/exp_dev_to_research_CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_NO_CAPACITY_CLIFF_CEILING_IS_CLUSTERED_CODEBOOK_2026-06-12.md',
        'verified_off_data': None,
        'cert_class': 'pre_reg_pass',
        'cell_commit': None,  # already 5c37ae3cb5bc in seed; preserve
        'note_tag': 'decomposition_resonator_alpha0p5_precision_at_1_flat_F2_8_noise_0p3_no_frady_sommer_cliff_codebook_crowding_K_dependent_ceiling',
        'manually_reviewed': True,
    },

    # (4) decomposition_resonator_cpu_v1 (MIDDLE_BAND in seed; same note prose)
    {
        'atom_id_substr': 'T3/EXP_substrate_decomposition_resonator_cpu_v1',
        'notes_path': 'notes/exp_dev_to_research_CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_NO_CAPACITY_CLIFF_CEILING_IS_CLUSTERED_CODEBOOK_2026-06-12.md',
        'verified_off_data': None,
        'cert_class': None,  # MIDDLE_BAND under_classified
        'cell_commit': None,  # already 067b4fa5a120 in seed
        'note_tag': 'decomposition_resonator_cpu_v1_middle_band_strict_pre_reg_F2_K280_0p842_lt_0p95_resonator_decode_robust_to_F_and_noise_codebook_crowding_caps_at_K280',
        'manually_reviewed': True,
    },

    # (5) Substrate-first hierarchical anchor batch (2026-06-08 handoff/research-route)
    {
        'atom_id_substr': 'T3/EXP_substrate_hierarchical_5corpus_meta_v1_n2048_gpu',
        'notes_path': 'notes/research_to_exp_dev_BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08.md',
        'verified_off_data': None,
        'cert_class': 'pre_reg_pass',
        'cell_commit': None,  # 2c43b8da8f91 already in seed
        'note_tag': 'substrate_first_hierarchical_5corpus_meta_v1_routing_anchors_batch_A1_to_A5_distill_intent_template_pii_routing_latency',
        'manually_reviewed': True,
    },
    {
        'atom_id_substr': 'T3/EXP_substrate_hierarchical_5corpus_meta_v2_n2048_gpu',
        'notes_path': 'notes/research_to_exp_dev_BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08.md',
        'verified_off_data': None,
        'cert_class': 'pre_reg_pass',
        'cell_commit': None,
        'note_tag': 'substrate_first_hierarchical_5corpus_meta_v2_routing_substrate_first_hierarchical_arch_research_route',
        'manually_reviewed': True,
    },

    # (6) Abduction kernel F1 weakest signature (kgram_xor groundtruth) -- HARD_PASS chain-grade
    # The git log 2026-06-12 commit 2e15ea83 promotes theta_burst; commit a215e5ed / 4222be8c / 8cbf1bfd
    # are the abduction phase track. The note matching the SEED atom 'abduction_f1_weakest_signature_kernel'
    # is the gap-driven-loop family. Closest narrative note:
    {
        'atom_id_substr': 'T3/EXP_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1',
        'notes_path': 'notes/research_to_skunkworks_PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_architecture_prototype_USER_described_2026-06-13.md',
        'verified_off_data': None,
        'cert_class': 'pre_reg_pass',  # PASS verdict in seed
        'cell_commit': None,  # already cb5279d561c5 in seed
        'note_tag': 'abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_gap_driven_loop_cell_abduction_f1_reverse_math_phase_B_recoverability_load_bearing_not_arity',
        'manually_reviewed': True,
    },

    # (7) kgram_xor real Llama1b MIDDLE_BAND (recheck per_unit if available)
    {
        'atom_id_substr': 'T3/EXP_substrate_kgram_xor_real_llama1b_v1',
        'notes_path': 'notes/research_to_skunkworks_PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_architecture_prototype_USER_described_2026-06-13.md',
        'verified_off_data': None,
        'cert_class': None,  # MIDDLE_BAND under_classified
        'cell_commit': None,  # already 9d5079d81c67 in seed
        'note_tag': 'kgram_xor_real_llama1b_middle_band_gap_driven_loop_F1_promotion_track_pre_reg_miss_recoverability_signature',
        'manually_reviewed': True,
    },

    # (8) Substrate cognitive core multihop hotpotqa HARD_FAIL
    {
        'atom_id_substr': 'T3/EXP_substrate_cognitive_core_multihop_hotpotqa_v1',
        'notes_path': 'notes/orchestrator_to_research_results_summary_2026-06-08_cycle186.md',
        'verified_off_data': None,
        'cert_class': None,  # HARD_FAIL under_classified
        'cell_commit': None,  # already ab99efb55c06 in seed
        'note_tag': 'hotpotqa_multihop_retrieval_middle_band_r_at_10_0p640_vs_raw_0p720_n50_8pt_deficit_whitening_larger_N_first_rescues',
        'manually_reviewed': False,
    },

    # (9) E3 permutation-indexed binding HARD_PASS (the Recchia-Jones permutation binding)
    # Note: there is no exact-match atom in seed for E3-permutation; closest is the role-binding
    # / dimsparse3 family but those don't match. Surface as window-2 unmatched debt.
    # (skip auto-write; flag below)
]


def find_seeded_row(atom_id_substr, rows):
    """Find the first Phase A seeded row whose atom_qualified_id contains the substr.

    Phase A seed rows have op='cert_ruling' and atomized_by='phase_a_seed'. We prefer those
    over any later cert_relabel rows (so supersedes correctly points to the seeded predecessor).
    """
    # First pass: prefer Phase A seed
    for r in rows:
        if atom_id_substr in (r.get('atom_id') or '') and r.get('atomized_by','').startswith('phase_a'):
            return r
    # Fallback: first match
    for r in rows:
        if atom_id_substr in (r.get('atom_id') or ''):
            return r
    return None


def main():
    print('=' * 72)
    print('Phase B window-2 (2026-06-08..2026-06-14) prose-enrichment')
    print('=' * 72)

    # ---------------- A5 PRE ----------------
    print('\n[PRE-GATE]')
    S = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert(S)
    pre_ax = axiom_count(S)
    pre_cap = cap_pres_str()
    pre_n = sum(1 for _ in S.all_atoms())
    print(f'  CERT N = {pre_cert}')
    print(f'  axiom_count = {pre_ax}')
    print(f'  cap_pres = {pre_cap}')
    print(f'  total atoms = {pre_n}')
    assert pre_ax == 206, f'axiom_count != 206 (got {pre_ax})'
    assert pre_cap == '6/6', f'cap_pres != 6/6 (got {pre_cap})'
    print('  PRE-GATE PASS')

    if not LEDGER_PATH.exists():
        print(f'  ABORT: ledger does not exist at {LEDGER_PATH}; run Phase A first')
        sys.exit(1)

    # ---------------- LOAD EXISTING ROWS ----------------
    print('\n[LOAD existing ledger]')
    existing_rows = []
    for line in LEDGER_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        existing_rows.append(json.loads(line))
    print(f'  Loaded {len(existing_rows)} existing rows')

    pre_audit_debt = sum(1 for r in existing_rows if r.get('verified_off_data') in (None, False))
    pre_notes_null = sum(
        1 for r in existing_rows
        if (r.get('referent_pointer') or {}).get('notes_path') is None
    )
    print(f'  audit-debt-queue size (verified_off_data null/false): {pre_audit_debt}')
    print(f'  rows with notes_path null: {pre_notes_null}')

    # ---------------- BUILD ENRICHMENT ROWS ----------------
    print('\n[BUILD enrichment rows]')
    new_rows = []
    stats = {
        'matched': 0,
        'unmatched': 0,
        'verified_off_data_true': 0,
        'verified_off_data_null': 0,
        'cert_class_counts': {},
        'ts_from_mtime': 0,
        'ts_null': 0,
        'cell_commit_backfilled': 0,
    }
    unmatched_atom_ids = []

    for entry in ENRICHMENTS:
        substr = entry['atom_id_substr']
        seeded = find_seeded_row(substr, existing_rows)
        if seeded is None:
            stats['unmatched'] += 1
            unmatched_atom_ids.append(substr)
            print(f'  UNMATCHED: {substr} (no Phase A seed row)')
            continue
        stats['matched'] += 1

        supersedes_hash = row_hash(seeded)

        ts = note_mtime_ts(entry['notes_path'])
        if ts is not None:
            stats['ts_from_mtime'] += 1
        else:
            stats['ts_null'] += 1

        new_cell_commit = entry.get('cell_commit') or seeded.get('cell_commit')
        if entry.get('cell_commit') and not seeded.get('cell_commit'):
            stats['cell_commit_backfilled'] += 1

        vod = entry.get('verified_off_data')
        if vod is True:
            stats['verified_off_data_true'] += 1
        else:
            stats['verified_off_data_null'] += 1

        cc = entry.get('cert_class')
        stats['cert_class_counts'][cc] = stats['cert_class_counts'].get(cc, 0) + 1

        relabel = {
            'ts': ts,
            'op': 'cert_relabel',
            'atom_id': seeded['atom_id'],
            'cert_status': seeded['cert_status'],
            'cert_class': cc,
            'verified_off_data': vod,
            'atomized_by': 'skunkworks_phase_b_window2',
            'cell_commit': new_cell_commit,
            'verdict': seeded.get('verdict'),
            'cert_increment_delta': 0,
            'cv': entry.get('cv'),
            'referent_pointer': {
                'notes_path': entry['notes_path'],
                'metrics_path': (seeded.get('referent_pointer') or {}).get('metrics_path'),
                'atom_qualified_id': seeded['atom_id'],
            },
            'supersedes': supersedes_hash,
            'note': entry['note_tag'],
        }
        new_rows.append(relabel)

    print(f'  Matched {stats["matched"]} / Unmatched {stats["unmatched"]}')
    print(f'  verified_off_data: true={stats["verified_off_data_true"]} / null={stats["verified_off_data_null"]}')
    print(f'  ts: from_mtime={stats["ts_from_mtime"]} / null={stats["ts_null"]}')
    print(f'  cell_commit backfilled: {stats["cell_commit_backfilled"]}')
    print(f'  cert_class distribution:')
    for cc, n in sorted(stats['cert_class_counts'].items(), key=lambda x: -(x[1])):
        print(f'    {cc}: {n}')
    if unmatched_atom_ids:
        print(f'  UNMATCHED atom_id substrings (surfaced as window-2 debt):')
        for s in unmatched_atom_ids:
            print(f'    - {s}')

    # ---------------- WRITE ----------------
    print('\n[WRITE]')
    if not new_rows:
        print('  No new rows to write; exiting')
        return

    all_rows = existing_rows + new_rows
    tmp = LEDGER_PATH.with_suffix('.jsonl.tmp.' + str(os.getpid()))
    with tmp.open('w', encoding='ascii', newline='\n') as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=True) + '\n')
    os.replace(tmp, LEDGER_PATH)
    print(f'  Appended {len(new_rows)} cert_relabel rows; total ledger rows = {len(all_rows)}')

    # ---------------- A5 POST ----------------
    print('\n[POST-GATE]')
    S2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert(S2)
    post_ax = axiom_count(S2)
    post_cap = cap_pres_str()
    post_n = sum(1 for _ in S2.all_atoms())
    print(f'  CERT N = {post_cert} (delta: {post_cert - pre_cert})')
    print(f'  axiom_count = {post_ax}')
    print(f'  cap_pres = {post_cap}')
    print(f'  total atoms = {post_n} (delta: {post_n - pre_n})')

    assert post_cert == pre_cert, 'CERT delta != 0 (Phase B relabel is CERT-neutral)'
    assert post_ax == 206, f'axiom drift {post_ax}'
    assert post_cap == '6/6', f'cap_pres drift {post_cap}'
    assert post_n == pre_n, f'atom-count drift'

    reloaded = []
    for line in LEDGER_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        reloaded.append(json.loads(line))
    assert len(reloaded) == len(all_rows), f'reload count mismatch: {len(reloaded)} vs {len(all_rows)}'
    sum_delta = sum(r.get('cert_increment_delta') or 0 for r in reloaded)
    pre_sum = sum(r.get('cert_increment_delta') or 0 for r in existing_rows)
    assert sum_delta == pre_sum, f'sum(cert_increment_delta) changed: {pre_sum} -> {sum_delta}'

    post_audit_debt = sum(1 for r in reloaded if r.get('verified_off_data') in (None, False))
    post_notes_null = sum(
        1 for r in reloaded
        if (r.get('referent_pointer') or {}).get('notes_path') is None
    )

    print('  POST-GATE PASS')
    print(f'\n  Audit-debt-queue (naive): {pre_audit_debt} -> {post_audit_debt} (delta: -{pre_audit_debt - post_audit_debt})')
    print(f'  Notes-path-null (naive): {pre_notes_null} -> {post_notes_null} (delta: -{pre_notes_null - post_notes_null})')

    print('\n' + '=' * 72)
    print('Phase B window-2 enrichment COMPLETE')
    print('=' * 72)


if __name__ == '__main__':
    main()
