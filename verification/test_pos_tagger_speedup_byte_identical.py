"""WITNESS: the fast POS tagger is BYTE-IDENTICAL to the stock tagger at scale, and >=2x faster.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost.
This is the gate the strategy session runs before landing the Q111 hdlab change. It asserts, on
HELD-OUT LitBank documents (NOT the doc used to profile/tune), that the optimized tagger:
  (1) produces a BIT-IDENTICAL emission matrix for every sentence (np.array_equal, variant C),
  (2) produces an IDENTICAL tag sequence for every sentence (variant C),
  (3) is ALSO bit-identical under the conservative fallback (variant A, per-tag full-sum),
  (4) is at least 2x faster on a warm run (interleaved same-process medians).

Scaffold-free: run directly with the venv python. Writes nothing. ASCII-only.
    .venv/Scripts/python.exe verification/test_pos_tagger_speedup_byte_identical.py
"""
from __future__ import annotations

import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger, pos_features
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_pos_tagger_fastfeat_v1 import FastTagger

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_CC = os.path.join(_REPO, "data/litbank/coref_conll")
# HELD-OUT docs: distinct from 1023_bleak_house (used to profile/tune).
_HELDOUT = [
    "105_persuasion_brat.conll",
    "113_the_secret_garden_brat.conll",
    "11_alices_adventures_in_wonderland_brat.conll",
    "120_treasure_island_brat.conll",
    "1260_jane_eyre_an_autobiography_brat.conll",
    "1064_the_masque_of_the_red_death_brat.conll",
    "1155_the_secret_adversary_brat.conll",
    "110_tess_of_the_durbervilles_a_pure_woman_brat.conll",
]


def _load(docs, maxlen=100):
    out = []
    for d in docs:
        p = os.path.join(_CC, d)
        if not os.path.exists(p):
            continue
        for toks in parse_conll_sentences(p):
            if 1 <= len(toks) <= maxlen:
                out.append(list(toks))
    return out


def _stock_em(tagger, obs):
    W = tagger._perc.weights
    tags = tagger.tags
    n = len(obs)
    return np.array([[sum(W.get(f, 0.0) for f in pos_features(obs, i, tags[k]))
                      for k in range(len(tags))] for i in range(n)])


def main():
    tagger = PosTagger.load(_POS_ASSET)
    sents = _load(_HELDOUT)
    ntok = sum(len(s) for s in sents)
    assert len(sents) > 300, "expected a large held-out set, got %d" % len(sents)
    fastC = FastTagger(tagger, "C")
    fastA = FastTagger(tagger, "A")

    checks = []

    # (1)+(2) variant C: emission-matrix + tag-sequence identity, every sentence
    em_bad = tag_bad = 0
    for s in sents:
        if not np.array_equal(_stock_em(tagger, s), fastC._emission(s, len(s))):
            em_bad += 1
        if tagger._tag_reference(s) != fastC.tag(s):
            tag_bad += 1
    checks.append(("C emission-matrix bit-identical (all sents)", em_bad == 0, "%d mismatch" % em_bad))
    checks.append(("C tag-sequence identical (all sents)", tag_bad == 0, "%d mismatch" % tag_bad))

    # (3) variant A conservative fallback: also bit-identical
    emA_bad = tagA_bad = 0
    for s in sents:
        if not np.array_equal(_stock_em(tagger, s), fastA._emission(s, len(s))):
            emA_bad += 1
        if tagger._tag_reference(s) != fastA.tag(s):
            tagA_bad += 1
    checks.append(("A (fallback) emission+tags bit-identical", emA_bad == 0 and tagA_bad == 0,
                   "em=%d tag=%d" % (emA_bad, tagA_bad)))

    # (4) >=2x warm speedup (interleaved same-process medians)
    def t_of(fn, reps=5):
        fn(sents[0])
        xs = []
        for _ in range(reps):
            t0 = time.perf_counter()
            for s in sents:
                fn(s)
            xs.append(time.perf_counter() - t0)
        xs.sort()
        return xs[len(xs) // 2]
    ts = t_of(tagger._tag_reference)
    tc = t_of(fastC.tag)
    speedup = ts / tc
    checks.append(("warm speedup >= 2x", speedup >= 2.0, "%.2fx (stock %.3fs -> fast %.3fs)" % (speedup, ts, tc)))

    print("HELD-OUT: %d sentences / %d tokens from %d docs" % (len(sents), ntok, len(_HELDOUT)))
    npass = 0
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed" % (npass, len(checks)))
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
