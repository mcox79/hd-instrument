#!/usr/bin/env python
"""Witness: a decision the owner has ALREADY SETTLED never comes back to the WAITING-ON-YOU list.

WHY THIS EXISTS, and it is the owner saying the same thing three times.

    2026-08-20, on D6:  "I did answer d6 but I don't think those legacy questions are working
                         properly... they are all legacy and need to be removed."
    2026-08-20, on D1:  "this has been answered, hasn't it?"          (board Q79)
    2026-08-20, on D2:  "this has already been answered, hasn't it?"  (board Q80)
    2026-08-21, on D3:  "this made its way back into the gui questions - it should be archived."
                                                                      (board Q100)

D1-D7 are parsed live out of `notes/PLAN.md` section 9 on every refresh. They are NOT board
questions, so answering one does not close it the way answering a question does -- it files a NEW
board row (`ANSWER TO D3 -- ...`) and the decision itself is only suppressed on the NEXT refresh, by
`status_state.answers_recorded_for()` reading that row back off the document. **If that read-back
breaks, or a decision is added to section 9, a settled item silently returns to the owner's working
list and the only person who can detect it is the owner.** That is exactly what happened four times.

WHAT WAS ALREADY GUARDED, AND WHAT WAS NOT. `test_board_answerable_all.py` check D asserts that an
answered decision lands in `board["recorded"]`. **It never asserts the row LEAVES the working
list**, which is the half the owner actually sees. This witness asserts the half that was missing.

WHAT IS ASSERTED, all of it at the RENDERED WIDGET:

  P  POSITIVE CONTROL, FIRST AND DELIBERATELY. An UNSETTLED decision IS rendered in the working
     list. Without this the whole witness passes trivially on a panel that renders nothing at all --
     and "a control excluding nothing is not a control" is a standing rule here, earned by a control
     that dropped 0 of 242 items.
  A  A SETTLED decision is ABSENT from the working list.
  B  ...and PRESENT in ARCHIVE mode. The owner asked for "archived", not "deleted", and the archive
     is built from the SAME `plan.decisions` list -- so deleting the parser to fix A would silently
     destroy the record of what they answered. B is what makes that mistake fail loudly.
  C  THE LIVE DOCUMENTS, not a fixture: with the real board and the real plan, ZERO settled rows
     appear in the working list. This is the owner's actual complaint tested against actual data.
  D  THE PARSER-COUPLED DOCUMENTS ARE NOT TOUCHED -- `notes/PLAN.md` (parsed by
     `tools/status_plan.py`) and `notes/STATUS.md` (grepped by `tools/session_start_hook.py` for
     `AS OF:` and `## WHAT IS RUNNING`) are hashed before and after.

RUN PRE-FIX, TO PROVE IT FAILS -- the suppression is `if done: continue` in
`status_gui._r_board()`; delete those two lines and A and C fail while P and B still pass.

RUNNABLE TWO WAYS: `pytest verification/test_settled_rows_leave_the_working_list.py` and directly as
a script. It SKIPS (never fails) when there is no display, matching `status_gui.self_test`.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = Path(os.environ.get("HD_TOOLS_DIR") or (REPO / "tools"))
if not TOOLS.is_absolute():
    TOOLS = (REPO / TOOLS).resolve()
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import tkinter as tk                                                    # noqa: E402

import board as board_mod                                               # noqa: E402
import status_gui                                                       # noqa: E402
import status_state                                                     # noqa: E402

REAL_PLAN = REPO / "notes" / "PLAN.md"
REAL_STATUS = REPO / "notes" / "STATUS.md"

_TMP = Path(tempfile.gettempdir())
_FIXTURE_BOARD = _TMP / "hd_settled_rows_board.md"
_FIXTURE_STATUS = _TMP / "hd_settled_rows_status.md"

# The SETTLED decision. Its board row must match `answers_recorded_for`'s `ANSWER TO <id>` shape --
# that regex IS the coupling between the two files, so the fixture states it literally.
SETTLED_ID = "D1"
SETTLED_ROW = {"id": SETTLED_ID,
               "question": "Raise the working dimensionality from 256 to 1024 on the live path?",
               "why": "It rewrites every persisted anchor store.",
               "default": "HOLD until nothing else is running and the stores are backed up."}
# The UNSETTLED decision -- the positive control. A deliberately unused id so it can never collide
# with a real answered row on the live board.
UNSETTLED_ID = "D42"
UNSETTLED_ROW = {"id": UNSETTLED_ID,
                 "question": "A decision nobody has answered yet.",
                 "why": "It is the positive control for this witness.",
                 "default": "Nothing happens."}


def _sha(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return "ABSENT"


def _reset_fixture_board() -> None:
    """A board carrying ONE settled decision, filed the way the GUI files one."""
    if _FIXTURE_BOARD.exists():
        _FIXTURE_BOARD.unlink()
    board_mod.ask(
        f"ANSWER TO {SETTLED_ID} -- a standing decision from notes/PLAN.md section 9. "
        f"THE DECISION, IN FULL: {SETTLED_ROW['question']}",
        f"{SETTLED_ID} was waiting on you and now it is not.",
        "rec", _FIXTURE_BOARD, _FIXTURE_STATUS, "Q900")
    board_mod.resolve("Q900", "yes, go to 1024", _FIXTURE_BOARD, _FIXTURE_STATUS)


def _payload() -> dict:
    q, answered, _e = board_mod.load(_FIXTURE_BOARD)
    fn = getattr(status_state, "answers_recorded_for", None)
    board = {"status": "OK", "path": str(_FIXTURE_BOARD), "open": q, "n_open": len(q),
             "answered": answered, "answered_count": len(answered), "writable": True,
             "recorded": fn(_FIXTURE_BOARD) if callable(fn) else {}}
    return {"ts": "witness", "took_s": 0.0, "board": board,
            "plan": {"status": "OK",
                     "decisions": [dict(SETTLED_ROW), dict(UNSETTLED_ROW)],
                     "operator": {"status": "OK", "rows": []}},
            "ages": {}}


def _rendered_ids(gui) -> dict:
    """{row_id: _kind} for every row the panel actually rendered."""
    return {str(r.get("id")): str(r.get("_kind")) for r in gui._wait_rows.values()}


def _render(gui, payload: dict) -> None:
    """Rebuild the panel, DISENGAGING first so the rebuild is not silently refused.

    `_r_board` deliberately does nothing while the owner is "engaged" (a row selected, the answer
    box focused, or unsaved text in it) -- that refusal is a real feature, fixing *"periodically it
    resets my selected answer to the first one"*. But the rebuild AUTO-SELECTS the first row when
    nothing is selected yet, so a witness that renders twice is engaged by its own first render and
    every later render is held.

    THAT IS NOT HYPOTHETICAL -- IT MADE CHECK C PASS AGAINST THE FIXTURE'S ROWS INSTEAD OF THE LIVE
    ONES on this witness's second run. It looked like a pass and asserted nothing. Hence this helper
    and the explicit "the payload actually took effect" assertion in C."""
    gui.board_tv.selection_remove(*gui.board_tv.selection())
    gui.answer_box.delete("1.0", "end")
    gui._drafts.clear()
    gui._selected_row_id = None
    gui._selected_qid = None
    gui._r_board(payload)


def _row_bookkeeping_gap(gui) -> list:
    """iids `_wait_rows` claims that the Treeview does not actually have.

    THE GENERAL FORM OF THE BUG THIS WITNESS FOUND ON ITS FIRST RUN. `_wait_rows` and the Treeview
    are two records of the same list, and they are READ TOGETHER by the selection-restore at the end
    of `_r_board_apply`: it looks the kept row up in `_wait_rows` and hands the iid straight to
    `tv.selection_set()`. So an entry in one and not the other is not cosmetic -- it raises
    `TclError: Item <iid> not found` and takes the entire panel refresh down.

    The original defect was registering `_wait_rows[iid]` BEFORE the `if done: continue` that skips
    a settled row, so every settled decision left a phantom entry. Asserting the two agree catches
    that instance and any other, rather than only the one already fixed."""
    try:
        have = set(gui.board_tv.get_children(""))
    except Exception as exc:                                   # pragma: no cover
        return [f"(could not read the Treeview: {exc})"]
    return sorted(set(gui._wait_rows) - have)


def run() -> int:
    ok = True
    results: list[tuple[bool, str]] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        results.append((bool(cond), label))
        print(f"[settled] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    plan_before, status_before = _sha(REAL_PLAN), _sha(REAL_STATUS)

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[settled] SKIP no display available: {exc}", file=sys.stderr)
        return 0
    root.withdraw()
    try:
        _reset_fixture_board()
        payload = _payload()
        check(SETTLED_ID.upper() in {k.upper() for k in payload["board"]["recorded"]},
              f"setup the fixture really does record {SETTLED_ID} as settled "
              f"(recorded: {sorted(payload['board']['recorded'])})")

        gui = status_gui.StatusWindow(root)
        gui.board_archive = False
        _render(gui, payload)
        working = _rendered_ids(gui)

        # -- P: POSITIVE CONTROL FIRST. Without it, A passes on an empty panel. ---------------
        check(UNSETTLED_ID in working,
              f"P POSITIVE CONTROL: the UNSETTLED decision {UNSETTLED_ID} IS in the working list, "
              f"so this witness can actually fail (rendered: {sorted(working)})")

        # -- A: the settled one is gone. The owner's complaint, four times over. ---------------
        check(SETTLED_ID not in working,
              f"A the SETTLED decision {SETTLED_ID} is ABSENT from the working list -- "
              f"'this made its way back into the gui questions' (rendered: {sorted(working)})")

        # -- E: the two records of the same list AGREE. Found by this witness on run 1. --------
        check(not _row_bookkeeping_gap(gui),
              f"E every _wait_rows entry has a real Treeview item -- a phantom entry crashes the "
              f"selection-restore and kills the refresh (phantoms: {_row_bookkeeping_gap(gui)})")

        # -- B: gone from the working list, but NOT gone from the record. ----------------------
        gui.board_archive = True
        _render(gui, payload)
        archived = _rendered_ids(gui)
        check(SETTLED_ID in archived,
              f"B the settled decision IS in the ARCHIVE -- the owner asked for 'archived', not "
              f"'deleted', and the archive is built from the same plan.decisions list "
              f"(archived: {sorted(archived)})")

        # -- C: THE LIVE DOCUMENTS. The complaint, against real data. --------------------------
        gui.board_archive = False
        live = status_state.collect()
        lb = dict(live.get("board") or {})
        lp = dict(live.get("plan") or {})
        recorded_live = {str(k).upper() for k in (lb.get("recorded") or {})}
        if lb.get("status") == "OK" and lp.get("status") == "OK":
            _render(gui, {"ts": "witness", "took_s": 0.0, "board": lb, "plan": lp, "ages": {}})
            live_working = _rendered_ids(gui)
            # THE PAYLOAD ACTUALLY TOOK EFFECT. Without this, a refused rebuild leaves the
            # FIXTURE's rows on screen and C passes having tested nothing -- which it did.
            check(UNSETTLED_ID not in live_working,
                  f"C the live payload really replaced the fixture's rows, so C is not passing on "
                  f"stale data (rendered: {sorted(live_working)})")
            leaked = sorted(rid for rid, kind in live_working.items()
                            if kind in ("DECISION", "STANDING") and rid.upper() in recorded_live)
            check(not leaked,
                  f"C on the LIVE board and plan, NO settled decision is in the working list "
                  f"(leaked: {leaked}; settled on disk: {len(recorded_live)}; "
                  f"working rows: {sorted(live_working)})")
        else:
            check(False, f"C the live state did not collect (board={lb.get('status')}, "
                         f"plan={lp.get('status')}) -- cannot test the owner's actual complaint")

        # -- D: the parser-coupled documents were never written to. ----------------------------
        check(_sha(REAL_PLAN) == plan_before,
              "D notes/PLAN.md is byte-identical (it is parsed by tools/status_plan.py)")
        check(_sha(REAL_STATUS) == status_before,
              "D notes/STATUS.md is byte-identical (tools/session_start_hook.py greps it for "
              "'AS OF:' and '## WHAT IS RUNNING')")
    finally:
        try:
            root.destroy()
        except Exception:
            pass

    n_pass = sum(1 for c, _ in results if c)
    print(f"\n[settled] {n_pass}/{len(results)} checks passed",
          file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


def test_settled_rows_leave_the_working_list() -> None:
    assert run() == 0


if __name__ == "__main__":
    sys.exit(run())
