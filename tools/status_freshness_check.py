"""Staleness guard for notes/STATUS.md.

Exits non-zero (with a clear message on stdout) if notes/STATUS.md is older than the newest
commit on the current branch -- i.e. work landed but STATUS.md was not updated to reflect it.

Report-only: the session-start hook surfaces this output as a warning. It never blocks
anything; nothing in this repo treats a non-zero exit here as fatal.

Usage: python tools/status_freshness_check.py
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATUS = REPO / 'notes' / 'STATUS.md'
GIT_TIMEOUT_SEC = 10


def main() -> int:
    if not STATUS.exists():
        print("STALE: notes/STATUS.md does not exist -- nothing to check freshness against.")
        return 1

    try:
        proc = subprocess.run(
            ['git', 'log', '-1', '--format=%ct'],
            cwd=str(REPO), capture_output=True, text=True, timeout=GIT_TIMEOUT_SEC,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"STALE-CHECK-ERROR: could not run git log ({exc}); treat as unknown, not fresh.")
        return 1
    if proc.returncode != 0 or not proc.stdout.strip():
        print(f"STALE-CHECK-ERROR: git log failed (exit {proc.returncode}): {proc.stderr.strip()}")
        return 1

    try:
        newest_commit_ts = int(proc.stdout.strip())
    except ValueError:
        print(f"STALE-CHECK-ERROR: unparseable git log output: {proc.stdout!r}")
        return 1

    status_mtime = STATUS.stat().st_mtime
    if status_mtime < newest_commit_ts:
        lag_h = (newest_commit_ts - status_mtime) / 3600.0
        print(
            f"STALE: notes/STATUS.md was last modified before the newest commit "
            f"(lag ~{lag_h:.1f}h). Work landed since STATUS.md was written -- rewrite it "
            f"in place (see the LEDGER CONVENTION note inside STATUS.md)."
        )
        return 1

    print("FRESH: notes/STATUS.md is at or after the newest commit.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
