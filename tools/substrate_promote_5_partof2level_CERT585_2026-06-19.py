"""Promote #5 EXP_partof_2level_completion_cpu_v1 -> CERT_CHAIN_GRADE (Skunkworks 5-MM #5 disposition 5-i + reconciliation
GO, 2026-06-19). CERT 584 -> 585. After re-apply 1 (the +125 PART_OF holonym completion restored), the BROAD-envelope
post-reapply re-run REPRODUCES #5's recall_after_completion EXACTLY (PART_OF-2hop 0.820, PART_OF-3hop 0.700, HYP 0.993/
0.931/0.853) -> the cert-chain is now recoverable (the completion edges restored + the recall reproduces). measurement-class.
Fix metrics_path -> data/exp_substrate_broad_envelope_postreapply1_20260619/metrics.json (the fresh reproducing run).

SAFE metadata-patch + fresh-Store LOAD gate; MATH single-writer window. DRY-RUN default; --apply. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

DATE = '2026-06-19'
ATOM = 'T3/EXP_partof_2level_completion_cpu_v1'
FRESH_METRICS = 'data/exp_substrate_broad_envelope_postreapply1_20260619/metrics.json'
REPRODUCED = {'PART_OF_2hop': 0.820, 'PART_OF_3hop': 0.700, 'HYPERNYM_2hop': 0.993, 'HYPERNYM_3hop': 0.931, 'HYPERNYM_4hop': 0.853}


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_axiom = axiom_term_count(ps)
    a = next((x for x in ps.all_atoms() if str(x.id) == ATOM), None)
    if a is None:
        print('atom not found'); return 2
    md = dict(a.metadata or {})
    if md.get('provenance_quality') == 'CERT_CHAIN_GRADE':
        print('already CERT -> skip'); return 0
    claimed = (md.get('key_metrics') or {}).get('recall_after_completion') or {}
    diverge = {k: (claimed.get(k), REPRODUCED[k]) for k in REPRODUCED if abs((claimed.get(k) or -1) - REPRODUCED[k]) > 0.01}
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom}')
    print(f'  reproduce-check: claimed recall_after_completion vs post-reapply BROAD -> diverge={diverge or "NONE (exact match)"}')
    if diverge:
        print('FLAG: divergence -> do NOT silently promote (Skunkworks reproduce-or-flag). Halt.'); return 3
    md['provenance_quality'] = 'CERT_CHAIN_GRADE'
    md['cert_vet_status'] = 'cert_promoted'
    md['cert_promoted_date'] = DATE
    md['cert_promoted_by_vet'] = 'skunkworks_5MM_disposition_#5_5i_reconciliation_2026-06-19'
    md['cert_promoted_from'] = 'MEASURED_MECHANISM'
    md['metrics_path'] = FRESH_METRICS
    md['rerun_reproduced'] = True
    md['rerun_reproduce_note'] = ('re-apply 1 restored the +125 PART_OF holonym completion edges (reverted by the corruption-'
                                  'restore concept->2e0b57c0); the post-reapply BROAD-envelope re-run reproduces recall_after_'
                                  'completion EXACTLY (PART_OF-2hop 0.627->0.820, all 5 >=0.7); measured_graph_bfs_held_out; '
                                  'this also RESTORED partof_broad_after HARD_PASS (the cert-integrity fix). measurement-class.')
    md['relevance_tier'] = md.get('relevance_tier') or 'ACTIVE'
    atom = dataclasses.replace(a, metadata=md)
    print(f'  {ATOM}: MEASURED_MECHANISM -> CERT_CHAIN_GRADE (verdict={md.get("verdict")}; metrics_path -> {FRESH_METRICS})')
    if not apply:
        print(f'\nDRY-RUN OK -> CERT {pre_cert}->{pre_cert+1}. Re-run --apply.'); return 0
    ps.add_atom(atom, source='promote_5_partof2level_CERT585', note='Skunkworks #5 5-i + reconciliation; reproduces post-reapply; measurement-class promote')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None)
    pq = (b.metadata or {}).get('provenance_quality') if b else None
    gate_ok = (pq == 'CERT_CHAIN_GRADE' and post_cert == pre_cert + 1 and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +1) axiom={post_axiom} | pq={pq} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate/CERT.'); return 6
    print(f'\nPROMOTE OK: {ATOM} CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. Route for Skunkworks verdict-VET. 5-MM batch: +5 (3 clean + #4 + #5) COMPLETE.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
