"""arceager_parser -- PROMOTED VERBATIM (2026-09-02, Q111) from
experiments/exp_arceager_parser_operator_v1.py.

The improved in-substrate dependency parser as a loadable INFERENCE operator:
arc-eager transition system + Zhang & Nivre 2011 RICH NON-LOCAL STRUCTURAL
FEATURES (leftmost/rightmost dependents, valency, head-of-stack -- a structured
working-memory buffer). UD-EWT test UAS 0.842 (vs the live richfeat 0.775) and
emits a per-attachment CONFIDENCE score (softmax over legal actions at the
attaching step + raw margin) for the graded_competition distribution / N7.

Glass-box / deterministic / CPU numpy only, NO torch / spaCy / external LLM at
inference. The trained averaged-perceptron weight vector lives on disk at
MODEL_PATH; call load_model(MODEL_PATH) once, then parse_with_conf(tokens, pos, W).

The load + parse (+ confidence) surface and every helper/constant it depends on
were copied BYTE-FOR-BYTE from the experiment cell. Training code
(_train_transition / _move_costs_live / _perc_update / _load_ud_feats / uas_on /
main) is deliberately omitted -- the reader only needs load + parse + confidence.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import zlib
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(_REPO, "data/frontend_assets_exp")
MODEL_PATH = os.path.join(ASSET_DIR, "arceager_dynamic_ud_ewt.npz")

SIZE = 1 << 21; MASK = SIZE - 1
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)
RICH = True  # rich non-local structural features (the finer-drill winner)


def _h(f): return zlib.crc32(f.encode("utf-8")) & MASK
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w
def _szbucket(k): return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))
def _val(k): return "0" if k == 0 else ("1" if k == 1 else ("2" if k == 2 else "3+"))
_ROOT = ("<root>", "ROOT", "<root>"); _NONE = ("<none>", "<NONE>", "<none>")


def _pos(attr, k):
    return attr[k][1] if (k is not None and 0 <= k < len(attr)) else "<n>"


def _mk_attr(sent):
    a = [_ROOT]
    for tok in sent:
        w = tok[1]; p = tok[2]; wl = w.lower(); a.append((wl, p, _suf(wl)))
    return a


def _config_feats(stack, bptr, n, attr, heads, lc, rc, hd):
    s0 = stack[-1]; s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None; b1 = (bptr + 1) if (bptr + 1) <= n else None; b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s = attr[s0]
    s1w, s1p, s1s = attr[s1] if s1 is not None else _NONE
    b0w, b0p, b0s = attr[b0] if b0 is not None else _NONE
    b1w, b1p, b1s = attr[b1] if b1 is not None else _NONE
    b2w, b2p, b2s = attr[b2] if b2 is not None else _NONE
    dd = _dist(b0 - s0) if (b0 is not None and s0 > 0) else "0"
    s0hh = "1" if s0 in heads else "0"
    F = ["bias", "s0p:" + s0p, "s0w:" + s0w, "s1p:" + s1p, "b0p:" + b0p, "b0w:" + b0w, "b1p:" + b1p, "b2p:" + b2p,
         "s0p_b0p:%s_%s" % (s0p, b0p), "s0w_b0w:%s_%s" % (s0w, b0w), "s0p_b0w:%s_%s" % (s0p, b0w), "s0w_b0p:%s_%s" % (s0w, b0p),
         "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
         "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
         "dist:%s_%s_%s" % (dd, s0p, b0p), "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
         "stksz:" + _szbucket(len(stack))]
    if RICH:
        s0lc = lc.get(s0, []); s0rc = rc.get(s0, []); b0lc = lc.get(b0, [])
        s0lcp = _pos(attr, s0lc[0]) if s0lc else "<nc>"
        s0rcp = _pos(attr, s0rc[-1]) if s0rc else "<nc>"
        b0lcp = _pos(attr, b0lc[0]) if b0lc else "<nc>"
        s0hp = _pos(attr, hd.get(s0)) if s0 in hd else "<nh>"
        s0lclc = _pos(attr, lc.get(s0lc[0], [None])[0]) if s0lc and lc.get(s0lc[0]) else "<nc>"
        F += ["s0lcp:" + s0lcp, "s0rcp:" + s0rcp, "b0lcp:" + b0lcp, "s0hp:" + s0hp,
              "s0p_s0lcp:%s_%s" % (s0p, s0lcp), "s0p_s0rcp:%s_%s" % (s0p, s0rcp), "b0p_b0lcp:%s_%s" % (b0p, b0lcp),
              "s0p_b0p_s0rcp:%s_%s_%s" % (s0p, b0p, s0rcp), "s0p_b0p_b0lcp:%s_%s_%s" % (s0p, b0p, b0lcp),
              "s0p_s0hp:%s_%s" % (s0p, s0hp), "s0lclcp:" + s0lclc,
              "s0vall:%s_%s" % (_val(len(s0lc)), s0p), "s0valr:%s_%s" % (_val(len(s0rc)), s0p), "b0vall:%s_%s" % (_val(len(b0lc)), b0p)]
    return F


def _legal(stack, bptr, n, heads):
    moves = []; s0 = stack[-1]; buf = bptr <= n
    if buf: moves.append(SHIFT)
    if buf and s0 != 0 and s0 not in heads: moves.append(LARC)
    if buf: moves.append(RARC)
    if s0 != 0 and s0 in heads: moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, lc, rc, hd, a):
    if a == SHIFT:
        stack.append(bptr); bptr += 1
    elif a == LARC:
        s0 = stack[-1]; heads[s0] = bptr; hd[s0] = bptr
        lc[bptr] = [s0] + lc.get(bptr, [])
        stack.pop()
    elif a == RARC:
        s0 = stack[-1]; heads[bptr] = s0; hd[bptr] = s0
        rc.setdefault(s0, []).append(bptr)
        stack.append(bptr); bptr += 1
    elif a == REDU:
        stack.pop()
    return stack, bptr


def _score_actions(base_ids, W, legal):
    return {a: float(W[(base_ids ^ ACT_SALT[a]) & MASK].sum()) for a in legal}


def _argmax_legal(scores):
    best_a = None; best = -1e18
    for a, s in scores.items():
        if s > best: best = s; best_a = a
    return best_a


def load_model(path):
    with np.load(path) as z:
        return z["avg"].astype(np.float64)


def parse_with_conf(sent_tokens, pos_tags, W):
    """(heads, attach_conf, attach_margin). attach_conf[i]=softmax prob of the action that attached token i;
    attach_margin[i]=raw best-second action score. Unattached -> (0.0, 0.0)."""
    n = len(sent_tokens)
    sent = [(k + 1, sent_tokens[k], pos_tags[k], 0, "_", None) for k in range(n)]
    attr = _mk_attr(sent)
    stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; conf = {}; marg = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1: break
        legal = _legal(stack, bptr, n, heads)
        if not legal: break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, lc, rc, hd)), dtype=np.int64)
        scores = _score_actions(base_ids, W, legal); a = _argmax_legal(scores)
        sv = np.array([scores[x] for x in legal], dtype=np.float64)
        so = np.sort(sv)[::-1]; m = float(so[0] - so[1]) if len(so) > 1 else float(so[0])
        e = np.exp(sv - sv.max()); pa = float((e / e.sum())[legal.index(a)])
        s0 = stack[-1]
        if a == LARC: conf[s0] = pa; marg[s0] = m
        elif a == RARC: conf[bptr] = pa; marg[bptr] = m
        stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a); guard += 1
        if guard > 4 * (n + 2): break
    for i in range(1, n + 1):
        heads.setdefault(i, 0); conf.setdefault(i, 0.0); marg.setdefault(i, 0.0)
    return heads, conf, marg


# Promoted public alias: the reader routes through `parse`.
parse = parse_with_conf
