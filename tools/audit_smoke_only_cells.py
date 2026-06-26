"""Audit smoke/low-seed HARD_PASS cells against cert ledger.

Identifies chain-grade-eligible cells stuck in smoke/low-seed state with no
corresponding cert atom — these are the rediscovery-risk surface that needs
back-fill cycles to systematically address.

USAGE:
  python tools/audit_smoke_only_cells.py [--strategic-only] [--max-age-days N]

Default: reports all strategic-keyword smoke-only HARD_PASS cells not in cert
ledger, sorted by anchor name.

Output columns: anchor | mode | n_seeds | age_days | path | strategic_keywords
"""
import json
import os
import glob
import time
import sys
import argparse


STRATEGIC_KEYWORDS = [
    'refuse', 'audit', 'kv_', 'compose', 'multihop', 'multi_hop', 'continual',
    'intent', 'capacity', 'cleanup', 'partition', 'segregat', 'composit',
    'binding', 'wm_', 'working', 'sequence', 'graph', 'verify', 'distill',
    'stage', 'cert', 'rollback', 'audit', 'permutation', 'encoder', 'lever',
    'routing', 'attention', 'cleanup', 'merkle', 'temporal',
]


def load_cert_anchors(cert_ledger_path):
    """Extract unique cell-anchor signatures from cert ledger."""
    anchors = set()
    if not os.path.exists(cert_ledger_path):
        return anchors
    with open(cert_ledger_path) as f:
        for line in f:
            try:
                r = json.loads(line)
                atom_id = r.get('atom_id', '')
                if 'EXP_' in atom_id:
                    parts = atom_id.split('EXP_', 1)
                    if len(parts) > 1:
                        anchors.add(parts[1].split('_chain_grade')[0]
                                    .split('_HARD_FAIL')[0]
                                    .split('_MM')[0]
                                    .split('_honest_negative')[0])
            except Exception:
                continue
    return anchors


def is_in_cert(anchor, cert_anchors):
    """Permissive check: anchor substring matches any cert anchor signature."""
    return any(anchor in c or c in anchor for c in cert_anchors)


def find_smoke_only_HARD_PASS(data_dir, cert_anchors, max_age_days=None):
    """Scan all cells for smoke/low-seed HARD_PASS not in cert."""
    now = time.time()
    results = []
    for path in glob.glob(os.path.join(data_dir, 'exp_*/metrics.json')):
        try:
            mtime = os.path.getmtime(path)
            age_days = (now - mtime) / 86400.0
            if max_age_days is not None and age_days > max_age_days:
                continue
            with open(path) as f:
                d = json.load(f)
            verdict = d.get('verdict', '')
            if 'HARD_PASS' not in verdict:
                continue
            mode = d.get('run_mode', '?')
            n_seeds = d.get('n_seeds', 0) or 0
            anchor = d.get('anchor_name') or os.path.basename(os.path.dirname(path))
            if mode == 'smoke' or n_seeds in (0, 1, 2):
                if not is_in_cert(anchor, cert_anchors):
                    matched_kw = [k for k in STRATEGIC_KEYWORDS if k in anchor.lower()]
                    results.append({
                        'anchor': anchor,
                        'mode': mode,
                        'n_seeds': n_seeds,
                        'age_days': round(age_days, 1),
                        'path': path,
                        'strategic_keywords': matched_kw,
                    })
        except Exception:
            continue
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategic-only', action='store_true',
                        help='Only report cells matching strategic keywords')
    parser.add_argument('--max-age-days', type=int, default=None,
                        help='Skip cells older than N days')
    parser.add_argument('--data-dir', default='data',
                        help='Data directory (default: data)')
    parser.add_argument('--cert-ledger',
                        default='data/substrate_index/meta/cert_ledger.jsonl',
                        help='Cert ledger path')
    args = parser.parse_args()

    cert_anchors = load_cert_anchors(args.cert_ledger)
    print(f'# Cert ledger anchors: {len(cert_anchors)}', file=sys.stderr)

    cells = find_smoke_only_HARD_PASS(args.data_dir, cert_anchors, args.max_age_days)
    if args.strategic_only:
        cells = [c for c in cells if c['strategic_keywords']]

    cells.sort(key=lambda c: (-len(c['strategic_keywords']), c['age_days']))
    print(f'# Total: {len(cells)} smoke/low-seed HARD_PASS cells NOT in cert', file=sys.stderr)
    print(f'# anchor\tmode\tn_seeds\tage_days\tkeywords')
    for c in cells:
        kw = ','.join(c['strategic_keywords']) if c['strategic_keywords'] else '-'
        print(f"{c['anchor']}\t{c['mode']}\t{c['n_seeds']}\t{c['age_days']}\t{kw}")


if __name__ == '__main__':
    main()
