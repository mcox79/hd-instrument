"""ship_anchor.py — one-call wrapper for: smoke + timeout-compute + queue_add + status_log.

Reduces ~50 lines of bash that exp_dev runs each ship to one command. Consolidates the
discipline that's identical every ship while preserving all PROT compliance:
- PROT-018 (_n<N> suffix binding) — delegated to queue_add.py
- PROT-019 (timeout floors) — computed here per formula
- PROT-021 (seed checkpoint M/run_mode tag) — script's responsibility
- PROT-022 (formula self-tests) — script's responsibility

Usage:
    python tools/ship_anchor.py \\
        --name <anchor_name> \\
        --script experiments/exp_<name>.py \\
        --prereg preregs/<date>_<name>.md \\
        --queue overnight_queue \\
        --smoke-n 4096 --smoke-seeds 2 \\
        --full-n 8192 --full-seeds 5 \\
        --scaling-exp 1.5 \\
        [--skip-smoke]                # if smoke already verified
        [--smoke-wall-s <N>]          # if smoke already run; bypass smoke step

What it does (in order):
    1. Pre-flight: check blocked_items.json; abort if anchor matches a blocked pattern
    2. Run smoke (or use --smoke-wall-s if provided)
    3. Compute timeout via PROT-019 formula:
       ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))
       Floor at 600s; cap at 14400s (>14400 needs justification; logged + non-zero exit if exceeded)
    4. Call tools/orchestrator/queue_add.sh with computed timeout
    5. Emit status_log entry (event_kind=experiment_queued)

Returns:
    Exit 0 + last line "SHIPPED: <name> timeout=<T>s queue=<Q>" on success.
    Non-zero exit + GATE_FAIL line on any failure.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOCKED_ITEMS_PATH = REPO / "data" / "blocked_items.json"
STATUS_LOG_PATH = REPO / "data" / "orchestrator_status_log.jsonl"
QUEUE_ADD_SH = REPO / "tools" / "orchestrator" / "queue_add.sh"

# PROT-019 floors
TIMEOUT_FLOOR_S = 600
TIMEOUT_CEILING_S = 14400


def fail(msg: str, exit_code: int = 1) -> None:
    print(f"GATE_FAIL: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def load_blocked() -> list[dict]:
    if not BLOCKED_ITEMS_PATH.exists():
        return []
    try:
        doc = json.loads(BLOCKED_ITEMS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"WARN: blocked_items.json unreadable: {e}", file=sys.stderr)
        return []
    return doc.get("blocked", [])


def is_blocked(name: str, blocked: list[dict]) -> tuple[bool, str]:
    for entry in blocked:
        pat = entry.get("anchor_pattern", "")
        if not pat:
            continue
        # Simple glob: trailing * matches prefix.
        if pat.endswith("*"):
            if name.startswith(pat[:-1]):
                return True, entry.get("reason", "blocked")
        elif pat == name:
            return True, entry.get("reason", "blocked")
    return False, ""


def run_smoke(script_rel: str, name: str) -> float:
    """Run script with --smoke, return wall_s. Fail if smoke fails."""
    print(f"[ship] running smoke: {script_rel}")
    env = {**os.environ, "HDLAB_EXP_NAME": name, "HDLAB_RUN_MODE": "smoke"}
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-u", str(REPO / script_rel), "--smoke"],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        fail(f"smoke timed out after 300s for {script_rel}")
    wall_s = time.time() - start
    if result.returncode != 0:
        tail = (result.stdout or "")[-1500:] + "\n" + (result.stderr or "")[-1500:]
        fail(f"smoke exit {result.returncode} for {script_rel}\n--- TAIL ---\n{tail}")
    print(f"[ship] smoke OK in {wall_s:.1f}s")
    return wall_s


def compute_timeout(
    smoke_wall_s: float,
    smoke_n: int,
    full_n: int,
    smoke_seeds: int,
    full_seeds: int,
    scaling_exp: float,
) -> int:
    """PROT-019 formula. Floor 600s, ceiling 14400s."""
    raw = 1.5 * smoke_wall_s * (full_n / smoke_n) ** scaling_exp * (full_seeds / smoke_seeds)
    timeout_s = int(math.ceil(raw))
    timeout_s = max(timeout_s, TIMEOUT_FLOOR_S)
    if timeout_s > TIMEOUT_CEILING_S:
        fail(
            f"computed timeout {timeout_s}s exceeds PROT-019 ceiling {TIMEOUT_CEILING_S}s; "
            f"smoke_wall={smoke_wall_s:.1f}s smoke_N={smoke_n} full_N={full_n} "
            f"smoke_seeds={smoke_seeds} full_seeds={full_seeds} scaling_exp={scaling_exp}",
            exit_code=7,
        )
    return timeout_s


def call_queue_add(
    queue: str, name: str, script_rel: str, prereg_rel: str, timeout_s: int
) -> None:
    """Call queue_add.sh; abort on non-zero exit."""
    if not QUEUE_ADD_SH.exists():
        fail(f"queue_add.sh missing: {QUEUE_ADD_SH}")
    print(f"[ship] invoking queue_add.sh queue={queue} name={name} timeout={timeout_s}")
    # Use bash to invoke (queue_add.sh is a bash script)
    result = subprocess.run(
        ["bash", str(QUEUE_ADD_SH), queue, name, script_rel, prereg_rel, str(timeout_s)],
        cwd=str(REPO),
    )
    if result.returncode != 0:
        fail(f"queue_add.sh exit {result.returncode}", exit_code=result.returncode)


def emit_status_log(name: str, queue: str, timeout_s: int, smoke_wall_s: float) -> None:
    """Append one experiment_queued entry to orchestrator_status_log.jsonl."""
    ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    entry = {
        "ts": ts,
        "event_kind": "experiment_queued",
        "summary": f"{name} queued to {queue} via ship_anchor.py",
        "sub_agents": ["ship_anchor.py"],
        "outcome": f"queued; smoke wall_s={smoke_wall_s:.1f}; timeout={timeout_s}s; PROT-018/019 OK",
        "plain_language": f"Anchor {name} shipped to {queue} with PROT-019 timeout {timeout_s}s.",
        "importance": "MEDIUM",
    }
    try:
        STATUS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATUS_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError as e:
        print(f"WARN: status_log emit failed: {e}", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser(description="ship_anchor.py: smoke + queue_add + status_log")
    p.add_argument("--name", required=True, help="Anchor name (also queue entry + HDLAB_EXP_NAME)")
    p.add_argument("--script", required=True, help="Script path relative to repo root")
    p.add_argument("--prereg", required=True, help="Prereg path relative to repo root")
    p.add_argument("--queue", required=True,
                   choices=["overnight_queue", "remote_cpu_queue", "local_cpu_queue"])
    p.add_argument("--smoke-n", type=int, default=4096, help="Smoke N (default 4096)")
    p.add_argument("--smoke-seeds", type=int, default=2, help="Smoke seeds (default 2)")
    p.add_argument("--full-n", type=int, required=True, help="Full-run N")
    p.add_argument("--full-seeds", type=int, default=5, help="Full-run seeds (default 5)")
    p.add_argument("--scaling-exp", type=float, default=1.5,
                   help="Wall scaling exponent in N (default 1.5)")
    p.add_argument("--skip-smoke", action="store_true",
                   help="Skip smoke step entirely (caller has already smoked)")
    p.add_argument("--smoke-wall-s", type=float, default=None,
                   help="Pre-measured smoke wall_s (skips smoke run; still computes timeout)")
    args = p.parse_args()

    # 1. Pre-flight: blocked check
    blocked = load_blocked()
    is_blk, reason = is_blocked(args.name, blocked)
    if is_blk:
        fail(f"anchor '{args.name}' is in data/blocked_items.json: {reason}", exit_code=8)

    # 1b. Script + prereg existence
    if not (REPO / args.script).exists():
        fail(f"script not found: {args.script}")
    if not (REPO / args.prereg).exists():
        fail(f"prereg not found: {args.prereg}")

    # 2. Smoke step (or skip)
    if args.skip_smoke:
        smoke_wall_s = args.smoke_wall_s or 1.0  # cheap default if caller wants pure rote
        print(f"[ship] smoke SKIPPED (caller asserts smoke already done; wall_s={smoke_wall_s})")
    elif args.smoke_wall_s is not None:
        smoke_wall_s = args.smoke_wall_s
        print(f"[ship] smoke wall_s provided: {smoke_wall_s:.1f}s")
    else:
        smoke_wall_s = run_smoke(args.script, args.name)

    # 3. Compute timeout
    timeout_s = compute_timeout(
        smoke_wall_s=smoke_wall_s,
        smoke_n=args.smoke_n,
        full_n=args.full_n,
        smoke_seeds=args.smoke_seeds,
        full_seeds=args.full_seeds,
        scaling_exp=args.scaling_exp,
    )
    print(f"[ship] timeout={timeout_s}s "
          f"(formula: ceil(1.5 * {smoke_wall_s:.1f} * "
          f"({args.full_n}/{args.smoke_n})^{args.scaling_exp} * "
          f"({args.full_seeds}/{args.smoke_seeds})))")

    # 4. queue_add
    call_queue_add(
        queue=args.queue,
        name=args.name,
        script_rel=args.script,
        prereg_rel=args.prereg,
        timeout_s=timeout_s,
    )

    # 5. Status log emit
    emit_status_log(args.name, args.queue, timeout_s, smoke_wall_s)

    print(f"SHIPPED: {args.name} timeout={timeout_s}s queue={args.queue}")


if __name__ == "__main__":
    main()
