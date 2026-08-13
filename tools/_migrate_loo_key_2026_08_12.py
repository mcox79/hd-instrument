"""One-shot key-name migration: attribution.*.leave_one_out_GROWING -> leave_one_out.

Landed-VET notes/landed_vet_readout_fix_v1_2026-08-12.md sec 6: the key was emitted as
`leave_one_out_GROWING` for every fix, but F1/F2 are attributed in the FIXED regime, so the NAME
misattributed the regime for 2 of 3 fixes. Values were always correct and the sibling
`regime_for_attribution` always disambiguated -- mislabel, not mis-value. Rename only; the
migration ASSERTS the value payload is untouched and refuses to run if anything else differs.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = ["data/exp_readout_fix_v1/metrics.json",
           "data/exp_readout_fix_v1_smoke/metrics.json"]
OLD, NEW = "leave_one_out_GROWING", "leave_one_out"


def migrate(path: str) -> str:
    full = os.path.join(REPO, path)
    if not os.path.isfile(full):
        return "MISSING %s" % path
    with open(full, "r", encoding="utf-8") as fh:
        before_text = fh.read()
    doc = json.loads(before_text)
    attr = doc.get("attribution")
    if not isinstance(attr, dict):
        return "NO_ATTRIBUTION %s" % path
    renamed = []
    for fix, rec in sorted(attr.items()):
        if not isinstance(rec, dict) or OLD not in rec:
            continue
        payload = rec[OLD]
        # rebuild preserving key ORDER, so the diff is the name and nothing else
        newrec = {(NEW if k == OLD else k): v for k, v in rec.items()}
        assert newrec[NEW] is payload, "value must be carried through by identity"
        attr[fix] = newrec
        renamed.append("%s(%s)" % (fix, rec.get("regime_for_attribution")))
    if not renamed:
        return "ALREADY_MIGRATED %s" % path
    doc.setdefault("_key_migrations", []).append(
        {"date": "2026-08-12", "from": OLD, "to": NEW,
         "reason": "regime mislabel; F1/F2 are attributed in FIXED. Values unchanged; regime is "
                   "read from the sibling regime_for_attribution.",
         "authority": "notes/landed_vet_readout_fix_v1_2026-08-12.md sec 6"})
    after_text = json.dumps(doc, indent=2, sort_keys=False)
    # value-identity gate: the two docs must differ ONLY by the key name and the migration stamp
    a = json.loads(before_text)
    b = json.loads(after_text)
    b.pop("_key_migrations", None)
    for fix, rec in b.get("attribution", {}).items():
        rec[OLD] = rec.pop(NEW)
    assert a == b, "migration changed more than the key name in %s" % path
    tmp = full + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(after_text + "\n")
    os.replace(tmp, full)
    return "MIGRATED %s -> %s" % (path, ", ".join(renamed))


if __name__ == "__main__":
    for t in TARGETS:
        print(migrate(t))
    sys.exit(0)
