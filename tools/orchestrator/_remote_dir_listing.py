#!/usr/bin/env python
"""List files (rel path + size) for a set of remote experiment dirs. Read-only."""
import json
import os
import sys

root = sys.argv[1]
dirs_file = sys.argv[2]
out = sys.argv[3]

with open(dirs_file, "r", encoding="utf-8") as fh:
    dirs = [ln.strip() for ln in fh if ln.strip()]

res = {}
total = 0
for d in dirs:
    full = os.path.join(root, d.replace("/", os.sep))
    files = []
    for dp, dn, fn in os.walk(full):
        for f in fn:
            p = os.path.join(dp, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                sz = -1
            files.append([os.path.relpath(p, full).replace("\\", "/"), sz])
            if sz > 0:
                total += sz
    res[d] = files

with open(out, "w", encoding="utf-8") as fh:
    json.dump({"root": root, "total_bytes": total, "dirs": res}, fh, indent=1)
print("LISTING_OK dirs=%d total_bytes=%d out=%s" % (len(dirs), total, out))
