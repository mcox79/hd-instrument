"""Witness: the fast arc parser is BYTE-IDENTICAL to the stock hdlab parser, at scale.

Problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost.

The BAR is byte-identity of parse heads + labels (+ the calibrated margin) on a HELD-OUT sentence
set. This witness parses thousands of real LitBank sentences from documents NOT used to build or
tune the optimization, and asserts, for EVERY sentence:
  - the flat feature-id stream per arc equals hdlab.arc_parser._arc_ids exactly (values AND order)
  - the decoded head map is identical
  - every per-token confidence margin is bit-identical (==, not approx)
It also re-confirms, from source, that the fast parser is materially faster (>= 2x on a warm slice).

Held-out docs (NOT the profiling/tuning doc 1023_bleak_house): persuasion, tess, secret_garden,
treasure_island, alice. Deterministic. NO LLM. numpy + pure-python.

Run: .venv/Scripts/python.exe verification/test_arc_parser_speedup_byte_identical.py
"""
import os
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_arc_parser_fastfeat_v3 import FastArcParserV3, sentence_flat
from experiments.exp_arc_parser_fastfeat_v1 import FeatCache

_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")

# held-out from the tuning doc (1023_bleak_house)
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


def load_tagged(docs, per_doc, minlen=1, maxlen=100):
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
    stock = ArcParser(avg)
    fast = FastArcParserV3(avg)

    sents = load_tagged(_HELD_OUT, per_doc=250)
    n_arc = sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)
    print("held-out: %d sentences, %d arcs, from %d docs" % (len(sents), n_arc, len(_HELD_OUT)), flush=True)

    # 1) flat feature-id stream identity vs stock _arc_ids (values + order), every arc
    C = FeatCache()
    flat_ok = True
    flat_checked = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        flat, starts, order, n = sentence_flat(sent, C)
        bnd = starts + [len(flat)]
        for k, (i, h) in enumerate(order):
            if flat[bnd[k]:bnd[k + 1]] != list(A._arc_ids(sent, i, h)):
                flat_ok = False
                break
            flat_checked += 1
        if not flat_ok:
            break
    chk("feature-id stream byte-identical to stock _arc_ids (values+order), every arc",
        flat_ok, "%d arcs checked" % flat_checked)

    # 2) end-to-end head + margin identity, every sentence.
    # NOTE: post-landing, ArcParser.parse() IS the fast path, so the byte-identity reference is
    # ArcParser._parse_reference() (the untouched stock arc-matrix + _decode body).
    head_mism = marg_mism = 0
    for toks, pos in sents:
        r = stock._parse_reference(toks, pos)
        f = fast.parse(toks, pos)
        if r.heads != f.heads:
            head_mism += 1
        if r.arcs != f.arcs:
            head_mism += 1
        for kk in r.margins:
            if r.margins[kk] != f.margins.get(kk):
                marg_mism += 1
                break
    chk("decoded heads + arcs identical on every held-out sentence", head_mism == 0,
        "%d/%d mismatched" % (head_mism, len(sents)))
    chk("per-token confidence margins bit-identical on every held-out sentence", marg_mism == 0,
        "%d/%d mismatched" % (marg_mism, len(sents)))

    # 3) speedup >= 2x on a warm slice (fair: same process, interleaved, median)
    slc = sents[:120]

    def t(fn, reps=5):
        fn(*slc[0])
        xs = []
        for _ in range(reps):
            t0 = time.perf_counter()
            for a, b in slc:
                fn(a, b)
            xs.append(time.perf_counter() - t0)
        xs.sort()
        return xs[len(xs) // 2]

    ts = t(stock._parse_reference)  # stock reference path (untouched _arc_ids + _decode)
    tf = t(fast.parse)              # landed fast path
    chk("fast parser >= 2x faster on a warm held-out slice (bar: parse cost at least halved)",
        ts / tf >= 2.0, "stock %.3fs vs fast %.3fs = %.2fx" % (ts, tf, ts / tf))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
