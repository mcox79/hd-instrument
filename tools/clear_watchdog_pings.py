#!/usr/bin/env python
"""Retention tool for notes/watchdog_ping_to_*.md and notes/blocker_ping_*.md.

Measured incident (meta_audit, 2026-08-14): 1585 watchdog_ping_to_<role>_<ts>.md files
in notes/ (15.7% of 10,081 total .md files there), produced continuously by the
`hd_session_watchdog` Windows Scheduled Task (tools/hd_session_watchdog.py, State=Running)
roughly every 10 minutes across 5 roles. The watchdog's designed delivery path is each
session's own v5 notes_monitor.sh (Phase-2, 4/5-session-fleet architecture) -- dead under
the current single-session Agent-spawn model (see CLAUDE.md "Notes directory
(single-session model)"). The one thing that actively reads notes/ (tools/dashboard/server.py)
explicitly SKIPS files matching "watchdog_ping" or "blocker_ping" in its scans (lines ~901,
993, 1081, 1118). Net: a scheduled task fires reliably and produces zero effect -- the
opposite failure mode from a silently-disabled cron, same root cause (no one reads what it
writes).

This tool does NOT touch the scheduled task (out of meta_audit's mandate -- "only stop/kill
what this session started"; the task predates this session). It only prunes the resulting
file clutter, following the same guard pattern as clear_scratch.py: refuses any target
outside notes/, matches ONLY the two ping filename patterns, dry-run by default, never
shells out to rm.

Usage:
  python tools/clear_watchdog_pings.py                # dry run: count + list a sample
  python tools/clear_watchdog_pings.py --older-than-hours 24 --yes   # delete matches
  python tools/clear_watchdog_pings.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = REPO_ROOT / "notes"

PING_RE = re.compile(r"^(watchdog_ping_to_[a-z_]+|blocker_ping_[a-z0-9_]+)_\d{8}T\d{6}Z\.md$", re.I)

GUARD_ENABLED = True


class GuardViolation(Exception):
    pass


def _real(p: Path) -> Path:
    return Path(os.path.realpath(str(p)))


def assert_under_notes(target: Path) -> None:
    if not GUARD_ENABLED:
        return
    rt, rr = _real(target), _real(NOTES_DIR)
    if rt == rr:
        raise GuardViolation(f"refusing to remove notes/ itself: {rt}")
    try:
        rt.relative_to(rr)
    except ValueError:
        raise GuardViolation(f"refusing target outside notes/: {rt}") from None
    if not PING_RE.match(target.name):
        raise GuardViolation(f"refusing non-ping-pattern filename: {target.name}")


def find_candidates(older_than_hours: float) -> list[Path]:
    now = time.time()
    cutoff = now - older_than_hours * 3600
    out = []
    for p in NOTES_DIR.iterdir():
        if not p.is_file():
            continue
        if not PING_RE.match(p.name):
            continue
        try:
            if p.stat().st_mtime <= cutoff:
                out.append(p)
        except OSError:
            continue
    return sorted(out, key=lambda x: x.name)


def run(older_than_hours: float, apply: bool) -> int:
    cands = find_candidates(older_than_hours)
    print(f"notes/ ping files matching pattern, older than {older_than_hours}h: {len(cands)}")
    for p in cands[:10]:
        print(f"  {p.name}")
    if len(cands) > 10:
        print(f"  ... and {len(cands) - 10} more")
    if not apply:
        print("DRY RUN -- pass --yes to delete. Nothing removed.")
        return len(cands)
    removed = 0
    for p in cands:
        try:
            assert_under_notes(p)
            p.unlink()
            removed += 1
        except (GuardViolation, OSError) as e:
            print(f"  SKIP {p.name}: {e}")
    print(f"Removed {removed}/{len(cands)}.")
    return removed


def self_test() -> None:
    import tempfile
    global NOTES_DIR
    orig_notes = NOTES_DIR
    with tempfile.TemporaryDirectory() as td:
        NOTES_DIR = Path(td)
        good = NOTES_DIR / "watchdog_ping_to_research_20260101T000000Z.md"
        good.write_text("x")
        bad = NOTES_DIR / "active_protocols.md"
        bad.write_text("real content")
        # guard: refuses non-matching filename even if passed directly
        try:
            assert_under_notes(bad)
            raise AssertionError("guard should have refused active_protocols.md")
        except GuardViolation:
            pass
        # guard: refuses path outside notes/
        outside = orig_notes.parent / "CLAUDE.md"
        try:
            assert_under_notes(outside)
            raise AssertionError("guard should have refused a path outside notes/")
        except GuardViolation:
            pass
        # matching file: found by dry run, removed by --yes
        os.utime(good, (time.time() - 3600 * 48, time.time() - 3600 * 48))
        n_found = run(older_than_hours=1, apply=False)
        assert n_found == 1, f"expected 1 dry-run candidate, got {n_found}"
        assert good.exists()
        n_removed = run(older_than_hours=1, apply=True)
        assert n_removed == 1, f"expected 1 removed, got {n_removed}"
        assert not good.exists()
        assert bad.exists(), "non-matching file must survive"
    NOTES_DIR = orig_notes
    print("SELF-TEST PASS: guard rejects non-pattern + outside-notes targets; matching pings removed cleanly.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--older-than-hours", type=float, default=48.0)
    ap.add_argument("--yes", action="store_true", help="actually delete (default: dry run)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    run(args.older_than_hours, apply=args.yes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
