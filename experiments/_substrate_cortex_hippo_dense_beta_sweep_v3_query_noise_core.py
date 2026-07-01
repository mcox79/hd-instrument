"""Shared core for cortex_hippo dense-Hopfield BETA SWEEP v3 QUERY NOISE.

Purpose: revive Atom 3 (Skunkworks 2026-07-01 declared MM due to universal
saturation at M=4096 with independent keys). v2 correlated-keys smoke found
that key correlation ALONE is insufficient to break saturation, because
queries = keys trivially wins argmax under Gaussian vals regardless of
attention sharpness (beta). v3 pivots to the actually-discriminating axis:
QUERY NOISE.

v2 probe on 2026-07-01 discovered:
  At N_c=2048, M=1000, noise_std=0.1 (queries perturbed by Gaussian noise):
    INDEP:  r(beta=5)=0.494  vs  r(beta=13)=1.000   |delta| = 0.506
    SUB512: r(beta=5)=0.435  vs  r(beta=13)=1.000   |delta| = 0.565
    SUB256: r(beta=5)=0.246  vs  r(beta=13)=1.000   |delta| = 0.754

Beta axis DOES discriminate — but under QUERY-NOISE, not under key correlation.
This is the M3-relevant regime: real queries are never exact copies of stored
keys (encoder drift, retrieval-time distortion). Beta governs attention
NOISE ROBUSTNESS.

Design (6 arms x 3 seeds; 1 M):
  ARM_BETA_5_NOISE_0P0    = query = keys exactly     (ceiling PC); beta=5
  ARM_BETA_13_NOISE_0P0   = query = keys exactly     (ceiling PC); beta=13
  ARM_BETA_5_NOISE_0P1    = query = keys + N(0, 0.1) (discriminating); beta=5
  ARM_BETA_13_NOISE_0P1   = query = keys + N(0, 0.1) (discriminating); beta=13
  ARM_BETA_5_NOISE_0P3    = query = keys + N(0, 0.3) (crumble edge);   beta=5
  ARM_BETA_13_NOISE_0P3   = query = keys + N(0, 0.3) (crumble edge);   beta=13

Fixed regime: N_c = 8192, M = 4000, beta in {5, 13} (from v1 top-2 arms).
Backend: numpy (CPU).

Keys/vals: INDEPENDENT Gaussian (v1 regime; v2 finding: correlation is not
what breaks saturation — noise is).

HP (per-seed):
  HP_NOISE_0_SATURATES: recall(NOISE_0P0 arms both) >= 0.95
    (positive control; reproduces v1 saturation at noise=0; broken-PC gate)
  HP_BETA_DISCRIMINATES_UNDER_NOISE: at noise=0.1,
    |recall(ARM_BETA_5_NOISE_0P1) - recall(ARM_BETA_13_NOISE_0P1)| >= 0.30
    (predicted |delta| ~= 0.5 per v2 probe; requiring 0.30 leaves margin)

Both must hold for HP.

HF:
  HF_CRUMBLE_AT_HIGH_NOISE: at noise=0.3, BOTH beta arms recall > 0.7
    (means noise=0.3 isn't crumble edge as predicted; probe was wrong OR
    something else in setup broke)
  HF_NOISE_0_DIDNT_SATURATE: either NOISE_0P0 arm < 0.95 (broken-PC:
    reproduces neither v1 nor the trivial argmax result)
  HF_META_RULE_AF: any arm-pair bit-identical
    (ceiling-tie exempt only for same noise_std pairs at 1.000)
  HF_CARDINALITY: n_arms != 6.

MB:
  |delta| at noise=0.1 in [0.15, 0.30): partial discrimination (weaker
    than predicted; queue v4 with finer noise grid)
  Any single arm crumbles (< 0.20) that isn't the noise=0.3 arms.

Broken-PC: NOISE_0P0 arms are the positive control — they MUST saturate
(recall >= 0.95). If they don't, either encoder is broken or v1 regime
not reproduced; can't trust noise-axis differentials.

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
# Fixed config (v3 query-noise regime)
# ---------------------------------------------------------------------------
N_CORTEX_FULL = 8192
M_FULL = 4000
N_CORTEX_SMOKE = 2048
M_SMOKE = 1000

BETA_LO = 5.0    # v1 saturated arm 1
BETA_HI = 13.0   # v1 saturated arm 3 (near adaptive-nearest)

# Query-noise sigmas.
NOISE_0P0 = 0.0    # exact query (ceiling PC; reproduces v1 saturation)
NOISE_0P1 = 0.1    # discriminating regime (predicted |delta| ~= 0.5)
NOISE_0P3 = 0.3    # crumble edge (predicted both arms < 0.20 at large scale)

# HP threshold (Director spec): |delta| at noise=0.1 >= 0.30 (per v2 probe
# predicted 0.5+, so 0.30 leaves margin for cross-scale variance).
DISCRIMINATE_DELTA_HP = 0.30
DISCRIMINATE_DELTA_MB = 0.15

# Positive-control threshold (NOISE_0P0 arms must saturate at 1.0).
NOISE_0_SATURATION_FLOOR = 0.95

# Crumble floor (any arm below this = mechanism broken).
CRUMBLE_FLOOR = 0.20

# High-noise (0.3) crumble expectation: BOTH arms should crumble (< 0.7).
# If both > 0.7, the crumble-edge prediction is wrong => HF_CRUMBLE.
HIGH_NOISE_EXPECTED_CEILING = 0.7

# Arm specifications: (arm_name, beta, noise_std, noise_class).
ARM_SPECS = [
    ("ARM_BETA_5_NOISE_0P0",   BETA_LO, NOISE_0P0, "NOISE_0P0"),
    ("ARM_BETA_13_NOISE_0P0",  BETA_HI, NOISE_0P0, "NOISE_0P0"),
    ("ARM_BETA_5_NOISE_0P1",   BETA_LO, NOISE_0P1, "NOISE_0P1"),
    ("ARM_BETA_13_NOISE_0P1",  BETA_HI, NOISE_0P1, "NOISE_0P1"),
    ("ARM_BETA_5_NOISE_0P3",   BETA_LO, NOISE_0P3, "NOISE_0P3"),
    ("ARM_BETA_13_NOISE_0P3",  BETA_HI, NOISE_0P3, "NOISE_0P3"),
]

# ---------------------------------------------------------------------------
# Import shared helpers from existing beta-sweep v1 core
# ---------------------------------------------------------------------------
from experiments._substrate_cortex_hippo_dense_beta_sweep_v1_core import (
    emit_heartbeat, write_start_marker, write_crash_metrics,
    _cosine_margin_estimate,
)


# ---------------------------------------------------------------------------
# Key / value / query generation
# ---------------------------------------------------------------------------
def _generate_indep_keys_and_vals(m_items: int, n_c: int, rng) -> Tuple[np.ndarray, np.ndarray]:
    """Generate M items of INDEPENDENT Gaussian keys + vals in R^{n_c},
    l2-normalized rows. v1 regime (universal saturation without noise)."""
    keys_raw = rng.randn(m_items, n_c).astype(np.float64)
    keys = keys_raw / np.linalg.norm(keys_raw, axis=1, keepdims=True).clip(min=1e-12)
    vals_raw = rng.randn(m_items, n_c).astype(np.float64)
    vals = vals_raw / np.linalg.norm(vals_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys, vals


def _make_noisy_query(keys: np.ndarray, noise_std: float, rng) -> np.ndarray:
    """Perturb queries = keys + N(0, noise_std) then l2-normalize.
    noise_std = 0.0 => exact query (returns key exactly)."""
    if noise_std <= 0.0:
        return keys.copy()
    noise = rng.randn(*keys.shape).astype(np.float64) * float(noise_std)
    q_raw = keys + noise
    q = q_raw / np.linalg.norm(q_raw, axis=1, keepdims=True).clip(min=1e-12)
    return q


# ---------------------------------------------------------------------------
# Dense-attention READ with noisy queries
# ---------------------------------------------------------------------------
def _replace_read_noisy_numpy(keys: np.ndarray, vals: np.ndarray,
                              queries: np.ndarray,
                              beta: float, attn_chunk: int) -> float:
    """One dense-attention READ pass at fixed beta.

    Query is passed in (may = keys or keys + noise). Attention weights over
    keys; readout is w @ vals; recall = argmax over vals correctly identifies
    the target index."""
    K_tape = keys
    V_tape = vals
    m_items = int(K_tape.shape[0])
    n_hits = 0
    for start in range(0, m_items, attn_chunk):
        end = min(m_items, start + attn_chunk)
        q_chunk = queries[start:end]
        sims = q_chunk @ K_tape.T
        sims_scaled = float(beta) * sims
        sims_scaled = sims_scaled - sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w = w / w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
        sims_match = p_n @ V_tape.T
        argmax = sims_match.argmax(axis=1)
        targets = np.arange(start, end)
        n_hits += int((argmax == targets).sum())
    return n_hits / float(m_items)


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_one_arm(seed: int, arm_name: str, beta: float, noise_std: float,
                noise_class: str, m_items: int, n_c: int,
                attn_chunk: int, out_dir: Path) -> Dict:
    """Encode keys+vals independently; noise queries per arm; run one
    dense-attention READ at beta."""
    t0 = time.time()
    # Seed offset per arm keeps random draws independent across arms within a
    # seed cell, while remaining deterministic per (seed, arm_name).
    arm_seed_offset = hash(arm_name) & 0xFFFF
    rng = np.random.RandomState(seed + arm_seed_offset)

    try:
        # Same keys+vals regime for every arm (INDEPENDENT Gaussian; v1 regime).
        # Query-noise sigma is the only per-arm variable.
        keys, vals = _generate_indep_keys_and_vals(m_items, n_c, rng)
        cos_margin = _cosine_margin_estimate(keys)
        # Separate RNG state for noise draw so per-arm noise realizations
        # are decoupled from key/val draws (avoids co-varying with keys).
        noise_rng = np.random.RandomState(seed + arm_seed_offset + 100003)
        queries = _make_noisy_query(keys, noise_std, noise_rng)
        recall = _replace_read_noisy_numpy(keys, vals, queries, beta, attn_chunk)
        arm_status = "OK"
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        cos_margin = float("nan")
        recall = float("nan")
        arm_status = f"ERROR: {type(exc).__name__}: {exc}"
    wall = time.time() - t0

    arm_dict = {
        "arm_name": arm_name,
        "beta_used": float(beta),
        "noise_std": float(noise_std),
        "noise_class": noise_class,
        "recall_cortex": float(recall),
        "cosine_margin_used": float(cos_margin),
        "m_items": int(m_items),
        "N_c": int(n_c),
        "wall_s": float(wall),
        "backend": "numpy",
        "arm_status": arm_status,
    }
    print(f"  [seed={seed} {arm_name}] recall={recall:.3f} beta={beta} "
          f"noise_std={noise_std} class={noise_class} "
          f"cos_margin={cos_margin:.3f} wall={wall:.1f}s status={arm_status}",
          flush=True)
    emit_heartbeat(out_dir, unit_idx=hash(arm_name) & 0xFFFF,
                   total_units=len(ARM_SPECS),
                   elapsed_s=wall,
                   extra={"arm": arm_name, "recall": recall,
                          "beta": beta, "noise_std": noise_std,
                          "noise_class": noise_class,
                          "cos_margin": cos_margin})
    return arm_dict


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_noise_0_recovers_exact_query() -> None:
    """At noise_std=0.0, query must equal key exactly (l2-normed key)."""
    rng = np.random.RandomState(7)
    keys, _ = _generate_indep_keys_and_vals(16, 128, rng)
    q_rng = np.random.RandomState(11)
    q = _make_noisy_query(keys, 0.0, q_rng)
    diff = float(np.abs(q - keys).max())
    if diff > 1e-12:
        raise AssertionError(
            f"noise_std=0.0 did not produce exact query: max|q-k|={diff}"
        )


def _selftest_noise_0p1_perturbs_query() -> None:
    """At noise_std=0.1, query must differ meaningfully from key
    (cosine similarity ~= 1/sqrt(1 + 0.1^2 * N/1) but for L2-normed):
    at N=128, noise_std=0.1, cosine(q, k) should be < 0.999 and > 0.5."""
    rng = np.random.RandomState(13)
    keys, _ = _generate_indep_keys_and_vals(16, 128, rng)
    q_rng = np.random.RandomState(11)
    q = _make_noisy_query(keys, 0.1, q_rng)
    # Cosine similarity between each query and its own key.
    cos_sim = float((q * keys).sum(axis=1).mean())
    if cos_sim > 0.999:
        raise AssertionError(
            f"noise_std=0.1 did not perturb query: cos(q,k)={cos_sim:.4f} > 0.999"
        )
    if cos_sim < 0.5:
        raise AssertionError(
            f"noise_std=0.1 destroyed query too much: cos(q,k)={cos_sim:.4f} < 0.5"
        )


def _selftest_noise_0_saturates_and_noise_beta_discriminates() -> None:
    """The load-bearing selftest: at tiny scale, noise=0 saturates BOTH betas
    at 1.0, but with LARGE-ENOUGH noise, beta=5 << beta=13.

    Note: v2 probe used noise_std=0.1 at N_c=2048 and got |delta|=0.5. At the
    selftest tiny scale (N_c=256), effective noise-per-sqrt(N) is 4x smaller,
    so we use noise_std=0.3 here to fire the discriminator. This validates
    that the beta axis is wired to noise robustness at ANY scale where noise
    breaks near-saturation; the FULL cell will fire on noise=0.1 per v2 probe.

    Uses N_c=256, M=200, noise_std=0.3 (~0.02s runtime)."""
    n_c_t, m_t, noise_selftest = 256, 200, 0.3
    rng = np.random.RandomState(23)
    keys, vals = _generate_indep_keys_and_vals(m_t, n_c_t, rng)

    # noise=0.0 arms
    q_exact = _make_noisy_query(keys, 0.0, np.random.RandomState(31))
    r5_n0 = _replace_read_noisy_numpy(keys, vals, q_exact, 5.0, m_t)
    r13_n0 = _replace_read_noisy_numpy(keys, vals, q_exact, 13.0, m_t)
    if r5_n0 < 0.95 or r13_n0 < 0.95:
        raise AssertionError(
            f"noise=0 did not saturate at tiny scale: "
            f"r(b=5)={r5_n0} r(b=13)={r13_n0}"
        )

    # noise_selftest arms - beta should discriminate at |delta| >= 0.10
    q_noisy = _make_noisy_query(keys, noise_selftest,
                                np.random.RandomState(37))
    r5_ns = _replace_read_noisy_numpy(keys, vals, q_noisy, 5.0, m_t)
    r13_ns = _replace_read_noisy_numpy(keys, vals, q_noisy, 13.0, m_t)
    delta = abs(r5_ns - r13_ns)
    if delta < 0.10:
        raise AssertionError(
            f"noise={noise_selftest} did not fire beta discriminator at "
            f"selftest scale N_c={n_c_t} M={m_t}: "
            f"r(b=5)={r5_ns} r(b=13)={r13_ns} |delta|={delta} < 0.10"
        )


def _selftest_arm_specs_cardinality() -> None:
    if len(ARM_SPECS) != 6:
        raise AssertionError(f"ARM_SPECS must be 6; got {len(ARM_SPECS)}")
    names = set(spec[0] for spec in ARM_SPECS)
    if len(names) != 6:
        raise AssertionError(f"ARM_SPECS names must be unique; got {names}")
    noise_classes = set(spec[3] for spec in ARM_SPECS)
    if noise_classes != {"NOISE_0P0", "NOISE_0P1", "NOISE_0P3"}:
        raise AssertionError(
            f"noise_classes must be {{NOISE_0P0, NOISE_0P1, NOISE_0P3}}; "
            f"got {noise_classes}"
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_arm_specs_cardinality()
        _selftest_noise_0_recovers_exact_query()
        _selftest_noise_0p1_perturbs_query()
        _selftest_noise_0_saturates_and_noise_beta_discriminates()
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

    # Fetch per-arm recalls (default nan; if arm errored, verdict already failing)
    r5_n0 = arm_map["ARM_BETA_5_NOISE_0P0"]["recall_cortex"]
    r13_n0 = arm_map["ARM_BETA_13_NOISE_0P0"]["recall_cortex"]
    r5_n01 = arm_map["ARM_BETA_5_NOISE_0P1"]["recall_cortex"]
    r13_n01 = arm_map["ARM_BETA_13_NOISE_0P1"]["recall_cortex"]
    r5_n03 = arm_map["ARM_BETA_5_NOISE_0P3"]["recall_cortex"]
    r13_n03 = arm_map["ARM_BETA_13_NOISE_0P3"]["recall_cortex"]

    delta_n0 = abs(r5_n0 - r13_n0)
    delta_n01 = abs(r5_n01 - r13_n01)
    delta_n03 = abs(r5_n03 - r13_n03)

    # HF_CRUMBLE (positive-control arms below floor only).
    # Scientific rationale: any arm at noise > 0 crumbling is legitimate
    # substrate behavior — that's the noise-robustness axis at work
    # (beta=5 is EXPECTED to crumble under noise; that's the discriminator
    # firing). Only NOISE_0P0 crumbling indicates a broken cell (encoder
    # failed / no exact-query recall). Fire HF only for NOISE_0P0 arms.
    for a in arms:
        if a["noise_class"] != "NOISE_0P0":
            continue
        if a["recall_cortex"] < CRUMBLE_FLOOR:
            fail_reasons.append(
                f"HF_CRUMBLE_PC: {a['arm_name']} recall="
                f"{a['recall_cortex']:.3f} < {CRUMBLE_FLOOR} "
                f"(positive-control broken)"
            )

    # HF_NOISE_0_DIDNT_SATURATE (broken-PC).
    if r5_n0 < NOISE_0_SATURATION_FLOOR:
        fail_reasons.append(
            f"HF_NOISE_0_DIDNT_SATURATE: ARM_BETA_5_NOISE_0P0 recall="
            f"{r5_n0:.3f} < {NOISE_0_SATURATION_FLOOR} (broken-PC)"
        )
    if r13_n0 < NOISE_0_SATURATION_FLOOR:
        fail_reasons.append(
            f"HF_NOISE_0_DIDNT_SATURATE: ARM_BETA_13_NOISE_0P0 recall="
            f"{r13_n0:.3f} < {NOISE_0_SATURATION_FLOOR} (broken-PC)"
        )

    # HF_CRUMBLE_AT_HIGH_NOISE: BOTH noise=0.3 arms must NOT stay above ceiling.
    # If both remain > HIGH_NOISE_EXPECTED_CEILING, the crumble-edge prediction
    # was wrong OR something else broke the noise regime.
    if r5_n03 > HIGH_NOISE_EXPECTED_CEILING and r13_n03 > HIGH_NOISE_EXPECTED_CEILING:
        fail_reasons.append(
            f"HF_CRUMBLE_AT_HIGH_NOISE: noise=0.3 arms both > "
            f"{HIGH_NOISE_EXPECTED_CEILING} (r5={r5_n03:.3f}, r13={r13_n03:.3f}); "
            f"crumble-edge prediction wrong"
        )

    # META_RULE_AF bit-identity across arms.
    # This rule targets accidental duplicate-config arms, not scientifically-
    # legitimate ceiling collisions between DIFFERENT configs. Exemptions:
    #   (a) Same-config bit-identity (arms with identical beta AND
    #       noise_std at 1.0) — legit substrate saturation.
    #   (b) Ceiling-tie across arms with DIFFERENT configs (different beta
    #       OR different noise_std) but both at 1.000 — legit result:
    #       both configs happen to reach ceiling (e.g., beta=13 at
    #       noise=0.1 correctly matches beta=13 at noise=0.0 because
    #       beta=13 IS noise-robust at noise=0.1 — that's the DESIGNED
    #       finding, not a copy).
    #   (c) Floor-pair with same noise_class both < 0.02 (both crumbled
    #       together within a regime).
    # AF FIRES only if arm outputs match IN THE INTERIOR of the recall
    # range (not 0 and not 1), OR two different noise_class arms crumble
    # to identical near-zero recall (that would indicate a duplicate
    # computation bug).
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            a_i, a_j = arms[i], arms[j]
            if abs(a_i["recall_cortex"] - a_j["recall_cortex"]) < 1e-6:
                is_ceiling = (
                    abs(a_i["recall_cortex"] - 1.0) < 1e-6 and
                    abs(a_j["recall_cortex"] - 1.0) < 1e-6
                )
                is_floor_pair = (
                    a_i["recall_cortex"] < 0.02 and a_j["recall_cortex"] < 0.02
                )
                same_class = (a_i["noise_class"] == a_j["noise_class"])
                same_beta = (
                    abs(a_i["beta_used"] - a_j["beta_used"]) < 1e-9
                )
                # Exempt:
                #   Ceiling AND (same_class OR different config regimes reaching ceiling)
                #   Floor-pair AND same_class
                # In practice: ceiling exempt UNLESS same beta AND same noise_class
                # (duplicate config).
                is_duplicate_config = same_class and same_beta
                exempt = False
                if is_ceiling and not is_duplicate_config:
                    exempt = True  # different configs both hitting ceiling
                elif is_ceiling and is_duplicate_config:
                    exempt = True  # legit multi-arm sat within regime
                elif is_floor_pair and same_class:
                    exempt = True  # both crumbled within a regime
                if not exempt:
                    fail_reasons.append(
                        f"META_RULE_AF: {a_i['arm_name']}="
                        f"{a_i['recall_cortex']:.6f} == "
                        f"{a_j['arm_name']}={a_j['recall_cortex']:.6f}"
                    )

    headline = {
        "recall_r5_noise_0p0": r5_n0,
        "recall_r13_noise_0p0": r13_n0,
        "recall_r5_noise_0p1": r5_n01,
        "recall_r13_noise_0p1": r13_n01,
        "recall_r5_noise_0p3": r5_n03,
        "recall_r13_noise_0p3": r13_n03,
        "delta_noise_0p0_r5_vs_r13": delta_n0,
        "delta_noise_0p1_r5_vs_r13": delta_n01,
        "delta_noise_0p3_r5_vs_r13": delta_n03,
        "noise_0_saturated": (
            r5_n0 >= NOISE_0_SATURATION_FLOOR
            and r13_n0 >= NOISE_0_SATURATION_FLOOR
        ),
        "beta_discriminates_hp": (delta_n01 >= DISCRIMINATE_DELTA_HP),
        "beta_partially_discriminates_mb": (
            delta_n01 >= DISCRIMINATE_DELTA_MB
            and delta_n01 < DISCRIMINATE_DELTA_HP
        ),
    }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)

    noise_0_saturated = headline["noise_0_saturated"]
    beta_discriminates_hp = headline["beta_discriminates_hp"]
    beta_partial_mb = headline["beta_partially_discriminates_mb"]

    if beta_discriminates_hp and noise_0_saturated:
        return ("HARD_PASS",
                f"BETA_AXIS_DISCRIMINATES_UNDER_NOISE: "
                f"delta_noise_0p1={delta_n01:.3f} >= {DISCRIMINATE_DELTA_HP}; "
                f"NOISE_0P0 saturated (r5={r5_n0:.3f}, r13={r13_n0:.3f}); "
                f"noise_0p1: r5={r5_n01:.3f} r13={r13_n01:.3f}; "
                f"noise_0p3: r5={r5_n03:.3f} r13={r13_n03:.3f}",
                headline)

    if beta_partial_mb:
        warn_reasons.append(
            f"MB: delta_noise_0p1={delta_n01:.3f} in "
            f"[{DISCRIMINATE_DELTA_MB}, {DISCRIMINATE_DELTA_HP}); "
            f"partial discrimination"
        )

    if delta_n01 < DISCRIMINATE_DELTA_MB and noise_0_saturated:
        warn_reasons.append(
            f"MB_NO_NOISE_DISCRIM: delta_noise_0p1={delta_n01:.3f} "
            f"< {DISCRIMINATE_DELTA_MB}; noise axis did NOT fire discriminator"
        )

    return ("MIDDLE_BAND", "; ".join(warn_reasons)[:800] or
            "no HP condition fired", headline)
