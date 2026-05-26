"""One-shot cutover from old single-runner to new multi-runner production.

Run this ON THE WORKSTATION (or remote via ssh). Performs the cutover as an
atomic step:

  1. Records current runner PIDs and their current experiments
  2. Stops current healer + current GPU runner + current CPU runner
  3. Re-queues any 'running' entries back to 'pending' (atomically via safe_queue)
  4. Starts new runner_v2_prod.py for GPU queue + CPU queue
  5. Starts new healer_v3.py
  6. Reports new PIDs + heartbeat paths

Use --dry-run to preview without making changes.

Threading: assumes you've already SCP'd the new code to:
  C:\\dev\\hd-instrument\\tools\\safe_queue.py
  C:\\dev\\hd-instrument\\tools\\runner_config.py
  C:\\dev\\hd-instrument\\tools\\healer_v3.py
  C:\\dev\\hd-instrument\\experiments\\runner_v2_prod.py
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")
PYTHON = str(REPO / ".venv" / "Scripts" / "python.exe")
sys.path.insert(0, str(REPO / "tools"))


def run_ps(cmd: str) -> str:
    """Run a PowerShell command and return stdout (stripped)."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


def find_runner_pid(queue_name: str) -> tuple[int | None, str | None]:
    """Return (pid, current_experiment) from the heartbeat file."""
    hb = REPO / "data" / queue_name / "heartbeat.json"
    if not hb.exists():
        return None, None
    try:
        data = json.loads(hb.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, None
    pid = data.get("pid")
    return (int(pid) if pid else None), data.get("current")


def find_healer_pid() -> int | None:
    hb = REPO / "data" / "healer_heartbeat.json"
    if not hb.exists():
        return None
    try:
        data = json.loads(hb.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    pid = data.get("pid")
    return int(pid) if pid else None


def find_child_pids(parent_pid: int) -> list[int]:
    """Return PIDs of python.exe children of the given parent."""
    cmd = (
        f"Get-CimInstance Win32_Process -Filter \"Name='python.exe' AND "
        f"ParentProcessId={parent_pid}\" | Select-Object -ExpandProperty ProcessId"
    )
    out = run_ps(cmd)
    return [int(line) for line in out.splitlines() if line.strip().isdigit()]


def stop_pid(pid: int, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [DRY] would stop PID {pid}")
        return True
    print(f"  Stopping PID {pid}...")
    cmd = f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], timeout=10)
    time.sleep(1)
    alive_cmd = f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{ 'alive' }} else {{ 'dead' }}"
    state = run_ps(alive_cmd)
    print(f"    PID {pid}: {state}")
    return state == "dead"


def requeue_running(queue_name: str, dry_run: bool) -> int:
    """Mark all 'running' entries in queue_name as 'pending'.
    Atomic via safe_queue."""
    from safe_queue import QueueLock
    queue_path = REPO / "data" / queue_name / "queue.json"
    if not queue_path.exists():
        print(f"  {queue_name}/queue.json does not exist; skipping")
        return 0
    if dry_run:
        # Read only to count
        with QueueLock(queue_path, max_wait_s=10.0) as lock:
            q = lock.read()
            count = sum(1 for e in q["experiments"] if e.get("status") == "running")
        print(f"  [DRY] would re-queue {count} 'running' entries in {queue_name}")
        return count
    with QueueLock(queue_path, max_wait_s=10.0) as lock:
        q = lock.read()
        count = 0
        for e in q["experiments"]:
            if e.get("status") == "running":
                e["status"] = "pending"
                e["note"] = (
                    (e.get("note", "") + "; " if e.get("note") else "")
                    + f"cutover({datetime.now().isoformat(timespec='seconds')}): "
                    + f"requeued (was running, claimed_by={e.get('claimed_by', 'old_runner')})"
                )
                count += 1
        if count > 0:
            lock.write(q)
    print(f"  Re-queued {count} 'running' entries in {queue_name}")
    return count


def launch_detached(args: list[str], env_extra: dict[str, str], label: str, dry_run: bool) -> int | None:
    """Launch a detached python process via WMI Win32_Process.Create so it survives
    ssh disconnect. Returns PID. Redirects stdout/stderr to a per-runner log file.

    Detachment notes: PowerShell Start-Process does NOT fully detach the child from
    the spawning session — when the parent powershell exits, the child can die.
    Win32_Process.Create makes the child a true detached process owned by the OS
    (no parent relationship), so ssh disconnect doesn't kill it.
    """
    if dry_run:
        env_str = " ".join(f"{k}={v}" for k, v in env_extra.items())
        print(f"  [DRY] would launch {label}: {' '.join(args)}  env: {env_str}")
        return None

    # Build a cmd.exe-wrapped command line: set env vars THEN run python, redirect output.
    # Quote each arg defensively in case of spaces.
    def _quote(a: str) -> str:
        if " " in a or "&" in a:
            return f'\\"{a}\\"'
        return a

    args_quoted = " ".join(_quote(a) for a in args)
    env_parts = " && ".join(f"set {k}={v}" for k, v in env_extra.items())
    safe_label = label.replace(" ", "_").replace("/", "_")
    log_file = f"C:\\dev\\hd-instrument\\data\\detached_{safe_label}.log"

    # The full cmd.exe payload — env first, then exec python, capture stdout+stderr.
    if env_parts:
        inner = f"{env_parts} && {args_quoted} > {log_file} 2>&1"
    else:
        inner = f"{args_quoted} > {log_file} 2>&1"

    # Wrap in cmd.exe /c so env vars take effect. Win32_Process.Create needs a single
    # CommandLine string.
    cmdline = f'cmd.exe /c "{inner}"'

    # Invoke via CIM (modern WMI). Returns the new PID.
    ps_script = (
        "$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        f"-Arguments @{{ CommandLine = '{cmdline}' }}; "
        "if ($result.ReturnValue -eq 0) { $result.ProcessId } "
        "else { Write-Error ('Win32_Process.Create failed: ' + $result.ReturnValue); '' }"
    )
    out = run_ps(ps_script)
    try:
        pid = int(out.splitlines()[-1])
        print(f"  Launched {label}: PID {pid}  (log: {log_file})")
        return pid
    except (ValueError, IndexError):
        print(f"  WARN: could not parse PID for {label}; ps output: {out!r}")
        return None


def cutover(dry_run: bool, do_gpu: bool = True, do_cpu: bool = True, do_healer: bool = True):
    print("=" * 60)
    print("CUTOVER: old runners -> new runner_v2_prod (multi-runner safe)")
    print(f"Dry-run: {dry_run}  GPU: {do_gpu}  CPU: {do_cpu}  Healer: {do_healer}")
    print("=" * 60)

    # 1. Verify new code is in place
    required = [
        REPO / "tools" / "safe_queue.py",
        REPO / "tools" / "runner_config.py",
        REPO / "tools" / "healer_v3.py",
        REPO / "experiments" / "runner_v2_prod.py",
    ]
    print("\n[1] Verifying new code in place...")
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print(f"  MISSING: {missing}")
        print("  Refusing to cutover. Upload these files first.")
        return 1
    for p in required:
        print(f"  OK: {p}")

    # 2. Identify current PIDs
    print("\n[2] Identifying current runner + healer PIDs...")
    gpu_pid, gpu_curr = find_runner_pid("overnight_queue") if do_gpu else (None, None)
    cpu_pid, cpu_curr = find_runner_pid("remote_cpu_queue") if do_cpu else (None, None)
    healer_pid = find_healer_pid() if do_healer else None
    print(f"  GPU runner: PID={gpu_pid}  current={gpu_curr}")
    print(f"  CPU runner: PID={cpu_pid}  current={cpu_curr}")
    print(f"  Healer:     PID={healer_pid}")

    # 3. Find child experiment subprocesses
    print("\n[3] Identifying child experiment subprocesses...")
    gpu_kids = find_child_pids(gpu_pid) if (do_gpu and gpu_pid) else []
    cpu_kids = find_child_pids(cpu_pid) if (do_cpu and cpu_pid) else []
    print(f"  GPU child PIDs: {gpu_kids}")
    print(f"  CPU child PIDs: {cpu_kids}")

    # 4. Stop everything (children first so parent can't mark them on exit)
    print("\n[4] Stopping current runners + healer + child experiments...")
    for pid in gpu_kids + cpu_kids:
        if pid:
            stop_pid(pid, dry_run)
    for pid_label, pid in [("GPU", gpu_pid), ("CPU", cpu_pid), ("Healer", healer_pid)]:
        if pid:
            stop_pid(pid, dry_run)

    # 5. Re-queue any 'running' entries that didn't get terminal status
    print("\n[5] Re-queueing 'running' entries (safe_queue atomic)...")
    if do_gpu:
        requeue_running("overnight_queue", dry_run)
    if do_cpu:
        requeue_running("remote_cpu_queue", dry_run)

    # 6. Launch new runner_v2_prod for each queue + healer_v3
    print("\n[6] Launching new processes...")
    # Thread budget: ask the recommender, don't hardcode. Previous version
    # used GPU=2 which choked CPU-heavy experiments (e.g. R10 PPMI phase at K=2048).
    # GPU runner now gets full usable cores; if CPU runner runs concurrently
    # they'll briefly oversubscribe (accepted: better than chronic slowdown).
    sys.path.insert(0, str(REPO / "tools"))
    from runner_config import recommend_runner_config

    # Both queues launch ONE runner_v2_prod each. Pass queue_depth=1 to the
    # recommender so it returns "1 runner with usable_cores threads" instead of
    # splitting cores across multiple imagined runners that we don't actually spawn.
    if do_gpu:
        gpu_cfg = recommend_runner_config(queue_kind="gpu", queue_depth=1, avg_runtime_min=30)
        print(f"  GPU thread budget: {gpu_cfg.threads_per_runner} (per recommender)")
        gpu_new_pid = launch_detached(
            [PYTHON, str(REPO / "experiments" / "runner_v2_prod.py"),
             "overnight_queue", "--id", "gpu_runner_0"],
            env_extra=gpu_cfg.env_vars(),
            label="GPU runner_v2_prod", dry_run=dry_run,
        )
    else:
        gpu_new_pid = None

    if do_cpu:
        cpu_cfg = recommend_runner_config(queue_kind="cpu", queue_depth=1, avg_runtime_min=30)
        print(f"  CPU thread budget: {cpu_cfg.threads_per_runner} (per recommender)")
        cpu_new_pid = launch_detached(
            [PYTHON, str(REPO / "experiments" / "runner_v2_prod.py"),
             "remote_cpu_queue", "--id", "cpu_runner_0"],
            env_extra=cpu_cfg.env_vars(),
            label="CPU runner_v2_prod", dry_run=dry_run,
        )
    else:
        cpu_new_pid = None
    healer_new_pid = launch_detached(
        [PYTHON, str(REPO / "tools" / "healer_v3.py")],
        env_extra={},
        label="Healer v3", dry_run=dry_run,
    ) if do_healer else None

    # 7. Brief verification window
    if not dry_run:
        print("\n[7] Verifying new heartbeats appear (waiting 8s)...")
        time.sleep(8)
        for label, queue, expected_id in [
            ("GPU", "overnight_queue", "gpu_runner_0"),
            ("CPU", "remote_cpu_queue", "cpu_runner_0"),
        ]:
            hb_path = REPO / "data" / queue / f"heartbeat.{expected_id}.json"
            if hb_path.exists():
                hb = json.loads(hb_path.read_text(encoding="utf-8"))
                print(f"  {label}: heartbeat OK, runner_id={hb.get('runner_id')}, "
                      f"pid={hb.get('pid')}, status={hb.get('status')}")
            else:
                print(f"  {label}: WARN — {hb_path.name} not yet present")

    print("\n" + "=" * 60)
    print(f"Cutover complete. New PIDs: GPU={gpu_new_pid} CPU={cpu_new_pid} Healer={healer_new_pid}")
    print("Old heartbeat.json files have been overwritten by new runners.")
    print("=" * 60)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Print plan without executing")
    ap.add_argument("--gpu-only", action="store_true", help="Cut over only GPU runner")
    ap.add_argument("--cpu-only", action="store_true", help="Cut over only CPU runner")
    ap.add_argument("--skip-healer", action="store_true", help="Leave healer untouched")
    args = ap.parse_args()
    if args.gpu_only and args.cpu_only:
        print("ERROR: --gpu-only and --cpu-only are mutually exclusive")
        return 2
    do_gpu = not args.cpu_only
    do_cpu = not args.gpu_only
    do_healer = not args.skip_healer
    # If targeting only one queue, leave healer alone (it serves both queues)
    if args.gpu_only or args.cpu_only:
        do_healer = False
        if not args.skip_healer:
            print("(Auto: --skip-healer because targeting single queue)")
    return cutover(args.dry_run, do_gpu=do_gpu, do_cpu=do_cpu, do_healer=do_healer)


if __name__ == "__main__":
    sys.exit(main())
