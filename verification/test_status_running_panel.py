#!/usr/bin/env python
"""Witness: the RUNNING panel has room to read, resizes, and never shows dead work as live.

WHY THIS EXISTS. Owner, 2026-08-16: *"the current runs have very small fields for me to see what's
currently running."* And separately, measured the same night: all 39 `scratch/*.pid` files pointed
at DEAD processes -- three of them cited as live in every agent brief for hours, and one of them was
the dashboard's own process -- while the panel showed none of them at all, because it could only
list processes that still existed.

EVERYTHING HERE IS ASSERTED AT THE RENDERED WIDGET, by building the real `StatusWindow` and reading
back `tv.column(c, 'width')` and `winfo_width()`. Reading the source would have missed both root
causes, which is why the last three defects in this window were only pinned by rendering it:

  L1  THE COLUMNS NEVER HAD ROOM. The table's declared widths summed to 1140 px inside a viewport
      of ~1100, so there was no spare space for `stretch` to hand out and every column stayed
      exactly as narrow as it was declared, no matter how large the window got. Asserted as: the
      declared widths FIT, and every column GROWS when the window is widened.
  L2  THE WINDOW OPENED BIGGER THAN THE SCREEN. `geometry("1280x860")` was unconditional; this
      display is 1128x752, so the right-hand columns and the bottom of every panel were off the
      edge. Asserted against the live screen size.
  L3  THE PANEL WAS NOT RESIZABLE. Three fixed grid rows, so the run list could not be given more
      room at the expense of the others. Asserted as: a PanedWindow with real sashes.
  L4  DEAD WORK WAS INVISIBLE, WHICH READS AS "NOTHING TO SEE". A run that died vanished while its
      pid file went on asserting it. Asserted as: a dead claim renders its own row, in an explicit
      DEAD BUT CLAIMED LIVE state, with its pid file and its leftover log named in the detail box.

RUN PRE-FIX, TO PROVE IT FAILS (does not modify the working tree):

    mkdir -p scratch/_prefix_tools
    git show HEAD:tools/status_gui.py   > scratch/_prefix_tools/status_gui.py
    git show HEAD:tools/status_state.py > scratch/_prefix_tools/status_state.py
    HD_TOOLS_DIR=scratch/_prefix_tools .venv/Scripts/python.exe \
        verification/test_status_running_panel.py

SKIPS (never fails) when there is no display.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = Path(os.environ.get("HD_TOOLS_DIR") or (REPO / "tools"))
if not TOOLS.is_absolute():
    TOOLS = (REPO / TOOLS).resolve()
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(REPO / "tools") not in sys.path:
    sys.path.append(str(REPO / "tools"))

# Redirect the writable documents before importing, so nothing here can touch the owner's board.
_TD = Path(tempfile.mkdtemp(prefix="running_panel_witness_"))
os.environ["HD_BOARD_PATH"] = str(_TD / "BOARD.md")

import tkinter as tk  # noqa: E402

import status_gui  # noqa: E402
import status_pidclaims  # noqa: E402  (always the real one: it is the FIXTURE source, not the SUT)
import status_state  # noqa: E402

DEAD_NAME = "a_run_that_died"
LIVE_NAME = "a_run_still_going"


def _fixture_claims() -> tuple[dict, int, int]:
    """A scratch dir holding one genuinely dead claim and one genuinely live one."""
    scratch = _TD / "scratch"
    scratch.mkdir(exist_ok=True)
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    dead_pid = p.pid
    live_pid = os.getpid()
    (scratch / f"{DEAD_NAME}.pid").write_text(str(dead_pid), encoding="utf-8")
    (scratch / f"{DEAD_NAME}.err").write_text("Traceback (most recent call last): ...",
                                              encoding="utf-8")
    (scratch / f"{LIVE_NAME}.pid").write_text(str(live_pid), encoding="utf-8")
    return status_pidclaims.scan_claims(live_pids={live_pid}, scratch=scratch), dead_pid, live_pid


def _payload(claims: dict, live_pid: int) -> dict:
    return {
        "ts": "witness", "took_s": 0.0,
        "loop": {"armed": False},
        "running": {
            "status": "OK", "state_status": "OK", "alerts": [],
            "gpu": {}, "gpu_util": None, "queues": {}, "runners": {},
            "local_experiments": [{"name": f"exp_{LIVE_NAME}.py", "pid": live_pid,
                                   "elapsed_s": 120.0, "mem_kb": 2048,
                                   "progress_pct": 40.0, "unit_idx": 2, "total_units": 5}],
            "claims": claims,
            "agents": {"status": "OK", "agents": [], "n_active": 0},
            "remote_checkpoint": {"state": "NO_REMOTE_RUN", "reason": "nothing remote"},
        },
        "ages": {},
    }


def _widths(tv) -> dict:
    return {c: int(tv.column(c, "width")) for c in tv["columns"]}


def _settle(root, geo: str) -> None:
    root.geometry(geo)
    for _ in range(8):
        root.update_idletasks()
        root.update()


def _row_values(tv) -> list[tuple]:
    return [tuple(str(v) for v in tv.item(iid, "values")) for iid in tv.get_children()]


def run() -> int:
    ok = True
    results: list[tuple[bool, str]] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        results.append((bool(cond), label))
        print(f"[running-panel] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[running-panel] SKIP no display available: {exc}", file=sys.stderr)
        return 0

    claims, dead_pid, live_pid = _fixture_claims()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    print(f"[running-panel] screen is {sw}x{sh}; dead fixture pid {dead_pid}, "
          f"live fixture pid {live_pid}")
    try:
        gui = status_gui.StatusWindow(root)
        gui.nb.select(gui.tab_running)

        # ---------------------------------------------------------------
        # L2 -- THE WINDOW MUST FIT THE SCREEN IT OPENS ON.
        # ---------------------------------------------------------------
        for _ in range(6):
            root.update_idletasks()
            root.update()
        req = root.geometry().split("+")[0]
        rw, rh = (int(x) for x in req.split("x"))
        check(rw <= sw and rh <= sh,
              f"L2 the window opens INSIDE the {sw}x{sh} screen (it asks for {rw}x{rh})")
        mn_w, mn_h = root.minsize()
        check(mn_w <= sw and mn_h <= sh,
              f"L2 and its MINIMUM size fits too, so it can always be shrunk into view "
              f"(minimum {mn_w}x{mn_h})")

        # ---------------------------------------------------------------
        # L3 -- THE PANEL IS RESIZABLE.
        # ---------------------------------------------------------------
        pw = getattr(gui, "running_panes", None)
        check(pw is not None, "L3 the RUNNING tab has a resizable split at all")
        if pw is not None:
            check(len(pw.panes()) >= 3,
                  f"L3 with a draggable sash between each part (got {len(pw.panes())} panes)")

        # ---------------------------------------------------------------
        # L4 -- DEAD WORK IS SHOWN, AS DEAD.
        # ---------------------------------------------------------------
        gui._r_running(_payload(claims, live_pid))
        for _ in range(4):
            root.update_idletasks()
            root.update()
        rows = _row_values(gui.local_tv)
        flat = [" | ".join(r) for r in rows]
        dead_rows = [r for r in flat if DEAD_NAME in r]
        check(len(dead_rows) == 1,
              f"L4 a run whose process is GONE still gets a row -- it does not silently vanish "
              f"(found {len(dead_rows)} of {len(rows)} rows)")
        check(dead_rows and "DEAD" in dead_rows[0].upper(),
              f"L4 and the row SAYS it is dead, in words, in its own column "
              f"({dead_rows[0][:110] if dead_rows else None!r})")
        check(dead_rows and "CLAIM" in dead_rows[0].upper(),
              f"L4 and says that something is still CLAIMING it is live "
              f"({dead_rows[0][:110] if dead_rows else None!r})")
        check(dead_rows and str(dead_pid) in dead_rows[0],
              f"L4 naming the process number that is gone ({dead_rows[0][:130] if dead_rows else None!r})")

        live_rows = [r for r in flat if LIVE_NAME in r and "DEAD" not in r.upper()]
        check(len(live_rows) >= 1,
              f"L4 and a genuinely live run is still listed, distinctly (found {len(live_rows)})")
        check(live_rows and "RUNNING" in live_rows[0].upper(),
              f"L4 and says RUNNING ({live_rows[0][:90] if live_rows else None!r})")

        # THE STATE MUST BE A COLUMN, not something inferred from a colour a reader may not see.
        # Deliberately keyed on ACTUALLY, not on RUNNING: the pre-fix table already had a column
        # headed "RUNNING FOR" (an elapsed time), which would have made a substring test on
        # "RUNNING" pass while the panel still had no state column at all.
        heads = [str(gui.local_tv.heading(c, "text")).upper() for c in gui.local_tv["columns"]]
        check(any("ACTUALLY" in h for h in heads),
              f"L4 there is a column that answers 'is it ACTUALLY running' (headings {heads})")

        # And the detail box must name the file that is telling the lie, plus the leftover log.
        dead_iid = next((iid for iid in gui.local_tv.get_children()
                         if DEAD_NAME in " ".join(str(v) for v in
                                                  gui.local_tv.item(iid, "values"))), None)
        check(dead_iid is not None, "L4 the dead row is selectable")
        if dead_iid is not None:
            gui.local_tv.selection_set(dead_iid)
            gui._show_running_detail()
            txt = gui.running_detail.get("1.0", "end")
            check(f"{DEAD_NAME}.pid" in txt,
                  f"L4 selecting it names the pid file still asserting the run "
                  f"(detail says {txt[:150]!r})")
            check(f"{DEAD_NAME}.err" in txt,
                  "L4 and names the log it left behind, which is the only evidence remaining")
            check("NOT happening" in txt or "not happening" in txt.lower(),
                  f"L4 and says plainly that the run is not happening (detail {txt[:220]!r})")

        # ---------------------------------------------------------------
        # L1 -- THE COLUMNS HAVE ROOM, AND SHARE THE WINDOW.
        # ---------------------------------------------------------------
        small = f"{min(1000, sw - 40)}x{min(700, sh - 40)}+10+10"
        big = f"{min(1280, sw)}x{min(860, sh)}+0+0"
        _settle(root, small)
        w_small = _widths(gui.local_tv)
        tree_w = gui.local_tv.winfo_width()
        a_small = _widths(gui.agents_tv)
        _settle(root, big)
        w_big = _widths(gui.local_tv)
        a_big = _widths(gui.agents_tv)
        print(f"[running-panel] run table at {small}: tree={tree_w} {w_small}")
        print(f"[running-panel] run table at {big}:   tree={gui.local_tv.winfo_width()} {w_big}")
        print(f"[running-panel] agents   at {big}:   {a_big}")

        check(sum(w_small.values()) <= tree_w + 2,
              f"L1 the columns FIT the table at the smaller size ({sum(w_small.values())} px of "
              f"columns in {tree_w} px) -- overflow is what left no space to stretch into")
        never_grew = [c for c in w_big if w_big[c] <= w_small[c]]
        check(not never_grew,
              f"L1 EVERY column grows when the window is widened, not just the wide ones "
              f"(stuck: {never_grew}; small {w_small} -> big {w_big})")
        agents_stuck = [c for c in a_big if a_big[c] <= a_small[c]]
        check(not agents_stuck,
              f"L1 the AGENTS table shares the width too (stuck: {agents_stuck})")

        # The identity and state columns specifically must be readable, not token.
        name_col = "name" if "name" in w_big else None
        state_col = "state" if "state" in w_big else None
        check(name_col is not None and w_big[name_col] >= 250,
              f"L1 the WHAT-IT-IS column is wide enough to read a run name "
              f"({w_big.get(name_col)} px)")
        check(state_col is not None and w_big[state_col] >= 165,
              f"L1 the IS-IT-RUNNING column is wide enough to read its own state "
              f"({w_big.get(state_col)} px)")

        # A minimum under every column, so shrinking cannot crush identity to an ellipsis.
        no_floor = [c for c in gui.local_tv["columns"]
                    if int(gui.local_tv.column(c, "minwidth")) < 55]
        check(not no_floor,
              f"L1 every column has a floor under it, so shrinking cannot crush it ({no_floor})")

        # ---------------------------------------------------------------
        # LIVE DATA. Not a fixture: the repo's real scratch/ directory.
        # ---------------------------------------------------------------
        live = status_state.collect_running()
        cl = live.get("claims") or {}
        print(f"[running-panel] LIVE scratch/: {cl.get('n_claims')} claims, "
              f"{cl.get('n_dead')} dead-but-claimed-live, {cl.get('n_running')} confirmed running")
        check(cl.get("status") == "OK",
              f"LIVE the real pid-file claims were read ({cl.get('status')}: "
              f"{str(cl.get('detail'))[:90]})")
        check(isinstance(cl.get("n_dead"), int) and cl["n_dead"] >= 1,
              f"LIVE the repo really does hold dead-but-claimed-live runs right now "
              f"(n_dead={cl.get('n_dead')} of {cl.get('n_claims')})")
        gui._r_running(live if "loop" in live else dict(_payload(claims, live_pid),
                                                        running=live))
        for _ in range(3):
            root.update_idletasks()
            root.update()
        live_flat = " | ".join(" ".join(r) for r in _row_values(gui.local_tv))
        check("DEAD BUT CLAIMED LIVE" in live_flat,
              "LIVE and the panel renders them, so the owner sees them rather than an empty table")
        tab = str(gui.nb.tab(gui.tab_running, "text"))
        check("DEAD" in tab.upper(),
              f"LIVE the tab title itself carries the count, so it is visible without opening the "
              f"tab (title {tab!r})")

    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass

    n_fail = sum(1 for good, _ in results if not good)
    print(f"[running-panel] {len(results) - n_fail}/{len(results)} checks passed")
    print("[running-panel] RESULT:", "PASS" if ok else "FAIL")
    print(f"[running-panel] modules under test: {TOOLS}")
    return 0 if ok else 1


def test_status_running_panel() -> None:
    assert run() == 0, "the RUNNING panel witness failed; see stderr"


if __name__ == "__main__":
    raise SystemExit(run())
