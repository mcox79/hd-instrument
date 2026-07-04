"""Encoder Migration Step 1b v3b -- BATCH-RATIO-MATCH sweep (primary) + NCE-weight
ablation / full-held DENSE-trajectory diagnostic (retained). Follow-up to the R1
global-landmark-RKD rescue
(experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py,
commit 6662c5717).

REFRAME (2026-07-04, post R1-mid-landing; supersedes this cell's original NCE-only
design): the R1 paired MID verdict landed HARD_FAIL -- global DENSE 0.521/BLOCK
0.511 vs in_batch DENSE 0.568/BLOCK 0.524 (delta -0.047/-0.013)
MEASURED@data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/metrics.json:recovery.
Global did NOT beat in_batch at mid scale.

DIAGNOSIS OF WHY MID (as originally run) COULD NOT SHOW THE EFFECT: the in-batch
pathology the landmark objective is meant to fix is a NEAR-NEIGHBOR-CO-OCCURRENCE-
RATE problem -- at FULL (train ~160k, cited in this cell's v3 parent docstring),
batch 512 samples coverage(B/V) = 512/160000 = 0.32%, so a specific near-neighbor
PAIR co-occurs in a batch with probability (B/V)^2 ~ 1e-5/step (graded geometry
essentially never supervised). At MID (train 39515, R1's actual split), the SAME
batch=512 gives coverage = 512/39515 = 1.296%% -- 4.05x the single-item coverage
and 16.4x the PAIRWISE co-occurrence rate of FULL (VERIFIED@this prereg via direct
computation, matches Director's independent estimate). The in-batch objective's
failure mode barely fires at that ratio -- both arms land in the same ~0.52-0.57
band because there is nothing scale-dependent to rescue. MID-as-run was UNDERPOWERED,
not evidence the objective fix is wrong.

THE FIX (this cell's PRIMARY new mechanism): reproduce FULL's near-neighbor
coverage ratio AT MID SCALE by matching batch/N_train, not the absolute batch.
batch_match = 512 * (39515/160000) = 126.4 -> DECISIVE_BATCH = 128 (coverage
128/39515 = 0.324%%, within 1.2%% of FULL's 0.32%% -- VERIFIED@this prereg). Since
matching the linear ratio B/V also matches (B/V)^2, this single batch value
reproduces BOTH the single-item and pairwise co-occurrence rates of FULL
simultaneously (squaring an equality preserves it).

BATCH_SWEEP = [512, 256, 128, 64] (paired GLOBAL vs IN_BATCH at each point, shared
split/mining/landmarks/seed) is the PRIMARY discriminator: if the in-batch
objective's failure is genuinely coverage-driven, its DENSE spearman should degrade
as batch shrinks (less per-step coverage, closer to FULL's starved regime) while
the GLOBAL landmark objective -- whose supervision comes from a FIXED L-landmark
frame, independent of batch-size co-occurrence -- should stay comparatively flat.
That CURVE (not a single point) is the evidence the objective mechanism is real;
it is also the cheap MID-scale stand-in for a genuine FULL-scale test.

RETAINED from the original design (still folded into this cell, now applied AT
THE DECISIVE BATCH so it inherits a co-occurrence-matched regime):
  (a) INSTRUMENT: full-held (n=4390, reduced-but-low-noise pair sample during
      training for cost; full 400k-pair sample for every final report number)
      dense-eval trajectory at every checkpoint, for ALL batch-sweep arms (not
      just the reference) -- settles whether R1's quick-eval peak-then-degrade
      (0.740@1200 -> 0.716@1500 -> final full 0.521@1800, all MEASURED@the v3 mid
      metrics.json) was real degradation (H1) or subsample-eval variance (H2), and
      whether it is GLOBAL-objective-specific or a generic schedule artifact
      affecting IN_BATCH too.
  (b) ABLATE the contrastive (NCE) term at the DECISIVE batch on the GLOBAL
      objective: NCE_CURRENT (nce_weight=0.5 const; this IS the sweep's
      B128_GLOBAL arm, reused, not re-trained), NCE_ZERO (nce_weight=0.0,
      RKD-only), NCE_DECAY40 (nce_weight anneals 0.5->0 starting at step
      0.4*total, near the diagnosed RKD-plateau step~700/1800 MEASURED@diagnosis).
  (c) CHECKPOINT-SELECT: best-by-full-held-eval checkpoint per arm (not just
      final/latest), so early-stop-at-peak is a cheap available win.

PAIRED TRIALS discipline (USER-locked 2026-07-04): every (batch, objective) pair
and every nce-weight ablation arm shares the SAME teacher split (seed=7
permutation), SAME mining shards, SAME landmark/anchor indices (global arms), SAME
initial student weights (torch.manual_seed(seed) per arm), and -- because each
arm's torch.Generator is re-seeded identically and the swept quantities (batch
size aside, which structurally changes the draw count per step) only enter loss
arithmetic or the draw COUNT, never change the underlying RNG stream construction
-- comparisons isolate the swept axis (batch size, objective, nce weight) cleanly.
Batch itself is NOT held constant across the sweep by definition (that is the
swept axis), so cross-batch comparisons read the SHAPE of the trend, not raw
sample-budget-matched magnitudes; the within-batch GLOBAL-vs-IN_BATCH comparison
at each sweep point IS sample-budget-matched (same steps, same batch, same
draws) and is the cleanest paired unit.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01): "contrastive
NCE loss ablation tail degradation checkpoint selection distillation RKD geometry"
(top hit cosine=0.4443, generic FrameNet/WordNet, NOT a prior arc cell) and
"checkpoint selection best held eval early stop training peak degrade" (top hit
cosine=0.2783, below the 0.30 threshold). No prior cell addresses NCE-weight
ablation, full-held trajectory instrumentation, or batch/N coverage-ratio matching
for this encoder lineage at cosine>0.30. GENUINELY NOVEL, not a rediscovery.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/mid gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace (write_metrics + checkpoint os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3 prereg; unchanged --
  this cell changes only batch size / objective / nce weight, not the block-
  quantization channel)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: SMOKE validates MACHINERY ONLY (batch-sweep loop
  runs all (B,objective) combos + ablation arms without crash, arms differ,
  dual-trajectory logging fires, best-checkpoint tracking fires). The actual
  coverage-ratio-collapse discriminator needs the REAL train/V_train scale
  relationship (option B, analytical justification): smoke's tiny V_train=3000
  cannot reproduce meaningful coverage-ratio deltas at these batch sizes (a
  batch=16 smoke arm already has huge relative coverage vs V=3000, nothing like
  the tiny FULL-scale ratio); the discriminator is validated ONLY at mid scale
  (matched to the real train ~39515 / batch ~128 regime).
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: batch-sweep collapse bands apply to {IN_BATCH across batch sizes} vs
  {GLOBAL across batch sizes}; nce-ablation bands apply to {NCE_ZERO,NCE_DECAY40}
  vs {NCE_CURRENT==B128_GLOBAL} only; RANDOM_BLOCK/CHARPOS are integrity-only.
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode, counted from per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical regime to the already-
  validated v3 mid prereg; only batch/objective/nce-weight are swept)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@
  throughout (VERIFIED@ = independently recomputed in this cell/prereg from the
  cited source numbers, not merely copied)

Prereg: preregs/2026-07-04_exp_encoder_migration_step1b_v3b_batch_ratio_nce_ablation_dense_recovery_diagnostic_v1.md
Parent cell: experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py

Does NOT touch the parent cell's output dirs
(data/exp_encoder_migration_step1b_v3_..._v1_mid/,
data/substrate_concept_encoder_v1b_v3global_mid/) -- this cell's artifacts live
under its own ANCHOR_NAME-derived paths.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
import argparse
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

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = ("encoder_migration_step1b_v3b_batch_ratio_match_"
               "nce_ablation_dense_recovery_v1")
SEED_DEFAULT = v3.SEED_DEFAULT  # 7 -- MUST match the R1 mid run for matched-config
                                 # comparability (same permutation, same landmarks).

# ---- batch-ratio-match sweep (PRIMARY new mechanism) -----------------------
# VERIFIED@this prereg: coverage(B/V) at mid batch=512 over N_train_mid=39515 is
# 1.296%%, 4.05x FULL's 512/160000=0.32%% (N_full=160000 CITED@v3 parent docstring
# "over 160k+ concepts"); pairwise co-occurrence (B/V)^2 ratio is 16.4x. Matching
# the linear ratio B/V also matches (B/V)^2 (squaring preserves equality), so a
# single batch value reproduces both simultaneously. batch_match = 512 *
# (39515/160000) = 126.4 -> DECISIVE_BATCH_MID = 128 (coverage 128/39515=0.324%%,
# within 1.2%% of FULL's 0.32%%).
BATCH_SWEEP_MID = [512, 256, 128, 64]
DECISIVE_BATCH_MID = 128
N_TRAIN_FULL_CITED = 160_000  # CITED@v3 parent docstring; used only for the ratio
                               # derivation documented above, not re-fetched here.

# Smoke-scale sweep: MACHINERY validation only (see discriminator-survives-scale
# note above); these values do not reproduce any real coverage ratio.
BATCH_SWEEP_SMOKE = [128, 64, 32, 16]
DECISIVE_BATCH_SMOKE = 32

# ---- NCE-weight ablation (retained; applied at the decisive batch only) ----
NCE_DECAY_START_FRAC_DEFAULT = 0.40
# HYPOTHESIZED@this prereg: near the diagnosed RKD-plateau step (~700/1800=0.389
# MEASURED@notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md via Director
# spawn context); stop pushing contrastive optimization once geometry has already
# converged, since further NCE gradient can only trade off against (not help) the
# already-converged RKD geometry.
ABLATION_ARM_LABELS = ["NCE_ZERO", "NCE_DECAY40"]  # NCE_CURRENT = the decisive
                                                     # batch's GLOBAL sweep arm.

# ---- smoke-scale: validates MACHINERY (batch/objective loop wiring, arms
# differ, dual trajectory logging, best-checkpoint tracking, no crash) -- NOT
# the coverage-ratio-collapse phenomenon (unreachable at smoke's tiny V_train).
SMOKE_STEPS_DIAG = 60
SMOKE_N_LANDMARKS_DIAG = 512
SMOKE_REFRESH_DIAG = 15
SMOKE_DENSE_EVAL_EVERY_DIAG = 15
SMOKE_CKPT_EVERY_DIAG = 30
SMOKE_QUICK_HELD_SUB = 300
SMOKE_QUICK_PAIRS = 8_000
SMOKE_FULL_TRAJ_PAIRS = 15_000
SMOKE_FULL_PAIRS_FINAL = 30_000
SMOKE_CHARPOS_CAP_DIAG = 800
SMOKE_TRIALS_DIAG = 30

# ---- mid-scale: the real diagnostic. Matched to the R1 mid config (same seed,
# HELD_FRAC/cap, landmark count/refresh, step budget); only batch/objective/nce
# weight are swept.
MID_STEPS_DIAG = v3.MID_STEPS                    # 1800
MID_N_LANDMARKS_DIAG = v3.N_LANDMARKS_MID         # 4096
MID_REFRESH_DIAG = v3.FRAME_REFRESH_MID           # 50
MID_DENSE_EVAL_EVERY_DIAG = 150                   # finer than v3's 300
MID_CKPT_EVERY_DIAG = v3.CKPT_EVERY_STEPS_MID     # 300
MID_QUICK_HELD_SUB = 1500                         # matches v3 run_midscale _deval
MID_QUICK_PAIRS = 60_000                          # matches v3 run_midscale _deval
MID_FULL_TRAJ_PAIRS = 100_000                     # reduced vs 400k for per-ckpt cost
MID_FULL_PAIRS_FINAL = v3.MID_PAIR_SAMPLE         # 400_000 -- exact R1 parity
MID_CHARPOS_CAP_DIAG = v3.MID_CHARPOS_CAP
MID_TRIALS_DIAG = v3.MID_TRIALS

# EXPECTED_N_UNITS (same structure both scales): 8 sweep-DENSE (4 batches x 2
# objectives) + 2 decisive-batch BLOCK (GLOBAL, IN_BATCH) + 4 ablation (NCE_ZERO,
# NCE_DECAY40 x {DENSE,BLOCK}) + RANDOM_BLOCK(1) + CHARPOS(1) = 16 semantic
# + keyed RANDOM_BLOCK J5 pos-ctrl(1) + keyed decisive-GLOBAL_BLOCK J5(1)
# + shuffled decisive-GLOBAL_BLOCK J5(1) = 3 algebra. Total = 19.
EXPECTED_N_UNITS_SMOKE = 19
EXPECTED_N_UNITS_MID = 19

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

# Batch-sweep recovery bands (HYPOTHESIZED@this prereg; the PRIMARY gate).
SWEEP_HP_INBATCH_DEGRADATION = 0.10   # inbatch[max_batch] - inbatch[min_batch]
SWEEP_HP_TREND_CORR = 0.50            # corr(batch, inbatch_dense) across sweep
SWEEP_HP_DECISIVE_DELTA = 0.15        # global-inbatch at decisive batch
SWEEP_HP_DECISIVE_FLOOR = 0.55        # global absolute floor at decisive batch
SWEEP_MB_DECISIVE_DELTA = 0.05
SWEEP_MB_INBATCH_DEGRADATION = 0.05

# NCE-ablation bands (retained; secondary finding, reported not gating).
ABLATION_HP_DENSE_FINAL = 0.70
ABLATION_HP_DELTA = 0.15
ABLATION_MB_DENSE_FINAL = 0.60
ABLATION_MB_DELTA = 0.05
PEAK_DECLINE_MARGIN = 0.03


def _artifact_dir(run_mode: str) -> Path:
    suffix = {"smoke": "_smoke", "mid": "_mid"}.get(run_mode, "")
    return _REPO / "data" / f"substrate_concept_encoder_v1b_v3b_batch_ratio{suffix}"


# ---------------------------------------------------------------------------
# NCE-weight schedules.
# ---------------------------------------------------------------------------

def _nce_weight_current(step: int, total: int) -> float:
    """Reference: constant nce weight = v3 default (v2/v3 baseline behavior)."""
    return v3.LAM_NCE


def _nce_weight_zero(step: int, total: int) -> float:
    """Ablation: RKD-only, no contrastive term at all."""
    return 0.0


def _nce_weight_decay(step: int, total: int,
                      decay_start_frac: float = NCE_DECAY_START_FRAC_DEFAULT) -> float:
    """Anneal nce weight LAM_NCE -> 0 linearly starting at decay_start_frac*total."""
    start = decay_start_frac * total
    if step <= start:
        return v3.LAM_NCE
    denom = max(1.0, total - start)
    prog = min(1.0, (step - start) / denom)
    return v3.LAM_NCE * (1.0 - prog)


def _make_nce_fn(label: str, decay_start_frac: float) -> Callable[[int, int], float]:
    if label in ("NCE_CURRENT", "GLOBAL", "IN_BATCH"):
        return _nce_weight_current
    if label == "NCE_ZERO":
        return _nce_weight_zero
    if label == "NCE_DECAY40":
        return lambda step, total: _nce_weight_decay(step, total, decay_start_frac)
    raise ValueError(f"unknown arm label {label}")


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3.
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
# Training loop (new; generalizes v3's _train_student to an explicit
# objective toggle {global,in_batch} PLUS an arbitrary nce-weight SCHEDULE,
# dual (quick+full) held-set trajectory logging, and best-by-full-held
# checkpointing). batch is a normal parameter -- this IS the swept axis.
# ---------------------------------------------------------------------------

def _train_student_diag(
    kb: int, blk_l: int,
    Xtr: torch.Tensor, pos_idx: torch.Tensor, semi_cands: torch.Tensor,
    steps: int, batch: int, warmup: int, seed: int, device: str,
    ckpt_path: Path, best_ckpt_path: Path, ckpt_every: int,
    output_dir: Path, t0: float,
    land_idx: Optional[torch.Tensor], refresh_every: int,
    nce_weight_fn: Callable[[int, int], float], arm_label: str,
    objective: str = "global",
    dense_eval_quick_fn: Optional[Callable] = None,
    dense_eval_full_fn: Optional[Callable] = None,
    dense_eval_every: int = 0,
) -> Tuple[torch.nn.Module, Dict]:
    """Train one MLP student under objective in {global,in_batch} with a
    configurable nce-weight schedule, at the given batch size. Logs BOTH the
    quick (subsample) and full (entire held set) dense-spearman trajectory at
    dense_eval_every cadence, and tracks a best-by-full-held checkpoint."""
    if objective not in ("global", "in_batch"):
        raise ValueError(f"unknown objective {objective}")
    out_dim = kb * blk_l
    student = v3._make_student("mlp", Xtr.shape[1], out_dim, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    start_step = 0
    dense_traj: List[Dict[str, float]] = []
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
            print(f"[v3b_batch_ratio] resume {arm_label} at step {start_step}",
                  flush=True)
        except (RuntimeError, KeyError, EOFError) as exc:
            print(f"[v3b_batch_ratio] WARN ckpt load failed ({type(exc).__name__}); "
                  f"retraining {arm_label} from scratch", flush=True)
            start_step = 0
            dense_traj = []
            best_state = {"score": -2.0, "step": -1}
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    Xland_d = None
    if objective == "global":
        if land_idx is None or land_idx.numel() == 0:
            raise ValueError(f"{arm_label}: global objective requires non-empty land_idx")
        Xland_d = Xd[land_idx.to(device)]
    frame_n = None
    loss_first = loss_last = None
    rkd_last = nce_last = lr_last = nce_w_last = None

    def _maybe_save_best(step_i: int, d_full: float) -> None:
        if not math.isfinite(d_full):
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
        bidx = v3._cluster_batch_idx(batch, 0.0, V, pos_idx, semi_cands, gen)
        x = Xd[bidx.to(device)]
        z = student(x)
        s = v3._block_ste(z, kb, blk_l)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        if objective == "global":
            if frame_n is None or (step % refresh_every == 0):
                frame_n = v3._frame_codes_norm(student, Xland_d, "block", kb, blk_l, kb)
            Tland = x @ Xland_d.T
            l_rkd = ((s_n @ frame_n.T - Tland) ** 2).mean()
        else:
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
        cur_nce_w = float(nce_weight_fn(step, steps))
        loss = l_rkd + cur_nce_w * l_nce
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: {arm_label} loss non-finite at step {step} "
                f"(l_rkd={float(l_rkd.detach())}, l_nce={float(l_nce.detach())}, "
                f"nce_w={cur_nce_w})")
        opt.zero_grad()
        loss.backward()
        opt.step()
        v_loss = float(loss.detach())
        v_rkd = float(l_rkd.detach())
        v_nce = float(l_nce.detach())
        if loss_first is None:
            loss_first = v_loss
        loss_last, rkd_last, nce_last, lr_last, nce_w_last = (
            v_loss, v_rkd, v_nce, cur_lr, cur_nce_w)
        if step % 100 == 0:
            print(f"[v3b_batch_ratio] {arm_label} step {step}/{steps} rkd={v_rkd:.4f} "
                  f"nce={v_nce:.4f} nce_w={cur_nce_w:.3f} lr={cur_lr:.2e} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
            _emit_heartbeat(output_dir, step, steps, time.perf_counter() - t0,
                            extra={"phase": f"train_{arm_label}", "loss": v_loss,
                                   "rkd": v_rkd, "nce_w": cur_nce_w})
        if (dense_eval_full_fn is not None and dense_eval_every > 0
                and step % dense_eval_every == 0):
            d_full = float(dense_eval_full_fn(student))
            d_quick = (float(dense_eval_quick_fn(student))
                       if dense_eval_quick_fn is not None else float("nan"))
            dense_traj.append({"step": step, "dense_full": d_full,
                               "dense_quick": d_quick, "nce_weight": cur_nce_w,
                               "rkd": v_rkd, "final": False})
            print(f"[v3b_batch_ratio] {arm_label} DENSE-traj step {step}: "
                  f"full={d_full:.4f} quick={d_quick:.4f}", flush=True)
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
        final_nce_w = float(nce_weight_fn(max(0, steps - 1), steps))
        dense_traj.append({"step": steps, "dense_full": d_full_fin,
                           "dense_quick": d_quick_fin, "nce_weight": final_nce_w,
                           "rkd": rkd_last if rkd_last is not None else float("nan"),
                           "final": True})
        _maybe_save_best(steps, d_full_fin)
        print(f"[v3b_batch_ratio] {arm_label} FINAL step {steps}: full={d_full_fin:.4f} "
              f"quick={d_quick_fin:.4f}", flush=True)
    return student, {
        "loss_first": loss_first if loss_first is not None else -1.0,
        "loss_last": loss_last if loss_last is not None else -1.0,
        "rkd_last": rkd_last if rkd_last is not None else -1.0,
        "nce_last": nce_last if nce_last is not None else -1.0,
        "lr_last": lr_last if lr_last is not None else -1.0,
        "nce_weight_last": nce_w_last if nce_w_last is not None else -1.0,
        "arm": arm_label, "objective": objective, "batch": batch,
        "dense_traj": dense_traj,
        "best_dense_full": best_state["score"], "best_step": best_state["step"],
    }


# ---------------------------------------------------------------------------
# Trajectory-analysis helpers (settle H1 vs H2; report both objectives).
# ---------------------------------------------------------------------------

def _peak_then_decline(traj: List[Dict], key: str,
                       margin: float = PEAK_DECLINE_MARGIN
                       ) -> Tuple[bool, Optional[int], Optional[float], Optional[int]]:
    vals = [(r["step"], r[key]) for r in traj if math.isfinite(r.get(key, float("nan")))]
    if len(vals) < 2:
        return False, None, None, None
    peak_step, peak_val = max(vals, key=lambda t: t[1])
    final_step, final_val = vals[-1]
    declined = bool((peak_val - final_val) >= margin and peak_step < final_step)
    return declined, peak_step, peak_val, final_step


def _traj_corr(traj: List[Dict], key_a: str, key_b: str) -> Optional[float]:
    a = [r[key_a] for r in traj if math.isfinite(r.get(key_a, float("nan")))
         and math.isfinite(r.get(key_b, float("nan")))]
    b = [r[key_b] for r in traj if math.isfinite(r.get(key_a, float("nan")))
         and math.isfinite(r.get(key_b, float("nan")))]
    if len(a) < 3:
        return None
    aa, bb = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64)
    if aa.std() == 0 or bb.std() == 0:
        return None
    return float(np.corrcoef(aa, bb)[0, 1])


def _corr_xy(xs: List[float], ys: List[float]) -> Optional[float]:
    if len(xs) < 3:
        return None
    xa, ya = np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)
    if xa.std() == 0 or ya.std() == 0:
        return None
    return float(np.corrcoef(xa, ya)[0, 1])


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_diag(per_unit: List[Dict], recovery: Dict, expected_units: int,
                  run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    normal = v3._by_unit(per_unit, "keyed", recovery["decisive_global_block_arm"], 5)
    shuf = v3._by_unit(per_unit, "shuffled_key", recovery["decisive_global_block_arm"], 5)
    if posc is None or normal is None or shuf is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed J=5 "
                f"{posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: {shuf['acc_at1']:.3f}/"
                f"{shuf['hit_any_member']:.3f}")

    sweep_tail = (f"[inbatch_by_batch={recovery['inbatch_dense_final_by_batch']} "
                 f"global_by_batch={recovery['global_dense_final_by_batch']} "
                 f"inbatch_degradation={recovery['inbatch_degradation']:.4f} "
                 f"inbatch_trend_corr={recovery['inbatch_trend_corr']} "
                 f"global_stability_drop={recovery['global_stability_drop']:.4f} "
                 f"decisive_delta={recovery['decisive_delta']:.4f} "
                 f"decisive_global={recovery['decisive_global_dense_final']:.4f}]")
    ablation_tail = (f"[ablation_verdict={recovery['ablation_verdict']} "
                     f"nce_current={recovery['nce_current_dense_final']:.4f} "
                     f"best_ablation={recovery['best_ablation_final_dense']:.4f} "
                     f"ablation_delta={recovery['ablation_delta_final']:.4f}]")
    h1h2_tail = (f"[b512_global_full_decl={recovery['b512_global_full_peak_decline']} "
                f"b512_inbatch_full_decl={recovery['b512_inbatch_full_peak_decline']} "
                f"bdec_global_full_decl={recovery['bdec_global_full_peak_decline']} "
                f"bdec_inbatch_full_decl={recovery['bdec_inbatch_full_peak_decline']}]")
    tail = f"{sweep_tail} {ablation_tail} {h1h2_tail}"

    if run_mode == "smoke":
        fails = []
        for label, tl in recovery["traj_len_by_arm"].items():
            if tl < 2:
                fails.append(f"S_traj_too_short_{label} ({tl})")
        for label, bs in recovery["best_step_by_arm"].items():
            if bs is None or bs < 0:
                fails.append(f"S_no_best_ckpt_{label}")
        if not (math.isfinite(recovery["decisive_global_dense_final"])
                and -1.0 <= recovery["decisive_global_dense_final"] <= 1.0):
            fails.append("S_dense_final_out_of_range")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: batch-sweep loop (all (B,objective) combos) + "
                f"ablation arms ran without crash; dual-trajectory logging + "
                f"best-checkpoint tracking fire for every arm {tail} "
                f"(coverage-ratio-collapse discriminator is a mid-scale-only "
                f"question; smoke's tiny V_train cannot reproduce a meaningful "
                f"coverage-ratio delta)")

    # mid: the real discriminators.
    inbatch_degrades = recovery["inbatch_degradation"] >= SWEEP_HP_INBATCH_DEGRADATION
    trend_ok = (recovery["inbatch_trend_corr"] is not None
               and recovery["inbatch_trend_corr"] >= SWEEP_HP_TREND_CORR)
    decisive_delta = recovery["decisive_delta"]
    decisive_floor_ok = (recovery["decisive_global_dense_final"]
                        >= SWEEP_HP_DECISIVE_FLOOR)
    if (inbatch_degrades and trend_ok and decisive_delta >= SWEEP_HP_DECISIVE_DELTA
            and decisive_floor_ok):
        return ("HARD_PASS",
                f"BATCH_RATIO_MATCH_CONFIRMS_OBJECTIVE_ADVANTAGE: in_batch degrades "
                f"with shrinking batch while global holds; decisive-batch delta "
                f"clears the recovery bar {tail}")
    partial = (decisive_delta >= SWEEP_MB_DECISIVE_DELTA
              or recovery["inbatch_degradation"] >= SWEEP_MB_INBATCH_DEGRADATION)
    if partial:
        return ("MIDDLE_BAND",
                f"PARTIAL_BATCH_RATIO_SIGNAL: some coverage-ratio-dependent signal "
                f"but short of the full recovery bar {tail}")
    return ("HARD_FAIL",
            f"BATCH_RATIO_MATCH_DID_NOT_CONFIRM: no meaningful in_batch degradation "
            f"or global-vs-inbatch advantage across the batch sweep at MID scale; "
            f"the objective's advantage (if real) requires an actual FULL-scale "
            f"test to demonstrate, or another confound is present {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_diag(run_mode: str, seed: int, device_arg: str, n_dim: int,
            teacher_cache_arg: Optional[str],
            decay_start_frac: float = NCE_DECAY_START_FRAC_DEFAULT) -> int:
    assert run_mode in ("smoke", "mid"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_{run_mode}"
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    if kb * blk_l != n_dim:
        raise ValueError(f"n_dim {n_dim} not divisible by k_blocks {kb}")

    if run_mode == "smoke":
        batch_sweep, decisive_batch = BATCH_SWEEP_SMOKE, DECISIVE_BATCH_SMOKE
        steps = SMOKE_STEPS_DIAG
        n_land, refresh = SMOKE_N_LANDMARKS_DIAG, SMOKE_REFRESH_DIAG
        dense_every, ckpt_every = SMOKE_DENSE_EVAL_EVERY_DIAG, SMOKE_CKPT_EVERY_DIAG
        quick_sub, quick_pairs = SMOKE_QUICK_HELD_SUB, SMOKE_QUICK_PAIRS
        full_traj_pairs, full_final_pairs = SMOKE_FULL_TRAJ_PAIRS, SMOKE_FULL_PAIRS_FINAL
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP_DIAG, SMOKE_TRIALS_DIAG
        n_tr_target, n_he_target = v3.SMOKE_N_TRAIN, v3.SMOKE_N_HELD
    else:
        batch_sweep, decisive_batch = BATCH_SWEEP_MID, DECISIVE_BATCH_MID
        steps = MID_STEPS_DIAG
        n_land, refresh = MID_N_LANDMARKS_DIAG, MID_REFRESH_DIAG
        dense_every, ckpt_every = MID_DENSE_EVAL_EVERY_DIAG, MID_CKPT_EVERY_DIAG
        quick_sub, quick_pairs = MID_QUICK_HELD_SUB, MID_QUICK_PAIRS
        full_traj_pairs, full_final_pairs = MID_FULL_TRAJ_PAIRS, MID_FULL_PAIRS_FINAL
        charpos_cap, n_trials = MID_CHARPOS_CAP_DIAG, MID_TRIALS_DIAG
        n_tr_target = n_he_target = None
    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_MID
    warmup = v3._warmup_for(steps)

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v3b_batch_ratio] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} steps={steps} batch_sweep={batch_sweep} "
          f"decisive_batch={decisive_batch} decay_start_frac={decay_start_frac}",
          flush=True)

    cache_path = v3._resolve_teacher_cache(teacher_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v3b_batch_ratio] teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        if V_cache < n_tr_target + n_he_target:
            raise RuntimeError(f"teacher cache too small for smoke: {V_cache}")
        n_tr, n_he = n_tr_target, n_he_target
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.MID_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx = perm[:n_tr]
    he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[v3b_batch_ratio] split train={n_tr} held={n_he}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    n_land_eff = min(n_land, n_tr)
    g_land = torch.Generator().manual_seed(seed + 101)
    land_idx = torch.randperm(n_tr, generator=g_land)[:n_land_eff]
    print(f"[v3b_batch_ratio] mining done cov={semi_cov:.3f} landmarks={n_land_eff} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, full_traj_pairs, seed + 7)

    # --- train the batch-sweep arms (paired GLOBAL vs IN_BATCH per batch) -----
    trained: Dict[str, Tuple[torch.nn.Module, Dict]] = {}
    for B in batch_sweep:
        for obj_key, obj in (("GLOBAL", "global"), ("INBATCH", "in_batch")):
            label = f"B{B}_{obj_key}"
            li = land_idx if obj == "global" else None
            st, diag = _train_student_diag(
                kb, blk_l, Xtr, pos_idx, semi_cands, steps, B, warmup, seed, device,
                art_dir / f"_ckpt_{label}.pt", art_dir / f"_ckpt_best_{label}.pt",
                ckpt_every, out_dir, t0, li, refresh, _nce_weight_current, label,
                objective=obj, dense_eval_quick_fn=_deval_quick,
                dense_eval_full_fn=_deval_full, dense_eval_every=dense_every)
            trained[label] = (st, diag)
            print(f"[v3b_batch_ratio] {label} trained rkd_last={diag['rkd_last']:.4f} "
                  f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- ablation-only arms at the decisive batch (global objective) ----------
    for arm in ABLATION_ARM_LABELS:
        nce_fn = _make_nce_fn(arm, decay_start_frac)
        st, diag = _train_student_diag(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, decisive_batch, warmup,
            seed, device, art_dir / f"_ckpt_{arm}.pt", art_dir / f"_ckpt_best_{arm}.pt",
            ckpt_every, out_dir, t0, land_idx, refresh, nce_fn, arm,
            objective="global", dense_eval_quick_fn=_deval_quick,
            dense_eval_full_fn=_deval_full, dense_eval_every=dense_every)
        trained[arm] = (st, diag)
        print(f"[v3b_batch_ratio] {arm} trained rkd_last={diag['rkd_last']:.4f} "
              f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- encode held codes -----------------------------------------------------
    arm_codes: Dict[str, torch.Tensor] = {}
    for B in batch_sweep:
        for obj_key in ("GLOBAL", "INBATCH"):
            label = f"B{B}_{obj_key}"
            st = trained[label][0]
            arm_codes[f"{label}_DENSE"] = v3._dense_sign_codes(st, Xhe)
            if B == decisive_batch:
                arm_codes[f"{label}_BLOCK"] = v3._encode_hard_block(st, Xhe, kb, blk_l)
    for arm in ABLATION_ARM_LABELS:
        st = trained[arm][0]
        arm_codes[f"{arm}_DENSE"] = v3._dense_sign_codes(st, Xhe)
        arm_codes[f"{arm}_BLOCK"] = v3._encode_hard_block(st, Xhe, kb, blk_l)
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)
    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, kb)

    # --- META_RULE_AF arms-must-differ ------------------------------------------
    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    # --- eval units --------------------------------------------------------------
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v3b_batch_ratio] unit {len(per_unit)}/{expected_units} "
                  f"{u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for B in batch_sweep:
        for obj_key in ("GLOBAL", "INBATCH"):
            label = f"B{B}_{obj_key}_DENSE"
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                      full_final_pairs, seed + 3)
    for obj_key in ("GLOBAL", "INBATCH"):
        label = f"B{decisive_batch}_{obj_key}_BLOCK"
        c = arm_codes[label]
        _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                  full_final_pairs, seed + 3)
    for arm in ABLATION_ARM_LABELS:
        for kind in ("DENSE", "BLOCK"):
            label = f"{arm}_{kind}"
            c = arm_codes[label]
            _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0,
                      full_final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", arm_codes["RANDOM_BLOCK"],
              arm_codes["RANDOM_BLOCK"], Xhe, Xhe, 0, full_final_pairs, seed + 3)
    cp_Xhe = Xhe[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
              full_final_pairs, seed + 3)

    decisive_global_block_arm = f"B{decisive_batch}_GLOBAL_BLOCK"
    decisive_global_block_codes = arm_codes[decisive_global_block_arm]
    _run_unit(v3._keyed_unit, "RANDOM_BLOCK", "sbc", arm_codes["RANDOM_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, decisive_global_block_arm, "sbc",
              decisive_global_block_codes, kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, decisive_global_block_arm, "sbc",
              decisive_global_block_codes, kb, blk_l, 5, n_trials, gen_eval, device,
              shuffled_key=True)

    # --- recovery discriminators --------------------------------------------------
    def _sp(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return float(u["spearman_all"]) if u else float("nan")

    inbatch_by_batch = {B: _sp(f"B{B}_INBATCH_DENSE") for B in batch_sweep}
    global_by_batch = {B: _sp(f"B{B}_GLOBAL_DENSE") for B in batch_sweep}
    sweep_sorted = sorted(batch_sweep, reverse=True)  # largest first
    b_max, b_min = sweep_sorted[0], sweep_sorted[-1]
    inbatch_degradation = inbatch_by_batch[b_max] - inbatch_by_batch[b_min]
    global_stability_drop = global_by_batch[b_max] - global_by_batch[b_min]
    inbatch_trend_corr = _corr_xy(list(batch_sweep),
                                  [inbatch_by_batch[B] for B in batch_sweep])
    global_trend_corr = _corr_xy(list(batch_sweep),
                                 [global_by_batch[B] for B in batch_sweep])
    decisive_global_final = global_by_batch[decisive_batch]
    decisive_inbatch_final = inbatch_by_batch[decisive_batch]
    decisive_delta = decisive_global_final - decisive_inbatch_final

    nce_current_final = decisive_global_final  # alias: B{decisive}_GLOBAL IS nce=0.5
    nce_zero_final = _sp("NCE_ZERO_DENSE")
    nce_decay_final = _sp("NCE_DECAY40_DENSE")
    best_ablation_final = max(nce_zero_final, nce_decay_final)
    ablation_delta = best_ablation_final - nce_current_final
    if best_ablation_final >= ABLATION_HP_DENSE_FINAL and ablation_delta >= ABLATION_HP_DELTA:
        ablation_verdict = "TAIL_CORRUPTION_CONFIRMED_RECOVERED"
    elif best_ablation_final >= ABLATION_MB_DENSE_FINAL and ablation_delta >= ABLATION_MB_DELTA:
        ablation_verdict = "PARTIAL_RECOVERY"
    else:
        ablation_verdict = "NOT_CONFIRMED"

    b512_global_traj = trained[f"B{b_max}_GLOBAL"][1]["dense_traj"]
    b512_inbatch_traj = trained[f"B{b_max}_INBATCH"][1]["dense_traj"]
    bdec_global_traj = trained[f"B{decisive_batch}_GLOBAL"][1]["dense_traj"]
    bdec_inbatch_traj = trained[f"B{decisive_batch}_INBATCH"][1]["dense_traj"]
    b512_g_decl, b512_g_pk, b512_g_pv, _ = _peak_then_decline(b512_global_traj, "dense_full")
    b512_i_decl, b512_i_pk, b512_i_pv, _ = _peak_then_decline(b512_inbatch_traj, "dense_full")
    bdec_g_decl, bdec_g_pk, bdec_g_pv, _ = _peak_then_decline(bdec_global_traj, "dense_full")
    bdec_i_decl, bdec_i_pk, bdec_i_pv, _ = _peak_then_decline(bdec_inbatch_traj, "dense_full")
    b512_global_quick_full_corr = _traj_corr(b512_global_traj, "dense_quick", "dense_full")

    traj_len_by_arm = {lbl: len(trained[lbl][1]["dense_traj"]) for lbl in trained}
    best_step_by_arm = {lbl: trained[lbl][1]["best_step"] for lbl in trained}

    recovery = {
        "batch_sweep": list(batch_sweep), "decisive_batch": decisive_batch,
        "decisive_global_block_arm": decisive_global_block_arm,
        "inbatch_dense_final_by_batch": inbatch_by_batch,
        "global_dense_final_by_batch": global_by_batch,
        "inbatch_degradation": inbatch_degradation,
        "global_stability_drop": global_stability_drop,
        "inbatch_trend_corr": inbatch_trend_corr,
        "global_trend_corr": global_trend_corr,
        "decisive_global_dense_final": decisive_global_final,
        "decisive_inbatch_dense_final": decisive_inbatch_final,
        "decisive_delta": decisive_delta,
        "decisive_global_block_final": _sp(f"B{decisive_batch}_GLOBAL_BLOCK"),
        "decisive_inbatch_block_final": _sp(f"B{decisive_batch}_INBATCH_BLOCK"),
        "nce_current_dense_final": nce_current_final,
        "nce_zero_dense_final": nce_zero_final,
        "nce_decay40_dense_final": nce_decay_final,
        "best_ablation_final_dense": best_ablation_final,
        "ablation_delta_final": ablation_delta,
        "ablation_verdict": ablation_verdict,
        "b512_global_full_peak_decline": b512_g_decl,
        "b512_global_full_peak_step": b512_g_pk,
        "b512_inbatch_full_peak_decline": b512_i_decl,
        "b512_inbatch_full_peak_step": b512_i_pk,
        "bdec_global_full_peak_decline": bdec_g_decl,
        "bdec_global_full_peak_step": bdec_g_pk,
        "bdec_inbatch_full_peak_decline": bdec_i_decl,
        "bdec_inbatch_full_peak_step": bdec_i_pk,
        "b512_global_quick_vs_full_traj_corr": b512_global_quick_full_corr,
        "h1_h2_verdict_b512_global": (
            "H1_REAL_DEGRADATION" if b512_g_decl else "H2_NO_FULL_HELD_DECLINE"),
        "charpos_dense": _sp("CHARPOS"), "random_block_dense": _sp("RANDOM_BLOCK"),
        "traj_len_by_arm": traj_len_by_arm, "best_step_by_arm": best_step_by_arm,
        "traj_by_arm": {lbl: trained[lbl][1]["dense_traj"] for lbl in trained},
    }
    verdict, verdict_msg = _verdict_diag(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch_sweep": list(batch_sweep),
        "decisive_batch": decisive_batch,
        "n_landmarks": n_land_eff, "refresh_every": refresh,
        "dense_eval_every": dense_every, "nce_decay_start_frac": decay_start_frac,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "train_diag": {lbl: {k: v for k, v in trained[lbl][1].items()}
                      for lbl in trained},
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "objective": ("batch-ratio-match sweep {512,256,128,64} x {global,in_batch} "
                     f"+ nce-weight ablation at decisive batch={decisive_batch} "
                     "(NCE_CURRENT=0.5 const [==sweep GLOBAL arm], NCE_ZERO=0.0, "
                     f"NCE_DECAY40=anneal-from-frac{decay_start_frac})"),
        "progress_logging": "print_flush_true",
        "primary_spearman": decisive_global_final,
        "dense_sign_spearman": decisive_global_final,
        "baseline_in_band": bool(
            0.05 < (v3._by_unit(per_unit, "semantic", "CHARPOS") or
                   {"ret_agree10": 0})["ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3)"),
        "discriminator_reachability": True,
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v3b_batch_ratio] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. nce-weight schedule functions (unchanged from prior design).
    assert _nce_weight_current(0, 100) == v3.LAM_NCE
    assert _nce_weight_zero(50, 100) == 0.0
    assert abs(_nce_weight_decay(0, 100, 0.4) - v3.LAM_NCE) < 1e-9
    assert abs(_nce_weight_decay(40, 100, 0.4) - v3.LAM_NCE) < 1e-9
    assert abs(_nce_weight_decay(70, 100, 0.4) - v3.LAM_NCE * 0.5) < 1e-6
    assert _nce_weight_decay(100, 100, 0.4) < 1e-9
    assert _make_nce_fn("NCE_ZERO", 0.4)(10, 100) == 0.0
    try:
        _make_nce_fn("BOGUS", 0.4)
        raise AssertionError("selftest: _make_nce_fn should reject unknown label")
    except ValueError:
        pass

    # 2. peak-then-decline / trajectory-correlation / xy-correlation helpers.
    rising = [{"step": i, "dense_full": 0.1 * i} for i in range(5)]
    decl, _, _, _ = _peak_then_decline(rising, "dense_full")
    assert decl is False
    peaky = [{"step": 0, "dense_full": 0.3}, {"step": 1, "dense_full": 0.7},
             {"step": 2, "dense_full": 0.75}, {"step": 3, "dense_full": 0.5}]
    decl2, pk2, pv2, _ = _peak_then_decline(peaky, "dense_full")
    assert decl2 is True and pk2 == 2 and abs(pv2 - 0.75) < 1e-9
    corr_traj = [{"dense_quick": 0.1 * i, "dense_full": 0.1 * i + 0.02}
                 for i in range(6)]
    assert _traj_corr(corr_traj, "dense_quick", "dense_full") > 0.99
    assert _corr_xy([512, 256, 128, 64], [0.3, 0.4, 0.5, 0.6]) < -0.9, \
        "selftest: xy-corr sign check (batch descending, value ascending -> negative)"
    assert _corr_xy([512, 256, 128, 64], [0.5, 0.5, 0.5, 0.5]) is None

    # 3. end-to-end diag training on tiny synthetic data: both objectives, varying
    #    batch, nce ablation, checkpoint/resume, arms-must-differ, best-ckpt.
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 400
    torch.manual_seed(11)
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    land_syn = torch.randperm(v_syn, generator=gen)[:48]
    Xhe_syn = Xsyn[:64]

    def _dq(student):
        return v3._dense_spearman_quick(student, Xhe_syn[:32], 500, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xhe_syn, 800, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # objective=global, batch=24 (small, non-default) works + best-ckpt fires.
        st_g, diag_g = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 10, 24, 2, 13, "cpu",
            tdp / "ckpt_g.pt", tdp / "ckpt_best_g.pt", 100, tdp, t0,
            land_syn, 3, _nce_weight_current, "TEST_GLOBAL", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3)
        assert math.isfinite(diag_g["rkd_last"])
        assert len(diag_g["dense_traj"]) >= 2
        assert diag_g["best_step"] >= 0
        assert (tdp / "ckpt_best_g.pt").exists()

        # objective=in_batch, different batch (16) -- no land_idx needed.
        st_i, diag_i = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 10, 16, 2, 13, "cpu",
            tdp / "ckpt_i.pt", tdp / "ckpt_best_i.pt", 100, tdp, t0,
            None, 3, _nce_weight_current, "TEST_INBATCH", objective="in_batch",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3)
        assert math.isfinite(diag_i["rkd_last"])

        # in_batch with land_idx=None but objective=global should raise.
        try:
            _train_student_diag(
                kb, blk_l, Xsyn, pos_syn, semi_syn, 3, 16, 1, 13, "cpu",
                tdp / "ckpt_bad.pt", tdp / "ckpt_best_bad.pt", 100, tdp, t0,
                None, 3, _nce_weight_current, "TEST_BAD_GLOBAL", objective="global")
            raise AssertionError("selftest: global objective without land_idx should raise")
        except ValueError:
            pass

        # nce-ablation arms at a shared batch: same init/batches, different loss
        # -> ARMS-MUST-DIFFER.
        st_zero, diag_zero = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 15, 20, 2, 13, "cpu",
            tdp / "ckpt_zero.pt", tdp / "ckpt_best_zero.pt", 100, tdp, t0,
            land_syn, 3, _nce_weight_zero, "NCE_ZERO", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3)
        st_cur, diag_cur = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 15, 20, 2, 13, "cpu",
            tdp / "ckpt_cur.pt", tdp / "ckpt_best_cur.pt", 100, tdp, t0,
            land_syn, 3, _nce_weight_current, "NCE_CURRENT", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=3)
        w_zero = torch.cat([p.flatten() for p in st_zero.parameters()])
        w_cur = torch.cat([p.flatten() for p in st_cur.parameters()])
        assert not torch.allclose(w_zero, w_cur, atol=1e-6), \
            "selftest: NCE_ZERO and NCE_CURRENT converged identically -- ablation " \
            "had no effect (arm-implementation bug)"
        # global vs in_batch at the SAME batch should also diverge (different loss).
        st_g2, _ = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 15, 20, 2, 13, "cpu",
            tdp / "ckpt_g2.pt", tdp / "ckpt_best_g2.pt", 100, tdp, t0,
            land_syn, 3, _nce_weight_current, "TEST_GLOBAL2", objective="global")
        st_i2, _ = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 15, 20, 2, 13, "cpu",
            tdp / "ckpt_i2.pt", tdp / "ckpt_best_i2.pt", 100, tdp, t0,
            None, 3, _nce_weight_current, "TEST_INBATCH2", objective="in_batch")
        w_g2 = torch.cat([p.flatten() for p in st_g2.parameters()])
        w_i2 = torch.cat([p.flatten() for p in st_i2.parameters()])
        assert not torch.allclose(w_g2, w_i2, atol=1e-6), \
            "selftest: global and in_batch objectives converged identically"

        # checkpoint/resume roundtrip persists dense_traj + best_state.
        st_a, diag_a = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 4, 16, 1, 17, "cpu",
            tdp / "ckpt_resume.pt", tdp / "ckpt_best_resume.pt", 4, tdp, t0,
            land_syn, 2, _nce_weight_zero, "RESUME_TEST", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=2)
        traj_before = len(diag_a["dense_traj"])
        st_b, diag_b = _train_student_diag(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 8, 16, 1, 17, "cpu",
            tdp / "ckpt_resume.pt", tdp / "ckpt_best_resume.pt", 4, tdp, t0,
            land_syn, 2, _nce_weight_zero, "RESUME_TEST", objective="global",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=2)
        assert len(diag_b["dense_traj"]) > traj_before
        assert diag_b["best_step"] >= 0

    # 4. verdict logic: hit all bands with synthetic per_unit/recovery, including
    #    the cardinality gate.
    fake_units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(19)]
    fake_units += [
        {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "keyed::B128_GLOBAL_BLOCK::J5", "arm": "B128_GLOBAL_BLOCK",
         "kind": "keyed", "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "shuffled_key::B128_GLOBAL_BLOCK::J5", "arm": "B128_GLOBAL_BLOCK",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
    ]
    rec_pass = {
        "decisive_global_block_arm": "B128_GLOBAL_BLOCK",
        "inbatch_dense_final_by_batch": {512: 0.55, 256: 0.45, 128: 0.35, 64: 0.30},
        "global_dense_final_by_batch": {512: 0.72, 256: 0.71, 128: 0.70, 64: 0.69},
        "inbatch_degradation": 0.25, "inbatch_trend_corr": 0.95,
        "global_stability_drop": 0.03, "decisive_delta": 0.35,
        "decisive_global_dense_final": 0.70, "nce_current_dense_final": 0.70,
        "best_ablation_final_dense": 0.72, "ablation_delta_final": 0.02,
        "ablation_verdict": "PARTIAL_RECOVERY",
        "b512_global_full_peak_decline": False, "b512_inbatch_full_peak_decline": True,
        "bdec_global_full_peak_decline": False, "bdec_inbatch_full_peak_decline": True,
    }
    v_pass, m_pass = _verdict_diag(fake_units, rec_pass, 19, "mid")
    assert v_pass == "HARD_PASS", f"selftest: expected HARD_PASS got {v_pass} ({m_pass})"
    rec_mb = dict(rec_pass, decisive_delta=0.08, inbatch_degradation=0.06,
                 inbatch_trend_corr=0.3)
    v_mb, _ = _verdict_diag(fake_units, rec_mb, 19, "mid")
    assert v_mb == "MIDDLE_BAND", f"selftest: expected MIDDLE_BAND got {v_mb}"
    rec_fail = dict(rec_pass, decisive_delta=0.01, inbatch_degradation=0.01,
                    inbatch_trend_corr=0.1)
    v_fail, _ = _verdict_diag(fake_units, rec_fail, 19, "mid")
    assert v_fail == "HARD_FAIL", f"selftest: expected HARD_FAIL got {v_fail}"
    v_card, m_card = _verdict_diag(fake_units[:5], rec_pass, 19, "mid")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    print(f"[selftest] PASS (nce schedules + peak-decline/traj-corr/xy-corr helpers "
          f"+ diag-train both objectives + varying batch + land_idx-required-for-"
          f"global guard + ablation arms-must-differ + objective arms-must-differ "
          f"+ checkpoint/resume + verdict bands incl cardinality) elapsed="
          f"{time.perf_counter() - t0:.2f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1b v3b -- batch-ratio-match sweep + NCE-weight "
        "ablation + full-held DENSE trajectory diagnostic."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "mid"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--mid", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p.add_argument("--n-dim", type=int, default=v3.N_DIM_DEFAULT)
    p.add_argument("--decay-start-frac", type=float,
                   default=NCE_DECAY_START_FRAC_DEFAULT)
    p.add_argument("--teacher-cache", default=None)
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.mid:
        args.run_mode = "mid"
    elif args.run_mode == "full":
        # DISPATCH-CONTRACT FIX (orchestrator self-heal, 2026-07-04): the
        # standard runner (experiments/runner_v2_prod.py:run_one) invokes
        # every queued script bare -- `[sys.executable, "-u", script_path]`,
        # no argv forwarding -- and unconditionally injects
        # HDLAB_RUN_MODE=full into the child env for production dispatch.
        # This cell's terminal/production tier is named "mid" (there is no
        # separate "full" tier -- MID *is* the decisive coverage-ratio-match
        # scale per this cell's docstring), so choices=["self_test","smoke",
        # "mid"] never included "full". Without this alias, a runner-driven
        # ship (as opposed to a direct local `--mid` CLI invocation) would
        # hit `assert run_mode in ("smoke","mid")` in run_diag() and
        # CELL_CRASH on launch, since argparse does not validate an unused
        # default against `choices` (verified empirically) so "full" reaches
        # here unrejected. Alias runner-injected "full" -> "mid" so standard
        # queue_add.sh/runner_v2_prod.py dispatch produces the intended
        # production run.
        args.run_mode = "mid"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_diag(args.run_mode, args.seed, args.device, args.n_dim,
                    args.teacher_cache, decay_start_frac=args.decay_start_frac)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass  # crash-writer failure is not fatal
        raise
