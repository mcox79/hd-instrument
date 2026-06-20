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
