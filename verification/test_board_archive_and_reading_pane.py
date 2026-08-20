"""Witness for the board ARCHIVE + BIGGER-READING-PANE controls (owner request 2026-08-20).

WHY IT DRIVES THE REAL WINDOW. Earlier the same day a diagnostic passed `py_compile`, was launched,
spent its whole multi-minute corpus read, and died on a print statement -- because COMPILING IS NOT
EXERCISING. A GUI change is the same hazard, worse: a broken grid row or a bad `configure` call
raises only when the widget is actually built and clicked. So this builds the real `StatusWindow`
against real collected state and drives the real controls.

WHAT IT ASSERTS, and each maps to a sentence in the request:
  "move the questions already answered to an archive I can click into"
      -> the archive toggle lists answered rows, and lists NONE of them when it is off
      -> clicking an archived row puts that question AND the recorded answer in the reading pane
  "make more room for the question text when it's selected"
      -> the bigger-reading-pane control actually reduces the table's height, which on this tab is
         what hands rows to the (only) weighted grid row
  and the thing most likely to break silently:
      -> the controls live INSIDE the table wrapper, so `_board_detail_row` and the answer box must
         still be on the grid rows their attributes claim.

Headless via `withdraw()`; needs no display server beyond a Tk build.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "tools"))

import tkinter as tk  # noqa: E402

import status_gui as G  # noqa: E402
import status_state as S  # noqa: E402


def main() -> int:
    b = S.collect_board()
    ans = b.get("answered") or []
    print("collector: %d open, %d answered rows exposed" % (b.get("n_open", 0), len(ans)))
    assert isinstance(ans, list), "collect_board() must expose an 'answered' LIST for the archive"
    if not ans:
        print("SKIP: no answered rows on the board, so the archive cannot be exercised.")
        return 0
    for k in ("id", "question", "answer"):
        assert k in ans[0], "answered row is missing %r -- the archive pane renders it" % k

    root = tk.Tk()
    root.withdraw()
    w = G.StatusWindow(root)
    state = S.collect()
    w.render(state)

    # ---- 1. archive OFF: no ANSWERED rows listed ------------------------------------------
    kinds = [w._wait_rows[i].get("_kind") for i in w.board_tv.get_children()]
    assert "ANSWERED" not in kinds, \
        "answered rows are showing in the WORKING list -- that is the thing being fixed"
    n_open_view = len(kinds)
    print("archive OFF: %d rows, kinds=%s" % (n_open_view, sorted(set(kinds))))

    # ---- 2. archive ON: only ANSWERED rows -------------------------------------------------
    w._state = state
    w._toggle_board_archive()
    ids = w.board_tv.get_children()
    kinds = [w._wait_rows[i].get("_kind") for i in ids]
    assert ids, "archive is EMPTY though the collector exposed %d answered rows" % len(ans)
    assert set(kinds) == {"ANSWERED"}, "archive must show ONLY answered rows, got %s" % set(kinds)
    print("archive ON : %d rows, all ANSWERED" % len(ids))

    # ---- 3. clicking an archived row shows the question AND the answer ---------------------
    w.board_tv.selection_set(ids[0])
    w._show_board_detail()
    txt = w.board_detail.get("1.0", "end")
    assert "YOUR ANSWER" in txt, "archive detail pane does not show the recorded answer"
    row = w._wait_rows[ids[0]]
    head = str(row.get("question") or "")[:40]
    assert head and head in txt, "archive detail pane does not show the question text"
    assert "(not recorded)" not in txt, \
        "placeholder text for a field this schema never carries -- it is noise on every row"
    print("archive row click: question + answer both rendered (%d chars)" % len(txt))

    # ---- 4. the bigger-reading-pane control really shrinks the table -----------------------
    before = int(w.board_tv.cget("height"))
    w._toggle_board_big_read()
    after = int(w.board_tv.cget("height"))
    assert after < before, "bigger-reading-pane did not shrink the table (%d -> %d)" % (before,
                                                                                        after)
    w._toggle_board_big_read()
    assert int(w.board_tv.cget("height")) == before, "reading-pane toggle does not restore"
    print("reading pane: table height %d -> %d -> %d (reversible)" % (before, after, before))

    # ---- 5. the layout attributes still point at the rows they claim -----------------------
    info = w.board_detail.master.grid_info()
    assert int(info.get("row", -1)) == w._board_detail_row, \
        ("the detail pane moved off _board_detail_row (%s vs %s) -- inserting the controls pushed "
         "the layout" % (info.get("row"), w._board_detail_row))
    print("layout: detail pane still on row %d as its attribute claims" % w._board_detail_row)

    # ---- 6. back to open questions ---------------------------------------------------------
    w._toggle_board_archive()
    kinds = [w._wait_rows[i].get("_kind") for i in w.board_tv.get_children()]
    assert "ANSWERED" not in kinds, "toggling back left archived rows in the working list"
    print("toggled back: %d rows, no ANSWERED" % len(kinds))

    root.destroy()
    print("\nALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
