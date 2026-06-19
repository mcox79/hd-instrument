"""PROT-018 audit: detect anchor _n<N> vs metrics-N mismatches and pre-PROT-018 backlog.

Two modes:

(1) Default -- scan LOCAL data/exp_*/metrics.json. Useful for finding stale local
    smoke artifacts that shadow remote FULL results (the dominant mode that fired
    78+ times on 2026-05-27 before PROT-018 landed).

(2) --remote -- fetch remote queue.json from marsh@home and report PENDING
    entries whose anchor has _n<N> suffix but whose source script's production
    config does NOT assign N=<suffix> (pre-PROT-018 backlog). queue_add.py
    exit-6 blocks these at SHIP time; this report names the ones that already
    slipped past.

ASCII-only output. Read-only.

Usage:
    python tools/audit_n_mismatch.py                    # local scan
    python tools/audit_n_mismatch.py --remote           # remote pending audit
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_N_SUFFIX_RE = re.compile(r"_n(\d+)(?:_|$)")


def _extract_anchor_n(name: str) -> int | None:
    m = _N_SUFFIX_RE.search(name)
    if m is None:
        return None
    try:
        return int(m.group(1))
    except (TypeError, ValueError):
        return None


def _extract_metrics_n(metrics) -> int | None:
    if not isinstance(metrics, dict):
        return None
    for key in ("summary", "config", "detail"):
        sub = metrics.get(key)
        if isinstance(sub, dict):
            val = sub.get("N")
            if val is None:
                val = sub.get("N_run")
            if isinstance(val, bool):
                continue
            try:
                return int(val)
            except (TypeError, ValueError):
                continue
    return None


def _script_has_production_N(script_path: Path, suffix_n: int) -> bool:
    """Mirror tools/queue_add.py check_n_suffix_binding's match logic.

    Returns True if the script source contains an N=<suffix_n> assignment
    that is not commented out.
    """
    if not script_path.exists():
        return False
    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    pattern = re.compile(
        r"(?:"
        r"\bN\s*=\s*" + str(suffix_n) + r"\b"
        r"|"
        r"\bn\s*=\s*" + str(suffix_n) + r"\b"
        r"|"
        r"\b[A-Z_]*N\s*=\s*" + str(suffix_n) + r"\b"
        r"|"
        r"default\s*=\s*" + str(suffix_n) + r"\b"
        r")"
    )
    for m in pattern.finditer(source):
        line_start = source.rfind("\n", 0, m.start()) + 1
        line_end = source.find("\n", m.end())
        if line_end == -1:
            line_end = len(source)
        matched_line = source[line_start:line_end].strip()
        if matched_line.lstrip().startswith("#"):
            continue
        return True
    return False


def scan_local() -> int:
    pattern = str(REPO / "data" / "exp_*" / "metrics.json")
    files = [Path(p) for p in glob.glob(pattern)]

    n_match = 0
    n_mismatch = 0
    n_no_metrics_n = 0
    mismatches = []
    no_metrics_n_entries = []

    for f in files:
        try:
            m = json.load(open(f, "r", encoding="utf-8", errors="replace"))
        except Exception:
            continue

        chosen_N = _extract_metrics_n(m)
        mode = None
        for key in ("config", "detail"):
            sub = m.get(key)
            if isinstance(sub, dict) and "mode" in sub:
                mode = sub["mode"]
                break

        dirname = f.parent.name.replace("exp_", "")
        suffix_n = _extract_anchor_n(dirname)
        if suffix_n is None:
            continue

        if chosen_N is None:
            n_no_metrics_n += 1
            no_metrics_n_entries.append((dirname, suffix_n, mode))
            continue

        if chosen_N != suffix_n:
            n_mismatch += 1
            mismatches.append((dirname, suffix_n, chosen_N, mode))
        else:
            n_match += 1

    print("=== LOCAL data/exp_*/metrics.json anchor-suffix-N audit ===")
    print(f"TOTAL _n<N> anchors with metrics: {n_match + n_mismatch + n_no_metrics_n}")
    print(f"  MATCH:           {n_match}")
    print(f"  MISMATCH:        {n_mismatch}")
    print(f"  NO_N_IN_METRICS: {n_no_metrics_n}")
    print()
    if mismatches:
        print("MISMATCH details (dirname suffix_N vs metrics_N mode):")
        for dname, suffix, actual, mode in mismatches:
            print(f"  {dname:60s} suffix_N={suffix:>6}  metrics_N={actual:>6}  mode={mode}")
    return 0 if n_mismatch == 0 else 2


def scan_remote() -> int:
    """Fetch remote queues via SSH and report pending _n<N> anchors whose
    source script lacks the N=<suffix> assignment (pre-PROT-018 backlog)."""
    queues = ("overnight_queue", "remote_cpu_queue")
    backlog = []
    for q in queues:
        remote_path = f"C:\\dev\\hd-instrument\\data\\{q}\\queue.json"
        try:
            out = subprocess.check_output(
                ["ssh", "marsh@home", f"type {remote_path}"],
                stderr=subprocess.DEVNULL,
                timeout=20,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception as e:
            print(f"WARN: SSH fetch failed for {q}: {e}", file=sys.stderr)
            continue
        try:
            doc = json.loads(out)
        except Exception as e:
            print(f"WARN: JSON parse failed for {q}: {e}", file=sys.stderr)
            continue

        exps = doc.get("experiments") or []
        for e in exps:
            if not isinstance(e, dict):
                continue
            if e.get("status") not in ("pending", "running"):
                continue
            name = e.get("name", "")
            suffix_n = _extract_anchor_n(name)
            if suffix_n is None:
                continue
            script_rel = e.get("script", "")
            script_path = REPO / script_rel
            has_n = _script_has_production_N(script_path, suffix_n)
            if not has_n:
                backlog.append((q, name, script_rel, suffix_n, e.get("status")))

    print("=== REMOTE queue pre-PROT-018 backlog audit ===")
    print(f"Pending/running _n<N> anchors lacking N=<suffix> in script: {len(backlog)}")
    if backlog:
        print()
        print("Backlog entries (queue / anchor / script / suffix_N / status):")
        for q, name, script, suffix, status in backlog:
            print(f"  {q:18s} {name:50s} suffix_N={suffix:>6} status={status} script={script}")
    return 0 if not backlog else 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remote", action="store_true",
                    help="Audit remote queues for pre-PROT-018 backlog")
    args = ap.parse_args(argv)
    if args.remote:
        return scan_remote()
    return scan_local()


if __name__ == "__main__":
    sys.exit(main())
