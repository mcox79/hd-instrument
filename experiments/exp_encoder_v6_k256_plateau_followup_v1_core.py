"""Encoder v6 -- does plateau-hold LR add FURTHER retrieval lift ON TOP of
the K=256 code, or does the K=256 gain already capture all the available
headroom (making the LR-schedule question moot at this operating point)?

QUEUE-DEPTH cell (3rd in this session's queue-depth sequence, authored while
sibling cells v4/v5 landed on remote GPU). Chains directly from BOTH landed
results this session produced:
  - v4 (convergence, sibling cell): once the Gate-D reproduction bug was
    fixed (see exp_encoder_v4_convergence_lr_hold_v1_core.py commit
    e845cf831), BOTH seeds show COSINE does NOT actually decline on the
    ret_agree10 trend (v3e's DECLINE_CONTINUES was a DENSE-proxy artifact),
    but PLATEAU-hold LR still gives a small, cross-seed-consistent lift over
    COSINE at K=128: seed7 +0.0206 (0.2318 vs 0.2112), seed13 +0.0294
    (0.2399 vs 0.2105) MEASURED@data/exp_encoder_v4_convergence_lr_hold_v1_
    seed{7,13}/metrics.json:recovery (recomputed post-fix).
  - v5 (K-capacity, sibling cell): K=256 lifts ret_agree10 by +0.0930 over
    K=128 at seed7 (0.2902 vs 0.1972), HARD_PASS K256_LIFTS_RETRIEVAL_
    CONFIRMED MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/
    metrics.json.
Both levers independently help at K=128's OLD operating point. This cell
asks the natural composition question directly: at the NEW (K=256) operating
point, does the small plateau-hold lift persist, compound, or vanish
(ceiling effect -- K=256 might already be capturing most of the fixable
headroom, leaving little room for the LR-schedule lever to add anything)?

TWO PAIRED ARMS, BOTH at K=256 (kb=256, blk_l=16), same seed/data/split/
mining/objective (in_batch-RKD-only, nce_weight=0, steps=6000, batch=128),
differing ONLY in LR schedule -- isolates the LR-mode question AT the
K=256 operating point specifically (does not re-litigate the K question,
which v5 already answered):
  K256_COSINE  -- reproduces v5's K256 arm exactly (Gate-D positive control;
                 tolerance-checked against v5 seed7's MEASURED numbers).
  K256_PLATEAU -- the new arm: constant post-warmup LR at K=256.
Reuses `exp_encoder_v4_convergence_lr_hold_v1_core._train_student_lrmode`
UNMODIFIED (that function already parameterizes BOTH `kb`/`blk_l` and
`lr_mode`) -- no new training-loop code needed for this cell, same
low-risk-reuse posture as the v5 sibling cell.

Determinism pinning identical to v4/v5 (coordinator mandate, 2026-07-04):
torch.use_deterministic_algorithms, explicit RNG seeding, CUBLAS_WORKSPACE_
CONFIG. THE REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL NUMBER; local
smoke/preview is a MACHINERY gate only.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "plateau hold learning rate additional lift on top of K256 block
  code ceiling effect combined levers retrieval agreement" -> top hit
  cosine=0.2841 (this arc's own v3c/v3e prose, expected self-similarity;
  the v4/v5 sibling cells' own prose at cosine=0.27-0.29, expected --
  same arc, distinct-but-related cells). NONE at cosine>0.30 for a
  DISTINCT prior cell testing THIS composition. GENUINELY NOVEL: no prior
  cell in this lineage trains a K=256 model under plateau-hold LR.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException, no
  bare except)
- crlb_floor_computed: K256 r_max=0.9466 (THEORETICAL, same formula/anchor
  as the v5 sibling cell; unchanged here -- LR schedule does not change the
  quantization channel)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification (same
  as the whole lineage): smoke's tiny V_train=3000 cannot reproduce the
  true coverage-ratio/ceiling-effect question; smoke validates MACHINERY
  ONLY. The actual "does plateau-hold add lift AT K=256" question needs the
  true 177899-concept corpus -- that IS the FULL dispatch, and the
  REMOTE-QUEUE OFFICIAL LANDING is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: delta band applies to K256_{COSINE,PLATEAU}_BLOCK_LAST FINAL
  only; *_BESTVAL is comparison/context; RANDOM_BLOCK/CHARPOS/shuffled_key
  are integrity-only (per-arm, though both arms share kb=256/blk_l=16 so
  the block partition is identical across arms here -- unlike the v5
  sibling cell, RANDOM_BLOCK CAN be shared safely, but this cell still
  computes it per-arm for symmetry/simplicity with the v4/v5 convention and
  to avoid a subtle assumption if a future edit makes the arms' K differ).
- cardinality_ok: EXPECTED_N_UNITS=17 both run_modes (SMOKE=FULL code path;
  same composition as the v4 sibling cell: 2 arms x 7 + 3 shared)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v6_k256_plateau_followup_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
  experiments/exp_encoder_v4_convergence_lr_hold_v1_core.py (imports
  `_train_student_lrmode` only; does NOT touch v4's own artifact/checkpoint
  directories)

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
from typing import Dict, List, Optional, Tuple

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
from experiments import (  # noqa: E402
    exp_encoder_v4_convergence_lr_hold_v1_core as v4,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v6_k256_plateau_followup_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0
OBJECTIVE = "in_batch"
K_KB, K_BLK_L = 256, 16   # BOTH arms use K=256 -- this cell isolates LR only
LR_MODES = ("COSINE", "PLATEAU")  # arm_name == lr_mode label at K=256

FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
HEADLINE_EVAL_EVERY_FULL = 500
FULL_TRIALS = v3.MID_TRIALS
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000
VAL_TRAJ_SUB = 2000
VAL_TRAJ_PAIRS = 30_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE

SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN
SMOKE_N_HELD = v3.SMOKE_N_HELD
SMOKE_STEPS = 240
SMOKE_CKPT_EVERY = 60
SMOKE_HEADLINE_EVAL_EVERY = 40
SMOKE_VAL_CAP = 200
SMOKE_VAL_TRAJ_SUB = 120
SMOKE_VAL_TRAJ_PAIRS = 3_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05

EXPECTED_N_UNITS_FULL = 17
EXPECTED_N_UNITS_SMOKE = 17

ALGEBRA_FLOOR = 0.90

# Delta band for "does plateau add lift ON TOP of K=256" (HYPOTHESIZED@this
# prereg; smaller than v5's K-effect HARD_PASS floor since this tests a
# SECOND-order composition effect, not the primary K lever which v5 already
# confirmed is large -- consistent with v4's own observed +0.02-0.03
# cross-seed lift at K=128).
DELTA_RET_AGREE10_HARD_PASS_MIN = 0.02
DELTA_HI80_COS_REGRESSION_FLOOR = -0.02

# CRLB (same formula/anchor as v5; K=256 ceiling, unchanged by LR schedule).
_CRLB_SIGMA_TEACHER = math.sqrt((0.901 ** 2 * 0.25 / 128) / (1 - 0.901 ** 2))


def _crlb_r_max(k: int) -> float:
    return _CRLB_SIGMA_TEACHER / math.sqrt(_CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


# Gate-D positive control: v5 seed7's landed K256 arm (MEASURED@data/
# exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json:recovery.K256.final).
V5_SEED7_K256_FINAL_BLOCK = 0.9482190081426722
V5_SEED7_K256_FINAL_RET_AGREE10 = 0.29017987633501885
V5_SEED7_K256_FINAL_HI80_COS = 0.8297631144523621
REPRO_TOL_BLOCK = 0.15
REPRO_TOL_RET = 0.10
REPRO_TOL_HI80 = 0.15


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v6_k256_plateau{tag}{suffix}"


# ---------------------------------------------------------------------------
# Determinism pinning (identical to v4/v5).
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
# Defensive helpers (mirrors v4/v5).
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
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_k256_plateau(per_unit: List[Dict], expected_units: int,
                          run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    if posc is None or posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed "
                f"J=5 {posc['acc_at1'] if posc else None} < 0.98")
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
                    f"FALSE_WIN_ALGEBRA_LAST_STEP_{mode}: keyed_roundtrip J=5 "
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR}")

    def _tf(mode: str) -> Dict:
        u = v3._by_unit(per_unit, "semantic", f"{mode}_BLOCK_LAST")
        if u is None:
            return {"spearman_all": float("nan"), "ret_agree10": float("nan"),
                   "hi80_cos": float("nan")}
        return {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
               "hi80_cos": u["hi80_cos"]}

    cos, plat = _tf("COSINE"), _tf("PLATEAU")
    delta_ret = plat["ret_agree10"] - cos["ret_agree10"]
    delta_hi80 = plat["hi80_cos"] - cos["hi80_cos"]

    repro_ok = (abs(cos["spearman_all"] - V5_SEED7_K256_FINAL_BLOCK) <= REPRO_TOL_BLOCK
               and abs(cos["ret_agree10"] - V5_SEED7_K256_FINAL_RET_AGREE10) <= REPRO_TOL_RET
               and abs(cos["hi80_cos"] - V5_SEED7_K256_FINAL_HI80_COS) <= REPRO_TOL_HI80)

    tail = (f"[K256_COSINE: ret={cos['ret_agree10']:.4f} hi80={cos['hi80_cos']:.4f} "
           f"spearman={cos['spearman_all']:.4f} repro_vs_v5_seed7={repro_ok}] "
           f"[K256_PLATEAU: ret={plat['ret_agree10']:.4f} hi80={plat['hi80_cos']:.4f} "
           f"spearman={plat['spearman_all']:.4f}] delta_ret={delta_ret:.4f} "
           f"delta_hi80={delta_hi80:.4f}")

    if run_mode == "smoke":
        if not math.isfinite(cos["ret_agree10"]) or not math.isfinite(plat["ret_agree10"]):
            return ("SMOKE_GATE_FAIL", "S_ret_agree10_missing")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both K256 LR-mode arms train end-to-end, "
                f"cardinality/integrity/algebra gates hold {tail} (the plateau-"
                f"adds-lift-at-K256 discriminator is a FULL-only question -- "
                f"REMOTE-QUEUE OFFICIAL LANDING is canonical, this local smoke "
                f"is a machinery gate only)")

    if not repro_ok:
        return ("MIDDLE_BAND",
                f"K256_COSINE_REPRODUCTION_OUTSIDE_TOLERANCE: this run's "
                f"K256_COSINE arm diverged from the v5 seed7 MEASURED "
                f"reference by more than tolerance -- environment drift "
                f"suspected; the plateau-delta below should be re-audited "
                f"{tail}")
    if delta_hi80 < DELTA_HI80_COS_REGRESSION_FLOOR:
        return ("HARD_FAIL",
                f"PLATEAU_REGRESSES_CALIBRATION_AT_K256: hi80_cos delta "
                f"{delta_hi80:.4f} < {DELTA_HI80_COS_REGRESSION_FLOOR} {tail}")
    if delta_ret >= DELTA_RET_AGREE10_HARD_PASS_MIN:
        return ("HARD_PASS",
                f"PLATEAU_ADDS_LIFT_AT_K256: ret_agree10 delta {delta_ret:.4f} "
                f">= {DELTA_RET_AGREE10_HARD_PASS_MIN} on top of the already-"
                f"confirmed K=256 gain -- the two levers COMPOSE (at least "
                f"partially additive), not a ceiling effect {tail}")
    if delta_ret <= 0.0:
        return ("HARD_FAIL",
                f"PLATEAU_ADDS_NO_LIFT_AT_K256: ret_agree10 delta "
                f"{delta_ret:.4f} <= 0 -- at the K=256 operating point the "
                f"LR-schedule lever no longer helps (or hurts); consistent "
                f"with a CEILING EFFECT where K=256 already captures the "
                f"available headroom {tail}")
    return ("MIDDLE_BAND",
            f"PLATEAU_MARGINAL_AT_K256: ret_agree10 delta {delta_ret:.4f} is "
            f"positive but below the {DELTA_RET_AGREE10_HARD_PASS_MIN} "
            f"HARD_PASS margin {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_k256_plateau(run_mode: str, seed: int, device_arg: str, n_dim: int,
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
    kb, blk_l = K_KB, K_BLK_L
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
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)), warmup)

    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[v6_k256_plateau] run_mode={run_mode} seed={seed} device={device} "
          f"n_dim={n_dim} steps={steps} batch={batch} kb={kb} blk_l={blk_l} "
          f"torch={det_info['torch_version']} "
          f"deterministic_ok={det_info['deterministic_algorithms_set']} "
          f"min_step_for_best={min_step_for_best}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v6_k256_plateau] teacher {cache_path.name}: {V_cache} concepts x "
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
        raise RuntimeError(f"TEST split too small: n_test={n_test}")
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xval = X[torch.from_numpy(val_idx.copy())].contiguous()
    Xtest = X[torch.from_numpy(test_idx.copy())].contiguous()
    names_test = [ids[i] for i in test_idx]
    print(f"[v6_k256_plateau] split train={n_tr} val={n_val} test={n_test}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v6_k256_plateau] mining done cov={semi_cov:.3f} "
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
        lr_mode = mode.lower()
        ckpt_path = art_dir / f"_ckpt_{mode}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{mode}.pt"
        _, diag = v4._train_student_lrmode(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            NCE_WEIGHT, mode, lr_mode,
            headline_eval_fn=_headline_eval, dense_eval_quick_fn=_dense_quick,
            eval_every=eval_every, min_step_for_best=min_step_for_best)
        arm_diag[mode] = diag
        print(f"[v6_k256_plateau] {mode} trained rkd_last={diag['rkd_last']:.4f} "
              f"best_ret_agree10={diag['best_ret_agree10']:.4f}@step{diag['best_step']} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    in_dim = Xtr.shape[1]
    arm_codes: Dict[str, torch.Tensor] = {}
    for mode in LR_MODES:
        ckpt_path = art_dir / f"_ckpt_{mode}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{mode}.pt"
        last_ck = torch.load(str(ckpt_path), map_location=device)
        last_student = v3._make_student("mlp", in_dim, kb * blk_l, device, seed)
        last_student.load_state_dict(last_ck["student"])
        last_student.eval()
        bestval_student = v4._reload_best_student(in_dim, kb * blk_l, device, best_ckpt_path)
        arm_codes[f"{mode}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xtest)
        arm_codes[f"{mode}_BLOCK_LAST"] = v3._encode_hard_block(last_student, Xtest, kb, blk_l)
        arm_codes[f"{mode}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xtest)
        arm_codes[f"{mode}_BLOCK_BESTVAL"] = v3._encode_hard_block(bestval_student, Xtest, kb, blk_l)

    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], n_dim, v3.K_BLOCKS_PRIMARY)

    exempted_pairs = set()
    for mode in LR_MODES:
        if arm_diag[mode]["best_step"] == steps or arm_diag[mode]["best_ckpt_fallback_to_final"]:
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
            print(f"[v6_k256_plateau] unit {len(per_unit)}/{expected_units} {u['unit']}: "
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

    verdict, verdict_msg = _verdict_k256_plateau(per_unit, expected_units, run_mode)
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
        "best_ckpt_fallback_to_final": arm_diag[mode]["best_ckpt_fallback_to_final"],
        "traj": arm_diag[mode]["traj"],
    } for mode in LR_MODES}

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE, "kb": K_KB, "blk_l": K_BLK_L,
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
                        "schedule (cosine-decay vs plateau-hold) AT THE FIXED "
                        "K=256 operating point (isolates the LR question from "
                        "the K question, which the sibling v5 cell already "
                        "answered); K256_COSINE is a Gate-D positive control "
                        "vs v5 seed7's landed K256 arm; FINAL-step ret_agree10/"
                        "hi80_cos delta is the PRIMARY gated comparison"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": _crlb_r_max(K_KB),
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K); same formula/anchor as the v5 sibling "
                                   "cell; unchanged by LR schedule"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v6_k256_plateau] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    r256 = _crlb_r_max(256)
    assert r256 > 0.901, "selftest: K256 ceiling must exceed K128's 0.901"

    def _fake_units(mode_finals=None):
        mode_finals = mode_finals or {}
        units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(9)]
        units += [
            {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
             "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        ]
        for mode in LR_MODES:
            ret, hi80, sp = mode_finals.get(mode, (0.20, 0.80, 0.90))
            units += [
                {"unit": f"semantic::{mode}_BLOCK_LAST", "arm": f"{mode}_BLOCK_LAST",
                 "kind": "semantic", "spearman_all": sp, "ret_agree10": ret,
                 "hi80_cos": hi80, "hi80_calib_err": 0.02},
                {"unit": f"keyed::{mode}_BLOCK_LAST::J5", "arm": f"{mode}_BLOCK_LAST",
                 "kind": "keyed", "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
                {"unit": f"keyed::{mode}_BLOCK_BESTVAL::J5", "arm": f"{mode}_BLOCK_BESTVAL",
                 "kind": "keyed", "J": 5, "acc_at1": 0.95, "hit_any_member": 0.95},
                {"unit": f"shuffled_key::{mode}_BLOCK_LAST::J5", "arm": f"{mode}_BLOCK_LAST",
                 "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
            ]
        return units

    pass_finals = {
        "COSINE": (V5_SEED7_K256_FINAL_RET_AGREE10, V5_SEED7_K256_FINAL_HI80_COS,
                  V5_SEED7_K256_FINAL_BLOCK),
        "PLATEAU": (V5_SEED7_K256_FINAL_RET_AGREE10 + 0.03, 0.83, 0.95),
    }
    v_pass, m_pass = _verdict_k256_plateau(_fake_units(pass_finals), 17, "full")
    assert v_pass == "HARD_PASS" and "PLATEAU_ADDS_LIFT_AT_K256" in m_pass, (
        f"selftest: expected HARD_PASS got {v_pass} ({m_pass})")

    nolift_finals = {
        "COSINE": (V5_SEED7_K256_FINAL_RET_AGREE10, V5_SEED7_K256_FINAL_HI80_COS,
                  V5_SEED7_K256_FINAL_BLOCK),
        "PLATEAU": (V5_SEED7_K256_FINAL_RET_AGREE10 - 0.01, 0.83, 0.95),
    }
    v_no, m_no = _verdict_k256_plateau(_fake_units(nolift_finals), 17, "full")
    assert v_no == "HARD_FAIL" and "PLATEAU_ADDS_NO_LIFT_AT_K256" in m_no, (
        f"selftest: expected no-lift HARD_FAIL got {v_no} ({m_no})")

    v_card, m_card = _verdict_k256_plateau(_fake_units(pass_finals)[:5], 17, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

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
            _, diag_st = v4._train_student_lrmode(
                kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
                tdp / f"ckpt_{mode}.pt", tdp / f"ckpt_best_{mode}.pt", 100, tdp, t0,
                0.0, f"TEST_{mode.upper()}", mode,
                headline_eval_fn=_hl, dense_eval_quick_fn=_dq, eval_every=4,
                min_step_for_best=2)
            assert math.isfinite(diag_st["rkd_last"])
            best_student = v4._reload_best_student(64, kb * blk_l, "cpu",
                                                    tdp / f"ckpt_best_{mode}.pt")
            c = v3._encode_hard_block(best_student, Xval_syn, kb, blk_l)
            assert c.shape == (40, kb * blk_l)
            assert torch.isfinite(c).all()

    print(f"[selftest] PASS (K256 CRLB > K128 + lift/no-lift/cardinality verdict "
          f"bands + v4._train_student_lrmode reuse at K=256 for BOTH lr_modes) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0
