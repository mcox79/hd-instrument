"""One-shot: enumerate all full-mode exp_* dirs, check coverage in cert_ledger.jsonl
and across substrate atoms.jsonl. Outputs structured audit data.

NOT a permanent tool - audit-spawn artifact 2026-06-28.
"""
import os, json, glob, re, sys
from collections import defaultdict

ROOT = 'data'
LEDGER = 'data/substrate_index/meta/cert_ledger.jsonl'

# Build set of atom_ids referenced in cert_ledger.jsonl
ledger_atoms = set()
ledger_metrics_paths = set()
ledger_by_atomid = {}
with open(LEDGER, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        rec = json.loads(line)
        aid = rec.get('atom_id', '')
        if aid:
            ledger_atoms.add(aid)
            ledger_by_atomid.setdefault(aid, []).append(rec)
        rp = rec.get('referent_pointer', {}) or {}
        if not isinstance(rp, dict):
            rp = {}
        mp = rp.get('metrics_path', '') or ''
        if isinstance(mp, list):
            for p in mp:
                if isinstance(p, str) and p:
                    ledger_metrics_paths.add(p.replace(chr(92), '/').strip())
        elif isinstance(mp, str) and mp:
            ledger_metrics_paths.add(mp.replace(chr(92), '/').strip())

# Build set of atom IDs across ALL partition atoms.jsonl
all_atom_ids = set()
all_atom_id_basenames = set()  # for fuzzy matching on cell name
partition_counts = {}
for ppath in glob.glob('data/substrate_index/*/atoms.jsonl'):
    partition = os.path.basename(os.path.dirname(ppath))
    count = 0
    with open(ppath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            count += 1
            aid = a.get('id', '') or a.get('atom_id', '')
            if aid:
                all_atom_ids.add(aid)
                # extract trailing name after last '/' for fuzzy match against cell name
                if '/' in aid:
                    bn = aid.rsplit('/', 1)[-1]
                    all_atom_id_basenames.add(bn.lower())
                all_atom_id_basenames.add(aid.lower())
    partition_counts[partition] = count

# Enumerate exp_ dirs
exp_dirs = sorted(glob.glob('data/exp_*'))
full_cells = []
smoke_only = []
selftest_only = []
no_metrics = []
for d in exp_dirs:
    name = os.path.basename(d)
    mpath = os.path.join(d, 'metrics.json')
    if not os.path.exists(mpath):
        no_metrics.append(name)
        continue
    lname = name.lower()
    if '_smoke' in lname or lname.endswith('_smoke') or 'smoketest' in lname:
        smoke_only.append(name)
    elif '_selftest' in lname or lname.endswith('_selftest'):
        selftest_only.append(name)
    else:
        try:
            with open(mpath, 'r', encoding='utf-8') as f:
                m = json.load(f)
            rm = m.get('run_mode', m.get('mode', ''))
            if isinstance(rm, str) and ('smoke' in rm.lower() or 'selftest' in rm.lower()):
                if 'smoke' in rm.lower():
                    smoke_only.append(name)
                else:
                    selftest_only.append(name)
            else:
                full_cells.append((name, m))
        except Exception:
            full_cells.append((name, {}))

print(f'Total exp dirs: {len(exp_dirs)}')
print(f'Full-mode cells: {len(full_cells)}')
print(f'Smoke-only cells: {len(smoke_only)}')
print(f'Selftest-only cells: {len(selftest_only)}')
print(f'No-metrics-json: {len(no_metrics)}')
print(f'Ledger distinct atom_ids: {len(ledger_atoms)}')
print(f'Ledger distinct metrics paths: {len(ledger_metrics_paths)}')
print(f'Atom partitions: {len(partition_counts)}; total atoms across all partitions: {sum(partition_counts.values())}')

# For each full cell, check if covered
covered_via_metrics_path = []
covered_via_atom_id = []
uncovered = []
for name, m in full_cells:
    # Stem name (strip exp_ prefix)
    stem = name[len('exp_'):] if name.startswith('exp_') else name
    cell_metrics_norm = f'data/{name}/metrics.json'
    cell_metrics_alt = f'data\\\\{name}\\\\metrics.json'.replace(chr(92), '/')
    if cell_metrics_norm in ledger_metrics_paths:
        covered_via_metrics_path.append(name)
        continue
    # Fuzzy: check if cell name (or stem) appears as substring in any atom id
    stem_l = stem.lower()
    matched = False
    for aid in all_atom_id_basenames:
        if stem_l in aid:
            covered_via_atom_id.append((name, aid))
            matched = True
            break
    if matched:
        continue
    uncovered.append((name, m))

print(f'\\nCoverage:')
print(f'  via metrics_path in ledger: {len(covered_via_metrics_path)}')
print(f'  via atom_id name match: {len(covered_via_atom_id)}')
print(f'  UNCOVERED: {len(uncovered)}')

# Write uncovered list
with open('/tmp/audit_uncovered_full_cells.json', 'w', encoding='utf-8') as f:
    out = []
    for name, m in uncovered:
        # Extract verdict-ish fields
        v = (m.get('verdict') or m.get('verdict_msg') or m.get('result') or m.get('status') or '')[:200] if isinstance(m, dict) else ''
        ts = m.get('timestamp', m.get('ts', '')) if isinstance(m, dict) else ''
        # mtime
        try:
            mt = os.path.getmtime(f'data/{name}/metrics.json')
        except:
            mt = 0
        out.append({'name': name, 'verdict': v, 'mtime': mt, 'ts': ts})
    out.sort(key=lambda x: x['mtime'])
    json.dump(out, f, indent=2)
print(f'\\nWrote /tmp/audit_uncovered_full_cells.json with {len(uncovered)} entries.')
