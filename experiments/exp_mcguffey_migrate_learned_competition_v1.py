"""exp_mcguffey_migrate_learned_competition_v1 -- THE FULL SOLUTION TEST: does a LEARNED competition of
order + morphology + GROUNDED thematic-fit reach BOTH domains and generalise to held-out inversion?

Deepening 4 showed the two cues have complementary domains (order->canonical 1.0; grounded thematic-fit->
non-canonical 0.688) and a HAND-SET combination underperforms both. The Competition Model says the weighting
must be LEARNED as conflict validity. This cell tests that: a glass-box logistic model over
[preverbal(order), passive(morphology), thematic_fit_logodds(grounded)] -- learned, no LLM -- vs SURFACE-ONLY
[preverbal, passive] and FIT-ONLY, on:
  1. IN-DISTRIBUTION (random split) -- does COMBINED reach order's canonical AND fit's non-canonical?
  2. CROSS-CONSTRUCTION (train canonical+passive, TEST ON UNSEEN INVERSION) -- does adding the grounded
     feature let the learned model generalise where surface-only walled (0.05)?
  3. TRAIN-BALANCED (upsample non-canonical) -- does exposing the learner to CONFLICT cases (Competition
     Model: conflict validity is learned from conflict exposure) unlock generalisation?
CAN-FAIL: COMBINED must (a) beat SURFACE-ONLY on the non-canonical / inversion cuts, (b) not lose to order on
canonical, (c) beat an info-free twin (shuffled labels). Selectional prefs learned on TRAIN only (no leakage).

Writes only to data/exp_mcguffey_migrate_learned_competition_v1/. Does NOT modify hdlab/.
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
from experiments.exp_mcguffey_migrate_learned_cue_transfer_v1 import fit_logreg  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_learned_competition_v1")
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu


def fit_logodds(model, verb, noun):
    ca, cp = model["vn"].get((verb, noun), [0, 0])
    na, npt = model["nn"].get(noun, [0, 0])
    ga, gp = model["glob"]
    a = 2.0 * ca + na + 0.5 * ga / max(1, ga + gp)
    p = 2.0 * cp + npt + 0.5 * gp / max(1, ga + gp)
    return float(np.log((a + 1e-6) / (p + 1e-6)))


def featurize(items, model, arm):
    X, y, ct = [], [], []
    for it in items:
        pre = 1.0 if it["preverbal"] else 0.0
        pas = 1.0 if it["canon_type"] == "passive" else 0.0
        fit = fit_logodds(model, it["verb"], it["noun"])
        if arm == "SURFACE":
            f = [pre, pas, 1.0]
        elif arm == "FIT":
            f = [fit, 1.0]
        else:  # COMBINED
            f = [pre, pas, fit, 1.0]
        X.append(f); y.append(1 if it["role"] == "agent" else 0); ct.append(it["canon_type"])
    return np.array(X, float), np.array(y, int), np.array(ct, object)


def acc_by_cut(w, X, y, ct):
    pred = (1.0 / (1.0 + np.exp(-(X @ w)))) >= 0.5
    ok = (pred.astype(int) == y)
    out = {"ALL": round(float(ok.mean()), 4)}
    for c in ("canonical", "passive", "inversion", "fronting"):
        m = (ct == c)
        out[c] = round(float(ok[m].mean()), 4) if m.sum() else None
    ncm = np.isin(ct, ["passive", "inversion", "fronting"])
    out["NONCANON"] = round(float(ok[ncm].mean()), 4) if ncm.sum() else None
    out["n"] = int(len(y))
    return out


def run_split(train_items, test_items, seed, balance=False):
    model = train_selpref(train_items)          # selectional prefs from TRAIN only
    if balance:
        nc = [it for it in train_items if it["canon_type"] != "canonical"]
        reps = max(1, len([it for it in train_items if it["canon_type"] == "canonical"]) // max(1, len(nc)))
        train_items = train_items + nc * (reps - 1)
    res = {}
    rng = np.random.default_rng(seed)
    for arm in ("SURFACE", "FIT", "COMBINED"):
        Xtr, ytr, _ = featurize(train_items, model, arm)
        Xte, yte, cte = featurize(test_items, model, arm)
        w = fit_logreg(Xtr, ytr)
        res[arm] = acc_by_cut(w, Xte, yte, cte)
    # info-free twin on COMBINED
    Xtr, ytr, _ = featurize(train_items, model, "COMBINED")
    Xte, yte, cte = featurize(test_items, model, "COMBINED")
    w_tw = fit_logreg(Xtr, rng.permutation(ytr))
    res["COMBINED_TWIN"] = acc_by_cut(w_tw, Xte, yte, cte)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    items = core_args(parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST))
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(items)); cut = int(0.7 * len(items))
    tr = [items[i] for i in idx[:cut]]; te = [items[i] for i in idx[cut:]]

    indist = run_split(tr, te, args.seed)

    # cross-construction: train canonical+passive, test inversion
    tr_cc = [it for it in items if it["canon_type"] in ("canonical", "passive")]
    te_cc = [it for it in items if it["canon_type"] == "inversion"]
    crosscon = run_split(tr_cc, te_cc, args.seed)
    crosscon_bal = run_split(tr_cc, te_cc, args.seed, balance=True)

    def g(d, arm, cut):
        return (d.get(arm) or {}).get(cut)

    verdict = {
        "indist_combined_reaches_both_domains":
            (g(indist, "COMBINED", "canonical") or 0) >= (g(indist, "SURFACE", "canonical") or 0) - 0.03 and
            (g(indist, "COMBINED", "NONCANON") or 0) > (g(indist, "SURFACE", "NONCANON") or 0) + 0.1,
        "indist_combined_beats_twin": (g(indist, "COMBINED", "ALL") or 0) > (g(indist, "COMBINED_TWIN", "ALL") or 0),
        "crosscon_combined_beats_surface_on_inversion":
            (g(crosscon, "COMBINED", "inversion") or 0) > (g(crosscon, "SURFACE", "inversion") or 0),
        "balanced_training_helps_inversion":
            (g(crosscon_bal, "COMBINED", "inversion") or 0) > (g(crosscon, "COMBINED", "inversion") or 0),
        "numbers": {
            "indist": {a: {"canonical": g(indist, a, "canonical"), "NONCANON": g(indist, a, "NONCANON"),
                           "ALL": g(indist, a, "ALL")} for a in ("SURFACE", "FIT", "COMBINED")},
            "crosscon_inversion": {a: g(crosscon, a, "inversion") for a in ("SURFACE", "FIT", "COMBINED")},
            "crosscon_balanced_inversion": {a: g(crosscon_bal, a, "inversion") for a in ("SURFACE", "COMBINED")},
        },
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "in_distribution": indist, "cross_construction": crosscon,
               "cross_construction_balanced": crosscon_bal, "verdict": verdict}

    if args.self_test:
        assert len(items) > 1000
        print("self-test PASS", json.dumps(verdict["numbers"]["indist"]["COMBINED"]))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 92)
    print("LEARNED CUE COMPETITION (order + morphology + GROUNDED thematic-fit; glass-box, no LLM)")
    print("=" * 92)
    print("\n[1] IN-DISTRIBUTION (random split) -- does COMBINED reach BOTH domains?")
    print(f"    {'arm':10s} {'canonical':>10s} {'NONCANON':>10s} {'ALL':>8s}")
    for a in ("SURFACE", "FIT", "COMBINED", "COMBINED_TWIN"):
        print(f"    {a:10s} {str(g(indist,a,'canonical')):>10s} {str(g(indist,a,'NONCANON')):>10s} {str(g(indist,a,'ALL')):>8s}")
    print("\n[2] CROSS-CONSTRUCTION (train canonical+passive -> TEST UNSEEN INVERSION)")
    for a in ("SURFACE", "FIT", "COMBINED"):
        print(f"    {a:10s} inversion={g(crosscon,a,'inversion')}   (balanced-train COMBINED={g(crosscon_bal,'COMBINED','inversion')})")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
