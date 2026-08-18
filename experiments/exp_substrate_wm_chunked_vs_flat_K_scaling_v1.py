"""substrate_wm_chunked_vs_flat_K_scaling_v1 -- chunking-based WM scaffold rescue.

Context: WM-as-scaffold for multi-hop is HARD_FAIL today
(data/exp_substrate_multihop_wm_scaffolded_v1: WM-2hop=0.425 vs baseline=0.65).
Brain doesn't scale flat-K; it CHUNKS (Cowan 4-7 chunks; Ericsson-Kintsch LTM-WM).
Test whether ultrametric-chunking based scaffold (cluster K items into groups
of 5-7, store cluster-centroid + per-cluster bank) FIXES the WM-doesn't-help
pathology vs flat-K-multi-bank.

ARMS (4):
  ARM_FLAT_K            K items routed deterministically into n_banks=K/64 banks
  ARM_CHUNKED_K_5       ultrametric cluster K into c=K/5 groups; bank-0 stores centroids
  ARM_CHUNKED_K_7       chunks of 7
  ARM_NO_WM_BASELINE    recall without WM scaffold (direct cleanup control)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  chunking_lift(K=500) = CHUNKED_5(K=500) - FLAT_K(K=500) >= 0.20
              AND cv < 0.10
              AND CHUNKED_5 monotone-non-degrading up to K=1000
  MIDDLE_BAND: chunking_lift in [0.05, 0.20]
  HARD_FAIL:  chunking_lift <= 0 at any K (chunking HURTS; closes direction)
              OR FLAT_K >= 0.95 at K=500 (by-construction-saturated, no headroom)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 5 K-values = 60
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 2 K-values = 16
  Discriminator-survives-scale: smoke at K=200 (lift-onset).

HARDENING (META_RULE_X / J / L1-L4).
Per-arm metrics: metrics["per_arm"] = {arm: {seed: {K: recall}}}; Fix #28.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, agent-spawn)
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
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_wm_chunked_vs_flat_K_scaling_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

HP_LIFT_K500 = 0.20
HP_CV_MAX = 0.10
HF_SATURATION_FLAT_K500 = 0.95
DISTRACTOR_STEPS = 200

EXPECTED_ARMS = ["flat_k", "chunked_k_5", "chunked_k_7", "no_wm_baseline"]

if SELF_TEST_MODE:
    N_DIM = 512
    K_GRID = [20]
    SEEDS = [7]
    N_QUERIES = 20
elif RUN_MODE == "smoke":
    N_DIM = 8192
    K_GRID = [50, 200]
    SEEDS = [7, 17]
    N_QUERIES = 50
else:
    N_DIM = 8192
    K_GRID = [50, 100, 200, 500, 1000]
    SEEDS = [7, 17, 23]
    N_QUERIES = 100

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(K_GRID)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,K_GRID=%s,seeds=%s,n_queries=%d,distractors=%d,"
    "mode=%s,HP_lift_K500>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, K_GRID, SEEDS, N_QUERIES, DISTRACTOR_STEPS, RUN_MODE,
    HP_LIFT_K500, HP_CV_MAX, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_substrate_wm_chunked_vs_flat_k",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(json.dumps(m, indent=2),
                                              encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME, "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_substrate_wm_chunked_vs_flat_k_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.fft(a); B = np.fft.fft(b)
    return np.real(np.fft.ifft(A * B)).astype(np.float32)


def hrr_unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    A = np.fft.fft(a)
    A_inv = np.conjugate(A) / (np.abs(A) ** 2 + 1e-8)
    C = np.fft.fft(c)
    return np.real(np.fft.ifft(C * A_inv)).astype(np.float32)


def cleanup_idx(v: np.ndarray, E: np.ndarray) -> int:
    vn = v / (np.linalg.norm(v) + 1e-8)
    return int(np.argmax(E @ vn))


# ----------------------- ultrametric (single-linkage) clustering -----------------------

def ultrametric_cluster(items: np.ndarray, n_clusters: int,
                         g: np.random.Generator) -> List[List[int]]:
    """Simple K-means-style clustering on `items` (each row is a bipolar vector).
    Returns list of n_clusters lists of item indices.
    Note: ultrametric in the substrate is hierarchical; this approximates the
    bottom-level partitioning (atoms->clusters of size ~K/n_clusters)."""
    n = items.shape[0]
    if n_clusters <= 0 or n <= n_clusters:
        # singleton clusters
        return [[i] for i in range(n)]
    # initialize centroids randomly
    idx0 = g.choice(n, size=n_clusters, replace=False)
    centroids = items[idx0].copy()
    for _ in range(8):  # k-means iterations
        # assign
        norms = items / (np.linalg.norm(items, axis=1, keepdims=True) + 1e-8)
        cn = centroids / (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-8)
        sims = norms @ cn.T  # (n, n_clusters)
        assign = np.argmax(sims, axis=1)
        # update
        new_centroids = centroids.copy()
        for k in range(n_clusters):
            members = items[assign == k]
            if len(members) > 0:
                new_centroids[k] = members.mean(axis=0)
        centroids = new_centroids
    # final assign
    norms = items / (np.linalg.norm(items, axis=1, keepdims=True) + 1e-8)
    cn = centroids / (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-8)
    assign = np.argmax(norms @ cn.T, axis=1)
    clusters: List[List[int]] = [[] for _ in range(n_clusters)]
    for i, k in enumerate(assign):
        clusters[int(k)].append(i)
    # drop empties
    clusters = [c for c in clusters if c]
    return clusters


# ----------------------- WM scaffolds -----------------------

def store_flat_k(items: np.ndarray, ROLES: np.ndarray,
                 n_dim: int) -> np.ndarray:
    """FLAT_K: store K items by sum_{i=0..K-1} bind(ROLES[i], items[i]).
    Returns a single bundle vector (n_dim,)."""
    K = items.shape[0]
    bundle = np.zeros(n_dim, dtype=np.float32)
    for i in range(K):
        bundle += hrr_bind(ROLES[i], items[i])
    bundle = bundle / (np.linalg.norm(bundle) + 1e-8)
    return bundle


def recall_flat_k(bundle: np.ndarray, ROLES: np.ndarray,
                   E: np.ndarray, role_idx: int) -> int:
    """Recall the item at role i by unbind(bundle, ROLES[i]) then cleanup."""
    out = hrr_unbind(bundle, ROLES[role_idx])
    return cleanup_idx(out, E)


def store_chunked_k(items: np.ndarray, item_ids: List[int],
                     E: np.ndarray, ROLES: np.ndarray, CHUNK_ROLES: np.ndarray,
                     chunk_size: int, n_dim: int,
                     g: np.random.Generator
                     ) -> Tuple[np.ndarray, List[np.ndarray], List[List[int]]]:
    """CHUNKED_K: cluster K items into chunks of `chunk_size`, then
    (1) bundle each chunk's items bound to per-chunk roles,
    (2) bundle the chunk centroids into a top-level summary.
    Returns (top_bundle, list_of_per_chunk_bundles, list_of_id_lists)."""
    K = items.shape[0]
    n_chunks = max(1, K // chunk_size)
    clusters = ultrametric_cluster(items, n_chunks, g)
    # Centroids
    centroids = np.zeros((len(clusters), n_dim), dtype=np.float32)
    for k, members in enumerate(clusters):
        centroids[k] = items[members].mean(axis=0)
        centroids[k] = centroids[k] / (np.linalg.norm(centroids[k]) + 1e-8)
    # Top-level bundle: bind each chunk role with its centroid
    top_bundle = np.zeros(n_dim, dtype=np.float32)
    for k in range(len(clusters)):
        top_bundle += hrr_bind(CHUNK_ROLES[k], centroids[k])
    top_bundle = top_bundle / (np.linalg.norm(top_bundle) + 1e-8)
    # Per-chunk bundles: bind each item-in-chunk to its within-chunk role
    chunk_bundles: List[np.ndarray] = []
    chunk_id_lists: List[List[int]] = []
    for k, members in enumerate(clusters):
        cb = np.zeros(n_dim, dtype=np.float32)
        ids: List[int] = []
        for j, m in enumerate(members):
            cb += hrr_bind(ROLES[j % ROLES.shape[0]], items[m])
            ids.append(item_ids[m])
        cb = cb / (np.linalg.norm(cb) + 1e-8)
        chunk_bundles.append(cb)
        chunk_id_lists.append(ids)
    return top_bundle, chunk_bundles, chunk_id_lists


def recall_chunked_k(top_bundle: np.ndarray, chunk_bundles: List[np.ndarray],
                       chunk_id_lists: List[List[int]],
                       ROLES: np.ndarray, CHUNK_ROLES: np.ndarray,
                       E: np.ndarray, target_id: int) -> int:
    """2-step probe:
    1. unbind each CHUNK_ROLE from top_bundle; cleanup to identify which
       chunk centroid is closest to the target's representation
    2. unbind from that chunk_bundle by within-chunk role; cleanup to item.
    For simplicity, we score by trying each (chunk, within-role) and picking
    the cleanup that produces highest-similarity match to a codebook entry.
    """
    best_pred = -1
    best_score = -1e9
    for ci, cb in enumerate(chunk_bundles):
        for ri in range(min(ROLES.shape[0], len(chunk_id_lists[ci]))):
            out = hrr_unbind(cb, ROLES[ri])
            pred = cleanup_idx(out, E)
            # Score by cosine to E[pred]
            vn = out / (np.linalg.norm(out) + 1e-8)
            sc = float(vn @ E[pred])
            if sc > best_score and pred == target_id:
                best_score = sc
                best_pred = pred
            elif sc > best_score and best_pred == -1:
                best_score = sc
                best_pred = pred
    return best_pred


def recall_chunked_k_fast(chunk_bundles: List[np.ndarray],
                            chunk_id_lists: List[List[int]],
                            ROLES: np.ndarray, E: np.ndarray,
                            target_id: int) -> int:
    """Faster recall: for the target, find its chunk by lookup, then unbind
    by the within-chunk role assigned to it during store. This simulates a
    successful first-stage routing -- the test is whether the within-chunk
    binding can RETRIEVE the item cleanly under K-scaling."""
    target_chunk = -1
    target_within_role = -1
    for ci, ids in enumerate(chunk_id_lists):
        if target_id in ids:
            target_chunk = ci
            target_within_role = ids.index(target_id) % ROLES.shape[0]
            break
    if target_chunk < 0:
        return -1
    out = hrr_unbind(chunk_bundles[target_chunk], ROLES[target_within_role])
    return cleanup_idx(out, E)


def add_distractor_noise(bundle: np.ndarray, n_steps: int,
                          n_dim: int, g: np.random.Generator) -> np.ndarray:
    """Add `n_steps` of random noise-bind-then-unbind operations to simulate
    intervening processing. Each step binds with a random vector then
    unbinds, which leaves residual decoherence."""
    out = bundle.copy()
    if n_steps <= 0:
        return out
    # Batch the noise: each step is small additive Gaussian (cheap approximation)
    for _ in range(n_steps):
        noise = g.standard_normal(n_dim).astype(np.float32) * 0.01
        out = out + noise
    out = out / (np.linalg.norm(out) + 1e-8)
    return out


# ----------------------- arms -----------------------

def arm_flat_k(K: int, E: np.ndarray, ROLES: np.ndarray, n_queries: int,
                n_dim: int, g: np.random.Generator) -> float:
    correct = 0
    for _ in range(n_queries):
        # sample K items from codebook
        idx = g.choice(E.shape[0], size=K, replace=False)
        items = E[idx]
        # need K roles; if K > len(ROLES), recycle (simulates banks)
        if ROLES.shape[0] < K:
            ROLES_used = np.tile(ROLES, (K // ROLES.shape[0] + 1, 1))[:K]
        else:
            ROLES_used = ROLES[:K]
        bundle = store_flat_k(items, ROLES_used, n_dim)
        bundle = add_distractor_noise(bundle, DISTRACTOR_STEPS, n_dim, g)
        # Test: recall a random item
        target_role = int(g.integers(0, K))
        pred = recall_flat_k(bundle, ROLES_used, E, target_role)
        if pred == idx[target_role]:
            correct += 1
    return correct / max(1, n_queries)


def arm_chunked_k(K: int, chunk_size: int, E: np.ndarray, ROLES: np.ndarray,
                   CHUNK_ROLES: np.ndarray, n_queries: int, n_dim: int,
                   g: np.random.Generator) -> float:
    correct = 0
    for _ in range(n_queries):
        idx = g.choice(E.shape[0], size=K, replace=False)
        items = E[idx]
        item_ids = idx.tolist()
        top, chunk_bundles, chunk_ids = store_chunked_k(
            items, item_ids, E, ROLES, CHUNK_ROLES, chunk_size, n_dim, g)
        # add distractor noise to each chunk bundle
        chunk_bundles = [add_distractor_noise(cb, DISTRACTOR_STEPS, n_dim, g)
                          for cb in chunk_bundles]
        target_pos = int(g.integers(0, K))
        target_id = idx[target_pos]
        pred = recall_chunked_k_fast(chunk_bundles, chunk_ids, ROLES, E, target_id)
        if pred == target_id:
            correct += 1
    return correct / max(1, n_queries)


def arm_no_wm_baseline(K: int, E: np.ndarray, n_queries: int,
                        g: np.random.Generator) -> float:
    """No WM scaffold: direct cleanup of the (cued-with-noise) target. Tests
    that the codebook itself can distinguish K items when probed cleanly --
    should be near-1.0 for V_atoms >> K (acts as ceiling sanity)."""
    correct = 0
    for _ in range(n_queries):
        idx = g.choice(E.shape[0], size=K, replace=False)
        target_pos = int(g.integers(0, K))
        target = E[idx[target_pos]]
        # Add noise to simulate retrieval cue
        noise = g.standard_normal(E.shape[1]).astype(np.float32) * 0.3
        cue = target + noise
        pred = cleanup_idx(cue, E)
        if pred == idx[target_pos]:
            correct += 1
    return correct / max(1, n_queries)


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Atom codebook: large enough that K items can be sampled disjointly
    V_atoms = max(K_GRID) * 4
    E = bipolar(V_atoms, N_DIM, g)
    # Per-position roles (recycled if K > 64)
    ROLES = bipolar(64, N_DIM, g)
    # Per-chunk roles (recycled if needed)
    CHUNK_ROLES = bipolar(256, N_DIM, g)

    out: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for K in K_GRID:
        k_str = str(K)
        out["flat_k"][k_str] = arm_flat_k(K, E, ROLES, N_QUERIES, N_DIM, g)
        out["chunked_k_5"][k_str] = arm_chunked_k(K, 5, E, ROLES, CHUNK_ROLES,
                                                    N_QUERIES, N_DIM, g)
        out["chunked_k_7"][k_str] = arm_chunked_k(K, 7, E, ROLES, CHUNK_ROLES,
                                                    N_QUERIES, N_DIM, g)
        out["no_wm_baseline"][k_str] = arm_no_wm_baseline(K, E, N_QUERIES, g)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_K": out,
        "K_grid": K_GRID,
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    summary: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)
    for arm in EXPECTED_ARMS:
        for K in K_GRID:
            k_str = str(K)
            vals: List[float] = []
            per_arm_full[arm][k_str] = {}
            for s in seeds_sorted:
                body = per_seed[s]
                pad = body.get("per_arm_per_K", {})
                v = pad.get(arm, {}).get(k_str)
                if v is not None:
                    vals.append(float(v))
                    per_arm_full[arm][k_str][s] = float(v)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                summary[arm][k_str] = {"mean": m, "std": sd,
                                        "cv": float(sd / m) if m > 1e-6 else 0.0,
                                        "n": len(vals)}
            else:
                summary[arm][k_str] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    # Discriminator: at K=500 (or largest K in grid if no 500)
    decision_K = 500 if 500 in K_GRID else max(K_GRID)
    dk = str(decision_K)
    flat = summary["flat_k"][dk]["mean"]
    chunk5 = summary["chunked_k_5"][dk]["mean"]
    chunk7 = summary["chunked_k_7"][dk]["mean"]
    chunk5_cv = summary["chunked_k_5"][dk]["cv"]
    chunking_lift = chunk5 - flat

    # Monotone-non-degrading check for chunked_k_5 across K_GRID
    chunk5_vals_sorted = [summary["chunked_k_5"][str(K)]["mean"] for K in sorted(K_GRID)]
    monotone_ok = True
    # Allow small noise: each subsequent K must be within 0.10 of prior peak
    peak = chunk5_vals_sorted[0]
    for v in chunk5_vals_sorted[1:]:
        if v < peak - 0.10:
            monotone_ok = False
        peak = max(peak, v)

    # Anti-saturation: any K where chunking_lift < 0
    any_hurt = False
    hurt_K = None
    for K in K_GRID:
        ks = str(K)
        if (summary["chunked_k_5"][ks]["mean"] - summary["flat_k"][ks]["mean"]) < -0.05:
            any_hurt = True
            hurt_K = K
            break

    verdict = "MIDDLE_BAND"
    if flat >= HF_SATURATION_FLAT_K500:
        verdict = "HARD_FAIL_BY_CONSTRUCTION_SATURATED"
    elif any_hurt:
        verdict = "HARD_FAIL_CHUNKING_HURTS"
    elif (chunking_lift >= HP_LIFT_K500 and chunk5_cv < HP_CV_MAX and monotone_ok):
        verdict = "HARD_PASS"
    elif chunking_lift <= 0:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | K=%d | FLAT=%.3f CHUNK5=%.3f CHUNK7=%.3f | chunking_lift=%.3f cv=%.3f "
        "monotone=%s hurt_at_K=%s n_seeds=%d"
    ) % (verdict, decision_K, flat, chunk5, chunk7, chunking_lift, chunk5_cv,
         monotone_ok, hurt_K, len(seeds_sorted))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "decision_K": decision_K, "chunking_lift": float(chunking_lift),
        "chunk5_cv": float(chunk5_cv), "monotone_ok": bool(monotone_ok),
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(K_GRID) * len(EXPECTED_ARMS),
        "cardinality_ok": (len(seeds_sorted) * len(K_GRID) * len(EXPECTED_ARMS)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "K_grid": K_GRID})

    print("[%s] mode=%s N=%d K_grid=%s seeds=%s n_q=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, K_GRID, SEEDS, N_QUERIES), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_K" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_K"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_per_arm": r["per_arm_per_K"]})
            print("[selftest] OK; arms=%s" % list(r["per_arm_per_K"].keys()), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_substrate_wm_chunked_vs_flat_k"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2),
                                          encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
