"""exp_consolidation_discriminative_rescore_v1 -- the MFS-QUARANTINE discriminative consolidation, re-scored on
the CACHED read-and-bind store (no re-read). Targets the exact residual the signal-loss trace isolated: our
reading-derived associates are TOPICAL/dominant-sense-biased, not sense-DISCRIMINATIVE. Curated SyntagNet helps
(+0.060) because its pairs are discriminative; ours do not.

BRAIN MECHANISM: biased competition (Jefferies 2013; Lambon-Ralph 2017) applied to the ACQUIRED associations --
keep an associate w for sense s ONLY IF s binds w MORE than its dominant lexical competitor does (per-sense
binding rate cooc[s][w]/sel[s] vs the max sibling rate). This quarantines the dominant-sense-shared (topical)
associates that flood a rare sense -- the "quarantine MFS-dominated edges" lever both research drills named.

Compares, on strict doc-disjoint SemCor subordinate (odd docs), mean readout via hdlab.diagnostic_context_wsd:
  gloss | v2 recurrence-only (all bound, recur-filtered) | DISCRIMINATIVE (MFS-quarantine) | curated SyntagNet.
Sweep (ratio, K) on DEV (even docs), report frozen on TEST. Glass-box, NO external LLM, gold only as the doc split.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1

_CACHE = G1._CACHE
STORE_PATH = os.path.join(_CACHE, "consol_readbind_0_4229728908.pkl")   # the landed full read-and-bind store
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_discriminative_rescore_v1")


def recurrence_assocs(syn, store, K, cap):
    cs = store["cooc"].get(syn, {})
    ws = [(w, c) for w, c in cs.items() if c >= K]
    ws.sort(key=lambda x: -x[1])
    return [w for w, _ in ws[:cap]]


def discriminative_assocs(syn, sibs, store, K, ratio, cap):
    """Keep w only if the rare sense binds it MORE than its best sibling competitor (MFS-quarantine)."""
    cooc = store["cooc"]; sel = store["sel"]
    cs = cooc.get(syn, {}); ns = sel.get(syn, 0)
    if ns == 0:
        return []
    scored = []
    for w, c in cs.items():
        if c < K:
            continue
        rate_s = c / ns
        rs = 0.0
        for sib in sibs:
            nsib = sel.get(sib, 0)
            if nsib > 0:
                r = cooc.get(sib, {}).get(w, 0) / nsib
                if r > rs:
                    rs = r
        if rate_s > ratio * rs:
            scored.append((w, rate_s - rs))
    scored.sort(key=lambda x: -x[1])
    return [w for w, _ in scored[:cap]]


def run(cap, smoke=False, store_path=STORE_PATH, tag="full"):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    store = pickle.load(open(store_path, "rb"))
    print("[run] store=%s (%d senses, %d binds)" % (os.path.basename(store_path), len(store["cooc"]),
          store.get("n_binds", -1)), flush=True)
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0]); test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        dev_idx = dev_idx[:300]; test_idx = test_idx[:300]
    cand = set()
    for i in dev_idx + test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in cand}
    sib_by_syn = {s: G1._siblings(s) for s in cand}
    Ctx_dev = G1.precompute_ctx(recs, dev_idx, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test_idx, mat, w2i)
    print("[run] dev=%d test=%d cand=%d store_senses=%d (%.0fs)"
          % (len(dev_idx), len(test_idx), len(cand), len(store["cooc"]), time.time() - t0), flush=True)

    def a_s(idxs, Ctx, assoc):
        return G1.score(recs, idxs, G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i), Ctx)

    gloss = {s: [] for s in cand}
    gdev = a_s(dev_idx, Ctx_dev, gloss); gtest = a_s(test_idx, Ctx_test, gloss)

    # sweep discriminative (ratio,K) on DEV
    sweep = {}
    best = None; best_dev = -1; best_assoc = None
    for ratio in [1.0, 1.5, 2.0]:
        for K in [2, 3]:
            assoc = {s: discriminative_assocs(s, sib_by_syn[s], store, K, ratio, cap) for s in cand}
            dv = float(a_s(dev_idx, Ctx_dev, assoc).mean())
            na = float(np.mean([len(assoc[s]) for s in cand]))
            sweep["ratio%.1f_K%d" % (ratio, K)] = {"dev": round(dv, 4), "assoc": round(na, 2)}
            print("[sweep] discr ratio=%.1f K=%d dev=%.4f assoc/sense=%.1f (%.0fs)"
                  % (ratio, K, dv, na, time.time() - t0), flush=True)
            if dv > best_dev:
                best_dev = dv; best = (ratio, K); best_assoc = assoc
    disc_test = a_s(test_idx, Ctx_test, best_assoc)

    # references
    recur_assoc = {s: recurrence_assocs(s, store, best[1], cap) for s in cand}
    recur_test = a_s(test_idx, Ctx_test, recur_assoc)
    syntag_assoc = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    syntag_test = a_s(test_idx, Ctx_test, syntag_assoc)

    n = min(len(gtest), len(disc_test), len(recur_test))
    res = {"n_dev": len(dev_idx), "n_test": len(test_idx), "cap": cap, "best_discr_cfg": {"ratio": best[0], "K": best[1]},
           "sweep": sweep,
           "a_s_test": {"gloss": round(float(gtest.mean()), 4),
                        "recurrence_only": round(float(recur_test.mean()), 4),
                        "DISCRIMINATIVE_mfs_quarantine": round(float(disc_test.mean()), 4),
                        "curated_syntagnet": round(float(syntag_test.mean()), 4)},
           "mean_assoc_discr": round(float(np.mean([len(best_assoc[s]) for s in cand])), 2),
           "DISCR_vs_gloss": G1._paired(disc_test[:n], gtest[:n], 401),
           "DISCR_vs_recurrence": G1._paired(disc_test[:n], recur_test[:n], 402),
           "syntagnet_vs_gloss": G1._paired(syntag_test[:n], gtest[:n], 403)}
    res["headline"] = ("DISCRIMINATIVE MFS-QUARANTINE | gloss=%.3f recur=%.3f DISCR=%.3f(sep_vs_gloss=%s,null=%s) "
                       "curated=%.3f(sep=%s) | best=%s assoc/sense=%.1f"
                       % (res["a_s_test"]["gloss"], res["a_s_test"]["recurrence_only"],
                          res["a_s_test"]["DISCRIMINATIVE_mfs_quarantine"], res["DISCR_vs_gloss"]["sep"],
                          res["DISCR_vs_gloss"]["null_p95"], res["a_s_test"]["curated_syntagnet"],
                          res["syntagnet_vs_gloss"]["sep"], res["best_discr_cfg"], res["mean_assoc_discr"]))
    res["store"] = os.path.basename(store_path)
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else tag)), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_discriminative_rescore_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    store = {"cooc": {"rare.n.01": {"river": 5, "money": 5}, "dom.n.01": {"money": 50}},
             "sel": {"rare.n.01": 10, "dom.n.01": 100}}
    out = discriminative_assocs("rare.n.01", ["dom.n.01"], store, K=2, ratio=1.0, cap=5)
    # river: rate_s=0.5 vs sib 0 -> keep; money: rate_s=0.5 vs sib 0.5 -> NOT > 1.0*0.5 -> drop
    assert out == ["river"], "MFS-quarantine keeps the rare-distinctive word, drops the dominant-shared one: %s" % out
    print("SELFTEST PASS", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--store-path", default=STORE_PATH)
    ap.add_argument("--tag", default="full")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.cap, smoke=args.smoke, store_path=args.store_path, tag=args.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
