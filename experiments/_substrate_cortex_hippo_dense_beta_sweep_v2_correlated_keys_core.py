"""Shared core for cortex_hippo dense-Hopfield BETA SWEEP v2 CORRELATED KEYS.

Purpose: revive Atom 3 (Skunkworks 2026-07-01 declared MM due to universal
saturation at M=4096 with independent keys). Skunkworks-declared revival
criterion: M >= 32768 OR correlated keys (subspace-drawn). This cell uses
Path B (correlated keys via a d_sub-dimensional subspace) which is cheaper
+ substantively more interesting since correlated keys are the M3 real-world
regime.

Design (6 arms x 3 seeds; 1 M):
  ARM_BETA_5_INDEP           = independent keys (baseline; positive control); beta=5
  ARM_BETA_13_INDEP          = independent keys; beta=13
  ARM_BETA_5_CORR_SUB512     = correlated keys drawn from 512-dim subspace; beta=5
  ARM_BETA_13_CORR_SUB512    = correlated keys drawn from 512-dim subspace; beta=13
  ARM_BETA_5_CORR_SUB256     = correlated keys drawn from 256-dim subspace; beta=5
  ARM_BETA_13_CORR_SUB256    = correlated keys drawn from 256-dim subspace; beta=13

Fixed regime: N_c = 8192, M = 4000, beta in {5, 13} (from v1 top-2 arms).
Backend: numpy (CPU).

HP (per-seed):
  HP_BETA_DISCRIMINATES_CORRELATED: at CORR_SUB512 or CORR_SUB256, |recall(beta=5)
    - recall(beta=13)| >= 0.15 (beta axis IS discriminating in correlated regime).
  HP_INDEP_REPRODUCES_SATURATION: recall(ARM_BETA_5_INDEP) >= 0.95 AND
    recall(ARM_BETA_13_INDEP) >= 0.95 (reproduces v1 saturation; positive control).

HF:
  HF_CRUMBLE: any arm recall < 0.20 (mechanism broken).
  HF_INDEP_DIDNT_SATURATE: either INDEP arm < 0.95 (parent regime not reproduced;
    invalidates the "correlation breaks saturation" comparison).
  HF_META_RULE_AF: any arm-pair bit-identical (ceiling-tie exempt at 1.0 for
    same subspace_class pairs only).
  HF_CARDINALITY: n arms != 6.

MB: any HP condition partial (e.g., discriminates at SUB256 but not SUB512;
    or |delta| in [0.05, 0.15) at any correlated arm-pair).

CARDINALITY (META_RULE_H):
  FULL: 6 arms per seed cell.
  SMOKE: 6 arms per seed cell (single M; same as full arm count; scale differs).

Broken-PC: INDEP arms are the positive control — they MUST reproduce v1
saturation (>= 0.95). If they don't, the cell setup is broken; we can't
trust the correlated-key differentials.

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ;
SystemExit before Exception (no BaseException).
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Fixed config (v2 correlated-keys regime)
# ---------------------------------------------------------------------------
N_CORTEX_FULL = 8192
M_FULL = 4000
N_CORTEX_SMOKE = 2048
M_SMOKE = 1000

BETA_LO = 5.0    # v1 saturated arm 1
BETA_HI = 13.0   # v1 saturated arm 3 (near adaptive-nearest)

# Subspace sizes: INDEP = full N_c; CORR_SUB512 = 512-dim; CORR_SUB256 = 256-dim.
D_SUB_INDEP = None   # None -> full-dimensional independent Gaussian
D_SUB_512 = 512
D_SUB_256 = 256

# Discriminator threshold: |beta=5 recall - beta=13 recall| >= 0.15 in
# correlated regime => HP.
DISCRIMINATE_DELTA_HP = 0.15
DISCRIMINATE_DELTA_MB = 0.05

# Positive-control threshold (INDEP arms must saturate).
INDEP_SATURATION_FLOOR = 0.95

# Crumble floor.
CRUMBLE_FLOOR = 0.20

# Arm specifications: (arm_name, beta, d_sub, subspace_class).
ARM_SPECS = [
    ("ARM_BETA_5_INDEP",         BETA_LO, D_SUB_INDEP, "INDEP"),
    ("ARM_BETA_13_INDEP",        BETA_HI, D_SUB_INDEP, "INDEP"),
    ("ARM_BETA_5_CORR_SUB512",   BETA_LO, D_SUB_512,   "CORR_SUB512"),
    ("ARM_BETA_13_CORR_SUB512",  BETA_HI, D_SUB_512,   "CORR_SUB512"),
    ("ARM_BETA_5_CORR_SUB256",   BETA_LO, D_SUB_256,   "CORR_SUB256"),
    ("ARM_BETA_13_CORR_SUB256",  BETA_HI, D_SUB_256,   "CORR_SUB256"),
]

# ---------------------------------------------------------------------------
# Import shared helpers from existing beta-sweep core
# ---------------------------------------------------------------------------
from experiments._substrate_cortex_hippo_dense_beta_sweep_v1_core import (
    emit_heartbeat, write_start_marker, write_crash_metrics,
    _cosine_margin_estimate,
    _replace_read_numpy,
)


# ---------------------------------------------------------------------------
# Correlated-key generation
# ---------------------------------------------------------------------------
def _generate_keys_and_vals(m_items: int, n_c: int, d_sub, rng) -> Tuple[np.ndarray, np.ndarray]:
    """Generate M items of keys + vals in R^{n_c}, l2-normalized rows.

    If d_sub is None: independent Gaussian, so keys span the full n_c space.
    Off-diagonal similarity ~ 1/sqrt(n_c) (nearly orthogonal at large n_c).

    If d_sub is an int (< n_c): draw a random d_sub-dim orthonormal basis
    B (shape d_sub x n_c), then keys = coeffs @ B where coeffs shape (M, d_sub).
    This confines keys to a d_sub-dim subspace, forcing correlation: off-diag
    similarity ~ 1/sqrt(d_sub) which is larger than 1/sqrt(n_c) => less
    orthogonal => attention has to discriminate under correlation.

    Values are ALWAYS drawn from full-space independent Gaussian (unchanged);
    only keys carry the correlation structure.
    """
    if d_sub is None:
        keys_raw = rng.randn(m_items, n_c).astype(np.float64)
    else:
        if d_sub >= n_c:
            raise ValueError(f"d_sub={d_sub} must be < n_c={n_c}")
        # Random orthonormal basis of a d_sub-dim subspace of R^{n_c}.
        B_raw = rng.randn(n_c, d_sub).astype(np.float64)
        # QR decomposition -> Q shape (n_c, d_sub) has orthonormal columns.
        Q, _ = np.linalg.qr(B_raw)   # Q shape (n_c, d_sub)
        coeffs = rng.randn(m_items, d_sub).astype(np.float64)  # (M, d_sub)
        keys_raw = coeffs @ Q.T   # (M, n_c) — but confined to span(Q)
    keys = keys_raw / np.linalg.norm(keys_raw, axis=1, keepdims=True).clip(min=1e-12)

    vals_raw = rng.randn(m_items, n_c).astype(np.float64)
    vals = vals_raw / np.linalg.norm(vals_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys, vals


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_one_arm(seed: int, arm_name: str, beta: float, d_sub,
                subspace_class: str, m_items: int, n_c: int,
                attn_chunk: int, out_dir: Path) -> Dict:
    """Encode keys+vals per subspace regime; run one dense-attention READ at beta."""
    t0 = time.time()
    # Seed offset per arm keeps random draws independent across arms within a
    # seed cell, while remaining deterministic per (seed, arm_name).
    arm_seed_offset = hash(arm_name) & 0xFFFF
    rng = np.random.RandomState(seed + arm_seed_offset)

    try:
        keys, vals = _generate_keys_and_vals(m_items, n_c, d_sub, rng)
        cos_margin = _cosine_margin_estimate(keys)
        recall = _replace_read_numpy(keys, vals, beta, attn_chunk)
        arm_status = "OK"
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        keys = None
        vals = None
        cos_margin = float("nan")
        recall = float("nan")
        arm_status = f"ERROR: {type(exc).__name__}: {exc}"
    wall = time.time() - t0

    arm_dict = {
        "arm_name": arm_name,
        "beta_used": float(beta),
        "d_sub": int(d_sub) if d_sub is not None else -1,   # -1 sentinel for INDEP
        "subspace_class": subspace_class,
        "recall_cortex": float(recall),
        "cosine_margin_used": float(cos_margin),
        "m_items": int(m_items),
        "N_c": int(n_c),
        "wall_s": float(wall),
        "backend": "numpy",
        "arm_status": arm_status,
    }
    print(f"  [seed={seed} {arm_name}] recall={recall:.3f} beta={beta} d_sub={d_sub} "
          f"class={subspace_class} cos_margin={cos_margin:.3f} wall={wall:.1f}s "
          f"status={arm_status}", flush=True)
    emit_heartbeat(out_dir, unit_idx=hash(arm_name) & 0xFFFF,
                   total_units=len(ARM_SPECS),
                   elapsed_s=wall,
                   extra={"arm": arm_name, "recall": recall,
                          "beta": beta, "d_sub": int(d_sub) if d_sub is not None else -1,
                          "subspace_class": subspace_class,
                          "cos_margin": cos_margin})
    return arm_dict


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_indep_keys_are_orthogonal() -> None:
    """INDEP keys at large n_c should have off-diag |sim| ~ 1/sqrt(n_c).
    For n_c=2048, expected ~ 0.022; we check |off-diag mean| < 0.05."""
    rng = np.random.RandomState(7)
    keys, _ = _generate_keys_and_vals(64, 2048, D_SUB_INDEP, rng)
    sim = keys @ keys.T
    mask = ~np.eye(64, dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    if off_mean_abs > 0.05:
        raise AssertionError(
            f"INDEP keys off-diag |sim|={off_mean_abs:.4f} > 0.05; "
            f"orthogonality broken"
        )


def _selftest_corr_keys_have_higher_similarity() -> None:
    """SUB256 correlated keys at n_c=2048 should have off-diag |sim|
    significantly larger than INDEP keys. Expected: SUB256 ~ 1/sqrt(256)=0.062,
    INDEP ~ 1/sqrt(2048)=0.022. Check that CORR_SUB256 |off-diag| is at
    least 1.5x INDEP |off-diag|.
    """
    rng = np.random.RandomState(11)
    keys_indep, _ = _generate_keys_and_vals(64, 2048, D_SUB_INDEP, rng)
    rng2 = np.random.RandomState(11)   # same seed => same coeffs but different structure
    keys_corr, _ = _generate_keys_and_vals(64, 2048, 256, rng2)
    mask = ~np.eye(64, dtype=bool)
    sim_indep = float(np.abs(keys_indep @ keys_indep.T)[mask].mean())
    sim_corr = float(np.abs(keys_corr @ keys_corr.T)[mask].mean())
    if sim_corr < 1.5 * sim_indep:
        raise AssertionError(
            f"CORR_SUB256 |off-diag|={sim_corr:.4f} not >= 1.5x "
            f"INDEP |off-diag|={sim_indep:.4f}; correlation not encoded"
        )


def _selftest_replace_read_beta_effect() -> None:
    """Beta axis must have discernible effect on tiny correlated world.
    At d_sub=32, n_c=256, m=64, beta=1 vs beta=50 should differ."""
    rng = np.random.RandomState(23)
    keys, vals = _generate_keys_and_vals(64, 256, 32, rng)
    r_lo = _replace_read_numpy(keys, vals, beta=1.0, attn_chunk=64)
    r_hi = _replace_read_numpy(keys, vals, beta=50.0, attn_chunk=64)
    if abs(r_lo - r_hi) < 1e-9:
        raise AssertionError(
            f"beta has no effect on recall in correlated selftest: "
            f"r_lo=r_hi={r_lo}"
        )


def _selftest_arm_specs_cardinality() -> None:
    if len(ARM_SPECS) != 6:
        raise AssertionError(f"ARM_SPECS must be 6; got {len(ARM_SPECS)}")
    names = set(spec[0] for spec in ARM_SPECS)
    if len(names) != 6:
        raise AssertionError(f"ARM_SPECS names must be unique; got {names}")


def _selftest_qr_orthonormal() -> None:
    """QR-derived basis Q must have orthonormal columns."""
    rng = np.random.RandomState(31)
    B_raw = rng.randn(1024, 128).astype(np.float64)
    Q, _ = np.linalg.qr(B_raw)
    QtQ = Q.T @ Q
    off_max = float(np.abs(QtQ - np.eye(128)).max())
    if off_max > 1e-8:
        raise AssertionError(
            f"QR basis not orthonormal: max |Q^T Q - I| = {off_max}"
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_arm_specs_cardinality()
        _selftest_qr_orthonormal()
        _selftest_indep_keys_are_orthogonal()
        _selftest_corr_keys_have_higher_similarity()
        _selftest_replace_read_beta_effect()
        if f"seed_{seed_this_chunk}" not in anchor_name:
            raise AssertionError(
                f"anchor '{anchor_name}' missing seed_{seed_this_chunk}"
            )
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def compute_verdict(per_seed_result: Dict) -> Tuple[str, str, Dict]:
    """Compute per-seed verdict from arm list."""
    arms = per_seed_result.get("arms", [])
    if len(arms) != 6:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected 6 arms, "
                f"got {len(arms)}",
                {})

    arm_map = {a["arm_name"]: a for a in arms}

    # All arms status OK
    fail_reasons: List[str] = []
    warn_reasons: List[str] = []
    for a in arms:
        if a["arm_status"] != "OK":
            fail_reasons.append(
                f"{a['arm_name']} error: {a['arm_status']}"
            )

    # HF_CRUMBLE
    for a in arms:
        if a["recall_cortex"] < CRUMBLE_FLOOR:
            fail_reasons.append(
                f"HF_CRUMBLE: {a['arm_name']} recall="
                f"{a['recall_cortex']:.3f} < {CRUMBLE_FLOOR}"
            )

    # HF_INDEP_DIDNT_SATURATE (broken-PC)
    r5_indep = arm_map["ARM_BETA_5_INDEP"]["recall_cortex"]
    r13_indep = arm_map["ARM_BETA_13_INDEP"]["recall_cortex"]
    if r5_indep < INDEP_SATURATION_FLOOR:
        fail_reasons.append(
            f"HF_INDEP_DIDNT_SATURATE: ARM_BETA_5_INDEP recall={r5_indep:.3f} "
            f"< {INDEP_SATURATION_FLOOR} (positive control broken)"
        )
    if r13_indep < INDEP_SATURATION_FLOOR:
        fail_reasons.append(
            f"HF_INDEP_DIDNT_SATURATE: ARM_BETA_13_INDEP recall={r13_indep:.3f} "
            f"< {INDEP_SATURATION_FLOOR} (positive control broken)"
        )

    # META_RULE_AF bit-identity across arms.
    # Ceiling-tie exempt: both at 1.000 AND same subspace_class.
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            a_i, a_j = arms[i], arms[j]
            if abs(a_i["recall_cortex"] - a_j["recall_cortex"]) < 1e-6:
                is_ceiling = (
                    abs(a_i["recall_cortex"] - 1.0) < 1e-6 and
                    abs(a_j["recall_cortex"] - 1.0) < 1e-6
                )
                same_class = (a_i["subspace_class"] == a_j["subspace_class"])
                exempt = is_ceiling and same_class
                if not exempt:
                    fail_reasons.append(
                        f"META_RULE_AF: {a_i['arm_name']}="
                        f"{a_i['recall_cortex']:.6f} == "
                        f"{a_j['arm_name']}={a_j['recall_cortex']:.6f}"
                    )

    # Beta discriminates in correlated regime (HP condition).
    r5_c512 = arm_map["ARM_BETA_5_CORR_SUB512"]["recall_cortex"]
    r13_c512 = arm_map["ARM_BETA_13_CORR_SUB512"]["recall_cortex"]
    r5_c256 = arm_map["ARM_BETA_5_CORR_SUB256"]["recall_cortex"]
    r13_c256 = arm_map["ARM_BETA_13_CORR_SUB256"]["recall_cortex"]
    delta_c512 = abs(r5_c512 - r13_c512)
    delta_c256 = abs(r5_c256 - r13_c256)
    delta_indep = abs(r5_indep - r13_indep)
    max_corr_delta = max(delta_c512, delta_c256)

    # Positive controls saturating
    indep_saturated = (r5_indep >= INDEP_SATURATION_FLOOR and
                       r13_indep >= INDEP_SATURATION_FLOOR)

    # Discriminator fires (HP)
    beta_discriminates_hp = (max_corr_delta >= DISCRIMINATE_DELTA_HP)
    beta_partially_discriminates_mb = (
        max_corr_delta >= DISCRIMINATE_DELTA_MB
        and max_corr_delta < DISCRIMINATE_DELTA_HP
    )

    headline = {
        "recall_r5_indep": r5_indep,
        "recall_r13_indep": r13_indep,
        "recall_r5_corr_sub512": r5_c512,
        "recall_r13_corr_sub512": r13_c512,
        "recall_r5_corr_sub256": r5_c256,
        "recall_r13_corr_sub256": r13_c256,
        "delta_indep_r5_vs_r13": delta_indep,
        "delta_corr_sub512_r5_vs_r13": delta_c512,
        "delta_corr_sub256_r5_vs_r13": delta_c256,
        "max_corr_delta": max_corr_delta,
        "indep_saturated": indep_saturated,
        "beta_discriminates_hp": beta_discriminates_hp,
        "beta_partially_discriminates_mb": beta_partially_discriminates_mb,
    }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)

    if beta_discriminates_hp and indep_saturated:
        return ("HARD_PASS",
                f"BETA_AXIS_DISCRIMINATES_CORRELATED: max_corr_delta="
                f"{max_corr_delta:.3f} >= {DISCRIMINATE_DELTA_HP}; "
                f"INDEP positive controls saturate (r5={r5_indep:.3f}, "
                f"r13={r13_indep:.3f}); "
                f"delta_sub512={delta_c512:.3f}, delta_sub256={delta_c256:.3f}",
                headline)

    if beta_partially_discriminates_mb:
        warn_reasons.append(
            f"MB: max_corr_delta={max_corr_delta:.3f} in "
            f"[{DISCRIMINATE_DELTA_MB}, {DISCRIMINATE_DELTA_HP}); "
            f"partial discrimination"
        )

    # Universal saturation persists even with correlated keys
    if max_corr_delta < DISCRIMINATE_DELTA_MB and indep_saturated:
        warn_reasons.append(
            f"HF_STILL_SATURATED_CORR: max_corr_delta={max_corr_delta:.3f} "
            f"< {DISCRIMINATE_DELTA_MB}; correlation did NOT break "
            f"saturation (Atom 3 MM verdict stands; try higher M or lower d_sub)"
        )

    return ("MIDDLE_BAND", "; ".join(warn_reasons)[:800] or
            "no HP condition fired", headline)
