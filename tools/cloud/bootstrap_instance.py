"""Lambda instance bootstrap: provision a fresh instance to run hd-instrument.

Steps (all via SSH; the orchestrator stays on the local box):
  1. Verify the instance is reachable on SSH (with retry; new instances need
     a minute or two before sshd accepts connections).
  2. Capture the baseline environment (uname, python, torch, CUDA, free RAM,
     disk). Saved locally as data/lambda_bootstrap_<instance_id>.json for
     post-mortem if anything goes wrong.
  3. Install OS-level prereqs (git, build-essential) if missing.
  4. Clone the hd-instrument GitHub repo to /home/ubuntu/hd-instrument.
  5. Create + populate a venv with the project's requirements (torch first
     to lock CUDA compat, then the rest).
  6. Run a final Python-import smoke (numpy / torch.cuda / faiss / hdlab)
     to catch deps that installed cleanly but won't import.

Usage:
  python tools/cloud/bootstrap_instance.py <instance_id> [options]

  Required:
    instance_id         The Lambda instance ID (from canary or launch_instance)

  Common options:
    --ssh-key-path PATH   Local private key matching the Lambda-registered key
    --repo-url URL        Git URL (default: https://github.com/mcox79/hd-instrument)
    --branch NAME         Branch to check out (default: main)
    --requirements-file   Path inside repo (default: requirements_cloud.txt
                          falling back to requirements.txt)
    --skip-deps           Skip the dep install step (use after first bootstrap)

Exit codes:
  0  bootstrap succeeded; instance is ready to run experiments
  1  SSH unreachable / bad credentials
  2  dep install failed (instance left running; manual investigation needed)
  3  final import smoke failed (deps installed but won't import)
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
    timeout_s: float = 120.0,
) -> tuple[int, str, str]:
    """Run a single SSH command. Returns (returncode, stdout, stderr)."""
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
            cmd, capture_output=True, text=True, timeout=timeout_s
        )
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"timeout after {timeout_s}s")
    except FileNotFoundError:
        return (-1, "", "ssh binary not found on local machine")
    except Exception as exc:
        return (-1, "", f"subprocess error: {exc}")


def _wait_for_ssh(
    ip: str,
    ssh_key_path: str | None,
    timeout_s: float = 300.0,
    retry_interval_s: float = 10.0,
) -> bool:
    """Poll SSH until 'echo ready' returns 0 or timeout."""
    deadline = time.time() + timeout_s
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        rc, out, err = _ssh_run(ip, ssh_key_path, "echo ready", timeout_s=20)
        if rc == 0 and "ready" in out:
            print(f"  ssh reachable (attempt {attempt})")
            return True
        print(f"  attempt {attempt}: ssh not yet ready (rc={rc}); retry in {retry_interval_s}s")
        time.sleep(retry_interval_s)
    return False


def _capture_baseline(ip: str, ssh_key_path: str | None) -> dict:
    """Snapshot the instance's pre-bootstrap environment."""
    probe = (
        "echo '=== uname ==='; uname -a; "
        "echo '=== os-release ==='; cat /etc/os-release 2>/dev/null | head -5; "
        "echo '=== python ==='; which python3; python3 --version; "
        "echo '=== nvidia-smi ==='; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>&1 | head -2; "
        "echo '=== torch (system python) ==='; python3 -c 'import torch; print(torch.__version__); print(\"cuda:\", torch.cuda.is_available())' 2>&1 | head -3; "
        "echo '=== free ==='; free -g | head -2; "
        "echo '=== disk ==='; df -h / | tail -1; "
        "echo '=== git ==='; which git || echo 'git: missing'"
    )
    rc, out, err = _ssh_run(ip, ssh_key_path, probe, timeout_s=30)
    return {
        "ok": rc == 0,
        "returncode": rc,
        "stdout": out,
        "stderr": err,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _do_bootstrap(
    ip: str,
    ssh_key_path: str | None,
    repo_url: str,
    branch: str,
    requirements_file: str,
    skip_deps: bool,
) -> dict:
    """Run the install steps. Returns a dict of step-by-step results."""
    results: dict = {"steps": []}

    def _step(name: str, command: str, timeout_s: float = 600.0) -> bool:
        print(f"\n[bootstrap] {name} ...")
        rc, out, err = _ssh_run(ip, ssh_key_path, command, timeout_s=timeout_s)
        ok = rc == 0
        tail = (out[-800:] + err[-400:])[-1200:]
        results["steps"].append({"name": name, "rc": rc, "tail": tail, "ok": ok})
        print(f"  {'OK' if ok else 'FAIL'} (rc={rc})")
        if not ok:
            print(f"  stdout tail:\n{out[-1500:]}")
            print(f"  stderr tail:\n{err[-1500:]}")
        return ok

    # Stage 1: ensure git + build-essential.
    if not _step(
        "ensure-git",
        "sudo apt-get update -qq && sudo apt-get install -y git build-essential",
        timeout_s=300,
    ):
        results["fatal"] = "apt install failed"
        return results

    # Stage 2: clone (idempotent — pull if already cloned).
    clone_cmd = (
        f"if [ -d ~/hd-instrument/.git ]; then "
        f"  cd ~/hd-instrument && git fetch origin && git checkout {branch} && git pull --rebase; "
        f"else "
        f"  git clone --branch {branch} {repo_url} ~/hd-instrument; "
        f"fi"
    )
    if not _step("clone-repo", clone_cmd, timeout_s=180):
        results["fatal"] = "git clone failed"
        return results

    if skip_deps:
        print("\n[bootstrap] --skip-deps set; jumping to import smoke")
    else:
        # Stage 3: venv. CRITICAL: use --system-site-packages so the venv
        # inherits the image's pre-installed torch (Lambda's image ships
        # torch + CUDA matched to the driver; pip would otherwise pull a
        # newer torch that requires a newer CUDA driver -> CUDA disabled).
        # If the venv already exists from a prior run we leave it alone.
        venv_cmd = (
            "cd ~/hd-instrument && "
            "if [ ! -d .venv ]; then python3 -m venv --system-site-packages .venv; fi && "
            ".venv/bin/python -m pip install --upgrade pip wheel setuptools"
        )
        if not _step("create-venv", venv_cmd, timeout_s=180):
            results["fatal"] = "venv creation failed"
            return results

        # Stage 4: install requirements. Try cloud-specific first, fall back to main.
        # CRITICAL: do NOT install torch via the inline fallback. The image's
        # system torch is matched to the CUDA driver; pip-installing torch
        # pulls a newer build whose CUDA needs a newer driver.
        install_cmd = (
            "cd ~/hd-instrument && "
            f"REQ={requirements_file}; "
            "if [ ! -f $REQ ]; then "
            "  if [ -f requirements_cloud.txt ]; then REQ=requirements_cloud.txt; "
            "  elif [ -f requirements.txt ]; then REQ=requirements.txt; "
            "  else "
            "    echo 'no requirements file found; installing minimal deps (no torch)'; "
            "    .venv/bin/python -m pip install numpy scipy faiss-cpu fastapi pydantic httpx cryptography pytest pyyaml 2>&1 | tail -20; REQ=__inline__; "
            "  fi; "
            "fi && "
            "if [ \"$REQ\" != \"__inline__\" ] && [ \"$REQ\" != \"__none__\" ]; then "
            "  echo \"using $REQ\"; .venv/bin/python -m pip install -r $REQ 2>&1 | tail -40; fi"
        )
        if not _step("pip-install", install_cmd, timeout_s=900):
            results["fatal"] = "pip install failed"
            return results

    # Stage 5: import smoke. Use the venv if it exists, else system python.
    smoke_cmd = (
        "cd ~/hd-instrument && "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        "$PY - <<'PY'\n"
        "import sys\n"
        "print('python:', sys.version.split()[0])\n"
        "try:\n"
        "    import numpy as np; print('numpy:', np.__version__)\n"
        "except Exception as e: print('numpy IMPORT FAIL:', e)\n"
        "try:\n"
        "    import torch; print('torch:', torch.__version__, 'cuda:', torch.cuda.is_available(), 'device_count:', torch.cuda.device_count())\n"
        "except Exception as e: print('torch IMPORT FAIL:', e)\n"
        "try:\n"
        "    import faiss; print('faiss: ok')\n"
        "except Exception as e: print('faiss IMPORT FAIL:', e)\n"
        "try:\n"
        "    import hdlab; print('hdlab: ok')\n"
        "except Exception as e: print('hdlab IMPORT FAIL:', e)\n"
        "PY"
    )
    rc, out, err = _ssh_run(ip, ssh_key_path, smoke_cmd, timeout_s=120)
    results["import_smoke"] = {"rc": rc, "stdout": out, "stderr": err, "ok": rc == 0}
    print("\n[bootstrap] import smoke:")
    print(out or "(no stdout)")
    if err:
        print(f"(stderr) {err}")
    # Load-bearing checks: numpy + torch + cuda + hdlab. faiss is optional
    # (many experiments don't need it). Anything else missing is a warning.
    load_bearing_ok = (
        rc == 0
        and "numpy IMPORT FAIL" not in out
        and "torch IMPORT FAIL" not in out
        and "hdlab IMPORT FAIL" not in out
        and "cuda: True" in out  # explicit: torch.cuda must be available
    )
    # Warnings for non-load-bearing failures (e.g., faiss missing).
    optional_fails = []
    for marker in ("faiss IMPORT FAIL",):
        if marker in out:
            optional_fails.append(marker.split(" IMPORT FAIL")[0])
    if optional_fails:
        print(f"\n[WARN] optional deps missing (non-blocking): {optional_fails}")
    results["ok"] = bool(load_bearing_ok)
    results["optional_fails"] = optional_fails
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Lambda instance bootstrap")
    parser.add_argument("instance_id", help="Lambda instance ID to bootstrap")
    parser.add_argument("--ssh-key-path",
                        help="Local private key file (for SSH to ubuntu@<ip>)")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file with LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git",
                        help="Git URL to clone (default: project public repo)")
    parser.add_argument("--branch", default="main", help="Branch to check out")
    parser.add_argument("--requirements-file", default="requirements_cloud.txt",
                        help="Inside-repo requirements path "
                             "(falls back to requirements.txt then core deps)")
    parser.add_argument("--skip-deps", action="store_true",
                        help="Skip the pip-install step (use for subsequent bootstraps)")
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
    if inst is None:
        print(f"[ERROR] instance {args.instance_id!r} not found")
        return 1
    if inst.status != "active":
        print(f"[ERROR] instance status is {inst.status!r}; needs to be 'active'")
        return 1
    if not inst.ip:
        print(f"[ERROR] instance has no IP")
        return 1
    print(f"[bootstrap] target ip={inst.ip} type={inst.instance_type_name} "
          f"rate=${inst.hourly_rate_usd:.2f}/hr")

    # Stage 0: SSH reach.
    print("\n[1/3] Waiting for SSH...")
    if not _wait_for_ssh(inst.ip, args.ssh_key_path, timeout_s=300):
        print("[ERROR] SSH never became reachable")
        return 1

    # Stage 1: baseline.
    print("\n[2/3] Capturing baseline environment...")
    baseline = _capture_baseline(inst.ip, args.ssh_key_path)
    baseline_path = _REPO_ROOT / "data" / f"lambda_bootstrap_{args.instance_id}.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"  saved: {baseline_path}")
    print(baseline.get("stdout", "")[:2000])

    # Stage 2: bootstrap proper.
    print("\n[3/3] Bootstrapping repo + deps...")
    results = _do_bootstrap(
        ip=inst.ip,
        ssh_key_path=args.ssh_key_path,
        repo_url=args.repo_url,
        branch=args.branch,
        requirements_file=args.requirements_file,
        skip_deps=args.skip_deps,
    )

    # Persist the full result for post-mortem.
    out_path = _REPO_ROOT / "data" / f"lambda_bootstrap_result_{args.instance_id}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[bootstrap] result saved: {out_path}")

    if results.get("fatal"):
        print(f"\n[BOOTSTRAP FAILED] {results['fatal']}")
        return 2
    if not results.get("ok"):
        print("\n[BOOTSTRAP FAILED] import smoke detected missing modules")
        return 3
    print(f"\n[BOOTSTRAP OK] instance {args.instance_id} ({inst.ip}) is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
