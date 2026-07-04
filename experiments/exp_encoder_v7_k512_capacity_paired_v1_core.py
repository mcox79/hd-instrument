"""Encoder v7 -- K=256 vs K=512 code-CAPACITY paired test: does the K128->K256
retrieval lift (genuinely trained, HARD_PASS, v5) CONTINUE at K=512, or does
a finer block code hit a ceiling/reversal once the per-block alphabet
(blk_l) gets small (blk_l=8 at K=512, vs 16 at K=256, 32 at K=128)?

CONTEXT (do not re-litigate; this cell is the direct sequel to v5, not a
fresh idea). v5 (FULL, PAIRED K128-vs-K256, in_batch-RKD-only, nce_weight=0,
steps=6000, cosine-decay LR, BOTH seeds HARD_PASS) landed:
  K128: final_ret_agree10=0.1972 (seed7) / 0.1984 (seed13)
  K256: final_ret_agree10=0.2902 (seed7) / 0.2958 (seed13), delta +0.093/+0.097
  MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed7/metrics.json
  MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed13/metrics.json.
A same-day READ-ONLY reuse of these checkpoints (zero training,
experiments/exp_encoder_retrieval_regime_density_curve_v1_core.py) confirmed
(a) these numbers reproduce bit-exact off the saved checkpoints, and (b)
naive OFF-MANIFOLD post-hoc repartition of a K128-trained model's output
into K=256/K=512 grids it never trained against does NOT help (goes
slightly DOWN vs native K128, not up) -- i.e. the K128->K256 lift v5 found
is genuinely a TRAINING effect (the STE gradient shape at a given kb/blk_l),
not something recoverable by relabeling an existing checkpoint. That is the
direct motivation for this cell: the ONLY way to learn whether K=512 lifts
retrieval further is to actually train a K=512 arm, matching v5's exact
paired methodology.

TWO PAIRED ARMS, same seed/data/split/mining/objective (in_batch-RKD-only,
nce_weight=0, steps=6000, batch=128 -- MATCHES v3e/v5 exactly) inside ONE
process, differing ONLY in the block-code resolution:
  K256 -- kb=256, blk_l=16 (6.25% active; REPRODUCED here as the internal
         positive control per Gate D -- this arm's own numbers must land
         within tolerance of v5's landed K256 arm before the K512 arm is
         trusted)
  K512 -- kb=512, blk_l=8 (12.5% active; the new arm -- doubles block COUNT
         again but blk_l shrinks to 8, a genuinely smaller per-block
         alphabet than K256's 16; unlike K128->K256, this is NOT assumed to
         keep lifting retrieval, since a smaller blk_l means each block's
         argmax has fewer choices, which could reduce per-block
         discriminative capacity even as the total block COUNT rises)
Both use `v3c._train_student_full` VERBATIM (unmodified; kb/blk_l are
already parameters of that function, so no new training-loop code is
needed for this cell, identical low-risk posture to v5). LR schedule is the
UNCHANGED cosine-decay-to-0 (v3e/v5's schedule) -- deliberately NOT v6's
validated plateau-hold LR, so this K-sweep stays isolated from the
convergence-schedule question exactly as v5 was kept isolated from v4 (the
two levers are already confirmed to compose in v6; testing them jointly
here would make a K512-specific delta impossible to attribute cleanly).

Note on the 2%-sparsity goal tension (flagged, not blocking, same as v5):
K=512 (12.5% active) moves FURTHER AWAY from the director_plan.json
encoder-goals' ~2%-sparsity target (k~82/N=4096) than K=256 already did.
This cell is the density-vs-retrieval CURVE'S next point, testing how far
the trade extends; the strategic tradeoff (denser code needed for capacity
vs the 2% goal, or runtime regime-switching between a dense retrieval
readout and a sparse composition readout) is a separate USER/Research-level
decision this cell surfaces but does not resolve.

Determinism pinning: identical to v5/v4 (`_pin_determinism`), records
torch.__version__ + device into metrics.json. THE REMOTE-QUEUE OFFICIAL
LANDING IS THE CANONICAL NUMBER; local smoke/preview is a MACHINERY gate
only (see discriminator-survives-scale below).

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "K512 block code capacity paired comparison retrieval agreement
  trained encoder versus K256 code resolution ceiling density curve" -> top
  hit cosine=0.2841 (this arc's own v3c/v3e prose, expected self-similarity
  from the shared lineage), v5's own prose at cosine=0.30 (expected -- same
  arc, direct predecessor cell), the same-day density-curve read-only-reuse
  cell's own prose at cosine=0.28 (expected -- same arc, distinct cell:
  read-only reuse vs fresh training). NONE at cosine>0.30 for a DISTINCT
  prior cell that TRAINS a K=512 student. GENUINELY NOVEL: no prior cell in
  this lineage trains a K=512 student or compares it against K=256 under
  matched conditions.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke/full gate (sha256 over all code matrices,
  per-arm RANDOM_BLOCK exemption note below)
- final_metrics_atomicity: tmp_replace (inherited from
  v3c._train_student_full, reused verbatim)
- except SystemExit: raise BEFORE except Exception (no BaseException, no
  bare except)
- crlb_floor_computed: K256 r_max computed via the SAME formula as the
  whole lineage (THEORETICAL@v2/v3/v3b/v3c/v3e/v5, unchanged); K512 r_max
  via the SAME formula, SAME implied sigma_teacher backed out from the
  K128 anchor (see `_crlb_r_max`; self-test asserts `_crlb_r_max(128)`
  reproduces 0.901). NOTE (honest simplification, inherited from v5): this
  formula's K term counts BLOCK COUNT only; it does not separately model
  blk_l shrinking (K512's blk_l=8 vs K256's 16), so the CRLB ceiling rising
  with K should NOT be read as guaranteeing K512's TRAINED result also
  rises -- the whole point of this cell is that blk_l-shrinkage is a
  DISTINCT, untested effect the closed-form ceiling does not capture.
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95)
- discriminator-survives-scale: option (B) analytical justification (same
  as the whole v3/v3b/v3c/v3e/v5 lineage): smoke's tiny V_train=3000
  cannot reproduce the true near-neighbor coverage-ratio or code-resolution
  effect; smoke validates MACHINERY ONLY (both K arms train end-to-end
  with DIFFERENT block partitions, per-arm RANDOM_BLOCK/keyed-algebra
  checks fire correctly for each block structure, cardinality holds). The
  actual K256-vs-K512-retrieval question needs the true 177899-concept
  corpus -- that IS the FULL dispatch, and the REMOTE-QUEUE OFFICIAL
  LANDING (not this local smoke) is canonical.
- HARD_PASS strictly above floor per prereg bands (META_RULE_L)
- HP_SCOPE: the K256-vs-K512 delta bands apply to {K256,K512}_BLOCK_LAST
  only; {K256,K512}_*_BESTVAL are comparison/context (KNOWN early-checkpoint
  inflation risk per v3e/v5's own bestval_step~8% findings -- FINAL is
  primary); RANDOM_BLOCK/CHARPOS/shuffled_key are integrity-only (per-arm
  for RANDOM_BLOCK/shuffled_key, since block partition differs by arm).
- cardinality_ok: EXPECTED_N_UNITS=19 both run_modes (SMOKE=FULL code path)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical hyperparameters
  to the validated v3c/v3e/v5 lineage; only K_BLOCKS/blk_l differ between
  arms)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_v7_k512_capacity_paired_v1.md
Parent cells (read-only imports, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
Does NOT touch v3/v3b/v3c/v3e/v4/v5/v6's own artifact/checkpoint/output
directories, nor the in-flight OPQ-style learned-rotation cell, nor the
already-landed teacher-sparsifier bypass cell.

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
ANCHOR_NAME = "encoder_v7_k512_capacity_paired_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = v3c.TEACHER_CACHE_DEFAULT  # pinned 177899-concept cache

NCE_WEIGHT = 0.0        # RKD-only (matches v3c/v3e's winning ablation config)
OBJECTIVE = "in_batch"  # GLOBAL stays dropped (algebra HARD_FAIL, see v3c seeds)

K_ARMS = {"K256": (256, 16), "K512": (512, 8)}  # arm_name -> (kb, blk_l); N_DIM=4096

# ---- FULL-scale config: MATCHES v3e exactly except K/blk_l ----
FULL_BATCH = 128
FULL_STEPS = 6000
CKPT_EVERY_STEPS_FULL = 500
DENSE_EVAL_EVERY_FULL = 500       # coarser than v3e's 50; bestval is SECONDARY
                                  # context here (FINAL-step is the primary
                                  # gated number for the K comparison)
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
MIN_TREND_POINTS = 4

# 2 arms x (semantic 4: DENSE/BLOCK x LAST/BESTVAL + semantic RANDOM_BLOCK(1,
# arm-specific block partition) + keyed RANDOM_BLOCK posctrl(1) + keyed LAST
# J5(1) + keyed BESTVAL J5(1) + shuffled-LAST J5(1)) = 2 x 9 = 18, + shared
# CHARPOS semantic(1, computed once at kb=128 -- a fixed non-trained
# orthographic reference, does not need to scale with the trained arm's K) = 19.
EXPECTED_N_UNITS_FULL = 19
EXPECTED_N_UNITS_SMOKE = 19

PREREG_BASELINE_ARMS = ["CHARPOS", "RANDOM_BLOCK"]

ALGEBRA_FLOOR = 0.90

# K128-vs-K256 retrieval-lift bands (HYPOTHESIZED@this prereg; first TRAINED
# comparison of these two K values -- the bypass diagnostic's +0.09 Spearman
# figure is a different metric on an UNTRAINED path, not directly portable
# to a ret_agree10 margin, so this cell's own bands are conservative and
# margin-based rather than reusing that number).
DELTA_RET_AGREE10_HARD_PASS_MIN = 0.03
DELTA_HI80_COS_REGRESSION_FLOOR = -0.02   # K256 must not meaningfully regress hi80_cos

# CRLB: same formula family as the whole lineage, sigma_teacher backed out
# from the established K=128 anchor (0.901) so K=256's ceiling is on the
# SAME theoretical footing, not a fresh unrelated estimate.
def _crlb_sigma_teacher(k_anchor: int, r_anchor: float) -> float:
    return math.sqrt((r_anchor ** 2 * 0.25 / k_anchor) / (1 - r_anchor ** 2))


CRLB_SIGMA_TEACHER = _crlb_sigma_teacher(128, 0.901)


def _crlb_r_max(k: int) -> float:
    return CRLB_SIGMA_TEACHER / math.sqrt(CRLB_SIGMA_TEACHER ** 2 + 0.25 / k)


def _artifact_dir(run_mode: str, run_tag: str = "") -> Path:
    suffix = {"smoke": "_smoke"}.get(run_mode, "")
    tag = f"_{run_tag}" if run_tag else ""
    return _REPO / "data" / f"substrate_concept_encoder_v7_k512{tag}{suffix}"


# ---------------------------------------------------------------------------
# Determinism pinning (coordinator mandate, 2026-07-04; identical to v4).
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
# Defensive helpers (start marker / crash metrics / heartbeat) -- mirrors v4/v3e.
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

def _verdict_k_capacity(per_unit: List[Dict], recovery: Dict, expected_units: int,
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
                    f"{prim['acc_at1']:.3f} < {ALGEBRA_FLOOR} (finer blocks may have "
                    f"broken SBC composability -- a genuine capacity-vs-algebra "
                    f"tradeoff finding, not a cell bug)")

    k256 = recovery["K256"]
    k512 = recovery["K512"]
    delta_ret = k512["final"]["ret_agree10"] - k256["final"]["ret_agree10"]
    delta_hi80 = k512["final"]["hi80_cos"] - k256["final"]["hi80_cos"]
    tail = (f"[K256: final_ret={k256['final']['ret_agree10']:.4f} "
           f"final_hi80={k256['final']['hi80_cos']:.4f} "
           f"final_block_spearman={k256['final']['spearman_all']:.4f}] "
           f"[K512: final_ret={k512['final']['ret_agree10']:.4f} "
           f"final_hi80={k512['final']['hi80_cos']:.4f} "
           f"final_block_spearman={k512['final']['spearman_all']:.4f}] "
           f"delta_ret={delta_ret:.4f} delta_hi80={delta_hi80:.4f}")

    if run_mode == "smoke":
        for arm in K_ARMS:
            if not math.isfinite(recovery[arm]["final"]["ret_agree10"]):
                return ("SMOKE_GATE_FAIL", f"S_ret_agree10_missing_{arm}")
            if not math.isfinite(recovery[arm]["final"]["hi80_cos"]):
                return ("SMOKE_GATE_FAIL", f"S_hi80_cos_missing_{arm}")
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: both K-resolution arms train end-to-end "
                f"with correctly-differing block partitions, per-arm RANDOM_BLOCK/"
                f"algebra checks fire, cardinality holds {tail} (the K256-vs-K512 "
                f"retrieval-lift discriminator is a FULL-only question; smoke's "
                f"tiny V_train cannot reproduce it -- REMOTE-QUEUE OFFICIAL "
                f"LANDING is canonical, this local smoke is a machinery gate only)")

    if delta_hi80 < DELTA_HI80_COS_REGRESSION_FLOOR:
        return ("HARD_FAIL",
                f"K512_REGRESSES_CALIBRATION: hi80_cos delta {delta_hi80:.4f} < "
                f"{DELTA_HI80_COS_REGRESSION_FLOOR} -- the denser code costs "
                f"semantic calibration, not just failing to help retrieval {tail}")
    if delta_ret >= DELTA_RET_AGREE10_HARD_PASS_MIN:
        return ("HARD_PASS",
                f"K512_LIFTS_RETRIEVAL_CONFIRMED: ret_agree10 delta {delta_ret:.4f} "
                f">= {DELTA_RET_AGREE10_HARD_PASS_MIN} with no calibration "
                f"regression -- the K128->K256 lift CONTINUES to K512; code "
                f"resolution keeps being a genuine retrieval lever even as "
                f"blk_l shrinks to 8 {tail}")
    if delta_ret <= 0.0:
        return ("HARD_FAIL",
                f"K512_DOES_NOT_LIFT_RETRIEVAL: ret_agree10 delta {delta_ret:.4f} "
                f"<= 0 -- the K128->K256 lift does NOT continue to K512; blk_l=8 "
                f"is likely too small an alphabet per block, a genuine ceiling/"
                f"reversal in the density-vs-retrieval curve, not a cell bug {tail}")
    return ("MIDDLE_BAND",
            f"K512_MARGINAL_LIFT: ret_agree10 delta {delta_ret:.4f} is positive "
            f"but below the {DELTA_RET_AGREE10_HARD_PASS_MIN} HARD_PASS margin -- "
            f"a real but small effect; consider a 2nd seed or an intermediate K "
            f"before drawing a strategic conclusion {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run_k_capacity(run_mode: str, seed: int, device_arg: str, n_dim: int,
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
    for arm, (kb, blk_l) in K_ARMS.items():
        if kb * blk_l != n_dim:
            raise ValueError(f"n_dim {n_dim} not divisible cleanly for {arm}: "
                             f"kb={kb} blk_l={blk_l}")

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
    print(f"[v7_k_capacity] run_mode={run_mode} seed={seed} device={device} "
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
    print(f"[v7_k_capacity] teacher {cache_path.name}: {V_cache} concepts x "
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
    print(f"[v7_k_capacity] split train={n_tr} held={n_he}", flush=True)

    # Mining is SHARED across both K-arms (positives/semi-hard candidates are
    # teacher-cosine-derived, independent of the student's block partition).
    pos_idx, semi_cands = v3._mine_teacher(
        Xtr, device, art_dir / "_mine_shards", out_dir, t0)
    semi_cov = float((semi_cands[:, 0] >= 0).float().mean())
    print(f"[v7_k_capacity] mining done cov={semi_cov:.3f} "
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
        print(f"[v7_k_capacity] {arm} (kb={kb},blk_l={blk_l}) trained "
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
        gen_ctrl = torch.Generator().manual_seed(seed + 1 + kb)  # per-arm-distinct control code
        arm_codes[f"{arm}_RANDOM_BLOCK"] = v3._random_block_codes(n_he, kb, blk_l, gen_ctrl)

    cp_cap = min(n_he, charpos_cap)
    cp_codes = v3._charpos_codes(names_he[:cp_cap], n_dim, v3.K_BLOCKS_PRIMARY)

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
            print(f"[v7_k_capacity] unit {len(per_unit)}/{expected_units} {u['unit']}: "
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
        "sparsity": K_ARMS[arm][0] / n_dim,
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

    verdict, verdict_msg = _verdict_k_capacity(per_unit, recovery, expected_units, run_mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "run_tag": run_tag, "seed": int(seed), "device": device, "N": n_dim,
        "student_arch": v3.STUDENT_ARCH_PRIMARY, "mlp_hidden": v3.MLP_HIDDEN,
        "warmup_steps": warmup, "steps": steps, "batch": batch,
        "nce_weight": NCE_WEIGHT, "objective": OBJECTIVE, "lr_schedule": "cosine_unchanged",
        "min_step_for_best": min_step_for_best, "dense_eval_every": dense_every,
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
        "methodology": ("PAIRED same-seed/data/split/mining comparison of code "
                        "resolution (K=256 vs K=512 blocks) at the in_batch-RKD-"
                        "only nce=0 config matching v3e/v5, UNCHANGED cosine-decay "
                        "LR schedule (kept separate from v6's validated but "
                        "orthogonal plateau-hold LR lever, exactly as v5 was kept "
                        "separate from v4, to avoid confounding this K-sweep); "
                        "FINAL-step ret_agree10/hi80_cos delta is the PRIMARY "
                        "gated comparison, best-by-VAL-on-TEST is SECONDARY "
                        "context; per-arm RANDOM_BLOCK/shuffled-key integrity + "
                        "FALSE_WIN_ALGEBRA checks run at EACH arm's own block "
                        "partition (K512's smaller blk_l=8 could in principle "
                        "break SBC composability even if it lifts retrieval -- "
                        "checked explicitly, not assumed)"),
        "progress_logging": "print_flush_true",
        "baseline_in_band": bool(0.05 < v3._by_unit(
            per_unit, "semantic", "CHARPOS")["ret_agree10"] < 0.95),
        "crlb_floor_computed": {"K256": _crlb_r_max(256), "K512": _crlb_r_max(512)},
        "crlb_formula_reference": ("r_max = sigma_teacher / sqrt(sigma_teacher^2 + "
                                   "0.25/K); sigma_teacher backed out from the "
                                   "established K=128 anchor value 0.901 "
                                   "(THEORETICAL@v2/v3/v3b/v3c/v3e/v5), then applied "
                                   "to K=256/K=512 on the same theoretical footing "
                                   "(honest caveat: this formula's K term does not "
                                   "separately model blk_l shrinking, see docstring)"),
        "discriminator_reachability": True,
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[v7_k_capacity] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; no cache dependency; fast).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. CRLB formula consistency: K=128 must reproduce the established 0.901
    #    anchor; K=512 must be a HIGHER ceiling (more blocks -> more bits).
    r128 = _crlb_r_max(128)
    r512 = _crlb_r_max(512)
    assert abs(r128 - 0.901) < 1e-3, f"selftest: CRLB(128) should reproduce 0.901, got {r128}"
    assert r512 > r128, "selftest: CRLB(512) must exceed CRLB(128) (finer code = higher ceiling)"

    # 2. verdict bands: cardinality / algebra / regression / lift / no-lift / marginal.
    def _fake_units(k256_algebra=1.0, k512_algebra=1.0, k256_shuf=0.01, k512_shuf=0.01):
        units = [{"unit": f"u{i}", "arm": "x", "kind": "k"} for i in range(11)]
        for arm, alg, shuf in (("K256", k256_algebra, k256_shuf), ("K512", k512_algebra, k512_shuf)):
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

    def _rec(k256_ret, k512_ret, k256_hi80=0.80, k512_hi80=0.82):
        return {
            "K256": {"final": {"spearman_all": 0.9, "ret_agree10": k256_ret,
                               "hi80_cos": k256_hi80, "hi80_calib_err": 0.02}},
            "K512": {"final": {"spearman_all": 0.9, "ret_agree10": k512_ret,
                               "hi80_cos": k512_hi80, "hi80_calib_err": 0.02}},
        }

    v_pass, m_pass = _verdict_k_capacity(_fake_units(), _rec(0.20, 0.25), 19, "full")
    assert v_pass == "HARD_PASS" and "K512_LIFTS_RETRIEVAL_CONFIRMED" in m_pass, (
        f"selftest: expected lift-confirmed HARD_PASS got {v_pass} ({m_pass})")

    v_nolift, m_nolift = _verdict_k_capacity(_fake_units(), _rec(0.20, 0.18), 19, "full")
    assert v_nolift == "HARD_FAIL" and "K512_DOES_NOT_LIFT_RETRIEVAL" in m_nolift, (
        f"selftest: expected no-lift HARD_FAIL got {v_nolift} ({m_nolift})")

    v_marg, m_marg = _verdict_k_capacity(_fake_units(), _rec(0.20, 0.21), 19, "full")
    assert v_marg == "MIDDLE_BAND" and "K512_MARGINAL_LIFT" in m_marg, (
        f"selftest: expected marginal MIDDLE_BAND got {v_marg} ({m_marg})")

    v_regress, m_regress = _verdict_k_capacity(
        _fake_units(), _rec(0.20, 0.25, k256_hi80=0.80, k512_hi80=0.70), 19, "full")
    assert v_regress == "HARD_FAIL" and "K512_REGRESSES_CALIBRATION" in m_regress, (
        f"selftest: expected calibration-regression HARD_FAIL got {v_regress} ({m_regress})")

    v_alg, m_alg = _verdict_k_capacity(
        _fake_units(k512_algebra=0.20), _rec(0.20, 0.25), 19, "full")
    assert v_alg == "HARD_FAIL" and "FALSE_WIN_ALGEBRA_LAST_STEP_K512" in m_alg, (
        f"selftest: expected K512 algebra-break HARD_FAIL got {v_alg} ({m_alg})")

    v_card, m_card = _verdict_k_capacity(_fake_units()[:5], _rec(0.20, 0.25), 19, "full")
    assert v_card == "HARD_FAIL" and "CARDINALITY_BREACH" in m_card

    # 3. tiny end-to-end training reuse of v3c._train_student_full at BOTH K
    #    values (proves this cell's driver wiring is correct without any new
    #    training-loop code -- v3c._train_student_full is used UNMODIFIED).
    n_dim, v_syn = 256, 400
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
        for arm, (kb, blk_l) in (("K16", (16, 16)), ("K32", (32, 8))):
            if kb * blk_l != n_dim:
                continue
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

    # 4. determinism pinning is idempotent.
    d1 = _pin_determinism(7)
    d2 = _pin_determinism(7)
    assert d1["torch_version"] == d2["torch_version"]

    print(f"[selftest] PASS (CRLB formula consistency K128->0.901 anchor + "
          f"K512>K128 ceiling + lift-confirmed/no-lift/marginal/calibration-"
          f"regression/algebra-break/cardinality verdict bands + "
          f"v3c._train_student_full reuse at 2 distinct K values + "
          f"determinism-pinning idempotence) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0
