#!/usr/bin/env python3
"""notes_monitor.py -- Python port of notes_monitor.sh (v5).

WHY THIS VERSION: the bash version spawned a 4-stage pipeline (find | grep | grep | sort)
every 20 seconds. Each child binary (find.exe / grep.exe / sort.exe) caused Windows
to allocate a fresh console under Claude Code's hidden-console process, producing a
visible popup flash. This Python version does the same set-diff logic in-process
(os.scandir + Python re + set ops) with ZERO subprocess spawns. After the initial arm,
no popups.

Filter discipline (unchanged from v5 bash): a note is "for me" if its filename contains
<session> OR `to_all` OR `_all_`, EXCLUDING own outgoing (filename starting "<session>_").
Each new note printed once as: NOTE-FOR-<SESS>: <filename>

Usage:  python tools/notes_monitor.py <session>
Invoked by the Monitor tool. Stdout is line-buffered.
"""
from __future__ import annotations

import os
import re
import sys
import time

if len(sys.argv) < 2:
    sys.stderr.write("usage: python tools/notes_monitor.py <session>\n")
    sys.exit(2)

SESS = sys.argv[1].strip()
ROOT = r"D:\AI\hd-instrument"
NOTES_DIR = os.path.join(ROOT, "notes")
LABEL = f"NOTE-FOR-{SESS.upper()}:"
SLEEP_SECONDS = 20

try:
    os.chdir(ROOT)
except OSError as e:
    sys.stderr.write(f"MONITOR-ERROR: cannot cd {ROOT}: {e}\n")
    sys.exit(1)

INCLUDE = re.compile(rf"{re.escape(SESS)}|_to_all_|_all_", re.IGNORECASE)
EXCLUDE = re.compile(rf"^{re.escape(SESS)}_", re.IGNORECASE)


def list_matching() -> set[str]:
    out: set[str] = set()
    try:
        with os.scandir(NOTES_DIR) as it:
            for entry in it:
                name = entry.name
                if not name.endswith(".md"):
                    continue
                if INCLUDE.search(name) and not EXCLUDE.search(name):
                    out.add(name)
    except FileNotFoundError:
        pass
    return out


seen = list_matching()

print(
    f"MONITOR-ARMED: notes_monitor for {SESS} "
    f"(Python port; in-process scan; no subprocess spawns)",
    flush=True,
)

while True:
    time.sleep(SLEEP_SECONDS)
    cur = list_matching()
    new = cur - seen
    if new:
        for name in sorted(new):
            print(f"{LABEL} {name}", flush=True)
        seen |= new
