"""tools/owner_updates.py -- SIGNIFICANT updates for the owner (achievements, improvements, walls overcome, problems).

Owner 2026-09-12: "a new tab in the gui where you post significant updates that I can read and then clear (via a
button) ... Only significant updates or problems ... Mostly I want to hear about achievements, improvements, walls that
you've overcome. I also want to know about walls that you did NOT overcome -- these should be specific questions to me
... but also you should seriously research any walls you encounter to try and overcome on your own."

RULES (strategy discipline):
  * Post ONLY significant items, in plain language (no slugs/paths/metric names): an ability got better (say how much,
    in words), a stand-in was replaced, a wall was overcome (what it was, how), a problem that matters.
  * A wall NOT overcome is NOT posted here as an update -- after serious research it becomes a SPECIFIC question on the
    board (tools/board.py ask), which the window's questions tab shows. Post here only the one-line pointer.
  * The owner clears the list when read (window button); cleared items are archived to notes/UPDATES_ARCHIVE.md.
File: notes/UPDATES_FOR_OWNER.md (one '- [date] KIND: text' line per item). Kinds: ACHIEVEMENT, IMPROVEMENT,
WALL-OVERCOME, PROBLEM, QUESTION-FILED.
CLI:  python tools/owner_updates.py post ACHIEVEMENT "plain text"   |   list   |   clear
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "notes" / "UPDATES_FOR_OWNER.md"
ARCHIVE = REPO / "notes" / "UPDATES_ARCHIVE.md"
KINDS = ("ACHIEVEMENT", "IMPROVEMENT", "WALL-OVERCOME", "PROBLEM", "QUESTION-FILED")
HEADER = ("# UPDATES FOR THE OWNER -- significant only (achievements, improvements, walls overcome, problems)\n"
          "# Cleared by the owner from the window (tools/scorecard_gui.py tab 3); cleared items go to UPDATES_ARCHIVE.md.\n\n")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")


def load() -> list[dict]:
    if not DOC.is_file():
        return []
    out = []
    for ln in DOC.read_text(encoding="utf-8").splitlines():
        if ln.startswith("- [") and "] " in ln:
            stamp, rest = ln[3:].split("] ", 1)
            kind, _, text = rest.partition(": ")
            out.append({"stamp": stamp, "kind": kind.strip(), "text": text.strip()})
    return out


def post(kind: str, text: str) -> dict:
    kind = kind.upper().strip()
    if kind not in KINDS:
        raise ValueError("kind must be one of %s" % (KINDS,))
    text = " ".join(text.split())
    if not DOC.is_file():
        DOC.write_text(HEADER, encoding="utf-8", newline="\n")
    with DOC.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("- [%s] %s: %s\n" % (_now(), kind, text))
    return {"stamp": _now(), "kind": kind, "text": text}


def clear() -> int:
    items = load()
    if items:
        with ARCHIVE.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n## cleared by the owner %s\n" % _now())
            for it in items:
                fh.write("- [%s] %s: %s\n" % (it["stamp"], it["kind"], it["text"]))
    DOC.write_text(HEADER, encoding="utf-8", newline="\n")
    return len(items)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("post"); p.add_argument("kind"); p.add_argument("text")
    sub.add_parser("list"); sub.add_parser("clear")
    a = ap.parse_args(argv)
    if a.cmd == "post":
        r = post(a.kind, a.text); print("[updates] posted %s: %s" % (r["kind"], r["text"][:80]))
    elif a.cmd == "list":
        for it in load():
            print("[%s] %s: %s" % (it["stamp"], it["kind"], it["text"]))
        print("%d update(s)" % len(load()))
    else:
        print("[updates] cleared %d (archived)" % clear())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
