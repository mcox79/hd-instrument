#!/usr/bin/env python
"""PostToolUse hook: enforce END-OF-TURN after a background Agent dispatch.

Installed 2026-08-13 (see notes/delegation_enforcement_2026-08-14.md).

Modes (argv[1]):
  agent  -- log the payload AND inject additionalContext telling the Director
            to end its turn immediately after dispatching a background agent.
  probe  -- log the payload ONLY (no additionalContext, no blocking). Used to
            determine empirically whether hook events fire for SUBAGENT tool
            calls as well as main-thread ones (Task 3 safety question).

Contract: always exit 0. A PostToolUse hook must never break the tool result.
Every failure path is swallowed -- a broken hook here would be an outage.

Disable: delete the "PostToolUse" key from D:/AI/.claude/settings.json
         (backup: D:/AI/.claude/settings.json.bak-20260813-190000).
"""
import json
import os
import sys
import time

LOG = r"D:\AI\hd-instrument\data\hooks\agent_dispatch_hook.log"

MESSAGE = (
    "SYSTEM ENFORCEMENT (PostToolUse/Agent): a background agent has been "
    "dispatched. END YOUR TURN NOW. Do not begin new work. Do not run "
    "adjacent or 'while we wait' commands. Do not read files, check status, "
    "or start a follow-up task. Report the dispatch in ONE line and stop. "
    "The agent will notify you when it completes; the USER is locked out of "
    "the session until you yield."
)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "agent"
    payload = {}
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # Log the FULL payload so main-thread vs subagent distinguishability can be
    # audited off-disk. Best-effort; never fatal.
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "mode": mode,
            "pid": os.getpid(),
            "payload_keys": sorted(payload.keys()),
            "payload": payload,
            "env_claude": {k: v for k, v in os.environ.items()
                           if k.startswith("CLAUDE")},
        }
        with open(LOG, "ab") as fh:
            fh.write((json.dumps(rec, ensure_ascii=True) + "\n").encode("utf-8"))
    except Exception:
        pass

    if mode == "agent":
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": MESSAGE,
            }
        }
        sys.stdout.write(json.dumps(out, ensure_ascii=True))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
