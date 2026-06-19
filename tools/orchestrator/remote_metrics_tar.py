#!/usr/bin/env python3
"""Create tarball of load-bearing experiment artifacts under data/ for cross-host sync.

Includes: metrics.json + results.json + provenance.json + verdict.json + recent_verdicts.json
(per DECISION 220 Tier-1 preservation scope) + cached_indices/*.npz (per Director RATIFY
2026-06-17 Action A bge-index-refresh Q6 manifest extension). Outputs to ~/metrics_pull.tar.
"""
import os
import sys
import tarfile

DATA_ROOT = "data"
LOAD_BEARING = {
    "metrics.json",
    "results.json",
    "provenance.json",
    "verdict.json",
    "recent_verdicts.json",
}
# Per-extension allowlist for specific subtrees (Action A Q6 extension)
EXT_INCLUDE_BY_DIR = {
    "cached_indices": {".npz"},  # bge index cache files
}
OUT = os.path.expanduser("~/metrics_pull.tar")


def main():
    root = os.environ.get("HD_INSTRUMENT_DIR", "C:/dev/hd-instrument")
    os.chdir(root)
    if not os.path.isdir(DATA_ROOT):
        print(f"[remote-tar] no data/ in {root}", file=sys.stderr)
        return 1

    count = 0
    bytes_total = 0
    with tarfile.open(OUT, "w") as tar:
        for dirpath, dirnames, filenames in os.walk(DATA_ROOT):
            for filename in filenames:
                included = False
                if filename in LOAD_BEARING:
                    included = True
                else:
                    for dir_marker, ext_set in EXT_INCLUDE_BY_DIR.items():
                        if dir_marker in dirpath.replace("\\", "/").split("/"):
                            ext = os.path.splitext(filename)[1].lower()
                            if ext in ext_set:
                                included = True
                                break
                if included:
                    full = os.path.join(dirpath, filename)
                    arcname = full.replace("\\", "/")
                    tar.add(full, arcname=arcname)
                    bytes_total += os.path.getsize(full)
                    count += 1
    print(f"[remote-tar] files={count} size_MB={bytes_total / 1024 / 1024:.2f} out={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
