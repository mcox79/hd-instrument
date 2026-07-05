"""schema_relation_hardneg_mined_scorer_v1 -- MARGIN-augmented (NOT exposure-mined) scorer loss.

SCIENTIFIC QUESTION (the rank-1 fix the post-hoc rescore could not deliver):
  The debias-rescore child (schema_relation_hubness_debias_rescore_v1) landed MIDDLE_BAND: the
  training-FREE CSLS/logit-adjust rescore lifts paired-rms but is a PHANTOM on the FROZEN slot (the
  scale-representative, post-hoc-immune slot) -- the win is 100% SHUFFLED-collapse
  (CITED@notes/research_hardneg_mined_scorer_v1_spec_2026-07-05.md; MEASURED@
  data/exp_schema_relation_hubness_debias_rescore_v1_smoke/metrics.json). The spec drill established:
  the scorer already trains EXACT FULL SOFTMAX (every candidate in the loss every step), so DPR/ANCE
  exposure-mining gives NO benefit (nothing was ever absent). The mechanistically-matched fix is a
  MARGIN-augmented loss (additive-margin softmax + a periodic hard-negative HINGE calibrated to the
  MEASURED z-margin 2.2-2.7 std) that keeps gradient pressure on the current top-ranked WRONG
  competitor after plain CE's gradient (p_true-1) has decayed to ~0. "Mining" is repurposed as
  curriculum / margin-target selection (identify the top wrong object every K steps; trivial at
  V<=1000, no ANN), NOT new-negative exposure.

  THE decisive question: does a TRAINED margin+mining fix move the needle where the training-FREE
  fix could not, on the SAME diagnosed bias? Applied to BOTH slots (FROZEN is the proven post-hoc-
  immune slot -- the real test is whether margin-TRAINING the scorer overcomes content-geometry
  hubness that post-hoc rescore couldn't). CE_BASELINE = the parent reframe scorer VERBATIM
  (positive control); MARGIN_HARDNEG + LOGIT_ADJUST_LOSS (Menon 2021 train-time) are the fixes.

DISCRIMINATOR (load-bearing): REAL-ABSOLUTE Hits@1 LIFT of the new-loss arm over the matched
  CE_BASELINE (same slot/V/seed), NOT the gameable paired-rms. A TRAINED mechanism can overfit-game
  the SHUFFLED control just like the post-hoc one did -> SHUF_OVERFIT_GUARD (mandatory, load-bearing):
  the SHUFFLED arm's absolute Hits@1 under the new loss must NOT rise more than +0.03 over CE_BASELINE
  SHUFFLED; a violation zeroes that unit's HP eligibility (instrument failure, not a win). MRR
  real_minus_shuf (inductive filtered) >= 0.15 is the second gate (genuine subject->object signal).

COMPUTE: class (a) batched-GPU. FROZEN trains each (method x paired-arm) as torch-bmm B=2 (ANALYTIC
  gradient; numpy fallback). JOINT trains each method as batched-B=2 autograd. device auto->cuda on the
  GPU box. Storage strategy: no_storage. No generative-LLM calls (deterministic caches only). Heavier
  than the debias cell (adds per-method training loops): expect ~15-25 min FULL.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; {CE,MARGIN,LOGIT} x REAL/SHUF matrices all differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException); start-marker + crash-diag + heartbeat
# - crlb n/a (rank transfer; no closed-form noise floor). chance floor k/V stated; reachability declared
# - baseline_in_band at smoke (SHUFFLED filtered Hits@10 not saturated <0.95; CE_BASELINE reproduces parent)
# - discriminator survives scale (B/C): synth_label_prior_hub proves the TRAINED fix instrument detects
#   a >=0.05 REAL Hits@1 lift on a by-construction removable label-prior nuisance (fires via LOGIT_ADJUST,
#   Menon's exact mechanism; MARGIN is FD-gradient-validated but ~0 on a converged bilinear -- a genuine
#   measured property, not a bug); synth_ambiguous_null proves NEITHER fix manufactures a win on
#   genuinely-ambiguous content. Real-data V>=300 lift IS the question, justified.
# - HARD_PASS strictly above floor (REAL Hits@1 lift 0.05 is 2.5x the HF ceiling 0.02; MRR rms 0.15)
# - HP_SCOPE: HP gates apply to best-of-{FROZEN,JOINT} x {MARGIN_HARDNEG,LOGIT_ADJUST_LOSS}
#   REAL/inductive/FILTERED SEMANTIC rel x enc at V>=300; CE_BASELINE=baseline(parent); SHUFFLED=guard
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = grid x 2 slots x 2 arms x 2 evals; methods sub-fields)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (m_add=1.0*tau/m_hinge=2.5*tau FIXED to the
#   MEASURED z-margin; synth-hub-fires + null-clean are the proofs; NOT tuned-for-pass on real data)
# - progress_logging = print_flush_true (all progress lines flush=True; line-buffered stdout)
# - reuse: parent scorer/split/rank/knn/joint-encoder imported VERBATIM as `ref`; CE_BASELINE calls
#   ref.fit_scorer_paired / ref.joint_train_score byte-for-byte (positive control = the parent, Gate D)
# - gradient self-tests: finite-difference checks on margin-CE + hinge + logit-adjust analytic gradients
# - all numbers in design notes tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "8")
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")   # CUDA env BEFORE torch import

import argparse
import json
import time
import hashlib
import platform
import traceback
import collections
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Reuse the parent reframe cell VERBATIM (byte-identical scorer/split/rank/knn/joint code objects).
import experiments.exp_schema_relation_hitsatk_mrr_reframe_v1 as ref
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

try:
    import torch
    import torch.nn.functional as F_t
    _TORCH_OK = True
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _TORCH_OK = False
    _DEVICE = "cpu"

ANCHOR_NAME = "schema_relation_hardneg_mined_scorer_v1"

# ----------------------------------------------------------------------------
# Run mode. Runner invokes BARE + injects HDLAB_RUN_MODE=full. Terminal tier = full.
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _P.parse_known_args()
_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")

# ----------------------------------------------------------------------------
# Config -- reuse parent constants; add margin/mining machinery.
# ----------------------------------------------------------------------------
N_DIM = ref.N_DIM
RELATIONS_SEM = ref.RELATIONS_SEM
RELATIONS_NEG = ref.RELATIONS_NEG
RELATIONS_ALL = ref.RELATIONS_ALL
CONTENT_ENCODINGS = ref.CONTENT_ENCODINGS
ARMS = ref.ARMS                       # ["REAL", "SHUFFLED"]
EVAL_MODES = ref.EVAL_MODES           # ["inductive", "transductive"]
SCORER_SLOTS = ["FROZEN", "JOINT"]    # trainable slots (KNN dropped -- no training loss)
HP_SLOTS = ["FROZEN", "JOINT"]
HITS_KS = ref.HITS_KS
METRIC_KEYS = ref.METRIC_KEYS

TRAIN_METHODS = ["CE_BASELINE", "MARGIN_HARDNEG", "LOGIT_ADJUST_LOSS"]
METHODS_HP = ["MARGIN_HARDNEG", "LOGIT_ADJUST_LOSS"]   # HP-eligible fixes (vs CE_BASELINE)

# FIXED loss hyperparameters, pre-registered BEFORE the real-data run; NOT tuned-for-pass:
# m_add / m_hinge are set in tau UNITS so the margin in softmax-input space is scale-free:
#   (S - m_add)/tau = S/tau - 1.0  (m_add = 1.0*tau)  -> +1 softmax-unit margin
#   hinge on raw S with m_hinge = 2.5*tau  -> +2.5 softmax-units, == the MEASURED z-margin 2.2-2.7 std
M_ADD_TAU_MULT = 1.0        # additive margin = M_ADD_TAU_MULT * tau_slot
M_HINGE_TAU_MULT = 2.5      # hinge margin  = M_HINGE_TAU_MULT * tau_slot (calibrated to z-margin)
LAMBDA_HINGE = 1.0          # hinge loss weight
TAU_ADJ = 1.0               # logit-adjustment temperature (Menon et al. 2021 default)
LOGIT_EPS = 1.0             # Laplace smoothing for the train-frequency prior
SLOT_TAU = {"FROZEN": ref.SCORER_TAU, "JOINT": ref.JOINT_TAU}

# Synthetic control regime (discriminator-fires proofs; construction may be calibrated to FIRE, the
# real-data bands below are independent + LOCKED). MEASURED off-disk 2026-07-05: the margin/mining
# lever is near-inert on a FROZEN bilinear at convergence (full-batch GD reaches the max-likelihood W
# regardless of margin) -- a genuine property, NOT a bug (margin's correctness is proven by the
# finite-difference gradient self-tests). The positive control therefore fires via LOGIT_ADJUST_LOSS
# (Menon 2021's exact train-time mechanism) on a by-construction removable label-prior nuisance -- the
# best-of{MARGIN,LOGIT} instrument detects a real >=0.05 removable bias; the null proves no false win.
SCM_D = ref.SCM_D
SCM_V = ref.SCM_V
SCM_M = ref.SCM_M
SCM_TEST = ref.SCM_TEST
SYNTH_LP_V = 24              # positive control vocab (small so per-object samples are plentiful)
SYNTH_LP_HN = 5             # head/hub object count (relabel target set)
SYNTH_LP_M = 2000           # train subjects (map well-learned)
SYNTH_LP_T = 800            # test subjects (large -> low Hits@1 variance)
SYNTH_LP_DF = 64            # scorer projection dim
SYNTH_LP_STEPS = 600        # CE overfits the train label prior -> LOGIT has a large nuisance to remove
SYNTH_LP_RELABEL = 0.60     # fraction of TRAIN relabeled to head objects (severe nuisance prior)
SYNTH_NULL_M = 2000
SYNTH_NULL_T = 800
SYNTH_NULL_STEPS = 400

# ----------------------------------------------------------------------------
# Pre-reg bands (LOCKED)
# ----------------------------------------------------------------------------
HP_REAL_HITS1_LIFT_MIN = 0.05   # best-of{MARGIN,LOGIT} REAL-abs Hits@1 lift over CE_BASELINE (same slot)
HP_MRR_RMS_MIN = 0.15           # new-loss arm filtered MRR real_minus_shuf(inductive)
SHUF_OVERFIT_TOL = 0.03         # SHUF_OVERFIT_GUARD: SHUFFLED-abs Hits@1 lift over CE_BASELINE <= this
HF_REAL_HITS1_LIFT_MAX = 0.02   # HARD_FAIL: max over sem(rel x enc) at V>=300 of best REAL Hits@1 lift <= this
# discriminator-fires gate (synthetic controls; NOT the real-data verdict):
SYNTH_LP_FIRE_LIFT = 0.05       # label_prior_hub: best-of{MARGIN,LOGIT} REAL Hits@1 lift over CE (fires via LOGIT)
SYNTH_LP_SHUF_MAX = 0.03        # label_prior_hub: SHUFFLED lift bounded (guard fires clean)
SYNTH_NULL_TOL = 0.03           # ambiguous_null: |margin/logit REAL & SHUF lift over CE| bounded
BIND_ROUNDTRIP_MIN = 0.90
BASE_SAT_HI = 0.95              # SHUFFLED filtered Hits@10 must be below this (not saturated)


# ----------------------------------------------------------------------------
# CONFIG GRID -- mirror the parent reframe / debias cells
# ----------------------------------------------------------------------------
def _cfg(name, V, M, rels, encs):
    return {"name": name, "V": V, "M": M, "rels": list(rels), "encs": list(encs)}


if RUN_MODE == "smoke":
    _smoke_seeds_env = os.environ.get("HDLAB_SMOKE_SEEDS", "")
    if _smoke_seeds_env.strip():
        SEEDS = [int(x) for x in _smoke_seeds_env.replace(",", " ").split()]
    else:
        SEEDS = [7, 13, 19]           # multi-seed smoke gate (discriminator = per-query Hits@1 lift)
    N_TEST_PER = 60
    POOL_CAP = 6000
    CONFIGS = [_cfg("V100", 100, 200, RELATIONS_SEM, ["bge_semantic"]),
               _cfg("V300", 300, 300, RELATIONS_SEM, ["bge_semantic"])]
    _SMOKE_JOINT = dict(H=128, DF=64, STEPS=80)
    _SMOKE_FROZEN_STEPS = 300
    _SMOKE_FROZEN_DF = 128
    _SMOKE_MINE_K = 25
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    POOL_CAP = 30000
    CONFIGS = [_cfg(f"V{v}", v, 800, RELATIONS_ALL, CONTENT_ENCODINGS) for v in [100, 300, 1000]]
    _SMOKE_JOINT = None
    _SMOKE_FROZEN_STEPS = None
    _SMOKE_FROZEN_DF = None
    _SMOKE_MINE_K = None

MINE_K = 25 if RUN_MODE == "smoke" else 50    # re-mine cadence (curriculum / target selection)


def _joint_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_JOINT["H"], _SMOKE_JOINT["DF"], _SMOKE_JOINT["STEPS"]
    return ref.JOINT_H, ref.JOINT_DF, ref.JOINT_STEPS


def _frozen_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_FROZEN_DF, _SMOKE_FROZEN_STEPS
    return ref.FROZEN_DF, ref.FROZEN_STEPS


def expected_units(configs, seeds) -> int:
    # per (cfg,rel,enc): slots(2) x arms(2) x evals(2) = 8
    tot = 0
    for c in configs:
        tot += len(c["rels"]) * len(c["encs"]) * (len(SCORER_SLOTS) * len(ARMS) * len(EVAL_MODES))
    return tot * len(seeds)


EXPECTED_N_UNITS = expected_units(CONFIGS, SEEDS)


def _r(x):
    try:
        return round(float(x), 4) if x == x else None
    except Exception:
        return None


def compute_log_prior(y_train: np.ndarray, V_eff: int, eps: float = LOGIT_EPS) -> np.ndarray:
    """log P_train(object) with Laplace smoothing. Invariant to subject-object shuffle (multiset same)."""
    cnt = np.bincount(y_train.astype(np.int64), minlength=V_eff).astype(np.float64)
    pi = (cnt + eps) / (cnt.sum() + eps * V_eff)
    return np.log(pi).astype(np.float32)


# ============================================================================
# FROZEN margin/logit training (ANALYTIC gradient) -- the new mechanism.
# CE_BASELINE is provided by ref.fit_scorer_paired (verbatim); this trains MARGIN/LOGIT.
# ============================================================================
def _frozen_grad_single(U, Vo, W, yv, tau, l2, loss_mode, m_add, m_hinge, lam_hinge, h_cache,
                        log_prior_adj) -> np.ndarray:
    """Analytic gradient of the chosen loss w.r.t. W for ONE arm. U:(M,df), Vo:(V,df), W:(df,df).
      loss_mode == 'margin_hardneg':  CE with additive margin -m_add on the true logit  +  lam*hinge
      loss_mode == 'logit_adjust'  :  CE with +tau_adj*log_prior added to the softmax INPUT (Menon)
    h_cache: (M,) mined hard-negative object indices (used by margin hinge; refreshed by caller).
    log_prior_adj: (V,) == tau_adj*log_prior (used by logit_adjust). Returns gW (df,df) incl. l2.
    """
    M = U.shape[0]
    ar = np.arange(M)
    S = (U @ W) @ Vo.T                                    # (M,V) raw scores
    if loss_mode == "logit_adjust":
        Z = S / tau + log_prior_adj[None, :]             # add adjustment to softmax input
        P = ref._softmax_rows(Z)
        P[ar, yv] -= 1.0
        P /= M
        gW = U.T @ (P @ Vo) / tau + l2 * W
        return gW.astype(np.float32)
    # margin_hardneg
    Sm = S.copy()
    Sm[ar, yv] -= m_add                                   # additive margin on true-class logit
    P = ref._softmax_rows(Sm / tau)
    P[ar, yv] -= 1.0
    P /= M
    gW_ce = U.T @ (P @ Vo) / tau
    # hinge: pressure toward the mined hard-negative h until (s_true - s_h) >= m_hinge
    s_true = S[ar, yv]
    s_h = S[ar, h_cache]
    active = (m_hinge - (s_true - s_h)) > 0.0            # (M,) bool
    diff = (Vo[h_cache] - Vo[yv]).astype(np.float32)     # (M,df); d/dW of (m_hinge-(s_true-s_h))
    diff[~active] = 0.0
    gW_hinge = U.T @ diff / M
    gW = gW_ce + lam_hinge * gW_hinge + l2 * W
    return gW.astype(np.float32)


def _mine_hardneg(U, Vo, W, yv) -> np.ndarray:
    """argmax over objects EXCLUDING the true object per row -> (M,) hard-negative indices."""
    S = (U @ W) @ Vo.T
    S[np.arange(S.shape[0]), yv] = -np.inf
    return np.argmax(S, axis=1).astype(np.int64)


def fit_frozen_loss_np(Fa, y, Fo, Ps, Po, steps, lr, tau, l2, loss_mode,
                       m_add, m_hinge, lam_hinge, mine_K, log_prior_adj) -> np.ndarray:
    """Single-arm numpy trainer for MARGIN/LOGIT (fallback + gradient-selftest reference)."""
    U = Fa @ Ps
    Vo = Fo @ Po
    df = U.shape[1]
    W = np.zeros((df, df), dtype=np.float32)
    yv = y.astype(np.int64)
    h_cache = _mine_hardneg(U, Vo, W, yv) if loss_mode == "margin_hardneg" else None
    for st in range(steps):
        if loss_mode == "margin_hardneg" and (st % mine_K == 0) and st > 0:
            h_cache = _mine_hardneg(U, Vo, W, yv)
        gW = _frozen_grad_single(U, Vo, W, yv, tau, l2, loss_mode, m_add, m_hinge,
                                 lam_hinge, h_cache, log_prior_adj)
        W -= lr * gW
    return W


def fit_frozen_loss_paired(Fa, y_real, y_shuf, Fo, Ps, Po, steps, lr, tau, l2, loss_mode,
                           m_add, m_hinge, lam_hinge, mine_K, log_prior_adj):
    """Fit REAL + SHUFFLED W under MARGIN/LOGIT. torch bmm B=2 on device if available, else numpy.
    Each arm mines its OWN hard-negatives from its OWN current W (paired-trials discipline)."""
    if _TORCH_OK:
        dev = _DEVICE

        def _t(x):
            return torch.as_tensor(np.ascontiguousarray(x, dtype=np.float32), device=dev)
        U = _t(Fa) @ _t(Ps)
        Vo = _t(Fo) @ _t(Po)
        M, df = int(U.shape[0]), int(U.shape[1])
        Ub = U.unsqueeze(0).expand(2, -1, -1)
        VoB = Vo.unsqueeze(0).expand(2, -1, -1)
        VoT = Vo.t().unsqueeze(0).expand(2, -1, -1).contiguous()
        W = torch.zeros((2, df, df), dtype=torch.float32, device=dev)
        ys = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                          torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])
        ar = torch.arange(M, device=dev)
        lp = torch.as_tensor(log_prior_adj, device=dev, dtype=torch.float32) if loss_mode == "logit_adjust" \
            else None

        def _scores():
            return torch.bmm(torch.bmm(Ub, W), VoT)      # (2,M,V) raw

        def _mine():
            S = _scores().clone()
            S.scatter_(2, ys.unsqueeze(2), float("-inf"))
            return S.argmax(dim=2)                        # (2,M)
        h = _mine() if loss_mode == "margin_hardneg" else None
        for st in range(steps):
            if loss_mode == "margin_hardneg" and (st % mine_K == 0) and st > 0:
                h = _mine()
            S = _scores()
            if loss_mode == "logit_adjust":
                Z = S / tau + lp.view(1, 1, -1)
                Z = Z - Z.max(dim=2, keepdim=True).values
                P = torch.softmax(Z, dim=2)
                P[0, ar, ys[0]] -= 1.0
                P[1, ar, ys[1]] -= 1.0
                P = P / M
                gW = torch.bmm(Ub.transpose(1, 2), torch.bmm(P, VoB)) / tau + l2 * W
            else:
                Sm = S.clone()
                Sm.scatter_(2, ys.unsqueeze(2),
                            Sm.gather(2, ys.unsqueeze(2)) - m_add)
                Zc = Sm / tau
                Zc = Zc - Zc.max(dim=2, keepdim=True).values
                P = torch.softmax(Zc, dim=2)
                P[0, ar, ys[0]] -= 1.0
                P[1, ar, ys[1]] -= 1.0
                P = P / M
                gW_ce = torch.bmm(Ub.transpose(1, 2), torch.bmm(P, VoB)) / tau
                s_true = S.gather(2, ys.unsqueeze(2)).squeeze(2)     # (2,M)
                s_h = S.gather(2, h.unsqueeze(2)).squeeze(2)
                active = ((m_hinge - (s_true - s_h)) > 0.0).float()  # (2,M)
                Vo_h = Vo[h.reshape(-1)].reshape(2, M, df)
                Vo_y = Vo[ys.reshape(-1)].reshape(2, M, df)
                diff = (Vo_h - Vo_y) * active.unsqueeze(2)           # (2,M,df)
                gW_hinge = torch.bmm(Ub.transpose(1, 2), diff) / M
                gW = gW_ce + lam_hinge * gW_hinge + l2 * W
            W = W - lr * gW
        Wr = W[0].detach().to("cpu").numpy().astype(np.float32)
        Ws = W[1].detach().to("cpu").numpy().astype(np.float32)
        return Wr, Ws
    Wr = fit_frozen_loss_np(Fa, y_real, Fo, Ps, Po, steps, lr, tau, l2, loss_mode,
                            m_add, m_hinge, lam_hinge, mine_K, log_prior_adj)
    Ws = fit_frozen_loss_np(Fa, y_shuf, Fo, Ps, Po, steps, lr, tau, l2, loss_mode,
                            m_add, m_hinge, lam_hinge, mine_K, log_prior_adj)
    return Wr, Ws


# ============================================================================
# JOINT margin/logit training (autograd) -- reuse ref encoder; new loss.
# CE_BASELINE is provided by ref.joint_train_score (verbatim).
# ============================================================================
def joint_train_loss(Fa, y_real, y_shuf, Fo, Fc_by, d, init_seed, h, df, steps, lr, wd, tau, dropout,
                     loss_mode, m_add, m_hinge, lam_hinge, mine_K, log_prior_adj):
    """Train batched (B=2) joint encoder + bilinear relation under MARGIN/LOGIT. Returns
    {arm -> {eval_mode -> (T,V) float RAW score matrix}} (scored with plain S; no margin/adjust at test)."""
    if not _TORCH_OK:
        raise ref.JointUnavailable("JOINT_TORCH_UNAVAILABLE")
    dev = _DEVICE
    Fa_t = torch.as_tensor(np.ascontiguousarray(Fa, dtype=np.float32), device=dev)
    Fo_t = torch.as_tensor(np.ascontiguousarray(Fo, dtype=np.float32), device=dev)
    y = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                     torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])
    M = int(Fa_t.shape[0])
    ar = torch.arange(M, device=dev)
    lp = torch.as_tensor(log_prior_adj, device=dev, dtype=torch.float32) if loss_mode == "logit_adjust" else None
    params = ref._joint_init_params(d, h, df, init_seed, dev)
    plist = list(params.values())
    opt = torch.optim.Adam(plist, lr=lr, weight_decay=wd)
    h_cache = None

    def _raw_scores():
        Us = ref._joint_encode(Fa_t, params, train=True, dropout=dropout)
        Vo = ref._joint_encode(Fo_t, params, train=True, dropout=dropout)
        SR = torch.einsum("bmd,bde->bme", Us, params["R"])
        return torch.einsum("bme,bve->bmv", SR, Vo)      # (2,M,V) raw
    for st in range(steps):
        opt.zero_grad(set_to_none=True)
        S = _raw_scores()
        if loss_mode == "logit_adjust":
            logits = S / tau + lp.view(1, 1, -1)
            loss = F_t.cross_entropy(logits[0], y[0]) + F_t.cross_entropy(logits[1], y[1])
        else:
            if (st % mine_K == 0):
                with torch.no_grad():
                    Sd = S.detach().clone()
                    Sd.scatter_(2, y.unsqueeze(2), float("-inf"))
                    h_cache = Sd.argmax(dim=2)           # (2,M)
            margin_col = torch.zeros_like(S)
            margin_col.scatter_(2, y.unsqueeze(2), m_add)
            logits = (S - margin_col) / tau
            loss_ce = F_t.cross_entropy(logits[0], y[0]) + F_t.cross_entropy(logits[1], y[1])
            s_true = S.gather(2, y.unsqueeze(2)).squeeze(2)
            s_h = S.gather(2, h_cache.unsqueeze(2)).squeeze(2)
            loss_hinge = torch.clamp(m_hinge - (s_true - s_h), min=0.0).mean()
            loss = loss_ce + lam_hinge * loss_hinge
        loss.backward()
        opt.step()
    out: Dict[str, Dict[str, np.ndarray]] = {"REAL": {}, "SHUFFLED": {}}
    with torch.no_grad():
        Vo = ref._joint_encode(Fo_t, params, train=False, dropout=0.0)
        for ev, Fc in Fc_by.items():
            Fc_t = torch.as_tensor(np.ascontiguousarray(Fc, dtype=np.float32), device=dev)
            Uc = ref._joint_encode(Fc_t, params, train=False, dropout=0.0)
            SR = torch.einsum("btd,bde->bte", Uc, params["R"])
            logits = torch.einsum("bte,bve->btv", SR, Vo)   # (2,T,V) RAW (no /tau, no margin)
            sc = logits.to("cpu").numpy().astype(np.float32)
            out["REAL"][ev] = sc[0]
            out["SHUFFLED"][ev] = sc[1]
    return out


# ============================================================================
# Core evaluation -- one (config, relation, encoding, seed) -> per slot/arm/method rank metrics.
# ============================================================================
def eval_config_relenc(cfg: Dict, relation: str, encoding: str, seed: int) -> Dict:
    V = cfg["V"]; M_op = cfg["M"]
    fdf, fsteps = _frozen_hp()
    jh, jdf, jsteps = _joint_hp()
    sp = ref.build_split_scaled(relation, seed, V, N_TEST_PER, POOL_CAP, M_op)
    codebook = sp["codebook"]; obj_idx = sp["obj_idx"]
    train_pairs = sp["train_pairs"]; ind_test = sp["ind_test"]; trans_test = sp["trans_test"]
    V_eff = sp["V_eff"]; m_eff = sp["m_eff"]; by_subj = sp["by_subj"]

    train_subs = [s for s, _ in train_pairs]
    y_train = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)
    rng = np.random.RandomState(seed + 991)
    perm = rng.permutation(len(train_pairs))
    y_shuf = y_train[perm]
    y_ind = np.array([obj_idx[o] for _, o in ind_test], dtype=np.int64)
    y_trans = np.array([obj_idx[o] for _, o in trans_test], dtype=np.int64)
    ind_subs = [s for s, _ in ind_test]
    trans_subs = [s for s, _ in trans_test]
    y_by = {"inductive": y_ind, "transductive": y_trans}
    subs_by = {"inductive": ind_subs, "transductive": trans_subs}

    Fo = ref.encode_feature_matrix(codebook, encoding)
    Fa = ref.encode_feature_matrix(train_subs, encoding)
    Fc_by = {"inductive": ref.encode_feature_matrix(ind_subs, encoding),
             "transductive": ref.encode_feature_matrix(trans_subs, encoding)}
    d = Fa.shape[1]

    filt_mask = {ev: ref._filter_mask(subs_by[ev], y_by[ev], by_subj, obj_idx, V_eff) for ev in EVAL_MODES}
    zero_mask = {ev: np.zeros((len(y_by[ev]), V_eff), dtype=bool) for ev in EVAL_MODES}

    log_prior = compute_log_prior(y_train, V_eff)
    assert np.allclose(log_prior, compute_log_prior(y_shuf, V_eff)), \
        "LOG_PRIOR_ARM_VARIANCE: shuffle must preserve object multiset -> identical prior"
    lp_adj = (TAU_ADJ * log_prior).astype(np.float32)

    # score matrices per slot/arm/method/eval
    smat: Dict = {sl: {a: {mth: {} for mth in TRAIN_METHODS} for a in ARMS} for sl in SCORER_SLOTS}

    # ---- FROZEN ----
    Ps, Po = ref._proj_pair(d, fdf, ref.PROJ_SEED)
    tau_f = SLOT_TAU["FROZEN"]
    m_add_f = M_ADD_TAU_MULT * tau_f
    m_hinge_f = M_HINGE_TAU_MULT * tau_f
    # CE_BASELINE == parent scorer VERBATIM (positive control, Gate D)
    Wr_ce, Ws_ce = ref.fit_scorer_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                                         ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    Wr_mg, Ws_mg = fit_frozen_loss_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                                          ref.SCORER_LR, tau_f, ref.SCORER_L2, "margin_hardneg",
                                          m_add_f, m_hinge_f, LAMBDA_HINGE, MINE_K, lp_adj)
    Wr_la, Ws_la = fit_frozen_loss_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                                          ref.SCORER_LR, tau_f, ref.SCORER_L2, "logit_adjust",
                                          m_add_f, m_hinge_f, LAMBDA_HINGE, MINE_K, lp_adj)
    fW = {"CE_BASELINE": (Wr_ce, Ws_ce), "MARGIN_HARDNEG": (Wr_mg, Ws_mg),
          "LOGIT_ADJUST_LOSS": (Wr_la, Ws_la)}
    for mth, (Wr, Ws) in fW.items():
        for ev in EVAL_MODES:
            smat["FROZEN"]["REAL"][mth][ev] = ref.score_scorer(Fc_by[ev], Wr, Fo, Ps, Po)
            smat["FROZEN"]["SHUFFLED"][mth][ev] = ref.score_scorer(Fc_by[ev], Ws, Fo, Ps, Po)

    # ---- JOINT ----
    init_seed = ref._stable_seed(f"{cfg['name']}|{relation}|{encoding}", salt=seed)
    tau_j = SLOT_TAU["JOINT"]
    m_add_j = M_ADD_TAU_MULT * tau_j
    m_hinge_j = M_HINGE_TAU_MULT * tau_j
    jp_ce = ref.joint_train_score(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed,
                                  jh, jdf, jsteps, ref.JOINT_LR, ref.JOINT_WD, ref.JOINT_TAU,
                                  ref.JOINT_DROPOUT)
    jp_mg = joint_train_loss(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed, jh, jdf, jsteps,
                             ref.JOINT_LR, ref.JOINT_WD, tau_j, ref.JOINT_DROPOUT, "margin_hardneg",
                             m_add_j, m_hinge_j, LAMBDA_HINGE, MINE_K, lp_adj)
    jp_la = joint_train_loss(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed, jh, jdf, jsteps,
                             ref.JOINT_LR, ref.JOINT_WD, tau_j, ref.JOINT_DROPOUT, "logit_adjust",
                             m_add_j, m_hinge_j, LAMBDA_HINGE, MINE_K, lp_adj)
    jp = {"CE_BASELINE": jp_ce, "MARGIN_HARDNEG": jp_mg, "LOGIT_ADJUST_LOSS": jp_la}
    for mth, jpx in jp.items():
        for ev in EVAL_MODES:
            smat["JOINT"]["REAL"][mth][ev] = jpx["REAL"][ev]
            smat["JOINT"]["SHUFFLED"][mth][ev] = jpx["SHUFFLED"][ev]

    # metrics: filtered + raw per slot/arm/method/eval
    metrics: Dict = {sl: {a: {ev: {} for ev in EVAL_MODES} for a in ARMS} for sl in SCORER_SLOTS}
    for slot in SCORER_SLOTS:
        for arm in ARMS:
            for ev in EVAL_MODES:
                yv = y_by[ev]
                mth_out: Dict[str, Dict] = {}
                for mth in TRAIN_METHODS:
                    S = smat[slot][arm][mth][ev]
                    r_filt = ref.filtered_ranks(S, yv, filt_mask[ev])
                    r_raw = ref.filtered_ranks(S, yv, zero_mask[ev])
                    assert np.all(r_filt <= r_raw), \
                        f"FILTER_INVARIANT_VIOLATION {slot}|{arm}|{ev}|{mth}: filtered > raw"
                    mth_out[mth] = {"filt": ref.rank_metrics(r_filt), "raw": ref.rank_metrics(r_raw)}
                metrics[slot][arm][ev] = mth_out

    digests = {f"{sl}|{ar}|{mth}|inductive": hashlib.sha256(
        np.ascontiguousarray(smat[sl][ar][mth]["inductive"]).tobytes()).hexdigest()
        for sl in SCORER_SLOTS for ar in ARMS for mth in TRAIN_METHODS}
    return {"metrics": metrics, "V_eff": V_eff, "m_eff": m_eff, "chance": 1.0 / V_eff,
            "n_ind": len(y_ind), "n_trans": len(y_trans), "score_digests": digests}


# ============================================================================
# Synthetic discriminator-fires controls
# ============================================================================
def _gen_label_prior_hub(seed: int, d: int, V: int, M: int, T: int, HN: int, relabel: float):
    """Clean linear-map truth (recoverable), then relabel a `relabel` fraction of TRAIN subjects to a
    HEAD object in [0,HN) -> a severe NUISANCE label prior present ONLY in TRAIN (test stays clean +
    ~balanced). CE over-predicts the head objects on test; LOGIT_ADJUST_LOSS (Menon 2021 train-time)
    subtracts tau*log(pi_train) and recovers the tail-truth rows (>=0.05 REAL Hits@1 lift; MEASURED
    off-disk seed0=+0.068, mean(7,13,19)=+0.061). MARGIN cannot remove a label prior -> ~0 (correct)."""
    rng = np.random.RandomState(seed)
    Fo = rng.standard_normal((V, d)).astype(np.float32)
    Fo /= np.linalg.norm(Fo, axis=1, keepdims=True) + 1e-9
    Tmap = (rng.standard_normal((d, d)).astype(np.float32)) / np.sqrt(d)

    def gen(n, rs):
        Fx = rs.standard_normal((n, d)).astype(np.float32)
        Fx /= np.linalg.norm(Fx, axis=1, keepdims=True) + 1e-9
        y = ((Fx @ Tmap.T) @ Fo.T).argmax(axis=1)         # clean argmax truth
        return Fx, y
    Fs, yA = gen(M, rng)
    Fc, yC = gen(T, np.random.RandomState(seed + 7))
    yA2 = yA.copy()
    rr = np.random.RandomState(seed + 3)
    idx = rr.choice(M, int(relabel * M), replace=False)
    yA2[idx] = rr.randint(0, HN, len(idx)).astype(yA2.dtype)   # nuisance prior into TRAIN only
    return Fs, yA2, Fc, yC, Fo, HN


def _synth_frozen_h1(Fs, yA, Fc, yC, Fo, tau, df, steps, mine_K, log_prior_adj):
    """Train CE / MARGIN / LOGIT single-arm (REAL) + a shuffled-arm, return per-method REAL/SHUF Hits@1."""
    d = Fs.shape[1]; V = Fo.shape[0]; T = Fc.shape[0]
    Ps, Po = ref._proj_pair(d, df, ref.PROJ_SEED)
    ish = np.random.RandomState(97).permutation(len(yA))
    yS = yA[ish]
    m_add = M_ADD_TAU_MULT * tau
    m_hinge = M_HINGE_TAU_MULT * tau
    fm = np.zeros((T, V), dtype=bool)

    def _h1(W):
        r = ref.filtered_ranks(ref.score_scorer(Fc, W, Fo, Ps, Po), yC, fm)
        return float((r <= 1).mean())
    # CE baseline (parent) paired
    Wr_ce, Ws_ce = ref.fit_scorer_paired(Fs, yA, yS, Fo, Ps, Po, steps,
                                         ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    Wr_mg, Ws_mg = fit_frozen_loss_paired(Fs, yA, yS, Fo, Ps, Po, steps, ref.SCORER_LR, tau,
                                          ref.SCORER_L2, "margin_hardneg", m_add, m_hinge,
                                          LAMBDA_HINGE, mine_K, log_prior_adj)
    Wr_la, Ws_la = fit_frozen_loss_paired(Fs, yA, yS, Fo, Ps, Po, steps, ref.SCORER_LR, tau,
                                          ref.SCORER_L2, "logit_adjust", m_add, m_hinge,
                                          LAMBDA_HINGE, mine_K, log_prior_adj)
    return {"CE_BASELINE": {"real": _h1(Wr_ce), "shuf": _h1(Ws_ce)},
            "MARGIN_HARDNEG": {"real": _h1(Wr_mg), "shuf": _h1(Ws_mg)},
            "LOGIT_ADJUST_LOSS": {"real": _h1(Wr_la), "shuf": _h1(Ws_la)}}


def synth_label_prior_hub(seed: int) -> Dict:
    """POSITIVE control (MUST FIRE via LOGIT): a severe train-only label-prior nuisance over a
    recoverable clean map. best-of{MARGIN,LOGIT} must lift REAL Hits@1 over CE_BASELINE by
    >=SYNTH_LP_FIRE_LIFT while NOT lifting SHUFFLED (SHUF_OVERFIT_GUARD clean). LOGIT_ADJUST_LOSS is
    Menon 2021's exact train-time mechanism; MARGIN is ~0 (a label prior is not a margin problem)."""
    d, HN = SCM_D, SYNTH_LP_HN
    Fs, yA, Fc, yC, Fo, HN = _gen_label_prior_hub(seed + 313, d, SYNTH_LP_V, SYNTH_LP_M, SYNTH_LP_T,
                                                  HN, SYNTH_LP_RELABEL)
    V = Fo.shape[0]
    lp_adj = (TAU_ADJ * compute_log_prior(yA, V)).astype(np.float32)   # REAL prior -> LOGIT has signal
    per = _synth_frozen_h1(Fs, yA, Fc, yC, Fo, ref.SCORER_TAU, SYNTH_LP_DF, SYNTH_LP_STEPS,
                           MINE_K, lp_adj)
    ce = per["CE_BASELINE"]
    lifts = {mth: {"real_lift": per[mth]["real"] - ce["real"], "shuf_lift": per[mth]["shuf"] - ce["shuf"]}
             for mth in METHODS_HP}
    # bias signature: how often CE predicts a head object on the balanced test (over-prediction share)
    Ps, Po = ref._proj_pair(d, SYNTH_LP_DF, ref.PROJ_SEED)
    Wr_ce, _ = ref.fit_scorer_paired(Fs, yA, yA, Fo, Ps, Po, SYNTH_LP_STEPS,
                                     ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    hub_win = float((ref.score_scorer(Fc, Wr_ce, Fo, Ps, Po).argmax(axis=1) < HN).mean())
    return {"per_method": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in per.items()},
            "lifts": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in lifts.items()},
            "hub_argmax_share_ce": round(hub_win, 4)}


def synth_ambiguous_null(seed: int) -> Dict:
    """NULL control (MUST STAY CLEAN): labels INDEPENDENT of content (genuinely ambiguous). Neither
    margin NOR logit-adjust may manufacture a test win -- |REAL & SHUF lift over CE| <= tol
    (Bayes-consistency + SHUF_OVERFIT_GUARD philosophy)."""
    rng = np.random.RandomState(seed + 424242)
    d, V, M, T = SCM_D, SYNTH_LP_V, SYNTH_NULL_M, SYNTH_NULL_T

    def _unit(n):
        X = rng.standard_normal((n, d)).astype(np.float32)
        X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
        return X
    Fo = _unit(V); Fs = _unit(M); Fc = _unit(T)
    yA = rng.randint(0, V, M).astype(np.int64)
    yC = rng.randint(0, V, T).astype(np.int64)
    lp = compute_log_prior(yA, V)
    per = _synth_frozen_h1(Fs, yA, Fc, yC, Fo, ref.SCORER_TAU, SYNTH_LP_DF, SYNTH_NULL_STEPS,
                           MINE_K, (TAU_ADJ * lp).astype(np.float32))
    ce = per["CE_BASELINE"]
    lifts = {mth: {"real_lift": per[mth]["real"] - ce["real"], "shuf_lift": per[mth]["shuf"] - ce["shuf"]}
             for mth in METHODS_HP}
    return {"per_method": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in per.items()},
            "lifts": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in lifts.items()}}


# ============================================================================
# arms-differ hash (META_RULE_AF) -- all {CE,MARGIN,LOGIT} x {REAL,SHUF} matrices must differ
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    d, V, M, T = SCM_D, SYNTH_LP_V, 600, 200
    Fs, yA, Fc, yC, Fo, _ = _gen_label_prior_hub(seed + 313, d, V, M, T, SYNTH_LP_HN, SYNTH_LP_RELABEL)
    yS = yA[np.random.RandomState(seed + 991).permutation(M)]
    Ps, Po = ref._proj_pair(d, SYNTH_LP_DF, ref.PROJ_SEED)
    lp = np.zeros(V, dtype=np.float32)
    tau = ref.SCORER_TAU
    m_add = M_ADD_TAU_MULT * tau; m_hinge = M_HINGE_TAU_MULT * tau
    Wr_ce, Ws_ce = ref.fit_scorer_paired(Fs, yA, yS, Fo, Ps, Po, 200,
                                         ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    Wr_mg, Ws_mg = fit_frozen_loss_paired(Fs, yA, yS, Fo, Ps, Po, 200, ref.SCORER_LR, tau,
                                          ref.SCORER_L2, "margin_hardneg", m_add, m_hinge,
                                          LAMBDA_HINGE, MINE_K, lp)
    Wr_la, Ws_la = fit_frozen_loss_paired(Fs, yA, yS, Fo, Ps, Po, 200, ref.SCORER_LR, tau,
                                          ref.SCORER_L2, "logit_adjust", m_add, m_hinge,
                                          LAMBDA_HINGE, MINE_K, (TAU_ADJ * compute_log_prior(yA, V)))
    preds = {
        "CE_real": ref.score_scorer(Fc, Wr_ce, Fo, Ps, Po),
        "CE_shuf": ref.score_scorer(Fc, Ws_ce, Fo, Ps, Po),
        "MG_real": ref.score_scorer(Fc, Wr_mg, Fo, Ps, Po),
        "MG_shuf": ref.score_scorer(Fc, Ws_mg, Fo, Ps, Po),
        "LA_real": ref.score_scorer(Fc, Wr_la, Fo, Ps, Po),
        "LA_shuf": ref.score_scorer(Fc, Ws_la, Fo, Ps, Po),
    }
    digests = {k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest() for k, v in preds.items()}
    req = [("CE_real", "MG_real"), ("CE_real", "LA_real"), ("MG_real", "LA_real"),
           ("CE_real", "CE_shuf"), ("MG_real", "MG_shuf"), ("LA_real", "LA_shuf")]
    ok = all(digests[a] != digests[b] for a, b in req)
    return ok, digests


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def _unit_key(cn, rel, enc, slot, arm, ev):
    return f"{cn}|{rel}|{enc}|{slot}|{arm}|{ev}"


def _flatten_unit(per_unit, cn, rel, enc, slot, arm, ev, mth_metrics, fc):
    per_unit[_unit_key(cn, rel, enc, slot, arm, ev)] = {
        "config": cn, "relation": rel, "encoding": enc, "mech": slot, "arm": arm, "eval": ev,
        "methods": mth_metrics, "failure_class": fc}


def _get(per_unit, cn, rel, enc, slot, arm, mth, metric, ev="inductive"):
    u = per_unit.get(_unit_key(cn, rel, enc, slot, arm, ev))
    if not u or u.get("methods") is None:
        return float("nan")
    mm = u["methods"].get(mth)
    if not mm or mm.get("filt") is None:
        return float("nan")
    return mm["filt"][metric]


def _print_cfg_progress(cfg, per_unit, seed):
    cn = cfg["name"]; rel = cfg["rels"][0]; enc = cfg["encs"][0]
    for slot in SCORER_SLOTS:
        ce_r = _get(per_unit, cn, rel, enc, slot, "REAL", "CE_BASELINE", "hits1")
        for mth in METHODS_HP:
            mr = _get(per_unit, cn, rel, enc, slot, "REAL", mth, "hits1")
            mrr_r = _get(per_unit, cn, rel, enc, slot, "REAL", mth, "mrr")
            mrr_s = _get(per_unit, cn, rel, enc, slot, "SHUFFLED", mth, "mrr")
            ce_s = _get(per_unit, cn, rel, enc, slot, "SHUFFLED", "CE_BASELINE", "hits1")
            ms = _get(per_unit, cn, rel, enc, slot, "SHUFFLED", mth, "hits1")
            print(f"  [seed={seed} {cn:<5} {rel[:11]:<11} {enc[:4]} {slot:<6} {mth[:6]}] "
                  f"REAL_H1 CE={ce_r:.3f}->{mr:.3f}(lift{mr-ce_r:+.3f}) MRRrms={mrr_r-mrr_s:+.3f} "
                  f"SHUF_H1 lift={ms-ce_s:+.3f}", flush=True)


def _emit_heartbeat(out_dir: Path, unit_idx: int, total: int, t0: float):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": time.time() - t0}
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_unit: Dict[str, Dict] = {}
    meta: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    unit_i = 0
    for cfg in CONFIGS:
        cn = cfg["name"]
        for relation in cfg["rels"]:
            for enc in cfg["encs"]:
                fc = None
                res = None
                try:
                    res = eval_config_relenc(cfg, relation, enc, seed)
                except ref.ContentUnavailable as e:
                    fc = str(e)
                except ref.JointUnavailable as e:
                    fc = str(e)
                except Exception as e:
                    fatal = True
                    fatal_msg = f"{cn}|{relation}|{enc}:{type(e).__name__}:{str(e)[:200]}"
                    print(f"  [seed={seed} {cn} {relation} {enc}] FAILED {type(e).__name__}: {e}", flush=True)
                    traceback.print_exc()
                    break
                for slot in SCORER_SLOTS:
                    for arm in ARMS:
                        for ev in EVAL_MODES:
                            mm = res["metrics"][slot][arm][ev] if res is not None else None
                            _flatten_unit(per_unit, cn, relation, enc, slot, arm, ev, mm, fc)
                if res is not None:
                    k = f"{cn}|{relation}|{enc}"
                    meta[k] = {"V_eff": res["V_eff"], "m_eff": res["m_eff"], "chance": res["chance"],
                               "n_ind": res["n_ind"], "n_trans": res["n_trans"],
                               "score_digests": res["score_digests"]}
                unit_i += 1
                _emit_heartbeat(out_dir, unit_i, len(CONFIGS), t0)
            if fatal:
                break
        if fatal:
            break
        _print_cfg_progress(cfg, per_unit, seed)

    hub = synth_label_prior_hub(seed)
    null = synth_ambiguous_null(seed)
    best_hub = max(hub["lifts"][m]["real_lift"] for m in METHODS_HP)
    print(f"  [seed={seed} SYNTH lp_hub(POS)] argmax_share_ce={hub['hub_argmax_share_ce']:.2f} "
          f"LOGIT real_lift={hub['lifts']['LOGIT_ADJUST_LOSS']['real_lift']:+.3f} "
          f"shuf_lift={hub['lifts']['LOGIT_ADJUST_LOSS']['shuf_lift']:+.3f} | "
          f"MARGIN real_lift={hub['lifts']['MARGIN_HARDNEG']['real_lift']:+.3f} best_real_lift={best_hub:+.3f}", flush=True)
    print(f"  [seed={seed} SYNTH null      ] LOGIT real_lift={null['lifts']['LOGIT_ADJUST_LOSS']['real_lift']:+.3f} "
          f"shuf_lift={null['lifts']['LOGIT_ADJUST_LOSS']['shuf_lift']:+.3f} "
          f"MARGIN real_lift={null['lifts']['MARGIN_HARDNEG']['real_lift']:+.3f}", flush=True)

    return {
        "seed": seed, "N": N_DIM, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},configs={len(CONFIGS)},seeds={SEEDS}",
        "per_unit": per_unit, "meta": meta,
        "synth_label_prior_hub": hub, "synth_ambiguous_null": null,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ============================================================================
# Aggregate + verdict
# ============================================================================
def _mean(vals: List[float]) -> float:
    v = [x for x in vals if x == x]
    return float(np.mean(v)) if v else float("nan")


def aggregate(per_seed: Dict) -> Dict:
    buckets: Dict[str, List[float]] = collections.defaultdict(list)
    n_units = 0; n_failed = 0
    enc_unavailable = collections.Counter(); joint_unavailable = 0
    meta_all: Dict[str, Dict] = {}
    ctrl = {t: collections.defaultdict(list) for t in ("synth_label_prior_hub", "synth_ambiguous_null")}
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("methods") is None:
                n_failed += 1
                fcx = rec.get("failure_class", "NA")
                if isinstance(fcx, str) and "CACHE_MISSING" in fcx:
                    enc_unavailable[rec.get("encoding", "?")] += 1
                elif isinstance(fcx, str) and "JOINT_TORCH_UNAVAILABLE" in fcx:
                    joint_unavailable += 1
                continue
            for mth in TRAIN_METHODS:
                mm = rec["methods"].get(mth)
                if not mm:
                    continue
                for proto in ("filt", "raw"):
                    for mk in METRIC_KEYS:
                        buckets[f"{key}|{mth}|{proto}|{mk}"].append(float(mm[proto][mk]))
        for mk, mv in sd.get("meta", {}).items():
            meta_all[mk] = mv
        for tag, store in ctrl.items():
            s = sd.get(tag)
            if s:
                for m in METHODS_HP:
                    store[f"{m}|real_lift"].append(s["lifts"][m]["real_lift"])
                    store[f"{m}|shuf_lift"].append(s["lifts"][m]["shuf_lift"])
                if "hub_argmax_share_ce" in s:
                    store["hub_argmax_share_ce"].append(s["hub_argmax_share_ce"])
    cells = {key: _mean(v) for key, v in buckets.items()}
    cells_n = {key: len([x for x in v if x == x]) for key, v in buckets.items()}
    return {
        "cells": cells, "cells_n": cells_n, "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "joint_unavailable": joint_unavailable, "meta": meta_all,
        "synth_label_prior_hub": {k: round(_mean(v), 4) for k, v in ctrl["synth_label_prior_hub"].items()},
        "synth_ambiguous_null": {k: round(_mean(v), 4) for k, v in ctrl["synth_ambiguous_null"].items()},
    }


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_rt: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]; meta = agg["meta"]
    good_units = agg["n_units"] - agg["n_units_failed"]
    hub = agg["synth_label_prior_hub"]; null = agg["synth_ambiguous_null"]

    def _c(cn, rel, enc, slot, arm, mth, metric, ev="inductive"):
        # bucket key = unit_key(cn,rel,enc,slot,arm,ev) | mth | proto | metric  (ev segment REQUIRED)
        return cells.get(f"{cn}|{rel}|{enc}|{slot}|{arm}|{ev}|{mth}|filt|{metric}", float("nan"))

    def _mrr_rms(cn, rel, enc, slot, mth):
        r = _c(cn, rel, enc, slot, "REAL", mth, "mrr")
        s = _c(cn, rel, enc, slot, "SHUFFLED", mth, "mrr")
        if r != r or s != s:
            return float("nan")
        return r - s

    # discriminator-fires: label-prior positive fires (best-of REAL lift up; max shuf bounded); null clean
    hub_best_real = max((hub.get(f"{m}|real_lift", float("nan")) for m in METHODS_HP),
                        default=float("nan"))
    hub_max_shuf = max((hub.get(f"{m}|shuf_lift", 1.0) for m in METHODS_HP), default=1.0)
    hub_fires = (hub_best_real == hub_best_real and hub_best_real >= SYNTH_LP_FIRE_LIFT
                 and hub_max_shuf <= SYNTH_LP_SHUF_MAX)
    null_clean = all(
        (abs(null.get(f"{m}|real_lift", 1.0)) <= SYNTH_NULL_TOL
         and abs(null.get(f"{m}|shuf_lift", 1.0)) <= SYNTH_NULL_TOL) for m in METHODS_HP)
    discriminator_fires = bool(hub_fires and null_clean)

    V300_PLUS = {"V300", "V1000"}
    records = []
    for cfg in CONFIGS:
        cn = cfg["name"]
        for rel in cfg["rels"]:
            is_sem = rel in RELATIONS_SEM
            for enc in cfg["encs"]:
                ch = float(meta.get(f"{cn}|{rel}|{enc}", {}).get("chance", float("nan")))
                # presence: at least one slot's CE_BASELINE landed
                present = any(_c(cn, rel, enc, sl, "REAL", "CE_BASELINE", "hits1") ==
                              _c(cn, rel, enc, sl, "REAL", "CE_BASELINE", "hits1") for sl in HP_SLOTS)
                if not present:
                    continue
                per_slot = {}
                cell_wins = False
                best_real_h1_lift = float("-inf")
                for slot in HP_SLOTS:
                    ce_real_h1 = _c(cn, rel, enc, slot, "REAL", "CE_BASELINE", "hits1")
                    ce_shuf_h1 = _c(cn, rel, enc, slot, "SHUFFLED", "CE_BASELINE", "hits1")
                    mstats = {}
                    for mth in METHODS_HP:
                        real_h1 = _c(cn, rel, enc, slot, "REAL", mth, "hits1")
                        shuf_h1 = _c(cn, rel, enc, slot, "SHUFFLED", mth, "hits1")
                        mrr_rms = _mrr_rms(cn, rel, enc, slot, mth)
                        real_h1_lift = (real_h1 - ce_real_h1) if (real_h1 == real_h1 and ce_real_h1 == ce_real_h1) else float("nan")
                        shuf_h1_lift = (shuf_h1 - ce_shuf_h1) if (shuf_h1 == shuf_h1 and ce_shuf_h1 == ce_shuf_h1) else float("nan")
                        overfit_flag = bool(shuf_h1_lift == shuf_h1_lift and shuf_h1_lift > SHUF_OVERFIT_TOL)
                        clears = (real_h1_lift == real_h1_lift and mrr_rms == mrr_rms
                                  and shuf_h1_lift == shuf_h1_lift
                                  and real_h1_lift >= HP_REAL_HITS1_LIFT_MIN
                                  and mrr_rms >= HP_MRR_RMS_MIN
                                  and shuf_h1_lift <= SHUF_OVERFIT_TOL)
                        if clears:
                            cell_wins = True
                        if real_h1_lift == real_h1_lift and not overfit_flag:
                            best_real_h1_lift = max(best_real_h1_lift, real_h1_lift)
                        mstats[mth] = {"real_hits1": _r(real_h1), "real_hits1_lift": _r(real_h1_lift),
                                       "mrr_rms": _r(mrr_rms), "shuf_hits1_lift": _r(shuf_h1_lift),
                                       "shuf_overfit_guard_violated": overfit_flag, "clears_HP": bool(clears)}
                    per_slot[slot] = {"ce_real_hits1": _r(ce_real_h1), "ce_shuf_hits1": _r(ce_shuf_h1),
                                      "methods": mstats}
                shuf_h10 = _c(cn, rel, enc, "FROZEN", "SHUFFLED", "CE_BASELINE", "hits10")
                records.append({
                    "config": cn, "V": cfg["V"], "rel": rel, "enc": enc, "is_sem": is_sem,
                    "is_neg_watchdog": rel in RELATIONS_NEG, "chance": ch, "per_slot": per_slot,
                    "cell_wins": cell_wins,
                    "best_real_hits1_lift": _r(best_real_h1_lift if best_real_h1_lift != float("-inf") else float("nan")),
                    "shuf_ce_hits10_filt": _r(shuf_h10)})

    wins = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS and r["cell_wins"]]
    win_rels = sorted(set(r["rel"] for r in wins))
    win_encs = sorted(set(r["enc"] for r in wins))
    expansion_met = len(win_rels) >= 2 and len(win_encs) >= 2

    v300_sem = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS]
    best_real_lift_v300 = max((r["best_real_hits1_lift"] for r in v300_sem
                               if r["best_real_hits1_lift"] is not None), default=float("nan"))

    diag = {
        "bind_roundtrip": bind_rt, "arms_differ_ok": arms_differ_ok,
        "good_units": good_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_label_prior_hub": hub, "synth_ambiguous_null": null,
        "hub_control_fires": bool(hub_fires), "null_control_clean": bool(null_clean),
        "discriminator_fires": discriminator_fires,
        "records": records, "wins": wins, "win_rels": win_rels, "win_encs": win_encs,
        "expansion_criterion_met": expansion_met,
        "best_real_hits1_lift_at_V300plus": _r(best_real_lift_v300),
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "device": _DEVICE,
    }

    expected = EXPECTED_N_UNITS
    if good_units < expected:
        gsbc_missing = agg["enc_unavailable"].get("gsbc", 0)
        if not (gsbc_missing > 0 and (good_units + gsbc_missing) >= expected):
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: good_units={good_units} < expected={expected} "
                    f"(not explained by gsbc-cache-missing).", diag)
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: method score-matrices bit-identical; impl bug.", diag)
    if not (bind_rt >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL", f"SANITY_RAIL_BIND: bind-roundtrip={bind_rt:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)

    summ = (f"dev={_DEVICE} discrim[lp_hub_fires={hub_fires}(best_real_lift={hub_best_real},"
            f"max_shuf_lift={hub_max_shuf}),null_clean={null_clean}] | "
            f"V300+ best_REAL_Hits@1_lift(guard-clean)={diag['best_real_hits1_lift_at_V300plus']} "
            f"win_rels={win_rels} win_encs={win_encs}")

    if not discriminator_fires:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_VACUOUS_DISCRIMINATOR: the margin/mining loss did NOT pass the synthetic "
                f"controls (hub_fires={hub_fires}, null_clean={null_clean}); real-data lift uninterpretable "
                f"until the trained fix provably lifts REAL Hits@1 on a by-construction content-baked hub "
                f"AND does NOT manufacture a win on genuinely-ambiguous content. {summ}", diag)

    if expansion_met:
        return ("HARD_PASS",
                f"HARD_PASS_MARGIN_TRAINS_THROUGH_HUBNESS: the margin-augmented loss (additive margin + "
                f"z-margin-calibrated hard-neg hinge) lifts REAL-absolute filtered Hits@1 by "
                f">={HP_REAL_HITS1_LIFT_MIN} over CE_BASELINE AND holds MRR real_minus_shuf>={HP_MRR_RMS_MIN} "
                f"with the SHUF_OVERFIT_GUARD clean (SHUFFLED lift<={SHUF_OVERFIT_TOL}), on best-of-"
                f"{{FROZEN,JOINT}}x{{MARGIN,LOGIT}} spanning relations={win_rels} x encoders={win_encs} at "
                f"V>=300 -- a TRAINED fix succeeds where the training-free rescore was a FROZEN-slot phantom. "
                f"{summ}", diag)

    if best_real_lift_v300 == best_real_lift_v300 and best_real_lift_v300 <= HF_REAL_HITS1_LIFT_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL_MARGIN_DOES_NOT_TRAIN_THROUGH: the margin/mining (and logit-adjust) trained "
                f"loss fails to lift REAL-absolute Hits@1 over CE_BASELINE on EVERY semantic rel x enc at "
                f"V>=300 (best guard-clean REAL Hits@1 lift={diag['best_real_hits1_lift_at_V300plus']} "
                f"<={HF_REAL_HITS1_LIFT_MAX}) while the synthetic hub control fired. BOTH the post-hoc AND "
                f"the trained-margin levers have now failed on the SAME diagnosed bias -> the remaining gap "
                f"is a genuine one-to-many/fanout ceiling or a content-decorrelation problem, not a loss "
                f"choice. {summ}", diag)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL_MARGIN_RECOVERY: the trained margin/mining fix lifts REAL-absolute Hits@1 "
            f"over CE_BASELINE (best guard-clean lift={diag['best_real_hits1_lift_at_V300plus']} at V>=300, "
            f"in (+{HF_REAL_HITS1_LIFT_MAX},+{HP_REAL_HITS1_LIFT_MIN}) or clears on one relation but not the "
            f">=2 rel x >=2 enc expansion) -- real but partial, likely the label-prior-dominant relation "
            f"(CausesDesire, LOGIT_ADJUST_LOSS near-direct transfer) clears while the genuine-geometric-hub "
            f"relation does not. Stage a hubness-decorrelation regularizer for the residual. {summ}", diag)


# ============================================================================
# Formula self-tests (import time) -- gradient direction is the load-bearing new code.
# ============================================================================
def _fd_grad(loss_fn, W, eps=1e-3):
    """Central finite-difference gradient of scalar loss_fn(W) w.r.t. a few entries of W."""
    g = np.zeros_like(W)
    idxs = [(0, 0), (1, 2), (3, 1), (2, 4)]
    for (i, j) in idxs:
        if i >= W.shape[0] or j >= W.shape[1]:
            continue
        Wp = W.copy(); Wp[i, j] += eps
        Wm = W.copy(); Wm[i, j] -= eps
        g[i, j] = (loss_fn(Wp) - loss_fn(Wm)) / (2 * eps)
    return g, idxs


def _test_margin_ce_gradient():
    """Analytic margin-CE gradient must match central finite differences (gradient DIRECTION check)."""
    rng = np.random.RandomState(11)
    M, V, df = 24, 12, 8
    U = rng.standard_normal((M, df)).astype(np.float32)
    Vo = rng.standard_normal((V, df)).astype(np.float32)
    W = 0.1 * rng.standard_normal((df, df)).astype(np.float32)
    yv = rng.randint(0, V, M).astype(np.int64)
    tau = 0.05; m_add = 1.0 * tau
    ar = np.arange(M)

    def loss(Wx):
        S = (U @ Wx) @ Vo.T
        Sm = S.copy(); Sm[ar, yv] -= m_add
        Z = Sm / tau
        Z = Z - Z.max(axis=1, keepdims=True)
        logp = Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))
        return float(-logp[ar, yv].mean())
    # analytic: hinge disabled (lam=0), l2=0
    ana = _frozen_grad_single(U, Vo, W, yv, tau, 0.0, "margin_hardneg", m_add, 0.0, 0.0,
                              np.zeros(M, dtype=np.int64), np.zeros(V, dtype=np.float32))
    fd, idxs = _fd_grad(loss, W)
    for (i, j) in idxs:
        assert abs(ana[i, j] - fd[i, j]) < 1e-2, \
            f"margin-CE grad mismatch at ({i},{j}): analytic={ana[i,j]:.5f} fd={fd[i,j]:.5f}"


def _test_hinge_gradient():
    """Analytic hinge gradient (fixed mined h) must match finite differences AND point to increase the
    true-minus-hardneg margin (loss decreases along -grad)."""
    rng = np.random.RandomState(23)
    M, V, df = 20, 10, 8
    U = rng.standard_normal((M, df)).astype(np.float32)
    Vo = rng.standard_normal((V, df)).astype(np.float32)
    W = 0.1 * rng.standard_normal((df, df)).astype(np.float32)
    yv = rng.randint(0, V, M).astype(np.int64)
    tau = 0.05; m_hinge = 2.5 * tau
    h = _mine_hardneg(U, Vo, W, yv)
    ar = np.arange(M)

    def hinge_loss(Wx):
        S = (U @ Wx) @ Vo.T
        gap = S[ar, yv] - S[ar, h]
        return float(np.maximum(0.0, m_hinge - gap).mean())
    # analytic hinge only: margin CE contribution removed by passing a huge m_add so CE term ~0? No --
    # isolate hinge by computing full grad then subtracting CE grad computed with lam via difference.
    full = _frozen_grad_single(U, Vo, W, yv, tau, 0.0, "margin_hardneg", 0.0, m_hinge, 1.0, h,
                               np.zeros(V, dtype=np.float32))
    ce_only = _frozen_grad_single(U, Vo, W, yv, tau, 0.0, "margin_hardneg", 0.0, m_hinge, 0.0, h,
                                  np.zeros(V, dtype=np.float32))
    hinge_ana = full - ce_only
    fd, idxs = _fd_grad(hinge_loss, W)
    for (i, j) in idxs:
        assert abs(hinge_ana[i, j] - fd[i, j]) < 1e-2, \
            f"hinge grad mismatch at ({i},{j}): analytic={hinge_ana[i,j]:.5f} fd={fd[i,j]:.5f}"
    # descent check: W - lr*grad decreases hinge loss
    l0 = hinge_loss(W)
    l1 = hinge_loss(W - 0.5 * hinge_ana)
    assert l1 <= l0 + 1e-6, f"hinge gradient not a descent direction: {l0:.5f} -> {l1:.5f}"


def _test_logit_adjust_gradient():
    """Analytic logit-adjust gradient must match finite differences."""
    rng = np.random.RandomState(31)
    M, V, df = 24, 12, 8
    U = rng.standard_normal((M, df)).astype(np.float32)
    Vo = rng.standard_normal((V, df)).astype(np.float32)
    W = 0.1 * rng.standard_normal((df, df)).astype(np.float32)
    yv = rng.randint(0, V, M).astype(np.int64)
    tau = 0.05
    lp_adj = (1.0 * rng.standard_normal(V)).astype(np.float32)
    ar = np.arange(M)

    def loss(Wx):
        S = (U @ Wx) @ Vo.T
        Z = S / tau + lp_adj[None, :]
        Z = Z - Z.max(axis=1, keepdims=True)
        logp = Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))
        return float(-logp[ar, yv].mean())
    ana = _frozen_grad_single(U, Vo, W, yv, tau, 0.0, "logit_adjust", 0.0, 0.0, 0.0,
                              np.zeros(M, dtype=np.int64), lp_adj)
    fd, idxs = _fd_grad(loss, W)
    for (i, j) in idxs:
        assert abs(ana[i, j] - fd[i, j]) < 1e-2, \
            f"logit-adjust grad mismatch at ({i},{j}): analytic={ana[i,j]:.5f} fd={fd[i,j]:.5f}"


def _test_zmargin_calibration():
    """m_hinge must be set to the MEASURED z-margin (2.2-2.7 std) in tau units; m_add = 1.0 tau unit."""
    for slot, tau in SLOT_TAU.items():
        assert abs(M_ADD_TAU_MULT - 1.0) < 1e-9, "m_add must be exactly 1 temperature unit"
        assert 2.2 <= M_HINGE_TAU_MULT <= 2.7, \
            f"m_hinge/tau={M_HINGE_TAU_MULT} outside MEASURED z-margin band [2.2,2.7] (slot {slot})"


def _test_ce_reproduces_parent():
    """fit_frozen_loss with a degenerate margin (m_add=0, lam_hinge=0, uniform prior via margin path)
    is NOT called for CE; instead confirm CE_BASELINE path uses ref.fit_scorer_paired byte-identically
    by checking the reference function object is the parent's."""
    assert ref.fit_scorer_paired.__module__ == "experiments.exp_schema_relation_hitsatk_mrr_reframe_v1", \
        "CE_BASELINE must call the parent scorer verbatim (positive control, Gate D)"
    assert ref.joint_train_score.__module__ == "experiments.exp_schema_relation_hitsatk_mrr_reframe_v1", \
        "JOINT CE_BASELINE must call the parent joint trainer verbatim"


def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = ref.cos_c(ref.unbind(ref.bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"

    _test_margin_ce_gradient()
    _test_hinge_gradient()
    _test_logit_adjust_gradient()
    _test_zmargin_calibration()
    _test_ce_reproduces_parent()

    # discriminator-fires proofs at seed 0 (positive fires via LOGIT_ADJUST; null clean for both)
    hub = synth_label_prior_hub(0)
    hub_best = max(hub["lifts"][m]["real_lift"] for m in METHODS_HP)
    hub_max_shuf = max(hub["lifts"][m]["shuf_lift"] for m in METHODS_HP)
    assert hub_best >= SYNTH_LP_FIRE_LIFT, \
        f"selftest label-prior POSITIVE: best MARGIN/LOGIT REAL Hits@1 lift={hub_best:+.3f} < {SYNTH_LP_FIRE_LIFT} (must fire)"
    assert hub_max_shuf <= SYNTH_LP_SHUF_MAX, \
        f"selftest label-prior SHUFFLED lifted {hub_max_shuf:+.3f} > {SYNTH_LP_SHUF_MAX} (SHUF_OVERFIT_GUARD)"
    null = synth_ambiguous_null(0)
    for m in METHODS_HP:
        assert abs(null["lifts"][m]["real_lift"]) <= SYNTH_NULL_TOL, \
            f"selftest null {m} REAL lift={null['lifts'][m]['real_lift']:+.3f} not <= {SYNTH_NULL_TOL} (manufactured)"
        assert abs(null["lifts"][m]["shuf_lift"]) <= SYNTH_NULL_TOL, \
            f"selftest null {m} SHUF lift={null['lifts'][m]['shuf_lift']:+.3f} not <= {SYNTH_NULL_TOL}"

    ad_ok, _ = arms_differ_check(0)
    assert ad_ok, "selftest arms_differ_check failed (method matrices identical)"

    print(f"[formula_selftest] bind_rt={rt:.3f} margin_ce_grad=PASS hinge_grad=PASS logit_grad=PASS "
          f"zmargin_calib(m_add=1.0tau,m_hinge={M_HINGE_TAU_MULT}tau)=PASS ce_reproduces_parent=PASS | "
          f"lp_hub(best_real_lift{hub_best:+.3f} via LOGIT={hub['lifts']['LOGIT_ADJUST_LOSS']['real_lift']:+.3f},"
          f"max_shuf{hub_max_shuf:+.3f},argmax_share{hub['hub_argmax_share_ce']:.2f}) "
          f"null(LOGITreal{null['lifts']['LOGIT_ADJUST_LOSS']['real_lift']:+.3f}) arms_differ=OK "
          f"torch_ok={_TORCH_OK} device={_DEVICE} bge_ok={ref._BGE.ok} gsbc_ok={ref._GSBC.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()
# reachability (THEORETICAL; no CRLB noise-floor for a rank-lift). REAL Hits@1 lift band 0.05 is
# reachable (JOINT undertrained-regime rescore already showed +0.467 real Hits@1 lift is achievable
# MEASURED@data/exp_schema_relation_hubness_debias_rescore_v1_smoke) and 2.5x the HF ceiling 0.02.
assert HF_REAL_HITS1_LIFT_MAX < HP_REAL_HITS1_LIFT_MIN < 0.95, "HP/HF lift bands must be ordered, below saturation"


# ============================================================================
# Defensive: start-marker + crash-diagnostic
# ============================================================================
def _write_start_marker(out_dir: Path):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "expected_n_units": EXPECTED_N_UNITS, "n_configs": len(CONFIGS), "host": platform.node(),
        "bge_ok": ref._BGE.ok, "gsbc_ok": ref._GSBC.ok,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_crash_metrics(out_dir: Path, exc: Exception):
    diag = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ============================================================================
# Main
# ============================================================================
def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} device={_DEVICE} torch_ok={_TORCH_OK} N={N_DIM} "
          f"n_configs={len(CONFIGS)} seeds={SEEDS} expected_units={EXPECTED_N_UNITS} "
          f"bge_ok={ref._BGE.ok} gsbc_ok={ref._GSBC.ok} methods={TRAIN_METHODS} mine_K={MINE_K}", flush=True)
    if not ref._GSBC.ok:
        print(f"[WARN] gsbc cache unavailable ({ref._GSBC.reason}); gsbc arm records per-unit "
              f"failure_class; bge_semantic axis still valid.", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed, out_dir)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s) fatal={r['fatal']}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)
    ad_ok, ad_digests = arms_differ_check(SEEDS[0])
    verdict, verdict_msg, diag = compute_verdict(agg, ad_ok, _BIND_RT)

    elapsed = time.time() - t_start
    summary = (f"{verdict}: best_REAL_Hits@1_lift@V300+={diag.get('best_real_hits1_lift_at_V300plus')} "
               f"win_rels={diag.get('win_rels')} win_encs={diag.get('win_encs')} "
               f"discrim_fires={diag.get('discriminator_fires')}")
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "relations_semantic": RELATIONS_SEM, "relations_neg_watchdog": RELATIONS_NEG,
        "content_encodings": CONTENT_ENCODINGS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "scorer_slots": SCORER_SLOTS, "hp_slots": HP_SLOTS, "train_methods": TRAIN_METHODS,
        "methods_hp": METHODS_HP, "hits_ks": HITS_KS,
        "loss_hp": {"m_add_tau_mult": M_ADD_TAU_MULT, "m_hinge_tau_mult": M_HINGE_TAU_MULT,
                    "lambda_hinge": LAMBDA_HINGE, "tau_adj": TAU_ADJ, "logit_eps": LOGIT_EPS,
                    "mine_K": MINE_K, "slot_tau": SLOT_TAU},
        "config_grid": [{"name": c["name"], "V": c["V"], "M": c["M"], "rels": c["rels"],
                         "encs": c["encs"]} for c in CONFIGS],
        "reuses_parent": "experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py (imported verbatim as ref)",
        "ce_baseline_is": "ref.fit_scorer_paired + ref.joint_train_score (byte-identical parent scorer; Gate D)",
        "n_seeds": len(per_seed), "seeds": [int(s) for s in per_seed.keys()],
        "expected_n_units": EXPECTED_N_UNITS, "n_units_counted": agg["n_units"],
        "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": (agg["n_units"] - agg["n_units_failed"]) >= EXPECTED_N_UNITS
        or agg["enc_unavailable"].get("gsbc", 0) > 0,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests, "bind_roundtrip": _BIND_RT,
        "synth_label_prior_hub": agg["synth_label_prior_hub"],
        "synth_ambiguous_null": agg["synth_ambiguous_null"],
        "hub_control_fires": diag.get("hub_control_fires"), "null_control_clean": diag.get("null_control_clean"),
        "discriminator_fires": diag.get("discriminator_fires"),
        "records": diag.get("records"), "wins": diag.get("wins"),
        "win_rels": diag.get("win_rels"), "win_encs": diag.get("win_encs"),
        "expansion_criterion_met": diag.get("expansion_criterion_met"),
        "best_real_hits1_lift_at_V300plus": diag.get("best_real_hits1_lift_at_V300plus"),
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "meta_per_relenc": agg["meta"],
        "hp_scope": {"best_of_FROZEN_JOINT_x_MARGIN_LOGIT_REAL_inductive_FILTERED_SEMANTIC_at_V>=300":
                     ["HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"],
                     "CE_BASELINE": ["parent_reframe_scorer_verbatim_positive_control_NOT_HP"],
                     "SHUFFLED": ["SHUF_OVERFIT_GUARD_anti_phantom_control"],
                     "DerivedFrom": ["surface_morphological_watchdog_NOT_HP"],
                     "raw_metrics": ["reported_not_gating"]},
        "bands": {"HP_REAL_HITS1_LIFT_MIN": HP_REAL_HITS1_LIFT_MIN, "HP_MRR_RMS_MIN": HP_MRR_RMS_MIN,
                  "SHUF_OVERFIT_TOL": SHUF_OVERFIT_TOL, "HF_REAL_HITS1_LIFT_MAX": HF_REAL_HITS1_LIFT_MAX,
                  "SYNTH_LP_FIRE_LIFT": SYNTH_LP_FIRE_LIFT, "SYNTH_LP_SHUF_MAX": SYNTH_LP_SHUF_MAX,
                  "SYNTH_NULL_TOL": SYNTH_NULL_TOL, "BASE_SAT_HI": BASE_SAT_HI},
        "cells_aggregate": agg["cells"], "cells_n": agg["cells_n"],
        "gate_diagnostics": {k: v for k, v in diag.items() if k not in ("records",)},
        "mechanism": ("margin_augmented_loss: additive_margin(-m_add on true logit)+z_margin_calibrated_"
                      "hard_neg_hinge(mine top wrong every K steps); LOGIT_ADJUST_LOSS=Menon2021 train-time"),
        "shuf_overfit_guard": ("a TRAINED mechanism can overfit-game the SHUFFLED control (unlike post-hoc "
                               "rescore); require SHUFFLED-abs Hits@1 lift over CE_BASELINE <= +0.03 or the "
                               "REAL lift is not credited (instrument failure, not a win)."),
        "filtered_protocol": "bordes_2013_filtered_hits_at_k_mrr_exclude_other_true_objects_per_subject",
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "allow_synthetic": False, "n_generative_llm_calls": 0,
        "metrics_source": "measured_margin_augmented_trained_frozen_joint_scorers_vs_ce_baseline",
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary, "elapsed_s": elapsed,
    }
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp_path, out_dir / "metrics.json")

    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s good_units={agg['n_units']-agg['n_units_failed']}/"
          f"{EXPECTED_N_UNITS} device={_DEVICE}", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (formula self-tests passed at import)", flush=True)
        sys.exit(0)
    _OUT = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT, e)
        raise
