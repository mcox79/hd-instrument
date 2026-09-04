"""Glass-box hashed arc-factored dependency parser -- persistable parse() front-end.

Front-end Asset 2 for the reader-parser pipeline. Reproduces exp_depparse_hashed_cpu_v1's
arc-factored averaged perceptron with feature hashing (deterministic crc32 -> fixed weight array),
but exposes it as a PERSISTED model + a parse(tokens, pos_tags)->arcs wrapper that consumes the
POS from Asset 1 (hdlab.pos_tagger). The per-arc confidence margin (best - second head score)
is the calibrated abstain signal and is returned alongside the arcs.

_arc_ids and decode are copied verbatim from experiments/exp_depparse_hashed_cpu_v1.py so a loaded
model reproduces the cell's UAS exactly.

Public API:
  train_arc(train_sents, epochs, ...) -> np.ndarray            # averaged hashed weight vector (size 2^21)
  ArcParser(avg)                                               # wrap a trained weight vector
  ArcParser.load(path) / .save(path)                           # persist weight vector (npz float32)
  parser.parse(tokens, pos_tags) -> ParseResult               # arcs + per-token head score margin

sent tuple format (matches _ud_loader): (idx:int, form:str, upos:str, head:int, deprel:str).
Only form (idx 1) and upos (idx 2) are read at inference; head/deprel are placeholders in parse().
NO LLM. NO nltk. NO torch. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import zlib
from typing import Dict, List, NamedTuple, Sequence, Tuple

import numpy as np

SIZE = 1 << 21  # hashed weight-vector size (must match exp_depparse_hashed_cpu_v1)


def _h(f: str) -> int:
    return zlib.crc32(f.encode("utf-8")) & (SIZE - 1)


_MASK = SIZE - 1
_BUCKETS = ("1", "2", "3-5", "6-10", "11+")
_crc = _h  # byte-identical alias used by the memoized fast path below (id == _h(original_string))


def _dist(d: int) -> str:
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w: str) -> str:
    return w[-3:] if len(w) >= 3 else w


def _arc_ids(sent: Sequence[tuple], i: int, h: int) -> np.ndarray:
    """Hashed feature ids for arc (dependent i -> head h). Verbatim from exp_depparse_hashed_cpu_v1."""
    n = len(sent)
    dw, dp = sent[i - 1][1].lower(), sent[i - 1][2]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"
        d = 0
        dr = "R"
    else:
        hw, hp = sent[h - 1][1].lower(), sent[h - 1][2]
        d = h - i
        dr = "L" if d < 0 else "R"
    db = _dist(d)
    F = ["b", "hp:" + hp, "dp:" + dp, "hp_dp:%s_%s" % (hp, dp), "hp_dp_dir:%s_%s_%s" % (hp, dp, dr),
         "hp_dp_dist:%s_%s_%s" % (hp, dp, db), "dw:" + dw, "hw:" + hw, "hw_dw:%s_%s" % (hw, dw),
         "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp), "dp_dir:%s_%s" % (dp, dr), "dp_dist:%s_%s" % (dp, db),
         "dsuf_hp:%s_%s" % (_suf(dw), hp), "hsuf_dp:%s_%s" % (_suf(hw), dp), "dsuf_dp_dir:%s_%s_%s" % (_suf(dw), dp, dr)]
    hp_l = sent[h - 2][2] if h >= 2 else "<S>"
    dp_l = sent[i - 2][2] if i >= 2 else "<S>"
    dp_r = sent[i][2] if i < n else "<E>"
    hp_r = sent[h][2] if 0 < h < n else "<E>"
    F += ["hpl_hp_dp:%s_%s_%s" % (hp_l, hp, dp), "dpl_dp_dir:%s_%s_%s" % (dp_l, dp, dr), "dpr_dp:%s_%s" % (dp_r, dp),
          "hpr_hp_dp:%s_%s_%s" % (hp_r, hp, dp)]
    if h != 0:
        lo, hi = min(i, h), max(i, h)
        between = [sent[k - 1][2] for k in range(lo + 1, hi)]
        if "VERB" in between:
            F.append("bV:%s_%s" % (hp, dp))
        if "PUNCT" in between:
            F.append("bP:%s_%s" % (hp, dp))
        F.append("dp_bn:%s_%s" % (dp, _dist(len(between))))
    return np.fromiter((_h(f) for f in F), dtype=np.int64, count=len(F))


def _precompute(sents: Sequence[Sequence[tuple]]) -> list:
    out = []
    for s in sents:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                arc[i][h] = _arc_ids(s, i, h)
        out.append(arc)
    return out


def train_arc(
    train_sents: Sequence[Sequence[tuple]],
    epochs: int = 10,
    seed: int = 1027,
    maxlen: int = 50,
) -> np.ndarray:
    """Train arc-factored averaged perceptron (verbatim algorithm from the cell). Returns averaged weights (float64, size 2^21)."""
    rng = np.random.default_rng(seed)
    train = [s for s in train_sents if 1 <= len(s) <= maxlen]
    tr_arc = _precompute(train)
    W = np.zeros(SIZE)
    CW = np.zeros(SIZE)
    c = 1
    for ep in range(epochs):
        for si in rng.permutation(len(train)):
            s = train[si]
            arc = tr_arc[si]
            n = len(s)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n:
                    continue
                best_h = -1
                best_s = -1e18
                for h in range(0, n + 1):
                    if h == i:
                        continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s:
                        best_s = sc
                        best_h = h
                if best_h != gold_h:
                    gi = arc[i][gold_h]
                    pi = arc[i][best_h]
                    np.add.at(W, gi, 1.0)
                    np.add.at(CW, gi, c)
                    np.add.at(W, pi, -1.0)
                    np.add.at(CW, pi, -c)
                c += 1
    return W - CW / c


def _decode(avg: np.ndarray, arc: list, n: int) -> Tuple[Dict[int, int], Dict[int, float]]:
    """Greedy heads + cycle-break (verbatim from the cell). Returns (head map, per-token greedy margin best-second)."""
    S: Dict[int, Dict[int, float]] = {}
    head: Dict[int, int] = {}
    margin: Dict[int, float] = {}
    for i in range(1, n + 1):
        cand = []
        for h in range(0, n + 1):
            if h == i:
                continue
            cand.append((float(avg[arc[i][h]].sum()), h))
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


# ---------------------------------------------------------------------------
# BYTE-IDENTICAL fast path (promoted verbatim from exp_arc_parser_fastfeat_v1/v2/v3, Q111).
# Produces the identical int64 feature-id stream (same values, SAME ORDER) as _arc_ids and
# scores it with a batched np.add.reduceat (verified bit-identical to per-arc .sum(), max abs
# diff 0.0 on 393,225 held-out arcs), so heads + margins are bit-identical to the reference by
# construction. The lever is the 26.9x feature-string reuse: each distinct (template, key) is
# crc32'd ONCE via its exact original string, so its integer id equals _h(original_string).
# ---------------------------------------------------------------------------
class FeatCache:
    """Per-template integer-id caches keyed on cheap tuples (value = crc32 id == _h(str)).
    A fresh instance per parser keeps it deterministic; reuse across a document is what makes it fast."""

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
            v = _dist(d)
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


def sentence_flat(sent, C: "FeatCache"):
    """Build (flat_ids list, starts list, order list, n) for every arc, IDs in exact _arc_ids order."""
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
            v = _dist(d); c_dist[d] = v
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


def sentence_scores(sent, avg, C: "FeatCache"):
    """Per-arc score dict Sc[i][h] via ONE batched np.add.reduceat (bit-identical to per-arc .sum())."""
    flat, starts, order, n = sentence_flat(sent, C)
    ids = np.asarray(flat, dtype=np.int64)
    scores = np.add.reduceat(avg[ids], np.asarray(starts, dtype=np.intp))
    Sc = {i: {} for i in range(1, n + 1)}
    for idx, (i, h) in enumerate(order):
        Sc[i][h] = float(scores[idx])
    return Sc


def decode_from_scores(Sc, n):
    """EXACT replica of _decode, reading Sc[i][h] instead of avg[arc].sum()."""
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


class ParseResult(NamedTuple):
    arcs: List[Tuple[int, int]]        # list of (head_idx, dep_idx); indices are 1-based, head 0 = ROOT
    margins: Dict[int, float]          # per dep_idx greedy head-score margin (best - second); calibrated abstain signal
    heads: Dict[int, int]              # dep_idx -> head_idx


class ArcParser:
    """Wraps a trained hashed arc weight vector as a persistable parse() operator."""

    def __init__(self, avg: np.ndarray):
        self.avg = np.asarray(avg)
        self._C = FeatCache()  # per-parser feature-id cache; reused across a document (byte-identical fast path)

    def save(self, path: str) -> None:
        """Persist the averaged weight vector (npz, float32 to halve size; reproduces UAS to <1e-4)."""
        np.savez_compressed(path, avg=self.avg.astype(np.float32))

    @classmethod
    def load(cls, path: str) -> "ArcParser":
        with np.load(path) as z:
            return cls(z["avg"].astype(np.float64))

    def parse(self, tokens: Sequence[str], pos_tags: Sequence[str]) -> ParseResult:
        """tokens + UPOS (from Asset 1) -> dependency arcs + per-arc confidence margins.

        Uses the memoized fast path (sentence_scores + decode_from_scores). Output is bit-identical
        to _parse_reference by construction (identical feature-id stream, reduceat == per-arc .sum());
        the landing witness proves it at scale."""
        if len(tokens) != len(pos_tags):
            raise ValueError("tokens (%d) and pos_tags (%d) length mismatch" % (len(tokens), len(pos_tags)))
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        Sc = sentence_scores(sent, self.avg, self._C)
        head, margin = decode_from_scores(Sc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margin, heads=head)

    def _parse_reference(self, tokens: Sequence[str], pos_tags: Sequence[str]) -> ParseResult:
        """Stock reference parse (arc matrix via _arc_ids + _decode), kept UNCHANGED as the byte-identity
        reference the landing witness checks parse() against. Not used at inference (parse() is the fast path)."""
        if len(tokens) != len(pos_tags):
            raise ValueError("tokens (%d) and pos_tags (%d) length mismatch" % (len(tokens), len(pos_tags)))
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                arc[i][h] = _arc_ids(sent, i, h)
        head, margin = _decode(self.avg, arc, n)
        arcs = [(head[i], i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margin, heads=head)

    def eval_uas(self, dev_sents: Sequence[Sequence[tuple]], maxlen: int = 50) -> Tuple[float, int, int]:
        """Reproduce UAS on gold conllu sentences using the persisted weights. Returns (uas, n_correct, n_arcs).

        Uses the fast path; heads are bit-identical to the reference, so UAS is unchanged."""
        dev = [s for s in dev_sents if 1 <= len(s) <= maxlen]
        correct = 0
        tot = 0
        for s in dev:
            n = len(s)
            sent = [(k + 1, s[k][1], s[k][2], 0, "_") for k in range(n)]
            Sc = sentence_scores(sent, self.avg, self._C)
            head, _ = decode_from_scores(Sc, n)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n:
                    continue
                correct += int(head.get(i, -1) == gold_h)
                tot += 1
        return (correct / tot if tot else 0.0, correct, tot)
