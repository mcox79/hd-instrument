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


class ParseResult(NamedTuple):
    arcs: List[Tuple[int, int]]        # list of (head_idx, dep_idx); indices are 1-based, head 0 = ROOT
    margins: Dict[int, float]          # per dep_idx greedy head-score margin (best - second); calibrated abstain signal
    heads: Dict[int, int]              # dep_idx -> head_idx


class ArcParser:
    """Wraps a trained hashed arc weight vector as a persistable parse() operator."""

    def __init__(self, avg: np.ndarray):
        self.avg = np.asarray(avg)

    def save(self, path: str) -> None:
        """Persist the averaged weight vector (npz, float32 to halve size; reproduces UAS to <1e-4)."""
        np.savez_compressed(path, avg=self.avg.astype(np.float32))

    @classmethod
    def load(cls, path: str) -> "ArcParser":
        with np.load(path) as z:
            return cls(z["avg"].astype(np.float64))

    def parse(self, tokens: Sequence[str], pos_tags: Sequence[str]) -> ParseResult:
        """tokens + UPOS (from Asset 1) -> dependency arcs + per-arc confidence margins."""
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
        """Reproduce UAS on gold conllu sentences using the persisted weights. Returns (uas, n_correct, n_arcs)."""
        dev = [s for s in dev_sents if 1 <= len(s) <= maxlen]
        correct = 0
        tot = 0
        for s in dev:
            n = len(s)
            arc = [[None] * (n + 1) for _ in range(n + 1)]
            for i in range(1, n + 1):
                for h in range(0, n + 1):
                    if h == i:
                        continue
                    arc[i][h] = _arc_ids(s, i, h)
            head, _ = _decode(self.avg, arc, n)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n:
                    continue
                correct += int(head.get(i, -1) == gold_h)
                tot += 1
        return (correct / tot if tot else 0.0, correct, tot)
