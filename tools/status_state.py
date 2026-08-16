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

# --- paths (env-overridable so the self-test can point at absent files) ------
# notes/, not data/: `.gitignore` line 43 is `data/*`, so a spec kept under data/ would be
# absent from a fresh clone and panel 1 would come up MISSING for the next person. It also
# belongs beside notes/PLAN.md, the document it is transcribed from and checked against.
COMPONENT_SPEC = Path(os.environ.get("HD_COMPONENT_SPEC")
                      or (REPO / "notes" / "component_health.json"))
PLAN_DOC = Path(os.environ.get("HD_PLAN_DOC") or (REPO / "notes" / "PLAN.md"))
STATUS_DOC = Path(os.environ.get("HD_STATUS_DOC") or (REPO / "notes" / "STATUS.md"))
BOARD_DOC = Path(os.environ.get("HD_BOARD_PATH") or (REPO / "notes" / "BOARD.md"))
DATA_DIR = Path(os.environ.get("HD_DATA_DIR") or (REPO / "data"))
HOOK_STATE = DATA_DIR / "hook_state"
AGENT_ROOT = Path(os.environ.get("HD_AGENT_ROOT") or (Path.home() / ".claude" / "projects"))

# --- budgets. Worst case total is the sum of these, and it is bounded. ------
WALLS_BUDGET_S = 4.0
BOARD_BUDGET_S = 4.0
RUNNING_BUDGET_S = 14.0     # build_state is internally bounded to ~10s
RESULTS_BUDGET_S = 8.0
LOOP_BUDGET_S = 3.0
AGENTS_BUDGET_S = 4.0
REMOTE_CKPT_BUDGET_S = 7.0

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
    for p in (PLAN_DOC, STATUS_DOC):
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
        "authority_docs": [str(PLAN_DOC), str(STATUS_DOC)],
        "authority_missing": missing_docs,
        "can_verify": can_verify,
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
        "writable": os.access(str(BOARD_DOC), os.W_OK),
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
    return {
        "status": "OK" if st_status == "OK" else st_status,
        "state_status": st_status,
        "alerts": base.get("alerts") or [],
        "gpu": g,
        "gpu_util": util,
        "queues": base.get("queues") or {},
        "runners": base.get("runners") or {},
        "local_experiments": base.get("local_experiments") or [],
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


def collect_results(n: int = RESULTS_N) -> dict:
    """The newest verdicts, newest first, each with its floor and whether it was separated.

    Cost control: one os.scandir of `data/` (about 8,000 directories, roughly 0.4s) to get
    mtimes, then only the newest `n` metrics.json files are actually opened. The full-tree
    walk that a naive version would do is what makes a dashboard unusable, and the session
    hook has the same rule for the same reason.
    """
    if not DATA_DIR.is_dir():
        return {"status": "MISSING", "detail": f"data directory not found: {DATA_DIR}",
                "rows": []}
    try:
        entries = [e for e in os.scandir(DATA_DIR) if e.is_dir()]
    except OSError as exc:
        return {"status": "ERROR", "detail": f"cannot scan {DATA_DIR}: {exc}", "rows": []}
    stamped: list[tuple[float, str, Path]] = []
    for e in entries:
        p = Path(e.path) / "metrics.json"
        try:
            stamped.append((p.stat().st_mtime, e.name, p))
        except OSError:
            continue
    if not stamped:
        return {"status": "MISSING",
                "detail": f"no metrics.json under {DATA_DIR}; no results to show",
                "rows": [], "n_scanned": len(entries)}
    stamped.sort(reverse=True)

    rows: list[dict] = []
    for mtime, name, p in stamped[: max(1, n)]:
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

def collect() -> dict:
    """All five panels. Never raises; never blocks past the sum of the panel budgets."""
    t0 = time.time()
    walls = _panel("walls", collect_walls, WALLS_BUDGET_S)
    board_p = _panel("board", collect_board, BOARD_BUDGET_S)
    running = _panel("running", collect_running, RUNNING_BUDGET_S)
    results = _panel("results", collect_results, RESULTS_BUDGET_S)
    loop = _panel("loop", collect_loop, LOOP_BUDGET_S)
    return {
        "ts": _now_iso(),
        "took_s": round(time.time() - t0, 2),
        "repo": str(REPO),
        "walls": walls,
        "board": board_p,
        "running": running,
        "results": results,
        "loop": loop,
    }


# ---------------------------------------------------------------------------
# human dump (also the fallback view if Tk is unavailable)
# ---------------------------------------------------------------------------

def render_text(s: dict) -> str:
    L: list[str] = []
    L.append(f"WHERE WE ARE / WHAT IS HAPPENING     {s['ts']}   (collected in {s['took_s']}s)")
    L.append("=" * 78)

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
            L.append(f"   {r['when']}  {r['verdict']:<22} [{mark}] "
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
    panels = ("walls", "board", "running", "results", "loop")

    # ---- A. normal -------------------------------------------------------
    t0 = time.time()
    a = collect()
    took_a = time.time() - t0
    check(all(k in a for k in panels), "A/normal: all five panels present")
    check(took_a < budget, f"A/normal: returned in {took_a:.1f}s (budget {budget:.0f}s)")
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
    check(all(k in b for k in panels), "B/remote-dead: all five panels still present")
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
    try:
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
    check(all(k in c for k in panels), "C/files-absent: all five panels still present")
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
    txt = render_text(c)
    check("MISSING" in txt, "C/files-absent: the rendered view SAYS MISSING to the reader")

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
