"""exp_grounded_role_gate_v1 -- consolidated bootstrap scoring for grounded_role_assignment_via_verb_keyed_thematic_fit.

Establishes, on the MODERN UD-EWT core-arg role gold (sentence-level held-out split), WHERE a brain-faithful
noisy-channel conflict gate helps and where it does not, with paired bootstrap CIs and the info-free twin.

The decisive finding is HONEST and mechanistic:
  * On the clean-parse AGGREGATE, the achievable gain comes from reliable STRUCTURAL ROUTING (detect strong
    passive morphology -> use the structural assigner; else word order), which needs NO thematic fit
    (route_only ~0.986 > word order 0.937 > graded_role 0.905). Adding a thematic-fit gate NET-HURTS the
    aggregate, because its cost on structure-silent CANONICAL items (plausible-but-atypical agents) swamps
    its help on the few structure-silent non-canonical ones. This REFUTES the brief's premise that thematic
    fit beats structure on non-canonical for CLEAN parses -- and it is exactly what the noisy-channel /
    Trueswell account predicts (fit is a disambiguation-under-uncertainty mechanism; a gold parse removes
    the uncertainty; research_thematic_fit_disambiguation_regime_2026-08-30.md).
  * The genuine contribution of grounded thematic fit is CONFINED to the STRUCTURE-SILENT NON-CANONICAL
    residual -- the exact regime the brain recruits it for. There, word order AND the structural assigner
    both collapse (~0.20), and the gate recovers role assignment CI-separated, with the info-free twin
    losing. On the class-imbalanced non-canonical subset this shows as a BALANCED-accuracy win over both floors.

Writes only to data/exp_grounded_role_gate_v1/. Does NOT modify hdlab/. No LLM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._grounded_role_data import load_items, split_by_sentence, add_animacy
from experiments._grounded_role_gate import (train_fit_model, count_fit_fn, make_noisy_channel_labeler,
                                             order_label, _strong_markedness)
from experiments._grounded_role_protofit import build_embeddings, build_prototypes, make_protofit_fn
from experiments.exp_grounded_role_baseline_v1 import graded_role_label, tag_reversible

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_gate_v1")
SEED = 20260830
N_BOOT = 2000
TAU = 1.0   # OUR-INVENTION recruitment threshold; swept in exp_grounded_role_uncertainty_curve_v1 (flat 1.0-2.5)


def _strong(it):
    return _strong_markedness(it["forms"], it["pos"], it["verb_ix"] + 1) > 0


def _correct_vec(items, fn):
    return np.array([int(fn(it) == it["role"]) for it in items], dtype=float)


def _paired_boot(a, b, seed=SEED):
    """(mean(a)-mean(b), lo2.5, hi97.5, half_width) of the paired bootstrap difference."""
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a)
    rng = np.random.default_rng(seed)
    d = np.array([a[idx].mean() - b[idx].mean() for idx in (rng.integers(0, n, n) for _ in range(N_BOOT))])
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return round(float(a.mean() - b.mean()), 4), round(lo, 4), round(hi, 4), round((hi - lo) / 2, 4)


def _balanced(items, fn):
    rec = {"agent": [0, 0], "patient": [0, 0]}
    for it in items:
        ok = int(fn(it) == it["role"])
        rec[it["role"]][0] += ok; rec[it["role"]][1] += 1
    parts = [rec[r][0] / rec[r][1] for r in rec if rec[r][1]]
    return sum(parts) / len(parts) if parts else float("nan")


def _balanced_boot(items, fa, fb, seed=SEED):
    """Paired bootstrap of the BALANCED-accuracy difference (resample clauses; macro over agent/patient)."""
    A = [(int(fa(it) == it["role"]), it["role"]) for it in items]
    B = [(int(fb(it) == it["role"]), it["role"]) for it in items]
    n = len(items); rng = np.random.default_rng(seed)

    def bal(sample, arr):
        rec = {"agent": [0, 0], "patient": [0, 0]}
        for i in sample:
            ok, r = arr[i]; rec[r][0] += ok; rec[r][1] += 1
        parts = [rec[r][0] / rec[r][1] for r in rec if rec[r][1]]
        return sum(parts) / len(parts) if len(parts) == 2 else np.nan
    ds = []
    for _ in range(N_BOOT):
        s = rng.integers(0, n, n)
        d = bal(s, A) - bal(s, B)
        if not np.isnan(d):
            ds.append(d)
    ds = np.array(ds)
    obs = _balanced(items, fa) - _balanced(items, fb)
    return round(float(obs), 4), round(float(np.percentile(ds, 2.5)), 4), round(float(np.percentile(ds, 97.5)), 4)


def _null_p95(items, fn, seed=SEED):
    """Label-permutation null: p95 of accuracy when gold roles are shuffled."""
    gold = np.array([1 if it["role"] == "agent" else 0 for it in items])
    pred = np.array([1 if fn(it) == "agent" else 0 for it in items])
    rng = np.random.default_rng(seed)
    accs = []
    for _ in range(N_BOOT):
        g = rng.permutation(gold)
        accs.append(np.mean((pred == 1) == (g == 1)))
    return round(float(np.percentile(accs, 95)), 4)


def run():
    items = add_animacy(load_items())
    train, test = split_by_sentence(items)
    tag_reversible(train); tag_reversible(test)

    cmodel = train_fit_model(train)
    cfit = count_fit_fn(cmodel)
    ctwin = count_fit_fn(train_fit_model(train, shuffle_roles=True))
    emb = build_embeddings(dim=100, max_vocab=12000)
    pfit = make_protofit_fn(emb, build_prototypes(train, emb), k=8.0)

    gate_c = make_noisy_channel_labeler(test, cfit, tau=TAU)
    gate_p = make_noisy_channel_labeler(test, pfit, tau=1.5)
    gate_tw = make_noisy_channel_labeler(test, ctwin, tau=TAU)
    route_only = lambda it: graded_role_label(it) if _strong(it) else order_label(it)          # NO fit
    composed_c = lambda it: graded_role_label(it) if _strong(it) else gate_c(it)                # structure+fit
    order = order_label

    # populations
    nc = [it for it in test if it["canon_type"] in ("passive", "inversion", "fronting")]
    canon = [it for it in test if it["canon_type"] == "canonical"]
    rev = [it for it in test if it.get("reversible")]
    resid_nc = [it for it in nc if not _strong(it)]   # STRUCTURE-SILENT non-canonical = the uncertainty residual

    def acc(pop, fn):
        return round(float(np.mean(_correct_vec(pop, fn))), 4) if pop else None

    arms = {"order": order, "graded_role": graded_role_label, "route_only": route_only,
            "gate_count": gate_c, "gate_proto": gate_p, "composed_count": composed_c, "gate_twin": gate_tw}
    table = {name: {"ALL": acc(test, fn), "canonical": acc(canon, fn), "NONCANON_raw": acc(nc, fn),
                    "NONCANON_bal": round(_balanced(nc, fn), 4), "reversible": acc(rev, fn),
                    "resid_nc": acc(resid_nc, fn)} for name, fn in arms.items()}

    # --- headline claims with paired bootstrap ---
    claims = {}
    # (1) AGGREGATE: routing beats both floors (the HONEST win -- no fit)
    claims["route_vs_order_ALL"] = _paired_boot(_correct_vec(test, route_only), _correct_vec(test, order))
    claims["route_vs_graded_ALL"] = _paired_boot(_correct_vec(test, route_only), _correct_vec(test, graded_role_label))
    # (2) STRUCTURE-SILENT NON-CANONICAL residual: fit recovers where order AND structure collapse
    claims["gateC_vs_order_residNC"] = _paired_boot(_correct_vec(resid_nc, gate_c), _correct_vec(resid_nc, order))
    claims["gateC_vs_graded_residNC"] = _paired_boot(_correct_vec(resid_nc, gate_c), _correct_vec(resid_nc, graded_role_label))
    claims["gateC_vs_twin_residNC"] = _paired_boot(_correct_vec(resid_nc, gate_c), _correct_vec(resid_nc, gate_tw))
    # (3) BALANCED non-canonical: fit beats both floors + twin (imbalance-robust)
    claims["gateC_vs_graded_NONCANON_bal"] = _balanced_boot(nc, gate_c, graded_role_label)
    claims["gateC_vs_order_NONCANON_bal"] = _balanced_boot(nc, gate_c, order)
    claims["gateC_vs_twin_NONCANON_bal"] = _balanced_boot(nc, gate_c, gate_tw)
    # (4) fit must NOT hurt canonical relative to order beyond a small margin -- reported, not gated

    nulls = {"gate_count_residNC_null_p95": _null_p95(resid_nc, gate_c),
             "route_only_ALL_null_p95": _null_p95(test, route_only)}

    verdict = {
        "AGGREGATE_win_is_ROUTING_not_fit":
            table["route_only"]["ALL"] > table["gate_count"]["ALL"] and table["route_only"]["ALL"] > table["order"]["ALL"],
        "fit_helps_the_structure_silent_residual":
            claims["gateC_vs_order_residNC"][1] > 0 and claims["gateC_vs_graded_residNC"][1] > 0,
        "twin_loses_on_residual": claims["gateC_vs_twin_residNC"][0] > 0,
        "fit_wins_balanced_noncanon_over_both_floors":
            claims["gateC_vs_graded_NONCANON_bal"][1] > 0 and claims["gateC_vs_order_NONCANON_bal"][1] > 0,
        "twin_loses_balanced_noncanon": claims["gateC_vs_twin_NONCANON_bal"][1] > 0,
        "brief_premise_refuted_on_clean_parses_raw_noncanon":
            table["gate_count"]["NONCANON_raw"] < table["graded_role"]["NONCANON_raw"],
    }
    return {"n_test": len(test), "n_noncanon": len(nc), "n_resid_nc": len(resid_nc),
            "n_resid_nc_agent": sum(it["role"] == "agent" for it in resid_nc),
            "n_canon": len(canon), "n_reversible": len(rev), "tau": TAU,
            "table": table, "claims": claims, "nulls": nulls, "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["n_resid_nc"] > 20, m["n_resid_nc"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 104)
    print("GROUNDED ROLE GATE -- consolidated (modern UD-EWT core-arg gold, sentence-level held-out)")
    print("=" * 104)
    print(f"n_test={m['n_test']} noncanon={m['n_noncanon']} structure-silent-noncanon(resid)={m['n_resid_nc']} "
          f"(agent={m['n_resid_nc_agent']}) canonical={m['n_canon']} reversible={m['n_reversible']}")
    cols = ["ALL", "canonical", "NONCANON_raw", "NONCANON_bal", "reversible", "resid_nc"]
    print(f"\n{'arm':16s}" + "".join(f"{c[:12]:>13s}" for c in cols))
    for name, r in m["table"].items():
        print(f"{name:16s}" + "".join(f"{str(r[c]):>13s}" for c in cols))
    print("\nHEADLINE CLAIMS (paired bootstrap: delta [lo, hi] (half-width)):")
    for k, v in m["claims"].items():
        print(f"  {k:34s} {v}")
    print("\nNULLS:", m["nulls"])
    print("VERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
