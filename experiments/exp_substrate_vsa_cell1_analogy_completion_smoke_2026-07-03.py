"""Stage 2 VSA Cell 1 -- Analogy Completion (SMOKE).

Parent prereg: preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md
Roadmap prereg: preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md
Anchor: stage2_vsa_cell1_analogy_completion_smoke

Task class A (analogy completion): a:b :: c:? -- VSA-native bind/unbind mechanism.
Substrate mechanism probe on supervised-synthetic analogy task per USER-LOCKED
2026-07-02 discipline ("substrate knows almost nothing"; this is mechanism proof
on designer-supplied test, NOT a general-knowledge claim).

Design (FHRR / Plate 2003, reveal-c formulation of analogy):
  A = N_CONCEPTS atomic concept vectors (unit-magnitude complex phasors)
  R = N_RELATIONS relation vectors (unit-magnitude complex phasors)

  Analogy: given (a, b, d), predict c such that a:b :: c:d.
    b = bundle(bind(a, r), bind(a_1, r_1), ..., bind(a_K, r_K))  # a-side storage
    d = bundle(bind(c, r), bind(c_1, r_1'), ..., bind(c_K, r_K'))  # c-side storage
    Both b and d are FHRR superpositions with K_DISTRACTORS role-filler pairs
    per side -- canonical VSA compositional storage per Plate 1995 / Kanerva
    1988.

  Pipeline:
    r_hat = unbind(b, a)  = r + noise from a-side distractors
    c_hat = unbind(d, r_maybe_cleaned)  # = c + noise
    predict = argmax_i sim(c_hat, A[i])

  CLEANUP arm: r_snap = argmax over R, then c_hat = unbind(d, r_snap).
               When r_snap picks r_true: c_hat = c + d-side noise (r-noise
               eliminated at this hop).  When r_snap picks wrong r_j:
               c_hat = c * (r / r_j) + noise; argmax over A likely misses.
  NO_CLEANUP arm: c_hat = unbind(d, r_hat_noisy).  Both a-side and d-side
                  noise carry through; c_hat = c * (r / r_hat) + ...

  Prediction target: c_idx.  Chance level = 1 / N_CONCEPTS = 1 / 100 = 0.01.

  The two arms diverge because unbind is NOT unitary w.r.t. the argmax over
  atomic A when the "key" r_hat is noisy; cleanup replaces the noisy key with
  a clean codebook member, denoising the retrieval step.
  Predict d given (a, b, c):
    r_hat = unbind(b, a)                # circular correlation via FFT
    CLEANUP arm: r_clean = argmax_j cos(r_hat, R[j]) -> R[argmax]
                 d_hat = bind(c, r_clean); predict = argmax_i cos(d_hat, C[i])
    NO_CLEANUP arm: d_hat = bind(c, r_hat); predict = argmax_i cos(d_hat, C[i])
  Baselines:
    COSINE_ARGMAX: predict = argmax_i cos(c, C[i])  # chance-level by construction
    RANDOM:        predict = random codebook index  # chance floor

Arms (4):
  ARM_HRR_BIND_UNBIND_CLEANUP    (LOAD-BEARING mechanism)
  ARM_HRR_BIND_UNBIND_NO_CLEANUP (ablation: does cleanup earn its keep?)
  ARM_COSINE_ARGMAX_BASELINE     (weak baseline)
  ARM_RANDOM_BASELINE            (chance floor)

HP_SCOPE (from prereg):
  HP1: ARM_HRR_BIND_UNBIND_CLEANUP mean recall@1 >= 0.80
  HP2: CLEANUP - COSINE_ARGMAX >= 0.20 gap
  HP3: CLEANUP - NO_CLEANUP >= 0.05 (cleanup positive control)

Cell-template mandates: META_RULE_AF (arms-must-differ), META_RULE_AH (atomic
metrics write), except SystemExit: raise BEFORE except Exception, start_marker,
crash_diagnostic. ASCII-only. Real-valued HRR (no complex; no sparsification).

PROT-018: no _n<N> suffix in anchor (this is a capability-test cell).
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


ANCHOR_NAME = "stage2_vsa_cell1_analogy_completion_smoke"

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
# Config
# -----------------------------------------------------------------------------
N_DIM = 2048
N_CONCEPTS = 100
N_RELATIONS = 10
N_QUERIES = 500
K_DISTRACTORS = 3  # number of distractor role-filler pairs superposed per side
SEEDS = [11, 17, 23]
EXPECTED_N_UNITS = len(SEEDS) * 4  # 3 seeds x 4 arms = 12

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},n_dim={N_DIM},N_C={N_CONCEPTS},N_R={N_RELATIONS},"
    f"N_Q={N_QUERIES},K_DIST={K_DISTRACTORS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},arms=4,cleanup=k_NN,binding=FHRR_complex_phasors"
)

ARM_NAMES = (
    "ARM_HRR_BIND_UNBIND_CLEANUP",
    "ARM_HRR_BIND_UNBIND_NO_CLEANUP",
    "ARM_COSINE_ARGMAX_BASELINE",
    "ARM_RANDOM_BASELINE",
)


# -----------------------------------------------------------------------------
# VSA primitives (FHRR / Frequency-HRR per Plate 2003).
# Vectors are unit-magnitude complex phasors -- each coordinate has |z|=1.
# bind = elementwise multiply (phasor add); unbind = elementwise multiply by
# conjugate (phasor subtract).  bind/unbind is exact up to floating-point.
# Real-valued HRR (circular convolution) has similar semantics but requires
# unit-magnitude Fourier spectrum which random Gaussians don't have; FHRR
# is cleaner and matches hdlab.binding.bind's complex path.
# -----------------------------------------------------------------------------
def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind: elementwise complex multiply. a, b: (n_dim,) complex128."""
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR unbind: elementwise multiply by conjugate. c, b: (n_dim,) complex128."""
    return c * b.conj()


def _fhrr_similarity(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """FHRR cosine sim: Re(<codebook, query>) / n_dim (each vec has |z|_2^2 = n_dim).

    codebook: (M, n_dim) complex; query: (n_dim,) complex -> sims: (M,) real.
    """
    dots = (codebook @ query.conj()).real  # Re(sum_k cb[k] * conj(q[k]))
    # both codebook and query have unit-magnitude coords so |x|^2 = n_dim
    return dots / float(query.shape[0])


def cosine_argmax(query: np.ndarray, codebook: np.ndarray) -> int:
    """argmax_i sim(query, codebook[i]).  codebook: (M, n_dim) complex."""
    sims = _fhrr_similarity(query, codebook)
    return int(np.argmax(sims))


def cleanup_argmax(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """k_NN cleanup: return codebook[argmax] (a unit-phasor vector)."""
    idx = cosine_argmax(query, codebook)
    return codebook[idx].copy()


def _rand_phasors(rng: np.random.Generator, shape) -> np.ndarray:
    """Return unit-magnitude complex phasors of the given shape."""
    phases = rng.uniform(-np.pi, np.pi, size=shape).astype(np.float64)
    return np.exp(1j * phases)


def bundle(vecs: np.ndarray) -> np.ndarray:
    """FHRR bundle: per-coord phase-average (normalize sum to unit magnitude).

    vecs: (K, n_dim) complex.  Returns (n_dim,) complex with |z_k|=1 per coord.
    Any coord whose magnitude is exactly 0 gets set to 1+0j (phase 0).
    """
    s = vecs.sum(axis=0)
    mag = np.abs(s)
    mag[mag < 1e-12] = 1.0
    return s / mag


# -----------------------------------------------------------------------------
# Codebook + analogy generation
# -----------------------------------------------------------------------------
def build_codebooks(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """FHRR codebooks. Returns (A, R):
      A: (N_CONCEPTS, n_dim) atomic phasor concepts
      R: (N_RELATIONS, n_dim) relation phasor vectors
    """
    rng = np.random.default_rng(seed)
    A = _rand_phasors(rng, (N_CONCEPTS, N_DIM))
    R = _rand_phasors(rng, (N_RELATIONS, N_DIM))
    return A, R


def sample_analogies(seed: int, n_queries: int) -> Dict[str, np.ndarray]:
    """Sample analogy queries with K_DISTRACTORS role-filler pairs per side.

    Returns dict with:
      target:   (n_queries, 3)  cols [a_idx, r_idx, c_idx]  (c_idx != a_idx)
      dist_a:   (n_queries, K_DISTRACTORS)  distractor concepts for b-side (!=a)
      dist_r_a: (n_queries, K_DISTRACTORS)  distractor relations for b-side
      dist_c:   (n_queries, K_DISTRACTORS)  distractor concepts for d-side (!=c)
      dist_r_c: (n_queries, K_DISTRACTORS)  distractor relations for d-side
    """
    rng = np.random.default_rng(seed + 991)
    target = np.empty((n_queries, 3), dtype=np.int64)
    dist_a = np.empty((n_queries, K_DISTRACTORS), dtype=np.int64)
    dist_r_a = np.empty((n_queries, K_DISTRACTORS), dtype=np.int64)
    dist_c = np.empty((n_queries, K_DISTRACTORS), dtype=np.int64)
    dist_r_c = np.empty((n_queries, K_DISTRACTORS), dtype=np.int64)
    for q in range(n_queries):
        a_idx = int(rng.integers(0, N_CONCEPTS))
        r_idx = int(rng.integers(0, N_RELATIONS))
        c_idx = int(rng.integers(0, N_CONCEPTS))
        while c_idx == a_idx:
            c_idx = int(rng.integers(0, N_CONCEPTS))
        target[q] = (a_idx, r_idx, c_idx)
        for k in range(K_DISTRACTORS):
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
                      A: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Build FHRR superposition: bundle target-binding + K distractor-bindings."""
    vecs = np.empty((1 + K_DISTRACTORS, N_DIM), dtype=np.complex128)
    vecs[0] = A[concept_idx] * R[r_idx]  # bind
    for k in range(K_DISTRACTORS):
        vecs[1 + k] = A[dist_concept_idx[k]] * R[dist_r_idx[k]]
    return bundle(vecs)


# -----------------------------------------------------------------------------
# Per-arm inference
# -----------------------------------------------------------------------------
def infer_cleanup(a: np.ndarray, b_bundle: np.ndarray, d_bundle: np.ndarray,
                  A: np.ndarray, R: np.ndarray) -> int:
    """CLEANUP arm: r_hat = unbind(b, a); r_snap = argmax over R;
       c_hat = unbind(d, r_snap); predict = argmax_i sim(c_hat, A[i])."""
    r_hat = unbind(b_bundle, a)
    r_snap = cleanup_argmax(r_hat, R)
    c_hat = unbind(d_bundle, r_snap)
    return cosine_argmax(c_hat, A)


def infer_no_cleanup(a: np.ndarray, b_bundle: np.ndarray, d_bundle: np.ndarray,
                     A: np.ndarray, R: np.ndarray) -> int:
    """NO_CLEANUP arm: c_hat = unbind(d, unbind(b, a));  no R-snap."""
    r_hat = unbind(b_bundle, a)
    c_hat = unbind(d_bundle, r_hat)
    return cosine_argmax(c_hat, A)


def infer_cosine_baseline(a: np.ndarray, b_bundle: np.ndarray,
                          d_bundle: np.ndarray,
                          A: np.ndarray, R: np.ndarray) -> int:
    """Weak baseline: predict c = argmax_i cos(d_bundle, A[i]) directly.
    d_bundle is a superposition of bind()'d pairs; atomic argmax has no
    structural alignment -- expected chance."""
    return cosine_argmax(d_bundle, A)


def infer_random(a: np.ndarray, b_bundle: np.ndarray, d_bundle: np.ndarray,
                 A: np.ndarray, R: np.ndarray,
                 rng: np.random.Generator) -> int:
    """Chance floor."""
    return int(rng.integers(0, N_CONCEPTS))


# -----------------------------------------------------------------------------
# Selftests (>= 5)
# -----------------------------------------------------------------------------
def _selftest_bind_unbind_roundtrip() -> None:
    """FHRR bind then unbind reproduces the original exactly (up to float)."""
    rng = np.random.default_rng(0)
    a = _rand_phasors(rng, (N_DIM,))
    b = _rand_phasors(rng, (N_DIM,))
    c = bind(a, b)
    a_hat = unbind(c, b)
    # sim(a_hat, a) = Re(sum a_hat * conj(a)) / n_dim = 1.0 (exact for FHRR)
    sim = float((a_hat @ a.conj()).real / N_DIM)
    if not np.isfinite(sim):
        raise AssertionError(f"bind/unbind sim non-finite: {sim}")
    if sim < 0.999:
        raise AssertionError(
            f"bind/unbind round-trip sim={sim:.6f} < 0.999 at n_dim={N_DIM}"
        )


def _selftest_analogy_generator_valid() -> None:
    q = sample_analogies(seed=7, n_queries=200)
    target = q["target"]
    if target.shape != (200, 3):
        raise AssertionError(f"analogy target shape wrong: {target.shape}")
    a_idx = target[:, 0]; c_idx = target[:, 2]
    if np.any(a_idx == c_idx):
        raise AssertionError("analogy generator leaked c_idx == a_idx")
    if np.any(a_idx < 0) or np.any(a_idx >= N_CONCEPTS):
        raise AssertionError("a_idx out of range")
    if np.any(c_idx < 0) or np.any(c_idx >= N_CONCEPTS):
        raise AssertionError("c_idx out of range")
    if np.any(target[:, 1] < 0) or np.any(target[:, 1] >= N_RELATIONS):
        raise AssertionError("r_idx out of range")
    # Distractor concept indices must differ from target on each side.
    if np.any(q["dist_a"] == a_idx[:, None]):
        raise AssertionError("dist_a leaked target a_idx")
    if np.any(q["dist_c"] == c_idx[:, None]):
        raise AssertionError("dist_c leaked target c_idx")
    for key in ("dist_a", "dist_r_a", "dist_c", "dist_r_c"):
        if q[key].shape != (200, K_DISTRACTORS):
            raise AssertionError(f"{key} shape wrong: {q[key].shape}")


def _selftest_cleanup_correct_topk() -> None:
    """Cleanup on clean codebook entry returns same vector (identity)."""
    A, R = build_codebooks(seed=13)
    for j in range(min(5, N_RELATIONS)):
        recovered = cleanup_argmax(R[j], R)
        sim = float((recovered @ R[j].conj()).real / N_DIM)
        if sim < 0.999:
            raise AssertionError(
                f"cleanup on clean R[{j}] gave sim={sim:.6f} (should be 1.0)"
            )
    # Atomic argmax selftest: clean A[i] retrieves index i.
    for i in range(min(5, N_CONCEPTS)):
        pred = cosine_argmax(A[i], A)
        if pred != i:
            raise AssertionError(f"atomic argmax mismatch: A[{i}] -> {pred}")


def _selftest_scale_sentinel_8192() -> None:
    """FHRR bind/unbind at n_dim=8192 stays finite and identity."""
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


def _selftest_deterministic_seed_invariance() -> None:
    """Same seed reproduces recall@1 to 1e-6."""
    r1 = _run_arm_recall_single_seed_shortcut(
        seed=42, arm_name="ARM_HRR_BIND_UNBIND_CLEANUP", n_queries=20
    )
    r2 = _run_arm_recall_single_seed_shortcut(
        seed=42, arm_name="ARM_HRR_BIND_UNBIND_CLEANUP", n_queries=20
    )
    if abs(r1 - r2) > 1e-6:
        raise AssertionError(
            f"seed invariance broken: r1={r1:.6f} r2={r2:.6f} delta={abs(r1 - r2):.2e}"
        )


def _selftest_arms_must_differ() -> None:
    """META_RULE_AF: all 4 arms produce different predictions on a shared batch."""
    A, R = build_codebooks(seed=101)
    q = sample_analogies(seed=101, n_queries=64)
    target = q["target"]
    preds_per_arm: Dict[str, np.ndarray] = {}
    rng_rand = np.random.default_rng(101 + 7)
    for arm in ARM_NAMES:
        preds = np.empty(target.shape[0], dtype=np.int64)
        for i in range(target.shape[0]):
            a_idx, r_idx, c_idx = int(target[i, 0]), int(target[i, 1]), int(target[i, 2])
            a = A[a_idx]
            b_bundle = build_side_bundle(a_idx, r_idx,
                                         q["dist_a"][i], q["dist_r_a"][i], A, R)
            d_bundle = build_side_bundle(c_idx, r_idx,
                                         q["dist_c"][i], q["dist_r_c"][i], A, R)
            if arm == "ARM_HRR_BIND_UNBIND_CLEANUP":
                preds[i] = infer_cleanup(a, b_bundle, d_bundle, A, R)
            elif arm == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
                preds[i] = infer_no_cleanup(a, b_bundle, d_bundle, A, R)
            elif arm == "ARM_COSINE_ARGMAX_BASELINE":
                preds[i] = infer_cosine_baseline(a, b_bundle, d_bundle, A, R)
            elif arm == "ARM_RANDOM_BASELINE":
                preds[i] = infer_random(a, b_bundle, d_bundle, A, R, rng_rand)
            else:
                raise AssertionError(f"unknown arm: {arm}")
        preds_per_arm[arm] = preds
    digests = {
        name: hashlib.sha256(p.tobytes()).hexdigest()
        for name, p in preds_per_arm.items()
    }
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} "
                    f"bit-identical predictions on smoke batch"
                )
    return


def _run_arm_recall_single_seed_shortcut(seed: int, arm_name: str,
                                         n_queries: int) -> float:
    """Compact per-arm recall for selftests only.  Full runner is run_seed."""
    A, R = build_codebooks(seed=seed)
    q = sample_analogies(seed=seed, n_queries=n_queries)
    target = q["target"]
    rng_rand = np.random.default_rng(seed + 7)
    n_hits = 0
    for i in range(target.shape[0]):
        a_idx, r_idx, c_idx = int(target[i, 0]), int(target[i, 1]), int(target[i, 2])
        a = A[a_idx]
        b_bundle = build_side_bundle(a_idx, r_idx,
                                     q["dist_a"][i], q["dist_r_a"][i], A, R)
        d_bundle = build_side_bundle(c_idx, r_idx,
                                     q["dist_c"][i], q["dist_r_c"][i], A, R)
        if arm_name == "ARM_HRR_BIND_UNBIND_CLEANUP":
            pred = infer_cleanup(a, b_bundle, d_bundle, A, R)
        elif arm_name == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
            pred = infer_no_cleanup(a, b_bundle, d_bundle, A, R)
        elif arm_name == "ARM_COSINE_ARGMAX_BASELINE":
            pred = infer_cosine_baseline(a, b_bundle, d_bundle, A, R)
        else:
            pred = infer_random(a, b_bundle, d_bundle, A, R, rng_rand)
        if pred == c_idx:
            n_hits += 1
    return n_hits / float(n_queries)


def _instrumentation_selftest() -> None:
    t0 = time.time()
    try:
        _selftest_bind_unbind_roundtrip()
        _selftest_analogy_generator_valid()
        _selftest_cleanup_correct_topk()
        _selftest_scale_sentinel_8192()
        _selftest_deterministic_seed_invariance()
        _selftest_arms_must_differ()
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
        f"N_Q={N_QUERIES}  seeds={SEEDS}  mode={RUN_MODE}  "
        f"elapsed={elapsed:.2f}s",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# -----------------------------------------------------------------------------
# Per-seed runner
# -----------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            A: np.ndarray, R: np.ndarray,
            q: Dict[str, np.ndarray],
            rng_rand: np.random.Generator) -> Dict:
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
                                         q["dist_a"][i], q["dist_r_a"][i], A, R)
            d_bundle = build_side_bundle(c_idx, r_idx,
                                         q["dist_c"][i], q["dist_r_c"][i], A, R)
            if arm_name == "ARM_HRR_BIND_UNBIND_CLEANUP":
                pred = infer_cleanup(a, b_bundle, d_bundle, A, R)
            elif arm_name == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
                pred = infer_no_cleanup(a, b_bundle, d_bundle, A, R)
            elif arm_name == "ARM_COSINE_ARGMAX_BASELINE":
                pred = infer_cosine_baseline(a, b_bundle, d_bundle, A, R)
            elif arm_name == "ARM_RANDOM_BASELINE":
                pred = infer_random(a, b_bundle, d_bundle, A, R, rng_rand)
            else:
                raise ValueError(f"unknown arm: {arm_name}")
            if pred == c_idx:
                n_hits += 1
        recall = n_hits / float(n_q)
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_1": float(recall),
            "n_queries": int(n_q),
            "n_dim": int(N_DIM),
            "N_C": int(N_CONCEPTS),
            "N_R": int(N_RELATIONS),
            "K_DISTRACTORS": int(K_DISTRACTORS),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_1": float("nan"),
            "n_queries": 0,
            "n_dim": int(N_DIM),
            "N_C": int(N_CONCEPTS),
            "N_R": int(N_RELATIONS),
            "K_DISTRACTORS": int(K_DISTRACTORS),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    A, R = build_codebooks(seed)
    q = sample_analogies(seed, N_QUERIES)
    rng_rand = np.random.default_rng(seed + 7)
    print(f"  [seed={seed}] built codebooks A=({N_CONCEPTS},{N_DIM}) "
          f"R=({N_RELATIONS},{N_DIM}); "
          f"{q['target'].shape[0]} queries, K_dist={K_DISTRACTORS}",
          flush=True)
    arms = []
    for arm_name in ARM_NAMES:
        out = run_arm(arm_name, seed, A, R, q, rng_rand)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
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
        "K_DISTRACTORS": K_DISTRACTORS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str, Dict]:
    """Returns (verdict, verdict_msg, per_gate_dict)."""
    if not results:
        return ("HARD_FAIL", "No valid seed results.", {})

    # Cardinality (META_RULE_H)
    n_seeds = len(results)
    total_arms = sum(len(r.get("arms", [])) for r in results)
    if n_seeds != len(SEEDS) or total_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"n_seeds={n_seeds}/{len(SEEDS)}, "
                f"total_arms={total_arms}/{EXPECTED_N_UNITS}", {})

    per_arm_recalls: Dict[str, List[float]] = {n: [] for n in ARM_NAMES}
    for r in results:
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"Arm {a['arm_name']} error seed={r['seed']}: "
                        f"{a['arm_status']}", {})
            per_arm_recalls[a["arm_name"]].append(float(a["recall_at_1"]))

    mean_per_arm = {n: float(np.mean(v)) for n, v in per_arm_recalls.items()}
    std_per_arm = {n: float(np.std(v)) for n, v in per_arm_recalls.items()}

    cleanup = mean_per_arm["ARM_HRR_BIND_UNBIND_CLEANUP"]
    no_cleanup = mean_per_arm["ARM_HRR_BIND_UNBIND_NO_CLEANUP"]
    cosine_base = mean_per_arm["ARM_COSINE_ARGMAX_BASELINE"]
    random_base = mean_per_arm["ARM_RANDOM_BASELINE"]

    hp1 = cleanup >= 0.80
    hp2 = (cleanup - cosine_base) >= 0.20
    hp3 = (cleanup - no_cleanup) >= 0.05

    # HARD_FAIL bands
    if cleanup < 0.50:
        return ("HARD_FAIL",
                f"HARD_FAIL_HF1: ARM_HRR_BIND_UNBIND_CLEANUP mean recall@1={cleanup:.3f} "
                f"< 0.50; mechanism does not work on intended VSA-native task class. "
                f"cleanup={cleanup:.3f} no_cleanup={no_cleanup:.3f} "
                f"cosine_base={cosine_base:.3f} random_base={random_base:.3f}",
                {"cleanup": cleanup, "no_cleanup": no_cleanup,
                 "cosine_base": cosine_base, "random_base": random_base,
                 "hp1": hp1, "hp2": hp2, "hp3": hp3})

    if cosine_base > 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL_baseline: ARM_COSINE_ARGMAX_BASELINE={cosine_base:.3f} "
                f"> 0.30; task not VSA-load-bearing (baseline sees structural leakage). "
                f"cleanup={cleanup:.3f}",
                {"cleanup": cleanup, "no_cleanup": no_cleanup,
                 "cosine_base": cosine_base, "random_base": random_base,
                 "hp1": hp1, "hp2": hp2, "hp3": hp3})

    summary = (
        f"n_seeds={n_seeds} n_dim={N_DIM} N_C={N_CONCEPTS} N_R={N_RELATIONS} "
        f"N_Q={N_QUERIES} | "
        f"CLEANUP={cleanup:.3f}+/-{std_per_arm['ARM_HRR_BIND_UNBIND_CLEANUP']:.3f} "
        f"NO_CLEANUP={no_cleanup:.3f}+/-{std_per_arm['ARM_HRR_BIND_UNBIND_NO_CLEANUP']:.3f} "
        f"COSINE_BASE={cosine_base:.3f} RANDOM={random_base:.3f} | "
        f"HP1(>=0.80)={hp1} HP2(gap>=0.20)={hp2}(gap={cleanup - cosine_base:+.3f}) "
        f"HP3(cleanup_gain>=0.05)={hp3}(gain={cleanup - no_cleanup:+.3f})"
    )
    gates = {
        "cleanup": cleanup, "no_cleanup": no_cleanup,
        "cosine_base": cosine_base, "random_base": random_base,
        "hp1": hp1, "hp2": hp2, "hp3": hp3,
        "cleanup_minus_cosine": cleanup - cosine_base,
        "cleanup_minus_no_cleanup": cleanup - no_cleanup,
        "std_per_arm": std_per_arm,
    }

    if hp1 and hp2 and hp3:
        return ("HARD_PASS",
                f"HARD_PASS: HP1+HP2+HP3 all cleared. "
                f"VSA-native mechanism performs analogy completion cleanly with "
                f"positive-control cleanup gain. {summary}",
                gates)

    if hp1 and hp2 and not hp3:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: HP1+HP2 cleared but cleanup ablation "
                f"gain={cleanup - no_cleanup:+.3f} < 0.05 (cleanup does not earn "
                f"its keep on this regime; ablation-safe). {summary}",
                gates)

    if hp1 and not hp2:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: mechanism works (HP1) but gap-to-baseline "
                f"gap={cleanup - cosine_base:+.3f} < 0.20 -- regime-too-easy pattern "
                f"(baseline saturates similarly). {summary}",
                gates)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: HP checks partial "
            f"hp=[hp1={hp1},hp2={hp2},hp3={hp3}]. {summary}",
            gates)


# -----------------------------------------------------------------------------
# Start marker + crash diagnostic (canonical exp_dev.md pattern)
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

    run_config = {
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}",
        flush=True,
    )

    t_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] stage2_vsa_cell1_analogy_completion  "
              f"n_dim={N_DIM} N_C={N_CONCEPTS} N_R={N_RELATIONS} "
              f"N_Q={N_QUERIES} mode={RUN_MODE}...",
              flush=True)
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

    cardinality_ok = (
        len(all_results) == len(SEEDS)
        and all(len(r.get("arms", [])) == 4 for r in all_results)
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} n_dim={N_DIM} N_C={N_CONCEPTS} "
            f"N_R={N_RELATIONS} N_Q={N_QUERIES} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "N_C": N_CONCEPTS,
        "N_R": N_RELATIONS,
        "N_Q": N_QUERIES,
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
