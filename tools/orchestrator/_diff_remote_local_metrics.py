#!/usr/bin/env python
"""Diff remote vs local metrics.json inventories by normalized cell name.

Matches on SEVERAL name variants before declaring anything remote-only:
  - leaf directory name as-is
  - leaf with leading 'exp_' / repeated 'exp_exp_' stripped
  - leaf with 'substrate_' prefix stripped
  - full relative dir path
  - the 'exp_name' field recorded inside metrics.json
"""
import json
import sys


def variants(rec):
    out = set()
    leaf = (rec.get("leaf") or "").strip()
    rel = (rec.get("rel_dir") or "").strip()
    cands = {leaf, rel}
    name = rec.get("exp_name")
    if name:
        cands.add(name.strip())
    # also every path segment that looks like the cell dir
    if rel and "/" in rel:
        cands.add(rel.split("/")[-1])
    for c in list(cands):
        if not c or c == ".":
            continue
        c = c.strip().lower()
        out.add(c)
        s = c
        while s.startswith("exp_"):
            s = s[4:]
            out.add(s)
        s2 = c
        if s2.startswith("substrate_"):
            out.add(s2[len("substrate_"):])
        # normalize separators
        out.add(c.replace("-", "_"))
    return {v for v in out if v and v != "."}


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


remote = load(sys.argv[1])
local = load(sys.argv[2])
outp = sys.argv[3]

local_keys = set()
for r in local["records"]:
    local_keys |= variants(r)

remote_keys = set()
for r in remote["records"]:
    remote_keys |= variants(r)

remote_only = []
both = []
for r in remote["records"]:
    v = variants(r)
    if v & local_keys:
        both.append(r)
    else:
        remote_only.append(r)

local_only = []
for r in local["records"]:
    v = variants(r)
    if not (v & remote_keys):
        local_only.append(r)

res = {
    "remote_total": remote["count"],
    "local_total": local["count"],
    "both": len(both),
    "remote_only": len(remote_only),
    "local_only": len(local_only),
    "remote_only_records": remote_only,
    "local_only_leafs": sorted({r["rel_dir"] for r in local_only}),
}
with open(outp, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)

print("remote_total=%d local_total=%d both=%d remote_only=%d local_only=%d"
      % (res["remote_total"], res["local_total"], res["both"],
         res["remote_only"], res["local_only"]))
