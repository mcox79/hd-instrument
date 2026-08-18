"""Enumerate data/ from the FILESYSTEM (os.walk), never from the registry.

Rule this obeys (CLAUDE.md Evidence discipline sec 2): enumerate from disk, then reconcile
to the registry -- never the reverse. 62 of 141 modules have no registry row, so a
registry-first audit is structurally blind.

HARD RULE: data/foundation/ is READ-ONLY with no backup. We do NOT descend into it. It is
pruned from the walk and reported by name only, from the parent directory listing.

du is unreliable here (512 KB st_blocks floor) -- we use os.path.getsize (apparent size).
ASCII only. Writes a JSON summary to scratch/.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

REPO = "D:/AI/hd-instrument"
DATA = os.path.join(REPO, "data")
FORBIDDEN = {os.path.normcase(os.path.join(DATA, "foundation"))}

# Directories whose per-file detail we do not need (thousands of experiment result dirs).
# We still COUNT and SIZE them; we just do not list every file.


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return "%.1f %s" % (n, unit)
        n /= 1024.0
    return str(n)


def main() -> int:
    top_entries = []
    with os.scandir(DATA) as it:
        for e in sorted(it, key=lambda x: x.name):
            top_entries.append((e.name, "dir" if e.is_dir() else "file"))

    # per top-level child of data/: total apparent bytes + file count
    per_top = defaultdict(lambda: {"bytes": 0, "files": 0, "pruned": False})
    ext_hist = defaultdict(lambda: {"bytes": 0, "files": 0})
    big_files = []  # (bytes, relpath)
    all_dirs = 0

    for root, dirs, files in os.walk(DATA):
        nroot = os.path.normcase(os.path.abspath(root))
        # prune forbidden
        keep = []
        for d in dirs:
            nd = os.path.normcase(os.path.abspath(os.path.join(root, d)))
            if nd in FORBIDDEN:
                rel = os.path.relpath(os.path.join(root, d), DATA).replace("\\", "/")
                per_top[rel.split("/")[0]]["pruned"] = True
                continue
            keep.append(d)
        dirs[:] = sorted(keep)
        all_dirs += 1

        rel_root = os.path.relpath(root, DATA).replace("\\", "/")
        top = "." if rel_root == "." else rel_root.split("/")[0]
        for f in files:
            p = os.path.join(root, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            per_top[top]["bytes"] += sz
            per_top[top]["files"] += 1
            ext = os.path.splitext(f)[1].lower() or "<noext>"
            ext_hist[ext]["bytes"] += sz
            ext_hist[ext]["files"] += 1
            if sz >= 5 * 1024 * 1024:
                big_files.append((sz, os.path.relpath(p, DATA).replace("\\", "/")))

    big_files.sort(reverse=True)

    out = {
        "data_root": DATA,
        "top_level_entries": top_entries,
        "n_top_level_entries": len(top_entries),
        "n_dirs_walked": all_dirs,
        "pruned_never_opened": sorted(FORBIDDEN),
        "per_top_level": {
            k: {"bytes": v["bytes"], "human": human(v["bytes"]), "files": v["files"],
                "contains_pruned_subtree": v["pruned"]}
            for k, v in sorted(per_top.items(), key=lambda kv: -kv[1]["bytes"])
        },
        "ext_histogram_top30": {
            k: {"bytes": v["bytes"], "human": human(v["bytes"]), "files": v["files"]}
            for k, v in sorted(ext_hist.items(), key=lambda kv: -kv[1]["bytes"])[:30]
        },
        "files_over_5MB": [{"human": human(s), "bytes": s, "path": p} for s, p in big_files[:200]],
        "n_files_over_5MB": len(big_files),
        "total_bytes_excluding_foundation": sum(v["bytes"] for v in per_top.values()),
    }
    out["total_human_excluding_foundation"] = human(out["total_bytes_excluding_foundation"])

    dest = os.path.join(REPO, "scratch", "data_asset_enumeration_2026-08-18.json")
    with open(dest, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", dest)
    print("top-level entries:", len(top_entries))
    print("total (excluding data/foundation):", out["total_human_excluding_foundation"])
    print("files >= 5MB:", len(big_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
