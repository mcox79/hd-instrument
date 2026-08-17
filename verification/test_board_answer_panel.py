#!/usr/bin/env python
"""Witness for the WAITING-ON-YOU answer panel in `tools/status_gui.py`.

WHY THIS EXISTS. On 2026-08-16 the owner reported, verbatim:

    "i tried to submit the below but it didn't work... I think there's an issue with this question
     process 'save my answer' doesn't do anything and regardless of what question I select the text
     box doesn't change. Also, periodically it resets my selected answer to the first one so it's
     hard to answer."

Three separate defects, and an answer was lost to them. Each is asserted below AT THE RENDERED
WIDGET, because the owner interacts with widgets and a fix that is right in the payload and wrong on
screen is not a fix. Every check in this file FAILED against the code as it stood at `03055c7fa`;
the failing output is recorded in `.claude/scan-out/dash-qa-fix.json`.

  D1  SAVE DOES NOTHING. When the board has no OPEN QUESTION row (the live state that night: all of
      Q1-Q12 answered), the only selectable rows are DECISION and STANDING, which are not
      answerable. The Save button stayed ENABLED and refused on press, so the panel looked live and
      could not write. Separately, a success wrote nothing to the screen naming WHAT was written or
      WHERE, so a silent failure was indistinguishable from a success.
  D2  THE BOX DOES NOT FOLLOW THE SELECTION. `_show_board_detail` never touched `answer_box`, so
      text typed for one question stayed in the box when another was selected and Save attached it
      to the WRONG question id. This is the dangerous one: it is silent and it corrupts the record.
  D3  THE SELECTION RESETS. `_r_board` restored the selection only for QUESTION rows, via
      `_selected_qid`, which `_show_board_detail` sets to None for every other kind. Selecting a
      DECISION or STANDING row therefore lost the selection on the next 20 s refresh, which snapped
      it back to the first row.

RUNNABLE TWO WAYS: `pytest verification/test_board_answer_panel.py` and directly as a script. It
SKIPS (never fails) when there is no display, matching `status_gui.self_test`.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

# The board tools resolve their document paths AT IMPORT TIME from these two variables, so a
# fixture board has to be installed before the import below or the test would drive the owner's
# real notes/BOARD.md.
_TD = Path(tempfile.mkdtemp(prefix="board_panel_witness_"))
_FIXTURE_BOARD = _TD / "BOARD.md"
_FIXTURE_STATUS = _TD / "STATUS.md"
os.environ["HD_BOARD_PATH"] = str(_FIXTURE_BOARD)
os.environ["HD_STATUS_DOC"] = str(_FIXTURE_STATUS)

_FIXTURE_STATUS.write_text(
    "# STATUS\n\nAS OF: 2099-01-01 | witness fixture\n\n"
    "## POSITION\nfixture position\n\n"
    "## TOP ITEM -- FIXTURE\nfixture top item\n\n"
    "## WHAT IS RUNNING / BLOCKED\n- a fixture thing\n",
    encoding="utf-8")

import tkinter as tk  # noqa: E402

import board as board_mod  # noqa: E402
import status_gui  # noqa: E402
import status_state  # noqa: E402

# The GUI's own module-level docs are the API this witness pins; keep them honest.
assert status_state.BOARD_DOC == _FIXTURE_BOARD, (
    f"the witness failed to redirect the board away from the real one "
    f"({status_state.BOARD_DOC}) -- refusing to run against notes/BOARD.md")

Q_A = "QW1"
Q_B = "QW2"
TEXT_A = "THIS TEXT BELONGS TO QW1 AND MUST NEVER LAND ON QW2"
TEXT_B = "this one is for QW2 | and it contains a raw pipe on purpose"


def _reset_fixture_board() -> None:
    if _FIXTURE_BOARD.exists():
        _FIXTURE_BOARD.unlink()
    board_mod.ask("First fixture question?", "witness A", "rec A",
                  _FIXTURE_BOARD, _FIXTURE_STATUS, Q_A)
    board_mod.ask("Second fixture question?", "witness B", "rec B",
                  _FIXTURE_BOARD, _FIXTURE_STATUS, Q_B)


def _payload() -> dict:
    """A board payload shaped exactly like `status_state.collect_board()` returns, plus one
    STANDING row so the not-answerable path is exercised. The STANDING row is what the owner had
    selected (OP1) when Save refused."""
    q, _a, _e = board_mod.load(_FIXTURE_BOARD)
    return {
        "ts": "witness", "took_s": 0.0,
        "board": {"status": "OK", "path": str(_FIXTURE_BOARD), "open": q,
                  "n_open": len(q), "answered_count": 0, "writable": True},
        "plan": {"status": "OK", "decisions": [],
                 "operator": {"status": "OK", "rows": [
                     {"id": "OP1", "title": "A standing operator decision",
                      "question": "the standing question text", "blocked": "nothing",
                      "standing": "the default stands", "rec": "leave it",
                      "source": "notes/STATUS.md"}]}},
        "ages": {},
    }


def _iid_for(gui, row_id: str) -> str:
    for iid, row in gui._wait_rows.items():
        if row.get("id") == row_id:
            return iid
    raise AssertionError(f"no rendered row for {row_id!r} (have "
                         f"{[r.get('id') for r in gui._wait_rows.values()]})")


def _select(gui, row_id: str) -> None:
    """Select a row the way a mouse click does: set the selection, then run the handler the
    <<TreeviewSelect>> binding runs. Driving the handler directly (rather than pumping the event
    loop) keeps the witness deterministic and headless."""
    gui.board_tv.selection_set(_iid_for(gui, row_id))
    gui._show_board_detail()


def _box(gui) -> str:
    return gui.answer_box.get("1.0", "end").strip()


def _frame_text(gui) -> str:
    """The answer box's own caption. Read defensively so that the PRE-FIX run of this witness
    reports a missing caption as a FAILED CHECK rather than dying on an AttributeError and hiding
    the two defects asserted after it.

    2026-08-17: moved from the LabelFrame's own `text=` (which does not wrap -- a long caption
    forced the frame wider than the whole window, found by walking the live widget tree) to a
    dedicated wrapping `answer_caption` label inside it. Reads whichever exists."""
    widget = getattr(gui, "answer_caption", None) or getattr(gui, "answer_frame", None)
    if widget is None:
        return "(NO CAPTION WIDGET EXISTS)"
    try:
        return str(widget.cget("text") or "")
    except tk.TclError:
        return "(CAPTION UNREADABLE)"


def _type(gui, text: str) -> None:
    gui.answer_box.delete("1.0", "end")
    gui.answer_box.insert("1.0", text)


def run() -> int:
    ok = True
    results: list[tuple[bool, str]] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        results.append((bool(cond), label))
        print(f"[board-panel] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[board-panel] SKIP no display available: {exc}", file=sys.stderr)
        return 0
    root.withdraw()
    gui = None
    try:
        _reset_fixture_board()
        gui = status_gui.StatusWindow(root)
        gui._r_board(_payload())

        # ---------------------------------------------------------------
        # D2 -- THE BOX MUST FOLLOW THE SELECTION.
        # The failure it guards is silent: text typed for QW1 gets written to QW2 and nothing on
        # screen ever said so.
        # ---------------------------------------------------------------
        _select(gui, Q_A)
        _type(gui, TEXT_A)
        _select(gui, Q_B)
        check(_box(gui) != TEXT_A,
              f"D2 selecting a different question does NOT leave the previous question's text in "
              f"the box (box now {_box(gui)[:44]!r})")

        # And the round trip: pressing Save now must not attach QW1's words to QW2.
        gui._save_answer()
        q_after, a_after, _e = board_mod.load(_FIXTURE_BOARD)
        rows = {r.get("id"): r for r in list(q_after) + list(a_after)}
        landed_on_b = (rows.get(Q_B) or {}).get("answer") or ""
        check(TEXT_A not in landed_on_b,
              f"D2 ROUND TRIP: QW1's text is NOT written into QW2's ANSWER cell "
              f"(QW2 answer is {landed_on_b[:60]!r})")

        # ---------------------------------------------------------------
        # D2b -- THE PANEL MUST NAME THE QUESTION THE BOX IS BOUND TO.
        # "Which question am I answering" must be readable without inference, because the owner
        # cannot audit an attachment they cannot see.
        # ---------------------------------------------------------------
        _reset_fixture_board()
        gui._r_board(_payload())
        _select(gui, Q_B)
        bound = _frame_text(gui).upper()
        check(Q_B in bound,
              f"D2b the answer box states WHICH question it will write to (frame reads "
              f"{bound[:80]!r})")

        # ---------------------------------------------------------------
        # D2c -- A DRAFT MUST BE KEPT PER QUESTION, not shared and not silently discarded.
        # Switching away and back is a normal thing to do while composing an answer.
        # ---------------------------------------------------------------
        _select(gui, Q_A)
        _type(gui, TEXT_A)
        _select(gui, Q_B)
        _type(gui, TEXT_B)
        _select(gui, Q_A)
        check(_box(gui) == TEXT_A,
              f"D2c switching away and back restores THAT question's own draft "
              f"(got {_box(gui)[:50]!r})")
        _select(gui, Q_B)
        check(_box(gui) == TEXT_B,
              f"D2c and the other question keeps its own draft (got {_box(gui)[:50]!r})")

        # ---------------------------------------------------------------
        # D3 -- A REFRESH MUST NOT DESTROY IN-PROGRESS INPUT.
        # The 20 s timer rebuilds this table. Selection AND draft must both survive it, for EVERY
        # row kind -- the reported reset happened on a STANDING row, which the old restore path
        # did not remember at all.
        # ---------------------------------------------------------------
        _reset_fixture_board()
        gui._r_board(_payload())
        _select(gui, Q_B)
        _type(gui, TEXT_B)
        gui._r_board(_payload())          # <-- the refresh timer, exactly as it fires
        sel = gui.board_tv.selection()
        sel_id = gui._wait_rows.get(sel[0], {}).get("id") if sel else None
        check(sel_id == Q_B,
              f"D3 a refresh keeps the selected QUESTION selected (selection is {sel_id!r})")
        check(_box(gui) == TEXT_B,
              f"D3 a refresh does NOT discard the text already typed (box is {_box(gui)[:50]!r})")

        _select(gui, "OP1")
        gui._r_board(_payload())
        sel = gui.board_tv.selection()
        sel_id = gui._wait_rows.get(sel[0], {}).get("id") if sel else None
        check(sel_id == "OP1",
              f"D3 a refresh keeps a NON-QUESTION row selected too, instead of snapping back to "
              f"the first row (selection is {sel_id!r})")

        # ---------------------------------------------------------------
        # D1 -- SAVE MUST NEVER LOOK LIVE AND DO NOTHING.
        #
        # AMENDED 2026-08-16 (second owner report: *"save answer is greyed out for all?"*). The
        # ORIGINAL form of this check asserted that Save is DISABLED on a STANDING row, which was
        # right for the design as it stood and wrong as a design: the board had zero open questions
        # that night, so every live row was DECISION or STANDING and the button was dead
        # everywhere. Every row is answerable now -- see verification/test_board_answerable_all.py,
        # which asserts that positively against the real D1-D7 / OP1-OP4.
        #
        # THE PROPERTY THIS CHECK EXISTS FOR IS UNCHANGED AND STILL ASSERTED: the button's state
        # must always match what pressing it will do. So it is live on a row it can write, dead
        # WITH A STATED REASON on the one case it cannot (nothing selected), and never
        # enabled-and-refusing.
        # ---------------------------------------------------------------
        _select(gui, "OP1")
        check("disabled" not in str(gui.answer_btn.state()),
              f"D1 Save is LIVE on a STANDING row -- it records the answer on the board rather "
              f"than greying out (state {gui.answer_btn.state()})")
        frame_txt = _frame_text(gui).upper()
        check("OP1" in frame_txt and "NOT ANSWERABLE" not in frame_txt,
              f"D1 and the box names OP1 as the row it will record against "
              f"(frame reads {frame_txt[:110]!r})")
        gui._selected_qid = None
        gui._sync_answer_ui(None)
        check("disabled" in str(gui.answer_btn.state()),
              f"D1 with NOTHING selected Save is disabled, not enabled-and-refusing "
              f"(state {gui.answer_btn.state()})")
        check("NOT ANSWERABLE" in _frame_text(gui).upper(),
              f"D1 and it states the reason (frame reads {_frame_text(gui)[:90]!r})")

        # ---------------------------------------------------------------
        # D1b -- A SUCCESSFUL SAVE MUST SHOW WHAT WAS WRITTEN AND WHERE.
        # ---------------------------------------------------------------
        _reset_fixture_board()
        gui._r_board(_payload())
        _select(gui, Q_A)
        _type(gui, TEXT_B)                # deliberately the one containing a raw `|`
        gui._save_answer()
        conf = gui.answer_status.cget("text")
        check(Q_A in conf,
              f"D1b the confirmation names the question id it wrote to (got {conf[:110]!r})")
        check("BOARD.md" in conf,
              f"D1b the confirmation names the file it wrote to (got {conf[:110]!r})")
        check(TEXT_B[:30] in conf,
              f"D1b the confirmation quotes the text that was written, so a silent failure is "
              f"impossible to mistake for a success (got {conf[:160]!r})")

        # ---------------------------------------------------------------
        # THE WRITE-BACK ITSELF: parse -> rewrite -> no data loss, no other row touched, and a raw
        # `|` survives. The board's own contract says typing one is safe; this proves the GUI path
        # honours that contract and not merely the CLI path.
        # ---------------------------------------------------------------
        q_after, a_after, _e = board_mod.load(_FIXTURE_BOARD)
        rows = {r.get("id"): r for r in list(q_after) + list(a_after)}
        check(rows.get(Q_A, {}).get("answer") == TEXT_B,
              f"ROUND TRIP: the answer parses back byte-identical INCLUDING the raw pipe "
              f"(got {rows.get(Q_A, {}).get('answer')!r})")
        check(rows.get(Q_A, {}).get("question") == "First fixture question?",
              f"ROUND TRIP: the answered row's own columns did not shift "
              f"(question is {rows.get(Q_A, {}).get('question')!r})")
        check(Q_B in rows and not (rows[Q_B].get("answer") or "").strip(),
              "ROUND TRIP: the OTHER row was not touched and is still open")
        check(rows.get(Q_B, {}).get("why") == "witness B",
              f"ROUND TRIP: the untouched row kept every column "
              f"(why is {rows.get(Q_B, {}).get('why')!r})")

        # Idempotence of the document after a GUI write, same bar board.py holds itself to.
        before = _FIXTURE_BOARD.read_text(encoding="utf-8")
        board_mod.sync(_FIXTURE_BOARD, _FIXTURE_STATUS)
        after = _FIXTURE_BOARD.read_text(encoding="utf-8")
        cut = lambda t: t.split(board_mod.H_QUESTIONS)[-1].split("_mirrored from")[0]  # noqa: E731
        check(cut(before) == cut(after),
              "ROUND TRIP: re-syncing after a GUI write changes nothing (idempotent)")

        # ---------------------------------------------------------------
        # A FAILED WRITE MUST SAY SO ON SCREEN. Never silent.
        # ---------------------------------------------------------------
        gui._selected_qid = "Q_DOES_NOT_EXIST_WITNESS"
        setattr(gui, "_answer_for", "Q_DOES_NOT_EXIST_WITNESS")
        _type(gui, "an answer to a question that is not on the board")
        gui._save_answer()
        check("REFUSED" in gui.answer_status.cget("text").upper(),
              f"a write that cannot land is REFUSED on screen, not swallowed "
              f"(got {gui.answer_status.cget('text')[:90]!r})")
        check(_box(gui).strip() != "",
              "and the typed text is KEPT in the box after a failed write, so the owner does not "
              "lose what they wrote")

        # ---------------------------------------------------------------
        # D1c -- THE EXACT STATE THE OWNER WAS IN: ZERO OPEN QUESTIONS.
        # notes/BOARD.md had Q1-Q12 all answered, so every selectable row was a DECISION or
        # STANDING item. Typed text had NO reachable destination and was lost. A text box the
        # owner can type into must always have somewhere to put the text.
        # ---------------------------------------------------------------
        _reset_fixture_board()
        board_mod.resolve(Q_A, "answered already", _FIXTURE_BOARD, _FIXTURE_STATUS)
        board_mod.resolve(Q_B, "answered already", _FIXTURE_BOARD, _FIXTURE_STATUS)
        empty = _payload()
        check(empty["board"]["n_open"] == 0,
              "D1c fixture reproduces the live state: the board has NO open question")
        gui._selected_row_id = None
        gui._selected_qid = None
        gui._answer_for = None
        gui._drafts.clear()
        gui._r_board(empty)
        # AMENDED 2026-08-16, same reason as D1 above. With no open question the panel falls back
        # to the STANDING row, and that row is now answerable -- so the text the owner types in
        # exactly this state REACHES DISK instead of having nowhere to go. That is the whole point:
        # this is the state their lost answer was typed in.
        check("disabled" not in str(gui.answer_btn.state()),
              f"D1c with ZERO open questions Save is still live, against the standing row "
              f"(state {gui.answer_btn.state()})")
        _type(gui, "remember that we have a phase diagram | per-process, not one global setting")
        gui._save_answer()
        check("SAVED" in gui.answer_status.cget("text").upper()
              and "NOT SAVED" not in gui.answer_status.cget("text").upper(),
              f"D1c pressing Save in the exact state that lost an answer now writes it "
              f"(got {gui.answer_status.cget('text')[:120]!r})")
        _q0, a0, _e0 = board_mod.load(_FIXTURE_BOARD)
        landed = [r for r in a0 if "phase diagram" in (r.get("answer") or "")]
        check(len(landed) == 1,
              f"D1c and the text is on disk in notes/BOARD.md (found {len(landed)})")
        check(landed and "OP1" in (landed[0].get("question") or ""),
              f"D1c naming the row it was written against "
              f"({(landed[0].get('question') if landed else '')[:90]!r})")

        # The escape hatch is still there for text that belongs to no row at all. Deliberately a
        # DIFFERENT sentence from the one saved above, so the two destinations cannot be confused
        # for one another when counting rows on disk.
        _type(gui, "a loose thought | belonging to no row at all")
        check("disabled" not in str(gui.note_btn.state()),
              "D1c a writable board always offers a destination for typed text")
        gui._file_note()
        note_conf = gui.answer_status.cget("text")
        check("FILED" in note_conf.upper() and "BOARD.md" in note_conf,
              f"D1c filing a note confirms WHERE it went (got {note_conf[:120]!r})")
        _q, a_notes, _e = board_mod.load(_FIXTURE_BOARD)
        filed = [r for r in a_notes if "loose thought" in (r.get("answer") or "")]
        check(len(filed) == 1,
              f"D1c the text reached notes/BOARD.md verbatim as its own ANSWERED row "
              f"(found {len(filed)})")
        check(filed and "|" in filed[0].get("answer", ""),
              f"D1c and the raw pipe survived the round trip "
              f"({filed[0].get('answer') if filed else None!r})")
        check(filed and filed[0].get("id", "") in note_conf,
              f"D1c the confirmation names the id it created ({note_conf[:80]!r})")

    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass

    n_fail = sum(1 for good, _ in results if not good)
    print(f"[board-panel] {len(results) - n_fail}/{len(results)} checks passed")
    print("[board-panel] RESULT:", "PASS" if ok else "FAIL")
    print(f"[board-panel] fixture board (not auto-removed, by design): {_FIXTURE_BOARD}")
    return 0 if ok else 1


def test_board_answer_panel() -> None:
    assert run() == 0, "the WAITING-ON-YOU answer panel witness failed; see stderr"


if __name__ == "__main__":
    raise SystemExit(run())
