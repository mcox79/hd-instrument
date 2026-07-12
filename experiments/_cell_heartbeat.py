"""Cell heartbeat helper (testbed observability deliverable 2; 2026-06-28).

Replaces the inline _heartbeat() snippet in exp_dev.md §13.D so cells get the
schema right by default. Older cells get retrofitted opportunistically; new
cells should import this from `experiments/_cell_heartbeat.py`.

Schema (one JSONL row per heartbeat):
    {
      "ts_iso": "2026-06-28T17:45:23Z",   # UTC; matches runner heartbeat ts_iso
      "unit_idx": 12,                      # 0-based current unit/seed/chunk
      "total_units": 100,                  # None if cell does not know total
      "elapsed_s": 433.21,                 # since main() start
      "extra": {...}                       # optional per-cell context
    }

Atomic-write is NOT used here: heartbeats are append-only and individual rows
are small enough (<256B typically) that POSIX/NTFS append is effectively atomic
for the consumer (runner_status.py reads with errors="replace" + tolerates
trailing partial rows by skipping json.loads failures).

Usage (cell-side):
    from experiments._cell_heartbeat import emit_heartbeat, CellHeartbeat

    # functional form (cell knows its own elapsed_s):
    emit_heartbeat(output_dir, unit_idx=i, total_units=N,
                   elapsed_s=time.perf_counter() - t0)

    # context-manager form (auto-elapsed; cadence-throttled):
    with CellHeartbeat(output_dir, total_units=N, interval_s=30) as hb:
        for i in range(N):
            ...work...
            hb.tick(i, extra={"loss": float(loss)})

Cadence guidance per exp_dev.md §13.D: emit every N units (default 5) OR
every 60s, whichever is sooner. The CellHeartbeat context manager handles
this throttling internally (interval_s default 30s).
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso_utc() -> str:
    """UTC ISO8601 with trailing Z. Matches runner_v2_prod.py format exactly
    so runner_status.py can compute age deltas without timezone gymnastics."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit_heartbeat(
    output_dir: str | os.PathLike,
    unit_idx: int,
    elapsed_s: float,
    total_units: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Append one heartbeat row to {output_dir}/_heartbeat.jsonl.

    Best-effort: any OSError is swallowed (a missing heartbeat must NEVER kill
    a running cell). The runner watchdog interprets absence-of-heartbeat as
    a zombie signal; that is correct behavior, not something to retry around.
    """
    row = {
        "ts_iso": _now_iso_utc(),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        # Mode "a" + write-and-close per row so a hung child cell still has its
        # last-known progress on disk for runner_status.py to read.
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


class CellHeartbeat:
    """Context manager + tick() for cadence-throttled heartbeats.

    interval_s: minimum seconds between heartbeats (default 30; matches the
    runner heartbeat half-cycle so cell-progress lag is bounded by ~45s
    worst-case).

    every_n_units: also emit when unit_idx advances by this many since the
    last heartbeat, even if interval_s has not elapsed (catches short-fast
    cells; default 5 per exp_dev.md §13.D).
    """

    def __init__(
        self,
        output_dir: str | os.PathLike,
        total_units: int | None = None,
        interval_s: float = 30.0,
        every_n_units: int = 5,
    ) -> None:
        self.output_dir = output_dir
        self.total_units = total_units
        self.interval_s = float(interval_s)
        self.every_n_units = int(every_n_units)
        self._t0: float | None = None
        self._last_emit_t: float = 0.0
        self._last_emit_idx: int = -10**9

    def __enter__(self) -> "CellHeartbeat":
        self._t0 = time.perf_counter()
        self._last_emit_t = 0.0
        self._last_emit_idx = -10**9
        # Emit a unit_idx=0 boot heartbeat so absence-vs-cold-start is
        # disambiguated even for cells that haven't reached tick() yet.
        emit_heartbeat(self.output_dir, unit_idx=0, elapsed_s=0.0,
                       total_units=self.total_units,
                       extra={"event": "cell_heartbeat_boot"})
        return self

    def tick(self, unit_idx: int, extra: dict[str, Any] | None = None,
             force: bool = False) -> None:
        """Maybe-emit a heartbeat based on cadence rules.

        force=True bypasses throttling (use at phase boundaries / before long
        sub-operations / on completion of any final unit)."""
        if self._t0 is None:
            return  # not in a with-block; refuse to compute elapsed_s
        now = time.perf_counter()
        elapsed = now - self._t0
        idx_gap = unit_idx - self._last_emit_idx
        time_gap = now - self._last_emit_t
        if (force
                or time_gap >= self.interval_s
                or idx_gap >= self.every_n_units):
            emit_heartbeat(self.output_dir, unit_idx=unit_idx,
                           elapsed_s=elapsed,
                           total_units=self.total_units, extra=extra)
            self._last_emit_t = now
            self._last_emit_idx = unit_idx

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._t0 is not None:
            elapsed = time.perf_counter() - self._t0
            event = "cell_heartbeat_exit_clean" if exc_type is None \
                else f"cell_heartbeat_exit_exc:{exc_type.__name__}"
            # Emit a final marker so the consumer can distinguish "still
            # running but quiet" from "exited cleanly" from "crashed".
            emit_heartbeat(self.output_dir,
                           unit_idx=self._last_emit_idx if self._last_emit_idx >= 0 else 0,
                           elapsed_s=elapsed, total_units=self.total_units,
                           extra={"event": event})


__all__ = ["emit_heartbeat", "CellHeartbeat"]
