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
        f.columnconfigure(0, weight=1); f.rowconfigure(1, weight=2); f.rowconfigure(3, weight=1)
        tk.Label(f, text="Open questions. Pick one, type your answer, press Send. (Typing into notes/BOARD.md works too.)",
                 bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 2))
        self.qtv = ttk.Treeview(f, columns=("q",), show="tree headings", selectmode="browse")
        self.qtv.heading("#0", text="ID"); self.qtv.column("#0", width=70, stretch=False)
        self.qtv.heading("q", text="Question"); self.qtv.column("q", width=1100)
        self.qtv.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        self.qtv.bind("<<TreeviewSelect>>", lambda _e: self._show_question())
        self.qdetail = tk.Text(f, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=10, pady=8, height=9)
        self.qdetail.grid(row=2, column=0, sticky="ew", padx=10, pady=4)
        self.qdetail.tag_configure("h", font=FONT_B, foreground=BLUE)
        box = tk.Frame(f, bg=BG); box.grid(row=3, column=0, sticky="nsew", padx=10, pady=(4, 10))
        box.columnconfigure(0, weight=1); box.columnconfigure(1, weight=1); box.rowconfigure(1, weight=1)
        tk.Label(box, text="Your answer to the selected question", bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(box, text="A note for the strategy session (anything you want me to know)", bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.answer = tk.Text(box, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=8, pady=6, height=5)
        self.answer.grid(row=1, column=0, sticky="nsew")
        self.note = tk.Text(box, bg=PANEL, fg=FG, font=FONT, wrap="word", relief="flat", padx=8, pady=6, height=5)
        self.note.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        tk.Button(box, text="Send answer", command=self._send_answer, bg="#2e5d3a", fg=FG, font=FONT_B, relief="flat", padx=12).grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Button(box, text="Send note", command=self._send_note, bg="#2e4a6e", fg=FG, font=FONT_B, relief="flat", padx=12).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(6, 0))
        # FINISHED WORK WAITING FOR YOUR VERDICT. The strategy session integrates a piece of work ONLY once you
        # have marked it DONE (owner_verdict: DONE in that problem's OWNER_NOTES.md). This list + button saves
        # the trip to the file; typing into the file still works.
        rv = tk.Frame(f, bg=BG); rv.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
        rv.columnconfigure(0, weight=1)
        tk.Label(rv, text="Finished work waiting for your verdict (select one, then Mark as DONE to have it folded in)",
                 bg=BG, fg=DIM, font=FONT, anchor="w").grid(row=0, column=0, sticky="ew")
        self.rvtv = ttk.Treeview(rv, columns=("t",), show="headings", selectmode="browse", height=4)
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

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        try:
            self.sc = SC.build()
            try:
                SC.write_outputs(self.sc)
            except Exception:
                pass
            self._fill_doing(); self._fill_questions(); self._fill_review()
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
    root.destroy()
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
