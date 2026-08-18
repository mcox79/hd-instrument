#!/usr/bin/env python
"""Enumerate every metrics.json under the remote experiment output tree.

Enumerates from the FILESYSTEM (os.walk), not from any queue file or manifest.
Writes a JSON inventory to the path given as argv[1].

Skips data/foundation/ entirely (READ-ONLY, no backup -- do not touch).
"""
import json
import os
import sys
import time

ROOT = sys.argv[2] if len(sys.argv) > 2 else r"C:\dev\hd-instrument\data"
OUT = sys.argv[1]

SKIP_DIR_NAMES = {"foundation", ".git", "__pycache__", "node_modules"}

records = []
walk_errors = []


def onerr(e):
    walk_errors.append(str(e))


for dirpath, dirnames, filenames in os.walk(ROOT, onerror=onerr):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
    if "metrics.json" not in filenames:
        continue
    full = os.path.join(dirpath, "metrics.json")
    try:
        st = os.stat(full)
        size = st.st_size
        mtime = st.st_mtime
    except OSError as e:
        walk_errors.append("stat %s: %s" % (full, e))
        continue
    rel = os.path.relpath(dirpath, ROOT).replace("\\", "/")
    leaf = os.path.basename(dirpath)
    verdict = None
    run_mode = None
    exp_name = None
    elapsed = None
    parse_err = None
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as fh:
            obj = json.load(fh)
        if isinstance(obj, dict):
            for k in ("verdict", "verdict_str", "status"):
                if k in obj and obj[k] is not None:
                    verdict = str(obj[k])[:200]
                    break
            for k in ("run_mode", "mode"):
                if k in obj and obj[k] is not None:
                    run_mode = str(obj[k])[:60]
                    break
            for k in ("experiment", "exp_name", "name", "cell"):
                if k in obj and obj[k] is not None:
                    exp_name = str(obj[k])[:200]
                    break
            for k in ("elapsed_s", "wall_s", "duration_s"):
                if k in obj and obj[k] is not None:
                    elapsed = obj[k]
                    break
    except Exception as e:  # noqa: BLE001
        parse_err = "%s: %s" % (type(e).__name__, str(e)[:120])

    records.append({
        "rel_dir": rel,
        "leaf": leaf,
        "size": size,
        "mtime": mtime,
        "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime)),
        "verdict": verdict,
        "run_mode": run_mode,
        "exp_name": exp_name,
        "elapsed_s": elapsed,
        "parse_error": parse_err,
    })

records.sort(key=lambda r: r["mtime"])
out = {
    "root": ROOT,
    "count": len(records),
    "oldest": records[0]["mtime_iso"] if records else None,
    "newest": records[-1]["mtime_iso"] if records else None,
    "walk_errors": walk_errors[:50],
    "walk_error_count": len(walk_errors),
    "records": records,
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
print("INVENTORY_OK count=%d oldest=%s newest=%s walk_errors=%d out=%s"
      % (out["count"], out["oldest"], out["newest"], out["walk_error_count"], OUT))
