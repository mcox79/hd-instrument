"""FastAPI backend. Endpoints read the cached snapshot maintained by Poller.

Run with: uvicorn server:app --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from poller import Poller


STATIC_DIR = Path(__file__).parent / "static"

# Local file paths for ack/answer writes (same machine as the dashboard).
_DATA_DIR = Path(r"D:\AI\hd-instrument\data")
_NEWS_ACKS_PATH = _DATA_DIR / "orchestrator_news_acks.jsonl"
_ANSWERS_PATH = _DATA_DIR / "orchestrator_answers.jsonl"
_QUESTIONS_MD_PATH = _DATA_DIR / "orchestrator_questions.md"

# A single lock guards the append-rename dance across both files. Append-only
# JSONL with atomic rewrite (.tmp + replace) keeps multiple writers safe.
_WRITE_LOCK = threading.Lock()


def _append_jsonl_atomic(path: Path, entry: dict) -> None:
    """Append one JSON line to path. Uses read+rewrite via tmp+replace for atomicity.

    Worth the extra read because multiple writers (the dashboard process plus
    any external tool that wants to nudge orchestrator) can collide on a plain
    open(..., 'a') on Windows.
    """
    with _WRITE_LOCK:
        existing = ""
        if path.is_file():
            existing = path.read_text(encoding="utf-8", errors="replace")
            if existing and not existing.endswith("\n"):
                existing += "\n"
        new_content = existing + json.dumps(entry, ensure_ascii=False) + "\n"
        fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, str(path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def _remove_question_from_md(question_number: int) -> bool:
    """Remove the numbered question from orchestrator_questions.md, atomically.

    Returns True if a question was actually removed. Returns False if the file
    doesn't exist or the number isn't found.

    The format of the markdown is conservative: numbered list items like
    "1. **TS** -- text...". We find the line starting with "<N>." and drop it
    along with any continuation lines that follow before the next "<M>." or a
    blank line that precedes a header.
    """
    with _WRITE_LOCK:
        if not _QUESTIONS_MD_PATH.is_file():
            return False
        text = _QUESTIONS_MD_PATH.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=False)
        out_lines: list[str] = []
        i = 0
        removed = False
        target_prefix_re = __import__("re").compile(
            rf"^\s*{question_number}\.\s"
        )
        next_item_re = __import__("re").compile(r"^\s*\d+\.\s")
        while i < len(lines):
            ln = lines[i]
            if not removed and target_prefix_re.match(ln):
                # Skip this item and its continuation lines.
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if next_item_re.match(nxt) or nxt.startswith("#") or nxt.strip() == "":
                        break
                    i += 1
                # Also skip one trailing blank line (numbered lists usually have one).
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
                removed = True
                continue
            out_lines.append(ln)
            i += 1

        if not removed:
            return False

        new_text = "\n".join(out_lines)
        # Preserve trailing newline if original had one.
        if text.endswith("\n") and not new_text.endswith("\n"):
            new_text += "\n"

        fd, tmp_path = tempfile.mkstemp(
            dir=str(_QUESTIONS_MD_PATH.parent),
            prefix=_QUESTIONS_MD_PATH.name + ".",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(new_text)
            os.replace(tmp_path, str(_QUESTIONS_MD_PATH))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    poller = Poller()
    app.state.poller = poller
    task = asyncio.create_task(poller.run_forever())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass
        poller.close()


app = FastAPI(title="hd-instrument dashboard", lifespan=lifespan)


@app.get("/api/health")
def health():
    return app.state.poller.health()


@app.get("/api/system")
def system():
    snap = app.state.poller.get_snapshot()
    return snap.get("system", {})


@app.get("/api/runs")
def runs():
    snap = app.state.poller.get_snapshot()
    return snap.get("runs", {})


@app.get("/api/queue")
def queue():
    snap = app.state.poller.get_snapshot()
    return snap.get("queue", {})


@app.get("/api/history")
def history():
    snap = app.state.poller.get_snapshot()
    return {"events": snap.get("history", [])}


@app.get("/api/tests")
def tests():
    snap = app.state.poller.get_snapshot()
    # Prefer the fresh queue-doc-derived list for the Experiments tab.
    return {"experiments": snap.get("queue_experiments", snap.get("experiments", []))}


@app.get("/api/debug")
def debug():
    snap = app.state.poller.get_snapshot()
    return snap.get("_debug", {})


# --- SPEC #2: local-substrate snapshot panel (closes the USER dashboard-gap: dashboard polled remote
#     state but NOT the local Store). Single-source: delegates to Skunkworks's authoritative --json checks
#     via tools/substrate_snapshot_once.py (NO inline reimplementation of CERT/axiom/invariant logic). ---
_REPO_ROOT = Path(__file__).resolve().parents[2]


@app.get("/api/substrate")
def substrate():
    """Cached local-substrate snapshot (read-only VIEW). Authoritative gate = the on-demand
    invariant-check; this is a button-triggered cached view (staleness shown via its `ts`)."""
    p = _REPO_ROOT / "data" / "local_substrate_snapshot.json"
    if not p.exists():
        return {"status": "no_snapshot", "hint": "POST /api/refresh-substrate (the 'Update Substrate' button)"}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        return JSONResponse({"status": "error", "error": str(e)[:200]}, status_code=500)


@app.post("/api/refresh-substrate")
def refresh_substrate():
    """'Update Substrate' button: run substrate_snapshot_once.py (delegates to Skunkworks's --json
    authoritative checks; single-source), then return the fresh snapshot. User-triggered, no poller."""
    import subprocess
    import sys as _sys
    script = _REPO_ROOT / "tools" / "substrate_snapshot_once.py"
    try:
        subprocess.run([_sys.executable, str(script)], cwd=str(_REPO_ROOT),
                       capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return JSONResponse({"status": "timeout", "error": "snapshot refresh exceeded 180s"}, status_code=504)
    p = _REPO_ROOT / "data" / "local_substrate_snapshot.json"
    if not p.exists():
        return JSONResponse({"status": "error", "error": "snapshot not written"}, status_code=500)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        return JSONResponse({"status": "error", "error": str(e)[:200]}, status_code=500)


@app.get("/api/capability")
def capability():
    """Raw markdown content of notes/substrate_capability_map.md. Read-only."""
    snap = app.state.poller.get_snapshot()
    return {"content": snap.get("capability_map", "")}


@app.get("/api/capability/raw")
def capability_raw():
    """Serve capability map as plain text for the open-in-new-tab link.

    Returns the full markdown so the browser can display it without DOM blowup.
    The JSON capability endpoint is fine for small consumers; this one is for
    humans reading the raw file directly.
    """
    snap = app.state.poller.get_snapshot()
    content = snap.get("capability_map", "")
    if not content:
        content = "(capability map not yet loaded — try again in a few seconds)"
    return PlainTextResponse(content, media_type="text/plain; charset=utf-8")


@app.get("/api/capability/tiers")
def capability_tiers():
    """Parsed tier summary from the last Summary tally table in the capability map."""
    snap = app.state.poller.get_snapshot()
    return snap.get("tier_summary", {"totals": {}, "parse_ok": False})


@app.get("/api/capability/rows")
def capability_rows():
    """Structured per-row payload for the redesigned Capability tab UI.

    Returns rows grouped by section (KILLER / UNSURE / PORTFOLIO / CLOSED)
    with state classifications, evidence/product columns, and per-group totals.
    See parsers.extract_capability_rows for the schema.
    """
    snap = app.state.poller.get_snapshot()
    return snap.get("capability_rows", {"parse_ok": False, "groups": [], "totals": {}})


@app.get("/api/status_log")
def status_log(
    limit: int = 50,
    kind: str | None = None,
    source: str | None = None,
):
    """Paginated, optionally filtered status log entries (newest first).

    Filters:
      kind   - event_kind exact match (e.g. "verdict_processed")
      source - source session match: orchestrator|research|testbed|cloud.
               Entries without a source field match only when source=='legacy'.
    """
    snap = app.state.poller.get_snapshot()
    entries: list[dict] = snap.get("status_log", [])
    if kind:
        entries = [e for e in entries if e.get("event_kind") == kind]
    if source:
        if source == "legacy":
            entries = [e for e in entries if not e.get("source")]
        else:
            entries = [e for e in entries if e.get("source") == source]
    return {"entries": entries[:max(1, min(300, limit))], "total": len(entries)}


@app.get("/api/cloud_cost")
def cloud_cost():
    """Cloud cost tracker snapshot.

    Returns the contents of data/cloud_cost_tracker.json if the cloud session
    is writing it; null otherwise. Schema (when present):
      { daily_budget_usd, accumulated_today_usd, current_hourly_rate_usd,
        last_updated, active_instances: [...] }
    """
    snap = app.state.poller.get_snapshot()
    return {"cloud_cost": snap.get("cloud_cost")}


@app.get("/api/sessions")
def sessions():
    """Per-session activity indicators.

    Returns the heartbeat for each session that has written one. Each entry
    has {session, ts, current_focus, last_event_ts, stale_after_s, age_s,
    is_stale}. Sessions that have never written a heartbeat are absent.

    See tools/orchestrator/session_heartbeat.py for the writer.
    """
    snap = app.state.poller.get_snapshot()
    return {"sessions": snap.get("sessions", {})}


_DIRECTOR_PLAN_PATH = _DATA_DIR / "director_plan.json"
_DIRECTOR_PLAN_CACHE = {"mtime": 0.0, "payload": None, "loaded_at": 0.0}
_DIRECTOR_PLAN_CACHE_LOCK = threading.Lock()


# === Dashboard v2 health endpoint (Research + Skunkworks vetted spec; aesthetic-locked-in 2026-06-20) ===
#
# Single consolidated endpoint that returns all 8 elements + the top-of-page aggregate.
# Self-maintaining: every source updates as real work happens (Store mtime, heartbeats,
# watchdog state, fleet_waiting_on.md, git log of cert-pattern commits).
#
# Refresh discipline: each element's data freshness matches its source's update cadence;
# the frontend shows per-element age stamps so the user can see whether something is fresh
# or actually stale (vs. the v1 "looks fresh but stale" paradox).
_HEALTH_CACHE = {
    "substrate_trust": {"loaded_at": 0.0, "store_mtime": 0.0, "payload": None},  # 5min cache OR Store mtime
    "discipline_drift": {"loaded_at": 0.0, "payload": None},                      # 5min cache
}
_HEALTH_CACHE_LOCK = threading.Lock()
_FLEET_WAITING_PATH = _DATA_DIR / "fleet_waiting_on.md"
_REPO_ROOT = _DATA_DIR.parent
_SUBSTRATE_INDEX_DIR = _DATA_DIR / "substrate_index"
_EXPERIMENTS_DIR = _REPO_ROOT / "experiments"


def _substrate_index_latest_mtime() -> float:
    """Return the most-recent mtime across all Store partition files."""
    if not _SUBSTRATE_INDEX_DIR.is_dir():
        return 0.0
    latest = 0.0
    try:
        with os.scandir(_SUBSTRATE_INDEX_DIR) as it:
            for entry in it:
                try:
                    if entry.is_file():
                        m = entry.stat().st_mtime
                        if m > latest:
                            latest = m
                except OSError:
                    pass
    except OSError:
        pass
    return latest


def _compute_substrate_trust() -> dict:
    """Composition bar + sparkline + integrity light.

    Returns:
      {
        composition: {total, passes, bounds, custom, to_classify, pct_passes, pct_bounds, pct_custom},
        motion_7d: {labels: [d-6..d], passes_added: [...], demotes: [...], net: [...]},
        integrity: {status: 'OK'|'FLAGS', n_flags, detail},
        _source_mtime, _computed_at
      }
    """
    try:
        # Local import so the module-load doesn't depend on store availability
        import sys as _sys
        if str(_REPO_ROOT) not in _sys.path:
            _sys.path.insert(0, str(_REPO_ROOT))
        from backend.substrate_index.partition import PartitionedStore  # type: ignore
    except Exception as e:
        return {"error": f"Store import failed: {type(e).__name__}: {str(e)[:100]}"}

    src_mtime = _substrate_index_latest_mtime()
    now = time.time()

    # Cache by Store mtime (live truth: refresh ONLY when Store actually changes)
    cache = _HEALTH_CACHE["substrate_trust"]
    if cache["payload"] is not None and cache["store_mtime"] == src_mtime and (now - cache["loaded_at"]) < 600:
        return dict(cache["payload"], _cache_age_s=round(now - cache["loaded_at"], 1), _from_cache=True)

    try:
        ps = PartitionedStore(str(_SUBSTRATE_INDEX_DIR))
        all_atoms = list(ps.all_atoms())
    except Exception as e:
        return {"error": f"Store load failed: {type(e).__name__}: {str(e)[:200]}"}

    # === Composition bar (3 segments) ===
    pass_verdicts = {"PASS", "HARD_PASS"}
    bound_verdicts = {"MIDDLE_BAND", "HARD_FAIL"}
    # Anything else with pq=CERT_CHAIN_GRADE is a "custom-verdict characterization"
    passes = 0
    bounds = 0
    custom = 0
    no_verdict = 0
    for a in all_atoms:
        md = a.metadata or {}
        if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
            continue
        v = md.get("verdict")
        # Treat the long descriptive "HARD_PASS_chain_grade_*" variant as PASS too
        if v in pass_verdicts or (isinstance(v, str) and v.startswith("HARD_PASS")):
            passes += 1
        elif v in bound_verdicts:
            bounds += 1
        elif v is None or v == "":
            no_verdict += 1
        else:
            custom += 1
    total_chain_grade = passes + bounds + custom + no_verdict
    composition = {
        "total": total_chain_grade,
        "passes": passes,
        "bounds": bounds,
        "custom": custom,
        "no_verdict": no_verdict,
        "pct_passes": round(100.0 * passes / max(1, total_chain_grade), 1),
        "pct_bounds": round(100.0 * bounds / max(1, total_chain_grade), 1),
        "pct_custom": round(100.0 * (custom + no_verdict) / max(1, total_chain_grade), 1),
        "_label": f"{passes} PASSES + {bounds} bounds + {custom + no_verdict} custom = {total_chain_grade} chain-grade",
    }

    # === Motion sparkline (7 days; passes-added by cert_promoted_date if present) ===
    # Look for cert_promoted_date metadata; fall back to atom.id-implied recent activity.
    from collections import defaultdict
    from datetime import datetime as _dt, timedelta as _td
    today = _dt.utcnow().date()
    day_labels = [(today - _td(days=i)).isoformat() for i in range(6, -1, -1)]
    daily_passes = defaultdict(int)
    for a in all_atoms:
        md = a.metadata or {}
        if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
            continue
        v = md.get("verdict")
        if not (v in pass_verdicts or (isinstance(v, str) and v.startswith("HARD_PASS"))):
            continue
        date_str = md.get("cert_promoted_date") or md.get("atomized_date")
        if not isinstance(date_str, str):
            continue
        # Extract YYYY-MM-DD prefix
        ds = date_str[:10]
        if ds in day_labels:
            daily_passes[ds] += 1
    passes_series = [daily_passes.get(d, 0) for d in day_labels]
    # Demotes/reframes from git log: count commits matching demote/reframe patterns in last 7 days
    daily_demotes = defaultdict(int)
    daily_reframes = defaultdict(int)
    try:
        import subprocess as _sp
        out = _sp.check_output(
            ["git", "-C", str(_REPO_ROOT), "log", "--since=7.days.ago",
             "--pretty=format:%cs|%s"],
            timeout=8, text=True, errors="replace",
        )
        for ln in out.splitlines():
            if "|" not in ln:
                continue
            ds, subj = ln.split("|", 1)
            ds = ds.strip()
            if ds not in day_labels:
                continue
            sl = subj.lower()
            if "demote" in sl or "5mm" in sl:
                daily_demotes[ds] += 1
            if "reframe" in sl or "relabel" in sl:
                daily_reframes[ds] += 1
    except Exception:
        pass
    motion_7d = {
        "labels": day_labels,
        "passes_added": passes_series,
        "demotes": [daily_demotes.get(d, 0) for d in day_labels],
        "reframes": [daily_reframes.get(d, 0) for d in day_labels],
    }
    motion_7d["total_passes_added"] = sum(motion_7d["passes_added"])
    motion_7d["total_demotes"] = sum(motion_7d["demotes"])
    motion_7d["total_reframes"] = sum(motion_7d["reframes"])

    # === Integrity light: count chain-grade atoms with verdict-vs-pq inconsistency ===
    # Specifically: pq=CERT_CHAIN_GRADE but verdict=HARD_FAIL with honest_scope NOT mentioning bound/limit
    # (rough proxy for label-honesty drift). Plus: no_verdict atoms are flags.
    flags = []
    bound_keywords = ("bound", "negative", "limit", "ceiling", "envelope", "proven", "measured")
    for a in all_atoms:
        md = a.metadata or {}
        if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
            continue
        v = md.get("verdict")
        if v == "HARD_FAIL":
            scope = (md.get("honest_scope") or "").lower()
            if not any(k in scope for k in bound_keywords):
                flags.append(str(a.id))
                if len(flags) >= 20:
                    break
    integrity = {
        "status": "OK" if not flags and no_verdict == 0 else "FLAGS",
        "n_flags": len(flags) + no_verdict,
        "n_under_classified_hard_fail": len(flags),
        "n_no_verdict": no_verdict,
        "sample_flagged_atoms": flags[:5],
    }

    payload = {
        "composition": composition,
        "motion_7d": motion_7d,
        "integrity": integrity,
        "_source_mtime": src_mtime,
        "_computed_at": now,
        "_total_atoms": len(all_atoms),
    }
    with _HEALTH_CACHE_LOCK:
        cache["payload"] = payload
        cache["store_mtime"] = src_mtime
        cache["loaded_at"] = now
    return dict(payload, _cache_age_s=0.0, _from_cache=False)


def _compute_project_health() -> dict:
    """Fleet activity dots + USER-pending queue + in-flight 1-line."""
    now = time.time()

    # === Fleet activity per session (5 roles) ===
    roles = ["research", "exp_dev", "orchestrator", "skunkworks", "testbed"]
    fleet = {}
    notes_dir = _REPO_ROOT / "notes"
    for role in roles:
        # heartbeat age
        hb = _DATA_DIR / "heartbeats" / f"{role}.timestamp"
        hb_age = None
        if hb.exists():
            try:
                hb_age = now - hb.stat().st_mtime
            except OSError:
                pass
        # latest substantive outgoing note (exclude blocker_ping / watchdog / own status)
        latest_note_age = None
        latest_note_name = None
        if notes_dir.is_dir():
            try:
                with os.scandir(notes_dir) as it:
                    for e in it:
                        if not e.name.endswith(".md"):
                            continue
                        nl = e.name.lower()
                        if not nl.startswith(f"{role}_"):
                            continue
                        if "blocker_ping" in nl or "watchdog_ping" in nl:
                            continue
                        try:
                            m = e.stat().st_mtime
                            age = now - m
                            if latest_note_age is None or age < latest_note_age:
                                latest_note_age = age
                                latest_note_name = e.name
                        except OSError:
                            pass
            except OSError:
                pass
        # State: ALIVE (substantive event < 30min) / WORKING (heartbeat but no event)
        # / STALE (>30min) / DEAD (>2h)
        # We use the LATEST of {hb_age, latest_note_age} as the canonical liveness signal
        signal_age = None
        if hb_age is not None and latest_note_age is not None:
            signal_age = min(hb_age, latest_note_age)
        elif hb_age is not None:
            signal_age = hb_age
        elif latest_note_age is not None:
            signal_age = latest_note_age
        if signal_age is None:
            state = "unknown"
        elif latest_note_age is not None and latest_note_age < 1800:  # <30min substantive event
            state = "alive"
        elif hb_age is not None and hb_age < 1800:  # <30min heartbeat but no event
            state = "working"
        elif signal_age < 7200:  # <2h
            state = "stale"
        else:
            state = "dead"
        fleet[role] = {
            "state": state,
            "heartbeat_age_s": round(hb_age, 1) if hb_age is not None else None,
            "latest_substantive_note_age_s": round(latest_note_age, 1) if latest_note_age is not None else None,
            "latest_substantive_note": latest_note_name,
        }

    # === USER-pending queue from fleet_waiting_on.md ## USER-pending section ===
    user_pending = {"count": 0, "oldest_age_h": None, "top_items": [], "source_age_s": None}
    if _FLEET_WAITING_PATH.is_file():
        try:
            user_pending["source_age_s"] = round(now - _FLEET_WAITING_PATH.stat().st_mtime, 1)
            raw = _FLEET_WAITING_PATH.read_text(encoding="utf-8", errors="replace")
            in_section = False
            items = []
            for ln in raw.splitlines():
                if ln.strip().startswith("## "):
                    section = ln.strip()[3:].strip().lower()
                    in_section = section == "user-pending"
                    continue
                if in_section and ln.strip().startswith("- ") and "(nothing" not in ln.lower():
                    items.append(ln.strip().lstrip("- ").strip())
            user_pending["count"] = len(items)
            user_pending["top_items"] = items[:3]
        except OSError:
            pass

    # === In-flight: max-mtime across {Store, experiments/*/metrics.json, latest substantive note} ===
    in_flight_candidates = []
    src_mtime = _substrate_index_latest_mtime()
    if src_mtime > 0:
        in_flight_candidates.append({"source": "substrate_store", "mtime": src_mtime,
                                      "desc": "substrate atom mutation (Store partition write)"})
    if _EXPERIMENTS_DIR.is_dir():
        try:
            with os.scandir(_EXPERIMENTS_DIR) as it:
                for e in it:
                    if e.is_dir():
                        mp = Path(e.path) / "metrics.json"
                        if mp.exists():
                            try:
                                in_flight_candidates.append({
                                    "source": "experiment",
                                    "mtime": mp.stat().st_mtime,
                                    "desc": f"experiment metrics: {e.name}",
                                })
                            except OSError:
                                pass
        except OSError:
            pass
    # Latest non-watchdog non-blocker note across all roles
    if notes_dir.is_dir():
        try:
            with os.scandir(notes_dir) as it:
                latest_n_mtime = 0
                latest_n_name = None
                for e in it:
                    if not e.name.endswith(".md"):
                        continue
                    nl = e.name.lower()
                    if "blocker_ping" in nl or "watchdog_ping" in nl:
                        continue
                    try:
                        m = e.stat().st_mtime
                        if m > latest_n_mtime:
                            latest_n_mtime = m
                            latest_n_name = e.name
                    except OSError:
                        pass
                if latest_n_name:
                    in_flight_candidates.append({"source": "note", "mtime": latest_n_mtime,
                                                  "desc": f"note: {latest_n_name}"})
        except OSError:
            pass
    in_flight = {"desc": "(no recent activity)", "age_s": None}
    if in_flight_candidates:
        latest = max(in_flight_candidates, key=lambda c: c["mtime"])
        in_flight = {
            "desc": latest["desc"][:160],
            "source_type": latest["source"],
            "age_s": round(now - latest["mtime"], 1),
        }

    return {
        "fleet": fleet,
        "user_pending": user_pending,
        "in_flight": in_flight,
        "_computed_at": now,
    }


def _compute_discipline_and_drift() -> dict:
    """Discipline-catches today + 4 drift detectors. 5min cached."""
    now = time.time()
    cache = _HEALTH_CACHE["discipline_drift"]
    if cache["payload"] is not None and (now - cache["loaded_at"]) < 300:
        return dict(cache["payload"], _cache_age_s=round(now - cache["loaded_at"], 1))

    # === Discipline-catches today: count notes + commits matching patterns since 00:00 UTC today ===
    from datetime import datetime as _dt
    today_iso = _dt.utcnow().strftime("%Y-%m-%d")
    # Bug fix 2026-06-21: parse as UTC, not local time, so the start-of-day is
    # the correct UTC-midnight anchor. Prior `.strptime(...).timestamp()` treated
    # the parsed date as LOCAL -> on a TZ where UTC midnight is in the future
    # (e.g., US Pacific late evening), today_start landed in the future + the
    # entire day's notes were excluded (catches today = 0 despite real activity).
    from datetime import timezone as _tz
    today_start = _dt.strptime(today_iso, "%Y-%m-%d").replace(tzinfo=_tz.utc).timestamp()
    notes_dir = _REPO_ROOT / "notes"

    # Patterns -> categorize each catch.
    # 2026-06-21 coverage expansion: today's actual substantive work (cycle-driven
    # ships, certifications, refutations, redesigns, hidden-positive lifts) was
    # invisible to the prior narrow patterns. Broadened to capture the real classes:
    pattern_keywords = {
        "miscites": ["miscite", "phantom", "verify_referent", "verify_the_referent"],
        "demotes": ["demote", "_5mm_", "downgrade", "retract"],
        "META": ["meta_", "_meta_", "atomized", "atomize"],
        "label_honesty": ["worst_label", "label_honesty", "relabel"],
        "LEVER": ["lever_1_5", "lever1_5", "lever_4", "lever_2", "lever_3"],
        "drift_owned": ["own_my_verify", "verify_miss", "vet_miss", "verify_error",
                         "own_my", "self_catch", "selfcatch", "self-catch"],
        # NEW classes (cycle-driven + cert-cascade work was invisible before):
        "chain_grade_ship": ["chain_grade_eligible", "chaingrade", "build_go", "schema_vet_pass",
                              "landed_vet"],
        "cert_atomize": ["cert_588", "cert_589", "cert_590", "cert_591", "cert_592",
                          "cert_585", "cert_582", "cert_586", "cert_587"],
        "hidden_positive": ["hidden_positive", "hidden_positives", "buried_positive",
                             "negatives_drill"],
        "redesign": ["redesign", "amendment", "reframe"],
        "waiting_cycle": ["waiting_cycle", "waiting_on_cycle", "lull_probe", "productivity_probe"],
        "red_flag": ["red_flag", "red-alert", "_red_", "hold_chaingrade"],
    }
    catches_breakdown = {k: 0 for k in pattern_keywords}

    if notes_dir.is_dir():
        try:
            with os.scandir(notes_dir) as it:
                for e in it:
                    if not e.name.endswith(".md"):
                        continue
                    try:
                        m = e.stat().st_mtime
                        if m < today_start:
                            continue
                    except OSError:
                        continue
                    nl = e.name.lower()
                    if "blocker_ping" in nl or "watchdog_ping" in nl:
                        continue
                    for cat, kws in pattern_keywords.items():
                        if any(k in nl for k in kws):
                            catches_breakdown[cat] += 1
                            break  # one note -> one category
        except OSError:
            pass
    catches_total = sum(catches_breakdown.values())

    # === Drift detectors (4) ===
    detectors = []

    # D1. silent-monitor: heartbeat <30min BUT no substantive note in >2h
    silent = []
    roles = ["research", "exp_dev", "orchestrator", "skunkworks", "testbed"]
    for role in roles:
        hb = _DATA_DIR / "heartbeats" / f"{role}.timestamp"
        if not hb.exists():
            continue
        try:
            hb_age = now - hb.stat().st_mtime
        except OSError:
            continue
        if hb_age >= 1800:
            continue
        # Find latest substantive note for role
        latest_note_age = float("inf")
        if notes_dir.is_dir():
            try:
                with os.scandir(notes_dir) as it:
                    for e in it:
                        if not e.name.endswith(".md"):
                            continue
                        nl = e.name.lower()
                        if not nl.startswith(f"{role}_"):
                            continue
                        if "blocker_ping" in nl or "watchdog_ping" in nl:
                            continue
                        try:
                            age = now - e.stat().st_mtime
                            if age < latest_note_age:
                                latest_note_age = age
                        except OSError:
                            pass
            except OSError:
                pass
        if latest_note_age > 7200:  # >2h
            silent.append({"role": role, "heartbeat_age_s": round(hb_age, 1),
                           "latest_note_age_s": round(latest_note_age, 1)})
    detectors.append({
        "name": "silent-monitor",
        "status": "RED" if silent else "OK",
        "detail": f"{len(silent)} session(s) have fresh heartbeat but no substantive note in >2h" if silent else "all heartbeating sessions have recent substantive notes",
        "evidence": silent,
    })

    # D2. upward-bias-creep: CERT count UP today but discipline-catches=0
    # We approximate "CERT count UP today" by checking if any cert-related commit landed today.
    cert_commits_today = 0
    try:
        import subprocess as _sp
        out = _sp.check_output(
            ["git", "-C", str(_REPO_ROOT), "log", f"--since={today_iso} 00:00",
             "--pretty=format:%s"],
            timeout=5, text=True, errors="replace",
        )
        for ln in out.splitlines():
            sl = ln.lower()
            if any(k in sl for k in ("cert ", "cert_", "chain-grade", "atomize")):
                cert_commits_today += 1
    except Exception:
        pass
    bias_creep = cert_commits_today > 0 and catches_total == 0
    detectors.append({
        "name": "upward-bias-creep",
        "status": "RED" if bias_creep else "OK",
        "detail": f"{cert_commits_today} cert-related commits today; {catches_total} discipline-catches" + (" (alarm: cert grew without catches)" if bias_creep else ""),
        "evidence": {"cert_commits_today": cert_commits_today, "catches_today": catches_total},
    })

    # D3. plan-stall: priority in-progress in director_plan.json but no commit touching its cell in >6h
    # 2026-06-21 reframe-awareness: ALSO check for a reframe/relabel/redesign commit touching
    # the priority's id keywords or honest_claim in the last 6h. If found, the priority is
    # functionally active even though its `cell` field points at a now-stale path. Skip in
    # that case (or downgrade RED -> YELLOW evidence-only). Prevents the false-RED that
    # fired on phase4b post-reframe today (cell unchanged because reframe wrote to a
    # different path).
    plan_stalls = []
    plan_p = _DIRECTOR_PLAN_PATH
    if plan_p.is_file():
        try:
            plan = json.loads(plan_p.read_text(encoding="utf-8", errors="replace"))
            for pr in plan.get("priorities", []) if isinstance(plan, dict) else []:
                if pr.get("status") != "in-progress":
                    continue
                cell = pr.get("cell")
                if not isinstance(cell, str):
                    continue
                # Reframe-awareness: look for any commit in last 6h whose subject mentions
                # the priority id (e.g., "phase4b") OR matches reframe/relabel/redesign
                # patterns. If yes, skip the stall flag (priority is functionally active).
                pid_keyword = (pr.get("id") or "").split("_")[0].lower()  # e.g. "phase4b"
                try:
                    import subprocess as _sp
                    out = _sp.check_output(
                        ["git", "-C", str(_REPO_ROOT), "log", "--since=6.hours.ago",
                         "--pretty=format:%s"],
                        timeout=5, text=True, errors="replace",
                    )
                    reframe_found = False
                    if pid_keyword and len(pid_keyword) >= 4:
                        for ln in out.splitlines():
                            ll = ln.lower()
                            if pid_keyword in ll and any(k in ll for k in
                                ("reframe", "relabel", "redesign", "amendment", "demote",
                                 "atomize", "retract", "schemavet", "schema_vet")):
                                reframe_found = True
                                break
                    if reframe_found:
                        continue  # priority is functionally active via reframe; skip
                except Exception:
                    pass
                # Get last commit touching this path
                try:
                    import subprocess as _sp
                    out = _sp.check_output(
                        ["git", "-C", str(_REPO_ROOT), "log", "-1", "--format=%ct",
                         "--", cell.split(" ")[0]],
                        timeout=3, text=True, errors="replace",
                    ).strip()
                    if out:
                        last_commit_ts = float(out)
                        age_h = (now - last_commit_ts) / 3600.0
                        if age_h > 6:
                            plan_stalls.append({"priority_id": pr.get("id"), "cell": cell.split(" ")[0],
                                                 "hours_since_commit": round(age_h, 1)})
                except Exception:
                    pass
        except (OSError, json.JSONDecodeError):
            pass
    detectors.append({
        "name": "plan-stall",
        "status": "RED" if plan_stalls else "OK",
        "detail": f"{len(plan_stalls)} in-progress priorit(ies) with no cell-commit in >6h" if plan_stalls else "all in-progress priorities have recent cell-commits",
        "evidence": plan_stalls[:3],
    })

    # D4. user-pending-stale: fleet_waiting_on.md ## USER-pending mtime > 24h while substrate had mutations
    user_pending_stale = False
    user_pending_age_h = None
    if _FLEET_WAITING_PATH.is_file():
        try:
            fw_age_h = (now - _FLEET_WAITING_PATH.stat().st_mtime) / 3600.0
            user_pending_age_h = round(fw_age_h, 1)
            store_age_h = (now - _substrate_index_latest_mtime()) / 3600.0
            # Alarm if waiting-on is >24h stale AND Store has been touched in last 6h
            if fw_age_h > 24 and store_age_h < 6:
                user_pending_stale = True
        except OSError:
            pass
    detectors.append({
        "name": "user-pending-stale",
        "status": "RED" if user_pending_stale else "OK",
        "detail": f"fleet_waiting_on.md is {user_pending_age_h}h old while substrate is actively mutating" if user_pending_stale else f"fleet_waiting_on.md updated {user_pending_age_h}h ago (acceptable)",
        "evidence": {"fleet_waiting_age_h": user_pending_age_h},
    })

    # D5. fleet-section-stale: per-section staleness in fleet_waiting_on.md (catches a single
    # session's section rotting while others are fresh; the whole-file mtime misses it).
    # Parses ## <role> blocks + their **Last-updated:** UTC timestamp; flags any role section
    # >3h old. USER caught the gap 2026-06-21 (orchestrator section was 4h stale; my whole-
    # file detector didn't surface it).
    from datetime import datetime as _dt
    stale_sections = []
    if _FLEET_WAITING_PATH.is_file():
        try:
            raw = _FLEET_WAITING_PATH.read_text(encoding="utf-8", errors="replace")
            current_role = None
            for ln in raw.splitlines():
                ls = ln.strip()
                if ls.startswith("## ") and not ls.startswith("## USER"):
                    current_role = ls[3:].strip().lower()
                    if " " in current_role:  # take first word only
                        current_role = current_role.split()[0]
                elif current_role and ls.startswith("**Last-updated:**"):
                    # Extract YYYY-MM-DDTHH:MM:SSZ pattern
                    import re as _re
                    m_ = _re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z?", ls)
                    if m_:
                        try:
                            ts = _dt.strptime(m_.group(1), "%Y-%m-%dT%H:%M:%S")
                            age_h = (now - ts.timestamp()) / 3600.0
                            if age_h > 3:
                                stale_sections.append({"role": current_role, "age_h": round(age_h, 1)})
                        except ValueError:
                            pass
                    current_role = None  # reset; one Last-updated per section
        except OSError:
            pass
    detectors.append({
        "name": "fleet-section-stale",
        "status": "RED" if stale_sections else "OK",
        "detail": (f"{len(stale_sections)} section(s) >3h stale: " +
                   ", ".join(f"{s['role']}({s['age_h']}h)" for s in stale_sections)
                   if stale_sections else "all session sections updated <3h ago"),
        "evidence": stale_sections,
    })

    drift_summary = {
        "n_total": len(detectors),
        "n_red": sum(1 for d in detectors if d["status"] == "RED"),
        "all_ok": all(d["status"] == "OK" for d in detectors),
    }

    payload = {
        "catches_today": {
            "total": catches_total,
            "breakdown": catches_breakdown,
            "_date_utc": today_iso,
        },
        "drift_detectors": detectors,
        "drift_summary": drift_summary,
        "_computed_at": now,
    }
    with _HEALTH_CACHE_LOCK:
        cache["payload"] = payload
        cache["loaded_at"] = now
    return dict(payload, _cache_age_s=0.0)


@app.get("/api/dashboard/v2/health")
def dashboard_v2_health():
    """Consolidated v2 dashboard endpoint -- 8 elements + top-of-page aggregate.

    Per Research + Skunkworks vetted spec + USER aesthetic sign-off 2026-06-20.
    All data sources self-maintaining (Store mtime, heartbeats, watchdog, git log,
    fleet_waiting_on.md). No human discipline overhead to keep this fresh.
    """
    t0 = time.time()
    substrate_trust = _compute_substrate_trust()
    project_health = _compute_project_health()
    discipline_and_drift = _compute_discipline_and_drift()

    # Top-of-page aggregate: highest-attention-wins per status-page best practice
    aggregate_status = "OK"  # OK | WARN | ERROR
    aggregate_notes = []
    # Substrate trust contributions
    if isinstance(substrate_trust.get("integrity"), dict):
        if substrate_trust["integrity"].get("status") == "FLAGS":
            aggregate_status = "WARN" if aggregate_status == "OK" else aggregate_status
            aggregate_notes.append(f"{substrate_trust['integrity'].get('n_flags', 0)} cert-hygiene flags")
    # Project health contributions
    fleet_states = [s.get("state") for s in (project_health.get("fleet") or {}).values()]
    n_dead = fleet_states.count("dead")
    n_stale = fleet_states.count("stale")
    n_alive_or_working = fleet_states.count("alive") + fleet_states.count("working")
    if n_dead > 0:
        aggregate_status = "ERROR"
        aggregate_notes.append(f"{n_dead} session(s) DEAD")
    elif n_stale > 0:
        if aggregate_status == "OK":
            aggregate_status = "WARN"
        aggregate_notes.append(f"{n_stale} session(s) stale")
    # User pending escalation
    up = project_health.get("user_pending", {})
    if up.get("count", 0) > 0:
        aggregate_notes.append(f"{up['count']} USER-pending")
    # Drift detector escalation
    ds = discipline_and_drift.get("drift_summary", {})
    if ds.get("n_red", 0) > 0:
        aggregate_status = "ERROR"
        aggregate_notes.append(f"{ds['n_red']}/{ds['n_total']} drift detector(s) RED")
    # CERT summary
    comp = substrate_trust.get("composition", {}) if isinstance(substrate_trust, dict) else {}
    if comp.get("total"):
        aggregate_notes.insert(0, f"CERT {comp['total']}")
    # 7d net motion
    motion = substrate_trust.get("motion_7d", {}) if isinstance(substrate_trust, dict) else {}
    if motion.get("total_passes_added", 0) or motion.get("total_demotes", 0):
        aggregate_notes.append(f"7d: +{motion.get('total_passes_added', 0)} / -{motion.get('total_demotes', 0)}")

    aggregate = {
        "status": aggregate_status,
        "summary": " · ".join(aggregate_notes) if aggregate_notes else "no signals",
        "n_fleet_alive_or_working": n_alive_or_working,
        "n_fleet_total": len(fleet_states),
    }

    return {
        "ts": time.time(),
        "aggregate": aggregate,
        "substrate_trust": substrate_trust,
        "project_health": project_health,
        "discipline": {
            "catches_today": discipline_and_drift.get("catches_today"),
            "_cache_age_s": discipline_and_drift.get("_cache_age_s", 0),
        },
        "drift_detectors": discipline_and_drift.get("drift_detectors", []),
        "drift_summary": discipline_and_drift.get("drift_summary", {}),
        "_meta": {
            "compute_time_ms": round((time.time() - t0) * 1000, 1),
            "spec_reference": "notes/testbed_to_research_skunkworks_DASHBOARD_RETHINK_*.md + aesthetic spec 2026-06-20 + USER ratify",
        },
    }


@app.get("/api/director_plan")
def director_plan():
    """Serve the Director-maintained data/director_plan.json (mtime-invalidate cached).

    Per Research's URGENT dashboard build routing 2026-06-20 (Testbed-owned MVP stage 1):
    surfaces the canonical plan so USER can see current priorities + status + waiting_on
    without `cat data/director_plan.json`. Cert-atom resolution against the Store deferred
    to next MVP stage (Skunkworks's render-time-resolve refinement). For now: pass-through
    the file with mtime-invalidate cache (1s minimum re-read window) + per-priority
    `stale_after_h` computed convenience field (h since `last_updated_ts`).

    Returns the parsed JSON plus a `_dashboard_meta` block with cache age + file mtime.
    Returns 404-shaped JSON if the file doesn't exist (Director hasn't authored it).
    """
    p = _DIRECTOR_PLAN_PATH
    if not p.is_file():
        return JSONResponse(
            {"error": "director_plan.json not found",
             "_dashboard_meta": {"path": str(p), "exists": False}},
            status_code=404,
        )
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return JSONResponse({"error": "cannot stat director_plan.json"}, status_code=500)

    with _DIRECTOR_PLAN_CACHE_LOCK:
        cache_mtime = _DIRECTOR_PLAN_CACHE["mtime"]
        cache_payload = _DIRECTOR_PLAN_CACHE["payload"]
        cache_loaded_at = _DIRECTOR_PLAN_CACHE["loaded_at"]
        now = time.time()
        # Re-read only if file changed OR cache is older than 1s
        if cache_payload is None or mtime != cache_mtime or (now - cache_loaded_at) > 1.0:
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
                payload = json.loads(raw)
            except (OSError, json.JSONDecodeError) as e:
                return JSONResponse(
                    {"error": f"parse failed: {type(e).__name__}", "detail": str(e)[:200]},
                    status_code=500,
                )
            # Convenience: per-priority hours_since_update (h since last_updated_ts).
            # Doesn't touch the source file; computed for rendering only.
            for pr in payload.get("priorities", []) if isinstance(payload, dict) else []:
                ts_str = pr.get("last_updated_ts")
                if isinstance(ts_str, str):
                    try:
                        dt = datetime.fromisoformat(ts_str.rstrip("Z").rstrip("+00:00"))
                        age_h = (now - dt.timestamp()) / 3600.0
                        pr["_hours_since_update"] = round(age_h, 2)
                    except (ValueError, TypeError):
                        pr["_hours_since_update"] = None
            _DIRECTOR_PLAN_CACHE["mtime"] = mtime
            _DIRECTOR_PLAN_CACHE["payload"] = payload
            _DIRECTOR_PLAN_CACHE["loaded_at"] = now
            cache_payload = payload
            cache_loaded_at = now

    if isinstance(cache_payload, dict):
        cache_payload = dict(cache_payload)
        cache_payload["_dashboard_meta"] = {
            "path": str(p),
            "file_mtime": mtime,
            "cache_age_s": round(now - cache_loaded_at, 2),
            "served_at": now,
        }
    return cache_payload


_WATCHDOG_STATE_PATH = _DATA_DIR / "watchdog" / "state.json"


@app.get("/api/fleet_waiting_graph")
def fleet_waiting_graph():
    """Parse fleet_waiting_on.md sub-structured ### Waiting on entries into a
    dependency graph (X blocking Y). Per USER 2026-06-21 sub-structure v2.

    Format expected per Waiting-on item:
      - [from=<role>] [type=<schema_vet|landed_vet|build|cell_land|user_decision|reciprocal>] [filed=<UTC>] : <desc>

    Returns:
      {
        sessions: {<role>: {last_updated_ts, n_waiting_on, n_in_flight, steady_state: bool, recently_cleared: int}},
        edges: [{from: <role>, to: <role>, type: <type>, filed: <UTC>, age_h: <float>, desc: <str>}],
        blockers_by_role: {<role>: <n-times-blocking-others>}  # who has the most pending asks on them
      }
    """
    import re
    if not _FLEET_WAITING_PATH.is_file():
        return JSONResponse({"error": "fleet_waiting_on.md not found"}, status_code=404)
    now = time.time()
    raw = _FLEET_WAITING_PATH.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    sessions = {}
    edges = []
    blockers_by_role = {}
    current_role = None
    current_subsection = None
    iso_re = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z?")
    waiting_token_re = re.compile(
        r"\[from=([a-z_]+)\]\s*\[type=([a-z_]+)\](?:\s*\[filed=([^\]]+)\])?\s*:\s*(.*)",
        re.IGNORECASE,
    )
    from datetime import datetime as _dt, timezone as _tz
    for ln in lines:
        s = ln.strip()
        if s.startswith("## ") and not s.startswith("## USER"):
            current_role = s[3:].strip().lower().split()[0]
            current_subsection = None
            if current_role in ("research", "exp_dev", "orchestrator", "skunkworks", "testbed"):
                sessions.setdefault(current_role, {
                    "last_updated_ts": None,
                    "last_updated_age_h": None,
                    "n_waiting_on": 0,
                    "n_in_flight": 0,
                    "steady_state": False,
                    "n_recently_cleared": 0,
                })
        elif s.startswith("### ") and current_role and current_role in sessions:
            sub = s[4:].strip().lower()
            if "waiting on" in sub:
                current_subsection = "waiting_on"
            elif "in flight" in sub:
                current_subsection = "in_flight"
            elif "next 3" in sub or "next-3" in sub:
                current_subsection = "next_3"
            elif "steady" in sub:
                current_subsection = "steady_state"
                sessions[current_role]["steady_state"] = True
            elif "recently cleared" in sub or "cleared" in sub:
                current_subsection = "recently_cleared"
            else:
                current_subsection = None
        elif current_role and current_role in sessions and s.startswith("**Last-updated:**"):
            m = iso_re.search(s)
            if m:
                try:
                    ts = _dt.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=_tz.utc).timestamp()
                    sessions[current_role]["last_updated_ts"] = ts
                    sessions[current_role]["last_updated_age_h"] = round((now - ts) / 3600.0, 2)
                except ValueError:
                    pass
        elif current_role and current_role in sessions and current_subsection and (s.startswith("- ") or (current_subsection == "next_3" and s and s[0].isdigit())):
            if current_subsection == "waiting_on":
                sessions[current_role]["n_waiting_on"] += 1
                m = waiting_token_re.search(s)
                if m:
                    from_role = m.group(1).lower()
                    typ = m.group(2).lower()
                    filed = (m.group(3) or "").strip()
                    desc = (m.group(4) or "").strip()[:120]
                    age_h = None
                    if filed:
                        fm = iso_re.search(filed)
                        if fm:
                            try:
                                fts = _dt.strptime(fm.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=_tz.utc).timestamp()
                                age_h = round((now - fts) / 3600.0, 2)
                            except ValueError:
                                pass
                    edges.append({
                        "from": from_role,  # who CAN_PROVIDE the unblock
                        "to": current_role,  # who is BLOCKED waiting
                        "type": typ,
                        "filed": filed or None,
                        "age_h": age_h,
                        "desc": desc,
                    })
                    blockers_by_role[from_role] = blockers_by_role.get(from_role, 0) + 1
            elif current_subsection == "in_flight":
                sessions[current_role]["n_in_flight"] += 1
            elif current_subsection == "recently_cleared":
                sessions[current_role]["n_recently_cleared"] += 1

    return {
        "sessions": sessions,
        "edges": edges,
        "blockers_by_role": blockers_by_role,
        "_meta": {
            "source": str(_FLEET_WAITING_PATH),
            "computed_at": now,
            "n_edges": len(edges),
            "note": "Edges are 'who is blocking whom' -- `from` field = role that CAN unblock; `to` = role waiting.",
        },
    }


@app.get("/api/fleet_engagement")
def fleet_engagement():
    """Combine /api/sessions (heartbeats) + watchdog state.json + per-session activity counts.

    Per Research's URGENT dashboard build routing 2026-06-20 (Testbed-owned MVP stage 1):
    surfaces who-is-active so USER can see fleet engagement at a glance. All filesystem-
    derived; no Store touch; no new Director discipline.

    Output schema:
      {
        sessions: {<role>: {heartbeat_ts, age_s, watchdog_state, last_ping_ts, ping_age_s,
                            recent_outgoing_notes: [name,...], _now}},
        _dashboard_meta: {sources, served_at}
      }
    """
    snap = app.state.poller.get_snapshot()
    sessions = dict(snap.get("sessions", {}))  # don't mutate snapshot
    now = time.time()

    # Augment with watchdog state.json if present
    watchdog_state = {}
    if _WATCHDOG_STATE_PATH.is_file():
        try:
            wd_raw = _WATCHDOG_STATE_PATH.read_text(encoding="utf-8", errors="replace")
            wd_parsed = json.loads(wd_raw)
            if isinstance(wd_parsed, dict):
                last_pings = wd_parsed.get("last_ping", {})
                if isinstance(last_pings, dict):
                    for role, ts in last_pings.items():
                        if isinstance(ts, (int, float)):
                            watchdog_state[role] = {
                                "last_ping_ts": ts,
                                "ping_age_s": round(now - ts, 1),
                            }
        except (OSError, json.JSONDecodeError):
            pass

    # Per-session recent outgoing notes (top 3 most recent), filesystem mtime-derived
    notes_dir = _DATA_DIR.parent / "notes"
    recent_outgoing = {role: [] for role in ("research", "exp_dev", "orchestrator", "skunkworks", "testbed")}
    if notes_dir.is_dir():
        try:
            with os.scandir(notes_dir) as it:
                # Gather all notes per session-prefix
                buckets = {role: [] for role in recent_outgoing.keys()}
                for entry in it:
                    if not entry.name.endswith(".md"):
                        continue
                    name_lower = entry.name.lower()
                    for role in buckets.keys():
                        if name_lower.startswith(f"{role}_"):
                            try:
                                buckets[role].append((entry.stat().st_mtime, entry.name))
                            except OSError:
                                pass
                            break
                for role, items in buckets.items():
                    items.sort(reverse=True)
                    recent_outgoing[role] = [{"name": n, "age_s": round(now - m, 1)} for m, n in items[:3]]
        except OSError:
            pass

    # Combine
    combined = {}
    all_roles = set(sessions.keys()) | set(watchdog_state.keys()) | set(recent_outgoing.keys())
    for role in all_roles:
        entry = {}
        if role in sessions:
            entry.update(sessions[role])
        if role in watchdog_state:
            entry.update(watchdog_state[role])
        entry["recent_outgoing_notes"] = recent_outgoing.get(role, [])
        combined[role] = entry

    return {
        "sessions": combined,
        "_dashboard_meta": {
            "sources": {
                "heartbeats": "data/heartbeats/<role>.timestamp (via poller /api/sessions)",
                "watchdog": "data/watchdog/state.json",
                "recent_outgoing": "notes/<role>_*.md mtime-derived",
            },
            "served_at": now,
        },
    }


@app.get("/api/exp/{name}/tail")
def exp_tail(name: str, lines: int = 30):
    """On-demand fetch of an experiment's stdout log tail + metrics.json. Cached 60s."""
    import re as _re
    if not _re.match(r"^[A-Za-z0-9_\-]+$", name):
        return JSONResponse({"error": "invalid name"}, status_code=400)
    snap = app.state.poller.get_snapshot()
    exp = next((e for e in snap.get("experiments", []) if e.get("name") == name), None)
    if not exp:
        return JSONResponse({"error": "experiment not found"}, status_code=404)
    queue_dir = exp.get("queue_dir") or exp.get("queue")
    if queue_dir not in ("overnight_queue", "remote_cpu_queue"):
        return JSONResponse({"error": f"no queue_dir for this experiment (got {queue_dir!r})"}, status_code=400)
    text = app.state.poller.fetch_exp_log_tail(name, queue_dir, lines=max(5, min(200, lines)))
    metrics_raw = app.state.poller.fetch_exp_metrics(name)
    return {"name": name, "queue_dir": queue_dir, "tail": text, "metrics": metrics_raw}


@app.get("/api/in_flight")
def in_flight():
    """Current in-flight orchestrator sub-agent dispatches."""
    snap = app.state.poller.get_snapshot()
    return snap.get("in_flight", {"dispatches": []})


@app.get("/api/orchestrator_health")
def orchestrator_health():
    """Routing-ratio snapshot — orchestrator wrapper-routing discipline.

    Source: data/orchestrator_routing_ratio.json (written by
    tools/orchestrator/routing_ratio.py). Returns null fields if the
    snapshot hasn't been computed yet.

    Audit reference: notes/orchestrator_process_audit_2026-05-24.md #3.
    Target: routing_ratio >= 0.75.
    """
    snap = app.state.poller.get_snapshot()
    return snap.get("orchestrator_health") or {"primary": None, "by_window": None}


@app.get("/api/infra_flags")
def infra_flags():
    """Infrastructure alert flags written by orchestrator cron scripts.

    Per Director RATIFY 2026-06-17 18:43 (research_to_orchestrator_skunkworks
    _RATIFY_crons_C1_certgrade_ACK): wire .substrate_gate_fail +
    .index_coverage_gap + .coverage_gap + .backup_stale_alert into
    dashboard for unattended safety net.

    Each flag = file existence in data/. Returns true/false + last-modified
    + content preview (first 500 chars if present).
    """
    from pathlib import Path as _Path
    data_root = _Path(__file__).resolve().parents[2] / "data"
    flags = {
        "substrate_gate_fail": ".substrate_gate_fail",
        "index_coverage_gap": ".index_coverage_gap",
        "coverage_gap": ".coverage_gap",
        "backup_stale_alert": ".backup_stale_alert",
    }
    out = {}
    for k, fname in flags.items():
        p = data_root / fname
        if p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="replace")[:500]
            except Exception:
                content = ""
            try:
                mtime = p.stat().st_mtime
            except Exception:
                mtime = None
            out[k] = {"active": True, "modified_unix": mtime, "preview": content}
        else:
            out[k] = {"active": False, "modified_unix": None, "preview": ""}
    out["any_active"] = any(v["active"] for v in out.values() if isinstance(v, dict))
    return out


@app.get("/api/questions")
def questions():
    """Orchestrator open questions for the user (from orchestrator_questions.md)."""
    snap = app.state.poller.get_snapshot()
    return {"questions": snap.get("orchestrator_questions", []), "raw": snap.get("orchestrator_questions_raw", "")}


@app.get("/api/news")
def news():
    """News items: substantive status-log events that the user hasn't acked yet."""
    snap = app.state.poller.get_snapshot()
    return {"items": snap.get("news_items", [])}


# ---- POST endpoints: write side ----

class AckNewsBody(BaseModel):
    news_id: str


@app.post("/api/ack_news")
def ack_news(body: AckNewsBody):
    """Mark a news item as read. Appends to data/orchestrator_news_acks.jsonl.

    The poller picks the new ack up on its next cycle and filters it out of
    /api/news. Idempotent — repeated acks for the same id are harmless.
    """
    if not body.news_id or not isinstance(body.news_id, str):
        return JSONResponse({"error": "news_id required"}, status_code=400)
    # Light sanity check on id shape (16 hex chars from parsers.news_item_id).
    if len(body.news_id) > 64 or any(c.isspace() for c in body.news_id):
        return JSONResponse({"error": "invalid news_id"}, status_code=400)
    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "news_id": body.news_id,
    }
    try:
        _append_jsonl_atomic(_NEWS_ACKS_PATH, entry)
    except Exception as e:
        return JSONResponse({"error": f"write failed: {type(e).__name__}: {e}"}, status_code=500)
    return {"ok": True, "news_id": body.news_id, "ts": entry["ts"]}


class AnswerQuestionBody(BaseModel):
    question_number: int
    answer: str


@app.post("/api/answer_question")
def answer_question(body: AnswerQuestionBody):
    """User submits an answer to an open orchestrator question.

    Appends to data/orchestrator_answers.jsonl AND removes the question from
    data/orchestrator_questions.md. dispatch.py watches the .jsonl and emits
    a `user_answer` event so the orchestrator can process the answer as if the
    user said it in chat.
    """
    if not isinstance(body.question_number, int) or body.question_number < 1:
        return JSONResponse({"error": "question_number must be a positive integer"}, status_code=400)
    answer_text = (body.answer or "").strip()
    if not answer_text:
        return JSONResponse({"error": "answer cannot be empty"}, status_code=400)
    if len(answer_text) > 8000:
        return JSONResponse({"error": "answer too long (limit 8000 chars)"}, status_code=400)
    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "question_number": body.question_number,
        "answer": answer_text,
    }
    try:
        _append_jsonl_atomic(_ANSWERS_PATH, entry)
    except Exception as e:
        return JSONResponse({"error": f"answer write failed: {type(e).__name__}: {e}"}, status_code=500)
    removed = False
    try:
        removed = _remove_question_from_md(body.question_number)
    except Exception as e:
        # The answer is recorded; failing to remove the markdown is recoverable
        # — surface the error but report success on the write.
        return {
            "ok": True,
            "question_number": body.question_number,
            "ts": entry["ts"],
            "question_removed": False,
            "removal_error": f"{type(e).__name__}: {e}",
        }
    return {
        "ok": True,
        "question_number": body.question_number,
        "ts": entry["ts"],
        "question_removed": removed,
    }


@app.get("/api/snapshot")
def snapshot():
    """Full snapshot — used by the HTML frontend so one fetch refreshes all panes."""
    snap = app.state.poller.get_snapshot()
    return JSONResponse({**snap, "_health": app.state.poller.health()})


@app.get("/api/research_map")
def research_map():
    """Parsed research meta-map: tier counts, 110-row matrix, adjacency map, top drills."""
    from parsers import parse_research_map
    return JSONResponse(parse_research_map())


@app.get("/api/substrate_snapshot")
def substrate_snapshot():
    """Substrate snapshot for the Substrate 3D tab (TRACK D Phase 3).

    Reads data/substrate_snapshot.json (generated by
    tools/substrate_snapshot_extractor.py) and serves it as JSON. READ-ONLY;
    no substrate mutation. Returns 503 if the snapshot file is missing.
    """
    path = Path(r"D:/AI/hd-instrument/data/substrate_snapshot.json")
    if not path.is_file():
        return JSONResponse(
            {"error": "substrate_snapshot.json missing; run tools/substrate_snapshot_extractor.py"},
            status_code=503,
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return JSONResponse(
            {"error": f"snapshot read failed: {type(e).__name__}: {e}"},
            status_code=500,
        )
    return JSONResponse(payload)


@app.get("/api/substrate_state")
def substrate_state():
    """Substrate state aggregate for the Substrate tab (TRACK D Phase 4).

    Reads data/substrate_state.json (generated by
    tools/substrate_state_collector.py) and serves it as JSON. READ-ONLY.
    Returns 503 if the file is missing.
    """
    path = Path(r"D:/AI/hd-instrument/data/substrate_state.json")
    if not path.is_file():
        return JSONResponse(
            {"error": "substrate_state.json missing; run tools/substrate_state_collector.py"},
            status_code=503,
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return JSONResponse(
            {"error": f"state read failed: {type(e).__name__}: {e}"},
            status_code=500,
        )
    return JSONResponse(payload)


@app.get("/")
def root():
    # Force browsers to re-fetch the HTML on every navigation. Without this,
    # opened tabs cache the page heuristically and never pick up new JS/CSS
    # after we ship a fix -- which masks live bug-fixes as "still broken".
    # API responses are not cached because the JS already sends {cache:"no-store"}.
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
