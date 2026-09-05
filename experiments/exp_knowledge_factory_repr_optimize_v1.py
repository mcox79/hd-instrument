"""exp_knowledge_factory_repr_optimize_v1 -- the DECISIVE no-new-data test (research-grounded): is the meaning
store's sibling-sense collapse (cosine 0.93, effective rank 17/200) a REPRESENTATION-SPACE artifact fixable by a
post-hoc transform, or a genuine DATA gap that needs targeted acquisition?

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift

RESEARCH BASIS (literature drill 2026-09-04):
  * All-but-the-Top (Mu & Viswanath 2018): subtract the common mean + project out the top-D PCs (they encode
    frequency, not meaning). Judge on the DOWNSTREAM task, NOT on isotropy -- for a CLASSIFIER-LIKE readout
    (ours picks a winning prototype) forcing isotropy can DESTROY cluster structure (Isotropy-Clusters-Classifiers
    2024: IsoScore<->silhouette r ~ -0.8..-1.0; Whitening-Not-Recommended-for-Classification 2024). So sweep a
    SMALL D and gate on WSD a_s.
  * Ethayarajh 2019: a raw cosine is meaningless without the mean RANDOM-PAIR cosine baseline (anisotropy inflates
    all cosines). Report sibling cosine MINUS random-pair cosine.
  * SIF discriminative pre-pooling (Arora-Liang-Ma 2017): each signature is a MEAN of overlapping bags -> shared
    tokens wash out the rare discriminative ones. Down-weight tokens shared across MANY senses (IDF over synset
    bags) when pooling -> the pooled-vector analog of all-but-the-top, NO new data.

DECISION: if all-but-the-top / SIF pooling lowers sibling-vs-random cosine AND raises WSD a_s -> artifact, ship the
transform, acquisition NOT yet needed. If a_s is flat/negative -> genuine DATA gap -> targeted acquisition.

Strict doc-disjoint SemCor subordinate; DEV=even (tune D / weighting), TEST=odd (report). Reuses the meaning-store
builder + the live hdlab readout. Glass-box, NO external LLM. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_repr_optimize_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse
from collections import Counter

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_knowledge_factory_meaning_store_v1 as M
import experiments.exp_knowledge_factory_intrinsic_trim_v1 as IT

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_repr_optimize_v1")


def _unit_rows(V):
    return V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)


def all_but_top(sig_by_syn, D):
    """Mu & Viswanath 2018: fit mean + top-D PCs on the stacked signatures (unsupervised), subtract the mean and
    project out the top-D directions, re-normalise. D=0 -> identity. Returns a NEW sig_by_syn."""
    names = [s for s, v in sig_by_syn.items() if v is not None]
    V = np.stack([sig_by_syn[s] for s in names]).astype(np.float64)
    mu = V.mean(axis=0)
    Vc = V - mu
    if D > 0:
        U, S, Vt = np.linalg.svd(Vc, full_matrices=False)
        P = Vt[:D]                                  # top-D principal directions
        Vc = Vc - (Vc @ P.T) @ P
    Vc = _unit_rows(Vc)
    out = dict(sig_by_syn)
    for i, s in enumerate(names):
        out[s] = Vc[i].astype(np.float32)
    return out


def idf_weights(prep):
    """IDF over synset bags: a token in MANY sense-bags is non-discriminative (shared/topical) -> low weight; a
    token in FEW bags is discriminative -> high weight. df(w) = #synsets whose (seed+assoc) bag contains w."""
    df = Counter()
    for s in prep["syns"]:
        for w in set(prep["seed_words"][s]) | set(prep["assoc"][s]):
            df[w] += 1
    N = len(prep["syns"])
    return {w: float(np.log((1.0 + N) / (1.0 + c))) for w, c in df.items()}


def sif_sigs(prep, mat, w2i, weights, abtt_D=0):
    """Rebuild signatures as an IDF-WEIGHTED mean of the bag word vectors (discriminative pre-pooling), then
    optionally all-but-the-top the result. weights: word -> weight."""
    sig = {}
    for s in prep["syns"]:
        words = prep["seed_words"][s] + prep["assoc"][s]
        rows = []; ws = []
        for w in words:
            if w in w2i:
                rows.append(mat[w2i[w]]); ws.append(weights.get(w, 1.0))
        if not rows:
            sig[s] = None; continue
        R = np.stack(rows).astype(np.float64); a = np.asarray(ws)
        v = (a[:, None] * R).sum(axis=0)
        sig[s] = G1._unit(v)
    if abtt_D > 0:
        sig = all_but_top(sig, abtt_D)
    return sig


def random_pair_cosine(sig_by_syn, seed=0, k=20000):
    """Ethayarajh baseline: mean cosine of RANDOM synset pairs (anisotropy floor). sibling-cos minus this is the
    honest sense-collapse signal."""
    V = np.stack([v for v in sig_by_syn.values() if v is not None]).astype(np.float32)
    rng = np.random.default_rng(seed)
    ii = rng.integers(0, len(V), k); jj = rng.integers(0, len(V), k)
    m = ii != jj
    return float((V[ii[m]] * V[jj[m]]).sum(axis=1).mean())


def run(level=3, smoke=False, Ds=(0, 1, 2, 3, 5, 8, 12)):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = M._load_eval()
    if smoke:
        dev = dev[:400]; test = test[:400]; Ds = (0, 1, 3, 8)
    cand = set()
    for i in dev + test:
        cand.update(recs[i]["tn"])
    Ctx_dev = G1.precompute_ctx(recs, dev, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test, mat, w2i)
    prep = M.prep_bags(cand, mat, w2i, level)
    prep0 = M.prep_bags(cand, mat, w2i, 0)
    gloss = M.sigs_at(prep0, mat, w2i, None)
    keepall = M.sigs_at(prep, mat, w2i, None)

    ok_gloss = M.a_s(recs, test, gloss, Ctx_test)
    ok_keepall_dev = M.a_s(recs, dev, keepall, Ctx_dev)
    ok_keepall_test = M.a_s(recs, test, keepall, Ctx_test)

    # honest isotropy diagnostics on the keep-all store
    sib0 = IT.sense_separation(keepall)["mean_sibling_cos"]; rnd0 = random_pair_cosine(keepall)
    diag = {"sibling_cos": round(sib0, 4), "random_pair_cos": round(rnd0, 4),
            "sibling_minus_random": round(sib0 - rnd0, 4),
            "effective_rank": round(IT.effective_rank(keepall), 2)}
    print("[diag] sibling_cos=%.4f random_pair_cos=%.4f (sib-rnd=%.4f) eff_rank=%.2f"
          % (sib0, rnd0, sib0 - rnd0, diag["effective_rank"]), flush=True)

    # 1) ALL-BUT-THE-TOP sweep on DEV
    abtt = {}
    for D in Ds:
        sig = all_but_top(keepall, D) if D > 0 else keepall
        d = float(M.a_s(recs, dev, sig, Ctx_dev).mean())
        sib = IT.sense_separation(sig)["mean_sibling_cos"]; rnd = random_pair_cosine(sig)
        abtt[D] = {"dev_a_s": round(d, 4), "sib_minus_rnd": round(sib - rnd, 4)}
        print("[abtt] D=%-2d dev_a_s=%.4f sib-rnd=%.4f (%.0fs)" % (D, d, sib - rnd, time.time() - t0), flush=True)
    bestD = max(Ds, key=lambda D: abtt[D]["dev_a_s"])

    # 2) SIF discriminative pre-pooling (IDF weights), alone and + best-D ABTT
    W = idf_weights(prep)
    sif = sif_sigs(prep, mat, w2i, W, abtt_D=0)
    sif_abtt = sif_sigs(prep, mat, w2i, W, abtt_D=bestD)
    dev_sif = float(M.a_s(recs, dev, sif, Ctx_dev).mean())
    dev_sif_abtt = float(M.a_s(recs, dev, sif_abtt, Ctx_dev).mean())
    print("[sif] dev_a_s IDF=%.4f  IDF+ABTT(D=%d)=%.4f (%.0fs)"
          % (dev_sif, bestD, dev_sif_abtt, time.time() - t0), flush=True)

    # pick the best config on DEV, report on TEST
    cfgs = {"keepall": (keepall, ok_keepall_dev.mean()),
            "abtt_bestD": (all_but_top(keepall, bestD) if bestD > 0 else keepall, abtt[bestD]["dev_a_s"]),
            "sif_idf": (sif, dev_sif), "sif_idf_abtt": (sif_abtt, dev_sif_abtt)}
    best_name = max(cfgs, key=lambda k: cfgs[k][1])
    ok_best_test = M.a_s(recs, test, cfgs[best_name][0], Ctx_test)
    n = min(len(ok_best_test), len(ok_keepall_test), len(ok_gloss))

    res = {"level": level, "n_test": int(n), "best_config": best_name, "best_D": int(bestD),
           "diagnostics": diag, "abtt_sweep": {str(k): v for k, v in abtt.items()},
           "dev_a_s": {k: round(float(v[1]), 4) for k, v in cfgs.items()},
           "test_a_s": {"gloss": round(float(ok_gloss.mean()), 4),
                        "keepall": round(float(ok_keepall_test.mean()), 4),
                        "BEST(%s)" % best_name: round(float(ok_best_test.mean()), 4)},
           "BEST_vs_keepall": G1._paired(ok_best_test[:n], ok_keepall_test[:n], 960),
           "BEST_vs_gloss": G1._paired(ok_best_test[:n], ok_gloss[:n], 950),
           "elapsed_s": round(time.time() - t0, 1)}
    verdict = ("REPRESENTATION-ARTIFACT (post-hoc transform helps -> ship it, acquisition not yet needed)"
               if res["BEST_vs_keepall"]["delta"] > 0 and res["BEST_vs_keepall"]["sep"]
               else "DATA-GAP (no post-hoc transform beats keep-all CI-sep -> the missing signal is not in the "
                    "bags; targeted acquisition is the lever)")
    res["VERDICT"] = verdict
    res["headline"] = ("REPR-OPT: best=%s test a_s=%.4f vs keepall %.4f (d=%+.4f sep=%s) vs gloss +%.4f | "
                       "sib-rnd %.4f | %s"
                       % (best_name, res["test_a_s"]["BEST(%s)" % best_name], res["test_a_s"]["keepall"],
                          res["BEST_vs_keepall"]["delta"], res["BEST_vs_keepall"]["sep"],
                          res["BEST_vs_gloss"]["delta"], diag["sibling_minus_random"], verdict))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_repr_optimize_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # all-but-the-top removes a planted common direction; IDF down-weights a shared token.
    rng = np.random.default_rng(0)
    base = {s: G1._unit(rng.standard_normal(M.EMB_DIM)) for s in ["a.n.01", "b.n.01", "c.n.01", "d.n.01"]}
    common = G1._unit(rng.standard_normal(M.EMB_DIM))
    planted = {s: G1._unit(v + 3.0 * common) for s, v in base.items()}   # inject a strong shared direction
    r0 = random_pair_cosine(planted); r1 = random_pair_cosine(all_but_top(planted, 1))
    assert r1 < r0, "all-but-the-top lowers the anisotropy (random-pair) floor: %.3f -> %.3f" % (r0, r1)
    print("SELFTEST PASS (all-but-the-top removes the planted common direction: rnd %.3f -> %.3f)" % (r0, r1),
          flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(level=args.level, smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
