"""Witness for the two MEASURED GUI defects fixed 2026-08-20, plus the diagnostics log.

THE DEFECTS, both reported by the owner and both measured rather than guessed at:

  1. *"it's hanging a lot"* -- `_newest_metrics_mtime()` walked `data/` with a `stat()` per
     directory **on the UI thread**, reached from `_update_tab_ages`, which the 1-second tick
     calls. Measured on the owner's own tree: **8,155 directories, 6.91 SECONDS**. Cached for 60s,
     so the window froze solid for ~7 seconds once a minute. The cache was doing its job; the
     defect was that the work was on the thread that draws.

  2. *"the tabs keep changing slightly with every update"* -- the same loop called
     `nb.tab(text=...)` on all eight tabs every second unconditionally. Each call re-measures the
     label and re-lays out the Notebook, so the tab strip shifted as an age string grew a character
     ("9s" -> "10s").

WHY A WITNESS AND NOT A CODE READ. Two earlier freeze reports were investigated and closed with "I
cannot tell you why" because there was no evidence left behind. The fix for that is this file plus
the diagnostics log it checks: the next report arrives WITH a duration attached.

Headless via `withdraw()`.
"""
import json
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "tools"))

import tkinter as tk  # noqa: E402

import status_gui as G  # noqa: E402


def main() -> int:
    root = tk.Tk()
    root.withdraw()
    w = G.StatusWindow(root)

    # ---- 1. THE FREEZE: the UI-thread call must return immediately -------------------------
    # First call has an EMPTY cache, which is exactly the case that used to block for 6.91s.
    w._metrics_mtime_cache = None
    t0 = time.time()
    w._newest_metrics_mtime()
    ms = 1000 * (time.time() - t0)
    assert ms < 250, ("_newest_metrics_mtime BLOCKED THE UI THREAD for %.0f ms on a cold cache -- "
                      "this is the 6.9-second freeze returning" % ms)
    print("cold-cache _newest_metrics_mtime returned in %.1f ms (was 6,910 ms on the UI thread)"
          % ms)

    # and the whole tick body, which is what the owner actually experiences
    t0 = time.time()
    w._update_tab_ages()
    ms = 1000 * (time.time() - t0)
    assert ms < 250, "_update_tab_ages took %.0f ms on the UI thread" % ms
    print("_update_tab_ages: %.1f ms" % ms)

    # ---- 1b. NO FILE I/O ON THE CALLING THREAD ---------------------------------------------
    # A DURATION ASSERTION CANNOT CATCH THIS ONE. Before the 10s off-thread source-mtime cache,
    # `_update_tab_ages` still ran a stat() per tab source; on an idle disk that is ~0.7ms and the
    # timing check above passed anyway. It only bit under I/O contention -- the diagnostics log
    # recorded `ui_stall` with `tab_ages_ms: 597` while heavy corpus reads were running, and pushed
    # the off-thread data/ scan from 5.4s to 121.6s. So assert the ABSENCE OF I/O, not its speed.
    stats = {"n": 0}
    real_stat = Path.stat

    def counting_stat(self, *a, **k):
        stats["n"] += 1
        return real_stat(self, *a, **k)

    Path.stat = counting_stat
    try:
        w._update_tab_ages()          # prime any cache
        time.sleep(0.4)               # let the off-thread scans settle
        w._update_tab_ages()
        stats["n"] = 0
        w._update_tab_ages()          # the pass that must be I/O-free
        on_thread = stats["n"]
    finally:
        Path.stat = real_stat
    assert on_thread == 0, ("_update_tab_ages made %d stat() calls ON THE CALLING THREAD -- under "
                            "disk contention each of those blocks, which is the residual stall the "
                            "diagnostics log recorded at 597ms" % on_thread)
    print("tab ages: %d stat() calls on the calling thread (all file I/O is off-thread)" % on_thread)

    # ---- 2. THE CHURN: a second identical pass must re-title NOTHING ------------------------
    calls = {"n": 0}
    real_tab = w.nb.tab

    def counting_tab(tab_id, **kw):
        if "text" in kw:
            calls["n"] += 1
        return real_tab(tab_id, **kw)

    w.nb.tab = counting_tab
    # CLEAR THE REMEMBERED TITLES FIRST, so this pass MUST re-title. Without it the "changed" pass
    # also reads 0 and the test cannot tell "correctly skipping" from "never titling at all" --
    # a checker sharing a blind spot with the thing it checks, which is this repo's most repeated
    # fault. The first number below is the POSITIVE CONTROL.
    w._tab_text_now = {}
    w._update_tab_ages()
    first = calls["n"]
    calls["n"] = 0
    w._update_tab_ages()
    second = calls["n"]
    w.nb.tab = real_tab
    assert first > 0, ("no tab was EVER re-titled, so the 'unchanged pass does nothing' result "
                       "below proves nothing -- the guard could simply be dead")
    assert second == 0, ("the tab strip was re-titled %d times on an unchanged pass -- this is the "
                         "once-a-second twitch the owner reported" % second)
    print("tab re-titles: %d on a changed pass (positive control), %d on an unchanged pass"
          % (first, second))

    # ---- 3. sub-minute ages must be STABLE, or the guard above fires every second -----------
    assert G.StatusWindow._fmt_age(3) == G.StatusWindow._fmt_age(41) == "just now", \
        "sub-minute ages still differ second to second: %r vs %r" % (
            G.StatusWindow._fmt_age(3), G.StatusWindow._fmt_age(41))
    assert G.StatusWindow._fmt_age(3600).endswith("m") or G.StatusWindow._fmt_age(3600).endswith("h")
    print("age format: 3s and 41s both render %r (stable within the minute)"
          % G.StatusWindow._fmt_age(3))

    # ---- 4. THE DIAGNOSTICS LOG actually gets written ---------------------------------------
    before = G.DIAG_PATH.stat().st_size if G.DIAG_PATH.exists() else 0
    G._diag("witness_probe", note="written by the verification witness")
    assert G.DIAG_PATH.exists(), "diagnostics log was never created at %s" % G.DIAG_PATH
    assert G.DIAG_PATH.stat().st_size > before, "diagnostics log did not grow"
    last = G.DIAG_PATH.read_text(encoding="utf-8").strip().splitlines()[-1]
    rec = json.loads(last)
    assert rec.get("event") == "witness_probe", "diagnostics log wrote the wrong record: %r" % rec
    print("diagnostics log: wrote and read back %r at %s" % (rec["event"], G.DIAG_PATH.name))

    # ---- 5. a logging FAILURE must never raise into the UI ----------------------------------
    saved = G.DIAG_PATH
    try:
        G.DIAG_PATH = Path("Z:/definitely/not/a/real/path/diag.jsonl")
        G._diag("should_not_raise", x=1)          # must swallow
        print("diagnostics log: an unwritable path is swallowed, not raised")
    finally:
        G.DIAG_PATH = saved

    root.destroy()
    print("\nALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
