"""Lambda Cloud canary lifecycle test.

What this script does (in order):
  1. Predicts the cost of the canary based on instance rate + estimated wall.
  2. Refuses to run if predicted cost exceeds --max-cost-usd (default $20).
  3. Launches ONE instance at the cheapest-with-capacity GPU type.
  4. Waits for it to reach `active` status (boot).
  5. Reports the IP + writes cloud_cost_tracker.json so the dashboard surfaces
     the live spend.
  6. SSH-smokes the instance: nvidia-smi + python version + torch cuda check.
  7. ALWAYS terminates the instance at the end (try-finally; even on errors).
  8. Reports actual cost vs predicted; flags if predicted was wrong.

Calibration goal: this run answers the question "are our cost estimates wrong?"
by comparing predicted ($ predicted from start_time * hourly_rate) against
observed (actual elapsed * hourly_rate, computed at termination time).

Usage:
  $env:LAMBDA_CLOUD_API_KEY = "your_key_here"
  python tools/cloud/canary_lifecycle.py [--max-cost-usd 20] [--dry-run]

Dry-run mode (--dry-run) prints what WOULD happen without launching anything.
Useful for review before the first real spend.

Exit codes:
  0  canary succeeded: instance launched, smoke passed, terminated cleanly,
     actual cost within tolerance of prediction
  1  fatal error during launch / smoke (instance terminated for cleanup)
  2  prediction was off by > 25% (cost-estimation calibration issue;
     still terminated; recorded for follow-up)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import (  # noqa: E402
    LambdaClient,
    LambdaClientError,
    Instance,
    compute_accumulated_cost,
)
from tools.cloud.cost_tracker import update_cost  # noqa: E402


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
        ln = ln.strip()
        if ln.startswith("LAMBDA_CLOUD_API_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v
    return None


def _ssh_smoke(ip: str, ssh_key_path: str | None, timeout_s: float = 30.0) -> tuple[bool, str]:
    """Run a small `nvidia-smi + python -c "import torch"` over SSH.

    Returns (ok, captured_stdout_stderr). Uses the standard ubuntu user
    that Lambda images come with.
    """
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
    cmd.append(
        "echo '=== uname ==='; uname -a; "
        "echo '=== python ==='; python3 --version; "
        "echo '=== nvidia-smi ==='; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; "
        "echo '=== torch ==='; python3 -c 'import torch; print(torch.__version__); print(\"cuda:\", torch.cuda.is_available()); print(\"device_count:\", torch.cuda.device_count())' 2>&1 | tail -10; "
        "echo '=== free ==='; free -g | head -2"
    )
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s + 30
        )
        out = (proc.stdout or "") + ("\n[stderr]\n" + proc.stderr if proc.stderr else "")
        return (proc.returncode == 0, out)
    except subprocess.TimeoutExpired:
        return (False, "ssh timeout")
    except FileNotFoundError:
        return (False, "ssh binary not found on local machine")
    except Exception as exc:
        return (False, f"ssh subprocess error: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lambda Cloud canary lifecycle test")
    parser.add_argument("--max-cost-usd", type=float, default=20.0,
                        help="Refuse to run if predicted cost exceeds this (default 20)")
    parser.add_argument("--expected-wall-min", type=float, default=12.0,
                        help="Expected wall time in minutes for cost prediction (default 12 = boot + smoke + terminate buffer)")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file containing LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--instance-type",
                        help="Override the chosen instance type (default: cheapest available)")
    parser.add_argument("--ssh-key-name",
                        help="Lambda-registered SSH key name to authorize for the instance "
                             "(default: first key listed)")
    parser.add_argument("--ssh-key-path",
                        help="Local private key file matching --ssh-key-name for SSH smoke")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan + estimated cost; do NOT launch any instance")
    parser.add_argument("--budget-cap-usd", type=float, default=50.0,
                        help="Daily budget cap for the dashboard cost-tracker (default 50)")
    args = parser.parse_args()

    key = _load_key(args.key_file)
    if not key and not args.dry_run:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY env var and no key file.")
        return 1

    # In dry-run we use mock=True for the catalog query so this runs without a key.
    client = LambdaClient(api_key=key, mock=(args.dry_run and not key))

    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog fetch failed: {exc}")
        return 1
    with_capacity = [t for t in catalog if t.regions_available]
    if not with_capacity:
        print("[ERROR] no instance types with capacity available right now.")
        return 1
    with_capacity.sort(key=lambda t: t.price_cents_per_hour)

    if args.instance_type:
        target = next((t for t in with_capacity if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] requested --instance-type {args.instance_type!r} has no capacity now.")
            print("Available types with capacity:")
            for t in with_capacity[:10]:
                print(f"  {t.name}  ${t.hourly_rate_usd:.2f}/hr")
            return 1
    else:
        target = with_capacity[0]

    predicted_cost = target.hourly_rate_usd * (args.expected_wall_min / 60.0)
    print("=" * 70)
    print("Lambda canary lifecycle plan")
    print("=" * 70)
    print(f"  Instance type:       {target.name}")
    print(f"  GPU description:     {target.gpu_description}")
    print(f"  Hourly rate:         ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Available regions:   {', '.join(target.regions_available)}")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min")
    print(f"  PREDICTED COST:      ${predicted_cost:.2f}")
    print(f"  Max-cost-usd cap:    ${args.max_cost_usd:.2f}")

    if predicted_cost > args.max_cost_usd:
        print(f"\n[REFUSE] Predicted ${predicted_cost:.2f} > cap ${args.max_cost_usd:.2f}.")
        print("        Reduce --expected-wall-min or pick a cheaper --instance-type, then retry.")
        return 1

    if args.dry_run:
        print("\n[DRY-RUN] No instance launched. Re-run without --dry-run to spend money.")
        return 0

    # Determine SSH key to authorize.
    try:
        keys = client.list_ssh_keys()
    except LambdaClientError as exc:
        print(f"[ERROR] list_ssh_keys failed: {exc}")
        return 1
    if not keys:
        print("[ERROR] no SSH keys registered on this Lambda account. Register one and retry.")
        return 1
    if args.ssh_key_name:
        chosen_key = next((k for k in keys if k.get("name") == args.ssh_key_name), None)
        if not chosen_key:
            print(f"[ERROR] no registered key named {args.ssh_key_name!r}. Available:")
            for k in keys:
                print(f"  {k.get('name')}")
            return 1
    else:
        chosen_key = keys[0]
    key_name = chosen_key.get("name")
    print(f"  SSH key:             {key_name}")

    region = target.regions_available[0]
    print(f"  Region:              {region}")
    print()

    # --- Launch ---
    print(f"[1/4] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)
    try:
        new_ids = client.launch_instance(
            region_name=region,
            instance_type_name=target.name,
            ssh_key_names=[key_name],
            quantity=1,
            name="canary-lifecycle-smoke",
        )
    except LambdaClientError as exc:
        print(f"[ERROR] launch failed: {exc}")
        return 1
    if not new_ids:
        print("[ERROR] launch returned no instance IDs")
        return 1
    instance_id = new_ids[0]
    print(f"  launched: {instance_id}")

    instance: Instance | None = None
    smoke_ok = False
    smoke_output = ""
    try:
        # --- Wait for active ---
        print(f"[2/4] Waiting for {instance_id} to reach `active` (boot)...")
        update_cost(
            daily_budget_usd=args.budget_cap_usd,
            accumulated_today_usd=0.0,
            current_hourly_rate_usd=target.hourly_rate_usd,
            active_instances=[{
                "instance_id": instance_id,
                "instance_type": target.name,
                "hourly_rate_usd": target.hourly_rate_usd,
                "started_at": launch_ts.isoformat(),
            }],
        )
        instance = client.wait_for_active(instance_id, timeout_s=900.0)
        print(f"  active: ip={instance.ip}  rate=${instance.hourly_rate_usd:.2f}/hr")

        # --- SSH smoke ---
        print(f"[3/4] SSH smoke against ubuntu@{instance.ip} ...")
        smoke_ok, smoke_output = _ssh_smoke(instance.ip, args.ssh_key_path)
        print("---- ssh smoke output ----")
        print(smoke_output[:4000])
        print("---- end ssh smoke ----")
        if smoke_ok:
            print("  smoke: OK")
        else:
            print("  smoke: FAILED (still terminating instance for cleanup)")
    finally:
        # --- Terminate (ALWAYS) ---
        print(f"[4/4] Terminating {instance_id} ...")
        terminate_ts = datetime.now(timezone.utc)
        try:
            terminated = client.terminate_instances([instance_id])
            print(f"  terminated: {terminated}")
        except LambdaClientError as exc:
            print(f"[CRITICAL] termination call failed: {exc}")
            print("  Manually terminate via Lambda web console NOW.")

    # --- Cost reconciliation ---
    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = target.hourly_rate_usd * (actual_wall_s / 3600.0)
    print("\n" + "=" * 70)
    print("Canary report")
    print("=" * 70)
    print(f"  Predicted cost:      ${predicted_cost:.2f}  (assumed {args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:         {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:         ${actual_cost:.2f}")
    delta = actual_cost - predicted_cost
    rel = (delta / predicted_cost * 100) if predicted_cost > 0 else 0
    print(f"  Delta:               ${delta:+.2f}  ({rel:+.1f}%)")
    print(f"  Smoke verdict:       {'PASS' if smoke_ok else 'FAIL'}")

    # Write a final cost snapshot so the dashboard reflects the canary spend
    # (will show $X / $cap once the page refreshes).
    update_cost(
        daily_budget_usd=args.budget_cap_usd,
        accumulated_today_usd=actual_cost,
        current_hourly_rate_usd=0.0,  # instance terminated
        active_instances=[],
    )

    # Final structured report; useful for piping into a status_log entry.
    report = {
        "instance_type": target.name,
        "hourly_rate_usd": target.hourly_rate_usd,
        "predicted_cost_usd": round(predicted_cost, 2),
        "actual_cost_usd": round(actual_cost, 2),
        "delta_pct": round(rel, 1),
        "smoke_ok": smoke_ok,
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    out_path = _REPO_ROOT / "data" / "lambda_canary_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report written: {out_path}")

    # Exit code
    if not smoke_ok:
        return 1
    if abs(rel) > 25.0:
        print("\n[WARN] Cost prediction was off by more than 25%. Update the wall estimate.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
