#!/usr/bin/env python3
"""problem_queue.py -- an at-a-glance, tick-in-place checklist of OPEN problems.

WHY THIS EXISTS (owner 2026-08-26): "can we have checkboxes to mark a problem that I've assigned to a
solver? It's getting hard to see which ones I'm actively working on." This renders every OPEN problem
as a GitHub-style markdown checkbox in ONE file, `notes/problems/QUEUE.md`, that any editor/GUI shows.

  [x] = you've assigned it to a solver (actively being worked)
  [ ] = open / available to assign

HOW IT STAYS TRUE (the board.py pattern -- REWRITE IN PLACE, PRESERVE THE OWNER'S EDITS):
  Running `python tools/problem_queue.py` re-reads the problem folders and rewrites QUEUE.md so it
  ADDS any new open problem (unchecked), DROPS any that got integrated, and KEEPS your existing ticks
  (matched by slug). So ticking a box is durable across refreshes; you never lose your marks, and the
  list never goes stale. Ticking a box changes NOTHING else -- it is a private "who's working what"
  marker, not a state the rest of the pipeline reads.

  "Open" here means exactly what the queue means everywhere else: a PROBLEM.md with a `priority:` and
  no `review:` (a solved+reviewed problem has left the queue and does not appear).

USAGE
  python tools/problem_queue.py            # refresh notes/problems/QUEUE.md, print a summary
  python tools/problem_queue.py --print    # also print the checklist to stdout
"""
from __future__ import annotations

import argparse
import os
import re
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(_REPO, "notes", "problems")
QUEUE_PATH = os.path.join(PROBLEMS_DIR, "QUEUE.md")

# a checklist line: "- [x] **p3** the_slug ..."  -- we key on the (checked, slug) pair
_LINE_RE = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?:\*\*p?\d+\*\*\s*)?(?P<slug>[a-z0-9_]+)", re.MULTILINE)


def _frontmatter_field(text: str, field: str) -> str:
    """Return the value of a top-of-file `field:` line, or '' if absent/empty."""
    m = re.search(rf"(?m)^{re.escape(field)}:[ \t]*(.*)$", text)
    return (m.group(1).strip() if m else "")


def scan_open_problems() -> list[tuple[int, str]]:
    """Every OPEN problem as (priority, slug): has a priority, no review. Sorted by priority."""
    out: list[tuple[int, str]] = []
    for name in sorted(os.listdir(PROBLEMS_DIR)):
        pf = os.path.join(PROBLEMS_DIR, name, "PROBLEM.md")
        if not os.path.isfile(pf):
            continue
        with open(pf, "r", encoding="utf-8") as fh:
            text = fh.read()
        prio = _frontmatter_field(text, "priority")
        review = _frontmatter_field(text, "review")
        if not prio or review:
            continue
        try:
            out.append((int(prio), name))
        except ValueError:
            continue  # a non-integer priority is malformed; the ledger flags it, not us
    return sorted(out, key=lambda t: (t[0], t[1]))


def read_existing_ticks() -> set[str]:
    """Slugs the owner has already ticked in QUEUE.md (preserved across refreshes)."""
    if not os.path.isfile(QUEUE_PATH):
        return set()
    with open(QUEUE_PATH, "r", encoding="utf-8") as fh:
        text = fh.read()
    return {m.group("slug") for m in _LINE_RE.finditer(text) if m.group("mark") in ("x", "X")}


def render(open_problems: list[tuple[int, str]], ticked: set[str]) -> str:
    n_assigned = sum(1 for _, slug in open_problems if slug in ticked)
    lines = [
        "# Problem queue -- tick `[x]` when you've assigned a problem to a solver",
        "",
        "`[x]` = assigned / actively being worked by a solver.  `[ ]` = open, available to assign.",
        "Refresh with `python tools/problem_queue.py` -- it adds new open problems (unchecked), drops",
        "integrated ones, and KEEPS your ticks. Ticking a box is a private marker; it changes nothing else.",
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
