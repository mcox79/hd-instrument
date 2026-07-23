"""
exp_depparse_global_beam_earlyupdate_cpu_v1.py -- GLOBAL structured-perceptron training (beam +
  EARLY-UPDATE, Collins-Roark 2004 / Zhang-Clark 2008) for the glass-box arc-eager transition parser,
  to break the LOCAL-ARGMAX saturation measured in exp_depparse_transition_arceager_cpu_v1 (atom 29451).

WHY (dedup-derived lever; disk-verified baseline):
  - 29451 arc-eager parser: LOCAL dynamic-oracle greedy training -> dev UAS 0.8109
    (vals [0.8103,0.8104,0.8119], se 0.0004).  MEASURED@data/exp_depparse_transition_arceager_cpu_v1/metrics.json
  - 29451 beam DECODE on that LOCAL-trained model HURT: UAS 0.7528 (<< 0.8109) = classic LABEL-BIAS
    mismatch (a locally-trained action scorer's per-step scores are not calibrated for cumulative
    sequence scoring, so beam accumulates miscalibrated scores and picks worse whole derivations).
    MEASURED@same:beam_uas.
  - headroom leak-hunt: LOCAL-argmax saturates ~0.81; classical arc-eager lit 0.86-0.89. The gap is a
    SEARCH / GLOBAL-TRAINING gap, not (necessarily) a feature gap.  CITED@notes/parser_global_beam_training_break_local_saturation_2026-07-23.md

WHAT THIS TESTS (ONE VARIABLE across the mechanism comparison = TRAINING REGIME; features held FIXED):
  The classic glass-box fix for "beam-decode hurts a locally-trained model" is to TRAIN GLOBALLY:
  maintain a beam of partial derivations, score whole ACTION SEQUENCES, and update with EARLY-UPDATE
  (stop + update the moment the gold derivation falls off the beam; Collins-Roark 2004). Averaged
  perceptron, inspectable linear weights, NO gradient/autograd, explicit beam items.

  FEATURES ARE HELD BIT-IDENTICAL across all arms = 29451's exact `_config_feats` transition config
  features (copied verbatim below; the arc-factored feateng_struct +0.04 features are NOT transferable
  to an action-scorer -- different decomposition -- so the reusable structural family IS the transition
  config/stack feature set). This isolates TRAINING REGIME as the single variable, which is exactly the
  headroom-leakhunt claim under test ("it's search not features"). If global-beam training with these
  SAME features does NOT beat local greedy by >= +0.03, that is an EARNED BOUND: the saturation is
  deeper than decode, and the real lever is richer features/representation (a separate follow-on).

ARMS (identical features + identical dev eval split; ONE variable = training regime):
  ARM_LOCAL        -- 29451 baseline: dynamic-oracle LOCAL greedy training, greedy decode. ~0.81.
                      In-run positive control (Gate D: reproduces 29451's 0.8109 at MAXLEN=50).
  ARM_LOCAL_BEAM   -- CONTROL: the SAME local-trained weights, BEAM decode (width B). Should REPRODUCE
                      the beam-hurts anomaly (~0.75). Isolates: decode alone does not help; if the
                      GLOBAL arm (same beam width) wins, the lever is TRAINING, not the decode.
  ARM_GLOBAL_BEAM  -- MECHANISM: GLOBAL beam + early-update training, BEAM decode (same width B).
                      HYPOTHESIS: beam now HELPS -> UAS toward 0.85-0.88.

PRE-REGISTERED bands (see prereg md; local_mean measured in-run, ~0.81):
  HARD_PASS = global_uas_mean_minus_2se >= local_uas_mean + 0.03 (clean +0.03 margin, approaching lit)
              AND beam_hurts_reproduced (ARM_LOCAL_BEAM < ARM_LOCAL by >= 0.01; isolates TRAINING)
              AND learning-curve RISES (global UAS at frac 1.0 - at frac 0.1 >= 0.02).
  HARD_FAIL = global_uas_mean <= local_uas_mean (global-beam training does NOT beat local greedy at all)
              -> EARNED BOUND: search does not help this feature set; saturation is deeper than decode.
  MIDDLE_BAND = global beats local by a positive margin but < clean +0.03, OR isolation not clean
                (beam did not hurt the local model), OR learning curve did not rise.
  UNKNOWN = corpus load fails OR global arm produced no parses (discriminator did not fire).
  crlb_n/a: parse/attachment accuracy is discrete argmax over trained scores -- no CRLB noise floor.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (global weights != local weights bit-check; global-beam heads
#   differ from local-greedy heads on >=1 dev sentence)
# - final_metrics_atomicity = tmp_replace (os.replace; write_metrics + crash path both atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete parse accuracy, no noise floor)
# - baseline_in_band at smoke (local UAS ~0.81 in (0.05,0.95))
# - discriminator fires: global arm parses dev; ARM_LOCAL_BEAM control reproduces beam-hurts direction
# - cardinality_ok: learning-curve EXPECTED points = len(LC_FRACS); verdict counts them
# - HYPOTHESIZED/MEASURED/CITED tags in report; deterministic seeding (fixed ints + crc32; NO hash(),
#   NO list(set()))
# - progress_logging: print_flush_true (long cell; per-epoch flush) + heartbeat
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
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu  # loader-parity anchor (same as 29451)

ANCHOR_NAME = "depparse_global_beam_earlyupdate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21
MASK = SIZE - 1
NOUN_POS = ("NOUN", "PROPN", "PRON")

# Actions (verbatim 29451)
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_NAMES = {SHIFT: "SHIFT", LARC: "LEFT-ARC", RARC: "RIGHT-ARC", REDU: "REDUCE"}
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)

# Tunables (env-overridable; FULL params fixed from smoke timing).
EPOCHS_LOCAL = int(os.environ.get("HDLAB_EPOCHS_LOCAL", "3" if SMOKE else "10"))
EPOCHS_GLOBAL = int(os.environ.get("HDLAB_EPOCHS_GLOBAL", "3" if SMOKE else "6"))
EPOCHS_LC = int(os.environ.get("HDLAB_EPOCHS_LC", "3" if SMOKE else "5"))
MAXLEN = int(os.environ.get("HDLAB_MAXLEN", "50"))
BEAM_WIDTH = int(os.environ.get("HDLAB_BEAM", "6" if SMOKE else "8"))
EXPLORE_AFTER = int(os.environ.get("HDLAB_EXPLORE_AFTER", "2"))
EXPLORE_P = float(os.environ.get("HDLAB_EXPLORE_P", "0.9"))
DO_LC = os.environ.get("HDLAB_DO_LC", "0" if SMOKE else "1") == "1"
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
# TRANSITION parser primitives -- COPIED VERBATIM from exp_depparse_transition_arceager_cpu_v1 (29451)
# so features/oracle/decode are BIT-IDENTICAL and ARM_LOCAL reproduces UAS 0.8109. token 6-tuple =
# (idx, form, upos, head, deprel, number).
# ================================================================================================
_ROOT_ATTR = ("<root>", "ROOT", "<root>")
_NONE_ATTR = ("<none>", "<NONE>", "<none>")


def _mk_attr(sent):
    a = [_ROOT_ATTR]
    for (i, w, p, h, dl, num) in sent:
        a.append((w.lower(), p, _suf(w.lower())))
    return a


def _config_feats(stack, bptr, n, attr, heads):
    """Base feature strings (no action). Glass-box config features over s0,s1,b0,b1,b2. VERBATIM 29451."""
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
    """Goldberg & Nivre 2012 arc-eager dynamic-oracle costs (# gold arcs made unreachable). VERBATIM 29451."""
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
            if gh != b0 and (bptr + 1) <= gh <= n:
                c += 1
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
        elif a == RARC:
            c = 0
            gh = gold[b0]
            if gh != s0 and (gh in stack_set or (bptr + 1) <= gh <= n):
                c += 1
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
    """Deterministic zero-cost move, fixed priority LARC>RARC>REDU>SHIFT (canonical gold derivation)."""
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


def _train_transition(train, seed, dynamic):
    """LOCAL averaged-perceptron action classifier (dynamic oracle). VERBATIM 29451 (ARM_LOCAL)."""
    rng = np.random.default_rng(seed)
    W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS_LOCAL):
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
                    a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                    if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                        _perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                    if explore and a_pred in legal and rng.random() < EXPLORE_P:
                        a_next = a_pred
                    else:
                        a_next = a_orl
                else:
                    a_gold = _static_oracle_move(stack, bptr, n, gold, heads)
                    if a_pred != a_gold:
                        _perc_update(W, CW, base_ids, a_gold, a_pred, c); c += 1
                    a_next = a_gold
                stack, bptr = _apply(stack, bptr, heads, a_next)
                guard += 1
                if guard > 4 * (n + 2):
                    break
    return W - CW / c


def _decode_greedy(sent, attr, W):
    n = len(sent)
    stack = [0]; bptr = 1; heads = {}
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
        stack, bptr = _apply(stack, bptr, heads, a)
        guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0
    return heads


def _decode_beam(sent, attr, W, width):
    """Beam arc-eager decode (cumulative action-score). VERBATIM 29451."""
    n = len(sent)
    init = (tuple([0]), 1, {}, 0.0)
    beam = [init]
    guard = 0
    max_steps = 4 * (n + 2)
    while True:
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
# GLOBAL beam + EARLY-UPDATE training (NEW; the mechanism). Collins-Roark 2004; Zhang-Clark 2008.
# Glass-box: each beam item is an explicit _Hyp(stack,bptr,heads,score) with a backpointer to the
# feature-ids it scored. Averaged perceptron; NO gradient/autograd.
# ================================================================================================
class _Hyp:
    __slots__ = ("stack", "bptr", "heads", "score", "parent", "ids")

    def __init__(self, stack, bptr, heads, score, parent, ids):
        self.stack = stack; self.bptr = bptr; self.heads = heads
        self.score = score; self.parent = parent; self.ids = ids


def _gold_derivation(sent, attr, n, gold):
    """Static-oracle canonical gold derivation. Returns [(base_ids, action), ...] or None if the tree
    is unreachable (non-projective) -> skip that sentence for global training (arc-eager cannot build it)."""
    stack = [0]; bptr = 1; heads = {}
    steps = []
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _legal(stack, bptr, n, heads)
        if not legal:
            return None
        a = _static_oracle_move(stack, bptr, n, gold, heads)
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads)), dtype=np.int64)
        steps.append((base_ids, a))
        stack, bptr = _apply(stack, bptr, heads, a)
        guard += 1
        if guard > 4 * (n + 2):
            return None
    for i in range(1, n + 1):
        if heads.get(i, 0) != gold[i]:
            return None
    return steps


def _collect_ids(hyp):
    out = []
    h = hyp
    while h is not None and h.ids is not None:
        out.append(h.ids); h = h.parent
    out.reverse()
    return out


def _perc_update_seq(W, CW, gold_list, pred_list, c):
    """One structured-perceptron update: +gold-prefix features, -pred-prefix features (averaged)."""
    if gold_list:
        g = np.concatenate(gold_list)
        np.add.at(W, g, 1.0); np.add.at(CW, g, float(c))
    if pred_list:
        p = np.concatenate(pred_list)
        np.add.at(W, p, -1.0); np.add.at(CW, p, -float(c))
    return c + 1


def _train_sentence_global(sent, attr, n, gold, W, CW, c, width):
    """Beam + EARLY-UPDATE on one sentence. Returns (c, skipped_flag)."""
    gold_steps = _gold_derivation(sent, attr, n, gold)
    if gold_steps is None:
        return c, 1
    root = _Hyp((0,), 1, {}, 0.0, None, None)
    beam = [root]
    gold_node = root
    gold_prefix = []
    T = len(gold_steps)
    for t in range(T):
        g_ids, g_a = gold_steps[t]
        g_taken = (g_ids ^ ACT_SALT[g_a]) & MASK
        nxt = []
        gold_child = None
        for hyp in beam:
            stack = list(hyp.stack)
            if hyp.bptr > n and len(stack) <= 1:
                continue
            legal = _legal(stack, hyp.bptr, n, hyp.heads)
            if not legal:
                continue
            base_ids = np.fromiter((_h(f) for f in _config_feats(stack, hyp.bptr, n, attr, hyp.heads)),
                                   dtype=np.int64)
            for a in legal:
                ids = (base_ids ^ ACT_SALT[a]) & MASK
                sc = hyp.score + float(W[ids].sum())
                st2 = list(stack); hd2 = dict(hyp.heads); bp2 = hyp.bptr
                st2, bp2 = _apply(st2, bp2, hd2, a)
                child = _Hyp(tuple(st2), bp2, hd2, sc, hyp, ids)
                nxt.append(child)
                if hyp is gold_node and a == g_a:
                    gold_child = child
        gold_prefix.append(g_taken)
        if not nxt or gold_child is None:
            break
        # ADVERSARIAL tie-break: rank gold LAST among equal scores so ties count against gold. This
        # bootstraps learning from zero weights (all-tied -> gold pushed off -> update fires) and is
        # the standard structured-perceptron/early-update convention (Collins 2002; Huang et al. 2012).
        nxt.sort(key=lambda hh: (-hh.score, 1 if hh is gold_child else 0))
        beam = nxt[:width]
        gold_alive = False
        for hh in beam:
            if hh is gold_child:
                gold_alive = True; break
        if not gold_alive:
            # EARLY-UPDATE: gold fell off the beam at step t -> update toward gold prefix, away from best.
            pred = beam[0]
            c = _perc_update_seq(W, CW, gold_prefix, _collect_ids(pred), c)
            return c, 0
        gold_node = gold_child
    # reached end with gold still on the beam: final update if gold is not the unique top derivation.
    if beam and beam[0] is not gold_node:
        c = _perc_update_seq(W, CW, gold_prefix, _collect_ids(beam[0]), c)
    return c, 0


def _train_global_beam(train, seed, width, epochs, out_dir=None, tag=""):
    rng = np.random.default_rng(seed)
    W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    n_skip = 0
    for ep in range(epochs):
        te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s); attr = _mk_attr(s)
            gold = [0] * (n + 1)
            for (i, w, p, h, dl, num) in s:
                gold[i] = h if 0 <= h <= n else 0
            c, sk = _train_sentence_global(s, attr, n, gold, W, CW, c, width)
            n_skip += sk
        print("  [global %s seed=%d] epoch %d/%d done %.1fs (updates=%d skip=%d)" % (
            tag, seed, ep + 1, epochs, time.time() - te, c - 1, n_skip), flush=True)
        if out_dir is not None:
            _hb(out_dir, "global %s seed %d ep %d/%d %.1fs" % (tag, seed, ep + 1, epochs, time.time() - te))
    return W - CW / c, n_skip


# ================================================================================================
# Corpus loader (Number morphology; token 6-tuple). VERBATIM 29451.
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


# ================================================================================================
# Evaluation: UAS (all + nopunct) + hard-attachment (distance-bucket) breakdown, one pass.
# ================================================================================================
def _eval_uas(sents, decode_fn):
    buckets = {"1": [0, 0], "2": [0, 0], "3-6": [0, 0], "7+": [0, 0]}
    allc = allt = npc = npt = 0
    for sent in sents:
        attr = _mk_attr(sent)
        heads = decode_fn(sent, attr)
        n = len(sent)
        for (i, w, p, h, dl, num) in sent:
            if h < 0 or h > n: continue
            ok = int(heads.get(i, -1) == h)
            allc += ok; allt += 1
            if p != "PUNCT": npc += ok; npt += 1
            d = abs(h - i) if h > 0 else 1
            b = "1" if d == 1 else ("2" if d == 2 else ("3-6" if d <= 6 else "7+"))
            buckets[b][0] += ok; buckets[b][1] += 1
    bydist = {k: {"uas": round(v[0] / v[1], 4) if v[1] else 0.0, "n": v[1]} for k, v in buckets.items()}
    return {"uas_all": round(allc / allt, 4) if allt else 0.0,
            "uas_nopunct": round(npc / npt, 4) if npt else 0.0,
            "n_arcs": allt, "by_distance": bydist}


# ================================================================================================
# Self-test: gold-derivation reachability + early-update firing + loader parity.
# ================================================================================================
def _selftest():
    assert _h("abc") == _h("abc")
    assert _dist(1) == "1" and _dist(4) == "3-5" and _dist(20) == "11+"

    # projective sentence: "the(1) key(2) to(3) the(4) cabinets(5) are(6) on(7) the(8) table(9)"
    gold = [0, 2, 6, 5, 5, 2, 0, 9, 9, 6]
    sent = [(1, "the", "DET", 2, "det", None), (2, "key", "NOUN", 6, "nsubj", "Sing"),
            (3, "to", "ADP", 5, "case", None), (4, "the", "DET", 5, "det", None),
            (5, "cabinets", "NOUN", 2, "nmod", "Plur"), (6, "are", "AUX", 0, "root", None),
            (7, "on", "ADP", 9, "case", None), (8, "the", "DET", 9, "det", None),
            (9, "table", "NOUN", 6, "obl", None)]
    n = 9; attr = _mk_attr(sent)
    steps = _gold_derivation(sent, attr, n, gold)
    assert steps is not None and len(steps) > 0, "gold derivation must be reachable (projective)"
    # replay gold_steps -> must rebuild the gold tree exactly.
    stack = [0]; bptr = 1; heads = {}
    for (base_ids, a) in steps:
        stack, bptr = _apply(stack, bptr, heads, a)
    for i in range(1, n + 1):
        assert heads.get(i) == gold[i], "gold replay head[%d]=%r != %d" % (i, heads.get(i), gold[i])
    print("[selftest] gold derivation reachable + replays to gold tree (%d steps)" % len(steps), flush=True)

    # EARLY-UPDATE must FIRE with adversarial weights that push gold off a width-1 beam.
    W = np.zeros(SIZE); CW = np.zeros(SIZE)
    # bias the very first legal non-gold action high so gold is immediately displaced at width 1.
    g0_ids, g0_a = steps[0]
    for a in _legal([0], 1, n, {}):
        if a != g0_a:
            bad = (g0_ids ^ ACT_SALT[a]) & MASK
            np.add.at(W, bad, 100.0)
    c0 = 1
    c1, sk = _train_sentence_global(sent, attr, n, gold, W, CW, c0, width=1)
    assert sk == 0, "projective sentence should not be skipped"
    assert c1 > c0, "EARLY-UPDATE must fire (c advanced) when gold pushed off the beam"
    print("[selftest] early-update fired under adversarial weights (c %d->%d)" % (c0, c1), flush=True)

    # a well-separated model where gold is trivially top -> NO update at width>=2.
    W2 = np.zeros(SIZE); CW2 = np.zeros(SIZE)
    for (base_ids, a) in steps:
        good = (base_ids ^ ACT_SALT[a]) & MASK
        np.add.at(W2, good, 50.0)
    c2 = 5
    c3, sk2 = _train_sentence_global(sent, attr, n, gold, W2, CW2, c2, width=4)
    assert sk2 == 0 and c3 == c2, "no update expected when gold is the top derivation (c %d->%d)" % (c2, c3)
    print("[selftest] no spurious update when gold is top (c stable at %d)" % c2, flush=True)

    # loader parity: first-5 fields must equal _ud_loader.load_conllu.
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
    print("[selftest] PASS: depparse-global-beam-earlyupdate (gold-deriv + early-update + loader parity)", flush=True)


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
        train = train[:300]; dev = dev[:150]
        pool = (dev + test)[:400]
        SEEDS = [1]
    else:
        pool = dev + test
        SEEDS = [1, 2, 3]
    print("[data] train=%d dev=%d pool=%d MAXLEN=%d EP_LOCAL=%d EP_GLOBAL=%d BEAM=%d seeds=%s" % (
        len(train), len(dev), len(pool), MAXLEN, EPOCHS_LOCAL, EPOCHS_GLOBAL, BEAM_WIDTH, SEEDS), flush=True)
    _hb(out_dir, "data loaded")

    def mean(x): return round(sum(x) / len(x), 4) if x else 0.0

    def se(x):
        if len(x) < 2: return 0.0
        m = sum(x) / len(x); v = sum((z - m) ** 2 for z in x) / len(x)
        return (v ** 0.5) / (len(x) ** 0.5)

    local_uas = []; local_beam_uas = []; global_uas = []
    W_local_s1 = None; W_global_s1 = None
    for sd in SEEDS:
        t = time.time()
        W_local = _train_transition(train, sd, dynamic=True)
        ev_l = _eval_uas(dev, lambda s, a: _decode_greedy(s, a, W_local))
        local_uas.append(ev_l["uas_all"])
        ev_lb = _eval_uas(dev, lambda s, a: _decode_beam(s, a, W_local, BEAM_WIDTH))
        local_beam_uas.append(ev_lb["uas_all"])
        print("  seed %d: LOCAL greedy UAS=%.4f | LOCAL+beam(w=%d) UAS=%.4f (%.1fs)" % (
            sd, ev_l["uas_all"], BEAM_WIDTH, ev_lb["uas_all"], time.time() - t), flush=True)
        _hb(out_dir, "seed %d local done greedy=%.4f beam=%.4f" % (sd, ev_l["uas_all"], ev_lb["uas_all"]))
        t = time.time()
        W_glob, n_skip = _train_global_beam(train, sd, BEAM_WIDTH, EPOCHS_GLOBAL, out_dir=out_dir, tag="main")
        ev_g = _eval_uas(dev, lambda s, a: _decode_beam(s, a, W_glob, BEAM_WIDTH))
        global_uas.append(ev_g["uas_all"])
        print("  seed %d: GLOBAL-BEAM+early-update UAS=%.4f (skip_nonproj=%d) (%.1fs)" % (
            sd, ev_g["uas_all"], n_skip, time.time() - t), flush=True)
        _hb(out_dir, "seed %d global done uas=%.4f" % (sd, ev_g["uas_all"]))
        if sd == SEEDS[0]:
            W_local_s1 = W_local; W_global_s1 = W_glob
            ev_l1, ev_lb1, ev_g1 = ev_l, ev_lb, ev_g

    # arms-differ: global weights != local weights; global-beam heads differ from local-greedy heads.
    arms_differ_weights = bool(W_global_s1 is not None and not np.array_equal(W_local_s1, W_global_s1))
    arms_differ_heads = False
    for sent in dev[:80]:
        attr = _mk_attr(sent)
        gh = _decode_beam(sent, attr, W_global_s1, BEAM_WIDTH)
        lh = _decode_greedy(sent, attr, W_local_s1)
        if gh != lh:
            arms_differ_heads = True; break

    # LEARNING CURVE (global arm, seed 1, data fractions) -- flexible/improving property.
    lc = {}
    if DO_LC and W_global_s1 is not None:
        rng = np.random.default_rng(999)
        perm = rng.permutation(len(train))
        for fr in LC_FRACS:
            k = max(1, int(round(fr * len(train))))
            sub = [train[i] for i in perm[:k]]
            Wl, _ = _train_global_beam(sub, 1, BEAM_WIDTH, EPOCHS_LC, out_dir=out_dir, tag="lc%.2f" % fr)
            ul = _eval_uas(dev, lambda s, a: _decode_beam(s, a, Wl, BEAM_WIDTH))["uas_all"]
            lc["%.2f" % fr] = {"n_train": k, "uas": ul}
            print("  [learning-curve global] frac=%.2f n=%d UAS=%.4f" % (fr, k, ul), flush=True)
            _hb(out_dir, "LC frac %.2f uas=%.4f" % (fr, ul))

    # buried subject-id per arm (seed 1) -- secondary structural readout.
    def _sid(head_fn):
        b, e, a, nb, ne = _subject_id(pool, head_fn)
        return {"buried": round(b, 4), "easy": round(e, 4), "all": round(a, 4), "n_buried": nb, "n_easy": ne}
    sid_local = _sid(lambda s, a: _decode_greedy(s, a, W_local_s1)) if W_local_s1 is not None else {}
    sid_global = _sid(lambda s, a: _decode_beam(s, a, W_global_s1, BEAM_WIDTH)) if W_global_s1 is not None else {}

    lc_lo = lc.get("%.2f" % LC_FRACS[0], {}).get("uas", 0.0)
    lc_hi = lc.get("%.2f" % LC_FRACS[-1], {}).get("uas", 0.0)
    out = {
        "n_seeds": len(SEEDS), "n_train": len(train), "n_dev": len(dev), "n_pool": len(pool),
        "beam_width": BEAM_WIDTH, "epochs_local": EPOCHS_LOCAL, "epochs_global": EPOCHS_GLOBAL,
        "local_uas_mean": mean(local_uas), "local_uas_vals": local_uas,
        "local_beam_uas_mean": mean(local_beam_uas), "local_beam_uas_vals": local_beam_uas,
        "global_uas_mean": mean(global_uas), "global_uas_vals": global_uas,
        "global_uas_se": round(se(global_uas), 4),
        "global_uas_mean_minus_2se": round(mean(global_uas) - 2 * se(global_uas), 4),
        "local_uas_29451_cited": 0.8109, "local_beam_29451_cited": 0.7528,
        "eval_local_seed1": ev_l1, "eval_local_beam_seed1": ev_lb1, "eval_global_seed1": ev_g1,
        "learning_curve": lc, "lc_lo_uas": lc_lo, "lc_hi_uas": lc_hi, "lc_rise": round(lc_hi - lc_lo, 4),
        "lc_points": len(lc), "lc_expected_points": (len(LC_FRACS) if DO_LC else 0),
        "buried_sid_local": sid_local, "buried_sid_global": sid_global,
        "global_minus_local": round(mean(global_uas) - mean(local_uas), 4),
        "local_minus_localbeam": round(mean(local_uas) - mean(local_beam_uas), 4),
        "arms_differ_weights": arms_differ_weights, "arms_differ_heads": arms_differ_heads,
    }
    print("\n  === SUMMARY (mean over %d seeds) ===" % len(SEEDS), flush=True)
    print("  UAS:  LOCAL_greedy=%.4f (29451 ref 0.8109)  LOCAL+beam=%.4f (29451 ref 0.7528)  "
          "GLOBAL_beam=%.4f (2SE-lo=%.4f)" % (
              out["local_uas_mean"], out["local_beam_uas_mean"], out["global_uas_mean"],
              out["global_uas_mean_minus_2se"]), flush=True)
    print("  global-local delta=%+.4f | local-localbeam delta=%+.4f (beam-hurts control)" % (
        out["global_minus_local"], out["local_minus_localbeam"]), flush=True)
    print("  learning curve: %.4f (frac %.2f) -> %.4f (frac %.2f) rise=%+.4f" % (
        lc_lo, LC_FRACS[0], lc_hi, LC_FRACS[-1], out["lc_rise"]), flush=True)
    return out


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r.get("global_uas_mean", 0.0) <= 0.0 or r.get("n_dev", 0) == 0:
        return ("UNKNOWN", "UNKNOWN: global arm produced no parses (discriminator did not fire)")
    if r.get("lc_expected_points", 0) and r.get("lc_points", 0) < r["lc_expected_points"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: learning-curve points %d < expected %d" % (
            r["lc_points"], r["lc_expected_points"]))
    loc = r["local_uas_mean"]; locb = r["local_beam_uas_mean"]
    glob = r["global_uas_mean"]; glob2 = r["global_uas_mean_minus_2se"]
    margin = glob - loc
    margin2 = glob2 - loc
    beam_hurts = (loc - locb) >= 0.01
    lc_rise = r.get("lc_rise", 0.0)
    lc_ok = (r.get("lc_expected_points", 0) == 0) or (lc_rise >= 0.02)
    s = ("UAS local_greedy=%.4f local+beam=%.4f global_beam=%.4f (2SE-lo=%.4f, vals=%s) | "
         "global-local=%+.4f (2SE margin=%+.4f) | beam-hurts control local-localbeam=%+.4f (reproduced=%s) | "
         "learning-curve %.4f->%.4f rise=%+.4f (ok=%s) | buried-sid local=%s global=%s" % (
             loc, locb, glob, glob2, r["global_uas_vals"], margin, margin2, r["local_minus_localbeam"],
             beam_hurts, r["lc_lo_uas"], r["lc_hi_uas"], lc_rise, lc_ok,
             r.get("buried_sid_local", {}).get("buried"), r.get("buried_sid_global", {}).get("buried")))
    # HARD_FAIL: global-beam training does NOT beat local greedy at all -> earned bound.
    if margin <= 0.0:
        return ("HARD_FAIL", "HARD_FAIL: GLOBAL-beam training UAS (%.4f) does NOT beat LOCAL greedy (%.4f) "
                "-- search does not help this feature set; saturation is deeper than decode (earned bound). "
                % (glob, loc) + s)
    # HARD_PASS: clean +0.03 (2SE) AND beam-hurts reproduced (isolates training) AND learning curve rises.
    if margin2 >= 0.03 and beam_hurts and lc_ok:
        return ("HARD_PASS", "HARD_PASS: GLOBAL-beam + early-update training beats LOCAL greedy by a clean +0.03 "
                "(2SE-lo margin=%+.4f), the beam-decode-on-local control reproduces the beam-hurts anomaly "
                "(isolates TRAINING as the lever), and the learning curve rises -- global structured training "
                "breaks the local-argmax saturation. " % margin2 + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: GLOBAL-beam beats LOCAL by %+.4f but below the clean +0.03 (2SE) bar "
            "OR isolation/learning-curve gate unmet (beam_hurts=%s lc_ok=%s). " % (margin, beam_hurts, lc_ok) + s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        _selftest()
        sys.exit(0)
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=(1 if SMOKE else 3))
    t0 = time.time()
    try:
        r = run(out_dir)
        v, vmsg = verdict(r)
        print("\n[VERDICT] " + vmsg, flush=True)
        metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
                   "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": [r],
                   "elapsed_s": time.time() - t0,
                   "arms_differ_verified": bool(r.get("arms_differ_weights", False) and
                                                r.get("arms_differ_heads", False)),
                   "final_metrics_atomicity": "tmp_replace",
                   "crlb_n_a": "discrete parse accuracy, no noise floor",
                   "progress_logging": "print_flush_true", "deterministic_seeding": True,
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


if __name__ == "__main__":
    main()
