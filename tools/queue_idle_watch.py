"""queue_idle_watch.py — emit QUEUE_IDLE events to stdout for Monitor consumption.

Polls runner_status.py --remote every 60s. Emits ONE line per state-change:
- "QUEUE_IDLE: <queue> | depth=0 | idle_min=N | DISPATCH_NOW" when queue first becomes idle past threshold
- Re-emits at escalating intervals (5, 15, 30, 60 min) while still idle
- "QUEUE_RECOVERED: <queue>" when queue gets work again

Run via Monitor tool to surface events as task-notifications.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

POLL_INTERVAL_S = 60
ESCALATION_MINUTES = [5, 15, 30, 60, 120]
RUNNER_STATUS_TOOL = Path(__file__).parent / "runner_status.py"


def get_queue_state() -> dict[str, dict]:
    """Run runner_status.py --remote and parse QUEUE STATE section."""
    try:
        result = subprocess.run(
            [sys.executable, str(RUNNER_STATUS_TOOL), "--remote"],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {}

    state = {}
    section = False
    for line in result.stdout.splitlines():
        if "=== QUEUE STATE ===" in line:
            section = True
            continue
        if section and line.startswith("==="):
            section = False
            continue
        if section:
            m = re.match(r"\s*(\S+):\s+(\d+)\s+running\s+\+\s+(\d+)\s+pending", line)
            if m:
                queue, running, pending = m.group(1), int(m.group(2)), int(m.group(3))
                state[queue] = {"running": running, "pending": pending}
    return state


def main():
    sys.stdout.write("QUEUE-IDLE-WATCH-ARMED: 60s poll; escalation 5/15/30/60/120min\n")
    sys.stdout.flush()

    last_emit_min: dict[str, int] = {}
    idle_since: dict[str, float] = {}

    while True:
        now = time.time()
        state = get_queue_state()

        if not state:
            time.sleep(POLL_INTERVAL_S)
            continue

        for queue, depths in state.items():
            total = depths["running"] + depths["pending"]
            if total == 0:
                if queue not in idle_since:
                    idle_since[queue] = now
                idle_min = (now - idle_since[queue]) / 60
                next_threshold = next(
                    (m for m in ESCALATION_MINUTES if m > last_emit_min.get(queue, -1) and m <= idle_min),
                    None,
                )
                if next_threshold is not None:
                    sys.stdout.write(
                        f"QUEUE_IDLE: {queue} | depth=0 | idle_min={idle_min:.0f} | DISPATCH_NOW\n"
                    )
                    sys.stdout.flush()
                    last_emit_min[queue] = next_threshold
            else:
                if queue in idle_since:
                    sys.stdout.write(
                        f"QUEUE_RECOVERED: {queue} | running={depths['running']} pending={depths['pending']}\n"
                    )
                    sys.stdout.flush()
                    del idle_since[queue]
                    last_emit_min.pop(queue, None)

        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
