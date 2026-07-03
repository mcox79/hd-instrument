"""Stage 2 VSA Cell 1 K_DIST sweep addendum (SMOKE).

Parent prereg: preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_k_dist_sweep_smoke.md
Fork of:      experiments/exp_substrate_vsa_cell1_analogy_completion_smoke_2026-07-03.py
Anchor:       stage2_vsa_cell1_analogy_completion_k_dist_sweep_smoke

Purpose (Skunkworks-approved sweep addendum, not a new anchor):
  Cell 1 smoke (commit ad43cd195) landed MB verdict -- HP1+HP2 cleared but
  HP3 (CLEANUP - NO_CLEANUP >= 0.05) FAILED at K_DISTRACTORS=3 with gap
  = +0.007. Author note: "HP3 fail is MEASURED_BOUND, not defect. At
  K_DIST=3, bundle noise on r_hat is small enough that atomic-A argmax
  already denoises. Would presumably fire at larger K."

  This cell sweeps K_DIST in {3, 5, 10, 20, 50} to characterize where
  cleanup earns its keep. K=3 arm is a regression-sanity check
  (must reproduce Cell 1 CLEANUP=0.861 / NO_CLEANUP=0.855 bit-identical).

  If sweep fires HP3 at K >= 10: atom (a) MEASURED_BOUND -> chain-grade
  upgrade candidate; supports 3rd witness -> CG_META META promotion path.
  If sweep fails HP3 at any K: refines atom (a) as "cleanup does not
  earn its keep on this canonical FHRR regime; may need different
  codebook or task structure."

Sweep design:
  K_DIST_VALUES = [3, 5, 10, 20, 50]  -- 5 sweep points
  ARMS_PER_K = [CLEANUP, NO_CLEANUP]  -- weak baselines skipped (Cell 1 characterized at chance)
  SEEDS = [11, 17, 23]                 -- same as Cell 1
  EXPECTED_N_UNITS = 3 * 5 * 2 = 30

Same primitives, same codebook construction, same query-generation logic;
ONLY K_DISTRACTORS varies. n_dim=2048, N_C=100, N_R=10, N_Q=500 held constant.

Cell-template mandates: META_RULE_AF, META_RULE_AH, except SystemExit
raise BEFORE except Exception, start_marker, crash_diagnostic. ASCII-only.

Regression-sanity check (asserted in selftest):
  At K=3 with seeds=[11, 17, 23], sample_analogies + run_arm code path
  is bit-identical to Cell 1; recall@1 values must match within 1e-9.
  MEASURED@d:/AI/hd-instrument/data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json:gates.cleanup

PROT-018: no _n<N> suffix (this is a capability/characterization cell).
"""
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "stage2_vsa_cell1_analogy_completion_k_dist_sweep_smoke"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "smoke").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "smoke").lower()
)

# -----------------------------------------------------------------------------
# Config (held constant from Cell 1 except K_DISTRACTORS which becomes the sweep axis)
# -----------------------------------------------------------------------------
N_DIM = 2048
N_CONCEPTS = 100
N_RELATIONS = 10
N_QUERIES = 500
K_DIST_VALUES = [3, 5, 10, 20, 50]
SEEDS = [11, 17, 23]
# 3 seeds x 5 K values x 2 arms (CLEANUP, NO_CLEANUP) = 30
EXPECTED_N_UNITS = len(SEEDS) * len(K_DIST_VALUES) * 2

# Regression-sanity reference from Cell 1 (K=3)
# MEASURED@d:/AI/hd-instrument/data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json
CELL1_K3_CLEANUP_MEAN = 0.8613333333333334
CELL1_K3_NO_CLEANUP_MEAN = 0.8546666666666667
REGRESSION_TOL = 1e-9

# HP3 threshold for CLEANUP - NO_CLEANUP gap
HP3_THRESHOLD = 0.05

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},n_dim={N_DIM},N_C={N_CONCEPTS},N_R={N_RELATIONS},"
    f"N_Q={N_QUERIES},K_DIST_SWEEP={'-'.join(str(k) for k in K_DIST_VALUES)},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},arms_per_K=2,cleanup=k_NN,binding=FHRR_complex_phasors"
)

ARM_MODES = ("ARM_HRR_BIND_UNBIND_CLEANUP", "ARM_HRR_BIND_UNBIND_NO_CLEANUP")


# -----------------------------------------------------------------------------
# VSA primitives (FHRR / Frequency-HRR per Plate 2003).
# Identical to Cell 1.
# -----------------------------------------------------------------------------
def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind: elementwise complex multiply. a, b: (n_dim,) complex128."""
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR unbind: elementwise multiply by conjugate."""
    return c * b.conj()


def _fhrr_similarity(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    dots = (codebook @ query.conj()).real
    return dots / float(query.shape[0])


def cosine_argmax(query: np.ndarray, codebook: np.ndarray) -> int:
    sims = _fhrr_similarity(query, codebook)
    return int(np.argmax(sims))


def cleanup_argmax(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    idx = cosine_argmax(query, codebook)
    return codebook[idx].copy()


def _rand_phasors(rng: np.random.Generator, shape) -> np.ndarray:
    phases = rng.uniform(-np.pi, np.pi, size=shape).astype(np.float64)
    return np.exp(1j * phases)


def bundle(vecs: np.ndarray) -> np.ndarray:
    s = vecs.sum(axis=0)
    mag = np.abs(s)
    mag[mag < 1e-12] = 1.0
    return s / mag


# -----------------------------------------------------------------------------
# Codebook + analogy generation (K-parameterized)
# -----------------------------------------------------------------------------
def build_codebooks(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    A = _rand_phasors(rng, (N_CONCEPTS, N_DIM))
    R = _rand_phasors(rng, (N_RELATIONS, N_DIM))
    return A, R


def sample_analogies(seed: int, n_queries: int, k_dist: int) -> Dict[str, np.ndarray]:
    """Same generator logic as Cell 1 but K_DISTRACTORS parameterized.

    CRITICAL: RNG stream depends on k_dist (different number of int draws
    per query). At k_dist=3 with same seed, reproduces Cell 1 sample exactly.
    """
    rng = np.random.default_rng(seed + 991)
    target = np.empty((n_queries, 3), dtype=np.int64)
    dist_a = np.empty((n_queries, k_dist), dtype=np.int64)
    dist_r_a = np.empty((n_queries, k_dist), dtype=np.int64)
    dist_c = np.empty((n_queries, k_dist), dtype=np.int64)
    dist_r_c = np.empty((n_queries, k_dist), dtype=np.int64)
    for q in range(n_queries):
        a_idx = int(rng.integers(0, N_CONCEPTS))
        r_idx = int(rng.integers(0, N_RELATIONS))
        c_idx = int(rng.integers(0, N_CONCEPTS))
        while c_idx == a_idx:
            c_idx = int(rng.integers(0, N_CONCEPTS))
        target[q] = (a_idx, r_idx, c_idx)
        for k in range(k_dist):
            ka = int(rng.integers(0, N_CONCEPTS))
            while ka == a_idx:
                ka = int(rng.integers(0, N_CONCEPTS))
            dist_a[q, k] = ka
            dist_r_a[q, k] = int(rng.integers(0, N_RELATIONS))
            kc = int(rng.integers(0, N_CONCEPTS))
            while kc == c_idx:
                kc = int(rng.integers(0, N_CONCEPTS))
            dist_c[q, k] = kc
            dist_r_c[q, k] = int(rng.integers(0, N_RELATIONS))
    return {
        "target": target,
        "dist_a": dist_a, "dist_r_a": dist_r_a,
        "dist_c": dist_c, "dist_r_c": dist_r_c,
    }


def build_side_bundle(concept_idx: int, r_idx: int,
                      dist_concept_idx: np.ndarray, dist_r_idx: np.ndarray,
                      A: np.ndarray, R: np.ndarray, k_dist: int) -> np.ndarray:
    """Build FHRR superposition: bundle target-binding + k_dist distractor bindings."""
    vecs = np.empty((1 + k_dist, N_DIM), dtype=np.complex128)
    vecs[0] = A[concept_idx] * R[r_idx]
    for k in range(k_dist):
        vecs[1 + k] = A[dist_concept_idx[k]] * R[dist_r_idx[k]]
    return bundle(vecs)


# -----------------------------------------------------------------------------
# Per-arm inference (identical to Cell 1)
# -----------------------------------------------------------------------------
def infer_cleanup(a: np.ndarray, b_bundle: np.ndarray, d_bundle: np.ndarray,
                  A: np.ndarray, R: np.ndarray) -> int:
    r_hat = unbind(b_bundle, a)
    r_snap = cleanup_argmax(r_hat, R)
    c_hat = unbind(d_bundle, r_snap)
    return cosine_argmax(c_hat, A)


def infer_no_cleanup(a: np.ndarray, b_bundle: np.ndarray, d_bundle: np.ndarray,
                     A: np.ndarray, R: np.ndarray) -> int:
    r_hat = unbind(b_bundle, a)
    c_hat = unbind(d_bundle, r_hat)
    return cosine_argmax(c_hat, A)


# -----------------------------------------------------------------------------
# Per-arm-per-K runner
# -----------------------------------------------------------------------------
def run_arm_at_k(arm_mode: str, seed: int, k_dist: int,
                 A: np.ndarray, R: np.ndarray,
                 q: Dict[str, np.ndarray]) -> Dict:
    t0 = time.time()
    target = q["target"]
    try:
        n_hits = 0
        n_q = target.shape[0]
        for i in range(n_q):
            a_idx = int(target[i, 0])
            r_idx = int(target[i, 1])
            c_idx = int(target[i, 2])
            a = A[a_idx]
            b_bundle = build_side_bundle(a_idx, r_idx,
                                         q["dist_a"][i], q["dist_r_a"][i],
                                         A, R, k_dist)
            d_bundle = build_side_bundle(c_idx, r_idx,
                                         q["dist_c"][i], q["dist_r_c"][i],
                                         A, R, k_dist)
            if arm_mode == "ARM_HRR_BIND_UNBIND_CLEANUP":
                pred = infer_cleanup(a, b_bundle, d_bundle, A, R)
            elif arm_mode == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
                pred = infer_no_cleanup(a, b_bundle, d_bundle, A, R)
            else:
                raise ValueError(f"unknown arm_mode: {arm_mode}")
            if pred == c_idx:
                n_hits += 1
        recall = n_hits / float(n_q)
        wall = time.time() - t0
        return {
            "arm_name": f"{arm_mode}_K{k_dist}",
            "arm_mode": arm_mode,
            "K_DIST": int(k_dist),
            "recall_at_1": float(recall),
            "n_queries": int(n_q),
            "n_dim": int(N_DIM),
            "N_C": int(N_CONCEPTS),
            "N_R": int(N_RELATIONS),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": f"{arm_mode}_K{k_dist}",
            "arm_mode": arm_mode,
            "K_DIST": int(k_dist),
            "recall_at_1": float("nan"),
            "n_queries": 0,
            "n_dim": int(N_DIM),
            "N_C": int(N_CONCEPTS),
            "N_R": int(N_RELATIONS),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    A, R = build_codebooks(seed)
    arms: List[Dict] = []
    print(f"  [seed={seed}] built codebooks A=({N_CONCEPTS},{N_DIM}) "
          f"R=({N_RELATIONS},{N_DIM})", flush=True)
    for k_dist in K_DIST_VALUES:
        q = sample_analogies(seed, N_QUERIES, k_dist)
        for arm_mode in ARM_MODES:
            out = run_arm_at_k(arm_mode, seed, k_dist, A, R, q)
            arms.append(out)
            print(
                f"  [seed={seed} K={k_dist} {arm_mode}] "
                f"recall@1={out['recall_at_1']:.3f} "
                f"n_q={out['n_queries']} "
                f"status={out['arm_status']} "
                f"wall={out['wall_s']:.2f}s",
                flush=True,
            )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "n_dim": N_DIM,
        "N_C": N_CONCEPTS,
        "N_R": N_RELATIONS,
        "N_Q": N_QUERIES,
        "K_DIST_VALUES": list(K_DIST_VALUES),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# -----------------------------------------------------------------------------
# Selftests (>= 5)
# -----------------------------------------------------------------------------
def _selftest_bind_unbind_roundtrip() -> None:
    rng = np.random.default_rng(0)
    a = _rand_phasors(rng, (N_DIM,))
    b = _rand_phasors(rng, (N_DIM,))
    c = bind(a, b)
    a_hat = unbind(c, b)
    sim = float((a_hat @ a.conj()).real / N_DIM)
    if not np.isfinite(sim):
        raise AssertionError(f"bind/unbind sim non-finite: {sim}")
    if sim < 0.999:
        raise AssertionError(
            f"bind/unbind round-trip sim={sim:.6f} < 0.999 at n_dim={N_DIM}"
        )


def _selftest_generator_valid_at_all_K() -> None:
    """Analogy generator: no leakage at K in {3, 10, 50}."""
    for k_dist in (3, 10, 50):
        q = sample_analogies(seed=7, n_queries=64, k_dist=k_dist)
        target = q["target"]
        if target.shape != (64, 3):
            raise AssertionError(f"K={k_dist}: target shape {target.shape}")
        a_idx = target[:, 0]; c_idx = target[:, 2]
        if np.any(a_idx == c_idx):
            raise AssertionError(f"K={k_dist}: c_idx == a_idx leak")
        if np.any(q["dist_a"] == a_idx[:, None]):
            raise AssertionError(f"K={k_dist}: dist_a leaked a_idx")
        if np.any(q["dist_c"] == c_idx[:, None]):
            raise AssertionError(f"K={k_dist}: dist_c leaked c_idx")
        for key in ("dist_a", "dist_r_a", "dist_c", "dist_r_c"):
            if q[key].shape != (64, k_dist):
                raise AssertionError(f"K={k_dist}: {key} shape {q[key].shape}")


def _selftest_cleanup_correct_topk() -> None:
    A, R = build_codebooks(seed=13)
    for j in range(min(5, N_RELATIONS)):
        recovered = cleanup_argmax(R[j], R)
        sim = float((recovered @ R[j].conj()).real / N_DIM)
        if sim < 0.999:
            raise AssertionError(
                f"cleanup on clean R[{j}] gave sim={sim:.6f}"
            )
    for i in range(min(5, N_CONCEPTS)):
        pred = cosine_argmax(A[i], A)
        if pred != i:
            raise AssertionError(f"atomic argmax mismatch: A[{i}] -> {pred}")


def _selftest_scale_sentinel_8192() -> None:
    rng = np.random.default_rng(19)
    n_big = 8192
    a = _rand_phasors(rng, (n_big,))
    b = _rand_phasors(rng, (n_big,))
    c = bind(a, b)
    a_hat = unbind(c, b)
    if not np.all(np.isfinite(a_hat)):
        raise AssertionError("scale sentinel n_dim=8192 non-finite")
    sim = float((a_hat @ a.conj()).real / n_big)
    if sim < 0.999:
        raise AssertionError(f"scale sentinel n_dim=8192 sim={sim:.6f}")


def _selftest_regression_sanity_K3() -> None:
    """K=3 must reproduce Cell 1 CLEANUP=0.861 / NO_CLEANUP=0.855 bit-identical.

    Runs the same 3 seeds x 500 queries at K=3 and asserts mean recall@1
    matches Cell 1 measured values within REGRESSION_TOL = 1e-9.

    MEASURED@d:/AI/hd-instrument/data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json
    """
    cleanup_recalls = []
    no_cleanup_recalls = []
    for seed in SEEDS:
        A, R = build_codebooks(seed)
        q = sample_analogies(seed, N_QUERIES, k_dist=3)
        out_c = run_arm_at_k("ARM_HRR_BIND_UNBIND_CLEANUP", seed, 3, A, R, q)
        out_nc = run_arm_at_k("ARM_HRR_BIND_UNBIND_NO_CLEANUP", seed, 3, A, R, q)
        if out_c["arm_status"] != "OK" or out_nc["arm_status"] != "OK":
            raise AssertionError(
                f"seed={seed}: K=3 arm failed "
                f"c={out_c['arm_status']} nc={out_nc['arm_status']}"
            )
        cleanup_recalls.append(out_c["recall_at_1"])
        no_cleanup_recalls.append(out_nc["recall_at_1"])
    cleanup_mean = float(np.mean(cleanup_recalls))
    no_cleanup_mean = float(np.mean(no_cleanup_recalls))
    dc = abs(cleanup_mean - CELL1_K3_CLEANUP_MEAN)
    dnc = abs(no_cleanup_mean - CELL1_K3_NO_CLEANUP_MEAN)
    if dc > REGRESSION_TOL:
        raise AssertionError(
            f"K=3 CLEANUP regression: got {cleanup_mean:.9f} "
            f"expected {CELL1_K3_CLEANUP_MEAN:.9f} delta={dc:.2e} "
            f"> tol={REGRESSION_TOL:.0e}"
        )
    if dnc > REGRESSION_TOL:
        raise AssertionError(
            f"K=3 NO_CLEANUP regression: got {no_cleanup_mean:.9f} "
            f"expected {CELL1_K3_NO_CLEANUP_MEAN:.9f} delta={dnc:.2e} "
            f"> tol={REGRESSION_TOL:.0e}"
        )


def _selftest_arms_must_differ_at_K10() -> None:
    """META_RULE_AF: CLEANUP and NO_CLEANUP produce distinct predictions at K=10.

    K=10 is chosen as a mid-sweep point where the discriminator is expected
    to fire cleanly. Uses a fresh seed (not in SEEDS) to avoid caching arms.
    """
    A, R = build_codebooks(seed=101)
    q = sample_analogies(seed=101, n_queries=64, k_dist=10)
    target = q["target"]
    preds_per_arm: Dict[str, np.ndarray] = {}
    for arm_mode in ARM_MODES:
        preds = np.empty(target.shape[0], dtype=np.int64)
        for i in range(target.shape[0]):
            a_idx = int(target[i, 0])
            r_idx = int(target[i, 1])
            c_idx = int(target[i, 2])
            a = A[a_idx]
            b_bundle = build_side_bundle(a_idx, r_idx,
                                         q["dist_a"][i], q["dist_r_a"][i],
                                         A, R, 10)
            d_bundle = build_side_bundle(c_idx, r_idx,
                                         q["dist_c"][i], q["dist_r_c"][i],
                                         A, R, 10)
            if arm_mode == "ARM_HRR_BIND_UNBIND_CLEANUP":
                preds[i] = infer_cleanup(a, b_bundle, d_bundle, A, R)
            else:
                preds[i] = infer_no_cleanup(a, b_bundle, d_bundle, A, R)
        preds_per_arm[arm_mode] = preds
    digests = {
        name: hashlib.sha256(p.tobytes()).hexdigest()
        for name, p in preds_per_arm.items()
    }
    if digests[ARM_MODES[0]] == digests[ARM_MODES[1]]:
        raise AssertionError(
            f"META_RULE_AF VIOLATION at K=10: arms {ARM_MODES[0]!r} and "
            f"{ARM_MODES[1]!r} bit-identical predictions on smoke batch"
        )


def _instrumentation_selftest() -> None:
    t0 = time.time()
    try:
        _selftest_bind_unbind_roundtrip()
        _selftest_generator_valid_at_all_K()
        _selftest_cleanup_correct_topk()
        _selftest_scale_sentinel_8192()
        _selftest_arms_must_differ_at_K10()
        _selftest_regression_sanity_K3()  # LAST: heavy (3 seeds x 500 x 2 arms)
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        traceback.print_exc()
        sys.exit(3)
    elapsed = time.time() - t0
    print(
        f"[selftest] PASS  n_dim={N_DIM}  N_C={N_CONCEPTS}  N_R={N_RELATIONS}  "
        f"N_Q={N_QUERIES}  K_DIST_VALUES={K_DIST_VALUES}  seeds={SEEDS}  "
        f"mode={RUN_MODE}  elapsed={elapsed:.2f}s",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str, Dict]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.", {})

    n_seeds = len(results)
    total_arms = sum(len(r.get("arms", [])) for r in results)
    expected_arms_per_seed = len(K_DIST_VALUES) * 2
    if n_seeds != len(SEEDS) or total_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"n_seeds={n_seeds}/{len(SEEDS)}, "
                f"total_arms={total_arms}/{EXPECTED_N_UNITS} "
                f"(expected {expected_arms_per_seed} per seed)", {})

    # Collect per-K per-mode recalls across seeds
    per_k_per_mode: Dict[int, Dict[str, List[float]]] = {
        k: {mode: [] for mode in ARM_MODES} for k in K_DIST_VALUES
    }
    for r in results:
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"Arm {a['arm_name']} error seed={r['seed']}: "
                        f"{a['arm_status']}", {})
            per_k_per_mode[int(a["K_DIST"])][a["arm_mode"]].append(
                float(a["recall_at_1"])
            )

    # Compute per-K stats + gap
    k_stats: Dict[int, Dict] = {}
    for k in K_DIST_VALUES:
        cleanup_v = per_k_per_mode[k]["ARM_HRR_BIND_UNBIND_CLEANUP"]
        nc_v = per_k_per_mode[k]["ARM_HRR_BIND_UNBIND_NO_CLEANUP"]
        cleanup_mean = float(np.mean(cleanup_v))
        nc_mean = float(np.mean(nc_v))
        gap = cleanup_mean - nc_mean
        k_stats[k] = {
            "cleanup_mean": cleanup_mean,
            "cleanup_std": float(np.std(cleanup_v)),
            "no_cleanup_mean": nc_mean,
            "no_cleanup_std": float(np.std(nc_v)),
            "gap_cleanup_minus_no_cleanup": gap,
            "hp3_fires": bool(gap >= HP3_THRESHOLD),
        }

    # Find smallest K where HP3 fires
    k_hp3_fires: int | None = None
    for k in sorted(K_DIST_VALUES):
        if k_stats[k]["hp3_fires"]:
            k_hp3_fires = k
            break

    # Regression sanity: K=3 CLEANUP + NO_CLEANUP within 1e-9 of Cell 1
    k3_cleanup = k_stats[3]["cleanup_mean"]
    k3_no_cleanup = k_stats[3]["no_cleanup_mean"]
    dc = abs(k3_cleanup - CELL1_K3_CLEANUP_MEAN)
    dnc = abs(k3_no_cleanup - CELL1_K3_NO_CLEANUP_MEAN)
    regression_ok = (dc <= REGRESSION_TOL and dnc <= REGRESSION_TOL)

    if not regression_ok:
        return ("HARD_FAIL",
                f"HARD_FAIL_REGRESSION_MISMATCH: K=3 arm did not reproduce "
                f"Cell 1 exactly. K=3 CLEANUP={k3_cleanup:.6f} "
                f"(Cell1={CELL1_K3_CLEANUP_MEAN:.6f} delta={dc:.2e}); "
                f"K=3 NO_CLEANUP={k3_no_cleanup:.6f} "
                f"(Cell1={CELL1_K3_NO_CLEANUP_MEAN:.6f} delta={dnc:.2e}); "
                f"tol={REGRESSION_TOL:.0e}",
                {"k_stats": k_stats, "regression_ok": False})

    # Verdict tiers
    # HP: HP3 fires at some K in sweep (some K >= 10 typically) + regression_ok
    # MB: sweep runs cleanly but no K fires HP3 (cleanup does not earn keep on any K)
    # HF: regression mismatch (handled above) OR all arms in error

    gaps_str = " ".join(
        f"K={k}:cleanup={k_stats[k]['cleanup_mean']:.3f} "
        f"nc={k_stats[k]['no_cleanup_mean']:.3f} "
        f"gap={k_stats[k]['gap_cleanup_minus_no_cleanup']:+.3f}"
        f"({'HP3' if k_stats[k]['hp3_fires'] else 'MB'})"
        for k in sorted(K_DIST_VALUES)
    )

    gates = {
        "k_stats": k_stats,
        "k_hp3_fires": k_hp3_fires,
        "regression_ok": True,
        "k3_regression_delta_cleanup": dc,
        "k3_regression_delta_no_cleanup": dnc,
        "hp3_threshold": HP3_THRESHOLD,
        "cell1_k3_cleanup_ref": CELL1_K3_CLEANUP_MEAN,
        "cell1_k3_no_cleanup_ref": CELL1_K3_NO_CLEANUP_MEAN,
    }

    if k_hp3_fires is not None:
        return ("HARD_PASS",
                f"HARD_PASS: K_DIST sweep fires HP3 (cleanup gain >= 0.05) "
                f"at K={k_hp3_fires}. Regression sanity K=3 reproduces Cell 1 "
                f"bit-identical (delta={dc:.2e}). Cleanup earns its keep at "
                f"K>={k_hp3_fires}; refines atom (a) MEASURED_BOUND -> "
                f"CG-upgrade candidate. Per-K gaps: {gaps_str}",
                gates)
    else:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: K_DIST sweep cleanly executed at all K in "
                f"{K_DIST_VALUES}; no K fires HP3 (max gap < {HP3_THRESHOLD}). "
                f"Cleanup does not earn its keep on this canonical FHRR regime "
                f"at any tested distractor count -- strong refinement of "
                f"atom (a) MEASURED_BOUND. Regression K=3 reproduces Cell 1 "
                f"(delta={dc:.2e}). Per-K gaps: {gaps_str}",
                gates)


# -----------------------------------------------------------------------------
# Start marker + crash diagnostic (canonical pattern)
# -----------------------------------------------------------------------------
def _write_start_marker(output_dir: Path) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(diag, fh, indent=2)
    os.replace(str(tmp), str(final))


# -----------------------------------------------------------------------------
# Main driver
# -----------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}", flush=True,
    )

    t_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME}  "
              f"n_dim={N_DIM} N_C={N_CONCEPTS} N_R={N_RELATIONS} "
              f"N_Q={N_QUERIES} K_DIST_VALUES={K_DIST_VALUES} "
              f"mode={RUN_MODE}...", flush=True)
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg, gates = compute_verdict(all_results)
    elapsed_s = time.time() - t_start

    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.2f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    expected_arms_per_seed = len(K_DIST_VALUES) * 2
    cardinality_ok = (
        len(all_results) == len(SEEDS)
        and all(len(r.get("arms", [])) == expected_arms_per_seed for r in all_results)
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} n_dim={N_DIM} N_C={N_CONCEPTS} "
            f"N_R={N_RELATIONS} N_Q={N_QUERIES} "
            f"K_DIST_SWEEP={K_DIST_VALUES} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "N_C": N_CONCEPTS,
        "N_R": N_RELATIONS,
        "N_Q": N_QUERIES,
        "K_DIST_VALUES": list(K_DIST_VALUES),
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "gates": gates,
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
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


if __name__ == "__main__":
    output_dir = get_output_dir(ANCHOR_NAME)
    try:
        _main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(output_dir, _exc)
        raise
