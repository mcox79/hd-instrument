"""BYTE-IDENTICAL fast feature-ID assembly for the arc parser -- the optimization.

Problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost.

Mechanism (all provably output-preserving):
  1. PER-TEMPLATE integer-id caches keyed on cheap tuples. The feature STRINGS reuse 26.9x
     (2.2M emitted, 82k distinct), so 96% of feature-id fetches become a dict-get on a small
     tuple key -- NO %-format, NO .encode, NO crc32. Each distinct (template,key) is hashed
     ONCE via the exact original string, so the integer id equals _h(original_string) exactly.
  2. PER-TOKEN precompute of word.lower() and suffix (O(n), was O(n^2)).
  3. PREFIX COUNTS of VERB/PUNCT so "VERB/PUNCT in between" and len(between) are O(1) -- the
     O(distance) between-scan is removed (same booleans, same bucket).
The int64 id ARRAY (same values, SAME ORDER) is handed to the UNCHANGED _decode, so heads +
margins are bit-identical by construction (we never touch the reduction or the decode).

This cell PROVES byte-identity vs the live hdlab._arc_ids on every arc of a real doc, and times
both. Writes only to its own dir. NO LLM. numpy + pure-python. ASCII-only.
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

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, SIZE, _decode
import experiments.exp_arc_parser_profile_v1 as P

_OUT = os.path.join(_REPO, "data/exp_arc_parser_fastfeat_v1")


# ---------------------------------------------------------------------------
# per-template integer-id caches (keyed on cheap tuples; value = crc32 id).
# Each miss builds the EXACT original feature string once, so id == _h(str).
# ---------------------------------------------------------------------------
def _crc(s: str) -> int:
    return zlib.crc32(s.encode("utf-8")) & (SIZE - 1)


class FeatCache:
    """Holds all per-template id caches. A fresh instance per parser keeps it deterministic and
    lets the witness reset state; module-global reuse across a doc is what makes it fast."""

    __slots__ = ("b", "hp", "dp", "hpdp", "hpdpdir", "hpdpdist", "dw", "hw", "hwdw", "hpdw",
                 "hwdp", "dpdir", "dpdist", "dsufhp", "hsufdp", "dsufdpdir", "hplhpdp",
                 "dpldpdir", "dprdp", "hprhpdp", "bV", "bP", "dpbn", "dist")

    def __init__(self):
        self.b = _crc("b")
        self.hp = {}; self.dp = {}; self.hpdp = {}; self.hpdpdir = {}; self.hpdpdist = {}
        self.dw = {}; self.hw = {}; self.hwdw = {}; self.hpdw = {}; self.hwdp = {}
        self.dpdir = {}; self.dpdist = {}; self.dsufhp = {}; self.hsufdp = {}; self.dsufdpdir = {}
        self.hplhpdp = {}; self.dpldpdir = {}; self.dprdp = {}; self.hprhpdp = {}
        self.bV = {}; self.bP = {}; self.dpbn = {}; self.dist = {}

    def dist_b(self, d):
        v = self.dist.get(d)
        if v is None:
            v = A._dist(d)
            self.dist[d] = v
        return v


def precompute_token(sent):
    """Per-token lower() + suffix + VERB/PUNCT prefix counts (1-based, len n+1)."""
    n = len(sent)
    low = [None] * (n + 1)
    suf = [None] * (n + 1)
    pv = [0] * (n + 1)   # pv[k] = #VERB in positions 1..k
    pp = [0] * (n + 1)   # pp[k] = #PUNCT in positions 1..k
    for k in range(1, n + 1):
        w = sent[k - 1][1].lower()
        low[k] = w
        suf[k] = w[-3:] if len(w) >= 3 else w
        pos = sent[k - 1][2]
        pv[k] = pv[k - 1] + (1 if pos == "VERB" else 0)
        pp[k] = pp[k - 1] + (1 if pos == "PUNCT" else 0)
    return low, suf, pv, pp


def fast_arc_ids(sent, i, h, low, suf, pv, pp, n, C: FeatCache) -> np.ndarray:
    """Byte-identical replacement for hdlab.arc_parser._arc_ids (same ids, SAME ORDER)."""
    dp = sent[i - 1][2]
    dw = low[i]
    sdw = suf[i]
    if h == 0:
        hw, hp, d, dr = "<ROOT>", "ROOT", 0, "R"
        shw = "<ROOT>" if len("<ROOT>") < 3 else "OT>"  # _suf("<ROOT>") == "OT>"
    else:
        hp = sent[h - 1][2]
        hw = low[h]
        shw = suf[h]
        d = h - i
        dr = "L" if d < 0 else "R"
    db = C.dist_b(d)

    # --- id fetch helpers (cache hit == tuple dict-get; miss builds exact string once) ---
    # 1..16 (the base block, exact original order)
    ids = [
        C.b,
        _get1(C.hp, hp, "hp:", ),
        _get1(C.dp, dp, "dp:"),
        _get2(C.hpdp, hp, dp, "hp_dp:%s_%s"),
        _get3(C.hpdpdir, hp, dp, dr, "hp_dp_dir:%s_%s_%s"),
        _get3(C.hpdpdist, hp, dp, db, "hp_dp_dist:%s_%s_%s"),
        _get1(C.dw, dw, "dw:"),
        _get1(C.hw, hw, "hw:"),
        _get2(C.hwdw, hw, dw, "hw_dw:%s_%s"),
        _get2(C.hpdw, hp, dw, "hp_dw:%s_%s"),
        _get2(C.hwdp, hw, dp, "hw_dp:%s_%s"),
        _get2(C.dpdir, dp, dr, "dp_dir:%s_%s"),
        _get2(C.dpdist, dp, db, "dp_dist:%s_%s"),
        _get2(C.dsufhp, sdw, hp, "dsuf_hp:%s_%s"),
        _get2(C.hsufdp, shw, dp, "hsuf_dp:%s_%s"),
        _get3(C.dsufdpdir, sdw, dp, dr, "dsuf_dp_dir:%s_%s_%s"),
    ]
    # 17..20 context block
    hp_l = sent[h - 2][2] if h >= 2 else "<S>"
    dp_l = sent[i - 2][2] if i >= 2 else "<S>"
    dp_r = sent[i][2] if i < n else "<E>"
    hp_r = sent[h][2] if 0 < h < n else "<E>"
    ids.append(_get3(C.hplhpdp, hp_l, hp, dp, "hpl_hp_dp:%s_%s_%s"))
    ids.append(_get3(C.dpldpdir, dp_l, dp, dr, "dpl_dp_dir:%s_%s_%s"))
    ids.append(_get2(C.dprdp, dp_r, dp, "dpr_dp:%s_%s"))
    ids.append(_get3(C.hprhpdp, hp_r, hp, dp, "hpr_hp_dp:%s_%s_%s"))
    # between block (O(1) via prefix counts; identical booleans + bucket)
    if h != 0:
        lo, hi = (i, h) if i < h else (h, i)
        nb = hi - lo - 1
        if pv[hi - 1] - pv[lo] > 0:               # "VERB" in between
            ids.append(_get2(C.bV, hp, dp, "bV:%s_%s"))
        if pp[hi - 1] - pp[lo] > 0:               # "PUNCT" in between
            ids.append(_get2(C.bP, hp, dp, "bP:%s_%s"))
        ids.append(_get2(C.dpbn, dp, C.dist_b(nb), "dp_bn:%s_%s"))
    return np.array(ids, dtype=np.int64)


def _get1(cache, k, prefix):
    v = cache.get(k)
    if v is None:
        v = _crc(prefix + k)
        cache[k] = v
    return v


def _get2(cache, a, b, tmpl):
    key = (a, b)
    v = cache.get(key)
    if v is None:
        v = _crc(tmpl % (a, b))
        cache[key] = v
    return v


def _get3(cache, a, b, c, tmpl):
    key = (a, b, c)
    v = cache.get(key)
    if v is None:
        v = _crc(tmpl % (a, b, c))
        cache[key] = v
    return v


def fast_arc_matrix(sent, C: FeatCache):
    """Drop-in for the arc[i][h] build loop in ArcParser.parse / eval_uas."""
    n = len(sent)
    low, suf, pv, pp = precompute_token(sent)
    arc = [[None] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for h in range(0, n + 1):
            if h == i:
                continue
            arc[i][h] = fast_arc_ids(sent, i, h, low, suf, pv, pp, n, C)
    return arc


class FastArcParser(ArcParser):
    def __init__(self, avg):
        super().__init__(avg)
        self._C = FeatCache()

    def parse(self, tokens, pos_tags):
        if len(tokens) != len(pos_tags):
            raise ValueError("len mismatch")
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        arc = fast_arc_matrix(sent, self._C)
        head, margin = _decode(self.avg, arc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        from hdlab.arc_parser import ParseResult
        return ParseResult(arcs=arcs, margins=margin, heads=head)


# ---------------------------------------------------------------------------
def byte_identity_check(sents):
    """For every arc of every sentence, assert fast_arc_ids == _arc_ids (values AND order)."""
    C = FeatCache()
    n_arc = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        n = len(sent)
        low, suf, pv, pp = precompute_token(sent)
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                a = A._arc_ids(sent, i, h)
                b = fast_arc_ids(sent, i, h, low, suf, pv, pp, n, C)
                if a.shape != b.shape or not np.array_equal(a, b):
                    return False, n_arc, (i, h, list(a), list(b))
                n_arc += 1
    return True, n_arc, None


def heads_identity_check(sents, avg):
    """End-to-end: heads + margins from FastArcParser must equal the stock ArcParser exactly."""
    ref = ArcParser(avg)
    fast = FastArcParser(avg)
    mism = 0
    for toks, pos in sents:
        r = ref.parse(toks, pos)
        f = fast.parse(toks, pos)
        if r.heads != f.heads:
            mism += 1
        # margins bit-identical
        for k in r.margins:
            if r.margins[k] != f.margins.get(k):
                mism += 1
                break
    return mism


def time_parse(parser, sents, reps):
    parser.parse(*sents[0])  # warm
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for toks, pos in sents:
            parser.parse(toks, pos)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2]


def main(n_sents=250, reps=3):
    os.makedirs(_OUT, exist_ok=True)
    parser = ArcParser.load(P._ARC_ASSET)
    avg = parser.avg
    sents = P.load_sentences(n_sents)
    n_arc = P.arc_count(sents)
    print("sentences=%d arcs=%d" % (len(sents), n_arc), flush=True)

    ok, checked, bad = byte_identity_check(sents)
    print("BYTE-IDENTITY (per-arc id arrays): %s  (%d arcs checked)" % (ok, checked), flush=True)
    if not ok:
        print("MISMATCH:", bad, flush=True)
        return

    mism = heads_identity_check(sents, avg)
    print("HEADS+MARGINS identity (end-to-end): mismatches=%d / %d sents" % (mism, len(sents)), flush=True)

    ref = ArcParser(avg)
    fast = FastArcParser(avg)
    t_ref = time_parse(ref, sents, reps)
    t_fast = time_parse(fast, sents, reps)
    print("STOCK parse : %.3fs  (%.0f arcs/s)" % (t_ref, n_arc / t_ref), flush=True)
    print("FAST  parse : %.3fs  (%.0f arcs/s)" % (t_fast, n_arc / t_fast), flush=True)
    print("SPEEDUP     : %.2fx  (parse-cost cut %.0f%%)" % (t_ref / t_fast, 100 * (1 - t_fast / t_ref)), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_arc": n_arc, "byte_identical_arcs": checked,
                   "heads_margin_mismatch": mism, "stock_s": t_ref, "fast_s": t_fast,
                   "speedup": t_ref / t_fast, "reps": reps}, f, indent=2)
    print("wrote", os.path.join(_OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        ss = P.load_sentences(12)
        avg = ArcParser.load(P._ARC_ASSET).avg
        ok, checked, bad = byte_identity_check(ss)
        assert ok, ("byte-identity FAIL", bad)
        assert heads_identity_check(ss, avg) == 0, "heads mismatch"
        print("SELF-TEST PASS: %d arcs byte-identical, heads+margins identical on 12 sents" % checked)
    else:
        main(a.n, a.reps)
