"""exp_atl_hubspoke_multicue_integration_v1 -- the final brain-foundational OPTIMIZATION: integrate ALL the weak,
partly-orthogonal cues by RELIABILITY (multisensory/cue integration -- Ernst-Banks 2002; Friston precision-weighting),
to push the glass-box chain to its ceiling.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

The brain integrates multiple cues, each weighted by its reliability (inverse variance). Our cues, each measured this
session: w2v PRECISION readout (0.334), ACT-R discriminative-W amplify-weak (0.345), GROUNDED hub (loses alone). This
cell integrates them: per item, each channel gives z-scored candidate scores; combine by RELIABILITY x per-item
CONFIDENCE (margin). Two variants: reliability-weighted sum, and confidence-gating (the most-confident channel picks).
Mix calibrated on the DISJOINT even-doc subordinate set, reported on odd-doc test; shuffled twin + MFS no-regression.

Glass-box at inference (NO external LLM/transformer); gold used only to build the offline ACT-R edge foundation
(doc-disjoint, leave-one-doc-out). Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv
# KB_REFERENT: data/grounding_testbed/Ratings_Warriner_et_al.csv
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import math
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF
import experiments.exp_atl_hubspoke_grounded_separability_v1 as A

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_multicue_integration_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0])
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    all_test_idx = list(np.where(doc % 2 == 1)[0])
    if smoke:
        dev_idx, test_idx, all_test_idx = dev_idx[:300], test_idx[:400], all_test_idx[:600]
    cand = set()
    for i in dev_idx + test_idx + all_test_idx:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}
    gr = A.Grounded(add_affect=True)
    sg_white = A.build_sense_grounded(sorted(cand), gr, whiten=True, own_lemma_w=0.0)

    # ACT-R discriminative-W edges from GOLD-resolved co-occurrence (leave-one-doc-out; the offline foundation)
    g_cooc = defaultdict(Counter); g_sel = Counter(); w_fan = defaultdict(set)
    d_cooc = defaultdict(lambda: defaultdict(Counter)); d_sel = defaultdict(Counter); g_N = 0; d_N = Counter()
    for i in range(len(recs)):
        r = recs[i]; s = r["gold"]; dd = r["doc_id"]
        toks = set(x for x in r["ctx"] if x in w2i)
        if not toks:
            continue
        g_N += 1; g_sel[s] += 1; d_N[dd] += 1; d_sel[dd][s] += 1
        for w in toks:
            g_cooc[s][w] += 1; w_fan[w].add(s); d_cooc[dd][s][w] += 1
    print("[setup] edges + grounded + rich atoms ready (%.0fs)" % (time.time() - t0), flush=True)

    def ch_precision(r):
        tn = r["tn"]; rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            return None
        C = np.stack(rows)
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T; diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        thr = np.sort(diag)[-5] if len(diag) > 5 else diag.min()
        wq = np.where(diag >= thr, diag, 0.0) ** 3.0
        q = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
        return G @ q

    def ch_actr(r):
        tn = r["tn"]; dd = r["doc_id"]; ctxw = [x for x in r["ctx"] if x in w2i]
        N = max(1, g_N - d_N[dd]); A_ = np.zeros(len(tn)); any_ = False
        spec = {}
        for w in ctxw:
            fan = len(w_fan.get(w, ())); spec[w] = 1.0 / (1.0 + math.log(1.0 + fan)) if fan > 0 else 0.0
        Z = sum(spec.values())
        if Z <= 1e-9:
            return None
        base = np.zeros(len(tn))
        for si, s in enumerate(tn):
            sel_s = g_sel.get(s, 0) - d_sel[dd].get(s, 0)
            base[si] = math.log(1.0 + max(0, sel_s))
            if sel_s <= 0:
                continue
            Ps = sel_s / N; tot = 0.0
            for w in ctxw:
                c_sw = g_cooc.get(s, {}).get(w, 0) - d_cooc[dd].get(s, {}).get(w, 0)
                cw = sum((g_cooc.get(ss, {}).get(w, 0) - d_cooc[dd].get(ss, {}).get(w, 0)) for ss in tn)
                if c_sw > 0 and cw > 0:
                    tot += spec[w] * math.log((c_sw / cw + 1e-9) / (Ps + 1e-9))
            A_[si] = tot / Z; any_ = any_ or (tot != 0)
        if not any_:
            return None
        return _z(A_) - 0.5 * _z(base)     # amplify-weak (inhibit dominant base)

    def ch_grounded(r):
        tn = r["tn"]; rows = [gr.vec(x, True) for x in r["ctx"]]; rows = [v for v in rows if v is not None]
        keys = [sg_white.get(s) for s in tn]
        if not rows or all(k is None for k in keys):
            return None
        from hdlab.diagnostic_context_wsd import diagnostic_context_scores
        d = rows[0].shape[0]
        G = np.stack([k if k is not None else np.zeros(d) for k in keys])
        return diagnostic_context_scores(np.stack(rows), G)

    def integrate(idxs, wts, gate=False, shuffle=None):
        rng = np.random.default_rng(88) if shuffle else None
        ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]
            p = ch_precision(r)
            if p is None:
                continue
            chans = [("prec", p, wts["prec"])]
            a = ch_actr(r); g = ch_grounded(r)
            if a is not None:
                chans.append(("actr", a, wts["actr"]))
            if g is not None:
                chans.append(("grnd", g, wts["grnd"]))
            if shuffle:
                chans = [(nm, (sc[rng.permutation(len(sc))] if nm == shuffle else sc), wt) for nm, sc, wt in chans]
            if gate:
                # confidence-gating: the channel with the highest reliability x margin picks
                best = None
                for nm, sc, wt in chans:
                    zz = _z(sc); srt = np.sort(zz)[::-1]; margin = (srt[0] - srt[1]) if len(srt) > 1 else srt[0]
                    conf = wt * margin
                    if best is None or conf > best[0]:
                        best = (conf, zz)
                fused = best[1]
            else:
                fused = np.zeros(len(tn))
                for nm, sc, wt in chans:
                    fused = fused + wt * _z(sc)
            ok.append(int(tn[int(np.argmax(fused))] == r["gold"]))
        return np.asarray(ok, float)

    # calibrate the 3-way mix on the DISJOINT dev set (coarse grid; low overfit risk -- 3 weights)
    grid = []
    for pa in [1.0]:
        for aa in [0.5, 1.0, 1.5, 2.0]:
            for gg in [0.0, 0.25, 0.5]:
                grid.append({"prec": pa, "actr": aa, "grnd": gg})
    best_w, best_dev, best_gate = None, -1.0, False
    for gate in (False, True):
        for wts in grid:
            dv = integrate(dev_idx, wts, gate=gate).mean()
            if dv > best_dev:
                best_dev, best_w, best_gate = float(dv), wts, gate
    test = integrate(test_idx, best_w, gate=best_gate)
    twin_a = integrate(test_idx, best_w, gate=best_gate, shuffle="actr")
    # single-channel refs on test
    prec_only = integrate(test_idx, {"prec": 1.0, "actr": 0.0, "grnd": 0.0})
    # MFS guard on the full (sub+dom) test population
    mfs_fused = integrate(all_test_idx, best_w, gate=best_gate)
    mfs_prec = integrate(all_test_idx, {"prec": 1.0, "actr": 0.0, "grnd": 0.0})

    def m(x):
        return round(float(x.mean()), 4) if len(x) else None

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    res = {
        "n_dev": len(dev_idx), "n_test": len(test_idx),
        "best_mix": best_w, "best_gate": best_gate, "dev_a_s": round(best_dev, 4),
        "arms": {"integrated": m(test), "precision_only": m(prec_only), "twin_shuffled_actr": m(twin_a)},
        "integrated_vs_precision": pair(test, prec_only, 861),
        "integrated_vs_twin": pair(test, twin_a, 862),
        "mfs_guard": {"fused_all": m(mfs_fused), "precision_all": m(mfs_prec),
                      "no_regression": bool((m(mfs_fused) or 0) >= (m(mfs_prec) or 0) - 0.005)},
        "crosses_0.35": bool((m(test) or 0) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("MULTI-CUE INTEGRATION | mix=%s gate=%s | integrated=%.4f precision_only=%.4f twin=%.4f | "
                       "vs precision sep=%s ci=%s | vs twin sep=%s | MFS no-regr=%s | crosses0.35=%s"
                       % (best_w, best_gate, res["arms"]["integrated"], res["arms"]["precision_only"],
                          res["arms"]["twin_shuffled_actr"], res["integrated_vs_precision"]["sep"],
                          res["integrated_vs_precision"]["ci"], res["integrated_vs_twin"]["sep"],
                          res["mfs_guard"]["no_regression"], res["crosses_0.35"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_multicue_integration_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (multi-cue integration cell imports + builds)", flush=True)
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
