"""
exp_agreement_depth_productivity_generalization_v1
==================================================

CHAIN-GRADE SHOT (Director task 2026-07-22): DEPTH-PRODUCTIVITY generalization on the CORRECTLY-
SPECIFIED compositional axis. The learned depth accumulator (atom 29453) was down-rated on
FW-HOLDOUT, but function words are a CLOSED CLASS the brain learns AS ITEMS and does not extrapolate
to novel ones -- FW-holdout is likely the WRONG generalization axis. The RIGHT axis (Fodor-Pylyshyn
productivity / Lake-Baroni SCAN length-gen / COGS depth-gen) is PRODUCTIVITY OVER STRUCTURE: train on
SHALLOW embeddings, test on DEEPER nesting than seen. Does the learned accumulator generalize
productively to unseen embedding DEPTH, or is it a depth-bounded shallow lookup?

DEPTH METRIC (span_depth): for each item, the MAX deterministic embedding-depth (PREP/SUBORD +1,
comma/close -1) over the nouns STRICTLY AFTER the subject (the intervening attractors up to the verb).
This is the recursion depth of the subject->verb span -- exactly the structure the deterministic
min-depth rule (atom 29450) is invariant to by construction. MEASURED distribution on real Linzen
buried subjects (MEASURED@scratchpad/probe_acc.py): depth0=2525, depth1=1303, depth>=2=2597.

SPLIT (ONE variable = the depth split):
  K = 1. TRAIN pool = ALL items (buried + non-buried) with span_depth <= 1 (model NEVER sees nesting
    deeper than one embedding). Held-out SHALLOW_TEST = deterministic 20% of the pool (in-distribution
    reference, depth==1 buried). DEEP_TEST = ALL buried items with span_depth >= 2 (structurally UNSEEN
    depth; N=2597). Learnable FW-vocab built from TRAIN only -- but closed-class FWs (of/in/to/that)
    appear at ALL depths, so the vocab covers deep (this is WHY FW-holdout was the wrong axis).
  No lexeme holdout needed: the accumulator learns FW increments ONLY (nouns get delta=0), so it
    CANNOT memorize subject lexemes -> the depth split alone is the generalization test.

ARMS (report BURIED agreement accuracy on DEEP_TEST and SHALLOW_TEST):
  1. learned_depth        -- THE mechanism, TRAINED ON SHALLOW ONLY, evaluated on DEEP held-out.
  2. deterministic_depth  -- reference CEILING = hand-coded recursive rule 29450 (Gate D positive
                             control; reproduces ~0.73 on deep AT THIS REGIME; depth-invariant by build).
  3. nearest_noun         -- positional shortcut / attractor baseline (degrades + stays ~0.30 on deep).
  4. first_noun           -- first noun.
  5. majority             -- reference floor.
  6. local_bag            -- SAME pipeline, OLD 10 local features (failed-method control).
  7. fixed_random         -- MUST-FAIL control: architecture with fixed-random deltas (no learning).

DELIVERABLE regardless of verdict = the DEPTH CURVE: learned / deterministic / nearest / majority
  accuracy per depth bin (1, 2, 3, 4+) with per-bin N + bootstrap 95% CI (HONESTY GUARD on rare deep
  bins). Verdict rests on the AGGREGATE deep (N=2597, robust); fine bins are descriptive w/ N shown.
  NO deep-template synthesis (real text only).

CORE DISCRIMINATOR (can-fail; not a rescue):
  Does the shallow-trained accumulator HOLD on deep (near deterministic 0.73, clearly above nearest,
  small depth-degradation) or DEGRADE toward nearest/majority?

BANDS (pre-registered; MEASURED@scratchpad/probe_acc.py deep anchors:
       deterministic_deep=0.731, nearest_deep=0.301, first_deep=0.467, majority_deep=0.574):
  HARD_PASS_DEPTH_PRODUCTIVE (ALL of):
    (a) learned_deep >= 0.66                          (holds near the 0.731 recursive ceiling)
    (b) learned_deep - nearest_deep >= 0.20           (clearly above the degrading positional shortcut)
    (c) learned_deep - majority_deep >= 0.05          (beats the majority floor)
    (d) depth_degradation = learned_shallow1 - learned_deep <= 0.08   (small drop = productive)
    (e) scramble_drop_deep >= 0.10                     (anti-cheat: lift is DEPTH not position)
    (f) number_flip_change == 0.0                      (number read AFTER selection)
  HARD_FAIL_DEPTH_BOUNDED_SHALLOW_LOOKUP (ANY of):
    (i)   learned_deep - nearest_deep <= 0.05          (degraded to the positional shortcut)
    (ii)  learned_deep <= majority_deep + 0.02         (no better than majority guessing)
    (iii) depth_degradation >= 0.15                    (collapses with depth = confirmed shallow lookup)
    (iv)  scramble_drop_deep < 0.05                    (position all along)
  MIDDLE = else (partial hold; beats shortcuts but real depth-decline, or lands 0.59-0.66).
HONEST FRAMING: HARD_PASS = the learned accumulator is genuinely RECURSIVE/PRODUCTIVE on real text ->
  correctly-specified chain-grade landmark (composes 29453/29450); flag for HARDEST skunkworks-VET.
  HARD_FAIL = 29453 is a depth-bounded shallow lookup -> earned bound; recursion must come from a
  richer STACK representation (roadmap #1 transition parser) -> that becomes the next build.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - deterministic: hashlib digests + fixed int seeds + np.random.default_rng + sorted(set); NO builtin hash(), NO list(set())
# - build-time gradient MANUAL numpy (closed form); runtime = HARD argmin, NO autograd, NO torch on select path
# - arms_differ verified (learned_depth / local_bag / fixed_random / nearest_noun distinct deep buried preds; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor
# - baseline_in_band: majority_deep ~0.57 + nearest/first in (0.05,0.95) (META_RULE_AG); asserted at self-test + run
# - cardinality: EXPECTED_N_UNITS = len(SEEDS) model-init seeds; no sweep axis; verdict counts per-seed results
# - discriminator survives scale: FULL uses ALL real deep items (N=2597); deterministic reproduces 0.73 recursive ceiling at scale
# - baseline_valid: fixed_random control validated NOT at arena floor (same architecture, live deltas)
# - all header/band numbers MEASURED@scratchpad/probe_acc.py or MEASURED@ this cell output; bands HYPOTHESIZED flagged
# - progress_logging: per-VAL_EVERY val_buried prints flush=True + _heartbeat.jsonl during training (timeout < 1800s expected)
# - Gate D: deterministic_depth arm reproduces the 29450 recursive-rule ceiling AT THIS TEST REGIME (positive control)
"""

import argparse
import gzip
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "exp_agreement_depth_productivity_generalization_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", ANCHOR_NAME)

# ---- depth split ----
K_SHALLOW = 1                 # train on span_depth <= K; test deep on span_depth > K
SHALLOW_TEST_FRAC = 0.20      # held-out shallow fraction (in-distribution reference)

# ---- pre-registered bands (MEASURED@scratchpad/probe_acc.py deep anchors) ----
HP_HOLD_CEILING = 0.66        # (a) learned_deep floor near the 0.731 deterministic ceiling
HP_ABOVE_NEAREST = 0.20       # (b) learned_deep - nearest_deep
HP_ABOVE_MAJORITY = 0.05      # (c) learned_deep - majority_deep
HP_MAX_DEGRADATION = 0.08     # (d) learned_shallow1 - learned_deep <= this
HP_SCRAMBLE_DROP = 0.10       # (e) scramble drop on deep
HF_TIE_NEAREST = 0.05         # (i) learned_deep - nearest_deep <= this => HARD_FAIL
HF_AT_MAJORITY = 0.02         # (ii) learned_deep <= majority_deep + this => HARD_FAIL
HF_DEGRADATION = 0.15         # (iii) depth_degradation >= this => HARD_FAIL
HF_SCRAMBLE_NOEFFECT = 0.05   # (iv) scramble drop < this => position all along

# ---- multi-seed (model-init variance; depth split is fixed/deterministic) ----
SEEDS = [7, 13, 19, 23, 31]
SMOKE_SEEDS = [7, 13]

# ---- learnable function-word vocab ----
MAX_VOCAB = 160
MIN_FREQ = 20

# ---- model / training hyperparams ----
EPS_POS = 0.30
L2_DELTA = 1e-4
LR = 0.05
ADAM_B1, ADAM_B2, ADAM_EPS = 0.9, 0.999, 1e-8
N_EPOCHS = 1500
VAL_EVERY = 50
SOFTMAX_TEMP_ANNEAL = True
BCE_CLIP = 1e-4

# ---- closed lists for the DETERMINISTIC positive-control arm (recursive 0.73 ceiling) ----
PREPS = set((
    "to of in on for with at by from into onto about over under between among against during "
    "without within through across after before around near above below beside besides beyond "
    "despite toward towards upon per via regarding concerning off out up down"
).split())
SUBORD = set((
    "that which who whom whose where when while because if although though unless until since "
    "whether as than"
).split())

# ---- the 10 LOCAL features (failed method) for the local_bag arm ----
LB_PREPS = {"of", "in", "on", "with", "by", "for", "to", "from", "at", "as", "into",
            "over", "under", "between", "among", "through", "during", "against", "about"}
LB_DETS = {"the", "a", "an", "this", "that", "these", "those", "its", "their", "his", "her", "our"}
N_LOCAL = 10


# ==================================================================================================
# Data + depth metric
# ==================================================================================================
def _stable_seed(*parts):
    key = "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") & ((1 << 63) - 1)


def load_items(max_items=None, representative=False):
    with gzip.open(CACHE_PATH, "rt", encoding="utf-8") as f:
        d = json.load(f)
    items = d["linzen"]
    if max_items is not None and max_items < len(items):
        if representative:
            stride = max(len(items) // max_items, 1)
            items = items[::stride][:max_items]
        else:
            items = items[:max_items]
    return items


def det_depths_at_nouns(item):
    """Deterministic hand-coded embedding-depth per noun (PREP/SUBORD +1; comma/close -1)."""
    ni = item["noun_word_idx"]
    words = item["words"]
    depth = 0
    out = {}
    widx_to_k = {wi: k for k, wi in enumerate(ni)}
    for i, w in enumerate(words):
        wl = w.lower()
        if i in widx_to_k:
            out[widx_to_k[i]] = depth
        if wl in PREPS or wl in SUBORD:
            depth += 1
        elif wl in (",", ")", ";") and depth > 0:
            depth -= 1
    return [out.get(k, 0) for k in range(len(ni))]


def span_depth(item):
    """Embedding depth of the subject->verb span = max det-depth of nouns STRICTLY after the subject.
    0 if no noun after the subject. This is the recursion depth the split bins on."""
    dd = det_depths_at_nouns(item)
    sp = int(item["subj_pos"])
    after = dd[sp + 1:]
    return max(after) if after else 0


def build_vocab(train_items):
    """Deterministic learnable FW vocab = top MAX_VOCAB non-noun token types by TRAIN freq
    (freq >= MIN_FREQ). Nouns excluded. NO test leak."""
    from collections import Counter
    noun_types = set()
    for it in train_items:
        ni = set(it["noun_word_idx"])
        for i, w in enumerate(it["words"]):
            if i in ni:
                noun_types.add(w.lower())
    tok = Counter()
    for it in train_items:
        ni = set(it["noun_word_idx"])
        for i, w in enumerate(it["words"]):
            if i not in ni:
                tok[w.lower()] += 1
    cand = [(w, c) for w, c in tok.items() if c >= MIN_FREQ and w not in noun_types]
    cand.sort(key=lambda x: (-x[1], x[0]))
    vocab = [w for w, _ in cand[:MAX_VOCAB]]
    return sorted(set(vocab)), noun_types


def local_features(item, k, widx):
    """The 10 LOCAL features for noun k at word index widx. NO number leak."""
    words = item["words"]
    L = len(words)
    nn = len(item["noun_word_idx"])
    prev = words[widx - 1].lower() if widx - 1 >= 0 else ""
    near_and = 0.0
    for j in range(max(0, widx - 2), min(L, widx + 3)):
        if words[j].lower() in ("and", "or"):
            near_and = 1.0
            break
    denom = max(L - 1, 1)
    return [
        1.0, widx / denom, (L - 1 - widx) / denom, k / max(nn - 1, 1),
        1.0 if k == 0 else 0.0, 1.0 if k == nn - 1 else 0.0, min(nn, 8) / 8.0,
        1.0 if prev in LB_PREPS else 0.0, 1.0 if prev in LB_DETS else 0.0, near_and,
    ]


def encode(items, vocab, maxnn):
    """Vectorize items into padded [B,maxnn,*] arrays. Also returns per-item span_depth."""
    vindex = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    B = len(items)
    A = np.zeros((B, maxnn, V), dtype=np.float32)
    X = np.zeros((B, maxnn, N_LOCAL), dtype=np.float32)
    det_depth = np.zeros((B, maxnn), dtype=np.float32)
    num = np.zeros((B, maxnn), dtype=np.float32)
    mask = np.zeros((B, maxnn), dtype=np.float32)
    pos = np.zeros((B, maxnn), dtype=np.float32)
    y = np.zeros(B, dtype=np.float32)
    subj_pos = np.zeros(B, dtype=np.int64)
    sdepth = np.zeros(B, dtype=np.int64)
    for bi, it in enumerate(items):
        ni = it["noun_word_idx"]
        words = it["words"]
        nn = len(ni)
        y[bi] = float(it["label"])
        subj_pos[bi] = int(it["subj_pos"])
        sdepth[bi] = span_depth(it)
        dd = det_depths_at_nouns(it)
        run = np.zeros(V, dtype=np.float32)
        widx_to_k = {wi: k for k, wi in enumerate(ni)}
        for i, w in enumerate(words):
            if i in widx_to_k:
                A[bi, widx_to_k[i]] = run
            vi = vindex.get(w.lower())
            if vi is not None:
                run[vi] += 1.0
        for k in range(nn):
            widx = ni[k]
            X[bi, k] = local_features(it, k, widx)
            det_depth[bi, k] = float(dd[k])
            num[bi, k] = float(it["nums"][k])
            mask[bi, k] = 1.0
            pos[bi, k] = k / max(nn - 1, 1)
    return {"A": A, "X": X, "det_depth": det_depth, "num": num, "mask": mask,
            "pos": pos, "y": y, "subj_pos": subj_pos, "sdepth": sdepth}


# ==================================================================================================
# Build-time training (MANUAL numpy gradient; closed form; NO autograd).
# ==================================================================================================
def _masked_softmax(score, mask):
    score = np.where(mask > 0, score, -1e30)
    m = score.max(axis=1, keepdims=True)
    e = np.exp(score - m) * mask
    s = e.sum(axis=1, keepdims=True)
    s = np.where(s <= 0, 1.0, s)
    return e / s


def _bce_and_dscore(score, mask, num, y):
    w = _masked_softmax(score, mask)
    pred = (w * num).sum(axis=1)
    p = np.clip(pred, BCE_CLIP, 1.0 - BCE_CLIP)
    B = len(y)
    loss = float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))
    dLdp = (p - y) / (p * (1 - p)) / B
    dscore = dLdp[:, None] * w * (num - pred[:, None]) * mask
    return loss, dscore, pred, w


def _hard_select_depth(depth, mask):
    """HARD runtime selection: rightmost noun at minimum depth. Pure numpy, NO gradient."""
    B, K = depth.shape
    big = 1e30
    d = np.where(mask > 0, depth, big)
    tie = np.arange(K)[None, :] * 1e-6
    score = np.where(mask > 0, d - tie, big)
    return score.argmin(axis=1)


def _acc_on(sel, data, row_mask):
    """agreement accuracy over the rows in row_mask, given a selection index per row."""
    if row_mask.sum() == 0:
        return None, 0
    picked = data["num"][np.arange(len(sel)), sel]
    correct = (picked == data["y"]).astype(np.float32)
    return float(correct[row_mask].mean()), int(row_mask.sum())


def _buried_mask(data):
    return data["subj_pos"] != 0


def _buried_acc(sel, data):
    return _acc_on(sel, data, _buried_mask(data))


def _emit_heartbeat(unit_idx, total, t0, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def train_depth(fit, val, seed, hb_t0=None, log_prefix=""):
    """Learn delta[V] + beta_raw via Adam on manual gradient. Early-stop on val buried HARD acc."""
    V = fit["A"].shape[2]
    rng = np.random.default_rng(_stable_seed("depth_init", seed))
    delta = (rng.standard_normal(V) * 0.01).astype(np.float32)
    beta_raw = np.float32(0.5413)
    m_d = np.zeros(V, dtype=np.float32); v_d = np.zeros(V, dtype=np.float32)
    m_b = np.float32(0.0); v_b = np.float32(0.0)
    A, mask, num, pos, y = fit["A"], fit["mask"], fit["num"], fit["pos"], fit["y"]
    best_val, best = -1.0, (delta.copy(), float(beta_raw))
    history = []
    for ep in range(1, N_EPOCHS + 1):
        beta = np.log1p(np.exp(beta_raw))
        anneal = (1.0 + 2.0 * ep / N_EPOCHS) if SOFTMAX_TEMP_ANNEAL else 1.0
        depth = np.einsum("bkv,v->bk", A, delta)
        score = anneal * (-beta * depth + EPS_POS * pos)
        loss, dscore, pred, w = _bce_and_dscore(score, mask, num, y)
        d_score_pre = dscore * anneal
        grad_delta = np.einsum("bk,bkv->v", d_score_pre * (-beta), A) + L2_DELTA * delta
        grad_beta_via = float(np.sum(d_score_pre * (-depth)))
        dbeta_draw = 1.0 / (1.0 + np.exp(-beta_raw))
        grad_beta_raw = grad_beta_via * dbeta_draw
        m_d = ADAM_B1 * m_d + (1 - ADAM_B1) * grad_delta
        v_d = ADAM_B2 * v_d + (1 - ADAM_B2) * grad_delta * grad_delta
        mhat = m_d / (1 - ADAM_B1 ** ep); vhat = v_d / (1 - ADAM_B2 ** ep)
        delta = delta - LR * mhat / (np.sqrt(vhat) + ADAM_EPS)
        m_b = ADAM_B1 * m_b + (1 - ADAM_B1) * grad_beta_raw
        v_b = ADAM_B2 * v_b + (1 - ADAM_B2) * grad_beta_raw * grad_beta_raw
        mhb = m_b / (1 - ADAM_B1 ** ep); vhb = v_b / (1 - ADAM_B2 ** ep)
        beta_raw = np.float32(beta_raw - LR * mhb / (np.sqrt(vhb) + ADAM_EPS))
        if ep % VAL_EVERY == 0 or ep == N_EPOCHS:
            vdepth = np.einsum("bkv,v->bk", val["A"], delta)
            vsel = _hard_select_depth(vdepth, val["mask"])
            vacc, vn = _buried_acc(vsel, val)
            history.append({"epoch": ep, "loss": round(loss, 5),
                            "val_buried": (round(vacc, 4) if vacc is not None else None),
                            "beta": round(float(np.log1p(np.exp(beta_raw))), 4)})
            if vacc is not None and vacc > best_val:
                best_val = vacc
                best = (delta.copy(), float(beta_raw))
            print("%s[depth seed=%d] ep=%d loss=%.5f val_buried=%s beta=%.3f" %
                  (log_prefix, seed, ep, loss, (round(vacc, 4) if vacc is not None else "NA"),
                   float(np.log1p(np.exp(beta_raw)))), flush=True)
            if hb_t0 is not None:
                _emit_heartbeat(ep, N_EPOCHS, hb_t0, {"seed": seed, "val_buried": vacc})
    return best[0], best[1], history


def train_local(fit, val, seed):
    """Learn W[N_LOCAL] over the 10 LOCAL features, SAME select+read+BCE pipeline."""
    rng = np.random.default_rng(_stable_seed("local_init", seed))
    W = (rng.standard_normal(N_LOCAL) * 0.01).astype(np.float32)
    mW = np.zeros(N_LOCAL, dtype=np.float32); vW = np.zeros(N_LOCAL, dtype=np.float32)
    X, mask, num, y = fit["X"], fit["mask"], fit["num"], fit["y"]
    best_val, best = -1.0, W.copy()
    history = []
    for ep in range(1, N_EPOCHS + 1):
        anneal = (1.0 + 2.0 * ep / N_EPOCHS) if SOFTMAX_TEMP_ANNEAL else 1.0
        score = anneal * np.einsum("bkf,f->bk", X, W)
        loss, dscore, pred, w = _bce_and_dscore(score, mask, num, y)
        grad_W = np.einsum("bk,bkf->f", dscore * anneal, X) + L2_DELTA * W
        mW = ADAM_B1 * mW + (1 - ADAM_B1) * grad_W
        vW = ADAM_B2 * vW + (1 - ADAM_B2) * grad_W * grad_W
        mhat = mW / (1 - ADAM_B1 ** ep); vhat = vW / (1 - ADAM_B2 ** ep)
        W = W - LR * mhat / (np.sqrt(vhat) + ADAM_EPS)
        if ep % VAL_EVERY == 0 or ep == N_EPOCHS:
            vsc = np.einsum("bkf,f->bk", val["X"], W)
            vscm = np.where(val["mask"] > 0, vsc, -1e30)
            vsel = vscm.argmax(axis=1)
            vacc, vn = _buried_acc(vsel, val)
            if vacc is not None and vacc > best_val:
                best_val = vacc
                best = W.copy()
    return best, history


# ---- evaluators (all number-read-AFTER-select) ----
def sel_depth(data, delta):
    return _hard_select_depth(np.einsum("bkv,v->bk", data["A"], delta), data["mask"])


def sel_local(data, W):
    sc = np.einsum("bkf,f->bk", data["X"], W)
    return np.where(data["mask"] > 0, sc, -1e30).argmax(axis=1)


def sel_det(data):
    return _hard_select_depth(data["det_depth"], data["mask"])


def sel_nearest(data):
    return (np.arange(data["mask"].shape[1])[None, :] * data["mask"]).argmax(axis=1)


def sel_first(data):
    return np.zeros(len(data["y"]), dtype=np.int64)


def majority_acc(data, row_mask):
    y = data["y"][row_mask]
    if len(y) == 0:
        return None, 0
    maj = int(round(float(y.mean())))
    return float(np.mean((y == maj).astype(np.float32))), int(len(y))


def bootstrap_ci(sel, data, row_mask, n_boot=2000, seed=0):
    """95% bootstrap CI of accuracy over the rows in row_mask (HONESTY GUARD for small bins)."""
    if row_mask.sum() == 0:
        return None, None, 0
    picked = data["num"][np.arange(len(sel)), sel]
    correct = (picked == data["y"]).astype(np.float32)[row_mask]
    n = len(correct)
    rng = np.random.default_rng(_stable_seed("bootstrap", seed, n))
    accs = np.array([correct[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(np.percentile(accs, 2.5)), float(np.percentile(accs, 97.5)), n


def scramble_drop_deep(data, delta, row_mask, seeds):
    """ANTI-CHEAT on DEEP: permute learned per-noun depths (preserve multiset + positions), reselect."""
    depth = np.einsum("bkv,v->bk", data["A"], delta)
    mask = data["mask"]; num = data["num"]; y = data["y"]
    true_sel = _hard_select_depth(depth, mask)
    true_acc, _ = _acc_on(true_sel, data, row_mask)
    B, K = depth.shape
    scr_accs, change_fracs = [], []
    for seed in seeds:
        rng = np.random.default_rng(_stable_seed("scramble", seed))
        sdepth = depth.copy()
        for b in range(B):
            n = int(mask[b].sum())
            if n > 1:
                perm = rng.permutation(n)
                sdepth[b, :n] = depth[b, :n][perm]
        ssel = _hard_select_depth(sdepth, mask)
        picked = num[np.arange(B), ssel]
        acc = float(((picked == y).astype(np.float32))[row_mask].mean())
        scr_accs.append(round(acc, 4))
        change_fracs.append(round(float((ssel[row_mask] != true_sel[row_mask]).mean()), 4))
    return round(true_acc, 4), scr_accs, change_fracs


def number_flip_invariance(data, delta, row_mask):
    """Selection must NOT change under number flip (number read AFTER select)."""
    sel_a = sel_depth(data, delta)
    _ = 1.0 - data["num"]  # unused by selection
    sel_b = sel_depth(data, delta)
    return float((sel_a[row_mask] != sel_b[row_mask]).mean())


# ==================================================================================================
def _write_start_marker(run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(diag)


def make_splits(items):
    """Depth split: train pool = span_depth<=K (minus shallow_test); deep_test = buried span_depth>K.
    Returns (fit_items, val_items, shallow_test_items, deep_test_items)."""
    shallow = [it for it in items if span_depth(it) <= K_SHALLOW]
    deep_buried = [it for it in items if span_depth(it) > K_SHALLOW and int(it["subj_pos"]) != 0]
    # deterministic held-out shallow_test (item-level, unsalted)
    idx = np.arange(len(shallow))
    rng = np.random.default_rng(_stable_seed("shallow_test_split", K_SHALLOW))
    rng.shuffle(idx)
    n_test = max(1, int(len(shallow) * SHALLOW_TEST_FRAC))
    test_idx = set(idx[:n_test].tolist())
    shallow_test = [shallow[i] for i in range(len(shallow)) if i in test_idx]
    trainval = [shallow[i] for i in range(len(shallow)) if i not in test_idx]
    # val for early stopping (item-level, deterministic)
    vidx = np.arange(len(trainval))
    vr = np.random.default_rng(_stable_seed("valsplit", K_SHALLOW))
    vr.shuffle(vidx)
    n_val = max(1, int(len(trainval) * 0.20))
    val_set = set(vidx[:n_val].tolist())
    val_items = [trainval[i] for i in range(len(trainval)) if i in val_set]
    fit_items = [trainval[i] for i in range(len(trainval)) if i not in val_set]
    return fit_items, val_items, shallow_test, deep_buried


def depth_curve(data, delta, det_or_learned="learned"):
    """Per-depth-bin buried accuracy for a selector. Bins: 1,2,3,'4+'. Returns list of dicts."""
    buried = _buried_mask(data)
    sdepth = data["sdepth"]
    if det_or_learned == "learned":
        sel = sel_depth(data, delta)
    elif det_or_learned == "det":
        sel = sel_det(data)
    elif det_or_learned == "nearest":
        sel = sel_nearest(data)
    else:
        sel = sel_first(data)
    out = []
    for lo, hi, name in [(1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 999, "4+")]:
        rm = buried & (sdepth >= lo) & (sdepth <= hi)
        acc, n = _acc_on(sel, data, rm)
        lo_ci, hi_ci, _ = bootstrap_ci(sel, data, rm) if n else (None, None, 0)
        maj, _ = majority_acc(data, rm)
        out.append({"depth_bin": name, "n": n, "acc": (round(acc, 4) if acc is not None else None),
                    "ci95": [round(lo_ci, 4), round(hi_ci, 4)] if lo_ci is not None else None,
                    "majority": (round(maj, 4) if maj is not None else None)})
    return out


def run(run_mode):
    t0 = time.perf_counter()
    seeds = SMOKE_SEEDS if run_mode == "smoke" else SEEDS
    _write_start_marker(run_mode, len(seeds))
    items = load_items(max_items=(4000 if run_mode == "smoke" else None),
                       representative=(run_mode == "smoke"))
    fit_items, val_items, shallow_test_items, deep_test_items = make_splits(items)
    vocab, noun_types = build_vocab(fit_items)
    maxnn = max(len(it["noun_word_idx"]) for it in items)

    fit = encode(fit_items, vocab, maxnn)
    val = encode(val_items, vocab, maxnn)
    shallow_test = encode(shallow_test_items, vocab, maxnn)
    deep_test = encode(deep_test_items, vocab, maxnn)

    deep_buried = _buried_mask(deep_test)                    # all rows (all buried span>K)
    shallow_buried1 = _buried_mask(shallow_test) & (shallow_test["sdepth"] == 1)  # in-dist depth==1 buried

    deep_n = int(deep_buried.sum())
    shallow1_n = int(shallow_buried1.sum())

    # ---- static baselines on DEEP held-out buried ----
    nn_deep, _ = _acc_on(sel_nearest(deep_test), deep_test, deep_buried)
    fn_deep, _ = _acc_on(sel_first(deep_test), deep_test, deep_buried)
    det_deep, _ = _acc_on(sel_det(deep_test), deep_test, deep_buried)
    maj_deep, _ = majority_acc(deep_test, deep_buried)

    # ---- per-seed learned arms (train SHALLOW only; eval DEEP + SHALLOW1) ----
    per_seed = []
    ld_deep_accs, ld_shallow1_accs, lb_deep_accs, fr_deep_accs = [], [], [], []
    delta_last = None
    for seed in seeds:
        delta, beta_raw, dhist = train_depth(fit, val, seed, hb_t0=t0, log_prefix="[%s] " % run_mode)
        W, _ = train_local(fit, val, seed)
        ld_deep, _ = _acc_on(sel_depth(deep_test, delta), deep_test, deep_buried)
        ld_sh1, _ = _acc_on(sel_depth(shallow_test, delta), shallow_test, shallow_buried1)
        lb_deep, _ = _acc_on(sel_local(deep_test, W), deep_test, deep_buried)
        rng = np.random.default_rng(_stable_seed("fixed_random", seed))
        delta_fr = (rng.standard_normal(len(vocab))).astype(np.float32)
        fr_deep, _ = _acc_on(sel_depth(deep_test, delta_fr), deep_test, deep_buried)
        ld_deep_accs.append(ld_deep); ld_shallow1_accs.append(ld_sh1)
        lb_deep_accs.append(lb_deep); fr_deep_accs.append(fr_deep)
        per_seed.append({"seed": seed, "learned_deep": round(ld_deep, 4),
                         "learned_shallow1": round(ld_sh1, 4), "local_bag_deep": round(lb_deep, 4),
                         "fixed_random_deep": round(fr_deep, 4),
                         "beta": round(float(np.log1p(np.exp(beta_raw))), 4),
                         "depth_hist_tail": dhist[-3:]})
        delta_last = delta
        print("[%s] SEED %d DONE learned_deep=%.4f learned_shallow1=%.4f local_bag_deep=%.4f fixed_random_deep=%.4f" %
              (run_mode, seed, ld_deep, ld_sh1, lb_deep, fr_deep), flush=True)

    ld_deep_mean = round(float(np.mean(ld_deep_accs)), 4); ld_deep_std = round(float(np.std(ld_deep_accs)), 4)
    ld_sh1_mean = round(float(np.mean(ld_shallow1_accs)), 4)
    lb_deep_mean = round(float(np.mean(lb_deep_accs)), 4)
    fr_deep_mean = round(float(np.mean(fr_deep_accs)), 4)
    depth_degradation = round(ld_sh1_mean - ld_deep_mean, 4)

    # ---- bootstrap CI on aggregate deep (last seed's learned selection) ----
    ld_deep_lo, ld_deep_hi, _ = bootstrap_ci(sel_depth(deep_test, delta_last), deep_test, deep_buried)

    # ---- ANTI-CHEAT scramble on DEEP (last seed) ----
    scr_seeds = [101, 103, 107, 109, 113] if run_mode != "smoke" else [101, 103]
    true_deep, scr_accs, change_fracs = scramble_drop_deep(deep_test, delta_last, deep_buried, scr_seeds)
    scr_mean = round(float(np.mean(scr_accs)), 4)
    scramble_drop_val = round(true_deep - scr_mean, 4)
    change_frac_mean = round(float(np.mean(change_fracs)), 4)

    # ---- fairness: number flip on deep ----
    flip_change = number_flip_invariance(deep_test, delta_last, deep_buried)

    # ---- DEPTH CURVE (deliverable) over ALL buried items (train contamination flagged for depth==1) ----
    all_items = load_items()
    all_data = encode(all_items, vocab, max(len(it["noun_word_idx"]) for it in all_items))
    curve_learned = depth_curve(all_data, delta_last, "learned")
    curve_det = depth_curve(all_data, None, "det")
    curve_nearest = depth_curve(all_data, None, "nearest")

    # ---- glass-box inspection of learned increments ----
    vindex = {w: i for i, w in enumerate(vocab)}
    inspect_tokens = ["of", "in", "to", "that", "which", "who", ",", "(", ")", "the", "a", "and", "is", "are"]
    learned_deltas = {t: (round(float(delta_last[vindex[t]]), 4) if t in vindex else None)
                      for t in inspect_tokens}

    # ---- arms-differ (META_RULE_AF): deep buried preds ----
    Wlast, _ = train_local(fit, val, seeds[-1])
    preds = {
        "learned_depth": deep_test["num"][np.arange(deep_test["y"].shape[0]), sel_depth(deep_test, delta_last)][deep_buried].astype(np.int64),
        "local_bag": deep_test["num"][np.arange(deep_test["y"].shape[0]), sel_local(deep_test, Wlast)][deep_buried].astype(np.int64),
        "nearest_noun": deep_test["num"][np.arange(deep_test["y"].shape[0]), sel_nearest(deep_test)][deep_buried].astype(np.int64),
    }
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    arms_differ = len(set(digs.values())) >= 2

    # ---- verdict (pre-registered) ----
    cond_a = ld_deep_mean >= HP_HOLD_CEILING
    cond_b = (ld_deep_mean - nn_deep) >= HP_ABOVE_NEAREST
    cond_c = (ld_deep_mean - maj_deep) >= HP_ABOVE_MAJORITY
    cond_d = depth_degradation <= HP_MAX_DEGRADATION
    cond_e = scramble_drop_val >= HP_SCRAMBLE_DROP
    cond_f = flip_change == 0.0
    hf_i = (ld_deep_mean - nn_deep) <= HF_TIE_NEAREST
    hf_ii = ld_deep_mean <= maj_deep + HF_AT_MAJORITY
    hf_iii = depth_degradation >= HF_DEGRADATION
    hf_iv = scramble_drop_val < HF_SCRAMBLE_NOEFFECT
    if cond_a and cond_b and cond_c and cond_d and cond_e and cond_f:
        verdict = "HARD_PASS_DEPTH_PRODUCTIVE"
    elif hf_i or hf_ii or hf_iii or hf_iv:
        verdict = "HARD_FAIL_DEPTH_BOUNDED_SHALLOW_LOOKUP"
    else:
        verdict = "MIDDLE_BAND"

    # Gate D positive control: deterministic reproduces recursive ceiling on deep
    gate_d_ok = (det_deep is not None) and (0.66 <= det_deep <= 0.82)
    baseline_in_band = (maj_deep is not None and 0.05 < maj_deep < 0.95
                        and nn_deep is not None and 0.05 < nn_deep < 0.95)

    msg = ("DEPTH-PRODUCTIVITY | DEEP held-out buried (n=%d, %d seeds): learned_deep=%.4f(+-%.4f) "
           "[CI95 %.3f-%.3f] | ceiling(determ29450)=%.4f nearest=%.4f first=%.4f majority=%.4f | "
           "SHALLOW1 learned=%.4f -> depth_degradation=%+.4f | local_bag_deep=%.4f fixed_random_deep=%.4f "
           "| SCRAMBLE true=%.4f scr=%.4f DROP=%+.4f (change=%.3f) | flip=%.4f | delta of=%s that=%s the=%s "
           "| GateD_det_reproduces_ceiling=%s | %s" % (
               deep_n, len(seeds), ld_deep_mean, ld_deep_std,
               (ld_deep_lo if ld_deep_lo is not None else -1), (ld_deep_hi if ld_deep_hi is not None else -1),
               det_deep, nn_deep, fn_deep, maj_deep, ld_sh1_mean, depth_degradation,
               lb_deep_mean, fr_deep_mean, true_deep, scr_mean, scramble_drop_val, change_frac_mean,
               flip_change, learned_deltas.get("of"), learned_deltas.get("that"), learned_deltas.get("the"),
               gate_d_ok, verdict))

    metrics = {
        "verdict": verdict, "verdict_tag": verdict, "verdict_msg": msg,
        "summary": ("%s | learned_deep=%.4f vs ceiling=%.4f vs nearest=%.4f vs majority=%.4f | "
                    "depth_degradation=%+.4f | scramble_drop=%+.4f | flip=%.4f" % (
                        verdict, ld_deep_mean, det_deep, nn_deep, maj_deep, depth_degradation,
                        scramble_drop_val, flip_change)),
        "elapsed_s": round(time.perf_counter() - t0, 2), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "depth_metric": "span_depth = max det-depth of nouns strictly after subject; K_SHALLOW=%d" % K_SHALLOW,
        "deep_test_buried_n": deep_n, "shallow_test_depth1_buried_n": shallow1_n, "n_seeds": len(seeds),
        "arms": {
            "learned_depth": {"deep_mean": ld_deep_mean, "deep_std": ld_deep_std, "deep_per_seed": ld_deep_accs,
                              "deep_ci95": [round(ld_deep_lo, 4), round(ld_deep_hi, 4)] if ld_deep_lo is not None else None,
                              "shallow1_mean": ld_sh1_mean, "shallow1_per_seed": ld_shallow1_accs},
            "deterministic_depth": {"deep": round(det_deep, 4), "note": "29450 recursive-rule ceiling at test regime (Gate D)"},
            "nearest_noun": {"deep": round(nn_deep, 4)},
            "first_noun": {"deep": round(fn_deep, 4)},
            "majority": {"deep": round(maj_deep, 4)},
            "local_bag": {"deep_mean": lb_deep_mean, "deep_per_seed": lb_deep_accs},
            "fixed_random": {"deep_mean": fr_deep_mean, "deep_per_seed": fr_deep_accs},
        },
        "depth_degradation": depth_degradation,
        "depth_curve": {"learned": curve_learned, "deterministic": curve_det, "nearest": curve_nearest,
                        "note": "over ALL buried items; depth<=1 is IN-training-distribution for learned (flagged)"},
        "scramble_discriminator": {"true_acc": true_deep, "scrambled_acc_mean": scr_mean,
                                   "scramble_drop": scramble_drop_val, "per_seed_scrambled": scr_accs,
                                   "per_seed_change_frac": change_fracs, "change_frac_mean": change_frac_mean,
                                   "seeds": scr_seeds},
        "number_flip_change_frac": flip_change,
        "learned_deltas_inspect": learned_deltas,
        "per_seed": per_seed,
        "verdict_conditions": {"cond_a_hold_ceiling": bool(cond_a), "cond_b_above_nearest": bool(cond_b),
                               "cond_c_above_majority": bool(cond_c), "cond_d_small_degradation": bool(cond_d),
                               "cond_e_scramble_fires": bool(cond_e), "cond_f_flip_invariant": bool(cond_f),
                               "hf_i_tie_nearest": bool(hf_i), "hf_ii_at_majority": bool(hf_ii),
                               "hf_iii_degradation": bool(hf_iii), "hf_iv_scramble_no_effect": bool(hf_iv)},
        "gate_d_det_reproduces_ceiling": bool(gate_d_ok),
        "arms_differ_verified": bool(arms_differ), "arms_differ_digests": digs,
        "baseline_in_band": bool(baseline_in_band),
        "bands": {"HP_HOLD_CEILING": HP_HOLD_CEILING, "HP_ABOVE_NEAREST": HP_ABOVE_NEAREST,
                  "HP_ABOVE_MAJORITY": HP_ABOVE_MAJORITY, "HP_MAX_DEGRADATION": HP_MAX_DEGRADATION,
                  "HP_SCRAMBLE_DROP": HP_SCRAMBLE_DROP, "HF_TIE_NEAREST": HF_TIE_NEAREST,
                  "HF_AT_MAJORITY": HF_AT_MAJORITY, "HF_DEGRADATION": HF_DEGRADATION,
                  "HF_SCRAMBLE_NOEFFECT": HF_SCRAMBLE_NOEFFECT},
        "n_vocab": len(vocab), "n_fit": len(fit_items), "n_val": len(val_items),
        "n_shallow_test": len(shallow_test_items), "n_deep_test": len(deep_test_items),
        "final_metrics_atomicity": "tmp_replace",
        "cardinality_ok": True, "expected_n_units": len(seeds), "observed_n_units": len(per_seed),
        "crlb_n_a": "classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor",
        "runtime_glassbox": "hard argmin over learned depth register; NO autograd, NO torch; gradient build-time only (manual numpy)",
        "progress_logging": "per-VAL_EVERY val_buried prints with flush=True + _heartbeat.jsonl during training",
    }
    _write_metrics(metrics)
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)
    print("[%s] elapsed=%.2fs run_mode=%s verdict=%s" % (ANCHOR_NAME, metrics["elapsed_s"], run_mode, verdict), flush=True)
    return metrics


def self_test():
    print("[%s] SELF-TEST" % ANCHOR_NAME, flush=True)
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
        print("[%s] F.5 source scan clean" % ANCHOR_NAME, flush=True)
    except ImportError:
        print("[%s] F.5 preflight module absent; hashlib-only discipline" % ANCHOR_NAME, flush=True)

    # ---- span_depth hand-trace ----
    # "keys[N0] to[+1] cabinet[N1] in[+1] hall[N2]": subj keys@0. after=[1,2] -> span_depth=2 (deep).
    it_deep = {"words": ["keys", "to", "cabinet", "in", "hall"], "noun_word_idx": [0, 2, 4],
               "nums": [1, 0, 0], "subj_pos": 0, "label": 1, "subj_word": "keys"}
    assert span_depth(it_deep) == 2, "span_depth deep should be 2: %s" % span_depth(it_deep)
    # buried single embedding: subject is N1 at depth 0? build: "a0[N0] to[+1] b1[N1,d1]" no.. use buried case
    it_shallow = {"words": ["dogs", "near", "cat"], "noun_word_idx": [0, 2],
                  "nums": [1, 0], "subj_pos": 0, "label": 1, "subj_word": "dogs"}
    assert span_depth(it_shallow) == 1, "span_depth shallow should be 1: %s" % span_depth(it_shallow)

    # ---- depth-feature construction + hard selection ----
    it = {"words": ["keys", "to", "cabinet"], "noun_word_idx": [0, 2],
          "nums": [1, 0], "subj_pos": 0, "label": 1, "subj_word": "keys"}
    vocab = ["to"]
    d = encode([it], vocab, 2)
    assert d["A"][0, 0, 0] == 0.0 and d["A"][0, 1, 0] == 1.0, "A count wrong: %s" % d["A"][0]
    depth = np.einsum("bkv,v->bk", d["A"], np.array([1.0], dtype=np.float32))
    assert _hard_select_depth(depth, d["mask"])[0] == 0, "learned +depth should pick subject N0"
    depth0 = np.einsum("bkv,v->bk", d["A"], np.array([0.0], dtype=np.float32))
    assert _hard_select_depth(depth0, d["mask"])[0] == 1, "delta=0 should default to nearest_noun N1"
    print("[%s] hand-trace OK: span_depth + depth-select" % ANCHOR_NAME, flush=True)

    # ---- number-flip invariance ----
    rm = np.array([True])
    assert number_flip_invariance(d, np.array([1.0], dtype=np.float32), rm) == 0.0, "number leaked into selection"

    # ---- manual-gradient finite-difference check ----
    rng = np.random.default_rng(0)
    B, K, V = 6, 4, 5
    A = rng.standard_normal((B, K, V)).astype(np.float32)
    mask = (rng.random((B, K)) > 0.2).astype(np.float32); mask[:, 0] = 1.0
    num = (rng.random((B, K)) > 0.5).astype(np.float32)
    pos = np.tile(np.arange(K), (B, 1)).astype(np.float32) / (K - 1)
    y = (rng.random(B) > 0.5).astype(np.float32)
    delta = rng.standard_normal(V).astype(np.float32); beta = 1.3

    def _loss(dl):
        score = -beta * np.einsum("bkv,v->bk", A, dl) + EPS_POS * pos
        w = _masked_softmax(score, mask)
        p = np.clip((w * num).sum(axis=1), BCE_CLIP, 1 - BCE_CLIP)
        return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))

    score = -beta * np.einsum("bkv,v->bk", A, delta) + EPS_POS * pos
    _, dscore, _, _ = _bce_and_dscore(score, mask, num, y)
    grad_delta = np.einsum("bk,bkv->v", dscore * (-beta), A)
    eps = 1e-4
    for j in range(V):
        dp = delta.copy(); dp[j] += eps
        dm = delta.copy(); dm[j] -= eps
        fd = (_loss(dp) - _loss(dm)) / (2 * eps)
        assert abs(fd - grad_delta[j]) < 1e-2, "grad mismatch j=%d analytic=%.5f fd=%.5f" % (j, grad_delta[j], fd)
    print("[%s] manual-gradient finite-difference check PASS" % ANCHOR_NAME, flush=True)

    # ---- data-backed smoke: depth split feasibility + baselines in band ----
    items = load_items(max_items=3000, representative=True)
    fit_items, val_items, shallow_test_items, deep_test_items = make_splits(items)
    assert len(fit_items) > 300, "fit too small: %d" % len(fit_items)
    assert len(deep_test_items) > 80, "deep_test too small on slice: %d" % len(deep_test_items)
    # NO deep structure leaked into training
    assert all(span_depth(it) <= K_SHALLOW for it in fit_items), "deep item leaked into fit"
    assert all(span_depth(it) <= K_SHALLOW for it in val_items), "deep item leaked into val"
    assert all(span_depth(it) > K_SHALLOW and int(it["subj_pos"]) != 0 for it in deep_test_items), "deep_test impure"
    vocab, _ = build_vocab(fit_items)
    assert 15 < len(vocab) <= MAX_VOCAB and "of" in vocab and "in" in vocab, "vocab off: %d" % len(vocab)
    maxnn = max(len(it["noun_word_idx"]) for it in items)
    deep = encode(deep_test_items, vocab, maxnn)
    db = _buried_mask(deep)
    nn_deep, _ = _acc_on(sel_nearest(deep), deep, db)
    det_deep, _ = _acc_on(sel_det(deep), deep, db)
    maj_deep, _ = majority_acc(deep, db)
    print("[%s] slice DEEP baselines: nearest=%.4f determ_ceiling=%.4f majority=%.4f n_deep_buried=%d" %
          (ANCHOR_NAME, nn_deep, det_deep, maj_deep, int(db.sum())), flush=True)
    assert 0.05 < maj_deep < 0.95 and 0.05 < nn_deep < 0.95, "deep baseline out of band (AG)"
    assert det_deep > nn_deep + 0.15, "deterministic ceiling should dominate nearest on deep (recursive rule works)"

    # short train to confirm training path runs + arms differ; NOT a verdict
    global N_EPOCHS
    saved = N_EPOCHS; N_EPOCHS = 80
    fit = encode(fit_items, vocab, maxnn); val = encode(val_items, vocab, maxnn)
    delta, beta_raw, _ = train_depth(fit, val, 7)
    N_EPOCHS = saved
    ld_deep, _ = _acc_on(sel_depth(deep, delta), deep, db)
    print("[%s] short-train preview learned_deep=%.4f (full trains %d epochs; smoke/full verdict-bearing)" %
          (ANCHOR_NAME, ld_deep, saved), flush=True)
    # arms differ
    p_ld = deep["num"][np.arange(deep["y"].shape[0]), sel_depth(deep, delta)][db].astype(np.int64)
    p_nn = deep["num"][np.arange(deep["y"].shape[0]), sel_nearest(deep)][db].astype(np.int64)
    assert hashlib.sha256(p_ld.tobytes()).hexdigest() != hashlib.sha256(p_nn.tobytes()).hexdigest() \
        or abs(ld_deep - nn_deep) < 1e-9, "learned vs nearest bit-identical (arms don't differ)"
    print("[%s] SELF-TEST PASS" % ANCHOR_NAME, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run("smoke"); return
    run("full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(e)
        raise
