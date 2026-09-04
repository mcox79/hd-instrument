"""exp_atl_hubspoke_ppr_signal_loss_v1 -- AGGRESSIVE DRILL of the joint-PPR located negative: WHERE does the
spreading-activation signal leak, and do the brain-faithful refinements (which PageRank lacks) recover it?

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

The joint PPR over WordNet++ (hdlab.grounded_semantic_graph) is topical: PPR-alone a_s 0.264 < precision 0.342. The
hypothesis for WHY (mechanism-diff from the brain's spreading activation): (1) PAGERANK DEGREE-BIAS -- the dominant
sense is a higher-degree node so it gets more stationary activation regardless of context; (2) NO INTEGRATION PHASE
-- Kintsch construction-integration follows diffusion with a competitive lateral-inhibition settling that suppresses
topically-central-but-incoherent nodes, which plain PPR lacks; (3) EDGE SEMANTICS -- WordNet++ edges are topical
relatedness, and the brain's are experience-weighted + fan-normalized (ACT-R fan effect divides association strength
by a node's number of associations, countering the degree-bias).

THIS CELL measures the leak and tests each brain-faithful refinement:
  DIAGNOSTIC: how often PPR-argmax == the DOMINANT sense; corr(PPR activation, node in-degree) and corr(PPR, prior).
  ARMS (a_s, strict doc-disjoint SemCor subordinate):
    ppr_raw            -- the organ's PPR (0.264 baseline)
    ppr_debiased       -- ppr / static-PageRank (UKB-style ppr_w2w: remove the degree/frequency stationary bias)
    ppr_over_prior     -- ppr / SemCor-frequency-prior (remove the dominant-sense bias directly)
    ppr_integrated     -- + Kintsch INTEGRATION: competitive lateral-inhibition settling to a fixed point
    ppr_debiased_integr-- de-bias + integration (the fullest brain-faithful spreading activation)
  vs precision readout 0.342 and the 0.35 ceiling; shuffled twin on the winner.

Glass-box, NO external LLM. Reuses hdlab.grounded_semantic_graph. Core-capped. ASCII. Own dir.
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
import hdlab.grounded_semantic_graph as GSG

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_ppr_signal_loss_v1")
_WNPOS = {"n": "N", "v": "V", "N": "N", "V": "V"}


def _integrate(ppr, iters=5, beta=6.0):
    """Kintsch INTEGRATION over the candidate scores: competitive lateral-inhibition settling (softmax sharpening
    to a fixed point). Suppresses topically-central-but-lower nodes -- the phase plain PPR diffusion lacks."""
    a = np.clip(np.asarray(ppr, float), 0, None)
    if a.sum() <= 1e-12:
        return a
    a = a / a.sum()
    for _ in range(iters):
        w = np.exp(beta * (a - a.max()))
        a = a * w
        s = a.sum()
        if s <= 1e-12:
            break
        a = a / s
    return a


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:250]

    from nltk.corpus import wordnet as wn
    print("[build] building GroundedSemanticGraph ...", flush=True)
    g = GSG.GroundedSemanticGraph().build()
    n = len(g.syn2idx)
    # static PageRank (uniform restart) = the context-FREE stationary bias (high for high-degree/dominant nodes)
    static_pr = GSG._ppr(list(range(n)), g.T, n)
    if static_pr is None:
        static_pr = np.ones(n) / n
    # node in-degree proxy (number of in-links) from T's sparsity
    indeg = np.asarray((g.T > 0).sum(axis=0)).ravel().astype(float)
    print("[build] nodes=%d edges=%d static-PR + in-degree ready (%.0fs)" % (n, g.n_edges, time.time() - t0), flush=True)

    def prior(r, tn):
        counts = []
        for s in tn:
            try:
                syn = wn.synset(s); c = 0
                for l in syn.lemmas():
                    if l.name().lower() == r["lemma"].lower():
                        c = l.count(); break
                counts.append(float(c))
            except Exception:
                counts.append(0.0)
        counts = np.array(counts, float)
        if counts.sum() == 0:
            counts = 1.0 / (1.0 + np.arange(len(tn)))
        return counts

    arms = {k: [] for k in ["ppr_raw", "ppr_debiased", "ppr_over_prior", "ppr_integrated",
                            "ppr_debiased_integr", "twin_debiased_integr"]}
    diag = {"n": 0, "ppr_pick_is_dominant": 0, "ppr_act_vs_indeg": [], "ppr_act_vs_prior": []}
    rng = np.random.default_rng(31337)
    for i in test_idx:
        r = recs[i]; tn = r["tn"]
        if len(tn) < 2:
            continue
        tgt = []
        ok_syn = True
        for s in tn:
            try:
                tgt.append(wn.synset(s))
            except Exception:
                ok_syn = False; break
        if not ok_syn:
            continue
        ppr = GSG._sense_ppr(wn, r["lemma"], _WNPOS.get(r["pos"], "N"), list(r["ctx"]),
                             g.syn2idx, g.T, n, tgt, tn)
        if ppr is None or not np.any(ppr):
            continue
        pr = prior(r, tn)
        idx = np.array([g.syn2idx.get(s, -1) for s in tn])
        spr = np.array([static_pr[j] if j >= 0 else 1e-9 for j in idx])
        deg = np.array([indeg[j] if j >= 0 else 1.0 for j in idx])
        dom = tn[int(np.argmax(pr))]
        gold = r["gold"]

        raw = ppr
        debiased = ppr / (spr + 1e-9)
        over_prior = ppr / (pr + 0.1)
        integrated = _integrate(ppr)
        deb_integr = _integrate(debiased)

        def pick(sc):
            return tn[int(np.argmax(sc))]
        arms["ppr_raw"].append(int(pick(raw) == gold))
        arms["ppr_debiased"].append(int(pick(debiased) == gold))
        arms["ppr_over_prior"].append(int(pick(over_prior) == gold))
        arms["ppr_integrated"].append(int(pick(integrated) == gold))
        arms["ppr_debiased_integr"].append(int(pick(deb_integr) == gold))
        sh = deb_integr[rng.permutation(len(deb_integr))]
        arms["twin_debiased_integr"].append(int(pick(sh) == gold))

        diag["n"] += 1
        diag["ppr_pick_is_dominant"] += int(pick(raw) == dom)
        if len(tn) >= 2:
            diag["ppr_act_vs_indeg"].append(float(np.corrcoef(raw, deg)[0, 1]) if deg.std() > 0 else 0.0)
            diag["ppr_act_vs_prior"].append(float(np.corrcoef(raw, pr)[0, 1]) if pr.std() > 0 else 0.0)

    def m(x):
        return round(float(np.mean(x)), 4) if len(x) else None

    def pair(a, b, seed):
        n2 = min(len(a), len(b)); return G1._paired(np.asarray(a[:n2], float), np.asarray(b[:n2], float), seed)

    res = {
        "n_test": len(test_idx), "n_scored": diag["n"],
        "diagnostic": {
            "ppr_pick_is_dominant_frac": round(diag["ppr_pick_is_dominant"] / max(1, diag["n"]), 4),
            "corr_ppr_activation_vs_indegree": round(float(np.mean(diag["ppr_act_vs_indeg"])), 4),
            "corr_ppr_activation_vs_dominant_prior": round(float(np.mean(diag["ppr_act_vs_prior"])), 4)},
        "arms": {k: m(v) for k, v in arms.items()},
        "precision_readout_ref": 0.342, "launchpad_ref": 0.313,
        "best_debias_vs_raw": pair(arms["ppr_debiased_integr"], arms["ppr_raw"], 801),
        "debias_integr_vs_twin": pair(arms["ppr_debiased_integr"], arms["twin_debiased_integr"], 802),
        "crosses_0.35": bool((m(arms["ppr_debiased_integr"]) or 0) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("PPR SIGNAL-LOSS DRILL | raw=%.4f debiased=%.4f over_prior=%.4f integrated=%.4f "
                       "debiased+integr=%.4f twin=%.4f | PPR-picks-dominant=%.3f corr(act,indeg)=%.3f "
                       "corr(act,prior)=%.3f | best-debias>raw sep=%s | crosses0.35=%s"
                       % (res["arms"]["ppr_raw"], res["arms"]["ppr_debiased"], res["arms"]["ppr_over_prior"],
                          res["arms"]["ppr_integrated"], res["arms"]["ppr_debiased_integr"],
                          res["arms"]["twin_debiased_integr"], res["diagnostic"]["ppr_pick_is_dominant_frac"],
                          res["diagnostic"]["corr_ppr_activation_vs_indegree"],
                          res["diagnostic"]["corr_ppr_activation_vs_dominant_prior"],
                          res["best_debias_vs_raw"]["sep"], res["crosses_0.35"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_ppr_signal_loss_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    a = _integrate(np.array([0.4, 0.35, 0.25]))
    assert int(np.argmax(a)) == 0 and a[0] > 0.4, "integration sharpens toward the top node: %s" % a
    print("SELFTEST PASS (integration sharpens the winner)", flush=True)
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
