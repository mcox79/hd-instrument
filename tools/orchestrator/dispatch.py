"""File-system event detector for the hd-instrument orchestrator.

Polls the repo for state changes and emits one EVENT line per change to stdout.
Each line becomes a Monitor notification that wakes the orchestrator session.

Event line format:
    EVENT <kind> <payload-json>

Kinds:
- ready          dispatch startup
- verdict        new entry in data/local_dashboard_snapshot.json recent_verdicts[],
                 OR new file in data/event_outcomes/ (Phase 2 direct-write)
- routing        new notes/<sender>_request_to_<recipient>_*.md or
                 new notes/<sender>_to_<recipient>_*.md (where recipient != queue)
- queue_add      new notes/<sender>_to_queue_*.md with parsed queue entry(ies)
- queue_change   gpu.queue_pending_count changed
- stale_runner   runner heartbeat older than threshold while status=running
- user_answer    user submitted an answer to an open question via the dashboard
                 (new line in data/orchestrator_answers.jsonl)
- stopped        dispatch shutting down
- error          recoverable error
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DASHBOARD = REPO / "data" / "local_dashboard_snapshot.json"
EVENT_OUTCOMES_DIR = REPO / "data" / "event_outcomes"
NOTES_DIR = REPO / "notes"
ANSWERS_PATH = REPO / "data" / "orchestrator_answers.jsonl"
SOURCE_FILE = Path(__file__).resolve()

POLL_INTERVAL_S = 2.0
STALE_RUNNER_MINUTES = 5

# Version stamp — bump when dispatch.py behavior changes; surfaced in `ready`
# event so stale running processes can be diagnosed quickly.
DISPATCH_VERSION = "2026-05-23.2-table-fallback"

CADENCE_SIGNAL_PATH = REPO / "data" / "orchestrator_cadence_signal.jsonl"

KNOWN_ROLES = ("queue_health", "exp_dev", "strategy", "research", "visibility", "product", "queue", "meta")
_ROLES_ALT = "|".join(re.escape(r) for r in KNOWN_ROLES)
ROUTING_RE = re.compile(rf"^(?P<sender>{_ROLES_ALT})(?:_request)?_to_(?P<recipient>{_ROLES_ALT})_.*\.md$")
QUEUE_ENTRY_RE = re.compile(
    r"(?:queue=(?P<queue>\S+)\s+)?name=(?P<name>\S+)\s+script=(?P<script>\S+)\s+prereg=(?P<prereg>\S+)\s+timeout=(?P<timeout>\d+)"
)
# Also detect a header-style target queue line: "**Target queue**: local_cpu_queue"
TARGET_QUEUE_HEADER_RE = re.compile(r"\*\*Target queue\*\*:\s*(?P<queue>\w+)", re.MULTILINE)

# Multi-entry markdown table schema used by exp_dev when shipping batches.
# Expected header columns (order-flexible): queue | name | script | prereg | timeout(s)
# Recognize any markdown table row (starts/ends with |) and parse columns by header.
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
# A header separator row in a GFM table: |---|---|---|
_TABLE_SEP_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def emit(kind: str, payload: dict[str, Any]) -> None:
    print(
        f"EVENT {kind} {json.dumps(payload, separators=(',', ':'), default=str)}",
        flush=True,
    )


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def minutes_since(iso: str | None) -> float | None:
    """Dashboard timestamps are local time without tz info; compare naive-to-naive."""
    if not iso:
        return None
    try:
        ts = datetime.fromisoformat(iso.replace("Z", ""))
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        return (datetime.now() - ts).total_seconds() / 60.0
    except Exception:
        return None


def _parse_table_entries(text: str, doc_queue: str) -> list[dict[str, Any]]:
    """Parse multi-entry markdown tables. Looks for a header row containing the
    required columns (queue, name, script, prereg, timeout) followed by a
    separator row, then collects subsequent data rows until the table ends.

    Returns [] if no valid table with required columns is found.
    """
    lines = text.splitlines()
    entries: list[dict[str, Any]] = []
    required = {"name", "script", "prereg"}
    timeout_aliases = {"timeout", "timeout(s)", "timeout_s"}

    i = 0
    while i < len(lines):
        row_m = _TABLE_ROW_RE.match(lines[i])
        if not row_m:
            i += 1
            continue
        # Candidate header row; require next non-empty line to be a separator
        if i + 1 >= len(lines) or not _TABLE_SEP_RE.match(lines[i + 1]):
            i += 1
            continue
        # Parse header column names (lowercased, stripped)
        header_cols = [c.strip().lower() for c in row_m.group(1).split("|")]
        # Drop empty leading/trailing cells from outer-pipe artifacts
        # (split on "|" inside the captured group already handles inner cells)
        if not required.issubset(set(header_cols)):
            i += 1
            continue
        # Build column index map; pick timeout column under any alias
        col_idx = {name: idx for idx, name in enumerate(header_cols)}
        timeout_idx = None
        for alias in timeout_aliases:
            if alias in col_idx:
                timeout_idx = col_idx[alias]
                break
        if timeout_idx is None:
            i += 1
            continue
        # Now consume data rows until table ends
        j = i + 2
        while j < len(lines):
            data_m = _TABLE_ROW_RE.match(lines[j])
            if not data_m or _TABLE_SEP_RE.match(lines[j]):
                break
            cells = [c.strip() for c in data_m.group(1).split("|")]
            if len(cells) < len(header_cols):
                j += 1
                continue
            try:
                name = cells[col_idx["name"]]
                script = cells[col_idx["script"]]
                prereg = cells[col_idx["prereg"]]
                timeout_raw = cells[timeout_idx]
                queue = cells[col_idx["queue"]] if "queue" in col_idx else doc_queue
                # Strip leading/trailing whitespace and accept bare ints
                timeout_val = int(timeout_raw)
            except (KeyError, ValueError, IndexError):
                j += 1
                continue
            # Skip empty / placeholder rows
            if not name or not script or not prereg or name.startswith("-"):
                j += 1
                continue
            entries.append(
                {
                    "queue": queue or doc_queue,
                    "name": name,
                    "script": script,
                    "prereg": prereg,
                    "timeout": timeout_val,
                }
            )
            j += 1
        i = j
    return entries


def parse_queue_entries(text: str) -> list[dict[str, Any]]:
    """Extract name=/script=/prereg=/timeout= entries from a queue note.

    Supports two schemas:
    1. Inline `key=value` blocks (single or multiple): one entry per line/block
       with `name=... script=... prereg=... timeout=...` and optional `queue=`.
    2. Markdown table with header row containing columns: queue | name | script
       | prereg | timeout(s) — one entry per data row.

    Also reads an optional document-level '**Target queue**: <name>' header.
    Default queue when absent: overnight_queue.
    """
    # Document-level header queue (applies to all entries that lack an inline queue=)
    header_m = TARGET_QUEUE_HEADER_RE.search(text)
    doc_queue = header_m.group("queue") if header_m else "overnight_queue"

    entries: list[dict[str, Any]] = []
    for m in QUEUE_ENTRY_RE.finditer(text):
        queue = m.group("queue") or doc_queue
        entries.append(
            {
                "queue": queue,
                "name": m.group("name"),
                "script": m.group("script"),
                "prereg": m.group("prereg"),
                "timeout": int(m.group("timeout")),
            }
        )

    # If the inline-form parser found nothing, try the markdown-table schema.
    # (Don't try both: inline-form notes can contain unrelated tables that would
    # produce spurious duplicates. Tables are the fallback when inline yields 0.)
    if not entries:
        entries = _parse_table_entries(text, doc_queue)

    return entries


def initial_seen_routings() -> set[str]:
    return {p.name for p in NOTES_DIR.glob("*.md") if ROUTING_RE.match(p.name)}


def _read_answers_lines() -> list[str]:
    """Read raw non-empty lines of the answers file. Returns [] if missing."""
    if not ANSWERS_PATH.exists():
        return []
    try:
        text = ANSWERS_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    return [ln for ln in text.splitlines() if ln.strip()]


def _read_cadence_lines() -> list[str]:
    """Return all non-empty lines in orchestrator_cadence_signal.jsonl, or []."""
    if not CADENCE_SIGNAL_PATH.exists():
        return []
    try:
        text = CADENCE_SIGNAL_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    return [ln for ln in text.splitlines() if ln.strip()]


def main() -> None:
    seen_verdicts: set[tuple[str, float]] = set()
    seen_outcomes: set[str] = set()
    seen_routings: set[str] = initial_seen_routings()
    last_pending: int | None = None
    last_stale_emit: dict[str, float] = {}

    # Snapshot current cadence-signal line count so we only emit events for NEW
    # signals written after dispatch started, not historical ones.
    seen_cadence_count = len(_read_cadence_lines())

    if DASHBOARD.exists():
        d = load_json(DASHBOARD)
        if d:
            for v in d.get("recent_verdicts", []):
                seen_verdicts.add((v.get("name", ""), v.get("mtime", 0.0)))
            last_pending = d.get("gpu", {}).get("queue_pending_count")

    if EVENT_OUTCOMES_DIR.exists():
        seen_outcomes = {p.name for p in EVENT_OUTCOMES_DIR.glob("*.json")}
    else:
        EVENT_OUTCOMES_DIR.mkdir(parents=True, exist_ok=True)

    # Snapshot the answers file's current length so we only emit user_answer
    # events for NEW answers, not historical ones from before dispatch started.
    seen_answers_count = len(_read_answers_lines())

    # Informational: capture source mtime once for the `ready` event payload.
    # NOTE: do NOT use this for self-exit-on-change — Monitor does not restart
    # the task, so exiting on mtime change registered as a failed task.
    try:
        source_mtime_at_start = SOURCE_FILE.stat().st_mtime
    except Exception:
        source_mtime_at_start = 0.0

    emit(
        "ready",
        {
            "watching": str(REPO),
            "poll_s": POLL_INTERVAL_S,
            "dispatch_version": DISPATCH_VERSION,
            "source_mtime": source_mtime_at_start,
        },
    )

    while True:
        try:
            if DASHBOARD.exists():
                d = load_json(DASHBOARD)
                if d:
                    verdicts = d.get("recent_verdicts") or []
                    for v in verdicts:
                        if not isinstance(v, dict):
                            continue
                        key = (v.get("name", ""), v.get("mtime", 0.0))
                        if key not in seen_verdicts:
                            seen_verdicts.add(key)
                            emit(
                                "verdict",
                                {
                                    "name": v.get("name"),
                                    "verdict": v.get("verdict"),
                                    "verdict_msg": v.get("verdict_msg"),
                                    "elapsed_s": v.get("elapsed_s"),
                                    "mtime_iso": v.get("mtime_iso"),
                                },
                            )

                    gpu = d.get("gpu") or {}
                    pending = gpu.get("queue_pending_count")
                    if pending != last_pending:
                        emit("queue_change", {"pending": pending, "previous": last_pending})
                        last_pending = pending

                    for runner in ("gpu", "cpu"):
                        runner_d = d.get(runner) or {}
                        hb = runner_d.get("heartbeat") or {}
                        mins = minutes_since(hb.get("ts"))
                        if mins is not None and mins > STALE_RUNNER_MINUTES and hb.get("status") == "running":
                            last = last_stale_emit.get(runner, 0.0)
                            if time.time() - last > 300:
                                emit("stale_runner", {"runner_id": runner, "minutes_since_beat": round(mins, 1)})
                                last_stale_emit[runner] = time.time()

            if EVENT_OUTCOMES_DIR.exists():
                for p in EVENT_OUTCOMES_DIR.glob("*.json"):
                    if p.name not in seen_outcomes:
                        seen_outcomes.add(p.name)
                        content = load_json(p) or {}
                        emit(
                            "verdict",
                            {
                                "source": "event_outcome_file",
                                "file": p.name,
                                "name": content.get("name"),
                                "verdict": content.get("verdict"),
                                "verdict_msg": content.get("verdict_msg"),
                            },
                        )

            for p in NOTES_DIR.glob("*.md"):
                if p.name in seen_routings:
                    continue
                m = ROUTING_RE.match(p.name)
                if not m:
                    continue
                seen_routings.add(p.name)
                sender = m.group("sender")
                recipient = m.group("recipient")
                if recipient == "queue":
                    try:
                        raw_text = p.read_text(encoding="utf-8", errors="replace")
                        entries = parse_queue_entries(raw_text)
                    except Exception as e:
                        emit("error", {"message": f"parse queue note {p.name}: {e}"})
                        continue
                    if not entries:
                        # Distinguish two cases:
                        # (a) Note is an informational shipment-record (no
                        #     parseable schema, no queue= tokens) — emit
                        #     `shipment_record` rather than a parse error.
                        # (b) Note tried to use a schema but malformed — keep
                        #     `parse_error` with raw preview so the orchestrator
                        #     can diagnose.
                        has_inline = "queue=" in raw_text or "name=" in raw_text
                        has_table = any(
                            _TABLE_ROW_RE.match(ln) for ln in raw_text.splitlines()
                        )
                        preview = raw_text[:500]
                        if not has_inline and not has_table:
                            emit(
                                "shipment_record",
                                {
                                    "file": p.name,
                                    "from": sender,
                                    "note": "no parseable schema; treating as informational",
                                },
                            )
                        else:
                            emit(
                                "queue_add",
                                {
                                    "file": p.name,
                                    "from": sender,
                                    "parse_error": "no entries found in note",
                                    "raw_preview": preview,
                                },
                            )
                    else:
                        for entry in entries:
                            emit("queue_add", {"file": p.name, "from": sender, **entry})
                else:
                    emit("routing", {"file": p.name, "from": sender, "to": recipient})

            # user_answer: new line(s) appended to data/orchestrator_answers.jsonl
            # by the dashboard /api/answer_question endpoint.
            answer_lines = _read_answers_lines()
            if len(answer_lines) > seen_answers_count:
                for ln in answer_lines[seen_answers_count:]:
                    try:
                        d = json.loads(ln)
                    except Exception:
                        # Skip malformed lines but advance the counter so we don't loop.
                        continue
                    if not isinstance(d, dict):
                        continue
                    emit(
                        "user_answer",
                        {
                            "question_number": d.get("question_number"),
                            "answer": d.get("answer"),
                            "ts": d.get("ts"),
                        },
                    )
                seen_answers_count = len(answer_lines)

            # cadence_signal: new line(s) in data/orchestrator_cadence_signal.jsonl
            # written by emit_cadence_signal.py via Windows Task Scheduler tasks.
            cadence_lines = _read_cadence_lines()
            if len(cadence_lines) > seen_cadence_count:
                for ln in cadence_lines[seen_cadence_count:]:
                    try:
                        obj = json.loads(ln)
                    except Exception:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    emit(
                        "cadence_signal",
                        {
                            "kind": obj.get("signal"),
                            "ts": obj.get("ts"),
                        },
                    )
                seen_cadence_count = len(cadence_lines)

            time.sleep(POLL_INTERVAL_S)
        except KeyboardInterrupt:
            emit("stopped", {})
            return
        except Exception as e:
            emit("error", {"message": str(e)})
            time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
