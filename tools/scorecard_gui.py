"""tools/scorecard_gui.py -- the owner's window, simplified (2026-09-11).

Owner: "simplify it (new version), and create a tab (remove the others) that gives me a clear idea of how well the
substrate is performing, and its capabilities ... kept updated, from a document that you keep updated ... We can
also keep the tab that asks me questions ... use me as a resource ... intuitive and jargon free."

TWO TABS.
  1. HOW WE'RE DOING   the plain-language scorecard: the short version, one row per ability (how well, compared
                       with a simple rule, trend since the previous full check, brain-faithful or a stand-in),
                       what changed, what we are working on, what is not yet brain-faithful.
                       Source of truth: notes/SCORECARD.md (hand-written sections) + data/scorecard.json, both
                       produced by tools/scorecard.py from the measurements on disk. Rebuilt on every refresh.
  2. QUESTIONS FOR YOU the open board questions (tools/board.py / notes/BOARD.md) with an answer box, plus a
                       "note for the strategy session" box (notes/COMMENTARY.md). Typing into the files directly
                       still works; this window just saves the trip.
The old eight-tab window (tools/status_gui.py) is left in place, untouched.

Launch:  .venv/Scripts/python.exe tools/scorecard_gui.py        (--self-test builds the window offscreen and exits)
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

REFRESH_MS = 60_000
BG, PANEL, FG, DIM, GREEN, BLUE, ORANGE, RED = "#1e1e1e", "#262626", "#e8e8e8", "#9a9a9a", "#7ccf8a", "#8ab4f8", "#f0b35b", "#ef6e6e"
FONT, FONT_B, FONT_H = ("Segoe UI", 11), ("Segoe UI", 11, "bold"), ("Segoe UI", 15, "bold")


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

    # ------------------------------------------------------------------ tab 1
    def _build_tab_doing(self) -> None:
        f = tk.Frame(self.nb, bg=BG)
        self.nb.add(f, text="1. HOW WE'RE DOING")
        f.columnconfigure(0, weight=3); f.columnconfigure(1, weight=2)
        f.rowconfigure(2, weight=1)
        self.headline = tk.Label(f, text="", bg=BG, fg=FG, font=FONT_H, anchor="w", justify="left", wraplength=1220)
        self.headline.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        self.short = tk.Label(f, text="", bg=BG, fg=FG, font=FONT, anchor="w", justify="left", wraplength=1220)
        self.short.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        cols = ("ability", "how", "vs", "trend", "faithful")
        self.tv = ttk.Treeview(f, columns=cols, show="tree headings", selectmode="browse")
        for c, w, t in (("#0", 220, "Group"), ("ability", 330, "Ability"), ("how", 200, "How well"),
                        ("vs", 300, "Compared with a simple rule"), ("trend", 190, "Since the previous check"),
                        ("faithful", 250, "Brain-faithful?")):
            self.tv.heading(c, text=t)
            self.tv.column(c, width=w, stretch=(c in ("ability", "vs")))
        self.tv.tag_configure("good", foreground=GREEN)
        self.tv.tag_configure("meh", foreground=ORANGE)
        self.tv.tag_configure("bad", foreground=RED)
        self.tv.tag_configure("none", foreground=DIM)
        self.tv.tag_configure("group", foreground=BLUE, font=FONT_B)
        self.tv.grid(row=2, column=0, sticky="nsew", padx=(10, 4), pady=4)
        self.tv.bind("<<TreeviewSelect>>", lambda _e: self._show_detail())
        right = tk.Frame(f, bg=BG)
        right.grid(row=2, column=1, sticky="nsew", padx=(4, 10), pady=4)
        right.rowconfigure(1, weight=1); right.columnconfigure(0, weight=1)
        tk.Label(right, text="Details, what changed, what we are working on", bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=0, sticky="ew")
        self.detail = tk.Text(right, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=10, pady=8)
        self.detail.grid(row=1, column=0, sticky="nsew")
        self.detail.tag_configure("h", font=FONT_B, foreground=BLUE)
        self.detail.tag_configure("dim", foreground=DIM)
        self.detail.tag_configure("warn", foreground=ORANGE)

    def _fill_doing(self) -> None:
        sc = self.sc
        o, fi = sc["overall"], sc["fidelity"]
        self.headline.config(text="%d of %d abilities are clearly better than a simple rule. %d of %d building blocks copy the brain's math exactly; %d are stand-ins still being replaced."
                             % (o["n_clearly_better"], o["n_abilities_scored"], fi["pinned"], fi["organs_total"], fi["stand_ins"]))
        self.short.config(text=sc["sections"].get("THE SHORT VERSION", "(no short version written yet)"))
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
        for sec in ("WHAT CHANGED LATELY", "WHAT WE ARE WORKING ON", "WHAT IS NOT YET BRAIN-FAITHFUL"):
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


def self_test() -> int:
    sc = SC.build()
    assert sc["capabilities"] and sc["sections"].get("THE SHORT VERSION"), "scorecard must build with a short version"
    root = tk.Tk()
    w = ScorecardWindow(root, offscreen=True)
    root.update()
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
    print("[scorecard_gui self-test] PASS: %d abilities rendered, %d questions, short version present" % (n_rows, len(sc["questions_for_owner"])))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="the owner's scorecard window")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    root = tk.Tk()
    ScorecardWindow(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
