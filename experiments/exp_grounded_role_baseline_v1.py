"""exp_grounded_role_baseline_v1 -- MEASURE THE FLOORS before building the gate.

Establishes, on the MODERN UD-EWT core-arg role gold (sentence-level held-out split), what every
floor/arm actually scores per subset, INCLUDING the degenerate majority-class constant, so the fair
metric is chosen from evidence rather than assumed. No gate yet.

Arms:
  naive_order        preverbal->agent (Bever NVN word order)          [bar floor 1]
  graded_role        hdlab.graded_role_assigner.hybrid_role_patient   [bar floor 2: current gramm-function assigner]
  always_patient     constant patient                                 [degeneracy probe -- non-canonical is ~all patient]
  thematic_fit       argmax of verb-keyed selectional preference      [the proven signal, gate-free]
  poc_combined       the PoC's confidence-conflict override           [prior crude gate]
Subsets: canonical / passive / inversion / fronting / NONCANON / reversible(anim-anim canonical) / ALL.
Reports raw accuracy AND balanced (macro over agent/patient) accuracy per subset.

Writes only to data/exp_grounded_role_baseline_v1/. Does NOT modify hdlab/. No LLM.
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
from experiments.exp_mcguffey_migrate_grounded_thematic_fit_poc_v1 import train_selpref, predict_tf, predict_combined
from experiments.exp_mcguffey_migrate_learned_competition_v1 import fit_logodds
from hdlab.graded_role_assigner import hybrid_role_patient, robust_passive, gap_config

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_baseline_v1")


def graded_role_label(it):
    """Map the landed patient-route organ to an agent/patient label for this item's noun, FAIRLY.

    The organ detects the PATIENT slot. A noun is patient iff it is the organ's pick AND that pick is a
    genuine patient (a post-verbal object exists, or a surface passive/gap override fired so a pre-verbal
    noun can be the patient). A LONE pre-verbal subject with no post-verbal object and no override cue is
    the AGENT -- forcing the patient-route organ to label it would be misuse (it always returns someone)."""
    v = it["verb_ix"] + 1
    pid = hybrid_role_patient(it["forms"], it["pos"], v, list(it["cand_ids"]))
    if pid != it["noun_id"]:
        return "agent"
    post = [c for c in it["cand_ids"] if c > v]
    override = robust_passive(it["forms"], it["pos"], v) or gap_config(it["forms"], it["pos"], v)[0] is not None
    if it["noun_id"] < v and not post and not override:
        return "agent"
    return "patient"


def tag_reversible(items):
    """A clause is reversible-ambiguous if it is canonical, has >=2 core nominal args, all ANIMATE
    (either could act). Model-independent of the fit signal. Tag each item in such a clause."""
    byv = defaultdict(list)
    for it in items:
        byv[(it["sent_uid"], it["verb_id"])].append(it)
    for grp in byv.values():
        anim = [x["animacy"] for x in grp]
        rev = len(grp) >= 2 and all(a == "animate" for a in anim) and all(x["canon_type"] == "canonical" for x in grp)
        for x in grp:
            x["reversible"] = bool(rev)
    return items


SUBSETS = ["ALL", "canonical", "passive", "inversion", "fronting", "NONCANON", "reversible"]


def _subset_of(it):
    s = [it["canon_type"], "ALL"]
    if it["canon_type"] in ("passive", "inversion", "fronting"):
        s.append("NONCANON")
    if it.get("reversible"):
        s.append("reversible")
    return s


def evaluate(items, predictor):
    raw = {k: [0, 0] for k in SUBSETS}
    perrole = {k: {"agent": [0, 0], "patient": [0, 0]} for k in SUBSETS}
    for it in items:
        ok = int(predictor(it) == it["role"])
        for s in _subset_of(it):
            raw[s][0] += ok; raw[s][1] += 1
            perrole[s][it["role"]][0] += ok; perrole[s][it["role"]][1] += 1
    out = {}
    for k in SUBSETS:
        n = raw[k][1]
        acc = round(raw[k][0] / n, 4) if n else None
        recs = []
        for r in ("agent", "patient"):
            rn = perrole[k][r][1]
            if rn:
                recs.append(perrole[k][r][0] / rn)
        bal = round(sum(recs) / len(recs), 4) if recs else None
        out[k] = {"acc": acc, "balanced_acc": bal, "n": n,
                  "n_agent": perrole[k]["agent"][1], "n_patient": perrole[k]["patient"][1]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    items = add_animacy(load_items())
    train, test = split_by_sentence(items)
    tag_reversible(train); tag_reversible(test)
    model = train_selpref(train)

    arms = {
        "naive_order": lambda it: "agent" if it["preverbal"] else "patient",
        "always_patient": lambda it: "patient",
        "graded_role": graded_role_label,
        "thematic_fit": lambda it: predict_tf(model, it["verb"], it["noun"]),
        "poc_combined": lambda it: predict_combined(model, it),
    }
    res = {name: evaluate(test, fn) for name, fn in arms.items()}

    if args.self_test:
        assert res["naive_order"]["canonical"]["acc"] > 0.95
        assert res["always_patient"]["NONCANON"]["n"] > 50
        print("self-test PASS", json.dumps({a: res[a]["NONCANON"]["acc"] for a in arms}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    meta = {"ts_iso": datetime.now(timezone.utc).isoformat(),
            "n_train": len(train), "n_test": len(test), "arms": res,
            "test_subset_n": {k: res["naive_order"][k]["n"] for k in SUBSETS}}
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("=" * 100)
    print("FLOORS on MODERN UD-EWT core-arg role gold (sentence-level held-out). acc [balanced_acc] per subset")
    print("=" * 100)
    hdr = f"{'arm':16s}"
    for k in SUBSETS:
        hdr += f"{k[:9]:>11s}"
    print(hdr)
    print(f"{'(n)':16s}" + "".join(f"{res['naive_order'][k]['n']:>11d}" for k in SUBSETS))
    print(f"{'(n agent)':16s}" + "".join(f"{res['naive_order'][k]['n_agent']:>11d}" for k in SUBSETS))
    for name in arms:
        row = f"{name:16s}"
        for k in SUBSETS:
            a = res[name][k]["acc"]; b = res[name][k]["balanced_acc"]
            row += f"{(str(a)+'/'+str(b))[:10]:>11s}" if a is not None else f"{'-':>11s}"
        print(row)
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
