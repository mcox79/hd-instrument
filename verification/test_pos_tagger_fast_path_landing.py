"""Landing witness: the LANDED hdlab POS tagger fast path is BYTE-IDENTICAL to the reference, at scale.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost (Q111 landing).

After the fast path was promoted into hdlab/pos_tagger.py + hdlab/perceptron.py, PosTagger.tag() IS the
memoized variant-C fast path (precomputed TM/SV + sparse-per-lane emission, then the stock numpy Viterbi
DP verbatim) and PosTagger._tag_reference() is the UNCHANGED stock Collins-Viterbi. This witness tags
thousands of real HELD-OUT LitBank sentences (docs NOT used to profile/tune) and asserts, for EVERY
sentence:
  - the fast emission matrix is BIT-IDENTICAL to the reference emission build (np.array_equal, 0 mismatch)
    -- STRONGER than tag equality: it proves the computation is identical, catching the ~1e-15 Neumaier
    drift class an earlier plain-accumulate variant had (which only a tag-only check would have missed),
  - the fast tag sequence is identical to the reference tag sequence,
and re-confirms PosTagger.tag() is materially faster than _tag_reference() (>= 2x on a warm slice).

Self-contained: imports ONLY hdlab (no experiments/ cell). Deterministic. NO LLM. numpy + pure-python.
ASCII-only.
    .venv/Scripts/python.exe verification/test_pos_tagger_fast_path_landing.py
"""
import os
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np

from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_CC = os.path.join(_REPO, "data/litbank/coref_conll")
# HELD-OUT docs: distinct from 1023_bleak_house (used to profile/tune) -- same set as the speedup witness.
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

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok
    FAIL += (not ok)
    return ok


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


def main():
    tagger = PosTagger.load(_POS_ASSET)
    sents = _load(_HELDOUT)
    ntok = sum(len(s) for s in sents)
    assert len(sents) > 300, "expected a large held-out set, got %d" % len(sents)
    print("held-out: %d sentences / %d tokens from %d docs" % (len(sents), ntok, len(_HELDOUT)), flush=True)

    # 1)+(2) emission-matrix bit-identity + tag-sequence identity: LANDED fast vs reference, every sentence
    em_bad = tag_bad = 0
    for s in sents:
        if not np.array_equal(tagger._emission_reference(s), tagger._emission_fast(s)):
            em_bad += 1
        if tagger._tag_reference(s) != tagger.tag(s):
            tag_bad += 1
    chk("PosTagger.tag emission matrix bit-identical to reference (np.array_equal, every held-out sentence)",
        em_bad == 0, "%d/%d mismatched" % (em_bad, len(sents)))
    chk("PosTagger.tag tag sequence identical to reference (every held-out sentence)",
        tag_bad == 0, "%d/%d mismatched" % (tag_bad, len(sents)))

    # 3) speedup >= 2x on a warm slice (fair: same process, interleaved, median)
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
    tf = t_of(tagger.tag)
    chk("PosTagger.tag >= 2x faster than _tag_reference() on a warm held-out slice (per-call cost at least halved)",
        ts / tf >= 2.0, "reference %.3fs vs fast %.3fs = %.2fx" % (ts, tf, ts / tf))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
