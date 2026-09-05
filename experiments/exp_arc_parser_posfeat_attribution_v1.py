"""Gaps (b) + (c): attribute the speedup to the brief's actual 8-POS lever, and test the remaining
hw_dw headroom.

Four byte-identical modes, all vs the landed hdlab fast path (M0):
  M0  hdlab fast          -- baseline (scalar sentence_scores).
  M1  vec word_mode=pyloop -- BRIEF-FAITHFUL: only the 8 POS-joint + hoisted features vectorized; the
                              6 word features stay in a Python arc-loop. Isolates the POS-only lever.
  M2  vec word_mode=tables -- FULL: word features also vectorized via per-token tables (shipping).
  M2r vec word_mode=tables_rollcrc -- FULL + hw_dw built via rolling-prefix crc32 (gap c).

Reports byte-identity (vs hdlab) + interleaved-median microbench (full set + per-length-bucket). OMP
via argv (default 1). NO LLM. numpy + pure-python. Writes only its own data dir.
Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_attribution_v1.py [omp]
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

from hdlab.arc_parser import ArcParser, FeatCache, sentence_scores
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
import experiments.exp_arc_parser_posfeat_vectorize_v1 as V

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_attribution_v1")
_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_HELD = V._HELD_OUT


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


def run():
    avg = ArcParser.load(_ARC).avg
    T = V.pos_tables()
    sents = load_tagged(_HELD)
    print("OMP=%s  held-out %d sents" % (_OMP, len(sents)), flush=True)

    hd = ArcParser(avg)
    m1 = V.VecParser(avg, word_mode="pyloop")
    m2 = V.VecParser(avg, word_mode="tables")
    m2r = V.VecParser(avg, word_mode="tables_rollcrc")

    # byte-identity of each mode vs hdlab.sentence_scores (bit-exact scores)
    print("\n[byte-identity vs hdlab.sentence_scores]")
    ident = {}
    for name, wm in [("pyloop", "pyloop"), ("tables", "tables"), ("tables_rollcrc", "tables_rollcrc")]:
        Cr = FeatCache(); Cv = FeatCache()
        bad = 0
        for toks, pos in sents:
            sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
            Sr = sentence_scores(sent, avg, Cr)
            Sv = V.sentence_scores_vec(sent, avg, Cv, T, wm)
            if any(Sr[i][h] != Sv[i].get(h) for i in Sr for h in Sr[i]):
                bad += 1
        ident[wm] = (bad == 0)
        print("  %-16s bit-identical: %s (%d/%d mismatch)" % (wm, bad == 0, bad, len(sents)))

    # microbench full set (interleaved median)
    print("\n[full-set microbench, interleaved median of 9, OMP=%s]" % _OMP)
    t0 = med_time(hd.parse, sents)
    t1 = med_time(m1.parse, sents)
    t2 = med_time(m2.parse, sents)
    t2r = med_time(m2r.parse, sents)
    print("  M0 hdlab fast         : %.4fs  = 1.00x" % t0)
    print("  M1 POS-only (pyloop)  : %.4fs  = %.2fx   <- brief-faithful (8 POS feats + hoisted)" % (t1, t0 / t1))
    print("  M2 full (tables)      : %.4fs  = %.2fx   <- shipping" % (t2, t0 / t2))
    print("  M2r full + rollcrc    : %.4fs  = %.2fx   <- hw_dw rolling-crc (gap c)" % (t2r, t0 / t2r))

    # per-length-bucket (M0 vs M1 vs M2)
    buckets = [(1, 10), (11, 20), (21, 30), (31, 50), (51, 120)]
    per_bucket = []
    print("\n[per-length-bucket: M1(POS-only) and M2(full) speedup over M0]")
    for lo, hi in buckets:
        bs = [(t, p) for t, p in sents if lo <= len(t) <= hi]
        if len(bs) < 3:
            continue
        b0 = med_time(hd.parse, bs); b1 = med_time(m1.parse, bs); b2 = med_time(m2.parse, bs)
        per_bucket.append({"bucket": "%d-%d" % (lo, hi), "n": len(bs),
                           "m1_speedup": b0 / b1, "m2_speedup": b0 / b2})
        print("  %-7s n=%-4d  M1 %.2fx   M2 %.2fx" % ("%d-%d" % (lo, hi), len(bs), b0 / b1, b0 / b2))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics_omp%s.json" % _OMP), "w", encoding="utf-8") as fh:
        json.dump({"omp": _OMP, "n_sents": len(sents), "byte_identical": ident,
                   "microbench": {"m0_hdlab_s": t0, "m1_posonly_s": t1, "m2_full_s": t2, "m2_rollcrc_s": t2r,
                                  "m1_speedup": t0 / t1, "m2_speedup": t0 / t2, "m2r_speedup": t0 / t2r},
                   "per_bucket": per_bucket, "numpy": np.__version__}, fh, indent=2)
    print("\nwrote metrics_omp%s.json" % _OMP)


if __name__ == "__main__":
    run()
