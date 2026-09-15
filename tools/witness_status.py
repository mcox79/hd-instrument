#!/usr/bin/env python3
"""Print the newest witness-execution manifest, plainly.

WHY: `pytest verification/` reporting "N passed" does not say which of the 622 files those N
came from -- see notes/problems/447_witness_files_define_no_test_function_.../PROBLEM.md. The
manifest (written by verification/_witness_manifest.py, a pytest plugin, on every run) says
exactly which witnesses ran, their tier, and their outcome; this script is the plain-language
read of it.

Usage:
    .venv/Scripts/python.exe tools/witness_status.py            # newest manifest, summary
    .venv/Scripts/python.exe tools/witness_status.py --list     # every manifest on disk, newest first
    .venv/Scripts/python.exe tools/witness_status.py --failed   # list the failed/errored nodeids
"""
from __future__ import annotations

import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_DIR = os.path.join(ROOT, "data", "hook_state")
MANIFEST_GLOB = os.path.join(MANIFEST_DIR, "witness_manifest_*.json")


def _manifests():
    return sorted(glob.glob(MANIFEST_GLOB), reverse=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="list every manifest on disk, newest first")
    ap.add_argument("--failed", action="store_true", help="print just the failed/errored nodeids")
    ap.add_argument("--n", type=int, default=1, help="how many recent manifests to summarize (default 1)")
    args = ap.parse_args(argv)

    paths = _manifests()
    if not paths:
        print("no witness manifest found under %s -- run `pytest verification/` (or -m fast / "
              "-m corpus / -m slow) at least once first." % MANIFEST_DIR)
        return 1

    if args.list:
        for p in paths:
            print(os.path.basename(p))
        return 0

    for path in paths[: max(1, args.n)]:
        manifest = json.load(open(path, encoding="utf-8"))
        totals = manifest["totals"]
        print("=" * 78)
        print("manifest: %s" % os.path.basename(path))
        print("run started (UTC): %s   markexpr: %r" % (manifest["run_utc"], manifest["markexpr"]))
        print("collected %(collected)d witness test(s); %(ran)d actually RAN this session "
              "(passed=%(passed)d failed=%(failed)d error=%(error)d skipped=%(skipped)d)"
              % totals)
        if totals["collected"] > totals["ran"]:
            print("  -> %d collected item(s) were DESELECTED by the marker expression and did "
                  "NOT run this session -- that is expected for -m fast excluding corpus/slow, "
                  "not a bug." % (totals["collected"] - totals["ran"]))
        by_tier = {}
        for row in manifest["items"]:
            by_tier.setdefault(row.get("tier") or "(untiered)", []).append(row)
        for tier, rows in sorted(by_tier.items()):
            n_fail = sum(1 for r in rows if r["outcome"] not in ("passed", "skipped"))
            total_s = sum(r["seconds"] for r in rows)
            print("  tier %-10s %4d ran, %2d failed/errored, %8.2fs total"
                  % (tier, len(rows), n_fail, total_s))
        if args.failed:
            bad = [r for r in manifest["items"] if r["outcome"] not in ("passed", "skipped")]
            if bad:
                print("  FAILED/ERRORED:")
                for r in bad:
                    print("    %s (%s, %.2fs)" % (r["nodeid"], r["outcome"], r["seconds"]))
            else:
                print("  (none failed/errored in this run)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
