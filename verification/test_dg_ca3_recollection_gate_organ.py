"""Witness: the DG/CA3 recollection-gate ORGAN (hdlab/dg_ca3_recollection_gate.py).

Promotes the proven mechanism from exp_dg_ca3_recollection_gate_v1 (problem
`no_automatic_reliability_signal_reaches_the_source_oracle`, SOLVED + integrated EXCELLENT 2026-08-26)
into hdlab. Asserts the BRAIN mechanism on the ORGAN's own methods, scaffold-free (no artifact reads):
  1. DG pattern separation + CA3 completion self-test (episodes sharing generic words orthogonalise; a
     partial cue completes to the right one).
  2. On a tiny synthetic store, recollect() picks the right lemma from a distinctive cue, and its
     confidence SELF-CERTIFIES -- a matching cue completes with higher overlap than a junk cue.
The full-scale performance result (route beats the counting floor CI-separated) is witnessed separately
by verification/test_dg_ca3_recollection_self_certifies.py against the live instrument.
"""
import os
import sys

import numpy as np
from scipy import sparse

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.dg_ca3_recollection_gate import DGCA3RecollectionGate, weight_by_idf, self_test


def _presence(rows_words, V):
    r, c = [], []
    for i, ws in enumerate(rows_words):
        for w in ws:
            r.append(i)
            c.append(w)
    return sparse.csr_matrix((np.ones(len(r), np.float32), (r, c)), shape=(len(rows_words), V))


def test_mechanism_self_test():
    assert self_test() == 0
    print("PASS mechanism_self_test (DG separates, CA3 completes)")


def test_recollect_picks_right_lemma_and_self_certifies():
    V = 400
    rng = np.random.default_rng(1)
    idf = np.ones(V, np.float32) * 4.0
    generic = list(range(30))
    for j in generic:
        idf[j] = 0.2                                   # frequent words: low idf
    n_lem, per = 5, 2
    distinct = {L: [50 + 10 * L + t for t in range(4)] for L in range(n_lem)}
    ep_words, offsets = [], []
    for L in range(n_lem):
        offsets.append(len(ep_words))                  # reduceat start index for lemma L
        for _ in range(per):
            g = list(rng.choice(generic, 5, replace=False))
            ep_words.append(g + distinct[L])           # episode = generic + lemma-distinctive words
    E = weight_by_idf(_presence(ep_words, V), idf)
    org = DGCA3RecollectionGate(V, d_dg=1024, k_wta=20, seed=3).build(E, offsets)

    # a distinctive partial cue for each lemma must complete to that lemma
    cues = [[distinct[L][0], distinct[L][1], generic[0]] for L in range(n_lem)]
    Q = weight_by_idf(_presence(cues, V), idf)
    pick, conf = org.recollect(Q)
    acc = float((pick == np.arange(n_lem)).mean())
    assert acc >= 0.8, "recollect must pick the right lemma from a distinctive cue: acc=%.2f" % acc

    # self-certification: matching cues complete with higher confidence than junk (generic-only) cues
    junk = weight_by_idf(_presence([[generic[1], generic[2]] for _ in range(n_lem)], V), idf)
    _, conf_junk = org.recollect(junk)
    assert conf.mean() > conf_junk.mean(), \
        "matching cues must be more confident than junk: %.3f vs %.3f" % (conf.mean(), conf_junk.mean())

    # dual-process route: fired items use recollection, the rest fall back to the given prediction
    fallback = np.full(n_lem, -1)
    pred, fired, _ = org.route(Q, fallback, fire_fraction=0.6)
    assert fired.sum() >= 1 and np.all(pred[fired] == pick[fired])
    print("PASS recollect_and_self_certify: acc=%.2f  conf %.3f > junk %.3f" % (acc, conf.mean(), conf_junk.mean()))


if __name__ == "__main__":
    test_mechanism_self_test()
    test_recollect_picks_right_lemma_and_self_certifies()
    print("WITNESS PASS")
