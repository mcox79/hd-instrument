"""Stage 2 VSA Cell 2 -- Compositional Generalization (SMOKE).

Parent prereg: preregs/2026-07-03_stage2_vsa_cell2_compositional_generalization_smoke.md
Roadmap prereg: preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md
Anchor: stage2_vsa_cell2_compositional_generalization_smoke

Task class B (compositional generalization): substrate must handle novel (role,
filler) combinations never bundled at training. 5 roles x 100 fillers = 500
possible combinations; 300 seen + 200 held-out; test on held-out pairs only.

Design (FHRR / Plate 2003, compositional-generalization formulation):
  R = N_ROLES atomic role vectors     (unit-magnitude complex phasors)
  F = N_FILLERS atomic filler vectors (unit-magnitude complex phasors)

  ALL_PAIRS = {(r, f) for r in R, f in F}  # 500 total
  SEEN = 300 pairs sampled uniformly    # used only by STORED_BUNDLE arm
  HELDOUT = 200 remaining pairs         # test queries

  Test procedure per held-out (role_q, filler_true):
    Distractors: sample K_DIST=10 other held-out pairs (never overlap target)
    Test bundle B_q = bundle(
        [bind(role_q, filler_true)] +
        [bind(role_dist_k, filler_dist_k) for k in K_DIST])
    Query: filler_hat = unbind(B_q, role_q)  = filler_true + K_DIST noise terms

  Arms (5):
    ARM_HRR_BIND_UNBIND_CLEANUP    -- filler_hat -> argmax over F codebook
                                      (LOAD-BEARING; test-time composition)
    ARM_HRR_BIND_UNBIND_NO_CLEANUP -- skip unbind: raw B_q -> argmax over F
                                      (ablation; K=10 forces separation)
    ARM_HRR_STORED_BUNDLE_LOOKUP   -- M_stored = bundle(all SEEN pairs);
                                      unbind(M_stored, role_q) -> argmax F
                                      (fair baseline; filler_true NOT in M_stored
                                       by held-out construction; expected ~0.0)
    ARM_COSINE_ARGMAX_BASELINE     -- argmax_i cos(role_q, F[i]) direct
                                      (weak; chance-level by construction)
    ARM_RANDOM_BASELINE            -- random filler index (chance floor)

HP_SCOPE (from prereg):
  HP1: ARM_HRR_BIND_UNBIND_CLEANUP mean recall@1 >= 0.60
  HP2: CLEANUP - NO_CLEANUP >= 0.10  (K_DIST=10 forces this; Cell 1 HP3 failed at K=3)
  HP3: CLEANUP - STORED_BUNDLE >= 0.05  (compositional generalization non-trivial)
  HP4: CLEANUP - COSINE >= 0.30

HF: CLEANUP < 0.30
MB: 0.30 <= CLEANUP < 0.60

Cell-template mandates: META_RULE_AF (arms-must-differ), META_RULE_AH (atomic
metrics write), except SystemExit: raise BEFORE except Exception, start_marker,
crash_diagnostic. ASCII-only. FHRR complex phasors.
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


ANCHOR_NAME = "stage2_vsa_cell2_compositional_generalization_smoke"

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
N_ROLES = 5
N_FILLERS = 100
N_SEEN = 300           # of 500 total combinations; 60% seen
N_HELDOUT = 200        # never bundled during "training"; test set
K_DISTRACTORS = 10     # Skunkworks-flagged threshold; forces cleanup discriminator
SEEDS = [11, 17, 23]
EXPECTED_N_UNITS = len(SEEDS) * 5  # 3 seeds x 5 arms = 15

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},n_dim={N_DIM},N_R={N_ROLES},N_F={N_FILLERS},"
    f"N_SEEN={N_SEEN},N_HELDOUT={N_HELDOUT},K_DIST={K_DISTRACTORS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},arms=5,cleanup=k_NN,binding=FHRR_complex_phasors"
)

ARM_NAMES = (
    "ARM_HRR_BIND_UNBIND_CLEANUP",
    "ARM_HRR_BIND_UNBIND_NO_CLEANUP",
    "ARM_HRR_STORED_BUNDLE_LOOKUP",
    "ARM_COSINE_ARGMAX_BASELINE",
    "ARM_RANDOM_BASELINE",
)


# -----------------------------------------------------------------------------
# FHRR primitives (per Plate 2003).
# Vectors are unit-magnitude complex phasors -- each coordinate has |z|=1.
# bind = elementwise multiply (phasor add); unbind = elementwise multiply by
# conjugate.  bind/unbind is exact up to floating-point.
# -----------------------------------------------------------------------------
def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind: elementwise complex multiply. a, b: (n_dim,) complex128."""
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR unbind: elementwise multiply by conjugate. c, b: (n_dim,) complex128."""
    return c * b.conj()


def _fhrr_similarity(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """FHRR cosine sim: Re(<codebook, query>) / n_dim (unit-magnitude coords).

    codebook: (M, n_dim) complex; query: (n_dim,) complex -> sims: (M,) real.
    """
    dots = (codebook @ query.conj()).real
    return dots / float(query.shape[0])


def cosine_argmax(query: np.ndarray, codebook: np.ndarray) -> int:
    """argmax_i sim(query, codebook[i]). codebook: (M, n_dim) complex."""
    sims = _fhrr_similarity(query, codebook)
    return int(np.argmax(sims))


def _rand_phasors(rng: np.random.Generator, shape) -> np.ndarray:
    """Return unit-magnitude complex phasors of the given shape."""
    phases = rng.uniform(-np.pi, np.pi, size=shape).astype(np.float64)
    return np.exp(1j * phases)


def bundle(vecs: np.ndarray) -> np.ndarray:
    """FHRR bundle: per-coord phase-average (normalize sum to unit magnitude).

    vecs: (K, n_dim) complex.  Returns (n_dim,) complex with |z_k|=1 per coord.
    """
    s = vecs.sum(axis=0)
    mag = np.abs(s)
    mag[mag < 1e-12] = 1.0
    return s / mag


# -----------------------------------------------------------------------------
# Codebook + data split
# -----------------------------------------------------------------------------
def build_codebooks(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """FHRR codebooks. Returns (R, F):
      R: (N_ROLES, n_dim) atomic phasor roles
      F: (N_FILLERS, n_dim) atomic phasor fillers
    """
    rng = np.random.default_rng(seed)
    R = _rand_phasors(rng, (N_ROLES, N_DIM))
    F = _rand_phasors(rng, (N_FILLERS, N_DIM))
    return R, F


def split_pairs(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Split all (role, filler) combinations into seen + held-out.

    Returns (seen, heldout) as int64 arrays of shape (N_SEEN, 2) and
    (N_HELDOUT, 2) with columns [role_idx, filler_idx].
    """
    rng = np.random.default_rng(seed + 991)
    all_pairs = np.array(
        [(r, f) for r in range(N_ROLES) for f in range(N_FILLERS)],
        dtype=np.int64,
    )
    if all_pairs.shape[0] != N_ROLES * N_FILLERS:
        raise AssertionError(
            f"all_pairs count wrong: {all_pairs.shape[0]} != {N_ROLES * N_FILLERS}"
        )
    if N_SEEN + N_HELDOUT != all_pairs.shape[0]:
        raise AssertionError(
            f"N_SEEN + N_HELDOUT ({N_SEEN + N_HELDOUT}) != total pairs "
            f"({all_pairs.shape[0]})"
        )
    perm = rng.permutation(all_pairs.shape[0])
    seen = all_pairs[perm[:N_SEEN]]
    heldout = all_pairs[perm[N_SEEN:]]
    return seen, heldout


def sample_distractor_indices(seed: int, n_queries: int,
                              n_available: int) -> np.ndarray:
    """For each query, sample K_DISTRACTORS distinct indices in [0, n_available)
    NOT equal to the query index. Returns (n_queries, K_DISTRACTORS) int64.
    """
    rng = np.random.default_rng(seed + 2027)
    out = np.empty((n_queries, K_DISTRACTORS), dtype=np.int64)
    for q in range(n_queries):
        candidates = list(range(n_available))
        candidates.remove(q)
        chosen = rng.choice(candidates, size=K_DISTRACTORS, replace=False)
        out[q] = chosen
    return out


# -----------------------------------------------------------------------------
# Per-arm inference primitives
# -----------------------------------------------------------------------------
def build_test_bundle(role_q_idx: int, filler_true_idx: int,
                      distractor_pairs: np.ndarray,
                      R: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Test-time bundle: target binding + K_DIST distractor bindings.

    role_q_idx, filler_true_idx: target ints.
    distractor_pairs: (K_DISTRACTORS, 2) int64, cols [role_idx, filler_idx].
    """
    vecs = np.empty((1 + K_DISTRACTORS, N_DIM), dtype=np.complex128)
    vecs[0] = R[role_q_idx] * F[filler_true_idx]  # bind
    for k in range(K_DISTRACTORS):
        r_k = int(distractor_pairs[k, 0])
        f_k = int(distractor_pairs[k, 1])
        vecs[1 + k] = R[r_k] * F[f_k]
    return bundle(vecs)


def infer_cleanup(role_q_idx: int, B_q: np.ndarray,
                  R: np.ndarray, F: np.ndarray,
                  M_stored: np.ndarray) -> int:
    """CLEANUP arm: filler_hat = unbind(B_q, role_q); argmax over F codebook.
    LOAD-BEARING test-time composition path."""
    filler_hat = unbind(B_q, R[role_q_idx])
    return cosine_argmax(filler_hat, F)


def infer_no_cleanup(role_q_idx: int, B_q: np.ndarray,
                     R: np.ndarray, F: np.ndarray,
                     M_stored: np.ndarray) -> int:
    """NO_CLEANUP arm: SKIP unbind. Predict argmax over F directly on the
    raw test bundle B_q -- bundle contains bind(r, f) products so raw cos
    with any single filler f_j has expected magnitude ~ O(1/sqrt(n_dim));
    argmax over 100 near-uniform similarities -> chance-level.

    Discriminator against CLEANUP: at K_DIST=10 the unbind step recovers
    filler_true + noise, whose argmax over F picks filler_true reliably;
    without unbind, no such recovery."""
    return cosine_argmax(B_q, F)


def infer_stored_bundle(role_q_idx: int, B_q: np.ndarray,
                        R: np.ndarray, F: np.ndarray,
                        M_stored: np.ndarray) -> int:
    """STORED_BUNDLE arm: fair baseline using ONLY the SEEN pairs bundled once.
    filler_hat = unbind(M_stored, role_q); argmax over F.

    By held-out construction, (role_q, filler_true) is NOT in M_stored, so
    filler_hat = superposition of ~N_SEEN/N_ROLES seen fillers paired with
    role_q -- filler_true not among them. Expected recall ~= 0.0."""
    filler_hat = unbind(M_stored, R[role_q_idx])
    return cosine_argmax(filler_hat, F)


def infer_cosine_baseline(role_q_idx: int, B_q: np.ndarray,
                          R: np.ndarray, F: np.ndarray,
                          M_stored: np.ndarray) -> int:
    """Weak baseline: direct argmax of cos(role_q, F[i]). Random-vs-random
    similarity, chance-level."""
    return cosine_argmax(R[role_q_idx], F)


def infer_random(role_q_idx: int, B_q: np.ndarray,
                 R: np.ndarray, F: np.ndarray,
                 M_stored: np.ndarray,
                 rng: np.random.Generator) -> int:
    """Chance floor: random filler index."""
    return int(rng.integers(0, N_FILLERS))


# -----------------------------------------------------------------------------
# Selftests
# -----------------------------------------------------------------------------
def _selftest_bind_unbind_roundtrip() -> None:
    """FHRR bind then unbind reproduces the original exactly (up to float)."""
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


def _selftest_data_split_valid() -> None:
    """Verify seen + held-out split is disjoint, correct sizes, valid indices."""
    seen, heldout = split_pairs(seed=7)
    if seen.shape != (N_SEEN, 2):
        raise AssertionError(f"seen shape wrong: {seen.shape}")
    if heldout.shape != (N_HELDOUT, 2):
        raise AssertionError(f"heldout shape wrong: {heldout.shape}")
    # No overlap between seen and heldout
    seen_set = set(map(tuple, seen.tolist()))
    heldout_set = set(map(tuple, heldout.tolist()))
    overlap = seen_set & heldout_set
    if overlap:
        raise AssertionError(f"seen/heldout overlap: {len(overlap)} pairs")
    # Union covers all 500 combinations exactly once
    if len(seen_set | heldout_set) != N_ROLES * N_FILLERS:
        raise AssertionError(
            f"union size wrong: {len(seen_set | heldout_set)} != "
            f"{N_ROLES * N_FILLERS}"
        )
    # Indices in valid range
    if seen[:, 0].max() >= N_ROLES or seen[:, 0].min() < 0:
        raise AssertionError("seen role_idx out of range")
    if seen[:, 1].max() >= N_FILLERS or seen[:, 1].min() < 0:
        raise AssertionError("seen filler_idx out of range")


def _selftest_cleanup_argmax_correct() -> None:
    """Clean codebook entry retrieves its own index."""
    R, F = build_codebooks(seed=13)
    for i in range(min(5, N_FILLERS)):
        pred = cosine_argmax(F[i], F)
        if pred != i:
            raise AssertionError(f"atomic filler argmax mismatch: F[{i}] -> {pred}")
    for j in range(min(3, N_ROLES)):
        pred = cosine_argmax(R[j], R)
        if pred != j:
            raise AssertionError(f"atomic role argmax mismatch: R[{j}] -> {pred}")


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
    r1 = _run_arm_shortcut(seed=42, arm_name="ARM_HRR_BIND_UNBIND_CLEANUP",
                           n_queries=20)
    r2 = _run_arm_shortcut(seed=42, arm_name="ARM_HRR_BIND_UNBIND_CLEANUP",
                           n_queries=20)
    if abs(r1 - r2) > 1e-6:
        raise AssertionError(
            f"seed invariance broken: r1={r1:.6f} r2={r2:.6f} "
            f"delta={abs(r1 - r2):.2e}"
        )


def _selftest_arms_must_differ() -> None:
    """META_RULE_AF: all 5 arms produce distinct predictions on a shared batch."""
    R, F = build_codebooks(seed=101)
    seen, heldout = split_pairs(seed=101)
    n_probe = min(64, N_HELDOUT)
    distractors = sample_distractor_indices(seed=101, n_queries=n_probe,
                                            n_available=N_HELDOUT)
    # Build M_stored (all seen pairs bundled)
    M_stored = _build_stored_memory(seen, R, F)

    preds_per_arm: Dict[str, np.ndarray] = {}
    rng_rand = np.random.default_rng(101 + 7)
    for arm in ARM_NAMES:
        preds = np.empty(n_probe, dtype=np.int64)
        for i in range(n_probe):
            role_q_idx = int(heldout[i, 0])
            filler_true_idx = int(heldout[i, 1])
            dist_pairs = heldout[distractors[i]]  # (K_DIST, 2)
            B_q = build_test_bundle(role_q_idx, filler_true_idx, dist_pairs, R, F)
            if arm == "ARM_HRR_BIND_UNBIND_CLEANUP":
                preds[i] = infer_cleanup(role_q_idx, B_q, R, F, M_stored)
            elif arm == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
                preds[i] = infer_no_cleanup(role_q_idx, B_q, R, F, M_stored)
            elif arm == "ARM_HRR_STORED_BUNDLE_LOOKUP":
                preds[i] = infer_stored_bundle(role_q_idx, B_q, R, F, M_stored)
            elif arm == "ARM_COSINE_ARGMAX_BASELINE":
                preds[i] = infer_cosine_baseline(role_q_idx, B_q, R, F, M_stored)
            elif arm == "ARM_RANDOM_BASELINE":
                preds[i] = infer_random(role_q_idx, B_q, R, F, M_stored, rng_rand)
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
                    f"META_RULE_AF VIOLATION: arms {names[i]!r} and "
                    f"{names[j]!r} bit-identical predictions on smoke batch"
                )


def _selftest_stored_bundle_heldout_isolation() -> None:
    """STORED_BUNDLE by construction cannot retrieve held-out filler_true
    (since M_stored does not contain (role_q, filler_true) binding).
    Verify on a small batch that STORED_BUNDLE recall is near 0."""
    R, F = build_codebooks(seed=53)
    seen, heldout = split_pairs(seed=53)
    M_stored = _build_stored_memory(seen, R, F)
    n_probe = min(50, N_HELDOUT)
    n_hits = 0
    for i in range(n_probe):
        role_q_idx = int(heldout[i, 0])
        filler_true_idx = int(heldout[i, 1])
        filler_hat = unbind(M_stored, R[role_q_idx])
        pred = cosine_argmax(filler_hat, F)
        if pred == filler_true_idx:
            n_hits += 1
    recall = n_hits / float(n_probe)
    if recall > 0.10:
        raise AssertionError(
            f"STORED_BUNDLE recall on held-out probe = {recall:.3f} > 0.10; "
            f"data split leakage suspected (heldout pairs may not be excluded "
            f"from M_stored)."
        )


def _build_stored_memory(seen: np.ndarray, R: np.ndarray,
                         F: np.ndarray) -> np.ndarray:
    """Bundle all seen (role, filler) bindings into one memory vector."""
    vecs = np.empty((seen.shape[0], N_DIM), dtype=np.complex128)
    for i in range(seen.shape[0]):
        vecs[i] = R[int(seen[i, 0])] * F[int(seen[i, 1])]
    return bundle(vecs)


def _run_arm_shortcut(seed: int, arm_name: str, n_queries: int) -> float:
    """Compact per-arm recall for selftests only. Full runner is run_seed."""
    R, F = build_codebooks(seed=seed)
    seen, heldout = split_pairs(seed=seed)
    M_stored = _build_stored_memory(seen, R, F)
    distractors = sample_distractor_indices(seed=seed, n_queries=n_queries,
                                            n_available=N_HELDOUT)
    rng_rand = np.random.default_rng(seed + 7)
    n_hits = 0
    for i in range(n_queries):
        role_q_idx = int(heldout[i, 0])
        filler_true_idx = int(heldout[i, 1])
        dist_pairs = heldout[distractors[i]]
        B_q = build_test_bundle(role_q_idx, filler_true_idx, dist_pairs, R, F)
        if arm_name == "ARM_HRR_BIND_UNBIND_CLEANUP":
            pred = infer_cleanup(role_q_idx, B_q, R, F, M_stored)
        elif arm_name == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
            pred = infer_no_cleanup(role_q_idx, B_q, R, F, M_stored)
        elif arm_name == "ARM_HRR_STORED_BUNDLE_LOOKUP":
            pred = infer_stored_bundle(role_q_idx, B_q, R, F, M_stored)
        elif arm_name == "ARM_COSINE_ARGMAX_BASELINE":
            pred = infer_cosine_baseline(role_q_idx, B_q, R, F, M_stored)
        else:
            pred = infer_random(role_q_idx, B_q, R, F, M_stored, rng_rand)
        if pred == filler_true_idx:
            n_hits += 1
    return n_hits / float(n_queries)


def _instrumentation_selftest() -> None:
    t0 = time.time()
    try:
        _selftest_bind_unbind_roundtrip()
        _selftest_data_split_valid()
        _selftest_cleanup_argmax_correct()
        _selftest_scale_sentinel_8192()
        _selftest_deterministic_seed_invariance()
        _selftest_arms_must_differ()
        _selftest_stored_bundle_heldout_isolation()
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
        f"[selftest] PASS  n_dim={N_DIM}  N_R={N_ROLES}  N_F={N_FILLERS}  "
        f"N_SEEN={N_SEEN}  N_HELDOUT={N_HELDOUT}  K_DIST={K_DISTRACTORS}  "
        f"seeds={SEEDS}  mode={RUN_MODE}  elapsed={elapsed:.2f}s",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# -----------------------------------------------------------------------------
# Per-seed runner
# -----------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            R: np.ndarray, F: np.ndarray,
            heldout: np.ndarray, M_stored: np.ndarray,
            distractors: np.ndarray,
            rng_rand: np.random.Generator) -> Dict:
    t0 = time.time()
    try:
        n_q = heldout.shape[0]
        n_hits = 0
        for i in range(n_q):
            role_q_idx = int(heldout[i, 0])
            filler_true_idx = int(heldout[i, 1])
            dist_pairs = heldout[distractors[i]]
            B_q = build_test_bundle(role_q_idx, filler_true_idx, dist_pairs, R, F)
            if arm_name == "ARM_HRR_BIND_UNBIND_CLEANUP":
                pred = infer_cleanup(role_q_idx, B_q, R, F, M_stored)
            elif arm_name == "ARM_HRR_BIND_UNBIND_NO_CLEANUP":
                pred = infer_no_cleanup(role_q_idx, B_q, R, F, M_stored)
            elif arm_name == "ARM_HRR_STORED_BUNDLE_LOOKUP":
                pred = infer_stored_bundle(role_q_idx, B_q, R, F, M_stored)
            elif arm_name == "ARM_COSINE_ARGMAX_BASELINE":
                pred = infer_cosine_baseline(role_q_idx, B_q, R, F, M_stored)
            elif arm_name == "ARM_RANDOM_BASELINE":
                pred = infer_random(role_q_idx, B_q, R, F, M_stored, rng_rand)
            else:
                raise ValueError(f"unknown arm: {arm_name}")
            if pred == filler_true_idx:
                n_hits += 1
        recall = n_hits / float(n_q)
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_1": float(recall),
            "n_queries": int(n_q),
            "n_dim": int(N_DIM),
            "N_R": int(N_ROLES),
            "N_F": int(N_FILLERS),
            "N_SEEN": int(N_SEEN),
            "N_HELDOUT": int(N_HELDOUT),
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
            "N_R": int(N_ROLES),
            "N_F": int(N_FILLERS),
            "N_SEEN": int(N_SEEN),
            "N_HELDOUT": int(N_HELDOUT),
            "K_DISTRACTORS": int(K_DISTRACTORS),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    R, F = build_codebooks(seed)
    seen, heldout = split_pairs(seed)
    M_stored = _build_stored_memory(seen, R, F)
    distractors = sample_distractor_indices(seed=seed, n_queries=N_HELDOUT,
                                            n_available=N_HELDOUT)
    rng_rand = np.random.default_rng(seed + 7)
    print(f"  [seed={seed}] built codebooks R=({N_ROLES},{N_DIM}) "
          f"F=({N_FILLERS},{N_DIM}); seen={seen.shape[0]} "
          f"heldout={heldout.shape[0]} K_dist={K_DISTRACTORS}",
          flush=True)
    arms = []
    for arm_name in ARM_NAMES:
        out = run_arm(arm_name, seed, R, F, heldout, M_stored,
                      distractors, rng_rand)
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
        "N_R": N_ROLES,
        "N_F": N_FILLERS,
        "N_SEEN": N_SEEN,
        "N_HELDOUT": N_HELDOUT,
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
    stored = mean_per_arm["ARM_HRR_STORED_BUNDLE_LOOKUP"]
    cosine_base = mean_per_arm["ARM_COSINE_ARGMAX_BASELINE"]
    random_base = mean_per_arm["ARM_RANDOM_BASELINE"]

    hp1 = cleanup >= 0.60
    hp2 = (cleanup - no_cleanup) >= 0.10
    hp3 = (cleanup - stored) >= 0.05
    hp4 = (cleanup - cosine_base) >= 0.30

    # HARD_FAIL bands
    if cleanup < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL_HF1: ARM_HRR_BIND_UNBIND_CLEANUP mean recall@1="
                f"{cleanup:.3f} < 0.30; substrate cannot compositionally "
                f"generalize on VSA-native task. "
                f"cleanup={cleanup:.3f} no_cleanup={no_cleanup:.3f} "
                f"stored={stored:.3f} cosine_base={cosine_base:.3f} "
                f"random_base={random_base:.3f}",
                {"cleanup": cleanup, "no_cleanup": no_cleanup,
                 "stored": stored, "cosine_base": cosine_base,
                 "random_base": random_base,
                 "hp1": hp1, "hp2": hp2, "hp3": hp3, "hp4": hp4})

    if stored > cleanup + 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL_stored_beats_mechanism: STORED_BUNDLE={stored:.3f} "
                f"> CLEANUP={cleanup:.3f} + 0.05; stored memory beats "
                f"compositional (would refute generalization claim; likely "
                f"data-split leakage).",
                {"cleanup": cleanup, "no_cleanup": no_cleanup,
                 "stored": stored, "cosine_base": cosine_base,
                 "random_base": random_base,
                 "hp1": hp1, "hp2": hp2, "hp3": hp3, "hp4": hp4})

    summary = (
        f"n_seeds={n_seeds} n_dim={N_DIM} N_R={N_ROLES} N_F={N_FILLERS} "
        f"N_SEEN={N_SEEN} N_HELDOUT={N_HELDOUT} K_DIST={K_DISTRACTORS} | "
        f"CLEANUP={cleanup:.3f}+/-{std_per_arm['ARM_HRR_BIND_UNBIND_CLEANUP']:.3f} "
        f"NO_CLEANUP={no_cleanup:.3f}+/-{std_per_arm['ARM_HRR_BIND_UNBIND_NO_CLEANUP']:.3f} "
        f"STORED={stored:.3f}+/-{std_per_arm['ARM_HRR_STORED_BUNDLE_LOOKUP']:.3f} "
        f"COSINE={cosine_base:.3f} RANDOM={random_base:.3f} | "
        f"HP1(>=0.60)={hp1} "
        f"HP2(cleanup_gain>=0.10)={hp2}(gain={cleanup - no_cleanup:+.3f}) "
        f"HP3(composition>=0.05)={hp3}(gap={cleanup - stored:+.3f}) "
        f"HP4(vs_cosine>=0.30)={hp4}(gap={cleanup - cosine_base:+.3f})"
    )
    gates = {
        "cleanup": cleanup, "no_cleanup": no_cleanup,
        "stored": stored, "cosine_base": cosine_base,
        "random_base": random_base,
        "hp1": hp1, "hp2": hp2, "hp3": hp3, "hp4": hp4,
        "cleanup_minus_no_cleanup": cleanup - no_cleanup,
        "cleanup_minus_stored": cleanup - stored,
        "cleanup_minus_cosine": cleanup - cosine_base,
        "std_per_arm": std_per_arm,
    }

    if hp1 and hp2 and hp3 and hp4:
        return ("HARD_PASS",
                f"HARD_PASS: HP1+HP2+HP3+HP4 all cleared. "
                f"VSA-native mechanism performs compositional generalization "
                f"on held-out role-filler pairs; cleanup earns keep at "
                f"K_DIST=10; test-time composition beats stored memory. "
                f"{summary}",
                gates)

    # MIDDLE_BAND cases
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: HP checks partial "
            f"hp=[hp1={hp1},hp2={hp2},hp3={hp3},hp4={hp4}]. {summary}",
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
        print(f"[seed={seed}] stage2_vsa_cell2_compositional_generalization  "
              f"n_dim={N_DIM} N_R={N_ROLES} N_F={N_FILLERS} "
              f"N_SEEN={N_SEEN} N_HELDOUT={N_HELDOUT} K_DIST={K_DISTRACTORS} "
              f"mode={RUN_MODE}...",
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
        and all(len(r.get("arms", [])) == 5 for r in all_results)
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} n_dim={N_DIM} N_R={N_ROLES} "
            f"N_F={N_FILLERS} N_SEEN={N_SEEN} N_HELDOUT={N_HELDOUT} "
            f"K_DIST={K_DISTRACTORS} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "N_R": N_ROLES,
        "N_F": N_FILLERS,
        "N_SEEN": N_SEEN,
        "N_HELDOUT": N_HELDOUT,
        "K_DISTRACTORS": K_DISTRACTORS,
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
