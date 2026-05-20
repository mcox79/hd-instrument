"""Add the missing threading.Thread spawn for heartbeat in main()."""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\experiments\run_overnight_queue.py")
src = p.read_text()
if "threading.Thread(target=_heartbeat_loop" in src:
    print("Already patched")
else:
    # Find the main() function and inject the thread spawn at its start
    old = 'def main() -> None:\n    log("============================================")'
    new = 'def main() -> None:\n    threading.Thread(target=_heartbeat_loop, daemon=True).start()\n    log("============================================")'
    if old in src:
        src = src.replace(old, new)
        p.write_text(src)
        print("Injected heartbeat thread spawn into main()")
    else:
        print("WARN: could not find main() entry point")
