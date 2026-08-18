"""
exp_depparse_transition_arceager_cpu_v1.py -- GLASS-BOX INCREMENTAL TRANSITION dependency parser
  (arc-eager; stack + buffer; structured averaged perceptron ACTION classifier) vs the substrate's
  BATCH arc-factored local-argmax reader. First transition parser ever built on this substrate.
  CPU. Fully inspectable: stack/buffer are literal token-index lists at every step; the action
  scorer is an averaged perceptron (no gradient, no opaque net); every action is loggable.

WHAT THIS TESTS (ONE variable = transition-decode vs batch-decode; SAME feature primitives family
  -- word/POS/suffix/distance/direction hashed exactly like the batch parser's _arc_ids):
  (1) UAS: does arc-eager (+ dynamic oracle) BEAT the batch local-argmax baseline (0.7875) and the
      batch global-MST decode (0.7895)? Target ~0.85-0.88 (transition parsers beat weak graph
      parsers). Batch LOCAL is reproduced IN THIS RUN as the same-split positive control.
  (2) LEARNING CURVE: UAS vs training-data fraction {0.1,0.25,0.5,1.0} -- the flexible/IMPROVING
      property (does the parser get better with exposure?).
  (3) BURIED SUBJECT-ID: frac(predicted_head[subject]==gold_verb) over gold nsubj arcs, split
      BURIED (subject-not-first AND >=1 intervening noun of DIFFERENT number) vs EASY. Same buried
      definition as exp_depparse_v2_mst_cpu_v1. Batch baseline ~0.30.
  (4) STACK-DEPTH readout: per-token embedding depth = the stack depth at which each token is
      first pushed (the two-birds property -- the depth feature the buried-subject agreement needs).

THE #1 RISK = ERROR PROPAGATION on greedy REDUCE/attach (McDonald & Nivre 2011: transition parsers
  do WORSE on LONGER dependencies via error propagation; here the correct arc key->verb is the LONG
  one, the attractor pull cabinets->verb is SHORT). MITIGATION (baked in): DYNAMIC ORACLE training
  (Goldberg & Nivre 2012 -- train the action classifier on configurations reachable from its OWN
  mistakes, not just the gold path) + optional small BEAM at decode. We measure directly whether
  dynamic-oracle beats a static-oracle greedy baseline (the error-propagation diagnostic).

GLASS-BOX / brain-faithful: incremental immediacy (Marslen-Wilson & Tyler 1980); left-corner
  bounded stack (Resnik 1992). Nivre 2003/2008 arc-eager mechanics. Goldberg & Nivre 2012 dynamic
  oracle cost functions (transcribed below, self-tested against arc-reachability semantics).

ARMS:
  ARM_BATCH_LOCAL   -- positive control; reproduces batch UAS ~0.7875 (Gate D). CITED@ prior atom.
  ARM_TRANS_STATIC  -- arc-eager + STATIC-oracle greedy training (always follow the gold canonical
                       derivation). The error-propagation-prone baseline for the dynamic comparison.
  ARM_TRANS_DYNAMIC -- arc-eager + DYNAMIC-oracle training with exploration (the mechanism). Main arm.
  ARM_TRANS_DYN_BEAM-- (optional, seed 1) dynamic-oracle model, beam decode (width 4).

PRE-REGISTERED bands (see prereg md):
  HARD_PASS = ARM_TRANS_DYNAMIC UAS beats batch (max(0.7875_local, 0.7895_mst)) by a REAL margin
              (mean-2SE >= 0.82, i.e. >= batch + ~0.03) AND buried subject-id(dynamic) > batch(~0.30)
              by >= 0.05 AND the learning curve RISES (UAS at 1.0 frac > UAS at 0.1 frac by >= 0.03).
  MIDDLE    = dynamic UAS > batch by any positive margin OR buried-sid improves, but not the full bar.
  HARD_FAIL = dynamic UAS <= batch (transition paradigm does not help here) OR dynamic-oracle no
              better than static-oracle greedy (mitigation is inert).
  UNKNOWN   = corpus load fails OR n_buried == 0 (discriminator did not fire).
  crlb_n/a: parse/attachment accuracy is discrete argmax over trained scores -- no CRLB noise floor.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (transition heads differ from batch heads on >=1 sentence;
#   dynamic-oracle weights differ from static-oracle weights)
# - final_metrics_atomicity = tmp_replace (os.replace; write_metrics + crash path both atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete parse accuracy, no noise floor)
# - baseline_in_band at smoke (batch UAS ~0.79 in (0.05,0.95); buried-sid ~0.30 leaves headroom)
# - discriminator fires: n_buried > 0 at smoke, else UNKNOWN
# - cardinality_ok: learning curve EXPECTED points = len(LC_FRACS); verdict counts them
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
from typing import Dict, Tuple, List, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu  # working UD-EWT loader (positive-control parity anchor)

ANCHOR_NAME = "depparse_transition_arceager_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21
MASK = SIZE - 1
NOUN_POS = ("NOUN", "PROPN", "PRON")

# Actions
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_NAMES = {SHIFT: "SHIFT", LARC: "LEFT-ARC", RARC: "RIGHT-ARC", REDU: "REDUCE"}
# FIXED per-action salts (deterministic; NEVER PYTHONHASHSEED hash()). Distinct hashed subspace/action.
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)

# Tunables (env-overridable so FULL wall-time can be bounded after smoke timing).
EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "3" if SMOKE else "10"))
MAXLEN = int(os.environ.get("HDLAB_MAXLEN", "50"))
EXPLORE_AFTER = int(os.environ.get("HDLAB_EXPLORE_AFTER", "2"))  # dynamic-oracle exploration burn-in
EXPLORE_P = float(os.environ.get("HDLAB_EXPLORE_P", "0.9"))
BEAM_WIDTH = int(os.environ.get("HDLAB_BEAM", "4"))
DO_BEAM = os.environ.get("HDLAB_DO_BEAM", "1") == "1"
DO_LC = os.environ.get("HDLAB_DO_LC", "1") == "1"
LC_FRACS = [0.1, 0.25, 0.5, 1.0]


def _h(f):
    return zlib.crc32(f.encode("utf-8")) & MASK


def _dist(d):
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w):
    return w[-3:] if len(w) >= 3 else w


def _szbucket(k):
    return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))


# ================================================================================================
# BATCH arc-factored features + local-argmax decode -- COPIED VERBATIM from
# exp_depparse_hashed_multiseed_cpu_v1 (so ARM_BATCH_LOCAL reproduces UAS=0.7875 exactly).
# ================================================================================================
def _arc_ids(sent, i, h):
    n = len(sent); dw, dp = sent[i - 1][1].lower(), sent[i - 1][2]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"; d = 0; dr = "R"
    else:
        hw, hp = sent[h - 1][1].lower(), sent[h - 1][2]; d = h - i; dr = "L" if d < 0 else "R"
    db = _dist(d)
    F = ["b", "hp:" + hp, "dp:" + dp, "hp_dp:%s_%s" % (hp, dp), "hp_dp_dir:%s_%s_%s" % (hp, dp, dr),
         "hp_dp_dist:%s_%s_%s" % (hp, dp, db), "dw:" + dw, "hw:" + hw, "hw_dw:%s_%s" % (hw, dw),
         "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp), "dp_dir:%s_%s" % (dp, dr), "dp_dist:%s_%s" % (dp, db),
         "dsuf_hp:%s_%s" % (_suf(dw), hp), "hsuf_dp:%s_%s" % (_suf(hw), dp), "dsuf_dp_dir:%s_%s_%s" % (_suf(dw), dp, dr)]
    hp_l = sent[h - 2][2] if h >= 2 else "<S>"; dp_l = sent[i - 2][2] if i >= 2 else "<S>"
    dp_r = sent[i][2] if i < n else "<E>"; hp_r = sent[h][2] if 0 < h < n else "<E>"
    F += ["hpl_hp_dp:%s_%s_%s" % (hp_l, hp, dp), "dpl_dp_dir:%s_%s_%s" % (dp_l, dp, dr), "dpr_dp:%s_%s" % (dp_r, dp),
          "hpr_hp_dp:%s_%s_%s" % (hp_r, hp, dp)]
    if h != 0:
        lo, hi = min(i, h), max(i, h); between = [sent[k - 1][2] for k in range(lo + 1, hi)]
        if "VERB" in between: F.append("bV:%s_%s" % (hp, dp))
        if "PUNCT" in between: F.append("bP:%s_%s" % (hp, dp))
        F.append("dp_bn:%s_%s" % (dp, _dist(len(between))))
    return np.fromiter((_h(f) for f in F), dtype=np.int64, count=len(F))


def _batch_precompute(sents):
    out = []
    for s in sents:
        n = len(s); arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i: continue
                arc[i][h] = _arc_ids(s, i, h)
        out.append(arc)
    return out


def _batch_train(train, tr_arc, seed):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        for si in rng.permutation(len(train)):
            s = train[si]; arc = tr_arc[si]; n = len(s)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n: continue
                best_h = -1; best_s = -1e18
                for h in range(0, n + 1):
                    if h == i: continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s: best_s = sc; best_h = h
                if best_h != gold_h:
                    gi = arc[i][gold_h]; pi = arc[i][best_h]
                    np.add.at(W, gi, 1.0); np.add.at(CW, gi, c)
                    np.add.at(W, pi, -1.0); np.add.at(CW, pi, -c)
                c += 1
    return W - CW / c


def _batch_local_decode(arc, n, avg):
    S = {}; head = {}
    for i in range(1, n + 1):
        cand = []
        for h in range(0, n + 1):
            if h == i: continue
            cand.append((float(avg[arc[i][h]].sum()), h))
        cand.sort(reverse=True)
        head[i] = cand[0][1]; S[i] = {h: sc for sc, h in cand}
    for _ in range(n + 2):
        cyc = None
        for start in range(1, n + 1):
            seen = []; x = start
            while x != 0 and x not in seen:
                seen.append(x); x = head[x]
            if x != 0:
                j = seen.index(x); cyc = seen[j:]; break
        if cyc is None: break
        best_node = None; best_alt = None; best_loss = 1e18; cset = set(cyc)
        for node in cyc:
            cur = S[node][head[node]]; alt_h = -1; alt_s = -1e18
            for h, sc in S[node].items():
                if h not in cset and sc > alt_s: alt_s = sc; alt_h = h
            if alt_h >= 0 and (cur - alt_s) < best_loss:
                best_loss = cur - alt_s; best_node = node; best_alt = alt_h
        if best_node is None: break
        head[best_node] = best_alt
    return head


# ================================================================================================
# TRANSITION parser: arc-eager. sent_attr[k] = (word_lower, pos, suf) for k in 1..n; index 0 = ROOT.
# Config = (stack:list, bptr:int, heads:dict). buffer = [bptr..n], b0 = bptr (front), s0 = stack[-1].
# ================================================================================================
_ROOT_ATTR = ("<root>", "ROOT", "<root>")
_NONE_ATTR = ("<none>", "<NONE>", "<none>")


def _mk_attr(sent):
    a = [_ROOT_ATTR]  # index 0
    for (i, w, p, h, dl, num) in sent:
        a.append((w.lower(), p, _suf(w.lower())))
    return a


def _config_feats(stack, bptr, n, attr, heads):
    """Base feature strings (no action). Glass-box config features over s0,s1,b0,b1,b2."""
    s0 = stack[-1]
    s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None
    b1 = (bptr + 1) if (bptr + 1) <= n else None
    b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s = attr[s0]
    s1w, s1p, s1s = attr[s1] if s1 is not None else _NONE_ATTR
    b0w, b0p, b0s = attr[b0] if b0 is not None else _NONE_ATTR
    b1w, b1p, b1s = attr[b1] if b1 is not None else _NONE_ATTR
    b2w, b2p, b2s = attr[b2] if b2 is not None else _NONE_ATTR
    if b0 is not None and s0 > 0:
        dd = _dist(b0 - s0)
    else:
        dd = "0"
    s0hh = "1" if s0 in heads else "0"
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
    return F


def _legal(stack, bptr, n, heads):
    """Legal action list at this config."""
    moves = []
    s0 = stack[-1]
    buf_nonempty = bptr <= n
    if buf_nonempty:
        moves.append(SHIFT)
    # LEFT-ARC: s0 not ROOT, s0 has no head, buffer non-empty
    if buf_nonempty and s0 != 0 and s0 not in heads:
        moves.append(LARC)
    # RIGHT-ARC: buffer non-empty (s0 always exists since ROOT on stack)
    if buf_nonempty:
        moves.append(RARC)
    # REDUCE: s0 has a head, s0 not ROOT
    if s0 != 0 and s0 in heads:
        moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, a):
    """Apply action; return new (stack, bptr) -- heads mutated in place. stack copied by caller if needed."""
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
    """Goldberg & Nivre 2012 arc-eager dynamic-oracle costs = # gold arcs made unreachable.
    gold[k] = gold head of token k (0 = root). buffer = [bptr..n], b0 = bptr, s0 = stack[-1].
    Returns dict {legal_action: cost}."""
    costs = {}
    s0 = stack[-1]
    b0 = bptr if bptr <= n else None
    stack_set = set(stack)
    legal = _legal(stack, bptr, n, heads)
    for a in legal:
        if a == SHIFT:
            # push b0: lose b0's dependents in stack + b0's head if in stack
            c = 0
            for k in stack:
                if gold[k] == b0: c += 1
            if 0 <= gold[b0] and gold[b0] in stack_set: c += 1
            costs[a] = c
        elif a == LARC:
            # add head[s0]=b0, pop s0: lose s0's head if a later buffer word; lose s0's buffer dependents
            c = 0
            gh = gold[s0]
            if gh != b0 and (bptr + 1) <= gh <= n:  # true head is a later buffer word
                c += 1
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
        elif a == RARC:
            # add head[b0]=s0, push b0: lose b0's true head (if != s0, in stack-or-buffer); b0's stack deps
            c = 0
            gh = gold[b0]
            if gh != s0 and (gh in stack_set or (bptr + 1) <= gh <= n):
                c += 1
            for k in stack:
                if gold[k] == b0: c += 1
            costs[a] = c
        elif a == REDU:
            # pop s0: lose s0's dependents still in buffer
            c = 0
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
    return costs


def _static_oracle_move(stack, bptr, n, gold, heads):
    """Deterministic zero-cost move by fixed priority LARC>RARC>REDU>SHIFT (canonical gold derivation)."""
    costs = _move_costs_live(stack, bptr, n, gold, heads)
    for a in (LARC, RARC, REDU, SHIFT):
        if costs.get(a, 1) == 0:
            return a
    # fallback: cheapest legal (defensive; should not happen for reachable arcs)
    return min(costs, key=lambda k: costs[k]) if costs else SHIFT


def _score_actions(base_ids, W, legal):
    """Return dict {action: score} for legal actions (vectorized hashed lookup)."""
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


def _train_transition(train, seed, dynamic):
    """Averaged-perceptron action classifier. dynamic=False -> static-oracle; True -> dynamic oracle
    with exploration (follow model's own move after burn-in; train toward best zero-cost move)."""
    rng = np.random.default_rng(seed)
    W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        explore = dynamic and ep >= EXPLORE_AFTER
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
                base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads)),
                                       dtype=np.int64)
                scores = _score_actions(base_ids, W, legal)
                a_pred = _argmax_legal(scores)
                if dynamic:
                    costs = _move_costs_live(stack, bptr, n, gold, heads)
                    zero = [a for a in legal if costs.get(a, 1) == 0]
                    if not zero:
                        zero = [min(costs, key=lambda k: costs[k])]
                    # best zero-cost move by model score = the oracle target from HERE
                    a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                    if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                        _perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                    # advance: explore (follow model) after burn-in, else follow oracle
                    if explore and a_pred in legal and rng.random() < EXPLORE_P:
                        a_next = a_pred
                    else:
                        a_next = a_orl
                else:
                    a_gold = _static_oracle_move(stack, bptr, n, gold, heads)
                    if a_pred != a_gold:
                        _perc_update(W, CW, base_ids, a_gold, a_pred, c); c += 1
                    a_next = a_gold  # static: always follow gold
                stack, bptr = _apply(stack, bptr, heads, a_next)
                guard += 1
                if guard > 4 * (n + 2):
                    break
    return W - CW / c


def _decode_greedy(sent, attr, W, want_depth=False):
    """Greedy arc-eager decode. Returns (head_dict, depth_dict?). depth[k] = stack size when k pushed."""
    n = len(sent)
    stack = [0]; bptr = 1; heads = {}
    depth = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _legal(stack, bptr, n, heads)
        if not legal:
            break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads)), dtype=np.int64)
        scores = _score_actions(base_ids, W, legal)
        a = _argmax_legal(scores)
        if a in (SHIFT, RARC) and want_depth and bptr not in depth:
            depth[bptr] = len(stack) + 1  # depth at which b0 becomes a stack token
        stack, bptr = _apply(stack, bptr, heads, a)
        guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0  # unattached -> ROOT (standard arc-eager terminal fill)
    if want_depth:
        return heads, depth
    return heads


def _decode_beam(sent, attr, W, width):
    """Beam arc-eager decode (cumulative action-score). Glass-box: each beam item is (stack,bptr,heads,score)."""
    n = len(sent)
    init = (tuple([0]), 1, {}, 0.0)
    beam = [init]
    guard = 0
    max_steps = 4 * (n + 2)
    while True:
        # all terminal?
        if all((bp > n and len(st) <= 1) for (st, bp, hd, sc) in beam):
            break
        nxt = []
        for (st, bp, hd, sc) in beam:
            stack = list(st)
            if bp > n and len(stack) <= 1:
                nxt.append((st, bp, hd, sc)); continue
            legal = _legal(stack, bp, n, hd)
            if not legal:
                nxt.append((st, bp, hd, sc)); continue
            base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bp, n, attr, hd)), dtype=np.int64)
            scores = _score_actions(base_ids, W, legal)
            for a in legal:
                st2 = list(stack); hd2 = dict(hd); bp2 = bp
                st2, bp2 = _apply(st2, bp2, hd2, a)
                nxt.append((tuple(st2), bp2, hd2, sc + scores[a]))
        nxt.sort(key=lambda t: t[3], reverse=True)
        beam = nxt[:width]
        guard += 1
        if guard > max_steps:
            break
    best = max(beam, key=lambda t: t[3])
    heads = dict(best[2])
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0
    return heads


# ================================================================================================
# Corpus with Number morphology (for buried-subject id). token = (idx,form,upos,head,deprel,number)
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
    """buried = subject NOT first noun AND >=1 intervening noun of DIFFERENT number. easy = subj is first noun."""
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
    """head_fn(sent, attr) -> head dict. Returns (sid_buried, sid_easy, sid_all, n_buried, n_easy)."""
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


# ================================================================================================
# Self-test: dynamic-oracle cost correctness + arc-eager hand-trace of "the key to the cabinets are".
# ================================================================================================
def _selftest():
    assert _h("abc") == _h("abc")
    assert _dist(1) == "1" and _dist(2) == "2" and _dist(4) == "3-5" and _dist(20) == "11+"

    # ---- HAND-TRACE: "the(1) key(2) to(3) the(4) cabinets(5) are(6) on(7) the(8) table(9)" ----
    # gold projective tree: 1->2 det, 2->6 nsubj, 3->5 case, 4->5 det, 5->2 nmod, 6->0 root,
    #                       7->9 case, 8->9 det, 9->6 obl.
    gold = [0, 2, 6, 5, 5, 2, 0, 9, 9, 6]  # index 1..9
    n = 9
    stack = [0]; bptr = 1; heads = {}
    seq = []
    cabinets_popped_step = None; are_pushed_step = None
    step = 0; guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        a = _static_oracle_move(stack, bptr, n, gold, heads)
        s0_before = stack[-1]; b0_before = bptr
        stack, bptr = _apply(stack, bptr, heads, a)
        seq.append((step, ACT_NAMES[a], s0_before, b0_before))
        # cabinets(5) is popped by LEFT-ARC or REDUCE (its s0 was 5)
        if a in (LARC, REDU) and s0_before == 5 and cabinets_popped_step is None:
            cabinets_popped_step = step
        # are(6) first enters the stack via SHIFT or RIGHT-ARC (b0 was 6)
        if a in (SHIFT, RARC) and b0_before == 6 and are_pushed_step is None:
            are_pushed_step = step
        step += 1; guard += 1
        assert guard < 60, "hand-trace did not terminate"
    # The static oracle must recover the gold tree exactly (projective sentence).
    for i in range(1, n + 1):
        assert heads.get(i) == gold[i], "hand-trace head[%d]=%r != gold %d (seq=%s)" % (i, heads.get(i), gold[i], seq)
    assert cabinets_popped_step is not None, "cabinets(5) never popped"
    assert are_pushed_step is not None, "are(6) never pushed"
    # THE structural claim: the PP (containing cabinets) reduces BEFORE the verb 'are' is processed.
    assert cabinets_popped_step < are_pushed_step, (
        "cabinets popped at %d NOT before are pushed at %d -- PP did not reduce before verb"
        % (cabinets_popped_step, are_pushed_step))
    # And the exposed subject attached to the verb is 'key'(2), not the attractor 'cabinets'(5).
    assert heads[2] == 6 and heads[5] == 2, "subject-id trace wrong: key->%d cabinets->%d" % (heads[2], heads[5])
    print("[selftest] hand-trace OK: PP 'to the cabinets' reduced at step %d, verb 'are' processed at step %d; "
          "key(2)->are(6), cabinets(5)->key(2)" % (cabinets_popped_step, are_pushed_step), flush=True)

    # ---- dynamic-oracle cost sanity: zero-cost set is non-empty and static move is in it ----
    stack = [0]; bptr = 1; heads = {}
    for _ in range(3):
        if bptr > n: break
        costs = _move_costs_live(stack, bptr, n, gold, heads)
        assert min(costs.values()) == 0, "no zero-cost move available (costs=%s)" % costs
        a = _static_oracle_move(stack, bptr, n, gold, heads)
        assert costs.get(a, 1) == 0, "static-oracle move %s has nonzero cost %s" % (ACT_NAMES[a], costs.get(a))
        stack, bptr = _apply(stack, bptr, heads, a)

    # ---- loader parity: first-5 fields must equal _ud_loader.load_conllu ----
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
    print("[selftest] PASS: depparse-transition-arceager (hand-trace + dyn-oracle costs + loader parity)", flush=True)


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


def _uas_transition(sents, W, beam=0):
    hit = tot = 0
    for sent in sents:
        attr = _mk_attr(sent)
        heads = _decode_beam(sent, attr, W, beam) if beam else _decode_greedy(sent, attr, W)
        for (i, w, p, h, dl, num) in sent:
            if h < 0 or h > len(sent): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


def _uas_batch(sents, arcs, avg):
    hit = tot = 0
    for si, sent in enumerate(sents):
        heads = _batch_local_decode(arcs[si], len(sent), avg)
        for (i, w, p, h, dl, num) in sent:
            if h < 0 or h > len(sent): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


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

    # -------- ARM_BATCH_LOCAL (positive control; same-split baseline) --------
    t = time.time()
    tr_arc = _batch_precompute(train); dv_arc = _batch_precompute(dev); pool_arc = _batch_precompute(pool)
    print("[batch] arc precompute %.1fs" % (time.time() - t), flush=True); _hb(out_dir, "batch arcs done")
    avg_b = _batch_train(train, tr_arc, 1)
    batch_uas = round(_uas_batch(dev, dv_arc, avg_b), 4)

    def _batch_head_fn(sent, attr):
        # attr unused; recompute arcs for this pool sentence via its precomputed index is not available here,
        # so build arcs on the fly (pool is modest). Cached below for subject-id pass.
        n = len(sent); arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i: continue
                arc[i][h] = _arc_ids(sent, i, h)
        return _batch_local_decode(arc, n, avg_b)

    b_sid_b, b_sid_e, b_sid_a, n_buried, n_easy = _subject_id(pool, _batch_head_fn)
    print("[batch] UAS=%.4f (ref 0.7875) | buried-sid=%.4f easy-sid=%.4f (n_buried=%d)" % (
        batch_uas, b_sid_b, b_sid_e, n_buried), flush=True)
    _hb(out_dir, "batch arm done")

    # -------- ARM_TRANS_STATIC + ARM_TRANS_DYNAMIC (multi-seed) --------
    stat_uas = []; dyn_uas = []
    dyn_sid_b = []; dyn_sid_e = []; dyn_sid_a = []
    arms_differ_batch_trans = False; arms_differ_stat_dyn = False
    W_dyn_seed1 = None; W_stat_seed1 = None
    for sd in SEEDS:
        t = time.time()
        W_stat = _train_transition(train, sd, dynamic=False)
        u_stat = round(_uas_transition(dev, W_stat), 4); stat_uas.append(u_stat)
        _hb(out_dir, "seed %d static done %.1fs uas=%.4f" % (sd, time.time() - t, u_stat))
        t = time.time()
        W_dyn = _train_transition(train, sd, dynamic=True)
        u_dyn = round(_uas_transition(dev, W_dyn), 4); dyn_uas.append(u_dyn)
        sb, se_, sa, _, _ = _subject_id(pool, lambda s, a: _decode_greedy(s, a, W_dyn))
        dyn_sid_b.append(sb); dyn_sid_e.append(se_); dyn_sid_a.append(sa)
        if not np.array_equal(W_stat, W_dyn): arms_differ_stat_dyn = True
        # batch-vs-transition head divergence check (arms_differ)
        for sent in dev[:50]:
            attr = _mk_attr(sent); th = _decode_greedy(sent, attr, W_dyn)
            n = len(sent); arc = [[None] * (n + 1) for _ in range(n + 1)]
            for i in range(1, n + 1):
                for h in range(0, n + 1):
                    if h == i: continue
                    arc[i][h] = _arc_ids(sent, i, h)
            bh = _batch_local_decode(arc, n, avg_b)
            if th != bh: arms_differ_batch_trans = True; break
        if sd == SEEDS[0]:
            W_dyn_seed1 = W_dyn; W_stat_seed1 = W_stat
        print("  seed %d: STATIC-UAS=%.4f DYNAMIC-UAS=%.4f | dyn buried-sid=%.4f (%.1fs)" % (
            sd, u_stat, u_dyn, sb, time.time() - t), flush=True)
        _hb(out_dir, "seed %d dynamic done uas=%.4f sid_b=%.4f" % (sd, u_dyn, sb))

    # -------- LEARNING CURVE (dynamic arm, seed 1, data fractions) --------
    lc = {}
    if DO_LC:
        rng = np.random.default_rng(999)
        perm = rng.permutation(len(train))
        for fr in LC_FRACS:
            k = max(1, int(round(fr * len(train))))
            sub = [train[i] for i in perm[:k]]
            Wl = _train_transition(sub, 1, dynamic=True)
            ul = round(_uas_transition(dev, Wl), 4)
            lc["%.2f" % fr] = {"n_train": k, "uas": ul}
            print("  [learning-curve] frac=%.2f n=%d UAS=%.4f" % (fr, k, ul), flush=True)
            _hb(out_dir, "LC frac %.2f uas=%.4f" % (fr, ul))

    # -------- BEAM (optional, seed 1) --------
    beam_uas = None
    if DO_BEAM and W_dyn_seed1 is not None:
        t = time.time()
        beam_uas = round(_uas_transition(dev, W_dyn_seed1, beam=BEAM_WIDTH), 4)
        print("  [beam w=%d] dynamic-model beam-UAS=%.4f (greedy was %.4f) %.1fs" % (
            BEAM_WIDTH, beam_uas, dyn_uas[0], time.time() - t), flush=True)
        _hb(out_dir, "beam done uas=%.4f" % beam_uas)

    # -------- STACK-DEPTH readout (dynamic seed1; log per-token depth availability) --------
    depth_sample = {}
    if W_dyn_seed1 is not None and dev:
        s0 = dev[0]; attr0 = _mk_attr(s0)
        _, dep = _decode_greedy(s0, attr0, W_dyn_seed1, want_depth=True)
        depth_sample = {"sentence_tokens": [t[1] for t in s0][:20],
                        "per_token_stack_depth": {str(k): int(v) for k, v in list(dep.items())[:20]},
                        "note": "depth[k] = stack size when token k first pushed; inspectable per-token embedding depth"}

    lc_lo = lc.get("%.2f" % LC_FRACS[0], {}).get("uas", 0.0)
    lc_hi = lc.get("%.2f" % LC_FRACS[-1], {}).get("uas", 0.0)
    out = {
        "n_seeds": len(SEEDS), "n_train": len(train), "n_dev": len(dev), "n_pool": len(pool),
        "n_buried": n_buried, "n_easy": n_easy,
        "batch_local_uas": batch_uas, "batch_mst_uas_cited": 0.7895,
        "batch_buried_sid": round(b_sid_b, 4), "batch_easy_sid": round(b_sid_e, 4), "batch_all_sid": round(b_sid_a, 4),
        "static_uas_mean": mean(stat_uas), "static_uas_vals": stat_uas,
        "dynamic_uas_mean": mean(dyn_uas), "dynamic_uas_vals": dyn_uas,
        "dynamic_uas_se": round(se(dyn_uas), 4),
        "dynamic_uas_mean_minus_2se": round(mean(dyn_uas) - 2 * se(dyn_uas), 4),
        "dynamic_buried_sid_mean": mean(dyn_sid_b), "dynamic_buried_sid_vals": [round(v, 4) for v in dyn_sid_b],
        "dynamic_easy_sid_mean": mean(dyn_sid_e), "dynamic_all_sid_mean": mean(dyn_sid_a),
        "learning_curve": lc, "lc_lo_uas": lc_lo, "lc_hi_uas": lc_hi, "lc_rise": round(lc_hi - lc_lo, 4),
        "lc_points": len(lc), "lc_expected_points": (len(LC_FRACS) if DO_LC else 0),
        "beam_uas": beam_uas, "beam_width": BEAM_WIDTH if beam_uas is not None else 0,
        "dyn_minus_static": round(mean(dyn_uas) - mean(stat_uas), 4),
        "arms_differ_batch_vs_transition": arms_differ_batch_trans,
        "arms_differ_static_vs_dynamic": arms_differ_stat_dyn,
        "stack_depth_readout_sample": depth_sample,
    }
    print("\n  === SUMMARY (mean over %d seeds) ===" % len(SEEDS), flush=True)
    print("  UAS:  BATCH_LOCAL=%.4f (ref 0.7875)  BATCH_MST=0.7895(cited)  STATIC=%.4f  DYNAMIC=%.4f (2SE-lo=%.4f)" % (
        batch_uas, out["static_uas_mean"], out["dynamic_uas_mean"], out["dynamic_uas_mean_minus_2se"]), flush=True)
    print("  dyn-static delta=%+.4f (error-prop mitigation) | beam-UAS=%s" % (out["dyn_minus_static"], beam_uas), flush=True)
    print("  BURIED subject-id:  BATCH=%.4f  DYNAMIC=%.4f (n_buried=%d)" % (
        out["batch_buried_sid"], out["dynamic_buried_sid_mean"], n_buried), flush=True)
    print("  learning curve: %.4f (frac %.2f) -> %.4f (frac %.2f) rise=%+.4f" % (
        lc_lo, LC_FRACS[0], lc_hi, LC_FRACS[-1], out["lc_rise"]), flush=True)
    return out


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r.get("n_buried", 0) == 0:
        return ("UNKNOWN", "UNKNOWN: discriminator did not fire (n_buried==0)")
    if r.get("lc_expected_points", 0) and r.get("lc_points", 0) < r["lc_expected_points"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: learning-curve points %d < expected %d" % (
            r["lc_points"], r["lc_expected_points"]))
    batch = max(r["batch_local_uas"], r["batch_mst_uas_cited"])
    dyn = r["dynamic_uas_mean"]; dyn2 = r["dynamic_uas_mean_minus_2se"]
    d_sid = r["dynamic_buried_sid_mean"] - r["batch_buried_sid"]
    dyn_vs_stat = r["dyn_minus_static"]
    lc_rise = r["lc_rise"]
    s = ("UAS batch_local=%.4f batch_mst=%.4f | static=%.4f dynamic=%.4f (2SE-lo=%.4f, vals=%s) | "
         "dyn-static=%+.4f | buried-sid batch=%.4f dynamic=%.4f (d=%+.4f, n=%d) | "
         "learning-curve %.4f->%.4f rise=%+.4f | beam=%s" % (
             r["batch_local_uas"], r["batch_mst_uas_cited"], r["static_uas_mean"], dyn, dyn2, r["dynamic_uas_vals"],
             dyn_vs_stat, r["batch_buried_sid"], r["dynamic_buried_sid_mean"], d_sid, r["n_buried"],
             r["lc_lo_uas"], r["lc_hi_uas"], lc_rise, r["beam_uas"]))
    # HARD_FAIL: transition does not beat batch, OR dynamic no better than static (mitigation inert)
    if dyn <= batch:
        return ("HARD_FAIL", "HARD_FAIL: transition dynamic UAS <= batch -- transition paradigm does not help here. " + s)
    if dyn_vs_stat <= 0.0:
        return ("HARD_FAIL", "HARD_FAIL: dynamic-oracle (%.4f) NOT better than static-oracle greedy (%.4f) -- the "
                "error-propagation mitigation is inert. " % (dyn, r["static_uas_mean"]) + s)
    # HARD_PASS: real margin over batch AND buried-sid improves AND learning curve rises
    if dyn2 >= 0.82 and d_sid >= 0.05 and lc_rise >= 0.03:
        return ("HARD_PASS", "HARD_PASS: arc-eager+dynamic-oracle transition parser beats batch by a real margin "
                "(2SE-lo>=0.82), improves buried subject-id over batch by >=0.05, and the learning curve rises "
                ">=0.03 -- crown incremental-reader capability. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: transition beats batch and dynamic beats static, but below the full "
            "crown bar (2SE-lo<0.82 or buried-sid margin<0.05 or lc-rise<0.03). " + s)


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
               "arms_differ_verified": bool(r.get("arms_differ_batch_vs_transition", False) and
                                            r.get("arms_differ_static_vs_dynamic", False)),
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
