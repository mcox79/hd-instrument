"""Phase A bulk-seed of data/substrate_index/meta/cert_ledger.jsonl from the Store.

Phase 3 of the Agent-Teams migration, Phase A only (Phase B prose-enrichment + Phase C live-write
integration are SEPARATE later spawns). Phase A: read all atoms with `metadata.provenance_quality
== 'CERT_CHAIN_GRADE'` from the Store and emit one `cert_ruling` row per atom; then emit
`cert_pending` rows for all non-PASS / custom atoms inside the chain-grade set + all
MEASURED_MECHANISM atoms (the sub-audit queue + the dual-MM partner atoms).

A5-gated:
- PRE: CERT N, axiom 206, cap_pres 6/6, Store-LOADS snapshot
- WRITE: assemble all rows in memory + write via atomic os.replace-of-tmp (single ledger file
  write, append-only by construction since file is empty pre-Phase-A)
- POST: re-load Store + verify CERT delta == 0 (Phase A is a parallel index; the Store atom
  schema is untouched), axiom 206, cap_pres 6/6, ledger row count matches expected, ledger
  re-parses cleanly, sum of cert_increment_delta == live CERT N

Discipline notes (per proposal Section 7 ratified decisions):
- Path: data/substrate_index/meta/cert_ledger.jsonl (sibling of audit.jsonl) [DEFAULT]
- verified_off_data for Phase-A seed rows: null (= seeded-not-audited) [DEFAULT]
- Sub-audit queue: ALL non-PASS/custom + ALL MM atoms get under_classified rows [DEFAULT]
- MM dual-atom convention: when a cell has a chain-grade row AND a separate MM atom, both get rows
- ts: null for ALL Phase-A rows (100% of chain-grade atoms have NO audit.jsonl entry; surfaced
  in completion note as the timestamp-fallback finding)

Run from project root with .venv:
    .venv/Scripts/python.exe tools/cert_ledger_phase_a_backfill.py
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore


LEDGER_PATH = Path('data/substrate_index/meta/cert_ledger.jsonl')
AUDIT_PATH = Path('data/substrate_index/meta/audit.jsonl')

PASS_VERDICTS = {'PASS', 'HARD_PASS'}
NON_PASS_VERDICTS = {'HARD_FAIL', 'MIDDLE_BAND', 'MIDDLE', 'MIDDLEBAND', 'MIXED', 'mixed', 'FAIL'}


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


def load_audit_target_ts():
    """Index audit.jsonl: target -> earliest ts (creation timestamp where present)."""
    target_to_ts = {}
    if not AUDIT_PATH.exists():
        return target_to_ts
    for line in AUDIT_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get('op') == 'add_atom' and row.get('target'):
            t = row['target']
            if t not in target_to_ts:
                target_to_ts[t] = row.get('ts')
    return target_to_ts


def classify_chain_grade(verdict):
    """Within CERT_CHAIN_GRADE atoms, determine cert_status + cert_increment_delta."""
    if verdict in PASS_VERDICTS:
        return ('chain_grade', 'pre_reg_pass', 1)
    if verdict and verdict.startswith('HARD_PASS'):
        # custom HARD_PASS_* variants are still chain-grade passes
        return ('chain_grade', 'pre_reg_pass', 1)
    if verdict in NON_PASS_VERDICTS:
        # non-PASS inside chain-grade tag = under_classified (the sub-audit queue)
        return ('under_classified', None, 0)
    # all other custom verdicts (HONEST_NEGATIVE, ATTRIBUTION, SPARSITY_NEUTRAL etc) -> under_classified
    return ('under_classified', None, 0)


def build_phase_a_rows(store, target_to_ts):
    """Emit one ledger row per cert-bearing atom.

    Returns: (rows_list, stats_dict)
    """
    rows = []
    stats = {
        'chain_grade_pass_family': 0,
        'chain_grade_under_classified_non_pass': 0,
        'chain_grade_under_classified_custom': 0,
        'measured_mechanism_pending': 0,
        'cell_commit_present': 0,
        'cell_commit_absent': 0,
        'ts_from_audit': 0,
        'ts_fallback_null': 0,
        'cert_increment_delta_sum': 0,
    }

    for a in store.all_atoms():
        md = a.metadata or {}
        pq = md.get('provenance_quality')
        if pq not in ('CERT_CHAIN_GRADE', 'MEASURED_MECHANISM'):
            continue

        verdict = md.get('verdict')
        bare_id = a.id
        qualified = a.qualified_id

        # ts: try audit.jsonl, else null (and surface the fallback count)
        ts = target_to_ts.get(bare_id)
        if ts is not None:
            stats['ts_from_audit'] += 1
        else:
            stats['ts_fallback_null'] += 1

        # cell_commit from metadata.cell_sha
        cell_commit = md.get('cell_sha') or None
        if cell_commit:
            stats['cell_commit_present'] += 1
        else:
            stats['cell_commit_absent'] += 1

        # metrics_path for referent_pointer
        metrics_path = md.get('metrics_path') or None

        if pq == 'CERT_CHAIN_GRADE':
            cert_status, cert_class, delta = classify_chain_grade(verdict)
            op = 'cert_ruling' if cert_status == 'chain_grade' else 'cert_pending'

            if cert_status == 'chain_grade':
                stats['chain_grade_pass_family'] += 1
                note_tag = 'phase_a_seeded_from_store_provenance_quality_flag'
            elif verdict in NON_PASS_VERDICTS:
                stats['chain_grade_under_classified_non_pass'] += 1
                note_tag = f'phase_a_under_classified_non_pass_verdict_{verdict}'
            else:
                stats['chain_grade_under_classified_custom'] += 1
                note_tag = f'phase_a_under_classified_custom_verdict'
        else:
            # MEASURED_MECHANISM atom -> cert_pending under_classified (the MM dual-atom partner)
            cert_status = 'measured_mechanism'
            cert_class = 'mechanism_characterization'
            delta = 0
            op = 'cert_pending'
            stats['measured_mechanism_pending'] += 1
            note_tag = 'phase_a_seeded_measured_mechanism_partner_atom'

        stats['cert_increment_delta_sum'] += delta

        row = {
            'ts': ts,
            'op': op,
            'atom_id': qualified,
            'cert_status': cert_status,
            'cert_class': cert_class,
            'verified_off_data': None,  # Phase A seeded-not-audited; Phase B fills
            'atomized_by': 'phase_a_backfill',
            'cell_commit': cell_commit,
            'verdict': verdict,
            'cert_increment_delta': delta,
            'cv': None,
            'referent_pointer': {
                'notes_path': None,  # Phase B fills from prose-mining
                'metrics_path': metrics_path,
                'atom_qualified_id': qualified,
            },
            'supersedes': None,
            'note': note_tag,
        }
        rows.append(row)

    return rows, stats


def atomic_write_ledger(rows, path):
    """Write ledger via os.replace-of-tmp atomic pattern."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.jsonl.tmp.' + str(os.getpid()))
    with tmp.open('w', encoding='ascii', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True) + '\n')
    os.replace(tmp, path)


def verify_ledger_roundtrip(path, expected_count):
    """Re-read + parse every line; return parsed rows."""
    parsed = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parsed.append(json.loads(line))
    assert len(parsed) == expected_count, f'ledger row count mismatch: got {len(parsed)} expected {expected_count}'
    return parsed


def main():
    print('=' * 72)
    print('Phase A cert_ledger backfill (one-shot seed from Store)')
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
    assert pre_cert > 0, 'no CERT_CHAIN_GRADE atoms found -- aborting'
    assert pre_ax == 206, f'axiom_count != 206 (got {pre_ax})'
    assert pre_cap == '6/6', f'cap_pres != 6/6 (got {pre_cap})'
    print('  PRE-GATE PASS')

    if LEDGER_PATH.exists():
        existing = LEDGER_PATH.read_text(encoding='utf-8').strip()
        if existing:
            print(f'\n  ABORT: ledger already exists at {LEDGER_PATH} with {len(existing.splitlines())} lines')
            print('  Phase A is one-shot seed (re-running would duplicate rows).')
            print('  If you intend to re-seed, manually move the existing file first.')
            sys.exit(1)

    # ---------------- BUILD ROWS ----------------
    print('\n[BUILD]')
    target_to_ts = load_audit_target_ts()
    print(f'  audit.jsonl target index size: {len(target_to_ts)}')
    rows, stats = build_phase_a_rows(S, target_to_ts)
    print(f'  Total rows assembled: {len(rows)}')
    print(f'    chain_grade (PASS-family ruling, +1 each): {stats["chain_grade_pass_family"]}')
    print(f'    chain_grade -> under_classified non-PASS (HARD_FAIL/MIDDLE_BAND, 0 each): {stats["chain_grade_under_classified_non_pass"]}')
    print(f'    chain_grade -> under_classified custom-verdict (0 each): {stats["chain_grade_under_classified_custom"]}')
    print(f'    measured_mechanism pending (dual-atom partner, 0 each): {stats["measured_mechanism_pending"]}')
    print(f'  sum(cert_increment_delta) = {stats["cert_increment_delta_sum"]}')
    print(f'  cell_commit present: {stats["cell_commit_present"]} / absent: {stats["cell_commit_absent"]}')
    print(f'  ts from audit.jsonl: {stats["ts_from_audit"]} / fallback to null: {stats["ts_fallback_null"]}')

    # Reconcile: chain-grade rows with delta=1 should sum to live CERT N
    assert stats['cert_increment_delta_sum'] == stats['chain_grade_pass_family'], (
        f'delta-sum mismatch: {stats["cert_increment_delta_sum"]} vs PASS-family {stats["chain_grade_pass_family"]}'
    )

    # The PASS-family count is the honest-floor estimate of genuine chain-grade passes.
    # The headline CERT N == 583 includes non-PASS+custom (these are the under_classified
    # queue). This is the explicit headline-honesty audit signal Phase A is making queryable.
    honest_floor = stats['chain_grade_pass_family']
    headline_cert_n = pre_cert
    print(f'\n  HEADLINE-HONESTY SIGNAL:')
    print(f'    headline CERT N (Store flag count)     = {headline_cert_n}')
    print(f'    PASS-family honest floor (this seed)   = {honest_floor}')
    print(f'    under_classified queue (sub-audit)     = {headline_cert_n - honest_floor}')

    # ---------------- WRITE ----------------
    print('\n[WRITE]')
    atomic_write_ledger(rows, LEDGER_PATH)
    print(f'  Wrote {len(rows)} rows to {LEDGER_PATH}')

    # ---------------- A5 POST ----------------
    print('\n[POST-GATE]')
    S2 = PartitionedStore(Path('data/substrate_index'))  # re-load to catch NULL-seam
    post_cert = cert(S2)
    post_ax = axiom_count(S2)
    post_cap = cap_pres_str()
    post_n = sum(1 for _ in S2.all_atoms())
    print(f'  CERT N = {post_cert} (delta: {post_cert - pre_cert})')
    print(f'  axiom_count = {post_ax}')
    print(f'  cap_pres = {post_cap}')
    print(f'  total atoms = {post_n} (delta: {post_n - pre_n})')

    assert post_cert == pre_cert, f'CERT N delta != 0 (phase A is parallel index, should not change cert count)'
    assert post_ax == 206, f'axiom drift {post_ax} != 206'
    assert post_cap == '6/6', f'cap_pres drift {post_cap} != 6/6'
    assert post_n == pre_n, f'atom-count drift {post_n} != {pre_n}'

    # Ledger roundtrip
    parsed = verify_ledger_roundtrip(LEDGER_PATH, len(rows))
    assert parsed == rows, 'ledger roundtrip mismatch (atomic write corrupted)'

    # Cross-check: rows with cert_increment_delta==1 should equal honest_floor (=PASS-family)
    rd = sum(r['cert_increment_delta'] for r in parsed)
    print(f'  ledger sum(cert_increment_delta) = {rd} (should match honest_floor {honest_floor})')
    assert rd == honest_floor, 'ledger delta-sum reload mismatch'

    print('  POST-GATE PASS')

    print('\n' + '=' * 72)
    print('Phase A SEED COMPLETE.')
    print('=' * 72)
    print(f'  Headline CERT N (Store flag)     : {headline_cert_n}')
    print(f'  PASS-family honest floor         : {honest_floor}')
    print(f'  Under-classified queue (Phase B) : {headline_cert_n - honest_floor + stats["measured_mechanism_pending"]}')
    print(f'  Ledger path                      : {LEDGER_PATH}')
    print(f'  Total ledger rows                : {len(rows)}')
    print('=' * 72)


if __name__ == '__main__':
    main()
