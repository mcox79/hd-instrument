"""WHERE WE ARE / WHAT IS HAPPENING -- the owner's status window.

Launch:
  D:\\AI\\hd-instrument\\.venv\\Scripts\\python.exe D:\\AI\\hd-instrument\\tools\\status_gui.py

WHY THIS REPLACES THE OLD WINDOW. The owner's verdict on `tools/dash_gui.py` (2026-08-15):
*"that gui is ancient and it's not showing anything I care about - can you update it so it's
relevant?"* That window was built for the 4-session fleet/queue architecture, which is dead --
it is agent-spawn only now -- so it showed GPU temperature, queue depth and runner heartbeats,
and nothing about whether the system is beating what it has to beat. This one answers four
questions: WHERE ARE WE, WHAT MOVED, WHICH BRAIN ORGANS DO WE ACTUALLY HAVE, and WHAT IS
HAPPENING RIGHT NOW.

REORGANISED 2026-08-16, on the owner's request: *"can you add your plan to that, and make sure
you keep all this updated? Also feel free to optimize all the content so it's better organized and
actionable, and easier to keep updated."*

FOUR GROUPS, EIGHT TABS. Originally reorganised down to seven (from eight) with the plan added;
back up to eight on 2026-08-17 when the note channel (see "A NOTE FOR ME", below) moved OUT from
under the notebook, where it sat on all seven other tabs, into a dedicated tab of its own -- the
owner reported that a fixed box repeated on every tab was "too much" and asked for "a separate tab
only." What was merged (or, for tab 8, un-merged), and why:

  WHERE WE ARE
    1. WHERE WE ARE           NEW. The five phases of notes/LONG_TERM_PLAN.md, each with its goal,
                              its GATE, its STOP-IF and its status, PLUS which phase we are in and
                              the single next action. PARSED LIVE on every refresh by
                              tools/status_plan.py -- never transcribed, because a transcribed plan
                              is stale the moment the plan moves, and that is the whole defect this
                              panel was asked to fix. Where the plan states no gate, the cell says
                              NOT STATED IN THE PLAN and it is counted as a parser-contract
                              violation on screen.
    2. RUNNING NOW            agents, experiments, the remote box -- AND the overnight loop, MERGED
                              IN from its own former tab. "Is the loop on" is a question about what
                              is running; it did not need a tab of its own, and putting it beside
                              the agents means one place answers "is anything happening".

  WHAT NEEDS YOU
    3. WAITING ON YOU         the board questions the owner can answer by typing, PLUS the standing
                              decisions D1..Dn parsed live out of notes/PLAN.md section 9, PLUS the
                              standing operator decisions that live only in prose. Previously the
                              board questions were here and the standing decisions were in no panel
                              at all -- the owner had to read three documents to find what was
                              waiting on them.

  EVIDENCE
    4. SCORES AND FLOORS      MERGED from the former THE WALLS and PROGRESS MADE tabs. Five of the
                              seven parts appeared in BOTH, so the owner was diffing two tabs by eye
                              to answer one question. One row per part now: what it was, what it is
                              now, and the floor beside both. THE TWO RULES SURVIVE THE MERGE
                              INTACT -- a score is never rendered without its floor, and RETRACTIONS
                              stay first-class rows in the same red as a loss, counted in the tab
                              title. Where the two merged sources disagree about the same part the
                              panel SAYS SO and counts it, rather than picking the flattering one.
    5. BRAIN ORGAN MAP        per organ: the brain structure, what it does in one plain sentence,
                              whether we built it, whether it is switched on, and what it measures.
                              Parsed live from notes/ORGAN_MAP.md plus data/capability_registry.jsonl.
                              Rows where section 10 re-audited an organ and section 4 was never
                              updated are marked CONFLICT and counted -- the panel reports the
                              disagreement instead of silently picking one of the two readings.
    6. HOW CLOSELY WE COPY THE BRAIN
                              the fidelity score, with an unmissable amber banner saying it is NOT a
                              measure of how well anything works and has NOT been shown to predict
                              that. Read from the scoring tool's own verdict string. Rows coloured
                              by the OUTCOME, never by the fidelity score.
    7. LATEST RESULTS         the newest finished experiments, losses as loud as wins.

  D. THE OWNER'S OWN CHANNEL
    8. NOTE FOR ME            MOVED HERE 2026-08-17 from a box that used to sit under the notebook
                              on every one of the other seven tabs. The tab title carries the
                              unread count so the channel stays noticeable without permanently
                              costing every other tab its own vertical space.

EVERY ROW SAYS WHEN ITS OWN EVIDENCE WAS LAST UPDATED (owner, 2026-08-16: *"I'd also like
timestamps for each entry on the dash - when it was last updated so I know what's new and what is
old."*). Every table has a LAST UPDATED column, and what it shows is THE AGE OF THE ARTIFACT THE ROW
IS DERIVED FROM -- the experiment's own `metrics.json`, the document the row was parsed out of, the
transcript an agent is appending to right now. It is NEVER the time this window last refreshed.
Those are different things and conflating them would be worse than showing nothing: a stale number
under a fresh clock reads as current. A row whose artifact cannot be found says UNKNOWN.

Relative ages are shown in the cell because that is what reads at a glance; the absolute time, the
artifact path and how it was resolved are all in the detail box under each table. Per panel, the
newest evidence is the reference point and any row more than an hour behind it is marked OLDER, so
"what is new and what is old" is answerable by looking rather than by subtracting. The resolution
rules live in `tools/status_evidence.py`.

DRIFT IS ON SCREEN (job 2). Every transcribed number in this window is re-checked against the
document it came from on every refresh, and every literal the plan parser depends on is checked
against the plan. That protection used to be invisible -- a drifted row said CHECK-SOURCE in a cell
you had to scroll to. The TOTAL now sits in the top strip, so a silent divergence becomes a visible
one. A panel that could not be checked counts as UNKNOWN, never as zero. Extended 2026-08-16 to the
fidelity banner, which transcribes RELATIONS between numbers rather than literals -- those are
recomputed from the scoring tool every refresh, because a substring search cannot check a relation
and so nothing was checking them at all.

PLAIN LANGUAGE IS A REQUIREMENT, NOT A STYLE. The owner has said twice that jargon makes our
artifacts unusable to them. Nothing on screen says recall@50, CI, hit@1, orthographic or
anchor. It says "the right answer is in our top 50", "spelling only", "the intervals do not
overlap".

THE ONE RULE THAT SHAPES EVERY PANEL: A SCORE IS NEVER SHOWN WITHOUT THE FLOOR IT MUST BEAT.
The whole "we beat scramble" era was a floor error, and right now a baseline that knows
nothing but spelling (8.70%) beats the live system (4.80%). So the score column and the floor
column sit side by side everywhere, and a result that states no floor is marked as stating no
floor. Likewise the results panel shows the losses as loudly as the wins -- a dashboard that
only surfaces good news is worse than none.

DIVISION OF LABOUR. All data collection lives in `tools/status_state.py` (which itself reuses
`inflight_monitor.build_state()`, `tools/board.py`, `tools/autoloop.py` and -- for the three
panels above -- `tools/status_organs.py`, rather than forking a second source of truth). This
file is a renderer and nothing else: it polls on a background thread, hands the result to the Tk
main thread through a queue, and every render is wrapped so that a bad field degrades one panel
instead of freezing the window.

WRITES. Two, both to `notes/BOARD.md`, both only when the owner presses a button, and both
delegated to `tools/board.py` rather than reimplemented -- it does the atomic temp-file-plus-replace
rewrite, preserves hand-added sections verbatim, and round-trips a raw `|` typed into a cell, all
under its own self-test. `Save my answer` -> `board.resolve()`; `File as a new note` ->
`board.ask()` + `board.resolve()`. Nothing else on this path writes anything.

THE ANSWER PANEL, and why it looks over-built (2026-08-16). The owner reported: *"'save my answer'
doesn't do anything and regardless of what question I select the text box doesn't change. Also,
periodically it resets my selected answer to the first one"*, and an answer was lost to it. Three
defects, one shape -- the controls did not describe the state:
  - the box was never rebound on selection, so a draft could be written to the WRONG question and
    nothing on screen said so (the worst of the three: silent, and it corrupts the record);
  - the 20 s refresh rebuilt the table and restored the selection only for QUESTION rows, so any
    other row snapped back to the first one;
  - Save stayed ENABLED over rows it could never write, and with zero open questions -- the live
    state that night -- it could not write at all while still looking live.
Hence: a caption naming the target question, per-question drafts, selection restored by row id for
every kind, a Save that is disabled with a stated reason rather than refusing on press, a
confirmation that quotes what landed and where, and an unconditional destination for typed text.

AND THEN THE FIX WAS ITSELF THE NEXT DEFECT (2026-08-16, second report): *"there is a new ~'save as
a new submission', but save answer is greyed out for all?"* Making Save honest about what it could
write revealed that it could write almost nothing -- the board had ZERO open questions, so all
eleven live rows were a DECISION (D1-D7) or a STANDING item (OP1-OP4), and the panel was correctly,
uselessly, dead everywhere. The decisions are exactly what the owner had been trying to answer.
EVERY ROW IS ANSWERABLE NOW. A QUESTION is still written into its own ANSWER cell; a DECISION or
STANDING answer becomes a NEW board row that names it and repeats its text in full, because
`notes/PLAN.md` and `notes/STATUS.md` are read by code -- `tools/status_plan.py` parses section 9 of
the first, `tools/session_start_hook.py` greps the second for `AS OF:` and `## WHAT IS RUNNING` --
and owner prose must never be typed into a machine-read region. The row carries the whole decision
rather than a bare identifier, because the owner has said twice that bare ids are useless to them:
*"I do not remember what Q7 was."* An answer already recorded is read BACK off the board, so a
decision settled on a phone shows as settled here.
Guarded by `verification/test_board_answer_panel.py` (32 checks) and
`verification/test_board_answerable_all.py` (26), every check of which failed before its fix.

THE RUNNING PANEL, rebuilt 2026-08-16 (*"the current runs have very small fields for me to see
what's currently running"*). Two faults, neither visible in the source and both obvious the moment
the widths were dumped from a rendered window: the table declared 1140 px of columns inside a
~1000 px viewport, so `stretch` had no spare space to give out and NOT ONE COLUMN GREW however large
the window got; and the window asked for 1280x860 on a 1128x752 screen, so its right-hand edge was
never on the display at all. Both are now measured against the live screen. The panel is a
PanedWindow, so the run list can be given room at the expense of its neighbours.
AND IT NO LONGER SHOWS DEAD WORK AS LIVE: the scan can only see processes that EXIST, so a run that
died simply vanished while its `scratch/<name>.pid` file went on asserting it -- 39 of 39 pointed at
nothing on the night this was written, three of them cited as live in agent briefs for hours, one of
them this window's own process. `tools/status_pidclaims.py` checks every claim against the OS and
the panel gives a dead one its own row reading DEAD BUT CLAIMED LIVE. A missing row reads as nothing
to see; a stale RUNNING is read as evidence, which is worse than no panel.
Guarded by `verification/test_status_running_panel.py` (25 checks; 3/21 before).

THE NOTE BOX, ON ITS OWN TAB (*"a box that I can write any commentary I'd like you to look at
during a run without interrupting you... a hook on that that tells you that I've sent something"*;
moved to its own tab 2026-08-17, see "A NOTE FOR ME" above -- it used to sit under the notebook on
every one of the seven other tabs, which the owner separately reported was "too much"). It appends
to `notes/COMMENTARY.md`, and BOTH `tools/session_start_hook.py` and the Stop hook's continuation
path (GUARD 3e) surface anything unread -- the Stop hook being the half that reaches an unattended
overnight run mid-flight. Unread is derived from the file's own contents, never from a flag this
window sets, so a note typed into the markdown from a phone is noticed identically, AND is what
drives the unread count in tab 8's own title -- the unobtrusive indicator that replaces the box
being permanently on screen. Guarded by `verification/test_commentary_channel.py` (20 checks).

Keys: F5 or r = refresh now. Ctrl+1..8 = jump to a panel.

  python tools/status_gui.py --self-test    # renders normal / degraded / garbage states
  python verification/test_board_answer_panel.py     # the answer panel's own witness
  python verification/test_board_answerable_all.py   # every row is answerable
  python verification/test_status_running_panel.py   # widths, resizing, dead-but-claimed-live
  python verification/test_commentary_channel.py     # the note box and both hooks
"""
from __future__ import annotations

import argparse
import json
import queue as _queue
import sys
import threading
import time
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import ttk

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# Repo root, for the RUNNING-tab action buttons (owner request 2026-08-18). Derived from THIS
# file's location, never from the process cwd -- the GUI is launched from a .bat, from a shell,
# and by the harness, and only one of those reliably starts in the repo.
_REPO = Path(__file__).resolve().parent.parent

# ---- THIS WINDOW CAN BE STALE, AND THAT COST THE OWNER FOUR SEPARATE REQUESTS -------------------
# MEASURED 2026-08-20: the owner's GUI process started 2026-08-17 17:50 and was still running three
# days later. Tk loads this file ONCE, at startup, so every feature added since was invisible to
# them -- including the two they then asked for AGAIN, not knowing they already existed:
#   072c18b05 (08-18 07:26)  the overnight ON/OFF buttons  -> re-requested 08-20 12:48
#   d79473ab8 (08-19)        per-tab data age              -> re-requested 08-19 19:44
# and it also explains board Q67, "I still only see the old questions here - d1 d2 etc".
#
# THE POINT IS NOT THE THREE DAYS. It is that a stale window is INDISTINGUISHABLE from a current
# one, so the owner reasonably read "the feature is missing" from "the feature is not on screen".
# This file already carries the rule for exactly this class of fault -- *a stale RUNNING panel is
# read as evidence, which is worse than no panel* -- and the window itself was the one surface not
# holding itself to it.
#
# The mtime is captured AT IMPORT, so it is the version this PROCESS is running, and compared to
# disk on every refresh. No version string to bump and forget: the file's own mtime cannot drift
# out of sync with the file.
try:
    _SRC_MTIME_AT_IMPORT = Path(__file__).resolve().stat().st_mtime
except OSError:                                   # unreadable -> never claim staleness
    _SRC_MTIME_AT_IMPORT = None

import status_state  # noqa: E402  (the collector; this file only renders)
from status_state import _fmt_dur  # noqa: E402

# The evidence-age formatter. Imported for its RENDERING helpers only -- every stamp on every row
# was already resolved by the collector, so this file still computes nothing and remains a renderer.
try:
    import status_evidence as _ev  # noqa: E402
except Exception:  # pragma: no cover - the window must open without it
    _ev = None

# THE OWNER'S SIDE CHANNEL. The only other writer in this file besides the board. Guarded like
# every other import here: if it will not load, the box says so and points at the markdown file,
# which works on its own.
try:
    import commentary as _commentary  # noqa: E402
except Exception as _e:  # pragma: no cover - the window must open without it
    _commentary = None
    _COMMENTARY_ERR = f"{type(_e).__name__}: {_e}"
else:
    _COMMENTARY_ERR = ""

# THE VETTING LEDGER. Guarded like every other import here. If it will not load, the VETTED? column
# says LEDGER UNAVAILABLE rather than falling back to a blank -- a blank is exactly the failure this
# column exists to fix, so degrading into one would be worse than not having the column.
try:
    import vetting_ledger as _ledger  # noqa: E402
except Exception as _e:  # pragma: no cover - the window must open without it
    _ledger = None
    _LEDGER_ERR = f"{type(_e).__name__}: {_e}"
else:
    _LEDGER_ERR = ""


def _vetting(name: str) -> dict:
    """Ledger record for an experiment, with UNVETTED as the answer when nobody has checked it.
    NEVER returns a blank disposition -- see the column comment in `_build_results`."""
    if _ledger is None:
        return {"disposition": "LEDGER UNAVAILABLE", "vetted": False, "verdict": "",
                "finding": "", "narrowing_or_rerun": "", "cell": name}
    try:
        return _ledger.lookup(name or "")
    except Exception:
        return {"disposition": "LEDGER UNAVAILABLE", "vetted": False, "verdict": "",
                "finding": "", "narrowing_or_rerun": "", "cell": name}


# What each disposition means in one plain phrase, and the row colour it earns. UNVETTED is AMBER,
# not neutral: "nobody has checked this" is a warning, not a null state.
_VET_TEXT = {
    "WIRE": ("CHECKED - upheld", "good"),
    "WIRE_NARROWED": ("CHECKED - narrower than claimed", "warn"),
    "RERUN_NAMED": ("CHECKED - cannot be judged yet", "warn"),
    "SHELVED_REFUTED": ("CHECKED - REFUTED, do not cite", "bad"),
    "UNVETTED": ("NOBODY HAS CHECKED IT", "warn"),
    "LEDGER UNAVAILABLE": ("LEDGER UNAVAILABLE", "bad"),
}

REFRESH_MS = 20000        # collection costs ~2.5s; 20s is live enough and stays cheap
TICK_MS = 1000

# ---- DIAGNOSTICS LOG (owner request 2026-08-20: "add some kind of error log or statistics that
# ---- can figure out what's going wrong with the gui - weird things happening and it's hanging")
#
# WHY A LOG AND NOT A GUESS. Two owner reports of freezing were investigated twice with no crash
# output, no hung process and nothing left running -- so there was nothing to diagnose FROM, and
# both times the honest answer was "I cannot tell you why." This file fixes that: every UI stall,
# every collect, and every exception is appended with a duration, so the NEXT report has evidence
# attached instead of a memory of it.
#
# THE ONE RULE IT MUST OBEY: the logger itself can never be the problem. Appending one short JSON
# line is bounded work, it is wrapped so a logging failure cannot raise into the UI, and the file
# is capped -- a diagnostic that fills a disk or blocks a redraw would be worse than no diagnostic.
DIAG_PATH = _REPO / "data" / "hook_state" / "status_gui_diag.jsonl"
DIAG_MAX_BYTES = 4_000_000
UI_STALL_MS = 250         # anything above this on the UI thread is a visible hitch


def _diag(event: str, **fields) -> None:
    """Append one JSON line. Never raises, never blocks on anything but a short write."""
    try:
        rec = {"t": round(time.time(), 3), "event": event}
        rec.update(fields)
        DIAG_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            if DIAG_PATH.exists() and DIAG_PATH.stat().st_size > DIAG_MAX_BYTES:
                # Truncate rather than rotate: this is a rolling diagnostic, not an audit trail,
                # and an unbounded file on the owner's machine is a defect of its own.
                DIAG_PATH.write_text("", encoding="utf-8")
        except OSError:
            pass
        with open(DIAG_PATH, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
    except Exception:
        pass
POLL_WEDGE_S = 60         # collection is internally bounded well below this

# The draft key for text typed while no answerable question is selected. It is a reserved key
# rather than a discard, because that is precisely the text that was lost on 2026-08-16: the board
# had no open question, every selectable row was a DECISION or STANDING item, and the owner's typed
# answer had nowhere to live. It cannot collide with a board id -- board.py mints `Q<n>`.
_UNATTACHED_DRAFT = "\x00unattached"

# --- palette (dark, matched to the terminal; meanings are load-bearing) -----
_BG = "#1e1e1e"
_PANEL = "#252526"
_ALT = "#2d2d30"
_FG = "#e0e0e0"
_DIM = "#8a8f98"
_BORDER = "#3c3c3c"
_HEAD_BG = "#333333"
_SEL_BG = "#264f78"

_RED = "#e5726a"          # below the floor / negative result / critical
_RED_BG = "#5a2320"
_AMBER = "#e0a458"        # unknown, missing, not separated, cannot verify
_AMBER_BG = "#5a4416"
_GREEN = "#5fbf6e"        # above the floor / a real win
_GREEN_BG = "#1f4a21"
_BLUE = "#6fa8d6"         # informational

_STANDING_TEXT = {
    "BELOW_FLOOR": ("LOSING to the floor", _RED),
    "ABOVE_FLOOR": ("beats its floor", _GREEN),
    "LEVEL": ("LEVEL with the floor", _AMBER),
    "UNKNOWN": ("not established", _AMBER),
}
_INSTRUMENT_TEXT = {
    "YES": ("yes", _GREEN),
    "PARTIAL": ("partly", _AMBER),
    "NO": ("NO - CANNOT MEASURE IT ALONE", _RED),
}


def _d(obj) -> dict:
    """Coerce anything to a dict for rendering.

    `x or {}` is NOT enough and the self-test proved it: a truthy non-dict (a string, a list,
    an int) sails past it and then explodes on `.get`. Panels get their payload from a
    collector that is itself defensive, so a wrong TYPE means something upstream is badly
    broken -- which is exactly when the window must stay up and say so."""
    return obj if isinstance(obj, dict) else {}


def _l(obj) -> list:
    """Same idea for anything rendered as a sequence of rows."""
    return obj if isinstance(obj, list) else []


def _verbatim(text: str, n: int = 400) -> str:
    """Quote the owner's own words back at them UNALTERED (only truncated, and visibly so).

    Deliberately NOT `_short`, which strips a leading `exp_` -- harmless on an experiment name and
    dishonest on a confirmation whose entire job is to show exactly what was written."""
    s = (text or "").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return s if len(s) <= n else s[:n] + f" [...{len(s) - n} more characters were also written]"


def _short(name: str, n: int = 46) -> str:
    s = name or "?"
    if s.startswith("exp_"):
        s = s[4:]
    return s if len(s) <= n else s[: n - 3] + "..."


def _gist(text: str, n: int = 70) -> str:
    """A LIST-ROW LABEL, never the reading copy (2026-08-17, third pass on the WAITING ON YOU
    tab). The owner's complaint -- "I can't read any of the question text" -- traced to this
    table stuffing the FULL question/decision text into a Treeview cell. A Treeview cell does not
    wrap; it clips silently at the column's pixel width with no visual sign anything is missing, so
    a 859-character question rendered as an illegible fragment. The full text still belongs, and
    now lives, only in the reading pane (`_show_board_detail`); this cuts at the last whole word
    inside the limit so a label never ends mid-word."""
    s = (text or "").replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return (cut or s[:n]) + "..."


_VOLATILE_AGE_KEYS = {"age_s", "rel", "took_s"}


def _strip_volatile_ages(obj):
    """Recursively drop `age_s`/`rel`/`took_s` from any dict -- see `StatusWindow._board_snapshot`
    for why: `age_s`/`rel` drift with wall-clock time alone regardless of whether the underlying
    artifact changed, and `took_s` (the collector's OWN timing, measured live to differ on every
    call: 0.02 vs 0.05, 0.17 vs 0.25) is noise about the collection itself, not the board. Leaving
    any of them in a change-detection fingerprint makes the fingerprint change on every tick."""
    if isinstance(obj, dict):
        return {k: _strip_volatile_ages(v) for k, v in obj.items() if k not in _VOLATILE_AGE_KEYS}
    if isinstance(obj, list):
        return [_strip_volatile_ages(v) for v in obj]
    return obj


# --- the LAST UPDATED cell, shared by every table --------------------------
#
# ONE FUNCTION, USED EVERYWHERE, so that no panel can quietly render an age differently from its
# neighbours -- and so that the single most important property is enforced in ONE place: what is
# shown is the ARTIFACT's age, and a row with no artifact says UNKNOWN rather than borrowing the
# refresh clock.

def _age_cell(row) -> str:
    st = _d(row).get("evidence_age")
    if not isinstance(st, dict):
        return "UNKNOWN"
    if _ev is not None:
        return _ev.line(st)
    txt = str(st.get("rel") or "UNKNOWN")
    return txt + ("   OLDER" if st.get("behind") else "")


# NOTE ON COLOUR, since its absence is a decision rather than an oversight: an older row is NOT
# recoloured. Being older is not being wrong, and spending the loss colour on age would devalue the
# colour that means a result went the wrong way. The OLDER marker lives in the text of the cell.


def _age_chunks(row, label: str = "WHEN THIS ROW'S EVIDENCE WAS LAST UPDATED") -> list:
    """The detail-box block: relative AND absolute, the artifact, and how it was resolved.

    The cell is deliberately terse and this is where the rest lives -- the owner asked for the
    relative form to read at a glance and for the absolute value to remain available."""
    st = _d(row).get("evidence_age")
    if not isinstance(st, dict):
        return [("\n" + label + "\n", "dim"),
                ("UNKNOWN -- this row carries no provenance at all.\n", "warn")]
    out: list = [("\n" + label + "\n", "dim")]
    if st.get("ts") is None:
        out.append(("UNKNOWN. ", "warn"))
        out.append(str(st.get("detail") or
                       "No artifact could be found for this row, so its age is not known. "
                       "UNKNOWN is shown rather than the time this window refreshed.") + "\n")
        for u in _l(st.get("undated"))[:4]:
            out.append((f"  it names {_d(u).get('raw')} -- {_d(u).get('why')}\n", "mono"))
        return out
    tag = "warn" if st.get("behind") else "good"
    out += [(f"{st.get('rel')}", tag), f"    (exactly: {st.get('when')})\n"]
    out.append((f"from: {st.get('source')}\n", "mono"))
    out.append((f"which is {st.get('kind_plain')}\n", "dim"))
    if st.get("behind") and st.get("behind_text"):
        out.append((f"This is {st.get('behind_text')} the newest evidence on this panel.\n",
                    "warn"))
    weaker = _l(st.get("weaker"))
    if weaker:
        out.append(("it also cites, and these were NOT used because they are weaker evidence: "
                    + ", ".join(str(_d(w).get('path')) for w in weaker[:4]) + "\n", "mono"))
    for u in _l(st.get("undated"))[:3]:
        out.append((f"named but not datable: {_d(u).get('raw')} -- {_d(u).get('why')}\n", "mono"))
    return out


def _panel_age_text(ages, panel_name: str) -> str:
    """The one-line summary a panel header carries: newest, oldest, how many are behind."""
    p = _d(_d(ages).get("panels")).get(panel_name)
    if not isinstance(p, dict):
        return ""
    return "   " + str(p.get("plain") or "")


class StatusWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("hd-instrument -- where we are / what is happening")
        # OPEN AT A SIZE THAT ACTUALLY FITS THE SCREEN (2026-08-16). The window asked for 1280x860
        # unconditionally; this display is 1128x752, so Windows clamped it and the right-hand
        # columns and the bottom of every panel were off the edge. That is half of *"the current
        # runs have very small fields for me to see what's currently running"* -- the table never
        # got the width it was asking for, so no column could ever stretch into space that was not
        # there. The minimum is clamped too, because a minsize LARGER than the screen is a window
        # the owner cannot shrink into view.
        try:
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        except tk.TclError:                        # pragma: no cover - no display
            sw, sh = 1280, 860
        w, h = min(1280, max(700, sw - 60)), min(860, max(500, sh - 80))
        root.geometry(f"{w}x{h}")
        root.minsize(min(980, w), min(620, h))
        # THE COLUMN BUDGET (2026-08-17). Every table below was authored with column widths that
        # summed to 1180-1370 px -- comfortable on a wide monitor, but measured on the owner's
        # actual 1128x752 screen those sums exceed the ~980 px a tab frame has left after the
        # notebook's own padding and the vertical scrollbar. A table whose declared widths already
        # exceed the viewport needs horizontal scrolling NO MATTER what `stretch` is set to --
        # stretch only ever grows columns into space that exists, it does not shrink them into
        # space that doesn't. `_tree()` reads this to scale every table's widths down together, so
        # nothing important on any tab requires a horizontal scrollbar on this screen, and the
        # scaling loosens automatically on a wider one.
        self._col_budget = max(560, w - 90)
        # THE WRAP WIDTH, same problem one level up. Every long label in this window (the headline,
        # every panel's hint line, every colored banner) was given a hardcoded `wraplength` of
        # 1000-1200 px, authored the same way the table columns were -- against a wide monitor.
        # On the owner's actual 1068 px window that number is BIGGER than the window, so Tk never
        # wraps: the text runs past the visible right edge instead, silently, which is worse than a
        # narrow column because there is no scrollbar to reveal what is missing. One shared value,
        # measured off the real window like `_col_budget` above, used everywhere instead of a
        # literal that goes stale the next time this ships to a smaller screen.
        self._wrap_w = max(620, w - 60)
        # A NARROWER wrap width for the few labels that share their row with a fixed-width sibling
        # (the RUNNING NOW tab's status text sits beside a "Copy the command" button in the same
        # grid, so its column's width adds to the button column's regardless of which row the
        # button is actually gridded on). Found the same way as the caption/disarm-box fixes: the
        # widget tree's own `winfo_reqwidth()` still exceeded the window after `_wrap_w` alone.
        self._wrap_w_narrow = max(480, self._wrap_w - 150)

        self._q: _queue.Queue = _queue.Queue()
        self._poll_inflight = False
        self._poll_started: float | None = None
        self._last_ok: float | None = None
        self._last_error: str | None = None
        self._state: dict | None = None
        self._board_rows: list[dict] = []
        # --- the answer panel's state. All four exist because of the 2026-08-16 report that an
        # answer was typed, saved, and lost. See _show_board_detail / _save_answer.
        # _selected_qid    the question Save may write to (None on a row that is not answerable)
        # _selected_row_id the row the owner picked, WHATEVER ITS KIND, so a refresh can put it
        #                  back. Restoring only QUESTION rows is what made the selection snap to
        #                  the first row every 20 s.
        # _answer_for      the question the text CURRENTLY IN THE BOX belongs to. Save refuses if
        #                  this and _selected_qid disagree, so a draft can never be attached to a
        #                  question the owner was not looking at.
        # _drafts          one in-progress answer per question id, so switching rows neither
        #                  carries text across nor throws it away.
        self._selected_qid: str | None = None
        self._selected_row_id: str | None = None
        self._answer_for: str | None = None
        self._drafts: dict[str, str] = {}
        self._board_writable: bool = False
        # The KIND and the full ROW of the selection, because an answer to a DECISION or a STANDING
        # item is filed as a NEW board row that must carry that row's own text inline -- the owner
        # has twice said a bare identifier is useless to them ("I do not remember what Q7 was").
        self._selected_kind: str | None = None
        self._selected_row: dict = {}
        self._board_state: dict = {}
        self._style()
        self._build()

        root.bind("<F5>", lambda _e: self.refresh_now())
        root.bind("r", lambda _e: self.refresh_now())
        for i in range(8):    # 8 tabs since 2026-08-17 (defect 2: NOTE FOR ME got its own tab)
            root.bind(f"<Control-Key-{i + 1}>",
                      lambda _e, k=i: self.nb.select(k))
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        self.refresh_now()
        self._schedule()
        self._tick()
        self.root.after(200, self._pump)

    # ------------------------------------------------------------------
    def _style(self) -> None:
        self.root.configure(bg=_BG)
        st = ttk.Style(self.root)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure(".", background=_PANEL, foreground=_FG,
                     fieldbackground=_PANEL, bordercolor=_BORDER)
        st.configure("TFrame", background=_PANEL)
        st.configure("TLabel", background=_PANEL, foreground=_FG)
        st.configure("TLabelframe", background=_PANEL, foreground=_FG, bordercolor=_BORDER)
        st.configure("TLabelframe.Label", background=_PANEL, foreground=_BLUE)
        st.configure("TButton", background="#3c3c3c", foreground=_FG, bordercolor=_BORDER)
        st.map("TButton", background=[("active", "#4a4a4a")])
        st.configure("TNotebook", background=_BG, bordercolor=_BORDER, tabmargins=(4, 4, 4, 0))
        st.configure("TNotebook.Tab", background="#2b2b2b", foreground=_FG,
                     padding=(14, 7), font=("Segoe UI", 10, "bold"))
        st.map("TNotebook.Tab", background=[("selected", _PANEL)],
               foreground=[("selected", "#ffffff")])
        # ROW FONT AND HEIGHT (2026-08-17 ui/ux pass). Rows had no explicit font -- Tk's system
        # default (~9 px on this machine) -- which is the other half of "very small fields for me
        # to see", the half that widening columns alone does not fix. Bumped one size up, with a
        # taller row to match, so text is not merely wider but genuinely larger.
        st.configure("Treeview", background=_PANEL, foreground=_FG,
                     fieldbackground=_PANEL, bordercolor=_BORDER, rowheight=28,
                     font=("Segoe UI", 10))
        st.map("Treeview", background=[("selected", _SEL_BG)],
               foreground=[("selected", "#ffffff")])
        st.configure("Treeview.Heading", background=_HEAD_BG, foreground="#d4d4d4",
                     relief="flat", font=("Segoe UI", 9, "bold"))
        st.map("Treeview.Heading", background=[("active", _HEAD_BG)])
        st.configure("Vertical.TScrollbar", background="#3c3c3c", troughcolor=_PANEL,
                     bordercolor=_BORDER, arrowcolor=_FG,
                     darkcolor=_PANEL, lightcolor=_PANEL)

    def _tree(self, parent, cols, widths, headings, height=8, minwidths=None, stretch_all=True):
        """A table. `minwidths` and the column-budget fit exist because of two owner reports.

        2026-08-16, *"the current runs have very small fields for me to see what's currently
        running."* Two faults: (1) only columns already >=200 px wide were allowed to stretch, so
        widening the window grew the columns that were ALREADY roomy and left the narrow ones --
        the ones holding the run's identity -- exactly as cramped as before; (2) nothing set a
        MINIMUM, so Tk was free to shrink a column below the width of the text in it. Every column
        now stretches (`stretch_all` is kept as a parameter for callers that pass it explicitly,
        but the fix applies unconditionally -- a table with only some stretchy columns reproduces
        fault (1) the moment a new column is added and someone forgets the threshold); `minwidths`
        puts a floor under each one.

        2026-08-17, the "waiting on you" ui/ux pass: every table's widths were AUTHORED against a
        wide monitor and summed to 1180-1370 px, comfortably wider than the ~980 px a tab has left
        on the owner's actual 1128x752 screen (`self._col_budget`, set once from the real screen
        size in `__init__`). `stretch` only ever grows a column into space that exists; a table
        whose declared widths already exceed the viewport needs a horizontal scrollbar regardless
        of that flag. So when the declared sum exceeds the budget, every width (and minwidth) is
        scaled down together by the same factor, floored so no column collapses to nothing --
        rather than hand-tuning seven call sites to numbers that go stale the next time a column is
        added."""
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tv = ttk.Treeview(frame, columns=cols, show="headings", height=height)
        widths = list(widths)
        mins = list(minwidths) if minwidths else [None] * len(cols)
        budget = getattr(self, "_col_budget", None)
        total = sum(widths)
        if budget and total > budget:
            scale = max(0.45, budget / total)
            widths = [max(40, int(round(wv * scale))) for wv in widths]
            mins = [(max(32, int(round(mv * scale))) if isinstance(mv, (int, float)) else mv)
                    for mv in mins]
        for c, w, h, mn in zip(cols, widths, headings, mins):
            tv.heading(c, text=h)
            tv.column(c, width=w, anchor="w",
                      minwidth=int(mn if mn is not None else min(w, 90)),
                      stretch=True)
        tv.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        tv.tag_configure("even", background=_PANEL)
        tv.tag_configure("odd", background=_ALT)
        tv.tag_configure("bad", foreground=_RED)
        tv.tag_configure("good", foreground=_GREEN)
        tv.tag_configure("warn", foreground=_AMBER)
        tv.tag_configure("dim", foreground=_DIM)
        return frame, tv

    def _detail(self, parent, height=7, font_size=10, heading_font_size=None, spacing=None):
        """`font_size`/`heading_font_size`/`spacing` default to the original values (10/11/none)
        for every caller except the WAITING ON YOU reading pane, which passes larger ones -- see
        `_build_board`. That pane is the PRIMARY CONTENT of its tab (owner: "I can't read any of
        the question text"); the other seven callers are secondary hint/detail boxes and are left
        exactly as they rendered before."""
        heading_font_size = heading_font_size or (font_size + 1)
        t = tk.Text(parent, height=height, wrap="word", bd=0, padx=10, pady=8,
                    bg=_ALT, fg=_FG, insertbackground=_FG, highlightthickness=0,
                    font=("Segoe UI", font_size), state="disabled")
        if spacing:
            s1, s2, s3 = spacing
            t.configure(spacing1=s1, spacing2=s2, spacing3=s3)
        t.tag_configure("h", foreground="#ffffff", font=("Segoe UI", heading_font_size, "bold"))
        t.tag_configure("bad", foreground=_RED, font=("Segoe UI", font_size, "bold"))
        t.tag_configure("good", foreground=_GREEN, font=("Segoe UI", font_size, "bold"))
        t.tag_configure("warn", foreground=_AMBER, font=("Segoe UI", font_size, "bold"))
        t.tag_configure("dim", foreground=_DIM)
        t.tag_configure("mono", font=("Consolas", max(8, font_size - 1)), foreground=_DIM)
        return t

    @staticmethod
    def _set_text(widget: tk.Text, chunks) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for chunk in chunks:
            if isinstance(chunk, tuple):
                widget.insert("end", chunk[0], chunk[1])
            else:
                widget.insert("end", chunk)
        widget.configure(state="disabled")

    # ---- SCROLL + SELECTION ACROSS A REFRESH (2026-08-17, defect 3) -------
    #
    # Owner report: "please fix the bug where on refresh the gui flicks back to the top on every
    # tab." Every table on this window is rebuilt from scratch on every 20s refresh
    # (`tv.delete(*tv.get_children())` then re-insert) because the DATA is re-read from disk each
    # time -- there is no cheap way to diff old rows against new ones for most of these panels. A
    # full rebuild resets a Treeview's scroll position to the top and (on most tables -- see the
    # per-panel calls below) its selection to a hardcoded first row, EVERY 20 SECONDS, which is
    # what "flicks back to the top" actually is. `board_tv` already restored SELECTION by data id
    # (2026-08-16, a harder problem: the SAME owner report also covered losing an in-progress
    # answer); this pair adds the missing half -- SCROLL POSITION -- to every table, board_tv
    # included, without disturbing that existing id-based logic.
    @staticmethod
    def _keep_scroll(tv) -> float:
        """Call BEFORE `tv.delete(*tv.get_children())`. Returns the scrollbar's top fraction."""
        try:
            return tv.yview()[0]
        except tk.TclError:
            return 0.0

    @staticmethod
    def _restore_scroll(tv, frac: float) -> None:
        """Call AFTER the table is fully rebuilt (rows re-inserted, selection restored)."""
        try:
            tv.yview_moveto(frac)
        except tk.TclError:
            pass

    @staticmethod
    def _keep_selection(tv) -> tuple[float, str | None]:
        """For the tables that do NOT already restore selection by a stable data id (unlike
        board_tv) -- captures both the scroll fraction and the selected row's CURRENT iid. Those
        iids are regenerated positionally (`sc0`, `sc1`, ...) on every rebuild from the same
        on-disk source in the same order, so the same iid ends up meaning the same row unless the
        underlying list itself reordered -- strictly better than the previous behaviour of
        unconditionally jumping back to row 0 on every refresh."""
        try:
            frac = tv.yview()[0]
        except tk.TclError:
            frac = 0.0
        sel = tv.selection()
        return frac, (sel[0] if sel else None)

    @staticmethod
    def _restore_selection(tv, kept: tuple[float, str | None], fallback_iid: str | None,
                           select_cb=None) -> None:
        """Put the selection back (previous row if it still exists, else `fallback_iid`, e.g. the
        first row) and then the scroll position, after a table has been fully rebuilt."""
        frac, sel_iid = kept
        try:
            children = tv.get_children()
        except tk.TclError:
            return
        target = sel_iid if (sel_iid and sel_iid in children) else fallback_iid
        if target and target in children:
            try:
                tv.selection_set(target)
                tv.focus(target)
            except tk.TclError:
                pass
            if select_cb:
                select_cb()
        try:
            tv.yview_moveto(frac)
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    def _build(self) -> None:
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        # ---- headline strip: answers "where are we" without clicking anything ----
        head = tk.Frame(root, bg=_RED_BG)
        head.grid(row=0, column=0, sticky="ew")
        head.columnconfigure(0, weight=1)
        # NOTE: tk.Label's own `pady` is a single distance, not a (top, bottom) pair -- a
        # tuple there raises TclError('bad screen distance'). Asymmetric spacing goes on the
        # geometry manager instead.
        # BOTH HEADLINE LABELS WRAP (2026-08-17). Neither had a wraplength, so on a window this
        # narrow the one line the owner sees on every tab without clicking anything -- the score,
        # the floor, the running counts, all pipe-joined onto one line -- ran off the right edge of
        # the window with no scrollbar to reveal the rest. Wrapping onto two or three lines costs a
        # little vertical space; running text invisibly off-screen costs the whole point of a
        # headline strip.
        self.headline_lbl = tk.Label(head, text="loading...", bg=_RED_BG, fg="#ffffff",
                                     font=("Segoe UI", 15, "bold"), anchor="w",
                                     justify="left", padx=14, wraplength=self._wrap_w)
        self.headline_lbl.grid(row=0, column=0, sticky="ew", pady=(9, 2))
        self.headsub_lbl = tk.Label(head, text="", bg=_RED_BG, fg="#f0e6e5",
                                    font=("Segoe UI", 10), anchor="w", justify="left",
                                    padx=14, wraplength=self._wrap_w)
        self.headsub_lbl.grid(row=1, column=0, sticky="ew", pady=(0, 9))

        # "YOU ARE LOOKING AT OLD CODE" -- hidden unless it is true. It lives INSIDE the headline
        # frame (row 2) rather than as a new root row, so the Notebook and the bottom bar keep their
        # existing row indices and no other layout has to move.
        self.stale_lbl = tk.Label(head, text="", bg="#5a2d00", fg="#ffd9a0", anchor="w",
                                  justify="left", padx=14, wraplength=self._wrap_w,
                                  font=("Segoe UI", 11, "bold"))
        self.stale_shown = False
        self.headbar = head

        self.nb = ttk.Notebook(root)
        self.nb.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        # THE ORDER IS THE ANSWER TO "what do I look at first". Group A says where we are and
        # what is happening; group B says what is stuck on the owner; group C is the evidence
        # behind both. Anything that needed two tabs to answer one question was merged.
        self._build_where()       # A
        self._build_running()     # A  (the overnight loop is folded in here)
        self._build_board()       # B  (board questions + the standing decisions)
        self._build_scores()      # C  (the former THE WALLS + PROGRESS MADE, merged)
        self._build_organs()      # C
        self._build_fidelity()    # C
        self._build_results()     # C
        self._build_commentary()  # D  (2026-08-17: its OWN tab -- see docstring below)
        self._register_tab_sources()

        bar = ttk.Frame(root)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        bar.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(bar, text="starting...", anchor="w", foreground=_DIM)
        self.status_lbl.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Refresh (F5)", command=self.refresh_now).grid(row=0, column=1)

    # ---- PER-TAB DATA AGE (owner, 2026-08-19) ---------------------------
    # "add an 'updated' timestamp on each tab so I know when the data is new or not".
    #
    # THE AGE GOES IN THE TAB TITLE, and that is a deliberate choice rather than a shortcut.
    # A strip inside each panel would show the age only of the tab you are already looking at,
    # and would need a new grid row inserted into eight existing layouts. In the title it is
    # visible for EVERY tab at once, without clicking through -- which is what "so I know when
    # the data is new" actually asks for.
    #
    # IT IS THE AGE OF THE EVIDENCE, NOT OF THE REFRESH. The bottom bar already carries the
    # refresh clock and says in so many words that it is "the REFRESH, not the age of anything
    # on screen". This fills exactly the gap that sentence admits to: each title shows how long
    # ago the FILE that tab is rendered from last changed. A tab reading live process state says
    # `live`, because there is no file whose mtime would mean anything.
    _TAB_SOURCES = {
        "1. WHERE WE ARE": ["notes/BUILD_PLAN_post_audit_2026-08-19.md", "notes/STATUS.md",
                            "notes/LONG_TERM_PLAN.md"],
        "2. RUNNING": None,                       # live process/queue state
        "3. WAITING ON YOU": ["notes/BOARD.md"],
        "4. SCORES": ["notes/STATUS.md", "notes/VETTING_LEDGER.md"],
        "5. ORGAN MAP": ["notes/ORGAN_MAP.md"],
        "6. COPYING THE BRAIN": ["notes/ORGAN_MAP.md"],
        "7. LATEST RESULTS": None,                # newest metrics.json, computed at render
        "8. NOTE FOR ME": ["notes/COMMENTARY.md"],
    }

    def _register_tab_sources(self) -> None:
        """Remember each tab's BASE title so the age suffix can be re-applied without accreting."""
        self._tab_base = {}
        # What each tab's title currently READS, so the 1-second tick can skip the re-title when
        # nothing changed (owner: "the tabs keep changing slightly with every update").
        self._tab_text_now = {}
        for tab_id in self.nb.tabs():
            self._tab_base[tab_id] = self.nb.tab(tab_id, "text")

    @staticmethod
    def _fmt_age(seconds: float) -> str:
        # NO SECOND-BY-SECOND PRECISION IN A TAB TITLE. This value goes into the tab strip, and a
        # string that changes every second makes the strip twitch every second even with the
        # only-when-changed guard above -- which is exactly what the owner reported. Under a minute
        # the honest and stable answer is "just now"; nobody needs a tab title accurate to 1s.
        if seconds < 60:
            return "just now"
        if seconds < 90:
            return "1m"
        if seconds < 5400:
            return "%dm" % int(seconds // 60)
        if seconds < 172800:
            return "%dh" % int(seconds // 3600)
        return "%dd" % int(seconds // 86400)

    def _newest_metrics_mtime(self) -> float | None:
        """Newest metrics.json under data/. Cached for 60 s -- this walks a large tree and the
        GUI refreshes far more often than results land."""
        now = time.time()
        cached = getattr(self, "_metrics_mtime_cache", None)
        if cached is not None and (now - cached[0]) < 60:
            return cached[1]

        # *** THIS WALK USED TO RUN ON THE UI THREAD AND IT IS THE MEASURED FREEZE. ***
        # Measured 2026-08-20 on the owner's own data/: **8,155 directories, 6.91 SECONDS**, with a
        # stat() per directory -- executed from `_update_tab_ages`, which the 1-second tick calls.
        # So once a minute the window went completely unresponsive for ~7s, and on a cold cache far
        # longer (a plain shell glob over the sibling experiments/ tree timed out at 120s the same
        # day). That is the owner's *"it's hanging a lot"*, and the docstring's "cached for 60s"
        # was doing its job -- the defect was never the FREQUENCY, it was that the work was on the
        # thread that draws.
        #
        # NOW: kick the rescan into a daemon thread and return the PREVIOUS value immediately. A
        # tab-title timestamp that is one refresh stale is invisible; a 7-second freeze is not.
        if not getattr(self, "_metrics_scan_running", False):
            self._metrics_scan_running = True

            def _scan():
                t0 = time.time()
                newest, n = None, 0
                try:
                    for d in (_REPO / "data").iterdir():
                        if not d.is_dir():
                            continue
                        n += 1
                        try:
                            m = (d / "metrics.json").stat().st_mtime
                        except OSError:
                            continue
                        if newest is None or m > newest:
                            newest = m
                except OSError:
                    newest = None
                self._metrics_mtime_cache = (time.time(), newest)
                self._metrics_scan_running = False
                _diag("metrics_scan", ms=round(1000 * (time.time() - t0)), dirs=n)

            threading.Thread(target=_scan, daemon=True).start()
        # Whatever we had last (None on the very first call, which renders as "[--]").
        return cached[1] if cached else None

    def _src_mtime_cached(self, key, srcs):
        """Newest mtime across `srcs`, cached 10s and refreshed OFF the drawing thread.

        Returns the previous value immediately -- None on the very first call, which renders as
        "[--]" for one tick. Never does file I/O on the caller's thread.
        """
        now = time.time()
        cache = getattr(self, "_src_mtime_cache", None)
        if cache is None:
            cache = self._src_mtime_cache = {}
        hit = cache.get(key)
        if hit is not None and (now - hit[0]) < 10.0:
            return hit[1]
        running = getattr(self, "_src_scan_running", None)
        if running is None:
            running = self._src_scan_running = set()
        if key not in running:
            running.add(key)

            def _scan():
                t0 = time.time()
                newest = None
                for rel in srcs:
                    try:
                        mt = (_REPO / rel).stat().st_mtime
                    except OSError:
                        continue
                    if newest is None or mt > newest:
                        newest = mt
                cache[key] = (time.time(), newest)
                running.discard(key)
                ms = 1000 * (time.time() - t0)
                if ms > UI_STALL_MS:
                    _diag("src_mtime_scan_slow", key=str(key), ms=round(ms), n=len(srcs))

            threading.Thread(target=_scan, daemon=True).start()
        return hit[1] if hit else None

    def _update_tab_ages(self) -> None:
        """Re-title every tab with the age of the evidence behind it. Never raises: a dashboard
        that dies while decorating itself is worse than one with no timestamps."""
        try:
            now = time.time()
            for tab_id in self.nb.tabs():
                base = self._tab_base.get(tab_id)
                if not base:
                    continue
                srcs = self._TAB_SOURCES.get(base, None)
                if base == "7. LATEST RESULTS":
                    m = self._newest_metrics_mtime()
                    suffix = ("  [%s]" % self._fmt_age(now - m)) if m else "  [--]"
                elif srcs is None:
                    suffix = "  [live]"
                else:
                    # *** STILL ON-THREAD I/O, AND THE DIAGNOSTICS LOG CAUGHT IT. ***
                    # After moving the data/ walk off-thread the worst UI stall fell 6,910ms ->
                    # 700ms, but `ui_stall` records kept arriving with `tab_ages_ms: 597`. These
                    # `stat()` calls are the remainder: individually trivial (measured 0.7ms for 40
                    # of them on an idle disk) but they BLOCK under I/O contention, and this window
                    # runs while the machine is doing heavy corpus reads -- the same contention
                    # pushed the off-thread data/ scan from 5.4s to 121.6s.
                    # Cached for 10s and refreshed off-thread, same pattern as the metrics scan.
                    # A tab-title age that is up to 10s stale is invisible; a 600ms hitch is not.
                    newest = self._src_mtime_cached(base, srcs)
                    suffix = ("  [%s]" % self._fmt_age(now - newest)) if newest else "  [--]"
                # *** ONLY RE-TITLE WHEN THE TEXT ACTUALLY CHANGES. ***
                # Owner 2026-08-20: *"the tabs keep changing slightly with every update"*. This
                # loop ran every TICK_MS (1 second) and unconditionally called `nb.tab(text=...)`
                # on all eight tabs. Each call re-measures the tab label and re-lays out the whole
                # Notebook, so the tab strip visibly shifted once a second as an age string grew a
                # character ("9s" -> "10s"). Comparing first makes the common case a no-op.
                want = base + suffix
                if self._tab_text_now.get(tab_id) != want:
                    self._tab_text_now[tab_id] = want
                    self.nb.tab(tab_id, text=want)
        except Exception as exc:
            _diag("tab_ages_error", err=f"{type(exc).__name__}: {exc}")

    # ---- the side channel: its OWN tab (2026-08-17, defect 2) -----------
    def _build_commentary(self) -> None:
        """A box for anything the owner wants looked at, without interrupting a run.

        Owner, 2026-08-16: *"a box that I can write any commentary I'd like you to look at during a
        run without interrupting you... a hook on that that tells you that I've sent something to
        look at during a computational run."*

        MOVED TO ITS OWN TAB (2026-08-17, defect 2). It used to sit under the notebook, present on
        every one of the seven other panels, on the reasoning that a note is written while looking
        at whatever the owner was already looking at, so it should not need a tab of its own.
        Owner, retesting: *"the 'note for me' section takes a whole section of every tab is too
        much - should be a separate tab only."* That reasoning was wrong in practice: a fixed-height
        box repeated on every single tab is a permanent tax on the seven tabs that are NOT this one,
        and (see the DEFECT 1 fix on the WAITING ON YOU tab, in `_build_board` above) permanently
        reserving vertical space for a widget most tabs never use is exactly the kind of fixed cost
        that starves the content that DOES vary. So: one dedicated tab, and the UNOBTRUSIVE
        INDICATOR that replaces "always visible" is the tab's own title, updated every refresh by
        `_r_commentary()` to name how many notes are unread -- `tools/commentary.py` already tracks
        that from the file's own contents (see COUPLING below), so this is a read, not a new flag.

        THE CONFIRMATION QUOTES THE TEXT AND NAMES THE FILE. That is not politeness: the Save
        button on the WAITING ON YOU panel failed silently for hours and the owner had no way to
        tell, and the whole value of this channel is the owner's confidence that the note landed.
        So a success echoes what was written and where, and a failure says the write did not happen
        and leaves the text in the box.

        A SHORT READ-ONLY HISTORY sits above the box (newest first, `tools/commentary.py load()`),
        so the tab is not just a box the owner types into blind -- they can see what was already
        sent and whether it is marked read yet.

        IT IS NOT THE ONLY WAY IN. `notes/COMMENTARY.md` is a plain markdown file; typing into it
        from a phone works identically, because unread is derived from the file's contents rather
        than from a flag this window sets."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="8. NOTE FOR ME")
        self.tab_commentary = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        tk.Label(f, text="A NOTE FOR ME -- write anything here; it does not interrupt whatever "
                         "is running, and I am told about it at the end of this turn (even "
                         "mid-run) and again at my next start.", bg=_PANEL, fg=_BLUE,
                 font=("Segoe UI", 10), anchor="w", justify="left",
                 wraplength=self._wrap_w, padx=4, pady=6).grid(row=0, column=0, sticky="ew")

        self.commentary_history = self._detail(f, height=10)
        self.commentary_history.grid(row=1, column=0, sticky="nsew", pady=(0, 6))

        wrap = ttk.LabelFrame(f, text="WRITE A NEW NOTE")
        wrap.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 4))
        wrap.columnconfigure(0, weight=1)
        self.commentary_frame = wrap
        self.commentary_box = tk.Text(wrap, height=3, wrap="word", bd=0, padx=8, pady=5,
                                      bg="#1b1b1b", fg=_FG, insertbackground=_FG,
                                      highlightthickness=1, highlightbackground=_BORDER,
                                      font=("Segoe UI", 11))
        self.commentary_box.grid(row=0, column=0, sticky="ew", padx=6, pady=5)
        btns = ttk.Frame(wrap)
        btns.grid(row=0, column=1, sticky="ns", padx=(0, 6))
        self.commentary_btn = ttk.Button(btns, text="Send it to me", command=self._send_commentary)
        self.commentary_btn.grid(row=0, column=0, sticky="ew", pady=(5, 3))
        ttk.Button(btns, text="Clear", command=lambda: self.commentary_box.delete(
            "1.0", "end")).grid(row=1, column=0, sticky="ew")
        self.commentary_status = tk.Label(wrap, text="", bg=_PANEL, fg=_DIM, anchor="w",
                                          font=("Segoe UI", 9), wraplength=self._wrap_w, justify="left")
        self.commentary_status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8,
                                    pady=(0, 5))

    # ---- render: commentary tab title + history (2026-08-17, defect 2) -----
    def _r_commentary(self, s: dict) -> None:
        """Cheap (commentary.py's own self-test: <0.05ms/call), so it runs every refresh cycle
        like every other panel. The unread count IS the "unobtrusive indicator elsewhere" that
        replaces the box being permanently visible on every tab."""
        if _commentary is None:
            self.nb.tab(self.tab_commentary, text="8. NOTE FOR ME")
            self._set_text(self.commentary_history, [
                (f"tools/commentary.py could not be loaded ({_COMMENTARY_ERR}).\n", "warn"),
                "You can still type into notes/COMMENTARY.md directly."])
            return
        try:
            entries = _commentary.load()
            n_unread = _commentary.count_unread()
        except Exception as exc:
            self.nb.tab(self.tab_commentary, text="8. NOTE FOR ME")
            self._set_text(self.commentary_history,
                           [(f"could not read notes/COMMENTARY.md ({type(exc).__name__}: {exc})\n",
                             "warn")])
            return
        try:
            self.nb.tab(self.tab_commentary,
                        text=(f"8. NOTE FOR ME ({n_unread} unread)" if n_unread
                              else "8. NOTE FOR ME"))
        except tk.TclError:
            pass
        if not entries:
            self._set_text(self.commentary_history,
                           [("No notes yet. Anything you type below is appended to "
                             "notes/COMMENTARY.md and read at the end of this turn.\n", "dim")])
            return
        chunks: list = []
        for e in reversed(entries[-12:]):
            when = e.get("stamp") or "no timestamp (typed by hand)"
            src = f"  ({e['source']})" if e.get("source") else ""
            chunks.append((f"{when}{src}\n", "h"))
            chunks.append(f"{e.get('body', '')}\n\n")
        if len(entries) > 12:
            chunks.append((f"... and {len(entries) - 12} older note(s) in notes/COMMENTARY.md\n",
                          "dim"))
        self._set_text(self.commentary_history, chunks)

    def _send_commentary(self) -> None:
        """Append the box to notes/COMMENTARY.md and SAY, on screen, exactly what landed where."""
        text = self.commentary_box.get("1.0", "end").strip()
        if not text:
            self.commentary_status.configure(
                text="NOT SENT: the box is empty, so there is nothing to record.", fg=_AMBER)
            return
        if _commentary is None:
            self.commentary_status.configure(
                text=f"NOT SENT: tools/commentary.py could not be loaded ({_COMMENTARY_ERR}). "
                     f"Your text is still in the box -- you can paste it into "
                     f"notes/COMMENTARY.md directly and it will be picked up.", fg=_RED)
            return
        try:
            e = _commentary.add(text, source="the status window")
        except Exception as exc:
            self.commentary_status.configure(
                text=f"NOT SENT ({type(exc).__name__}: {exc}). Your text is still in the box.",
                fg=_RED)
            return
        self.commentary_status.configure(
            text=(f"SENT at {e['stamp']}. Written to notes/COMMENTARY.md ({e['path']}): "
                  f"\"{_verbatim(text)}\"   I am told about it at the end of the current turn, "
                  f"even mid-run, and again at my next start."), fg=_GREEN)
        self.commentary_box.delete("1.0", "end")

    # ---- TAB 1 (group A) ----------------------------------------------
    def _build_where(self) -> None:
        """WHERE WE ARE. The plan, rendered from the plan file, on every refresh.

        Nothing in this panel is a stored copy of a sentence that exists in
        notes/LONG_TERM_PLAN.md. A cell whose label is absent from the plan says NOT STATED IN THE
        PLAN and is counted in the contract strip at the top, which is the difference between a
        panel that goes quietly wrong and one that tells you it has."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="1. WHERE WE ARE")
        self.tab_where = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        now = tk.Frame(f, bg=_GREEN_BG)
        now.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        now.columnconfigure(0, weight=1)
        self.where_phase = tk.Label(now, text="", bg=_GREEN_BG, fg="#ffffff",
                                    font=("Segoe UI", 14, "bold"), anchor="w", padx=12,
                                    justify="left", wraplength=self._wrap_w)
        self.where_phase.grid(row=0, column=0, sticky="ew", pady=(9, 2))
        self.where_next = tk.Label(now, text="", bg=_GREEN_BG, fg="#e8f4e9",
                                   font=("Segoe UI", 11), anchor="w", justify="left",
                                   padx=12, wraplength=self._wrap_w)
        self.where_next.grid(row=1, column=0, sticky="ew", pady=(0, 9))

        self.where_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                   anchor="w", justify="left", wraplength=self._wrap_w, padx=4, pady=4)
        self.where_hint.grid(row=1, column=0, sticky="ew")

        frame, self.where_tv = self._tree(
            f,
            cols=("phase", "state", "goal", "gate", "stop", "updated"),
            widths=(230, 140, 280, 300, 260, 160),
            headings=("PHASE", "WHERE IT IS", "WHAT IT IS FOR",
                      "WHAT WOULD COUNT AS SUCCESS", "WHAT WOULD MAKE US STOP",
                      "EVIDENCE LAST UPDATED"),
            height=8)
        frame.grid(row=2, column=0, sticky="nsew")
        self.where_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_where_detail())

        self.where_detail = self._detail(f, height=13)
        self.where_detail.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    # ---- TAB 4 (group C) ----------------------------------------------
    def _build_scores(self) -> None:
        """SCORES AND FLOORS -- the former THE WALLS and PROGRESS MADE, merged into one row per
        part. Both load-bearing rules are preserved and are checked at the RENDERED CELL by the
        self-test: no score without its floor, and retractions as loud as any loss."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="4. SCORES")
        self.tab_scores = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        gov = tk.Frame(f, bg=_RED_BG)
        gov.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        gov.columnconfigure(0, weight=1)
        self.sc_gov_title = tk.Label(gov, text="", bg=_RED_BG, fg="#ffffff",
                                     font=("Segoe UI", 12, "bold"), anchor="w", padx=12,
                                     justify="left", wraplength=self._wrap_w)
        self.sc_gov_title.grid(row=0, column=0, sticky="ew", pady=(8, 2))
        self.sc_gov_body = tk.Label(gov, text="", bg=_RED_BG, fg="#f4e9e8",
                                    font=("Segoe UI", 10), anchor="w", justify="left",
                                    padx=12, wraplength=self._wrap_w)
        self.sc_gov_body.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.sc_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                anchor="w", justify="left", wraplength=self._wrap_w, padx=4, pady=4)
        self.sc_hint.grid(row=1, column=0, sticky="ew")

        frame, self.sc_tv = self._tree(
            f,
            cols=("what", "alone", "before", "now", "dir", "updated"),
            widths=(270, 150, 250, 270, 200, 160),
            headings=("PART OF THE MACHINE", "CAN WE MEASURE IT ALONE?",
                      "WHAT IT WAS  (and its floor)", "WHAT IT IS NOW  (and its floor)",
                      "WHERE THAT LEAVES US", "EVIDENCE LAST UPDATED"),
            height=16)
        frame.grid(row=2, column=0, sticky="nsew")
        self.sc_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_score_detail())

        self.sc_detail = self._detail(f, height=11)
        self.sc_detail.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    # ---- PANEL B ------------------------------------------------------
    def _build_organs(self) -> None:
        """THE BRAIN ORGAN MAP. Per organ: the brain structure, what it does in one plain
        sentence, whether we built it, whether it is switched on, and what it measures."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="5. ORGAN MAP")
        self.tab_organs = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        self.organ_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                   anchor="w", justify="left", wraplength=self._wrap_w, padx=4, pady=6)
        self.organ_hint.grid(row=0, column=0, sticky="ew")

        frame, self.organ_tv = self._tree(
            f,
            cols=("organ", "brain", "built", "state", "measured", "updated"),
            widths=(280, 260, 80, 190, 250, 160),
            headings=("ORGAN (plain name)", "THE PART OF THE BRAIN", "BUILT?",
                      "IS IT SWITCHED ON?", "WHAT IT MEASURES", "EVIDENCE LAST UPDATED"),
            height=15)
        frame.grid(row=1, column=0, sticky="nsew")
        self.organ_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_organ_detail())

        self.organ_detail = self._detail(f, height=12)
        self.organ_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

    # ---- PANEL C ------------------------------------------------------
    def _build_fidelity(self) -> None:
        """HOW CLOSELY WE COPY THE BRAIN -- with the banner the owner corrected on 2026-08-16.

        WHAT CHANGED AND WHY. This panel used to say the fidelity score *"has NOT been shown to
        predict"* how well anything works, and headed its detail box *"WHY THIS NUMBER MUST NOT BE
        READ AS A PREDICTION"*. Both were unscoped, and read together they assert a general negative
        that six points with one positive cannot support. The owner's correction is the better
        argument and it is now what the panel says: TOO LITTLE EVIDENCE TO TELL IS NOT THE SAME
        STATEMENT AS NO RELATIONSHIP, and a handful of points inside a low-fidelity range is exactly
        where a real relationship would be hardest to detect.

        WHAT DID NOT CHANGE, because it is true and it stops a real failure: a fidelity score may
        not be used today as evidence that something works. The two named misses stay on screen as
        the honest counter-evidence, presented as what they are -- two points, not a refutation.

        AND THE PREMISE IS SHOWN RATHER THAN ASSERTED. The scatter and the range line are here
        because the owner asked to see the band for themselves. Six points visible beats any
        adjective, including any adjective this window might have chosen for them."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="6. COPYING THE BRAIN")
        self.tab_fidelity = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(4, weight=1)
        f.rowconfigure(6, weight=1)

        warn = tk.Frame(f, bg=_AMBER_BG)
        warn.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        warn.columnconfigure(0, weight=1)
        self.fid_head = tk.Label(
            warn, text="UNVALIDATED AS A PREDICTOR AT OUR CURRENT LOW FIDELITY.",
            bg=_AMBER_BG, fg="#ffffff", font=("Segoe UI", 12, "bold"), anchor="w",
            justify="left", padx=12, wraplength=self._wrap_w)
        self.fid_head.grid(row=0, column=0, sticky="ew", pady=(8, 2))
        self.fid_warn = tk.Label(warn, text="", bg=_AMBER_BG, fg="#f7ecd8",
                                 font=("Segoe UI", 10), anchor="w", justify="left",
                                 padx=12, wraplength=self._wrap_w)
        self.fid_warn.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # THE SCATTER. Every scored point, with its n, on the two axes that matter: how closely it
        # copies the brain, and whether the result actually held. It is drawn rather than described
        # because the owner asked to see the band, and because a picture of six points makes the
        # power problem self-evident in a way no sentence does.
        self.fid_canvas = tk.Canvas(f, height=178, bg=_ALT, highlightthickness=0, bd=0)
        self.fid_canvas.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        self.fid_canvas.bind("<Configure>", lambda _e: self._draw_scatter())
        self.fid_scatter_cap = tk.Label(f, text="", bg=_PANEL, fg=_DIM,
                                        font=("Segoe UI", 9), anchor="w", justify="left",
                                        wraplength=self._wrap_w, padx=4)
        self.fid_scatter_cap.grid(row=2, column=0, sticky="ew", pady=(0, 4))

        tk.Label(f, text="WHAT WE SCORED, AND WHAT ACTUALLY HAPPENED TO IT",
                 bg=_PANEL, fg=_BLUE, anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=3, column=0, sticky="ew", pady=(2, 2))
        frame, self.fid_tv = self._tree(
            f, cols=("thing", "pct", "outcome", "updated"),
            widths=(330, 180, 520, 150),
            headings=("WHAT WAS SCORED", "HOW CLOSELY WE COPY THE BRAIN",
                      "WHAT ACTUALLY HAPPENED WHEN IT WAS MEASURED",
                      "EVIDENCE LAST UPDATED"),
            height=7)
        frame.grid(row=4, column=0, sticky="nsew")
        self.fid_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_fidelity_detail())

        tk.Label(f, text="WHERE OURS DIVERGES FROM THE BIOLOGY, ORGAN BY ORGAN",
                 bg=_PANEL, fg=_BLUE, anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=5, column=0, sticky="ew", pady=(8, 2))
        frame2, self.fid_div_tv = self._tree(
            f, cols=("organ", "shape", "position", "metric", "pinned", "updated"),
            widths=(340, 160, 170, 180, 190, 140),
            headings=("ORGAN", "IS IT THE SAME OPERATION?", "IS IT IN THE RIGHT PLACE?",
                      "IS IT JUDGED THE BRAIN'S WAY?", "DOES THE SCIENCE PIN THIS DOWN?",
                      "LAST UPDATED"),
            height=8)
        frame2.grid(row=6, column=0, sticky="nsew")
        self.fid_div_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_fidelity_detail(True))

        self.fid_detail = self._detail(f, height=9)
        self.fid_detail.grid(row=7, column=0, sticky="ew", pady=(6, 0))

    def _draw_scatter(self) -> None:
        """Fidelity against outcome, one dot per scored point, with n stated on the chart.

        NOTHING IS INVENTED ON THIS CHART. The points come from the collector's `scatter` block,
        which is the same `rows` the table above shows, re-shaped. A point with no score is left
        OFF and COUNTED in the caption -- plotting it at zero would put a number on the chart that
        nobody measured, which is the failure this whole panel exists to prevent."""
        c = getattr(self, "fid_canvas", None)
        if c is None:
            return
        try:
            c.delete("all")
            w = max(int(c.winfo_width()), 400)
            h = max(int(c.winfo_height()), 120)
        except tk.TclError:
            return
        sc = _d(_d(getattr(self, "_fid_state", None)).get("scatter"))
        pts = [_d(p) for p in _l(sc.get("points"))]
        left, right, top, bot = 190, w - 30, 34, h - 34
        if right <= left + 40:
            return

        # axes
        c.create_line(left, bot, right, bot, fill=_BORDER)
        c.create_line(left, top, left, bot, fill=_BORDER)
        c.create_text(left, 14, text="EVERY POINT WE HAVE, PLOTTED", anchor="w",
                      fill=_FG, font=("Segoe UI", 9, "bold"))
        c.create_text(right, 14, text=f"n = {sc.get('n', 0)}", anchor="e", fill=_AMBER,
                      font=("Segoe UI", 10, "bold"))
        c.create_text((left + right) // 2, h - 12,
                      text=str(sc.get("x_label") or "how closely it copies the brain"),
                      fill=_DIM, font=("Segoe UI", 9))
        for frac, lab in ((0.0, "0%"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1.0, "100%")):
            x = left + (right - left) * frac
            c.create_line(x, bot, x, bot + 4, fill=_BORDER)
            c.create_text(x, bot + 14, text=lab, fill=_DIM, font=("Segoe UI", 8))

        y_hold, y_fail = top + 26, bot - 30
        c.create_text(left - 10, y_hold, text="the result HELD", anchor="e", fill=_GREEN,
                      font=("Segoe UI", 9, "bold"))
        c.create_text(left - 10, y_fail, text="it did NOT hold", anchor="e", fill=_RED,
                      font=("Segoe UI", 9, "bold"))
        if not pts:
            c.create_text((left + right) // 2, (top + bot) // 2,
                          text="NO SCORED POINTS -- nothing to plot", fill=_AMBER,
                          font=("Segoe UI", 11, "bold"))
            return

        # A tiny horizontal jitter for exact ties, so two points at the same score do not hide each
        # other. It is applied to the DRAWING only and is disclosed in the caption -- the flat bag
        # and the conjunctive arm genuinely tie, and a chart that showed five dots for six points
        # would be lying about the sample size.
        seen: dict[tuple, int] = {}
        for p in pts:
            pct = p.get("pct")
            if not isinstance(pct, (int, float)):
                continue
            held = bool(p.get("held"))
            key = (round(pct, 4), held)
            k = seen.get(key, 0)
            seen[key] = k + 1
            x = left + (right - left) * max(0.0, min(1.0, float(pct))) + (k * 13)
            y = y_hold if held else y_fail
            col = _GREEN if held else _RED
            c.create_oval(x - 6, y - 6, x + 6, y + 6, fill=col, outline="#ffffff", width=1)
            name = str(p.get("component") or "")
            name = name.split("_", 1)[1] if (name[:2].isalpha() is False and "_" in name) else name
            c.create_text(x, y + (-18 if held else 18), text=_short(name, 26)[:26],
                          fill=_FG, font=("Segoe UI", 8))

    def _r_scatter_caption(self, fd: dict) -> None:
        sc = _d(fd.get("scatter"))
        fr = _d(fd.get("framing"))
        bits = [str(sc.get("caption") or "")]
        if sc.get("n_unscored"):
            bits.append(f"{sc.get('n_unscored')} scored nothing at all and is therefore NOT on "
                        f"the chart rather than being drawn at zero.")
        bits.append("Points that tie exactly are nudged sideways so six points show as six dots.")
        if fr.get("range_text"):
            bits.append(str(fr.get("range_text")))
        self.fid_scatter_cap.configure(text="  ".join(b for b in bits if b))

    # ---- TAB 3 (group B) ----------------------------------------------
    def _build_board(self) -> None:
        """WAITING ON YOU -- everything stuck on a decision, in one place.

        THREE KINDS IN ONE TABLE, and the kind column matters because only one of them is
        answerable here:
          QUESTION  a notes/BOARD.md row. Typing below writes straight into it.
          DECISION  a D-numbered decision parsed live out of notes/PLAN.md section 9. Each has a
                    recommended default, so SILENCE IS NOT NEUTRAL -- the default is what happens.
          STANDING  a decision recorded in running prose in the status documents, transcribed with
                    its numbers re-checked against the source on every refresh.
        Before this merge the last two appeared in no panel at all and the owner had to read three
        documents to find out what was waiting on them.

        THE LAYOUT WAS THE REAL DEFECT (2026-08-17, SECOND REPORT). The 2026-08-17 placeholder-row
        fix above was real, but the owner re-tested and reported the SAME thing again: "the
        'waiting on me' tab... does NOT have an ability for me to select different questions."
        Measured live against this window's own StatusWindow -- not guessed, not inferred from a
        self-test that only ever calls `.render()` on a payload and never checks a real widget's
        allocated pixels -- with `f.winfo_reqheight()` at 924 against an actual `f.winfo_height()`
        of 318 on the owner's real ~1128x752 screen: this tab's banner + hint + table + detail box
        + answer box together REQUEST ~600px more height than the tab is ever given. Only the
        table's grid row carried `weight=1`; every sibling (the detail box, the answer box) was a
        FIXED-size row that Tk's grid geometry manager honours in full BEFORE handing whatever is
        left to the one weighted row. With a 600px deficit, that left the table -- the one thing
        the owner needs to see and click between rows -- measured at a literal 1x1 PIXELS, and
        pushed the answer box (Save, the text box, the caption) 73px past the bottom edge of the
        window: present in the widget tree, entirely unreachable, no scrollbar reaches it. Nothing
        was wrong with the ROWS (both Q16 and Q17 were always present and correctly selectable in
        the data) or the CLICK HANDLER -- there was simply nothing on screen to click. This is why
        the previous fix (which was a genuine, separate defect: a placeholder row that faked a
        QUESTION so the owner never even reached real rows) did not resolve the report: it fixed
        the DATA, not the LAYOUT that was hiding it. Fixed here the same way the RUNNING NOW tab's
        cramped-columns defect was fixed below: a PanedWindow with a `minsize` floor under every
        pane, so no pane can ever again be crushed to nothing, and the owner can drag a sash to
        give any one of them more room."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="3. WAITING ON YOU")
        self.tab_board = f
        f.columnconfigure(0, weight=1)
        # THE READING PANE GETS THE MAJORITY OF THE VERTICAL SPACE (2026-08-17, THIRD PASS). Row 4
        # (the detail/reading pane) is the ONLY row with weight -- every other row (banner, hint,
        # new-data hint, table, answer box) is a plain fixed-height grid row. This replaces the
        # PanedWindow the second pass used for table+detail: that mechanism was measured TWICE to
        # mis-size its panes (an earlier pane's request/minsize satisfied before a later one's, an
        # explicit `sash_place()` call measured to have no effect at all) and STILL left the owner
        # unable to read -- a PanedWindow negotiates space by each pane's own request, and the
        # table's request (height=12 rows =~ 356px) was consuming nearly the whole budget on the
        # owner's screen regardless of any minsize floor set on the detail pane. A fixed-height
        # table plus one weighted row is deterministic: the table gets exactly what its declared
        # row count needs (now a compact 6, shrunk from 12 -- the STANDARD below says the table
        # carries short labels, not full text, so it does not need to show every row at once; the
        # scrollbar reaches the rest), and QUESTION TEXT -- THE PRIMARY CONTENT OF THIS TAB -- gets
        # everything left over, not whatever a heuristic decided to spare it.
        self._board_table_row = 3
        self._board_detail_row = 4
        f.rowconfigure(self._board_detail_row, weight=1)

        # THE COUNT BANNER (2026-08-17, fixing the owner report *"the questions tab now only
        # appears to have one question, and no way for me to select a new one"*). What was
        # actually happening: BOARD.md had zero OPEN QUESTIONS that night, so this tab drew exactly
        # one tree row literally labelled QUESTION -- a placeholder reading "No open question", not
        # selectable, not answerable, id "-". The eleven real, answerable DECISION and STANDING
        # rows were there too, but nothing on screen said "there are 11 more things below, and they
        # count as things to answer even though they are not called questions" -- so a reader
        # scanning for "questions" found the one placeholder, tried to select a new one, and there
        # was nothing behind it to select. Fixed two ways: this banner states the real breakdown in
        # large text before anything else is read, and the placeholder row itself is gone (see
        # _r_board) -- every row now in the table is a real, answerable row.
        banner = tk.Frame(f, bg="#26415c")
        banner.grid(row=0, column=0, sticky="ew", pady=(2, 2))
        banner.columnconfigure(0, weight=1)
        self.wait_count_lbl = tk.Label(banner, text="", bg="#26415c", fg="#ffffff",
                                       font=("Segoe UI", 12, "bold"), anchor="w",
                                       justify="left", padx=12, wraplength=self._wrap_w)
        # Padding trimmed further 6,6 -> 3,3 and font 13 -> 12 (2026-08-17, third pass, defect A --
        # measured live: this banner alone cost 64px, and the fixed rows on this tab (banner+hint+
        # table+answer) totalled MORE than the ~441px the tab actually has, which is why the
        # reading pane -- the one row that is supposed to get the SPACE THEY DON'T USE -- measured
        # 1px even before this trim). Still bold and still the most prominent text on the tab.
        self.wait_count_lbl.grid(row=0, column=0, sticky="ew", pady=(3, 3))
        self.wait_banner = banner

        self.board_hint = tk.Label(
            f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 9), anchor="w",
            justify="left", wraplength=self._wrap_w, padx=4, pady=2)
        self.board_hint.grid(row=1, column=0, sticky="ew")

        # THE "NEW DATA" AFFORDANCE (2026-08-17, DEFECT B -- see _r_board / _board_engaged).
        # Hidden (`grid_remove`) until a refresh arrives while the owner is reading or typing on
        # this tab; that refresh is NOT applied (nothing here may move under the owner while they
        # are engaged with it), so this is the only thing that changes on screen -- and it is an
        # explicit click, never automatic.
        self.board_new_data_lbl = tk.Label(
            f, text="", bg=_AMBER_BG, fg="#ffffff", font=("Segoe UI", 9, "bold"), anchor="w",
            justify="left", wraplength=self._wrap_w, padx=8, pady=4, cursor="hand2")
        self.board_new_data_lbl.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        self.board_new_data_lbl.bind("<Button-1>", self._board_force_refresh)
        self.board_new_data_lbl.grid_remove()

        # THE TABLE -- A FIXED, COMPACT ROW (see the rowconfigure comment above for why this
        # replaces the PanedWindow). height=3 (was 12, then 6 -- measured live: even 6 rows
        # (197px) left the fixed rows on this tab totalling MORE than its ~441px budget, which is
        # why the reading pane still measured 1px after the first trim). The STANDARD is that this
        # list carries SHORT LABELS ONLY -- an id plus a gist -- never the full question text (see
        # `_gist` below), so it does not need to show every row at once; the scrollbar `_tree()`
        # already attaches reaches the rest, and Ctrl/Shift-click plus the up/down arrows keep
        # every row reachable without a mouse.
        tv_wrap = ttk.Frame(f)
        tv_wrap.columnconfigure(0, weight=1)
        tv_wrap.rowconfigure(0, weight=1)
        frame, self.board_tv = self._tree(
            tv_wrap, cols=("id", "kind", "question", "now", "updated"),
            widths=(55, 150, 420, 250, 130),
            minwidths=(45, 120, 260, 180, 110),
            headings=("#", "", "WHAT NEEDS YOUR DECISION (click a row to read it in full below)",
                      "WHAT HAPPENS IF YOU SAY NOTHING", "RECORDED / LAST UPDATED"), height=3)
        frame.grid(row=0, column=0, sticky="nsew")
        self.board_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_board_detail())
        tv_wrap.grid(row=self._board_table_row, column=0, sticky="ew", pady=(0, 4))

        # ---- ARCHIVE + READING-SIZE CONTROLS (owner, 2026-08-20) --------------------------------
        # "move the questions already answered to an archive that I can click into if I want" and
        # "make more room for the question text when it's selected".
        #
        # A TOGGLE RATHER THAN A TREE HIERARCHY, deliberately. Nesting answered rows under a
        # collapsible parent node would change every iid in `self._wait_rows`, which is the key the
        # selection handler and the answer box both index by -- a much larger blast radius than this
        # tab's history justifies. A toggle swaps WHICH rows are listed and touches nothing else.
        #
        # THE READING PANE GROWS BY SHRINKING THE TABLE, because this tab's layout gives the detail
        # pane the only weighted grid row: every row the table gives up goes straight to it. The
        # table is a fixed `height` in ROWS, so this is one `configure` call and it is reversible.
        self.board_archive = False
        self.board_big_read = False
        # Lives INSIDE `tv_wrap` (row 1) rather than as a new row on `f`. Inserting a row into `f`
        # would push `_board_detail_row` and the answer box down by one, and those indices are held
        # in attributes and referenced elsewhere -- renumbering them is exactly the kind of layout
        # churn that has already broken this tab twice.
        ctl = tk.Frame(tv_wrap, bg=_ALT)
        ctl.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.board_archive_btn = ttk.Button(ctl, text="Show answered archive",
                                            command=self._toggle_board_archive)
        self.board_archive_btn.grid(row=0, column=0, padx=(2, 6))
        self.board_big_btn = ttk.Button(ctl, text="Bigger reading pane",
                                        command=self._toggle_board_big_read)
        self.board_big_btn.grid(row=0, column=1, padx=(0, 10))
        self.board_mode_lbl = tk.Label(ctl, text="", bg=_ALT, fg=_DIM, anchor="w",
                                       font=("Segoe UI", 9), wraplength=self._wrap_w_narrow)
        self.board_mode_lbl.grid(row=0, column=2, sticky="ew")
        ctl.columnconfigure(2, weight=1)

        # THE READING PANE -- THE PRIMARY CONTENT OF THIS TAB. Bigger font (13pt heading 16pt,
        # up from 10pt/11pt), generous line spacing, and it is the one row with grid weight (see
        # above), so it takes essentially all the space the table and the fixed rows do not use.
        # Given its own scrollbar too (the other seven `_detail()` panes don't need one -- they are
        # secondary hint boxes with a fixed height -- but this is the pane the owner reads a full
        # question from, and it must never silently clip content the way the old table cell did).
        det_wrap = ttk.Frame(f)
        det_wrap.columnconfigure(0, weight=1)
        det_wrap.rowconfigure(0, weight=1)
        self.board_detail = self._detail(det_wrap, height=10, font_size=13,
                                         heading_font_size=16, spacing=(2, 6, 12))
        self.board_detail.grid(row=0, column=0, sticky="nsew")
        det_sb = ttk.Scrollbar(det_wrap, orient="vertical", command=self.board_detail.yview)
        self.board_detail.configure(yscrollcommand=det_sb.set)
        det_sb.grid(row=0, column=1, sticky="ns")
        det_wrap.grid(row=self._board_detail_row, column=0, sticky="nsew")

        # THE ANSWER BOX stays a plain fixed grid row -- the mechanism that has reliably given the
        # banner and the hint their full height all along; a PanedWindow pane was tried for it in
        # the second pass and measured to collapse to 4px regardless of its own minsize.
        #
        # PLAIN ttk.Frame, NOT ttk.LabelFrame (2026-08-17, third pass, defect A). The LabelFrame's
        # own static border title used to read "YOUR ANSWER" -- entirely redundant with
        # `answer_caption` below, which already says "YOUR ANSWER TO <row>...", and a LabelFrame's
        # border+title costs real pixels for no information the caption doesn't already carry.
        # Measured live: this saved part of the space that got the reading pane off a 1px crush.
        ans = ttk.Frame(f)
        self.answer_frame = ans
        ans.grid(row=5, column=0, sticky="ew", pady=(4, 0))
        ans.columnconfigure(0, weight=1)
        # THE CAPTION IS LOAD-BEARING, not decoration. It names the exact question this box will
        # write to, and it is the only thing standing between the owner and an answer attached to
        # the wrong row. It is rewritten on every selection change by _sync_answer_ui().
        # tk.Label's own `pady` is a single distance, not a (top, bottom) pair (see the identical
        # note on the headline label above) -- asymmetric spacing goes on the grid call instead.
        self.answer_caption = tk.Label(ans, text="", bg=_PANEL, fg=_BLUE,
                                       font=("Segoe UI", 11, "bold"), anchor="w", justify="left",
                                       wraplength=self._wrap_w, padx=6)
        self.answer_caption.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        # DEFECT 4: an obviously-an-answer-box border (was a thin 1px border in the window's
        # default colour, indistinguishable from every other box on screen) plus a slightly larger
        # font. Height 2 (was 3, then 3 again under the paned-window regime) -- measured live: on
        # this tab's real ~441px budget, 3 lines was part of what crushed the reading pane to 1px;
        # 2 lines is still enough to see a real sentence while typing it, and the box itself never
        # blocks typing more -- Tk lets a Text widget's content scroll past its declared height.
        self.answer_box = tk.Text(ans, height=2, wrap="word", bd=0, padx=8, pady=4,
                                  bg="#1b1b1b", fg=_FG, insertbackground=_FG,
                                  highlightthickness=2, highlightbackground="#4a7fb5",
                                  highlightcolor="#4a7fb5", font=("Segoe UI", 11))
        self.answer_box.grid(row=1, column=0, sticky="ew", padx=6, pady=4)
        # Keystrokes are captured into the per-question draft as they happen, so that a refresh
        # landing between the last keypress and the button press cannot lose them.
        self.answer_box.bind("<KeyRelease>", lambda _e: self._stash_draft())
        btns = ttk.Frame(ans)
        btns.grid(row=1, column=1, sticky="ns", padx=(0, 6))
        self.answer_btn = ttk.Button(btns, text="Save my answer", command=self._save_answer)
        self.answer_btn.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        # THE ESCAPE HATCH. On the night this panel was reported broken the board had ZERO open
        # questions, so every selectable row was a DECISION or a STANDING item, none of which can
        # be written -- the owner typed a real answer and the panel had nowhere to put it. This
        # button gives typed text somewhere to go REGARDLESS of what is selected: it files the text
        # as its own board row, already answered, through the same tested board.py calls.
        self.note_btn = ttk.Button(btns, text="File as a new note", command=self._file_note)
        self.note_btn.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        ttk.Button(btns, text="Clear",
                   command=self._clear_answer).grid(row=2, column=0, sticky="ew")
        self.answer_status = tk.Label(ans, text="", bg=_PANEL, fg=_DIM, anchor="w",
                                      font=("Segoe UI", 9), wraplength=self._wrap_w, justify="left")
        self.answer_status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 3))

    # ---- TAB 2 (group A) ----------------------------------------------
    def _build_running(self) -> None:
        """RUNNING NOW -- agents, experiments, the remote box, AND the overnight loop.

        The loop had its own tab. It did not need one: "is the loop on" is a question about whether
        anything is happening, which is this tab's question, and separating them meant the owner had
        to check two tabs to answer "is work still going". The stop command stays on screen with a
        copy button, because it is the one control in this window that stops the machine."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="2. RUNNING")
        self.tab_running = f
        f.columnconfigure(0, weight=1)

        loop = tk.Frame(f, bg=_ALT)
        loop.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        loop.columnconfigure(0, weight=1)
        self.loop_big = tk.Label(loop, text="...", bg=_ALT, fg=_FG,
                                 font=("Segoe UI", 15, "bold"), anchor="w", padx=12,
                                 wraplength=self._wrap_w_narrow)
        self.loop_big.grid(row=0, column=0, sticky="ew", pady=(8, 1))
        self.loop_sub = tk.Label(loop, text="", bg=_ALT, fg=_DIM, font=("Segoe UI", 10),
                                 anchor="w", justify="left", padx=12,
                                 wraplength=self._wrap_w_narrow)
        self.loop_sub.grid(row=1, column=0, sticky="ew")
        tk.Label(loop, text="TO STOP IT, RUN THIS:", bg=_ALT, fg=_AMBER,
                 font=("Segoe UI", 9, "bold"), anchor="w",
                 padx=12).grid(row=2, column=0, sticky="ew", pady=(6, 1))
        # `width=` PINNED (2026-08-17). A bare tk.Text defaults to width=80 CHARACTERS -- at this
        # font that is ~1150 px, wider than the whole window, found the same way as the caption fix
        # above (a live widget requesting more than `winfo_width()`). `sticky="ew"` does not shrink
        # a widget below its own request, so this alone was forcing the RUNNING NOW tab, and with
        # it the Notebook itself, to demand ~1150 px regardless of the column-budget work elsewhere.
        # The real disarm command is ~35 chars; 56 leaves headroom without reproducing the fault.
        self.disarm_box = tk.Text(loop, height=1, width=56, wrap="none", bd=0, padx=12, pady=4,
                                  bg="#1b1b1b", fg="#ffd479", insertbackground=_FG,
                                  highlightthickness=0, font=("Consolas", 12, "bold"))
        self.disarm_box.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 4))
        self.loop_alt = tk.Label(loop, text="", bg=_ALT, fg=_DIM, font=("Segoe UI", 9),
                                 anchor="w", justify="left", padx=12,
                                 wraplength=self._wrap_w_narrow)
        self.loop_alt.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(loop, text="Copy the command",
                   command=self._copy_disarm).grid(row=3, column=1, padx=(6, 12))

        # OWNER REQUEST 2026-08-18 (COMMENTARY): "there should be a button on the 'running' tab to
        # turn off overnight or turn it back on, with an input for iterations. There should also be
        # a button on that tab to kill the orphans / zombie processes that haven't cleanly exited".
        # The copy-the-command box above stays: it is the one control that still works if this GUI
        # or the venv is broken, which is exactly when someone most needs to stop the loop.
        ctl = tk.Frame(loop, bg=_ALT)
        ctl.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 10))
        tk.Label(ctl, text="iterations:", bg=_ALT, fg=_DIM,
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        self.loop_iters = tk.Entry(ctl, width=8, bd=0, bg="#1b1b1b", fg=_FG,
                                   insertbackground=_FG, highlightthickness=1,
                                   highlightbackground="#3a3a3a", font=("Consolas", 11))
        self.loop_iters.grid(row=0, column=1, sticky="w", padx=(6, 10))
        self.loop_iters.insert(0, "200")
        ttk.Button(ctl, text="Turn overnight ON",
                   command=self._loop_arm).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(ctl, text="Turn overnight OFF",
                   command=self._loop_disarm).grid(row=0, column=3, padx=(0, 18))
        ttk.Button(ctl, text="Kill stuck runs...",
                   command=self._kill_stuck_runs).grid(row=0, column=4)
        self.loop_action_msg = tk.Label(ctl, text="", bg=_ALT, fg=_DIM, anchor="w",
                                        font=("Segoe UI", 9), wraplength=self._wrap_w_narrow)
        self.loop_action_msg.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(4, 0))

        # A RESIZABLE PANEL (owner, 2026-08-16). The three parts of this tab used to be fixed-height
        # grid rows, so the owner could not give the run list more room no matter how large they
        # made the window. A PanedWindow puts a draggable sash between each pair: whichever part
        # they are reading can be grown at the expense of the others, and the whole thing still
        # grows with the window.
        pw = tk.PanedWindow(f, orient="vertical", bg=_BG, bd=0, sashwidth=7, sashrelief="raised",
                            sashpad=1, showhandle=False, opaqueresize=False)
        pw.grid(row=1, column=0, sticky="nsew")
        f.rowconfigure(1, weight=1)
        self.running_panes = pw

        ag_wrap = ttk.Frame(pw)
        ag_wrap.columnconfigure(0, weight=1)
        ag_wrap.rowconfigure(1, weight=1)
        tk.Label(ag_wrap, text="AGENTS", bg=_PANEL, fg=_BLUE, anchor="w",
                 font=("Segoe UI", 10, "bold"), padx=4).grid(row=0, column=0, sticky="ew",
                                                             pady=(4, 2))
        # THE DECLARED WIDTHS DELIBERATELY SUM TO LESS THAN THE VIEWPORT. That is the second half of
        # the cramped-fields fault: the previous widths summed to 1140 px inside a ~1100 px table,
        # so there was never any spare space for `stretch` to distribute and every column stayed at
        # its declared size no matter how large the window got. Leave room, and stretching becomes
        # real. The MINIMUMS are the floor under the identity columns.
        frame, self.agents_tv = self._tree(
            ag_wrap, cols=("state", "name", "doing", "running", "last"),
            widths=(115, 210, 340, 100, 150),
            minwidths=(105, 175, 240, 95, 135),
            headings=("", "AGENT", "WHAT IT IS DOING", "RUNNING FOR",
                      "TRANSCRIPT LAST WRITTEN"),
            height=6, stretch_all=True)
        frame.grid(row=1, column=0, sticky="nsew")
        pw.add(ag_wrap, minsize=110, stretch="always")

        # ONE TABLE FOR "WHAT IS RUNNING", not two, and it includes the things that are NOT.
        # A run that died used to vanish from this tab entirely while its scratch/<name>.pid file
        # stayed on disk and went on being quoted as live -- 37 of 39 of them pointed at nothing on
        # the night this was written, three of those cited as live in agent briefs for hours, and
        # one was this dashboard's own process. A missing row reads as "nothing to see"; a row that
        # says DEAD BUT CLAIMED LIVE cannot be misread. Identity and state get the width here:
        # WHAT IT IS and WHETHER IT IS ACTUALLY ALIVE are the two things the owner asked to see.
        lx_wrap = ttk.Frame(pw)
        lx_wrap.columnconfigure(0, weight=1)
        lx_wrap.rowconfigure(1, weight=1)
        self.local_head = tk.Label(lx_wrap, text="WORK ON THIS MACHINE", bg=_PANEL, fg=_BLUE,
                                   anchor="w", font=("Segoe UI", 10, "bold"), padx=4,
                                   justify="left", wraplength=self._wrap_w)
        self.local_head.grid(row=0, column=0, sticky="ew", pady=(4, 2))
        # MEMORY was dropped as a column. The owner asked to see run IDENTITY and STATE; a megabyte
        # figure was consuming width that those two needed, and it is still in the detail box below.
        frame2, self.local_tv = self._tree(
            lx_wrap, cols=("state", "name", "progress", "running", "pid", "updated"),
            widths=(190, 300, 210, 105, 70, 130),
            minwidths=(165, 250, 165, 95, 60, 115),
            headings=("IS IT ACTUALLY RUNNING?", "WHAT IT IS", "PROGRESS / LAST OUTPUT",
                      "RUNNING FOR", "PROCESS", "OUTPUT LAST WRITTEN"),
            height=9, stretch_all=True)
        frame2.grid(row=1, column=0, sticky="nsew")
        self.local_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_running_detail())
        pw.add(lx_wrap, minsize=150, stretch="always")

        det_wrap = ttk.Frame(pw)
        det_wrap.columnconfigure(0, weight=1)
        det_wrap.rowconfigure(0, weight=1)
        self.running_detail = self._detail(det_wrap, height=10)
        self.running_detail.grid(row=0, column=0, sticky="nsew")
        pw.add(det_wrap, minsize=90, stretch="never")

    # ---- PANEL 7 ------------------------------------------------------
    def _build_results(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="7. LATEST RESULTS")
        self.tab_results = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        self.results_hint = tk.Label(
            f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10), anchor="w",
            justify="left", wraplength=self._wrap_w, padx=4, pady=6)
        self.results_hint.grid(row=0, column=0, sticky="ew")

        # VETTED? is not decoration and it is not last on purpose. 2026-08-18 measured that 99.5%
        # of the archive's HARD_PASS carry neither a CI nor a null, and 30 cells vetted produced
        # ONE upheld result -- so a verdict string rendered straight out of metrics.json with
        # nothing beside it reads as an endorsement this project cannot make. UNVETTED is the
        # VISIBLE DEFAULT, never a blank (notes/PLAN_SECTION_7_audit_findings_2026-08-18.md 7.5b).
        frame, self.results_tv = self._tree(
            f, cols=("when", "what", "verdict", "vetted", "floor", "sep", "name"),
            widths=(175, 100, 260, 150, 130, 150, 320),
            headings=("RESULT LAST WRITTEN", "", "WHAT IT CONCLUDED", "HAS ANYONE CHECKED IT?",
                      "DID IT NAME A FLOOR?", "INTERVALS SEPARATED?", "EXPERIMENT"),
            height=13)
        frame.grid(row=1, column=0, sticky="nsew")
        self.results_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_result_detail())

        self.results_detail = self._detail(f, height=8)
        self.results_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

    def _copy_disarm(self) -> None:
        try:
            cmd = self.disarm_box.get("1.0", "end").strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self.loop_alt.configure(text="Copied. Paste it into a terminal in D:/AI/hd-instrument.")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # RUNNING-tab actions (owner request 2026-08-18)
    # ------------------------------------------------------------------
    def _say(self, msg: str, ok: bool = True) -> None:
        try:
            self.loop_action_msg.configure(text=msg, fg=(_DIM if ok else _AMBER))
        except tk.TclError:
            pass

    def _run_tool(self, args: list) -> tuple:
        """Run a repo tool with the REPO VENV, never bare `python` (CLAUDE.md convention).
        Returns (ok, output). Never raises -- a dashboard button must not take the window down."""
        import subprocess
        py = _REPO / ".venv" / "Scripts" / "python.exe"
        if not py.exists():                       # POSIX / venv-less fallback
            py = Path(sys.executable)
        try:
            r = subprocess.run([str(py)] + [str(a) for a in args], capture_output=True, text=True,
                               timeout=30, cwd=str(_REPO),
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()
        except Exception as exc:
            return False, f"{type(exc).__name__}: {exc}"

    def _loop_arm(self) -> None:
        raw = (self.loop_iters.get() or "").strip()
        # "unlimited" is a REAL cap value in autoloop.py, so it is accepted here rather than
        # silently coerced -- but anything else non-numeric is refused instead of guessed at.
        if raw.lower() in ("unlimited", "inf", "none"):
            cap = "unlimited"
        else:
            try:
                cap = str(int(raw))
                if int(cap) < 1:
                    raise ValueError
            except ValueError:
                self._say(f"'{raw}' is not a number of iterations. "
                          f"Type a whole number (e.g. 200) or the word 'unlimited'.", ok=False)
                return
        ok, out = self._run_tool([_REPO / "tools" / "autoloop.py", "arm", "--max", cap,
                                  "--by", "status_gui"])
        self._say(f"Overnight loop ARMED, cap {cap}. It resumes at the end of the next turn."
                  if ok else f"Could not arm: {out[:300]}", ok=ok)

    def _loop_disarm(self) -> None:
        ok, out = self._run_tool([_REPO / "tools" / "autoloop.py", "disarm"])
        self._say("Overnight loop DISARMED. The current turn finishes, then it stops."
                  if ok else f"Could not disarm: {out[:300]}", ok=ok)

    @staticmethod
    def _cpu_seconds(pid: int):
        """Total CPU (user+kernel) seconds for a pid, or None if unreadable. ctypes only -- no
        subprocess, so this stays cheap enough to call twice inside a button press."""
        if sys.platform != "win32":
            return None
        try:
            import ctypes
            from ctypes import wintypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x0400 | 0x1000, False, int(pid))   # QUERY_INFORMATION|LIMITED
            if not h:
                return None
            try:
                c = wintypes.FILETIME(); e = wintypes.FILETIME()
                u = wintypes.FILETIME(); s = wintypes.FILETIME()
                if not k.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e),
                                         ctypes.byref(s), ctypes.byref(u)):
                    return None
                def _ticks(ft):
                    return ((ft.dwHighDateTime << 32) | ft.dwLowDateTime) / 1e7
                return _ticks(u) + _ticks(s)
            finally:
                k.CloseHandle(h)
        except Exception:
            return None

    def _filter_to_idle(self, cands: list, settle_s: float = 2.0) -> tuple:
        """Keep only candidates whose CPU time does NOT advance over `settle_s`.

        A process we cannot read CPU for is treated as BUSY (kept out of the kill list). The bias
        is deliberate and one-directional: failing to offer a genuinely dead process costs nothing,
        while offering a live one risks destroying hours of work.
        """
        first = {pid: self._cpu_seconds(pid) for pid, _ in cands}
        time.sleep(settle_s)
        idle, busy = [], 0
        for pid, cmd in cands:
            a, b = first.get(pid), self._cpu_seconds(pid)
            if a is None or b is None or b > a + 0.01:
                busy += 1
            else:
                idle.append((pid, cmd))
        return idle, busy

    def _kill_stuck_runs(self) -> None:
        """List ORPHANED repo python processes and kill only after explicit confirmation.

        DEFINING "STUCK" CORRECTLY MATTERS MORE THAN THE BUTTON. The obvious rule -- "no living
        parent" -- IS WRONG HERE, and was caught before this shipped: the first draft of this
        function would have offered to kill PID 27628, a HEALTHY density sweep, because runs in
        this repo are launched DETACHED via PowerShell Start-Process precisely so they survive
        their launching shell. Parentless is what a correct long run looks like. A button built on
        that rule would kill live work, which is the opposite of what it is for.

        SO STUCK = parentless AND **BURNING NO CPU** AND **HAVING NO LIVE CHILD**. All three are
        load-bearing, and the third was added after the second draft was tested against reality:
        PID 27628 read as parentless AND idle (0.0156 CPU seconds in 26 minutes) and would have
        been offered -- but it is the WRAPPER of PID 28944, which was doing the actual work and
        writing a unit that same minute. An idle parent waiting on a busy child is the NORMAL shape
        of a detached run here, not a zombie, and killing it can take the child with it.

        A working compute job accumulates CPU time; a wedged one does not. CPU is sampled twice
        ~2s apart and anything that advances is excluded. That is a real liveness probe rather
        than a proxy -- but it must be read on the whole PROCESS TREE, not one node of it.

        DELIBERATELY NEVER OFFERED: this GUI, its parent, and dash_gui.py -- the same exclusion
        `_enforce_single_instance` makes, for the same reason (a cleanup button that can kill the
        window you pressed it in is a trap). Processes with a LIVE parent are never offered either:
        somebody is waiting on those.
        """
        from tkinter import messagebox
        try:
            from local_exp_scan import _wmic_python_procs
        except Exception as exc:
            self._say(f"Cannot enumerate processes: {exc}", ok=False)
            return
        import os
        procs = _wmic_python_procs()
        if not procs:
            self._say("Found no python processes to examine.", ok=False)
            return
        live = {p.get("pid") for p in procs if p.get("pid") is not None}
        # Every pid that is the PARENT of some live process. A detached run in this repo is
        # typically an idle wrapper plus a busy worker; the wrapper must never be offered.
        parents_of_live = {p.get("ppid") for p in procs if p.get("ppid") is not None}
        try:
            own, parent = os.getpid(), os.getppid()
        except OSError:
            own, parent = -1, -1
        cands = []
        for p in procs:
            pid, ppid, cmd = p.get("pid"), p.get("ppid"), (p.get("cmd") or "")
            low = cmd.lower()
            if pid in (own, parent) or pid is None:
                continue
            if "status_gui.py" in low or "dash_gui.py" in low:
                continue
            if "hd-instrument" not in low.replace("\\", "/").replace("d:/ai/", ""):
                if "hd-instrument" not in low:
                    continue
            if ppid in live:            # parent still alive -> a running job, not an orphan
                continue
            if pid in parents_of_live:  # idle WRAPPER of a busy child -> never offer (see docstring)
                continue
            cands.append((pid, cmd))
        if not cands:
            self._say("No stuck runs found. (A process whose parent is still alive is somebody's "
                      "running job and is never offered here.)")
            return
        # THE CPU PROBE -- this is what separates a wedged run from a healthy detached one.
        cands, busy = self._filter_to_idle(cands)
        if not cands:
            self._say(f"No stuck runs found. {busy} detached run(s) have no parent but ARE burning "
                      f"CPU, so they are working normally and were not offered.")
            return
        lines = [f"  PID {pid}  {cmd[:110]}" for pid, cmd in cands[:15]]
        more = "" if len(cands) <= 15 else f"\n  ... and {len(cands)-15} more"
        if not messagebox.askyesno(
                "Kill orphaned runs?",
                f"{len(cands)} python process(es) in this repo have NO LIVING PARENT:\n\n"
                + "\n".join(lines) + more
                + "\n\nKill them? This cannot be undone, and any UNSAVED progress in them is lost.\n"
                  "Completed per-unit checkpoints on disk are NOT affected.",
                icon="warning", default="no"):
            self._say("Cancelled. Nothing was killed.")
            return
        import subprocess
        killed, failed = 0, 0
        for pid, _ in cands:
            try:
                r = subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True,
                                   timeout=6,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                killed += 1 if r.returncode == 0 else 0
                failed += 0 if r.returncode == 0 else 1
            except Exception:
                failed += 1
        self._say(f"Killed {killed} orphaned process(es)"
                  + (f"; {failed} could not be killed (may need admin)." if failed else "."),
                  ok=(failed == 0))

    # ------------------------------------------------------------------
    # polling
    # ------------------------------------------------------------------
    def _schedule(self) -> None:
        self.root.after(REFRESH_MS, self._auto)

    def _auto(self) -> None:
        self.refresh_now()
        self._schedule()

    def refresh_now(self) -> None:
        if self._poll_inflight:
            started = self._poll_started
            if started is None or (time.time() - started) < POLL_WEDGE_S:
                return
        self._poll_inflight = True
        self._poll_started = time.time()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        t0 = time.time()
        try:
            payload = status_state.collect()
            _diag("collect", ms=round(1000 * (time.time() - t0)))
            self._q.put(("ok", payload))
        except Exception as exc:
            # The FULL traceback goes to the log; the short form goes on screen. Before this, a
            # collector exception was shown truncated to 400 chars in the status bar and recorded
            # nowhere, so a recurring failure left no trace to diagnose it from afterwards.
            _diag("collect_error", ms=round(1000 * (time.time() - t0)),
                  err=f"{type(exc).__name__}: {exc}", tb=traceback.format_exc(limit=12))
            self._q.put(("error", traceback.format_exc(limit=6)))

    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self._q.get_nowait()
                self._poll_inflight = False
                if kind == "ok":
                    self._state = payload
                    self._last_ok = time.time()
                    self._last_error = None
                    self.render(payload)
                else:
                    self._last_error = str(payload)[:400]
        except _queue.Empty:
            pass
        self.root.after(200, self._pump)

    def _tick(self) -> None:
        parts = []
        if self._last_ok is not None:
            parts.append(f"updated {int(time.time() - self._last_ok)}s ago")
        else:
            parts.append("no data yet")
        if self._poll_inflight and self._poll_started is not None:
            held = time.time() - self._poll_started
            parts.append("POLL WEDGED - data may be stale" if held > POLL_WEDGE_S
                         else "refreshing...")
        if self._last_error:
            parts.append(f"LAST REFRESH ERROR: {self._last_error[:160]}")
        # SURFACE THE DIAGNOSTIC, do not just write it to a file nobody opens. If the window has
        # hitched at all this session the owner sees the worst one and where the log is.
        worst = getattr(self, "_worst_stall_ms", 0)
        if worst > UI_STALL_MS:
            parts.append("worst UI freeze this session %.1fs (log: %s)"
                         % (worst / 1000.0, DIAG_PATH.name))
        # This bar is the ONLY place the refresh clock appears, and it says so: every timestamp in
        # every table is an evidence age, and the two must not be read for one another.
        parts.append(f"auto-refresh every {REFRESH_MS // 1000}s  |  F5 = refresh  |  "
                     f"Ctrl+1..7 = jump to a panel  |  this clock is the REFRESH, not the age of "
                     f"anything on screen")
        self.status_lbl.configure(text="    |    ".join(parts))
        # Per-tab evidence age, re-applied on the tick so it counts up between refreshes rather
        # than freezing at whatever it was when the data last landed.
        # ---- EVERYTHING BELOW RUNS ON THE UI THREAD, SO IT IS TIMED ----------------------------
        # The freeze this instruments was a 6.9s `data/` walk reached from `_update_tab_ages`. It
        # is off-thread now, but the point of a diagnostic is to catch the NEXT one, which will be
        # somewhere nobody suspects. Anything over UI_STALL_MS is a hitch the owner can see.
        _t0 = time.time()
        self._update_tab_ages()
        _t1 = time.time()
        # Checked on the TICK, not on a successful collect: a window running code old enough to
        # matter may also be failing to collect, and that is precisely when the owner most needs
        # to be told the window itself is the problem.
        self._check_self_stale()
        _t2 = time.time()
        ms_total = 1000 * (_t2 - _t0)
        if ms_total > UI_STALL_MS:
            _diag("ui_stall", ms=round(ms_total),
                  tab_ages_ms=round(1000 * (_t1 - _t0)),
                  self_stale_ms=round(1000 * (_t2 - _t1)))
            self._worst_stall_ms = max(getattr(self, "_worst_stall_ms", 0), ms_total)
        self.root.after(TICK_MS, self._tick)

    def _check_self_stale(self) -> None:
        """Say so, unmissably, when this file has changed on disk since the process loaded it.

        Never raises and never claims staleness it cannot prove: an unreadable mtime, or a missing
        baseline, leaves the banner hidden. The bias is deliberate -- a false 'restart me' is a
        nuisance, a false 'you are up to date' is the three-day failure this exists to prevent.
        """
        if _SRC_MTIME_AT_IMPORT is None:
            return
        try:
            now_mtime = Path(__file__).resolve().stat().st_mtime
        except OSError:
            return
        # Whole seconds: some filesystems report sub-second jitter that is not a real edit.
        stale = int(now_mtime) > int(_SRC_MTIME_AT_IMPORT)
        try:
            if stale and not self.stale_shown:
                age = _fmt_dur(max(0.0, time.time() - _SRC_MTIME_AT_IMPORT))
                self.stale_lbl.configure(
                    text=("THIS WINDOW IS RUNNING OLD CODE -- CLOSE IT AND OPEN IT AGAIN.\n"
                          f"It loaded {age} ago and the dashboard has been changed since. "
                          "Buttons, tabs and questions added after that point are NOT on screen, "
                          "so anything that looks missing may already exist."))
                self.stale_lbl.grid(row=2, column=0, sticky="ew", pady=(0, 9))
                self.stale_shown = True
            elif not stale and self.stale_shown:
                self.stale_lbl.grid_remove()
                self.stale_shown = False
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # rendering -- every panel independently guarded
    # ------------------------------------------------------------------
    def render(self, s: dict) -> None:
        for name, fn in (("headline", self._r_headline), ("where", self._r_where),
                         ("scores", self._r_scores), ("organs", self._r_organs),
                         ("fidelity", self._r_fidelity),
                         ("board", self._r_board), ("running", self._r_running),
                         ("results", self._r_results), ("commentary", self._r_commentary)):
            try:
                fn(s)
            except Exception:
                # One broken panel must never take the window down. Say which one broke.
                self._last_error = f"{name} panel render failed: " + \
                    traceback.format_exc(limit=3).replace("\n", " | ")

    # ---- headline -----------------------------------------------------
    def _r_headline(self, s: dict) -> None:
        """The strip answers three things without a click: WHERE WE ARE, HOW WE ARE DOING against
        the floor, and HOW MUCH OF THIS NO LONGER MATCHES ITS SOURCE."""
        pl = _d(s.get("plan"))
        w = _d(s.get("walls"))
        h = _d(w.get("headline")) or None
        standing = h.get("standing") if isinstance(h, dict) else None
        bg = {"BELOW_FLOOR": _RED_BG, "ABOVE_FLOOR": _GREEN_BG}.get(standing, _AMBER_BG)
        for widget in (self.headbar, self.headline_lbl, self.headsub_lbl):
            widget.configure(bg=bg)

        # LINE 1: where we are, and the one next thing to do.
        if pl.get("status") == "OK" and _d(pl.get("current")):
            cur = _d(pl.get("current"))
            nxt = _d(pl.get("next_action")).get("text") or "NOT STATED IN THE PLAN"
            self.headline_lbl.configure(
                text=f"WE ARE IN {cur.get('id')} -- {cur.get('title')}.    "
                     f"NEXT: {str(nxt)[:150]}")
        else:
            self.headline_lbl.configure(
                text=f"THE PLAN IS {pl.get('status', 'MISSING')} -- "
                     f"{str(pl.get('detail', ''))[:160]}")

        # LINE 2: the score beside its floor, then the counts. A score is never shown alone.
        bits = []
        if isinstance(h, dict):
            verb = {"BELOW_FLOOR": "WE ARE BELOW IT", "ABOVE_FLOOR": "WE ARE ABOVE IT",
                    "LEVEL": "WE ARE LEVEL WITH IT"}.get(standing, "NOT ESTABLISHED")
            bits.append(f"WE GET {h.get('score')}, {h.get('floor_name')} GETS "
                        f"{h.get('floor')} -- {verb}")
        else:
            bits.append(f"SCORES ARE MISSING ({w.get('status', '?')})")
        gov = _d(_d(s.get("scores")).get("governing_floor"))
        if gov.get("score"):
            bits.append(f"and a {gov.get('floor_name', 'constant')} gets {gov.get('score')}")
        b = _d(s.get("board"))
        pl_dec = len(_l(pl.get("decisions"))) + len(_l(_d(pl.get("operator")).get("rows")))
        n_open = b.get("n_open")
        bits.append(f"{n_open if n_open is not None else '?'} question(s) + {pl_dec} standing "
                    f"decision(s) waiting on you")
        rn = _d(s.get("running"))
        ag = _d(rn.get("agents"))
        bits.append(f"{ag.get('n_active', '?')} agent(s) working")
        bits.append(f"{len(_l(rn.get('local_experiments')))} experiment(s) running here")
        lp = _d(s.get("loop"))
        bits.append("overnight loop ON" if lp.get("armed") is True else
                    "overnight loop off" if lp.get("armed") is False else
                    "overnight loop UNKNOWN")
        dr = _d(s.get("drift"))
        nd, nu = dr.get("n_drifted"), dr.get("n_unknown")
        if nd is not None:
            bits.append(f"{nd} value(s) no longer match their source"
                        + (f", {nu} panel(s) unchecked" if nu else ""))
        # HOW OLD IS WHAT I AM LOOKING AT -- answerable without opening a tab. Deliberately worded
        # as EVIDENCE, because the refresh clock lives in the status bar at the bottom and the two
        # must never be mistaken for each other.
        ags = _d(s.get("ages"))
        if ags.get("status") == "OK":
            bits.append(f"evidence on screen: newest {ags.get('newest_rel')}, oldest "
                        f"{ags.get('oldest_rel')}"
                        + (f", {ags.get('n_unknown')} undated" if ags.get("n_unknown") else ""))
        else:
            bits.append(f"evidence ages {ags.get('status', 'MISSING')}")
        self.headsub_lbl.configure(text="     |     ".join(bits), fg="#f4f4f4")

    # ---- tab 1: WHERE WE ARE ------------------------------------------
    def _r_where(self, s: dict) -> None:
        p = _d(s.get("plan"))
        tv = self.where_tv
        _scroll_frac = self._keep_scroll(tv)   # defect 3
        tv.delete(*tv.get_children())
        self._where_rows: dict[str, dict] = {}
        # Stashed from the payload JUST RENDERED, not read back from self._state. A direct
        # render() (which is what the self-test does) must not be a different code path from the
        # live poll, or the self-test stops testing the thing that ships.
        self._where_state: dict = p
        if p.get("status") != "OK":
            self.where_phase.configure(text=f"THE PLAN IS {p.get('status', 'MISSING')}")
            self.where_next.configure(text=str(p.get("detail", ""))[:400])
            for wdg in (self.where_phase, self.where_next):
                wdg.configure(bg=_AMBER_BG)
            self.where_phase.master.configure(bg=_AMBER_BG)
            self.where_hint.configure(text="", fg=_AMBER)
            tv.insert("", "end", values=(f"{p.get('status')}", "MISSING", "MISSING",
                                         "MISSING", "MISSING", "UNKNOWN"), tags=("warn",))
            self._set_text(self.where_detail, [
                (f"{p.get('status')}\n", "warn"), str(p.get("detail", "no detail")) + "\n\n",
                ("Nothing here is reconstructed from memory. If the plan cannot be read, this "
                 "panel shows MISSING rather than a plan somebody remembers.\n", "dim")])
            self._restore_scroll(tv, _scroll_frac)
            return

        for wdg in (self.where_phase, self.where_next):
            wdg.configure(bg=_GREEN_BG)
        self.where_phase.master.configure(bg=_GREEN_BG)
        cur = _d(p.get("current"))
        nxt = _d(p.get("next_action"))
        self.where_phase.configure(
            text=f"WE ARE IN {cur.get('id')} -- {cur.get('title')}")
        self.where_next.configure(
            text=f"THE SINGLE NEXT ACTION: {nxt.get('text') or 'NOT STATED IN THE PLAN'}\n"
                 f"(which phase: {p.get('current_basis')};  which action: {nxt.get('basis')})")

        con = _d(p.get("contract"))
        nv = con.get("n_violations") or 0
        self.where_hint.configure(
            text=(f"Read live from {p.get('doc')} on every refresh -- nothing on this tab is a "
                  f"copy. {nv} thing(s) the plan does not state are shown as NOT STATED IN THE "
                  f"PLAN rather than filled in; select a phase to see which. "
                  f"{p.get('numbers_joined', 0)} of {p.get('n_phases', 0)} phases also have "
                  f"before/now numbers attached."
                  + _panel_age_text(s.get("ages"), "the plan")),
            fg=_AMBER if nv else _BLUE)

        for i, ph in enumerate(_l(p.get("phases"))):
            ph = _d(ph)
            iid = f"ph{i}"
            self._where_rows[iid] = ph
            st = str(ph.get("status") or "NOT STATED")
            tag = ("good" if st == "DONE" else
                   "bad" if st == "BLOCKED" else
                   "warn" if st in ("NOT STATED", "NOT STARTED") else "dim")
            if st == "IN PROGRESS":
                tag = "good"
            tv.insert("", "end", iid=iid, values=(
                f"{ph.get('id')}  {ph.get('title')}", st,
                ph.get("goal") or "NOT STATED IN THE PLAN",
                ph.get("gate") or "NOT STATED IN THE PLAN",
                ph.get("kill") or "NOT STATED IN THE PLAN",
                _age_cell(ph),
            ), tags=(tag, "even" if i % 2 == 0 else "odd"))
        keep = next((k for k, v in self._where_rows.items()
                     if v.get("id") == p.get("current_id")), None)
        if self._where_rows:
            tv.selection_set(keep or "ph0")
            self._show_where_detail()
        self._restore_scroll(tv, _scroll_frac)   # defect 3
        try:
            self.nb.tab(self.tab_where,
                        text=f"1. WHERE WE ARE ({cur.get('id', '?')})")
        except tk.TclError:
            pass

    def _show_where_detail(self) -> None:
        sel = self.where_tv.selection()
        ph = getattr(self, "_where_rows", {}).get(sel[0]) if sel else None
        if not ph:
            return
        st = str(ph.get("status") or "NOT STATED")
        tag = "good" if st in ("DONE", "IN PROGRESS") else "bad" if st == "BLOCKED" else "warn"
        chunks = [
            (f"{ph.get('id')}  {ph.get('title')}\n", "h"),
            ("WHERE IT IS: ", "dim"), (f"{st}\n", tag),
            (f"(how we know: {ph.get('status_basis')})\n\n", "dim"),
            ("WHAT IT IS FOR\n", "dim"),
            f"{ph.get('goal') or 'The plan states no goal line for this phase.'}\n",
        ]
        if ph.get("brain_structure"):
            chunks += [("\nWHICH PART OF THE BRAIN\n", "dim"), f"{ph.get('brain_structure')}\n"]
        if ph.get("where_it_stands"):
            chunks += [("\nWHERE IT STANDS\n", "dim"), f"{ph.get('where_it_stands')}\n"]

        work = _l(ph.get("work"))
        if work:
            chunks.append(("\nTHE WORK\n", "dim"))
            for w in work:
                w = _d(w)
                if w.get("retracted"):
                    chunks.append((f"  {w.get('n') or '-'}. RETRACTED -- {w.get('text')}\n", "bad"))
                else:
                    chunks.append(f"  {w.get('n') or '-'}. {w.get('text')}\n")
        chunks += [("\nWHAT WOULD COUNT AS SUCCESS\n", "dim"),
                   f"{ph.get('gate') or 'NOT STATED IN THE PLAN'}\n",
                   ("\nWHAT WOULD MAKE US STOP\n", "dim"),
                   f"{ph.get('kill') or 'NOT STATED IN THE PLAN'}\n"]

        num = _d(ph.get("numbers"))
        if num:
            b, n = _d(num.get("before")), _d(num.get("now"))
            chunks += [
                ("\nWHAT MOVED\n", "dim"),
                f"  before ({b.get('when') or 'date not recorded'}): "
                f"{b.get('score') or 'NOT MEASURED'}   floor {b.get('floor') or 'MISSING'} "
                f"= {b.get('floor_name') or 'MISSING'}\n",
                f"  now    ({n.get('when') or 'date not recorded'}): "
                f"{n.get('score') or 'NOT MEASURED'}   floor {n.get('floor') or 'MISSING'} "
                f"= {n.get('floor_name') or 'MISSING'}\n",
                f"  {num.get('what_moved', '')}\n",
            ]
        else:
            chunks.append(("\nNo before/now numbers are recorded against this phase.\n", "dim"))

        for lab in ph.get("missing_labels") or []:
            chunks.append((f"\nTHE PLAN STATES NO '{lab}' FOR THIS PHASE. That cell is shown as "
                           f"NOT STATED rather than filled in, and it is counted in the drift "
                           f"figure at the top of the window. See "
                           f"notes/LONG_TERM_PLAN_PARSER_CONTRACT.md.\n", "bad"))
        if st == "NOT STATED":
            chunks.append(("\nTHE PLAN STATES NO STATUS FOR THIS PHASE. Adding a '**Status:**' "
                           "line to it resolves this; nothing is guessed in the meantime.\n",
                           "warn"))

        chunks += _age_chunks(ph, "WHEN THIS PHASE'S EVIDENCE WAS LAST UPDATED")

        lad = _l(_d(getattr(self, "_where_state", None)).get("ladder"))
        if lad:
            chunks.append(("\nWHAT WOULD COUNT AS THE WHOLE THING WORKING, IN ORDER\n", "dim"))
            for r in lad:
                r = _d(r)
                chunks.append(f"  {r.get('n')}. {r.get('text')}"
                              f"{'   [' + str(r.get('phase')) + ']' if r.get('phase') else ''}\n")
        self._set_text(self.where_detail, chunks)

    # ---- tab 4: SCORES AND FLOORS -------------------------------------
    def _r_scores(self, s: dict) -> None:
        m = _d(s.get("scores"))
        tv = self.sc_tv
        _kept = self._keep_selection(tv)   # defect 3: was hardcoded back to row 0 every refresh
        tv.delete(*tv.get_children())
        self._score_rows: dict[str, dict] = {}
        if m.get("status") != "OK":
            self.sc_gov_title.configure(text=f"SCORE DATA IS {m.get('status', 'MISSING')}")
            self.sc_gov_body.configure(text=str(m.get("detail", ""))[:400])
            self.sc_hint.configure(text="", fg=_AMBER)
            tv.insert("", "end", values=(f"{m.get('status')}", "-", "MISSING", "MISSING", "",
                                         "UNKNOWN"), tags=("warn",))
            self._set_text(self.sc_detail, [
                (f"{m.get('status')}\n", "warn"), str(m.get("detail", "no detail")) + "\n\n",
                ("A blank where a measurement should be is information. This panel shows MISSING "
                 "rather than a number it does not have.\n", "dim")])
            self._restore_scroll(tv, _kept[0])
            return

        gov = _d(m.get("governing_floor"))
        if gov:
            self.sc_gov_title.configure(text=str(gov.get("title", "")))
            body = " ".join(str(x) for x in
                            (gov.get("plain_verdict") or gov.get("plain") or "",
                             gov.get("detail") or "") if x)
            if gov.get("scope"):
                body += f"   SCOPE: {gov.get('scope')}"
            if gov.get("verify_status") in ("CHECK_PLAN", "CHECK_SOURCE"):
                body += ("   [CHECK THE SOURCE: " + ", ".join(gov.get("verify_missing") or [])
                         + " is no longer findable in the plan.]")
            self.sc_gov_body.configure(text=body)
        else:
            self.sc_gov_title.configure(text="NO GOVERNING FLOOR RECORDED")
            self.sc_gov_body.configure(
                text="Nothing names the strongest floor. Read every number below with that gap "
                     "in mind.")

        nr = m.get("n_retracted") or 0
        nd = m.get("n_disagreements") or 0
        as_of = m.get("as_of") or "an unrecorded date"
        self.sc_hint.configure(
            text=(f"One row per part of the machine, as of {as_of}. "
                  f"Every number sits beside the floor it has to beat -- a score with no "
                  f"floor cannot be graded. {nr} claim(s) were RETRACTED and are shown in red at "
                  f"the bottom exactly like a loss, on purpose. {nd} part(s) are reported "
                  f"differently by the two sources that feed this table; those say so rather "
                  f"than one being picked."
                  + _panel_age_text(s.get("ages"), "scores and floors")),
            fg=_AMBER if (nr or nd) else _BLUE)

        i = 0
        for r in _l(m.get("rows")):
            r = _d(r)
            iid = f"sc{i}"
            self._score_rows[iid] = r
            inst_txt, inst_col = _INSTRUMENT_TEXT.get(
                (r.get("instrument") or "").upper(),
                ("not recorded", _AMBER) if r.get("instrument") is None
                else ("unknown", _AMBER))
            stand_txt, stand_col = _STANDING_TEXT.get(r.get("standing") or "UNKNOWN",
                                                      ("not established", _AMBER))
            sep = r.get("separated")
            if sep == "YES":
                stand_txt += " (separated)"
            elif sep == "NO":
                stand_txt += " (not separated)"
            direction = (r.get("direction") or "").upper()
            if direction:
                stand_txt = f"{direction} -- {stand_txt}"
            before, _ = self._side_cell(r.get("before"))
            now, gap = self._side_cell(r.get("now"))
            if gap:
                stand_txt += "  (no floor)"
            if r.get("disagreement"):
                stand_txt += "   [SOURCES DISAGREE]"
            if r.get("verify_status") in ("CHECK_PLAN", "CHECK_SOURCE"):
                stand_txt += "   [CHECK SOURCE]"
            elif r.get("verify_status") == "CANNOT_VERIFY":
                stand_txt += "   [CANNOT VERIFY]"
            tag = ("bad" if (stand_col == _RED or direction in ("DOWN", "WORSE", "NULL"))
                   else "good" if (stand_col == _GREEN or direction in ("UP", "BETTER"))
                   else "warn")
            title = (("HEADLINE  " if r.get("headline") else
                      (f"#{r.get('n')}  " if r.get("n") else "")) + str(r.get("title")))
            tv.insert("", "end", iid=iid,
                      values=(title, inst_txt, before, now, stand_txt, _age_cell(r)),
                      tags=(tag, "even" if i % 2 == 0 else "odd"))
            i += 1

        # RETRACTIONS. Same red, same table, at the bottom where they cannot be missed by a
        # reader who scrolls -- never a separate tab a reader can decline to open.
        for r in _l(m.get("retractions")):
            r = _d(r)
            iid = f"sc{i}"
            r = dict(r, _retracted=True)
            self._score_rows[iid] = r
            before, _ = self._side_cell(r.get("before"))
            now, gap = self._side_cell(r.get("now"))
            tv.insert("", "end", iid=iid,
                      values=(str(r.get("title")), "-", before, now,
                              "RETRACTED" + ("  (no floor)" if gap else ""), _age_cell(r)),
                      tags=("bad", "even" if i % 2 == 0 else "odd"))
            i += 1

        if self._score_rows:
            self._restore_selection(tv, _kept, fallback_iid="sc0",
                                    select_cb=self._show_score_detail)
        else:
            self._restore_scroll(tv, _kept[0])
        try:
            # Base label shortened 2026-08-17 (see the RUNNING tab comment above) -- "retracted"
            # itself must survive; the self-test asserts it is in this exact string.
            self.nb.tab(self.tab_scores,
                        text=f"4. SCORES ({nr} retracted)" if nr else "4. SCORES")
        except tk.TclError:
            pass

    def _show_score_detail(self) -> None:
        sel = self.sc_tv.selection()
        r = getattr(self, "_score_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        stand_txt, stand_col = _STANDING_TEXT.get(r.get("standing") or "UNKNOWN",
                                                  ("not established", _AMBER))
        tag = "bad" if stand_col == _RED else "good" if stand_col == _GREEN else "warn"
        if r.get("_retracted"):
            tag = "bad"
        b, n = _d(r.get("before")), _d(r.get("now"))
        chunks = [(f"{r.get('title')}\n", "h")]
        if r.get("_retracted"):
            chunks.append(("THIS CLAIM WAS RETRACTED.\n", "bad"))
        if r.get("what_it_does"):
            chunks.append(f"{r.get('what_it_does')}\n")
        if r.get("plain") and r.get("plain") != r.get("what_it_does"):
            chunks.append(f"\n{r.get('plain')}\n")
        chunks.append("\n")
        if r.get("instrument"):
            chunks += ["Can we measure this part on its own?  ",
                       (f"{r.get('instrument')}",
                        "good" if r.get("instrument") == "YES" else "warn"),
                       f" -- {r.get('instrument_note', '')}\n\n"]
        chunks += [
            ("BEFORE", "dim"), f"  ({b.get('when') or 'date not recorded'})\n",
            f"   {b.get('score') or 'NOT MEASURED'}"
            f"{'  -- ' + str(b.get('score_detail')) if b.get('score_detail') else ''}\n",
            f"   floor: {b.get('floor') or 'MISSING'}  = {b.get('floor_name') or 'MISSING'}"
            f"{'  (' + str(b.get('floor_detail')) + ')' if b.get('floor_detail') else ''}\n\n",
            ("NOW", "h"), f"  ({n.get('when') or 'date not recorded'})\n",
            f"   {n.get('score') or 'NOT MEASURED'}"
            f"{'  -- ' + str(n.get('score_detail')) if n.get('score_detail') else ''}\n",
            f"   floor: {n.get('floor') or 'MISSING'}  = {n.get('floor_name') or 'MISSING'}"
            f"{'  (' + str(n.get('floor_detail')) + ')' if n.get('floor_detail') else ''}\n",
        ]
        if n.get("floor_superseded_by"):
            chunks.append((f"   {n.get('floor_superseded_by')}\n", "bad"))
        chunks.append("\n")
        if r.get("standing"):
            chunks += [("VERDICT: ", "dim"), (f"{stand_txt}", tag),
                       f"   intervals separated: {r.get('separated')}\n"]
        if r.get("plain_verdict"):
            chunks.append((f"{r.get('plain_verdict')}\n", tag))
        if r.get("what_moved"):
            chunks += [("\nWHAT MOVED\n", "dim"), f"{r.get('what_moved')}\n"]
        if r.get("disagreement"):
            chunks += [("\nTHE TWO SOURCES DISAGREE ABOUT THIS PART\n", "warn"),
                       f"{r.get('disagreement')}\n"]
        chunks += _age_chunks(r)
        chunks.append((f"\nevidence: {r.get('evidence', '')}\n", "mono"))
        if r.get("instrument_evidence"):
            chunks.append((f"instrument: {r.get('instrument_evidence')}\n", "mono"))
        if r.get("sources"):
            chunks.append((f"assembled from: {', '.join(r.get('sources'))}\n", "mono"))
        if r.get("verify_status") in ("CHECK_PLAN", "CHECK_SOURCE"):
            chunks.append(("\nCHECK THE SOURCE: these numbers are no longer findable in the plan "
                           f"or status documents: {r.get('verify_missing')}. Those documents are "
                           "the authority; this row may be stale.\n", "bad"))
        elif r.get("verify_status") == "CANNOT_VERIFY":
            chunks.append(("\nCannot cross-check this row: its authority document was not "
                           "readable. That is NOT the same as verified.\n", "warn"))
        self._set_text(self.sc_detail, chunks)

    # ---- shared by the score cells ------------------------------------
    @staticmethod
    def _side_cell(side) -> tuple[str, bool]:
        """One before/now cell: the score AND the floor, or an explicit non-answer.

        Returns (text, floor_missing). THE RULE: a score is never rendered alone. If a row states
        a score and no floor, this returns the score with 'NO FLOOR STATED' beside it and flags
        it, because a score with no floor beside it cannot be graded and saying so is the useful
        output."""
        d = _d(side)
        score = d.get("score")
        floor = d.get("floor")
        fname = d.get("floor_name") or ""
        if not score:
            return (d.get("score_detail") or "NOT MEASURED"), False
        if floor:
            return f"{score}   vs floor {floor}" + (f" ({fname})" if fname else ""), False
        if fname and ("NOT APPLICABLE" in fname.upper() or "NOT MEASURED" in fname.upper()
                      or "NONE" in fname.upper() or "NOT YET" in fname.upper()
                      or "NOT REACHED" in fname.upper() or "NOT ESTABLISHED" in fname.upper()):
            return f"{score}   ({fname})", False
        return f"{score}   NO FLOOR STATED", True


    # ---- panel B ------------------------------------------------------
    def _r_organs(self, s: dict) -> None:
        o = _d(s.get("organs"))
        tv = self.organ_tv
        _kept = self._keep_selection(tv)   # defect 3: was hardcoded back to row 0 every refresh
        tv.delete(*tv.get_children())
        self._organ_rows: dict[str, dict] = {}
        if o.get("status") != "OK":
            self.organ_hint.configure(text=f"{o.get('status')}: {o.get('detail', '')}", fg=_AMBER)
            tv.insert("", "end", values=(f"{o.get('status')}", "MISSING", "?", "?", "MISSING",
                                         "UNKNOWN"), tags=("warn",))
            self._set_text(self.organ_detail,
                           [(f"{o.get('status')}\n", "warn"), str(o.get("detail", ""))])
            self._restore_scroll(tv, _kept[0])
            return
        reg = _d(o.get("registry"))
        self.organ_hint.configure(
            text=(f"{o.get('n_organs')} organs -- {o.get('n_from_map')} from the organ map, "
                  f"{o.get('n_overlay')} built or measured since it was last written. "
                  f"{o.get('n_missing')} are NOT BUILT. "
                  f"{reg.get('n_brain_structure')} of {reg.get('n_rows')} entries in the "
                  f"capability list name a part of the brain; "
                  f"{reg.get('n_no_brain_structure')} deliberately do not, and filling those in "
                  f"after the fact is banned -- so the backlog is shown rather than hidden."
                  + _panel_age_text(s.get("ages"), "brain organ map")),
            fg=_BLUE)
        n_conf = o.get("n_conflicts") or 0
        if n_conf:
            self.organ_hint.configure(
                text=self.organ_hint.cget("text") +
                     f"   {n_conf} organ(s) are marked CONFLICT: section 10 of the map re-audited "
                     f"them and section 4 was never updated, so the document asserts BOTH a "
                     f"floored result AND untested about the same organ. This panel reports the "
                     f"disagreement instead of picking one.", fg=_AMBER)
        if o.get("missing_required"):
            self.organ_hint.configure(
                text=self.organ_hint.cget("text") +
                     f"   MISSING FROM THE SOURCES: {o.get('missing_required')}", fg=_RED)

        for i, r in enumerate(_l(o.get("rows"))):
            r = _d(r)
            iid = f"o{i}"
            self._organ_rows[iid] = r
            built = r.get("built_short") or "?"
            state = str(r.get("state") or "NOT STATED")
            su = state.upper()
            if built == "NO" or su.startswith("MISSING"):
                tag = "bad"
            elif su in ("SWITCHED ON", "WIRED"):
                tag = "good"
            else:
                tag = "warn"
            if r.get("has_conflict"):
                tag = "warn"
            brain = r.get("brain_structure") or "NOT NAMED"
            organ = f"{r.get('id', '?')}  {r.get('plain_name') or r.get('title') or '?'}"
            measured = str(r.get("measured") or "")
            if r.get("floor_named") is False and r.get("source") == "ORGAN_MAP":
                measured = "NO FLOOR -- " + measured
            tv.insert("", "end", iid=iid,
                      values=(organ, str(brain)[:120], built, state, measured, _age_cell(r)),
                      tags=(tag, "even" if i % 2 == 0 else "odd"))
        if self._organ_rows:
            self._restore_selection(tv, _kept, fallback_iid="o0",
                                    select_cb=self._show_organ_detail)
        else:
            self._restore_scroll(tv, _kept[0])
        try:
            self.nb.tab(self.tab_organs, text=f"5. ORGAN MAP ({o.get('n_missing')} missing)")
        except tk.TclError:
            pass

    def _show_organ_detail(self) -> None:
        sel = self.organ_tv.selection()
        r = getattr(self, "_organ_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        built = r.get("built_short")
        tag = "bad" if built == "NO" else "good" if built == "YES" else "warn"
        chunks = [(f"{r.get('id')}  {r.get('plain_name') or r.get('title')}\n", "h")]
        if r.get("title") and r.get("title") != r.get("plain_name"):
            chunks.append((f"{r.get('title')}\n", "dim"))
        chunks.append("\n")
        chunks += [("THE PART OF THE BRAIN\n", "dim")]
        if r.get("brain_structure"):
            chunks.append(f"{r.get('brain_structure')}\n")
        else:
            chunks.append(("NOT NAMED. No brain structure is recorded for this organ, and one "
                           "is NOT invented here.\n", "warn"))
        if r.get("brain_structure_source"):
            chunks.append((f"(named in {r.get('brain_structure_source')})\n", "mono"))
        if r.get("brain_plain"):
            chunks += [("\nWHAT IT DOES IN THE BRAIN\n", "dim"), f"{r.get('brain_plain')}\n"]
        else:
            chunks.append(("\nNo plain-language summary written yet for this organ.\n", "dim"))
        if r.get("brain_math_pinned") is False:
            chunks.append(("\nThe science does NOT pin down the equation for this one, so its "
                           "fidelity cannot be scored at all. That is a finding about the state "
                           "of neuroscience, not a hole to fill with something plausible.\n",
                           "warn"))
        chunks += [("\nHAVE WE BUILT IT: ", "dim"), (f"{r.get('built')}\n", tag),
                   ("IS IT SWITCHED ON: ", "dim"), f"{r.get('state')}\n"]
        if r.get("state_detail"):
            chunks.append((f"{r.get('state_detail')}\n", "mono"))
        if r.get("module"):
            chunks.append((f"our module: hdlab/{r.get('module')}\n", "mono"))
        elif r.get("ours"):
            chunks.append((f"ours: {str(r.get('ours'))[:400]}\n", "mono"))
        chunks += [("\nWHAT IT MEASURES\n", "dim"), f"{r.get('measured')}\n"]
        for c in _l(r.get("conflicts")):
            c = _d(c)
            chunks += [("\nTHE MAP CONTRADICTS ITSELF ABOUT THIS ORGAN\n", "bad"),
                       f"on: {c.get('axis')}\n",
                       f"  it says: {c.get('says_a')}\n",
                       f"  and also: {c.get('says_b')}\n",
                       (f"  why: {c.get('why')}. Both readings are shown because picking one "
                        f"would be a fabrication in whichever direction this code happened to "
                        f"fall. The raw sentence is below -- adjudicate it there.\n", "dim")]
        if r.get("evidence"):
            chunks.append((f"{str(r.get('evidence'))[:900]}\n", "mono"))
        if r.get("evidence_field") == "WIRED note":
            chunks.append(("(that evidence is recorded in the map's wiring note, not in a "
                           "separate evidence line)\n", "dim"))
        if r.get("the_honest_part"):
            chunks += [("\nTHE HONEST PART\n", "warn"), f"{r.get('the_honest_part')}\n"]
        if r.get("has_registry_row") is False:
            chunks.append(("\nThis module has NO entry in the capability list at all, so the "
                           "keep-it-or-shelve-it decision has never been applied to it.\n", "bad"))
        if r.get("blocks"):
            chunks += [("\nWHAT IT HOLDS UP: ", "dim"), f"{r.get('blocks')}\n"]
        if r.get("verify_status") == "CHECK_SOURCE":
            chunks.append((f"\nCHECK THE SOURCE: {r.get('verify_missing')} no longer findable.\n",
                           "bad"))
        chunks += _age_chunks(r, "WHEN THIS ORGAN'S EVIDENCE WAS LAST UPDATED")
        self._set_text(self.organ_detail, chunks)

    # ---- panel C ------------------------------------------------------
    def _r_fidelity(self, s: dict) -> None:
        fd = _d(s.get("fidelity"))
        tv, tv2 = self.fid_tv, self.fid_div_tv
        _kept1 = self._keep_selection(tv)    # defect 3
        _kept2 = self._keep_selection(tv2)
        tv.delete(*tv.get_children())
        tv2.delete(*tv2.get_children())
        self._fid_rows: dict[str, dict] = {}
        self._fid_div: dict[str, dict] = {}
        # Stashed for the detail box, which needs the panel-level warning alongside a single row.
        # Taken from the payload just rendered rather than from self._state, so a direct render()
        # (as the self-test does) is not a different code path from the live one.
        self._fid_state: dict = fd
        if fd.get("status") == "MISSING":
            self.fid_head.configure(text="HOW CLOSELY WE COPY THE BRAIN: MISSING")
            self.fid_warn.configure(text=str(fd.get("detail", ""))[:500])
            self.fid_scatter_cap.configure(text="")
            self._draw_scatter()
            tv.insert("", "end", values=("MISSING", "MISSING", str(fd.get("detail", ""))[:120],
                                         "UNKNOWN"), tags=("warn",))
            self._set_text(self.fid_detail, [("MISSING\n", "warn"), str(fd.get("detail", ""))])
            self._restore_scroll(tv, _kept1[0])
            self._restore_scroll(tv2, _kept2[0])
            return

        # THE BANNER. Three clauses, each separately true, replacing an unscoped general negative:
        #   1. UNVALIDATED AS A PREDICTOR AT OUR CURRENT LOW FIDELITY
        #   2. EXPECTED TO BECOME PREDICTIVE AS FIDELITY RISES  (the OWNER'S argument, named as one)
        #   3. NOT USABLE AS A PERFORMANCE CLAIM TODAY          (unchanged, and it is the gate)
        # The tool's own VALIDATION_VERDICT is still carried VERBATIM below them, so if the tool
        # ever changes its mind the panel changes with it rather than repeating a typed sentence.
        fr = _d(fd.get("framing"))
        self.fid_head.configure(
            text=str(fr.get("verdict_line")
                     or "UNVALIDATED AS A PREDICTOR AT OUR CURRENT LOW FIDELITY."))
        body = [
            str(fr.get("what_it_is") or fd.get("headline") or ""),
            str(fr.get("why_unvalidated") or ""),
            str(fr.get("the_correction") or ""),
            str(fr.get("owner_argument") or ""),
            str(fr.get("still_true_today") or ""),
        ]
        misses = _l(fr.get("named_misses"))
        if misses:
            body.append("THE TWO MISSES, KEPT ON SCREEN: "
                        + "; and ".join(str(m) for m in misses) + ".  "
                        + str(fr.get("counter_evidence_note") or ""))
        body.append(str(fr.get("system_text") or ""))
        body.append(str(fr.get("two_populations_warning") or ""))
        body.append("THE SCORING TOOL'S OWN VERDICT, VERBATIM: "
                    + str(fd.get("validation_verdict") or ""))
        stale = _l(fd.get("drifted"))
        if stale:
            body.insert(0, f"CHECK THIS BANNER: {len(stale)} of the statements below "
                            f"({', '.join(str(x) for x in stale)}) no longer hold when recomputed "
                            f"from the scoring tool. They are re-derived every refresh precisely "
                            f"so this cannot pass unnoticed.")
        cc = _l(fd.get("cannot_check"))
        if cc:
            body.append(f"{len(cc)} statement(s) could not be re-checked on this refresh "
                        f"({', '.join(str(x) for x in cc)}) -- that is NOT the same as verified.")
        self.fid_warn.configure(text="\n\n".join(b for b in body if b))

        self._draw_scatter()
        self._r_scatter_caption(fd)

        for i, r in enumerate(_l(fd.get("rows"))):
            r = _d(r)
            iid = f"f{i}"
            self._fid_rows[iid] = r
            pct = r.get("pct")
            pct_s = (f"{pct * 100:.0f}%  ({r.get('points')} of {r.get('max')})"
                     if isinstance(pct, (int, float)) else "not scored")
            outcome = str(r.get("outcome") or "")
            # Colour by the OUTCOME, never by the fidelity score. Colouring by the score would
            # imply the score means something about the result -- and that is the claim this panel
            # says we have too little evidence to make either way.
            tag = "good" if r.get("held") else "bad"
            tv.insert("", "end", iid=iid,
                      values=(str(r.get("component") or "?"), pct_s, outcome[:220], _age_cell(r)),
                      tags=(tag, "even" if i % 2 == 0 else "odd"))

        for i, r in enumerate(_l(fd.get("divergence"))):
            r = _d(r)
            iid = f"dv{i}"
            self._fid_div[iid] = r
            pinned = r.get("pinned")
            pin_s = ("yes, the equation is pinned" if pinned is True
                     else "NO -- the science does not pin it" if pinned is False
                     else "not stated")
            bad = any(str(v).upper().startswith(("DIVERGES", "NOT BUILT"))
                      for v in (r.get("shape"), r.get("position"), r.get("metric")))
            tag = "bad" if bad else ("good" if r.get("class") == "SAME" else "warn")
            tv2.insert("", "end", iid=iid,
                       values=(f"{r.get('id')}  {r.get('title')}", r.get("shape"),
                               r.get("position"), r.get("metric"), pin_s, _age_cell(r)),
                       tags=(tag, "even" if i % 2 == 0 else "odd"))
        if not _l(fd.get("divergence")):
            tv2.insert("", "end", values=(str(fd.get("divergence_detail")
                                              or "the organ map is not readable -- MISSING"),
                                          "", "", "", "", "UNKNOWN"), tags=("warn",))
        if self._fid_rows:
            self._restore_selection(tv, _kept1, fallback_iid="f0",
                                    select_cb=self._show_fidelity_detail)
        else:
            self._restore_scroll(tv, _kept1[0])
        self._restore_selection(tv2, _kept2, fallback_iid=None,
                                select_cb=lambda: self._show_fidelity_detail(True))
        try:
            self.nb.tab(self.tab_fidelity,
                        text=f"6. COPYING THE BRAIN ({_d(fd.get('scatter')).get('n', '?')} pts)")
        except tk.TclError:
            pass

    def _show_fidelity_detail(self, from_div: bool = False) -> None:
        st = _d(getattr(self, "_fid_state", None))
        if from_div:
            sel = self.fid_div_tv.selection()
            r = getattr(self, "_fid_div", {}).get(sel[0]) if sel else None
            if not r:
                return
            self._set_text(self.fid_detail, [
                (f"{r.get('id')}  {r.get('title')}\n", "h"),
                (f"{r.get('map_title', '')}\n", "dim"),
                f"\n{r.get('plain', '')}\n\n",
                ("Is it the same operation?  ", "dim"), f"{r.get('shape')}\n",
                ("Is it in the right place in the pipeline?  ", "dim"), f"{r.get('position')}\n",
                ("Is it judged the way the brain judges it?  ", "dim"), f"{r.get('metric')}\n\n",
                (f"the organ map's own verdict: {r.get('class')}\n", "mono"),
                ("\nNone of this says whether the organ WORKS. It says how closely it resembles "
                 "the biology. Those are two different gates and neither can soften the other.\n",
                 "warn"),
            ] + _age_chunks(r, "WHEN THIS ORGAN'S VERDICT WAS LAST UPDATED"))
            return
        sel = self.fid_tv.selection()
        r = getattr(self, "_fid_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        pct = r.get("pct")
        chunks = [
            (f"{r.get('component')}\n", "h"),
            ("HOW CLOSELY WE COPY THE BRAIN: ", "dim"),
            (f"{pct * 100:.0f}%" if isinstance(pct, (int, float)) else "not scored", "h"),
            f"   ({r.get('points')} of {r.get('max')} points, over {r.get('n_scorable')} "
            f"scorable aspects)\n\n",
            ("WHAT ACTUALLY HAPPENED WHEN IT WAS MEASURED\n", "warn"),
            f"{r.get('outcome')}\n",
            (f"{r.get('outcome_source', '')}\n", "mono"),
        ]
        if r.get("regime_or_pairing_zero"):
            chunks.append(("\nThis one is flagged: it was measured at an operating point where "
                           "the thing being tested could not show an effect, or its matched "
                           "partner organ does not exist.\n", "warn"))
        if r.get("dimensions"):
            chunks.append((f"\nper-aspect scores: {r.get('dimensions')}\n", "mono"))
        chunks += _age_chunks(r, "WHEN THIS POINT'S EVIDENCE WAS LAST UPDATED")
        # HEADING CORRECTED 2026-08-16. It read "WHY THIS NUMBER MUST NOT BE READ AS A PREDICTION",
        # which is an unscoped general negative -- and six points with one positive cannot support
        # one. What IS supported is that we have too little evidence to tell, and that the number
        # may not be used as a performance claim today. Both of those are said instead.
        fr2 = _d(st.get("framing"))
        chunks += [("\nHOW FAR THIS NUMBER MAY BE READ\n", "warn"),
                   f"{fr2.get('why_unvalidated', '')}\n",
                   (f"{fr2.get('the_correction', '')}\n", "warn"),
                   (f"{fr2.get('still_true_today', '')}\n", "bad"),
                   ("\nTHE SCORING TOOL'S OWN VERDICT, VERBATIM\n", "dim"),
                   f"{st.get('validation_verdict', '')}\n"]
        for c in _l(st.get("claims")):
            c = _d(c)
            holds = c.get("holds")
            mark = ("still holds" if holds is True else
                    "NO LONGER HOLDS -- this banner line is stale" if holds is False else
                    "CANNOT BE CHECKED on this refresh, which is not the same as verified")
            chunks.append((f"  [{c.get('id')}] {c.get('text')} -- {mark}\n",
                           "dim" if holds is True else "bad" if holds is False else "warn"))
        if st.get("was_anything_tuned"):
            chunks += [("\nWAS ANYTHING TUNED TO MAKE THIS LOOK BETTER?\n", "dim"),
                       f"{st.get('was_anything_tuned')}\n"]
        if st.get("unscored_is_the_finding"):
            chunks += [("\nWHAT COULD NOT BE SCORED AT ALL\n", "dim"),
                       f"{st.get('unscored_is_the_finding')}\n"]
        chunks.append((f"\n{st.get('n_registry_with_basis')} of {st.get('n_registry_rows')} "
                       f"capability entries record whether their design choice is pinned by "
                       f"evidence or is our own invention under test; "
                       f"{st.get('n_registry_backlog')} do not, and filling those in after the "
                       f"fact is banned.\n", "mono"))
        self._set_text(self.fid_detail, chunks)

    # ---- tab 3: WAITING ON YOU ----------------------------------------
    def _board_engaged(self) -> bool:
        """True while the owner is reading or composing on this tab, per the owner's own standard:
        "if a row is selected, or the answer box has focus, or the answer box has unsaved text, the
        question/answer panes MUST NOT be rebuilt by the refresh timer." While this is True,
        `_r_board` must not touch the table, the detail pane, or the answer box, because even an
        identical rebuild resets the text cursor and any scroll/selection state.

        DELIBERATELY UNCONDITIONAL ON *WHY* A ROW IS SELECTED -- an earlier version of this pass
        tried to distinguish "the owner clicked this" from "this window auto-picked it for
        convenience" so a fresh, never-touched tab would not freeze forever. That distinction
        needed to know WHICH selection-set call the live `<<TreeviewSelect>>` event belonged to,
        and `tv.selection_set()` only QUEUES that event -- on the real, event-pumped window
        (unlike this file's own self-test, which never calls `root.update()`) it can fire AFTER a
        same-turn boolean suppression flag had already reset, misattributing an internal pick to
        the owner. Rather than chase that race further, this reverts to the plain, literal rule:
        ANY selection freezes the tab, full stop. The escape valve is the "new data available"
        hint (`board_new_data_lbl`), which always stays live and gives the owner an explicit,
        one-click way to pull fresh data -- so nothing is ever silently lost, only held until they
        ask for it."""
        try:
            if self.board_tv.selection():
                return True
        except tk.TclError:
            pass
        try:
            if self.root.focus_get() is self.answer_box:
                return True
        except (tk.TclError, KeyError):
            pass
        try:
            if self.answer_box.get("1.0", "end").strip():
                return True
        except tk.TclError:
            pass
        return False

    @staticmethod
    def _board_snapshot(s: dict) -> str:
        """A cheap fingerprint of the data this tab renders, so the "new data available" hint
        only lights up when something actually changed -- not on every 20s tick regardless.

        VOLATILE AGE FIELDS ARE STRIPPED FIRST (found live: without this, the hint lit on nearly
        every tick even though nothing meaningful had changed). Every row's `evidence_age` carries
        `age_s`, recomputed as `time.time() - artifact_mtime` on EVERY collection -- it drifts on
        its own even when the artifact has not been touched, so it is not evidence of new data,
        only of time passing. `rel` (its bucketed text, e.g. "just now") is stripped for the same
        reason: it can flip on a bucket boundary from the clock alone. `ts`/`when`/`when_utc` are
        kept -- those are deterministic functions of the artifact's own mtime and DO change when
        the artifact genuinely does."""
        try:
            payload = _strip_volatile_ages({"board": _d(s.get("board")), "plan": _d(s.get("plan"))})
            return json.dumps(payload, sort_keys=True, default=str)
        except (TypeError, ValueError):
            return repr((s.get("board"), s.get("plan")))

    def _board_update_new_data_hint(self, s: dict) -> None:
        key = self._board_snapshot(s)
        if key == getattr(self, "_board_rendered_snapshot", None):
            return   # the incoming payload is identical to what is already on screen -- say nothing
        try:
            self.board_new_data_lbl.configure(
                text="NEW BOARD DATA ARRIVED WHILE YOU WERE READING OR ANSWERING -- this tab is "
                     "frozen ON PURPOSE so nothing moves under you. Click here to load it now.")
            self.board_new_data_lbl.grid()
        except tk.TclError:
            pass

    def _board_clear_new_data_hint(self) -> None:
        try:
            self.board_new_data_lbl.configure(text="")
            self.board_new_data_lbl.grid_remove()
        except tk.TclError:
            pass

    def _board_force_refresh(self, _evt=None) -> None:
        """The new-data hint's click target: the ONE way this tab's automatic freeze is lifted --
        an explicit, owner-initiated pull of whatever arrived most recently, never automatic."""
        s = getattr(self, "_board_last_state", None)
        if s is not None:
            self._r_board_apply(s)
        self._board_clear_new_data_hint()

    def _r_board(self, s: dict) -> None:
        """Entry point for EVERY refresh of this tab -- the 20s auto timer, F5, and the post-Save
        refresh all land here.

        DEFECT B (third report, 2026-08-17 evening): *"I can barely use the question/answer tab...
        every once in a while the text jumps."* Traced to THIS function: on every refresh it
        unconditionally deleted and reinserted the table, and (by re-selecting the same row through
        `tv.selection_set`, which fires `<<TreeviewSelect>>` even when the selection does not
        change) re-ran `_show_board_detail`, which reloads the answer box from its draft via
        `delete` + `insert`. The CONTENT after that round-trip is identical, but the delete+insert
        resets the text cursor to the end -- invisible in a diff, very visible to someone mid-
        sentence, and it is what "the text jumps" was describing. The two prior passes never looked
        here because they were both diagnosing the LAYOUT (why the pane was unreadably small), not
        the REBUILD (why something the owner was not touching kept resetting) -- both defects were
        real and neither fix touched the other's cause.

        THE FIX: if the owner is ENGAGED (a row selected, the answer box focused, or the box holds
        unsaved text -- see `_board_engaged`), this function does not touch the table, the detail
        pane, or the answer box AT ALL, not even to "restore" anything, because nothing was moved
        in the first place. It only lights the small `board_new_data_lbl` hint if the incoming data
        actually differs from what is on screen, and remembers the payload in `_board_last_state`
        so an explicit disengage (Save, or clicking the hint) always applies the freshest data
        received meanwhile -- nothing is ever lost, only held."""
        self._board_last_state = s
        if self._board_engaged():
            self._board_update_new_data_hint(s)
            return
        self._board_clear_new_data_hint()
        self._r_board_apply(s)

    def _r_board_apply(self, s: dict) -> None:
        """The actual rebuild, run only when `_r_board` has established the owner is NOT engaged
        with this tab -- see that method's docstring for why the split exists."""
        b = _d(s.get("board"))
        pl = _d(s.get("plan"))
        self._board_state = b
        tv = self.board_tv
        _scroll_frac = self._keep_scroll(tv)   # defect 3: restored at the end of this function
        tv.delete(*tv.get_children())
        self._board_rows = [_d(r) for r in _l(b.get("open"))]
        self._wait_rows: dict[str, dict] = {}

        decisions = _l(pl.get("decisions")) if pl.get("status") == "OK" else []
        ops = _d(pl.get("operator"))
        standing = _l(ops.get("rows")) if ops.get("status") == "OK" else []
        n_q = b.get("n_open") or 0
        n_all = n_q + len(decisions) + len(standing)
        try:
            self.nb.tab(self.tab_board, text=f"3. WAITING ON YOU ({n_all})" if n_all else
                                             "3. WAITING ON YOU")
        except tk.TclError:
            pass

        # THE BANNER STATES THE BREAKDOWN IN ONE SENTENCE, in the largest text on the tab, before
        # the table below is even scanned. "0 open questions" reads as nothing to do UNLESS the
        # decisions and standing items are named in the same breath -- they are what was actually
        # missed on 2026-08-17.
        if b.get("status") != "OK":
            self.wait_count_lbl.configure(
                text="THE BOARD COULD NOT BE READ -- see the line below.", bg=_RED_BG)
            self.wait_banner.configure(bg=_RED_BG)
        elif n_all == 0:
            self.wait_count_lbl.configure(
                text="NOTHING IS WAITING ON YOU. No open questions, no undecided items.",
                bg=_GREEN_BG)
            self.wait_banner.configure(bg=_GREEN_BG)
        else:
            # SHORTENED 2026-08-17 (third pass, defect A -- vertical space). This used to end
            # "-- click any row, type an answer, press Save.", which pushed the sentence past one
            # line at 13pt bold on the owner's real window width, measured live: the banner alone
            # cost 64px (two lines) of a tab that only has ~441px total, most of which needs to go
            # to the reading pane. That instruction is not lost -- it is exactly what the table's
            # own heading column now says ("click a row to read it in full below").
            self.wait_count_lbl.configure(
                text=(f"{n_q} OPEN QUESTION{'S' if n_q != 1 else ''}  +  {len(decisions)} "
                      f"DECISION{'S' if len(decisions) != 1 else ''}  +  {len(standing)} "
                      f"STANDING ITEM{'S' if len(standing) != 1 else ''}  =  {n_all} "
                      f"ROW{'S' if n_all != 1 else ''} WAITING ON YOU"),
                bg="#26415c")
            self.wait_banner.configure(bg="#26415c")

        # Whether the DOCUMENT can be written at all. Whether the SELECTED ROW can be written is a
        # separate question and is decided in _sync_answer_ui() -- conflating the two is what left
        # the Save button enabled over a row it could never write.
        self._board_writable = bool(b.get("status") == "OK" and b.get("writable") is not False)
        # SHORTENED 2026-08-17 (part of the defect-1 layout fix). This used to be a 3-sentence,
        # ~550-character paragraph that alone consumed ~130px of the ~260px this tab's PanedWindow
        # actually has to share between the table, the detail box and the answer box (measured
        # live) -- pushing the Save button off the bottom of the window was not fixable by the
        # PanedWindow alone while this much fixed prose sat above it. Everything it used to say is
        # NOT lost: the per-kind explanation ("a DECISION answer is recorded as its own new row...")
        # already lives in `_show_board_detail()`'s DECISION/STANDING branches, read once a row is
        # actually selected -- which is where the owner needs it, not repeated on every refresh
        # above a table they are trying to read.
        parts = []
        if b.get("status") != "OK":
            parts.append(f"THE BOARD IS {b.get('status')}: {b.get('detail', '')}")
        elif b.get("writable") is False:
            parts.append("notes/BOARD.md is not writable from here -- answer it in the file.")
            self.answer_status.configure(
                text="notes/BOARD.md is not writable from here -- answer it in the file "
                     "instead.", fg=_AMBER)
        parts.append(_panel_age_text(s.get("ages"), "waiting on you").strip())
        self.board_hint.configure(text="  ".join(x for x in parts if x),
                                  fg=_AMBER if b.get("status") != "OK" else _BLUE)

        # NO PLACEHOLDER ROW (removed 2026-08-17). A row reading "No open question", unselectable
        # and carrying id "-", used to be drawn here whenever BOARD.md had zero open QUESTIONS --
        # which is most of the time, since a question leaves this list the moment it is answered.
        # That row was the entire reproduction of *"the questions tab now only appears to have one
        # question, and no way for me to select a new one"*: it was the only row literally kind
        # QUESTION, it could not be clicked (it is not in `self._wait_rows`, so selecting it makes
        # `_show_board_detail` return immediately and nothing on screen changes), and it sat above
        # eleven real, answerable DECISION/STANDING rows that do not say "question" anywhere in
        # their text. The "0 open questions" fact still needs to be said -- it now lives in the
        # banner above, worded together with the count of decisions and standing items so it never
        # again reads as "there is nothing here."
        # THE "question" CELL CARRIES A GIST, NOT THE FULL TEXT (2026-08-17, third pass on this
        # tab -- see `_gist`). A Treeview cell clips silently at its pixel width; the owner's
        # "I can't read any of the question text" traced to the FULL text (up to 859 characters
        # measured live) being stuffed into this cell with no wrap and no visible sign anything was
        # cut off. The full text is unchanged and unabridged in the reading pane below, once a row
        # is selected -- see `_show_board_detail`.
        i = 0
        # ARCHIVE MODE (owner 2026-08-20): show ONLY what is settled, newest first, and nothing
        # that is still waiting. The two views are mutually exclusive on purpose -- the complaint
        # was that answered rows were cluttering the working list, so a mode that shows both would
        # not fix anything.
        if getattr(self, "board_archive", False):
            for j, r in enumerate(_l(b.get("answered"))):
                r = _d(r)
                iid = f"a{j}"
                self._wait_rows[iid] = dict(r, _kind="ANSWERED")
                tv.insert("", "end", iid=iid,
                          values=(r.get("id", "?"), "ANSWERED",
                                  _gist(r.get("question", "")),
                                  "you answered: " + _verbatim(str(r.get("answer") or ""), 120),
                                  str(r.get("resolved") or r.get("asked") or "")[:19]),
                          tags=("good", "even" if i % 2 == 0 else "odd"))
                i += 1
            # ...and the DECISION / STANDING rows that already carry an answer. Owner 2026-08-20:
            # *"I did answer d6 but I don't think those legacy questions are working properly...
            # they are all legacy and need to be removed."* The answer HAD stuck (D6 -> Q81,
            # "Yes - merge this branch to main"); the defect was that an answered decision kept
            # sitting in the WAITING-ON-YOU list, so answering it changed nothing the owner could
            # see. Settled rows belong here, in the archive, not in the working list.
            rec_a = _d(b.get("recorded"))
            for grp, kind in ((_l((s.get("plan") or {}).get("decisions")), "DECISION"),
                              (_l((s.get("plan") or {}).get("standing")), "STANDING")):
                for r in grp:
                    r = _d(r)
                    done = _d(rec_a.get(str(r.get("id") or "").upper()))
                    if not done:
                        continue
                    iid = "z%s" % r.get("id")
                    self._wait_rows[iid] = dict(r, _kind="ANSWERED",
                                                answer=done.get("answer"),
                                                resolved=done.get("resolved"))
                    tv.insert("", "end", iid=iid,
                              values=(r.get("id", "?"), "%s - ANSWERED" % kind,
                                      _gist(r.get("question", "")),
                                      "you answered: " + _verbatim(str(done.get("answer") or ""),
                                                                   120),
                                      str(done.get("resolved") or "")[:19]),
                              tags=("good", "even" if i % 2 == 0 else "odd"))
                    i += 1
            self._update_board_mode_label()
            return

        for j, r in enumerate(self._board_rows):
            iid = f"q{j}"
            self._wait_rows[iid] = dict(r, _kind="QUESTION")
            tv.insert("", "end", iid=iid,
                      values=(r.get("id", "?"), "QUESTION (answerable here)",
                              _gist(r.get("question", "")), "it stays open", _age_cell(r)),
                      tags=("warn", "even" if i % 2 == 0 else "odd"))
            i += 1
        # WHICH OF THESE THE OWNER HAS ALREADY ANSWERED, read back out of notes/BOARD.md. A panel
        # that keeps presenting a settled decision as outstanding is the same defect as a stale
        # RUNNING row: it is read as evidence and it is wrong.
        recorded = _d(b.get("recorded"))
        for d in decisions:
            d = _d(d)
            iid = f"d{d.get('id')}"
            done = _d(recorded.get(str(d.get("id") or "").upper()))
            # ANSWERED ROWS LEAVE THE WORKING LIST (owner 2026-08-20). They are in the archive.
            # Leaving them here is what made answering D6 feel like it "did not work": the answer
            # was recorded correctly, and the row stayed exactly where it was.
            #
            # `_wait_rows` IS REGISTERED **AFTER** THIS SKIP, NEVER BEFORE IT (fixed 2026-08-21,
            # found by verification/test_settled_rows_leave_the_working_list.py on its first run).
            # Registering first left `_wait_rows` claiming a row the Treeview had never been given,
            # and the two are read together 50 lines below: the selection-restore looks `keep` up in
            # `_wait_rows` and hands it to `tv.selection_set()`, which raises
            # `TclError: Item dD1 not found` and takes the WHOLE PANEL REFRESH down with it.
            # Reachable by the owner's ordinary workflow -- select a decision, answer it, wait for
            # the next 20 s refresh -- which is when the row disappears while still selected.
            if done:
                continue
            self._wait_rows[iid] = dict(d, _kind="DECISION")
            tv.insert("", "end", iid=iid,
                      values=(d.get("id", "?"),
                              "DECISION - ANSWERED" if done else "DECISION (answerable here)",
                              _gist(d.get("question", "")),
                              ("you answered: " + _verbatim(str(done.get("answer") or ""), 120))
                              if done else
                              ("the default happens: " + str(d.get("default") or "NONE STATED")),
                              _age_cell(d)),
                      tags=("good" if done else "dim", "even" if i % 2 == 0 else "odd"))
            i += 1
        for o in standing:
            o = _d(o)
            iid = f"o{o.get('id')}"
            drift = ("   [CHECK SOURCE]"
                     if o.get("verify_status") == "CHECK_SOURCE" else "")
            done = _d(recorded.get(str(o.get("id") or "").upper()))
            if done:                       # answered -> the archive, not the working list
                continue
            # AFTER the skip, for the same reason as the DECISION branch above: a `_wait_rows` entry
            # with no matching Treeview item crashes the selection-restore and kills the refresh.
            self._wait_rows[iid] = dict(o, _kind="STANDING")
            tv.insert("", "end", iid=iid,
                      values=(o.get("id", "?"),
                              "STANDING - ANSWERED" if done else "STANDING (answerable here)",
                              _gist(str(o.get("title", "")), 90) + drift,
                              ("you answered: " + _verbatim(str(done.get("answer") or ""), 120))
                              if done else str(o.get("standing") or "not recorded"),
                              _age_cell(o)),
                      tags=("bad" if drift else ("good" if done else "warn"),
                            "even" if i % 2 == 0 else "odd"))
            i += 1

        # A REFRESH MUST NEVER DESTROY IN-PROGRESS INPUT (2026-08-16 owner report: "periodically it
        # resets my selected answer to the first one so it's hard to answer").
        #
        # This table is rebuilt from scratch every 20 s, which throws the selection away, so the
        # selection has to be put back by ROW ID. It used to be put back from `_selected_qid`,
        # which `_show_board_detail` sets to None for every kind except QUESTION -- so selecting a
        # DECISION or a STANDING row left nothing to restore and the rebuild fell through to
        # `next(iter(...))`, the first row. `_selected_row_id` records the pick WHATEVER ITS KIND.
        # Falling back to the first row is now reserved for the case where the owner has genuinely
        # not picked anything yet; if their row has disappeared (they just answered it) the
        # selection is dropped rather than silently moved onto a neighbour.
        keep = None
        if self._selected_row_id:
            keep = next((k for k, v in self._wait_rows.items()
                         if v.get("id") == self._selected_row_id), None)
        if self._wait_rows:
            if keep is None and self._selected_row_id is None:
                keep = next(iter(self._wait_rows))
            if keep is not None:
                tv.selection_set(keep)
                self._show_board_detail()
            else:
                tv.selection_remove(*tv.selection())
                self._selected_qid = None
                self._sync_answer_ui(None)
                self._set_text(self.board_detail, [
                    ("Select a row above to read it here.\n", "dim"),
                    "(the row you had selected is no longer on the board -- most likely you just "
                    "answered it)"])
        else:
            self._set_text(self.board_detail, [("Nothing is waiting on you.\n", "good"),
                                               "No open question and no undecided standing item."])
            self._selected_qid = None
            self._sync_answer_ui(None)
        # defect 3: put the scrollbar back where the owner left it. Selection is already handled
        # above by data id (2026-08-16); this restores the other half a refresh used to reset.
        self._restore_scroll(tv, _scroll_frac)
        # DEFECT B bookkeeping: remember what is now actually on screen, so the next `_r_board`
        # call while the owner is engaged can tell whether new data has genuinely arrived.
        self._board_rendered_snapshot = self._board_snapshot(s)

    # ---- the answer box: one draft per question, and it always says which -------------
    def _draft_key(self) -> str:
        """The key the box's CURRENT contents belong under. A draft typed while no question was
        selected is kept too (under a reserved key) rather than thrown away -- that text is exactly
        what was lost on 2026-08-16."""
        return self._answer_for or _UNATTACHED_DRAFT

    def _stash_draft(self) -> None:
        self._drafts[self._draft_key()] = self.answer_box.get("1.0", "end").rstrip("\n")

    def _load_draft(self, qid: str | None) -> None:
        self.answer_box.delete("1.0", "end")
        self.answer_box.insert("1.0", self._drafts.get(qid or _UNATTACHED_DRAFT, ""))
        self._answer_for = qid

    def _clear_answer(self) -> None:
        self.answer_box.delete("1.0", "end")
        self._drafts.pop(self._draft_key(), None)

    def _sync_answer_ui(self, row: dict | None) -> None:
        """Make the box SAY what it will do, and make the button able to do only that.

        EVERY ROW IS ANSWERABLE (2026-08-16, second owner report: *"there is a new 'save as a new
        submission', but save answer is greyed out for all?"*). The previous fix greyed Save out on
        any row that was not a board QUESTION -- and the board had ZERO open questions, so all
        eleven live rows were DECISION or STANDING and Save was correctly, uselessly, dead
        everywhere. Decisions are precisely what the owner has been trying to answer. So the
        question is no longer WHAT KIND OF ROW this is; it is only whether notes/BOARD.md can be
        written and whether a row is selected at all.

        The earlier discipline survives intact: the caption names the exact row the box is bound to,
        and Save is disabled WITH A STATED REASON rather than enabled-and-refusing. An enabled
        control that refuses on press is the defect; a disabled control that says why is the fix."""
        kind = (row or {}).get("_kind")
        rid = (row or {}).get("id")
        can_save = bool(self._board_writable and rid)
        if can_save and kind == "QUESTION":
            cap = (f"YOUR ANSWER TO {rid}  --  pressing Save writes it into the ANSWER cell of "
                   f"{rid} in notes/BOARD.md")
        elif can_save:
            cap = (f"YOUR ANSWER TO {rid}  --  pressing Save records it in notes/BOARD.md as a new "
                   f"row that names {rid} and carries the whole of its text, so it reads on its own "
                   f"later. {rid} lives in a document that code parses, so nothing is written "
                   f"there.")
        elif row is None:
            cap = ("YOUR ANSWER  --  NOT ANSWERABLE: no row is selected, so there is nothing to "
                   "write to. Anything you type here can still be filed with 'File as a new note'.")
        else:
            cap = (f"YOUR ANSWER TO {rid}  --  NOT ANSWERABLE: notes/BOARD.md cannot be written "
                   f"from here. Type into the ANSWER cell in the file instead.")
        try:
            self.answer_caption.configure(text=cap)
        except tk.TclError:
            pass
        self.answer_btn.state(["!disabled"] if can_save else ["disabled"])
        self.note_btn.state(["!disabled"] if self._board_writable else ["disabled"])

    # ---- board archive + reading size (owner, 2026-08-20) --------------------------------------
    def _toggle_board_archive(self) -> None:
        self.board_archive = not self.board_archive
        self.board_archive_btn.configure(
            text="Back to open questions" if self.board_archive else "Show answered archive")
        # STRAIGHT TO `_r_board_apply`, NOT `_r_board`. `_r_board` is a deliberate freeze-guard: it
        # refuses to re-render when the incoming payload is byte-identical to what is on screen, so
        # the table cannot jump while the owner is mid-sentence in the answer box. A mode toggle
        # changes NOTHING in the payload -- only which subset is listed -- so routing it through
        # that guard means the click does nothing at all. This is an explicit owner action and takes
        # the same path `_board_force_refresh` does.
        s = self._state or getattr(self, "_board_last_state", None)
        if s:
            self._r_board_apply(s)
        self._update_board_mode_label()

    def _toggle_board_big_read(self) -> None:
        """Trade table rows for reading rows. The detail pane owns the only weighted grid row on
        this tab, so every row the table gives up goes straight to the question text."""
        self.board_big_read = not self.board_big_read
        try:
            self.board_tv.configure(height=1 if self.board_big_read else 3)
        except tk.TclError:
            pass
        self.board_big_btn.configure(
            text="Smaller reading pane" if self.board_big_read else "Bigger reading pane")
        self._update_board_mode_label()

    def _update_board_mode_label(self) -> None:
        try:
            n = len(self.board_tv.get_children())
        except tk.TclError:
            n = 0
        if self.board_archive:
            msg = ("ARCHIVE -- %d question(s) you have already answered, newest first. "
                   "Click one to read it and your answer in full." % n)
        else:
            msg = "%d item(s) waiting on you. Click a row to read it in full below." % n
        try:
            self.board_mode_lbl.configure(text=msg)
        except tk.TclError:
            pass

    def _show_board_detail(self) -> None:
        sel = self.board_tv.selection()
        r = getattr(self, "_wait_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        kind = r.get("_kind")
        # THE BOX FOLLOWS THE SELECTION (2026-08-16 owner report: "regardless of what question I
        # select the text box doesn't change"). Before this, the box was never touched here, so
        # text composed for one question stayed put when another was selected and Save attached it
        # to the WRONG id, silently. Now the outgoing draft is banked under the question it was
        # written for and the incoming question's own draft is loaded -- switching rows can neither
        # carry text across nor discard it.
        self._stash_draft()
        # EVERY KIND IS ANSWERABLE NOW, so the draft key and the Save target are the row id
        # whatever the row is. Before this, `_selected_qid` was set only for QUESTION rows, which is
        # what made Save dead on all eleven live rows.
        self._selected_qid = r.get("id")
        self._selected_kind = kind
        self._selected_row = r
        self._selected_row_id = r.get("id")
        self._load_draft(self._selected_qid)
        self._sync_answer_ui(r)
        if kind == "ANSWERED":
            # Read-only history. It deliberately does NOT offer to re-answer: the row is settled,
            # and the answer box above is for things still waiting.
            chunks = [(f"{r.get('id')}  {r.get('question')}\n\n", "h"),
                      ("YOUR ANSWER\n", "good"),
                      (f"{r.get('answer') or '(no answer text recorded)'}\n\n", "")]
            # Only render fields the ANSWERED schema actually carries. Measured: answered rows have
            # id / question / answer / rec / resolved and NOT why / asked, so printing those
            # unconditionally put "(not recorded)" on every single row -- noise that makes a real
            # missing value indistinguishable from a field that never exists here.
            for key, head, style in (("why", "WHY IT WAS ASKED", "warn"),
                                     ("rec", "WHAT I RECOMMENDED AT THE TIME", "dim")):
                if r.get(key):
                    chunks += [(head + "\n", style), (f"{r.get(key)}\n\n", "")]
            if r.get("resolved"):
                chunks.append((f"settled {r.get('resolved')}\n", "dim"))
            chunks.append(("\nThis is the archive -- the row is settled and nothing is waiting on "
                           "it. Press 'Back to open questions' to return to what still needs "
                           "you.\n", "dim"))
            self._set_text(self.board_detail, chunks)
            return
        if kind == "QUESTION":
            self._set_text(self.board_detail, [
                (f"{r.get('id')}  {r.get('question')}\n\n", "h"),
                ("WHAT IS BLOCKED ON IT\n", "warn"),
                f"{r.get('why') or '(not recorded)'}\n\n",
                ("MY RECOMMENDATION\n", "good"),
                f"{r.get('rec') or '(none)'}\n\n",
                ("You can answer this one by typing below and pressing Save.\n", "dim"),
            ] + _age_chunks(r, "WHEN THIS QUESTION WAS LAST TOUCHED"))
            return
        if kind == "DECISION":
            self._set_text(self.board_detail, [
                (f"{r.get('id')}  {r.get('question')}\n\n", "h"),
                ("WHY IT IS OPEN\n", "warn"), f"{r.get('why') or '(not recorded)'}\n\n",
                ("WHAT HAPPENS IF YOU SAY NOTHING\n", "good"),
                f"{r.get('default') or 'NO DEFAULT IS STATED, so nothing happens at all.'}\n\n",
                ("Read live out of notes/PLAN.md section 9 on every refresh. You CAN answer it "
                 "here: your answer is recorded in notes/BOARD.md as its own row naming this "
                 "decision and carrying its text, because notes/PLAN.md is parsed by code and no "
                 "typed prose is written into it.\n", "dim"),
            ] + self._recorded_chunks(r) + _age_chunks(
                r, "WHEN THE DOCUMENT RECORDING THIS WAS LAST WRITTEN"))
            return
        chunks = [
            (f"{r.get('id')}  {r.get('title')}\n\n", "h"),
            f"{r.get('question') or ''}\n\n",
            ("WHAT IS BLOCKED ON IT\n", "warn"), f"{r.get('blocked') or '(not recorded)'}\n\n",
            ("WHAT IS HAPPENING TODAY WHILE NOBODY ANSWERS\n", "warn"),
            f"{r.get('standing') or '(not recorded)'}\n\n",
            ("MY RECOMMENDATION\n", "good"), f"{r.get('rec') or '(none)'}\n\n",
            (f"recorded in: {r.get('source', '')}\n", "mono"),
        ]
        if r.get("verify_status") == "CHECK_SOURCE":
            chunks.append(("\nCHECK THE SOURCE: these numbers are no longer findable in the "
                           f"status documents: {r.get('verify_missing')}. This row may be "
                           "stale.\n", "bad"))
        elif r.get("verify_status") == "CANNOT_VERIFY":
            chunks.append(("\nThis row's numbers could not be cross-checked -- the status "
                           "documents were not readable. That is NOT the same as verified.\n",
                           "warn"))
        chunks += self._recorded_chunks(r)
        chunks += _age_chunks(r, "WHEN THE DOCUMENT RECORDING THIS WAS LAST WRITTEN")
        self._set_text(self.board_detail, chunks)

    def _recorded_chunks(self, row: dict) -> list:
        """If this row has ALREADY been answered on the board, show the answer back.

        Read out of notes/BOARD.md by the collector, never remembered here, so an answer the owner
        typed on a phone shows up identically to one typed in this window. Without this, a decision
        the owner has already settled keeps presenting itself as outstanding forever."""
        rec = _d(_d(getattr(self, "_board_state", None)).get("recorded")).get(
            str(_d(row).get("id") or "").upper())
        if not isinstance(rec, dict):
            return []
        return [("\nYOU HAVE ALREADY ANSWERED THIS\n", "good"),
                f"{rec.get('answer') or ''}\n",
                (f"recorded on the board as {rec.get('board_id')} at {rec.get('resolved')}. "
                 f"Answering again simply records another row; nothing is overwritten.\n", "mono")]

    def _save_answer(self) -> None:
        """Write the box into notes/BOARD.md for the selected row, and SAY SO ON SCREEN.

        Every branch here reports. The owner's report was "'save my answer' doesn't do anything",
        and an operation whose failure and whose success look identical is indistinguishable from
        one that does nothing -- so a success echoes the id, the file and the text that landed, and
        a failure says which of those did not happen. Nothing exits quietly."""
        text = self.answer_box.get("1.0", "end").strip()
        qid = self._selected_qid
        if not qid:
            self.answer_status.configure(
                text="NOT SAVED: no row is selected, so there is nothing to record an answer "
                     "against. Pick any row above -- a question, a decision or a standing item; "
                     "all three can be answered here. Your text is still in the box, and 'File as "
                     "a new note' will record it on the board as its own row.",
                fg=_AMBER)
            return
        # DEFENCE IN DEPTH against the mis-attachment defect. The box and the selection are kept in
        # step by _show_board_detail; if they have somehow drifted apart, REFUSE rather than write
        # a draft against a question the owner was not looking at. Silence here is what put one
        # question's words into another question's cell.
        if self._answer_for != qid:
            self.answer_status.configure(
                text=f"NOT SAVED: the text in the box was written for "
                     f"{self._answer_for or 'no question'}, but {qid} is selected. Nothing was "
                     f"written. Re-select the question you meant and press Save again.", fg=_RED)
            return
        if not text:
            self.answer_status.configure(
                text=f"NOT SAVED: the box is empty, and an empty answer would silently close "
                     f"{qid}. Nothing was written.", fg=_AMBER)
            return
        # THE ROW AND THE ID MUST AGREE (found by this file's own self-test, 2026-08-16). Now that
        # the KIND decides where an answer goes -- into a question's own cell, or into a new row
        # carrying a decision's text -- a kind left over from a previous selection would file an
        # answer against a row the panel is not showing. It is the same class of fault as the
        # mis-attachment guard above, one level up, so it gets the same treatment: refuse, say so,
        # and keep the text. Writing SOMETHING plausible is what loses an answer.
        row = _d(getattr(self, "_selected_row", None))
        kind = getattr(self, "_selected_kind", None)
        if not kind or row.get("id") != qid:
            self.answer_status.configure(
                text=f"NOT SAVED: REFUSED -- this window has lost track of which row {qid} is "
                     f"(it is holding {row.get('id')!r} as a "
                     f"{kind or 'row of no known kind'}). Nothing was written. Click the row you "
                     f"meant in the table above and press Save again; your text is still in the "
                     f"box.", fg=_RED)
            return
        ok, msg, board_id = status_state.record_answer(kind, qid, row, text)
        if not ok:
            # The text is deliberately LEFT IN THE BOX and in the draft, so a failed write never
            # costs the owner what they typed.
            self.answer_status.configure(
                text=f"NOT SAVED to {status_state.BOARD_DOC}: {msg}   Your text is still in the "
                     f"box.", fg=_RED)
            return
        # THE CONFIRMATION. It names the row, the file, and quotes the text back, so that
        # "did that land?" is answerable from the screen alone.
        where = (f"in {qid}'s ANSWER cell" if kind == "QUESTION"
                 else f"as row {board_id}, which names {qid} and repeats its text in full")
        self.answer_status.configure(
            text=(f"SAVED against {qid}. Written into notes/BOARD.md "
                  f"({status_state.BOARD_DOC}), {where}: \"{_verbatim(text)}\"   -- {msg}"),
            fg=_GREEN)
        self._drafts.pop(qid, None)
        self.answer_box.delete("1.0", "end")
        self._answer_for = None
        self._selected_qid = None
        self._selected_row_id = None
        self._selected_kind = None
        self._selected_row = {}
        # DEFECT B: this used to clear only the python bookkeeping above, leaving the TREEVIEW
        # WIDGET itself still showing the row highlighted -- harmless before this pass, but now
        # `_board_engaged()` reads the widget's own selection, so a stale highlight would freeze
        # the very refresh two lines below from ever showing the row's new ANSWERED state. A
        # successful save is a deliberate, owner-initiated action, so disengaging here (not
        # merely on the next idle tick) is correct, not just convenient for the freeze to work.
        try:
            self.board_tv.selection_remove(*self.board_tv.selection())
        except tk.TclError:
            pass
        self.refresh_now()

    def _file_note(self) -> None:
        """Record the typed text on the board as its OWN already-answered row.

        WHY THIS EXISTS. On 2026-08-16 the board had zero open questions, so every selectable row
        was a DECISION or STANDING item, none of which this window can write -- and the owner typed
        a real answer that consequently had nowhere to go and was lost. A panel with a text box and
        no reachable destination is a trap. This gives typed text a destination unconditionally.

        It goes through `board.ask()` + `board.resolve()` rather than touching the document,
        because those are the tested calls: atomic temp-file rewrite, hand-added sections preserved
        verbatim, a raw `|` in the text round-tripped."""
        text = self.answer_box.get("1.0", "end").strip()
        if not text:
            self.answer_status.configure(
                text="NOT FILED: the box is empty, so there is nothing to record.", fg=_AMBER)
            return
        ctx = self._selected_row_id or "no row selected"
        ok, msg, new_id = status_state.file_board_note(text, context=ctx)
        if not ok:
            self.answer_status.configure(
                text=f"NOT FILED to {status_state.BOARD_DOC}: {msg}   Your text is still in the "
                     f"box.", fg=_RED)
            return
        self.answer_status.configure(
            text=(f"FILED as {new_id}. Written into notes/BOARD.md ({status_state.BOARD_DOC}) "
                  f"under ANSWERED, noted against {ctx}: \"{_verbatim(text)}\""), fg=_GREEN)
        self._drafts.pop(self._draft_key(), None)
        self.answer_box.delete("1.0", "end")
        self.refresh_now()

    # ---- panel 6 ------------------------------------------------------
    def _r_running(self, s: dict) -> None:
        # THE OVERNIGHT LOOP, merged in from its own former tab. Whether the machine keeps working
        # is part of "what is running", and the stop command belongs beside it.
        lp = _d(s.get("loop"))
        armed = lp.get("armed")
        if armed is True:
            self.loop_big.configure(text="THE OVERNIGHT LOOP IS ON", fg=_GREEN)
            self.loop_sub.configure(
                text=(f"It will keep working through the night without you, and will stop by "
                      f"itself after {lp.get('cap_label')} continuations. Switched on at "
                      f"{lp.get('armed_at')} by {lp.get('armed_by')}. "
                      f"{lp.get('continuations_recent_total', 0)} continuation(s) used in the "
                      f"last 24 hours."))
        elif armed is False:
            self.loop_big.configure(text="THE OVERNIGHT LOOP IS OFF", fg=_DIM)
            self.loop_sub.configure(text="Work stops when the current turn ends.")
        else:
            self.loop_big.configure(text="OVERNIGHT LOOP: UNKNOWN", fg=_AMBER)
            self.loop_sub.configure(text=str(lp.get("detail", "")))
        self.disarm_box.configure(state="normal")
        self.disarm_box.delete("1.0", "end")
        self.disarm_box.insert("1.0", lp.get("disarm_cmd") or "python tools/autoloop.py disarm")
        self.loop_alt.configure(text=str(lp.get("disarm_alt", ""))
                                + f"   setting file: {lp.get('state_path')}")

        rn = _d(s.get("running"))
        ag = _d(rn.get("agents"))
        tv = self.agents_tv
        _kept_ag = self._keep_scroll(tv)   # defect 3 (no per-row detail pane on this table)
        tv.delete(*tv.get_children())
        if ag.get("status") != "OK":
            tv.insert("", "end", values=(ag.get("status", "?"),
                                         str(ag.get("detail", ""))[:60], "", "", "UNKNOWN"),
                      tags=("warn",))
        else:
            agents = [_d(a) for a in _l(ag.get("agents"))]
            if not agents:
                tv.insert("", "end", values=("", "no agents active in the last hour",
                                             "", "", ""), tags=("dim",))
            for i, a in enumerate(agents):
                if a.get("stopped_by_user"):
                    state, tag = "stopped by you", "dim"
                elif a.get("state") == "WORKING":
                    state, tag = "WORKING", "good"
                else:
                    state, tag = "no output 15min+", "warn"
                tv.insert("", "end", values=(
                    state, f"{a.get('name')}  ({a.get('model')})", a.get("description", ""),
                    _fmt_dur(a.get("elapsed_s")), _age_cell(a),
                ), tags=(tag, "even" if i % 2 == 0 else "odd"))
        self._restore_scroll(tv, _kept_ag)

        tv2 = self.local_tv
        _kept_lx = self._keep_selection(tv2)   # defect 3
        tv2.delete(*tv2.get_children())
        self._run_rows: dict[str, dict] = {}
        lx = [_d(e) for e in _l(rn.get("local_experiments"))]
        cl = _d(rn.get("claims"))
        claims = [_d(c) for c in _l(cl.get("claims"))]

        head = "WORK ON THIS MACHINE -- what is running, AND what only CLAIMS to be"
        if cl.get("status") == "OK":
            head += "        " + str(cl.get("headline") or "")
        elif cl.get("status"):
            head += (f"        the pid-file claims could NOT be checked ({cl.get('status')}: "
                     f"{str(cl.get('detail'))[:90]}) -- treat this list as INCOMPLETE, not as empty")
        self.local_head.configure(
            text=head, fg=_RED if (cl.get("n_dead") or 0) else _BLUE)

        i = 0
        if not lx and not claims:
            tv2.insert("", "end", values=("nothing at all", "no process is running here and "
                                          "nothing claims to be", "", "", "", ""),
                       tags=("dim",))
        # THE LIVE ONES FIRST. These are observed processes, not claims.
        for e in lx:
            prog = ""
            if e.get("progress_pct") is not None:
                prog = (f"{e.get('unit_idx')}/{e.get('total_units')} "
                        f"{int(e['progress_pct'])}%")
                if e.get("eta_s"):
                    prog += f"  about {_fmt_dur(e['eta_s'])} left"
                if e.get("phase"):
                    prog += f"  ({e['phase']})"
            iid = f"lx{i}"
            self._run_rows[iid] = dict(e, _kind="LIVE")
            tv2.insert("", "end", iid=iid, values=(
                "RUNNING - process seen", _short(e.get("name", "?"), 70),
                prog or "no progress reported",
                _fmt_dur(e.get("elapsed_s")), e.get("pid", "?"), _age_cell(e),
            ), tags=("good", "even" if i % 2 == 0 else "odd"))
            i += 1
        # THEN THE CLAIMS. A claim already matched to a live process is skipped -- it is the row
        # above. Everything else is a run that SAYS it is going and is not, and it is shown in the
        # loss colour, because being quietly absent is exactly how three dead runs were briefed as
        # live for hours.
        live_pids = {e.get("pid") for e in lx} | {e.get("shim_pid") for e in lx}
        for c in claims:
            if c.get("state") == "RUNNING" and c.get("pid") in live_pids:
                continue
            state = str(c.get("state") or "UNKNOWN")
            tag = ("bad" if state.startswith("DEAD") else
                   "warn" if state.startswith(("UNKNOWN", "PID FILE", "ALIVE")) else "good")
            logs = _l(c.get("logs"))
            newest = _d(logs[0]) if logs else {}
            iid = f"cl{i}"
            self._run_rows[iid] = dict(c, _kind="CLAIM")
            tv2.insert("", "end", iid=iid, values=(
                state, _short(str(c.get("name") or "?"), 70),
                (f"its last output was {_fmt_dur(newest.get('age_s'))} ago ({newest.get('name')})"
                 if newest else "it left no output file at all"),
                (f"claimed {_fmt_dur(c.get('claimed_age_s'))} ago"
                 if c.get("claimed_age_s") is not None else "unknown"),
                c.get("pid", "?"),
                (_fmt_dur(newest.get("age_s")) + " ago" if newest.get("age_s") is not None
                 else "UNKNOWN"),
            ), tags=(tag, "even" if i % 2 == 0 else "odd"))
            i += 1
        # defect 3: restore whichever run row was selected (fallback_iid=None -- there is no
        # sensible "default" run to jump to, unlike the tables that always have a natural row 0).
        self._restore_selection(tv2, _kept_lx, fallback_iid=None,
                                select_cb=self._show_running_detail)

        # remote box + alerts
        g = _d(rn.get("gpu"))
        ck = _d(rn.get("remote_checkpoint"))
        util = rn.get("gpu_util")
        src = {"feed": "live feed", "cache": "the 30-second file copy from the remote box",
               "ssh": "a direct check over the network", "stale": "NOTHING - no reading"}.get(
            g.get("source"), "unknown")
        chunks = [("THE REMOTE MACHINE (the graphics card)\n", "h")]
        if util is None or g.get("source") == "stale":
            chunks += [("No reading at all right now.", "warn"),
                       " The feed, the copied file and the direct check all failed. "
                       "This is UNKNOWN, not idle.\n"]
        else:
            busy = isinstance(util, (int, float)) and util >= 25
            chunks += [f"Graphics card is ", (f"{util}% busy", "good" if busy else "dim"),
                       f", read from {src}.\n"]
            if busy and (g.get("queue_status") == "running" or g.get("experiment_on_card")):
                chunks.append(("That is OUR work.\n", "good"))
            elif busy:
                chunks.append(("That is somebody else's work; our own queue is idle.\n", "warn"))
            else:
                chunks.append("Our queue is idle.\n")
        state = ck.get("state")
        chunks.append("\nIs a remote run actually alive? ")
        if state == "SEEN":
            age = ck.get("age_s")
            chunks += [("its save-file was written ", "dim"),
                       (f"{_fmt_dur(age)} ago", "good" if (age or 1e9) < 1800 else "warn"),
                       f" ({ck.get('checkpoint')}).\n"]
        elif state == "NO_REMOTE_RUN":
            chunks.append(("nothing is running remotely, so there is nothing to check.\n", "dim"))
        else:
            chunks.append((f"{state or 'UNKNOWN'} -- {ck.get('reason', '')}\n", "warn"))
        chunks.append(("We judge this by the save-file being written, never by the progress "
                       "ping: the ping is coarse and has wrongly cried 'stalled' three "
                       "times.\n", "dim"))

        age_line = _panel_age_text(s.get("ages"), "running now").strip()
        if age_line:
            chunks += [("\nHOW FRESH IS ANY OF THIS\n", "dim"), age_line + "\n",
                       ("These are the times the transcripts and output files were last written "
                        "-- what the processes actually produced, not what this window last "
                        "asked.\n", "dim")]

        alerts = [_d(a) for a in _l(rn.get("alerts"))]
        chunks.append("\n")
        if alerts:
            chunks.append(("PROBLEMS THE MONITOR IS REPORTING\n", "h"))
            for a in alerts[:8]:
                lvl = a.get("level")
                chunks.append((f"[{lvl}] {a.get('code')}: {a.get('msg')}\n",
                               "bad" if lvl == "CRITICAL" else "warn"))
        else:
            chunks.append(("Nothing is broken that the monitor can see.\n", "good"))
        self._running_summary = chunks
        self._show_running_detail()

        n_dead = cl.get("n_dead") or 0
        # TAB LABELS SHORTENED (2026-08-17). The seven tab labels, measured with their own font,
        # needed ~1750 px in a row to display unclipped -- more than the whole 1068 px window on
        # the owner's actual screen, forcing ttk to wrap the tab strip onto a second row before the
        # content below it is even reached. This one drops "loop ON/off" (already the first thing
        # shown, in large text, the moment this tab is opened) and the active-agent count (not
        # covered by any self-test); the dead-run count survives because
        # verification/test_status_running_panel.py asserts it is visible without opening the tab.
        dead_tag = f" ({n_dead} dead)" if n_dead else ""
        try:
            self.nb.tab(self.tab_running, text=f"2. RUNNING{dead_tag}")
        except tk.TclError:
            pass

    def _show_running_detail(self) -> None:
        """The selected run's own story, above the machine-wide summary.

        For a DEAD BUT CLAIMED LIVE row this is the whole point of the panel: it names the pid file
        that is still asserting the run, says how the operating system was asked, and points at the
        log files -- which are the only evidence a detached run leaves behind once its process is
        gone."""
        summary = list(getattr(self, "_running_summary", []) or [])
        sel = self.local_tv.selection() if hasattr(self, "local_tv") else ()
        r = _d(getattr(self, "_run_rows", {}).get(sel[0])) if sel else {}
        if not r:
            self._set_text(self.running_detail, summary)
            return
        head: list = []
        if r.get("_kind") == "CLAIM":
            state = str(r.get("state") or "UNKNOWN")
            head += [(f"{r.get('name')}  --  {state}\n", "bad" if state.startswith("DEAD") else
                      "warn")]
            if state.startswith("DEAD"):
                head.append(("This run is NOT happening. Something wrote a file saying it was, and "
                             "that file is still there. Do not read it as evidence of work in "
                             "flight.\n", "bad"))
            head += [(f"how we know: {r.get('basis', '')}\n", "dim"),
                     (f"the claim lives in: {r.get('pid_file')}\n", "mono"),
                     (f"it names process {r.get('pid')}, and was written "
                      f"{_fmt_dur(r.get('claimed_age_s'))} ago\n", "mono")]
            logs = _l(r.get("logs"))
            if logs:
                head.append(("what it left behind (this is the only evidence left once the process "
                             "is gone):\n", "dim"))
                for lg in logs:
                    lg = _d(lg)
                    head.append((f"    {lg.get('path')}  --  {lg.get('bytes')} bytes, last "
                                 f"written {_fmt_dur(lg.get('age_s'))} ago\n", "mono"))
            else:
                head.append(("it left no output file at all, so there is nothing to read.\n",
                             "warn"))
            head.append(("Nothing in this window deletes or tidies these files; it only reports "
                         "them.\n", "dim"))
        else:
            head += [(f"{r.get('name')}  --  RUNNING\n", "good"),
                     (f"process {r.get('pid')}"
                      + (f" (started through shim {r.get('shim_pid')})" if r.get("shim_pid")
                         else "") + f", running for {_fmt_dur(r.get('elapsed_s'))}\n", "mono"),
                     ("This one was observed as a live process, not inferred from a file.\n",
                      "dim")]
            head += _age_chunks(r, "WHEN THIS RUN LAST WROTE ANYTHING")
        self._set_text(self.running_detail, head + ["\n"] + summary)

    # ---- panel 7 ------------------------------------------------------
    def _r_results(self, s: dict) -> None:
        res = _d(s.get("results"))
        tv = self.results_tv
        _kept = self._keep_selection(tv)   # defect 3: was hardcoded back to row 0 every refresh
        tv.delete(*tv.get_children())
        self._result_rows: dict[str, dict] = {}
        if res.get("status") != "OK":
            self.results_hint.configure(
                text=f"{res.get('status')}: {res.get('detail', '')}", fg=_AMBER)
            self._set_text(self.results_detail,
                           [(f"{res.get('status')}\n", "warn"), str(res.get("detail", ""))])
            self._restore_scroll(tv, _kept[0])
            return
        rows = [_d(r) for r in _l(res.get("rows"))]
        n_unvetted = sum(1 for r in rows if not _vetting(r.get("name") or "").get("vetted"))
        self.results_hint.configure(
            text=(f"The {len(rows)} most recent finished experiments. "
                  f"{res.get('n_negative')} of them are negative and "
                  f"{res.get('n_no_floor')} never named a floor at all -- a result with no "
                  f"floor beside it cannot be graded. Losses are shown exactly as loudly as "
                  f"wins, on purpose. "
                  f"{n_unvetted} of {len(rows)} have never been checked by anyone: "
                  f"{_ledger.base_rate() if _ledger else 'the vetting ledger would not load.'}"
                  + _panel_age_text(s.get("ages"), "latest results")),
            fg=_AMBER if (res.get("n_negative") or n_unvetted) else _BLUE)
        for i, r in enumerate(rows):
            iid = f"r{i}"
            self._result_rows[iid] = r
            label = r.get("label", "FINDING")
            tag = {"NEGATIVE": "bad", "WIN": "good"}.get(label, "warn")
            floor_cell = "yes" if r.get("floor_named") else "NO FLOOR STATED"
            sep = {"YES": "yes, separated", "NO": "NO - they overlap"}.get(
                r.get("separated"), "not stated")
            name = _short(r.get("name", "?"), 52)
            if r.get("is_smoke"):
                name += "   (smoke)"
            vet = _vetting(r.get("name") or "")
            r["_vetting"] = vet
            vet_txt, vet_tag = _VET_TEXT.get(vet["disposition"],
                                             (vet["disposition"], "warn"))
            # A REFUTED or unchecked claim colours the whole row, overriding the run's own label --
            # a cell that called itself a WIN and was later refuted must not still render green.
            if vet_tag == "bad":
                tag = "bad"
            elif tag == "good" and vet_tag == "warn":
                tag = "warn"
            # The relative age is what reads at a glance; the exact stamp stays one click away in
            # the detail box, which is the split the owner asked for.
            tv.insert("", "end", iid=iid, values=(
                _age_cell(r), label, r.get("verdict"), vet_txt, floor_cell, sep, name),
                tags=(tag, "even" if i % 2 == 0 else "odd"))
        if rows:
            self._restore_selection(tv, _kept, fallback_iid="r0",
                                    select_cb=self._show_result_detail)
        else:
            self._restore_scroll(tv, _kept[0])

    def _show_result_detail(self) -> None:
        sel = self.results_tv.selection()
        r = getattr(self, "_result_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        label = r.get("label", "FINDING")
        tag = {"NEGATIVE": "bad", "WIN": "good"}.get(label, "warn")
        vet = r.get("_vetting") or _vetting(r.get("name") or "")
        vet_txt, vet_tag = _VET_TEXT.get(vet["disposition"], (vet["disposition"], "warn"))
        chunks = [
            (f"{r.get('name')}\n", "h"),
            (f"{label}: {r.get('verdict')}\n\n", tag),
            f"{r.get('verdict_msg') or '(the run recorded no explanation)'}\n\n",
        ]
        # THE DISPOSITION GOES ABOVE THE FLOOR AND SEPARATION WARNINGS, because it outranks them:
        # a refuted cell's floor is beside the point, and an unchecked one's verdict is a claim.
        chunks.append((f"HAS ANYONE CHECKED IT?  {vet_txt}\n", vet_tag))
        if vet.get("vetted"):
            chunks.append(f"{vet.get('finding') or ''}\n")
            if vet.get("narrowing_or_rerun"):
                key = ("RERUN NEEDED" if vet["disposition"] == "RERUN_NAMED"
                       else "CITE ONLY WITH THIS ATTACHED")
                chunks.append((f"{key}: {vet['narrowing_or_rerun']}\n", "warn"))
            if vet["disposition"] == "SHELVED_REFUTED":
                chunks.append(("DO NOT CITE THIS RESULT.\n", "bad"))
        elif _ledger is not None:
            chunks.append((f"{_ledger.base_rate()}\n", "dim"))
        else:
            chunks.append((f"The vetting ledger would not load: {_LEDGER_ERR}\n", "bad"))
        chunks.append("\n")
        if not r.get("floor_named"):
            chunks.append(("This result names no floor. A score with no floor beside it "
                           "cannot be graded -- treat it as an observation, not a verdict.\n",
                           "warn"))
        if r.get("separated") == "UNKNOWN":
            chunks.append(("It also does not say whether the intervals are separated.\n",
                           "warn"))
        chunks += _age_chunks(r, "WHEN THIS RESULT WAS LAST WRITTEN")
        chunks.append((f"\nfinished {r.get('when')} | took "
                       f"{_fmt_dur(r.get('elapsed_s'))} | {r.get('path')}\n", "mono"))
        self._set_text(self.results_detail, chunks)


# ---------------------------------------------------------------------------

def _enforce_single_instance() -> None:
    """OPT-IN ONLY (`--single-instance`). Kills other `status_gui.py` processes and NOTHING
    else -- in particular it never matches `dash_gui.py`, which may be running and is not
    ours to stop. Default is OFF precisely so that launching this window can never take a
    process down by surprise."""
    if sys.platform != "win32":
        return
    try:
        import os
        import subprocess
        from local_exp_scan import _wmic_python_procs
    except Exception:
        return
    no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    own = os.getpid()
    try:
        ppid = os.getppid()
    except OSError:
        ppid = -1
    for p in _wmic_python_procs():
        pid = p.get("pid")
        cmd = (p.get("cmd") or "").lower()
        if pid in (own, ppid) or pid is None:
            continue
        if "status_gui.py" in cmd and "dash_gui.py" not in cmd:
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                               capture_output=True, timeout=6, creationflags=no_window)
            except Exception:
                pass


def self_test() -> int:
    """Build the real window and render three states into it without entering the main loop.

    The point is the DEGRADED cases: a renderer that only works on healthy data is a
    renderer that goes blank at 3am, exactly when the data is not healthy. So it is rendered
    against (1) live data, (2) every panel MISSING, (3) structurally wrong types in every
    field. All three must leave the window standing.
    """
    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"[self-test] SKIP no display available: {exc}", file=sys.stderr)
        return 0
    root.withdraw()
    gui = None
    try:
        gui = StatusWindow(root)
        check(True, "the window builds")

        t0 = time.time()
        live = status_state.collect()
        gui.render(live)
        check(gui._last_error is None,
              f"renders LIVE data with no panel error ({gui._last_error})")
        check(time.time() - t0 < 40, "live collect + render is well inside a refresh cycle")
        check(len(gui.nb.tabs()) == 8,
              f"eight tabs: seven content tabs plus NOTE FOR ME on its own since 2026-08-17 "
              f"(got {len(gui.nb.tabs())})")

        # --- defect A (2026-08-17, THIRD PASS): the reading pane gets the majority of the
        # vertical space, deterministically -- not via a PanedWindow (removed; measured TWICE to
        # mis-size its panes, see _build_board's comment). Checked STRUCTURALLY (grid row weights
        # and the table's declared row count), not by reading winfo_height() -- a headless,
        # unfocused Tk window's actual painted geometry is not a reliable signal (measured live:
        # winfo_ismapped() can stay 0 indefinitely off-screen even after the layout has resolved).
        check(not hasattr(gui, "board_panes"),
              "defect A: the fragile PanedWindow is gone from the WAITING ON YOU tab")
        detail_row = getattr(gui, "_board_detail_row", None)
        table_row = getattr(gui, "_board_table_row", None)
        check(detail_row is not None and table_row is not None,
              "defect A: the tab records which grid row is the table and which is the detail pane")
        if detail_row is not None:
            weight = int(gui.tab_board.grid_rowconfigure(detail_row).get("weight", 0))
            check(weight >= 1,
                  f"defect A: the READING PANE's row is the one with grid weight, so it receives "
                  f"the space every other fixed row does not use (weight {weight})")
        if table_row is not None:
            tweight = int(gui.tab_board.grid_rowconfigure(table_row).get("weight", 0))
            check(tweight == 0,
                  f"defect A: the TABLE's row is fixed, not weighted, so it cannot expand and "
                  f"starve the reading pane the way the height=12 table used to (weight {tweight})")
        check(int(gui.board_tv.cget("height")) <= 7,
              f"defect A: the table is compact (short labels only, per the owner's standard) "
              f"rather than trying to show every row at once (declared height "
              f"{gui.board_tv.cget('height')})")
        bfont = str(gui.board_detail.cget("font"))
        check(bool(bfont.strip()),
              f"defect A: the reading pane has an explicit font configured (got {bfont!r})")
        # The answer box (Save) is a fixed, non-negotiable grid row, unchanged by this pass.
        check(hasattr(gui, "answer_frame") and str(gui.answer_frame.master) == str(gui.tab_board),
              "defect A: the answer box's parent is the tab's plain frame, not a pane that could "
              "shrink")
        check(hasattr(gui, "board_new_data_lbl"),
              "defect B: the WAITING ON YOU tab has a new-data affordance widget")

        # --- defect 2 (2026-08-17): the note channel lives on its OWN tab, not spread across
        # every other one.
        check(hasattr(gui, "tab_commentary") and str(gui.tab_commentary) in gui.nb.tabs(),
              "defect 2: NOTE FOR ME is a real tab registered in the notebook")
        if hasattr(gui, "tab_commentary"):
            check(str(gui.commentary_box.winfo_parent()).startswith(str(gui.tab_commentary)),
                  f"defect 2: the note box lives INSIDE its own tab, not under the notebook on "
                  f"every tab (parent {gui.commentary_box.winfo_parent()!r})")
            for other in (gui.tab_where, gui.tab_board, gui.tab_scores):
                check(str(gui.tab_commentary) != str(other),
                      "defect 2: the note tab is distinct from every content tab")

        # --- the headline strip answers WHERE WE ARE and HOW WE ARE DOING ----
        head1 = gui.headline_lbl.cget("text")
        head2 = gui.headsub_lbl.cget("text")
        check("WE ARE IN PHASE" in head1.upper(),
              f"the top strip says which phase we are in (got {head1[:80]!r})")
        check("NEXT:" in head1,
              f"the top strip says the single next action without a click (got {head1[:120]!r})")
        check("WE GET" in head2 and "GETS" in head2,
              f"the top strip still states our score AND its floor together (got {head2[:110]!r})")
        check("no longer match their source" in head2,
              f"THE DRIFT COUNT IS ON SCREEN, not buried in a cell (got {head2[-140:]!r})")

        # --- tab 1: the plan, parsed live -----------------------------------
        check(len(gui.where_tv.get_children()) >= 5,
              f"the plan panel drew one row per phase (got {len(gui.where_tv.get_children())})")
        wcells = [gui.where_tv.item(i, "values") for i in gui.where_tv.get_children()]
        # A gate the plan does not state must SAY SO in the rendered cell. Never blank, never
        # invented, never carried over from a remembered version of the plan.
        blanks = [c[0] for c in wcells if not str(c[3]).strip()]
        check(not blanks, f"no phase renders an empty gate cell ({blanks})")
        check(any("NOT STATED IN THE PLAN" in str(c[3]) for c in wcells),
              "a gate the plan does not state renders as NOT STATED IN THE PLAN")
        check(any(str(c[1]).strip() in ("DONE", "MOSTLY DONE", "IN PROGRESS", "BLOCKED",
                                        "NOT STARTED", "NOT STATED") for c in wcells),
              f"every phase renders one of the declared status values "
              f"(got {[c[1] for c in wcells]})")
        wd = gui.where_detail.get("1.0", "end")
        check("WHAT WOULD COUNT AS SUCCESS" in wd and "WHAT WOULD MAKE US STOP" in wd,
              "the plan detail box shows the gate and the stop-if for the selected phase")
        check("WHAT WOULD COUNT AS THE WHOLE THING WORKING" in wd,
              "the plan detail box carries the ordered success ladder from section 7")
        check("RETRACTED" in wd,
              "a struck-through work item is shown AS retracted, not hidden and not offered")

        # --- tab 4: the merged scores view ----------------------------------
        check(len(gui.sc_tv.get_children()) >= 10,
              f"the merged scores panel drew its rows "
              f"(got {len(gui.sc_tv.get_children())})")
        check(len(gui.results_tv.get_children()) >= 1, "the results panel drew its rows")
        # THE VETTING RULE, checked at the RENDERED CELL like the floor rule below it and for the
        # same reason: the harm was a verdict shown with NOTHING beside it, so a blank in this
        # column is the exact defect and an empty string must fail. UNVETTED is a real answer.
        _vet_cells = [str(gui.results_tv.set(iid, "vetted"))
                      for iid in gui.results_tv.get_children()]
        check(bool(_vet_cells) and all(c.strip() for c in _vet_cells),
              f"no result is shown without a vetting disposition beside it -- a blank reads as "
              f"an endorsement ({sum(1 for c in _vet_cells if not c.strip())} blank of "
              f"{len(_vet_cells)})")
        check(_ledger is not None and _ledger.disposition("no_such_cell_anywhere") == "UNVETTED",
              "an unknown cell resolves to UNVETTED rather than to a blank or an exception")
        check(_ledger is not None
              and _ledger.disposition("exp_agreement_depth_productivity_generalization_v1") == "WIRE"
              and _ledger.disposition("exp_desiderative_negation_channel_v1") == "SHELVED_REFUTED",
              "the ledger lookup returns the right disposition for a known upheld and a known "
              "refuted cell")
        check(len(gui.organ_tv.get_children()) >= 30,
              f"the organ map drew its rows (got {len(gui.organ_tv.get_children())})")
        check(len(gui.fid_tv.get_children()) >= 1, "the fidelity panel drew its rows")
        check(len(gui.fid_div_tv.get_children()) >= 30,
              "the per-organ divergence table drew its rows")
        # THE RULE, checked at the RENDERED CELL and not at the data, and it must survive the
        # merge: no row may show a score with neither a floor nor an explicit non-answer.
        cells = [gui.sc_tv.item(i, "values") for i in gui.sc_tv.get_children()]
        naked = [c[0] for c in cells
                 if c[3] and not any(k in c[3] for k in
                                     ("floor", "NOT MEASURED", "NOT APPLICABLE", "NOT STARTED",
                                      "NOT REACHED", "NOT YET", "NOT ESTABLISHED", "NONE",
                                      "NO FLOOR", "(", "MISSING"))]
        check(not naked, f"every score row renders a floor or an explicit non-answer ({naked})")
        # RETRACTIONS SURVIVE THE MERGE, in the same table, in the same red.
        retr = [c for c in cells if "RETRACTED" in str(c[4])]
        check(len(retr) >= 3,
              f"retraction rows are still rendered as rows, not a footnote (got {len(retr)})")
        check("retracted" in gui.nb.tab(gui.tab_scores, "text"),
              f"the tab title counts the retractions "
              f"(got {gui.nb.tab(gui.tab_scores, 'text')!r})")

        # --- tab 3: everything waiting on the owner, in one place -----------
        bcells = [gui.board_tv.item(i, "values") for i in gui.board_tv.get_children()]
        kinds = {str(c[1]).split(" ")[0] for c in bcells}
        check({"DECISION", "STANDING"} <= kinds,
              f"the waiting-on-you tab carries the plan's decisions AND the standing operator "
              f"decisions, which previously appeared in no panel at all (got {kinds})")
        # The board legitimately empties -- the owner answers questions. So the QUESTION kind is
        # asserted against the DATA rather than against a fixed expectation: a self-test that
        # demanded an open question would start failing the moment the owner did their job. This
        # used to be checked unconditionally (a comment-vs-code mismatch: the comment said "against
        # the DATA" but the assertion did not), which only passed because of a placeholder row that
        # faked a QUESTION-kind entry even at zero open questions -- exactly the row removed
        # 2026-08-17 as the fix for *"the questions tab now only appears to have one question, and
        # no way for me to select a new one"* (that placeholder was unselectable and answerable to
        # nobody). Now genuinely conditional both ways: QUESTION present iff there is really one.
        n_open_live = ((live.get("board") or {}).get("n_open")
                       if isinstance(live.get("board"), dict) else None)
        if n_open_live:
            check("QUESTION" in kinds,
                  f"open board questions render with their own kind in the same table "
                  f"({n_open_live} open right now, got {kinds})")
        else:
            check("QUESTION" not in kinds,
                  f"with zero open questions, no placeholder QUESTION row is drawn -- the count "
                  f"lives in the banner instead, and every remaining row is really selectable "
                  f"({n_open_live} open right now, got {kinds})")
        check(all(str(c[3]).strip() for c in bcells),
              f"every waiting row says what happens if the owner says nothing "
              f"({[c[0] for c in bcells if not str(c[3]).strip()]})")
        # defect A: NO row's list-cell carries the full text (owner: "I can't read any of the
        # question text" -- traced to unbounded text landing, unwrapped, in this exact cell).
        long_cells = [(c[0], len(str(c[2]))) for c in bcells if len(str(c[2])) > 90]
        check(not long_cells,
              f"defect A: every list-row's question/decision cell is a short gist, not the full "
              f"text (over 90 chars: {long_cells})")

        # --- defect B: THE FREEZE. Select a row, type into the answer box, then call _r_board
        # again TWICE -- exactly what the 20s auto-refresh timer does -- and prove nothing on
        # screen moves. This is the same check the owner was asked to do by hand; done here at the
        # widget level so it runs on every self-test rather than only when someone remembers to
        # click through it manually.
        if gui._wait_rows:
            probe_iid = next(iter(gui._wait_rows))
            gui.board_tv.selection_set(probe_iid)
            gui._show_board_detail()
            probe_text = "SELF-TEST DRAFT -- must survive two refresh cycles untouched"
            gui.answer_box.delete("1.0", "end")
            gui.answer_box.insert("1.0", probe_text)
            gui._stash_draft()
            check(gui._board_engaged(),
                  "defect B: a selected row with unsaved text counts as ENGAGED")
            before_children = gui.board_tv.get_children()
            before_detail = gui.board_detail.get("1.0", "end")
            gui._r_board(live)     # refresh cycle 1, exactly as the 20s timer fires
            gui._r_board(live)     # refresh cycle 2
            check(gui.board_tv.get_children() == before_children,
                  "defect B: two refresh cycles while engaged did not rebuild the table")
            check(gui.board_detail.get("1.0", "end") == before_detail,
                  "defect B: two refresh cycles while engaged did not touch the reading pane")
            check(gui.answer_box.get("1.0", "end").rstrip("\n") == probe_text,
                  f"defect B: the answer box text is byte-identical after two refresh cycles "
                  f"(got {gui.answer_box.get('1.0', 'end').rstrip(chr(10))[:60]!r})")
            check(tuple(gui.board_tv.selection()) == (probe_iid,),
                  "defect B: the selection itself is untouched, not merely restored")
            # Disengaging (deselect + clear the box) must let the NEXT refresh apply normally --
            # the freeze is deliberately not permanent.
            gui.board_tv.selection_remove(*gui.board_tv.selection())
            gui.answer_box.delete("1.0", "end")
            gui._drafts.clear()
            check(not gui._board_engaged(), "defect B: clearing selection and draft disengages")
            gui._r_board(live)
            check(True, "defect B: a disengaged refresh applies without error")
        # --- EVERY ROW ON EVERY PANEL CARRIES ITS EVIDENCE AGE ---------------
        # Checked at the RENDERED CELL throughout. The owner reads cells, and the whole point of
        # this feature is defeated by a timestamp that is right in the payload and absent on screen.
        age_tables = {
            "the plan": (gui.where_tv, 5),
            "scores and floors": (gui.sc_tv, 5),
            "brain organ map": (gui.organ_tv, 5),
            "fidelity points": (gui.fid_tv, 3),
            "organ divergence": (gui.fid_div_tv, 5),
            "waiting on you": (gui.board_tv, 4),
            "agents": (gui.agents_tv, 4),
            "latest results": (gui.results_tv, 0),
        }
        blank_cells = []
        all_age_cells: list[str] = []
        for tname, (tv, col) in age_tables.items():
            cells = [str(tv.item(i, "values")[col]) for i in tv.get_children()
                     if len(tv.item(i, "values")) > col]
            all_age_cells += cells
            if any(not c.strip() for c in cells):
                blank_cells.append(tname)
        check(not blank_cells,
              f"ages: NO row on any table renders an empty last-updated cell ({blank_cells})")
        check(len(all_age_cells) >= 100,
              f"ages: the column is populated across the whole window, not one table "
              f"(got {len(all_age_cells)} cells)")
        # A stamp must be an ARTIFACT age. Documents and experiment outputs are hours or days old,
        # so a window in which EVERY cell reads 'just now' would mean the refresh clock had leaked
        # in -- which is the one failure this feature exists to prevent.
        real_ages = [c for c in all_age_cells if ("ago" in c or "UNKNOWN" in c)]
        check(len(real_ages) >= 100,
              f"ages: cells read as ages, not as anything else ({len(real_ages)} of "
              f"{len(all_age_cells)})")
        check(any(("h ago" in c or "d ago" in c or "w ago" in c) for c in all_age_cells),
              "ages: real artifact ages in hours/days are on screen, so the clock did not leak in")
        check(sum(1 for c in all_age_cells if "just now" in c) < len(all_age_cells) // 2,
              f"ages NEGATIVE CONTROL: the window is NOT stamping everything with the refresh "
              f"time ({sum(1 for c in all_age_cells if 'just now' in c)} of "
              f"{len(all_age_cells)} read 'just now')")
        check(any("OLDER" in c for c in all_age_cells),
              "ages: rows resting on older evidence than the rest of their panel are MARKED, so "
              "the owner does not have to subtract dates")
        check(not all("OLDER" in c for c in all_age_cells),
              "ages NEGATIVE CONTROL: the OLDER marker is not simply on every row")
        # The absolute value must remain reachable, as asked.
        sc_det = gui.sc_detail.get("1.0", "end")
        check("EVIDENCE WAS LAST UPDATED" in sc_det.upper(),
              "ages: the detail box carries the evidence-age block")
        check("exactly:" in sc_det,
              f"ages: the exact absolute timestamp is kept available beside the relative one")
        check("from: " in sc_det,
              "ages: the detail box names WHICH artifact the age came from")
        head2b = gui.headsub_lbl.cget("text")
        check("evidence on screen: newest" in head2b,
              f"ages: the top strip answers how old the whole window is without a click "
              f"(got {head2b[-120:]!r})")
        # And the panel headers answer it per panel.
        check("Newest evidence on this panel" in gui.results_hint.cget("text"),
              f"ages: each panel states its own newest and oldest evidence "
              f"(got {gui.results_hint.cget('text')[-140:]!r})")

        # --- tab 6: the fidelity banner, CORRECTED ---------------------------
        # Every assertion here reads the RENDERED WIDGET, not the payload. The owner reads the
        # screen; a banner that is right in the data and wrong on screen is wrong.
        head_txt = gui.fid_head.cget("text").upper()
        warn_txt = gui.fid_warn.cget("text").upper()
        check("UNVALIDATED AS A PREDICTOR AT OUR CURRENT LOW FIDELITY" in head_txt,
              f"fidelity: the banner SCOPES the null to our current low fidelity "
              f"(got {head_txt[:80]!r})")
        check("EXPECTED TO BECOME PREDICTIVE AS FIDELITY RISES" in head_txt,
              f"fidelity: the banner carries the clause the owner argued for (got {head_txt!r})")
        check("NOT USABLE AS A PERFORMANCE CLAIM TODAY" in head_txt,
              "fidelity: and the clause that actually prevents the failure mode is still there")
        check("IT DOES NOT SAY HOW WELL THAT PART WORKS" in warn_txt,
              f"fidelity: the banner still denies that this measures how well anything works "
              f"(got {warn_txt[:150]!r})")
        # THE OVERREACH MUST BE GONE FROM THE SCREEN, not merely softened somewhere in the data.
        check("HAS NOT BEEN SHOWN TO PREDICT" not in (head_txt + warn_txt),
              "fidelity NEGATIVE CONTROL: the unscoped 'has NOT been shown to predict' wording is "
              "no longer anywhere on the banner")
        check("TOO LITTLE EVIDENCE TO TELL IS NOT THE SAME STATEMENT AS NO RELATIONSHIP"
              in warn_txt,
              "fidelity: the banner names exactly what the old wording overreached into")
        check("HARDEST TO DETECT" in warn_txt,
              "fidelity: it says WHY six low-fidelity points are the worst place to look")
        check("OWNER'S ARGUMENT" in warn_txt and "NOT AS A MEASUREMENT" in warn_txt,
              "fidelity: the owner's reasoning is on screen AS AN ARGUMENT, explicitly not as "
              "something this window measured")
        check("THE TWO MISSES, KEPT ON SCREEN" in warn_txt,
              f"fidelity: the two named misses are still rendered (got {warn_txt[-400:-200]!r})")
        check("TWO POINTS, NOT A REFUTATION" in warn_txt,
              "fidelity: and they are framed as two points rather than as a refutation")
        check("62%" in warn_txt and "25%" in warn_txt,
              f"fidelity: the miss carries its actual numbers, re-derived from the tool")
        check("P ~ 0.17" in warn_txt or "1 IN 6" in warn_txt,
              f"fidelity: the banner carries WHY it is unvalidated, not just the word "
              f"(got {warn_txt[-200:]!r})")
        check("THE SCORING TOOL'S OWN VERDICT, VERBATIM" in warn_txt and "UNVALIDATED" in warn_txt,
              "fidelity: the tool's own verdict is still quoted verbatim beneath the framing")
        # THE RANGE, on screen, so the owner can judge the band rather than be told about it.
        cap_txt = gui.fid_scatter_cap.cget("text")
        check("THE BAND ACTUALLY TESTED" in cap_txt.upper(),
              f"fidelity: the range of scores actually observed is printed (got {cap_txt[:120]!r})")
        check("0%" in cap_txt and "100%" in cap_txt,
              f"fidelity: and it prints the real endpoints rather than characterising them "
              f"(got {cap_txt[:200]!r})")
        # THE SCATTER, drawn, with its n visible.
        items = gui.fid_canvas.find_all()
        check(len(items) > 10,
              f"fidelity: the six-point scatter is actually drawn (got {len(items)} canvas items)")
        texts = " ".join(str(gui.fid_canvas.itemcget(i, "text"))
                         for i in items if gui.fid_canvas.type(i) == "text")
        check("N = 6" in texts.upper(),
              f"fidelity: the scatter states its n on the chart (got {texts[:120]!r})")
        ovals = [i for i in items if gui.fid_canvas.type(i) == "oval"]
        check(len(ovals) == 6,
              f"fidelity: six points means six dots -- exact ties are nudged apart, not merged "
              f"(got {len(ovals)})")
        check("THE RESULT HELD" in texts.upper() and "IT DID NOT HOLD" in texts.upper(),
              "fidelity: the outcome axis is labelled in plain words")
        # The organ header must state the deliberate backlog rather than hiding it.
        oh = gui.organ_hint.cget("text")
        check("deliberately do not" in oh,
              f"the organ header reports the empty-brain-structure backlog (got {oh[:90]!r})")
        check("CONFLICT" in oh,
              f"the organ header reports the section-10-versus-section-4 conflicts rather than "
              f"silently picking one reading (got {oh[-200:]!r})")

        # every panel MISSING
        # DEFECT B: this window now deliberately REFUSES to rebuild the WAITING ON YOU tab while a
        # row is selected (see _board_engaged) -- and the defect-B probe above left one selected on
        # purpose. This section is testing a DIFFERENT thing (every panel degrades correctly), so
        # it disengages first, the same way an owner would before walking away, rather than being
        # silently frozen on the LIVE render's stale board state.
        gui.board_tv.selection_remove(*gui.board_tv.selection())
        gui.answer_box.delete("1.0", "end")
        gui._last_error = None
        missing = {"ts": "x", "took_s": 0.0,
                   "plan": {"status": "MISSING", "detail": "the plan document is gone"},
                   "scores": {"status": "MISSING", "detail": "both score sources gone"},
                   "drift": {"n_drifted": 0, "n_unknown": 4, "parts": []},
                   "walls": {"status": "MISSING", "detail": "spec gone"},
                   "board": {"status": "MISSING", "detail": "board gone"},
                   "running": {"status": "ERROR", "detail": "monitor gone",
                               "agents": {"status": "MISSING", "detail": "no transcripts"},
                               "alerts": [], "gpu": {}, "local_experiments": [],
                               "remote_checkpoint": {"state": "UNKNOWN", "reason": "ssh down"}},
                   "results": {"status": "MISSING", "detail": "no data dir"},
                   "loop": {"status": "ERROR", "detail": "autoloop gone", "armed": None},
                   "progress": {"status": "MISSING", "detail": "progress ledger gone"},
                   "organs": {"status": "MISSING", "detail": "organ map and registry gone"},
                   "fidelity": {"status": "MISSING", "detail": "scoring tool gone"}}
        gui.render(missing)
        check(gui._last_error is None,
              f"renders an ALL-MISSING state with no panel error ({gui._last_error})")
        check("MISSING" in gui.headline_lbl.cget("text").upper(),
              "the headline SAYS the plan is missing rather than showing a remembered one")
        check("MISSING" in gui.where_detail.get("1.0", "end").upper(),
              "the plan panel tells the reader it is MISSING")
        check(len(gui.where_tv.get_children()) <= 1,
              "the plan panel draws no phases it does not have")
        check("MISSING" in gui.sc_detail.get("1.0", "end").upper(),
              "the scores panel tells the reader it is MISSING")
        check(str(gui.answer_btn.state()).find("disabled") >= 0,
              "the answer button is DISABLED when the board is unreadable")
        check("UNKNOWN" in gui.running_detail.get("1.0", "end").upper(),
              "remote liveness renders as UNKNOWN, not as idle")
        check("UNKNOWN" in gui.loop_big.cget("text").upper(),
              "the overnight loop renders as UNKNOWN inside the running tab, not as off")
        check("MISSING" in gui.organ_detail.get("1.0", "end").upper(),
              "the organ map tells the reader it is MISSING")
        check("MISSING" in gui.fid_detail.get("1.0", "end").upper(),
              "the fidelity panel tells the reader it is MISSING rather than showing a number")
        check(len(gui.organ_tv.get_children()) <= 1,
              "the organ map draws no organs it does not have")
        # THE ALL-MISSING PAYLOAD CARRIES NO `ages` KEY AT ALL, which is the sharpest test of the
        # rule: with no age data whatsoever, a cell must say UNKNOWN and must never fall back to
        # the refresh clock. A window that fills a blank with `now()` is the failure this feature
        # was built to prevent, and it would look completely normal on screen.
        gone_cells = []
        for tname, (tv, col) in age_tables.items():
            gone_cells += [str(tv.item(i, "values")[col]) for i in tv.get_children()
                           if len(tv.item(i, "values")) > col]
        check(all(("UNKNOWN" in c or not c.strip()) for c in gone_cells),
              f"ages/all-missing: with no age data at all, every cell says UNKNOWN -- not a time "
              f"({[c for c in gone_cells if c.strip() and 'UNKNOWN' not in c][:4]})")
        check(not any("just now" in c or "ago" in c for c in gone_cells),
              f"ages/all-missing NEGATIVE CONTROL: NOT ONE cell invents an age "
              f"({[c for c in gone_cells if 'ago' in c][:4]})")
        check("MISSING" in gui.sc_detail.get("1.0", "end").upper()
              and "exactly:" not in gui.sc_detail.get("1.0", "end"),
              "ages/all-missing: the detail box shows NO timestamp at all rather than last "
              "refresh's one")
        check("MISSING" in gui.headsub_lbl.cget("text")
              or "UNKNOWN" in gui.headsub_lbl.cget("text"),
              f"ages/all-missing: the top strip reports the age data as unavailable "
              f"(got {gui.headsub_lbl.cget('text')[-90:]!r})")
        # And the fidelity banner must degrade too, rather than keeping last refresh's framing.
        check("MISSING" in gui.fid_head.cget("text").upper(),
              f"fidelity/all-missing: the banner says MISSING instead of leaving the corrected "
              f"framing standing over no data (got {gui.fid_head.cget('text')[:70]!r})")
        gone_items = gui.fid_canvas.find_all()
        gone_ovals = [i for i in gone_items if gui.fid_canvas.type(i) == "oval"]
        gone_text = " ".join(str(gui.fid_canvas.itemcget(i, "text")) for i in gone_items
                             if gui.fid_canvas.type(i) == "text").upper()
        check(not gone_ovals,
              f"fidelity/all-missing: the scatter draws NO points rather than keeping last "
              f"refresh's (got {len(gone_ovals)} dots)")
        check("NO SCORED POINTS" in gone_text,
              f"fidelity/all-missing: and it SAYS there is nothing to plot instead of showing an "
              f"empty chart that reads as zero (got {gone_text[:120]!r})")

        # structurally wrong types everywhere
        gui._last_error = None
        garbage = {"ts": None, "took_s": None, "plan": 3.14, "scores": "not a dict",
                   "drift": [1, 2], "walls": "not a dict", "board": 42,
                   "running": ["nope"], "results": None, "loop": "?"}
        gui.render(garbage)
        check(gui._last_error is None,
              f"survives structurally wrong types in every panel ({gui._last_error})")
        check(bool(root.winfo_exists()), "the window is still alive after all three states")

        # THE WRITE-BACK GUARDS, through the button path. Every branch must SAY what it did:
        # "Save does nothing" was the owner's report on 2026-08-16, and an operation whose failure
        # is invisible is indistinguishable from one that does nothing. The panel's full behaviour
        # (selection restore, per-question drafts, the caption, the round trip) is covered by
        # verification/test_board_answer_panel.py; these three are the button-path guards.
        gui._selected_qid = None
        gui._answer_for = None
        gui.answer_box.delete("1.0", "end")
        gui.answer_box.insert("1.0", "an answer with nothing selected")
        gui._save_answer()
        check("NOT SAVED" in gui.answer_status.cget("text").upper(),
              f"pressing Save with nothing selected SAYS it did not save, rather than doing "
              f"nothing visible ({gui.answer_status.cget('text')[:70]!r})")
        check(gui.answer_box.get("1.0", "end").strip() != "",
              "and it does NOT discard what the owner typed")
        # The box and the selection disagreeing is the mis-attachment defect. It must refuse.
        gui._selected_qid = "Q_SELECTED_SELFTEST"
        gui._answer_for = "Q_TYPED_FOR_SOMETHING_ELSE"
        gui._save_answer()
        check("NOT SAVED" in gui.answer_status.cget("text").upper()
              and "Q_TYPED_FOR_SOMETHING_ELSE" in gui.answer_status.cget("text"),
              f"a draft written for one question is REFUSED against a different selected "
              f"question, and the refusal names both ({gui.answer_status.cget('text')[:90]!r})")
        # And an id that is not on the board at all is refused by board.py itself.
        gui._selected_qid = "Q_DOES_NOT_EXIST_SELFTEST"
        gui._answer_for = "Q_DOES_NOT_EXIST_SELFTEST"
        gui._save_answer()
        check("REFUSED" in gui.answer_status.cget("text").upper(),
              f"answering an unknown question id is REFUSED "
              f"({gui.answer_status.cget('text')[:70]})")
        check("NOT SAVED" in gui.answer_status.cget("text").upper(),
              "and the refusal leads with the fact that nothing was written")
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="hd-instrument status window")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--single-instance", action="store_true",
                    help="kill any other status_gui.py first (never touches dash_gui.py)")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.single_instance:
        _enforce_single_instance()
    root = tk.Tk()
    StatusWindow(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
