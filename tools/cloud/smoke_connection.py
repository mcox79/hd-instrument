"""Lambda Cloud smoke-connection check (zero-spend).

Run this FIRST when the API key arrives. It performs ONLY read operations
(list instance types + list current instances + list ssh keys). No instance
launch, no resource creation, zero billing impact.

What it verifies:
  1. The API key authenticates correctly (HTTP 401 means wrong key).
  2. The /instance-types catalog is reachable + parseable.
  3. There are no existing instances quietly burning money on this account.
  4. SSH keys are listed (you'll need at least one for the canary launch).

Usage:
  $env:LAMBDA_CLOUD_API_KEY = "your_key_here"   # PowerShell
  python tools/cloud/smoke_connection.py

  # Or pass an explicit file (gitignored):
  python tools/cloud/smoke_connection.py --key-file .env.lambda

Exit codes:
  0  smoke passed; safe to proceed to canary_lifecycle.py
  1  auth failure or network error
  2  account has existing active instances (manual review required)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow running this script standalone without sys.path setup.
_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import (  # noqa: E402
    LambdaClient,
    LambdaClientError,
    compute_accumulated_cost,
)


def _load_key_from_file(path: Path) -> str | None:
    """Read an env-style .env.lambda file and return the LAMBDA_CLOUD_API_KEY value."""
    if not path.is_file():
        return None
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if "=" not in ln:
            continue
        k, _, v = ln.partition("=")
        if k.strip() == "LAMBDA_CLOUD_API_KEY":
            v = v.strip().strip('"').strip("'")
            return v
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Lambda Cloud smoke connection check")
    parser.add_argument(
        "--key-file",
        default=".env.lambda",
        help="Path to env file containing LAMBDA_CLOUD_API_KEY (default: .env.lambda)",
    )
    args = parser.parse_args()

    # Resolve API key: env var > key file
    key = os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
    if not key:
        kp = Path(args.key_file)
        if not kp.is_absolute():
            kp = _REPO_ROOT / kp
        file_key = _load_key_from_file(kp)
        if file_key:
            key = file_key
            print(f"[smoke] using key from {kp}")
    if not key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY env var and no key file. Set one and retry.")
        return 1

    try:
        client = LambdaClient(api_key=key)
    except LambdaClientError as exc:
        print(f"[ERROR] client init failed: {exc}")
        return 1

    print("=" * 70)
    print("Lambda Cloud smoke-connection check (zero-spend)")
    print("=" * 70)

    # Step 1: catalog
    print("\n[1/3] Fetching instance-type catalog...")
    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] list_instance_types failed: {exc}")
        if "401" in str(exc):
            print("       -> 401 means the API key is wrong.")
        elif "network" in str(exc).lower():
            print("       -> Network unreachable; check connectivity.")
        return 1
    print(f"  OK: {len(catalog)} instance types in catalog")
    with_cap = [t for t in catalog if t.regions_available]
    print(f"  {len(with_cap)} have capacity available right now")
    if with_cap:
        with_cap.sort(key=lambda t: t.price_cents_per_hour)
        cheapest = with_cap[0]
        print(f"  Cheapest available: {cheapest.name}  ${cheapest.hourly_rate_usd:.2f}/hr  "
              f"({cheapest.gpu_description})  regions={cheapest.regions_available}")
        # Top 5 with capacity, sorted by price
        print("  Top 5 cheapest with capacity:")
        for t in with_cap[:5]:
            print(f"    {t.name:30s}  ${t.hourly_rate_usd:5.2f}/hr  {t.gpu_description}")

    # Step 2: current instances (look for stale spend)
    print("\n[2/3] Listing current instances...")
    try:
        instances = client.list_instances()
    except LambdaClientError as exc:
        print(f"[ERROR] list_instances failed: {exc}")
        return 1
    active = [i for i in instances if i.status in ("active", "booting", "terminating", "unhealthy")]
    print(f"  OK: {len(instances)} total, {len(active)} billable")
    if active:
        acc, hourly, per_instance = compute_accumulated_cost(active)
        print(f"  CURRENT SPEND TODAY: ${acc:.2f}  (rate ${hourly:.2f}/hr)")
        for p in per_instance:
            print(f"    {p['instance_id'][:12]}  {p['instance_type']:24s}  "
                  f"${p['hourly_rate_usd']:.2f}/hr  ${p['accumulated_today_usd']:.2f} today  "
                  f"status={p['status']}")
        print("\n  [WARN] There are existing active instances. Review before launching the canary.")
        print("  Terminate them with:")
        for p in per_instance:
            print(f"    python -m tools.cloud.lambda_client terminate {p['instance_id']}")
        # Don't return 2 if user explicitly wants to keep them; just warn.
    else:
        print("  No active instances. Account is at $0/hr right now.")

    # Step 3: SSH keys
    print("\n[3/3] Listing SSH keys...")
    try:
        keys = client.list_ssh_keys()
    except LambdaClientError as exc:
        print(f"[ERROR] list_ssh_keys failed: {exc}")
        return 1
    print(f"  OK: {len(keys)} SSH keys registered")
    for k in keys:
        name = k.get("name", "(unnamed)")
        kid = k.get("id", "?")[:12]
        print(f"    {kid}  {name}")
    if not keys:
        print("  [WARN] No SSH keys registered. The canary launch will need one.")
        print("        Add one via Lambda's web console OR via:")
        print("          python -m tools.cloud.lambda_client add_ssh_key <name>")

    # Verdict
    print("\n" + "=" * 70)
    if active:
        print("VERDICT: API works. Account has active spend; review before canary.")
        return 2
    print("VERDICT: API works. Account at $0/hr. Safe to proceed to canary_lifecycle.")
    print(f"Suggested cheapest canary target: {with_cap[0].name if with_cap else 'NONE AVAILABLE'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
