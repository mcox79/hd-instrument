"""tools/scorecard_gui.py -- the owner's window, simplified (2026-09-11).

Owner: "simplify it (new version), and create a tab (remove the others) that gives me a clear idea of how well the
substrate is performing, and its capabilities ... kept updated, from a document that you keep updated ... We can
also keep the tab that asks me questions ... use me as a resource ... intuitive and jargon free."

FOUR TABS.
  1. HOW WE'RE DOING   REDESIGNED 2026-09-14 (owner: "more informative and less like a list ... kept updated ...
                       reference a live doc"). It is no longer a table of abilities. It is a status view, built
                       in the order a reader actually needs it (Shneiderman 1996: overview first, details on
                       demand) -- see notes/GUI_HOW_WE_ARE_DOING_design_2026-09-14.md:
                         BAND    the goal (small, standing) + ONE sentence saying where we are (large), plus
                                 four figures: the board, what simple rules get, how many parts beat them, n.
                         CHAIN   the seven rungs a passage passes through, left to right, each with a status
                                 colour and its own honest number; click one for what it is.
                         TREND   the board over the recent full checks. Runs measured on a DIFFERENT set of
                                 questions are drawn hollow and are NOT joined to the line.
                         THEN    what moved (dated), what is running, what is next, risks -- each folded.
                         LAST    the full ability table, folded away behind one line.
                       SOURCE OF TRUTH: notes/HOW_WE_ARE_DOING.md, which the strategy session edits in a few
                       lines per landing (its own 10-line "how to keep this current" header says how). The
                       parser lives in tools/how_we_are_doing_web.py and is shared with the browser view, so
                       the window and the web page can never disagree. The board line is read from
                       notes/BOARD_TREND.jsonl; the ability table still comes from tools/scorecard.py.
  2. QUESTIONS FOR YOU the open board questions (tools/board.py / notes/BOARD.md) with an answer box, plus a
                       "note for the strategy session" box (notes/COMMENTARY.md). Typing into the files directly
                       still works; this window just saves the trip.
  3. UPDATES           significant items only.        4. PROBLEMS TO HAND OUT   solver briefs with a copy button.
The old eight-tab window (tools/status_gui.py) is left in place, untouched.

Launch:  .venv/Scripts/python.exe tools/scorecard_gui.py        (--self-test builds the window offscreen and exits)

REMOTE (Tailscale): this is a Tkinter app, so it only draws on the machine it runs on -- over Tailscale that
means an RDP session into the desktop. To read the same thing from a phone or laptop WITHOUT remote desktop,
run  .venv/Scripts/python.exe tools/how_we_are_doing_web.py --bind <this machine's 100.x.y.z>  and open
http://100.x.y.z:8787/  (the desktop 'home' is 100.91.12.42 today; `tailscale ip -4` prints it). Every path in
both files is resolved from the file's own location, never absolute, so both run unchanged after the move to
the desktop. Details and the firewall / `tailscale serve` note: notes/GUI_HOW_WE_ARE_DOING_design_2026-09-14.md.
"""
from __future__ import annotations

import argparse
import os
import json
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))
import scorecard as SC  # noqa: E402
import how_we_are_doing_web as HWD  # noqa: E402  (the shared parser; also the browser view)

REFRESH_MS = 60_000
BG, PANEL, FG, DIM, GREEN, BLUE, ORANGE, RED = "#1e1e1e", "#262626", "#e8e8e8", "#9a9a9a", "#7ccf8a", "#8ab4f8", "#f0b35b", "#ef6e6e"
CARD, EDGE = "#242424", "#3a3a3a"
FONT, FONT_B, FONT_H = ("Segoe UI", 11), ("Segoe UI", 11, "bold"), ("Segoe UI", 15, "bold")
FONT_S, FONT_SB = ("Segoe UI", 9), ("Segoe UI", 9, "bold")
FONT_POS, FONT_BIG, FONT_SEC = ("Segoe UI", 15, "bold"), ("Segoe UI", 18, "bold"), ("Segoe UI", 10, "bold")


class Disclosure:
    """One folded section: a clickable header that packs/unpacks its body.

    Progressive disclosure (Nielsen 1995; Shneiderman's 'details on demand') is the whole reason this tab
    can hold the plan, the trend, the movements, the risks AND the 36-row ability table without reading
    as a list: everything past the first few lines of each section is one click away, not on screen.
    """

    def __init__(self, parent, title: str, subtitle: str = "", open_: bool = False, wrapper=None):
        self.frame = tk.Frame(parent, bg=CARD, highlightbackground=EDGE, highlightthickness=1)
        self.open = bool(open_)
        self.has_more = True   # False -> no fold arrow, because unfolding would reveal nothing
        head = tk.Frame(self.frame, bg=CARD)
        head.pack(fill="x", padx=12, pady=(9, 0))
        self.arrow = tk.Label(head, text="", bg=CARD, fg=BLUE, font=FONT_SB, width=2)
        self.arrow.pack(side="left")
        self.title = tk.Label(head, text=title.upper(), bg=CARD, fg=DIM, font=FONT_SEC, anchor="w")
        self.title.pack(side="left")
        self.sub = tk.Label(head, text=subtitle, bg=CARD, fg=DIM, font=FONT_S, anchor="w")
        self.sub.pack(side="left", padx=(10, 0))
        # `preview` is always on screen (the first few items); `body` is what folding reveals.
        self.preview = tk.Frame(self.frame, bg=CARD)
        self.preview.pack(fill="x", padx=12, pady=(6, 0))
        self.body = tk.Frame(self.frame, bg=CARD)
        for w in (head, self.arrow, self.title, self.sub):
            w.bind("<Button-1>", lambda _e: self.toggle())
            try:
                w.configure(cursor="hand2")
            except tk.TclError:
                pass
        if wrapper is not None:
            wrapper(self.title)
        self._render()

    def toggle(self) -> None:
        if not self.has_more:
            return
        self.open = not self.open
        self._render()

    def _render(self) -> None:
        self.arrow.config(text=("▾" if self.open else "▸") if self.has_more else " ")
        if self.open:
            self.body.pack(fill="both", expand=True, padx=12, pady=(6, 10))
        else:
            self.body.pack_forget()


class ScorecardWindow:
    def __init__(self, root: tk.Tk, offscreen: bool = False) -> None:
        self.root = root
        root.title("How the reading system is doing")
        root.configure(bg=BG)
        try:
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
            root.geometry("%dx%d+20+20" % (min(1280, sw - 40), min(900, sh - 80)))
        except Exception:
            root.geometry("1280x860")
        if offscreen:
            root.withdraw()
        st = ttk.Style(root)
        try:
            st.theme_use("clam")
        except Exception:
            pass
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background="#2b2b2b", foreground=FG, padding=(16, 8), font=FONT_B)
        st.map("TNotebook.Tab", background=[("selected", PANEL)])
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=26, font=FONT)
        st.configure("Treeview.Heading", background="#333", foreground=FG, font=FONT_B)
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.sc: dict = {}
        self._build_tab_doing()
        self._build_tab_questions()
        self._build_tab_updates()
        self._build_tab_problems()
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=10, pady=(0, 8))
        self.stamp = tk.Label(bar, text="", bg=BG, fg=DIM, font=FONT, anchor="w")
        self.stamp.pack(side="left")
        tk.Button(bar, text="Refresh now", command=self.refresh, bg="#333", fg=FG, font=FONT, relief="flat", padx=10).pack(side="right")
        self.refresh()
        if not offscreen:
            root.after(REFRESH_MS, self._tick)

    # ------------------------------------------------------------------ tab 1: HOW WE'RE DOING
    # Rebuilt 2026-09-14. Reading order is deliberate and is the design (see the module docstring and
    # notes/GUI_HOW_WE_ARE_DOING_design_2026-09-14.md): one sentence, then four figures, then the chain,
    # then the trend, then the movements -- and everything else folded away behind one line each.
    def _build_tab_doing(self) -> None:
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="1. HOW WE'RE DOING")
        f.rowconfigure(0, weight=1); f.columnconfigure(0, weight=1)
        cv = tk.Canvas(f, bg=BG, highlightthickness=0, takefocus=1)
        vsb = ttk.Scrollbar(f, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        cv.grid(row=0, column=0, sticky="nsew"); vsb.grid(row=0, column=1, sticky="ns")
        inner = tk.Frame(cv, bg=BG)
        self._doing_cv, self._doing_win = cv, cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", self._on_doing_resize)
        # The wheel is bound only while the pointer is over this canvas, so it does not steal scrolling
        # from the treeviews on the other tabs.
        cv.bind("<Enter>", lambda _e: cv.bind_all("<MouseWheel>", self._doing_wheel))
        cv.bind("<Leave>", lambda _e: cv.unbind_all("<MouseWheel>"))
        self._wraps: list[tuple[tk.Widget, int]] = []      # fixed labels: (label, horizontal margin)
        self._wraps_dyn: list[tuple[tk.Widget, int]] = []  # rebuilt every refresh, so it must not accumulate
        self._doing_width = 1200

        # --- BAND: the standing goal small, then the ONE sentence that answers "how are we doing"
        band = tk.Frame(inner, bg=BG)
        band.pack(fill="x", padx=14, pady=(12, 2))
        self.goal_lbl = tk.Label(band, text="", bg=BG, fg=DIM, font=FONT_S, anchor="w", justify="left")
        self.goal_lbl.pack(fill="x")
        self._wraps.append((self.goal_lbl, 60))
        self.position_lbl = tk.Label(band, text="", bg=BG, fg=FG, font=FONT_POS, anchor="w", justify="left")
        self.position_lbl.pack(fill="x", pady=(9, 0))
        self._wraps.append((self.position_lbl, 60))
        self.chips = tk.Frame(band, bg=BG)
        self.chips.pack(fill="x", pady=(12, 0))

        # --- THE CHAIN: seven rungs left to right, status colour + honest number, detail on click
        card = tk.Frame(inner, bg=CARD, highlightbackground=EDGE, highlightthickness=1)
        card.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(card, text="WHERE WE ARE ON THE PLAN — a passage of text goes left to right through these",
                 bg=CARD, fg=DIM, font=FONT_SEC, anchor="w").pack(fill="x", padx=12, pady=(9, 2))
        self.chain_strip = tk.Frame(card, bg=CARD)
        self.chain_strip.pack(fill="x", padx=8, pady=(2, 4))
        self.chain_detail = tk.Label(card, text="Click a stage above to see what it is.", bg=CARD, fg=DIM,
                                     font=FONT, anchor="w", justify="left")
        self.chain_detail.pack(fill="x", padx=12, pady=(2, 10))
        self._wraps.append((self.chain_detail, 70))
        self._stage_cells: list[tuple[tk.Widget, dict]] = []
        self._stage_sel: int | None = None

        # --- THE TREND: a point number means little without its history (Few 2006)
        tcard = tk.Frame(inner, bg=CARD, highlightbackground=EDGE, highlightthickness=1)
        tcard.pack(fill="x", padx=14, pady=10)
        self.trend_title = tk.Label(tcard, text="THE BOARD OVER THE RECENT FULL CHECKS", bg=CARD, fg=DIM,
                                    font=FONT_SEC, anchor="w")
        self.trend_title.pack(fill="x", padx=12, pady=(9, 2))
        self.trend_cv = tk.Canvas(tcard, bg=CARD, height=170, highlightthickness=0)
        self.trend_cv.pack(fill="x", padx=6, pady=(0, 2))
        self.trend_cv.bind("<Configure>", lambda _e: self._draw_trend())
        self.trend_note = tk.Label(tcard, text="", bg=CARD, fg=DIM, font=FONT_S, anchor="w", justify="left")
        self.trend_note.pack(fill="x", padx=12, pady=(0, 10))
        self._wraps.append((self.trend_note, 70))

        # --- FOLDED SECTIONS
        self.sec_moved = Disclosure(inner, "What moved", "newest first", wrapper=None)
        self.sec_moved.frame.pack(fill="x", padx=14, pady=(0, 8))
        self.sec_running = Disclosure(inner, "What is running right now", open_=False)
        self.sec_running.frame.pack(fill="x", padx=14, pady=(0, 8))
        self.sec_next = Disclosure(inner, "What is next", open_=False)
        self.sec_next.frame.pack(fill="x", padx=14, pady=(0, 8))
        self.sec_risks = Disclosure(inner, "Risks and corrections", "read these before quoting a number", open_=False)
        self.sec_risks.frame.pack(fill="x", padx=14, pady=(0, 8))

        # --- THE FULL ABILITY TABLE, folded away. It is still the most detailed thing here, but it is now
        #     the LAST thing, behind one line, instead of being the tab (owner: "less like a list").
        self.sec_table = Disclosure(inner, "Every ability, measured", "the full table", open_=False)
        self.sec_table.frame.pack(fill="x", padx=14, pady=(0, 16))
        body = self.sec_table.body
        body.columnconfigure(0, weight=3); body.columnconfigure(1, weight=2)
        cols = ("ability", "how", "vs", "trend", "faithful")
        self.tv = ttk.Treeview(body, columns=cols, show="tree headings", selectmode="browse", height=18)
        for c, w, t in (("#0", 180, "Group"), ("ability", 300, "Ability"), ("how", 180, "How well"),
                        ("vs", 260, "Compared with a simple rule"), ("trend", 170, "Since the previous check"),
                        ("faithful", 230, "Brain-faithful?")):
            self.tv.heading(c, text=t)
            self.tv.column(c, width=w, stretch=(c in ("ability", "vs")))
        self.tv.tag_configure("good", foreground=GREEN)
        self.tv.tag_configure("meh", foreground=ORANGE)
        self.tv.tag_configure("bad", foreground=RED)
        self.tv.tag_configure("none", foreground=DIM)
        self.tv.tag_configure("group", foreground=BLUE, font=FONT_B)
        self.tv.grid(row=0, column=0, sticky="nsew", pady=4)
        self.tv.bind("<<TreeviewSelect>>", lambda _e: self._show_detail())
        self.detail = tk.Text(body, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=10, pady=8,
                              height=18, width=40)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)
        self.detail.tag_configure("h", font=FONT_B, foreground=BLUE)
        self.detail.tag_configure("dim", foreground=DIM)
        self.detail.tag_configure("warn", foreground=ORANGE)

    # ---- scrolling / resizing helpers
    def _doing_wheel(self, evt) -> None:
        try:
            self._doing_cv.yview_scroll(int(-1 * (evt.delta / 120)), "units")
        except tk.TclError:
            pass

    def _on_doing_resize(self, evt) -> None:
        self._doing_width = max(int(evt.width), 520)
        self._doing_cv.itemconfigure(self._doing_win, width=self._doing_width)
        for lbl, margin in self._wraps + self._wraps_dyn:
            try:
                lbl.config(wraplength=max(self._doing_width - margin, 260))
            except tk.TclError:
                pass
        self._layout_chain()

    # ---- the live document
    def _fill_doing(self) -> None:
        """Render notes/HOW_WE_ARE_DOING.md (via the shared parser) plus the board history and the table."""
        self.doc = HWD.parse_doc()
        self.trend = HWD.load_trend()
        if not self.doc.get("ok"):
            self.goal_lbl.config(text="notes/HOW_WE_ARE_DOING.md could not be read.", fg=RED)
            self.position_lbl.config(text=str(self.doc.get("error") or ""), font=FONT)
        else:
            self.goal_lbl.config(text=self.doc["goal"], fg=DIM)
            self.position_lbl.config(text=self.doc["position"], font=FONT_POS, fg=FG)
        self._fill_chips()
        self._layout_chain()
        self._draw_trend()
        self._fill_sections()
        self._fill_table()

    def _fill_chips(self) -> None:
        for w in self.chips.winfo_children():
            w.destroy()
        latest = (self.trend or {}).get("latest")
        if not latest:
            tk.Label(self.chips, text="No full check on record yet.", bg=BG, fg=DIM, font=FONT).pack(side="left")
            return
        d, words = HWD.trend_delta(self.trend)
        arrow = "" if d is None or abs(d) < 0.0005 else (" ▲" if d > 0 else " ▼")
        col = GREEN if (d or 0) > 0.0005 else (ORANGE if (d or 0) < -0.0005 else FG)
        chips = [("%.0f in 100%s" % (latest["model"] * 100, arrow), "the board overall · " + words, col)]
        if latest.get("floor") is not None:
            chips.append(("%.0f in 100" % (latest["floor"] * 100), "what simple rules get on the same questions", DIM))
        if latest.get("n_sep") is not None:
            chips.append(("%s of %s" % (latest["n_sep"], latest.get("n_dims", "?")),
                          "parts of the board clearly better than simple rules", FG))
        chips.append(("{:,}".format(latest.get("n") or 0), "test questions in the last full check", DIM))
        # Grid, not pack: on a 1128-wide laptop screen four packed chips ran off the right edge.
        # Two rows below 1000px, one row above; every column shares the width equally.
        per_row = len(chips) if self._doing_width >= 1000 else 2
        for i, (big, small, colour) in enumerate(chips):
            r, col = divmod(i, per_row)
            c = tk.Frame(self.chips, bg=CARD, highlightbackground=EDGE, highlightthickness=1)
            c.grid(row=r, column=col, sticky="nsew", padx=(0, 8), pady=(0, 6))
            tk.Label(c, text=big, bg=CARD, fg=colour, font=FONT_BIG, anchor="w").pack(fill="x", padx=12, pady=(7, 0))
            lbl = tk.Label(c, text=small, bg=CARD, fg=DIM, font=FONT_S, anchor="w", justify="left")
            lbl.pack(fill="x", padx=12, pady=(0, 8))
            lbl.config(wraplength=max(int((self._doing_width - 60) / per_row) - 44, 110))
        for col in range(per_row):
            self.chips.columnconfigure(col, weight=1, uniform="chip")

    def _layout_chain(self) -> None:
        stages = (self.doc or {}).get("stages") or []
        if not stages:
            return
        rebuild = len(self._stage_cells) != len(stages)
        if rebuild:
            for w in self.chain_strip.winfo_children():
                w.destroy()
            self._stage_cells = []
        # One row while there is room; wrap to two rows on a narrow window (RDP sessions are often 1024 wide).
        per_row = len(stages) if self._doing_width >= 980 else max(1, (len(stages) + 1) // 2)
        for i, s in enumerate(stages):
            r, c = divmod(i, per_row)
            if rebuild:
                cell = tk.Frame(self.chain_strip, bg=PANEL, highlightbackground=EDGE, highlightthickness=1)
                nm = tk.Label(cell, bg=PANEL, fg=FG, font=FONT_SB, anchor="nw", justify="left")
                nm.pack(fill="x", padx=8, pady=(8, 0))
                bar = tk.Frame(cell, bg=PANEL, height=3)
                bar.pack(fill="x", padx=8, pady=(6, 0))
                st = tk.Label(cell, bg=PANEL, font=FONT_SB, anchor="w")
                st.pack(fill="x", padx=8, pady=(4, 0))
                no = tk.Label(cell, bg=PANEL, fg=FG, font=FONT_S, anchor="nw", justify="left")
                no.pack(fill="x", padx=8, pady=(2, 8))
                widgets = {"cell": cell, "nm": nm, "bar": bar, "st": st, "no": no}
                for w in widgets.values():
                    w.bind("<Button-1>", lambda _e, k=i: self._select_stage(k))
                    try:
                        w.configure(cursor="hand2")
                    except tk.TclError:
                        pass
                self._stage_cells.append((cell, widgets))
            cell, widgets = self._stage_cells[i]
            wide = max(int((self._doing_width - 60) / max(per_row, 1)) - 24, 100)
            widgets["nm"].config(text=s["stage"], wraplength=wide)
            widgets["bar"].config(bg=s["colour_dark"])
            widgets["st"].config(text=s["status"].upper(), fg=s["colour_dark"])
            widgets["no"].config(text=s["number"], wraplength=wide)
            cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        for c in range(per_row):
            self.chain_strip.columnconfigure(c, weight=1, uniform="stage")
        if self._stage_sel is not None and self._stage_sel < len(stages):
            self._select_stage(self._stage_sel)

    def _select_stage(self, i: int) -> None:
        stages = (self.doc or {}).get("stages") or []
        if i >= len(stages):
            return
        self._stage_sel = i
        for k, (cell, _w) in enumerate(self._stage_cells):
            cell.config(highlightbackground=(stages[k]["colour_dark"] if k == i else EDGE),
                        highlightthickness=(2 if k == i else 1))
        s = stages[i]
        self.chain_detail.config(text="%s — %s. %s" % (s["stage"], s["number"], s["detail"]), fg=FG)

    def _draw_trend(self) -> None:
        """A sparkline of the board. Runs on a DIFFERENT set of questions are drawn hollow and are not
        joined to the line -- joining them would be a cross-population comparison, which the measurement
        bar forbids and which would read as a fall that never happened."""
        cv = self.trend_cv
        cv.delete("all")
        pts = (self.trend or {}).get("points") or []
        w = max(int(cv.winfo_width()), 400)
        h = int(cv["height"])
        if len(pts) < 2:
            cv.create_text(14, h // 2, text="Not enough full checks on record to draw a trend yet.",
                           fill=DIM, font=FONT, anchor="w")
            self.trend_note.config(text="")
            return
        pad_l, pad_r, pad_t, pad_b = 46, 156, 14, 26   # right margin holds the "simple rules NN in 100" label
        vals = [p["model"] for p in pts] + [p["floor"] for p in pts if p["floor"] is not None]
        lo, hi = min(vals), max(vals)
        span = max(hi - lo, 0.02)
        lo, hi = lo - span * 0.25, hi + span * 0.25
        iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
        X = lambda i: pad_l + iw * i / max(len(pts) - 1, 1)          # noqa: E731
        Y = lambda v: pad_t + ih - ih * (v - lo) / (hi - lo)         # noqa: E731
        fl = [(X(i), Y(p["floor"])) for i, p in enumerate(pts) if p["floor"] is not None]
        if len(fl) > 1:
            flat = [c for q in fl for c in q]
            cv.create_line(*flat, fill="#5a5a5a", width=1, dash=(4, 3))
            cv.create_text(fl[-1][0] + 8, fl[-1][1], text="simple rules %.0f in 100" % (pts[-1]["floor"] * 100),
                           fill=DIM, font=FONT_S, anchor="w")
        run: list[float] = []
        for i, p in enumerate(pts):
            if p["comparable"]:
                run += [X(i), Y(p["model"])]
            else:
                if len(run) >= 4:
                    cv.create_line(*run, fill=GREEN, width=2, smooth=False)
                run = []
        if len(run) >= 4:
            cv.create_line(*run, fill=GREEN, width=2, smooth=False)
        for i, p in enumerate(pts):
            x, y = X(i), Y(p["model"])
            if p["comparable"]:
                cv.create_oval(x - 3, y - 3, x + 3, y + 3, fill=GREEN, outline=GREEN)
            else:
                cv.create_oval(x - 4, y - 4, x + 4, y + 4, fill=CARD, outline=DIM, width=2)
        # Few's rule: a sparkline needs magnitude -- label the first and the last value.
        cv.create_text(X(0) - 8, Y(pts[0]["model"]), text="%.0f" % (pts[0]["model"] * 100), fill=FG,
                       font=FONT_S, anchor="e")
        cv.create_text(X(len(pts) - 1) + 8, Y(pts[-1]["model"]), text="%.0f in 100" % (pts[-1]["model"] * 100),
                       fill=GREEN, font=FONT_B, anchor="w")
        cv.create_text(pad_l, h - 8, text=pts[0]["ts"], fill=DIM, font=FONT_S, anchor="w")
        cv.create_text(X(len(pts) - 1), h - 8, text=pts[-1]["ts"], fill=DIM, font=FONT_S, anchor="e")
        n_off = sum(1 for p in pts if not p["comparable"])
        self.trend_title.config(text="THE BOARD OVER THE LAST %d FULL CHECKS" % len(pts))
        self.trend_note.config(
            text=("Hollow marks (%d of %d) were measured on a different set of questions, so they are not joined "
                  "to the line and must not be read as a rise or a fall." % (n_off, len(pts))) if n_off else
                 "Every check shown was measured on the same set of questions.")

    def _fill_sections(self) -> None:
        self._wraps_dyn = []          # the labels below are destroyed and rebuilt on every refresh
        d = self.doc or {}
        moved = d.get("moved") or []
        self._fill_list(self.sec_moved, [("%s  %s" % (m["date"], m["text"])).strip() for m in moved], preview=3)
        self.sec_moved.sub.config(text="newest first · %d recorded" % len(moved))
        self._fill_list(self.sec_running, d.get("running") or [], preview=99)
        self._fill_list(self.sec_next, d.get("next") or [], preview=2)
        self._fill_list(self.sec_risks, d.get("risks") or [], preview=1)
        if d.get("mtime"):
            self.sec_risks.sub.config(text="live document last edited %s" % d["mtime"])

    def _fill_list(self, sec: "Disclosure", items: list[str], preview: int = 3) -> None:
        for holder in (sec.preview, sec.body):
            for w in holder.winfo_children():
                w.destroy()
        if not items:
            tk.Label(sec.preview, text="Nothing recorded.", bg=CARD, fg=DIM, font=FONT, anchor="w").pack(fill="x")
            sec.sub.config(text="")
            sec.has_more = False
            sec.open = False
            sec._render()
            return
        head, tail = items[:preview], items[preview:]
        for holder, group in ((sec.preview, head), (sec.body, tail)):
            for it in group:
                row = tk.Frame(holder, bg=CARD)
                row.pack(fill="x", pady=(0, 5))
                tk.Label(row, text="•", bg=CARD, fg=BLUE, font=FONT, anchor="nw").pack(side="left", padx=(0, 6))
                lbl = tk.Label(row, text=it, bg=CARD, fg=FG, font=FONT, anchor="w", justify="left")
                lbl.pack(side="left", fill="x", expand=True)
                self._wraps_dyn.append((lbl, 120))
                lbl.config(wraplength=max(self._doing_width - 120, 260))
        sec.has_more = bool(tail)
        sec.sub.config(text=("%d more" % len(tail)) if tail else "")
        if not tail:
            sec.open = False
        sec._render()

    def _fill_table(self) -> None:
        sc = self.sc
        if not sc:
            return
        self.tv.delete(*self.tv.get_children())
        groups: dict[str, str] = {}
        for r in sc["capabilities"]:
            g = r["group"]
            if g not in groups:
                groups[g] = self.tv.insert("", "end", text=g, open=True, tags=("group",))
            if r["model"] is None:
                tag = "none"
            elif r["ci_sep"]:
                tag = "good"
            elif r["floor"] is not None and r["model"] <= r["floor"]:
                tag = "bad"
            else:
                tag = "meh"
            self.tv.insert(groups[g], "end", iid=r["key"], text="", tags=(tag,),
                           values=(r["name"] + (" (headline)" if r["headline"] else ""), r["how_well"], r["verdict"], r["trend"], r["fidelity"]))
        o, fi = sc["overall"], sc["fidelity"]
        self.sec_table.sub.config(
            text="%d of %d clearly better than a simple rule · %d of %d building blocks copy the brain's maths "
                 "exactly, %d are stand-ins" % (o["n_clearly_better"], o["n_abilities_scored"], fi["pinned"],
                                                fi["organs_total"], fi["stand_ins"]))
        self._show_detail()

    def _show_detail(self) -> None:
        d = self.detail
        d.config(state="normal"); d.delete("1.0", "end")
        sel = self.tv.selection()
        caps = {r["key"]: r for r in self.sc.get("capabilities", [])}
        if sel and sel[0] in caps:
            r = caps[sel[0]]
            d.insert("end", r["name"] + "\n", "h")
            d.insert("end", "%s; %s.\n" % (r["how_well"], r["verdict"]))
            if r["n"]:
                d.insert("end", "Measured on %s test items. Information-free twin: %s.\n" % (r["n"], SC._pct(r["twin"]) if r["twin"] is not None else "-"), "dim")
            d.insert("end", "Brain-faithful? %s.\n" % r["fidelity"], "warn" if r["stand_ins"] else None)
            if r["stand_ins"]:
                d.insert("end", "Stand-in parts: %s.\n" % ", ".join(r["stand_ins"]), "warn")
            d.insert("end", "Built from: %s.\n\n" % ", ".join(r["organs"]), "dim")
        else:
            d.insert("end", "Click an ability on the left for how it was measured.\n\n", "dim")
        for sec in ("WHAT IS NOT YET BRAIN-FAITHFUL",):
            d.insert("end", sec.capitalize() + "\n", "h")
            d.insert("end", self.sc["sections"].get(sec, "(not written yet)") + "\n\n")
        pr = self.sc.get("problems", {})
        if pr.get("in_review"):
            d.insert("end", "Finished work waiting for your review\n", "h")
            for p in pr["in_review"]:
                d.insert("end", "- %s\n" % p["title"][:140])
        d.config(state="disabled")

    # ------------------------------------------------------------------ tab 2
    def _build_tab_questions(self) -> None:
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="2. QUESTIONS FOR YOU")
        # LAYOUT: fixed-height pieces stacked top-down so the ANSWER BOX is always on screen (the first version
        # let the question list grow and pushed the answer box off the bottom -- owner: "there is no field for me
        # to answer questions"). Only the detail pane stretches.
        f.columnconfigure(0, weight=1); f.rowconfigure(2, weight=1)
        tk.Label(f, text="Questions I need you to decide. Click one, read the details, type your answer in the green box, press Send answer.",
                 bg=BG, fg=FG, font=FONT_B, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 2))
        self.qtv = ttk.Treeview(f, columns=("q",), show="tree headings", selectmode="browse", height=4)
        self.qtv.heading("#0", text="#"); self.qtv.column("#0", width=60, stretch=False)
        self.qtv.heading("q", text="Question"); self.qtv.column("q", width=1100)
        self.qtv.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        self.qtv.bind("<<TreeviewSelect>>", lambda _e: self._show_question())
        self.qdetail = tk.Text(f, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=10, pady=8, height=6)
        self.qdetail.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        self.qdetail.tag_configure("h", font=FONT_B, foreground=BLUE)
        box = tk.Frame(f, bg=BG); box.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 6))
        box.columnconfigure(0, weight=1); box.columnconfigure(1, weight=1)
        tk.Label(box, text="YOUR ANSWER to the selected question (type here, then press Send answer)", bg=BG, fg=GREEN, font=FONT_B, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(box, text="A NOTE FOR ME (anything you want the strategy session to know)", bg=BG, fg=BLUE, font=FONT_B, anchor="w").grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.answer = tk.Text(box, bg="#1f2f23", fg=FG, font=FONT, wrap="word", relief="flat", padx=8, pady=6, height=4,
                              insertbackground=FG, highlightthickness=2, highlightbackground=GREEN, highlightcolor=GREEN)
        self.answer.grid(row=1, column=0, sticky="ew")
        self.note = tk.Text(box, bg="#1f2633", fg=FG, font=FONT, wrap="word", relief="flat", padx=8, pady=6, height=4,
                            insertbackground=FG, highlightthickness=2, highlightbackground=BLUE, highlightcolor=BLUE)
        self.note.grid(row=1, column=1, sticky="ew", padx=(8, 0))
        tk.Button(box, text="Send answer", command=self._send_answer, bg="#2e5d3a", fg=FG, font=FONT_B, relief="flat", padx=12).grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Button(box, text="Send note", command=self._send_note, bg="#2e4a6e", fg=FG, font=FONT_B, relief="flat", padx=12).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(6, 0))
        # FINISHED WORK WAITING FOR YOUR VERDICT. The strategy session integrates a piece of work ONLY once you
        # have marked it DONE (owner_verdict: DONE in that problem's OWNER_NOTES.md). This list + button saves
        # the trip to the file; typing into the file still works.
        rv = tk.Frame(f, bg=BG); rv.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
        rv.columnconfigure(0, weight=1)
        tk.Label(rv, text="Finished work waiting for your verdict (select one, then Mark as DONE to have it folded in)",
                 bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=0, sticky="ew")
        self.rvtv = ttk.Treeview(rv, columns=("t",), show="headings", selectmode="browse", height=3)
        self.rvtv.heading("t", text="What it delivers"); self.rvtv.column("t", width=1100)
        self.rvtv.grid(row=1, column=0, sticky="ew")
        tk.Button(rv, text="Mark as DONE", command=self._mark_done, bg="#5d4a2e", fg=FG, font=FONT_B, relief="flat", padx=12).grid(row=1, column=1, sticky="n", padx=(8, 0))
        self.qstatus = tk.Label(f, text="", bg=BG, fg=DIM, font=FONT, anchor="w")
        self.qstatus.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 8))

    def _fill_review(self) -> None:
        self.rvtv.delete(*self.rvtv.get_children())
        for p in self.sc.get("problems", {}).get("in_review", []):
            self.rvtv.insert("", "end", iid=p["slug"], values=(p["title"][:200],))

    def _mark_done(self) -> None:
        sel = self.rvtv.selection()
        if not sel:
            self.qstatus.config(text="Select a finished piece of work first.", fg=ORANGE); return
        slug = sel[0]
        path = REPO / "notes" / "problems" / slug / "OWNER_NOTES.md"
        try:
            txt = path.read_text(encoding="utf-8") if path.is_file() else ""
            if txt.startswith("---"):
                head, _, rest = txt[3:].partition("---")
                lines = [ln for ln in head.strip("\n").splitlines() if not ln.strip().startswith("owner_verdict:")]
                lines.append("owner_verdict: DONE")
                txt = "---\n" + "\n".join(lines) + "\n---" + rest
            else:
                txt = "---\nowner_verdict: DONE\n---\n\n" + txt
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(txt, encoding="utf-8", newline="\n")
            self.qstatus.config(text="Marked DONE: %s. The strategy session will fold it in." % slug[:60], fg=GREEN)
            self.refresh()
        except Exception as e:
            self.qstatus.config(text="Could not mark DONE: %s: %s" % (type(e).__name__, e), fg=RED)

    def _fill_questions(self) -> None:
        self.qtv.delete(*self.qtv.get_children())
        for q in self.sc.get("questions_for_owner", []):
            self.qtv.insert("", "end", iid=q["id"] or "-", text=q["id"] or "-", values=((q["question"] or "")[:300],))
        self.nb.tab(1, text="2. QUESTIONS FOR YOU (%d)" % len(self.sc.get("questions_for_owner", [])))
        self._show_question()

    def _show_question(self) -> None:
        d = self.qdetail
        d.config(state="normal"); d.delete("1.0", "end")
        sel = self.qtv.selection()
        qs = {q["id"]: q for q in self.sc.get("questions_for_owner", [])}
        if sel and sel[0] in qs:
            q = qs[sel[0]]
            d.insert("end", "Question\n", "h"); d.insert("end", (q["question"] or "") + "\n\n")
            d.insert("end", "What is waiting on it\n", "h"); d.insert("end", (q["why"] or "") + "\n\n")
            d.insert("end", "My recommendation\n", "h"); d.insert("end", (q["rec"] or "") + "\n")
        elif not qs:
            d.insert("end", "Nothing is waiting on you right now.")
        d.config(state="disabled")

    def _send_answer(self) -> None:
        sel = self.qtv.selection()
        text = self.answer.get("1.0", "end").strip()
        if not sel or not text:
            self.qstatus.config(text="Pick a question and type an answer first.", fg=ORANGE); return
        try:
            import board as B
            B.resolve(sel[0], text)
            self.answer.delete("1.0", "end")
            self.qstatus.config(text="Answer to %s saved to notes/BOARD.md." % sel[0], fg=GREEN)
            self.refresh()
        except Exception as e:
            self.qstatus.config(text="Could not save: %s: %s" % (type(e).__name__, e), fg=RED)

    def _send_note(self) -> None:
        text = self.note.get("1.0", "end").strip()
        if not text:
            self.qstatus.config(text="Type a note first.", fg=ORANGE); return
        try:
            import commentary as C
            C.add(text, source="the scorecard window")
            self.note.delete("1.0", "end")
            self.qstatus.config(text="Note saved to notes/COMMENTARY.md; it is read at the start of the next turn.", fg=GREEN)
        except Exception as e:
            self.qstatus.config(text="Could not save: %s: %s" % (type(e).__name__, e), fg=RED)

    # ------------------------------------------------------------------ tab 3
    def _build_tab_updates(self) -> None:
        """Significant updates only (achievements, improvements, walls overcome, problems) -- owner 2026-09-12. The owner
        clears them when read; cleared items are archived. Walls NOT overcome become questions in tab 2, not updates."""
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="3. UPDATES")
        f.columnconfigure(0, weight=1); f.rowconfigure(1, weight=1)
        tk.Label(f, text="Significant updates since you last cleared: what got better, what stand-in was replaced, what wall "
                         "was overcome, what went wrong. Press Clear when read.", bg=BG, fg=FG, font=FONT_B, anchor="w",
                 justify="left", wraplength=1220).grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        self.updates = tk.Text(f, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=12, pady=10)
        self.updates.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        for k, col in (("ACHIEVEMENT", GREEN), ("IMPROVEMENT", GREEN), ("WALL-OVERCOME", BLUE), ("PROBLEM", RED), ("QUESTION-FILED", ORANGE)):
            self.updates.tag_configure(k, foreground=col, font=FONT_B)
        self.updates.tag_configure("stamp", foreground=DIM)
        bar = tk.Frame(f, bg=BG); bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 10))
        tk.Button(bar, text="Clear (I have read these)", command=self._clear_updates, bg="#5d2e2e", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left")
        self.ustatus = tk.Label(bar, text="", bg=BG, fg=DIM, font=FONT, anchor="w"); self.ustatus.pack(side="left", padx=12)

    def _fill_updates(self) -> None:
        import owner_updates as U
        items = U.load()
        self.nb.tab(2, text="3. UPDATES (%d)" % len(items))
        t = self.updates; t.config(state="normal"); t.delete("1.0", "end")
        if not items:
            t.insert("end", "Nothing significant since you last cleared.")
        for it in reversed(items):
            t.insert("end", it["stamp"] + "  ", "stamp"); t.insert("end", it["kind"], it["kind"])
            t.insert("end", "\n" + it["text"] + "\n\n")
        t.config(state="disabled")

    def _clear_updates(self) -> None:
        try:
            import owner_updates as U
            n = U.clear(); self._fill_updates()
            self.ustatus.config(text="Cleared %d update(s); archived in notes/UPDATES_ARCHIVE.md." % n, fg=GREEN)
        except Exception as e:
            self.ustatus.config(text="Could not clear: %s: %s" % (type(e).__name__, e), fg=RED)

    # ------------------------------------------------------------------ tab 4
    def _build_tab_problems(self) -> None:
        """OPEN problems to hand to your own solver sessions (owner 2026-09-12: "create a button that will copy the prompt to my
        clipboard so I can paste it"). The prompt is problem_ledger.kickoff_prompt -- the single source of truth the CLI prints."""
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="4. PROBLEMS TO HAND OUT")
        f.columnconfigure(0, weight=2); f.columnconfigure(1, weight=3); f.rowconfigure(1, weight=1)
        tk.Label(f, text="Hard, bounded problems written for a separate solver session (opus). Click one, then press Copy and paste the "
                         "prompt into a new solver session. Lower priority number = more important. Problems with a SOLVED.md are not "
                         "listed here (they are in tab 2 waiting for your verdict).", bg=BG, fg=FG, font=FONT_B, anchor="w",
                 justify="left", wraplength=1220).grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4))
        self.ptv = ttk.Treeview(f, columns=("pri", "state", "title"), show="headings", selectmode="browse")
        self.ptv.heading("pri", text="Pri"); self.ptv.heading("state", text="Where it stands"); self.ptv.heading("title", text="Problem (plain words)")
        self.ptv.column("pri", width=50, anchor="center", stretch=False); self.ptv.column("state", width=150, anchor="w", stretch=False)
        self.ptv.column("title", width=360, anchor="w")
        self.ptv.grid(row=1, column=0, sticky="nsew", padx=(10, 4), pady=4)
        self.ptv.bind("<<TreeviewSelect>>", self._show_prompt)
        self.prompt = tk.Text(f, bg=PANEL, fg=FG, font=("Consolas", 10), wrap="word", relief="flat", padx=12, pady=10)
        self.prompt.grid(row=1, column=1, sticky="nsew", padx=(4, 10), pady=4)
        bar = tk.Frame(f, bg=BG); bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 2))
        tk.Button(bar, text="Copy solver prompt to clipboard", command=self._copy_prompt, bg="#2e5d3a", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left")
        self.assigned_var = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="Assigned to a solver session", variable=self.assigned_var, command=self._toggle_assigned, bg=BG, fg=FG,
                       selectcolor="#333", activebackground=BG, activeforeground=FG, font=FONT_B).pack(side="left", padx=16)
        self.pstatus = tk.Label(bar, text="", bg=BG, fg=DIM, font=FONT, anchor="w"); self.pstatus.pack(side="left", padx=12)
        # the solver's result comes back through the owner: paste it here, save it into the problem folder, mark DONE when satisfied
        tk.Label(f, text="Paste the solver session's final result / solution brief here (saved into the problem's folder as "
                         "SOLVER_RESULT_pasted.md; the strategy session reads it). Mark DONE only when you are satisfied -- that is the "
                         "signal the strategy session integrates on.", bg=BG, fg=DIM, font=FONT, anchor="w", justify="left",
                 wraplength=1220).grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 2))
        self.paste = tk.Text(f, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=10, pady=8, height=7, insertbackground=FG)
        self.paste.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        bar2 = tk.Frame(f, bg=BG); bar2.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 10))
        tk.Button(bar2, text="Save pasted result to the problem folder", command=self._save_pasted, bg="#2e4a5d", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left")
        tk.Button(bar2, text="Mark DONE (integrate it)", command=lambda: self._verdict("DONE"), bg="#2e5d3a", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left", padx=8)
        tk.Button(bar2, text="More needed", command=lambda: self._verdict("MORE_NEEDED"), bg="#5d4a2e", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left")
        tk.Button(bar2, text="Park it", command=lambda: self._verdict("PARKED"), bg="#444", fg=FG, font=FONT_B,
                  relief="flat", padx=12).pack(side="left", padx=8)
        self._problem_rows: list = []

    def _fill_problems(self) -> None:
        import problem_ledger as PL
        # OPEN briefs AND solved-but-not-yet-DONE ones (owner 2026-09-12: a solved problem must not vanish from this tab --
        # it stays listed as 'solved -> awaiting your verdict' with the Mark DONE button here). Integrated ones drop off.
        rows = [r for r in PL.scan() if r["brief"] and not r.get("integrated")
                and (r["state"] == "OPEN" or (r["state"] in ("SOLVED", "PARTIAL", "REFUTED") and PL.load_owner(r["slug"]).get("verdict", "") != "DONE"))]
        rows.sort(key=lambda r: (r["priority"] if isinstance(r["priority"], int) else 999, r["slug"]))
        self._problem_rows = rows
        self.nb.tab(3, text="4. PROBLEMS TO HAND OUT (%d)" % len(rows))
        sel = self.ptv.selection(); keep = self.ptv.item(sel[0], "values")[1] if sel else None
        self.ptv.delete(*self.ptv.get_children())
        for r in rows:
            title = r["slug"].replace("_", " ")
            iid = self.ptv.insert("", "end", values=(r["priority"] if r["priority"] is not None else "-", self._state_word(r), title))
            if keep == title:
                self.ptv.selection_set(iid)

    @staticmethod
    def _state_word(r) -> str:
        import problem_ledger as PL
        d = os.path.join(PL.PROBLEMS_DIR, r["slug"])
        verdict = PL.load_owner(r["slug"]).get("verdict", "")
        if verdict == "DONE":
            return "DONE -> folding in"
        if r.get("state") in ("SOLVED", "PARTIAL", "REFUTED"):
            return "%s -> awaiting your verdict" % r["state"].lower()
        if verdict == "PARKED":
            return "parked"
        if os.path.exists(os.path.join(d, "SOLVER_RESULT_pasted.md")):
            return "result pasted" + (" (more needed)" if verdict == "MORE_NEEDED" else "")
        if r.get("assigned"):
            return "assigned"
        return "free"

    def _selected_slug(self):
        sel = self.ptv.selection()
        if not sel:
            return None
        idx = self.ptv.index(sel[0])
        return self._problem_rows[idx]["slug"] if idx < len(self._problem_rows) else None

    def _toggle_assigned(self) -> None:
        import problem_ledger as PL
        slug = self._selected_slug()
        if not slug:
            self.assigned_var.set(False); self.pstatus.config(text="Click a problem first.", fg=ORANGE); return
        PL.set_assigned(slug, bool(self.assigned_var.get())); self._fill_problems()
        self.pstatus.config(text=("Marked assigned: " if self.assigned_var.get() else "Unassigned: ") + slug[:60], fg=GREEN)

    def _save_pasted(self) -> None:
        import datetime
        import problem_ledger as PL
        slug = self._selected_slug(); text = self.paste.get("1.0", "end").strip()
        if not slug:
            self.pstatus.config(text="Click a problem first.", fg=ORANGE); return
        if not text:
            self.pstatus.config(text="Nothing pasted.", fg=ORANGE); return
        path = os.path.join(PL.PROBLEMS_DIR, slug, "SOLVER_RESULT_pasted.md")
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n\n## pasted by the owner %s (raw; strategy reads this)\n\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text))
        PL.set_assigned(slug, True); self._fill_problems()
        self.pstatus.config(text="Saved %d characters to %s" % (len(text), os.path.relpath(path, REPO)), fg=GREEN)

    def _verdict(self, verdict: str) -> None:
        import problem_ledger as PL
        slug = self._selected_slug()
        if not slug:
            self.pstatus.config(text="Click a problem first.", fg=ORANGE); return
        note = self.paste.get("1.0", "end").strip() or PL.load_owner(slug).get("text", "")
        try:
            PL.save_owner(slug, verdict, note); self._fill_problems()
            self.pstatus.config(text="%s recorded for %s%s" % (verdict, slug[:50], " -- the strategy session will fold it in." if verdict == "DONE" else ""), fg=GREEN)
        except Exception as e:
            self.pstatus.config(text="Could not record: %s: %s" % (type(e).__name__, e), fg=RED)

    def _show_prompt(self, _evt=None) -> None:
        import problem_ledger as PL
        sel = self.ptv.selection()
        if not sel:
            return
        idx = self.ptv.index(sel[0])
        if idx >= len(self._problem_rows):
            return
        slug = self._problem_rows[idx]["slug"]
        self.prompt.config(state="normal"); self.prompt.delete("1.0", "end")
        self.prompt.insert("end", PL.kickoff_prompt(slug)); self.prompt.config(state="disabled")
        self.assigned_var.set(bool(self._problem_rows[idx].get("assigned")))
        self.paste.delete("1.0", "end"); self.paste.insert("end", PL.load_owner(slug).get("text", ""))
        self.pstatus.config(text="Showing the prompt for: %s" % slug, fg=DIM)

    def _copy_prompt(self) -> None:
        text = self.prompt.get("1.0", "end").strip()
        if not text:
            self.pstatus.config(text="Click a problem first.", fg=ORANGE); return
        try:
            self.root.clipboard_clear(); self.root.clipboard_append(text); self.root.update()
            self.pstatus.config(text="Copied %d characters -- paste it into a new solver session." % len(text), fg=GREEN)
        except Exception as e:
            self.pstatus.config(text="Could not copy: %s: %s" % (type(e).__name__, e), fg=RED)

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        try:
            self.sc = SC.build()
            try:
                SC.write_outputs(self.sc)
            except Exception:
                pass
            self._fill_doing(); self._fill_questions(); self._fill_review(); self._fill_updates()
            self._fill_problems()
            self.stamp.config(text="Last full check of the system: %s   |   scorecard refreshed %s   |   %d full checks on record"
                              % (self.sc.get("last_full_check") or "none yet", self.sc["generated"], self.sc["n_full_checks"]), fg=DIM)
        except Exception as e:
            self.stamp.config(text="Could not build the scorecard: %s: %s" % (type(e).__name__, e), fg=RED)

    def _tick(self) -> None:
        self.refresh()
        self.root.after(REFRESH_MS, self._tick)


def parser_smoke() -> dict:
    """Parse notes/HOW_WE_ARE_DOING.md into the section model WITHOUT opening a window.

    This is the half of the tab that can break silently (a renamed heading, a status word the colour
    map does not know, a stage row with no number), so it is checked on its own and runs anywhere --
    including over ssh on a machine with no display.
    """
    doc = HWD.parse_doc()
    assert doc["ok"], "notes/HOW_WE_ARE_DOING.md must be readable: %s" % doc.get("error")
    for sec in HWD.SECTION_ORDER:
        assert sec in doc["sections"], "the live document is missing '## %s'" % sec
    assert doc["goal"] and doc["position"], "GOAL and POSITION must both carry text"
    assert len(doc["stages"]) >= 5, "the plan needs its stages"
    known = [k for k, _, _ in HWD.STATUS_STYLES]
    for s in doc["stages"]:
        assert s["status_key"] in known, "stage %r: unknown status %r" % (s["stage"], s["status"])
        assert s["number"] and s["detail"], "stage %r needs a number and a plain-words detail" % s["stage"]
    assert doc["moved"] and doc["moved"][0]["date"], "WHAT MOVED needs dated entries"
    assert doc["running"] and doc["next"] and doc["risks"], "running / next / risks must not be empty"
    trend = HWD.load_trend()
    assert trend["ok"] and any(p["comparable"] for p in trend["points"]), "board history must load"
    print("[scorecard_gui parser smoke] PASS: %d sections, %d stages (%s), %d movements, %d board runs"
          % (len(doc["sections"]), len(doc["stages"]),
             ", ".join(s["status_key"].lower() for s in doc["stages"]), len(doc["moved"]),
             len(trend["points"])))
    return doc


def self_test() -> int:
    doc = parser_smoke()
    sc = SC.build()
    assert sc["capabilities"] and sc["sections"].get("THE SHORT VERSION"), "scorecard must build with a short version"
    root = tk.Tk()
    w = ScorecardWindow(root, offscreen=True)
    root.update()
    # --- the redesigned tab 1
    assert w.position_lbl.cget("text") == doc["position"], "the band must show the live document's position line"
    assert len(w._stage_cells) == len(doc["stages"]), ("chain strip", len(w._stage_cells))
    w._select_stage(0)
    assert doc["stages"][0]["stage"] in w.chain_detail.cget("text"), "clicking a stage must show its detail"
    assert len(w.chips.winfo_children()) >= 3, "the band must carry the board figures"
    assert w.trend_cv.find_all(), "the trend panel must draw something"
    foldable = [s for s in (w.sec_moved, w.sec_running, w.sec_next, w.sec_risks, w.sec_table) if s.has_more]
    assert len(foldable) >= 3, "most sections should have something folded away"
    for sec in foldable:
        assert not sec.open, "sections start folded"
        sec.toggle(); assert sec.open, "a section with more must open"; sec.toggle()
    # 'what is running' shows everything, so it carries no fold arrow and clicking it does nothing.
    assert not w.sec_running.has_more and w.sec_running.arrow.cget("text").strip() == "", "running work is never hidden"
    assert w.sec_moved.preview.winfo_children(), "the newest movements must be visible without unfolding"
    n_rows = sum(len(w.tv.get_children(g)) for g in w.tv.get_children())
    assert n_rows == len(sc["capabilities"]), (n_rows, len(sc["capabilities"]))
    n_prob = len(w.ptv.get_children())
    assert n_prob == len(w._problem_rows) and n_prob >= 1, ("problems tab", n_prob)
    first = w.ptv.get_children()[0]; w.ptv.selection_set(first); w._show_prompt()
    assert "slug is:" in w.prompt.get("1.0", "end"), "kickoff prompt must render"
    w._copy_prompt(); assert w.root.clipboard_get().startswith("You are the SOLVER"), "clipboard copy must work"
    assert any(tok in w.ptv.item(first, "values")[1] for tok in ("free", "assigned", "result pasted", "parked", "DONE", "awaiting")), "state word"
    root.destroy()
    print("[scorecard_gui self-test] PASS: %d open problems listed with copyable prompts" % n_prob)
    print("[scorecard_gui self-test] PASS: band + %d-stage chain + trend + 5 folded sections render; "
          "%d abilities in the folded table, %d questions" % (len(doc["stages"]), n_rows, len(sc["questions_for_owner"])))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="the owner's scorecard window")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--parser-smoke", action="store_true", dest="parser_smoke",
                    help="parse notes/HOW_WE_ARE_DOING.md into the section model and exit; opens no window")
    a = ap.parse_args(argv)
    if a.parser_smoke:
        parser_smoke()
        return 0
    if a.self_test:
        return self_test()
    root = tk.Tk()
    ScorecardWindow(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
