"""Pure parsers for SSH outputs. No I/O, fully testable."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# News item enrichment: plain_language + importance inference
# ---------------------------------------------------------------------------

def _infer_importance(entry: dict) -> str:
    """Derive an importance tier (CRITICAL/HIGH/MEDIUM/LOW) from log entry heuristics.

    Criteria (highest tier wins):
      CRITICAL — capability newly demonstrated at FULL, structural closure (KILL / portfolio count
                 changed), or narrative flip (e.g., narrow → tiered SLA).
      HIGH     — envelope expansion/characterisation of existing cap; first-of-kind infra
                 milestone; major research delivery suggesting new direction.
      MEDIUM   — partial rescues, smoke results needing FULL confirmation, deferred-then-revived.
      LOW      — re-confirmations of existing FULL, routine cap_map bumps, error messages.
    """
    kind = entry.get("event_kind", "")
    summary = (entry.get("summary") or "").upper()
    substrate = (entry.get("substrate_product") or "").upper()
    outcome = (entry.get("outcome") or "").upper()
    combined = f"{summary} {substrate} {outcome}"

    # ---- CRITICAL ----
    # Capability structurally closed or portfolio count changed.
    if "KILL" in summary or "CLOSED" in summary or "CLOSURE" in combined:
        return "CRITICAL"
    if re.search(r"PORTFOLIO\s+\d+\s*[-→>]\s*\d+", combined):
        return "CRITICAL"
    # Narrative flip
    if "NARRATIVE FLIPPED" in combined or "WIDENS" in combined or "FLIPPED" in combined:
        return "CRITICAL"
    # Capability at FULL (newly demonstrated)
    if kind == "verdict" and "FULL" in summary and "PASS" in summary:
        return "CRITICAL"
    if kind == "verdict" and "FULL" in summary and re.search(r"\bPASS\b|\bDEMONSTRATED\b", summary):
        return "CRITICAL"

    # ---- HIGH ----
    if kind == "verdict" and "FULL" in summary:
        # Envelope expansion / characterisation
        if any(w in combined for w in ("ENVELOPE", "SLA", "EXPANSION", "CHARACTERIZ")):
            return "HIGH"
        return "HIGH"
    if kind == "research_delivery":
        return "HIGH"
    if kind == "audit":
        return "HIGH"
    if kind == "cap_map_committed":
        return "HIGH"
    if kind == "hard_gate":
        return "HIGH"

    # ---- MEDIUM ----
    if "PARTIAL" in summary or "INCONCLUSIVE" in summary or "NARROW" in summary:
        return "MEDIUM"
    if "SMOKE" in summary:
        return "MEDIUM"

    # ---- LOW ----
    return "LOW"


# Map of summary keyword fragments to plain-language templates.
# Checked in order; first match wins. Keys are uppercase strings to search
# in the combined summary+substrate_product text.
_PLAIN_LANGUAGE_TEMPLATES: list[tuple[str, str]] = [
    # ---- Closures ----
    ("CAP2_MARGIN_KILL",
     "We tested whether the substrate can gauge its own confidence in its answers (Cap 2). "
     "The correlation between confidence margin and correctness was below noise threshold in every tested stratum. "
     "This capability has been structurally closed; the portfolio shrunk by one."),
    ("CAP2", "Testing Cap 2 (self-monitoring / confidence annotation) — "
     "see summary for outcome details."),

    # ---- Crooks / forensic-erase (Cap 1) ----
    ("CROOKS_NOISE_CORRECTED_PASS",
     "Earlier we thought forensic-erase verification (Cap 1) broke under noise. "
     "Re-analysed with a noise-corrected theoretical bound (Sagawa-Ueda): the test actually passes at all noise levels tested. "
     "The capability's quality guarantee now comes with a tiered noise-tolerance certificate."),
    ("CROOKS_NOISE_ENVELOPE_KILL",
     "Forensic-erase verification (Cap 1) appeared to fail under noisy conditions. "
     "Follow-up research is being triggered to determine whether a corrected bound rescues this."),
    ("CROOKS",
     "Experiment touching Cap 1 (forensic erase / verifiable delete). See summary for outcome."),

    # ---- Streaming / Cap 3 ----
    ("STREAMING_NOISE_ENVELOPE_PASS",
     "The streaming inference capability (Cap 3) now passes with noise present — "
     "bit-flip rates tested all achieve throughput >= 0.9. "
     "The envelope is expanded to include noisy operating conditions."),
    ("STREAMING",
     "Experiment touching Cap 3 (streaming inference). See summary for outcome."),

    # ---- Online W / Cap 5 ----
    ("ONLINE_W_NOISE_ENVELOPE_NARROW",
     "The online-learning capability (Cap 5) works up to about 30% bit-flip noise but breaks above that. "
     "This documents the operating envelope: use it under moderate noise, avoid heavy noise regimes."),
    ("ONLINE_W_POLYAK_PARTIAL",
     "A Polyak-averaging variant of the online-learning weight update (Cap 5) partially rescues performance under noise "
     "but does not expand the envelope beyond what we already knew. The existing 30% ceiling holds."),
    ("ONLINE_W",
     "Experiment touching Cap 5 (online weight learning). See summary for outcome."),

    # ---- Beta-M / init experiments ----
    ("BETA_M_INIT_UNIFORM_KILL",
     "An experiment testing uniform initialisation of memory capacity parameters hit an out-of-memory error. "
     "This was diagnosed as an artefact (OOM) not a fundamental refutation of the mechanism."),
    ("BETA_M_INIT_OOM",
     "Capacity parameter sweep at high memory-to-dimension ratios was killed by OOM — expected behaviour at over-capacity, not a bug."),
    ("BETA_M",
     "Experiment on memory capacity parameters (Beta-M family). See summary for outcome."),

    # ---- Continual edit / Bet A ----
    ("BETA CONTINUAL_EDIT",
     "An attempt to continuously edit the substrate's memory at large dimension (N>=16384) ran out of memory. "
     "A hard gate is now in place blocking this class of experiment until a chunked-matmul refactor ships."),
    ("CONTINUAL_EDIT",
     "Experiment on continual memory editing. See summary for outcome."),

    # ---- PQ / order parameter ----
    ("PQ_OTHER_CARDINALITY",
     "Measurement of the substrate's order-parameter distribution (P(q)) resolved a hierarchical multi-scale structure: "
     "7 outer peaks each containing ~8-9 inner peaks (~60 total). "
     "This reconciles earlier partial observations and characterises the physical memory landscape."),
    ("PQ",
     "Experiment probing the order-parameter distribution P(q) of the substrate. See summary for outcome."),

    # ---- Audit ----
    ("HISTORICAL AUDIT",
     "A self-audit found the research priorities file was many versions out of date, "
     "several recent findings were never integrated, and some rescue sketches were missing. "
     "These gaps are being fixed."),
    ("AUDIT",
     "Scheduled self-audit of research state. See report for details."),

    # ---- Research delivery ----
    ("CROOKS NOISE-ROBUST",
     "Research deep-dive confirmed a noise-corrected theoretical bound that widens Cap 1's validity. "
     "This suggests re-analysing the earlier negative result rather than abandoning the capability."),

    # ---- Migration / infra ----
    ("FULL MIGRATION",
     "The orchestrator infrastructure was migrated: old cron jobs removed, five tabs closed, "
     "and the new file-system-event-driven orchestrator is now live."),
    ("ORCHESTRATOR SKELETON",
     "Initial orchestrator scaffolding built — dispatch system and the first five sub-agent prompts are in place."),
    ("MIGRATION",
     "Infrastructure change. See summary for details."),
    ("ORCHESTRATOR_INIT",
     "Orchestrator status log was initialised. Prior events are being backfilled."),
]


def _infer_plain_language(entry: dict) -> str:
    """Derive a plain-language explanation for a news item that lacks one.

    Checks the combined summary+substrate_product text against a keyword template
    table.  Falls through to a generic template if nothing matches.
    """
    summary = (entry.get("summary") or "")
    substrate = (entry.get("substrate_product") or "")
    outcome = (entry.get("outcome") or "")
    kind = entry.get("event_kind", "")
    combined_upper = f"{summary} {substrate} {outcome}".upper()

    for keyword, template in _PLAIN_LANGUAGE_TEMPLATES:
        if keyword.upper() in combined_upper:
            return template

    # Generic fallback by event kind
    if kind == "verdict":
        return (
            f"Experimental result: {summary}. "
            f"{('Outcome: ' + outcome) if outcome else ''}"
        ).strip()
    if kind == "research_delivery":
        mech = entry.get("mechanism", "")
        rec = entry.get("recommendation", "")
        return (
            f"Research finding: {summary}. "
            f"{('Mechanism: ' + mech + '. ') if mech else ''}"
            f"{('Recommended action: ' + rec) if rec else ''}"
        ).strip()
    if kind == "audit":
        return f"Audit completed: {summary}."
    if kind == "cap_map_committed":
        return f"The capability map was updated: {summary}."
    if kind == "hard_gate":
        return f"A hard gate was applied blocking further experiments: {summary}."
    return f"{summary}."


# Event kinds that promote to "news" on the For You tab. Routine churn events
# (sub_agent_dispatched/returned, queue_change, queue_add, routing) are filtered
# out — the user does not want to see them on the news feed.
#
# Policy: include anything a user would want to see (capability map changes,
# verdicts, research deliveries, audits, infra events, diagnostics).
# Exclude: routing_decision, routing_handled, exp_dev_dispatch, queue_refill,
# queue_state, runner_state, memory_write, exp_shipped, exp_dev_ship,
# routing, research_routing, exp_dev_upstream_push, upstream_push,
# exp_dev_handoff_filed, placeholder_filed, research_routing_filed — these
# are internal plumbing events that generate noise without user value.
_NEWS_KINDS = {
    # Core verdicts and capability map
    "verdict",
    "verdict_processed",       # verdict_handler processed output (includes cap map impact)
    "cap_map_committed",       # old name
    "cap_map_commit",          # new name (same semantic)
    "cap_map_change",          # inline annotation / CRITICAL cap map mutations
    "cap_map_annotation",
    # Research
    "audit",
    "meta_audit",
    "research_delivery",
    "research_drill_closure",
    "research_drill_delivered",
    "research_delivered",
    # Dispatch / pipeline
    # NOTE: experiment_queued intentionally excluded — it generates O(40+) entries
    # per wave and appears as "unread spam" since new experiments are queued constantly.
    # It is internal plumbing equivalent to exp_shipped/exp_dev_ship which are
    # already in the exclude list. Restored from _NEWS_KINDS 2026-05-26.
    "major_dispatch",
    "hard_gate",
    "architecture_rollout",
    # Infrastructure events the user cares about
    "watchdog_armed",
    "watchdog_patch",
    "watchdog_cache_staleness_fix",
    "watchdog_restart_or_patch",
    # Diagnostics and audits (sub-agent quality, routing ratio, etc.)
    "exp_dev_skill_audit",
    "diagnostic_test_quality_audit",
    "diagnostic_watchdog_truth",
    "diagnostic_routing_ratio_fix",
    "for_you_tab_diagnostic_fix",  # self-reference for diagnostic fix
    "for_you_ack_fix",             # self-reference for ack-persistence fix (2026-05-26)
    # Lifecycle / infra milestones
    "orchestrator_init",
    "migration",
    "infra",
    "fix",
    "resume",
    "runner_revived",
    "local_runner_revived",
    "strategy_proactive",
    "strategy_proactive_drill",
    "strategy_triage",
    "experiment_completed_batch",
    "gpu_reroute",
    "gpu_queue_drained_with_2_new_verdicts",
    "verdict_reclassification_cycle_v204",
    # Multi-session events (architecture v1 2026-05-31). Each parallel session
    # writes log_event(..., source='<session>'). The For-You source filter chips
    # let the user view by session; these event kinds opt-in to the news feed.
    "testbed_delivery",
    "testbed_session_started",
    "research_delivery",  # already above but kept here for documentation
    "research_session_started",
    "cloud_session_started",
    "cloud_delivery",
    "cloud_cost_alert",
    "cloud_budget_exceeded",
    "cloud_instance_launched",
    "cloud_instance_terminated",
    "cloud_watchdog_armed",
    # cloud_api_error intentionally excluded -- transient network blips are noise
    # in the news feed. Errors still hit status_log so the dashboard's debug
    # endpoint surfaces them; the user-facing feed stays clean.
}


def news_item_id(entry: dict) -> str:
    """Stable id for a status-log entry so acks survive restarts.

    Hash the ts + event_kind + summary. Any later edit to those fields would
    produce a different id, which is fine (treat as a new news item).
    """
    raw = f"{entry.get('ts','')}|{entry.get('event_kind','')}|{entry.get('summary','')}"
    return hashlib.sha1(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def derive_news_items(
    status_log: list[dict],
    acked_ids: set[str],
    limit: int = 30,
) -> list[dict]:
    """Pick news-worthy entries from the status log, drop acked, cap to limit.

    Returns list of dicts: {id, ts, event_kind, summary, headline, detail, outcome,
    sub_agents, mechanism, p_estimate, recommendation, plain_language, importance, raw}.

    plain_language and importance are taken from the entry if present (Option A —
    written at log time) or derived via heuristics (Option B — fallback for existing
    entries).

    Sorting: CRITICAL items always appear first, then HIGH, then MEDIUM, then LOW.
    Within each importance tier, items are ordered newest-first (status_log default).
    This ensures the user never has to scroll past LOW-importance items to find a
    CRITICAL result that landed in the same poll cycle.

    status_log is expected sorted newest-first (parse_status_log default).
    """
    _IMPORTANCE_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    out: list[dict] = []
    # Collect up to 3× limit candidates so importance-sorting can surface buried
    # CRITICAL/HIGH items that would otherwise fall below the raw limit cutoff.
    _collect_limit = min(limit * 3, len(status_log))
    _collected = 0
    for entry in status_log:
        if _collected >= _collect_limit:
            break
        kind = entry.get("event_kind", "")
        if kind not in _NEWS_KINDS:
            continue
        nid = news_item_id(entry)
        if nid in acked_ids:
            continue

        summary = entry.get("summary") or ""
        # Compose a short 1-line headline + 1-2 line detail.
        headline = summary
        detail_parts: list[str] = []
        for k in ("outcome", "recommendation", "substrate_product", "report"):
            v = entry.get(k)
            if v:
                detail_parts.append(str(v))
        detail = " · ".join(detail_parts)

        # Option A: use structured fields if already written at log time.
        # Option B: derive via heuristics when absent.
        plain_language = entry.get("plain_language") or _infer_plain_language(entry)
        importance = entry.get("importance") or _infer_importance(entry)

        out.append({
            "id": nid,
            "ts": entry.get("ts", ""),
            "event_kind": kind,
            "source": entry.get("source", ""),  # session attribution (architecture v1)
            "headline": headline,
            "detail": detail,
            "outcome": entry.get("outcome", ""),
            "sub_agents": entry.get("sub_agents", []),
            "mechanism": entry.get("mechanism", ""),
            "p_estimate": entry.get("p_estimate"),
            "recommendation": entry.get("recommendation", ""),
            "plain_language": plain_language,
            "importance": importance,
            "raw": entry,
        })
        _collected += 1

    # Sort: CRITICAL first, then HIGH, then MEDIUM, then LOW; newest-first within tier.
    # Stable sort preserves the within-tier newest-first order from status_log walk.
    out.sort(key=lambda item: _IMPORTANCE_RANK.get(
        (item.get("importance") or "LOW").upper(), 3
    ))
    return out[:limit]


def parse_acks(text: str) -> set[str]:
    """Parse data/orchestrator_news_acks.jsonl -> set of acked news_ids.

    Each line is {ts, news_id}. Malformed lines skipped silently.
    """
    out: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            d = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(d, dict):
            nid = d.get("news_id")
            if isinstance(nid, str):
                out.add(nid)
    return out


def parse_answers(text: str) -> list[dict]:
    """Parse data/orchestrator_answers.jsonl -> list of {ts, question_number, answer}."""
    out: list[dict] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            d = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(d, dict):
            out.append(d)
    return out


def parse_local_queue_doc(doc: dict | None) -> dict:
    """Adapt a local_cpu_queue/queue.json doc into the same shape the rest of the
    poller expects (status counts + pending list).

    The local queue uses 'completed'/'killed'/'pending' status strings — same
    canonical buckets as remote, so queue_counts() handles them directly.
    """
    return doc or {}


def safe_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def parse_nvidia_smi(out: str) -> dict:
    """Parse one CSV row from nvidia-smi --format=csv,noheader,nounits.

    Expected fields: utilization.gpu, memory.used, memory.total, temperature.gpu
    """
    row = next((ln for ln in out.strip().splitlines() if ln.strip()), "")
    parts = [p.strip() for p in row.split(",")]
    if len(parts) < 4:
        return {"util_pct": None, "mem_used_mb": None, "mem_total_mb": None, "temp_c": None}
    try:
        return {
            "util_pct": int(parts[0]),
            "mem_used_mb": int(parts[1]),
            "mem_total_mb": int(parts[2]),
            "temp_c": int(parts[3]),
        }
    except (ValueError, IndexError):
        return {"util_pct": None, "mem_used_mb": None, "mem_total_mb": None, "temp_c": None}


def estimate_expected_wall_s(
    name: str,
    queue_events_desc: list[dict],
    queue_doc: dict | None,
) -> tuple[float | None, str | None]:
    """Estimate expected wall time for an experiment.

    Returns (seconds, source) where source is one of:
      "historical" - mean wall_s of past DONE events for this name
      "timeout"    - timeout_s from queue.json (fallback when no history)
      None         - no estimate available

    Pure derivation; no schema additions.
    """
    samples = [
        ev["wall_s"] for ev in queue_events_desc
        if ev.get("name") == name and ev.get("event") == "DONE" and ev.get("wall_s")
    ]
    if samples:
        return sum(samples) / len(samples), "historical"
    if queue_doc:
        for e in queue_doc.get("experiments", []):
            if e.get("name") == name and e.get("timeout_s"):
                try:
                    return float(e["timeout_s"]), "timeout"
                except (TypeError, ValueError):
                    pass
    return None, None


def parse_progress_dir_listing(text: str) -> list[str]:
    """Parse `Get-ChildItem -Recurse -Filter progress.json` output, return list of
    directory paths that contain a progress.json file (e.g. C:\\...\\data\\exp_NAME).
    """
    dirs: list[str] = []
    current_dir: str | None = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Directory:"):
            current_dir = s[len("Directory:"):].strip()
            continue
        # File lines start with mode like "-a----"
        if current_dir and s.startswith("-") and "progress.json" in s:
            dirs.append(current_dir)
    return dirs


def find_running_from_log(events_desc: list[dict]) -> str | None:
    """Most recent START with no later DONE/FAIL on the same name.

    queue.log is the most timely signal of what's actually running — it gets the
    START line at experiment kickoff, before queue.json or heartbeat update.
    Walks newest-first, tracking which names have been terminated.
    """
    terminated: set[str] = set()
    for ev in events_desc:
        name = ev.get("name")
        if not name:
            continue
        if ev.get("event") in ("DONE", "FAIL"):
            terminated.add(name)
        elif ev.get("event") == "START" and name not in terminated:
            return name
    return None


def parse_event_log(text: str) -> list[dict]:
    """Parse the session events JSONL, tolerating malformed (e.g. torn-write) lines."""
    events: list[dict] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            ev = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(ev, dict):
            events.append(ev)
    return events


def parse_status_log(text: str) -> list[dict]:
    """Parse orchestrator_status_log.jsonl into a list of structured entries.

    Each entry has at minimum: ts, event_kind, summary.
    Optional fields: sub_agents, outcome, mechanism, p_estimate, recommendation,
    report, substrate_product.
    Returns entries sorted newest-first.

    Malformed lines are skipped with a stderr warning rather than dropping the
    whole file, so a single bad heredoc escape does not poison the dashboard.
    """
    import sys as _sys
    entries: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s:
            continue
        try:
            ev = json.loads(s)
        except (json.JSONDecodeError, ValueError) as exc:
            print(
                f"[parse_status_log] WARNING: skipping malformed line {lineno}: {exc}",
                file=_sys.stderr,
            )
            continue
        if not isinstance(ev, dict):
            print(
                f"[parse_status_log] WARNING: skipping non-dict line {lineno}",
                file=_sys.stderr,
            )
            continue
        # Normalize: ensure required fields exist
        ev.setdefault("event_kind", "observation")
        ev.setdefault("summary", "")
        entries.append(ev)
    # Sort newest-first by ts string (ISO, so lexicographic is correct).
    # Coerce to str so legacy entries with numeric (Unix epoch) ts don't crash
    # the comparison — they sort to the end of the list, which is fine.
    entries.sort(key=lambda e: str(e.get("ts", "")), reverse=True)
    return entries


def extract_tier_summary(cap_md: str) -> dict:
    """Parse the last 'Summary tally' markdown table from the capability map.

    Returns a dict with:
      totals: {validated, want_stronger, inconclusive, research_only, untested, closed}
      parse_ok: bool
      raw_table: list[list[str]]  (header + data rows)
    """
    if not cap_md:
        return {"totals": {}, "parse_ok": False, "raw_table": []}

    # Find the last occurrence of "Summary tally" header
    lines = cap_md.split("\n")
    last_tally_idx = -1
    for i, ln in enumerate(lines):
        if "Summary tally" in ln:
            last_tally_idx = i

    if last_tally_idx < 0:
        return {"totals": {}, "parse_ok": False, "raw_table": []}

    # Collect the table starting from last_tally_idx+1
    table_lines: list[str] = []
    for ln in lines[last_tally_idx + 1:]:
        s = ln.strip()
        if s.startswith("|"):
            table_lines.append(s)
        elif table_lines:
            # First non-table line after we started collecting = end of table
            break

    if len(table_lines) < 3:
        return {"totals": {}, "parse_ok": False, "raw_table": []}

    def split_row(row: str) -> list[str]:
        return [c.strip() for c in row.strip("|").split("|")]

    header = split_row(table_lines[0])
    # table_lines[1] is the separator row
    data_rows = [split_row(r) for r in table_lines[2:] if not re.match(r"^\|[-:| ]+\|?$", r)]

    # Map column headers to canonical keys
    # Header example: Section | ✅ Validated | 🟢 Want stronger | 🟡 Inconclusive | 🔬 Research only | ⚪ Untested | ❌ Closed
    col_map: dict[int, str] = {}
    for ci, h in enumerate(header):
        hl = h.lower()
        if "validated" in hl and "want" not in hl:
            col_map[ci] = "validated"
        elif "want" in hl:
            col_map[ci] = "want_stronger"
        elif "inconclusive" in hl:
            col_map[ci] = "inconclusive"
        elif "research" in hl:
            col_map[ci] = "research_only"
        elif "untested" in hl:
            col_map[ci] = "untested"
        elif "closed" in hl:
            col_map[ci] = "closed"

    if not col_map:
        return {"totals": {}, "parse_ok": False, "raw_table": [table_lines]}

    totals: dict[str, int] = {k: 0 for k in col_map.values()}
    for row in data_rows:
        for ci, key in col_map.items():
            if ci < len(row):
                val = row[ci].strip()
                # Accept integers; treat "—" or "-" as 0
                if val in ("—", "-", "", "?"):
                    continue
                try:
                    totals[key] = totals.get(key, 0) + int(val)
                except ValueError:
                    pass

    return {"totals": totals, "parse_ok": True, "raw_table": [split_row(t) for t in table_lines]}


def extract_cap_version_meta(cap_md: str) -> dict:
    """Extract current cap_map version number and key framework-reliability metrics.

    Scans the version-history table (lines like '| v211 | date | ...') for the
    highest version number, and also scans recent narrative blocks for the
    framework reliability and Combined Tier-1 P strings.

    Returns:
      {
        "version": int | None,         # e.g. 211
        "version_date": str,           # e.g. "2026-05-26"
        "framework_reliability": str,  # e.g. "48-62%" or ""
        "tier1_p": str,                # e.g. "50-65%" or ""
        "portfolio_count": str,        # e.g. "14 demonstrated + 7 evidence-strength" or ""
      }
    """
    if not cap_md:
        return {"version": None, "version_date": "", "framework_reliability": "",
                "tier1_p": "", "portfolio_count": ""}

    # Find the highest vNNN version number from three formats:
    #   1. Compact table row: "| v211 | 2026-05-26 | ..."
    #   2. H2 narrative header: "## v211 - (2026-05-26) ..."
    #   3. H2 transition header: "## v289 -> v290 @ ..." (multi-session era;
    #      no date in header -- date sourced from later narrative if needed)
    version: int | None = None
    version_date: str = ""
    _ver_table_re = re.compile(r"^\|\s*v(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})")
    _ver_h2_re = re.compile(r"^##\s+v(\d+)\s+[-–—]+\s+\(?(\d{4}-\d{2}-\d{2})\)?")
    _ver_transition_re = re.compile(r"^##\s+v\d+\s*[-–—>]+\s*v(\d+)\s*@")
    for line in cap_md.splitlines():
        s = line.strip()
        for rx in (_ver_table_re, _ver_h2_re):
            m = rx.match(s)
            if m:
                v = int(m.group(1))
                if version is None or v > version:
                    version = v
                    version_date = m.group(2)
                break
        # Transition headers don't have a date in the header; only the version.
        m_trans = _ver_transition_re.match(s)
        if m_trans:
            v = int(m_trans.group(1))
            if version is None or v > version:
                version = v
                # Keep the prior version_date (from the most recent dated entry)
                # unless this is the very first version we've seen.

    # Extract framework reliability and Tier-1 P from the most recent vNNN narrative
    # block. Scan the last 100 KB of the file (most recent history block) so we catch
    # long v211 narrative sections. Pick the LAST match (most recent update wins).
    framework_reliability: str = ""
    tier1_p: str = ""
    portfolio_count: str = ""

    # Two patterns per metric:
    #   A) "UPGRADED X -> Y" — extract Y (the new value after the arrow)
    #   B) plain "... X%" — extract X
    # Pattern A is checked first; if found, its match is preferred over pattern B.
    _frel_upg_re = re.compile(
        r"framework reliability\s+UPGRADED\s+\d{2,3}[-–—]\d{2,3}\s*[-–—>]+\s*(\d{2,3}[-–—]\d{2,3}%?)",
        re.IGNORECASE,
    )
    _frel_re = re.compile(r"framework reliability\s*[^0-9\n]*?(\d{2,3}[-–—]\d{2,3}%)", re.IGNORECASE)
    _t1p_upg_re = re.compile(
        r"[Cc]ombined\s+Tier-1\s+P\s+\S+\s*[-–—>]+\s*(\d{2,3}[-–—]\d{2,3}%?)",
        re.IGNORECASE,
    )
    _t1p_re = re.compile(r"[Cc]ombined\s+Tier-1\s+P\s*[^0-9\n]*?(\d{2,3}[-–—]\d{2,3}%)", re.IGNORECASE)
    _port_re = re.compile(r"(\d+\s+demonstrated\s*\+\s*\d+\s+evidence-strength\s*rows?)", re.IGNORECASE)

    # Use 100 KB tail — the v211 block is large (~50 KB of narrative).
    tail = cap_md[-100_000:]

    # Framework reliability: prefer the UPGRADED pattern (extracts new value after arrow).
    all_upg = list(_frel_upg_re.finditer(tail))
    if all_upg:
        v = all_upg[-1].group(1)
        framework_reliability = v if v.endswith("%") else v + "%"
    else:
        all_frel = list(_frel_re.finditer(tail))
        if all_frel:
            framework_reliability = all_frel[-1].group(1)

    # Combined Tier-1 P: prefer the upgrade pattern too (e.g. "50-65% ->")
    all_t1p_upg = list(_t1p_upg_re.finditer(tail))
    if all_t1p_upg:
        v = all_t1p_upg[-1].group(1)
        tier1_p = v if v.endswith("%") else v + "%"
    else:
        all_t1p = list(_t1p_re.finditer(tail))
        if all_t1p:
            tier1_p = all_t1p[-1].group(1)

    all_port = list(_port_re.finditer(tail))
    if all_port:
        portfolio_count = all_port[-1].group(1)

    # Last-bump attribution (architecture v1 multi-session):
    # Only the orchestrator writes cap_map, so last_bumped_by is always
    # 'orchestrator'. The interesting field is the trigger context taken from
    # the most-recent version-header narrative. Headers look like:
    #   '## v289 -> v290 @ BATCHED 8-VERDICT T2-T5 + ... MAJOR EVENT (...)'
    # We strip the leading 'vXXX -> vYYY @ ' and keep the rest as the summary.
    last_bumped_by = "orchestrator"
    last_bump_summary = ""
    if version is not None:
        # Find the H2 header for the current top version, in the tail block.
        _hdr_re = re.compile(
            rf"^##\s+v\d+\s*[-–—>]+\s*v{version}\s*@?\s*(.*)$",
            re.MULTILINE,
        )
        m = _hdr_re.search(tail)
        if m:
            last_bump_summary = m.group(1).strip()[:280]
        else:
            # Fallback: try the H2 single-version form
            _hdr_solo_re = re.compile(
                rf"^##\s+v{version}\s*[-–—>:]+\s*(.*)$",
                re.MULTILINE,
            )
            m2 = _hdr_solo_re.search(tail)
            if m2:
                last_bump_summary = m2.group(1).strip()[:280]

    return {
        "version": version,
        "version_date": version_date,
        "framework_reliability": framework_reliability,
        "tier1_p": tier1_p,
        "portfolio_count": portfolio_count,
        "last_bumped_by": last_bumped_by,
        "last_bump_summary": last_bump_summary,
    }


# ---------------------------------------------------------------------------
# Structured capability-row extraction for the redesigned Capability tab.
# ---------------------------------------------------------------------------

# State icons used in the capability map. Order matters for first-match wins
# (longer / more-specific glyphs first when one is a prefix of another).
_CAP_STATE_GLYPHS = [
    ("✅", "validated"),       # ✅
    ("\U0001F7E2", "want_stronger"),  # 🟢
    ("\U0001F7E1", "inconclusive"),   # 🟡
    ("\U0001F52C", "research_only"),  # 🔬
    ("⚪", "untested"),        # ⚪
    ("❌", "closed"),          # ❌
]

# Map the high-level section under which a row lives to a UI "group" the
# dashboard wants to show separately. The cap_map.md has four primary sections
# (numbered 1-4): CAN / CANNOT / UNSURE / KILLER. Anything else (e.g., later
# narrative blocks "Tier-1 board after vN", "What's now under-tested ...") is
# kept under a generic "OTHER" bucket so the parser never raises.
_CAP_SECTION_GROUP = {
    "can": "PORTFOLIO",         # 1. CAN — capabilities with empirical evidence
    "cannot": "CLOSED",         # 2. CANNOT — empirically closed limits
    "unsure": "UNSURE",         # 3. UNSURE — known unknowns
    "killer": "KILLER",         # 4. KILLER — game-changing capabilities
}

# Order in which groups should be rendered in the UI (top to bottom).
_CAP_GROUP_ORDER = ["KILLER", "UNSURE", "PORTFOLIO", "CLOSED", "OTHER"]


def _classify_state(state_cell: str) -> str:
    """Return canonical state key for a state cell. 'unknown' on no match.

    Detection order: explicit glyph -> text keywords. The text fallback
    catches KILLER / UNSURE rows where the "current status" column is
    prose like "CANNOT (we're byte K-gram...)" or "🟡 PARTIAL at v189
    ..." or "UNSURE — multimodal research synthesis exists".
    """
    if not state_cell:
        return "unknown"
    for glyph, key in _CAP_STATE_GLYPHS:
        if glyph in state_cell:
            return key
    # Text-only fallback for KILLER / UNSURE prose states.
    s = state_cell.upper()
    if "CANNOT" in s or "REFUTED" in s or "CLOSED" in s or "DEAD" in s:
        return "closed"
    if "PARTIAL" in s or "INCONCLUSIVE" in s or "MIDDLE" in s:
        return "inconclusive"
    if "VALIDATED" in s or "DEMONSTRATED" in s or "PASSES" in s:
        return "validated"
    if "RESEARCH ONLY" in s or "RESEARCH-ONLY" in s:
        return "research_only"
    if "UNSURE" in s or "UNTESTED" in s or "PROPOSED" in s:
        return "untested"
    return "unknown"


def _identify_group(section_h2: str) -> str:
    """Map a `## N. NAME` H2 text to a group key. 'OTHER' if no canonical fit."""
    s = section_h2.lower()
    for token, group in _CAP_SECTION_GROUP.items():
        if token in s:
            return group
    return "OTHER"


def extract_capability_rows(cap_md: str) -> dict:
    """Parse the v1 cap_map.md table sections into structured rows for the UI.

    The capability map has four canonical sections (## 1. CAN / 2. CANNOT /
    3. UNSURE / 4. KILLER). Each contains sub-sections (### Memory primitives,
    etc.) with markdown tables whose first column is the capability name and
    second column contains a state icon. Later "vN update" prose blocks add
    annotations but do NOT define new portfolio rows -- the v1 table is the
    canonical structure the user reads as "the capability map."

    This parser walks the file top-to-bottom and emits ONE row per table row
    found inside any of the four canonical sections (parser STOPS at the
    first `## vN` history-narrative H2 because those blocks contain narrative
    moves not new portfolio rows).

    Returns:
      {
        "parse_ok": bool,
        "groups": [
          {
            "key": "KILLER",
            "label": "KILLER — game-changing capabilities",
            "subsections": [
              {
                "name": "Tier 1: would define the product",
                "rows": [
                  {"name": "...", "state": "validated"/"want_stronger"/...,
                   "state_glyph": "✅", "raw_state": "✅ Validated",
                   "evidence": "...", "product": "..."},
                  ...
                ],
              },
              ...
            ],
          },
          ...
        ],
        "totals": {validated: N, ...},  # rollup across rows (best-effort)
      }
    """
    if not cap_md:
        return {"parse_ok": False, "groups": [], "totals": {}}

    lines = cap_md.split("\n")
    # By-group containers; we accumulate then sort by _CAP_GROUP_ORDER.
    by_group: dict[str, list[dict]] = {}
    totals: dict[str, int] = {}

    current_group: str | None = None
    current_section_label: str = ""
    current_subsection: str = ""
    section_h2_full: str = ""

    i = 0
    N = len(lines)
    while i < N:
        line = lines[i]
        # Detect canonical H2 like "## 1. CAN" — we only walk the v1 region.
        m_h2 = re.match(r"^##\s+(\d+)\.\s+(.+?)\s*$", line)
        if m_h2:
            section_h2_full = m_h2.group(2).strip()
            current_group = _identify_group(section_h2_full)
            current_section_label = f"{m_h2.group(1)}. {section_h2_full}"
            current_subsection = ""
            i += 1
            continue
        # Stop the parser as soon as we see the first `## vN update` (history
        # narrative) — those blocks are NOT canonical row sources.
        if re.match(r"^##\s+v\d+\b", line) or re.match(r"^#\s+v\d+\b", line):
            break
        # Detect non-numbered H2 (Summary tally, Open questions, etc.) and
        # treat as end of the canonical four-section walk. Anything that
        # starts with `## ` but DOESN'T have a `<digit>. ` prefix is meta.
        m_meta_h2 = re.match(r"^##\s+([A-Z][a-zA-Z].+)$", line)
        if m_meta_h2 and not re.match(r"^##\s+\d+\.", line):
            current_group = None
            current_subsection = ""
            i += 1
            continue
        # H3 subsection (### Memory primitives etc.)
        m_h3 = re.match(r"^###\s+(.+?)\s*$", line)
        if m_h3 and current_group is not None:
            current_subsection = m_h3.group(1).strip()
            i += 1
            continue
        # A table starts when we hit a line beginning with `|` and the NEXT
        # line is a separator row. We tolerate the table being in either CAN
        # or any other section.
        if current_group is not None and line.lstrip().startswith("|") and (
            i + 1 < N and re.match(r"^\s*\|[\s\-:|]+\|?\s*$", lines[i + 1])
        ):
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip the separator and walk rows until the table ends.
            j = i + 2
            while j < N and lines[j].lstrip().startswith("|"):
                row = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                # The first column may be a tally row; skip rows where col-0
                # is "Section" / contains many state glyphs (the Summary tally
                # table has 6 state-icon column headers, not row content).
                row_text = " ".join(row)
                glyph_count = sum(1 for g, _ in _CAP_STATE_GLYPHS if g in row_text)
                # If a row has >=4 distinct state glyphs in it, it's almost
                # certainly the Summary tally header/data row, not a cap row.
                if glyph_count >= 4 and not row[0].startswith("**"):
                    j += 1
                    continue
                if len(row) < 2:
                    j += 1
                    continue
                name = row[0].strip()
                state_cell = row[1].strip()
                if not name or name == "Section":
                    j += 1
                    continue
                state = _classify_state(state_cell)
                if state == "unknown":
                    # Some sections (CANNOT / UNSURE) put the state INTO the
                    # name/comment instead of a dedicated column. Probe the
                    # full row text for a state glyph or keyword.
                    state = _classify_state(row_text)
                # CANNOT section rows are all closed by definition even when
                # the table uses an unmarked first column.
                if state == "unknown" and current_group == "CLOSED":
                    state = "closed"
                # UNSURE rows without explicit state (e.g. "Capability
                # questions we haven't asked") are by definition untested.
                if state == "unknown" and current_group == "UNSURE":
                    state = "untested"
                # KILLER rows without explicit state default to untested
                # ("Tier 3 bonus capabilities (nice if cheap)" entries).
                if state == "unknown" and current_group == "KILLER":
                    state = "untested"
                # Evidence / product columns vary by section. We pull the
                # next two cells if present (most CAN tables: state, evidence,
                # product implication; KILLER tables: current status, why
                # killer; UNSURE: direction, what it might give, test path,
                # estimate). The UI groups them as evidence + meta.
                evidence = row[2] if len(row) > 2 else ""
                product = row[3] if len(row) > 3 else ""
                # Find the state glyph string actually present in the cell.
                state_glyph = ""
                for glyph, key in _CAP_STATE_GLYPHS:
                    if key == state and glyph in (state_cell or row_text):
                        state_glyph = glyph
                        break
                row_dict = {
                    "name": _strip_md_bold(name),
                    "state": state,
                    "state_glyph": state_glyph,
                    "raw_state": state_cell,
                    "evidence": evidence,
                    "product": product,
                    "subsection": current_subsection,
                    "section": current_section_label,
                }
                by_group.setdefault(current_group, []).append(row_dict)
                if state in totals:
                    totals[state] += 1
                else:
                    totals[state] = 1
                j += 1
            i = j
            continue
        i += 1

    # Build the ordered groups payload.
    out_groups: list[dict] = []
    group_labels = {
        "KILLER": "KILLER — game-changing capabilities to chase",
        "UNSURE": "UNSURE — known unknowns",
        "PORTFOLIO": "PORTFOLIO — demonstrated capabilities (CAN)",
        "CLOSED": "CLOSED — empirically refuted limits (CANNOT)",
        "OTHER": "OTHER",
    }
    for group_key in _CAP_GROUP_ORDER:
        rows = by_group.get(group_key)
        if not rows:
            continue
        # Bucket by subsection for collapsibility.
        subsections: dict[str, list[dict]] = {}
        order: list[str] = []
        for r in rows:
            sub = r.get("subsection") or "(general)"
            if sub not in subsections:
                subsections[sub] = []
                order.append(sub)
            subsections[sub].append(r)
        sub_payload = [
            {"name": sub, "rows": subsections[sub]} for sub in order
        ]
        # Per-group state tally for the section header pill.
        gtotals: dict[str, int] = {}
        for r in rows:
            gtotals[r["state"]] = gtotals.get(r["state"], 0) + 1
        out_groups.append({
            "key": group_key,
            "label": group_labels.get(group_key, group_key),
            "subsections": sub_payload,
            "totals": gtotals,
            "row_count": len(rows),
        })

    return {
        "parse_ok": bool(out_groups),
        "groups": out_groups,
        "totals": totals,
    }


def _strip_md_bold(s: str) -> str:
    """Strip leading/trailing markdown bold so capability names render cleanly."""
    if not s:
        return s
    # **name** -> name; keep inner content unchanged.
    m = re.match(r"^\*\*(.+?)\*\*(.*)$", s)
    if m:
        return (m.group(1) + m.group(2)).strip()
    return s


def parse_in_flight(text: str) -> dict:
    """Parse orchestrator_in_flight.json.

    Returns {"dispatches": [...]} with elapsed_s injected per entry.
    Falls back to {"dispatches": []} on any parse error.
    """
    d = safe_json(text)
    if not isinstance(d, dict):
        return {"dispatches": []}
    dispatches = d.get("dispatches")
    if not isinstance(dispatches, list):
        return {"dispatches": []}
    now = datetime.now().astimezone()
    out: list[dict] = []
    for item in dispatches:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        started = item.get("started_at")
        if started:
            try:
                dt = datetime.fromisoformat(started)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                entry["elapsed_s"] = round((now - dt).total_seconds())
            except (ValueError, TypeError):
                entry["elapsed_s"] = None
        else:
            entry["elapsed_s"] = None
        out.append(entry)
    return {"dispatches": out}


def parse_questions_md(text: str) -> list[dict]:
    """Parse orchestrator_questions.md into a list of structured question dicts.

    Expected format::

        ## Open questions

        1. **2026-05-23 12:35** -- Question text. (Context: ...)

        2. **2026-05-23 13:00** -- ...

    Returns list of {"number": int, "posted_at": str, "text": str}.
    If the file is empty or has no numbered questions, returns [].
    """
    if not text or not text.strip():
        return []

    questions: list[dict] = []
    # Each question: a line starting with a number, a dot, optional space, then content.
    # Bold timestamp is optional: **YYYY-MM-DD HH:MM** -- rest
    import re as _re
    item_re = _re.compile(r"^\s*(\d+)\.\s+(.*)", _re.DOTALL)
    ts_re = _re.compile(r"^\*\*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\*\*\s*[-–—]+\s*(.*)", _re.DOTALL)

    # Split into lines and collect numbered items (may span multiple lines).
    lines = text.splitlines()
    current_num: int | None = None
    current_lines: list[str] = []

    def flush():
        if current_num is None or not current_lines:
            return
        full = " ".join(" ".join(current_lines).split())
        m = ts_re.match(full)
        if m:
            questions.append({
                "number": current_num,
                "posted_at": m.group(1),
                "text": m.group(2).strip(),
            })
        else:
            questions.append({
                "number": current_num,
                "posted_at": "",
                "text": full,
            })

    for line in lines:
        stripped = line.strip()
        m = item_re.match(line)
        if m:
            flush()
            current_num = int(m.group(1))
            current_lines = [m.group(2).strip()] if m.group(2).strip() else []
        elif current_num is not None and stripped and not stripped.startswith("#"):
            current_lines.append(stripped)
        elif stripped.startswith("#") or not stripped:
            # Section header or blank line: end of current item
            flush()
            current_num = None
            current_lines = []

    flush()
    return questions


_REGISTRY_EVENT_TYPES = {
    "experiment_planned", "experiment_research",
    "experiment_outcome", "experiment_abandoned",
}

# Normalize queue identifier to its on-disk directory name.
_QUEUE_DIR_MAP = {
    "gpu": "overnight_queue",
    "cpu": "remote_cpu_queue",
    "overnight_queue": "overnight_queue",
    "remote_cpu_queue": "remote_cpu_queue",
}


def _normalize_queue_dir(q: str | None) -> str | None:
    if not q:
        return None
    return _QUEUE_DIR_MAP.get(q.strip().lower(), q)


def build_experiment_registry(
    session_events: list[dict],
    queue_events_by_queue: dict[str, list[dict]],
) -> list[dict]:
    """Build per-experiment registry from session events + queue.log events.

    Status precedence (highest wins): abandoned > verdicted > running > ran > planned.
    The verdict comes from experiment_outcome (the user's ground truth — queue.log's
    exit code alone doesn't tell us if a hypothesis was confirmed or falsified).
    """
    registry: dict[str, dict] = {}

    # Apply session events in chronological order so latest writes win.
    chrono = sorted(session_events, key=lambda e: e.get("ts", ""))
    for ev in chrono:
        et = ev.get("type", "")
        if et not in _REGISTRY_EVENT_TYPES:
            continue
        name = ev.get("name")
        if not name:
            continue
        rec = registry.setdefault(name, {"name": name})

        if et == "experiment_planned":
            if ev.get("purpose"): rec["purpose"] = ev["purpose"]
            if ev.get("queue"):   rec["queue"] = _normalize_queue_dir(ev["queue"])
            if ev.get("tier"):    rec["tier"] = ev["tier"]
            rec.setdefault("planned_at", ev.get("ts"))

        elif et == "experiment_research":
            if ev.get("level"):  rec["research_level"] = ev["level"]
            if ev.get("notes"):  rec["research_notes"] = ev["notes"]
            rec["research_updated_at"] = ev.get("ts")

        elif et == "experiment_outcome":
            if ev.get("verdict"):       rec["verdict"] = ev["verdict"]
            if ev.get("summary"):       rec["outcome_summary"] = ev["summary"]
            if ev.get("metrics_path"):  rec["metrics_path"] = ev["metrics_path"]
            rec["outcome_headline"] = bool(ev.get("headline"))
            rec["outcome_at"] = ev.get("ts")

        elif et == "experiment_abandoned":
            rec["abandoned"] = True
            if ev.get("reason"): rec["abandoned_reason"] = ev["reason"]
            rec["abandoned_at"] = ev.get("ts")

    # Merge in queue.log events (the actual run record). Walk chronologically per queue.
    for queue_label, q_events_desc in queue_events_by_queue.items():
        for ev in reversed(q_events_desc):     # reversed = chronological
            name = ev.get("name")
            if not name:
                continue
            rec = registry.setdefault(name, {"name": name})
            rec.setdefault("queue", _normalize_queue_dir(queue_label))
            etype = ev.get("event")
            if etype == "START":
                rec["started_at"] = ev.get("ts")
                rec["last_log_event"] = "START"
            elif etype in ("DONE", "FAIL"):
                rec["ended_at"] = ev.get("ts")
                rec["wall_s"] = ev.get("wall_s")
                rec["exit_code"] = ev.get("exit_code")
                rec["last_log_event"] = etype
            elif etype == "SKIP":
                rec["last_log_event"] = "SKIP"
                rec.setdefault("ended_at", ev.get("ts"))

    # Threshold beyond which a "running" entry is treated as a zombie.
    _ZOMBIE_HOURS = 6.0

    # Derive final status per record.
    from datetime import datetime as _dt
    _now = _dt.now()
    for rec in registry.values():
        if rec.get("abandoned"):
            rec["status"] = "abandoned"
        elif rec.get("verdict"):
            rec["status"] = "verdicted"
        elif rec.get("last_log_event") == "START":
            # Promote to "zombie" if the START is old enough.
            started = rec.get("started_at")
            zombie = False
            if started:
                try:
                    age_h = (_now - _dt.fromisoformat(started)).total_seconds() / 3600.0
                    if age_h >= _ZOMBIE_HOURS:
                        zombie = True
                        rec["zombie_age_h"] = round(age_h, 1)
                except (ValueError, TypeError):
                    pass
            rec["status"] = "zombie" if zombie else "running"
        elif rec.get("last_log_event") in ("DONE", "FAIL", "SKIP"):
            rec["status"] = "ran"
        else:
            rec["status"] = "planned"
        rec.setdefault("research_level", "none")
        # queue_dir is always the normalized on-disk directory name.
        rec["queue_dir"] = _normalize_queue_dir(rec.get("queue"))

    # Sort by most-recent activity descending.
    def _activity_ts(r: dict) -> str:
        return max(
            r.get("outcome_at") or "",
            r.get("ended_at") or "",
            r.get("started_at") or "",
            r.get("research_updated_at") or "",
            r.get("abandoned_at") or "",
            r.get("planned_at") or "",
        )

    items = list(registry.values())
    items.sort(key=_activity_ts, reverse=True)
    return items


def parse_nvidia_compute_apps(out: str) -> list[dict]:
    """Parse `nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader`."""
    apps: list[dict] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            pid = int(parts[0])
        except ValueError:
            continue
        name = parts[1]
        mem_mib: int | None = None
        mem_str = parts[2]
        # nvidia-smi reports memory as "1234 MiB"
        if mem_str.upper().endswith("MIB"):
            try:
                mem_mib = int(mem_str[:-3].strip())
            except ValueError:
                pass
        apps.append({"pid": pid, "name": name, "gpu_mem_mib": mem_mib})
    return apps


def parse_python_procs(out: str) -> list[dict]:
    """Parse `tasklist /FI "IMAGENAME eq python.exe"` text output, capturing mem usage in KB."""
    procs: list[dict] = []
    for line in out.splitlines():
        line = line.rstrip()
        if not line or line.startswith("=") or line.lstrip().startswith("Image Name"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].lower() == "python.exe":
            try:
                pid = int(parts[1])
            except ValueError:
                continue
            mem_kb: int | None = None
            # Last two tokens are typically "<n,nnn> K"
            if len(parts) >= 2 and parts[-1].upper() == "K":
                try:
                    mem_kb = int(parts[-2].replace(",", ""))
                except ValueError:
                    pass
            procs.append({"pid": pid, "mem_kb": mem_kb, "raw": line})
    return procs


_LOG_RE = re.compile(
    r"^\[(?P<ts>[^\]]+)\]\s+(?P<event>START|DONE|FAIL|SKIP)\s+(?P<name>[^\s:]+)(?P<rest>.*)$"
)
_DONE_RE = re.compile(r"in\s+([\d.]+)s\s+\(exit\s+(-?\d+)\)")


def parse_queue_log(text: str, queue_label: str) -> list[dict]:
    """Parse queue.log into a list of structured events keyed by (queue, name, ts)."""
    events: list[dict] = []
    for line in text.splitlines():
        m = _LOG_RE.match(line.rstrip())
        if not m:
            continue
        d = m.groupdict()
        rest = (d["rest"] or "").strip()
        ev: dict = {
            "ts": d["ts"],
            "queue": queue_label,
            "name": d["name"],
            "event": d["event"],
            "wall_s": None,
            "exit_code": None,
            "extra": rest,
        }
        m2 = _DONE_RE.search(rest)
        if m2:
            try:
                ev["wall_s"] = float(m2.group(1))
                ev["exit_code"] = int(m2.group(2))
            except ValueError:
                pass
        events.append(ev)
    return events


def parse_iso_local(s: str) -> datetime | None:
    """Parse 'YYYY-MM-DDTHH:MM:SS' as workstation local time, return UTC-aware datetime.

    The other session writes naive ISO timestamps; we treat them as workstation local.
    """
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc)


_STATUS_TO_BUCKET = {
    "pending": "queued",
    "queue": "queued",
    "queued": "queued",
    "completed": "completed",
    "done": "completed",
    "running": "running",
    "active": "running",
    "failed": "failed",
    "fail": "failed",
    "error": "failed",
    "killed": "failed",
}


def queue_counts(queue_doc: dict | None) -> dict:
    """Tally experiments by status from a queue.json document.

    Multiple status spellings collapse to canonical buckets — runners in this
    project write either 'pending' or 'queued' for the same intent.
    """
    if not queue_doc:
        return {"total": 0, "completed": 0, "running": 0, "queued": 0, "failed": 0, "other": 0}
    exps = queue_doc.get("experiments", [])
    counts = {"total": len(exps), "completed": 0, "running": 0, "queued": 0, "failed": 0, "other": 0}
    for e in exps:
        raw = (e.get("status") or "").lower().strip()
        bucket = _STATUS_TO_BUCKET.get(raw)
        if bucket:
            counts[bucket] += 1
        else:
            counts["other"] += 1
    return counts


def queue_pending(queue_doc: dict | None) -> list[dict]:
    """Return experiments that are truly upcoming (not running, not finished).

    Skips terminal/non-pickup statuses: completed, failed, killed, running,
    inconclusive, deferred. An entry left as inconclusive or deferred is a
    persisted decision artifact, not work a runner will pick up — the dashboard
    "Up Next" panel must not count it as in-flight or pending.
    """
    if not queue_doc:
        return []
    skip = {"completed", "failed", "killed", "running", "inconclusive", "deferred"}
    out: list[dict] = []
    for idx, e in enumerate(queue_doc.get("experiments", [])):
        s = (e.get("status") or "").lower()
        if s in skip:
            continue
        out.append({
            "name": e.get("name"),
            "status": e.get("status"),
            "purpose": e.get("purpose"),
            "timeout_s": e.get("timeout_s"),
            "position": idx,
        })
    return out


def derive_run_state(
    queue_label: str,
    heartbeat: dict | None,
    queue_doc: dict | None,
    now_utc: datetime,
) -> dict:
    """Combine heartbeat + queue.json into raw 'now running' state for one queue.

    Does NOT compute warning/severity here. That requires pid_alive from a proc
    listing, which the poller has and parsers does not. See compute_severity().
    """
    if heartbeat is None:
        return {"queue": queue_label, "error": "heartbeat unreadable"}

    hb_ts = parse_iso_local(heartbeat.get("ts", ""))
    stale_s: float | None = (now_utc - hb_ts).total_seconds() if hb_ts else None

    status = heartbeat.get("status")
    current = heartbeat.get("current")
    pid = heartbeat.get("pid")

    queue_marks_running = False
    queue_running_name: str | None = None
    started_at_iso: str | None = None
    elapsed_s: float | None = None
    if queue_doc:
        for e in queue_doc.get("experiments", []):
            if (e.get("status") or "").lower() == "running":
                queue_marks_running = True
                queue_running_name = e.get("name")
                started_at_iso = e.get("started_at") or e.get("ts") or e.get("start_at")
                sa = parse_iso_local(started_at_iso) if started_at_iso else None
                if sa is not None:
                    elapsed_s = (now_utc - sa).total_seconds()
                break

    return {
        "queue": queue_label,
        "status": status,
        "current": current,
        "pid": pid,
        "stale_s": round(stale_s, 1) if stale_s is not None else None,
        "started_at": started_at_iso,
        "elapsed_s": round(elapsed_s, 1) if elapsed_s is not None else None,
        "queue_marks_running": queue_marks_running,
        "queue_running_name": queue_running_name,
    }


def compute_severity(
    state: dict,
    pid_alive: bool | None,
    tail_age_s: float | None = None,
) -> tuple[str, str | None]:
    """Return (severity, message). The experiment log's freshness is ground truth.

    When the queue says running, we trust the log file's tail-change time over the
    heartbeat — multiple racing runners (real scenario in this project) can write
    stale 'idle' to heartbeat even while a different runner is actively producing
    log output. The log being written is the definitive signal of life.

    Severity tiers:
      'error' - ZOMBIE (queue says running + PID dead), RUNNER STOPPED, HEARTBEAT UNREADABLE
      'warn'  - log idle > 5min while queue marks running
      'info'  - log idle 1-5min, or heartbeat-mismatch with no log signal yet
      'ok'    - log growing, or nothing notable
    """
    status = state.get("status")
    stale_s = state.get("stale_s")
    queue_marks_running = state.get("queue_marks_running", False)

    # Heartbeat completely unreadable (file missing, SSH transport down, JSON
    # parse failed). derive_run_state returns {queue, error: "heartbeat unreadable"}
    # with no status / stale_s / queue_marks_running set. Without this branch the
    # panel showed as fake-ok / idle, giving the user a silent "unknown" display
    # rather than a visible failure. Analogous to the local-CPU 'exited' fix.
    if state.get("error"):
        msg = str(state["error"])
        return "error", f"HEARTBEAT UNREADABLE - {msg}"
    if status == "stopped":
        return "error", "RUNNER STOPPED"
    if status == "exited":
        # Runner process exited cleanly (idle-timeout or kill). Heartbeat will
        # never refresh again until the runner is relaunched. Flag as dead so
        # the Live tab shows a clear DEAD state instead of fake-healthy "idle".
        return "error", "RUNNER EXITED - relaunch needed"
    if queue_marks_running and pid_alive is False:
        return "error", "ZOMBIE - queue says running but runner PID is dead"
    # Unknown / unexpected heartbeat status — surface as error rather than silent ok.
    # Known/handled states: "running", "idle", "exited", "stopped", None (covered above).
    if status is not None and status not in ("running", "idle", "starting", "active"):
        return "error", f"UNKNOWN HEARTBEAT STATUS: {status!r}"

    # Ground truth: experiment log is being written → alive, regardless of heartbeat.
    # Thresholds are generous because GPU-bound compute phases can legitimately go
    # minutes between log writes; tight thresholds false-positive on normal runs.
    if queue_marks_running and tail_age_s is not None:
        if tail_age_s < 1800:           # < 30min: normal
            return "ok", None
        if tail_age_s < 5400:           # 30-90min: worth noting, not alarming
            return "info", f"log idle {int(tail_age_s/60)}m"
        return "warn", f"log idle {int(tail_age_s/60)}m - may be stuck"

    # No log signal yet (just started, or no current experiment). Fall back to heartbeat.
    if status == "idle" and queue_marks_running:
        return "info", "queue says running, no log signal yet (likely racing runners)"
    if stale_s is not None and stale_s > 600 and pid_alive:
        return "info", f"long run - heartbeat {int(stale_s/60)}m stale, PID alive"
    if stale_s is not None and stale_s > 180 and pid_alive:
        return "info", f"heartbeat {int(stale_s/60)}m stale, PID alive"
    return "ok", None


# ---------------------------------------------------------------------------
# Research meta-map parser
# ---------------------------------------------------------------------------

_NOTES_DIR = Path(r"D:\AI\hd-instrument\notes")


def _latest_research_map_path() -> Path | None:
    """Find the most recently modified research_meta_map file in notes/.

    Returns Path of newest match, or None if no candidates exist. Previously
    this was hardcoded to the 2026-05-23 file, so the tab went stale every
    time a newer meta-map landed. Now glob-by-mtime so the tab tracks the
    latest version automatically.
    """
    candidates = sorted(
        _NOTES_DIR.glob("research_meta_map_and_adjacencies_*.md"),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )
    return candidates[0] if candidates else None

# Yield canonical names
_YIELD_CANONICAL = {
    "load-bearing": "load-bearing",
    "load bearing": "load-bearing",
    "strong": "strong",
    "weak": "weak",
    "none": "none",
    "closed": "none",
    "tbd": "TBD",
    "pending": "TBD",
}


def _normalize_yield(raw: str) -> str:
    """Normalize yield cell text to canonical tier string."""
    s = raw.strip().lower().lstrip("*").rstrip("*").strip()
    # handle "load-bearing (then partial)" etc.
    base = re.split(r"[(\s]", s)[0].strip()
    return _YIELD_CANONICAL.get(base, _YIELD_CANONICAL.get(s, "TBD"))


def _normalize_adopted(raw: str) -> str:
    """Return 'yes', 'partial', or 'no'."""
    s = raw.strip().lower()
    if s in ("no", "no (closed)", "no (closed v93)", "no (orphan)", "no (pending)"):
        return "no"
    if not s or s in ("—", "-"):
        return "no"
    if "partial" in s:
        return "partial"
    # Any non-empty, non-"no" entry is treated as yes
    return "yes"


# ---------------------------------------------------------------------------
# Field tagging
# ---------------------------------------------------------------------------
# Ordered keyword map: each row in the research matrix is tagged with the FIRST
# matching field. Order matters: more specific tags come first.
# Field tag = research lens / mathematical domain we drilled through.
_FIELD_KEYWORDS: list[tuple[str, str]] = [
    # Thermodynamics / fluctuation theorems
    ("thermodynamics", r"\b(crooks|jarzynski|fluctuation theorem|sagawa[- ]ueda|thermal anneal|annealing|erasure thermo|hatano|ness|landauer|two[- ]temperature|fdt|maxwell demon)"),
    # Spin glass / Parisi / RSB
    ("spin-glass", r"\b(parisi|rsb|rs[- ]phase|p\(q\)|at[- ]line|aizenman|rfot|spin[- ]glass|albanese|sk model|replica|order[- ]param)"),
    # AMP / VAMP / message passing
    ("AMP/VAMP", r"\b(amp\b|vamp|spatially[- ]coupled|kudekar|threshold[- ]saturation|approximate message passing|block[- ]vamp|bundle[- ]decompose)"),
    # Conformal / calibration
    ("conformal/calibration", r"\b(conformal|venn[- ]abers|mondrian|tempscale|temp[- ]scale|calibration|\bece\b|polyak[- ]juditsky|iterate averaging|robbins[- ]monro|\bsnap\b)"),
    # Modern Hopfield / dense AM
    ("modern-Hopfield", r"\b(krotov|demircigil|modern[- ]hopfield|modern dense|dense am|exp[- ]capacity|p[- ]body|hopfield)"),
    # Hopf algebra / categorical / topological
    ("algebraic-topo", r"\b(hopf|connes[- ]kreimer|drinfeld|steenrod|topological probe|tomita|takesaki|modular flow|rooted[- ]tree|categorical bp|holographic|ssh/bsc)"),
    # Kerdock / coding / codebook
    ("coding-theory", r"\b(kerdock|rm\(1|reed[- ]muller|codebook|coset|walsh|bent function|\bfht\b|fast hadamard|anti[- ]linear|n=65536)"),
    # Materials / phase / avalanche / glassy dynamics / domain walls / quirky matsci
    ("materials-physics", r"\b(materials char|kovacs|chi_4|chi3|chi4|1/f|avalanche|abbm|critical slow|critical point|phase transform|triple[- ]point|aging|nucleation|facilitat|dislocation|domain wall|ferromagnet|magnon|soliton|wannier|exciton|quirky matsci|fresh angles)"),
    # Semiconductor / drift-diffusion / RTN
    ("semiconductor", r"\b(semiconductor|drift[- ]diffusion|\bdlts\b|\brtn\b|pn[- ]junction)"),
    # Quantum / OAQEC / photonic / repeater
    ("quantum-info", r"\b(oaqec|operator[- ]algebra qec|harlow|quantum repeater|photonic|light[- ]matter)"),
    # Free probability / R-transform
    ("free-probability", r"\b(free probability|r[- ]transform|s[- ]transform|\bbbp\b)"),
    # Bayesian inference / BP / EP / SMC / smoother
    ("inference", r"\b(\bbp\b|belief propagation|bcjr|\bhmm\b|smoother|\bsmc\b|particle filter|whiteley|matrix[- ]product bp|forward[- ]backward|cluster trap|hypothesis[- ]tracking ep|\bep\b smoother|ensemble smoother|sampling rescue)"),
    # Hebbian / learning rules
    ("learning-rules", r"\b(hebb|anti[- ]hebb|tyulmankov|redundancy[- ]max|self[- ]supervised|sparse dict|learning[- ]theory)"),
    # Coherence / Arnold tongue / dynamics / sleep / resonance
    ("dynamics", r"\b(coherence bridge|arnold tongue|mode[- ]lock|sleep consolid|replay|alpha_c|k[- ]resonance)"),
    # Substrate observability / probes / TAP / Fisher / C_ij / eigenvalue
    ("observability", r"\b(observability|tap complex|fisher info|sinova|houdayer|c_ij|eigenvalue extensive|liao 2025|exceptional deficiency)"),
    # Compositional / skill graph / cross-modal / holistic readout
    ("composition", r"\b(compositional|skill[- ]graph|skill composition|cross[- ]modal|cued|holistic readout|source[- ]item dissociat)"),
    # Phase retrieval / signal recovery / provenance
    ("signal-recovery", r"\b(phase retrieval|sign recovery|provenance|order[- ]param 2x)"),
    # Multi-hop / chain / retraction
    ("multi-hop-chain", r"\b(multi[- ]hop|chained cam|retraction|forward[- ]only|backward smoother|absorbing[- ]diffusion|endpoint partition|hubness|\bdpi\b)"),
    # Online learning / OCO
    ("online-learning", r"\b(ddam[- ]oco|online gradient|sublinear regret|online w)"),
    # Meta / strategy / methodology / capabilities
    ("meta-strategy", r"\b(meta gaps|strategy open|methodology|deferred synthesis|capabilit|cap[- ]map|cap 1|cap 2|cap 3|cap 4|r38/r39|r36 mechanism)"),
    # Bets / portfolio-named work (catch-all for project-internal bet labels not otherwise matched)
    ("bet-program", r"\bBet [A-Z]\b|substrate evaluation|evaluation harness|V2 substrate"),
]
_FIELD_KEYWORDS_RE = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in _FIELD_KEYWORDS]


def _tag_field(framework: str) -> str:
    """Return the first matching field tag for a framework string, or 'other'."""
    if not framework:
        return "other"
    for name, rx in _FIELD_KEYWORDS_RE:
        if rx.search(framework):
            return name
    return "other"


def _parse_matrix_table(lines: list[str]) -> list[dict]:
    """Parse the Part 1 pipe-table from the research_meta_map markdown.

    Returns list of dicts with keys: idx, framework, date, p, outcome,
    adopted_raw, adopted, yield_raw, yield_tier, field.
    """
    in_table = False
    rows: list[dict] = []
    table_header_passed = False

    for line in lines:
        stripped = line.strip()
        if not in_table:
            # Detect the header line of the matrix table
            if stripped.startswith("|") and "Framework" in stripped and "Yield" in stripped:
                in_table = True
                table_header_passed = False
                continue
        else:
            if not stripped.startswith("|"):
                # End of table
                break
            # Skip separator rows like |---|---|...
            if re.match(r"^\|[-:| ]+\|?$", stripped):
                table_header_passed = True
                continue
            if not table_header_passed:
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 7:
                continue
            try:
                idx = int(re.sub(r"\D", "", cells[0]))
            except ValueError:
                continue
            framework = cells[1].strip()
            rows.append({
                "idx": idx,
                "framework": framework,
                "field": _tag_field(framework),
                "date": cells[2].strip(),
                "p": cells[3].strip(),
                "outcome": cells[4].strip(),
                "adopted_raw": cells[5].strip(),
                "adopted": _normalize_adopted(cells[5]),
                "yield_raw": cells[6].strip(),
                "yield_tier": _normalize_yield(cells[6]),
            })
    return rows


def _parse_adjacency(lines: list[str]) -> list[dict]:
    """Parse Part 3 adjacency clusters.

    Returns list of {"anchor": str, "anchor_label": str, "neighbors": [
       {"code": str, "name": str, "why": str, "cost": str}
    ]}.
    """
    in_part3 = False
    clusters: list[dict] = []
    current_cluster: dict | None = None
    in_adj_table = False
    adj_header_passed = False

    _anchor_re = re.compile(r"^###\s+([A-Z]\d*)\.\s+(.*)")
    _part3_re = re.compile(r"^##\s+Part 3")
    _part4_re = re.compile(r"^##\s+Part 4")

    for line in lines:
        stripped = line.strip()

        if not in_part3:
            if _part3_re.match(stripped):
                in_part3 = True
            continue

        if _part4_re.match(stripped):
            break

        m = _anchor_re.match(stripped)
        if m:
            current_cluster = {
                "anchor": m.group(1),
                "anchor_label": m.group(2).strip(),
                "neighbors": [],
            }
            clusters.append(current_cluster)
            in_adj_table = False
            adj_header_passed = False
            continue

        if current_cluster is None:
            continue

        if stripped.startswith("|") and "Adjacent un-drilled" in stripped:
            in_adj_table = True
            adj_header_passed = False
            continue

        if in_adj_table:
            if not stripped.startswith("|"):
                in_adj_table = False
                adj_header_passed = False
                continue
            if re.match(r"^\|[-:| ]+\|?$", stripped):
                adj_header_passed = True
                continue
            if not adj_header_passed:
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 3:
                continue
            # Parse "A1. Jarzynski equality (work vs free-energy difference)"
            cell0 = cells[0]
            code_m = re.match(r"^([A-Z]\d+)\.\s+(.*)", cell0)
            if code_m:
                code = code_m.group(1)
                name = code_m.group(2).strip()
            else:
                code = ""
                name = cell0
            current_cluster["neighbors"].append({
                "code": code,
                "name": name,
                "why": cells[1].strip() if len(cells) > 1 else "",
                "cost": cells[2].strip() if len(cells) > 2 else "",
            })

    return clusters


def _parse_top_drills(lines: list[str]) -> list[dict]:
    """Parse Part 4 top drill cards.

    Returns list of {"rank": int, "code": str, "name": str, "adjacency": str,
    "test": str, "runtime": str, "hard_pass": str, "hard_fail": str, "p": str, "wedge": str}.
    """
    in_part4 = False
    drills: list[dict] = []
    current: dict | None = None

    _part4_re = re.compile(r"^##\s+Part 4")
    _drill_re = re.compile(r"^###\s+Drill\s+(\d+)\s+[-–—]+\s+(.*)")

    _field_map = {
        "adjacency": "adjacency",
        "**adjacency**": "adjacency",
        "cheap decisive test": "test",
        "**cheap decisive test**": "test",
        "estimated runtime": "runtime",
        "**estimated runtime**": "runtime",
        "hard pass": "hard_pass",
        "**hard pass**": "hard_pass",
        "hard fail": "hard_fail",
        "**hard fail**": "hard_fail",
        "p (deflated)": "p",
        "**p (deflated)**": "p",
        "substrate-product wedge": "wedge",
        "**substrate-product wedge**": "wedge",
    }

    for line in lines:
        stripped = line.strip()

        if not in_part4:
            if _part4_re.match(stripped):
                in_part4 = True
            continue

        # Stop at honorable mentions / end of file
        if stripped.startswith("### Honorable") or stripped.startswith("---"):
            if current:
                drills.append(current)
                current = None
            if stripped.startswith("---"):
                break
            continue

        m = _drill_re.match(stripped)
        if m:
            if current:
                drills.append(current)
            # Extract code hint from trailing parenthetical e.g. "(H1)" or "(B4 + F5)"
            title = m.group(2).strip()
            code_m = re.search(r"\(([A-Z0-9 +]+)\)\s*$", title)
            code = code_m.group(1).strip() if code_m else ""
            name = re.sub(r"\s*\([A-Z0-9 +]+\)\s*$", "", title).strip()
            current = {
                "rank": int(m.group(1)),
                "code": code,
                "name": name,
                "adjacency": "",
                "test": "",
                "runtime": "",
                "hard_pass": "",
                "hard_fail": "",
                "p": "",
                "wedge": "",
            }
            continue

        if current is None:
            continue

        # Parse field lines like "**Adjacency**: text..."
        field_m = re.match(r"^\*\*([^*]+)\*\*:\s*(.*)", stripped)
        if field_m:
            key_raw = field_m.group(1).strip().lower()
            value = field_m.group(2).strip()
            canonical = _field_map.get(f"**{key_raw}**") or _field_map.get(key_raw)
            if canonical:
                current[canonical] = value

    if current:
        drills.append(current)

    return drills


def _parse_tier_counts(lines: list[str]) -> dict:
    """Parse the yield tier breakdown table below Part 1.

    Returns {"load-bearing": int, "strong": int, "weak": int, "none": int, "TBD": int, "total": int}.
    """
    in_breakdown = False
    counts: dict[str, int] = {
        "load-bearing": 0, "strong": 0, "weak": 0, "none": 0, "TBD": 0, "total": 0
    }

    for line in lines:
        stripped = line.strip()
        if "### Yield tier breakdown" in stripped or "Yield tier breakdown" in stripped:
            in_breakdown = True
            continue
        if in_breakdown:
            if not stripped.startswith("|"):
                if stripped.startswith("#") or stripped.startswith("---"):
                    break
                continue
            if re.match(r"^\|[-:| ]+\|?$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 2:
                continue
            tier_cell = cells[0].strip("*").strip().lower()
            count_m = re.match(r"(\d+)", cells[1])
            if not count_m:
                continue
            count = int(count_m.group(1))
            tier_key = _normalize_yield(tier_cell)
            if tier_key in counts:
                counts[tier_key] = count
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    return counts


def _summarize_fields(matrix: list[dict]) -> list[dict]:
    """Aggregate matrix rows by field tag.

    Returns list of {"field", "count", "tiers": {load-bearing, strong, weak, none, TBD},
    "latest_date", "load_bearing_pct"} sorted by count desc.
    """
    from collections import defaultdict
    by_field: dict[str, dict] = defaultdict(lambda: {
        "count": 0,
        "tiers": {"load-bearing": 0, "strong": 0, "weak": 0, "none": 0, "TBD": 0},
        "latest_date": "",
        "indices": [],
    })
    for row in matrix:
        f = row.get("field") or "other"
        entry = by_field[f]
        entry["count"] += 1
        tier = row.get("yield_tier") or "TBD"
        if tier in entry["tiers"]:
            entry["tiers"][tier] += 1
        date = row.get("date", "")
        # Naive max — dates start with "MM-DD" so string-compare works in same year.
        if date > entry["latest_date"]:
            entry["latest_date"] = date
        entry["indices"].append(row.get("idx"))

    out = []
    for field, e in by_field.items():
        total = e["count"] or 1
        lb_strong = e["tiers"]["load-bearing"] + e["tiers"]["strong"]
        out.append({
            "field": field,
            "count": e["count"],
            "tiers": e["tiers"],
            "latest_date": e["latest_date"],
            "yield_pct": round(100.0 * lb_strong / total, 1),
            "indices": e["indices"],
        })
    out.sort(key=lambda x: (-x["count"], x["field"]))
    return out


def _derive_fields_not_explored(matrix: list[dict], adjacency: list[dict]) -> list[dict]:
    """Find adjacency-neighbor names whose field tag does NOT appear in the matrix.

    Returns list of {"field", "mentions": [{"code", "name", "anchor"}]} for surfacing
    families we've mentioned in adjacency but never drilled.
    """
    explored_fields = {row.get("field") for row in matrix if row.get("field")}
    from collections import defaultdict
    untouched: dict[str, list] = defaultdict(list)
    for cluster in adjacency:
        anchor = cluster.get("anchor", "")
        anchor_label = cluster.get("anchor_label", "")
        for n in cluster.get("neighbors", []):
            name = n.get("name", "")
            field = _tag_field(name)
            if field == "other":
                continue
            if field not in explored_fields:
                untouched[field].append({
                    "code": n.get("code", ""),
                    "name": name,
                    "anchor": f"{anchor}. {anchor_label}",
                    "cost": n.get("cost", ""),
                })

    out = []
    for field, mentions in untouched.items():
        out.append({"field": field, "mentions": mentions, "count": len(mentions)})
    out.sort(key=lambda x: -x["count"])
    return out


def parse_research_map() -> dict:
    """Parse the most recent research_meta_map_and_adjacencies_*.md into structured data.

    Picks the freshest file by mtime (was hardcoded to 2026-05-23 and went stale on
    every newer meta-map). Also enumerates recent research notes so the dashboard's
    research tab covers ALL substantive research output (15_angles_triage,
    5_new_directions, deep drills, audit drills, fifth-mechanism requests, etc.),
    not just the single meta-map.

    Returns {
        "tiers": {"load-bearing": int, ...},
        "matrix": [{"idx", "framework", "field", "date", "p", "outcome", "adopted", "yield_tier", ...}],
        "fields": [{"field", "count", "tiers", "latest_date", "yield_pct"}],
        "fields_not_explored": [{"field", "mentions": [...], "count"}],
        "adjacency": [{"anchor", "anchor_label", "neighbors": [...]}],
        "top_drills": [{"rank", "code", "name", "adjacency", "test", ...}],
        "source_path": str,             # path of meta-map actually parsed
        "recent_notes": [{"path", "title", "mtime_iso", "size"}],
        "parse_ok": bool,
        "error": str | None,
    }.
    """
    src = _latest_research_map_path()
    if src is None:
        return {
            "tiers": {}, "matrix": [], "adjacency": [], "top_drills": [],
            "fields": [], "fields_not_explored": [],
            "source_path": "", "recent_notes": _list_recent_research_notes(),
            "parse_ok": False, "error": "no research_meta_map_and_adjacencies_*.md found",
        }
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as exc:
        return {
            "tiers": {}, "matrix": [], "adjacency": [], "top_drills": [],
            "fields": [], "fields_not_explored": [],
            "source_path": str(src), "recent_notes": _list_recent_research_notes(),
            "parse_ok": False, "error": str(exc),
        }

    lines = text.splitlines()
    matrix = _parse_matrix_table(lines)
    adjacency = _parse_adjacency(lines)
    top_drills = _parse_top_drills(lines)
    tiers = _parse_tier_counts(lines)
    fields = _summarize_fields(matrix)
    fields_not_explored = _derive_fields_not_explored(matrix, adjacency)

    # Fallback: derive tier counts from matrix if table parse got all zeros
    if sum(v for k, v in tiers.items() if k != "total") == 0 and matrix:
        from collections import Counter
        c = Counter(r["yield_tier"] for r in matrix)
        for k in ("load-bearing", "strong", "weak", "none", "TBD"):
            tiers[k] = c.get(k, 0)
        tiers["total"] = sum(v for k, v in tiers.items() if k != "total")

    return {
        "tiers": tiers,
        "matrix": matrix,
        "fields": fields,
        "fields_not_explored": fields_not_explored,
        "adjacency": adjacency,
        "top_drills": top_drills,
        "source_path": str(src),
        "recent_notes": _list_recent_research_notes(),
        "parse_ok": len(matrix) > 0,
        "error": None,
    }


# Filenames that are administrative (not research findings) — excluded from
# recent_notes so the tab focuses on substantive output the user cares about.
_RESEARCH_NOTE_EXCLUDE_PREFIXES = (
    "research_decisions_",       # session journal
    "research_routing_",         # routing notes (not deliverables)
    "research_request_",         # inbound requests (deliverable lands elsewhere)
)


def _extract_title(path: Path, max_chars: int = 200) -> str:
    """Return the first markdown H1 of the file, or the filename stem fallback."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for _ in range(40):           # only scan the head; titles live there
                line = f.readline()
                if not line:
                    break
                s = line.strip()
                if s.startswith("# "):
                    return s[2:].strip()[:max_chars]
    except (OSError, IOError):
        pass
    return path.stem


def _list_recent_research_notes(limit: int = 40) -> list[dict]:
    """List substantive research notes in notes/, freshest first.

    Includes everything matching research_*.md EXCEPT administrative prefixes
    (decisions/routing/request — see _RESEARCH_NOTE_EXCLUDE_PREFIXES). The
    dashboard research tab previously only saw the single hardcoded meta-map;
    this surfaces the 15_angles_triage, 5_new_directions, deep drills, audit
    drills, and other deliverables the user actually wants visibility on.
    """
    try:
        candidates = list(_NOTES_DIR.glob("research_*.md"))
    except OSError:
        return []
    enriched: list[tuple[float, Path]] = []
    for p in candidates:
        name = p.name
        if any(name.startswith(prefix) for prefix in _RESEARCH_NOTE_EXCLUDE_PREFIXES):
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        enriched.append((st.st_mtime, p))
    enriched.sort(key=lambda t: t[0], reverse=True)
    out: list[dict] = []
    for mtime, p in enriched[:limit]:
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        out.append({
            "path": str(p),
            "name": p.name,
            "title": _extract_title(p),
            "mtime_iso": datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="seconds"),
            "size": size,
        })
    return out
