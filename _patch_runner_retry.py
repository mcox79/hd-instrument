"""Patch run_overnight_queue.py: add retry-on-PermissionError to read_queue + write_queue."""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\experiments\run_overnight_queue.py")
src = p.read_text()

old_read = '''def read_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"experiments": []}
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"Queue file unreadable ({e}); waiting for next poll")
        return {"experiments": []}'''

new_read = '''def read_queue() -> dict:
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

old_write = '''def write_queue(q: dict) -> None:
    QUEUE_FILE.write_text(json.dumps(q, indent=2))'''

new_write = '''def write_queue(q: dict) -> None:
    for attempt in range(8):
        try:
            QUEUE_FILE.write_text(json.dumps(q, indent=2))
            return
        except PermissionError:
            time.sleep(0.25 * (attempt + 1))
    log("Queue file locked for write after 8 retries; skipping update this cycle")'''

if old_read not in src:
    print("ERROR: read_queue pattern not found (already patched?)")
elif old_write not in src:
    print("ERROR: write_queue pattern not found")
else:
    src2 = src.replace(old_read, new_read).replace(old_write, new_write)
    p.write_text(src2)
    print(f"Patched {p}: {len(src)} -> {len(src2)} bytes")
