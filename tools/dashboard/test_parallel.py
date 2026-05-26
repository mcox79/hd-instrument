"""Smoke test for the Phase 2 stack: run the poller _poll_once and print the snapshot."""

from __future__ import annotations

import json
import time

from poller import Poller


def main() -> None:
    p = Poller()
    t0 = time.perf_counter()
    p._poll_once()
    dt = (time.perf_counter() - t0) * 1000.0
    p.close()

    snap = p.get_snapshot()
    print(f"=== timing ===")
    print(f"_poll_once: {dt:.1f} ms")
    print()
    print("=== system ===")
    print(json.dumps(snap.get("system", {}), indent=2))
    print()
    print("=== runs ===")
    print(json.dumps(snap.get("runs", {}), indent=2))
    print()
    print("=== queue counts + first 3 pending ===")
    for label, q in snap.get("queue", {}).items():
        pending = q.get("pending", [])
        print(f"  [{label}] counts={q.get('counts')}")
        for p_ in pending[:3]:
            print(f"    pending: {p_.get('name')} ({p_.get('status')})")
        if len(pending) > 3:
            print(f"    ... +{len(pending)-3} more")
    print()
    print("=== history (most recent 8) ===")
    for ev in snap.get("history", [])[:8]:
        print(f"  [{ev['ts']}] [{ev['queue']}] {ev['event']:5s} {ev['name']}"
              + (f"  wall={ev['wall_s']}s exit={ev['exit_code']}" if ev.get('wall_s') is not None else ""))


if __name__ == "__main__":
    main()
