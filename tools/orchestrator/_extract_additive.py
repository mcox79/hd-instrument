#!/usr/bin/env python
"""Extract a tarball ADDITIVELY under a destination root.

Hard rules enforced here:
  - NEVER overwrite an existing local file. Collisions are extracted to a
    clearly-suffixed path (<name>.remote_<stamp><ext>) and reported.
  - NEVER delete anything.
  - Refuse any member that resolves outside dest_root, or under 'foundation/'.
"""
import os
import sys
import tarfile

tgz = sys.argv[1]
dest = os.path.abspath(sys.argv[2])
stamp = sys.argv[3] if len(sys.argv) > 3 else "20260818"

written = []
collisions = []
refused = []
bytes_written = 0

with tarfile.open(tgz, "r:gz") as tf:
    for m in tf.getmembers():
        if not m.isfile():
            continue
        name = m.name.replace("\\", "/").lstrip("/")
        if ".." in name.split("/"):
            refused.append((name, "path_traversal"))
            continue
        if name.split("/")[0] == "foundation":
            refused.append((name, "foundation_readonly"))
            continue
        target = os.path.abspath(os.path.join(dest, name))
        if not target.startswith(dest + os.sep):
            refused.append((name, "escapes_dest"))
            continue
        if os.path.exists(target):
            base, ext = os.path.splitext(target)
            target = "%s.remote_%s%s" % (base, stamp, ext)
            collisions.append(name)
            if os.path.exists(target):
                refused.append((name, "collision_suffix_also_exists"))
                continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        src = tf.extractfile(m)
        if src is None:
            continue
        data = src.read()
        with open(target, "wb") as fh:
            fh.write(data)
        written.append(os.path.relpath(target, dest).replace("\\", "/"))
        bytes_written += len(data)

print("EXTRACT_OK files_written=%d bytes_written=%d collisions=%d refused=%d"
      % (len(written), bytes_written, len(collisions), len(refused)))
for c in collisions:
    print("COLLISION %s" % c)
for r, why in refused:
    print("REFUSED %s (%s)" % (r, why))
