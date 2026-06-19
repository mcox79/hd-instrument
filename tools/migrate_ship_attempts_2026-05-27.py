"""One-shot migration for data/recent_ship_attempts.jsonl.

Context (2026-05-27)
--------------------
heartbeat_watchdog had two layered bugs causing perpetual false-positive
`ship_unconfirmed` events:

  1. queue_add.sh wrote `attempted_at` as a naive ISO-8601 string (no `Z`).
     `datetime.fromisoformat` parsed that as naive, and `.timestamp()`
     reinterpreted it as LOCAL time on the watchdog host, inflating ages
     by the local UTC offset.

  2. `_is_confirmed` checked recent_verdicts but the sentinel-pruning loop
     in evaluate_ship_unconfirmed never stamped `landed_at` early enough
     to prevent the cooldown loop from re-firing on entries that had
     already completed.

queue_add.sh and heartbeat_watchdog.py are fixed in the same commit. This
script cleans the legacy backlog so the next watchdog cycle does not see
hours-old "unconfirmed" sentinels that actually completed long ago.

Actions per entry:
  * If `name` appears in remote_state_cache.recent_verdicts, stamp
    `landed_at = verdict.ended_at`.
  * If `attempted_at` is naive (no `Z`), rewrite as `attempted_at + "Z"`.
  * Drop entries whose age (now-UTC minus attempted-UTC) exceeds
    SHIP_CONFIRMED_RETENTION_S (600s).

Atomic write (.tmp + os.replace).  Safe to run while watchdog is live —
worst case the watchdog reads an intermediate state and re-derives on the
next 30s cycle.

Run once.  File is kept in the repo for audit (do not delete).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SENTINEL = REPO / "data" / "recent_ship_attempts.jsonl"
CACHE = REPO / "data" / "remote_state_cache.json"
RETENTION_S = 600.0


def parse_iso_utc(s: str) -> datetime | None:
    """Parse ISO-8601; assume UTC if naive. Returns None on failure."""
    if not isinstance(s, str) or not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def main() -> int:
    if not SENTINEL.is_file():
        print(f"[migrate] sentinel not found: {SENTINEL}")
        return 0

    # Load verdict map: name -> ended_at (ISO string, as found in cache)
    verdict_ended_by_name: dict[str, str] = {}
    if CACHE.is_file():
        try:
            doc = json.loads(CACHE.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            print(f"[migrate] WARN: cache unreadable: {e}")
            doc = {}
        rv = doc.get("recent_verdicts") or []
        if isinstance(rv, list):
            for v in rv:
                if not isinstance(v, dict):
                    continue
                vn = v.get("name")
                ended = v.get("ended_at")
                if isinstance(vn, str) and isinstance(ended, str):
                    verdict_ended_by_name[vn] = ended
        print(f"[migrate] loaded {len(verdict_ended_by_name)} verdicts from cache")
    else:
        print(f"[migrate] WARN: cache not found: {CACHE}")

    # Read sentinel.
    raw_lines = SENTINEL.read_text(encoding="utf-8", errors="replace").splitlines()
    entries: list[dict] = []
    for ln in raw_lines:
        s = ln.strip()
        if not s:
            continue
        try:
            entries.append(json.loads(s))
        except Exception:
            # Malformed line; preserve as-is by skipping (drop).
            continue

    print(f"[migrate] read {len(entries)} entries from sentinel")

    now_utc = datetime.now(timezone.utc)
    kept: list[dict] = []
    dropped = 0
    stamped = 0
    tz_rewrites = 0

    for att in entries:
        name = att.get("name")
        attempted_at = att.get("attempted_at") or att.get("ts")
        if not isinstance(name, str) or not isinstance(attempted_at, str):
            dropped += 1
            continue

        # Normalize attempted_at to include Z if naive.
        had_tz = attempted_at.endswith("Z") or "+" in attempted_at[10:] or attempted_at.endswith("00")
        # The above heuristic is loose; use parse to be safe.
        dt = parse_iso_utc(attempted_at)
        if dt is None:
            dropped += 1
            continue
        normalized_iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        if normalized_iso != attempted_at:
            att = dict(att)
            att["attempted_at"] = normalized_iso
            # Keep ts in sync if it matched the old attempted_at.
            if att.get("ts") == attempted_at or att.get("ts") and parse_iso_utc(att["ts"]) == dt:
                att["ts"] = normalized_iso
            tz_rewrites += 1

        age_s = (now_utc - dt).total_seconds()

        # Stamp landed_at from verdict cache if applicable.
        if name in verdict_ended_by_name and not att.get("landed_at"):
            ended = verdict_ended_by_name[name]
            # Normalize ended_at to UTC Z form for consistency.
            ended_dt = parse_iso_utc(ended)
            if ended_dt is not None:
                att = dict(att)
                att["landed_at"] = ended_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                stamped += 1

        # Drop if past retention.
        if age_s > RETENTION_S:
            dropped += 1
            continue

        kept.append(att)

    # Atomic write.
    tmp = SENTINEL.with_suffix(SENTINEL.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for k in kept:
            fh.write(json.dumps(k, separators=(",", ":")) + "\n")
    os.replace(tmp, SENTINEL)

    print(
        f"[migrate] result: kept={len(kept)} dropped={dropped} "
        f"landed_at_stamped={stamped} tz_rewrites={tz_rewrites}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
