"""Phase C live-write integration for data/substrate_index/meta/cert_ledger.jsonl.

Shared helper module called by atomize tools + landed-VET cert-decision flows. Every NEW
cert event (chain-grade atomization / MM characterization / demote / retract / honest-negative
ruling) appends a ledger row in the SAME A5 PRE/POST window as the Store write.

Discipline (per the ratified proposal):
- Single-writer window inherited via os.replace-of-tmp atomic append + path-scoped commit gate
- Idempotency: if the EXACT same row content already exists at ledger tail, skip
- verified_off_data is caller-asserted (auditor role-separation enforced upstream: only
  atomize tools / landed-VET tools edit ledger paths; exp_dev / research / testbed do not)
- The helper does NOT do prose-parsing or supersedes-chain inference -- caller fills
  the `supersedes` field if a relabel/demote/retract is intended
- A5 PRE-snapshot (CERT N, axiom 206, cap_pres 6/6, ledger-readable) BEFORE write
- Atomic append via tmp + os.replace (matches Phase A pattern)
- A5 POST-verify (CERT delta matches `cert_increment_delta` claim; axiom 206; cap_pres 6/6;
  Store re-loads; ledger tail row matches intent)

Usage (in any atomize tool):

    from tools.cert_ledger_writer import append_cert_ledger_row, row_hash

    # ... your atomize tool finishes its Store add_atom() + POST-A5 verify ...

    new_hash = append_cert_ledger_row({
        'op': 'cert_ruling',
        'atom_id': 'math::T3/EXP_my_cell_v1',
        'cert_status': 'chain_grade',
        'cert_class': 'pre_reg_pass',
        'verified_off_data': True,                # the auditor asserts; caller-responsibility
        'atomized_by': 'skunkworks',
        'cell_commit': 'abcd1234',
        'verdict': 'HARD_PASS',
        'cert_increment_delta': 1,                # +1 for chain_grade; 0 for MM/honest_neg; -1 for demote
        'cv': None,
        'referent_pointer': {
            'notes_path': 'notes/skunkworks_to_all_LANDED_VET_...md',
            'metrics_path': 'data/exp_my_cell_v1/metrics.json',
            'atom_qualified_id': 'math::T3/EXP_my_cell_v1',
        },
        'supersedes': None,                       # or prior_row_hash if relabel/demote
        'note': 'phase_c_live_write_skunkworks_atomize_chain_grade',
        # ts auto-filled with time.time() if not provided
    },
        expected_cert_n_pre=583,                   # PRE-snapshot CERT N (verified equal)
        expected_cert_n_post=584,                  # POST-snapshot CERT N (must equal pre + delta)
    )

The helper returns the row's stable hash so the caller can pass it to a chained supersedes
write later (e.g. atomize a chain_grade, then later atomize a demote that supersedes it).

Run self-tests with:
    .venv/Scripts/python.exe tools/cert_ledger_writer.py --self-test
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# Path resolution: works whether called from repo root or as a module import
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

LEDGER_PATH = _REPO_ROOT / 'data' / 'substrate_index' / 'meta' / 'cert_ledger.jsonl'


# ============================================================================
# A5 invariants (mirror Phase A / Phase B pattern; never drift this contract)
# ============================================================================

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


# ============================================================================
# Schema enforcement (mirrors Phase A / Phase B row shape exactly)
# ============================================================================

REQUIRED_FIELDS = (
    'op', 'atom_id', 'cert_status', 'cert_class', 'verified_off_data',
    'atomized_by', 'cell_commit', 'verdict', 'cert_increment_delta', 'cv',
    'referent_pointer', 'supersedes', 'note',
)

VALID_OPS = {
    'cert_ruling', 'cert_relabel', 'cert_demote', 'cert_promote',
    'cert_retract', 'cert_pending', 'cert_dissolve',
}

VALID_CERT_STATUS = {
    'chain_grade', 'measured_mechanism', 'honest_negative', 'proven_bound',
    'under_classified', 'dissolved', 'retracted', 'custom',
}

VALID_CERT_CLASS = {
    'pre_reg_pass', 'post_hoc_pass', 'pre_reg_miss_proven_bound',
    'mechanism_characterization', 'discipline_meta', 'data_attribution',
    'infra_record', None,
}


def _normalize_row(raw):
    """Build a canonical-shape row from a partial dict; fill ts; validate enums."""
    row = {}

    # ts: caller may pre-fill (preserves time-monotonic ordering across A5 windows);
    # else stamp now
    row['ts'] = raw.get('ts')
    if row['ts'] is None:
        row['ts'] = float(time.time())

    # required fields
    for f in REQUIRED_FIELDS:
        if f not in raw:
            raise ValueError(f'cert_ledger_writer: required field missing: {f!r}')
        row[f] = raw[f]

    # enum validation
    if row['op'] not in VALID_OPS:
        raise ValueError(f'cert_ledger_writer: invalid op {row["op"]!r}; valid={sorted(VALID_OPS)}')
    if row['cert_status'] not in VALID_CERT_STATUS:
        raise ValueError(
            f'cert_ledger_writer: invalid cert_status {row["cert_status"]!r}; '
            f'valid={sorted(VALID_CERT_STATUS)}'
        )
    if row['cert_class'] not in VALID_CERT_CLASS:
        raise ValueError(
            f'cert_ledger_writer: invalid cert_class {row["cert_class"]!r}; '
            f'valid={sorted(s for s in VALID_CERT_CLASS if s is not None)} or None'
        )
    if not isinstance(row['cert_increment_delta'], int):
        raise ValueError(
            f'cert_ledger_writer: cert_increment_delta must be int; got '
            f'{type(row["cert_increment_delta"]).__name__}'
        )
    if row['verified_off_data'] not in (True, False, None):
        raise ValueError(
            f'cert_ledger_writer: verified_off_data must be True/False/None; '
            f'got {row["verified_off_data"]!r}'
        )

    # referent_pointer shape
    rp = row['referent_pointer'] or {}
    if not isinstance(rp, dict):
        raise ValueError('cert_ledger_writer: referent_pointer must be a dict (or null)')
    row['referent_pointer'] = {
        'notes_path': rp.get('notes_path'),
        'metrics_path': rp.get('metrics_path'),
        'atom_qualified_id': rp.get('atom_qualified_id') or row['atom_id'],
    }

    # supersedes consistency: only relabel/demote/promote/retract should set it
    if row['supersedes'] is not None and row['op'] not in (
        'cert_relabel', 'cert_demote', 'cert_promote', 'cert_retract'
    ):
        # not strictly forbidden, but flag visibly
        print(
            f'  WARNING: supersedes set on op={row["op"]!r} '
            f'(typical for relabel/demote/promote/retract only)',
            file=sys.stderr,
        )

    return row


def row_hash(row):
    """Stable 16-char hex hash of a row, matches Phase B convention."""
    # Use only schema fields; ts excluded since it's clock-dependent
    # We hash the full canonical row (including ts) to match Phase B's row_hash exactly.
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode('ascii')).hexdigest()[:16]


# ============================================================================
# Atomic write + idempotency
# ============================================================================

def _read_ledger(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _atomic_append(path, new_row):
    """Atomic append-by-rewrite via os.replace-of-tmp (matches Phase A/B pattern)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_ledger(path)
    all_rows = existing + [new_row]
    tmp = path.with_suffix('.jsonl.tmp.' + str(os.getpid()))
    with tmp.open('w', encoding='ascii', newline='\n') as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=True) + '\n')
    os.replace(tmp, path)
    return all_rows


# ============================================================================
# The public helper
# ============================================================================

def append_cert_ledger_row(
    raw_row,
    *,
    expected_cert_n_pre=None,
    expected_cert_n_post=None,
    ledger_path=LEDGER_PATH,
    strict_a5=True,
):
    """Append a row to data/substrate_index/meta/cert_ledger.jsonl with A5 PRE/POST gating.

    Args:
        raw_row: dict with the required schema fields (per cert_ledger_writer.REQUIRED_FIELDS)
        expected_cert_n_pre: int or None; if set, asserted equal to live CERT N at PRE
        expected_cert_n_post: int or None; if set, asserted equal to live CERT N at POST
            (POST-CERT should equal PRE + cert_increment_delta)
        ledger_path: override (default = data/substrate_index/meta/cert_ledger.jsonl)
        strict_a5: if False, skip Store-load gates (for offline testing only)

    Returns:
        str: 16-char hex hash of the appended row (for supersedes chaining)

    Raises:
        ValueError on schema violation
        AssertionError on A5 PRE/POST gate failure
        FileNotFoundError if ledger parent dir cannot be created
    """
    # Normalize + validate
    row = _normalize_row(raw_row)
    rh = row_hash(row)

    # A5 PRE -- load Store + ledger, snapshot invariants
    if strict_a5:
        from backend.substrate_index.partition import PartitionedStore
        ps_pre = PartitionedStore(_REPO_ROOT / 'data' / 'substrate_index')
        pre_cert = _cert_count(ps_pre)
        pre_ax = _axiom_count(ps_pre)
        pre_cap = _cap_pres_ok()
        assert pre_ax == 206, f'A5-PRE axiom drift: {pre_ax} != 206'
        assert pre_cap, 'A5-PRE cap_pres FAIL'
        if expected_cert_n_pre is not None:
            assert pre_cert == expected_cert_n_pre, (
                f'A5-PRE CERT mismatch: live={pre_cert} expected={expected_cert_n_pre}'
            )
    else:
        pre_cert = None

    # Idempotency check: if ANY row in the ledger has identical structural content
    # (all schema fields except `ts`, which is clock-dependent), skip. We compare the row
    # bodies modulo ts because re-running an atomize tool stamps a fresh ts each time but
    # the cert decision itself is the same.
    # Scanning the whole ledger (not just the tail) makes the script-re-run case safe:
    # if a multi-row backfill script is re-run, each row finds its prior twin and skips.
    existing = _read_ledger(ledger_path)

    def _ts_stripped(r):
        return {k: v for k, v in r.items() if k != 'ts'}

    if existing:
        target_body = _ts_stripped(row)
        for prior in existing:
            if _ts_stripped(prior) == target_body:
                existing_hash = row_hash(prior)
                print(
                    f'  IDEMPOTENT-SKIP: identical row (modulo ts) already in ledger '
                    f'(hash={existing_hash})',
                    file=sys.stderr,
                )
                return existing_hash

    # WRITE: atomic append
    all_rows = _atomic_append(ledger_path, row)

    # A5 POST -- re-load Store + ledger; verify CERT delta matches claim
    if strict_a5:
        ps_post = PartitionedStore(_REPO_ROOT / 'data' / 'substrate_index')
        post_cert = _cert_count(ps_post)
        post_ax = _axiom_count(ps_post)
        post_cap = _cap_pres_ok()
        assert post_ax == 206, f'A5-POST axiom drift: {post_ax} != 206'
        assert post_cap, 'A5-POST cap_pres FAIL'

        # The ledger write itself does not change CERT N (the Store add_atom upstream
        # of THIS call is what moved CERT). Pre/post should match the caller's expectations.
        # If the caller asserts expected_cert_n_post, verify post == post + (their delta).
        if expected_cert_n_post is not None:
            assert post_cert == expected_cert_n_post, (
                f'A5-POST CERT mismatch: live={post_cert} expected={expected_cert_n_post} '
                f'(caller claimed cert_increment_delta={row["cert_increment_delta"]}; '
                f'pre={pre_cert})'
            )

        # Ledger tail row must be exactly what we appended
        post_existing = _read_ledger(ledger_path)
        assert len(post_existing) == len(existing) + 1, (
            f'ledger row count drift: pre={len(existing)} post={len(post_existing)} '
            f'(expected pre+1)'
        )
        assert post_existing[-1] == row, 'ledger tail row mismatch (atomic write corrupted)'
        # Cross-check: re-hash the on-disk tail row
        assert row_hash(post_existing[-1]) == rh, 'ledger tail row hash mismatch'

    return rh


# ============================================================================
# Convenience builders for the common cases
# ============================================================================

def build_chain_grade_ruling_row(
    *,
    atom_id,
    cell_commit,
    verdict,
    notes_path,
    metrics_path,
    cv=None,
    cert_class='pre_reg_pass',
    atomized_by='skunkworks',
    note,
    ts=None,
):
    """Build a cert_ruling row for a chain-grade atomization (delta=+1)."""
    return {
        'ts': ts,
        'op': 'cert_ruling',
        'atom_id': atom_id,
        'cert_status': 'chain_grade',
        'cert_class': cert_class,
        'verified_off_data': True,  # atomize-tool callers ARE the auditor; verified
        'atomized_by': atomized_by,
        'cell_commit': cell_commit,
        'verdict': verdict,
        'cert_increment_delta': 1,
        'cv': cv,
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': atom_id,
        },
        'supersedes': None,
        'note': note,
    }


def build_measured_mechanism_row(
    *,
    atom_id,
    cell_commit,
    verdict,
    notes_path,
    metrics_path,
    atomized_by='skunkworks',
    note,
    ts=None,
):
    """Build a cert_ruling row for an MM characterization (delta=0; CERT-neutral)."""
    return {
        'ts': ts,
        'op': 'cert_ruling',
        'atom_id': atom_id,
        'cert_status': 'measured_mechanism',
        'cert_class': 'mechanism_characterization',
        'verified_off_data': True,
        'atomized_by': atomized_by,
        'cell_commit': cell_commit,
        'verdict': verdict,
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': atom_id,
        },
        'supersedes': None,
        'note': note,
    }


def build_honest_negative_row(
    *,
    atom_id,
    cell_commit,
    verdict,
    notes_path,
    metrics_path,
    cert_class='pre_reg_miss_proven_bound',
    atomized_by='skunkworks',
    note,
    verified_off_data=True,
    ts=None,
):
    """Build a cert_ruling row for an honest-negative pre-reg miss (delta=0)."""
    return {
        'ts': ts,
        'op': 'cert_ruling',
        'atom_id': atom_id,
        'cert_status': 'honest_negative',
        'cert_class': cert_class,
        'verified_off_data': verified_off_data,
        'atomized_by': atomized_by,
        'cell_commit': cell_commit,
        'verdict': verdict,
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': atom_id,
        },
        'supersedes': None,
        'note': note,
    }


def build_demote_row(
    *,
    atom_id,
    cell_commit,
    verdict,
    notes_path,
    metrics_path,
    supersedes_hash,
    cert_class='mechanism_characterization',
    new_cert_status='measured_mechanism',
    atomized_by='skunkworks',
    note,
    ts=None,
):
    """Build a cert_demote row (delta=-1) superseding a prior chain_grade row."""
    if not supersedes_hash:
        raise ValueError(
            'build_demote_row: supersedes_hash is required (the prior chain_grade row hash)'
        )
    return {
        'ts': ts,
        'op': 'cert_demote',
        'atom_id': atom_id,
        'cert_status': new_cert_status,
        'cert_class': cert_class,
        'verified_off_data': True,
        'atomized_by': atomized_by,
        'cell_commit': cell_commit,
        'verdict': verdict,
        'cert_increment_delta': -1,
        'cv': None,
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': atom_id,
        },
        'supersedes': supersedes_hash,
        'note': note,
    }


def build_retract_row(
    *,
    atom_id,
    cell_commit,
    verdict,
    notes_path,
    metrics_path,
    supersedes_hash,
    atomized_by='skunkworks',
    note,
    ts=None,
):
    """Build a cert_retract row (delta=-1) superseding a prior chain_grade row."""
    if not supersedes_hash:
        raise ValueError(
            'build_retract_row: supersedes_hash is required (the prior chain_grade row hash)'
        )
    return {
        'ts': ts,
        'op': 'cert_retract',
        'atom_id': atom_id,
        'cert_status': 'retracted',
        'cert_class': None,
        'verified_off_data': True,
        'atomized_by': atomized_by,
        'cell_commit': cell_commit,
        'verdict': verdict,
        'cert_increment_delta': -1,
        'cv': None,
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': atom_id,
        },
        'supersedes': supersedes_hash,
        'note': note,
    }


# ============================================================================
# Self-test (run with --self-test)
# ============================================================================

def _self_test():
    """Sandbox self-test: writes to a tmp ledger, verifies idempotency + schema enforcement.

    Does NOT mutate the real ledger; uses a tmp path under data/substrate_index/meta/.
    """
    import tempfile

    print('=' * 72)
    print('cert_ledger_writer self-test')
    print('=' * 72)

    tmp_ledger = Path(tempfile.mkdtemp(prefix='cert_ledger_writer_selftest_')) / 'tmp.jsonl'
    print(f'\n[1] Tmp ledger path: {tmp_ledger}')

    # Build a row via the convenience builder
    row1 = build_honest_negative_row(
        atom_id='math::T3/EXP_selftest_honest_negative_v1',
        cell_commit='deadbeef',
        verdict='MIDDLE_BAND',
        notes_path='notes/selftest_note.md',
        metrics_path='data/exp_selftest/metrics.json',
        note='cert_ledger_writer_selftest_honest_negative',
    )

    # First write -- should succeed
    print('\n[2] First write (chain-grade honest_negative; delta=0)')
    h1 = append_cert_ledger_row(row1, strict_a5=False, ledger_path=tmp_ledger)
    print(f'   row_hash = {h1}')

    rows = _read_ledger(tmp_ledger)
    assert len(rows) == 1, f'expected 1 row, got {len(rows)}'
    print(f'   ledger now has {len(rows)} rows')

    # Idempotent re-write -- should skip (whole-ledger structural match modulo ts)
    print('\n[3] Idempotent re-write of same row (tail position)')
    h2 = append_cert_ledger_row(row1, strict_a5=False, ledger_path=tmp_ledger)
    rows2 = _read_ledger(tmp_ledger)
    # h2 is the EXISTING tail row's hash (durable identity), so h1 == h2
    assert h1 == h2, f'idempotent re-write should return same hash: got h1={h1} h2={h2}'
    assert len(rows2) == 1, f'idempotency broken: ledger now has {len(rows2)} rows (expected 1)'
    print(f'   idempotency held; ledger still has {len(rows2)} rows; returned hash {h2}')

    # Different row -- should append
    print('\n[4] Different row (MM characterization; delta=0)')
    row2 = build_measured_mechanism_row(
        atom_id='math::T3/EXP_selftest_mm_v1',
        cell_commit='cafefeed',
        verdict='MIDDLE_BAND',
        notes_path='notes/selftest_note_mm.md',
        metrics_path='data/exp_selftest_mm/metrics.json',
        note='cert_ledger_writer_selftest_mm',
    )
    h3 = append_cert_ledger_row(row2, strict_a5=False, ledger_path=tmp_ledger)
    rows3 = _read_ledger(tmp_ledger)
    assert len(rows3) == 2, f'expected 2 rows, got {len(rows3)}'
    print(f'   row_hash = {h3}')
    print(f'   ledger now has {len(rows3)} rows')

    # Whole-ledger idempotency: re-write the FIRST row (now no longer at tail) -- should
    # still skip since it structurally matches an earlier row
    print('\n[4b] Whole-ledger idempotency (re-write row1, now off-tail)')
    h_re = append_cert_ledger_row(row1, strict_a5=False, ledger_path=tmp_ledger)
    rows_re = _read_ledger(tmp_ledger)
    assert h_re == h1, f'whole-ledger idempotency broken: h_re={h_re} h1={h1}'
    assert len(rows_re) == 2, (
        f'whole-ledger idempotency broken: ledger has {len(rows_re)} rows (expected 2)'
    )
    print(f'   whole-ledger idempotency held; ledger still has {len(rows_re)} rows')

    # Schema violation: bad cert_status
    print('\n[5] Schema violation (bad cert_status)')
    bad_row = dict(row1)
    bad_row['cert_status'] = 'not_a_real_status'
    try:
        append_cert_ledger_row(bad_row, strict_a5=False, ledger_path=tmp_ledger)
        raise AssertionError('expected ValueError for bad cert_status')
    except ValueError as e:
        print(f'   correctly raised ValueError: {e}')

    # Schema violation: bad op
    print('\n[6] Schema violation (bad op)')
    bad_row2 = dict(row1)
    bad_row2['op'] = 'not_a_real_op'
    try:
        append_cert_ledger_row(bad_row2, strict_a5=False, ledger_path=tmp_ledger)
        raise AssertionError('expected ValueError for bad op')
    except ValueError as e:
        print(f'   correctly raised ValueError: {e}')

    # Demote with supersedes
    print('\n[7] Demote row with supersedes pointer (delta=-1)')
    demote = build_demote_row(
        atom_id='math::T3/EXP_selftest_demoted_v1',
        cell_commit='12345678',
        verdict='MIDDLE',
        notes_path='notes/selftest_demote.md',
        metrics_path='data/exp_selftest_demote/metrics.json',
        supersedes_hash=h3,
        note='cert_ledger_writer_selftest_demote',
    )
    h4 = append_cert_ledger_row(demote, strict_a5=False, ledger_path=tmp_ledger)
    rows4 = _read_ledger(tmp_ledger)
    assert len(rows4) == 3, f'expected 3 rows, got {len(rows4)}'
    assert rows4[-1]['op'] == 'cert_demote'
    assert rows4[-1]['cert_increment_delta'] == -1
    assert rows4[-1]['supersedes'] == h3
    print(f'   row_hash = {h4}; supersedes = {h3}')

    # Strict-A5 against the REAL Store/ledger (read-only check)
    print('\n[8] Strict-A5 dry path (no write -- just verify Store loads + invariants hold)')
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(_REPO_ROOT / 'data' / 'substrate_index')
    cert_n = _cert_count(ps)
    ax = _axiom_count(ps)
    cap = _cap_pres_ok()
    print(f'   live CERT N = {cert_n}; axiom = {ax}; cap_pres = {"6/6" if cap else "FAIL"}')
    assert ax == 206 and cap, 'environment A5 invariants broken (real Store)'

    # Cleanup
    import shutil
    shutil.rmtree(tmp_ledger.parent)
    print('\nself-test: ALL PASSED')
    return 0


def main():
    if '--self-test' in sys.argv:
        return _self_test()
    print('cert_ledger_writer.py: helper module for live cert-ledger appends.')
    print('Run with --self-test to verify behavior.')
    print('Import append_cert_ledger_row / build_*_row from atomize tools.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
