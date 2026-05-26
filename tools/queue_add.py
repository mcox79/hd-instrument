"""Queue-entry gate: verify a script is queueable before adding it.

Usage:
    python tools/queue_add.py <queue_name> <entry_name> <script_path> \\
        --prereg preregs/<file>.md [--timeout 3600]

Required checks (script must pass ALL):
    1. Script file exists.
    2. Script supports `--self-test` and exits 0.
    3. Script supports `--smoke` and exits 0, producing metrics.json at
       data/exp_{HDLAB_EXP_NAME}/metrics.json with required fields.
    4. Prereg markdown file exists.

Prevents the silent-failure mode from 2026-05-20 where scripts wrote to
hardcoded names while the queue renamed them, producing zero metrics.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from safe_queue import QueueLock  # noqa: E402

PYTHON = sys.executable
REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")
SMOKE_TIMEOUT_S = 180  # 3 min cap on smoke


def fail(msg: str) -> "None":
    print(f"GATE_FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_script_exists(script: str) -> Path:
    path = REPO / script
    if not path.exists():
        fail(f"script not found: {path}")
    return path


def run_with_flag(script: Path, flag: str, env_extra: dict) -> tuple[int, str]:
    """Run script with single flag. Return (exit_code, tail_of_log).

    Uses a temp log file (matches the actual runner's approach) instead of
    capture_output, which has pipe-buffering issues with CUDA-heavy scripts.
    """
    env = {**os.environ, **env_extra}
    log_path = REPO / "data" / f"gate_log_{script.stem}_{flag.lstrip('-')}.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8") as logf:
            result = subprocess.run(
                [PYTHON, "-u", str(script), flag],
                cwd=str(REPO),
                env=env,
                stdout=logf,
                stderr=subprocess.STDOUT,
                timeout=SMOKE_TIMEOUT_S,
            )
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {SMOKE_TIMEOUT_S}s (log: {log_path})"
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        tail = "\n".join(lines[-15:])
    except OSError:
        tail = f"(log unreadable at {log_path})"
    return result.returncode, tail


def validate_metrics(path: Path) -> str | None:
    if not path.exists():
        return f"missing at {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"invalid_json: {e}"
    if not isinstance(data, dict):
        return "not_an_object"
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return f"missing_fields: {missing}"
    if not data.get("verdict"):
        return "empty_verdict"
    if not data.get("verdict_msg"):
        return "empty_verdict_msg"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("queue_name", help="Queue dir under data/ (e.g. overnight_queue)")
    ap.add_argument("entry_name", help="Name for the queue entry (also HDLAB_EXP_NAME)")
    ap.add_argument("script", help="Script path relative to repo root")
    ap.add_argument("--prereg", required=True, help="Path to prereg markdown (relative to repo)")
    ap.add_argument("--timeout", type=int, default=3600, help="Per-run timeout seconds")
    ap.add_argument("--purpose", default="", help="One-line purpose string for the queue entry")
    ap.add_argument("--skip-smoke", action="store_true",
                    help="Skip smoke run (use only when previously smoke-tested)")
    ap.add_argument(
        "--rerun-as",
        metavar="NEW_NAME",
        default=None,
        help=(
            "Clone the entry under NEW_NAME (inherits script+prereg) and queue it as pending. "
            "Bypasses dedup: the original entry is untouched. "
            "Use when Strategy explicitly wants to re-run a previously-queued experiment. "
            "If NEW_NAME is the same as entry_name, a date suffix is appended automatically."
        ),
    )
    ap.add_argument(
        "--allow-duplicate",
        action="store_true",
        help=(
            "If entry_name already exists with status in {done, failed, completed, canceled, killed}, "
            "reset it to pending in-place (clears started_at, increments run_index). "
            "Refuses if status is 'running' or 'pending' (use --rerun-as for those)."
        ),
    )
    args = ap.parse_args()

    # ── Host guard ──────────────────────────────────────────────────────────────
    # Remote queues (overnight_queue, remote_cpu_queue) are owned by the remote
    # runner on marsh@home. Writing to their queue.json from the local Windows
    # box only mutates the LOCAL data/<queue>/queue.json — the remote runner
    # never sees the entry. This caused 5 anchors to silently fail to ship on
    # 2026-05-24.
    #
    # Structural fix: refuse remote-queue invocations unless the env marker
    # HDLAB_QUEUE_ADD_ON_REMOTE=1 is set. queue_add.sh sets this when SSH'ing
    # into the remote host before invoking queue_add.py, so the legitimate
    # remote-side call still works. Direct local invocation now fails loud.
    REMOTE_QUEUES = {"overnight_queue", "remote_cpu_queue"}
    if args.queue_name in REMOTE_QUEUES and os.environ.get("HDLAB_QUEUE_ADD_ON_REMOTE") != "1":
        fail(
            f"queue '{args.queue_name}' is a REMOTE queue and must be added via "
            f"`bash tools/orchestrator/queue_add.sh {args.queue_name} ...` (which "
            f"SCPs the script and SSHs into marsh@home). Direct local invocation "
            f"of queue_add.py only writes the LOCAL data/{args.queue_name}/queue.json "
            f"and the remote runner never sees the entry. If you ARE running this on "
            f"the remote host, set HDLAB_QUEUE_ADD_ON_REMOTE=1."
        )

    print(f"[gate] entry_name={args.entry_name}")
    print(f"[gate] script={args.script}")
    print(f"[gate] prereg={args.prereg}")

    # 1. Script exists
    script_path = check_script_exists(args.script)
    print(f"[gate] OK: script exists at {script_path}")

    # 2. Prereg exists
    prereg_path = REPO / args.prereg
    if not prereg_path.exists():
        fail(f"prereg not found: {prereg_path}")
    print(f"[gate] OK: prereg exists at {prereg_path}")

    # 3. Self-test passes
    print(f"[gate] running --self-test...")
    t0 = time.monotonic()
    rc, tail = run_with_flag(script_path, "--self-test",
                             env_extra={"HDLAB_EXP_NAME": args.entry_name})
    if rc != 0:
        print(tail, file=sys.stderr)
        fail(f"--self-test exit={rc} (after {time.monotonic()-t0:.1f}s)")
    print(f"[gate] OK: --self-test passed in {time.monotonic()-t0:.1f}s")

    # 4. Smoke passes + valid metrics
    if not args.skip_smoke:
        print(f"[gate] running --smoke under HDLAB_EXP_NAME={args.entry_name}_smoke...")
        smoke_name = f"{args.entry_name}_smoke"
        t0 = time.monotonic()
        rc, tail = run_with_flag(script_path, "--smoke",
                                 env_extra={"HDLAB_EXP_NAME": smoke_name})
        if rc != 0:
            print(tail, file=sys.stderr)
            fail(f"--smoke exit={rc} (after {time.monotonic()-t0:.1f}s)")
        smoke_metrics = REPO / "data" / f"exp_{smoke_name}" / "metrics.json"
        err = validate_metrics(smoke_metrics)
        if err:
            fail(f"smoke metrics invalid: {err}")
        print(f"[gate] OK: --smoke produced valid metrics in {time.monotonic()-t0:.1f}s")

    # Validate flag combinations
    if args.rerun_as and args.allow_duplicate:
        fail("--rerun-as and --allow-duplicate are mutually exclusive; pick one")

    # 5. Add to queue
    queue_dir = REPO / "data" / args.queue_name
    queue_dir.mkdir(parents=True, exist_ok=True)
    queue_file = queue_dir / "queue.json"

    # Resolve the actual name that will be registered in the queue.
    # For --rerun-as: the new name is the target; for all other cases it's entry_name.
    if args.rerun_as:
        register_name = args.rerun_as
        # If caller passed the same name as entry_name, auto-suffix with today's date.
        if register_name == args.entry_name:
            register_name = f"{args.entry_name}_rerun_{time.strftime('%Y-%m-%d')}"
            print(f"[gate] --rerun-as same as entry_name; auto-suffixed to {register_name}")
    else:
        register_name = args.entry_name

    entry = {
        "name": register_name,
        "script": args.script,
        "status": "pending",
        "purpose": args.purpose or f"See {args.prereg}",
        "prereg": args.prereg,
        "timeout_s": args.timeout,
        "gated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # Terminal statuses that --allow-duplicate can reset.
    _TERMINAL = {"done", "failed", "completed", "canceled", "killed"}

    with QueueLock(queue_file, max_wait_s=10.0) as lock:
        if queue_file.exists():
            q = lock.read()
        else:
            q = {"experiments": []}

        existing_map = {e["name"]: e for e in q["experiments"]}

        if args.allow_duplicate:
            # --allow-duplicate: reset an existing terminal entry in-place.
            if args.entry_name in existing_map:
                ex = existing_map[args.entry_name]
                cur_status = ex.get("status", "")
                if cur_status in ("running", "pending"):
                    fail(
                        f"--allow-duplicate refused: {args.entry_name} is currently "
                        f"'{cur_status}'. Use --rerun-as to queue a parallel copy."
                    )
                if cur_status not in _TERMINAL:
                    fail(
                        f"--allow-duplicate refused: {args.entry_name} has unrecognised "
                        f"status '{cur_status}'. Inspect queue.json manually."
                    )
                run_index = ex.get("run_index", 1) + 1
                ex.update({
                    "status": "pending",
                    "purpose": args.purpose or ex.get("purpose", f"See {args.prereg}"),
                    "prereg": args.prereg,
                    "timeout_s": args.timeout,
                    "gated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "run_index": run_index,
                    # Clear previous-run timestamps.
                    "started_at": None,
                    "finished_at": None,
                    "claimed_by": None,
                })
                lock.write(q)
                print(f"[gate] OK: reset {args.entry_name} to pending (run_index={run_index})")
            else:
                # Name not in queue yet; just add fresh (--allow-duplicate is harmless here).
                q["experiments"].append(entry)
                lock.write(q)
                print(f"[gate] OK: queued {register_name} (new entry; --allow-duplicate was no-op)")

        elif args.rerun_as:
            # --rerun-as: always append under register_name (already de-collided above).
            if register_name in existing_map:
                fail(
                    f"--rerun-as target '{register_name}' already exists in queue. "
                    f"Choose a different name or use --allow-duplicate on that name."
                )
            q["experiments"].append(entry)
            lock.write(q)
            print(f"[gate] OK: queued clone '{register_name}' (original '{args.entry_name}' untouched)")

        else:
            # Default: dedup by name (original behaviour).
            if args.entry_name in existing_map:
                print(
                    f"[gate] WARN: {args.entry_name} already in queue; not adding duplicate. "
                    f"Use --rerun-as <new_name> or --allow-duplicate to override."
                )
            else:
                q["experiments"].append(entry)
                lock.write(q)
                print(f"[gate] OK: queued {register_name}")

        pending = [e["name"] for e in q["experiments"] if e["status"] == "pending"]
    print(f"[gate] queue pending now ({len(pending)}): {pending}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
