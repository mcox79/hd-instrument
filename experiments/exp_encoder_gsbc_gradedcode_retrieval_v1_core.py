"""Paired hard-block-STE vs graded-GSBC retrieval, in the carry-through SHIP-METRIC
regime, to attack the ret_agree10 gap (carry-through INBATCH_BLOCK ret_agree10 =
0.1837 < 0.30) with a REPRESENTATION-side lever.

HYPOTHESIS (Director hand-off): hard block-STE quantization (one bipolar winner
per block, no magnitude) loses the fine rank ordering needed for top-10 retrieval
agreement (the student ranks well -- spearman ~0.886 -- but hard-quantizes so the
top-10 neighborhood is coarse); a graded / annealed GSBC code (top-m graded
survivors per block, unit-L1, sign-free positive magnitudes for retrieval; block
circular-conv binding for algebra) preserves the retrieval-relevant structure
WITHOUT breaking the SBC/GSBC bind-unbind algebra.

PAIRED CONTRACT (Director):
  ARM_HARD_STE  = hard block-STE (baseline; reproduces ~0.18-0.21 ret_agree10)
  ARM_GRADED    = annealed soft->hard graded GSBC + listwise-rank + absolute-
                  cosine anchor (treatment)
  HARD-PASS = ret_agree10 lift (graded - hard) >= +0.05 WHILE
              graded cosine_to_gold(hi80) >= 0.80 AND graded composed_roundtrip
              (keyed@J10) >= 0.95.
  HARD-FAIL = ret_agree10 lift <= +0.02, OR graded breaks algebra (composed
              roundtrip < 0.95) OR degrades cosine (cosine_to_gold < 0.80).
  MIDDLE    = real but partial (lift in (0.02,0.05) with cosine+algebra intact).
  Report ALL THREE (ret_agree10, cosine_to_gold, composed roundtrip) for BOTH
  arms so a retrieval gain that sacrifices algebra/calibration is caught (the
  JOINT-gate FALSE-PASS discipline: a rank lift bought by overshooting teacher
  cosine and wrecking hi80 is NOT a win).

PRIOR-WORK CHECK -- CRITICAL (exp_dev, filesystem-verify Fix#28, 2026-07-05):
  (1) substrate-KB concept-query "graded soft GSBC code straight-through
      estimator anneal temperature quantization retrieval agreement top-k" ->
      top hit cosine 0.2656 (a Bengio-STE citation buried in a decode-side
      note); ALL hits <= 0.2656, NONE > 0.30. No prior arc CELL at threshold in
      the KB. But the KB is not the disk:
  (2) FILESYSTEM shows this lever LARGELY LANDED already. Both MEASURED on the
      SAME 177899-concept teacher cache, FULL, 2 seeds each, HARD_PASS:
        exp_encoder_v11_gsbc_graded_sparse_v1 (graded GSBC top-3 + annealed
          soft->hard STE + listwise + anchor). Deployed-code (BLOCK_LAST) at
          177899, seed7:
            SIGN_BLOCK  ret_agree10 = 0.2117  hi80_cos = 0.8290  keyed@J5 = 1.000
              MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/metrics.json:per_unit[SIGN_BLOCK_BLOCK_LAST]
            GSBC_FULL   ret_agree10 = 0.3986  hi80_cos = 0.8338  keyed@J5 = 1.000
              MEASURED@ same :per_unit[GSBC_FULL_BLOCK_LAST]
            LIFT = +0.1869 (>> +0.05); cosine PRESERVED (0.8338 >= 0.80);
              algebra PRESERVED (keyed@J5 1.000 >= 0.95).
        exp_encoder_v12_gsbc_gwta_expansion_v1 (GSBC + FlyHash GWTA expansion),
          177899, seed7: GSBC_EXPAND2X ret_agree10 = 0.6027 hi80 = 0.8449
          keyed@J8 = 1.000 keyed@J16 = 1.000 (composed algebra holds past J10)
            MEASURED@data/exp_encoder_v12_gsbc_gwta_expansion_v1_seed7/metrics.json:per_unit
      SO THE TASK HYPOTHESIS IS ALREADY CONFIRMED ON DISK. This cell is NOT a
      rediscovery of the lever; it is a paired carry-through of the PROVEN lever
      into the carry-through cell's EXACT ship-metric regime + gates, whose only
      genuine measurement gap vs v11 is: composed_roundtrip AT J10 for the
      GSBC_FULL graded code specifically (v11 gated keyed@J5 only; v12 brackets
      J8=J16=1.0 but for the EXPAND2X code, not GSBC_FULL). It gives a single
      clean paired hard-vs-graded table in the ship regime with the stricter
      cosine>=0.80 + composed@J10>=0.95 gates. The completion report leads with
      this finding so the Director can decide FULL-GPU-spend vs re-verdict of
      landed v11/v12 (this cell can also SKIP dispatch entirely if the Director
      judges v11/v12 sufficient). NO BUSY WORK: staged, not self-dispatched.

REUSE (no shared-file edits): trainer/encode/keyed all imported READ-ONLY from
  v11 (exp_encoder_v11_gsbc_graded_sparse_v1_core) -- the SAME code path that
  produced the landed HARD_PASS -- and semantic/charpos units from v3. This cell
  is a THIN orchestrator; it does not reimplement the graded machinery.

DISCRIMINATOR-SURVIVES-SCALE (option B analytical + prior-landed): the ret-lift
  discriminator is a FULL-only question (smoke V=3000, 200 steps, width 256 will
  NOT crystallize the trained ret gap -- same precedent as v11/v12/carry-through
  smoke). Smoke validates MACHINERY + fires the ALGEBRA discriminator via the
  training-INDEPENDENT random-code positive control (RANDOM keyed@J5 ~= 1.0 for
  BOTH sbc and gsbc_circconv algebra) + shuffled-key leak control + arms-differ.
  The FULL-scale lift is MEASURED@ landed v11 (+0.1869) and v12 (+0.16..+0.39):
  the discriminator provably survives scale.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over float32 codes of HARD/GRADED/CHARPOS/RANDOMs
  (float bytes, NOT int8 -- graded codes are positive fractional; int8 cast would
  collapse them to 0 and false-trigger AF).
- final_metrics_atomicity: tmp_replace (write_metrics atomic).
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare).
- crlb_floor_computed: r_max=0.901 at K=128 (THEORETICAL; same block channel).
  discriminator_reachability=True: the +0.05 HARD-PASS lift is far below the
  MEASURED@ landed +0.1869 (v11) lift -> reachable.
- baseline_in_band: CHARPOS ret_agree10 in (0.05,0.95).
- HARD_PASS strictly above the +0.02 HARD-FAIL ceiling by >5% band-width.
- HP_SCOPE: {GRADED: [ret_agree10_lift, cosine_to_gold, composed_roundtrip]}.
  HARD_STE (paired baseline) + CHARPOS + RANDOM_* are integrity-only.
- cardinality_ok: EXPECTED_N_UNITS declared, counted from per_unit.
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (identical hyperparameters to the
  landed v11 arms; only the eval is re-pointed at the carry-through ship gates).
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@.
- cell_chunked: False (single-seed; FULL multi-seed via re-dispatch of --seed).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (line-buffered stdout + flush=True).

Parent cells (imported, single-hop, READ-ONLY):
  experiments/exp_encoder_migration_step1b_v3_..._v1_core.py                 (v3)
  experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py                 (v11)
Prereg: preregs/2026-07-05_exp_encoder_gsbc_gradedcode_retrieval_v1.md

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys as _sys
_ARGV_SNAPSHOT = list(_sys.argv)

import argparse
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

if list(sys.argv) != _ARGV_SNAPSHOT:
    sys.argv = _ARGV_SNAPSHOT

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_gsbc_gradedcode_retrieval_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_FULL = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

# ---- Paired arms (both via v11._train_student_v11; identical batch sampling,
# differ ONLY in mode/geometry/recipe = the treatment) ----
# (mode, kb, blk_l, m, recipe). kb*blk_l == N_DIM (4096).
HARD_ARM = ("sign", 128, 32, 1, "rkd_only")   # hard block-STE baseline (== v11 SIGN_BLOCK == v3e)
GRADED_ARM = ("gsbc", 32, 128, 3, "full")     # annealed graded GSBC + rank + anchor (== v11 GSBC_FULL)

# ---- FULL config: MATCHED to v11 GSBC_FULL (the landed HARD_PASS recipe) ----
FULL_STEPS = v11.FULL_STEPS               # 8000 (anneal schedule tuned for this)
FULL_BATCH = v11.FULL_BATCH               # 128
FULL_WIDTH = 2048                         # v11 STE_ARMS width
FULL_CKPT_EVERY = v11.CKPT_EVERY_STEPS_FULL   # 500
FULL_DENSE_EVAL_EVERY = v11.DENSE_EVAL_EVERY_FULL  # 400
FULL_QUICK_SUB = v11.VAL_QUICK_SUB        # 1500
FULL_QUICK_PAIRS = v11.VAL_QUICK_PAIRS    # 40000
FULL_TRAJ_PAIRS = v11.VAL_FULL_PAIRS      # 60000
FULL_FINAL_PAIRS = v11.TEST_FINAL_PAIRS   # 400000
FULL_CHARPOS_CAP = v11.FULL_CHARPOS_CAP   # 3000
FULL_TRIALS = v11.FULL_TRIALS             # 60

# ---- Smoke config: MACHINERY validation only (option B; see docstring) ----
SMOKE_N_TRAIN = v3.SMOKE_N_TRAIN          # 3000
SMOKE_N_HELD = v3.SMOKE_N_HELD            # 800
SMOKE_STEPS = 200
SMOKE_WIDTH = 256
SMOKE_CKPT_EVERY = 60
SMOKE_DENSE_EVAL_EVERY = 40
SMOKE_QUICK_SUB = 120
SMOKE_QUICK_PAIRS = 3_000
SMOKE_TRAJ_PAIRS = 5_000
SMOKE_FINAL_PAIRS = 8_000
SMOKE_CHARPOS_CAP = 300
SMOKE_TRIALS = 20

MIN_STEP_FRAC_FOR_BEST = 0.05

# Algebra roundtrip loads: J_ISO = isolated; J_COMPOSED = the ship-grade harder
# composed load (carry-through gates composed_roundtrip at J10).
J_ISO = 5
J_COMPOSED_FULL = 10
J_COMPOSED_SMOKE = 8

# Units: per arm {semantic, keyed@J_ISO, keyed@J_COMPOSED, shuffled@J_ISO,
# random-posctrl@J_ISO} = 5; x2 arms = 10; + CHARPOS semantic = 11.
EXPECTED_N_UNITS = 11

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_HARD", "RANDOM_GRADED"]

# ---- Ship-metric bands (PAIRED gate; Director hand-off contract) ----
HP_LIFT = 0.05               # HYPOTHESIZED@hand-off: ret_agree10 lift HARD-PASS floor
HF_LIFT = 0.02               # HYPOTHESIZED@hand-off: ret_agree10 lift HARD-FAIL ceiling
HP_COS_TO_GOLD = 0.80        # HYPOTHESIZED@hand-off: graded cosine_to_gold floor
HP_COMPOSED_RT = 0.95        # HYPOTHESIZED@hand-off: graded composed roundtrip floor
# Integrity thresholds.
POSCTRL_KEYED_FLOOR = 0.98   # random-code keyed roundtrip (algebra machinery)
SHUFFLED_LEAK_CEIL = 0.05    # shuffled-key must not retrieve the true target


def _artifact_dir(run_mode: str, seed: int) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return (_REPO / "data"
            / f"substrate_gsbc_gradedcode_retrieval_v1{suffix}_seed{int(seed)}")


# ---------------------------------------------------------------------------
# Defensive helpers.
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


def _resolve_smoke_cache(min_concepts: int) -> Path:
    cand_dir = _REPO / "data" / "substrate_index" / "cached_indices"
    best: Optional[Tuple[int, Path]] = None
    for p in sorted(cand_dir.glob("bge_large_v2_name_*.npz")):
        parts = p.stem.split("_")
        try:
            count = int(parts[4])
        except (IndexError, ValueError):
            continue
        if count >= min_concepts and (best is None or count < best[0]):
            best = (count, p)
    if best is None:
        return v3._resolve_teacher_cache(None)
    return best[1]


def _code_digest(code: torch.Tensor) -> str:
    """sha256 over float32 code bytes (NOT int8: graded codes are fractional)."""
    arr = code.detach().to(torch.float32).contiguous().cpu().numpy()
    return hashlib.sha256(arr.tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Train + encode one paired arm (thin wrapper over v11).
# ---------------------------------------------------------------------------

def _train_encode_arm(arm_label: str, spec: Tuple, Xtr: torch.Tensor,
                      Xhe: torch.Tensor, art_dir: Path, out_dir: Path,
                      steps: int, batch: int, width: int, ckpt_every: int,
                      dense_every: int, quick_sub: int, quick_pairs: int,
                      traj_pairs: int, seed: int, device: str, warmup: int,
                      min_step_for_best: int, t0: float
                      ) -> Tuple[torch.Tensor, Dict, Tuple[int, int, int]]:
    """Train arm via v11, reload best ckpt, return (deployed_code_he, diag, geom)."""
    mode, kb, blk_l, m, recipe = spec
    Xhe_sub = Xhe[:min(quick_sub, Xhe.shape[0])].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, traj_pairs, seed + 7)

    ck = art_dir / f"_ckpt_{arm_label}.pt"
    best = art_dir / f"_ckpt_best_{arm_label}.pt"
    _student, diag = v11._train_student_v11(
        mode, kb, blk_l, m, width, Xtr, steps, batch, warmup, seed, device,
        ck, best, ckpt_every, out_dir, t0, _deval_quick, _deval_full,
        dense_every, min_step_for_best, v11.SELECT_TAU, recipe, arm_label)
    best_student = v11._reload_best_v11(width, Xtr.shape[1], kb * blk_l, device, best)
    code_he = v11._encode_block_for_arm(mode, best_student, Xhe, kb, blk_l, m)
    print(f"[graded] arm {arm_label} trained rkd_last={diag['rkd_last']:.4f} "
          f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
          f"tau_last={diag.get('tau_last')} ({time.perf_counter() - t0:.1f}s)",
          flush=True)
    return code_he, diag, (kb, blk_l, m)


# ---------------------------------------------------------------------------
# Verdict logic (PAIRED ship gate on GRADED vs HARD_STE).
# ---------------------------------------------------------------------------

def _verdict(per_unit: List[Dict], ship: Dict, expected_units: int,
             run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")

    # Integrity gates (both modes): algebra machinery + no leak, BOTH algebras.
    pc_h = v3._by_unit(per_unit, "keyed", "RANDOM_HARD", J_ISO)
    pc_g = v3._by_unit(per_unit, "keyed", "RANDOM_GRADED", J_ISO)
    sh_h = v3._by_unit(per_unit, "shuffled_key", "HARD_STE", J_ISO)
    sh_g = v3._by_unit(per_unit, "shuffled_key", "GRADED", J_ISO)
    if any(u is None for u in (pc_h, pc_g, sh_h, sh_g)):
        return ("HARD_FAIL", "HARD_FAIL_MISSING_GATE_UNITS")
    for nm, u in (("RANDOM_HARD", pc_h), ("RANDOM_GRADED", pc_g)):
        if u["acc_at1"] < POSCTRL_KEYED_FLOOR:
            return ("HARD_FAIL",
                    f"HARD_FAIL_ALGEBRA_LOSSLESS_PRIOR: {nm} keyed J={J_ISO} "
                    f"{u['acc_at1']:.3f} < {POSCTRL_KEYED_FLOOR} (bind/unbind "
                    f"machinery broken; not a training result)")
    for nm, u in (("HARD_STE", sh_h), ("GRADED", sh_g)):
        if u["acc_at1"] > SHUFFLED_LEAK_CEIL or u["hit_any_member"] > 0.10:
            return ("HARD_FAIL",
                    f"HARD_FAIL_SHUFFLED_KEY_LEAK: {nm} {u['acc_at1']:.3f}/"
                    f"{u['hit_any_member']:.3f}")

    h_ra = ship["hard_ret_agree10"]
    g_ra = ship["graded_ret_agree10"]
    lift = ship["ret_agree10_lift"]
    g_cos = ship["graded_cosine_to_gold"]
    h_cos = ship["hard_cosine_to_gold"]
    g_iso = ship["graded_isolated_roundtrip"]
    g_comp = ship["graded_composed_roundtrip"]
    h_comp = ship["hard_composed_roundtrip"]
    charpos_ra = ship["charpos_ret_agree10"]
    baseline_in_band = ship["baseline_in_band"]
    tail = (f"[HARD ret={h_ra:.4f} cos={h_cos:.4f} comp@J{ship['j_composed']}="
            f"{h_comp:.4f} | GRADED ret={g_ra:.4f} cos={g_cos:.4f} "
            f"iso@J{J_ISO}={g_iso:.4f} comp@J{ship['j_composed']}={g_comp:.4f} | "
            f"LIFT={lift:+.4f} charpos_ret={charpos_ra:.4f} "
            f"baseline_in_band={baseline_in_band}]")

    if run_mode == "smoke":
        fails = []
        for k in ("hard_ret_agree10", "graded_ret_agree10", "graded_composed_roundtrip"):
            if not math.isfinite(ship[k]):
                fails.append(f"S_{k}_nan")
        if not (-1.0 <= g_ra <= 1.0) or not (-1.0 <= h_ra <= 1.0):
            fails.append("S_ret_agree_out_of_range")
        if fails:
            return ("SMOKE_GATE_FAIL", "; ".join(fails))
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: BOTH arms (hard-block-STE sbc + annealed "
                f"graded-GSBC circ-conv) train end-to-end with differing codes; "
                f"algebra pos-ctrl fires for BOTH algebras (RANDOM_HARD keyed="
                f"{pc_h['acc_at1']:.3f}, RANDOM_GRADED keyed={pc_g['acc_at1']:.3f} "
                f">= {POSCTRL_KEYED_FLOOR}); no shuffled-key leak "
                f"(HARD {sh_h['acc_at1']:.3f}, GRADED {sh_g['acc_at1']:.3f}); "
                f"the trained ret-lift is a FULL-only question (smoke V/steps too "
                f"small to crystallize; MEASURED@ landed v11 +0.1869) {tail}")

    # FULL: paired ship gate. HARD-FAIL first.
    if lift <= HF_LIFT:
        return ("HARD_FAIL",
                f"SHIP_HARD_FAIL_NO_LIFT: ret_agree10 lift {lift:+.4f} <= "
                f"{HF_LIFT:+.4f}. The graded code did NOT beat hard block-STE on "
                f"top-10 retrieval agreement at ship scale (contradicts landed "
                f"v11 +0.1869 -- investigate regime/seed) {tail}")
    if g_cos < HP_COS_TO_GOLD:
        return ("HARD_FAIL",
                f"SHIP_HARD_FAIL_CALIB_COLLAPSE: graded cosine_to_gold(hi80) "
                f"{g_cos:.4f} < {HP_COS_TO_GOLD}. A ret lift bought by wrecking "
                f"absolute-cosine calibration is a FALSE PASS, not a win "
                f"(the JOINT-gate discipline) {tail}")
    if g_comp < HP_COMPOSED_RT:
        return ("HARD_FAIL",
                f"SHIP_HARD_FAIL_ALGEBRA_BREAK: graded composed_roundtrip@J"
                f"{ship['j_composed']} {g_comp:.4f} < {HP_COMPOSED_RT}. The "
                f"graded code lifts retrieval but breaks the GSBC bind/unbind "
                f"algebra under composed load -- a graded code that breaks "
                f"algebra is a HARD_FAIL per contract {tail}")

    joint_pass = (lift >= HP_LIFT and g_cos >= HP_COS_TO_GOLD
                  and g_comp >= HP_COMPOSED_RT and baseline_in_band)
    if joint_pass:
        return ("HARD_PASS",
                f"SHIP_HARD_PASS: graded-GSBC lifts ret_agree10 by {lift:+.4f} "
                f">= {HP_LIFT} over hard block-STE WHILE preserving "
                f"cosine_to_gold ({g_cos:.4f} >= {HP_COS_TO_GOLD}) AND composed "
                f"algebra ({g_comp:.4f} >= {HP_COMPOSED_RT}). The representation-"
                f"side lever closes the retrieval-agreement gap without "
                f"sacrificing calibration or algebra {tail}")
    return ("MIDDLE_BAND",
            f"SHIP_MIDDLE_BAND: partial -- lift>= {HP_LIFT}? {lift >= HP_LIFT}; "
            f"graded cosine>= {HP_COS_TO_GOLD}? {g_cos >= HP_COS_TO_GOLD}; graded "
            f"composed>= {HP_COMPOSED_RT}? {g_comp >= HP_COMPOSED_RT}. Real signal "
            f"but the JOINT ship gate is not fully cleared {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_paired(run_mode: str, seed: int, device_arg: str, n_dim: int,
               teacher_cache_arg: Optional[str]) -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, seed)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    if n_dim != v3.N_DIM_DEFAULT:
        raise ValueError(f"n_dim {n_dim} != {v3.N_DIM_DEFAULT} (arm geometry pinned)")

    det = v11._pin_determinism(seed)

    if run_mode == "smoke":
        steps, batch, width = SMOKE_STEPS, SMOKE_N_TRAIN, SMOKE_WIDTH
        batch = min(FULL_BATCH, SMOKE_N_TRAIN)
        ckpt_every, dense_every = SMOKE_CKPT_EVERY, SMOKE_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = SMOKE_QUICK_SUB, SMOKE_QUICK_PAIRS
        traj_pairs, final_pairs = SMOKE_TRAJ_PAIRS, SMOKE_FINAL_PAIRS
        charpos_cap, n_trials = SMOKE_CHARPOS_CAP, SMOKE_TRIALS
        j_composed = J_COMPOSED_SMOKE
        n_tr_target, n_he_target = SMOKE_N_TRAIN, SMOKE_N_HELD
    else:
        steps, batch, width = FULL_STEPS, FULL_BATCH, FULL_WIDTH
        ckpt_every, dense_every = FULL_CKPT_EVERY, FULL_DENSE_EVAL_EVERY
        quick_sub, quick_pairs = FULL_QUICK_SUB, FULL_QUICK_PAIRS
        traj_pairs, final_pairs = FULL_TRAJ_PAIRS, FULL_FINAL_PAIRS
        charpos_cap, n_trials = FULL_CHARPOS_CAP, FULL_TRIALS
        j_composed = J_COMPOSED_FULL
        n_tr_target = n_he_target = None

    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(MIN_STEP_FRAC_FOR_BEST * steps)))
    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.perf_counter()
    print(f"[graded] run_mode={run_mode} seed={seed} device={device} n_dim={n_dim} "
          f"steps={steps} batch={batch} width={width} j_composed={j_composed}",
          flush=True)

    # ---- teacher cache + split (carry-through style) ----
    if run_mode == "full":
        cache_arg = teacher_cache_arg or TEACHER_CACHE_FULL
        cache_path = v3._resolve_teacher_cache(cache_arg)
    else:
        cache_path = (v3._resolve_teacher_cache(teacher_cache_arg)
                      if teacher_cache_arg
                      else _resolve_smoke_cache(SMOKE_N_TRAIN + SMOKE_N_HELD))
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[graded] teacher {cache_path.name}: {V_cache} concepts x {X.shape[1]}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        if V_cache < n_tr_target + n_he_target:
            raise RuntimeError(f"teacher cache too small for smoke: {V_cache}")
        n_tr, n_he = n_tr_target, n_he_target
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = V_cache - n_he
    tr_idx, he_idx = perm[:n_tr], perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    names_he = [ids[i] for i in he_idx]
    print(f"[graded] split train={n_tr} held={n_he}", flush=True)

    # ---- PHASE A: train + encode BOTH paired arms ----
    hard_code, hard_diag, hard_geom = _train_encode_arm(
        "HARD_STE", HARD_ARM, Xtr, Xhe, art_dir, out_dir, steps, batch, width,
        ckpt_every, dense_every, quick_sub, quick_pairs, traj_pairs, seed, device,
        warmup, min_step_for_best, t0)
    _emit_heartbeat(out_dir, 0, EXPECTED_N_UNITS, time.perf_counter() - t0,
                    extra={"stage": "trained_HARD_STE"})
    graded_code, graded_diag, graded_geom = _train_encode_arm(
        "GRADED", GRADED_ARM, Xtr, Xhe, art_dir, out_dir, steps, batch, width,
        ckpt_every, dense_every, quick_sub, quick_pairs, traj_pairs, seed, device,
        warmup, min_step_for_best, t0)
    _emit_heartbeat(out_dir, 0, EXPECTED_N_UNITS, time.perf_counter() - t0,
                    extra={"stage": "trained_GRADED"})

    kb_h, blk_h, m_h = hard_geom
    kb_g, blk_g, m_g = graded_geom

    # control codes.
    gen_ctrl = torch.Generator().manual_seed(seed + 1)
    rand_hard = v11._random_code_for_arm("sign", n_he, kb_h, blk_h, m_h, gen_ctrl)
    rand_graded = v11._random_code_for_arm("gsbc", n_he, kb_g, blk_g, m_g, gen_ctrl)
    cp_cap = min(n_he, charpos_cap)
    charpos_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, kb_h)

    # ---- META_RULE_AF arms-must-differ (float32 bytes; graded is fractional) ----
    digests = {
        "HARD_STE": _code_digest(hard_code),
        "GRADED": _code_digest(graded_code),
        "CHARPOS": _code_digest(charpos_codes),
        "RANDOM_HARD": _code_digest(rand_hard),
        "RANDOM_GRADED": _code_digest(rand_graded),
    }
    names = list(digests)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            if digests[names[a]] == digests[names[b]]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: "
                    f"{names[a]}/{names[b]} identical")

    # ---- PHASE B: ship-metric + algebra units ----
    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 2)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[graded] unit {len(per_unit)}/{EXPECTED_N_UNITS} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), EXPECTED_N_UNITS,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    cp_Xhe = Xhe[:cp_cap]
    # semantic (cosine_to_gold via hi80_cos + ret_agree10 vs teacher).
    _run_unit(v3._semantic_unit, "HARD_STE", hard_code, hard_code,
              Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "GRADED", graded_code, graded_code,
              Xhe, Xhe, 0, final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, "CHARPOS", charpos_codes, charpos_codes,
              cp_Xhe, cp_Xhe, 0, final_pairs, seed + 3)

    # keyed algebra (arm-appropriate: sbc for hard, gsbc_circconv for graded).
    _run_unit(v11._keyed_for_arm, "sign", "RANDOM_HARD", rand_hard, kb_h, blk_h,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "gsbc", "RANDOM_GRADED", rand_graded, kb_g, blk_g,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "sign", "HARD_STE", hard_code, kb_h, blk_h,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "sign", "HARD_STE", hard_code, kb_h, blk_h,
              j_composed, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "gsbc", "GRADED", graded_code, kb_g, blk_g,
              J_ISO, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "gsbc", "GRADED", graded_code, kb_g, blk_g,
              j_composed, n_trials, gen_eval, device)
    _run_unit(v11._keyed_for_arm, "sign", "HARD_STE", hard_code, kb_h, blk_h,
              J_ISO, n_trials, gen_eval, device, shuffled_key=True)
    _run_unit(v11._keyed_for_arm, "gsbc", "GRADED", graded_code, kb_g, blk_g,
              J_ISO, n_trials, gen_eval, device, shuffled_key=True)

    # ---- assemble paired ship dict ----
    h_sem = v3._by_unit(per_unit, "semantic", "HARD_STE")
    g_sem = v3._by_unit(per_unit, "semantic", "GRADED")
    cp_sem = v3._by_unit(per_unit, "semantic", "CHARPOS")
    h_iso = v3._by_unit(per_unit, "keyed", "HARD_STE", J_ISO)
    h_comp = v3._by_unit(per_unit, "keyed", "HARD_STE", j_composed)
    g_iso = v3._by_unit(per_unit, "keyed", "GRADED", J_ISO)
    g_comp = v3._by_unit(per_unit, "keyed", "GRADED", j_composed)
    charpos_ra = float(cp_sem["ret_agree10"]) if cp_sem else float("nan")
    hard_ra = float(h_sem["ret_agree10"])
    graded_ra = float(g_sem["ret_agree10"])
    ship = {
        "hard_ret_agree10": hard_ra,
        "graded_ret_agree10": graded_ra,
        "ret_agree10_lift": graded_ra - hard_ra,
        "hard_cosine_to_gold": float(h_sem["hi80_cos"]),
        "graded_cosine_to_gold": float(g_sem["hi80_cos"]),
        "hard_cosine_calib_err": float(h_sem["hi80_calib_err"]),
        "graded_cosine_calib_err": float(g_sem["hi80_calib_err"]),
        "hard_spearman_all": float(h_sem["spearman_all"]),
        "graded_spearman_all": float(g_sem["spearman_all"]),
        "hard_isolated_roundtrip": float(h_iso["acc_at1"]),
        "graded_isolated_roundtrip": float(g_iso["acc_at1"]),
        "hard_composed_roundtrip": float(h_comp["acc_at1"]),
        "graded_composed_roundtrip": float(g_comp["acc_at1"]),
        "j_composed": int(j_composed),
        "charpos_ret_agree10": charpos_ra,
        "baseline_in_band": bool(0.05 < charpos_ra < 0.95)
        if not math.isnan(charpos_ra) else False,
    }

    verdict, verdict_msg = _verdict(per_unit, ship, EXPECTED_N_UNITS, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": "mlp", "mlp_hidden": width,
        "hard_arm": {"mode": HARD_ARM[0], "kb": kb_h, "blk_l": blk_h, "m": m_h,
                     "recipe": HARD_ARM[4], "algebra": "sbc"},
        "graded_arm": {"mode": GRADED_ARM[0], "kb": kb_g, "blk_l": blk_g, "m": m_g,
                       "recipe": GRADED_ARM[4], "algebra": "gsbc_circconv",
                       "select_tau": v11.SELECT_TAU, "tau_hi": v11.TAU_HI,
                       "tau_lo": v11.TAU_LO, "anneal_frac": v11.ANNEAL_FRAC,
                       "cons_weight": v11.CONS_WEIGHT, "rank_weight": v11.RANK_WEIGHT,
                       "anchor_weight": v11.ANCHOR_WEIGHT},
        "objective": "IN_BATCH-RKD paired: hard-block-STE (sign) vs annealed "
                     "graded-GSBC (gsbc,full: soft->hard STE + soft/hard "
                     "consistency + listwise-rank + absolute-cosine anchor); "
                     "REUSES v11._train_student_v11 verbatim (landed HARD_PASS "
                     "code path)",
        "steps": steps, "batch": batch, "warmup_steps": warmup,
        "min_step_for_best": min_step_for_best,
        "j_iso": J_ISO, "j_composed": j_composed,
        "teacher_cache": cache_path.name, "teacher_n_concepts": V_cache,
        "n_train": n_tr, "n_held": n_he,
        "ship": ship,
        "train_diag": {"hard": {k: hard_diag[k] for k in
                                ("rkd_last", "best_dense_full", "best_step",
                                 "train_loss_floored", "best_ckpt_fallback_to_final")},
                       "graded": {k: graded_diag[k] for k in
                                  ("rkd_last", "cons_last", "rank_last",
                                   "anchor_last", "tau_last", "activefrac_last",
                                   "best_dense_full", "best_step",
                                   "train_loss_floored",
                                   "best_ckpt_fallback_to_final")}},
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) == EXPECTED_N_UNITS,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "paired: SBC_block_local_circular_convolution "
                               "(hard) + GSBC_block_circular_convolution (graded)",
        "progress_logging": "print_flush_true",
        "primary_metric_ret_agree10_lift": ship["ret_agree10_lift"],
        "graded_cosine_to_gold": ship["graded_cosine_to_gold"],
        "graded_composed_roundtrip": ship["graded_composed_roundtrip"],
        "baseline_in_band": ship["baseline_in_band"],
        "crlb_floor_computed": 0.901,
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 "
                                   "+ 0.25/K), K=128 -> 0.901 (block channel; "
                                   "ret-agreement lift is the discriminator, not "
                                   "a noise floor -- crlb is a reference bound)"),
        "discriminator_reachability": True,
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "hp_scope": {"GRADED": ["ret_agree10_lift", "cosine_to_gold",
                                "composed_roundtrip"]},
        "determinism": det,
        "prior_work_landed": {
            "v11_GSBC_FULL_ret_agree10_seed7": 0.3986,
            "v11_SIGN_BLOCK_ret_agree10_seed7": 0.2117,
            "v11_lift_seed7": 0.1869,
            "v11_GSBC_FULL_hi80_seed7": 0.8338,
            "v12_GSBC_EXPAND2X_ret_agree10_seed7": 0.6027,
            "source": "MEASURED@data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/"
                      "metrics.json + v12 seed7",
        },
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[graded] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast). Formula self-tests:
# anneal schedule + graded-code invariants + roundtrip + paired verdict bands.
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. anneal schedule: tau_hi -> tau_lo, monotone non-increasing, holds at lo.
    steps = 100
    taus = [v11._tau_at(s, steps, v11.ANNEAL_FRAC, v11.TAU_HI, v11.TAU_LO)
            for s in range(steps)]
    assert abs(taus[0] - v11.TAU_HI) < 1e-6, f"selftest: tau[0] {taus[0]} != TAU_HI"
    assert abs(taus[-1] - v11.TAU_LO) < 1e-6, f"selftest: tau[-1] {taus[-1]} != TAU_LO"
    for i in range(1, len(taus)):
        assert taus[i] <= taus[i - 1] + 1e-9, f"selftest: tau not monotone at {i}"
    anneal_end = int(round(v11.ANNEAL_FRAC * steps))
    assert abs(taus[min(anneal_end, steps - 1)] - v11.TAU_LO) < 1e-6, \
        "selftest: tau not held at TAU_LO after anneal window"

    # 2. graded code invariants: positive, unit-L1 per block, m active per block.
    kb, blk_l, m = 32, 128, 3
    z = torch.randn(8, kb * blk_l)
    code = v11._gsbc_code_from_z(z, kb, blk_l, m, v11.SELECT_TAU)
    cb = code.reshape(8, kb, blk_l)
    assert bool((cb >= -1e-6).all()), "selftest: graded code has negative entries"
    l1 = cb.sum(dim=-1)
    assert torch.allclose(l1, torch.ones_like(l1), atol=1e-4), \
        "selftest: graded block not unit-L1"
    nnz = (cb.abs() > 1e-8).sum(dim=-1)
    assert bool((nnz <= m).all()), f"selftest: graded block nnz > m ({int(nnz.max())})"

    # 3. hard block-STE code: exactly one bipolar winner per block.
    zb = torch.randn(8, 128 * 32)
    hard = v3._block_ste(zb, 128, 32).reshape(8, 128, 32)
    hnnz = (hard.abs() > 1e-8).sum(dim=-1)
    assert bool((hnnz == 1).all()), "selftest: hard block-STE not one-per-block"
    assert bool(((hard.abs() < 1e-8) | (torch.abs(hard.abs() - 1.0) < 1e-6)).all()), \
        "selftest: hard block-STE not bipolar {-1,0,1}"

    # 4. algebra roundtrip machinery (both algebras) on random codes -> acc ~ 1.
    gen = torch.Generator().manual_seed(3)
    rh = v11._random_code_for_arm("sign", 40, 128, 32, 1, gen)
    rg = v11._random_code_for_arm("gsbc", 40, 32, 128, 3, gen)
    uh = v11._keyed_for_arm("sign", "RANDOM_HARD", rh, 128, 32, 5, 20, gen, "cpu")
    ug = v11._keyed_for_arm("gsbc", "RANDOM_GRADED", rg, 32, 128, 5, 20, gen, "cpu")
    assert uh["acc_at1"] >= 0.98, f"selftest: sbc random roundtrip {uh['acc_at1']}"
    assert ug["acc_at1"] >= 0.98, f"selftest: gsbc random roundtrip {ug['acc_at1']}"
    # shuffled key must NOT retrieve.
    ush = v11._keyed_for_arm("gsbc", "GRADED", rg, 32, 128, 5, 20, gen, "cpu",
                             shuffled_key=True)
    assert ush["acc_at1"] <= 0.10, f"selftest: gsbc shuffled leak {ush['acc_at1']}"

    # 5. paired verdict bands (HP / MB / HF variants + integrity gates).
    def _units(pc_h=0.99, pc_g=0.99, sh_h=0.01, sh_g=0.01):
        u = [{"unit": f"semantic::{a}", "arm": a, "kind": "semantic"}
             for a in ("HARD_STE", "GRADED", "CHARPOS")]
        u += [
            {"unit": f"keyed::RANDOM_HARD::J{J_ISO}", "arm": "RANDOM_HARD",
             "kind": "keyed", "J": J_ISO, "acc_at1": pc_h, "hit_any_member": pc_h},
            {"unit": f"keyed::RANDOM_GRADED::J{J_ISO}", "arm": "RANDOM_GRADED",
             "kind": "keyed", "J": J_ISO, "acc_at1": pc_g, "hit_any_member": pc_g},
            {"unit": f"keyed::HARD_STE::J{J_ISO}", "arm": "HARD_STE",
             "kind": "keyed", "J": J_ISO, "acc_at1": 1.0, "hit_any_member": 1.0},
            {"unit": f"keyed::HARD_STE::J{J_COMPOSED_FULL}", "arm": "HARD_STE",
             "kind": "keyed", "J": J_COMPOSED_FULL, "acc_at1": 1.0,
             "hit_any_member": 1.0},
            {"unit": f"keyed::GRADED::J{J_ISO}", "arm": "GRADED",
             "kind": "keyed", "J": J_ISO, "acc_at1": 1.0, "hit_any_member": 1.0},
            {"unit": f"keyed::GRADED::J{J_COMPOSED_FULL}", "arm": "GRADED",
             "kind": "keyed", "J": J_COMPOSED_FULL, "acc_at1": 0.98,
             "hit_any_member": 0.98},
            {"unit": f"shuffled_key::HARD_STE::J{J_ISO}", "arm": "HARD_STE",
             "kind": "shuffled_key", "J": J_ISO, "acc_at1": sh_h,
             "hit_any_member": sh_h},
            {"unit": f"shuffled_key::GRADED::J{J_ISO}", "arm": "GRADED",
             "kind": "shuffled_key", "J": J_ISO, "acc_at1": sh_g,
             "hit_any_member": sh_g},
        ]
        return u

    def _ship(h_ra, g_ra, g_cos, g_comp, charpos=0.30, g_iso=1.0, h_comp=1.0,
              h_cos=0.83):
        return {"hard_ret_agree10": h_ra, "graded_ret_agree10": g_ra,
                "ret_agree10_lift": g_ra - h_ra, "graded_cosine_to_gold": g_cos,
                "hard_cosine_to_gold": h_cos,
                "graded_isolated_roundtrip": g_iso,
                "graded_composed_roundtrip": g_comp, "hard_composed_roundtrip": h_comp,
                "j_composed": J_COMPOSED_FULL, "charpos_ret_agree10": charpos,
                "baseline_in_band": (0.05 < charpos < 0.95)}

    v_hp, _ = _verdict(_units(), _ship(0.21, 0.40, 0.83, 0.98), EXPECTED_N_UNITS, "full")
    assert v_hp == "HARD_PASS", f"selftest: expected HARD_PASS got {v_hp}"
    # lift below HARD-FAIL ceiling -> HARD_FAIL.
    v_hf, _ = _verdict(_units(), _ship(0.21, 0.22, 0.83, 0.98), EXPECTED_N_UNITS, "full")
    assert v_hf == "HARD_FAIL", f"selftest: expected HARD_FAIL (no lift) got {v_hf}"
    # lift in (0.02, 0.05) -> MIDDLE.
    v_mb, _ = _verdict(_units(), _ship(0.21, 0.245, 0.83, 0.98), EXPECTED_N_UNITS, "full")
    assert v_mb == "MIDDLE_BAND", f"selftest: expected MIDDLE_BAND got {v_mb}"
    # graded cosine collapse -> HARD_FAIL.
    v_cc, m_cc = _verdict(_units(), _ship(0.21, 0.40, 0.70, 0.98), EXPECTED_N_UNITS, "full")
    assert v_cc == "HARD_FAIL" and "CALIB_COLLAPSE" in m_cc, f"got {v_cc}/{m_cc[:60]}"
    # graded algebra break -> HARD_FAIL.
    v_ab, m_ab = _verdict(_units(), _ship(0.21, 0.40, 0.83, 0.80), EXPECTED_N_UNITS, "full")
    assert v_ab == "HARD_FAIL" and "ALGEBRA_BREAK" in m_ab, f"got {v_ab}/{m_ab[:60]}"
    # algebra pos-ctrl broken -> HARD_FAIL regardless of ship.
    v_pc, m_pc = _verdict(_units(pc_g=0.5), _ship(0.21, 0.40, 0.83, 0.98),
                          EXPECTED_N_UNITS, "full")
    assert v_pc == "HARD_FAIL" and "LOSSLESS_PRIOR" in m_pc
    # shuffled leak -> HARD_FAIL.
    v_lk, m_lk = _verdict(_units(sh_g=0.5), _ship(0.21, 0.40, 0.83, 0.98),
                          EXPECTED_N_UNITS, "full")
    assert v_lk == "HARD_FAIL" and "SHUFFLED_KEY_LEAK" in m_lk
    # cardinality breach.
    v_cd, m_cd = _verdict(_units()[:5], _ship(0.21, 0.40, 0.83, 0.98),
                          EXPECTED_N_UNITS, "full")
    assert v_cd == "HARD_FAIL" and "CARDINALITY_BREACH" in m_cd
    # smoke machinery-OK.
    v_sm, _ = _verdict(_units(), _ship(0.48, 0.49, float("nan"), 1.0),
                       EXPECTED_N_UNITS, "smoke")
    assert v_sm == "HARD_PASS", f"selftest: expected smoke HARD_PASS got {v_sm}"

    print(f"[selftest] PASS (anneal schedule monotone + graded-code unit-L1/top-m "
          f"invariants + hard-block-STE one-per-block + BOTH-algebra roundtrip "
          f"pos-ctrl + shuffled-leak + paired verdict bands HP/MB/HF/calib/algebra"
          f"/posctrl/leak/cardinality/smoke) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Paired hard-block-STE vs graded-GSBC retrieval in the carry-through "
        "ship-metric regime (attack ret_agree10 gap; preserve cosine + algebra)."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p.add_argument("--n-dim", type=int, default=v3.N_DIM_DEFAULT)
    p.add_argument("--teacher-cache", default=None)
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_paired(args.run_mode, args.seed, args.device, args.n_dim,
                      args.teacher_cache)


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
            pass
        raise
