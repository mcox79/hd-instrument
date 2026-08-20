"""POSITIVE CONTROL for the GUI's new "you are running old code" banner.

WHY THIS EXISTS. The banner was written because the owner's dashboard process ran for three days
while four requested features landed on disk unseen. A banner that never fires would reproduce that
failure exactly, while LOOKING like the fix -- which is this project's most-repeated fault class
(*a checker sharing a flaw with what it checks hides it*). So the guard is run against the very
situation that broke: a file edited after the process loaded it.

IT DRIVES THE REAL WIDGET, not a re-implementation of the predicate. Testing a copy of the
comparison would pass even if the banner were never gridded, which is the failure that matters.
Tk is driven headlessly via an unmapped root (`withdraw`), so this needs no display.

THREE CASES, and the third is the one that keeps the banner honest:
  FRESH   file untouched since import      -> banner HIDDEN
  STALE   file's mtime moved forward       -> banner SHOWN
  BACK    mtime restored                   -> banner HIDDEN AGAIN (it must not latch on)
"""
import os
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "tools"))

import tkinter as tk

import status_gui as G

SRC = Path(G.__file__).resolve()
ORIG = SRC.stat()


class _Stub:
    """The smallest object `_check_self_stale` actually touches: a label and two flags."""

    def __init__(self, root):
        self.stale_lbl = tk.Label(root, text="")
        self.stale_shown = False
        self._gridded = False
        # Record grid()/grid_remove() calls so we assert on the WIDGET, not just the flag.
        _real_grid, _real_rm = self.stale_lbl.grid, self.stale_lbl.grid_remove

        def grid(*a, **k):
            self._gridded = True
            return _real_grid(*a, **k)

        def grid_remove(*a, **k):
            self._gridded = False
            return _real_rm(*a, **k)

        self.stale_lbl.grid = grid
        self.stale_lbl.grid_remove = grid_remove

    _check_self_stale = G.StatusWindow._check_self_stale


def main() -> int:
    root = tk.Tk()
    root.withdraw()
    s = _Stub(root)

    # --- FRESH: nothing changed since import ---------------------------------
    s._check_self_stale()
    assert not s.stale_shown, "banner fired on an UNCHANGED file -- it would cry wolf every run"
    assert not s._gridded, "banner widget was gridded while the file was unchanged"
    print("FRESH  file untouched            -> banner hidden   OK")

    # --- STALE: reproduce the owner's three days, without waiting three days --
    # +2 hours is beyond any sub-second filesystem jitter and is the same *kind* of difference the
    # real incident had (a later edit), just compressed.
    future = ORIG.st_mtime + 7200
    os.utime(SRC, (ORIG.st_atime, future))
    try:
        s._check_self_stale()
        assert s.stale_shown, "BANNER DID NOT FIRE ON AN EDITED FILE -- this is the original bug"
        assert s._gridded, "banner flag set but the widget was never placed on screen"
        txt = s.stale_lbl.cget("text")
        assert "OLD CODE" in txt and "OPEN IT AGAIN" in txt, \
            "banner text does not tell the owner what to DO: %r" % txt[:120]
        print("STALE  file edited after import  -> banner SHOWN    OK")
        print("       text: %s" % txt.splitlines()[0])
    finally:
        os.utime(SRC, (ORIG.st_atime, ORIG.st_mtime))

    # --- BACK: it must clear, not latch --------------------------------------
    s._check_self_stale()
    assert not s.stale_shown, "banner LATCHED on -- it never clears once shown"
    assert not s._gridded, "banner widget stayed on screen after the file matched again"
    print("BACK   mtime restored            -> banner hidden   OK")

    # --- the unreadable-baseline path must stay silent, never guess ----------
    saved = G._SRC_MTIME_AT_IMPORT
    G._SRC_MTIME_AT_IMPORT = None
    try:
        s._check_self_stale()
        assert not s.stale_shown, "claimed staleness with NO baseline to compare against"
    finally:
        G._SRC_MTIME_AT_IMPORT = saved
    print("NULL   no baseline available     -> silent          OK")

    root.destroy()
    print("\nALL 4 CASES PASS -- the guard fires on the condition that actually occurred.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
