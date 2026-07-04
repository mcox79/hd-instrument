"""Encoder v4 -- CONVERGENCE fix diagnostic: does a constant post-warmup
("plateau-hold") LR stop the in_batch-RKD-only DECLINE that v3e found at FULL
178k scale, versus the lineage's existing warmup+cosine-decay-to-zero schedule?

QUEUE-DEPTH cell authored while the R1 rescue sequence's other in-flight work
finishes elsewhere; designed to dispatch to overnight_queue the moment GPU is
free. Two SEPARATE problems the honest v3e result exposed are split into two
cells; THIS cell = problem 1 (convergence/plateau). Sibling cell = problem 2
(K=128 vs K=256 code-capacity paired test):
  experiments/exp_encoder_v5_k256_capacity_paired_v1_core.py

CONTEXT (do not re-litigate; read before amending). v3e (FULL, seed=7,
in_batch-RKD-only, nce_weight=0, steps=6000) landed HARD_FAIL
DECLINE_CONTINUES MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/
metrics.json:
  final_block=0.9187 final_dense=0.6571 final_ret_agree10=0.2112
  final_hi80_cos=0.8320 bestval_step=450 (7.5% into the 6000-step run)
  bestval_block_on_test=0.9015 bestval_ret_agree10=0.1920
  trend (on dense_full, the cheap DENSE-Spearman-over-mostly-random-pairs
  proxy used every 50 steps for cost reasons): early_half_mean=0.6898 ->
  late_half_mean=0.5671, early_minus_late=0.1228 (>= the 0.10 DECLINE
  threshold) -> HARD_FAIL fired on the DENSE proxy trend alone (the verdict's
  OR-condition on final_block<=0.45 was NOT what triggered it -- final_block
  0.9187 is nowhere near that ceiling).

VERIFIED@this session (direct read of the landed metrics.json above, prior to
authoring this cell): the actual HEADLINE metrics this arc is locked to
(hi80_cos, ret_agree10) do NOT show the same decline the DENSE-proxy trend
does in this one data point -- final ret_agree10 (0.2112) is even slightly
ABOVE bestval's (0.1920), and final_block (BLOCK-code Spearman-over-random,
0.9187) beats bestval's (0.9015) too. The DENSE proxy used for both the
trend-diagnostic AND the best-checkpoint SELECTION in the v3e/v3c lineage is
a different quantity than the BLOCK-code headline metrics that actually
matter for the 0.85 goal -- selecting/gating on the wrong metric risks
"fixing" or "declaring decline" on an artifact. THIS CELL's methodology fix
(mandated this session, composing with the locked headline-metric rule):
track PLATEAU/DECLINE and best-checkpoint SELECTION on the VAL-evaluated
BLOCK-code ret_agree10 trajectory directly (the actual headline retrieval
metric), not the cheap DENSE proxy. The DENSE proxy and BLOCK-code Spearman
are STILL logged per checkpoint (diagnostic transparency; also the concrete
empirical test of candidate lever (c) below) but no longer drive the
verdict.

TWO PAIRED ARMS, same seed/data/split/mining/objective/code (in_batch-RKD-
only, nce_weight=0, K=128, steps=6000, batch=128 -- MATCHES v3e exactly)
inside ONE process, differing ONLY in the LR schedule (a true paired
comparison per the USER-locked "paired trials mandatory for arm-comparison"
rule -- comparing against v3e's already-landed number instead would compare
across a possible torch-version/determinism gap, see below):
  COSINE   -- linear warmup then cosine-decay-to-0 over `steps` (REPRODUCES
             v3e's schedule; also the positive-control/reproduce-prior-
             result arm per canonical instruction file section 15 Gate D --
             tolerance-checked against the v3e MEASURED numbers above).
  PLATEAU  -- linear warmup then HOLD CONSTANT at peak LR for the remainder
             (candidate lever (a) from the USER's convergence-fix request).
Candidate lever (b) (early-stop-at-VAL-plateau) is answered by the existing
best-by-VAL-selection machinery applied to BOTH arms (now selecting by
ret_agree10, see above) -- no separate arm needed.
Candidate lever (c) (does block-STE gradient or the RKD objective itself
degrade geometry late) is answered EMPIRICALLY per arm by comparing the
DENSE-proxy trend against the BLOCK-code Spearman trend (both logged at the
same per-checkpoint cadence): if DENSE declines while BLOCK-code stays flat/
high (as v3e's single landed data point suggests), that is evidence the
DEPLOYED (block-quantized) representation is NOT degrading the way the
continuous readout is -- i.e. NOT primarily a block-STE artifact making
things look falsely fine, but rather the DENSE proxy itself may be measuring
something (bulk near-orthogonality drift) that the coarser block-quantized
code is insensitive to.

COORDINATOR COURSE-CORRECTION (2026-07-04, mid-authoring; VET caught 2
reproducibility gaps the same day -- BCT 0.989 (local-preview) vs 0.836
(remote-official), v3c 0.7336 (v3b) vs 0.6514 (v3c's own independent re-run
at the same nominal config) -- traced to torch-version drift + no
determinism pinning): this cell PINS determinism (see _pin_determinism:
torch.use_deterministic_algorithms(True, warn_only=True), explicit seeding
of torch/numpy/python RNGs, fixed thread count, CUBLAS_WORKSPACE_CONFIG for
CUDA determinism) and records torch.__version__ + device into metrics.json
so a future divergence is diagnosable instead of silently re-litigated. THE
REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL NUMBER; local smoke/preview
in this cell is a MACHINERY gate only (see discriminator-survives-scale
option (B) below) -- this is stated explicitly in the verdict_msg and the
"canonical_source" metrics field so no downstream reader confuses the two.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "constant learning rate plateau hold versus cosine decay convergence
  fix declining training trajectory retrieval headline metric" -> top hit
  cosine=0.2841 (this arc's own v3c/v3e prose, expected self-similarity), all
  other hits <=0.27. NONE at cosine>0.30 for a DISTINCT prior cell.
  GENUINELY NOVEL: no prior cell in this lineage runs a paired LR-schedule
  (cosine-decay vs constant-hold) comparison, nor gates plateau/decline on
  the ret_agree10 trajectory instead of the DENSE-Spearman-over-random proxy.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3e
  prereg, unchanged -- same K=128/N=4096 quantization channel; this cell
  changes only the LR schedule, not K)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification (same as
  the whole v3/v3b/v3c/v3e lineage): smoke's tiny V_train=3000 cannot
  reproduce the true near-neighbor coverage-ratio effect that drives the
  decline; smoke validates MACHINERY ONLY (both LR-mode arms train end-to-
  end, the headline-metric trend/best-selection wiring runs on a real
  multi-point trajectory, cardinality holds, determinism pinning does not
  crash CPU-only smoke). The actual plateau-vs-decline-under-plateau-hold-LR
  question needs the true 177899-concept corpus AND the full 6000-step
  budget -- that IS the FULL dispatch, and per the coordinator note above,
  the REMOTE-QUEUE OFFICIAL LANDING (not this local smoke) is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: the trend/floor bands apply to {COSINE,PLATEAU}_BLOCK_LAST val-
  trajectory only; {COSINE,PLATEAU}_*_BESTVAL are comparison/context;
  RANDOM_BLOCK/CHARPOS/shuffled_key are integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=17 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (same hyperparameters as the
  validated v3c/v3e lineage; only LR schedule, best-selection metric, and
  trend-diagnostic metric differ)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v4_convergence_lr_hold_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
Does NOT touch v3/v3b/v3c/v3e's own artifact/checkpoint/output directories.

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
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as v3c,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v4_convergence_lr_hold_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0        # RKD-only (matches v3c/v3e's winning ablation config)
OBJECTIVE = "in_batch"  # GLOBAL stays dropped (algebra HARD_FAIL, see v3c seeds)
LR_MODES = ("COSINE", "PLATEAU")

# ---- FULL-scale config: MATCHES v3e exactly except LR schedule ----
FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
HEADLINE_EVAL_EVERY_FULL = 500     # coarser than v3e's dense-only 50 (headline
                                   # eval is a real block-encode + semantic_unit
                                   # call, not just a cheap dense-sign pass)
FULL_TRIALS = v3.MID_TRIALS
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000
VAL_TRAJ_SUB = 2000                # val subset used for the per-checkpoint
                                   # headline-eval (block-encode cost bound)
VAL_TRAJ_PAIRS = 30_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE  # 400_000 -- reported-number sample

# ---- Smoke config: MACHINERY validation only (SAME code path as FULL) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN    # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD      # 800
SMOKE_STEPS = 240
SMOKE_CKPT_EVERY = 60
SMOKE_HEADLINE_EVAL_EVERY = 40      # 6 trend points (>= MIN_TREND_POINTS)
SMOKE_VAL_CAP = 200
SMOKE_VAL_TRAJ_SUB = 120
SMOKE_VAL_TRAJ_PAIRS = 3_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05      # anti-gaming floor (unchanged convention)
MIN_TREND_POINTS = 4

# semantic(2 arms x 4: DENSE/BLOCK x LAST/BESTVAL) + keyed(2 arms x 3: LAST J5,
# BESTVAL J5, shuffled-LAST J5) + shared integrity (RANDOM_BLOCK semantic +
# RANDOM_BLOCK keyed posctrl + CHARPOS semantic) = 8 + 6 + 3 = 17.
EXPECTED_N_UNITS_FULL = 17
EXPECTED_N_UNITS_SMOKE = 17

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

ALGEBRA_FLOOR = 0.90

# Trend/verdict bands on the VAL ret_agree10 trajectory (HYPOTHESIZED@this
# prereg -- first trajectory-level instrumentation of this metric; v3e only
# ever reported ret_agree10 at 2 discrete points -- final=0.2112, bestval@
# step450=0.1920 -- so absolute-scale bands are provisional and deliberately
# generous; the claim this cell tests is TREND SHAPE, not magnitude (Cell v5
# is the magnitude/capacity question)).
RET_PLATEAU_EARLY_MINUS_LATE_MAX = 0.02
RET_DECLINE_EARLY_MINUS_LATE_MIN = 0.05
RET_FINAL_FLOOR_FOR_PLATEAU = 0.05
HI80_COS_FLOOR_FOR_NONCOLLAPSE = 0.50   # v3e measured 0.832; generous collapse floor

# Gate-D positive-control tolerance for the COSINE arm reproducing v3e seed7
# (MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/metrics.json).
V3E_SEED7_FINAL_BLOCK = 0.9187171766106591
V3E_SEED7_FINAL_RET_AGREE10 = 0.21121188428458665
V3E_SEED7_FINAL_HI80_COS = 0.8319917321205139
REPRO_TOL_BLOCK = 0.15
REPRO_TOL_RET = 0.10
REPRO_TOL_HI80 = 0.15


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v4_convergence{tag}{suffix}"


# ---------------------------------------------------------------------------
# Determinism pinning (coordinator mandate, 2026-07-04).
# ---------------------------------------------------------------------------

def _pin_determinism(seed: int) -> Dict:
    """Best-effort determinism pinning; records what actually took effect so a
    future divergence is diagnosable instead of silently re-litigated."""
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
        except Exception as exc:  # pragma: no cover -- environment-dependent
            det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # pragma: no cover -- environment-dependent
        det_ok, det_err = False, f"{type(exc).__name__}: {exc}"
    n_threads = min(8, os.cpu_count() or 4)
    try:
        torch.set_num_threads(n_threads)
    except RuntimeError:
        pass
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass  # interop pool already started elsewhere in-process; not fatal
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
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3e.
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
# LR schedule (the new mechanism this cell adds).
# ---------------------------------------------------------------------------

def _lr_at_mode(step: int, total: int, warmup: int, base_lr: float, mode: str) -> float:
    """Linear warmup then either cosine-decay-to-~0 ("cosine", = v3/v3c/v3e's
    unchanged schedule) or HOLD CONSTANT at base_lr ("plateau")."""
    if warmup > 0 and step < warmup:
        return base_lr * float(step + 1) / float(warmup)
    if mode == "plateau":
        return base_lr
    if mode == "cosine":
        denom = max(1, total - warmup)
        prog = float(step - warmup) / float(denom)
        prog = min(1.0, max(0.0, prog))
        return 0.5 * base_lr * (1.0 + math.cos(math.pi * prog))
    raise ValueError(f"unknown lr_mode {mode}")


# ---------------------------------------------------------------------------
# Trend diagnostic (generic on trajectory key; reused for ret_agree10, hi80_cos,
# dense_full, val_block_spearman -- same shape as v3e's, kept self-contained
# here per the "parent cells read-only, not imported for internals" convention).
# ---------------------------------------------------------------------------

def _trend_diagnostic(traj: List[Dict], key: str, min_step: int) -> Dict:
    pts = [(r["step"], r[key]) for r in traj
           if math.isfinite(r.get(key, float("nan"))) and r["step"] >= min_step]
    if len(pts) < MIN_TREND_POINTS:
        return {"sufficient": False, "n_points": len(pts)}
    steps_arr = np.array([p[0] for p in pts], dtype=np.float64)
    vals_arr = np.array([p[1] for p in pts], dtype=np.float64)
    slope, intercept = np.polyfit(steps_arr, vals_arr, 1)
    mid_step = steps_arr.min() + (steps_arr.max() - steps_arr.min()) / 2.0
    early = vals_arr[steps_arr < mid_step]
    late = vals_arr[steps_arr >= mid_step]
    early_mean = float(early.mean()) if early.size else float("nan")
    late_mean = float(late.mean()) if late.size else float("nan")
    return {
        "sufficient": True, "n_points": len(pts),
        "slope_per_step": float(slope), "intercept": float(intercept),
        "early_half_mean": early_mean, "late_half_mean": late_mean,
        "early_minus_late": (early_mean - late_mean
                             if math.isfinite(early_mean) and math.isfinite(late_mean)
                             else float("nan")),
        "first_point": {"step": int(steps_arr[0]), "val": float(vals_arr[0])},
        "last_point": {"step": int(steps_arr[-1]), "val": float(vals_arr[-1])},
    }


# ---------------------------------------------------------------------------
# Training loop (adapted from v3c._train_student_full: parameterized LR mode,
# best-checkpoint SELECTION now driven by VAL ret_agree10 not the DENSE proxy,
# headline-eval trajectory logged alongside the cheap DENSE proxy).
# ---------------------------------------------------------------------------

def _train_student_lrmode(
    kb: int, blk_l: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int,
    output_dir: Path, t0: float,
    nce_weight: float, arm_label: str, lr_mode: str,
    headline_eval_fn: Optional[Callable] = None,
    dense_eval_quick_fn: Optional[Callable] = None,
    eval_every: int = 0,
    min_step_for_best: int = 0,
) -> Tuple[torch.nn.Module, Dict]:
    out_dim = kb * blk_l
    student = v3._make_student("mlp", Xtr.shape[1], out_dim, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    traj: List[Dict] = []
    best_state = {"score": -2.0, "step": -1}
    alltime_state = {"score": -2.0, "step": -1}
    if ckpt_path.exists():
        try:
            ck = torch.load(str(ckpt_path), map_location=device)
            student.load_state_dict(ck["student"])
            opt.load_state_dict(ck["opt"])
            gen.set_state(ck["gen_state"])
            start_step = int(ck["step"])
            traj = list(ck.get("traj", []))
            best_state["score"] = float(ck.get("best_score", -2.0))
            best_state["step"] = int(ck.get("best_step", -1))
            alltime_state["score"] = float(ck.get("alltime_score", -2.0))
            alltime_state["step"] = int(ck.get("alltime_step", -1))
            print(f"[v4_lrmode] resume {arm_label} at step {start_step}", flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v4_lrmode] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining {arm_label} from scratch", flush=True)
            start_step = 0
            traj = []
            best_state = {"score": -2.0, "step": -1}
            alltime_state = {"score": -2.0, "step": -1}
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    loss_first = loss_last = None
    rkd_last = nce_last = lr_last = None

    def _maybe_save_best(step_i: int, score: float) -> None:
        if not math.isfinite(score):
            return
        if score > alltime_state["score"]:
            alltime_state["score"] = score
            alltime_state["step"] = step_i
        if step_i < min_step_for_best:
            return
        if score > best_state["score"]:
            best_state["score"] = score
            best_state["step"] = step_i
            tmp_b = best_ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "step": step_i,
                       "ret_agree10": score, "arm": arm_label}, str(tmp_b))
            os.replace(str(tmp_b), str(best_ckpt_path))

    for step in range(start_step, steps):
        cur_lr = _lr_at_mode(step, steps, warmup, v3.LR, lr_mode)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = v3._cluster_batch_idx(batch, 0.0, V, pos_idx, semi_cands, gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        s = v3._block_ste(z, kb, blk_l)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        T = x @ x.T
        off = ~torch.eye(batch, dtype=torch.bool, device=device)
        l_rkd = (((s_n @ s_n.T) - T)[off] ** 2).mean()
        p_ = pos_idx[bidx]
        cols = torch.randint(0, v3.N_SEMI_CANDS, (batch, v3.N_NEG_PER_ANCHOR),
                             generator=gen)
        negs = torch.gather(semi_cands[bidx], 1, cols)
        fallback = torch.randint(0, V, (batch, v3.N_NEG_PER_ANCHOR), generator=gen)
        negs = torch.where(negs < 0, fallback, negs)
        cand_idx = torch.cat([p_.unsqueeze(1), negs], dim=1)
        zc = student(Xd[cand_idx.reshape(-1).to(device)])
        sc = v3._block_ste(zc, kb, blk_l)
        sc = sc.reshape(batch, 1 + v3.N_NEG_PER_ANCHOR, -1)
        sc_n = sc / (sc.norm(dim=-1, keepdim=True) + 1e-8)
        lg_h = torch.einsum("bd,bcd->bc", s_n, sc_n) / v3.TAU_NCE
        lg_i = (s_n @ s_n.T / v3.TAU_NCE).masked_fill(
            torch.eye(batch, dtype=torch.bool, device=device), -1e4)
        l_nce = torch.nn.functional.cross_entropy(
            torch.cat([lg_h, lg_i], dim=1),
            torch.zeros(batch, dtype=torch.long, device=device))
        loss = l_rkd + nce_weight * l_nce
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_nce={float(l_nce.detach())})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        v_nce = float(l_nce.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last, rkd_last, nce_last, lr_last = v_loss, v_rkd, v_nce, cur_lr
        if step % 200 == 0:
            print(f"[v4_lrmode] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"nce={v_nce:.4f} lr={cur_lr:.2e} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "loss": v_loss,
                                   "rkd": v_rkd})
        if (headline_eval_fn is not None and eval_every > 0 and step % eval_every == 0):
            hl = headline_eval_fn(student)
            d_quick = (float(dense_eval_quick_fn(student))
                      if dense_eval_quick_fn is not None else float("nan"))
            row = {"step": step, "val_ret_agree10": float(hl["ret_agree10"]),
                  "val_hi80_cos": float(hl["hi80_cos"]),
                  "val_block_spearman": float(hl["spearman_all"]),
                  "dense_full": d_quick, "rkd": v_rkd, "final": False}
            traj.append(row)
            print(f"[v4_lrmode] {arm_label} VAL-traj step {step}: "
                  f"ret_agree10={row['val_ret_agree10']:.4f} "
                  f"hi80_cos={row['val_hi80_cos']:.4f} "
                  f"block_spearman={row['val_block_spearman']:.4f} "
                  f"dense_full={row['dense_full']:.4f}", flush=True)
            _maybe_save_best(step, row["val_ret_agree10"])
        if (step + 1) % ckpt_every == 0 or (step + 1) == steps:
            tmp = ckpt_path.with_suffix(".tmp")
            torch.save({"student": student.state_dict(), "opt": opt.state_dict(),
                       "gen_state": gen.get_state(), "step": step + 1,
                       "traj": traj, "best_score": best_state["score"],
                       "best_step": best_state["step"],
                       "alltime_score": alltime_state["score"],
                       "alltime_step": alltime_state["step"]}, str(tmp))
            os.replace(str(tmp), str(ckpt_path))
    if headline_eval_fn is not None:
        hl_fin = headline_eval_fn(student)
        d_quick_fin = (float(dense_eval_quick_fn(student))
                      if dense_eval_quick_fn is not None else float("nan"))
        traj.append({"step": steps, "val_ret_agree10": float(hl_fin["ret_agree10"]),
                    "val_hi80_cos": float(hl_fin["hi80_cos"]),
                    "val_block_spearman": float(hl_fin["spearman_all"]),
                    "dense_full": d_quick_fin,
                    "rkd": rkd_last if rkd_last is not None else float("nan"),
                    "final": True})
        _maybe_save_best(steps, float(hl_fin["ret_agree10"]))
        print(f"[v4_lrmode] {arm_label} FINAL step {steps}: "
              f"ret_agree10={hl_fin['ret_agree10']:.4f} "
              f"hi80_cos={hl_fin['hi80_cos']:.4f} "
              f"block_spearman={hl_fin['spearman_all']:.4f}", flush=True)
    best_ckpt_fallback_to_final = best_state["step"] < 0
    if best_ckpt_fallback_to_final:
        tmp_b = best_ckpt_path.with_suffix(".tmp")
        torch.save({"student": student.state_dict(), "step": steps,
                   "ret_agree10": float("nan"), "arm": arm_label}, str(tmp_b))
        os.replace(str(tmp_b), str(best_ckpt_path))
        print(f"[v4_lrmode] WARN {arm_label}: no eval point >= min_step_for_best; "
              f"best-ckpt falls back to FINAL student", flush=True)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "nce_last": nce_last if nce_last is not None else -1.0,
        "lr_last": lr_last if lr_last is not None else -1.0,
        "lr_mode": lr_mode, "arm": arm_label, "batch": batch,
        "traj": traj,
        "best_ret_agree10": best_state["score"], "best_step": best_state["step"],
        "best_ckpt_fallback_to_final": best_ckpt_fallback_to_final,
        "alltime_best_ret_agree10": alltime_state["score"],
        "alltime_best_step": alltime_state["step"],
    }


def _reload_best_student(in_dim: int, out_dim: int, device: str,
                         best_ckpt_path: Path) -> torch.nn.Module:
    ck = torch.load(str(best_ckpt_path), map_location=device)
    student = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    student.load_state_dict(ck["student"])
    student.eval()
    return student


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _trend_call(traj: List[Dict], key: str, min_step: int,
                plateau_max: float, decline_min: float) -> Tuple[str, Dict]:
    trend = _trend_diagnostic(traj, key, min_step)
    if not trend.get("sufficient", False):
        return "INSUFFICIENT", trend
    eml = trend["early_minus_late"]
    if eml <= plateau_max:
        return "PLATEAU", trend
    if eml >= decline_min:
        return "DECLINE", trend
    return "AMBIGUOUS", trend


def _verdict_convergence(per_unit: List[Dict], arm_diag: Dict[str, Dict],
                         expected_units: int, run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    if posc is None or posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed "
                f"J=5 {posc['acc_at1'] if posc else None} < 0.98 (SBC lossless prior)")
    for mode in LR_MODES:
        prim = v3._by_unit(per_unit, "keyed", f"{mode}_BLOCK_LAST", 5)
        shuf = v3._by_unit(per_unit, "shuffled_key", f"{mode}_BLOCK_LAST", 5)
        if prim is None or shuf is None:
            return ("HARD_FAIL", f"HARD_FAIL_MISSING_GATE_UNITS: {mode}")
        if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SHUFFLED_KEY_LEAK: {mode} "
                    f"{shuf['acc_at1']:.3f}/{shuf['hit_any_member']:.3f}")
        if prim["acc_at1"] < ALGEBRA_FLOOR:
            return ("HARD_FAIL",
                    f"FALSE_WIN_ALGEBRA_LAST_STEP: {mode} keyed_roundtrip J=5 "
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR}")

    min_step_for_best = arm_diag["COSINE"].get("_min_step_for_best", 0)
    calls = {}
    for mode in LR_MODES:
        call, trend = _trend_call(arm_diag[mode]["traj"], "val_ret_agree10",
                                  min_step_for_best,
                                  RET_PLATEAU_EARLY_MINUS_LATE_MAX,
                                  RET_DECLINE_EARLY_MINUS_LATE_MIN)
        calls[mode] = {"call": call, "trend": trend}

    def _final(mode: str, key: str) -> float:
        pts = [r for r in arm_diag[mode]["traj"] if r.get("final")]
        return float(pts[-1][key]) if pts else float("nan")

    cos_final_ret = _final("COSINE", "val_ret_agree10")
    cos_final_hi80 = _final("COSINE", "val_hi80_cos")
    plat_final_ret = _final("PLATEAU", "val_ret_agree10")
    plat_final_hi80 = _final("PLATEAU", "val_hi80_cos")

    repro_block_ok = abs(_final("COSINE", "val_block_spearman")
                         - V3E_SEED7_FINAL_BLOCK) <= REPRO_TOL_BLOCK
    repro_ret_ok = abs(cos_final_ret - V3E_SEED7_FINAL_RET_AGREE10) <= REPRO_TOL_RET
    repro_hi80_ok = abs(cos_final_hi80 - V3E_SEED7_FINAL_HI80_COS) <= REPRO_TOL_HI80
    repro_ok = repro_block_ok and repro_ret_ok and repro_hi80_ok

    tail = (f"[COSINE: call={calls['COSINE']['call']} "
           f"eml={calls['COSINE']['trend'].get('early_minus_late')} "
           f"final_ret={cos_final_ret:.4f} final_hi80={cos_final_hi80:.4f} "
           f"repro_vs_v3e_seed7={repro_ok}] "
           f"[PLATEAU: call={calls['PLATEAU']['call']} "
           f"eml={calls['PLATEAU']['trend'].get('early_minus_late')} "
           f"final_ret={plat_final_ret:.4f} final_hi80={plat_final_hi80:.4f}]")

    if run_mode == "smoke":
        fails = []
        for mode in LR_MODES:
            if calls[mode]["call"] == "INSUFFICIENT":
                fails.append(f"S_trend_insufficient_{mode}")
            if not math.isfinite(_final(mode, "val_ret_agree10")):
                fails.append(f"S_ret_agree10_missing_{mode}")
            if not math.isfinite(_final(mode, "val_hi80_cos")):
                fails.append(f"S_hi80_cos_missing_{mode}")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both LR-mode arms train end-to-end, "
                f"headline VAL trend/best-selection wiring runs on a real "
                f"multi-point trajectory, cardinality/integrity/algebra "
                f"gates hold {tail} (the plateau-vs-decline discriminator is "
                f"a FULL-only question; smoke's tiny V_train cannot "
                f"reproduce it -- REMOTE-QUEUE OFFICIAL LANDING is canonical, "
                f"this local smoke is a machinery gate only)")

    for mode in LR_MODES:
        if calls[mode]["call"] == "INSUFFICIENT":
            return ("HARD_FAIL", f"HARD_FAIL_TREND_INSUFFICIENT_POINTS_{mode} {tail}")

    if not repro_ok:
        return ("MIDDLE_BAND",
                f"COSINE_REPRODUCTION_OUTSIDE_TOLERANCE: this run's COSINE arm "
                f"(same seed/config as v3e seed7, now with determinism pinning) "
                f"diverged from the v3e MEASURED reference by more than the "
                f"declared tolerance (block<=+-{REPRO_TOL_BLOCK}, "
                f"ret<=+-{REPRO_TOL_RET}, hi80<=+-{REPRO_TOL_HI80}) -- "
                f"environment/torch-version drift is suspected; the PLATEAU-"
                f"vs-COSINE comparison below is still reported but should be "
                f"re-audited against a fresh COSINE-only rerun before trusting "
                f"a fix-confirmed claim {tail}")

    cos_call, plat_call = calls["COSINE"]["call"], calls["PLATEAU"]["call"]
    if cos_call == "DECLINE" and plat_call == "PLATEAU" and plat_final_ret >= cos_final_ret \
            and plat_final_hi80 >= HI80_COS_FLOOR_FOR_NONCOLLAPSE:
        return ("HARD_PASS",
                f"CONVERGENCE_FIX_CONFIRMED: COSINE reproduces the known "
                f"decline while PLATEAU (constant post-warmup LR) genuinely "
                f"plateaus on the VAL ret_agree10 trajectory AND does not lose "
                f"ground on the final headline numbers -- lever (a) "
                f"(plateau-hold LR) is validated as a convergence fix for the "
                f"in_batch-RKD-only objective {tail}")
    if cos_call == "DECLINE" and plat_call == "DECLINE":
        return ("HARD_FAIL",
                f"LR_SCHEDULE_DOES_NOT_FIX_DECLINE: both arms show the same "
                f"decline signature on VAL ret_agree10 -- the LR schedule is "
                f"NOT the root cause; lever (a) is falsified for this "
                f"objective, pursue an objective-family change (R2/R3/R4 in "
                f"notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md) "
                f"instead {tail}")
    if cos_call != "DECLINE":
        return ("MIDDLE_BAND",
                f"COSINE_DID_NOT_REPRODUCE_DECLINE_SHAPE: the reproduction arm "
                f"did not show the DECLINE call this cell expected from v3e "
                f"(call={cos_call}) even though its final numbers were within "
                f"tolerance -- the trend-band mismatch between the OLD "
                f"(dense_full) and NEW (val_ret_agree10) trend metrics may "
                f"itself be the finding (see docstring VERIFIED note); "
                f"investigate before drawing a lever-(a) conclusion {tail}")
    return ("MIDDLE_BAND",
            f"AMBIGUOUS_CONVERGENCE_OUTCOME: COSINE declines as expected but "
            f"PLATEAU's outcome ({plat_call}, final_ret={plat_final_ret:.4f} "
            f"vs COSINE's {cos_final_ret:.4f}) does not cleanly confirm or "
            f"refute lever (a) -- consider a longer run or additional seeds "
            f"{tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_convergence(run_mode: str, seed: int, device_arg: str, n_dim: int,
                    teacher_cache_arg: Optional[str], run_tag: str = "") -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    det_info = _pin_determinism(seed)
    tag_suffix = f"_{run_tag}" if run_tag else ""
    anchor = f"{ANCHOR_NAME}{tag_suffix}_smoke" if run_mode == "smoke" \
        else f"{ANCHOR_NAME}{tag_suffix}"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, run_tag)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    if kb * blk_l != n_dim:
        raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")

    if run_mode == "smoke":
        steps = SMOKE_STEPS
        ckpt_every, eval_every = SMOKE_CKPT_EVERY, SMOKE_HEADLINE_EVAL_EVERY
        val_cap, val_traj_sub, val_traj_pairs = SMOKE_VAL_CAP, SMOKE_VAL_TRAJ_SUB, SMOKE_VAL_TRAJ_PAIRS
        test_final_pairs = SMOKE_TEST_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        batch = min(FULL_BATCH, 32)
    else:
        steps = FULL_STEPS
        ckpt_every, eval_every = CKPT_EVERY_STEPS_FULL, HEADLINE_EVAL_EVERY_FULL
        val_cap, val_traj_sub, val_traj_pairs = VAL_CAP, VAL_TRAJ_SUB, VAL_TRAJ_PAIRS
        test_final_pairs = TEST_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        n_tr_target = n_he_target = None
        batch = FULL_BATCH
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    warmup = v3._warmup_for(steps)
    # Also exclude the shared warmup ramp from best-checkpoint eligibility: the
    # COSINE and PLATEAU LR schedules are MATHEMATICALLY IDENTICAL during
    # warmup (both do the same linear ramp), so with identical seed/batches a
    # checkpoint saved inside warmup is bit-identical across arms by
    # construction -- not a genuine cross-arm comparison, and not yet at the
    # target LR either (same rationale as excluding the untrained-network
    # spike). Caught at smoke scale (2026-07-04): both arms' best_step landed
    # at step=40 (< warmup=48), tripping a legitimate-but-confusing
    # META_RULE_AF cross-arm identical-digest case.
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)), warmup)

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v4_convergence] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} steps={steps} batch={batch} torch={det_info['torch_version']} "
          f"deterministic_ok={det_info['deterministic_algorithms_set']} "
          f"min_step_for_best={min_step_for_best}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v4_convergence] teacher {cache_path.name}: {V_cache} concepts x "
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
    held_idx = perm[n_tr:n_tr + n_he]
    n_val = min(val_cap, n_he - 1)
    val_idx = held_idx[:n_val]
    test_idx = held_idx[n_val:]
    n_test = test_idx.shape[0]
    if n_test < 10:
        raise RuntimeError(f"TEST split too small: n_test={n_test} (n_he={n_he}, n_val={n_val})")
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xval = X[torch.from_numpy(val_idx.copy())].contiguous()
    Xtest = X[torch.from_numpy(test_idx.copy())].contiguous()
    names_test = [ids[i] for i in test_idx]
    print(f"[v4_convergence] split train={n_tr} val={n_val} test={n_test}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v4_convergence] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xval_traj = Xval[:min(val_traj_sub, n_val)].contiguous()

    def _dense_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval_traj, val_traj_pairs, seed + 7)

    def _headline_eval(student: torch.nn.Module) -> Dict:
        codes = v3._encode_hard_block(student, Xval_traj, kb, blk_l)
        return v3._semantic_unit("VAL_TRAJ", codes, codes, Xval_traj, Xval_traj,
                                 0, val_traj_pairs, seed + 9)

    arm_diag: Dict[str, Dict] = {}
    for mode in LR_MODES:
        ckpt_path = art_dir / f"_ckpt_{mode}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{mode}.pt"
        lr_mode = mode.lower()  # "COSINE" -> "cosine", "PLATEAU" -> "plateau"
        _, diag = _train_student_lrmode(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            NCE_WEIGHT, mode, lr_mode,
            headline_eval_fn=_headline_eval, dense_eval_quick_fn=_dense_quick,
            eval_every=eval_every, min_step_for_best=min_step_for_best)
        diag["_min_step_for_best"] = min_step_for_best
        arm_diag[mode] = diag
        print(f"[v4_convergence] {mode} trained rkd_last={diag['rkd_last']:.4f} "
              f"best_ret_agree10={diag['best_ret_agree10']:.4f}@step{diag['best_step']} "
              f"n_traj_points={len(diag['traj'])} ({time.perf_counter() - t0:.1f}s)",
              flush=True)

    in_dim = Xtr.shape[1]
    arm_codes: Dict[str, torch.Tensor] = {}
    for mode in LR_MODES:
        ckpt_path = art_dir / f"_ckpt_{mode}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{mode}.pt"
        last_ck = torch.load(str(ckpt_path), map_location=device)
        last_student = v3._make_student("mlp", in_dim, kb * blk_l, device, seed)
        last_student.load_state_dict(last_ck["student"])
        last_student.eval()
        bestval_student = _reload_best_student(in_dim, kb * blk_l, device, best_ckpt_path)
        arm_codes[f"{mode}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xtest)
        arm_codes[f"{mode}_BLOCK_LAST"] = v3._encode_hard_block(last_student, Xtest, kb, blk_l)
        arm_codes[f"{mode}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xtest)
        arm_codes[f"{mode}_BLOCK_BESTVAL"] = v3._encode_hard_block(bestval_student, Xtest, kb, blk_l)

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], n_dim, kb)

    # META_RULE_AF exemption (legitimate, NOT a bug): the best-by-VAL-ret_agree10
    # checkpoint can coincide with the FINAL checkpoint when a run does not
    # decline (best_step == steps, or the no-eligible-point fallback fired) --
    # in that case LAST and BESTVAL are, correctly, the identical trained
    # weights. Only the LAST-vs-BESTVAL pair for the SAME lr_mode is exempted;
    # cross-mode and cross-representation (DENSE vs BLOCK) identity is still a
    # hard failure.
    exempted_pairs = set()
    for mode in LR_MODES:
        bestval_equals_last = (arm_diag[mode]["best_step"] == steps
                               or arm_diag[mode]["best_ckpt_fallback_to_final"])
        if bestval_equals_last:
            exempted_pairs.add(frozenset((f"{mode}_DENSE_LAST", f"{mode}_DENSE_BESTVAL")))
            exempted_pairs.add(frozenset((f"{mode}_BLOCK_LAST", f"{mode}_BLOCK_BESTVAL")))

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                if frozenset((a, b)) in exempted_pairs:
                    continue
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v4_convergence] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for mode in LR_MODES:
        for label in (f"{mode}_DENSE_LAST", f"{mode}_BLOCK_LAST",
                      f"{mode}_DENSE_BESTVAL", f"{mode}_BLOCK_BESTVAL"):
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xtest, Xtest, 0,
                      test_final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", arm_codes["RANDOM_BLOCK"],
              arm_codes["RANDOM_BLOCK"], Xtest, Xtest, 0, test_final_pairs, seed + 3)
    cp_Xtest = Xtest[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xtest, cp_Xtest, 0,
              test_final_pairs, seed + 3)

    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", arm_codes["RANDOM_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    for mode in LR_MODES:
        _run_unit(v3._keyed_unit, f"{mode}_BLOCK_LAST", "sbc",
                  arm_codes[f"{mode}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{mode}_BLOCK_BESTVAL", "sbc",
                  arm_codes[f"{mode}_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials,
                  gen_eval, device)
        _run_unit(v3._keyed_unit, f"{mode}_BLOCK_LAST", "sbc",
                  arm_codes[f"{mode}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval,
                  device, shuffled_key=True)

    verdict, verdict_msg = _verdict_convergence(per_unit, arm_diag, expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    def _sem_summary(mode: str, kind: str) -> Dict:
        u = v3._by_unit(per_unit, "semantic", f"{mode}_{kind}")
        if u is None:
            return {}
        return {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
               "hi80_cos": u["hi80_cos"], "hi80_calib_err": u["hi80_calib_err"]}

    recovery = {mode: {
        "final": _sem_summary(mode, "BLOCK_LAST"),
        "bestval_on_test": _sem_summary(mode, "BLOCK_BESTVAL"),
        "best_step": arm_diag[mode]["best_step"],
        "best_step_frac": (arm_diag[mode]["best_step"] / steps
                           if steps > 0 and arm_diag[mode]["best_step"] >= 0 else None),
        "best_ckpt_fallback_to_final": arm_diag[mode]["best_ckpt_fallback_to_final"],
        "trend_val_ret_agree10": _trend_diagnostic(
            arm_diag[mode]["traj"], "val_ret_agree10", min_step_for_best),
        "trend_dense_full": _trend_diagnostic(
            arm_diag[mode]["traj"], "dense_full", min_step_for_best),
        "trend_val_block_spearman": _trend_diagnostic(
            arm_diag[mode]["traj"], "val_block_spearman", min_step_for_best),
        "n_traj_points": len(arm_diag[mode]["traj"]),
        "traj": arm_diag[mode]["traj"],
    } for mode in LR_MODES}

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE,
        "min_step_for_best": min_step_for_best, "headline_eval_every": eval_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_val": n_val,
        "n_test": n_test, "n_held_pool": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "determinism": det_info,
        "canonical_source": "remote_queue_official_landing_only; local_smoke_is_gate_only",
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "arms_differ_exempted": [tuple(sorted(p)) for p in exempted_pairs],
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("PAIRED same-seed/data/split/mining comparison of LR "
                        "schedule (cosine-decay-to-0 vs plateau-hold) at the "
                        "in_batch-RKD-only nce=0 config matching v3e; plateau/"
                        "decline verdict + best-checkpoint selection driven by "
                        "the VAL ret_agree10 trajectory (headline metric), NOT "
                        "the old cheap DENSE-Spearman-over-random proxy; FINAL-"
                        "step is the PRIMARY gated number, best-by-VAL-on-TEST "
                        "is SECONDARY context; DENSE-proxy and BLOCK-code "
                        "Spearman trends both logged per checkpoint as the "
                        "empirical test of whether block-STE or the underlying "
                        "objective degrades geometry late"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b/"
                                   "v3c/v3e; this cell changes only LR schedule)"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v4_convergence] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. LR schedule: plateau holds flat post-warmup; cosine decays to ~0.
    warmup, total, base = 10, 100, 1e-3
    lr_plateau_mid = _lr_at_mode(50, total, warmup, base, "plateau")
    lr_plateau_end = _lr_at_mode(99, total, warmup, base, "plateau")
    assert abs(lr_plateau_mid - base) < 1e-12, "selftest: plateau must hold at base_lr"
    assert abs(lr_plateau_end - base) < 1e-12, "selftest: plateau must hold to the end"
    lr_cos_mid = _lr_at_mode(50, total, warmup, base, "cosine")
    lr_cos_end = _lr_at_mode(99, total, warmup, base, "cosine")
    assert lr_cos_mid < base * 0.6, "selftest: cosine must have decayed by midpoint"
    assert lr_cos_end < base * 0.05, "selftest: cosine must be near-zero at the end"
    assert lr_cos_end < lr_plateau_end, "selftest: cosine must end lower than plateau"
    try:
        _lr_at_mode(50, total, warmup, base, "bogus")
        raise AssertionError("selftest: unknown lr_mode must raise")
    except ValueError:
        pass

    # 2. trend diagnostic (reused shape from v3e lineage; generic on key).
    traj = ([{"step": 0, "val_ret_agree10": 0.30}] +
            [{"step": s, "val_ret_agree10": 0.25 - 0.01 * (s // 20)}
             for s in range(20, 201, 20)])
    trend = _trend_diagnostic(traj, "val_ret_agree10", min_step=10)
    assert trend["sufficient"] is True
    assert trend["early_minus_late"] > 0.03, "selftest: declining traj must show early>late"
    flat_traj = ([{"step": 0, "val_ret_agree10": 0.30}] +
                [{"step": s, "val_ret_agree10": 0.20 + 0.001 * ((s % 3) - 1)}
                 for s in range(20, 201, 20)])
    trend_flat = _trend_diagnostic(flat_traj, "val_ret_agree10", min_step=10)
    assert abs(trend_flat["early_minus_late"]) < 0.02, "selftest: flat traj must read as plateau"

    # 3. verdict bands: synthetic arm_diag for HARD_PASS / HARD_FAIL / MIDDLE_BAND.
    def _fake_units():
        units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(10)]
        units += [
            {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
             "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        ]
        for mode in LR_MODES:
            units += [
                {"unit": f"keyed::{mode}_BLOCK_LAST::J5", "arm": f"{mode}_BLOCK_LAST",
                 "kind": "keyed", "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
                {"unit": f"keyed::{mode}_BLOCK_BESTVAL::J5", "arm": f"{mode}_BLOCK_BESTVAL",
                 "kind": "keyed", "J": 5, "acc_at1": 0.95, "hit_any_member": 0.95},
                {"unit": f"shuffled_key::{mode}_BLOCK_LAST::J5", "arm": f"{mode}_BLOCK_LAST",
                 "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
            ]
        return units

    def _traj_for(final_ret, eml, n=100, final_hi80=0.80, final_block=0.90):
        pts = [{"step": s, "val_ret_agree10": final_ret + eml * (1 - s / (n * 20)),
               "val_hi80_cos": final_hi80, "val_block_spearman": final_block,
               "dense_full": 0.6, "final": False}
              for s in range(0, n * 20, 20)]
        pts.append({"step": n * 20, "val_ret_agree10": final_ret,
                   "val_hi80_cos": final_hi80, "val_block_spearman": final_block,
                   "dense_full": 0.6, "final": True})
        return pts

    fake_units = _fake_units()
    arm_diag_pass = {
        "COSINE": {"traj": _traj_for(V3E_SEED7_FINAL_RET_AGREE10, 0.15,
                                     final_hi80=V3E_SEED7_FINAL_HI80_COS,
                                     final_block=V3E_SEED7_FINAL_BLOCK),
                  "_min_step_for_best": 10},
        "PLATEAU": {"traj": _traj_for(V3E_SEED7_FINAL_RET_AGREE10 + 0.02, 0.005,
                                      final_hi80=0.80, final_block=0.90),
                   "_min_step_for_best": 10},
    }
    v_pass, m_pass = _verdict_convergence(fake_units, arm_diag_pass, 17, "full")
    assert v_pass == "HARD_PASS" and "CONVERGENCE_FIX_CONFIRMED" in m_pass, (
        f"selftest: expected fix-confirmed HARD_PASS got {v_pass} ({m_pass})")

    arm_diag_fail = {
        "COSINE": {"traj": _traj_for(V3E_SEED7_FINAL_RET_AGREE10, 0.15,
                                     final_hi80=V3E_SEED7_FINAL_HI80_COS,
                                     final_block=V3E_SEED7_FINAL_BLOCK),
                  "_min_step_for_best": 10},
        "PLATEAU": {"traj": _traj_for(0.05, 0.15, final_hi80=0.60, final_block=0.90),
                   "_min_step_for_best": 10},
    }
    v_fail, m_fail = _verdict_convergence(fake_units, arm_diag_fail, 17, "full")
    assert v_fail == "HARD_FAIL" and "LR_SCHEDULE_DOES_NOT_FIX_DECLINE" in m_fail, (
        f"selftest: expected schedule-does-not-fix HARD_FAIL got {v_fail} ({m_fail})")

    v_card, m_card = _verdict_convergence(fake_units[:5], arm_diag_pass, 17, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    # 4. tiny end-to-end training reuse (proves _train_student_lrmode wiring:
    #    both lr_mode branches, headline-eval closure, best-selection-by-
    #    ret_agree10, checkpoint save/reload all execute without error).
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    Xval_syn = Xsyn[:40].contiguous()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _hl(student):
        codes = v3._encode_hard_block(student, Xval_syn, kb, blk_l)
        return v3._semantic_unit("SYN_VAL", codes, codes, Xval_syn, Xval_syn, 0, 500, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for mode in ("cosine", "plateau"):
            _, diag_st = _train_student_lrmode(
                kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
                tdp / f"ckpt_{mode}.pt", tdp / f"ckpt_best_{mode}.pt", 100, tdp, t0,
                0.0, f"TEST_{mode.upper()}", mode,
                headline_eval_fn=_hl, dense_eval_quick_fn=_dq, eval_every=4,
                min_step_for_best=2)
            assert math.isfinite(diag_st["rkd_last"])
            assert len(diag_st["traj"]) >= MIN_TREND_POINTS
            assert diag_st["lr_mode"] == mode
            trend_real = _trend_diagnostic(diag_st["traj"], "val_ret_agree10", min_step=2)
            assert trend_real["sufficient"] is True
            best_student = _reload_best_student(64, kb * blk_l, "cpu",
                                                tdp / f"ckpt_best_{mode}.pt")
            c = v3._encode_hard_block(best_student, Xval_syn, kb, blk_l)
            assert c.shape == (40, kb * blk_l)
            assert torch.isfinite(c).all()

    # 5. determinism pinning is idempotent and does not raise on repeated calls.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]
    assert isinstance(d1["deterministic_algorithms_set"], bool)

    print(f"[selftest] PASS (LR-mode schedule incl unknown-mode-raises + "
          f"trend-diagnostic reuse + fix-confirmed/schedule-fails/cardinality "
          f"verdict bands + _train_student_lrmode wiring for BOTH lr_modes via "
          f"tiny synthetic training + determinism-pinning idempotence) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
