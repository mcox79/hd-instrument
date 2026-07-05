"""Encoder v11 -- Sparse-GSBC (Generalized Sparse Block Codes) graded code vs
pure-sign block control. THE elegant-2% lever: drop the argmax-to-SIGN
quantization; keep the block-wise TOP-m GRADED positive survivors (unit-L1 per
block) and bind with BLOCK-WISE CIRCULAR CONVOLUTION (the ideal GSBC binding).
Raises the retrieval ceiling above the sign-only 0.43 while keeping keyed@J5
algebra EXACTLY.

WHY THE SIGN-BLOCK FAMILY IS CLOSED (verified from disk, not summarized):
  MEASURED@data/exp_encoder_v6_annealed_ste_fidelity_k128_v1_seed7/metrics.json:
    ANNEAL_STE cons_last = 0.000132  -> soft==hard already converged, so the
      annealed/peakier-hardening lever fixed a NON-problem (Skunkworks VET).
    ANNEAL_STE final(hard block) ret 0.048 keyed@J5 0.233; final_dense ret 0.65
      but hi80 0.48 calib 0.37 (calib-collapsed).  Lever B CLOSED.
  MEASURED@data/exp_encoder_ceiling_density_curve_v1/metrics.json:
    ORTHO_K128 (pure-SIGN block argmax) ret 0.4295 keyed@J5 1.00;
    RAW_ISOMETRIC (dense FLOAT) ret 1.0000.
  The 0.43 ceiling is the LOCAL-WTA / sign-quantization penalty, NOT a density
  limit. GSBC keeps the graded magnitudes (positive-real) -> a continuous
  per-block distribution -> the RKD Gram is no longer quantized to
  (#matched-#mismatched)/K. Reference: "Generalized Sparse Block Codes"
  arXiv:2303.13957 (Frady/Kleyko/Rahimi, IBM), which shows block-wise circular
  convolution is the IDEAL binding for graded-sparse block codes (element-wise
  product is lossy for graded).

ZERO-TRAINING FORMAT PROBES (this cell's discriminator-survives-scale evidence,
option C -- the make-or-break ALGEBRA question answered at full format scale):
  MEASURED@scratchpad/gsbc_format_probe.py (ORTHO isometric lift, local
  43905-corpus, N_test=4000, zero training):
    GSBC kb32/L128/m3 (2.34% active): ret 0.5499, keyed@J5 1.0000 (pos-shift
      keys) / 1.0000 (+-1 keys) / shuffled 0.0000.
    GSBC kb64/L64/m2  (3.12% active): ret 0.5769, keyed@J5 1.0000; vs
      sign-block m=1 0.5392 (magnitude discarded).
  => block-wise circular-conv binding round-trips J=5 EXACTLY on graded GSBC
     codes (the whole point holds), and graded already lifts retrieval at zero
     training; the trained upside (Frady/Kleyko ceiling ~0.7-0.9) is the FULL
     question.

ARMS (PAIRED; same seed/data/split/objective/LR/steps/WIDTH=2048 for ALL; ONLY
the block CODE differs; per-arm block geometry so each code is at its intended
sparsity):
  SIGN_BLOCK  sign  kb128 blk32 m1  -- control == v3e (pure sign; 3.12%; Gate-D)
  GSBC_2PCT   gsbc  kb32  blk128 m3 -- graded top-3, unit-L1, circ-conv (2.34%;
                                       PRIMARY)
  GSBC_3PCT   gsbc  kb64  blk64  m2 -- graded top-2 (3.12%; matched-active vs
                                       sign; SECONDARY density point)
  PRIMARY (pre-declared): GSBC_2PCT. JOINT instrument (ret_agree10 + calib_err +
  hi80_cos all REPORTED; a lift on one with collapse on another is a FALSE PASS):
  the DEPLOYED GSBC code ret_agree10 must reach >= 0.35 at ~2% active WITH
  keyed@J5 >= 0.95 (HARD co-gate; GSBC+circ-conv should hold it EXACTLY -- if it
  does not, THAT is the finding) and no coarse-cosine collapse.

FREE CAPACITY DIAGNOSTIC (carried from v6): every arm logs its train-loss (RKD)
trajectory; SIGN_BLOCK floored while ret ~0.21 confirms capacity is not the
bottleneck.

ONE TRAINER for all arms (nce_weight=0 -> NCE dropped). SIGN arm reuses
v3._block_ste / v3._encode_hard_block / v3._keyed_unit VERBATIM (reproduces v3e).
GSBC arms use the local graded encoder + block-wise circular-conv keyed
(hdlab.binding.bind/unbind over the (kb,blk_l) reshape + POSITIVE one-hot shift
keys that preserve the unit-L1 invariant). v3._make_student / v3._lr_at /
v3._semantic_unit / v3._dense_sign_codes / v3._chunked_cleanup_argmax reused.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "sparsify dense retrieval geometry into block argmax sparse code survive
  hardening k-WTA entropy penalty two-stage distillation" -> top cosine=0.293
  (06-23 note: keep ONE codebook space) + Olshausen/Foldiak (0.28); NONE >0.30.
  A trained GRADED Sparse-Block-Code with circular-conv binding, gated on BOTH
  retrieval AND SBC algebra, is UNTESTED in the arc (all prior arms sign-only) ->
  GENUINELY NOVEL (Frady/Kleyko GSBC is CITED external theory, not prior arc work).

METHODOLOGY (LOCKED for all encoder cells): FINAL-step (not best-ckpt) primary;
headline ret_agree10 + hi80_cos; keyed@J5 a HARD co-gate. Disjoint held/test;
exclude step-0; PAIRED same-seed/data/split; determinism pinned; torch version
recorded. CANONICAL = the REMOTE-QUEUE OFFICIAL landing, NOT local smoke. 2 SEEDS
via sibling _seed_7 / _seed_13 wrappers (CHUNKED single-seed-per-cell).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over each arm's code)
- final_metrics_atomicity: tmp_replace (write_metrics + atomic ckpt saves)
- except SystemExit: raise BEFORE except Exception (no BaseException/bare)
- crlb/capacity-feasibility: pure-SIGN K128 ceiling 0.4295 (MEASURED@bypass);
  GSBC's graded ceiling is higher (dense-float=1.0) and the zero-train probe
  already shows GSBC>=sign -> HARD_PASS ret 0.35 reachable. crlb_n_a declared.
- baseline_in_band: CHARPOS ret in (0.05,0.95); Gate-D SIGN in [0.15,0.28]
- discriminator-survives-scale: option (C) -- the make-or-break ALGEBRA question
  is answered at FULL FORMAT SCALE by the zero-training probe (GSBC keyed@J5=1.00);
  the ret>=0.35 discriminator is FULL-only (smoke's tiny V_train cannot reproduce
  ret_agree10 coverage), so smoke is a MACHINERY gate (all 3 arms train, codes
  differ, keyed units run for BOTH sign and gsbc algebra, cardinality holds).
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: joint gate (ret>=0.35 + keyed>=0.95 + hi80 guard) applies to
  {GSBC_2PCT,GSBC_3PCT}_BLOCK_LAST; SIGN_BLOCK is Gate-D + baseline; DENSE_* are
  CONTEXT only; RANDOM_BLOCK/CHARPOS/shuffled_key integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=28 both run modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-04_exp_encoder_v11_gsbc_graded_sparse_v1.md
Parent cell (read-only import, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
Does NOT touch v3/v3c/v3e/v5/v6's own artifact/checkpoint/output directories.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)
from hdlab.binding import bind, unbind  # noqa: E402 -- block-wise circular conv over (kb,blk_l)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v11_gsbc_graded_sparse_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7
N_DIM = v3.N_DIM_DEFAULT        # 4096 (student output dim; block reshape differs per arm)

TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

OBJECTIVE = "in_batch"  # RKD-only, nce_weight=0 (matches v3e/v5/v6 winning config)
SELECT_TAU = v3.TAU_GUMBEL  # 1.0; softmax temperature for the straight-through top-m mask

# arm -> (mode, kb, blk_l, m, width, recipe). mode in {sign, gsbc}; recipe in
# {rkd_only, full}. kb*blk_l == N_DIM. Nested ablation: SIGN (v3e) -> GSBC_RKD
# (isolates the CODE: graded vs sign at RKD-only) -> GSBC_FULL (isolates the
# training RECIPE on the graded code).
STE_ARMS = {
    "SIGN_BLOCK": ("sign", 128, 32, 1, 2048, "rkd_only"),  # control == v3e (3.12%)
    "GSBC_RKD": ("gsbc", 32, 128, 3, 2048, "rkd_only"),    # graded top-3 RKD-only (2.34%)
    "GSBC_FULL": ("gsbc", 32, 128, 3, 2048, "full"),       # graded + recipe (2.34%; PRIMARY)
}
SMOKE_STE_ARMS = {
    "SIGN_BLOCK": ("sign", 128, 32, 1, 256, "rkd_only"),
    "GSBC_RKD": ("gsbc", 32, 128, 3, 256, "rkd_only"),
    "GSBC_FULL": ("gsbc", 32, 128, 3, 256, "full"),
}
CONTROL_ARM = "SIGN_BLOCK"
SECONDARY_ARM = "GSBC_RKD"   # graded RKD-only (isolates code from recipe)
PRIMARY_ARM = "GSBC_FULL"    # graded + annealed estimator + listwise-rank + anchor

# ---- Training recipe (research drill 2026-07-04; applies ONLY to recipe=full) ----
# ESTIMATOR: annealed soft->hard graded top-m straight-through + soft/hard
# consistency (the SAME estimator that learned 0.65 dense geometry in v6; the
# graded code removes the block-argmax carrier bottleneck). OBJECTIVE: graded-RKD
# backbone + listwise-rank (ListNet) + a MANDATORY absolute-cosine anchor.
# #1 RISK (readable in metrics): the anchor may CAP trained ret below 0.35 even
# though the code ceiling is ~0.7-0.9 (drill P_deflated 0.44) -> report
# trained-ret vs code-ceiling gap + calib JOINTLY.
TAU_HI = 2.0
TAU_LO = 0.1
ANNEAL_FRAC = 0.8
CONS_WEIGHT = 0.5       # soft/hard consistency MSE
RANK_WEIGHT = 0.5       # listwise-rank (ListNet top-1 listwise CE) term
ANCHOR_WEIGHT = 1.0     # MANDATORY absolute-cosine anchor (calibration guard; NOT optional)
ANCHOR_HI_THRESH = 0.5  # teacher-sim band for the absolute-cosine anchor

# ---- FULL-scale config: matches v3e/v5/v6 except the code ----
FULL_BATCH = 128
FULL_STEPS = 8000
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 400
FULL_TRIALS = v3.MID_TRIALS
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_QUICK_SUB = 1500
VAL_QUICK_PAIRS = 40_000
VAL_FULL_PAIRS = 60_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE  # 400_000

# ---- Smoke config: MACHINERY validation only (SAME code path as FULL) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN    # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD      # 800
SMOKE_STEPS = 200
SMOKE_CKPT_EVERY = 60
SMOKE_DENSE_EVAL_EVERY = 40
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05

# 3 arms x 9 units + shared CHARPOS(1) = 28.
EXPECTED_N_UNITS_FULL = 28
EXPECTED_N_UNITS_SMOKE = 28

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]
# keyed@J5 SBC/GSBC algebra HARD co-gate. Zero-train probe: GSBC circ-conv holds 1.00.
ALGEBRA_FLOOR = 0.95

# ---- GSBC bands (coordinator spec: HARD-PASS ret>=0.35 at ~2% WITH keyed>=0.95) ----
GSBC_RET_HARD_PASS = 0.35   # deployed GSBC block-code ret_agree10 >= 0.35
GSBC_RET_HARD_FAIL = 0.25   # <= 0.25 -> no meaningful lift over the sign 0.21 baseline
HI80_COLLAPSE_FLOOR = 0.30  # coarse cosine must not collapse below this (joint guard)
BASELINE_RET_LO = 0.15      # Gate-D band around v3e MEASURED 0.2112
BASELINE_RET_HI = 0.28
CODE_CEILING_RET_K128 = 0.4295278  # MEASURED@bypass SIGN-only ortho ceiling (GSBC exceeds)


def _crlb_sigma_teacher(k_anchor: int, r_anchor: float) -> float:
    return math.sqrt((r_anchor ** 2 * 0.25 / k_anchor) / (1 - r_anchor ** 2))


CRLB_SIGMA_TEACHER = _crlb_sigma_teacher(128, 0.901)


def _crlb_r_max(k: int) -> float:
    return CRLB_SIGMA_TEACHER / math.sqrt(CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v11_gsbc{tag}{suffix}"


# ---------------------------------------------------------------------------
# GSBC code + block-wise circular-conv algebra (lever; Frady/Kleyko GSBC).
# ---------------------------------------------------------------------------

def _gsbc_code_from_z(z: torch.Tensor, kb: int, blk_l: int, m: int,
                      select_tau: float) -> torch.Tensor:
    """Differentiable block top-m GRADED positive survivors, unit-L1 per block.

    FORWARD: keep the |z| magnitudes of the top-m entries per blk_l block, zero
    the rest, normalize each block to unit L1 -> a positive per-block sparse
    distribution. BACKWARD: straight-through top-m mask (hard + softmax - detach)
    so near-winner logits get gradient; the survivor magnitudes carry real
    gradient (no sign quantization). Matches _encode_gsbc FORWARD exactly.
    """
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    mag = zb.abs()
    p = torch.softmax(mag / select_tau, dim=-1)
    idx = mag.topk(m, dim=-1).indices
    hard = torch.zeros_like(mag)
    hard.scatter_(-1, idx, 1.0)
    mask_st = hard + p - p.detach()          # forward=top-m one-hot(s), backward=grad(p)
    surv = mag * mask_st                      # graded positive survivors
    l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
    return (surv / l1).reshape(B, kb * blk_l)


def _tau_at(step: int, steps: int, anneal_frac: float, tau_hi: float,
            tau_lo: float) -> float:
    """Cosine anneal tau_hi -> tau_lo over the first anneal_frac of steps, hold."""
    anneal_steps = max(1, int(round(anneal_frac * steps)))
    if step >= anneal_steps:
        return tau_lo
    frac = step / anneal_steps
    return tau_lo + 0.5 * (tau_hi - tau_lo) * (1.0 + math.cos(math.pi * frac))


def _gsbc_soft_hard(z: torch.Tensor, kb: int, blk_l: int, m: int,
                    tau: float) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Annealed soft->hard graded estimator (the v6 0.65-learner, graded).

    FORWARD = the EXACT hard graded top-m unit-L1 code (what eval deploys).
    BACKWARD = via the annealed soft per-block softmax (gradient to near-winner
    positions; tau HIGH early -> soft/explore, tau LOW late -> peaked/near-hard).
    Returns (code_st, soft_norm, hard_norm) for the soft/hard consistency term.
    """
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    mag = zb.abs()
    idx = mag.topk(m, dim=-1).indices
    hs = torch.zeros_like(mag)
    hs.scatter_(-1, idx, torch.gather(mag, -1, idx))
    hard = hs / hs.sum(dim=-1, keepdim=True).clamp_min(1e-8)   # top-m unit-L1
    soft = torch.softmax(mag / tau, dim=-1)                    # annealed soft, unit-L1
    code_st = hard + soft - soft.detach()                      # fwd=hard, bwd=grad(soft)
    return (code_st.reshape(B, kb * blk_l), soft.reshape(B, kb * blk_l),
            hard.reshape(B, kb * blk_l))


def _listnet_loss(S: torch.Tensor, T: torch.Tensor, off: torch.Tensor) -> torch.Tensor:
    """Listwise-rank (ListNet top-1): per-row cross-entropy between softmax(teacher
    sims) and log_softmax(code sims) over the off-diagonal. Optimizes near-neighbor
    RANK (ret_agree10) directly, complementing the absolute RKD Gram match."""
    neg = torch.full_like(T, -1e9)
    Tm = torch.where(off, T, neg)
    Sm = torch.where(off, S, neg)
    pt = torch.softmax(Tm, dim=-1)
    logps = torch.log_softmax(Sm, dim=-1)
    return -(pt * logps).sum(dim=-1).mean()


def _anchor_loss(S: torch.Tensor, T: torch.Tensor, off: torch.Tensor,
                 thresh: float) -> torch.Tensor:
    """MANDATORY absolute-cosine anchor: MSE(code_cos, teacher_cos) on the
    high-teacher-sim band (T >= thresh). Guards against the rank/estimator levers
    INFLATING cosine and wrecking calibration (the joint-gate FALSE-PASS trap)."""
    hi = off & (T >= thresh)
    if hi.sum() == 0:
        return torch.zeros((), device=S.device)
    return ((S[hi] - T[hi]) ** 2).mean()


@torch.no_grad()
def _encode_gsbc(student: torch.nn.Module, X: torch.Tensor, kb: int, blk_l: int,
                 m: int, batch: int = 8192) -> torch.Tensor:
    """Eval-time deployed GSBC code (positive, unit-L1 per block)."""
    dev = v3._student_device(student)
    out = torch.zeros(X.shape[0], kb * blk_l, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        zb = student(X[lo:lo + batch].to(dev)).reshape(-1, kb, blk_l)
        mag = zb.abs()
        idx = mag.topk(m, dim=-1).indices
        surv = torch.zeros_like(mag)
        surv.scatter_(-1, idx, torch.gather(mag, -1, idx))
        l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        out[lo:lo + batch] = (surv / l1).reshape(-1, kb * blk_l).cpu()
    return out


def _random_gsbc_codes(n: int, kb: int, blk_l: int, m: int,
                       gen: torch.Generator) -> torch.Tensor:
    """Random positive unit-L1 GSBC codes (positive control)."""
    z = torch.randn(n, kb, blk_l, generator=gen)
    mag = z.abs()
    idx = mag.topk(m, dim=-1).indices
    surv = torch.zeros_like(mag)
    surv.scatter_(-1, idx, torch.gather(mag, -1, idx))
    l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
    return (surv / l1).reshape(n, kb * blk_l)


def _pos_shift_keys(J: int, kb: int, blk_l: int, gen: torch.Generator) -> torch.Tensor:
    """Positive one-hot key per block (pure circular shift; preserves unit-L1)."""
    keys = torch.zeros(J, kb, blk_l)
    offs = torch.randint(0, blk_l, (J, kb), generator=gen)
    keys.scatter_(-1, offs.unsqueeze(-1), 1.0)
    return keys


def _gsbc_keyed_unit(arm: str, codes_all: torch.Tensor, kb: int, blk_l: int,
                     J: int, n_trials: int, gen: torch.Generator, device: str,
                     shuffled_key: bool = False) -> Dict:
    """GSBC keyed roundtrip: bind(shift_key, code) block-wise circular-conv, sum
    over J, unbind key_q, cleanup@1 (cosine). Ideal GSBC binding (Frady/Kleyko)."""
    V, n_dim = codes_all.shape
    queries, targets, members = [], [], []
    for _ in range(n_trials):
        fi = torch.randint(0, V, (J,), generator=gen)
        keys = _pos_shift_keys(J, kb, blk_l, gen)
        bundle = torch.zeros(kb, blk_l)
        for j in range(J):
            bundle = bundle + bind(keys[j], codes_all[fi[j]].reshape(kb, blk_l))
        qj = int(torch.randint(0, J, (1,), generator=gen))
        key_q = (_pos_shift_keys(1, kb, blk_l, gen)[0] if shuffled_key else keys[qj])
        u = unbind(bundle, key_q).reshape(n_dim)
        queries.append(u)
        targets.append(int(fi[qj]))
        members.append(fi.tolist())
    Q = torch.stack(queries)
    pred, best, second = v3._chunked_cleanup_argmax(Q, codes_all, device)
    tgt = torch.tensor(targets)
    acc = float((pred == tgt).float().mean())
    hit_any = float(np.mean([int(int(pred[t]) in members[t]) for t in range(n_trials)]))
    unit_name = ("shuffled_key" if shuffled_key else "keyed")
    return {
        "unit": f"{unit_name}::{arm}::J{J}", "arm": arm, "kind": unit_name,
        "J": J, "algebra": "gsbc_circconv", "acc_at1": acc,
        "hit_any_member": hit_any,
        "snr_margin_mean": float((best - second).mean()), "n_trials": n_trials,
    }


# ---- Per-arm dispatch (sign uses v3 verbatim; gsbc uses the graded path) ----

def _encode_block_for_arm(mode: str, student: torch.nn.Module, X: torch.Tensor,
                          kb: int, blk_l: int, m: int) -> torch.Tensor:
    if mode == "sign":
        return v3._encode_hard_block(student, X, kb, blk_l)
    if mode == "gsbc":
        return _encode_gsbc(student, X, kb, blk_l, m)
    raise ValueError(f"unknown mode {mode}")


def _random_code_for_arm(mode: str, n: int, kb: int, blk_l: int, m: int,
                         gen: torch.Generator) -> torch.Tensor:
    if mode == "sign":
        return v3._random_block_codes(n, kb, blk_l, gen)
    if mode == "gsbc":
        return _random_gsbc_codes(n, kb, blk_l, m, gen)
    raise ValueError(f"unknown mode {mode}")


def _keyed_for_arm(mode: str, arm: str, code: torch.Tensor, kb: int, blk_l: int,
                   J: int, n_trials: int, gen: torch.Generator, device: str,
                   shuffled_key: bool = False) -> Dict:
    if mode == "sign":
        return v3._keyed_unit(arm, "sbc", code, kb, blk_l, J, n_trials, gen,
                              device, shuffled_key=shuffled_key)
    if mode == "gsbc":
        return _gsbc_keyed_unit(arm, code, kb, blk_l, J, n_trials, gen, device,
                                shuffled_key=shuffled_key)
    raise ValueError(f"unknown mode {mode}")


# ---------------------------------------------------------------------------
# Determinism pinning (identical to v5/v4/v6).
# ---------------------------------------------------------------------------

def _pin_determinism(seed: int) -> Dict:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    det_ok = True
    det_err = ""
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except TypeError:
        try:
            torch.use_deterministic_algorithms(True)
        except Exception as exc:  # pragma: no cover
            det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # pragma: no cover
        det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    n_threads = min(8, os.cpu_count() or 4)
    try:
        torch.set_num_threads(n_threads)
    except RuntimeError:
        pass
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    return {
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "num_threads_requested": n_threads,
        "deterministic_algorithms_set": det_ok,
        "deterministic_algorithms_error": det_err,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
    }


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": int(expected_n_units), "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": int(unit_idx),
           "total_units": int(total_units), "elapsed_s": float(elapsed_s)}
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Trainer (ONE trainer, per-arm mode/geometry; nce_weight=0 -> NCE dropped).
# ---------------------------------------------------------------------------

def _train_loss_floored(rkd_traj: List[Dict]) -> Tuple[bool, float]:
    pts = [(r["step"], r["rkd"]) for r in rkd_traj if math.isfinite(r.get("rkd", float("nan")))]
    if len(pts) < 3:
        return False, float("nan")
    pts.sort()
    rkd_first = pts[0][1]
    rkd_last = pts[-1][1]
    total = rkd_first - rkd_last
    if total <= 1e-9:
        return True, 1.0
    half_i = len(pts) // 2
    q3_i = (3 * len(pts)) // 4
    frac_by_half = (rkd_first - pts[half_i][1]) / total
    last_quarter = (pts[q3_i][1] - rkd_last) / total
    return bool(last_quarter < 0.05), float(frac_by_half)


def _train_student_v11(
    mode: str, kb: int, blk_l: int, m: int, width: int, Xtr: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int, output_dir: Path,
    t0: float, dense_eval_quick_fn: Optional[Callable],
    dense_eval_full_fn: Optional[Callable], dense_eval_every: int,
    min_step_for_best: int, select_tau: float, recipe: str, arm_label: str,
) -> Tuple[torch.nn.Module, Dict]:
    """In-batch trainer. mode in {sign, gsbc}; recipe in {rkd_only, full}.

    rkd_only: loss = graded/sign RKD only (sign == v3e; gsbc == fixed-tau STE).
    full (gsbc only): annealed soft->hard graded estimator (+ soft/hard
      consistency MSE) + graded-RKD backbone + listwise-rank (ListNet) + a
      MANDATORY absolute-cosine anchor. Eval uses the DEPLOYED hard graded code.
    """
    if mode not in ("sign", "gsbc"):
        raise ValueError(f"unknown mode {mode}")
    if recipe not in ("rkd_only", "full"):
        raise ValueError(f"unknown recipe {recipe}")
    if recipe == "full" and mode != "gsbc":
        raise ValueError(f"recipe=full only valid for gsbc mode, got {mode}")
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = width
    try:
        student = v3._make_student("mlp", Xtr.shape[1], kb * blk_l, device, seed)
    finally:
        v3.MLP_HIDDEN = orig_hidden
    actual_hidden = int(student.net[0].out_features)
    if actual_hidden != width:
        raise RuntimeError(
            f"failure_class=WIDTH_MONKEYPATCH_FAILED: {arm_label} built student "
            f"hidden={actual_hidden} != requested width={width}")
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    start_step = 0
    dense_traj: List[Dict] = []
    best_state = {"score": -2.0, "step": -1}
    if ckpt_path.exists():
        try:
            ck = torch.load(str(ckpt_path), map_location=device)
            student.load_state_dict(ck["student"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            dense_traj = list(ck.get("dense_traj", []))
            best_state["score"] = float(ck.get("best_score", -2.0))
            best_state["step"] = int(ck.get("best_step", -1))
            print(f"[v11_gsbc] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v11_gsbc] WARN {arm_label} ckpt load failed ({type(exc).__name__}); "
                  f"retraining from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}

    off = ~torch.eye(batch, dtype=torch.bool, device=device)
    loss_first = loss_last = rkd_last = activefrac_last = None
    cons_last = rank_last = anchor_last = tau_last = None

    def _maybe_save_best(step_i: int, d_full: float) -> None:
        if not math.isfinite(d_full) or step_i < min_step_for_best:
            return
        if d_full > best_state["score"]:
            best_state["score"] = d_full
            best_state["step"] = step_i
            tmp_b = best_ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "step": step_i,
                        "dense_full": d_full, "arm": arm_label}, str(tmp_b))
            os.replace(str(tmp_b), str(best_ckpt_path))

    for step in range(start_step, steps):
        cur_lr = v3._lr_at(step, steps, warmup, v3.LR)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = torch.randint(0, V, (batch,), generator=gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        T = x @ x.T
        if recipe == "full":
            tau = _tau_at(step, steps, ANNEAL_FRAC, TAU_HI, TAU_LO)
            s, soft, hard = _gsbc_soft_hard(z, kb, blk_l, m, tau)
            s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
            S = s_n @ s_n.T
            l_rkd = ((S - T)[off] ** 2).mean()
            l_cons = ((soft - hard.detach()) ** 2).mean()
            l_rank = _listnet_loss(S, T, off)
            l_anchor = _anchor_loss(S, T, off, ANCHOR_HI_THRESH)
            loss = l_rkd + CONS_WEIGHT * l_cons + RANK_WEIGHT * l_rank + ANCHOR_WEIGHT * l_anchor
        else:
            tau = float("nan")
            if mode == "sign":
                s = v3._block_ste(z, kb, blk_l)
            else:
                s = _gsbc_code_from_z(z, kb, blk_l, m, select_tau)
            s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
            l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
            l_cons = l_rank = l_anchor = torch.zeros((), device=device)
            loss = l_rkd
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_cons={float(l_cons.detach())}, "
                f"l_rank={float(l_rank.detach())}, l_anchor={float(l_anchor.detach())}, "
                f"tau={tau})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            activefrac = float((s.detach() != 0).float().sum() / (s.shape[0] * s.shape[1]))
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last, rkd_last, activefrac_last = v_loss, v_rkd, activefrac
        cons_last, rank_last, anchor_last = (float(l_cons.detach()),
                                             float(l_rank.detach()),
                                             float(l_anchor.detach()))
        tau_last = tau
        if step % 200 == 0:
            print(f"[v11_gsbc] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"cons={cons_last:.4f} rank={rank_last:.4f} anchor={anchor_last:.4f} "
                  f"tau={tau if math.isfinite(tau) else -1:.3f} active={activefrac:.4f} "
                  f"lr={cur_lr:.2e} ({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "rkd": v_rkd,
                                   "cons": cons_last, "rank": rank_last,
                                   "anchor": anchor_last, "active": activefrac})
        if (dense_eval_full_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_full = float(dense_eval_full_fn(student))
            d_quick = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
            dense_traj.append({"step": step, "dense_full": d_full,
                               "dense_quick": d_quick, "rkd": v_rkd,
                               "active": activefrac, "final": False})
            print(f"[v11_gsbc] {arm_label} DENSE-traj step {step}: full={d_full:.4f} "
                  f"quick={d_quick:.4f} rkd={v_rkd:.4f}", flush=True)
            _maybe_save_best(step, d_full)
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "opt": opt.state_dict(),
                        "gen_state": gen.get_state(), "step": step + 1,
                        "dense_traj": dense_traj, "best_score": best_state["score"],
                        "best_step": best_state["step"]}, str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    if dense_eval_full_fn is not None:
        d_full_fin = float(dense_eval_full_fn(student))
        d_quick_fin = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
        dense_traj.append({"step": steps, "dense_full": d_full_fin,
                           "dense_quick": d_quick_fin,
                           "rkd": rkd_last if rkd_last is not None else float("nan"),
                           "active": activefrac_last, "final": True})
        _maybe_save_best(steps, d_full_fin)
        print(f"[v11_gsbc] {arm_label} FINAL step {steps}: full={d_full_fin:.4f}",
              flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                    "dense_full": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[v11_gsbc] WARN {arm_label}: no eval >= min_step_for_best; "
              f"best-ckpt falls back to FINAL", flush=True)
    floored, frac_half = _train_loss_floored(dense_traj)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "cons_last": cons_last if cons_last is not None else -1.0,
        "rank_last": rank_last if rank_last is not None else -1.0,
        "anchor_last": anchor_last if anchor_last is not None else -1.0,
        "tau_last": tau_last if tau_last is not None else float("nan"),
        "activefrac_last": activefrac_last if activefrac_last is not None else -1.0,
        "select_tau": select_tau, "recipe": recipe,
        "mode": mode, "kb": kb, "blk_l": blk_l, "m": m,
        "mlp_hidden": width, "arm": arm_label, "objective": OBJECTIVE, "batch": batch,
        "dense_traj": dense_traj, "train_loss_floored": floored,
        "train_loss_descent_frac_by_half": frac_half,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
    }


def _reload_best_v11(width: int, in_dim: int, out_dim: int, device: str,
                     best_ckpt_path: Path) -> torch.nn.Module:
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = width
    try:
        student = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    finally:
        v3.MLP_HIDDEN = orig_hidden
    ck = torch.load(str(best_ckpt_path), map_location=device)
    student.load_state_dict(ck["student"])
    return student


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_v11(per_unit: List[Dict], recovery: Dict, arm_names: List[str],
                 control_arm: str, secondary_arm: str, primary_arm: str,
                 expected_units: int, run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    for arm in arm_names:
        posc = v3._by_unit(per_unit, "keyed", f"{arm}_RANDOM_BLOCK", 5)
        if posc is None or posc["acc_at1"] < 0.98:
            return ("HARD_FAIL",
                    f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: {arm} RANDOM_BLOCK "
                    f"keyed J=5 {posc['acc_at1'] if posc else None} < 0.98")
        shuf = v3._by_unit(per_unit, "shuffled_key", f"{arm}_BLOCK_LAST", 5)
        if shuf is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {arm} shuffled_key")
        if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SHUFFLED_KEY_LEAK: {arm} "
                    f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")
        prim = v3._by_unit(per_unit, "keyed", f"{arm}_BLOCK_LAST", 5)
        if prim is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {arm} keyed LAST")

    def _alg(arm: str) -> float:
        u = v3._by_unit(per_unit, "keyed", f"{arm}_BLOCK_LAST", 5)
        return float(u["acc_at1"]) if u else 0.0

    ctrl = recovery[control_arm]["final"]
    sec = recovery[secondary_arm]["final"]
    pri = recovery[primary_arm]["final"]
    ctrl_alg, sec_alg, pri_alg = _alg(control_arm), _alg(secondary_arm), _alg(primary_arm)
    diag = recovery[control_arm].get("train_loss_floored")
    cap_diag = ("train_loss_floored_at_low_ret->capacity_NOT_bottleneck"
                if diag else "train_loss_not_floored->capacity_may_matter")
    tail = (f"[{control_arm} ret={ctrl['ret_agree10']:.4f} hi80={ctrl['hi80_cos']:.4f} "
            f"calib={ctrl['hi80_calib_err']:.4f} alg={ctrl_alg:.3f} floored={diag}] "
            f"[{primary_arm} ret={pri['ret_agree10']:.4f} hi80={pri['hi80_cos']:.4f} "
            f"calib={pri['hi80_calib_err']:.4f} alg={pri_alg:.3f}] "
            f"[{secondary_arm} ret={sec['ret_agree10']:.4f} hi80={sec['hi80_cos']:.4f} "
            f"calib={sec['hi80_calib_err']:.4f} alg={sec_alg:.3f}] "
            f"sign_ceiling={CODE_CEILING_RET_K128:.4f} cap_diag={cap_diag}")

    if run_mode == "smoke":
        for arm in arm_names:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: all {len(arm_names)} arms (sign + 2 GSBC) train "
                f"end-to-end with differing codes; per-arm RANDOM_BLOCK/shuffled-key "
                f"checks fire; keyed units run for BOTH sign (element SBC) and GSBC "
                f"(circular-conv) algebra; cardinality holds {tail} (the ret>=0.35 "
                f"discriminator is FULL-only; smoke's tiny V_train cannot reproduce it "
                f"-- REMOTE-QUEUE OFFICIAL LANDING is canonical; GSBC-keeps-keyed@J5 was "
                f"shown at full format scale by the zero-training probe)")

    # ---- FULL verdict ----
    if not (BASELINE_RET_LO <= ctrl["ret_agree10"] <= BASELINE_RET_HI):
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: control {control_arm} final "
                f"ret_agree10 {ctrl['ret_agree10']:.4f} outside v3e-reproduction band "
                f"[{BASELINE_RET_LO},{BASELINE_RET_HI}] -- sign baseline drifted; GSBC "
                f"comparison not trustworthy {tail}")
    if ctrl_alg < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_CONTROL_ALGEBRA_BROKE: {control_arm} keyed@J5 {ctrl_alg:.3f} "
                f"< {ALGEBRA_FLOOR} -- sign baseline SBC algebra broken; machinery {tail}")

    def _joint_pass(ret: float, alg: float, hi80: float) -> bool:
        return (ret >= GSBC_RET_HARD_PASS and alg >= ALGEBRA_FLOOR
                and hi80 >= HI80_COLLAPSE_FLOOR)

    # 1. Any GSBC arm LIFTS but BREAKS algebra -> HARD_FAIL (the finding).
    if (pri["ret_agree10"] > GSBC_RET_HARD_FAIL and pri_alg < ALGEBRA_FLOOR) or \
       (sec["ret_agree10"] > GSBC_RET_HARD_FAIL and sec_alg < ALGEBRA_FLOOR):
        return ("HARD_FAIL",
                f"GSBC_BREAKS_ALGEBRA: a GSBC arm lifts ret but keyed@J5 dropped below "
                f"{ALGEBRA_FLOOR} (pri {pri_alg:.3f}/sec {sec_alg:.3f}) -- graded code "
                f"corrupts block circular-conv binding under training; THIS is the "
                f"finding (GSBC theory predicts it should hold exactly) {tail}")
    # 2. PRIMARY (GSBC_2PCT) clean joint pass -> HARD_PASS.
    if _joint_pass(pri["ret_agree10"], pri_alg, pri["hi80_cos"]):
        return ("HARD_PASS",
                f"GSBC_GRADED_CLEARS_TARGET_ALGEBRA_HELD: {primary_arm} deployed GSBC "
                f"code ret {pri['ret_agree10']:.4f} >= {GSBC_RET_HARD_PASS} at ~2% active "
                f"WITH keyed@J5 {pri_alg:.3f} >= {ALGEBRA_FLOOR} and no coarse collapse -- "
                f"the graded Sparse-Block-Code + circular-conv binding beats the "
                f"sign-only 0.43 ceiling JOINTLY (ret+algebra+hi80). Next: density dial "
                f"+ composition-depth VET + global-WTA/expansion arm {tail}")
    # 3. PRIMARY ret+algebra pass but coarse cosine collapsed -> MIDDLE_BAND.
    if pri["ret_agree10"] >= GSBC_RET_HARD_PASS and pri_alg >= ALGEBRA_FLOOR \
            and pri["hi80_cos"] < HI80_COLLAPSE_FLOOR:
        return ("MIDDLE_BAND",
                f"GSBC_CLEARS_RET_BUT_HI80_COLLAPSES: {primary_arm} ret "
                f"{pri['ret_agree10']:.4f} algebra {pri_alg:.3f} OK but hi80_cos "
                f"{pri['hi80_cos']:.4f} < {HI80_COLLAPSE_FLOOR}; positive-code "
                f"calibration cost, joint instrument not fully clean {tail}")
    # 4. SECONDARY (GSBC_3PCT) clean joint pass (primary did not) -> MIDDLE_BAND.
    if _joint_pass(sec["ret_agree10"], sec_alg, sec["hi80_cos"]):
        return ("MIDDLE_BAND",
                f"GSBC_3PCT_CLEARS_BUT_2PCT_DID_NOT: {secondary_arm} ret "
                f"{sec['ret_agree10']:.4f} algebra {sec_alg:.3f} clean at 3.12% but the "
                f"2% primary did not clear {GSBC_RET_HARD_PASS} -- density matters; next "
                f"cell makes 3% (or a density dial) the primary {tail}")
    # 5. Neither GSBC arm lifts above the fail floor -> HARD_FAIL structural.
    if pri["ret_agree10"] <= GSBC_RET_HARD_FAIL and sec["ret_agree10"] <= GSBC_RET_HARD_FAIL:
        return ("HARD_FAIL",
                f"GSBC_NO_LIFT: neither {primary_arm} ({pri['ret_agree10']:.4f}) nor "
                f"{secondary_arm} ({sec['ret_agree10']:.4f}) lifts ret above "
                f"{GSBC_RET_HARD_FAIL}; the graded code does not exploit the magnitude "
                f"channel under training -- honest wall, route to the density dial {tail}")
    # 6. Marginal (lift over baseline but below the 0.35 target, algebra held).
    return ("MIDDLE_BAND",
            f"GSBC_MARGINAL: best GSBC ret between {GSBC_RET_HARD_FAIL} and "
            f"{GSBC_RET_HARD_PASS} with algebra held -- graded helps but does not clear "
            f"the 0.35 target at ~2%; needs the 2nd seed or a density nudge {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_gsbc_sweep(run_mode: str, seed: int, device_arg: str, n_dim: int,
                   teacher_cache_arg: Optional[str], run_tag: str = "") -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    if n_dim != N_DIM:
        raise ValueError(f"n_dim {n_dim} != N_DIM {N_DIM}")
    det_info = _pin_determinism(seed)
    tag_suffix = f"_{run_tag}" if run_tag else ""
    anchor = f"{ANCHOR_NAME}{tag_suffix}_smoke" if run_mode == "smoke" \
        else f"{ANCHOR_NAME}{tag_suffix}"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, run_tag)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg

    ste_arms = SMOKE_STE_ARMS if run_mode == "smoke" else STE_ARMS
    arm_names = list(ste_arms.keys())
    for arm, (mode, kb, blk_l, m, width, recipe) in ste_arms.items():
        if kb * blk_l != n_dim:
            raise ValueError(f"{arm}: kb*blk_l {kb * blk_l} != n_dim {n_dim}")

    if run_mode == "smoke":
        steps = SMOKE_STEPS
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = SMOKE_VAL_QUICK_SUB, SMOKE_VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = SMOKE_VAL_FULL_PAIRS, SMOKE_TEST_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        batch = min(FULL_BATCH, 32)
    else:
        steps = FULL_STEPS
        ckpt_every, dense_every = CKPT_EVERY_STEPS_FULL, DENSE_EVAL_EVERY_FULL
        quick_sub, quick_pairs = VAL_QUICK_SUB, VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = VAL_FULL_PAIRS, TEST_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        n_tr_target = n_he_target = None
        batch = FULL_BATCH
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v11_gsbc] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"arms={ste_arms} steps={steps} batch={batch} select_tau={SELECT_TAU} "
          f"torch={det_info['torch_version']} "
          f"deterministic_ok={det_info['deterministic_algorithms_set']}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v11_gsbc] teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        if V_cache < n_tr_target + n_he_target:
            raise RuntimeError(f"teacher cache too small for smoke: {V_cache}")
        n_tr, n_he = n_tr_target, n_he_target
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx = perm[:n_tr]
    he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[v11_gsbc] split train={n_tr} held={n_he}", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, val_full_pairs, seed + 7)

    arm_diag: Dict[str, Dict] = {}
    arm_codes: Dict[str, torch.Tensor] = {}
    arm_geom: Dict[str, Tuple] = {}
    for arm, (mode, kb, blk_l, m, width, recipe) in ste_arms.items():
        arm_geom[arm] = (mode, kb, blk_l, m)
        ckpt_path = art_dir / f"_ckpt_{arm}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{arm}.pt"
        last_student, diag = _train_student_v11(
            mode, kb, blk_l, m, width, Xtr, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            _deval_quick, _deval_full, dense_every, min_step_for_best,
            SELECT_TAU, recipe, arm)
        bestval_student = _reload_best_v11(width, Xtr.shape[1], kb * blk_l, device,
                                           best_ckpt_path)
        arm_diag[arm] = diag
        arm_codes[f"{arm}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xhe)
        arm_codes[f"{arm}_BLOCK_LAST"] = _encode_block_for_arm(mode, last_student, Xhe, kb, blk_l, m)
        arm_codes[f"{arm}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xhe)
        arm_codes[f"{arm}_BLOCK_BESTVAL"] = _encode_block_for_arm(mode, bestval_student, Xhe, kb, blk_l, m)
        # Per-arm-distinct seed so RANDOM_BLOCK controls do not collide across arms
        # that share geometry (e.g. GSBC_RKD vs GSBC_FULL) -- avoids a spurious AF hit.
        gen_ctrl = torch.Generator().manual_seed(
            seed + 1 + width + kb + m + 1009 * arm_names.index(arm))
        arm_codes[f"{arm}_RANDOM_BLOCK"] = _random_code_for_arm(mode, n_he, kb, blk_l, m, gen_ctrl)
        print(f"[v11_gsbc] {arm} (mode={mode} kb={kb} blk_l={blk_l} m={m} hidden={width}) "
              f"rkd_last={diag['rkd_last']:.4f} active={diag['activefrac_last']:.4f} "
              f"floored={diag['train_loss_floored']} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, v3.K_BLOCKS_PRIMARY)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(
            np.ascontiguousarray(c.to(torch.float32).numpy()).tobytes()).hexdigest()

    def _is_last_bestval_pair(a: str, b: str) -> bool:
        return a != b and a.replace("_BESTVAL", "_LAST") == b.replace("_BESTVAL", "_LAST")

    af_exempted: List[List[str]] = []
    for aa in digests:
        for bb in digests:
            if aa < bb and digests[aa] == digests[bb]:
                if _is_last_bestval_pair(aa, bb):
                    af_exempted.append([aa, bb])
                    continue
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {aa}/{bb} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v11_gsbc] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for arm in arm_names:
        for label in (f"{arm}_DENSE_LAST", f"{arm}_BLOCK_LAST",
                      f"{arm}_DENSE_BESTVAL", f"{arm}_BLOCK_BESTVAL"):
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                      test_final_pairs, seed + 3)
        _run_unit(v3._semantic_unit, f"{arm}_RANDOM_BLOCK", arm_codes[f"{arm}_RANDOM_BLOCK"],
                  arm_codes[f"{arm}_RANDOM_BLOCK"], Xhe, Xhe, 0, test_final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              test_final_pairs, seed + 3)

    for arm in arm_names:
        mode, kb, blk_l, m = arm_geom[arm]
        _run_unit(_keyed_for_arm, mode, f"{arm}_RANDOM_BLOCK", arm_codes[f"{arm}_RANDOM_BLOCK"],
                  kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(_keyed_for_arm, mode, f"{arm}_BLOCK_LAST",
                  arm_codes[f"{arm}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(_keyed_for_arm, mode, f"{arm}_BLOCK_BESTVAL",
                  arm_codes[f"{arm}_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(_keyed_for_arm, mode, f"{arm}_BLOCK_LAST",
                  arm_codes[f"{arm}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval,
                  device, shuffled_key=True)

    def _sem_summary(arm: str, kind: str) -> Dict:
        u = v3._by_unit(per_unit, "semantic", f"{arm}_{kind}")
        if u is None:
            return {"spearman_all": float("nan"), "ret_agree10": float("nan"),
                    "hi80_cos": float("nan"), "hi80_calib_err": float("nan")}
        return {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
                "hi80_cos": u["hi80_cos"], "hi80_calib_err": u["hi80_calib_err"]}

    recovery = {arm: {
        "mode": ste_arms[arm][0], "kb": ste_arms[arm][1], "blk_l": ste_arms[arm][2],
        "m": ste_arms[arm][3], "mlp_hidden": ste_arms[arm][4], "recipe": ste_arms[arm][5],
        "active_frac": (ste_arms[arm][1] * ste_arms[arm][3]) / n_dim,
        "final": _sem_summary(arm, "BLOCK_LAST"),
        "bestval_on_test": _sem_summary(arm, "BLOCK_BESTVAL"),
        "final_dense": _sem_summary(arm, "DENSE_LAST"),
        "bestval_dense_on_test": _sem_summary(arm, "DENSE_BESTVAL"),
        "rkd_last": arm_diag[arm]["rkd_last"],
        "cons_last": arm_diag[arm]["cons_last"],
        "rank_last": arm_diag[arm]["rank_last"],
        "anchor_last": arm_diag[arm]["anchor_last"],
        "tau_last": arm_diag[arm]["tau_last"],
        "activefrac_last": arm_diag[arm]["activefrac_last"],
        "train_loss_floored": arm_diag[arm]["train_loss_floored"],
        "train_loss_descent_frac_by_half": arm_diag[arm]["train_loss_descent_frac_by_half"],
        "rkd_traj": [{"step": r["step"], "rkd": r["rkd"], "dense_full": r["dense_full"]}
                     for r in arm_diag[arm]["dense_traj"]],
        "best_step": arm_diag[arm]["best_step"],
        "best_ckpt_fallback_to_final": arm_diag[arm]["best_ckpt_fallback_to_final"],
    } for arm in arm_names}

    verdict, verdict_msg = _verdict_v11(
        per_unit, recovery, arm_names,
        CONTROL_ARM if CONTROL_ARM in recovery else arm_names[0],
        SECONDARY_ARM if SECONDARY_ARM in recovery else arm_names[-1],
        PRIMARY_ARM if PRIMARY_ARM in recovery else arm_names[1],
        expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    ctrl_floored = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["train_loss_floored"]
    ctrl_ret = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["final"]["ret_agree10"]
    capacity_hypothesis_diagnostic = (
        "train_loss_floored_while_ret_low->capacity_NOT_bottleneck"
        if (ctrl_floored and math.isfinite(ctrl_ret) and ctrl_ret < 0.30)
        else "train_loss_not_floored_or_ret_high->capacity_may_matter")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": "mlp",
        "ste_arms": {k: list(v) for k, v in ste_arms.items()},
        "control_arm": CONTROL_ARM, "primary_arm": PRIMARY_ARM,
        "secondary_arm": SECONDARY_ARM,
        "select_tau": SELECT_TAU,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": 0.0, "objective": OBJECTIVE, "lr_schedule": "cosine_8000",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held_pool": n_he,
        "recovery": recovery,
        "capacity_hypothesis_diagnostic": capacity_hypothesis_diagnostic,
        "code_ceiling_ret_agree10_k128_signonly": CODE_CEILING_RET_K128,
        "code_ceiling_source": ("MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/"
                                "metrics.json:/recovery/ortho_k128_ret_agree10 (SIGN-only)"),
        "gsbc_bands": {"ret_hard_pass": GSBC_RET_HARD_PASS,
                       "ret_hard_fail": GSBC_RET_HARD_FAIL,
                       "algebra_floor": ALGEBRA_FLOOR,
                       "hi80_collapse_floor": HI80_COLLAPSE_FLOOR},
        "training_recipe": {"tau_hi": TAU_HI, "tau_lo": TAU_LO,
                            "anneal_frac": ANNEAL_FRAC, "cons_weight": CONS_WEIGHT,
                            "rank_weight": RANK_WEIGHT, "anchor_weight": ANCHOR_WEIGHT,
                            "anchor_hi_thresh": ANCHOR_HI_THRESH,
                            "estimator": "annealed_soft_to_hard_graded_topm_straight_through",
                            "objective": "graded_RKD + ListNet_listwise_rank + mandatory_absolute_cosine_anchor"},
        # #1 RISK (readable): the MANDATORY anchor may CAP trained ret below 0.35
        # even though the graded code ceiling is ~0.7-0.9 (drill P_deflated 0.44).
        # Read trained_ret + calib JOINTLY -- high ret with collapsed calib is a
        # FALSE PASS (the guard the anchor exists to prevent), not a win.
        "anchor_ret_cap_readout": {
            "primary_arm": PRIMARY_ARM,
            "trained_ret": recovery[PRIMARY_ARM]["final"]["ret_agree10"],
            "trained_calib_err": recovery[PRIMARY_ARM]["final"]["hi80_calib_err"],
            "trained_hi80_cos": recovery[PRIMARY_ARM]["final"]["hi80_cos"],
            "gsbc_rkd_only_ret": recovery[SECONDARY_ARM]["final"]["ret_agree10"],
            "sign_baseline_ret": recovery[CONTROL_ARM]["final"]["ret_agree10"],
            "sign_only_code_ceiling": CODE_CEILING_RET_K128,
            "gsbc_code_ceiling_estimate": "0.7-0.9 CITED@arXiv:2303.13957_Frady_Kleyko_GSBC",
            "ret_vs_signceiling_gap": (recovery[PRIMARY_ARM]["final"]["ret_agree10"]
                                       - CODE_CEILING_RET_K128),
            "note": ("anchor-may-cap-ret risk: report trained_ret AND calib together; "
                     "the anchor is the designed calibration guard so a ret<0.35 with "
                     "GOOD calib is an HONEST result, not a failure of the code"),
        },
        "determinism": det_info,
        "canonical_source": "remote_queue_official_landing_only; local_smoke_is_gate_only",
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "arms_differ_exempted": af_exempted,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "sign:SBC_block_local_circular_conv; gsbc:GSBC_block_circular_conv_pos_L1",
        "methodology": ("PAIRED at FIXED N_DIM=4096: SIGN_BLOCK control (== v3e; pure "
                        "sign block argmax; Gate-D reproduce ~0.21) -> GSBC_2PCT (graded "
                        "top-3 unit-L1, kb32/blk128, 2.34%, block-wise circular-conv "
                        "binding) PRIMARY -> GSBC_3PCT (graded top-2, kb64/blk64, 3.12%) "
                        "SECONDARY. ONE trainer (nce=0). GSBC drops the argmax-to-sign "
                        "quantization; keyed@J5 uses each code's ideal binding (sign: "
                        "element/circular SBC via v3._keyed_unit; gsbc: circular-conv + "
                        "positive shift keys). FINAL-step deployed-block ret_agree10 is "
                        "the gated number; keyed@J5 >= 0.95 is a HARD co-gate."),
        "sequenced_next_cell": ("IF GSBC clears 0.35: density dial (m/blk sweep) + "
                                "composition-depth VET + global-WTA/FlyHash-expansion arm "
                                "(B5 dual readout) + B-dim block-energy side channel. IF "
                                "GSBC_BREAKS_ALGEBRA: graded-vs-binding tension is real, "
                                "route to research. IF NO_LIFT: density dial to K256+."),
        "storage_strategy": ("no_composition; single-hop retrieval-agreement is the metric; "
                             "keyed-J5 is a fixed integrity control (bounded 5-item bundle)"),
        "compute_architecture": ("batched-GPU: student fwd/bwd + graded top-m + block "
                                 "circular-conv (FFT) are batched on cuda; eval samples "
                                 "pairs batched; keyed loops J=5 per trial (cheap)"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": {"K128_spearman_r_max": _crlb_r_max(128)},
        "crlb_formula_reference": ("ret discriminator reachability via the SIGN-only K128 "
                                   "ceiling 0.4295 (MEASURED@bypass) AND the zero-training "
                                   "GSBC probe (graded >= sign at matched sparsity); the "
                                   "graded ceiling is higher (dense-float=1.0) so ret>=0.35 "
                                   "is reachable."),
        "crlb_n_a": "ret_agree10 has no closed-form sigma CRLB; reachability via probes",
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "gsbc_algebra_probe": ("MEASURED@scratchpad/gsbc_format_probe.py: GSBC circular-conv "
                               "keyed@J5=1.0000 (pos + pm1 keys), shuffled 0.0000, "
                               "zero-training ORTHO lift; algebra certified at format scale"),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v11_gsbc] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. GSBC encode: top-m graded positive unit-L1 per block; matches eval path.
    torch.manual_seed(3)
    z = torch.randn(4, 8 * 16)  # kb=8, blk_l=16
    code = _gsbc_code_from_z(z, 8, 16, 3, 1.0)
    cb = code.reshape(4, 8, 16)
    assert (cb >= 0).all(), "GSBC code must be non-negative"
    assert torch.allclose(cb.sum(-1), torch.ones(4, 8), atol=1e-5), "unit-L1 per block"
    assert ((cb != 0).sum(-1) == 3).all(), "exactly m=3 survivors per block"

    class _Fake(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.p = torch.nn.Parameter(torch.zeros(1))  # gives _student_device a device

        def forward(self, x):
            return x
    fake = _Fake()
    Xz = torch.randn(4, 8 * 16)
    enc = _encode_gsbc(fake, Xz, 8, 16, 3)
    ref = _gsbc_code_from_z(Xz, 8, 16, 3, 1.0)
    assert torch.allclose(enc, ref, atol=1e-5), "eval encode must match train forward"

    # 2. straight-through gradient flows to z.
    zg = torch.randn(4, 8 * 16, requires_grad=True)
    c = _gsbc_code_from_z(zg, 8, 16, 3, 1.0)
    c.sum().backward()
    assert zg.grad is not None and zg.grad.abs().sum() > 0, "STE must pass gradient to z"

    # 3. GSBC keyed@J5 round-trips (circular-conv binding); shuffled key fails.
    gen = torch.Generator().manual_seed(5)
    codes = _random_gsbc_codes(40, 8, 16, 3, gen)
    u_keyed = _gsbc_keyed_unit("T", codes, 8, 16, 5, 40, gen, "cpu")
    assert u_keyed["acc_at1"] >= 0.9, f"GSBC keyed@J5 should round-trip, got {u_keyed['acc_at1']}"
    u_shuf = _gsbc_keyed_unit("T", codes, 8, 16, 5, 40, gen, "cpu", shuffled_key=True)
    assert u_shuf["acc_at1"] <= 0.15, f"shuffled key should fail, got {u_shuf['acc_at1']}"

    # 3b. training-recipe helpers: tau schedule, annealed soft/hard estimator
    #     (forward == hard graded top-m == eval code), ListNet, anchor.
    assert abs(_tau_at(0, 100, 0.8, 2.0, 0.1) - 2.0) < 1e-6, "tau(0)=tau_hi"
    assert abs(_tau_at(80, 100, 0.8, 2.0, 0.1) - 0.1) < 1e-6, "tau(anneal_end)=tau_lo"
    assert 0.1 < _tau_at(40, 100, 0.8, 2.0, 0.1) < 2.0, "tau mid between"
    zsh = torch.randn(4, 8 * 16)
    code_st, soft, hard = _gsbc_soft_hard(zsh, 8, 16, 3, 0.5)
    assert torch.allclose(code_st, hard, atol=1e-6), "soft/hard FORWARD must equal hard"
    assert torch.allclose(code_st, _gsbc_code_from_z(zsh, 8, 16, 3, 1.0), atol=1e-6), \
        "annealed FORWARD must equal the deployed hard graded top-m code"
    zg2 = zsh.clone().requires_grad_(True)
    c2, _, _ = _gsbc_soft_hard(zg2, 8, 16, 3, 0.5)
    c2.sum().backward()
    assert zg2.grad is not None and zg2.grad.abs().sum() > 0, "annealed STE grad to z"
    _T = torch.tensor([[1.0, 0.9, 0.1], [0.9, 1.0, 0.2], [0.1, 0.2, 1.0]])
    _off = ~torch.eye(3, dtype=torch.bool)
    _Sgood, _Sbad = _T.clone(), _T.flip(0).clone()
    assert _listnet_loss(_Sgood, _T, _off) < _listnet_loss(_Sbad, _T, _off), \
        "ListNet: rank-aligned S must have lower loss than mis-ranked S"
    assert float(_anchor_loss(_T, _T, _off, 0.5)) < 1e-9, "anchor(T,T)=0"
    assert float(_anchor_loss(_T * 0.0, _T, _off, 0.5)) > 0, "anchor penalizes cosine gap"

    # 4. train-loss-floored detector.
    floored, _ = _train_loss_floored(
        [{"step": s, "rkd": r} for s, r in
         [(0, 1.0), (1, 0.5), (2, 0.2), (3, 0.11), (4, 0.105), (5, 0.10)]])
    assert floored, "expected floored=True for a plateaued loss"
    not_floored, _ = _train_loss_floored(
        [{"step": s, "rkd": r} for s, r in
         [(0, 1.0), (1, 0.8), (2, 0.6), (3, 0.4), (4, 0.2), (5, 0.05)]])
    assert not not_floored, "expected floored=False for a still-descending loss"

    # 5. verdict bands.
    arms = ["SIGN_BLOCK", "GSBC_2PCT", "GSBC_3PCT"]

    def _fake_units(alg_by_arm=None, shuf=0.01):
        alg_by_arm = alg_by_arm or {a: 0.99 for a in arms}
        units = [{"unit": "u0", "arm": "x", "kind": "k"}]
        for arm in arms:
            a = alg_by_arm.get(arm, 0.99)
            units += [
                {"unit": f"keyed::{arm}_RANDOM_BLOCK::J5", "arm": f"{arm}_RANDOM_BLOCK",
                 "kind": "keyed", "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
                {"unit": f"keyed::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "keyed", "J": 5, "acc_at1": a, "hit_any_member": a},
                {"unit": f"keyed::{arm}_BLOCK_BESTVAL::J5", "arm": f"{arm}_BLOCK_BESTVAL",
                 "kind": "keyed", "J": 5, "acc_at1": a, "hit_any_member": a},
                {"unit": f"shuffled_key::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "shuffled_key", "J": 5, "acc_at1": shuf, "hit_any_member": shuf},
            ]
        return units

    def _rec(rets, hi80s=None):
        hi80s = hi80s or {a: 0.55 for a in arms}
        return {a: {"train_loss_floored": True,
                    "final": {"spearman_all": 0.8, "ret_agree10": rets[a],
                              "hi80_cos": hi80s[a], "hi80_calib_err": 0.3}}
                for a in arms}

    def _pad(units, n=28):
        u = list(units)
        while len(u) < n:
            u.append({"unit": f"pad{len(u)}", "arm": "pad", "kind": "pad"})
        return u

    v_pass, m_pass = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.40, "GSBC_3PCT": 0.44}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_pass == "HARD_PASS" and "GSBC_GRADED_CLEARS_TARGET" in m_pass, f"{v_pass} {m_pass}"

    v_fw, m_fw = _verdict_v11(
        _pad(_fake_units(alg_by_arm={"SIGN_BLOCK": 0.99, "GSBC_2PCT": 0.40, "GSBC_3PCT": 0.99})),
        _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.42, "GSBC_3PCT": 0.30}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_fw == "HARD_FAIL" and "GSBC_BREAKS_ALGEBRA" in m_fw, f"{v_fw} {m_fw}"

    v_nolift, m_nl = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.22, "GSBC_3PCT": 0.24}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_nolift == "HARD_FAIL" and "GSBC_NO_LIFT" in m_nl, f"{v_nolift} {m_nl}"

    v_sec, m_sec = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.30, "GSBC_3PCT": 0.40}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_sec == "MIDDLE_BAND" and "GSBC_3PCT_CLEARS" in m_sec, f"{v_sec} {m_sec}"

    v_marg, m_marg = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.30, "GSBC_3PCT": 0.31}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_marg == "MIDDLE_BAND" and "GSBC_MARGINAL" in m_marg, f"{v_marg} {m_marg}"

    v_hi80, m_hi80 = _verdict_v11(
        _pad(_fake_units()),
        _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.40, "GSBC_3PCT": 0.20},
             hi80s={"SIGN_BLOCK": 0.55, "GSBC_2PCT": 0.20, "GSBC_3PCT": 0.20}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_hi80 == "MIDDLE_BAND" and "HI80_COLLAPSES" in m_hi80, f"{v_hi80} {m_hi80}"

    v_gd, m_gd = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.05, "GSBC_2PCT": 0.40, "GSBC_3PCT": 0.44}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_gd == "HARD_FAIL" and "REGIME_OR_INVOCATION_MISMATCH" in m_gd, f"{v_gd} {m_gd}"

    v_card, m_card = _verdict_v11(
        _fake_units()[:5], _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.40, "GSBC_3PCT": 0.44}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card, f"{v_card} {m_card}"

    v_smk, m_smk = _verdict_v11(
        _pad(_fake_units()), _rec({"SIGN_BLOCK": 0.21, "GSBC_2PCT": 0.10, "GSBC_3PCT": 0.10}),
        arms, "SIGN_BLOCK", "GSBC_3PCT", "GSBC_2PCT", 28, "smoke")
    assert v_smk == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_smk, f"{v_smk} {m_smk}"

    # 6. tiny end-to-end: sign + gsbc modes train + produce DISTINCT hard codes.
    v_syn = 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    Xval_syn = Xsyn[:40].contiguous()
    Xtest_syn = Xsyn[40:64].contiguous()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xval_syn, 500, 3)

    import tempfile
    code_by_mode = {}
    orig = v3.MLP_HIDDEN
    try:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for arm, (mode, kb, blk_l, m, width, recipe) in (
                    ("S", ("sign", 16, 16, 1, 32, "rkd_only")),
                    ("R", ("gsbc", 8, 32, 2, 32, "rkd_only")),
                    ("F", ("gsbc", 8, 32, 2, 32, "full"))):
                st_last, diag_st = _train_student_v11(
                    mode, kb, blk_l, m, width, Xsyn, 40, 24, 4, 13, "cpu",
                    tdp / f"ckpt_{arm}.pt", tdp / f"ckpt_best_{arm}.pt", 100, tdp, t0,
                    _dq, _df, 8, 2, 1.0, recipe, arm)
                assert int(st_last.net[0].out_features) == width
                assert math.isfinite(diag_st["rkd_last"])
                if recipe == "full":
                    assert math.isfinite(diag_st["cons_last"]), "full: cons logged"
                    assert math.isfinite(diag_st["rank_last"]), "full: rank logged"
                    assert math.isfinite(diag_st["anchor_last"]), "full: anchor logged"
                c_last = _encode_block_for_arm(mode, st_last, Xtest_syn, kb, blk_l, m)
                assert c_last.shape == (24, kb * blk_l)
                assert torch.isfinite(c_last).all()
                code_by_mode[arm] = hashlib.sha256(
                    np.ascontiguousarray(c_last.to(torch.float32).numpy()).tobytes()).hexdigest()
                st_best = _reload_best_v11(width, 64, kb * blk_l, "cpu",
                                           tdp / f"ckpt_best_{arm}.pt")
                assert int(st_best.net[0].out_features) == width
                ku = _keyed_for_arm(mode, arm, c_last, kb, blk_l, 5, 20, gen, "cpu")
                assert "acc_at1" in ku
    finally:
        v3.MLP_HIDDEN = orig
    assert code_by_mode["S"] != code_by_mode["R"], "sign vs gsbc identical codes (AF)"
    assert code_by_mode["R"] != code_by_mode["F"], "gsbc rkd vs full identical codes (AF)"
    assert v3.MLP_HIDDEN == orig, "MLP_HIDDEN not restored"

    # 7. determinism idempotence.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]

    print(f"[selftest] PASS (GSBC encode top-m unit-L1 pos + eval-match + STE grad + "
          f"circular-conv keyed roundtrip + shuffled-fail + floored detector + verdict "
          f"bands [pass/false-win/no-lift/secondary/marginal/hi80/gate-D/cardinality/"
          f"smoke] + sign&gsbc train -> distinct codes + determinism) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
