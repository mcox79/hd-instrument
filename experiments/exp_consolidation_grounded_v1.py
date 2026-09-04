"""exp_consolidation_grounded_v1 -- THE CEILING-CROSSER the located negative named: inject GROUNDING into the
sense signature, the ONE signal reading co-occurrence structurally lacks.

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

The distributional consolidation gate is a located NEGATIVE: reading-derived knowledge, tightened all the way to
real dependency links + MFS-quarantine, climbs only TO gloss (0.238->0.242->0.246->0.251) and never above, while
curated SyntagNet reaches 0.302. The signal-loss trace localized the residual to ASSOCIATION DISCRIMINATIVENESS +
GROUNDING: "a text-distributional signature has ZERO sensorimotor/affective dimensions, so overlapping/sparse
senses are inseparable IN PRINCIPLE from reading alone." The brain individuates them from GROUNDED features (ATL
hub + sensorimotor spokes; Patterson 2007; Binder & Desai 2011; Lambon-Ralph 2017).

THIS cell tests that fix, GLASS-BOX, using the WIRED grounding organ hdlab.grounded_similarity:
  * sense_grounding(s) = mean distinctive_grounded_vector over s's gloss/lemma/hypernym tokens (12-dim ATL-whitened
    perceptual centroid -- the whitening privileges DISTINCTIVE features, so a sense's centroid separates from its
    siblings). context_grounding(item) = mean grounded_vector over the context words.
  * GROUNDED-FUSE readout: score(s) = z(diagnostic gloss score) + lam * z(cos(context_grounding, sense_grounding))
    -- a second, NON-distributional channel that discriminates senses the diagnostic gloss query cannot.
  * GROUNDED-FILTER: admit a reading-derived associate w to sense s ONLY IF grounding says it is sense-discriminative
    (cos(grounded(w), sense_grounding(s)) > cos to the dominant sibling's grounding) -- the grounded version of
    MFS-quarantine, using PERCEPTUAL not distributional discrimination.

GROWTH OVER TIME: this is the consolidation gate the learner grows through -- each reading round adds candidate
associates (hdlab.grounded_semantic_graph.learn_from_text), grounding filters them to sense-discriminative ones,
and hdlab.cls_growth (keep-both + rollback_gate + EMA slow-anchor eta=0.1; PROVEN +0.110 over 6 rounds, corruption
0.116<0.15, drift-free) admits them safely. This cell measures the STATIC ceiling the grounded channel reaches;
the growth engine is cls_growth (cited, composed, not re-derived).

Strict doc-disjoint SemCor subordinate, n=2676, diagnostic readout, NO external LLM. grounded_similarity is a WIRED
glass-box organ over offline norm assets (Lancaster sensorimotor + Brysbaert concreteness). ASCII-only. Own dir.
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
import experiments.exp_consolidation_discriminative_rescore_v1 as DR
from hdlab.diagnostic_context_wsd import diagnostic_context_scores
from hdlab.grounded_similarity import grounded_vector, distinctive_grounded_vector

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_grounded_v1")
WARRINER = os.path.join(_REPO, "data", "grounding_testbed", "Ratings_Warriner_et_al.csv")
_RICHNESS = "base"   # 'base'=12d sensorimotor+concreteness; 'affect'=+Warriner VAD (15d); 'whitened'=12d ATL-distinctive
_WARR = None


def _warr():
    """Warriner valence/arousal/dominance, z-scored -- the affect dims sensorimotor grounding lacks."""
    global _WARR
    if _WARR is None:
        import csv
        d = {}
        with open(WARRINER, encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                try:
                    d[row["Word"].lower()] = np.array([float(row["V.Mean.Sum"]), float(row["A.Mean.Sum"]),
                                                       float(row["D.Mean.Sum"])], np.float32)
                except Exception:
                    pass
        M = np.stack(list(d.values())); mu = M.mean(0); sd = M.std(0) + 1e-9
        _WARR = {w: (v - mu) / sd for w, v in d.items()}
    return _WARR
# the landed dependency-parsed syntagmatic store (best distributional reading knowledge) for the grounded-FILTER arm
DEP_STORE = None
for _f in sorted(os.listdir(_CACHE)) if os.path.isdir(_CACHE) else []:
    if _f.startswith("consol_syntactic_1000000_"):
        DEP_STORE = os.path.join(_CACHE, _f)


def _gv(w, cache={}):
    key = (_RICHNESS, w)
    if key in cache:
        return cache[key]
    if _RICHNESS == "whitened":
        v = distinctive_grounded_vector(w)
        v = None if v is None else np.asarray(v, np.float32)
    else:
        v = grounded_vector(w)
        v = None if v is None else np.asarray(v, np.float32)
        if _RICHNESS == "affect" and v is not None:
            a = _warr().get(w)
            v = np.concatenate([v, a if a is not None else np.zeros(3, np.float32)])
    cache[key] = v
    return v


def _dgv(w, cache={}):
    if w in cache:
        return cache[w]
    v = distinctive_grounded_vector(w)
    v = None if v is None else np.asarray(v, np.float32)
    cache[w] = v
    return v


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def sense_grounding(seeds):
    # RAW grounded_vector for BOTH sense centroid and context (same space -> cosine is meaningful).
    # (distinctive/whitened is a different linear space; mixing it with raw context flips the sign.)
    vs = [_gv(w) for w in seeds]
    vs = [v for v in vs if v is not None]
    return _unit(np.mean(vs, 0)) if vs else None


def context_grounding(ctx_words):
    vs = [_gv(w) for w in ctx_words]
    vs = [v for v in vs if v is not None]
    return _unit(np.mean(vs, 0)) if vs else None


def _z(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def _grounded_channel(ctx_words, tn, sgrnd, shuffle_grnd=None):
    """BIASED COMPETITION in the GROUNDED space (the same brain mechanism as the distributional readout, applied to
    perceptual vectors) -- NOT a flat grounded-topic-blur mean. Weight each context word's grounded vector by how
    much it discriminates the candidate senses' grounded centroids; score sense = cos(grounded diagnostic query,
    sense grounded centroid). Returns (S,) or None if no grounded context/senses."""
    rows = [_unit(v) for w in ctx_words if (v := _gv(w)) is not None]
    if not rows:
        return None
    Cg = np.stack(rows); D = Cg.shape[1]
    Gg = []
    for s in tn:
        key = shuffle_grnd[s] if shuffle_grnd else s
        sg = sgrnd.get(key)
        Gg.append(sg if sg is not None else np.zeros(D, np.float32))
    Gg = np.stack(Gg)
    if not np.any(Gg):
        return None
    return diagnostic_context_scores(Cg, Gg)


def score_fused(recs, idxs, sig_by_syn, sgrnd, mat, w2i, lam, shuffle_grnd=None):
    """distributional diagnostic gloss score + lam * GROUNDED diagnostic score (both biased-competition; per-item
    z-combined). shuffle_grnd: permute the sense-grounding onto the WRONG sense (info-free twin)."""
    ok = []
    for i in idxs:
        r = recs[i]; tn = r["tn"]
        rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            continue
        G = np.stack([sig_by_syn.get(s) if sig_by_syn.get(s) is not None else np.zeros(G1.EMB_DIM, np.float32)
                      for s in tn])
        if not np.any(G):
            continue
        diag = diagnostic_context_scores(np.stack(rows), G)
        if lam == 0.0:
            fin = diag
        else:
            grnd = _grounded_channel(r["ctx"], tn, sgrnd, shuffle_grnd)
            if grnd is None:
                fin = diag
            else:
                # RELIABILITY-WEIGHTED fusion (Ernst-Banks / Feldman-Friston precision): trust the grounded cue
                # only where the candidate senses are actually SEPARABLE in grounded space -- grounding
                # discriminates concrete homonyms but not abstract/relational senses, so gate it by sense-centroid
                # separation. sep in [0,1]: 0 = grounded-indistinguishable senses (ignore grounding), 1 = far apart.
                sgvs = [_unit(v) for s in tn if (v := sgrnd.get(shuffle_grnd[s] if shuffle_grnd else s)) is not None]
                if len(sgvs) >= 2:
                    P = np.stack(sgvs); sims = P @ P.T
                    off = sims[np.triu_indices(len(sgvs), 1)]
                    sep = float(np.clip(0.5 * (1.0 - off.mean()), 0.0, 1.0))
                else:
                    sep = 0.0
                fin = _z(diag) + (lam * sep) * _z(grnd)
        ok.append(int(tn[int(np.argmax(fin))] == r["gold"]))
    return np.array(ok, float)


def grounded_filter_assocs(syn, sibs, store, sgrnd, K, cap):
    """admit reading-derived associate w to s only if grounding says it is sense-discriminative (closer to s's
    grounded centroid than to any sibling's) AND recurs >= K. The grounded version of MFS-quarantine."""
    cs = store["cooc"].get(syn, {})
    sg = sgrnd.get(syn)
    if sg is None:
        return []
    sib_g = [sgrnd.get(x) for x in sibs if sgrnd.get(x) is not None]
    scored = []
    for w, c in cs.items():
        if c < K:
            continue
        gw = _gv(w)
        if gw is None:
            continue
        gw = _unit(gw)
        self_s = float(gw @ sg)
        sib_s = max((float(gw @ g) for g in sib_g), default=-1.0)
        if self_s - sib_s > 0:
            scored.append((w, (self_s - sib_s) * c))
    scored.sort(key=lambda x: -x[1])
    return [w for w, _ in scored[:cap]]


def run(cap, lam_grid, smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0]); test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        dev_idx = dev_idx[:300]; test_idx = test_idx[:300]
    cand = set()
    for i in dev_idx + test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in cand}
    sib_by_syn = {s: G1._siblings(s) for s in cand}
    all_syn = set(cand)
    for sibs in sib_by_syn.values():
        all_syn.update(sibs)
    seeds_all = {s: G1._seed_words(s, w2i) for s in all_syn}
    sgrnd = {s: sense_grounding(seeds_all[s]) for s in all_syn}
    cov = np.mean([sgrnd[s] is not None for s in cand])
    print("[run] dev=%d test=%d cand=%d sense-grounding-coverage=%.2f (%.0fs)"
          % (len(dev_idx), len(test_idx), len(cand), cov, time.time() - t0), flush=True)

    gloss_sig = {s: G1._sigvec(mat, w2i, seeds_by_syn[s]) for s in cand}

    # --- arm 1: gloss (diag only) ---
    g_dev = score_fused(recs, dev_idx, gloss_sig, sgrnd, mat, w2i, 0.0)
    g_test = score_fused(recs, test_idx, gloss_sig, sgrnd, mat, w2i, 0.0)

    # --- arm 2: GROUNDED-FUSE (diag + lam*grounded), sweep lam on dev ---
    fuse_sweep = {}
    best_lam = 0.0; best_dev = float(g_dev.mean())
    for lam in lam_grid:
        dv = float(score_fused(recs, dev_idx, gloss_sig, sgrnd, mat, w2i, lam).mean())
        fuse_sweep["lam%.2f" % lam] = round(dv, 4)
        print("[sweep] grounded-fuse lam=%.2f dev=%.4f (%.0fs)" % (lam, dv, time.time() - t0), flush=True)
        if dv > best_dev:
            best_dev = dv; best_lam = lam
    fuse_test = score_fused(recs, test_idx, gloss_sig, sgrnd, mat, w2i, best_lam)

    # --- arm 3: GROUNDED-FILTER reading associates (from the dependency store) admitted, then FUSE ---
    filt_test = None; full_test = None; n_dep = 0
    if DEP_STORE and os.path.exists(DEP_STORE):
        store = pickle.load(open(DEP_STORE, "rb")); n_dep = store.get("n_binds", 0)
        filt_assoc = {s: grounded_filter_assocs(s, sib_by_syn[s], store, sgrnd, 2, cap) for s in cand}
        filt_sig = {s: G1._sigvec(mat, w2i, list(seeds_by_syn[s]) + list(filt_assoc[s])) for s in cand}
        filt_test = score_fused(recs, test_idx, filt_sig, sgrnd, mat, w2i, 0.0)          # filtered reading, no fuse
        full_test = score_fused(recs, test_idx, filt_sig, sgrnd, mat, w2i, best_lam)     # filtered reading + fuse
        print("[arm] grounded-filter mean assoc/sense=%.1f"
              % np.mean([len(filt_assoc[s]) for s in cand]), flush=True)

    # --- STRATIFIED: does grounding help where senses are grounded-SEPARABLE (concrete) vs not (abstract)? ---
    def _sep(tn):
        vs = [_unit(v) for s in tn if (v := sgrnd.get(s)) is not None]
        if len(vs) < 2:
            return 0.0
        P = np.stack(vs); off = (P @ P.T)[np.triu_indices(len(vs), 1)]
        return float(np.clip(0.5 * (1.0 - off.mean()), 0.0, 1.0))
    seps = np.array([_sep(recs[i]["tn"]) for i in test_idx])
    thr = float(np.median(seps))
    hi = [test_idx[k] for k in range(len(test_idx)) if seps[k] > thr]
    lo = [test_idx[k] for k in range(len(test_idx)) if seps[k] <= thr]
    strat = {}
    for name, ix in [("HIGH_sep_grounded_separable", hi), ("LOW_sep_grounded_indistinct", lo)]:
        gl = score_fused(recs, ix, gloss_sig, sgrnd, mat, w2i, 0.0)
        fu = score_fused(recs, ix, gloss_sig, sgrnd, mat, w2i, best_lam)
        strat[name] = {"n": len(ix), "gloss": round(float(gl.mean()), 4), "fuse": round(float(fu.mean()), 4),
                       "fuse_vs_gloss": G1._paired(fu, gl, 610)}
        print("[strat] %-30s n=%d gloss=%.4f fuse=%.4f sep=%s"
              % (name, len(ix), strat[name]["gloss"], strat[name]["fuse"], strat[name]["fuse_vs_gloss"]["sep"]),
              flush=True)

    # --- ceiling + info-free twin ---
    syntag_sig = {s: G1._sigvec(mat, w2i, list(seeds_by_syn[s]) + [w.lower().split("_")[0] for w in syntag.get(s, [])])
                  for s in cand}
    cur_test = score_fused(recs, test_idx, syntag_sig, sgrnd, mat, w2i, 0.0)
    rng = np.random.default_rng(7); cl = sorted(cand); perm = list(cl); rng.shuffle(perm)
    shuf = dict(zip(cl, perm))
    twin_test = score_fused(recs, test_idx, gloss_sig, sgrnd, mat, w2i, best_lam, shuffle_grnd=shuf)

    n = len(g_test)
    res = {"n_dev": len(dev_idx), "n_test": len(test_idx), "cap": cap, "best_lam": best_lam,
           "sense_grounding_coverage": round(float(cov), 3), "fuse_sweep": fuse_sweep, "n_dep_binds": n_dep,
           "a_s_test": {"gloss": round(float(g_test.mean()), 4),
                        "GROUNDED_fuse": round(float(fuse_test.mean()), 4),
                        "curated_syntagnet": round(float(cur_test.mean()), 4),
                        "twin_shuffled_grounding": round(float(twin_test.mean()), 4)},
           "GROUNDED_fuse_vs_gloss": G1._paired(fuse_test[:n], g_test[:n], 601),
           "GROUNDED_fuse_vs_shuffled": G1._paired(fuse_test[:n], twin_test[:n], 602),
           "stratified_by_grounded_separability": strat}
    if filt_test is not None:
        res["a_s_test"]["grounded_filter_reading"] = round(float(filt_test.mean()), 4)
        res["a_s_test"]["grounded_filter_plus_fuse"] = round(float(full_test.mean()), 4)
        res["FULL_vs_gloss"] = G1._paired(full_test[:n], g_test[:n], 603)
        res["filter_vs_gloss"] = G1._paired(filt_test[:n], g_test[:n], 604)
    res["headline"] = ("GROUNDED CROSSING | gloss=%.3f GROUNDED_fuse=%.3f (lam=%.2f, sep_vs_gloss=%s null=%s) "
                       "curated=%.3f | twin_shuf=%.3f (fuse>shuf sep=%s)%s"
                       % (res["a_s_test"]["gloss"], res["a_s_test"]["GROUNDED_fuse"], best_lam,
                          res["GROUNDED_fuse_vs_gloss"]["sep"], res["GROUNDED_fuse_vs_gloss"]["null_p95"],
                          res["a_s_test"]["curated_syntagnet"], res["a_s_test"]["twin_shuffled_grounding"],
                          res["GROUNDED_fuse_vs_shuffled"]["sep"],
                          "" if filt_test is None else " | filter+fuse=%.3f (sep=%s)"
                          % (res["a_s_test"]["grounded_filter_plus_fuse"], res["FULL_vs_gloss"]["sep"])))
    res["richness"] = _RICHNESS
    res["elapsed_s"] = round(time.time() - t0, 1)
    tag = ("smoke" if smoke else "full") + "_" + _RICHNESS
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_grounded_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    import numpy as np
    rb = sense_grounding(["slope", "land", "water", "river", "edge"])
    mb = sense_grounding(["financial", "institution", "money", "loan", "deposit"])
    cr = context_grounding(["water", "fish", "boat", "flow"])
    assert rb is not None and mb is not None and cr is not None, "grounding must cover common words"
    sim_r = float(cr @ rb); sim_m = float(cr @ mb)
    assert sim_r > sim_m, "grounded context must match the RIGHT sense centroid more (%.3f vs %.3f)" % (sim_r, sim_m)
    print("SELFTEST PASS (grounding separates senses: river-ctx river=%.3f > money=%.3f)" % (sim_r, sim_m), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--richness", default="base", choices=["base", "affect", "whitened"])
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    global _RICHNESS
    _RICHNESS = args.richness
    print("[richness] %s" % _RICHNESS, flush=True)
    run(args.cap, [0.25, 0.5, 0.75, 1.0, 1.5, 2.0], smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
