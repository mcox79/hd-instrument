"""Gap (a): nail the read-level number with a CLEAN, un-confounded, higher-rep measurement at the
reader's realistic thread settings. Run this ALONE (no concurrent CPU load).

Reports, hdlab vs the length-gated vec path, over MANY reps (median + IQR + min/max):
  - PARSE-IN-READ time (reliable: wraps sentence_scores to accumulate only the scoring wall-time
    inside a real read; small signal but low variance).
  - WHOLE-READ time (noisy: the parser is only a slice of a read, so this carries the read's own GC/OS
    variance -- reported honestly with spread, not as a point estimate).
Asserts the parse-sensitive SituationModel summary is IDENTICAL. OMP via argv (default 1).
Run ALONE: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_e2e_robust_v1.py [omp] [reps]
"""
from __future__ import annotations

import os
import sys

_OMP = sys.argv[1] if len(sys.argv) > 1 else "1"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ[_v] = _OMP

import json
import statistics
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_e2e_robust_v1")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_READ_DOCS = ["105_persuasion_brat.conll", "113_the_secret_garden_brat.conll",
              "120_treasure_island_brat.conll"]
_REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 9


def _summ(sm):
    ev = [(getattr(e, "sent_idx", None), getattr(e, "predicate", None),
           getattr(e, "agent", None), getattr(e, "patient", None)) for e in (getattr(sm, "events", []) or [])]
    return {"n": len(ev), "ev": ev, "coref": round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6)}


def stats(xs):
    xs = sorted(xs)
    return {"median": statistics.median(xs), "min": xs[0], "max": xs[-1],
            "iqr_lo": xs[len(xs) // 4], "iqr_hi": xs[(3 * len(xs)) // 4]}


def run():
    from hdlab.situation_reader import SituationReader
    docpaths = [os.path.join(_CONLL, d) for d in _READ_DOCS if os.path.exists(os.path.join(_CONLL, d))]
    hd_orig = A.sentence_scores
    acc = {"t": 0.0}

    def timed(fn):
        def w(sent, avg, C):
            t0 = time.perf_counter(); r = fn(sent, avg, C); acc["t"] += time.perf_counter() - t0
            return r
        return w

    def gated(sent, avg, C):
        if len(sent) < V.GATE_THRESH:
            return hd_orig(sent, avg, C)
        return V.sentence_scores_vec(sent, avg, C, V.pos_tables())

    def measure(scorer, reps):
        A.sentence_scores = timed(scorer)
        try:
            for p in docpaths:  # warm
                SituationReader().read(p)
            reads, parses = [], []
            for _ in range(reps):
                acc["t"] = 0.0
                t0 = time.perf_counter()
                for p in docpaths:
                    SituationReader().read(p)
                reads.append(time.perf_counter() - t0)
                parses.append(acc["t"])
        finally:
            A.sentence_scores = hd_orig
        return stats(reads), stats(parses)

    # output identity (gated vs hdlab)
    base = {p: _summ(SituationReader().read(p)) for p in docpaths}
    A.sentence_scores = gated
    try:
        ident = all(_summ(SituationReader().read(p)) == base[p] for p in docpaths)
    finally:
        A.sentence_scores = hd_orig

    hd_read, hd_parse = measure(hd_orig, _REPS)
    g_read, g_parse = measure(gated, _REPS)

    print("OMP=%s reps=%d docs=%d  output_identical=%s" % (_OMP, _REPS, len(docpaths), ident), flush=True)
    print("\nPARSE-IN-READ (reliable):")
    print("  hdlab  median %.3fs  [iqr %.3f-%.3f min %.3f max %.3f]"
          % (hd_parse["median"], hd_parse["iqr_lo"], hd_parse["iqr_hi"], hd_parse["min"], hd_parse["max"]))
    print("  gated  median %.3fs  [iqr %.3f-%.3f min %.3f max %.3f]"
          % (g_parse["median"], g_parse["iqr_lo"], g_parse["iqr_hi"], g_parse["min"], g_parse["max"]))
    print("  parse-in-read speedup (median): %.2fx" % (hd_parse["median"] / g_parse["median"]))
    print("\nWHOLE-READ (noisy -- parser is a slice):")
    print("  hdlab  median %.3fs  [iqr %.3f-%.3f min %.3f max %.3f]"
          % (hd_read["median"], hd_read["iqr_lo"], hd_read["iqr_hi"], hd_read["min"], hd_read["max"]))
    print("  gated  median %.3fs  [iqr %.3f-%.3f min %.3f max %.3f]"
          % (g_read["median"], g_read["iqr_lo"], g_read["iqr_hi"], g_read["min"], g_read["max"]))
    print("  whole-read speedup (median): %.3fx  (min/min %.3fx)"
          % (hd_read["median"] / g_read["median"], hd_read["min"] / g_read["min"]))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_omp%s.json" % _OMP), "w", encoding="utf-8") as fh:
        json.dump({"omp": _OMP, "reps": _REPS, "output_identical": ident,
                   "parse_in_read": {"hdlab": hd_parse, "gated": g_parse,
                                     "speedup_median": hd_parse["median"] / g_parse["median"]},
                   "whole_read": {"hdlab": hd_read, "gated": g_read,
                                  "speedup_median": hd_read["median"] / g_read["median"]},
                   "numpy": np.__version__}, fh, indent=2)
    print("\nwrote metrics_omp%s.json" % _OMP)


if __name__ == "__main__":
    run()
