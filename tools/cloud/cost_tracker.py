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
    accumulated_today_usd: Optional[float] = None,
    current_hourly_rate_usd: Optional[float] = None,
    active_instances: Optional[Iterable[dict]] = None,
    daily_budget_usd: Optional[float] = None,
) -> None:
    """Atomically merge values into the cost-tracker snapshot.

    Any argument left as None preserves the existing value in the JSON
    file. Pass an explicit float / list to overwrite. This is the merge
    semantic the launchers actually want: "set hourly_rate now without
    resetting cumulative spend".

    To INCREMENT accumulated cost (the common case at run termination),
    use accumulate_run_cost() instead of computing the new total here.

    Args:
        accumulated_today_usd: total spend so far today (UTC). None = preserve.
        current_hourly_rate_usd: aggregate $/hr across all active instances.
            None = preserve. Set to 0.0 explicitly at terminate.
        active_instances: list of dicts describing currently-spending
            instances. None = preserve. Pass [] explicitly at terminate.
        daily_budget_usd: OPTIONAL per-UTC-day cap. None = preserve
            existing value (or absence). Pass 0 / float to overwrite.
    """
    existing = read_cost() or {}
    entry = {
        "accumulated_today_usd": float(accumulated_today_usd) if accumulated_today_usd is not None
            else float(existing.get("accumulated_today_usd") or 0.0),
        "current_hourly_rate_usd": float(current_hourly_rate_usd) if current_hourly_rate_usd is not None
            else float(existing.get("current_hourly_rate_usd") or 0.0),
        "last_updated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "active_instances": list(active_instances) if active_instances is not None
            else list(existing.get("active_instances") or []),
    }
    if daily_budget_usd is not None:
        entry["daily_budget_usd"] = float(daily_budget_usd)
    elif "daily_budget_usd" in existing and existing["daily_budget_usd"] is not None:
        entry["daily_budget_usd"] = float(existing["daily_budget_usd"])
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


def accumulate_run_cost(actual_cost_usd: float) -> float:
    """Increment cumulative session spend by a completed run's cost.

    Reads the current accumulated_today_usd, adds actual_cost_usd, writes
    back. Returns the new total. Use this at run termination instead of
    overwriting accumulated_today_usd with a single run's cost.
    """
    existing = read_cost() or {}
    current = float(existing.get("accumulated_today_usd") or 0.0)
    new_total = current + float(actual_cost_usd)
    update_cost(accumulated_today_usd=new_total)
    return new_total


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
