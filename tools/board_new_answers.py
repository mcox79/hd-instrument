"""Report board questions the owner has ANSWERED since I last looked. Run it every turn.

WHY THIS EXISTS. On 2026-08-19 the owner answered two board questions at 20:01Z. I found out at
roughly 20:08Z, and only by accident: the Stop hook's open-question COUNT disagreed with the number
I thought I had filed, and I went looking for the discrepancy. **Nothing tells me when an answer
arrives.**

The hook reports how many questions are OPEN and whether `notes/COMMENTARY.md` has unread notes.
Neither fires when an existing question gains an ANSWER -- the count simply goes DOWN, which is
indistinguishable from me resolving one myself. So the owner can answer a question and have it sit
unread indefinitely while I carry on. That is the same class as the stale WHAT IS RUNNING section:
a channel the owner uses that I do not watch.

USAGE
  python tools/board_new_answers.py            # list answers newer than the last mark, then mark
  python tools/board_new_answers.py --peek     # list them WITHOUT advancing the mark
  python tools/board_new_answers.py --self-test

The mark is a single timestamp in data/hook_state/board_answers_seen.txt. First run reports
nothing and just sets the mark -- a fresh checkout is not a backlog of unread answers, which is the
same first-run rule the commentary gate already uses.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_BOARD = _REPO / "notes" / "BOARD.md"
_MARK = _REPO / "data" / "hook_state" / "board_answers_seen.txt"


def _rows(text: str):
    """Every markdown table row in the file, as a list of cells. Format-agnostic on purpose: the
    board has two tables with different column counts and this must not care which is which."""
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|- "):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and cells[0].upper() != "ID" and cells[0].startswith("Q"):
            out.append(cells)
    return out


def answered(text: str):
    """(id, question, answer, when) for rows that carry BOTH an answer and a timestamp.

    A row is 'answered' only if the answer cell is non-empty. A resolved-but-unanswered row -- one
    I closed myself -- has a timestamp and no answer, and must NOT be reported as the owner
    speaking to me.
    """
    out = []
    for cells in _rows(text):
        if len(cells) < 3:
            continue
        when = cells[-1]
        ans = cells[-2]
        if not ans or not when or "T" not in when:
            continue
        out.append((cells[0], cells[1], ans, when))
    return out


def read_mark() -> str:
    try:
        return _MARK.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def write_mark(v: str) -> None:
    _MARK.parent.mkdir(parents=True, exist_ok=True)
    _MARK.write_bytes((v + "\n").encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--peek", action="store_true", help="do not advance the mark")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return _self_test()

    if not _BOARD.exists():
        print("[board-answers] no BOARD.md")
        return 0
    text = _BOARD.read_text(encoding="utf-8")
    rows = answered(text)
    mark = read_mark()
    newest = max((w for _, _, _, w in rows), default="")

    if not mark:
        if not a.peek:
            write_mark(newest)
        print("[board-answers] first run -- mark set to %s, reporting nothing "
              "(a fresh checkout is not a backlog)" % (newest or "(none)"))
        return 0

    fresh = [r for r in rows if r[3] > mark]
    if not fresh:
        print("[board-answers] no new answers since %s" % mark)
        return 0

    print("[board-answers] %d NEW ANSWER(S) FROM THE OWNER since %s" % (len(fresh), mark))
    for qid, q, ans, when in sorted(fresh, key=lambda r: r[3]):
        print()
        print("  %s  (%s)" % (qid, when))
        print("    Q: %s" % q[:300])
        print("    A: %s" % ans.replace("<br>", "\n       ")[:600])
    if not a.peek:
        write_mark(newest)
    return 0


def _self_test() -> int:
    doc = ("| ID | Question | My recommendation | ANSWER | resolved |\n"
           "|---|---|---|---|---|\n"
           "| Q1 | did it work | do X | yes go ahead | 2026-08-19T10:00:00Z |\n"
           "| Q2 | other thing | do Y |  | 2026-08-19T11:00:00Z |\n"
           "| Q3 | third thing | do Z | no, stop | 2026-08-19T12:00:00Z |\n")
    got = answered(doc)
    ids = [g[0] for g in got]
    assert ids == ["Q1", "Q3"], f"expected Q1 and Q3, got {ids}"
    print("[self-test] PASS an ANSWERED row is detected")
    print("[self-test] PASS a row I resolved MYSELF (timestamp, no answer) is NOT reported as the "
          "owner speaking -- that distinction is the whole point")
    fresh = [g for g in got if g[3] > "2026-08-19T11:30:00Z"]
    assert [f[0] for f in fresh] == ["Q3"], "mark filtering did not work"
    print("[self-test] PASS only answers NEWER than the mark are reported")
    hdr = _rows("| ID | Question |\n|---|---|\n| Q9 | x |\n")
    assert [h[0] for h in hdr] == ["Q9"], "header row leaked into the results"
    print("[self-test] PASS the header row is not parsed as a question")
    print("[self-test] RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
