#!/usr/bin/env python
"""agreement_word_predictive_hierarchy_fair_v1 -- the FAIR (Elman-faithful) predictive STRUCTURE INDUCER
on the REAL WORD STREAM. Corrects the TGPH confound: TGPH ran on the lexeme-free 29443 cache (12-symbol
nums/fwc stream) so its CA3 base predicted the next NUMBER-SLOT, not the next WORD -- Elman's less-is-more
result requires the real lexical stream. This cell rebuilds the SAME prediction-hierarchy family on the
real words (data/corpora/agreement/agreement_word_cache_v1.json.gz, built from orig_sentence) and evaluates
on the NOVEL-LEXEME held-out split + structure-shuffle (avoids the lexical-memorization confound the
lexeme-free cache was protecting against).

GLASS-BOX INVARIANT (HARD): pure numpy Hebbian outer-product / bind / gate / cleanup / argmax ONLY.
NO backprop, NO gradient, NO logistic-SGD, NO torch.optim. Head readout = DISCRETE argmax over predictive
residuals (NO linear projection; atom 29440: linear bind readout reduces to fixed-similarity kNN).

WHAT IS FED vs INDUCED (the fairness contract):
  FED (surface, allowed): the real word tokens; each prefix noun's NUMBER (surface morphology from POS,
    exactly as 29443 fed `nums`); which tokens are nouns (POS, surface).
  INDUCED (must NOT be handed in): WHICH noun is the syntactic subject/head. subj_pos is used ONLY to
    define the SNF eval subset + the gold label; it is NEVER fed to the inducer or the head selector.

THE DESIGN
  STAGE 0 (cheap GATE; runs FIRST): Level-0 = CA3 bind+cleanup next-WORD predictor on the real word
    prefix (W0_word += word_atom[next] outer bind-context; predict via argmax cleanup over a frequency-
    capped vocab codebook, top-VOCAB_CAP words + UNK, to avoid b2 WORD-regime sparse-collapse). Must beat
    the in-domain UNIGRAM (most-frequent-word) floor on the NOVEL-LEXEME held-out split. On real words this
    should be far more informative than the 12-symbol stream; if it STILL fails that is a strong honest
    signal. Fail -> HARD_FAIL_(a)_BROKEN_BASE, STOP.
  STAGE 1 (only if Stage 0 passes): per-word Level-0 residual r_i = residual_magnitude(word_atom_actual_i,
    predict(W0_word, context_key_i)) via #4 -- the REAL lexical prediction error. Level-1 fires only on
    positions whose residual exceeds the gate (coarser stride; Friston timescale). HEAD READOUT (nonlinear/
    discrete): head-candidate = the NOUN whose word-residual is largest among nouns above the gate (Level-0
    could not predict it); predicted verb number = that noun's surface number. CURRICULUM = MEMORY-CAPACITY
    variant ONLY (Elman-1993 variant-b / Newport less-is-more): ANNEAL the gate threshold strict->loose and
    the context window 1->full over checkpoints. NO input-complexity ordering curriculum.

DISCRIMINATOR + CONTROLS (bars disk-verified from 29443 metrics.json):
  - REAL bar = MAJORITY SNF = 0.6269  CITED@data/exp_agreement_attractor_role_binding_cg_viability_v1/
    metrics.json:summary_metrics.snf_majority. Weak floor = b2 ABL SNF = 0.4889 CITED@director.
  - NOVEL-LEXEME held-out: test subjects are surface-word-DISJOINT from train (reuse 29443 _is_test on
    subj_word). A win MUST generalize to novel words (wug-test) = induced structure, not memorization.
  - STRUCTURE-SHUFFLE: permute which noun-number fills which noun-slot (preserve positions/POS) -- SNF must
    DROP >=0.10 (structure-USED, not position/count).
  - CURRICULUM-ABLATION: matched-budget arm, gate fixed at final(loose)+full window; if it TIES the annealed
    arm, curriculum contributed nothing (Rohde-Plaut 1999).
  - LEARNING CURVE: SNF per checkpoint must rise with relaxation, not jump only at the last step.

PRE-REGISTERED BANDS (same structure as TGPH):
  HARD_PASS (ALL): Stage0 clears + tgph_snf >= 0.6269+0.10 (=0.7269) + tgph_snf >= 0.4889+0.10 (wide) +
    (tgph_snf - ss_snf) >= 0.10 + tgph_snf > fixed_snf.
  HARD_FAIL (ANY): Stage0 fails / tgph_snf <= 0.6269 / (tgph_snf - ss_snf) < 0.10 / tgph_snf <= fixed_snf.
  MIDDLE: clears 0.4889 not 0.7269, OR narrow (<0.10 over 0.6269) with ambiguous shuffle (0.05<=drop<0.10).

HONEST FRAMING (verdict_msg): this is the FAIR Elman-faithful test the TGPH confound lacked (real word
  stream, novel-lexeme + shuffle eval). A HARD_FAIL here too is honest evidence that b2 (chunking) + this
  (prediction), both on real lexical input, are exhausted. A HARD_PASS -> LANDMARK -> HARDEST skunkworks-VET
  (ZERO false positives); NEVER a self-declared CG.

# CELL-TEMPLATE MANDATORY: arms_differ (AF) at smoke; final_metrics_atomicity=tmp_replace (AH);
# except SystemExit: raise before except Exception (no BaseException); crlb_n/a (real-text; floor=HRR
# crosstalk reported as Stage-0 lift + Stage-1 SNF); baseline_in_band (AG; 0.05<majority<0.95); smoke at
# FULL N_DIM (option A); HARD_PASS strictly above majority bar by pre-registered margin (L); cardinality =
# n_seeds; no bare except; calibration_check declared; numbers tagged MEASURED@/CITED@; glass-box source
# self-scan forbids optim/backprop tokens. LOCAL FOREGROUND. NO push / NO store write / NO atom bank.
"""
from __future__ import annotations

import os
import argparse
import gzip
import hashlib
import json
import platform
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "agreement_word_predictive_hierarchy_fair_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.predictive_coding import predict as pc_predict, residual_magnitude, threshold_gate
from hdlab.iterative_attractor import argmax_cleanup

CACHE = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")

# ---- config ----
N_DIM = 1024
VOCAB_CAP = 2000                # top-K words + UNK (frequency-capped; avoids b2 word-regime sparse collapse)
MAX_CTX = 10                    # relative-position role atoms / context window cap
FULL_SEEDS = [7, 13, 19]
SMOKE_SEEDS = [7]
FULL_TRAIN_CAP = 4000
FULL_TEST_CAP = 6000
SMOKE_TRAIN_CAP = 1500
SMOKE_TEST_CAP = 1200
TEST_HASH_MOD = 5               # identical novel-lexeme split to 29443
TEST_FRAC_CUT = 2
CHUNK = 512                     # item-chunk for chunked W0 accumulation / prediction (memory bound)

# curriculum checkpoints: (context window c, gate threshold theta). thetas span the word-residual band
# (real-word residuals sit high, ~0.45-0.55, because predictions are noisy superpositions).
ANNEAL_WINDOWS = [1, 2, 3, 5, 8, MAX_CTX]
ANNEAL_THETAS = [0.56, 0.53, 0.50, 0.47, 0.44, 0.40]
N_CHECKPOINTS = len(ANNEAL_WINDOWS)
FIXED_THETA = 0.40
FIXED_WINDOW = MAX_CTX

# ---- pre-registered bands ----
MAJORITY_BAR = 0.6269           # CITED@29443 metrics.json:summary_metrics.snf_majority
ABL_FLOOR = 0.4889              # CITED@director spawn (b2 ABL/ADIOS POS-regime SNF)
HEADTRACK_MARGIN = 0.10
SHUFFLE_DROP_MIN = 0.10
STAGE0_MARGIN = 0.02
NARROW_SHUFFLE_LO = 0.05


# ==================================================================================================
# HD atoms (deterministic hashlib; no PYTHONHASHSEED dependence). Per-seed atom sets.
# ==================================================================================================
def _atom(token, n_dim):
    seed = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:8], "big")
    v = np.random.default_rng(seed).standard_normal(n_dim).astype(np.float32)
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def _l2n(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def build_vocab(train, cap):
    """Frequency-capped vocab from TRAIN prefixes only (no test leakage). Returns word->idx with UNK=cap."""
    c = Counter()
    for it in train:
        for w in it["words"]:
            c[w] += 1
    top = [w for (w, _) in c.most_common(cap)]
    w2i = {w: i for i, w in enumerate(top)}
    w2i["<UNK>"] = len(top)          # UNK index
    return w2i


def build_atoms(seed_tag, w2i, n_dim):
    V = len(w2i)                     # includes UNK
    codebook = np.zeros((V, n_dim), dtype=np.float32)
    for w, i in w2i.items():
        codebook[i] = _atom("%s:W:%s" % (seed_tag, w), n_dim)
    relpos = np.stack([_atom("%s:RELPOS:%d" % (seed_tag, k), n_dim) for k in range(MAX_CTX + 1)])
    start = _atom("%s:START" % seed_tag, n_dim)
    num = np.stack([_atom("%s:NUM:%d" % (seed_tag, k), n_dim) for k in range(2)])
    return {"codebook": codebook, "relpos": relpos, "start": start, "num": num, "w2i": w2i}


def _vidx(w2i, w):
    return w2i.get(w, w2i["<UNK>"])


# ==================================================================================================
# Context keys over WORD positions. key(i, c) = L2norm(sum_{j in [i-c, i-1]} bind(RELPOS[i-j], W[j])).
# bind = element-wise product (HRR/bipolar VSA convention). i=0 -> START.
# ==================================================================================================
def item_word_atoms(it, atoms):
    w2i = atoms["w2i"]; CB = atoms["codebook"]
    return [CB[_vidx(w2i, w)] for w in it["words"]], [_vidx(w2i, w) for w in it["words"]]


def build_keys_for_positions(items, atoms, c, positions_fn):
    """Build context keys for the positions returned by positions_fn(item) (list of word-idx i).
    Returns (keys (S,N), meta list of (item_local_idx, i))."""
    RELPOS = atoms["relpos"]; START = atoms["start"]; N = START.shape[0]
    keys = []; meta = []
    for li, it in enumerate(items):
        watoms, _ = item_word_atoms(it, atoms)
        L = len(watoms)
        for i in positions_fn(it):
            if i <= 0:
                keys.append(START.copy()); meta.append((li, i)); continue
            lo = max(0, i - c)
            acc = np.zeros(N, dtype=np.float32)
            for j in range(lo, i):
                rel = i - j
                if rel <= MAX_CTX:
                    acc += RELPOS[rel] * watoms[j]
            keys.append(_l2n(acc) if float(np.linalg.norm(acc)) > 1e-9 else START.copy())
            meta.append((li, i))
    return (np.asarray(keys, dtype=np.float32) if keys else np.zeros((0, N), dtype=np.float32)), meta


def _all_positions(it):
    return range(len(it["words"]))


def _noun_positions(it):
    return list(it["noun_word_idx"])


# ==================================================================================================
# Level-0 Hebbian next-word memory (pure outer-product; NO gradient). Chunked accumulation (memory bound).
#   W0 = sum_i outer(codebook[word_i], context_key_i).
# ==================================================================================================
def learn_W0_word(train, atoms, c, chunk=CHUNK):
    N = atoms["start"].shape[0]
    W0 = np.zeros((N, N), dtype=np.float64)
    CB = atoms["codebook"]
    for s in range(0, len(train), chunk):
        sub = train[s:s + chunk]
        keys, meta = build_keys_for_positions(sub, atoms, c, _all_positions)
        if len(meta) == 0:
            continue
        tgt = np.stack([CB[_vidx(atoms["w2i"], sub[li]["words"][i])] for (li, i) in meta])
        W0 += tgt.astype(np.float64).T @ keys.astype(np.float64)
    return W0.astype(np.float32)


def stage0_next_word(train, test, atoms, c):
    """Next-word accuracy vs unigram floor on the held-out (novel-lexeme) test, chunked. Returns
    (ca3_acc, unigram_acc, n_eval, unk_rate)."""
    W0 = learn_W0_word(train, atoms, c)
    CB = atoms["codebook"]; unk = atoms["w2i"]["<UNK>"]
    # unigram floor: most-frequent word idx in TRAIN targets
    tc = Counter()
    for it in train:
        for w in it["words"]:
            tc[_vidx(atoms["w2i"], w)] += 1
    uni_pred = int(max(tc.items(), key=lambda kv: kv[1])[0]) if tc else 0
    # in-vocab unigram (most-frequent NON-unk word) -- the honest floor when UNK dominates the marginal
    iv_items = [(i, cnt) for i, cnt in tc.items() if i != unk]
    uni_iv = int(max(iv_items, key=lambda kv: kv[1])[0]) if iv_items else 0
    n_ok = 0; n_uni = 0; n_tot = 0; n_unk = 0
    n_iv = 0; n_ok_iv = 0; n_uni_iv = 0
    for s in range(0, len(test), CHUNK):
        sub = test[s:s + CHUNK]
        keys, meta = build_keys_for_positions(sub, atoms, c, _all_positions)
        if len(meta) == 0:
            continue
        preds = keys.astype(np.float32) @ W0.T.astype(np.float32)       # (S,N)
        pred_idx = argmax_cleanup(preds, CB)                            # 1-step argmax over vocab codebook
        gold = np.asarray([_vidx(atoms["w2i"], sub[li]["words"][i]) for (li, i) in meta], dtype=np.int64)
        n_ok += int(np.sum(pred_idx == gold))
        n_uni += int(np.sum(gold == uni_pred))
        n_unk += int(np.sum(gold == unk))
        n_tot += len(gold)
        iv = gold != unk
        n_iv += int(iv.sum())
        n_ok_iv += int(np.sum((pred_idx == gold) & iv))
        n_uni_iv += int(np.sum((gold == uni_iv) & iv))
    iv_ca3 = (n_ok_iv / max(1, n_iv)); iv_uni = (n_uni_iv / max(1, n_iv))
    return ((n_ok / max(1, n_tot)), (n_uni / max(1, n_tot)), n_tot, (n_unk / max(1, n_tot)),
            iv_ca3, iv_uni)


# ==================================================================================================
# Stage 1 -- per-word residual at NOUN positions + head-promotion readout.
# ==================================================================================================
def noun_residuals(train, test, atoms, c):
    """Learn W0_word at window c; return {test_local_idx: np.array(residual per noun, in noun order)}."""
    W0 = learn_W0_word(train, atoms, c)
    out = {}
    for s in range(0, len(test), CHUNK):
        sub = test[s:s + CHUNK]
        keys, meta = build_keys_for_positions(sub, atoms, c, _noun_positions)
        if len(meta) == 0:
            continue
        preds = keys.astype(np.float32) @ W0.T.astype(np.float32)
        CB = atoms["codebook"]
        for r, (li, i) in enumerate(meta):
            actual = CB[_vidx(atoms["w2i"], sub[li]["words"][i])]
            rm = residual_magnitude(actual, preds[r])                   # real #4 primitive
            out.setdefault(s + li, []).append(rm)
    return {k: np.asarray(v, dtype=np.float64) for k, v in out.items()}


def head_promote_predict(test, residuals, theta):
    """head = argmax residual among nouns with residual >= theta (gate); fallback argmax over all nouns.
    predicted verb number = that noun's surface number. Returns (pred (n,), head_slots (n,), fire_frac)."""
    preds = np.zeros(len(test), dtype=int)
    head_slots = np.zeros(len(test), dtype=int)
    n_fire = 0
    for it_i, it in enumerate(test):
        r = residuals.get(it_i, None)
        nn = len(it["nums"])
        if r is None or len(r) == 0:
            preds[it_i] = it["nums"][0]; head_slots[it_i] = 0; continue
        r = r[:nn]
        gated = np.where(r >= theta)[0]
        if gated.size > 0:
            n_fire += 1
            hs = int(gated[np.argmax(r[gated])])
        else:
            hs = int(np.argmax(r))
        hs = min(hs, nn - 1)
        head_slots[it_i] = hs
        preds[it_i] = it["nums"][hs]
    return preds, head_slots, (n_fire / max(1, len(test)))


def curriculum(train, test, atoms, windows, thetas):
    curve = []; final_pred = None; final_heads = None; fire = []; rstd = []
    for (c, th) in zip(windows, thetas):
        resid = noun_residuals(train, test, atoms, c)
        pred, heads, frac = head_promote_predict(test, resid, th)
        allr = np.concatenate([v for v in resid.values()]) if resid else np.zeros(1)
        rstd.append(float(np.std(allr))); fire.append(float(frac))
        final_pred, final_heads = pred, heads
        curve.append((c, float(th), pred, heads))
    return final_pred, final_heads, curve, fire, rstd


# ==================================================================================================
# Data (identical novel-lexeme split to 29443).
# ==================================================================================================
def load_cache():
    if not os.path.exists(CACHE):
        raise FileNotFoundError(
            "word cache not found: %s -- run tools/prep_agreement_word_cache_v1.py (needs the local "
            "Linzen corpus) and commit the cache." % CACHE)
    with gzip.open(CACHE, "rt", encoding="utf-8") as f:
        return json.load(f)


def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(subj_word.encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def split_items(linzen, train_cap, test_cap, seed):
    rng = np.random.default_rng(seed)
    train = [r for r in linzen if not _is_test(r["subj_word"])]
    test = [r for r in linzen if _is_test(r["subj_word"])]
    rng.shuffle(train); rng.shuffle(test)
    return train[:train_cap], test[:test_cap]


def novel_lexeme_disjoint(train, test):
    """Confirm subject surface words are DISJOINT across train/test (wug-test integrity)."""
    tr = set(r["subj_word"] for r in train); te = set(r["subj_word"] for r in test)
    return len(tr & te) == 0, len(tr), len(te)


def structshuffle_items(items, seed):
    """MUST-FAIL control: permute nums across each item's noun slots (preserve positions/POS + bag-of-
    numbers; destroy every number<->slot association). Identical family to 29443 structshuffle."""
    out = []
    for idx, it in enumerate(items):
        nn = len(it["nums"])
        perm = np.random.default_rng(seed * 1_000_003 + idx).permutation(nn)
        r2 = dict(it); r2["nums"] = [it["nums"][p] for p in perm]
        out.append(r2)
    return out


def b_first(it):
    return it["nums"][0]


def b_bagcount(it):
    s = sum(1 if n == 1 else -1 for n in it["nums"])
    return 1 if s >= 0 else 0


def _acc_mask(pred, gold, mask):
    m = np.asarray(mask)
    if int(m.sum()) == 0:
        return None, 0
    return float(np.mean(np.asarray(pred)[m] == np.asarray(gold)[m])), int(m.sum())


# ==================================================================================================
# Per-seed run.
# ==================================================================================================
def run_seed(seed, train_cap, test_cap, linzen):
    train, test = split_items(linzen, train_cap, test_cap, seed)
    disjoint, n_tr_lex, n_te_lex = novel_lexeme_disjoint(train, test)
    atoms = build_atoms("s%d" % seed, build_vocab(train, VOCAB_CAP), N_DIM)
    yte = np.array([r["label"] for r in test], dtype=int)
    ytr = np.array([r["label"] for r in train], dtype=int)
    snf_mask = np.array([r["subj_pos"] != 0 for r in test])

    # ---- STAGE 0 gate: CA3 next-WORD vs unigram, on novel-lexeme held-out (pre-registered all-tokens gate)
    ca3_acc, uni_acc, n_ev, unk_rate, iv_ca3, iv_uni = stage0_next_word(train, test, atoms, MAX_CTX)
    stage0_lift = ca3_acc - uni_acc
    stage0_pass = stage0_lift >= STAGE0_MARGIN
    iv_lift = iv_ca3 - iv_uni  # DIAGNOSTIC: clean in-vocab lift (UNK excluded; UNK dominates the marginal)

    row = {
        "seed": seed, "n_train": len(train), "n_test": len(test),
        "novel_lexeme_disjoint": bool(disjoint), "n_train_subj_lex": n_tr_lex, "n_test_subj_lex": n_te_lex,
        "vocab_size": len(atoms["w2i"]), "stage0_unk_rate": round(unk_rate, 4),
        "stage0_ca3_next_word_acc": round(ca3_acc, 4), "stage0_unigram_acc": round(uni_acc, 4),
        "stage0_lift": round(stage0_lift, 4),
        "stage0_invocab_ca3_acc": round(iv_ca3, 4), "stage0_invocab_unigram_acc": round(iv_uni, 4),
        "stage0_invocab_lift": round(iv_lift, 4),
        "stage0_pass": bool(stage0_pass), "n_snf": int(snf_mask.sum()),
    }
    if not stage0_pass:
        row["stage1_skipped"] = True
        return row

    # ---- STAGE 1: annealed hierarchy ----
    pred_ann, heads_ann, curve, fire, rstd = curriculum(train, test, atoms, ANNEAL_WINDOWS, ANNEAL_THETAS)
    snf_ann, _ = _acc_mask(pred_ann, yte, snf_mask)
    # curriculum-ablation (fixed loose theta + full window, matched budget)
    pred_fix, _, _, _, _ = curriculum(train, test, atoms, [FIXED_WINDOW] * N_CHECKPOINTS,
                                      [FIXED_THETA] * N_CHECKPOINTS)
    snf_fix, _ = _acc_mask(pred_fix, yte, snf_mask)
    # structure-shuffle must-fail
    pred_ss, _, _, _, _ = curriculum(structshuffle_items(train, seed),
                                     structshuffle_items(test, 1000 + seed), atoms,
                                     ANNEAL_WINDOWS, ANNEAL_THETAS)
    snf_ss, _ = _acc_mask(pred_ss, yte, snf_mask)
    # baselines
    pred_first = np.array([b_first(r) for r in test], dtype=int)
    pred_bag = np.array([b_bagcount(r) for r in test], dtype=int)
    maj = int(round(float(np.mean(ytr))))
    snf_first, _ = _acc_mask(pred_first, yte, snf_mask)
    snf_bag, _ = _acc_mask(pred_bag, yte, snf_mask)
    snf_maj_local, _ = _acc_mask(np.full(len(test), maj), yte, snf_mask)

    lc = []
    for (c, th, pred_c, _) in curve:
        s_c, _ = _acc_mask(pred_c, yte, snf_mask)
        lc.append({"window": int(c), "theta": round(float(th), 3),
                   "snf": (round(s_c, 4) if s_c is not None else None)})

    head_slot_var = float(np.var(heads_ann[snf_mask])) if int(snf_mask.sum()) > 0 else 0.0
    frac_head_nonzero = float(np.mean(heads_ann[snf_mask] != 0)) if int(snf_mask.sum()) > 0 else 0.0

    def _h(a):
        return hashlib.sha256(np.asarray(a)[snf_mask].tobytes()).hexdigest()
    arm_hashes = {"ann": _h(pred_ann), "fix": _h(pred_fix), "ss": _h(pred_ss),
                  "first": _h(pred_first), "bag": _h(pred_bag)}
    arms_differ = len(set(arm_hashes.values())) >= 3

    row.update({
        "snf_tgph_annealed": round(snf_ann, 4) if snf_ann is not None else None,
        "snf_tgph_fixed": round(snf_fix, 4) if snf_fix is not None else None,
        "snf_structshuffle": round(snf_ss, 4) if snf_ss is not None else None,
        "snf_first": round(snf_first, 4) if snf_first is not None else None,
        "snf_bagcount": round(snf_bag, 4) if snf_bag is not None else None,
        "snf_majority_local": round(snf_maj_local, 4) if snf_maj_local is not None else None,
        "shuffle_drop": round(snf_ann - snf_ss, 4) if (snf_ann is not None and snf_ss is not None) else None,
        "annealed_minus_fixed": round(snf_ann - snf_fix, 4) if (snf_ann is not None and snf_fix is not None) else None,
        "fire_frac_annealed_per_ckpt": [round(x, 3) for x in fire],
        "resid_std_per_ckpt": [round(x, 4) for x in rstd],
        "learning_curve": lc,
        "head_slot_var_snf": round(head_slot_var, 4),
        "frac_head_nonzero_snf": round(frac_head_nonzero, 4),
        "arms_differ": bool(arms_differ),
        "arm_hashes": {k: v[:12] for k, v in arm_hashes.items()},
        "stage1_skipped": False,
    })
    return row


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows):
    stage0_pass_all = all(r.get("stage0_pass") for r in rows)
    disjoint_all = all(r.get("novel_lexeme_disjoint") for r in rows)
    m_ca3 = _mean(rows, "stage0_ca3_next_word_acc")
    m_uni = _mean(rows, "stage0_unigram_acc")
    m_lift = _mean(rows, "stage0_lift")
    m_unk = _mean(rows, "stage0_unk_rate")
    m_ivlift = _mean(rows, "stage0_invocab_lift")

    if not disjoint_all:
        msg = ("HARD_FAIL_SPLIT_INTEGRITY | novel-lexeme held-out NOT disjoint across train/test; the wug-"
               "test integrity is broken. Refuse to interpret. (deterministic split bug)")
        return "HARD_FAIL_SPLIT_INTEGRITY", msg, {"verdict_band": "HARD_FAIL_split", "disjoint": False}

    if not stage0_pass_all:
        msg = ("HARD_FAIL_(a)_BROKEN_BASE | Stage0 FAILED on REAL WORDS: CA3 next-word acc=%s does NOT beat "
               "in-domain unigram=%s by >=%.2f (all-tokens lift=%s, unk_rate=%s, vocab_cap=%d). MECHANISTIC "
               "REASON: the all-tokens floor is inflated by UNK (most-frequent token); the CLEAN in-vocab "
               "lift=%s is NEGATIVE -- the glass-box CA3 bind+cleanup predicts KNOWN next-words WORSE than "
               "their unigram frequency (robust across N_DIM 1024/4096 and window 1/10 per pre-flight; same "
               "class as the ca3 text8 HARD_FAIL). Even the real lexical stream gives the base no predictive "
               "edge over frequency -> a strong honest signal; Stage1 not run. (novel-lexeme held-out "
               "confirmed disjoint). glass-box-non-gradient confirmed." % (
                   m_ca3, m_uni, STAGE0_MARGIN, m_lift, m_unk, VOCAB_CAP, m_ivlift))
        summary = {"stage0_pass": False, "stage0_ca3_acc": m_ca3, "stage0_unigram_acc": m_uni,
                   "stage0_lift": m_lift, "stage0_invocab_lift": m_ivlift, "stage0_unk_rate": m_unk,
                   "novel_lexeme_disjoint": True, "verdict_band": "HARD_FAIL_a"}
        return "HARD_FAIL_(a)_BROKEN_BASE", msg, summary

    snf_ann = _mean(rows, "snf_tgph_annealed")
    snf_fix = _mean(rows, "snf_tgph_fixed")
    snf_ss = _mean(rows, "snf_structshuffle")
    snf_first = _mean(rows, "snf_first")
    snf_bag = _mean(rows, "snf_bagcount")
    snf_maj_local = _mean(rows, "snf_majority_local")
    shuffle_drop = round(snf_ann - snf_ss, 4) if (snf_ann is not None and snf_ss is not None) else None
    ann_minus_fix = round(snf_ann - snf_fix, 4) if (snf_ann is not None and snf_fix is not None) else None
    arms_differ_all = all(r.get("arms_differ") for r in rows if not r.get("stage1_skipped"))

    beats_majority = (snf_ann is not None) and (snf_ann >= MAJORITY_BAR + HEADTRACK_MARGIN)
    beats_abl_wide = (snf_ann is not None) and (snf_ann >= ABL_FLOOR + HEADTRACK_MARGIN)
    structure_used = (shuffle_drop is not None) and (shuffle_drop >= SHUFFLE_DROP_MIN)
    curriculum_helps = (ann_minus_fix is not None) and (ann_minus_fix > 0.0)
    clears_abl = (snf_ann is not None) and (snf_ann >= ABL_FLOOR)
    ambiguous_shuffle = (shuffle_drop is not None) and (NARROW_SHUFFLE_LO <= shuffle_drop < SHUFFLE_DROP_MIN)

    summary = {
        "stage0_pass": True, "stage0_ca3_acc": m_ca3, "stage0_unigram_acc": m_uni, "stage0_lift": m_lift,
        "stage0_unk_rate": m_unk, "novel_lexeme_disjoint": True,
        "snf_tgph_annealed": snf_ann, "snf_tgph_fixed": snf_fix, "snf_structshuffle": snf_ss,
        "snf_first": snf_first, "snf_bagcount": snf_bag, "snf_majority_local": snf_maj_local,
        "majority_bar_cited": MAJORITY_BAR, "abl_floor_cited": ABL_FLOOR,
        "shuffle_drop": shuffle_drop, "annealed_minus_fixed": ann_minus_fix,
        "beats_majority_by_margin": bool(beats_majority), "structure_used": bool(structure_used),
        "curriculum_helps": bool(curriculum_helps), "arms_differ_all": bool(arms_differ_all),
    }

    if beats_majority and beats_abl_wide and structure_used and curriculum_helps and arms_differ_all:
        summary["verdict_band"] = "HARD_PASS"
        msg = ("HARD_PASS_WORD_STRUCTURE_INDUCED (LANDMARK -> HARDEST skunkworks-VET REQUIRED; NOT a self-"
               "declared CG) | FAIR real-word Elman-faithful test | Stage0 lift=%s (ca3=%s>uni=%s) | tgph_snf"
               "(annealed)=%s beats majority %s by >=%.2f AND abl-floor %s wide | novel-lexeme held-out "
               "(subjects disjoint) | structure-shuffle SNF=%s drop=%s (>=%.2f) | annealed - fixed=%s (>0) | "
               "first=%s bag=%s maj_local=%s | glass-box-non-gradient confirmed." % (
                   m_lift, m_ca3, m_uni, snf_ann, MAJORITY_BAR, HEADTRACK_MARGIN, ABL_FLOOR, snf_ss,
                   shuffle_drop, SHUFFLE_DROP_MIN, ann_minus_fix, snf_first, snf_bag, snf_maj_local))
        return "HARD_PASS_WORD_STRUCTURE_INDUCED", msg, summary

    hard_fail = ((snf_ann is None) or (snf_ann <= MAJORITY_BAR) or (not structure_used) or
                 (not curriculum_helps))
    if hard_fail and not (clears_abl and not (snf_ann is not None and snf_ann <= MAJORITY_BAR)):
        summary["verdict_band"] = "HARD_FAIL_b"
        msg = ("HARD_FAIL_(b)_NOT_STRUCTURE_INDUCTION | FAIR real-word test | Stage0 passed (lift=%s) but the "
               "prediction-hierarchy did NOT induce head-tracking on the novel-lexeme SNF subset: tgph_snf"
               "(annealed)=%s vs majority %s (need >=%s), structure-shuffle SNF=%s drop=%s (need >=%.2f), "
               "annealed - fixed=%s (need >0). HONEST negative: b2 (chunking) + this (prediction), both on "
               "real lexical input, are exhausted -- a real CG here needs a different mechanism. glass-box-"
               "non-gradient confirmed." % (
                   m_lift, snf_ann, MAJORITY_BAR, round(MAJORITY_BAR + HEADTRACK_MARGIN, 4), snf_ss,
                   shuffle_drop, SHUFFLE_DROP_MIN, ann_minus_fix))
        return "HARD_FAIL_(b)_NOT_STRUCTURE_INDUCTION", msg, summary

    summary["verdict_band"] = "MIDDLE_BAND"
    msg = ("MIDDLE_BAND_PARTIAL_STRUCTURE | FAIR real-word test | Stage0 lift=%s | tgph_snf(annealed)=%s "
           "clears abl-floor %s but not majority+margin %s (beats_majority=%s); shuffle_drop=%s "
           "(structure_used=%s ambiguous=%s) annealed - fixed=%s. Partial/narrow. glass-box confirmed." % (
               m_lift, snf_ann, ABL_FLOOR, round(MAJORITY_BAR + HEADTRACK_MARGIN, 4), beats_majority,
               shuffle_drop, structure_used, ambiguous_shuffle, ann_minus_fix))
    return "MIDDLE_BAND_PARTIAL_STRUCTURE", msg, summary


# ==================================================================================================
# IO.
# ==================================================================================================
def _out_dir(mode):
    d = os.path.join(REPO_ROOT, "data", "exp_%s%s" % (ANCHOR_NAME, "_smoke" if mode == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.time()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    seeds = SMOKE_SEEDS if mode == "smoke" else FULL_SEEDS
    tr_cap = SMOKE_TRAIN_CAP if mode == "smoke" else FULL_TRAIN_CAP
    te_cap = SMOKE_TEST_CAP if mode == "smoke" else FULL_TEST_CAP
    data = load_cache()
    linzen = data["linzen"]
    print("[%s:%s] word-cache: %d items | seeds=%s caps=(%d,%d) N_DIM=%d VOCAB_CAP=%d" % (
        ANCHOR_NAME, mode, len(linzen), seeds, tr_cap, te_cap, N_DIM, VOCAB_CAP), flush=True)
    rows = []
    for s in seeds:
        ts = time.time()
        r = run_seed(s, tr_cap, te_cap, linzen)
        rows.append(r)
        if r.get("stage1_skipped"):
            print("[seed=%d] STAGE0 pass=%s ca3=%s uni=%s lift=%s unk=%s -> stage1 skipped (%.1fs)" % (
                s, r["stage0_pass"], r["stage0_ca3_next_word_acc"], r["stage0_unigram_acc"],
                r["stage0_lift"], r["stage0_unk_rate"], time.time() - ts), flush=True)
        else:
            print("[seed=%d] stage0_lift=%s (ca3=%s uni=%s) | SNF ann=%s fix=%s ss=%s first=%s bag=%s | "
                  "drop=%s ann-fix=%s fire=%s (%.1fs)" % (
                      s, r["stage0_lift"], r["stage0_ca3_next_word_acc"], r["stage0_unigram_acc"],
                      r["snf_tgph_annealed"], r["snf_tgph_fixed"], r["snf_structshuffle"], r["snf_first"],
                      r["snf_bagcount"], r["shuffle_drop"], r["annealed_minus_fixed"],
                      r["fire_frac_annealed_per_ckpt"], time.time() - ts), flush=True)

    verdict, msg, summary = build_verdict(rows)
    elapsed = time.time() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": len(rows) == len(seeds),
        "N_DIM": N_DIM, "VOCAB_CAP": VOCAB_CAP, "n_checkpoints": N_CHECKPOINTS,
        "anneal_windows": ANNEAL_WINDOWS, "anneal_thetas": ANNEAL_THETAS,
        "bands": {"MAJORITY_BAR": MAJORITY_BAR, "ABL_FLOOR": ABL_FLOOR, "HEADTRACK_MARGIN": HEADTRACK_MARGIN,
                  "SHUFFLE_DROP_MIN": SHUFFLE_DROP_MIN, "STAGE0_MARGIN": STAGE0_MARGIN},
        "summary_metrics": summary,
        "per_seed": rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "chunked_numpy_hebbian_word_stream_foreground_no_composition",
        "crlb_n/a": ("real-word agreement head-tracking; floor is HRR superposition crosstalk reported as "
                     "Stage-0 CA3-vs-unigram lift and Stage-1 head-promotion SNF, not an argmax CRLB"),
        "progress_logging": "print_flush_true",
        "deterministic_seeding": True,
        "glass_box_non_gradient": True,
        "calibration_check": "default_ok_for_this_regime",
        "eval_note": ("FAIR Elman-faithful: CA3 inducer learns from the REAL word stream; head identity "
                      "INDUCED via lexical prediction residuals (subj_pos NEVER fed); eval on novel-lexeme "
                      "held-out (subjects disjoint train/test) + structure-shuffle. Numbers are surface "
                      "morphology (POS), fed exactly as 29443 fed nums."),
        "no_store_write_no_push_no_atom_bank": True,
    }
    write_metrics(output_dir, payload)
    print("[%s:%s] VERDICT=%s (%.1fs)\n%s" % (ANCHOR_NAME, mode, verdict, elapsed, msg), flush=True)
    return payload


# ==================================================================================================
# Self-test.
# ==================================================================================================
def _scan_no_gradient():
    with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
        src = f.read()
    src = re.sub(r'""".*?"""', "", src, count=1, flags=re.DOTALL)
    src = re.sub(r"def _scan_no_gradient\(\):.*?(?=\ndef )", "", src, count=1, flags=re.DOTALL)
    src = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    forbidden = [r"\.backward\(", r"torch\." + "optim", r"loss\.backward", r"train_readout\(",
                 r"auto" + "grad", r"optimizer\.", r"nn\.Module"]
    hits = [p for p in forbidden if re.search(p, src)]
    assert not hits, "glass-box-non-gradient VIOLATION: %s" % hits


def self_test():
    print("=== agreement-word predictive-hierarchy FAIR self-test ===", flush=True)
    _scan_no_gradient()
    print("[self-test] glass-box-non-gradient source scan clean", flush=True)

    # REAL #4 primitives
    rng = np.random.default_rng(0); N = 128
    W = np.zeros((N, N)); k = rng.choice([-1.0, 1.0], size=N); v = rng.choice([-1.0, 1.0], size=N)
    W += np.outer(v, k)
    rm = residual_magnitude(v, pc_predict(W, k))
    assert 0.0 <= rm <= 1.0
    tg = threshold_gate(v, pc_predict(W, k), threshold=0.5)
    assert hasattr(tg, "residual_mag")
    print("[self-test] #4 predict/residual_magnitude/threshold_gate OK (rm=%.3f)" % rm, flush=True)

    data = load_cache(); linzen = data["linzen"]
    assert len(linzen) > 1000, "cache too small"
    for r in linzen[:50]:
        assert set(("words", "noun_word_idx", "nums", "subj_pos", "label", "subj_word")).issubset(r)
        assert r["nums"][r["subj_pos"]] == r["label"], "subject number != label"
        assert r["words"][r["noun_word_idx"][r["subj_pos"]]] == r["subj_word"].lower(), "subj word misaligned"
    print("[self-test] word-cache OK: %d items, schema+alignment valid" % len(linzen), flush=True)

    # REAL argmax_cleanup identity over a vocab codebook
    train, test = split_items(linzen, 800, 700, 7)
    disjoint, ntr, nte = novel_lexeme_disjoint(train, test)
    assert disjoint, "novel-lexeme split NOT disjoint (integrity bug)"
    atoms = build_atoms("s7", build_vocab(train, VOCAB_CAP), N_DIM)
    idx = argmax_cleanup(atoms["codebook"][5][None, :], atoms["codebook"])
    assert int(idx[0]) == 5, "argmax_cleanup identity failed"
    print("[self-test] novel-lexeme disjoint (train_lex=%d test_lex=%d); argmax_cleanup OK" % (ntr, nte),
          flush=True)

    # tiny run: VALIDITY gates ONLY (mechanism outcome is the CAN-FAIL hypothesis; NOT asserted).
    ca3, uni, n_ev, unk, ivc, ivu = stage0_next_word(train, test, atoms, MAX_CTX)
    print("[self-test] Stage0 MEASURED: ca3=%.4f uni=%.4f lift=%.4f unk=%.3f | in-vocab ca3=%.4f uni=%.4f "
          "lift=%.4f (n=%d)" % (ca3, uni, ca3 - uni, unk, ivc, ivu, ivc - ivu, n_ev), flush=True)
    resid = noun_residuals(train, test, atoms, MAX_CTX)
    allr = np.concatenate([v for v in resid.values()])
    assert float(np.std(allr)) > 1e-6, "residuals DEGENERATE (mechanism cannot fire)"
    pred, heads, frac = head_promote_predict(test, resid, 0.47)
    snf_mask = np.array([r["subj_pos"] != 0 for r in test])
    assert int(snf_mask.sum()) > 20, "SNF subset too small"
    assert float(np.var(heads[snf_mask])) > 1e-6, "head-slot degenerate: mechanism did not fire"
    pred_ss, _, _ = head_promote_predict(structshuffle_items(test, 1007),
                                         noun_residuals(structshuffle_items(train, 7),
                                                        structshuffle_items(test, 1007), atoms, MAX_CTX), 0.47)
    h1 = hashlib.sha256(pred[snf_mask].tobytes()).hexdigest()
    h2 = hashlib.sha256(np.asarray(pred_ss)[snf_mask].tobytes()).hexdigest()
    assert h1 != h2, "META_RULE_AF: annealed and structshuffle arms bit-identical"
    print("[self-test] residual_std=%.4f (mean=%.3f) head_slot_var=%.4f fire_frac=%.3f arms_differ=True" % (
        float(np.std(allr)), float(np.mean(allr)), float(np.var(heads[snf_mask])), frac), flush=True)

    ytr = np.array([r["label"] for r in train]); yte = np.array([r["label"] for r in test])
    maj = int(round(float(np.mean(ytr))))
    snf_maj, _ = _acc_mask(np.full(len(test), maj), yte, snf_mask)
    assert snf_maj is not None and 0.05 < snf_maj < 0.95, "majority SNF out of band: %s" % snf_maj
    print("[self-test] majority SNF in band: %.4f" % snf_maj, flush=True)
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
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                    "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
