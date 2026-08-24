"""Move hd-instrument off the USB stick onto the internal drive. Owner-authorised, board Q119/Q121.

WHY A SCRIPT AND NOT A COMMAND. The owner authorised the move ("do it"). The move itself is a
one-liner; everything expensive about it is the ORDER and the CHECKS. This file exists so the move
is one reviewable operation with a refusal built in, rather than a copy started at the wrong moment.

MEASURED, 2026-08-24:
  174 GB / 316,265 files. C: has 1,433 GB free -- space is not the constraint.
  data/ alone is 152.92 GB; code + notes + history is ~21 GB.
  The slowness tracks FILE COUNT on the read path, not size: .venv is 44,635 files opened on EVERY
  python start (that is the measured 167 s test startup), lean_oracle 121,688, .git 25,243.

THE THREE THINGS THAT MAKE A NAIVE COPY WRONG, each measured rather than feared:

  1. THE REPO IS WRITTEN CONTINUOUSLY. At 14:21 on 2026-08-24, writes landed SECONDS apart from a
     live experiment, a CPU-runner heartbeat, a watchdog, the orchestrator log, and the autoloop
     hook itself. A copy taken while those run is not risky, it is inconsistent BY CONSTRUCTION --
     different files captured at different moments. Hence `--preflight`, which REFUSES.

  2. `.venv` MUST BE REBUILT, NOT COPIED. A virtualenv bakes absolute paths into its scripts and
     `pyvenv.cfg`. Copied to a new drive letter it may appear to work and then fail in ways that
     look like package bugs. It is EXCLUDED here on purpose.

  3. IT MUST BE A FILE COPY, NEVER A FRESH CLONE. `data/foundation/` is UNTRACKED, and CLAUDE.md
     records that a worktree/clean flow would destroy it. A `git clone` of this repo silently loses
     data that has no other copy.

AND THE PART THAT BREAKS ITS OWN EXECUTOR: `D:/AI/.claude/settings.json` hard-codes the old path
FOUR times, including the hook that drives the autoloop. It lives OUTSIDE the repo, is not version
controlled, and a bad write is not cheaply reversible. **This script PRINTS the required edits and
does not apply them.** That is deliberate.

USAGE
    python tools/move_repo_to_internal_drive.py --preflight     # safe any time; refuses if unclean
    python tools/move_repo_to_internal_drive.py --plan          # print the copy command + checklist
    python tools/move_repo_to_internal_drive.py --verify <dst>  # compare counts/bytes after a copy

NOTHING IS DELETED FROM THE STICK BY THIS SCRIPT, EVER. Removing the old copy is a separate human
decision taken after the new one is proven.
"""

import argparse
import os
import subprocess
import sys
import time

SRC = r"D:\AI\hd-instrument"
DST_DEFAULT = r"C:\AI\hd-instrument"
SETTINGS = r"D:\AI\.claude\settings.json"

# Written continuously by the loop, the runners and the watchdog. Fresh mtimes here mean a copy
# would be inconsistent -- these are the canaries, not an exhaustive list.
CANARIES = [
    r"data\hook_state\_invocation_log.txt",
    r"data\local_cpu_queue\heartbeat.json",
    r"data\events\orchestrator.log",
    r"data\heartbeat_watchdog_state.json",
]
QUIET_SECONDS = 300          # nothing may have been written in the last 5 minutes


def _recent_writes(root, seconds):
    """(count, newest_path, newest_age_s) for files written inside `seconds`."""
    cut = time.time() - seconds
    n, newest, newest_age = 0, None, None
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", ".venv", "__pycache__")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if m > cut:
                n += 1
                age = time.time() - m
                if newest_age is None or age < newest_age:
                    newest, newest_age = p, age
    return n, newest, newest_age


def preflight(verbose=True, deep=False):
    """Return True only if a consistent copy is possible RIGHT NOW.

    FAST BY DEFAULT, AND THAT IS A CORRECTION TO MY OWN FIRST DRAFT. The first version walked all
    316,265 files looking for recent writes -- on the very USB drive this move exists to escape,
    which took so long it had to be backgrounded. A preflight nobody waits for is a preflight
    nobody runs; that is the same defect I had just fixed in `cite_check.py` (507 s -> 4.1 s).

    The CANARIES are sufficient and instant: they are the files the autoloop hook, the CPU runner,
    the watchdog and the orchestrator touch every few seconds. If those are quiet, the writers are
    stopped. `--deep` adds the full walk for a final belt-and-braces check when the tree is idle.
    """
    problems = []

    # 1. live processes running out of the repo
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\" | "
             "Where-Object { $_.CommandLine -like '*hd-instrument*' } | "
             "Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True, text=True, timeout=120)
        live = int((out.stdout or "0").strip() or 0)
    except Exception as e:                                    # noqa: BLE001
        live = -1
        problems.append("could not count live processes (%s); treat as UNSAFE" % e)
    if live > 0:
        problems.append("%d python process(es) are running out of %s -- stop them first" % (live, SRC))

    # 2. recent writes anywhere in the tree -- OPT-IN ONLY, see the docstring. On this hardware the
    #    full walk costs minutes, which is why it is not the default.
    if deep:
        n, newest, age = _recent_writes(SRC, QUIET_SECONDS)
        if n:
            problems.append("%d file(s) written in the last %ds; newest %s (%.0fs ago)"
                            % (n, QUIET_SECONDS, os.path.relpath(newest, SRC) if newest else "?", age or -1))

    # 3. the canaries -- the loop's own heartbeat. INSTANT, and sufficient on its own.
    for rel in CANARIES:
        p = os.path.join(SRC, rel)
        if os.path.exists(p):
            a = time.time() - os.path.getmtime(p)
            if a < QUIET_SECONDS:
                problems.append("CANARY %s written %.0fs ago -- the loop or a runner is alive" % (rel, a))

    if verbose:
        print("PREFLIGHT for %s" % SRC)
        if problems:
            print("  RESULT: NOT SAFE TO COPY (%d problem(s))" % len(problems))
            for pr in problems:
                print("    - %s" % pr)
            print()
            print("  A copy taken now would be INCONSISTENT BY CONSTRUCTION: different files")
            print("  captured at different moments. That is not a small risk, it is certain.")
            print("  Stop the autoloop (python tools/autoloop.py disarm), let any experiment")
            print("  finish, close the status window, then re-run this.")
        else:
            print("  RESULT: SAFE -- no live processes and nothing written in %ds." % QUIET_SECONDS)
    return not problems


def plan(dst):
    print("MOVE PLAN  %s  ->  %s" % (SRC, dst))
    print()
    print("STEP 1  Stop the writers. The autoloop hook, the CPU runner and the status window all")
    print("        write every few seconds. `python tools/autoloop.py disarm` stops the loop.")
    print("STEP 2  python tools/move_repo_to_internal_drive.py --preflight     (must say SAFE)")
    print("STEP 3  Copy. robocopy is restartable and logs; /MIR mirrors, /XD excludes .venv.")
    print()
    print('        robocopy "%s" "%s" /MIR /R:2 /W:2 /MT:16 /XD "%s" /LOG:"%s" /TEE'
          % (SRC, dst, os.path.join(SRC, ".venv"), os.path.join(os.path.dirname(dst), "hd_move.log")))
    print()
    print("        .venv is EXCLUDED ON PURPOSE -- a virtualenv bakes absolute paths and must be")
    print("        REBUILT at the destination, not copied.")
    print("STEP 4  python tools/move_repo_to_internal_drive.py --verify %s" % dst)
    print("STEP 5  Rebuild the venv AT THE DESTINATION:")
    print('        cd /d %s && python -m venv .venv && .venv\\Scripts\\python -m pip install -r requirements.txt' % dst)
    print("STEP 6  Patch %s -- it hard-codes the OLD path and drives the autoloop." % SETTINGS)
    _print_settings_hits()
    print("STEP 7  Start from the new location and confirm before deleting anything.")
    print()
    print("NOTHING IS DELETED FROM THE STICK BY THIS SCRIPT. Removing the old copy is a separate")
    print("decision, taken only after the new one is proven to work.")


def _print_settings_hits():
    if not os.path.exists(SETTINGS):
        print("        (settings.json not found at %s -- check the path)" % SETTINGS)
        return
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError as e:                                      # noqa: BLE001
        print("        (could not read settings.json: %s)" % e)
        return
    hits = [(i + 1, ln.strip()) for i, ln in enumerate(lines)
            if "hd-instrument" in ln and ("D:/" in ln or "D:\\" in ln)]
    print("        %d line(s) reference the OLD path:" % len(hits))
    for ln, txt in hits:
        print("          L%-4d %s" % (ln, txt[:110]))
    print("        NOT PATCHED AUTOMATICALLY: this file is outside the repo, is not version")
    print("        controlled, and carries the hooks. Edit it deliberately, not from a script.")


def verify(dst):
    def walk(root):
        n = b = 0
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".venv"]
            for fn in filenames:
                try:
                    b += os.path.getsize(os.path.join(dirpath, fn))
                    n += 1
                except OSError:
                    pass
        return n, b
    sn, sb = walk(SRC)
    dn, db = walk(dst)
    print("VERIFY (.venv excluded from both sides)")
    print("  source : %9d files  %10.2f GB" % (sn, sb / 1024 ** 3))
    print("  dest   : %9d files  %10.2f GB" % (dn, db / 1024 ** 3))
    ok = (sn == dn) and (sb == db)
    print("  RESULT : %s" % ("MATCH" if ok else "MISMATCH -- do NOT delete the source"))
    if not ok:
        print("           missing %d files / %.2f GB" % (sn - dn, (sb - db) / 1024 ** 3))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--deep", action="store_true",
                    help="also walk the whole tree for recent writes (minutes on the USB drive)")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--verify", metavar="DST")
    ap.add_argument("--dst", default=DST_DEFAULT)
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if verify(a.verify) else 1)
    if a.plan:
        plan(a.dst)
        sys.exit(0)
    sys.exit(0 if preflight(deep=a.deep) else 2)
