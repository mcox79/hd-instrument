#!/usr/bin/env python
"""State collector for the owner-facing status window (`tools/status_gui.py`).

WHY THIS EXISTS (owner verdict, 2026-08-15): *"that gui is ancient and it's not showing
anything I care about - can you update it so it's relevant?"* `tools/dash_gui.py` is built
around a fleet/queue model that is dead (the 4-session architecture was retired; it is
agent-spawn only now). It shows GPU temperature and queue depth. It does not show whether the
system is beating the thing it has to beat, what is waiting on the owner, or whether the
overnight loop is armed.

WHAT THIS MODULE IS. One read-only collector, five panels, each independent:

  1. WALLS      per-component health -- SCORE AND ITS FLOOR, ALWAYS AS A PAIR
  2. BOARD      the questions waiting on the owner        (tools/board.py, reused)
  3. RUNNING    agents, detached experiments, GPU         (inflight_monitor.build_state, reused)
  4. RESULTS    latest verdicts, negatives as loud as wins
  5. LOOP       overnight continuation loop               (tools/autoloop.py, reused)

FOUR RULES IT IS BUILT AROUND, each one paid for:

  * A SCORE WITHOUT ITS FLOOR IS FORBIDDEN. The whole "we beat scramble" era was a floor
    error; a spelling-only baseline (8.70%) currently beats the live system (4.80%). Every
    number this module emits carries `floor`, `floor_name`, `standing` and `separated`.
  * MISSING IS INFORMATION. A panel with no data reports MISSING. It never invents a number
    and never hides itself. A blank where a measurement should be is the finding.
  * NOTHING MAY BLOCK. Every external source (dashboard HTTP, SSH, WMI, the filesystem) runs
    under a wall-clock cap that no socket or subprocess internal can defeat, and every panel
    is wrapped so that its failure degrades that panel to UNKNOWN and leaves the other four
    intact. A dashboard that dies because SSH is down is useless at 3am. Proven by
    `--self-test`, which runs the whole collection with the remote pointed at a dead port and
    an invalid SSH alias, and with every required file absent.
  * REMOTE LIVENESS IS THE CHECKPOINT, NOT THE HEARTBEAT (CLAUDE.md). The `_heartbeat.jsonl`
    cadence is coarse and has false-alarmed as "stalled" three times. The truth signal is the
    in-progress checkpoint mtime advancing plus GPU utilisation.

DO NOT FORK A SECOND SOURCE OF TRUTH. Running-state comes from
`inflight_monitor.build_state()`, the board from `tools/board.py`, the loop from
`tools/autoloop.py` -- imported, never reimplemented. Only the three things that had no
existing source (component health, the verdict index, live agents) are collected here, and
they are collected here ONCE so the GUI stays a renderer.

WRITES. This module writes NOTHING. (One inherited exception, disclosed rather than hidden:
`inflight_monitor.build_state()` itself rate-limits a self-heal that can restart a wedged
dashboard worker when the web feed has been frozen for over 10 minutes. That behaviour
predates this file and is shared with `tools/dash_gui.py`.) The only write anywhere in the
new GUI is the board answer write-back, which goes through `board.resolve()` -- an atomic
temp-file-plus-replace that has its own self-test for hand-edited boards.

COUPLING (CLAUDE.md "a doc parsed by code is coupled to it"). This module reads
`data/component_health.json`, whose numbers are transcribed from `notes/PLAN.md` section 3.
Each row carries `verify` strings that must still appear in `notes/PLAN.md` or
`notes/STATUS.md`; a row whose string has gone missing renders as CHECK-PLAN rather than
quietly showing a stale figure. Dash characters are normalised before comparison so an
en-dash in the plan matches a hyphen in the spec.

USAGE
  python tools/status_state.py                 # human-readable dump
  python tools/status_state.py --json          # machine-readable
  python tools/status_state.py --self-test     # degradation + timing proof
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# Reuse, never reimplement. Each import is optional: a missing/broken dependency degrades ONE
# panel to UNKNOWN instead of taking the window down.
try:
    import inflight_monitor as _inflight
except Exception as _e:  # pragma: no cover - import guard
    _inflight = None
    _INFLIGHT_ERR = f"{type(_e).__name__}: {_e}"
else:
    _INFLIGHT_ERR = ""

try:
    import board as _board
except Exception as _e:  # pragma: no cover
    _board = None
    _BOARD_ERR = f"{type(_e).__name__}: {_e}"
else:
    _BOARD_ERR = ""

try:
    import autoloop as _autoloop
except Exception as _e:  # pragma: no cover
    _autoloop = None
    _AUTOLOOP_ERR = f"{type(_e).__name__}: {_e}"
else:
    _AUTOLOOP_ERR = ""

# Panels A (progress), B (the brain organ map) and C (fidelity). Their collection lives in its own
# module purely for size -- it is NOT a second source of truth: this file remains the one entry
# point, and each collector below runs through the same `_panel()` wrapper as the original five,
# so a failure there degrades one panel and leaves the rest of the window standing.
try:
    import status_organs as _organs
except Exception as _e:  # pragma: no cover
    _organs = None
    _ORGANS_ERR = f"{type(_e).__name__}: {_e}"
else:
    _ORGANS_ERR = ""

# THE PLAN PANEL (added 2026-08-16, owner: "can you add your plan to that, and make sure you keep
# all this updated?"). It PARSES notes/LONG_TERM_PLAN.md and notes/PLAN.md live on every refresh --
# there is no transcription of the plan anywhere in this window, because a transcribed plan is
# stale the moment the plan moves, which is the whole defect being fixed. Same import guard as the
# others: a failure here degrades ONE panel.
try:
    import status_plan as _plan
except Exception as _e:  # pragma: no cover
    _plan = None
    _PLAN_ERR = f"{type(_e).__name__}: {_e}"
else:
    _PLAN_ERR = ""

# PER-ROW EVIDENCE AGES (owner, 2026-08-16: *"I'd also like timestamps for each entry on the dash -
# when it was last updated so I know what's new and what is old."*). Same import guard as the rest:
# a failure here leaves every panel standing and the ages simply report UNKNOWN, which is the
# correct degradation -- the one thing that must never happen is a row stamped with the REFRESH
# time, because a fresh clock over a stale number reads as current.
try:
    import status_evidence as _ev
except Exception as _e:  # pragma: no cover
    _ev = None
    _EV_ERR = f"{type(_e).__name__}: {_e}"
else:
    _EV_ERR = ""

# WHAT CLAIMS TO BE RUNNING (added 2026-08-16). The live scan can only see processes that exist, so
# a dead run vanished from the panel while its scratch/*.pid file went on being quoted as live. This
# module reads those claims and checks each against the OS. Same import guard as the rest.
try:
    import status_pidclaims as _pidclaims
except Exception as _e:  # pragma: no cover
    _pidclaims = None
    _PIDCLAIMS_ERR = f"{type(_e).__name__}: {_e}"
else:
    _PIDCLAIMS_ERR = ""

# --- paths (env-overridable so the self-test can point at absent files) ------
# notes/, not data/: `.gitignore` line 43 is `data/*`, so a spec kept under data/ would be
# absent from a fresh clone and panel 1 would come up MISSING for the next person. It also
# belongs beside notes/PLAN.md, the document it is transcribed from and checked against.
COMPONENT_SPEC = Path(os.environ.get("HD_COMPONENT_SPEC")
                      or (REPO / "notes" / "component_health.json"))
PLAN_DOC = Path(os.environ.get("HD_PLAN_DOC") or (REPO / "notes" / "PLAN.md"))
# ADDED 2026-08-16. Panel 1's headline named SPELLING 8.70% as the floor to beat; that is
# superseded by the CONSTANT GUESS (13.90% / 15.18%), which beats the spelling channel
# CI-separated. The correction is stated in notes/LONG_TERM_PLAN.md section 2 and NOWHERE in
# notes/PLAN.md -- so without this document in the authority corpus, writing the correction into
# the spec would have rendered the row as CHECK-PLAN, and the previous agent correctly declined to
# make that trade. notes/PLAN.md is do-not-touch; ADDING an authority document is not editing one.
LONG_PLAN_DOC = Path(os.environ.get("HD_LONG_PLAN_DOC")
                     or (REPO / "notes" / "LONG_TERM_PLAN.md"))
STATUS_DOC = Path(os.environ.get("HD_STATUS_DOC") or (REPO / "notes" / "STATUS.md"))
BOARD_DOC = Path(os.environ.get("HD_BOARD_PATH") or (REPO / "notes" / "BOARD.md"))
DATA_DIR = Path(os.environ.get("HD_DATA_DIR") or (REPO / "data"))
HOOK_STATE = DATA_DIR / "hook_state"
AGENT_ROOT = Path(os.environ.get("HD_AGENT_ROOT") or (Path.home() / ".claude" / "projects"))

# --- budgets. Worst case total is the sum of these, and it is bounded. ------
WALLS_BUDGET_S = 4.0
BOARD_BUDGET_S = 4.0
RUNNING_BUDGET_S = 14.0     # build_state is internally bounded to ~10s
# RAISED 8.0 -> 12.0 on 2026-08-16, and the reason is on the record rather than implied. The panel
# was measured at 18.08 s against the old 8 s while live runs were writing, so it intermittently
# showed TIMEOUT and no results. The COST was fixed first (see `_newest_metrics`: 8,015 file stats
# -> a few dozen, measured 0.866 s -> ~0.01 s warm); the budget is raised as well because the
# failure mode is I/O CONTENTION, which multiplied the old cost roughly 20x and can multiply the
# new one too. 12 s keeps the whole collection inside one 20 s refresh with room to spare.
RESULTS_BUDGET_S = 12.0
LOOP_BUDGET_S = 3.0
# Measured, not guessed: the three new panels collect in ~0.05 s together (the organ map is parsed
# once and cached on mtime; the fidelity score runs in-process at ~16 ms). The budgets are set two
# orders of magnitude above that so a pathological file cannot wedge the window, and no panel here
# ever shells out or touches the network.
PROGRESS_BUDGET_S = 4.0
ORGANS_BUDGET_S = 5.0
FIDELITY_BUDGET_S = 5.0
# The plan panel parses two markdown documents (~440 + ~1,150 lines) and reads three more for its
# drift check. Measured at well under 0.1 s; no subprocess, no network. The budget is two orders of
# magnitude above the cost so a pathological document cannot wedge the window.
PLAN_BUDGET_S = 5.0
AGENTS_BUDGET_S = 4.0
REMOTE_CKPT_BUDGET_S = 7.0
# Measured on the real scratch/ (39 pid files, each an in-process OpenProcess + a few stats):
# 855 ms cold, well under this. No subprocess, no window, no signal ever sent.
CLAIMS_BUDGET_S = 4.0

RESULTS_N = 14              # newest verdicts to show
# An agent is WORKING if its transcript was appended to this recently. 15 minutes, not 4: a
# single Bash call, a long experiment smoke or a thorough investigation legitimately runs for
# tens of minutes without writing a line, and CLAUDE.md says outright that duration alone is
# not evidence of a stuck agent. Too short a threshold reports healthy agents as idle, which
# is the more damaging error here.
AGENT_ACTIVE_S = 900.0
AGENT_RECENT_S = 3600.0     # older than this is not shown at all
METRICS_MAX_BYTES = 1_000_000
REMOTE_CKPT_CACHE_S = 120.0

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

# Verdict strings that mean "this did not work". Shown exactly as loudly as the wins -- a
# dashboard that only surfaces good news is worse than none.
#
# NEGATION DOMINATES, and this is not a nicety. Verdict strings in this repo are built by
# concatenation, so `NO_READOUT_VARIANT_CLEARS_THE_FLOOR` and `NO_ASSET_CLEARS_THE_STRONGEST_
# FLOOR` both contain the positive word CLEARS while meaning the exact opposite. A naive
# substring match scores them as wins -- which is the precise failure this panel exists to
# prevent. So a negation word anywhere in the verdict makes it negative regardless of what
# else it contains.
_NEGATION_WORDS = frozenset({
    "NO", "NOT", "NONE", "NEVER", "WITHOUT", "FAIL", "FAILED", "FAILS", "CANNOT", "UNABLE",
})
# Short, ambiguous markers: matched as WHOLE TOKENS only (TIE would otherwise fire inside
# PROPERTIES, OOM inside a hash, PASS inside BYPASSED).
_NEGATIVE_WORDS = frozenset({
    "HURT", "HURTS", "NULL", "VOID", "OOM", "TIE", "TIED", "TIES", "KILLED", "CRASH",
    "CRASHED", "ERROR", "BELOW", "WORSE", "REGRESSION", "STOPPED", "ABORTED", "TIMEOUT",
})
# Long, distinctive markers: substring match is safe and catches compound verdicts.
_NEGATIVE_SUBSTRINGS = (
    "STILL_LOOSE", "NOT_EVALUABLE", "NOT_SCORABLE", "NOT_ESTABLISHED", "INCONCLUSIVE",
    "SATURATION", "REFUTED", "REFUTES", "DOES_NOT", "DID_NOT", "NO_EFFECT", "UNDERPOWERED",
    "INSTRUMENT_STILL",
)
# Deliberately NOT in the list above: domain words that merely sound bad. `DISAGREEMENT` in
# `KEY_DISAGREEMENT_IS_THE_COST` names a measured quantity, not a failure. Guessing a verdict
# from vocabulary is how a scanner ends up flagging honesty as overclaim -- 49 of 49 flags in
# three passes were false positives that way. Unclassified renders as FINDING, which is the
# honest answer.
_POSITIVE_WORDS = frozenset({"PASS", "PASSED", "CLEARS", "CLEARED", "BEATS", "SEPARATED"})
_POSITIVE_SUBSTRINGS = ("HARD_PASS", "SEPARATED_ABOVE", "CLEARS_THE")

NO_VERDICT = "(no verdict recorded)"


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _norm_dashes(s: str) -> str:
    """Normalise every dash-like character to '-'. Lets a spec written with a plain hyphen
    match a plan written with an en-dash, so the drift check does not fire on typography."""
    if not s:
        return ""
    for ch in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212"):
        s = s.replace(ch, "-")
    return s


def _bounded(fn, timeout_s: float, default):
    """Run fn() under a wall-clock cap that no subprocess/socket internal can defeat.
    Returns (value, completed). Delegates to inflight_monitor._bounded when available so
    there is one implementation of the guarantee, not two."""
    if _inflight is not None and hasattr(_inflight, "_bounded"):
        return _inflight._bounded(fn, timeout_s, default)
    import threading
    box = {"v": default, "done": False}

    def _run():
        try:
            box["v"] = fn()
        except Exception:
            box["v"] = default
        finally:
            box["done"] = True

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    th.join(timeout_s)
    return box["v"], box["done"]


def _panel(name: str, fn, budget_s: float) -> dict:
    """Run one panel collector under its own budget, and NEVER let it take the others down.

    Three outcomes, all of them explicit in the returned dict:
      ok       -> the collector's own dict, status untouched
      TIMEOUT  -> exceeded its budget and was abandoned
      ERROR    -> raised; the exception text is carried so it is visible in the window
    """
    t0 = time.time()
    box: dict = {}

    def _run():
        try:
            box["v"] = fn()
        except Exception as exc:
            box["err"] = f"{type(exc).__name__}: {exc}"
        return None

    _v, done = _bounded(_run, budget_s, None)
    took = round(time.time() - t0, 2)
    if not done:
        return {"status": "TIMEOUT", "panel": name, "took_s": took,
                "detail": f"{name} exceeded its {budget_s:.0f}s budget and was abandoned; "
                          f"showing UNKNOWN rather than blocking the window"}
    if "err" in box:
        return {"status": "ERROR", "panel": name, "took_s": took, "detail": box["err"]}
    out = box.get("v") or {}
    if not isinstance(out, dict):
        out = {"status": "ERROR", "detail": f"{name} returned {type(out).__name__}"}
    out.setdefault("status", "OK")
    out["panel"] = name
    out["took_s"] = took
    return out


def _fmt_dur(s) -> str:
    if not isinstance(s, (int, float)):
        return "?"
    s = int(s)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m{s % 60:02d}s"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m"


# ---------------------------------------------------------------------------
# PANEL 1 -- THE WALLS / COMPONENT HEALTH
# ---------------------------------------------------------------------------

def collect_walls() -> dict:
    """Per-component: what it is, whether it can be measured alone, its score, and THE FLOOR
    IT MUST BEAT. Never a score without its floor.

    The spec file is the structured transcription; `notes/PLAN.md` is the authority. Every row
    is re-checked against the authority on every refresh, so a plan edit that moves a number
    surfaces as CHECK-PLAN instead of the window quietly showing yesterday's figure."""
    if not COMPONENT_SPEC.is_file():
        return {"status": "MISSING",
                "detail": f"component spec not found: {COMPONENT_SPEC}. "
                          f"Panel 1 has no data. This is a MISSING panel, not a zero.",
                "headline": None, "rows": [], "watch": []}
    try:
        spec = json.loads(COMPONENT_SPEC.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "ERROR",
                "detail": f"component spec unreadable ({type(exc).__name__}: {exc})",
                "headline": None, "rows": [], "watch": []}

    # Load the authority documents once. Absent authority == cannot verify, NOT == verified.
    corpus_parts, missing_docs = [], []
    for p in (PLAN_DOC, STATUS_DOC, LONG_PLAN_DOC):
        try:
            corpus_parts.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            missing_docs.append(p.name)
    corpus = _norm_dashes("\n".join(corpus_parts))
    can_verify = bool(corpus_parts)

    def _check(row: dict) -> dict:
        strings = [s for s in (row.get("verify") or []) if s]
        if not can_verify:
            row["verify_status"] = "CANNOT_VERIFY"
            row["verify_missing"] = []
            return row
        if not strings:
            row["verify_status"] = "NO_VERIFY_STRINGS"
            row["verify_missing"] = []
            return row
        missing = [s for s in strings if _norm_dashes(s) not in corpus]
        row["verify_missing"] = missing
        row["verify_status"] = "CHECK_PLAN" if missing else "VERIFIED"
        return row

    headline = spec.get("headline")
    if isinstance(headline, dict):
        headline = _check(dict(headline))
    gov = spec.get("governing_floor")
    gov = _check(dict(gov)) if isinstance(gov, dict) else None
    rows = [_check(dict(r)) for r in (spec.get("components") or []) if isinstance(r, dict)]
    watch = [_check(dict(w)) for w in (spec.get("watch_items") or []) if isinstance(w, dict)]

    # Counts the owner actually wants: how many parts can we not even measure, and how many
    # are losing to a no-understanding baseline.
    no_instrument = [r["title"] for r in rows if (r.get("instrument") or "").upper() == "NO"]
    below = [r["title"] for r in rows if (r.get("standing") or "") == "BELOW_FLOOR"]
    missing_score = [r["title"] for r in rows if r.get("score") in (None, "")]
    missing_floor = [r["title"] for r in rows if r.get("floor") in (None, "")]
    drifted = [r["title"] for r in rows if r.get("verify_status") == "CHECK_PLAN"]

    return {
        "status": "OK",
        "as_of": spec.get("as_of"),
        "spec_path": str(COMPONENT_SPEC),
        "authority_docs": [str(PLAN_DOC), str(STATUS_DOC), str(LONG_PLAN_DOC)],
        "authority_missing": missing_docs,
        "can_verify": can_verify,
        "governing_floor": gov,
        "headline": headline,
        "rows": rows,
        "watch": watch,
        "n_no_instrument": len(no_instrument),
        "no_instrument": no_instrument,
        "n_below_floor": len(below),
        "below_floor": below,
        "missing_score": missing_score,
        "missing_floor": missing_floor,
        "drifted": drifted,
    }


# ---------------------------------------------------------------------------
# PANEL 2 -- OPEN QUESTIONS FOR THE OWNER
# ---------------------------------------------------------------------------

def collect_board() -> dict:
    """The questions waiting on the owner. Read-only here; the GUI's answer button is the
    only writer and it goes through board.resolve()."""
    if _board is None:
        return {"status": "ERROR", "detail": f"tools/board.py unavailable ({_BOARD_ERR})",
                "open": [], "answered_count": 0, "path": str(BOARD_DOC)}
    if not BOARD_DOC.is_file():
        return {"status": "MISSING",
                "detail": f"board file not found: {BOARD_DOC}",
                "open": [], "answered_count": 0, "path": str(BOARD_DOC),
                "writable": False}
    q, answered, _extra = _board.load(BOARD_DOC)
    open_rows = [r for r in q if not _board.is_settled(r)]
    return {
        "status": "OK",
        "path": str(BOARD_DOC),
        "open": open_rows,
        "n_open": len(open_rows),
        "answered_count": len(answered),
        # THE ANSWERED ROWS THEMSELVES (owner request 2026-08-20: "move the questions already
        # answered to an archive I can click into if I want"). Only the count was exposed before,
        # so the GUI could say HOW MANY were settled but could not show one. Newest first, because
        # an archive is read backwards. Capped at 200: the whole point is to keep settled rows OUT
        # of the working view, and an unbounded list would put the cost back on every refresh.
        "answered": list(reversed(answered))[:200],
        "writable": os.access(str(BOARD_DOC), os.W_OK),
        # Which DECISION / STANDING rows already carry an answer on the board. Read back off the
        # document, so an answer typed on a phone counts the same as one typed in the window.
        "recorded": answers_recorded_for(BOARD_DOC),
        "how_to_answer_in_file": (
            "Open notes/BOARD.md in any markdown editor, on any device. Type your decision "
            "into the ANSWER cell of the row. Save. That is the whole protocol -- you do not "
            "need to touch the status cell and you do not need to run anything."),
    }


def answer_question(item_id: str, answer: str,
                    board_path: Path | None = None) -> tuple[bool, str]:
    """Write one answer back to notes/BOARD.md. The ONLY write in this GUI.

    Deliberately delegated to board.resolve() rather than reimplemented: that function does an
    atomic temp-file-plus-os.replace rewrite, preserves hand-added sections verbatim, tolerates
    a raw `|` typed into a cell, and has a self-test covering exactly those cases. A
    half-built write-back that can corrupt the board is worse than no write-back, so there is
    no second code path here -- this function validates, delegates, and reports.
    """
    if _board is None:
        return False, f"tools/board.py unavailable ({_BOARD_ERR})"
    bp = Path(board_path) if board_path else BOARD_DOC
    if not bp.is_file():
        return False, f"board file not found: {bp}"
    text = (answer or "").strip()
    if not text:
        return False, "REFUSED: an empty answer would silently close the question."
    if not (item_id or "").strip():
        return False, "REFUSED: no question id."
    try:
        row = _board.resolve(item_id.strip(), text, bp, STATUS_DOC)
    except KeyError as exc:
        return False, f"REFUSED: {exc}"
    except Exception as exc:
        return False, f"WRITE FAILED ({type(exc).__name__}: {exc}) -- board NOT changed."
    return True, f"{row.get('id')} answered and moved to ANSWERED at {row.get('resolved')}."


def file_board_note(text: str, context: str = "",
                    board_path: Path | None = None) -> tuple[bool, str, str]:
    """Record free text on the board as its own already-answered row. Returns (ok, msg, id).

    WHY THIS EXISTS (2026-08-16). The GUI could only write into an EXISTING open question. On the
    night the answer panel was reported broken the board had zero open questions, so the owner's
    typed answer had no reachable destination and was lost. A text box the owner can type into must
    always have somewhere to put the text.

    Same discipline as answer_question above: NO second write path. It composes `board.ask()` and
    `board.resolve()`, which between them do the atomic temp-file rewrite, preserve hand-added
    sections verbatim, and round-trip a raw `|` typed into the text -- all covered by
    `board.py self-test`. This function validates, delegates, and reports.
    """
    if _board is None:
        return False, f"tools/board.py unavailable ({_BOARD_ERR})", ""
    bp = Path(board_path) if board_path else BOARD_DOC
    body = (text or "").strip()
    if not body:
        return False, "REFUSED: an empty note would record nothing.", ""
    where = (context or "").strip() or "no row selected"
    prompt = (f"NOTE TYPED INTO THE STATUS WINDOW while looking at {where}. Recorded verbatim "
              f"because it did not belong to any open question.")
    try:
        row = _board.ask(prompt, why="nothing -- this is a record, not a question",
                         rec="(no recommendation: the owner wrote this unprompted)",
                         board_path=bp, status_path=STATUS_DOC)
        done = _board.resolve(row["id"], body, bp, STATUS_DOC)
    except Exception as exc:
        return False, f"WRITE FAILED ({type(exc).__name__}: {exc}) -- board NOT changed.", ""
    return (True,
            f"{done.get('id')} recorded under ANSWERED at {done.get('resolved')}.",
            str(done.get("id") or ""))


# ---------------------------------------------------------------------------
# ANSWERING A ROW THAT IS NOT A BOARD QUESTION (2026-08-16, owner report)
# ---------------------------------------------------------------------------
#
# THE DEFECT THIS FIXES IS A DESIGN ERROR, NOT A BUG. The previous fix made Save honest -- it greys
# out on a row it cannot write -- and `notes/BOARD.md` then had ZERO open questions, so every one of
# the eleven live rows was a DECISION (D1-D7, notes/PLAN.md section 9) or a STANDING item
# (OP1-OP4, transcribed from the status documents). The panel was therefore CORRECTLY telling the
# owner that nothing at all was answerable, which is useless to them: the decisions are exactly what
# they have been trying to answer, and one attempt (D1) was lost entirely.
#
# WHY THE ANSWER GOES TO THE BOARD AND NOT TO THE SOURCE DOCUMENT. `notes/PLAN.md` and
# `notes/STATUS.md` are both PARSER-COUPLED -- `tools/status_plan.py` parses section 9 of the first;
# `tools/session_start_hook.py` greps the second for the literals `AS OF:` and `## WHAT IS RUNNING`,
# and a past rewording of exactly those two silently degraded every compaction recovery for days
# (CLAUDE.md, "A doc parsed by code is coupled to it"). Writing owner prose into either document
# would put a human sentence inside a machine-read region on the owner's keystrokes. So every answer
# lands in `notes/BOARD.md` instead: ONE write path, ONE parser, ONE file the owner can read on a
# phone, and it already round-trips a hand edit under its own self-test.
#
# THE ROW CARRIES THE DECISION'S TEXT INLINE, never a bare identifier. The owner has said so twice,
# most recently: "In general, you should include context in these questions. I do not remember what
# Q7 was." A row that says only "D3" is a row that is unreadable a day later.

_KIND_PLAIN = {
    "QUESTION": "a question on the board",
    "DECISION": "a standing decision from notes/PLAN.md section 9",
    "STANDING": "a standing operator decision recorded in the status documents",
}


def _context_block(kind: str, row_id: str, row: dict) -> tuple[str, str]:
    """(question_text, recommendation) for a board row that RECORDS an answer to `row_id`.

    Everything the owner would need to understand the decision a month later is written into the
    question cell itself, because that cell is what they will re-read. Fields that the source
    document does not state are OMITTED rather than filled with a placeholder."""
    row = row if isinstance(row, dict) else {}
    what = _KIND_PLAIN.get(kind, "an item on the WAITING ON YOU panel")
    bits = [f"ANSWER TO {row_id} -- {what}."]
    title = str(row.get("title") or "").strip()
    question = str(row.get("question") or "").strip()
    if title and title != question:
        bits.append(f"IT IS ABOUT: {title}")
    if question:
        bits.append(f"THE DECISION, IN FULL: {question}")
    why = str(row.get("why") or row.get("blocked") or "").strip()
    if why:
        bits.append(f"WHAT IS BLOCKED ON IT: {why}")
    default = str(row.get("default") or row.get("standing") or "").strip()
    if default:
        bits.append(f"WHAT WOULD HAVE HAPPENED IF NOBODY ANSWERED: {default}")
    src = str(row.get("source") or "").strip()
    if src:
        bits.append(f"RECORDED IN: {src}")
    rec = str(row.get("rec") or row.get("default") or "").strip()
    return " ".join(bits), (rec or "(the source document states no recommendation)")


def record_answer(kind: str, row_id: str, row: dict, answer: str,
                  board_path: Path | None = None) -> tuple[bool, str, str]:
    """Record the owner's answer to ANY row on the WAITING ON YOU panel. (ok, message, board_id).

    QUESTION rows keep the pre-existing path exactly: `board.resolve()` writes into that question's
    own ANSWER cell. Every OTHER kind becomes a NEW board row that names the decision and carries
    its text inline, filed already-answered through `board.ask()` + `board.resolve()`.

    NO SECOND WRITE PATH, for the same reason as `answer_question` and `file_board_note` above:
    those two board calls do the atomic temp-file-plus-os.replace rewrite, preserve hand-added
    sections verbatim, and round-trip a raw `|` typed into a cell, all under `board.py self-test`.
    This function validates, delegates, and reports."""
    text = (answer or "").strip()
    rid = (row_id or "").strip()
    if not text:
        return False, "REFUSED: an empty answer would record nothing.", ""
    if not rid:
        return False, "REFUSED: no row is selected, so there is nothing to record an answer to.", ""
    if _board is None:
        return False, f"tools/board.py unavailable ({_BOARD_ERR})", ""
    bp = Path(board_path) if board_path else BOARD_DOC

    if kind == "QUESTION":
        ok, msg = answer_question(rid, text, bp)
        return ok, msg, (rid if ok else "")

    question, rec = _context_block(kind, rid, row)
    try:
        new = _board.ask(question, why=f"{rid} was waiting on you and now it is not.",
                         rec=rec, board_path=bp, status_path=STATUS_DOC)
        done = _board.resolve(new["id"], text, bp, STATUS_DOC)
    except Exception as exc:
        return False, f"WRITE FAILED ({type(exc).__name__}: {exc}) -- board NOT changed.", ""
    return (True,
            f"recorded as {done.get('id')} on the board at {done.get('resolved')}, naming {rid} "
            f"and carrying its full text.",
            str(done.get("id") or ""))


def answers_recorded_for(board_path: Path | None = None) -> dict:
    """{row_id: board_id} for every DECISION/STANDING row already answered on the board.

    Read back out of the DOCUMENT rather than remembered in the window, so an answer typed on a
    phone into notes/BOARD.md counts exactly the same as one typed here, and so the panel can show
    ANSWERED beside a decision instead of asking for it again forever."""
    out: dict = {}
    if _board is None:
        return out
    bp = Path(board_path) if board_path else BOARD_DOC
    try:
        _q, answered, _e = _board.load(bp)
    except Exception:
        return out
    for r in answered:
        m = re.match(r"ANSWER TO ([A-Za-z]{1,10}\d{1,4})\b", str(r.get("question") or "").strip())
        if m:
            out.setdefault(m.group(1).upper(), {"board_id": r.get("id"),
                                                "answer": r.get("answer"),
                                                "resolved": r.get("resolved")})
    return out


# ---------------------------------------------------------------------------
# PANEL 3 -- WHAT IS RUNNING RIGHT NOW
# ---------------------------------------------------------------------------

def _agent_subdirs(limit: int = 40) -> list[Path]:
    """Every `<project>/<session>/subagents` directory under the Claude projects root."""
    out: list[Path] = []
    try:
        projects = [e for e in os.scandir(AGENT_ROOT) if e.is_dir()]
    except OSError:
        return out
    for proj in projects:
        try:
            sessions = [e for e in os.scandir(proj.path) if e.is_dir()]
        except OSError:
            continue
        for sess in sessions:
            sd = Path(sess.path) / "subagents"
            if sd.is_dir():
                out.append(sd)
                if len(out) >= limit:
                    return out
    return out


def collect_agents() -> dict:
    """Live agents, from the transcript each agent is actually writing.

    Liveness is the TRANSCRIPT MTIME, not a registry and not a self-report: an agent that is
    working is appending to its own `agent-*.jsonl` right now. The sibling `.meta.json` (a few
    hundred bytes) carries the name, the description, the agent type and the model, so this
    costs one scandir plus a handful of tiny reads -- the multi-megabyte transcripts are
    never opened.

    Same discipline as the remote-liveness rule in CLAUDE.md: observe the artifact the process
    produces, not a proxy that reports on it.
    """
    dirs = _agent_subdirs()
    if not dirs:
        return {"status": "MISSING",
                "detail": f"no agent transcript directory under {AGENT_ROOT}; "
                          f"cannot tell which agents are live",
                "agents": [], "n_active": 0}
    now = time.time()
    found: list[dict] = []
    for sd in dirs:
        try:
            entries = list(os.scandir(sd))
        except OSError:
            continue
        metas = {}
        jsonls = {}
        for e in entries:
            if e.name.endswith(".meta.json"):
                metas[e.name[:-len(".meta.json")]] = e
            elif e.name.endswith(".jsonl"):
                jsonls[e.name[:-len(".jsonl")]] = e
        for key, je in jsonls.items():
            try:
                st = je.stat()
            except OSError:
                continue
            age = now - st.st_mtime
            if age > AGENT_RECENT_S:
                continue
            meta = {}
            me = metas.get(key)
            if me is not None:
                try:
                    meta = json.loads(Path(me.path).read_text(encoding="utf-8"))
                except Exception:
                    meta = {}
            if not isinstance(meta, dict):
                meta = {}
            started = getattr(st, "st_ctime", None)
            found.append({
                "id": key,
                "name": meta.get("name") or key[:18],
                "description": meta.get("description") or "(no description recorded)",
                "agent_type": meta.get("agentType") or "?",
                "model": meta.get("model") or "?",
                "stopped_by_user": bool(meta.get("stoppedByUser")),
                "idle_s": round(age, 1),
                "elapsed_s": round(now - started, 1) if started else None,
                "state": "WORKING" if age <= AGENT_ACTIVE_S else "QUIET",
                "transcript_kb": st.st_size // 1024,
            })
    found.sort(key=lambda a: a["idle_s"])
    active = [a for a in found if a["state"] == "WORKING" and not a["stopped_by_user"]]
    return {
        "status": "OK",
        "agents": found,
        "n_active": len(active),
        "active_threshold_s": AGENT_ACTIVE_S,
        "source": str(AGENT_ROOT),
    }


_ckpt_cache: dict = {"ts": 0.0, "value": None}


def _remote_run_in_flight(state: dict) -> bool:
    """Is anything actually running remotely? Skips the SSH probe when nothing is, which is
    both cheaper and honest -- 'no remote run' is a different answer from 'unknown'."""
    for rid, r in (state.get("runners") or {}).items():
        if (r or {}).get("status") == "running":
            return True
    for qname in ("overnight_queue", "remote_cpu_queue"):
        if (state.get("queues", {}).get(qname, {}) or {}).get("running"):
            return True
    g = state.get("gpu") or {}
    return bool(g.get("queue_status") == "running" or g.get("experiment_on_card"))


def probe_remote_checkpoint(alias: str | None = None) -> dict:
    """The REMOTE-LIVENESS TRUTH SIGNAL: is the in-progress checkpoint file advancing?

    CLAUDE.md is explicit that the training heartbeat is NOT this signal -- its cadence is
    coarse (roughly every 20 minutes), it stops between beats and when a run finishes, and it
    false-alarmed as a stall three times on 2026-07-28. The signal that is trustworthy is the
    `ckpt_*_inprogress.pt` mtime advancing, together with GPU utilisation (which
    `build_state()` already supplies from its own three-tier source).

    Hardened exactly like `inflight_monitor.probe_gpu_via_ssh`: BatchMode so it can never
    prompt, ConnectTimeout for a connect stall, ServerAlive for a post-connect read stall,
    ControlMaster=no/ControlPath=none so no persistent master survives to defeat the timeout,
    stdin from DEVNULL, a subprocess timeout, CREATE_NO_WINDOW, and the caller ALSO wraps it
    in a wall-clock cap. Never raises: every failure returns UNKNOWN with a reason.

    HONESTY NOTE, because it matters for how this reading should be treated: this probe has
    NOT been exercised against a live remote training run (no remote run was in flight when it
    was written, and the runners were idle). Its failure path is tested; its success path is
    not. Treat an UNKNOWN here as "we could not tell", never as "the run is dead".
    """
    alias = alias or getattr(_inflight, "SSH_ALIAS", "home")
    remote_cmd = (
        "powershell -NoProfile -NonInteractive -Command "
        "\"$f=Get-ChildItem -Path C:\\dev\\hd-instrument\\data -Recurse -Filter "
        "'*inprogress*.pt' -ErrorAction SilentlyContinue | "
        "Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1; "
        "if($f){ Write-Output ($f.Name + '|' + "
        "$f.LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')) } else { Write-Output 'NONE' }\""
    )
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
        "-o", "ServerAliveInterval=2", "-o", "ServerAliveCountMax=2",
        "-o", "ControlMaster=no", "-o", "ControlPath=none",
        alias, remote_cmd,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5.0,
                              creationflags=_NO_WINDOW, stdin=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"state": "UNKNOWN", "reason": f"ssh probe failed ({type(exc).__name__})",
                "alias": alias}
    if proc.returncode != 0:
        return {"state": "UNKNOWN",
                "reason": f"ssh exit {proc.returncode}: "
                          f"{(proc.stderr or '').strip()[:120] or 'no stderr'}",
                "alias": alias}
    line = next((l.strip() for l in (proc.stdout or "").splitlines() if l.strip()), "")
    if not line or line == "NONE":
        return {"state": "NO_CHECKPOINT",
                "reason": "no in-progress checkpoint file found on the remote box",
                "alias": alias}
    name, _, ts = line.partition("|")
    age = None
    if _inflight is not None:
        age = _inflight._naive_or_utc_age_s(ts)
    return {"state": "SEEN", "checkpoint": name, "mtime_utc": ts,
            "age_s": round(age, 1) if age is not None else None, "alias": alias,
            "note": "the checkpoint mtime is the liveness signal; the training heartbeat is not"}


def collect_running() -> dict:
    """Agents, detached experiments, queues, runners, GPU, and the remote truth signal."""
    if _inflight is None:
        base = {"alerts": [{"level": "CRITICAL", "code": "MONITOR_UNAVAILABLE",
                            "msg": f"tools/inflight_monitor.py could not be imported "
                                   f"({_INFLIGHT_ERR})"}],
                "gpu": {}, "queues": {}, "runners": {}, "local_experiments": []}
        st_status = "ERROR"
    else:
        st, done = _bounded(_inflight.build_state, RUNNING_BUDGET_S - 2.0, None)
        if not done or not isinstance(st, dict):
            base = {"alerts": [{"level": "WARN", "code": "STATE_TIMEOUT",
                                "msg": "build_state() exceeded its budget; "
                                       "running-state is UNKNOWN this tick"}],
                    "gpu": {}, "queues": {}, "runners": {}, "local_experiments": []}
            st_status = "TIMEOUT"
        else:
            base = st
            st_status = "OK"

    agents = _panel("agents", collect_agents, AGENTS_BUDGET_S)

    # Remote checkpoint: only probed when something is actually running remotely, and only
    # every REMOTE_CKPT_CACHE_S so a 7-second refresh cannot turn into an SSH storm.
    if st_status != "OK":
        ckpt = {"state": "UNKNOWN", "reason": "running-state unavailable, so we do not know "
                                              "whether a remote run exists"}
    elif not _remote_run_in_flight(base):
        ckpt = {"state": "NO_REMOTE_RUN", "reason": "no remote runner or queue entry is "
                                                    "marked running; nothing to check"}
    else:
        now = time.time()
        if _ckpt_cache["value"] is not None and (now - _ckpt_cache["ts"]) < REMOTE_CKPT_CACHE_S:
            ckpt = dict(_ckpt_cache["value"])
            ckpt["cached_s"] = round(now - _ckpt_cache["ts"], 1)
        else:
            ckpt, done = _bounded(probe_remote_checkpoint, REMOTE_CKPT_BUDGET_S, None)
            if not done or not isinstance(ckpt, dict):
                ckpt = {"state": "UNKNOWN",
                        "reason": "checkpoint probe exceeded its budget and was abandoned"}
            _ckpt_cache["ts"] = now
            _ckpt_cache["value"] = ckpt

    g = base.get("gpu") or {}
    util = g.get("util_ema") if g.get("util_ema") is not None else g.get("util_pct")
    local = base.get("local_experiments") or []

    # WHAT CLAIMS TO BE RUNNING (2026-08-16). The scan above can only see processes that EXIST, so a
    # run that died simply vanished from the panel while its scratch/<name>.pid file stayed on disk
    # and kept being quoted as live -- 37 of 39 such files pointed at nothing on the night this was
    # added, three of them cited as live in agent briefs for hours. A stale RUNNING is worse than no
    # panel because it is read as evidence, so the claim and the OS's answer are now shown together.
    # The live pid set is what separates "our run is up" from a recycled process number.
    live_pids = set()
    for e in local:
        if isinstance(e, dict):
            for k in ("pid", "shim_pid"):
                if isinstance(e.get(k), int):
                    live_pids.add(e[k])
    if _pidclaims is None:
        claims = {"status": "ERROR", "claims": [], "n_claims": 0, "n_dead": 0,
                  "detail": f"tools/status_pidclaims.py unavailable ({_PIDCLAIMS_ERR})"}
    else:
        claims = _panel("pid claims",
                        lambda: _pidclaims.scan_claims(live_pids=live_pids), CLAIMS_BUDGET_S)

    return {
        "status": "OK" if st_status == "OK" else st_status,
        "state_status": st_status,
        "alerts": base.get("alerts") or [],
        "gpu": g,
        "gpu_util": util,
        "queues": base.get("queues") or {},
        "runners": base.get("runners") or {},
        "local_experiments": local,
        "claims": claims,
        "cache_age_s": base.get("cache_age_s"),
        "agents": agents,
        "remote_checkpoint": ckpt,
    }


# ---------------------------------------------------------------------------
# PANEL 4 -- LATEST RESULTS
# ---------------------------------------------------------------------------

def _read_metrics(path: Path) -> dict:
    """Pull the verdict fields out of a metrics.json without ever loading a huge one whole."""
    try:
        size = path.stat().st_size
    except OSError:
        return {}
    if size <= METRICS_MAX_BYTES:
        try:
            d = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return d if isinstance(d, dict) else {}
        except (OSError, json.JSONDecodeError, ValueError):
            return {}
    # Oversized: take a bounded prefix and lift just the fields we render.
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:200_000]
    except OSError:
        return {}
    out: dict = {"_truncated": True}
    for key in ("verdict", "verdict_msg", "summary", "run_mode"):
        m = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)"' % key, head)
        if m:
            try:
                out[key] = json.loads('"' + m.group(1) + '"')
            except ValueError:
                out[key] = m.group(1)
    m = re.search(r'"elapsed_s"\s*:\s*([0-9.eE+-]+)', head)
    if m:
        try:
            out["elapsed_s"] = float(m.group(1))
        except ValueError:
            pass
    return out


def _grade(verdict: str, msg: str, metrics: dict) -> dict:
    """Classify a verdict, and -- the point of this panel -- say whether it came with a FLOOR
    and whether the margin was CI-SEPARATED. A result with no floor beside it cannot be
    graded, and saying so is more useful than showing the number alone."""
    v = (verdict or "").upper()
    blob = f"{v} {msg or ''}"
    blob_u = blob.upper()
    if not verdict or verdict == NO_VERDICT:
        # A run that wrote metrics without a verdict (still in flight, or it crashed before
        # adjudicating). That is its own state -- calling it a FINDING would imply something
        # was concluded, and the negation rule below would otherwise read the literal word
        # "no" in the placeholder text as a negative result.
        return {"negative": False, "positive": False, "label": "NO VERDICT YET",
                "floor_named": False, "ci_mentioned": False, "separated": "UNKNOWN"}
    tokens = set(t for t in re.split(r"[^A-Z0-9]+", v) if t)
    negated = bool(tokens & _NEGATION_WORDS)
    negative = (negated
                or bool(tokens & _NEGATIVE_WORDS)
                or any(sub in v for sub in _NEGATIVE_SUBSTRINGS))
    positive = (not negative
                and (bool(tokens & _POSITIVE_WORDS)
                     or any(sub in v for sub in _POSITIVE_SUBSTRINGS)))
    # Anything we cannot confidently call either way is a FINDING, never a win. The default
    # direction matters: an unclassified verdict quietly rendered as good news is the bias
    # this panel is supposed to remove.
    label = "NEGATIVE" if negative else ("WIN" if positive else "FINDING")
    floor_named = bool(re.search(r"floor|baseline|scramble|orthograph|spelling|trigram|"
                                 r"frequency|chance|STRINGCTRL|control arm",
                                 blob, re.IGNORECASE))
    # Structured evidence beats a text match when the cell recorded it.
    for k in metrics:
        if isinstance(k, str) and "floor" in k.lower():
            floor_named = True
            break
    ci_mentioned = bool(re.search(r"\bCI\b|confidence interval|\[\s*-?\d", blob))
    separated = "UNKNOWN"
    if re.search(r"CI[ S]*(EXCL|separated|does not (?:include|cross)|excludes)\s*(0|zero)?",
                 blob, re.IGNORECASE) or "CI-SEPARATED" in blob_u or "CI SEPARATED" in blob_u:
        separated = "YES"
    if re.search(r"CI (includes|covers|crosses)\s*(0|zero)|crosses zero|not separable|"
                 r"NOT SEPARAT|overlap", blob, re.IGNORECASE):
        separated = "NO"
    if separated == "UNKNOWN" and re.search(r"CI \[\s*-", blob):
        # An interval printed with a negative lower bound alongside a positive claim.
        separated = "NO" if re.search(r"CI \[\s*-[\d.]+\s*,\s*[\d.]+\s*\]", blob) else separated
    return {
        "negative": negative,
        "positive": positive,
        "label": label,
        "floor_named": floor_named,
        "ci_mentioned": ci_mentioned,
        "separated": separated,
    }


def _newest_metrics(entries: list, n: int,
                    time_cap_s: float = 3.0) -> tuple[list[tuple[float, str, Path]], dict]:
    """The n newest `metrics.json` files, WITHOUT statting all ~8,000 of them.

    THE DEFECT THIS FIXES, measured. The previous version called `stat()` on
    `<dir>/metrics.json` for every one of 8,015 directories. Warm that costs 0.87 s; with the
    live runs writing it was measured at **18.08 s against an 8 s budget**, so the panel
    intermittently degraded to TIMEOUT and the owner saw no results at all. The panel was
    behaving correctly -- it degraded rather than blocking -- but the cost was wrong.

    THE MECHANISM. `os.scandir` on Windows returns the directory's own timestamps inside the
    DirEntry, so `entry.stat()` costs no syscall at all: 8,015 of them measured at **0.006 s**
    against 0.866 s for the same number of separate file stats, a 140x difference. So we sort
    directories by the free timestamp and open `metrics.json` only in the newest few.

    WHY THAT IS CORRECT AND NOT JUST FAST. `metrics.json` is created or replaced inside its
    directory (CLAUDE.md mandates the atomic `os.replace` pattern), and creating or replacing an
    entry updates the parent directory's own mtime. So for every directory
    `dir_mtime >= metrics_mtime`. Probing in descending `dir_mtime` order, once we hold n
    candidates whose n-th best `metrics_mtime` is at or above the `dir_mtime` of the next
    unprobed directory, no unprobed directory can beat it. That is a proof, and it is recorded in
    the return value as `complete: True`.

    THE ONE ASSUMPTION, DISCLOSED RATHER THAN BURIED: a `metrics.json` REWRITTEN IN PLACE (opened
    and written without a create or a rename) does not touch its parent directory's mtime, and
    such a file could be missed. The repo's own convention forbids that write pattern. When the
    proof cannot be completed inside `time_cap_s` the result is returned with `complete: False`
    and the caller says so on screen rather than implying it scanned everything.
    """
    t0 = time.time()
    dirs: list[tuple[float, str, str]] = []
    for e in entries:
        try:
            dirs.append((e.stat().st_mtime, e.name, e.path))
        except OSError:
            continue
    dirs.sort(key=lambda t: t[0], reverse=True)

    found: list[tuple[float, str, Path]] = []
    want = max(1, n)
    i, probed, complete = 0, 0, False
    step = max(want * 4, 64)
    while i < len(dirs):
        stop = min(i + step, len(dirs))
        for _dm, name, path in dirs[i:stop]:
            p = Path(path) / "metrics.json"
            probed += 1
            try:
                found.append((p.stat().st_mtime, name, p))
            except OSError:
                continue
        i = stop
        found.sort(key=lambda t: t[0], reverse=True)
        if i >= len(dirs):
            complete = True
            break
        if len(found) >= want and found[want - 1][0] >= dirs[i][0]:
            complete = True
            break
        if (time.time() - t0) > time_cap_s:
            break
        step = min(step * 4, 4096)
    return found[:want], {
        "n_dirs": len(dirs),
        "n_metrics_opened": probed,
        "complete": complete,
        "took_s": round(time.time() - t0, 3),
        "method": ("newest-first by the directory timestamp the scandir already carries; "
                   "metrics.json is opened only where it can still be one of the newest"),
    }


def collect_results(n: int = RESULTS_N) -> dict:
    """The newest verdicts, newest first, each with its floor and whether it was separated.

    Cost control lives in `_newest_metrics` above and is a measured fix, not a guess: the naive
    version statted 8,015 files and blew its budget under concurrent writes.
    """
    if not DATA_DIR.is_dir():
        return {"status": "MISSING", "detail": f"data directory not found: {DATA_DIR}",
                "rows": []}
    try:
        entries = [e for e in os.scandir(DATA_DIR) if e.is_dir()]
    except OSError as exc:
        return {"status": "ERROR", "detail": f"cannot scan {DATA_DIR}: {exc}", "rows": []}
    stamped, scan_info = _newest_metrics(entries, max(1, n))
    if not stamped:
        return {"status": "MISSING",
                "detail": f"no metrics.json under {DATA_DIR}; no results to show",
                "rows": [], "n_scanned": len(entries), "scan": scan_info}

    rows: list[dict] = []
    for mtime, name, p in stamped:
        m = _read_metrics(p)
        verdict = str(m.get("verdict") or "").strip() or NO_VERDICT
        msg = str(m.get("verdict_msg") or m.get("summary") or "").strip()
        grade = _grade(verdict, msg, m)
        rows.append({
            "name": name,
            "verdict": verdict,
            "verdict_msg": msg,
            "when": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
            "age_s": round(time.time() - mtime, 1),
            "elapsed_s": m.get("elapsed_s"),
            "run_mode": m.get("run_mode"),
            "is_smoke": name.endswith("_smoke") or str(m.get("run_mode", "")).lower() == "smoke",
            "path": str(p),
            **grade,
        })
    return {
        "status": "OK",
        "rows": rows,
        "n_scanned": len(entries),
        "n_with_metrics": len(stamped),
        "scan": scan_info,
        "n_negative": sum(1 for r in rows if r["negative"]),
        "n_no_floor": sum(1 for r in rows if not r["floor_named"]),
    }


# ---------------------------------------------------------------------------
# PANEL 5 -- LOOP STATE
# ---------------------------------------------------------------------------

def _continuation_counts() -> list[dict]:
    """Per-session continuation counters the Stop hook maintains."""
    out: list[dict] = []
    if not HOOK_STATE.is_dir():
        return out
    try:
        entries = [e for e in os.scandir(HOOK_STATE)
                   if e.is_file() and e.name.startswith("stop_continuations")]
    except OSError:
        return out
    for e in entries:
        try:
            st = e.stat()
            raw = Path(e.path).read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        try:
            count = int(raw or 0)
        except ValueError:
            count = None
        session = e.name.replace("stop_continuations_", "").replace("stop_continuations", "")
        out.append({"session": session.lstrip("_") or "(unnamed)", "count": count,
                    "age_s": round(time.time() - st.st_mtime, 1)})
    out.sort(key=lambda r: r["age_s"])
    return out


def collect_loop() -> dict:
    """Is the overnight loop armed, what is its cap, how many continuations has it used, and
    -- prominently -- how to stop it."""
    disarm_cmd = "python tools/autoloop.py disarm"
    if _autoloop is None:
        return {"status": "ERROR", "detail": f"tools/autoloop.py unavailable ({_AUTOLOOP_ERR})",
                "armed": None, "disarm_cmd": disarm_cmd}
    state_path = _autoloop.DEFAULT_STATE
    raw = _autoloop.load_state(state_path)
    armed = _autoloop.is_armed(state_path)
    cap = _autoloop.resolve_cap(state_path)
    counts = _continuation_counts()
    recent = [c for c in counts if c["age_s"] <= 86400]
    return {
        "status": "OK" if state_path.is_file() else "MISSING",
        "detail": "" if state_path.is_file()
                  else f"{state_path} does not exist -- which reads as DISARMED (fail-safe)",
        "armed": armed,
        "cap": cap,
        "cap_label": _autoloop.cap_label(cap),
        "armed_at": raw.get("armed_at"),
        "armed_by": raw.get("armed_by"),
        "state_path": str(state_path),
        "continuations": counts[:8],
        "continuations_recent_total": sum(c["count"] or 0 for c in recent),
        "disarm_cmd": disarm_cmd,
        "disarm_alt": (f"or open {state_path} in any editor, set \"armed\": false, and save. "
                       f"Anything that is not exactly true reads as DISARMED."),
    }


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def _organs_missing(what: str) -> dict:
    return {"status": "MISSING",
            "detail": f"tools/status_organs.py could not be imported ({_ORGANS_ERR}), so the "
                      f"{what} panel has no data. Showing MISSING rather than a stale value."}


def _score_key(row: dict) -> str:
    return str(row.get("id") or row.get("title") or "").strip().lower()


def merge_scores(walls: dict, progress: dict) -> dict:
    """ONE table of every part's score beside the floor it has to beat -- and what it was before.

    WHY THIS MERGE EXISTS. The window had two tabs answering nearly the same question. THE WALLS
    held `score + floor + can we measure it alone` per component; PROGRESS MADE held
    `before + now + floor` per component. Five of the seven parts appeared in BOTH, so the owner had
    to hold two tabs in their head and diff them by eye to answer "how are we doing" -- which is the
    hunting the owner asked to be rid of.

    WHAT IS PRESERVED, because both are load-bearing and neither is negotiable:
      * A SCORE IS NEVER SHOWN WITHOUT ITS FLOOR. Every cell carries its floor or an explicit
        non-answer, and the merged row keeps `floor_name` from whichever source supplied the score.
      * RETRACTIONS STAY FIRST-CLASS ROWS in the same red as a loss, counted in the tab title.

    AND WHERE THE TWO SOURCES DISAGREE, THE PANEL SAYS SO RATHER THAN PICKING ONE. They do disagree
    today, and it is not a bug in either: THE WALLS records retrieval at 55.65% against a spelling
    floor of 54.55% (measured with the exact key); the ledger records the SAME component at 0.3758
    against 0.5235 (measured under a partial cue, which correction C30 established is the real
    operating condition). Silently preferring one would hide the single most important retrieval
    finding of 2026-08-16. So both are rendered and the disagreement is counted.
    """
    if not isinstance(walls, dict):
        walls = {}
    if not isinstance(progress, dict):
        progress = {}
    w_ok = walls.get("status") == "OK"
    p_ok = progress.get("status") == "OK"
    if not w_ok and not p_ok:
        return {"status": "MISSING",
                "detail": f"neither source is readable -- scores: {walls.get('status')} "
                          f"({walls.get('detail', '')}); what-moved: {progress.get('status')} "
                          f"({progress.get('detail', '')})",
                "rows": [], "retractions": [], "governing_floor": None}

    w_rows: list[dict] = []
    if w_ok:
        h = walls.get("headline")
        if isinstance(h, dict):
            w_rows.append(dict(h, _headline=True))
        w_rows += [dict(r) for r in (walls.get("rows") or []) if isinstance(r, dict)]
    p_rows = [dict(r) for r in (progress.get("components") or [])
              if isinstance(r, dict)] if p_ok else []
    p_by_key = {_score_key(r): r for r in p_rows}

    merged: list[dict] = []
    used: set[str] = set()
    for w in w_rows:
        key = _score_key(w)
        p = p_by_key.get(key)
        if p is not None:
            used.add(key)
        merged.append(_merge_one(w, p))
    for p in p_rows:
        if _score_key(p) in used:
            continue
        merged.append(_merge_one(None, p))

    gov = walls.get("governing_floor") if w_ok else None
    if not isinstance(gov, dict):
        gov = progress.get("governing_floor") if p_ok else None
    return {
        "status": "OK",
        "as_of": walls.get("as_of") or progress.get("as_of"),
        "governing_floor": gov if isinstance(gov, dict) else None,
        "rows": merged,
        "retractions": [dict(r) for r in (progress.get("retractions") or [])
                        if isinstance(r, dict)] if p_ok else [],
        "n_retracted": progress.get("n_retracted") if p_ok else None,
        "n_disagreements": sum(1 for r in merged if r.get("disagreement")),
        "n_no_instrument": walls.get("n_no_instrument") if w_ok else None,
        "sources_ok": {"scores": w_ok, "what_moved": p_ok},
        "source_detail": {"scores": walls.get("detail"), "what_moved": progress.get("detail")},
    }


def _merge_one(w: dict | None, p: dict | None) -> dict:
    """One merged row. Fields come from whichever source has them; nothing is invented."""
    w = w or {}
    p = p or {}
    src = [s for s, present in (("scores", bool(w)), ("what moved", bool(p))) if present]
    # NOW: the ledger's dated `now` when it has one, else the walls score. Both are carried.
    p_now = p.get("now") if isinstance(p.get("now"), dict) else {}
    now = {"score": p_now.get("score") or w.get("score"),
           "score_detail": p_now.get("score_detail") or w.get("score_detail"),
           "floor": p_now.get("floor") if p_now else w.get("floor"),
           "floor_name": (p_now.get("floor_name") if p_now else None) or w.get("floor_name"),
           "floor_detail": (p_now.get("floor_detail") if p_now else None) or w.get("floor_detail"),
           "floor_superseded_by": w.get("floor_superseded_by"),
           "when": p_now.get("when")}
    disagreement = None
    if p_now.get("score") and w.get("score") and p_now["score"] != w["score"]:
        disagreement = (
            f"the two sources report different current scores for this part: the component table "
            f"says {w.get('score')} against {w.get('floor')} ({w.get('floor_name')}), the "
            f"what-moved ledger says {p_now.get('score')} against {p_now.get('floor')} "
            f"({p_now.get('floor_name')}). They are not both wrong -- they are measured under "
            f"different conditions. Read both, and read the detail below before quoting either.")
    return {
        "id": w.get("id") or p.get("id"),
        "n": w.get("n"),
        "headline": bool(w.get("_headline")),
        "title": w.get("title") or p.get("title"),
        "what_it_does": w.get("what_it_does") or p.get("plain"),
        "plain": p.get("plain") or w.get("plain_verdict"),
        "instrument": w.get("instrument"),
        "instrument_note": w.get("instrument_note"),
        "instrument_evidence": w.get("instrument_evidence"),
        "before": p.get("before") if isinstance(p.get("before"), dict) else None,
        "now": now,
        "direction": p.get("direction"),
        "what_moved": p.get("what_moved"),
        "standing": w.get("standing"),
        "separated": w.get("separated"),
        "plain_verdict": w.get("plain_verdict"),
        "evidence": w.get("evidence") or p.get("evidence"),
        "sources": src,
        "disagreement": disagreement,
        # The stricter of the two verify verdicts wins: a row is only VERIFIED if every source
        # that fed it verified. A half-checked row reported as VERIFIED is a check that lies.
        "verify_status": _strictest_verify(w.get("verify_status"), p.get("verify_status")),
        "verify_missing": (w.get("verify_missing") or []) + (p.get("verify_missing") or []),
    }


_VERIFY_RANK = {"CHECK_PLAN": 0, "CHECK_SOURCE": 0, "CANNOT_VERIFY": 1, "NO_VERIFY_STRINGS": 2,
                "VERIFIED": 3}


def _strictest_verify(*states) -> str | None:
    real = [s for s in states if s]
    if not real:
        return None
    return min(real, key=lambda s: _VERIFY_RANK.get(s, 1))


def _norm_phase_id(x) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(x or "").upper())


def join_plan_numbers(plan: dict, progress: dict) -> None:
    """Attach each phase's BEFORE/NOW numbers (from the ledger) to the LIVE phase (from the plan).

    TWO SOURCES, ONE ROW, AND NEITHER DUPLICATES THE OTHER. The plan states goals, gates and stop-if
    conditions in prose and states no numbers; the ledger states numbers with their floors and no
    longer states any goal, gate or stop-if. Joining them here means the panel has one row per
    phase with both, and there is no second copy of either to go stale.

    THE JOIN IS ASSERTED, NOT ASSUMED (standing discipline: *silent joins fabricate both green and
    red -- assert and count joined rows*). A ledger row whose `phase_ref` matches no live phase is
    an ORPHAN: the plan renamed or renumbered that phase and the ledger did not follow. Orphans are
    counted and surfaced as a contract violation rather than dropped on the floor, which is what an
    unasserted join would do.
    """
    if not isinstance(plan, dict) or plan.get("status") != "OK":
        return
    phases = plan.get("phases") or []
    by_id = {_norm_phase_id(p.get("id")): p for p in phases}
    for p in phases:
        p["numbers"] = None
    matched = 0
    orphans: list[str] = []
    if isinstance(progress, dict) and progress.get("status") == "OK":
        for row in progress.get("phases") or []:
            if not isinstance(row, dict):
                continue
            key = _norm_phase_id(row.get("phase_ref") or row.get("id"))
            target = by_id.get(key)
            if target is None:
                orphans.append(str(row.get("title") or row.get("id")))
                continue
            target["numbers"] = row
            matched += 1
    else:
        orphans = []
    plan["numbers_joined"] = matched
    plan["numbers_orphaned"] = orphans
    plan["numbers_unmatched_phases"] = [p["id"] for p in phases if not p.get("numbers")]
    if orphans:
        con = plan.setdefault("contract", {})
        con.setdefault("violations", []).extend({
            "kind": "PHASE_REF_ORPHAN", "literal": o, "phase": o,
            "detail": f"notes/progress_ledger.json has a before/now row for '{o}' whose "
                      f"phase_ref matches no phase in the plan. The plan renamed or renumbered "
                      f"that phase; the numbers row was left behind.",
        } for o in orphans)
        con["n_violations"] = len(con.get("violations") or [])
        con["status"] = "VIOLATIONS"
        plan["n_contract_violations"] = con["n_violations"]


def drift_rollup(s: dict) -> dict:
    """ONE NUMBER FOR "how much of what is on screen no longer matches its source".

    WHY IT IS ON SCREEN (owner, 2026-08-16: *"make sure you keep all this updated"*). Every panel
    already re-checks its own transcribed literals against the authority document on every
    refresh. That protection was invisible: a drifted row said CHECK-SOURCE in a cell the owner had
    to scroll to and click. A divergence nobody can see is a divergence nobody fixes, so the total
    is rendered in the window's top strip.

    THREE STATES, NEVER TWO. A panel that could not be checked at all (its authority document was
    unreadable, or the panel itself is MISSING or TIMEOUT) contributes to `n_unknown`, NEVER to
    `n_drifted` as a zero. A check that silently passes when its input is missing is not a check --
    the same rule the per-panel verifiers already follow, applied to the total.
    """
    parts: list[dict] = []

    def _one(key: str, label: str, getter) -> None:
        panel = s.get(key)
        if not isinstance(panel, dict) or panel.get("status") not in ("OK", "PARTIAL",
                                                                      "VIOLATIONS"):
            parts.append({"panel": label, "n": None,
                          "why": f"{(panel or {}).get('status', 'MISSING')} -- cannot be checked"})
            return
        items = getter(panel) or []
        parts.append({"panel": label, "n": len(items), "items": [str(x) for x in items][:12]})

    _one("walls", "scores and floors", lambda p: p.get("drifted"))
    _one("progress", "what moved", lambda p: p.get("drifted"))
    _one("organs", "brain organ map", lambda p: p.get("drifted"))
    _one("plan", "the plan", lambda p: [v.get("literal") for v in
                                        (p.get("contract") or {}).get("violations") or []])
    # ADDED 2026-08-16. The fidelity banner transcribes RELATIONS between numbers ("the refuted arm
    # scores above the incumbent that beats it"), not literals, so the substring check the other
    # four panels use cannot see it -- and before this it was checked by nothing at all. Each of
    # those relations is now recomputed from the scoring tool's live output every refresh, and one
    # that no longer holds lands here.
    _one("fidelity", "how closely we copy the brain", lambda p: p.get("drifted"))

    known = [p for p in parts if isinstance(p.get("n"), int)]
    unknown = [p for p in parts if p.get("n") is None]
    return {
        "n_drifted": sum(p["n"] for p in known),
        "n_unknown": len(unknown),
        "parts": parts,
        "plain": ("Every number this window shows is re-checked against the document it came from, "
                  "every refresh. This is how many no longer match."),
    }


# ---------------------------------------------------------------------------
# WHEN WAS EACH ROW'S EVIDENCE LAST UPDATED
# ---------------------------------------------------------------------------

def _rel_to_repo(p) -> str:
    """A repo-relative path string, which is the form the reference scanner recognises."""
    if not p:
        return ""
    try:
        return str(Path(str(p)).resolve().relative_to(REPO)).replace("\\", "/")
    except (ValueError, OSError, TypeError):
        return str(p).replace("\\", "/")


def _rows_of(panel: dict, *keys) -> list[dict]:
    out: list[dict] = []
    for k in keys:
        v = panel.get(k)
        if isinstance(v, list):
            out += [r for r in v if isinstance(r, dict)]
        elif isinstance(v, dict):
            out.append(v)
    return out


def attach_evidence(s: dict) -> dict:
    """Stamp EVERY ROW ON EVERY PANEL with when its own evidence was last updated.

    DERIVED, NOT COLLECTED A SECOND TIME. This runs after `collect()` has assembled the panels and
    reads only what those panels already carry -- the same discipline as `merge_scores()` and
    `drift_rollup()`. No panel is re-read, no collector is forked, and a panel that came back
    MISSING simply has no rows to stamp.

    WHERE EACH ROW'S TIME COMES FROM, panel by panel. In every case it is THE ARTIFACT, never the
    refresh clock (see `tools/status_evidence.py` for the ranking that decides between several):

      the plan            the plan document it is parsed from, or the measurement its numbers cite
      waiting on you      the board / plan / status document the item is recorded in
      scores and floors   the experiment directory named in the row's own `evidence` line
      brain organ map     the module or experiment the organ row cites, else the map document
      fidelity            the `outcome_source` metrics.json of each scored point
      latest results      that run's own metrics.json -- already stat'd while ranking them
      running now         the agent transcript / experiment output being written RIGHT NOW

    AND THE POINT OF IT: per panel, every row is compared against the newest evidence on that same
    panel, so "what is new and what is old" is answerable by looking rather than by subtracting.
    """
    if _ev is None:
        s["ages"] = {"status": "MISSING",
                     "detail": f"tools/status_evidence.py could not be imported ({_EV_ERR}), so no "
                               f"row can be dated. Every row shows UNKNOWN -- which is correct, "
                               f"and is not the same as up to date.",
                     "panels": {}, "n_unknown": None, "n_behind": None}
        return s["ages"]

    t0 = time.time()
    panels: dict[str, dict] = {}

    def do(label: str, rows: list[dict], texts_fn, carrier=None, carrier_label=None) -> None:
        rows = [r for r in rows if isinstance(r, dict)]
        for r in rows:
            try:
                texts = [t for t in (texts_fn(r) or []) if isinstance(t, str) and t]
            except Exception:
                texts = []
            r["evidence_age"] = _ev.stamp(texts, carrier=carrier,
                                          carrier_label=carrier_label)
        panels[label] = _ev.mark_panel(rows, key="evidence_age")

    def known(label: str, rows: list[dict], ts_fn, kind: str, source_fn) -> None:
        rows = [r for r in rows if isinstance(r, dict)]
        for r in rows:
            try:
                ts, src = ts_fn(r), source_fn(r)
            except Exception:
                ts, src = None, ""
            r["evidence_age"] = _ev.stamp_known(ts, kind, src)
        panels[label] = _ev.mark_panel(rows, key="evidence_age")

    # ---- the plan ------------------------------------------------------
    plan = s.get("plan") if isinstance(s.get("plan"), dict) else {}
    plan_doc = _rel_to_repo(plan.get("doc")) or "notes/LONG_TERM_PLAN.md"
    do("the plan", _rows_of(plan, "phases"),
       lambda r: [str((r.get("numbers") or {}).get("evidence") or ""), plan_doc])

    # ---- waiting on you: board questions, plan decisions, standing items ----
    board = s.get("board") if isinstance(s.get("board"), dict) else {}
    board_doc = _rel_to_repo(board.get("path")) or "notes/BOARD.md"
    near_doc = _rel_to_repo(plan.get("near_doc")) or "notes/PLAN.md"
    ops = plan.get("operator") if isinstance(plan.get("operator"), dict) else {}
    ops_path = ops.get("path")
    waiting = []
    for r in _rows_of(board, "open"):
        r["_ev_texts"] = [board_doc]
        waiting.append(r)
    for r in _rows_of(plan, "decisions"):
        r["_ev_texts"] = [near_doc]
        waiting.append(r)
    for r in _rows_of(ops, "rows"):
        r["_ev_texts"] = [str(r.get("source") or ""), _rel_to_repo(ops_path)]
        waiting.append(r)
    do("waiting on you", waiting, lambda r: r.pop("_ev_texts", []),
       carrier=ops_path, carrier_label="the standing-decisions file")

    # ---- scores and floors (the merged evidence table) ------------------
    scores = s.get("scores") if isinstance(s.get("scores"), dict) else {}
    walls = s.get("walls") if isinstance(s.get("walls"), dict) else {}
    spec = walls.get("spec_path") or str(COMPONENT_SPEC)
    do("scores and floors", _rows_of(scores, "rows", "retractions", "governing_floor"),
       lambda r: [str(r.get("evidence") or ""), str(r.get("instrument_evidence") or "")],
       carrier=spec, carrier_label="the component-health file")

    # ---- the brain organ map -------------------------------------------
    organs = s.get("organs") if isinstance(s.get("organs"), dict) else {}
    map_doc = _rel_to_repo(organs.get("map_path")) or "notes/ORGAN_MAP.md"

    def _organ_texts(r: dict) -> list:
        t = [str(r.get("evidence") or ""), str(r.get("ours") or "")]
        if r.get("module"):
            t.append("hdlab/" + str(r["module"]))
        if r.get("source") == "ORGAN_MAP":
            t.append(map_doc)
        return t

    do("brain organ map", _rows_of(organs, "rows"), _organ_texts,
       carrier=organs.get("overlay_path"), carrier_label="the organ-panel file")

    # ---- how closely we copy the brain ---------------------------------
    fid = s.get("fidelity") if isinstance(s.get("fidelity"), dict) else {}
    fid_map = _rel_to_repo(fid.get("map_path")) or "notes/ORGAN_MAP.md"
    do("how closely we copy the brain", _rows_of(fid, "rows"),
       lambda r: [str(r.get("outcome_source") or "")],
       carrier=REPO / "tools" / "brain_fidelity_score.py",
       carrier_label="the scoring tool that carries this fixture")
    # The divergence table is a second table on the same tab and is stamped separately, because its
    # evidence is a different artifact (the map) from the scored points above (their own runs).
    do("organ divergence", _rows_of(fid, "divergence"), lambda r: [fid_map])

    # ---- latest results: the mtime is already in hand from the ranking ---
    res = s.get("results") if isinstance(s.get("results"), dict) else {}
    now = time.time()
    known("latest results", _rows_of(res, "rows"),
          lambda r: (now - r["age_s"]) if isinstance(r.get("age_s"), (int, float)) else None,
          "MEASUREMENT", lambda r: _rel_to_repo(r.get("path")))

    # ---- running now: liveness IS the evidence timestamp ----------------
    run = s.get("running") if isinstance(s.get("running"), dict) else {}
    ag = run.get("agents") if isinstance(run.get("agents"), dict) else {}
    known("running now", _rows_of(ag, "agents"),
          lambda r: (now - r["idle_s"]) if isinstance(r.get("idle_s"), (int, float)) else None,
          "ACTIVITY", lambda r: "the agent's own transcript, appended to as it works")
    ag_summary = panels.pop("running now", None)
    do("running experiments", _rows_of(run, "local_experiments"),
       lambda r: [str(r.get("name") or "")])
    exp_summary = panels.get("running experiments")
    # One tab, one summary: the agents and the experiments on it are merged into a single
    # "running now" reading rather than two, because the owner reads one tab.
    merged_rows = _rows_of(ag, "agents") + _rows_of(run, "local_experiments")
    panels["running now"] = _ev.mark_panel(merged_rows, key="evidence_age")
    panels.pop("running experiments", None)
    _ = (ag_summary, exp_summary)

    all_summaries = list(panels.values())
    dated_ts = [p["newest_ts"] for p in all_summaries if p.get("newest_ts")]
    old_ts = [p["oldest_ts"] for p in all_summaries if p.get("oldest_ts")]
    out = {
        "status": "OK",
        "panels": panels,
        "n_rows": sum(p.get("n_rows", 0) for p in all_summaries),
        "n_unknown": sum(p.get("n_unknown", 0) for p in all_summaries),
        "n_behind": sum(p.get("n_behind", 0) for p in all_summaries),
        "newest_rel": _ev.relative(now - max(dated_ts)) if dated_ts else "UNKNOWN",
        "oldest_rel": _ev.relative(now - min(old_ts)) if old_ts else "UNKNOWN",
        "took_s": round(time.time() - t0, 3),
        "cache": _ev.cache_stats(),
        "plain": ("Every row carries WHEN ITS OWN EVIDENCE was last updated -- the experiment's "
                  "output file, the document it was parsed from, the transcript being written. "
                  "Never when this window last refreshed: a fresh clock over a stale number is "
                  "worse than no clock at all."),
    }
    s["ages"] = out
    return out


def collect() -> dict:
    """All nine panels. Never raises; never blocks past the sum of the panel budgets."""
    t0 = time.time()
    if _ev is not None:
        # One stat per distinct artifact per refresh. Cleared here so an experiment that finishes
        # between two refreshes shows its new time on the next one.
        _ev.begin_refresh()
    walls = _panel("walls", collect_walls, WALLS_BUDGET_S)
    board_p = _panel("board", collect_board, BOARD_BUDGET_S)
    running = _panel("running", collect_running, RUNNING_BUDGET_S)
    results = _panel("results", collect_results, RESULTS_BUDGET_S)
    loop = _panel("loop", collect_loop, LOOP_BUDGET_S)
    if _organs is None:
        progress = _organs_missing("progress")
        organs = _organs_missing("organ map")
        fidelity = _organs_missing("fidelity")
    else:
        progress = _panel("progress", _organs.collect_progress, PROGRESS_BUDGET_S)
        organs = _panel("organs", _organs.collect_organs, ORGANS_BUDGET_S)
        fidelity = _panel("fidelity", _organs.collect_fidelity, FIDELITY_BUDGET_S)
    if _plan is None:
        plan = {"status": "MISSING",
                "detail": f"tools/status_plan.py could not be imported ({_PLAN_ERR}), so the plan "
                          f"panel has no data. Showing MISSING rather than a remembered plan."}
    else:
        plan = _panel("plan", _plan.collect_plan, PLAN_BUDGET_S)
    join_plan_numbers(plan, progress)
    out = {
        "ts": _now_iso(),
        "took_s": round(time.time() - t0, 2),
        "repo": str(REPO),
        "plan": plan,
        "walls": walls,
        "board": board_p,
        "running": running,
        "results": results,
        "loop": loop,
        "progress": progress,
        "organs": organs,
        "fidelity": fidelity,
    }
    # The merged EVIDENCE view. Derived, never collected a second time: it is a join of two panels
    # already in this dict, so there is no third source of truth and no extra file read.
    out["scores"] = merge_scores(walls, progress)
    out["drift"] = drift_rollup(out)
    # LAST, because it stamps the rows of every panel above INCLUDING the merged scores view.
    attach_evidence(out)
    return out


# ---------------------------------------------------------------------------
# human dump (also the fallback view if Tk is unavailable)
# ---------------------------------------------------------------------------

def render_text(s: dict) -> str:
    L: list[str] = []
    L.append(f"WHERE WE ARE / WHAT IS HAPPENING     {s['ts']}   (collected in {s['took_s']}s)")
    L.append("=" * 78)

    d = s.get("drift") or {}
    L.append(f"DRIFT: {d.get('n_drifted')} value(s) on screen no longer match the document they "
             f"came from; {d.get('n_unknown')} panel(s) could not be checked at all")
    for p in d.get("parts") or []:
        L.append(f"   {p.get('panel')}: "
                 f"{p['n'] if p.get('n') is not None else 'UNKNOWN -- ' + str(p.get('why'))}")

    ag = s.get("ages") or {}
    L.append("")
    if ag.get("status") != "OK":
        L.append(f"EVIDENCE AGE: {ag.get('status')} -- {str(ag.get('detail'))[:160]}")
    else:
        L.append(f"EVIDENCE AGE: newest thing on screen {ag.get('newest_rel')}, oldest "
                 f"{ag.get('oldest_rel')}. {ag.get('n_behind')} of {ag.get('n_rows')} rows rest on "
                 f"evidence behind the newest on their own panel; {ag.get('n_unknown')} could not "
                 f"be dated. (These are ARTIFACT times, never the refresh clock.)")
        for name, p in (ag.get("panels") or {}).items():
            L.append(f"   {name}: newest {p.get('newest_rel')}, oldest {p.get('oldest_rel')}, "
                     f"{p.get('n_behind')} older, {p.get('n_unknown')} undated")

    L.append("")
    if _plan is not None:
        try:
            L.append(_plan.render_text(s.get("plan") or {}))
        except Exception as exc:
            L.append(f"the plan: RENDER FAILED ({type(exc).__name__}: {exc})")
    else:
        L.append(f"the plan: MISSING ({_PLAN_ERR})")

    w = s["walls"]
    L.append("")
    L.append("1. THE WALLS -- every score next to the floor it has to beat")
    if w.get("status") != "OK":
        L.append(f"   {w.get('status')}: {w.get('detail', '')}")
    else:
        h = w.get("headline") or {}
        if h:
            L.append(f"   {h.get('title')}")
            L.append(f"     ours {h.get('score')} ({h.get('score_detail')})")
            L.append(f"     floor {h.get('floor')} = {h.get('floor_name')} "
                     f"({h.get('floor_detail')})")
            L.append(f"     -> {h.get('standing')}, intervals separated: {h.get('separated')}")
            L.append(f"     {h.get('plain_verdict')}")
        for r in w.get("rows") or []:
            score = r.get("score") or "MISSING"
            floor = r.get("floor") or "MISSING"
            flag = "" if r.get("verify_status") == "VERIFIED" else \
                f"  [{r.get('verify_status')}]"
            L.append(f"   #{r.get('n')} {r.get('title')}  measurable alone: "
                     f"{r.get('instrument')}{flag}")
            L.append(f"       ours {score}   vs floor {floor} ({r.get('floor_name')})   "
                     f"{r.get('standing')} / separated {r.get('separated')}")
        L.append(f"   parts with NO instrument at all: {w.get('n_no_instrument')} "
                 f"{w.get('no_instrument')}")
        L.append(f"   parts BELOW their floor: {w.get('n_below_floor')} {w.get('below_floor')}")
        if w.get("drifted"):
            L.append(f"   CHECK THE PLAN -- numbers no longer found in notes/PLAN.md: "
                     f"{w['drifted']}")

    b = s["board"]
    L.append("")
    L.append(f"2. WAITING ON YOU -- {b.get('n_open', '?')} open question(s)")
    if b.get("status") != "OK":
        L.append(f"   {b.get('status')}: {b.get('detail', '')}")
    for r in b.get("open") or []:
        L.append(f"   {r.get('id')}: {r.get('question')}")
        L.append(f"       my recommendation: {r.get('rec')}")

    rn = s["running"]
    L.append("")
    L.append("3. RUNNING RIGHT NOW")
    if rn.get("status") != "OK":
        L.append(f"   {rn.get('status')}: {rn.get('detail', '')}")
    ag = rn.get("agents") or {}
    if ag.get("status") == "OK":
        L.append(f"   agents working: {ag.get('n_active')}")
        for a in (ag.get("agents") or [])[:8]:
            L.append(f"     [{a['state']}] {a['name']} ({a['agent_type']}, {a['model']}) "
                     f"running {_fmt_dur(a['elapsed_s'])}, last active "
                     f"{_fmt_dur(a['idle_s'])} ago -- {a['description']}")
    else:
        L.append(f"   agents: {ag.get('status')} {ag.get('detail', '')}")
    lx = rn.get("local_experiments") or []
    L.append(f"   detached experiments on this machine: {len(lx)}")
    for e in lx:
        L.append(f"     {e.get('name')} pid={e.get('pid')} "
                 f"running {_fmt_dur(e.get('elapsed_s'))}")
    g = rn.get("gpu") or {}
    L.append(f"   remote GPU: util {rn.get('gpu_util')}% (source {g.get('source')}), "
             f"queue {g.get('queue_status')}")
    ck = rn.get("remote_checkpoint") or {}
    L.append(f"   remote liveness (checkpoint, NOT the heartbeat): {ck.get('state')} "
             f"-- {ck.get('reason') or ck.get('checkpoint', '')}")
    for a in rn.get("alerts") or []:
        L.append(f"   ALERT [{a.get('level')}] {a.get('code')}: {a.get('msg')}")

    res = s["results"]
    L.append("")
    L.append("4. LATEST RESULTS")
    if res.get("status") != "OK":
        L.append(f"   {res.get('status')}: {res.get('detail', '')}")
    else:
        L.append(f"   {res.get('n_negative')} of the last {len(res.get('rows') or [])} are "
                 f"negative; {res.get('n_no_floor')} state no floor")
        for r in res.get("rows") or []:
            mark = r.get("label", "FINDING")
            age = (r.get("evidence_age") or {})
            age_s = _ev.line(age) if _ev is not None else "?"
            L.append(f"   {r['when']}  ({age_s})  {r['verdict']:<22} [{mark}] "
                     f"floor named: {'yes' if r['floor_named'] else 'NO'}  "
                     f"separated: {r['separated']}  {r['name']}")
            if r["verdict_msg"]:
                L.append(f"        {r['verdict_msg'][:150]}")

    lp = s["loop"]
    L.append("")
    L.append("5. OVERNIGHT LOOP")
    if lp.get("armed") is True:
        L.append(f"   ARMED, cap {lp.get('cap_label')}, armed at {lp.get('armed_at')}")
    elif lp.get("armed") is False:
        L.append("   DISARMED")
    else:
        L.append(f"   UNKNOWN: {lp.get('detail', '')}")
    L.append(f"   continuations used recently: {lp.get('continuations_recent_total')}")
    L.append(f"   STOP IT WITH:  {lp.get('disarm_cmd')}")

    # Panels A / B / C. Rendered by their own module so there is one renderer per collector.
    L.append("")
    L.append("=" * 78)
    if _organs is not None:
        try:
            L.append(_organs.render_text({"progress": s.get("progress"),
                                          "organs": s.get("organs"),
                                          "fidelity": s.get("fidelity")}))
        except Exception as exc:  # a broken renderer must not take the dump down
            L.append(f"progress / organ map / fidelity: RENDER FAILED "
                     f"({type(exc).__name__}: {exc})")
    else:
        L.append(f"progress / organ map / fidelity: MISSING ({_ORGANS_ERR})")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# self-test -- the degradation proof
# ---------------------------------------------------------------------------

def self_test() -> int:
    """Prove the two properties that matter at 3am: it does not hang, and it does not die.

    Three scenarios, all run for real (no mocking of the result, only of the environment):
      A. NORMAL      -- against the live repo, to prove the panels actually populate.
      B. REMOTE DEAD -- dashboard pointed at a closed port and the SSH alias made invalid, so
                        every remote path genuinely fails rather than being skipped.
      C. FILES GONE  -- every required file pointed at a nonexistent path.
    In B and C the collector must still return all five panels, must mark the affected ones
    MISSING/UNKNOWN rather than inventing numbers, and must come back inside its budget.
    """
    import tempfile
    ok = True
    results: list[str] = []

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        line = f"[self-test] {'PASS' if cond else 'FAIL'} {label}"
        print(line, file=sys.stdout if cond else sys.stderr)
        results.append(line)
        if not cond:
            ok = False

    budget = (WALLS_BUDGET_S + BOARD_BUDGET_S + RUNNING_BUDGET_S
              + RESULTS_BUDGET_S + LOOP_BUDGET_S)
    panels = ("plan", "walls", "board", "running", "results", "loop",
              "progress", "organs", "fidelity")

    # ---- A. normal -------------------------------------------------------
    t0 = time.time()
    a = collect()
    took_a = time.time() - t0
    check(all(k in a for k in panels), "A/normal: all nine panels present")
    check(a["plan"].get("status") == "OK",
          f"A/normal: the plan panel populated ({a['plan'].get('status')}: "
          f"{str(a['plan'].get('detail'))[:120]})")
    check(a["plan"].get("current_id") is not None,
          "A/normal: the plan panel resolves WHICH PHASE WE ARE IN")
    check(bool((a["plan"].get("next_action") or {}).get("text")),
          "A/normal: the plan panel resolves a single NEXT ACTION")
    check(a["plan"].get("numbers_joined") == len(a["plan"].get("phases") or []),
          f"A/normal: every phase's before/now numbers joined to a live phase "
          f"(joined {a['plan'].get('numbers_joined')} of "
          f"{len(a['plan'].get('phases') or [])})")
    check(not a["plan"].get("numbers_orphaned"),
          f"A/normal: no numbers row is orphaned by a plan rename "
          f"({a['plan'].get('numbers_orphaned')})")
    dr = a.get("drift") or {}
    check(isinstance(dr.get("n_drifted"), int) and isinstance(dr.get("n_unknown"), int),
          "A/normal: the drift roll-up produces two counts the window can render")
    check(dr.get("n_unknown") == 0,
          f"A/normal: every drift-checkable panel WAS checked "
          f"(unchecked: {[p for p in dr.get('parts') or [] if p.get('n') is None]})")
    # The results panel is the one that was blowing its budget. Prove the fix, not the intent.
    sc = (a["results"] or {}).get("scan") or {}
    check(sc.get("complete") is True,
          f"A/normal: the newest-results search PROVED it found the newest "
          f"(complete={sc.get('complete')!r})")
    check(isinstance(sc.get("n_metrics_opened"), int)
          and sc["n_metrics_opened"] < max(400, sc.get("n_dirs", 0) // 4),
          f"A/normal: it opened {sc.get('n_metrics_opened')} metrics.json out of "
          f"{sc.get('n_dirs')} directories, not all of them")
    # `(x or 99)` was the original form and it is WRONG for a duration: a scan that costs 0.0 s is
    # the best possible outcome and `0.0 or 99` evaluates to 99, so the assertion failed precisely
    # when the panel was fastest. Caught 2026-08-16 when the warm scan hit 0.0 s.
    _scan_s = sc.get("took_s")
    check(isinstance(_scan_s, (int, float)) and _scan_s < 3.0,
          f"A/normal: the results scan cost {_scan_s}s, well inside its "
          f"{RESULTS_BUDGET_S:.0f}s budget")
    check(took_a < budget, f"A/normal: returned in {took_a:.1f}s (budget {budget:.0f}s)")
    check(a["progress"].get("status") == "OK", "A/normal: progress panel populated")
    check(a["organs"].get("status") == "OK", "A/normal: organ-map panel populated")
    check(a["fidelity"].get("status") in ("OK", "PARTIAL"),
          "A/normal: fidelity panel populated")
    check("UNVALIDATED" in str(a["fidelity"].get("validation_verdict", "")).upper(),
          "A/normal: the fidelity panel carries its UNVALIDATED verdict, not a bare number")
    check(not (a["progress"].get("drifted") or []),
          f"A/normal: every transcribed progress number is still findable in its source "
          f"(drifted: {a['progress'].get('drifted')})")
    sc_m = a.get("scores") or {}
    check(sc_m.get("status") == "OK",
          f"A/normal: the merged scores-and-floors view built ({sc_m.get('status')})")
    check(len(sc_m.get("rows") or []) >= 8,
          f"A/normal: the merge produced one row per part, not two tabs' worth "
          f"(got {len(sc_m.get('rows') or [])})")
    naked_m = [r.get("title") for r in sc_m.get("rows") or []
               if (r.get("now") or {}).get("score") and not (r.get("now") or {}).get("floor")
               and not (r.get("now") or {}).get("floor_name")]
    check(not naked_m,
          f"A/normal: THE RULE SURVIVES THE MERGE -- no merged row shows a score with neither a "
          f"floor nor an explicit non-answer ({naked_m})")
    check(isinstance(sc_m.get("n_retracted"), int) and sc_m["n_retracted"] > 0,
          f"A/normal: retractions survive the merge as first-class rows "
          f"(got {sc_m.get('n_retracted')})")
    check(isinstance(sc_m.get("n_disagreements"), int),
          "A/normal: where the two merged sources disagree, the count is reported not hidden")
    check(a["walls"].get("status") == "OK", "A/normal: walls panel populated")
    check(a["walls"].get("headline") is not None, "A/normal: headline score+floor present")
    hl = a["walls"].get("headline") or {}
    check(bool(hl.get("score")) and bool(hl.get("floor")),
          "A/normal: the headline carries BOTH a score and a floor")
    bad = [r["title"] for r in (a["walls"].get("rows") or [])
           if r.get("score") not in (None, "") and r.get("floor") in (None, "")
           and r.get("floor_name") != "MISSING"]
    check(not bad, f"A/normal: no row shows a score without a floor or an explicit MISSING "
                   f"({bad})")
    check(a["loop"].get("armed") in (True, False),
          "A/normal: loop arm state resolves to a real boolean")
    check(a["results"].get("status") in ("OK", "MISSING"),
          "A/normal: results panel resolved")
    drift = a["walls"].get("drifted") or []
    check(not drift, f"A/normal: every quoted number still found in notes/PLAN.md "
                     f"(drifted: {drift})")

    # ---- A2. EVERY ROW CARRIES WHEN ITS OWN EVIDENCE WAS LAST UPDATED ----
    ages = a.get("ages") or {}
    check(ages.get("status") == "OK",
          f"A2/ages: the evidence-age pass ran ({ages.get('status')}: "
          f"{str(ages.get('detail'))[:110]})")
    check((ages.get("took_s") or 99) < 1.0,
          f"A2/ages: dating every row cost {ages.get('took_s')}s -- the refresh stays cheap")
    check(len(ages.get("panels") or {}) >= 7,
          f"A2/ages: every panel got an age summary (got {sorted(ages.get('panels') or {})})")
    check((ages.get("n_rows") or 0) >= 100,
          f"A2/ages: it stamped the whole window, not one panel (got {ages.get('n_rows')} rows)")

    # Collect every stamp that was actually produced, so the rules below are checked against the
    # rendered values and not against the intent.
    def _stamps(state: dict) -> list[dict]:
        found: list[dict] = []
        stack = [state]
        seen = 0
        while stack and seen < 20000:
            cur = stack.pop()
            seen += 1
            if isinstance(cur, dict):
                st = cur.get("evidence_age")
                if isinstance(st, dict):
                    found.append(st)
                stack.extend(v for v in cur.values() if isinstance(v, (dict, list)))
            elif isinstance(cur, list):
                stack.extend(v for v in cur if isinstance(v, (dict, list)))
        return found

    st_all = _stamps(a)
    check(len(st_all) >= 100,
          f"A2/ages: the stamps are ON THE ROWS the window renders (found {len(st_all)})")
    check(all(("rel" in x) for x in st_all),
          "A2/ages: every stamp carries a relative age the owner can read at a glance")
    check(all((x.get("when") or x.get("rel") == "UNKNOWN") for x in st_all),
          "A2/ages: every dated stamp ALSO carries its absolute value, as asked")

    # THE RULE THAT MATTERS, AND ITS NEGATIVE CONTROL. A stamp must be the ARTIFACT's time. A
    # stamp equal to the refresh clock would be the exact failure this was built to prevent -- a
    # fresh clock over a stale number. The only rows legitimately at 'now' are the live ones on
    # RUNNING NOW, whose artifact genuinely is being written this second, so they are excluded by
    # KIND rather than by panel name.
    t_now = time.time()
    clocked = [x for x in st_all
               if isinstance(x.get("ts"), (int, float))
               and abs(x["ts"] - t_now) < 5.0 and x.get("kind") != "ACTIVITY"]
    check(not clocked,
          f"A2/ages: NO row is stamped with the refresh clock "
          f"({[c.get('source') for c in clocked][:4]})")
    kinds = {x.get("kind") for x in st_all}
    check("MEASUREMENT" in kinds,
          f"A2/ages: rows ARE being dated from experiment output files, not just documents "
          f"(kinds seen: {sorted(k for k in kinds if k)})")
    # The control that proves the line above can fail: the SAME machinery, pointed at nothing.
    if _ev is not None:
        blank = _ev.stamp(["nothing at all is named here"], carrier=None)
        check(blank.get("ts") is None and blank.get("rel") == "UNKNOWN",
              f"A2/ages NEGATIVE CONTROL: a row with no artifact is UNKNOWN, so the pass above "
              f"is not passing everything (got {blank.get('rel')!r})")

    # "what is new and what is old" must be answerable without arithmetic.
    res_ages = (ages.get("panels") or {}).get("latest results") or {}
    check(res_ages.get("newest_rel") and res_ages.get("oldest_rel"),
          f"A2/ages: each panel states its newest AND oldest evidence "
          f"({res_ages.get('newest_rel')} / {res_ages.get('oldest_rel')})")
    check(isinstance(ages.get("n_behind"), int) and ages["n_behind"] > 0,
          f"A2/ages: rows behind the newest evidence on their own panel are FLAGGED, and the live "
          f"window really does have some (got {ages.get('n_behind')})")
    # ... and the control that the flag is not simply always on.
    fresh_panel = [p for p in (ages.get("panels") or {}).values()
                   if p.get("n_dated", 0) >= 2 and p.get("n_behind") == 0]
    check(bool(fresh_panel),
          f"A2/ages NEGATIVE CONTROL: at least one multi-row panel has NO row flagged older, so "
          f"the marker is not fired on everything "
          f"({[(k, v.get('n_behind')) for k, v in (ages.get('panels') or {}).items()]})")

    # ---- A3. THE FIDELITY PANEL'S FRAMING AND ITS RE-DERIVED CLAIMS ------
    fd = a.get("fidelity") or {}
    fr = fd.get("framing") or {}
    vl = str(fr.get("verdict_line") or "").upper()
    check("UNVALIDATED AS A PREDICTOR AT OUR CURRENT LOW FIDELITY" in vl,
          f"A3/fidelity: the banner scopes the null to our CURRENT LOW FIDELITY (got {vl[:90]!r})")
    check("EXPECTED TO BECOME PREDICTIVE AS FIDELITY RISES" in vl,
          "A3/fidelity: the banner carries the second clause the owner argued for")
    check("NOT USABLE AS A PERFORMANCE CLAIM TODAY" in vl,
          "A3/fidelity: and the clause that actually prevents the failure mode is still there")
    check("NOT A MEASURE OF HOW WELL" in str(fd.get("headline")).upper(),
          "A3/fidelity: the headline still denies that this measures how well anything works")
    check("OWNER'S ARGUMENT" in str(fr.get("owner_argument") or "").upper()
          and "NOT AS A MEASUREMENT" in str(fr.get("owner_argument") or "").upper(),
          "A3/fidelity: the owner's reasoning is carried as an ARGUMENT, explicitly not as a "
          "measurement this module made")
    check(len(fr.get("named_misses") or []) == 2,
          f"A3/fidelity: BOTH named misses are kept on screen as counter-evidence "
          f"(got {fr.get('named_misses')})")
    check("TWO POINTS, not a refutation" in str(fr.get("counter_evidence_note") or ""),
          "A3/fidelity: and they are presented as two points rather than as a refutation")
    check(isinstance(fr.get("pct_min"), (int, float))
          and isinstance(fr.get("pct_max"), (int, float)),
          f"A3/fidelity: the RANGE of scores actually observed is computed and shown "
          f"(got {fr.get('pct_min')}..{fr.get('pct_max')})")
    sca = fd.get("scatter") or {}
    check(sca.get("n") == len(fd.get("rows") or []) - (sca.get("n_unscored") or 0),
          f"A3/fidelity: the scatter carries every scored point and counts the unscored "
          f"(n={sca.get('n')}, unscored={sca.get('n_unscored')})")
    check(sca.get("n", 0) >= 5 and all(isinstance(p.get("pct"), (int, float))
                                       for p in sca.get("points") or []),
          f"A3/fidelity: every plotted point has a real score -- none is plotted at zero to fill "
          f"the chart (n={sca.get('n')})")
    claims = fd.get("claims") or []
    check(len(claims) >= 6,
          f"A3/fidelity: every relation the banner asserts is re-derived, not transcribed "
          f"(got {len(claims)} claims)")
    check(all(c.get("holds") is not False for c in claims),
          f"A3/fidelity: on the live data every re-derived claim still holds "
          f"({[c['id'] for c in claims if c.get('holds') is False]})")
    check(not (fd.get("cannot_check") or []),
          f"A3/fidelity: every claim could actually be checked ({fd.get('cannot_check')})")

    # THE NEGATIVE CONTROL FOR THE NEW DRIFT RULE. Feed the claim machinery a world in which the
    # named miss has stopped being true, and prove it is CAUGHT rather than repeated. Without this
    # the whole drift extension could be a no-op that always says zero.
    if _organs is not None:
        doctored = [
            {"component": "c_ca3_completion_as_built", "pct": 0.10, "held": False, "outcome": "x"},
            {"component": "d_the_flat_bag_incumbent", "pct": 0.90, "held": True, "outcome": "x"},
            {"component": "a_conjunctive_perirhinal_coding", "pct": 0.10, "held": True,
             "outcome": "x"},
        ]
        dc = {c["id"]: c for c in _organs._fidelity_claims(doctored, "NOW VALIDATED", {"SAME": 9})}
        check(dc["F3"]["holds"] is False,
              "A3/drift NEGATIVE CONTROL: if the CA3 arm stopped outscoring the flat bag the "
              "banner sentence is caught as STALE, not repeated")
        check(dc["F4"]["holds"] is False,
              "A3/drift NEGATIVE CONTROL: the flat-bag/conjunctive tie is re-derived and can fail")
        check(dc["F1"]["holds"] is False,
              "A3/drift NEGATIVE CONTROL: a tool that stopped saying UNVALIDATED is caught")
        check(dc["F2"]["holds"] is False,
              "A3/drift NEGATIVE CONTROL: a second positive result is caught, because it would "
              "change the power argument the banner rests on")
        check(dc["F6"]["holds"] is False,
              "A3/drift NEGATIVE CONTROL: 'fewer than half our organs match' is recounted and "
              "can fail")
        missing_comp = {c["id"]: c for c in _organs._fidelity_claims([], None, {})}
        check(missing_comp["F3"]["holds"] is None,
              "A3/drift: a claim whose components are absent is CANNOT-CHECK, never True -- a "
              "check that passes when its input is gone is not a check")
        # And it must reach the roll-up the owner reads, not stop at the data.
        doctored_state = dict(a)
        doctored_state["fidelity"] = dict(fd, status="OK", drifted=["F3", "F4"])
        roll = drift_rollup(doctored_state)
        base_roll = drift_rollup(a)
        check(roll["n_drifted"] == base_roll["n_drifted"] + 2,
              f"A3/drift NEGATIVE CONTROL: a stale fidelity claim RAISES the drift count on screen "
              f"({base_roll['n_drifted']} -> {roll['n_drifted']})")

    # ---- B. remote unreachable ------------------------------------------
    saved = {}
    if _inflight is not None:
        saved = {"dash": _inflight.DASHBOARD, "alias": _inflight.SSH_ALIAS}
        # 127.0.0.1:1 is closed on every machine -> a real connection refusal, not a mock.
        _inflight.DASHBOARD = "http://127.0.0.1:1"
        _inflight.SSH_ALIAS = "hd-instrument-no-such-host-selftest"
    _ckpt_cache["ts"] = 0.0
    _ckpt_cache["value"] = None
    try:
        t0 = time.time()
        b = collect()
        took_b = time.time() - t0
    finally:
        if _inflight is not None and saved:
            _inflight.DASHBOARD = saved["dash"]
            _inflight.SSH_ALIAS = saved["alias"]
        _ckpt_cache["ts"] = 0.0
        _ckpt_cache["value"] = None
    check(all(k in b for k in panels), "B/remote-dead: all nine panels still present")
    check(b["plan"].get("status") == "OK",
          "B/remote-dead: the plan panel is UNAFFECTED by the remote being down")
    check(took_b < budget, f"B/remote-dead: returned in {took_b:.1f}s (budget {budget:.0f}s) "
                           f"-- did NOT hang on an unreachable remote")
    check(b["walls"].get("status") == "OK",
          "B/remote-dead: the walls panel is UNAFFECTED by the remote being down")
    check(b["board"].get("status") in ("OK", "MISSING"),
          "B/remote-dead: the board panel is UNAFFECTED by the remote being down")
    check(b["loop"].get("armed") in (True, False),
          "B/remote-dead: the loop panel is UNAFFECTED by the remote being down")
    rck = (b["running"] or {}).get("remote_checkpoint") or {}
    check(rck.get("state") in ("UNKNOWN", "NO_REMOTE_RUN", "NO_CHECKPOINT"),
          f"B/remote-dead: remote liveness degrades to a named non-answer "
          f"(got {rck.get('state')!r}), never a fabricated one")
    gpu_b = (b["running"] or {}).get("gpu") or {}
    check(gpu_b.get("source") in (None, "stale", "cache", "ssh", "feed"),
          "B/remote-dead: GPU source is a declared value, not a guess")

    # B2. The probe itself, forced down an unresolvable host. Scenario B skips the probe when
    # nothing is running remotely (which is correct, and is why it is not sufficient on its
    # own): this exercises the SSH failure path directly, which is the one that must not hang.
    t0 = time.time()
    direct = probe_remote_checkpoint("hd-instrument-no-such-host-selftest")
    took_probe = time.time() - t0
    check(isinstance(direct, dict) and direct.get("state") == "UNKNOWN",
          f"B2/ssh-dead: an unresolvable host returns UNKNOWN with a reason "
          f"(got {direct.get('state')!r}: {str(direct.get('reason'))[:60]})")
    check(took_probe < REMOTE_CKPT_BUDGET_S,
          f"B2/ssh-dead: the probe gave up in {took_probe:.1f}s "
          f"(cap {REMOTE_CKPT_BUDGET_S:.0f}s), it did not hang")
    check("age_s" not in direct and "checkpoint" not in direct,
          "B2/ssh-dead: a failed probe reports NO checkpoint age -- never a fabricated one")

    # ---- C. required files absent ---------------------------------------
    td = Path(tempfile.mkdtemp(prefix="status_state_selftest_"))
    g = globals()
    keep = {k: g[k] for k in ("COMPONENT_SPEC", "PLAN_DOC", "STATUS_DOC", "BOARD_DOC",
                              "DATA_DIR", "HOOK_STATE", "AGENT_ROOT")}
    # The new panels read their own files, so pointing only THIS module's paths at nowhere would
    # leave them populated and the scenario would not be the scenario it claims to be.
    og = vars(_organs) if _organs is not None else {}
    okeep = {k: og[k] for k in ("ORGAN_MAP_DOC", "PROGRESS_SPEC", "ORGAN_SPEC", "REGISTRY",
                                "AUTHORITY_DOCS")} if og else {}
    pg = vars(_plan) if _plan is not None else {}
    pkeep = {k: pg[k] for k in ("LONG_PLAN_DOC", "NEAR_PLAN_DOC", "OPERATOR_SPEC", "CONTRACT_DOC",
                                "AUTHORITY_DOCS")} if pg else {}
    # The evidence resolver has its own idea of where the repo is, so pointing only the collectors
    # at nowhere would leave every artifact resolvable and the scenario would be vacuous -- the
    # same trap the organ panels fell into when they were added.
    eg = vars(_ev) if _ev is not None else {}
    ekeep = {k: eg[k] for k in ("REPO", "DATA_DIR")} if eg else {}
    try:
        if eg:
            eg["REPO"] = td / "nope_repo"
            eg["DATA_DIR"] = td / "nope_repo" / "data"
            _ev.begin_refresh()
        if pg:
            pg["LONG_PLAN_DOC"] = td / "nope_LONG_TERM_PLAN.md"
            pg["NEAR_PLAN_DOC"] = td / "nope_PLAN.md"
            pg["OPERATOR_SPEC"] = td / "nope_operator_decisions.json"
            pg["CONTRACT_DOC"] = td / "nope_contract.md"
            pg["AUTHORITY_DOCS"] = [td / "nope_STATUS.md"]
        if og:
            og["ORGAN_MAP_DOC"] = td / "nope_ORGAN_MAP.md"
            og["PROGRESS_SPEC"] = td / "nope_progress_ledger.json"
            og["ORGAN_SPEC"] = td / "nope_organ_panel.json"
            og["REGISTRY"] = td / "nope_capability_registry.jsonl"
            og["AUTHORITY_DOCS"] = [td / "nope_STATUS.md"]
            _organs._cache.clear()
        g["COMPONENT_SPEC"] = td / "nope_component_health.json"
        g["PLAN_DOC"] = td / "nope_PLAN.md"
        g["STATUS_DOC"] = td / "nope_STATUS.md"
        g["BOARD_DOC"] = td / "nope_BOARD.md"
        g["DATA_DIR"] = td / "nope_data"
        g["HOOK_STATE"] = td / "nope_data" / "hook_state"
        g["AGENT_ROOT"] = td / "nope_projects"
        t0 = time.time()
        c = collect()
        took_c = time.time() - t0
    finally:
        g.update(keep)
        if og:
            og.update(okeep)
            _organs._cache.clear()
        if pg:
            pg.update(pkeep)
        if eg:
            eg.update(ekeep)
            _ev.begin_refresh()
    check(all(k in c for k in panels), "C/files-absent: all nine panels still present")
    check(c["plan"].get("status") == "MISSING",
          f"C/files-absent: the plan panel reports MISSING (got {c['plan'].get('status')!r})")
    check(not (c["plan"].get("phases") or []),
          "C/files-absent: the plan panel invents no phases when the plan is gone")
    check((c["plan"].get("contract") or {}).get("status") == "CANNOT_CHECK",
          "C/files-absent: the plan's parser contract says CANNOT_CHECK, never VERIFIED")
    dc = c.get("drift") or {}
    check(dc.get("n_unknown", 0) >= 3,
          f"C/files-absent: unchecked panels count as UNKNOWN, never as zero drift "
          f"(n_unknown={dc.get('n_unknown')}, n_drifted={dc.get('n_drifted')})")
    check(c["progress"].get("status") == "MISSING",
          f"C/files-absent: progress reports MISSING (got {c['progress'].get('status')!r})")
    check(not (c["progress"].get("components") or []),
          "C/files-absent: progress invents no rows when its ledger is gone")
    check(c["organs"].get("status") == "MISSING",
          f"C/files-absent: organ map reports MISSING (got {c['organs'].get('status')!r})")
    check(not (c["organs"].get("rows") or []),
          "C/files-absent: the organ map invents no organs when its sources are gone")
    check(took_c < budget, f"C/files-absent: returned in {took_c:.1f}s")
    check(c["walls"].get("status") == "MISSING",
          f"C/files-absent: walls reports MISSING (got {c['walls'].get('status')!r})")
    check(not (c["walls"].get("rows") or []),
          "C/files-absent: walls invents no rows when the spec is gone")
    check(c["board"].get("status") == "MISSING",
          f"C/files-absent: board reports MISSING (got {c['board'].get('status')!r})")
    check(c["results"].get("status") in ("MISSING", "ERROR"),
          f"C/files-absent: results reports MISSING (got {c['results'].get('status')!r})")
    ag_c = (c["running"] or {}).get("agents") or {}
    check(ag_c.get("status") in ("MISSING", "OK"),
          "C/files-absent: agents panel resolves without raising")
    # The evidence pass must survive every artifact vanishing, and -- the point -- must NOT fall
    # back to the refresh clock when it can no longer find anything to date.
    ac = c.get("ages") or {}
    check(ac.get("status") == "OK",
          f"C/files-absent: the evidence-age pass still returns (got {ac.get('status')!r})")
    st_c = _stamps(c)
    t_now_c = time.time()
    clocked_c = [x for x in st_c
                 if isinstance(x.get("ts"), (int, float)) and abs(x["ts"] - t_now_c) < 5.0
                 and x.get("kind") != "ACTIVITY"]
    check(not clocked_c,
          f"C/files-absent: with every artifact gone, NOT ONE row falls back to the refresh clock "
          f"({[x.get('source') for x in clocked_c][:4]})")
    # With the repo pointed at nowhere, NO row may still claim a measurement, a fragment or a
    # document behind it. The only stamps that may survive are UNKNOWN, or the CARRIER stamp of a
    # file that genuinely did not vanish (the scoring tool is an imported MODULE, so it is still
    # there) -- and a CARRIER stamp says on screen that it is not the evidence date.
    kinds_c = {x.get("kind") for x in st_c}
    check(not (kinds_c & {"MEASUREMENT", "FRAGMENT", "NOTE", "REGISTRY", "CODE"}),
          f"C/files-absent: no row still claims an artifact that is gone (kinds: "
          f"{sorted(k for k in kinds_c if k)})")
    check(all(x.get("rel") == "UNKNOWN" or x.get("kind") == "CARRIER" for x in st_c),
          f"C/files-absent: every remaining stamp is UNKNOWN or an explicitly-labelled carrier "
          f"({[(x.get('kind'), x.get('rel')) for x in st_c][:4]})")
    txt = render_text(c)
    check("MISSING" in txt, "C/files-absent: the rendered view SAYS MISSING to the reader")
    check("EVIDENCE AGE" in txt,
          "C/files-absent: the rendered view still tells the reader about evidence ages")

    # ---- D. the write-back refuses the dangerous cases -------------------
    ok_w, msg_w = answer_question("Q1", "   ", td / "nope_BOARD.md")
    check(not ok_w, f"D/write-back: an empty answer is REFUSED ({msg_w[:60]})")
    ok_w, msg_w = answer_question("", "something", td / "nope_BOARD.md")
    check(not ok_w, "D/write-back: a missing question id is REFUSED")
    ok_w, msg_w = answer_question("Q1", "an answer", td / "nope_BOARD.md")
    check(not ok_w, "D/write-back: a missing board file is REFUSED, not created")
    check(not (td / "nope_BOARD.md").exists(),
          "D/write-back: a refused write created NO file")

    # A real round trip on a throwaway board, so the success path is proven too.
    bp = td / "BOARD.md"
    sp = td / "STATUS.md"
    sp.write_text("# STATUS\n\nAS OF: 2099-01-01 | fixture\n\n## POSITION\np\n\n"
                  "## TOP ITEM\nt\n\n## WHAT IS RUNNING\n- x\n", encoding="utf-8")
    if _board is not None:
        _board.ask("fixture question?", "nothing", "do it", bp, sp, "Q1")
        before = bp.read_text(encoding="utf-8")
        ok_w, msg_w = answer_question("Q1", "yes | with the cheap path", bp)
        check(ok_w, f"D/write-back: a real answer writes ({msg_w[:60]})")
        after = bp.read_text(encoding="utf-8")
        # Checked through the parser, not against raw bytes: board.py escapes a raw `|` on
        # write (`\|`) precisely so one typed into a cell cannot blow the row apart. What must
        # survive is the TEXT, which is what load() returns.
        _q2, _a2, _e2 = _board.load(bp)
        stored = next((r.get("answer") for r in _a2 if r.get("id") == "Q1"), None)
        check(stored == "yes | with the cheap path",
              f"D/write-back: the answer text round-trips intact, raw pipe and all "
              f"(got {stored!r})")
        check(_board.count_open(bp) == 0,
              "D/write-back: the question moved out of OPEN")
        check(before != after and "## ANSWERED" in after,
              "D/write-back: the board is still a well-formed board afterwards")
        ok_w, _ = answer_question("Q1", "again", bp)
        check(not ok_w, "D/write-back: answering an already-answered question is REFUSED")

    # ---- E. verdict classification, on REAL verdict strings from this repo ----------
    # Every case below is a string that has actually been written to a metrics.json here. The
    # first two are the reason negation has to dominate: both contain the word CLEARS and both
    # mean the opposite of a win. An earlier version of this function scored the first as a
    # win, which is exactly the "dashboard only surfaces good news" failure.
    cases = [
        ("NO_READOUT_VARIANT_CLEARS_THE_FLOOR", "NEGATIVE"),
        ("NO_ASSET_CLEARS_THE_STRONGEST_FLOOR", "NEGATIVE"),
        ("ASSET_CLEARS_THE_STRONGEST_FLOOR", "WIN"),
        ("ASSET_CLEARS_THE_HARDENED_FLOOR_AT_POWER", "WIN"),
        ("STRUCTURE_HURTS", "NEGATIVE"),
        ("CONJUNCTIVE_HURTS", "NEGATIVE"),
        ("CONJUNCTIVE_DOES_NOT_HELP", "NEGATIVE"),
        ("INSTRUMENT_STILL_LOOSE", "NEGATIVE"),
        ("G3_RESCORED_FAIL", "NEGATIVE"),
        ("HARD_PASS", "WIN"),
        ("MEASURED", "FINDING"),
        (NO_VERDICT, "NO VERDICT YET"),
        ("", "NO VERDICT YET"),
    ]
    wrong = [(v, want, _grade(v, "", {})["label"]) for v, want in cases
             if _grade(v, "", {})["label"] != want]
    check(not wrong, f"E/verdicts: all {len(cases)} real verdict strings classify correctly "
                     f"(wrong: {wrong})")
    check(_grade("SOMETHING_UNRECOGNISED_V3", "", {})["label"] == "FINDING",
          "E/verdicts: an unrecognised verdict defaults to FINDING, never to a win")
    sep_no = _grade("X", "margin 0.2737 CI [-0.2505, 0.7621]", {})["separated"]
    check(sep_no == "NO",
          f"E/verdicts: an interval whose lower bound is negative reads NOT separated "
          f"(got {sep_no!r})")
    sep_yes = _grade("X", "CI-separated BELOW it (strongest floor 0.0870)", {})["separated"]
    check(sep_yes == "YES", f"E/verdicts: an explicit CI-separated claim is read (got {sep_yes!r})")
    check(_grade("X", "no mention at all", {})["floor_named"] is False,
          "E/verdicts: a result that never names a floor is flagged as such")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Owner-facing status collector")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    s = collect()
    print(json.dumps(s, indent=2, default=str) if args.json else render_text(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
