"""Encoder v3e -- DECLINE-vs-PLATEAU diagnostic for in_batch-RKD-only
(NCE off), at v3c's config but run LONGER with finer trajectory logging.

COORDINATOR REDIRECT (2026-07-04, supersedes this agent's prior "confirm
0.89 robustness" cell -- exp_encoder_v3d_inbatch_robustness_confirmation_v1
-- CANCELLED by a Skunkworks VET verdict before it was smoke-tested or
committed): the VET REFUTED v3c's 0.89 headline. Grounds (VERIFIED@this
session, direct metrics.json reads):
  (a) best-ckpt INFLATION -- seed_7's in_batch DENSE trajectory declines from
      its post-floor peak (0.876@step450) to 0.759@step1800 (FINAL), a ~13%
      drop; v3c's OWN peak-then-decline flag is structurally miscalibrated
      (it counts the untrained-network step-0 spike, ~0.956, as "the peak,"
      so its HARD_PASS branch requiring "not peak_decline" is unreachable by
      construction for ANY arm in this lineage -- both GLOBAL and INBATCH
      show peak_step=0 in both seed_7 and seed_13).
  (b) NOT REPRODUCIBLE at the SAME nominal config: v3b's NCE_ZERO (global,
      batch=128, steps=1800) landed FINAL DENSE=0.7336
      MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_
      recovery_diagnostic_v1/metrics.json vs v3c's independent re-run at the
      same nominal config landing FINAL DENSE=0.6514 (GLOBAL arm) -- an 11%
      gap under supposedly identical hyperparameters.
  (c) CONFOUNDED trajectory: the v2->v3c improvement (0.368->0.89) moved
      steps (40000->1800), batch, AND best-of-13-checkpoints selection
      simultaneously; in_batch is ALREADY declining within the 1800-step
      budget, so "recovery" cannot be cleanly attributed to the NCE-removal
      alone without first knowing whether it keeps declining given more steps.
  (d) WRONG METRIC for the actual 0.85 goal: v3c's per_unit gate metric is
      Spearman rank-correlation over 400k mostly-RANDOM held pairs (most
      random concept pairs have near-zero teacher cosine -- a rank
      correlation over a mostly-uninformative-pair sample is not the same
      question as "is a genuinely similar pair's code-cosine close to its
      teacher-cosine", which is what the 0.85 target is actually about).
      ret_agree10 (retrieval-agreement@10, the closer analog) swings
      0.15-0.67 across seed_7/seed_13's own arms -- unstable, and was never
      surfaced as a headline number.
GLOBAL (landmark) stays DROPPED (already independently confirmed broken --
keyed_roundtrip J=5 = 0.133/0.317 << 0.90 in both v3c seeds).

THIS CELL answers the honest next question directly (VET-specified): does
in_batch-RKD-only PLATEAU at a usable level given a LONGER training budget,
or does it keep DECLINING toward v2's 0.368 collapse floor? This decides
whether removing NCE genuinely FIXES the in_batch objective or merely SLOWS
its collapse (a temporary reprieve, not a fix).

Design changes vs the (cancelled, never-dispatched) v3d cell this reuses
machinery from:
  - STEPS: 6000 (was 1800) -- the VET's requested 4000-6000 range, upper end
    chosen to maximize the chance of observing genuine asymptotic behavior.
  - DENSE_EVAL_EVERY: 50 (was 150) -- ~120 trajectory points over the run
    (vs v3c's 13), enough for a real slope/trend estimate, not just
    peak-vs-final anecdote.
  - FINAL-step numbers are ALWAYS reported (inherited from v3d: LAST-step
    requires no selection, so it is never a cherry-picked artifact) --
    alongside best-by-VAL-on-TEST as SECONDARY context, never as the sole
    number, per VET's explicit instruction.
  - HEADLINE METRICS PROMOTED (VET's explicit ask -- "not buried per_unit
    fields"): ret_agree10 AND a cosine-to-gold metric are top-level fields,
    co-equal with (and reported ALONGSIDE, not instead of) the Spearman
    number this lineage has used so far. The cosine-to-gold metric reuses
    v3's existing `_semantic_unit` hi80_cos/hi80_teacher_mean/hi80_calib_err
    fields (mean code-pair cosine restricted to pairs whose TEACHER cosine
    is itself >= 0.80 -- i.e. "genuinely gold-similar pairs", exactly the
    regime the 0.85 target is stated in) -- these already existed in every
    prior cell in this lineage but were never promoted out of per_unit.
  - TREND-SLOPE verdict (new): a linear fit of dense_full vs step over all
    post-anti-gaming-floor eval points, plus an early-half-vs-late-half mean
    comparison, decides PLATEAU_CONFIRMED / DECLINE_CONTINUES / AMBIGUOUS.
    Mapped to the pipeline's canonical verdict enum as
    HARD_PASS/HARD_FAIL/MIDDLE_BAND respectively (verdict_msg carries the
    real semantic label).
  - Algebra suite SIMPLIFIED back to v3c's original single-J=5 convention
    (keyed + shuffled-key only; the 6-point J-grid from the cancelled v3d
    design is dropped for THIS cell -- not what VET asked for, and keeping
    per-run cost down matters more now that steps are 3.3x longer). Full
    J-grid work is deferred to a follow-up if this diagnostic's headline
    result warrants deeper algebra characterization.
  - 3-way split (train/val/test, TEST never used for checkpoint selection)
    KEPT from v3d -- still the correct methodology fix for the
    best-ckpt-doubles-as-reported-number leakage class, orthogonal to and
    still valuable alongside the plateau-vs-decline question.

TWO SEEDS (7, 13 -- matching the original v3c seeds for direct
before/after comparability; CHUNKED single-seed-per-cell per exp_dev
canonical instruction file section 13). Given the trajectory-SHAPE question
this cell answers is expected to be less seed-sensitive than a single
point-estimate, 2 seeds is the proportionate starting scope; more seeds are
a cheap follow-up if the 2-seed read is ambiguous.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "longer training decline plateau trajectory in-batch objective
  contrastive removed cosine to gold retrieval agreement headline metric"
  -> top hit cosine=0.2841 (this arc's own v3c/v3b prose, expected self-
  similarity), all other hits <=0.26. NONE at cosine>0.30 for a DISTINCT
  prior cell. GENUINELY NOVEL: no prior cell in this lineage runs a
  6000-step trajectory with a trend-slope verdict or promotes ret_agree10/
  hi80_cos to headline status.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices)
- final_metrics_atomicity: tmp_replace (inherited from v3c's
  _train_student_full, reused read-only)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL@v2/v3/v3b/v3c/v3d
  prereg, unchanged -- same K=128/N=4096 quantization channel)
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification (same
  as v3/v3b/v3c/v3d): smoke's tiny V_train=3000 cannot reproduce the true
  near-neighbor coverage-ratio effect; smoke validates MACHINERY ONLY
  (in_batch trains end-to-end at the longer step count, 3-way split
  partitions correctly, best-by-VAL selection + reload fire, the trend-
  slope computation runs on a real multi-point trajectory, cardinality
  holds). The actual plateau-vs-decline question needs the true 177899-
  concept corpus AND the full 6000-step budget -- that IS the FULL dispatch.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: the trend-slope/final-value bands apply to INBATCH_BLOCK_LAST
  only; INBATCH_*_BESTVAL (on TEST) is comparison/context, NOT separately
  gated; RANDOM_BLOCK/CHARPOS/shuffled_key are integrity-only.
- cardinality_ok: EXPECTED_N_UNITS=10 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (same hyperparameters as
  the validated v3c lineage; only step count, eval cadence, headline-metric
  promotion, and verdict semantics differ)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v3e_decline_vs_plateau_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
Does NOT touch v3/v3b/v3c's own artifact/checkpoint directories, nor the
already-dispatched v3c seed_23/29/31 robustness-replicate runs (VET said let
those finish; this is a separate, differently-scoped cell).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import platform
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
ANCHOR_NAME = "encoder_v3e_decline_vs_plateau_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0        # RKD-only (matches v3c's winning ablation config)
OBJECTIVE = "in_batch"  # GLOBAL dropped -- see docstring

# ---- FULL-scale config: LONGER than v3c (VET's explicit ask: 4000-6000) ----
FULL_BATCH = 128                          # matches v3c
FULL_STEPS = 6000                         # VET: 4000-6000, upper end chosen
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 50                # VET: "every ~50 steps"
FULL_TRIALS = v3.MID_TRIALS               # 60 (keyed n_trials)
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP

VAL_CAP = 5000
VAL_QUICK_SUB = 1500
VAL_QUICK_PAIRS = 40_000                  # smaller than v3d: eval fires 8x more often
VAL_FULL_PAIRS = 60_000
TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE      # 400_000 -- reported-number sample

# ---- Smoke config: MACHINERY validation only (SAME code path as FULL) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN          # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD            # 800
SMOKE_STEPS = 200                         # enough eval points to trend-fit
SMOKE_CKPT_EVERY = 60
SMOKE_DENSE_EVAL_EVERY = 20               # ~10 eval points at smoke scale
SMOKE_VAL_CAP = 200
SMOKE_VAL_QUICK_SUB = 120
SMOKE_VAL_QUICK_PAIRS = 3_000
SMOKE_VAL_FULL_PAIRS = 5_000
SMOKE_TEST_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05     # anti-gaming floor (unchanged convention)
MIN_TREND_POINTS = 4              # minimum eval points for a trend fit to count

# semantic(6: LAST+BESTVAL x {DENSE,BLOCK}, RANDOM_BLOCK, CHARPOS) +
# keyed(4: RANDOM_BLOCK-posctrl J5, LAST J5, LAST-shuffled J5, BESTVAL-cmp J5)
# = 10.
EXPECTED_N_UNITS_FULL = 10
EXPECTED_N_UNITS_SMOKE = 10

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

# Trend/verdict bands (HYPOTHESIZED@this prereg). early_minus_late is the
# post-floor early-half-mean minus late-half-mean of the dense_full
# trajectory (positive = declining over training). final_block is the
# LAST-step INBATCH_BLOCK spearman (TEST). V2's documented collapse floor is
# 0.368 CITED@notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md.
PLATEAU_EARLY_MINUS_LATE_MAX = 0.03   # <= this -> essentially flat (plateau)
DECLINE_EARLY_MINUS_LATE_MIN = 0.10   # >= this -> clearly still declining
PLATEAU_FINAL_BLOCK_FLOOR = 0.50      # final must still be well above v2's 0.368 floor
DECLINE_FINAL_BLOCK_CEILING = 0.45    # final approaching v2's 0.368 floor
ALGEBRA_FLOOR = 0.90


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v3e_plateau{tag}{suffix}"


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v3c/v3d.
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
# Trend-slope diagnostic (the core NEW mechanism this cell adds).
# ---------------------------------------------------------------------------

def _trend_diagnostic(traj: List[Dict], key: str, min_step: int) -> Dict:
    """Linear-fit slope + early-half-vs-late-half means over post-floor eval
    points. Returns a dict; `sufficient=False` if too few points to trust."""
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
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_plateau(per_unit: List[Dict], recovery: Dict, expected_units: int,
                     run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")
    posc = v3._by_unit(per_unit, "keyed", "RANDOM_BLOCK", 5)
    prim = v3._by_unit(per_unit, "keyed", "INBATCH_BLOCK_LAST", 5)
    shuf = v3._by_unit(per_unit, "shuffled_key", "INBATCH_BLOCK_LAST", 5)
    if posc is None or prim is None or shuf is None:
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    if posc["acc_at1"] < 0.98:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: RANDOM_BLOCK keyed J=5 "
                f"{posc['acc_at1']:.3f} < 0.98 (SBC lossless prior)")
    if shuf["acc_at1"] > 0.05 or shuf["hit_any_member"] > 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL_SHUFFLED_KEY_LEAK: {shuf['acc_at1']:.3f}/"
                f"{shuf['hit_any_member']:.3f}")

    trend = recovery["trend"]
    tail = (f"[final_dense={recovery['final_dense']:.4f} "
           f"final_block={recovery['final_block']:.4f} "
           f"final_ret_agree10={recovery['headline_final_ret_agree10']:.4f} "
           f"final_hi80_cos={recovery['headline_final_hi80_cos']:.4f} "
           f"final_hi80_calib_err={recovery['headline_final_hi80_calib_err']:.4f} "
           f"bestval_block_on_test={recovery['bestval_block_on_test']:.4f} "
           f"bestval_step={recovery['bestval_step']} "
           f"trend_sufficient={trend.get('sufficient')} "
           f"early_minus_late={trend.get('early_minus_late')} "
           f"n_trend_points={trend.get('n_points')} "
           f"keyed_J5_last={prim['acc_at1']:.3f}]")

    if run_mode == "smoke":
        fails = []
        if not trend.get("sufficient", False):
            fails.append("S_trend_insufficient_points")
        if recovery["bestval_step"] is None or recovery["bestval_step"] < 0:
            fails.append("S_no_best_ckpt")
        if not (math.isfinite(recovery["final_block"]) and -1.0 <= recovery["final_block"] <= 1.0):
            fails.append("S_block_out_of_range")
        if not math.isfinite(recovery["headline_final_ret_agree10"]):
            fails.append("S_ret_agree10_missing")
        if not math.isfinite(recovery["headline_final_hi80_cos"]):
            fails.append("S_hi80_cos_missing")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: in_batch trains end-to-end at the longer "
                f"step count, 3-way split partitions correctly, trend-slope "
                f"diagnostic runs on a real multi-point trajectory, headline "
                f"ret_agree10/hi80_cos fields populate {tail} (the plateau-vs-"
                f"decline discriminator is a FULL-only question; smoke's tiny "
                f"V_train and step count cannot reproduce it)")

    # full: FALSE_WIN_ALGEBRA (unchanged single-J=5 convention this cell uses).
    if prim["acc_at1"] < ALGEBRA_FLOOR:
        return ("HARD_FAIL",
                f"FALSE_WIN_ALGEBRA_LAST_STEP: keyed_roundtrip J=5 "
                f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (BLOCK code at "
                f"LAST-step is not a valid composable SBC code) {tail}")

    if not trend.get("sufficient", False):
        return ("HARD_FAIL", f"HARD_FAIL_TREND_INSUFFICIENT_POINTS {tail}")

    eml = trend["early_minus_late"]
    final_block = recovery["final_block"]
    if eml <= PLATEAU_EARLY_MINUS_LATE_MAX and final_block >= PLATEAU_FINAL_BLOCK_FLOOR:
        return ("HARD_PASS",
                f"PLATEAU_CONFIRMED: the post-floor trajectory is essentially "
                f"flat (early-half-mean minus late-half-mean = {eml:.4f} <= "
                f"{PLATEAU_EARLY_MINUS_LATE_MAX}) and the FINAL-step BLOCK "
                f"spearman ({final_block:.4f}) stays well above v2's 0.368 "
                f"collapse floor -- removing NCE genuinely FIXES the in_batch "
                f"objective's late-training behavior, not merely delays "
                f"collapse {tail}")
    if eml >= DECLINE_EARLY_MINUS_LATE_MIN or final_block <= DECLINE_FINAL_BLOCK_CEILING:
        return ("HARD_FAIL",
                f"DECLINE_CONTINUES: the trajectory is still meaningfully "
                f"declining post-floor (early-half-mean minus late-half-mean = "
                f"{eml:.4f}) and/or the FINAL-step value ({final_block:.4f}) is "
                f"approaching v2's 0.368 collapse floor -- removing NCE only "
                f"SLOWED the in_batch objective's collapse, it did not fix it; "
                f"the true asymptote likely requires an objective-family change "
                f"(Rank 2, KL/PKT-style swap) not just a longer NCE-off run "
                f"{tail}")
    return ("MIDDLE_BAND",
            f"AMBIGUOUS_TREND: neither a clean plateau nor a clear continued "
            f"decline at 6000 steps -- real signal, inconclusive on the "
            f"plateau-vs-decline question; consider an even longer run or "
            f"more seeds before deciding the objective-family question {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_plateau(run_mode: str, seed: int, device_arg: str, n_dim: int,
               teacher_cache_arg: Optional[str], run_tag: str = "") -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
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
    print(f"[v3e_plateau] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} nce_weight={NCE_WEIGHT} "
          f"dense_eval_every={dense_every} min_step_for_best={min_step_for_best}",
          flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[v3e_plateau] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v3e_plateau] split train={n_tr} val={n_val} test={n_test}", flush=True)

    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v3e_plateau] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xval_sub = Xval[:min(quick_sub, n_val)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xval, val_full_pairs, seed + 7)

    ckpt_path = art_dir / "_ckpt_INBATCH.pt"
    best_ckpt_path = art_dir / "_ckpt_best_INBATCH.pt"
    last_student, diag = v3c._train_student_full(
        kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
        ckpt_path, best_ckpt_path, ckpt_every, out_dir, t0,
        None, 0, NCE_WEIGHT, "INBATCH", OBJECTIVE,
        dense_eval_quick_fn=_deval_quick, dense_eval_full_fn=_deval_full,
        dense_eval_every=dense_every, min_step_for_best=min_step_for_best)
    print(f"[v3e_plateau] INBATCH trained rkd_last={diag['rkd_last']:.4f} "
          f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
          f"n_traj_points={len(diag['dense_traj'])} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    in_dim = Xtr.shape[1]
    bestval_student = v3c._reload_best_student(
        "mlp", in_dim, kb * blk_l, device, best_ckpt_path)

    arm_codes: Dict[str, torch.Tensor] = {
        "INBATCH_DENSE_LAST": v3._dense_sign_codes(last_student, Xtest),
        "INBATCH_BLOCK_LAST": v3._encode_hard_block(last_student, Xtest, kb, blk_l),
        "INBATCH_DENSE_BESTVAL": v3._dense_sign_codes(bestval_student, Xtest),
        "INBATCH_BLOCK_BESTVAL": v3._encode_hard_block(bestval_student, Xtest, kb, blk_l),
    }
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], n_dim, kb)

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
            print(f"[v3e_plateau] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in ("INBATCH_DENSE_LAST", "INBATCH_BLOCK_LAST",
                  "INBATCH_DENSE_BESTVAL", "INBATCH_BLOCK_BESTVAL"):
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
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK_LAST", "sbc",
              arm_codes["INBATCH_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK_BESTVAL", "sbc",
              arm_codes["INBATCH_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials,
              gen_eval, device)
    _run_unit(v3._keyed_unit, "INBATCH_BLOCK_LAST", "sbc",
              arm_codes["INBATCH_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval,
              device, shuffled_key=True)

    def _sp(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return u

    last_dense_u = _sp("INBATCH_DENSE_LAST")
    last_block_u = _sp("INBATCH_BLOCK_LAST")
    bestval_dense_u = _sp("INBATCH_DENSE_BESTVAL")
    bestval_block_u = _sp("INBATCH_BLOCK_BESTVAL")

    trend = _trend_diagnostic(diag["dense_traj"], "dense_full", min_step_for_best)

    recovery = {
        "final_dense": float(last_dense_u["spearman_all"]) if last_dense_u else float("nan"),
        "final_block": float(last_block_u["spearman_all"]) if last_block_u else float("nan"),
        "bestval_dense_on_test": float(bestval_dense_u["spearman_all"]) if bestval_dense_u else float("nan"),
        "bestval_block_on_test": float(bestval_block_u["spearman_all"]) if bestval_block_u else float("nan"),
        "bestval_step": diag["best_step"],
        "bestval_step_frac": (diag["best_step"] / steps) if steps > 0 and diag["best_step"] >= 0 else None,
        "best_ckpt_fallback_to_final": diag["best_ckpt_fallback_to_final"],
        # HEADLINE metrics (VET's explicit ask -- promoted out of per_unit).
        "headline_final_ret_agree10": float(last_block_u["ret_agree10"]) if last_block_u else float("nan"),
        "headline_final_hi80_cos": float(last_block_u["hi80_cos"]) if last_block_u else float("nan"),
        "headline_final_hi80_teacher_mean": float(last_block_u["hi80_teacher_mean"]) if last_block_u else float("nan"),
        "headline_final_hi80_calib_err": float(last_block_u["hi80_calib_err"]) if last_block_u else float("nan"),
        "headline_bestval_ret_agree10": float(bestval_block_u["ret_agree10"]) if bestval_block_u else float("nan"),
        "headline_bestval_hi80_cos": float(bestval_block_u["hi80_cos"]) if bestval_block_u else float("nan"),
        "trend": trend,
        "n_traj_points": len(diag["dense_traj"]),
        "dense_traj_val": diag["dense_traj"],
        "charpos_ret_agree10": float(_sp("CHARPOS")["ret_agree10"]) if _sp("CHARPOS") else float("nan"),
        "random_block_ret_agree10": float(_sp("RANDOM_BLOCK")["ret_agree10"]) if _sp("RANDOM_BLOCK") else float("nan"),
    }
    verdict, verdict_msg = _verdict_plateau(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE,
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_train": n_tr, "n_val": n_val,
        "n_test": n_test, "n_held_pool": n_he,
        "semi_hard_coverage": semi_cov,
        "recovery": recovery,
        "train_diag": diag,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("LONGER (6000-step) in_batch-RKD-only run with finer "
                        "(every-50-step) trajectory logging; 3-way split "
                        "(train/val/test, TEST never used for selection); "
                        "FINAL-step is the PRIMARY gated number, best-by-VAL-"
                        "on-TEST is SECONDARY context; ret_agree10 + hi80_cos "
                        "promoted to top-level headline fields alongside the "
                        "Spearman number; trend-slope (linear fit + early-vs-"
                        "late-half means, post-anti-gaming-floor) decides "
                        "PLATEAU_CONFIRMED / DECLINE_CONTINUES / AMBIGUOUS_TREND"),
        "progress_logging": "print_flush_true",
        "primary_spearman": recovery["final_block"],
        "dense_sign_spearman": recovery["final_dense"],
        "baseline_in_band": bool(0.05 < recovery["charpos_ret_agree10"] < 0.95),
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K), K=128 -> 0.901 (unchanged from v2/v3/v3b/v3c)"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v3e_plateau] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. trend diagnostic: declining synthetic trajectory must show
    #    early_minus_late > 0 and a negative slope; step0-only artifact
    #    (excluded by min_step) must not corrupt it.
    traj = ([{"step": 0, "dense_full": 0.95}] +
            [{"step": s, "dense_full": 0.80 - 0.05 * (s // 20)}
             for s in range(20, 201, 20)])
    trend = _trend_diagnostic(traj, "dense_full", min_step=10)
    assert trend["sufficient"] is True
    assert trend["slope_per_step"] < 0, "selftest: declining synthetic traj must have negative slope"
    assert trend["early_minus_late"] > 0.05, "selftest: declining traj must show early>late"

    flat_traj = ([{"step": 0, "dense_full": 0.95}] +
                [{"step": s, "dense_full": 0.75 + 0.001 * ((s % 3) - 1)}
                 for s in range(20, 201, 20)])
    trend_flat = _trend_diagnostic(flat_traj, "dense_full", min_step=10)
    assert abs(trend_flat["early_minus_late"]) < 0.03, "selftest: flat traj must read as plateau"

    too_short = [{"step": 0, "dense_full": 0.9}, {"step": 10, "dense_full": 0.8}]
    trend_short = _trend_diagnostic(too_short, "dense_full", min_step=0)
    assert trend_short["sufficient"] is False

    # 2. verdict bands.
    fake_units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(6)]
    fake_units += [
        {"unit": "keyed::RANDOM_BLOCK::J5", "arm": "RANDOM_BLOCK", "kind": "keyed",
         "J": 5, "acc_at1": 0.99, "hit_any_member": 0.99},
        {"unit": "keyed::INBATCH_BLOCK_LAST::J5", "arm": "INBATCH_BLOCK_LAST",
         "kind": "keyed", "J": 5, "acc_at1": 0.97, "hit_any_member": 0.97},
        {"unit": "keyed::INBATCH_BLOCK_BESTVAL::J5", "arm": "INBATCH_BLOCK_BESTVAL",
         "kind": "keyed", "J": 5, "acc_at1": 0.96, "hit_any_member": 0.96},
        {"unit": "shuffled_key::INBATCH_BLOCK_LAST::J5", "arm": "INBATCH_BLOCK_LAST",
         "kind": "shuffled_key", "J": 5, "acc_at1": 0.01, "hit_any_member": 0.01},
    ]
    rec_plateau = {
        "final_dense": 0.72, "final_block": 0.75, "bestval_dense_on_test": 0.80,
        "bestval_block_on_test": 0.81, "bestval_step": 3000,
        "headline_final_ret_agree10": 0.45, "headline_final_hi80_cos": 0.80,
        "headline_final_hi80_calib_err": 0.05,
        "trend": {"sufficient": True, "n_points": 100, "early_minus_late": 0.01},
    }
    v_plateau, m_plateau = _verdict_plateau(fake_units, rec_plateau, 10, "full")
    assert v_plateau == "HARD_PASS" and "PLATEAU_CONFIRMED" in m_plateau, (
        f"selftest: expected PLATEAU HARD_PASS got {v_plateau} ({m_plateau})")

    rec_decline = dict(rec_plateau, final_block=0.40,
                      trend={"sufficient": True, "n_points": 100, "early_minus_late": 0.15})
    v_decline, m_decline = _verdict_plateau(fake_units, rec_decline, 10, "full")
    assert v_decline == "HARD_FAIL" and "DECLINE_CONTINUES" in m_decline, (
        f"selftest: expected DECLINE HARD_FAIL got {v_decline} ({m_decline})")

    rec_ambig = dict(rec_plateau, final_block=0.60,
                     trend={"sufficient": True, "n_points": 100, "early_minus_late": 0.06})
    v_ambig, m_ambig = _verdict_plateau(fake_units, rec_ambig, 10, "full")
    assert v_ambig == "MIDDLE_BAND" and "AMBIGUOUS_TREND" in m_ambig, (
        f"selftest: expected AMBIGUOUS MIDDLE_BAND got {v_ambig} ({m_ambig})")

    v_card, m_card = _verdict_plateau(fake_units[:3], rec_plateau, 10, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    fake_units_leak = copy.deepcopy(fake_units)
    for u in fake_units_leak:
        if u.get("kind") == "shuffled_key":
            u["acc_at1"] = 0.5
    v_leak, m_leak = _verdict_plateau(fake_units_leak, rec_plateau, 10, "full")
    assert v_leak == "HARD_FAIL" and "SHUFFLED_KEY_LEAK" in m_leak

    fake_units_algbreak = copy.deepcopy(fake_units)
    for u in fake_units_algbreak:
        if u.get("arm") == "INBATCH_BLOCK_LAST" and u.get("kind") == "keyed":
            u["acc_at1"] = 0.20
    v_alg, m_alg = _verdict_plateau(fake_units_algbreak, rec_plateau, 10, "full")
    assert v_alg == "HARD_FAIL" and "FALSE_WIN_ALGEBRA_LAST_STEP" in m_alg

    # 3. tiny end-to-end training reuse of v3c._train_student_full +
    #    _reload_best_student (proves the longer-run wiring is correct).
    n_dim, kb, blk_l, v_syn = 256, 16, 16, 400
    torch.manual_seed(11)
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
        st_last, diag_st = v3c._train_student_full(
            kb, blk_l, Xsyn, pos_syn, semi_syn, 40, 24, 4, 13, "cpu",
            tdp / "ckpt.pt", tdp / "ckpt_best.pt", 100, tdp, t0,
            None, 0, 0.0, "TEST_INBATCH", "in_batch",
            dense_eval_quick_fn=_dq, dense_eval_full_fn=_df, dense_eval_every=4,
            min_step_for_best=2)
        assert math.isfinite(diag_st["rkd_last"])
        assert len(diag_st["dense_traj"]) >= MIN_TREND_POINTS
        trend_real = _trend_diagnostic(diag_st["dense_traj"], "dense_full", min_step=2)
        assert trend_real["sufficient"] is True
        st_bestval = v3c._reload_best_student("mlp", 64, kb * blk_l, "cpu",
                                              tdp / "ckpt_best.pt")
        c_last = v3._encode_hard_block(st_last, Xtest_syn, kb, blk_l)
        c_bestval = v3._encode_hard_block(st_bestval, Xtest_syn, kb, blk_l)
        assert c_last.shape == c_bestval.shape == (24, kb * blk_l)
        assert torch.isfinite(c_last).all() and torch.isfinite(c_bestval).all()
        u = v3._semantic_unit("TEST", c_last, c_last, Xtest_syn, Xtest_syn, 0, 500, 3)
        assert "ret_agree10" in u and "hi80_cos" in u, (
            "selftest: headline fields (ret_agree10/hi80_cos) must be present "
            "on the raw semantic unit this cell promotes to top-level")

    print(f"[selftest] PASS (trend-slope diagnostic incl step0-artifact "
          f"exclusion + plateau/decline/ambiguous verdict bands + cardinality/"
          f"integrity/algebra gates + v3c._train_student_full/_reload_best_"
          f"student reuse via tiny synthetic longer-run training + headline-"
          f"field presence check) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0
