#!/usr/bin/env python
"""Async decision board -- `notes/BOARD.md`, REWRITTEN IN PLACE so it never scrolls.

WHY THIS EXISTS (2026-08-15, owner directive): an unattended overnight loop has no one to ask.
The owner reads and answers on a phone or a desktop markdown editor, whenever they look. So the
questions have to live in ONE short file that is rewritten (never appended), and answering has to
be nothing more than typing into a table cell. Anything that requires running a command to answer
will not get answered.

THE HAND-EDIT IS THE NORMAL CASE, NOT AN ERROR. Every parser decision here follows from that:

  - An ANSWER cell with a raw `|` in it does NOT corrupt the row. A row with more cells than the
    header has its OVERFLOW MERGED BACK INTO THE ANSWER COLUMN (the only free-text column an owner
    types into), keeping the fixed leading columns and the fixed trailing columns intact.
  - A row with FEWER cells than the header is PADDED, not dropped.
  - The `status` column is advisory. **A non-empty ANSWER means answered, whatever `status` says**
    -- the owner will type an answer and not update a second cell, and a board that then reports
    the question as still open is worse than no board.
  - Rows are matched by ID, not by position, so reordering is safe.
  - Missing sections are recreated; the separator row is optional; leading/trailing `|` optional.
  - Sections the owner adds by hand are PRESERVED VERBATIM. Stray header text is preserved into a
    `## NOTES` section rather than being dropped.

COUPLING (CLAUDE.md "A doc parsed by code is coupled to it"): this file parses TWO documents.
  1. `notes/BOARD.md` -- headings `## STATUS`, `## QUESTIONS FOR YOU`, `## ANSWERED` and the two
     table shapes below are an API. Doc-side record: the PARSER CONTRACT block that this tool
     writes into the top of BOARD.md itself, naming this file.
  2. `notes/STATUS.md` -- literals `AS OF:` (colon required), `## POSITION`, `## TOP ITEM`,
     `## WHAT IS RUNNING`. `AS OF:` and `## WHAT IS RUNNING` were ALREADY an API of
     `tools/session_start_hook.py`; `## POSITION` and `## TOP ITEM` are NEW as of this file.
     Doc-side record: `notes/STATUS_SPEC.md` sec 2. A missing literal FAILS LOUD (a banner in the
     board), never a quiet placeholder -- that quiet placeholder is exactly how the 2026-08-13
     reword degraded every compaction recovery undetected.

TABLE SHAPES (both are an API):
  ## QUESTIONS FOR YOU
  | ID | Question | What's blocked on it | My recommendation | ANSWER | status |
  ## ANSWERED
  | ID | Question | My recommendation | ANSWER | resolved |

  ANSWERED deliberately keeps `My recommendation` beside `ANSWER`: that pair is the record of what
  was advised versus what the owner decided, which is the only part of a settled question still
  worth reading. `What's blocked on it` is dropped on resolve -- it is no longer blocked.

USAGE
  python tools/board.py ask "<question>" --why "<what is blocked>" --rec "<recommendation>"
  python tools/board.py open                 # human-readable list of open questions
  python tools/board.py open --json          # machine-readable
  python tools/board.py count                # just the integer, for the session-start hook
  python tools/board.py resolve <ID> [--answer "<the decision>"]
  python tools/board.py sync                 # rewrite in place (re-mirrors STATUS.md, migrates
                                             #   hand-answered rows into ANSWERED)
  python tools/board.py self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# HD_BOARD_PATH exists so the Stop hook's end-to-end self-test can exercise the real
# denial-to-board path against a throwaway file instead of the owner's actual board.
DEFAULT_BOARD = Path(os.environ.get("HD_BOARD_PATH") or (REPO_ROOT / "notes" / "BOARD.md"))
DEFAULT_STATUS = REPO_ROOT / "notes" / "STATUS.md"

# --- BOARD.md API: headings ------------------------------------------------
H_STATUS = "## STATUS"
H_QUESTIONS = "## QUESTIONS FOR YOU"
H_ANSWERED = "## ANSWERED"
H_NOTES = "## NOTES"
MANAGED_HEADINGS = (H_STATUS, H_QUESTIONS, H_ANSWERED)

# --- BOARD.md API: table shapes -------------------------------------------
Q_HEADERS = ["ID", "Question", "What's blocked on it", "My recommendation", "ANSWER", "status"]
Q_ANSWER_IDX = 4          # the free-text column an owner types into; overflow merges here
Q_FIELDS = ["id", "question", "why", "rec", "answer", "status"]

A_HEADERS = ["ID", "Question", "My recommendation", "ANSWER", "resolved"]
A_ANSWER_IDX = 3
A_FIELDS = ["id", "question", "rec", "answer", "resolved"]

# `status` values that mean settled even with an empty ANSWER cell. Compared casefolded.
SETTLED_STATUS = {"answered", "resolved", "done", "closed", "ok", "yes"}

# --- notes/STATUS.md API: parsed literals (see COUPLING in the module docstring) ---
STATUS_AS_OF = "AS OF:"
STATUS_SECTIONS = ("## POSITION", "## TOP ITEM", "## WHAT IS RUNNING")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Cell-level escaping. A markdown table cannot carry a bare `|`; an owner will
# type one anyway. We escape on write and unescape on read, AND the row parser
# below survives a bare one that was typed by hand and never escaped.
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    """Make a string safe inside one table cell without changing what it says."""
    s = "" if s is None else str(s)
    s = s.replace("\\", "\\\\").replace("|", "\\|")
    # A hand-pasted multi-line answer must not blow the row apart.
    s = s.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
    return s.strip()


def _unesc(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out).strip()


def _split_cells(line: str) -> list[str]:
    """Split one markdown table row into raw cells. Leading/trailing `|` optional."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c for c in re.split(r"(?<!\\)\|", s)]


def _is_separator(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.fullmatch(r"[\s:\-]*", c or "") and "-" in (c or "") for c in cells)


def _normalize_row(cells: list[str], ncols: int, answer_idx: int) -> list[str]:
    """Reconcile a hand-edited row to exactly ncols cells WITHOUT losing text.

    Too FEW cells  -> pad with empties (the owner deleted a trailing `|`).
    Too MANY cells -> the surplus can only have come from a raw `|` typed inside the free-text
    ANSWER cell, so keep the fixed leading columns and the fixed trailing columns and rejoin
    everything between them back into ANSWER. This is why an answer like
    "use A | fall back to B" round-trips instead of shifting every later column left.
    """
    cells = [c for c in cells]
    if len(cells) < ncols:
        cells = cells + [""] * (ncols - len(cells))
    elif len(cells) > ncols:
        n_tail = ncols - answer_idx - 1
        head = cells[:answer_idx]
        tail = cells[len(cells) - n_tail:] if n_tail else []
        middle = cells[answer_idx: len(cells) - n_tail] if n_tail else cells[answer_idx:]
        cells = head + [" | ".join(c.strip() for c in middle)] + tail
    return [_unesc(c) for c in cells]


def parse_rows(body_lines: list[str], headers: list[str], answer_idx: int,
               fields: list[str]) -> list[dict]:
    """Parse a markdown table body into dicts. Skips the header row and the separator row.
    Never raises on a malformed row -- it normalizes it (see _normalize_row)."""
    rows: list[dict] = []
    header_norm = [h.strip().casefold() for h in headers]
    for ln in body_lines:
        if "|" not in ln:
            continue
        raw = _split_cells(ln)
        if _is_separator(raw):
            continue
        probe = [c.strip().casefold() for c in raw]
        # Header row: matched loosely so a reflowed/renamed-case header is still skipped.
        if probe[:2] == header_norm[:2] or (probe and probe[0] == "id"):
            continue
        cells = _normalize_row(raw, len(headers), answer_idx)
        if not any(c.strip() for c in cells):
            continue
        rows.append(dict(zip(fields, cells)))
    return rows


def render_table(headers: list[str], rows: list[dict], fields: list[str]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_esc(r.get(f, "")) for f in fields) + " |")
    return out


def is_settled(row: dict) -> bool:
    """A non-empty ANSWER settles a question regardless of what `status` says. This is the
    single most important tolerance in this file: the owner types an answer and moves on."""
    if (row.get("answer") or "").strip():
        return True
    return (row.get("status") or "").strip().casefold() in SETTLED_STATUS


# ---------------------------------------------------------------------------
# Document structure. Managed sections are regenerated; everything else survives.
# ---------------------------------------------------------------------------

def _heading_key(heading: str) -> str | None:
    norm = re.sub(r"\s+", " ", heading.strip()).upper()
    for m in MANAGED_HEADINGS:
        if norm == m or norm.startswith(m + " "):
            return m
    return None


def split_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    cur: list[str] | None = None
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = []
            sections.append((ln, cur))
        elif cur is None:
            preamble.append(ln)
        else:
            cur.append(ln)
    return preamble, sections


# ---------------------------------------------------------------------------
# notes/STATUS.md mirror
# ---------------------------------------------------------------------------

def _missing_literal_banner(literal: str, path: Path) -> str:
    """FAIL LOUD. Same discipline as tools/session_start_hook.py: a placeholder that reads like
    ordinary output is how a reworded literal survives undetected."""
    return (f"> **MISSING REQUIRED LITERAL `{literal}` in `{path.name}`.** `tools/board.py` parses\n"
            f"> this exact string; it is an API, not a formatting choice. See "
            f"`notes/STATUS_SPEC.md` sec 2.")


def status_block(status_path: Path = DEFAULT_STATUS, max_lines_per_section: int = 14) -> list[str]:
    """Mirror STATUS.md's AS-OF line + POSITION + TOP ITEM + WHAT IS RUNNING."""
    if not status_path.exists():
        return [f"> **`{status_path}` MISSING.** Nothing to mirror.", ""]
    try:
        text = status_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"> **`{status_path.name}` unreadable: {exc}**", ""]

    lines = text.splitlines()
    out: list[str] = []
    as_of = next((ln.strip() for ln in lines if ln.strip().startswith(STATUS_AS_OF)), None)
    out.append(as_of if as_of else _missing_literal_banner(STATUS_AS_OF, status_path))
    out.append("")

    _, sections = split_sections(text)
    for want in STATUS_SECTIONS:
        body = None
        title = want
        for heading, blines in sections:
            norm = re.sub(r"\s+", " ", heading.strip()).upper()
            if norm == want or norm.startswith(want + " ") or norm.startswith(want):
                body, title = blines, heading.strip()
                break
        if body is None:
            out.append(_missing_literal_banner(want, status_path))
            out.append("")
            continue
        kept = [b for b in body if b.strip()][:max_lines_per_section]
        out.append(f"**{title.lstrip('# ').strip()}**")
        out.extend(kept)
        out.append("")
    out.append(f"_mirrored from `notes/STATUS.md` at {_now()} by `tools/board.py`._")
    return out


# ---------------------------------------------------------------------------
# Header block (owned by this tool; stray owner text is preserved into ## NOTES)
# ---------------------------------------------------------------------------

HEADER = """\
# BOARD -- questions waiting on you

**How to answer:** type your decision into the **ANSWER** cell of any row below, in any markdown
editor, on any device. Save. That is the whole protocol. You do NOT need to touch the `status`
cell, and you do NOT need to run anything: a non-empty ANSWER is treated as answered, and the row
moves down to ANSWERED on the next update.

This file is **REWRITTEN IN PLACE**, never appended, so it does not scroll and never gets long.

**Stop the overnight loop instantly:** `python tools/autoloop.py disarm`
(or open `data/hook_state/autoloop.json` and set `"armed": false`). See
`notes/BOARD_AND_LOOP_README.md`.

<!-- PARSER CONTRACT -- READ BEFORE REWORDING ANYTHING ABOVE OR BELOW.
     This document is machine-parsed by tools/board.py (which also rewrites it) and its open-
     question count is injected at every session start by tools/session_start_hook.py.
     The following are an API, not formatting choices:
       - the headings `## STATUS`, `## QUESTIONS FOR YOU`, `## ANSWERED`
       - the QUESTIONS column order: ID | Question | What's blocked on it | My recommendation | ANSWER | status
       - the ANSWERED column order: ID | Question | My recommendation | ANSWER | resolved
     Editing CELL TEXT is always safe and is the intended use, including typing a raw `|`.
     Adding your own `## <anything else>` section is safe; it is preserved verbatim.
     Renaming a managed heading or reordering columns is NOT safe -- change tools/board.py in the
     same edit. (CLAUDE.md: "A doc parsed by code is coupled to it".) -->
"""


def render_board(questions: list[dict], answered: list[dict],
                 extra: list[tuple[str, list[str]]],
                 status_path: Path = DEFAULT_STATUS) -> str:
    out: list[str] = [HEADER, ""]
    out.append(H_STATUS)
    out.append("")
    out.extend(status_block(status_path))
    out.append("")
    out.append(H_QUESTIONS)
    out.append("")
    if questions:
        out.extend(render_table(Q_HEADERS, questions, Q_FIELDS))
    else:
        out.extend(render_table(Q_HEADERS, [], Q_FIELDS))
        out.append("")
        out.append("_No open questions. Nothing is waiting on you._")
    out.append("")
    out.append(H_ANSWERED)
    out.append("")
    if answered:
        out.extend(render_table(A_HEADERS, answered[-40:], A_FIELDS))
        if len(answered) > 40:
            out.append("")
            out.append(f"_(showing the last 40 of {len(answered)} answered)_")
    else:
        out.extend(render_table(A_HEADERS, [], A_FIELDS))
    out.append("")
    for heading, body in extra:
        out.append(heading)
        out.extend(body)
        if not body or body[-1].strip():
            out.append("")
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load(board_path: Path) -> tuple[list[dict], list[dict], list[tuple[str, list[str]]]]:
    """Returns (open_questions, answered, extra_sections). Tolerant of every hand edit."""
    if not board_path.exists():
        return [], [], []
    text = board_path.read_text(encoding="utf-8")
    preamble, sections = split_sections(text)

    questions: list[dict] = []
    answered: list[dict] = []
    extra: list[tuple[str, list[str]]] = []
    for heading, body in sections:
        key = _heading_key(heading)
        if key == H_QUESTIONS:
            questions.extend(parse_rows(body, Q_HEADERS, Q_ANSWER_IDX, Q_FIELDS))
        elif key == H_ANSWERED:
            answered.extend(parse_rows(body, A_HEADERS, A_ANSWER_IDX, A_FIELDS))
        elif key == H_STATUS:
            continue  # regenerated from notes/STATUS.md every write
        else:
            extra.append((heading, body))

    # Stray header text the owner typed above the first heading is PRESERVED, not dropped.
    stray = [ln for ln in preamble
             if ln.strip() and not ln.lstrip().startswith("<!--") and ln.strip() != "-->"
             and ln.strip() not in {l.strip() for l in HEADER.splitlines()}]
    stray = [ln for ln in stray if not ln.lstrip().startswith(("#", ">", "|"))]
    if stray:
        for i, (h, b) in enumerate(extra):
            if _heading_key(h) is None and re.sub(r"\s+", " ", h.strip()).upper() == H_NOTES:
                extra[i] = (h, b + [""] + stray)
                break
        else:
            extra.append((H_NOTES, [""] + stray))
    return questions, answered, extra


def _migrate_settled(questions: list[dict], answered: list[dict]) -> tuple[list[dict], list[dict]]:
    """Move hand-answered rows out of QUESTIONS into ANSWERED. This is what makes 'type an answer
    and walk away' work."""
    still_open, newly = [], []
    for q in questions:
        if is_settled(q):
            newly.append({"id": q.get("id", ""), "question": q.get("question", ""),
                          "rec": q.get("rec", ""), "answer": q.get("answer", ""),
                          "resolved": _now()})
        else:
            still_open.append(q)
    known = {a.get("id", "") for a in answered}
    answered = answered + [n for n in newly if n["id"] not in known]
    return still_open, answered


def save(board_path: Path, questions: list[dict], answered: list[dict],
         extra: list[tuple[str, list[str]]], status_path: Path = DEFAULT_STATUS) -> None:
    """Atomic rewrite-in-place: temp file + os.replace (same pattern as dispatch_queue.save_items)."""
    board_path.parent.mkdir(parents=True, exist_ok=True)
    text = render_board(questions, answered, extra, status_path)
    tmp = board_path.with_suffix(board_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(str(tmp), str(board_path))


def sync(board_path: Path = DEFAULT_BOARD, status_path: Path = DEFAULT_STATUS) -> tuple[int, int]:
    q, a, extra = load(board_path)
    q, a = _migrate_settled(q, a)
    save(board_path, q, a, extra, status_path)
    return len(q), len(a)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def _next_id(questions: list[dict], answered: list[dict]) -> str:
    n = 0
    for r in list(questions) + list(answered):
        m = re.fullmatch(r"[Qq](\d+)", (r.get("id") or "").strip())
        if m:
            n = max(n, int(m.group(1)))
    return f"Q{n + 1}"


def ask(question: str, why: str, rec: str, board_path: Path = DEFAULT_BOARD,
        status_path: Path = DEFAULT_STATUS, item_id: str | None = None) -> dict:
    q, a, extra = load(board_path)
    q, a = _migrate_settled(q, a)
    new = {"id": item_id or _next_id(q, a), "question": question.strip(),
           "why": why.strip(), "rec": rec.strip(), "answer": "", "status": "open"}
    q.append(new)
    save(board_path, q, a, extra, status_path)
    return new


def resolve(item_id: str, answer: str | None, board_path: Path = DEFAULT_BOARD,
            status_path: Path = DEFAULT_STATUS) -> dict:
    q, a, extra = load(board_path)
    target = item_id.strip().casefold()
    for row in q:
        if (row.get("id") or "").strip().casefold() == target:
            if answer is not None:
                row["answer"] = answer
            row["status"] = "answered"
            if not (row.get("answer") or "").strip():
                row["answer"] = "(resolved with no written answer)"
            q, a = _migrate_settled(q, a)
            save(board_path, q, a, extra, status_path)
            return next(r for r in a if (r.get("id") or "").strip().casefold() == target)
    for row in a:
        if (row.get("id") or "").strip().casefold() == target:
            raise KeyError(f"{item_id} is already answered (resolved {row.get('resolved')!r})")
    raise KeyError(f"no such question: {item_id}")


def open_questions(board_path: Path = DEFAULT_BOARD) -> list[dict]:
    q, _a, _e = load(board_path)
    return [r for r in q if not is_settled(r)]


def count_open(board_path: Path = DEFAULT_BOARD) -> int:
    """Cheap, never raises. Used by tools/session_start_hook.py and by the Stop hook."""
    try:
        return len(open_questions(board_path))
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    import tempfile
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="board_selftest_"))
    bp = td / "BOARD.md"
    sp = td / "STATUS.md"
    sp.write_text(
        "# STATUS\n\nAS OF: 2099-01-01 | fixture branch\n\n"
        "## POSITION\nposition line one\nposition line two\n\n"
        "## TOP ITEM -- SOMETHING\ntop item body\n\n"
        "## WHAT IS RUNNING / BLOCKED\n- a live thing\n",
        encoding="utf-8")

    # 1. ask() creates the file with a well-formed table
    ask("Should we do X?", "STEP 2 cannot start", "do X", bp, sp)
    ask("Pick A or B?", "the encoder choice", "A", bp, sp)
    t = bp.read_text(encoding="utf-8")
    check(H_QUESTIONS in t and H_ANSWERED in t and H_STATUS in t, "all three sections written")
    check("AS OF: 2099-01-01" in t, "STATUS.md AS-OF line mirrored")
    check("position line one" in t and "top item body" in t and "a live thing" in t,
          "POSITION + TOP ITEM + WHAT IS RUNNING all mirrored")
    check(count_open(bp) == 2, f"count_open == 2 (got {count_open(bp)})")

    # 2. THE ROUND TRIP: hand-style edit -> parse -> rewrite, no data loss.
    #    Every mutation below is one a human plausibly makes in a markdown editor.
    hand = bp.read_text(encoding="utf-8")
    hand = hand.replace(
        "| Q1 | Should we do X? | STEP 2 cannot start | do X |  | open |",
        "|Q1|Should we do X?|STEP 2 cannot start|do X| yes, but use the cheap path | open")
    #      ^ collapsed spaces, raw `|` typed in ANSWER, trailing `|` deleted, status left `open`
    hand = hand.replace(
        "| Q2 | Pick A or B? | the encoder choice | A |  | open |",
        "| Q2 | Pick A or B? | the encoder choice | A |   |   |")
    hand += "\n## MY OWN NOTES\n\nremember to check the GPU box.\n"
    bp.write_text(hand, encoding="utf-8")

    q, a, extra = load(bp)
    q1 = next((r for r in q + a if r["id"] == "Q1"), None)
    check(q1 is not None, "Q1 survives a hand-mangled row (collapsed spaces, no trailing pipe)")
    if q1:
        check(q1["why"] == "STEP 2 cannot start" and q1["rec"] == "do X",
              f"Q1 columns did NOT shift despite a raw pipe in ANSWER (why={q1['why']!r})")
        check("yes, but use the cheap path" in q1["answer"],
              f"Q1 ANSWER text preserved intact (got {q1['answer']!r})")
    check(any(re.sub(r'\s+', ' ', h.strip()).upper() == "## MY OWN NOTES" for h, _ in extra),
          "a hand-added section is preserved")

    sync(bp, sp)
    t2 = bp.read_text(encoding="utf-8")
    check("yes, but use the cheap path" in t2, "ANSWER text survives the rewrite")
    check("remember to check the GPU box." in t2, "hand-added section survives the rewrite")
    check("| Q2 |" in t2, "the still-open Q2 survives the rewrite")
    check(count_open(bp) == 1,
          f"hand-answered Q1 auto-migrated; only Q2 open (got {count_open(bp)})")
    check("Q1" in t2.split(H_ANSWERED)[-1], "Q1 now sits under ANSWERED")

    # 3. idempotence: a second rewrite changes nothing
    before = bp.read_text(encoding="utf-8")
    sync(bp, sp)
    after = bp.read_text(encoding="utf-8")
    body_b = before.split(H_QUESTIONS)[-1].split("_mirrored from")[0]
    body_a = after.split(H_QUESTIONS)[-1].split("_mirrored from")[0]
    check(body_b == body_a, "rewrite is idempotent (question/answer bodies byte-identical)")

    # 4. resolve() moves an open row and refuses a double-resolve
    resolve("Q2", "go with A", bp, sp)
    check(count_open(bp) == 0, "resolve() closed the last open question")
    try:
        resolve("Q2", "again", bp, sp)
        check(False, "double-resolve refused")
    except KeyError:
        check(True, "double-resolve refused")
    try:
        resolve("Q99", None, bp, sp)
        check(False, "resolving an unknown id refused")
    except KeyError:
        check(True, "resolving an unknown id refused")

    # 5. LOUD failure on a reworded STATUS.md literal (never a quiet placeholder)
    sp2 = td / "STATUS_broken.md"
    sp2.write_text("# STATUS\n\nAS OF 2099-01-01\n\n## RUNNING / BLOCKED\n- x\n", encoding="utf-8")
    blk = "\n".join(status_block(sp2))
    check("MISSING REQUIRED LITERAL `AS OF:`" in blk, "missing 'AS OF:' fails LOUD")
    check("MISSING REQUIRED LITERAL `## POSITION`" in blk, "missing '## POSITION' fails LOUD")
    check("MISSING REQUIRED LITERAL `## WHAT IS RUNNING`" in blk,
          "missing '## WHAT IS RUNNING' fails LOUD")

    # 6. garbage tolerance: a completely mangled table must not raise or drop good rows
    bp2 = td / "BOARD_garbage.md"
    bp2.write_text(
        H_QUESTIONS + "\n\nID | Question\n| Q7 | only two cells\n"
        "|||||||\n| Q8 | q | w | r | a | open | extra | cells |\n"
        "\n" + H_ANSWERED + "\n(the owner deleted this whole table)\n", encoding="utf-8")
    q3, a3, _e3 = load(bp2)
    ids = {r["id"] for r in q3}
    check("Q7" in ids, "a short row is padded, not dropped")
    q8 = next((r for r in q3 if r["id"] == "Q8"), None)
    check(q8 is not None and q8["status"] == "cells",
          f"an over-long row keeps its LAST column as status (got {q8 and q8['status']!r})")
    check(q8 is not None and "extra" in q8["answer"],
          f"an over-long row merges surplus into ANSWER (got {q8 and q8['answer']!r})")
    save(bp2, q3, a3, _e3, sp)
    check(bp2.exists(), "a garbage board still rewrites without raising")

    # 7. count_open never raises, even on a nonexistent path
    check(count_open(td / "nope.md") == 0, "count_open on a missing file returns 0, never raises")

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default=str(DEFAULT_BOARD))
    ap.add_argument("--status", default=str(DEFAULT_STATUS))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ask = sub.add_parser("ask")
    p_ask.add_argument("question")
    p_ask.add_argument("--why", required=True, help="what is blocked on this")
    p_ask.add_argument("--rec", required=True, help="my recommendation")
    p_ask.add_argument("--id", default=None)

    p_open = sub.add_parser("open")
    p_open.add_argument("--json", action="store_true")

    sub.add_parser("count")
    sub.add_parser("sync")

    p_res = sub.add_parser("resolve")
    p_res.add_argument("id")
    p_res.add_argument("--answer", default=None)

    sub.add_parser("self-test")

    args = ap.parse_args(argv)
    bp, sp = Path(args.board), Path(args.status)

    if args.cmd == "self-test":
        return self_test()

    if args.cmd == "ask":
        row = ask(args.question, args.why, args.rec, bp, sp, args.id)
        print(f"[board] filed {row['id']}: {row['question']}")
        print(f"[board] {count_open(bp)} open question(s) -> {bp}")
        return 0

    if args.cmd == "open":
        rows = open_questions(bp)
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        if not rows:
            print("[board] 0 open questions.")
            return 0
        for r in rows:
            print(f"  {r['id']}: {r['question']}")
            print(f"      blocked: {r['why']}")
            print(f"      my rec : {r['rec']}")
        print(f"-- {len(rows)} open question(s) in {bp}")
        return 0

    if args.cmd == "count":
        print(count_open(bp))
        return 0

    if args.cmd == "sync":
        n_open, n_ans = sync(bp, sp)
        print(f"[board] rewrote {bp}: {n_open} open, {n_ans} answered")
        return 0

    if args.cmd == "resolve":
        try:
            row = resolve(args.id, args.answer, bp, sp)
        except KeyError as e:
            print(f"[board] REFUSED: {e}", file=sys.stderr)
            return 2
        print(f"[board] resolved {row['id']} at {row['resolved']}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
