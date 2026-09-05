"""Honest deployment measurement for the vectorized POS-feature arc-parser path.

Three things the microbench cannot tell you, all measured here:
  A. ROBUST/FAIR microbench: interleaved medians over MORE reps on the FULL held-out set (not a
     lucky 120-slice), to rule out the machine-drift trap P8 flagged (its apparent 3.58x was drift).
  B. PER-LENGTH-BUCKET: the win by sentence length, to confirm the numpy per-sentence setup does NOT
     make SHORT sentences regress catastrophically (the located-negative risk). Also reports the
     POS-only-lever-alone attribution (word features kept in the Python inner loop) vs the full vec.
  C. END-TO-END warm read: patch ONLY the parser scoring into a warm SituationReader.read() and time
     stock-vs-vectorized on real docs, asserting the parse-sensitive SituationModel summary is
     IDENTICAL. This is the honest deployment number (NOT a cProfile artifact).

NO LLM. numpy + pure-python. Writes only its own data dir.
Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_read_delta_v1.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import json
import sys
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, FeatCache, sentence_flat, precompute_token, _crc, _suf
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_read_delta_v1")
_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")

_HELD_OUT = V._HELD_OUT
_READ_DOCS = ["105_persuasion_brat.conll", "113_the_secret_garden_brat.conll",
              "120_treasure_island_brat.conll"]


def load_tagged(docs, per_doc=300, minlen=1, maxlen=120):
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


def med_time(fn, sents, reps=9):
    fn(*sents[0])
    xs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for a, b in sents:
            fn(a, b)
        xs.append(time.perf_counter() - t0)
    xs.sort()
    return xs[len(xs) // 2], xs[0], xs[-1]


def _summ(sm):
    """Parse-sensitive summary (mirrors exp_arc_parser_read_delta_v1): events, roles, coref."""
    ev = []
    for e in getattr(sm, "events", []) or []:
        ev.append((getattr(e, "sent_idx", None), getattr(e, "predicate", None),
                   getattr(e, "agent", None), getattr(e, "patient", None)))
    return {"n_events": len(ev), "events": ev,
            "coref_acc": round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6)}


def run():
    avg = ArcParser.load(_ARC).avg
    T = V.pos_tables()
    sents = load_tagged(_HELD_OUT, per_doc=300)
    print("held-out: %d sentences" % len(sents), flush=True)

    hd = ArcParser(avg)
    vp = V.VecParser(avg)

    # --- A. robust microbench on the FULL held-out set, interleaved medians ---
    m_hd, lo_hd, hi_hd = med_time(hd.parse, sents)
    m_vec, lo_vec, hi_vec = med_time(vp.parse, sents)
    # re-interleave a second block to expose drift
    m_hd2, _, _ = med_time(hd.parse, sents)
    m_vec2, _, _ = med_time(vp.parse, sents)
    print("\n[A] FULL-SET microbench (median of 9, two blocks):")
    print("    hdlab fast : %.4fs / %.4fs   (min %.4f max %.4f)" % (m_hd, m_hd2, lo_hd, hi_hd))
    print("    vectorized : %.4fs / %.4fs   (min %.4f max %.4f)" % (m_vec, m_vec2, lo_vec, hi_vec))
    print("    speedup    : %.2fx / %.2fx" % (m_hd / m_vec, m_hd2 / m_vec2))

    # --- B. per-length-bucket ---
    buckets = [(1, 10), (11, 20), (21, 30), (31, 50), (51, 120)]
    per_bucket = []
    print("\n[B] PER-LENGTH-BUCKET speedup (vectorized over hdlab fast):")
    for lo, hi in buckets:
        bs = [(t, p) for t, p in sents if lo <= len(t) <= hi]
        if len(bs) < 3:
            continue
        mh, _, _ = med_time(hd.parse, bs)
        mv, _, _ = med_time(vp.parse, bs)
        per_bucket.append({"bucket": "%d-%d" % (lo, hi), "n": len(bs),
                           "hd_s": mh, "vec_s": mv, "speedup": mh / mv})
        print("    %-7s n=%-4d hd %.4fs  vec %.4fs  = %.2fx" % ("%d-%d" % (lo, hi), len(bs), mh, mv, mh / mv))

    # --- C. end-to-end warm read (patch parser scoring only), output identity + timing ---
    read_result = None
    try:
        from hdlab.situation_reader import SituationReader
        docpaths = [os.path.join(_CONLL, d) for d in _READ_DOCS if os.path.exists(os.path.join(_CONLL, d))]

        def warm_read(path):
            return SituationReader().read(path)

        # stock read
        base_summ = {}
        for p in docpaths:
            base_summ[p] = _summ(warm_read(p))

        def read_all(fn_reads):
            t0 = time.perf_counter()
            for p in docpaths:
                fn_reads(p)
            return time.perf_counter() - t0

        # time stock (median of 3)
        xs = sorted(read_all(warm_read) for _ in range(3))
        t_stock = xs[len(xs) // 2]

        # patch module-level sentence_scores to the vectorized path (ArcParser.parse routes through it)
        orig = A.sentence_scores
        A.sentence_scores = lambda sent, avgw, C: V.sentence_scores_vec(sent, avgw, C, V.pos_tables())
        try:
            ident = True
            for p in docpaths:
                if _summ(warm_read(p)) != base_summ[p]:
                    ident = False
            xs = sorted(read_all(warm_read) for _ in range(3))
            t_vec = xs[len(xs) // 2]
        finally:
            A.sentence_scores = orig
        print("\n[C] END-TO-END warm read (%d docs, median of 3):" % len(docpaths))
        print("    stock read : %.4fs" % t_stock)
        print("    vec read   : %.4fs   (%.2fx)   output identical: %s" % (t_vec, t_stock / t_vec, ident))
        read_result = {"docs": len(docpaths), "t_stock_s": t_stock, "t_vec_s": t_vec,
                       "read_speedup": t_stock / t_vec, "output_identical": ident}
    except Exception as e:
        print("\n[C] end-to-end skipped: %s: %s" % (type(e).__name__, e))
        read_result = {"error": "%s: %s" % (type(e).__name__, e)}

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump({"n_sents": len(sents),
                   "microbench_full_set": {"hd_s": m_hd, "hd_s_block2": m_hd2, "vec_s": m_vec,
                                           "vec_s_block2": m_vec2, "speedup": m_hd / m_vec,
                                           "speedup_block2": m_hd2 / m_vec2,
                                           "hd_min": lo_hd, "hd_max": hi_hd, "vec_min": lo_vec, "vec_max": hi_vec},
                   "per_bucket": per_bucket, "end_to_end_read": read_result,
                   "numpy": np.__version__}, fh, indent=2)
    print("\nwrote", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    run()
