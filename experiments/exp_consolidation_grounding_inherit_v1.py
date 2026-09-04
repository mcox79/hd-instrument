"""exp_consolidation_grounding_inherit_v1 -- BRAIN-FOUNDATIONAL grounding to full coverage: NOT a ridge regressor
(the brain does not regress word-vectors onto feature-ratings), but SEMANTIC INHERITANCE through the concept
hierarchy -- the mechanism the brain actually uses to ground abstract/unseen concepts.

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

HOW THE BRAIN DOES THIS (PINNED): grounded meaning = perceptual/affective experience bound to a word in the ATL
hub-and-spoke (Patterson 2007; Lambon-Ralph 2017). The Lancaster/Warriner norms are our PINNED SUBSTITUTE for the
perceptual spoke. Coverage to concepts NOT directly perceived comes from CATEGORY-BASED INFERENCE: a hyponym
inherits its hypernym's grounded features, and an abstract sense inherits from its concrete relatives -- spreading
activation / inheritance in the semantic hierarchy (the ATL hub over the WordNet++ graph, our grounded_semantic_graph
organ). NO regression, NO external LLM, NO training on a ratings table -- the ONLY "learning" is Hebbian binding +
CLS consolidation (this problem's gate + hdlab.cls_growth).

MECHANISM: sense_grounding_inherit(synset) aggregates grounded_vector over the synset's OWN lemma/gloss words PLUS
its hypernym chain (inherit UP, decayed by distance) PLUS its hyponyms (aggregate the concrete descendants that
ground an abstract sense DOWN), weighted by hierarchy distance. Fused with the distributional diagnostic readout
(reusing the grounded cell's biased-competition fusion). Strict doc-disjoint SemCor subordinate, n=2676. ASCII.
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
import experiments.exp_consolidation_grounded_v1 as GR   # reuse the biased-competition grounded fusion

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_grounding_inherit_v1")
_ICACHE = {}


def sense_grounding_inherit(syn_name, up_depth=3, n_hypo=12, decay=0.5):
    """Grounded centroid by SEMANTIC INHERITANCE through the WordNet hierarchy (the brain's category-based
    grounding inference), aggregating grounded_vector over own + hypernym-chain + hyponym words, distance-weighted."""
    if syn_name in _ICACHE:
        return _ICACHE[syn_name]
    from nltk.corpus import wordnet as wn
    weighted = []   # (word, weight)

    def add(syn, w):
        for ln in syn.lemma_names():
            weighted.append((ln.lower().split("_")[0], w))
        for tok in G1._toks(syn.definition()):
            weighted.append((tok, w * 0.5))
    try:
        s = wn.synset(syn_name)
    except Exception:
        _ICACHE[syn_name] = None
        return None
    add(s, 1.0)
    cur = [s]; ww = decay
    for _ in range(up_depth):                       # inherit UP the hypernym chain (decayed)
        nxt = []
        for x in cur:
            for h in x.hypernyms():
                add(h, ww); nxt.append(h)
        cur = nxt; ww *= decay
        if not cur:
            break
    for h in s.hyponyms()[:n_hypo]:                 # aggregate concrete descendants DOWN (ground abstract senses)
        add(h, decay)
    vs = []
    for word, wt in weighted:
        g = GR._gv(word)
        if g is not None:
            vs.append(GR._unit(np.asarray(g, np.float32)) * wt)
    v = GR._unit(np.sum(vs, 0)) if vs else None
    _ICACHE[syn_name] = v
    return v


def run(smoke=False):
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
    gloss_sig = {s: G1._sigvec(mat, w2i, seeds_by_syn[s]) for s in cand}
    # BRAIN-FAITHFUL grounding: inheritance through the hierarchy (vs the gloss-only centroid in the grounded cell)
    sgrnd_inh = {s: sense_grounding_inherit(s) for s in cand}
    sgrnd_gloss = {s: GR.sense_grounding(seeds_by_syn[s]) for s in cand}   # the shallow (own-gloss-only) baseline
    cov = np.mean([sgrnd_inh[s] is not None for s in cand])
    print("[run] dev=%d test=%d cand=%d inherit-coverage=%.2f (%.0fs)"
          % (len(dev_idx), len(test_idx), len(cand), cov, time.time() - t0), flush=True)

    def fuse(idxs, sgrnd, lam, shuffle=None):
        return GR.score_fused(recs, idxs, gloss_sig, sgrnd, mat, w2i, lam, shuffle_grnd=shuffle)

    g_test = fuse(test_idx, sgrnd_inh, 0.0)
    out = {"n_dev": len(dev_idx), "n_test": len(test_idx), "inherit_coverage": round(float(cov), 3), "arms": {}}
    for name, sg in [("INHERIT", sgrnd_inh), ("gloss_only_centroid", sgrnd_gloss)]:
        best_lam, best_dev = 0.0, float(fuse(dev_idx, sg, 0.0).mean())
        sweep = {}
        for lam in [0.25, 0.5, 0.75, 1.0, 1.5]:
            dv = float(fuse(dev_idx, sg, lam).mean()); sweep["lam%.2f" % lam] = round(dv, 4)
            if dv > best_dev:
                best_dev, best_lam = dv, lam
        ft = fuse(test_idx, sg, best_lam)
        out["arms"][name] = {"best_lam": best_lam, "sweep": sweep, "a_s": round(float(ft.mean()), 4),
                             "vs_gloss": G1._paired(ft[:len(g_test)], g_test, 801)}
        print("[arm] %-20s best_lam=%.2f a_s=%.4f sep_vs_gloss=%s (%.0fs)"
              % (name, best_lam, out["arms"][name]["a_s"], out["arms"][name]["vs_gloss"]["sep"], time.time() - t0),
              flush=True)
    out["a_s_gloss"] = round(float(g_test.mean()), 4)
    out["headline"] = ("GROUNDING-BY-INHERITANCE | gloss=%.3f INHERIT_fuse=%.3f (sep=%s null=%s) "
                       "gloss-centroid_fuse=%.3f"
                       % (out["a_s_gloss"], out["arms"]["INHERIT"]["a_s"], out["arms"]["INHERIT"]["vs_gloss"]["sep"],
                          out["arms"]["INHERIT"]["vs_gloss"]["null_p95"], out["arms"]["gloss_only_centroid"]["a_s"]))
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_grounding_inherit_v1", "verdict": "MEASURED", "result": out}, f,
                  indent=2, default=str)
    print("[run] " + out["headline"], flush=True)
    return out


def self_test():
    v = sense_grounding_inherit("car.n.01")
    assert v is not None and len(v) == 12, "inheritance grounding returns a 12-dim centroid"
    print("SELFTEST PASS (inheritance grounding: car.n.01 -> %d-dim)" % len(v), flush=True)
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
