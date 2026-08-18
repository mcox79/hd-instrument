#!/usr/bin/env python
"""Emit a compact per-directory file manifest for a data tree.

Output JSON: {reldir: {"n": <file count>, "b": <total bytes>, "f": [sorted names]}}
Skips foundation/, .git/, __pycache__/. READ-ONLY.
"""
import json
import os
import sys

root = sys.argv[1]
out = sys.argv[2]
SKIP = {"foundation", ".git", "__pycache__", "node_modules"}

man = {}
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in SKIP]
    if not fn:
        continue
    rel = os.path.relpath(dp, root).replace("\\", "/")
    tot = 0
    for f in fn:
        try:
            tot += os.path.getsize(os.path.join(dp, f))
        except OSError:
            pass
    man[rel] = {"n": len(fn), "b": tot, "f": sorted(fn)}

with open(out, "w", encoding="utf-8") as fh:
    json.dump(man, fh)
print("MANIFEST_OK dirs=%d files=%d out=%s"
      % (len(man), sum(v["n"] for v in man.values()), out))
