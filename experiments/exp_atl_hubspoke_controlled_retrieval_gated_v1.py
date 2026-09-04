"""exp_atl_hubspoke_controlled_retrieval_gated_v1 -- LAND the controlled-retrieval win: anti-dominant diagnostic-word
identification crosses 0.35 on subordinate senses but blanket-applied it regresses the dominant population. The brain
recruits control BY CONFLICT (Rodd 2005; Thompson-Schill 1997), not always. So GATE it: fire controlled retrieval
only when the context strongly evidences a non-dominant reading, else trust the (precision) default. Tune the gate on
the DISJOINT dev set to keep subordinate a_s > 0.35 AND preserve MFS (no dominant-population regression).

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

Mechanism (glass-box, gold-blind -- "dominant" = MFS/SemCor-frequency prior):
  anti_dom(c) = max_{s!=MFS} cos(c,key_s) - cos(c,key_MFS)     -- evidence for a non-dominant reading from word c
  gate_signal(item) = max_c relu(anti_dom(c))                  -- strength of the strongest anti-dominant cue
  if gate_signal >= tau:  controlled query  q = weighted_mean(C, precision_w * relu(anti_dom))   (override prepotent)
  else:                   default query     q = weighted_mean(C, precision_w)                    (trust MFS/topical)
  tau tuned on DEV (even docs): maximize subordinate a_s s.t. all-population a_s >= precision all-pop a_s - 0.003.

This is the BAR arm: subordinate a_s > 0.35 CI-separated over the launch pad, info-free twin losing, NO MFS regression.

Glass-box, frozen w2v, NO external LLM/transformer/training. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

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
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_controlled_retrieval_gated_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_sub = list(np.where((doc % 2 == 0) & sub)[0]); dev_all = list(np.where(doc % 2 == 0)[0])
    test_sub = list(np.where((doc % 2 == 1) & sub)[0]); test_all = list(np.where(doc % 2 == 1)[0])
    if smoke:
        dev_sub, dev_all, test_sub, test_all = dev_sub[:300], dev_all[:600], test_sub[:400], test_all[:800]
    cand = set()
    for i in dev_sub + dev_all + test_sub + test_all:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}

    def item_parts(r):
        tn = r["tn"]; ctxw = [x for x in r["ctx"] if x in w2i]
        if not ctxw:
            return None
        C = np.stack([_unit(mat[w2i[x]]) for x in ctxw])
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        thr = np.sort(diag)[-5] if len(diag) > 5 else diag.min()
        prec_w = np.where(diag >= thr, diag, 0.0) ** 3.0
        mfs = int(np.argmax(np.asarray(r["prior"], float)[:len(tn)]))
        if len(tn) > 1:
            other = np.delete(np.arange(len(tn)), mfs)
            anti = np.clip(sim[:, other].max(1) - sim[:, mfs], 0, None)
        else:
            anti = np.zeros(len(ctxw))
        return tn, C, G, prec_w, anti, tn.index(r["gold"])

    def pick(r, tau, shuffle=False):
        p = item_parts(r)
        if p is None:
            return None
        tn, C, G, prec_w, anti, gi = p
        gate = float(anti.max()) if len(anti) else 0.0
        if shuffle:
            rng = np.random.default_rng((hash(r["lemma"]) & 0xffff) + 1); anti = anti[rng.permutation(len(anti))]
        if gate >= tau:
            wts = prec_w * anti
            if wts.sum() <= 1e-9:
                wts = prec_w
        else:
            wts = prec_w
        q = _unit((wts[:, None] * C).sum(0)) if wts.sum() > 1e-9 else _unit(C.mean(0))
        return int(np.argmax(G @ q) == gi)

    def acc(idxs, tau, shuffle=False):
        return np.asarray([v for i in idxs if (v := pick(recs[i], tau, shuffle)) is not None], float)

    prec_dev_all = acc(dev_all, 1e9).mean()          # tau=inf => never fires control => pure precision
    # tune tau on DEV: maximize subordinate a_s s.t. all-pop a_s >= prec_dev_all - 0.003
    best_tau, best_sub = 1e9, -1.0
    for tau in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 1e9]:
        s = acc(dev_sub, tau).mean(); a = acc(dev_all, tau).mean()
        if a >= prec_dev_all - 0.003 and s > best_sub:
            best_sub, best_tau = float(s), tau
    print("[tune] best_tau=%.3f dev_sub=%.4f (prec_dev_all floor=%.4f) (%.0fs)"
          % (best_tau, best_sub, prec_dev_all, time.time() - t0), flush=True)

    test_g = acc(test_sub, best_tau); test_p = acc(test_sub, 1e9); test_tw = acc(test_sub, best_tau, shuffle=True)
    mfs_g = acc(test_all, best_tau); mfs_p = acc(test_all, 1e9)
    # launch-pad floor (flat bag) on test_sub for the bar
    def launchpad(r):
        p = item_parts(r)
        if p is None:
            return None
        tn, C, G, prec_w, anti, gi = p
        return int(np.argmax(G @ _unit(C.mean(0))) == gi)
    lp = np.asarray([v for i in test_sub if (v := launchpad(recs[i])) is not None], float)

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    res = {
        "n_test_sub": len(test_sub), "n_test_all": len(test_all), "best_tau": best_tau,
        "a_s": {"gated_control": round(float(test_g.mean()), 4), "precision": round(float(test_p.mean()), 4),
                "launchpad": round(float(lp.mean()), 4), "twin_shuffled_anti": round(float(test_tw.mean()), 4)},
        "gated_vs_precision": pair(test_g, test_p, 881),
        "gated_vs_launchpad": pair(test_g, lp, 882),
        "gated_vs_twin": pair(test_g, test_tw, 883),
        "mfs_guard": {"gated_all": round(float(mfs_g.mean()), 4), "precision_all": round(float(mfs_p.mean()), 4),
                      "delta": round(float(mfs_g.mean() - mfs_p.mean()), 4),
                      "no_regression": bool(mfs_g.mean() >= mfs_p.mean() - 0.005)},
        "crosses_0.35": bool(test_g.mean() >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    PASS = (res["crosses_0.35"] and res["gated_vs_launchpad"]["sep"] and res["gated_vs_twin"]["sep"]
            and res["mfs_guard"]["no_regression"])
    res["BAR_PASS"] = bool(PASS)
    res["headline"] = ("GATED CONTROLLED RETRIEVAL | tau=%.3f | gated=%.4f precision=%.4f launchpad=%.4f twin=%.4f | "
                       "vs launchpad sep=%s ci=%s | vs twin sep=%s | MFS %.4f->%.4f (d%+.4f) no-regr=%s | "
                       "crosses0.35=%s | BAR_PASS=%s"
                       % (best_tau, res["a_s"]["gated_control"], res["a_s"]["precision"], res["a_s"]["launchpad"],
                          res["a_s"]["twin_shuffled_anti"], res["gated_vs_launchpad"]["sep"], res["gated_vs_launchpad"]["ci"],
                          res["gated_vs_twin"]["sep"], res["mfs_guard"]["precision_all"], res["mfs_guard"]["gated_all"],
                          res["mfs_guard"]["delta"], res["mfs_guard"]["no_regression"], res["crosses_0.35"], PASS))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_controlled_retrieval_gated_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (gated controlled-retrieval cell imports)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
