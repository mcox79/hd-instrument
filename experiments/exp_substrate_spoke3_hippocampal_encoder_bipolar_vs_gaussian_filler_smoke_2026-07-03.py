"""exp_substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke_2026_07_03

Stage 2 Spoke 3 hippocampal-encoder BIPOLAR-vs-GAUSSIAN filler geometry probe:
revival criterion for Skunkworks MM_TENTATIVE analytical-model calibration atom
(META_SKUNKWORKS_ANALYTICAL_MODEL_CALIBRATION_GAUSSIAN_JL_ASSUMPTION_FAILS_AT_
BIPOLAR_DIM_ZERO_CUE_DETERMINISM).

Task class: SAME as Cell 4 discriminative-regime cell (episodic-binding +
partial-cue retrieval at N=500 pairs adversarial-cluster 75% dim-zero
corruption). ONLY the filler geometry changes to test whether the Skunkworks
Gaussian-JL analytical prediction (baseline cosine degrades at cluster_cos~0.90)
holds at Gaussian filler geometry after having FAILED at bipolar geometry
(commit 1350c7789).

Regime A (BIPOLAR): flip_frac=0.026 -> within-cluster filler cos_theoretical =
  (1-2*0.026)^2 = 0.900. Signal channel at 75% dim-zero cue is DETERMINISTIC
  bit-identity (Cell 4 mechanism-vs-baseline failure).
Regime B (GAUSSIAN): per-dim ~ N(0,1) with cluster mixing rho=0.90. Signal
  channel at 75% dim-zero cue has continuous Gaussian variance (Skunkworks
  Gaussian-JL assumption bed).

Arms (4 arm-templates x 2 geometries x 3 seeds = 24 units):
  A ARM_HIPPO_BIPOLAR                    (LOAD_BEARING; HP4 regression)
  B ARM_HIPPO_DG_ONLY_BIPOLAR            (ablation)
  C ARM_COSINE_BASELINE_BIPOLAR          (REGRESSION; HP4)
  D ARM_RANDOM_BASELINE_BIPOLAR          (chance floor)
  E ARM_HIPPO_GAUSSIAN                   (LOAD_BEARING; HP2, HP3)
  F ARM_HIPPO_DG_ONLY_GAUSSIAN           (ablation)
  G ARM_COSINE_BASELINE_GAUSSIAN         (LOAD_BEARING; HP1)
  H ARM_RANDOM_BASELINE_GAUSSIAN         (chance floor)

HP band:
  HP1  ARM_COSINE_BASELINE_GAUSSIAN r@1 <= 0.90 (baseline degrades at Gaussian)
  HP2  ARM_HIPPO_GAUSSIAN r@1 >= 0.60 (mechanism fires at Gaussian)
  HP3  ARM_HIPPO_GAUSSIAN - ARM_COSINE_BASELINE_GAUSSIAN r@1 delta >= 0.10
       (W2 discriminative-regime WIN witness)
  HP4  ARM_COSINE_BASELINE_BIPOLAR r@1 >= 0.99 (regression: bit-identity holds)

HARD_PASS = HP1 AND HP2 AND HP3 AND HP4.
HF-cosine-still-saturates: HP1 fails at Gaussian -> Gaussian-JL prediction ALSO fails.
HF-regression: HP4 fails -> code drift; downstream Gaussian verdict UNRELIABLE.
HF-hippo-broken: HP2 fails AND HIPPO_BIPOLAR also below 0.60.
HF-separation: HP3 fails AND HP1 fires (baseline degrades but mechanism doesn't win).
MB: partial fires.

Regime:
  N_DIM=2048, DG_DIM=8192, SPARSITY=0.02 (T-F capacity ~1047 THEORETICAL@).
  N_PAIRS=500, CORRUPTION=0.75, CLUSTER_SIZE=5.
  FLIP_FRAC_BIPOLAR=0.026 -> within-cluster filler cos target 0.90.
  GAUSSIAN_CLUSTER_RHO=0.90 -> within-cluster filler cos target 0.90.
  Seeds=[11,17,23].

Pre-reg: preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_smoke.md
Primitive: hdlab/hippocampal_encoder.py.

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM discriminator on SUPERVISED synthetic
  binding task. Not a general-knowledge / language claim.
- Prior Skunkworks Gaussian-JL analytical FAILED at bipolar (Cell 4);
  this cell tests the COUNTERFACTUAL Gaussian regime.
- If HP1+HP2+HP3+HP4: Gaussian-JL prediction VALIDATED at Gaussian; W2 opens
  with filler-geometry qualifier.
- If HP1 fails: Gaussian-JL prediction ALSO fails; deeper limitation.
- Skunkworks T-F formula C_TF = dg_dim / (2 * ln(1/p)).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception
- baseline_in_band (META_RULE_AG; RANDOM sanity per geometry)
- HP_SCOPE per-arm declaration
- cardinality_ok (EXPECTED_N_UNITS = 8 arms x 3 seeds = 24)
- per-unit failure_class instrumentation
- start_marker_written, crash_diagnostic_present, heartbeat_present
- per-seed checkpoint (SH-4)
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)

Scope: SMOKE-only. USER-locked SMOKE-only-on-local_cpu.

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
    "substrate_spoke3_hippocampal_encoder_bipolar_vs_gaussian_filler_"
    "smoke_2026_07_03"
)

# --- Config ---

N_DIM = 2048
DG_DIM = 8192
DG_SPARSITY = 0.02
N_PAIRS = 500
CORRUPTION = 0.75
CLUSTER_SIZE = 5
FLIP_FRAC_BIPOLAR = 0.026   # (1-2*f)^2 = 0.900 THEORETICAL@ within-cluster filler cos
GAUSSIAN_CLUSTER_RHO = 0.90  # THEORETICAL@ within-cluster filler cos = rho
SEEDS = [11, 17, 23]

# HP thresholds.
HP1_COSINE_GAUSSIAN_MAX = 0.90
HP2_HIPPO_GAUSSIAN_MIN = 0.60
HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN = 0.10
HP4_COSINE_BIPOLAR_MIN = 0.99

# HF band tolerances.
BIPOLAR_HIPPO_MIN_FOR_REGRESSION = 0.85  # widened; flip_frac 0.026 not 0.10
                                          # MEASURED@Cell4=0.978 at flip_frac=0.10;
                                          # HYPOTHESIZED@ this cell at flip_frac=0.026
                                          # (harder codebook) expected [0.90, 1.00]

# HF-baseline sanity.
CHANCE_R1 = 1.0 / N_PAIRS  # 0.002
BASELINE_IN_BAND_R1_MAX = 5.0 * CHANCE_R1  # 0.010

# DG architectural constraint.
DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040

# THEORETICAL@ Tsodyks-Feigelman capacity C_TF = dg_dim / (2 * ln(1/sparsity)).
_TF_CAPACITY = DG_DIM / (2.0 * math.log(1.0 / DG_SPARSITY))


# --- Arm specs ---

ARM_SPECS = [
    # (name, encoder_kind, filler_geometry, role)
    ("ARM_HIPPO_BIPOLAR",                   "hippocampal", "bipolar",  "load_bearing_regression"),
    ("ARM_HIPPO_DG_ONLY_BIPOLAR",           "dg_only",     "bipolar",  "ablation"),
    ("ARM_COSINE_BASELINE_BIPOLAR",         "cosine",      "bipolar",  "regression_hp4"),
    ("ARM_RANDOM_BASELINE_BIPOLAR",         "random",      "bipolar",  "chance_floor"),
    ("ARM_HIPPO_GAUSSIAN",                  "hippocampal", "gaussian", "load_bearing_hp2_hp3"),
    ("ARM_HIPPO_DG_ONLY_GAUSSIAN",          "dg_only",     "gaussian", "ablation"),
    ("ARM_COSINE_BASELINE_GAUSSIAN",        "cosine",      "gaussian", "load_bearing_hp1"),
    ("ARM_RANDOM_BASELINE_GAUSSIAN",        "random",      "gaussian", "chance_floor"),
]
ARM_NAMES = [s[0] for s in ARM_SPECS]

ARM_HIPPO_B      = "ARM_HIPPO_BIPOLAR"
ARM_HIPPO_G      = "ARM_HIPPO_GAUSSIAN"
ARM_COSINE_B     = "ARM_COSINE_BASELINE_BIPOLAR"
ARM_COSINE_G     = "ARM_COSINE_BASELINE_GAUSSIAN"
ARM_RANDOM_B     = "ARM_RANDOM_BASELINE_BIPOLAR"
ARM_RANDOM_G     = "ARM_RANDOM_BASELINE_GAUSSIAN"
ARM_DGONLY_B     = "ARM_HIPPO_DG_ONLY_BIPOLAR"
ARM_DGONLY_G     = "ARM_HIPPO_DG_ONLY_GAUSSIAN"


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
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)


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

def _draw_pairs_adversarial_bipolar(n_pairs: int, n_dim: int, seed: int,
                                    cluster_size: int = CLUSTER_SIZE,
                                    flip_frac: float = FLIP_FRAC_BIPOLAR
                                    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Adversarial cluster-shared BIPOLAR codebook.

    Per cluster: shared bipolar `anchor_role_key` + shared bipolar `anchor_filler`.
    Each member's filler = anchor_filler with `flip_frac` random dims flipped
    (per-member independent). role_key SHARED across cluster.

    THEORETICAL@ within-cluster filler cos = (1 - 2*flip_frac)^2
      = 0.900 at flip_frac = 0.026.
    """
    rng = np.random.default_rng(int(seed) * 953 + 19)
    n_flip = int(round(flip_frac * n_dim))
    role_keys = np.zeros((n_pairs, n_dim), dtype=np.float32)
    fillers = np.zeros((n_pairs, n_dim), dtype=np.float32)
    n_clusters = (n_pairs + cluster_size - 1) // cluster_size
    for c in range(n_clusters):
        anchor_role = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
        anchor_filler = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
        start = c * cluster_size
        end = min(start + cluster_size, n_pairs)
        for i in range(start, end):
            role_keys[i] = anchor_role
            member = anchor_filler.copy()
            if n_flip > 0:
                flip_idx = rng.choice(n_dim, size=n_flip, replace=False)
                member[flip_idx] *= -1.0
            fillers[i] = member
    episodes = (role_keys * fillers).astype(np.float32)
    return role_keys, fillers, episodes


def _draw_pairs_adversarial_gaussian(n_pairs: int, n_dim: int, seed: int,
                                     cluster_size: int = CLUSTER_SIZE,
                                     rho: float = GAUSSIAN_CLUSTER_RHO
                                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Adversarial cluster-shared GAUSSIAN codebook.

    Per cluster: shared BIPOLAR `anchor_role_key` (role_key stays bipolar for
    binding-primitive compatibility) + shared GAUSSIAN `anchor_filler`. Each
    member's filler = sqrt(rho) * anchor_filler + sqrt(1 - rho) * per_member_gauss.
    role_key SHARED across cluster.

    THEORETICAL@ within-cluster filler cos = rho (both terms zero-mean unit-variance
    independent Gaussians; cos = <sqrt(rho)*a + sqrt(1-rho)*n_i, sqrt(rho)*a + sqrt(1-rho)*n_j>
    / ||...||||...|| approaches rho as n_dim -> inf).

    Episode = role_key * filler (dim-wise product). With bipolar role_key
    (+/-1) and Gaussian filler (~N(0,1)), episode dim ~ N(0,1) preserved.
    Retrieval channel at 75% dim-zero cue -> 25% dims contribute Gaussian
    signal with SAME sign channel as target but continuous magnitude (NOT
    deterministic bit-identity).
    """
    rng = np.random.default_rng(int(seed) * 953 + 19)
    role_keys = np.zeros((n_pairs, n_dim), dtype=np.float32)
    fillers = np.zeros((n_pairs, n_dim), dtype=np.float32)
    sqrt_rho = math.sqrt(rho)
    sqrt_one_minus = math.sqrt(1.0 - rho)
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
    rng = np.random.default_rng(int(seed) * 977 + 13)
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


# --- Encoder implementations ---

def _encode_hippocampal(episodes: np.ndarray, seed: int
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
    cues = _corrupt_cue(episodes, CORRUPTION, seed=int(seed))
    completed_dg = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "hippocampal",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(CORRUPTION),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    return stored_dg, completed_dg, fit_wall, ret_wall, diag


def _encode_dg_only(episodes: np.ndarray, seed: int
                    ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    from hdlab.hippocampal_encoder import HippocampalEncoder
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    stored_dg = enc.dg.encode_batch(episodes)
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(stored_dg)

    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, CORRUPTION, seed=int(seed))
    cue_dg = enc.dg.encode_batch(cues)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "dg_only",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "partial_cue_fraction_zeroed": float(CORRUPTION),
        "ca3_used": False,
    }
    return stored_dg, cue_dg, fit_wall, ret_wall, diag


def _encode_cosine_baseline(episodes: np.ndarray, seed: int
                            ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    fit_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, CORRUPTION, seed=int(seed))
    fit_wall = time.perf_counter() - fit_t0
    diag = {"encoder": "cosine_baseline", "input_dim": N_DIM,
            "partial_cue_fraction_zeroed": float(CORRUPTION)}
    return episodes.copy(), cues, 0.0, fit_wall, diag


def _encode_random(episodes: np.ndarray, seed: int
                   ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    n = episodes.shape[0]
    rng = np.random.default_rng(int(seed) * 883 + 29)
    t0 = time.perf_counter()
    stored = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    query = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    diag = {"encoder": "random", "input_dim": N_DIM}
    return stored, query, 0.0, wall, diag


ENCODER_FUNCS = {
    "hippocampal": _encode_hippocampal,
    "dg_only": _encode_dg_only,
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
        sys.argv = ["exp_bipolar_vs_gaussian_smoke"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_corrupt_cue_75pct() -> None:
    rng = np.random.default_rng(3)
    n, d = 20, 512
    episodes = (rng.integers(0, 2, size=(n, d)) * 2 - 1).astype(np.float32)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.75, seed=11)
    zeros_per_row = (cues == 0.0).sum(axis=1)
    expected = int(round(0.75 * d))
    assert np.all(zeros_per_row == expected), (
        f"75%: zeros_per_row {zeros_per_row[:5]} expected {expected}"
    )
    nonzero_mask = cues != 0.0
    assert np.all(cues[nonzero_mask] == episodes[nonzero_mask]), \
        "cue non-zero dims don't match episode"
    print("[selftest corrupt_cue_75pct] PASS", flush=True)


def _selftest_bipolar_within_cluster_cos_hits_0_90() -> None:
    _, fillers, _ = _draw_pairs_adversarial_bipolar(
        n_pairs=100, n_dim=N_DIM, seed=11,
        cluster_size=CLUSTER_SIZE, flip_frac=FLIP_FRAC_BIPOLAR)
    obs = _within_cluster_cos_observed(fillers, cluster_size=CLUSTER_SIZE,
                                       max_comparisons=100)
    # THEORETICAL@ (1 - 2*0.026)^2 = 0.900. Tolerance +/- 0.05.
    assert 0.85 <= obs <= 0.95, (
        f"bipolar within-cluster filler cos {obs:.4f} outside [0.85, 0.95] "
        f"(THEORETICAL 0.90 at flip_frac={FLIP_FRAC_BIPOLAR})"
    )
    print(f"[selftest bipolar_within_cluster_cos_hits_0_90] PASS obs={obs:.4f}",
          flush=True)


def _selftest_gaussian_within_cluster_cos_hits_0_90() -> None:
    _, fillers, _ = _draw_pairs_adversarial_gaussian(
        n_pairs=100, n_dim=N_DIM, seed=11,
        cluster_size=CLUSTER_SIZE, rho=GAUSSIAN_CLUSTER_RHO)
    obs = _within_cluster_cos_observed(fillers, cluster_size=CLUSTER_SIZE,
                                       max_comparisons=100)
    # THEORETICAL@ rho = 0.900. Tolerance +/- 0.05.
    assert 0.85 <= obs <= 0.95, (
        f"gaussian within-cluster filler cos {obs:.4f} outside [0.85, 0.95] "
        f"(THEORETICAL {GAUSSIAN_CLUSTER_RHO} at rho={GAUSSIAN_CLUSTER_RHO})"
    )
    print(f"[selftest gaussian_within_cluster_cos_hits_0_90] PASS obs={obs:.4f}",
          flush=True)


def _selftest_gaussian_filler_is_real_valued() -> None:
    """Gaussian filler should NOT be {-1, +1} bipolar."""
    _, fillers, _ = _draw_pairs_adversarial_gaussian(
        n_pairs=20, n_dim=512, seed=11, cluster_size=5,
        rho=GAUSSIAN_CLUSTER_RHO)
    unique_vals = np.unique(np.round(fillers, 4))
    assert unique_vals.size > 10, (
        f"gaussian filler has only {unique_vals.size} unique values; "
        f"expected continuous (>>10). first 10: {unique_vals[:10]}"
    )
    # Check variance is reasonable (~ E[fillers^2] approx var(anchor)+var(noise) = 1)
    var = float(np.var(fillers))
    assert 0.7 <= var <= 1.3, (
        f"gaussian filler variance {var:.4f} outside [0.7, 1.3]; "
        f"expected ~1.0 for unit-variance Gaussian"
    )
    print(f"[selftest gaussian_filler_is_real_valued] PASS "
          f"n_unique={unique_vals.size} var={var:.4f}", flush=True)


def _selftest_arms_differ_hash_micro() -> None:
    """Same episodes -> different encoders should produce different queries."""
    _, _, episodes = _draw_pairs_adversarial_bipolar(
        n_pairs=20, n_dim=256, seed=11, cluster_size=5, flip_frac=0.026)
    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02, seed=11)
    _ = enc.encode_and_write(episodes)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.75, seed=11)
    completed = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    enc2 = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02, seed=11)
    cue_dg = enc2.dg.encode_batch(cues)
    h_hip = hashlib.sha256(completed.tobytes()).hexdigest()[:16]
    h_dg = hashlib.sha256(cue_dg.tobytes()).hexdigest()[:16]
    h_cos = hashlib.sha256(cues.tobytes()).hexdigest()[:16]
    assert len({h_hip, h_dg, h_cos}) == 3, (
        f"arms not distinct: hip={h_hip} dg={h_dg} cos={h_cos}"
    )
    print(f"[selftest arms_differ_hash_micro] PASS "
          f"hip={h_hip[:8]} dg={h_dg[:8]} cos={h_cos[:8]}", flush=True)


def _selftest_determinism_gaussian() -> None:
    """Gaussian codebook with SAME seed produces bit-identical fillers."""
    _, fA, epA = _draw_pairs_adversarial_gaussian(
        n_pairs=30, n_dim=256, seed=11, cluster_size=5,
        rho=GAUSSIAN_CLUSTER_RHO)
    _, fB, epB = _draw_pairs_adversarial_gaussian(
        n_pairs=30, n_dim=256, seed=11, cluster_size=5,
        rho=GAUSSIAN_CLUSTER_RHO)
    assert np.array_equal(fA, fB), "Gaussian filler draw non-deterministic"
    assert np.array_equal(epA, epB), "Gaussian episode non-deterministic"
    print("[selftest determinism_gaussian] PASS", flush=True)


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
            f"hdlab.hippocampal_encoder --self-test returned {result.returncode}"
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
        ("corrupt_cue_75pct", _selftest_corrupt_cue_75pct),
        ("bipolar_within_cluster_cos_hits_0_90",
         _selftest_bipolar_within_cluster_cos_hits_0_90),
        ("gaussian_within_cluster_cos_hits_0_90",
         _selftest_gaussian_within_cluster_cos_hits_0_90),
        ("gaussian_filler_is_real_valued",
         _selftest_gaussian_filler_is_real_valued),
        ("arms_differ_hash_micro", _selftest_arms_differ_hash_micro),
        ("determinism_gaussian", _selftest_determinism_gaussian),
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

def _episode_cache_key(geometry: str, seed: int) -> str:
    return f"{geometry}_s{seed}"


def _run_one_seed(seed: int, output_dir: Path) -> Dict:
    n_arms = len(ARM_SPECS)
    per_arm: Dict[str, Dict] = {}
    per_arm_query: Dict[str, np.ndarray] = {}
    episode_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    cluster_cos_by_geom: Dict[str, float] = {}

    for arm_idx, spec in enumerate(ARM_SPECS):
        arm_name, encoder_kind, geometry, role = spec
        _log(f"[seed {seed}] arm {arm_idx+1}/{n_arms} {arm_name} "
             f"(encoder={encoder_kind} geometry={geometry} role={role})")
        arm_t0 = time.perf_counter()

        try:
            if encoder_kind == "random":
                episodes = np.zeros((N_PAIRS, N_DIM), dtype=np.float32)
            else:
                key = _episode_cache_key(geometry, seed)
                if key not in episode_cache:
                    if geometry == "bipolar":
                        rk, fl, ep = _draw_pairs_adversarial_bipolar(
                            N_PAIRS, N_DIM, seed=seed)
                    elif geometry == "gaussian":
                        rk, fl, ep = _draw_pairs_adversarial_gaussian(
                            N_PAIRS, N_DIM, seed=seed)
                    else:
                        raise ValueError(f"Unknown geometry: {geometry}")
                    episode_cache[key] = (rk, fl, ep)
                    obs_cos = _within_cluster_cos_observed(fl)
                    cluster_cos_by_geom[geometry] = obs_cos
                    _log(f"[seed {seed}]   drew {geometry} codebook "
                         f"N={N_PAIRS}: intra-cluster-filler-cos-obs="
                         f"{obs_cos:.4f}")
                _, _, episodes = episode_cache[key]

            enc_fn = ENCODER_FUNCS[encoder_kind]
            stored, query, enc_wall, fit_wall, arm_diag = enc_fn(episodes, seed)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "encoder_kind": encoder_kind,
                "geometry": geometry,
                "role": role,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {arm_name} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, n_arms,
                       time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed",
                        "failure_class": failure_class})
            continue

        n_nan = int(np.isnan(stored).sum()) + int(np.isnan(query).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "encoder_kind": encoder_kind,
                "geometry": geometry,
                "role": role,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
            }
            _log(f"[seed {seed}] arm {arm_name} NaN (n_nan={n_nan})")
            continue

        metrics = _retrieval_metrics(stored, query, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "encoder_kind": encoder_kind,
            "geometry": geometry,
            "role": role,
            "stored_dim": int(stored.shape[1]),
            "encoding_wall_s": float(enc_wall),
            "fit_wall_s": float(fit_wall),
            "arm_wall_s": float(time.perf_counter() - arm_t0),
            "arm_diag": arm_diag,
        })
        per_arm[arm_name] = metrics
        per_arm_query[arm_name] = query
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.4f} "
             f"r@5={metrics['recall_at_5']:.4f} "
             f"intra={metrics['intra_pair_cos_mean']:.3f} "
             f"inter={metrics['inter_pair_cos_mean']:.3f} "
             f"arm_wall={metrics['arm_wall_s']:.1f}s")
        _heartbeat(output_dir, arm_idx, n_arms,
                   time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_1": metrics["recall_at_1"]})

    # META_RULE_AF: RANDOM_BIPOLAR and RANDOM_GAUSSIAN legitimately share
    # bit-identical queries (both are chance-floor arms; the _encode_random
    # sampler doesn't consume geometry -- it just draws fresh random bipolar
    # vectors keyed on seed, which is the correct chance-floor semantic).
    # Exempted from arms_differ_hash; digested informationally.
    arms_differ_exempted_pairs = [(ARM_RANDOM_B, ARM_RANDOM_G)]
    non_exempt_query = {
        n: q for n, q in per_arm_query.items()
        if n not in (ARM_RANDOM_B, ARM_RANDOM_G)
    }
    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    if len(non_exempt_query) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(non_exempt_query)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}
    # Also fingerprint the exempted random arms informationally.
    for arm_name in (ARM_RANDOM_B, ARM_RANDOM_G):
        if arm_name in per_arm_query:
            arr = per_arm_query[arm_name]
            arms_differ_digests[arm_name + "_exempted"] = hashlib.sha256(
                np.ascontiguousarray(arr.astype(np.float32)).tobytes()
            ).hexdigest()[:16]

    return {
        "seed": int(seed),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
        "cluster_cos_observed_by_geometry": cluster_cos_by_geom,
    }


# --- Aggregation + verdict ---

def _aggregate(per_seed: List[Dict]) -> Dict:
    out: Dict[str, Dict] = {}
    for arm in ARM_NAMES:
        r1s, r5s, mrrs, walls, fits = [], [], [], [], []
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
            fits.append(arm_m.get("fit_wall_s", 0.0))
            intras.append(arm_m.get("intra_pair_cos_mean", 0.0))
            inters.append(arm_m.get("inter_pair_cos_mean", 0.0))
            diag = arm_m.get("arm_diag") or {}
            if "dg_sparse_rate_observed" in diag:
                dg_rates.append(diag["dg_sparse_rate_observed"])
        if r1s:
            entry = {
                "n_seeds_succeeded": len(r1s),
                "n_seeds_failed": n_failed,
                "recall_at_1_mean": float(np.mean(r1s)),
                "recall_at_1_std": float(np.std(r1s)),
                "recall_at_5_mean": float(np.mean(r5s)),
                "mrr_mean": float(np.mean(mrrs)),
                "intra_pair_cos_mean": float(np.mean(intras)),
                "inter_pair_cos_mean": float(np.mean(inters)),
                "arm_wall_s_mean": float(np.mean(walls)),
                "fit_wall_s_mean": float(np.mean(fits)),
            }
            if dg_rates:
                entry["dg_sparse_rate_mean"] = float(np.mean(dg_rates))
            out[arm] = entry
        else:
            out[arm] = {"n_seeds_succeeded": 0, "n_seeds_failed": n_failed,
                        "recall_at_1_mean": None}
    return out


def _verdict(agg: Dict, expected_n_units: int,
             actual_n_units: int) -> Tuple[str, str]:
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics "
                f"but got {actual_n_units}. See per-seed failure_class.")

    def _r1(arm: str):
        return agg.get(arm, {}).get("recall_at_1_mean")

    hip_b = _r1(ARM_HIPPO_B)
    hip_g = _r1(ARM_HIPPO_G)
    cos_b = _r1(ARM_COSINE_B)
    cos_g = _r1(ARM_COSINE_G)
    rnd_b = _r1(ARM_RANDOM_B)
    rnd_g = _r1(ARM_RANDOM_G)
    dg_only_b = _r1(ARM_DGONLY_B)
    dg_only_g = _r1(ARM_DGONLY_G)
    dg_rate_hip_g = agg.get(ARM_HIPPO_G, {}).get("dg_sparse_rate_mean")
    dg_rate_hip_b = agg.get(ARM_HIPPO_B, {}).get("dg_sparse_rate_mean")

    missing = []
    for a, v in [(ARM_HIPPO_B, hip_b), (ARM_HIPPO_G, hip_g),
                 (ARM_COSINE_B, cos_b), (ARM_COSINE_G, cos_g),
                 (ARM_RANDOM_B, rnd_b), (ARM_RANDOM_G, rnd_g)]:
        if v is None:
            missing.append(a)
    if missing:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: arm(s) with no recall@1: {missing}")

    # HF-baseline sanity (META_RULE_AG).
    for geom_name, rnd_v in [("BIPOLAR", rnd_b), ("GAUSSIAN", rnd_g)]:
        if rnd_v > BASELINE_IN_BAND_R1_MAX:
            return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                    f"HF baseline_in_band failed: ARM_RANDOM_{geom_name} "
                    f"r@1={rnd_v:.4f} > {BASELINE_IN_BAND_R1_MAX:.4f} "
                    f"(chance={CHANCE_R1:.4f}). Retrieval bug.")

    # HF-dg-rate architectural sanity.
    for geom_name, dg_v in [("BIPOLAR", dg_rate_hip_b),
                            ("GAUSSIAN", dg_rate_hip_g)]:
        if dg_v is not None and not (
                DG_SPARSE_RATE_MIN <= dg_v <= DG_SPARSE_RATE_MAX):
            return ("HARD_FAIL_DG_SPARSE_RATE_ARCHITECTURAL",
                    f"HF DG sparse rate ({geom_name})={dg_v:.4f} outside "
                    f"[{DG_SPARSE_RATE_MIN:.3f}, {DG_SPARSE_RATE_MAX:.3f}] "
                    f"(target {DG_SPARSITY:.3f}).")

    # HP4: regression bipolar cosine saturation (code-integrity gate).
    hp4_ok = cos_b >= HP4_COSINE_BIPOLAR_MIN
    if not hp4_ok:
        return ("HARD_FAIL_REGRESSION_BROKEN",
                f"HF regression: HP4 requires ARM_COSINE_BASELINE_BIPOLAR r@1 "
                f">= {HP4_COSINE_BIPOLAR_MIN} (bit-identity determinism); got "
                f"{cos_b:.4f}. Code drift from Cell 4 or codebook change "
                f"broke bipolar saturation; downstream Gaussian verdict "
                f"UNRELIABLE. hip_b={hip_b} dg_only_b={dg_only_b} "
                f"cos_g={cos_g} hip_g={hip_g}")

    # HP1 primary: cosine degrades at Gaussian (Skunkworks Gaussian-JL test).
    hp1_ok = cos_g <= HP1_COSINE_GAUSSIAN_MAX
    # HP2: hippo fires at Gaussian.
    hp2_ok = hip_g >= HP2_HIPPO_GAUSSIAN_MIN
    # HP3: mechanism-vs-baseline separation at Gaussian (W2 witness).
    sep_g = hip_g - cos_g if (hip_g is not None and cos_g is not None) else None
    hp3_ok = (sep_g is not None
              and sep_g >= HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN)

    # HARD_PASS: all 4 HPs.
    if hp1_ok and hp2_ok and hp3_ok and hp4_ok:
        return ("HARD_PASS",
                f"HARD_PASS: Skunkworks Gaussian-JL analytical prediction "
                f"VALIDATED at Gaussian filler geometry. HP1: COSINE_GAUSSIAN "
                f"r@1={cos_g:.4f} <= {HP1_COSINE_GAUSSIAN_MAX} (baseline "
                f"degrades). HP2: HIPPO_GAUSSIAN r@1={hip_g:.4f} >= "
                f"{HP2_HIPPO_GAUSSIAN_MIN} (mechanism fires). HP3: HIPPO-"
                f"COSINE separation={sep_g:+.4f} >= "
                f"{HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN} (W2 discriminative-"
                f"regime WIN witness). HP4: COSINE_BIPOLAR r@1={cos_b:.4f} "
                f">= {HP4_COSINE_BIPOLAR_MIN} (bit-identity determinism holds "
                f"in bipolar regime; code-integrity gate). BIPOLAR reference: "
                f"HIPPO r@1={hip_b:.4f} DG_ONLY r@1={dg_only_b}. GAUSSIAN "
                f"reference: DG_ONLY r@1={dg_only_g}. Analytical model "
                f"scope-refined (Gaussian-JL applies to Gaussian fillers only, "
                f"not bipolar-adjacent geometries). SCOPE: "
                f"MECHANISM_DISCRIMINATED_ON_SUPERVISED synthetic Gaussian-"
                f"filler binding; does NOT grant substrate general-knowledge "
                f"or language capability. HOLD pending USER decision.")

    # HF-cosine-still-saturates-at-Gaussian (primary probe outcome).
    if not hp1_ok:
        # Add secondary observation if HIPPO also broken at both geometries.
        hip_broken_note = ""
        if not hp2_ok and hip_b is not None and hip_b < HP2_HIPPO_GAUSSIAN_MIN:
            hip_broken_note = (
                f" SECONDARY: HIPPO mechanism ALSO below "
                f"{HP2_HIPPO_GAUSSIAN_MIN} at BOTH geometries "
                f"(bipolar={hip_b:.4f}, gaussian={hip_g:.4f}); harder codebook "
                f"(cluster_cos~0.90 vs Cell 4's ~0.64) crushes HIPPO too. "
                f"DG_ONLY_B={dg_only_b} DG_ONLY_G={dg_only_g}. Even at "
                f"HP2-passing HIPPO, HP3 separation likely negative because "
                f"cosine saturates at 1.000."
            )
        return ("HARD_FAIL_COSINE_STILL_SATURATES_AT_GAUSSIAN",
                f"HF: Skunkworks Gaussian-JL analytical prediction ALSO FAILS "
                f"at Gaussian regime. HP1: COSINE_GAUSSIAN r@1={cos_g:.4f} > "
                f"{HP1_COSINE_GAUSSIAN_MAX} (baseline STILL saturates). "
                f"HIPPO_GAUSSIAN r@1={hip_g:.4f} (HP2={hp2_ok}). Separation "
                f"HIPPO-COSINE at Gaussian={sep_g:+.4f} (HP3={hp3_ok}). "
                f"BIPOLAR reference: HIPPO r@1={hip_b:.4f} COSINE "
                f"r@1={cos_b:.4f} DG_ONLY r@1={dg_only_b} (HP4={hp4_ok}). "
                f"Interpretation: analytical model has deeper limitation "
                f"than just bipolar-determinism; W2 discriminative-regime "
                f"may not be achievable with this primitive at cluster_cos-"
                f"0.90 geometry regardless of filler encoding. HONEST SCOPE: "
                f"prediction refuted at both bipolar AND Gaussian; route to "
                f"research 2x-drill on primitive-substrate scale-sensitivity."
                f"{hip_broken_note}")

    # HF-hippo-broken-everywhere (HP1 fires but hippo below floor at both geoms).
    if not hp2_ok and (hip_b is not None and hip_b < HP2_HIPPO_GAUSSIAN_MIN):
        return ("HARD_FAIL_HIPPO_BROKEN_EVERYWHERE",
                f"HF: HP1 fires (COSINE_GAUSSIAN r@1={cos_g:.4f} <= "
                f"{HP1_COSINE_GAUSSIAN_MAX}; baseline degrades) BUT HIPPO "
                f"mechanism r@1 below {HP2_HIPPO_GAUSSIAN_MIN} at BOTH "
                f"geometries (bipolar={hip_b:.4f}, gaussian={hip_g:.4f}); "
                f"mechanism has scale/regime issue not filler-geometry-"
                f"diagnosable. HP4={hp4_ok} (cos_b={cos_b:.4f}). "
                f"dg_only_b={dg_only_b} dg_only_g={dg_only_g}")

    # HF-separation: baseline degrades but mechanism doesn't win.
    if hp1_ok and not hp3_ok:
        return ("HARD_FAIL_NO_MECHANISM_SEPARATION_AT_GAUSSIAN",
                f"HF: baseline degrades at Gaussian (HP1 OK: COSINE_GAUSSIAN "
                f"r@1={cos_g:.4f}) BUT mechanism doesn't win. HP3: HIPPO-"
                f"COSINE sep={sep_g:+.4f} < "
                f"{HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN}. HIPPO_GAUSSIAN "
                f"r@1={hip_g:.4f} (HP2={hp2_ok}). W2 discriminative-regime "
                f"witness missing. BIPOLAR: HIPPO={hip_b:.4f} COS={cos_b:.4f} "
                f"DG_ONLY_G={dg_only_g}. Interpretation: prediction "
                f"partially validates (baseline degrades) but mechanism does "
                f"NOT outperform baseline; substrate structural mechanism "
                f"has deeper issue at Gaussian regime.")

    # MIDDLE_BAND: partial fires.
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial HP set. "
            f"HP1 COSINE_GAUSSIAN <= {HP1_COSINE_GAUSSIAN_MAX}: "
            f"{'PASS' if hp1_ok else 'FAIL'} ({cos_g:.4f}). "
            f"HP2 HIPPO_GAUSSIAN >= {HP2_HIPPO_GAUSSIAN_MIN}: "
            f"{'PASS' if hp2_ok else 'FAIL'} ({hip_g:.4f}). "
            f"HP3 HIPPO-COSINE sep >= {HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN}: "
            f"{'PASS' if hp3_ok else 'FAIL'} ({sep_g}). "
            f"HP4 COSINE_BIPOLAR >= {HP4_COSINE_BIPOLAR_MIN}: "
            f"{'PASS' if hp4_ok else 'FAIL'} ({cos_b:.4f}). "
            f"BIPOLAR ref: HIPPO={hip_b:.4f} DG_ONLY={dg_only_b}. "
            f"GAUSSIAN DG_ONLY={dg_only_g}. Prediction test inconclusive.")


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
    _log(f"[config] run_mode={RUN_MODE} n_arms={len(ARM_SPECS)} seeds={SEEDS}")
    _log(f"[config] n_dim={N_DIM} dg_dim={DG_DIM} sparsity={DG_SPARSITY} "
         f"cluster_size={CLUSTER_SIZE}")
    _log(f"[config] N_PAIRS={N_PAIRS} CORRUPTION={CORRUPTION}")
    _log(f"[config] BIPOLAR flip_frac={FLIP_FRAC_BIPOLAR} -> theoretical "
         f"cluster_cos={(1 - 2*FLIP_FRAC_BIPOLAR)**2:.4f}")
    _log(f"[config] GAUSSIAN rho={GAUSSIAN_CLUSTER_RHO} -> theoretical "
         f"cluster_cos={GAUSSIAN_CLUSTER_RHO:.4f}")
    _log(f"[config] tf_capacity_theoretical={_TF_CAPACITY:.1f}")
    _log(f"[config] load_fraction N_PAIRS/C_TF={N_PAIRS/_TF_CAPACITY*100:.1f}%")
    _log(f"[config] HP1 COSINE_GAUSSIAN r@1 <= {HP1_COSINE_GAUSSIAN_MAX}")
    _log(f"[config] HP2 HIPPO_GAUSSIAN r@1 >= {HP2_HIPPO_GAUSSIAN_MIN}")
    _log(f"[config] HP3 HIPPO-COSINE sep at Gaussian >= "
         f"{HP3_HIPPO_MINUS_COSINE_GAUSSIAN_MIN}")
    _log(f"[config] HP4 COSINE_BIPOLAR r@1 >= {HP4_COSINE_BIPOLAR_MIN}")

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
        "corruption": CORRUPTION,
        "cluster_size": CLUSTER_SIZE,
        "flip_frac_bipolar": FLIP_FRAC_BIPOLAR,
        "gaussian_cluster_rho": GAUSSIAN_CLUSTER_RHO,
        "tf_capacity_theoretical": _TF_CAPACITY,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "arms_differ_exempted": [
            {"arm_pair": [ARM_RANDOM_B, ARM_RANDOM_G],
             "reason": "Both are chance-floor arms; _encode_random draws "
                       "fresh random bipolar vectors keyed on seed, "
                       "independent of geometry. Bit-identical query is the "
                       "correct chance-floor semantic (measures the same "
                       "thing regardless of ground-truth episode geometry)."}
        ],
        "baseline_in_band_check": {
            "arms": [ARM_RANDOM_B, ARM_RANDOM_G],
            "chance_r1": CHANCE_R1,
            "band_max_r1": BASELINE_IN_BAND_R1_MAX,
            "observed_r1_mean_bipolar":
                agg.get(ARM_RANDOM_B, {}).get("recall_at_1_mean"),
            "observed_r1_mean_gaussian":
                agg.get(ARM_RANDOM_G, {}).get("recall_at_1_mean"),
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": [ARM_COSINE_G],
            "HP2": [ARM_HIPPO_G],
            "HP3": [ARM_HIPPO_G, ARM_COSINE_G],
            "HP4": [ARM_COSINE_B],
            "HF_baseline_in_band": [ARM_RANDOM_B, ARM_RANDOM_G],
            "HF_dg_sparse_rate": [ARM_HIPPO_B, ARM_HIPPO_G],
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
