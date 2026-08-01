#!/usr/bin/env python3
"""Director-KB freshness gate (testbed 2026-08-01; ANCHOR durability fix).

WHY THIS EXISTS: the continuous-ingest loop (`tools/director_kb_continuous_ingest.py`,
scheduled as Windows task `hd_director_kb_continuous_ingest`, --once every 5 min) is
enforced ONLY by that scheduler entry. On 2026-07-26 the scheduled task was silently
DISABLED (same failure class as the 2026-07-16..07-28 "11 hd_* tasks silently disabled"
incident documented in CLAUDE.md / MEMORY.md) and nothing noticed for 6 days: the
queryable director_kb went stale (director_kb_query.py kept answering, just with
2026-07-26-and-earlier content) while notes/preregs/metrics kept landing on disk only.

Per the USER-locked discipline "durability = SESSION-START READ, not crons" (CLAUDE.md
Capability tracking section), a cron is a backstop, never the enforcement mechanism.
This script is the READ-side enforcement: run it every session start (wired next to
`tools/capability_registry_audit.py` in the SESSION STARTUP RITUAL) and it will LOUDLY
flag staleness on stdout/stderr (exit code 1) regardless of what the scheduler is doing,
and optionally kick a catch-up ingest itself (--fix).

Staleness definition: compare `data/director_kb_continuous_state.json`'s
`last_scan_max_mtime` against the newest mtime actually observed under notes/ and
preregs/ (the two source classes that land fastest + carry tonight's content). If the
gap exceeds --stale-threshold-sec (default 1800s = 30min, generous vs the 5-min poll
cadence so a mid-ingest run doesn't false-positive) OR the state file's own
last_ingest_ts is older than --max-index-age-sec (default 3600s), the KB is STALE.

Usage:
  python tools/director_kb_freshness_check.py                # report only, exit 1 if stale
  python tools/director_kb_freshness_check.py --fix           # + trigger chunked catch-up
  python tools/director_kb_freshness_check.py --self-test

ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE_PATH = REPO / "data" / "director_kb_continuous_state.json"
FAST_DIRS = ["notes", "preregs"]

DEFAULT_STALE_THRESHOLD_SEC = 1800.0
DEFAULT_MAX_INDEX_AGE_SEC = 3600.0


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _newest_mtime(dirs: list[str]) -> float:
    """Newest file mtime under `dirs` (recursive).

    Uses os.scandir with the DirEntry's cached stat (populated by the underlying
    readdir on Windows) instead of Path.rglob + a fresh f.stat() syscall per
    file. Over the ~33k files under notes/+preregs/ the rglob+stat form took 5+
    min under concurrent I/O (a KB load + a peer session's queries were running);
    the scandir form is the same popup-free in-process pattern the testbed
    monitor ports use and completes in low single-digit seconds. This gate runs
    at session start, so it must be fast.
    """
    newest = 0.0
    stack = [str(REPO / d) for d in dirs]
    while stack:
        cur = stack.pop()
        try:
            it = os.scandir(cur)
        except OSError:
            continue
        with it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        mt = entry.stat(follow_symlinks=False).st_mtime
                        if mt > newest:
                            newest = mt
                except OSError:
                    continue
    return newest


def check(stale_threshold_sec: float, max_index_age_sec: float) -> dict:
    state = _load_state()
    now = time.time()
    last_scan_max_mtime = float(state.get("last_scan_max_mtime", 0.0))
    last_ingest_ts = float(state.get("last_ingest_ts", 0.0))
    disk_newest = _newest_mtime(FAST_DIRS)

    scan_gap_sec = max(0.0, disk_newest - last_scan_max_mtime)
    index_age_sec = max(0.0, now - last_ingest_ts) if last_ingest_ts else float("inf")

    stale = (scan_gap_sec > stale_threshold_sec) or (index_age_sec > max_index_age_sec)

    return {
        "stale": stale,
        "scan_gap_sec": scan_gap_sec,
        "index_age_sec": index_age_sec,
        "last_scan_max_mtime": last_scan_max_mtime,
        "last_ingest_ts": last_ingest_ts,
        "disk_newest_mtime_fast_dirs": disk_newest,
        "n_failed_ingests": state.get("n_failed_ingests"),
        "last_coverage_check_ok": state.get("last_coverage_check_ok"),
    }


def _fmt_ts(ts: float) -> str:
    if not ts:
        return "never"
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stale-threshold-sec", type=float, default=DEFAULT_STALE_THRESHOLD_SEC)
    ap.add_argument("--max-index-age-sec", type=float, default=DEFAULT_MAX_INDEX_AGE_SEC)
    ap.add_argument("--fix", action="store_true",
                     help="If stale, launch a catch-up ingest (director_kb_continuous_ingest.py --once) "
                          "in the background and report it was triggered (does not wait for completion).")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args()

    if args.self_test:
        result = check(args.stale_threshold_sec, args.max_index_age_sec)
        assert "stale" in result
        assert isinstance(result["scan_gap_sec"], float)
        print("[selftest] director_kb_freshness_check PASS", flush=True)
        return 0

    result = check(args.stale_threshold_sec, args.max_index_age_sec)

    if not result["stale"]:
        print(f"[director-kb-freshness] OK last_ingest={_fmt_ts(result['last_ingest_ts'])} "
              f"scan_gap={result['scan_gap_sec']:.0f}s index_age={result['index_age_sec']:.0f}s")
        return 0

    print("=" * 78, file=sys.stderr)
    print("[director-kb-freshness] *** STALE INDEX ***", file=sys.stderr)
    print(f"  last successful ingest scan covers up to: {_fmt_ts(result['last_scan_max_mtime'])}", file=sys.stderr)
    print(f"  newest file on disk (notes/preregs):      {_fmt_ts(result['disk_newest_mtime_fast_dirs'])}", file=sys.stderr)
    print(f"  scan_gap={result['scan_gap_sec']:.0f}s index_age={result['index_age_sec']:.0f}s "
          f"n_failed_ingests={result['n_failed_ingests']} coverage_ok={result['last_coverage_check_ok']}", file=sys.stderr)
    print("  ACTION: director_kb queries are answering STALE content. Check whether the "
          "hd_director_kb_continuous_ingest scheduled task is Disabled (Get-ScheduledTask), "
          "and/or run: python tools/director_kb_continuous_ingest.py --once", file=sys.stderr)
    print("=" * 78, file=sys.stderr)

    if args.fix:
        log_path = REPO / "data" / "director_kb_freshness_autofix.log"
        with open(log_path, "ab") as lf:
            subprocess.Popen(
                [sys.executable, str(REPO / "tools" / "director_kb_continuous_ingest.py"),
                 "--once", "--quiet"],
                stdout=lf, stderr=lf,
                creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
            )
        print(f"[director-kb-freshness] --fix: launched catch-up ingest in background, "
              f"log={log_path}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
