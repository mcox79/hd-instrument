"""Shared core for substrate_continual_learning_CRISPR_phase_diagram_v1 sibling cells.

Provides the CPU phase-diagram sweep over (M, N, forget_rate) with 3 arms
(ARM_CRISPR_FULL / ARM_NO_FORGET / ARM_OVERWRITE_ONLY) measuring continual-
learning final-recall on the FIRST-written cohort after sequential writes.

Goal: characterize the regime where CRISPR (selective overwrite + decay)
HOLDS vs COLLAPSES. Fills Stage 1 continual-learning phase coverage MID -> HIGH
per pattern_completion v2.1 / sequence_binding v2 promotion path.

CRISPR mechanism (substrate-native simplification of chain-grade cl_crispr
primitive): covariance write of (key, value) pairs onto W; "selectivity" =
key-overlap-gated write so collisions overwrite, fresh keys ADD; decay factor
(1 - forget_rate) applied to W before each new write cohort.

Sweep axis (75 grid points; write_strength fixed at 1.0):
  M (items per cohort, sequential cohorts of size 100) in {100, 500, 1000, 5000, 10000} - 5
  N (substrate dim) in {2048, 4096, 8192}                                              - 3
  forget_rate in {0.001, 0.006, 0.01, 0.05, 0.1}                                       - 5

ARMS (3, fired discriminator):
  ARM_CRISPR_FULL       - covariance write + selective overwrite + forget decay (full)
  ARM_NO_FORGET         - covariance write + selective overwrite, NO decay
  ARM_OVERWRITE_ONLY    - covariance write to ALL keys (no selectivity) + NO decay
                          i.e. catastrophic interference baseline

Each grid point measures:
  - recall_first_cohort: cosine-cleanup recall of the FIRST-written cohort's
    values, queried by their keys, AFTER all M items written.
  - recall_last_cohort:  same but for the LAST-written cohort (recency control).

Discriminator: ARM_CRISPR_FULL.recall_first_cohort > ARM_OVERWRITE_ONLY.recall_first_cohort
            by >= 0.30 at >= 30 of 75 grid points.

Positive-control at small-M / large-N / mid-forget: expect ARM_CRISPR ~= 1.000.

ASCII-only. CPU numpy primary.
Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 1 phase-diagram coverage
"""
# PRESERVE_ENV_VARS: HDLAB_QUEUE=local_cpu_queue
# PRESERVE_ENV_VARS_RATIONALE: CPU-only numpy cell; declares contract per
#   Skunkworks META RULE 2026-06-28 (env_var_contract_must_survive_runner_dispatch).
#   Cell does NOT import torch; gpu_mandate_check is not applicable here, but the
#   marker is greppable for orchestrator dispatch wrappers.

from __future__ import annotations

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ANCHOR_PREFIX = "substrate_continual_learning_CRISPR_phase_diagram_v1"

# ----- Phase axes (LOCKED) -----
M_VALUES = (100, 500, 1000, 5000, 10000)       # 5 points
N_VALUES = (2048, 4096, 8192)                  # 3 points
FORGET_VALUES = (0.001, 0.006, 0.01, 0.05, 0.1)  # 5 points (centered on legacy 0.006)
WRITE_STRENGTH = 1.0                           # fixed per scope-reduction
ARMS = ("ARM_CRISPR_FULL", "ARM_NO_FORGET", "ARM_OVERWRITE_ONLY")

# Smoke corners (chosen to FIRE the discriminator + cover regimes):
#   - small-M small-N mid-forget (CRISPR easy)
#   - mid-M mid-N mid-forget (mechanism-active regime)
#   - large-M small-N mid-forget (CRISPR challenged, OVERWRITE collapses)
#   - small-M large-N low-forget (positive control)
#   - mid-M large-N high-forget (CRISPR holds; NO_FORGET worse than CRISPR)
#   - large-M large-N mid-forget (capacity boundary)
SMOKE_CORNERS = (
    (100,   2048, 0.006),
    (1000,  4096, 0.006),
    (5000,  2048, 0.006),
    (100,   8192, 0.001),
    (1000,  8192, 0.05),
    (10000, 8192, 0.006),
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load)
HP_FULL_MIN_DISCRIM_PTS = 30        # >= 30 of 75 grid pts with CRISPR > OVERWRITE by >= 0.30
HP_DISCRIM_DELTA = 0.30             # ARM_CRISPR_FULL.recall_first - ARM_OVERWRITE_ONLY.recall_first
HP_POS_CONTROL_MIN = 0.95           # at smallest M, largest N, mid forget: ARM_CRISPR >= this
HF_NO_DISCRIM_PTS = 5               # if < 5 of 75 fire discriminator: HARD_FAIL (mechanism not active)
HF_ARMS_IDENTICAL_DELTA = 0.02      # if mean |CRISPR - OVERWRITE| < this across grid: identical arms
MB_PTS_MIN = 10                     # MIDDLE_BAND if 10..29 pts fire
MB_PTS_MAX = 29

# Smoke discriminator (must fire >= 2 of 6 corners with delta >= 0.30):
SMOKE_MIN_DISCRIM_PTS = 2
SMOKE_DISCRIM_DELTA = 0.30
SMOKE_MAX_SAT_PTS = 5
SMOKE_MAX_FLOOR_PTS = 5

# Probe / readout config
N_PROBE_PER_COHORT = 30        # number of cohort items used to compute recall
COHORT_SIZE = 100              # first/last cohort size; sequential cohorts are size COHORT_SIZE
COSINE_FLOOR_RECALL = 0.5      # cos > 0.5 counted as correct (bipolar/0-mean clean)

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ----- Primitives -----

def _bipolar(rng: np.random.Generator, m: int, n: int) -> np.ndarray:
    """Bipolar +/-1 array (m, n)."""
    return rng.integers(0, 2, size=(m, n), dtype=np.int8).astype(np.float32) * 2.0 - 1.0


def _normalize_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8
    return x / n


def _make_cohorts(rng: np.random.Generator, M_total: int, N: int,
                   cohort_size: int = 100,
                   within_cohort_overlap: float = 0.6) -> Tuple[np.ndarray, np.ndarray]:
    """Generate keys + values for M_total items, partitioned into cohorts.

    Keys: each cohort has a shared "cohort tag" bipolar vector. Within-cohort
    keys are constructed as alpha*tag + (1-alpha)*item_specific, then normalized.
    This creates within-cohort key overlap (cos ~= within_cohort_overlap) and
    near-zero cross-cohort overlap. This is the catastrophic-interference
    regime: OVERWRITE accumulates noise at correlated keys; CRISPR's selective
    write + decay handles it.

    Values: independent random bipolar (no correlation by design).
    Returns (keys, values), both shape (M_total, N), row-unit-norm.
    """
    n_cohorts = (M_total + cohort_size - 1) // cohort_size
    cohort_tags = _bipolar(rng, n_cohorts, N)
    cohort_tags = _normalize_rows(cohort_tags)
    K = np.empty((M_total, N), dtype=np.float32)
    for c in range(n_cohorts):
        lo = c * cohort_size
        hi = min(lo + cohort_size, M_total)
        n_in = hi - lo
        # Item-specific random component
        item_part = _bipolar(rng, n_in, N)
        item_part = _normalize_rows(item_part)
        tag = cohort_tags[c:c+1]      # (1, N)
        # Mix: alpha * tag + (1-alpha) * item_specific
        alpha = float(within_cohort_overlap)
        mixed = alpha * tag + (1.0 - alpha) * item_part
        K[lo:hi] = _normalize_rows(mixed)
    V = _bipolar(rng, M_total, N)
    V = _normalize_rows(V)
    return K, V


def _cohort_indices(M_total: int, cohort_idx: int, cohort_size: int) -> Tuple[int, int]:
    """Return (lo, hi) inclusive-exclusive into the M_total array for a given cohort."""
    lo = cohort_idx * cohort_size
    hi = min(lo + cohort_size, M_total)
    return lo, hi


# ----- Arms -----

def _arm_crispr_full(
    K_all: np.ndarray, V_all: np.ndarray, forget_rate: float,
    cohort_size: int, write_strength: float,
) -> np.ndarray:
    """ARM_CRISPR_FULL: per-cohort decay-then-write with selective-overwrite.

    Decay: W *= (1 - forget_rate) before each cohort.
    Selective overwrite: for each item (k, v):
      e_old = W @ k     (current associated value)
      delta = v - e_old (residual; the "selective overwrite" = only fix where wrong)
      W += alpha * outer(delta, k) / N
    where alpha = write_strength, N = K_all.shape[1].

    This is the substrate-native CRISPR primitive: by-construction selective
    (residual goes to zero at converged keys -> no further write).
    """
    M_total, N = K_all.shape
    n_cohorts = (M_total + cohort_size - 1) // cohort_size
    W = np.zeros((N, N), dtype=np.float32)
    for c in range(n_cohorts):
        # 1. decay
        if forget_rate > 0.0:
            W *= (1.0 - forget_rate)
        # 2. write cohort with selective-residual
        lo, hi = _cohort_indices(M_total, c, cohort_size)
        Kc = K_all[lo:hi]
        Vc = V_all[lo:hi]
        # residual write (vectorized across cohort)
        E_old = Kc @ W.T              # (m, N) predicted values
        D = Vc - E_old                # (m, N) residual
        # W += write_strength * D^T @ K / N (one matmul; vectorized batch update)
        W += (write_strength * (D.T @ Kc) / float(N)).astype(np.float32)
    return W


def _arm_no_forget(
    K_all: np.ndarray, V_all: np.ndarray, forget_rate: float,
    cohort_size: int, write_strength: float,
) -> np.ndarray:
    """ARM_NO_FORGET: same selective-residual write, but NO decay between cohorts.

    Discriminates CRISPR-with-forget from naive-residual-additive accumulation.
    Note: forget_rate is IGNORED here by design.
    """
    M_total, N = K_all.shape
    n_cohorts = (M_total + cohort_size - 1) // cohort_size
    W = np.zeros((N, N), dtype=np.float32)
    for c in range(n_cohorts):
        # NO decay
        lo, hi = _cohort_indices(M_total, c, cohort_size)
        Kc = K_all[lo:hi]
        Vc = V_all[lo:hi]
        E_old = Kc @ W.T
        D = Vc - E_old
        W += (write_strength * (D.T @ Kc) / float(N)).astype(np.float32)
    return W


def _arm_overwrite_only(
    K_all: np.ndarray, V_all: np.ndarray, forget_rate: float,
    cohort_size: int, write_strength: float,
) -> np.ndarray:
    """ARM_OVERWRITE_ONLY: naive Hebbian write (NO selectivity, NO decay).

    This is the catastrophic-interference baseline: each item just adds
    outer(v, k) regardless of prior state. Old items get overwritten.
    """
    M_total, N = K_all.shape
    n_cohorts = (M_total + cohort_size - 1) // cohort_size
    W = np.zeros((N, N), dtype=np.float32)
    for c in range(n_cohorts):
        lo, hi = _cohort_indices(M_total, c, cohort_size)
        Kc = K_all[lo:hi]
        Vc = V_all[lo:hi]
        # Naive Hebbian: W += alpha * V^T K / N
        W += (write_strength * (Vc.T @ Kc) / float(N)).astype(np.float32)
    return W


def _recall_cohort(
    W: np.ndarray, K_all: np.ndarray, V_all: np.ndarray,
    cohort_idx: int, cohort_size: int, n_probe: int,
    rng: np.random.Generator,
) -> Tuple[float, float]:
    """Query the cohort at cohort_idx with cosine-cleanup recall over ALL M values.

    Returns (recall_top1_against_FULL_set, mean_cosine_to_true).

    Method: for each of n_probe items in the cohort, predict v_hat = W @ k_i;
    cosine-cleanup against ALL M values (not just the cohort); top1 = correct
    if argmax cosine == global_i. This is the catastrophic-interference test:
    can the substrate disambiguate the right item out of all M written items?
    OVERWRITE_ONLY will fail this at high M (W accumulates all writes; query
    returns a superposition); CRISPR with decay preserves recency-weighted
    discrimination.
    """
    lo, hi = _cohort_indices(K_all.shape[0], cohort_idx, cohort_size)
    Kc = K_all[lo:hi]
    Vc = V_all[lo:hi]
    if Kc.shape[0] == 0:
        return 0.0, 0.0
    n_q = min(n_probe, Kc.shape[0])
    # Sample n_q random items from the cohort
    local_idx = rng.choice(Kc.shape[0], size=n_q, replace=False)
    global_idx = lo + local_idx     # absolute index into K_all / V_all
    K_q = Kc[local_idx]
    V_q = Vc[local_idx]
    # Predict
    V_hat = K_q @ W.T              # (n_q, N)
    V_hat = _normalize_rows(V_hat)
    # Cleanup against ALL M values (catastrophic-interference test)
    sims = V_hat @ V_all.T          # (n_q, M_total)
    top1_global = sims.argmax(axis=-1)
    correct = (top1_global == global_idx).astype(np.float32).mean()
    # Mean cosine to true value
    true_cos = (V_hat * V_q).sum(axis=-1)
    return float(correct), float(true_cos.mean())


# ----- Phase point -----

def _run_phase_point(
    rng: np.random.Generator,
    M: int, N: int, forget_rate: float,
    n_probe: int, cohort_size: int,
) -> Dict[str, Any]:
    """Run all 3 arms on one (M, N, forget) phase point.

    Builds keys/values ONCE, runs all 3 arms on the same data (apples-to-apples).
    Returns a dict with per-arm recall_first / recall_last metrics + arm-diff.
    """
    K_all, V_all = _make_cohorts(rng, M, N)
    n_cohorts = (M + cohort_size - 1) // cohort_size
    first_idx = 0
    last_idx = n_cohorts - 1

    out: Dict[str, Any] = {
        "M": int(M),
        "N": int(N),
        "forget_rate": float(forget_rate),
        "n_cohorts": int(n_cohorts),
        "n_probe": int(n_probe),
    }

    # Arms (separate rngs for probing each arm to keep apples-to-apples for the
    # readout sample selection)
    arm_funcs = {
        "ARM_CRISPR_FULL": _arm_crispr_full,
        "ARM_NO_FORGET": _arm_no_forget,
        "ARM_OVERWRITE_ONLY": _arm_overwrite_only,
    }
    probe_seed = int(rng.integers(0, 2**31 - 1))
    for arm_name, arm_fn in arm_funcs.items():
        W = arm_fn(K_all, V_all, forget_rate, cohort_size, WRITE_STRENGTH)
        # Use a fresh rng with same seed for each arm so probe-index sampling
        # is identical across arms.
        probe_rng_first = np.random.default_rng(probe_seed)
        recall_first, cos_first = _recall_cohort(
            W, K_all, V_all, first_idx, cohort_size, n_probe, probe_rng_first,
        )
        probe_rng_last = np.random.default_rng(probe_seed + 1)
        recall_last, cos_last = _recall_cohort(
            W, K_all, V_all, last_idx, cohort_size, n_probe, probe_rng_last,
        )
        out[f"{arm_name}_recall_first"] = recall_first
        out[f"{arm_name}_recall_last"] = recall_last
        out[f"{arm_name}_cos_first"] = cos_first
        out[f"{arm_name}_cos_last"] = cos_last

    # Discriminator delta
    out["discrim_delta_first"] = (
        out["ARM_CRISPR_FULL_recall_first"] - out["ARM_OVERWRITE_ONLY_recall_first"]
    )
    out["discrim_delta_last"] = (
        out["ARM_CRISPR_FULL_recall_last"] - out["ARM_OVERWRITE_ONLY_recall_last"]
    )
    return out


# ----- Sweep driver -----

def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    """Run full or smoke phase diagram for one seed.

    Args:
        seed: integer seed.
        run_mode: "smoke" | "full" | "selftest".
        smoke_corners: if True, only run SMOKE_CORNERS (smoke gate).
    """
    rng = np.random.default_rng(seed)

    if smoke_corners or run_mode == "smoke":
        points = list(SMOKE_CORNERS)
        n_probe = 20
        cohort_size = COHORT_SIZE
    elif run_mode == "selftest":
        # tiny selftest: 2 corner points
        points = [SMOKE_CORNERS[0], SMOKE_CORNERS[3]]   # small-M-small-N + positive-control
        n_probe = 10
        cohort_size = COHORT_SIZE
    else:
        points = []
        for M in M_VALUES:
            for N in N_VALUES:
                for forget in FORGET_VALUES:
                    points.append((M, N, forget))
        n_probe = N_PROBE_PER_COHORT
        cohort_size = COHORT_SIZE

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (M, N, forget) in points:
        pt_rng = np.random.default_rng(int(rng.integers(0, 2**31 - 1)))
        try:
            res = _run_phase_point(pt_rng, M, N, forget, n_probe, cohort_size)
            phase_map.append(res)
        except Exception as e:
            # Record-and-halt per 3-smoke-disciplines: NO silent except blocks
            err = {
                "M": int(M), "N": int(N), "forget_rate": float(forget),
                "ERROR": f"{type(e).__name__}: {e}",
                "_traceback": traceback.format_exc(),
            }
            phase_map.append(err)
            print(f"[ERROR at M={M} N={N} forget={forget}]: {e}", flush=True)
            # Halt the sweep so the cell doesn't silently drop points
            break

    elapsed = time.time() - started

    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "smoke_corners": bool(smoke_corners),
        "backend": get_backend_label(),
        "n_phase_points": len(phase_map),
        "n_probe_per_point": int(n_probe),
        "cohort_size": int(cohort_size),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


# ----- Aggregate + verdict -----

def aggregate_and_verdict(
    per_seed: Dict[str, Dict[str, Any]],
    run_mode: str,
) -> Dict[str, Any]:
    """Compute discriminator-fires-per-grid-point + verdict from per-seed maps."""
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool by (M, N, forget); compute mean per arm per pt
    bucket: Dict[Tuple[int, int, float], Dict[str, List[float]]] = {}
    error_pts: List[Dict[str, Any]] = []
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            if "ERROR" in pt:
                error_pts.append(pt)
                continue
            key = (int(pt["M"]), int(pt["N"]), float(pt["forget_rate"]))
            d = bucket.setdefault(key, {
                "ARM_CRISPR_FULL_recall_first": [],
                "ARM_NO_FORGET_recall_first": [],
                "ARM_OVERWRITE_ONLY_recall_first": [],
                "ARM_CRISPR_FULL_recall_last": [],
                "ARM_NO_FORGET_recall_last": [],
                "ARM_OVERWRITE_ONLY_recall_last": [],
            })
            for k in d:
                d[k].append(float(pt.get(k, 0.0)))

    if not bucket:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": f"no valid phase points; {len(error_pts)} errors",
                "summary": f"no valid phase points; {len(error_pts)} errors",
                "error_pts": error_pts}

    # Per-pt aggregate
    summary_per_pt: List[Dict[str, Any]] = []
    discrim_fires = 0
    discrim_deltas: List[float] = []
    sat_pts = 0
    floor_pts = 0
    arms_identical_deltas: List[float] = []
    for key, d in sorted(bucket.items()):
        M, N, forget = key
        crispr_first = float(np.mean(d["ARM_CRISPR_FULL_recall_first"]))
        noforget_first = float(np.mean(d["ARM_NO_FORGET_recall_first"]))
        overwrite_first = float(np.mean(d["ARM_OVERWRITE_ONLY_recall_first"]))
        crispr_last = float(np.mean(d["ARM_CRISPR_FULL_recall_last"]))
        noforget_last = float(np.mean(d["ARM_NO_FORGET_recall_last"]))
        overwrite_last = float(np.mean(d["ARM_OVERWRITE_ONLY_recall_last"]))
        delta = crispr_first - overwrite_first
        discrim_deltas.append(delta)
        arms_identical_deltas.append(abs(delta))
        if delta >= HP_DISCRIM_DELTA:
            discrim_fires += 1
        # SAT pt: all 3 arms >= 0.95 on first cohort = saturated (mechanism not active)
        if crispr_first >= 0.95 and overwrite_first >= 0.95 and noforget_first >= 0.95:
            sat_pts += 1
        # FLOOR pt: all 3 arms <= 0.10 on first cohort = collapsed
        if crispr_first <= 0.10 and overwrite_first <= 0.10 and noforget_first <= 0.10:
            floor_pts += 1
        summary_per_pt.append({
            "M": M, "N": N, "forget_rate": forget,
            "ARM_CRISPR_FULL_recall_first": crispr_first,
            "ARM_NO_FORGET_recall_first": noforget_first,
            "ARM_OVERWRITE_ONLY_recall_first": overwrite_first,
            "ARM_CRISPR_FULL_recall_last": crispr_last,
            "ARM_NO_FORGET_recall_last": noforget_last,
            "ARM_OVERWRITE_ONLY_recall_last": overwrite_last,
            "discrim_delta_first": delta,
            "n_seeds": len(d["ARM_CRISPR_FULL_recall_first"]),
        })

    n_total = len(summary_per_pt)
    mean_arms_identical = float(np.mean(arms_identical_deltas)) if arms_identical_deltas else 0.0

    # Positive control: at smallest M / largest N / mid forget, ARM_CRISPR should be high
    pc_pts = [p for p in summary_per_pt
              if p["M"] == M_VALUES[0] and p["N"] == N_VALUES[-1]
              and abs(p["forget_rate"] - 0.006) < 1e-6]
    pc_met = bool(pc_pts) and pc_pts[0]["ARM_CRISPR_FULL_recall_first"] >= HP_POS_CONTROL_MIN

    # Smoke or full thresholds
    if run_mode == "smoke" or any(b.get("smoke_corners") for b in per_seed.values()):
        # Smoke mode
        min_discrim = SMOKE_MIN_DISCRIM_PTS
        max_sat = SMOKE_MAX_SAT_PTS
        max_floor = SMOKE_MAX_FLOOR_PTS
    else:
        min_discrim = HP_FULL_MIN_DISCRIM_PTS
        max_sat = max(2, n_total // 3)  # tolerate up to 1/3 saturated
        max_floor = max(2, n_total // 3)

    # HARD_FAIL checks
    if error_pts:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL: {len(error_pts)} grid pts errored; "
                             f"see error_pts for diagnostics"),
            "summary": f"HARD_FAIL: {len(error_pts)} grid errors",
            "n_total": n_total,
            "discrim_fires": discrim_fires,
            "error_pts": error_pts[:5],
        }

    if mean_arms_identical < HF_ARMS_IDENTICAL_DELTA:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_ARMS_IDENTICAL: mean |CRISPR-OVERWRITE| = "
                             f"{mean_arms_identical:.4f} < {HF_ARMS_IDENTICAL_DELTA}; "
                             f"mechanism not firing"),
            "summary": f"ARMS_IDENTICAL mean|delta|={mean_arms_identical:.4f}",
            "n_total": n_total,
            "discrim_fires": discrim_fires,
            "mean_arms_identical_delta": mean_arms_identical,
            "summary_per_phase_point": summary_per_pt,
        }

    if discrim_fires < HF_NO_DISCRIM_PTS:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: "
                             f"discrim_fires={discrim_fires} < {HF_NO_DISCRIM_PTS} "
                             f"(sat={sat_pts}, floor={floor_pts}, n_total={n_total})"),
            "summary": (f"discriminator did not fire enough ({discrim_fires}/"
                         f"{n_total}); sat={sat_pts} floor={floor_pts}"),
            "n_total": n_total,
            "discrim_fires": discrim_fires,
            "sat_pts": sat_pts,
            "floor_pts": floor_pts,
            "summary_per_phase_point": summary_per_pt,
        }

    if sat_pts > max_sat:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_BY_CONSTRUCTION_SAT: sat_pts={sat_pts} > "
                             f"{max_sat}; substrate cannot stress mechanism "
                             f"(M too small / N too large for regime)"),
            "summary": f"too saturated ({sat_pts}/{n_total})",
            "n_total": n_total,
            "discrim_fires": discrim_fires,
            "sat_pts": sat_pts,
            "summary_per_phase_point": summary_per_pt,
        }

    # HARD_PASS gate (full only)
    if run_mode == "full":
        if discrim_fires >= HP_FULL_MIN_DISCRIM_PTS and pc_met:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: discrim_fires={discrim_fires}/{n_total} >= "
                f"{HP_FULL_MIN_DISCRIM_PTS}; positive_control_met={pc_met} "
                f"(ARM_CRISPR @ M={M_VALUES[0]} N={N_VALUES[-1]} forget=0.006); "
                f"mean_arms_identical_delta={mean_arms_identical:.4f}; "
                f"sat={sat_pts} floor={floor_pts}"
            )
        elif discrim_fires >= MB_PTS_MIN:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: discrim_fires={discrim_fires}/{n_total} in "
                f"[{MB_PTS_MIN}, {HP_FULL_MIN_DISCRIM_PTS-1}); pos_control_met={pc_met}"
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND_LOWER: discrim_fires={discrim_fires}/{n_total} "
                f"<{MB_PTS_MIN}; pos_control_met={pc_met}"
            )
    else:
        # Smoke gate
        if discrim_fires >= min_discrim and sat_pts <= max_sat and floor_pts <= max_floor:
            verdict = "SMOKE_OK"
            verdict_msg = (
                f"SMOKE_OK: discrim_fires={discrim_fires}/{n_total} >= {min_discrim}; "
                f"sat={sat_pts}<={max_sat}; floor={floor_pts}<={max_floor}; "
                f"pos_control_met={pc_met}"
            )
        else:
            verdict = "SMOKE_FAIL"
            verdict_msg = (
                f"SMOKE_FAIL: discrim_fires={discrim_fires}/{n_total} (need >={min_discrim}); "
                f"sat={sat_pts} (max {max_sat}); floor={floor_pts} (max {max_floor})"
            )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_total": n_total,
        "discrim_fires": discrim_fires,
        "sat_pts": sat_pts,
        "floor_pts": floor_pts,
        "mean_arms_identical_delta": mean_arms_identical,
        "mean_discrim_delta": float(np.mean(discrim_deltas)) if discrim_deltas else 0.0,
        "positive_control_met": pc_met,
        "n_seeds_complete": len(per_seed),
        "summary_per_phase_point": summary_per_pt,
        "expected_n_units": 75,
        "observed_n_units": n_total,
        "cardinality_ok": (n_total == 75) if run_mode == "full" else True,
    }


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corners, asserts discriminator FIRES on at least one
    point (CRISPR > OVERWRITE by some margin)."""
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        # Positive control point: (100, 8192, 0.001) - small M, large N, low forget
        # CRISPR should be very high.
        pc = [p for p in pts if p["M"] == 100 and p["N"] == 8192]
        if not pc:
            return False, "selftest: missing positive-control corner"
        crispr_pc = pc[0]["ARM_CRISPR_FULL_recall_first"]
        if crispr_pc < 0.80:
            return False, (f"selftest: ARM_CRISPR positive-control "
                            f"(M=100,N=8192,forget=0.001) recall_first="
                            f"{crispr_pc:.3f} (expected >= 0.80)")

        # Discriminator: at least one point should show CRISPR > OVERWRITE
        # by > 0.10 on either first or last cohort (small selftest tolerance).
        deltas = []
        for p in pts:
            d_first = (p["ARM_CRISPR_FULL_recall_first"]
                        - p["ARM_OVERWRITE_ONLY_recall_first"])
            d_last = (p["ARM_CRISPR_FULL_recall_last"]
                        - p["ARM_OVERWRITE_ONLY_recall_last"])
            deltas.append(max(d_first, d_last))
        max_delta = max(deltas) if deltas else 0.0
        if max_delta < 0.05:
            return False, (f"selftest: max discriminator delta = {max_delta:.3f} "
                            f"(expected >= 0.05); arms may be identical")

        msg = (f"selftest OK: ARM_CRISPR_pc={crispr_pc:.3f}, "
               f"max_discrim_delta={max_delta:.3f}, backend={body['backend']}, "
               f"elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
