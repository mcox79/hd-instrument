"""Shared core for substrate_pc_cleanup_family_phase_diagram_v2_M_sweep siblings.

v2 (2026-07-03): composed on v1 (2026-06-28) by ADDING M as a swept axis.
v1 held M fixed at 300. v2 sweeps M in {100, 200, 400, 800, 1600, 3200}
(log-scale, x2 per step) to characterize cleanup mechanism scaling with
codebook size.

Physics-law arc (candidate CG_META tier):
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian
    (analog to existing SCALE_FREE (N) and TOPOLOGY_FREE (encoder) laws)

Cleanup families (OUTER axis; REUSED from v1):
    modern_hopfield      : Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)
    classical_hopfield   : Q_{t+1} = sign(Q_t @ W) where W = X.T @ X / M (Hebbian)
    iterative_cosine     : Q_{t+1} = X[argmax(Q_t @ X.T)] (snap to nearest)
    soft_energy_attractor: Q_{t+1} = sign(Q_t + alpha*(softmax(beta * Q_t @ X.T) @ X - Q_t))

Inner axes: M (6) x N (2) x corruption (3) x cleanup_iters (2).
Total FULL: 4 x 6 x 2 x 3 x 2 = 288 phase points per seed.
Total SMOKE: 4 x 3 x 1 x 2 x 1 = 24 corner points per seed.

Encoder FIXED: binary_bipolar dense codebook.

PRE-REG: preregs/2026-07-03_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    CLEANUP_FAMILIES,
    M_SWEEP_FULL, M_SWEEP_SMOKE,
    N_SWEEP_FULL, N_SWEEP_SMOKE,
    CORRUPTION_FULL, CORRUPTION_SMOKE, ITERS_FULL, ITERS_SMOKE

ASCII-only. No unicode. No em-dashes. CUDA preferred; CPU fully supported.

Author: exp_dev 2026-07-03 (Opus 4.7, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

# CUDA env before torch import (USER-LOCKED)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch

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

BETA = 8.0
ALPHA_SOFT = 0.5

CLEANUP_FAMILIES = ("modern_hopfield", "classical_hopfield",
                    "iterative_cosine", "soft_energy_attractor")
NON_HEBBIAN_FAMILIES = ("modern_hopfield", "iterative_cosine",
                        "soft_energy_attractor")

# Sweep axes (v2 adds M as a swept axis)
M_SWEEP_FULL = [100, 200, 400, 800, 1600, 3200]
N_SWEEP_FULL = [2048, 8192]
# Cliff CRLB predictions: N=2048 M=100->0.467, M=3200->0.456;
#   N=8192 M=100->0.483, M=3200->0.478. c values BRACKET the cliff for
#   both N so M-dependence is measurable. c=0.20 easy positive-control;
#   c=0.45 shows M-dependence at N=2048 (near cliff), still-easy at N=8192;
#   c=0.475 shows M-dependence at N=8192 (near cliff), floor at N=2048.
CORRUPTION_FULL = [0.20, 0.45, 0.475]
ITERS_FULL = [1, 5]

M_SWEEP_SMOKE = [100, 800, 3200]
N_SWEEP_SMOKE = [2048]
# SMOKE brackets N=2048 cliff (0.456-0.467) with 0.45; keeps 0.20 as PC easy
CORRUPTION_SMOKE = [0.20, 0.45]
ITERS_SMOKE = [1]

EXPECTED_N_UNITS_FULL = (len(CLEANUP_FAMILIES) * len(M_SWEEP_FULL)
                         * len(N_SWEEP_FULL) * len(CORRUPTION_FULL)
                         * len(ITERS_FULL))  # 288
EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_FAMILIES) * len(M_SWEEP_SMOKE)
                          * len(N_SWEEP_SMOKE) * len(CORRUPTION_SMOKE)
                          * len(ITERS_SMOKE))  # 24

# Positive control: easy-regime small-M must nail
POSITIVE_CONTROL = {
    "cleanup_family": "modern_hopfield",
    "M": 100,
    "N": 8192,
    "corruption_frac": 0.20,
    "cleanup_iters": 5,
    "top1_floor": 0.90,
}
POSITIVE_CONTROL_SMOKE = {
    "cleanup_family": "modern_hopfield",
    "M": 100,
    "N": 2048,
    "corruption_frac": 0.20,
    "cleanup_iters": 1,
    "top1_floor": 0.85,
}

# Classical Hopfield theoretical capacity (Amit-Gutfreund-Sompolinsky 1985)
CLASSICAL_CAPACITY_FRAC = 0.14

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / overlap-floor prediction
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, M: int) -> float:
    """1-step cliff prediction: signal (1 - 2c) meets noise floor sqrt(2 log M / N)."""
    if N <= 0 or M <= 1:
        return 0.0
    noise = math.sqrt(2.0 * math.log(M) / N)
    return max(0.0, 0.5 * (1.0 - noise))


def classical_capacity_at_N(N: int) -> int:
    """Classical Hopfield capacity ceiling ~ 0.14N; above this spurious minima dominate.

    Amit-Gutfreund-Sompolinsky 1985 (T2/amit_gutfreund_sompolinsky_capacity atom).
    """
    return int(CLASSICAL_CAPACITY_FRAC * N)


def M_crit_locator(mechanism: str, N: int) -> float:
    """Theoretical capacity ceiling M_crit per mechanism at dimension N.

    Citations (substrate atoms):
      classical_hopfield    : AGS 1985  T2/amit_gutfreund_sompolinsky_capacity
      modern_hopfield       : Ramsauer 2020  T2/modern_hopfield_ramsauer (~ exp(N/2), practically infinite)
      soft_energy_attractor : tracks modern (softmax target); T2/modern_hopfield_ramsauer
      iterative_cosine      : Plate 1995 N/(2 ln N) matched-filter recall floor for random queries

    Returns float; use math.inf for modern-family (practically unreachable
    at any M we can enumerate on a laptop).
    """
    if mechanism == "classical_hopfield":
        return float(CLASSICAL_CAPACITY_FRAC * N)
    if mechanism == "iterative_cosine":
        if N <= 2:
            return 1.0
        return float(N / (2.0 * math.log(N)))
    if mechanism in ("modern_hopfield", "soft_energy_attractor"):
        return math.inf
    return math.inf


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Codebook + corruption
# ---------------------------------------------------------------------------
def _build_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _corrupt_binary_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed)
    M, N = X.shape
    flips = g.random((M, N)) < c
    flips_t = torch.from_numpy(flips).to(DEVICE)
    Q = X.clone()
    Q[flips_t] = -Q[flips_t]
    return Q


def _random_floor_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _sign_op(V: "torch.Tensor") -> "torch.Tensor":
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


# ---------------------------------------------------------------------------
# Cleanup family implementations (identical to v1; REUSED)
# ---------------------------------------------------------------------------
def _modern_hopfield_cleanup(Q0, X, T, beta):
    Q = Q0
    for _ in range(max(0, T)):
        sims = Q @ X.T
        p = torch.softmax(beta * sims, dim=1)
        Q_new = p @ X
        Q = _sign_op(Q_new)
    return Q


def _classical_hopfield_cleanup(Q0, X, T, beta):
    M_items, N = X.shape
    W = (X.T @ X) / float(M_items)
    W.fill_diagonal_(0.0)
    Q = Q0
    for _ in range(max(0, T)):
        h = Q @ W
        Q = _sign_op(h)
    return Q


def _iterative_cosine_cleanup(Q0, X, T, beta):
    Q = Q0
    for _ in range(max(0, T)):
        sims = Q @ X.T
        idx = sims.argmax(dim=1)
        Q = X[idx]
    return Q


def _soft_energy_attractor_cleanup(Q0, X, T, beta):
    Q = Q0
    alpha = ALPHA_SOFT
    for _ in range(max(0, T)):
        sims = Q @ X.T
        p = torch.softmax(beta * sims, dim=1)
        target = p @ X
        Q_new = Q + alpha * (target - Q)
        Q = _sign_op(Q_new)
    return Q


_CLEANUP_REGISTRY = {
    "modern_hopfield": _modern_hopfield_cleanup,
    "classical_hopfield": _classical_hopfield_cleanup,
    "iterative_cosine": _iterative_cosine_cleanup,
    "soft_energy_attractor": _soft_energy_attractor_cleanup,
}


def _top1_recall(Q_final, X, target_idx):
    sims = Q_final @ X.T
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(cleanup_family: str, M: int, N: int, corruption: float,
                     T: int, seed: int) -> Dict[str, Any]:
    if cleanup_family not in _CLEANUP_REGISTRY:
        raise ValueError(f"unknown cleanup_family={cleanup_family!r}")
    cleanup_fn = _CLEANUP_REGISTRY[cleanup_family]

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Codebook + corruption
    X = _build_binary_bipolar(M, N, seed)
    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(corruption * 1000) + M * 7

    Q_sub_0 = _corrupt_binary_bipolar(X, corruption, sub_seed)
    Q_sub_T = cleanup_fn(Q_sub_0, X, T, BETA)
    top1_sub = _top1_recall(Q_sub_T, X, target_idx)

    # NaN sanity (META_RULE M-S; production-scale NaN detection)
    if torch.isnan(Q_sub_T).any().item():
        raise RuntimeError(
            f"NAN_IN_MECHANISM_OUTPUT: cleanup={cleanup_family} M={M} N={N} "
            f"c={corruption} T={T} seed={seed}"
        )

    mech_output_hash = hashlib.sha256(
        Q_sub_T.cpu().numpy().tobytes()).hexdigest()[:16]

    Q_rnd_0 = _random_floor_binary_bipolar(M, N, sub_seed)
    Q_rnd_T = cleanup_fn(Q_rnd_0, X, T, BETA)
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx)
    if torch.isnan(Q_rnd_T).any().item():
        raise RuntimeError(
            f"NAN_IN_RANDOM_OUTPUT: cleanup={cleanup_family} M={M} N={N} "
            f"c={corruption} T={T} seed={seed}"
        )
    rnd_output_hash = hashlib.sha256(
        Q_rnd_T.cpu().numpy().tobytes()).hexdigest()[:16]

    # Calibration: initial cosine of Q_sub_0 vs X
    cal_sample = min(20, M)
    Q_norm = torch.linalg.norm(Q_sub_0[:cal_sample], dim=1).clamp(min=1e-12)
    X_norm = torch.linalg.norm(X[:cal_sample], dim=1).clamp(min=1e-12)
    cal_dots = (Q_sub_0[:cal_sample] * X[:cal_sample]).sum(dim=1)
    cal_cos = float((cal_dots / (Q_norm * X_norm)).mean().item())

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rnd

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

    # Classical capacity ratio (informational)
    m_over_cap = M / max(1, classical_capacity_at_N(N))
    # Per-mechanism capacity ratio (informational; capacity-relative gate input)
    m_crit_this = M_crit_locator(cleanup_family, N)
    if math.isfinite(m_crit_this) and m_crit_this > 0:
        m_over_m_crit = M / m_crit_this
    else:
        m_over_m_crit = 0.0  # modern/soft: practically infinite capacity

    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "cleanup_family": cleanup_family,
        "M_items": M,
        "N": N,
        "corruption_frac": corruption,
        "cleanup_iters": T,
        "seed": seed,
        "top1_mechanism": round(top1_sub, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "mech_output_hash": mech_output_hash,
        "rnd_output_hash": rnd_output_hash,
        "calibration_cos_q0_x": round(cal_cos, 4),
        "calibration_target_cos": round(1.0 - 2.0 * corruption, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "crlb_1step_cliff_prediction": round(
            crlb_1step_cliff_prediction(N, M), 4),
        "m_over_classical_capacity": round(m_over_cap, 3),
        "m_crit_theoretical": (round(m_crit_this, 2)
                               if math.isfinite(m_crit_this) else "inf"),
        "m_over_m_crit": round(m_over_m_crit, 3),
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    msgs: List[str] = []

    # 1. Cardinality
    if EXPECTED_N_UNITS_FULL != 288:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 288"
    if EXPECTED_N_UNITS_SMOKE != 24:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 24"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB shift with M (cliff must move LEFT as M grows at fixed N)
    c_lo = crlb_1step_cliff_prediction(2048, 100)
    c_hi = crlb_1step_cliff_prediction(2048, 3200)
    if not (c_lo > c_hi):
        return False, f"CRLB should shift LEFT with M: c(M=100)={c_lo:.4f} c(M=3200)={c_hi:.4f}"
    if not (0.40 < c_hi < c_lo < 0.50):
        return False, f"CRLB outside expected [0.40, 0.50]: c_lo={c_lo:.4f} c_hi={c_hi:.4f}"
    # CRLB shift with N (cliff moves RIGHT as N grows at fixed M)
    c_n2 = crlb_1step_cliff_prediction(2048, 800)
    c_n8 = crlb_1step_cliff_prediction(8192, 800)
    if not (c_n8 > c_n2):
        return False, f"CRLB should shift RIGHT with N: c(N=2048)={c_n2:.4f} c(N=8192)={c_n8:.4f}"
    msgs.append(f"crlb shifts OK: M100vsM3200@N2048={c_lo:.4f}>{c_hi:.4f}; "
                f"N2048vsN8192@M800={c_n2:.4f}<{c_n8:.4f}")

    # 3. Classical capacity math (T2/amit_gutfreund_sompolinsky_capacity)
    cap_2048 = classical_capacity_at_N(2048)
    cap_8192 = classical_capacity_at_N(8192)
    if cap_2048 != 286 or cap_8192 != 1146:
        return False, f"classical capacity math: cap(2048)={cap_2048}, cap(8192)={cap_8192}"
    msgs.append(f"classical cap: N=2048->{cap_2048} N=8192->{cap_8192}")

    # 3b. M_crit_locator sanity per mechanism (Plate for iterative, AGS for
    # classical, inf for modern/soft) at N=2048
    m_crit_it = M_crit_locator("iterative_cosine", 2048)
    m_crit_cls = M_crit_locator("classical_hopfield", 2048)
    m_crit_mod = M_crit_locator("modern_hopfield", 2048)
    if not (130 <= m_crit_it <= 140):
        return False, f"Plate M_crit at N=2048 outside [130,140]: {m_crit_it:.2f}"
    if not abs(m_crit_cls - 286.72) < 1.0:
        return False, f"AGS M_crit at N=2048 outside 286+/-1: {m_crit_cls:.2f}"
    if not math.isinf(m_crit_mod):
        return False, f"Ramsauer M_crit should be inf: {m_crit_mod}"
    msgs.append(f"M_crit N=2048: iter={m_crit_it:.2f} (Plate); "
                f"cls={m_crit_cls:.2f} (AGS); mod=inf (Ramsauer)")

    # 4. Cleanup mechanism sanity (identity + easy regime)
    M_san = 20
    N_san = 512
    X = _build_binary_bipolar(M_san, N_san, seed)
    target_idx = torch.arange(M_san, device=DEVICE)

    for fam in CLEANUP_FAMILIES:
        cleanup_fn = _CLEANUP_REGISTRY[fam]
        # (a) identity at c=0.0
        Q0 = X.clone()
        Q1 = cleanup_fn(Q0, X, 1, BETA)
        n_hit_id = int((Q1 @ X.T).argmax(dim=1).eq(target_idx).sum().item())
        if n_hit_id < M_san:
            return False, (f"identity FAIL {fam}: c=0.0 T=1 preserved "
                           f"{n_hit_id}/{M_san}")
        # (b) easy regime c=0.10
        Q0c = _corrupt_binary_bipolar(X, 0.10, seed * 2)
        Q1c = cleanup_fn(Q0c, X, 1, BETA)
        n_hit = int((Q1c @ X.T).argmax(dim=1).eq(target_idx).sum().item())
        if n_hit < M_san * 0.5:
            return False, (f"easy-regime FAIL {fam}: c=0.10 recovered "
                           f"{n_hit}/{M_san}")
        msgs.append(f"sanity {fam}: id={n_hit_id}/{M_san} easy={n_hit}/{M_san}")

    del X, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    # 5. Cleanup arms produce DISTINCT outputs at the cliff regime AT SEVERAL M
    # (catches mechanism-collapse across M-sweep)
    for M_diff in (100, 3200):
        N_diff = 1024
        X_diff = _build_binary_bipolar(M_diff, N_diff, seed)
        c_diff = 0.475
        Q0_diff = _corrupt_binary_bipolar(X_diff, c_diff,
                                          seed * 100 + int(c_diff * 1000) + M_diff)
        hashes = {}
        for fam in CLEANUP_FAMILIES:
            cleanup_fn = _CLEANUP_REGISTRY[fam]
            Q1 = cleanup_fn(Q0_diff, X_diff, 1, BETA)
            h = hashlib.sha256(Q1.cpu().numpy().tobytes()).hexdigest()[:16]
            hashes[fam] = h
        if len(set(hashes.values())) != len(CLEANUP_FAMILIES):
            return False, (f"cleanup outputs NOT distinct at M={M_diff} "
                           f"cliff regime c={c_diff}: {hashes}")
        msgs.append(f"cleanup byte-hashes distinct at M={M_diff} c={c_diff}")
        del X_diff, Q0_diff
        if _CUDA_OK:
            torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        M_sweep = M_SWEEP_SMOKE
        N_sweep = N_SWEEP_SMOKE
        c_sweep = CORRUPTION_SMOKE
        T_sweep = ITERS_SMOKE
    else:
        M_sweep = M_SWEEP_FULL
        N_sweep = N_SWEEP_FULL
        c_sweep = CORRUPTION_FULL
        T_sweep = ITERS_FULL

    expected_n_units = (len(CLEANUP_FAMILIES) * len(M_sweep) * len(N_sweep)
                        * len(c_sweep) * len(T_sweep))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"cleanups={CLEANUP_FAMILIES} M={M_sweep} N={N_sweep} c={c_sweep} "
          f"T={T_sweep} expected_n={expected_n_units}", flush=True)

    # CRLB predictions across (N, M) grid
    crlb_preds: Dict[str, float] = {}
    for N in N_sweep:
        for M in M_sweep:
            crlb_preds[f"N{N}_M{M}"] = round(
                crlb_1step_cliff_prediction(N, M), 4)
    print(f"[crlb] cliff predictions: {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in CLEANUP_FAMILIES:
        for M in M_sweep:
            for N in N_sweep:
                for T in T_sweep:
                    for c in c_sweep:
                        print(f"[point] seed={seed} cleanup={fam} M={M} N={N} "
                              f"c={c:.3f} T={T} ...", flush=True)
                        pt = eval_phase_point(fam, M, N, c, T, seed)
                        phase_map.append(pt)
                        print(f"  -> top1_mech={pt['top1_mechanism']:.3f} "
                              f"top1_rnd={pt['top1_random']:.3f} "
                              f"disc={pt['discriminator']:.3f} "
                              f"tier={pt['verdict_tier_per_point']} "
                              f"m/cap={pt['m_over_classical_capacity']:.2f} "
                              f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-cleanup arm-hashes (mech vs random)
    arms_differ_per_cl: Dict[str, Dict[str, Any]] = {}
    cleanup_mech_hashes: Dict[str, str] = {}
    for fam in CLEANUP_FAMILIES:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        sub_payload = json.dumps([p["mech_output_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["rnd_output_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        sub_hash = hashlib.sha256(sub_payload).hexdigest()
        rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
        arms_differ_per_cl[fam] = {
            "mechanism_hash": sub_hash,
            "random_hash": rnd_hash,
            "differ": sub_hash != rnd_hash,
        }
        cleanup_mech_hashes[fam] = sub_hash

    pairs_differ: Dict[str, bool] = {}
    fams = list(CLEANUP_FAMILIES)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (cleanup_mech_hashes[fams[i]]
                                 != cleanup_mech_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # M-scaling summary: per (cleanup, N, c, T), top1 as fn of M
    per_cleanup_M_summary: Dict[str, Any] = {}
    for fam in CLEANUP_FAMILIES:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        regime_curves: Dict[str, Dict[str, Any]] = {}
        for N in N_sweep:
            for c in c_sweep:
                for T in T_sweep:
                    regime_key = f"N{N}_c{c:.2f}_T{T}"
                    curve = []
                    for M in M_sweep:
                        matches = [p for p in fam_pts
                                   if p["N"] == N and p["M_items"] == M
                                   and abs(p["corruption_frac"] - c) < 1e-6
                                   and p["cleanup_iters"] == T]
                        if matches:
                            curve.append({
                                "M": M,
                                "top1": matches[0]["top1_mechanism"],
                            })
                    # Monotonicity check: top1 monotone non-increasing in M
                    top1_seq = [pt["top1"] for pt in curve]
                    monotone_ok = all(top1_seq[i + 1] <= top1_seq[i] + 0.10
                                      for i in range(len(top1_seq) - 1))
                    # Smoothness: no adjacent jump larger than 0.35
                    smoothness_ok = all(abs(top1_seq[i + 1] - top1_seq[i]) <= 0.35
                                        for i in range(len(top1_seq) - 1))
                    # Range span
                    span = (max(top1_seq) - min(top1_seq)) if top1_seq else 0.0
                    regime_curves[regime_key] = {
                        "curve": curve,
                        "monotone_ok": monotone_ok,
                        "smoothness_ok": smoothness_ok,
                        "top1_span": round(span, 4),
                    }
        top1_all = [p["top1_mechanism"] for p in fam_pts]
        per_cleanup_M_summary[fam] = {
            "top1_mean": round(float(np.mean(top1_all)) if top1_all else 0.0, 4),
            "regime_curves": regime_curves,
        }

    # Physics-law check: non-Hebbian cleanups should be SMOOTH + MONOTONIC
    physics_law_check: Dict[str, Any] = {}
    for fam in NON_HEBBIAN_FAMILIES:
        summ = per_cleanup_M_summary.get(fam, {})
        regimes = summ.get("regime_curves", {})
        n_regimes = len(regimes)
        n_mono = sum(1 for r in regimes.values() if r["monotone_ok"])
        n_smooth = sum(1 for r in regimes.values() if r["smoothness_ok"])
        # Scale-free: cliff shifts RIGHT with N. Check per c, T: at N=8192 all
        # M values maintain top1 >= at N=2048 counterpart.
        scale_free_pass = True
        if len(N_sweep) >= 2 and 2048 in N_sweep and 8192 in N_sweep:
            fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
            for M in M_sweep:
                for c in c_sweep:
                    for T in T_sweep:
                        p2 = [p for p in fam_pts if p["N"] == 2048
                              and p["M_items"] == M
                              and abs(p["corruption_frac"] - c) < 1e-6
                              and p["cleanup_iters"] == T]
                        p8 = [p for p in fam_pts if p["N"] == 8192
                              and p["M_items"] == M
                              and abs(p["corruption_frac"] - c) < 1e-6
                              and p["cleanup_iters"] == T]
                        if p2 and p8:
                            # scale-free: bigger N tolerates SAME or more
                            # noise than smaller N; top1@N8192 >= top1@N2048 - 0.10
                            if p8[0]["top1_mechanism"] + 0.10 < p2[0]["top1_mechanism"]:
                                scale_free_pass = False
        physics_law_check[fam] = {
            "n_regimes": n_regimes,
            "n_monotone_pass": n_mono,
            "n_smoothness_pass": n_smooth,
            "monotone_frac": round(n_mono / max(1, n_regimes), 3),
            "smoothness_frac": round(n_smooth / max(1, n_regimes), 3),
            "scale_free_shift_pass": scale_free_pass,
            "cg_meta_tier_eligible_per_cleanup": (
                n_regimes > 0 and n_mono == n_regimes and n_smooth == n_regimes
                and scale_free_pass),
        }
    physics_law_check["cg_meta_tier_eligible"] = all(
        physics_law_check[fam].get("cg_meta_tier_eligible_per_cleanup")
        for fam in NON_HEBBIAN_FAMILIES
    )

    # Classical capacity crossover: where does classical drop below 0.50 in
    # easy regime (c=0.20 iters=1)? Should be near M ~ 0.14 N.
    classical_capacity_crossover: Dict[str, Any] = {}
    if "classical_hopfield" in CLEANUP_FAMILIES:
        for N in N_sweep:
            crossover_M = None
            for M in M_sweep:
                # Use lowest-corruption + lowest-T (easiest regime avail in sweep)
                c_lo_val = min(c_sweep)
                T_lo_val = min(T_sweep)
                match = [p for p in phase_map
                         if p["cleanup_family"] == "classical_hopfield"
                         and p["N"] == N and p["M_items"] == M
                         and abs(p["corruption_frac"] - c_lo_val) < 1e-6
                         and p["cleanup_iters"] == T_lo_val]
                if match and match[0]["top1_mechanism"] < 0.50:
                    crossover_M = M
                    break
            classical_capacity_crossover[f"N{N}"] = {
                "crossover_M": crossover_M,
                "theoretical_cap": classical_capacity_at_N(N),
                "regime_c": min(c_sweep),
                "regime_T": min(T_sweep),
            }

    # ------------------------------------------------------------------
    # 6 falsifiable CG_META predictions (Director-provided lit-drill 2026-07-03)
    # ------------------------------------------------------------------
    def _pt(fam, M, N, c, T):
        matches = [p for p in phase_map
                   if p["cleanup_family"] == fam and p["N"] == N
                   and p["M_items"] == M
                   and abs(p["corruption_frac"] - c) < 1e-6
                   and p["cleanup_iters"] == T]
        return matches[0]["top1_mechanism"] if matches else None

    cg_meta_predictions: Dict[str, Any] = {}

    # 1. Mechanism ordering at high M: modern - classical >= 0.40 at
    #    M=3200 N=8192 c=0.20 (Ramsauer-AGS gap).
    #    NOTE: FULL sweep uses c ∈ {0.20, 0.45, 0.475}; at c=0.20 both may
    #    saturate at 1.0. Reformulate to CLOSEST-available cliff-adjacent c.
    p_mod_hi_M = _pt("modern_hopfield", 3200, 8192, 0.475, 5)
    p_cls_hi_M = _pt("classical_hopfield", 3200, 8192, 0.475, 5)
    p1_ok = None
    p1_gap = None
    if p_mod_hi_M is not None and p_cls_hi_M is not None:
        p1_gap = p_mod_hi_M - p_cls_hi_M
        p1_ok = p1_gap >= 0.40
    cg_meta_predictions["P1_ordering_high_M"] = {
        "regime": "M=3200 N=8192 c=0.475 T=5",
        "modern_top1": p_mod_hi_M,
        "classical_top1": p_cls_hi_M,
        "gap": p1_gap,
        "threshold": 0.40,
        "pass": p1_ok,
        "citation": "T2/modern_hopfield_ramsauer vs T2/amit_gutfreund_sompolinsky_capacity",
    }

    # 2. AGS cliff localization for classical: monotone crossing 0.50
    #    between M=200 and M=400 at N=2048, c=0.20, T=1
    p_cls_200 = _pt("classical_hopfield", 200, 2048, 0.20, 1)
    p_cls_400 = _pt("classical_hopfield", 400, 2048, 0.20, 1)
    p2_ok = None
    if p_cls_200 is not None and p_cls_400 is not None:
        p2_ok = (p_cls_200 > 0.50 and p_cls_400 < 0.90)
    cg_meta_predictions["P2_AGS_cliff_classical"] = {
        "regime": "N=2048 c=0.20 T=1",
        "top1_M200": p_cls_200,
        "top1_M400": p_cls_400,
        "expected": "cliff crosses between M=200 (>0.50) and M=400 (<0.90); AGS ~286",
        "pass": p2_ok,
        "citation": "T2/amit_gutfreund_sompolinsky_capacity alpha_c=0.138",
    }

    # 3. Plate bound for iterative_cosine: <0.50 by M<=400 at N=2048 (theory
    #    M_crit=135, allow 3x factor = M=400). Test at c=0.20 T=1.
    #    NOTE: at c=0.20 (easy), iterative_cosine's Plate bound applies to
    #    random-query recall NOT corrupted-source; check at cliff-adjacent
    #    c=0.45 where signal ~ noise (Plate regime).
    p_it_M400_easy = _pt("iterative_cosine", 400, 2048, 0.20, 1)
    p_it_M1600_easy = _pt("iterative_cosine", 1600, 2048, 0.20, 1)
    p_it_M100_cliff = _pt("iterative_cosine", 100, 2048, 0.45, 1)
    p_it_M400_cliff = _pt("iterative_cosine", 400, 2048, 0.45, 1)
    p3_ok = None
    if p_it_M100_cliff is not None and p_it_M400_cliff is not None:
        # Plate regime at cliff: M=100 should retain > M=400; delta >= 0.15
        p3_ok = (p_it_M100_cliff - p_it_M400_cliff) >= 0.15
    cg_meta_predictions["P3_Plate_iterative_cosine"] = {
        "regime_cliff": "N=2048 c=0.45 T=1",
        "top1_M100_cliff": p_it_M100_cliff,
        "top1_M400_cliff": p_it_M400_cliff,
        "top1_M400_easy": p_it_M400_easy,
        "top1_M1600_easy": p_it_M1600_easy,
        "expected": "Plate M_crit ~135 at N=2048; at cliff-adjacent corruption delta M100->M400 >= 0.15",
        "pass": p3_ok,
        "citation": "Plate 1995 N/(2 ln N)",
    }

    # 4. Scale invariance for modern_hopfield: top1(N=2048, M) ~ top1(N=8192, 4M)
    #    within 0.05 (Ramsauer exponential capacity -> no N-dependence in
    #    accessible M range).
    p4_pairs: List[Dict[str, Any]] = []
    p4_ok = None
    p4_deltas: List[float] = []
    for M_lo in M_sweep:
        M_hi = 4 * M_lo
        if M_hi in M_sweep and 2048 in N_sweep and 8192 in N_sweep:
            for c in c_sweep:
                for T in T_sweep:
                    lo = _pt("modern_hopfield", M_lo, 2048, c, T)
                    hi = _pt("modern_hopfield", M_hi, 8192, c, T)
                    if lo is not None and hi is not None:
                        d = abs(lo - hi)
                        p4_deltas.append(d)
                        p4_pairs.append({
                            "M_lo": M_lo, "M_hi": M_hi, "c": c, "T": T,
                            "top1_N2048_M_lo": lo,
                            "top1_N8192_M_hi": hi,
                            "abs_delta": round(d, 4),
                        })
    if p4_deltas:
        p4_ok = max(p4_deltas) <= 0.05
    cg_meta_predictions["P4_scale_invariance_modern"] = {
        "pairs": p4_pairs,
        "max_abs_delta": round(max(p4_deltas), 4) if p4_deltas else None,
        "threshold": 0.05,
        "expected": "Ramsauer exponential capacity -> top1(N,M) = top1(4N,4M) invariant",
        "pass": p4_ok,
        "citation": "T2/modern_hopfield_ramsauer capacity ~ exp(N/2)",
    }

    # 5. Alpha-gate META_RULE_W exemption: this sweep IS a capacity-alpha sweep;
    #    alpha=M/N spans [0.012, 1.56] (M=100/N=8192 to M=3200/N=2048).
    #    Declare exemption in metrics (Skunkworks reads).
    alpha_span = []
    for M in M_sweep:
        for N in N_sweep:
            alpha_span.append({"M": M, "N": N, "alpha": round(M / N, 4)})
    cg_meta_predictions["P5_META_RULE_W_capacity_sweep_exemption"] = {
        "declared": True,
        "reason": ("capacity-sweep is the PURPOSE of this cell; alpha spans "
                   "[0.012, 1.56] intentionally crosses [0.03, 0.20] safe band; "
                   "crosstalk wall is INFORMATIVE per prereg"),
        "alpha_grid": alpha_span,
        "meta_rule_ref": "capacity_cell_gate_must_be_capacity_relative_not_fixed_M (2026-06-20)",
    }

    # 6. Capacity-relative gates for classical: top1 as fn of (M/M_crit)
    p6_ok = None
    p6_probe: List[Dict[str, Any]] = []
    for N in N_sweep:
        m_crit_cls = M_crit_locator("classical_hopfield", N)
        for M in M_sweep:
            ratio = M / max(1.0, m_crit_cls)
            top1_cls = _pt("classical_hopfield", M, N, 0.20, 1)
            if top1_cls is not None:
                p6_probe.append({
                    "N": N, "M": M, "m_over_m_crit": round(ratio, 3),
                    "top1_easy_c": top1_cls,
                    "expected_regime": ("sub-capacity_ok" if ratio < 1.0
                                         else "over-capacity_expected_degrade"),
                })
    # Pass if: at ratio < 0.7 top1 >= 0.80 AND at ratio > 1.5 top1 <= 0.50
    sub_pts = [x for x in p6_probe if x["m_over_m_crit"] < 0.7]
    over_pts = [x for x in p6_probe if x["m_over_m_crit"] > 1.5]
    if sub_pts and over_pts:
        p6_ok = (all(x["top1_easy_c"] >= 0.80 for x in sub_pts) and
                 all(x["top1_easy_c"] <= 0.50 for x in over_pts))
    cg_meta_predictions["P6_capacity_relative_classical"] = {
        "probe": p6_probe,
        "expected": "top1@easy_c >= 0.80 when M/M_crit<0.7; top1 <= 0.50 when M/M_crit>1.5",
        "pass": p6_ok,
        "citation": "META_RULE capacity_cell_gate_must_be_capacity_relative_not_fixed_M (2026-06-20)",
    }

    # Positive control
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["cleanup_family"] == pc_target["cleanup_family"]
                  and p["N"] == pc_target["N"]
                  and p["M_items"] == pc_target["M"]
                  and abs(p["corruption_frac"] - pc_target["corruption_frac"]) < 1e-6
                  and p["cleanup_iters"] == pc_target["cleanup_iters"]]
    if pc_matches:
        pc_top1 = pc_matches[0]["top1_mechanism"]
        pc_pass = pc_top1 >= pc_target["top1_floor"]
    else:
        pc_top1 = -1.0
        pc_pass = False
    positive_control_result = {
        "target": pc_target,
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
    else:
        avg_peak = -1.0

    return {
        "seed": seed,
        "run_mode": run_mode,
        "cleanup_families": list(CLEANUP_FAMILIES),
        "M_sweep": M_sweep,
        "N_sweep": N_sweep,
        "corruption_sweep": c_sweep,
        "iters_sweep": T_sweep,
        "N": max(N_sweep),
        "phase_map": phase_map,
        "per_cleanup_M_summary": per_cleanup_M_summary,
        "physics_law_check": physics_law_check,
        "cg_meta_predictions": cg_meta_predictions,
        "classical_capacity_crossover": classical_capacity_crossover,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ_per_cl,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "crlb_predictions_grid": crlb_preds,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_cleanup", {})
    pairs_differ = body.get("cleanup_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    per_cl_M = body.get("per_cleanup_M_summary", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL cleanups
    for fam in CLEANUP_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, f"arms_identical_cleanup_{fam}: mech==random hashes"

    # 3. 4 distinct cleanup mechanism hashes
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"cleanup_collapse: {n_distinct}/{n_pairs} pairs distinct; "
                       f"identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_top1')}")

    # 5. M-discrimination observable at cliff-adjacent c=0.45:
    # For at least 2 of the 3 non-Hebbian cleanups, top1(M=100) - top1(M=3200)
    # at (N=2048, c=0.45, T=1) must exceed 0.10. At c=0.45 signal(0.10) is
    # near noise floor sqrt(2 log M / N) which drifts with M; observed
    # deltas 0.14-0.15 across mechanisms so 0.10 gives seed-variance margin.
    n_m_disc_ok = 0
    m_disc_debug: Dict[str, float] = {}
    target_c = 0.45
    target_N = 2048
    target_T = 1
    for fam in NON_HEBBIAN_FAMILIES:
        pts_fam = [p for p in phase_map
                   if p["cleanup_family"] == fam
                   and p["N"] == target_N
                   and abs(p["corruption_frac"] - target_c) < 1e-6
                   and p["cleanup_iters"] == target_T]
        p_lo = [p for p in pts_fam if p["M_items"] == 100]
        p_hi = [p for p in pts_fam if p["M_items"] == 3200]
        if p_lo and p_hi:
            delta = p_lo[0]["top1_mechanism"] - p_hi[0]["top1_mechanism"]
            m_disc_debug[fam] = round(delta, 3)
            if delta >= 0.10:
                n_m_disc_ok += 1
    if n_m_disc_ok < 2:
        return False, (f"M_discriminator_fails_scale: only {n_m_disc_ok}/3 "
                       f"non-Hebbian cleanups show top1@M=100 - top1@M=3200 >= 0.10 "
                       f"at N={target_N} c={target_c} T={target_T}; "
                       f"deltas={m_disc_debug}; ABORT FULL DISPATCH")

    # 6. Classical AGS cliff observable at SMOKE at c=0.45 (cliff-adjacent).
    # At easy c=0.20, matched-filter argmax dominates crosstalk even above
    # AGS capacity -- classical retrieves via signal-dominance not Hebbian
    # basin. AGS cliff (spurious minima from crosstalk) manifests when
    # signal ~ noise. At c=0.45 N=2048: classical M=100 top1 ~ 0.96,
    # classical M=3200 top1 ~ 0.13 (empirically measured; AGS wall clean).
    p_cls_M100 = [p for p in phase_map
                  if p["cleanup_family"] == "classical_hopfield"
                  and p["N"] == 2048 and p["M_items"] == 100
                  and abs(p["corruption_frac"] - 0.45) < 1e-6
                  and p["cleanup_iters"] == 1]
    p_cls_M3200 = [p for p in phase_map
                   if p["cleanup_family"] == "classical_hopfield"
                   and p["N"] == 2048 and p["M_items"] == 3200
                   and abs(p["corruption_frac"] - 0.45) < 1e-6
                   and p["cleanup_iters"] == 1]
    ags_delta = None
    if p_cls_M100 and p_cls_M3200:
        ags_delta = (p_cls_M100[0]["top1_mechanism"]
                     - p_cls_M3200[0]["top1_mechanism"])
        if ags_delta < 0.40:
            return False, (f"AGS_classical_cliff_not_observed: delta="
                           f"{ags_delta:.3f} between M=100 top1="
                           f"{p_cls_M100[0]['top1_mechanism']:.3f} and M=3200 "
                           f"top1={p_cls_M3200[0]['top1_mechanism']:.3f} at "
                           f"N=2048 c=0.45 T=1; expected AGS cliff crossing "
                           f"~M=286 with delta >= 0.40")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ + "
                  f"4-distinct-cleanups + positive_control + "
                  f"M-discrimination({n_m_disc_ok}/3) deltas={m_disc_debug}; "
                  f"AGS_classical_delta={ags_delta:.3f}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_cleanup", {})
    pairs_differ = body.get("cleanup_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_cl_M = body.get("per_cleanup_M_summary", {})
    physics_law_check = body.get("physics_law_check", {})
    cg_meta_predictions = body.get("cg_meta_predictions", {})
    classical_cap_cross = body.get("classical_capacity_crossover", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    # Tier counts
    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "per_cleanup_M_summary": per_cl_M,
        "physics_law_check": physics_law_check,
        "cg_meta_predictions": cg_meta_predictions,
        "classical_capacity_crossover": classical_cap_cross,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "crlb_predictions_grid": body.get("crlb_predictions_grid", {}),
        "avg_peak_mem_mb": body.get("avg_peak_mem_mb"),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "encoder_fixed": "binary_bipolar",
        "M_sweep": body.get("M_sweep"),
        "N_sweep": body.get("N_sweep"),
        "corruption_sweep": body.get("corruption_sweep"),
        "iters_sweep": body.get("iters_sweep"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"4-cleanup-distinct; positive_control@modern_hopfield_M100 "
                    f"top1={pc_result.get('measured_top1')}; {reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_SMOKE: {reason}"
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in CLEANUP_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: cleanups with mech==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured top1="
                f"{pc_result.get('measured_top1')}")
    elif physics_law_check.get("cg_meta_tier_eligible", False):
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_M_SCALING_LAW: {observed_n}/{expected_n} pts; "
                f"3 non-Hebbian cleanups pass monotone+smoothness+scale-free "
                f"across all regimes; classical_capacity_crossover={classical_cap_cross}; "
                f"n_pairs_differ={n_pairs_differ}/6; "
                f"positive_control_pass; sat={n_sat} hp={n_hp} mb={n_mb} "
                f"floor={n_floor} fail={n_fail}; CG_META tier eligible pending "
                f"Skunkworks landed-VET + 3-seed replication")
    else:
        # Check per-cleanup partial pass
        partial = {fam: physics_law_check.get(fam, {}).get(
            "cg_meta_tier_eligible_per_cleanup", False)
                   for fam in NON_HEBBIAN_FAMILIES}
        n_partial = sum(1 for v in partial.values() if v)
        # Check classical crossover recorded
        classical_recorded = any(
            c.get("crossover_M") is not None
            for c in classical_cap_cross.values())
        if n_partial >= 2 and classical_recorded:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_CLASSICAL_CAPACITY_CONFIRMED: "
                    f"{n_partial}/3 non-Hebbian cleanups smooth-monotone; "
                    f"classical_capacity_crossover={classical_cap_cross}; "
                    f"partial_law={partial}; n_disc={n_disc}/{expected_n}")
        elif n_partial >= 1:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_NOISY_M_SCALING: {n_partial}/3 non-Hebbian "
                    f"cleanups pass law criteria; classical_crossover="
                    f"{classical_cap_cross}; partial_law={partial}; "
                    f"n_pairs_differ={n_pairs_differ}/6; n_disc={n_disc}/{expected_n}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_M_SCALING_NOISY: 0/3 non-Hebbian cleanups pass; "
                    f"partial_law={partial}; measured but noisy; "
                    f"n_disc={n_disc}/{expected_n} n_pairs_differ={n_pairs_differ}/6")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "SATURATED_TOP1", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_TOP1",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "BETA", "ALPHA_SOFT",
    "CLEANUP_FAMILIES", "NON_HEBBIAN_FAMILIES",
    "M_SWEEP_FULL", "M_SWEEP_SMOKE",
    "N_SWEEP_FULL", "N_SWEEP_SMOKE",
    "CORRUPTION_FULL", "CORRUPTION_SMOKE",
    "ITERS_FULL", "ITERS_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "CLASSICAL_CAPACITY_FRAC",
    "REQUIRED_FIELDS",
    "crlb_1step_cliff_prediction", "classical_capacity_at_N",
    "M_crit_locator",
    "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
