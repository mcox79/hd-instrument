"""BRAIN-FAITHFUL readout: GROUNDED sensorimotor channel + ATTRACTOR-SETTLING comparison (no cosine).
(problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection)

Owner-directed: "prototype EXACTLY how the brain does it; for the missing items we have organs and/or vast
data -- look." Two brain-fidelity deviations of the distributional-w2v readout, each closed with a REAL
substrate asset, tested one-variable against the parent's banked floors (bag 0.283, diagnostic 0.309):

  GROUNDING (the sensorimotor hub -- the biggest missing modality).  Word meaning in the brain is grounded
    in sensorimotor experience (Lambon-Ralph hub-and-spoke; Binder 2016). We have VAST data:
    data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv -- 39,707 words x 11 grounded
    dimensions (6 perceptual: Auditory/Gustatory/Haptic/Interoceptive/Olfactory/Visual; 5 action-effector:
    Foot_leg/Hand_arm/Head/Mouth/Torso). A rare sense and its dominant twin SHARE distributional topic but
    can differ in grounded profile (river-bank: Visual/Foot_leg; money-bank: Hand_arm/low-perceptual). We
    add a GROUNDED channel: score(sense) = fit(context sensorimotor profile, sense-gloss sensorimotor
    profile), and FUSE it with the distributional biased-competition readout. Info-free twin must lose.

  ATTRACTOR SETTLING (no cosine in the brain).  ORGAN_MAP: "comparison is deep recurrent settling, not a
    cosine." We reuse hdlab/iterative_attractor.py (CA3/Amari soft-attractor settling with alpha=0.5 cue
    re-injection) and hdlab/modern_hopfield_readout.py (Ramsauer pMTG-IFG semantic control: one Hopfield
    update then re-rank) as the comparison operator over the candidate-sense codebook, replacing cosine-
    argmax. Both are REAL landed organs, reused verbatim.

This cell is READOUT-SIDE and needs NO trained neural net (the grounded + distributional channels come from
w2v + Lancaster + WordNet), so it gives a fast, decisive read on whether the brain's grounded modality and
settling comparison cross the 0.309 ceiling -- the faithful pathway the neural encoder (PC-SG) then feeds.
Strict document-disjoint SemCor, subordinate senses, subject a_s, same n~2676 population. Twins + paired
bootstrap (CI + null p95). Glass-box, NO external LLM. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import time
import json
import pickle
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_context2vec_encoder_wsd_v1 as C2V
from hdlab import diagnostic_context_wsd as DCW
from hdlab import iterative_attractor as IA
from hdlab import modern_hopfield_readout as MHR

# KB_REFERENT: data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
LANCASTER = os.path.join(_REPO, "data", "grounding_testbed", "Lancaster_sensorimotor_norms_for_39707_words.csv")
_SCRATCH = SG._SCRATCH
_DIMS = ["Auditory", "Gustatory", "Haptic", "Interoceptive", "Olfactory", "Visual",
         "Foot_leg", "Hand_arm", "Head", "Mouth", "Torso"]


def _load_lancaster():
    """word(lower) -> 11-dim grounded sensorimotor vector (the .mean columns). Cached."""
    cache = os.path.join(_SCRATCH, "lancaster_sensorimotor_11d.pkl")
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)
    d = {}
    with open(LANCASTER, encoding="utf-8", errors="ignore") as fh:
        header = fh.readline().rstrip("\n").split(",")
        idx = [header.index("%s.mean" % dim) for dim in _DIMS]
        for line in fh:
            p = line.rstrip("\n").split(",")
            if len(p) <= max(idx):
                continue
            w = p[0].strip().lower()
            try:
                v = np.array([float(p[i]) for i in idx], np.float32)
            except ValueError:
                continue
            d[w] = v
    with open(cache, "wb") as f:
        pickle.dump(d, f)
    print("[lanc] %d grounded words" % len(d), flush=True)
    return d


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _ground_vec(lanc, words):
    vs = [lanc[w] for w in words if w in lanc]
    if not vs:
        return None
    return _unit(np.mean(vs, 0))


def _z(a):
    a = np.asarray(a, float); s = a.std()
    return (a - a.mean()) / s if s > 1e-12 else np.zeros(len(a))


def run(max_files, settle_temp, settle_steps, settle_alpha):
    t0 = time.time()
    emb = SG._build_embeddings(0, "full")
    w2i = emb["w2i"]; w2v = emb["mat"]
    lanc = _load_lancaster()
    recs = C2V._recs(emb, max_files)
    names = sorted({s for r in recs for s in r["tn"]})
    gw = {s: C2V._gloss_word_list(s) for s in names}
    gsig_w2v = {s: C2V._sig(gw[s], w2v, w2i) for s in names}
    gsig_grd = {s: _ground_vec(lanc, gw[s]) for s in names}
    # grounded coverage
    gcov = float(np.mean([gsig_grd[s] is not None for s in names]))
    print("[run] %d recs, %d senses, grounded gloss cov=%.3f (%.0fs)" % (len(recs), len(names), gcov, time.time() - t0), flush=True)

    hop = MHR.ModernHopfieldReadout(beta=float(settle_temp), normalize_query_and_store=True)

    def _pick_cosine(q, cands, gsig):
        sc = [float(q @ gsig[s]) if gsig[s] is not None else -9.0 for s in cands]
        return int(np.argmax(sc))

    def _pick_settle(q, cands, gsig):
        """attractor-settling comparison over the candidate-gloss codebook (iterative_attractor, alpha cue
        re-injection) -- the brain's 'settle to a fixed point', replacing cosine-argmax."""
        rows = [gsig[s] if gsig[s] is not None else None for s in cands]
        keep = [i for i, r in enumerate(rows) if r is not None]
        if len(keep) < 2:
            return _pick_cosine(q, cands, gsig)
        cb = np.stack([rows[i] for i in keep]).astype(np.float32)
        out = IA.iterative_cleanup(q.astype(np.float32), cb, temp=float(settle_temp),
                                   max_steps=int(settle_steps), alpha=float(settle_alpha))
        return keep[int(out["argmax_idx"])]

    def _pick_hopfield(q, cands, gsig):
        rows = [gsig[s] if gsig[s] is not None else None for s in cands]
        keep = [i for i, r in enumerate(rows) if r is not None]
        if len(keep) < 2:
            return _pick_cosine(q, cands, gsig)
        cb = np.stack([rows[i] for i in keep]).astype(np.float32)
        top = hop.top_k_by_retrieved(q.astype(np.float32), cb, k=1)[0]
        return keep[int(top[0])]

    def _bag_query(ctx, mat):
        vs = [mat[w2i[w]] for w in ctx if w in w2i]
        return _unit(np.mean(vs, 0)) if vs else None

    def _diag_query(ctx, cands, gsig, mat, dim):
        rows = [_unit(mat[w2i[w]]) for w in ctx if w in w2i]
        if not rows:
            return None
        C = np.stack(rows).astype(np.float32)
        G = np.stack([gsig[s] if gsig[s] is not None else np.zeros(dim, np.float32) for s in cands]).astype(np.float32)
        return DCW.diagnostic_query(C, G)

    def _grounded_scores(ctx, cands):
        """grounded biased-competition: diagnostic-weighted context sensorimotor profile vs gloss profiles."""
        rows = [lanc[w] for w in ctx if w in lanc]
        if not rows:
            return None
        C = np.stack([_unit(r) for r in rows]).astype(np.float32)
        G = np.stack([gsig_grd[s] if gsig_grd[s] is not None else np.zeros(11, np.float32) for s in cands]).astype(np.float32)
        q = DCW.diagnostic_query(C, G)
        return G @ q

    # per-rec picks for each arm
    doc = np.array([r["doc_id"] for r in recs]); te = doc % 2 == 1; tr = doc % 2 == 0
    sub = np.array([r["subordinate"] for r in recs], bool)
    tsub = te & sub

    def score_arm(pickfn):
        return np.array([int(recs[i]["tn"][pickfn(i)] == recs[i]["gold"]) for i in range(len(recs))], int)

    # distributional queries (bag + diagnostic) reused across readouts
    diagq = [_diag_query(r["ctx"], r["tn"], gsig_w2v, w2v, SG.EMB_DIM) for r in recs]
    bagq = [_bag_query(r["ctx"], w2v) for r in recs]
    grdsc = [_grounded_scores(r["ctx"], r["tn"]) for r in recs]

    def pick_bag(i):
        q = bagq[i]; return _pick_cosine(q, recs[i]["tn"], gsig_w2v) if q is not None else 0

    def pick_diag_cos(i):
        q = diagq[i]; return _pick_cosine(q, recs[i]["tn"], gsig_w2v) if q is not None else 0

    def pick_diag_settle(i):
        q = diagq[i]; return _pick_settle(q, recs[i]["tn"], gsig_w2v) if q is not None else 0

    def pick_diag_hop(i):
        q = diagq[i]; return _pick_hopfield(q, recs[i]["tn"], gsig_w2v) if q is not None else 0

    def pick_grounded(i):
        sc = grdsc[i]
        return int(np.argmax(sc)) if sc is not None else 0

    arms = {
        "bag_w2v": score_arm(pick_bag),
        "diag_w2v_cosine": score_arm(pick_diag_cos),
        "diag_w2v_settle": score_arm(pick_diag_settle),
        "diag_w2v_hopfield": score_arm(pick_diag_hop),
        "grounded_only": score_arm(pick_grounded),
    }

    # FUSED distributional-diagnostic + grounded, lambda swept on TRAIN docs, evaluated on TEST.
    def fused_ok(lam):
        ok = np.zeros(len(recs), int)
        for i, r in enumerate(recs):
            q = diagq[i]; g = grdsc[i]
            if q is None:
                continue
            ds = np.array([float(q @ gsig_w2v[s]) if gsig_w2v[s] is not None else -9.0 for s in r["tn"]])
            if g is None:
                fs = ds
            else:
                fs = _z(ds) + lam * _z(g)
            ok[i] = int(r["tn"][int(np.argmax(fs))] == r["gold"])
        return ok
    best = None
    for lam in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
        ok = fused_ok(lam)
        acc_tr = ok[tr & sub].mean()
        if best is None or acc_tr > best[1]:
            best = (lam, acc_tr, ok)
    lam_star, _, ok_fused = best
    arms["fused_diag+grounded"] = ok_fused

    # info-free twin: grounded channel with SHUFFLED context (cross-item, same sense-count bucket)
    buckets = defaultdict(list)
    for i, r in enumerate(recs):
        buckets[len(r["tn"])].append(i)
    rng = np.random.default_rng(7); mp = {}
    for _, idxs in buckets.items():
        perm = list(idxs); rng.shuffle(perm)
        for a, c in zip(idxs, perm):
            mp[a] = c
    grd_twin = np.array([int(recs[i]["tn"][int(np.argmax(grdsc[mp[i]]))] == recs[i]["gold"])
                         if grdsc[mp[i]] is not None else 0 for i in range(len(recs))], int)

    def a_s(arm):
        return round(float(arms[arm][tsub].mean()), 4)

    out = {"n_test_sub": int(tsub.sum()), "grounded_gloss_cov": round(gcov, 4), "lambda_star": lam_star,
           "settle": {"temp": settle_temp, "steps": settle_steps, "alpha": settle_alpha},
           "a_s": {k: a_s(k) for k in arms},
           "paired": {
               "fused_vs_diag": V1._paired(arms["fused_diag+grounded"][tsub].astype(float),
                                           arms["diag_w2v_cosine"][tsub].astype(float), 511),
               "settle_vs_cosine": V1._paired(arms["diag_w2v_settle"][tsub].astype(float),
                                              arms["diag_w2v_cosine"][tsub].astype(float), 512),
               "hopfield_vs_cosine": V1._paired(arms["diag_w2v_hopfield"][tsub].astype(float),
                                                arms["diag_w2v_cosine"][tsub].astype(float), 513),
               "grounded_vs_twin": V1._paired(arms["grounded_only"][tsub].astype(float),
                                              grd_twin[tsub].astype(float), 514),
           }}
    p = out["paired"]
    out["headline"] = (
        "GROUNDED+SETTLE strict doc-disjoint subord n=%d gcov=%.2f | bag=%.3f diag_cos=%.3f settle=%.3f "
        "hop=%.3f grounded=%.3f | FUSED(diag+grounded lam=%.2f)=%.3f (vs diag %+.4f sep=%s) | grounded-vs-twin "
        "%+.4f sep=%s"
        % (out["n_test_sub"], gcov, out["a_s"]["bag_w2v"], out["a_s"]["diag_w2v_cosine"],
           out["a_s"]["diag_w2v_settle"], out["a_s"]["diag_w2v_hopfield"], out["a_s"]["grounded_only"],
           lam_star, out["a_s"]["fused_diag+grounded"], p["fused_vs_diag"]["delta"], p["fused_vs_diag"]["sep"],
           p["grounded_vs_twin"]["delta"], p["grounded_vs_twin"]["sep"]))
    odir = os.path.join(_REPO, "data", "exp_sg_lite_grounded_settling_readout_v1")
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "sg_lite_grounded_settling_readout_v1", "verdict": "MEASURED", "result": out},
                  f, indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    lanc = {"river": np.ones(11, np.float32), "money": np.zeros(11, np.float32) + 0.1}
    assert _ground_vec(lanc, ["river", "x"]) is not None
    # settle + hopfield pick over a tiny 2-attractor codebook
    q = np.array([1, 0, 0], np.float32); cb = np.array([[1, 0, 0], [0, 1, 0]], np.float32)
    out = IA.iterative_cleanup(q, cb, temp=4.0, max_steps=4, alpha=0.5)
    assert int(out["argmax_idx"]) == 0
    top = MHR.ModernHopfieldReadout(beta=8.0).top_k_by_retrieved(q, cb, k=1)[0]
    assert int(top[0]) == 0
    print("SELFTEST PASS (lancaster loader + iterative_attractor + modern_hopfield picks)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-files", type=int, default=30)
    ap.add_argument("--settle-temp", type=float, default=4.0)
    ap.add_argument("--settle-steps", type=int, default=8)
    ap.add_argument("--settle-alpha", type=float, default=0.5)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.max_files, args.settle_temp, args.settle_steps, args.settle_alpha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
