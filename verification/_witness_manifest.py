"""pytest plugin: records which witnesses ACTUALLY ran in a given check, and writes an execution
manifest -- because "pytest verification/ is green" and "every witness ran" are different claims
(see notes/problems/447_witness_files_define_no_test_function_.../PROBLEM.md), and a green run
should be checkable against which of the two it is.

Loaded via `pyproject.toml`'s `addopts = ["-p", "verification._witness_manifest", ...]` (a plugin
module named by dotted path, not a conftest.py -- this file is not on the solver's write-list for
files outside verification/, and a `-p` entry needs no conftest.py to be discovered).

WHAT IT WRITES: one JSON file per pytest session, `data/hook_state/witness_manifest_<UTC stamp>.json`:
    {
      "run_utc": "...", "markexpr": "<the -m expression in force, if any>",
      "totals": {"collected": N, "ran": N, "passed": N, "failed": N, "error": N, "skipped": N},
      "items": [
        {"nodeid": "verification/test_x.py::test_witness", "file": "test_x.py",
         "tier": "fast"|"corpus"|"slow"|None, "outcome": "passed"|"failed"|"error"|"skipped",
         "seconds": 0.01}
        , ...
      ]
    }

`tools/witness_status.py` reads the newest one back and prints a plain summary.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "hook_state")

_TIERS = ("fast", "corpus", "slow")

# Module-level, not config-attribute, state: `TestReport` objects (received by
# pytest_runtest_logreport) carry no back-reference to the session's `config`, only `nodeid` --
# measured directly (an earlier version assumed `report.config` existed; it does not, and every
# run raised `AttributeError` inside the hook, which pytest reports as an INTERNALERROR wrapping
# whatever test happened to finish first).
_ITEMS: list[dict] = []
_TIERS_BY_NODEID: dict[str, str | None] = {}
_STARTED = None
_MARKEXPR = ""


def _tier_of(item) -> str | None:
    for marker in item.iter_markers():
        if marker.name in _TIERS:
            return marker.name
    return None


def pytest_configure(config):
    global _STARTED, _MARKEXPR
    _ITEMS.clear()
    _TIERS_BY_NODEID.clear()
    _STARTED = datetime.now(timezone.utc)
    _MARKEXPR = getattr(config.option, "markexpr", "") or ""


def pytest_runtest_logreport(report):
    # "call" is the phase that actually executes the test body; a failure in "setup"/"teardown"
    # still needs recording (it means the witness did NOT run cleanly) so accept those too, but
    # only once per test (avoid triple-counting setup+call+teardown for a plain pass).
    if report.when == "call" or (report.when in ("setup", "teardown") and report.outcome != "passed"):
        _ITEMS.append({
            "nodeid": report.nodeid,
            "file": report.nodeid.split("::", 1)[0].split("/")[-1],
            "outcome": report.outcome,
            "when": report.when,
            "seconds": round(getattr(report, "duration", 0.0), 4),
        })


def pytest_collection_modifyitems(config, items):
    # Stash tier per nodeid now, while marker objects are still cheaply available, so
    # sessionfinish does not need to re-walk the collected item tree.
    for item in items:
        _TIERS_BY_NODEID[item.nodeid] = _tier_of(item)


def pytest_sessionfinish(session, exitstatus):
    items = _ITEMS
    for row in items:
        row["tier"] = _TIERS_BY_NODEID.get(row["nodeid"])

    totals = {"collected": len(_TIERS_BY_NODEID), "ran": len(items), "passed": 0, "failed": 0,
              "error": 0, "skipped": 0}
    for row in items:
        outcome = row["outcome"]
        if outcome == "passed":
            totals["passed"] += 1
        elif outcome == "failed":
            totals["failed"] += 1
        elif outcome == "skipped":
            totals["skipped"] += 1
        else:
            totals["error"] += 1

    started = _STARTED or datetime.now(timezone.utc)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "run_utc": started.isoformat(),
        "markexpr": _MARKEXPR,
        "totals": totals,
        "items": sorted(items, key=lambda r: r["nodeid"]),
    }
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "witness_manifest_%s.json" % stamp)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=1)
    except OSError:
        # a manifest that fails to write must never fail the actual test run it describes.
        pass
