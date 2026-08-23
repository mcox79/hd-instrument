#!/usr/bin/env python
"""For each recent note, is its headline NUMBER actually present in the plan or STATUS?

WHY THIS EXISTS. On 2026-08-23 I folded a night's work into the plan and STATUS, then checked with a
list of ten literals. One was missing -- `+0.0232`, the anchor-clustering gap -- and it was not a
casualty of line-merging: **the word CLUSTERED appeared nowhere in the plan.** The two-session
reconciliation, the most important scientific finding of that night, had reached STATUS and its own
note and never reached the plan. I had folded a different thread in and assumed this one went with
it.

**A NOTE NOBODY FOLDED FORWARD IS INVISIBLE.** `notes/` is not injected at session start; the plan
and `STATUS.md` are what a recovering session reads. A finding that lives only in a note is one
compaction away from not existing, and the failure is SILENT -- the note is still there, so nothing
looks wrong.

WHAT THIS CHECKS, and its limits are stated rather than hidden: it extracts decimal literals from
each note and asks whether ANY of them appears in the plan or STATUS. That is a WEAK test -- a note
can be properly represented by prose with no shared number, and a number can coincide by accident.
**It is a triage flag, not a verdict**, and its output is a list to look at rather than a list to act
on.

    python tools/did_the_finding_reach_the_plan.py            # notes from the last 2 days
    python tools/did_the_finding_reach_the_plan.py --days 7
    python tools/did_the_finding_reach_the_plan.py --self-test
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(REPO, "notes", "BUILD_PLAN_post_audit_2026-08-19.md")
STATUS = os.path.join(REPO, "notes", "STATUS.md")

# 3+ decimals: distinctive enough that a coincidental match is unlikely, unlike "0.5" or "12".
NUM = re.compile(r"\b\d+\.\d{3,4}\b")


def _read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def audit(days=2):
    plan, status = _read(PLAN), _read(STATUS)
    if not plan or not status:
        print("[audit] REFUSING: could not read the plan or STATUS -- a silent empty read here would")
        print("        report every note as unreached, which is the opposite of the truth.")
        return 2

    cutoff = time.time() - days * 86400
    notes = [p for p in glob.glob(os.path.join(REPO, "notes", "*.md"))
             if os.path.getmtime(p) >= cutoff]
    skip = ("STATUS.md", "STATUS_LESSONS.md", "BUILD_PLAN_post_audit_2026-08-19.md",
            "BOARD.md", "COMMENTARY.md", "STATUS_SPEC.md")
    notes = [p for p in notes if os.path.basename(p) not in skip]

    print("notes modified in the last %d day(s): %d" % (days, len(notes)))
    print("(excluding the destination documents themselves)")
    print()

    unreached, thin, fine, nonum = [], [], [], []
    for p in sorted(notes):
        t = _read(p)
        nums = set(NUM.findall(t))
        if not nums:
            nonum.append(p)
            continue
        hit = sum(1 for n in nums if n in plan or n in status)
        name = os.path.basename(p)
        if hit == 0:
            unreached.append((name, len(nums)))
        elif hit <= 2:
            thin.append((name, hit, len(nums)))
        else:
            fine.append((name, hit, len(nums)))

    if unreached:
        print("!! NONE OF THEIR NUMBERS APPEAR IN THE PLAN OR STATUS -- look at these first:")
        for name, tot in unreached:
            print("     %-72s (%d distinct numbers)" % (name[:72], tot))
    else:
        print("   every recent note has at least one number represented downstream")
    print()
    if thin:
        print("   thinly represented (1-2 numbers reached):")
        for name, hit, tot in thin:
            print("     %-64s %d of %d" % (name[:64], hit, tot))
    print()
    print("   well represented: %d note(s) | carry no decimal numbers: %d" % (len(fine), len(nonum)))
    print()
    print("REMEMBER WHAT THIS IS: a shared NUMBER is a proxy for a finding having been folded")
    print("forward. A note can be faithfully represented in prose and still flag here. Read the")
    print("flagged ones; do not bulk-edit on this output.")
    return 1 if unreached else 0


def self_test():
    ok = True
    plan, status = _read(PLAN), _read(STATUS)

    # POSITIVE CONTROL: the number whose absence caused this tool must now be present.
    if "0.0232" in plan or "0.0232" in status:
        print("[self-test] PASS the anchor-clustering gap 0.0232 is present downstream")
    else:
        print("[self-test] FAIL 0.0232 is still missing -- the incident that motivated this is live")
        ok = False

    # NEGATIVE CONTROL: an invented literal must NOT be found, or matching is vacuous.
    if "0.9182734655" not in plan and "0.9182734655" not in status:
        print("[self-test] PASS an invented literal is not found (matching is not vacuous)")
    else:
        print("[self-test] FAIL invented literal matched")
        ok = False

    # The extractor must find numbers in a real note, or every note reads as 'no numbers'.
    sample = sorted(glob.glob(os.path.join(REPO, "notes", "*2026-08-2*.md")))
    found = 0
    for p in sample[:6]:
        found += len(set(NUM.findall(_read(p))))
    if found > 0:
        print("[self-test] PASS the number extractor finds %d literals in real notes" % found)
    else:
        print("[self-test] FAIL extractor found nothing -- it would report every note as unreached")
        ok = False

    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    days = 2
    if "--days" in argv:
        try:
            days = int(argv[argv.index("--days") + 1])
        except (IndexError, ValueError):
            pass
    return audit(days)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
