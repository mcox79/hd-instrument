"""Promote the 3 cleanly-recoverable MEASURED_MECHANISM atoms -> CERT_CHAIN_GRADE per Skunkworks's 5-MM per-atom
disposition (2026-06-19). CERT 580 -> 583. The 5-MM Track-B-at-scale batch (item 1, next-20h).

Per-atom (Skunkworks dispositions):
- #1 a1_multihop_provenance: promote as MEASURED-MECHANISM (verdict stays ATTRIBUTION, NOT a HARD_PASS WIN).
  NUANCE (verify-the-referent): the metrics.json DOES have a pre-reg band {hard_pass:0.7} that the run beat -- so
  "no pre-reg band" is refuted -- BUT n_seeds=1 is the BINDING constraint (single-seed != robust WIN). So per
  Skunkworks's override-needs-band-AND-adequate-seeds: default = measured-mechanism. Record the HARD_PASS run-outcome
  in key_metrics + honest-scope (single-seed; beat band but not multi-seed -> measured-mechanism, not a WIN-claim).
- #2 a1_8a_4channel_attribution: BACKFILL metrics_source=measured_torch_gpu (from surviving run-output) -> promote.
- #3 a1v2_ratio_profile: BACKFILL key_metrics (from surviving run-output) -> promote.

SAFE metadata-patch (load live -> dataclasses.replace metadata -> add_atom update -> fresh-Store all_atoms() LOAD gate).
MATH partition; serialized single-writer window. DRY-RUN default; --apply. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

DATE = '2026-06-19'
VET = 'skunkworks_5MM_disposition_2026-06-19'
TARGETS = ['T3/EXP_a1_multihop_provenance_cpu_v1', 'T3/EXP_a1_8a_4channel_attribution_v1', 'T3/EXP_a1v2_ratio_profile_v1']
JSON = {
    'T3/EXP_a1_multihop_provenance_cpu_v1': 'data/substrate_a1_multihop_provenance_cpu_v1/metrics.json',
    'T3/EXP_a1_8a_4channel_attribution_v1': 'data/exp_a1_8a_4channel_attribution_v1/metrics.json',
    'T3/EXP_a1v2_ratio_profile_v1': 'data/exp_a1v2_ratio_profile_v1/metrics.json',
}


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def _json(aid):
    try:
        return json.loads(Path(JSON[aid]).read_text(encoding='utf-8'))
    except Exception:
        return {}


def patch_metadata(aid, md):
    md = dict(md)
    j = _json(aid)
    # common promotion fields
    md['provenance_quality'] = 'CERT_CHAIN_GRADE'
    md['cert_vet_status'] = 'cert_promoted'
    md['cert_promoted_date'] = DATE
    md['cert_promoted_by_vet'] = VET
    md['cert_promoted_from'] = 'MEASURED_MECHANISM'
    md['relevance_tier'] = md.get('relevance_tier') or 'ACTIVE'
    if aid == 'T3/EXP_a1_multihop_provenance_cpu_v1':
        # measured-mechanism (ATTRIBUTION), NOT a HARD_PASS WIN
        md['verdict'] = 'ATTRIBUTION'
        km = dict(md.get('key_metrics') or {})
        km['run_outcome_measured'] = j.get('verdict')           # HARD_PASS (the measured run-OUTCOME)
        km['bands_in_run'] = j.get('bands')                     # {hard_pass:0.7, hard_fail:0.4}
        km['n_seeds'] = j.get('n_seeds')                        # 1
        km['metrics_source'] = j.get('metrics_source')
        for k in ('answer_found', 'edge_verifiable_100pct', 'max_depth', 'n_2hop_chains', 'min_cert_along_path'):
            if k in j:
                km[k] = j[k]
        md['key_metrics'] = km
        md['n_seeds'] = j.get('n_seeds')
        md['honest_scope'] = ('promoted as MEASURED-MECHANISM (verdict=ATTRIBUTION), NOT a HARD_PASS WIN: the run-output '
                              'beat the pre-registered band (hard_pass=0.7) BUT n_seeds=1 (single-seed != robust WIN; '
                              'could be seed-luck). Per Skunkworks override-needs-band-AND-adequate-seeds, default = '
                              'measured-mechanism. The HARD_PASS is recorded as the measured run-outcome in key_metrics. '
                              'A multi-seed re-run could later upgrade to a WIN-claim.')
        md['promote_note'] = 'cert-chain recoverable (measured_graph_bfs + key_metrics + cell_commit + surviving run-output); measurement-class promote'
    elif aid == 'T3/EXP_a1_8a_4channel_attribution_v1':
        md['metrics_source'] = j.get('metrics_source')          # measured_torch_gpu (backfilled from run-output)
        md['metrics_source_backfilled'] = True
        md['metrics_source_backfill_from'] = JSON[aid]
        md['promote_note'] = 'metrics_source backfilled from surviving run-output (promotion-path #1); measurement-class promote'
    elif aid == 'T3/EXP_a1v2_ratio_profile_v1':
        # backfill key_metrics from the surviving run-output (the attribution findings)
        km = dict(md.get('key_metrics') or {})
        for k in ('measured_bounds', 'ratio_nonmonotone_any', 'interaction_only_nonmonotonicity',
                  'net_speedup_localization', 'n_cells', 'headline', 'attribution', 'localize', 'measures_quantity'):
            if k in j:
                km[k] = j[k]
        km['metrics_source'] = j.get('metrics_source')
        md['key_metrics'] = km
        md['key_metrics_backfilled'] = True
        md['key_metrics_backfill_from'] = JSON[aid]
        md['promote_note'] = 'key_metrics backfilled from surviving run-output; measurement-class promote'
    return md


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_axiom = axiom_term_count(ps)
    live = {str(a.id): a for a in ps.all_atoms() if str(a.id) in TARGETS}
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom} | present: {sorted(live)}', flush=True)
    if len(live) != len(TARGETS):
        print('HARD_FAIL: not all 3 present:', sorted(set(TARGETS) - set(live))); return 2
    patched = []
    for aid in TARGETS:
        a = live[aid]; md = a.metadata or {}
        if md.get('provenance_quality') == 'CERT_CHAIN_GRADE':
            print(f'  {aid}: already CERT -> skip'); continue
        nm = patch_metadata(aid, md)
        patched.append((aid, dataclasses.replace(a, metadata=nm)))
        print(f'  {aid}: MEASURED_MECHANISM -> CERT_CHAIN_GRADE (verdict={nm.get("verdict")}; {nm.get("promote_note")})')
    if not patched:
        print('nothing to promote.'); return 0
    if not apply:
        print(f'\nDRY-RUN OK: {len(patched)} ready -> CERT {pre_cert}->{pre_cert+len(patched)}. Re-run --apply.'); return 0
    for (aid, atom) in patched:
        ps.add_atom(atom, source='promote_3MM_clean_CERT583', note='Skunkworks 5-MM disposition; measurement-class promote')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    by = {str(a.id): a for a in ps2.all_atoms() if str(a.id) in TARGETS}
    all_cert = all((by[i].metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE' for i in TARGETS if i in by)
    gate_ok = (len(by) == len(TARGETS) and all_cert and post_cert == pre_cert + len(patched) and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +{len(patched)}) axiom={post_axiom} | all 3 CERT={all_cert} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    for aid in TARGETS:
        m = (by.get(aid).metadata or {})
        print(f'  {aid}: pq={m.get("provenance_quality")} verdict={m.get("verdict")} metrics_source={m.get("metrics_source")}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate/CERT count.'); return 6
    print(f'\nPROMOTE OK: 3 MEASURED_MECHANISM -> CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. Route for Skunkworks per-atom verdict-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
