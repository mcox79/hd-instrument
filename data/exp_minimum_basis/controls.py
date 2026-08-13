"""ANALYSIS-ONLY controls for the minimum-basis derivation (2026-08-13).

C1  Frequency-matched control: is the basis more concrete/earlier than corpus lemmas OF THE SAME
    CORPUS FREQUENCY, or is the apparent effect just a frequency effect?
C2  Topology-only control: how much of the greedy basis is just the top-out-degree nodes?
C3  Provenance spot-check on suspicious members.
Writes only under data/exp_minimum_basis/.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import random
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUT = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, OUT)
from build_basis import (build_graph, load_aoa, load_concreteness, load_lancaster, mwu, desc,
                         corpus_vocab, lem)
from hdlab.closed_class_lexicon import is_eligible_meaning

import numpy as np


def main():
    freq, _ = corpus_vocab()
    elig = sorted(w for w in freq if is_eligible_meaning(w))
    rows = json.load(open(os.path.join(OUT, "basis_top200.json"), encoding="utf-8"))
    basis = sorted({r["lemma"] for r in rows})
    eall, nall, _ = build_graph({"v5", "v62", "v4", "v3"})

    norms = {"conc": load_concreteness(), "aoa": load_aoa(), "sm": load_lancaster()}
    out = {}

    # ---- C1 frequency-matched control (log-freq stratified, 20 draws, seed 20260813)
    lf = {w: np.log10(freq[w] + 1) for w in elig}
    bins = {}
    for w in elig:
        bins.setdefault(round(lf[w], 1), []).append(w)
    bins = {k: sorted(v) for k, v in sorted(bins.items())}
    rng = random.Random(20260813)
    matched_draws = []
    for _ in range(20):
        draw = []
        for w in basis:
            b = round(lf.get(w, 0.0), 1)
            pool = [x for x in bins.get(b, []) if x not in set(basis)]
            if pool:
                draw.append(rng.choice(pool))
        matched_draws.append(sorted(set(draw)))
    c1 = {}
    for nm, tbl in norms.items():
        bv = [tbl[w] for w in basis if w in tbl]
        ps, rbcs, meds = [], [], []
        for d in matched_draws:
            mv = [tbl[w] for w in d if w in tbl]
            t = mwu(bv, mv)
            if "p_two_sided" in t:
                ps.append(t["p_two_sided"]); rbcs.append(t["rank_biserial_a_vs_b"])
                meds.append(float(np.median(mv)))
        c1[nm] = {"basis": desc(bv),
                  "matched_median_of_medians": round(float(np.median(meds)), 4) if meds else None,
                  "median_p": float(np.median(ps)) if ps else None,
                  "median_rank_biserial": round(float(np.median(rbcs)), 4) if rbcs else None,
                  "n_draws_p_lt_.05": int(sum(1 for p in ps if p < 0.05)),
                  "n_draws": len(ps)}
    out["C1_frequency_matched"] = c1
    out["C1_note"] = ("basis vs corpus lemmas matched on log10(corpus freq) to 0.1 dex; "
                      "20 independent draws, seed 20260813; median across draws reported")

    # ---- C2 topology-only overlap
    hub = sorted(eall, key=lambda x: (-len(eall[x]), x))
    for n in (50, 100, 200):
        h = set(hub[:n]); b = set([r["lemma"] for r in rows][:n])
        out.setdefault("C2_hub_overlap", {})["top%d" % n] = {
            "intersection": len(h & b), "jaccard": round(len(h & b) / len(h | b), 4)}
    # rank correlation of greedy gain vs out-degree
    from scipy.stats import spearmanr
    g = [r["gain"] for r in rows]; d = [len(eall.get(r["lemma"], ())) for r in rows]
    rho, p = spearmanr(g, d)
    out["C2_gain_vs_outdegree_spearman"] = {"rho": round(float(rho), 4), "p": float(p), "n": len(g)}

    # ---- C3 provenance spot-check on odd members
    susp = ["joy", "congratulations", "canada", "director", "company", "gnetophytes", "process"]
    ev = {}
    for w in susp:
        ev[w] = {"outdeg": len(eall.get(w, ())), "corpus_freq": freq.get(w, 0),
                 "children_sample": sorted(eall.get(w, ()))[:15]}
    out["C3_spotcheck"] = ev

    # ---- degree distribution of the graph (is it star-shaped?)
    degs = sorted((len(v) for v in eall.values()), reverse=True)
    out["graph_outdegree"] = {"n_source_nodes": len(degs), "max": degs[0],
                              "top10": degs[:10],
                              "n_deg1": int(sum(1 for x in degs if x == 1)),
                              "frac_edges_from_top20_sources":
                                  round(sum(degs[:20]) / sum(degs), 4)}
    # in-degree: how many nodes have NO incoming definitional edge (unreachable, need anchoring)
    has_in = {s for v in eall.values() for s in v}
    out["graph_indegree"] = {"n_nodes": len(nall), "n_with_incoming_edge": len(has_in),
                             "n_source_only_unreachable": len(set(nall) - has_in)}

    with open(os.path.join(OUT, "controls.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
