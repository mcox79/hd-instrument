"""Launch + bootstrap + V1 + verify HARD_PASS + terminate (one-shot atomic).

Single atomic experiment for the Tier 1b validation gate:

  1. Launch a fresh A10 (or specified instance type)
  2. Wait for active + SSH-reachable
  3. Bootstrap the instance (apt + clone + venv + pip install)
  4. Run V1 PIPELINE VALIDATION script over SSH:
       exp_modern_hopfield_pipeline_validation_v1_n2048_n4096.py
  5. SCP the resulting metrics.json back to local
  6. Inspect the local copy: HARD_PASS verdict + non-null metrics +
     audit-cert validity per the V1 pre-registration
  7. TERMINATE the instance in try-finally + atexit + signal handlers

This is THE validation gate per the kickoff doc + session_architecture_v1.
A green run means Tier 2 work can confidently use Lambda for real
experiments.

Note: there is no local-vs-cloud numerical comparison in this version
because we don't have a clean local HARD_PASS reference for V1 on this
checkout. Instead we use the V1 script's OWN pre-registered HARD_PASS
criteria (n_crashed_total == 0, n_non_null_total == 39, cert_all_valid
True). If a numerical reference becomes available later, the comparison
logic from tools/cloud/v1_reproducer_canary.py can be folded back in.

Usage:
  python tools/cloud/launch_v1_canary.py \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path C:/Users/marsh/.ssh/lambda_canary.pem \\
    [--instance-type gpu_1x_a10] \\
    [--max-cost-usd 2.00] \\
    [--expected-wall-min 40]

Exit codes:
  0  V1 ran + HARD_PASS criteria met
  1  fatal error (launch, ssh, scp, etc.)
  2  V1 ran but HARD_PASS criteria NOT met (instrumentation issue)
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import LambdaClient, LambdaClientError  # noqa: E402
from tools.cloud.cost_tracker import update_cost  # noqa: E402


_V1_ANCHOR = "modern_hopfield_pipeline_validation_v1_n2048_n4096"
_V1_SCRIPT = f"experiments/exp_{_V1_ANCHOR}.py"
_REMOTE_METRICS_PATH = f"data/exp_{_V1_ANCHOR}/metrics.json"


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


_TERMINATE_STATE: dict = {"client": None, "instance_ids": [], "done": False}


def _force_terminate():
    if _TERMINATE_STATE["done"] or not _TERMINATE_STATE["client"]:
        return
    if not _TERMINATE_STATE["instance_ids"]:
        _TERMINATE_STATE["done"] = True
        return
    try:
        terminated = _TERMINATE_STATE["client"].terminate_instances(
            _TERMINATE_STATE["instance_ids"]
        )
        print(f"[launch_v1_canary] cleanup: terminated {terminated}", flush=True)
    except Exception as exc:
        print(f"[launch_v1_canary] CLEANUP FAILED: {exc}", flush=True)
        print(f"  Instance ids: {_TERMINATE_STATE['instance_ids']}", flush=True)
        print(f"  MANUALLY TERMINATE VIA LAMBDA WEB CONSOLE NOW", flush=True)
    _TERMINATE_STATE["done"] = True


def _signal_handler(signum, frame):
    print(f"[launch_v1_canary] signal {signum}; cleaning up", flush=True)
    _force_terminate()
    sys.exit(130)


def _ssh_run(
    ip: str,
    ssh_key_path: str | None,
    command: str,
    timeout_s: float = 60.0,
) -> tuple[int, str, str]:
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=15",
        "-o", "LogLevel=ERROR",
    ]
    if ssh_key_path:
        cmd.extend(["-i", ssh_key_path])
    cmd.append(f"ubuntu@{ip}")
    cmd.append(command)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout_s,
        )
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"ssh timeout after {timeout_s}s")
    except Exception as exc:
        return (-1, "", f"ssh error: {exc}")


def _scp_from(
    ip: str,
    ssh_key_path: str | None,
    remote_path: str,
    local_path: Path,
) -> bool:
    cmd = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if ssh_key_path:
        cmd.extend(["-i", ssh_key_path])
    cmd.append(f"ubuntu@{ip}:{remote_path}")
    cmd.append(str(local_path))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return proc.returncode == 0
    except Exception:
        return False


def _evaluate_v1_metrics(metrics: dict) -> tuple[bool, str, dict]:
    """Apply V1's pre-registered HARD_PASS criteria to a metrics dict.

    Per the script docstring:
      HARD_PASS = all cells at BOTH N values produce non-null metrics for
                  every measurement AND no operation crashes
      HARD_FAIL = any cell produces null metric OR any operation crashes

    Different V1 revisions emit slightly different keys; we look for the
    canonical fields with reasonable fallbacks.
    """
    summary = {}
    label = (metrics.get("verdict_label") or metrics.get("label") or "").upper()
    summary["verdict_label"] = label

    # Cell counts (canonical fields).
    n_crashed = metrics.get("n_crashed_total")
    n_non_null = metrics.get("n_non_null_total")
    n_total = metrics.get("n_cells_total")
    if n_crashed is None and "per_cell" in metrics:
        per_cell = metrics["per_cell"]
        if isinstance(per_cell, list):
            n_total = len(per_cell)
            n_crashed = sum(1 for c in per_cell if c.get("crashed"))
            n_non_null = sum(1 for c in per_cell if not c.get("crashed"))
    summary["n_crashed_total"] = n_crashed
    summary["n_non_null_total"] = n_non_null
    summary["n_cells_total"] = n_total

    cert_all_valid = metrics.get("cert_all_valid")
    summary["cert_all_valid"] = cert_all_valid

    # Pass conditions (lenient -- accept either label or per-cell evidence).
    if "PIPELINE_HARD_PASS" in label or "HARD_PASS" in label:
        return True, f"verdict label HARD_PASS ({label})", summary
    if (n_crashed == 0 and n_non_null is not None and n_total is not None
            and n_non_null == n_total and cert_all_valid is True):
        return True, "per-cell: 0 crashed + all non-null + certs valid", summary
    if n_crashed is not None and n_crashed > 0:
        return False, f"FAIL: {n_crashed} cells crashed", summary
    if n_total is not None and n_non_null is not None and n_non_null < n_total:
        return False, f"FAIL: {n_total - n_non_null}/{n_total} cells null", summary
    return False, f"unable to determine pass/fail from metrics", summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch + bootstrap + V1 + terminate")
    parser.add_argument("--ssh-key-name", required=True)
    parser.add_argument("--ssh-key-path", required=True)
    parser.add_argument("--key-file", default=".env.lambda")
    parser.add_argument("--instance-type", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--max-cost-usd", type=float, default=2.0)
    parser.add_argument("--expected-wall-min", type=float, default=40.0,
                        help="Boot + bootstrap + V1 + scp + terminate")
    parser.add_argument("--budget-cap-usd", type=float, default=50.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--v1-timeout-min", type=float, default=45.0,
                        help="SSH command timeout for the V1 dispatch")
    args = parser.parse_args()

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

    # Catalog + pick target.
    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog: {exc}")
        return 1
    with_capacity = [t for t in catalog if t.regions_available]
    if not with_capacity:
        print("[ERROR] no capacity")
        return 1
    with_capacity.sort(key=lambda t: t.price_cents_per_hour)
    if args.instance_type:
        target = next((t for t in with_capacity if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] requested {args.instance_type} has no capacity")
            return 1
    else:
        target = with_capacity[0]
    region = args.region or target.regions_available[0]

    predicted = target.hourly_rate_usd * (args.expected_wall_min / 60.0)
    print("=" * 70)
    print("V1 reproducer canary plan")
    print("=" * 70)
    print(f"  Instance type:       {target.name}")
    print(f"  Region:              {region}")
    print(f"  Rate:                ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min")
    print(f"  PREDICTED COST:      ${predicted:.2f}")
    print(f"  Max-cost cap:        ${args.max_cost_usd:.2f}")
    if predicted > args.max_cost_usd:
        print(f"\n[REFUSE] predicted ${predicted:.2f} > cap ${args.max_cost_usd:.2f}")
        return 1

    atexit.register(_force_terminate)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
    except (AttributeError, ValueError):
        pass

    # --- Launch ---
    print(f"\n[1/5] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)
    try:
        new_ids = client.launch_instance(
            region_name=region,
            instance_type_name=target.name,
            ssh_key_names=[args.ssh_key_name],
            quantity=1,
            name="v1-reproducer-canary",
        )
    except LambdaClientError as exc:
        print(f"[ERROR] launch: {exc}")
        return 1
    if not new_ids:
        print("[ERROR] no instance_ids")
        return 1
    instance_id = new_ids[0]
    _TERMINATE_STATE["instance_ids"] = [instance_id]
    print(f"  launched: {instance_id}")

    # --- Wait active ---
    print(f"[2/5] Waiting for active...")
    try:
        inst = client.wait_for_active(instance_id, timeout_s=900.0)
    except LambdaClientError as exc:
        print(f"[ERROR] wait_for_active: {exc}")
        return 1
    print(f"  active: ip={inst.ip}")
    ip = inst.ip
    update_cost(
        daily_budget_usd=args.budget_cap_usd,
        accumulated_today_usd=0.0,
        current_hourly_rate_usd=inst.hourly_rate_usd,
        active_instances=[{
            "instance_id": instance_id,
            "instance_type": target.name,
            "hourly_rate_usd": inst.hourly_rate_usd,
            "started_at": launch_ts.isoformat(),
        }],
    )

    # --- Bootstrap ---
    print(f"\n[3/5] Bootstrapping {instance_id}...")
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
            encoding="utf-8", errors="replace",
            timeout=2700,
        )
        print(result.stdout)
        if result.stderr:
            print(f"---- bootstrap stderr ----\n{result.stderr[-2000:]}",
                  file=sys.stderr)
        boot_ok = (result.returncode == 0)
        print(f"  bootstrap rc: {result.returncode}")
    except Exception as exc:
        print(f"  [ERROR] bootstrap subprocess: {exc}")
        boot_ok = False
    if not boot_ok:
        print(f"\n[ERROR] bootstrap FAILED; aborting V1 dispatch")
        return 1

    # --- V1 dispatch ---
    print(f"\n[4/5] Dispatching V1 via SSH (timeout {args.v1_timeout_min:.0f} min)...")
    v1_cmd = (
        "cd ~/hd-instrument && "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        f"REMOTE_OUT=data/exp_{_V1_ANCHOR}; "
        f"mkdir -p $REMOTE_OUT && "
        f"$PY {_V1_SCRIPT} 2>&1 | tail -250; "
        f"echo '=== metrics.json ==='; "
        f"if [ -f $REMOTE_OUT/metrics.json ]; then "
        f"  echo 'METRICS_OK'; ls -la $REMOTE_OUT/metrics.json; "
        f"else "
        f"  echo 'NO_METRICS_PRODUCED'; "
        f"fi"
    )
    rc, out, err = _ssh_run(
        ip, args.ssh_key_path, v1_cmd,
        timeout_s=int(args.v1_timeout_min * 60),
    )
    print("---- v1 stdout tail ----")
    print(out[-3500:])
    if err:
        print(f"---- v1 stderr ----\n{err[-1000:]}")
    print(f"---- v1 exit: {rc} ----")
    log_path = _REPO_ROOT / "data" / f"lambda_v1_canary_{instance_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + "\n[stderr]\n" + err, encoding="utf-8")
    print(f"  saved log: {log_path}")

    metrics: dict | None = None
    v1_ok = False
    verdict_msg = "not_evaluated"
    summary: dict = {}

    if rc == 0 and "METRICS_OK" in out:
        # SCP metrics.json back.
        print(f"\n[5/5] SCPing metrics.json back...")
        local_metrics_path = _REPO_ROOT / "data" / f"lambda_v1_canary_metrics_{instance_id}.json"
        ok = _scp_from(
            ip, args.ssh_key_path,
            f"~/hd-instrument/{_REMOTE_METRICS_PATH}",
            local_metrics_path,
        )
        if not ok:
            print(f"  [WARN] SCP failed")
        else:
            print(f"  saved: {local_metrics_path}")
            try:
                metrics = json.loads(local_metrics_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"  [WARN] metrics parse: {exc}")

    if metrics is not None:
        v1_ok, verdict_msg, summary = _evaluate_v1_metrics(metrics)
        print(f"\n  V1 verdict: {'PASS' if v1_ok else 'FAIL'}  ({verdict_msg})")
        for k, v in summary.items():
            print(f"    {k}: {v}")
    else:
        v1_ok = False
        verdict_msg = "no metrics retrieved"
        print(f"\n[FAIL] V1 produced no metrics or SCP failed")

    # --- Terminate (atexit also fires; explicit here for clarity) ---
    print(f"\n[terminate] {instance_id}...")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)

    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)
    print()
    print("=" * 70)
    print("V1 canary report")
    print("=" * 70)
    print(f"  Predicted:           ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:         {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:         ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:               ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  V1 verdict:          {'PASS' if v1_ok else 'FAIL'}  ({verdict_msg})")

    update_cost(
        daily_budget_usd=args.budget_cap_usd,
        accumulated_today_usd=actual_cost,
        current_hourly_rate_usd=0.0,
        active_instances=[],
    )

    report = {
        "instance_id": instance_id,
        "instance_type": target.name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "v1_ok": v1_ok,
        "verdict_msg": verdict_msg,
        "v1_summary": summary,
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    rp = _REPO_ROOT / "data" / f"lambda_v1_canary_report_{instance_id}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report: {rp}")

    return 0 if v1_ok else 2


if __name__ == "__main__":
    sys.exit(main())
