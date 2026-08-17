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

THREE GROUPS, SEVEN TABS -- DOWN FROM EIGHT, WITH THE PLAN ADDED. Eight tabs was already a lot;
adding a ninth would have made the reorganisation worse than the problem. What was merged, and why:

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

THE NOTE BOX AT THE BOTTOM (*"a box that I can write any commentary I'd like you to look at during a
run without interrupting you... a hook on that that tells you that I've sent something"*). It is
under the notebook rather than on a tab, because a note is written while looking at whatever the
owner was already looking at. It appends to `notes/COMMENTARY.md`, and BOTH
`tools/session_start_hook.py` and the Stop hook's continuation path (GUARD 3e) surface anything
unread -- the Stop hook being the half that reaches an unattended overnight run mid-flight. Unread
is derived from the file's own contents, never from a flag this window sets, so a note typed into
the markdown from a phone is noticed identically. Guarded by
`verification/test_commentary_channel.py` (20 checks).

Keys: F5 or r = refresh now. Ctrl+1..7 = jump to a panel.

  python tools/status_gui.py --self-test    # renders normal / degraded / garbage states
  python verification/test_board_answer_panel.py     # the answer panel's own witness
  python verification/test_board_answerable_all.py   # every row is answerable
  python verification/test_status_running_panel.py   # widths, resizing, dead-but-claimed-live
  python verification/test_commentary_channel.py     # the note box and both hooks
"""
from __future__ import annotations

import argparse
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

REFRESH_MS = 20000        # collection costs ~2.5s; 20s is live enough and stays cheap
TICK_MS = 1000
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
        for i in range(7):
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
        st.configure("Treeview", background=_PANEL, foreground=_FG,
                     fieldbackground=_PANEL, bordercolor=_BORDER, rowheight=24)
        st.map("Treeview", background=[("selected", _SEL_BG)],
               foreground=[("selected", "#ffffff")])
        st.configure("Treeview.Heading", background=_HEAD_BG, foreground="#d4d4d4",
                     relief="flat", font=("Segoe UI", 9, "bold"))
        st.map("Treeview.Heading", background=[("active", _HEAD_BG)])
        st.configure("Vertical.TScrollbar", background="#3c3c3c", troughcolor=_PANEL,
                     bordercolor=_BORDER, arrowcolor=_FG,
                     darkcolor=_PANEL, lightcolor=_PANEL)

    def _tree(self, parent, cols, widths, headings, height=8, minwidths=None, stretch_all=False):
        """A table. `minwidths` and `stretch_all` exist because of the 2026-08-16 owner report:
        *"the current runs have very small fields for me to see what's currently running."*

        Two separate faults produced that. (1) Only columns already >=200 px wide were allowed to
        stretch, so widening the window grew the columns that were ALREADY roomy and left the
        narrow ones -- the ones holding the run's identity -- exactly as cramped as before.
        (2) Nothing set a MINIMUM, so Tk was free to shrink a column below the width of the text in
        it. `stretch_all` makes every column share the extra space; `minwidths` puts a floor under
        each one so the identity of a run can never be squeezed into an ellipsis."""
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tv = ttk.Treeview(frame, columns=cols, show="headings", height=height)
        mins = list(minwidths) if minwidths else [None] * len(cols)
        for c, w, h, mn in zip(cols, widths, headings, mins):
            tv.heading(c, text=h)
            tv.column(c, width=w, anchor="w",
                      minwidth=int(mn if mn is not None else min(w, 90)),
                      stretch=(True if stretch_all else (w >= 200)))
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

    def _detail(self, parent, height=7):
        t = tk.Text(parent, height=height, wrap="word", bd=0, padx=10, pady=8,
                    bg=_ALT, fg=_FG, insertbackground=_FG, highlightthickness=0,
                    font=("Segoe UI", 10), state="disabled")
        t.tag_configure("h", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
        t.tag_configure("bad", foreground=_RED, font=("Segoe UI", 10, "bold"))
        t.tag_configure("good", foreground=_GREEN, font=("Segoe UI", 10, "bold"))
        t.tag_configure("warn", foreground=_AMBER, font=("Segoe UI", 10, "bold"))
        t.tag_configure("dim", foreground=_DIM)
        t.tag_configure("mono", font=("Consolas", 9), foreground=_DIM)
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
        self.headline_lbl = tk.Label(head, text="loading...", bg=_RED_BG, fg="#ffffff",
                                     font=("Segoe UI", 15, "bold"), anchor="w",
                                     justify="left", padx=14)
        self.headline_lbl.grid(row=0, column=0, sticky="ew", pady=(9, 2))
        self.headsub_lbl = tk.Label(head, text="", bg=_RED_BG, fg="#f0e6e5",
                                    font=("Segoe UI", 10), anchor="w", justify="left",
                                    padx=14)
        self.headsub_lbl.grid(row=1, column=0, sticky="ew", pady=(0, 9))
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

        self._build_commentary(root)

        bar = ttk.Frame(root)
        bar.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 6))
        bar.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(bar, text="starting...", anchor="w", foreground=_DIM)
        self.status_lbl.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Refresh (F5)", command=self.refresh_now).grid(row=0, column=1)

    # ---- the side channel (always on screen, on every tab) -------------
    def _build_commentary(self, root) -> None:
        """A box for anything the owner wants looked at, without interrupting a run.

        Owner, 2026-08-16: *"a box that I can write any commentary I'd like you to look at during a
        run without interrupting you... a hook on that that tells you that I've sent something to
        look at during a computational run."*

        IT IS NOT ON A TAB, and that is the design. A note is written when the owner thinks of it,
        which is while they are looking at whatever they were already looking at -- putting it
        behind a tab means finding the tab first. It sits under the notebook and is present on all
        seven panels.

        THE CONFIRMATION QUOTES THE TEXT AND NAMES THE FILE. That is not politeness: the Save
        button on the panel above failed silently for hours and the owner had no way to tell, and
        the whole value of this channel is the owner's confidence that the note landed. So a
        success echoes what was written and where, and a failure says the write did not happen and
        leaves the text in the box.

        IT IS NOT THE ONLY WAY IN. `notes/COMMENTARY.md` is a plain markdown file; typing into it
        from a phone works identically, because unread is derived from the file's contents rather
        than from a flag this window sets."""
        wrap = ttk.LabelFrame(root, text="A NOTE FOR ME -- write anything here; it does not "
                                         "interrupt whatever is running")
        wrap.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 4))
        wrap.columnconfigure(0, weight=1)
        self.commentary_frame = wrap
        self.commentary_box = tk.Text(wrap, height=2, wrap="word", bd=0, padx=8, pady=5,
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
                                          font=("Segoe UI", 9), wraplength=1100, justify="left")
        self.commentary_status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8,
                                    pady=(0, 5))

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
                                    justify="left", wraplength=1200)
        self.where_phase.grid(row=0, column=0, sticky="ew", pady=(9, 2))
        self.where_next = tk.Label(now, text="", bg=_GREEN_BG, fg="#e8f4e9",
                                   font=("Segoe UI", 11), anchor="w", justify="left",
                                   padx=12, wraplength=1200)
        self.where_next.grid(row=1, column=0, sticky="ew", pady=(0, 9))

        self.where_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                   anchor="w", justify="left", wraplength=1200, padx=4, pady=4)
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
        self.nb.add(f, text="4. SCORES AND FLOORS")
        self.tab_scores = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        gov = tk.Frame(f, bg=_RED_BG)
        gov.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        gov.columnconfigure(0, weight=1)
        self.sc_gov_title = tk.Label(gov, text="", bg=_RED_BG, fg="#ffffff",
                                     font=("Segoe UI", 12, "bold"), anchor="w", padx=12,
                                     justify="left", wraplength=1200)
        self.sc_gov_title.grid(row=0, column=0, sticky="ew", pady=(8, 2))
        self.sc_gov_body = tk.Label(gov, text="", bg=_RED_BG, fg="#f4e9e8",
                                    font=("Segoe UI", 10), anchor="w", justify="left",
                                    padx=12, wraplength=1200)
        self.sc_gov_body.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.sc_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                anchor="w", justify="left", wraplength=1200, padx=4, pady=4)
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
        self.nb.add(f, text="5. BRAIN ORGAN MAP")
        self.tab_organs = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        self.organ_hint = tk.Label(f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10),
                                   anchor="w", justify="left", wraplength=1200, padx=4, pady=6)
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
        self.nb.add(f, text="6. HOW CLOSELY WE COPY THE BRAIN")
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
            justify="left", padx=12, wraplength=1200)
        self.fid_head.grid(row=0, column=0, sticky="ew", pady=(8, 2))
        self.fid_warn = tk.Label(warn, text="", bg=_AMBER_BG, fg="#f7ecd8",
                                 font=("Segoe UI", 10), anchor="w", justify="left",
                                 padx=12, wraplength=1200)
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
                                        wraplength=1200, padx=4)
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
        documents to find out what was waiting on them."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="3. WAITING ON YOU")
        self.tab_board = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        self.board_hint = tk.Label(
            f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10), anchor="w",
            justify="left", wraplength=1180, padx=4, pady=6)
        self.board_hint.grid(row=0, column=0, sticky="ew")

        frame, self.board_tv = self._tree(
            f, cols=("id", "kind", "question", "now", "updated"),
            widths=(60, 175, 545, 300, 150),
            headings=("#", "", "WHAT NEEDS YOUR DECISION",
                      "WHAT HAPPENS IF YOU SAY NOTHING", "RECORDED / LAST UPDATED"), height=12)
        frame.grid(row=1, column=0, sticky="nsew")
        self.board_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_board_detail())

        self.board_detail = self._detail(f, height=10)
        self.board_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        # THE CAPTION IS LOAD-BEARING, not decoration. It names the exact question this box will
        # write to, and it is the only thing standing between the owner and an answer attached to
        # the wrong row. It is rewritten on every selection change by _sync_answer_ui().
        ans = ttk.LabelFrame(f, text="YOUR ANSWER")
        self.answer_frame = ans
        ans.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        ans.columnconfigure(0, weight=1)
        self.answer_box = tk.Text(ans, height=3, wrap="word", bd=0, padx=8, pady=6,
                                  bg="#1b1b1b", fg=_FG, insertbackground=_FG,
                                  highlightthickness=1, highlightbackground=_BORDER,
                                  font=("Segoe UI", 11))
        self.answer_box.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        # Keystrokes are captured into the per-question draft as they happen, so that a refresh
        # landing between the last keypress and the button press cannot lose them.
        self.answer_box.bind("<KeyRelease>", lambda _e: self._stash_draft())
        btns = ttk.Frame(ans)
        btns.grid(row=0, column=1, sticky="ns", padx=(0, 6))
        self.answer_btn = ttk.Button(btns, text="Save my answer", command=self._save_answer)
        self.answer_btn.grid(row=0, column=0, sticky="ew", pady=(6, 3))
        # THE ESCAPE HATCH. On the night this panel was reported broken the board had ZERO open
        # questions, so every selectable row was a DECISION or a STANDING item, none of which can
        # be written -- the owner typed a real answer and the panel had nowhere to put it. This
        # button gives typed text somewhere to go REGARDLESS of what is selected: it files the text
        # as its own board row, already answered, through the same tested board.py calls.
        self.note_btn = ttk.Button(btns, text="File as a new note", command=self._file_note)
        self.note_btn.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        ttk.Button(btns, text="Clear",
                   command=self._clear_answer).grid(row=2, column=0, sticky="ew")
        self.answer_status = tk.Label(ans, text="", bg=_PANEL, fg=_DIM, anchor="w",
                                      font=("Segoe UI", 9), wraplength=1180, justify="left")
        self.answer_status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))

    # ---- TAB 2 (group A) ----------------------------------------------
    def _build_running(self) -> None:
        """RUNNING NOW -- agents, experiments, the remote box, AND the overnight loop.

        The loop had its own tab. It did not need one: "is the loop on" is a question about whether
        anything is happening, which is this tab's question, and separating them meant the owner had
        to check two tabs to answer "is work still going". The stop command stays on screen with a
        copy button, because it is the one control in this window that stops the machine."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="2. RUNNING NOW")
        self.tab_running = f
        f.columnconfigure(0, weight=1)

        loop = tk.Frame(f, bg=_ALT)
        loop.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        loop.columnconfigure(0, weight=1)
        self.loop_big = tk.Label(loop, text="...", bg=_ALT, fg=_FG,
                                 font=("Segoe UI", 15, "bold"), anchor="w", padx=12)
        self.loop_big.grid(row=0, column=0, sticky="ew", pady=(8, 1))
        self.loop_sub = tk.Label(loop, text="", bg=_ALT, fg=_DIM, font=("Segoe UI", 10),
                                 anchor="w", justify="left", padx=12, wraplength=1000)
        self.loop_sub.grid(row=1, column=0, sticky="ew")
        tk.Label(loop, text="TO STOP IT, RUN THIS:", bg=_ALT, fg=_AMBER,
                 font=("Segoe UI", 9, "bold"), anchor="w",
                 padx=12).grid(row=2, column=0, sticky="ew", pady=(6, 1))
        self.disarm_box = tk.Text(loop, height=1, wrap="none", bd=0, padx=12, pady=4,
                                  bg="#1b1b1b", fg="#ffd479", insertbackground=_FG,
                                  highlightthickness=0, font=("Consolas", 12, "bold"))
        self.disarm_box.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 4))
        self.loop_alt = tk.Label(loop, text="", bg=_ALT, fg=_DIM, font=("Segoe UI", 9),
                                 anchor="w", justify="left", padx=12, wraplength=1000)
        self.loop_alt.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(loop, text="Copy the command",
                   command=self._copy_disarm).grid(row=3, column=1, padx=(6, 12))

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
                                   justify="left", wraplength=1200)
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
            justify="left", wraplength=1180, padx=4, pady=6)
        self.results_hint.grid(row=0, column=0, sticky="ew")

        frame, self.results_tv = self._tree(
            f, cols=("when", "what", "verdict", "floor", "sep", "name"),
            widths=(175, 100, 280, 150, 175, 350),
            headings=("RESULT LAST WRITTEN", "", "WHAT IT CONCLUDED", "DID IT NAME A FLOOR?",
                      "INTERVALS SEPARATED?", "EXPERIMENT"),
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
        try:
            self._q.put(("ok", status_state.collect()))
        except Exception:
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
        # This bar is the ONLY place the refresh clock appears, and it says so: every timestamp in
        # every table is an evidence age, and the two must not be read for one another.
        parts.append(f"auto-refresh every {REFRESH_MS // 1000}s  |  F5 = refresh  |  "
                     f"Ctrl+1..7 = jump to a panel  |  this clock is the REFRESH, not the age of "
                     f"anything on screen")
        self.status_lbl.configure(text="    |    ".join(parts))
        self.root.after(TICK_MS, self._tick)

    # ------------------------------------------------------------------
    # rendering -- every panel independently guarded
    # ------------------------------------------------------------------
    def render(self, s: dict) -> None:
        for name, fn in (("headline", self._r_headline), ("where", self._r_where),
                         ("scores", self._r_scores), ("organs", self._r_organs),
                         ("fidelity", self._r_fidelity),
                         ("board", self._r_board), ("running", self._r_running),
                         ("results", self._r_results)):
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
            tv.selection_set("sc0")
            tv.focus("sc0")
            self._show_score_detail()
        try:
            self.nb.tab(self.tab_scores,
                        text=f"4. SCORES AND FLOORS ({nr} retracted)" if nr
                             else "4. SCORES AND FLOORS")
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
        tv.delete(*tv.get_children())
        self._organ_rows: dict[str, dict] = {}
        if o.get("status") != "OK":
            self.organ_hint.configure(text=f"{o.get('status')}: {o.get('detail', '')}", fg=_AMBER)
            tv.insert("", "end", values=(f"{o.get('status')}", "MISSING", "?", "?", "MISSING",
                                         "UNKNOWN"), tags=("warn",))
            self._set_text(self.organ_detail,
                           [(f"{o.get('status')}\n", "warn"), str(o.get("detail", ""))])
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
            tv.selection_set("o0")
            self._show_organ_detail()
        try:
            self.nb.tab(self.tab_organs,
                        text=f"5. BRAIN ORGAN MAP ({o.get('n_missing')} not built)")
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
            tv.selection_set("f0")
            self._show_fidelity_detail()
        try:
            self.nb.tab(self.tab_fidelity,
                        text=f"6. HOW CLOSELY WE COPY THE BRAIN (n={_d(fd.get('scatter')).get('n', '?')})")
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
    def _r_board(self, s: dict) -> None:
        b = _d(s.get("board"))
        pl = _d(s.get("plan"))
        self._board_state = b
        tv = self.board_tv
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

        # Whether the DOCUMENT can be written at all. Whether the SELECTED ROW can be written is a
        # separate question and is decided in _sync_answer_ui() -- conflating the two is what left
        # the Save button enabled over a row it could never write.
        self._board_writable = bool(b.get("status") == "OK" and b.get("writable") is not False)
        parts = []
        if b.get("status") != "OK":
            parts.append(f"THE BOARD IS {b.get('status')}: {b.get('detail', '')} -- no question "
                         f"can be answered from here.")
        else:
            parts.append("EVERY ROW HERE CAN BE ANSWERED. Pick any one -- a question, a decision "
                         "or a standing item -- type below, press Save. All of them land in "
                         "notes/BOARD.md, which you can also open in any markdown editor on any "
                         "device and type into directly.")
            if b.get("writable") is False:
                self.answer_status.configure(
                    text="notes/BOARD.md is not writable from here -- answer it in the file "
                         "instead.", fg=_AMBER)
        if pl.get("status") == "OK":
            parts.append("A DECISION or STANDING answer is recorded as its own board row that "
                         "names the decision and repeats its text in full, because the plan and "
                         "status documents are read by code and nothing typed here is written into "
                         "them. Every one of these already has a default, so saying nothing IS a "
                         "choice: the right-hand column says what that choice currently is.")
        else:
            parts.append(f"The standing decisions could not be read ({pl.get('status')}).")
        parts.append(_panel_age_text(s.get("ages"), "waiting on you").strip())
        self.board_hint.configure(text="  ".join(x for x in parts if x),
                                  fg=_AMBER if b.get("status") != "OK" else _BLUE)

        i = 0
        if b.get("status") == "OK" and not self._board_rows:
            # Even the placeholder is dated. "You are up to date on the board" is itself a claim
            # read off notes/BOARD.md, and an undated claim is exactly what this column exists to
            # stop -- so it carries the panel's own newest evidence age rather than a blank.
            tv.insert("", "end", values=("-", "QUESTION", "No open question -- you are up to date "
                                                          "on the board.",
                                         "nothing; there is nothing to answer",
                                         str(_d(_d(_d(s.get("ages")).get("panels"))
                                                .get("waiting on you")).get("newest_rel")
                                             or "UNKNOWN")), tags=("dim",))
        for j, r in enumerate(self._board_rows):
            iid = f"q{j}"
            self._wait_rows[iid] = dict(r, _kind="QUESTION")
            tv.insert("", "end", iid=iid,
                      values=(r.get("id", "?"), "QUESTION (answerable here)",
                              r.get("question", ""), "it stays open", _age_cell(r)),
                      tags=("warn", "even" if i % 2 == 0 else "odd"))
            i += 1
        # WHICH OF THESE THE OWNER HAS ALREADY ANSWERED, read back out of notes/BOARD.md. A panel
        # that keeps presenting a settled decision as outstanding is the same defect as a stale
        # RUNNING row: it is read as evidence and it is wrong.
        recorded = _d(b.get("recorded"))
        for d in decisions:
            d = _d(d)
            iid = f"d{d.get('id')}"
            self._wait_rows[iid] = dict(d, _kind="DECISION")
            done = _d(recorded.get(str(d.get("id") or "").upper()))
            tv.insert("", "end", iid=iid,
                      values=(d.get("id", "?"),
                              "DECISION - ANSWERED" if done else "DECISION (answerable here)",
                              d.get("question", ""),
                              ("you answered: " + _verbatim(str(done.get("answer") or ""), 120))
                              if done else
                              ("the default happens: " + str(d.get("default") or "NONE STATED")),
                              _age_cell(d)),
                      tags=("good" if done else "dim", "even" if i % 2 == 0 else "odd"))
            i += 1
        for o in standing:
            o = _d(o)
            iid = f"o{o.get('id')}"
            self._wait_rows[iid] = dict(o, _kind="STANDING")
            drift = ("   [CHECK SOURCE]"
                     if o.get("verify_status") == "CHECK_SOURCE" else "")
            done = _d(recorded.get(str(o.get("id") or "").upper()))
            tv.insert("", "end", iid=iid,
                      values=(o.get("id", "?"),
                              "STANDING - ANSWERED" if done else "STANDING (answerable here)",
                              str(o.get("title", "")) + drift,
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
        else:
            self._set_text(self.board_detail, [("Nothing is waiting on you.\n", "good"),
                                               "No open question and no undecided standing item."])
            self._selected_qid = None
            self._sync_answer_ui(None)

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
            self.answer_frame.configure(text=cap)
        except tk.TclError:
            pass
        self.answer_btn.state(["!disabled"] if can_save else ["disabled"])
        self.note_btn.state(["!disabled"] if self._board_writable else ["disabled"])

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

        tv2 = self.local_tv
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

        n_act = ag.get("n_active", 0) if ag.get("status") == "OK" else "?"
        n_dead = cl.get("n_dead") or 0
        loop_tag = ("loop ON" if armed is True else "loop off" if armed is False else "loop ?")
        dead_tag = f", {n_dead} DEAD-BUT-CLAIMED" if n_dead else ""
        try:
            self.nb.tab(self.tab_running,
                        text=f"2. RUNNING NOW ({n_act}, {loop_tag}{dead_tag})")
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
        tv.delete(*tv.get_children())
        self._result_rows: dict[str, dict] = {}
        if res.get("status") != "OK":
            self.results_hint.configure(
                text=f"{res.get('status')}: {res.get('detail', '')}", fg=_AMBER)
            self._set_text(self.results_detail,
                           [(f"{res.get('status')}\n", "warn"), str(res.get("detail", ""))])
            return
        rows = [_d(r) for r in _l(res.get("rows"))]
        self.results_hint.configure(
            text=(f"The {len(rows)} most recent finished experiments. "
                  f"{res.get('n_negative')} of them are negative and "
                  f"{res.get('n_no_floor')} never named a floor at all -- a result with no "
                  f"floor beside it cannot be graded. Losses are shown exactly as loudly as "
                  f"wins, on purpose."
                  + _panel_age_text(s.get("ages"), "latest results")),
            fg=_AMBER if res.get("n_negative") else _BLUE)
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
            # The relative age is what reads at a glance; the exact stamp stays one click away in
            # the detail box, which is the split the owner asked for.
            tv.insert("", "end", iid=iid, values=(
                _age_cell(r), label, r.get("verdict"), floor_cell, sep, name),
                tags=(tag, "even" if i % 2 == 0 else "odd"))
        if rows:
            tv.selection_set("r0")
            self._show_result_detail()

    def _show_result_detail(self) -> None:
        sel = self.results_tv.selection()
        r = getattr(self, "_result_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        label = r.get("label", "FINDING")
        tag = {"NEGATIVE": "bad", "WIN": "good"}.get(label, "warn")
        chunks = [
            (f"{r.get('name')}\n", "h"),
            (f"{label}: {r.get('verdict')}\n\n", tag),
            f"{r.get('verdict_msg') or '(the run recorded no explanation)'}\n\n",
        ]
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
        check(len(gui.nb.tabs()) == 7,
              f"seven tabs, down from eight, with the plan added (got {len(gui.nb.tabs())})")

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
        # demanded an open question would start failing the moment the owner did their job.
        n_open_live = ((live.get("board") or {}).get("n_open")
                       if isinstance(live.get("board"), dict) else None)
        check("QUESTION" in kinds,
              f"the answerable board questions have their own kind in the same table "
              f"({n_open_live} open right now)")
        check(all(str(c[3]).strip() for c in bcells),
              f"every waiting row says what happens if the owner says nothing "
              f"({[c[0] for c in bcells if not str(c[3]).strip()]})")
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
