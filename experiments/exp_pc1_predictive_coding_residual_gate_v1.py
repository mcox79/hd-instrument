"""
pc1_predictive_coding_residual_gate_v1 -- substrate-native predictive coding gate.

MOTIVATION (Research brain-mechanism x HD broad-exploration drill 2026-06-22):
  Friston / Rao-Ballard 1999 -- the brain runs a hierarchical generative model;
  each layer predicts the layer below; only prediction errors propagate up. The
  free-energy principle says: minimize variational free energy = surprise.

  Substrate-fit: the existing W matrix is *already* an implicit generative
  model. predict(key) = sign(W @ key) is the substrate's current best guess at
  the value bound to key. residual = observed - predicted is the bipolar
  mismatch (in {-2, 0, +2} per coordinate). Residual-gating the Hebbian write
  means: don't write what's already predicted; concentrate plasticity on
  surprising patterns. This is mechanism #1 in the broad-exploration drill,
  P_deflated = 0.38.

  Today's substrate writes every Hebbian-bind at full strength. Predictive
  coding should:
    (a) reduce W matrix saturation (skip writes for predicted patterns)
    (b) compose with refuse-gate (high residual = anomaly score)
    (c) preserve recall at lower W_norm.

HYPOTHESIS (PRE-REG, must answer in verdict):
  At M=2000 (alpha=2000/4096 ~ 0.49 -- moderate-to-heavy saturation regime
  for Hopfield-style associative memory; well above alpha_c=0.138), some
  variant of residual-gating maintains recall_at_1 while substantially
  reducing W_norm growth, demonstrating substrate-natural free-energy
  minimization.

ARMS (4):
  VANILLA_HEBBIAN          -- baseline: every write at full strength
  PC_RESIDUAL_GATE_THRESH_0p3 -- write only when residual_mag >= 0.3
  PC_RESIDUAL_PROPORTIONAL -- write strength = residual_mag (clipped [0, 1])
  RANDOM_GATE_CONTROL      -- write randomly with p=0.5 (CAN-FAIL discriminator)

The RANDOM_GATE_CONTROL is the load-bearing discriminator: if it matches the
PC arms, the gate is not load-bearing -- recall preservation is just an
artifact of skipping any 50% of writes. Symmetric verify both ways.

PRE-REGISTERED HARD BANDS:
  HARD_PASS: some PC arm achieves
    - recall_at_1 >= VANILLA recall_at_1 - 0.05 absolute (preserve recall)
    - AND final W_norm <= 0.5 * VANILLA W_norm (>=50% growth reduction)
    - AND >= 30% writes skipped (genuine saturation reduction)
    - AND RANDOM_GATE_CONTROL recall < that PC arm's recall by >= 0.05
      (gate is load-bearing, not random-skip artifact)
    - CV across seeds < 0.07 mandatory for the passing arm

  HARD_FAIL:
    - all PC arms recall drop > 0.10 vs VANILLA
    - OR no PC arm reduces W_norm
    - OR RANDOM_GATE_CONTROL recall matches PC arms within 0.03 (gate not
      load-bearing)
    - OR n_llm_calls > 0 (substrate-only-decode gate violation)

  MIDDLE_BAND: PC arm preserves recall (>= VANILLA - 0.05) but W_norm
    reduction < 30%, OR W_norm reduction >= 50% but recall drop in (0.05, 0.10]

INSTRUMENTATION:
  per_arm:
    arm_name, recall_at_1, W_norm, n_writes_total, n_writes_skipped,
    mean_residual_at_convergence, write_skip_frac, recall_minus_vanilla,
    wnorm_ratio_to_vanilla
  per_seed: full per_arm payload + the 4 arm-comparisons

SUBSTRATE-ONLY DECODE GATE:
  This script imports NO transformers / huggingface / openai. n_llm_calls
  is logged as 0 by structural-guarantee. Decode is sign(W @ key) cosine
  cleanup against value matrix. Verified in metrics.

PROT-018: production N = 4096 (anchor name has no _n suffix; this is a
  capability-test cell, not a sweep -- N is fixed at 4096 to land in the
  moderate-saturation regime).

PROT-019: timeout floor not triggered (no _n4096 suffix; CPU budget ~30-60min).

ASCII-only; no unicode; no emojis.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# ---------------------------------------------------------------------------
# Predictive-coding primitive (inlined to keep the cell self-contained on the
# remote runner without requiring a separate hdlab/predictive_coding.py SCP).
# The canonical copy lives at hdlab/predictive_coding.py; this is a verbatim
# duplicate of the public surface predict / residual_magnitude / threshold_gate
# / proportional_gate / gated_write / vanilla_hebbian_write.
# ---------------------------------------------------------------------------
from dataclasses import dataclass


def predict(W: np.ndarray, key: np.ndarray, *, sign_cleanup: bool = True) -> np.ndarray:
    """Substrate's current bipolar prediction for value bound to key."""
    if key.ndim == 1:
        raw = W @ key
    elif key.ndim == 2:
        raw = key @ W.T
    else:
        raise ValueError(f"key must be 1D or 2D, got ndim={key.ndim}")
    if not sign_cleanup:
        return raw
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def residual_magnitude(observed: np.ndarray, predicted: np.ndarray) -> float:
    """Normalized mismatch fraction in [0, 1] (0=perfect, 1=opposite)."""
    obs = observed.ravel()
    pred = predicted.ravel()
    n = obs.shape[0]
    if n == 0:
        return 0.0
    obs_n = float(np.linalg.norm(obs))
    pred_n = float(np.linalg.norm(pred))
    if obs_n <= 1e-12 or pred_n <= 1e-12:
        return 1.0
    cos = float(np.dot(obs, pred)) / (obs_n * pred_n)
    cos = max(-1.0, min(1.0, cos))
    return 0.5 * (1.0 - cos)


@dataclass(frozen=True)
class WriteDecision:
    write_strength: float
    residual_mag: float
    skipped: bool
    reason: str


def threshold_gate(observed: np.ndarray, predicted: np.ndarray, *,
                   threshold: float) -> WriteDecision:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0, 1]; got {threshold}")
    mag = residual_magnitude(observed, predicted)
    if mag >= threshold:
        return WriteDecision(1.0, mag, False, f"mag>={threshold}")
    return WriteDecision(0.0, mag, True, f"mag<{threshold}")


def proportional_gate(observed: np.ndarray, predicted: np.ndarray, *,
                      min_strength: float = 0.0,
                      max_strength: float = 1.0) -> WriteDecision:
    if min_strength < 0.0 or max_strength <= 0.0 or min_strength > max_strength:
        raise ValueError(f"invalid bounds: min={min_strength}, max={max_strength}")
    mag = residual_magnitude(observed, predicted)
    strength = max(min_strength, min(max_strength, mag))
    return WriteDecision(float(strength), mag, strength <= 0.0,
                         f"mag={mag:.3f}->{strength:.3f}")


def gated_write(W: np.ndarray, key: np.ndarray, value: np.ndarray,
                decision: WriteDecision) -> Tuple[np.ndarray, bool]:
    if decision.skipped or decision.write_strength <= 0.0:
        return W, False
    W += decision.write_strength * np.outer(value, key)
    return W, True


def vanilla_hebbian_write(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> np.ndarray:
    W += np.outer(value, key)
    return W

ANCHOR_NAME = "pc1_predictive_coding_residual_gate_v1"

# ---------------------------------------------------------------------------
# Substrate-only decode audit (Skunkworks structural blocker)
# ---------------------------------------------------------------------------
# This module imports no LLM / transformer / huggingface modules. The counter
# stays at 0 by structural guarantee; logged in metrics so the claim is
# auditable rather than asserted-by-comment.
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Production constants (PROT-018 -- no _n suffix; cell-author choice N=4096)
# ---------------------------------------------------------------------------
N_FULL = 4096
M_FULL = 2000               # alpha = 0.488; well above alpha_c=0.138
SEEDS_FULL = [7, 17, 23]    # 3 seeds (per pre-reg)
N_QUERIES_FULL = 500        # held-out recall queries
THRESHOLD_PC = 0.3

if RUN_MODE == "smoke":
    N = 256
    M = 80                  # alpha = 0.31 (still in saturating regime, fast)
    SEEDS = [7]
    N_QUERIES = 50
else:
    N = N_FULL
    M = M_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

ALPHA = M / N

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M={M},alpha={ALPHA:.3f},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"THRESHOLD_PC={THRESHOLD_PC},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation (bipolar +-1 keys and values)
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (keys, values) each shape (M, N), bipolar +-1, independent."""
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


# ---------------------------------------------------------------------------
# Recall: for each key, predict via sign(W @ key) and cosine-match to value
# ---------------------------------------------------------------------------
def recall_at_1(W: np.ndarray, keys: np.ndarray, values: np.ndarray,
                n_queries: int, rng: np.random.RandomState) -> float:
    """Fraction of queries whose predicted bipolar value matches the bound value.

    Uses cosine-similarity match against ALL stored values; recall_at_1 means
    the bound value is the top-1 nearest by cosine.
    """
    M_count = keys.shape[0]
    N_dim = keys.shape[1]
    idx = rng.choice(M_count, size=min(n_queries, M_count), replace=False)
    n_hits = 0
    for i in idx:
        pred = predict(W, keys[i])                       # (N,) bipolar
        sims = values @ pred / float(N_dim)              # (M,) cosine
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(idx))


# ---------------------------------------------------------------------------
# Arm implementations
# ---------------------------------------------------------------------------
def run_arm_vanilla(keys: np.ndarray, values: np.ndarray, N_dim: int) -> Dict:
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    M_count = keys.shape[0]
    last_residual = 0.0
    for i in range(M_count):
        # For instrumentation parity, record residual BEFORE write.
        pred = predict(W, keys[i])
        last_residual = residual_magnitude(values[i], pred)
        vanilla_hebbian_write(W, keys[i], values[i])
    return {
        "W": W,
        "n_writes_total": M_count,
        "n_writes_skipped": 0,
        "last_residual": float(last_residual),
    }


def run_arm_threshold(keys: np.ndarray, values: np.ndarray, N_dim: int,
                      threshold: float) -> Dict:
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    M_count = keys.shape[0]
    n_skipped = 0
    last_residual = 0.0
    for i in range(M_count):
        pred = predict(W, keys[i])
        dec = threshold_gate(values[i], pred, threshold=threshold)
        last_residual = dec.residual_mag
        _, applied = gated_write(W, keys[i], values[i], dec)
        if not applied:
            n_skipped += 1
    return {
        "W": W,
        "n_writes_total": M_count,
        "n_writes_skipped": n_skipped,
        "last_residual": float(last_residual),
    }


def run_arm_proportional(keys: np.ndarray, values: np.ndarray, N_dim: int) -> Dict:
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    M_count = keys.shape[0]
    n_skipped = 0
    last_residual = 0.0
    for i in range(M_count):
        pred = predict(W, keys[i])
        dec = proportional_gate(values[i], pred)
        last_residual = dec.residual_mag
        _, applied = gated_write(W, keys[i], values[i], dec)
        if not applied:
            n_skipped += 1
    return {
        "W": W,
        "n_writes_total": M_count,
        "n_writes_skipped": n_skipped,
        "last_residual": float(last_residual),
    }


def run_arm_random_control(keys: np.ndarray, values: np.ndarray, N_dim: int,
                           seed: int, p_write: float = 0.5) -> Dict:
    """CAN-FAIL discriminator: write with p_write (default 50%), ignore residual."""
    rng = np.random.RandomState(seed + 991)
    W = np.zeros((N_dim, N_dim), dtype=np.float64)
    M_count = keys.shape[0]
    n_skipped = 0
    last_residual = 0.0
    for i in range(M_count):
        pred = predict(W, keys[i])
        last_residual = residual_magnitude(values[i], pred)
        if rng.random() < p_write:
            vanilla_hebbian_write(W, keys[i], values[i])
        else:
            n_skipped += 1
    return {
        "W": W,
        "n_writes_total": M_count,
        "n_writes_skipped": n_skipped,
        "last_residual": float(last_residual),
    }


# ---------------------------------------------------------------------------
# Self-tests (run at import; gate the script)
# ---------------------------------------------------------------------------
def _selftest_predict_shape():
    rng = np.random.RandomState(0)
    N_t = 32
    W_t = rng.randn(N_t, N_t)
    k_t = rng.choice([-1.0, 1.0], size=N_t)
    p = predict(W_t, k_t)
    assert p.shape == (N_t,), f"predict shape: {p.shape}"
    assert set(np.unique(p)).issubset({-1.0, 1.0}), "predict not bipolar"
    return True


def _selftest_residual_mag_bounds():
    a = np.array([1.0, 1.0, 1.0, 1.0])
    assert abs(residual_magnitude(a, a) - 0.0) < 1e-9
    assert abs(residual_magnitude(a, -a) - 1.0) < 1e-9
    return True


def _selftest_vanilla_recall_at_alpha():
    """At alpha=0.05 (well below alpha_c=0.138), vanilla recall_at_1 ~ 1.0."""
    rng = np.random.RandomState(1)
    N_t, M_t = 256, 12
    keys = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W = np.zeros((N_t, N_t))
    for k, v in zip(keys, values):
        vanilla_hebbian_write(W, k, v)
    rng2 = np.random.RandomState(2)
    r = recall_at_1(W, keys, values, M_t, rng2)
    assert r >= 0.80, f"vanilla recall at alpha=0.047: {r:.3f} (expected >=0.8)"
    return r


def _selftest_random_control_skips():
    """RANDOM_GATE_CONTROL skips approximately 50%."""
    rng_seed = 0
    N_t, M_t = 64, 100
    rng = np.random.RandomState(rng_seed)
    keys = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    r = run_arm_random_control(keys, values, N_t, seed=0, p_write=0.5)
    skip_frac = r["n_writes_skipped"] / M_t
    assert 0.35 < skip_frac < 0.65, f"random control skip_frac={skip_frac:.3f} out of [0.35, 0.65]"
    return skip_frac


def _instrumentation_selftest():
    _selftest_predict_shape()
    _selftest_residual_mag_bounds()
    rec = _selftest_vanilla_recall_at_alpha()
    skip_frac = _selftest_random_control_skips()
    print(
        f"[selftest] PASS  vanilla_recall_low_alpha={rec:.3f}  "
        f"random_control_skip_frac={skip_frac:.3f}  N={N}  M={M}  alpha={ALPHA:.3f}  "
        f"mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    keys, values = generate_pairs(M, N, seed)
    rng_eval = np.random.RandomState(seed + 401)

    # ARM 1: VANILLA
    t1 = time.time()
    van = run_arm_vanilla(keys, values, N)
    van_wall = time.time() - t1
    van_recall = recall_at_1(van["W"], keys, values, N_QUERIES, rng_eval)
    van_norm = float(np.linalg.norm(van["W"]))

    # ARM 2: PC threshold gate
    t2 = time.time()
    rng_eval2 = np.random.RandomState(seed + 402)
    thr = run_arm_threshold(keys, values, N, THRESHOLD_PC)
    thr_wall = time.time() - t2
    thr_recall = recall_at_1(thr["W"], keys, values, N_QUERIES, rng_eval2)
    thr_norm = float(np.linalg.norm(thr["W"]))

    # ARM 3: PC proportional
    t3 = time.time()
    rng_eval3 = np.random.RandomState(seed + 403)
    prp = run_arm_proportional(keys, values, N)
    prp_wall = time.time() - t3
    prp_recall = recall_at_1(prp["W"], keys, values, N_QUERIES, rng_eval3)
    prp_norm = float(np.linalg.norm(prp["W"]))

    # ARM 4: RANDOM control
    t4 = time.time()
    rng_eval4 = np.random.RandomState(seed + 404)
    rnd = run_arm_random_control(keys, values, N, seed=seed, p_write=0.5)
    rnd_wall = time.time() - t4
    rnd_recall = recall_at_1(rnd["W"], keys, values, N_QUERIES, rng_eval4)
    rnd_norm = float(np.linalg.norm(rnd["W"]))

    elapsed = time.time() - t0

    def pack(name: str, arm: Dict, recall: float, wnorm: float, wall: float) -> Dict:
        skipped = arm["n_writes_skipped"]
        total = arm["n_writes_total"]
        return {
            "arm_name": name,
            "recall_at_1": float(recall),
            "W_norm": float(wnorm),
            "n_writes_total": int(total),
            "n_writes_skipped": int(skipped),
            "write_skip_frac": float(skipped) / float(max(total, 1)),
            "mean_residual_at_convergence": float(arm["last_residual"]),
            "wall_s": float(wall),
            "recall_minus_vanilla": float(recall - van_recall),
            "wnorm_ratio_to_vanilla": float(wnorm / max(van_norm, 1e-12)),
        }

    arms = [
        pack("VANILLA_HEBBIAN", van, van_recall, van_norm, van_wall),
        pack("PC_RESIDUAL_GATE_THRESH_0p3", thr, thr_recall, thr_norm, thr_wall),
        pack("PC_RESIDUAL_PROPORTIONAL", prp, prp_recall, prp_norm, prp_wall),
        pack("RANDOM_GATE_CONTROL", rnd, rnd_recall, rnd_norm, rnd_wall),
    ]

    print(
        f"  [seed={seed} N={N} M={M} alpha={ALPHA:.3f}] "
        f"VAN: rec={van_recall:.3f} norm={van_norm:.1f}  "
        f"PC_THR: rec={thr_recall:.3f} norm={thr_norm:.1f} skip={arms[1]['write_skip_frac']:.2f}  "
        f"PC_PRP: rec={prp_recall:.3f} norm={prp_norm:.1f} skip={arms[2]['write_skip_frac']:.2f}  "
        f"RND: rec={rnd_recall:.3f} norm={rnd_norm:.1f} skip={arms[3]['write_skip_frac']:.2f}  "
        f"elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha": float(ALPHA),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES),
        "threshold_pc": float(THRESHOLD_PC),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict logic (PRE-REG bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # Aggregate per-arm across seeds.
    arm_names = ["VANILLA_HEBBIAN", "PC_RESIDUAL_GATE_THRESH_0p3",
                 "PC_RESIDUAL_PROPORTIONAL", "RANDOM_GATE_CONTROL"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        recalls = [a["recall_at_1"] for a in per]
        norms = [a["W_norm"] for a in per]
        skips = [a["write_skip_frac"] for a in per]
        agg[name] = {
            "mean_recall": float(np.mean(recalls)),
            "std_recall": float(np.std(recalls)),
            "cv_recall": float(np.std(recalls) / max(abs(np.mean(recalls)), 1e-9)),
            "mean_norm": float(np.mean(norms)),
            "mean_skip_frac": float(np.mean(skips)),
        }

    van = agg["VANILLA_HEBBIAN"]
    rnd = agg["RANDOM_GATE_CONTROL"]
    pc_arms = ["PC_RESIDUAL_GATE_THRESH_0p3", "PC_RESIDUAL_PROPORTIONAL"]

    # Substrate-only-decode gate (any seed with n_llm_calls > 0 fails).
    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                f"HARD_FAIL: substrate-only-decode gate violated (n_llm_calls > 0).")

    summary_parts = [
        f"VAN(rec={van['mean_recall']:.3f},norm={van['mean_norm']:.1f})",
    ]
    for name in pc_arms:
        a = agg[name]
        summary_parts.append(
            f"{name}(rec={a['mean_recall']:.3f},norm={a['mean_norm']:.1f},"
            f"skip={a['mean_skip_frac']:.2f},cv={a['cv_recall']:.3f})"
        )
    summary_parts.append(
        f"RND(rec={rnd['mean_recall']:.3f},norm={rnd['mean_norm']:.1f},"
        f"skip={rnd['mean_skip_frac']:.2f})"
    )
    summary = "; ".join(summary_parts)

    # HARD_PASS: some PC arm meets all four conditions:
    #   (1) recall >= van.recall - 0.05
    #   (2) norm <= 0.5 * van.norm
    #   (3) skip_frac >= 0.30
    #   (4) recall - rnd.recall >= 0.05 (gate is load-bearing)
    #   (5) cv_recall < 0.07
    hp_candidates = []
    for name in pc_arms:
        a = agg[name]
        c1 = a["mean_recall"] >= van["mean_recall"] - 0.05
        c2 = a["mean_norm"] <= 0.5 * van["mean_norm"]
        c3 = a["mean_skip_frac"] >= 0.30
        c4 = a["mean_recall"] - rnd["mean_recall"] >= 0.05
        c5 = a["cv_recall"] < 0.07
        all_pass = all([c1, c2, c3, c4, c5])
        hp_candidates.append((name, all_pass, [c1, c2, c3, c4, c5]))

    any_hp = any(p for _, p, _ in hp_candidates)
    if any_hp:
        passed = [n for n, p, _ in hp_candidates if p]
        return ("HARD_PASS",
                f"HARD_PASS: PC arm(s) {passed} preserve recall + reduce W_norm + "
                f"discriminate vs RANDOM_GATE_CONTROL. {summary}")

    # HARD_FAIL conditions:
    all_pc_recall_drop = all(
        van["mean_recall"] - agg[n]["mean_recall"] > 0.10 for n in pc_arms
    )
    if all_pc_recall_drop:
        return ("HARD_FAIL",
                f"HARD_FAIL: all PC arms drop recall > 0.10 vs VANILLA. {summary}")

    no_norm_reduction = all(agg[n]["mean_norm"] >= van["mean_norm"] for n in pc_arms)
    if no_norm_reduction:
        return ("HARD_FAIL",
                f"HARD_FAIL: no PC arm reduces W_norm vs VANILLA. {summary}")

    random_matches_pc = all(
        abs(agg[n]["mean_recall"] - rnd["mean_recall"]) < 0.03 for n in pc_arms
    )
    if random_matches_pc:
        return ("HARD_FAIL",
                f"HARD_FAIL: RANDOM_GATE_CONTROL recall matches PC arms within 0.03 "
                f"-- gate is not load-bearing. {summary}")

    # MIDDLE_BAND: some PC arm preserves recall but fails one of the other criteria.
    middle_candidates = []
    for name in pc_arms:
        a = agg[name]
        recall_ok = a["mean_recall"] >= van["mean_recall"] - 0.05
        norm_partial = van["mean_norm"] * 0.5 < a["mean_norm"] <= van["mean_norm"]
        norm_strong = a["mean_norm"] <= van["mean_norm"] * 0.5
        recall_partial_drop = (
            van["mean_recall"] - a["mean_recall"] > 0.05
            and van["mean_recall"] - a["mean_recall"] <= 0.10
        )
        if (recall_ok and norm_partial) or (norm_strong and recall_partial_drop):
            middle_candidates.append(name)
    if middle_candidates:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: PC arm(s) {middle_candidates} partially meet criteria. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: no PC arm meets any HP/MIDDLE band. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pc1 N={N} M={M} alpha={ALPHA:.3f} mode={RUN_MODE}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

# PRE-FLIGHT run_mode guard (Fix #5): if any seed says smoke but anchor expects full, fail loud.
mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials detected in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N} M={M} alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"threshold={THRESHOLD_PC}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "M": M,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "threshold_pc": float(THRESHOLD_PC),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
