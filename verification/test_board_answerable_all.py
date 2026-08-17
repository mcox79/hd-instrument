#!/usr/bin/env python
"""Witness: EVERY row of the WAITING-ON-YOU panel can be answered, and the answer lands on disk.

WHY THIS EXISTS. On 2026-08-16, after the previous answer-panel fix, the owner reported verbatim:

    "I closed the dashboard because It still wasn't working right (there is a new ~'save as a new
     submission', but save answer is greyed out for all?)"

That was not a code bug. The previous fix made Save HONEST -- it greys out on a row it cannot write
-- and `notes/BOARD.md` had ZERO open questions at the time, so all eleven live rows were a DECISION
(D1-D7, `notes/PLAN.md` section 9) or a STANDING item (OP1-OP4, transcribed from the status
documents), none of which the panel would write. The panel was therefore correctly telling the owner
that nothing at all was answerable, which is useless to them: the decisions are exactly what they
had been trying to answer, and one attempt (D1) was lost entirely.

WHAT IS ASSERTED HERE, all of it at the RENDERED WIDGET and at the FILE ON DISK:

  A  SAVE IS LIVE ON EVERY KIND. A DECISION row and a STANDING row both arm the button. Pre-fix,
     `_sync_answer_ui` computed `can_save = ... and kind == "QUESTION"`, so both were dead.
  B  THE ANSWER REACHES notes/BOARD.md, and the row it creates carries the decision's OWN TEXT
     inline -- not a bare "D3". The owner has said this twice: "In general, you should include
     context in these questions. I do not remember what Q7 was."
  C  THE PARSER-COUPLED DOCUMENTS ARE NOT TOUCHED. `notes/PLAN.md` is parsed by
     `tools/status_plan.py`; `notes/STATUS.md` is grepped by `tools/session_start_hook.py` for the
     literals `AS OF:` and `## WHAT IS RUNNING`, and a past rewording of exactly those two silently
     degraded every compaction recovery for days. Both files are hashed before and after.
  D  AN ANSWER IS READ BACK. A decision already answered shows as ANSWERED with its text, sourced
     from the document rather than from window memory, so an answer typed on a phone counts too.
  E  THE LIVE REPO'S OWN ROWS. Not a fixture: the real D1-D7 and OP1-OP4 are collected and every one
     of them is asserted answerable. This is the owner's actual claim, tested against actual data.

RUN PRE-FIX, TO PROVE IT FAILS: extract the previous revision of the two tool modules and point the
witness at them (this is how the pre-fix count in `.claude/scan-out/dash-answerable-all.json` was
produced -- it does NOT modify the working tree):

    mkdir -p scratch/_prefix_tools
    git show HEAD:tools/status_gui.py   > scratch/_prefix_tools/status_gui.py
    git show HEAD:tools/status_state.py > scratch/_prefix_tools/status_state.py
    HD_TOOLS_DIR=scratch/_prefix_tools .venv/Scripts/python.exe \
        verification/test_board_answerable_all.py

RUNNABLE TWO WAYS: `pytest verification/test_board_answerable_all.py` and directly as a script. It
SKIPS (never fails) when there is no display, matching `status_gui.self_test`.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# HD_TOOLS_DIR exists ONLY so this witness can be pointed at an older revision of the modules to
# demonstrate that it fails against them. It defaults to the live tools directory.
TOOLS = Path(os.environ.get("HD_TOOLS_DIR") or (REPO / "tools"))
if not TOOLS.is_absolute():
    TOOLS = (REPO / TOOLS).resolve()
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
# The pre-fix copy needs its siblings (status_plan, status_evidence, board, ...) which live in the
# real tools dir; put that SECOND so the overridden modules win.
if str(REPO / "tools") not in sys.path:
    sys.path.append(str(REPO / "tools"))

# The board tools resolve their document paths AT IMPORT TIME, so the fixture must be installed
# before the imports below or this witness would drive the owner's real notes/BOARD.md.
_TD = Path(tempfile.mkdtemp(prefix="answerable_all_witness_"))
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

assert status_state.BOARD_DOC == _FIXTURE_BOARD, (
    f"the witness failed to redirect the board away from the real one "
    f"({status_state.BOARD_DOC}) -- refusing to run against notes/BOARD.md")

# The REAL documents this window must never write into. Hashed before and after (check C).
REAL_PLAN = REPO / "notes" / "PLAN.md"
REAL_STATUS = REPO / "notes" / "STATUS.md"

Q_OPEN = "QW1"
D_TEXT = ("Raise the working dimensionality from 256 to 1024 on the live path? Sixteen times the "
          "dimensions bought +0.0843 at probe scale, the largest lever measured.")
D_ROW = {"id": "D1", "question": D_TEXT,
         "why": "It rewrites every persisted anchor store, and a concurrent session is live.",
         "default": "HOLD. Do it only when no concurrent session is running and a backup exists."}
O_ROW = {"id": "OP4", "title": "The status file is over its size limit and the raise needs granting",
         "question": "A raise from 8704 to 9216 bytes has been measured and proposed. Grant it?",
         "blocked": "Every future edit has to choose between breaking the cap and evicting an entry.",
         "standing": "The file stays over cap and the next maintainer faces the same choice.",
         "rec": "Grant the raise.", "source": "notes/STATUS.md; notes/STATUS_SPEC.md sec 7"}

ANSWER_D = "yes, go to 1024 | but back the stores up first and do it when nothing else is running"
ANSWER_O = "granted, raise it to 9216"


def _sha(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return "ABSENT"


def _reset_fixture_board() -> None:
    if _FIXTURE_BOARD.exists():
        _FIXTURE_BOARD.unlink()
    board_mod.ask("A genuine open board question?", "witness", "rec",
                  _FIXTURE_BOARD, _FIXTURE_STATUS, Q_OPEN)


def _payload() -> dict:
    q, _a, _e = board_mod.load(_FIXTURE_BOARD)
    board = {"status": "OK", "path": str(_FIXTURE_BOARD), "open": q,
             "n_open": len(q), "answered_count": 0, "writable": True}
    # `recorded` is what the fixed collector adds; a pre-fix status_state has no such function, and
    # the panel must still render. Resolved defensively so the pre-fix run reports FAILED CHECKS
    # rather than dying here and hiding everything after it.
    fn = getattr(status_state, "answers_recorded_for", None)
    board["recorded"] = fn(_FIXTURE_BOARD) if callable(fn) else {}
    return {
        "ts": "witness", "took_s": 0.0,
        "board": board,
        "plan": {"status": "OK", "decisions": [dict(D_ROW)],
                 "operator": {"status": "OK", "rows": [dict(O_ROW)]}},
        "ages": {},
    }


def _iid_for(gui, row_id: str) -> str:
    for iid, row in gui._wait_rows.items():
        if row.get("id") == row_id:
            return iid
    raise AssertionError(f"no rendered row for {row_id!r} (have "
                         f"{[r.get('id') for r in gui._wait_rows.values()]})")


def _select(gui, row_id: str) -> None:
    gui.board_tv.selection_set(_iid_for(gui, row_id))
    gui._show_board_detail()


def _type(gui, text: str) -> None:
    gui.answer_box.delete("1.0", "end")
    gui.answer_box.insert("1.0", text)


def _box(gui) -> str:
    return gui.answer_box.get("1.0", "end").strip()


def _frame_text(gui) -> str:
    frame = getattr(gui, "answer_frame", None)
    if frame is None:
        return "(NO CAPTION WIDGET EXISTS)"
    try:
        return str(frame.cget("text") or "")
    except tk.TclError:
        return "(CAPTION UNREADABLE)"


def _enabled(btn) -> bool:
    return "disabled" not in str(btn.state())


def run() -> int:
    ok = True
    results: list[tuple[bool, str]] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        results.append((bool(cond), label))
        print(f"[answerable] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    plan_before, status_before = _sha(REAL_PLAN), _sha(REAL_STATUS)

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[answerable] SKIP no display available: {exc}", file=sys.stderr)
        return 0
    root.withdraw()
    try:
        _reset_fixture_board()
        gui = status_gui.StatusWindow(root)
        gui._r_board(_payload())

        # ---------------------------------------------------------------
        # A -- SAVE IS LIVE ON EVERY KIND OF ROW.
        # ---------------------------------------------------------------
        _select(gui, Q_OPEN)
        check(_enabled(gui.answer_btn),
              f"A a board QUESTION arms Save (state {gui.answer_btn.state()})")
        _select(gui, "D1")
        check(_enabled(gui.answer_btn),
              f"A a DECISION row arms Save -- this is the reported defect "
              f"(state {gui.answer_btn.state()})")
        cap = _frame_text(gui).upper()
        check("D1" in cap and "NOT ANSWERABLE" not in cap,
              f"A the caption names D1 and does NOT declare it unanswerable (reads {cap[:110]!r})")
        _select(gui, "OP4")
        check(_enabled(gui.answer_btn),
              f"A a STANDING row arms Save too (state {gui.answer_btn.state()})")

        # No row selected at all is the ONE case that may disable Save, and it must say why.
        gui._selected_qid = None
        gui._sync_answer_ui(None)
        check(not _enabled(gui.answer_btn),
              "A with NO row selected, Save is disabled rather than enabled-and-refusing")
        check("NOT ANSWERABLE" in _frame_text(gui).upper(),
              f"A and it says so (reads {_frame_text(gui)[:90]!r})")

        # ---------------------------------------------------------------
        # B -- THE ANSWER REACHES THE BOARD, CARRYING THE DECISION'S TEXT.
        # ---------------------------------------------------------------
        gui._r_board(_payload())
        _select(gui, "D1")
        _type(gui, ANSWER_D)
        gui._save_answer()
        conf = gui.answer_status.cget("text")
        check("NOT SAVED" not in conf.upper(),
              f"B pressing Save on a DECISION actually saves (screen says {conf[:130]!r})")
        check("D1" in conf and "BOARD.md" in conf,
              f"B the confirmation names the decision and the file (got {conf[:130]!r})")
        check(ANSWER_D[:30] in conf,
              f"B the confirmation quotes the text that landed (got {conf[:170]!r})")

        _q, answered, _e = board_mod.load(_FIXTURE_BOARD)
        hit = [r for r in answered if ANSWER_D in (r.get("answer") or "")]
        check(len(hit) == 1,
              f"B EXACTLY ONE row on disk carries the answer (found {len(hit)})")
        if hit:
            row = hit[0]
            check(row.get("answer") == ANSWER_D,
                  f"B the answer round-trips byte-identical INCLUDING the raw pipe "
                  f"(got {row.get('answer')!r})")
            qcell = row.get("question") or ""
            check("D1" in qcell,
                  f"B the row NAMES the decision it answers (question cell {qcell[:80]!r})")
            check(D_TEXT[:60] in qcell,
                  f"B and carries the decision's OWN TEXT inline, not a bare identifier "
                  f"(question cell {qcell[:160]!r})")
            check(D_ROW["default"][:30] in qcell,
                  f"B including what would have happened had nobody answered "
                  f"(question cell {qcell[:200]!r})")

        # A STANDING row travels the same path.
        gui._r_board(_payload())
        _select(gui, "OP4")
        _type(gui, ANSWER_O)
        gui._save_answer()
        _q, answered, _e = board_mod.load(_FIXTURE_BOARD)
        hit_o = [r for r in answered if ANSWER_O in (r.get("answer") or "")]
        check(len(hit_o) == 1, f"B a STANDING row's answer lands too (found {len(hit_o)})")
        check(hit_o and O_ROW["title"][:40] in (hit_o[0].get("question") or ""),
              f"B and it carries the standing item's own title "
              f"({(hit_o[0].get('question') if hit_o else '')[:120]!r})")

        # The genuinely-open QUESTION path is unchanged: it still writes IN PLACE, not as a new row.
        gui._r_board(_payload())
        _select(gui, Q_OPEN)
        _type(gui, "the ordinary question path still writes in place")
        gui._save_answer()
        _q, answered, _e = board_mod.load(_FIXTURE_BOARD)
        qrow = next((r for r in answered if r.get("id") == Q_OPEN), None)
        check(qrow is not None and "still writes in place" in (qrow.get("answer") or ""),
              f"B a real QUESTION is still answered IN ITS OWN CELL, not duplicated "
              f"(got {qrow and qrow.get('answer')!r})")

        # ---------------------------------------------------------------
        # D -- AN ANSWERED DECISION IS READ BACK OFF THE DOCUMENT.
        # ---------------------------------------------------------------
        p = _payload()
        check("D1" in {k.upper() for k in (p["board"].get("recorded") or {})},
              f"D the collector reads the D1 answer back out of notes/BOARD.md "
              f"(recorded: {sorted((p['board'].get('recorded') or {}))})")
        gui._r_board(p)
        vals = [gui.board_tv.item(iid, "values")
                for iid, r in gui._wait_rows.items() if r.get("id") == "D1"]
        joined = " ".join(str(v) for v in (vals[0] if vals else ()))
        check("ANSWERED" in joined.upper(),
              f"D and the row shows as ANSWERED instead of asking again forever (row {joined[:150]!r})")
        check(ANSWER_D[:25] in joined,
              f"D with the answer visible in the row (row {joined[:200]!r})")

        # ---------------------------------------------------------------
        # A REFRESH STILL MUST NOT DESTROY IN-PROGRESS INPUT, on a DECISION row.
        # ---------------------------------------------------------------
        _select(gui, "D1")
        _type(gui, "a draft I am still composing")
        gui._r_board(_payload())
        sel = gui.board_tv.selection()
        sel_id = gui._wait_rows.get(sel[0], {}).get("id") if sel else None
        check(sel_id == "D1", f"a refresh keeps the DECISION row selected (selection {sel_id!r})")
        check(_box(gui) == "a draft I am still composing",
              f"and keeps the half-typed answer (box {_box(gui)[:50]!r})")

        # ---------------------------------------------------------------
        # E -- THE LIVE REPO'S OWN ROWS, not a fixture. Every one answerable.
        # ---------------------------------------------------------------
        try:
            import status_plan
            live = status_plan.collect_plan()
        except Exception as exc:      # pragma: no cover - the panel degrades, so must this
            live = {"status": f"ERROR {type(exc).__name__}"}
        live_rows = []
        if live.get("status") == "OK":
            live_rows = [dict(d, _kind="DECISION") for d in (live.get("decisions") or [])]
            ops = live.get("operator") or {}
            if ops.get("status") == "OK":
                live_rows += [dict(r, _kind="STANDING") for r in (ops.get("rows") or [])]
        check(len(live_rows) >= 11,
              f"E the real repo really does have the eleven rows the owner saw "
              f"(got {len(live_rows)}: {[r.get('id') for r in live_rows]})")
        gui._r_board({"board": _payload()["board"],
                      "plan": {"status": "OK",
                               "decisions": [r for r in live_rows if r["_kind"] == "DECISION"],
                               "operator": {"status": "OK",
                                            "rows": [r for r in live_rows
                                                     if r["_kind"] == "STANDING"]}},
                      "ages": {}})
        dead = []
        for rid in [r.get("id") for r in live_rows]:
            try:
                _select(gui, rid)
            except AssertionError:
                dead.append(f"{rid}(not rendered)")
                continue
            if not _enabled(gui.answer_btn):
                dead.append(rid)
        check(not dead,
              f"E EVERY live row arms Save -- the owner's 'greyed out for all' is gone "
              f"(still dead: {dead})")

        # ---------------------------------------------------------------
        # C -- THE PARSER-COUPLED DOCUMENTS WERE NEVER WRITTEN TO.
        # ---------------------------------------------------------------
        check(_sha(REAL_PLAN) == plan_before,
              "C notes/PLAN.md is byte-identical after every answer above (it is parsed by "
              "tools/status_plan.py; owner prose must never be written into it)")
        check(_sha(REAL_STATUS) == status_before,
              "C notes/STATUS.md is byte-identical too (tools/session_start_hook.py greps it for "
              "'AS OF:' and '## WHAT IS RUNNING')")

    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass

    n_fail = sum(1 for good, _ in results if not good)
    print(f"[answerable] {len(results) - n_fail}/{len(results)} checks passed")
    print("[answerable] RESULT:", "PASS" if ok else "FAIL")
    print(f"[answerable] fixture board (not auto-removed, by design): {_FIXTURE_BOARD}")
    print(f"[answerable] modules under test: {TOOLS}")
    return 0 if ok else 1


def test_board_answerable_all() -> None:
    assert run() == 0, "the every-row-answerable witness failed; see stderr"


if __name__ == "__main__":
    raise SystemExit(run())
