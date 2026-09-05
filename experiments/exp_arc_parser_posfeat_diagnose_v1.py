"""Diagnose the microbench(2x)-vs-end-to-end(0.85x) contradiction for the vectorized POS-feature path.

The microbench says the vectorized parser is ~2x faster on this (long-sentenced) corpus, but a full
warm SituationReader.read() came back 0.85x (SLOWER). A faster parser that makes the read slower is a
regression, not a win -- this cell isolates WHY before anything is claimed:
  1. IN-READ parse-time isolation: wrap sentence_scores to accumulate ONLY the scoring wall-time (and
     call count + parsed-sentence length histogram) during a real read, for hdlab vs vec vs a
     LENGTH-GATED hybrid (vec for n>=thresh, hdlab scalar below). This says whether the parser itself
     is faster/slower in the actual (memoized, once-per-sentence) read call pattern.
  2. numpy THREADING sensitivity: many small numpy ops can be slower multi-threaded. Set via argv.
Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_diagnose_v1.py [omp_threads] [thresh]
"""
from __future__ import annotations

import os
import sys

_OMP = sys.argv[1] if len(sys.argv) > 1 else "3"
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
import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_diagnose_v1")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_READ_DOCS = ["105_persuasion_brat.conll", "113_the_secret_garden_brat.conll",
              "120_treasure_island_brat.conll"]
_THRESH = int(sys.argv[2]) if len(sys.argv) > 2 else 12


def make_timed(orig_fn, acc):
    """Wrap a sentence_scores(sent, avg, C) to accumulate scoring wall-time, count, and n-histogram."""
    def wrapped(sent, avg, C):
        t0 = time.perf_counter()
        r = orig_fn(sent, avg, C)
        acc["t"] += time.perf_counter() - t0
        acc["n"] += 1
        acc["lens"].append(len(sent))
        return r
    return wrapped


def gated_scores_factory(T, thresh):
    hd = A.sentence_scores  # the landed scalar fast path

    def gated(sent, avg, C):
        if len(sent) < thresh:
            return hd(sent, avg, C)
        return V.sentence_scores_vec(sent, avg, C, V.pos_tables())
    return gated


def run():
    from hdlab.situation_reader import SituationReader
    docpaths = [os.path.join(_CONLL, d) for d in _READ_DOCS if os.path.exists(os.path.join(_CONLL, d))]
    T = V.pos_tables()
    hd_orig = A.sentence_scores
    vec_fn = lambda sent, avg, C: V.sentence_scores_vec(sent, avg, C, V.pos_tables())
    gated_fn = gated_scores_factory(T, _THRESH)

    modes = {"hdlab": hd_orig, "vec": vec_fn, "gated@%d" % _THRESH: gated_fn}
    print("OMP=%s thresh=%d docs=%d" % (_OMP, _THRESH, len(docpaths)), flush=True)

    results = {}
    for name, fn in modes.items():
        acc = {"t": 0.0, "n": 0, "lens": []}
        A.sentence_scores = make_timed(fn, acc)
        try:
            # one warm read pass (module-cached parser persists), then two timed read passes
            for p in docpaths:
                SituationReader().read(p)
            acc["t"] = 0.0; acc["n"] = 0; acc["lens"] = []
            reps = []
            for _ in range(2):
                acc["t"] = 0.0; acc["n"] = 0; acc["lens"] = []
                t0 = time.perf_counter()
                for p in docpaths:
                    SituationReader().read(p)
                reps.append((time.perf_counter() - t0, acc["t"], acc["n"], list(acc["lens"])))
        finally:
            A.sentence_scores = hd_orig
        reps.sort(key=lambda x: x[0])
        read_t, parse_t, ncalls, lens = reps[0]  # min read as the cleanest
        results[name] = {"read_s": read_t, "parse_s": parse_t, "n_parse": ncalls,
                         "parse_share": parse_t / read_t if read_t else 0.0}
        print("  %-9s read %.3fs  parse-in-read %.3fs (%.1f%% of read, %d calls)"
              % (name, read_t, parse_t, 100 * parse_t / read_t, ncalls), flush=True)

    # length histogram of parsed sentences (from the last mode's lens)
    import collections
    hist = collections.Counter()
    for L in lens:
        b = "1-10" if L <= 10 else "11-20" if L <= 20 else "21-30" if L <= 30 else "31-50" if L <= 50 else "51+"
        hist[b] += 1
    print("  parsed-sentence lengths:", dict(sorted(hist.items())), flush=True)

    # summary deltas
    base = results["hdlab"]["parse_s"]
    print("\n  PARSE-IN-READ speedup (hdlab / mode):")
    for name in results:
        p = results[name]["parse_s"]
        print("    %-9s %.3fs  = %.2fx" % (name, p, base / p if p else 0.0))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_omp%s_t%d.json" % (_OMP, _THRESH)), "w", encoding="utf-8") as fh:
        json.dump({"omp": _OMP, "thresh": _THRESH, "results": results,
                   "length_hist": dict(hist), "numpy": np.__version__}, fh, indent=2)
    print("wrote metrics")


if __name__ == "__main__":
    run()
