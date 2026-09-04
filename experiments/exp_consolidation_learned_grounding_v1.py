"""exp_consolidation_learned_grounding_v1 -- [DROPPED as NOT brain-foundational; kept as a documented control.]
The brain does NOT regress word-vectors onto feature-ratings, so this ridge w2v->Binder-65 approach was rejected
(owner 2026-09-03) in favor of the brain-faithful SEMANTIC-INHERITANCE mechanism (exp_consolidation_grounding_
inherit_v1). Recorded here because it was run: the learned Binder-65 space also does NOT cross gloss (smoke 0.250),
consistent with the located negative -- and, per the corrected framing, grounding is not the crosser anyway
(the barrier is a CONTEXTUAL text-representation, exp_context_encoder_from_text_v1).

ORIGINAL DOCSTRING: does LEARNING a rich grounded representation cross the barrier the raw
12-dim norm lookup could not?

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

The 12-15-dim norm lookups (sensorimotor+concreteness+affect) do NOT beat gloss on rare-sense selection -- too
coarse, abstract-blind. But the ideal grounded space is Binder et al. 2016's 65-dim BRAIN-BASED componential
semantics (Vision/Motion/Touch/Audition/.../Cognition/Social/emotion/attention), which covers only 535 words. THIS
cell LEARNS to propagate that brain-based space to FULL coverage: a ridge map from [w2v + sensorimotor/affect norms]
-> Binder-65, trained on the 535 Binder words (brain-SUPERVISED, so the learned space reorganizes toward
brain-relevant structure, not just w2v), applied to every word. Then it tests whether that LEARNED brain-based
grounded representation, fused with the distributional diagnostic readout, crosses gloss on strict doc-disjoint
SemCor subordinate senses.

BRAIN-FOUNDATIONAL: Binder 2016 IS the brain's componential semantic code (fMRI-derived attribute ratings mapped to
cortical systems); learning to predict it from our features is the glass-box analog of the ATL hub distilling a
rich amodal representation from spokes. NO external LLM. Ridge fit + fusion weight learned on EVEN (train) docs;
reported on ODD (test) docs. ASCII-only. own dir.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import csv
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
from hdlab.diagnostic_context_wsd import diagnostic_context_scores
from hdlab.grounded_similarity import grounded_vector

# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv
_CACHE = G1._CACHE
BINDER = os.path.join(_REPO, "data", "corpora", "binder", "binder2016_ratings.csv")
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_learned_grounding_v1")
_META = {"no", "word", "wc", "n", "mean r", "sd", "mean rt", "sd rt", "list", "freq", "length"}


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def load_binder():
    """word -> 65-dim brain-based vector; returns (dict, feature_names)."""
    with open(BINDER, encoding="utf-8", errors="ignore") as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    # feature columns = numeric columns whose header is not metadata
    feat_idx = []
    for j, h in enumerate(hdr):
        if h.strip().lower() in _META:
            continue
        vals = []
        for r in rows[1:6]:
            try:
                vals.append(float(r[j]));
            except Exception:
                vals = None; break
        if vals is not None:
            feat_idx.append(j)
    wi = hdr.index("Word") if "Word" in hdr else 1
    d = {}
    for r in rows[1:]:
        w = r[wi].strip().lower()
        try:
            d[w] = np.array([float(r[j]) for j in feat_idx], np.float32)
        except Exception:
            pass
    return d, [hdr[j] for j in feat_idx]


def train_binder_predictor(emb, use_norms=True):
    """ridge [w2v(+norms)] -> Binder-65, trained on the 535 Binder words in vocab. Returns predict(word)->65d."""
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import cross_val_score
    w2i, mat = emb["w2i"], emb["mat"]
    binder, feats = load_binder()

    def feat(w):
        if w not in w2i:
            return None
        v = mat[w2i[w]].astype(np.float32)
        if use_norms:
            g = grounded_vector(w)
            v = np.concatenate([v, np.asarray(g, np.float32) if g is not None else np.zeros(12, np.float32)])
        return v

    X, Y = [], []
    for w, y in binder.items():
        f = feat(w)
        if f is not None:
            X.append(f); Y.append(y)
    X = np.stack(X); Y = np.stack(Y)
    # z-score targets
    ymu = Y.mean(0); ysd = Y.std(0) + 1e-9
    Yz = (Y - ymu) / ysd
    # pick alpha by CV R2
    best_a, best_r2 = 100.0, -9.0
    for a in [1.0, 10.0, 100.0, 300.0, 1000.0]:
        r2 = cross_val_score(Ridge(alpha=a), X, Yz, cv=5, scoring="r2").mean()
        if r2 > best_r2:
            best_r2, best_a = r2, a
    model = Ridge(alpha=best_a).fit(X, Yz)
    cache = {}

    def predict(w):
        if w in cache:
            return cache[w]
        f = feat(w)
        v = None if f is None else model.predict(f[None, :])[0].astype(np.float32)
        cache[w] = v
        return v
    return predict, {"n_train": len(X), "cv_r2": round(float(best_r2), 4), "alpha": best_a, "n_feats": len(feats)}


def centroid(words, fn):
    vs = [fn(w) for w in words]; vs = [v for v in vs if v is not None]
    return _unit(np.mean(vs, 0)) if vs else None


def score(recs, idxs, gloss_sig, sgrndL, predict, mat, w2i, lam):
    """distributional diagnostic + lam * LEARNED-Binder diagnostic (biased competition in the learned brain space)."""
    ok = []
    for i in idxs:
        r = recs[i]; tn = r["tn"]
        rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            continue
        G = np.stack([gloss_sig.get(s) if gloss_sig.get(s) is not None else np.zeros(G1.EMB_DIM, np.float32)
                      for s in tn])
        if not np.any(G):
            continue
        diag = diagnostic_context_scores(np.stack(rows), G)
        if lam == 0.0:
            fin = diag
        else:
            crows = [_unit(v) for x in r["ctx"] if (v := predict(x)) is not None]
            Gg = [sgrndL.get(s) for s in tn]
            if not crows or all(g is None for g in Gg):
                fin = diag
            else:
                D = len(crows[0])
                GgM = np.stack([g if g is not None else np.zeros(D, np.float32) for g in Gg])
                grnd = diagnostic_context_scores(np.stack(crows), GgM)
                fin = _z(diag) + lam * _z(grnd)
        ok.append(int(tn[int(np.argmax(fin))] == r["gold"]))
    return np.array(ok, float)


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0]); test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        dev_idx = dev_idx[:300]; test_idx = test_idx[:300]
    predict, fit = train_binder_predictor(emb, use_norms=True)
    print("[fit] Binder-65 ridge: n_train=%d cv_r2=%.4f alpha=%s n_feats=%d (%.0fs)"
          % (fit["n_train"], fit["cv_r2"], fit["alpha"], fit["n_feats"], time.time() - t0), flush=True)

    cand = set()
    for i in dev_idx + test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in cand}
    gloss_sig = {s: G1._sigvec(mat, w2i, seeds_by_syn[s]) for s in cand}
    sgrndL = {s: centroid(seeds_by_syn[s], predict) for s in cand}
    covL = np.mean([sgrndL[s] is not None for s in cand])
    Ctx_dev, Ctx_test = dev_idx, test_idx
    print("[run] dev=%d test=%d cand=%d learned-sense-coverage=%.2f (%.0fs)"
          % (len(dev_idx), len(test_idx), len(cand), covL, time.time() - t0), flush=True)

    g_test = score(recs, test_idx, gloss_sig, sgrndL, predict, mat, w2i, 0.0)
    sweep = {}; best_lam = 0.0; best_dev = float(score(recs, dev_idx, gloss_sig, sgrndL, predict, mat, w2i, 0.0).mean())
    for lam in [0.25, 0.5, 0.75, 1.0, 1.5]:
        dv = float(score(recs, dev_idx, gloss_sig, sgrndL, predict, mat, w2i, lam).mean())
        sweep["lam%.2f" % lam] = round(dv, 4)
        print("[sweep] learned-Binder fuse lam=%.2f dev=%.4f (%.0fs)" % (lam, dv, time.time() - t0), flush=True)
        if dv > best_dev:
            best_dev = dv; best_lam = lam
    fuse_test = score(recs, test_idx, gloss_sig, sgrndL, predict, mat, w2i, best_lam)

    n = len(g_test)
    res = {"n_dev": len(dev_idx), "n_test": len(test_idx), "ridge_fit": fit, "learned_coverage": round(float(covL), 3),
           "best_lam": best_lam, "sweep": sweep,
           "a_s_test": {"gloss": round(float(g_test.mean()), 4), "LEARNED_binder_fuse": round(float(fuse_test.mean()), 4)},
           "LEARNED_vs_gloss": G1._paired(fuse_test[:n], g_test[:n], 701)}
    res["headline"] = ("LEARNED-GROUNDING (Binder-65 ridge, cv_r2=%.3f) | gloss=%.3f LEARNED_fuse=%.3f (lam=%.2f) "
                       "sep_vs_gloss=%s null_p95=%s ci=%s"
                       % (fit["cv_r2"], res["a_s_test"]["gloss"], res["a_s_test"]["LEARNED_binder_fuse"], best_lam,
                          res["LEARNED_vs_gloss"]["sep"], res["LEARNED_vs_gloss"]["null_p95"],
                          res["LEARNED_vs_gloss"]["ci"]))
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_learned_grounding_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    d, feats = load_binder()
    assert len(d) > 400 and 60 <= len(feats) <= 75, "Binder loads ~535 words x ~65-72 feats (got %d x %d)" % (len(d), len(feats))
    print("SELFTEST PASS (Binder %d words x %d brain-based feats)" % (len(d), len(feats)), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
