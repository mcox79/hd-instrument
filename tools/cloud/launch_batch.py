"""Stringed Lambda batch launcher: bootstrap once, run N experiments, terminate once.

Per-launch overhead (boot + bootstrap) is ~5 min wall and ~$0.13 per
experiment with launch_experiment.py. For a 2-3 anchor batch, that's
10-15 min wall + $0.26-0.39 wasted on re-paying setup.

This script pays setup ONCE then runs every experiment in the batch on
the same instance sequentially. The first anchor's bootstrap leaves the
.venv + git clone in place; subsequent anchors just re-dispatch.

Division of labor (per session_architecture_v1):
  - orchestrator designs experiments (writes experiments/exp_*.py)
  - testbed batches them at dispatch time (this script)

Usage:
  python tools/cloud/launch_batch.py \\
    --batch path/to/batch.json \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path ~/.ssh/lambda_canary.pem \\
    --max-cost-usd 2.00 \\
    --budget-cap-usd 5.00 \\
    --expected-wall-min 45

batch.json format (list of anchor dicts):
[
  {
    "anchor": "exp_anchor_name_v1_n4096",
    "script": "experiments/exp_anchor_name_v1_n4096.py",
    "total_cells": 15,
    "cell_regex": "(optional; defaults to substrate pattern)",
    "experiment_timeout_min": 60,
    "result_paths": [
      "data/testbed_pp8_week2/phi3_qformer_wiring_cuda.json",
      "data/testbed_pp8_week2/train_v1/*"
    ]
  },
  ...
]

result_paths (optional): list of remote glob patterns (relative to
~/hd-instrument/) to SCP back AFTER the experiment completes. Files are
mirrored under data/lambda_batch_results/<anchor>_<instance_id[:8]>/ on
local. Closes the NO_METRICS gap where script outputs at custom paths
were never preserved.

All 3 safety layers from launch_experiment.py:
  1. terminate retry with backoff + leak flag (single terminate at end
     OR on any signal mid-batch)
  2. always-verbose remote dispatch (set -ex + python -u + stdbuf + tee)
  3. pre-launch snapshot + 5xx retry + orphan reconcile (once)

Per-anchor: ProgressPoller spawned for each, runs while that anchor's
SSH dispatch is in flight, then stops before the next.

Exit codes:
  0  all experiments ran to completion (each rc=0)
  1  fatal error pre-batch (launch/ssh/bootstrap)
  2  one or more experiments returned non-zero rc; batch still cleanly
     terminated; per-anchor reports indicate which
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import LambdaClient, LambdaClientError  # noqa: E402
from tools.cloud.cost_tracker import update_cost, accumulate_run_cost  # noqa: E402


_TERMINATE_STATE: dict = {"client": None, "instance_ids": [], "done": False}
_PROGRESS_POLL_INTERVAL_S = 30
_DEFAULT_CELL_REGEX = (
    r"^\s+(?:M=\d+\s+d=\d+\s+)?seed=\d+\s+(?:ok=|acc=|FAILED:)"
)


def _load_key(key_file_arg: str) -> str | None:
    key = os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
    if key:
        return key
    kp = Path(key_file_arg)
    if not kp.is_absolute():
        kp = _REPO_ROOT / kp
    if not kp.is_file():
        return None
    for ln in kp.read_text(encoding="utf-8").splitlines():
        if ln.startswith("LAMBDA_CLOUD_API_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v
    return None


def _force_terminate():
    """Single terminate at batch end OR on signal. Retry w/ backoff + leak flag."""
    if _TERMINATE_STATE["done"] or not _TERMINATE_STATE["client"]:
        return
    if not _TERMINATE_STATE["instance_ids"]:
        _TERMINATE_STATE["done"] = True
        return
    ids = list(_TERMINATE_STATE["instance_ids"])
    backoff = 1.0
    last_exc = None
    for attempt in range(6):
        try:
            terminated = _TERMINATE_STATE["client"].terminate_instances(ids)
            print(f"[launch_batch] cleanup attempt {attempt+1}: terminated {terminated}",
                  flush=True)
            _TERMINATE_STATE["done"] = True
            return
        except Exception as exc:
            last_exc = exc
            print(f"[launch_batch] cleanup attempt {attempt+1} failed: {exc}",
                  flush=True)
            if attempt < 5:
                print(f"  retrying in {backoff:.0f}s...", flush=True)
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
    print(f"[launch_batch] CLEANUP EXHAUSTED RETRIES: {last_exc}", flush=True)
    print(f"  Instance ids: {ids}; MANUALLY TERMINATE", flush=True)
    try:
        flag = _REPO_ROOT / "data" / f"lambda_LEAKED_instance_{ids[0]}.flag"
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(
            json.dumps({"instance_ids": ids,
                        "leaked_at": datetime.now(timezone.utc).isoformat(),
                        "last_error": str(last_exc)}, indent=2),
            encoding="utf-8")
        print(f"  leak flag: {flag}", flush=True)
    except Exception:
        pass
    _TERMINATE_STATE["done"] = True


def _signal_handler(signum, frame):
    print(f"[launch_batch] signal {signum}; cleanup", flush=True)
    _force_terminate()
    sys.exit(130)


def _ssh_run(ip: str, key: str | None, cmd: str, timeout_s: float) -> tuple[int, str, str]:
    base = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=15",
        "-o", "LogLevel=ERROR",
        # PHASE 0.5 FIX (Dispatch 14 post-mortem): SSH session died with
        # 'Connection reset by peer' 13 min into Wave 1's 60-90 min ingest.
        # Some intermediate network layer was killing idle SSH sessions.
        # Keepalive: send 60s probes; tolerate 60 missed responses (60 min
        # gap before declaring connection dead). Anchor experiments can now
        # run silently for up to 60 min without the launcher SSH dropping.
        # TCPKeepAlive is OS-level (sends TCP keepalive packets in addition
        # to SSH's own ServerAlive pings).
        "-o", "ServerAliveInterval=60",
        "-o", "ServerAliveCountMax=60",
        "-o", "TCPKeepAlive=yes",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}")
    base.append(cmd)
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout_s,
        )
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"timeout {timeout_s}s")
    except Exception as exc:
        return (-1, "", str(exc))


def _scp_from(ip: str, key: str | None, remote: str, local: Path) -> bool:
    base = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}:{remote}")
    base.append(str(local))
    try:
        proc = subprocess.run(base, capture_output=True, text=True, timeout=120)
        return proc.returncode == 0
    except Exception:
        return False


def _scp_to(ip: str, key: str | None, local: Path, remote: str) -> bool:
    """Upload a local file to ubuntu@ip:remote. Returns True on success.

    Used by Phase 0.5 dispatch to seed .hf_token + bring-up script + (when
    re-using cached Wave 1 artifacts) probe_ckpt/codebook/metrics onto the
    instance before the first anchor runs.

    Pre-mkdir's the remote parent directory via ssh so scp doesn't fail on
    cached-artifact uploads to paths like data/exp_phase05_probe_training_v1/
    which don't exist on a fresh-bootstrapped instance.

    Auto-scales timeout for large files (1 GB at ~50 MB/s = 20s; budget 600s
    for files > 100 MB).
    """
    # mkdir -p remote parent (idempotent)
    parent = remote.rsplit("/", 1)[0] if "/" in remote else None
    if parent:
        mkdir_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=30",
        ]
        if key:
            mkdir_cmd.extend(["-i", key])
        mkdir_cmd.append(f"ubuntu@{ip}")
        mkdir_cmd.append(f"mkdir -p {parent}")
        try:
            subprocess.run(mkdir_cmd, capture_output=True, text=True, timeout=30)
        except Exception:
            pass  # best-effort; scp will fail audibly if parent missing
    # Estimate timeout from file size
    try:
        size_mb = local.stat().st_size / (1024 * 1024)
    except Exception:
        size_mb = 1.0
    scp_timeout = 120 if size_mb < 100 else 600
    base = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.append(str(local))
    base.append(f"ubuntu@{ip}:{remote}")
    try:
        proc = subprocess.run(base, capture_output=True, text=True, timeout=scp_timeout)
        if proc.returncode != 0:
            print(f"  [scp_to] FAILED rc={proc.returncode} stderr={proc.stderr[:300]}")
        return proc.returncode == 0
    except Exception as e:
        print(f"  [scp_to] EXC {e}")
        return False


def _scp_recursive_from(ip: str, key: str | None, remote: str, local: Path,
                        timeout_s: int = 300) -> tuple[bool, str]:
    """Recursively SCP a remote path (file or directory) to a local path.

    Returns (success, message). The local target's parent is created if needed.
    Uses scp -r for directories; plain scp for files.
    """
    local.parent.mkdir(parents=True, exist_ok=True)
    base = [
        "scp", "-r",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}:{remote}")
    base.append(str(local))
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True, timeout=timeout_s)
        if proc.returncode == 0:
            return True, "ok"
        return False, (proc.stderr or proc.stdout or f"rc={proc.returncode}")[:200]
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout_s}s"
    except Exception as exc:
        return False, str(exc)[:200]


def _ssh_glob(ip: str, key: str | None, pattern: str) -> list[str]:
    """List remote paths matching `pattern` (relative to ~/hd-instrument/).

    Uses a shell-evaluated glob expansion on the remote so callers can pass
    patterns like `data/testbed_pp8_week2/*.json`. Returns absolute paths.
    """
    cmd = (
        f"cd ~/hd-instrument && "
        f"for f in {pattern}; do "
        f"  [ -e \"$f\" ] && echo \"$HOME/hd-instrument/$f\"; "
        f"done"
    )
    base = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.extend([f"ubuntu@{ip}", cmd])
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return []
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _scp_back_result_paths(
    ip: str, key: str | None, instance_id: str, anchor: str,
    result_paths: list[str], local_base: Path,
) -> list[dict[str, Any]]:
    """SCP-back a list of result patterns from the remote to local.

    `result_paths` is a list of patterns relative to ~/hd-instrument/ on the
    remote (e.g. "data/testbed_pp8_week2/phi3_qformer_wiring_cuda.json" or
    "data/testbed_pp8_week2/train_v1/*"). Glob expansion happens on the remote.

    Returns a list of per-path dicts {"pattern", "matches", "results": [...]}.
    Each result is {"remote": str, "local": str, "ok": bool, "msg": str}.
    """
    summary: list[dict[str, Any]] = []
    if not result_paths:
        return summary
    print(f"  [scp-back] declared result_paths ({len(result_paths)}):")
    for pattern in result_paths:
        remote_matches = _ssh_glob(ip, key, pattern)
        entry: dict[str, Any] = {
            "pattern": pattern,
            "matches": len(remote_matches),
            "results": [],
        }
        if not remote_matches:
            print(f"    {pattern}: no matches on remote")
            summary.append(entry)
            continue
        for remote in remote_matches:
            # Mirror the remote subpath under local_base, keyed by anchor +
            # instance_id so multiple anchors don't collide.
            # remote is absolute: /home/ubuntu/hd-instrument/data/...
            try:
                rel = remote.split("hd-instrument/", 1)[1]
            except IndexError:
                rel = Path(remote).name
            local_dest = local_base / f"{anchor}_{instance_id[:8]}" / rel
            ok, msg = _scp_recursive_from(ip, key, remote, local_dest)
            entry["results"].append({
                "remote": remote,
                "local": str(local_dest),
                "ok": ok,
                "msg": msg if not ok else "ok",
            })
            print(f"    {remote} -> {local_dest}: {'OK' if ok else 'FAIL: ' + msg}")
        summary.append(entry)
    return summary


class ProgressPoller(threading.Thread):
    """Same shape as launch_experiment's ProgressPoller; runs per anchor."""

    def __init__(self, ip, ssh_key_path, instance_id, anchor, stop_event,
                 poll_interval_s=_PROGRESS_POLL_INTERVAL_S):
        super().__init__(daemon=True, name=f"progress-poller-{anchor}")
        self.ip = ip
        self.ssh_key_path = ssh_key_path
        self.instance_id = instance_id
        self.anchor = anchor
        self.stop_event = stop_event
        self.poll_interval_s = poll_interval_s
        self.remote_path = f"~/hd-instrument/data/exp_{anchor}/progress.json"
        self.local_path = (
            _REPO_ROOT / "data" / f"lambda_progress_{anchor}_{instance_id}.json"
        )
        self._last_cell: int | None = None

    def run(self):
        if self.stop_event.wait(timeout=10):
            return
        while not self.stop_event.is_set():
            try:
                self._poll_once()
            except Exception as exc:
                print(f"[progress-poller] error (continuing): {exc}", flush=True)
            if self.stop_event.wait(timeout=self.poll_interval_s):
                break

    def _poll_once(self):
        tmp = self.local_path.with_suffix(self.local_path.suffix + ".tmp")
        if not _scp_from(self.ip, self.ssh_key_path, self.remote_path, tmp):
            return
        if not tmp.is_file():
            return
        try:
            entry = json.loads(tmp.read_text(encoding="utf-8"))
        except Exception:
            tmp.unlink(missing_ok=True)
            return
        os.replace(str(tmp), str(self.local_path))
        cell = entry.get("cell")
        total = entry.get("total_cells")
        phase = entry.get("phase") or ""
        eta = entry.get("eta_sec")
        if cell is None or total is None or cell == self._last_cell:
            return
        self._last_cell = int(cell)
        pct = (cell / total * 100) if total else 0
        eta_str = f"ETA {eta}s" if eta is not None else "ETA -"
        ts = datetime.now().astimezone().strftime("%H:%M:%S")
        print(f"[progress {ts}] {self.anchor} cell {cell}/{total}  "
              f"({pct:.1f}%)  {phase}  {eta_str}", flush=True)


def _launch_detached(ip: str, ssh_key_path: str | None, anchor: str,
                      script: str, total_cells: int, cell_regex: str,
                      script_args: str, remote_anchor_dir: str) -> tuple[bool, str, str]:
    """Start the experiment as a nohup-detached process on the remote.

    Architecture (Dispatch 15 post-mortem; agent's "fire-and-poll" pattern):
      - The experiment runs in `nohup bash -c '<body>' > log 2>&1 < /dev/null & disown`
      - The body writes its exit code to <REMOTE_OUT>/exp.rc as its final action
      - We capture the background PID and write it to <REMOTE_OUT>/exp.pid
      - All subsequent monitoring is done via SHORT polling SSH calls
        (no long-lived foreground connection that intermediate NATs can drop)

    Returns (success, pid_str, error_msg). On success, the experiment is
    running detached; SSH disconnect / network blip has NO effect on it.
    """
    regex_escaped = cell_regex.replace("'", "'\\''")
    script_args_escaped = script_args.replace("'", "'\\''") if script_args else ""
    target_cmd = (
        f"$PY -u tools/cloud/generic_progress_wrapper.py "
        f"--anchor {anchor} "
        f"--script {script} "
        f"--total-cells {total_cells} "
        f"--cell-regex '{regex_escaped}'"
        + (f" --script-args '{script_args_escaped}'" if script_args else "")
    )
    # The experiment body. Runs inside a nohup'd bash subshell so SIGHUP
    # cannot kill it on SSH disconnect.
    #
    # CRITICAL: use 'trap ... EXIT' to write exp.rc on ANY exit path (success,
    # error, signal). Dispatch 16 lesson: 'set -e' aborts the body when the
    # experiment exits non-zero, so the subsequent 'echo $? > exp.rc' never
    # runs and the poll loop reports DEAD_NO_RC. The trap fires unconditionally.
    body = (
        f"REMOTE_OUT={remote_anchor_dir}; "
        # Trap writes exp.rc on ANY exit (success, error, signal, set -e abort).
        # Dispatch 17 lesson: keep this trap MINIMAL -- just one command, no
        # auxiliary echos. Earlier multi-command trap had an EXP_EXIT echo
        # that succeeded but the file write somehow didn't. One command means
        # one possible failure point.
        "trap 'echo $? > $REMOTE_OUT/exp.rc' EXIT; "
        "cd ~/hd-instrument; "
        "git pull --ff-only > /dev/null 2>&1 || true; "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        "if [ -f .hf_token ]; then export HF_TOKEN=$(cat .hf_token); fi; "
        "export HDLAB_RUN_MODE=full; "
        "export CUBLAS_WORKSPACE_CONFIG=:4096:8; "
        "echo \"--- env ---\"; "
        "$PY --version; "
        "free -h | head -2; "
        "echo \"--- dispatch ---\"; "
        f"stdbuf -oL {target_cmd} 2>&1; "
        "EXP_RC=$?; "
        "echo \"--- result ---\"; "
        f"if [ -f $REMOTE_OUT/metrics.json ]; then "
        "  echo \"METRICS_OK\"; "
        "  ls -la $REMOTE_OUT/metrics.json; "
        "else "
        "  echo \"NO_METRICS\"; "
        "fi; "
        # Explicit exit triggers the trap with the experiment's rc
        "exit $EXP_RC"
    )
    # Escape single quotes inside body for outer single-quote wrapping
    body_escaped = body.replace("'", "'\\''")
    launch_cmd = (
        f"mkdir -p {remote_anchor_dir} && "
        f"rm -f {remote_anchor_dir}/exp.rc {remote_anchor_dir}/exp.pid && "
        f"nohup bash -c '{body_escaped}' > {remote_anchor_dir}/exp_run.log 2>&1 < /dev/null & "
        f"disown; "
        f"echo $! > {remote_anchor_dir}/exp.pid; "
        f"echo PID=$!"
    )
    # Bumped 60s -> 180s. Dispatch 16 Wave 1 launch SSH timed out at 60s on
    # this very call (transient network blip; Wave 2 launched cleanly on the
    # same instance). 180s budget accommodates SSH handshake + multi-line
    # body parse + nohup spawn even under slow-network conditions.
    #
    # Dispatch 17 confirmed pattern: Wave 1 launch on a fresh instance
    # hits a SYSTEMATIC cold-start delay (~3-5min) on the first SSH after
    # bring-up; subsequent SSHs work. Add retry with backoff -- the second
    # attempt typically succeeds because Lambda's SSH listener warmed up.
    last_err = ""
    for attempt in range(1, 4):
        rc, out, err = _ssh_run(ip, ssh_key_path, launch_cmd, timeout_s=180)
        if rc == 0:
            break
        last_err = f"attempt {attempt}/3: rc={rc} stderr={err[:200]}"
        print(f"  [launch] {anchor} ssh attempt {attempt}/3 failed: {last_err}; "
              f"sleeping 20s then retrying", flush=True)
        if attempt < 3:
            time.sleep(20)
    if rc != 0:
        return False, "", f"launch ssh failed 3x: {last_err}"
    pid = None
    for line in (out or "").splitlines():
        line = line.strip()
        if line.startswith("PID="):
            pid = line.split("=", 1)[1].strip()
            break
    if not pid or not pid.isdigit():
        return False, "", f"could not parse PID from launch output: {out[:500]!r}"
    return True, pid, ""


def _poll_for_completion(ip: str, ssh_key_path: str | None, anchor: str,
                          remote_anchor_dir: str, pid: str,
                          timeout_min: float,
                          poll_interval_s: float = 30.0) -> tuple[int, str]:
    """Poll the remote until experiment completes, dies, or timeout fires.

    Returns (rc, reason).
      rc >= 0: experiment finished with that exit code (read from exp.rc)
      rc == -1: ssh polling failed repeatedly (>5 consecutive)
      rc == -2: process died without writing exp.rc (crash without sentinel)
      rc == -3: wall-clock timeout; remote process force-killed via SIGKILL

    Streams log deltas to local stdout for visibility during the run.
    """
    deadline = time.time() + timeout_min * 60.0
    last_log_size = 0
    consecutive_ssh_failures = 0
    last_progress_print_ts = 0.0
    while time.time() < deadline:
        # Probe: rc file present? process alive? current log size?
        probe = (
            f"if [ -f {remote_anchor_dir}/exp.rc ]; then "
            f"  echo \"DONE=$(cat {remote_anchor_dir}/exp.rc)\"; "
            f"elif kill -0 {pid} 2>/dev/null; then "
            f"  echo \"ALIVE\"; "
            f"  stat -c %s {remote_anchor_dir}/exp_run.log 2>/dev/null || echo 0; "
            f"else "
            f"  echo \"DEAD_NO_RC\"; "
            f"fi"
        )
        rc, out, err = _ssh_run(ip, ssh_key_path, probe, timeout_s=30)
        if rc != 0:
            consecutive_ssh_failures += 1
            print(f"  [poll] SSH probe failed (attempt {consecutive_ssh_failures}/5): "
                  f"rc={rc} err={err[:120]!r}", flush=True)
            if consecutive_ssh_failures >= 5:
                return -1, f"ssh polling failed 5 consecutive times"
            time.sleep(min(poll_interval_s, 10.0))
            continue
        consecutive_ssh_failures = 0
        lines = (out or "").strip().splitlines()
        if not lines:
            time.sleep(poll_interval_s)
            continue
        first = lines[0].strip()
        if first.startswith("DONE="):
            rc_str = first.split("=", 1)[1].strip()
            try:
                exp_rc = int(rc_str)
            except ValueError:
                exp_rc = 99
            # Flush final log delta to local stdout
            _stream_log_delta(ip, ssh_key_path, remote_anchor_dir,
                              last_log_size, anchor)
            return exp_rc, "done"
        if first == "DEAD_NO_RC":
            _stream_log_delta(ip, ssh_key_path, remote_anchor_dir,
                              last_log_size, anchor)
            return -2, "remote process died without writing exp.rc"
        if first == "ALIVE":
            # Optionally stream log delta if grew
            try:
                cur_size = int(lines[1].strip()) if len(lines) > 1 else 0
            except ValueError:
                cur_size = 0
            if cur_size > last_log_size:
                _stream_log_delta(ip, ssh_key_path, remote_anchor_dir,
                                  last_log_size, anchor, end_byte=cur_size)
                last_log_size = cur_size
            # Heartbeat every 5 minutes if no log progress
            now = time.time()
            if now - last_progress_print_ts > 300:
                print(f"  [poll] {anchor} alive (pid {pid}, log size {cur_size}); "
                      f"elapsed {int((now - (deadline - timeout_min*60))/60)}min", flush=True)
                last_progress_print_ts = now
            time.sleep(poll_interval_s)
            continue
        time.sleep(poll_interval_s)
    # Wall-clock timeout: kill remote process
    print(f"  [poll] {anchor} hit wall-clock timeout {timeout_min}min; killing pid {pid}",
          flush=True)
    _ssh_run(ip, ssh_key_path, f"kill -9 {pid} 2>/dev/null || true", timeout_s=30)
    return -3, f"wall-clock timeout {timeout_min}min"


def _stream_log_delta(ip: str, ssh_key_path: str | None,
                       remote_anchor_dir: str, start_byte: int,
                       anchor: str, end_byte: int | None = None) -> None:
    """Print remote log bytes [start_byte:end_byte] to local stdout."""
    if end_byte is not None and end_byte <= start_byte:
        return
    if end_byte is not None:
        count = end_byte - start_byte
        cmd = (f"dd if={remote_anchor_dir}/exp_run.log "
               f"bs=1 skip={start_byte} count={count} 2>/dev/null")
        timeout = max(120, count // 1_000_000 * 30)  # 30s per MB
    else:
        cmd = (f"if [ -f {remote_anchor_dir}/exp_run.log ]; then "
               f"  dd if={remote_anchor_dir}/exp_run.log bs=1 skip={start_byte} 2>/dev/null; "
               f"fi")
        timeout = 300
    rc, out, err = _ssh_run(ip, ssh_key_path, cmd, timeout_s=timeout)
    if rc == 0 and out:
        # cp1252 safety on Windows stdout
        safe = out.encode("ascii", errors="replace").decode("ascii")
        sys.stdout.write(safe)
        sys.stdout.flush()


def _run_one_anchor(ip, ssh_key_path, anchor, script, total_cells,
                    cell_regex, instance_id, experiment_timeout_min,
                    result_paths: list[str] | None = None,
                    script_args: str = ""):
    """Dispatch one anchor as a DETACHED remote process; poll for completion.

    Detached architecture (Dispatch 15 post-mortem):
      1. _launch_detached: SHORT SSH call launches the experiment under nohup;
         body writes to exp_run.log and finishes by writing exit code to
         exp.rc. Disown ensures SIGHUP from SSH disconnect cannot kill it.
      2. _poll_for_completion: SHORT SSH calls every 30s check for exp.rc /
         liveness / log delta. Streams new log bytes to local stdout. SSH
         disconnect / network blip during polling triggers retry, not failure.
      3. SCP back metrics.json, exp_run.log, progress.json, + declared
         result_paths.

    Returns (rc, metrics_local_path).
    """
    remote_anchor_dir = f"data/exp_{anchor}"

    # Step 1: launch detached
    print(f"  [launch] {anchor}: starting detached on remote ...", flush=True)
    ok, pid, err = _launch_detached(
        ip, ssh_key_path, anchor, script, total_cells, cell_regex,
        script_args, remote_anchor_dir,
    )
    if not ok:
        print(f"  [launch] FAILED: {err}", flush=True)
        rc = -1
    else:
        print(f"  [launch] pid={pid}; polling for completion (timeout "
              f"{experiment_timeout_min:.0f}min, 30s interval)", flush=True)
        # Step 2: poll for completion
        rc, reason = _poll_for_completion(
            ip, ssh_key_path, anchor, remote_anchor_dir, pid,
            timeout_min=experiment_timeout_min,
        )
        print(f"  [poll] {anchor} finished: rc={rc} ({reason})", flush=True)

    out = ""  # backwards-compat with local-log-file code below
    err = ""
    print(f"---- {anchor} exit: {rc} ----")
    metrics_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_metrics_{instance_id}.json"
    if _scp_from(ip, ssh_key_path,
                 f"~/hd-instrument/{remote_anchor_dir}/metrics.json",
                 metrics_local):
        print(f"  metrics: {metrics_local}")
    remote_log_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_remote_log_{instance_id}.log"
    _scp_from(ip, ssh_key_path,
              f"~/hd-instrument/{remote_anchor_dir}/exp_run.log",
              remote_log_local)
    progress_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_progress_final_{instance_id}.json"
    _scp_from(ip, ssh_key_path,
              f"~/hd-instrument/{remote_anchor_dir}/progress.json",
              progress_local)

    # Declared-result-paths SCP-back (closes Phase 1's NO_METRICS gap where
    # the experiment's output JSON existed on the remote but was never pulled
    # because the standard metrics.json scrape didn't match its path).
    result_paths_summary: list[dict[str, Any]] = []
    if result_paths:
        local_base = _REPO_ROOT / "data" / "lambda_batch_results"
        result_paths_summary = _scp_back_result_paths(
            ip, ssh_key_path, instance_id, anchor, result_paths, local_base,
        )
        # Persist the summary so the batch report can reference what was pulled
        summary_path = (local_base / f"{anchor}_{instance_id[:8]}"
                        / "result_paths_summary.json")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(result_paths_summary, indent=2), encoding="utf-8")

    return rc, metrics_local


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description="Stringed Lambda batch launcher")
    parser.add_argument("--batch", required=True,
                        help="Path to JSON batch config (list of anchor dicts)")
    parser.add_argument("--ssh-key-name", required=True)
    parser.add_argument("--ssh-key-path", required=True)
    parser.add_argument("--key-file", default=".env.lambda")
    parser.add_argument("--instance-type", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--max-cost-usd", type=float, default=5.0)
    parser.add_argument("--expected-wall-min", type=float, default=45.0)
    parser.add_argument("--budget-cap-usd", type=float, default=10.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--default-experiment-timeout-min", type=float, default=60.0)
    parser.add_argument("--wait-for-capacity-max-s", type=float, default=3600.0,
                        help="Max time to poll Lambda catalog for capacity "
                             "BEFORE attempting launch_instance. Zero billable "
                             "cost during this wait. Default 3600s (1 hour).")
    parser.add_argument("--capacity-poll-interval-s", type=float, default=30.0,
                        help="Catalog poll interval during capacity-wait.")
    parser.add_argument("--stuck-booting-max-s", type=float, default=300.0,
                        help="If instance status stays `booting` for this many "
                             "seconds without progress, terminate fast-fail. "
                             "Caps wasted boot billing at "
                             "~rate * stuck_booting_max_s (e.g., $4.29/hr H100 "
                             "* 300s = $0.36 vs $1.07 at 900s default). "
                             "Default 300s (5 min).")
    parser.add_argument("--upload-file", action="append", default=[],
                        help="Repeatable: 'local_path:remote_path'. SCP'd to the "
                             "instance after bootstrap, before first anchor. "
                             "Use for secrets / config files that should NOT be "
                             "in the git repo (e.g., .hf_token).")
    parser.add_argument("--post-bootstrap-script", default=None,
                        help="Path to a local bash script SCP'd to the instance "
                             "after bootstrap and executed once before anchors. "
                             "Receives HF_TOKEN via env if .hf_token uploaded.")
    args = parser.parse_args()

    batch_path = Path(args.batch)
    if not batch_path.is_absolute():
        batch_path = _REPO_ROOT / batch_path
    if not batch_path.is_file():
        print(f"[ERROR] batch config not found: {batch_path}")
        return 1
    try:
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] batch JSON parse: {exc}")
        return 1
    if not isinstance(batch, list) or not batch:
        print(f"[ERROR] batch must be non-empty JSON list")
        return 1
    for i, b in enumerate(batch):
        for required in ("anchor", "script", "total_cells"):
            if required not in b:
                print(f"[ERROR] batch[{i}] missing '{required}'")
                return 1
        try:
            re.compile(b.get("cell_regex", _DEFAULT_CELL_REGEX))
        except re.error as exc:
            print(f"[ERROR] batch[{i}] invalid cell_regex: {exc}")
            return 1

    api_key = _load_key(args.key_file)
    if not api_key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY")
        return 1
    try:
        client = LambdaClient(api_key=api_key)
    except LambdaClientError as exc:
        print(f"[ERROR] {exc}")
        return 1
    _TERMINATE_STATE["client"] = client

    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog: {exc}")
        return 1
    with_cap = [t for t in catalog if t.regions_available]
    with_cap.sort(key=lambda t: t.price_cents_per_hour)
    if args.instance_type:
        # Explicit type: look up in FULL catalog so we can fall through to the
        # wait_for_capacity gate even when current capacity is zero. This is
        # the whole point of having the gate -- capacity often becomes
        # available within minutes; we should not error out instantly.
        target = next((t for t in catalog if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] {args.instance_type} not in Lambda catalog at all")
            return 1
        if not target.regions_available:
            print(f"  {args.instance_type} has no current capacity; "
                  f"will poll via wait_for_capacity gate")
    else:
        if not with_cap:
            print("[ERROR] no capacity for ANY instance type")
            return 1
        target = with_cap[0]
    predicted = target.hourly_rate_usd * (args.expected_wall_min / 60.0)

    print("=" * 70)
    print(f"Batch launcher: {len(batch)} anchor(s)")
    print("=" * 70)
    for i, b in enumerate(batch):
        print(f"  [{i+1}/{len(batch)}] {b['anchor']} ({b['total_cells']} cells)")
    print(f"  Instance type:       {target.name}")
    print(f"  Region preference:   {args.region or 'ANY (first available)'}")
    print(f"  Rate:                ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min (entire batch)")
    print(f"  PREDICTED COST:      ${predicted:.2f}")
    print(f"  Max-cost cap:        ${args.max_cost_usd:.2f}")
    if predicted > args.max_cost_usd:
        print(f"\n[REFUSE] ${predicted:.2f} > cap ${args.max_cost_usd:.2f}")
        return 1

    atexit.register(_force_terminate)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
    except (AttributeError, ValueError):
        pass

    # Pre-flight capacity gate: confirm target type has regions_available
    # BEFORE we make a billable launch call. Returns the available regions
    # at the moment capacity was seen; we use the FIRST one for launch so
    # there's no stale-region-cache risk if capacity shifted during the wait.
    print(f"\n[0/3] Verifying capacity for {target.name} "
          f"(region preference={args.region or 'ANY'}; "
          f"max wait {args.wait_for_capacity_max_s:.0f}s; zero billable cost)...")
    try:
        available_regions = client.wait_for_capacity(
            instance_type_name=target.name,
            regions=[args.region] if args.region else None,
            max_wait_s=args.wait_for_capacity_max_s,
            poll_interval_s=args.capacity_poll_interval_s,
            verbose=True,
        )
    except LambdaClientError as exc:
        print(f"[ERROR] capacity gate: {exc}")
        return 1
    # Use FRESH capacity result, not the cached target.regions_available
    # from the initial catalog query (which may have gone stale during wait).
    region = available_regions[0]
    print(f"  Selected region for launch: {region}")

    print(f"\n[1/3] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)

    def _snapshot() -> set[str]:
        try:
            return {i.instance_id for i in client.list_instances()
                    if i.status in ("active", "booting", "terminating", "unhealthy")}
        except Exception:
            return set()

    pre_ids = _snapshot()
    print(f"  pre-launch active on account: {len(pre_ids)}")
    new_ids: list[str] = []
    last_exc = None
    backoff = 2.0
    for attempt in range(3):
        try:
            new_ids = client.launch_instance(
                region_name=region,
                instance_type_name=target.name,
                ssh_key_names=[args.ssh_key_name],
                quantity=1,
                name=f"batch-{batch[0]['anchor'][:24]}",
            )
            if new_ids:
                break
        except LambdaClientError as exc:
            last_exc = exc
            transient = any(c in str(exc) for c in (" 502 ", " 503 ", " 504 "))
            print(f"  attempt {attempt+1} failed: {exc}")
            if not transient:
                break
            if attempt < 2:
                time.sleep(backoff); backoff *= 2
    time.sleep(5)
    post_ids = _snapshot()
    orphan_ids = sorted(post_ids - pre_ids - set(new_ids))
    all_ours = list(set(new_ids) | set(orphan_ids))
    if orphan_ids:
        print(f"  reconciled {len(orphan_ids)} orphan(s): {orphan_ids}")
    if not all_ours:
        print(f"[ERROR] no instance (last_error={last_exc!r})")
        return 1
    _TERMINATE_STATE["instance_ids"] = all_ours
    instance_id = new_ids[0] if new_ids else orphan_ids[0]
    print(f"  launched: {instance_id} (tracked: {len(all_ours)})")

    print(f"[wait] Waiting for active (stuck-booting fast-fail at "
          f"{args.stuck_booting_max_s:.0f}s)...")
    try:
        inst = client.wait_for_active(
            instance_id, timeout_s=args.stuck_booting_max_s)
    except LambdaClientError as exc:
        print(f"[ERROR] {exc}")
        return 1
    print(f"  active: ip={inst.ip}")
    ip = inst.ip
    update_cost(
        current_hourly_rate_usd=inst.hourly_rate_usd,
        active_instances=[{
            "instance_id": instance_id,
            "instance_type": target.name,
            "hourly_rate_usd": inst.hourly_rate_usd,
            "started_at": launch_ts.isoformat(),
        }],
    )

    print(f"\n[2/3] Bootstrapping {instance_id} (ONCE for entire batch)...")
    boot_cmd = [
        sys.executable,
        str(_REPO_ROOT / "tools" / "cloud" / "bootstrap_instance.py"),
        instance_id,
        "--ssh-key-path", args.ssh_key_path,
        "--repo-url", args.repo_url,
        "--branch", args.branch,
    ]
    try:
        result = subprocess.run(
            boot_cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=2700,
        )
        print(result.stdout)
        if result.stderr:
            print(f"---- bootstrap stderr ----\n{result.stderr[-1500:]}",
                  file=sys.stderr)
        boot_ok = (result.returncode == 0)
    except Exception as exc:
        print(f"  [ERROR] bootstrap: {exc}")
        boot_ok = False
    if not boot_ok:
        print(f"\n[ERROR] bootstrap failed; aborting")
        return 1

    # Optional post-bootstrap upload + script (Phase 0.5 HF token + bring-up).
    if args.upload_file:
        print(f"\n[2.5/3] Uploading {len(args.upload_file)} file(s) post-bootstrap...")
        for spec in args.upload_file:
            if ":" not in spec:
                print(f"  [WARN] --upload-file '{spec}' missing ':'; skipping")
                continue
            local_path, remote_path = spec.split(":", 1)
            local_p = Path(local_path)
            if not local_p.is_absolute():
                local_p = _REPO_ROOT / local_p
            if not local_p.exists():
                print(f"  [ERROR] local file not found: {local_p}")
                return 1
            print(f"  scp {local_p.name} -> ubuntu@{ip}:{remote_path}")
            if not _scp_to(ip, args.ssh_key_path, local_p, remote_path):
                print(f"  [ERROR] upload failed for {local_p}")
                return 1

    if args.post_bootstrap_script:
        script_local = Path(args.post_bootstrap_script)
        if not script_local.is_absolute():
            script_local = _REPO_ROOT / script_local
        if not script_local.exists():
            print(f"[ERROR] post-bootstrap script not found: {script_local}")
            return 1
        remote_script = f"/home/ubuntu/{script_local.name}"
        print(f"\n[2.75/3] Post-bootstrap script: {script_local.name}")
        print(f"  scp {script_local.name} -> ubuntu@{ip}:{remote_script}")
        if not _scp_to(ip, args.ssh_key_path, script_local, remote_script):
            print(f"  [ERROR] post-bootstrap script upload failed")
            return 1
        # Source .hf_token to export HF_TOKEN before script runs (if uploaded).
        post_cmd = (
            f"chmod +x {remote_script}; "
            f"if [ -f ~/hd-instrument/.hf_token ]; then "
            f"  export HF_TOKEN=$(cat ~/hd-instrument/.hf_token); "
            f"fi; "
            f"bash {remote_script}"
        )
        try:
            rc, out, err = _ssh_run(ip, args.ssh_key_path, post_cmd, timeout_s=1800)
            _safe_out = (out[-3000:] or "").encode("ascii", errors="replace").decode("ascii")
            _safe_err = (err[-1500:] or "").encode("ascii", errors="replace").decode("ascii")
            print(_safe_out)
            if err:
                print(f"---- post-bootstrap stderr ----\n{_safe_err}")
            print(f"---- post-bootstrap exit: {rc} ----")
            if rc != 0:
                print(f"\n[ERROR] post-bootstrap script exit rc={rc}; aborting")
                return 1
        except Exception as e:
            print(f"[ERROR] post-bootstrap script failed: {e}")
            return 1

    print(f"\n[3/3] Dispatching {len(batch)} experiments sequentially...")
    rcs: list[tuple[str, int, Path | None]] = []
    for i, b in enumerate(batch):
        timeout = b.get("experiment_timeout_min", args.default_experiment_timeout_min)
        cell_regex = b.get("cell_regex", _DEFAULT_CELL_REGEX)
        print(f"\n=== [{i+1}/{len(batch)}] {b['anchor']} "
              f"({b['total_cells']} cells, {timeout:.0f}m timeout) ===")
        result_paths = b.get("result_paths") or []
        script_args = b.get("script_args", "")
        rc, metrics_path = _run_one_anchor(
            ip=ip, ssh_key_path=args.ssh_key_path,
            anchor=b["anchor"], script=b["script"],
            total_cells=int(b["total_cells"]),
            cell_regex=cell_regex,
            instance_id=instance_id,
            experiment_timeout_min=timeout,
            result_paths=result_paths,
            script_args=script_args,
        )
        rcs.append((b["anchor"], rc, metrics_path if metrics_path and metrics_path.is_file() else None))
        # Per-anchor abort-on-failure gate (Phase 0.5 probe-validation use case):
        # if a gating anchor declares abort_batch_on_failure=True and exited
        # non-zero, stop the batch before running downstream anchors that depend
        # on its artifacts.
        if rc != 0 and bool(b.get("abort_batch_on_failure", False)):
            print(f"\n[abort] {b['anchor']} exited rc={rc} and "
                  f"abort_batch_on_failure=True; skipping remaining "
                  f"{len(batch) - (i + 1)} anchor(s) and terminating instance.")
            break

    print(f"\n[terminate]")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)
    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)

    print()
    print("=" * 70)
    print(f"Batch report: {len(batch)} anchor(s)")
    print("=" * 70)
    print(f"  Predicted:     ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:   {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:   ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:         ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  Bootstrap pay-once savings: ~${0.13 * (len(batch) - 1):.2f} + "
          f"~{5 * (len(batch) - 1)}m wall vs N separate launches")
    print()
    for anchor, rc, mp in rcs:
        status = "OK" if rc == 0 else f"rc={rc}"
        mpath = str(mp) if mp else "MISSING"
        print(f"  [{status:>6}] {anchor}: {mpath}")

    update_cost(current_hourly_rate_usd=0.0, active_instances=[])
    new_total = accumulate_run_cost(actual_cost)
    print(f"  Cumulative today: ${new_total:.2f}")

    report = {
        "batch_size": len(batch),
        "anchors": [a for a, _, _ in rcs],
        "instance_id": instance_id,
        "instance_type": target.name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "experiment_rcs": [{"anchor": a, "rc": rc,
                            "metrics": str(mp) if mp else None}
                           for a, rc, mp in rcs],
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    rp = _REPO_ROOT / "data" / f"lambda_batch_report_{instance_id}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  Report: {rp}")

    all_clean = all(rc == 0 for _, rc, _ in rcs)
    return 0 if all_clean else 2


if __name__ == "__main__":
    sys.exit(main())
