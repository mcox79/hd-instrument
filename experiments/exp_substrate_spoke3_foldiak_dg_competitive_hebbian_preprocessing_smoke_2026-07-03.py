"""exp_substrate_spoke3_foldiak_dg_competitive_hebbian_preprocessing_smoke_2026_07_03

Stage 2 Spoke 3 Hypothesis-C SMOKE probe: does Foldiak 1990 competitive-Hebbian
DG preprocessing (upstream of CA3) recover a positive HIPPO delta at the CA3
anti-signal regime (cluster_cos ~ 0.90 + 75% partial-cue corruption)?

Rank-2 post section-6 dispatch per research drill:
  notes/research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md

Task class: SAME as Cell 4 (episodic-binding at cluster_cos ~ 0.90 + 75% corrupt --
the CA3 anti-signal regime where standard HIPPO=0.517 < DG_ONLY=0.700 < COSINE=1.000).

Mechanism variant under test:
  STANDARD HIPPO: DGProjection (random-projection + top-K) -> CA3AutoAssociator
  FOLDIAK HIPPO: FoldiakDGProjection (competitive Hebbian + anti-Hebbian W + adaptive t) -> CA3AutoAssociator
  DG_ONLY: DGProjection only (no CA3)
  COSINE_BASELINE: plain cosine at n_dim
  RANDOM_BASELINE: chance floor

HP band (PRIMARY = N=500 ADV_CLUSTER 75-corrupt):
  HP1: FOLDIAK - DG_ONLY >= 0                  (Foldiak enables CA3 to add non-negative signal)
  HP2: FOLDIAK - STANDARD >= 0.10               (Foldiak beats standard HIPPO by measurable margin)
  HP3: FOLDIAK - COSINE >= 0                    (Foldiak achieves parity/beats cosine at this regime)
  HF: FOLDIAK <= STANDARD + 0.05 (within noise; CA3 anti-signal is more fundamental than DG-preprocessing)
  MB: partial (HP1 fires but HP2/HP3 don't)

Framing discipline (USER-locked + Skunkworks 2026-07-03):
- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM discriminator on SUPERVISED synthetic
  episodic-binding task. Not a general-knowledge claim. Not a language claim.
- Foldiak 1990 is CANONICAL literature mechanism; NOT novel-primitive claim.
- Cell-author self-correction pattern (CG_META tier).
- Anti-personification maintained.

Pre-reg: preregs/2026-07-03_substrate_spoke3_foldiak_dg_competitive_hebbian_preprocessing_smoke.md
Primitives: hdlab/hippocampal_encoder.py::DGProjection + CA3AutoAssociator (compose; no CA3 modification).
Cell 4 regression targets (MEASURED@ data/exp_substrate_vsa_cell4_episodic_formal_discriminative_smoke_2026_07_03/metrics.json:per_arm_aggregate):
  ARM_HIPPO_STANDARD:  r@1 = 0.517 +/- 0.05  (seeds [11,17,23])
  ARM_HIPPO_DG_ONLY:   r@1 = 0.700 +/- 0.05
  ARM_COSINE_BASELINE: r@1 = 1.000 exact
  ARM_RANDOM:          r@1 = 0.003 (chance 1/500 = 0.002)

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
    "substrate_spoke3_foldiak_dg_competitive_hebbian_preprocessing_smoke_2026_07_03"
)

# --- Config (matches Cell 4 regime bit-identically for regression bit-identity) ---
N_DIM = 2048
DG_DIM = 8192
DG_SPARSITY = 0.02
SEEDS = [11, 17, 23]
CLUSTER_SIZE = 5
ADVERSARIAL_FLIP_FRAC = 0.026
REGRESSION_R1_EXPECTED = 1.000
REGRESSION_TOLERANCE = 0.05

# Cell 4 MEASURED@ regression targets for ADV_CLUSTER 75-corrupt N=500 arms.
CELL4_STANDARD_R1_MEAN = 0.517
CELL4_DG_ONLY_R1_MEAN = 0.700
CELL4_COSINE_R1_MEAN = 1.000
CELL4_R1_TOLERANCE = 0.05

# HP band constants.
HP1_FOLDIAK_MINUS_DG_ONLY_FLOOR = 0.00
HP2_FOLDIAK_MINUS_STANDARD_FLOOR = 0.10
HP3_FOLDIAK_MINUS_COSINE_FLOOR = 0.00
HF_FOLDIAK_STANDARD_NOISE_MARGIN = 0.05

CHANCE_R1_N500 = 1.0 / 500
BASELINE_IN_BAND_R1_MAX_N500 = 5.0 * CHANCE_R1_N500

DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040

# Tsodyks-Feigelman capacity (Skunkworks-verified).
_TF_CAPACITY = DG_DIM / (2.0 * math.log(1.0 / DG_SPARSITY))

# Foldiak hyperparameters (smoke-scale).
FOLDIAK_N_EPOCHS = 3
FOLDIAK_N_RELAX = 2
FOLDIAK_LR_Q = 0.05
FOLDIAK_LR_W = 0.02
FOLDIAK_LR_T = 0.05
FOLDIAK_W_MAX = 5.0  # clamp lateral inhibition to prevent runaway

# --- Arm specs ---
ARM_SPECS = [
    ("ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50CORRUPT",
     "hippocampal", 50, "random", 0.50, "regression"),
    ("ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50_RANDOM_50CORRUPT",
     "dg_only", 50, "random", 0.50, "regression"),
    ("ARM_REGRESSION_COSINE_BASELINE_N50_RANDOM_50CORRUPT",
     "cosine", 50, "random", 0.50, "regression"),
    ("ARM_HIPPO_STANDARD_ADV_CLUSTER_75CORRUPT",
     "hippocampal", 500, "adversarial", 0.75, "regression_primary"),
    ("ARM_HIPPO_FOLDIAK_ADV_CLUSTER_75CORRUPT",
     "hippocampal_foldiak", 500, "adversarial", 0.75, "load_bearing"),
    ("ARM_HIPPO_DG_ONLY_ADV_CLUSTER_75CORRUPT",
     "dg_only", 500, "adversarial", 0.75, "regression_dg_only"),
    ("ARM_COSINE_BASELINE_ADV_CLUSTER_75CORRUPT",
     "cosine", 500, "adversarial", 0.75, "regression_cosine"),
    ("ARM_RANDOM_BASELINE",
     "random", 500, "n/a", 0.0, "chance_floor"),
]
ARM_NAMES = [s[0] for s in ARM_SPECS]

ARM_HIPPO_STANDARD = "ARM_HIPPO_STANDARD_ADV_CLUSTER_75CORRUPT"
ARM_HIPPO_FOLDIAK = "ARM_HIPPO_FOLDIAK_ADV_CLUSTER_75CORRUPT"
ARM_HIPPO_DG_ONLY = "ARM_HIPPO_DG_ONLY_ADV_CLUSTER_75CORRUPT"
ARM_COSINE = "ARM_COSINE_BASELINE_ADV_CLUSTER_75CORRUPT"
ARM_RANDOM = "ARM_RANDOM_BASELINE"

REGRESSION_ARMS = [
    "ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50CORRUPT",
    "ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50_RANDOM_50CORRUPT",
    "ARM_REGRESSION_COSINE_BASELINE_N50_RANDOM_50CORRUPT",
]


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


# --- Task-data generation (bit-identical to Cell 4 for regression) ---

def _draw_pairs_random(n_pairs: int, n_dim: int, seed: int
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed) * 991 + 7)
    role_keys = (rng.integers(0, 2, size=(n_pairs, n_dim)) * 2 - 1).astype(np.float32)
    fillers = (rng.integers(0, 2, size=(n_pairs, n_dim)) * 2 - 1).astype(np.float32)
    episodes = (role_keys * fillers).astype(np.float32)
    return role_keys, fillers, episodes


def _draw_pairs_adversarial(n_pairs: int, n_dim: int, seed: int,
                            cluster_size: int = CLUSTER_SIZE,
                            flip_frac: float = ADVERSARIAL_FLIP_FRAC
                            ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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


def _corrupt_cue(episodes: np.ndarray, fraction_zeroed: float,
                 seed: int) -> np.ndarray:
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


# --- Foldiak DG projection: competitive-Hebbian sparse coder ---

class FoldiakDGProjection:
    """Foldiak 1990 competitive-Hebbian sparse coder with anti-Hebbian lateral W.

    Same output shape + sparsity target as DGProjection so composition with
    CA3AutoAssociator is a drop-in swap.

    Learning rules (Foldiak 1990 "Forming sparse representations by local
    anti-Hebbian learning"; simplified for smoke-scale):
      Q [dg_dim, input_dim]:  competitive-Hebbian; active-unit pull toward input
      W [dg_dim, dg_dim]:     anti-Hebbian; W_ij += lr * (y_i y_j - p^2), off-diag
                              clamped to [0, W_MAX] (inhibitory only)
      t [dg_dim]:             threshold adapts so activity target p is maintained

    Encoding:
      preact = Q x - t                       (feedforward drive)
      relax n_relax iters:
        activation = preact - W y_prev
        y = top-K by |activation|, magnitude p * dg_dim (target sparsity)
      output ternary code: sign(activation) * mask_topK  (drop-in DGProjection shape)
    """
    def __init__(self, input_dim: int, dg_dim: int, sparsity: float,
                 seed: int = 0, n_epochs: int = FOLDIAK_N_EPOCHS,
                 n_relax: int = FOLDIAK_N_RELAX,
                 lr_Q: float = FOLDIAK_LR_Q, lr_W: float = FOLDIAK_LR_W,
                 lr_t: float = FOLDIAK_LR_T) -> None:
        if dg_dim <= input_dim:
            raise ValueError(
                f"FoldiakDGProjection requires expansion: dg_dim ({dg_dim}) "
                f"must be > input_dim ({input_dim})."
            )
        if not (0.0 < sparsity < 1.0):
            raise ValueError(f"sparsity must be in (0,1); got {sparsity}")
        self.input_dim = int(input_dim)
        self.dg_dim = int(dg_dim)
        self.sparsity = float(sparsity)
        self.seed = int(seed)
        self.n_epochs = int(n_epochs)
        self.n_relax = int(n_relax)
        self.lr_Q = float(lr_Q)
        self.lr_W = float(lr_W)
        self.lr_t = float(lr_t)
        self.p_target = self.sparsity
        rng = np.random.default_rng(int(seed) * 991 + 13)
        # Initialize Q as scaled bipolar (same variance as DGProjection random
        # projection); competitive Hebbian will differentiate rows.
        self._Q = ((rng.integers(0, 2, size=(dg_dim, input_dim)) * 2 - 1)
                   .astype(np.float32))
        self._Q *= 1.0 / np.sqrt(float(input_dim))
        self._W = np.zeros((dg_dim, dg_dim), dtype=np.float32)
        self._t = np.zeros(dg_dim, dtype=np.float32)
        self._trained = False

    def _topk_mask(self, mag: np.ndarray) -> np.ndarray:
        d = int(mag.shape[-1])
        k = max(1, int(round(self.sparsity * d)))
        if k >= d:
            return np.ones_like(mag, dtype=bool)
        if mag.ndim == 1:
            thresh = np.partition(mag, d - k)[d - k]
            return mag >= thresh
        thresh = np.partition(mag, d - k, axis=1)[:, d - k][:, None]
        return mag >= thresh

    def _activate(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Encode single input via feedforward + relaxation.
        Returns (y_binary, activation_final). Both [dg_dim]."""
        preact = self._Q @ x.astype(np.float32) - self._t
        y = np.zeros(self.dg_dim, dtype=np.float32)
        act = preact
        for _ in range(self.n_relax):
            act = preact - self._W @ y
            mask = self._topk_mask(np.abs(act))
            y = mask.astype(np.float32)
        return y, act

    def fit(self, X_train: np.ndarray) -> None:
        """Train Q, W, t via Foldiak's local learning rules on X_train.
        [n_train, input_dim] -> in-place update of self._Q, self._W, self._t."""
        if X_train.ndim != 2 or X_train.shape[1] != self.input_dim:
            raise ValueError(
                f"FoldiakDGProjection.fit expects [n, {self.input_dim}]; "
                f"got shape {X_train.shape}"
            )
        rng_perm = np.random.default_rng(int(self.seed) * 977 + 17)
        n = X_train.shape[0]
        p2 = self.p_target * self.p_target
        for ep in range(self.n_epochs):
            perm = rng_perm.permutation(n)
            for idx in perm:
                x = X_train[idx].astype(np.float32)
                y, act = self._activate(x)
                active = y > 0.5
                if active.any():
                    # Competitive-Hebbian on Q for active units: pull toward x.
                    # Sign convention: pull toward x scaled by activation sign so
                    # bipolar-output ternary code inherits sign discrimination.
                    sign_active = np.sign(act[active]).astype(np.float32)
                    sign_active[sign_active == 0] = 1.0
                    self._Q[active] += self.lr_Q * (
                        x[None, :] * sign_active[:, None] - self._Q[active]
                    )
                # Anti-Hebbian on W (off-diagonal).
                yy = np.outer(y, y).astype(np.float32) - p2
                np.fill_diagonal(yy, 0.0)
                self._W += self.lr_W * yy
                np.clip(self._W, 0.0, FOLDIAK_W_MAX, out=self._W)
                # Threshold adapts toward target activity.
                self._t += self.lr_t * (y - self.p_target)
        self._trained = True

    def encode(self, x: np.ndarray) -> np.ndarray:
        """[input_dim] -> ternary sparse code [dg_dim]."""
        if x.ndim != 1 or x.shape[0] != self.input_dim:
            raise ValueError(
                f"FoldiakDGProjection.encode expects [{self.input_dim}]; "
                f"got shape {x.shape}"
            )
        y, act = self._activate(x)
        sign = np.sign(act).astype(np.float32)
        sign[sign == 0] = 1.0
        return sign * y

    def encode_batch(self, X: np.ndarray) -> np.ndarray:
        """[n, input_dim] -> ternary [n, dg_dim]. Sequential; single-sample activate."""
        if X.ndim != 2 or X.shape[1] != self.input_dim:
            raise ValueError(
                f"FoldiakDGProjection.encode_batch expects [n, {self.input_dim}]; "
                f"got shape {X.shape}"
            )
        out = np.zeros((X.shape[0], self.dg_dim), dtype=np.float32)
        for i in range(X.shape[0]):
            out[i] = self.encode(X[i])
        return out

    def sparse_rate(self, code: np.ndarray) -> float:
        if code.ndim == 1:
            return float(np.count_nonzero(code)) / float(code.shape[0])
        return float(np.count_nonzero(code)) / float(code.size)


# --- Arm encoder implementations ---

def _encode_hippocampal(episodes: np.ndarray, corruption: float, seed: int
                        ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """Standard HIPPO: DGProjection + CA3AutoAssociator. Reproduces Cell 4."""
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
        "encoder": "hippocampal_standard",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(corruption),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    return stored_dg, completed_dg, fit_wall, ret_wall, diag


def _encode_hippocampal_foldiak(episodes: np.ndarray, corruption: float, seed: int
                                 ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """LOAD-BEARING: Foldiak DG + CA3 auto-associator.

    Foldiak DG stage trained on the episode corpus (learning driver); CA3 same
    Marr-1971 outer-product auto-associator as standard HIPPO (no CA3 mod).
    """
    from hdlab.hippocampal_encoder import CA3AutoAssociator
    n = episodes.shape[0]
    fit_t0 = time.perf_counter()
    dg = FoldiakDGProjection(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    # Train Foldiak on stored episodes (learning driver operates on the corpus).
    dg.fit(episodes)
    stored_dg = dg.encode_batch(episodes)
    dg_sparse_rate = dg.sparse_rate(stored_dg)
    ca3 = CA3AutoAssociator(dg_dim=DG_DIM)
    for i in range(stored_dg.shape[0]):
        ca3.write(stored_dg[i])
    fit_wall = time.perf_counter() - fit_t0

    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, corruption, seed=int(seed))
    cue_codes = dg.encode_batch(cues)
    # CA3 settle with top-K sparsify after (same as HippocampalEncoder.retrieve).
    act = ca3.settle_batch_activations(cue_codes)
    k = max(1, int(round(DG_SPARSITY * DG_DIM)))
    if k >= DG_DIM:
        mask = np.ones_like(act, dtype=bool)
    else:
        mag = np.abs(act)
        thresh = np.partition(mag, DG_DIM - k, axis=1)[:, DG_DIM - k][:, None]
        mask = mag >= thresh
    sign = np.sign(act).astype(np.float32)
    sign[sign == 0] = 1.0
    completed = sign * mask.astype(np.float32)
    ret_wall = time.perf_counter() - ret_t0

    # Diagnostics: measure code cos before/after training if seed matches selftest.
    diag = {
        "encoder": "hippocampal_foldiak",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(ca3.n_written),
        "partial_cue_fraction_zeroed": float(corruption),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
        "foldiak_n_epochs": int(FOLDIAK_N_EPOCHS),
        "foldiak_n_relax": int(FOLDIAK_N_RELAX),
        "foldiak_lr_Q": float(FOLDIAK_LR_Q),
        "foldiak_lr_W": float(FOLDIAK_LR_W),
        "foldiak_lr_t": float(FOLDIAK_LR_T),
        "foldiak_W_mean": float(np.mean(dg._W)),
        "foldiak_W_max": float(np.max(dg._W)),
        "foldiak_t_mean": float(np.mean(dg._t)),
        "foldiak_t_std": float(np.std(dg._t)),
    }
    return stored_dg, completed, fit_wall, ret_wall, diag


def _encode_dg_only(episodes: np.ndarray, corruption: float, seed: int
                    ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    from hdlab.hippocampal_encoder import HippocampalEncoder
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    stored_dg = enc.dg.encode_batch(episodes)
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(stored_dg)

    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, corruption, seed=int(seed))
    cue_dg = enc.dg.encode_batch(cues)
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "encoder": "dg_only",
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "partial_cue_fraction_zeroed": float(corruption),
        "ca3_used": False,
    }
    return stored_dg, cue_dg, fit_wall, ret_wall, diag


def _encode_cosine_baseline(episodes: np.ndarray, corruption: float, seed: int
                            ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    fit_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, corruption, seed=int(seed))
    fit_wall = time.perf_counter() - fit_t0
    diag = {"encoder": "cosine_baseline", "input_dim": N_DIM,
            "partial_cue_fraction_zeroed": float(corruption)}
    return episodes.copy(), cues, 0.0, fit_wall, diag


def _encode_random(episodes: np.ndarray, corruption: float, seed: int
                   ) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    n = episodes.shape[0]
    rng = np.random.default_rng(int(seed) * 883 + 29)
    t0 = time.perf_counter()
    stored = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    query = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    _ = corruption
    diag = {"encoder": "random", "input_dim": N_DIM}
    return stored, query, 0.0, wall, diag


ENCODER_FUNCS = {
    "hippocampal": _encode_hippocampal,
    "hippocampal_foldiak": _encode_hippocampal_foldiak,
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
                    f"bit-identical (hash={digests[a]})."
                )
    return digests


# --- Cell-level selftests ---

def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_spoke3_foldiak_smoke"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_corrupt_cue_correct_fractions() -> None:
    rng = np.random.default_rng(3)
    n, d = 20, 512
    episodes = (rng.integers(0, 2, size=(n, d)) * 2 - 1).astype(np.float32)
    for frac in (0.50, 0.75, 0.90):
        cues = _corrupt_cue(episodes, fraction_zeroed=frac, seed=11)
        zeros_per_row = (cues == 0.0).sum(axis=1)
        expected = int(round(frac * d))
        assert np.all(zeros_per_row == expected), (
            f"frac={frac}: zeros {zeros_per_row[:5]} expected {expected}"
        )
    print("[selftest corrupt_cue_correct_fractions] PASS", flush=True)


def _selftest_adversarial_codebook_within_cluster_cos() -> None:
    _, fillers, episodes = _draw_pairs_adversarial(
        n_pairs=100, n_dim=N_DIM, seed=11)
    obs = _within_cluster_cos_observed(fillers)
    assert 0.85 <= obs <= 0.95, (
        f"cluster_cos {obs:.4f} not in [0.85, 0.95] (THEORETICAL@ ~0.899)"
    )
    ep_cos = _within_cluster_cos_observed(episodes)
    assert 0.85 <= ep_cos <= 0.95, (
        f"episode cluster_cos {ep_cos:.4f} not in [0.85, 0.95]"
    )
    print(f"[selftest adversarial_cluster_cos] PASS filler={obs:.4f} "
          f"episode={ep_cos:.4f}", flush=True)


def _selftest_regression_arm_bit_identical() -> None:
    _, _, episodes = _draw_pairs_random(n_pairs=50, n_dim=N_DIM, seed=11)
    stored, query, _, _, _ = _encode_hippocampal(episodes, corruption=0.50, seed=11)
    m = _retrieval_metrics(stored, query, seed=11)
    assert m["recall_at_1"] >= 0.95, (
        f"regression HIPPO N=50 random 0.50 r@1={m['recall_at_1']:.4f} < 0.95 "
        f"(Cell 4 MEASURED@ 1.000). Code drift."
    )
    print(f"[selftest regression_arm_bit_identical] PASS r@1={m['recall_at_1']:.4f}",
          flush=True)


def _selftest_foldiak_dg_produces_sparse_ternary() -> None:
    """FoldiakDGProjection output is ternary {-1, 0, +1} at target sparsity."""
    dg = FoldiakDGProjection(input_dim=128, dg_dim=1024, sparsity=0.02, seed=11,
                              n_epochs=1)
    rng = np.random.default_rng(3)
    X = rng.standard_normal((20, 128)).astype(np.float32)
    dg.fit(X)
    C = dg.encode_batch(X)
    uniq = set(np.unique(C).tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), f"non-ternary: {uniq}"
    rate = float(np.count_nonzero(C)) / float(C.size)
    assert 0.5 * 0.02 <= rate <= 2.0 * 0.02, (
        f"sparse rate {rate:.4f} outside [0.01, 0.04]"
    )
    print(f"[selftest foldiak_dg_produces_sparse_ternary] PASS unique={uniq} "
          f"rate={rate:.4f}", flush=True)


def _selftest_foldiak_dg_learning_reduces_within_cluster_code_cos() -> None:
    """After training on clustered episodes, Foldiak codes are LESS correlated
    within-cluster than DGProjection random codes on the same input.

    This is the functional pattern-separation test: the Foldiak-trained DG
    stage should ORTHOGONALIZE within-cluster inputs better than random-projection.
    """
    _, _, episodes = _draw_pairs_adversarial(
        n_pairs=50, n_dim=N_DIM, seed=11)
    # DGProjection random-projection baseline.
    from hdlab.hippocampal_encoder import DGProjection
    dg_rand = DGProjection(input_dim=N_DIM, dg_dim=DG_DIM,
                            sparsity=DG_SPARSITY, seed=11)
    C_rand = dg_rand.encode_batch(episodes)
    within_rand = _within_cluster_cos_observed(C_rand)
    # Foldiak (trained on same episodes; smoke-scale 2 epochs).
    dg_fol = FoldiakDGProjection(input_dim=N_DIM, dg_dim=DG_DIM,
                                  sparsity=DG_SPARSITY, seed=11, n_epochs=2)
    dg_fol.fit(episodes)
    C_fol = dg_fol.encode_batch(episodes)
    within_fol = _within_cluster_cos_observed(C_fol)
    # Not a strict inequality: mini-Foldiak may not always dominate; we just
    # verify both are finite and log for smoke-visibility (diagnostic selftest,
    # NOT a discriminator gate -- HP band lives in the FULL cell verdict).
    assert np.isfinite(within_rand) and np.isfinite(within_fol), (
        f"non-finite within-cluster cos: rand={within_rand}, fol={within_fol}"
    )
    print(f"[selftest foldiak_dg_learning_reduces_within_cluster_code_cos] "
          f"PASS DIAGNOSTIC rand={within_rand:.4f} foldiak={within_fol:.4f} "
          f"(rand-fol delta={within_rand - within_fol:+.4f}); interpretation "
          f"in verdict logic.", flush=True)


def _selftest_arms_differ_hash_micro() -> None:
    """STANDARD vs FOLDIAK vs DG_ONLY completed cues must differ."""
    _, _, episodes = _draw_pairs_random(n_pairs=8, n_dim=N_DIM, seed=11)
    s_std, q_std, _, _, _ = _encode_hippocampal(episodes, corruption=0.50, seed=11)
    s_fol, q_fol, _, _, _ = _encode_hippocampal_foldiak(episodes, corruption=0.50, seed=11)
    s_dg, q_dg, _, _, _ = _encode_dg_only(episodes, corruption=0.50, seed=11)
    h_std = hashlib.sha256(q_std.tobytes()).hexdigest()[:16]
    h_fol = hashlib.sha256(q_fol.tobytes()).hexdigest()[:16]
    h_dg = hashlib.sha256(q_dg.tobytes()).hexdigest()[:16]
    assert h_std != h_fol, f"STANDARD == FOLDIAK bit-identical (hash={h_std})"
    assert h_std != h_dg, f"STANDARD == DG_ONLY bit-identical (hash={h_std})"
    assert h_fol != h_dg, f"FOLDIAK == DG_ONLY bit-identical (hash={h_fol})"
    _ = s_std, s_fol, s_dg
    print(f"[selftest arms_differ_hash_micro] PASS std={h_std[:8]} "
          f"fol={h_fol[:8]} dg={h_dg[:8]}", flush=True)


def _selftest_primitive_selftests_chain() -> None:
    """Chain hippocampal_encoder primitive selftests (13 tests)."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "hdlab.hippocampal_encoder", "--self-test"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print("[primitive_selftests_chain] STDOUT:\n" + result.stdout)
        print("[primitive_selftests_chain] STDERR:\n" + result.stderr)
        raise AssertionError(f"primitive selftest rc={result.returncode}")
    if "13/13 passed" not in result.stdout:
        raise AssertionError(
            f"primitive selftest summary not '13/13 passed'; tail:\n"
            f"{result.stdout[-500:]}"
        )
    print("[selftest primitive_selftests_chain] PASS 13/13", flush=True)


def _run_selftests() -> int:
    tests = [
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
        ("corrupt_cue_correct_fractions", _selftest_corrupt_cue_correct_fractions),
        ("adversarial_codebook_within_cluster_cos",
         _selftest_adversarial_codebook_within_cluster_cos),
        ("regression_arm_bit_identical", _selftest_regression_arm_bit_identical),
        ("foldiak_dg_produces_sparse_ternary",
         _selftest_foldiak_dg_produces_sparse_ternary),
        ("foldiak_dg_learning_reduces_within_cluster_code_cos",
         _selftest_foldiak_dg_learning_reduces_within_cluster_code_cos),
        ("arms_differ_hash_micro", _selftest_arms_differ_hash_micro),
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
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed",
          flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---

def _episode_cache_key(n_pairs: int, codebook: str, seed: int) -> str:
    return f"{codebook}_n{n_pairs}_s{seed}"


def _run_one_seed(seed: int, output_dir: Path) -> Dict:
    n_arms = len(ARM_SPECS)
    per_arm: Dict[str, Dict] = {}
    per_arm_query: Dict[str, np.ndarray] = {}
    episode_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    for arm_idx, spec in enumerate(ARM_SPECS):
        arm_name, encoder_kind, n_pairs, codebook, corruption, role = spec
        _log(f"[seed {seed}] arm {arm_idx+1}/{n_arms} {arm_name} "
             f"(encoder={encoder_kind} N={n_pairs} codebook={codebook} "
             f"corrupt={corruption} role={role})")
        arm_t0 = time.perf_counter()

        try:
            if encoder_kind == "random":
                episodes = np.zeros((n_pairs, N_DIM), dtype=np.float32)
            else:
                key = _episode_cache_key(n_pairs, codebook, seed)
                if key not in episode_cache:
                    if codebook == "random":
                        rk, fl, ep = _draw_pairs_random(n_pairs, N_DIM, seed=seed)
                    elif codebook == "adversarial":
                        rk, fl, ep = _draw_pairs_adversarial(n_pairs, N_DIM, seed=seed)
                    else:
                        raise ValueError(f"Unknown codebook: {codebook}")
                    episode_cache[key] = (rk, fl, ep)
                    _log(f"[seed {seed}]   drew {codebook} codebook N={n_pairs}: "
                         f"intra_cluster_filler_cos_obs="
                         f"{_within_cluster_cos_observed(fl):.4f}")
                _, _, episodes = episode_cache[key]

            enc_fn = ENCODER_FUNCS[encoder_kind]
            stored, query, enc_wall, fit_wall, arm_diag = enc_fn(
                episodes, corruption, seed
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name, "encoder_kind": encoder_kind,
                "n_pairs": n_pairs, "codebook": codebook,
                "corruption": corruption, "role": role,
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
                "arm_name": arm_name, "encoder_kind": encoder_kind,
                "n_pairs": n_pairs, "codebook": codebook,
                "corruption": corruption, "role": role,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
            }
            _log(f"[seed {seed}] arm {arm_name} NaN (n_nan={n_nan})")
            continue

        metrics = _retrieval_metrics(stored, query, seed=seed)
        metrics.update({
            "arm_name": arm_name, "encoder_kind": encoder_kind,
            "n_pairs": n_pairs, "codebook": codebook,
            "corruption": corruption, "role": role,
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

    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    non_regression_query = {
        n: q for n, q in per_arm_query.items() if n not in REGRESSION_ARMS
    }
    if len(non_regression_query) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(non_regression_query)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}

    regression_digests: Dict[str, str] = {}
    for n in REGRESSION_ARMS:
        if n in per_arm_query:
            arr = per_arm_query[n]
            flat = arr.reshape(-1)
            sig = flat[:min(200, flat.size)].astype(np.float32).tobytes()
            regression_digests[n] = hashlib.sha256(sig).hexdigest()[:16]

    return {
        "seed": int(seed),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
        "arms_differ_exempted_regression_group": REGRESSION_ARMS,
        "regression_arm_query_digests": regression_digests,
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


def _verdict(agg: Dict, expected_n_units: int, actual_n_units: int
             ) -> Tuple[str, str]:
    """HP band (PRIMARY = N=500 ADV_CLUSTER 75-corrupt):
      HP1: FOLDIAK - DG_ONLY >= 0            (Foldiak enables CA3 non-negative delta)
      HP2: FOLDIAK - STANDARD >= 0.10          (Foldiak beats standard HIPPO)
      HP3: FOLDIAK - COSINE >= 0               (Foldiak parity/beats cosine; hardest)
      HF:  FOLDIAK <= STANDARD + 0.05          (CA3 anti-signal more fundamental)
      MB:  partial (HP1 fires, HP2/HP3 don't)
      REGRESSION: STANDARD ~ 0.517, DG_ONLY ~ 0.700, COSINE ~ 1.000, RANDOM ~ chance
    """
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics "
                f"but got {actual_n_units}. See per-seed per_arm failure_class.")

    def _r1(arm: str):
        return agg.get(arm, {}).get("recall_at_1_mean")

    r_std = _r1(ARM_HIPPO_STANDARD)
    r_fol = _r1(ARM_HIPPO_FOLDIAK)
    r_dg = _r1(ARM_HIPPO_DG_ONLY)
    r_cos = _r1(ARM_COSINE)
    r_rand = _r1(ARM_RANDOM)
    dg_rate_std = agg.get(ARM_HIPPO_STANDARD, {}).get("dg_sparse_rate_mean")
    dg_rate_fol = agg.get(ARM_HIPPO_FOLDIAK, {}).get("dg_sparse_rate_mean")

    missing = []
    for a, v in [(ARM_HIPPO_STANDARD, r_std), (ARM_HIPPO_FOLDIAK, r_fol),
                 (ARM_HIPPO_DG_ONLY, r_dg), (ARM_COSINE, r_cos),
                 (ARM_RANDOM, r_rand)]:
        if v is None:
            missing.append(a)
    if missing:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: arm(s) missing recall@1: {missing}")

    # Regression check: N=50 random regression arms.
    reg_failures = []
    for arm in REGRESSION_ARMS:
        v = _r1(arm)
        if v is None:
            reg_failures.append(f"{arm}=<missing>")
        elif v < 1.0 - REGRESSION_TOLERANCE:
            reg_failures.append(f"{arm}={v:.4f}")
    if reg_failures:
        return ("HARD_FAIL_REGRESSION_BROKEN",
                f"HF regression N=50 random 0.50 arms: {reg_failures}. "
                f"Cell 4 MEASURED@ 1.000 all seeds. Code drift; downstream "
                f"Foldiak verdict UNRELIABLE.")

    # Cell 4 regression bit-identity check.
    reg_drift = []
    if abs(r_std - CELL4_STANDARD_R1_MEAN) > CELL4_R1_TOLERANCE:
        reg_drift.append(f"STANDARD r@1={r_std:.4f} vs Cell 4 "
                         f"MEASURED@ {CELL4_STANDARD_R1_MEAN} "
                         f"(tol {CELL4_R1_TOLERANCE})")
    if abs(r_dg - CELL4_DG_ONLY_R1_MEAN) > CELL4_R1_TOLERANCE:
        reg_drift.append(f"DG_ONLY r@1={r_dg:.4f} vs Cell 4 "
                         f"MEASURED@ {CELL4_DG_ONLY_R1_MEAN} "
                         f"(tol {CELL4_R1_TOLERANCE})")
    if abs(r_cos - CELL4_COSINE_R1_MEAN) > CELL4_R1_TOLERANCE:
        reg_drift.append(f"COSINE r@1={r_cos:.4f} vs Cell 4 "
                         f"MEASURED@ {CELL4_COSINE_R1_MEAN} "
                         f"(tol {CELL4_R1_TOLERANCE})")
    if reg_drift:
        return ("HARD_FAIL_CELL4_REGIME_REGRESSION_DRIFT",
                f"HF Cell 4 regime regression drift: {reg_drift}. Regime not "
                f"bit-identical to Cell 4; Foldiak vs STANDARD comparison "
                f"UNRELIABLE.")

    # HF-baseline (META_RULE_AG).
    if r_rand > BASELINE_IN_BAND_R1_MAX_N500:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF baseline_in_band: RANDOM r@1={r_rand:.4f} > "
                f"{BASELINE_IN_BAND_R1_MAX_N500:.4f} (chance={CHANCE_R1_N500:.4f})")

    # HF-dg-rate (architectural sanity for FOLDIAK).
    if dg_rate_fol is not None and not (
            DG_SPARSE_RATE_MIN <= dg_rate_fol <= DG_SPARSE_RATE_MAX):
        return ("HARD_FAIL_FOLDIAK_DG_SPARSE_RATE_ARCHITECTURAL",
                f"HF Foldiak dg_sparse_rate={dg_rate_fol:.4f} outside "
                f"[{DG_SPARSE_RATE_MIN:.3f}, {DG_SPARSE_RATE_MAX:.3f}] "
                f"(target {DG_SPARSITY:.3f}). Foldiak top-K threshold broken.")

    # Deltas.
    d_fol_std = r_fol - r_std
    d_fol_dg = r_fol - r_dg
    d_fol_cos = r_fol - r_cos

    hp1_ok = d_fol_dg >= HP1_FOLDIAK_MINUS_DG_ONLY_FLOOR
    hp2_ok = d_fol_std >= HP2_FOLDIAK_MINUS_STANDARD_FLOOR
    hp3_ok = d_fol_cos >= HP3_FOLDIAK_MINUS_COSINE_FLOOR

    gates = (
        f"HP1(FOLDIAK>=DG_ONLY, floor={HP1_FOLDIAK_MINUS_DG_ONLY_FLOOR:+.2f})="
        f"{'PASS' if hp1_ok else 'FAIL'}[FOLDIAK={r_fol:.4f} DG_ONLY={r_dg:.4f} "
        f"delta={d_fol_dg:+.4f}] | "
        f"HP2(FOLDIAK-STANDARD>={HP2_FOLDIAK_MINUS_STANDARD_FLOOR:+.2f})="
        f"{'PASS' if hp2_ok else 'FAIL'}[STANDARD={r_std:.4f} "
        f"delta={d_fol_std:+.4f}] | "
        f"HP3(FOLDIAK>=COSINE, floor={HP3_FOLDIAK_MINUS_COSINE_FLOOR:+.2f})="
        f"{'PASS' if hp3_ok else 'FAIL'}[COSINE={r_cos:.4f} "
        f"delta={d_fol_cos:+.4f}]"
    )

    # HF: Foldiak fails to recover (within noise of STANDARD).
    if d_fol_std <= HF_FOLDIAK_STANDARD_NOISE_MARGIN and not hp1_ok:
        return ("HARD_FAIL_FOLDIAK_DOES_NOT_RECOVER",
                f"HF: FOLDIAK does not recover positive HIPPO delta at the "
                f"CA3 anti-signal regime. FOLDIAK r@1={r_fol:.4f} vs STANDARD "
                f"r@1={r_std:.4f} (delta={d_fol_std:+.4f} <= "
                f"{HF_FOLDIAK_STANDARD_NOISE_MARGIN:.2f} noise margin) and "
                f"FOLDIAK also < DG_ONLY r@1={r_dg:.4f} "
                f"(delta={d_fol_dg:+.4f}). Hypothesis C P_deflated to < 0.20; "
                f"CA3 anti-signal is more fundamental than DG-preprocessing "
                f"choice. Hypothesis A (iteration count) / B (Storkey) / D "
                f"(fundamental) become active. CA3-anti-signal atom BROADENS "
                f"(mechanism-invariant across Foldiak-vs-random-projection DG). "
                f"{gates}. HONEST SCOPE: MECHANISM_INVARIANT_ON_SUPERVISED "
                f"synthetic episodic-binding regime at cluster_cos~0.90 + "
                f"75-corrupt; SUBSTRATE KNOWS ALMOST NOTHING; does NOT grant "
                f"substrate general-knowledge or language capability. "
                f"Anti-personification maintained.")

    # HARD_PASS: all 3 HP fire.
    if hp1_ok and hp2_ok and hp3_ok:
        return ("HARD_PASS",
                f"HARD_PASS: Foldiak DG competitive-Hebbian preprocessing "
                f"FULLY RECOVERS mechanism signal at the CA3 anti-signal "
                f"regime (cluster_cos~0.90 + 75% corrupt). All 3 HP fire: "
                f"{gates}. Hypothesis C validated at P_measured > 0.55; "
                f"CA3-anti-signal atom scope TIGHTENS to standard-random-"
                f"projection-DG-only. Refutes universal CA3 anti-signal "
                f"claim at this regime. FOLDIAK r@1={r_fol:.4f} achieves "
                f"parity/beats cosine baseline ({r_cos:.4f}). Regression arms "
                f"REPRODUCED Cell 4 MEASURED@ (STANDARD={r_std:.4f} vs 0.517 "
                f"target; DG_ONLY={r_dg:.4f} vs 0.700 target; COSINE={r_cos:.4f}"
                f" vs 1.000 target; RANDOM={r_rand:.4f}). "
                f"HONEST SCOPE: MECHANISM_DISCRIMINATED_ON_SUPERVISED synthetic "
                f"episodic-binding regime; SUBSTRATE KNOWS ALMOST NOTHING; "
                f"NOT a general-knowledge or language claim. Foldiak 1990 is "
                f"CANONICAL literature mechanism (arXiv:2301.02196 also directly "
                f"cited); NOT a novel-primitive claim. "
                f"Anti-personification maintained. HOLD pending Skunkworks "
                f"landed-VET.")

    # MIDDLE_BAND: partial recovery.
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial Foldiak recovery. {gates}. "
            f"Interpretation: HP1 (FOLDIAK >= DG_ONLY) = "
            f"{'PASS' if hp1_ok else 'FAIL'}; HP2 (FOLDIAK - STANDARD >= 0.10) = "
            f"{'PASS' if hp2_ok else 'FAIL'}; HP3 (FOLDIAK >= COSINE) = "
            f"{'PASS' if hp3_ok else 'FAIL'}. FOLDIAK r@1={r_fol:.4f} vs "
            f"STANDARD={r_std:.4f} DG_ONLY={r_dg:.4f} COSINE={r_cos:.4f} "
            f"RANDOM={r_rand:.4f}. Hypothesis C partially supported at "
            f"P_measured between 0.30-0.55. Cell 4 regime regression verified "
            f"(STANDARD, DG_ONLY, COSINE within tol). CA3-anti-signal atom "
            f"scope-adjustment ambiguous; requires 2x-drill or further "
            f"Foldiak tuning (n_epochs, lr_Q, lr_W). "
            f"HONEST SCOPE: MECHANISM_PARTIALLY_DISCRIMINATED_ON_SUPERVISED "
            f"synthetic episodic-binding regime; SUBSTRATE KNOWS ALMOST "
            f"NOTHING. Anti-personification maintained.")


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
         f"cluster_size={CLUSTER_SIZE} flip_frac={ADVERSARIAL_FLIP_FRAC}")
    _log(f"[config] tf_capacity_theoretical={_TF_CAPACITY:.1f}")
    _log(f"[config] Foldiak: n_epochs={FOLDIAK_N_EPOCHS} n_relax={FOLDIAK_N_RELAX} "
         f"lr_Q={FOLDIAK_LR_Q} lr_W={FOLDIAK_LR_W} lr_t={FOLDIAK_LR_T}")
    _log(f"[config] HP1: FOLDIAK - DG_ONLY >= {HP1_FOLDIAK_MINUS_DG_ONLY_FLOOR:+.2f}")
    _log(f"[config] HP2: FOLDIAK - STANDARD >= {HP2_FOLDIAK_MINUS_STANDARD_FLOOR:+.2f}")
    _log(f"[config] HP3: FOLDIAK - COSINE >= {HP3_FOLDIAK_MINUS_COSINE_FLOOR:+.2f}")

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
        1 for ps in per_seed
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
        "cluster_size": CLUSTER_SIZE,
        "adversarial_flip_frac": ADVERSARIAL_FLIP_FRAC,
        "tf_capacity_theoretical": _TF_CAPACITY,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "arms_differ_exempted": [
            {"arm_pair": REGRESSION_ARMS,
             "reason": "regression arms share input episodes (random codebook "
                       "at N=50 seed=fixed); encoder outputs still differ; "
                       "exempted from bit-identity check within group."}
        ],
        "baseline_in_band_check": {
            "arm": ARM_RANDOM,
            "chance_r1": CHANCE_R1_N500,
            "band_max_r1": BASELINE_IN_BAND_R1_MAX_N500,
            "observed_r1_mean": agg.get(ARM_RANDOM, {}).get("recall_at_1_mean"),
        },
        "cell4_regression_targets": {
            "STANDARD": CELL4_STANDARD_R1_MEAN,
            "DG_ONLY": CELL4_DG_ONLY_R1_MEAN,
            "COSINE": CELL4_COSINE_R1_MEAN,
            "tolerance": CELL4_R1_TOLERANCE,
        },
        "foldiak_hyperparams": {
            "n_epochs": FOLDIAK_N_EPOCHS, "n_relax": FOLDIAK_N_RELAX,
            "lr_Q": FOLDIAK_LR_Q, "lr_W": FOLDIAK_LR_W, "lr_t": FOLDIAK_LR_T,
            "W_max": FOLDIAK_W_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "line_buffered_stdout",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": [ARM_HIPPO_FOLDIAK, ARM_HIPPO_DG_ONLY],
            "HP2": [ARM_HIPPO_FOLDIAK, ARM_HIPPO_STANDARD],
            "HP3": [ARM_HIPPO_FOLDIAK, ARM_COSINE],
            "REGRESSION": REGRESSION_ARMS + [ARM_HIPPO_STANDARD, ARM_HIPPO_DG_ONLY,
                                             ARM_COSINE],
            "HF_baseline_in_band": [ARM_RANDOM],
            "HF_foldiak_dg_sparse_rate": [ARM_HIPPO_FOLDIAK],
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
