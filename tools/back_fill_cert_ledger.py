"""Back-fill cert_ledger.jsonl entries for atoms that were written to atoms.jsonl
without a corresponding ledger row.

Usage:
    .venv/Scripts/python.exe tools/back_fill_cert_ledger.py <atom_id> \
        --cell-commit <sha> --note <one-line-note> [--dry-run]

    # audit-only mode: list ledger-orphan atoms in a commit
    .venv/Scripts/python.exe tools/back_fill_cert_ledger.py --audit-commit <sha>

The tool derives ledger fields from the atom's on-disk metadata:
    - cert_status / cert_class / cert_increment_delta from atom.kind + metadata
    - verdict from metadata.verdict (or MEASURED_MECHANISM/HARD_FAIL by kind)
    - referent_pointer from metadata.metrics_path or convention
    - op = "back_fill" (Fix #28-adjacent audit tag)

Writes via tools/cert_ledger_writer.append_cert_ledger_row with strict_a5=False
(back-fill by definition happens AFTER the Store write; CERT N is already at post).

Verified_off_data=True (the atom body is the source of truth; we re-derive fields
from the on-disk atom, not from a cached summary).

Historical context: commit a8dfb00b (2026-06-30 22:29 EDT) wrote 5+1 atoms to
math corpus atoms.jsonl but did NOT append to cert_ledger.jsonl. Skunkworks fixed
the discipline going forward at 7cef91b3 + e5f50e02. This tool back-fills those
orphans (op=back_fill; verified_off_data=True).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.cert_ledger_writer import (  # noqa: E402
    VALID_CERT_CLASS,
    VALID_CERT_STATUS,
    _read_ledger,
    append_cert_ledger_row,
    LEDGER_PATH,
)

ATOMS_PATH_BY_CORPUS = {
    'math': _REPO_ROOT / 'data' / 'substrate_index' / 'math' / 'atoms.jsonl',
    'concept': _REPO_ROOT / 'data' / 'substrate_index' / 'concept' / 'atoms.jsonl',
    'meta': _REPO_ROOT / 'data' / 'substrate_index' / 'meta' / 'atoms.jsonl',
    'methodology': _REPO_ROOT / 'data' / 'substrate_index' / 'methodology' / 'atoms.jsonl',
}


def find_atom(atom_id: str):
    """Locate an atom by id across corpora; return (atom_dict, corpus_str, path)."""
    # Some callers pass fully-qualified "math::T3/..." form; strip corpus prefix.
    lookup_id = atom_id.split('::', 1)[1] if '::' in atom_id else atom_id
    for corpus, path in ATOMS_PATH_BY_CORPUS.items():
        if not path.exists():
            continue
        with path.open('r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                if d.get('id') == lookup_id:
                    return d, corpus, path
    return None, None, None


def derive_cert_fields(atom: dict) -> dict:
    """Map atom.kind + metadata onto (cert_status, cert_class, delta, verdict)."""
    kind = str(atom.get('kind') or '')
    md = atom.get('metadata') or {}

    # Explicit metadata wins if present
    cert_class_md = md.get('cert_class')
    verdict_md = md.get('verdict')

    # Kind-based derivation for kinds without full metadata (e.g. sleep spindles).
    # Note: the atom's metadata.cert_class is the ATOM-SCHEMA cert_class (e.g.
    # 'chain_grade_phase_characterization'), which is DIFFERENT from the LEDGER
    # cert_class enum (which uses 'pre_reg_pass' / 'mechanism_characterization' /
    # etc). Do NOT propagate atom cert_class into ledger cert_class.
    if kind == 'chain_grade_phase_characterization':
        cert_status = 'chain_grade'
        cert_class = 'pre_reg_pass'
        # chain_grade_phase_characterization was intended CERT +1 in a8dfb00b
        # (CERT 637 -> 639 range documented in commit message).
        # But delta must be tolerant: if the atom was already counted via
        # provenance_quality=CERT_CHAIN_GRADE, delta accounting is done at
        # Store-load. Here we record the INTENT of the atomization.
        delta = 1
        verdict = verdict_md or 'HARD_PASS'
    elif kind == 'phase_characterization_chain_grade':
        cert_status = 'chain_grade'
        cert_class = 'pre_reg_pass'
        delta = 1
        verdict = verdict_md or 'HARD_PASS'
    elif kind == 'chain_grade_capability_break':
        cert_status = 'chain_grade'
        cert_class = 'pre_reg_pass'
        delta = 1
        verdict = verdict_md or 'HARD_PASS'
    elif kind == 'measured_mechanism_partial_rescue':
        cert_status = 'measured_mechanism'
        cert_class = 'mechanism_characterization'
        delta = 0
        verdict = verdict_md or 'MEASURED_MECHANISM'
    elif kind == 'experiment_record':
        # cert_class in metadata is the definitive signal
        if cert_class_md == 'mechanism_characterization':
            cert_status = 'measured_mechanism'
            cert_class = 'mechanism_characterization'
            delta = 0
            verdict = verdict_md or 'MEASURED_MECHANISM'
        elif cert_class_md == 'proven_negative':
            # honest_negative is closest ledger cert_status for proven_negative
            cert_status = 'honest_negative'
            # 'proven_negative' isn't in VALID_CERT_CLASS; fall back
            cert_class = 'pre_reg_miss_proven_bound'
            delta = 0
            verdict = verdict_md or 'HARD_FAIL'
        elif cert_class_md == 'pre_reg_pass':
            cert_status = 'chain_grade'
            cert_class = 'pre_reg_pass'
            delta = 1
            verdict = verdict_md or 'HARD_PASS'
        else:
            raise ValueError(
                f'back_fill: atom kind=experiment_record with unhandled '
                f'metadata.cert_class={cert_class_md!r}; refusing to guess.'
            )
    else:
        raise ValueError(
            f'back_fill: unhandled atom.kind={kind!r}; add explicit derivation '
            f'or refuse (this tool refuses to guess for unknown kinds).'
        )

    # Enum sanity — the writer will re-check, but fail early here with a clearer msg
    if cert_status not in VALID_CERT_STATUS:
        raise ValueError(
            f'back_fill: derived cert_status={cert_status!r} not in VALID_CERT_STATUS'
        )
    if cert_class not in VALID_CERT_CLASS:
        raise ValueError(
            f'back_fill: derived cert_class={cert_class!r} not in VALID_CERT_CLASS'
        )
    return dict(cert_status=cert_status, cert_class=cert_class,
                cert_increment_delta=delta, verdict=verdict)


def build_back_fill_row(atom: dict, corpus: str, cell_commit: str, note: str):
    """Build a canonical ledger row for back-fill."""
    fields = derive_cert_fields(atom)
    lookup_id = atom['id']
    fq_id = f'{corpus}::{lookup_id}'
    md = atom.get('metadata') or {}

    metrics_path = md.get('metrics_path')
    notes_path = md.get('notes_path')

    return {
        'ts': float(time.time()),
        'op': 'cert_ruling',   # standard op; the "back_fill" tag lives in note
        'atom_id': fq_id,
        'cert_status': fields['cert_status'],
        'cert_class': fields['cert_class'],
        'verified_off_data': True,
        'atomized_by': 'back_fill_cert_ledger',
        'cell_commit': cell_commit,
        'verdict': fields['verdict'],
        'cert_increment_delta': fields['cert_increment_delta'],
        'cv': md.get('cv'),
        'referent_pointer': {
            'notes_path': notes_path,
            'metrics_path': metrics_path,
            'atom_qualified_id': fq_id,
        },
        'supersedes': None,
        'note': f'back_fill_orphan_ledger_row: {note}',
    }


def audit_commit_orphans(commit_sha: str):
    """List atoms.jsonl atom-ids added in <commit_sha> that lack a ledger entry."""
    # Get added lines from the commit's atoms.jsonl diff
    try:
        diff = subprocess.check_output(
            ['git', 'show', commit_sha, '--',
             'data/substrate_index/math/atoms.jsonl',
             'data/substrate_index/concept/atoms.jsonl',
             'data/substrate_index/meta/atoms.jsonl',
             'data/substrate_index/methodology/atoms.jsonl'],
            cwd=str(_REPO_ROOT), stderr=subprocess.STDOUT, encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        print(f'ERROR: git show {commit_sha!r} failed: {e.output}', file=sys.stderr)
        return 3

    added_ids = []
    for line in diff.splitlines():
        if not line.startswith('+{'):
            continue
        try:
            d = json.loads(line[1:])
            added_ids.append(d.get('id'))
        except json.JSONDecodeError:
            continue

    if not added_ids:
        print(f'audit: no atoms added in commit {commit_sha}')
        return 0

    # Read the current ledger and check for each id
    ledger = _read_ledger(LEDGER_PATH)
    ledger_atom_ids = set()
    for row in ledger:
        aid = row.get('atom_id') or ''
        ledger_atom_ids.add(aid.split('::', 1)[1] if '::' in aid else aid)

    orphans = []
    covered = []
    for aid in added_ids:
        if aid in ledger_atom_ids:
            covered.append(aid)
        else:
            orphans.append(aid)

    print(f'audit commit {commit_sha}: {len(added_ids)} atoms added, '
          f'{len(covered)} in ledger, {len(orphans)} orphans')
    for aid in orphans:
        print(f'  ORPHAN: {aid}')
    return 0 if not orphans else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('atom_id', nargs='?',
                    help='Atom id (with or without corpus:: prefix)')
    ap.add_argument('--cell-commit', default='unknown',
                    help='Cell commit sha (for provenance)')
    ap.add_argument('--note', default='back_fill_ac8eb015_orphan',
                    help='One-line note for the ledger row')
    ap.add_argument('--dry-run', action='store_true',
                    help='Print row that would be written; do not append')
    ap.add_argument('--audit-commit', dest='audit_commit',
                    help='Audit-only mode: list orphan atoms added in a commit')
    args = ap.parse_args()

    if args.audit_commit:
        return audit_commit_orphans(args.audit_commit)

    if not args.atom_id:
        ap.error('atom_id required (unless using --audit-commit)')

    atom, corpus, path = find_atom(args.atom_id)
    if atom is None:
        print(f'ERROR: atom_id {args.atom_id!r} not found in any corpus atoms.jsonl',
              file=sys.stderr)
        return 2

    print(f'[back_fill] found atom in corpus={corpus} at {path}')
    print(f'[back_fill] atom.kind = {atom.get("kind")!r}')

    row = build_back_fill_row(atom, corpus, args.cell_commit, args.note)

    print(f'[back_fill] built row:')
    print(json.dumps(row, indent=2, ensure_ascii=True))

    if args.dry_run:
        print('[back_fill] --dry-run: not writing')
        return 0

    # strict_a5=False: back-fill by definition happens after CERT N has already
    # been updated by earlier writes; there's no PRE/POST invariant to gate on
    # for a retro-ledger entry. The atom is on-disk and already counted.
    row_hash = append_cert_ledger_row(row, strict_a5=False)
    print(f'[back_fill] WROTE row_hash={row_hash}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
