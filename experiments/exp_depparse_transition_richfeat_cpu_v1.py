"""
exp_depparse_transition_richfeat_cpu_v1.py -- RICH-FEATURE LIBRARY on the glass-box arc-eager
  transition dependency parser. ONE VARIABLE = the FEATURE SET (base hashed config-features vs
  base + rich classical templates). SAME transition system (arc-eager), SAME dynamic-oracle training
  (Goldberg & Nivre 2012), SAME UD-EWT split, SAME seeds, SAME EPOCHS as the base cell
  exp_depparse_transition_arceager_cpu_v1 (which landed MIDDLE at dynamic UAS 0.8109 / batch 0.79).

WHY (roadmap move #2, envelope-push on build-#1 MIDDLE): the reader-capability roadmap identifies
  RICH FEATURES as the cross-cutting classical lever that lifts parser + POS + NER + chunking. Apply
  it to the parser first. Dependency-parsing literature (Koo/Carreras/Collins 2008; Bohnet 2010;
  Honnibal 2013) credits word-shape, prefix/suffix affixes, capitalization/digit flags, and word
  CLUSTERS with the biggest cheap UAS gains (clusters generalize known words; shape/affix generalize
  to UNSEEN words). All templates are inspectable classical strings; averaged structured perceptron,
  no gradient.

PRIOR-WORK (KB, build-on + credit, cosine<0.30 so novel for the PARSER but adjacent NER evidence):
  ner_brown_cluster_cpu_v1 (MIDDLE, +0.0111 F1) + ner_feature_ablation_cpu_v1 found on THIS substrate:
  Brown clusters ~ +1pp MIDDLE, char-ngrams SUBSUMED by char-shape, and feature STACKING SATURATES
  (POS-cascade > Brown-cluster > gazetteer). So the honest prior expectation is MIDDLE-grade lift;
  HARD_PASS (+0.03) would be a genuine step beyond the NER precedent. CITED@notes/strategy_decisions_2026-06-11/12.

ARMS (ONE variable = feature set; dynamic-oracle transition parser, 3 seeds each):
  ARM_BASE_FEAT  -- base config-features (BYTE-IDENTICAL to the base cell's _config_feats). Positive
                    control: must reproduce dynamic UAS ~0.8109 at this regime (Gate D, tol 0.02).
  ARM_RICH_FEAT  -- base + MORPH (shape + prefix1-3 + suffix1-4 + caps/digit/hyphen flags) + CLUST
                    (distributional k-means word-cluster + frequency-rank bucket). The mechanism arm.
  ABLATION (seed 1 only, to attribute the lift -- which feature group helps):
    ARM_BASE_PLUS_MORPH  -- base + MORPH only.
    ARM_BASE_PLUS_CLUST  -- base + CLUST only.
  LEARNING CURVE: rich arm, seed 1, data fractions {0.1,0.25,0.5,1.0} -- must stay INTACT (rise>0).

CLUSTER = distributional k-means proxy (NOT full Brown/Ney-Essen bigram-MI exchange clustering, which
  is O(V*C) fiddly + risky for local-foreground). Context vector per word = normalized counts of
  (left coarse-POS, right coarse-POS); K=32 cosine k-means, deterministic freq-ordered init, fixed
  seed. Glass-box: centroids + assignments inspectable. Reported HONESTLY as a proxy per the task's
  cheap-proxy allowance. POS is already a substrate input feature so POS-context clustering is fair.

MEASURE: UAS (rich vs base, both 3-seed, 2SE) + rich learning curve + (secondary, small-n) buried
  subject-id. Design-gate: real baseline (in-run base-feat arm reproduces 0.8109), CAN-FAIL (rich
  ties base), difficulty-on (real UD-EWT), ONE variable (feature set).

PRE-REGISTERED bands (see prereg md):
  HARD_PASS = ARM_RICH_FEAT UAS mean-2SE >= base_mean + 0.03 (a REAL 2SE-clean margin, i.e. rich CI
              lower bound clears base mean by >= 0.03) AND rich learning curve RISES (lc_rise >= 0.02).
  MIDDLE    = rich UAS > base by a positive margin but below the +0.03 2SE-clean bar.
  HARD_FAIL = rich UAS <= base (rich features do not help) OR rich CI overlaps base (no real lift).
  UNKNOWN   = corpus load fails OR base-feat arm fails to reproduce 0.8109 within tol 0.02 (Gate D:
              feature-plumbing is wrong; downstream rich comparison untrustworthy) OR n_buried == 0.
  crlb_n/a: parse accuracy is discrete argmax over trained scores -- no CRLB noise floor.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (rich weights differ from base weights; base reproduces 0.8109)
# - final_metrics_atomicity = tmp_replace (os.replace; write_metrics + crash path both atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete parse accuracy, no noise floor)
# - baseline_in_band at smoke (base dynamic UAS ~0.73-0.81 in (0.05,0.95); headroom to 0.88)
# - discriminator fires: base vs rich weights differ AND base reproduces prior (Gate D); n_buried>0
# - cardinality_ok: learning curve EXPECTED points = len(LC_FRACS); verdict counts them
# - Gate D positive control: base-feat arm reproduces prior dynamic UAS at THIS regime (tol 0.02)
# - HYPOTHESIZED/MEASURED/CITED tags in report; no PYTHONHASHSEED-derived seeding (fixed ints + crc32)
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, zlib, traceback, platform
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu

ANCHOR_NAME = "depparse_transition_richfeat_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21
MASK = SIZE - 1
NOUN_POS = ("NOUN", "PROPN", "PRON")

SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_NAMES = {SHIFT: "SHIFT", LARC: "LEFT-ARC", RARC: "RIGHT-ARC", REDU: "REDUCE"}
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)

EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "3" if SMOKE else "10"))
MAXLEN = int(os.environ.get("HDLAB_MAXLEN", "50"))
EXPLORE_AFTER = int(os.environ.get("HDLAB_EXPLORE_AFTER", "2"))
EXPLORE_P = float(os.environ.get("HDLAB_EXPLORE_P", "0.9"))
DO_LC = os.environ.get("HDLAB_DO_LC", "1") == "1"
DO_ABLATION = os.environ.get("HDLAB_DO_ABLATION", "1") == "1"
LC_FRACS = [0.1, 0.25, 0.5, 1.0]
CLU_K = int(os.environ.get("HDLAB_CLU_K", "32"))
CLU_V = int(os.environ.get("HDLAB_CLU_V", "2000"))
CLU_ITERS = int(os.environ.get("HDLAB_CLU_ITERS", "12"))

# Feature modes
M_BASE, M_MORPH, M_CLUST, M_RICH = "base", "morph", "clust", "rich"


def _h(f):
    return zlib.crc32(f.encode("utf-8")) & MASK


def _dist(d):
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w):
    return w[-3:] if len(w) >= 3 else w


def _szbucket(k):
    return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))


# ---- rich morphology helpers (surface-form only; generalize to UNSEEN words) ----
def _shape(w):
    """Collapsed word shape: X=upper x=lower d=digit punct=literal; adjacent repeats collapsed."""
    out = []
    for ch in w:
        if ch.isupper():
            c = "X"
        elif ch.islower():
            c = "x"
        elif ch.isdigit():
            c = "d"
        else:
            c = ch
        if out and out[-1] == c:
            continue
        out.append(c)
    return "".join(out)[:8]


def _flags(w):
    """(cap, allcap, hasdigit, hashyphen) as a compact string flag."""
    cap = 1 if (w[:1].isupper()) else 0
    allcap = 1 if (len(w) > 1 and w.isupper()) else 0
    dig = 1 if any(ch.isdigit() for ch in w) else 0
    hyp = 1 if ("-" in w) else 0
    return "%d%d%d%d" % (cap, allcap, dig, hyp)


def _pref(w, k):
    return w[:k] if len(w) >= k else w


def _sufk(w, k):
    return w[-k:] if len(w) >= k else w


# ================================================================================================
# CLUSTER = distributional k-means proxy over (left/right coarse-POS) context. Deterministic.
# ================================================================================================
def _build_clusters(train, K=CLU_K, V=CLU_V, iters=CLU_ITERS):
    freq = {}
    for s in train:
        for (i, w, p, h, dl, num) in s:
            wl = w.lower(); freq[wl] = freq.get(wl, 0) + 1
    POS_LIST = sorted({p for s in train for (i, w, p, h, dl, num) in s})
    pidx = {p: k for k, p in enumerate(POS_LIST)}
    P = len(POS_LIST)
    # freq-rank dict (deterministic tie-break by word)
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    rank = {w: r for r, (w, _) in enumerate(ranked)}
    vocab = [w for (w, _) in ranked[:V]]
    widx = {w: k for k, w in enumerate(vocab)}
    ctx = np.zeros((len(vocab), 2 * P), dtype=np.float64)
    for s in train:
        toks = [(w.lower(), p) for (i, w, p, h, dl, num) in s]
        m = len(toks)
        for j in range(m):
            wl = toks[j][0]
            r = widx.get(wl)
            if r is None:
                continue
            if j > 0:
                ctx[r, pidx[toks[j - 1][1]]] += 1.0
            if j < m - 1:
                ctx[r, P + pidx[toks[j + 1][1]]] += 1.0
    norms = np.linalg.norm(ctx, axis=1, keepdims=True); norms[norms == 0] = 1.0
    ctxn = ctx / norms
    K = min(K, len(vocab)) if len(vocab) else 0
    clu = {}
    if K >= 2:
        cent = ctxn[:K].copy()  # deterministic freq-ordered init
        for _ in range(iters):
            sims = ctxn @ cent.T
            assign = sims.argmax(1)
            newc = np.zeros_like(cent)
            for k in range(K):
                mask = assign == k
                if mask.any():
                    newc[k] = ctxn[mask].mean(0)
                else:
                    newc[k] = cent[k]
            nn = np.linalg.norm(newc, axis=1, keepdims=True); nn[nn == 0] = 1.0
            cent = newc / nn
        assign = (ctxn @ cent.T).argmax(1)
        clu = {vocab[r]: int(assign[r]) for r in range(len(vocab))}
    return {"clu": clu, "rank": rank, "n_vocab": len(vocab), "n_clusters": K}


def _clu_of(wl, lex):
    c = lex["clu"].get(wl)
    return ("c%d" % c) if c is not None else "cRARE"


def _fb_of(wl, lex):
    r = lex["rank"].get(wl)
    if r is None:
        return "OOV"
    if r < 100:
        return "0"
    if r < 500:
        return "1"
    if r < 2000:
        return "2"
    if r < 8000:
        return "3"
    return "4"


# ================================================================================================
# Config = (stack, bptr, heads). attr[k] = (word_lower, pos, suf3, form_original) for k in 1..n.
# ================================================================================================
_ROOT_ATTR = ("<root>", "ROOT", "<root>", "<root>")
_NONE_ATTR = ("<none>", "<NONE>", "<none>", "<none>")


def _mk_attr(sent):
    a = [_ROOT_ATTR]
    for (i, w, p, h, dl, num) in sent:
        a.append((w.lower(), p, _suf(w.lower()), w))
    return a


def _config_feats(stack, bptr, n, attr, heads, mode, lex):
    """Config features. mode=base -> BYTE-IDENTICAL to the base cell's _config_feats. mode adds groups."""
    s0 = stack[-1]
    s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None
    b1 = (bptr + 1) if (bptr + 1) <= n else None
    b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s, s0f = attr[s0]
    s1w, s1p, s1s, s1f = attr[s1] if s1 is not None else _NONE_ATTR
    b0w, b0p, b0s, b0f = attr[b0] if b0 is not None else _NONE_ATTR
    b1w, b1p, b1s, b1f = attr[b1] if b1 is not None else _NONE_ATTR
    b2w, b2p, b2s, b2f = attr[b2] if b2 is not None else _NONE_ATTR
    if b0 is not None and s0 > 0:
        dd = _dist(b0 - s0)
    else:
        dd = "0"
    s0hh = "1" if s0 in heads else "0"
    # ---- BASE templates (identical to base cell) ----
    F = [
        "bias",
        "s0p:" + s0p, "s0w:" + s0w, "s1p:" + s1p,
        "b0p:" + b0p, "b0w:" + b0w, "b1p:" + b1p, "b2p:" + b2p,
        "s0p_b0p:%s_%s" % (s0p, b0p), "s0w_b0w:%s_%s" % (s0w, b0w),
        "s0p_b0w:%s_%s" % (s0p, b0w), "s0w_b0p:%s_%s" % (s0w, b0p),
        "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
        "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
        "dist:%s_%s_%s" % (dd, s0p, b0p),
        "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
        "stksz:" + _szbucket(len(stack)),
    ]
    if mode == M_BASE:
        return F
    add_morph = mode in (M_MORPH, M_RICH)
    add_clust = mode in (M_CLUST, M_RICH)
    if add_morph:
        s0sh = _shape(s0f); b0sh = _shape(b0f); s1sh = _shape(s1f)
        s0fl = _flags(s0f); b0fl = _flags(b0f)
        F += [
            # word shape
            "s0sh:" + s0sh, "b0sh:" + b0sh, "s0sh_b0sh:%s_%s" % (s0sh, b0sh),
            "s0sh_b0p:%s_%s" % (s0sh, b0p), "b0sh_s0p:%s_%s" % (b0sh, s0p),
            "s1sh_s0sh:%s_%s" % (s1sh, s0sh),
            # prefixes (1-3) + extra suffixes (1,2,4); base already has suf3 as s0s/b0s
            "s0p1:" + _pref(s0w, 1), "s0p2:" + _pref(s0w, 2), "s0p3:" + _pref(s0w, 3),
            "b0p1:" + _pref(b0w, 1), "b0p2:" + _pref(b0w, 2), "b0p3:" + _pref(b0w, 3),
            "s0u1:" + _sufk(s0w, 1), "s0u2:" + _sufk(s0w, 2), "s0u4:" + _sufk(s0w, 4),
            "b0u1:" + _sufk(b0w, 1), "b0u2:" + _sufk(b0w, 2), "b0u4:" + _sufk(b0w, 4),
            "s0u4_b0p:%s_%s" % (_sufk(s0w, 4), b0p), "b0u4_s0p:%s_%s" % (_sufk(b0w, 4), s0p),
            # capitalization / digit / hyphen flags (x POS)
            "s0fl:" + s0fl, "b0fl:" + b0fl, "s0fl_p:%s_%s" % (s0fl, s0p), "b0fl_p:%s_%s" % (b0fl, b0p),
            "s0fl_b0p:%s_%s" % (s0fl, b0p),
        ]
    if add_clust:
        s0c = _clu_of(s0w, lex); b0c = _clu_of(b0w, lex)
        s1c = _clu_of(s1w, lex) if s1 is not None else "cNONE"
        b1c = _clu_of(b1w, lex) if b1 is not None else "cNONE"
        s0fb = _fb_of(s0w, lex); b0fb = _fb_of(b0w, lex)
        F += [
            "s0c:" + s0c, "b0c:" + b0c, "s0c_b0c:%s_%s" % (s0c, b0c),
            "s0c_b0p:%s_%s" % (s0c, b0p), "s0p_b0c:%s_%s" % (s0p, b0c),
            "s1c_s0c_b0c:%s_%s_%s" % (s1c, s0c, b0c), "s0c_b1c:%s_%s" % (s0c, b1c),
            "s0c_b0w:%s_%s" % (s0c, b0w), "s0w_b0c:%s_%s" % (s0w, b0c),
            "s0fb:" + s0fb, "b0fb:" + b0fb, "s0fb_b0fb:%s_%s" % (s0fb, b0fb),
            "s0fb_p:%s_%s" % (s0fb, s0p),
        ]
    return F


# ---- arc-eager mechanics (identical to base cell) ----
def _legal(stack, bptr, n, heads):
    moves = []
    s0 = stack[-1]
    buf_nonempty = bptr <= n
    if buf_nonempty:
        moves.append(SHIFT)
    if buf_nonempty and s0 != 0 and s0 not in heads:
        moves.append(LARC)
    if buf_nonempty:
        moves.append(RARC)
    if s0 != 0 and s0 in heads:
        moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, a):
    if a == SHIFT:
        stack.append(bptr); bptr += 1
    elif a == LARC:
        heads[stack[-1]] = bptr; stack.pop()
    elif a == RARC:
        heads[bptr] = stack[-1]; stack.append(bptr); bptr += 1
    elif a == REDU:
        stack.pop()
    return stack, bptr


def _move_costs_live(stack, bptr, n, gold, heads):
    costs = {}
    s0 = stack[-1]
    b0 = bptr if bptr <= n else None
    stack_set = set(stack)
    legal = _legal(stack, bptr, n, heads)
    for a in legal:
        if a == SHIFT:
            c = 0
            for k in stack:
                if gold[k] == b0: c += 1
            if 0 <= gold[b0] and gold[b0] in stack_set: c += 1
            costs[a] = c
        elif a == LARC:
            c = 0
            gh = gold[s0]
            if gh != b0 and (bptr + 1) <= gh <= n: c += 1
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
        elif a == RARC:
            c = 0
            gh = gold[b0]
            if gh != s0 and (gh in stack_set or (bptr + 1) <= gh <= n): c += 1
            for k in stack:
                if gold[k] == b0: c += 1
            costs[a] = c
        elif a == REDU:
            c = 0
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
    return costs


def _static_oracle_move(stack, bptr, n, gold, heads):
    costs = _move_costs_live(stack, bptr, n, gold, heads)
    for a in (LARC, RARC, REDU, SHIFT):
        if costs.get(a, 1) == 0:
            return a
    return min(costs, key=lambda k: costs[k]) if costs else SHIFT


def _score_actions(base_ids, W, legal):
    out = {}
    for a in legal:
        ids = (base_ids ^ ACT_SALT[a]) & MASK
        out[a] = float(W[ids].sum())
    return out


def _argmax_legal(scores):
    best_a = None; best = -1e18
    for a, s in scores.items():
        if s > best: best = s; best_a = a
    return best_a


def _perc_update(W, CW, base_ids, a_gold, a_pred, c):
    ig = (base_ids ^ ACT_SALT[a_gold]) & MASK
    ip = (base_ids ^ ACT_SALT[a_pred]) & MASK
    np.add.at(W, ig, 1.0); np.add.at(CW, ig, c)
    np.add.at(W, ip, -1.0); np.add.at(CW, ip, -c)


def _train_transition(train, seed, mode, lex):
    """Dynamic-oracle averaged-perceptron action classifier under a given feature MODE."""
    rng = np.random.default_rng(seed)
    W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        explore = ep >= EXPLORE_AFTER
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s)
            attr = _mk_attr(s)
            gold = [0] * (n + 1)
            for (i, w, p, h, dl, num) in s:
                gold[i] = h if 0 <= h <= n else 0
            stack = [0]; bptr = 1; heads = {}
            guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1:
                    break
                legal = _legal(stack, bptr, n, heads)
                if not legal:
                    break
                base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, mode, lex)),
                                       dtype=np.int64)
                scores = _score_actions(base_ids, W, legal)
                a_pred = _argmax_legal(scores)
                costs = _move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0]
                if not zero:
                    zero = [min(costs, key=lambda k: costs[k])]
                a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                    _perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                if explore and a_pred in legal and rng.random() < EXPLORE_P:
                    a_next = a_pred
                else:
                    a_next = a_orl
                stack, bptr = _apply(stack, bptr, heads, a_next)
                guard += 1
                if guard > 4 * (n + 2):
                    break
    return W - CW / c


def _decode_greedy(sent, attr, W, mode, lex):
    n = len(sent)
    stack = [0]; bptr = 1; heads = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _legal(stack, bptr, n, heads)
        if not legal:
            break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, mode, lex)),
                               dtype=np.int64)
        scores = _score_actions(base_ids, W, legal)
        a = _argmax_legal(scores)
        stack, bptr = _apply(stack, bptr, heads, a)
        guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0
    return heads


# ================================================================================================
# Corpus
# ================================================================================================
UD_DIR = REPO / "experiments" / "data" / "ud_english_ewt"


def _num_of(feats):
    for kv in feats.split("|"):
        if kv.startswith("Number="):
            v = kv.split("=", 1)[1]
            return v if v in ("Sing", "Plur") else None
    return None


def _load_ud_feats(split):
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split)
    sents = []; cur = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur: sents.append(cur); cur = []
                continue
            if line.startswith("#"): continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]: continue
            try:
                idx = int(c[0]); head = int(c[6])
            except Exception:
                continue
            cur.append((idx, c[1], c[3], head, c[7], _num_of(c[5])))
    if cur: sents.append(cur)
    return sents


def _first_noun_idx(sent):
    for (i, w, p, h, dl, num) in sent:
        if p in NOUN_POS: return i
    return None


def _classify_arc(sent, s_idx, v_idx, s_num):
    fn = _first_noun_idx(sent)
    subj_is_first = (fn == s_idx)
    lo, hi = min(s_idx, v_idx), max(s_idx, v_idx)
    diff_attractor = False
    if s_num is not None:
        for (i, w, p, h, dl, num) in sent:
            if lo < i < hi and p in NOUN_POS and num is not None and num != s_num:
                diff_attractor = True; break
    return (not subj_is_first) and diff_attractor, subj_is_first


def _subject_id(sents, head_fn):
    hb = tb = he = te = ha = ta = 0
    for sent in sents:
        n = len(sent)
        attr = _mk_attr(sent)
        heads = head_fn(sent, attr)
        for (i, w, p, h, dl, s_num) in sent:
            if not dl.startswith("nsubj"): continue
            v_idx = h
            if v_idx < 1 or v_idx > n: continue
            vtok = sent[v_idx - 1]
            if vtok[2] not in ("VERB", "AUX"): continue
            is_buried, is_easy = _classify_arc(sent, i, v_idx, s_num)
            corr = int(heads.get(i, -1) == v_idx)
            ha += corr; ta += 1
            if is_buried: hb += corr; tb += 1
            if is_easy: he += corr; te += 1
    return (hb / tb if tb else 0.0, he / te if te else 0.0, ha / ta if ta else 0.0, tb, te)


def _uas(sents, W, mode, lex):
    hit = tot = 0
    for sent in sents:
        attr = _mk_attr(sent)
        heads = _decode_greedy(sent, attr, W, mode, lex)
        for (i, w, p, h, dl, num) in sent:
            if h < 0 or h > len(sent): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


# ================================================================================================
# Self-test
# ================================================================================================
def _selftest():
    assert _h("abc") == _h("abc")
    assert _dist(1) == "1" and _dist(4) == "3-5" and _dist(20) == "11+"
    # shape
    assert _shape("Xerox") == "Xx"
    assert _shape("1234") == "d"
    assert _shape("iPhone-5s") == "xXx-dx"
    assert _shape("HELLO") == "X"
    # flags
    assert _flags("Apple") == "1000"
    assert _flags("APPLE") == "1100"
    assert _flags("a1") == "0010"
    assert _flags("co-op") == "0001"
    # base-mode features must be BYTE-IDENTICAL count/content to the base cell for a hand config.
    # tiny sentence "the(1) dog(2)" gold: 1->2 det, 2->0 root.
    sent = [(1, "the", "DET", 2, "det", None), (2, "dog", "NOUN", 0, "root", None)]
    attr = _mk_attr(sent)
    stack = [0, 1]; bptr = 2; heads = {}
    fb = _config_feats(stack, bptr, len(sent), attr, heads, M_BASE, None)
    # base returns exactly 22 templates (the base cell's fixed F list length).
    assert len(fb) == 22, "base-mode feature count %d != 22 (base parity broken)" % len(fb)
    assert fb[0] == "bias" and any(x.startswith("stksz:") for x in fb)
    # rich must be a strict SUPERSET of base (ONE-variable additivity).
    lex = {"clu": {"dog": 3, "the": 7}, "rank": {"dog": 5, "the": 1}, "n_vocab": 2, "n_clusters": 8}
    fr = _config_feats(stack, bptr, len(sent), attr, heads, M_RICH, lex)
    assert set(fb).issubset(set(fr)), "rich is not a superset of base (ONE-variable additivity broken)"
    assert len(fr) > len(fb), "rich added no features"
    fm = _config_feats(stack, bptr, len(sent), attr, heads, M_MORPH, lex)
    fc = _config_feats(stack, bptr, len(sent), attr, heads, M_CLUST, lex)
    assert set(fb).issubset(set(fm)) and set(fb).issubset(set(fc))
    # morph + clust groups partition the rich additions (no accidental overlap beyond base).
    morph_add = set(fm) - set(fb); clust_add = set(fc) - set(fb)
    assert morph_add and clust_add and not (morph_add & clust_add), "feature-group partition broken"
    assert set(fr) == set(fb) | morph_add | clust_add, "rich != base + morph + clust (ablation attribution unsound)"
    # cluster determinism: same word -> same cluster string.
    assert _clu_of("dog", lex) == "c3" and _clu_of("unseen", lex) == "cRARE"
    assert _fb_of("the", lex) == "0" and _fb_of("unseen", lex) == "OOV"

    # ---- arc-eager hand-trace (same as base cell; guards the mechanics copy) ----
    gold = [0, 2, 6, 5, 5, 2, 0, 9, 9, 6]
    n = 9
    stack = [0]; bptr = 1; heads = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        a = _static_oracle_move(stack, bptr, n, gold, heads)
        stack, bptr = _apply(stack, bptr, heads, a)
        guard += 1
        assert guard < 60, "hand-trace did not terminate"
    for i in range(1, n + 1):
        assert heads.get(i) == gold[i], "hand-trace head[%d]=%r != gold %d" % (i, heads.get(i), gold[i])
    assert heads[2] == 6 and heads[5] == 2, "subject-id trace wrong"

    # ---- k-means cluster builder: determinism + shape ----
    toy = [
        [(1, "the", "DET", 2, "det", None), (2, "cat", "NOUN", 3, "nsubj", None),
         (3, "sat", "VERB", 0, "root", None)],
        [(1, "a", "DET", 2, "det", None), (2, "dog", "NOUN", 3, "nsubj", None),
         (3, "ran", "VERB", 0, "root", None)],
    ]
    lx1 = _build_clusters(toy, K=2, V=10, iters=5)
    lx2 = _build_clusters(toy, K=2, V=10, iters=5)
    assert lx1["clu"] == lx2["clu"], "cluster builder non-deterministic"
    assert lx1["n_clusters"] >= 1

    # ---- loader parity ----
    try:
        base = load_conllu("dev"); mine = _load_ud_feats("dev")
        assert len(base) == len(mine), "loader sentence-count mismatch"
        for bs, ms in list(zip(base, mine))[:100]:
            assert len(bs) == len(ms)
            for bt, mt in zip(bs, ms):
                assert tuple(bt) == tuple(mt[:5]), "loader field mismatch"
        print("[selftest] loader parity OK (%d sents)" % len(mine), flush=True)
    except FileNotFoundError:
        print("[selftest] WARN: UD corpus not found at self-test (checked at runtime)", flush=True)
    print("[selftest] PASS: richfeat parser (shape/flags/cluster + base-superset + hand-trace + kmeans)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ================================================================================================
# Runner scaffolding
# ================================================================================================
def _write_start_marker(output_dir, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "run_mode": RUN_MODE}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _hb(output_dir, msg):
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}) + "\n")
    except Exception:
        pass


def run(out_dir):
    try:
        train = _load_ud_feats("train"); dev = _load_ud_feats("dev"); test = _load_ud_feats("test")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True)
        return {"error": "corpus_load_failed"}
    train = [s for s in train if 1 <= len(s) <= MAXLEN]
    dev = [s for s in dev if 1 <= len(s) <= MAXLEN]
    test = [s for s in test if 1 <= len(s) <= MAXLEN]
    if SMOKE:
        train = train[:400]; dev = dev[:150]
        pool = (dev + test)[:600]
        SEEDS = [1, 2]
    else:
        pool = dev + test
        SEEDS = [1, 2, 3]
    print("[data] train=%d dev=%d pool=%d MAXLEN=%d EPOCHS=%d seeds=%s" % (
        len(train), len(dev), len(pool), MAXLEN, EPOCHS, SEEDS), flush=True)
    _hb(out_dir, "data loaded")

    def mean(x): return round(sum(x) / len(x), 4) if x else 0.0

    def se(x):
        if len(x) < 2: return 0.0
        m = sum(x) / len(x); v = sum((z - m) ** 2 for z in x) / len(x)
        return (v ** 0.5) / (len(x) ** 0.5)

    # -------- CLUSTER model (built on TRAIN only; used by clust/rich arms) --------
    t = time.time()
    lex = _build_clusters(train)
    print("[cluster] built n_vocab=%d n_clusters=%d %.1fs" % (lex["n_vocab"], lex["n_clusters"], time.time() - t),
          flush=True)
    _hb(out_dir, "clusters built")

    # -------- ARM_BASE_FEAT + ARM_RICH_FEAT (multi-seed) --------
    base_uas = []; rich_uas = []
    rich_sid_b = []; base_sid_b = []
    W_base_seed1 = None; W_rich_seed1 = None
    arms_differ_base_rich = False
    for sd in SEEDS:
        t = time.time()
        W_b = _train_transition(train, sd, M_BASE, lex)
        u_b = round(_uas(dev, W_b, M_BASE, lex), 4); base_uas.append(u_b)
        _hb(out_dir, "seed %d base done %.1fs uas=%.4f" % (sd, time.time() - t, u_b))
        t = time.time()
        W_r = _train_transition(train, sd, M_RICH, lex)
        u_r = round(_uas(dev, W_r, M_RICH, lex), 4); rich_uas.append(u_r)
        sb_r, _, _, _, _ = _subject_id(pool, lambda s, a: _decode_greedy(s, a, W_r, M_RICH, lex))
        sb_b, _, _, n_buried, n_easy = _subject_id(pool, lambda s, a: _decode_greedy(s, a, W_b, M_BASE, lex))
        rich_sid_b.append(sb_r); base_sid_b.append(sb_b)
        if not np.array_equal(W_b, W_r): arms_differ_base_rich = True
        if sd == SEEDS[0]:
            W_base_seed1 = W_b; W_rich_seed1 = W_r
        print("  seed %d: BASE-UAS=%.4f RICH-UAS=%.4f (d=%+.4f) | rich buried-sid=%.4f (%.1fs)" % (
            sd, u_b, u_r, u_r - u_b, sb_r, time.time() - t), flush=True)
        _hb(out_dir, "seed %d rich done uas=%.4f" % (sd, u_r))

    # -------- ABLATION (seed 1 only): base+morph, base+clust -- attribute the lift --------
    abl = {}
    if DO_ABLATION:
        t = time.time()
        W_m = _train_transition(train, SEEDS[0], M_MORPH, lex)
        u_m = round(_uas(dev, W_m, M_MORPH, lex), 4)
        W_c = _train_transition(train, SEEDS[0], M_CLUST, lex)
        u_c = round(_uas(dev, W_c, M_CLUST, lex), 4)
        abl = {"base_plus_morph_uas": u_m, "base_plus_clust_uas": u_c,
               "morph_lift_over_base_seed1": round(u_m - base_uas[0], 4),
               "clust_lift_over_base_seed1": round(u_c - base_uas[0], 4)}
        print("  [ablation seed1] base=%.4f  +morph=%.4f (%+.4f)  +clust=%.4f (%+.4f)  rich=%.4f (%+.4f)" % (
            base_uas[0], u_m, u_m - base_uas[0], u_c, u_c - base_uas[0], rich_uas[0], rich_uas[0] - base_uas[0]),
            flush=True)
        _hb(out_dir, "ablation done morph=%.4f clust=%.4f" % (u_m, u_c))

    # -------- LEARNING CURVE (rich arm, seed 1) --------
    lc = {}
    if DO_LC:
        rng = np.random.default_rng(999)
        perm = rng.permutation(len(train))
        for fr in LC_FRACS:
            k = max(1, int(round(fr * len(train))))
            sub = [train[i] for i in perm[:k]]
            Wl = _train_transition(sub, SEEDS[0], M_RICH, lex)
            ul = round(_uas(dev, Wl, M_RICH, lex), 4)
            lc["%.2f" % fr] = {"n_train": k, "uas": ul}
            print("  [learning-curve rich] frac=%.2f n=%d UAS=%.4f" % (fr, k, ul), flush=True)
            _hb(out_dir, "LC frac %.2f uas=%.4f" % (fr, ul))

    b_mean = mean(base_uas); r_mean = mean(rich_uas)
    r_se = se(rich_uas)
    lc_lo = lc.get("%.2f" % LC_FRACS[0], {}).get("uas", 0.0)
    lc_hi = lc.get("%.2f" % LC_FRACS[-1], {}).get("uas", 0.0)
    out = {
        "n_seeds": len(SEEDS), "n_train": len(train), "n_dev": len(dev), "n_pool": len(pool),
        "n_buried": n_buried, "n_easy": n_easy,
        "n_clusters": lex["n_clusters"], "cluster_vocab": lex["n_vocab"],
        "cluster_method": "distributional_kmeans_leftright_coarsePOS_proxy_NOT_full_brown",
        "batch_local_uas_cited": 0.7864, "base_dynamic_uas_cited": 0.8109,
        "base_uas_mean": b_mean, "base_uas_vals": base_uas,
        "rich_uas_mean": r_mean, "rich_uas_vals": rich_uas,
        "rich_uas_se": round(r_se, 4), "rich_uas_mean_minus_2se": round(r_mean - 2 * r_se, 4),
        "rich_minus_base": round(r_mean - b_mean, 4),
        "rich_2se_lo_minus_base_mean": round((r_mean - 2 * r_se) - b_mean, 4),
        "base_buried_sid_mean": mean(base_sid_b), "rich_buried_sid_mean": mean(rich_sid_b),
        "ablation": abl,
        "learning_curve": lc, "lc_lo_uas": lc_lo, "lc_hi_uas": lc_hi, "lc_rise": round(lc_hi - lc_lo, 4),
        "lc_points": len(lc), "lc_expected_points": (len(LC_FRACS) if DO_LC else 0),
        "arms_differ_base_vs_rich": arms_differ_base_rich,
        "gate_d_base_reproduces_prior": bool(abs(b_mean - 0.8109) <= 0.02) if not SMOKE else None,
    }
    print("\n  === SUMMARY (mean over %d seeds) ===" % len(SEEDS), flush=True)
    print("  UAS:  BASE=%.4f (vals=%s)  RICH=%.4f (vals=%s, 2SE-lo=%.4f)  d=%+.4f  (batch~0.79, base-cell 0.8109)" % (
        b_mean, base_uas, r_mean, rich_uas, out["rich_uas_mean_minus_2se"], out["rich_minus_base"]), flush=True)
    print("  rich_2SE_lo - base_mean = %+.4f (>=0.03 for HARD_PASS)" % out["rich_2se_lo_minus_base_mean"], flush=True)
    print("  buried subject-id: base=%.4f rich=%.4f (n_buried=%d)" % (
        out["base_buried_sid_mean"], out["rich_buried_sid_mean"], n_buried), flush=True)
    if lc:
        print("  learning curve (rich): %.4f -> %.4f rise=%+.4f" % (lc_lo, lc_hi, out["lc_rise"]), flush=True)
    return out


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r.get("n_buried", 0) == 0:
        return ("UNKNOWN", "UNKNOWN: discriminator did not fire (n_buried==0)")
    if r.get("lc_expected_points", 0) and r.get("lc_points", 0) < r["lc_expected_points"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: learning-curve points %d < expected %d" % (
            r["lc_points"], r["lc_expected_points"]))
    # Gate D: base-feat arm must reproduce the prior dynamic UAS at THIS regime (full only).
    if r.get("gate_d_base_reproduces_prior") is False:
        return ("UNKNOWN", "UNKNOWN_GATE_D: base-feat arm UAS=%.4f did NOT reproduce prior dynamic 0.8109 within "
                "tol 0.02 -- feature plumbing suspect, rich comparison untrustworthy. %s" % (
                    r["base_uas_mean"], _sfx(r)))
    b = r["base_uas_mean"]; rm = r["rich_uas_mean"]; r2 = r["rich_uas_mean_minus_2se"]
    s = _sfx(r)
    if rm <= b:
        return ("HARD_FAIL", "HARD_FAIL: rich UAS (%.4f) <= base UAS (%.4f) -- rich features do not help. %s" % (rm, b, s))
    if r2 <= b:
        return ("HARD_FAIL", "HARD_FAIL: rich CI overlaps base (rich 2SE-lo=%.4f <= base mean=%.4f) -- no real lift. %s"
                % (r2, b, s))
    if (r2 - b) >= 0.03 and r["lc_rise"] >= 0.02:
        return ("HARD_PASS", "HARD_PASS: rich-feature library lifts transition-parser UAS by a REAL 2SE-clean margin "
                "(rich 2SE-lo - base mean = %+.4f >= 0.03) with the learning curve intact (rise=%+.4f). %s" % (
                    r2 - b, r["lc_rise"], s))
    return ("MIDDLE_BAND", "MIDDLE_BAND: rich features lift UAS above base (2SE-clean) but below the +0.03 crown bar "
            "(rich 2SE-lo - base mean = %+.4f). %s" % (r2 - b, s))


def _sfx(r):
    ab = r.get("ablation", {})
    return ("UAS base=%.4f rich=%.4f (2SE-lo=%.4f, base_vals=%s rich_vals=%s) | d=%+.4f | "
            "ablation +morph=%s(%s) +clust=%s(%s) | buried-sid base=%.4f rich=%.4f (n=%d) | "
            "LC rise=%+.4f | clusters=%s" % (
                r["base_uas_mean"], r["rich_uas_mean"], r["rich_uas_mean_minus_2se"],
                r["base_uas_vals"], r["rich_uas_vals"], r["rich_minus_base"],
                ab.get("base_plus_morph_uas"), ab.get("morph_lift_over_base_seed1"),
                ab.get("base_plus_clust_uas"), ab.get("clust_lift_over_base_seed1"),
                r["base_buried_sid_mean"], r["rich_buried_sid_mean"], r["n_buried"],
                r["lc_rise"], r["n_clusters"]))


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
_write_start_marker(out_dir, expected_n_units=(2 if SMOKE else 3))
t0 = time.time()
try:
    r = run(out_dir)
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
               "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": [r],
               "elapsed_s": time.time() - t0,
               "arms_differ_verified": bool(r.get("arms_differ_base_vs_rich", False)),
               "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "discrete parse accuracy, no noise floor",
               "cardinality_ok": True}
    metrics.update(r)
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written -> %s" % os.path.join(out_dir, "metrics.json"), flush=True)
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(out_dir, e)
    raise
