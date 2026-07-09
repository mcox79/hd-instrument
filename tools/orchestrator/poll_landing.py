#!/usr/bin/env python3
"""Robust landing-detection poller -- replaces the fragile `ssh type queue.json | grep`.

Root cause it fixes (2026-07-08/09 incident: bxa1qe5l7 timed out; b526tzfrg never
emitted a landing event despite the run completing):
    The old SSH-poll landing monitors decided "landed / not-landed" by matching a
    substring against the raw stdout of
        ssh marsh@home "type queue.json"   (or Get-Content ... | Select-String)
    SSH banner / MOTD lines, CRLF injection (no -T pty), and OEM-codepage mojibake
    intermittently blanked or corrupted that stdout, so the terminal-state substring
    never matched. A blanked match was (wrongly) read as "not terminal" -> the
    monitor either timed out (bxa1qe5l7) or silently missed the landing (b526tzfrg).
    Fleet visibility degraded: the Director could not confirm what was running while a
    FULL was actually landing (USER saw the empty dash + idle runners).

    Every REAL landing that session was caught by the DIRECT path:
        scp_recover_landing.py  (byte transfer, rc-checked -- no stdout parsing)
      + verify_landing.py       (reads local metrics.json off disk -- no SSH at all)
    This tool wraps that exact 100%-reliable path in a poll loop, and hardens the
    optional cheap pre-check so SSH stdout noise can NEVER be mistaken for
    "not landed" -- corrupted/blank output classifies as UNKNOWN (keep waiting /
    escalate to the authoritative recover), never as absence.

Two-layer detection (no `grep` on noisy stdout anywhere):
    1. CHEAP PRE-CHECK (optional, --queue): a base64-sentinel-framed read of the
       remote queue.json. The payload is wrapped between @@HDIB64_BEGIN@@ /
       @@HDIB64_END@@ markers and base64-encoded remote-side, so banner lines,
       CRLF, and codepage bytes OUTSIDE the sentinels are discarded, and the
       payload INSIDE is pure [A-Za-z0-9+/=] (immune to codepage). ssh runs with
       -T (no pty -> no CR injection) and -o LogLevel=ERROR (suppress banner).
       If the sentinels are missing / rc!=0 / base64 fails -> status = UNKNOWN,
       which triggers the authoritative recover rather than a false "not landed".
    2. AUTHORITATIVE CONFIRM: on a terminal-or-UNKNOWN pre-check, run
       scp_recover_landing.py --verify-after <anchor>. rc==0 means metrics.json
       was recovered AND verify_landing.py confirmed run_mode=full + terminal
       verdict. That -- not any stdout substring -- is the landing signal.

    On confirm, landing_notifier.scan() is invoked so recent_landings.jsonl and
    latest_landings.md (the Director turn-start pane) update, closing the
    visibility gap the incident exposed.

Usage:
    python tools/orchestrator/poll_landing.py <anchor> [<anchor> ...]
    python tools/orchestrator/poll_landing.py --anchor a1 --anchor a2 \
        --queue overnight_queue --timeout-s 5400 --interval-s 60
    python tools/orchestrator/poll_landing.py --expect-mode any <anchor>   # accept smoke|full
    python tools/orchestrator/poll_landing.py --once <anchor>              # single pass, no loop

Exit codes:
    0 = all requested anchors landed (verify_landing OK)
    3 = timeout: at least one anchor did NOT land within --timeout-s
    2 = usage / internal error

Design note (consistency with existing architecture):
    - Reuses Pattern-5b auto-SCP tool (scp_recover_landing.py) + SH-9 sync-lag recovery.
    - Reuses the verify_landing.py FULL-vs-selftest gate (does NOT reimplement it).
    - Does NOT change dispatch semantics -- landing DETECTION reliability only.
    - Pure functions (extract_b64_payload / parse_queue_status / classify_status)
      are unit-tested offline in tools/test_poll_landing.py against synthetic noisy
      stdout (the incident's exact failure modes).
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TOOLS = REPO / "tools"
REMOTE_HOST = "marsh@home"
REMOTE_ROOT = "C:/dev/hd-instrument/data"

# Base64 payload sentinels. Distinctive tokens that will not appear in an SSH
# banner or a JSON body; extraction keys off exact stripped-line equality.
B64_BEGIN = "@@HDIB64_BEGIN@@"
B64_END = "@@HDIB64_END@@"
NOFILE_MARK = "@@HDIB64_NOFILE@@"

# queue.json entry statuses (safe_queue.mark_outcome / force_status vocabulary).
TERMINAL_STATUSES = {"completed", "failed", "error", "timeout", "killed", "cancelled"}
NONTERMINAL_STATUSES = {"pending", "running", "claimed", ""}

# ssh hardening: -T disables pty (no CR injection); LogLevel=ERROR suppresses the
# banner/MOTD; BatchMode avoids prompts; bounded connect + keepalive.
SSH_OPTS = [
    "-T",
    "-o", "ConnectTimeout=15",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=3",
]

# Windows: keep ssh subprocesses windowless (testbed CREATE_NO_WINDOW discipline).
_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


# ---------- pure, offline-testable core ----------

def extract_b64_payload(raw_stdout: str) -> tuple[str | None, str]:
    """Extract the base64 payload between the sentinels from noisy ssh stdout.

    Robust to: SSH banner / MOTD lines, CRLF, and codepage mojibake surrounding
    the sentinel block. Returns (payload_or_None, state) where state is one of:
        'OK'      -> payload is the base64 string between the sentinels
        'NOFILE'  -> remote reported the queue.json did not exist
        'UNKNOWN' -> sentinels not found / blank output (poll infra hiccup)

    A blank or banner-only stdout yields ('', 'UNKNOWN') -- NEVER an empty-but-OK
    payload -- so the caller cannot mistake SSH noise for "not landed".
    """
    if raw_stdout is None:
        return None, "UNKNOWN"
    # Normalize CR out, strip each line; base64 ignores interior whitespace but we
    # key sentinel detection off exact stripped-line equality.
    lines = [ln.replace("\r", "").strip() for ln in raw_stdout.split("\n")]
    if any(ln == NOFILE_MARK for ln in lines):
        return None, "NOFILE"
    try:
        i0 = lines.index(B64_BEGIN)
        i1 = lines.index(B64_END)
    except ValueError:
        return None, "UNKNOWN"
    if i1 <= i0:
        return None, "UNKNOWN"
    payload = "".join(lines[i0 + 1:i1])
    # Keep only the base64 alphabet -- any stray codepage byte that survived is dropped.
    payload = "".join(c for c in payload if c.isalnum() or c in "+/=")
    if not payload:
        return None, "UNKNOWN"
    return payload, "OK"


def parse_queue_status(queue_json_bytes: bytes, anchor: str) -> tuple[str | None, str]:
    """Find the anchor's entry status in a queue.json byte payload.

    Returns (status_or_None, state):
        'FOUND'    -> status is the entry's status string
        'NOTFOUND' -> queue parsed but no entry named <anchor>
        'UNKNOWN'  -> payload not valid JSON (treat as poll hiccup)
    Matches both the canonical anchor and its SH-4 double-prefix form.
    """
    try:
        d = json.loads(queue_json_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "UNKNOWN"
    exps = d.get("experiments", []) if isinstance(d, dict) else []
    naked = anchor[len("exp_"):] if anchor.startswith("exp_") else anchor
    candidates = {anchor, naked, f"exp_{naked}", f"exp_exp_{naked}"}
    for entry in exps:
        if not isinstance(entry, dict):
            continue
        if entry.get("name") in candidates:
            return str(entry.get("status", "")), "FOUND"
    return None, "NOTFOUND"


def classify_status(status: str | None, state: str) -> str:
    """Map a (status, state) pair to a poll decision.

    Returns one of:
        'TERMINAL'    -> queue says the run reached a terminal status; confirm now
        'NONTERMINAL' -> run is still pending/running; keep waiting (skip scp)
        'UNKNOWN'     -> could not read status; escalate to authoritative recover
    A NOTFOUND entry classifies as UNKNOWN (the entry may not be visible yet, or
    the anchor name differs) so we still attempt the authoritative confirm rather
    than declare absence.
    """
    if state in ("UNKNOWN", "NOFILE", "NOTFOUND"):
        return "UNKNOWN"
    s = (status or "").strip().lower()
    if s in NONTERMINAL_STATUSES:
        return "NONTERMINAL"
    if s in TERMINAL_STATUSES:
        return "TERMINAL"
    # Unrecognized status -> be conservative, confirm authoritatively.
    return "UNKNOWN"


# ---------- side-effecting layer ----------

def _run_bounded(cmd: list[str], timeout_s: int) -> tuple[int, str, str]:
    """Run cmd windowless with a wall-timeout. Returns (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s,
            creationflags=_CREATE_NO_WINDOW,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or ""), (e.stderr or "") + f"\n[timeout {timeout_s}s]"
    except FileNotFoundError as e:
        return 127, "", f"[executable not found: {e}]"


def remote_queue_precheck(queue: str, anchor: str) -> str:
    """Cheap, SSH-noise-robust classification of an anchor's remote queue status.

    Returns 'TERMINAL' / 'NONTERMINAL' / 'UNKNOWN'. Never raises. UNKNOWN on any
    infra hiccup so the caller escalates to the authoritative recover.
    """
    remote_q = f"{REMOTE_ROOT}/{queue}/queue.json"
    ps = (
        f"$p='{remote_q}'; "
        f"if (Test-Path $p) {{ "
        f"Write-Output '{B64_BEGIN}'; "
        f"Write-Output ([Convert]::ToBase64String([IO.File]::ReadAllBytes($p))); "
        f"Write-Output '{B64_END}' }} "
        f"else {{ Write-Output '{NOFILE_MARK}' }}"
    )
    cmd = ["ssh", *SSH_OPTS, REMOTE_HOST,
           f"powershell -NoProfile -NonInteractive -Command \"{ps}\""]
    rc, out, _ = _run_bounded(cmd, timeout_s=30)
    if rc != 0:
        return "UNKNOWN"
    payload, state = extract_b64_payload(out)
    if state != "OK" or payload is None:
        return classify_status(None, state)
    try:
        raw = base64.b64decode(payload, validate=False)
    except (binascii.Error, ValueError):
        return "UNKNOWN"
    status, pstate = parse_queue_status(raw, anchor)
    return classify_status(status, pstate)


def authoritative_confirm(anchor: str, expect_mode: str) -> tuple[bool, str]:
    """Run scp_recover_landing.py --verify-after; rc==0 == genuinely landed.

    Returns (landed, detail). scp is a byte transfer (rc-checked) and
    verify_landing reads local metrics.json -- neither parses noisy remote stdout,
    so this is the reliable landing signal.
    """
    recover = TOOLS / "orchestrator" / "scp_recover_landing.py"
    if not recover.exists():
        return False, f"scp_recover_landing.py missing at {recover}"
    cmd = [sys.executable, str(recover), "--verify-after", anchor]
    rc, out, err = _run_bounded(cmd, timeout_s=180)
    # scp_recover folds the verify_landing rc into its own exit code, but only for
    # the default expect-mode. For non-default modes, re-verify explicitly.
    if rc == 0 and expect_mode != "full":
        verify = TOOLS / "verify_landing.py"
        vrc, vout, _ = _run_bounded(
            [sys.executable, str(verify), anchor, "--expect-mode", expect_mode],
            timeout_s=30)
        if vrc != 0:
            return False, (vout or out).strip().splitlines()[-1] if (vout or out).strip() else "verify_fail"
    detail = (out or err).strip().splitlines()
    return rc == 0, (detail[-1] if detail else f"rc={rc}")


def _notify_panes() -> None:
    """Refresh recent_landings.jsonl + latest_landings.md so the Director pane updates."""
    try:
        sys.path.insert(0, str(TOOLS))
        import landing_notifier  # noqa: E402
        landing_notifier.scan()
    except Exception:
        pass  # pane refresh is best-effort; never block the poll on it


def poll(anchors: list[str], queue: str | None, expect_mode: str,
         timeout_s: int, interval_s: int, once: bool) -> int:
    pending = list(dict.fromkeys(anchors))  # de-dupe, keep order
    landed: dict[str, str] = {}
    deadline = time.time() + timeout_s
    first = True
    while pending:
        if not first:
            time.sleep(interval_s)
        first = False
        for anchor in list(pending):
            decision = "UNKNOWN"
            if queue:
                decision = remote_queue_precheck(queue, anchor)
            if decision == "NONTERMINAL":
                # Still running per a cleanly-read queue -> skip the scp this tick.
                print(f"[poll] {anchor}: running (queue nonterminal)", flush=True)
                continue
            # TERMINAL or UNKNOWN (or no queue given) -> authoritative confirm.
            ok, detail = authoritative_confirm(anchor, expect_mode)
            if ok:
                landed[anchor] = detail
                pending.remove(anchor)
                print(f"LANDED {anchor}  {detail}", flush=True)
                _notify_panes()
            else:
                tag = "terminal-in-queue-but-metrics-not-ready" if decision == "TERMINAL" else "not-landed"
                print(f"[poll] {anchor}: {tag} ({detail})", flush=True)
        if not pending:
            break
        if once:
            break
        if time.time() >= deadline:
            break

    for a in anchors:
        if a in landed:
            print(f"OK   {a}  {landed[a]}")
        else:
            print(f"MISS {a}  did not land within {timeout_s}s")
    if pending and not once:
        return 3
    if pending and once:
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Robust landing poller (scp_recover + verify_landing; "
                    "base64-sentinel queue pre-check). Replaces `type queue.json | grep`.")
    p.add_argument("anchors", nargs="*", help="one or more anchor names")
    p.add_argument("--anchor", action="append", default=[],
                   help="anchor name (repeatable; alternative to positional)")
    p.add_argument("--queue", default=None,
                   help="remote queue dir name for the cheap pre-check "
                        "(e.g. overnight_queue). Omit to always use the "
                        "authoritative scp+verify path each tick.")
    p.add_argument("--expect-mode", default="full", choices=["full", "smoke", "any"],
                   help="run_mode gate handed to verify_landing (default full)")
    p.add_argument("--timeout-s", type=int, default=5400,
                   help="give up after this many seconds (default 5400 = 90min)")
    p.add_argument("--interval-s", type=int, default=60,
                   help="seconds between poll ticks (default 60)")
    p.add_argument("--once", action="store_true",
                   help="single pass, no loop (for scripted / scheduled checks)")
    args = p.parse_args(argv)

    anchors = list(args.anchors) + list(args.anchor)
    if not anchors:
        p.print_usage()
        print("error: at least one anchor required", file=sys.stderr)
        return 2
    if args.interval_s <= 0:
        print("error: --interval-s must be > 0", file=sys.stderr)
        return 2

    return poll(anchors, args.queue, args.expect_mode,
                args.timeout_s, args.interval_s, args.once)


if __name__ == "__main__":
    sys.exit(main())
