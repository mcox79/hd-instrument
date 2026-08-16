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

DRIFT IS ON SCREEN (job 2). Every transcribed number in this window is re-checked against the
document it came from on every refresh, and every literal the plan parser depends on is checked
against the plan. That protection used to be invisible -- a drifted row said CHECK-SOURCE in a cell
you had to scroll to. The TOTAL now sits in the top strip, so a silent divergence becomes a visible
one. A panel that could not be checked counts as UNKNOWN, never as zero.

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

WRITES. Exactly one, and only when the owner presses the button: the board answer write-back,
which goes through `board.resolve()` -- atomic temp-file-plus-replace, with its own self-test
for hand-edited boards. Nothing else on this path writes anything.

Keys: F5 or r = refresh now. Ctrl+1..7 = jump to a panel.

  python tools/status_gui.py --self-test    # renders normal / degraded / garbage states
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

REFRESH_MS = 20000        # collection costs ~2.5s; 20s is live enough and stays cheap
TICK_MS = 1000
POLL_WEDGE_S = 60         # collection is internally bounded well below this

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


def _short(name: str, n: int = 46) -> str:
    s = name or "?"
    if s.startswith("exp_"):
        s = s[4:]
    return s if len(s) <= n else s[: n - 3] + "..."


class StatusWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("hd-instrument -- where we are / what is happening")
        root.geometry("1280x860")
        root.minsize(980, 660)

        self._q: _queue.Queue = _queue.Queue()
        self._poll_inflight = False
        self._poll_started: float | None = None
        self._last_ok: float | None = None
        self._last_error: str | None = None
        self._state: dict | None = None
        self._board_rows: list[dict] = []
        self._selected_qid: str | None = None

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

    def _tree(self, parent, cols, widths, headings, height=8):
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tv = ttk.Treeview(frame, columns=cols, show="headings", height=height)
        for c, w, h in zip(cols, widths, headings):
            tv.heading(c, text=h)
            tv.column(c, width=w, anchor="w", stretch=(w >= 200))
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

        bar = ttk.Frame(root)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        bar.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(bar, text="starting...", anchor="w", foreground=_DIM)
        self.status_lbl.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Refresh (F5)", command=self.refresh_now).grid(row=0, column=1)

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
            cols=("phase", "state", "goal", "gate", "stop"),
            widths=(230, 150, 320, 340, 320),
            headings=("PHASE", "WHERE IT IS", "WHAT IT IS FOR",
                      "WHAT WOULD COUNT AS SUCCESS", "WHAT WOULD MAKE US STOP"),
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
            cols=("what", "alone", "before", "now", "dir"),
            widths=(300, 190, 280, 300, 220),
            headings=("PART OF THE MACHINE", "CAN WE MEASURE IT ALONE?",
                      "WHAT IT WAS  (and its floor)", "WHAT IT IS NOW  (and its floor)",
                      "WHERE THAT LEAVES US"),
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
            cols=("organ", "brain", "built", "state", "measured"),
            widths=(300, 300, 90, 210, 300),
            headings=("ORGAN (plain name)", "THE PART OF THE BRAIN", "BUILT?",
                      "IS IT SWITCHED ON?", "WHAT IT MEASURES"),
            height=15)
        frame.grid(row=1, column=0, sticky="nsew")
        self.organ_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_organ_detail())

        self.organ_detail = self._detail(f, height=12)
        self.organ_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

    # ---- PANEL C ------------------------------------------------------
    def _build_fidelity(self) -> None:
        """HOW CLOSELY WE COPY THE BRAIN -- and, on screen and unmissable, the fact that this
        number has NOT been shown to predict whether anything works."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="6. HOW CLOSELY WE COPY THE BRAIN")
        self.tab_fidelity = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)
        f.rowconfigure(4, weight=1)

        warn = tk.Frame(f, bg=_AMBER_BG)
        warn.grid(row=0, column=0, sticky="ew", pady=(4, 6))
        warn.columnconfigure(0, weight=1)
        tk.Label(warn, text="THIS IS NOT A SCORE FOR HOW WELL ANYTHING WORKS.",
                 bg=_AMBER_BG, fg="#ffffff", font=("Segoe UI", 12, "bold"), anchor="w",
                 padx=12).grid(row=0, column=0, sticky="ew", pady=(8, 2))
        self.fid_warn = tk.Label(warn, text="", bg=_AMBER_BG, fg="#f7ecd8",
                                 font=("Segoe UI", 10), anchor="w", justify="left",
                                 padx=12, wraplength=1200)
        self.fid_warn.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        tk.Label(f, text="WHAT WE SCORED, AND WHAT ACTUALLY HAPPENED TO IT",
                 bg=_PANEL, fg=_BLUE, anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=1, column=0, sticky="ew", pady=(2, 2))
        frame, self.fid_tv = self._tree(
            f, cols=("thing", "pct", "outcome"),
            widths=(360, 190, 640),
            headings=("WHAT WAS SCORED", "HOW CLOSELY WE COPY THE BRAIN",
                      "WHAT ACTUALLY HAPPENED WHEN IT WAS MEASURED"),
            height=7)
        frame.grid(row=2, column=0, sticky="nsew")
        self.fid_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_fidelity_detail())

        tk.Label(f, text="WHERE OURS DIVERGES FROM THE BIOLOGY, ORGAN BY ORGAN",
                 bg=_PANEL, fg=_BLUE, anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=3, column=0, sticky="ew", pady=(8, 2))
        frame2, self.fid_div_tv = self._tree(
            f, cols=("organ", "shape", "position", "metric", "pinned"),
            widths=(390, 170, 190, 190, 250),
            headings=("ORGAN", "IS IT THE SAME OPERATION?", "IS IT IN THE RIGHT PLACE?",
                      "IS IT JUDGED THE BRAIN'S WAY?", "DOES THE SCIENCE PIN THIS DOWN?"),
            height=8)
        frame2.grid(row=4, column=0, sticky="nsew")
        self.fid_div_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_fidelity_detail(True))

        self.fid_detail = self._detail(f, height=9)
        self.fid_detail.grid(row=5, column=0, sticky="ew", pady=(6, 0))

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
            f, cols=("id", "kind", "question", "now"), widths=(60, 190, 640, 330),
            headings=("#", "", "WHAT NEEDS YOUR DECISION",
                      "WHAT HAPPENS IF YOU SAY NOTHING"), height=12)
        frame.grid(row=1, column=0, sticky="nsew")
        self.board_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_board_detail())

        self.board_detail = self._detail(f, height=10)
        self.board_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        ans = ttk.LabelFrame(f, text="YOUR ANSWER (typing here writes straight into notes/BOARD.md)")
        ans.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        ans.columnconfigure(0, weight=1)
        self.answer_box = tk.Text(ans, height=3, wrap="word", bd=0, padx=8, pady=6,
                                  bg="#1b1b1b", fg=_FG, insertbackground=_FG,
                                  highlightthickness=1, highlightbackground=_BORDER,
                                  font=("Segoe UI", 11))
        self.answer_box.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        btns = ttk.Frame(ans)
        btns.grid(row=0, column=1, sticky="ns", padx=(0, 6))
        self.answer_btn = ttk.Button(btns, text="Save my answer", command=self._save_answer)
        self.answer_btn.grid(row=0, column=0, sticky="ew", pady=(6, 3))
        ttk.Button(btns, text="Clear",
                   command=lambda: self.answer_box.delete("1.0", "end")).grid(row=1, column=0,
                                                                              sticky="ew")
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
        f.rowconfigure(2, weight=1)
        f.rowconfigure(4, weight=1)

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

        tk.Label(f, text="AGENTS", bg=_PANEL, fg=_BLUE, anchor="w",
                 font=("Segoe UI", 10, "bold"), padx=4).grid(row=1, column=0, sticky="ew",
                                                             pady=(6, 2))
        frame, self.agents_tv = self._tree(
            f, cols=("state", "name", "doing", "running", "last"),
            widths=(110, 210, 520, 130, 150),
            headings=("", "AGENT", "WHAT IT IS DOING", "RUNNING FOR", "LAST ACTIVE"),
            height=6)
        frame.grid(row=2, column=0, sticky="nsew")

        tk.Label(f, text="EXPERIMENTS RUNNING ON THIS MACHINE", bg=_PANEL, fg=_BLUE,
                 anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=3, column=0, sticky="ew", pady=(8, 2))
        frame2, self.local_tv = self._tree(
            f, cols=("name", "progress", "running", "pid", "mem"),
            widths=(430, 330, 130, 90, 100),
            headings=("EXPERIMENT", "PROGRESS", "RUNNING FOR", "PROCESS", "MEMORY"),
            height=5)
        frame2.grid(row=4, column=0, sticky="nsew")

        self.running_detail = self._detail(f, height=10)
        self.running_detail.grid(row=5, column=0, sticky="ew", pady=(8, 0))

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
            widths=(120, 110, 300, 160, 190, 380),
            headings=("WHEN", "", "WHAT IT CONCLUDED", "DID IT NAME A FLOOR?",
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
        parts.append(f"auto-refresh every {REFRESH_MS // 1000}s  |  F5 = refresh  |  "
                     f"Ctrl+1..5 = jump to a panel")
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
                                         "MISSING", "MISSING"), tags=("warn",))
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
                  f"before/now numbers attached."),
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
            tv.insert("", "end", values=(f"{m.get('status')}", "-", "MISSING", "MISSING", ""),
                      tags=("warn",))
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
                  f"than one being picked."),
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
                      values=(title, inst_txt, before, now, stand_txt),
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
                              "RETRACTED" + ("  (no floor)" if gap else "")),
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
            tv.insert("", "end", values=(f"{o.get('status')}", "MISSING", "?", "?", "MISSING"),
                      tags=("warn",))
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
                  f"after the fact is banned -- so the backlog is shown rather than hidden."),
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
                      values=(organ, str(brain)[:120], built, state, measured),
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
            self.fid_warn.configure(text=str(fd.get("detail", ""))[:500])
            tv.insert("", "end", values=("MISSING", "MISSING", str(fd.get("detail", ""))[:120]),
                      tags=("warn",))
            self._set_text(self.fid_detail, [("MISSING\n", "warn"), str(fd.get("detail", ""))])
            return

        # THE WARNING, read from the scoring tool itself rather than paraphrased here, so that if
        # the tool's own verdict ever changes this panel changes with it.
        self.fid_warn.configure(
            text=(f"{fd.get('headline', '')}\n\n{fd.get('validation_verdict', '')}"))

        for i, r in enumerate(_l(fd.get("rows"))):
            r = _d(r)
            iid = f"f{i}"
            self._fid_rows[iid] = r
            pct = r.get("pct")
            pct_s = (f"{pct * 100:.0f}%  ({r.get('points')} of {r.get('max')})"
                     if isinstance(pct, (int, float)) else "not scored")
            outcome = str(r.get("outcome") or "")
            # Colour by the OUTCOME, never by the fidelity score. Colouring by the score would
            # imply the score means something about the result, which is the exact claim this
            # panel exists to deny.
            tag = "good" if r.get("held") else "bad"
            tv.insert("", "end", iid=iid,
                      values=(str(r.get("component") or "?"), pct_s, outcome[:220]),
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
                               r.get("position"), r.get("metric"), pin_s),
                       tags=(tag, "even" if i % 2 == 0 else "odd"))
        if not _l(fd.get("divergence")):
            tv2.insert("", "end", values=(str(fd.get("divergence_detail")
                                              or "the organ map is not readable -- MISSING"),
                                          "", "", "", ""), tags=("warn",))
        if self._fid_rows:
            tv.selection_set("f0")
            self._show_fidelity_detail()

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
            ])
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
        chunks += [("\nWHY THIS NUMBER MUST NOT BE READ AS A PREDICTION\n", "bad"),
                   f"{st.get('validation_verdict', '')}\n"]
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

        parts = []
        if b.get("status") != "OK":
            parts.append(f"THE BOARD IS {b.get('status')}: {b.get('detail', '')} -- no question "
                         f"can be answered from here.")
            self.answer_btn.state(["disabled"])
        else:
            parts.append("Type your decision below and press Save -- QUESTION rows are written "
                         "straight into notes/BOARD.md. You can also answer without this window: "
                         "open notes/BOARD.md in any markdown editor on any device, type into the "
                         "ANSWER cell, and save.")
            if b.get("writable") is False:
                self.answer_btn.state(["disabled"])
                self.answer_status.configure(
                    text="notes/BOARD.md is not writable from here -- answer it in the file "
                         "instead.", fg=_AMBER)
            else:
                self.answer_btn.state(["!disabled"])
        if pl.get("status") == "OK":
            parts.append(f"DECISION and STANDING rows are NOT answerable here -- they are recorded "
                         f"in the plan and status documents and need an edit there. Every one of "
                         f"them already has a default, so saying nothing IS a choice: the "
                         f"right-hand column says what that choice currently is.")
        else:
            parts.append(f"The standing decisions could not be read ({pl.get('status')}).")
        self.board_hint.configure(text="  ".join(parts),
                                  fg=_AMBER if b.get("status") != "OK" else _BLUE)

        i = 0
        if b.get("status") == "OK" and not self._board_rows:
            tv.insert("", "end", values=("-", "QUESTION", "No open question -- you are up to date "
                                                          "on the board.",
                                         "nothing; there is nothing to answer"), tags=("dim",))
        for j, r in enumerate(self._board_rows):
            iid = f"q{j}"
            self._wait_rows[iid] = dict(r, _kind="QUESTION")
            tv.insert("", "end", iid=iid,
                      values=(r.get("id", "?"), "QUESTION (answerable here)",
                              r.get("question", ""), "it stays open"),
                      tags=("warn", "even" if i % 2 == 0 else "odd"))
            i += 1
        for d in decisions:
            d = _d(d)
            iid = f"d{d.get('id')}"
            self._wait_rows[iid] = dict(d, _kind="DECISION")
            tv.insert("", "end", iid=iid,
                      values=(d.get("id", "?"), "DECISION (from the plan)",
                              d.get("question", ""),
                              "the default happens: " + str(d.get("default") or "NONE STATED")),
                      tags=("dim", "even" if i % 2 == 0 else "odd"))
            i += 1
        for o in standing:
            o = _d(o)
            iid = f"o{o.get('id')}"
            self._wait_rows[iid] = dict(o, _kind="STANDING")
            drift = ("   [CHECK SOURCE]"
                     if o.get("verify_status") == "CHECK_SOURCE" else "")
            tv.insert("", "end", iid=iid,
                      values=(o.get("id", "?"), "STANDING (not taken)",
                              str(o.get("title", "")) + drift,
                              str(o.get("standing") or "not recorded")),
                      tags=("bad" if drift else "warn", "even" if i % 2 == 0 else "odd"))
            i += 1

        keep = None
        if self._selected_qid:
            keep = next((k for k, v in self._wait_rows.items()
                         if v.get("id") == self._selected_qid), None)
        if self._wait_rows:
            tv.selection_set(keep or next(iter(self._wait_rows)))
            self._show_board_detail()
        else:
            self._set_text(self.board_detail, [("Nothing is waiting on you.\n", "good"),
                                               "No open question and no undecided standing item."])

    def _show_board_detail(self) -> None:
        sel = self.board_tv.selection()
        r = getattr(self, "_wait_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        kind = r.get("_kind")
        # Only a board QUESTION is answerable from this window; selecting anything else must not
        # arm the Save button against a row it cannot write.
        self._selected_qid = r.get("id") if kind == "QUESTION" else None
        if kind == "QUESTION":
            self._set_text(self.board_detail, [
                (f"{r.get('id')}  {r.get('question')}\n\n", "h"),
                ("WHAT IS BLOCKED ON IT\n", "warn"),
                f"{r.get('why') or '(not recorded)'}\n\n",
                ("MY RECOMMENDATION\n", "good"),
                f"{r.get('rec') or '(none)'}\n\n",
                ("You can answer this one by typing below and pressing Save.\n", "dim"),
            ])
            return
        if kind == "DECISION":
            self._set_text(self.board_detail, [
                (f"{r.get('id')}  {r.get('question')}\n\n", "h"),
                ("WHY IT IS OPEN\n", "warn"), f"{r.get('why') or '(not recorded)'}\n\n",
                ("WHAT HAPPENS IF YOU SAY NOTHING\n", "good"),
                f"{r.get('default') or 'NO DEFAULT IS STATED, so nothing happens at all.'}\n\n",
                ("Read live out of notes/PLAN.md section 9 on every refresh. It is not "
                 "answerable from this window -- deciding it means editing that document.\n",
                 "dim"),
            ])
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
        self._set_text(self.board_detail, chunks)

    def _save_answer(self) -> None:
        text = self.answer_box.get("1.0", "end").strip()
        qid = self._selected_qid
        if not qid:
            self.answer_status.configure(
                text="Pick a question first. Only QUESTION rows can be answered from this window "
                     "-- DECISION and STANDING rows live in the plan and status documents and "
                     "have to be decided there.", fg=_AMBER)
            return
        ok, msg = status_state.answer_question(qid, text)
        self.answer_status.configure(text=msg, fg=_GREEN if ok else _RED)
        if ok:
            self.answer_box.delete("1.0", "end")
            self._selected_qid = None
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
                                         str(ag.get("detail", ""))[:60], "", "", ""),
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
                    _fmt_dur(a.get("elapsed_s")), f"{_fmt_dur(a.get('idle_s'))} ago",
                ), tags=(tag, "even" if i % 2 == 0 else "odd"))

        tv2 = self.local_tv
        tv2.delete(*tv2.get_children())
        lx = [_d(e) for e in _l(rn.get("local_experiments"))]
        if not lx:
            tv2.insert("", "end", values=("nothing running directly on this machine",
                                          "", "", "", ""), tags=("dim",))
        for i, e in enumerate(lx):
            prog = ""
            if e.get("progress_pct") is not None:
                prog = (f"{e.get('unit_idx')}/{e.get('total_units')} "
                        f"{int(e['progress_pct'])}%")
                if e.get("eta_s"):
                    prog += f"  about {_fmt_dur(e['eta_s'])} left"
                if e.get("phase"):
                    prog += f"  ({e['phase']})"
            tv2.insert("", "end", values=(
                _short(e.get("name", "?"), 58), prog or "no progress reported",
                _fmt_dur(e.get("elapsed_s")), e.get("pid", "?"),
                f"{int((e.get('mem_kb') or 0) / 1024)} MB",
            ), tags=("even" if i % 2 == 0 else "odd",))

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
        self._set_text(self.running_detail, chunks)

        n_act = ag.get("n_active", 0) if ag.get("status") == "OK" else "?"
        loop_tag = ("loop ON" if armed is True else "loop off" if armed is False else "loop ?")
        try:
            self.nb.tab(self.tab_running, text=f"2. RUNNING NOW ({n_act}, {loop_tag})")
        except tk.TclError:
            pass

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
                  f"wins, on purpose."),
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
            tv.insert("", "end", iid=iid, values=(
                r.get("when"), label, r.get("verdict"), floor_cell, sep, name),
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
        # The fidelity warning must be ON SCREEN, not merely in the data.
        warn_txt = gui.fid_warn.cget("text").upper()
        check("UNVALIDATED" in warn_txt,
              f"the fidelity panel says UNVALIDATED on screen (got {warn_txt[:70]!r})")
        check("NOT A MEASURE OF HOW WELL" in warn_txt,
              "the fidelity panel's banner denies that the score measures how well it works")
        check("P ~ 0.17" in warn_txt or "1/6" in warn_txt,
              f"the banner carries WHY it is unvalidated, not just the word "
              f"(got {warn_txt[-160:]!r})")
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

        # structurally wrong types everywhere
        gui._last_error = None
        garbage = {"ts": None, "took_s": None, "plan": 3.14, "scores": "not a dict",
                   "drift": [1, 2], "walls": "not a dict", "board": 42,
                   "running": ["nope"], "results": None, "loop": "?"}
        gui.render(garbage)
        check(gui._last_error is None,
              f"survives structurally wrong types in every panel ({gui._last_error})")
        check(bool(root.winfo_exists()), "the window is still alive after all three states")

        # the write-back guard, through the button path
        gui._selected_qid = None
        gui._save_answer()
        check("Pick a question" in gui.answer_status.cget("text"),
              "pressing Save with nothing selected refuses instead of writing")
        gui._selected_qid = "Q_DOES_NOT_EXIST_SELFTEST"
        gui.answer_box.insert("1.0", "an answer to a question that does not exist")
        gui._save_answer()
        check("REFUSED" in gui.answer_status.cget("text"),
              f"answering an unknown question id is REFUSED "
              f"({gui.answer_status.cget('text')[:70]})")
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
