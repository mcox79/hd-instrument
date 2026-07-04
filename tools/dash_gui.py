"""Local Tkinter fleet monitor -- REPLACES the web dashboard as the primary
day-to-day monitor (USER request, asked twice).

WHY (testbed 2026-07-04): tools/dashboard/ (server.py + poller.py + supervisor.py
+ static/index.html) has a recurring reliability failure class -- dead poller
thread, duplicate supervisors/workers, port/server fragility, slow browser
render, and structural blindness to direct-subprocess (off-queue) experiment
work. Root cause of the launch fragility (for context, NOT re-fixed here):
scheduled-task launch pattern (cmd /c start /b launcher -> synchronous pythonw
grand-orphan killed by the job object) plus a \r\r\n wmic-csv delimiter bug in
the taskkill singleton loop.

A local GUI eliminates the whole failure class structurally: no web server, no
port binding, no supervisor process, no poller thread, no browser render path.
This script polls INLINE on its own Tk timer, in a background thread so the UI
never blocks, and renders directly into native widgets.

Data source: tools/inflight_monitor.py's build_state() -- imported, not
reimplemented. That function already gathers:
  * GPU util/mem/temp + queue state          (dashboard localhost HTTP -- the
    ONE remaining soft dependency: GPU truth specifically comes from
    tools/dashboard/server.py + poller.py being up; build_state() reports
    DASHBOARD_DOWN / FEED_STALE explicitly rather than lying about it, and this
    GUI never hangs or crashes on that -- it renders "GPU: stale (Ns)")
  * LOCAL direct-subprocess experiments       (tools/local_exp_scan.py, WMIC,
    independent of the dashboard -- works even when the dashboard is dead)
  * The three queues + recent terminal verdicts (remote_state_cache.json +
    local_cpu_queue/queue.json -- local file reads, independent of the
    dashboard)
  * Runner heartbeats / alerts                (same local-file source)

Usage:
  python tools/dash_gui.py            # launch the window
  (or double-click tools/dash_gui.bat)

Keys: F5 or 'r' = manual refresh. Auto-refresh every REFRESH_MS.
"""

from __future__ import annotations

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

from inflight_monitor import build_state, render_human, _fmt_dur  # noqa: E402  (reuse, don't reimplement)

REFRESH_MS = 7000          # auto-refresh cadence
TICK_MS = 1000             # freshness-clock tick (independent of poll cadence)
GPU_BUSY_UTIL = 25         # matches dashboard server.py's _GPU_BUSY_UTIL threshold
GPU_HOT_C = 85             # cosmetic warn threshold for temp
# build_state() is hard-bounded to ~10s. If a poll worker exceeds this it is
# WEDGED (should be impossible given the internal caps) -- surface it and allow a
# fresh poll rather than letting the window silently freeze on stale data.
POLL_WEDGE_S = 20

# --- Dark theme palette (terminal-matched, USER request 2026-07-04; cosmetic only) ---
_BG = "#1e1e1e"            # root window background
_PANEL_BG = "#252526"      # LabelFrame/Frame panel background
_FG = "#e0e0e0"            # primary text
_BORDER = "#3c3c3c"
_TREE_BG = "#252526"
_TREE_ALT_BG = "#2d2d30"   # alternating row stripe
_TREE_SELECT_BG = "#264f78"
_TREE_SELECT_FG = "#ffffff"
_HEADING_BG = "#333333"
_HEADING_FG = "#d4d4d4"
_BTN_BG = "#3c3c3c"
_BTN_ACTIVE_BG = "#4a4a4a"

# Semantic colors, muted/darkened so they read on a dark background instead of
# blinding (same meanings as before: alerts banner clear/warn/critical, GPU
# util busy/idle/stale, temp-hot, runner-stale, ownership sublabel).
_LEVEL_BG = {"CRITICAL": "#7a2e2a", "WARN": "#7a5a1e"}
_OK_BG = "#255a27"
_EXTERNAL_FG = "#e0a458"   # muted amber: external/BOINC load, or stale/uncertain
_OURS_FG = "#5fbf6e"       # muted green: our work on the card
_IDLE_FG = "#8a8f98"       # muted grey: idle
_HOT_FG = "#e5726a"        # muted red: temp-hot / runner-stale


def _short_exp_name(name: str) -> str:
    """Compact anchor label: drop `exp_` prefix + `_core.py`/`.py` suffix (ask #3)."""
    s = name or "?"
    if s.lower().endswith(".py"):
        s = s[:-3]
    if s.endswith("_core"):
        s = s[:-5]
    if s.startswith("exp_"):
        s = s[4:]
    return s


def _progress_cell(e: dict) -> str:
    """e.g. '1600/1800 88% eta 13m train_mlp_block_in_batch' (blank if no heartbeat)."""
    ui, tu = e.get("unit_idx"), e.get("total_units")
    pct, phase, eta = e.get("progress_pct"), e.get("phase"), e.get("eta_s")
    if ui is None and pct is None:
        return ""
    parts: list[str] = []
    if ui is not None and tu:
        parts.append(f"{ui}/{tu}")
    if pct is not None:
        parts.append(f"{int(pct)}%")
    if eta:
        parts.append(f"eta {_fmt_dur(eta)}")
    if phase:
        parts.append(str(phase))
    return " ".join(parts)


class DashGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("hd-instrument fleet monitor (local)")
        root.geometry("1040x760")
        root.minsize(760, 560)

        self._q: _queue.Queue = _queue.Queue()
        self._poll_inflight = False
        self._poll_started_ts: float | None = None
        self._last_state: dict | None = None
        self._last_poll_ok_ts: float | None = None
        self._last_poll_error: str | None = None

        self._configure_style()
        self._build_widgets()
        root.bind("<F5>", lambda _e: self.refresh_now())
        root.bind("r", lambda _e: self.refresh_now())
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        # First poll immediately, then settle into the timer cadence.
        self.refresh_now()
        self._schedule_poll()
        self._tick()
        self.root.after(200, self._pump_queue)

    # ------------------------------------------------------------------
    # Dark theme (cosmetic only -- no polling/threading/data logic here)
    # ------------------------------------------------------------------
    def _configure_style(self) -> None:
        self.root.configure(bg=_BG)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")   # 'clam' honors background/foreground overrides
        except tk.TclError:
            pass

        style.configure(".", background=_PANEL_BG, foreground=_FG,
                         fieldbackground=_PANEL_BG, bordercolor=_BORDER)
        style.configure("TFrame", background=_PANEL_BG)
        style.configure("TLabelframe", background=_PANEL_BG, foreground=_FG,
                         bordercolor=_BORDER)
        style.configure("TLabelframe.Label", background=_PANEL_BG, foreground=_FG)
        style.configure("TLabel", background=_PANEL_BG, foreground=_FG)
        style.configure("TButton", background=_BTN_BG, foreground=_FG,
                         bordercolor=_BORDER, focuscolor=_BORDER)
        style.map("TButton",
                  background=[("active", _BTN_ACTIVE_BG)],
                  foreground=[("active", _FG)])

        style.configure("Treeview", background=_TREE_BG, foreground=_FG,
                         fieldbackground=_TREE_BG, bordercolor=_BORDER, rowheight=20)
        style.map("Treeview",
                  background=[("selected", _TREE_SELECT_BG)],
                  foreground=[("selected", _TREE_SELECT_FG)])
        style.configure("Treeview.Heading", background=_HEADING_BG, foreground=_HEADING_FG,
                         bordercolor=_BORDER, relief="flat")
        style.map("Treeview.Heading", background=[("active", _HEADING_BG)])

        style.configure("Vertical.TScrollbar", background=_BTN_BG, troughcolor=_PANEL_BG,
                         bordercolor=_BORDER, arrowcolor=_FG,
                         darkcolor=_PANEL_BG, lightcolor=_PANEL_BG)
        style.map("Vertical.TScrollbar", background=[("active", _BTN_ACTIVE_BG)])

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=0)   # gpu row: fixed
        root.rowconfigure(2, weight=1)   # local experiments: grows
        root.rowconfigure(3, weight=1)   # queues/runners: grows
        root.rowconfigure(4, weight=0)   # status bar: fixed

        # --- Alerts banner (row 0) ---
        self.alerts_text = tk.Text(root, height=4, wrap="word", bd=0,
                                    font=("Consolas", 10, "bold"),
                                    fg=_FG, bg=_OK_BG, state="disabled",
                                    padx=8, pady=6, highlightthickness=0,
                                    insertbackground=_FG)
        self.alerts_text.grid(row=0, column=0, sticky="ew")

        # --- GPU panel (row 1) ---
        gpu_frame = ttk.LabelFrame(root, text="GPU")
        gpu_frame.grid(row=1, column=0, sticky="ew", padx=6, pady=(6, 3))
        for c in range(4):
            gpu_frame.columnconfigure(c, weight=1)

        self.gpu_util_lbl = tk.Label(gpu_frame, text="--%", font=("Consolas", 30, "bold"),
                                      bg=_PANEL_BG, fg=_FG)
        self.gpu_util_lbl.grid(row=0, column=0, rowspan=2, sticky="w", padx=10)
        self.gpu_mem_lbl = tk.Label(gpu_frame, text="mem: --", font=("Consolas", 12),
                                     bg=_PANEL_BG, fg=_FG)
        self.gpu_mem_lbl.grid(row=0, column=1, sticky="w")
        self.gpu_temp_lbl = tk.Label(gpu_frame, text="temp: --", font=("Consolas", 12),
                                      bg=_PANEL_BG, fg=_FG)
        self.gpu_temp_lbl.grid(row=1, column=1, sticky="w")
        self.gpu_status_lbl = tk.Label(gpu_frame, text="queue: --", font=("Consolas", 12),
                                        bg=_PANEL_BG, fg=_FG)
        self.gpu_status_lbl.grid(row=0, column=2, sticky="w")
        self.gpu_feed_lbl = tk.Label(gpu_frame, text="feed: --", font=("Consolas", 12),
                                      bg=_PANEL_BG, fg=_FG)
        self.gpu_feed_lbl.grid(row=1, column=2, sticky="w")
        self.gpu_oncard_lbl = tk.Label(gpu_frame, text="", font=("Consolas", 10),
                                        anchor="w", justify="left", bg=_PANEL_BG, fg=_FG)
        self.gpu_oncard_lbl.grid(row=0, column=3, rowspan=2, sticky="w", padx=(10, 6))
        # Ownership banner (ask #2): OUR WORK vs external/BOINC, full-width + loud.
        self.gpu_owner_lbl = tk.Label(gpu_frame, text="", font=("Consolas", 13, "bold"),
                                       anchor="w", bg=_PANEL_BG, fg=_FG)
        self.gpu_owner_lbl.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=(2, 4))

        # --- Local experiments (row 2) ---
        local_frame = ttk.LabelFrame(root, text="LOCAL EXPERIMENTS (direct subprocess, off-queue)")
        local_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=3)
        local_frame.columnconfigure(0, weight=1)
        local_frame.rowconfigure(0, weight=1)
        cols = ("name", "progress", "pid", "elapsed", "mem", "device", "seed", "tier")
        self.local_tree = ttk.Treeview(local_frame, columns=cols, show="headings", height=5)
        for c, w in zip(cols, (230, 210, 60, 75, 70, 65, 50, 55)):
            self.local_tree.heading(c, text=c.upper())
            self.local_tree.column(c, width=w, anchor="w")
        self.local_tree.grid(row=0, column=0, sticky="nsew")
        self.local_tree.tag_configure("evenrow", background=_TREE_BG)
        self.local_tree.tag_configure("oddrow", background=_TREE_ALT_BG)
        lsb = ttk.Scrollbar(local_frame, orient="vertical", command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=lsb.set)
        lsb.grid(row=0, column=1, sticky="ns")

        # --- Queues + Runners side by side (row 3) ---
        mid = ttk.Frame(root)
        mid.grid(row=3, column=0, sticky="nsew", padx=6, pady=3)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)

        q_frame = ttk.LabelFrame(mid, text="QUEUES + recent verdicts")
        q_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        q_frame.columnconfigure(0, weight=1)
        q_frame.rowconfigure(0, weight=1)
        self.q_tree = ttk.Treeview(q_frame, columns=("running", "pending"),
                                    show="tree headings", height=10)
        self.q_tree.heading("#0", text="queue / recent verdict")
        self.q_tree.heading("running", text="running")
        self.q_tree.heading("pending", text="pending")
        self.q_tree.column("#0", width=260, anchor="w")
        self.q_tree.column("running", width=110, anchor="w")
        self.q_tree.column("pending", width=70, anchor="center")
        self.q_tree.grid(row=0, column=0, sticky="nsew")
        self.q_tree.tag_configure("evenrow", background=_TREE_BG)
        self.q_tree.tag_configure("oddrow", background=_TREE_ALT_BG)
        qsb = ttk.Scrollbar(q_frame, orient="vertical", command=self.q_tree.yview)
        self.q_tree.configure(yscrollcommand=qsb.set)
        qsb.grid(row=0, column=1, sticky="ns")

        r_frame = ttk.LabelFrame(mid, text="RUNNERS + heartbeat age")
        r_frame.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
        r_frame.columnconfigure(0, weight=1)
        r_frame.rowconfigure(0, weight=1)
        rcols = ("status", "pid", "hb_age", "current")
        self.r_tree = ttk.Treeview(r_frame, columns=rcols, show="tree headings", height=10)
        self.r_tree.heading("#0", text="runner")
        for c, w in zip(rcols, (80, 70, 90, 180)):
            self.r_tree.heading(c, text=c.upper())
            self.r_tree.column(c, width=w, anchor="w")
        self.r_tree.column("#0", width=110, anchor="w")
        self.r_tree.grid(row=0, column=0, sticky="nsew")
        self.r_tree.tag_configure("evenrow", background=_TREE_BG)
        self.r_tree.tag_configure("oddrow", background=_TREE_ALT_BG)
        rsb = ttk.Scrollbar(r_frame, orient="vertical", command=self.r_tree.yview)
        self.r_tree.configure(yscrollcommand=rsb.set)
        rsb.grid(row=0, column=1, sticky="ns")

        # --- Status bar (row 4) ---
        status = ttk.Frame(root)
        status.grid(row=4, column=0, sticky="ew", padx=6, pady=(3, 6))
        status.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(status, text="starting...", anchor="w")
        self.status_lbl.grid(row=0, column=0, sticky="ew")
        ttk.Button(status, text="Refresh (F5)", command=self.refresh_now).grid(row=0, column=1)

    # ------------------------------------------------------------------
    # Polling (background thread -> queue -> main-thread render)
    # ------------------------------------------------------------------
    def _schedule_poll(self) -> None:
        self.root.after(REFRESH_MS, self._auto_poll)

    def _auto_poll(self) -> None:
        self.refresh_now()
        self._schedule_poll()

    def refresh_now(self) -> None:
        if self._poll_inflight:
            # A poll is already running. If it has wedged past the cap (should be
            # impossible -- build_state is hard-bounded), abandon it and start a
            # fresh one so the window can't freeze permanently on a stuck worker.
            started = self._poll_started_ts
            if started is None or (time.time() - started) < POLL_WEDGE_S:
                return
        self._poll_inflight = True
        self._poll_started_ts = time.time()
        t = threading.Thread(target=self._poll_worker, daemon=True)
        t.start()

    def _poll_worker(self) -> None:
        try:
            st = build_state()
            self._q.put(("ok", st))
        except Exception:
            self._q.put(("error", traceback.format_exc(limit=6)))

    def _pump_queue(self) -> None:
        try:
            while True:
                kind, payload = self._q.get_nowait()
                self._poll_inflight = False
                if kind == "ok":
                    self._last_state = payload
                    self._last_poll_ok_ts = time.time()
                    self._last_poll_error = None
                    self._safe_render(payload)
                else:
                    self._last_poll_error = str(payload)[:400]
        except _queue.Empty:
            pass
        self.root.after(200, self._pump_queue)

    def _tick(self) -> None:
        """Freshness clock -- ticks every second independent of poll cadence so a
        frozen display (vs. a frozen app) is visually distinguishable."""
        self._update_status_bar()
        self.root.after(TICK_MS, self._tick)

    # ------------------------------------------------------------------
    # Rendering (never let a bad field crash the UI -- degrade, don't die)
    # ------------------------------------------------------------------
    def _safe_render(self, st: dict) -> None:
        try:
            self._render(st)
        except Exception:
            self._set_alert_banner([{
                "level": "CRITICAL", "code": "RENDER_ERROR",
                "msg": traceback.format_exc(limit=4).replace("\n", " | "),
            }])

    def _set_alert_banner(self, alerts: list[dict]) -> None:
        bg = _OK_BG
        if any(a.get("level") == "CRITICAL" for a in alerts):
            bg = _LEVEL_BG["CRITICAL"]
        elif alerts:
            bg = _LEVEL_BG["WARN"]
        lines = ["ALL CLEAR - no alerts"] if not alerts else [
            f"[{a.get('level', '?')}] {a.get('code', '?')}: {a.get('msg', '')}" for a in alerts
        ]
        self.alerts_text.configure(state="normal", bg=bg)
        self.alerts_text.delete("1.0", "end")
        self.alerts_text.insert("1.0", "\n".join(lines))
        self.alerts_text.configure(state="disabled")

    def _render(self, st: dict) -> None:
        self._set_alert_banner(st.get("alerts") or [])

        # --- GPU ---
        g = st.get("gpu") or {}
        feed = st.get("feed") or {}
        dashboard_up = bool(st.get("dashboard_up"))
        # source: "feed" (dashboard live) | "ssh" (feed down, direct nvidia-smi
        # fallback succeeded) | "stale" (feed down AND probe failed). build_state
        # only runs the SSH probe when the feed is untrustworthy, so the feed-up
        # path is unchanged.
        source = g.get("source")
        util = g.get("util_ema") if g.get("util_ema") is not None else g.get("util_pct")
        have_util = isinstance(util, (int, float)) and source in ("feed", "ssh")

        if have_util:
            queue_running = g.get("queue_status") == "running"
            busy = util >= GPU_BUSY_UTIL or queue_running
            self.gpu_util_lbl.configure(text=f"{util}%", fg=(_OURS_FG if busy else _IDLE_FG))
        else:
            age = feed.get("age_s")
            age_txt = f"{age}s" if age is not None else "unknown age"
            self.gpu_util_lbl.configure(text=f"stale ({age_txt})", fg=_EXTERNAL_FG)

        # Ownership disambiguation (ask #2) -- never let a high util read
        # ambiguously as "our work" when it is BOINC/external and our queue is idle.
        owner_text, owner_fg = "", _FG
        if not have_util:
            owner_text = "GPU reading unavailable (dashboard feed down, SSH probe failed)"
            owner_fg = _EXTERNAL_FG
        elif source == "ssh":
            # Real util via SSH but the feed is down, so queue/on-card attribution
            # is unknown -- say so rather than guessing ownership.
            if util >= GPU_BUSY_UTIL:
                owner_text = "GPU BUSY (util via SSH; feed DOWN so ownership unknown)"
                owner_fg = _EXTERNAL_FG
            else:
                owner_text = "GPU idle (util via SSH; dashboard feed DOWN)"
                owner_fg = _IDLE_FG
        else:  # source == "feed": full attribution available
            queue_running = g.get("queue_status") == "running"
            on_card = bool(g.get("experiment_on_card"))
            if util >= GPU_BUSY_UTIL:
                if queue_running or on_card:
                    owner_text, owner_fg = "OUR WORK on GPU", _OURS_FG
                else:
                    owner_text = "external load (BOINC/other); our queue idle"
                    owner_fg = _EXTERNAL_FG
            else:
                owner_text, owner_fg = "GPU idle", _IDLE_FG
        self.gpu_owner_lbl.configure(text=owner_text, fg=owner_fg)

        mem = g.get("mem_used_mb")
        self.gpu_mem_lbl.configure(text=f"mem: {mem if mem is not None else '--'} MB")
        temp = g.get("temp_c")
        temp_fg = _HOT_FG if isinstance(temp, (int, float)) and temp >= GPU_HOT_C else _FG
        self.gpu_temp_lbl.configure(text=f"temp: {temp if temp is not None else '--'} C", fg=temp_fg)
        src_txt = {"feed": "via feed", "ssh": "via SSH", "stale": "stale"}.get(source, "?")
        self.gpu_status_lbl.configure(
            text=f"queue: {g.get('queue_status') or '-'} | src: {src_txt}")
        self.gpu_feed_lbl.configure(
            text=f"feed: {'STALE' if feed.get('stale') else 'live'} "
                 f"({feed.get('age_s')}s) | dash: {'up' if dashboard_up else 'DOWN'} "
                 f"| cache: {_fmt_dur(st.get('cache_age_s'))}")
        oncard = ""
        if g.get("experiment_on_card") and g.get("exp_name"):
            prog = f" {g.get('progress_pct')}%" if g.get("progress_pct") is not None else ""
            eta = f" eta {_fmt_dur(g.get('eta_sec'))}" if g.get("eta_sec") else ""
            oncard = (f"on card: {g['exp_name']}{prog}{eta}\n"
                      f"elapsed {_fmt_dur(g.get('elapsed_s'))}")
            if g.get("last_line"):
                oncard += f"\n-> {str(g['last_line'])[:90]}"
        elif g.get("current"):
            oncard = f"running (queue): {g['current']}"
        self.gpu_oncard_lbl.configure(text=oncard)

        # --- Local experiments ---
        self.local_tree.delete(*self.local_tree.get_children())
        lx = st.get("local_experiments") or []
        if not lx:
            self.local_tree.insert("", "end", values=("(none detected)", "", "", "", "", "", "", ""),
                                    tags=("evenrow",))
        for i, e in enumerate(lx):
            args = e.get("args") or {}
            mem_mb = int((e.get("mem_kb") or 0) / 1024)
            stripe = "evenrow" if i % 2 == 0 else "oddrow"
            self.local_tree.insert("", "end", values=(
                _short_exp_name(e.get("name", "?")), _progress_cell(e),
                e.get("pid", "?"), _fmt_dur(e.get("elapsed_s")), f"{mem_mb}MB",
                args.get("device", "-"), args.get("seed", "-"), args.get("tier", "-"),
            ), tags=(stripe,))

        # --- Queues ---
        self.q_tree.delete(*self.q_tree.get_children())
        for i, (qname, qd) in enumerate((st.get("queues") or {}).items()):
            run = qd.get("running") or []
            pend = qd.get("pending") or []
            stripe = "evenrow" if i % 2 == 0 else "oddrow"
            parent = self.q_tree.insert("", "end", text=qname, values=(
                ",".join(run) or "-", len(pend)), tags=(stripe,))
            for j, t in enumerate((qd.get("terminal_recent") or [])[:3]):
                child_stripe = "evenrow" if j % 2 == 0 else "oddrow"
                self.q_tree.insert(parent, "end",
                                    text=f"  {t.get('name', '?')} = {t.get('status', '?')}",
                                    values=("", ""), tags=(child_stripe,))
            self.q_tree.item(parent, open=True)

        # --- Runners ---
        self.r_tree.delete(*self.r_tree.get_children())
        for i, (rid, r) in enumerate((st.get("runners") or {}).items()):
            hb_age = r.get("heartbeat_age_s")
            stripe = "evenrow" if i % 2 == 0 else "oddrow"
            tags = (stripe,)
            if r.get("status") == "running" and isinstance(hb_age, (int, float)) and hb_age > 300:
                tags = (stripe, "stale")
            self.r_tree.insert("", "end", text=rid, values=(
                r.get("status") or "-", r.get("pid") or "-",
                _fmt_dur(hb_age), r.get("current") or "-",
            ), tags=tags)
        self.r_tree.tag_configure("stale", foreground=_HOT_FG)

    def _update_status_bar(self) -> None:
        parts = []
        if self._last_poll_ok_ts is not None:
            age = time.time() - self._last_poll_ok_ts
            parts.append(f"last data: {int(age)}s ago")
        else:
            parts.append("last data: (none yet)")
        # Distinguish a normal in-flight poll from a WEDGED one (worker exceeded
        # build_state's hard bound) so the window never silently freezes.
        if self._poll_inflight and self._poll_started_ts is not None:
            in_flight = time.time() - self._poll_started_ts
            if in_flight > POLL_WEDGE_S:
                parts.append(f"POLL WEDGED ({int(in_flight)}s) - data may be stale, retrying")
            else:
                parts.append("polling...")
        if self._last_poll_error:
            parts.append(f"LAST POLL ERROR: {self._last_poll_error[:150]}")
        parts.append(f"auto-refresh every {REFRESH_MS // 1000}s (F5/r = refresh now)")
        self.status_lbl.configure(text="  |  ".join(parts))


def main() -> int:
    root = tk.Tk()
    DashGui(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
