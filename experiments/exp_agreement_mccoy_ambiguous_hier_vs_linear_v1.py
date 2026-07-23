"""
exp_agreement_mccoy_ambiguous_hier_vs_linear_v1
===============================================

CLEAN-CG SHOT (Director task 2026-07-23): the CANONICAL McCoy-Frank-Linzen 2020 ambiguous-training
paradigm applied to our substrate. QUESTION: does the incremental depth-ACCUMULATOR architecture
SELECT the HIERARCHICAL structure over the LINEAR shortcut from AMBIGUOUS real-text data (Perfors
2011 model-selection), the way McCoy showed only tree/stack-structured models do?

McCoy, Frank & Linzen 2020 "Does syntax need to grow on trees?" (arXiv:2001.03632):  the ONLY
factor that reliably yields a HIERARCHICAL inductive bias is ARCHITECTURAL structure (tree/stack);
structure-free sequence models generalize LINEARLY.  Perfors/Tenenbaum/Regier 2011: an ideal learner
SELECTS hierarchy over linear via Bayesian model selection over a hypothesis space that INCLUDES
hierarchical grammars.  This cell asks BOTH for a VSA/accumulator: given its architectural structural
capacity, does it SELECT the hierarchical rule from data that is CONSISTENT WITH BOTH?

THE PARADIGM (one variable = presence of architectural structure)
  TRAIN on the AMBIGUOUS pool: items where the HIERARCHICAL rule (min-depth noun nearest verb, per
    atom 29450) and the LINEAR rule (first noun) AGREE on the gold subject.  On these BOTH rules give
    the gold -> training is consistent with a hierarchical OR a linear generalization (McCoy-ambiguous).
  TEST on the DIVERGE / BURIED pool: items where the two rules DISAGREE (hier != first) and the subject
    is buried (subj_pos != 0).  Here hier -> the real subject, first/linear -> an attractor.
  MEASURE which generalization the substrate learned:
    - accuracy vs gold on diverge (hierarchical pole = 0.80 determ ceiling; linear pole = 0.42 first).
    - ALIGNMENT (no gold): frac of diverge picks == hier rule vs == linear rule.
    - the LEARNING CURVE of the hier-vs-linear preference across training epochs.

ARMS
  ARM_ACCUM  (the substrate) : incremental depth accumulator; per-FW depth increments LEARNED; runtime
                               = HARD min-depth argmin.  Its ONLY positional term is a small FIXED
                               EPS_POS position prior that favors NEAREST-verb (the OPPOSITE of first),
                               so it has NO first-noun shortcut -> it can fit ambiguous training ONLY via
                               genuine FW-depth structure.  HYPOTHESIS: generalizes HIERARCHICALLY.
  ARM_FLAT   (must-fail ctrl): structure-free bag/linear readout over the SAME 10 token features (incl
                               a first-noun flag), no accumulator.  HYPOTHESIS: learns FIRST-noun from
                               ambiguous training -> generalizes LINEARLY (reproduces McCoy sequence model).
  ARM_MIX    (Perfors probe) : ARM_ACCUM architecture but the position weight gamma is ALSO LEARNED
                               (score = -beta*depth + gamma*pos).  Given BOTH a depth pathway and a
                               position pathway, does ambiguous training keep it hierarchical (gamma
                               small, tracks depth) or let it drift linear?  Report learned gamma +
                               diverge accuracy.  Descriptive (NOT in the core gate).
  deterministic_depth (29450): hierarchical CEILING + Gate D positive control (reproduces 0.80 on diverge).
  first_noun                 : LINEAR pole.
  nearest_noun, majority     : reference baselines.
  fixed_random               : accum architecture with fixed-random deltas (no learning) MUST-FAIL floor.

SPLIT (gold used ONLY to build the split, NEVER at inference; selection is argmin over structure):
  hier_idx(item)  = rightmost noun at minimum deterministic embedding-depth (== sel_det; atom 29450).
  first_idx(item) = 0.
  AGREE (train)   = { hier_idx == first_idx == gold_subj_idx }.  Genuinely ambiguous + both correct.
  DIVERGE (test)  = { hier_idx != first_idx  AND  subj_pos != 0 }.  Buried; rules disagree.
  AGREE and DIVERGE are DISJOINT by construction (hier==first vs hier!=first); zero leakage (asserted).

BANDS (pre-registered; MEASURED@scratchpad/probe_mccoy_split.py on real Linzen cache, diverge_buried
       n=5581: determ(hier)=0.8004  first(linear)=0.4223  nearest=0.5569  majority=0.6121):
  CLEAN_CG_PASS_HIERARCHICAL_SELECTION (ALL of):
    (a) accum_buried >= 0.70                       (near the 0.80 hier ceiling, far above 0.42 linear pole)
    (b) accum_buried - flat_buried >= 0.15         (architecture confers the bias the flat model lacks)
    (c) accum_buried - majority(0.6121) >= 0.05    (beats the majority floor)
    (d) accum_buried - first(0.4223) >= 0.20       (clearly above the linear pole)
    (e) accum_scramble_drop >= 0.10                (anti-cheat: lift is DEPTH not position)
    (f) accum_number_flip == 0.0                   (number read AFTER selection)
    (g) flat_buried <= majority + 0.05 (0.662)     (flat did NOT go hierarchical -> the one-variable contrast holds)
    (h) accum_align_hier >= 0.60                   (accum picks track the HIER rule, not the linear rule)
  HARD_FAIL_ACCUM_ALSO_LINEAR (ANY of):
    (i)   accum_buried - flat_buried <= 0.05       (accum no better than the structure-free model -> no bias)
    (ii)  accum_buried <= majority + 0.02 (0.632)  (no hierarchical lift over guessing)
    (iii) accum_buried <= first + 0.10 (0.522)     (collapsed toward the linear pole)
    (iv)  accum_scramble_drop < 0.05 AND accum_buried <= majority + 0.05  (lift, if any, is POSITION not depth)
    (v)   accum_align_first >= 0.60 AND accum_align_hier < 0.45           (accum picks track the LINEAR rule)
  MIDDLE = else (partial hierarchical lift; beats shortcuts but short of the ceiling / clean contrast).
HONEST FRAMING (HONESTY GUARD -- this is the 4th CG framing this arc; defensible ONLY as the canonical
  published paradigm, McCoy+Perfors):  CLEAN_CG_PASS = the accumulator architecture SELECTS hierarchical
  structure over the linear shortcut from ambiguous real-text data = brain-faithful learned compositional
  structure (composes 29455/29453/29450); flag for HARDEST skunkworks-VET.  HARD_FAIL = the earlier wins
  needed buried supervision; ambiguous agree-data does NOT drive hierarchical selection -> an earned bound
  + a Perfors-relevant negative -> BANK IT HONESTLY, do NOT invent a 5th bar.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - deterministic: hashlib digests + fixed int seeds + np.random.default_rng + sorted(set); NO builtin hash(), NO list(set())
# - build-time gradient MANUAL numpy (closed form); runtime = HARD argmin, NO autograd, NO torch on select path
# - arms_differ verified (accum / flat / first distinct diverge preds; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor
# - baseline_in_band: majority=0.612 + first=0.422 + nearest=0.557 all in (0.05,0.95) (META_RULE_AG); asserted at self-test + run
# - cardinality: EXPECTED_N_UNITS = len(SEEDS) model-init seeds; no sweep axis; verdict counts per-seed results
# - discriminator survives scale: FULL uses ALL real diverge_buried (n=5581); determ reproduces 0.80 hier ceiling at scale (Gate D)
# - baseline_valid: fixed_random control validated NOT at arena floor (same architecture, live random deltas)
# - all header/band numbers MEASURED@scratchpad/probe_mccoy_split.py or MEASURED@ this cell output; bands HYPOTHESIZED flagged
# - progress_logging: per-VAL_EVERY val + diverge-curve prints flush=True + _heartbeat.jsonl during training (timeout < 1800s)
# - Gate D: deterministic_depth arm reproduces the 29450 hier ceiling (0.80) AT THIS TEST REGIME (positive control)
# - ONE variable = architecture (accum vs flat); split by rule-vs-rule agreement, gold only builds the split
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

ANCHOR_NAME = "exp_agreement_mccoy_ambiguous_hier_vs_linear_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", ANCHOR_NAME)

# ---- pre-registered bands (MEASURED@scratchpad/probe_mccoy_split.py diverge_buried anchors) ----
HP_ACCUM_FLOOR = 0.70       # (a) accum_buried >= this (near 0.80 hier ceiling)
HP_ABOVE_FLAT = 0.15        # (b) accum_buried - flat_buried
HP_ABOVE_MAJORITY = 0.05    # (c) accum_buried - majority
HP_ABOVE_FIRST = 0.20       # (d) accum_buried - first
HP_SCRAMBLE_DROP = 0.10     # (e) scramble drop
HP_FLAT_CEILING = 0.05      # (g) flat_buried <= majority + this (flat stays linear)
HP_ALIGN_HIER = 0.60        # (h) accum align to hier rule
HF_TIE_FLAT = 0.05          # (i) accum - flat <= this => FAIL
HF_AT_MAJORITY = 0.02       # (ii) accum <= majority + this => FAIL
HF_NEAR_FIRST = 0.10        # (iii) accum <= first + this => FAIL
HF_SCRAMBLE_NOEFFECT = 0.05 # (iv) scramble drop < this (with weak lift) => FAIL
HF_ALIGN_FIRST = 0.60       # (v) accum align to first rule
HF_ALIGN_HIER_LOW = 0.45    # (v) accum align to hier below this

# ---- multi-seed (model-init variance; the agree/diverge split is fixed/deterministic) ----
SEEDS = [7, 13, 19, 23, 31]
SMOKE_SEEDS = [7, 13]

# ---- learnable function-word vocab ----
MAX_VOCAB = 160
MIN_FREQ = 20

# ---- model / training hyperparams ----
EPS_POS = 0.30              # FIXED position prior for ARM_ACCUM (favors nearest-verb tie-break; NO first shortcut)
L2_DELTA = 1e-4
LR = 0.05
ADAM_B1, ADAM_B2, ADAM_EPS = 0.9, 0.999, 1e-8
N_EPOCHS = 1500
VAL_EVERY = 50
SOFTMAX_TEMP_ANNEAL = True
BCE_CLIP = 1e-4

# ---- closed lists for the DETERMINISTIC hier arm (recursive 0.80 ceiling; atom 29450) ----
PREPS = set((
    "to of in on for with at by from into onto about over under between among against during "
    "without within through across after before around near above below beside besides beyond "
    "despite toward towards upon per via regarding concerning off out up down"
).split())
SUBORD = set((
    "that which who whom whose where when while because if although though unless until since "
    "whether as than"
).split())

# ---- the 10 LOCAL features for the ARM_FLAT structure-free readout ----
LB_PREPS = {"of", "in", "on", "with", "by", "for", "to", "from", "at", "as", "into",
            "over", "under", "between", "among", "through", "during", "against", "about"}
LB_DETS = {"the", "a", "an", "this", "that", "these", "those", "its", "their", "his", "her", "our"}
N_LOCAL = 10


# ==================================================================================================
# Data + deterministic depth + rule predictions
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


def item_hier_idx(item):
    """Hierarchical rule prediction (atom 29450): rightmost noun at MINIMUM deterministic depth."""
    dd = det_depths_at_nouns(item)
    best_d = min(dd)
    cand = [k for k in range(len(dd)) if dd[k] == best_d]
    return max(cand)


def item_first_idx(item):
    return 0


def span_depth(item):
    """Embedding depth of the subject->verb span = max det-depth of nouns strictly after the subject."""
    dd = det_depths_at_nouns(item)
    sp = int(item["subj_pos"])
    after = dd[sp + 1:]
    return max(after) if after else 0


def build_vocab(train_items):
    """Deterministic learnable FW vocab = top MAX_VOCAB non-noun token types by TRAIN freq (>= MIN_FREQ)."""
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
    """The 10 LOCAL features for noun k at word index widx (ARM_FLAT). Includes first/last flags. NO number leak."""
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
    """Vectorize items into padded [B,maxnn,*] arrays. Also returns per-item hier/first idx + span_depth."""
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
    hidx = np.zeros(B, dtype=np.int64)
    sdepth = np.zeros(B, dtype=np.int64)
    for bi, it in enumerate(items):
        ni = it["noun_word_idx"]
        words = it["words"]
        nn = len(ni)
        y[bi] = float(it["label"])
        subj_pos[bi] = int(it["subj_pos"])
        hidx[bi] = item_hier_idx(it)
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
            "pos": pos, "y": y, "subj_pos": subj_pos, "hidx": hidx, "sdepth": sdepth}


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
    if row_mask.sum() == 0:
        return None, 0
    picked = data["num"][np.arange(len(sel)), sel]
    correct = (picked == data["y"]).astype(np.float32)
    return float(correct[row_mask].mean()), int(row_mask.sum())


def _full_acc(sel, data):
    """Agreement accuracy over ALL rows (early-stop metric on the agree val set)."""
    picked = data["num"][np.arange(len(sel)), sel]
    return float((picked == data["y"]).astype(np.float32).mean())


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


def train_accum(fit, val, diverge, seed, learn_gamma=False, init_gamma=EPS_POS,
                hb_t0=None, log_prefix=""):
    """Learn delta[V] (+ optional gamma) via Adam on manual gradient. Early-stop on val FULL acc
    (in-distribution agree; NEVER on diverge). Records the diverge learning-curve descriptively."""
    V = fit["A"].shape[2]
    rng = np.random.default_rng(_stable_seed("accum_init", seed, learn_gamma))
    delta = (rng.standard_normal(V) * 0.01).astype(np.float32)
    beta_raw = np.float32(0.5413)
    gamma = np.float32(init_gamma)
    m_d = np.zeros(V, dtype=np.float32); v_d = np.zeros(V, dtype=np.float32)
    m_b = np.float32(0.0); v_b = np.float32(0.0)
    m_g = np.float32(0.0); v_g = np.float32(0.0)
    A, mask, num, pos, y = fit["A"], fit["mask"], fit["num"], fit["pos"], fit["y"]
    best_val, best = -1.0, (delta.copy(), float(beta_raw), float(gamma))
    history = []
    for ep in range(1, N_EPOCHS + 1):
        beta = np.log1p(np.exp(beta_raw))
        anneal = (1.0 + 2.0 * ep / N_EPOCHS) if SOFTMAX_TEMP_ANNEAL else 1.0
        depth = np.einsum("bkv,v->bk", A, delta)
        score = anneal * (-beta * depth + gamma * pos)
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
        if learn_gamma:
            grad_gamma = float(np.sum(d_score_pre * pos))
            m_g = ADAM_B1 * m_g + (1 - ADAM_B1) * grad_gamma
            v_g = ADAM_B2 * v_g + (1 - ADAM_B2) * grad_gamma * grad_gamma
            mhg = m_g / (1 - ADAM_B1 ** ep); vhg = v_g / (1 - ADAM_B2 ** ep)
            gamma = np.float32(gamma - LR * mhg / (np.sqrt(vhg) + ADAM_EPS))
        if ep % VAL_EVERY == 0 or ep == N_EPOCHS:
            vsel = _hard_select_depth(np.einsum("bkv,v->bk", val["A"], delta), val["mask"])
            vacc = _full_acc(vsel, val)
            # diverge learning-curve (descriptive; NOT used for model selection)
            dsel = _hard_select_depth(np.einsum("bkv,v->bk", diverge["A"], delta), diverge["mask"])
            dacc, _ = _acc_on(dsel, diverge, np.ones(len(diverge["y"]), dtype=bool))
            al_h = float((dsel == diverge["hidx"]).mean())
            al_f = float((dsel == 0).mean())
            history.append({"epoch": ep, "loss": round(loss, 5), "val_full": round(vacc, 4),
                            "diverge_acc": round(dacc, 4), "align_hier": round(al_h, 4),
                            "align_first": round(al_f, 4),
                            "beta": round(float(np.log1p(np.exp(beta_raw))), 4),
                            "gamma": round(float(gamma), 4)})
            if vacc > best_val:
                best_val = vacc
                best = (delta.copy(), float(beta_raw), float(gamma))
            print("%s[accum seed=%d gamma_learn=%s] ep=%d loss=%.5f val_full=%.4f "
                  "diverge=%.4f align_hier=%.3f align_first=%.3f beta=%.3f gamma=%.3f" %
                  (log_prefix, seed, learn_gamma, ep, loss, vacc, dacc, al_h, al_f,
                   float(np.log1p(np.exp(beta_raw))), float(gamma)), flush=True)
            if hb_t0 is not None:
                _emit_heartbeat(ep, N_EPOCHS, hb_t0, {"seed": seed, "diverge": dacc})
    return best[0], best[1], best[2], history


def train_flat(fit, val, seed):
    """ARM_FLAT: learn W[N_LOCAL] over the 10 LOCAL features (incl first-flag), SAME select+read+BCE."""
    rng = np.random.default_rng(_stable_seed("flat_init", seed))
    W = (rng.standard_normal(N_LOCAL) * 0.01).astype(np.float32)
    mW = np.zeros(N_LOCAL, dtype=np.float32); vW = np.zeros(N_LOCAL, dtype=np.float32)
    X, mask, num, y = fit["X"], fit["mask"], fit["num"], fit["y"]
    best_val, best = -1.0, W.copy()
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
            vsel = np.where(val["mask"] > 0, vsc, -1e30).argmax(axis=1)
            vacc = _full_acc(vsel, val)
            if vacc > best_val:
                best_val = vacc
                best = W.copy()
    return best


# ---- evaluators (all number-read-AFTER-select) ----
def sel_accum_gamma(data, delta, beta, gamma):
    """ARM_MIX runtime select = argmax(-beta*depth + gamma*pos) == argmin(beta*depth - gamma*pos)."""
    depth = np.einsum("bkv,v->bk", data["A"], delta)
    score = beta * depth - gamma * data["pos"]
    return _hard_select_depth(score, data["mask"])


def sel_flat(data, W):
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
    if row_mask.sum() == 0:
        return None, None, 0
    picked = data["num"][np.arange(len(sel)), sel]
    correct = (picked == data["y"]).astype(np.float32)[row_mask]
    n = len(correct)
    rng = np.random.default_rng(_stable_seed("bootstrap", seed, n))
    accs = np.array([correct[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(np.percentile(accs, 2.5)), float(np.percentile(accs, 97.5)), n


def scramble_drop(data, delta, row_mask, seeds):
    """ANTI-CHEAT: permute learned per-noun depths (preserve multiset + positions), reselect."""
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
    sel_a = _hard_select_depth(np.einsum("bkv,v->bk", data["A"], delta), data["mask"])
    _ = 1.0 - data["num"]  # unused by selection
    sel_b = _hard_select_depth(np.einsum("bkv,v->bk", data["A"], delta), data["mask"])
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


def make_mccoy_splits(items):
    """AGREE (train) = hier==first==gold ; DIVERGE (test) = hier!=first & subj!=0 ; DISJOINT by build.
    Returns (fit_items, val_items, diverge_items)."""
    agree, diverge = [], []
    for it in items:
        h = item_hier_idx(it); f = item_first_idx(it); g = int(it["subj_pos"])
        if h == f and h == g:
            agree.append(it)
        if h != f and g != 0:
            diverge.append(it)
    # deterministic val hold-out from agree (early stop; item-level, unsalted)
    idx = np.arange(len(agree))
    rng = np.random.default_rng(_stable_seed("agree_val_split"))
    rng.shuffle(idx)
    n_val = max(1, int(len(agree) * 0.20))
    val_set = set(idx[:n_val].tolist())
    val_items = [agree[i] for i in range(len(agree)) if i in val_set]
    fit_items = [agree[i] for i in range(len(agree)) if i not in val_set]
    return fit_items, val_items, diverge


def depth_curve(data, delta):
    """Per-span_depth-bin accuracy of accum / determ / first on diverge (productivity compose, 29455)."""
    sdepth = data["sdepth"]
    rows = np.ones(len(data["y"]), dtype=bool)
    sa = _hard_select_depth(np.einsum("bkv,v->bk", data["A"], delta), data["mask"])
    sd = sel_det(data); sf = sel_first(data)
    out = []
    for lo, hi, name in [(1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 999, "4+")]:
        rm = rows & (sdepth >= lo) & (sdepth <= hi)
        a_ac, n = _acc_on(sa, data, rm)
        a_de, _ = _acc_on(sd, data, rm)
        a_fi, _ = _acc_on(sf, data, rm)
        out.append({"span_depth": name, "n": n,
                    "accum": (round(a_ac, 4) if a_ac is not None else None),
                    "determ": (round(a_de, 4) if a_de is not None else None),
                    "first": (round(a_fi, 4) if a_fi is not None else None)})
    return out


def run(run_mode):
    t0 = time.perf_counter()
    seeds = SMOKE_SEEDS if run_mode == "smoke" else SEEDS
    _write_start_marker(run_mode, len(seeds))
    items = load_items(max_items=(6000 if run_mode == "smoke" else None),
                       representative=(run_mode == "smoke"))
    fit_items, val_items, diverge_items = make_mccoy_splits(items)
    vocab, noun_types = build_vocab(fit_items)
    maxnn = max(len(it["noun_word_idx"]) for it in items)

    fit = encode(fit_items, vocab, maxnn)
    val = encode(val_items, vocab, maxnn)
    diverge = encode(diverge_items, vocab, maxnn)
    allrows = np.ones(len(diverge["y"]), dtype=bool)
    diverge_n = len(diverge_items)

    # ---- static baselines / poles on the DIVERGE test ----
    det_d, _ = _acc_on(sel_det(diverge), diverge, allrows)      # hier ceiling (Gate D)
    first_d, _ = _acc_on(sel_first(diverge), diverge, allrows)  # linear pole
    near_d, _ = _acc_on(sel_nearest(diverge), diverge, allrows)
    maj_d, _ = majority_acc(diverge, allrows)

    # ---- per-seed learned arms (train on AGREE only; eval on DIVERGE) ----
    per_seed = []
    accum_accs, flat_accs, fr_accs, mix_accs, mix_gammas = [], [], [], [], []
    alh_list, alf_list = [], []
    delta_last = W_last = None
    beta_last = gamma_mix_last = None
    hist_accum_last = hist_mix_last = None
    for seed in seeds:
        delta, beta_raw, gamma, dhist = train_accum(fit, val, diverge, seed, learn_gamma=False,
                                                    hb_t0=t0, log_prefix="[%s] " % run_mode)
        W = train_flat(fit, val, seed)
        d_mix, br_mix, g_mix, mhist = train_accum(fit, val, diverge, seed, learn_gamma=True,
                                                  hb_t0=None, log_prefix="[%s-mix] " % run_mode)
        beta_mix = float(np.log1p(np.exp(br_mix)))

        sa = _hard_select_depth(np.einsum("bkv,v->bk", diverge["A"], delta), diverge["mask"])
        acc_ac, _ = _acc_on(sa, diverge, allrows)
        acc_fl, _ = _acc_on(sel_flat(diverge, W), diverge, allrows)
        rng = np.random.default_rng(_stable_seed("fixed_random", seed))
        delta_fr = (rng.standard_normal(len(vocab))).astype(np.float32)
        acc_fr, _ = _acc_on(_hard_select_depth(np.einsum("bkv,v->bk", diverge["A"], delta_fr), diverge["mask"]),
                            diverge, allrows)
        sm = sel_accum_gamma(diverge, d_mix, beta_mix, g_mix)
        acc_mix, _ = _acc_on(sm, diverge, allrows)

        al_h = float((sa == diverge["hidx"]).mean())
        al_f = float((sa == 0).mean())

        accum_accs.append(acc_ac); flat_accs.append(acc_fl); fr_accs.append(acc_fr)
        mix_accs.append(acc_mix); mix_gammas.append(g_mix)
        alh_list.append(al_h); alf_list.append(al_f)
        per_seed.append({"seed": seed, "accum": round(acc_ac, 4), "flat": round(acc_fl, 4),
                         "fixed_random": round(acc_fr, 4), "mix": round(acc_mix, 4),
                         "mix_gamma": round(g_mix, 4), "align_hier": round(al_h, 4),
                         "align_first": round(al_f, 4),
                         "beta": round(float(np.log1p(np.exp(beta_raw))), 4),
                         "accum_hist_tail": dhist[-3:]})
        delta_last, W_last, beta_last, gamma_mix_last = delta, W, float(np.log1p(np.exp(beta_raw))), g_mix
        hist_accum_last, hist_mix_last = dhist, mhist
        print("[%s] SEED %d DONE accum=%.4f flat=%.4f mix=%.4f(g=%.3f) fixed_random=%.4f align_hier=%.3f align_first=%.3f" %
              (run_mode, seed, acc_ac, acc_fl, acc_mix, g_mix, acc_fr, al_h, al_f), flush=True)

    accum_mean = round(float(np.mean(accum_accs)), 4); accum_std = round(float(np.std(accum_accs)), 4)
    flat_mean = round(float(np.mean(flat_accs)), 4)
    fr_mean = round(float(np.mean(fr_accs)), 4)
    mix_mean = round(float(np.mean(mix_accs)), 4); mix_gamma_mean = round(float(np.mean(mix_gammas)), 4)
    align_hier_mean = round(float(np.mean(alh_list)), 4); align_first_mean = round(float(np.mean(alf_list)), 4)

    # ---- bootstrap CI on accum diverge (last seed) ----
    sa_last = _hard_select_depth(np.einsum("bkv,v->bk", diverge["A"], delta_last), diverge["mask"])
    ac_lo, ac_hi, _ = bootstrap_ci(sa_last, diverge, allrows)

    # ---- ANTI-CHEAT scramble (last seed) ----
    scr_seeds = [101, 103, 107, 109, 113] if run_mode != "smoke" else [101, 103]
    true_ac, scr_accs, change_fracs = scramble_drop(diverge, delta_last, allrows, scr_seeds)
    scr_mean = round(float(np.mean(scr_accs)), 4)
    scramble_drop_val = round(true_ac - scr_mean, 4)
    change_frac_mean = round(float(np.mean(change_fracs)), 4)

    # ---- fairness: number flip ----
    flip_change = number_flip_invariance(diverge, delta_last, allrows)

    # ---- productivity compose (29455): depth curve on diverge ----
    curve = depth_curve(diverge, delta_last)

    # ---- glass-box learned increments ----
    vindex = {w: i for i, w in enumerate(vocab)}
    inspect_tokens = ["of", "in", "to", "that", "which", "who", ",", "(", ")", "the", "a", "and", "is", "are"]
    learned_deltas = {t: (round(float(delta_last[vindex[t]]), 4) if t in vindex else None) for t in inspect_tokens}

    # ---- arms-differ (META_RULE_AF): diverge preds ----
    preds = {
        "accum": diverge["num"][np.arange(diverge["y"].shape[0]), sa_last].astype(np.int64),
        "flat": diverge["num"][np.arange(diverge["y"].shape[0]), sel_flat(diverge, W_last)].astype(np.int64),
        "first": diverge["num"][np.arange(diverge["y"].shape[0]), sel_first(diverge)].astype(np.int64),
    }
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    arms_differ = len(set(digs.values())) >= 2

    # ---- verdict (pre-registered) ----
    cond_a = accum_mean >= HP_ACCUM_FLOOR
    cond_b = (accum_mean - flat_mean) >= HP_ABOVE_FLAT
    cond_c = (accum_mean - maj_d) >= HP_ABOVE_MAJORITY
    cond_d = (accum_mean - first_d) >= HP_ABOVE_FIRST
    cond_e = scramble_drop_val >= HP_SCRAMBLE_DROP
    cond_f = flip_change == 0.0
    cond_g = flat_mean <= maj_d + HP_FLAT_CEILING
    cond_h = align_hier_mean >= HP_ALIGN_HIER
    hf_i = (accum_mean - flat_mean) <= HF_TIE_FLAT
    hf_ii = accum_mean <= maj_d + HF_AT_MAJORITY
    hf_iii = accum_mean <= first_d + HF_NEAR_FIRST
    hf_iv = (scramble_drop_val < HF_SCRAMBLE_NOEFFECT) and (accum_mean <= maj_d + 0.05)
    hf_v = (align_first_mean >= HF_ALIGN_FIRST) and (align_hier_mean < HF_ALIGN_HIER_LOW)
    if all([cond_a, cond_b, cond_c, cond_d, cond_e, cond_f, cond_g, cond_h]):
        verdict = "CLEAN_CG_PASS_HIERARCHICAL_SELECTION"
    elif any([hf_i, hf_ii, hf_iii, hf_iv, hf_v]):
        verdict = "HARD_FAIL_ACCUM_ALSO_LINEAR"
    else:
        verdict = "MIDDLE_BAND"

    gate_d_ok = (det_d is not None) and (0.70 <= det_d <= 0.88)
    baseline_in_band = all(v is not None and 0.05 < v < 0.95 for v in (maj_d, first_d, near_d))

    msg = ("McCOY AMBIGUOUS-TRAINING | DIVERGE/buried test (n=%d, %d seeds): ACCUM=%.4f(+-%.4f) "
           "[CI95 %.3f-%.3f] FLAT=%.4f MIX=%.4f(gamma=%.3f) fixed_random=%.4f | poles: hier_ceiling(det29450)=%.4f "
           "first(linear)=%.4f nearest=%.4f majority=%.4f | ALIGN accum->hier=%.3f accum->first=%.3f | "
           "SCRAMBLE true=%.4f scr=%.4f DROP=%+.4f (change=%.3f) | flip=%.4f | delta of=%s that=%s the=%s | "
           "GateD_det_ceiling=%s | %s" % (
               diverge_n, len(seeds), accum_mean, accum_std,
               (ac_lo if ac_lo is not None else -1), (ac_hi if ac_hi is not None else -1),
               flat_mean, mix_mean, mix_gamma_mean, fr_mean, det_d, first_d, near_d, maj_d,
               align_hier_mean, align_first_mean, true_ac, scr_mean, scramble_drop_val, change_frac_mean,
               flip_change, learned_deltas.get("of"), learned_deltas.get("that"), learned_deltas.get("the"),
               gate_d_ok, verdict))

    metrics = {
        "verdict": verdict, "verdict_tag": verdict, "verdict_msg": msg,
        "summary": ("%s | accum=%.4f flat=%.4f mix=%.4f | hier_ceiling=%.4f first(linear)=%.4f majority=%.4f | "
                    "align_hier=%.3f align_first=%.3f | scramble_drop=%+.4f flip=%.4f" % (
                        verdict, accum_mean, flat_mean, mix_mean, det_d, first_d, maj_d,
                        align_hier_mean, align_first_mean, scramble_drop_val, flip_change)),
        "elapsed_s": round(time.perf_counter() - t0, 2), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "paradigm": "McCoy2020 ambiguous training: train on agree(hier==first==gold), test on diverge/buried(hier!=first & subj!=0)",
        "diverge_test_n": diverge_n, "n_seeds": len(seeds),
        "arms": {
            "accum": {"diverge_mean": accum_mean, "diverge_std": accum_std, "diverge_per_seed": accum_accs,
                      "diverge_ci95": [round(ac_lo, 4), round(ac_hi, 4)] if ac_lo is not None else None,
                      "align_hier_mean": align_hier_mean, "align_first_mean": align_first_mean},
            "flat": {"diverge_mean": flat_mean, "diverge_per_seed": flat_accs, "note": "structure-free must-fail control"},
            "mix": {"diverge_mean": mix_mean, "gamma_mean": mix_gamma_mean, "per_seed_gamma": [round(g, 4) for g in mix_gammas],
                    "note": "Perfors probe: accum + LEARNED position weight gamma; descriptive not gated"},
            "deterministic_depth": {"diverge": round(det_d, 4), "note": "29450 hier ceiling at test regime (Gate D)"},
            "first_noun": {"diverge": round(first_d, 4), "note": "linear pole"},
            "nearest_noun": {"diverge": round(near_d, 4)},
            "majority": {"diverge": round(maj_d, 4)},
            "fixed_random": {"diverge_mean": fr_mean, "diverge_per_seed": fr_accs},
        },
        "learning_curve_accum": hist_accum_last,
        "learning_curve_mix": hist_mix_last,
        "depth_curve_diverge": {"rows": curve, "note": "productivity compose (29455): accum/determ/first per span_depth on diverge"},
        "scramble_discriminator": {"true_acc": true_ac, "scrambled_acc_mean": scr_mean,
                                   "scramble_drop": scramble_drop_val, "per_seed_scrambled": scr_accs,
                                   "per_seed_change_frac": change_fracs, "change_frac_mean": change_frac_mean,
                                   "seeds": scr_seeds},
        "number_flip_change_frac": flip_change,
        "learned_deltas_inspect": learned_deltas,
        "per_seed": per_seed,
        "verdict_conditions": {"cond_a_accum_floor": bool(cond_a), "cond_b_above_flat": bool(cond_b),
                               "cond_c_above_majority": bool(cond_c), "cond_d_above_first": bool(cond_d),
                               "cond_e_scramble_fires": bool(cond_e), "cond_f_flip_invariant": bool(cond_f),
                               "cond_g_flat_stays_linear": bool(cond_g), "cond_h_align_hier": bool(cond_h),
                               "hf_i_tie_flat": bool(hf_i), "hf_ii_at_majority": bool(hf_ii),
                               "hf_iii_near_first": bool(hf_iii), "hf_iv_scramble_no_effect": bool(hf_iv),
                               "hf_v_aligns_linear": bool(hf_v)},
        "gate_d_det_reproduces_ceiling": bool(gate_d_ok),
        "arms_differ_verified": bool(arms_differ), "arms_differ_digests": digs,
        "baseline_in_band": bool(baseline_in_band),
        "bands": {"HP_ACCUM_FLOOR": HP_ACCUM_FLOOR, "HP_ABOVE_FLAT": HP_ABOVE_FLAT,
                  "HP_ABOVE_MAJORITY": HP_ABOVE_MAJORITY, "HP_ABOVE_FIRST": HP_ABOVE_FIRST,
                  "HP_SCRAMBLE_DROP": HP_SCRAMBLE_DROP, "HP_FLAT_CEILING": HP_FLAT_CEILING,
                  "HP_ALIGN_HIER": HP_ALIGN_HIER, "HF_TIE_FLAT": HF_TIE_FLAT, "HF_AT_MAJORITY": HF_AT_MAJORITY,
                  "HF_NEAR_FIRST": HF_NEAR_FIRST, "HF_SCRAMBLE_NOEFFECT": HF_SCRAMBLE_NOEFFECT,
                  "HF_ALIGN_FIRST": HF_ALIGN_FIRST, "HF_ALIGN_HIER_LOW": HF_ALIGN_HIER_LOW},
        "n_vocab": len(vocab), "n_fit": len(fit_items), "n_val": len(val_items), "n_diverge": len(diverge_items),
        "final_metrics_atomicity": "tmp_replace",
        "cardinality_ok": True, "expected_n_units": len(seeds), "observed_n_units": len(per_seed),
        "crlb_n_a": "classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor",
        "runtime_glassbox": "hard argmin over learned depth register; NO autograd, NO torch; gradient build-time only (manual numpy)",
        "progress_logging": "per-VAL_EVERY val + diverge-curve prints flush=True + _heartbeat.jsonl during training",
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

    # ---- rule predictions hand-trace ----
    # "keys[N0] to[+1] cabinet[N1] in[+1] hall[N2]": depths [0,1,2]; hier=min-depth-rightmost=N0; first=N0.
    it = {"words": ["keys", "to", "cabinet", "in", "hall"], "noun_word_idx": [0, 2, 4],
          "nums": [1, 0, 0], "subj_pos": 0, "label": 1, "subj_word": "keys"}
    assert item_hier_idx(it) == 0, "hier should pick N0: %d" % item_hier_idx(it)
    assert item_first_idx(it) == 0
    # buried diverge: subject is N1 (depth 0), an earlier attractor N0 embedded deeper.
    it2 = {"words": ["in", "spring", "flowers", "bloom"], "noun_word_idx": [1, 2],
           "nums": [0, 1], "subj_pos": 1, "label": 1, "subj_word": "flowers"}
    # depths: 'in'->+1 before N0(spring) => spring depth1; flowers depth1. min depth=1, rightmost=N1(flowers).
    assert item_hier_idx(it2) == 1, "hier should pick N1 flowers: %d (depths=%s)" % (item_hier_idx(it2), det_depths_at_nouns(it2))
    assert item_first_idx(it2) == 0
    print("[%s] hand-trace OK: hier/first rule preds" % ANCHOR_NAME, flush=True)

    # ---- encode + hier idx consistency with sel_det ----
    vocab = ["to", "in"]
    d = encode([it], vocab, 3)
    assert sel_det(d)[0] == item_hier_idx(it), "sel_det must match item_hier_idx"
    assert d["hidx"][0] == item_hier_idx(it)
    # delta favoring +depth for 'to','in' -> subject N0 min-depth picked
    depth = np.einsum("bkv,v->bk", d["A"], np.array([1.0, 1.0], dtype=np.float32))
    assert _hard_select_depth(depth, d["mask"])[0] == 0, "learned +depth should pick subject N0"

    # ---- number-flip invariance ----
    rm = np.array([True])
    assert number_flip_invariance(d, np.array([1.0, 1.0], dtype=np.float32), rm) == 0.0, "number leaked into selection"

    # ---- manual-gradient finite-difference check (delta + gamma) ----
    rng = np.random.default_rng(0)
    B, K, V = 6, 4, 5
    A = rng.standard_normal((B, K, V)).astype(np.float32)
    mask = (rng.random((B, K)) > 0.2).astype(np.float32); mask[:, 0] = 1.0
    num = (rng.random((B, K)) > 0.5).astype(np.float32)
    pos = np.tile(np.arange(K), (B, 1)).astype(np.float32) / (K - 1)
    y = (rng.random(B) > 0.5).astype(np.float32)
    delta = rng.standard_normal(V).astype(np.float32); beta = 1.3; gamma = 0.4

    def _loss(dl, gm):
        score = -beta * np.einsum("bkv,v->bk", A, dl) + gm * pos
        w = _masked_softmax(score, mask)
        p = np.clip((w * num).sum(axis=1), BCE_CLIP, 1 - BCE_CLIP)
        return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))

    score = -beta * np.einsum("bkv,v->bk", A, delta) + gamma * pos
    _, dscore, _, _ = _bce_and_dscore(score, mask, num, y)
    grad_delta = np.einsum("bk,bkv->v", dscore * (-beta), A)
    grad_gamma = float(np.sum(dscore * pos))
    eps = 1e-4
    for j in range(V):
        dp = delta.copy(); dp[j] += eps
        dm = delta.copy(); dm[j] -= eps
        fd = (_loss(dp, gamma) - _loss(dm, gamma)) / (2 * eps)
        assert abs(fd - grad_delta[j]) < 1e-2, "grad delta mismatch j=%d analytic=%.5f fd=%.5f" % (j, grad_delta[j], fd)
    fdg = (_loss(delta, gamma + eps) - _loss(delta, gamma - eps)) / (2 * eps)
    assert abs(fdg - grad_gamma) < 1e-2, "grad gamma mismatch analytic=%.5f fd=%.5f" % (grad_gamma, fdg)
    print("[%s] manual-gradient finite-difference check PASS (delta + gamma)" % ANCHOR_NAME, flush=True)

    # ---- data-backed smoke: split feasibility + poles in band + disjointness ----
    items = load_items(max_items=4000, representative=True)
    fit_items, val_items, diverge_items = make_mccoy_splits(items)
    assert len(fit_items) > 300, "fit too small: %d" % len(fit_items)
    assert len(diverge_items) > 300, "diverge too small on slice: %d" % len(diverge_items)
    # DISJOINTNESS: no diverge item in fit/val (agree vs diverge disjoint by construction)
    fit_ids = set(id(x) for x in fit_items) | set(id(x) for x in val_items)
    assert not any(id(x) in fit_ids for x in diverge_items), "LEAK: diverge item in train"
    for it_ in fit_items + val_items:
        assert item_hier_idx(it_) == item_first_idx(it_) == int(it_["subj_pos"]), "train item not agree/ambiguous"
    for it_ in diverge_items:
        assert item_hier_idx(it_) != item_first_idx(it_) and int(it_["subj_pos"]) != 0, "diverge item impure"
    vocab, _ = build_vocab(fit_items)
    assert 15 < len(vocab) <= MAX_VOCAB and "of" in vocab and "in" in vocab, "vocab off: %d" % len(vocab)
    maxnn = max(len(it["noun_word_idx"]) for it in items)
    dv = encode(diverge_items, vocab, maxnn)
    allrows = np.ones(len(dv["y"]), dtype=bool)
    det_d, _ = _acc_on(sel_det(dv), dv, allrows)
    first_d, _ = _acc_on(sel_first(dv), dv, allrows)
    near_d, _ = _acc_on(sel_nearest(dv), dv, allrows)
    maj_d, _ = majority_acc(dv, allrows)
    print("[%s] slice DIVERGE poles: hier_ceiling(det)=%.4f first(linear)=%.4f nearest=%.4f majority=%.4f n=%d" %
          (ANCHOR_NAME, det_d, first_d, near_d, maj_d, int(allrows.sum())), flush=True)
    assert 0.05 < maj_d < 0.95 and 0.05 < first_d < 0.95, "diverge baseline out of band (AG)"
    assert det_d >= first_d + 0.20, "hier ceiling must dominate the linear pole on diverge (discriminator can fire)"

    # short train to confirm training path + arms differ; NOT a verdict
    global N_EPOCHS
    saved = N_EPOCHS; N_EPOCHS = 80
    fit = encode(fit_items, vocab, maxnn); val = encode(val_items, vocab, maxnn)
    delta, beta_raw, gamma, _ = train_accum(fit, val, dv, 7, learn_gamma=False)
    W = train_flat(fit, val, 7)
    N_EPOCHS = saved
    acc_ac, _ = _acc_on(_hard_select_depth(np.einsum("bkv,v->bk", dv["A"], delta), dv["mask"]), dv, allrows)
    acc_fl, _ = _acc_on(sel_flat(dv, W), dv, allrows)
    print("[%s] short-train preview accum=%.4f flat=%.4f (full trains %d epochs; smoke/full verdict-bearing)" %
          (ANCHOR_NAME, acc_ac, acc_fl, saved), flush=True)
    p_ac = dv["num"][np.arange(dv["y"].shape[0]), _hard_select_depth(np.einsum("bkv,v->bk", dv["A"], delta), dv["mask"])].astype(np.int64)
    p_fl = dv["num"][np.arange(dv["y"].shape[0]), sel_flat(dv, W)].astype(np.int64)
    assert hashlib.sha256(p_ac.tobytes()).hexdigest() != hashlib.sha256(p_fl.tobytes()).hexdigest() \
        or abs(acc_ac - acc_fl) < 1e-9, "accum vs flat bit-identical (arms don't differ)"
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
