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
