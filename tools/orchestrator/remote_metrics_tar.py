#!/usr/bin/env python3
"""Create tarball of load-bearing experiment artifacts under data/ for cross-host sync.

Includes: metrics.json + results.json + provenance.json + verdict.json + recent_verdicts.json
(per DECISION 220 Tier-1 preservation scope). Outputs to ~/metrics_pull.tar.
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
                if filename in LOAD_BEARING:
                    full = os.path.join(dirpath, filename)
                    arcname = full.replace("\\", "/")
                    tar.add(full, arcname=arcname)
                    bytes_total += os.path.getsize(full)
                    count += 1
    print(f"[remote-tar] files={count} size_MB={bytes_total / 1024 / 1024:.2f} out={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
