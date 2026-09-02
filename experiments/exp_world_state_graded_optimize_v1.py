"""exp_world_state_graded_optimize_v1 -- prototype graded_coref_pick AS the register's he/she densifier and
OPTIMIZE it, driven by the #3 residual finding (the misses are LONG-DISTANCE, not pool competition).

BRAIN-FOUNDATIONAL HYPOTHESIS: the ACT-R base-level activation A = ln(sum_k role_w(k) * dt_k^-d) is copied
(PINNED computation), but the decay exponent d is a PARAMETER (a memory constraint we do not share) -- and it is
DEV-tuned to 3.0 (STEEP: far antecedents are heavily penalized). Since the residual is long-distance, a SMALLER d
(slower decay) should recover more far antecedents. Sweep d (and a couple of cue-weight variants) on a TRAIN split
of LitBank docs; evaluate the picked setting on a HELD-OUT test split (never grade on the tuning data). Info-free
control: a random-antecedent twin. Reports resolver accuracy (he/she coref) = the register's he/she who-has-what
ceiling. NO spaCy/LLM (pure re-picking over cached candidate pools). ASCII only.
# KB_REFERENT: data/corpora/litbank_coref_conll
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_world_state_he_she_ceiling_v1 import role_of, MASC, FEM

ANCHOR = "world_state_graded_optimize_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")


def doc_targets(path):
    """Per he/she target: (candidate_priors, cand_clusters, gold_cluster, p_sent, pron_role). Pools are gn-compatible
    + landed pool-cleanup; params-independent so the sweep is pure re-picking."""
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets, load_name_gender
    from hdlab.graded_coref_pick import keep_after_pool_cleanup
    from collections import defaultdict
    gaz = load_name_gender()
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    if not mentions:
        return []
    cl_mentions = defaultdict(list)
    for m in mentions:
        cl_mentions[m["cluster"]].append(m)
    cl_gender = {}
    for c, ms in cl_mentions.items():
        gs = [(mm.get("gender") or mm.get("name_gender")) for mm in ms]
        gs = [g for g in gs if g in ("masc", "fem")]
        cl_gender[c] = (max(set(gs), key=gs.count) if gs else None)
    out = []
    for tgt in build_pronoun_targets(mentions):
        P = tgt["target"]
        g_p = "masc" if P["head"] in MASC else ("fem" if P["head"] in FEM else None)
        if g_p is None:
            continue
        m_p = P["midx"]
        cand_clusters, cand_priors, cand_heads = [], [], []
        for c, ms in cl_mentions.items():
            priors = [(mm["sent_idx"], role_of(mm)) for mm in ms if mm["midx"] < m_p]
            if not priors or cl_gender[c] not in (g_p, None):
                continue
            cand_clusters.append(c); cand_priors.append(priors)
            cand_heads.append([mm["head"] for mm in ms if mm["midx"] < m_p])
        if not cand_clusters:
            continue
        keep = keep_after_pool_cleanup(cand_heads)
        kc = [cand_clusters[i] for i in keep] or cand_clusters
        kp = [cand_priors[i] for i in keep] or cand_priors
        out.append({"priors": kp, "clusters": kc, "gold": P["cluster"],
                    "p_sent": P["sent_idx"], "pron_role": role_of(P)})
    return out


def acc_for(targets, weights, gain, d):
    from hdlab.graded_coref_pick import graded_antecedent_pick
    hit = 0
    for t in targets:
        g = graded_antecedent_pick(t["priors"], p_sent=t["p_sent"], pron_role=t["pron_role"],
                                   weights=weights, gain=gain, d=d)
        pick = t["clusters"][g["pick"]] if g["pick"] >= 0 else None
        hit += int(pick == t["gold"])
    return hit / len(targets) if targets else 0.0


def boot_ci(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return (None, [None, None])
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    return (round(float(vals.mean()), 4), [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)])


def per_item_correct(targets, weights, gain, d):
    from hdlab.graded_coref_pick import graded_antecedent_pick
    out = []
    for t in targets:
        g = graded_antecedent_pick(t["priors"], p_sent=t["p_sent"], pron_role=t["pron_role"],
                                   weights=weights, gain=gain, d=d)
        pick = t["clusters"][g["pick"]] if g["pick"] >= 0 else None
        out.append(int(pick == t["gold"]))
    return out


def run(mode="full", n_boot=2000, seed=20260902):
    import hdlab.graded_coref_pick as G
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    if mode == "smoke":
        files = files[:6]
    all_by_doc = []
    for f in files:
        t = doc_targets(f)
        if t:
            all_by_doc.append(t)
    # deterministic doc split (even index -> train, odd -> test)
    train = [t for i, d in enumerate(all_by_doc) if i % 2 == 0 for t in d]
    test = [t for i, d in enumerate(all_by_doc) if i % 2 == 1 for t in d]

    D_GRID = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    WEIGHT_VARIANTS = {
        "default": dict(G.TUNED_WEIGHTS),
        "+recency": {**G.TUNED_WEIGHTS, "recency": 0.5},
        "+first": {**G.TUNED_WEIGHTS, "first": 0.5},
        "+recency+first": {**G.TUNED_WEIGHTS, "recency": 0.5, "first": 0.5},
    }
    default_w, default_gain, default_d = dict(G.TUNED_WEIGHTS), G.DEFAULT_GAIN, G.DEFAULT_ACTR_D

    # --- d sweep on TRAIN (weights=default) ---
    d_curve_train = [(d, round(acc_for(train, default_w, default_gain, d), 4)) for d in D_GRID]
    best_d = max(d_curve_train, key=lambda x: x[1])[0]

    # --- weight-variant sweep on TRAIN (at best_d) ---
    w_train = {name: round(acc_for(train, w, default_gain, best_d), 4) for name, w in WEIGHT_VARIANTS.items()}
    best_w_name = max(w_train, key=w_train.get)
    best_w = WEIGHT_VARIANTS[best_w_name]

    # --- evaluate on HELD-OUT TEST: default vs tuned (best_d, best_w) ---
    def_test = per_item_correct(test, default_w, default_gain, default_d)
    tuned_test = per_item_correct(test, best_w, default_gain, best_d)
    def_acc, def_ci = boot_ci(def_test, n_boot, seed + 1)
    tun_acc, tun_ci = boot_ci(tuned_test, n_boot, seed + 2)
    d = np.asarray(tuned_test, float) - np.asarray(def_test, float)
    rng = np.random.default_rng(seed + 3)
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    delta = {"delta": round(float(d.mean()), 4),
             "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}

    # d curve on TEST too (diagnostic, not model selection)
    d_curve_test = [(dd, round(acc_for(test, default_w, default_gain, dd), 4)) for dd in D_GRID]

    return {
        "anchor": ANCHOR, "mode": mode, "n_train": len(train), "n_test": len(test),
        "default_params": {"d": default_d, "gain": default_gain, "weights": default_w},
        "d_curve_train": d_curve_train, "best_d_on_train": best_d,
        "weight_sweep_train_at_best_d": w_train, "best_weights_on_train": best_w_name,
        "d_curve_test_diagnostic": d_curve_test,
        "HELDOUT_default": {"acc": def_acc, "ci": def_ci},
        "HELDOUT_tuned": {"acc": tun_acc, "ci": tun_ci, "d": best_d, "weights": best_w_name},
        "tuned_minus_default_heldout": delta,
        "tuned_beats_default_CIsep": bool(delta["ci"][0] > 0),
    }


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    from hdlab.graded_coref_pick import graded_antecedent_pick
    # a FAR topical subject (sents 0,1) vs a NEAR oblique (sent 5); small d (slow decay) should keep the topical one.
    cp = [[(0, "SUBJECT"), (1, "SUBJECT")], [(5, "OTHER")]]
    import hdlab.graded_coref_pick as G
    g_steep = graded_antecedent_pick(cp, p_sent=6, d=4.0, weights=G.TUNED_WEIGHTS)
    g_slow = graded_antecedent_pick(cp, p_sent=6, d=0.5, weights=G.TUNED_WEIGHTS)
    print("[self-test] steep d=4 pick=%d ; slow d=0.5 pick=%d (slow should favor the topical far subject, idx0)"
          % (g_steep["pick"], g_slow["pick"]), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    print("\n  GRADED optimize (LitBank he/she; train=%d test=%d):" % (res["n_train"], res["n_test"]), flush=True)
    print("  d-curve (TRAIN): %s -> best d=%s (default=%s)" % (res["d_curve_train"], res["best_d_on_train"], res["default_params"]["d"]), flush=True)
    print("  weight sweep (TRAIN @best d): %s -> best=%s" % (res["weight_sweep_train_at_best_d"], res["best_weights_on_train"]), flush=True)
    print("  d-curve (TEST, diagnostic): %s" % res["d_curve_test_diagnostic"], flush=True)
    print("  HELD-OUT: default %.3f %s  ->  tuned(d=%s,%s) %.3f %s"
          % (res["HELDOUT_default"]["acc"], res["HELDOUT_default"]["ci"], res["HELDOUT_tuned"]["d"],
             res["HELDOUT_tuned"]["weights"], res["HELDOUT_tuned"]["acc"], res["HELDOUT_tuned"]["ci"]), flush=True)
    print("  tuned-default (held-out) %.3f %s  CI-sep=%s"
          % (res["tuned_minus_default_heldout"]["delta"], res["tuned_minus_default_heldout"]["ci"], res["tuned_beats_default_CIsep"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
