"""exp_atl_hubspoke_controlled_retrieval_v1 -- ATTACK the largest located signal loss: diagnostic-word IDENTIFICATION
on the query side (headroom precision 0.336 -> oracle 0.63-0.87). The cue is IN the frozen context ~87% of the time;
we pick the wrong word because diagnosticity up-weights topical words that point to the DOMINANT sense. The brain's
control network (LIFG/pMTG) resolves this by CONTROLLED RETRIEVAL that OVERRIDES the prepotent (dominant) response and
seeks evidence for the weak/subordinate reading (Thompson-Schill 1997; Badre-Wagner 2007; Rodd 2005: control recruited
by dominant/subordinate conflict; CSC amplify-weak/inhibit-dominant, Lambon-Ralph 2017).

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

MECHANISM (glass-box, gold-blind -- "dominant" = the MFS / SemCor-frequency prior, available without the label):
  anti_dom(c) = max_{s != MFS} cos(c, key_s) - cos(c, key_MFS)   -- how much context word c favors a NON-dominant
                sense over the dominant one (the controlled-retrieval signal: evidence against the prepotent).
  ARMS:
    precision            -- diagnosticity-weighted query (baseline 0.336)
    ctrl_soft            -- weight context words by relu(anti_dom) (up-weight anti-dominant evidence)
    ctrl_wta             -- WINNER-TAKE-ALL: the single most anti-dominant context word IS the clincher; pick
                            argmax_s cos(clincher, key_s) (mimics the oracle-single structure, gold-blind)
    ctrl_x_precision     -- diagnosticity * relu(anti_dom) (a word must both discriminate AND favor a non-dominant sense)
    conflict_gated       -- apply control ONLY when there is cross-sense conflict, else fall back to precision (Rodd)
  MFS no-regression guard on the full (sub+dom) population; shuffled twin; toward ORACLE_signed 0.627.

Glass-box, frozen w2v, NO external LLM. Core-capped. ASCII. Own dir.
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
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_controlled_retrieval_v1")


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
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    all_test_idx = list(np.where(doc % 2 == 1)[0])
    if smoke:
        test_idx = test_idx[:400]; all_test_idx = all_test_idx[:800]
    cand = set()
    for i in test_idx + all_test_idx:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}

    def score_item(r, mode):
        tn = r["tn"]; ctxw = [x for x in r["ctx"] if x in w2i]
        if not ctxw:
            return None
        C = np.stack([_unit(mat[w2i[x]]) for x in ctxw])
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T                                   # (W,S)
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        thr = np.sort(diag)[-5] if len(diag) > 5 else diag.min()
        prec_w = np.where(diag >= thr, diag, 0.0) ** 3.0
        mfs = int(np.argmax(np.asarray(r["prior"], float)[:len(tn)]))
        # anti-dominant evidence per context word: favor a non-MFS sense over the MFS
        if len(tn) > 1:
            other = np.delete(np.arange(len(tn)), mfs)
            anti = sim[:, other].max(1) - sim[:, mfs]
        else:
            anti = np.zeros(len(ctxw))
        anti_r = np.clip(anti, 0, None)

        def q_from(wts):
            return _unit((wts[:, None] * C).sum(0)) if wts.sum() > 1e-9 else _unit(C.mean(0))

        if mode == "precision":
            q = q_from(prec_w)
        elif mode == "ctrl_soft":
            q = q_from(anti_r)
        elif mode == "ctrl_wta":
            # the single most anti-dominant word is the clincher
            c = int(np.argmax(anti)); return int(tn[int(np.argmax(G @ _unit(C[c])))] == r["gold"])
        elif mode == "ctrl_x_precision":
            q = q_from(prec_w * anti_r)
        elif mode == "conflict_gated":
            # conflict = several context words split across senses; if low conflict, trust precision
            conflict = float((anti_r > 0).mean())
            q = q_from(prec_w * anti_r) if conflict >= 0.25 else q_from(prec_w)
        elif mode == "shuffled_twin":
            rng = np.random.default_rng(hash(r["lemma"]) & 0xffff)
            q = q_from((prec_w * anti_r)[rng.permutation(len(ctxw))])
        else:
            q = q_from(prec_w)
        return int(tn[int(np.argmax(G @ q))] == r["gold"])

    def evalmode(idxs, mode):
        return np.asarray([v for i in idxs if (v := score_item(recs[i], mode)) is not None], float)

    modes = ["precision", "ctrl_soft", "ctrl_wta", "ctrl_x_precision", "conflict_gated", "shuffled_twin"]
    arms = {mode: round(float(evalmode(test_idx, mode).mean()), 4) for mode in modes}
    print("[arms] " + " ".join("%s=%.4f" % (k, v) for k, v in arms.items()) + " (%.0fs)" % (time.time() - t0), flush=True)

    best = max([m for m in modes if m != "shuffled_twin"], key=lambda k: arms[k])
    bvec = evalmode(test_idx, best); pvec = evalmode(test_idx, "precision"); tvec = evalmode(test_idx, "shuffled_twin")

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    # MFS no-regression on the full population
    mfs_best = evalmode(all_test_idx, best); mfs_prec = evalmode(all_test_idx, "precision")
    res = {
        "n_test": len(test_idx), "arms": arms,
        "oracle_signed_ref": 0.627, "oracle_single_ref": 0.868,
        "best_arm": best, "best_a_s": arms[best],
        "best_vs_precision": pair(bvec, pvec, 871), "best_vs_twin": pair(bvec, tvec, 872),
        "mfs_guard": {"best_all": round(float(mfs_best.mean()), 4), "precision_all": round(float(mfs_prec.mean()), 4),
                      "no_regression": bool(mfs_best.mean() >= mfs_prec.mean() - 0.005)},
        "crosses_0.35": bool(arms[best] >= 0.35),
        "recovered_headroom_frac": round((arms[best] - arms["precision"]) / max(1e-9, 0.627 - arms["precision"]), 3),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("CONTROLLED RETRIEVAL (anti-dominant diagnostic-word ID) | %s | best=%s %.4f vs precision "
                       "%.4f sep=%s ci=%s | twin=%.4f sep=%s | MFS no-regr=%s | crosses0.35=%s | recovered %.0f%% of "
                       "the precision->oracle_signed headroom"
                       % (" ".join("%s=%.3f" % (k, v) for k, v in arms.items()), best, arms[best], arms["precision"],
                          res["best_vs_precision"]["sep"], res["best_vs_precision"]["ci"], arms["shuffled_twin"],
                          res["best_vs_twin"]["sep"], res["mfs_guard"]["no_regression"], res["crosses_0.35"],
                          100 * res["recovered_headroom_frac"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_controlled_retrieval_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (controlled-retrieval cell imports)", flush=True)
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
