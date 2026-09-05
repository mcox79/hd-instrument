"""CLEAN single-process benchmark (no concurrent contention) to settle the read-level story and set
the length-gate threshold. Forces OMP=1 (small numpy gathers/scatters are hurt by BLAS thread-spin;
OMP=1 was measured faster for this path). Run this ALONE (nothing else competing for CPU).

  PART 1  per-length-bucket microbench, hdlab fast vs vec (interleaved median) -> the crossover point
          where vec starts winning, which sets the gate threshold (or shows none is needed at OMP=1).
  PART 2  end-to-end warm read, hdlab vs gated@THRESH, median of 5 reps, single process, asserting the
          parse-sensitive SituationModel summary is IDENTICAL. The honest read-level number.

Run ALONE: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_clean_bench_v1.py [omp] [thresh]
"""
from __future__ import annotations

import os
import sys

_OMP = sys.argv[1] if len(sys.argv) > 1 else "1"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ[_v] = _OMP

import json
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_clean_bench_v1")
_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_HELD = V._HELD_OUT
_READ_DOCS = ["105_persuasion_brat.conll", "113_the_secret_garden_brat.conll",
              "120_treasure_island_brat.conll"]
_THRESH = int(sys.argv[2]) if len(sys.argv) > 2 else 12


def load_tagged(docs, per_doc=300, maxlen=120):
    tagger = PosTagger.load(_POS)
    out = []
    for d in docs:
        p = os.path.join(_CONLL, d)
        if not os.path.exists(p):
            continue
        cnt = 0
        for toks in parse_conll_sentences(p):
            if 1 <= len(toks) <= maxlen:
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
    return xs[len(xs) // 2]


def _summ(sm):
    ev = [(getattr(e, "sent_idx", None), getattr(e, "predicate", None),
           getattr(e, "agent", None), getattr(e, "patient", None)) for e in (getattr(sm, "events", []) or [])]
    return {"n_events": len(ev), "events": ev,
            "coref_acc": round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6)}


def run():
    avg = ArcParser.load(_ARC).avg
    T = V.pos_tables()
    hd = ArcParser(avg); vp = V.VecParser(avg)
    sents = load_tagged(_HELD)
    print("OMP=%s  held-out %d sents" % (_OMP, len(sents)), flush=True)

    # PART 1: per-bucket crossover
    buckets = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 30), (31, 50), (51, 120)]
    per_bucket = []
    print("\n[1] PER-LENGTH-BUCKET (hdlab fast vs vec, interleaved median of 9):")
    for lo, hi in buckets:
        bs = [(t, p) for t, p in sents if lo <= len(t) <= hi]
        if len(bs) < 3:
            continue
        mh = med_time(hd.parse, bs); mv = med_time(vp.parse, bs)
        per_bucket.append({"bucket": "%d-%d" % (lo, hi), "n": len(bs), "hd_s": mh, "vec_s": mv,
                           "speedup": mh / mv})
        print("    %-7s n=%-4d  hd %.4fs  vec %.4fs  = %.2fx" % ("%d-%d" % (lo, hi), len(bs), mh, mv, mh / mv))

    # PART 2: clean end-to-end read, hdlab vs gated@THRESH, median of 5
    read_res = None
    try:
        from hdlab.situation_reader import SituationReader
        docpaths = [os.path.join(_CONLL, d) for d in _READ_DOCS if os.path.exists(os.path.join(_CONLL, d))]
        hd_orig = A.sentence_scores

        def gated(sent, avgw, C):
            if len(sent) < _THRESH:
                return hd_orig(sent, avgw, C)
            return V.sentence_scores_vec(sent, avgw, C, V.pos_tables())

        def read_all():
            t0 = time.perf_counter()
            for p in docpaths:
                SituationReader().read(p)
            return time.perf_counter() - t0

        base = {}
        for p in docpaths:
            base[p] = _summ(SituationReader().read(p))

        def timed(reps=5):
            read_all()  # warm
            xs = sorted(read_all() for _ in range(reps))
            return xs[len(xs) // 2], xs[0], xs[-1]

        t_hd, hlo, hhi = timed()
        A.sentence_scores = gated
        try:
            ident = all(_summ(SituationReader().read(p)) == base[p] for p in docpaths)
            t_g, glo, ghi = timed()
        finally:
            A.sentence_scores = hd_orig
        print("\n[2] END-TO-END warm read (%d docs, median of 5, OMP=%s, gate@%d):" % (len(docpaths), _OMP, _THRESH))
        print("    hdlab   : %.3fs  (min %.3f max %.3f)" % (t_hd, hlo, hhi))
        print("    gated   : %.3fs  (min %.3f max %.3f)   %.3fx   output identical: %s"
              % (t_g, glo, ghi, t_hd / t_g, ident))
        read_res = {"t_hd_s": t_hd, "t_gated_s": t_g, "read_speedup": t_hd / t_g, "output_identical": ident,
                    "hd_min": hlo, "hd_max": hhi, "gated_min": glo, "gated_max": ghi, "thresh": _THRESH}
    except Exception as e:
        print("\n[2] end-to-end skipped: %s: %s" % (type(e).__name__, e))
        read_res = {"error": "%s: %s" % (type(e).__name__, e)}

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_omp%s.json" % _OMP), "w", encoding="utf-8") as fh:
        json.dump({"omp": _OMP, "thresh": _THRESH, "per_bucket": per_bucket, "end_to_end": read_res,
                   "numpy": np.__version__}, fh, indent=2)
    print("\nwrote metrics_omp%s.json" % _OMP)


if __name__ == "__main__":
    run()
