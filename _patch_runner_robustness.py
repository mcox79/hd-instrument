"""Patch run_overnight_queue.py with:
1. Background heartbeat thread (writes every 30s regardless of subprocess state)
2. Dedupe-on-read in read_queue
3. Inconclusive-not-failed when exit=0 but metrics.json missing/empty
"""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\experiments\run_overnight_queue.py")
src = p.read_text()

# ===== Add threading import if not present =====
if "import threading" not in src:
    src = src.replace("import json", "import json\nimport threading", 1)

# ===== Add heartbeat thread infra =====
old_hb = '''def heartbeat(status: str, current: str | None = None) -> None:
    """Write a heartbeat file so external observers can verify the runner is alive."""
    HEARTBEAT_FILE.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "current": current,
        "pid": str(__import__("os").getpid()),
    }, indent=2))'''

new_hb = '''_HB_STATE = {"status": "idle", "current": None, "stop": False}


def heartbeat(status: str, current: str | None = None) -> None:
    """Write a heartbeat file so external observers can verify the runner is alive."""
    _HB_STATE["status"] = status
    _HB_STATE["current"] = current
    _write_heartbeat()


def _write_heartbeat() -> None:
    try:
        HEARTBEAT_FILE.write_text(json.dumps({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "status": _HB_STATE["status"],
            "current": _HB_STATE["current"],
            "pid": str(__import__("os").getpid()),
        }, indent=2))
    except OSError:
        pass  # transient file lock; next tick will retry


def _heartbeat_loop():
    """Background thread: refresh heartbeat every 30s regardless of subprocess state."""
    while not _HB_STATE["stop"]:
        _write_heartbeat()
        time.sleep(30)'''

if old_hb in src:
    src = src.replace(old_hb, new_hb)
    print("Added heartbeat thread infra.")

# ===== Add dedupe-on-read in read_queue =====
old_read = '''def read_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"experiments": []}
    for attempt in range(8):
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log(f"Queue file unreadable ({e}); waiting for next poll")
            return {"experiments": []}
        except PermissionError:
            time.sleep(0.25 * (attempt + 1))
    log("Queue file locked after 8 retries; treating as empty for this poll")
    return {"experiments": []}'''

new_read = '''def read_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"experiments": []}
    raw = None
    for attempt in range(8):
        try:
            raw = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            break
        except json.JSONDecodeError as e:
            log(f"Queue file unreadable ({e}); waiting for next poll")
            return {"experiments": []}
        except PermissionError:
            time.sleep(0.25 * (attempt + 1))
    if raw is None:
        log("Queue file locked after 8 retries; treating as empty for this poll")
        return {"experiments": []}
    # Dedupe by name. Status preference: completed/inconclusive > failed > running > pending.
    pref = {"completed": 5, "inconclusive": 5, "failed": 4, "running": 3, "pending": 2}
    seen = set()
    deduped = []
    by_name_best = {}
    for e in raw["experiments"]:
        name = e["name"]
        existing = by_name_best.get(name)
        if existing is None or pref.get(e.get("status"), 0) > pref.get(existing.get("status"), 0):
            by_name_best[name] = e
    for e in raw["experiments"]:
        if e["name"] in seen:
            continue
        seen.add(e["name"])
        deduped.append(by_name_best[e["name"]])
    if len(deduped) != len(raw["experiments"]):
        log(f"Dedupe: collapsed {len(raw['experiments'])} entries -> {len(deduped)} unique names")
    return {"experiments": deduped}'''

if old_read in src:
    src = src.replace(old_read, new_read)
    print("Added dedupe-on-read.")

# ===== Inconclusive-not-failed when exit=0 but no metrics.json =====
old_done_block = '''log(f"DONE {name} in {dt:.1f}s (exit 0)")
        record_outcome(0)'''

new_done_block = '''log(f"DONE {name} in {dt:.1f}s (exit 0)")
        # Verify metrics.json exists; if not, mark inconclusive (not completed)
        metrics_path = REPO / "data" / f"exp_{name}" / "metrics.json"
        if not (metrics_path.exists() and metrics_path.stat().st_size > 100):
            log(f"WARN: {name} exited 0 but metrics.json missing/empty; marking inconclusive")
            update_entry(name, status="inconclusive",
                         ended_at=datetime.now().isoformat(timespec="seconds"),
                         wall_s=dt, note="exit=0 but no metrics.json output")
            record_outcome(0)
            return "inconclusive"
        record_outcome(0)'''

if old_done_block in src:
    src = src.replace(old_done_block, new_done_block)
    print("Added inconclusive-vs-completed distinction.")

# ===== Spawn background heartbeat thread in main =====
old_main_start = '''def main() -> None:'''
new_main_start = '''def main() -> None:
    threading.Thread(target=_heartbeat_loop, daemon=True).start()'''
# only patch if no thread spawn yet
if "_heartbeat_loop" not in src.split("def main")[1] if "def main" in src else False:
    pass  # already patched
elif new_main_start not in src:
    src = src.replace(old_main_start, new_main_start)
    print("Added background heartbeat thread spawn in main().")

p.write_text(src)
print(f"Wrote {p}")
