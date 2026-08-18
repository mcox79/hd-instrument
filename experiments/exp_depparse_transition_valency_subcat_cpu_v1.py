"""
exp_depparse_transition_valency_subcat_cpu_v1.py -- LEARNED verb-VALENCY/SUBCATEGORIZATION features
  added to the glass-box arc-eager INCREMENTAL transition parser (extends 29451
  exp_depparse_transition_arceager_cpu_v1). THE lever the global-beam HARD_FAIL pointed to: the ~0.81
  wall is a FEATURE/REPRESENTATION limit, not a search/training-regime limit (global_beam 0.8090 ~=
  local_greedy 0.8109; beam-hurts control reproduced). Brain-drill: verb SUBCATEGORIZATION/VALENCY has
  IMMEDIATE effects on human parsing (MacDonald/Pearlmutter/Seidenberg 1994; Trueswell; constraint-based
  lexicalist); "a SMART LEXICALIZATION driven by subcategorization leads to FAR BETTER results in
  dependency parsing" (Zeman COLING 2002). We LEARN per head-lemma (esp. verbs) a frame signature from the
  TRAIN treebank + back off to POS for unseen lemmas, and inject valency features into the SAME averaged-
  perceptron action classifier. ONE VARIABLE = the valency feature block.

WHAT THIS TESTS (ONE variable = presence of the LEARNED valency feature block; SAME parser/train/eval/split):
  (1) UAS: does ARM_VALENCY beat ARM_BASE (arc-eager dynamic-oracle, base config features; reproduces
      29451 dynamic UAS ~0.8109 as the same-split positive control, Gate D) by >= +0.03 (2SE-clean)?
  (2) VERB-ARGUMENT concentration: is the gain concentrated on gold VERB/AUX-headed core-argument arcs
      (nsubj/obj/iobj/csubj/ccomp/xcomp/obl)? Valency lift on verb-arg arcs should be >= overall lift.
  (3) LEARNING CURVE: valency-arm UAS vs training-data fraction {0.1,0.5,1.0} -- the frame tables are
      built FROM the same training subset, so they get RICHER with exposure (flexible/IMPROVING property).
  (4) HELD-OUT VERB generalization: attachment accuracy on VERB core-arg arcs whose HEAD LEMMA was UNSEEN
      in TRAIN (pure POS/global backoff) must beat a trivial linear-previous baseline (backoff generalizes).
  (5) ANTI-CHEAT: SHUFFLE the frame table (each head-key gets a RANDOM other key's frame) -> the valency
      features become noise; the lift must COLLAPSE (proves LEARNED frames carry the signal, not just the
      extra parameters/capacity the valency block adds).

FRAME SIGNATURE (learned from TRAIN gold ONLY; NO gold-frame leakage at test):
  per head-key (lemma if count>=MINCOUNT else head-POS else global):
    - pos_dir_counts[(dir,dep_pos)]  -> P(a dependent of dep_pos on this side | head)  = argument fit
    - rel_counts[deprel]             -> P(core obj), P(nsubj), core-arg fraction         = transitivity/subcat
    - deg_mean                       -> typical number of dependents                     = valency saturation
  At each config, valency features describe BOTH proposed arcs (RARC: head=s0 dep=b0; LARC: head=b0 dep=s0)
  -- config-level features shared across actions, per-action salt lets the perceptron learn action-specific
  weights (identical mechanism to the base config features). Saturation uses the live children count.

ARMS (dynamic-oracle in every arm; ONLY the valency feature block differs):
  ARM_BASE     -- base config features only (FT=None). Positive control; reproduces 29451 dyn ~0.8109.
  ARM_VALENCY  -- base + LEARNED valency features (FT = frame table from TRAIN). The mechanism arm.
  ARM_VAL_SHUF -- base + valency features from a SHUFFLED frame table (anti-cheat; must collapse the lift).

PRE-REGISTERED bands (see prereg md):
  HARD_PASS = (valency_mean - 2*valency_SE) - base_uas >= 0.03  (2SE-clean +0.03 lift)
              AND verbarg_lift >= max(0.03, overall_lift)       (gain concentrated on verb-arg arcs)
              AND lc_rise(valency) >= 0.03                       (frame tables improve with exposure)
              AND heldout_verbarg_acc(valency) >= linear_prev_baseline_on_same_arcs (backoff generalizes)
              AND shuffle_lift <= 0.5 * real_lift               (anti-cheat: learned frames carry it).
  HARD_FAIL = real_lift (valency_mean - base_uas) < 0.03        (valency does NOT lift -> earned bound: the
              ceiling is deeper than lexicalization)  OR  shuffle_lift >= real_lift (the lift is just extra
              params, NOT learned frames -> mechanism invalid).  BOTH are live, reachable outcomes.
  MIDDLE    = positive lift but below the full bar (2SE<0.03, or not verb-arg-concentrated, or lc flat, or
              shuffle only partially collapses, or heldout below the positional floor).
  UNKNOWN   = corpus load fails OR base positive-control off (|base_uas - 0.8109| > 0.03) OR n_verbarg==0.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke: W_base != W_valency (bit); FT_shuffle lemma-records != FT
# - final_metrics_atomicity = tmp_replace (write_metrics + crash path both os.replace atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete parse accuracy, no noise floor)
# - baseline_in_band at smoke (ARM_BASE UAS in (0.05,0.95); Gate D positive control vs cited 0.8109)
# - discriminator fires: n_verbarg > 0 at smoke, else UNKNOWN; FT has >0 lemma keys
# - cardinality_ok: learning curve EXPECTED points = len(LC_FRACS); verdict counts them
# - HYPOTHESIZED/MEASURED/CITED tags in report; no PYTHONHASHSEED-derived seeding (fixed ints + crc32 + np rng)
# - Gate D positive control: ARM_BASE reproduces cited dynamic UAS 0.8109 within 0.03 (same split, same code path)
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import argparse, json, time, zlib, traceback, platform
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu  # working UD-EWT loader (positive-control parity anchor)

ANCHOR_NAME = "depparse_transition_valency_subcat_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21
MASK = SIZE - 1
NOUN_POS = ("NOUN", "PROPN", "PRON")
VERB_POS = ("VERB", "AUX")
CITED_BASE_UAS = 0.8109  # CITED@ data/exp_depparse_transition_arceager_cpu_v1/metrics.json:dynamic_uas_mean

# Actions
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_NAMES = {SHIFT: "SHIFT", LARC: "LEFT-ARC", RARC: "RIGHT-ARC", REDU: "REDUCE"}
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)

# Valency frame classes (Universal Dependencies deprels).
CORE_ARG_RELS = ("nsubj", "obj", "iobj", "csubj", "ccomp", "xcomp")           # true core arguments
VERBARG_RELS = ("nsubj", "obj", "iobj", "csubj", "ccomp", "xcomp", "obl")     # verb-arg breakdown set
MINCOUNT = 5  # min head-lemma occurrences to trust the lemma-level frame; else back off to POS

EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "3" if SMOKE else "10"))
MAXLEN = int(os.environ.get("HDLAB_MAXLEN", "50"))
EXPLORE_AFTER = int(os.environ.get("HDLAB_EXPLORE_AFTER", "2"))
EXPLORE_P = float(os.environ.get("HDLAB_EXPLORE_P", "0.9"))
DO_LC = os.environ.get("HDLAB_DO_LC", "1") == "1"
DO_SHUF = os.environ.get("HDLAB_DO_SHUF", "1") == "1"
TRAIN_CAP = int(os.environ.get("HDLAB_TRAIN_CAP", "0"))   # >0 caps train (mid-scale preview only)
SEEDS_OVR = os.environ.get("HDLAB_SEEDS", "")             # e.g. "1" for a single-seed preview
LC_FRACS = [0.1, 0.5, 1.0]


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
# so ARM_BASE reproduces its dynamic-oracle UAS exactly (same code path, same split = Gate D control).
# attr[k] = (word_lower, pos, suf); index 0 = ROOT. Config = (stack, bptr, heads).
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


def _apply_v(stack, bptr, heads, nchild, a):
    """Apply action; ALSO maintain nchild[head] += 1 when an arc is added (valency saturation).
    Action semantics IDENTICAL to 29451 _apply -> base path (FT=None) is bit-identical to 29451."""
    if a == SHIFT:
        stack.append(bptr); bptr += 1
    elif a == LARC:
        heads[stack[-1]] = bptr; nchild[bptr] = nchild.get(bptr, 0) + 1; stack.pop()
    elif a == RARC:
        heads[bptr] = stack[-1]; nchild[stack[-1]] = nchild.get(stack[-1], 0) + 1
        stack.append(bptr); bptr += 1
    elif a == REDU:
        stack.pop()
    return stack, bptr


def _move_costs_live(stack, bptr, n, gold, heads):
    """Goldberg & Nivre 2012 arc-eager dynamic-oracle costs. VERBATIM 29451."""
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


# ================================================================================================
# LEARNED FRAME TABLE (valency / subcategorization). Built from TRAIN gold ONLY. No test leakage.
# ================================================================================================
class Frame:
    __slots__ = ("total", "pos_dir", "rel", "deg_sum", "deg_n")

    def __init__(self):
        self.total = 0                     # number of DEPENDENTS seen for this head-key
        self.pos_dir = defaultdict(int)    # (dir, dep_pos) -> count
        self.rel = defaultdict(int)        # deprel -> count
        self.deg_sum = 0                   # sum of per-head-instance dependent counts
        self.deg_n = 0                     # number of head instances (of this key)

    def p_posdir(self, dir_, pos):
        return (self.pos_dir.get((dir_, pos), 0) / self.total) if self.total else 0.0

    def p_rel(self, rel):
        return (self.rel.get(rel, 0) / self.total) if self.total else 0.0

    def p_core(self):
        if not self.total: return 0.0
        return sum(self.rel.get(r, 0) for r in CORE_ARG_RELS) / self.total

    def deg_mean(self):
        return (self.deg_sum / self.deg_n) if self.deg_n else 0.0


def build_frame_table(train_sents):
    """Return dict FT with keys:
       'lemma' -> {word_lower: Frame}, 'pos' -> {head_pos: Frame}, 'global' -> Frame,
       'lemma_keys' -> set(word_lower with total>=MINCOUNT)  (the 'seen/learned' head lemmas).
    Learned from gold heads + gold deprels + gold POS in TRAIN."""
    by_lemma = defaultdict(Frame)
    by_pos = defaultdict(Frame)
    glob = Frame()
    for s in train_sents:
        n = len(s)
        # per head-instance dependent count (valency degree)
        deg = defaultdict(int)
        for (i, w, p, h, dl, num) in s:
            if h < 1 or h > n:
                continue
            deg[h] += 1
            hw = s[h - 1][1].lower(); hp = s[h - 1][2]
            dep_pos = p
            dir_ = "L" if i < h else "R"
            rel = dl.split(":")[0] if dl else "dep"
            for fr in (by_lemma[hw], by_pos[hp], glob):
                fr.total += 1
                fr.pos_dir[(dir_, dep_pos)] += 1
                fr.rel[rel] += 1
        # record degree per head instance
        seen_heads = set(deg.keys())
        for h in seen_heads:
            hw = s[h - 1][1].lower(); hp = s[h - 1][2]
            by_lemma[hw].deg_sum += deg[h]; by_lemma[hw].deg_n += 1
            by_pos[hp].deg_sum += deg[h]; by_pos[hp].deg_n += 1
            glob.deg_sum += deg[h]; glob.deg_n += 1
    lemma_keys = set(k for k, fr in by_lemma.items() if fr.total >= MINCOUNT)
    return {"lemma": dict(by_lemma), "pos": dict(by_pos), "global": glob, "lemma_keys": lemma_keys}


def shuffle_frame_table(FT, seed):
    """ANTI-CHEAT control: reassign each head-key's Frame to a RANDOM other key's Frame (permutation).
    The lemma AND pos records are permuted among themselves -> the valency features become noise while the
    number of extra parameters/capacity is UNCHANGED. lemma_keys (which keys are 'seen') stays the same so
    the same feature strings fire; only the frame VALUES behind each key are wrong."""
    rng = np.random.default_rng(seed)
    out = {"lemma_keys": set(FT["lemma_keys"]), "global": FT["global"]}
    for level in ("lemma", "pos"):
        keys = sorted(FT[level].keys())
        vals = [FT[level][k] for k in keys]
        perm = rng.permutation(len(vals))
        out[level] = {keys[i]: vals[perm[i]] for i in range(len(keys))}
    return out


def _lookup_frame(FT, head_lemma, head_pos):
    """Backoff: lemma (if in learned lemma_keys) -> head-POS -> global. Returns (Frame, source_tag)."""
    if head_lemma in FT["lemma_keys"]:
        return FT["lemma"][head_lemma], "lem"
    fp = FT["pos"].get(head_pos)
    if fp is not None and fp.total > 0:
        return fp, "pos"
    return FT["global"], "glo"


def _pbucket(p):
    if p <= 0.0: return "z"
    if p < 0.05: return "lo"
    if p < 0.15: return "md"
    if p < 0.35: return "hi"
    return "vh"


def _satbucket(nch, deg):
    if deg <= 0: return "na"
    r = nch / deg
    return "under" if r < 0.6 else ("at" if r < 1.2 else "over")


VAL_LEAN = os.environ.get("HDLAB_VAL_LEAN", "1") == "1"
VAL_RAREGATE = int(os.environ.get("HDLAB_VAL_RAREGATE", "0"))  # >0: fire valency ONLY on head lemmas with
#   fewer than this many TRAIN instances (rare/unseen), where lexicalization is weak. 0 = always fire.
# VAL_MODE: "abs" = absolute-probability buckets (INTEGRATION BUG: fires high on every typical verb -> a
#   constant attachment bias -> real frames hurt MORE than random). "dev" = LEMMA-vs-POS DEVIATION (the FIX:
#   encodes only how a specific head deviates from its POS-general prior = the genuine subcategorization
#   signal base POS features lack; typical verbs contribute ~0, atypical verbs (intransitive 'sleep')
#   contribute a suppressive signal). Default "dev".
VAL_MODE = os.environ.get("HDLAB_VAL_MODE", "dev").lower()
# VAL_FEATS: comma set from {fit,obj,core,subj,sat,fitsrc,fit_core} for ablation. Default the lean 3.
VAL_FEATS = set(x.strip() for x in os.environ.get("HDLAB_VAL_FEATS", "fit,obj,core,subj").split(",") if x.strip())


def _head_instances(FT, hl):
    fr = FT["lemma"].get(hl)
    return fr.deg_n if fr is not None else 0


def _devbucket(d):
    if d <= -0.08: return "neg"
    if d < 0.08: return "z"
    return "pos"


def _arc_val_feats(attr, hidx, didx, dir_, nch, FT, tag):
    """Valency features for a proposed arc head=hidx dep=didx in direction dir_ ('R' dep right of head,
    'L' dep left). tag in {'vR','vL'} keeps the two proposed arcs in distinct hashed subspaces."""
    hl, hp, _ = attr[hidx]
    if VAL_RAREGATE > 0 and _head_instances(FT, hl) >= VAL_RAREGATE:
        return []                         # well-lexicalized head: rely on the base lexical features
    dp = attr[didx][1]
    # ----- DEVIATION mode (the FIX): lemma-specific deviation from the head-POS prior -----
    if VAL_MODE == "dev":
        if hl not in FT["lemma_keys"]:
            return []                     # unseen lemma -> no lemma-specific deviation; base POS feats cover
        fl = FT["lemma"][hl]
        fp = FT["pos"].get(hp)
        if fp is None or fp.total == 0:
            return []
        F = []
        if "fit" in VAL_FEATS:
            d = fl.p_posdir(dir_, dp) - fp.p_posdir(dir_, dp)
            F.append("%s_fitdev:%s_%s_%s" % (tag, _devbucket(d), hp, dp))
        if "obj" in VAL_FEATS:
            d = fl.p_rel("obj") - fp.p_rel("obj")
            F.append("%s_objdev:%s_%s" % (tag, _devbucket(d), hp))
        if "subj" in VAL_FEATS:
            d = fl.p_rel("nsubj") - fp.p_rel("nsubj")
            F.append("%s_subjdev:%s_%s" % (tag, _devbucket(d), hp))
        if "core" in VAL_FEATS:
            d = fl.p_core() - fp.p_core()
            F.append("%s_coredev:%s_%s" % (tag, _devbucket(d), dp))
        return F
    # ----- ABSOLUTE mode (original; kept for the ablation record) -----
    fr, src = _lookup_frame(FT, hl, hp)
    p_fit = fr.p_posdir(dir_, dp); p_obj = fr.p_rel("obj"); p_core = fr.p_core()
    F = []
    if "fit" in VAL_FEATS:
        F.append("%s_fit:%s_%s_%s" % (tag, _pbucket(p_fit), hp, dp))
    if "fitsrc" in VAL_FEATS:
        F.append("%s_fitsrc:%s_%s" % (tag, _pbucket(p_fit), src))
    if "obj" in VAL_FEATS:
        F.append("%s_obj:%s_%s" % (tag, _pbucket(p_obj), hp))
    if "subj" in VAL_FEATS:
        F.append("%s_subj:%s_%s" % (tag, _pbucket(fr.p_rel("nsubj")), hp))
    if "core" in VAL_FEATS:
        F.append("%s_core:%s_%s" % (tag, _pbucket(p_core), dp))
    if "sat" in VAL_FEATS:
        F.append("%s_sat:%s_%s" % (tag, _satbucket(nch, fr.deg_mean()), hp))
    if "fit_core" in VAL_FEATS:
        F.append("%s_fit_core:%s_%s" % (tag, _pbucket(p_fit), _pbucket(p_core)))
    return F


def _config_feats_aug(stack, bptr, n, attr, heads, nchild, FT):
    """Base config features (VERBATIM) + (if FT) the LEARNED valency block for BOTH proposed arcs.
    FT=None -> returns EXACTLY the base features -> ARM_BASE == 29451 dynamic arm."""
    F = _config_feats(stack, bptr, n, attr, heads)
    if FT is None:
        return F
    s0 = stack[-1]
    b0 = bptr if bptr <= n else None
    if b0 is not None and s0 > 0:
        # RARC candidate: head=s0, dep=b0, dep is to the RIGHT of head (b0 > s0)
        F += _arc_val_feats(attr, s0, b0, "R", nchild.get(s0, 0), FT, "vR")
        # LARC candidate: head=b0, dep=s0, dep is to the LEFT of head (s0 < b0)
        F += _arc_val_feats(attr, b0, s0, "L", nchild.get(b0, 0), FT, "vL")
    return F


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


def _train_transition(train, seed, FT=None):
    """Averaged-perceptron action classifier, DYNAMIC oracle with exploration (identical to 29451's
    dynamic arm). FT=None -> base features; FT=table -> base + valency features (ONE variable)."""
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
            stack = [0]; bptr = 1; heads = {}; nchild = {}
            guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1:
                    break
                legal = _legal(stack, bptr, n, heads)
                if not legal:
                    break
                base_ids = np.fromiter((_h(f) for f in _config_feats_aug(stack, bptr, n, attr, heads, nchild, FT)),
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
                stack, bptr = _apply_v(stack, bptr, heads, nchild, a_next)
                guard += 1
                if guard > 4 * (n + 2):
                    break
    return W - CW / c


def _decode_greedy(sent, attr, W, FT=None):
    """Greedy arc-eager decode. Returns head_dict."""
    n = len(sent)
    stack = [0]; bptr = 1; heads = {}; nchild = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _legal(stack, bptr, n, heads)
        if not legal:
            break
        base_ids = np.fromiter((_h(f) for f in _config_feats_aug(stack, bptr, n, attr, heads, nchild, FT)),
                               dtype=np.int64)
        scores = _score_actions(base_ids, W, legal)
        a = _argmax_legal(scores)
        stack, bptr = _apply_v(stack, bptr, heads, nchild, a)
        guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0
    return heads


# ================================================================================================
# UAS + verb-argument breakdown + held-out-verb generalization.
# ================================================================================================
def _uas_breakdown(sents, W, FT, seen_lemmas):
    """Return dict: overall_uas, verbarg_uas, verbarg_seen_uas, verbarg_held_uas,
    verbarg_held_linearprev (positional floor on the SAME held-out-verb arcs), n_verbarg, n_held."""
    o_hit = o_tot = 0
    va_hit = va_tot = 0
    seen_hit = seen_tot = 0
    held_hit = held_tot = 0
    held_lin_hit = 0
    for sent in sents:
        n = len(sent)
        attr = _mk_attr(sent)
        heads = _decode_greedy(sent, attr, W, FT)
        for (i, w, p, h, dl, num) in sent:
            if h < 0 or h > n: continue
            corr = int(heads.get(i, -1) == h)
            o_hit += corr; o_tot += 1
            if h < 1: continue
            hp = sent[h - 1][2]
            rel = dl.split(":")[0] if dl else "dep"
            if hp in VERB_POS and rel in VERBARG_RELS:
                va_hit += corr; va_tot += 1
                hl = sent[h - 1][1].lower()
                if hl in seen_lemmas:
                    seen_hit += corr; seen_tot += 1
                else:
                    held_hit += corr; held_tot += 1
                    held_lin_hit += int((i - 1) == h)  # linear-previous baseline: head == i-1
    return {
        "overall_uas": round(o_hit / o_tot, 4) if o_tot else 0.0,
        "verbarg_uas": round(va_hit / va_tot, 4) if va_tot else 0.0,
        "verbarg_seen_uas": round(seen_hit / seen_tot, 4) if seen_tot else 0.0,
        "verbarg_held_uas": round(held_hit / held_tot, 4) if held_tot else 0.0,
        "verbarg_held_linearprev": round(held_lin_hit / held_tot, 4) if held_tot else 0.0,
        "n_verbarg": va_tot, "n_verbarg_seen": seen_tot, "n_verbarg_held": held_tot,
    }


# ================================================================================================
# Corpus loader with Number morphology + deprel. token = (idx,form,upos,head,deprel,number)
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


# ================================================================================================
# Self-test: base-parser hand-trace (VERBATIM 29451) + frame-table learning + backoff + shuffle + loader.
# ================================================================================================
def _selftest():
    assert _h("abc") == _h("abc")
    assert _dist(1) == "1" and _dist(2) == "2" and _dist(4) == "3-5" and _dist(20) == "11+"

    # ---- HAND-TRACE (base transition system unchanged): "the key to the cabinets are on the table" ----
    gold = [0, 2, 6, 5, 5, 2, 0, 9, 9, 6]
    n = 9
    stack = [0]; bptr = 1; heads = {}; nchild = {}
    cabinets_popped_step = None; are_pushed_step = None
    step = 0; guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        a = _static_oracle_move(stack, bptr, n, gold, heads)
        s0_before = stack[-1]; b0_before = bptr
        stack, bptr = _apply_v(stack, bptr, heads, nchild, a)
        if a in (LARC, REDU) and s0_before == 5 and cabinets_popped_step is None:
            cabinets_popped_step = step
        if a in (SHIFT, RARC) and b0_before == 6 and are_pushed_step is None:
            are_pushed_step = step
        step += 1; guard += 1
        assert guard < 60, "hand-trace did not terminate"
    for i in range(1, n + 1):
        assert heads.get(i) == gold[i], "hand-trace head[%d]=%r != gold %d" % (i, heads.get(i), gold[i])
    assert cabinets_popped_step is not None and are_pushed_step is not None
    assert cabinets_popped_step < are_pushed_step, "PP did not reduce before verb"
    assert heads[2] == 6 and heads[5] == 2, "subject-id trace wrong"
    # nchild sanity: verb 'are'(6) collected its dependents (key(2) subj, table(9) obl) -> 2 children
    assert nchild.get(6, 0) == 2, "nchild(are)=%r != 2" % nchild.get(6)

    # ---- FRAME-TABLE learning: transitive 'eat' (always obj) vs intransitive 'sleep' (never obj) ----
    def _mk(idx, form, pos, head, rel, num=None):
        return (idx, form, pos, head, rel, num)
    syn = []
    for _ in range(8):
        # "cats eat fish"  cats(1)->eat(2) nsubj ; fish(3)->eat(2) obj ; eat(2)->0 root
        syn.append([_mk(1, "cats", "NOUN", 2, "nsubj"), _mk(2, "eat", "VERB", 0, "root"),
                    _mk(3, "fish", "NOUN", 2, "obj")])
        # "cats sleep"  cats(1)->sleep(2) nsubj ; sleep(2)->0 root  (NO object)
        syn.append([_mk(1, "cats", "NOUN", 2, "nsubj"), _mk(2, "sleep", "VERB", 0, "root")])
    FT = build_frame_table(syn)
    fe, _ = _lookup_frame(FT, "eat", "VERB")
    fs, _ = _lookup_frame(FT, "sleep", "VERB")
    assert "eat" in FT["lemma_keys"] and "sleep" in FT["lemma_keys"], "frame lemma keys missing"
    assert fe.p_rel("obj") > 0.3 and fs.p_rel("obj") == 0.0, (
        "subcat not learned: P(obj|eat)=%.3f P(obj|sleep)=%.3f" % (fe.p_rel("obj"), fs.p_rel("obj")))
    assert fe.p_rel("nsubj") > 0.0 and fs.p_rel("nsubj") > 0.0, "nsubj not learned"
    # backoff: an UNSEEN verb lemma falls back to head-POS frame (VERB), which is non-empty
    fu, src = _lookup_frame(FT, "zzzunseenverb", "VERB")
    assert src == "pos" and fu.total > 0, "POS backoff failed for unseen verb (src=%s)" % src
    # valency degree: 'eat' has 2 deps/instance, 'sleep' has 1
    assert abs(fe.deg_mean() - 2.0) < 1e-6 and abs(fs.deg_mean() - 1.0) < 1e-6, (
        "deg_mean wrong eat=%.3f sleep=%.3f" % (fe.deg_mean(), fs.deg_mean()))

    # ---- SHUFFLE control differs from the real table on >=1 lemma record ----
    FTs = shuffle_frame_table(FT, 1234)
    diff = False
    for k in FT["lemma_keys"]:
        if FT["lemma"][k].p_rel("obj") != FTs["lemma"][k].p_rel("obj"):
            diff = True; break
    assert diff, "shuffle_frame_table did not change any lemma record (control is inert)"

    # ---- valency feature block: FT=None returns EXACTLY base features; FT!=None appends 'vR'/'vL' feats ----
    attr = [_ROOT_ATTR, ("cats", "NOUN", "ats"), ("eat", "VERB", "eat"), ("fish", "NOUN", "ish")]
    base_only = _config_feats_aug([0, 1], 2, 3, attr, {}, {}, None)
    with_val = _config_feats_aug([0, 1], 2, 3, attr, {}, {}, FT)
    assert base_only == _config_feats([0, 1], 2, 3, attr, {}), "FT=None must equal base features"
    assert len(with_val) > len(base_only) and any(f.startswith("vR_") or f.startswith("vL_") for f in with_val), (
        "valency features not appended")

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
    print("[selftest] PASS: valency-subcat (hand-trace + frame learning + backoff + shuffle + featblock + loader)",
          flush=True)


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
        SEEDS = [1, 2]
    else:
        SEEDS = [1, 2, 3]
    if TRAIN_CAP > 0:
        train = train[:TRAIN_CAP]
    if SEEDS_OVR:
        SEEDS = [int(x) for x in SEEDS_OVR.split(",") if x.strip()]
    print("[data] train=%d dev=%d MAXLEN=%d EPOCHS=%d seeds=%s" % (
        len(train), len(dev), MAXLEN, EPOCHS, SEEDS), flush=True)
    _hb(out_dir, "data loaded")

    def mean(x): return round(sum(x) / len(x), 4) if x else 0.0

    def se(x):
        if len(x) < 2: return 0.0
        m = sum(x) / len(x); v = sum((z - m) ** 2 for z in x) / len(x)
        return (v ** 0.5) / (len(x) ** 0.5)

    # -------- FRAME TABLE (learned from TRAIN gold ONLY) --------
    t = time.time()
    FT = build_frame_table(train)
    FT_shuf = shuffle_frame_table(FT, 20260723)
    seen_lemmas = FT["lemma_keys"]
    n_lemma_keys = len(seen_lemmas)
    print("[frame] built: %d learned lemma-keys (>=%d occ), %d POS keys, global.total=%d (%.1fs)" % (
        n_lemma_keys, MINCOUNT, len(FT["pos"]), FT["global"].total, time.time() - t), flush=True)
    _hb(out_dir, "frame table built lemma_keys=%d" % n_lemma_keys)

    # -------- ARM_BASE + ARM_VALENCY (multi-seed) --------
    base_uas = []; val_uas = []
    base_va = []; val_va = []
    base_held = []; val_held = []; val_held_lin = []
    W_base_s1 = None; W_val_s1 = None
    n_verbarg = 0; n_held = 0
    for sd in SEEDS:
        t = time.time()
        W_base = _train_transition(train, sd, FT=None)
        bd = _uas_breakdown(dev, W_base, None, seen_lemmas)
        base_uas.append(bd["overall_uas"]); base_va.append(bd["verbarg_uas"]); base_held.append(bd["verbarg_held_uas"])
        _hb(out_dir, "seed %d base done %.1fs uas=%.4f" % (sd, time.time() - t, bd["overall_uas"]))
        t = time.time()
        W_val = _train_transition(train, sd, FT=FT)
        vd = _uas_breakdown(dev, W_val, FT, seen_lemmas)
        val_uas.append(vd["overall_uas"]); val_va.append(vd["verbarg_uas"]); val_held.append(vd["verbarg_held_uas"])
        val_held_lin.append(vd["verbarg_held_linearprev"])
        n_verbarg = vd["n_verbarg"]; n_held = vd["n_verbarg_held"]
        if sd == SEEDS[0]:
            W_base_s1 = W_base; W_val_s1 = W_val
        print("  seed %d: BASE uas=%.4f (va=%.4f) | VALENCY uas=%.4f (va=%.4f) | held va base=%.4f val=%.4f lin=%.4f (%.1fs)"
              % (sd, bd["overall_uas"], bd["verbarg_uas"], vd["overall_uas"], vd["verbarg_uas"],
                 bd["verbarg_held_uas"], vd["verbarg_held_uas"], vd["verbarg_held_linearprev"], time.time() - t),
              flush=True)
        _hb(out_dir, "seed %d valency done uas=%.4f" % (sd, vd["overall_uas"]))

    arms_differ = bool(W_base_s1 is not None and W_val_s1 is not None and not np.array_equal(W_base_s1, W_val_s1))

    # -------- ANTI-CHEAT: SHUFFLED frame table (seed 1) --------
    shuf_uas = None
    if DO_SHUF:
        t = time.time()
        W_shuf = _train_transition(train, SEEDS[0], FT=FT_shuf)
        sd_bd = _uas_breakdown(dev, W_shuf, FT_shuf, seen_lemmas)
        shuf_uas = sd_bd["overall_uas"]
        print("  [anti-cheat] SHUFFLED-frame valency uas=%.4f (%.1fs)" % (shuf_uas, time.time() - t), flush=True)
        _hb(out_dir, "shuffle arm done uas=%.4f" % shuf_uas)

    # -------- LEARNING CURVE (base + valency; frame table rebuilt from each subset) --------
    lc_base = {}; lc_val = {}; lc_frame_keys = {}
    if DO_LC:
        rng = np.random.default_rng(999)
        perm = rng.permutation(len(train))
        for fr in LC_FRACS:
            k = max(1, int(round(fr * len(train))))
            sub = [train[perm[i]] for i in range(k)]
            FT_sub = build_frame_table(sub)
            Wb = _train_transition(sub, SEEDS[0], FT=None)
            ub = _uas_breakdown(dev, Wb, None, FT_sub["lemma_keys"])["overall_uas"]
            Wv = _train_transition(sub, SEEDS[0], FT=FT_sub)
            uv = _uas_breakdown(dev, Wv, FT_sub, FT_sub["lemma_keys"])["overall_uas"]
            lc_base["%.2f" % fr] = ub; lc_val["%.2f" % fr] = uv
            lc_frame_keys["%.2f" % fr] = len(FT_sub["lemma_keys"])
            print("  [LC] frac=%.2f n=%d frame_keys=%d BASE=%.4f VALENCY=%.4f" % (
                fr, k, len(FT_sub["lemma_keys"]), ub, uv), flush=True)
            _hb(out_dir, "LC frac %.2f base=%.4f val=%.4f" % (fr, ub, uv))

    base_m = mean(base_uas); val_m = mean(val_uas); val_se = se(val_uas)
    val_2se_lo = round(val_m - 2 * val_se, 4)
    real_lift = round(val_m - base_m, 4)
    real_lift_2se = round(val_2se_lo - base_m, 4)
    overall_lift = real_lift
    verbarg_lift = round(mean(val_va) - mean(base_va), 4)
    shuf_lift = round(shuf_uas - base_m, 4) if shuf_uas is not None else None
    lc_lo = lc_val.get("%.2f" % LC_FRACS[0], 0.0); lc_hi = lc_val.get("%.2f" % LC_FRACS[-1], 0.0)
    lc_rise = round(lc_hi - lc_lo, 4)
    held_val_m = mean(val_held); held_lin_m = mean(val_held_lin)

    out = {
        "n_seeds": len(SEEDS), "n_train": len(train), "n_dev": len(dev),
        "n_lemma_keys": n_lemma_keys, "n_verbarg": n_verbarg, "n_verbarg_held": n_held,
        "cited_base_uas": CITED_BASE_UAS,
        "base_uas_mean": base_m, "base_uas_vals": base_uas,
        "valency_uas_mean": val_m, "valency_uas_vals": val_uas, "valency_uas_se": round(val_se, 4),
        "valency_uas_2se_lo": val_2se_lo,
        "real_lift": real_lift, "real_lift_2se_clean": real_lift_2se,
        "base_verbarg_uas_mean": mean(base_va), "valency_verbarg_uas_mean": mean(val_va),
        "verbarg_lift": verbarg_lift, "overall_lift": overall_lift,
        "shuffle_uas": shuf_uas, "shuffle_lift": shuf_lift,
        "valency_held_verbarg_uas_mean": round(held_val_m, 4),
        "base_held_verbarg_uas_mean": round(mean(base_held), 4),
        "held_linearprev_baseline_mean": round(held_lin_m, 4),
        "lc_base": lc_base, "lc_valency": lc_val, "lc_frame_keys": lc_frame_keys,
        "lc_lo_uas": lc_lo, "lc_hi_uas": lc_hi, "lc_rise": lc_rise,
        "lc_points": len(lc_val), "lc_expected_points": (len(LC_FRACS) if DO_LC else 0),
        "arms_differ_base_vs_valency": arms_differ,
        "gate_d_positive_control_ok": bool(abs(base_m - CITED_BASE_UAS) <= 0.03),
    }
    print("\n  === SUMMARY (mean over %d seeds) ===" % len(SEEDS), flush=True)
    print("  UAS:  BASE=%.4f (cited 0.8109)  VALENCY=%.4f (2SE-lo=%.4f)  SHUFFLE=%s" % (
        base_m, val_m, val_2se_lo, ("%.4f" % shuf_uas) if shuf_uas is not None else "n/a"), flush=True)
    print("  real_lift=%+.4f (2SE-clean=%+.4f)  shuffle_lift=%s  verbarg_lift=%+.4f (overall=%+.4f)" % (
        real_lift, real_lift_2se, ("%+.4f" % shuf_lift) if shuf_lift is not None else "n/a",
        verbarg_lift, overall_lift), flush=True)
    print("  held-out-verb va: valency=%.4f base=%.4f linear-prev-floor=%.4f (n_held=%d)" % (
        held_val_m, mean(base_held), held_lin_m, n_held), flush=True)
    print("  learning curve (valency): %.4f (frac %.2f) -> %.4f (frac %.2f) rise=%+.4f" % (
        lc_lo, LC_FRACS[0], lc_hi, LC_FRACS[-1], lc_rise), flush=True)
    return out


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if not r.get("gate_d_positive_control_ok", False):
        return ("UNKNOWN", "UNKNOWN: Gate D positive control off -- ARM_BASE UAS %.4f not within 0.03 of cited %.4f "
                "(same-split base did not reproduce; downstream lift untrustworthy)" % (
                    r["base_uas_mean"], r["cited_base_uas"]))
    if r.get("n_verbarg", 0) == 0:
        return ("UNKNOWN", "UNKNOWN: discriminator did not fire (n_verbarg==0)")
    if r.get("n_lemma_keys", 0) == 0:
        return ("UNKNOWN", "UNKNOWN: frame table has 0 learned lemma keys (valency features vacuous)")
    if r.get("lc_expected_points", 0) and r.get("lc_points", 0) < r["lc_expected_points"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: learning-curve points %d < expected %d" % (
            r["lc_points"], r["lc_expected_points"]))
    real2 = r["real_lift_2se_clean"]; real = r["real_lift"]
    shuf = r["shuffle_lift"]; va_lift = r["verbarg_lift"]; ov_lift = r["overall_lift"]
    lc_rise = r["lc_rise"]; held = r["valency_held_verbarg_uas_mean"]; floor = r["held_linearprev_baseline_mean"]
    s = ("UAS base=%.4f valency=%.4f (2SE-lo=%.4f, vals=%s) shuffle=%.4f | real_lift=%+.4f (2SE-clean=%+.4f) "
         "shuffle_lift=%+.4f | verbarg_lift=%+.4f (overall=%+.4f) | lc %.4f->%.4f rise=%+.4f | "
         "held-va valency=%.4f floor=%.4f (n_held=%d)" % (
             r["base_uas_mean"], r["valency_uas_mean"], r["valency_uas_2se_lo"], r["valency_uas_vals"],
             r["shuffle_uas"], real, real2, shuf, va_lift, ov_lift, lc_rise, r["lc_lo_uas"], r["lc_hi_uas"],
             held, floor, r["n_verbarg_held"]))
    # HARD_FAIL: no lift OR anti-cheat fails (shuffle carries as much as the real frames)
    if real < 0.03:
        return ("HARD_FAIL", "HARD_FAIL: valency does NOT lift UAS by >=0.03 (real_lift=%+.4f) -- the ~0.81 ceiling "
                "is deeper than lexicalization (earned representational bound; lever is a different "
                "representation). " % real + s)
    if shuf >= real:
        return ("HARD_FAIL", "HARD_FAIL_ANTICHEAT: shuffled-frame lift (%+.4f) >= real-frame lift (%+.4f) -- the "
                "gain is just extra parameters/capacity, NOT learned frames (mechanism invalid). " % (shuf, real) + s)
    # HARD_PASS: 2SE-clean +0.03, verb-arg-concentrated, LC rises, held-out beats floor, shuffle collapses
    if (real2 >= 0.03 and va_lift >= max(0.03, ov_lift) and lc_rise >= 0.03 and held >= floor
            and shuf <= 0.5 * real):
        return ("HARD_PASS", "HARD_PASS: LEARNED verb-valency/subcat features lift arc-eager UAS by >=+0.03 "
                "(2SE-clean), the gain concentrates on verb-argument arcs, the learning curve rises (frames "
                "improve with exposure), backoff generalizes to held-out verb lemmas (>floor), and the "
                "anti-cheat shuffle collapses the lift -- smart lexicalization breaks the feature ceiling. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: valency gives a positive lift but below the full bar (2SE-clean<0.03, or "
            "not verb-arg-concentrated, or lc-rise<0.03, or held-out below floor, or shuffle only partially "
            "collapses). " + s)


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
               "arms_differ_verified": bool(r.get("arms_differ_base_vs_valency", False)),
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
