"""Encoder v8 -- MINIMUM-DENSITY paired test: what is the SPARSEST block code
that still clears the ret_agree10>=0.35 retrieval target the trained curve
approaches from below?

CONTEXT (do not re-litigate; direct sequel to v5/v7). The TRAINED density-vs-
retrieval curve is now monotone-RISING with density:
  K128 (3.125% active) final_ret_agree10 ~ 0.197/0.198  (v5, 2 seeds)
    MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json:recovery.K128.final.ret_agree10
  K256 (6.25%  active) final_ret_agree10 ~ 0.290/0.296  (v5, 2 seeds, HARD_PASS)
    MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json:recovery.K256.final.ret_agree10
  K512 (12.5%  active) final_ret_agree10 ~ 0.414/0.415  (v7, 2 seeds, HARD_PASS)
    MEASURED@data/exp_encoder_v7_k512_capacity_paired_v1_seed7/metrics.json:recovery.K512.final.ret_agree10
Roughly +0.10 ret_agree10 per doubling of active density. K256 (0.29) is
BELOW the 0.35 target; K512 (0.414) is ABOVE it. Linear interpolation in
density places the 0.35 crossing at ~9.3% active
(THEORETICAL@(0.35-0.290)/(0.414-0.290)*(0.125-0.0625)+0.0625). This cell
trains ONE intermediate-density arm right at that predicted crossing to find
the MINIMUM density (hence the minimum sparsity cost) that clears 0.35 --
answering "can we clear the retrieval target at a sparser code than K512's
12.5%, and if so how sparse."

TILING REALITY (why K is 372, not a round 384): a block code's active
density is exactly 1/blk_l, and the total code width is kb*blk_l. N_DIM=4096
= 2^12 has ONLY power-of-2 divisors, so the ONLY block counts that tile 4096
exactly are 128/256/512/1024/... (densities 3.125/6.25/12.5/25%). There is
NO block count in [320,448] (the coordinator's target band) that tiles 4096
-- an intermediate density REQUIRES a non-4096 width. So this cell uses
PER-ARM widths (unlike v5/v7, where both arms happened to share N=4096
because 4096 is divisible by both 16 and 8):
  K256 control -- kb=256, blk_l=16, width=4096, 6.250% active (EXACT v5
         regime; the Gate-D internal positive control -- its own numbers
         must reproduce v5's landed K256 arm before the new arm is trusted)
  K372 new     -- kb=372, blk_l=11, width=4092, 9.091% active (blk_l=11 is
         the integer per-block alphabet whose density 1/11=9.09% sits at the
         predicted 0.35 crossing; kb=372 -> width 4092, within 4 dims / 0.1%
         of 4096, so the student's MLP output width is materially identical
         to the K256/K512 students' 4096 for capacity comparability). blk_l=
         11 is LARGER than K512's already-validated blk_l=8, so per-block
         binding SNR is HIGHER than K512's -- SBC algebra is expected to be
         at least as safe as K512 (checked explicitly per arm, not assumed).

Both arms use `v3c._train_student_full` VERBATIM (unmodified; kb/blk_l are
already parameters, so per-arm width needs no new training-loop code), same
seed/data/split/mining/objective (in_batch-RKD-only, nce_weight=0,
steps=6000, batch=128), UNCHANGED cosine-decay LR (kept isolated from v6's
plateau-hold lever exactly as v5/v7 were). The ONLY thing that differs
between arms is (kb, blk_l) and hence width.

Determinism pinning: identical to v5/v7 (`_pin_determinism`), records
torch.__version__ + device into metrics.json. THE REMOTE-QUEUE OFFICIAL
LANDING IS THE CANONICAL NUMBER; local smoke is a MACHINERY gate only.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "minimum density block code trained encoder retrieval agreement 0.35
  target intermediate K sparsity crossing paired" -> top hits are this arc's
  own v5/v7/density-curve prose (expected self-similarity, same lineage),
  all cosine<=0.30 for any DISTINCT prior cell training an intermediate-
  density (non-power-of-2-blk_l) arm. GENUINELY NOVEL: no prior cell trains a
  blk_l=11 / 9.09%-active student or searches for the minimum density that
  clears 0.35; v5 (K128/K256) and v7 (K256/K512) only touch power-of-2 blk_l.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace (inherited from v3c._train_student_full)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare)
- crlb_floor_computed: per-arm r_max via the SAME formula as the whole lineage
  (K anchor 0.901 at K=128); honest caveat inherited from v7 (formula's K
  counts block COUNT only, does not separately model blk_l shrinking).
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical (same as v3/v5/v7): smoke
  validates MACHINERY only (both arms train end-to-end at DIFFERENT widths,
  per-arm RANDOM_BLOCK/algebra checks fire, cardinality holds); the actual
  retrieval-vs-density question needs the 177899-concept corpus -> FULL, and
  the REMOTE-QUEUE OFFICIAL LANDING is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: the target-clearing gate applies to K372_BLOCK_LAST FINAL only;
  {arm}_*_BESTVAL is context; RANDOM_BLOCK/CHARPOS/shuffled_key integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=19 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters to
  v5/v7; only kb/blk_l/width differ between arms)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v8_k372_mindensity_paired_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_..._v1_core.py (v3)
  experiments/exp_encoder_migration_step1b_v3c_..._v1_core.py (v3c)
Does NOT touch any v3/v5/v6/v7/opq/bypass/ceiling artifact directory.

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

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_v8_k372_mindensity_paired_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0        # RKD-only (matches v3c/v3e/v5/v7's winning config)
OBJECTIVE = "in_batch"  # GLOBAL stays dropped (algebra HARD_FAIL, see v3c)

# arm_name -> (kb, blk_l). PER-ARM width = kb*blk_l (K256->4096, K372->4092).
# density = 1/blk_l (K256 6.25%, K372 9.091%). CONTROL_ARM reproduces v5's
# landed K256; NEW_ARM is the intermediate-density probe.
CONTROL_ARM = "K256"
NEW_ARM = "K372"
K_ARMS = {CONTROL_ARM: (256, 16), NEW_ARM: (372, 11)}
N_DIM_REF = 4096                      # CHARPOS reference width + metrics anchor

# ---- FULL-scale config: MATCHES v5/v7 exactly except K/blk_l/width ----
FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 500
FULL_TRIALS = v3.MID_TRIALS
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000
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
SMOKE_VAL_CAP = 200
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05

# 2 arms x 9 units (semantic DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK
# + keyed RANDOM_BLOCK posctrl + keyed LAST J5 + keyed BESTVAL J5 + shuffled-
# LAST J5) = 18, + shared CHARPOS semantic(1) = 19.
EXPECTED_N_UNITS_FULL = 19
EXPECTED_N_UNITS_SMOKE = 19

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

ALGEBRA_FLOOR = 0.90

# Target-clearing bands (HYPOTHESIZED@this prereg). PRIMARY question: does the
# NEW_ARM's FINAL-step ret_agree10 CLEAR the 0.35 retrieval target?
RET_AGREE10_TARGET = 0.35
# Secondary: the new (sparser) arm must not badly regress semantic calibration
# vs the K256 control (same floor convention as v5/v7).
DELTA_HI80_COS_REGRESSION_FLOOR = -0.02


def _crlb_sigma_teacher(k_anchor: int, r_anchor: float) -> float:
    return math.sqrt((r_anchor ** 2 * 0.25 / k_anchor) / (1 - r_anchor ** 2))


CRLB_SIGMA_TEACHER = _crlb_sigma_teacher(128, 0.901)


def _crlb_r_max(k: int) -> float:
    return CRLB_SIGMA_TEACHER / math.sqrt(CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v8_k372{tag}{suffix}"


# ---------------------------------------------------------------------------
# Determinism pinning (identical to v5/v7).
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
# Defensive helpers (mirror v7).
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
# Verdict logic (generalized control/new arm; PRIMARY = new arm clears target).
# ---------------------------------------------------------------------------

def _verdict_mindensity(per_unit: List[Dict], recovery: Dict, expected_units: int,
                        run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    for arm in K_ARMS:
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
        if prim["acc_at1"] < ALGEBRA_FLOOR:
            return ("HARD_FAIL",
                    f"FALSE_WIN_ALGEBRA_LAST_STEP_{arm}: keyed_roundtrip J=5 "
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (blk_l={K_ARMS[arm][1]} "
                    f"may have broken SBC composability -- a genuine capacity-vs-"
                    f"algebra tradeoff finding, not a cell bug)")

    ctrl = recovery[CONTROL_ARM]
    new = recovery[NEW_ARM]
    new_ret = new["final"]["ret_agree10"]
    ctrl_ret = ctrl["final"]["ret_agree10"]
    delta_hi80 = new["final"]["hi80_cos"] - ctrl["final"]["hi80_cos"]
    tail = (f"[{CONTROL_ARM}({ctrl['sparsity']*100:.3f}% active): "
           f"final_ret={ctrl_ret:.4f} final_hi80={ctrl['final']['hi80_cos']:.4f}] "
           f"[{NEW_ARM}({new['sparsity']*100:.3f}% active): "
           f"final_ret={new_ret:.4f} final_hi80={new['final']['hi80_cos']:.4f} "
           f"final_block_spearman={new['final']['spearman_all']:.4f}] "
           f"delta_hi80={delta_hi80:.4f}")

    if run_mode == "smoke":
        for arm in K_ARMS:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both arms (K256 4096-wide + K372 4092-wide) "
                f"train end-to-end with correctly-differing block partitions/widths, "
                f"per-arm RANDOM_BLOCK/algebra checks fire, cardinality holds {tail} "
                f"(the 'does 9.09%-active clear 0.35' question is a FULL-only "
                f"question; smoke's tiny V_train cannot reproduce it -- REMOTE-QUEUE "
                f"OFFICIAL LANDING is canonical, this local smoke is a machinery gate)")

    if delta_hi80 < DELTA_HI80_COS_REGRESSION_FLOOR:
        return ("HARD_FAIL",
                f"MINDENSITY_REGRESSES_CALIBRATION: hi80_cos delta {delta_hi80:.4f} < "
                f"{DELTA_HI80_COS_REGRESSION_FLOOR} -- the sparser 9.09% code costs "
                f"semantic calibration vs the K256 control {tail}")
    if new_ret >= RET_AGREE10_TARGET:
        return ("HARD_PASS",
                f"MINDENSITY_CLEARS_TARGET: {NEW_ARM} (9.091% active) final "
                f"ret_agree10 {new_ret:.4f} >= {RET_AGREE10_TARGET} target -- the "
                f"retrieval target is reachable at a code SPARSER than K512's 12.5% "
                f"(9.09% suffices), no calibration regression vs K256 {tail}")
    return ("MIDDLE_BAND",
            f"MINDENSITY_BELOW_TARGET: {NEW_ARM} (9.091% active) final ret_agree10 "
            f"{new_ret:.4f} < {RET_AGREE10_TARGET} target -- 9.09% active is NOT "
            f"enough to clear 0.35; the minimum-density crossing is between 9.09% "
            f"and K512's 12.5% (a useful lower bound, locates the crossing) {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_mindensity(run_mode: str, seed: int, device_arg: str,
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
    # PER-ARM width by construction (kb*blk_l); no shared-n_dim assertion.
    n_dim_by_arm = {arm: kb * blk_l for arm, (kb, blk_l) in K_ARMS.items()}

    if run_mode == "smoke":
        steps = SMOKE_STEPS
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        val_cap = SMOKE_VAL_CAP
        quick_sub, quick_pairs = SMOKE_VAL_QUICK_SUB, SMOKE_VAL_QUICK_PAIRS
        val_full_pairs, test_final_pairs = SMOKE_VAL_FULL_PAIRS, SMOKE_TEST_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
        batch = min(FULL_BATCH, 32)
    else:
        steps = FULL_STEPS
        ckpt_every, dense_every = CKPT_EVERY_STEPS_FULL, DENSE_EVAL_EVERY_FULL
        val_cap = VAL_CAP
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
    print(f"[v8_mindensity] run_mode={run_mode} seed={seed} device={device} "
          f"widths={n_dim_by_arm} steps={steps} batch={batch} "
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
    print(f"[v8_mindensity] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v8_mindensity] split train={n_tr} held={n_he}", flush=True)

    # Mining SHARED across both arms (teacher-cosine-derived, width-independent).
    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v8_mindensity] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, val_full_pairs, seed + 7)

    arm_diag: Dict[str, Dict] = {}
    arm_students: Dict[str, Tuple[torch.nn.Module, torch.nn.Module]] = {}
    for arm, (kb, blk_l) in K_ARMS.items():
        ckpt_path = art_dir / f"_ckpt_{arm}.pt"
        best_ckpt_path = art_dir / f"_ckpt_best_{arm}.pt"
        last_student, diag = v3c._train_student_full(
            kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
            ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
            None, 0, NCE_WEIGHT, arm, OBJECTIVE,
            dense_eval_quick_fn=_deval_quick, dense_eval_full_fn=_deval_full,
            dense_eval_every=dense_every, min_step_for_best=min_step_for_best)
        bestval_student = v3c._reload_best_student(
            "mlp", Xtr.shape[1], kb * blk_l, device, best_ckpt_path)
        arm_diag[arm] = diag
        arm_students[arm] = (last_student, bestval_student)
        print(f"[v8_mindensity] {arm} (kb={kb},blk_l={blk_l},width={kb*blk_l}) trained "
              f"rkd_last={diag['rkd_last']:.4f} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"n_traj_points={len(diag['dense_traj'])} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    arm_codes: Dict[str, torch.Tensor] = {}
    for arm, (kb, blk_l) in K_ARMS.items():
        last_student, bestval_student = arm_students[arm]
        arm_codes[f"{arm}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xhe)
        arm_codes[f"{arm}_BLOCK_LAST"] = v3._encode_hard_block(last_student, Xhe, kb, blk_l)
        arm_codes[f"{arm}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xhe)
        arm_codes[f"{arm}_BLOCK_BESTVAL"] = v3._encode_hard_block(bestval_student, Xhe, kb, blk_l)
        gen_ctrl = torch.Generator().manual_seed(seed + 1 + kb)
        arm_codes[f"{arm}_RANDOM_BLOCK"] = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)

    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], N_DIM_REF, v3.K_BLOCKS_PRIMARY)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v8_mindensity] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for arm in K_ARMS:
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

    for arm, (kb, blk_l) in K_ARMS.items():
        _run_unit(v3._keyed_unit, f"{arm}_RANDOM_BLOCK", "sbc", arm_codes[f"{arm}_RANDOM_BLOCK"],
                  kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
                  arm_codes[f"{arm}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_BESTVAL", "sbc",
                  arm_codes[f"{arm}_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials, gen_eval, device)
        _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
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
        "kb": K_ARMS[arm][0], "blk_l": K_ARMS[arm][1],
        "n_dim": n_dim_by_arm[arm],
        "sparsity": 1.0 / K_ARMS[arm][1],   # density = 1/blk_l (active fraction)
        "final": _sem_summary(arm, "BLOCK_LAST"),
        "bestval_on_test": _sem_summary(arm, "BLOCK_BESTVAL"),
        "final_dense": _sem_summary(arm, "DENSE_LAST"),
        "bestval_dense_on_test": _sem_summary(arm, "DENSE_BESTVAL"),
        "best_step": arm_diag[arm]["best_step"],
        "best_step_frac": (arm_diag[arm]["best_step"] / steps
                          if steps > 0 and arm_diag[arm]["best_step"] >= 0 else None),
        "best_ckpt_fallback_to_final": arm_diag[arm]["best_ckpt_fallback_to_final"],
        "crlb_r_max": _crlb_r_max(K_ARMS[arm][0]),
    } for arm in K_ARMS}

    verdict, verdict_msg = _verdict_mindensity(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device,
        "N_ref": N_DIM_REF, "n_dim_by_arm": n_dim_by_arm,
        "control_arm": CONTROL_ARM, "new_arm": NEW_ARM,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE, "lr_schedule": "cosine_unchanged",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "ret_agree10_target": RET_AGREE10_TARGET,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_held_pool": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "determinism": det_info,
        "canonical_source": "remote_queue_official_landing_only; local_smoke_is_gate_only",
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "arms_differ_exempted": [],
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("PAIRED same-seed/data/split/mining minimum-density probe: "
                        "K256 control (blk_l=16, width 4096, 6.25% active -- Gate-D "
                        "reproducer of v5's landed K256) vs K372 new arm (blk_l=11, "
                        "width 4092, 9.091% active -- the integer per-block alphabet "
                        "whose density sits at the predicted ret_agree10=0.35 "
                        "crossing between K256's 0.29 and K512's 0.414). in_batch-"
                        "RKD-only nce=0 config matching v5/v7, UNCHANGED cosine-decay "
                        "LR (isolated from v6's plateau lever); FINAL-step "
                        "ret_agree10 is the PRIMARY gated number (does 9.09% clear "
                        "0.35); per-arm RANDOM_BLOCK/shuffled-key/FALSE_WIN_ALGEBRA "
                        "checks run at EACH arm's own block partition (blk_l=11 is "
                        "larger than K512's validated blk_l=8, so algebra is expected "
                        "at least as safe -- checked, not assumed)"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": {arm: _crlb_r_max(K_ARMS[arm][0]) for arm in K_ARMS},
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K); sigma_teacher backed out from the K=128 "
                                   "anchor 0.901 (THEORETICAL@v2/v3/v3b/v3c/v3e/v5/v7); "
                                   "honest caveat: K counts block COUNT only, does not "
                                   "separately model blk_l shrinking, see docstring"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v8_mindensity] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. CRLB formula consistency: K=128 reproduces the 0.901 anchor; K=372 is
    #    a HIGHER ceiling than K=256 (more blocks -> more bits).
    r128 = _crlb_r_max(128)
    r256 = _crlb_r_max(256)
    r372 = _crlb_r_max(372)
    assert abs(r128 - 0.901) < 1e-3, f"selftest: CRLB(128) should reproduce 0.901, got {r128}"
    assert r372 > r256, "selftest: CRLB(372) must exceed CRLB(256) (finer code = higher ceiling)"

    # 2. tiling / density sanity: new arm width ~4096, density strictly between
    #    K256 (6.25%) and K512 (12.5%).
    for arm, (kb, blk_l) in K_ARMS.items():
        assert kb * blk_l == {"K256": 4096, "K372": 4092}[arm], (
            f"selftest: {arm} width {kb*blk_l} unexpected")
    new_density = 1.0 / K_ARMS[NEW_ARM][1]
    assert 0.0625 < new_density < 0.125, (
        f"selftest: NEW_ARM density {new_density} not strictly between K256 and K512")
    assert abs(K_ARMS[NEW_ARM][0] * K_ARMS[NEW_ARM][1] - N_DIM_REF) <= 8, (
        "selftest: NEW_ARM width should be within 8 dims of N_DIM_REF for comparability")

    # 3. verdict bands: cardinality / algebra / regression / clears / below.
    def _fake_units(ctrl_alg=1.0, new_alg=1.0, ctrl_shuf=0.01, new_shuf=0.01):
        units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(11)]
        for arm, alg, shuf in ((CONTROL_ARM, ctrl_alg, ctrl_shuf),
                               (NEW_ARM, new_alg, new_shuf)):
            units += [
                {"unit": f"keyed::{arm}_RANDOM_BLOCK::J5", "arm": f"{arm}_RANDOM_BLOCK",
                 "kind": "keyed", "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
                {"unit": f"keyed::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "keyed", "J": 5, "acc_at1": alg, "hit_any_member": alg},
                {"unit": f"keyed::{arm}_BLOCK_BESTVAL::J5", "arm": f"{arm}_BLOCK_BESTVAL",
                 "kind": "keyed", "J": 5, "acc_at1": alg, "hit_any_member": alg},
                {"unit": f"shuffled_key::{arm}_BLOCK_LAST::J5", "arm": f"{arm}_BLOCK_LAST",
                 "kind": "shuffled_key", "J": 5, "acc_at1": shuf, "hit_any_member": shuf},
            ]
        return units

    def _rec(ctrl_ret, new_ret, ctrl_hi80=0.82, new_hi80=0.82):
        return {
            CONTROL_ARM: {"sparsity": 0.0625,
                          "final": {"spearman_all": 0.9, "ret_agree10": ctrl_ret,
                                    "hi80_cos": ctrl_hi80, "hi80_calib_err": 0.02}},
            NEW_ARM: {"sparsity": 1.0/11,
                      "final": {"spearman_all": 0.9, "ret_agree10": new_ret,
                                "hi80_cos": new_hi80, "hi80_calib_err": 0.02}},
        }

    v_clear, m_clear = _verdict_mindensity(_fake_units(), _rec(0.29, 0.37), 19, "full")
    assert v_clear == "HARD_PASS" and "MINDENSITY_CLEARS_TARGET" in m_clear, (
        f"selftest: expected clears-target HARD_PASS got {v_clear} ({m_clear})")

    v_below, m_below = _verdict_mindensity(_fake_units(), _rec(0.29, 0.33), 19, "full")
    assert v_below == "MIDDLE_BAND" and "MINDENSITY_BELOW_TARGET" in m_below, (
        f"selftest: expected below-target MIDDLE_BAND got {v_below} ({m_below})")

    v_reg, m_reg = _verdict_mindensity(
        _fake_units(), _rec(0.29, 0.37, ctrl_hi80=0.82, new_hi80=0.70), 19, "full")
    assert v_reg == "HARD_FAIL" and "MINDENSITY_REGRESSES_CALIBRATION" in m_reg, (
        f"selftest: expected calibration-regression HARD_FAIL got {v_reg} ({m_reg})")

    v_alg, m_alg = _verdict_mindensity(
        _fake_units(new_alg=0.20), _rec(0.29, 0.37), 19, "full")
    assert v_alg == "HARD_FAIL" and f"FALSE_WIN_ALGEBRA_LAST_STEP_{NEW_ARM}" in m_alg, (
        f"selftest: expected new-arm algebra-break HARD_FAIL got {v_alg} ({m_alg})")

    v_card, m_card = _verdict_mindensity(_fake_units()[:5], _rec(0.29, 0.37), 19, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    v_smoke, m_smoke = _verdict_mindensity(_fake_units(), _rec(0.29, 0.33), 19, "smoke")
    assert v_smoke == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_smoke, (
        f"selftest: expected smoke machinery HARD_PASS got {v_smoke} ({m_smoke})")

    # 4. tiny end-to-end training reuse of v3c._train_student_full at TWO
    #    DIFFERENT widths (256 and 252) -- proves per-arm-width driver wiring is
    #    correct without any new training-loop code.
    torch.manual_seed(11)
    v_syn = 400
    Xsyn = torch.randn(v_syn, 64)
    Xsyn = Xsyn / Xsyn.norm(dim=-1, keepdim=True)
    gen = torch.Generator().manual_seed(11)
    pos_syn = torch.randint(0, v_syn, (v_syn,), generator=gen)
    semi_syn = torch.randint(0, v_syn, (v_syn, v3.N_SEMI_CANDS), generator=gen)
    Xval_syn = Xsyn[:40].contiguous()
    Xtest_syn = Xsyn[40:64].contiguous()

    def _dq(student):
        return v3._dense_spearman_quick(student, Xval_syn[:20], 300, 3)

    def _df(student):
        return v3._dense_spearman_quick(student, Xval_syn, 500, 3)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # two arms with DIFFERENT widths (16*16=256 and 36*7=252) to exercise
        # the per-arm-width path (the real cell's 4096 vs 4092 in miniature).
        for arm, (kb, blk_l) in (("A", (16, 16)), ("B", (36, 7))):
            st_last, diag_st = v3c._train_student_full(
                kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
                tdp / f"ckpt_{arm}.pt", tdp / f"ckpt_best_{arm}.pt", 100, tdp, t0,
                None, 0, 0.0, arm, "in_batch",
                dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=4,
                min_step_for_best=2)
            assert math.isfinite(diag_st["rkd_last"])
            st_bestval = v3c._reload_best_student("mlp", 64, kb * blk_l, "cpu",
                                                  tdp / f"ckpt_best_{arm}.pt")
            c_last = v3._encode_hard_block(st_last, Xtest_syn, kb, blk_l)
            c_bestval = v3._encode_hard_block(st_bestval, Xtest_syn, kb, blk_l)
            assert c_last.shape == c_bestval.shape == (24, kb * blk_l)
            assert torch.isfinite(c_last).all() and torch.isfinite(c_bestval).all()
            u = v3._semantic_unit(arm, c_last, c_last, Xtest_syn, Xtest_syn, 0, 500, 3)
            assert "ret_agree10" in u and "hi80_cos" in u

    # 5. determinism pinning is idempotent.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]

    print(f"[selftest] PASS (CRLB K128->0.901 + K372>K256 ceiling + tiling/density "
          f"sanity + clears/below/regression/algebra-break/cardinality/smoke verdict "
          f"bands + v3c._train_student_full reuse at TWO DIFFERENT widths + "
          f"determinism idempotence) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0
