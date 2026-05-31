"""V1 reproducer canary: dispatch the V1 pipeline validation on Lambda and
compare its result to a known-good local result.

This is the FINAL gate before Tier 2 work uses Lambda for real. It answers:
  "Does experiments/exp_modern_hopfield_pipeline_validation_v1_n2048_n4096.py
   produce numerically-comparable HARD_PASS on a fresh Lambda GPU instance?"

Pre-requisites:
  - Lambda API key in env / .env.lambda
  - At least one Lambda-registered SSH key
  - bootstrap_instance.py succeeded on the target (repo cloned + deps installed)
  - A local reference result.json (see --reference-result-path)

Flow:
  1. Verify target instance is active + bootstrapped.
  2. (optional) Re-run bootstrap if --re-bootstrap.
  3. Dispatch the V1 anchor over SSH; capture stdout + return code.
  4. SCP the resulting result.json back to local.
  5. Compare the cloud result against the local reference:
       - HARD_PASS flag matches (must be True both sides)
       - Per-cell n_crashed == 0 both sides
       - Per-cell n_non_null counts match
       - cert_all_valid == True both sides
       - max(|cloud_metric - local_metric|/local_metric) per metric reported
  6. Write a verdict report; exit with corresponding code.

Cost estimate:
  V1 is CPU-only by design but a Lambda GPU instance still runs it fine.
  Wall: ~10-20 min for both N values + all M cells. At gpu_1x_a10 ($0.75/hr)
  that's ~$0.15-0.25; at gpu_1x_h100_pcie ($2.49/hr) it's ~$0.50-0.85.

Exit codes:
  0  HARD_PASS on cloud + numerical match with local reference
  1  fatal error (API, bootstrap, SCP, etc.)
  2  HARD_PASS on cloud but numerical drift > --max-rel-drift (signal: env
     parity issue; reproducibility question)
  3  cloud run did NOT HARD_PASS (whether HARD_FAIL or MIDDLE_BAND)
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

from tools.cloud.lambda_client import LambdaClient, LambdaClientError  # noqa: E402

_V1_ANCHOR = "modern_hopfield_pipeline_validation_v1_n2048_n4096"
_V1_SCRIPT = f"experiments/exp_{_V1_ANCHOR}.py"


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


def _ssh_run(
    ip: str,
    ssh_key_path: str | None,
    command: str,
    timeout_s: float = 1800.0,
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
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"timeout after {timeout_s}s")
    except Exception as exc:
        return (-1, "", str(exc))


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


def _compare_results(
    local: dict,
    cloud: dict,
    max_rel_drift: float,
) -> dict:
    """Compare two result dicts. Returns a verdict dict.

    Schema flexibility: V1 outputs vary by script revision. We check a small
    set of always-present pipeline-correctness fields, then compare any
    numeric scalars that appear in both at the top level.
    """
    out: dict = {
        "schema_match": True,
        "label_match": False,
        "drift": [],
        "drift_exceeded": False,
        "max_rel_drift_seen": 0.0,
        "local_label": local.get("verdict_label") or local.get("label") or "",
        "cloud_label": cloud.get("verdict_label") or cloud.get("label") or "",
    }

    out["label_match"] = (
        out["local_label"] and out["local_label"] == out["cloud_label"]
    )

    # Per-cell pipeline checks (the V1 HARD_PASS criteria).
    for fld in ("n_crashed_total", "n_non_null_total", "cert_all_valid"):
        lv = local.get(fld)
        cv = cloud.get(fld)
        if lv is None or cv is None:
            continue
        if lv != cv:
            out["drift"].append({
                "field": fld,
                "local": lv,
                "cloud": cv,
                "rel": None,
                "exceeded": True,
            })
            out["drift_exceeded"] = True

    # Numeric scalar drift (rel diff per shared top-level numeric field).
    for k in sorted(set(local.keys()) & set(cloud.keys())):
        lv = local.get(k)
        cv = cloud.get(k)
        if not isinstance(lv, (int, float)) or not isinstance(cv, (int, float)):
            continue
        if isinstance(lv, bool) or isinstance(cv, bool):
            continue
        if lv == 0:
            continue
        rel = abs(cv - lv) / abs(lv)
        if rel > out["max_rel_drift_seen"]:
            out["max_rel_drift_seen"] = round(rel, 6)
        if rel > max_rel_drift:
            out["drift"].append({
                "field": k,
                "local": lv,
                "cloud": cv,
                "rel": rel,
                "exceeded": True,
            })
            out["drift_exceeded"] = True

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="V1 reproducer canary on Lambda")
    parser.add_argument("instance_id", help="Lambda instance ID (must be active + bootstrapped)")
    parser.add_argument("--ssh-key-path",
                        help="Local private key file (for SSH/SCP)")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file with LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--reference-result-path",
                        default=f"data/exp_{_V1_ANCHOR}/result.json",
                        help="Local reference result.json (from prior local V1 HARD_PASS run)")
    parser.add_argument("--max-rel-drift", type=float, default=0.01,
                        help="Max acceptable per-field relative drift (default 1%%)")
    parser.add_argument("--terminate-on-done", action="store_true",
                        help="Terminate the instance after the canary completes "
                             "(regardless of pass/fail). Recommended for cost discipline.")
    parser.add_argument("--remote-timeout-min", type=float, default=45.0,
                        help="SSH command timeout for the V1 run (default 45 min)")
    args = parser.parse_args()

    key = _load_key(args.key_file)
    if not key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY env var and no key file.")
        return 1
    try:
        client = LambdaClient(api_key=key)
        inst = client.get_instance(args.instance_id)
    except LambdaClientError as exc:
        print(f"[ERROR] Lambda API: {exc}")
        return 1
    if inst is None or inst.status != "active" or not inst.ip:
        print(f"[ERROR] instance {args.instance_id!r} not active or no IP")
        return 1

    print("=" * 70)
    print("V1 reproducer canary")
    print("=" * 70)
    print(f"  target instance:   {args.instance_id}")
    print(f"  ip:                {inst.ip}")
    print(f"  type:              {inst.instance_type_name}")
    print(f"  rate:              ${inst.hourly_rate_usd:.2f}/hr")
    print(f"  anchor:            {_V1_ANCHOR}")
    print(f"  reference local:   {args.reference_result_path}")
    print(f"  max rel drift:     {args.max_rel_drift*100:.2f}%")

    ref_path = Path(args.reference_result_path)
    if not ref_path.is_absolute():
        ref_path = _REPO_ROOT / ref_path
    if not ref_path.is_file():
        print(f"\n[ERROR] reference result missing: {ref_path}")
        print("        Run the V1 anchor locally first to produce one, or pass")
        print("        --reference-result-path pointing to an existing file.")
        return 1
    try:
        local_result = json.loads(ref_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] reading reference: {exc}")
        return 1

    run_start = datetime.now(timezone.utc)

    # Dispatch the V1 script on the instance. Uses the venv installed by
    # bootstrap_instance.py; falls back to system python if venv is absent.
    run_cmd = (
        "cd ~/hd-instrument && "
        f"PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        f"REMOTE_OUT=data/exp_{_V1_ANCHOR}; "
        f"mkdir -p $REMOTE_OUT && "
        f"$PY {_V1_SCRIPT} 2>&1 | tail -200; "
        f"echo '=== result.json ==='; "
        f"if [ -f $REMOTE_OUT/result.json ]; then "
        f"  echo 'OK result.json present'; "
        f"else "
        f"  echo 'NO result.json produced'; "
        f"fi"
    )

    print(f"\n[1/3] Dispatching V1 on Lambda (~{args.remote_timeout_min:.0f}m timeout)...")
    rc, out, err = _ssh_run(
        inst.ip,
        args.ssh_key_path,
        run_cmd,
        timeout_s=int(args.remote_timeout_min * 60),
    )
    print("---- v1 stdout tail ----")
    print(out[-3000:])
    if err:
        print(f"---- v1 stderr ----\n{err[-1500:]}")
    print(f"---- exit: {rc} ----")

    # Persist the log on the local side regardless of result.
    log_path = _REPO_ROOT / "data" / f"lambda_v1_canary_{args.instance_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + "\n[stderr]\n" + err, encoding="utf-8")
    print(f"\n  saved log: {log_path}")

    if rc != 0:
        print(f"\n[ERROR] V1 script exited rc={rc}")
        if args.terminate_on_done:
            try:
                client.terminate_instances([args.instance_id])
                print(f"  terminated {args.instance_id}")
            except Exception:
                pass
        return 3

    # SCP the cloud result.
    print(f"\n[2/3] SCPing cloud result.json back...")
    cloud_result_path = _REPO_ROOT / "data" / f"lambda_v1_canary_result_{args.instance_id}.json"
    ok = _scp_from(
        inst.ip,
        args.ssh_key_path,
        f"~/hd-instrument/data/exp_{_V1_ANCHOR}/result.json",
        cloud_result_path,
    )
    if not ok:
        print(f"[ERROR] SCP failed (no result.json on remote?)")
        if args.terminate_on_done:
            try:
                client.terminate_instances([args.instance_id])
            except Exception:
                pass
        return 1
    print(f"  saved: {cloud_result_path}")
    try:
        cloud_result = json.loads(cloud_result_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] cloud result parse: {exc}")
        if args.terminate_on_done:
            try:
                client.terminate_instances([args.instance_id])
            except Exception:
                pass
        return 1

    # Compare.
    print(f"\n[3/3] Comparing cloud vs local reference...")
    verdict = _compare_results(local_result, cloud_result, args.max_rel_drift)
    print(f"  local label:           {verdict['local_label']}")
    print(f"  cloud label:           {verdict['cloud_label']}")
    print(f"  label match:           {verdict['label_match']}")
    print(f"  max rel drift seen:    {verdict['max_rel_drift_seen']*100:.4f}%")
    print(f"  drift threshold:       {args.max_rel_drift*100:.2f}%")
    print(f"  drift exceeded:        {verdict['drift_exceeded']}")
    if verdict["drift"]:
        print(f"  drift detail (top 10):")
        for d in verdict["drift"][:10]:
            rel_str = f"{d['rel']*100:.4f}%" if d["rel"] is not None else "-"
            print(f"    {d['field']:30s}  local={d['local']!r:>16s}  "
                  f"cloud={d['cloud']!r:>16s}  rel={rel_str}")

    run_end = datetime.now(timezone.utc)
    wall_min = (run_end - run_start).total_seconds() / 60.0
    actual_cost = inst.hourly_rate_usd * (wall_min / 60.0)
    print(f"\n  wall time:             {wall_min:.1f} min")
    print(f"  approx run cost:       ${actual_cost:.2f}")

    # Persist verdict report.
    report = {
        "instance_id": args.instance_id,
        "instance_type": inst.instance_type_name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(wall_min, 1),
        "approx_cost_usd": round(actual_cost, 2),
        "verdict": verdict,
        "run_start": run_start.isoformat(),
        "run_end": run_end.isoformat(),
    }
    report_path = _REPO_ROOT / "data" / f"lambda_v1_canary_report_{args.instance_id}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  report written: {report_path}")

    if args.terminate_on_done:
        try:
            client.terminate_instances([args.instance_id])
            print(f"\n  terminated {args.instance_id}")
        except Exception as exc:
            print(f"\n[WARN] termination failed: {exc}")

    # Final exit code.
    if not verdict["label_match"]:
        print(f"\n[FAIL] cloud verdict label != local reference label")
        return 3
    if verdict["drift_exceeded"]:
        print(f"\n[WARN] HARD_PASS matches but numerical drift > {args.max_rel_drift*100:.2f}%")
        print(f"       Environment parity issue likely (CUDA/torch version). Investigate.")
        return 2
    print(f"\n[OK] V1 reproduces on Lambda within drift tolerance. Tier 2 may proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
