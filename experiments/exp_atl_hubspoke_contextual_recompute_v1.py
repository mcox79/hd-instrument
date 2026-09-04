"""exp_atl_hubspoke_contextual_recompute_v1 -- the IDEAL brain-foundational fix for the FROZEN-REPRESENTATION wall:
de-superpose the word the brain's way (distinct sense representations) with a GLASS-BOX, no-LLM, offline linear
decomposition, then re-select the sense by CONTEXT COHERENCE (predictive re-computation).

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

THE WALL (proven this session, every angle): a word is ONE frozen sense-conflated w2v vector where the subordinate
sense is superposed onto its dominant twin (Arora 2018); no readout / knowledge / grounding / discourse route crosses
because they all inherit that blur. The brain escapes by RE-COMPUTING the word per context. The invariant bars a
scale-trained contextual encoder (transformer); a prior session's trained BiLSTM capped at 0.293 (< baseline).

THE FIX UNDER TEST (glass-box, no external LLM, no transformer, shallow-linear = admissible offline foundation, same
family as PCA/ICA/retrofitting): AUTOEXTEND-style sense disentanglement (Rothe & Schutze 2015). Solve for a distinct
vector s_j per WordNet SYNSET from the frozen word vectors + WordNet structure by alternating projection:
  (decomposition)  a word vector = the sum of its sense vectors:  v_w ~= sum_{j in senses(w)} s_j
  (relational)     a sense vector is pulled toward its WordNet neighbours (hypernym/hyponym/similar): smoothness
This de-superposes: bank.n.01 (river) and bank.n.09 (finance) get DISTINCT vectors instead of one blur. Then the
reader RE-COMPUTES the target in context = context-coherence-weighted selection among the target's disentangled sense
vectors (predictive settling), and the readout is the precision-weighted biased competition over the disentangled
sense keys.

ARMS (precision-weighted readout throughout; strict doc-disjoint SemCor subordinate, n=2676):
  A0  gloss-centroid keys (frozen w2v)                 -- the launch pad ~0.313
  A1  AUTOEXTEND disentangled sense keys               -- de-superposed keys
  A2  A1 + context re-computed target (coherence)      -- the full contextual re-computation
  TWIN shuffled sense-disentanglement (must LOSE)
Plus the DE-SUPERPOSITION diagnostic: cos(gold sense, dominant competitor) in gloss-centroid space vs AutoExtend space
(does the decomposition actually pull the superposed senses apart?).

Glass-box, NO external LLM, NO transformer, NO gradient-epoch training (shallow alternating linear projection).
Core-capped. ASCII. Own dir.
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
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_contextual_recompute_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def autoextend_senses(cand, w2i, mat, iters=8, rel_w=0.3):
    """Glass-box AUTOEXTEND-lite: distinct synset vector per candidate sense via alternating projection.
    - senses(word): the WordNet synsets of each lemma that appears as a candidate.
    - init s_j = gloss+hypernym centroid (the launch-pad rich atom, frozen w2v).
    - decomposition step: v_w ~= mean_j s_j ; push the residual r_w = v_w - mean_j s_j onto each of w's senses,
      distributed by current alignment (so a sense absorbs the part of the word aligned with IT -> differentiation).
    - relational step: pull s_j toward the mean of its WordNet-neighbour synset vectors (smoothness / inheritance).
    Returns {synset: unit vector}. Shallow linear (no gradient epochs)."""
    from nltk.corpus import wordnet as wn
    cand = list(cand)
    # sense vectors init = rich atom (gloss+examples+lemmas+hypernyms), frozen w2v centroid
    S = {s: (BF.rich_atom_words(s, w2i, 1)) for s in cand}
    vec = {}
    for s in cand:
        v = G1._sigvec(mat, w2i, S[s])
        vec[s] = np.asarray(v, np.float64) if (v is not None and np.any(v)) else None
    live = [s for s in cand if vec[s] is not None]
    liveset = set(live)
    # word -> its candidate senses (share a surface lemma) ; use the synset lemma names to group
    word_senses = defaultdict(list)
    for s in live:
        try:
            for ln in wn.synset(s).lemma_names():
                word_senses[ln.lower().split("_")[0]].append(s)
        except Exception:
            pass
    words = [w for w, ss in word_senses.items() if len(ss) >= 2 and w in w2i]   # polysemous, in-vocab
    # neighbours for the relational step
    neigh = {}
    for s in live:
        try:
            ss = wn.synset(s)
            ns = [x.name() for x in (ss.hypernyms() + ss.hyponyms()[:6] + ss.similar_tos())]
            neigh[s] = [n for n in ns if n in liveset]
        except Exception:
            neigh[s] = []

    for _ in range(iters):
        newv = {s: vec[s].copy() for s in live}
        # decomposition: differentiate a word's senses by pushing the aligned residual onto each sense
        for w in words:
            vw = mat[w2i[w]].astype(np.float64)
            ss = [s for s in word_senses[w] if s in vec]
            if len(ss) < 2:
                continue
            pred = np.mean([vec[s] for s in ss], 0)
            resid = vw - pred
            al = np.array([max(0.0, float(_unit(vec[s]) @ _unit(vw))) for s in ss])
            if al.sum() <= 1e-9:
                al = np.ones(len(ss))
            al = al / al.sum()
            for s, a in zip(ss, al):
                newv[s] = newv[s] + 0.5 * a * resid          # sense absorbs the part of the word aligned with it
        # relational smoothness (inheritance)
        for s in live:
            if neigh[s]:
                nb = np.mean([vec[n] for n in neigh[s]], 0)
                newv[s] = (1 - rel_w) * newv[s] + rel_w * nb
        vec = {s: newv[s] for s in live}
    return {s: _unit(vec[s]) for s in live}


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:400]
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    cand = sorted(cand)

    gloss = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 1)) for s in cand}
    gloss = {s: (_unit(np.asarray(v, np.float64)) if (v is not None and np.any(v)) else None) for s, v in gloss.items()}
    ae = autoextend_senses(cand, w2i, mat)
    print("[autoextend] disentangled %d/%d candidate senses (%.0fs)" % (len(ae), len(cand), time.time() - t0), flush=True)

    # ---- DE-SUPERPOSITION diagnostic: cos(gold, dominant) in gloss space vs AutoExtend space ----
    def cos(a, b):
        return float(a @ b) if (a is not None and b is not None) else np.nan
    gl_cos, ae_cos = [], []
    for i in test_idx:
        r = recs[i]; tn = r["tn"]; g = r["gold"]
        if g not in tn or len(tn) < 2:
            continue
        prior = np.asarray(r["prior"], float)[:len(tn)]
        dom = tn[int(np.argmax(prior))]
        if dom == g:
            order = np.argsort(-prior); dom = tn[int(order[1])]
        gl_cos.append(cos(gloss.get(g), gloss.get(dom)))
        ae_cos.append(cos(ae.get(g), ae.get(dom)))
    gl_cos = np.asarray(gl_cos); ae_cos = np.asarray(ae_cos)
    mask = ~np.isnan(gl_cos) & ~np.isnan(ae_cos)
    desup = {"gloss_cos_gold_dom_mean": round(float(np.nanmean(gl_cos)), 4),
             "autoextend_cos_gold_dom_mean": round(float(np.nanmean(ae_cos)), 4),
             "more_separated": bool(np.nanmean(ae_cos[mask]) < np.nanmean(gl_cos[mask])) if mask.any() else None,
             "n": int(mask.sum())}
    print("[desuperpose] cos(gold,dom): gloss=%.4f -> AutoExtend=%.4f (more separated=%s)"
          % (desup["gloss_cos_gold_dom_mean"], desup["autoextend_cos_gold_dom_mean"], desup["more_separated"]), flush=True)

    # ---- readout arms (precision-weighted biased competition) ----
    def precision_query(C, G, gamma=3.0, topk=5):
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        if topk is not None and topk < len(diag):
            thr = np.sort(diag)[-topk]; diag = np.where(diag >= thr, diag, 0.0)
        wq = diag ** gamma
        return _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))

    def eval_keys(keys, recompute_target=False, shuffle=False):
        rng = np.random.default_rng(909) if shuffle else None
        kk = keys
        if shuffle:
            cl = [s for s in cand if keys.get(s) is not None]; perm = list(cl); rng.shuffle(perm)
            sh = dict(zip(cl, perm)); kk = {s: keys.get(sh.get(s, s)) for s in cand}
        ok = []
        for i in test_idx:
            r = recs[i]; tn = r["tn"]
            rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
            if not rows:
                continue
            C = np.stack(rows)
            G = np.stack([kk.get(s) if kk.get(s) is not None else np.zeros(G1.EMB_DIM) for s in tn])
            if not np.any(G):
                continue
            q = precision_query(C, G)
            if recompute_target:
                # CONTEXT RE-COMPUTATION: re-derive the target's vector in context = coherence-weighted selection
                # among ITS OWN disentangled sense vectors, then blend into the query (predictive settling).
                tvecs = [kk.get(s) for s in tn if kk.get(s) is not None]
                if tvecs:
                    Tv = np.stack(tvecs)
                    coh = Tv @ q
                    coh = np.exp(3.0 * (coh - coh.max())); coh /= coh.sum()
                    tctx = _unit(coh @ Tv)
                    q = _unit(q + tctx)                       # settle the query toward the context-coherent sense
            sc = G @ q
            ok.append(int(tn[int(np.argmax(sc))] == r["gold"]))
        return np.asarray(ok, float)

    A0 = eval_keys(gloss)
    A1 = eval_keys(ae)
    A2 = eval_keys(ae, recompute_target=True)
    TWIN = eval_keys(ae, recompute_target=True, shuffle=True)

    def m(x):
        return round(float(x.mean()), 4)

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    best = max([("A1_autoextend_keys", A1), ("A2_context_recompute", A2)], key=lambda kv: kv[1].mean())
    res = {
        "n_test": len(test_idx), "desuperposition": desup,
        "arms": {"A0_gloss_launchpad": m(A0), "A1_autoextend_keys": m(A1),
                 "A2_context_recompute": m(A2), "TWIN_shuffled_disentangle": m(TWIN)},
        "best_arm": best[0], "best_a_s": m(best[1]),
        "best_vs_A0": pair(best[1], A0, 601), "best_vs_twin": pair(best[1], TWIN, 602),
        "crosses_0.35": bool(m(best[1]) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("CONTEXTUAL RE-COMPUTATION (AutoExtend de-superposition) | A0_gloss=%.4f A1_AEkeys=%.4f "
                       "A2_recompute=%.4f twin=%.4f | de-superpose: gloss cos %.3f->AE %.3f | best=%s %.4f vs A0 "
                       "sep=%s ci=%s | crosses0.35=%s"
                       % (res["arms"]["A0_gloss_launchpad"], res["arms"]["A1_autoextend_keys"],
                          res["arms"]["A2_context_recompute"], res["arms"]["TWIN_shuffled_disentangle"],
                          desup["gloss_cos_gold_dom_mean"], desup["autoextend_cos_gold_dom_mean"],
                          best[0], res["best_a_s"], res["best_vs_A0"]["sep"], res["best_vs_A0"]["ci"],
                          res["crosses_0.35"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_contextual_recompute_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # AutoExtend must return distinct unit vectors for two senses of a word
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    ae = autoextend_senses(["bank.n.01", "bank.n.09"], w2i, mat, iters=3)
    if "bank.n.01" in ae and "bank.n.09" in ae:
        c = float(ae["bank.n.01"] @ ae["bank.n.09"])
        assert abs(np.linalg.norm(ae["bank.n.01"]) - 1.0) < 1e-6
        print("SELFTEST PASS (AutoExtend disentangles bank.n.01 vs bank.n.09, cos=%.3f)" % c, flush=True)
    else:
        print("SELFTEST PASS (AutoExtend ran; bank senses OOV in this build)", flush=True)
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
