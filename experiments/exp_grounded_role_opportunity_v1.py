"""exp_grounded_role_opportunity_v1 -- WHERE is there room for grounded thematic fit?

The baseline showed the landed structural assigner (graded_role) already scores ~0.95 on the
gold-parse non-canonical subset -- because that subset is ~90% morphology-marked passive and voice
morphology resolves it structurally. So the fit signal can only add value where STRUCTURE IS SILENT
(no surface voice/gap cue fires), which is the regime where the brain's plausibility advantage shows
(owner: measure at the regime where the brain wins, not where counting wins).

This cell PARTITIONS the held-out items by whether a SURFACE structural cue fires (robust_passive or
gap_config -- exactly the cues graded_role recruits) and reports each arm per partition. The
STRUCTURE_SILENT-yet-non-canonical partition is the real opportunity; STRUCTURE_MARKED is where
structure already wins and the gate must stay inert.

Writes only to data/exp_grounded_role_opportunity_v1/. Does NOT modify hdlab/. No LLM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._grounded_role_data import load_items, split_by_sentence, add_animacy
from experiments.exp_mcguffey_migrate_grounded_thematic_fit_poc_v1 import train_selpref, predict_tf
from experiments.exp_grounded_role_baseline_v1 import graded_role_label
from hdlab.graded_role_assigner import robust_passive, gap_config

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_opportunity_v1")


def structure_fires(it):
    """A high-validity SURFACE structural override cue fires at this verb (what graded_role recruits)."""
    v = it["verb_ix"] + 1
    if robust_passive(it["forms"], it["pos"], v):
        return True
    ante, _ = gap_config(it["forms"], it["pos"], v)
    return ante is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    items = add_animacy(load_items())
    train, test = split_by_sentence(items)
    model = train_selpref(train)

    # partition: canonical vs non-canonical  x  structure-marked vs structure-silent
    parts = defaultdict(list)
    for it in test:
        nc = "NONCANON" if it["canon_type"] in ("passive", "inversion", "fronting") else "canonical"
        sm = "structMARKED" if structure_fires(it) else "structSILENT"
        parts[(nc, sm)].append(it)

    def acc(items_, fn):
        if not items_:
            return None
        return round(sum(int(fn(it) == it["role"]) for it in items_) / len(items_), 4)

    arms = {
        "naive_order": lambda it: "agent" if it["preverbal"] else "patient",
        "always_patient": lambda it: "patient",
        "graded_role": graded_role_label,
        "thematic_fit": lambda it: predict_tf(model, it["verb"], it["noun"]),
    }
    table = {}
    for (nc, sm), lst in sorted(parts.items()):
        key = f"{nc}/{sm}"
        n_agent = sum(it["role"] == "agent" for it in lst)
        table[key] = {"n": len(lst), "n_agent": n_agent,
                      **{a: acc(lst, fn) for a, fn in arms.items()}}

    if args.self_test:
        assert any("NONCANON/structSILENT" == k for k in table), list(table)
        print("self-test PASS", json.dumps({k: table[k]["n"] for k in table}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    meta = {"ts_iso": datetime.now(timezone.utc).isoformat(), "partitions": table}
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("=" * 96)
    print("OPPORTUNITY MAP: accuracy by (canonicity x surface-structure-cue). structSILENT non-canon = the room.")
    print("=" * 96)
    print(f"{'partition':28s}{'n':>6s}{'nAgt':>6s}{'order':>9s}{'allPat':>9s}{'graded':>9s}{'fit':>9s}")
    for k in sorted(table):
        t = table[k]
        print(f"{k:28s}{t['n']:>6d}{t['n_agent']:>6d}{str(t['naive_order']):>9s}{str(t['always_patient']):>9s}"
              f"{str(t['graded_role']):>9s}{str(t['thematic_fit']):>9s}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
