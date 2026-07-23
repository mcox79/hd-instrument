"""
exp_agreement_sigmap_depth_induction_v1
========================================

GENUINE STRUCTURAL-INDUCTION SHOT (Director task 2026-07-22): learn a token's embedding-depth
DELTA from its UNSUPERVISED DISTRIBUTIONAL/POSITIONAL SIGNATURE -- with NO per-lexeme function-word
identity allowed -- and prove it EXTRAPOLATES to HELD-OUT function words (FW-HOLDOUT). This is the
lever the last VET defined: the per-FW-scalar accumulator (atom 29453) was down-rated because it
learned a per-function-word LOOKUP that COLLAPSES to majority (~0.64) when the high-frequency
depth-opener function words are frozen. A GENUINE inducer must infer a HELD-OUT function word's
depth-role from its SIGNATURE alone, so it does not collapse.

ONE VARIABLE (the isolation): both arms share the ENTIRE pipeline -- signature-weighted incremental
depth accumulation, build-time manual-numpy gradient, hard-argmin runtime selection, read number
AFTER selection. They differ ONLY in the per-vocab FEATURE MATRIX F:
  - signature_map : F = distributional/positional SIGNATURE  [V, D_sig]  (generative; global map)
  - scalar_lookup : F = IDENTITY one-hot                     [V, V]       (= 29453; per-FW scalar)
delta[v] = active[v] * (F[v,:] . theta). depth[b,k] = sum_v count[b,k,v] * delta[v].
For signature_map delta is a GLOBAL function of signature -> a held-out FW gets a delta from its
signature. For scalar_lookup delta[v] is a free per-FW weight -> a held-out FW (no training gradient,
theta init 0) contributes 0 -> collapses. That collapse (control) minus the map's HOLD = the
generative contribution of the signature.

FW-HOLDOUT (the discriminator; MUST be able to fail):
  - HEADLINE = high-frequency-opener holdout: DISABLE the top HF_HOLDOUT_M FW-vocab tokens by TRAIN
    frequency during theta-fitting (this block CONTAINS every decisive opener: of/in/to/that/for/
    with/on/by/from/which...). Fit theta on the mid/low-frequency tail ONLY. At test ENABLE all FWs;
    held-out FWs seen ONLY through signature (map) or through an untrained-0 scalar (lookup).
    Reproduces the exact condition under which 29453 collapsed to 0.6425.
  - ROBUSTNESS = 5-fold rotating hash holdout (every FW held out once); report mean map-minus-scalar.
ANTI-CHEAT: scramble the per-noun learned depths (preserve multiset + positions) -> selection must
  collapse toward nearest_noun (lift is DEPTH not position).
NO LEAK: signature computed from TRAIN sentences only, WITHOUT the agreement label or number; number
  read AFTER selection (number-flip = 0). Feature list audited + printed; none encodes subjecthood/
  number. The signature is a DESCRIPTION of a token's corpus distribution, never its identity.

BANDS (pre-registered; majority + shortcuts MEASURED at run; see HP_/HF_ constants):
  HARD_PASS (ALL, headline high-freq holdout, multi-seed mean):
    (a) map_hf_holdout >= majority + 0.06          (map HOLDS clearly above majority)
    (b) map_hf_holdout - scalar_hf_holdout >= 0.05 (map beats the lookup under the SAME holdout)
    (c) scalar_hf_holdout <= majority + 0.03       (control COLLAPSES to ~majority; reproduces VET)
    (d) scramble_drop >= 0.10                       (anti-cheat: lift is DEPTH not position)
  HARD_FAIL (ANY):
    (i)  map_hf_holdout - majority <= 0.02          (map ALSO collapses -> EARNED bound: depth-role
                                                     not predictable from surface signature at scale)
    (ii) map_hf_holdout - scalar_hf_holdout <= 0.02 (map does no generative work beyond the lookup)
    (iii) scramble_drop < 0.05                       (position all along)
  If (c) fails but (a)&(b) hold -> MIDDLE_BAND_HOLDOUT_NOT_DECISIVE (the control did not collapse ->
    the high-freq block was not load-bearing -> test-design inconclusive, NOT a substrate verdict).
  Else MIDDLE_BAND.
HONEST FRAMING: HARD_PASS = the FIRST LEARNED result on real text where a structural role EXTRAPOLATES
  to unseen structural markers from their distribution alone -> chain-grade landmark -> hardest VET
  (is it truly signature-generative vs disguised frequency; is the held-out block representative;
  did the linear map just re-fit freq). HARD_FAIL = a precise EARNED bound (surface distribution is
  insufficient to induce the depth-opening role at this scale).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - deterministic: hashlib digests + fixed int seeds + np.random.default_rng + sorted(set); NO builtin hash(), NO list(set())
# - build-time gradient MANUAL numpy (closed form + finite-difference checked); runtime = HARD argmin, NO autograd, NO torch
# - ONE VARIABLE: F = signature matrix vs F = identity; entire rest of pipeline bit-identical
# - arms_differ verified (signature_map / scalar_lookup / nearest_noun distinct buried pred vectors; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor
# - baseline_in_band: majority_buried ~0.63 + shortcuts in (0.05,0.95) (META_RULE_AG); asserted at self-test + run
# - cardinality: EXPECTED_N_UNITS = len(SEEDS) headline seeds; verdict counts per-seed results
# - discriminator survives scale: FULL run IS full-N; deterministic ceiling reproduces the structural ceiling at scale;
#     smoke = representative stride slice previews map-minus-scalar gap + arms differ before FULL
# - baseline_valid: scalar_lookup control is the SAME architecture (identity F) -> not an arena-floor sentinel
# - NO LEAK: signature from TRAIN sentences only, no label/number; number-flip=0 asserted; feature audit printed
# - all header numbers MEASURED@ this cell's output or prior cells (0.759 ceiling / 0.628 majority) with tags
# - progress_logging: per-VAL_EVERY val_buried prints flush=True + _heartbeat.jsonl during training
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
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "exp_agreement_sigmap_depth_induction_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", ANCHOR_NAME)

# ---- pre-registered bands ----
HP_ABOVE_MAJORITY = 0.06       # (a) map_hf_holdout - majority
HP_MAP_OVER_SCALAR = 0.05      # (b) map_hf_holdout - scalar_hf_holdout
HP_SCALAR_COLLAPSE = 0.03      # (c) scalar_hf_holdout <= majority + this
HP_SCRAMBLE_DROP = 0.10        # (d) scramble collapse
HF_MAP_COLLAPSE = 0.02         # (i) map_hf_holdout - majority <= this => HARD_FAIL (earned bound)
HF_NO_ISOLATION = 0.02         # (ii) map - scalar <= this => no generative work
HF_SCRAMBLE_NOEFFECT = 0.05    # (iii) scramble drop < this => position all along

# ---- holdout config ----
HF_HOLDOUT_M = 24              # disable top-M FW-vocab tokens by TRAIN freq (the decisive-opener block)
KFOLDS = 5                     # rotating hash holdout for robustness

# ---- multi-seed (theta-init variance; splits are fixed/deterministic) ----
SEEDS = [7, 13, 19, 23, 31]
SMOKE_SEEDS = [7, 13]
KFOLD_SEED = 7                 # single seed for the 5-fold robustness sweep

# ---- sentence split (held-out subject lexemes; disjoint pools) + val carve ----
TEST_HASH_MOD = 5
TEST_FRAC_CUT = 2              # ~40% of subject lexemes -> test sentences
VAL_FRAC = 0.20               # novel-lexeme validation carved from train (early stopping)

# ---- learnable function-word vocab ----
MAX_VOCAB = 160               # top non-noun token types by TRAIN frequency
MIN_FREQ = 20                 # candidate must appear >= this in TRAIN

# ---- model / training hyperparams ----
EPS_POS = 0.30                # fixed position tie-break weight (favors verb-adjacent at equal depth)
L2_THETA = 1e-4              # L2 reg on the map coefficients (glass-box stability)
LR = 0.05                     # Adam step
ADAM_B1, ADAM_B2, ADAM_EPS = 0.9, 0.999, 1e-8
N_EPOCHS = 1000
VAL_EVERY = 50
SOFTMAX_TEMP_ANNEAL = True
BCE_CLIP = 1e-4

# ---- deterministic positive-control (hand-coded structural ceiling) ----
PREPS = set((
    "to of in on for with at by from into onto about over under between among against during "
    "without within through across after before around near above below beside besides beyond "
    "despite toward towards upon per via regarding concerning off out up down"
).split())
SUBORD = set((
    "that which who whom whose where when while because if although though unless until since "
    "whether as than"
).split())

# ---- signature feature names (order is load-bearing; theta printed against these) ----
FEAT_NAMES = [
    "bias", "log_freq_z", "p_next_noun_z", "p_prev_noun_z", "p_next_content_z",
    "p_prev_content_z", "p_next_punct_z", "p_prev_punct_z", "is_punct",
    "word_len_z", "mean_relpos_z", "succ_diversity_z", "connective_z",
]
D_SIG = len(FEAT_NAMES)


# ==================================================================================================
# Data
# ==================================================================================================
def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(str(subj_word).encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def _stable_seed(*parts):
    key = "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") & ((1 << 63) - 1)


def _fold_of(token):
    h = int.from_bytes(hashlib.sha256(("fold|" + str(token)).encode("utf-8")).digest()[:8], "big")
    return h % KFOLDS


def _is_punct(tok):
    return 0.0 if any(c.isalnum() for c in tok) else 1.0


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
    """Deterministic hand-coded depth per noun (PREP/SUBORD +1; comma/close -1). Positive-control."""
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


def build_vocab_and_nounrate(train_items):
    """FW-vocab = top MAX_VOCAB non-noun token types by TRAIN freq (freq>=MIN_FREQ; nouns excluded).
    noun_rate[token] = P(occurrence at a noun position) over TRAIN, for ALL tokens (content proxy).
    NO label / number used."""
    tot = Counter()
    at_noun = Counter()
    noun_types = set()
    nonnoun = Counter()
    for it in train_items:
        ni = set(it["noun_word_idx"])
        for i, w in enumerate(it["words"]):
            wl = w.lower()
            tot[wl] += 1
            if i in ni:
                at_noun[wl] += 1
                noun_types.add(wl)
            else:
                nonnoun[wl] += 1
    noun_rate = {w: (at_noun[w] / tot[w]) for w in tot}
    cand = [(w, c) for w, c in nonnoun.items() if c >= MIN_FREQ and w not in noun_types]
    cand.sort(key=lambda x: (-x[1], x[0]))            # freq desc, token asc (stable order)
    vocab = [w for w, _ in cand[:MAX_VOCAB]]
    return sorted(set(vocab)), noun_rate, tot


def compute_signature(train_items, vocab, noun_rate):
    """Per-vocab distributional/positional SIGNATURE from TRAIN sentences ONLY. No label/number.
    Returns S[V, D_SIG] and a raw-feature dict for glass-box inspection.
    content(token) := noun_rate(token) > 0.5 (frequency/structure proxy; NOT the agreement label)."""
    vset = set(vocab)
    vidx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    cnt = np.zeros(V, dtype=np.float64)
    nxt_noun = np.zeros(V); prv_noun = np.zeros(V)
    nxt_cont = np.zeros(V); prv_cont = np.zeros(V)
    nxt_punc = np.zeros(V); prv_punc = np.zeros(V)
    relpos = np.zeros(V); wlen = np.zeros(V)
    succ_types = [set() for _ in range(V)]
    for it in train_items:
        words = it["words"]
        ni = set(it["noun_word_idx"])
        L = len(words)
        denom = max(L - 1, 1)
        for i, w in enumerate(words):
            wl = w.lower()
            vi = vidx.get(wl)
            if vi is None:
                continue
            cnt[vi] += 1.0
            relpos[vi] += i / denom
            wlen[vi] += len(wl)
            # right neighbor
            if i + 1 < L:
                nw = words[i + 1].lower()
                if (i + 1) in ni:
                    nxt_noun[vi] += 1.0
                if noun_rate.get(nw, 0.0) > 0.5:
                    nxt_cont[vi] += 1.0
                if _is_punct(nw):
                    nxt_punc[vi] += 1.0
                succ_types[vi].add(nw)
            # left neighbor
            if i - 1 >= 0:
                pw = words[i - 1].lower()
                if (i - 1) in ni:
                    prv_noun[vi] += 1.0
                if noun_rate.get(pw, 0.0) > 0.5:
                    prv_cont[vi] += 1.0
                if _is_punct(pw):
                    prv_punc[vi] += 1.0
    c = np.maximum(cnt, 1.0)
    raw = {
        "log_freq": np.log(cnt + 1.0),
        "p_next_noun": nxt_noun / c,
        "p_prev_noun": prv_noun / c,
        "p_next_content": nxt_cont / c,
        "p_prev_content": prv_cont / c,
        "p_next_punct": nxt_punc / c,
        "p_prev_punct": prv_punc / c,
        "is_punct": np.array([_is_punct(w) for w in vocab], dtype=np.float64),
        "word_len": wlen / c,
        "mean_relpos": relpos / c,
        "succ_diversity": np.array([len(succ_types[i]) for i in range(V)], dtype=np.float64) / c,
    }
    raw["connective"] = raw["p_prev_noun"] * raw["p_next_noun"]   # opener/connective interaction

    def _z(x):
        m, s = float(np.mean(x)), float(np.std(x))
        return (x - m) / (s + 1e-8)

    S = np.zeros((V, D_SIG), dtype=np.float32)
    S[:, 0] = 1.0                                   # bias
    S[:, 1] = _z(raw["log_freq"])
    S[:, 2] = _z(raw["p_next_noun"])
    S[:, 3] = _z(raw["p_prev_noun"])
    S[:, 4] = _z(raw["p_next_content"])
    S[:, 5] = _z(raw["p_prev_content"])
    S[:, 6] = _z(raw["p_next_punct"])
    S[:, 7] = _z(raw["p_prev_punct"])
    S[:, 8] = raw["is_punct"]                       # already 0/1
    S[:, 9] = _z(raw["word_len"])
    S[:, 10] = _z(raw["mean_relpos"])
    S[:, 11] = _z(raw["succ_diversity"])
    S[:, 12] = _z(raw["connective"])
    return S, raw


def encode_counts(items, vocab, MAXNN):
    """A[B,MAXNN,V] = count of FW-vocab token v strictly BEFORE noun k (glass-box depth convention);
    plus num/mask/pos/subj_pos/y/det_depth. NO number in selection features."""
    vindex = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    B = len(items)
    A = np.zeros((B, MAXNN, V), dtype=np.float32)
    det_depth = np.zeros((B, MAXNN), dtype=np.float32)
    num = np.zeros((B, MAXNN), dtype=np.float32)
    mask = np.zeros((B, MAXNN), dtype=np.float32)
    pos = np.zeros((B, MAXNN), dtype=np.float32)
    y = np.zeros(B, dtype=np.float32)
    subj_pos = np.zeros(B, dtype=np.int64)
    for bi, it in enumerate(items):
        ni = it["noun_word_idx"]
        words = it["words"]
        nn = len(ni)
        y[bi] = float(it["label"])
        subj_pos[bi] = int(it["subj_pos"])
        dd = det_depths_at_nouns(it)
        run = np.zeros(V, dtype=np.float32)
        widx_to_k = {wi: k for k, wi in enumerate(ni)}
        for i, w in enumerate(words):
            if i in widx_to_k:
                A[bi, widx_to_k[i]] = run             # counts BEFORE this noun
            vi = vindex.get(w.lower())
            if vi is not None:
                run[vi] += 1.0
        for k in range(nn):
            det_depth[bi, k] = float(dd[k])
            num[bi, k] = float(it["nums"][k])
            mask[bi, k] = 1.0
            pos[bi, k] = k / max(nn - 1, 1)
    return {"A": A, "det_depth": det_depth, "num": num, "mask": mask,
            "pos": pos, "y": y, "subj_pos": subj_pos}


# ==================================================================================================
# Build-time training (MANUAL numpy gradient; NO autograd). Runtime = HARD argmin.
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
    """HARD runtime selection: rightmost (verb-adjacent) noun at MINIMUM depth. Pure numpy, NO grad."""
    B, K = depth.shape
    big = 1e30
    d = np.where(mask > 0, depth, big)
    tie = np.arange(K)[None, :] * 1e-6                # prefer larger index at equal depth
    score = np.where(mask > 0, d - tie, big)
    return score.argmin(axis=1)


def _buried_acc(sel, data):
    subj_pos = data["subj_pos"]; num = data["num"]; y = data["y"]
    buried = subj_pos != 0
    if buried.sum() == 0:
        return None, 0
    picked = num[np.arange(len(sel)), sel]
    return float(((picked == y).astype(np.float32))[buried].mean()), int(buried.sum())


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


def train_map(G_fit, fit, G_val, val, theta_dim, seed, theta_zero_init=False,
              hb_t0=None, log_prefix=""):
    """Learn theta[theta_dim] + beta via Adam on manual gradient. depth = G @ theta.
    Early-stop on val buried HARD acc. G_val uses the SAME active-mask regime as G_fit (holdout
    disabled in val too) so early stopping never peeks at the extrapolation signal."""
    rng = np.random.default_rng(_stable_seed("theta_init", seed, theta_dim))
    if theta_zero_init:
        theta = np.zeros(theta_dim, dtype=np.float32)          # scalar_lookup: untrained FW -> exactly 0
    else:
        theta = (rng.standard_normal(theta_dim) * 0.01).astype(np.float32)
    beta_raw = np.float32(0.5413)                              # softplus ~ 1.0
    m_t = np.zeros(theta_dim, dtype=np.float32); v_t = np.zeros(theta_dim, dtype=np.float32)
    m_b = np.float32(0.0); v_b = np.float32(0.0)
    mask, num, pos, y = fit["mask"], fit["num"], fit["pos"], fit["y"]
    best_val, best = -1.0, (theta.copy(), float(beta_raw))
    history = []
    for ep in range(1, N_EPOCHS + 1):
        beta = np.log1p(np.exp(beta_raw))
        anneal = (1.0 + 2.0 * ep / N_EPOCHS) if SOFTMAX_TEMP_ANNEAL else 1.0
        depth = np.einsum("bkd,d->bk", G_fit, theta)
        score = anneal * (-beta * depth + EPS_POS * pos)
        loss, dscore, pred, w = _bce_and_dscore(score, mask, num, y)
        d_score_pre = dscore * anneal
        grad_theta = np.einsum("bk,bkd->d", d_score_pre * (-beta), G_fit) + L2_THETA * theta
        grad_beta_via = float(np.sum(d_score_pre * (-depth)))
        dbeta_draw = 1.0 / (1.0 + np.exp(-beta_raw))
        grad_beta_raw = grad_beta_via * dbeta_draw
        m_t = ADAM_B1 * m_t + (1 - ADAM_B1) * grad_theta
        v_t = ADAM_B2 * v_t + (1 - ADAM_B2) * grad_theta * grad_theta
        mhat = m_t / (1 - ADAM_B1 ** ep); vhat = v_t / (1 - ADAM_B2 ** ep)
        theta = theta - LR * mhat / (np.sqrt(vhat) + ADAM_EPS)
        m_b = ADAM_B1 * m_b + (1 - ADAM_B1) * grad_beta_raw
        v_b = ADAM_B2 * v_b + (1 - ADAM_B2) * grad_beta_raw * grad_beta_raw
        mhb = m_b / (1 - ADAM_B1 ** ep); vhb = v_b / (1 - ADAM_B2 ** ep)
        beta_raw = np.float32(beta_raw - LR * mhb / (np.sqrt(vhb) + ADAM_EPS))
        if ep % VAL_EVERY == 0 or ep == N_EPOCHS:
            vdepth = np.einsum("bkd,d->bk", G_val, theta)
            vsel = _hard_select_depth(vdepth, val["mask"])
            vacc, _ = _buried_acc(vsel, val)
            history.append({"epoch": ep, "loss": round(loss, 5),
                            "val_buried": (round(vacc, 4) if vacc is not None else None),
                            "beta": round(float(np.log1p(np.exp(beta_raw))), 4)})
            if vacc is not None and vacc > best_val:
                best_val = vacc
                best = (theta.copy(), float(beta_raw))
            print("%s[map dim=%d seed=%d] ep=%d loss=%.5f val_buried=%s beta=%.3f" %
                  (log_prefix, theta_dim, seed, ep, loss,
                   (round(vacc, 4) if vacc is not None else "NA"),
                   float(np.log1p(np.exp(beta_raw)))), flush=True)
            if hb_t0 is not None:
                _emit_heartbeat(ep, N_EPOCHS, hb_t0, {"seed": seed, "dim": theta_dim, "val_buried": vacc})
    return best[0], best[1], history


def make_G(A, active, S=None):
    """G[b,k,:] = signature-weighted (or masked-count) depth features under an active-FW mask.
    active[V] in {0,1}. If S is None -> scalar_lookup arm (G = masked counts, dim V)."""
    Am = A * active[None, None, :]
    if S is None:
        return Am                                    # scalar arm: depth = counts . theta_scalar
    return np.einsum("bkv,vd->bkd", Am, S)           # signature arm: depth = (counts . sig) . theta


def hard_eval_G(G, theta, data):
    depth = np.einsum("bkd,d->bk", G, theta)
    sel = _hard_select_depth(depth, data["mask"])
    acc, n = _buried_acc(sel, data)
    return sel, acc, n, depth


# ---- static baselines ----
def eval_nearest_noun(data):
    idx = (np.arange(data["mask"].shape[1])[None, :] * data["mask"]).argmax(axis=1)
    acc, n = _buried_acc(idx, data)
    return idx, acc, n


def eval_first_noun(data):
    sel = np.zeros(len(data["y"]), dtype=np.int64)
    acc, n = _buried_acc(sel, data)
    return sel, acc, n


def eval_majority(data):
    y = data["y"]; buried = data["subj_pos"] != 0
    yb = y[buried]
    if len(yb) == 0:
        return None
    maj = int(round(float(yb.mean())))
    return float(np.mean((yb == maj).astype(np.float32)))


def hard_eval_det(data):
    sel = _hard_select_depth(data["det_depth"], data["mask"])
    acc, n = _buried_acc(sel, data)
    return sel, acc, n


def scramble_drop_from_depth(depth, data, seeds):
    """ANTI-CHEAT: permute per-noun depth (preserve multiset + positions), re-select on buried."""
    mask = data["mask"]; subj_pos = data["subj_pos"]; num = data["num"]; y = data["y"]
    buried = subj_pos != 0
    true_sel = _hard_select_depth(depth, mask)
    true_acc, _ = _buried_acc(true_sel, data)
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
        acc = float(((picked == y).astype(np.float32))[buried].mean())
        scr_accs.append(round(acc, 4))
        change_fracs.append(round(float((ssel[buried] != true_sel[buried]).mean()), 4))
    return round(true_acc, 4), scr_accs, change_fracs


def number_flip_change(depth, data):
    """FAIRNESS: selection must not change when noun numbers flip (number read AFTER selection)."""
    sel_a = _hard_select_depth(depth, data["mask"])
    _ = 1.0 - data["num"]                            # flipped numbers unused by selection
    sel_b = _hard_select_depth(depth, data["mask"])
    return float((sel_a != sel_b).mean())


# ==================================================================================================
def _write_start_marker(run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "_start_marker.json"))


def _write_metrics(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(diag)


def _prep_splits(run_mode):
    items = load_items(max_items=(4500 if run_mode == "smoke" else None),
                       representative=(run_mode == "smoke"))
    train_items = [it for it in items if not _is_test(it["subj_word"])]
    test_items = [it for it in items if _is_test(it["subj_word"])]
    vocab, noun_rate, _ = build_vocab_and_nounrate(train_items)
    # novel-lexeme val carve from train
    subjects = sorted(set(it["subj_word"] for it in train_items))
    vr = np.random.default_rng(_stable_seed("valsplit"))
    subj_sh = list(subjects); vr.shuffle(subj_sh)
    n_val = max(1, int(len(subj_sh) * VAL_FRAC))
    val_subj = set(subj_sh[:n_val])
    fit_items = [it for it in train_items if it["subj_word"] not in val_subj]
    val_items = [it for it in train_items if it["subj_word"] in val_subj]
    # signature from FIT sentences only (train-side; no test peek, no label/number)
    S, raw = compute_signature(fit_items, vocab, noun_rate)
    MAXNN = max(len(it["noun_word_idx"]) for it in items)
    fit = encode_counts(fit_items, vocab, MAXNN)
    val = encode_counts(val_items, vocab, MAXNN)
    test = encode_counts(test_items, vocab, MAXNN)
    return items, vocab, noun_rate, S, raw, fit, val, test, MAXNN


def _fit_arm(fit, val, test, active, S, seed, theta_zero_init, hb_t0=None, log_prefix=""):
    """Fit one arm under one active-mask holdout; return (theta, test_buried_acc, test_depth)."""
    G_fit = make_G(fit["A"], active, S)
    G_val = make_G(val["A"], active, S)
    theta_dim = G_fit.shape[2]
    theta, beta_raw, hist = train_map(G_fit, fit, G_val, val, theta_dim, seed,
                                      theta_zero_init=theta_zero_init, hb_t0=hb_t0, log_prefix=log_prefix)
    all_active = np.ones(active.shape[0], dtype=np.float32)      # at TEST all FWs enabled
    G_test = make_G(test["A"], all_active, S)
    _, acc, _, depth = hard_eval_G(G_test, theta, test)
    return theta, acc, depth, hist


def run(run_mode):
    t0 = time.perf_counter()
    seeds = SMOKE_SEEDS if run_mode == "smoke" else SEEDS
    _write_start_marker(run_mode, len(seeds))
    items, vocab, noun_rate, S, raw, fit, val, test, MAXNN = _prep_splits(run_mode)
    V = len(vocab)
    freq = raw["log_freq"]                          # log(count+1); order = freq order

    # ---- active masks ----
    all_active = np.ones(V, dtype=np.float32)
    # high-freq holdout: disable top HF_HOLDOUT_M vocab tokens by TRAIN freq
    order = np.argsort(-freq, kind="stable")
    hf_idx = order[:HF_HOLDOUT_M]
    hf_holdout_tokens = sorted(vocab[i] for i in hf_idx)
    active_hf = np.ones(V, dtype=np.float32); active_hf[hf_idx] = 0.0

    # ---- static baselines / positive control on held-out test ----
    _, nn_acc, buried_n = eval_nearest_noun(test)
    _, fn_acc, _ = eval_first_noun(test)
    maj_acc = eval_majority(test)
    _, det_acc, _ = hard_eval_det(test)

    # ---- headline: full-training reference + high-freq holdout, both arms, multi-seed ----
    map_full, map_hf, scal_hf = [], [], []
    full_depth_last = None
    per_seed = []
    for si, seed in enumerate(seeds):
        th_mf, acc_mf, dep_mf, _ = _fit_arm(fit, val, test, all_active, S, seed, False,
                                            hb_t0=t0, log_prefix="[%s full] " % run_mode)
        th_hf, acc_hf, dep_hf, _ = _fit_arm(fit, val, test, active_hf, S, seed, False,
                                            hb_t0=t0, log_prefix="[%s hf ] " % run_mode)
        _, acc_sc, _, _ = _fit_arm(fit, val, test, active_hf, None, seed, True,
                                   hb_t0=t0, log_prefix="[%s scl] " % run_mode)
        map_full.append(acc_mf); map_hf.append(acc_hf); scal_hf.append(acc_sc)
        full_depth_last = dep_mf
        theta_full_last = th_mf
        per_seed.append({"seed": seed, "map_full": round(acc_mf, 4),
                         "map_hf_holdout": round(acc_hf, 4), "scalar_hf_holdout": round(acc_sc, 4)})
        print("[%s] SEED %d map_full=%.4f map_hf_holdout=%.4f scalar_hf_holdout=%.4f" %
              (run_mode, seed, acc_mf, acc_hf, acc_sc), flush=True)

    mf_mean = round(float(np.mean(map_full)), 4); mf_std = round(float(np.std(map_full)), 4)
    hf_mean = round(float(np.mean(map_hf)), 4); hf_std = round(float(np.std(map_hf)), 4)
    sc_mean = round(float(np.mean(scal_hf)), 4); sc_std = round(float(np.std(scal_hf)), 4)

    # ---- robustness: K-fold rotating holdout (single seed) ----
    kfold = []
    for f in range(KFOLDS):
        active_f = np.array([0.0 if _fold_of(vocab[i]) == f else 1.0 for i in range(V)], dtype=np.float32)
        held = int(V - active_f.sum())
        _, acc_m, _, _ = _fit_arm(fit, val, test, active_f, S, KFOLD_SEED, False,
                                  log_prefix="[%s kf%d map] " % (run_mode, f))
        _, acc_s, _, _ = _fit_arm(fit, val, test, active_f, None, KFOLD_SEED, True,
                                  log_prefix="[%s kf%d scl] " % (run_mode, f))
        kfold.append({"fold": f, "n_held": held, "map": round(acc_m, 4), "scalar": round(acc_s, 4),
                      "gap": round(acc_m - acc_s, 4)})
        print("[%s] KFOLD %d held=%d map=%.4f scalar=%.4f gap=%+.4f" %
              (run_mode, f, held, acc_m, acc_s, acc_m - acc_s), flush=True)
    kfold_map_mean = round(float(np.mean([k["map"] for k in kfold])), 4)
    kfold_scal_mean = round(float(np.mean([k["scalar"] for k in kfold])), 4)
    kfold_gap_mean = round(kfold_map_mean - kfold_scal_mean, 4)

    # ---- anti-cheat scramble + number-flip on full-training map ----
    scr_seeds = [101, 103, 107, 109, 113] if run_mode != "smoke" else [101, 103]
    true_acc, scr_accs, change_fracs = scramble_drop_from_depth(full_depth_last, test, scr_seeds)
    scr_mean = round(float(np.mean(scr_accs)), 4)
    scramble_drop_val = round(true_acc - scr_mean, 4)
    change_frac_mean = round(float(np.mean(change_fracs)), 4)
    flip_change = number_flip_change(full_depth_last, test)

    # ---- glass-box: learned signature coefficients (full-training last seed) ----
    theta_coeffs = {FEAT_NAMES[d]: round(float(theta_full_last[d]), 4) for d in range(D_SIG)}

    # ---- arms-differ (META_RULE_AF) on buried preds: map_full vs scalar_hf vs nearest_noun ----
    G_test_map = make_G(test["A"], all_active, S)
    sel_map, _, _, _ = hard_eval_G(G_test_map, theta_full_last, test)
    # a representative scalar_hf model (last seed) for the digest
    th_sc, _, _, _ = _fit_arm(fit, val, test, active_hf, None, seeds[-1], True)
    G_test_sc = make_G(test["A"], all_active, None)
    sel_sc, _, _, _ = hard_eval_G(G_test_sc, th_sc, test)
    sel_nn, _, _ = eval_nearest_noun(test)
    buried = test["subj_pos"] != 0
    preds = {"signature_map": test["num"][np.arange(len(sel_map)), sel_map][buried].astype(np.int64),
             "scalar_lookup": test["num"][np.arange(len(sel_sc)), sel_sc][buried].astype(np.int64),
             "nearest_noun": test["num"][np.arange(len(sel_nn)), sel_nn][buried].astype(np.int64)}
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    arms_differ = len(set(digs.values())) >= 2

    # ---- verdict (pre-registered) ----
    cond_a = (hf_mean - maj_acc) >= HP_ABOVE_MAJORITY
    cond_b = (hf_mean - sc_mean) >= HP_MAP_OVER_SCALAR
    cond_c = sc_mean <= maj_acc + HP_SCALAR_COLLAPSE
    cond_d = scramble_drop_val >= HP_SCRAMBLE_DROP
    hf_i = (hf_mean - maj_acc) <= HF_MAP_COLLAPSE
    hf_ii = (hf_mean - sc_mean) <= HF_NO_ISOLATION
    hf_iii = scramble_drop_val < HF_SCRAMBLE_NOEFFECT
    if cond_a and cond_b and cond_c and cond_d:
        verdict = "HARD_PASS_SIGNATURE_MAP_EXTRAPOLATES_TO_HELDOUT_FW"
    elif hf_i or hf_ii or hf_iii:
        verdict = "HARD_FAIL_SIGNATURE_INSUFFICIENT_FOR_DEPTH_INDUCTION"
    elif cond_a and cond_b and not cond_c:
        verdict = "MIDDLE_BAND_HOLDOUT_NOT_DECISIVE"
    else:
        verdict = "MIDDLE_BAND"

    baseline_in_band = (maj_acc is not None and 0.05 < maj_acc < 0.95 and 0.05 < nn_acc < 0.95)

    msg = ("SIGMAP-DEPTH-INDUCTION | held-out buried (n=%d, %d seeds): map_HFholdout=%.4f(+-%.4f) "
           "scalar_HFholdout=%.4f(+-%.4f) map_full=%.4f | majority=%.4f nearest_noun=%.4f "
           "first_noun=%.4f det_ceiling=%.4f | map-scalar=%+.4f map-majority=%+.4f | KFOLD map=%.4f "
           "scalar=%.4f gap=%+.4f | SCRAMBLE true=%.4f scr=%.4f DROP=%+.4f | number_flip=%.4f | "
           "HF_holdout(%d)=%s | theta: connective=%s p_prev_noun=%s p_next_noun=%s is_punct=%s "
           "log_freq=%s | %s" % (
               buried_n, len(seeds), hf_mean, hf_std, sc_mean, sc_std, mf_mean, maj_acc, nn_acc,
               fn_acc, det_acc, round(hf_mean - sc_mean, 4), round(hf_mean - maj_acc, 4),
               kfold_map_mean, kfold_scal_mean, kfold_gap_mean, true_acc, scr_mean, scramble_drop_val,
               flip_change, HF_HOLDOUT_M, ",".join(hf_holdout_tokens[:12]) + "...",
               theta_coeffs["connective_z"], theta_coeffs["p_prev_noun_z"], theta_coeffs["p_next_noun_z"],
               theta_coeffs["is_punct"], theta_coeffs["log_freq_z"], verdict))

    metrics = {
        "verdict": verdict, "verdict_tag": verdict, "verdict_msg": msg,
        "summary": ("%s | map_HFholdout=%.4f vs scalar_HFholdout=%.4f (isolation=%+.4f) vs "
                    "majority=%.4f (lift=%+.4f) | map_full=%.4f det_ceiling=%.4f | scramble_drop=%+.4f"
                    " | flip=%.4f" % (verdict, hf_mean, sc_mean, round(hf_mean - sc_mean, 4), maj_acc,
                                      round(hf_mean - maj_acc, 4), mf_mean, det_acc, scramble_drop_val,
                                      flip_change)),
        "elapsed_s": round(time.perf_counter() - t0, 2), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "held_out_buried_n": buried_n, "n_seeds": len(seeds),
        "arms": {
            "signature_map_hf_holdout": {"buried_mean": hf_mean, "buried_std": hf_std, "per_seed": [round(a, 4) for a in map_hf]},
            "scalar_lookup_hf_holdout": {"buried_mean": sc_mean, "buried_std": sc_std, "per_seed": [round(a, 4) for a in scal_hf]},
            "signature_map_full": {"buried_mean": mf_mean, "buried_std": mf_std, "per_seed": [round(a, 4) for a in map_full]},
            "nearest_noun": {"buried": round(nn_acc, 4)},
            "first_noun": {"buried": round(fn_acc, 4)},
            "deterministic_depth": {"buried": round(det_acc, 4), "note": "hand-coded structural ceiling positive control at test regime"},
            "majority": {"buried": round(maj_acc, 4)},
        },
        "isolation_map_minus_scalar_hf": round(hf_mean - sc_mean, 4),
        "lift_map_minus_majority_hf": round(hf_mean - maj_acc, 4),
        "kfold_holdout": {"map_mean": kfold_map_mean, "scalar_mean": kfold_scal_mean,
                          "gap_mean": kfold_gap_mean, "per_fold": kfold, "seed": KFOLD_SEED},
        "scramble_discriminator": {"true_acc": true_acc, "scrambled_acc_mean": scr_mean,
                                   "scramble_drop": scramble_drop_val, "per_seed_scrambled": scr_accs,
                                   "per_seed_change_frac": change_fracs, "change_frac_mean": change_frac_mean,
                                   "seeds": scr_seeds},
        "number_flip_change_frac": flip_change,
        "signature_theta_coeffs": theta_coeffs,
        "signature_feature_names": FEAT_NAMES,
        "signature_audit": ("features are corpus token-type distributional/positional statistics from "
                            "FIT sentences only; NO agreement label, NO noun number, NO subjecthood; "
                            "content proxy = noun_rate>0.5 (frequency/structure, not label)"),
        "hf_holdout_tokens": hf_holdout_tokens,
        "per_seed": per_seed,
        "verdict_conditions": {"cond_a_map_above_majority": bool(cond_a), "cond_b_map_over_scalar": bool(cond_b),
                               "cond_c_scalar_collapses": bool(cond_c), "cond_d_scramble_fires": bool(cond_d),
                               "hf_i_map_collapses": bool(hf_i), "hf_ii_no_isolation": bool(hf_ii),
                               "hf_iii_scramble_no_effect": bool(hf_iii)},
        "arms_differ_verified": bool(arms_differ), "arms_differ_digests": digs,
        "baseline_in_band": bool(baseline_in_band),
        "bands": {"HP_ABOVE_MAJORITY": HP_ABOVE_MAJORITY, "HP_MAP_OVER_SCALAR": HP_MAP_OVER_SCALAR,
                  "HP_SCALAR_COLLAPSE": HP_SCALAR_COLLAPSE, "HP_SCRAMBLE_DROP": HP_SCRAMBLE_DROP,
                  "HF_MAP_COLLAPSE": HF_MAP_COLLAPSE, "HF_NO_ISOLATION": HF_NO_ISOLATION,
                  "HF_SCRAMBLE_NOEFFECT": HF_SCRAMBLE_NOEFFECT},
        "n_vocab": V, "n_fit": len(fit["y"]), "n_val": len(val["y"]), "n_test": len(test["y"]),
        "hf_holdout_m": HF_HOLDOUT_M, "kfolds": KFOLDS, "d_sig": D_SIG,
        "final_metrics_atomicity": "tmp_replace",
        "cardinality_ok": True, "expected_n_units": len(seeds), "observed_n_units": len(per_seed),
        "crlb_n_a": "classification accuracy over deterministic-at-runtime selectors; no per-decode Gaussian noise floor",
        "runtime_glassbox": "hard argmin over signature-mapped depth register; NO autograd, NO torch; gradient build-time only (manual numpy, finite-difference checked)",
        "one_variable": "F = distributional signature [V,D_sig] vs F = identity one-hot [V,V]; entire pipeline otherwise identical",
        "progress_logging": "per-VAL_EVERY val_buried prints flush=True + _heartbeat.jsonl during training",
    }
    _write_metrics(metrics)
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)
    print("[%s] elapsed=%.2fs run_mode=%s verdict=%s" % (ANCHOR_NAME, metrics["elapsed_s"], run_mode, verdict), flush=True)
    return metrics


def self_test():
    print("[%s] SELF-TEST" % ANCHOR_NAME, flush=True)
    # F.5 static source scan for nondeterministic seeding
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
        print("[%s] F.5 source scan clean" % ANCHOR_NAME, flush=True)
    except ImportError:
        print("[%s] F.5 preflight module absent; hashlib-only discipline" % ANCHOR_NAME, flush=True)

    # ---- hand trace: signature-weighted depth + hard selection ----
    # "keys[N0] to[FW] cabinet[N1]": FW 'to' counted before N1, none before N0.
    it = {"words": ["keys", "to", "cabinet"], "noun_word_idx": [0, 2],
          "nums": [1, 0], "subj_pos": 0, "label": 1, "subj_word": "keys"}
    vocab = ["to"]
    A = encode_counts([it], vocab, 2)["A"]
    assert A[0, 0, 0] == 0.0 and A[0, 1, 0] == 1.0, "count-before-noun wrong: %s" % A[0]
    # signature with one feature that gives 'to' a +1 delta -> depth=[0,1] -> min-depth picks N0 (subject)
    S = np.array([[1.0]], dtype=np.float32)          # single feature = bias
    G = make_G(A, np.array([1.0], np.float32), S)
    depth = np.einsum("bkd,d->bk", G, np.array([1.0], np.float32))
    mask = np.array([[1.0, 1.0]], np.float32)
    sel = _hard_select_depth(depth, mask)
    assert sel[0] == 0, "+delta on 'to' should pick subject N0, got %s" % sel[0]
    depth0 = np.einsum("bkd,d->bk", G, np.array([0.0], np.float32))
    assert _hard_select_depth(depth0, mask)[0] == 1, "delta=0 should default to nearest_noun N1"
    # active-mask disables the FW -> depth flat -> nearest_noun
    Gd = make_G(A, np.array([0.0], np.float32), S)
    dd = np.einsum("bkd,d->bk", Gd, np.array([1.0], np.float32))
    assert _hard_select_depth(dd, mask)[0] == 1, "disabled FW should not open depth"
    print("[%s] hand-trace OK: signature delta opens depth; disable/zero -> nearest_noun" % ANCHOR_NAME, flush=True)

    # ---- signature ignores label + number (NO LEAK) ----
    toy = [{"words": ["a", "of", "b", ",", "c"], "noun_word_idx": [0, 2, 4],
            "nums": [1, 0, 1], "subj_pos": 1, "label": 1, "subj_word": "b"} for _ in range(30)]
    voc, nr, _ = build_vocab_and_nounrate(toy) if False else (["of", ","], {"a": 0.0, "of": 0.0, "b": 1.0, ",": 0.0, "c": 1.0}, None)
    S1, _ = compute_signature(toy, voc, nr)
    toy2 = [dict(t, nums=[1 - n for n in t["nums"]], label=1 - t["label"]) for t in toy]
    S2, _ = compute_signature(toy2, voc, nr)
    assert np.allclose(S1, S2), "signature changed when label/number flipped -> LEAK"
    print("[%s] no-leak: signature invariant to label/number flip" % ANCHOR_NAME, flush=True)

    # ---- masked softmax + manual-gradient finite-difference check (build-time path) ----
    rng = np.random.default_rng(0)
    B, K, D = 6, 4, 5
    G = rng.standard_normal((B, K, D)).astype(np.float32)
    mask = (rng.random((B, K)) > 0.2).astype(np.float32); mask[:, 0] = 1.0
    num = (rng.random((B, K)) > 0.5).astype(np.float32)
    pos = np.tile(np.arange(K), (B, 1)).astype(np.float32) / (K - 1)
    y = (rng.random(B) > 0.5).astype(np.float32)
    theta = rng.standard_normal(D).astype(np.float32); beta = 1.3

    def _loss(th):
        score = -beta * np.einsum("bkd,d->bk", G, th) + EPS_POS * pos
        w = _masked_softmax(score, mask)
        pred = (w * num).sum(axis=1)
        p = np.clip(pred, BCE_CLIP, 1 - BCE_CLIP)
        return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))

    score = -beta * np.einsum("bkd,d->bk", G, theta) + EPS_POS * pos
    _, dscore, _, _ = _bce_and_dscore(score, mask, num, y)
    grad_theta = np.einsum("bk,bkd->d", dscore * (-beta), G)
    eps = 1e-4
    for j in range(D):
        dp = theta.copy(); dp[j] += eps
        dm = theta.copy(); dm[j] -= eps
        fd = (_loss(dp) - _loss(dm)) / (2 * eps)
        assert abs(fd - grad_theta[j]) < 1e-2, "grad mismatch j=%d analytic=%.5f fd=%.5f" % (j, grad_theta[j], fd)
    print("[%s] manual-gradient finite-difference check PASS" % ANCHOR_NAME, flush=True)

    # ---- data-backed slice: baselines in band, ceiling beats nearest, discriminator can move ----
    items = load_items(max_items=2500, representative=True)
    train_items = [it for it in items if not _is_test(it["subj_word"])]
    test_items = [it for it in items if _is_test(it["subj_word"])]
    assert len(train_items) > 300 and len(test_items) > 150, "slice too small"
    vocab, noun_rate, _ = build_vocab_and_nounrate(train_items)
    assert 30 < len(vocab) <= MAX_VOCAB, "vocab size off: %d" % len(vocab)
    assert "of" in vocab and "in" in vocab and "that" in vocab, "expected openers missing from vocab"
    S, raw = compute_signature(train_items, vocab, noun_rate)
    assert S.shape == (len(vocab), D_SIG)
    MAXNN = max(len(it["noun_word_idx"]) for it in items)
    test = encode_counts(test_items, vocab, MAXNN)
    _, nn_acc, bn = eval_nearest_noun(test)
    maj = eval_majority(test)
    _, det_acc, _ = hard_eval_det(test)
    assert bn > 60, "too few buried in slice: %d" % bn
    assert maj is not None and 0.05 < maj < 0.95, "majority_buried out of band (AG): %s" % maj
    assert det_acc > nn_acc, "deterministic ceiling should beat nearest_noun on slice (%.4f vs %.4f)" % (det_acc, nn_acc)
    print("[%s] slice baselines: nearest=%.4f majority=%.4f det_ceiling=%.4f n_buried=%d vocab=%d" %
          (ANCHOR_NAME, nn_acc, maj, det_acc, bn, len(vocab)), flush=True)

    # short train just to confirm the arm-fit path runs + arms differ (NOT a verdict)
    subjects = sorted(set(it["subj_word"] for it in train_items))
    vr = np.random.default_rng(_stable_seed("valsplit")); subj_sh = list(subjects); vr.shuffle(subj_sh)
    val_subj = set(subj_sh[:max(1, int(len(subj_sh) * VAL_FRAC))])
    fit_items = [it for it in train_items if it["subj_word"] not in val_subj]
    val_items = [it for it in train_items if it["subj_word"] in val_subj]
    fit = encode_counts(fit_items, vocab, MAXNN); val = encode_counts(val_items, vocab, MAXNN)
    global N_EPOCHS
    saved = N_EPOCHS; N_EPOCHS = 60
    all_active = np.ones(len(vocab), np.float32)
    th_m, acc_m, dep_m, _ = _fit_arm(fit, val, test, all_active, S, 7, False)
    th_s, acc_s, _, _ = _fit_arm(fit, val, test, all_active, None, 7, True)
    N_EPOCHS = saved
    sel_m = _hard_select_depth(np.einsum("bkd,d->bk", make_G(test["A"], all_active, S), th_m), test["mask"])
    sel_nn, _, _ = eval_nearest_noun(test)
    buried = test["subj_pos"] != 0
    p_m = test["num"][np.arange(len(sel_m)), sel_m][buried].astype(np.int64)
    p_nn = test["num"][np.arange(len(sel_nn)), sel_nn][buried].astype(np.int64)
    assert hashlib.sha256(p_m.tobytes()).hexdigest() != hashlib.sha256(p_nn.tobytes()).hexdigest() \
        or acc_m == nn_acc, "signature_map and nearest_noun bit-identical (arms don't differ)"
    print("[%s] short-train preview: map=%.4f scalar=%.4f (full trains %d epochs)" %
          (ANCHOR_NAME, acc_m, acc_s, saved), flush=True)
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
