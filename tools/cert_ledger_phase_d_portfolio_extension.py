"""Phase D extension: project portfolio_state PP-rows into cert_ledger.jsonl.

Per Phase B window-2 finding (`notes/phase_b_window2_cert_trail_2026-06-22.md`):
the BIG window-2-era cert events (COMP-DEPTH cliff / WAVES 1-4 / ~67 HP-cells /
+56 PP-rows PP-229..PP-284 / k-gram-XOR / theta-burst / abduction-kernel) live in
`notes/substrate_capability_map.md` (the "portfolio_state" surface, NOT cell-atoms
in the Store). Phase A's `provenance_quality == CERT_CHAIN_GRADE` rule cannot see
them. Phase D projects each PP-row as one ledger row with a DISTINCT atom-id
namespace so the two surfaces never collide.

Scope of THIS spawn:
- Reads `notes/substrate_capability_map.md`
- Extracts every `**NEW ROW PP-NNN:**` cert event (the per-cycle portfolio rows)
- Skips the table-style PP-1..PP-55 capability-descriptor rows (those are
  capability ANCHORS, not cert events; they have their own dashboard projection)
- One ledger row per NEW-ROW entry; delta=0 (cert-neutral; this is a SUBSET
  projection, NOT a re-counting of live CERT N)
- atom_id = `portfolio::PP-NNN` (own namespace; no collision with `math::T3/EXP_*`)
- cert_status derived from PP-row verdict (HP/HARD_PASS -> chain_grade;
  MIDDLE_BAND -> under_classified; HARD_FAIL -> honest_negative)
- cert_class = `infra_record` (Phase D rows are historical portfolio projections,
  NOT math chain-grade rulings; the distinction is the load-bearing observability
  signal that Phase A and Phase D occupy different planes)
- verified_off_data = null (seeded-not-audited; bulk historical seed; matches the
  Phase A convention for the original seed)
- ts: derived from cycle-number via a cycle->date lookup built from the
  `orchestrator_to_research_results_summary_YYYY-MM-DD_cycleNNN.md` filenames;
  ALL cycle-bearing PP-rows get a ts; non-cycle rows get NULL
- cell_commit = null (PP-row prose does not cite SHAs)
- cert_increment_delta = 0 (CERT-neutral; this is a SUBSET projection)

Idempotent on re-run via the cert_ledger_writer.append_cert_ledger_row(...)
whole-ledger structural-match (modulo ts) check.

Run from project root with .venv:
    .venv/Scripts/python.exe tools/cert_ledger_phase_d_portfolio_extension.py --dry-run
    .venv/Scripts/python.exe tools/cert_ledger_phase_d_portfolio_extension.py
"""
from __future__ import annotations
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

LEDGER_PATH = _REPO / 'data' / 'substrate_index' / 'meta' / 'cert_ledger.jsonl'
CAP_MAP_PATH = _REPO / 'notes' / 'substrate_capability_map.md'
NOTES_DIR = _REPO / 'notes'

# Regex for the NEW-ROW PP-N entries. Captures: id, name, verdict
# Format examples:
#   **NEW ROW PP-179:** nary_relation_roles_cpu_v1 HP v521: ...
#   **NEW ROW PP-303:** negres_struct_align_cpu_v1 [LVH-274-NOTED] HARD_PASS v554: ...
#   **NEW ROW PP-379: pos_discriminative_perceptron_cpu_v1 HARD_PASS v569:** ...
#   **NEW ROW PP-413: substrate_cliff_sharpness_N_scaling_gpu_v1 LOCATION-CONFIRMED + SHARPNESS-REFUTED v592:** ...
PP_ROW_RE = re.compile(
    r'^\*\*NEW ROW PP-?(\d+):?\*?\*?\s+'                 # PP id + optional colon-asterisk
    r'([a-zA-Z0-9_]+)'                                    # cell name
    r'(?:\s+\[[^\]]+\])?'                                 # optional [LVH-...] tag
    r'\s+([A-Z][A-Z_+\-]+)'                               # verdict token
    r'\s+v(\d+):'                                         # cap_map version
    r'(.*)$',                                             # remainder
    re.MULTILINE,
)

# Cycle reference inside the PP-row body
CYCLE_RE = re.compile(r'\(cycle\s+(\d+)\b')

# Verdict normalization
VERDICT_NORMALIZE = {
    'HP': 'HARD_PASS',
    'HARD_PASS': 'HARD_PASS',
    'HARDPASS': 'HARD_PASS',
    'MIDDLE_BAND': 'MIDDLE_BAND',
    'MIDDLE': 'MIDDLE_BAND',
    'MIDDLEBAND': 'MIDDLE_BAND',
    'HARD_FAIL': 'HARD_FAIL',
    'HARDFAIL': 'HARD_FAIL',
    'HF': 'HARD_FAIL',
    'FAIL': 'HARD_FAIL',
    # custom / multi-token verdicts collapse to UNDER_CLASSIFIED in cert_status mapping
}

PASS_TOKENS = {'HP', 'HARD_PASS', 'HARDPASS'}
MIDDLE_TOKENS = {'MIDDLE_BAND', 'MIDDLE', 'MIDDLEBAND'}
FAIL_TOKENS = {'HARD_FAIL', 'HARDFAIL', 'HF', 'FAIL'}


def cert_status_for_verdict(raw_verdict):
    """Map a parsed verdict string to (cert_status, cert_class) for Phase D rows.

    Phase D cert_class is ALWAYS 'infra_record' (this is a historical portfolio
    projection, not a math chain-grade ruling). cert_status varies with verdict.
    """
    v = raw_verdict.upper()
    if v in PASS_TOKENS:
        return 'chain_grade', 'infra_record'
    if v in MIDDLE_TOKENS:
        return 'under_classified', 'infra_record'
    if v in FAIL_TOKENS:
        return 'honest_negative', 'infra_record'
    # Custom verdicts like LOCATION-CONFIRMED, MIXED, etc.
    return 'under_classified', 'infra_record'


def normalize_verdict(raw_verdict):
    """Return canonical verdict string preserving custom multi-token forms."""
    v = raw_verdict.upper()
    if v in VERDICT_NORMALIZE:
        return VERDICT_NORMALIZE[v]
    return raw_verdict  # preserve custom: LOCATION-CONFIRMED, MIXED, etc.


def build_cycle_to_date_map():
    """Scan orchestrator results-summary note filenames for cycle->date lookup.

    Returns: dict[int, datetime.date]
    """
    cycle_to_date = {}
    pattern = re.compile(
        r'^orchestrator_to_research_results_summary_'
        r'(\d{4}-\d{2}-\d{2})_cycle(\d+)\.md$'
    )
    for child in NOTES_DIR.iterdir():
        if not child.is_file():
            continue
        m = pattern.match(child.name)
        if not m:
            continue
        date_str, cycle_str = m.group(1), m.group(2)
        cycle = int(cycle_str)
        try:
            date = _dt.date.fromisoformat(date_str)
        except ValueError:
            continue
        # Keep earliest (first occurrence) date per cycle
        if cycle not in cycle_to_date or date < cycle_to_date[cycle]:
            cycle_to_date[cycle] = date
    return cycle_to_date


def cycle_to_ts(cycle, cycle_to_date):
    """Map a cycle number to a Unix timestamp via the cycle->date lookup.

    Uses NEAREST-prior cycle if the exact cycle isn't in the map. Returns None if
    no cycle reference exists or if no neighbor cycle has a date.
    """
    if cycle is None:
        return None
    if cycle in cycle_to_date:
        date = cycle_to_date[cycle]
    else:
        # Nearest neighbor (prefer earlier)
        keys = sorted(cycle_to_date)
        if not keys:
            return None
        # Find largest key <= cycle
        candidate = None
        for k in keys:
            if k <= cycle:
                candidate = k
            else:
                break
        if candidate is None:
            candidate = keys[0]
        date = cycle_to_date[candidate]
    # Convert to noon-UTC of that date (stable, ordering-preserving)
    dt = _dt.datetime.combine(date, _dt.time(12, 0, 0))
    return dt.replace(tzinfo=_dt.timezone.utc).timestamp()


def parse_pp_rows(cap_map_path):
    """Extract NEW-ROW PP-NNN entries from substrate_capability_map.md.

    Returns: list of dicts with keys: pp_id, cell_name, verdict_raw, cap_map_v,
             cycle, raw_line, body_snippet
    """
    text = cap_map_path.read_text(encoding='utf-8')
    rows = []
    for m in PP_ROW_RE.finditer(text):
        pp_id = int(m.group(1))
        cell_name = m.group(2)
        verdict_raw = m.group(3).strip()
        cap_map_v = int(m.group(4))
        remainder = m.group(5)

        # Find cycle in the remainder (or the line if remainder is empty)
        cycle = None
        cm = CYCLE_RE.search(remainder)
        if cm:
            cycle = int(cm.group(1))

        rows.append({
            'pp_id': pp_id,
            'cell_name': cell_name,
            'verdict_raw': verdict_raw,
            'cap_map_v': cap_map_v,
            'cycle': cycle,
            'body_snippet': (remainder.strip()[:200] + '...') if len(remainder.strip()) > 200 else remainder.strip(),
        })
    return rows


def build_phase_d_rows(pp_rows, cycle_to_date):
    """Convert parsed PP-rows to ledger row dicts.

    Returns: (rows_list, stats_dict)
    """
    rows = []
    stats = {
        'chain_grade_hp_family': 0,
        'under_classified_middle_band': 0,
        'under_classified_custom_verdict': 0,
        'honest_negative_hard_fail': 0,
        'ts_from_cycle': 0,
        'ts_null_no_cycle': 0,
        'cap_map_versions_seen': set(),
        'cycles_seen': set(),
        'pp_ids_seen': set(),
        'duplicate_pp_ids': 0,
    }

    seen_pp_ids = set()
    for pr in pp_rows:
        pp_id = pr['pp_id']
        if pp_id in seen_pp_ids:
            stats['duplicate_pp_ids'] += 1
        seen_pp_ids.add(pp_id)
        stats['pp_ids_seen'].add(pp_id)
        stats['cap_map_versions_seen'].add(pr['cap_map_v'])
        if pr['cycle'] is not None:
            stats['cycles_seen'].add(pr['cycle'])

        cert_status, cert_class = cert_status_for_verdict(pr['verdict_raw'])
        verdict_norm = normalize_verdict(pr['verdict_raw'])

        # ts derivation
        ts = cycle_to_ts(pr['cycle'], cycle_to_date)
        if ts is not None:
            stats['ts_from_cycle'] += 1
        else:
            stats['ts_null_no_cycle'] += 1

        # Per-status counter (matches the cert_status mapping)
        if cert_status == 'chain_grade':
            stats['chain_grade_hp_family'] += 1
        elif cert_status == 'under_classified':
            if pr['verdict_raw'].upper() in MIDDLE_TOKENS:
                stats['under_classified_middle_band'] += 1
            else:
                stats['under_classified_custom_verdict'] += 1
        elif cert_status == 'honest_negative':
            stats['honest_negative_hard_fail'] += 1

        atom_id = f'portfolio::PP-{pp_id}'
        note_tag = (
            f'phase_d_portfolio_extension_PP_{pp_id}_'
            f'cell_{pr["cell_name"]}_'
            f'cap_map_v{pr["cap_map_v"]}_'
            f'cycle_{pr["cycle"]}_'
            f'verdict_{verdict_norm}'
        )

        row = {
            'ts': ts,
            'op': 'cert_ruling',
            'atom_id': atom_id,
            'cert_status': cert_status,
            'cert_class': cert_class,
            'verified_off_data': None,  # seeded-not-audited; matches Phase A bulk-seed convention
            'atomized_by': 'phase_d_portfolio_extension',
            'cell_commit': None,        # PP-row prose does not cite SHAs
            'verdict': verdict_norm,
            'cert_increment_delta': 0,  # cert-neutral: SUBSET projection, not re-counting
            'cv': None,
            'referent_pointer': {
                'notes_path': 'notes/substrate_capability_map.md',
                'metrics_path': None,
                'atom_qualified_id': atom_id,
            },
            'supersedes': None,
            'note': note_tag,
        }
        rows.append(row)

    # Convert sets to counts for printable stats
    stats['n_cap_map_versions'] = len(stats['cap_map_versions_seen'])
    stats['n_cycles'] = len(stats['cycles_seen'])
    stats['n_unique_pp_ids'] = len(stats['pp_ids_seen'])
    del stats['cap_map_versions_seen']
    del stats['cycles_seen']
    del stats['pp_ids_seen']

    return rows, stats


# ============================================================================
# A5 invariants (mirror Phase A pattern exactly)
# ============================================================================

def _cert_n(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )


def _axiom_n(store):
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


def main():
    dry_run = '--dry-run' in sys.argv

    print('=' * 72)
    print('Phase D cert_ledger portfolio_state extension')
    print(f'mode: {"DRY-RUN" if dry_run else "LIVE-WRITE"}')
    print('=' * 72)

    # ---------------- A5 PRE ----------------
    print('\n[PRE-GATE]')
    from backend.substrate_index.partition import PartitionedStore
    S = PartitionedStore(_REPO / 'data' / 'substrate_index')
    pre_cert = _cert_n(S)
    pre_ax = _axiom_n(S)
    pre_cap = _cap_pres_ok()
    print(f'  CERT N        = {pre_cert}')
    print(f'  axiom_count   = {pre_ax}')
    print(f'  cap_pres      = {"6/6" if pre_cap else "FAIL"}')
    assert pre_ax == 206, f'A5-PRE axiom drift {pre_ax} != 206'
    assert pre_cap, 'A5-PRE cap_pres FAIL'

    # Existing ledger snapshot
    if not LEDGER_PATH.exists():
        print('  ABORT: cert_ledger.jsonl does not exist; Phase A must be run first.')
        sys.exit(1)
    pre_ledger_lines = LEDGER_PATH.read_text(encoding='utf-8').splitlines()
    pre_ledger_count = sum(1 for ln in pre_ledger_lines if ln.strip())
    print(f'  cert_ledger.jsonl rows = {pre_ledger_count}')
    print('  PRE-GATE PASS')

    # ---------------- PARSE ----------------
    print('\n[PARSE]')
    if not CAP_MAP_PATH.exists():
        print(f'  ABORT: {CAP_MAP_PATH} does not exist')
        sys.exit(1)
    print(f'  Reading {CAP_MAP_PATH}')
    pp_rows = parse_pp_rows(CAP_MAP_PATH)
    print(f'  Parsed {len(pp_rows)} NEW-ROW PP-* entries')

    print('\n  cycle->date lookup')
    cycle_to_date = build_cycle_to_date_map()
    print(f'  {len(cycle_to_date)} cycle->date mappings from results-summary filenames')
    if cycle_to_date:
        keys = sorted(cycle_to_date)
        print(f'  cycle range: {keys[0]}..{keys[-1]}; date range: '
              f'{cycle_to_date[keys[0]]}..{cycle_to_date[keys[-1]]}')

    # ---------------- BUILD ----------------
    print('\n[BUILD]')
    rows, stats = build_phase_d_rows(pp_rows, cycle_to_date)
    print(f'  Total rows assembled: {len(rows)}')
    print(f'    chain_grade (HP/HARD_PASS, infra_record): {stats["chain_grade_hp_family"]}')
    print(f'    under_classified (MIDDLE_BAND):           {stats["under_classified_middle_band"]}')
    print(f'    under_classified (custom verdict):        {stats["under_classified_custom_verdict"]}')
    print(f'    honest_negative (HARD_FAIL):              {stats["honest_negative_hard_fail"]}')
    print(f'  unique PP-ids: {stats["n_unique_pp_ids"]} (duplicates in source: {stats["duplicate_pp_ids"]})')
    print(f'  unique cap_map versions: {stats["n_cap_map_versions"]}')
    print(f'  unique cycles: {stats["n_cycles"]}')
    print(f'  ts derived from cycle: {stats["ts_from_cycle"]}; null (no cycle): {stats["ts_null_no_cycle"]}')

    delta_sum = sum(r['cert_increment_delta'] for r in rows)
    print(f'  sum(cert_increment_delta) = {delta_sum} (expected: 0; Phase D is cert-neutral)')
    assert delta_sum == 0, f'Phase D must be cert-neutral; got delta-sum {delta_sum}'

    # Sample 5 rows for review
    print('\n  Sample rows (first 3 + middle + last):')
    sample_idx = [0, 1, 2, len(rows) // 2, len(rows) - 1] if len(rows) >= 5 else list(range(len(rows)))
    for idx in sample_idx:
        r = rows[idx]
        ts_str = (
            _dt.datetime.fromtimestamp(r['ts'], tz=_dt.timezone.utc).date().isoformat()
            if r['ts'] is not None else 'null'
        )
        print(f'    [{idx}] {r["atom_id"]:<20} {r["cert_status"]:<18} verdict={r["verdict"]:<12} ts={ts_str}')

    if dry_run:
        print('\n[DRY-RUN] No write. Stop here.')
        print('  re-run without --dry-run to perform live A5-gated write.')
        return 0

    # ---------------- LIVE WRITE ----------------
    print('\n[WRITE]')
    print(f'  Writing {len(rows)} rows to {LEDGER_PATH} via cert_ledger_writer (idempotent)')
    from tools.cert_ledger_writer import append_cert_ledger_row

    n_written = 0
    n_skipped_idempotent = 0
    for i, raw_row in enumerate(rows):
        # cert_ledger_writer expects the schema fields + optional ts; we ALREADY include ts
        try:
            # A5 invariants are gated per-row by the writer; CERT-N expected unchanged
            # throughout (delta=0). Pass expected pre/post equal to live cert.
            h = append_cert_ledger_row(
                raw_row,
                expected_cert_n_pre=pre_cert,
                expected_cert_n_post=pre_cert,  # delta=0 for Phase D
            )
            # Compare ledger row count delta to detect idempotent-skip
            cur_lines = LEDGER_PATH.read_text(encoding='utf-8').splitlines()
            cur_count = sum(1 for ln in cur_lines if ln.strip())
            expected_count = pre_ledger_count + n_written + 1
            if cur_count == expected_count:
                n_written += 1
            else:
                n_skipped_idempotent += 1
        except Exception as e:
            print(f'  FAIL row [{i}] {raw_row.get("atom_id")}: {e}')
            raise
        if (i + 1) % 50 == 0:
            print(f'  ... processed {i + 1}/{len(rows)} rows')

    print(f'  wrote: {n_written}; idempotent-skip: {n_skipped_idempotent}')

    # ---------------- A5 POST ----------------
    print('\n[POST-GATE]')
    S2 = PartitionedStore(_REPO / 'data' / 'substrate_index')
    post_cert = _cert_n(S2)
    post_ax = _axiom_n(S2)
    post_cap = _cap_pres_ok()
    post_lines = LEDGER_PATH.read_text(encoding='utf-8').splitlines()
    post_ledger_count = sum(1 for ln in post_lines if ln.strip())

    print(f'  CERT N        = {post_cert} (delta {post_cert - pre_cert}; expected 0)')
    print(f'  axiom_count   = {post_ax}')
    print(f'  cap_pres      = {"6/6" if post_cap else "FAIL"}')
    print(f'  ledger rows   = {post_ledger_count} (delta {post_ledger_count - pre_ledger_count})')

    assert post_cert == pre_cert, f'A5-POST CERT delta != 0 (got {post_cert - pre_cert})'
    assert post_ax == 206, f'A5-POST axiom drift {post_ax} != 206'
    assert post_cap, 'A5-POST cap_pres FAIL'

    # Verify ledger parses cleanly
    for ln in post_lines:
        if not ln.strip():
            continue
        json.loads(ln)  # raises on parse error
    print('  POST-GATE PASS (ledger re-parses clean)')

    print('\n' + '=' * 72)
    print('Phase D extension COMPLETE')
    print('=' * 72)
    print(f'  ledger rows pre  : {pre_ledger_count}')
    print(f'  ledger rows post : {post_ledger_count}')
    print(f'  Phase D rows added: {post_ledger_count - pre_ledger_count}')
    print(f'  CERT N           : {pre_cert} -> {post_cert} (delta 0; cert-neutral)')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
