"""substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v1.

DIAGNOSTIC PROBE.  Default tier MEASURED_MECHANISM (NOT chain-grade promotion).
Identifies WHICH structural mechanism creates the DIRECT-STANDARD readout
gap observed in cortex_hippo_handoff_with_hippo_capacity_rescue_v1.

LINEAGE / WHY:
  v1 standard handoff               -> CLOSED-negative at M=8192
  v2 replay-fixed                   -> CLOSED-negative
  spaced-rep NREM v1                -> 3-way COLLAPSE (initial attribution:
                                       "alpha_h ~0.137 Hopfield-strict")
  hippo_capacity_rescue v1          -> DISPROVES alpha attribution.  At
                                       N_h=8192/M=2048 alpha_h=0.014 (well
                                       sub-capacity, alpha_simple=0.25),
                                       DIRECT still 0.989 vs STANDARD 0.226.
                                       2-step Hopfield cleanup collapses
                                       to zero.  Bottleneck is STRUCTURAL,
                                       not capacity.

HYPOTHESES (to discriminate):
  H1 SPARSE-OVERLAP INTERFERENCE
      Sparse-DG codes (k=10% of N_h active per item) have many shared
      active bits across items.  W_h @ cue then sums vals_h-rows weighted
      by overlap counts; "popular" bits dominate, washing out the cue-
      specific signal that selects the correct val.
  H2 SIGN-QUANTIZATION
      sign(W_h @ cue) collapses real-valued matmul result to {-1,+1}.
      Magnitude information (which entries are "loudest" -> evidence of
      correct stored val) is destroyed at the readout boundary.
  H3 SIGN+NORM COMBINED DESTRUCTION
      After sign() and projection to cortex, L2-normalization removes the
      remaining correlation-with-stored-val.

ARMS (5; META_RULE_AF arms-must-differ):
  ARM_DIRECT
      Cortex writes from the real cue (no hippo read).  Reference ceiling.
      Reproduces rescue v1's 0.989 at N_h=8192 / M=2048.
  ARM_STANDARD
      sign(W_h @ cue), sparse-DG hippo.  Baseline.  Reproduces 0.226.
  ARM_REAL_VALUED
      W_h @ cue with NO sign().  Sparse-DG hippo retained.  L2-norm at
      projection.  Tests H2 in isolation: if recall jumps vs STANDARD,
      sign() is the killer.
  ARM_DENSE_DG
      Replace sparse-DG (k-WTA at 10%) with DENSE bipolar (no k-WTA;
      sparsity = 1.0).  Keep sign() readout.  Tests H1 in isolation: if
      recall jumps vs STANDARD, sparse-overlap was the killer.
  ARM_DENSE_REAL
      Dense bipolar + real-valued readout.  Tests H1+H2 combined.

EXPECTED OUTCOMES (pre-reg interpretive map):
  REAL_VALUED >> STANDARD                 -> H2 dominant (sign-readout
                                             destroys magnitude info)
  DENSE_DG    >> STANDARD                 -> H1 dominant (sparse-overlap
                                             interference)
  DENSE_REAL  >> STANDARD,
    REAL_VALUED ~= STANDARD,
    DENSE_DG    ~= STANDARD               -> Pure interaction; neither
                                             cause alone suffices
  All three lifts in PROPORTION                -> Composition (additive)
  None of the three lifts                 -> NONE of H1/H2/H3 -- some
                                             OTHER structural cause

DISCRIMINATOR SLOPES:
  Pre-reg: |gap closed by any arm| > 0.15 is a CLOSURE.
  ARM_REAL_VALUED closes >= 0.40 of DIRECT-STANDARD gap            -> H2 CONFIRMED
  ARM_DENSE_DG    closes >= 0.40 of DIRECT-STANDARD gap            -> H1 CONFIRMED
  ARM_DENSE_REAL  closes >= 0.80 AND others close less             -> H1xH2 SYNERGY
  All three close less than 0.15                                   -> H_OTHER
                                                                       (open question
                                                                       for next probe)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = N_ARMS * N_SEEDS = 5 * 3 = 15 (FULL)
                                       5 * 1 =  5 (SMOKE)

REGIME (held fixed, both SMOKE and FULL -- discriminator-survives-scale per USER 2026-06-26):
  FULL:  M=2048, N_h=8192, N_c=2048  (rescue v1 sub-capacity row; gap=0.76)
  SMOKE: M=512,  N_h=2048, N_c=512   (same alpha_simple=0.25; check the gap
                                       survives at smoke scale BEFORE we ship)

  Per the rescue v1 smoke run, DIRECT/STANDARD gap is approximately invariant
  across N_h when M is scaled to hold alpha_simple constant: gap ~0.76 at all
  three sub-capacity N_h points.  Smoke at M=512/N_h=2048 (alpha_simple=0.25)
  should show DIRECT > STANDARD by >= 0.50.

ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ; META_RULE_H cardinality_ok.

PRESERVE_ENV_VARS: HDLAB_QUEUE
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
import inspect
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

# Heartbeat helper (inlined).
from datetime import datetime as _dt_mod, timezone as _tz_mod
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": _dt_mod.now(_tz_mod.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


ANCHOR_NAME = "substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v1"
_HARDENING_MARKER = "v1_bottleneck_class_diagnostic"

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
# Config.  Hold regime fixed across SMOKE and FULL except for M/N_h scaling.
# Same alpha_simple = M / N_h = 0.25 in both modes.
# ---------------------------------------------------------------------------
# FULL: rescue v1 sub-capacity row (gap 0.76 measured).
M_ITEMS_FULL = 2048
N_HIPPO_FULL = 8192
N_CORTEX_FULL = 2048
ETA_CORTEX_FULL = 0.005
SEEDS_FULL = [7, 17, 23]

# SMOKE: scaled M and N_h to hold alpha_simple = 0.25 (same regime).
M_ITEMS_SMOKE = 512
N_HIPPO_SMOKE = 2048
N_CORTEX_SMOKE = 512
ETA_CORTEX_SMOKE = 0.005
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    M_ITEMS = M_ITEMS_SMOKE
    N_HIPPO = N_HIPPO_SMOKE
    N_CORTEX = N_CORTEX_SMOKE
    ETA_CORTEX = ETA_CORTEX_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    M_ITEMS = M_ITEMS_FULL
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = SEEDS_FULL

# Hippo sparsity for ARMs that use sparse-DG (STANDARD and REAL_VALUED).
# Matches rescue v1.
HIPPO_SPARSITY_SPARSE = 0.10
# Dense arms: full bipolar.  sparsity = 1.0 means "all bits active".
HIPPO_SPARSITY_DENSE = 1.0

N_REPLAY_PER_ITEM = 1  # one replay-write per item per arm (rescue v1 convention).

ARM_NAMES: Tuple[str, ...] = (
    "ARM_DIRECT",
    "ARM_STANDARD",
    "ARM_REAL_VALUED",
    "ARM_DENSE_DG",
    "ARM_DENSE_REAL",
)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

# Discriminator thresholds.
GAP_DIR_STD_MIN_FOR_DISCRIM = 0.40  # the DIRECT-STANDARD gap must be huge at this regime
                                     # (rescue v1 measured 0.76).  Below this, smoke is
                                     # broken.
CLOSURE_FRAC_MIN_FOR_CLAIM = 0.40    # a single arm closing 0.40+ of the gap = mechanism
                                     # CONFIRMED.
CLOSURE_FRAC_SYNERGY = 0.80          # DENSE_REAL closing 0.80+ while others lag = H1xH2
                                     # SYNERGY.
NOISE_TOLERANCE = 0.15               # below this, "no closure" / H_OTHER.


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


def _alpha_h(M: int, N_h: int) -> float:
    if N_h <= 1:
        return float("inf")
    return float(M) / (2.0 * float(N_h) * math.log(float(N_h)))


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity_sparse={HIPPO_SPARSITY_SPARSE},sparsity_dense={HIPPO_SPARSITY_DENSE},"
    f"n_replay={N_REPLAY_PER_ITEM},eta_c={ETA_CORTEX},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"arms={'+'.join(ARM_NAMES)},backend=numpy,"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+ARM_HASH_DIVERGENCE+RESCUE_V1_LINEAGE"
)


# ---------------------------------------------------------------------------
# Primitives.
# ---------------------------------------------------------------------------
def _l2_normalize_batch(v_batch: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v_batch, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return v_batch / norms


def _batched_sparse_pattern_separator(x_batch: np.ndarray,
                                      P: np.ndarray, k: int) -> np.ndarray:
    """Batched k-WTA sparse pattern separator (rescue v1 reference path).

    x_batch: (M, N_raw); P: (N_h, N_raw); returns (M, N_h) bipolar sparse with
    exactly k non-zero entries per row.
    """
    h_raw = x_batch @ P.T
    abs_h = np.abs(h_raw)
    topk_idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    rows = np.arange(h_raw.shape[0])[:, None]
    signs_at_topk = np.sign(h_raw[rows, topk_idx])
    signs_at_topk[signs_at_topk == 0] = 1.0
    h_sparse = np.zeros_like(h_raw)
    h_sparse[rows, topk_idx] = signs_at_topk
    return h_sparse


def _batched_dense_bipolar(x_batch: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Dense bipolar encoder: NO k-WTA.  h = sign(P @ x), all N_h bits active.

    x_batch: (M, N_raw); P: (N_h, N_raw); returns (M, N_h) bipolar dense
    (all entries +-1).
    """
    h_raw = x_batch @ P.T
    h = np.sign(h_raw)
    h[h == 0] = 1.0
    return h


def _encode_hippo(arm_name: str, x_batch: np.ndarray, P: np.ndarray,
                  N_h: int) -> np.ndarray:
    """Per-arm hippo encoding: sparse-DG for STANDARD/REAL_VALUED, dense for
    DENSE_DG/DENSE_REAL.  ARM_DIRECT does not use hippo (caller doesn't call
    this for DIRECT)."""
    if arm_name in ("ARM_STANDARD", "ARM_REAL_VALUED"):
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h)))
        return _batched_sparse_pattern_separator(x_batch, P, k_active)
    if arm_name in ("ARM_DENSE_DG", "ARM_DENSE_REAL"):
        return _batched_dense_bipolar(x_batch, P)
    raise ValueError(f"unknown arm for hippo encode: {arm_name}")


def _hippo_readout(arm_name: str, W_h: np.ndarray, cues_h: np.ndarray) -> np.ndarray:
    """Per-arm hippo readout.

    STANDARD     : sign(cues_h @ W_h.T) -- collapses to {-1,+1}, sparse cue
    REAL_VALUED  : cues_h @ W_h.T       -- keep real magnitude, sparse cue
    DENSE_DG     : sign(cues_h @ W_h.T) -- collapses to {-1,+1}, dense cue
    DENSE_REAL   : cues_h @ W_h.T       -- keep real magnitude, dense cue
    """
    raw = cues_h @ W_h.T  # (M, N_h)
    if arm_name in ("ARM_STANDARD", "ARM_DENSE_DG"):
        out = np.sign(raw)
        out[out == 0] = 1.0
        return out
    if arm_name in ("ARM_REAL_VALUED", "ARM_DENSE_REAL"):
        return raw
    raise ValueError(f"unknown arm for hippo readout: {arm_name}")


def _arm_hash(arm_name: str, vals_c_react: np.ndarray) -> str:
    """First-N hash of the readout-projected vals_c_react matrix.  Two arms
    must NOT produce identical hashes (META_RULE_AF arms-must-differ).
    """
    # Hash the first 64 entries of the first 4 rows to bound cost.
    sample = vals_c_react[:4, :64].astype(np.float64)
    # Convert to bytes deterministically.
    return hashlib.sha256(sample.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-arm runner (numpy, single seed, single arm).
# ---------------------------------------------------------------------------
def run_arm_numpy(arm_name: str, seed: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray,
                  out_dir: Path) -> Dict:
    """One arm at the cell's fixed (M, N_h, N_c).

    Returns dict with recall_cortex, cortex_norm, arm_hash, arm_status, wall_s.
    """
    t0 = time.time()
    try:
        # Encode all items into hippo + cortex.
        if arm_name == "ARM_DIRECT":
            # No hippo read; cortex writes from real-cue projection directly.
            # We still need keys_c / vals_c in cortex space.  Use the sparse-DG
            # encode as the reference (matches rescue v1 DIRECT arm).
            keys_h = _batched_sparse_pattern_separator(
                keys_raw, P_in,
                max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
            )
            vals_h = _batched_sparse_pattern_separator(
                vals_raw, P_in,
                max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
            )
        else:
            keys_h = _encode_hippo(arm_name, keys_raw, P_in, N_HIPPO)
            vals_h = _encode_hippo(arm_name, vals_raw, P_in, N_HIPPO)

        keys_c_raw = keys_h @ P_hc.T
        vals_c_raw = vals_h @ P_hc.T
        keys_c = _l2_normalize_batch(keys_c_raw)
        vals_c = _l2_normalize_batch(vals_c_raw)

        # Hippo encode (additive Hebbian outer-product sum).
        if arm_name != "ARM_DIRECT":
            W_hippo = vals_h.T @ keys_h  # (N_h, N_h)
        else:
            W_hippo = None  # not used

        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)

        # Replay phase.  One pass over a permutation of all M items.
        rng = np.random.RandomState(seed + 17)
        n_total_writes = 0
        for rep in range(N_REPLAY_PER_ITEM):
            perm = rng.permutation(M_ITEMS)
            cues_h = keys_h[perm]    # (M, N_h)
            cues_c = keys_c[perm]    # (M, N_c)

            if arm_name == "ARM_DIRECT":
                vals_c_react = vals_c[perm]
            else:
                vals_react_h = _hippo_readout(arm_name, W_hippo, cues_h)
                vals_c_react_raw = vals_react_h @ P_hc.T
                vals_c_react = _l2_normalize_batch(vals_c_react_raw)

            W_cortex += ETA_CORTEX * (vals_c_react.T @ cues_c)
            n_total_writes += M_ITEMS

            emit_heartbeat(out_dir, unit_idx=rep,
                           total_units=N_REPLAY_PER_ITEM,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "replay", "arm": arm_name,
                                  "seed": int(seed),
                                  "writes_so_far": n_total_writes})

        # Hash AFTER the last replay -- captures the actual signal-into-cortex
        # for the arm-hash divergence check.
        if arm_name == "ARM_DIRECT":
            arm_hash_val = _arm_hash(arm_name, vals_c[perm])
        else:
            arm_hash_val = _arm_hash(arm_name, vals_c_react)

        if W_hippo is not None:
            W_hippo[:] = 0.0  # free intermediate

        # Recall test (BATCHED).
        preds_raw = keys_c @ W_cortex.T          # (M, N_c)
        preds = np.sign(preds_raw)
        preds[preds == 0] = 1.0
        preds_n = _l2_normalize_batch(preds)
        sims = preds_n @ vals_c.T                # (M, M)
        argmax = np.argmax(sims, axis=1)
        n_hits = int(np.sum(argmax == np.arange(M_ITEMS)))
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(np.linalg.norm(W_cortex))

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "arm_hash": "ERROR",
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Per-seed runner.
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    # Same projection matrices across all arms within a seed (fairness:
    # arms only differ in their hippo encoding / readout).
    rng_p = np.random.RandomState(seed + 1000)
    P_in = rng_p.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng_p.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)

    print(f"  [seed={seed}] M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} "
          f"arms={list(ARM_NAMES)} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name in ARM_NAMES:
        out = run_arm_numpy(arm_name, seed,
                            keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>16s}] "
            f"recall={out['recall_cortex']:.3f} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"hash={out['arm_hash']} "
            f"status={out['arm_status']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_CORTEX,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "M": M_ITEMS,
        "n_arms": len(ARM_NAMES),
        "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "hippo_sparsity_dense": HIPPO_SPARSITY_DENSE,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_recall_mean(arms_across_seeds: List[List[Dict]],
                     arm_name: str) -> float:
    vals = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                vals.append(float(a["recall_cortex"]))
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hash_set(arms_across_seeds: List[List[Dict]],
                  arm_name: str) -> List[str]:
    hashes = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                hashes.append(str(a["arm_hash"]))
    return hashes


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {len(SEEDS)} seeds, got {len(results)}")
    # Validate per-arm cardinality + arm errors.
    arms_across = []
    for r in results:
        if len(r.get("arms", [])) != len(ARM_NAMES):
            return ("HARD_FAIL",
                    f"CARDINALITY_BREACH: seed={r.get('seed')} has "
                    f"{len(r.get('arms', []))} arms, expected {len(ARM_NAMES)}")
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"seed={r['seed']} arm={a['arm_name']} "
                        f"error: {a['arm_status']}")
        arms_across.append(r["arms"])

    # META_RULE_AF arms-must-differ: arms with distinct mechanism must produce
    # distinct hashes within at least one seed.
    af_violations: List[str] = []
    arm_pairs_must_differ = [
        ("ARM_STANDARD",   "ARM_REAL_VALUED"),
        ("ARM_STANDARD",   "ARM_DENSE_DG"),
        ("ARM_STANDARD",   "ARM_DENSE_REAL"),
        ("ARM_REAL_VALUED","ARM_DENSE_REAL"),
        ("ARM_DENSE_DG",   "ARM_DENSE_REAL"),
    ]
    for a1, a2 in arm_pairs_must_differ:
        h1_set = _arm_hash_set(arms_across, a1)
        h2_set = _arm_hash_set(arms_across, a2)
        # Per seed (zip), at least one pair must differ.
        any_diff = any(x != y for x, y in zip(h1_set, h2_set))
        if not any_diff and h1_set and h2_set:
            af_violations.append(f"{a1}/{a2}")
    if af_violations:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: identical arm_hash across all seeds "
                f"for: {af_violations}.  Mechanism arms are bit-identical.")

    # Mean recall per arm.
    R_DIRECT = _arm_recall_mean(arms_across, "ARM_DIRECT")
    R_STANDARD = _arm_recall_mean(arms_across, "ARM_STANDARD")
    R_REAL = _arm_recall_mean(arms_across, "ARM_REAL_VALUED")
    R_DENSE_DG = _arm_recall_mean(arms_across, "ARM_DENSE_DG")
    R_DENSE_REAL = _arm_recall_mean(arms_across, "ARM_DENSE_REAL")

    gap = R_DIRECT - R_STANDARD

    def close_frac(arm_recall: float) -> float:
        if abs(gap) < 1e-6:
            return 0.0
        return (arm_recall - R_STANDARD) / gap

    cf_real = close_frac(R_REAL)
    cf_dense_dg = close_frac(R_DENSE_DG)
    cf_dense_real = close_frac(R_DENSE_REAL)

    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} mode={RUN_MODE} "
        f"R_DIRECT={R_DIRECT:.3f} R_STANDARD={R_STANDARD:.3f} "
        f"R_REAL_VALUED={R_REAL:.3f} R_DENSE_DG={R_DENSE_DG:.3f} "
        f"R_DENSE_REAL={R_DENSE_REAL:.3f} "
        f"gap_DIR_STD={gap:+.3f}; "
        f"closeFrac REAL={cf_real:+.3f} DENSE_DG={cf_dense_dg:+.3f} "
        f"DENSE_REAL={cf_dense_real:+.3f}"
    )

    # Discriminator check: at sub-capacity regime, gap MUST be large.
    if abs(gap) < GAP_DIR_STD_MIN_FOR_DISCRIM:
        return ("MIDDLE_BAND",
                f"INCONCLUSIVE: DIRECT-STANDARD gap ({gap:+.3f}) below "
                f"discriminator threshold ({GAP_DIR_STD_MIN_FOR_DISCRIM}).  "
                f"Expected ~0.76 at this regime (rescue v1 baseline).  Cell "
                f"may not be in saturated-readout regime; verify smoke vs full "
                f"M/N_h ratios.  {summary}")

    # Hypothesis classification.
    h2_confirmed = cf_real >= CLOSURE_FRAC_MIN_FOR_CLAIM
    h1_confirmed = cf_dense_dg >= CLOSURE_FRAC_MIN_FOR_CLAIM
    h1xh2_synergy = (
        cf_dense_real >= CLOSURE_FRAC_SYNERGY
        and cf_real < CLOSURE_FRAC_MIN_FOR_CLAIM
        and cf_dense_dg < CLOSURE_FRAC_MIN_FOR_CLAIM
    )
    h_other = (
        cf_real < NOISE_TOLERANCE
        and cf_dense_dg < NOISE_TOLERANCE
        and cf_dense_real < NOISE_TOLERANCE
    )

    tags = []
    if h1_confirmed:
        tags.append("H1_SPARSE_OVERLAP_CONFIRMED")
    if h2_confirmed:
        tags.append("H2_SIGN_QUANT_CONFIRMED")
    if h1xh2_synergy:
        tags.append("H1xH2_SYNERGY")
    if h_other:
        tags.append("H_OTHER_NEW_PROBE_NEEDED")
    tag_str = ",".join(tags) if tags else "MIXED"

    # HARD_PASS criterion for this DIAGNOSTIC: any single hypothesis cleanly
    # explains the gap.  H1 / H2 / H1xH2 / H_OTHER are all informative
    # outcomes.  Mixed signals are MIDDLE_BAND.
    is_hard_pass = (
        (h1_confirmed and not h2_confirmed)
        or (h2_confirmed and not h1_confirmed)
        or h1xh2_synergy
        or h_other
    )

    if is_hard_pass:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic; tag={tag_str}): bottleneck class "
                f"identified.  {summary}")

    if h1_confirmed and h2_confirmed:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic; tag=H1_AND_H2_BOTH_LIFT): both "
                f"sparse-overlap and sign-quantization independently close "
                f">= {CLOSURE_FRAC_MIN_FOR_CLAIM} of gap.  {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND (diagnostic; tag={tag_str}): partial / mixed signal "
            f"-- no single hypothesis cleanly explains the gap.  {summary}")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((128, 128), dtype=np.float64)
    W_c = np.zeros((256, 256), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c")
    if W_h.shape == W_c.shape:
        raise AssertionError(f"shapes match: W_h={W_h.shape} W_c={W_c.shape}")


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 32
    N_h_test = 128
    k_test = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_test)))
    P = rng.randn(N_h_test, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=(4, N_raw)).astype(np.float64)
    h = _batched_sparse_pattern_separator(x, P, k_test)
    active = np.sum(np.abs(h) > 0, axis=1)
    if not np.all(active == k_test):
        raise AssertionError(
            f"k-WTA sparsity wrong: got {active} active, want {k_test}"
        )


def _selftest_dense_bipolar_is_dense() -> None:
    rng = np.random.RandomState(11)
    N_raw, N_h = 32, 64
    P = rng.randn(N_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=(3, N_raw)).astype(np.float64)
    h = _batched_dense_bipolar(x, P)
    active = np.sum(np.abs(h) > 0, axis=1)
    if not np.all(active == N_h):
        raise AssertionError(
            f"dense bipolar should have all N_h={N_h} bits active; got {active}"
        )
    if not np.all(np.isin(h, [-1.0, 1.0])):
        raise AssertionError("dense bipolar should be {-1,+1}-valued")


def _selftest_arm_pair_mechanism_distinct() -> None:
    """Pairs of arms with distinct mechanisms must produce DIFFERENT readouts
    at small scale (catches accidental bit-equivalence between arms)."""
    rng = np.random.RandomState(29)
    M_t, N_h_t, N_c_t, N_raw_t = 16, 64, 32, 16

    keys = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)

    # Build a saturated W_h to force the arms to actually differ on readout.
    k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))
    keys_sparse = _batched_sparse_pattern_separator(keys, P, k_active)
    keys_dense = _batched_dense_bipolar(keys, P)
    W_h_sparse = keys_sparse.T @ keys_sparse  # symmetric saturated
    W_h_dense = keys_dense.T @ keys_dense

    std_out = _hippo_readout("ARM_STANDARD", W_h_sparse, keys_sparse)
    real_out = _hippo_readout("ARM_REAL_VALUED", W_h_sparse, keys_sparse)
    dense_dg_out = _hippo_readout("ARM_DENSE_DG", W_h_dense, keys_dense)
    dense_real_out = _hippo_readout("ARM_DENSE_REAL", W_h_dense, keys_dense)

    # STANDARD vs REAL_VALUED: same encode, different readout fn.  Output
    # types differ ({-1,+1} vs real); their first-row sample MUST differ
    # by more than rounding.
    if np.allclose(std_out[0], real_out[0], atol=1e-6):
        raise AssertionError(
            "ARM_STANDARD and ARM_REAL_VALUED produced bit-identical readouts "
            "on the first row -- sign() is a no-op on this matmul output."
        )
    # STANDARD vs DENSE_DG: same readout fn, different encode -- must differ.
    if std_out.shape != dense_dg_out.shape:
        raise AssertionError("ARM_STANDARD vs ARM_DENSE_DG shape mismatch")
    if np.allclose(std_out[0], dense_dg_out[0], atol=1e-6):
        raise AssertionError(
            "ARM_STANDARD and ARM_DENSE_DG produced bit-identical readouts "
            "on the first row -- sparse vs dense encoding is a no-op."
        )
    # DENSE_DG vs DENSE_REAL: same encode, different readout.
    if np.allclose(dense_dg_out[0], dense_real_out[0], atol=1e-6):
        raise AssertionError(
            "ARM_DENSE_DG and ARM_DENSE_REAL produced bit-identical readouts."
        )


def _selftest_arm_hash_diverges() -> None:
    """End-to-end: at small scale, vals_c_react for the 5 arms must produce
    5 DISTINCT arm_hash values.  Catches the case where ARMs converge in
    cortex-projected space even if they differ in hippo space."""
    rng = np.random.RandomState(53)
    M_t, N_h_t, N_c_t, N_raw_t = 16, 64, 32, 16

    keys = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P_in = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc = rng.randn(N_c_t, N_h_t).astype(np.float64) / np.sqrt(N_h_t)

    arm_hashes: Dict[str, str] = {}
    k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))

    for arm_name in ARM_NAMES:
        if arm_name == "ARM_DIRECT":
            keys_h = _batched_sparse_pattern_separator(keys, P_in, k_active)
            vals_h = _batched_sparse_pattern_separator(vals, P_in, k_active)
        else:
            keys_h = _encode_hippo(arm_name, keys, P_in, N_h_t)
            vals_h = _encode_hippo(arm_name, vals, P_in, N_h_t)
        vals_c_raw = vals_h @ P_hc.T
        vals_c = _l2_normalize_batch(vals_c_raw)
        if arm_name == "ARM_DIRECT":
            vals_c_react = vals_c
        else:
            W_h = vals_h.T @ keys_h
            cues_h = keys_h  # no permutation in selftest
            vals_react_h = _hippo_readout(arm_name, W_h, cues_h)
            vals_c_react = _l2_normalize_batch(vals_react_h @ P_hc.T)
        arm_hashes[arm_name] = _arm_hash(arm_name, vals_c_react)

    # All 5 must be distinct.
    seen = {}
    for arm, h in arm_hashes.items():
        if h in seen:
            raise AssertionError(
                f"ARM_HASH COLLISION: {arm} and {seen[h]} produced "
                f"identical hash {h} in self-test.  Mechanisms are not "
                f"empirically distinguishable; META_RULE_AF violation would "
                f"fire on real cell."
            )
        seen[h] = arm


def _selftest_regime_check() -> None:
    """Confirm the cell's smoke and full regimes hold alpha_simple constant."""
    alpha_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    alpha_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if not (0.20 < alpha_full < 0.30):
        raise AssertionError(
            f"FULL alpha_simple={alpha_full:.3f} not in (0.20,0.30); "
            f"regime drifted from rescue v1's sub-capacity row."
        )
    if not (0.20 < alpha_smoke < 0.30):
        raise AssertionError(
            f"SMOKE alpha_simple={alpha_smoke:.3f} not in (0.20,0.30); "
            f"smoke regime does not match full."
        )


def _selftest_expected_n_units_matches_seeds() -> None:
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError(
            f"EXPECTED_N_UNITS={EXPECTED_N_UNITS} but n_arms*n_seeds="
            f"{len(ARM_NAMES)}*{len(SEEDS)}={expected}"
        )


def _selftest_arm_names_distinct() -> None:
    if len(set(ARM_NAMES)) != len(ARM_NAMES):
        raise AssertionError(f"ARM_NAMES has duplicates: {ARM_NAMES}")


def _selftest_positive_control_small() -> None:
    """ARM_DIRECT at sub-capacity must reach >= 0.95 recall on a small world.

    N_c chosen so alpha at cortex (M/N_c) ~ 0.4 -- well sub-capacity.  Earlier
    revision used N_c=256 with M=200 (alpha_c~0.78, near-saturated) which gave
    recall ~0.895 even on a CORRECT pipeline (the cortex was the bottleneck,
    not a code bug).  Calibrated against rescue v1's positive-control regime.
    """
    rng = np.random.RandomState(61)
    M_t, N_h_t, N_c_t, N_raw_t = 200, 256, 512, 32
    k_t = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))
    eta = 0.05

    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P_in_t = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(N_c_t, N_h_t).astype(np.float64) / np.sqrt(N_h_t)

    keys_h_t = _batched_sparse_pattern_separator(keys_raw_t, P_in_t, k_t)
    vals_h_t = _batched_sparse_pattern_separator(vals_raw_t, P_in_t, k_t)
    keys_c_t = _l2_normalize_batch(keys_h_t @ P_hc_t.T)
    vals_c_t = _l2_normalize_batch(vals_h_t @ P_hc_t.T)

    W_c = np.zeros((N_c_t, N_c_t), dtype=np.float64)
    W_c += eta * (vals_c_t.T @ keys_c_t)

    preds_raw = keys_c_t @ W_c.T
    preds = np.sign(preds_raw); preds[preds == 0] = 1.0
    preds_n = _l2_normalize_batch(preds)
    sims = preds_n @ vals_c_t.T
    argmax = np.argmax(sims, axis=1)
    n_hits = int(np.sum(argmax == np.arange(M_t)))
    recall = n_hits / float(M_t)
    if recall < 0.95:
        raise AssertionError(
            f"POSITIVE CONTROL FAIL: DIRECT-style at sub-cap small world "
            f"returned recall={recall:.3f}; expected >= 0.95.  Pipeline broken."
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_dense_bipolar_is_dense()
        _selftest_arm_pair_mechanism_distinct()
        _selftest_arm_hash_diverges()
        _selftest_regime_check()
        _selftest_expected_n_units_matches_seeds()
        _selftest_arm_names_distinct()
        _selftest_positive_control_small()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  M={M_ITEMS}  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity_sparse={HIPPO_SPARSITY_SPARSE}  "
        f"sparsity_dense={HIPPO_SPARSITY_DENSE}  "
        f"n_replay={N_REPLAY_PER_ITEM}  eta_c={ETA_CORTEX}  "
        f"alpha_simple={_alpha_simple(M_ITEMS,N_HIPPO):.3f}  "
        f"alpha_h={_alpha_h(M_ITEMS,N_HIPPO):.4f}  "
        f"seeds={SEEDS}  arms={ARM_NAMES}  "
        f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
        f"marker={_HARDENING_MARKER}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "_start_marker.txt").write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"v1_bottleneck_class_diagnostic=YES",
        encoding="utf-8",
    )

    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "N_h": N_HIPPO,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} M={M_ITEMS} N_h={N_HIPPO} "
              f"N_c={N_CORTEX} mode={RUN_MODE}...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n",
                encoding="utf-8",
            )
            raise
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

    # Per-arm aggregated rows for downstream landed-VET.
    per_arm_rows: List[Dict] = []
    for arm_name in ARM_NAMES:
        recalls = []
        for r in all_results:
            for a in r.get("arms", []):
                if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                    recalls.append(float(a["recall_cortex"]))
        if recalls:
            per_arm_rows.append({
                "arm_name": arm_name,
                "recall_mean": float(np.mean(recalls)),
                "recall_std": float(np.std(recalls)) if len(recalls) > 1 else 0.0,
                "n_seeds_ok": len(recalls),
            })

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} M={M_ITEMS} N_h={N_HIPPO} "
            f"N_c={N_CORTEX} arms={ARM_NAMES} mode={RUN_MODE} "
            f"alpha_simple={_alpha_simple(M_ITEMS,N_HIPPO):.3f} "
            f"alpha_h={_alpha_h(M_ITEMS,N_HIPPO):.4f} "
            f"bottleneck_class_diagnostic_v1"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "M": M_ITEMS,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "hippo_sparsity_dense": HIPPO_SPARSITY_DENSE,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "numpy",
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == len(SEEDS)
            and all(len(r.get("arms", [])) == len(ARM_NAMES) for r in all_results)
        ),
        "run_mode": RUN_MODE,
        "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
        "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
        "per_arm_rows": per_arm_rows,
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
    _main()
