"""BYTE-IDENTICAL fast arc parser v3 -- hoist token-local feature IDs out of the O(n^2) loop.

Builds on v2 (inlined caches + batched reduceat scoring). v3 attacks the remaining pure-Python
inner-loop cost (v2 profile: 2.29M dict.get + 2.5M append) by computing the feature IDs that do
NOT depend on the (dependent, head) PAIR just once per token, then placing them by position:

  - head-local  : "hp:"+hp (feat 2), "hw:"+hw (feat 8)           -> hp_id[h], hw_id[h], once per head
  - dep-local   : "dp:"+dp (3), "dw:"+dw (7), "dpr_dp:.." (19)   -> once per dependent i
  - dir/dist-local (dep-side): dp_dir (12), dp_dist (13), dpl_dp_dir (18) depend only on i plus the
    direction L/R or distance bucket, so a tiny per-i map indexed by dr/db replaces a tuple+cache-get

The ~8 hoisted features leave 14 genuinely (i,h)-joint features in the inner loop. IDs and ORDER
are unchanged, so the flat id stream per arc is byte-identical to hdlab._arc_ids and the batched
reduceat scores + decode are bit-identical.

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

_OUT = os.path.join(_REPO, "data/exp_arc_parser_fastfeat_v3")
_MASK = SIZE - 1
_BUCKETS = ("1", "2", "3-5", "6-10", "11+")


def _crc(s: str) -> int:
    return zlib.crc32(s.encode("utf-8")) & _MASK


def sentence_flat(sent, C: FeatCache):
    """Build (flat_ids list, starts list, order list) for every arc, IDs in exact _arc_ids order."""
    n = len(sent)
    low, suf, pv, pp = precompute_token(sent)
    pos = [None] + [sent[k - 1][2] for k in range(1, n + 1)]

    c_hp = C.hp; c_dp = C.dp; c_hpdp = C.hpdp; c_hpdpdir = C.hpdpdir; c_hpdpdist = C.hpdpdist
    c_dw = C.dw; c_hw = C.hw; c_hwdw = C.hwdw; c_hpdw = C.hpdw; c_hwdp = C.hwdp
    c_dpdir = C.dpdir; c_dpdist = C.dpdist; c_dsufhp = C.dsufhp; c_hsufdp = C.hsufdp; c_dsufdpdir = C.dsufdpdir
    c_hplhpdp = C.hplhpdp; c_dpldpdir = C.dpldpdir; c_dprdp = C.dprdp; c_hprhpdp = C.hprhpdp
    c_bV = C.bV; c_bP = C.bP; c_dpbn = C.dpbn; c_dist = C.dist
    b_id = C.b

    def dist_b(d):
        v = c_dist.get(d)
        if v is None:
            v = A._dist(d); c_dist[d] = v
        return v

    # ---- head-local id arrays (once per head, indices 0..n) ----
    hp_id = [0] * (n + 1)
    hw_id = [0] * (n + 1)
    for h in range(0, n + 1):
        hp = "ROOT" if h == 0 else pos[h]
        v = c_hp.get(hp)
        if v is None: v = _crc("hp:" + hp); c_hp[hp] = v
        hp_id[h] = v
        hw = "<ROOT>" if h == 0 else low[h]
        v = c_hw.get(hw)
        if v is None: v = _crc("hw:" + hw); c_hw[hw] = v
        hw_id[h] = v

    flat = []
    ap = flat.append
    starts = []
    order = []

    for i in range(1, n + 1):
        dp = pos[i]; dw = low[i]; sdw = suf[i]
        dp_l = pos[i - 1] if i >= 2 else "<S>"
        dp_r = pos[i + 1] if i < n else "<E>"
        # dep-local ids (feat 3, 7, 19) -- once per i
        v = c_dp.get(dp)
        if v is None: v = _crc("dp:" + dp); c_dp[dp] = v
        dp_id = v
        v = c_dw.get(dw)
        if v is None: v = _crc("dw:" + dw); c_dw[dw] = v
        dw_id = v
        k = (dp_r, dp); v = c_dprdp.get(k)
        if v is None: v = _crc("dpr_dp:%s_%s" % k); c_dprdp[k] = v
        dpr_id = v
        # dep-side dir/dist maps (feat 12,13,18) -- once per i
        dpdir_i = {}
        dpldir_i = {}
        for dr in ("L", "R"):
            k = (dp, dr); v = c_dpdir.get(k)
            if v is None: v = _crc("dp_dir:%s_%s" % k); c_dpdir[k] = v
            dpdir_i[dr] = v
            k = (dp_l, dp, dr); v = c_dpldpdir.get(k)
            if v is None: v = _crc("dpl_dp_dir:%s_%s_%s" % k); c_dpldpdir[k] = v
            dpldir_i[dr] = v
        dpdist_i = {}
        for db in _BUCKETS:
            k = (dp, db); v = c_dpdist.get(k)
            if v is None: v = _crc("dp_dist:%s_%s" % k); c_dpdist[k] = v
            dpdist_i[db] = v

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

            ap(b_id)                    # 1
            ap(hp_id[h])                # 2
            ap(dp_id)                   # 3
            k = (hp, dp); v = c_hpdp.get(k)                                   # 4
            if v is None: v = _crc("hp_dp:%s_%s" % k); c_hpdp[k] = v
            ap(v)
            k = (hp, dp, dr); v = c_hpdpdir.get(k)                            # 5
            if v is None: v = _crc("hp_dp_dir:%s_%s_%s" % k); c_hpdpdir[k] = v
            ap(v)
            k = (hp, dp, db); v = c_hpdpdist.get(k)                           # 6
            if v is None: v = _crc("hp_dp_dist:%s_%s_%s" % k); c_hpdpdist[k] = v
            ap(v)
            ap(dw_id)                   # 7
            ap(hw_id[h])                # 8
            k = (hw, dw); v = c_hwdw.get(k)                                   # 9
            if v is None: v = _crc("hw_dw:%s_%s" % k); c_hwdw[k] = v
            ap(v)
            k = (hp, dw); v = c_hpdw.get(k)                                   # 10
            if v is None: v = _crc("hp_dw:%s_%s" % k); c_hpdw[k] = v
            ap(v)
            k = (hw, dp); v = c_hwdp.get(k)                                   # 11
            if v is None: v = _crc("hw_dp:%s_%s" % k); c_hwdp[k] = v
            ap(v)
            ap(dpdir_i[dr])             # 12
            ap(dpdist_i[db])            # 13
            k = (sdw, hp); v = c_dsufhp.get(k)                               # 14
            if v is None: v = _crc("dsuf_hp:%s_%s" % k); c_dsufhp[k] = v
            ap(v)
            k = (shw, dp); v = c_hsufdp.get(k)                               # 15
            if v is None: v = _crc("hsuf_dp:%s_%s" % k); c_hsufdp[k] = v
            ap(v)
            k = (sdw, dp, dr); v = c_dsufdpdir.get(k)                        # 16
            if v is None: v = _crc("dsuf_dp_dir:%s_%s_%s" % k); c_dsufdpdir[k] = v
            ap(v)
            hp_l = pos[h - 1] if h >= 2 else "<S>"
            k = (hp_l, hp, dp); v = c_hplhpdp.get(k)                          # 17
            if v is None: v = _crc("hpl_hp_dp:%s_%s_%s" % k); c_hplhpdp[k] = v
            ap(v)
            ap(dpldir_i[dr])           # 18
            ap(dpr_id)                 # 19
            hp_r = pos[h + 1] if 0 < h < n else "<E>"
            k = (hp_r, hp, dp); v = c_hprhpdp.get(k)                          # 20
            if v is None: v = _crc("hpr_hp_dp:%s_%s_%s" % k); c_hprhpdp[k] = v
            ap(v)
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
    return flat, starts, order, n


def sentence_scores(sent, avg, C):
    flat, starts, order, n = sentence_flat(sent, C)
    ids = np.asarray(flat, dtype=np.int64)
    scores = np.add.reduceat(avg[ids], np.asarray(starts, dtype=np.intp))
    Sc = {i: {} for i in range(1, n + 1)}
    for idx, (i, h) in enumerate(order):
        Sc[i][h] = float(scores[idx])
    return Sc


# decode reused from v2 (identical logic)
from experiments.exp_arc_parser_fastfeat_v2 import decode_from_scores


class FastArcParserV3(ArcParser):
    def __init__(self, avg):
        super().__init__(avg)
        self._C = FeatCache()

    def parse(self, tokens, pos_tags):
        if len(tokens) != len(pos_tags):
            raise ValueError("len mismatch")
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        Sc = sentence_scores(sent, self.avg, self._C)
        n = len(sent)
        head, margin = decode_from_scores(Sc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margin, heads=head)


def flat_byte_identity(sents):
    """Reconstruct each arc's ids from the flat stream and compare to stock _arc_ids (values+order)."""
    C = FeatCache()
    checked = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        flat, starts, order, n = sentence_flat(sent, C)
        starts2 = starts + [len(flat)]
        for k, (i, h) in enumerate(order):
            seg = flat[starts2[k]:starts2[k + 1]]
            ref = list(A._arc_ids(sent, i, h))
            if seg != ref:
                return False, checked, (i, h, seg, ref)
            checked += 1
    return True, checked, None


def heads_identity_check(sents, avg):
    ref = ArcParser(avg); fast = FastArcParserV3(avg)
    mism = marg = 0
    for toks, pos in sents:
        r = ref.parse(toks, pos); f = fast.parse(toks, pos)
        if r.heads != f.heads: mism += 1
        for k in r.margins:
            if r.margins[k] != f.margins.get(k): marg += 1; break
    return mism, marg


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

    ok, checked, bad = flat_byte_identity(sents)
    print("FLAT byte-identity vs stock _arc_ids: %s (%d arcs)" % (ok, checked), flush=True)
    if not ok:
        print("MISMATCH", bad, flush=True); return
    mism, marg = heads_identity_check(sents, avg)
    print("HEADS mism=%d MARGIN mism=%d /%d" % (mism, marg, len(sents)), flush=True)

    ref = ArcParser(avg); fast = FastArcParserV3(avg)
    t_ref = time_parse(ref, sents, reps)
    t_fast = time_parse(fast, sents, reps)
    print("STOCK: %.3fs  FAST3: %.3fs  SPEEDUP %.2fx (cut %.0f%%)"
          % (t_ref, t_fast, t_ref / t_fast, 100 * (1 - t_fast / t_ref)), flush=True)
    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_arc": n_arc, "byte_identical_arcs": checked,
                   "heads_mismatch": mism, "margin_mismatch": marg, "stock_s": t_ref,
                   "fast_s": t_fast, "speedup": t_ref / t_fast, "reps": reps}, f, indent=2)
    print("wrote metrics.json", flush=True)


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
        ok, ch, bad = flat_byte_identity(ss)
        assert ok, ("flat mismatch", bad)
        m, mm = heads_identity_check(ss, avg)
        assert m == 0 and mm == 0, ("head/margin", m, mm)
        print("SELF-TEST PASS: %d arcs byte-identical, heads+margins identical" % ch)
    else:
        main(a.n, a.reps)
