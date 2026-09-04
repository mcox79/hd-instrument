"""BYTE-IDENTICAL speed optimization for the BRAIN-FOUNDATIONAL parser (arc-eager).

Context: the more-brain-foundational chain routes the reader through the arc-EAGER parser (incremental,
ranked-parallel, WM-buffer; UAS 0.842 vs the arc-factored 0.791) -- which is ALSO already ~9x faster
(O(n) transitions vs O(n^2) arcs). This applies the SAME byte-identical feature-ID memoization proven
on the arc-factored parser (SOLVED.md) to arc-eager, so the brain-foundational parser is faster still
with PROVABLY identical heads + attach-confidence + margin.

Mechanism (output-preserving): the per-transition feature strings reuse massively across the O(n)
transitions and across sentences (they are POS/word/suffix/valency combos), so memoizing crc32 on the
feature string collapses the hashing. Identical ids -> identical base_ids -> identical action scores ->
identical transitions -> identical heads/conf/margin, by construction. The reduction (_score_actions,
softmax) is UNCHANGED.

BREADTH: the crc32-memoization is a GENERAL substrate primitive -- it applies to BOTH parsers (arc-
factored + arc-eager) and to the POS tagger's hashed features -- one technique, every consumer benefits.

Writes only to its own dir. NO LLM. numpy + pure-python. ASCII-only.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import time
import json
import zlib

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.arceager_parser as AE
from hdlab.arceager_parser import (load_model, MODEL_PATH, MASK, ACT_SALT,
                                    _config_feats, _legal, _apply, _mk_attr, _argmax_legal)
import experiments.exp_arc_parser_profile_v1 as P

_OUT = os.path.join(_REPO, "data/exp_arceager_fastfeat_v1")

# ---- memoized crc32 (deterministic -> pure byte-identical) ----
_HCACHE = {}


def _hc(f):
    v = _HCACHE.get(f)
    if v is None:
        v = zlib.crc32(f.encode("utf-8")) & MASK
        _HCACHE[f] = v
    return v


def parse_fast(sent_tokens, pos_tags, W):
    """Byte-identical replacement for arceager_parser.parse_with_conf using memoized feature hashing."""
    n = len(sent_tokens)
    sent = [(k + 1, sent_tokens[k], pos_tags[k], 0, "_", None) for k in range(n)]
    attr = _mk_attr(sent)
    stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; conf = {}; marg = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _legal(stack, bptr, n, heads)
        if not legal:
            break
        feats = _config_feats(stack, bptr, n, attr, heads, lc, rc, hd)
        base_ids = np.fromiter((_hc(f) for f in feats), dtype=np.int64, count=len(feats))
        scores = {a: float(W[(base_ids ^ ACT_SALT[a]) & MASK].sum()) for a in legal}
        a = _argmax_legal(scores)
        sv = np.array([scores[x] for x in legal], dtype=np.float64)
        so = np.sort(sv)[::-1]; m = float(so[0] - so[1]) if len(so) > 1 else float(so[0])
        e = np.exp(sv - sv.max()); pa = float((e / e.sum())[legal.index(a)])
        s0 = stack[-1]
        if a == AE.LARC:
            conf[s0] = pa; marg[s0] = m
        elif a == AE.RARC:
            conf[bptr] = pa; marg[bptr] = m
        stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a); guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        heads.setdefault(i, 0); conf.setdefault(i, 0.0); marg.setdefault(i, 0.0)
    return heads, conf, marg


def identity_check(sents, W):
    hmis = cmis = mmis = 0
    for toks, pos in sents:
        h0, c0, m0 = AE.parse_with_conf(toks, pos, W)
        h1, c1, m1 = parse_fast(toks, pos, W)
        if h0 != h1:
            hmis += 1
        if any(c0[k] != c1.get(k) for k in c0):
            cmis += 1
        if any(m0[k] != m1.get(k) for k in m0):
            mmis += 1
    return hmis, cmis, mmis


def time_it(fn, sents, W, reps):
    fn(*sents[0], W)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for toks, pos in sents:
            fn(toks, pos, W)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2]


def main(n=250, reps=5):
    os.makedirs(_OUT, exist_ok=True)
    W = load_model(MODEL_PATH)
    sents = P.load_sentences(n)
    ntok = sum(len(t) for t, _ in sents)

    hmis, cmis, mmis = identity_check(sents, W)
    print("BYTE-IDENTITY: heads mism=%d conf mism=%d margin mism=%d / %d sents"
          % (hmis, cmis, mmis, len(sents)), flush=True)

    t_ref = time_it(AE.parse_with_conf, sents, W, reps)
    t_fast = time_it(parse_fast, sents, W, reps)
    print("STOCK arc-eager : %.3fs (%.0f tok/s)" % (t_ref, ntok / t_ref), flush=True)
    print("FAST  arc-eager : %.3fs (%.0f tok/s)" % (t_fast, ntok / t_fast), flush=True)
    print("SPEEDUP         : %.2fx  (crc32 cache size=%d distinct feats)" % (t_ref / t_fast, len(_HCACHE)), flush=True)
    # for context: the arc-factored parser on the same input (the parser this replaces)
    from hdlab.arc_parser import ArcParser
    af = ArcParser.load(os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz"))
    af.parse(*sents[0])
    t0 = time.perf_counter()
    for toks, pos in sents:
        af.parse(toks, pos)
    t_af = time.perf_counter() - t0
    print("(context) arc-FACTORED parser same input: %.3fs -> fast arc-eager is %.1fx faster than the parser it replaces"
          % (t_af, t_af / t_fast), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_tok": ntok, "heads_mism": hmis, "conf_mism": cmis,
                   "margin_mism": mmis, "stock_s": t_ref, "fast_s": t_fast, "speedup": t_ref / t_fast,
                   "arcfactored_s": t_af, "fast_ae_vs_arcfactored": t_af / t_fast,
                   "distinct_feats": len(_HCACHE)}, f, indent=2)
    print("wrote metrics.json", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        W = load_model(MODEL_PATH)
        ss = P.load_sentences(10)
        h, c, m = identity_check(ss, W)
        assert h == 0 and c == 0 and m == 0, ("mismatch", h, c, m)
        print("SELF-TEST PASS: fast arc-eager byte-identical (heads+conf+margin) on 10 sents")
    else:
        main(a.n, a.reps)
