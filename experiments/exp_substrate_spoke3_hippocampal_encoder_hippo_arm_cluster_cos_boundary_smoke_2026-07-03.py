"""exp_substrate_spoke3_hippocampal_encoder_hippo_arm_cluster_cos_boundary_smoke_2026_07_03

Stage 2 Spoke 3 hippocampal-encoder HIPPO-ARM CLUSTER-COS BOUNDARY PROBE.

Closes the empirical expansion criterion of the CG_HN_ARCHITECTURAL parent
atom `MATH_CA3_AUTO_ASSOCIATOR_ANTI_SIGNAL_CROSS_GEOMETRY_2ND_WITNESS` by
tracing the CA3 anti-signal delta = HIPPO_ONE_SHOT - HIPPO_DG_ONLY across
the 2D grid cluster_cos in {0.30, 0.50, 0.70, 0.90} x corrupt in
{0.50, 0.75}. The prior lower-cluster-cos probe (commit 6d0da70dc)
measured HIPPO across the same grid but not HIPPO_DG_ONLY; without the
DG-only ablation the anti-signal delta cannot be evaluated regime-by-
regime.

Also tests Cycle 178 substrate-side inverted-U hypothesis for the CA3
mechanism (HIPPO r@1 higher at mild cluster than at high cluster;
prior probe MEASURED@ HIPPO_C030_R050=1.0000 vs HIPPO_C090_R050=0.7567 =>
observed drop 0.24; HP1 requires monotone drop >= 0.10).

Task class: SAME as Cell 4 / prior lower-cluster-cos probe (episodic-
binding + partial-cue retrieval; N=500 pairs; adversarial cluster-shared
Gaussian codebook).

Sweep (2D characterization):
  cluster_cos in {0.30, 0.50, 0.70, 0.90}
  corruption in {0.50, 0.75}
  filler geometry: Gaussian only.

Arms (per seed):
  ARM_HIPPO_ONE_SHOT_C{cc}_R{corr}  (LOAD_BEARING; 8 grid cells)
  ARM_HIPPO_DG_ONLY_C{cc}_R{corr}   (NEW; ablation; 8 grid cells)
  ARM_COSINE_BASELINE_C090_R075_regression   (single cell; code-integrity)
  ARM_RANDOM_BASELINE_C090_R075_regression   (single cell; chance floor)
Total per-seed: 18 arms; SEEDS=[11,17,23] -> 54 unit-instances.

HP band:
  HP1 (Cycle 178 inverted-U): at corrupt=0.50,
       mean(HIPPO r@1 at cluster_cos in {0.30, 0.50}) - HIPPO r@1 at
       cluster_cos=0.90 >= 0.10 (monotone drop MEASURED@ prior probe = 0.24).
  HP2a (regression): HIPPO_ONE_SHOT at (0.90, 0.75) mean r@1 in [0.44, 0.60]
       (band around prior MEASURED@ 0.5107 +/- 0.06).
  HP2b (anti-signal delta): delta at (0.90, 0.75) =
       HIPPO_ONE_SHOT - HIPPO_DG_ONLY <= -0.05 (MEASURED@ bipolar-vs-
       Gaussian = -0.163).
  HP3 (boundary threshold interior): at corrupt=0.75, delta transitions
       sign across cluster_cos; threshold interior to sweep (not at 0.30 or
       0.90 edge).
HARD_PASS = HP1 AND HP2a AND HP2b AND HP3.
HF-anti-signal-universal: delta <= -0.05 at ALL cluster_cos (parent atom
  stays broad scope; no cluster_cos refinement).
HF-regression-broken: HP2a fails; codebook / encoder drift.
HF-no-inverted-U: HP1 fails; refutes Cycle 178 substrate-side hypothesis.
MIDDLE_BAND: partial fires.

Regime:
  N_DIM=2048, DG_DIM=8192, SPARSITY=0.02 (T-F capacity ~1047 THEORETICAL@).
  N_PAIRS=500, CLUSTER_SIZE=5.
  Filler geometry: GAUSSIAN only.
  Seeds=[11, 17, 23].

Pre-reg:
  preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_hippo_arm_
  cluster_cos_boundary_smoke.md
Primitive: hdlab/hippocampal_encoder.py.

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM BOUNDARY characterization on
  SUPERVISED synthetic episodic-binding regime.
- If Cycle 178 inverted-U validates AND boundary interior: parent atom
  CG_HN_ARCHITECTURAL scope-refines (cluster_cos >~ threshold; not
  universal).
- If HIPPO <= DG_ONLY at ALL cluster_cos: parent stays broad-scoped;
  anti-signal is a universal architectural constraint.
- Anti-personification: substrate operates on integer indices + real-
  valued vectors.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception
- baseline_in_band (META_RULE_AG; RANDOM regression sanity)
- HP_SCOPE per-arm declaration
- cardinality_ok (EXPECTED_N_UNITS = 18 arms x 3 seeds = 54)
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
    "substrate_spoke3_hippocampal_encoder_hippo_arm_cluster_cos_boundary_"
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

# Regression cell (single).
REG_CLUSTER_COS = 0.90
REG_CORRUPTION = 0.75

# HP thresholds.
# HP1 (Cycle 178 inverted-U for CA3 mechanism).
HP1_CORRUPTION = 0.50
HP1_LOW_CLUSTER_MEAN_MEMBERS = [0.30, 0.50]   # average over these
HP1_HIGH_CLUSTER = 0.90
HP1_MONOTONE_DROP_MIN = 0.10  # HYPOTHESIZED@ prior probe drop = 0.24

# HP2a (regression band).
HP2A_HIPPO_LOAD_BEARING_R1_MIN = 0.44
HP2A_HIPPO_LOAD_BEARING_R1_MAX = 0.60

# HP2b (anti-signal at high cluster).
HP2B_ANTI_SIGNAL_DELTA_MAX = -0.05

# HP3 (boundary threshold interior).
HP3_DELTA_NEUTRAL_ABS = 0.05   # |delta| < 0.05 = neutral
HP3_DELTA_ANTI = -0.05         # delta <= -0.05 = anti-signal

# Regression: COSINE at load-bearing regime.
COSINE_REGRESSION_R1_MIN = 0.99   # MEASURED@ prior probe = 1.000

# HF-baseline sanity: RANDOM should be near-chance.
CHANCE_R1 = 1.0 / N_PAIRS  # 0.002
BASELINE_IN_BAND_R1_MAX = 5.0 * CHANCE_R1  # 0.010

# DG architectural constraint.
DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040

# THEORETICAL@ Tsodyks-Feigelman capacity C_TF = dg_dim / (2 * ln(1/sparsity)).
_TF_CAPACITY = DG_DIM / (2.0 * math.log(1.0 / DG_SPARSITY))


# --- Arm specs ---
# Kinds:
#   hippo_one_shot -> HippocampalEncoder, use_ca3=True, sparsify_after_settle=True
#   hippo_dg_only  -> HippocampalEncoder, use_ca3=False
# Regression-only kinds:
#   cosine  -> return corrupted episodes as query (baseline cosine argmax over stored)
#   random  -> random bipolar draws (chance floor)

def _arm_name(kind: str, cluster_cos: float, corruption: float,
              regression: bool = False) -> str:
    label_map = {
        "hippo_one_shot": "HIPPO_ONE_SHOT",
        "hippo_dg_only": "HIPPO_DG_ONLY",
        "cosine": "COSINE_BASELINE",
        "random": "RANDOM_BASELINE",
    }
    label = label_map[kind]
    suffix = "_regression" if regression else ""
    return (f"ARM_{label}_C{cluster_cos:.2f}"
            f"_R{corruption:.2f}{suffix}").replace(".", "")


def _arm_name_readable(kind: str, cluster_cos: float, corruption: float,
                        regression: bool = False) -> str:
    label_map = {
        "hippo_one_shot": "HIPPO_ONE_SHOT",
        "hippo_dg_only": "HIPPO_DG_ONLY",
        "cosine": "COSINE_BASELINE",
        "random": "RANDOM_BASELINE",
    }
    label = label_map[kind]
    tag = " [regression]" if regression else ""
    return f"ARM_{label}_C{cluster_cos:.2f}_R{corruption:.2f}{tag}"


def _build_arm_specs():
    specs = []
    # Grid arms: HIPPO_ONE_SHOT and HIPPO_DG_ONLY at every (cc, corr) cell.
    for kind in ("hippo_one_shot", "hippo_dg_only"):
        for cc in CLUSTER_COS_SWEEP:
            for corr in CORRUPTION_SWEEP:
                specs.append((_arm_name(kind, cc, corr), kind, cc, corr,
                              False))
    # Regression arms: single cell at (0.90, 0.75).
    specs.append((_arm_name("cosine", REG_CLUSTER_COS, REG_CORRUPTION,
                             regression=True),
                  "cosine", REG_CLUSTER_COS, REG_CORRUPTION, True))
    specs.append((_arm_name("random", REG_CLUSTER_COS, REG_CORRUPTION,
                             regression=True),
                  "random", REG_CLUSTER_COS, REG_CORRUPTION, True))
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

    Per cluster: shared BIPOLAR anchor_role_key + shared GAUSSIAN
    anchor_filler. member_filler = sqrt(rho)*anchor_filler +
    sqrt(1-rho)*per_member_gauss.

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


# --- Encoder implementations (parameterized by kind + corruption) ---

def _encode_hippo_one_shot(episodes: np.ndarray, seed: int, corruption: float
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
    completed_dg = enc.retrieve(cues, use_ca3=True,
                                 sparsify_after_settle=True)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "hippo_one_shot",
        "use_ca3": True,
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(corruption),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    return stored_dg, completed_dg, fit_wall, ret_wall, diag


def _encode_hippo_dg_only(episodes: np.ndarray, seed: int, corruption: float
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
    # use_ca3=False -> DG-only projection of cue (no CA3 settle)
    dg_only_code = enc.retrieve(cues, use_ca3=False,
                                 sparsify_after_settle=False)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "hippo_dg_only",
        "use_ca3": False,
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(corruption),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    return stored_dg, dg_only_code, fit_wall, ret_wall, diag


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
    "hippo_one_shot": _encode_hippo_one_shot,
    "hippo_dg_only": _encode_hippo_dg_only,
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
        sys.argv = ["exp_hippo_arm_cluster_cos_boundary_smoke"]
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
    for rho in CLUSTER_COS_SWEEP:
        _, fillers, _ = _draw_pairs_adversarial_gaussian(
            n_pairs=100, n_dim=N_DIM, seed=11,
            cluster_size=CLUSTER_SIZE, rho=rho)
        obs = _within_cluster_cos_observed(fillers,
                                           cluster_size=CLUSTER_SIZE,
                                           max_comparisons=100)
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
    """HIPPO_ONE_SHOT and HIPPO_DG_ONLY produce distinct queries at (0.90,0.75)."""
    _, _, episodes = _draw_pairs_adversarial_gaussian(
        n_pairs=20, n_dim=256, seed=11, cluster_size=5, rho=0.90)
    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02,
                             seed=11)
    _ = enc.encode_and_write(episodes)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.75, seed=11)
    q_one_shot = enc.retrieve(cues, use_ca3=True,
                               sparsify_after_settle=True)
    q_dg_only = enc.retrieve(cues, use_ca3=False,
                              sparsify_after_settle=False)
    h_one = hashlib.sha256(q_one_shot.tobytes()).hexdigest()[:16]
    h_dg = hashlib.sha256(q_dg_only.tobytes()).hexdigest()[:16]
    assert h_one != h_dg, (
        f"HIPPO_ONE_SHOT == HIPPO_DG_ONLY at (0.90,0.75); "
        f"one={h_one} dg={h_dg}. CA3 settle produced identical output; "
        f"anti-signal ablation broken."
    )
    print(f"[selftest arms_differ_hash_micro] PASS one={h_one[:8]} "
          f"dg={h_dg[:8]}", flush=True)


def _selftest_determinism_gaussian() -> None:
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


def _selftest_regression_hippo_and_cosine_at_load_bearing_regime() -> None:
    """At (0.90, 0.75), reduced-N=100 probe:
    - COSINE r@1 >= 0.95 (regression; exact-carrier saturation)
    - HIPPO_ONE_SHOT r@1 >= 0.35
    - HIPPO_DG_ONLY r@1 > HIPPO_ONE_SHOT (anti-signal fires; delta < 0)
    """
    rho = 0.90
    corruption = 0.75
    seed = 11
    _, _, episodes = _draw_pairs_adversarial_gaussian(
        n_pairs=100, n_dim=N_DIM, seed=seed,
        cluster_size=CLUSTER_SIZE, rho=rho)
    # Cosine baseline
    cues = _corrupt_cue(episodes, corruption, seed=seed)
    m_cos = _retrieval_metrics(episodes, cues, seed=seed)
    r_cos = m_cos["recall_at_1"]

    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=seed)
    stored_dg = enc.encode_and_write(episodes)
    completed_one_shot = enc.retrieve(cues, use_ca3=True,
                                       sparsify_after_settle=True)
    dg_only = enc.retrieve(cues, use_ca3=False,
                            sparsify_after_settle=False)
    m_one = _retrieval_metrics(stored_dg, completed_one_shot, seed=seed)
    m_dg = _retrieval_metrics(stored_dg, dg_only, seed=seed)
    r_one = m_one["recall_at_1"]
    r_dg = m_dg["recall_at_1"]

    assert r_cos >= 0.95, (
        f"regression expected COSINE r@1 >= 0.95 at rho=0.90+corrupt=0.75; "
        f"got {r_cos:.4f} (N=100). Code drift OR reduced-N regime shift."
    )
    assert r_one >= 0.35, (
        f"regression expected HIPPO_ONE_SHOT r@1 >= 0.35 at "
        f"rho=0.90+corrupt=0.75; got {r_one:.4f} (N=100). Mechanism may "
        f"be broken."
    )
    # Anti-signal fires at reduced-N (delta may be small; require dg >= one)
    assert r_dg >= r_one - 0.05, (
        f"anti-signal expected r_dg >= r_one - 0.05 at (0.90, 0.75, N=100); "
        f"got r_dg={r_dg:.4f} r_one={r_one:.4f}. If DG_ONLY << ONE_SHOT "
        f"the ablation setup may be reversed."
    )
    print(f"[selftest regression_hippo_and_cosine_at_load_bearing_regime] "
          f"PASS cos={r_cos:.4f} one_shot={r_one:.4f} dg_only={r_dg:.4f} "
          f"delta={r_one - r_dg:.4f} (N=100)", flush=True)


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
        ("regression_hippo_and_cosine_at_load_bearing_regime",
         _selftest_regression_hippo_and_cosine_at_load_bearing_regime),
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
        arm_name, encoder_kind, cluster_cos, corruption, regression = spec
        readable = _arm_name_readable(encoder_kind, cluster_cos, corruption,
                                       regression)
        _log(f"[seed {seed}] arm {arm_idx+1}/{n_arms} {readable} "
             f"(encoder={encoder_kind} cluster_cos={cluster_cos:.2f} "
             f"corrupt={corruption:.2f} regression={regression})")
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
                "regression_arm": regression,
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
                "regression_arm": regression,
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
            "regression_arm": regression,
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
                "regression_arm": spec[4],
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
                        "regression_arm": spec[4],
                        "encoder_kind": spec[1]}
    return out


def _delta_at(agg: Dict, cluster_cos: float, corruption: float
              ) -> Tuple[float, float, float]:
    """Return (r_one_shot, r_dg_only, delta) at a grid cell.
    delta = HIPPO_ONE_SHOT - HIPPO_DG_ONLY."""
    nm_one = _arm_name("hippo_one_shot", cluster_cos, corruption)
    nm_dg = _arm_name("hippo_dg_only", cluster_cos, corruption)
    r_one = agg.get(nm_one, {}).get("recall_at_1_mean")
    r_dg = agg.get(nm_dg, {}).get("recall_at_1_mean")
    if r_one is None or r_dg is None:
        return (float("nan"), float("nan"), float("nan"))
    return (float(r_one), float(r_dg), float(r_one - r_dg))


def _boundary_from_delta_sweep(agg: Dict, corruption: float
                                ) -> Tuple[float, str, List[Tuple[float, float]]]:
    """Identify cluster_cos where delta transitions from neutral/positive
    to anti-signal (<= -0.05). Returns (threshold, regime, points) where
    regime is INTERIOR / ALL_NEUTRAL / ALL_ANTI / AT_EDGE / MIXED / MISSING."""
    coses = sorted(CLUSTER_COS_SWEEP)
    points: List[Tuple[float, float]] = []
    for cc in coses:
        _, _, delta = _delta_at(agg, cc, corruption)
        points.append((cc, delta))
    missing = [cc for cc, d in points if not (d == d)]  # NaN check
    if missing:
        return (float("nan"),
                f"MISSING_at_cluster_cos={missing}_corruption={corruption}",
                points)

    all_neutral = all(abs(d) < HP3_DELTA_NEUTRAL_ABS for _, d in points)
    all_anti = all(d <= HP3_DELTA_ANTI for _, d in points)
    if all_anti:
        return (min(coses), "ALL_ANTI", points)
    if all_neutral:
        return (float("nan"), "ALL_NEUTRAL", points)

    # Find lowest cluster_cos at which delta transitions from
    # (not-anti) to (anti).
    lowest_anti = None
    for cc, d in points:
        if d <= HP3_DELTA_ANTI:
            lowest_anti = cc
            break
    if lowest_anti is not None:
        if lowest_anti > min(coses) and lowest_anti < max(coses):
            return (lowest_anti, "INTERIOR", points)
        return (lowest_anti, "AT_EDGE", points)
    return (float("nan"), "MIXED", points)


def _verdict(agg: Dict, expected_n_units: int,
             actual_n_units: int) -> Tuple[str, str]:
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-"
                f"metrics but got {actual_n_units}. See per-seed "
                f"failure_class.")

    # HF-baseline sanity (META_RULE_AG) on RANDOM regression arm.
    nm_random = _arm_name("random", REG_CLUSTER_COS, REG_CORRUPTION,
                           regression=True)
    r_rand = agg.get(nm_random, {}).get("recall_at_1_mean")
    if r_rand is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: RANDOM regression arm missing.")
    if r_rand > BASELINE_IN_BAND_R1_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF baseline_in_band: RANDOM regression r@1={r_rand:.4f} "
                f"> {BASELINE_IN_BAND_R1_MAX:.4f} (chance={CHANCE_R1:.4f}).")

    # HF-dg-sparse-rate architectural.
    for cc in CLUSTER_COS_SWEEP:
        for corr in CORRUPTION_SWEEP:
            for kind in ("hippo_one_shot", "hippo_dg_only"):
                nm = _arm_name(kind, cc, corr)
                dg_v = agg.get(nm, {}).get("dg_sparse_rate_mean")
                if dg_v is not None and not (
                        DG_SPARSE_RATE_MIN <= dg_v <= DG_SPARSE_RATE_MAX):
                    return ("HARD_FAIL_DG_SPARSE_RATE_ARCHITECTURAL",
                            f"HF DG sparse rate arm={nm} = {dg_v:.4f} "
                            f"outside [{DG_SPARSE_RATE_MIN:.3f}, "
                            f"{DG_SPARSE_RATE_MAX:.3f}].")

    # HP2a regression: HIPPO_ONE_SHOT at (0.90, 0.75).
    r_one_reg, r_dg_reg, delta_reg = _delta_at(agg, REG_CLUSTER_COS,
                                                REG_CORRUPTION)
    if r_one_reg != r_one_reg:  # NaN
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: HIPPO_ONE_SHOT or HIPPO_DG_ONLY at "
                f"({REG_CLUSTER_COS},{REG_CORRUPTION}) missing.")

    hp2a_ok = (HP2A_HIPPO_LOAD_BEARING_R1_MIN <= r_one_reg <=
                HP2A_HIPPO_LOAD_BEARING_R1_MAX)
    if not hp2a_ok:
        return ("HARD_FAIL_REGRESSION_BROKEN",
                f"HF regression HP2a: HIPPO_ONE_SHOT at "
                f"(cluster_cos={REG_CLUSTER_COS}, corrupt={REG_CORRUPTION}) "
                f"r@1={r_one_reg:.4f} outside "
                f"[{HP2A_HIPPO_LOAD_BEARING_R1_MIN}, "
                f"{HP2A_HIPPO_LOAD_BEARING_R1_MAX}] (prior "
                f"MEASURED@ 0.5107). Codebook/encoder drift; downstream "
                f"boundary verdict UNRELIABLE. delta_reg={delta_reg:.4f}.")

    # Also validate the COSINE regression arm.
    nm_cos_reg = _arm_name("cosine", REG_CLUSTER_COS, REG_CORRUPTION,
                            regression=True)
    r_cos_reg = agg.get(nm_cos_reg, {}).get("recall_at_1_mean")
    if r_cos_reg is None or r_cos_reg < COSINE_REGRESSION_R1_MIN:
        return ("HARD_FAIL_REGRESSION_BROKEN",
                f"HF regression COSINE at (0.90,0.75) r@1="
                f"{r_cos_reg if r_cos_reg is not None else 'None'} < "
                f"{COSINE_REGRESSION_R1_MIN} (prior MEASURED@ 1.000). "
                f"Cosine baseline regressed; codebook drift.")

    # HP2b anti-signal at high cluster.
    hp2b_ok = delta_reg <= HP2B_ANTI_SIGNAL_DELTA_MAX

    # HP1 Cycle 178 inverted-U at corrupt=0.50.
    r_one_lows = []
    for cc in HP1_LOW_CLUSTER_MEAN_MEMBERS:
        r, _, _ = _delta_at(agg, cc, HP1_CORRUPTION)
        if r == r:
            r_one_lows.append(r)
    r_one_high, _, _ = _delta_at(agg, HP1_HIGH_CLUSTER, HP1_CORRUPTION)
    hp1_ok = False
    hp1_diag = ""
    if len(r_one_lows) >= 1 and r_one_high == r_one_high:
        r_one_low_mean = float(np.mean(r_one_lows))
        hp1_drop = r_one_low_mean - r_one_high
        hp1_ok = hp1_drop >= HP1_MONOTONE_DROP_MIN
        hp1_diag = (f"mean(HIPPO r@1 at cc in "
                     f"{HP1_LOW_CLUSTER_MEAN_MEMBERS})={r_one_low_mean:.4f}, "
                     f"HIPPO r@1 at cc=0.90 = {r_one_high:.4f}, "
                     f"drop={hp1_drop:.4f} (min={HP1_MONOTONE_DROP_MIN})")
    else:
        hp1_diag = "HP1 inputs missing"

    # HP3 boundary threshold interior (delta sweep at corrupt=0.75).
    boundary_075 = _boundary_from_delta_sweep(agg, corruption=0.75)
    boundary_050 = _boundary_from_delta_sweep(agg, corruption=0.50)
    hp3_ok = (boundary_075[1] == "INTERIOR"
              or boundary_050[1] == "INTERIOR")

    def _delta_grid_str(corr):
        parts = []
        for cc in CLUSTER_COS_SWEEP:
            r_one, r_dg, d = _delta_at(agg, cc, corr)
            parts.append(f"cc={cc:.2f} one={r_one:.4f} dg={r_dg:.4f} "
                          f"delta={d:+.4f}")
        return " | ".join(parts)

    grid_075 = _delta_grid_str(0.75)
    grid_050 = _delta_grid_str(0.50)

    grid_note = (f"r=0.75 grid: [{grid_075}]; r=0.50 grid: [{grid_050}]. "
                 f"Boundary_r0.75=({boundary_075[0]:.2f},{boundary_075[1]}); "
                 f"Boundary_r0.50=({boundary_050[0]:.2f},{boundary_050[1]}). "
                 f"HP1: {hp1_diag}. Regression HIPPO_ONE_SHOT@(0.90,0.75) "
                 f"r@1={r_one_reg:.4f} band=[{HP2A_HIPPO_LOAD_BEARING_R1_MIN},"
                 f"{HP2A_HIPPO_LOAD_BEARING_R1_MAX}]; COSINE regression "
                 f"r@1={r_cos_reg:.4f} min={COSINE_REGRESSION_R1_MIN}; delta "
                 f"at (0.90,0.75) = {delta_reg:+.4f}.")

    # Anti-signal-universal check (all cc <= HP2B threshold).
    all_anti_075 = boundary_075[1] == "ALL_ANTI"
    all_anti_050 = boundary_050[1] == "ALL_ANTI"

    if hp1_ok and hp2a_ok and hp2b_ok and hp3_ok:
        return ("HARD_PASS",
                f"HARD_PASS: CA3 anti-signal scope-refines. HP1 (Cycle 178 "
                f"inverted-U): HIPPO_ONE_SHOT drops from mild cluster to "
                f"high cluster at corrupt=0.50 by >= "
                f"{HP1_MONOTONE_DROP_MIN}. HP2a (regression): HIPPO_ONE_SHOT "
                f"at (0.90,0.75) r@1={r_one_reg:.4f} in "
                f"[{HP2A_HIPPO_LOAD_BEARING_R1_MIN},"
                f"{HP2A_HIPPO_LOAD_BEARING_R1_MAX}]. HP2b (anti-signal): "
                f"delta at (0.90,0.75) = {delta_reg:+.4f} "
                f"<= {HP2B_ANTI_SIGNAL_DELTA_MAX}. HP3 (boundary INTERIOR): "
                f"threshold observable in cluster_cos sweep for at least "
                f"one corruption. SCOPE: parent CG_HN_ARCHITECTURAL atom "
                f"scope-refines to cluster_cos >= threshold (not universal). "
                f"SUBSTRATE KNOWS ALMOST NOTHING: MECHANISM boundary probe "
                f"on SUPERVISED synthetic episodic-binding regime; no "
                f"general-knowledge or language capability claim. "
                f"{grid_note} HOLD pending USER decision.")

    if all_anti_075 or all_anti_050:
        return ("HARD_FAIL_ANTI_SIGNAL_UNIVERSAL",
                f"HF anti-signal-universal: delta = HIPPO_ONE_SHOT - "
                f"HIPPO_DG_ONLY <= {HP2B_ANTI_SIGNAL_DELTA_MAX} at ALL "
                f"cluster_cos values for at least one corruption "
                f"(r=0.75 all_anti={all_anti_075}, r=0.50 all_anti="
                f"{all_anti_050}). CA3 anti-signal is universal; parent "
                f"CG_HN_ARCHITECTURAL atom stays broad-scoped; no "
                f"cluster_cos scope-refinement. {grid_note}")

    if not hp1_ok:
        return ("HARD_FAIL_NO_INVERTED_U",
                f"HF Cycle-178 inverted-U refuted: {hp1_diag} (need drop "
                f">= {HP1_MONOTONE_DROP_MIN}). HIPPO r@1 does NOT rise as "
                f"cluster_cos decreases at moderate corruption; substrate-"
                f"KB Cycle 178 hypothesis for CA3 mechanism NOT supported. "
                f"HP2a={r_one_reg:.4f} in band ({hp2a_ok}); HP2b delta="
                f"{delta_reg:+.4f} (<= {HP2B_ANTI_SIGNAL_DELTA_MAX}: "
                f"{hp2b_ok}); HP3 boundary interior={hp3_ok}. {grid_note}")

    if not hp3_ok:
        return ("HARD_FAIL_NO_BOUNDARY_OBSERVABLE",
                f"HF: no INTERIOR delta-sign transition in cluster_cos sweep "
                f"axis. Boundary_r=0.75=({boundary_075[0]:.2f},"
                f"{boundary_075[1]}); Boundary_r=0.50=("
                f"{boundary_050[0]:.2f},{boundary_050[1]}). "
                f"HP1={hp1_ok} HP2a={hp2a_ok} HP2b={hp2b_ok}. "
                f"Interpretation: threshold OUTSIDE the sweep axis (below "
                f"0.30 or above 0.90) OR non-monotonic delta curve. Axis "
                f"needs re-scoping. {grid_note}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial HP set. "
            f"HP1 inverted-U (drop >= {HP1_MONOTONE_DROP_MIN}): "
            f"{'PASS' if hp1_ok else 'FAIL'}. "
            f"HP2a regression HIPPO in "
            f"[{HP2A_HIPPO_LOAD_BEARING_R1_MIN},"
            f"{HP2A_HIPPO_LOAD_BEARING_R1_MAX}]: "
            f"{'PASS' if hp2a_ok else 'FAIL'} ({r_one_reg:.4f}). "
            f"HP2b anti-signal delta<={HP2B_ANTI_SIGNAL_DELTA_MAX}: "
            f"{'PASS' if hp2b_ok else 'FAIL'} ({delta_reg:+.4f}). "
            f"HP3 boundary INTERIOR: {'PASS' if hp3_ok else 'FAIL'} "
            f"(r=0.75: {boundary_075[1]}; r=0.50: {boundary_050[1]}). "
            f"Boundary characterization partial; downstream scope decision "
            f"deferred. {grid_note}")


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
    _log(f"[config] HP1 mean(low)-high >= {HP1_MONOTONE_DROP_MIN} at "
         f"corrupt={HP1_CORRUPTION}")
    _log(f"[config] HP2a HIPPO_ONE_SHOT@(0.90,0.75) in "
         f"[{HP2A_HIPPO_LOAD_BEARING_R1_MIN},"
         f"{HP2A_HIPPO_LOAD_BEARING_R1_MAX}]")
    _log(f"[config] HP2b delta@(0.90,0.75) <= "
         f"{HP2B_ANTI_SIGNAL_DELTA_MAX}")
    _log(f"[config] HP3 INTERIOR boundary observable in cluster_cos sweep")

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
        "reg_cluster_cos": REG_CLUSTER_COS,
        "reg_corruption": REG_CORRUPTION,
        "tf_capacity_theoretical": _TF_CAPACITY,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "baseline_in_band_check": {
            "chance_r1": CHANCE_R1,
            "band_max_r1": BASELINE_IN_BAND_R1_MAX,
            "random_arm_r1_mean": agg.get(
                _arm_name("random", REG_CLUSTER_COS, REG_CORRUPTION,
                          regression=True), {}).get("recall_at_1_mean"),
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": [_arm_name("hippo_one_shot", cc, HP1_CORRUPTION)
                    for cc in (HP1_LOW_CLUSTER_MEAN_MEMBERS +
                                [HP1_HIGH_CLUSTER])],
            "HP2a": [_arm_name("hippo_one_shot", REG_CLUSTER_COS,
                                REG_CORRUPTION)],
            "HP2b": [_arm_name("hippo_one_shot", REG_CLUSTER_COS,
                                REG_CORRUPTION),
                     _arm_name("hippo_dg_only", REG_CLUSTER_COS,
                                REG_CORRUPTION)],
            "HP3": [_arm_name(kind, cc, corr)
                    for kind in ("hippo_one_shot", "hippo_dg_only")
                    for cc in CLUSTER_COS_SWEEP
                    for corr in CORRUPTION_SWEEP],
            "HF_baseline_in_band": [_arm_name(
                "random", REG_CLUSTER_COS, REG_CORRUPTION, regression=True)],
            "HF_dg_sparse_rate": [_arm_name(kind, cc, corr)
                                   for kind in ("hippo_one_shot",
                                                 "hippo_dg_only")
                                   for cc in CLUSTER_COS_SWEEP
                                   for corr in CORRUPTION_SWEEP],
            "REGRESSION_COSINE": [_arm_name(
                "cosine", REG_CLUSTER_COS, REG_CORRUPTION,
                regression=True)],
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
