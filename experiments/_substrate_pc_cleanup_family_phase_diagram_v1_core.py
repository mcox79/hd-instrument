"""Shared core for substrate_pc_cleanup_family_phase_diagram_v1 sibling cells.

THIRD COMPONENT-SUBSTITUTION phase diagram (after encoder-family for PC +
encoder-family for sequence-binding). USER directive 2026-06-28 (Research):
fill out comprehensive phase diagrams across COMPONENTS. Cleanup-attractor
mechanism is the 2nd-most-load-bearing lever (after encoder). Current
default modern-Hopfield softmax has never been independently audited.

Cleanup families (OUTER axis):
    modern_hopfield      : Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)
    classical_hopfield   : Q_{t+1} = sign(Q_t @ W) where W = X.T @ X / M (Hebbian)
    iterative_cosine     : Q_{t+1} = X[argmax(Q_t @ X.T)] (snap to nearest)
    soft_energy_attractor: Q_{t+1} = sign(Q_t + alpha*(softmax(beta * Q_t @ X.T) @ X - Q_t))

Inner axes: N (2048, 8192) x corruption (5 pts) x cleanup_iters (1, 5).
4 cleanups * 2 N * 5 c * 2 T = 80 phase points per seed FULL.
4 cleanups * 1 N * 3 c * 1 T = 12 corner points per seed SMOKE.

Encoder FIXED: binary_bipolar dense codebook (PC v2.2 default).

PRE-REG: preregs/2026-06-28_substrate_pc_cleanup_family_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    CLEANUP_FAMILIES,
    N_SWEEP_FULL, CORRUPTION_FULL, ITERS_FULL,
    N_SWEEP_SMOKE, CORRUPTION_SMOKE, ITERS_SMOKE,
    M_ITEMS_FULL, M_ITEMS_SMOKE

ASCII-only. No unicode. CUDA preferred; CPU fully supported (no GPU mandate).

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan)
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
ALPHA_SOFT = 0.5  # soft_energy_attractor mixing rate

# Cleanup families (OUTER axis; LOCKED at module init)
CLEANUP_FAMILIES = ("modern_hopfield", "classical_hopfield",
                    "iterative_cosine", "soft_energy_attractor")

# Sweep axes
N_SWEEP_FULL = [2048, 8192]
CORRUPTION_FULL = [0.20, 0.35, 0.45, 0.475, 0.50]
ITERS_FULL = [1, 5]
M_ITEMS_FULL = 300

N_SWEEP_SMOKE = [2048]
CORRUPTION_SMOKE = [0.20, 0.45, 0.50]
ITERS_SMOKE = [1]
M_ITEMS_SMOKE = 200

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(CLEANUP_FAMILIES) * len(N_SWEEP_FULL)
                         * len(CORRUPTION_FULL) * len(ITERS_FULL))  # 80
EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_FAMILIES) * len(N_SWEEP_SMOKE)
                          * len(CORRUPTION_SMOKE) * len(ITERS_SMOKE))  # 12

# Positive control point: modern_hopfield @ N=8192, c=0.475, T=5 must reproduce
# PC v2.2 measured top1 >= 0.50 (PC v2.2 commit 2daf9b55 evidence at this
# point: top1 ~ 0.55-0.65; SAFE FLOOR for control PASS = 0.50)
POSITIVE_CONTROL = {
    "cleanup_family": "modern_hopfield",
    "N": 8192,
    "corruption_frac": 0.475,
    "cleanup_iters": 5,
    "top1_floor": 0.50,
}
# Smoke variant of positive control (smaller N, easier c)
POSITIVE_CONTROL_SMOKE = {
    "cleanup_family": "modern_hopfield",
    "N": 2048,
    "corruption_frac": 0.20,
    "cleanup_iters": 1,
    "top1_floor": 0.80,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / overlap-floor prediction (META_RULE_AG)
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, M: int) -> float:
    """1-step cliff prediction for random binary_bipolar codes.

    Matched-filter noise floor sqrt(2 log M / N); cliff = corruption where
    signal (1 - 2c) == noise floor.
    """
    if N <= 0 or M <= 1:
        return 0.0
    noise = math.sqrt(2.0 * math.log(M) / N)
    return max(0.0, 0.5 * (1.0 - noise))


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Codebook + corruption (FIXED: binary_bipolar across all cleanup arms)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense bipolar {-1, +1}^N codebook (M, N) float32 on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _corrupt_binary_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of bits. E[cos(Q, src)] = 1 - 2c."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    flips = g.random((M, N)) < c
    flips_t = torch.from_numpy(flips).to(DEVICE)
    Q = X.clone()
    Q[flips_t] = -Q[flips_t]
    return Q


def _random_floor_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    """Fresh-random codebook entry (independent of source X) for floor arm."""
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _sign_op(V: "torch.Tensor") -> "torch.Tensor":
    """sign() with 0 -> +1 to stay bipolar."""
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


# ---------------------------------------------------------------------------
# Cleanup family implementations
# ---------------------------------------------------------------------------
def _modern_hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor",
                              T: int, beta: float) -> "torch.Tensor":
    """T-step modern-Hopfield: Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)."""
    Q = Q0
    for _ in range(max(0, T)):
        sims = Q @ X.T  # (M, M_items)
        p = torch.softmax(beta * sims, dim=1)  # (M, M_items)
        Q_new = p @ X  # (M, N) mixture
        Q = _sign_op(Q_new)
    return Q


def _classical_hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor",
                                 T: int, beta: float) -> "torch.Tensor":
    """T-step classical Hopfield: Q_{t+1} = sign(Q_t @ W) where W = X.T @ X / M.

    Hebbian outer-product weight matrix. Batched-parallel sign update (not
    async-sequential bit). Capacity ~0.14*N; at M/N > 0.14, spurious minima
    dominate.
    """
    M_items, N = X.shape
    # Hebbian weight matrix (zero-diagonal convention to avoid self-coupling)
    W = (X.T @ X) / float(M_items)  # (N, N)
    # Zero diagonal (standard classical Hopfield convention)
    W.fill_diagonal_(0.0)
    Q = Q0
    for _ in range(max(0, T)):
        h = Q @ W  # (M, N) local field
        Q = _sign_op(h)
    return Q


def _iterative_cosine_cleanup(Q0: "torch.Tensor", X: "torch.Tensor",
                               T: int, beta: float) -> "torch.Tensor":
    """T-step iterative cosine snap: Q_{t+1} = X[argmax(Q_t @ X.T)].

    No softmax, no mixing - pick argmax codeword and snap exactly. If the
    correct codeword is the argmax, fixed point at T=1; otherwise can flip
    among incorrect codewords (oscillation possible but bounded in M).
    """
    Q = Q0
    for _ in range(max(0, T)):
        sims = Q @ X.T  # (M, M_items)
        idx = sims.argmax(dim=1)  # (M,)
        Q = X[idx]  # snap to nearest codeword
    return Q


def _soft_energy_attractor_cleanup(Q0: "torch.Tensor", X: "torch.Tensor",
                                    T: int, beta: float) -> "torch.Tensor":
    """T-step soft-energy gradient: damped move toward modern-Hopfield target.

    Q_{t+1} = sign(Q_t + alpha * (softmax(beta * Q_t @ X.T) @ X - Q_t))

    alpha=ALPHA_SOFT (0.5) - half-step toward softmax target each iter. At
    alpha=1.0 equivalent to modern_hopfield. At alpha=0.0 identity (no
    update). 0.5 gives smoother basin descent.
    """
    Q = Q0
    alpha = ALPHA_SOFT
    for _ in range(max(0, T)):
        sims = Q @ X.T
        p = torch.softmax(beta * sims, dim=1)
        target = p @ X  # (M, N) modern-Hopfield target
        Q_new = Q + alpha * (target - Q)
        Q = _sign_op(Q_new)
    return Q


_CLEANUP_REGISTRY = {
    "modern_hopfield": _modern_hopfield_cleanup,
    "classical_hopfield": _classical_hopfield_cleanup,
    "iterative_cosine": _iterative_cosine_cleanup,
    "soft_energy_attractor": _soft_energy_attractor_cleanup,
}


def _top1_recall(Q_final: "torch.Tensor", X: "torch.Tensor",
                  target_idx: "torch.Tensor") -> float:
    """Top-1 recall: fraction where argmax(Q_final @ X.T) == target_idx."""
    sims = Q_final @ X.T
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(cleanup_family: str, N: int, corruption: float, T: int,
                      M: int, seed: int) -> Dict[str, Any]:
    """Run one (cleanup, N, c, T) phase point with both arms."""
    if cleanup_family not in _CLEANUP_REGISTRY:
        raise ValueError(f"unknown cleanup_family={cleanup_family!r}")
    cleanup_fn = _CLEANUP_REGISTRY[cleanup_family]

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build codebook + targets (same encoder across all cleanup arms; seeded
    # by seed so all 4 cleanup arms see IDENTICAL X for fair comparison)
    X = _build_binary_bipolar(M, N, seed)
    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(corruption * 1000)

    # ARM_MECHANISM: corruption -> cleanup
    Q_sub_0 = _corrupt_binary_bipolar(X, corruption, sub_seed)
    Q_sub_T = cleanup_fn(Q_sub_0, X, T, BETA)
    top1_sub = _top1_recall(Q_sub_T, X, target_idx)
    # Output bytes hash for cleanup-distinctness check (per-point); catches
    # mechanism collapse even when top1 happens to agree across cleanups
    mech_output_hash = hashlib.sha256(
        Q_sub_T.cpu().numpy().tobytes()).hexdigest()[:16]

    # ARM_RANDOM_FLOOR: fresh-random codebook entry instead of corrupted source
    Q_rnd_0 = _random_floor_binary_bipolar(M, N, sub_seed)
    Q_rnd_T = cleanup_fn(Q_rnd_0, X, T, BETA)
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx)
    rnd_output_hash = hashlib.sha256(
        Q_rnd_T.cpu().numpy().tobytes()).hexdigest()[:16]

    # Calibration check: initial cosine of Q_sub_0 vs X (sanity)
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
        "cleanup_family": cleanup_family,
        "N": N,
        "corruption_frac": corruption,
        "cleanup_iters": T,
        "M_items": M,
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
    }


# ---------------------------------------------------------------------------
# Selftest (cleanup mechanism sanity + CRLB + cardinality)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Cleanup mechanism sanity + CRLB + cardinality.

    For each cleanup family at N=512, M=20:
      (a) at c=0.0, T=1: top1 == 1.0 (identity check; cleanup doesn't break clean)
      (b) at c=0.10, T=1: top1 >= 0.5 (easy regime; all cleanups must recover)
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 80:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 80"
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB formula sanity (N=2048, M=300 cliff in [0.40, 0.50])
    c1 = crlb_1step_cliff_prediction(2048, M_ITEMS_FULL)
    c2 = crlb_1step_cliff_prediction(8192, M_ITEMS_FULL)
    if not (0.40 < c1 < 0.50):
        return False, f"crlb N=2048 M=300 outside [0.40, 0.50]: {c1}"
    if not (0.40 < c2 < 0.50):
        return False, f"crlb N=8192 M=300 outside [0.40, 0.50]: {c2}"
    if not (c2 > c1):
        return False, f"cliff should shift right with N: c1={c1} c2={c2}"
    msgs.append(f"crlb N=2048 cliff={c1:.4f}; N=8192 cliff={c2:.4f}")

    # 3. Cleanup mechanism sanity
    M_san = 20
    N_san = 512
    X = _build_binary_bipolar(M_san, N_san, seed)
    target_idx = torch.arange(M_san, device=DEVICE)

    for fam in CLEANUP_FAMILIES:
        cleanup_fn = _CLEANUP_REGISTRY[fam]

        # (a) Identity at c=0.0, T=1
        Q0 = X.clone()
        Q1 = cleanup_fn(Q0, X, 1, BETA)
        n_hit_id = int((Q1 @ X.T).argmax(dim=1).eq(target_idx).sum().item())
        if n_hit_id < M_san:
            return False, (
                f"identity FAIL {fam}: at c=0.0 T=1 only {n_hit_id}/{M_san} "
                f"clean items preserved")

        # (b) Easy regime c=0.10
        Q0 = _corrupt_binary_bipolar(X, 0.10, seed * 2)
        Q1 = cleanup_fn(Q0, X, 1, BETA)
        n_hit = int((Q1 @ X.T).argmax(dim=1).eq(target_idx).sum().item())
        if n_hit < M_san * 0.5:
            return False, (
                f"easy-regime FAIL {fam}: at c=0.10 N={N_san} M={M_san} "
                f"only {n_hit}/{M_san} recovered after T=1")
        msgs.append(f"sanity {fam}: c=0.0 id={n_hit_id}/{M_san}; "
                    f"c=0.10 recovered {n_hit}/{M_san}")

    del X, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    # 4. Cleanup mechanism output bytes differ at the CLIFF regime (c=0.475,
    # N=1024, M=50, T=1). At low c (clean regime), modern_hopfield collapses
    # to iterative_cosine because beta=8.0 makes softmax = argmax when the
    # top-1 codeword is well-separated. At the cliff (c near 0.475), the
    # argmax is contested and modern_hopfield's softmax MIXING distinguishes
    # it from iterative_cosine's pure-snap. This is the cell-level
    # discriminator-distinctness check + an empirical note: at HIGH-CONFIDENCE
    # regimes, modern_hopfield = iterative_cosine = soft_energy_attractor
    # collapse together (only classical_hopfield differs there).
    M_diff = 50
    N_diff = 1024
    X_diff = _build_binary_bipolar(M_diff, N_diff, seed)
    c_diff = 0.475  # cliff regime; argmax is contested -> mechanisms diverge
    Q0_diff = _corrupt_binary_bipolar(X_diff, c_diff, seed * 100 + int(c_diff * 1000))
    hashes = {}
    for fam in CLEANUP_FAMILIES:
        cleanup_fn = _CLEANUP_REGISTRY[fam]
        Q1 = cleanup_fn(Q0_diff, X_diff, 1, BETA)
        out_bytes = Q1.cpu().numpy().tobytes()
        h = hashlib.sha256(out_bytes).hexdigest()[:16]
        hashes[fam] = h
    if len(set(hashes.values())) != len(CLEANUP_FAMILIES):
        return False, (f"cleanup outputs NOT distinct at seed={seed} "
                        f"cliff regime c={c_diff} T=1: {hashes}; "
                        f"some cleanups producing identical bipolar output bytes")
    msgs.append(f"cleanup byte-hashes distinct at cliff c={c_diff} T=1: {hashes}")

    del X_diff, Q0_diff
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (cleanup, N, c, T) phase points for one seed; return result dict."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_sweep = N_SWEEP_SMOKE
        c_sweep = CORRUPTION_SMOKE
        T_sweep = ITERS_SMOKE
        M_items = M_ITEMS_SMOKE
    else:
        N_sweep = N_SWEEP_FULL
        c_sweep = CORRUPTION_FULL
        T_sweep = ITERS_FULL
        M_items = M_ITEMS_FULL

    expected_n_units = (len(CLEANUP_FAMILIES) * len(N_sweep)
                        * len(c_sweep) * len(T_sweep))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"cleanups={CLEANUP_FAMILIES} N_sweep={N_sweep} c={c_sweep} T={T_sweep} "
          f"M={M_items} expected_n={expected_n_units}", flush=True)

    crlb_preds = {f"N{N}": round(crlb_1step_cliff_prediction(N, M_items), 4)
                  for N in N_sweep}
    print(f"[crlb] 1-step cliff predictions: {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in CLEANUP_FAMILIES:
        for N in N_sweep:
            for T in T_sweep:
                for c in c_sweep:
                    print(f"[point] seed={seed} cleanup={fam} N={N} c={c:.3f} T={T} ...",
                          flush=True)
                    pt = eval_phase_point(fam, N, c, T, M_items, seed)
                    phase_map.append(pt)
                    print(f"  -> top1_mech={pt['top1_mechanism']:.3f} "
                          f"top1_rnd={pt['top1_random']:.3f} "
                          f"disc={pt['discriminator']:.3f} "
                          f"tier={pt['verdict_tier_per_point']} "
                          f"cal_cos={pt['calibration_cos_q0_x']:.3f} "
                          f"peak_mb={pt['peak_mem_mb']:.1f} "
                          f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-cleanup arms-differ hashes (use OUTPUT-BYTES hashes per point,
    # not top1 alone; catches mechanism collapse where top1 agrees but
    # bipolar outputs differ -- modern_hopfield vs iterative_cosine at
    # high-confidence regimes is the canonical case)
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

    # Cleanup-pair distinctness (META_RULE_AF extension)
    pairs_differ = {}
    fams = list(CLEANUP_FAMILIES)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (cleanup_mech_hashes[fams[i]]
                                 != cleanup_mech_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Per-cleanup summary
    per_cleanup_summary: Dict[str, Dict[str, Any]] = {}
    for fam in CLEANUP_FAMILIES:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        top1s = [p["top1_mechanism"] for p in fam_pts]
        top1_mean = float(np.mean(top1s)) if top1s else 0.0
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # Cliff locator: per (N, T), smallest c where top1 < 0.50
        cliff_locator: Dict[str, float] = {}
        for N in N_sweep:
            for T in T_sweep:
                cliff = -1.0
                for c in c_sweep:
                    matches = [p for p in fam_pts
                               if p["N"] == N and p["cleanup_iters"] == T
                               and abs(p["corruption_frac"] - c) < 1e-6]
                    if matches and matches[0]["top1_mechanism"] < MIDDLE_BAND_LO:
                        cliff = c
                        break
                cliff_locator[f"N{N}_T{T}"] = cliff
        per_cleanup_summary[fam] = {
            "top1_mean": round(top1_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "cliff_locator": cliff_locator,
        }

    # Tier the cleanups (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_cleanup_summary[fam]["top1_mean"] for fam in CLEANUP_FAMILIES}
    best_mean = max(means.values()) if means else 0.0
    cleanup_tiers: Dict[str, str] = {}
    for fam in CLEANUP_FAMILIES:
        m = means[fam]
        if m >= best_mean - 0.05:
            if m == best_mean:
                others = [v for k, v in means.items() if k != fam]
                next_best = max(others) if others else 0.0
                if m - next_best > 0.10:
                    cleanup_tiers[fam] = "DOMINANT_CLEANUP"
                else:
                    cleanup_tiers[fam] = "COMPETITIVE_CLEANUP"
            else:
                cleanup_tiers[fam] = "COMPETITIVE_CLEANUP"
        else:
            cleanup_tiers[fam] = "DOMINATED_CLEANUP"

    # Skunkworks N-drop check: compare delta-top1 from N=8192 to N=2048
    # for modern_hopfield vs classical_hopfield (only meaningful if FULL has both N)
    skunkworks_n_drop_check: Dict[str, Any] = {"applicable": False}
    if len(N_sweep) >= 2 and 2048 in N_sweep and 8192 in N_sweep:
        # Average top1 across c x T at each N for both cleanups
        def avg_at_N(fam: str, N_val: int) -> float:
            pts = [p["top1_mechanism"] for p in phase_map
                   if p["cleanup_family"] == fam and p["N"] == N_val]
            return float(np.mean(pts)) if pts else -1.0
        mod_n2 = avg_at_N("modern_hopfield", 2048)
        mod_n8 = avg_at_N("modern_hopfield", 8192)
        cls_n2 = avg_at_N("classical_hopfield", 2048)
        cls_n8 = avg_at_N("classical_hopfield", 8192)
        # "Wins at N drop" = modern HOLDS UP more at low N than classical
        # delta = top1(N=2048) - top1(N=8192); more positive = holds up better at low N
        mod_delta = mod_n2 - mod_n8
        cls_delta = cls_n2 - cls_n8
        skunkworks_n_drop_check = {
            "applicable": True,
            "modern_hopfield_top1_at_N2048": round(mod_n2, 4),
            "modern_hopfield_top1_at_N8192": round(mod_n8, 4),
            "modern_hopfield_delta_lowN_minus_highN": round(mod_delta, 4),
            "classical_hopfield_top1_at_N2048": round(cls_n2, 4),
            "classical_hopfield_top1_at_N8192": round(cls_n8, 4),
            "classical_hopfield_delta_lowN_minus_highN": round(cls_delta, 4),
            # If modern delta > classical delta, modern "holds up better at low N"
            # (i.e. it wins more at the low-N regime relative to its own high-N)
            "modern_wins_at_N_drop": mod_delta > cls_delta,
            "interpretation": (
                "modern_wins_at_N_drop=True confirms Skunkworks informal "
                "finding: modern Hopfield outperforms classical Hopfield more "
                "at low N (relative to each at high N)"
            ),
        }

    # Positive control check
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["cleanup_family"] == pc_target["cleanup_family"]
                  and p["N"] == pc_target["N"]
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

    return {
        "seed": seed,
        "run_mode": run_mode,
        "cleanup_families": list(CLEANUP_FAMILIES),
        "N_sweep": N_sweep,
        "corruption_sweep": c_sweep,
        "iters_sweep": T_sweep,
        "M_items": M_items,
        "N": max(N_sweep),  # PROT-021 N stamp
        "phase_map": phase_map,
        "per_cleanup_summary": per_cleanup_summary,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ_per_cl,
        "positive_control_result": positive_control_result,
        "skunkworks_n_drop_check": skunkworks_n_drop_check,
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
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate. Return (passed, reason)."""
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_cleanup", {})
    pairs_differ = body.get("cleanup_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL cleanups
    for fam in CLEANUP_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, f"arms_identical_cleanup_{fam}: mech and random hashes match"

    # 3. 4 distinct cleanup mechanism hashes (all 6 pairs differ)
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"cleanup_collapse: {n_distinct}/{n_pairs} cleanup pairs "
                       f"distinct; identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_top1')}; "
                       f"test rig broken")

    # 5. Cliff observable: at least 1 cleanup shows top1 in [0.10, 0.95] at c=0.45
    cliff_pts = [p for p in phase_map
                 if abs(p["corruption_frac"] - 0.45) < 1e-6
                 and 0.10 < p["top1_mechanism"] < 0.95]
    if not cliff_pts:
        cliff_vals = {f"{p['cleanup_family']}_N{p['N']}": p["top1_mechanism"]
                      for p in phase_map if abs(p["corruption_frac"] - 0.45) < 1e-6}
        return False, (f"discriminator_fails_scale: c=0.45 produced no cliff-edge "
                       f"values; all in [0, 0.10] or [0.95, 1.0]: {cliff_vals}; "
                       f"ABORT FULL DISPATCH")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ(4 cleanups) + "
                  f"4-distinct-cleanups + positive_control_pass + cliff_observable")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    """Aggregate one-seed partial into final metrics with verdict."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
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
    per_cl_summary = body.get("per_cleanup_summary", {})
    cleanup_tiers = body.get("cleanup_tiers", {})
    skunk_check = body.get("skunkworks_n_drop_check", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    # GPU util estimate
    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 50.0))
    else:
        gpu_util_estimate = 0.0

    # Tier counts (overall)
    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "per_cleanup_summary": per_cl_summary,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ,
        "positive_control_result": pc_result,
        "skunkworks_n_drop_check": skunk_check,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "crlb_predictions_1step": body.get("crlb_predictions_1step", {}),
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "encoder_fixed": "binary_bipolar",
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"4-cleanup-distinct; positive_control@modern_hopfield "
                    f"top1={pc_result.get('measured_top1'):.3f}; "
                    f"cleanup_tiers={cleanup_tiers}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
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
                f"{pc_result.get('measured_top1')}; test rig broken; "
                f"any cleanup-discrimination framing UNTRUSTED")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_NULL_CLEANUP_INVARIANCE: all 4 cleanups produced "
                f"identical mechanism hashes; cleanup is NOT a discriminating "
                f"lever for PC in this regime; honest negative; n_disc={n_disc}/80")
    elif n_disc >= 24 and n_pairs_differ >= 2:
        any_real_cliff = False
        for fam, summ in per_cl_summary.items():
            for cliff_key, cliff_val in summ.get("cliff_locator", {}).items():
                if 0.20 < cliff_val < 0.50:
                    any_real_cliff = True
                    break
            if any_real_cliff:
                break
        if any_real_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_CLEANUP_DISCRIMINATION: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"n_pairs_differ={n_pairs_differ}/6; cleanup_tiers={cleanup_tiers}; "
                    f"positive_control_pass; skunk_n_drop="
                    f"{skunk_check.get('modern_wins_at_N_drop')}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_CLEANUP_DIFFERS_BUT_NO_CLIFF: cleanups distinguish "
                    f"but no interior cliff; n_disc={n_disc}/80; "
                    f"n_pairs_differ={n_pairs_differ}/6; cleanup_tiers={cleanup_tiers}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_CLEANUP_DIFFERS_BUT_LOW_DISC: n_disc={n_disc}/80 "
                f"(need >=24); n_pairs_differ={n_pairs_differ}/6 (need >=2); "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"cleanup_tiers={cleanup_tiers}")

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
    "CLEANUP_FAMILIES",
    "N_SWEEP_FULL", "CORRUPTION_FULL", "ITERS_FULL", "M_ITEMS_FULL",
    "N_SWEEP_SMOKE", "CORRUPTION_SMOKE", "ITERS_SMOKE", "M_ITEMS_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "crlb_1step_cliff_prediction", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
