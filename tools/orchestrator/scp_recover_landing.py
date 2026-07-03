#!/usr/bin/env python3
"""SCP-recover a landing's metrics artifacts from remote (marsh@home) to local.

Load-bearing gap this fixes (2026-07-01 Wave 21 LLN + Wave 23 M1.6 v2 incident):
    hd_metrics_sync `last_run_utc` update is necessary but NOT sufficient. Even
    AFTER the scheduled sync task ran, the local `data/exp_<anchor>/metrics.json`
    may still be missing because:
      (a) the remote tar was built BEFORE the cell landed (20-min cadence gap), OR
      (b) the tarball skipped the file (size cap / walk-timing), OR
      (c) the tar-pipe merge is only mtime-newer-wins and remote file exists
          but wasn't in the tar snapshot at build time.

    Orchestrator confirmed today: even after status.json last_run_utc updated,
    verify_landing.py returned metrics_path_missing on the two anchors until
    explicit SCP-per-file recovery ran.

    This tool is the on-demand SCP recovery path — call it BEFORE framing an
    expected-landing as failed, whenever verify_landing.py fails but the queue
    entry says completed/terminal.

Usage:
    python tools/orchestrator/scp_recover_landing.py <anchor> [<anchor> ...]
    python tools/orchestrator/scp_recover_landing.py --anchor a1 --anchor a2
    python tools/orchestrator/scp_recover_landing.py --dry-run <anchor>
    python tools/orchestrator/scp_recover_landing.py --verify-after <anchor>
    python tools/orchestrator/scp_recover_landing.py --files metrics.json,verdict.json <anchor>

Remote layout assumed: marsh@home:C:/dev/hd-instrument/data/exp_<anchor>/<file>
Local layout: D:/AI/hd-instrument/data/exp_<anchor>/<file>

Exit codes:
    0 = all anchors recovered (or already-fresh)
    1 = at least one anchor failed recovery
    2 = usage error

Cross-refs:
    tools/verify_landing.py  — post-recovery verification
    tools/orchestrator/local_metrics_sync.ps1  — recurring 20-min sync
    tools/orchestrator/remote_metrics_tar.py  — tarball builder
    Discipline: hdi_orchestrator.md SH-9 (SCP post-sync data/ subdir gap)
    Incident: 2026-07-01 21:34Z Wave 21 LLN + 21:40Z sync + 21:42Z verify miss + 21:45Z SCP recover
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DATA = REPO / "data"
REMOTE_HOST = "marsh@home"
REMOTE_ROOT = "C:/dev/hd-instrument/data"

# Load-bearing landing artifacts (matches remote_metrics_tar.py LOAD_BEARING set).
DEFAULT_FILES = ["metrics.json", "results.json", "provenance.json",
                 "verdict.json", "recent_verdicts.json"]

SSH_OPTS = [
    "-o", "ConnectTimeout=15",
    "-o", "BatchMode=yes",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=3",
]


def _resolve_local_dir(anchor: str) -> Path:
    """Return the local target directory for an anchor.

    Anchor `exp_foo` maps to `data/exp_foo/`. Anchor `foo` maps to `data/exp_foo/`.
    (Matches verify_landing.py canonical resolution; SH-4 double-prefix left for
    the caller to detect via verify_landing.py after recovery.)
    """
    if anchor.startswith("exp_"):
        return DATA / anchor
    return DATA / f"exp_{anchor}"


def _remote_path(anchor: str, filename: str) -> str:
    """Build the remote path for scp source spec (canonical stem)."""
    stem = anchor if anchor.startswith("exp_") else f"exp_{anchor}"
    return f"{REMOTE_ROOT}/{stem}/{filename}"


def _remote_path_sh4(anchor: str, filename: str) -> str:
    """Build the SH-4 double-prefix remote path candidate.

    Runner writes `data/exp_exp_<anchor>/` when queue entry begins with `exp_`
    (see experiments/_seed_checkpoint.get_output_dir). Callers try canonical
    first then fall back here. Testbed 2026-07-03 fleet audit.
    """
    stem = anchor if anchor.startswith("exp_") else f"exp_{anchor}"
    return f"{REMOTE_ROOT}/exp_{stem}/{filename}"


def _run_bounded(cmd: list[str], timeout_s: int = 45) -> tuple[int, str, str]:
    """Run cmd with wall-timeout. Returns (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s,
            # No shell; args as list; no creationflags (this is a CLI tool,
            # not a scheduled task — popup discipline doesn't apply here).
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", (e.stderr or "") + f"\n[timeout after {timeout_s}s]"
    except FileNotFoundError as e:
        return 127, "", f"[executable not found: {e}]"


def _remote_file_exists(anchor: str, filename: str) -> bool:
    """Probe remote for file existence via ssh Test-Path (bounded)."""
    remote = _remote_path(anchor, filename)
    # Use PowerShell Test-Path so we get a reliable True/False sentinel.
    ps = f"if (Test-Path '{remote}') {{ 'YES' }} else {{ 'NO' }}"
    cmd = ["ssh", *SSH_OPTS, REMOTE_HOST,
           f"powershell -NoProfile -Command \"{ps}\""]
    rc, out, _ = _run_bounded(cmd, timeout_s=30)
    if rc != 0:
        return False
    return "YES" in (out or "").upper()


def _scp_one(anchor: str, filename: str, dry_run: bool = False) -> tuple[bool, str]:
    """SCP a single anchor+file remote->local. Returns (ok, msg).

    Skips silently (ok=True) when the file doesn't exist remotely - many landings
    only write metrics.json + verdict.json, so absence of results.json is normal.

    SH-4: probes canonical remote path first, then double-prefix
    (data/exp_exp_<anchor>/). Recovery pulls to canonical local dir either way
    so downstream verify_landing.py hits the SH-4-normalized target.
    """
    remote_source = _remote_path(anchor, filename)
    if not _remote_file_exists(anchor, filename):
        # Try SH-4 double-prefix on remote.
        remote_source_sh4 = _remote_path_sh4(anchor, filename)
        ps = f"if (Test-Path '{remote_source_sh4}') {{ 'YES' }} else {{ 'NO' }}"
        cmd = ["ssh", *SSH_OPTS, REMOTE_HOST,
               f"powershell -NoProfile -Command \"{ps}\""]
        rc, out, _ = _run_bounded(cmd, timeout_s=30)
        if rc != 0 or "YES" not in (out or "").upper():
            return True, f"remote missing (skip): {filename}"
        remote_source = remote_source_sh4

    local_dir = _resolve_local_dir(anchor)
    if not dry_run:
        local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / filename
    remote_spec = f"{REMOTE_HOST}:{remote_source}"

    if dry_run:
        return True, f"DRY: scp {remote_spec} {local_path}"

    cmd = ["scp", *SSH_OPTS, remote_spec, str(local_path)]
    rc, out, err = _run_bounded(cmd, timeout_s=60)
    if rc == 0 and local_path.exists():
        sh4_tag = " [SH-4]" if "/exp_exp_" in remote_source else ""
        return True, f"copied{sh4_tag}: {filename} ({local_path.stat().st_size} bytes)"
    reason = (err or out or "").strip().splitlines()
    reason_s = reason[-1] if reason else f"rc={rc}"
    return False, f"scp fail {filename}: {reason_s}"


def recover_anchor(anchor: str, files: list[str], dry_run: bool = False) -> dict:
    """Recover one anchor's load-bearing files. Returns per-file result dict."""
    started = time.time()
    result = {"anchor": anchor, "files": {}, "ok": True, "wall_s": 0.0}
    for fn in files:
        ok, msg = _scp_one(anchor, fn, dry_run=dry_run)
        result["files"][fn] = {"ok": ok, "msg": msg}
        # Only metrics.json is load-bearing for verify_landing.py. results.json /
        # provenance.json / verdict.json / recent_verdicts.json are secondary —
        # scp fail on them shouldn't fail the whole anchor. But if metrics.json
        # can't be recovered, that's a hard failure.
        if not ok and fn == "metrics.json":
            result["ok"] = False
    result["wall_s"] = round(time.time() - started, 2)
    return result


def verify_after(anchors: list[str]) -> tuple[int, str]:
    """Invoke tools/verify_landing.py on the recovered anchors. Returns (rc, output)."""
    verify_script = REPO / "tools" / "verify_landing.py"
    if not verify_script.exists():
        return 2, f"verify_landing.py not found at {verify_script}"
    cmd = [sys.executable, str(verify_script), *anchors]
    rc, out, err = _run_bounded(cmd, timeout_s=30)
    return rc, (out or "") + (("\n" + err) if err else "")


def _fmt_result(r: dict) -> str:
    tag = "OK  " if r["ok"] else "FAIL"
    lines = [f"{tag} {r['anchor']}  wall_s={r['wall_s']}"]
    for fn, sub in r["files"].items():
        sub_tag = "  ok" if sub["ok"] else "FAIL"
        lines.append(f"    {sub_tag}  {fn}: {sub['msg']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="SCP-recover landing metrics artifacts from marsh@home to local.")
    p.add_argument("anchors", nargs="*", help="one or more anchor names")
    p.add_argument("--anchor", action="append", default=[],
                   help="anchor name (repeatable; alternative to positional)")
    p.add_argument("--files", default=",".join(DEFAULT_FILES),
                   help=f"comma-list of files to pull (default: {','.join(DEFAULT_FILES)})")
    p.add_argument("--dry-run", action="store_true",
                   help="print what would be pulled; do not execute scp")
    p.add_argument("--verify-after", action="store_true",
                   help="after recovery, run tools/verify_landing.py on the anchors")
    args = p.parse_args(argv)

    anchors = list(args.anchors) + list(args.anchor)
    if not anchors:
        p.print_usage()
        print("error: at least one anchor required", file=sys.stderr)
        return 2

    files = [f.strip() for f in args.files.split(",") if f.strip()]
    if not files:
        print("error: --files list empty", file=sys.stderr)
        return 2

    all_ok = True
    for anchor in anchors:
        r = recover_anchor(anchor, files, dry_run=args.dry_run)
        print(_fmt_result(r))
        if not r["ok"]:
            all_ok = False

    if args.verify_after and not args.dry_run:
        print("\n--- verify_landing.py ---")
        rc, out = verify_after(anchors)
        print(out.rstrip())
        # Fold verify result into exit code — if verify fails on any anchor,
        # signal that so callers know the recovery didn't close the loop.
        if rc != 0:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
