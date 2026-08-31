"""exp_grounded_role_uncertainty_curve_v1 -- THE DECISIVE BRAIN-PINNED TEST.

The gold-parse baseline showed grounded thematic fit adds ~nothing over word order for role
assignment. The research drill (research_thematic_fit_disambiguation_regime_2026-08-30.md) says that is
a REGIME ARTIFACT, not a ceiling: thematic fit is a DISAMBIGUATION-UNDER-UNCERTAINTY mechanism
(Trueswell/Tanenhaus/Garnsey 1994 -- plausibility effects vanish when morphology is unambiguous; McRae/
Spivey-Knowlton/Tanenhaus 1998 competition-integration -- fit is competition-GATED). Gibson/Bergen/
Piantadosi 2013 noisy-channel gives the EXACT falsifiable prediction: role-reversal (plausibility-driven)
recruitment rises MONOTONICALLY with the noise/uncertainty in the surface signal; at zero noise (a gold
parse) the posterior collapses onto the literal parse and plausibility contributes ~nothing.

This cell tests that prediction. It CORRUPTS the disambiguating passive morphology (the be/get/being
auxiliary + the "by") with probability p, simulating the degraded/uncertain structural signal the real
reader faces (POS-tag noise; reduced passives; the 0.288 non-canonical collapse the migration measured
on the noisy front-end). It then scores, as a function of p:
  order        word order only (no structure, no fit)
  graded_role  the landed structural assigner (its whole value is the morphology it is losing)
  gate         the grounded conflict-gated assigner (thematic fit recruited under conflict)
  gate_twin    info-free twin (thematic fit trained on SHUFFLED roles)  -- must NOT recover
  always_patient  degeneracy probe

Population is ROLE-BALANCED (canonical transitives contribute agents+patients; passives contribute
patients) and the headline metric is BALANCED accuracy (macro over agent/patient recall), so the
all-patient majority constant scores 0.5 and cannot win. Corruption is LEXICAL MASKING (keeps token
indices stable): the aux -> a neutral ADV, "by" -> a neutral ADP-less token, so robust_passive/gap stop
firing while word order is untouched.

BRAIN PREDICTION (can-fail): as p rises, graded_role collapses toward order while the gate DEGRADES
GRACEFULLY (fit carries) -> the gate-minus-structure gap GROWS monotonically with p (the noisy-channel
signature). A FLAT gate curve, or the info-free twin recovering, is the real negative.

Writes only to data/exp_grounded_role_uncertainty_curve_v1/. Does NOT modify hdlab/. No LLM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._grounded_role_data import load_items, split_by_sentence, add_animacy
from experiments._grounded_role_gate import (train_fit_model, count_fit_fn, make_noisy_channel_labeler,
                                             order_label)
from experiments.exp_grounded_role_baseline_v1 import graded_role_label, tag_reversible
from hdlab.graded_role_assigner import BE_AUX, GET_AUX

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_uncertainty_curve_v1")
CUE_AUX = set(BE_AUX) | set(GET_AUX) | {"being"}


def cue_token_ixs(it):
    """0-based indices of the passive-marking function words near the verb: aux (be/get/being) in the 3
    tokens before the verb, and 'by' in the 3 tokens after. These are the morphology the structural cue
    reads; masking them is the noisy-channel corruption."""
    forms = it["forms"]; v = it["verb_ix"]
    low = [f.lower() for f in forms]
    ixs = []
    for j in range(max(0, v - 3), v):
        if low[j] in CUE_AUX:
            ixs.append(j)
    for j in range(v + 1, min(len(forms), v + 4)):
        if low[j] == "by":
            ixs.append(j)
    return ixs


def corrupt_item(it, mask_ixs):
    """Return a shallow-copied item with the cue tokens lexically MASKED (indices preserved)."""
    if not mask_ixs:
        return it
    forms = list(it["forms"]); pos = list(it["pos"])
    for j in mask_ixs:
        if pos[j] == "ADP" or forms[j].lower() == "by":
            forms[j] = "near"; pos[j] = "ADV"     # kill the by-agent cue, keep it a modifier
        else:
            forms[j] = "then"; pos[j] = "ADV"      # kill the aux cue
    c = dict(it); c["forms"] = forms; c["pos"] = pos
    return c


def balanced_acc(items, predictor):
    rec = {"agent": [0, 0], "patient": [0, 0]}
    for it in items:
        ok = int(predictor(it) == it["role"])
        rec[it["role"]][0] += ok; rec[it["role"]][1] += 1
    parts = [rec[r][0] / rec[r][1] for r in ("agent", "patient") if rec[r][1]]
    return sum(parts) / len(parts) if parts else None, {r: (rec[r][0] / rec[r][1] if rec[r][1] else None) for r in rec}


def run(seed=20260830, tau=1.5):
    items = add_animacy(load_items())
    train, test = split_by_sentence(items)
    tag_reversible(train); tag_reversible(test)
    model = count_fit_fn(train_fit_model(train))
    twin = count_fit_fn(train_fit_model(train, shuffle_roles=True))

    # role-balanced population: canonical transitives (both roles) + passives (patient, order-misleading)
    pop = [it for it in test
           if (it["canon_type"] == "canonical" and it["n_args"] >= 2) or it["canon_type"] == "passive"]

    rng = np.random.default_rng(seed)
    for it in pop:
        it["_cue_ixs"] = cue_token_ixs(it)

    static_arms = {
        "order": lambda it: order_label(it),
        "always_patient": lambda it: "patient",
        "graded_role": graded_role_label,
    }
    all_names = list(static_arms) + ["gate", "gate_twin"]
    ps = [0.0, 0.25, 0.5, 0.75, 1.0]
    curve = {a: [] for a in all_names}
    perrole = {a: [] for a in all_names}
    for p in ps:
        # sample a mask for each item at this corruption level (seeded, deterministic per p)
        corr = []
        for it in pop:
            mask = [j for j in it["_cue_ixs"] if rng.random() < p]
            corr.append(corrupt_item(it, mask))
        # the joint noisy-channel gate + its info-free twin must be REBUILT on the corrupted forms
        # (markedness reads the corrupted morphology)
        gate_fn = make_noisy_channel_labeler(corr, model, tau=tau)
        twin_fn = make_noisy_channel_labeler(corr, twin, tau=tau)
        arms = dict(static_arms); arms["gate"] = gate_fn; arms["gate_twin"] = twin_fn
        for a, fn in arms.items():
            b, pr = balanced_acc(corr, fn)
            curve[a].append(round(b, 4))
            perrole[a].append({k: (round(v, 4) if v is not None else None) for k, v in pr.items()})

    # the noisy-channel signature: gate-minus-structure gap grows monotonically with p
    gap = [round(curve["gate"][i] - curve["graded_role"][i], 4) for i in range(len(ps))]
    gap_grows = all(gap[i] <= gap[i + 1] + 1e-9 for i in range(len(ps) - 1)) and gap[-1] > gap[0]
    twin_gap = [round(curve["gate_twin"][i] - curve["graded_role"][i], 4) for i in range(len(ps))]
    gate_recovers = curve["gate"][-1] - curve["gate"][0] > -0.05   # gate does NOT collapse as structure dies
    twin_flat_or_worse = curve["gate_twin"][-1] <= curve["gate"][-1] - 0.03  # twin cannot exploit the regime

    n_pass = sum(1 for it in pop if it["canon_type"] == "passive")
    verdict = {
        "gate_minus_structure_gap_by_p": dict(zip(map(str, ps), gap)),
        "gap_grows_monotonically_with_corruption": bool(gap_grows),
        "twin_minus_structure_gap_by_p": dict(zip(map(str, ps), twin_gap)),
        "gate_does_not_collapse_as_structure_dies": bool(gate_recovers),
        "info_free_twin_loses_at_full_corruption": bool(twin_flat_or_worse),
        "gate_beats_order_and_structure_at_full_corruption":
            bool(curve["gate"][-1] > curve["order"][-1] and curve["gate"][-1] > curve["graded_role"][-1]),
    }
    return {"ps": ps, "curve_balanced_acc": curve, "per_role_recall": perrole,
            "n_population": len(pop), "n_passive": n_pass, "verdict": verdict,
            "tau": tau, "seed": seed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["n_passive"] > 100, m["n_passive"]
        print("self-test PASS", json.dumps({"gap": list(m["verdict"]["gate_minus_structure_gap_by_p"].values())}))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 92)
    print("NOISY-CHANNEL CORRUPTION CURVE (Gibson 2013 prediction): balanced accuracy vs corruption p")
    print("=" * 92)
    print(f"population={m['n_population']} (passives={m['n_passive']}); metric=balanced acc (macro agent/patient)")
    print(f"\n{'p (corruption)':16s}" + "".join(f"{p:>8}" for p in m["ps"]))
    for a in ("order", "always_patient", "graded_role", "gate", "gate_twin"):
        print(f"{a:16s}" + "".join(f"{v:>8.3f}" for v in m["curve_balanced_acc"][a]))
    print(f"\ngate - structure gap by p: {list(m['verdict']['gate_minus_structure_gap_by_p'].values())}")
    print("VERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
