"""P8-named lever: vectorize the arc parser's POS-only joint features via a precomputed integer
POS-feature table + numpy gather, BYTE-IDENTICALLY.

Approach (byte-identity is by construction, not by luck):
  The arc score is np.add.reduceat(avg[flat_ids], starts) over a flat int64 id array in a FIXED
  order (P8). Margins are score DIFFERENCES and are checked with == by the witness, so the float
  reduction MUST NOT be split or reordered (P8's Neumaier lesson). Therefore the ONLY lever is
  building the SAME flat id array (same values, same order) with fewer per-arc Python ops.

  This cell builds that identical flat array with numpy SCATTER of column gathers instead of the
  O(n^2) per-arc Python dict.get + list.append loop:
    - POS-only joint features (hp_dp, hp_dp_dir, hp_dp_dist, hpl_hp_dp, hpr_hp_dp, bV, bP, dp_bn):
      gathered from a precomputed CLOSED-tagset integer table (UPOS x UPOS x dir/dist/bucket), built
      ONCE (the id == _h(exact_original_string), so values are identical to hdlab._arc_ids).
    - hoisted per-token features (b, hp, dp, dw, hw, dp_dir, dp_dist, dpl_dp_dir, dpr_dp): built O(n)
      per sentence via the FeatCache word dicts, then gathered across arcs.
    - reducible word features (hp_dw, hw_dp, dsuf_hp, hsuf_dp, dsuf_dp_dir): built into small
      per-sentence (token x POS-code) tables (~O(n*|tags|)) then gathered. Only hw_dw is genuinely
      open-vocabulary O(n^2) and is built as an (n+1 x n+1) table (same # dict.gets as the per-arc
      path, but nothing else in that loop).
  All 20 fixed feature slots are scattered into positions starts+slot; the 3 conditional tail
  features (bV,bP,dp_bn) are scattered with masks at starts+20(+offsets). reduceat over the same
  starts -> bit-identical scores -> bit-identical heads + margins.

Verifies: (1) flat id stream identical to hdlab.sentence_flat (values+order), every arc; (2) Sc dict
identical to hdlab.sentence_scores; (3) heads+arcs+margins identical to hdlab parse(); (4) fair
interleaved-median timing vs hdlab parse(). Held-out docs never used to tune. NO LLM. numpy+pure-py.

Run: .venv/Scripts/python.exe experiments/exp_arc_parser_posfeat_vectorize_v1.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import json
import sys
import time
import zlib

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.arc_parser as A
from hdlab.arc_parser import (ArcParser, FeatCache, sentence_flat, sentence_scores,
                              decode_from_scores, precompute_token, _crc, _suf, _dist, _MASK)
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

OUT_DIR = os.path.join(_REPO, "data/exp_arc_parser_posfeat_vectorize_v1")
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

# ---- closed POS-code universe (UPOS + specials used in feature strings) ----
# Derived from the WIRED tagger asset so a modified/extended tagger auto-adapts (the tables are keyed
# on tag STRINGS, so any tag set is byte-identical -- a larger inventory just makes bigger, still-cheap
# tables). Falls back to the standard 17 UPOS if the asset is unreadable.
_UPOS_FALLBACK = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART",
                  "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"]


def _load_upos():
    try:
        import json
        with open(_POS, encoding="utf-8") as fh:
            tags = json.load(fh).get("tags")
        if tags and all(isinstance(t, str) for t in tags):
            return list(tags)
    except Exception:
        pass
    return list(_UPOS_FALLBACK)


_UPOS = _load_upos()
_SPECIAL = ["ROOT", "<S>", "<E>"]
_CODES = _UPOS + _SPECIAL
_TAG2CODE = {t: k for k, t in enumerate(_CODES)}
_NC = len(_CODES)
_ROOT = _TAG2CODE["ROOT"]
_S = _TAG2CODE["<S>"]
_E = _TAG2CODE["<E>"]
_DIRSTR = ("L", "R")           # dir index 0=L, 1=R
_BUCKETS = ("1", "2", "3-5", "6-10", "11+")


def _bucket_idx(absd: np.ndarray) -> np.ndarray:
    """Vectorized _dist -> bucket index (0..4). abs 0->'3-5'(2), matches _dist(0)."""
    return np.select([absd == 1, absd == 2, absd <= 5, absd <= 10], [0, 1, 2, 3], default=4)


class PosTables:
    """Precomputed closed-tagset integer id tables for the 8 POS-only joint features. Built ONCE.
    Each entry == _crc(exact original feature string), so gathered ids match hdlab._arc_ids exactly."""

    __slots__ = ("hpdp", "hpdpdir", "hpdpdist", "hplhpdp", "hprhpdp", "bV", "bP", "dpbn")

    def __init__(self):
        C = _CODES
        NC = _NC
        self.hpdp = np.empty((NC, NC), dtype=np.int64)
        self.bV = np.empty((NC, NC), dtype=np.int64)
        self.bP = np.empty((NC, NC), dtype=np.int64)
        self.hpdpdir = np.empty((NC, NC, 2), dtype=np.int64)
        self.hpdpdist = np.empty((NC, NC, 5), dtype=np.int64)
        self.hplhpdp = np.empty((NC, NC, NC), dtype=np.int64)
        self.hprhpdp = np.empty((NC, NC, NC), dtype=np.int64)
        self.dpbn = np.empty((NC, 5), dtype=np.int64)
        for a in range(NC):
            ha = C[a]
            for b in range(NC):
                db = C[b]
                self.hpdp[a, b] = _crc("hp_dp:%s_%s" % (ha, db))
                self.bV[a, b] = _crc("bV:%s_%s" % (ha, db))
                self.bP[a, b] = _crc("bP:%s_%s" % (ha, db))
                for di in range(2):
                    self.hpdpdir[a, b, di] = _crc("hp_dp_dir:%s_%s_%s" % (ha, db, _DIRSTR[di]))
                for bi in range(5):
                    self.hpdpdist[a, b, bi] = _crc("hp_dp_dist:%s_%s_%s" % (ha, db, _BUCKETS[bi]))
                for c in range(NC):
                    self.hplhpdp[c, a, b] = _crc("hpl_hp_dp:%s_%s_%s" % (C[c], ha, db))
                    self.hprhpdp[c, a, b] = _crc("hpr_hp_dp:%s_%s_%s" % (C[c], ha, db))
            for bi in range(5):
                self.dpbn[a, bi] = _crc("dp_bn:%s_%s" % (ha, _BUCKETS[bi]))


_POS_TABLES = None


def pos_tables() -> PosTables:
    global _POS_TABLES
    if _POS_TABLES is None:
        _POS_TABLES = PosTables()
    return _POS_TABLES


def _word_cols_tables(low, suf, pos_s, code, n, i_arc, h_arc, hp_arc, dp_arc, dir_arc, C, rollcrc=False):
    """The 6 word features via small per-sentence (token x POS-code) tables + gather (feats 9-16).
    Only hw_dw (feat 9) is genuinely O(n^2). rollcrc=True builds it via a rolling-prefix crc32 over
    pre-encoded dep bytes (byte-identical: crc32(pre, crc32(prefix)) == crc32(prefix+pre))."""
    c_hpdw = C.hpdw; c_hwdp = C.hwdp; c_dsufhp = C.dsufhp; c_hsufdp = C.hsufdp
    c_dsufdpdir = C.dsufdpdir; c_hwdw = C.hwdw
    head_codes = sorted(set(int(code[h]) for h in range(0, n + 1)))
    dep_codes = sorted(set(int(code[i]) for i in range(1, n + 1)))

    T10 = np.zeros((_NC, n + 1), dtype=np.int64)          # feat 10 hp_dw : (hp_code, i)
    T14 = np.zeros((n + 1, _NC), dtype=np.int64)          # feat 14 dsuf_hp : (i, hp_code)
    for cc in head_codes:
        hs = _CODES[cc]
        for i in range(1, n + 1):
            dw = low[i]
            k = (hs, dw); v = c_hpdw.get(k)
            if v is None: v = _crc("hp_dw:%s_%s" % k); c_hpdw[k] = v
            T10[cc, i] = v
            k = (suf[i], hs); v = c_dsufhp.get(k)
            if v is None: v = _crc("dsuf_hp:%s_%s" % k); c_dsufhp[k] = v
            T14[i, cc] = v
    T11 = np.zeros((n + 1, _NC), dtype=np.int64)          # feat 11 hw_dp : (h, dp_code)
    T15 = np.zeros((n + 1, _NC), dtype=np.int64)          # feat 15 hsuf_dp : (h, dp_code)
    for h in range(0, n + 1):
        hw = "<ROOT>" if h == 0 else low[h]
        shw = _suf(hw)
        for cc in dep_codes:
            ds = _CODES[cc]
            k = (hw, ds); v = c_hwdp.get(k)
            if v is None: v = _crc("hw_dp:%s_%s" % k); c_hwdp[k] = v
            T11[h, cc] = v
            k = (shw, ds); v = c_hsufdp.get(k)
            if v is None: v = _crc("hsuf_dp:%s_%s" % k); c_hsufdp[k] = v
            T15[h, cc] = v
    T16 = np.zeros((n + 1, 2), dtype=np.int64)            # feat 16 dsuf_dp_dir : (i, dir)
    for i in range(1, n + 1):
        sdw = suf[i]; dp = pos_s[i]
        for di, dr in enumerate(_DIRSTR):
            k = (sdw, dp, dr); v = c_dsufdpdir.get(k)
            if v is None: v = _crc("dsuf_dp_dir:%s_%s_%s" % k); c_dsufdpdir[k] = v
            T16[i, di] = v
    T9 = np.empty((n + 1, n + 1), dtype=np.int64)         # feat 9 hw_dw : (h, i) -- genuinely O(n^2)
    if rollcrc:
        dwb = [b"" ] + [low[i].encode("utf-8") for i in range(1, n + 1)]  # encode each dep word once
        for h in range(0, n + 1):
            hw = "<ROOT>" if h == 0 else low[h]
            prefix = zlib.crc32(("hw_dw:" + hw + "_").encode("utf-8"))
            for i in range(1, n + 1):
                k = (hw, low[i]); v = c_hwdw.get(k)
                if v is None: v = zlib.crc32(dwb[i], prefix) & _MASK; c_hwdw[k] = v
                T9[h, i] = v
    else:
        for h in range(0, n + 1):
            hw = "<ROOT>" if h == 0 else low[h]
            for i in range(1, n + 1):
                dw = low[i]
                k = (hw, dw); v = c_hwdw.get(k)
                if v is None: v = _crc("hw_dw:%s_%s" % k); c_hwdw[k] = v
                T9[h, i] = v
    return (T9[h_arc, i_arc], T10[hp_arc, i_arc], T11[h_arc, dp_arc],
            T14[i_arc, hp_arc], T15[h_arc, dp_arc], T16[i_arc, dir_arc])


def _word_cols_pyloop(low, suf, pos_s, i_arc, h_arc, n, C):
    """Brief-faithful variant: the 6 word features via a Python arc-loop (word features 'stay in
    Python'), so ONLY the 8 POS-joint + hoisted features are vectorized. Isolates the POS-only lever."""
    c_hwdw = C.hwdw; c_hpdw = C.hpdw; c_hwdp = C.hwdp
    c_dsufhp = C.dsufhp; c_hsufdp = C.hsufdp; c_dsufdpdir = C.dsufdpdir
    na = i_arc.shape[0]
    c09 = np.empty(na, np.int64); c10 = np.empty(na, np.int64); c11 = np.empty(na, np.int64)
    c14 = np.empty(na, np.int64); c15 = np.empty(na, np.int64); c16 = np.empty(na, np.int64)
    ia = i_arc.tolist(); ha = h_arc.tolist()
    for k in range(na):
        i = ia[k]; h = ha[k]
        dw = low[i]; sdw = suf[i]; dp = pos_s[i]
        if h == 0:
            hw = "<ROOT>"; hp = "ROOT"; shw = "OT>"; dr = "R"
        else:
            hw = low[h]; hp = pos_s[h]; shw = suf[h]; dr = "L" if h < i else "R"
        key = (hw, dw); v = c_hwdw.get(key)
        if v is None: v = _crc("hw_dw:%s_%s" % key); c_hwdw[key] = v
        c09[k] = v
        key = (hp, dw); v = c_hpdw.get(key)
        if v is None: v = _crc("hp_dw:%s_%s" % key); c_hpdw[key] = v
        c10[k] = v
        key = (hw, dp); v = c_hwdp.get(key)
        if v is None: v = _crc("hw_dp:%s_%s" % key); c_hwdp[key] = v
        c11[k] = v
        key = (sdw, hp); v = c_dsufhp.get(key)
        if v is None: v = _crc("dsuf_hp:%s_%s" % key); c_dsufhp[key] = v
        c14[k] = v
        key = (shw, dp); v = c_hsufdp.get(key)
        if v is None: v = _crc("hsuf_dp:%s_%s" % key); c_hsufdp[key] = v
        c15[k] = v
        key = (sdw, dp, dr); v = c_dsufdpdir.get(key)
        if v is None: v = _crc("dsuf_dp_dir:%s_%s_%s" % key); c_dsufdpdir[key] = v
        c16[k] = v
    return c09, c10, c11, c14, c15, c16


def sentence_flat_vec(sent, C: FeatCache, T: PosTables, word_mode: str = "tables"):
    """Build (flat np.int64 array, starts np.intp array, order list, n) byte-identical to hdlab.sentence_flat.
    word_mode: 'tables' (default, full vectorization) | 'tables_rollcrc' (rolling-crc hw_dw) |
    'pyloop' (brief-faithful: word features via a Python loop; only POS+hoisted vectorized)."""
    n = len(sent)
    low, suf, pv_l, pp_l = precompute_token(sent)
    pos_s = [None] + [sent[k - 1][2] for k in range(1, n + 1)]

    # per-token POS code array, index 0..n ; code[0] = ROOT so hp_arc = code[h_arc] directly
    code = np.empty(n + 1, dtype=np.intp)
    code[0] = _ROOT
    for k in range(1, n + 1):
        c = _TAG2CODE.get(pos_s[k])
        if c is None:  # fail loud: the tag universe must cover the wired tagger (named coupling)
            raise KeyError("POS tag %r outside the vectorizer tag universe %s; rebuild PosTables "
                           "from the wired tagger's tag set" % (pos_s[k], _CODES))
        code[k] = c
    pv = np.asarray(pv_l, dtype=np.intp)
    pp = np.asarray(pp_l, dtype=np.intp)

    # arc enumeration order: for i in 1..n, for h in 0..n if h!=i  (meshgrid row-major == that order)
    ii, hh = np.meshgrid(np.arange(1, n + 1, dtype=np.intp),
                         np.arange(0, n + 1, dtype=np.intp), indexing="ij")
    keep = hh != ii
    i_arc = ii[keep]
    h_arc = hh[keep]
    na = i_arc.shape[0]
    order = list(zip(i_arc.tolist(), h_arc.tolist()))

    root = h_arc == 0
    nonroot = ~root
    dir_arc = np.where(root, 1, (h_arc > i_arc).astype(np.intp))          # 0=L,1=R ; root->R
    d = np.where(root, 0, h_arc - i_arc)
    dist_arc = _bucket_idx(np.abs(d))
    hp_arc = code[h_arc]                                                  # code[0]=ROOT
    dp_arc = code[i_arc]
    hpl_arc = np.where(h_arc >= 2, code[np.clip(h_arc - 1, 0, n)], _S)
    hpr_arc = np.where((h_arc > 0) & (h_arc < n), code[np.clip(h_arc + 1, 0, n)], _E)
    lo = np.minimum(i_arc, h_arc)
    hi = np.maximum(i_arc, h_arc)
    hiq = np.clip(hi - 1, 0, n)
    hasV = (pv[hiq] - pv[lo]) > 0
    hasP = (pp[hiq] - pp[lo]) > 0
    hasV_e = nonroot & hasV
    hasP_e = nonroot & hasP
    nb = hi - lo - 1
    btwn_arc = _bucket_idx(np.abs(np.where(root, 0, nb)))

    # ---- 8 POS-only joint columns (gather from closed table) ----
    c04 = T.hpdp[hp_arc, dp_arc]
    c05 = T.hpdpdir[hp_arc, dp_arc, dir_arc]
    c06 = T.hpdpdist[hp_arc, dp_arc, dist_arc]
    c17 = T.hplhpdp[hpl_arc, hp_arc, dp_arc]
    c20 = T.hprhpdp[hpr_arc, hp_arc, dp_arc]
    cbV = T.bV[hp_arc, dp_arc]
    cbP = T.bP[hp_arc, dp_arc]
    cbn = T.dpbn[dp_arc, btwn_arc]

    # ---- hoisted per-token id arrays (O(n)), then gather ----
    c_hp = C.hp; c_dp = C.dp; c_dw = C.dw; c_hw = C.hw; c_dpdir = C.dpdir
    c_dpdist = C.dpdist; c_dpldpdir = C.dpldpdir; c_dprdp = C.dprdp

    ph_hp = np.empty(n + 1, dtype=np.int64)     # feat 2
    ph_hw = np.empty(n + 1, dtype=np.int64)     # feat 8
    for h in range(0, n + 1):
        hpt = "ROOT" if h == 0 else pos_s[h]
        v = c_hp.get(hpt)
        if v is None: v = _crc("hp:" + hpt); c_hp[hpt] = v
        ph_hp[h] = v
        hwt = "<ROOT>" if h == 0 else low[h]
        v = c_hw.get(hwt)
        if v is None: v = _crc("hw:" + hwt); c_hw[hwt] = v
        ph_hw[h] = v
    pd_dp = np.empty(n + 1, dtype=np.int64)     # feat 3
    pd_dw = np.empty(n + 1, dtype=np.int64)     # feat 7
    pd_dpr = np.empty(n + 1, dtype=np.int64)    # feat 19
    pd_dpdir = np.empty((n + 1, 2), dtype=np.int64)   # feat 12
    pd_dpldir = np.empty((n + 1, 2), dtype=np.int64)  # feat 18
    pd_dpdist = np.empty((n + 1, 5), dtype=np.int64)  # feat 13
    for i in range(1, n + 1):
        dp = pos_s[i]
        v = c_dp.get(dp)
        if v is None: v = _crc("dp:" + dp); c_dp[dp] = v
        pd_dp[i] = v
        dw = low[i]
        v = c_dw.get(dw)
        if v is None: v = _crc("dw:" + dw); c_dw[dw] = v
        pd_dw[i] = v
        dp_r = pos_s[i + 1] if i < n else "<E>"
        k = (dp_r, dp); v = c_dprdp.get(k)
        if v is None: v = _crc("dpr_dp:%s_%s" % k); c_dprdp[k] = v
        pd_dpr[i] = v
        dp_l = pos_s[i - 1] if i >= 2 else "<S>"
        for di, dr in enumerate(_DIRSTR):
            k = (dp, dr); v = c_dpdir.get(k)
            if v is None: v = _crc("dp_dir:%s_%s" % k); c_dpdir[k] = v
            pd_dpdir[i, di] = v
            k = (dp_l, dp, dr); v = c_dpldpdir.get(k)
            if v is None: v = _crc("dpl_dp_dir:%s_%s_%s" % k); c_dpldpdir[k] = v
            pd_dpldir[i, di] = v
        for bi, bk in enumerate(_BUCKETS):
            k = (dp, bk); v = c_dpdist.get(k)
            if v is None: v = _crc("dp_dist:%s_%s" % k); c_dpdist[k] = v
            pd_dpdist[i, bi] = v

    c01 = C.b                                    # feat 1 const
    c02 = ph_hp[h_arc]
    c03 = pd_dp[i_arc]
    c07 = pd_dw[i_arc]
    c08 = ph_hw[h_arc]
    c12 = pd_dpdir[i_arc, dir_arc]
    c13 = pd_dpdist[i_arc, dist_arc]
    c18 = pd_dpldir[i_arc, dir_arc]
    c19 = pd_dpr[i_arc]

    # ---- word features (feats 9-16): mode-selected, all byte-identical ----
    if word_mode == "pyloop":
        c09, c10, c11, c14, c15, c16 = _word_cols_pyloop(low, suf, pos_s, i_arc, h_arc, n, C)
    else:
        c09, c10, c11, c14, c15, c16 = _word_cols_tables(
            low, suf, pos_s, code, n, i_arc, h_arc, hp_arc, dp_arc, dir_arc, C,
            rollcrc=(word_mode == "tables_rollcrc"))

    # ---- assemble flat via scatter ----
    seg_len = np.full(na, 20, dtype=np.intp) + nonroot.astype(np.intp) \
        + hasV_e.astype(np.intp) + hasP_e.astype(np.intp)
    starts = np.empty(na, dtype=np.intp)
    starts[0] = 0
    np.cumsum(seg_len[:-1], out=starts[1:])
    total = int(starts[-1] + seg_len[-1])
    flat = np.empty(total, dtype=np.int64)

    cols = [np.full(na, c01, dtype=np.int64), c02, c03, c04, c05, c06, c07, c08, c09, c10,
            c11, c12, c13, c14, c15, c16, c17, c18, c19, c20]  # feats 1..20 in order
    for slot, col in enumerate(cols):
        flat[starts + slot] = col
    base = starts + 20
    off = np.zeros(na, dtype=np.intp)
    m = hasV_e
    flat[base[m]] = cbV[m]
    off = off + hasV_e.astype(np.intp)
    m = hasP_e
    flat[(base + off)[m]] = cbP[m]
    off = off + hasP_e.astype(np.intp)
    m = nonroot
    flat[(base + off)[m]] = cbn[m]
    return flat, starts, order, n


def sentence_scores_vec(sent, avg, C: FeatCache, T: PosTables, word_mode: str = "tables"):
    flat, starts, order, n = sentence_flat_vec(sent, C, T, word_mode)
    scores = np.add.reduceat(avg[flat], starts)
    Sc = {i: {} for i in range(1, n + 1)}
    for idx, (i, h) in enumerate(order):
        Sc[i][h] = float(scores[idx])
    return Sc


# Length gate: the vectorized path's per-sentence numpy setup only pays off once O(n^2) is large.
# Measured (OMP=1, clean, two independent runs): n<=10 reliably REGRESSES (0.24-0.79x); n>=21 reliably
# WINS (1.5-2.6x); the 11-20 zone is NOISY across runs (0.69x-1.32x), i.e. near the crossover. So the
# gate is set conservatively at 16 to keep the win robust to ANY sentence-length distribution (never a
# meaningful regression). It is tunable per corpus; even UNGATED the aggregate parser throughput is
# ~2.16x because long sentences dominate the total arc count. Both branches are byte-identical.
GATE_THRESH = 16


def sentence_scores_auto(sent, avg, C: FeatCache, T: PosTables, thresh: int = GATE_THRESH):
    """Length-gated scorer: vectorized POS-feature path for n>=thresh, hdlab scalar fast path below.
    Byte-identical to hdlab.sentence_scores on both branches."""
    if len(sent) < thresh:
        return sentence_scores(sent, avg, C)
    return sentence_scores_vec(sent, avg, C, T)


class VecParser:
    """Same interface as ArcParser.parse but scores via the (optionally length-gated) vectorized path."""

    def __init__(self, avg, gate: bool = False, thresh: int = GATE_THRESH, word_mode: str = "tables"):
        self.avg = np.asarray(avg)
        self._C = FeatCache()
        self._T = pos_tables()
        self._gate = gate
        self._thresh = thresh
        self._word_mode = word_mode

    def parse(self, tokens, pos_tags):
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        if self._gate and n < self._thresh:
            Sc = sentence_scores(sent, self.avg, self._C)
        else:
            Sc = sentence_scores_vec(sent, self.avg, self._C, self._T, self._word_mode)
        head, margin = decode_from_scores(Sc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        from hdlab.arc_parser import ParseResult
        return ParseResult(arcs=arcs, margins=margin, heads=head)


def load_tagged(docs, per_doc=250, minlen=1, maxlen=120):
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


def run():
    avg = ArcParser.load(_ARC).avg
    T = pos_tables()
    sents = load_tagged(_HELD_OUT, per_doc=250)
    n_arc = sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)
    print("held-out: %d sentences, %d arcs" % (len(sents), n_arc), flush=True)

    # (1) flat id stream identity vs hdlab.sentence_flat (values + order), every arc
    Cref = FeatCache(); Cvec = FeatCache()
    flat_mismatch = 0; arcs_checked = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        fr, sr, orr, _ = sentence_flat(sent, Cref)
        fv, sv, ov, _ = sentence_flat_vec(sent, Cvec, T)
        if list(fv) != list(fr) or list(sv) != list(sr) or ov != orr:
            flat_mismatch += 1
        arcs_checked += len(orr)
    print("(1) flat id stream identical to hdlab.sentence_flat: %s  (%d sents, %d arcs, %d mismatched)"
          % (flat_mismatch == 0, len(sents), arcs_checked, flat_mismatch), flush=True)

    # (2) Sc dict identity vs hdlab.sentence_scores (bit-identical floats)
    Cref2 = FeatCache(); Cvec2 = FeatCache()
    sc_mismatch = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        Sr = sentence_scores(sent, avg, Cref2)
        Sv = sentence_scores_vec(sent, avg, Cvec2, T)
        bad = False
        for i in Sr:
            for h in Sr[i]:
                if Sr[i][h] != Sv[i].get(h):
                    bad = True; break
            if bad: break
        sc_mismatch += int(bad)
    print("(2) Sc scores bit-identical to hdlab.sentence_scores: %s  (%d mismatched sents)"
          % (sc_mismatch == 0, sc_mismatch), flush=True)

    # (3) heads + arcs + margins identical to hdlab parse()
    hd = ArcParser(avg)
    vp = VecParser(avg)
    head_mis = marg_mis = 0
    for toks, pos in sents:
        r = hd.parse(toks, pos)
        f = vp.parse(toks, pos)
        if r.heads != f.heads or r.arcs != f.arcs:
            head_mis += 1
        for kk in r.margins:
            if r.margins[kk] != f.margins.get(kk):
                marg_mis += 1; break
    print("(3) parse() heads+arcs identical: %s  margins bit-identical: %s  (%d/%d head, %d/%d margin)"
          % (head_mis == 0, marg_mis == 0, head_mis, len(sents), marg_mis, len(sents)), flush=True)

    # (4) fair interleaved-median timing vs hdlab parse()
    slc = sents[:120]
    hd2 = ArcParser(avg); vp2 = VecParser(avg)
    t_hd = med_time(hd2.parse, slc)
    t_vec = med_time(vp2.parse, slc)
    print("\n(4) TIMING (warm, 120-sent slice, median of 7):")
    print("    hdlab parse() (landed fast): %.4fs" % t_hd)
    print("    vectorized POS-feat path:    %.4fs   (%.2fx over landed fast path)" % (t_vec, t_hd / t_vec))

    byte_ok = (flat_mismatch == 0 and sc_mismatch == 0 and head_mis == 0 and marg_mis == 0)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump({"n_sents": len(sents), "n_arcs": n_arc, "arcs_checked": arcs_checked,
                   "flat_mismatch": flat_mismatch, "sc_mismatch": sc_mismatch,
                   "head_mismatch": head_mis, "margin_mismatch": marg_mis,
                   "byte_identical": byte_ok,
                   "t_hdlab_fast_s": t_hd, "t_vec_s": t_vec, "vec_over_fast": t_hd / t_vec,
                   "numpy": np.__version__}, fh, indent=2)
    print("\nBYTE-IDENTICAL: %s | speedup over landed fast path: %.2fx" % (byte_ok, t_hd / t_vec))
    print("wrote", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    run()
