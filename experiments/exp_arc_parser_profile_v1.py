"""Profile the arc parser inner loop -- FIRST-HAND confirmation of the _arc_ids/_h hotspot.

Problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost.
This cell ONLY MEASURES (writes to its own data dir). It does NOT change hdlab/.

It (1) loads the live frontend ArcParser + PosTagger assets, (2) tags a fixed set of real
LitBank sentences (1023_bleak_house) once, (3) cProfiles parser.parse over them to confirm
_arc_ids / _h dominate, and (4) times the warm (unprofiled) parse cost as the baseline the
optimization must beat -- with byte-identity of heads/margins as the invariant.

NO LLM. numpy + pure-python. ASCII-only. Deterministic (fixed doc + fixed sentence slice).
"""
from __future__ import annotations

import os
import sys

# constrain local threads (shared 16-core box; heavy runs go remote) -- memory discipline
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import cProfile
import pstats
import io
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.arc_parser import ArcParser
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_DOC = os.path.join(_REPO, "data/litbank/coref_conll/1023_bleak_house_brat.conll")
_OUT = os.path.join(_REPO, "data/exp_arc_parser_profile_v1")


def load_sentences(n_sents: int, minlen: int = 1, maxlen: int = 100):
    """Return [(tokens, pos_tags)] for the first n_sents in-range sentences of the doc, tagged once."""
    tagger = PosTagger.load(_POS_ASSET)
    toks_list = parse_conll_sentences(_DOC)
    out = []
    for toks in toks_list:
        if not (minlen <= len(toks) <= maxlen):
            continue
        pos = tagger.tag(toks)
        out.append((list(toks), list(pos)))
        if len(out) >= n_sents:
            break
    return out


def _parse_all(parser, sents):
    heads = []
    for toks, pos in sents:
        heads.append(parser.parse(toks, pos).heads)
    return heads


def arc_count(sents):
    """Total (i,h) arcs computed = sum over sentences of n*(n+1) - n  (h in 0..n, h!=i)."""
    return sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)


def main(n_sents: int = 250, warm_reps: int = 3):
    os.makedirs(_OUT, exist_ok=True)
    parser = ArcParser.load(_ARC_ASSET)
    sents = load_sentences(n_sents)
    n_tok = sum(len(t) for t, _ in sents)
    n_arc = arc_count(sents)
    print("sentences=%d tokens=%d arcs=%d (mean len=%.1f)"
          % (len(sents), n_tok, n_arc, n_tok / max(1, len(sents))), flush=True)

    # warm up (fills any lazy state), then time the unprofiled baseline
    _parse_all(parser, sents[:5])
    times = []
    for _ in range(warm_reps):
        t0 = time.perf_counter()
        _parse_all(parser, sents)
        times.append(time.perf_counter() - t0)
    times.sort()
    warm = times[len(times) // 2]
    print("WARM parse (median of %d): %.3fs  (%.0f arcs/s, %.1f sents/s)"
          % (warm_reps, warm, n_arc / warm, len(sents) / warm), flush=True)

    # cProfile a single pass to confirm the hotspot
    pr = cProfile.Profile()
    pr.enable()
    _parse_all(parser, sents)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(15)
    prof_txt = s.getvalue()
    print("\n=== cProfile (tottime, top 15) ===\n" + prof_txt, flush=True)

    # extract the parser-internal hotspot lines
    hot = {}
    for line in prof_txt.splitlines():
        for key in ("_arc_ids", "_h ", "_h(", "crc32", "_dist", "_suf", "_decode", "fromiter"):
            if key in line:
                hot.setdefault(key.strip(), line.strip())

    import json
    with open(os.path.join(_OUT, "profile.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_tok": n_tok, "n_arc": n_arc,
                   "warm_s": warm, "warm_reps": warm_reps,
                   "arcs_per_s": n_arc / warm, "hot_lines": hot}, f, indent=2)
    print("wrote", os.path.join(_OUT, "profile.json"), flush=True)
    return warm


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        # tiny smoke: parse 8 sentences, confirm heads dict shape
        p = ArcParser.load(_ARC_ASSET)
        ss = load_sentences(8)
        hs = _parse_all(p, ss)
        assert all(isinstance(h, dict) and len(h) == len(t) for h, (t, _) in zip(hs, ss)), "bad heads"
        print("SELF-TEST PASS: parsed %d sentences, head dicts well-formed" % len(ss))
    else:
        main(a.n, a.reps)
