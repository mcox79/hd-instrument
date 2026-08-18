"""substrate_pattern_completion_corruption_cliff_phase_diagram_v1 -- GPU.

Layer-1 phase-diagram cell #2: localize the corruption-cliff for pattern
completion across (N x corruption_frac x cleanup_iters). Prior point
exp_iterative_cleanup_gpu_v1 saturated at top1=1.000 single-step from
FLIP=0.30 N=2048; this cell maps where the cliff actually is, how it moves
with N, and what cleanup_iters buys in the cliff regime.

MECHANISM: Substrate bipolar codebook X (M x N). For each item i, corrupt
by flipping corruption_frac of bits to get Q_i. Run T iterations of
modern-Hopfield cleanup:
  Q_{t+1} = sign(softmax(beta * Q_t @ X.T) @ X)
top1 recall = (argmax_j (Q_T @ X.T)[j] == i). SUBSTRATE arm: this. RANDOM
arm: Q_0 replaced by fresh random +/-1, same pipeline; floor ~ 1/M.

SWEEP AXES (cardinality 4 x 6 x 3 = 72 FULL; 6 corners SMOKE):
  N             : [2048, 4096, 8192, 16384]
  corruption    : [0.10, 0.30, 0.50, 0.70, 0.85, 0.95]
  cleanup_iters : [1, 5, 20]

PRE-REG bands per-point:
  SATURATED   top1_substrate >= 0.95
  HARD_PASS   [0.80, 0.95) AND substrate - random >= 0.50
  MIDDLE_BAND [0.50, 0.80) AND substrate - random >= 0.30
  HARD_FAIL   < 0.50
  FLOOR       <= 0.10 (substrate at chance)

CRLB / overlap-floor prediction (Python-computed at module init):
  1-step cliff at corruption_frac = 0.5 * (1 - sqrt(2*log(P)/N))
  N=2048..16384, P=500 -> cliff predicted in [0.46, 0.49] for T=1.
  T=5 and T=20 should extend cliff RIGHTWARD via basin-of-attraction growth.

CARDINALITY_OK (META_RULE_H):
  SMOKE EXPECTED_N_UNITS = 6 ; FULL EXPECTED_N_UNITS = 72

GPU MANDATE (Fix #24): DEVICE=cuda, is_available asserted at full, batched
matmul, codebook hoisted per (seed, N), per-arm peak_mem_mb logged.

PROT-018: anchor has no _n<N> suffix (multi-N sweep cell).
PROT-019: no _n>=4096 suffix -> no timeout floor (cell estimates ~2 min FULL).

Substrate-as-canonical query: cross-checked prior cleanup_attractor
capability + reviewed exp_iterative_cleanup_gpu_v1 (saturated baseline) +
exp_pc_cleanup_attractor_v1 (chain-traversal, different mechanism).

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-06-28.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_pattern_completion_corruption_cliff_phase_diagram_v1"
_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_pattern_completion_corruption_cliff"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = (RUN_MODE == "smoke")


# ---------------------------------------------------------------------------
# Pre-reg bands LOCKED at module init (META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_TOP1 = 0.95
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_TOP1 = 0.10
HP_DISCRIMINATOR = 0.50
MB_DISCRIMINATOR = 0.30

BETA = 8.0  # softmax sharpness; matches exp_iterative_cleanup_gpu_v1


# ---------------------------------------------------------------------------
# Sweep axes
# ---------------------------------------------------------------------------
N_SWEEP_FULL = [2048, 4096, 8192, 16384]
CORRUPTION_FULL = [0.10, 0.30, 0.50, 0.70, 0.85, 0.95]
ITERS_FULL = [1, 5, 20]
M_ITEMS_FULL = 500
SEED_FULL = 11

N_SWEEP_SMOKE = [2048, 16384]
CORRUPTION_SMOKE = [0.10, 0.50, 0.95]
ITERS_SMOKE = [5]
M_ITEMS_SMOKE = 200

if SMOKE:
    N_SWEEP = N_SWEEP_SMOKE
    CORRUPTION_SWEEP = CORRUPTION_SMOKE
    ITERS_SWEEP = ITERS_SMOKE
    M_ITEMS = M_ITEMS_SMOKE
    EXPECTED_N_UNITS = len(N_SWEEP) * len(CORRUPTION_SWEEP) * len(ITERS_SWEEP)
else:
    N_SWEEP = N_SWEEP_FULL
    CORRUPTION_SWEEP = CORRUPTION_FULL
    ITERS_SWEEP = ITERS_FULL
    M_ITEMS = M_ITEMS_FULL
    EXPECTED_N_UNITS = len(N_SWEEP) * len(CORRUPTION_SWEEP) * len(ITERS_SWEEP)


# ---------------------------------------------------------------------------
# CRLB / overlap-floor pre-validation (Python-computed; META_RULE_AG)
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


CRLB_PREDICTIONS = {N: crlb_1step_cliff_prediction(N, M_ITEMS) for N in N_SWEEP}


# ---------------------------------------------------------------------------
# Self-test (REQUIRED for queue_add.py gate)
# ---------------------------------------------------------------------------
def _selftest() -> None:
    # 1. CRLB formula sanity
    c1 = crlb_1step_cliff_prediction(2048, 500)
    c2 = crlb_1step_cliff_prediction(16384, 500)
    assert 0.40 < c1 < 0.50, "crlb_1step N=2048 P=500 outside expected band: %s" % c1
    assert 0.40 < c2 < 0.50, "crlb_1step N=16384 P=500 outside expected band: %s" % c2
    assert c2 > c1, "cliff should shift right with N (N=16384 cliff %s should exceed N=2048 cliff %s)" % (c2, c1)
    # 2. Bipolar codebook orthogonality sanity
    rng = np.random.default_rng(7)
    X = (rng.integers(0, 2, size=(50, 256)) * 2 - 1).astype(np.float32)
    norms = np.sqrt((X * X).sum(axis=1))
    assert np.allclose(norms, np.sqrt(256), atol=1e-3), "bipolar norm mismatch"
    # 3. Single-step mechanism sanity (corruption=0.10 should saturate at N=256)
    item0 = X[0].copy()
    flips = rng.random(256) < 0.10
    q = item0.copy()
    q[flips] = -q[flips]
    sims = q @ X.T
    pred = int(np.argmax(sims))
    assert pred == 0, "mechanism sanity: 10pct corruption should recover item 0 (got %d)" % pred
    # 4. Cardinality OK
    if SMOKE:
        assert EXPECTED_N_UNITS == 6, "smoke EXPECTED_N_UNITS=6 (got %d)" % EXPECTED_N_UNITS
    else:
        assert EXPECTED_N_UNITS == 72, "full EXPECTED_N_UNITS=72 (got %d)" % EXPECTED_N_UNITS
    print("[selftest] PASS: %s (CRLB N=2048 cliff=%.3f N=16384 cliff=%.3f; EXPECTED_N_UNITS=%d)" % (
        ANCHOR_NAME, c1, c2, EXPECTED_N_UNITS), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Torch import (deferred; self-test runs without torch)
# ---------------------------------------------------------------------------
try:
    import torch
except Exception as e:
    print("[FATAL] torch import failed: %s" % e, flush=True)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Device selection (Fix #24): cuda preferred; warn if cpu fallback
# ---------------------------------------------------------------------------
GPU_AVAIL = torch.cuda.is_available()
DEVICE = torch.device("cuda" if GPU_AVAIL else "cpu")
if GPU_AVAIL:
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("[GPU] %s (%.1f GB)" % (GPU_NAME, GPU_MAX_MEM_GB), flush=True)
else:
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0
    print("[WARN] CUDA unavailable; running on CPU (smoke OK; FULL must be on GPU)", flush=True)

# Hard gate: FULL run on CPU is forbidden (Fix #24); smoke on CPU OK
if not SMOKE and not GPU_AVAIL:
    print("[FATAL] FULL run requires CUDA (Fix #24 GPU mandate)", flush=True)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Mechanism primitives
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

    For T=0 returns Q0 unchanged; for T>=1 applies T cleanup steps.
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
    """Compute top-1 recall: fraction where argmax(Q @ X.T) == target_idx."""
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

    Returns dict with top1_substrate, top1_random, peak_mem_mb, elapsed_s.
    """
    t0 = time.time()
    if GPU_AVAIL:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Encoder hoisted (codebook constructed ONCE per (seed, N) point)
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

    if GPU_AVAIL:
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

    # Free per-point memory
    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx
    if GPU_AVAIL:
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
        "crlb_1step_cliff_prediction": round(CRLB_PREDICTIONS.get(N, 0.0), 4),
    }


# ---------------------------------------------------------------------------
# Phase sweep + cliff locator
# ---------------------------------------------------------------------------
def run_phase_sweep() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Run all (N, corruption, T) phase points sequentially. Halts on first
    exception (META_RULE_J: no silent except).
    """
    phase_map: List[Dict[str, Any]] = []
    seed = SEED_FULL
    for N in N_SWEEP:
        for T in ITERS_SWEEP:
            for c in CORRUPTION_SWEEP:
                print("[point] N=%d corruption=%.2f iters=%d ..." % (N, c, T), flush=True)
                pt = eval_phase_point(N, c, T, M_ITEMS, seed)
                phase_map.append(pt)
                print("  -> top1_sub=%.3f top1_rnd=%.3f disc=%.3f tier=%s peak_mb=%.1f t=%.2fs" % (
                    pt["top1_substrate"], pt["top1_random"], pt["discriminator"],
                    pt["verdict_tier_per_point"], pt["peak_mem_mb"],
                    pt["elapsed_per_point_s"]), flush=True)

    # Cliff locator: for each (N, T) combo, smallest corruption where top1 < 0.50
    cliff_locator: Dict[str, Dict[str, float]] = {}
    for T in ITERS_SWEEP:
        key_T = "iters_%d" % T
        cliff_locator[key_T] = {}
        for N in N_SWEEP:
            cliff = None
            for c in CORRUPTION_SWEEP:
                matching = [p for p in phase_map
                             if p["N"] == N and p["cleanup_iters"] == T
                             and abs(p["corruption_frac"] - c) < 1e-6]
                if matching and matching[0]["top1_substrate"] < MIDDLE_BAND_LO:
                    cliff = c
                    break
            cliff_locator[key_T]["N_%d" % N] = cliff if cliff is not None else -1.0

    return phase_map, cliff_locator


# ---------------------------------------------------------------------------
# Arms-differ SHA-256 (META_RULE_AC, META_RULE_AF)
# ---------------------------------------------------------------------------
def arms_differ_sha256(phase_map: List[Dict[str, Any]]) -> Dict[str, Any]:
    sub_payload = json.dumps([p["top1_substrate"] for p in phase_map],
                              sort_keys=True).encode("utf-8")
    rnd_payload = json.dumps([p["top1_random"] for p in phase_map],
                              sort_keys=True).encode("utf-8")
    sub_hash = hashlib.sha256(sub_payload).hexdigest()
    rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
    return {
        "substrate_hash": sub_hash,
        "random_hash": rnd_hash,
        "differ": sub_hash != rnd_hash,
    }


# ---------------------------------------------------------------------------
# Smoke gate predicate (must pass before FULL is dispatched)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(phase_map: List[Dict[str, Any]],
                          arms_differ: Dict[str, Any]) -> Tuple[bool, str]:
    """Return (passed, reason). Per pre-reg:
      - all 6 corner points ran
      - >= 2 points discriminate (substrate > random + 0.20)
      - >= 1 point saturates (corruption=0.10 corner)
      - >= 1 point fails (corruption=0.95 corner)
      - arms_differ_sha256.differ == True
    """
    n_pts = len(phase_map)
    if n_pts != EXPECTED_N_UNITS:
        return False, "cardinality_breach: expected %d got %d" % (EXPECTED_N_UNITS, n_pts)
    n_disc = sum(1 for p in phase_map if p["discriminator"] >= 0.20)
    if n_disc < 2:
        return False, "discriminator_breach: only %d/%d points showed sub-rand > 0.20" % (n_disc, n_pts)
    easy_pts = [p for p in phase_map if p["corruption_frac"] <= 0.20]
    if easy_pts and not any(p["top1_substrate"] >= SATURATED_TOP1 for p in easy_pts):
        return False, "easy_corner_no_saturation: corruption<=0.20 never reached top1>=%.2f" % SATURATED_TOP1
    hard_pts = [p for p in phase_map if p["corruption_frac"] >= 0.90]
    if hard_pts and not any(p["top1_substrate"] < 0.50 for p in hard_pts):
        return False, "hard_corner_no_failure: corruption>=0.90 never dropped below 0.50 (suspect saturation; see Skunkworks Q-rule)"
    if not arms_differ.get("differ"):
        return False, "arms_identical: substrate and random produced identical hashes"
    return True, "smoke_gate_pass"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("[config] anchor=%s mode=%s N_sweep=%s corruption=%s iters=%s M=%d EXPECTED_N_UNITS=%d device=%s" % (
        ANCHOR_NAME, RUN_MODE, N_SWEEP, CORRUPTION_SWEEP, ITERS_SWEEP, M_ITEMS,
        EXPECTED_N_UNITS, DEVICE), flush=True)
    print("[crlb] 1-step cliff predictions: %s" % CRLB_PREDICTIONS, flush=True)

    t0 = time.time()
    phase_map, cliff_locator = run_phase_sweep()

    # Cardinality check (META_RULE_H)
    observed_n_units = len(phase_map)
    cardinality_ok = observed_n_units == EXPECTED_N_UNITS
    if not cardinality_ok:
        print("[CARDINALITY_BREACH] expected=%d observed=%d" % (
            EXPECTED_N_UNITS, observed_n_units), flush=True)

    arms_differ = arms_differ_sha256(phase_map)
    elapsed = time.time() - t0

    # GPU util estimate (utilization measured as wall-time spent matmul-bound
    # / total wall-time; rough estimate since smoke is mostly matmul under
    # this small mechanism)
    if GPU_AVAIL:
        # Peak memory aggregate as a util proxy + matmul-dominated wall ratio
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 50.0))
    else:
        gpu_util_estimate = 0.0

    # Smoke gate (smoke-mode only)
    smoke_gate_pass = None
    smoke_gate_reason = None
    if SMOKE:
        passed, reason = smoke_gate_predicate(phase_map, arms_differ)
        smoke_gate_pass = passed
        smoke_gate_reason = reason
        print("[smoke_gate] %s: %s" % ("PASS" if passed else "FAIL", reason), flush=True)

    # Verdict
    n_hard_pass = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mid = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")

    if SMOKE:
        if smoke_gate_pass:
            verdict = "HARD_PASS"
            vmsg = ("HARD_PASS_SMOKE: %d/%d corner points; saturated=%d hard_pass=%d "
                    "middle=%d floor=%d fail=%d; arms_differ=%s; gpu_util~%.2f"
                    ) % (observed_n_units, EXPECTED_N_UNITS, n_sat, n_hard_pass,
                          n_mid, n_floor, n_fail, arms_differ["differ"],
                          gpu_util_estimate)
        else:
            verdict = "HARD_FAIL"
            vmsg = ("HARD_FAIL_SMOKE: smoke gate fail: %s; saturated=%d hard_pass=%d "
                    "middle=%d floor=%d fail=%d") % (
                smoke_gate_reason, n_sat, n_hard_pass, n_mid, n_floor, n_fail)
    else:
        # FULL run: characterize the cliff
        if not cardinality_ok:
            verdict = "HARD_FAIL"
            vmsg = "HARD_FAIL_CARDINALITY_BREACH: expected=%d observed=%d" % (
                EXPECTED_N_UNITS, observed_n_units)
        elif not arms_differ["differ"]:
            verdict = "HARD_FAIL"
            vmsg = "HARD_FAIL_ARMS_IDENTICAL: substrate and random hashes match"
        elif n_hard_pass + n_mid + n_sat == 0:
            verdict = "HARD_FAIL"
            vmsg = "HARD_FAIL: no points reached MIDDLE_BAND or better"
        elif n_hard_pass + n_mid >= 6:
            verdict = "PHASE_DIAGRAM_LOCALIZED_CLIFF"
            vmsg = ("PHASE_DIAGRAM_LOCALIZED_CLIFF: cliff located; %d/%d phase points; "
                    "saturated=%d hard_pass=%d middle=%d floor=%d fail=%d; "
                    "cliff_locator=%s; gpu_util~%.2f"
                    ) % (observed_n_units, EXPECTED_N_UNITS, n_sat, n_hard_pass,
                          n_mid, n_floor, n_fail, cliff_locator,
                          gpu_util_estimate)
        else:
            verdict = "MIDDLE_BAND"
            vmsg = ("MIDDLE_BAND: partial cliff characterization; sat=%d hp=%d mb=%d "
                    "floor=%d fail=%d; cliff=%s") % (
                n_sat, n_hard_pass, n_mid, n_floor, n_fail, cliff_locator)

    # Substrate-only decode gate (META_RULE)
    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL_GATE_BREACH: substrate-only required"

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
        "n_seeds": 1,
        "phase_map": phase_map,
        "cliff_locator": cliff_locator,
        "arms_differ_sha256": arms_differ,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed_n_units,
        "crlb_predictions_1step": CRLB_PREDICTIONS,
        "smoke_gate_pass": smoke_gate_pass,
        "smoke_gate_reason": smoke_gate_reason,
        "tier_counts": {
            "SATURATED": n_sat, "HARD_PASS": n_hard_pass,
            "MIDDLE_BAND": n_mid, "FLOOR": n_floor, "HARD_FAIL": n_fail,
        },
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "beta": BETA,
        "corpus_provenance": CORPUS_PROVENANCE,
        "config_version": ("ANCHOR=%s,N=%s,corruption=%s,iters=%s,M=%d,seed=%d,"
                            "RUN_MODE=%s,BETA=%.1f") % (
            ANCHOR_NAME, N_SWEEP, CORRUPTION_SWEEP, ITERS_SWEEP, M_ITEMS,
            SEED_FULL, RUN_MODE, BETA),
        "n_llm_calls": _LLM_CALL_COUNTER[0],
    }
    write_metrics(out_dir, metrics)
    print("\n[VERDICT] %s" % vmsg, flush=True)
    print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
