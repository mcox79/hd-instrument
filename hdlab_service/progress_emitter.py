"""Atomic progress.json writer for long-running experiments.

The dashboard poller (tools/dashboard/poller.py) already reads
data/exp_<anchor>/progress.json with this exact schema:

  {
    "phase":       "running cell N=2048 M=8192 s=17",
    "cell":        14,
    "total_cells": 39,
    "eta_sec":     420,
    "updated_at":  "2026-05-31T17:14:22-04:00"
  }

Atomic .tmp + os.replace writes mean a concurrent reader (the dashboard's
30-second SCP pull) never sees a partial file.

Usage in an experiment script:

    from hdlab_service.progress_emitter import ProgressEmitter

    p = ProgressEmitter(
        out_path="data/exp_my_anchor/progress.json",
        total_cells=42,
        phase="warming up",
    )
    for cell_idx, work in enumerate(work_items, start=1):
        do_work(work)
        p.update(cell=cell_idx, phase=f"N=... M=...")
    p.done()

ETA is computed from a rolling window of the last 8 cell durations so a
single slow cell does not skew the estimate. None when fewer than 2 cells
have completed.

Per architecture v1 testbed ownership: this module lives under
hdlab_service/ which is testbed-owned. Experiments and cloud wrappers may
import it freely; the orchestrator does not write to it.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_ROLLING_WINDOW = 8


class ProgressEmitter:
    """Atomic progress.json writer with rolling-window ETA."""

    def __init__(
        self,
        out_path: str | Path,
        total_cells: int,
        phase: str = "starting",
    ):
        self.out_path = Path(out_path)
        self.total_cells = int(total_cells)
        self.phase = phase
        self.cell = 0
        self.start_ts = datetime.now(timezone.utc)
        self.last_cell_ts = self.start_ts
        self._durations: deque[float] = deque(maxlen=_ROLLING_WINDOW)
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self._write()

    def update(self, cell: int, phase: Optional[str] = None) -> None:
        """Advance progress; recompute ETA; write atomically."""
        now = datetime.now(timezone.utc)
        if cell > self.cell:
            delta = cell - self.cell
            span = (now - self.last_cell_ts).total_seconds()
            per_cell = span / max(1, delta)
            for _ in range(delta):
                self._durations.append(per_cell)
        self.cell = int(cell)
        if phase is not None:
            self.phase = phase
        self.last_cell_ts = now
        self._write()

    def done(self, phase: str = "done") -> None:
        """Mark complete; ETA goes to 0."""
        self.cell = self.total_cells
        self.phase = phase
        self._write()

    def _write(self) -> None:
        eta: Optional[int] = None
        if self._durations and self.cell < self.total_cells:
            avg = sum(self._durations) / len(self._durations)
            remaining = self.total_cells - self.cell
            eta = int(round(avg * remaining))
        elif self.cell >= self.total_cells:
            eta = 0
        entry = {
            "phase": self.phase,
            "cell": self.cell,
            "total_cells": self.total_cells,
            "eta_sec": eta,
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.out_path.parent),
            prefix=self.out_path.name + ".",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)
            os.replace(tmp_path, str(self.out_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
