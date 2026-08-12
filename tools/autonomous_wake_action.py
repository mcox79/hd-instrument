"""Autonomous wake action — execute the next item from data/autonomous_wake_queue.json.

Pattern: tight execution-driven wake. Each call reads NEXT queue item, executes it,
appends result to data/autonomous_wake_log.jsonl, increments position. Visible audit
trail at every step.

Called by ScheduleWakeup prompts. Single source of truth: queue file + log.

For 'spawn_research' items, the script EMITS the prompt to a routing file and notes
in the log that a Director-action is required (Agent tool needs main-conversation context).
The check_landings type runs the landing notifier + reports new arrivals.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "data" / "autonomous_wake_queue.json"
LOG = REPO / "data" / "autonomous_wake_log.jsonl"


def append_log(entry: dict) -> None:
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def execute_smoke(item: dict) -> dict:
    """Execute smoke cmd. Translates leading '.venv/Scripts/python.exe' to absolute path so
    it works regardless of shell working directory. Other commands run via shell as-is."""
    cmd = item["cmd"]
    venv_py = str(REPO / ".venv" / "Scripts" / "python.exe")
    # Replace common venv prefix with absolute path
    if cmd.startswith(".venv/Scripts/python.exe"):
        cmd_fixed = cmd.replace(".venv/Scripts/python.exe", f'"{venv_py}"', 1)
    else:
        cmd_fixed = cmd
    try:
        result = subprocess.run(cmd_fixed, shell=True, capture_output=True, text=True,
                                 timeout=600, cwd=str(REPO))
        return {
            "kind": "smoke_result",
            "id": item["id"],
            "cmd": cmd[:200],
            "exit": result.returncode,
            "stdout_tail": result.stdout[-2000:] if result.stdout else "",
            "stderr_tail": result.stderr[-500:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"kind": "smoke_timeout", "id": item["id"], "cmd": cmd[:200]}
    except Exception as e:
        return {"kind": "smoke_error", "id": item["id"], "cmd": cmd[:200], "error": f"{type(e).__name__}: {e}"}


def execute_inline_python(item: dict) -> dict:
    code = item["code"]
    try:
        result = subprocess.run(
            [str(REPO / ".venv" / "Scripts" / "python.exe"), "-c", code],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )
        return {
            "kind": "inline_python_result",
            "id": item["id"],
            "exit": result.returncode,
            "stdout_tail": result.stdout[-2000:] if result.stdout else "",
            "stderr_tail": result.stderr[-500:] if result.stderr else "",
        }
    except Exception as e:
        return {"kind": "inline_python_error", "id": item["id"], "error": f"{type(e).__name__}: {e}"}


def execute_check_landings(item: dict) -> dict:
    try:
        result = subprocess.run(
            [str(REPO / ".venv" / "Scripts" / "python.exe"), str(REPO / "tools" / "landing_notifier.py")],
            capture_output=True, text=True, timeout=120, cwd=str(REPO),
        )
        return {
            "kind": "landing_check",
            "id": item["id"],
            "stdout_tail": result.stdout[-1500:] if result.stdout else "(no new arrivals)",
        }
    except Exception as e:
        return {"kind": "landing_check_error", "id": item["id"], "error": str(e)}


def emit_spawn_research_request(item: dict) -> dict:
    """For research-drill spawns, write a routing file (Director picks up on next-wake)."""
    out_path = REPO / "data" / f"autonomous_spawn_request_{item['id']}_{int(time.time())}.json"
    payload = {
        "request_type": "spawn_research_drill",
        "queue_item_id": item["id"],
        "topic": item["topic"],
        "purpose": item.get("purpose", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "Director should read this file on next wake + spawn the hdi_research drill (Agent tool requires main-conversation context).",
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "kind": "spawn_research_request_emitted",
        "id": item["id"],
        "request_file": str(out_path),
        "topic": item["topic"][:200],
    }


def main():
    if not QUEUE.exists():
        append_log({"kind": "no_queue", "msg": f"queue file missing: {QUEUE}"})
        return
    state = json.loads(QUEUE.read_text(encoding="utf-8"))
    pos = state.get("queue_position", 0)
    items = state.get("items", [])
    if pos >= len(items):
        # Queue exhausted: default to check_landings forever (overnight resilience)
        append_log({"kind": "queue_exhausted_default_to_landings", "position": pos, "total_items": len(items)})
        result = execute_check_landings({"id": pos})
        append_log(result)
        return
    item = items[pos]
    append_log({"kind": "wake_start", "position": pos, "item_id": item["id"], "type": item["type"]})

    handlers = {
        "smoke": execute_smoke,
        "inline_python": execute_inline_python,
        "check_landings": execute_check_landings,
        "spawn_research": emit_spawn_research_request,
    }
    handler = handlers.get(item["type"])
    if handler is None:
        result = {"kind": "unknown_type", "id": item["id"], "type": item["type"]}
    else:
        result = handler(item)

    append_log(result)
    # Advance position
    state["queue_position"] = pos + 1
    QUEUE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    append_log({"kind": "wake_done", "position_after": pos + 1, "items_remaining": len(items) - (pos + 1)})


if __name__ == "__main__":
    main()
