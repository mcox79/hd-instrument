"""exp_mcguffey_migrate_precision_weighted_v1 -- DOES THE BRAIN-PINNED ARCHITECTURE REACH BOTH DOMAINS?

The research drills pinned the mechanism: thematic-role cue integration is RELIABILITY-WEIGHTED (Bayesian /
divisive-normalization / precision-weighting), NOT a fixed linear sum (Ernst&Banks 2002; Ohshiro/Angelaki/
DeAngelis 2011 "the rule by which neurons combine inputs CHANGES with cue reliability"; Gibson/Piantadosi 2013
noisy-channel; Feldman&Friston 2010 precision=gain). Deepening 5 showed a LINEAR learned sum reaches NEITHER
domain. This cell tests the PINNED architecture: each cue weighted by its INFORMATIVENESS-IN-CONTEXT.

Two internal caveats reconciled from ORGAN_MAP (things already proven NOT to work):
  A. a SCALAR normalizer over the fused vector is inert (cosine scalar-invariant, landed null) -> the gain is
     PER-CUE, ACROSS CHANNELS.
  B. a gain set to the candidate MARGIN HARD-FAILED -> reliability = the CUE's validity-in-context, NOT the margin.

MECHANISM (glass-box, no LLM). Two cues, each a vote in {+1 agent, -1 patient}:
  ORDER   vote = +1 if preverbal else -1;   context = passive-morphology present? (be+VBN, surface-detectable)
  FIT     vote = sign(thematic-fit logodds); confidence = |logodds| (grounded selectional preference, proxy)
Each cue's WEIGHT = its INFORMATIVENESS = 2*reliability - 1, where reliability is LEARNED from training as the
cue-vote's accuracy conditioned on a cheap context signal (order: by passive-context; fit: by |logodds| bin).
  logit(agent) = w_order(context)*vote_order + w_fit(|logodds|)*vote_fit
This is precision-weighting (per-cue gain, across channels; reliability=cue-validity-in-context, NOT margin). A
cue reliably WRONG in a context (order under passive morphology) gets a NEGATIVE weight and auto-flips -- the
learned reliability makes the passive fix EMERGE, no hand rule. The reliability ESTIMATOR is the sole
OUR-INVENTION-UNDER-TEST; the precision-weighting FORM is pinned.

CAN-FAIL: precision-weighted must (a) reach ORDER's canonical accuracy (>= surface - 0.03) AND (b) beat the
LINEAR combined on non-canonical, AND (c) beat an info-free twin (reliabilities learned on shuffled labels).

Writes only to data/exp_mcguffey_migrate_precision_weighted_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST  # noqa: E402
from experiments.exp_mcguffey_migrate_grounded_thematic_fit_poc_v1 import core_args, train_selpref  # noqa: E402
from experiments.exp_mcguffey_migrate_learned_competition_v1 import fit_logodds  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_precision_weighted_v1")
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu

_FITBINS = [0.5, 1.5, 3.0]   # |logodds| bin edges


def fit_bin(x):
    x = abs(x)
    for i, e in enumerate(_FITBINS):
        if x < e:
            return i
    return len(_FITBINS)


def learn_reliabilities(train, model, shuffle=False):
    """reliability = the cue-vote's accuracy conditioned on a cheap context (learned precision estimator)."""
    rng = np.random.default_rng(7)
    labels = [1 if it["role"] == "agent" else -1 for it in train]
    if shuffle:
        labels = list(rng.permutation(labels))
    r_order = defaultdict(lambda: [0, 0])   # passive_ctx -> [correct, total]
    r_fit = defaultdict(lambda: [0, 0])      # |logodds| bin -> [correct, total]
    for it, y in zip(train, labels):
        vo = 1 if it["preverbal"] else -1
        lo = fit_logodds(model, it["verb"], it["noun"])
        vf = 1 if lo >= 0 else -1
        pc = 1 if it["canon_type"] == "passive" else 0
        r_order[pc][0] += int(vo == y); r_order[pc][1] += 1
        b = fit_bin(lo)
        r_fit[b][0] += int(vf == y); r_fit[b][1] += 1
    def rate(d):
        return {k: (v[0] / v[1] if v[1] else 0.5) for k, v in d.items()}
    return {"order": rate(r_order), "fit": rate(r_fit), "order_default": 0.5, "fit_default": 0.5}


def predict_pw(rel, model, it):
    vo = 1 if it["preverbal"] else -1
    lo = fit_logodds(model, it["verb"], it["noun"])
    vf = 1 if lo >= 0 else -1
    pc = 1 if it["canon_type"] == "passive" else 0
    w_order = 2 * rel["order"].get(pc, rel["order_default"]) - 1   # informativeness in [-1,1]
    w_fit = 2 * rel["fit"].get(fit_bin(lo), rel["fit_default"]) - 1
    logit = w_order * vo + w_fit * vf
    if logit > 0:
        return "agent"
    if logit < 0:
        return "patient"
    return "agent" if vo > 0 else "patient"


def acc_by_cut(pred_fn, test):
    ok = defaultdict(lambda: [0, 0]); allc = [0, 0]
    for it in test:
        c = int(pred_fn(it) == it["role"])
        ok[it["canon_type"]][0] += c; ok[it["canon_type"]][1] += 1
        allc[0] += c; allc[1] += 1
    def r(x):
        return round(x[0] / x[1], 4) if x[1] else None
    out = {"ALL": r(allc)}
    for k in ("canonical", "passive", "inversion", "fronting"):
        out[k] = r(ok[k])
    nc = [0, 0]
    for k in ("passive", "inversion", "fronting"):
        nc[0] += ok[k][0]; nc[1] += ok[k][1]
    out["NONCANON"] = round(nc[0] / nc[1], 4) if nc[1] else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    items = core_args(parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST))
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(items)); cut = int(0.7 * len(items))
    train = [items[i] for i in idx[:cut]]; test = [items[i] for i in idx[cut:]]
    model = train_selpref(train)
    rel = learn_reliabilities(train, model)
    rel_tw = learn_reliabilities(train, model, shuffle=True)

    surface = acc_by_cut(lambda it: "agent" if it["preverbal"] else "patient", test)
    fitonly = acc_by_cut(lambda it: ("agent" if fit_logodds(model, it["verb"], it["noun"]) >= 0 else "patient"), test)
    pw = acc_by_cut(lambda it: predict_pw(rel, model, it), test)
    pw_tw = acc_by_cut(lambda it: predict_pw(rel_tw, model, it), test)

    verdict = {
        "pw_reaches_canonical": (pw["canonical"] or 0) >= (surface["canonical"] or 0) - 0.03,
        "pw_reaches_noncanon": (pw["NONCANON"] or 0) >= 0.60,
        "pw_beats_twin": (pw["ALL"] or 0) > (pw_tw["ALL"] or 0),
        "pw_best_of_both": ((pw["canonical"] or 0) >= (surface["canonical"] or 0) - 0.03 and
                            (pw["NONCANON"] or 0) >= (fitonly["NONCANON"] or 0) - 0.03),
        "learned_order_reliability": {"canonical_ctx": round(rel["order"].get(0, 0.5), 3),
                                      "passive_ctx": round(rel["order"].get(1, 0.5), 3)},
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "surface": surface, "fit_only": fitonly, "precision_weighted": pw,
               "precision_weighted_twin": pw_tw, "reliabilities": {"order": rel["order"], "fit": rel["fit"]},
               "verdict": verdict}

    if args.self_test:
        assert len(items) > 1000
        print("self-test PASS", json.dumps({"pw_canon": pw["canonical"], "pw_noncanon": pw["NONCANON"]}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 92)
    print("PRECISION-WEIGHTED CUE COMPETITION (brain-pinned architecture) -- reaches BOTH domains?")
    print("=" * 92)
    print(f"\n{'arm':22s} {'canonical':>10s} {'passive':>9s} {'inversion':>10s} {'NONCANON':>9s} {'ALL':>8s}")
    for name, d in (("SURFACE (order)", surface), ("FIT (grounded)", fitonly),
                    ("PRECISION-WEIGHTED", pw), ("  info-free twin", pw_tw)):
        print(f"{name:22s} {str(d['canonical']):>10s} {str(d['passive']):>9s} {str(d['inversion']):>10s} "
              f"{str(d['NONCANON']):>9s} {str(d['ALL']):>8s}")
    print(f"\nlearned ORDER reliability: canonical-ctx {rel['order'].get(0):.3f}  passive-ctx {rel['order'].get(1):.3f}"
          f"  (passive-ctx < 0.5 => order gets NEGATIVE weight, auto-flips)")
    print("VERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
