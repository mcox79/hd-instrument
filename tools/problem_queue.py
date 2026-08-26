#!/usr/bin/env python3
"""problem_queue.py -- a READ-ONLY markdown MIRROR of the GUI's ASSIGNED checkboxes.

WHY THIS EXISTS (owner 2026-08-26): "can we have checkboxes to mark a problem that I've assigned to a
solver? It's getting hard to see which ones I'm actively working on." The real checkboxes live in the
GUI (`tools/status_gui.py`, tab 6 PROBLEMS -- the clickable ASSIGNED column). This tool renders the
SAME shared state to `notes/problems/QUEUE.md` for anyone who prefers a plain-text/phone view.

  [x] = assigned to a solver (actively being worked)      [ ] = open / available to assign

ONE SOURCE OF TRUTH. Both the GUI and this tool read the assigned set from `problem_ledger`
(`load_assigned()` / `set_assigned()`, backed by `data/hook_state/assigned_problems.json`). You TICK
in the GUI; this file is regenerated from that state and editing it by hand does nothing. So the two
can never disagree, and the marker GATES NOTHING in the pipeline -- it is purely the who's-working-what
view.

  "Open" here means exactly what the queue means everywhere else: a PROBLEM.md with a `priority:` and
  no `review:` (a solved+reviewed problem has left the queue and does not appear).

USAGE
  python tools/problem_queue.py            # regenerate notes/problems/QUEUE.md from the shared state
  python tools/problem_queue.py --print    # also print the checklist to stdout
"""
from __future__ import annotations

import argparse
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TOOLS = os.path.dirname(os.path.abspath(__file__))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import problem_ledger  # noqa: E402  -- owns the OPEN scan and the shared assigned-state

PROBLEMS_DIR = os.path.join(_REPO, "notes", "problems")
QUEUE_PATH = os.path.join(PROBLEMS_DIR, "QUEUE.md")


def scan_open_problems() -> list[tuple[int, str]]:
    """Every OPEN problem as (priority, slug): has a priority, no review. Sorted by priority.
    Delegates to problem_ledger.scan() so there is ONE definition of 'open' across the tools."""
    out: list[tuple[int, str]] = []
    for r in problem_ledger.scan():
        prio = r.get("priority")
        if prio is None or r.get("review"):
            continue
        out.append((int(prio), r["slug"]))
    return sorted(out, key=lambda t: (t[0], t[1]))


def read_existing_ticks() -> set[str]:
    """The SHARED 'assigned to a solver' set -- the SAME state the GUI's tab-6 checkboxes write
    (problem_ledger.load_assigned). QUEUE.md is a read-only MIRROR of it, so the two never diverge."""
    return problem_ledger.load_assigned()


def render(open_problems: list[tuple[int, str]], ticked: set[str]) -> str:
    n_assigned = sum(1 for _, slug in open_problems if slug in ticked)
    lines = [
        "# Problem queue -- a READ-ONLY MIRROR of the GUI's ASSIGNED checkboxes",
        "",
        "`[x]` = assigned / actively being worked by a solver.  `[ ]` = open, available to assign.",
        "**Tick problems in the GUI (tab 6, PROBLEMS -- the ASSIGNED column), not here.** This file is",
        "regenerated from that shared state by `python tools/problem_queue.py`; editing it does nothing.",
        "",
        f"**{n_assigned} of {len(open_problems)} open problems assigned.**",
        "",
    ]
    for prio, slug in open_problems:
        mark = "x" if slug in ticked else " "
        lines.append(f"- [{mark}] **p{prio}** {slug}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh the tick-in-place open-problem checklist.")
    ap.add_argument("--print", action="store_true", dest="do_print", help="also print the checklist")
    args = ap.parse_args()

    open_problems = scan_open_problems()
    ticked = read_existing_ticks()
    # a slug that was ticked but is no longer open has been integrated -> it simply drops out.
    body = render(open_problems, ticked)
    with open(QUEUE_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)

    kept = sorted(t for t in ticked if any(slug == t for _, slug in open_problems))
    dropped = sorted(t for t in ticked if t not in {slug for _, slug in open_problems})
    print(f"[problem_queue] {len(open_problems)} open; {len(kept)} tick(s) preserved; "
          f"{len(dropped)} dropped (integrated). Wrote {os.path.relpath(QUEUE_PATH, _REPO)}")
    if dropped:
        print("  dropped (no longer open): " + ", ".join(dropped))
    if args.do_print:
        print("\n" + body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
