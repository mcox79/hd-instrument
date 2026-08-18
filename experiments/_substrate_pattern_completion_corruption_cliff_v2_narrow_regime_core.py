"""Shared core for substrate_pattern_completion_corruption_cliff_v2_narrow_regime
sibling cells (seed_7, seed_13, seed_19).

v2 fix for v1 by-construction phase-coverage failure: corruption_frac NARROWED
from v1 wide-range {0.10, 0.30, 0.50, 0.70, 0.85, 0.95} (24 sat + 48 floor +
0 hp + 0 mb) to v2 cliff-walking band {0.40, 0.50, 0.55, 0.60, 0.65, 0.70}.

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    N_SWEEP_FULL, CORRUPTION_FULL, ITERS_FULL,
    N_SWEEP_SMOKE, CORRUPTION_SMOKE, ITERS_SMOKE,
    M_ITEMS_FULL, M_ITEMS_SMOKE

ASCII-only. No unicode. CUDA preferred; CPU fallback with warn for smoke.
FULL on CPU REFUSED (exit 2; Fix #24 GPU mandate).

PRE-REG: preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2_narrow_regime.md

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (Fix #24 GPU eligibility scan)
import torch

_TORCH_OK = True
_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_TOP1 = 0.95
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_TOP1 = 0.10
HP_DISCRIMINATOR = 0.50
MB_DISCRIMINATOR = 0.30

BETA = 8.0  # softmax sharpness; matches v1 + exp_iterative_cleanup_gpu_v1

# Sweep axes (v2 NARROWED corruption_frac around CRLB cliff ~0.46-0.49)
# v2.1 (post-smoke-rejection 2026-06-28): cliff is SHARPER than v1 sweep suggested.
# v1 showed corruption=0.50 already floors everywhere (top1=0.0) at all N and all T.
# v2 first attempt {0.40,0.50,0.55,0.60,0.65,0.70} ALSO rejected by smoke
# (corruption=0.55 floored at both N). Iterative cleanup does NOT push the cliff
# right empirically. So v2.1 walks the cliff TIGHTLY in [0.40, 0.52], straddling
# CRLB predictions {0.461 (N=2048), 0.472 (N=4096), 0.481 (N=8192), 0.486 (N=16384)}.
N_SWEEP_FULL = [2048, 4096, 8192, 16384]
CORRUPTION_FULL = [0.40, 0.43, 0.46, 0.48, 0.50, 0.52]  # v2.1 tight cliff band
ITERS_FULL = [1, 5, 20]
M_ITEMS_FULL = 500

# Smoke: discriminator-survives-scale (USER 2026-06-26 META_RULE)
# - N=2048 (low) + N=16384 (FULL preview) tests scale survival
# - corruption=0.40 (below ALL cliff predictions; should saturate) +
#   corruption=0.46 (on cliff for N=2048; just below cliff for N=16384;
#                    should produce edge value at >= 1 N) +
#   corruption=0.52 (above ALL cliff predictions; should floor)
N_SWEEP_SMOKE = [2048, 16384]
CORRUPTION_SMOKE = [0.40, 0.46, 0.52]
ITERS_SMOKE = [5]
M_ITEMS_SMOKE = 200

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / overlap-floor predictions (META_RULE_AG)
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, P: int) -> float:
    """1-step cliff prediction for bipolar pattern completion.

    For random bipolar +/-1 codebook with P stored items in N-dim space,
    cosine sim of a corrupted query (c fraction bits flipped) to its source
    is (1 - 2c). Noise floor (cosine to other items) ~ sqrt(2 log P / N).
    Cliff = corruption where signal == noise floor.
    """
    if N <= 0 or P <= 1:
        return 0.0
    noise = math.sqrt(2.0 * math.log(P) / N)
    return max(0.0, 0.5 * (1.0 - noise))


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    return "torch.cpu"


# ---------------------------------------------------------------------------
# Mechanism primitives (torch on DEVICE)
# ---------------------------------------------------------------------------
def build_codebook(M: int, N: int, seed: int) -> "torch.Tensor":
    """Build bipolar +/-1 codebook (M, N) on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def corrupt_batch(X: "torch.Tensor", corruption_frac: float, seed: int) -> "torch.Tensor":
    """Flip corruption_frac of bits independently per item (returns Q same shape)."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    flips = g.random((M, N)) < corruption_frac
    flips_t = torch.from_numpy(flips).to(DEVICE)
    Q = X.clone()
    Q[flips_t] = -Q[flips_t]
    return Q


def random_bipolar_batch(M: int, N: int, seed: int) -> "torch.Tensor":
    """Fresh random bipolar +/-1 batch (M, N) on DEVICE."""
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def hopfield_iterative_cleanup(Q0: "torch.Tensor", X: "torch.Tensor",
                                T: int, beta: float) -> "torch.Tensor":
    """T-step modern-Hopfield cleanup: Q_{t+1} = sign(softmax(beta * Q @ X.T) @ X).

    T=0 returns Q0 unchanged; T>=1 applies T cleanup steps.
    """
    Q = Q0
    for _ in range(max(0, T)):
        sims = Q @ X.T  # (M, M_items)
        p = torch.softmax(beta * sims, dim=1)  # (M, M_items)
        Q_new = torch.sign(p @ X)
        # Resolve zero -> +1 to stay bipolar
        Q_new = torch.where(Q_new == 0, torch.ones_like(Q_new), Q_new)
        Q = Q_new
    return Q


def top1_recall(Q_final: "torch.Tensor", X: "torch.Tensor",
                 target_idx: "torch.Tensor") -> float:
    """top-1 recall: fraction where argmax(Q @ X.T) == target_idx."""
    sims = Q_final @ X.T  # (M, M_items)
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(N: int, corruption: float, T: int, M: int,
                      seed: int) -> Dict[str, Any]:
    """Run one (N, corruption, T) phase point with both arms.

    Returns dict with top1_substrate, top1_random, discriminator, tier,
    peak_mem_mb, elapsed_s.
    """
    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Encoder hoisted: codebook built ONCE per phase point on DEVICE
    X = build_codebook(M, N, seed)  # (M, N)
    target_idx = torch.arange(M, device=DEVICE)

    # ARM_SUBSTRATE: corruption -> iterative cleanup
    Q_sub_0 = corrupt_batch(X, corruption, seed * 1000 + int(corruption * 100))
    Q_sub_T = hopfield_iterative_cleanup(Q_sub_0, X, T, BETA)
    top1_sub = top1_recall(Q_sub_T, X, target_idx)

    # ARM_RANDOM_FLOOR: fresh random bipolar -> identical cleanup pipeline
    Q_rnd_0 = random_bipolar_batch(M, N, seed * 1000 + int(corruption * 100))
    Q_rnd_T = hopfield_iterative_cleanup(Q_rnd_0, X, T, BETA)
    top1_rnd = top1_recall(Q_rnd_T, X, target_idx)

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rnd

    # Per-point verdict tier
    if top1_sub >= SATURATED_TOP1:
        tier = "SATURATED"
        saturation_flag = True
    elif top1_sub >= HARD_PASS_LO and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
        saturation_flag = False
    elif top1_sub >= MIDDLE_BAND_LO and discriminator >= MB_DISCRIMINATOR:
        tier = "MIDDLE_BAND"
        saturation_flag = False
    elif top1_sub <= FLOOR_TOP1:
        tier = "FLOOR"
        saturation_flag = False
    else:
        tier = "HARD_FAIL"
        saturation_flag = False

    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "N": N,
        "corruption_frac": corruption,
        "cleanup_iters": T,
        "M_items": M,
        "seed": seed,
        "top1_substrate": round(top1_sub, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "crlb_1step_cliff_prediction": round(
            crlb_1step_cliff_prediction(N, M), 4),
    }


# ---------------------------------------------------------------------------
# Selftest (called from sibling __main__ when --self-test passed)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Verify CRLB formula + bipolar mechanism + cardinality math.

    Returns (ok, msg). Halts cell on assertion fail.
    """
    msgs: List[str] = []
    # 1. CRLB formula sanity
    c1 = crlb_1step_cliff_prediction(2048, 500)
    c2 = crlb_1step_cliff_prediction(16384, 500)
    if not (0.40 < c1 < 0.50):
        return False, f"crlb N=2048 P=500 outside [0.40, 0.50]: {c1}"
    if not (0.40 < c2 < 0.50):
        return False, f"crlb N=16384 P=500 outside [0.40, 0.50]: {c2}"
    if not (c2 > c1):
        return False, f"cliff should shift right with N: c1={c1} c2={c2}"
    msgs.append(f"crlb N=2048 cliff={c1:.4f}; N=16384 cliff={c2:.4f}")

    # 2. v2 narrow band straddles CRLB cliff predictions
    cliff_range_min = min(c1, c2)
    cliff_range_max = max(c1, c2)
    has_below = any(c < cliff_range_min for c in CORRUPTION_FULL)
    has_above = any(c > cliff_range_max for c in CORRUPTION_FULL)
    if not has_below:
        return False, (f"CORRUPTION_FULL {CORRUPTION_FULL} lacks point BELOW "
                       f"min CRLB cliff {cliff_range_min:.4f}; cell wouldn't "
                       f"detect saturation regime")
    if not has_above:
        return False, (f"CORRUPTION_FULL {CORRUPTION_FULL} lacks point ABOVE "
                       f"max CRLB cliff {cliff_range_max:.4f}; cell wouldn't "
                       f"detect floor regime")
    msgs.append(f"corruption sweep {CORRUPTION_FULL} brackets CRLB band "
                f"[{cliff_range_min:.4f}, {cliff_range_max:.4f}]")

    # 3. Bipolar codebook orthogonality sanity
    g = np.random.default_rng(seed)
    X = (g.integers(0, 2, size=(50, 256)) * 2 - 1).astype(np.float32)
    norms = np.sqrt((X * X).sum(axis=1))
    if not np.allclose(norms, np.sqrt(256), atol=1e-3):
        return False, "bipolar norm mismatch"
    msgs.append("bipolar codebook norms ok")

    # 4. Mechanism sanity (10pct corruption should recover at N=256)
    item0 = X[0].copy()
    flips = g.random(256) < 0.10
    q = item0.copy()
    q[flips] = -q[flips]
    sims = q @ X.T
    pred = int(np.argmax(sims))
    if pred != 0:
        return False, f"mechanism sanity: 10pct corruption should recover item 0; got {pred}"
    msgs.append("mechanism single-step sanity ok")

    # 5. Cardinality math
    full_n = len(N_SWEEP_FULL) * len(CORRUPTION_FULL) * len(ITERS_FULL)
    smoke_n = len(N_SWEEP_SMOKE) * len(CORRUPTION_SMOKE) * len(ITERS_SMOKE)
    if full_n != 72:
        return False, f"FULL cardinality {full_n} != 72"
    if smoke_n != 6:
        return False, f"SMOKE cardinality {smoke_n} != 6"
    msgs.append(f"cardinality FULL={full_n} SMOKE={smoke_n}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep (drives one sibling cell)
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (N, corruption, T) phase points for one seed; return result dict.

    Halts on first exception (META_RULE_J: no silent except).
    """
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_sweep = N_SWEEP_SMOKE
        corruption_sweep = CORRUPTION_SMOKE
        iters_sweep = ITERS_SMOKE
        M_items = M_ITEMS_SMOKE
    else:
        N_sweep = N_SWEEP_FULL
        corruption_sweep = CORRUPTION_FULL
        iters_sweep = ITERS_FULL
        M_items = M_ITEMS_FULL

    expected_n_units = len(N_sweep) * len(corruption_sweep) * len(iters_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"N_sweep={N_sweep} corruption={corruption_sweep} iters={iters_sweep} "
          f"M={M_items} expected_n={expected_n_units}", flush=True)

    crlb_preds = {N: round(crlb_1step_cliff_prediction(N, M_items), 4)
                  for N in N_sweep}
    print(f"[crlb] 1-step cliff predictions: {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for N in N_sweep:
        for T in iters_sweep:
            for c in corruption_sweep:
                # Heartbeat (defensive pattern #4)
                print(f"[point] seed={seed} N={N} corruption={c:.2f} iters={T} ...",
                      flush=True)
                pt = eval_phase_point(N, c, T, M_items, seed)
                phase_map.append(pt)
                print(f"  -> top1_sub={pt['top1_substrate']:.3f} "
                      f"top1_rnd={pt['top1_random']:.3f} "
                      f"disc={pt['discriminator']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Cliff locator: for each (N, T), smallest corruption where top1 < 0.50
    cliff_locator: Dict[str, Dict[str, float]] = {}
    for T in iters_sweep:
        key_T = f"iters_{T}"
        cliff_locator[key_T] = {}
        for N in N_sweep:
            cliff = -1.0
            for c in corruption_sweep:
                matching = [p for p in phase_map
                            if p["N"] == N and p["cleanup_iters"] == T
                            and abs(p["corruption_frac"] - c) < 1e-6]
                if matching and matching[0]["top1_substrate"] < MIDDLE_BAND_LO:
                    cliff = c
                    break
            cliff_locator[key_T][f"N_{N}"] = cliff

    # Per-point arms-differ hashes
    sub_payload = json.dumps([p["top1_substrate"] for p in phase_map],
                              sort_keys=True).encode("utf-8")
    rnd_payload = json.dumps([p["top1_random"] for p in phase_map],
                              sort_keys=True).encode("utf-8")
    sub_hash = hashlib.sha256(sub_payload).hexdigest()
    rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
    arms_differ = {
        "substrate_hash": sub_hash,
        "random_hash": rnd_hash,
        "differ": sub_hash != rnd_hash,
    }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "N_sweep": N_sweep,
        "corruption_sweep": corruption_sweep,
        "iters_sweep": iters_sweep,
        "M_items": M_items,
        "N": N_sweep[-1],  # PROT-021 N stamp (highest N in sweep)
        "phase_map": phase_map,
        "cliff_locator": cliff_locator,
        "arms_differ_sha256": arms_differ,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "crlb_predictions_1step": crlb_preds,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(phase_map: List[Dict[str, Any]],
                          arms_differ: Dict[str, Any],
                          expected_n_units: int) -> Tuple[bool, str]:
    """Pre-reg smoke gate. Return (passed, reason)."""
    n_pts = len(phase_map)
    if n_pts != expected_n_units:
        return False, f"cardinality_breach: expected {expected_n_units} got {n_pts}"
    if not arms_differ.get("differ"):
        return False, "arms_identical: substrate and random hashes match"

    # corruption=0.40 must saturate at >= 1 N (easy regime sanity; below CRLB cliffs)
    easy_pts = [p for p in phase_map if abs(p["corruption_frac"] - 0.40) < 1e-6]
    if not easy_pts:
        return False, "easy_corner_missing: no corruption=0.40 points (smoke config bug)"
    if not any(p["top1_substrate"] >= SATURATED_TOP1 for p in easy_pts):
        max_easy = max(p["top1_substrate"] for p in easy_pts)
        return False, (f"easy_corner_no_saturation: corruption=0.40 max top1_substrate="
                       f"{max_easy:.3f} below {SATURATED_TOP1}; v2 narrow band may need"
                       f" to shift LEFT (cliff already at corruption < 0.40)")

    # corruption=0.52 must floor at >= 1 N (hard regime sanity; above all CRLB cliffs)
    hard_pts = [p for p in phase_map if abs(p["corruption_frac"] - 0.52) < 1e-6]
    if not hard_pts:
        return False, "hard_corner_missing: no corruption=0.52 points"
    if not any(p["top1_substrate"] < 0.50 for p in hard_pts):
        min_hard = min(p["top1_substrate"] for p in hard_pts)
        return False, (f"hard_corner_no_failure: corruption=0.52 min top1_substrate="
                       f"{min_hard:.3f} above 0.50; v2 narrow band may need to shift "
                       f"RIGHT (substrate more tolerant than CRLB predicts)")

    # corruption=0.46 must produce edge value at >= 1 N (DISCRIMINATOR-SURVIVES-SCALE)
    # corruption=0.46 sits ~ON cliff for N=2048 (predicted 0.461) and just BELOW
    # cliff for N=16384 (predicted 0.486). Should produce edge value at >= 1 N.
    edge_pts = [p for p in phase_map if abs(p["corruption_frac"] - 0.46) < 1e-6]
    if not edge_pts:
        return False, "edge_corner_missing: no corruption=0.46 points"
    edge_in_band = [p for p in edge_pts
                    if 0.10 < p["top1_substrate"] < 0.95]
    if not edge_in_band:
        edge_vals = {f"N={p['N']}": p["top1_substrate"] for p in edge_pts}
        return False, (f"discriminator_fails_scale: corruption=0.46 produced "
                       f"NO edge values at any N; all in [0, 0.10] or [0.95, 1.0]: "
                       f"{edge_vals}. Cliff width sharper than expected; reduce "
                       f"corruption spacing (try {{0.44, 0.46, 0.48}}); ABORT FULL DISPATCH")

    # >= 1 point in HARD_PASS or MIDDLE_BAND (real discrimination)
    n_disc_tier = sum(1 for p in phase_map
                      if p["verdict_tier_per_point"] in ("HARD_PASS", "MIDDLE_BAND"))
    if n_disc_tier < 1:
        tier_counts = {}
        for p in phase_map:
            t = p["verdict_tier_per_point"]
            tier_counts[t] = tier_counts.get(t, 0) + 1
        return False, (f"no_discriminating_tier: 0 points in HARD_PASS+MIDDLE_BAND; "
                       f"tier_counts={tier_counts}; v2 still by-construction-fails")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ + 0.40_sat "
                  f"+ 0.52_floor + 0.46_edge + {n_disc_tier}_discriminating_pts")


# ---------------------------------------------------------------------------
# Aggregate + verdict (called by sibling after seed completes)
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Aggregate one-seed partial into final metrics with verdict."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: aggregator received empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    # Single-seed cell: take the (only) partial
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_sha256", {})
    cardinality_ok = body.get("cardinality_ok", False)
    expected_n_units = body.get("expected_n_units", 0)
    observed_n_units = body.get("observed_n_units", 0)
    cliff_locator = body.get("cliff_locator", {})
    crlb_predictions = body.get("crlb_predictions_1step", {})

    # GPU util estimate (rough; matmul-bound peak_mem proxy)
    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 50.0))
    else:
        gpu_util_estimate = 0.0

    # Tier counts
    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    if is_smoke:
        passed, reason = smoke_gate_predicate(phase_map, arms_differ, expected_n_units)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n_units}/{expected_n_units} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"arms_differ={arms_differ.get('differ')}; "
                    f"gpu_util~{gpu_util_estimate:.2f}; reason={reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
        return {
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "phase_map": phase_map,
            "cliff_locator": cliff_locator,
            "arms_differ_sha256": arms_differ,
            "cardinality_ok": cardinality_ok,
            "expected_n_units": expected_n_units,
            "observed_n_units": observed_n_units,
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
            "crlb_predictions_1step": crlb_predictions,
            "gpu_util_estimate": round(gpu_util_estimate, 3),
            "device": body.get("device"),
            "gpu_name": body.get("gpu_name"),
        }

    # FULL: cell-level verdict per pre-reg bands
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n_units} "
                f"observed={observed_n_units}")
    elif not arms_differ.get("differ"):
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL_ARMS_IDENTICAL: substrate and random hashes match"
    elif n_disc <= 5:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_BY_CONSTRUCTION_REPEAT: only {n_disc}/72 points in "
                f"HARD_PASS+MIDDLE_BAND (v2 narrow band still fails discriminator; "
                f"same regime as v1 24sat+48floor); sat={n_sat} hp={n_hp} mb={n_mb} "
                f"floor={n_floor} fail={n_fail}; cliff_locator={cliff_locator}")
    elif n_disc >= 22:
        # Check cliff_locator returned real cliff-edges (must be > 0.40 and < 0.52
        # to count as a real interior cliff; -1 means no transition observed,
        # 0.40 means cliff already below sweep, 0.52 means cliff at sweep edge)
        real_cliffs = 0
        for T_key, N_dict in cliff_locator.items():
            for N_key, cliff_val in N_dict.items():
                if cliff_val > 0.40 and cliff_val < 0.52:
                    real_cliffs += 1
        if real_cliffs >= 1:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_PHASE_DIAGRAM_LOCALIZED_CLIFF: "
                    f"{observed_n_units}/{expected_n_units} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"real_cliff_edges={real_cliffs}; cliff_locator={cliff_locator}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND: {n_disc} discriminating pts but cliff_locator "
                    f"returned no real edges (all -1 or 0.40); cliff_locator={cliff_locator}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: {n_disc}/72 discriminating pts (need >=22); "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"cliff_locator={cliff_locator}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "phase_map": phase_map,
        "cliff_locator": cliff_locator,
        "arms_differ_sha256": arms_differ,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "crlb_predictions_1step": crlb_predictions,
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
    }


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "SATURATED_TOP1", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_TOP1",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "BETA",
    "N_SWEEP_FULL", "CORRUPTION_FULL", "ITERS_FULL", "M_ITEMS_FULL",
    "N_SWEEP_SMOKE", "CORRUPTION_SMOKE", "ITERS_SMOKE", "M_ITEMS_SMOKE",
    "REQUIRED_FIELDS",
    "crlb_1step_cliff_prediction", "get_backend_label",
    "build_codebook", "corrupt_batch", "random_bipolar_batch",
    "hopfield_iterative_cleanup", "top1_recall",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
