#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_agreement_attractor_role_binding_cg_viability_v1

TWO-STAGE VIABILITY PROBE (design-gated, can-fail). First real-text compositional-generalization
(chain-grade) shot in the program: can the glass-box substrate LEARN subject-verb agreement ACROSS AN
ATTRACTOR -- i.e. discover, from labeled examples on RAW token structure, that predictive weight
belongs on the syntactic-HEAD noun (the subject) not the linearly-NEAREST noun -- without being handed
a parse? Real corpus: Linzen, Dupoux & Goldberg 2016 Wikipedia agreement (primary); Gulordava et al
2018 English nonce (confound-killing transfer cross-check).

FAIRNESS DESIGN (USER-directed; a violation voids the result):
  TAUGHT-then-GENERALIZE, not discover-untaught. It is FAIR to TEACH the role/position-binding SCAFFOLD
  and to give raw-token-derivable HINTS (position ranks + the preceding function-word class of each
  noun -- all present in the raw input, NOT a parse). What must be the SUBSTRATE'S OWN is the learned
  WEIGHTING that GENERALIZES to held-out items -- we never hand-install "the subject is noun k".

STAGE 1 (REPRESENTABILITY, run first, cheap): the whole prefix's noun-number map is held in ONE bound
  HRR superposition S (brain-faithful: a single working-memory state, agreement resolved by cue-based
  content-addressable retrieval a la Wagers/Lau/Phillips 2009). GIVEN the ORACLE subject position
  (teaching), unbind its role from S and read the number. If the addressed head-number does NOT survive
  the superposition crosstalk (acc < floor), a downstream learning failure would be a rigged-encoding
  artifact -> we report REPRESENTABILITY_FAIL_REDESIGN, Stage 2 is not interpretable. This gate must
  pass first.

STAGE 2 (LEARNABILITY, no oracle): the SAME raw structure, NO parse / NO head feature. A glass-box
  logistic readout reads the substrate's own role-slots (unbind from S -> signed number score per slot)
  and must DISCOVER the head-tracking weighting from labels. Held-out by NOVEL SUBJECT LEXEME
  (compound-divergence-style; the substrate encoding is LEXEME-FREE by construction so lexical
  memorization is architecturally impossible -- the win must be structural).

FAIR BASELINES (SAME raw structural input; computed directly, NOT via substrate):
  B_nearest  : nearest-noun-number (last noun before verb) -- the STANDARD surface baseline. On the
               label-balanced attractor subset the nearest noun is ~always the attractor -> BELOW chance
               (this corpus makes the surface heuristic actively wrong). Must be beaten.
  B_first    : first-noun-number -- a STRONGER positional heuristic here (subjects sit early). Beating
               nearest-noun is trivial; the HONEST bar is beating FIRST-NOUN, esp. on the
               subject-is-NOT-first-noun (SNF) subset where first-noun is at/below chance -> that is the
               genuine HEAD-TRACKING discriminator (identify the subject when it is not simply "first").
  B_major    : majority-class / frequency-only baseline (the note's chance/frequency reference).
  B_anynoun  : permissive "any noun plural -> plural" vote -- loophole sanity check (must NOT silently
               recover the label).

DISCRIMINATOR (primary): substrate_SNF_acc - max(first_noun_SNF, majority_SNF) on the held-out
  subject-not-first subset. A pure positional-heuristic collapse (substrate ~ first-noun) is MIDDLE, not
  a head-tracking win. Real head-tracking uses the function-word structure (subjects almost never PREP/
  REL-preceded; attractors often are) -- learnable from raw tokens.

MUST-FAIL control: WRONG-ROLE unbind (roles never used in the binding) -> the role-addressed reads
  become noise -> readout collapses to ~majority. Confirms the signal comes from the role-binding, not
  an artifact of the clean feature list. ABLATION: readout on CLEAN (non-superposition) number votes
  isolates the crosstalk cost; kNN-on-substrate-features (arm D) attributes representation vs learner.

HONEST FRAMING: a HARD_PASS is "THIS mechanism + THESE conditions LEARNED the head-tracking feature
  from raw structure on real text" -- a GREEN-LIGHT-PENDING-VET, not a self-declared CG. A HARD_FAIL is
  "THIS mechanism did not acquire the feature here" (a well-specified negative pointing at a needed
  structure-induction capability), NEVER "the substrate cannot".

# CELL-TEMPLATE MANDATORY:
# - arms_differ asserted (baselines + substrate + wrong-role predictions distinct; weights non-degenerate)
# - final_metrics_atomicity: tmp_replace ; except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator survives scale: smoke = FULL N_DIM (option A), 2 seeds; full 3 seeds
# - baseline_in_band: B_major ~0.5-0.62 (0.05<acc<0.95); substrate expected above it
# - crlb_n/a: real-text agreement discrimination; the floor is HRR superposition crosstalk (reported as
#   Stage-1 oracle-read accuracy), not an argmax-capacity CRLB
# - deterministic_seeding: fixed ints + hashlib atoms (no builtin-hash, no list-set dedupe); progress flush
# - cardinality_ok: n_seed_rows == len(seeds)
# LOCAL SMOKE ; FULL routes remote_cpu_queue (reads committed cache). No push / no store write / no atom
#   bank. ASCII only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import gzip
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "agreement_attractor_role_binding_cg_viability_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

CACHE = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agreement_probe_cache_v1.json.gz")

# ---- config ----
N_DIM = 2048                  # HRR dim; superposition holds up to ~3*n_nouns bound pairs
R_RANK = 8                    # read ranks 1..R from each end (rank-from-verb, rank-from-start)
N_FWC = 6                     # function-word classes (START,DET,PREP,REL,CCONJ,OTHER)
READOUT_STEPS = 600
READOUT_LR = 0.5
L2 = 1e-3
FULL_SEEDS = [7, 13, 19]
SMOKE_SEEDS = [7, 13]
FULL_TRAIN_CAP = 6000
FULL_TEST_CAP = 6000
SMOKE_TRAIN_CAP = 700
SMOKE_TEST_CAP = 500
TEST_HASH_MOD = 5             # subj_word hash % MOD < TEST_FRAC_CUT -> held-out (novel lexeme)
TEST_FRAC_CUT = 2            # -> ~40% held out, disjoint subject lexemes

# ---- pre-registered bands ----
STAGE1_REPRESENTABLE_MIN = 0.90   # oracle-head-number read from S must survive crosstalk
HEADTRACK_MARGIN = 0.10           # substrate SNF acc must beat max(first-noun, majority) SNF by this
CONFLICT_BEAT_MAJOR = 0.15        # substrate must beat majority on the aggregate conflict subset by this
WRONGROLE_COLLAPSE_MIN = 0.10     # substrate_SNF - structshuffle_SNF (win must come from STRUCTURE not counts)
BIN4_ABOVE_CHANCE_MIN = 0.55      # substrate acc at 4 attractors stays above chance


# ==================================================================================================
# HD atoms (deterministic hashlib -> gaussian; no PYTHONHASHSEED dependence). One atom set per seed.
# ==================================================================================================
def _atom(token, n_dim):
    seed = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:8], "big")
    v = np.random.default_rng(seed).standard_normal(n_dim).astype(np.float32)
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def build_atoms(seed_tag, n_dim):
    """Roles for rank-from-verb (RV), rank-from-start (RS), function-word-class (FW); number atoms
    SING/PLUR. One atom set per seed (deterministic)."""
    rv = [_atom("%s:RV:%d" % (seed_tag, k), n_dim) for k in range(R_RANK)]
    rs = [_atom("%s:RS:%d" % (seed_tag, k), n_dim) for k in range(R_RANK)]
    fw = [_atom("%s:FW:%d" % (seed_tag, k), n_dim) for k in range(N_FWC)]
    num = {0: _atom("%s:NUM:SING" % seed_tag, n_dim), 1: _atom("%s:NUM:PLUR" % seed_tag, n_dim)}
    return {"rv": rv, "rs": rs, "fw": fw, "num": num}


# ==================================================================================================
# HRR bind/unbind. self_test asserts the vectorized numpy-FFT path is BIT-CLOSE to hdlab.binding
# (real substrate primitive; gate F.1). Batched encoding uses the vectorized path for speed.
# ==================================================================================================
def _fft(v):
    return np.fft.fft(v, axis=-1)


def encode_items(items, atoms, n_dim, structshuffle_seed=None):
    """Return (n_items, 2*R_RANK + N_FWC) signed-number feature matrix read from the per-item HRR
    superposition S via unbind (roles == the real rv/rs/fw sets throughout).
    S = sum over prefix nouns of [ bind(RV[rank_from_verb], NUM[num]) + bind(RS[rank_from_start], NUM)
        + bind(FW[class], NUM) ]. Feature = cos(unbind(S, role), PLUR) - cos(unbind(S, role), SING).

    structshuffle_seed (MUST-FAIL structural control): if set, each item's number labels are randomly
    PERMUTED across its noun slots before binding -- this PRESERVES the bag-of-noun-numbers COUNT but
    DESTROYS every number<->position and number<->function-word association. If the substrate's
    predictive advantage survives this shuffle, it is riding noun-COUNTS, not role/position STRUCTURE;
    a genuine head-tracking win must beat this control."""
    RV = np.asarray([atoms["rv"][k] for k in range(R_RANK)], dtype=np.float32)  # (R,N)
    RS = np.asarray([atoms["rs"][k] for k in range(R_RANK)], dtype=np.float32)
    FW = np.asarray([atoms["fw"][k] for k in range(N_FWC)], dtype=np.float32)
    SING = atoms["num"][0]; PLUR = atoms["num"][1]
    fRVb = _fft(RV); fRSb = _fft(RS); fFWb = _fft(FW)
    fSING = _fft(SING); fPLUR = _fft(PLUR)
    cf_RV = np.conj(_fft(RV)); cf_RS = np.conj(_fft(RS)); cf_FW = np.conj(_fft(FW))

    n = len(items)
    feats = np.zeros((n, 2 * R_RANK + N_FWC), dtype=np.float32)
    for idx, it in enumerate(items):
        nums = it["nums"]; fwc = it["fwc"]; L = len(nums)
        if structshuffle_seed is not None:
            perm = np.random.default_rng((structshuffle_seed * 1_000_003 + idx)).permutation(L)
            nums = [nums[p] for p in perm]
        Sf = np.zeros(n_dim, dtype=np.complex128)
        for i in range(L):
            fnum = fPLUR if nums[i] == 1 else fSING
            rv_k = L - 1 - i            # rank_from_verb-1 (0-based): last noun -> 0
            rs_k = i                    # rank_from_start-1
            if rv_k < R_RANK:
                Sf += fRVb[rv_k] * fnum
            if rs_k < R_RANK:
                Sf += fRSb[rs_k] * fnum
            Sf += fFWb[fwc[i]] * fnum
        # normalize S in time domain
        S = np.fft.ifft(Sf).real
        nrm = float(np.linalg.norm(S))
        if nrm > 1e-9:
            Sf = Sf / nrm
        # unbind reads (frequency domain): read_r = ifft(Sf * conj(fft(role)))
        def score(cf_roles, nroles, off):
            for k in range(nroles):
                rd = np.fft.ifft(Sf * cf_roles[k]).real.astype(np.float32)
                rn = float(np.linalg.norm(rd)) + 1e-9
                cp = float(rd @ PLUR) / rn
                cs = float(rd @ SING) / rn
                feats[idx, off + k] = cp - cs
        score(cf_RV, R_RANK, 0)
        score(cf_RS, R_RANK, R_RANK)
        score(cf_FW, N_FWC, 2 * R_RANK)
    return feats


def clean_features(items):
    """Non-superposition number votes (crosstalk-free upper bound / ablation). Same layout as
    encode_items: signed number (+1 plural / -1 singular) per role slot; multi-noun FW slots averaged."""
    n = len(items)
    feats = np.zeros((n, 2 * R_RANK + N_FWC), dtype=np.float32)
    for idx, it in enumerate(items):
        nums = it["nums"]; fwc = it["fwc"]; L = len(nums)
        fwc_acc = np.zeros(N_FWC, dtype=np.float32); fwc_cnt = np.zeros(N_FWC, dtype=np.float32)
        for i in range(L):
            s = 1.0 if nums[i] == 1 else -1.0
            rv_k = L - 1 - i; rs_k = i
            if rv_k < R_RANK:
                feats[idx, rv_k] = s
            if rs_k < R_RANK:
                feats[idx, R_RANK + rs_k] = s
            fwc_acc[fwc[i]] += s; fwc_cnt[fwc[i]] += 1.0
        for c in range(N_FWC):
            if fwc_cnt[c] > 0:
                feats[idx, 2 * R_RANK + c] = fwc_acc[c] / fwc_cnt[c]
    return feats


# ---- glass-box logistic readout (inspectable) ----
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def train_readout(X, y, steps, lr, l2, seed):
    rng = np.random.default_rng(seed)
    d = X.shape[1]
    w = rng.standard_normal(d).astype(np.float64) * 0.01
    b = 0.0
    Xd = X.astype(np.float64); yd = y.astype(np.float64); n = len(yd)
    for _ in range(steps):
        p = _sigmoid(Xd @ w + b)
        g = p - yd
        w -= lr * ((Xd.T @ g) / n + l2 * w)
        b -= lr * float(np.mean(g))
    return w, b


def readout_predict(X, w, b):
    return (_sigmoid(X.astype(np.float64) @ w + b) >= 0.5).astype(int)


def knn_predict(trainX, trainY, testX):
    tX = trainX.astype(np.float64)
    tX = tX / (np.linalg.norm(tX, axis=1, keepdims=True) + 1e-9)
    preds = []
    for hx in testX:
        h = hx.astype(np.float64); h = h / (np.linalg.norm(h) + 1e-9)
        preds.append(int(trainY[int(np.argmax(tX @ h))]))
    return np.array(preds, dtype=int)


def _acc(pred, gold):
    return float(np.mean(np.asarray(pred) == np.asarray(gold)))


# ==================================================================================================
# Data.
# ==================================================================================================
def load_cache():
    if not os.path.exists(CACHE):
        raise FileNotFoundError(
            "agreement probe cache not found: %s -- run tools/prep_agreement_probe_cache.py "
            "(needs the local Linzen corpus) and commit the cache." % CACHE)
    with gzip.open(CACHE, "rt", encoding="utf-8") as f:
        return json.load(f)


def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(subj_word.encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def split_items(linzen, train_cap, test_cap, seed):
    """Held-out by NOVEL subject lexeme (disjoint subj_word pools). Balanced-ish caps."""
    rng = np.random.default_rng(seed)
    train = [r for r in linzen if not _is_test(r["subj_word"])]
    test = [r for r in linzen if _is_test(r["subj_word"])]
    rng.shuffle(train); rng.shuffle(test)
    return train[:train_cap], test[:test_cap]


# baselines (clean, same raw structural input)
def b_nearest(it):
    return it["nums"][-1]


def b_first(it):
    return it["nums"][0]


def b_anynoun(it):
    return 1 if any(n == 1 for n in it["nums"]) else 0


def b_bagcount(it):
    """Net noun-number vote (plural nouns minus singular nouns); the pure count baseline."""
    s = sum(1 if n == 1 else -1 for n in it["nums"])
    return 1 if s >= 0 else 0


# ==================================================================================================
# Per-seed run.
# ==================================================================================================
def run_seed(seed, train_cap, test_cap, linzen, nonce, n_dim):
    atoms = build_atoms("s%d" % seed, n_dim)
    train, test = split_items(linzen, train_cap, test_cap, seed)
    ytr = np.array([r["label"] for r in train], dtype=int)
    yte = np.array([r["label"] for r in test], dtype=int)

    # ---- Stage 1: representability (oracle head number read from S) ----
    # read the SUBJECT's own rank-from-start slot from S; compare to true subject number (==label).
    feats_tr = encode_items(train, atoms, n_dim)
    feats_te = encode_items(test, atoms, n_dim)
    # oracle read: subject rank-from-start slot score sign -> predicted subject number
    def oracle_read_acc(items, feats):
        ok = 0; tot = 0
        for it, f in zip(items, feats):
            rs_k = it["subj_pos"]
            if rs_k >= R_RANK:
                continue
            pred = 1 if f[R_RANK + rs_k] > 0 else 0
            ok += int(pred == it["label"]); tot += 1
        return (ok / tot) if tot else 0.0, tot
    s1_acc_tr, s1_n_tr = oracle_read_acc(train, feats_tr)
    s1_acc_te, s1_n_te = oracle_read_acc(test, feats_te)

    # ---- Stage 2: learned readout (no oracle) on substrate features ----
    w, b = train_readout(feats_tr, ytr, READOUT_STEPS, READOUT_LR, L2, seed)
    pred_sub = readout_predict(feats_te, w, b)
    acc_sub = _acc(pred_sub, yte)

    # baselines on the SAME held-out set
    pred_near = np.array([b_nearest(r) for r in test], dtype=int)
    pred_first = np.array([b_first(r) for r in test], dtype=int)
    pred_any = np.array([b_anynoun(r) for r in test], dtype=int)
    pred_bag = np.array([b_bagcount(r) for r in test], dtype=int)
    maj = int(round(float(np.mean(ytr))))  # majority class from TRAIN
    pred_major = np.full(len(test), maj, dtype=int)
    acc_near = _acc(pred_near, yte); acc_first = _acc(pred_first, yte)
    acc_any = _acc(pred_any, yte); acc_major = _acc(pred_major, yte); acc_bag = _acc(pred_bag, yte)

    # ---- must-fail: STRUCTURE-SHUFFLE (same encoder, number<->slot associations destroyed, counts
    # preserved). Surviving this => the win rides noun-COUNTS not role/position STRUCTURE. ----
    feats_tr_ss = encode_items(train, atoms, n_dim, structshuffle_seed=seed)
    feats_te_ss = encode_items(test, atoms, n_dim, structshuffle_seed=1000 + seed)
    w_ss, b_ss = train_readout(feats_tr_ss, ytr, READOUT_STEPS, READOUT_LR, L2, seed)
    pred_ss = readout_predict(feats_te_ss, w_ss, b_ss)
    acc_ss = _acc(pred_ss, yte)

    # ---- ablation: clean (non-superposition) features + kNN attribution ----
    cf_tr = clean_features(train); cf_te = clean_features(test)
    w_cl, b_cl = train_readout(cf_tr, ytr, READOUT_STEPS, READOUT_LR, L2, seed)
    acc_clean = _acc(readout_predict(cf_te, w_cl, b_cl), yte)
    acc_knnD = _acc(knn_predict(feats_tr, ytr, feats_te), yte)

    # ---- scramble control (informational) ----
    rng = np.random.default_rng(3000 + seed)
    ys = ytr[rng.permutation(len(ytr))]
    w_s, b_s = train_readout(feats_tr, ys, READOUT_STEPS, READOUT_LR, L2, seed)
    acc_scr = _acc(readout_predict(feats_te, w_s, b_s), yte)

    # ---- subsets: conflict (nearest != label) and subject-not-first (SNF) ----
    conflict = np.array([b_nearest(r) != r["label"] for r in test])
    snf = np.array([r["subj_pos"] != 0 for r in test])
    def sub_acc(mask, pred):
        if int(mask.sum()) == 0:
            return None, 0
        return float(np.mean(np.asarray(pred)[mask] == yte[mask])), int(mask.sum())
    sub_sub_conf, n_conf = sub_acc(conflict, pred_sub)
    maj_conf, _ = sub_acc(conflict, pred_major)
    near_conf, _ = sub_acc(conflict, pred_near)
    bag_conf, _ = sub_acc(conflict, pred_bag)
    sub_snf, n_snf = sub_acc(snf, pred_sub)
    first_snf, _ = sub_acc(snf, pred_first)
    maj_snf, _ = sub_acc(snf, pred_major)
    near_snf, _ = sub_acc(snf, pred_near)
    bag_snf, _ = sub_acc(snf, pred_bag)
    ss_snf, _ = sub_acc(snf, pred_ss)

    # ---- per attractor-bin substrate accuracy ----
    per_bin = {}
    for bcount in range(5):
        mask = np.array([r["ndiff"] == bcount for r in test])
        a, nn = sub_acc(mask, pred_sub)
        per_bin[str(bcount)] = {"acc": (round(a, 4) if a is not None else None), "n": nn}
    bin4 = per_bin["4"]["acc"]

    # ---- nonce transfer cross-check (frozen readout on Gulordava nonce; optional/graceful) ----
    nonce_res = nonce_transfer(nonce, atoms, n_dim, w, b)

    # ---- arms-differ + weights ----
    hashes = {
        "sub": hashlib.sha256(pred_sub.tobytes()).hexdigest(),
        "near": hashlib.sha256(pred_near.tobytes()).hexdigest(),
        "first": hashlib.sha256(pred_first.tobytes()).hexdigest(),
        "ss": hashlib.sha256(pred_ss.tobytes()).hexdigest(),
    }
    arms_differ = len(set(hashes.values())) >= 3
    weights_nondeg = bool(float(np.max(np.abs(w))) > 1e-4)

    # readable weight summary (which slots the learner relies on)
    wsum = {
        "RV1_nearest": round(float(w[0]), 3),
        "RS1_first": round(float(w[R_RANK]), 3),
        "FW_START": round(float(w[2 * R_RANK + 0]), 3),
        "FW_DET": round(float(w[2 * R_RANK + 1]), 3),
        "FW_PREP": round(float(w[2 * R_RANK + 2]), 3),
        "FW_REL": round(float(w[2 * R_RANK + 3]), 3),
        "FW_CCONJ": round(float(w[2 * R_RANK + 4]), 3),
    }

    return {
        "seed": seed, "n_train": len(train), "n_test": len(test),
        "stage1_oracle_read_acc_train": round(s1_acc_tr, 4), "stage1_n_train": s1_n_tr,
        "stage1_oracle_read_acc_test": round(s1_acc_te, 4), "stage1_n_test": s1_n_te,
        "acc_substrate": round(acc_sub, 4),
        "acc_nearest": round(acc_near, 4), "acc_first": round(acc_first, 4),
        "acc_majority": round(acc_major, 4), "acc_anynoun": round(acc_any, 4),
        "acc_bagcount": round(acc_bag, 4),
        "acc_structshuffle": round(acc_ss, 4), "acc_clean_ablation": round(acc_clean, 4),
        "acc_knn_relational_D": round(acc_knnD, 4), "acc_scramble_info": round(acc_scr, 4),
        "conflict_subset": {"n": n_conf, "substrate": _r(sub_sub_conf), "majority": _r(maj_conf),
                            "nearest": _r(near_conf), "bagcount": _r(bag_conf)},
        "snf_subset": {"n": n_snf, "substrate": _r(sub_snf), "first_noun": _r(first_snf),
                       "majority": _r(maj_snf), "nearest": _r(near_snf), "bagcount": _r(bag_snf),
                       "structshuffle": _r(ss_snf)},
        "per_attractor_bin": per_bin, "bin4_substrate_acc": bin4,
        "nonce_transfer": nonce_res,
        "learned_weights_summary": wsum,
        "arms_differ": bool(arms_differ), "weights_nondegenerate": weights_nondeg,
    }


def _r(x):
    return round(x, 4) if x is not None else None


# ==================================================================================================
# Nonce transfer cross-check (Gulordava English). POS-tag prefix -> same structural features -> apply
# FROZEN Linzen-trained readout. Graceful: if tagging unavailable, report deferred (never fabricate).
# ==================================================================================================
def nonce_to_item(prefix):
    """POS-tag a nonce prefix with hdlab.pos_tagger; extract the same lexeme-free noun-number/fnword
    structural features. Returns an item dict or None."""
    try:
        from hdlab.pos_tagger import tag as pos_tag
    except Exception:
        return None
    try:
        toks = prefix.split()
        tags = pos_tag(toks)
    except Exception:
        return None
    if not tags or len(tags) != len(toks):
        return None
    NOUN = {"NN", "NNP", "NNS", "NNPS"}
    PLURAL = {"NNS", "NNPS"}
    from tools.prep_agreement_probe_cache import fwc_of  # reuse identical mapping
    nums = []; fwc = []
    for i, (tk, tg) in enumerate(zip(toks, tags)):
        if tg not in NOUN:
            continue
        prev = tags[i - 1] if i >= 1 else None
        nums.append(1 if tg in PLURAL else 0)
        fwc.append(fwc_of(prev))
    if not nums:
        return None
    return {"nums": nums, "fwc": fwc, "subj_pos": 0, "label": 0, "ndiff": 0}


def nonce_transfer(nonce, atoms, n_dim, w, b):
    out = {"available": False, "note": "", "n": 0, "acc": None}
    if not nonce:
        out["note"] = "no nonce items in cache"; return out
    gens = [r for r in nonce if r.get("type") == "generated"]
    items = []; labels = []
    for r in gens:
        it = nonce_to_item(r["prefix"])
        if it is None:
            continue
        items.append(it); labels.append(r["label"])
    if len(items) < 20:
        out["note"] = ("nonce transfer DEFERRED: POS-tagging unavailable or <20 taggable prefixes "
                       "(got %d). Substrate encoding is lexeme-free so lexical-memorization confound is "
                       "architecturally excluded regardless; nonce is a redundant secondary check here."
                       % len(items))
        return out
    try:
        feats = encode_items(items, atoms, n_dim)
        pred = readout_predict(feats, w, b)
        acc = _acc(pred, np.array(labels, dtype=int))
        out.update({"available": True, "n": len(items), "acc": round(acc, 4),
                    "note": "frozen Linzen-trained readout applied to Gulordava nonce prefixes"})
    except Exception as e:
        out["note"] = "nonce transfer error: %s" % (str(e)[:150],)
    return out


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def _mean_sub(rows, sub, key):
    vals = [r[sub][key] for r in rows if r.get(sub, {}).get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows):
    m_s1 = _mean(rows, "stage1_oracle_read_acc_test")
    m_sub = _mean(rows, "acc_substrate")
    m_near = _mean(rows, "acc_nearest"); m_first = _mean(rows, "acc_first")
    m_major = _mean(rows, "acc_majority"); m_bag = _mean(rows, "acc_bagcount")
    m_ss = _mean(rows, "acc_structshuffle")
    m_clean = _mean(rows, "acc_clean_ablation"); m_knnD = _mean(rows, "acc_knn_relational_D")
    # conflict subset
    c_sub = _mean_sub(rows, "conflict_subset", "substrate")
    c_maj = _mean_sub(rows, "conflict_subset", "majority")
    c_near = _mean_sub(rows, "conflict_subset", "nearest")
    # SNF subset (the head-tracking discriminator)
    snf_sub = _mean_sub(rows, "snf_subset", "substrate")
    snf_first = _mean_sub(rows, "snf_subset", "first_noun")
    snf_maj = _mean_sub(rows, "snf_subset", "majority")
    snf_bag = _mean_sub(rows, "snf_subset", "bagcount")
    snf_ss = _mean_sub(rows, "snf_subset", "structshuffle")
    m_bin4 = _mean(rows, "bin4_substrate_acc")

    arms_ok = all(r["arms_differ"] for r in rows) if rows else False
    weights_ok = all(r["weights_nondegenerate"] for r in rows) if rows else False
    baseline_in_band = (m_major is not None and 0.05 < m_major < 0.95)

    # Stage 1 gate
    stage1_pass = (m_s1 is not None and m_s1 >= STAGE1_REPRESENTABLE_MIN)

    # primary head-tracking discriminator (SNF): substrate must beat the STRONGEST non-structural
    # heuristic available on the subject-not-first subset -- first-noun, majority AND bag-of-counts.
    snf_base = max([x for x in [snf_first, snf_maj, snf_bag] if x is not None], default=None)
    headtrack_delta = round(snf_sub - snf_base, 4) if (snf_sub is not None and snf_base is not None) else None
    headtrack_win = (headtrack_delta is not None and headtrack_delta >= HEADTRACK_MARGIN)

    # aggregate conflict gate (beat majority + nearest)
    conflict_win = (c_sub is not None and c_maj is not None and c_near is not None
                    and (c_sub - c_maj) >= CONFLICT_BEAT_MAJOR and c_sub > c_near)

    # STRUCTURE must-fail collapse: substrate must beat the structure-shuffle control (counts preserved,
    # number<->slot structure destroyed) on the SNF subset -- proves the win comes from POSITION/
    # function-word STRUCTURE, not noun COUNTS.
    structure_used = (snf_ss is not None and snf_sub is not None
                      and (snf_sub - snf_ss) >= WRONGROLE_COLLAPSE_MIN)

    bin4_ok = (m_bin4 is not None and m_bin4 >= BIN4_ABOVE_CHANCE_MIN)

    learns_something = (m_sub is not None and m_major is not None and (m_sub - m_major) >= 0.05)

    if not stage1_pass:
        verdict = "REPRESENTABILITY_FAIL_REDESIGN"
        note = ("Stage-1 oracle-head number read from the HRR superposition = %s < %.2f: the head-number "
                "feature does NOT survive binding crosstalk at N_DIM=%d. A Stage-2 learning failure would "
                "be a rigged-encoding artifact, not informative. Redesign (raise N_DIM / reduce bound "
                "pairs) before interpreting learnability." % (m_s1, STAGE1_REPRESENTABLE_MIN, N_DIM))
    elif (headtrack_win and conflict_win and structure_used and bin4_ok and arms_ok and weights_ok):
        verdict = "HARD_PASS_LEARNED_HEADTRACK_GREEN_LIGHT_PENDING_VET"
        note = ("Stage-1 representable (oracle-read=%s). Stage-2: substrate LEARNED readout BEATS the "
                "strongest non-structural heuristics (first-noun/majority/bag-count) on the held-out "
                "subject-not-first subset by %s (SNF sub=%s vs base=%s), beats majority on the conflict "
                "subset by %s (conf sub=%s maj=%s near=%s), holds above chance at 4 attractors (%s); the "
                "STRUCTURE-SHUFFLE must-fail collapses on SNF (ss=%s, sub-ss>=%.2f) so the win comes from "
                "POSITION/function-word STRUCTURE not noun COUNTS. Learned from RAW structure, LEXEME-FREE "
                "encoding (no lexical memorization). GREEN-LIGHT-PENDING-VET, NOT a self-declared CG: "
                "arm-D kNN=%s (representation-vs-learner attribution) + adversarial VET required."
                % (m_s1, headtrack_delta, snf_sub, snf_base, round(c_sub - c_maj, 4), c_sub, c_maj,
                   c_near, m_bin4, snf_ss, WRONGROLE_COLLAPSE_MIN, m_knnD))
    elif (not learns_something) or (c_sub is not None and c_near is not None and c_sub <= c_near):
        verdict = "HARD_FAIL_NO_LEARNED_STRUCTURE"
        reasons = []
        if not learns_something:
            reasons.append("substrate=%s barely beats majority=%s (learns ~nothing)" % (m_sub, m_major))
        if c_sub is not None and c_near is not None and c_sub <= c_near:
            reasons.append("does not beat nearest-noun on conflict subset (sub=%s near=%s)" % (c_sub, c_near))
        if not arms_ok:
            reasons.append("arms bit-identical")
        note = "; ".join(reasons) if reasons else "no learned structure"
    else:
        verdict = "MIDDLE_BAND_POSITIONAL_OR_COUNT_HEURISTIC"
        note = ("Stage-1 representable (oracle-read=%s). Substrate beats nearest-noun/frequency in "
                "aggregate but does NOT clear the genuine head-tracking bar on the subject-not-first "
                "subset: SNF sub=%s vs strongest-non-structural base=%s (delta=%s, need >=%.2f); "
                "structure-shuffle control SNF=%s (structure_used=%s, need sub-ss>=%.2f); conflict_win=%s "
                "bin4_ok=%s. It reduces to a POSITIONAL/COUNT heuristic, not learned head-tracking. "
                "Well-specified negative: a real CG here needs a structure-induction capability beyond "
                "fixed position/function-word weighting on a bound superposition."
                % (m_s1, snf_sub, snf_base, headtrack_delta, HEADTRACK_MARGIN, snf_ss, structure_used,
                   WRONGROLE_COLLAPSE_MIN, conflict_win, bin4_ok))

    msg = (f"{verdict} | Stage1 oracle-read(test)={m_s1} (floor {STAGE1_REPRESENTABLE_MIN}) | held-out "
           f"acc: substrate={m_sub} nearest={m_near} first={m_first} majority={m_major} bag={m_bag} "
           f"structshuffle={m_ss} clean-abl={m_clean} knnD={m_knnD} | CONFLICT sub={c_sub} maj={c_maj} "
           f"near={c_near} | SNF(head-track) sub={snf_sub} first={snf_first} maj={snf_maj} bag={snf_bag} "
           f"ss={snf_ss} delta={headtrack_delta} (margin {HEADTRACK_MARGIN}) | bin4={m_bin4} | "
           f"headtrack_win={headtrack_win} structure_used={structure_used} conflict_win={conflict_win} "
           f"arms_differ={arms_ok} weights_nondeg={weights_ok} baseline_in_band={baseline_in_band} | {note}")
    summ = {
        "stage1_oracle_read_test": m_s1, "stage1_pass": stage1_pass,
        "acc_substrate": m_sub, "acc_nearest": m_near, "acc_first": m_first, "acc_majority": m_major,
        "acc_bagcount": m_bag, "acc_structshuffle": m_ss, "acc_clean_ablation": m_clean,
        "acc_knn_relational_D": m_knnD,
        "conflict_substrate": c_sub, "conflict_majority": c_maj, "conflict_nearest": c_near,
        "snf_substrate": snf_sub, "snf_first": snf_first, "snf_majority": snf_maj, "snf_bagcount": snf_bag,
        "snf_structshuffle": snf_ss, "snf_base_strongest": snf_base,
        "headtrack_delta": headtrack_delta, "headtrack_win": headtrack_win,
        "conflict_win": conflict_win, "structure_used": structure_used,
        "bin4_substrate_acc": m_bin4, "arms_differ_all": arms_ok, "weights_nondeg_all": weights_ok,
        "baseline_in_band": baseline_in_band,
    }
    return verdict, msg, summ


# ==================================================================================================
# IO.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START agreement-attractor role-binding CG viability probe", flush=True)

    data = load_cache()
    linzen = data["linzen"]; nonce = data.get("nonce", [])
    print(f"[{ANCHOR_NAME}:{mode}] cache: {len(linzen)} Linzen + {len(nonce)} nonce items", flush=True)

    if mode == "smoke":
        seeds = SMOKE_SEEDS; tr_cap, te_cap = SMOKE_TRAIN_CAP, SMOKE_TEST_CAP
    else:
        seeds = FULL_SEEDS; tr_cap, te_cap = FULL_TRAIN_CAP, FULL_TEST_CAP

    rows = []
    for seed in seeds:
        r = run_seed(seed, tr_cap, te_cap, linzen, nonce, N_DIM)
        rows.append(r)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} S1oracle={r['stage1_oracle_read_acc_test']} "
              f"sub={r['acc_substrate']} near={r['acc_nearest']} first={r['acc_first']} "
              f"maj={r['acc_majority']} bag={r['acc_bagcount']} ss={r['acc_structshuffle']} | "
              f"SNF sub={r['snf_subset']['substrate']} first={r['snf_subset']['first_noun']} "
              f"maj={r['snf_subset']['majority']} bag={r['snf_subset']['bagcount']} "
              f"ss={r['snf_subset']['structshuffle']} | weights FW_PREP="
              f"{r['learned_weights_summary']['FW_PREP']} FW_START="
              f"{r['learned_weights_summary']['FW_START']} RS1={r['learned_weights_summary']['RS1_first']}",
              flush=True)

    verdict, msg, summ = build_verdict(rows)
    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": bool(len(rows) == len(seeds)),
        "N_DIM": N_DIM, "R_RANK": R_RANK, "n_fwc": N_FWC, "readout_steps": READOUT_STEPS, "l2": L2,
        "train_cap": tr_cap, "test_cap": te_cap,
        "bands": {"STAGE1_REPRESENTABLE_MIN": STAGE1_REPRESENTABLE_MIN, "HEADTRACK_MARGIN": HEADTRACK_MARGIN,
                  "CONFLICT_BEAT_MAJOR": CONFLICT_BEAT_MAJOR, "WRONGROLE_COLLAPSE_MIN": WRONGROLE_COLLAPSE_MIN,
                  "BIN4_ABOVE_CHANCE_MIN": BIN4_ABOVE_CHANCE_MIN},
        "summary_metrics": summ,
        "per_seed": rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "sequential_cpu_light_probe_wall_under_a_few_min_no_storage_no_composition",
        "crlb_n/a": ("real-text agreement head-tracking discrimination; the floor is HRR superposition "
                     "crosstalk, reported as Stage-1 oracle-head read accuracy, not an argmax-capacity CRLB"),
        "progress_logging": "print_flush_true",
        "deterministic_seeding": True,
        "no_store_write_no_push_no_atom_bank": True,
        "honest_scope": ("Beating nearest-noun is trivial here (nearest is the attractor -> below chance); "
                         "the HONEST discriminator is beating the FIRST-NOUN positional heuristic on the "
                         "subject-not-first subset via LEARNED function-word structure. A first-noun "
                         "collapse is MIDDLE (positional heuristic), not head-tracking. A HARD_PASS is a "
                         "GREEN-LIGHT-PENDING-VET (arm-D attributes representation vs learner), never a "
                         "self-declared CG. Real Linzen corpus; lexeme-free structural encoding."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ==================================================================================================
# Self-test (real substrate code paths at tiny scale + vectorized-FFT == hdlab.binding check).
# ==================================================================================================
def self_test():
    print("=== agreement-attractor role-binding CG viability self-test ===", flush=True)

    # (F.1) vectorized numpy-FFT bind/unbind == the REAL substrate primitive (hdlab.binding), tiny N.
    import torch
    from hdlab.binding import bind as hd_bind, unbind as hd_unbind
    nd = 64
    ra = _atom("t:role", nd); nb = _atom("t:num", nd)
    hb = hd_bind(torch.from_numpy(np.ascontiguousarray(ra)), torch.from_numpy(np.ascontiguousarray(nb))).numpy()
    vb = np.fft.ifft(_fft(ra) * _fft(nb)).real.astype(np.float32)
    assert np.max(np.abs(hb - vb)) < 1e-4, "vectorized bind diverges from hdlab.binding.bind"
    hu = hd_unbind(torch.from_numpy(np.ascontiguousarray(hb)), torch.from_numpy(np.ascontiguousarray(nb))).numpy()
    vu = np.fft.ifft(_fft(vb) * np.conj(_fft(nb))).real.astype(np.float32)
    assert np.max(np.abs(hu - vu)) < 1e-4, "vectorized unbind diverges from hdlab.binding.unbind"
    print("[self-test] vectorized FFT bind/unbind == hdlab.binding (real primitive)", flush=True)

    # cache present + fields
    data = load_cache()
    linzen = data["linzen"]; nonce = data.get("nonce", [])
    assert len(linzen) > 1000, "cache too small"
    for r in linzen[:50]:
        assert set(("ndiff", "label", "nums", "fwc", "subj_pos", "subj_word")).issubset(r)
        assert r["nums"][r["subj_pos"]] == r["label"], "subject number != label in cache"

    # tiny run: VALIDITY gates only (Stage-1 representability floor = a design prerequisite; arms differ;
    # baseline in band; runs). The MECHANISM outcome (does the substrate beat the baselines / does the
    # structure-shuffle collapse) is the CAN-FAIL hypothesis under test -- NOT asserted here (asserting
    # it would rig the probe toward a pass).
    r = run_seed(7, 400, 400, linzen, nonce, N_DIM)
    print("[self-test] seed7: S1oracle=%s sub=%s first=%s maj=%s bag=%s ss=%s | SNF sub=%s first=%s "
          "maj=%s ss=%s knnD=%s" % (
              r["stage1_oracle_read_acc_test"], r["acc_substrate"], r["acc_first"], r["acc_majority"],
              r["acc_bagcount"], r["acc_structshuffle"], r["snf_subset"]["substrate"],
              r["snf_subset"]["first_noun"], r["snf_subset"]["majority"], r["snf_subset"]["structshuffle"],
              r["acc_knn_relational_D"]), flush=True)
    assert r["arms_differ"], "arms bit-identical"
    assert r["weights_nondegenerate"], "readout weights degenerate"
    assert r["stage1_oracle_read_acc_test"] >= STAGE1_REPRESENTABLE_MIN, \
        "Stage-1 representability BELOW floor at seed7: %s < %s (design prerequisite; bump N_DIM)" % (
            r["stage1_oracle_read_acc_test"], STAGE1_REPRESENTABLE_MIN)
    assert 0.05 < r["acc_majority"] < 0.95, "majority baseline out of band: %s" % r["acc_majority"]
    print("[self-test PASS]", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
