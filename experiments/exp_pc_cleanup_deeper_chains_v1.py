"""pc_cleanup_deeper_chains_v1 -- Wave 1.5 stressed re-dispatch.

WAVE 1.5 MOTIVATION (Research handoff 2026-06-26):
  Wave 1 cell (`pc_cleanup_attractor_v1`) HARD_PASS'd at depths (5, 10) with
  vanilla & PC both at recall=1.000 -- the regime was too easy; PC's
  differential lift never had headroom to demonstrate.

DEEPER + NOISIER REGIME (per Wave-1.5 spec):
  - DEPTHS = (15, 20, 30): vanilla should START degrading at depth >= 15
    when per-hop noise accumulates. Verifies the regime is genuinely hard.
  - HOP_NOISE_P_FLIP: bumped 0.15 -> 0.30 (was just below the cleanup-margin
    at smoke and depth-5; doubled to push cleanup-on-cleanup error budget).
  - Additional cleanup-NOISE sigma: per-hop GAUSSIAN_SIGMA=0.5 added to the
    bipolar state BEFORE codebook cleanup. This is the Wave-1.5 "sigma=0.5
    cleanup noise per hop" requirement -- forces the cleanup step to actually
    work against analog noise, not just bit-flips. Combined with bit-flip
    noise this is a harder regime than HOP_NOISE alone.

DISCRIMINATOR (Wave-1.5 HARD_PASS requirement; load-bearing):
  HARD_PASS now REQUIRES (verbatim from Wave-1.5 spec):
    VAN_d20 < 0.85 (proving regime is hard) AND
    PC_d20 >= VAN_d20 + 0.10 (PC differentially helps)

ARMS (3 mandatory; same as Wave-1):
  ARM_VANILLA_CLEANUP_BASELINE
  ARM_PC_CLEANUP_AT_EACH_HOP
  ARM_PC_CLEANUP_FINAL_ONLY

PROT-018: N=2048 (no _n suffix; capability-test).
PROT-019: no _n>=4096 -> no timeout floor.

ASCII-only; no unicode; no emojis; no em-dashes.
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


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def residual_magnitude(observed: np.ndarray, predicted: np.ndarray) -> float:
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


ANCHOR_NAME = "pc_cleanup_deeper_chains_v1"
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
# Production constants (Wave-1.5 deeper-and-noisier regime)
# ---------------------------------------------------------------------------
N_FULL = 2048
# M_CHAINS = 160 puts us in the discriminator regime (smoke-probe 2026-06-26):
# at M=80 (Wave-1 + Wave-1.5-original), VAN saturates at 1.000 across all
# depths -> mechanism never tested. At M=160, VAN remains ~0.94-1.0 at d=15
# (regime still hard but feasible) while PC's softmax-bundle accumulates
# error and drops to ~0.44 at d=20 -- the discriminator FIRES (|gap| >> 0.10).
# This is the regime where Wave-1.5's PASS criterion "VAN_d20<0.85 AND
# PC_d20>=VAN+0.10" can be honestly tested (Wave-1.5 spec line: "If still
# indistinguishable, this is honest negative evidence").
M_CHAINS_FULL = 160
V_FULL = 7680               # need M_CHAINS * L_MAX = 160 * 32 = 5120 <= 7680
L_MAX_FULL = 32             # supports depth up to 31
DEPTHS_FULL = (15, 20, 30)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 80         # bounded by M_CHAINS
PC_BETA = 8.0
PC_RESIDUAL_BLEND = 0.30
PC_TOP_K = 4
HOP_NOISE_P_FLIP = 0.30     # bumped from 0.15
HOP_NOISE_SIGMA = 0.50      # Wave-1.5 added: Gaussian sigma per hop (analog)

if RUN_MODE == "smoke":
    # Smoke: depths (5, 10) test that the new noise regime PRESERVES
    # baseline functionality before stressing deeper.
    N = 256
    V = 320          # 4*8 = 32 needed; bump to 320 for slack
    M_CHAINS = 4
    L_MAX = 16
    SEEDS = [7]
    N_QUERIES = 4
    DEPTHS_TEST = (5, 10)
else:
    N = N_FULL
    V = V_FULL
    M_CHAINS = M_CHAINS_FULL
    L_MAX = L_MAX_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL
    DEPTHS_TEST = DEPTHS_FULL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},V={V},M_CHAINS={M_CHAINS},L_MAX={L_MAX},"
    f"DEPTHS={DEPTHS_TEST},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},PC_BETA={PC_BETA},PC_BLEND={PC_RESIDUAL_BLEND},"
    f"HOP_NOISE_P_FLIP={HOP_NOISE_P_FLIP},HOP_NOISE_SIGMA={HOP_NOISE_SIGMA},"
    f"RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Codebook + chain ingest
# ---------------------------------------------------------------------------
def build_codebook(V_count: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(V_count, N_dim)).astype(np.float64)


def build_chains(M_count: int, L_len: int, V_count: int, seed: int) -> np.ndarray:
    needed = M_count * L_len
    if V_count < needed:
        raise ValueError(
            f"build_chains: V_count={V_count} < M_count*L_len={needed}; "
            f"unique chain construction infeasible."
        )
    rng = np.random.RandomState(seed + 901)
    perm = rng.permutation(V_count)[:needed]
    return perm.reshape(M_count, L_len).astype(np.int64)


def ingest_chains(codebook: np.ndarray, chains: np.ndarray,
                   N_dim: int) -> np.ndarray:
    """Vectorized: W = sum over (i->j) edges of outer(value_j, value_i)
    = dst.T @ src where src = codebook[chains[:, :-1]] and dst = codebook[chains[:, 1:]].
    Equivalent to the explicit-outer-product loop, ~190x faster at M=80 N=2048.
    """
    src = codebook[chains[:, :-1].ravel()]   # (M*(L-1), N)
    dst = codebook[chains[:, 1:].ravel()]    # (M*(L-1), N)
    W = dst.T @ src                          # (N, N)
    return W


def codebook_cleanup(state: np.ndarray, codebook: np.ndarray,
                      N_dim: int) -> Tuple[int, float, np.ndarray]:
    sims = codebook @ state / float(N_dim)
    idx = int(np.argmax(sims))
    z = PC_BETA * sims
    z = z - np.max(z)
    e = np.exp(z)
    p = e / np.sum(e)
    return idx, float(p[idx]), codebook[idx].copy()


# ---------------------------------------------------------------------------
# Hop runners — with bit-flip + Gaussian noise (Wave-1.5)
# ---------------------------------------------------------------------------
def _apply_hop_noise(state: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
    """Apply bit-flip noise then Gaussian-sigma noise (Wave-1.5)."""
    if HOP_NOISE_P_FLIP > 0.0:
        flips = rng.random(state.shape) < HOP_NOISE_P_FLIP
        state = np.where(flips, -state, state)
    if HOP_NOISE_SIGMA > 0.0:
        # Add Gaussian noise; downstream sign(W @ state) is robust but
        # codebook cleanup sees the analog noise.
        state = state + rng.normal(0.0, HOP_NOISE_SIGMA, size=state.shape)
    return state


def hop_vanilla(W: np.ndarray, state: np.ndarray, codebook: np.ndarray,
                 N_dim: int,
                 rng: np.random.RandomState) -> Tuple[int, float, np.ndarray]:
    noisy = _apply_hop_noise(state, rng)
    raw = predict(W, noisy)
    idx, pmax, cleaned = codebook_cleanup(raw, codebook, N_dim)
    free_energy = -math.log(max(pmax, 1e-12))
    return idx, free_energy, cleaned


def hop_pc_refined(W: np.ndarray, state: np.ndarray, codebook: np.ndarray,
                    N_dim: int,
                    rng: np.random.RandomState) -> Tuple[int, float, np.ndarray]:
    """One hop with PC top-K softmax-bundle refinement."""
    noisy = _apply_hop_noise(state, rng)
    raw = predict(W, noisy)
    sims = codebook @ raw / float(N_dim)
    K = min(PC_TOP_K, codebook.shape[0])
    top_k_idx = np.argpartition(-sims, K - 1)[:K]
    top_k_sims = sims[top_k_idx]
    z = PC_BETA * top_k_sims
    z = z - np.max(z)
    w = np.exp(z)
    w = w / np.sum(w)
    bundle_raw = (w[:, None] * codebook[top_k_idx]).sum(axis=0)
    bundle = np.sign(bundle_raw)
    bundle[bundle == 0] = 1.0
    top1_idx = int(top_k_idx[int(np.argmax(top_k_sims))])
    z_full = PC_BETA * sims
    z_full = z_full - np.max(z_full)
    p_full = np.exp(z_full)
    p_full = p_full / np.sum(p_full)
    p_max = float(np.max(p_full))
    free_energy = -math.log(max(p_max, 1e-12))
    return top1_idx, free_energy, bundle


# ---------------------------------------------------------------------------
# Full-chain runners
# ---------------------------------------------------------------------------
def run_chain_vanilla(W: np.ndarray, start_idx: int, codebook: np.ndarray,
                      depth: int, N_dim: int,
                      rng: np.random.RandomState
                      ) -> Tuple[int, List[float], List[int]]:
    state = codebook[start_idx].copy()
    fe_trace = []
    idx_trace = []
    for h in range(depth):
        idx, fe, state = hop_vanilla(W, state, codebook, N_dim, rng)
        fe_trace.append(fe)
        idx_trace.append(idx)
    return idx_trace[-1], fe_trace, idx_trace


def run_chain_pc_each_hop(W: np.ndarray, start_idx: int, codebook: np.ndarray,
                          depth: int, N_dim: int,
                          rng: np.random.RandomState
                          ) -> Tuple[int, List[float], List[int]]:
    state = codebook[start_idx].copy()
    fe_trace = []
    idx_trace = []
    for h in range(depth):
        idx, fe, state = hop_pc_refined(W, state, codebook, N_dim, rng)
        fe_trace.append(fe)
        idx_trace.append(idx)
    return idx_trace[-1], fe_trace, idx_trace


def run_chain_pc_final_only(W: np.ndarray, start_idx: int, codebook: np.ndarray,
                            depth: int, N_dim: int,
                            rng: np.random.RandomState
                            ) -> Tuple[int, List[float], List[int]]:
    state = codebook[start_idx].copy()
    fe_trace = []
    idx_trace = []
    for h in range(depth):
        if h < depth - 1:
            idx, fe, state = hop_vanilla(W, state, codebook, N_dim, rng)
        else:
            idx, fe, state = hop_pc_refined(W, state, codebook, N_dim, rng)
        fe_trace.append(fe)
        idx_trace.append(idx)
    return idx_trace[-1], fe_trace, idx_trace


# ---------------------------------------------------------------------------
# Arm evaluation
# ---------------------------------------------------------------------------
def evaluate_arm(arm_name: str, W: np.ndarray, codebook: np.ndarray,
                 chains: np.ndarray, depth: int,
                 query_idx: np.ndarray, N_dim: int) -> Dict:
    n_hits = 0
    fe_per_hop_sum = np.zeros(depth, dtype=np.float64)
    n_queries = len(query_idx)
    for qi, q in enumerate(query_idx):
        start_idx = int(chains[q, 0])
        true_target = int(chains[q, depth])
        rng = np.random.RandomState(int(q) * 1000003 + depth * 7919)
        if arm_name == "ARM_VANILLA_CLEANUP_BASELINE":
            pred, fe_trace, _ = run_chain_vanilla(W, start_idx, codebook, depth, N_dim, rng)
        elif arm_name == "ARM_PC_CLEANUP_AT_EACH_HOP":
            pred, fe_trace, _ = run_chain_pc_each_hop(W, start_idx, codebook, depth, N_dim, rng)
        elif arm_name == "ARM_PC_CLEANUP_FINAL_ONLY":
            pred, fe_trace, _ = run_chain_pc_final_only(W, start_idx, codebook, depth, N_dim, rng)
        else:
            raise ValueError(f"unknown arm {arm_name}")
        if pred == true_target:
            n_hits += 1
        fe_per_hop_sum += np.array(fe_trace)
    recall = float(n_hits) / float(n_queries)
    fe_per_hop_mean = (fe_per_hop_sum / float(n_queries)).tolist()
    monotone_within = bool(all(fe_per_hop_mean[i] >= fe_per_hop_mean[i + 1] - 1e-6
                         for i in range(len(fe_per_hop_mean) - 1)))
    return {
        "arm_name": arm_name,
        "depth": int(depth),
        "recall": float(recall),
        "fe_per_hop": fe_per_hop_mean,
        "fe_monotone_non_increasing": monotone_within,
        "fe_mean": float(np.mean(fe_per_hop_mean)),
        "n_queries": int(n_queries),
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_predict_shape():
    rng = np.random.RandomState(0)
    N_t = 32
    W_t = rng.randn(N_t, N_t)
    k_t = rng.choice([-1.0, 1.0], size=N_t)
    p = predict(W_t, k_t)
    assert p.shape == (N_t,)
    assert set(np.unique(p)).issubset({-1.0, 1.0})
    return True


def _selftest_residual_bounds():
    a = np.array([1.0, 1.0, 1.0, 1.0])
    assert abs(residual_magnitude(a, a) - 0.0) < 1e-9
    assert abs(residual_magnitude(a, -a) - 1.0) < 1e-9
    return True


def _selftest_codebook_cleanup_perfect():
    cb = np.array([[1.0, 1.0], [-1.0, -1.0]])
    idx, pmax, cleaned = codebook_cleanup(np.array([1.0, 1.0]), cb, N_dim=2)
    assert idx == 0
    assert pmax > 0.5
    return True


def _selftest_noise_applies_both_bitflip_and_gaussian():
    """At sigma=0.5 the analog state should NOT match a pure bipolar -> mixed regime."""
    rng = np.random.RandomState(0)
    state = np.ones(64, dtype=np.float64)
    noisy = _apply_hop_noise(state, rng)
    # With Gaussian noise applied, the analog distribution is non-degenerate.
    assert noisy.std() > 0.1, f"gaussian noise should add analog spread; got std={noisy.std():.3f}"
    return True


def _selftest_chain_storage_recall():
    """Test storage codepath at depth 1 with the new noise regime."""
    N_t = 256
    V_t = 16
    cb = np.random.RandomState(1).choice([-1.0, 1.0], size=(V_t, N_t)).astype(np.float64)
    chains = np.array([[0, 1, 2, 3], [4, 5, 6, 7]], dtype=np.int64)
    W_t = ingest_chains(cb, chains, N_t)
    rng = np.random.RandomState(0)
    pred, _, _ = run_chain_vanilla(W_t, 0, cb, depth=1, N_dim=N_t, rng=rng)
    # At depth-1 with N=256, V=16, single-successor: cleanup margin >> noise.
    assert pred == 1, f"depth-1 vanilla recall failed: pred={pred} expected 1"
    return True


def _instrumentation_selftest():
    _selftest_predict_shape()
    _selftest_residual_bounds()
    _selftest_codebook_cleanup_perfect()
    _selftest_noise_applies_both_bitflip_and_gaussian()
    _selftest_chain_storage_recall()
    print(
        f"[selftest] PASS  N={N}  V={V}  M_CHAINS={M_CHAINS}  L_MAX={L_MAX}  "
        f"depths={DEPTHS_TEST}  p_flip={HOP_NOISE_P_FLIP}  sigma={HOP_NOISE_SIGMA}  "
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
    codebook = build_codebook(V, N, seed)
    chains = build_chains(M_CHAINS, L_MAX, V, seed)
    W = ingest_chains(codebook, chains, N)

    rng = np.random.RandomState(seed + 401)
    n_q = min(N_QUERIES, M_CHAINS)
    query_idx = rng.choice(M_CHAINS, size=n_q, replace=False)

    arms_by_depth: Dict[int, List[Dict]] = {}
    for depth in DEPTHS_TEST:
        arms_by_depth[depth] = []
        for arm_name in ["ARM_VANILLA_CLEANUP_BASELINE",
                          "ARM_PC_CLEANUP_AT_EACH_HOP",
                          "ARM_PC_CLEANUP_FINAL_ONLY"]:
            r = evaluate_arm(arm_name, W, codebook, chains, depth, query_idx, N)
            arms_by_depth[depth].append(r)
            print(
                f"  [seed={seed} depth={depth} {arm_name}] "
                f"recall={r['recall']:.3f}  monotone_fe={r['fe_monotone_non_increasing']}  "
                f"fe_end={r['fe_per_hop'][-1]:.3f}",
                flush=True,
            )

    flat_arms = []
    for depth, arr in arms_by_depth.items():
        for a in arr:
            tagged = dict(a)
            tagged["arm_name"] = f"{a['arm_name']}_d{depth}"
            flat_arms.append(tagged)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "V": V,
        "M_CHAINS": M_CHAINS,
        "L_MAX": L_MAX,
        "depths_tested": list(DEPTHS_TEST),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(n_q),
        "pc_blend": float(PC_RESIDUAL_BLEND),
        "pc_beta": float(PC_BETA),
        "hop_noise_p_flip": float(HOP_NOISE_P_FLIP),
        "hop_noise_sigma": float(HOP_NOISE_SIGMA),
        "arms": flat_arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (Wave-1.5 deeper-and-noisier bands; VAN_d20 < 0.85 + PC_d20 >= VAN+0.10)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    depths_seen = sorted({int(a["depth"]) for a in results[0]["arms"]})
    if len(depths_seen) < 2:
        return ("HARD_FAIL",
                f"HARD_FAIL: expected >= 2 depths; got {depths_seen}")

    # Aggregate per arm @ depth.
    arm_names = []
    for d in depths_seen:
        for base in ("ARM_VANILLA_CLEANUP_BASELINE",
                      "ARM_PC_CLEANUP_AT_EACH_HOP",
                      "ARM_PC_CLEANUP_FINAL_ONLY"):
            arm_names.append(f"{base}_d{d}")

    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec = [a["recall"] for a in per]
        fe_mean = [a.get("fe_mean", 0.0) for a in per]
        agg[name] = {
            "mean_recall": float(np.mean(rec)),
            "std_recall": float(np.std(rec)),
            "cv_recall": float(np.std(rec) / max(abs(np.mean(rec)), 1e-9)),
            "mean_fe": float(np.mean(fe_mean)),
        }

    # Pick canonical "hardness-prove" depth and "PC-lift" depth.
    # FULL (15, 20, 30): hardness at d=20; lift at d=20.
    # smoke (5, 10):  hardness at d=10; lift at d=10.
    d_lift = depths_seen[-2] if len(depths_seen) >= 3 else depths_seen[-1]
    # For full: 15/20/30 -> d_lift = 20.  For smoke: 5/10 -> d_lift = 10.
    d_hardness = d_lift  # same anchor depth for both criteria

    van_lift = agg[f"ARM_VANILLA_CLEANUP_BASELINE_d{d_lift}"]
    pc_lift = agg[f"ARM_PC_CLEANUP_AT_EACH_HOP_d{d_lift}"]
    pcf_lift = agg[f"ARM_PC_CLEANUP_FINAL_ONLY_d{d_lift}"]

    pc_minus_van = pc_lift["mean_recall"] - van_lift["mean_recall"]

    # Also report deepest depth for context.
    d_deep = depths_seen[-1]
    van_deep = agg[f"ARM_VANILLA_CLEANUP_BASELINE_d{d_deep}"]
    pc_deep = agg[f"ARM_PC_CLEANUP_AT_EACH_HOP_d{d_deep}"]

    summary_parts = []
    for d in depths_seen:
        v = agg[f"ARM_VANILLA_CLEANUP_BASELINE_d{d}"]["mean_recall"]
        p = agg[f"ARM_PC_CLEANUP_AT_EACH_HOP_d{d}"]["mean_recall"]
        f = agg[f"ARM_PC_CLEANUP_FINAL_ONLY_d{d}"]["mean_recall"]
        summary_parts.append(f"d{d}:VAN={v:.3f},PC={p:.3f},PC_FIN={f:.3f}")
    summary = " ".join(summary_parts) + f"  PC-VAN@d{d_lift}={pc_minus_van:+.3f}"

    # HARD_FAIL guards.
    if pc_lift["mean_recall"] <= 0.0 and van_lift["mean_recall"] <= 0.0:
        return ("HARD_FAIL",
                f"HARD_FAIL: both PC and VAN at recall=0 @d{d_lift} (regime "
                f"over-stressed; nothing recoverable). {summary}")

    # Bands depend on full vs smoke.
    if (5, 10) == tuple(depths_seen):
        # Smoke regime: just verify mechanism direction is detectable + verdict
        # plumbing exercised.
        if pc_minus_van >= 0.05:
            return ("HARD_PASS",
                    f"HARD_PASS: smoke discriminator shows PC-VAN@d{d_lift}"
                    f"={pc_minus_van:+.3f} >= 0.05. {summary}")
        elif abs(pc_minus_van) < 0.05:
            return ("MIDDLE_BAND",
                    f"MIDDLE_BAND: smoke PC-VAN@d{d_lift}={pc_minus_van:+.3f}"
                    f" within +/-0.05. {summary}")
        else:
            return ("HARD_FAIL",
                    f"HARD_FAIL: smoke shows PC HURTS, PC-VAN@d{d_lift}"
                    f"={pc_minus_van:+.3f}. {summary}")

    # FULL regime: Wave-1.5 bands.
    hardness_satisfied = van_lift["mean_recall"] < 0.85
    pc_lift_satisfied = pc_minus_van >= 0.10

    if hardness_satisfied and pc_lift_satisfied:
        return ("HARD_PASS",
                f"HARD_PASS: VAN@d{d_lift}={van_lift['mean_recall']:.3f} < 0.85 "
                f"(regime is hard) AND PC@d{d_lift}-VAN@d{d_lift}"
                f"={pc_minus_van:+.3f} >= 0.10 (PC differentially helps). "
                f"{summary}")

    if not hardness_satisfied:
        # Regime not hard enough: by-construction-saturation persists.
        if van_lift["mean_recall"] >= 0.95:
            return ("HARD_FAIL",
                    f"HARD_FAIL: VAN@d{d_lift}={van_lift['mean_recall']:.3f} "
                    f">= 0.95 (regime still saturated, mechanism untested). "
                    f"{summary}")
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: VAN@d{d_lift}={van_lift['mean_recall']:.3f} in "
                f"[0.85, 0.95) (regime not quite hard enough); "
                f"PC-VAN@d{d_lift}={pc_minus_van:+.3f}. {summary}")

    # Hardness satisfied but PC lift not at +0.10.
    if pc_minus_van >= 0.05:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: regime hard but PC-VAN={pc_minus_van:+.3f} in "
                f"[0.05, 0.10). {summary}")

    if pc_minus_van >= 0.0:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: regime hard; PC matches VAN within "
                f"+/-0.05 (mechanism neutral). {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: regime hard but PC HURTS, PC-VAN={pc_minus_van:+.3f}. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "V": V, "L_MAX": L_MAX, "DEPTHS": list(DEPTHS_TEST),
              "P_FLIP": HOP_NOISE_P_FLIP, "SIGMA": HOP_NOISE_SIGMA,
              "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pc_cleanup DEEPER N={N} V={V} M_chains={M_CHAINS} "
          f"depths={DEPTHS_TEST} p_flip={HOP_NOISE_P_FLIP} sigma={HOP_NOISE_SIGMA} "
          f"mode={RUN_MODE}...",
          flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N} V={V} M_CHAINS={M_CHAINS} "
        f"depths={DEPTHS_TEST} mode={RUN_MODE} "
        f"p_flip={HOP_NOISE_P_FLIP} sigma={HOP_NOISE_SIGMA}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "V": V,
    "M_CHAINS": M_CHAINS,
    "L_MAX": L_MAX,
    "depths_tested": list(DEPTHS_TEST),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "pc_blend": float(PC_RESIDUAL_BLEND),
    "pc_beta": float(PC_BETA),
    "hop_noise_p_flip": float(HOP_NOISE_P_FLIP),
    "hop_noise_sigma": float(HOP_NOISE_SIGMA),
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
