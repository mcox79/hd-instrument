"""Launch + bootstrap + terminate in one atomic unit.

Wraps `tools/cloud/bootstrap_instance.py` with explicit lifecycle control:
  1. Launch the cheapest-available GPU (default gpu_1x_a10 in us-east-1)
  2. Wait for SSH-reachable
  3. Run bootstrap_instance.py against the new instance
  4. TERMINATE the instance in a try-finally (fires even on bootstrap
     failure, atexit, SIGTERM)
  5. Report actual cost vs predicted

This script exists because bootstrap_instance.py alone assumes the
instance is already launched + leaves it running afterward (so a follow-up
script like v1_reproducer_canary.py can reuse it). For one-shot
"is bootstrap working" validation runs that should auto-cleanup, use
THIS wrapper instead.

Usage:
  python tools/cloud/bootstrap_and_terminate.py \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path C:/Users/marsh/.ssh/lambda_canary.pem \\
    [--instance-type gpu_1x_a10] [--max-cost-usd 1.00]
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


# Global so atexit + signal handlers can reach it.
_TERMINATE_STATE: dict = {"client": None, "instance_ids": [], "done": False}


def _force_terminate():
    """Idempotent terminate with retry. Tolerates transient network failures.

    Cleanup MUST succeed even if local DNS / network blips at the wrong
    moment (we observed [Errno 11001] getaddrinfo failed on a real run,
    which leaked an instance until manual cleanup). Retry up to 6 times
    with exponential backoff (1s, 2s, 4s, 8s, 16s, 32s ~ 63s total).

    If all retries fail the function writes a sticky leak flag so the
    next session / dashboard sees it.
    """
    if _TERMINATE_STATE["done"] or not _TERMINATE_STATE["client"]:
        return
    if not _TERMINATE_STATE["instance_ids"]:
        _TERMINATE_STATE["done"] = True
        return
    instance_ids = list(_TERMINATE_STATE["instance_ids"])
    backoff = 1.0
    last_exc: Exception | None = None
    for attempt in range(6):
        try:
            terminated = _TERMINATE_STATE["client"].terminate_instances(instance_ids)
            print(f"[bootstrap_and_terminate] cleanup attempt {attempt+1}: terminated {terminated}",
                  flush=True)
            _TERMINATE_STATE["done"] = True
            return
        except Exception as exc:
            last_exc = exc
            print(f"[bootstrap_and_terminate] cleanup attempt {attempt+1} failed: {exc}",
                  flush=True)
            if attempt < 5:
                print(f"  retrying in {backoff:.0f}s...", flush=True)
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
    print(f"[bootstrap_and_terminate] CLEANUP EXHAUSTED RETRIES: {last_exc}", flush=True)
    print(f"  Instance ids: {instance_ids}", flush=True)
    print(f"  MANUALLY TERMINATE VIA LAMBDA WEB CONSOLE", flush=True)
    try:
        flag = _REPO_ROOT / "data" / f"lambda_LEAKED_instance_{instance_ids[0]}.flag"
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(
            json.dumps({
                "instance_ids": instance_ids,
                "leaked_at": datetime.now(timezone.utc).isoformat(),
                "last_error": str(last_exc),
            }, indent=2),
            encoding="utf-8",
        )
        print(f"  leak flag written: {flag}", flush=True)
    except Exception as exc2:
        print(f"  could not write leak flag: {exc2}", flush=True)
    _TERMINATE_STATE["done"] = True


def _signal_handler(signum, frame):
    print(f"[bootstrap_and_terminate] caught signal {signum}; terminating cleanup", flush=True)
    _force_terminate()
    sys.exit(130)


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch + bootstrap + terminate (one-shot)")
    parser.add_argument("--ssh-key-name", required=True,
                        help="Lambda-registered SSH key name")
    parser.add_argument("--ssh-key-path", required=True,
                        help="Local private-key file matching --ssh-key-name")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file with LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--instance-type", default=None,
                        help="Override instance type (default: cheapest with capacity)")
    parser.add_argument("--region", default=None,
                        help="Override region (default: first region with capacity for target type)")
    parser.add_argument("--max-cost-usd", type=float, default=2.0,
                        help="Refuse if predicted cost exceeds this (default $2)")
    parser.add_argument("--expected-wall-min", type=float, default=15.0,
                        help="Expected wall time in min (boot + apt + clone + pip + smoke + terminate)")
    parser.add_argument("--budget-cap-usd", type=float, default=50.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
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

    # Catalog + pick target
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
    print("Bootstrap-and-terminate plan")
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

    # Register cleanup handlers BEFORE the launch call.
    atexit.register(_force_terminate)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except (AttributeError, ValueError):
        pass
    try:
        signal.signal(signal.SIGINT, _signal_handler)
    except (AttributeError, ValueError):
        pass

    # --- Launch (pre-snapshot + 5xx retry + orphan reconcile) ---
    # Lambda's API can return 502/503/504 mid-launch while still spinning
    # up the instance, leaving an orphan we never learn the id of. Pattern:
    # snapshot active ids before; retry transient 5xx; reconcile any new
    # active ids since snapshot as "ours" regardless of API reply.
    print(f"\n[1/4] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)

    def _snapshot_active_ids() -> set[str]:
        try:
            return {
                i.instance_id for i in client.list_instances()
                if i.status in ("active", "booting", "terminating", "unhealthy")
            }
        except Exception:
            return set()

    pre_launch_ids = _snapshot_active_ids()
    print(f"  pre-launch active instances on account: {len(pre_launch_ids)}")

    new_ids: list[str] = []
    last_exc: Exception | None = None
    backoff = 2.0
    for attempt in range(3):
        try:
            new_ids = client.launch_instance(
                region_name=region,
                instance_type_name=target.name,
                ssh_key_names=[args.ssh_key_name],
                quantity=1,
                name="bootstrap-canary",
            )
            if new_ids:
                break
        except LambdaClientError as exc:
            last_exc = exc
            msg = str(exc)
            transient = any(c in msg for c in (" 502 ", " 503 ", " 504 "))
            print(f"  launch attempt {attempt+1} failed: {exc}")
            if not transient:
                break
            if attempt < 2:
                print(f"  transient 5xx; retrying in {backoff:.0f}s...")
                time.sleep(backoff)
                backoff *= 2

    time.sleep(5)
    post_launch_ids = _snapshot_active_ids()
    orphan_ids = sorted(post_launch_ids - pre_launch_ids - set(new_ids))
    all_ours = list(set(new_ids) | set(orphan_ids))
    if orphan_ids:
        print(f"  reconciliation detected {len(orphan_ids)} orphan(s): {orphan_ids}; "
              f"registering for cleanup")

    if not all_ours:
        print(f"[ERROR] launch produced no instance (last_error={last_exc!r})")
        return 1

    _TERMINATE_STATE["instance_ids"] = all_ours
    instance_id = new_ids[0] if new_ids else orphan_ids[0]
    print(f"  launched: {instance_id}  (tracked total: {len(all_ours)})")

    # --- Wait active ---
    print(f"[2/4] Waiting for active...")
    try:
        inst = client.wait_for_active(instance_id, timeout_s=900.0)
    except LambdaClientError as exc:
        print(f"[ERROR] wait_for_active: {exc}")
        return 1
    print(f"  active: ip={inst.ip}")

    # Update cost tracker live
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
    print(f"\n[3/4] Running bootstrap_instance.py {instance_id}...")
    boot_cmd = [
        sys.executable,
        str(_REPO_ROOT / "tools" / "cloud" / "bootstrap_instance.py"),
        instance_id,
        "--ssh-key-path", args.ssh_key_path,
        "--repo-url", args.repo_url,
        "--branch", args.branch,
    ]
    boot_t0 = time.time()
    try:
        result = subprocess.run(
            boot_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",          # avoid Windows cp1252 UnicodeDecodeError
            errors="replace",          # on non-ASCII bytes in pip output
            timeout=2700,              # 45 min cap
        )
        print(result.stdout)
        if result.stderr:
            print(f"---- bootstrap stderr ----\n{result.stderr}", file=sys.stderr)
        boot_ok = (result.returncode == 0)
        print(f"  bootstrap rc: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("  [ERROR] bootstrap timed out")
        boot_ok = False
    except Exception as exc:
        print(f"  [ERROR] bootstrap subprocess: {exc}")
        boot_ok = False
    boot_wall_s = time.time() - boot_t0
    print(f"  bootstrap wall: {boot_wall_s/60:.1f} min")

    # --- Terminate (always; finally would catch but explicit is clearer) ---
    print(f"\n[4/4] Terminating {instance_id}...")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)

    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)

    print()
    print("=" * 70)
    print("Bootstrap-and-terminate report")
    print("=" * 70)
    print(f"  Predicted:           ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:         {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:         ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:               ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  Bootstrap verdict:   {'PASS' if boot_ok else 'FAIL'}")

    # Final cost tracker snapshot
    update_cost(
        daily_budget_usd=args.budget_cap_usd,
        accumulated_today_usd=actual_cost,
        current_hourly_rate_usd=0.0,
        active_instances=[],
    )

    report = {
        "instance_type": target.name,
        "region": region,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "predicted_cost_usd": round(predicted, 2),
        "actual_wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "bootstrap_ok": boot_ok,
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    rp = _REPO_ROOT / "data" / "lambda_bootstrap_and_terminate_report.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report: {rp}")

    return 0 if boot_ok else 1


if __name__ == "__main__":
    sys.exit(main())
