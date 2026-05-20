"""Patch the healer to surface verdict gaps (completions without outcome events)."""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\tools\healer_v2.py")
src = p.read_text()

# Add the surface function before run_iteration
old_func = "def heal_inconclusive(q: dict) -> int:"
new_block = '''def surface_verdict_gaps() -> int:
    """Find completed/inconclusive/failed entries that have no experiment_outcome event yet.
    Writes data/needs_verdict.json with the list. Returns count."""
    events_path = REPO / "data" / "session_events.jsonl"
    seen = set()
    if events_path.exists():
        try:
            for line in events_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "experiment_outcome":
                    seen.add(e.get("name"))
        except (OSError, PermissionError):
            log("  surface: could not read session_events.jsonl; skipping gap scan")
            return 0
    gaps = []
    terminal = {"completed", "inconclusive", "failed"}
    for queue_name in QUEUES:
        q = read_queue(queue_name)
        if q is None:
            continue
        for e in q["experiments"]:
            if e.get("status") in terminal and e["name"] not in seen:
                gaps.append({
                    "name": e["name"],
                    "queue": queue_name,
                    "status": e.get("status"),
                    "ended_at": e.get("ended_at"),
                    "has_metrics": metrics_exists_with_content(e["name"]),
                })
    surface_path = REPO / "data" / "needs_verdict.json"
    surface_path.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "count": len(gaps),
        "gaps": gaps,
    }, indent=2))
    if gaps:
        log(f"  SURFACE: {len(gaps)} terminal entries without outcome events")
    return len(gaps)


def heal_inconclusive(q: dict) -> int:'''

if old_func in src and "def surface_verdict_gaps" not in src:
    src = src.replace(old_func, new_block)
    print("Added surface_verdict_gaps function")

# Add the call to run_iteration
old_iter_end = '''    return total_actions


def main():'''

new_iter_end = '''    # Surface gaps without making changes
    surface_verdict_gaps()
    return total_actions


def main():'''

if old_iter_end in src and "surface_verdict_gaps()" not in src.split("def main")[0]:
    src = src.replace(old_iter_end, new_iter_end)
    print("Wired surface_verdict_gaps into run_iteration")

p.write_text(src)
print(f"Wrote {p}")
