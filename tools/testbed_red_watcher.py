#!/usr/bin/env python3
"""testbed_red_watcher.py -- Python port of testbed_red_watcher.sh.

Polls the Health endpoint every 60s + scans notes/ for new RED-class notes.
Emits one stdout line per transition or new RED note. Run via Monitor tool.

WHY THIS VERSION: bash version called curl + python -c (subshell) every 60s,
each spawning a console under Claude Code's hidden-console parent. Python
version uses urllib + os.scandir in-process: zero subprocess spawns after arm.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

URL = "http://localhost:8765/api/dashboard/v2/health"
ROOT = r"D:\AI\hd-instrument"
NOTES_DIR = os.path.join(ROOT, "notes")
SLEEP_SECONDS = 60

RED_PAT = re.compile(
    r"(red_flag|red-alert|data_referent_drift|data-drift|reproducibility_hazard|"
    r"hold_chaingrade|runaway|leak|failed|cuda_oom|i_missed|missed_it|stall|crash|"
    r"hang|hazard|over_call|self_catch)",
    re.IGNORECASE,
)


def list_red_notes() -> set[str]:
    out: set[str] = set()
    try:
        with os.scandir(NOTES_DIR) as it:
            for entry in it:
                name = entry.name
                if not name.endswith(".md"):
                    continue
                if RED_PAT.search(name):
                    out.add(name)
    except FileNotFoundError:
        pass
    return out


def fetch_health() -> tuple[str, list[str]] | None:
    try:
        with urllib.request.urlopen(URL, timeout=10) as r:
            body = r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    try:
        d = json.loads(body)
    except json.JSONDecodeError:
        return None
    agg = (d.get("aggregate") or {}).get("status", "?")
    red = sorted(
        det["name"]
        for det in d.get("drift_detectors", [])
        if det.get("status") == "RED"
    )
    ig = (d.get("substrate_trust") or {}).get("integrity") or {}
    if ig.get("status") == "FLAGS" and ig.get("n_flags", 0) > 30:
        red.append("integrity-flags-rising")
    return agg, red


seen_reds = list_red_notes()
prev_reds: list[str] = []
prev_agg = ""

print(
    "RED-WATCHER-ARMED: polling Health + notes/ every 60s (Python port; no subprocess spawns)",
    flush=True,
)

while True:
    time.sleep(SLEEP_SECONDS)

    health = fetch_health()
    if health is not None:
        agg, reds = health
        if reds != prev_reds:
            new_set = set(reds) - set(prev_reds)
            cleared = set(prev_reds) - set(reds)
            if new_set:
                print(f"RED-NEW: {','.join(sorted(new_set))} (agg={agg})", flush=True)
            if cleared:
                print(f"RED-CLEARED: {','.join(sorted(cleared))} (agg={agg})", flush=True)
            prev_reds = reds
        worse = {"OK": 0, "WARN": 1, "RED": 2, "?": 0}
        if worse.get(agg, 0) > worse.get(prev_agg, 0):
            print(f"AGG-WORSE: {prev_agg} -> {agg}", flush=True)
        prev_agg = agg

    cur_reds = list_red_notes()
    new_red_notes = cur_reds - seen_reds
    if new_red_notes:
        for name in sorted(new_red_notes):
            print(f"RED-NOTE: {name}", flush=True)
        seen_reds |= new_red_notes
