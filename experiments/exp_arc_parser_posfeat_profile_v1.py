"""Profile the LANDED arc-parser fast path (hdlab.arc_parser) to locate the remaining warm-read cost.

Goal: reproduce first-hand, before building anything, (1) the current parse() vs _parse_reference
timing on a warm held-out slice, (2) WHERE the time goes inside sentence_flat (the POS-only dict
lookups vs the word dict lookups vs the flat-list append loop vs the numpy reduceat), and (3) the
arc-parser share of a warm read. This is the baseline the P8-named POS-feature-gather lever must beat,
BYTE-IDENTICALLY.

Feature taxonomy (from _arc_ids order), determined by reading hdlab/arc_parser.py:
  HOISTED already (computed once per token, not in the O(n^2) inner loop):
    1 b(const) 2 hp:hp 3 dp:dp 7 dw:dw 8 hw:hw 12 dp_dir 13 dp_dist 18 dpl_dp_dir 19 dpr_dp
  IN THE INNER LOOP, POS-ONLY (value depends only on closed POS tags + dir/dist/between-bucket/hasV/hasP):
    4 hp_dp   5 hp_dp_dir   6 hp_dp_dist   17 hpl_hp_dp   20 hpr_hp_dp
    bV(cond)  bP(cond)   dp_bn(cond)                         <- the ~8 POS-only joint features
  IN THE INNER LOOP, WORD (open-vocabulary; stay in Python):
    9 hw_dw  10 hp_dw  11 hw_dp  14 dsuf_hp  15 hsuf_dp  16 dsuf_dp_dir

NO LLM. numpy + pure-python. Deterministic. Writes only its own data dir.
Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_profile_v1.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import cProfile
import io
import json
import pstats
import sys
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, FeatCache, sentence_flat, precompute_token
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_profile_v1")
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


def load_tagged(docs, per_doc=250, minlen=1, maxlen=100):
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


def med_time(fn, sents, reps=7):
    fn(*sents[0])
    xs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for a, b in sents:
            fn(a, b)
        xs.append(time.perf_counter() - t0)
    xs.sort()
    return xs[len(xs) // 2]


def count_features(sents):
    """Count total feature-id emissions and split by taxonomy, to size the lever."""
    C = FeatCache()
    tot = 0
    pos_only = 0
    word = 0
    hoisted = 0
    n_arc = 0
    # feature-slot -> class, by _arc_ids order (1-based positions in the 20-block)
    HOIST = {1, 2, 3, 7, 8, 12, 13, 18, 19}
    POSJ = {4, 5, 6, 17, 20}   # + bV,bP,dp_bn conditionals
    WORD = {9, 10, 11, 14, 15, 16}
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        flat, starts, order, n = sentence_flat(sent, C)
        n_arc += len(order)
        bnd = starts + [len(flat)]
        for k, (i, h) in enumerate(order):
            seg = flat[bnd[k]:bnd[k + 1]]
            L = len(seg)
            tot += L
            # first 20 are fixed slots; remainder are conditional POS-only (bV/bP/dp_bn)
            for slot in range(1, 21):
                if slot in HOIST:
                    hoisted += 1
                elif slot in POSJ:
                    pos_only += 1
                elif slot in WORD:
                    word += 1
            pos_only += (L - 20)  # bV/bP/dp_bn are all POS-only
    return {"total_feat_emissions": tot, "n_arcs": n_arc,
            "hoisted": hoisted, "pos_only_joint": pos_only, "word": word,
            "pos_only_frac": round(pos_only / tot, 4), "word_frac": round(word / tot, 4),
            "hoisted_frac": round(hoisted / tot, 4)}


def profile_sentence_flat(sents):
    """cProfile just sentence_flat to see the internal cost split (indicative, not deployment cost)."""
    C = FeatCache()
    prepared = [[(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))] for toks, pos in sents]
    # warm the cache
    for sent in prepared:
        sentence_flat(sent, C)
    pr = cProfile.Profile()
    pr.enable()
    for _ in range(3):
        for sent in prepared:
            sentence_flat(sent, C)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(15)
    return s.getvalue()


def run():
    avg = ArcParser.load(_ARC).avg
    parser = ArcParser(avg)
    sents = load_tagged(_HELD_OUT, per_doc=250)
    n_arc = sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)
    print("held-out: %d sentences, %d arcs" % (len(sents), n_arc), flush=True)

    # 1) baseline: current fast path parse() vs stock _parse_reference
    slc = sents[:120]
    t_ref = med_time(parser._parse_reference, slc)
    t_fast = med_time(parser.parse, slc)
    print("\n[BASELINE, warm, 120-sent slice, median of 7]")
    print("  _parse_reference (stock): %.4fs" % t_ref)
    print("  parse() (landed fast):    %.4fs   (%.2fx over stock)" % (t_fast, t_ref / t_fast))

    # 2) feature taxonomy counts
    counts = count_features(sents)
    print("\n[FEATURE TAXONOMY over %d arcs, %d emissions]" % (counts["n_arcs"], counts["total_feat_emissions"]))
    print("  hoisted:        %8d (%.1f%%)" % (counts["hoisted"], 100 * counts["hoisted_frac"]))
    print("  POS-only joint: %8d (%.1f%%)  <- the lever" % (counts["pos_only_joint"], 100 * counts["pos_only_frac"]))
    print("  word:           %8d (%.1f%%)  <- stay in Python" % (counts["word"], 100 * counts["word_frac"]))

    # 3) profile sentence_flat internals
    prof = profile_sentence_flat(slc)
    print("\n[cProfile sentence_flat x3 over 120 sents (indicative internal split)]")
    print(prof)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump({"t_ref_s": t_ref, "t_fast_s": t_fast, "fast_over_stock": t_ref / t_fast,
                   "n_sents": len(sents), "n_arcs_total": n_arc, "counts": counts,
                   "numpy": np.__version__}, fh, indent=2)
    print("wrote", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    run()
