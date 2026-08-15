#!/usr/bin/env python
"""PostToolUse hook: enforce END-OF-TURN after a background Agent dispatch, AND count
main-thread Agent dispatches per turn (turn-boundary state for the single-dispatch-turn
detector -- see data/hooks/staging/stop_hook.py's _single_dispatch_turn_gate, which reads
the counter this hook writes).

Installed 2026-08-13 (see notes/delegation_enforcement_2026-08-14.md). Turn-counter added
2026-08-15 (owner directive on parallel-dispatch enforcement) -- PostToolUse/Agent is the
only event that fires exactly once per Agent tool_use, main-thread or subagent, and its
payload carries agent_type (null for main-thread, per notes/delegation_enforcement_2026-08-14.md
sec 3's empirical proof), which is exactly the signal needed to count main-thread dispatches
without also counting a dispatched agent's OWN recursive Agent calls (which it should not have
anyway -- see the no-spawn rule -- but the filter is correct defense in depth regardless).

Modes (argv[1]):
  agent  -- log the payload, increment the per-session turn counter (main-thread dispatches
            only), AND inject additionalContext telling the Director to end its turn
            immediately after dispatching a background agent.
  probe  -- log the payload ONLY (no additionalContext, no counter, no blocking). Used to
            determine empirically whether hook events fire for SUBAGENT tool calls as well
            as main-thread ones (Task 3 safety question, 2026-08-13).

Contract: always exit 0. A PostToolUse hook must never break the tool result.
Every failure path is swallowed -- a broken hook here would be an outage.

Disable: delete the "PostToolUse" key from D:/AI/.claude/settings.json
         (backup: D:/AI/.claude/settings.json.bak-20260813-190000).
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

LOG = r"D:\AI\hd-instrument\data\hooks\agent_dispatch_hook.log"

# Repo root for turn-counter state -- this script lives at <repo>/tools/, one level up.
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _derive_session_from_transcript(transcript_path: str) -> str:
    """MUST match data/hooks/staging/stop_hook.py's function of the same name byte-for-byte --
    this is the only way the two hooks (independent processes, no shared module) agree on a
    session key. Both receive the identical transcript_path from the harness per session, so
    the same hash always derives the same key in both places."""
    h = hashlib.sha256(transcript_path.encode('utf-8')).hexdigest()[:10]
    return f'auto_{h}'


def _resolve_session_key(payload: dict) -> str:
    """Same priority order as stop_hook.py's session resolution: CLAUDE_SESSION_NAME env var
    first (per-launcher, human-readable, set for both hooks alike since they are children of
    the same session process), else derive from transcript_path. No positional-arg fallback
    here (this hook is always invoked with mode as argv[1], never a session name)."""
    session = os.environ.get('CLAUDE_SESSION_NAME', '').strip()
    if session:
        return session
    transcript_path = str(payload.get('transcript_path', '')).strip()
    if transcript_path:
        return _derive_session_from_transcript(transcript_path)
    # Last-resort fallback unique to this hook (stop_hook.py never sees this case since it
    # always has either the env var or a transcript_path) -- better than silently not counting.
    sid = str(payload.get('session_id', '')).strip()
    return f'sid_{sid}' if sid else 'unknown'


def _bump_turn_counter(payload: dict, repo_root: Path = None) -> None:
    """Increment the per-session main-thread-Agent-dispatch counter. Best-effort, swallows
    all errors (never break the tool result). Only counts main-thread dispatches: a non-null
    agent_type means the Agent call came from INSIDE a subagent's own sidechain, not the
    Director's main thread, and must not count toward the single-dispatch-turn signal.
    repo_root is overridable for self-test; production callers always use the default."""
    root = repo_root if repo_root is not None else _REPO_ROOT
    try:
        agent_type = payload.get('agent_type')
        if agent_type:  # non-null/non-empty -- a subagent dispatched this, not main thread
            return
        session = _resolve_session_key(payload)
        state_dir = root / 'data' / 'hook_state'
        state_dir.mkdir(parents=True, exist_ok=True)
        counter_file = state_dir / f'agent_dispatch_turn_count_{session}.txt'
        try:
            count = int(counter_file.read_text().strip()) if counter_file.exists() else 0
        except (ValueError, OSError):
            count = 0
        counter_file.write_text(str(count + 1))
    except Exception:
        pass


def _self_test() -> int:
    """Prove: (1) main-thread dispatches (agent_type null) increment the counter; (2)
    subagent-originated dispatches (agent_type set) do NOT; (3) CLAUDE_SESSION_NAME takes
    priority over transcript_path when both are present; (4) the transcript_path hash
    fallback is deterministic (same path -> same key every call), matching
    data/hooks/staging/stop_hook.py's derivation so the two hooks agree. Runs entirely
    against a tempfile repo root -- never touches the real data/hook_state/."""
    import tempfile
    ok = True
    root = Path(tempfile.mkdtemp(prefix="agent_dispatch_hook_selftest_"))

    # 1. main-thread dispatch (agent_type None) increments the counter 0 -> 1 -> 2
    os.environ['CLAUDE_SESSION_NAME'] = 'selftest_session_A'
    try:
        _bump_turn_counter({'agent_type': None}, repo_root=root)
        _bump_turn_counter({'agent_type': None}, repo_root=root)
        cf = root / 'data' / 'hook_state' / 'agent_dispatch_turn_count_selftest_session_A.txt'
        val = int(cf.read_text().strip()) if cf.exists() else -1
        if val == 2:
            print("[self-test] PASS main-thread dispatches increment the counter (0->1->2)")
        else:
            print(f"[self-test] FAIL expected counter=2, got {val}", file=sys.stderr)
            ok = False
    finally:
        pass

    # 2. subagent-originated dispatch (agent_type set) does NOT increment
    _bump_turn_counter({'agent_type': 'hdi_testbed'}, repo_root=root)
    val2 = int(cf.read_text().strip())
    if val2 == 2:
        print("[self-test] PASS subagent-originated Agent call (agent_type set) does not increment")
    else:
        print(f"[self-test] FAIL subagent call changed the counter to {val2}", file=sys.stderr)
        ok = False

    # 3. CLAUDE_SESSION_NAME takes priority over transcript_path
    key = _resolve_session_key({'transcript_path': r'C:\some\other\path.jsonl'})
    if key == 'selftest_session_A':
        print("[self-test] PASS CLAUDE_SESSION_NAME env var takes priority over transcript_path")
    else:
        print(f"[self-test] FAIL expected env-var session, got {key!r}", file=sys.stderr)
        ok = False

    # 4. transcript_path hash fallback is deterministic and matches stop_hook.py's algorithm
    del os.environ['CLAUDE_SESSION_NAME']
    tp = r'C:\Users\marsh\.claude\projects\D--AI\deadbeef.jsonl'
    k1 = _resolve_session_key({'transcript_path': tp})
    k2 = _resolve_session_key({'transcript_path': tp})
    expected = 'auto_' + hashlib.sha256(tp.encode('utf-8')).hexdigest()[:10]
    if k1 == k2 == expected:
        print(f"[self-test] PASS transcript_path hash fallback is deterministic ({k1})")
    else:
        print(f"[self-test] FAIL non-deterministic or wrong hash: {k1!r} vs {k2!r} vs {expected!r}",
              file=sys.stderr)
        ok = False
    os.environ['CLAUDE_SESSION_NAME'] = 'selftest_session_A'  # restore for any later checks

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {root}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

MESSAGE = (
    "SYSTEM ENFORCEMENT (PostToolUse/Agent): a background agent has been "
    "dispatched. END YOUR TURN NOW. Do not begin new work. Do not run "
    "adjacent or 'while we wait' commands. Do not read files, check status, "
    "or start a follow-up task. Report the dispatch in ONE line and stop. "
    "The agent will notify you when it completes; the USER is locked out of "
    "the session until you yield."
)


def main():
    # --self-test: maintenance entrypoint, not a hook firing -- exit before any stdin read.
    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        return _self_test()

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
        _bump_turn_counter(payload)
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
