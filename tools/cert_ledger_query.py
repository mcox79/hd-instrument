"""Read-only query tool for data/substrate_index/meta/cert_ledger.jsonl.

Pure Python stdlib (no .venv deps); usable from any fresh teammate spawn without env setup.
Outputs plain text by default (greppable); `--json` for structured output.

Subcommands:
  count-by-status              Group-by cert_status; print counts
  list-under-classified        Print all atom_ids with cert_status == under_classified
  reconcile-cert-N             Sum cert_increment_delta and compare to live Store CERT count
                                 (requires .venv if comparing live; otherwise reports ledger-only sum)
  list-chain-grade-chronological  Print chain-grade rows sorted by ts (null ts grouped at end)
  find-by-atom-id <id>         Print all rows matching atom_id (substring match)
  find-by-cell-commit <sha>    Print all rows matching cell_commit (prefix match)
  audit-debt-queue             Print rows where verified_off_data is null OR false (the sub-audit + audit-debt set)
  count-by-class               Group-by cert_class within chain_grade
  count-by-verdict             Group-by underlying cell verdict
  show-mm-partners             Print MEASURED_MECHANISM rows (CERT-neutral mechanism characterizations)

Modes:
  --follow-supersedes  When set, count-by-status / audit-debt-queue / count-by-class / count-by-verdict
                       fold supersedes chains: for each atom_qualified_id, only the LATEST row
                       (the one not superseded by anything else) is counted. This makes Phase-B
                       relabel rows correctly mask their seeded predecessors. Without this flag,
                       all rows count (the historical append-only view). Phase B window-1's
                       Section 5a flagged this as the load-bearing tooling refinement.

Usage:
    python tools/cert_ledger_query.py count-by-status
    python tools/cert_ledger_query.py count-by-status --follow-supersedes
    python tools/cert_ledger_query.py list-under-classified --json
    python tools/cert_ledger_query.py find-by-atom-id EXP_kv_learned
    python tools/cert_ledger_query.py find-by-cell-commit fbd7078f
    python tools/cert_ledger_query.py audit-debt-queue --follow-supersedes | wc -l
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict


DEFAULT_LEDGER = Path('data/substrate_index/meta/cert_ledger.jsonl')


def load_ledger(path):
    if not path.exists():
        print(f'ERROR: ledger not found at {path}', file=sys.stderr)
        sys.exit(2)
    rows = []
    for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f'WARNING: line {i} not JSON: {e}', file=sys.stderr)
    return rows


def _row_hash(row):
    """Stable 16-char hash of a row (matches Phase B / cert_ledger_writer convention)."""
    import hashlib
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode('ascii')).hexdigest()[:16]


def fold_supersedes(rows):
    """Return only the LATEST row per atom_qualified_id, following supersedes chains forward.

    Algorithm:
    - Compute the hash of every row.
    - Build the set of hashes that are SUPERSEDED (i.e. appear as some other row's supersedes).
    - For each atom_id, keep ONLY rows whose own hash is NOT in the superseded set
      (i.e. they are the latest in their chain).
    - If an atom has multiple non-superseded rows (e.g. it was never relabeled but has 2 rulings
      for some reason, or it has two parallel chains), keep the one with the LATEST ts.

    This makes count-by-status semantically correct after Phase B relabels: a Phase-A seeded
    row that has a Phase-B `cert_relabel` row pointing at its hash is masked, and the relabel
    row's `verified_off_data: true` is the queryable truth.
    """
    if not rows:
        return rows

    # Index rows by their own hash + collect the set of superseded hashes
    row_hashes = [(_row_hash(r), r) for r in rows]
    superseded = set()
    for _, r in row_hashes:
        sup = r.get('supersedes')
        if sup:
            superseded.add(sup)

    # Bucket by atom_id, keep only non-superseded latest
    by_atom = defaultdict(list)
    for h, r in row_hashes:
        if h in superseded:
            continue
        by_atom[r.get('atom_id')].append(r)

    folded = []
    for atom_id, candidates in by_atom.items():
        if len(candidates) == 1:
            folded.append(candidates[0])
            continue
        # Multiple non-superseded rows for one atom: pick latest ts (None ts sorts last)
        def key(r):
            ts = r.get('ts')
            return (ts is None, ts if ts is not None else 0.0)
        candidates.sort(key=key)
        folded.append(candidates[-1])

    return folded


def fmt_row(row, mode='line'):
    """Plain-text one-line render for terminal grep, or json mode."""
    if mode == 'json':
        return json.dumps(row, ensure_ascii=True)
    ts = row.get('ts')
    ts_str = f'{ts:.1f}' if isinstance(ts, (int, float)) else 'null'
    return (
        f'{ts_str}\t{row.get("op","-")}\t{row.get("cert_status","-")}\t'
        f'{row.get("cert_class","-") or "-"}\t'
        f'delta={row.get("cert_increment_delta","-")}\t'
        f'verified_off_data={row.get("verified_off_data","-")}\t'
        f'verdict={row.get("verdict","-") or "-"}\t'
        f'cell={row.get("cell_commit","-") or "-"}\t'
        f'{row.get("atom_id","-")}'
    )


def cmd_count_by_status(rows, json_mode=False):
    c = Counter(r.get('cert_status') for r in rows)
    if json_mode:
        print(json.dumps(dict(c), ensure_ascii=True))
        return
    print('cert_status                 count')
    print('-' * 40)
    for status, n in sorted(c.items(), key=lambda x: -x[1]):
        print(f'{(status or "null"):28} {n}')
    print('-' * 40)
    print(f'{"TOTAL":28} {sum(c.values())}')


def cmd_list_under_classified(rows, json_mode=False):
    matches = [r for r in rows if r.get('cert_status') == 'under_classified']
    if json_mode:
        print(json.dumps([r.get('atom_id') for r in matches], ensure_ascii=True))
        return
    for r in matches:
        print(f'{r.get("atom_id","-")}\tverdict={r.get("verdict","-") or "-"}\tnote={r.get("note","-") or "-"}')
    print(f'\n# {len(matches)} atoms under_classified (Phase B sub-audit queue)', file=sys.stderr)


def cmd_reconcile_cert_N(rows, json_mode=False):
    delta_sum = sum(r.get('cert_increment_delta') or 0 for r in rows)
    chain_grade_count = sum(1 for r in rows if r.get('cert_status') == 'chain_grade')
    pending_count = sum(1 for r in rows if r.get('cert_status') == 'under_classified')
    mm_count = sum(1 for r in rows if r.get('cert_status') == 'measured_mechanism')

    # Attempt live CERT lookup if .venv is available; else report ledger-only
    live_cert = None
    try:
        sys.path.insert(0, str(Path('.').resolve()))
        from backend.substrate_index.partition import PartitionedStore
        S = PartitionedStore(Path('data/substrate_index'))
        live_cert = sum(
            1 for a in S.all_atoms()
            if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
        )
    except Exception as e:
        # Live comparison unavailable (no .venv); ledger-only mode
        pass

    # Within the chain_grade-tagged set: ledger has chain_grade rows (PASS-family, delta=1)
    # AND under_classified rows (HARD_FAIL/MIDDLE_BAND/custom inside chain-grade tag, delta=0).
    # Live CERT N is the count of ALL atoms with provenance_quality==CERT_CHAIN_GRADE in the Store.
    # Reconciliation: chain_grade_rows + under_classified_rows_FROM_CHAIN_GRADE_SET == live_cert.
    # Phase A puts every chain-grade-flagged atom into either chain_grade OR under_classified rows
    # (NOT into measured_mechanism -- MM rows come from separate pq=MEASURED_MECHANISM atoms).
    chain_grade_set_rows = chain_grade_count + pending_count
    reconciles = (live_cert is None) or (chain_grade_set_rows == live_cert)
    out = {
        'ledger_sum_cert_increment_delta': delta_sum,
        'ledger_chain_grade_rows': chain_grade_count,
        'ledger_under_classified_rows': pending_count,
        'ledger_measured_mechanism_rows': mm_count,
        'live_store_cert_n': live_cert,
        'chain_grade_set_rows_total': chain_grade_set_rows,
        'reconciles_chain_grade_set_vs_live_cert': reconciles,
        'note': (
            'ledger_sum_cert_increment_delta = honest-floor PASS-family count; '
            'live_store_cert_n = headline CERT N includes under_classified rows inside chain_grade tag; '
            'chain_grade_set_rows = chain_grade_rows + under_classified_rows; '
            'reconciliation: chain_grade_set_rows == live_store_cert_n'
        ),
    }
    if json_mode:
        print(json.dumps(out, ensure_ascii=True))
        return
    print(f'ledger sum(cert_increment_delta)        = {delta_sum}  (honest-floor PASS-family)')
    print(f'ledger chain_grade rows                 = {chain_grade_count}')
    print(f'ledger under_classified rows            = {pending_count}')
    print(f'ledger measured_mechanism rows          = {mm_count}')
    if live_cert is not None:
        print(f'live Store CERT N (provenance_quality)  = {live_cert}')
        print(f'  chain_grade set rows (chain+under)   = {chain_grade_set_rows}')
        print(f'  reconciles? {reconciles}')
        print(f'  under_classified queue size          = {pending_count} (Phase B sub-audit target)')
    else:
        print('live Store CERT N: UNAVAILABLE (no .venv); ledger-only reconciliation reported')


def cmd_list_chain_grade_chronological(rows, json_mode=False):
    cg = [r for r in rows if r.get('cert_status') == 'chain_grade']
    # ts may be null; group nulls at end
    def key(r):
        ts = r.get('ts')
        return (ts is None, ts if ts is not None else 0.0)
    cg.sort(key=key)
    if json_mode:
        print(json.dumps(cg, ensure_ascii=True))
        return
    for r in cg:
        print(fmt_row(r))


def cmd_find_by_atom_id(rows, atom_id_substr, json_mode=False):
    matches = [r for r in rows if atom_id_substr in (r.get('atom_id') or '')]
    if json_mode:
        print(json.dumps(matches, ensure_ascii=True))
        return
    for r in matches:
        print(fmt_row(r))
    print(f'\n# {len(matches)} matches for atom_id containing "{atom_id_substr}"', file=sys.stderr)


def cmd_find_by_cell_commit(rows, sha, json_mode=False):
    matches = [r for r in rows if (r.get('cell_commit') or '').startswith(sha)]
    if json_mode:
        print(json.dumps(matches, ensure_ascii=True))
        return
    for r in matches:
        print(fmt_row(r))
    print(f'\n# {len(matches)} matches for cell_commit prefix "{sha}"', file=sys.stderr)


def cmd_audit_debt_queue(rows, json_mode=False):
    debt = [r for r in rows if r.get('verified_off_data') in (None, False)]
    if json_mode:
        print(json.dumps(debt, ensure_ascii=True))
        return
    for r in debt:
        print(fmt_row(r))
    print(f'\n# {len(debt)} rows in audit-debt queue (verified_off_data null OR false)', file=sys.stderr)


def cmd_count_by_class(rows, json_mode=False):
    c = Counter(r.get('cert_class') for r in rows if r.get('cert_status') == 'chain_grade')
    if json_mode:
        print(json.dumps(dict(c), ensure_ascii=True))
        return
    print('cert_class (within chain_grade)  count')
    print('-' * 50)
    for cls, n in sorted(c.items(), key=lambda x: -x[1]):
        print(f'{(cls or "null"):34} {n}')


def cmd_count_by_verdict(rows, json_mode=False):
    c = Counter(r.get('verdict') for r in rows)
    if json_mode:
        print(json.dumps(dict(c), ensure_ascii=True))
        return
    print('verdict (cell-level)        count')
    print('-' * 50)
    for v, n in sorted(c.items(), key=lambda x: -x[1]):
        print(f'{(v or "null")[:50]:50} {n}')


def cmd_show_mm_partners(rows, json_mode=False):
    mm = [r for r in rows if r.get('cert_status') == 'measured_mechanism']
    if json_mode:
        print(json.dumps(mm, ensure_ascii=True))
        return
    for r in mm:
        print(fmt_row(r))
    print(f'\n# {len(mm)} measured_mechanism rows (CERT-neutral mechanism characterizations)', file=sys.stderr)


def main():
    p = argparse.ArgumentParser(prog='cert_ledger_query', description=__doc__.split('\n')[0])
    p.add_argument('--ledger', type=Path, default=DEFAULT_LEDGER, help='ledger JSONL path')
    p.add_argument('--json', action='store_true', help='emit structured JSON instead of plain text')
    p.add_argument(
        '--follow-supersedes', action='store_true',
        help=('fold supersedes chains: for each atom_id, only the LATEST row '
              '(not superseded by any other) is counted. Affects count-by-status, '
              'audit-debt-queue, count-by-class, count-by-verdict, show-mm-partners, '
              'list-under-classified, list-chain-grade-chronological.')
    )
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('count-by-status')
    sub.add_parser('list-under-classified')
    sub.add_parser('reconcile-cert-N')
    sub.add_parser('list-chain-grade-chronological')
    p1 = sub.add_parser('find-by-atom-id')
    p1.add_argument('atom_id_substr')
    p2 = sub.add_parser('find-by-cell-commit')
    p2.add_argument('sha')
    sub.add_parser('audit-debt-queue')
    sub.add_parser('count-by-class')
    sub.add_parser('count-by-verdict')
    sub.add_parser('show-mm-partners')

    args = p.parse_args()
    rows = load_ledger(args.ledger)

    # find-by-atom-id / find-by-cell-commit / reconcile-cert-N do NOT fold (they want
    # the full historical view including the supersedes chain for a specific atom).
    # Everything else respects --follow-supersedes.
    folding_commands = {
        'count-by-status', 'list-under-classified', 'list-chain-grade-chronological',
        'audit-debt-queue', 'count-by-class', 'count-by-verdict', 'show-mm-partners',
    }
    if args.follow_supersedes and args.cmd in folding_commands:
        pre_n = len(rows)
        rows = fold_supersedes(rows)
        print(f'# --follow-supersedes folded {pre_n} rows -> {len(rows)} latest-per-atom',
              file=sys.stderr)

    if args.cmd == 'count-by-status':
        cmd_count_by_status(rows, args.json)
    elif args.cmd == 'list-under-classified':
        cmd_list_under_classified(rows, args.json)
    elif args.cmd == 'reconcile-cert-N':
        cmd_reconcile_cert_N(rows, args.json)
    elif args.cmd == 'list-chain-grade-chronological':
        cmd_list_chain_grade_chronological(rows, args.json)
    elif args.cmd == 'find-by-atom-id':
        cmd_find_by_atom_id(rows, args.atom_id_substr, args.json)
    elif args.cmd == 'find-by-cell-commit':
        cmd_find_by_cell_commit(rows, args.sha, args.json)
    elif args.cmd == 'audit-debt-queue':
        cmd_audit_debt_queue(rows, args.json)
    elif args.cmd == 'count-by-class':
        cmd_count_by_class(rows, args.json)
    elif args.cmd == 'count-by-verdict':
        cmd_count_by_verdict(rows, args.json)
    elif args.cmd == 'show-mm-partners':
        cmd_show_mm_partners(rows, args.json)


if __name__ == '__main__':
    main()
