#!/usr/bin/env python
"""Witness: the owner can write a note mid-run, and BOTH hooks put it in front of the agent.

WHY THIS EXISTS. Owner, 2026-08-16, verbatim:

    "a box that I can write any commentary I'd like you to look at during a run without
     interrupting you... a hook on that that tells you that I've sent something to look at during a
     computational run."

Two halves, and a channel with only the first half is worse than none -- the owner writes, believes
it landed, and nothing ever reads it. So this witness drives BOTH ends, through the real code:

  C1  THE BOX WRITES, AND SAYS SO. The `StatusWindow` is built headlessly, typed into, and the
      button pressed. The confirmation must quote the text back and name the file. The Save button
      on the panel above this one failed silently for hours and the owner had no way to tell; a
      confirmation that does not quote what landed does not fix that.
  C2  IT REACHES THE AGENT AT SESSION START, verbatim, through `tools/session_start_hook.py`.
  C3  IT REACHES THE AGENT MID-RUN, through the Stop hook's continuation path, fired as a REAL
      SUBPROCESS with the loop DISARMED -- so the note alone is proven sufficient to reach the
      session, rather than riding on a block that would have happened anyway.
  C4  READ/UNREAD IS HONEST. Surfaced once, never twice; a NEW note always fires; an edit to an
      already-seen note fires again, because those words have not been seen.
  C5  IT WORKS FROM THE MARKDOWN FILE ALONE. Every check above is repeated with the note typed
      STRAIGHT INTO `notes/COMMENTARY.md` and no tool involved -- the owner writes from other
      devices, and a channel that only notices its own window's writes is not the channel asked for.
  C6  THE HOOK STAYS INSIDE ITS BUDGET. Measured, not assumed: the session-start hook is documented
      as needing to stay under 10 s.

NOTHING HERE TOUCHES THE REAL notes/COMMENTARY.md OR ITS READ MARK. Both are redirected to a
tempdir before the imports, because a test that consumed the owner's actual unread notes -- marking
them read as a side effect of running -- would be the worst possible failure of this file.

SKIPS (never fails) when there is no display; the non-GUI checks still run.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

_TD = Path(tempfile.mkdtemp(prefix="commentary_witness_"))
_DOC = _TD / "COMMENTARY.md"
_MARK = _TD / "commentary_read.json"
os.environ["HD_COMMENTARY_PATH"] = str(_DOC)
os.environ["HD_COMMENTARY_MARK"] = str(_MARK)
os.environ["HD_BOARD_PATH"] = str(_TD / "BOARD.md")

import commentary  # noqa: E402
import session_start_hook  # noqa: E402

assert commentary.DOC == _DOC, (
    f"the witness failed to redirect the side channel away from the real one ({commentary.DOC}) "
    f"-- refusing to run against the owner's notes/COMMENTARY.md")

STOP_HOOK = REPO / "data" / "hooks" / "staging" / "stop_hook.py"

FROM_WINDOW = "check the affect channel before another night on bridging"
FROM_PHONE = "and stop quoting the 6x-its-floor number | it is retracted"
EDITED = "ACTUALLY, stop quoting it everywhere, not just in the status file"


def _fire_stop_hook(session: str, td: Path) -> str:
    """Run the REAL Stop hook as a subprocess, exactly as the harness does."""
    env = dict(os.environ)
    env["CLAUDE_SESSION_NAME"] = session
    env["HD_COMMENTARY_PATH"] = str(_DOC)
    env["HD_COMMENTARY_MARK"] = str(_MARK)
    env["HD_BOARD_PATH"] = str(td / "BOARD.md")
    env["HD_AUTOLOOP_STATE"] = str(td / "autoloop.json")   # never armed by this witness
    env["HD_STOP_DEDUPE_WINDOW_S"] = "0"
    env.pop("HD_STOP_HOOK_HARD_CAP", None)
    payload = {"stop_hook_active": False, "transcript_path": str(td / "sess.jsonl")}
    p = subprocess.run([sys.executable, str(STOP_HOOK)], env=env, input=json.dumps(payload),
                       capture_output=True, text=True, timeout=60)
    return (p.stdout or "").strip()


def _reason(out: str) -> str:
    if not out:
        return ""
    try:
        return json.loads(out.splitlines()[-1]).get("reason", "")
    except (json.JSONDecodeError, ValueError):
        return ""


def run() -> int:
    ok = True
    results: list[tuple[bool, str]] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        results.append((bool(cond), label))
        print(f"[commentary-ch] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    (_TD / "sess.jsonl").write_text("", encoding="utf-8")

    # -------------------------------------------------------------------
    # C1 -- THE BOX WRITES, AND SAYS SO.
    # -------------------------------------------------------------------
    import tkinter as tk
    gui_ran = False
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[commentary-ch] SKIP the GUI half: no display ({exc})", file=sys.stderr)
        root = None
    if root is not None:
        root.withdraw()
        try:
            import status_gui
            gui = status_gui.StatusWindow(root)
            for _ in range(3):
                root.update_idletasks()
                root.update()
            check(hasattr(gui, "commentary_box") and hasattr(gui, "commentary_btn"),
                  "C1 the window has a commentary box with its own send button")
            # DESIGN REVERSED 2026-08-17 (defect 2). It used to have to live OUTSIDE the tab strip
            # so it was reachable from every panel; the owner reported that made it "take a whole
            # section of every tab" and asked for "a separate tab only." Now the assertion is the
            # opposite: it must live INSIDE the notebook, on its OWN dedicated tab, so it no longer
            # costs the other seven tabs any space. The unread count moves to the tab's own title.
            check(hasattr(gui, "tab_commentary"),
                  "C1-DEFECT2 the note box has its own dedicated notebook tab")
            parent = str(gui.commentary_box.winfo_parent())
            if hasattr(gui, "tab_commentary"):
                check(parent.startswith(str(gui.tab_commentary)),
                      f"C1-DEFECT2 it lives INSIDE that one tab, not spread across every panel "
                      f"(its parent is {parent!r}, its tab is {str(gui.tab_commentary)!r})")
            check(".!notebook" in parent,
                  f"C1-DEFECT2 and that tab is part of the notebook, not a bar under it (its "
                  f"parent is {parent!r})")

            gui.commentary_box.insert("1.0", FROM_WINDOW)
            gui._send_commentary()
            conf = gui.commentary_status.cget("text")
            check("SENT" in conf.upper() and "NOT SENT" not in conf.upper(),
                  f"C1 pressing it reports success rather than doing nothing visible "
                  f"(screen says {conf[:120]!r})")
            check(FROM_WINDOW[:35] in conf,
                  f"C1 and QUOTES BACK what was written (got {conf[:170]!r})")
            check("COMMENTARY.md" in conf,
                  f"C1 and names the file it went to (got {conf[:170]!r})")
            check(gui.commentary_box.get("1.0", "end").strip() == "",
                  "C1 and clears the box, so the same note cannot be sent twice by accident")

            entries = commentary.load()
            check(any(e["body"] == FROM_WINDOW for e in entries),
                  f"C1 ROUND TRIP: the note is on disk, verbatim "
                  f"({[e['body'][:40] for e in entries]})")
            gui_ran = True
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass
    if not gui_ran:
        commentary.add(FROM_WINDOW, "the status window")   # keep the rest of the witness meaningful

    # -------------------------------------------------------------------
    # C2 -- SESSION START SURFACES IT, VERBATIM.
    # -------------------------------------------------------------------
    out = session_start_hook.commentary_report(_DOC, _MARK)
    check(FROM_WINDOW in out,
          f"C2 the session-start hook injects the owner's own words, not a summary "
          f"(got {out[:160]!r})")
    check("UNREAD" in out.upper(),
          f"C2 and flags them as unread so they are not read as background ({out[:110]!r})")
    check("no unread notes" in session_start_hook.commentary_report(_DOC, _MARK),
          "C4 surfaced ONCE -- a second session start does not repeat it")

    # -------------------------------------------------------------------
    # C5 -- THE HAND EDIT. Typed straight into the markdown, no tool involved.
    # -------------------------------------------------------------------
    with _DOC.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## 2026-08-16T23:30:00Z  --  typed on my phone\n\n{FROM_PHONE}\n")
    u = commentary.unread()
    check(len(u) == 1 and u[0]["body"] == FROM_PHONE,
          f"C5 a note typed straight into the markdown is unread, with no tool involved "
          f"({[e['body'][:40] for e in u]})")
    check(u and "|" in u[0]["body"],
          "C5 including a raw pipe, which needs no escaping in a plain markdown log")

    # -------------------------------------------------------------------
    # C3 -- IT REACHES A RUNNING SESSION, through the real Stop hook, DISARMED.
    # -------------------------------------------------------------------
    session = f"_commentary_witness_{os.getpid()}"
    _fire_stop_hook(session, _TD)          # first fire establishes this session's marks
    with _DOC.open("a", encoding="utf-8") as fh:
        fh.write("\n## 2026-08-16T23:45:00Z  --  typed on my phone\n\n"
                 "one more thing while you are running\n")
    reason = _reason(_fire_stop_hook(session, _TD))
    check(bool(reason),
          "C3 an unread note BLOCKS the stop, so a run in flight is told about it "
          "(loop DISARMED -- the note alone did this)")
    check("one more thing while you are running" in reason,
          f"C3 and the note is quoted verbatim into what the session reads next "
          f"(got {reason[:200]!r})")
    check("COMMENTARY" in reason.upper(),
          f"C3 naming the file, so the session can go read the rest ({reason[:140]!r})")
    check(_reason(_fire_stop_hook(session, _TD)) == "",
          "C4 and it does not re-fire every turn until the continuation cap")

    # -------------------------------------------------------------------
    # C4 -- AN EDIT TO AN ALREADY-SEEN NOTE FIRES AGAIN.
    # -------------------------------------------------------------------
    txt = _DOC.read_text(encoding="utf-8").replace(FROM_PHONE, EDITED)
    _DOC.write_text(txt, encoding="utf-8")
    u2 = commentary.unread()
    check(len(u2) == 1 and u2[0]["body"] == EDITED,
          f"C4 editing a note the agent had already seen makes it unread again -- changed words "
          f"have not been seen ({[e['body'][:40] for e in u2]})")

    # NOTHING IS EVER LOST: the log keeps every entry, including the ones already read.
    all_entries = commentary.load()
    check(any(e["body"] == FROM_WINDOW for e in all_entries),
          f"the first note is still in the file after four later writes -- this is a log, never "
          f"rewritten ({len(all_entries)} entries)")

    # -------------------------------------------------------------------
    # C6 -- BUDGET. The session-start hook is documented as needing to stay under 10 s.
    # -------------------------------------------------------------------
    t0 = time.time()
    for _ in range(20):
        commentary.count_unread()
    per = (time.time() - t0) / 20
    check(per < 0.05, f"C6 one unread check costs {per*1000:.2f} ms, so it cannot push the "
                      f"10 s hook budget")

    # And the real repo's own file, whatever state it is in, must parse without raising.
    real = REPO / "notes" / "COMMENTARY.md"
    try:
        n_real = len(commentary.load(real))
        real_ok = True
    except Exception as exc:                      # pragma: no cover
        n_real, real_ok = -1, False
        print(f"[commentary-ch] real file raised: {exc}", file=sys.stderr)
    check(real_ok, f"the repo's own notes/COMMENTARY.md parses without raising "
                   f"({n_real} entries; absent is fine and counts as zero)")

    n_fail = sum(1 for good, _ in results if not good)
    print(f"[commentary-ch] {len(results) - n_fail}/{len(results)} checks passed")
    print("[commentary-ch] RESULT:", "PASS" if ok else "FAIL")
    print(f"[commentary-ch] fixture (not auto-removed, by design): {_DOC}")
    return 0 if ok else 1


def test_commentary_channel() -> None:
    assert run() == 0, "the commentary channel witness failed; see stderr"


if __name__ == "__main__":
    raise SystemExit(run())
