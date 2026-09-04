"""BYTE-IDENTICAL fast arc parser v2 -- inlined caches + BATCHED segmented scoring.

Builds on v1 (per-template id caches, per-token precompute, prefix VERB/PUNCT). v2 adds the two
remaining wins the v1 profile exposed:
  A. INLINE the per-feature cache lookups (v1 spent ~0.9s in _get1/2/3 function-call overhead over
     2.2M calls). No helper calls; the cache dicts are bound to locals.
  B. BATCH the scoring. v1 did 98k np.array + 98k avg[ids].sum() calls. v2 concatenates every arc's
     feature-ids for a sentence into ONE flat array, gathers the weights once, and reduces all arc
     scores in ONE np.add.reduceat. VERIFIED bit-identical to per-arc .sum() (max abs diff 0.0 on
     98,168 arcs) -- reduceat reduces each contiguous segment with the same pairwise algorithm as a
     stand-alone .sum(), so the score matrix is bit-identical and _decode's output is unchanged.

decode_from_scores replicates hdlab._decode EXACTLY, reading the precomputed score matrix instead
of recomputing avg[arc].sum(). Heads + margins are therefore bit-identical by construction.

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

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, SIZE, ParseResult
import experiments.exp_arc_parser_profile_v1 as P
from experiments.exp_arc_parser_fastfeat_v1 import FeatCache, precompute_token

_OUT = os.path.join(_REPO, "data/exp_arc_parser_fastfeat_v2")
_MASK = SIZE - 1


def _crc(s: str) -> int:
    return zlib.crc32(s.encode("utf-8")) & _MASK


def sentence_scores(sent, avg, C: FeatCache):
    """Return Sc: dict i -> dict h -> float score, bit-identical to float(avg[_arc_ids(sent,i,h)].sum()).

    Builds every arc's feature-ids inline into one flat list, then batches gather + segmented sum.
    """
    n = len(sent)
    low, suf, pv, pp = precompute_token(sent)
    pos = [None] + [sent[k - 1][2] for k in range(1, n + 1)]  # 1-based POS

    # bind caches to locals (kills attribute lookups in the hot loop)
    b_id = C.b
    c_hp = C.hp; c_dp = C.dp; c_hpdp = C.hpdp; c_hpdpdir = C.hpdpdir; c_hpdpdist = C.hpdpdist
    c_dw = C.dw; c_hw = C.hw; c_hwdw = C.hwdw; c_hpdw = C.hpdw; c_hwdp = C.hwdp
    c_dpdir = C.dpdir; c_dpdist = C.dpdist; c_dsufhp = C.dsufhp; c_hsufdp = C.hsufdp; c_dsufdpdir = C.dsufdpdir
    c_hplhpdp = C.hplhpdp; c_dpldpdir = C.dpldpdir; c_dprdp = C.dprdp; c_hprhpdp = C.hprhpdp
    c_bV = C.bV; c_bP = C.bP; c_dpbn = C.dpbn; c_dist = C.dist

    def dist_b(d):
        v = c_dist.get(d)
        if v is None:
            v = A._dist(d); c_dist[d] = v
        return v

    flat = []
    ap = flat.append
    ext = flat.extend
    starts = []
    order = []  # (i,h) in the exact iteration order

    for i in range(1, n + 1):
        dp = pos[i]; dw = low[i]; sdw = suf[i]
        dp_l = pos[i - 1] if i >= 2 else "<S>"
        dp_r = pos[i + 1] if i < n else "<E>"
        for h in range(0, n + 1):
            if h == i:
                continue
            starts.append(len(flat))
            order.append((i, h))
            if h == 0:
                hw = "<ROOT>"; hp = "ROOT"; d = 0; dr = "R"; shw = "OT>"
            else:
                hp = pos[h]; hw = low[h]; shw = suf[h]
                d = h - i; dr = "L" if d < 0 else "R"
            db = dist_b(d)

            # feat 1 b
            ap(b_id)
            # 2 hp:
            v = c_hp.get(hp)
            if v is None: v = _crc("hp:" + hp); c_hp[hp] = v
            ap(v)
            # 3 dp:
            v = c_dp.get(dp)
            if v is None: v = _crc("dp:" + dp); c_dp[dp] = v
            ap(v)
            # 4 hp_dp
            k = (hp, dp); v = c_hpdp.get(k)
            if v is None: v = _crc("hp_dp:%s_%s" % k); c_hpdp[k] = v
            ap(v)
            # 5 hp_dp_dir
            k = (hp, dp, dr); v = c_hpdpdir.get(k)
            if v is None: v = _crc("hp_dp_dir:%s_%s_%s" % k); c_hpdpdir[k] = v
            ap(v)
            # 6 hp_dp_dist
            k = (hp, dp, db); v = c_hpdpdist.get(k)
            if v is None: v = _crc("hp_dp_dist:%s_%s_%s" % k); c_hpdpdist[k] = v
            ap(v)
            # 7 dw:
            v = c_dw.get(dw)
            if v is None: v = _crc("dw:" + dw); c_dw[dw] = v
            ap(v)
            # 8 hw:
            v = c_hw.get(hw)
            if v is None: v = _crc("hw:" + hw); c_hw[hw] = v
            ap(v)
            # 9 hw_dw
            k = (hw, dw); v = c_hwdw.get(k)
            if v is None: v = _crc("hw_dw:%s_%s" % k); c_hwdw[k] = v
            ap(v)
            # 10 hp_dw
            k = (hp, dw); v = c_hpdw.get(k)
            if v is None: v = _crc("hp_dw:%s_%s" % k); c_hpdw[k] = v
            ap(v)
            # 11 hw_dp
            k = (hw, dp); v = c_hwdp.get(k)
            if v is None: v = _crc("hw_dp:%s_%s" % k); c_hwdp[k] = v
            ap(v)
            # 12 dp_dir
            k = (dp, dr); v = c_dpdir.get(k)
            if v is None: v = _crc("dp_dir:%s_%s" % k); c_dpdir[k] = v
            ap(v)
            # 13 dp_dist
            k = (dp, db); v = c_dpdist.get(k)
            if v is None: v = _crc("dp_dist:%s_%s" % k); c_dpdist[k] = v
            ap(v)
            # 14 dsuf_hp
            k = (sdw, hp); v = c_dsufhp.get(k)
            if v is None: v = _crc("dsuf_hp:%s_%s" % k); c_dsufhp[k] = v
            ap(v)
            # 15 hsuf_dp
            k = (shw, dp); v = c_hsufdp.get(k)
            if v is None: v = _crc("hsuf_dp:%s_%s" % k); c_hsufdp[k] = v
            ap(v)
            # 16 dsuf_dp_dir
            k = (sdw, dp, dr); v = c_dsufdpdir.get(k)
            if v is None: v = _crc("dsuf_dp_dir:%s_%s_%s" % k); c_dsufdpdir[k] = v
            ap(v)
            # 17 hpl_hp_dp
            hp_l = pos[h - 1] if h >= 2 else "<S>"
            k = (hp_l, hp, dp); v = c_hplhpdp.get(k)
            if v is None: v = _crc("hpl_hp_dp:%s_%s_%s" % k); c_hplhpdp[k] = v
            ap(v)
            # 18 dpl_dp_dir
            k = (dp_l, dp, dr); v = c_dpldpdir.get(k)
            if v is None: v = _crc("dpl_dp_dir:%s_%s_%s" % k); c_dpldpdir[k] = v
            ap(v)
            # 19 dpr_dp
            k = (dp_r, dp); v = c_dprdp.get(k)
            if v is None: v = _crc("dpr_dp:%s_%s" % k); c_dprdp[k] = v
            ap(v)
            # 20 hpr_hp_dp
            hp_r = pos[h + 1] if 0 < h < n else "<E>"
            k = (hp_r, hp, dp); v = c_hprhpdp.get(k)
            if v is None: v = _crc("hpr_hp_dp:%s_%s_%s" % k); c_hprhpdp[k] = v
            ap(v)
            # between block
            if h != 0:
                lo, hi = (i, h) if i < h else (h, i)
                nb = hi - lo - 1
                if pv[hi - 1] - pv[lo] > 0:
                    k = (hp, dp); v = c_bV.get(k)
                    if v is None: v = _crc("bV:%s_%s" % k); c_bV[k] = v
                    ap(v)
                if pp[hi - 1] - pp[lo] > 0:
                    k = (hp, dp); v = c_bP.get(k)
                    if v is None: v = _crc("bP:%s_%s" % k); c_bP[k] = v
                    ap(v)
                k = (dp, dist_b(nb)); v = c_dpbn.get(k)
                if v is None: v = _crc("dp_bn:%s_%s" % k); c_dpbn[k] = v
                ap(v)

    ids = np.asarray(flat, dtype=np.int64)
    gathered = avg[ids]
    starts_arr = np.asarray(starts, dtype=np.intp)
    scores = np.add.reduceat(gathered, starts_arr)  # one score per arc, arc order
    # scatter into Sc[i][h]
    Sc = {i: {} for i in range(1, n + 1)}
    for idx, (i, h) in enumerate(order):
        Sc[i][h] = float(scores[idx])
    return Sc


def decode_from_scores(Sc, n):
    """EXACT replica of hdlab.arc_parser._decode, reading Sc[i][h] instead of avg[arc].sum()."""
    S = {}
    head = {}
    margin = {}
    for i in range(1, n + 1):
        cand = []
        sci = Sc[i]
        for h in range(0, n + 1):
            if h == i:
                continue
            cand.append((sci[h], h))
        cand.sort(reverse=True)
        head[i] = cand[0][1]
        S[i] = {h: sc for sc, h in cand}
        margin[i] = cand[0][0] - (cand[1][0] if len(cand) > 1 else cand[0][0])
    for _ in range(n + 2):
        cyc = None
        for start in range(1, n + 1):
            seen = []
            x = start
            while x != 0 and x not in seen:
                seen.append(x)
                x = head[x]
            if x != 0:
                j = seen.index(x)
                cyc = seen[j:]
                break
        if cyc is None:
            break
        best_node = None
        best_alt = None
        best_loss = 1e18
        cset = set(cyc)
        for node in cyc:
            cur = S[node][head[node]]
            alt_h = -1
            alt_s = -1e18
            for h, sc in S[node].items():
                if h not in cset and sc > alt_s:
                    alt_s = sc
                    alt_h = h
            if alt_h >= 0 and (cur - alt_s) < best_loss:
                best_loss = cur - alt_s
                best_node = node
                best_alt = alt_h
        if best_node is None:
            break
        head[best_node] = best_alt
    return head, margin


class FastArcParserV2(ArcParser):
    def __init__(self, avg):
        super().__init__(avg)
        self._C = FeatCache()

    def parse(self, tokens, pos_tags):
        if len(tokens) != len(pos_tags):
            raise ValueError("len mismatch")
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        Sc = sentence_scores(sent, self.avg, self._C)
        head, margin = decode_from_scores(Sc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margin, heads=head)


def heads_identity_check(sents, avg):
    ref = ArcParser(avg)
    fast = FastArcParserV2(avg)
    mism = 0
    marg_mism = 0
    for toks, pos in sents:
        r = ref.parse(toks, pos)
        f = fast.parse(toks, pos)
        if r.heads != f.heads:
            mism += 1
        for k in r.margins:
            if r.margins[k] != f.margins.get(k):
                marg_mism += 1
                break
    return mism, marg_mism


def time_parse(parser, sents, reps):
    parser.parse(*sents[0])
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for toks, pos in sents:
            parser.parse(toks, pos)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2]


def main(n_sents=250, reps=5):
    os.makedirs(_OUT, exist_ok=True)
    avg = ArcParser.load(P._ARC_ASSET).avg
    sents = P.load_sentences(n_sents)
    n_arc = P.arc_count(sents)
    print("sentences=%d arcs=%d" % (len(sents), n_arc), flush=True)

    mism, marg = heads_identity_check(sents, avg)
    print("HEADS identity mismatches=%d  MARGIN mismatches=%d  / %d sents" % (mism, marg, len(sents)), flush=True)

    ref = ArcParser(avg)
    fast = FastArcParserV2(avg)
    t_ref = time_parse(ref, sents, reps)
    t_fast = time_parse(fast, sents, reps)
    print("STOCK parse : %.3fs  (%.0f arcs/s)" % (t_ref, n_arc / t_ref), flush=True)
    print("FAST2 parse : %.3fs  (%.0f arcs/s)" % (t_fast, n_arc / t_fast), flush=True)
    print("SPEEDUP     : %.2fx  (parse-cost cut %.0f%%)" % (t_ref / t_fast, 100 * (1 - t_fast / t_ref)), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_arc": n_arc, "heads_mismatch": mism,
                   "margin_mismatch": marg, "stock_s": t_ref, "fast_s": t_fast,
                   "speedup": t_ref / t_fast, "reps": reps}, f, indent=2)
    print("wrote", os.path.join(_OUT, "metrics.json"), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        ss = P.load_sentences(12)
        avg = ArcParser.load(P._ARC_ASSET).avg
        m, mm = heads_identity_check(ss, avg)
        assert m == 0 and mm == 0, ("mismatch", m, mm)
        print("SELF-TEST PASS: heads+margins identical on 12 sents (batched reduceat scoring)")
    else:
        main(a.n, a.reps)
