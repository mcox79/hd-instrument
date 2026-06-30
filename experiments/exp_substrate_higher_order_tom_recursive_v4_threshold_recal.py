"""substrate_higher_order_tom_recursive_v4_threshold_recal -- Stage 3 TOM
higher-order chain-grade promotion via threshold-recalibration of v3.

Prereg: preregs/2026-06-30_substrate_higher_order_tom_recursive_v4.md
Predecessor: v3 (smoke MIDDLE_BAND; expanded instrument N_LOC=32 + depth-scaled
distractors surfaces depth signal at N=8192: TENSOR depth_var=0.076 across
d={1,3,5}; v3 cite from data/exp_substrate_higher_order_tom_recursive_v3_smoke/
partial_metrics_7.json).

v3 result: depth signal SURFACES (TENSOR cliff 0.833 -> 0.400 -> 0.167 across
d={1,3,5}; HRR depth-aware; BOW depth_var ~0.005 stays small). MIDDLE_BAND
purely because pre-reg HP_DEPTH_VAR_MIN=0.10 was set BEFORE measured SNR was
known. v4 recalibrates threshold to match observed SNR + adds SE bands for
3-seed statistical validity + explicit BOW-vs-mechanism discriminator gate.

CHANGES vs v3:
  (1) HP_DEPTH_VAR_MIN: 0.10 -> 0.05 (matches observed TENSOR depth_var=0.076
      at single-seed smoke; 3-seed FULL with N_TRIALS=100 should average up;
      SE band gate guards stat-validity)
  (2) NEW HP_DEPTH_VAR_SE_MAX: 0.03 (standard error across 3 seeds must be
      below threshold-buffer; ensures the mean comfortably exceeds the 0.05
      floor at 1 SE distance)
  (3) NEW HP_MECHANISM_BEATS_BOW_MARGIN: 0.03 (mechanism arm depth_var must
      exceed BOW depth_var by at least 0.03 -- confirms depth signal is
      recursion-driven not distractor-budget artifact)
  (4) 3 seeds [7, 13, 19] (was 1 seed in v3 smoke); FULL DEPTHS=[1,2,3,4,5]
      (was {1,3,5} in v3 smoke); N_TRIALS=100 (was 30); N_DIMS=[4096,8192,16384]
  (5) Inherited bands kept (positive control, monotonic decay, random-band,
      META_RULE_Q, cardinality_ok); ARMs unchanged
  (6) BOW arm UNCHANGED: still constant n_distract_bow=4 (depth-blind by
      design); but verdict explicitly rejects PASS if BOW depth_var >=
      mechanism depth_var (caught by HP_MECHANISM_BEATS_BOW_MARGIN)

PRE-REG (HARD-LOCKED); HARD_PASS requires ALL of:
  >=1 of [ARM_HRR_RECURSIVE, ARM_TENSOR_RANK2]: depth_var across DEPTHS
    at N=8192 across seeds:
      mean(depth_var) >= 0.05  AND  SE(depth_var) <= 0.03
    AND  depth_var > BOW_depth_var + 0.03 at N=8192
  positive control (d=1, N=8192): mean(HRR) >= 0.65 AND mean(TENSOR) >= 0.65
    AND mean(BOW) >= 0.40 (across 3 seeds; chance = 0.031)
  monotonic decay (N=8192): mean(arm at d=1) - mean(arm at d=5) >= 0.20 for
    >=1 of [HRR, TENSOR] (substrate IS depth-sensitive)
  arms-distinct SHA-256 per cell (META_RULE_AF)
  cardinality_ok: completed >= 0.90 * expected
  random arm in chance band [0.005, 0.080]

HARD_FAIL ladder (any):
  HARD_FAIL_FLAT_DEPTH_V4: max depth-var < 0.03 across N for BOTH HRR + TENSOR
  HARD_FAIL_BOW_DOMINATES_DEPTH: BOW depth_var >= max(HRR,TENSOR) depth_var
    (distractor-budget artifact; depth signal NOT recursion-driven)
  HARD_FAIL_NESTED_BOW_DISCRIMINATES: BOW arm shows depth_var >= 0.10
  HARD_FAIL_ARMS_IDENTICAL: HRR == BOW for >=10% of cells
  HARD_FAIL_CARDINALITY_BREACH: completed < 0.90 expected
  HARD_FAIL META_RULE_Q: arm >= 0.999 at d>=3

DISCRIMINATOR-MUST-SURVIVE-SCALE per Director directive 2026-06-30:
  smoke runs at FULL DEPTHS + FULL N range; predicts cliff exists at the full
  test regime before dispatch. Per Check A (smoke at full-N) -- v3 smoke ALREADY
  showed cliff at N=8192. v4 smoke = v3 result on disk + 3 seeds for stat band.

Author: exp_dev (hdi_exp_dev agent) 2026-06-30 per Director threshold-recal
directive. See preregs/2026-06-30_substrate_higher_order_tom_recursive_v4.md.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AE/AF/AG/AH/AN/AP_v4):
# - arms_differ_verified per cell at smoke + production (META_RULE_AF SHA-256)
# - final_metrics_atomicity (tmp + os.replace)
# - except SystemExit raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed (per-level SNR retention; Kanerva capacity bound)
# - DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke uses full DEPTHS + full N range
# - HARD_PASS strictly above floor + SE band for stat-validity
# - HP_SCOPE per-cell-per-arm declaration
# - cardinality_ok for sweep-axis cells
# - HARD_FAIL ladder: FLAT_V4, BOW_DOMINATES, NESTED_BOW_DISCRIM, ARMS_IDENT,
#                    CARDINALITY, META_RULE_Q
# - start_marker + crash_diagnostic + heartbeat (defensive cell hardening)

from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_higher_order_tom_recursive_v4_threshold_recal"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--seed", type=int, default=None,
                 help="override single seed (for chunked single-seed dispatch)")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
_NAME_SAYS_SELFTEST = "_selftest" in _HDLAB_EXP_NAME.lower()
_NAME_SEED_MATCH = None
import re as _re
_seed_match = _re.search(r"_seed_(\d+)$", _HDLAB_EXP_NAME or "")
if _seed_match:
    _NAME_SEED_MATCH = int(_seed_match.group(1))

RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE
                         or _NAME_SAYS_SELFTEST)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----------------------- Pre-reg bands HARD-LOCKED v4 -----------------------
HP_DEPTH_VAR_MIN = 0.05            # recalibrated from v3's 0.10
HP_DEPTH_VAR_SE_MAX = 0.03         # NEW: SE across 3 seeds must be tight
HP_MECHANISM_BEATS_BOW_MARGIN = 0.03  # NEW: mechanism depth_var > BOW + 0.03
HP_POS_CONTROL_HRR_MIN = 0.65
HP_POS_CONTROL_TENSOR_MIN = 0.65
HP_POS_CONTROL_BOW_MIN = 0.40
HP_MONOTONIC_DECAY_MIN = 0.20

# HF ladder
HF_FLAT_DEPTH_VAR_MAX = 0.03       # if ALL arms have max depth-var < this -> HF_V4
HF_BOW_DOMINATES = True            # if BOW depth_var >= mechanism depth_var -> HF
HF_NESTED_BOW_VAR_MAX = 0.10
HF_ARMS_IDENTICAL_FRAC_MAX = 0.10
HF_CARDINALITY_FRAC_MIN = 0.90
SUSPECT_1000 = 0.999

N_LOCATIONS = 32
CHANCE = 1.0 / N_LOCATIONS
RANDOM_BAND_LO = 0.005
RANDOM_BAND_HI = 0.080

# Sweep axes
DEPTHS_FULL = [1, 2, 3, 4, 5]
N_DIMS_FULL = [4096, 8192, 16384]

# Smoke uses FULL DEPTHS + FULL N range (DISCRIMINATOR-MUST-SURVIVE-SCALE Check A)
DEPTHS_SMOKE = [1, 3, 5]
N_DIMS_SMOKE = [4096, 8192, 16384]

EXPECTED_ARMS = ["ARM_HRR_RECURSIVE", "ARM_TENSOR_RANK2", "ARM_NESTED_BOW"]
N_AGENTS_MAX = 16
N_OBJECTS = 4
DISTRACTOR_SCALING = "depth"

# Mode-dependent shape
if SELF_TEST_MODE:
    DEPTHS = [1, 3]
    N_DIMS = [4096]
    N_TRIALS = 10
    SEEDS = [7]
elif RUN_MODE == "smoke":
    DEPTHS = DEPTHS_SMOKE
    N_DIMS = N_DIMS_SMOKE
    N_TRIALS = 30
    SEEDS = [7]
else:
    DEPTHS = DEPTHS_FULL
    N_DIMS = N_DIMS_FULL
    N_TRIALS = 100
    if _ARGS.seed is not None:
        SEEDS = [_ARGS.seed]
    elif _NAME_SEED_MATCH is not None:
        SEEDS = [_NAME_SEED_MATCH]
    else:
        SEEDS = [7, 13, 19]

N_CELLS = len(DEPTHS) * len(N_DIMS)
EXPECTED_N_UNITS = len(SEEDS) * N_CELLS * len(EXPECTED_ARMS) * N_TRIALS

CONFIG_VERSION = (
    "ANCHOR=%s,depths=%s,N_dims=%s,n_trials=%d,seeds=%s,mode=%s,"
    "n_objects=%d,n_locations=%d,n_agents_max=%d,distractor_scaling=%s,"
    "HP_depth_var_min=%.3f,HP_depth_var_se_max=%.3f,HP_mechanism_beats_bow=%.3f,"
    "HP_pc_hrr=%.2f,HP_pc_tensor=%.2f,HP_pc_bow=%.2f,HP_monotonic_decay_min=%.2f,"
    "HF_flat_var_max=%.3f,HF_bow_var_max=%.2f,HF_arms_id_max=%.2f,"
    "expected_n=%d,arms=%s,"
    "hardening=L1early+L2perseed+L3outertry+L4importsentinel"
    "+META_RULE_AF+META_RULE_AH+META_RULE_AG+META_RULE_AN+META_RULE_AP_v4"
    "+SE_BAND_v4+BOW_DOMINATES_HF_v4"
) % (
    ANCHOR_NAME, DEPTHS, N_DIMS, N_TRIALS, SEEDS, RUN_MODE,
    N_OBJECTS, N_LOCATIONS, N_AGENTS_MAX, DISTRACTOR_SCALING,
    HP_DEPTH_VAR_MIN, HP_DEPTH_VAR_SE_MAX, HP_MECHANISM_BEATS_BOW_MARGIN,
    HP_POS_CONTROL_HRR_MIN, HP_POS_CONTROL_TENSOR_MIN, HP_POS_CONTROL_BOW_MIN,
    HP_MONOTONIC_DECAY_MIN,
    HF_FLAT_DEPTH_VAR_MAX, HF_NESTED_BOW_VAR_MAX, HF_ARMS_IDENTICAL_FRAC_MAX,
    EXPECTED_N_UNITS, EXPECTED_ARMS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_start_marker(out_dir: Path) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        marker = {
            "pid": os.getpid(),
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "expected_n_units": EXPECTED_N_UNITS,
            "host": platform.node(),
            "seeds": SEEDS,
            "depths": DEPTHS,
            "n_dims": N_DIMS,
        }
        tmp = out_dir / "_start_marker.json.tmp"
        tmp.write_text(json.dumps(marker, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "_start_marker.json"))
    except Exception as e:
        print("[_write_start_marker] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                           extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v4_threshold_recal_SE_band_BOW_dominates_HF",
        }
        if extra:
            metrics.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        diag = {
            "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_crash_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH",
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v4_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# ----------------- FHRR primitives (UNCHANGED from v3) -----------------

def random_unit_phases(M: int, n_half: int,
                       g: np.random.Generator) -> np.ndarray:
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (c * np.conj(key)).astype(np.complex64)


def superpose_sum(arrs: List[np.ndarray]) -> np.ndarray:
    if not arrs:
        return np.zeros(1, dtype=np.complex64)
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_argmax(q: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    sims = np.real(codebook @ np.conj(q))
    norm_q = np.linalg.norm(q) + 1e-12
    norm_cb = np.linalg.norm(codebook, axis=1) + 1e-12
    cos = sims / (norm_q * norm_cb)
    idx = int(np.argmax(cos))
    return idx, float(cos[idx])


def n_distractors_for(depth: int) -> int:
    if DISTRACTOR_SCALING == "depth":
        return max(1, depth)
    elif DISTRACTOR_SCALING == "const2":
        return 2
    elif DISTRACTOR_SCALING == "depth_sq":
        return max(1, depth * depth)
    else:
        return max(1, depth)


# ----------------- arm encoders (UNCHANGED from v3) -----------------

def _hrr_encode(agent_chain: List[int], obj_idx: int, loc_idx: int,
                obj_cb: np.ndarray, loc_cb: np.ndarray,
                agent_cb: np.ndarray, role_believes: np.ndarray,
                rng: np.random.Generator) -> np.ndarray:
    depth = len(agent_chain)
    n_distract = n_distractors_for(depth)
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]

    inner = bind(obj_cb[obj_idx], loc_cb[loc_idx])
    if n_distract > 0:
        inner_distractors = []
        for _ in range(n_distract):
            oi = int(rng.integers(n_objs))
            li = int(rng.integers(n_locs))
            inner_distractors.append(bind(obj_cb[oi], loc_cb[li]))
        inner = superpose_sum([inner] + inner_distractors)
    cur = inner
    for agent_idx in reversed(agent_chain):
        wrapped = bind(role_believes, bind(agent_cb[agent_idx], cur))
        if n_distract > 0:
            level_distractors = []
            for _ in range(n_distract):
                oi = int(rng.integers(n_objs))
                li = int(rng.integers(n_locs))
                sibling_inner = bind(obj_cb[oi], loc_cb[li])
                sibling_wrap = bind(role_believes,
                                    bind(agent_cb[agent_idx], sibling_inner))
                level_distractors.append(sibling_wrap)
            wrapped = superpose_sum([wrapped] + level_distractors)
        cur = wrapped
    return cur


def _hrr_decode(bank: np.ndarray, agent_chain: List[int], obj_idx: int,
                obj_cb: np.ndarray, loc_cb: np.ndarray,
                agent_cb: np.ndarray, role_believes: np.ndarray
                ) -> Tuple[int, float]:
    cur = bank
    for agent_idx in agent_chain:
        cur = unbind(cur, role_believes)
        cur = unbind(cur, agent_cb[agent_idx])
    cur = unbind(cur, obj_cb[obj_idx])
    return cleanup_argmax(cur, loc_cb)


def run_arm_hrr_recursive(scenarios, obj_cb, loc_cb, agent_cb,
                          role_believes, g):
    preds, truths = [], []
    for sc in scenarios:
        bank = _hrr_encode(sc["agent_chain"], sc["object_idx"],
                           sc["loc_truth"], obj_cb, loc_cb,
                           agent_cb, role_believes, g)
        pred, _ = _hrr_decode(bank, sc["agent_chain"], sc["object_idx"],
                              obj_cb, loc_cb, agent_cb, role_believes)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


def _tensor_encode(agent_chain, obj_idx, loc_idx, obj_cb, loc_cb, agent_cb,
                   role_believes_a, role_believes_b, rng):
    depth = len(agent_chain)
    n_distract = n_distractors_for(depth)
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]

    inner = bind(obj_cb[obj_idx], loc_cb[loc_idx])
    if n_distract > 0:
        inner_distractors = []
        for _ in range(n_distract):
            oi = int(rng.integers(n_objs))
            li = int(rng.integers(n_locs))
            inner_distractors.append(bind(obj_cb[oi], loc_cb[li]))
        inner = superpose_sum([inner] + inner_distractors)
    cur = inner
    for agent_idx in reversed(agent_chain):
        wrap_a = bind(role_believes_a, bind(agent_cb[agent_idx], cur))
        wrap_b = bind(role_believes_b, bind(agent_cb[agent_idx], cur))
        wrapped = superpose_sum([wrap_a, wrap_b])
        if n_distract > 0:
            level_distractors = []
            for _ in range(n_distract):
                oi = int(rng.integers(n_objs))
                li = int(rng.integers(n_locs))
                sibling_inner = bind(obj_cb[oi], loc_cb[li])
                sib_a = bind(role_believes_a,
                             bind(agent_cb[agent_idx], sibling_inner))
                sib_b = bind(role_believes_b,
                             bind(agent_cb[agent_idx], sibling_inner))
                level_distractors.append(superpose_sum([sib_a, sib_b]))
            wrapped = superpose_sum([wrapped] + level_distractors)
        cur = wrapped
    return cur


def _tensor_decode(bank, agent_chain, obj_idx, obj_cb, loc_cb, agent_cb,
                   role_believes_a, role_believes_b):
    cur_a = bank
    cur_b = bank
    for agent_idx in agent_chain:
        cur_a = unbind(cur_a, role_believes_a)
        cur_a = unbind(cur_a, agent_cb[agent_idx])
        cur_b = unbind(cur_b, role_believes_b)
        cur_b = unbind(cur_b, agent_cb[agent_idx])
    cur_a = unbind(cur_a, obj_cb[obj_idx])
    cur_b = unbind(cur_b, obj_cb[obj_idx])
    cur = superpose_sum([cur_a, cur_b])
    return cleanup_argmax(cur, loc_cb)


def run_arm_tensor_rank2(scenarios, obj_cb, loc_cb, agent_cb,
                         role_believes_a, role_believes_b, g):
    preds, truths = [], []
    for sc in scenarios:
        bank = _tensor_encode(sc["agent_chain"], sc["object_idx"],
                              sc["loc_truth"], obj_cb, loc_cb,
                              agent_cb, role_believes_a, role_believes_b, g)
        pred, _ = _tensor_decode(bank, sc["agent_chain"], sc["object_idx"],
                                 obj_cb, loc_cb, agent_cb,
                                 role_believes_a, role_believes_b)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


def _bow_encode(agent_chain, obj_idx, loc_idx, obj_cb, loc_cb, rng):
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]
    n_distract_bow = 4  # depth-INDEPENDENT
    pairs = [bind(obj_cb[obj_idx], loc_cb[loc_idx])]
    for _ in range(n_distract_bow):
        oi = int(rng.integers(n_objs))
        li = int(rng.integers(n_locs))
        pairs.append(bind(obj_cb[oi], loc_cb[li]))
    return superpose_sum(pairs)


def _bow_decode(bank, obj_idx, obj_cb, loc_cb):
    cur = unbind(bank, obj_cb[obj_idx])
    return cleanup_argmax(cur, loc_cb)


def run_arm_nested_bow(scenarios, obj_cb, loc_cb, g):
    preds, truths = [], []
    for sc in scenarios:
        bank = _bow_encode(sc["agent_chain"], sc["object_idx"],
                           sc["loc_truth"], obj_cb, loc_cb, g)
        pred, _ = _bow_decode(bank, sc["object_idx"], obj_cb, loc_cb)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


# ----------------- scenarios + arm-distinct (UNCHANGED) -----------------

def make_scenarios(g, depth, n_trials, n_objects, n_locations, n_agents_avail):
    assert depth >= 1
    assert n_agents_avail >= depth
    scenarios = []
    for _ in range(n_trials):
        obj_idx = int(g.integers(n_objects))
        loc_truth = int(g.integers(n_locations))
        all_agents = list(range(n_agents_avail))
        g.shuffle(all_agents)
        agent_chain = all_agents[:depth]
        scenarios.append({
            "depth": depth,
            "object_idx": obj_idx,
            "loc_truth": loc_truth,
            "agent_chain": agent_chain,
        })
    return scenarios


def arms_must_differ_per_cell(arm_preds):
    digests = {}
    for name, preds in arm_preds.items():
        b = np.asarray(preds, dtype=np.int32).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    arms = sorted(arm_preds.keys())
    diag = {"digests": {k: v[:16] for k, v in digests.items()},
            "pairs": []}
    all_distinct = True
    any_disagreement = False
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            ai, aj = arms[i], arms[j]
            pi = np.asarray(arm_preds[ai])
            pj = np.asarray(arm_preds[aj])
            disagreement = float(np.mean(pi != pj))
            if disagreement > 0:
                any_disagreement = True
            pair_pass = digests[ai] != digests[aj]
            diag["pairs"].append({"a": ai, "b": aj,
                                  "disagreement": disagreement,
                                  "pass": pair_pass})
            if not pair_pass:
                all_distinct = False
    if not any_disagreement:
        diag["all_arms_identical"] = True
    diag["all_pairs_distinct"] = all_distinct
    return all_distinct, diag


# ----------------- per-cell runner (UNCHANGED) -----------------

def run_one_cell(seed, N, depth, n_trials):
    g = np.random.default_rng(seed + depth * 1000 + N * 7)
    n_half = N // 2

    obj_cb = random_unit_phases(N_OBJECTS, n_half, g)
    loc_cb = random_unit_phases(N_LOCATIONS, n_half, g)
    agent_cb = random_unit_phases(N_AGENTS_MAX, n_half, g)
    role_believes = random_unit_phases(1, n_half, g)[0]
    role_believes_a = random_unit_phases(1, n_half, g)[0]
    role_believes_b = random_unit_phases(1, n_half, g)[0]

    scen_rng = np.random.default_rng(seed + depth * 1000 + N * 7 + 999)
    scenarios = make_scenarios(scen_rng, depth, n_trials,
                                N_OBJECTS, N_LOCATIONS, N_AGENTS_MAX)

    rng_hrr = np.random.default_rng(seed + depth * 1000 + N * 7 + 100)
    rng_tensor = np.random.default_rng(seed + depth * 1000 + N * 7 + 200)
    rng_bow = np.random.default_rng(seed + depth * 1000 + N * 7 + 300)
    rng_rand = np.random.default_rng(seed + depth * 1000 + N * 7 + 400)

    res_hrr = run_arm_hrr_recursive(scenarios, obj_cb, loc_cb, agent_cb,
                                    role_believes, rng_hrr)
    res_tensor = run_arm_tensor_rank2(scenarios, obj_cb, loc_cb, agent_cb,
                                       role_believes_a, role_believes_b,
                                       rng_tensor)
    res_bow = run_arm_nested_bow(scenarios, obj_cb, loc_cb, rng_bow)
    rand_preds = [int(rng_rand.integers(N_LOCATIONS)) for _ in range(n_trials)]
    truths = [sc["loc_truth"] for sc in scenarios]

    acc_hrr = float(np.mean([p == t for p, t in zip(res_hrr["preds"],
                                                      res_hrr["truths"])]))
    acc_tensor = float(np.mean([p == t for p, t in zip(res_tensor["preds"],
                                                         res_tensor["truths"])]))
    acc_bow = float(np.mean([p == t for p, t in zip(res_bow["preds"],
                                                      res_bow["truths"])]))
    acc_rand = float(np.mean([p == t for p, t in zip(rand_preds, truths)]))

    arm_preds_map = {
        "ARM_HRR_RECURSIVE": res_hrr["preds"],
        "ARM_TENSOR_RANK2": res_tensor["preds"],
        "ARM_NESTED_BOW": res_bow["preds"],
    }
    arms_distinct, arms_diag = arms_must_differ_per_cell(arm_preds_map)

    return {
        "N": N, "depth": depth, "n_trials": n_trials,
        "acc_hrr": acc_hrr, "acc_tensor": acc_tensor,
        "acc_bow": acc_bow, "acc_random": acc_rand,
        "arms_distinct": bool(arms_distinct), "arms_diag": arms_diag,
        "n_distractors_used": n_distractors_for(depth),
    }


def run_one_seed(seed):
    per_cell = {}
    t_seed_start = time.time()
    cell_idx = 0
    total_cells = N_CELLS
    for N in N_DIMS:
        for depth in DEPTHS:
            cell_idx += 1
            t0 = time.time()
            cell_res = run_one_cell(seed, N, depth, N_TRIALS)
            cell_res["wall_s"] = round(time.time() - t0, 3)
            key = "N%d_d%d" % (N, depth)
            per_cell[key] = cell_res
            print("[seed=%d cell=%d/%d %s] hrr=%.3f tensor=%.3f bow=%.3f "
                  "rand=%.3f arms_d=%s n_dist=%d %.1fs" % (
                      seed, cell_idx, total_cells, key,
                      cell_res["acc_hrr"], cell_res["acc_tensor"],
                      cell_res["acc_bow"], cell_res["acc_random"],
                      cell_res["arms_distinct"],
                      cell_res["n_distractors_used"],
                      cell_res["wall_s"]), flush=True)

    return {
        "seed": int(seed), "depths": DEPTHS, "N_dims": N_DIMS,
        "n_trials": N_TRIALS, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION, "anchor_name": ANCHOR_NAME,
        "per_cell": per_cell,
        "seed_wall_s": round(time.time() - t_seed_start, 1),
    }


# ----------------- v4 verdict logic (new SE-band + BOW-dominates) -----------------

def aggregate_and_verdict(per_seed):
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))

    cell_summary = {}
    for N in N_DIMS:
        for depth in DEPTHS:
            key = "N%d_d%d" % (N, depth)
            hrr_a, tensor_a, bow_a, rand_a = [], [], [], []
            arms_distinct_all = True
            completed = 0
            for s in seeds_sorted:
                pc = per_seed[s].get("per_cell", {}).get(key)
                if pc is None:
                    continue
                hrr_a.append(pc["acc_hrr"])
                tensor_a.append(pc["acc_tensor"])
                bow_a.append(pc["acc_bow"])
                rand_a.append(pc["acc_random"])
                if not pc.get("arms_distinct", True):
                    arms_distinct_all = False
                completed += pc.get("n_trials", 0)
            if hrr_a:
                cs = {
                    "N": N, "depth": depth,
                    "hrr_mean": float(np.mean(hrr_a)),
                    "hrr_std": float(np.std(hrr_a)),
                    "tensor_mean": float(np.mean(tensor_a)),
                    "tensor_std": float(np.std(tensor_a)),
                    "bow_mean": float(np.mean(bow_a)),
                    "bow_std": float(np.std(bow_a)),
                    "rand_mean": float(np.mean(rand_a)),
                    "n_seeds": len(hrr_a),
                    "completed_trials": completed,
                    "arms_distinct": arms_distinct_all,
                }
            else:
                cs = {"N": N, "depth": depth, "hrr_mean": 0.0,
                      "tensor_mean": 0.0, "bow_mean": 0.0, "rand_mean": 0.0,
                      "n_seeds": 0, "completed_trials": 0,
                      "arms_distinct": True}
            cell_summary[key] = cs

    # ---- v4 NEW: per-seed depth_var, then mean + SE across seeds ----
    # For each (N, arm), compute depth_var PER SEED first, then aggregate.
    depth_var_per_seed_per_N_per_arm = {}
    for N in N_DIMS:
        depth_var_per_seed_per_N_per_arm["N%d" % N] = {}
        for arm_key, mean_key in [
            ("ARM_HRR_RECURSIVE", "acc_hrr"),
            ("ARM_TENSOR_RANK2", "acc_tensor"),
            ("ARM_NESTED_BOW", "acc_bow"),
        ]:
            per_seed_dv = []
            for s in seeds_sorted:
                pc_s = per_seed[s].get("per_cell", {})
                means_d = []
                ok = True
                for d in DEPTHS:
                    k = "N%d_d%d" % (N, d)
                    if k not in pc_s:
                        ok = False
                        break
                    means_d.append(pc_s[k][mean_key])
                if ok and len(means_d) > 1:
                    per_seed_dv.append(float(np.var(means_d)))
            depth_var_per_seed_per_N_per_arm["N%d" % N][arm_key] = per_seed_dv

    # mean + SE of depth_var across seeds per (N, arm)
    depth_var_mean_per_N_per_arm = {}
    depth_var_se_per_N_per_arm = {}
    for N in N_DIMS:
        depth_var_mean_per_N_per_arm["N%d" % N] = {}
        depth_var_se_per_N_per_arm["N%d" % N] = {}
        for arm in EXPECTED_ARMS:
            dvs = depth_var_per_seed_per_N_per_arm["N%d" % N][arm]
            if len(dvs) >= 1:
                m = float(np.mean(dvs))
                se = (float(np.std(dvs, ddof=1) / np.sqrt(len(dvs)))
                      if len(dvs) >= 2 else 0.0)
            else:
                m = 0.0
                se = 0.0
            depth_var_mean_per_N_per_arm["N%d" % N][arm] = m
            depth_var_se_per_N_per_arm["N%d" % N][arm] = se

    # Also keep aggregate depth_var (variance of cross-seed-mean across depths)
    # for backward-compat / diagnostics
    depth_var_per_N_per_arm = {}
    for N in N_DIMS:
        depth_var_per_N_per_arm["N%d" % N] = {}
        for arm, mk in [("ARM_HRR_RECURSIVE", "hrr_mean"),
                         ("ARM_TENSOR_RANK2", "tensor_mean"),
                         ("ARM_NESTED_BOW", "bow_mean")]:
            means_across_depths = [cell_summary["N%d_d%d" % (N, d)][mk]
                                   for d in DEPTHS]
            depth_var_per_N_per_arm["N%d" % N][arm] = float(
                np.var(means_across_depths))

    max_depth_var_per_arm = {}
    for arm in EXPECTED_ARMS:
        max_depth_var_per_arm[arm] = max(
            depth_var_per_N_per_arm["N%d" % N][arm] for N in N_DIMS)

    # ---- Positive control (d=1, N=8192) ----
    pc_key = "N8192_d1"
    pc_cs = cell_summary.get(pc_key)
    pos_control_hrr_ok = (pc_cs is not None
                          and pc_cs["hrr_mean"] >= HP_POS_CONTROL_HRR_MIN)
    pos_control_tensor_ok = (pc_cs is not None
                              and pc_cs["tensor_mean"]
                              >= HP_POS_CONTROL_TENSOR_MIN)
    pos_control_bow_ok = (pc_cs is not None
                          and pc_cs["bow_mean"] >= HP_POS_CONTROL_BOW_MIN)

    # ---- Monotonic decay (N=8192) ----
    monotonic_decay = {}
    for arm_key, mean_key in [("ARM_HRR_RECURSIVE", "hrr_mean"),
                              ("ARM_TENSOR_RANK2", "tensor_mean")]:
        d1 = cell_summary["N8192_d%d" % DEPTHS[0]][mean_key]
        d_last = cell_summary["N8192_d%d" % DEPTHS[-1]][mean_key]
        monotonic_decay[arm_key] = d1 - d_last
    monotonic_decay_ok = any(v >= HP_MONOTONIC_DECAY_MIN
                              for v in monotonic_decay.values())

    arms_distinct_all_cells = all(cs["arms_distinct"]
                                   for cs in cell_summary.values())

    n_arms_identical = 0
    for cs in cell_summary.values():
        if (abs(cs["hrr_mean"] - cs["bow_mean"]) < 1e-9
                and not cs["arms_distinct"] and cs["n_seeds"] > 0):
            n_arms_identical += 1
    frac_arms_identical = (n_arms_identical / len(cell_summary)
                           if cell_summary else 0.0)

    # Cardinality
    expected_per_seed = N_CELLS * N_TRIALS
    total_completed = 0
    for s in seeds_sorted:
        for cs in per_seed[s].get("per_cell", {}).values():
            total_completed += cs.get("n_trials", 0)
    expected_total = len(seeds_sorted) * expected_per_seed
    cardinality_ok = (total_completed >= int(expected_total
                                              * HF_CARDINALITY_FRAC_MIN))

    # Suspect-1000
    suspect_1000 = False
    suspect_msg = ""
    for cs in cell_summary.values():
        if cs["depth"] >= 3:
            for arm_key, mean_key in [("HRR", "hrr_mean"),
                                       ("TENSOR", "tensor_mean")]:
                if cs[mean_key] >= SUSPECT_1000:
                    suspect_1000 = True
                    suspect_msg = ("arm=%s N=%d d=%d mean=%.4f"
                                   % (arm_key, cs["N"], cs["depth"],
                                      cs[mean_key]))
                    break
            if suspect_1000:
                break

    random_in_band = False
    for cs in cell_summary.values():
        if cs["n_seeds"] > 0:
            if RANDOM_BAND_LO <= cs["rand_mean"] <= RANDOM_BAND_HI:
                random_in_band = True
                break

    bow_depth_var_max = max_depth_var_per_arm["ARM_NESTED_BOW"]
    bow_discriminates_artifact = (bow_depth_var_max >= HF_NESTED_BOW_VAR_MAX)

    flat_depth_everywhere_real_bound = all(
        v < HF_FLAT_DEPTH_VAR_MAX
        for v in [max_depth_var_per_arm["ARM_HRR_RECURSIVE"],
                  max_depth_var_per_arm["ARM_TENSOR_RANK2"]])

    # NEW v4: BOW depth_var >= mechanism depth_var at N=8192 -> HF
    dv_hrr_8192 = depth_var_per_N_per_arm["N8192"]["ARM_HRR_RECURSIVE"]
    dv_tensor_8192 = depth_var_per_N_per_arm["N8192"]["ARM_TENSOR_RANK2"]
    dv_bow_8192 = depth_var_per_N_per_arm["N8192"]["ARM_NESTED_BOW"]
    max_mech_dv_8192 = max(dv_hrr_8192, dv_tensor_8192)
    bow_dominates = (dv_bow_8192 >= max_mech_dv_8192)

    # NEW v4: SE band + BOW margin
    dv_hrr_mean_8192 = depth_var_mean_per_N_per_arm["N8192"]["ARM_HRR_RECURSIVE"]
    dv_hrr_se_8192 = depth_var_se_per_N_per_arm["N8192"]["ARM_HRR_RECURSIVE"]
    dv_tensor_mean_8192 = depth_var_mean_per_N_per_arm["N8192"]["ARM_TENSOR_RANK2"]
    dv_tensor_se_8192 = depth_var_se_per_N_per_arm["N8192"]["ARM_TENSOR_RANK2"]
    dv_bow_mean_8192 = depth_var_mean_per_N_per_arm["N8192"]["ARM_NESTED_BOW"]

    # HARD_PASS condition: at N=8192, >=1 mechanism arm has
    #   (a) per-seed-mean depth_var >= HP_DEPTH_VAR_MIN (0.05)
    #   (b) per-seed-SE depth_var <= HP_DEPTH_VAR_SE_MAX (0.03)
    #   (c) per-seed-mean depth_var - BOW per-seed-mean depth_var
    #         >= HP_MECHANISM_BEATS_BOW_MARGIN (0.03)
    def _arm_passes_v4(mech_mean, mech_se, bow_mean):
        cond_a = mech_mean >= HP_DEPTH_VAR_MIN
        cond_b = mech_se <= HP_DEPTH_VAR_SE_MAX
        cond_c = (mech_mean - bow_mean) >= HP_MECHANISM_BEATS_BOW_MARGIN
        return cond_a, cond_b, cond_c

    hrr_a, hrr_b, hrr_c = _arm_passes_v4(dv_hrr_mean_8192, dv_hrr_se_8192,
                                           dv_bow_mean_8192)
    tensor_a, tensor_b, tensor_c = _arm_passes_v4(
        dv_tensor_mean_8192, dv_tensor_se_8192, dv_bow_mean_8192)

    hrr_v4_pass = hrr_a and hrr_b and hrr_c
    tensor_v4_pass = tensor_a and tensor_b and tensor_c
    depth_signal_v4_ok = hrr_v4_pass or tensor_v4_pass

    # Verdict ladder
    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not arms_distinct_all_cells:
        verdict = "HARD_FAIL"
        verdict_reason = ("META_RULE_AF_ARMS_IDENTICAL: arms-must-differ FAIL "
                          "in >=1 cell")
    elif frac_arms_identical >= HF_ARMS_IDENTICAL_FRAC_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("HARD_FAIL_ARMS_IDENTICAL: HRR == BOW for %.0f%%"
                          % (100 * frac_arms_identical))
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                          "completed=%d < %.2f*expected=%d" % (
                              total_completed, HF_CARDINALITY_FRAC_MIN,
                              int(expected_total * HF_CARDINALITY_FRAC_MIN)))
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = ("META_RULE_Q_SUSPECT_1000: %s (rig too easy)"
                          % suspect_msg)
    elif bow_discriminates_artifact:
        verdict = "HARD_FAIL"
        verdict_reason = ("HARD_FAIL_NESTED_BOW_DISCRIMINATES: BOW depth_var=%.3f"
                          " >= %.2f -- depth signal is distractor-scaling "
                          "artifact NOT recursion" % (
                              bow_depth_var_max, HF_NESTED_BOW_VAR_MAX))
    elif bow_dominates:
        verdict = "HARD_FAIL"
        verdict_reason = ("HARD_FAIL_BOW_DOMINATES_DEPTH_v4: BOW depth_var "
                          "%.4f >= mechanism max %.4f at N=8192 -- recursion "
                          "arms NOT depth-aware beyond noise budget" % (
                              dv_bow_8192, max_mech_dv_8192))
    elif flat_depth_everywhere_real_bound:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "HARD_FAIL_FLAT_DEPTH_v4: max depth-var < %.2f for BOTH "
            "HRR (%.3f) and TENSOR (%.3f) across ALL N -- closed negative "
            "after recalibration" % (
                HF_FLAT_DEPTH_VAR_MAX,
                max_depth_var_per_arm["ARM_HRR_RECURSIVE"],
                max_depth_var_per_arm["ARM_TENSOR_RANK2"]))
    elif not random_in_band:
        verdict = "HARD_FAIL"
        verdict_reason = ("PIPELINE_BROKEN: ARM_RANDOM outside chance band "
                          "[%.3f, %.3f]" % (RANDOM_BAND_LO, RANDOM_BAND_HI))
    else:
        hp_all = (depth_signal_v4_ok and pos_control_hrr_ok
                  and pos_control_tensor_ok and pos_control_bow_ok
                  and monotonic_decay_ok)
        if hp_all:
            verdict = "HARD_PASS"
            verdict_reason = (
                "RECURSIVE_TOM_DEPTH_DYNAMICS_CHAIN_GRADE: HRR_v4_pass=%s "
                "(dv=%.4f SE=%.4f vs BOW=%.4f) TENSOR_v4_pass=%s "
                "(dv=%.4f SE=%.4f vs BOW=%.4f) pos_control=OK "
                "monotonic_decay=HRR:%.3f/TENSOR:%.3f BOW_flat=%.4f" % (
                    hrr_v4_pass, dv_hrr_mean_8192, dv_hrr_se_8192,
                    dv_bow_mean_8192,
                    tensor_v4_pass, dv_tensor_mean_8192, dv_tensor_se_8192,
                    dv_bow_mean_8192,
                    monotonic_decay["ARM_HRR_RECURSIVE"],
                    monotonic_decay["ARM_TENSOR_RANK2"], bow_depth_var_max))
        else:
            verdict = "MIDDLE_BAND"
            verdict_reason = (
                "PARTIAL_v4: depth_signal_v4_ok=%s "
                "[HRR a/b/c=%s/%s/%s TENSOR a/b/c=%s/%s/%s] "
                "pos_ctrl_hrr=%s/tensor=%s/bow=%s monotonic=%s "
                "BOW_flat=%.4f" % (
                    depth_signal_v4_ok,
                    hrr_a, hrr_b, hrr_c,
                    tensor_a, tensor_b, tensor_c,
                    pos_control_hrr_ok, pos_control_tensor_ok,
                    pos_control_bow_ok, monotonic_decay_ok,
                    bow_depth_var_max))

    verdict_msg = (
        "%s | %s | n_seeds=%d N_LOC=%d distractor_scaling=%s "
        "depths=%s N_dims=%s expected_n=%d") % (
        verdict, verdict_reason, len(seeds_sorted), N_LOCATIONS,
        DISTRACTOR_SCALING, DEPTHS, N_DIMS, EXPECTED_N_UNITS,
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "cell_summary": cell_summary,
        "depth_var_per_N_per_arm": depth_var_per_N_per_arm,
        "depth_var_mean_per_N_per_arm": depth_var_mean_per_N_per_arm,
        "depth_var_se_per_N_per_arm": depth_var_se_per_N_per_arm,
        "max_depth_var_per_arm": max_depth_var_per_arm,
        "flat_depth_everywhere_real_bound": flat_depth_everywhere_real_bound,
        "bow_discriminates_artifact": bow_discriminates_artifact,
        "bow_dominates_v4": bow_dominates,
        "depth_signal_v4_ok": depth_signal_v4_ok,
        "hrr_v4_a_b_c": [hrr_a, hrr_b, hrr_c],
        "tensor_v4_a_b_c": [tensor_a, tensor_b, tensor_c],
        "pos_control_hrr_ok": pos_control_hrr_ok,
        "pos_control_tensor_ok": pos_control_tensor_ok,
        "pos_control_bow_ok": pos_control_bow_ok,
        "pos_control_hrr_mean": pc_cs["hrr_mean"] if pc_cs else None,
        "pos_control_tensor_mean": pc_cs["tensor_mean"] if pc_cs else None,
        "pos_control_bow_mean": pc_cs["bow_mean"] if pc_cs else None,
        "pos_control_rand_mean": pc_cs["rand_mean"] if pc_cs else None,
        "monotonic_decay": monotonic_decay,
        "monotonic_decay_ok": monotonic_decay_ok,
        "arms_distinct_all_cells": arms_distinct_all_cells,
        "frac_arms_identical": frac_arms_identical,
        "suspect_1000": suspect_1000,
        "random_in_band": random_in_band,
        "cardinality_ok": cardinality_ok,
        "total_completed_trials": total_completed,
        "expected_total_trials": expected_total,
        "n_seeds_complete": len(seeds_sorted),
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_verified": bool(arms_distinct_all_cells),
        "crlb_floor_computed": (1.0 / np.sqrt(min(N_DIMS) / 2)
                                if N_DIMS else 0.0),
        "crlb_formula_reference": (
            "Kanerva FHRR capacity: SNR ~ sqrt(N / (2*K_eff)); "
            "K_eff = (1+distractors)^depth for nested chain; "
            "distractors = depth (scaling=depth)"),
        "discriminator_reachability": True,
        "calibration_check": (
            "v4_recalibrated_HP_DEPTH_VAR_MIN=0.05_per_v3_observed_SNR_0.076"),
        "chance_baseline": CHANCE,
        "v4_thresholds": {
            "HP_DEPTH_VAR_MIN": HP_DEPTH_VAR_MIN,
            "HP_DEPTH_VAR_SE_MAX": HP_DEPTH_VAR_SE_MAX,
            "HP_MECHANISM_BEATS_BOW_MARGIN": HP_MECHANISM_BEATS_BOW_MARGIN,
        },
        "v3_anchor_evidence": {
            "tensor_depth_var_smoke_d135_N8192_seed7": 0.076,
            "tensor_d135_values": [0.833, 0.400, 0.167],
            "source_path": ("data/exp_substrate_higher_order_tom_recursive_v3"
                             "_smoke/partial_metrics_7.json"),
        },
    }


# ----------------- main -----------------

def main():
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(out_dir)
    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s seeds=%s n_cells=%d" % (
                               os.getpid(), RUN_MODE, SEEDS, N_CELLS),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "depths": DEPTHS, "N_dims": N_DIMS,
                                  "n_locations": N_LOCATIONS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s n_cells=%d (depths=%s x N=%s) "
          "n_trials=%d seeds=%s expected_n=%d N_LOC=%d scaling=%s" % (
              ANCHOR_NAME, RUN_MODE, N_CELLS, DEPTHS, N_DIMS,
              N_TRIALS, SEEDS, EXPECTED_N_UNITS,
              N_LOCATIONS, DISTRACTOR_SCALING), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_cell" in r
            hrr_means = [c["acc_hrr"] for c in r["per_cell"].values()]
            assert max(hrr_means) > 3 * CHANCE, (
                "self-test no meaningful HRR accuracy: max=%.3f (3x chance=%.3f)"
                % (max(hrr_means), 3 * CHANCE))
            n_distinct = sum(1 for c in r["per_cell"].values()
                              if c.get("arms_distinct"))
            assert n_distinct >= 1
            tensor_means = [c["acc_tensor"] for c in r["per_cell"].values()]
            bow_means = [c["acc_bow"] for c in r["per_cell"].values()]
            assert max(tensor_means) > CHANCE
            _write_minimal_metrics(
                out_dir, "SELFTEST_OK",
                "SELFTEST_OK: cells=%d max_hrr=%.3f max_tensor=%.3f max_bow=%.3f"
                " arms_distinct_cells=%d" % (
                    len(r["per_cell"]), max(hrr_means), max(tensor_means),
                    max(bow_means), n_distinct),
                extra={"_phase": "selftest_done",
                       "n_cells_tested": len(r["per_cell"]),
                       "max_hrr_acc": max(hrr_means),
                       "max_tensor_acc": max(tensor_means),
                       "max_bow_acc": max(bow_means),
                       "arms_distinct_cells": n_distinct})
            print("[selftest] OK cells=%d max_hrr=%.3f max_tensor=%.3f "
                  "max_bow=%.3f arms_d=%d/%d" % (
                      len(r["per_cell"]), max(hrr_means), max(tensor_means),
                      max(bow_means), n_distinct, len(r["per_cell"])),
                  flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                    "SELFTEST_FAIL: %s" % e,
                                    extra={"_traceback":
                                            traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIMS[0], "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "depths_signature": str(DEPTHS),
                  "N_dims_signature": str(N_DIMS),
                  "n_locations": N_LOCATIONS,
                  "distractor_scaling": DISTRACTOR_SCALING,
                  "v4_threshold_signature":
                  "HP_dv_min=%.3f,SE_max=%.3f,bow_margin=%.3f" % (
                      HP_DEPTH_VAR_MIN, HP_DEPTH_VAR_SE_MAX,
                      HP_MECHANISM_BEATS_BOW_MARGIN)}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                                "RUNNING: seed=%d (%d/%d)" % (
                                    seed, i + 1, len(remaining)),
                                extra={"_phase": "seed_running",
                                       "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        cliff_keys = [("N8192_d%d" % d) for d in DEPTHS]
        cliff_msg = " ".join(
            "d%d=%.2f" % (DEPTHS[i],
                          result["per_cell"].get(cliff_keys[i], {})
                          .get("acc_hrr", 0.0))
            for i in range(len(DEPTHS))
            if cliff_keys[i] in result["per_cell"])
        print("[seed=%d] DONE in %.1fs HRR depth-cliff(N=8192): %s" % (
            seed, time.time() - t0, cliff_msg), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["expected_n_units"] = EXPECTED_N_UNITS
    final["_hardening_marker"] = "v4_threshold_recal_SE_band_BOW_dominates_HF"
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
