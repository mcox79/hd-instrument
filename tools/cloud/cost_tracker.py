"""Cloud cost tracker — single owner of data/cloud_cost_tracker.json.

The cloud session (when active) calls update_cost() to advertise current
spend, hourly rate, and active instances. The dashboard reads the file
(see tools/dashboard/poller.py) and surfaces a cost line on the Lambda
runner card + cost-cap watchdog signals.

Pre-cloud-activation: this module is unused. The dashboard renders the
Lambda card as "inactive" with no cost line.

Schema (atomic .tmp + os.replace):
  {
    "daily_budget_usd": 50.00,           # cap per UTC day
    "accumulated_today_usd": 12.43,      # spend so far today
    "current_hourly_rate_usd": 1.50,     # $/hr at this moment (sum of
                                         # active instances' rates)
    "last_updated": "2026-05-31T...",    # local ISO-8601
    "active_instances": [                # what is currently spending
      {"instance_id": "abc123",
       "instance_type": "gpu_1x_h100",
       "hourly_rate_usd": 1.50,
       "started_at": "..."}
    ]
  }

Atomic writes via .tmp + os.replace; safe against concurrent dashboard reads.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


_REPO_ROOT = Path(__file__).parents[2]
_DATA_DIR = _REPO_ROOT / "data"
_COST_PATH = _DATA_DIR / "cloud_cost_tracker.json"


def update_cost(
    daily_budget_usd: float,
    accumulated_today_usd: float,
    current_hourly_rate_usd: float,
    active_instances: Optional[Iterable[dict]] = None,
) -> None:
    """Write a fresh cost-tracker snapshot.

    Args:
        daily_budget_usd: per-UTC-day cap. The cost-discipline layer
            triggers shutdown when accumulated_today_usd >= this.
        accumulated_today_usd: total spend so far today (UTC).
        current_hourly_rate_usd: aggregate $/hr across all active instances.
        active_instances: list of dicts describing currently-spending
            instances (instance_id, instance_type, hourly_rate_usd,
            started_at). Optional.
    """
    entry = {
        "daily_budget_usd": float(daily_budget_usd),
        "accumulated_today_usd": float(accumulated_today_usd),
        "current_hourly_rate_usd": float(current_hourly_rate_usd),
        "last_updated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "active_instances": list(active_instances or []),
    }
    _COST_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(_COST_PATH.parent), prefix=_COST_PATH.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
        os.replace(tmp_path, str(_COST_PATH))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_cost() -> Optional[dict]:
    """Read the current cost-tracker snapshot, or None if absent / corrupt."""
    if not _COST_PATH.is_file():
        return None
    try:
        with open(_COST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def budget_alert_level(cost: dict) -> str:
    """Return alert level for a cost snapshot: ok | warn | over.

    warn at >= 75% of daily budget; over at >= 100%.
    """
    if not cost:
        return "ok"
    budget = float(cost.get("daily_budget_usd") or 0)
    acc = float(cost.get("accumulated_today_usd") or 0)
    if budget <= 0:
        return "ok"
    ratio = acc / budget
    if ratio >= 1.0:
        return "over"
    if ratio >= 0.75:
        return "warn"
    return "ok"
