#!/usr/bin/env python
"""agreement_word_prediction_rep_number_probe_v1 -- the LITERAL Elman test for the glass-box structure-
induction arc: does the PREDICTION-INDUCED REPRESENTATION itself encode the subject's agreement number?

CONTEXT (disk-verified). The sparse-CA3 predictor (agreement_word_sparse_ca3_predictive_hierarchy_v1)
CLEARED Stage-0 (beats frequency at next-word; in-vocab lift +0.028 MEASURED). But the head-promotion
residual READOUT HARD_FAILed: the subject/head signal was NOT in the prediction ERROR. b2 (chunking),
dense-prediction, and sparse-prediction-RESIDUAL all HARD_FAILed. This cell tests the ONE untested Elman-
faithful variant: structure in the REPRESENTATION, not the residual. Elman (1991) SRN: a next-word predictor
develops an internal state that ENCODES the subject's grammatical number (recoverable by an inspectable
probe, generalizing to novel lexemes). Atom 29443 probed a RAW structural encoding and it FAILED (below
majority) -- so the RAW-BIND baseline here is EXPECTED to fail. THE QUESTION: does PREDICTION-SHAPING make
the representation encode the head where the raw encoding did not?

THE REPRESENTATION (reuse the sparse-CA3 recipe VERBATIM: 29444 soft-shard E=4/f=0.20/center + CA3 bind/
cleanup). Run the sparse-CA3 predictor over each sentence prefix (the cache `words` = the Linzen prefix
ending right before the target verb, MEASURED@cache-inspect -- so the verb-position context code IS the
predictive state). At the verb position build the sparse key of the prefix (windowed context code), then:
  RAW-BIND rep      = coder.encode(verb_key)          (the un-prediction-shaped sparse encoding of the prefix)
  PREDICTION rep    = M * coder.encode(verb_key)       (M = soft-shard next-word store; q = the retrieved
                                                        prediction superposition = what the predictor BUILDS
                                                        while predicting the upcoming verb)
Both reps L2-normalized before probing so the ONLY variable is whether the prediction store M was applied.

WHY THE PROBE CAN DISCRIMINATE (analytic, honest). q = M ⊙ key is key rescaled elementwise by M, so a
LINEAR probe on q is linearly equivalent to a (re-weighted) linear probe on key -- the linear probe CANNOT
separate pred from raw (atom 29440: a linear readout on a bind reduces to fixed-similarity; a NEGATIVE
linear result is consistent with only-non-linearly-encoded). A PROTOTYPE / nearest-class (cosine) readout is
NOT invariant to the M-rescaling, so it CAN see prediction-shaping. We report BOTH and take the winner; the
prototype partially guards the linear-collapse caveat. Both probes are CLOSED-FORM measurement readouts
(prototype = mean+cosine; ridge = (X^T X + lam I)^-1 X^T y via np.linalg.solve) -- NO gradient/backprop/optim.

THE DISCRIMINATOR (makes it airtight). For the winning probe, compare pred-rep SNF vs the SAME probe on the
RAW-BIND rep. A win must be attributable to PREDICTION-SHAPING (pred beats raw by a clear margin), NOT the
fixed encoding. STRUCTURE-SHUFFLE control = WORD-ORDER shuffle (permute word positions within each sentence:
preserves the bag of words + bag of numbers, destroys the syntactic arrangement that binds the subject into
its structural role); rebuild rep + probe; SNF must DROP >=0.10 (else the probe read bag-of-words/a present
number-marked noun, not the SUBJECT'S number). NOVEL-LEXEME held-out: test subjects are surface-word-DISJOINT
from train, and word atoms are random per token (no shared morpheme), so a probe that generalizes learned an
ABSTRACT number code, not a memorized token.

BARS (disk-verified). MAJORITY_BAR = 0.6269 CITED@data/exp_agreement_attractor_role_binding_cg_viability_v1/
metrics.json (snf_majority). HARD_PASS (ALL): novel-lexeme disjoint AND pred-rep probe SNF >= 0.6269+0.10
(=0.7269) AND pred beats raw-bind probe by >= 0.05 (same probe) AND word-order-shuffle drop >= 0.10.
HARD_FAIL (ANY): pred SNF <= 0.6269 OR does not beat raw-bind (< 0.05 margin) OR shuffle drop < 0.05.
MIDDLE: clears 0.6269 narrowly (< 0.7269), or ambiguous shuffle (0.05 <= drop < 0.10), else.

HONEST FRAMING (verdict_msg). This is the LITERAL Elman test (structure in the representation). HARD_FAIL =
the induction-arc conclusion is AIRTIGHT: glass-box prediction WORKS but does NOT shape its representation to
encode induced structure -- the representation-shaping step is gradient-dependent (the precisely-localized b2
wall). HARD_PASS = LANDMARK (first glass-box structure induction here) -> HARDEST skunkworks-VET (ZERO false
positives); NEVER a self-declared CG.

# CELL-TEMPLATE MANDATORY: arms_differ (AF) at smoke (4 probe arms >=3 distinct); final_metrics_atomicity=
# tmp_replace (AH); except SystemExit: raise before except Exception (no BaseException); crlb_n/a (real-text
# probe; floor = majority 0.6269 + raw-bind baseline, not an argmax CRLB); baseline_in_band (AG; 0.05<majority
# <0.95); smoke at FULL N_DIM + FULL train cap (option A: sparse-lift is scale-sensitive -> discriminator
# fires at real scale); HARD_PASS strictly above majority bar by pre-registered 0.10 margin (L); cardinality =
# n_seeds; no bare except; calibration_check=default_ok (probe is a FIXED closed-form readout, RIDGE_LAM
# pre-registered=1.0, NO tuning); numbers tagged MEASURED@/CITED@/THEORETICAL@; glass-box source self-scan
# forbids optim/backprop tokens; deterministic seeding (hashlib atoms + fixed default_rng). ONE variable =
# prediction-shaped rep (M applied) vs raw-bind rep (M not applied), same probe. LOCAL FOREGROUND. NO push /
# NO store write / NO atom bank (skunkworks banks on HARD_PASS).
"""
from __future__ import annotations

import os
import argparse
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

ANCHOR_NAME = "agreement_word_prediction_rep_number_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# REUSE the fair cell's glass-box data/context helpers + the sparse-CA3 cell's soft-shard recipe VERBATIM.
import experiments.exp_agreement_word_predictive_hierarchy_fair_v1 as FAIR
import experiments.exp_agreement_word_sparse_ca3_predictive_hierarchy_v1 as SP

# ---- config ----
N_DIM = 1024
VOCAB_CAP = 2000
REP_WINDOW = FAIR.MAX_CTX        # =10; the verb-position representation must contain the SUBJECT to test
#                                  whether prediction-shaping encodes it. subj-in-window(<=10) coverage =
#                                  0.728 of SNF test MEASURED@cache-inspect; reported per seed as a ceiling.
# 29444 soft-shard recipe reused VERBATIM (task-specified E=4/f=0.20/center). window = REP_WINDOW (the whole
# predictor operates at this window; next-word ACCURACY is worse at wide window per the prior cell, but the
# representation must see the subject -- reported Stage-0 lift is the honest predictor-quality context).
CFG = {"E": 4, "f": 0.20, "method": "center", "window": REP_WINDOW}
RIDGE_LAM = 1.0                  # pre-registered fixed ridge penalty; NO tuning (calibration_check=default_ok)

FULL_SEEDS = [7, 13, 19]
SMOKE_SEEDS = [7]
FULL_TRAIN_CAP = 4000
FULL_TEST_CAP = 6000
SMOKE_TRAIN_CAP = 4000           # full train scale in smoke (sparse-lift is scale-sensitive; option A)
SMOKE_TEST_CAP = 1500

# ---- pre-registered bands ----
MAJORITY_BAR = 0.6269            # CITED@data/exp_agreement_attractor_role_binding_cg_viability_v1/metrics.json
ABL_FLOOR = 0.4889              # CITED@director (b2 ABL/ADIOS POS-regime SNF); reported for context
HEADTRACK_MARGIN = 0.10
RAW_MARGIN = 0.05               # "clear margin": pred-rep probe must beat the SAME probe on raw-bind by >=this
SHUFFLE_DROP_MIN = 0.10
NARROW_SHUFFLE_LO = 0.05


# ==================================================================================================
# Representation extraction (verb-position predictive rep vs raw-bind rep). Reuses the sparse-CA3 store.
# ==================================================================================================
def _verb_position(it):
    """Position right after the last prefix word == the verb-prediction step (cache prefix ends pre-verb)."""
    return [len(it["words"])]


def _l2rows(X):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return (X / (n + 1e-12)).astype(np.float32)


def compute_reps(train, test, atoms, w2i, cfg, seed):
    """Build the soft-shard predictor once; return (sp_tr, q_tr, sp_te, q_te). sp=raw-bind key,
    q=M*key=prediction rep. One rep per item at the verb position."""
    N = atoms["start"].shape[0]
    coder = SP.SparseCoder(cfg, seed, N)
    coder.fit_center(SP._iter_train_contexts(train, atoms, coder.window))
    Vcode = SP._value_codebook(w2i, coder.D, seed)
    M = SP.build_M(train, atoms, coder, Vcode, w2i)

    def verbreps(items):
        keys, meta = FAIR.build_keys_for_positions(items, atoms, coder.window, _verb_position)
        sp = coder.encode(keys)                     # (S, D) L2-normalized sparse key
        q = (M * sp).astype(np.float32)             # (S, D) prediction-shaped (elementwise store apply)
        row_of_item = np.full(len(items), -1, dtype=int)
        for r, (li, i) in enumerate(meta):
            row_of_item[li] = r
        assert np.all(row_of_item >= 0), "verb-rep alignment: some item produced no rep"
        return sp[row_of_item], q[row_of_item]

    sp_tr, q_tr = verbreps(train)
    sp_te, q_te = verbreps(test)
    return sp_tr, q_tr, sp_te, q_te


# ==================================================================================================
# Inspectable probes (closed-form measurement readouts; NO gradient). Reps L2-normalized inside each.
# ==================================================================================================
def proto_fit_predict(Xtr, ytr, Xte):
    """Nearest-class prototype (cosine) readout. proto_c = L2norm(mean of train reps for class c)."""
    Xtr = _l2rows(Xtr); Xte = _l2rows(Xte)
    protos = []
    for c in (0, 1):
        m = Xtr[ytr == c]
        p = m.mean(0) if len(m) else np.zeros(Xtr.shape[1], dtype=np.float32)
        protos.append(FAIR._l2n(p.astype(np.float32)))
    P = np.stack(protos)                             # (2, D)
    return np.argmax(Xte @ P.T, axis=1).astype(int)


def ridge_fit_predict(Xtr, ytr, Xte, lam):
    """Closed-form ridge-linear probe: w = (X^T X + lam I)^-1 X^T y, y in {-1,+1}; predict sign(x.w)."""
    Xtr = _l2rows(Xtr).astype(np.float64); Xte = _l2rows(Xte).astype(np.float64)
    y = (2.0 * ytr - 1.0).astype(np.float64)
    D = Xtr.shape[1]
    A = Xtr.T @ Xtr + lam * np.eye(D)
    w = np.linalg.solve(A, Xtr.T @ y)
    return (Xte @ w > 0.0).astype(int)


def wordorder_shuffle(items, seed):
    """STRUCTURE-SHUFFLE control: permute word POSITIONS within each item (preserve multiset of words +
    numbers; destroy syntactic arrangement / subject structural role). Rep is word-based so this changes it;
    the subject-number LABEL (r['label']) and SNF membership (r['subj_pos']) are UNCHANGED."""
    out = []
    for idx, it in enumerate(items):
        w = list(it["words"])
        perm = np.random.default_rng(seed * 1_000_003 + idx).permutation(len(w))
        r2 = dict(it)
        r2["words"] = [w[p] for p in perm]
        out.append(r2)
    return out


# ==================================================================================================
# Per-seed run.
# ==================================================================================================
def _snf_acc(pred, yte, snf):
    a, _ = FAIR._acc_mask(pred, yte, snf)
    return a


def _all_acc(pred, yte):
    return float(np.mean(np.asarray(pred) == np.asarray(yte)))


def run_seed(seed, tr_cap, te_cap, linzen):
    train, test = FAIR.split_items(linzen, tr_cap, te_cap, seed)
    disjoint, ntr_lex, nte_lex = FAIR.novel_lexeme_disjoint(train, test)
    w2i = FAIR.build_vocab(train, VOCAB_CAP)
    atoms = FAIR.build_atoms("s%d" % seed, w2i, N_DIM)
    ytr = np.array([r["label"] for r in train], dtype=int)
    yte = np.array([r["label"] for r in test], dtype=int)
    snf = np.array([r["subj_pos"] != 0 for r in test])
    maj = int(round(float(np.mean(ytr))))
    snf_maj = _snf_acc(np.full(len(test), maj), yte, snf)
    # subject-in-window coverage (ceiling; subj_pos used ONLY for this diagnostic + label + SNF subset)
    cov_list = [(len(r["words"]) - r["noun_word_idx"][r["subj_pos"]]) <= REP_WINDOW
                for r in test if r["subj_pos"] != 0]
    subj_in_window = round(float(np.mean(cov_list)), 4) if cov_list else None

    # ---- Stage-0 predictor-quality diagnostic (next-word in-vocab lift at REP_WINDOW; honest context) ----
    s0 = SP.stage0_config(train, test, atoms, w2i, CFG, seed)

    # ---- representations ----
    sp_tr, q_tr, sp_te, q_te = compute_reps(train, test, atoms, w2i, CFG, seed)

    # ---- 4 probe arms ----
    raw_proto = proto_fit_predict(sp_tr, ytr, sp_te)
    pred_proto = proto_fit_predict(q_tr, ytr, q_te)
    raw_lin = ridge_fit_predict(sp_tr, ytr, sp_te, RIDGE_LAM)
    pred_lin = ridge_fit_predict(q_tr, ytr, q_te, RIDGE_LAM)

    rp = _snf_acc(raw_proto, yte, snf); pp = _snf_acc(pred_proto, yte, snf)
    rl = _snf_acc(raw_lin, yte, snf); pl = _snf_acc(pred_lin, yte, snf)

    # ---- structure-shuffle (word-order) on the prediction rep, both probes ----
    sh_tr = wordorder_shuffle(train, seed)
    sh_te = wordorder_shuffle(test, 1000 + seed)
    _, qsh_tr, _, qsh_te = compute_reps(sh_tr, sh_te, atoms, w2i, CFG, seed)
    ysh_tr = np.array([r["label"] for r in sh_tr], dtype=int)   # labels unchanged by word-order shuffle
    sh_pred_proto = proto_fit_predict(qsh_tr, ysh_tr, qsh_te)
    sh_pred_lin = ridge_fit_predict(qsh_tr, ysh_tr, qsh_te, RIDGE_LAM)
    sh_pp = _snf_acc(sh_pred_proto, yte, snf); sh_pl = _snf_acc(sh_pred_lin, yte, snf)

    # ---- winner-probe headline (does ANY inspectable probe recover subject-number from the prediction rep) ----
    if pp >= pl:
        winner = "prototype"; pred_snf = pp; raw_snf = rp; sh_snf = sh_pp
    else:
        winner = "ridge_linear"; pred_snf = pl; raw_snf = rl; sh_snf = sh_pl
    margin_raw = round(pred_snf - raw_snf, 4)
    shuffle_drop = round(pred_snf - sh_snf, 4)

    # ---- arms_differ (META_RULE_AF): 4 probe arms, require >=3 distinct on SNF ----
    def _h(a):
        return hashlib.sha256(np.asarray(a)[snf].tobytes()).hexdigest()
    arm_hashes = {"pred_proto": _h(pred_proto), "raw_proto": _h(raw_proto),
                  "pred_lin": _h(pred_lin), "raw_lin": _h(raw_lin)}
    arms_differ = len(set(arm_hashes.values())) >= 3

    return {
        "seed": seed, "n_train": len(train), "n_test": len(test), "n_snf": int(snf.sum()),
        "novel_lexeme_disjoint": bool(disjoint), "n_train_subj_lex": ntr_lex, "n_test_subj_lex": nte_lex,
        "vocab_size": len(w2i), "subj_in_window_frac": subj_in_window,
        "snf_majority_local": round(snf_maj, 4) if snf_maj is not None else None,
        "stage0_invocab_lift": s0["invocab_lift"], "stage0_invocab_ca3": s0["invocab_ca3"],
        "stage0_invocab_unigram": s0["invocab_unigram"], "stage0_unk_rate": s0["unk_rate"],
        "rep_dim": int(sp_tr.shape[1]),
        # per-arm SNF (the load-bearing measurements)
        "snf_pred_proto": round(pp, 4), "snf_raw_proto": round(rp, 4),
        "snf_pred_linear": round(pl, 4), "snf_raw_linear": round(rl, 4),
        "snf_shuffle_pred_proto": round(sh_pp, 4), "snf_shuffle_pred_linear": round(sh_pl, 4),
        # full-test diagnostics
        "all_pred_proto": round(_all_acc(pred_proto, yte), 4),
        "all_raw_proto": round(_all_acc(raw_proto, yte), 4),
        # winner headline
        "winner_probe": winner, "pred_snf": round(pred_snf, 4), "raw_snf": round(raw_snf, 4),
        "shuffle_snf": round(sh_snf, 4), "margin_vs_raw": margin_raw, "shuffle_drop": shuffle_drop,
        "arms_differ": bool(arms_differ), "arm_hashes": {k: v[:12] for k, v in arm_hashes.items()},
    }


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows):
    disjoint_all = all(r.get("novel_lexeme_disjoint") for r in rows)
    m_pred = _mean(rows, "pred_snf")
    m_raw = _mean(rows, "raw_snf")
    m_shuf = _mean(rows, "shuffle_snf")
    m_predproto = _mean(rows, "snf_pred_proto")
    m_predlin = _mean(rows, "snf_pred_linear")
    m_rawproto = _mean(rows, "snf_raw_proto")
    m_rawlin = _mean(rows, "snf_raw_linear")
    m_lift = _mean(rows, "stage0_invocab_lift")
    m_cov = _mean(rows, "subj_in_window_frac")
    m_majloc = _mean(rows, "snf_majority_local")
    margin_raw = round(m_pred - m_raw, 4) if (m_pred is not None and m_raw is not None) else None
    shuffle_drop = round(m_pred - m_shuf, 4) if (m_pred is not None and m_shuf is not None) else None
    arms_differ_all = all(r.get("arms_differ") for r in rows)
    winners = [r.get("winner_probe") for r in rows]

    summary = {
        "pred_rep_snf": m_pred, "raw_bind_snf": m_raw, "shuffle_snf": m_shuf,
        "snf_pred_proto": m_predproto, "snf_pred_linear": m_predlin,
        "snf_raw_proto": m_rawproto, "snf_raw_linear": m_rawlin,
        "majority_bar_cited": MAJORITY_BAR, "abl_floor_cited": ABL_FLOOR,
        "snf_majority_local": m_majloc, "margin_vs_raw": margin_raw, "shuffle_drop": shuffle_drop,
        "stage0_invocab_lift": m_lift, "subj_in_window_frac": m_cov,
        "winners_per_seed": winners, "arms_differ_all": bool(arms_differ_all),
        "raw_margin_required": RAW_MARGIN, "shuffle_drop_min": SHUFFLE_DROP_MIN,
    }

    if not disjoint_all:
        summary["verdict_band"] = "HARD_FAIL_split"
        return "HARD_FAIL_SPLIT_INTEGRITY", \
            "novel-lexeme split NOT disjoint across train/test; wug-integrity broken; refuse to interpret.", \
            summary

    beats_majority_wide = (m_pred is not None) and (m_pred >= MAJORITY_BAR + HEADTRACK_MARGIN)
    beats_majority_any = (m_pred is not None) and (m_pred > MAJORITY_BAR)
    beats_raw = (margin_raw is not None) and (margin_raw >= RAW_MARGIN)
    structure_used = (shuffle_drop is not None) and (shuffle_drop >= SHUFFLE_DROP_MIN)
    ambiguous_shuffle = (shuffle_drop is not None) and (NARROW_SHUFFLE_LO <= shuffle_drop < SHUFFLE_DROP_MIN)
    cfg_str = "E=%d,f=%.2f,%s,win=%d,D=%d" % (CFG["E"], CFG["f"], CFG["method"], CFG["window"],
                                              rows[0].get("rep_dim", 0))

    # ---- HARD_PASS: ALL of {wide-majority, beats-raw, structure-used, arms-differ} ----
    if beats_majority_wide and beats_raw and structure_used and arms_differ_all:
        summary["verdict_band"] = "HARD_PASS"
        msg = ("HARD_PASS_PREDICTION_REP_ENCODES_NUMBER (LANDMARK -> HARDEST skunkworks-VET REQUIRED; NOT a "
               "self-declared CG) | LITERAL Elman test: the PREDICTION-INDUCED representation encodes the "
               "subject's agreement number | winner-probe pred-rep SNF=%s beats majority %s by >=%.2f | beats "
               "the SAME probe on the RAW-BIND rep (raw SNF=%s, margin=%s >= %.2f) -> attributable to "
               "PREDICTION-SHAPING not the fixed encoding | word-order-shuffle SNF=%s drop=%s (>=%.2f) | novel-"
               "lexeme held-out disjoint | probes: pred_proto=%s pred_lin=%s raw_proto=%s raw_lin=%s | %s "
               "subj-in-window=%s stage0_lift=%s | glass-box closed-form probe (no gradient)." % (
                   m_pred, MAJORITY_BAR, HEADTRACK_MARGIN, m_raw, margin_raw, RAW_MARGIN, m_shuf, shuffle_drop,
                   SHUFFLE_DROP_MIN, m_predproto, m_predlin, m_rawproto, m_rawlin, cfg_str, m_cov, m_lift))
        return "HARD_PASS_PREDICTION_REP_ENCODES_NUMBER", msg, summary

    # ---- HARD_FAIL: ANY of {below-majority, no-raw-margin, shuffle-clearly-no-drop} ----
    hard_fail = ((m_pred is None) or (m_pred <= MAJORITY_BAR) or (not beats_raw) or
                 (shuffle_drop is None) or (shuffle_drop < NARROW_SHUFFLE_LO))
    if hard_fail:
        summary["verdict_band"] = "HARD_FAIL"
        msg = ("HARD_FAIL_PREDICTION_REP_DOES_NOT_ENCODE_NUMBER | LITERAL Elman test (structure in the "
               "REPRESENTATION, not the residual) | the prediction-induced rep does NOT carry the subject's "
               "number recoverable by an inspectable probe: winner-probe pred-rep SNF=%s vs majority %s (need "
               ">=%s), margin vs raw-bind=%s (need >=%.2f; raw SNF=%s), word-order-shuffle drop=%s (need >=%.2f)"
               ". AIRTIGHT induction-arc conclusion: glass-box prediction WORKS (stage0 in-vocab lift=%s) but "
               "does NOT shape its representation to encode induced structure -- b2 (chunking) + dense + sparse-"
               "residual + this (representation) all exhausted; the representation-shaping step is gradient-"
               "dependent (the precisely-localized b2 wall). A real CG needs a different mechanism. probes: "
               "pred_proto=%s pred_lin=%s raw_proto=%s raw_lin=%s | %s subj-in-window=%s | glass-box closed-form "
               "probe (no gradient)." % (
                   m_pred, MAJORITY_BAR, round(MAJORITY_BAR + HEADTRACK_MARGIN, 4), margin_raw, RAW_MARGIN,
                   m_raw, shuffle_drop, SHUFFLE_DROP_MIN, m_lift, m_predproto, m_predlin, m_rawproto, m_rawlin,
                   cfg_str, m_cov))
        return "HARD_FAIL_PREDICTION_REP_DOES_NOT_ENCODE_NUMBER", msg, summary

    # ---- MIDDLE: clears majority narrowly, or ambiguous shuffle ----
    summary["verdict_band"] = "MIDDLE_BAND"
    msg = ("MIDDLE_BAND_PARTIAL_REP_STRUCTURE | LITERAL Elman test | winner-probe pred-rep SNF=%s beats "
           "majority %s (any=%s) but not wide+margin %s (wide=%s); margin vs raw-bind=%s (beats_raw=%s); word-"
           "order-shuffle drop=%s (structure_used=%s ambiguous=%s). Partial/narrow -- suggestive but not the "
           "airtight landmark. probes: pred_proto=%s pred_lin=%s raw_proto=%s raw_lin=%s | %s subj-in-window=%s "
           "stage0_lift=%s | glass-box closed-form probe (no gradient)." % (
               m_pred, MAJORITY_BAR, beats_majority_any, round(MAJORITY_BAR + HEADTRACK_MARGIN, 4),
               beats_majority_wide, margin_raw, beats_raw, shuffle_drop, structure_used, ambiguous_shuffle,
               m_predproto, m_predlin, m_rawproto, m_rawlin, cfg_str, m_cov, m_lift))
    return "MIDDLE_BAND_PARTIAL_REP_STRUCTURE", msg, summary


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
    data = FAIR.load_cache()
    linzen = data["linzen"]
    print("[%s:%s] word-cache: %d items | seeds=%s caps=(%d,%d) N_DIM=%d cfg=%s" % (
        ANCHOR_NAME, mode, len(linzen), seeds, tr_cap, te_cap, N_DIM, CFG), flush=True)

    rows = []
    for s in seeds:
        ts = time.time()
        r = run_seed(s, tr_cap, te_cap, linzen)
        rows.append(r)
        print("[seed=%d] pred_snf=%s raw_snf=%s (margin=%s) shuffle_snf=%s (drop=%s) winner=%s | "
              "pred_proto=%s raw_proto=%s pred_lin=%s raw_lin=%s | maj_loc=%s cov=%s lift=%s (%.1fs)" % (
                  s, r["pred_snf"], r["raw_snf"], r["margin_vs_raw"], r["shuffle_snf"], r["shuffle_drop"],
                  r["winner_probe"], r["snf_pred_proto"], r["snf_raw_proto"], r["snf_pred_linear"],
                  r["snf_raw_linear"], r["snf_majority_local"], r["subj_in_window_frac"],
                  r["stage0_invocab_lift"], time.time() - ts), flush=True)

    verdict, msg, summary = build_verdict(rows)
    elapsed = time.time() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": len(rows) == len(seeds), "N_DIM": N_DIM, "VOCAB_CAP": VOCAB_CAP, "cfg": CFG,
        "ridge_lam": RIDGE_LAM,
        "bands": {"MAJORITY_BAR": MAJORITY_BAR, "HEADTRACK_MARGIN": HEADTRACK_MARGIN,
                  "RAW_MARGIN": RAW_MARGIN, "SHUFFLE_DROP_MIN": SHUFFLE_DROP_MIN,
                  "NARROW_SHUFFLE_LO": NARROW_SHUFFLE_LO},
        "summary_metrics": summary, "per_seed": rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "chunked_numpy_softshard_sparse_bind_store_plus_closedform_probe_foreground",
        "crlb_n/a": ("real-word agreement representation probe; floor is majority %s (cited) + the raw-bind "
                     "baseline probe, not an argmax CRLB" % MAJORITY_BAR),
        "progress_logging": "print_flush_true", "deterministic_seeding": True,
        "glass_box_non_gradient": True,
        "calibration_check": "default_ok_for_this_regime",
        "mechanism_note": ("LITERAL Elman test: prediction-INDUCED rep (q=M*sparse_key at verb position) vs "
                           "RAW-BIND rep (sparse_key, no store) -- ONE variable = store applied. Both L2-"
                           "normalized. Inspectable closed-form probes: prototype (cosine) + ridge-linear "
                           "((X^T X + lam I)^-1 X^T y). Discriminator = pred beats SAME probe on raw by >=%s. "
                           "Structure-shuffle = word-order permutation (bag preserved, syntax destroyed) drop "
                           ">=%s. Novel-lexeme held-out (subjects disjoint; random per-token atoms)." % (
                               RAW_MARGIN, SHUFFLE_DROP_MIN)),
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
    forbidden = [r"\.backward\(", r"torch\." + "optim", r"loss\.backward", r"auto" + "grad",
                 r"optimizer\.", r"nn\.Module"]
    hits = [p for p in forbidden if re.search(p, src)]
    assert not hits, "glass-box-non-gradient VIOLATION: %s" % hits


def self_test():
    print("=== prediction-rep number-probe self-test ===", flush=True)
    _scan_no_gradient()
    print("[self-test] glass-box-non-gradient source scan clean", flush=True)

    # closed-form probes recover a planted linear signal (validity, not the mechanism outcome)
    rng = np.random.default_rng(0)
    D = 64; ntr = 200; nte = 120
    direction = rng.standard_normal(D).astype(np.float32)
    ytr = rng.integers(0, 2, ntr); yte = rng.integers(0, 2, nte)
    Xtr = rng.standard_normal((ntr, D)).astype(np.float32) + (2 * ytr - 1)[:, None] * direction
    Xte = rng.standard_normal((nte, D)).astype(np.float32) + (2 * yte - 1)[:, None] * direction
    acc_p = float(np.mean(proto_fit_predict(Xtr, ytr, Xte) == yte))
    acc_r = float(np.mean(ridge_fit_predict(Xtr, ytr, Xte, RIDGE_LAM) == yte))
    assert acc_p > 0.8 and acc_r > 0.8, "probes fail on planted signal: proto=%.3f ridge=%.3f" % (acc_p, acc_r)
    # predictions are {0,1}
    assert set(np.unique(proto_fit_predict(Xtr, ytr, Xte)).tolist()).issubset({0, 1})
    print("[self-test] probes recover planted signal: proto=%.3f ridge=%.3f" % (acc_p, acc_r), flush=True)

    data = FAIR.load_cache(); linzen = data["linzen"]
    assert len(linzen) > 1000, "cache too small"
    train, test = FAIR.split_items(linzen, 800, 700, 7)
    disjoint, ntr_l, nte_l = FAIR.novel_lexeme_disjoint(train, test)
    assert disjoint, "novel-lexeme split NOT disjoint"
    w2i = FAIR.build_vocab(train, VOCAB_CAP)
    atoms = FAIR.build_atoms("s7", w2i, N_DIM)
    ytr = np.array([r["label"] for r in train]); yte = np.array([r["label"] for r in test])
    assert set(np.unique(ytr).tolist()) == {0, 1}, "train labels not both classes present"
    snf = np.array([r["subj_pos"] != 0 for r in test])
    assert int(snf.sum()) > 20, "SNF subset too small"
    maj = int(round(float(np.mean(ytr))))
    snf_maj, _ = FAIR._acc_mask(np.full(len(test), maj), yte, snf)
    assert snf_maj is not None and 0.05 < snf_maj < 0.95, "majority SNF out of band (AG): %s" % snf_maj
    print("[self-test] cache OK %d; novel-lexeme disjoint (tr=%d te=%d); majority SNF in band=%.4f" % (
        len(linzen), ntr_l, nte_l, snf_maj), flush=True)

    # REAL substrate reps at tiny scale (exercise the actual store path) + arms differ + shuffle changes rep
    sp_tr, q_tr, sp_te, q_te = compute_reps(train, test, atoms, w2i, CFG, 7)
    assert sp_tr.shape[1] == CFG["E"] * N_DIM, "rep dim wrong"
    assert not np.allclose(sp_te, q_te), "pred rep (M*key) identical to raw rep (key) -- store did nothing"
    pp = proto_fit_predict(q_tr, ytr, q_te); rp = proto_fit_predict(sp_tr, ytr, sp_te)
    pl = ridge_fit_predict(q_tr, ytr, q_te, RIDGE_LAM); rl = ridge_fit_predict(sp_tr, ytr, sp_te, RIDGE_LAM)
    hashes = {k: hashlib.sha256(np.asarray(v)[snf].tobytes()).hexdigest()
              for k, v in [("pp", pp), ("rp", rp), ("pl", pl), ("rl", rl)]}
    assert len(set(hashes.values())) >= 3, "META_RULE_AF: <3 distinct probe arms (bit-identical bug)"
    sh_tr = wordorder_shuffle(train, 7)
    _, qsh_tr, _, _ = compute_reps(sh_tr, test, atoms, w2i, CFG, 7)
    assert not np.allclose(qsh_tr, q_tr), "word-order shuffle did not change the prediction rep"
    a_pp, _ = FAIR._acc_mask(pp, yte, snf); a_rp, _ = FAIR._acc_mask(rp, yte, snf)
    print("[self-test] reps OK D=%d; pred!=raw; arms_differ=%s (>=3); shuffle changes rep | "
          "pred_proto SNF=%.4f raw_proto SNF=%.4f" % (sp_tr.shape[1], len(set(hashes.values())) >= 3,
                                                      a_pp, a_rp), flush=True)
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
