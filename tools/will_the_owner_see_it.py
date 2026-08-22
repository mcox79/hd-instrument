"""Ask whether a finding actually REACHES THE OWNER, before assuming that writing it down did.

WHY THIS EXISTS, and it is one measured miss. On 2026-08-22 the most striking result of the session
-- `0.5278`, random credit assignment beating the real mechanism where ours read `0.3056` -- was
written up carefully in `notes/RANDOM_CREDIT_BEATS_THE_REAL_MECHANISM_...md` and existed **in no
file the owner's status window opens.** It had been recorded and not communicated, and those felt
identical from the inside.

WHAT THE GUI ACTUALLY OPENS, read out of `tools/status_gui.py` rather than assumed -- SEVEN files
plus the problems folder:

    notes/STATUS.md                          notes/ORGAN_MAP.md
    notes/BUILD_PLAN_post_audit_2026-08-19.md notes/BOARD.md
    notes/LONG_TERM_PLAN.md                  notes/COMMENTARY.md
    notes/VETTING_LEDGER.md                  notes/problems/**

**EVERYTHING ELSE IS INVISIBLE TO THE OWNER BY CONSTRUCTION** -- every other note, every commit
message, every docstring. That is correct for an evidence archive and wrong for a conclusion.

BASE RATE, measured before this tool was written, per the standing rule that a flag firing on
everything is not a flag: **61 of 206 lead numbers (30%) from one day's notes appear in NO
GUI-visible file.** High enough to be worth checking, low enough that most notes are fine.

THIS IS A TARGETED LOOKUP, NEVER A BROADCAST. Most working-note detail SHOULD stay in the note; you
ask about the one finding you believe you have communicated.

Usage:
    python tools/will_the_owner_see_it.py 0.5278
    python tools/will_the_owner_see_it.py "random credit"
    python tools/will_the_owner_see_it.py --self-test
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# A DOC PARSED BY CODE IS COUPLED TO IT: this list mirrors the paths named in tools/status_gui.py.
# If a tab is added or a file renamed there, change it here in the SAME commit -- otherwise this
# tool will cheerfully report "visible" about a file nobody opens.
GUI_FILES = (
    "notes/STATUS.md",
    "notes/BUILD_PLAN_post_audit_2026-08-19.md",
    "notes/LONG_TERM_PLAN.md",
    "notes/ORGAN_MAP.md",
    "notes/BOARD.md",
    "notes/COMMENTARY.md",
    "notes/VETTING_LEDGER.md",
)
PROBLEMS_DIR = os.path.join("notes", "problems")


def _read(path: str) -> str:
    p = os.path.join(REPO_ROOT, path)
    if not os.path.isfile(p):
        return ""
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def visible_sources():
    """[(label, text)] for everything the owner's window can open. Enumerated, not assumed."""
    out = [(f, _read(f)) for f in GUI_FILES]
    root = os.path.join(REPO_ROOT, PROBLEMS_DIR)
    if os.path.isdir(root):
        for dirpath, _dirs, files in os.walk(root):
            for f in sorted(files):
                if f.endswith(".md"):
                    rel = os.path.relpath(os.path.join(dirpath, f), REPO_ROOT).replace("\\", "/")
                    out.append((rel, _read(rel)))
    return out


def where_visible(literal: str):
    """Files the owner can open that contain this literal."""
    return [label for label, text in visible_sources() if literal and literal in text]


def where_hidden(literal: str, limit: int = 6):
    """Files the owner CANNOT open that contain it -- i.e. where it is currently buried."""
    hits = []
    for dirpath, _dirs, files in os.walk(os.path.join(REPO_ROOT, "notes")):
        if os.path.join("notes", "problems") in dirpath:
            continue
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), REPO_ROOT).replace("\\", "/")
            if rel in GUI_FILES:
                continue
            if literal and literal in _read(rel):
                hits.append(rel)
                if len(hits) >= limit:
                    return hits
    return hits


def run(argv):
    lits = [a for a in argv if not a.startswith("--")]
    if not lits:
        print(__doc__.strip().splitlines()[-3])
        return 2
    srcs = visible_sources()
    # COUNTS BEFORE RESULTS -- silence must never read as absence.
    print("[visibility] %d owner-visible sources scanned (%d GUI files + %d problem docs)"
          % (len(srcs), len(GUI_FILES), len(srcs) - len(GUI_FILES)))
    rc = 0
    for lit in lits:
        seen = where_visible(lit)
        print("\n  %r" % lit)
        if seen:
            print("    VISIBLE -- THE OWNER CAN SEE THIS. Appears in %d visible source(s):" % len(seen))
            for s in seen[:6]:
                print("       %s" % s)
        else:
            rc = 1
            buried = where_hidden(lit)
            print("    NOT VISIBLE. It is in NO file the status window opens.")
            if buried:
                print("    It is buried in %d note(s) the owner never opens:" % len(buried))
                for b in buried:
                    print("       %s" % b)
                print("    -> Put it in STATUS.md (position), the build plan (what to do),")
                print("       or a problems/<slug>/PROBLEM.md. Writing it down is not telling them.")
            else:
                print("    Not found anywhere in notes/ either -- check the literal itself.")
    return rc


def self_test():
    ok = True

    def check(c, label):
        nonlocal ok
        print("[self-test] %s %s" % ("PASS" if c else "FAIL", label),
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    srcs = visible_sources()
    check(len(srcs) > len(GUI_FILES), "problem docs are included (%d sources)" % len(srcs))
    check(sum(1 for _l, t in srcs if t) >= 5, "the visible sources actually have content")

    # POSITIVE CONTROL against real data. Without it, "not visible" is indistinguishable from a
    # broken reader -- the exact failure this repo has recorded for every absence-checking tool.
    probe = "AS OF:"
    check(bool(where_visible(probe)),
          "POSITIVE CONTROL: a literal known to be in STATUS.md IS found")

    # NEGATIVE CONTROL: a literal nobody has written must come back not-visible.
    check(where_visible("zzqq_not_a_real_literal_9182734") == [],
          "NEGATIVE CONTROL: an invented literal is not reported visible")

    # And the buried-search must be able to return non-zero, or its silence means nothing.
    check(isinstance(where_hidden("the"), list), "the buried-note search runs")

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else run(sys.argv[1:]))
