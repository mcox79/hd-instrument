"""Measure orchestrator routing-ratio from the Claude Code session JSONL transcript.

Audit recommendation #3 (notes/orchestrator_process_audit_2026-05-24.md):
the wrapper-routing ratio is ~44% — the structural agent-usage mandate is
not internalized. Without measurement, drift is invisible: each main-thread
tool use looks individually justified, but the cumulative pattern is the
failure mode the user has flagged 5+ times.

This script parses the active session transcript and reports, per assistant
turn (one assistant message between two user messages):
  - sub-agent dispatches (Agent tool calls)
  - main-thread tool uses (Bash / Edit / Read / Write / Glob / Grep / etc.)
  - chat-text length (line count of assistant text outside tool calls)

routing_ratio = dispatches / (dispatches + main_thread_tool_uses)

Target: >= 0.75 (audit). Reads inline read-only ops as "main-thread" but
exempts a small allowlist for routing-discipline-neutral helpers
(see _is_routing_neutral).

Outputs:
  - JSON summary on stdout (or to --out path)
  - Per-turn breakdown when --verbose
  - Writes a rolling snapshot to data/orchestrator_routing_ratio.json so
    the dashboard panel can read it without re-parsing the JSONL.

Usage:
  python tools/orchestrator/routing_ratio.py                    # summary
  python tools/orchestrator/routing_ratio.py --window 20        # last 20 turns
  python tools/orchestrator/routing_ratio.py --verbose          # per-turn
  python tools/orchestrator/routing_ratio.py --session <path>   # specific JSONL
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "data"
SNAPSHOT_PATH = DATA_DIR / "orchestrator_routing_ratio.json"

# Default location of Claude Code session transcripts (Windows).
DEFAULT_SESSION_DIR = Path.home() / ".claude" / "projects" / "d--AI"

# Tools that count as sub-agent dispatches (the "good" axis).
DISPATCH_TOOLS = {"Task", "Agent"}

# Tools that count as main-thread work (the "drift" axis). We treat ANY
# direct tool use as main-thread by default. The set is explicit so we can
# audit / extend it; unknown tools are also counted main-thread (conservative).
MAIN_THREAD_TOOLS = {
    "Bash",
    "PowerShell",
    "Edit",
    "Write",
    "Read",
    "Glob",
    "Grep",
    "NotebookEdit",
    "MultiEdit",
    "WebFetch",
    "WebSearch",
}

# Tools that are routing-neutral — they do not count toward EITHER axis.
# Reading the post-compaction brief, checking status flag files, looking
# at the cap_map: these are reconnaissance, not substantive analysis,
# and forcing the orchestrator to spawn a sub-agent for each would be
# pointless overhead.
ROUTING_NEUTRAL_TOOLS = {
    "ToolSearch",
    "Skill",  # skill invocation is meta-routing, not work
    "ShareOnboardingGuide",
    "Monitor",
    "TaskStop",
    "PushNotification",
    "RemoteTrigger",
    "EnterWorktree",
    "ExitWorktree",
    "CronCreate",
    "CronDelete",
    "CronList",
    "TodoWrite",  # task-tracking meta-op; not substantive analysis; routing-neutral per audit fix 1
}


def _is_routing_neutral_bash(input_str: str) -> bool:
    """Cheap bash invocations that are reconnaissance (status reads), not work.

    Whitelist a few common patterns that the orchestrator runs to OBSERVE
    state without doing analysis: tailing the dashboard JSON, reading queue
    counts, checking pause flag, append_decision_log etc. These don't
    represent "main-thread analysis" — they're harness ops.
    """
    s = (input_str or "").strip().lower()
    if not s:
        return False
    neutral_markers = (
        "queue.json",
        "heartbeat.json",
        "orchestrator_paused.flag",
        "orchestrator_in_flight.json",
        "state_check.py",
        "append_decision_log.py",
        "emit_cadence_signal.py",
        "in_flight.py",
        "git status",
        "git log -",
        "git pull",
    )
    return any(m in s for m in neutral_markers)


def _classify_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Return 'dispatch' | 'main_thread' | 'neutral'."""
    if name in DISPATCH_TOOLS:
        return "dispatch"
    if name in ROUTING_NEUTRAL_TOOLS:
        return "neutral"
    if name == "Bash" and isinstance(tool_input, dict):
        cmd = tool_input.get("command") or ""
        if _is_routing_neutral_bash(cmd):
            return "neutral"
    if name in MAIN_THREAD_TOOLS:
        return "main_thread"
    # Unknown tool name — count conservatively as main_thread so additions
    # don't silently inflate the ratio.
    return "main_thread"


def _extract_assistant_blocks(msg: dict[str, Any]) -> tuple[list[dict], str]:
    """From an assistant message, return (tool_uses, joined_text).

    Claude Code transcript shape:
        {"type":"assistant","message":{"content":[
            {"type":"text","text":"..."},
            {"type":"tool_use","name":"Read","input":{...}},
            ...
        ]}}
    """
    inner = msg.get("message") or {}
    content = inner.get("content")
    tool_uses: list[dict] = []
    text_parts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_use":
                tool_uses.append(block)
            elif btype == "text":
                t = block.get("text") or ""
                if t:
                    text_parts.append(t)
            elif btype == "thinking":
                # Thinking blocks don't count toward chat-overhead;
                # they're not surfaced to user.
                pass
    elif isinstance(content, str):
        text_parts.append(content)
    return tool_uses, "\n".join(text_parts)


def _iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _session_has_dispatches(path: Path, scan_lines: int = 2000) -> bool:
    """Quick scan: return True iff the session contains at least one Agent/Task tool call.

    Reads at most `scan_lines` lines from the tail of the file so large sessions
    are not fully parsed. We scan from the tail because recent turns are what matter
    and dispatches appear throughout (not just at the beginning).

    This is used to distinguish the orchestrator's session from sub-agent sessions:
    sub-agents dispatched BY the orchestrator are recorded in their OWN session files
    (the most-recently-modified file) and have zero dispatches — they only use
    Read/Bash/Grep etc. The orchestrator's session will have Agent tool calls.
    """
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        # Scan the tail to keep cost low on large files.
        for line in lines[-scan_lines:]:
            if '"name":"Agent"' in line or '"name":"Task"' in line:
                return True
    except Exception:
        pass
    return False


def find_latest_session(session_dir: Path = DEFAULT_SESSION_DIR) -> Path | None:
    """Return the most-recently-modified .jsonl in session_dir that contains
    at least one Agent/Task dispatch (i.e. the orchestrator's session).

    Sub-agents spawned by the orchestrator write their own session JSONL files.
    Those files are often MORE recently modified than the orchestrator's session
    (they are being actively written while the orchestrator waits). Naively
    returning the most-recently-modified file therefore picks the sub-agent's
    session — which has zero dispatches — instead of the orchestrator's session,
    causing a false routing_ratio_low alert.

    Fix: among the N most-recently-modified candidates, prefer the first one that
    has at least one dispatch. Fall back to the absolute most-recent file only if
    no candidates have dispatches (e.g., a brand-new session with no dispatches
    yet).
    """
    if not session_dir.is_dir():
        return None
    candidates = [p for p in session_dir.glob("*.jsonl") if p.is_file()]
    if not candidates:
        return None
    # Sort newest-first.
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    # Check up to 5 most-recent sessions for dispatches (cheap quick scan).
    for p in candidates[:5]:
        if _session_has_dispatches(p):
            return p
    # No session with dispatches found — return the absolute most recent file
    # (the orchestrator may just be starting up with no dispatches yet).
    return candidates[0]


def parse_session(path: Path) -> list[dict[str, Any]]:
    """Return a list of per-turn dicts.

    A "turn" = one assistant message. We don't try to group consecutive
    assistant messages — each gets its own row. (In Claude Code, each top-
    level assistant message corresponds to one wake-up; tool results between
    them are inserted as user-role messages with tool_result blocks.)

    Sidechain messages (sub-agent internal transcripts) are SKIPPED — we
    only want the main thread's behavior.
    """
    turns: list[dict[str, Any]] = []
    for rec in _iter_jsonl(path):
        if rec.get("type") != "assistant":
            continue
        # Skip sidechain transcripts — those are sub-agent internals.
        if rec.get("isSidechain"):
            continue
        tool_uses, text = _extract_assistant_blocks(rec)
        dispatches = 0
        main_thread = 0
        neutral = 0
        tool_details: list[dict] = []
        for tu in tool_uses:
            name = tu.get("name") or ""
            tin = tu.get("input") or {}
            klass = _classify_tool(name, tin)
            if klass == "dispatch":
                dispatches += 1
            elif klass == "main_thread":
                main_thread += 1
            else:
                neutral += 1
            tool_details.append({"name": name, "class": klass})
        chat_lines = 0 if not text else len([ln for ln in text.splitlines() if ln.strip()])
        denom = dispatches + main_thread
        ratio = (dispatches / denom) if denom > 0 else None
        turns.append(
            {
                "ts": rec.get("timestamp") or "",
                "uuid": rec.get("uuid") or "",
                "dispatches": dispatches,
                "main_thread_tool_uses": main_thread,
                "neutral_tool_uses": neutral,
                "chat_lines": chat_lines,
                "routing_ratio": ratio,
                "tools": tool_details,
            }
        )
    return turns


def summarize(turns: list[dict[str, Any]], window: int | None) -> dict[str, Any]:
    """Aggregate ratios across the last `window` turns (or all if None)."""
    if not turns:
        return {
            "n_turns": 0,
            "window": window,
            "routing_ratio": None,
            "chat_overhead": None,
            "total_dispatches": 0,
            "total_main_thread": 0,
            "total_neutral": 0,
            "status": "no_data",
        }
    selected = turns[-window:] if window else turns
    total_disp = sum(t["dispatches"] for t in selected)
    total_main = sum(t["main_thread_tool_uses"] for t in selected)
    total_neutral = sum(t["neutral_tool_uses"] for t in selected)
    total_chat = sum(t["chat_lines"] for t in selected)
    denom = total_disp + total_main
    ratio = (total_disp / denom) if denom > 0 else None
    chat_overhead = total_chat / len(selected)
    # Status banding (audit target = 0.75).
    if ratio is None:
        status = "no_tool_activity"
    elif ratio >= 0.75:
        status = "green"
    elif ratio >= 0.55:
        status = "yellow"
    else:
        status = "red"
    # Per-turn ratios for sparkline / panel rendering.
    sparkline = [
        {
            "ts": t["ts"],
            "ratio": t["routing_ratio"],
            "dispatches": t["dispatches"],
            "main_thread": t["main_thread_tool_uses"],
        }
        for t in selected
    ]
    return {
        "n_turns": len(selected),
        "window": window,
        "routing_ratio": round(ratio, 3) if ratio is not None else None,
        "chat_overhead": round(chat_overhead, 1),
        "total_dispatches": total_disp,
        "total_main_thread": total_main,
        "total_neutral": total_neutral,
        "total_chat_lines": total_chat,
        "target_ratio": 0.75,
        "status": status,
        "sparkline": sparkline,
    }


def write_snapshot(summary: dict[str, Any], summaries_by_window: dict[str, Any]) -> None:
    """Persist the summary to data/ for the dashboard panel to consume."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "primary": summary,
        "by_window": summaries_by_window,
        "schema_version": 1,
    }
    tmp = SNAPSHOT_PATH.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, default=str),
        encoding="utf-8",
    )
    os.replace(tmp, SNAPSHOT_PATH)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--session",
        type=str,
        default=None,
        help="Path to a Claude Code session JSONL. Defaults to most-recent in ~/.claude/projects/d--AI/.",
    )
    p.add_argument(
        "--window",
        type=int,
        default=20,
        help="Number of most-recent assistant turns to summarize. Default 20.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-turn breakdown JSON to stdout in addition to summary.",
    )
    p.add_argument(
        "--no-snapshot",
        action="store_true",
        help="Skip writing data/orchestrator_routing_ratio.json.",
    )
    args = p.parse_args()

    if args.session:
        path = Path(args.session)
    else:
        path = find_latest_session() or Path()
    if not path or not path.is_file():
        print(json.dumps({"error": f"no session JSONL found at {path}"}, indent=2))
        return 2

    turns = parse_session(path)
    summary = summarize(turns, args.window)
    summary["session_path"] = str(path)

    # Also compute alternate windows useful for the dashboard.
    by_window: dict[str, Any] = {}
    for w in (10, 20, 50, None):
        wkey = "all" if w is None else str(w)
        s = summarize(turns, w)
        by_window[wkey] = {
            "n_turns": s["n_turns"],
            "routing_ratio": s["routing_ratio"],
            "chat_overhead": s["chat_overhead"],
            "status": s["status"],
            "total_dispatches": s["total_dispatches"],
            "total_main_thread": s["total_main_thread"],
        }

    if not args.no_snapshot:
        write_snapshot(summary, by_window)

    if args.verbose:
        print(json.dumps({"summary": summary, "turns": turns}, indent=2, default=str))
    else:
        print(json.dumps({"summary": summary, "by_window": by_window}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
