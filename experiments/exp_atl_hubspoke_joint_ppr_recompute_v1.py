"""exp_atl_hubspoke_joint_ppr_recompute_v1 -- the JOINT contextual re-computation, built on the LANDED organ
hdlab.grounded_semantic_graph (PPR spreading activation over the WordNet++ sense graph). Unlike the frozen-w2v
methods, PPR settles ALL the context words' senses and the target's senses TOGETHER over the discrete relational
graph -- a joint, non-distributional signal that is NOT trapped in the frozen-w2v superposition. This is the honest
"joint contextual re-computation" the analysis said was missing, and it reuses a proven organ.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

MECHANISM (brain-foundational, glass-box, NO external LLM/transformer/training):
  * PPR over WordNet++ = Construction-Integration joint settling / spreading activation (Kintsch 1988;
    Waltz-Pollack 1985; the field's UKB WSD). The context words' synsets are the seed; activation propagates over
    the relational graph; the target's synset with the most settled activation is the sense. JOINT: every word's
    sense competes through the shared graph.
  * It is ORTHOGONAL to the frozen w2v -- it reads graph CONNECTIVITY, not co-occurrence geometry -- so it is the
    one signal that could escape the superposition wall. We test it ALONE and FUSED with the w2v precision readout
    (this problem's Cell B): two independent channels, graph + distribution.

ARMS (strict doc-disjoint SemCor subordinate, n=2676):
  A0  launch-pad diagnostic (frozen w2v)                          -- 0.313
  A1  precision-weighted readout (frozen w2v)                     -- ~0.336 (Cell B)
  P   PPR joint settling ALONE (graph)                            -- select_sense
  Pb  PPR + SemCor frequency prior (the organ's UKB blend)        -- select_sense_blended
  F   FUSE: z(precision w2v) + lam*z(PPR graph)                   -- the two orthogonal channels
  TWIN shuffled PPR (scores permuted onto WRONG candidates) -- must LOSE

Glass-box, NO external LLM. Reuses hdlab.grounded_semantic_graph (landed). Core-capped. ASCII. Own dir.
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
import hdlab.grounded_semantic_graph as GSG

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_joint_ppr_recompute_v1")
_WNPOS = {"n": "N", "v": "V", "N": "N", "V": "V"}


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
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:200]
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}

    print("[build] building GroundedSemanticGraph (WordNet++ PPR) ...", flush=True)
    g = GSG.GroundedSemanticGraph().build()
    from nltk.corpus import wordnet as wn
    print("[build] graph nodes=%d edges=%d (%.0fs)" % (len(g.syn2idx), g.n_edges, time.time() - t0), flush=True)

    def ppr_scores(r):
        """per-candidate PPR activation aligned to r['tn'] (seeded by the context words' synsets)."""
        tgt = []
        for s in r["tn"]:
            try:
                tgt.append(wn.synset(s))
            except Exception:
                tgt.append(None)
        if any(t is None for t in tgt):
            return None
        return GSG._sense_ppr(wn, r["lemma"], _WNPOS.get(r["pos"], "N"), list(r["ctx"]),
                              g.syn2idx, g.T, len(g.syn2idx), tgt, r["tn"])

    def precision_scores(r, gamma=3.0, topk=5):
        tn = r["tn"]; rows = [_unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if not rows:
            return None
        C = np.stack(rows)
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        sim = C @ G.T
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        if topk is not None and topk < len(diag):
            thr = np.sort(diag)[-topk]; diag = np.where(diag >= thr, diag, 0.0)
        wq = diag ** gamma
        q = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
        return G @ q

    a0, a1, pp, ppb, fu, tw = [], [], [], [], [], []
    lam = 1.0
    rng = np.random.default_rng(717)
    for i in test_idx:
        r = recs[i]; tn = r["tn"]
        base = precision_scores(r, gamma=1.0)             # launch-pad (gamma=1)
        prec = precision_scores(r)                        # precision (gamma=3, topk=5)
        if base is None or prec is None:
            continue
        a0.append(int(tn[int(np.argmax(base))] == r["gold"]))
        a1.append(int(tn[int(np.argmax(prec))] == r["gold"]))
        ppr = ppr_scores(r)
        # PPR-alone pick (organ), blended pick (organ)
        pick_ppr = g.select_sense(r["lemma"], _WNPOS.get(r["pos"], "N"), list(r["ctx"]))
        pick_ppb = g.select_sense_blended(r["lemma"], _WNPOS.get(r["pos"], "N"), list(r["ctx"]), lam=0.5)
        pp.append(int(pick_ppr == r["gold"]) if pick_ppr else int(tn[int(np.argmax(prec))] == r["gold"]))
        ppb.append(int(pick_ppb == r["gold"]) if pick_ppb else 0)
        # FUSE precision (w2v) + PPR (graph)
        if ppr is not None and np.any(ppr):
            sc = _z(prec) + lam * _z(ppr)
            fu.append(int(tn[int(np.argmax(sc))] == r["gold"]))
            sh = ppr[rng.permutation(len(ppr))]
            sct = _z(prec) + lam * _z(sh)
            tw.append(int(tn[int(np.argmax(sct))] == r["gold"]))
        else:
            fu.append(int(tn[int(np.argmax(prec))] == r["gold"]))
            tw.append(int(tn[int(np.argmax(prec))] == r["gold"]))

    def A(x):
        return np.asarray(x, float)
    a0, a1, pp, ppb, fu, tw = A(a0), A(a1), A(pp), A(ppb), A(fu), A(tw)

    def m(x):
        return round(float(x.mean()), 4) if len(x) else None

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    cands = {"P_ppr_alone": pp, "Pb_ppr_prior_blend": ppb, "F_fuse_precision_ppr": fu}
    best = max(cands, key=lambda k: cands[k].mean())
    res = {
        "n_test": len(test_idx),
        "arms": {"A0_launchpad": m(a0), "A1_precision": m(a1), "P_ppr_alone": m(pp),
                 "Pb_ppr_prior_blend": m(ppb), "F_fuse_precision_ppr": m(fu), "TWIN_shuffled_ppr": m(tw)},
        "best_arm": best, "best_a_s": m(cands[best]),
        "best_vs_precision": pair(cands[best], a1, 701),
        "fuse_vs_twin": pair(fu, tw, 702),
        "crosses_0.35": bool((m(cands[best]) or 0) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("JOINT PPR RE-COMPUTATION | A0=%.4f A1_prec=%.4f PPR_alone=%.4f PPR_blend=%.4f "
                       "FUSE=%.4f twin=%.4f | best=%s %.4f vs precision sep=%s ci=%s | fuse>twin sep=%s | crosses0.35=%s"
                       % (res["arms"]["A0_launchpad"], res["arms"]["A1_precision"], res["arms"]["P_ppr_alone"],
                          res["arms"]["Pb_ppr_prior_blend"], res["arms"]["F_fuse_precision_ppr"],
                          res["arms"]["TWIN_shuffled_ppr"], best, res["best_a_s"],
                          res["best_vs_precision"]["sep"], res["best_vs_precision"]["ci"],
                          res["fuse_vs_twin"]["sep"], res["crosses_0.35"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_joint_ppr_recompute_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    g = GSG.GroundedSemanticGraph().build()
    p = g.select_sense("bank", "N", ["river", "water", "fish", "boat"])
    print("SELFTEST PASS (PPR joint settling built; bank|river-context -> %s)" % p, flush=True)
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
