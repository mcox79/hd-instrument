"""Scaffold-free witness for exp_learned_graph_cls_grow_v1 (the LEARNED semantic-graph organ).

Verifies, on REAL data with can-fail assertions (not a replay):
  W1  the mechanism self-test (PPMI surprise-weighting, cross-situational + precision gates, grown-graph
      row-stochasticity, shuffle-twin, semantic_control flips a subordinate item, cooc merge).
  W2  a small growth from reading actually produces context-disambiguated PPMI edges.
  W3  EMERGENT semantic coherence (can-fail): learned edges connect WordNet-RELATED senses MORE than a
      random-endpoint twin -- i.e. the growth learns structure, not noise. This is the property the
      full-scale run reports at scale (learned path-sim > random, CI-separated).
  W4  EMERGENT frequency-dominance (can-fail): higher-frequency senses accumulate MORE learned edges
      (Rodd basin-depth ~ frequency) -- Spearman(log freq, degree) > 0 and > a shuffled-frequency null.

Fast (~1-2 min): uses the `base` graph (relations+glosses; no ConceptNet/SyntagNet) and 500 sentences.
Writes only to its OWN temp dir. Glass-box, LM-free, deterministic.
"""
import os
import sys
import tempfile

os.environ["LADDER_DATA_DIR"] = tempfile.mkdtemp(prefix="lgcg_witness_")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
from scipy.stats import spearmanr
import math

import experiments.exp_learned_graph_cls_grow_v1 as G
import experiments.exp_grounded_semantic_graph_ladder_wsd_v1 as M


def main():
    from nltk.corpus import wordnet as wn, wordnet_ic

    # W1 -- mechanism self-test
    st = G.self_test()
    assert st.get("self_test") == "PASS", st
    assert st["semantic_control_flips_subordinate"] is True
    print("W1 mechanism self-test: PASS")

    syns = M._synsets_ordered()
    s2i = {s.name(): i for i, s in enumerate(syns)}
    n = len(syns)
    ck = G._ck()
    A_base = G._base_adjacency("base", s2i, syns, n, ck)
    T = M._row_stochastic(A_base.copy())

    # W2 -- growth produces edges
    sents = G._corpus_sentences(G.SIMPLEWIKI, 500)
    assert len(sents) >= 100, "need the simplewiki corpus present"
    cooc, supp, marg = G._accumulate(sents, wn, s2i, T, n, "ctx")
    rr, cc, ww, estat = G._ppmi_edges(cooc, supp, marg, "ppmi", A_base, schema_gate=True)
    assert len(rr) > 0, "growth must produce context-disambiguated PPMI edges"
    print("W2 growth produced %d edges (%s): PASS" % (len(rr), estat))

    def psim(a, b):
        try:
            v = wn.synset(syns[int(a)].name()).path_similarity(wn.synset(syns[int(b)].name()))
            return float(v) if v is not None else 0.0
        except Exception:
            return 0.0

    # W3 -- emergent semantic coherence (learned endpoints more related than random)
    m = min(500, len(rr))
    rng = np.random.default_rng(0)
    nodes = np.array(sorted(set(rr + cc)))
    learned = float(np.mean([psim(rr[k], cc[k]) for k in range(m)]))
    rand = float(np.mean([psim(int(rng.choice(nodes)), int(rng.choice(nodes))) for _ in range(m)]))
    assert learned > rand, "learned edges must connect more-related senses than random (structure, not noise)"
    print("W3 semantic coherence: learned %.4f > random %.4f: PASS" % (learned, rand))

    # W4 -- emergent frequency-dominance (freq ~ degree), > shuffled null
    deg = {}
    for i, j in zip(rr, cc):
        deg[i] = deg.get(i, 0.0) + 1.0
        deg[j] = deg.get(j, 0.0) + 1.0
    ic = wordnet_ic.ic("ic-semcor.dat")
    fr, dg = [], []
    for idx, d in deg.items():
        s = wn.synset(syns[idx].name())
        if s.pos() not in ("n", "v"):
            continue
        fr.append(math.log1p(float(ic[s.pos()].get(s.offset(), 0.0))))
        dg.append(d)
    fr = np.array(fr); dg = np.array(dg)
    rho, p = spearmanr(fr, dg)
    perm = np.random.default_rng(7).permutation(len(fr))
    rho_null, _ = spearmanr(fr[perm], dg)
    assert rho > 0 and rho > abs(rho_null), "frequency-dominance must emerge (freq correlates with learned degree)"
    print("W4 frequency-dominance: rho=%.3f > null=%.3f: PASS" % (rho, rho_null))

    print("ALL WITNESS CHECKS PASSED (4/4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
