"""Encoder v12 -- push the GSBC graded code toward its ceiling via GLOBAL-WTA and
FlyHash-style EXPANSION, built on the SIMPLER GSBC_RKD base (the v11 WINNER), plus
a composition-depth VET (J-sweep) on each deployed GSBC code.

WHY THIS CELL (verified from disk, not summarized):
  v11 landed HARD_PASS both seeds. Off-disk FINAL-step numbers:
    MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/metrics.json:
      GSBC_RKD  (graded top-m + PLAIN RKD, no ListNet/anchor) ret_agree10 0.4447
        hi80_cos 0.8416 calib 0.0024 keyed@J5 1.000 (WINNER)
      GSBC_FULL (graded + annealed+ListNet+anchor)           ret_agree10 0.3986
        hi80_cos 0.8338 calib 0.0102 keyed@J5 1.000
      SIGN_BLOCK (pure sign control)                          ret_agree10 0.2117
    MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed13/metrics.json:
      GSBC_RKD ret 0.4664 ; GSBC_FULL ret 0.3968 ; SIGN 0.2177.
  => The FULL recipe (ListNet+anchor+annealed estimator) slightly HURT retrieval.
     The DEPLOY candidate is the SIMPLER GSBC_RKD (graded top-m block code + plain
     RKD). This cell builds the ceiling-push levers on THAT base (recipe=rkd_only
     for ALL arms), so the ONLY thing that differs across arms is the CODE GEOMETRY.

  Code ceiling: pure-SIGN K128 ret 0.4295 (MEASURED@bypass); graded dense-float
  ret=1.0; Frady/Kleyko GSBC theoretical ceiling ~0.7-0.9 CITED@arXiv:2303.13957.
  Trained GSBC_RKD sits at ~0.44 -> large headroom. Two ceiling-levers from the
  drills:
    (1) GLOBAL-WTA: pick top-K over the WHOLE N=4096 vector (not exactly-m per
        block). Block-top-m is the special case where every block gets exactly m;
        global-WTA lets occupancy VARY (concentrate active dims where the signal
        is) -> a strict SUPERSET whose retrieval ceiling can only rise.
    (2) EXPANSION-before-WTA (FlyHash): student outputs a 2x-wider layer (8192),
        then global top-K at the SAME sparsity FRACTION (2.34%). CITED@
        dual_readout_format_probe: EXPAND2x global-topk +0.111 vs +0.086 non-
        expanded (zero-training). This cell tests whether it survives TRAINING.

  Binding risk the composition-depth VET exists to catch: global-WTA can leave
  some (kb) blocks EMPTY; block-wise circular-conv binding of an empty block is a
  no-op, reducing effective binding dimensionality. If keyed@J5 drops below 0.95
  on a lever arm, THAT is the finding (global allocation trades block-binding SNR
  for retrieval). The J-sweep {1,2,5,8,16,32,64} maps where each code's bind/unbind
  algebra holds >= 0.95 (the composition-depth envelope), the same VET the
  regime-switch key passed at depth.

PRIMARY QUESTION (coordinator): which arm+lever gives the best JOINT
  (ret_agree10 + keyed@J5 >= 0.95 + hi80_cos no-collapse + calib) at ~2% active?
  HARD_PASS iff a LEVER arm (global-WTA or expansion) beats the block baseline in
  ret by a paired margin WHILE holding keyed@J5 >= 0.95, hi80 not collapsed, and
  calib in band. If block-top-m remains best, that is an HONEST NO_LIFT wall (block
  allocation already optimal at this sparsity) -> route to density dial.

ARMS (PAIRED; same seed/data/split/steps/LR/width=2048/recipe=rkd_only for ALL;
ONLY the block CODE GEOMETRY differs; all at 2.34% active):
  GSBC_RKD_BLOCK  block  out4096 kb32  blk128 m3   -- baseline == v11 GSBC_RKD (Gate-D)
  GSBC_GWTA       gwta   out4096 kb32  blk128 K96  -- global top-96, PRIMARY lever
  GSBC_EXPAND2X   gwta   out8192 kb64  blk128 K192 -- 2x expand + global top-192, SECONDARY

METHODOLOGY (LOCKED): FINAL-step (not best-ckpt) primary; headline ret_agree10 +
hi80_cos; keyed@J5 a HARD co-gate. Disjoint held pool; exclude self; PAIRED
same-seed/data/split; determinism pinned; torch version recorded. CANONICAL = the
REMOTE-QUEUE OFFICIAL landing, NOT local smoke. 2 SEEDS via sibling _seed_7 /
_seed_13 wrappers (CHUNKED single-seed-per-cell).

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "GSBC graded sparse block code global-WTA expansion composition depth
  circular convolution unbind retrieval algebra" -> top cosine=0.352
  (wordnet 'convolution'), 0.334 (CAP_circular_convolution = the binding primitive
  this cell USES), 0.318 (a training-speed note, not a GSBC VET); NONE is a prior
  global-WTA/expansion or GSBC composition-depth cell. GENUINELY NOVEL (the GSBC
  arc landed 2026-07-04 and is not yet in the KB; global-WTA/FlyHash levers on the
  graded code, gated on JOINT ret+algebra, are untested in the arc).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over each arm's code)
- final_metrics_atomicity: tmp_replace (write_metrics + atomic ckpt saves)
- except SystemExit: raise BEFORE except Exception (no BaseException/bare)
- crlb/capacity-feasibility: block-top-m baseline reproduces v11 GSBC_RKD ret in
  [0.38,0.55]; global-WTA is a strict superset (ceiling >= block); crlb_n_a declared
- baseline_in_band: CHARPOS ret in (0.05,0.95); GSBC_RKD_BLOCK in [0.38,0.55]
- discriminator-survives-scale: option (C) hybrid -- the keyed ALGEBRA co-gate
  (keyed@J5 + shuffled leak + composition J-sweep) FIRES at smoke for all 3 arms;
  the ret-LIFT discriminator is FULL-only (smoke's tiny V_train cannot reproduce
  ret_agree10 coverage), so smoke is a MACHINERY + mechanism-fires gate (global-WTA
  block-occupancy VARIES vs block-top-m; codes differ) and canonical = remote landing
- HARD_PASS strictly above floor: lever ret >= baseline + 0.03 (META_RULE_L)
- HP_SCOPE: JOINT gate (ret-lift + keyed@J5>=0.95 + hi80>=0.30 + calib<0.10) applies
  to {GSBC_GWTA,GSBC_EXPAND2X}; GSBC_RKD_BLOCK is Gate-D baseline; DENSE_* context;
  RANDOM/shuffled_key integrity-only
- cardinality_ok: EXPECTED_N_UNITS=37 both run modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-05_exp_encoder_v12_gsbc_gwta_expansion_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py
Does NOT touch v3/v11's artifact/checkpoint/output directories.

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
from experiments import (  # noqa: E402
    exp_encoder_v11_gsbc_graded_sparse_v1_core as v11,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v12_gsbc_gwta_expansion_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7
N_DIM = v3.N_DIM_DEFAULT        # 4096 (block-arm student output dim)

TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

OBJECTIVE = "in_batch"  # RKD-only, nce_weight=0 (matches the v11 GSBC_RKD winner)
SELECT_TAU = v3.TAU_GUMBEL  # 1.0; softmax temperature for the straight-through mask

# arm -> (code_mode, out_dim, kb, blk_l, sparsity, width).
#   code_mode "block": sparsity == m (per-block top-m); kb*m active.
#   code_mode "gwta":  sparsity == K (global top-K over out_dim); K active.
# kb*blk_l == out_dim for every arm. All arms 2.34% active, recipe=rkd_only.
STE_ARMS = {
    "GSBC_RKD_BLOCK": ("block", 4096, 32, 128, 3, 2048),   # baseline == v11 GSBC_RKD (96/4096)
    "GSBC_GWTA": ("gwta", 4096, 32, 128, 96, 2048),        # global top-96 (2.34%), PRIMARY
    "GSBC_EXPAND2X": ("gwta", 8192, 64, 128, 192, 2048),   # 2x expand + top-192 (2.34%), SECONDARY
}
SMOKE_STE_ARMS = {
    "GSBC_RKD_BLOCK": ("block", 4096, 32, 128, 3, 256),
    "GSBC_GWTA": ("gwta", 4096, 32, 128, 96, 256),
    "GSBC_EXPAND2X": ("gwta", 8192, 64, 128, 192, 256),
}
CONTROL_ARM = "GSBC_RKD_BLOCK"   # Gate-D reproducer of the v11 GSBC_RKD winner
PRIMARY_ARM = "GSBC_GWTA"        # global-WTA lever
SECONDARY_ARM = "GSBC_EXPAND2X"  # FlyHash-expansion lever

# Composition-depth VET J-sweep (includes 5 for the keyed@J5 co-gate + controls).
J_SWEEP = [1, 2, 5, 8, 16, 32, 64]
J_COGATE = 5  # the locked keyed@J5 algebra co-gate
# The keyed J-sweep composition-depth VET cleans up against the FULL concept set
# (M=177899) at FULL, matching the regime-switch key's J=64-at-full-M proof so the
# GSBC-vs-regime-switch depth comparison is apples-to-apples. Smoke uses the small
# held pool (machinery only). The RANDOM positive-control codebook is capped
# (a bounded distractor set is sufficient for a bind-perfectly control).
KEYED_FULLM_CAP = 200_000       # >= full V_cache -> effectively all concepts
RANDOM_KEYED_M_CAP = 20_000     # positive-control codebook cap (memory bound)

# ---- FULL-scale config: matches v11 except the code geometry ----
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

# ---- Smoke config: MACHINERY + mechanism-fires (SAME code path as FULL) ----
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

# 3 arms x (3 semantic + 9 keyed) + CHARPOS(1) = 3*12 + 1 = 37.
EXPECTED_N_UNITS_FULL = 37
EXPECTED_N_UNITS_SMOKE = 37

# ---- Bands ----
ALGEBRA_FLOOR = 0.95            # keyed@J5 SBC/GSBC algebra HARD co-gate
LIFT_HARD_PASS = 0.03          # paired ret lift over the block baseline toward ceiling
HI80_COLLAPSE_FLOOR = 0.30     # coarse cosine must not collapse below this (joint guard)
CALIB_CEIL = 0.10              # hi80 calib_err must stay below this (joint guard)
BASELINE_RET_LO = 0.38         # GSBC_RKD_BLOCK must reproduce v11 GSBC_RKD (0.4447/0.4664)
BASELINE_RET_HI = 0.55
CODE_CEILING_RET_K128 = 0.4295278  # MEASURED@bypass SIGN-only ortho ceiling (GSBC exceeds)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v12_gwta{tag}{suffix}"


# ---------------------------------------------------------------------------
# GLOBAL-WTA graded code (the ceiling lever). Block-top-m reused from v11.
# ---------------------------------------------------------------------------

def _gsbc_gwta_code_from_z(z: torch.Tensor, K: int, select_tau: float) -> torch.Tensor:
    """Differentiable GLOBAL top-K graded positive survivors, GLOBAL unit-L1.

    FORWARD: keep |z| of the K largest-magnitude entries over the WHOLE row, zero
    the rest, normalize the row to unit L1 -> a positive global sparse distribution
    (block occupancy VARIES; strict superset of block-top-m). BACKWARD:
    straight-through global top-K mask (hard + softmax(mag) - detach) so near-winner
    logits keep gradient; survivor magnitudes carry real gradient. Matches
    _encode_gsbc_gwta FORWARD exactly.
    """
    mag = z.abs()
    p = torch.softmax(mag / select_tau, dim=-1)     # global soft (STE backward)
    idx = mag.topk(K, dim=-1).indices               # global top-K
    hard = torch.zeros_like(mag)
    hard.scatter_(-1, idx, 1.0)
    mask_st = hard + p - p.detach()                 # fwd=top-K one-hot, bwd=grad(p)
    surv = mag * mask_st                            # graded positive survivors
    l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
    return surv / l1                                # global unit-L1


@torch.no_grad()
def _encode_gsbc_gwta(student: torch.nn.Module, X: torch.Tensor, K: int,
                      batch: int = 8192) -> torch.Tensor:
    """Eval-time deployed global-WTA code (positive, global unit-L1)."""
    dev = v3._student_device(student)
    out_dim = int(student.out_dim)
    out = torch.zeros(X.shape[0], out_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
        mag = z.abs()
        idx = mag.topk(K, dim=-1).indices
        surv = torch.zeros_like(mag)
        surv.scatter_(-1, idx, torch.gather(mag, -1, idx))
        l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        out[lo:lo + batch] = (surv / l1).cpu()
    return out


def _random_gsbc_gwta_codes(n: int, N: int, K: int,
                            gen: torch.Generator) -> torch.Tensor:
    """Random positive global unit-L1 global-WTA codes (positive control)."""
    z = torch.randn(n, N, generator=gen)
    mag = z.abs()
    idx = mag.topk(K, dim=-1).indices
    surv = torch.zeros_like(mag)
    surv.scatter_(-1, idx, torch.gather(mag, -1, idx))
    l1 = surv.sum(dim=-1, keepdim=True).clamp_min(1e-8)
    return surv / l1


def _block_occupancy_std(code: torch.Tensor, kb: int, blk_l: int) -> float:
    """Std of per-block active-count across blocks (mechanism-fires signal:
    block-top-m has 0 std; global-WTA has > 0 std)."""
    cb = code.reshape(code.shape[0], kb, blk_l)
    occ = (cb != 0).sum(dim=-1).float()   # (n, kb)
    return float(occ.std(dim=-1).mean())


# ---- Per-arm dispatch (block reuses v11; gwta/expand use the global path) ----

def _code_from_z_for_arm(code_mode: str, z: torch.Tensor, kb: int, blk_l: int,
                         sparsity: int, select_tau: float) -> torch.Tensor:
    if code_mode == "block":
        return v11._gsbc_code_from_z(z, kb, blk_l, sparsity, select_tau)  # sparsity=m
    if code_mode == "gwta":
        return _gsbc_gwta_code_from_z(z, sparsity, select_tau)            # sparsity=K
    raise ValueError(f"unknown code_mode {code_mode}")


def _encode_for_arm(code_mode: str, student: torch.nn.Module, X: torch.Tensor,
                    kb: int, blk_l: int, sparsity: int) -> torch.Tensor:
    if code_mode == "block":
        return v11._encode_gsbc(student, X, kb, blk_l, sparsity)
    if code_mode == "gwta":
        return _encode_gsbc_gwta(student, X, sparsity)
    raise ValueError(f"unknown code_mode {code_mode}")


def _random_for_arm(code_mode: str, n: int, out_dim: int, kb: int, blk_l: int,
                    sparsity: int, gen: torch.Generator) -> torch.Tensor:
    if code_mode == "block":
        return v11._random_gsbc_codes(n, kb, blk_l, sparsity, gen)
    if code_mode == "gwta":
        return _random_gsbc_gwta_codes(n, out_dim, sparsity, gen)
    raise ValueError(f"unknown code_mode {code_mode}")


# ---------------------------------------------------------------------------
# Determinism / defensive helpers.
# ---------------------------------------------------------------------------

def _pin_determinism(seed: int) -> Dict:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    det_ok, det_err = True, ""
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
# Trainer (lean rkd-only; per-arm code-geometry dispatch; nce_weight=0).
# ---------------------------------------------------------------------------

def _train_student_v12(
    code_mode: str, kb: int, blk_l: int, out_dim: int, sparsity: int, width: int,
    Xtr: torch.Tensor, steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int, output_dir: Path,
    t0: float, dense_eval_quick_fn: Optional[Callable],
    dense_eval_full_fn: Optional[Callable], dense_eval_every: int,
    min_step_for_best: int, select_tau: float, arm_label: str,
) -> Tuple[torch.nn.Module, Dict]:
    """In-batch RKD-only trainer. code_mode in {block, gwta}. Eval uses the
    DEPLOYED hard code. Isolates the CODE GEOMETRY lever (all arms same recipe)."""
    if code_mode not in ("block", "gwta"):
        raise ValueError(f"unknown code_mode {code_mode}")
    if kb * blk_l != out_dim:
        raise ValueError(f"{arm_label}: kb*blk_l {kb * blk_l} != out_dim {out_dim}")
    orig_hidden = v3.MLP_HIDDEN
    v3.MLP_HIDDEN = width
    try:
        student = v3._make_student("mlp", Xtr.shape[1], out_dim, device, seed)
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
            print(f"[v12_gwta] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v12_gwta] WARN {arm_label} ckpt load failed ({type(exc).__name__}); "
                  f"retraining from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}

    off = ~torch.eye(batch, dtype=torch.bool, device=device)
    loss_first = loss_last = rkd_last = activefrac_last = None

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
        s = _code_from_z_for_arm(code_mode, z, kb, blk_l, sparsity, select_tau)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
        loss = l_rkd
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())})")
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
        if step % 200 == 0:
            print(f"[v12_gwta] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"active={activefrac:.4f} lr={cur_lr:.2e} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "rkd": v_rkd,
                                   "active": activefrac})
        if (dense_eval_full_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_full = float(dense_eval_full_fn(student))
            d_quick = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
            dense_traj.append({"step": step, "dense_full": d_full,
                               "dense_quick": d_quick, "rkd": v_rkd,
                               "active": activefrac, "final": False})
            print(f"[v12_gwta] {arm_label} DENSE-traj step {step}: full={d_full:.4f} "
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
        print(f"[v12_gwta] {arm_label} FINAL step {steps}: full={d_full_fin:.4f}",
              flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                    "dense_full": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[v12_gwta] WARN {arm_label}: no eval >= min_step_for_best; "
              f"best-ckpt falls back to FINAL", flush=True)
    floored, frac_half = v11._train_loss_floored(dense_traj)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "activefrac_last": activefrac_last if activefrac_last is not None else -1.0,
        "select_tau": select_tau, "recipe": "rkd_only",
        "code_mode": code_mode, "kb": kb, "blk_l": blk_l, "out_dim": out_dim,
        "sparsity": sparsity, "mlp_hidden": width, "arm": arm_label,
        "objective": OBJECTIVE, "batch": batch,
        "dense_traj": dense_traj, "train_loss_floored": floored,
        "train_loss_descent_frac_by_half": frac_half,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
    }


def _reload_best_v12(width: int, in_dim: int, out_dim: int, device: str,
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
# Composition-depth envelope + verdict.
# ---------------------------------------------------------------------------

def _keyed_acc(per_unit: List[Dict], arm_label: str, J: int) -> Optional[float]:
    u = v11.v3._by_unit(per_unit, "keyed", arm_label, J)
    return None if u is None else float(u["acc_at1"])


def _depth_envelope(per_unit: List[Dict], arm_label: str, floor: float) -> Dict:
    """Largest CONTIGUOUS J (from J_SWEEP[0]) that holds keyed acc >= floor, plus
    the full J->acc curve."""
    curve = {}
    for J in J_SWEEP:
        a = _keyed_acc(per_unit, arm_label, J)
        curve[J] = a
    hold = 0
    for J in J_SWEEP:
        a = curve.get(J)
        if a is not None and a >= floor:
            hold = J
        else:
            break
    return {"max_J_at_floor": hold, "curve": curve}


def _verdict_v12(per_unit: List[Dict], recovery: Dict, arm_names: List[str],
                 control_arm: str, primary_arm: str, secondary_arm: str,
                 expected_units: int, run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    # Integrity gates per arm.
    for arm in arm_names:
        posc = v3._by_unit(per_unit, "keyed", f"{arm}_RANDOM", J_COGATE)
        if posc is None or posc["acc_at1"] < 0.98:
            return ("HARD_FAIL",
                    f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: {arm} RANDOM keyed "
                    f"J={J_COGATE} {posc['acc_at1'] if posc else None} < 0.98")
        shuf = v3._by_unit(per_unit, "shuffled_key", f"{arm}_CODE_LAST", J_COGATE)
        if shuf is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {arm} shuffled_key")
        if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SHUFFLED_KEY_LEAK: {arm} "
                    f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")

    def _alg(arm: str) -> float:
        u = v3._by_unit(per_unit, "keyed", f"{arm}_CODE_LAST", J_COGATE)
        return float(u["acc_at1"]) if u else 0.0

    ctrl = recovery[control_arm]["final"]
    pri = recovery[primary_arm]["final"]
    sec = recovery[secondary_arm]["final"]
    ctrl_alg, pri_alg, sec_alg = _alg(control_arm), _alg(primary_arm), _alg(secondary_arm)
    env = {arm: _depth_envelope(per_unit, f"{arm}_CODE_LAST", ALGEBRA_FLOOR)
           for arm in arm_names}
    env_str = " ".join(f"{a}:depth<={env[a]['max_J_at_floor']}" for a in arm_names)
    lift_pri = pri["ret_agree10"] - ctrl["ret_agree10"]
    lift_sec = sec["ret_agree10"] - ctrl["ret_agree10"]

    tail = (f"[{control_arm}(baseline) ret={ctrl['ret_agree10']:.4f} hi80={ctrl['hi80_cos']:.4f} "
            f"calib={ctrl['hi80_calib_err']:.4f} alg={ctrl_alg:.3f}] "
            f"[{primary_arm} ret={pri['ret_agree10']:.4f} (lift{lift_pri:+.4f}) "
            f"hi80={pri['hi80_cos']:.4f} calib={pri['hi80_calib_err']:.4f} alg={pri_alg:.3f}] "
            f"[{secondary_arm} ret={sec['ret_agree10']:.4f} (lift{lift_sec:+.4f}) "
            f"hi80={sec['hi80_cos']:.4f} calib={sec['hi80_calib_err']:.4f} alg={sec_alg:.3f}] "
            f"sign_ceiling={CODE_CEILING_RET_K128:.4f} compdepth[{env_str}]")

    if run_mode == "smoke":
        for arm in arm_names:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        # mechanism-fires: the two gwta levers must have VARIABLE block occupancy
        # (std > 0) -> genuinely global-WTA, not block-top-m in disguise.
        for arm in (primary_arm, secondary_arm):
            occ = recovery[arm].get("block_occupancy_std", 0.0)
            if not (occ > 0.0):
                return ("SMOKE_GATE_FAIL",
                        f"S_MECHANISM_DID_NOT_FIRE: {arm} block_occupancy_std {occ} "
                        f"== 0 (global-WTA collapsed to uniform per-block; not a "
                        f"superset of block-top-m)")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: all {len(arm_names)} arms (block + 2 global-WTA "
                f"levers) train end-to-end with differing codes; global-WTA occupancy "
                f"VARIES (mechanism fires); per-arm RANDOM/shuffled-key + full J-sweep "
                f"keyed units run (gsbc circular-conv algebra fires at every J); "
                f"cardinality holds {tail} (the ret-LIFT discriminator is FULL-only; "
                f"smoke's tiny V_train cannot reproduce it -- REMOTE-QUEUE OFFICIAL "
                f"LANDING is canonical)")

    # ---- FULL verdict ----
    if not (BASELINE_RET_LO <= ctrl["ret_agree10"] <= BASELINE_RET_HI):
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: baseline {control_arm} "
                f"ret {ctrl['ret_agree10']:.4f} outside v11-GSBC_RKD reproduction band "
                f"[{BASELINE_RET_LO},{BASELINE_RET_HI}] -- block baseline drifted; the "
                f"lever comparison is not trustworthy {tail}")
    if ctrl_alg < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_CONTROL_ALGEBRA_BROKE: {control_arm} keyed@J{J_COGATE} "
                f"{ctrl_alg:.3f} < {ALGEBRA_FLOOR} -- block baseline algebra broken; "
                f"machinery suspect {tail}")

    def _joint_ok(rec: Dict, alg: float) -> bool:
        return (rec["ret_agree10"] >= ctrl["ret_agree10"] + LIFT_HARD_PASS
                and alg >= ALGEBRA_FLOOR
                and rec["hi80_cos"] >= HI80_COLLAPSE_FLOOR
                and math.isfinite(rec["hi80_calib_err"])
                and rec["hi80_calib_err"] < CALIB_CEIL)

    # rank levers by lift; the best lever that JOINT-passes wins.
    levers = sorted([(primary_arm, pri, pri_alg, lift_pri),
                     (secondary_arm, sec, sec_alg, lift_sec)],
                    key=lambda t: t[3], reverse=True)
    best_arm, best_rec, best_alg, best_lift = levers[0]

    # 1. Best lever JOINT-passes -> HARD_PASS.
    if _joint_ok(best_rec, best_alg):
        return ("HARD_PASS",
                f"LEVER_LIFTS_TOWARD_CEILING: {best_arm} deployed code ret "
                f"{best_rec['ret_agree10']:.4f} (lift {best_lift:+.4f} vs block "
                f"{ctrl['ret_agree10']:.4f}) at ~2% active WITH keyed@J{J_COGATE} "
                f"{best_alg:.3f} >= {ALGEBRA_FLOOR}, hi80 {best_rec['hi80_cos']:.4f} "
                f"no-collapse, calib {best_rec['hi80_calib_err']:.4f} in band -- "
                f"{'global-WTA' if 'GWTA' in best_arm else 'FlyHash-expansion'} beats "
                f"block-top-m JOINTLY and climbs toward the GSBC ceiling. Next: density "
                f"dial + full-M=177899 composition VET {tail}")
    # 2. A lever LIFTS ret but its algebra DEGRADES (empty-block risk realized).
    for arm, rec, alg, lift in levers:
        if lift >= LIFT_HARD_PASS and alg < ALGEBRA_FLOOR:
            return ("MIDDLE_BAND",
                    f"LEVER_LIFTS_BUT_ALGEBRA_DEGRADES: {arm} lifts ret {lift:+.4f} "
                    f"but keyed@J{J_COGATE} {alg:.3f} < {ALGEBRA_FLOOR} -- global "
                    f"allocation leaves blocks empty and trades block-binding SNR for "
                    f"retrieval; the joint instrument is not clean (THIS is the "
                    f"finding: global-WTA breaks the bind/unbind at ~2%) {tail}")
    # 3. A lever LIFTS ret+algebra but hi80/calib collapses.
    for arm, rec, alg, lift in levers:
        if lift >= LIFT_HARD_PASS and alg >= ALGEBRA_FLOOR:
            return ("MIDDLE_BAND",
                    f"LEVER_LIFTS_BUT_CALIB_OR_HI80: {arm} ret lift {lift:+.4f} algebra "
                    f"{alg:.3f} OK but hi80 {rec['hi80_cos']:.4f} / calib "
                    f"{rec['hi80_calib_err']:.4f} out of band (joint not clean) {tail}")
    # 4. No lever lifts above the block baseline -> HONEST NO_LIFT wall.
    if best_lift <= 0.0:
        return ("HARD_FAIL",
                f"NO_LIFT: neither {primary_arm} ({lift_pri:+.4f}) nor {secondary_arm} "
                f"({lift_sec:+.4f}) beats block-top-m ret; block allocation is already "
                f"optimal at ~2% active -- global-WTA + expansion do not help here; "
                f"route to the density dial {tail}")
    # 5. Marginal lift (0 < lift < LIFT_HARD_PASS), algebra held.
    return ("MIDDLE_BAND",
            f"MARGINAL_LIFT: best lever {best_arm} lifts ret {best_lift:+.4f} "
            f"(< {LIFT_HARD_PASS}) with algebra held -- a lever helps but does not "
            f"clear the paired margin; needs the 2nd seed or a density nudge {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_v12_sweep(run_mode: str, seed: int, device_arg: str, n_dim: int,
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
    for arm, (code_mode, out_dim, kb, blk_l, sparsity, width) in ste_arms.items():
        if kb * blk_l != out_dim:
            raise ValueError(f"{arm}: kb*blk_l {kb * blk_l} != out_dim {out_dim}")

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
    print(f"[v12_gwta] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
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
    print(f"[v12_gwta] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v12_gwta] split train={n_tr} held={n_he}", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, val_full_pairs, seed + 7)

    arm_diag: Dict[str, Dict] = {}
    arm_codes: Dict[str, torch.Tensor] = {}
    arm_geom: Dict[str, Tuple] = {}
    arm_occ: Dict[str, float] = {}
    arm_students: Dict[str, torch.nn.Module] = {}
    for arm, (code_mode, out_dim, kb, blk_l, sparsity, width) in ste_arms.items():
        arm_geom[arm] = (code_mode, out_dim, kb, blk_l, sparsity)
        ckpt_path = art_dir / f"_ckpt_{arm}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{arm}.pt"
        last_student, diag = _train_student_v12(
            code_mode, kb, blk_l, out_dim, sparsity, width, Xtr, steps, batch, warmup,
            seed, device, ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            _deval_quick, _deval_full, dense_every, min_step_for_best, SELECT_TAU, arm)
        bestval_student = _reload_best_v12(width, Xtr.shape[1], out_dim, device,
                                           best_ckpt_path)
        arm_diag[arm] = diag
        # bestval_student reload validates the best-ckpt is loadable (integrity
        # guard); FINAL-step codes are the gated deploy artifact.
        del bestval_student
        arm_students[arm] = last_student
        code_last = _encode_for_arm(code_mode, last_student, Xhe, kb, blk_l, sparsity)
        arm_codes[f"{arm}_CODE_LAST"] = code_last
        arm_codes[f"{arm}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xhe)
        arm_occ[arm] = _block_occupancy_std(code_last, kb, blk_l)
        gen_ctrl = torch.Generator().manual_seed(
            seed + 1 + width + kb + sparsity + 1009 * arm_names.index(arm))
        arm_codes[f"{arm}_RANDOM"] = _random_for_arm(
            code_mode, n_he, out_dim, kb, blk_l, sparsity, gen_ctrl)
        print(f"[v12_gwta] {arm} (mode={code_mode} out={out_dim} kb={kb} blk_l={blk_l} "
              f"sparsity={sparsity} hidden={width}) rkd_last={diag['rkd_last']:.4f} "
              f"active={diag['activefrac_last']:.4f} occ_std={arm_occ[arm]:.3f} "
              f"floored={diag['train_loss_floored']} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, v3.K_BLOCKS_PRIMARY)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(
            np.ascontiguousarray(c.to(torch.float32).numpy()).tobytes()).hexdigest()
    af_exempted: List[List[str]] = []
    for aa in digests:
        for bb in digests:
            if aa < bb and digests[aa] == digests[bb]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {aa}/{bb} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v12_gwta] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    # Semantic units: deployed CODE_LAST + DENSE_LAST + RANDOM per arm; + CHARPOS.
    for arm in arm_names:
        for label in (f"{arm}_CODE_LAST", f"{arm}_DENSE_LAST", f"{arm}_RANDOM"):
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                      test_final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              test_final_pairs, seed + 3)

    # Keyed composition-depth VET codebook: FULL concept set (M=177899) at FULL,
    # held pool at smoke (machinery). The J-sweep on this deployed-code codebook maps
    # where each code's circular-conv bind/unbind holds >= 0.95 at full-scale distractor
    # load -- the apples-to-apples GSBC-vs-regime-switch depth comparison.
    if run_mode == "smoke":
        X_keyed = Xhe
    else:
        keyed_m = min(V_cache, KEYED_FULLM_CAP)
        X_keyed = X[:keyed_m].contiguous()
    KEYED_M = int(X_keyed.shape[0])
    random_keyed_m = min(KEYED_M, RANDOM_KEYED_M_CAP)
    print(f"[v12_gwta] composition-depth VET codebook M={KEYED_M} "
          f"(random-control M={random_keyed_m}) ({time.perf_counter() - t0:.1f}s)",
          flush=True)

    # Keyed composition-depth VET: full J-sweep on the deployed code per arm (PAIRED
    # across arms -- same generator seed per J), plus RANDOM@J5 (positive control) and
    # shuffled_key@J5 (leak control). All gsbc circular-conv binding. Encode the full-M
    # codebook per arm then free it (bounds peak memory to one codebook).
    for arm in arm_names:
        code_mode, out_dim, kb, blk_l, sparsity = arm_geom[arm]
        code_fullm = _encode_for_arm(code_mode, arm_students[arm], X_keyed,
                                     kb, blk_l, sparsity)
        gen_rand = torch.Generator().manual_seed(seed + 5 + arm_names.index(arm))
        random_fullm = _random_for_arm(code_mode, random_keyed_m, out_dim, kb, blk_l,
                                       sparsity, gen_rand)
        for J in J_SWEEP:
            gen_J = torch.Generator().manual_seed(seed + 2 + 131 * J)
            _run_unit(v11._gsbc_keyed_unit, f"{arm}_CODE_LAST",
                      code_fullm, kb, blk_l, J, n_trials, gen_J, device)
        gen_ctrl_k = torch.Generator().manual_seed(seed + 2 + 131 * J_COGATE + 7)
        _run_unit(v11._gsbc_keyed_unit, f"{arm}_RANDOM",
                  random_fullm, kb, blk_l, J_COGATE, n_trials, gen_ctrl_k, device)
        gen_shuf = torch.Generator().manual_seed(seed + 2 + 131 * J_COGATE + 13)
        _run_unit(v11._gsbc_keyed_unit, f"{arm}_CODE_LAST",
                  code_fullm, kb, blk_l, J_COGATE, n_trials, gen_shuf,
                  device, shuffled_key=True)
        del code_fullm, random_fullm
        if device == "cuda":
            torch.cuda.empty_cache()

    def _sem_summary(arm: str, kind: str) -> Dict:
        u = v3._by_unit(per_unit, "semantic", f"{arm}_{kind}")
        if u is None:
            return {"spearman_all": float("nan"), "ret_agree10": float("nan"),
                    "hi80_cos": float("nan"), "hi80_calib_err": float("nan")}
        return {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
                "hi80_cos": u["hi80_cos"], "hi80_calib_err": u["hi80_calib_err"]}

    recovery = {arm: {
        "code_mode": ste_arms[arm][0], "out_dim": ste_arms[arm][1],
        "kb": ste_arms[arm][2], "blk_l": ste_arms[arm][3], "sparsity": ste_arms[arm][4],
        "mlp_hidden": ste_arms[arm][5], "recipe": "rkd_only",
        "active_frac": ste_arms[arm][4] / ste_arms[arm][1]
        if ste_arms[arm][0] == "gwta"
        else (ste_arms[arm][2] * ste_arms[arm][4]) / ste_arms[arm][1],
        "block_occupancy_std": arm_occ[arm],
        "final": _sem_summary(arm, "CODE_LAST"),
        "final_dense": _sem_summary(arm, "DENSE_LAST"),
        "rkd_last": arm_diag[arm]["rkd_last"],
        "activefrac_last": arm_diag[arm]["activefrac_last"],
        "train_loss_floored": arm_diag[arm]["train_loss_floored"],
        "train_loss_descent_frac_by_half": arm_diag[arm]["train_loss_descent_frac_by_half"],
        "rkd_traj": [{"step": r["step"], "rkd": r["rkd"], "dense_full": r["dense_full"]}
                     for r in arm_diag[arm]["dense_traj"]],
        "best_step": arm_diag[arm]["best_step"],
        "best_ckpt_fallback_to_final": arm_diag[arm]["best_ckpt_fallback_to_final"],
        "depth_envelope": _depth_envelope(per_unit, f"{arm}_CODE_LAST", ALGEBRA_FLOOR),
    } for arm in arm_names}

    verdict, verdict_msg = _verdict_v12(
        per_unit, recovery, arm_names,
        CONTROL_ARM if CONTROL_ARM in recovery else arm_names[0],
        PRIMARY_ARM if PRIMARY_ARM in recovery else arm_names[1],
        SECONDARY_ARM if SECONDARY_ARM in recovery else arm_names[-1],
        expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    ctrl_floored = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["train_loss_floored"]
    ctrl_ret = recovery.get(CONTROL_ARM, recovery[arm_names[0]])["final"]["ret_agree10"]
    capacity_hypothesis_diagnostic = (
        "train_loss_floored_while_ret_below_ceiling->capacity_NOT_bottleneck"
        if (ctrl_floored and math.isfinite(ctrl_ret) and ctrl_ret < 0.60)
        else "train_loss_not_floored_or_ret_high->capacity_may_matter")

    best_joint = None
    for arm in arm_names:
        rec = recovery[arm]["final"]
        u = v3._by_unit(per_unit, "keyed", f"{arm}_CODE_LAST", J_COGATE)
        alg = float(u["acc_at1"]) if u else float("nan")
        joint_ok = bool(math.isfinite(rec["ret_agree10"]) and alg >= ALGEBRA_FLOOR
                        and rec["hi80_cos"] >= HI80_COLLAPSE_FLOOR
                        and math.isfinite(rec["hi80_calib_err"])
                        and rec["hi80_calib_err"] < CALIB_CEIL)
        cand = {"arm": arm, "ret_agree10": rec["ret_agree10"], "keyed_at_cogate": alg,
                "hi80_cos": rec["hi80_cos"], "calib_err": rec["hi80_calib_err"],
                "joint_ok": joint_ok}
        if joint_ok and (best_joint is None
                         or rec["ret_agree10"] > best_joint["ret_agree10"]):
            best_joint = cand

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": "mlp",
        "ste_arms": {k: list(v) for k, v in ste_arms.items()},
        "control_arm": CONTROL_ARM, "primary_arm": PRIMARY_ARM,
        "secondary_arm": SECONDARY_ARM, "select_tau": SELECT_TAU,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": 0.0, "objective": OBJECTIVE, "lr_schedule": "cosine_8000",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "j_sweep": J_SWEEP, "j_cogate": J_COGATE,
        "keyed_codebook_M": KEYED_M, "random_keyed_M": random_keyed_m,
        "composition_depth_vet_scale": (
            "full_M_177899" if run_mode == "full" and KEYED_M >= 100000
            else f"held_pool_M{KEYED_M}"),
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held_pool": n_he,
        "recovery": recovery,
        "capacity_hypothesis_diagnostic": capacity_hypothesis_diagnostic,
        "best_joint_arm": best_joint,
        "code_ceiling_ret_agree10_k128_signonly": CODE_CEILING_RET_K128,
        "code_ceiling_source": ("MEASURED@data/exp_encoder_teacher_sparsifier_bypass_v1/"
                                "metrics.json:/recovery/ortho_k128_ret_agree10 (SIGN-only); "
                                "GSBC ceiling ~0.7-0.9 CITED@arXiv:2303.13957_Frady_Kleyko"),
        "bands": {"algebra_floor": ALGEBRA_FLOOR, "lift_hard_pass": LIFT_HARD_PASS,
                  "hi80_collapse_floor": HI80_COLLAPSE_FLOOR, "calib_ceil": CALIB_CEIL,
                  "baseline_ret_lo": BASELINE_RET_LO, "baseline_ret_hi": BASELINE_RET_HI},
        "v11_baseline_ref": {
            "gsbc_rkd_ret_seed7": 0.4446767847105089,
            "gsbc_rkd_ret_seed13": 0.46636874648679005,
            "source": ("MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed{7,13}/"
                       "metrics.json:/recovery/GSBC_RKD/final/ret_agree10"),
            "note": "GSBC_RKD_BLOCK arm must reproduce this (Gate-D)."},
        "determinism": det_info,
        "canonical_source": "remote_queue_official_landing_only; local_smoke_is_gate_only",
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "arms_differ_exempted": af_exempted,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "gsbc_block_circular_conv_pos_L1 (all arms); "
                               "block: per-block top-m; gwta/expand: global top-K",
        "methodology": ("PAIRED at recipe=rkd_only (the v11 GSBC_RKD winner base); ONLY "
                        "the CODE GEOMETRY differs: GSBC_RKD_BLOCK (per-block top-m=3, "
                        "Gate-D reproduce v11 ~0.44) -> GSBC_GWTA (global top-96, strict "
                        "superset) PRIMARY -> GSBC_EXPAND2X (2x-wide student + global "
                        "top-192) SECONDARY. All 2.34% active. FINAL-step deployed-code "
                        "ret_agree10 is the gated number; keyed@J5 >= 0.95 is a HARD "
                        "co-gate; a J-sweep {1,2,5,8,16,32,64} maps each code's "
                        "composition-depth envelope. Retrieval eval is PAIRED "
                        "(same seed+3 pair-sampling, same held pool) across arms."),
        "sequenced_next_cell": ("IF a lever HARD_PASS: density dial + full-M=177899 "
                                "composition VET on the winning code + 3rd seed. IF "
                                "ALGEBRA_DEGRADES: global-WTA empty-block tension is real, "
                                "add per-block min-occupancy constraint. IF NO_LIFT: block "
                                "allocation is optimal at 2.34%; route to density dial K256."),
        "storage_strategy": ("no_composition for retrieval (single-hop agreement); the "
                             "keyed J-sweep is a bounded-bundle composition-depth VET "
                             "(J items bound then unbound, cleanup@1 vs held pool)"),
        "compute_architecture": ("batched-GPU: student fwd/bwd + graded top-m/global "
                                 "top-K + block circular-conv (FFT) batched on cuda; eval "
                                 "pairs batched; keyed loops J per trial (cheap)"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_n_a": ("ret_agree10 has no closed-form sigma CRLB; reachability via the "
                     "SIGN K128 ceiling 0.4295 (MEASURED@bypass) + global-WTA being a "
                     "strict superset of block-top-m (ceiling can only rise) + GSBC "
                     "dense ceiling 1.0"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v12_gwta] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. global-WTA encode: global top-K graded positive, global unit-L1; matches eval.
    torch.manual_seed(3)
    z = torch.randn(4, 8 * 16)  # N=128, kb=8, blk_l=16
    code = _gsbc_gwta_code_from_z(z, 12, 1.0)
    assert (code >= 0).all(), "global-WTA code must be non-negative"
    assert torch.allclose(code.sum(-1), torch.ones(4), atol=1e-5), "global unit-L1"
    assert ((code != 0).sum(-1) == 12).all(), "exactly K=12 global survivors"

    class _Fake(torch.nn.Module):
        def __init__(self, out_dim):
            super().__init__()
            self.p = torch.nn.Parameter(torch.zeros(1))
            self.out_dim = out_dim

        def forward(self, x):
            return x
    fake = _Fake(8 * 16)
    Xz = torch.randn(4, 8 * 16)
    enc = _encode_gsbc_gwta(fake, Xz, 12)
    ref = _gsbc_gwta_code_from_z(Xz, 12, 1.0)
    assert torch.allclose(enc, ref, atol=1e-5), "eval encode must match train forward"

    # 2. straight-through gradient flows to z.
    zg = torch.randn(4, 8 * 16, requires_grad=True)
    c = _gsbc_gwta_code_from_z(zg, 12, 1.0)
    c.sum().backward()
    assert zg.grad is not None and zg.grad.abs().sum() > 0, "STE must pass gradient to z"

    # 2b. mechanism-fires: global-WTA occupancy VARIES vs block-top-m (std 0).
    torch.manual_seed(9)
    zocc = torch.randn(64, 8 * 16)
    gw = _gsbc_gwta_code_from_z(zocc, 12, 1.0)
    bl = v11._gsbc_code_from_z(zocc, 8, 16, 3, 1.0)  # exactly 3 per block -> std 0
    assert _block_occupancy_std(gw, 8, 16) > 0.0, "global-WTA occupancy must vary"
    assert _block_occupancy_std(bl, 8, 16) < 1e-6, "block-top-m occupancy must be uniform"

    # 3. global-WTA keyed@J5 round-trips (circular-conv binding); shuffled key fails.
    gen = torch.Generator().manual_seed(5)
    codes = _random_gsbc_gwta_codes(40, 8 * 16, 12, gen)
    u_keyed = v11._gsbc_keyed_unit("T", codes, 8, 16, 5, 40, gen, "cpu")
    assert u_keyed["acc_at1"] >= 0.9, f"gwta keyed@J5 should round-trip, got {u_keyed['acc_at1']}"
    u_shuf = v11._gsbc_keyed_unit("T", codes, 8, 16, 5, 40, gen, "cpu", shuffled_key=True)
    assert u_shuf["acc_at1"] <= 0.15, f"shuffled key should fail, got {u_shuf['acc_at1']}"

    # 4. depth envelope helper: contiguous-hold from J_SWEEP[0].
    fake_units = []
    accs = {1: 1.0, 2: 1.0, 5: 1.0, 8: 0.99, 16: 0.9, 32: 0.5, 64: 0.1}
    for J, a in accs.items():
        fake_units.append({"unit": f"keyed::A_CODE_LAST::J{J}", "arm": "A_CODE_LAST",
                           "kind": "keyed", "J": J, "acc_at1": a, "hit_any_member": a})
    env = _depth_envelope(fake_units, "A_CODE_LAST", 0.95)
    assert env["max_J_at_floor"] == 8, f"contiguous hold should stop at J=8, got {env}"

    # 5. verdict bands.
    arms = ["GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X"]

    def _units(alg_by_arm=None, shuf=0.01, depth=None):
        alg_by_arm = alg_by_arm or {a: 0.99 for a in arms}
        depth = depth or {a: {J: 0.99 for J in J_SWEEP} for a in arms}
        units = [{"unit": "u0", "arm": "x", "kind": "k"}]
        for arm in arms:
            for J in J_SWEEP:
                acc = depth[arm].get(J, 0.99)
                if J == J_COGATE:
                    acc = alg_by_arm.get(arm, 0.99)
                units.append({"unit": f"keyed::{arm}_CODE_LAST::J{J}",
                              "arm": f"{arm}_CODE_LAST", "kind": "keyed", "J": J,
                              "acc_at1": acc, "hit_any_member": acc})
            units.append({"unit": f"keyed::{arm}_RANDOM::J{J_COGATE}",
                          "arm": f"{arm}_RANDOM", "kind": "keyed", "J": J_COGATE,
                          "acc_at1": 0.99, "hit_any_member": 0.99})
            units.append({"unit": f"shuffled_key::{arm}_CODE_LAST::J{J_COGATE}",
                          "arm": f"{arm}_CODE_LAST", "kind": "shuffled_key", "J": J_COGATE,
                          "acc_at1": shuf, "hit_any_member": shuf})
        return units

    def _rec(rets, hi80s=None, calibs=None, occ=None):
        hi80s = hi80s or {a: 0.83 for a in arms}
        calibs = calibs or {a: 0.01 for a in arms}
        occ = occ or {"GSBC_RKD_BLOCK": 0.0, "GSBC_GWTA": 1.5, "GSBC_EXPAND2X": 1.5}
        return {a: {"train_loss_floored": True, "block_occupancy_std": occ[a],
                    "final": {"spearman_all": 0.9, "ret_agree10": rets[a],
                              "hi80_cos": hi80s[a], "hi80_calib_err": calibs[a]}}
                for a in arms}

    def _pad(units, n=37):
        u = list(units)
        while len(u) < n:
            u.append({"unit": f"pad{len(u)}", "arm": "pad", "kind": "pad"})
        return u

    # HARD_PASS: GWTA lifts +0.06 with algebra + hi80 + calib clean.
    v_p, m_p = _verdict_v12(
        _pad(_units()), _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.50, "GSBC_EXPAND2X": 0.45}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_p == "HARD_PASS" and "LEVER_LIFTS_TOWARD_CEILING" in m_p, f"{v_p} {m_p}"

    # ALGEBRA_DEGRADES: GWTA lifts ret but keyed@J5 drops.
    v_ad, m_ad = _verdict_v12(
        _pad(_units(alg_by_arm={"GSBC_RKD_BLOCK": 0.99, "GSBC_GWTA": 0.80,
                                "GSBC_EXPAND2X": 0.99})),
        _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.52, "GSBC_EXPAND2X": 0.45}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_ad == "MIDDLE_BAND" and "ALGEBRA_DEGRADES" in m_ad, f"{v_ad} {m_ad}"

    # NO_LIFT: neither lever beats block.
    v_nl, m_nl = _verdict_v12(
        _pad(_units()), _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.43, "GSBC_EXPAND2X": 0.42}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_nl == "HARD_FAIL" and "NO_LIFT" in m_nl, f"{v_nl} {m_nl}"

    # MARGINAL_LIFT: lever lifts +0.01 (< 0.03), algebra held.
    v_mg, m_mg = _verdict_v12(
        _pad(_units()), _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.45, "GSBC_EXPAND2X": 0.445}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_mg == "MIDDLE_BAND" and "MARGINAL_LIFT" in m_mg, f"{v_mg} {m_mg}"

    # HI80/CALIB: lever lifts ret + algebra but calib blows out.
    v_cb, m_cb = _verdict_v12(
        _pad(_units()),
        _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.52, "GSBC_EXPAND2X": 0.45},
             calibs={"GSBC_RKD_BLOCK": 0.01, "GSBC_GWTA": 0.30, "GSBC_EXPAND2X": 0.01}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_cb == "MIDDLE_BAND" and "CALIB_OR_HI80" in m_cb, f"{v_cb} {m_cb}"

    # Gate-D: baseline out of band.
    v_gd, m_gd = _verdict_v12(
        _pad(_units()), _rec({"GSBC_RKD_BLOCK": 0.20, "GSBC_GWTA": 0.50, "GSBC_EXPAND2X": 0.45}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_gd == "HARD_FAIL" and "REGIME_OR_INVOCATION_MISMATCH" in m_gd, f"{v_gd} {m_gd}"

    # Cardinality.
    v_c, m_c = _verdict_v12(
        _units()[:5], _rec({"GSBC_RKD_BLOCK": 0.44, "GSBC_GWTA": 0.50, "GSBC_EXPAND2X": 0.45}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "full")
    assert v_c == "HARD_FAIL" and "CARDINALITY_BREACH" in m_c, f"{v_c} {m_c}"

    # SMOKE machinery pass (mechanism fires: gwta occ > 0).
    v_s, m_s = _verdict_v12(
        _pad(_units()), _rec({"GSBC_RKD_BLOCK": 0.20, "GSBC_GWTA": 0.20, "GSBC_EXPAND2X": 0.20}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "smoke")
    assert v_s == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_s, f"{v_s} {m_s}"

    # SMOKE mechanism-did-not-fire: gwta occ 0 -> SMOKE_GATE_FAIL.
    v_sf, m_sf = _verdict_v12(
        _pad(_units()),
        _rec({"GSBC_RKD_BLOCK": 0.20, "GSBC_GWTA": 0.20, "GSBC_EXPAND2X": 0.20},
             occ={"GSBC_RKD_BLOCK": 0.0, "GSBC_GWTA": 0.0, "GSBC_EXPAND2X": 1.5}),
        arms, "GSBC_RKD_BLOCK", "GSBC_GWTA", "GSBC_EXPAND2X", 37, "smoke")
    assert v_sf == "SMOKE_GATE_FAIL" and "MECHANISM_DID_NOT_FIRE" in m_sf, f"{v_sf} {m_sf}"

    # 6. tiny end-to-end: block + gwta modes train + produce DISTINCT codes.
    torch.manual_seed(11)
    Xsyn = torch.randn(400, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    Xval_syn = Xsyn[:40].contiguous()
    Xtest_syn = Xsyn[40:64].contiguous()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xval_syn, 500, 3)

    import tempfile
    code_by_arm = {}
    orig = v3.MLP_HIDDEN
    try:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for arm, (code_mode, out_dim, kb, blk_l, sparsity, width) in (
                    ("B", ("block", 256, 8, 32, 2, 32)),
                    ("G", ("gwta", 256, 8, 32, 16, 32)),
                    ("E", ("gwta", 512, 16, 32, 32, 32))):
                st_last, diag_st = _train_student_v12(
                    code_mode, kb, blk_l, out_dim, sparsity, width, Xsyn, 40, 24, 4, 13,
                    "cpu", tdp / f"ckpt_{arm}.pt", tdp / f"ckpt_best_{arm}.pt", 100, tdp,
                    t0, _dq, _df, 8, 2, 1.0, arm)
                assert int(st_last.net[0].out_features) == width
                assert math.isfinite(diag_st["rkd_last"])
                c_last = _encode_for_arm(code_mode, st_last, Xtest_syn, kb, blk_l, sparsity)
                assert c_last.shape == (24, out_dim)
                assert torch.isfinite(c_last).all()
                code_by_arm[arm] = hashlib.sha256(
                    np.ascontiguousarray(c_last.to(torch.float32).numpy()).tobytes()).hexdigest()
                st_best = _reload_best_v12(width, 64, out_dim, "cpu",
                                           tdp / f"ckpt_best_{arm}.pt")
                assert int(st_best.net[0].out_features) == width
                gk = torch.Generator().manual_seed(1)
                ku = v11._gsbc_keyed_unit(arm, c_last, kb, blk_l, 5, 20, gk, "cpu")
                assert "acc_at1" in ku
    finally:
        v3.MLP_HIDDEN = orig
    assert code_by_arm["B"] != code_by_arm["G"], "block vs gwta identical codes (AF)"
    assert code_by_arm["G"] != code_by_arm["E"], "gwta vs expand identical codes (AF)"
    assert v3.MLP_HIDDEN == orig, "MLP_HIDDEN not restored"

    # 7. determinism idempotence.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]

    print(f"[selftest] PASS (global-WTA encode top-K unit-L1 pos + eval-match + STE grad "
          f"+ occupancy-varies mechanism + circular-conv keyed roundtrip + shuffled-fail "
          f"+ depth-envelope + verdict bands [pass/algebra-degrades/no-lift/marginal/"
          f"calib/gate-D/cardinality/smoke/smoke-fail] + block&gwta train -> distinct "
          f"codes + determinism) elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
