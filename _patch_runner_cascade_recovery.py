"""Patch run_overnight_queue.py with cascade-failure detection + OS recovery sleep.

If 3+ consecutive experiments fail with the same exit code, sleep 5 min to let
OS recover from shared-state corruption (the failure mode observed 2026-05-20 01:30).
"""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\experiments\run_overnight_queue.py")
src = p.read_text()

# Locate the main loop's failure-handling region
old_tail = '''def main():
    log("============================================")
    log("Overnight queue runner started")
    log(f"Repo: {REPO}")
    log(f"Queue file: {QUEUE_FILE}")'''

new_main_prelude = '''CASCADE_THRESHOLD = 3       # consecutive same-exit failures trigger recovery
CASCADE_SLEEP_S = 300       # 5 min OS-recovery sleep


def main():
    log("============================================")
    log("Overnight queue runner started")
    log(f"Repo: {REPO}")
    log(f"Queue file: {QUEUE_FILE}")'''

if old_tail in src:
    src = src.replace(old_tail, new_main_prelude)

# Add cascade-tracking to the loop. Look for the run_one call.
old_run = '''            status = run_one(next_entry)
            log(f"DONE {next_entry['name']} -> {status}" if status not in ("failed",) else f"FAIL pattern: {status}")'''

# This may not match exactly; alternative is to find the run_one + update_entry section.
# Instead: patch update_entry to take exit_code, and track cascade in main.
# Use a simpler injection: add after the line that calls run_one with the result.

# Strategy: inject a class-level tracker AFTER the heartbeat function.
old_hb_close = '''def heartbeat(status: str, current: str | None = None) -> None:
    """Write a heartbeat file so external observers can verify the runner is alive."""
    HEARTBEAT_FILE.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "current": current,
        "pid": str(__import__("os").getpid()),
    }, indent=2))'''

cascade_funcs = '''def heartbeat(status: str, current: str | None = None) -> None:
    """Write a heartbeat file so external observers can verify the runner is alive."""
    HEARTBEAT_FILE.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "current": current,
        "pid": str(__import__("os").getpid()),
    }, indent=2))


_CASCADE_STATE = {"consecutive_fails": 0, "last_exit": None}
CASCADE_THRESHOLD = 3
CASCADE_SLEEP_S = 300


def record_outcome(exit_code: int) -> None:
    """Track consecutive failures with same exit code. Sleep if cascade detected."""
    if exit_code == 0:
        _CASCADE_STATE["consecutive_fails"] = 0
        _CASCADE_STATE["last_exit"] = None
        return
    if exit_code == _CASCADE_STATE["last_exit"]:
        _CASCADE_STATE["consecutive_fails"] += 1
    else:
        _CASCADE_STATE["consecutive_fails"] = 1
        _CASCADE_STATE["last_exit"] = exit_code
    if _CASCADE_STATE["consecutive_fails"] >= CASCADE_THRESHOLD:
        log(f"CASCADE detected: {_CASCADE_STATE['consecutive_fails']} consecutive failures with exit={exit_code}. Sleeping {CASCADE_SLEEP_S}s for OS recovery.")
        heartbeat("cascade_recovery", current=f"exit={exit_code}")
        time.sleep(CASCADE_SLEEP_S)
        _CASCADE_STATE["consecutive_fails"] = 0
        _CASCADE_STATE["last_exit"] = None
        log("Cascade recovery sleep done; resuming.")'''

if old_hb_close in src:
    src = src.replace(old_hb_close, cascade_funcs)

# Now patch run_one to call record_outcome with the actual exit code
old_run_one_tail = '''    log(f"DONE {name} in {wall_s:.1f}s (exit {result.returncode})")
    update_entry(name, status=final_status, ended_at=datetime.now().isoformat(timespec="seconds"), wall_s=wall_s)
    return final_status'''

# Use a less brittle pattern; find the return final_status pattern
import re
# Locate "return final_status" line and inject before it
new_run_one_tail = '''    log(f"DONE {name} in {wall_s:.1f}s (exit {result.returncode})")
    update_entry(name, status=final_status, ended_at=datetime.now().isoformat(timespec="seconds"), wall_s=wall_s)
    record_outcome(result.returncode)
    return final_status'''

if old_run_one_tail in src:
    src = src.replace(old_run_one_tail, new_run_one_tail)
    print("Patched run_one with record_outcome.")
else:
    # Try alternative match
    pattern = re.compile(r"(update_entry\(name, status=final_status[^)]+\))\s*\n(\s+)return final_status", re.MULTILINE)
    m = pattern.search(src)
    if m:
        replacement = m.group(1) + f"\n{m.group(2)}record_outcome(result.returncode)\n{m.group(2)}return final_status"
        src = src[:m.start()] + replacement + src[m.end():]
        print("Patched run_one via regex.")
    else:
        print("WARNING: could not find run_one tail; patch incomplete.")

p.write_text(src)
print(f"Wrote {p}")
