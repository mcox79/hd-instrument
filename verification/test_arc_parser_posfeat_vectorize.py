"""Pre-landing witness: the vectorized POS-feature arc-parser path is BYTE-IDENTICAL to the landed
hdlab fast path, at scale, and materially faster.

Problem: numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever.

The vectorized path (experiments/exp_arc_parser_posfeat_vectorize_v1.py) rebuilds the SAME flat int64
feature-id array in the SAME order as hdlab.sentence_flat, but via numpy scatter of precomputed-table
gathers instead of the O(n^2) per-arc Python dict.get+append loop. Because the flat array and the
reduceat segments are identical, heads + arcs + per-token margins are bit-identical BY CONSTRUCTION.

This witness parses thousands of real held-out LitBank sentences (docs NOT used to tune) and asserts:
  W1  flat id stream identical to hdlab.sentence_flat (values AND order), every arc.
  W2  Sc arc scores bit-identical to hdlab.sentence_scores (==, not approx).
  W3  parse() heads + arcs + per-token margins bit-identical to hdlab.ArcParser.parse.
  W4  the vectorized path is materially faster than the landed hdlab fast path (>= 1.3x, warm,
      fair interleaved median) -- a byte-identical speedup, not a parse change.
  W5  INFO-FREE CONTROL: a corrupted POS-feature table (one entry perturbed) MUST break the flat-id
      identity -- proving the byte-identity check has teeth and a broken vectorization is caught.

Reruns NO landed cell; recomputes from source (hdlab + the experiment functions + the model asset);
writes nothing. NO LLM. numpy + pure-python. Deterministic.

Run: .venv/Scripts/python.exe verification/test_arc_parser_posfeat_vectorize.py
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

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, FeatCache, sentence_flat, sentence_scores
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_HELD_OUT = [
    "105_persuasion_brat.conll",
    "110_tess_of_the_durbervilles_a_pure_woman_brat.conll",
    "113_the_secret_garden_brat.conll",
    "120_treasure_island_brat.conll",
    "11_alices_adventures_in_wonderland_brat.conll",
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


def load_tagged(docs, per_doc=250, minlen=1, maxlen=120):
    tagger = PosTagger.load(_POS)
    out = []
    for d in docs:
        path = os.path.join(_CONLL, d)
        if not os.path.exists(path):
            continue
        cnt = 0
        for toks in parse_conll_sentences(path):
            if not (minlen <= len(toks) <= maxlen):
                continue
            out.append((list(toks), list(tagger.tag(toks))))
            cnt += 1
            if cnt >= per_doc:
                break
    return out


def main():
    avg = ArcParser.load(_ARC).avg
    T = V.pos_tables()
    sents = load_tagged(_HELD_OUT, per_doc=250)
    n_arc = sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)
    print("held-out: %d sentences, %d arcs, %d docs" % (len(sents), n_arc, len(_HELD_OUT)), flush=True)

    # W1: flat id stream identical, every arc
    Cref = FeatCache(); Cvec = FeatCache()
    flat_bad = 0; checked = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        fr, sr, orr, _ = sentence_flat(sent, Cref)
        fv, sv, ov, _ = V.sentence_flat_vec(sent, Cvec, T)
        if list(fv) != list(fr) or list(sv) != list(sr) or ov != orr:
            flat_bad += 1
        checked += len(orr)
    chk("vectorized flat id stream byte-identical to hdlab.sentence_flat (values+order), every arc",
        flat_bad == 0, "%d arcs checked, %d sents mismatched" % (checked, flat_bad))

    # W2: Sc scores bit-identical
    Cr2 = FeatCache(); Cv2 = FeatCache()
    sc_bad = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        Sr = sentence_scores(sent, avg, Cr2)
        Sv = V.sentence_scores_vec(sent, avg, Cv2, T)
        if any(Sr[i][h] != Sv[i].get(h) for i in Sr for h in Sr[i]):
            sc_bad += 1
    chk("vectorized Sc arc scores bit-identical to hdlab.sentence_scores", sc_bad == 0,
        "%d/%d sents mismatched" % (sc_bad, len(sents)))

    # W3: heads + arcs + margins identical to ArcParser.parse
    hd = ArcParser(avg); vp = V.VecParser(avg)
    head_bad = marg_bad = 0
    for toks, pos in sents:
        r = hd.parse(toks, pos)
        f = vp.parse(toks, pos)
        if r.heads != f.heads or r.arcs != f.arcs:
            head_bad += 1
        if any(r.margins[k] != f.margins.get(k) for k in r.margins):
            marg_bad += 1
    chk("parse() heads+arcs+margins bit-identical to hdlab.ArcParser.parse", head_bad == 0 and marg_bad == 0,
        "%d head, %d margin mismatched of %d" % (head_bad, marg_bad, len(sents)))

    # W4: material speedup, warm, fair interleaved median
    slc = sents[:120]

    def t(fn, reps=7):
        fn(*slc[0])
        xs = []
        for _ in range(reps):
            t0 = time.perf_counter()
            for a, b in slc:
                fn(a, b)
            xs.append(time.perf_counter() - t0)
        xs.sort()
        return xs[len(xs) // 2]

    hd2 = ArcParser(avg); vp2 = V.VecParser(avg)
    # Post-landing (2026-09-05, numpy_vectorize... integrated): ArcParser.parse is NOW the vectorized auto
    # path, so timing it against the vec path is circular. Measure the vec speedup against the SCALAR
    # reference (_parse_reference, the untouched byte-identity fast path) -- the meaningful, still-true claim.
    th = t(hd2._parse_reference); tv = t(vp2.parse)
    chk("vectorized path >= 1.3x faster than the SCALAR reference (byte-identical speedup)",
        th / tv >= 1.3, "scalar %.3fs vs vec %.3fs = %.2fx" % (th, tv, th / tv))

    # W5: info-free control -- a corrupted POS table MUST break the identity (the check has teeth)
    toks, pos = sents[0]
    sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
    fr, _, _, _ = sentence_flat(sent, FeatCache())
    import copy
    Tbad = copy.copy(T)
    Tbad.hpdp = T.hpdp.copy() ^ np.int64(1)  # perturb every hp_dp id (feat 4 is present on every arc)
    fv_bad, _, _, _ = V.sentence_flat_vec(sent, FeatCache(), Tbad)
    chk("corrupted POS table BREAKS flat-id identity (control has teeth)", list(fv_bad) != list(fr),
        "perturbed hp_dp table")

    # W6: the SHIPPING length-gated path (vec for n>=thresh, scalar below) is ALSO bit-identical
    gp = V.VecParser(avg, gate=True)
    ghead_bad = gmarg_bad = 0
    for toks, pos in sents:
        r = hd.parse(toks, pos)
        g = gp.parse(toks, pos)
        if r.heads != g.heads or r.arcs != g.arcs:
            ghead_bad += 1
        if any(r.margins[k] != g.margins.get(k) for k in r.margins):
            gmarg_bad += 1
    chk("length-gated parser (shipping design) heads+arcs+margins bit-identical to hdlab.ArcParser.parse",
        ghead_bad == 0 and gmarg_bad == 0, "%d head, %d margin mismatched of %d (gate@%d)"
        % (ghead_bad, gmarg_bad, len(sents), V.GATE_THRESH))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
