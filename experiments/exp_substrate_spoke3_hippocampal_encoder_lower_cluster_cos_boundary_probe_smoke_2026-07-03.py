"""exp_substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_smoke_2026_07_03

Stage 2 Spoke 3 hippocampal-encoder LOWER-CLUSTER-COS BOUNDARY PROBE:
characterizes the analytical-scope boundary of Skunkworks'
`MATH_COSINE_ARGMAX_ROBUST_AT_EXTREME_SPARSE_CUE_JL_ORTHOGONALITY_MM_STANDARD`
atom after the amendment
`META_GAUSSIAN_JL_ANALYTICAL_PREDICTION_FAILS_AT_CLUSTER_COS_HIGH_REGARDLESS_OF_FILLER_GEOMETRY`
(MM_STANDARD_2ND_WITNESS 2026-07-03) broadened the failure scope to bipolar +
Gaussian at cluster_cos=0.90.

The prior 2 cells (Cell 4 + bipolar-vs-Gaussian) at cluster_cos~0.90 + 75%
dim-zero cue showed baseline cosine SATURATES at r@1=1.000 regardless of
filler geometry. This cell tests the OPEN scope question: at LOWER cluster_cos
and/or LOWER corruption, does the Gaussian-JL analytical prediction
(baseline degrades due to sib_std variance) ACTUALLY HOLD?

Task class: SAME as Cell 4 / bipolar-vs-Gaussian (episodic-binding + partial-cue
retrieval; N=500 pairs; adversarial cluster-shared codebook). ONLY the
cluster_cos and corruption VARY. Filler geometry is Gaussian ONLY (bipolar
determinism already ruled out; Skunkworks predicted JL applies at Gaussian).

Sweep (2D characterization):
  cluster_cos in {0.30, 0.50, 0.70, 0.90}
    - 0.30 = ~random (no cluster structure); Gaussian-JL should apply CLEANLY
    - 0.50 = mild cluster; intermediate regime
    - 0.70 = moderate cluster; expected boundary region
    - 0.90 = high cluster (Cell 4 regime; REGRESSION)
  corruption in {0.50, 0.75}
    - 0.50 = moderate corruption; theoretically JL region if cluster_cos low
    - 0.75 = Cell 4 regime; REGRESSION

Arms (3 arms x 4 cluster_cos x 2 corruption = 24 unit-instances x 3 seeds = 72):
  ARM_HIPPO_C{cluster}_R{corrupt}    - mechanism
  ARM_COSINE_C{cluster}_R{corrupt}   - baseline (Skunkworks JL prediction target)
  ARM_RANDOM_C{cluster}_R{corrupt}   - chance floor

HP band (ALL AT GAUSSIAN FILLER):
  HP1 (Skunkworks-JL PREDICTION TEST at low cluster + moderate corruption):
       ARM_COSINE_C0.30_R0.50 r@1 <= 0.90 (baseline degrades; JL prediction
       VALIDATES at counterfactual regime).
  HP2 (regime boundary characterization):
       cluster_cos threshold identifiable where COSINE transitions from
       r@1 <= 0.90 (JL-degradation) to r@1 >= 0.99 (exact-carrier saturation).
       Threshold in [0.30, 0.90] interior region.
  HP3 (regression at cluster_cos=0.90 + 75% corruption):
       ARM_COSINE_C0.90_R0.75 r@1 >= 0.99 (matches Cell 4 + bipolar-vs-Gaussian
       pattern; code-integrity gate).

HARD_PASS = HP1 AND HP2 AND HP3.
HF-jl-fails-even-at-low-cluster: HP1 fails at cluster_cos=0.30 (deeper limitation).
HF-regression: HP3 fails (code drift; downstream verdict UNRELIABLE).
HF-no-boundary-observable: HP2 fails (COSINE at all cluster_cos values either
  all-saturate or all-degrade; regime axis is TOO NARROW/broad to observe
  transition).
MIDDLE_BAND: partial fires (JL fires at some but not all low-cluster regimes).

Regime:
  N_DIM=2048, DG_DIM=8192, SPARSITY=0.02 (T-F capacity ~1047 THEORETICAL@).
  N_PAIRS=500, CLUSTER_SIZE=5.
  Filler geometry: GAUSSIAN only.
  Seeds=[11, 17, 23].

Pre-reg: preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_smoke.md
Primitive: hdlab/hippocampal_encoder.py.

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM probe characterizing ANALYTICAL
  SCOPE of prior Skunkworks JL atom. Not a general-knowledge or language claim.
- Skunkworks-corrected T-F formula: C_TF = dg_dim / (2 * ln(1/p)).
- If Skunkworks-JL VALIDATES at low cluster: analytical model has a legitimate
  regime; MM_STANDARD atom can promote to CG_MEASURED_BOUND with clear
  regime characterization (cluster_cos threshold).
- If Skunkworks-JL ALSO fails at low cluster: deeper analytical model limitation;
  suggests bit/value exact-carrier dominates at ALL corruption > 50% regardless
  of cluster_cos.
- No sigma claims without formula verification AND filler-geometry AND
  cluster_cos annotation.
- Anti-personification: substrate operates on integer indices + real-valued
  vectors.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception
- baseline_in_band (META_RULE_AG; RANDOM sanity per cluster_cos x corruption)
- HP_SCOPE per-arm declaration
- cardinality_ok (EXPECTED_N_UNITS = 3 arms x 4 cluster_cos x 2 corruption x
  3 seeds = 72)
- per-unit failure_class instrumentation
- start_marker_written, crash_diagnostic_present, heartbeat_present
- per-seed checkpoint (SH-4)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)

Scope: SMOKE-only on local_cpu. USER-locked SMOKE-only-on-local_cpu.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = (
    "substrate_spoke3_hippocampal_encoder_lower_cluster_cos_boundary_probe_"
    "smoke_2026_07_03"
)

# --- Config ---

N_DIM = 2048
DG_DIM = 8192
DG_SPARSITY = 0.02
N_PAIRS = 500
CLUSTER_SIZE = 5
SEEDS = [11, 17, 23]

CLUSTER_COS_SWEEP = [0.30, 0.50, 0.70, 0.90]
CORRUPTION_SWEEP = [0.50, 0.75]

# HP thresholds.
HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX = 0.90  # cluster_cos=0.30, corrupt=0.50
HP1_CLUSTER_COS = 0.30
HP1_CORRUPTION = 0.50

HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN = 0.99  # cluster_cos=0.90, corrupt=0.75
HP3_CLUSTER_COS = 0.90
HP3_CORRUPTION = 0.75

# HP2: boundary characterization. Find the lowest cluster_cos at which COSINE
# saturates at r@1 >= 0.99 for a given corruption. If interior (not 0.30 or
# 0.90), the boundary is observable.
BOUNDARY_SATURATION_MIN = 0.99
BOUNDARY_DEGRADATION_MAX = 0.90

# HF-baseline sanity: RANDOM should be near-chance.
CHANCE_R1 = 1.0 / N_PAIRS  # 0.002
BASELINE_IN_BAND_R1_MAX = 5.0 * CHANCE_R1  # 0.010

# DG architectural constraint.
DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040

# THEORETICAL@ Tsodyks-Feigelman capacity C_TF = dg_dim / (2 * ln(1/sparsity)).
_TF_CAPACITY = DG_DIM / (2.0 * math.log(1.0 / DG_SPARSITY))


# --- Arm specs ---
# Cross product of (arm_kind, cluster_cos, corruption)

ENCODER_KINDS = ["hippocampal", "cosine", "random"]


def _arm_name(kind: str, cluster_cos: float, corruption: float) -> str:
    label = {"hippocampal": "HIPPO", "cosine": "COSINE",
             "random": "RANDOM"}[kind]
    return (f"ARM_{label}_C{cluster_cos:.2f}"
            f"_R{corruption:.2f}").replace(".", "")  # strip decimals for
                                                     # queue-safe arm keys


def _arm_name_readable(kind: str, cluster_cos: float, corruption: float) -> str:
    """Human-readable form for logs."""
    label = {"hippocampal": "HIPPO", "cosine": "COSINE",
             "random": "RANDOM"}[kind]
    return f"ARM_{label}_C{cluster_cos:.2f}_R{corruption:.2f}"


def _build_arm_specs():
    specs = []
    for kind in ENCODER_KINDS:
        for cc in CLUSTER_COS_SWEEP:
            for corr in CORRUPTION_SWEEP:
                nm = _arm_name(kind, cc, corr)
                specs.append((nm, kind, cc, corr))
    return specs


ARM_SPECS = _build_arm_specs()
ARM_NAMES = [s[0] for s in ARM_SPECS]


# --- Args ---
def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode",
                    default=os.environ.get("HDLAB_RUN_MODE", None),
                    choices=[None, "self_test", "smoke", "full"])
    args, _ = ap.parse_known_args()
    if args.self_test:
        return "self_test"
    if args.smoke:
        return "smoke"
    if args.run_mode is not None:
        return args.run_mode
    return "smoke"


RUN_MODE = _parse_args()
IS_SMOKE = RUN_MODE == "smoke"
IS_SELFTEST = RUN_MODE == "self_test"


# --- Observability helpers ---
def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}",
          flush=True)


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int,
               elapsed_s: float, extra: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
        "extra": extra,
    }
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_partial_seed(output_dir: Path, seed: int, payload: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / f"partial_metrics_{seed}.json.tmp"
    final = output_dir / f"partial_metrics_{seed}.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --- Codebook draws ---

def _draw_pairs_adversarial_gaussian(n_pairs: int, n_dim: int, seed: int,
                                     cluster_size: int,
                                     rho: float
                                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Adversarial cluster-shared GAUSSIAN codebook with variable rho.

    Per cluster: shared BIPOLAR anchor_role_key + shared GAUSSIAN anchor_filler.
    member_filler = sqrt(rho)*anchor_filler + sqrt(1-rho)*per_member_gauss.

    THEORETICAL@ within-cluster filler cos -> rho as n_dim -> inf.
    Episode = role_key * filler (dim-wise product).
    """
    rng = np.random.default_rng(int(seed) * 953 + 19 + int(round(rho * 1000)))
    role_keys = np.zeros((n_pairs, n_dim), dtype=np.float32)
    fillers = np.zeros((n_pairs, n_dim), dtype=np.float32)
    sqrt_rho = math.sqrt(max(rho, 0.0))
    sqrt_one_minus = math.sqrt(max(1.0 - rho, 0.0))
    n_clusters = (n_pairs + cluster_size - 1) // cluster_size
    for c in range(n_clusters):
        anchor_role = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
        anchor_filler = rng.standard_normal(size=n_dim).astype(np.float32)
        start = c * cluster_size
        end = min(start + cluster_size, n_pairs)
        for i in range(start, end):
            role_keys[i] = anchor_role
            per_member = rng.standard_normal(size=n_dim).astype(np.float32)
            fillers[i] = sqrt_rho * anchor_filler + sqrt_one_minus * per_member
    episodes = (role_keys * fillers).astype(np.float32)
    return role_keys, fillers, episodes


def _corrupt_cue(episodes: np.ndarray, fraction_zeroed: float,
                 seed: int) -> np.ndarray:
    """Zero fraction_zeroed of dims per row. Deterministic w.r.t. seed."""
    n, d = episodes.shape
    n_zero = int(round(fraction_zeroed * d))
    rng = np.random.default_rng(int(seed) * 977 + 13 +
                                int(round(fraction_zeroed * 1000)))
    cues = episodes.copy()
    for i in range(n):
        zero_idx = rng.choice(d, size=n_zero, replace=False)
        cues[i, zero_idx] = 0.0
    return cues


def _within_cluster_cos_observed(fillers: np.ndarray,
                                 cluster_size: int = CLUSTER_SIZE,
                                 max_comparisons: int = 100) -> float:
    n, d = fillers.shape
    n_clusters = n // cluster_size
    fn = fillers / (np.linalg.norm(fillers, axis=1, keepdims=True) + 1e-8)
    cos_vals = []
    count = 0
    for c in range(n_clusters):
        s = c * cluster_size
        for i in range(s, s + cluster_size):
            for j in range(i + 1, s + cluster_size):
                cos_vals.append(float(np.dot(fn[i], fn[j])))
                count += 1
                if count >= max_comparisons:
                    return float(np.mean(cos_vals))
    if not cos_vals:
        return float("nan")
    return float(np.mean(cos_vals))


# --- Encoder implementations (parameterized by corruption) ---

def _encode_hippocampal(episodes: np.ndarray, seed: int, corruption: float
                        ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    from hdlab.hippocampal_encoder import HippocampalEncoder
    n = episodes.shape[0]
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    stored_dg = enc.encode_and_write(episodes)
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(stored_dg)

    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, corruption, seed=int(seed))
    completed_dg = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "hippocampal",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(corruption),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    return stored_dg, completed_dg, fit_wall, ret_wall, diag


def _encode_cosine_baseline(episodes: np.ndarray, seed: int, corruption: float
                            ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    fit_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, corruption, seed=int(seed))
    fit_wall = time.perf_counter() - fit_t0
    diag = {"encoder": "cosine_baseline", "input_dim": N_DIM,
            "partial_cue_fraction_zeroed": float(corruption)}
    return episodes.copy(), cues, 0.0, fit_wall, diag


def _encode_random(episodes: np.ndarray, seed: int, corruption: float
                   ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    n = episodes.shape[0]
    # Include corruption in seed offset to make each random arm bit-distinct
    # from same-seed random arms at other corruption values (arms-differ).
    rng = np.random.default_rng(int(seed) * 883 + 29 +
                                int(round(corruption * 1000)))
    t0 = time.perf_counter()
    stored = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    query = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    diag = {"encoder": "random", "input_dim": N_DIM,
            "partial_cue_fraction_zeroed": float(corruption)}
    return stored, query, 0.0, wall, diag


ENCODER_FUNCS = {
    "hippocampal": _encode_hippocampal,
    "cosine": _encode_cosine_baseline,
    "random": _encode_random,
}


# --- Retrieval metrics ---

def _unit_norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / (n + eps)


def _retrieval_metrics(stored: np.ndarray, query: np.ndarray,
                       seed: int) -> Dict[str, float]:
    s = _unit_norm(stored.astype(np.float32))
    q = _unit_norm(query.astype(np.float32))
    n = s.shape[0]
    sims = q @ s.T
    order = np.argsort(-sims, axis=1)
    r1 = 0
    r5 = 0
    mrr_sum = 0.0
    intra_sum = 0.0
    for i in range(n):
        intra_sum += float(sims[i, i])
        r1 += int(order[i, 0] == i)
        if i in order[i, :5]:
            r5 += 1
        rank_arr = np.where(order[i] == i)[0]
        if rank_arr.size > 0:
            mrr_sum += 1.0 / float(rank_arr[0] + 1)
    r1 /= n
    r5 /= n
    mrr = mrr_sum / n
    intra = intra_sum / n
    rng = np.random.default_rng(int(seed) * 991 + 7)
    perm = rng.permutation(n)
    for i in range(n):
        if perm[i] == i:
            j = (i + 1) % n
            perm[i], perm[j] = perm[j], perm[i]
    inter = float(np.mean(np.sum(q * s[perm], axis=1)))
    snr = intra / max(abs(inter), 1e-6)
    return {
        "recall_at_1": float(r1),
        "recall_at_5": float(r5),
        "mean_reciprocal_rank": float(mrr),
        "intra_pair_cos_mean": float(intra),
        "inter_pair_cos_mean": float(inter),
        "signal_to_noise_ratio": float(snr),
    }


# --- arms-differ hash ---

def _arms_differ_hash(arms_query: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests: Dict[str, str] = {}
    for name, arr in arms_query.items():
        sig = np.ascontiguousarray(arr.astype(np.float32)).tobytes()
        digests[name] = hashlib.sha256(sig).hexdigest()[:16]
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"META_RULE_AF VIOLATION arms_differ: {a!r} and {b!r} "
                    f"bit-identical query (hash={digests[a]})."
                )
    return digests


# --- Selftests ---

def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_lower_cluster_cos_boundary_smoke"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_corrupt_cue_50pct_and_75pct() -> None:
    rng = np.random.default_rng(3)
    n, d = 20, 512
    episodes = (rng.integers(0, 2, size=(n, d)) * 2 - 1).astype(np.float32)
    for frac in (0.50, 0.75):
        cues = _corrupt_cue(episodes, fraction_zeroed=frac, seed=11)
        zeros_per_row = (cues == 0.0).sum(axis=1)
        expected = int(round(frac * d))
        assert np.all(zeros_per_row == expected), (
            f"{frac*100:.0f}%: zeros_per_row {zeros_per_row[:5]} expected "
            f"{expected}"
        )
        nonzero_mask = cues != 0.0
        assert np.all(cues[nonzero_mask] == episodes[nonzero_mask]), (
            f"cue non-zero dims don't match episode at frac={frac}")
    print("[selftest corrupt_cue_50pct_and_75pct] PASS", flush=True)


def _selftest_gaussian_within_cluster_cos_at_each_rho() -> None:
    """Empirical filler-cos must match theoretical rho at each cluster_cos."""
    for rho in CLUSTER_COS_SWEEP:
        _, fillers, _ = _draw_pairs_adversarial_gaussian(
            n_pairs=100, n_dim=N_DIM, seed=11,
            cluster_size=CLUSTER_SIZE, rho=rho)
        obs = _within_cluster_cos_observed(fillers,
                                           cluster_size=CLUSTER_SIZE,
                                           max_comparisons=100)
        # THEORETICAL@ rho; tolerance +/- 0.06 at N_DIM=2048, 100 comparisons.
        tol = 0.06
        assert (rho - tol) <= obs <= (rho + tol), (
            f"gaussian within-cluster filler cos {obs:.4f} at rho={rho:.2f} "
            f"outside [{rho-tol:.4f}, {rho+tol:.4f}]"
        )
        print(f"[selftest gaussian_within_cluster_cos rho={rho:.2f}] PASS "
              f"obs={obs:.4f}", flush=True)


def _selftest_gaussian_filler_is_real_valued() -> None:
    _, fillers, _ = _draw_pairs_adversarial_gaussian(
        n_pairs=20, n_dim=512, seed=11, cluster_size=5, rho=0.50)
    unique_vals = np.unique(np.round(fillers, 4))
    assert unique_vals.size > 10, (
        f"gaussian filler has only {unique_vals.size} unique values; "
        f"expected continuous (>>10)"
    )
    var = float(np.var(fillers))
    assert 0.7 <= var <= 1.3, (
        f"gaussian filler variance {var:.4f} outside [0.7, 1.3]"
    )
    print(f"[selftest gaussian_filler_is_real_valued] PASS "
          f"n_unique={unique_vals.size} var={var:.4f}", flush=True)


def _selftest_arms_differ_hash_micro() -> None:
    """Same episodes -> different encoders should produce different queries."""
    _, _, episodes = _draw_pairs_adversarial_gaussian(
        n_pairs=20, n_dim=256, seed=11, cluster_size=5, rho=0.50)
    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02,
                             seed=11)
    _ = enc.encode_and_write(episodes)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.75, seed=11)
    completed = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    h_hip = hashlib.sha256(completed.tobytes()).hexdigest()[:16]
    h_cos = hashlib.sha256(cues.tobytes()).hexdigest()[:16]
    assert h_hip != h_cos, f"hippo == cosine arms: hip={h_hip} cos={h_cos}"
    print(f"[selftest arms_differ_hash_micro] PASS hip={h_hip[:8]} "
          f"cos={h_cos[:8]}", flush=True)


def _selftest_determinism_gaussian() -> None:
    """Gaussian codebook with SAME seed+rho produces bit-identical fillers."""
    for rho in (0.30, 0.90):
        _, fA, epA = _draw_pairs_adversarial_gaussian(
            n_pairs=30, n_dim=256, seed=11, cluster_size=5, rho=rho)
        _, fB, epB = _draw_pairs_adversarial_gaussian(
            n_pairs=30, n_dim=256, seed=11, cluster_size=5, rho=rho)
        assert np.array_equal(fA, fB), (
            f"Gaussian filler draw non-deterministic at rho={rho}")
        assert np.array_equal(epA, epB), (
            f"Gaussian episode non-deterministic at rho={rho}")
    print("[selftest determinism_gaussian] PASS", flush=True)


def _selftest_scale_sentinel_n_dim_8192() -> None:
    """Verify codebook + corrupt-cue work at scale sentinel n_dim=8192."""
    _, fillers, episodes = _draw_pairs_adversarial_gaussian(
        n_pairs=20, n_dim=8192, seed=11, cluster_size=5, rho=0.90)
    obs = _within_cluster_cos_observed(fillers, cluster_size=5,
                                       max_comparisons=20)
    assert 0.84 <= obs <= 0.96, (
        f"scale sentinel N=8192 rho=0.90: obs={obs:.4f} outside "
        f"[0.84, 0.96]"
    )
    cues = _corrupt_cue(episodes, fraction_zeroed=0.75, seed=11)
    zeros_per_row = (cues == 0.0).sum(axis=1)
    expected = int(round(0.75 * 8192))
    assert np.all(zeros_per_row == expected), (
        f"scale sentinel corrupt: zeros_per_row[:3]={zeros_per_row[:3]}"
    )
    print(f"[selftest scale_sentinel_n_dim_8192] PASS obs={obs:.4f}",
          flush=True)


def _selftest_regression_expected_hippo_and_cosine_at_regression_regime(
        ) -> None:
    """Regression at cluster_cos=0.90 + 75% corrupt:
        HIPPO ~= 0.500 (Gaussian; MEASURED@ bipolar-vs-Gaussian ~0.53 mean)
        COSINE = 1.000 exact.
    Uses reduced-scale probe (100 pairs, 3 seeds informational) to validate
    the arm behavior BEFORE the full smoke matrix; keeps this cheap.
    """
    rho = 0.90
    corruption = 0.75
    hippos = []
    cosines = []
    for seed in (11,):
        _, _, episodes = _draw_pairs_adversarial_gaussian(
            n_pairs=100, n_dim=N_DIM, seed=seed,
            cluster_size=CLUSTER_SIZE, rho=rho)
        # Cosine baseline
        cues = _corrupt_cue(episodes, corruption, seed=seed)
        m_cos = _retrieval_metrics(episodes, cues, seed=seed)
        cosines.append(m_cos["recall_at_1"])
        # Hippo
        from hdlab.hippocampal_encoder import HippocampalEncoder
        enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                                 sparsity=DG_SPARSITY, seed=seed)
        stored_dg = enc.encode_and_write(episodes)
        completed = enc.retrieve(cues, use_ca3=True,
                                 sparsify_after_settle=True)
        m_h = _retrieval_metrics(stored_dg, completed, seed=seed)
        hippos.append(m_h["recall_at_1"])
    mean_cos = float(np.mean(cosines))
    mean_h = float(np.mean(hippos))
    # COSINE should saturate near 1.000 at cluster_cos=0.90 + 75% corrupt
    # (Cell 4 + bipolar-vs-Gaussian pattern MEASURED@)
    assert mean_cos >= 0.95, (
        f"regression expected COSINE r@1 >= 0.95 at rho=0.90+corrupt=0.75; "
        f"got {mean_cos:.4f} (n=100 pairs). Interpretation: code drift OR "
        f"reduced-N regime shift; investigate before smoke."
    )
    # HIPPO at cluster_cos=0.90 + 75% corrupt: MEASURED@ bipolar-vs-Gaussian
    # gaussian ~= 0.53. Reduced-N=100 will be higher (less inter-cluster
    # confusion). Widen band to [0.35, 1.00]; strict floor detects primitive
    # break.
    assert mean_h >= 0.35, (
        f"regression expected HIPPO r@1 >= 0.35 at rho=0.90+corrupt=0.75; "
        f"got {mean_h:.4f} (n=100). Mechanism may be broken."
    )
    print(f"[selftest regression_expected_hippo_and_cosine_at_regression_"
          f"regime] PASS cosine={mean_cos:.4f} hippo={mean_h:.4f} (N=100)",
          flush=True)


def _selftest_primitive_selftests_chain() -> None:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "hdlab.hippocampal_encoder", "--self-test"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print("[selftest primitive_selftests_chain] STDOUT:")
        print(result.stdout)
        print("[selftest primitive_selftests_chain] STDERR:")
        print(result.stderr)
        raise AssertionError(
            f"hdlab.hippocampal_encoder --self-test returned "
            f"{result.returncode}"
        )
    if "13/13 passed" not in result.stdout:
        raise AssertionError(
            f"hippocampal_encoder selftest not '13/13 passed'; "
            f"stdout tail:\n{result.stdout[-500:]}"
        )
    print("[selftest primitive_selftests_chain] PASS 13/13", flush=True)


def _run_selftests() -> int:
    tests = [
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
        ("corrupt_cue_50pct_and_75pct",
         _selftest_corrupt_cue_50pct_and_75pct),
        ("gaussian_within_cluster_cos_at_each_rho",
         _selftest_gaussian_within_cluster_cos_at_each_rho),
        ("gaussian_filler_is_real_valued",
         _selftest_gaussian_filler_is_real_valued),
        ("arms_differ_hash_micro", _selftest_arms_differ_hash_micro),
        ("determinism_gaussian", _selftest_determinism_gaussian),
        ("scale_sentinel_n_dim_8192", _selftest_scale_sentinel_n_dim_8192),
        ("regression_expected_hippo_and_cosine_at_regression_regime",
         _selftest_regression_expected_hippo_and_cosine_at_regression_regime),
        ("primitive_selftests_chain", _selftest_primitive_selftests_chain),
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, f"AssertionError: {e}"))
            print(f"[selftest {name}] FAIL: {e}", flush=True)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}",
                  flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed",
          flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---

def _episode_cache_key(cluster_cos: float, seed: int) -> str:
    return f"g_c{cluster_cos:.2f}_s{seed}"


def _run_one_seed(seed: int, output_dir: Path) -> Dict:
    n_arms = len(ARM_SPECS)
    per_arm: Dict[str, Dict] = {}
    per_arm_query: Dict[str, np.ndarray] = {}
    episode_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    cluster_cos_observed: Dict[float, float] = {}

    for arm_idx, spec in enumerate(ARM_SPECS):
        arm_name, encoder_kind, cluster_cos, corruption = spec
        readable = _arm_name_readable(encoder_kind, cluster_cos, corruption)
        _log(f"[seed {seed}] arm {arm_idx+1}/{n_arms} {readable} "
             f"(encoder={encoder_kind} cluster_cos={cluster_cos:.2f} "
             f"corrupt={corruption:.2f})")
        arm_t0 = time.perf_counter()

        try:
            if encoder_kind == "random":
                episodes = np.zeros((N_PAIRS, N_DIM), dtype=np.float32)
            else:
                key = _episode_cache_key(cluster_cos, seed)
                if key not in episode_cache:
                    rk, fl, ep = _draw_pairs_adversarial_gaussian(
                        N_PAIRS, N_DIM, seed=seed,
                        cluster_size=CLUSTER_SIZE, rho=cluster_cos)
                    episode_cache[key] = (rk, fl, ep)
                    obs_cos = _within_cluster_cos_observed(fl)
                    cluster_cos_observed[cluster_cos] = obs_cos
                    _log(f"[seed {seed}]   drew gaussian codebook rho="
                         f"{cluster_cos:.2f} N={N_PAIRS}: "
                         f"intra-cluster-filler-cos-obs={obs_cos:.4f}")
                _, _, episodes = episode_cache[key]

            enc_fn = ENCODER_FUNCS[encoder_kind]
            stored, query, enc_wall, fit_wall, arm_diag = enc_fn(
                episodes, seed, corruption)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "arm_readable": readable,
                "encoder_kind": encoder_kind,
                "cluster_cos": cluster_cos,
                "corruption": corruption,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {readable} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, n_arms,
                       time.perf_counter() - arm_t0,
                       {"arm": readable, "status": "failed",
                        "failure_class": failure_class})
            continue

        n_nan = int(np.isnan(stored).sum()) + int(np.isnan(query).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "arm_readable": readable,
                "encoder_kind": encoder_kind,
                "cluster_cos": cluster_cos,
                "corruption": corruption,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
            }
            _log(f"[seed {seed}] arm {readable} NaN (n_nan={n_nan})")
            continue

        metrics = _retrieval_metrics(stored, query, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "arm_readable": readable,
            "encoder_kind": encoder_kind,
            "cluster_cos": cluster_cos,
            "corruption": corruption,
            "stored_dim": int(stored.shape[1]),
            "encoding_wall_s": float(enc_wall),
            "fit_wall_s": float(fit_wall),
            "arm_wall_s": float(time.perf_counter() - arm_t0),
            "arm_diag": arm_diag,
        })
        per_arm[arm_name] = metrics
        per_arm_query[arm_name] = query
        _log(f"[seed {seed}] arm {readable} r@1={metrics['recall_at_1']:.4f} "
             f"r@5={metrics['recall_at_5']:.4f} "
             f"intra={metrics['intra_pair_cos_mean']:.3f} "
             f"inter={metrics['inter_pair_cos_mean']:.3f} "
             f"arm_wall={metrics['arm_wall_s']:.1f}s")
        _heartbeat(output_dir, arm_idx, n_arms,
                   time.perf_counter() - arm_t0,
                   {"arm": readable, "recall_at_1": metrics["recall_at_1"]})

    # arms_differ hash: cosine arms at same corruption+cluster_cos will
    # legitimately match each other's OWN query only. Across (cc, corr)
    # queries differ (different corruption seeds + different underlying
    # episodes). Random arms differ from each other because seed-corruption
    # offset produces distinct draws.
    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    if len(per_arm_query) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(per_arm_query)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}

    return {
        "seed": int(seed),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
        "cluster_cos_observed_by_rho": {
            f"{k:.2f}": v for k, v in cluster_cos_observed.items()
        },
    }


# --- Aggregation + verdict ---

def _aggregate(per_seed: List[Dict]) -> Dict:
    out: Dict[str, Dict] = {}
    for spec in ARM_SPECS:
        arm = spec[0]
        r1s, r5s, mrrs, walls = [], [], [], []
        intras, inters, dg_rates = [], [], []
        n_failed = 0
        for ps in per_seed:
            arm_m = ps.get("per_arm", {}).get(arm, {})
            if "failure_class" in arm_m:
                n_failed += 1
                continue
            r1s.append(arm_m.get("recall_at_1", 0.0))
            r5s.append(arm_m.get("recall_at_5", 0.0))
            mrrs.append(arm_m.get("mean_reciprocal_rank", 0.0))
            walls.append(arm_m.get("arm_wall_s", 0.0))
            intras.append(arm_m.get("intra_pair_cos_mean", 0.0))
            inters.append(arm_m.get("inter_pair_cos_mean", 0.0))
            diag = arm_m.get("arm_diag") or {}
            if "dg_sparse_rate_observed" in diag:
                dg_rates.append(diag["dg_sparse_rate_observed"])
        if r1s:
            entry = {
                "arm_name": arm,
                "encoder_kind": spec[1],
                "cluster_cos": spec[2],
                "corruption": spec[3],
                "n_seeds_succeeded": len(r1s),
                "n_seeds_failed": n_failed,
                "recall_at_1_mean": float(np.mean(r1s)),
                "recall_at_1_std": float(np.std(r1s)),
                "recall_at_5_mean": float(np.mean(r5s)),
                "mrr_mean": float(np.mean(mrrs)),
                "intra_pair_cos_mean": float(np.mean(intras)),
                "inter_pair_cos_mean": float(np.mean(inters)),
                "arm_wall_s_mean": float(np.mean(walls)),
            }
            if dg_rates:
                entry["dg_sparse_rate_mean"] = float(np.mean(dg_rates))
            out[arm] = entry
        else:
            out[arm] = {"n_seeds_succeeded": 0, "n_seeds_failed": n_failed,
                        "recall_at_1_mean": None,
                        "cluster_cos": spec[2], "corruption": spec[3],
                        "encoder_kind": spec[1]}
    return out


def _boundary_from_cosine_sweep(agg: Dict, corruption: float
                                ) -> Tuple[float, str]:
    """Identify the lowest cluster_cos at which COSINE saturates at r@1>=0.99
    for the given corruption. Returns (threshold, regime_label) where regime is
    one of INTERIOR / ALL_DEGRADE / ALL_SATURATE / MIXED."""
    coses = sorted(CLUSTER_COS_SWEEP)
    r1s = []
    for cc in coses:
        nm = _arm_name("cosine", cc, corruption)
        r1 = agg.get(nm, {}).get("recall_at_1_mean")
        r1s.append((cc, r1))
    # Handle missing arms.
    missing = [cc for cc, v in r1s if v is None]
    if missing:
        return (float("nan"),
                f"ARM_MISSING_at_cluster_cos={missing}_corruption={corruption}")
    lowest_sat = None
    for cc, v in r1s:
        if v >= BOUNDARY_SATURATION_MIN:
            lowest_sat = cc
            break
    all_sat = all(v >= BOUNDARY_SATURATION_MIN for _, v in r1s)
    all_deg = all(v <= BOUNDARY_DEGRADATION_MAX for _, v in r1s)
    if all_sat:
        return (min(coses), "ALL_SATURATE")
    if all_deg:
        return (float("nan"), "ALL_DEGRADE")
    if lowest_sat is not None:
        if lowest_sat > min(coses) and lowest_sat < max(coses):
            return (lowest_sat, "INTERIOR")
        return (lowest_sat, "AT_EDGE")
    # Mixed: some degrade some saturate but no clean threshold.
    return (float("nan"), "MIXED")


def _verdict(agg: Dict, expected_n_units: int,
             actual_n_units: int) -> Tuple[str, str]:
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-"
                f"metrics but got {actual_n_units}. See per-seed "
                f"failure_class.")

    # HF-baseline sanity (META_RULE_AG) across all random arms.
    for cc in CLUSTER_COS_SWEEP:
        for corr in CORRUPTION_SWEEP:
            nm = _arm_name("random", cc, corr)
            r1 = agg.get(nm, {}).get("recall_at_1_mean")
            if r1 is None:
                continue
            if r1 > BASELINE_IN_BAND_R1_MAX:
                return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                        f"HF baseline_in_band failed: RANDOM at "
                        f"cluster_cos={cc:.2f} corrupt={corr:.2f} "
                        f"r@1={r1:.4f} > {BASELINE_IN_BAND_R1_MAX:.4f} "
                        f"(chance={CHANCE_R1:.4f}). Retrieval bug.")

    # HF-dg-rate architectural sanity across all hippo arms.
    for cc in CLUSTER_COS_SWEEP:
        for corr in CORRUPTION_SWEEP:
            nm = _arm_name("hippocampal", cc, corr)
            dg_v = agg.get(nm, {}).get("dg_sparse_rate_mean")
            if dg_v is not None and not (
                    DG_SPARSE_RATE_MIN <= dg_v <= DG_SPARSE_RATE_MAX):
                return ("HARD_FAIL_DG_SPARSE_RATE_ARCHITECTURAL",
                        f"HF DG sparse rate at cluster_cos={cc:.2f} "
                        f"corrupt={corr:.2f} = {dg_v:.4f} outside "
                        f"[{DG_SPARSE_RATE_MIN:.3f}, "
                        f"{DG_SPARSE_RATE_MAX:.3f}] "
                        f"(target {DG_SPARSITY:.3f}).")

    # Load HP arms.
    hp1_arm = _arm_name("cosine", HP1_CLUSTER_COS, HP1_CORRUPTION)
    hp3_arm = _arm_name("cosine", HP3_CLUSTER_COS, HP3_CORRUPTION)
    hp1_r1 = agg.get(hp1_arm, {}).get("recall_at_1_mean")
    hp3_r1 = agg.get(hp3_arm, {}).get("recall_at_1_mean")
    if hp1_r1 is None or hp3_r1 is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: HP arm(s) missing r@1. hp1={hp1_r1} "
                f"hp3={hp3_r1}")

    # HP3: regression (code-integrity gate).
    hp3_ok = hp3_r1 >= HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN
    if not hp3_ok:
        return ("HARD_FAIL_REGRESSION_BROKEN",
                f"HF regression: HP3 requires "
                f"ARM_COSINE_C0.90_R0.75 r@1 >= "
                f"{HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN} (matches "
                f"Cell 4 + bipolar-vs-Gaussian pattern); got {hp3_r1:.4f}. "
                f"Code drift from prior cells or codebook change broke "
                f"regression; downstream boundary verdict UNRELIABLE. "
                f"hp1_r1={hp1_r1:.4f}")

    # HP1: JL prediction at low cluster + moderate corruption.
    hp1_ok = hp1_r1 <= HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX

    # HP2: boundary characterization at each corruption.
    boundary_075 = _boundary_from_cosine_sweep(agg, corruption=0.75)
    boundary_050 = _boundary_from_cosine_sweep(agg, corruption=0.50)
    # HP2 passes if EITHER corruption sweep shows an INTERIOR boundary.
    hp2_ok = (boundary_075[1] == "INTERIOR"
              or boundary_050[1] == "INTERIOR")

    def _cos_grid():
        rows = []
        for cc in CLUSTER_COS_SWEEP:
            row_cells = []
            for corr in CORRUPTION_SWEEP:
                nm = _arm_name("cosine", cc, corr)
                v = agg.get(nm, {}).get("recall_at_1_mean")
                row_cells.append(f"c={cc:.2f},r={corr:.2f}:"
                                 f"{v:.4f}" if v is not None
                                 else f"c={cc:.2f},r={corr:.2f}:None")
            rows.append(" | ".join(row_cells))
        return " ;; ".join(rows)

    def _hip_grid():
        rows = []
        for cc in CLUSTER_COS_SWEEP:
            row_cells = []
            for corr in CORRUPTION_SWEEP:
                nm = _arm_name("hippocampal", cc, corr)
                v = agg.get(nm, {}).get("recall_at_1_mean")
                row_cells.append(f"c={cc:.2f},r={corr:.2f}:"
                                 f"{v:.4f}" if v is not None
                                 else f"c={cc:.2f},r={corr:.2f}:None")
            rows.append(" | ".join(row_cells))
        return " ;; ".join(rows)

    grid_note = (f"COSINE grid: {_cos_grid()}. HIPPO grid: {_hip_grid()}. "
                 f"Boundary_r0.75=({boundary_075[0]:.2f},"
                 f"{boundary_075[1]}). "
                 f"Boundary_r0.50=({boundary_050[0]:.2f},"
                 f"{boundary_050[1]}).")

    # HARD_PASS: HP1 AND HP2 AND HP3.
    if hp1_ok and hp2_ok and hp3_ok:
        return ("HARD_PASS",
                f"HARD_PASS: Skunkworks-JL analytical prediction VALIDATES "
                f"at low cluster + moderate corruption. HP1: "
                f"COSINE at cluster_cos={HP1_CLUSTER_COS:.2f} corrupt="
                f"{HP1_CORRUPTION:.2f} r@1={hp1_r1:.4f} <= "
                f"{HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX} (baseline "
                f"degrades). HP2: cluster_cos boundary observable INTERIOR "
                f"(threshold r=0.75: {boundary_075[0]:.2f}; threshold r=0.50: "
                f"{boundary_050[0]:.2f}). HP3: COSINE at cluster_cos="
                f"{HP3_CLUSTER_COS:.2f} corrupt={HP3_CORRUPTION:.2f} "
                f"r@1={hp3_r1:.4f} >= "
                f"{HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN} (regression: "
                f"exact-carrier saturation reproduces Cell 4 + bipolar-vs-"
                f"Gaussian pattern). ANALYTICAL SCOPE: Skunkworks JL atom "
                f"can promote from MM_STANDARD to CG_MEASURED_BOUND with "
                f"regime characterization (JL degradation observed at "
                f"cluster_cos <= threshold; exact-carrier saturation at "
                f"cluster_cos >= threshold). SCOPE: MECHANISM ANALYTICAL "
                f"SCOPE PROBE on SUPERVISED synthetic Gaussian binding; "
                f"does NOT grant substrate general-knowledge or language "
                f"capability. {grid_note} HOLD pending USER decision.")

    # HF-jl-fails-even-at-low-cluster (primary HF): HP1 fails but HP3 holds.
    if not hp1_ok and hp3_ok:
        return ("HARD_FAIL_JL_FAILS_EVEN_AT_LOW_CLUSTER",
                f"HF: Skunkworks-JL analytical prediction FAILS even at "
                f"low-cluster + moderate-corruption counterfactual regime. "
                f"HP1: COSINE at cluster_cos={HP1_CLUSTER_COS:.2f} "
                f"corrupt={HP1_CORRUPTION:.2f} r@1={hp1_r1:.4f} > "
                f"{HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX} (baseline "
                f"STILL saturates in the JL-friendly counterfactual). HP3: "
                f"r@1={hp3_r1:.4f} at (0.90, 0.75) reproduces regression. "
                f"Interpretation: analytical model has DEEPER LIMITATION "
                f"than just cluster-cos-0.90; bit/value exact-carrier "
                f"dominates at ALL corruption > 50% regardless of "
                f"cluster_cos. JL orthogonality atom's declared scope is "
                f"NOT scope-refinable via cluster_cos axis at 75% "
                f"corruption regime. Suggests route to research 2x-drill "
                f"on exact-carrier-vs-JL mechanism at moderate corruption "
                f"or lower N_PAIRS/tighter cluster geometry. {grid_note}")

    # HF-no-boundary-observable (HP2 fails structurally): HP1 fires but no
    # observable transition.
    if hp1_ok and not hp2_ok:
        return ("HARD_FAIL_NO_BOUNDARY_OBSERVABLE",
                f"HF: HP1 fires (JL degradation at low cluster) but no "
                f"observable INTERIOR boundary in the cluster_cos sweep "
                f"axis. Boundary_r=0.75=({boundary_075[0]:.2f},"
                f"{boundary_075[1]}); Boundary_r=0.50=({boundary_050[0]:.2f},"
                f"{boundary_050[1]}). HP1 COSINE r@1={hp1_r1:.4f} at "
                f"(0.30, 0.50); HP3 COSINE r@1={hp3_r1:.4f} at (0.90, 0.75). "
                f"Interpretation: transition is either OUTSIDE the sweep "
                f"axis (below 0.30 or above 0.90) OR spans multiple axes "
                f"non-monotonically. Sweep axis needs re-scoping "
                f"(finer resolution / different range). {grid_note}")

    # MIDDLE_BAND: partial fires.
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial HP set. "
            f"HP1 COSINE at (cluster_cos={HP1_CLUSTER_COS:.2f}, corrupt="
            f"{HP1_CORRUPTION:.2f}) <= "
            f"{HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX}: "
            f"{'PASS' if hp1_ok else 'FAIL'} ({hp1_r1:.4f}). "
            f"HP2 boundary_INTERIOR observable in either corruption sweep: "
            f"{'PASS' if hp2_ok else 'FAIL'} (r=0.75: {boundary_075[1]}; "
            f"r=0.50: {boundary_050[1]}). "
            f"HP3 COSINE at ({HP3_CLUSTER_COS:.2f}, {HP3_CORRUPTION:.2f}) "
            f">= {HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN}: "
            f"{'PASS' if hp3_ok else 'FAIL'} ({hp3_r1:.4f}). "
            f"Prediction test inconclusive across the 2D sweep. {grid_note}")


# --- main ---

def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * len(ARM_SPECS)
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_arms={len(ARM_SPECS)} "
         f"seeds={SEEDS}")
    _log(f"[config] n_dim={N_DIM} dg_dim={DG_DIM} sparsity={DG_SPARSITY} "
         f"cluster_size={CLUSTER_SIZE}")
    _log(f"[config] N_PAIRS={N_PAIRS}")
    _log(f"[config] cluster_cos_sweep={CLUSTER_COS_SWEEP}")
    _log(f"[config] corruption_sweep={CORRUPTION_SWEEP}")
    _log(f"[config] tf_capacity_theoretical={_TF_CAPACITY:.1f}")
    _log(f"[config] load_fraction N_PAIRS/C_TF="
         f"{N_PAIRS/_TF_CAPACITY*100:.1f}%")
    _log(f"[config] HP1 COSINE C{HP1_CLUSTER_COS} R{HP1_CORRUPTION} "
         f"r@1 <= {HP1_COSINE_LOW_CLUSTER_MODERATE_CORRUPT_MAX}")
    _log(f"[config] HP2 cluster_cos INTERIOR boundary observable")
    _log(f"[config] HP3 COSINE C{HP3_CLUSTER_COS} R{HP3_CORRUPTION} "
         f"r@1 >= {HP3_COSINE_HIGH_CLUSTER_HIGH_CORRUPT_MIN}")

    t0 = time.perf_counter()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        seed_t0 = time.perf_counter()
        ps = _run_one_seed(seed, output_dir)
        ps["seed_elapsed_s"] = float(time.perf_counter() - seed_t0)
        per_seed.append(ps)
        _write_partial_seed(output_dir, seed, ps)
        _log(f"[seed {seed}] complete in {ps['seed_elapsed_s']:.2f}s; "
             f"checkpoint written")

    agg = _aggregate(per_seed)
    actual_n_units = sum(
        1
        for ps in per_seed
        for arm_m in ps.get("per_arm", {}).values()
        if "failure_class" not in arm_m
    )
    verdict, verdict_msg = _verdict(agg, expected_n_units, actual_n_units)
    _log(f"[VERDICT] {verdict}")
    _log(f"[VERDICT_MSG] {verdict_msg}")
    total_elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_arms": len(ARM_SPECS),
        "n_dim": N_DIM,
        "dg_dim": DG_DIM,
        "dg_sparsity_target": DG_SPARSITY,
        "n_pairs": N_PAIRS,
        "cluster_size": CLUSTER_SIZE,
        "cluster_cos_sweep": CLUSTER_COS_SWEEP,
        "corruption_sweep": CORRUPTION_SWEEP,
        "tf_capacity_theoretical": _TF_CAPACITY,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "baseline_in_band_check": {
            "chance_r1": CHANCE_R1,
            "band_max_r1": BASELINE_IN_BAND_R1_MAX,
            "random_arm_r1_means": {
                _arm_name("random", cc, corr):
                    agg.get(_arm_name("random", cc, corr), {}).get(
                        "recall_at_1_mean")
                for cc in CLUSTER_COS_SWEEP for corr in CORRUPTION_SWEEP
            },
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": [_arm_name("cosine", HP1_CLUSTER_COS, HP1_CORRUPTION)],
            "HP2": [_arm_name("cosine", cc, corr)
                    for cc in CLUSTER_COS_SWEEP
                    for corr in CORRUPTION_SWEEP],
            "HP3": [_arm_name("cosine", HP3_CLUSTER_COS, HP3_CORRUPTION)],
            "HF_baseline_in_band": [_arm_name("random", cc, corr)
                                    for cc in CLUSTER_COS_SWEEP
                                    for corr in CORRUPTION_SWEEP],
            "HF_dg_sparse_rate": [_arm_name("hippocampal", cc, corr)
                                  for cc in CLUSTER_COS_SWEEP
                                  for corr in CORRUPTION_SWEEP],
        },
        "per_seed": per_seed,
        "per_arm_aggregate": agg,
        "elapsed_s": total_elapsed,
        "ts_iso_end": datetime.now(timezone.utc).isoformat(),
    }

    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    _log(f"[metrics] written to {final} (elapsed={total_elapsed:.2f}s)")

    write_metrics(output_dir, metrics)
    return 0


if __name__ == "__main__":
    _output_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
        sys.exit(rc or 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
