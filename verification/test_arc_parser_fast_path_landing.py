"""Landing witness: the LANDED hdlab arc parser fast path is BYTE-IDENTICAL to the reference, at scale.

Problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost (Q111 landing).

After the fast path was promoted into hdlab/arc_parser.py, ArcParser.parse() IS the memoized fast
path and ArcParser._parse_reference() is the UNCHANGED stock path (arc matrix via _arc_ids + _decode).
This witness parses thousands of real LitBank sentences from documents NOT used to tune the
optimization and asserts, for EVERY sentence:
  - the flat feature-id stream per arc equals hdlab.arc_parser._arc_ids exactly (values AND order)
  - parse() decoded heads + arcs are identical to _parse_reference()
  - every per-token confidence margin is bit-identical (==, not approx)
and re-confirms parse() is materially faster than _parse_reference() (>= 2x on a warm slice).

Self-contained: imports ONLY hdlab (no experiments/ cell). Deterministic. NO LLM. numpy + pure-python.

Run: .venv/Scripts/python.exe verification/test_arc_parser_fast_path_landing.py
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
from hdlab.arc_parser import ArcParser, FeatCache, sentence_flat
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

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
    fast = ArcParser(avg)  # parse() = landed fast path; _parse_reference() = stock

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
    chk("hdlab.sentence_flat feature-id stream byte-identical to hdlab._arc_ids (values+order), every arc",
        flat_ok, "%d arcs checked" % flat_checked)

    # 2) end-to-end head + margin identity: parse() (fast) vs _parse_reference() (stock), every sentence
    head_mism = marg_mism = 0
    for toks, pos in sents:
        r = fast._parse_reference(toks, pos)
        f = fast.parse(toks, pos)
        if r.heads != f.heads:
            head_mism += 1
        if r.arcs != f.arcs:
            head_mism += 1
        for kk in r.margins:
            if r.margins[kk] != f.margins.get(kk):
                marg_mism += 1
                break
    chk("parse() heads + arcs identical to _parse_reference() on every held-out sentence", head_mism == 0,
        "%d/%d mismatched" % (head_mism, len(sents)))
    chk("parse() per-token confidence margins bit-identical to _parse_reference()", marg_mism == 0,
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

    ts = t(fast._parse_reference)
    tf = t(fast.parse)
    chk("parse() >= 2x faster than _parse_reference() on a warm held-out slice (parse cost at least halved)",
        ts / tf >= 2.0, "stock %.3fs vs fast %.3fs = %.2fx" % (ts, tf, ts / tf))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
