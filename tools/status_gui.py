"""WHERE WE ARE / WHAT IS HAPPENING -- the owner's status window.

Launch:
  D:\\AI\\hd-instrument\\.venv\\Scripts\\python.exe D:\\AI\\hd-instrument\\tools\\status_gui.py

WHY THIS REPLACES THE OLD WINDOW. The owner's verdict on `tools/dash_gui.py` (2026-08-15):
*"that gui is ancient and it's not showing anything I care about - can you update it so it's
relevant?"* That window was built for the 4-session fleet/queue architecture, which is dead --
it is agent-spawn only now -- so it showed GPU temperature, queue depth and runner heartbeats,
and nothing about whether the system is beating what it has to beat. This one answers two
questions and only those two: WHERE ARE WE, and WHAT IS HAPPENING RIGHT NOW.

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
`inflight_monitor.build_state()`, `tools/board.py` and `tools/autoloop.py` rather than forking
a second source of truth). This file is a renderer and nothing else: it polls on a background
thread, hands the result to the Tk main thread through a queue, and every render is wrapped so
that a bad field degrades one panel instead of freezing the window.

WRITES. Exactly one, and only when the owner presses the button: the board answer write-back,
which goes through `board.resolve()` -- atomic temp-file-plus-replace, with its own self-test
for hand-edited boards. Nothing else on this path writes anything.

Keys: F5 or r = refresh now. Ctrl+1..5 = jump to a panel.

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
        for i in range(5):
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

        self._build_walls()
        self._build_board()
        self._build_running()
        self._build_results()
        self._build_loop()

        bar = ttk.Frame(root)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        bar.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(bar, text="starting...", anchor="w", foreground=_DIM)
        self.status_lbl.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Refresh (F5)", command=self.refresh_now).grid(row=0, column=1)

    # ---- PANEL 1 ------------------------------------------------------
    def _build_walls(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="1. THE WALLS")
        self.tab_walls = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        tk.Label(f, text="Every part of the machine, what it is for, and -- always side by "
                         "side -- our score and THE FLOOR IT HAS TO BEAT.",
                 bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10), anchor="w",
                 padx=4, pady=6).grid(row=0, column=0, sticky="ew")

        frame, self.walls_tv = self._tree(
            f,
            cols=("part", "alone", "ours", "floor", "standing"),
            widths=(300, 210, 190, 300, 200),
            headings=("PART OF THE MACHINE", "CAN WE MEASURE IT ON ITS OWN?",
                      "OURS", "THE FLOOR IT MUST BEAT", "WHERE THAT LEAVES US"),
            height=9)
        frame.grid(row=1, column=0, sticky="nsew")
        self.walls_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_wall_detail())

        self.walls_detail = self._detail(f, height=9)
        self.walls_detail.grid(row=2, column=0, sticky="ew", pady=(6, 0))

    # ---- PANEL 2 ------------------------------------------------------
    def _build_board(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="2. WAITING ON YOU")
        self.tab_board = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        self.board_hint = tk.Label(
            f, text="", bg=_PANEL, fg=_BLUE, font=("Segoe UI", 10), anchor="w",
            justify="left", wraplength=1180, padx=4, pady=6)
        self.board_hint.grid(row=0, column=0, sticky="ew")

        frame, self.board_tv = self._tree(
            f, cols=("id", "question"), widths=(60, 1120),
            headings=("#", "QUESTION"), height=5)
        frame.grid(row=1, column=0, sticky="nsew")
        self.board_tv.bind("<<TreeviewSelect>>", lambda _e: self._show_board_detail())

        self.board_detail = self._detail(f, height=9)
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

    # ---- PANEL 3 ------------------------------------------------------
    def _build_running(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="3. RUNNING NOW")
        self.tab_running = f
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)
        f.rowconfigure(3, weight=1)

        tk.Label(f, text="AGENTS", bg=_PANEL, fg=_BLUE, anchor="w",
                 font=("Segoe UI", 10, "bold"), padx=4).grid(row=0, column=0, sticky="ew",
                                                             pady=(6, 2))
        frame, self.agents_tv = self._tree(
            f, cols=("state", "name", "doing", "running", "last"),
            widths=(110, 210, 520, 130, 150),
            headings=("", "AGENT", "WHAT IT IS DOING", "RUNNING FOR", "LAST ACTIVE"),
            height=7)
        frame.grid(row=1, column=0, sticky="nsew")

        tk.Label(f, text="EXPERIMENTS RUNNING ON THIS MACHINE", bg=_PANEL, fg=_BLUE,
                 anchor="w", font=("Segoe UI", 10, "bold"),
                 padx=4).grid(row=2, column=0, sticky="ew", pady=(8, 2))
        frame2, self.local_tv = self._tree(
            f, cols=("name", "progress", "running", "pid", "mem"),
            widths=(430, 330, 130, 90, 100),
            headings=("EXPERIMENT", "PROGRESS", "RUNNING FOR", "PROCESS", "MEMORY"),
            height=5)
        frame2.grid(row=3, column=0, sticky="nsew")

        self.running_detail = self._detail(f, height=10)
        self.running_detail.grid(row=4, column=0, sticky="ew", pady=(8, 0))

    # ---- PANEL 4 ------------------------------------------------------
    def _build_results(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="4. LATEST RESULTS")
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

    # ---- PANEL 5 ------------------------------------------------------
    def _build_loop(self) -> None:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="5. OVERNIGHT LOOP")
        self.tab_loop = f
        f.columnconfigure(0, weight=1)

        self.loop_big = tk.Label(f, text="...", bg=_PANEL, fg=_FG,
                                 font=("Segoe UI", 26, "bold"), anchor="w", padx=10, pady=14)
        self.loop_big.grid(row=0, column=0, sticky="ew")
        self.loop_sub = tk.Label(f, text="", bg=_PANEL, fg=_FG, font=("Segoe UI", 11),
                                 anchor="w", justify="left", padx=12, wraplength=1180)
        self.loop_sub.grid(row=1, column=0, sticky="ew")

        stop = tk.Frame(f, bg=_AMBER_BG)
        stop.grid(row=2, column=0, sticky="ew", padx=10, pady=16)
        stop.columnconfigure(0, weight=1)
        tk.Label(stop, text="TO STOP IT, RUN THIS:", bg=_AMBER_BG, fg="#ffffff",
                 font=("Segoe UI", 11, "bold"), anchor="w",
                 padx=12).grid(row=0, column=0, sticky="ew", pady=(10, 2))
        self.disarm_box = tk.Text(stop, height=1, wrap="none", bd=0, padx=12, pady=6,
                                  bg="#1b1b1b", fg="#ffd479", insertbackground=_FG,
                                  highlightthickness=0, font=("Consolas", 14, "bold"))
        self.disarm_box.grid(row=1, column=0, sticky="ew", padx=12)
        self.loop_alt = tk.Label(stop, text="", bg=_AMBER_BG, fg="#f5e6c8",
                                 font=("Segoe UI", 10), anchor="w", justify="left",
                                 padx=12, wraplength=1140)
        self.loop_alt.grid(row=2, column=0, sticky="ew", pady=(4, 12))
        ttk.Button(stop, text="Copy the command",
                   command=self._copy_disarm).grid(row=1, column=1, padx=(6, 12))

        self.loop_detail = self._detail(f, height=8)
        self.loop_detail.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

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
        for name, fn in (("headline", self._r_headline), ("walls", self._r_walls),
                         ("board", self._r_board), ("running", self._r_running),
                         ("results", self._r_results), ("loop", self._r_loop)):
            try:
                fn(s)
            except Exception:
                # One broken panel must never take the window down. Say which one broke.
                self._last_error = f"{name} panel render failed: " + \
                    traceback.format_exc(limit=3).replace("\n", " | ")

    # ---- headline -----------------------------------------------------
    def _r_headline(self, s: dict) -> None:
        w = _d(s.get("walls"))
        h = _d(w.get("headline")) or None
        if not isinstance(h, dict):
            self.headline_lbl.configure(text="COMPONENT HEALTH DATA IS MISSING")
            self.headsub_lbl.configure(
                text=f"{w.get('status', '?')}: {w.get('detail', '')}"[:300])
            for widget in (self.headbar, self.headline_lbl, self.headsub_lbl):
                widget.configure(bg=_AMBER_BG)
            self.headsub_lbl.configure(fg="#f5e6c8")
            return
        standing = h.get("standing")
        bg = {"BELOW_FLOOR": _RED_BG, "ABOVE_FLOOR": _GREEN_BG}.get(standing, _AMBER_BG)
        for widget in (self.headbar, self.headline_lbl, self.headsub_lbl):
            widget.configure(bg=bg)
        verb = {"BELOW_FLOOR": "WE ARE BELOW IT", "ABOVE_FLOOR": "WE ARE ABOVE IT",
                "LEVEL": "WE ARE LEVEL WITH IT"}.get(standing, "NOT ESTABLISHED")
        self.headline_lbl.configure(
            text=f"{h.get('title')}:  WE GET {h.get('score')}.   "
                 f"{h.get('floor_name')} GETS {h.get('floor')}.   {verb}.")

        bits = []
        b = s.get("board") or {}
        n_open = b.get("n_open")
        bits.append(f"{n_open if n_open is not None else '?'} question(s) waiting on you")
        rn = _d(s.get("running"))
        ag = _d(rn.get("agents"))
        bits.append(f"{ag.get('n_active', '?')} agent(s) working")
        lx = _l(rn.get("local_experiments"))
        bits.append(f"{len(lx)} experiment(s) running here")
        res = _d(s.get("results"))
        if res.get("status") == "OK":
            bits.append(f"{res.get('n_negative')} of the last {len(_l(res.get('rows')))} "
                        f"results are negative")
        lp = _d(s.get("loop"))
        if lp.get("armed") is True:
            bits.append(f"overnight loop ARMED (cap {lp.get('cap_label')})")
        elif lp.get("armed") is False:
            bits.append("overnight loop off")
        else:
            bits.append("overnight loop UNKNOWN")
        n_no = w.get("n_no_instrument")
        if n_no:
            bits.append(f"{n_no} part(s) we still cannot measure at all")
        self.headsub_lbl.configure(text="     ".join(bits), fg="#f4f4f4")

    # ---- panel 1 ------------------------------------------------------
    def _r_walls(self, s: dict) -> None:
        w = _d(s.get("walls"))
        tv = self.walls_tv
        tv.delete(*tv.get_children())
        self._wall_rows: dict[str, dict] = {}
        if w.get("status") != "OK":
            tv.insert("", "end", iid="_missing",
                      values=(f"{w.get('status')}", "-", "MISSING", "MISSING",
                              str(w.get("detail", ""))[:80]), tags=("warn",))
            self._set_text(self.walls_detail, [
                (f"{w.get('status')}\n", "warn"),
                str(w.get("detail", "no detail")) + "\n\n",
                ("A blank where a measurement should be is information. This panel is showing "
                 "MISSING rather than a number it does not have.\n", "dim")])
            return

        rows = []
        h = w.get("headline")
        if isinstance(h, dict):
            rows.append(("HEADLINE", h))
        for r in _l(w.get("rows")):
            rows.append((f"#{_d(r).get('n')}", _d(r)))

        for i, (prefix, r) in enumerate(rows):
            iid = f"w{i}"
            self._wall_rows[iid] = r
            inst_txt, inst_col = _INSTRUMENT_TEXT.get(
                (r.get("instrument") or "").upper(), ("unknown", _AMBER))
            stand_txt, stand_col = _STANDING_TEXT.get(r.get("standing") or "UNKNOWN",
                                                      ("not established", _AMBER))
            score = r.get("score") or "MISSING"
            floor = r.get("floor") or "MISSING"
            floor_cell = f"{floor}   ({r.get('floor_name') or 'MISSING'})"
            sep = r.get("separated")
            if sep == "YES":
                stand_txt += " (separated)"
            elif sep == "NO":
                stand_txt += " (not separated)"
            drift = "" if r.get("verify_status") in ("VERIFIED", "NO_VERIFY_STRINGS") \
                else f"   [{r.get('verify_status')}]"
            tag = ("bad" if stand_col == _RED else
                   "good" if stand_col == _GREEN else "warn")
            title = f"{prefix}  {r.get('title')}"
            tv.insert("", "end", iid=iid,
                      values=(title, inst_txt, score, floor_cell, stand_txt + drift),
                      tags=(tag, "even" if i % 2 == 0 else "odd"))
        if rows:
            tv.selection_set("w0")
            tv.focus("w0")
            self._show_wall_detail()

    def _show_wall_detail(self) -> None:
        sel = self.walls_tv.selection()
        r = getattr(self, "_wall_rows", {}).get(sel[0]) if sel else None
        if not r:
            return
        stand_txt, stand_col = _STANDING_TEXT.get(r.get("standing") or "UNKNOWN",
                                                  ("not established", _AMBER))
        tag = "bad" if stand_col == _RED else "good" if stand_col == _GREEN else "warn"
        chunks = [
            (f"{r.get('title')}\n", "h"),
            f"{r.get('what_it_does')}\n\n",
            "Can we measure this part on its own?  ",
            (f"{r.get('instrument')}", "warn" if (r.get('instrument') or '') != "YES" else "good"),
            f" -- {r.get('instrument_note', '')}\n\n",
            "OURS: ", (f"{r.get('score') or 'MISSING'}", "h"),
            f"  ({r.get('score_detail') or 'no detail'})\n",
            "FLOOR IT MUST BEAT: ", (f"{r.get('floor') or 'MISSING'}", "h"),
            f"  = {r.get('floor_name')}  ({r.get('floor_detail') or 'no detail'})\n",
            "VERDICT: ", (f"{stand_txt}", tag),
            f"   intervals separated: {r.get('separated')}\n\n",
            (f"{r.get('plain_verdict', '')}\n\n", tag),
            (f"evidence: {r.get('evidence', '')}\n", "mono"),
            (f"instrument: {r.get('instrument_evidence', '')}\n", "mono"),
        ]
        if r.get("verify_status") == "CHECK_PLAN":
            chunks.append(("\nCHECK THE PLAN: these numbers are no longer findable in "
                           f"notes/PLAN.md: {r.get('verify_missing')}. The plan is the "
                           "authority; this row may be stale.\n", "bad"))
        elif r.get("verify_status") == "CANNOT_VERIFY":
            chunks.append(("\nCannot cross-check this row: notes/PLAN.md was not readable.\n",
                           "warn"))
        self._set_text(self.walls_detail, chunks)

    # ---- panel 2 ------------------------------------------------------
    def _r_board(self, s: dict) -> None:
        b = _d(s.get("board"))
        tv = self.board_tv
        tv.delete(*tv.get_children())
        self._board_rows = [_d(r) for r in _l(b.get("open"))]
        n = b.get("n_open") or 0
        try:
            self.nb.tab(self.tab_board, text=f"2. WAITING ON YOU ({n})" if n else
                                             "2. WAITING ON YOU")
        except tk.TclError:
            pass

        if b.get("status") != "OK":
            self.board_hint.configure(
                text=f"{b.get('status')}: {b.get('detail', '')}\n"
                     f"No questions can be shown or answered from here.", fg=_AMBER)
            self.answer_btn.state(["disabled"])
            self._set_text(self.board_detail, [(f"{b.get('status')}\n", "warn"),
                                               str(b.get("detail", ""))])
            return

        self.board_hint.configure(
            text=("Type your decision below and press Save -- it is written straight into "
                  "notes/BOARD.md. You can also answer WITHOUT this window: open "
                  "notes/BOARD.md in any markdown editor on any device, type into the ANSWER "
                  "cell of the row, and save. That is the whole protocol."), fg=_BLUE)
        if not self._board_rows:
            tv.insert("", "end", values=("", "Nothing is waiting on you."), tags=("dim",))
            self.answer_btn.state(["disabled"])
            self._set_text(self.board_detail, [("No open questions.\n", "good"),
                                               "Nothing is blocked on a decision from you."])
            return

        if b.get("writable") is False:
            self.answer_btn.state(["disabled"])
            self.answer_status.configure(
                text="notes/BOARD.md is not writable from here -- answer it in the file "
                     "instead.", fg=_AMBER)
        else:
            self.answer_btn.state(["!disabled"])

        for i, r in enumerate(self._board_rows):
            tv.insert("", "end", iid=f"q{i}",
                      values=(r.get("id", "?"), r.get("question", "")),
                      tags=("even" if i % 2 == 0 else "odd",))
        keep = None
        if self._selected_qid:
            keep = next((f"q{i}" for i, r in enumerate(self._board_rows)
                         if r.get("id") == self._selected_qid), None)
        tv.selection_set(keep or "q0")
        self._show_board_detail()

    def _show_board_detail(self) -> None:
        sel = self.board_tv.selection()
        if not sel or not sel[0].startswith("q"):
            return
        try:
            r = self._board_rows[int(sel[0][1:])]
        except (ValueError, IndexError):
            return
        self._selected_qid = r.get("id")
        self._set_text(self.board_detail, [
            (f"{r.get('id')}  {r.get('question')}\n\n", "h"),
            ("WHAT IS BLOCKED ON IT\n", "warn"),
            f"{r.get('why') or '(not recorded)'}\n\n",
            ("MY RECOMMENDATION\n", "good"),
            f"{r.get('rec') or '(none)'}\n",
        ])

    def _save_answer(self) -> None:
        text = self.answer_box.get("1.0", "end").strip()
        qid = self._selected_qid
        if not qid:
            self.answer_status.configure(text="Pick a question first.", fg=_AMBER)
            return
        ok, msg = status_state.answer_question(qid, text)
        self.answer_status.configure(text=msg, fg=_GREEN if ok else _RED)
        if ok:
            self.answer_box.delete("1.0", "end")
            self._selected_qid = None
            self.refresh_now()

    # ---- panel 3 ------------------------------------------------------
    def _r_running(self, s: dict) -> None:
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
        try:
            self.nb.tab(self.tab_running, text=f"3. RUNNING NOW ({n_act})")
        except tk.TclError:
            pass

    # ---- panel 4 ------------------------------------------------------
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

    # ---- panel 5 ------------------------------------------------------
    def _r_loop(self, s: dict) -> None:
        lp = _d(s.get("loop"))
        armed = lp.get("armed")
        if armed is True:
            self.loop_big.configure(text="THE OVERNIGHT LOOP IS ON", fg=_GREEN)
            self.loop_sub.configure(
                text=(f"It will keep working through the night without you. It will stop by "
                      f"itself after {lp.get('cap_label')} continuations. "
                      f"Switched on at {lp.get('armed_at')} by {lp.get('armed_by')}."))
            try:
                self.nb.tab(self.tab_loop, text="5. OVERNIGHT LOOP (ON)")
            except tk.TclError:
                pass
        elif armed is False:
            self.loop_big.configure(text="THE OVERNIGHT LOOP IS OFF", fg=_DIM)
            self.loop_sub.configure(text="Work stops when the current turn ends.")
            try:
                self.nb.tab(self.tab_loop, text="5. OVERNIGHT LOOP (off)")
            except tk.TclError:
                pass
        else:
            self.loop_big.configure(text="OVERNIGHT LOOP: UNKNOWN", fg=_AMBER)
            self.loop_sub.configure(text=str(lp.get("detail", "")))

        self.disarm_box.configure(state="normal")
        self.disarm_box.delete("1.0", "end")
        self.disarm_box.insert("1.0", lp.get("disarm_cmd") or "python tools/autoloop.py disarm")
        self.loop_alt.configure(text=lp.get("disarm_alt", ""))

        rows = [_d(c) for c in _l(lp.get("continuations"))]
        chunks = [("How many times it has carried on by itself\n", "h"),
                  f"{lp.get('continuations_recent_total', 0)} continuation(s) in the last "
                  f"24 hours, across these sessions:\n"]
        if not rows:
            chunks.append(("no continuation counters on disk yet\n", "dim"))
        for c in rows[:6]:
            chunks.append(f"  {c['session']}: {c['count']}  "
                          f"(last touched {_fmt_dur(c['age_s'])} ago)\n")
        chunks.append((f"\nsetting file: {lp.get('state_path')}\n", "mono"))
        self._set_text(self.loop_detail, chunks)


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
        check("WE GET" in gui.headline_lbl.cget("text"),
              "the headline states our score and the floor together")
        check(len(gui.walls_tv.get_children()) >= 6,
              f"the walls panel drew its rows "
              f"(got {len(gui.walls_tv.get_children())})")
        check(len(gui.results_tv.get_children()) >= 1, "the results panel drew its rows")

        # every panel MISSING
        gui._last_error = None
        missing = {"ts": "x", "took_s": 0.0,
                   "walls": {"status": "MISSING", "detail": "spec gone"},
                   "board": {"status": "MISSING", "detail": "board gone"},
                   "running": {"status": "ERROR", "detail": "monitor gone",
                               "agents": {"status": "MISSING", "detail": "no transcripts"},
                               "alerts": [], "gpu": {}, "local_experiments": [],
                               "remote_checkpoint": {"state": "UNKNOWN", "reason": "ssh down"}},
                   "results": {"status": "MISSING", "detail": "no data dir"},
                   "loop": {"status": "ERROR", "detail": "autoloop gone", "armed": None}}
        gui.render(missing)
        check(gui._last_error is None,
              f"renders an ALL-MISSING state with no panel error ({gui._last_error})")
        check("MISSING" in gui.headline_lbl.cget("text").upper(),
              "the headline SAYS the data is missing rather than showing a stale number")
        check("MISSING" in gui.walls_detail.get("1.0", "end").upper(),
              "the walls panel tells the reader it is MISSING")
        check(str(gui.answer_btn.state()).find("disabled") >= 0,
              "the answer button is DISABLED when the board is unreadable")
        check("UNKNOWN" in gui.running_detail.get("1.0", "end").upper(),
              "remote liveness renders as UNKNOWN, not as idle")

        # structurally wrong types everywhere
        gui._last_error = None
        garbage = {"ts": None, "took_s": None, "walls": "not a dict", "board": 42,
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
