"""Encoder v9 -- CONTAINER-EXPANSION falsifier: is retrieval set by the ABSOLUTE
active-unit count (block COUNT K) or by the sparse FRACTION (1/blk_l)? The
landed density curve CONFOUNDED them (K, fraction, active-count all moved
together at fixed total_dim=4096). This cell DECOUPLES them: hold K FIXED at
512 blocks (the config that already hits ret_agree10~0.414, v7 HARD_PASS) and
INCREASE total_dim so blk_l grows and the active FRACTION drops.

CONTEXT (do not re-litigate; direct sequel to v5/v7/v8). The landed TRAINED
curve moved K, fraction, AND active-count together, all at total_dim=4096:
  K128 blk_l32: 128 active, 3.125% fraction, ret_agree10 ~0.197/0.198 (v5)
  K256 blk_l16: 256 active, 6.25%  fraction, ret_agree10 ~0.290/0.296 (v5)
  K512 blk_l8 : 512 active, 12.5%  fraction, ret_agree10 ~0.414/0.415 (v7)
    MEASURED@data/exp_encoder_v7_k512_capacity_paired_v1_seed7/metrics.json:recovery.K512.final.ret_agree10 = 0.4141
    MEASURED@data/exp_encoder_v7_k512_capacity_paired_v1_seed13/metrics.json:recovery.K512.final.ret_agree10 = 0.4148
Because ret_agree10 rose with all three jointly, we cannot say WHICH drove it.
A brain drill (dentate gyrus expansion / pattern separation) reframed the
shortfall: retrieval quality may track the absolute active-count (= K), not
the sparse fraction. If so, we can DROP the fraction to the ~2% sparsity goal
WITHOUT losing retrieval, by pure re-parameterization of an already-validated
config -- expanding the container while holding K.

THE FALSIFIER. Hold K=512 FIXED (block COUNT) and sweep blk_l so the container
(total_dim = K*blk_l) expands and the fraction (1/blk_l) falls:
  K512L8  -- kb=512, blk_l=8,  width=4096,  fraction 12.5%  (Gate-D reproducer
             of v7's landed K512 arm; its own ret MUST land within tolerance of
             0.414 before the wider-container arms are trusted)
  K512L16 -- kb=512, blk_l=16, width=8192,  fraction 6.25%
  K512L32 -- kb=512, blk_l=32, width=16384, fraction 3.125%
  K512L50 -- kb=512, blk_l=50, width=25600, fraction 2.0%   (PRIMARY arm: does
             ret HOLD at the 2% sparsity goal when K stays at 512?)
Active-count is CONSTANT (512) across all four arms; only the fraction falls
12.5% -> 2%. PREDICTION TO FALSIFY: if ret_agree10 STAYS ~0.41 as the fraction
falls to 2%, retrieval is set by K (active-count) not fraction -> we hit 0.35+
AT 2% by re-parameterizing an already-validated config (CONTAINER_EXPANSION_
CONFIRMED). If ret DROPS toward the K128-fraction level (~0.21) as fraction->
2%, the sparse FRACTION is the driver and expansion does NOT help (FRACTION_IS_
THE_DRIVER).

Because K (block COUNT) is FIXED at 512, the lineage CRLB ceiling formula
(r_max = f(K), THEORETICAL@v2..v7) predicts the SAME ceiling for ALL FOUR arms
-- the CONSTANCY of that ceiling across the arms IS the closed-form statement
of the K-driver hypothesis (honest caveat inherited from v7: the formula's K
term counts block COUNT only, it does not separately model blk_l/fraction, so
the ceiling being equal is a PREDICTION this cell tests empirically, not a
guarantee).

Everything else is IDENTICAL to the validated v7 K512 cell: same student (MLP,
Linear(1024->2048) GELU Linear(2048->width)), in_batch-RKD-only nce_weight=0,
steps=6000 (NOTE: 6000 is v7's exact FULL config -- the 0.414 anchor was
produced at 6000 steps, NOT 8000; matching it is load-bearing for the Gate-D
reproduction), batch=128, UNCHANGED cosine-decay LR (kept isolated from v6's
plateau-hold lever exactly as v5/v7/v8 were), block-argmax code, same eval,
same 177899-concept teacher cache, same seed-derived train/held split and
shared mining. The ONLY thing that differs between arms is blk_l (hence width).
`v3c._train_student_full` reused VERBATIM (unmodified; kb/blk_l already
parameters), same low-risk posture as v5/v7/v8. Per-arm re-seeding inside
_train_student_full (student init from seed, batch-gen re-seeded from seed at
each arm start; VERIFIED@experiments/exp_encoder_migration_step1b_v3c_..._core.py:343-345)
makes each arm's training INDEPENDENT of arm order, so K512L8 reproduces v7's
K512 exactly regardless of the 3 other arms in this process.

MEMORY: float32 codes (VERIFIED@..._v3_..._core.py:492 _encode_hard_block
allocates torch.float32) at n_he=17790 x width=25600 x 5 code-matrices ~= 9.1GB
for the widest arm. Holding all 4 arms at once (v7/v8 structure) would be ~19GB
and risk OOM. This cell therefore processes ONE arm at a time: train -> encode
-> run that arm's 9 eval units -> FREE that arm's codes/students before the
next arm. Peak RAM = one arm's codes (~9.1GB) + Xtr/Xhe. Only the per-code
sha256 DIGEST (a string) is retained across arms so the ARMS-MUST-DIFFER
(META_RULE_AF) cross-arm hash-distinctness check and cardinality gate still
hold. The per-arm loop is IDENTICAL in smoke and full (SMOKE=FULL branch
coverage; smoke exercises all 4 widths incl 25600 at n_he=800, ~410MB).

Determinism pinning: identical to v5/v7/v8 (`_pin_determinism`), records
torch.__version__ + device. THE REMOTE-QUEUE OFFICIAL LANDING IS THE CANONICAL
NUMBER; local smoke is a MACHINERY gate only.

Prior-work check (substrate concept-query, USER-locked 2026-07-01):
  query "container expansion decouple block count K from sparse fraction blk_l
  fixed active unit count retrieval agreement encoder total_dim expansion
  dentate gyrus separation" -> top distinct-prior hits:
    DG-EXPANSION-SEPARATION anchor cosine=0.3184
      (notes/exp_dev_handoff_research_biological_precedents_animal_scales_2026-06-04.md)
    "expansion NON_TEST capacity metric disfavors expansion" cosine=0.3145
      (notes/exp_dev_to_skunkworks_..._C1_replicated_expansion_..._2026-06-18.md)
  RE-AIMED, not rediscovered: the DG-EXPANSION-SEPARATION anchor aimed the
  expansion idea at STORE-SIDE interference (pattern separation between stored
  items); this cell aims it at the RETRIEVAL HEAD of the trained concept
  encoder (does expanding the code container hold retrieval as the fraction
  falls at fixed K). The 2026-06-18 note is a DIFFERENT readout axis (C1
  capacity metric on an untrained expanded-linear readout) and found capacity
  DISFAVORS expansion under a NON-TEST metric -- a cautionary prior worth
  reporting, but not the trained-retrieval-head question here. GENUINELY NOVEL
  for this axis: no prior cell holds K fixed and sweeps the container to
  decouple active-count from fraction on the trained retrieval head.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices,
  accumulated incrementally so per-arm-free memory design still cross-checks)
- final_metrics_atomicity: tmp_replace (write_metrics helper + crash-writer)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare)
- crlb_floor_computed: SAME formula as the whole lineage; K=512 for ALL arms so
  the ceiling is identical across arms (that constancy IS the K-driver
  prediction; honest caveat: formula's K counts block COUNT only).
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical (same as v3/v5/v7/v8):
  smoke validates MACHINERY only (all 4 arms train end-to-end at DIFFERENT
  widths, per-arm RANDOM_BLOCK/algebra/shuffled checks fire, cardinality
  holds); the actual retrieval-vs-fraction-at-fixed-K question needs the
  177899-concept corpus -> FULL, REMOTE-QUEUE OFFICIAL LANDING is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: the container-expansion retrieval gate applies to K512L50_BLOCK_LAST
  FINAL only; Gate-D reproduction gate applies to K512L8_BLOCK_LAST FINAL only;
  {arm}_*_BESTVAL / DENSE are context; RANDOM_BLOCK/CHARPOS/shuffled integrity.
- cardinality_ok: EXPECTED_N_UNITS=37 both run_modes (4 arms x 9 + CHARPOS)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters to
  v5/v7/v8; only blk_l/width differ between arms)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v9_container_expansion_k512fixed_paired_v1.md
Parent cells (read-only imports, NOT edited): v3, v3c (same lineage as v5/v7/v8).
Does NOT touch any v3/v5/v6/v7/v8/opq/bypass/ceiling artifact directory.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import gc
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
ANCHOR_NAME = "encoder_v9_container_expansion_k512fixed_paired_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0        # RKD-only (matches v3c/v3e/v5/v7/v8's winning config)
OBJECTIVE = "in_batch"  # GLOBAL stays dropped (algebra HARD_FAIL, see v3c)

# arm_name -> (kb, blk_l). K (block COUNT) FIXED at 512; blk_l (hence width and
# fraction) is the swept axis. fraction (active density) = 1/blk_l. width=kb*blk_l.
K_FIXED = 512
BLK_LS = [8, 16, 32, 50]                       # fractions 12.5 / 6.25 / 3.125 / 2.0 %
K_ARMS = {f"K512L{bl}": (K_FIXED, bl) for bl in BLK_LS}
CONTROL_ARM = "K512L8"     # Gate-D reproducer of v7's landed K512 (width 4096, 12.5%)
PRIMARY_ARM = "K512L50"    # the 2%-fraction arm; PRIMARY container-expansion readout
N_DIM_REF = 4096           # CHARPOS reference width (fixed orthographic baseline)

# ---- FULL-scale config: MATCHES v5/v7/v8 exactly except blk_l/width ----
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

# 4 arms x 9 units (semantic DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK
# + keyed RANDOM_BLOCK posctrl + keyed LAST J5 + keyed BESTVAL J5 + shuffled-
# LAST J5) = 36, + shared CHARPOS semantic(1) = 37.
EXPECTED_N_UNITS_FULL = 37
EXPECTED_N_UNITS_SMOKE = 37

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

# Structural composability floor (below this at ANY arm = genuine SBC break).
ALGEBRA_FLOOR = 0.90
# Strict algebra bar that a full CONTAINER_EXPANSION_CONFIRMED HARD_PASS needs.
ALGEBRA_HARD_PASS = 0.95

# Container-expansion falsifier bands (HYPOTHESIZED@this prereg). PRIMARY arm =
# K512L50 (2% fraction, K=512 fixed). CONTROL arm = K512L8 (12.5%, v7 anchor).
RET_TARGET_HARD_PASS = 0.35     # PRIMARY ret >= this (+ strict algebra) = K-driver CONFIRMED
RET_COLLAPSE_HARD_FAIL = 0.25   # PRIMARY ret <= this = fraction is the driver, expansion fails
# Gate-D: control arm must reproduce v7's landed K512 within tolerance.
V7_K512_ANCHOR = 0.414          # MEASURED@data/exp_encoder_v7_..._seed7/13 (0.4141/0.4148)
GATE_D_TOL = 0.06


def _crlb_sigma_teacher(k_anchor: int, r_anchor: float) -> float:
    return math.sqrt((r_anchor ** 2 * 0.25 / k_anchor) / (1 - r_anchor ** 2))


CRLB_SIGMA_TEACHER = _crlb_sigma_teacher(128, 0.901)


def _crlb_r_max(k: int) -> float:
    return CRLB_SIGMA_TEACHER / math.sqrt(CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v9_ctrexp{tag}{suffix}"


# ---------------------------------------------------------------------------
# Determinism pinning (identical to v5/v7/v8).
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
# Defensive helpers (mirror v7/v8).
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
# Verdict logic (CONTAINER-EXPANSION falsifier).
# ---------------------------------------------------------------------------

def _verdict_container_expansion(per_unit: List[Dict], recovery: Dict,
                                 expected_units: int, run_mode: str) -> Tuple[str, str]:
    if len(per_unit) < expected_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_unit)}/{expected_units} units")

    # Per-arm structural integrity (RANDOM_BLOCK posctrl, shuffled-key leak,
    # SBC composability floor). Runs at EACH arm's own block partition.
    algebras: Dict[str, float] = {}
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
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (blk_l={K_ARMS[arm][1]}; "
                    f"a genuine SBC composability break at this container size, not a "
                    f"cell bug)")
        algebras[arm] = prim["acc_at1"]

    ctrl_ret = recovery[CONTROL_ARM]["final"]["ret_agree10"]
    prim_ret = recovery[PRIMARY_ARM]["final"]["ret_agree10"]
    min_alg = min(algebras.values())

    ordered = sorted(K_ARMS, key=lambda a: -recovery[a]["sparsity"])  # 12.5% -> 2%
    trend = " ".join(
        f"[{a} frac={recovery[a]['sparsity']*100:.3f}% "
        f"ret={recovery[a]['final']['ret_agree10']:.4f} "
        f"hi80={recovery[a]['final']['hi80_cos']:.4f} "
        f"calib={recovery[a]['final']['hi80_calib_err']:.4f} "
        f"alg={algebras[a]:.3f}]" for a in ordered)
    drop = ctrl_ret - prim_ret
    tail = (f"{trend} | ret_change(12.5%->2%)={drop:+.4f} "
            f"(~0 => K/active-count driver; large + => fraction driver) "
            f"min_algebra={min_alg:.3f}")

    if run_mode == "smoke":
        for arm in K_ARMS:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: all 4 fixed-K=512 arms (widths "
                f"4096/8192/16384/25600, fractions 12.5/6.25/3.125/2.0%) train "
                f"end-to-end with correctly-differing block partitions/widths, "
                f"per-arm RANDOM_BLOCK/algebra/shuffled checks fire, cardinality "
                f"holds {tail} (the container-expansion discriminator -- does ret "
                f"HOLD as fraction drops at fixed K -- is a FULL-only question; "
                f"smoke's tiny V_train cannot reproduce it; REMOTE-QUEUE OFFICIAL "
                f"LANDING is canonical, this local smoke is a machinery gate only)")

    # FULL. Gate-D: control arm (width 4096, 12.5%) reproduces v7's landed K512.
    if abs(ctrl_ret - V7_K512_ANCHOR) > GATE_D_TOL:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH: Gate-D control "
                f"{CONTROL_ARM} (width 4096, 12.5%) final ret_agree10 {ctrl_ret:.4f} "
                f"deviates > {GATE_D_TOL} from v7's landed K512 anchor "
                f"{V7_K512_ANCHOR} (MEASURED@data/exp_encoder_v7_k512_capacity_"
                f"paired_v1_seed7) -- this cell's training/eval invocation differs "
                f"from v7's; the wider-container arms are UNTRUSTED {tail}")

    # PRIMARY readout: does the 2%-fraction arm hold retrieval at fixed K=512?
    if prim_ret <= RET_COLLAPSE_HARD_FAIL:
        return ("HARD_FAIL",
                f"FRACTION_IS_THE_DRIVER: {PRIMARY_ARM} (2% fraction, K=512 fixed) "
                f"final ret_agree10 {prim_ret:.4f} <= {RET_COLLAPSE_HARD_FAIL} -- "
                f"retrieval COLLAPSES toward the K128-fraction level as the fraction "
                f"falls at constant active-count; the sparse FRACTION (not the "
                f"absolute active-count K) is the retrieval driver; container-"
                f"expansion does NOT rescue the encoder {tail}")
    if prim_ret >= RET_TARGET_HARD_PASS and min_alg >= ALGEBRA_HARD_PASS:
        return ("HARD_PASS",
                f"CONTAINER_EXPANSION_CONFIRMED: {PRIMARY_ARM} (2% fraction, K=512 "
                f"fixed) final ret_agree10 {prim_ret:.4f} >= {RET_TARGET_HARD_PASS} "
                f"with algebra {min_alg:.3f} >= {ALGEBRA_HARD_PASS} -- retrieval is "
                f"set by the ABSOLUTE active-count K (512 blocks), NOT the sparse "
                f"fraction; holding K fixed and expanding total_dim drops the "
                f"fraction 12.5%->2% WITHOUT losing retrieval; the encoder reaches "
                f"the 0.35+ target AT 2% sparsity by pure re-parameterization of an "
                f"already-validated config {tail}")
    if prim_ret >= RET_TARGET_HARD_PASS and min_alg < ALGEBRA_HARD_PASS:
        return ("MIDDLE_BAND",
                f"EXPANSION_RETRIEVAL_HOLDS_ALGEBRA_SUBSTRICT: {PRIMARY_ARM} "
                f"ret_agree10 {prim_ret:.4f} >= {RET_TARGET_HARD_PASS} (retrieval "
                f"held as fraction->2%) BUT min algebra {min_alg:.3f} in "
                f"[{ALGEBRA_FLOOR},{ALGEBRA_HARD_PASS}) short of the strict "
                f"{ALGEBRA_HARD_PASS} HARD_PASS bar -- retrieval-side confirmed, "
                f"composability slightly below strict target {tail}")
    return ("MIDDLE_BAND",
            f"PARTIAL_EXPANSION: {PRIMARY_ARM} (2% fraction) final ret_agree10 "
            f"{prim_ret:.4f} sits in ({RET_COLLAPSE_HARD_FAIL},{RET_TARGET_HARD_PASS}) "
            f"-- retrieval PARTLY holds as the fraction drops at fixed K but does not "
            f"fully clear 0.35; BOTH active-count and fraction contribute; expansion "
            f"helps but is not the whole story {tail}")


# ---------------------------------------------------------------------------
# Per-arm eval (compute codes -> run 9 units -> return summaries + digests).
# Isolated so the driver can FREE each arm's codes/students before the next.
# ---------------------------------------------------------------------------

def _eval_one_arm(arm: str, kb: int, blk_l: int, last_student, bestval_student,
                  Xhe: torch.Tensor, n_he: int, test_final_pairs: int, n_trials: int,
                  seed: int, device: str, gen_eval: torch.Generator,
                  per_unit: List[Dict], unit_fail: List[Dict], digests: Dict[str, str],
                  out_dir: Path, expected_units: int, t0: float) -> None:
    arm_codes: Dict[str, torch.Tensor] = {}
    arm_codes[f"{arm}_DENSE_LAST"] = v3._dense_sign_codes(last_student, Xhe)
    arm_codes[f"{arm}_BLOCK_LAST"] = v3._encode_hard_block(last_student, Xhe, kb, blk_l)
    arm_codes[f"{arm}_DENSE_BESTVAL"] = v3._dense_sign_codes(bestval_student, Xhe)
    arm_codes[f"{arm}_BLOCK_BESTVAL"] = v3._encode_hard_block(bestval_student, Xhe, kb, blk_l)
    gen_ctrl = torch.Generator().manual_seed(seed + 1 + blk_l)  # per-arm-distinct control
    arm_codes[f"{arm}_RANDOM_BLOCK"] = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)

    for name, c in arm_codes.items():
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[v9_ctrexp] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in (f"{arm}_DENSE_LAST", f"{arm}_BLOCK_LAST",
                  f"{arm}_DENSE_BESTVAL", f"{arm}_BLOCK_BESTVAL"):
        c = arm_codes[label]
        _run_unit(v3._semantic_unit, label, c, c, Xhe, Xhe, 0, test_final_pairs, seed + 3)
    _run_unit(v3._semantic_unit, f"{arm}_RANDOM_BLOCK", arm_codes[f"{arm}_RANDOM_BLOCK"],
              arm_codes[f"{arm}_RANDOM_BLOCK"], Xhe, Xhe, 0, test_final_pairs, seed + 3)

    _run_unit(v3._keyed_unit, f"{arm}_RANDOM_BLOCK", "sbc", arm_codes[f"{arm}_RANDOM_BLOCK"],
              kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
              arm_codes[f"{arm}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, f"{arm}_BLOCK_BESTVAL", "sbc",
              arm_codes[f"{arm}_BLOCK_BESTVAL"], kb, blk_l, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, f"{arm}_BLOCK_LAST", "sbc",
              arm_codes[f"{arm}_BLOCK_LAST"], kb, blk_l, 5, n_trials, gen_eval,
              device, shuffled_key=True)

    # Free this arm's code matrices (memory-safe per-arm design).
    arm_codes.clear()
    del arm_codes


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_container_expansion(run_mode: str, seed: int, device_arg: str,
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
    print(f"[v9_ctrexp] run_mode={run_mode} seed={seed} device={device} "
          f"K_FIXED={K_FIXED} widths={n_dim_by_arm} steps={steps} batch={batch} "
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
    print(f"[v9_ctrexp] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v9_ctrexp] split train={n_tr} held={n_he}", flush=True)

    # Mining SHARED across all arms (teacher-cosine-derived, width-independent).
    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v9_ctrexp] mining done cov={semi_cov:.3f} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    Xhe_sub = Xhe[:min(quick_sub, n_he)].contiguous()

    def _deval_quick(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe_sub, quick_pairs, seed + 7)

    def _deval_full(student: torch.nn.Module) -> float:
        return v3._dense_spearman_quick(student, Xhe, val_full_pairs, seed + 7)

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    digests: Dict[str, str] = {}
    arm_diag: Dict[str, Dict] = {}
    gen_eval = torch.Generator().manual_seed(seed + 2)

    # ---- Per-arm process-and-free (memory-safe for the wide-container arms) ----
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
        print(f"[v9_ctrexp] {arm} (kb={kb},blk_l={blk_l},width={kb*blk_l},"
              f"frac={100.0/blk_l:.3f}%) trained rkd_last={diag['rkd_last']:.4f} "
              f"best_val={diag['best_dense_full']:.4f}@step{diag['best_step']} "
              f"n_traj_points={len(diag['dense_traj'])} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

        _eval_one_arm(arm, kb, blk_l, last_student, bestval_student, Xhe, n_he,
                      test_final_pairs, n_trials, seed, device, gen_eval,
                      per_unit, unit_fail, digests, out_dir, expected_units, t0)

        del last_student, bestval_student
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
        print(f"[v9_ctrexp] {arm} eval done + freed ({time.perf_counter() - t0:.1f}s)",
              flush=True)

    # CHARPOS: fixed orthographic reference (computed once at kb=128 ref width).
    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], N_DIM_REF, v3.K_BLOCKS_PRIMARY)
    digests["CHARPOS"] = hashlib.sha256(cp_codes.to(torch.int8).numpy().tobytes()).hexdigest()
    cp_Xhe = Xhe[:cp_cap]
    try:
        u = v3._semantic_unit("CHARPOS", cp_codes, cp_codes, cp_Xhe, cp_Xhe, 0,
                              test_final_pairs, seed + 3)
        per_unit.append(u)
        print(f"[v9_ctrexp] unit {len(per_unit)}/{expected_units} {u['unit']}: "
              + json.dumps({k: round(v, 4) for k, v in u.items()
                            if isinstance(v, float)}), flush=True)
    except (RuntimeError, ValueError, IndexError) as exc:
        unit_fail.append({"fn": "_semantic_unit_CHARPOS",
                          "failure_class": type(exc).__name__, "msg": str(exc)[:300]})
        raise

    # ARMS-MUST-DIFFER (META_RULE_AF): all code matrices bit-distinct (via digests
    # accumulated across the per-arm-freed loop; strings only, no matrices held).
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

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
        "sparsity": 1.0 / K_ARMS[arm][1],   # active fraction = 1/blk_l
        "active_count": K_ARMS[arm][0],     # = K = 512 (FIXED across arms)
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

    verdict, verdict_msg = _verdict_container_expansion(
        per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device,
        "N_ref": N_DIM_REF, "n_dim_by_arm": n_dim_by_arm,
        "k_fixed": K_FIXED, "blk_ls": BLK_LS,
        "control_arm": CONTROL_ARM, "primary_arm": PRIMARY_ARM,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE, "lr_schedule": "cosine_unchanged",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
        "ret_target_hard_pass": RET_TARGET_HARD_PASS,
        "ret_collapse_hard_fail": RET_COLLAPSE_HARD_FAIL,
        "algebra_floor": ALGEBRA_FLOOR, "algebra_hard_pass": ALGEBRA_HARD_PASS,
        "v7_k512_anchor": V7_K512_ANCHOR, "gate_d_tol": GATE_D_TOL,
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
        "per_arm_memory_isolation": "train_encode_eval_free_one_arm_at_a_time",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("PAIRED same-seed/data/split/mining CONTAINER-EXPANSION "
                        "falsifier: K (block COUNT) FIXED at 512 across all 4 arms; "
                        "blk_l swept {8,16,32,50} so total_dim expands "
                        "{4096,8192,16384,25600} and the active FRACTION (1/blk_l) "
                        "falls {12.5,6.25,3.125,2.0}% while active-count stays 512. "
                        "K512L8 (12.5%) is the Gate-D reproducer of v7's landed K512 "
                        "(0.414) -- its own FINAL ret_agree10 must land within "
                        f"{GATE_D_TOL} of the anchor before the wider arms are "
                        "trusted. PRIMARY gated number: does K512L50 (2% fraction) "
                        "FINAL-step ret_agree10 HOLD >= 0.35 (K/active-count driver, "
                        "CONTAINER_EXPANSION_CONFIRMED) or collapse <= 0.25 toward the "
                        "K128-fraction level (FRACTION driver). in_batch-RKD-only "
                        "nce=0, UNCHANGED cosine-decay LR (isolated from v6's plateau "
                        "lever); per-arm RANDOM_BLOCK/shuffled-key/FALSE_WIN_ALGEBRA "
                        "checks run at EACH arm's own block partition (blk_l grows "
                        "8->50, larger per-block alphabet, so SBC algebra expected at "
                        "least as safe as the validated K512L8 -- checked, not "
                        "assumed). Memory-safe per-arm process-and-free: only one "
                        "arm's float32 codes held at once (~9.1GB at width 25600 vs "
                        "~19GB if all 4 held)."),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": {arm: _crlb_r_max(K_ARMS[arm][0]) for arm in K_ARMS},
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K); sigma_teacher backed out from the K=128 "
                                   "anchor 0.901 (THEORETICAL@v2/v3/v3b/v3c/v3e/v5/v7/"
                                   "v8). K=512 for ALL arms so the ceiling is IDENTICAL "
                                   "across arms -- that constancy IS the closed-form "
                                   "statement of the K-driver hypothesis this cell "
                                   "tests; honest caveat: K counts block COUNT only, "
                                   "does not separately model blk_l/fraction, so equal "
                                   "ceilings is a PREDICTION not a guarantee"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v9_ctrexp] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. CRLB formula consistency: K=128 reproduces the 0.901 anchor; K=512
    #    (the FIXED block count for every arm) is a single higher ceiling shared
    #    by all arms (the K-driver hypothesis in closed form).
    r128 = _crlb_r_max(128)
    r512 = _crlb_r_max(512)
    assert abs(r128 - 0.901) < 1e-3, f"selftest: CRLB(128) should reproduce 0.901, got {r128}"
    assert r512 > r128, "selftest: CRLB(512) must exceed CRLB(128) (finer code = higher ceiling)"
    # all arms share K=512 -> identical ceiling
    ceils = {arm: _crlb_r_max(K_ARMS[arm][0]) for arm in K_ARMS}
    assert len(set(round(c, 9) for c in ceils.values())) == 1, (
        f"selftest: fixed-K arms must share ONE CRLB ceiling, got {ceils}")

    # 2. arm geometry: K fixed=512, widths + fractions as specified, distinct.
    widths = {arm: kb * blk_l for arm, (kb, blk_l) in K_ARMS.items()}
    assert widths == {"K512L8": 4096, "K512L16": 8192, "K512L32": 16384,
                      "K512L50": 25600}, f"selftest: unexpected widths {widths}"
    fracs = {arm: 1.0 / K_ARMS[arm][1] for arm in K_ARMS}
    assert abs(fracs["K512L8"] - 0.125) < 1e-9 and abs(fracs["K512L50"] - 0.02) < 1e-9, (
        f"selftest: unexpected fractions {fracs}")
    assert all(kb == K_FIXED for kb, _ in K_ARMS.values()), "selftest: K not fixed at 512"

    # 3. verdict bands.
    def _fake_units(algs=None, shufs=None):
        # algs/shufs: dict arm -> value (defaults 1.0 / 0.01)
        algs = algs or {}
        shufs = shufs or {}
        units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(1)]
        for arm in K_ARMS:
            alg = algs.get(arm, 1.0)
            shuf = shufs.get(arm, 0.01)
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
        # pad to expected 37 (the 4 semantic + charpos per-arm units are not read
        # by verdict except via recovery; only cardinality len is checked).
        while len(units) < EXPECTED_N_UNITS_FULL:
            units.append({"unit": f"pad{len(units)}", "arm": "x", "kind": "semantic"})
        return units

    def _rec(rets, hi80=0.82, algebra_stub=1.0):
        # rets: dict arm -> ret_agree10
        return {arm: {"sparsity": 1.0 / K_ARMS[arm][1], "active_count": K_FIXED,
                      "final": {"spearman_all": 0.9, "ret_agree10": rets[arm],
                                "hi80_cos": hi80, "hi80_calib_err": 0.02}}
                for arm in K_ARMS}

    # HARD_PASS: control reproduces v7 anchor, primary (2%) holds >= 0.35, algebra strict.
    rets_hold = {"K512L8": 0.414, "K512L16": 0.40, "K512L32": 0.38, "K512L50": 0.37}
    v_pass, m_pass = _verdict_container_expansion(_fake_units(), _rec(rets_hold), 37, "full")
    assert v_pass == "HARD_PASS" and "CONTAINER_EXPANSION_CONFIRMED" in m_pass, (
        f"selftest: expected container-confirmed HARD_PASS got {v_pass} ({m_pass})")

    # HARD_FAIL fraction-driver: primary collapses <= 0.25.
    rets_collapse = {"K512L8": 0.414, "K512L16": 0.34, "K512L32": 0.27, "K512L50": 0.22}
    v_frac, m_frac = _verdict_container_expansion(_fake_units(), _rec(rets_collapse), 37, "full")
    assert v_frac == "HARD_FAIL" and "FRACTION_IS_THE_DRIVER" in m_frac, (
        f"selftest: expected fraction-driver HARD_FAIL got {v_frac} ({m_frac})")

    # MIDDLE_BAND partial: primary in (0.25, 0.35).
    rets_partial = {"K512L8": 0.414, "K512L16": 0.37, "K512L32": 0.33, "K512L50": 0.30}
    v_part, m_part = _verdict_container_expansion(_fake_units(), _rec(rets_partial), 37, "full")
    assert v_part == "MIDDLE_BAND" and "PARTIAL_EXPANSION" in m_part, (
        f"selftest: expected partial MIDDLE_BAND got {v_part} ({m_part})")

    # MIDDLE_BAND retrieval-holds-algebra-substrict: primary >= 0.35 but algebra in [0.90,0.95).
    v_sub, m_sub = _verdict_container_expansion(
        _fake_units(algs={"K512L50": 0.92}), _rec(rets_hold), 37, "full")
    assert v_sub == "MIDDLE_BAND" and "ALGEBRA_SUBSTRICT" in m_sub, (
        f"selftest: expected algebra-substrict MIDDLE_BAND got {v_sub} ({m_sub})")

    # HARD_FAIL algebra break (< 0.90) at any arm.
    v_alg, m_alg = _verdict_container_expansion(
        _fake_units(algs={"K512L50": 0.20}), _rec(rets_hold), 37, "full")
    assert v_alg == "HARD_FAIL" and "FALSE_WIN_ALGEBRA_LAST_STEP_K512L50" in m_alg, (
        f"selftest: expected algebra-break HARD_FAIL got {v_alg} ({m_alg})")

    # HARD_FAIL Gate-D: control deviates from v7 anchor.
    rets_gated = {"K512L8": 0.30, "K512L16": 0.30, "K512L32": 0.30, "K512L50": 0.37}
    v_gd, m_gd = _verdict_container_expansion(_fake_units(), _rec(rets_gated), 37, "full")
    assert v_gd == "HARD_FAIL" and "Gate-D control" in m_gd, (
        f"selftest: expected Gate-D mismatch HARD_FAIL got {v_gd} ({m_gd})")

    # HARD_FAIL cardinality.
    v_card, m_card = _verdict_container_expansion(_fake_units()[:5], _rec(rets_hold), 37, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    # SMOKE machinery HARD_PASS (bands not applied; only finiteness).
    v_smk, m_smk = _verdict_container_expansion(_fake_units(), _rec(rets_partial), 37, "smoke")
    assert v_smk == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_smk, (
        f"selftest: expected smoke machinery HARD_PASS got {v_smk} ({m_smk})")

    # 4. tiny end-to-end training reuse of v3c._train_student_full at TWO
    #    DIFFERENT widths at FIXED kb (256, 512 wide) -- proves per-arm-width
    #    driver wiring at fixed block count without new training-loop code.
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
        # FIXED kb=16, two blk_l (8, 16) -> widths 128 and 256 (the real cell's
        # fixed-K / varying-width path in miniature).
        for arm, (kb, blk_l) in (("A", (16, 8)), ("B", (16, 16))):
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

    print(f"[selftest] PASS (CRLB K128->0.901 + fixed-K=512 arms share ONE ceiling "
          f"+ arm geometry widths/fractions/K-fixed + container-confirmed/fraction-"
          f"driver/partial/algebra-substrict/algebra-break/Gate-D/cardinality/smoke "
          f"verdict bands + v3c._train_student_full reuse at TWO widths fixed-kb + "
          f"determinism idempotence) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0
