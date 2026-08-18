#!/usr/bin/env python
"""Pack result-bearing files (json/jsonl/.done/.md/.txt/.log) from listed remote
experiment dirs into a single tar.gz for transfer. READ-ONLY on the source tree:
nothing is deleted or modified.
"""
import os
import sys
import tarfile

root = sys.argv[1]
dirs_file = sys.argv[2]
out_tgz = sys.argv[3]

KEEP_EXT = {".json", ".jsonl", ".done", ".md", ".txt", ".log", ".csv", ".yaml", ".yml"}
MAX_BYTES = 50 * 1024 * 1024  # skip anything unexpectedly huge

with open(dirs_file, "r", encoding="utf-8") as fh:
    dirs = [ln.strip() for ln in fh if ln.strip()]

n = 0
total = 0
skipped_big = []
with tarfile.open(out_tgz, "w:gz") as tf:
    for d in dirs:
        full = os.path.join(root, d.replace("/", os.sep))
        if not os.path.isdir(full):
            print("MISSING_REMOTE_DIR %s" % d)
            continue
        for dp, dn, fn in os.walk(full):
            for f in fn:
                ext = os.path.splitext(f)[1].lower()
                if ext not in KEEP_EXT:
                    continue
                p = os.path.join(dp, f)
                try:
                    sz = os.path.getsize(p)
                except OSError:
                    continue
                if sz > MAX_BYTES:
                    skipped_big.append((os.path.relpath(p, root), sz))
                    continue
                arc = os.path.relpath(p, root).replace("\\", "/")
                tf.add(p, arcname=arc)
                n += 1
                total += sz

print("PACK_OK files=%d raw_bytes=%d tgz=%s tgz_bytes=%d skipped_big=%d"
      % (n, total, out_tgz, os.path.getsize(out_tgz), len(skipped_big)))
for p, s in skipped_big:
    print("SKIPPED_BIG %s %d" % (p, s))
