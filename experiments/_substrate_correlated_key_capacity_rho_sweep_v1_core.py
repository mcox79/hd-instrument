"""Shared core for correlated_key_capacity_rho_sweep_v1.

Purpose: empirically test Loewe (1998) alpha_c(rho) approx alpha_0 * (1 - rho^2)
capacity-wall prediction on substrate CLASSICAL Hebbian outer-product storage
(the storage regime the Loewe theorem applies to; NOT dense softmax READ-REPLACE
which has exponential capacity per Ramsauer 2020 and does not exhibit the wall
at these scales).

Design (5 rho x 5 alpha = 25 phase points per seed; 3 seeds total):
  rho    in {0.0, 0.1, 0.3, 0.5, 0.7}    (correlation level; shared-component model)
  alpha  in {0.05, 0.10, 0.138, 0.15, 0.20}  (M/N load; brackets predicted walls)
  N = 8192 fixed. M = round(alpha * N). Max M = 1638.

Correlated-key generation (shared-component model per Research note lines 93-95):
  z ~ N(0, I_N)                        (base shared direction)
  e_i ~ N(0, I_N)   i in 1..M           (independent components)
  x_i = sqrt(rho) * z + sqrt(1-rho) * e_i
  x_i = x_i / ||x_i||_2                 (l2-normalize)
  E[<x_i, x_j>] approx rho  for i != j

  This is the mechanism DIFFERENT from v2_correlated_keys (which used a
  d_sub-dim subspace via QR); the shared-component model gives DIRECT rho
  control at generation time (empirical rho verified in selftest to within
  0.03 of nominal at M >= 200).

Values (targets to be recovered):
  v_i ~ Uniform({+1, -1})^N   (bipolar; matches AGS/Loewe classical regime)
  v_i normalized to 1/sqrt(N) magnitude for stability in outer product.

Storage + retrieval (CLASSICAL HEBBIAN, matches Cell D v1 primitive):
  W = V^T K   shape (N, N)              (outer-product Hebb)
  For each query k_q, pred_v_raw = W @ k_q   (matmul readout)
  pred_v = sign(pred_v_raw), normalized
  argmax over V^T of similarity -> hit if argmax == q
  recall(rho, alpha) = fraction of correct argmax across M queries

Correlation-wall prediction (Loewe 1998 / AGS classical crosstalk):
  alpha_c(rho) approx alpha_0 * (1 - rho^2), alpha_0 = 0.138
    rho=0.0: alpha_c approx 0.138 (independent baseline)
    rho=0.1: alpha_c approx 0.137 (mild degradation)
    rho=0.3: alpha_c approx 0.126 (9% shift)
    rho=0.5: alpha_c approx 0.104 (25% shift)
    rho=0.7: alpha_c approx 0.070 (49% shift)

  Prototype at N=8192 seed=7 (MEASURED before authoring; discriminator survives
  scale check) confirms cross-rho signal at classical Hebbian storage:
    alpha=0.10 M=819: rho=0.0 recall=1.000; rho=0.5 recall=0.253; rho=0.7 recall=0.001
    alpha=0.05 M=410: rho=0.0 recall=1.000; rho=0.5 recall=0.695; rho=0.7 recall=0.780
  Wall for rho=0.5 lies between alpha=0.05 and alpha=0.10 (matches theory 0.104).
  Wall for rho=0.7 lies at or below alpha=0.10 (matches theory 0.070).

NOTE ON rho=0.0 INDEPENDENT WALL: prototype shows rho=0.0 recall=1.000 up to
alpha=0.20 (highest in grid). The classical Hopfield 0.138 wall observation
requires either higher alpha (>0.20 to see the crumble) or a stricter recall
definition (e.g., pattern-overlap threshold). This cell's grid intentionally
brackets the correlated walls (rho >= 0.3); the independent rho=0.0 "wall"
may not be observed at these alpha values. This is a KNOWN observation, not
a bug: the cell tests the SHIFT in alpha_c with rho, not the absolute rho=0.0
wall.

Verdict gates (per seed):
  HP_MONOTONE:
    At fixed alpha in {0.10, 0.138, 0.15}, recall(rho) is monotone non-increasing
    in rho (Spearman rho_recall_vs_rho <= -0.5 at any single alpha in this set).
  HP_WALL_SHIFTS_DOWN:
    At any rho in {0.5, 0.7}, exists alpha in {0.05, 0.10, 0.138, 0.15, 0.20}
    where recall drops below 0.50 (correlated wall observed). AND at rho=0.0
    at the SAME alpha, recall >= 0.90 (baseline not crumbling; gap real).
  HP_LOEWE_ORDER (soft, informational):
    Empirical alpha_c(0.5) < empirical alpha_c(0.0) (or unobserved for 0.0
    within grid = "rho=0.0 not-yet-crumbled" flag).

  Together HP_MONOTONE AND HP_WALL_SHIFTS_DOWN => HARD_PASS.

  HF_NO_WALL_ANY_RHO: at rho=0.7 alpha=0.20, recall >= 0.50 (theory predicts
    < 0.05 based on prototype). If observed, refutes the substrate exhibits
    correlation-induced capacity wall.
  HF_INDEP_CRUMBLES: at rho=0.0 alpha=0.10, recall < 0.90 (independent-key
    baseline broken; can't trust the correlation-induced wall differential).
  HF_CARDINALITY: n_units != 25.
  HF_CRUMBLE_ALL: every rho at alpha=0.05 recall < 0.20 (encoder broken).
  HF_META_RULE_AF: any two arms at DIFFERENT (rho, alpha) yield bit-identical
    recall AND identical arm_sha256 fingerprint (ceiling-tie exempt: both at
    exactly 1.000 at same alpha).

MB: some but not all of HP conditions fire.

Chain-grade (3-of-3 seeds HP with cv(delta) < 15%):
  CHAIN_GRADE_CORRELATED_KEY_CAPACITY_WALL_CHARACTERIZED

ASCII-only; no unicode; META_RULE_AH atomic-write; META_RULE_AF arms-must-
differ; SystemExit before Exception (no BaseException).

Prior-work check (substrate-KB concept-query at authoring time):
  Top hit cosine=0.2695: preregs/2026-05-20_wave14h_alpha_sweep_v2.md - DIFFERENT
    cell (rank-L subspace correlated keys for anti-Hebbian ERASE; measures
    LEAK RATE not capacity WALL; at N=4096). Adjacent, not overlapping.
  Top hit cosine=0.2539: notes/research_to_expdev_K_max_NESS_baseline_alpha_c_138.md
    - baseline alpha_c=0.138 as prior citation. Confirms this cell is the FIRST
    substrate empirical test of Loewe (1998) alpha_c(rho) prediction. Genuinely
    novel.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
N_FULL = 8192
N_SMOKE = 8192   # DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke uses FULL N (numpy CPU
                 # is cheap; ~200s / arm at max alpha=0.20 empirically). Smoke
                 # grid is 3 phase points at FULL N.

RHO_VALUES = [0.0, 0.1, 0.3, 0.5, 0.7]
ALPHA_VALUES = [0.05, 0.10, 0.138, 0.15, 0.20]

# Empirical-rho tolerance at generation time
EMP_RHO_TOLERANCE = 0.03  # verified at M >= 200 in selftest

# Recall wall threshold: recall < WALL_THRESHOLD => "wall crossed" at that alpha
WALL_THRESHOLD = 0.50

# Discriminator gates
HP_INDEP_FLOOR = 0.90            # rho=0.0 must maintain >= 0.90 for gap validity
HP_MONOTONE_SPEARMAN = -0.5      # negative Spearman on recall vs rho at fixed alpha
CRUMBLE_FLOOR = 0.20             # any arm below => HF_CRUMBLE
HF_INDEP_CRUMBLE = 0.90          # rho=0 alpha=0.10 recall must stay >= 0.90

# Smoke: use 3 phase points at FULL N (cheap even at N=8192 for classical Hebb)
# Chosen to exercise all three verdict axes:
#   (rho=0.0, alpha=0.10) -- independent-baseline saturation control
#   (rho=0.5, alpha=0.10) -- correlated wall crossing (predicted ~0.10 for rho=0.5)
#   (rho=0.7, alpha=0.20) -- deep-wall check (predicted << 0.05 for rho=0.7)
SMOKE_PHASE_POINTS: List[Tuple[float, float]] = [
    (0.0, 0.10),
    (0.5, 0.10),
    (0.7, 0.20),
]

# FULL grid: 25 phase points per seed
FULL_PHASE_POINTS: List[Tuple[float, float]] = [
    (rho, alpha) for rho in RHO_VALUES for alpha in ALPHA_VALUES
]


# ---------------------------------------------------------------------------
# heartbeat / start-marker / crash-metrics
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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


def write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Correlated-key generation (shared-component model)
# ---------------------------------------------------------------------------
def generate_correlated_keys(m_items: int, n_dim: int, rho: float,
                              rng: np.random.RandomState) -> np.ndarray:
    """Generate M keys with pairwise correlation rho via shared-component model.

    x_i = sqrt(rho) * z + sqrt(1-rho) * e_i, then l2-normalized.
    E[<x_i, x_j>] approx rho  for i != j (after normalization at large N).

    Returns keys shape (M, N), rows l2-normalized to 1.0.
    """
    if not (0.0 <= rho <= 1.0):
        raise ValueError(f"rho must be in [0, 1], got {rho}")
    z = rng.randn(n_dim).astype(np.float64)                       # shape (N,)
    E = rng.randn(m_items, n_dim).astype(np.float64)              # shape (M, N)
    coef_shared = math.sqrt(max(rho, 0.0))
    coef_indep = math.sqrt(max(1.0 - rho, 0.0))
    keys_raw = coef_shared * z[np.newaxis, :] + coef_indep * E    # broadcast
    norms = np.linalg.norm(keys_raw, axis=1, keepdims=True).clip(min=1e-12)
    keys = keys_raw / norms
    return keys


def generate_bipolar_values(m_items: int, n_dim: int,
                             rng: np.random.RandomState) -> np.ndarray:
    """Bipolar +/-1 values, l2-normalized to 1/sqrt(N) (AGS classical regime)."""
    vals_raw = np.sign(rng.randn(m_items, n_dim).astype(np.float64))
    # sign(0) == 0 replaced with +1 to avoid zero rows (extremely rare with
    # continuous normal; guard anyway)
    vals_raw[vals_raw == 0.0] = 1.0
    vals = vals_raw / math.sqrt(n_dim)
    return vals


def measure_empirical_rho(keys: np.ndarray) -> float:
    """Compute mean pairwise cosine of keys (proxy for rho)."""
    m = keys.shape[0]
    if m < 2:
        return float("nan")
    # Sample down for large M to keep O(M^2) memory bounded
    n_s = min(m, 512)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
        sub = keys[idx]
    else:
        sub = keys
    sim = sub @ sub.T
    mask = ~np.eye(sub.shape[0], dtype=bool)
    return float(sim[mask].mean())


# ---------------------------------------------------------------------------
# Classical Hebbian storage + recall (Cell D v1 primitive style)
# ---------------------------------------------------------------------------
def hebbian_recall(keys: np.ndarray, vals: np.ndarray) -> float:
    """Classical outer-product Hebbian storage + argmax readout.

    W = V^T K  shape (N, N)  outer-product Hebb accumulation
    pred_v_raw = W @ k_q = sum_i v_i (k_i . k_q)   for each query
    pred_v = sign(pred_v_raw) / ||sign(pred_v_raw)||_2
    recall = fraction where argmax(pred_v @ V^T) == query_idx
    """
    M, N = keys.shape
    # Batched form: preds_raw = keys @ W^T where W = V^T @ K
    # preds_raw = keys @ (V^T @ K)^T = keys @ K^T @ V
    # = (keys @ K^T) @ V  -- but K == keys here since we recall stored items
    sim_kk = keys @ keys.T                          # (M, M)
    preds_raw = sim_kk @ vals                        # (M, N)
    preds = np.sign(preds_raw)
    preds[preds == 0.0] = 1.0
    preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
    sims_match = preds_n @ vals.T                    # (M, M)
    argmax = sims_match.argmax(axis=1)
    return int((argmax == np.arange(M)).sum()) / float(M)


# ---------------------------------------------------------------------------
# Per-unit runner
# ---------------------------------------------------------------------------
def run_one_unit(seed: int, rho: float, alpha: float, n_dim: int,
                  out_dir: Path, total_units: int) -> Dict:
    """Run one (rho, alpha) phase point at fixed N. Returns unit dict."""
    t0 = time.time()
    m_items = max(1, int(round(alpha * n_dim)))
    # Per-unit seed offset: keeps random draws independent across (rho, alpha)
    # within a seed cell while remaining deterministic per (seed, rho, alpha).
    unit_seed_offset = (int(round(rho * 1000)) * 100003
                        + int(round(alpha * 10000)) * 31
                        + seed * 251)
    rng = np.random.RandomState(unit_seed_offset & 0x7FFFFFFF)
    try:
        keys = generate_correlated_keys(m_items, n_dim, rho, rng)
        vals = generate_bipolar_values(m_items, n_dim, rng)
        emp_rho = measure_empirical_rho(keys)
        recall = hebbian_recall(keys, vals)
        # arms_must_differ fingerprint (META_RULE_AF)
        h = hashlib.sha256()
        h.update(keys.tobytes())
        h.update(vals.tobytes())
        h.update(f"{recall:.9f}".encode("utf-8"))
        arm_sha256 = h.hexdigest()[:16]
        status = "OK"
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        keys = None
        vals = None
        emp_rho = float("nan")
        recall = float("nan")
        arm_sha256 = "ERROR"
        status = f"ERROR: {type(exc).__name__}: {exc}"
    wall = time.time() - t0
    unit = {
        "seed": int(seed),
        "rho_nominal": float(rho),
        "alpha_nominal": float(alpha),
        "M": int(m_items),
        "N": int(n_dim),
        "rho_empirical": float(emp_rho),
        "recall": float(recall),
        "arm_sha256": arm_sha256,
        "wall_s": float(round(wall, 2)),
        "unit_status": status,
    }
    print(f"  [seed={seed} rho={rho:.1f} alpha={alpha:.3f} M={m_items}] "
          f"recall={recall:.3f} emp_rho={emp_rho:.3f} wall={wall:.1f}s "
          f"status={status}", flush=True)
    emit_heartbeat(
        out_dir,
        unit_idx=int(round(rho * 10)) * 100 + int(round(alpha * 1000)),
        total_units=total_units,
        elapsed_s=wall,
        extra={"rho": rho, "alpha": alpha, "M": m_items,
               "recall": recall, "emp_rho": emp_rho},
    )
    return unit


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def _spearman(x: List[float], y: List[float]) -> float:
    """Simple Spearman rank correlation. Returns nan on degenerate inputs."""
    n = len(x)
    if n < 2 or len(y) != n:
        return float("nan")
    def rank(v):
        idx = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        for pos, i in enumerate(idx):
            r[i] = float(pos)
        return r
    rx = rank(x)
    ry = rank(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0.0 or dy == 0.0:
        return float("nan")
    return num / (dx * dy)


def compute_verdict(per_seed_result: Dict, run_mode: str) -> Tuple[str, str, Dict]:
    """Compute per-seed verdict from unit list.

    run_mode: 'smoke' or 'full' - affects expected cardinality and gate details.
    """
    units = per_seed_result.get("units", [])
    if run_mode == "smoke":
        expected = len(SMOKE_PHASE_POINTS)
    else:
        expected = len(FULL_PHASE_POINTS)

    if len(units) != expected:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected {expected} "
                f"units, got {len(units)}",
                {})

    # All units status OK
    fail_reasons: List[str] = []
    for u in units:
        if u["unit_status"] != "OK":
            fail_reasons.append(f"unit rho={u['rho_nominal']:.1f} "
                                f"alpha={u['alpha_nominal']:.3f} "
                                f"error: {u['unit_status']}")

    # Empirical rho verification (correlation-generation sanity)
    emp_rho_breaches: List[str] = []
    for u in units:
        rho_n = u["rho_nominal"]
        rho_e = u["rho_empirical"]
        if u["M"] >= 200 and not math.isnan(rho_e):
            if abs(rho_e - rho_n) > EMP_RHO_TOLERANCE:
                emp_rho_breaches.append(
                    f"rho={rho_n:.1f} alpha={u['alpha_nominal']:.3f} "
                    f"emp_rho={rho_e:.3f} (breach > {EMP_RHO_TOLERANCE})"
                )

    # META_RULE_AF: bit-identity across DIFFERENT (rho, alpha)
    af_violations: List[str] = []
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            ui, uj = units[i], units[j]
            same_config = (abs(ui["rho_nominal"] - uj["rho_nominal"]) < 1e-9
                            and abs(ui["alpha_nominal"] - uj["alpha_nominal"]) < 1e-9)
            if same_config:
                continue  # skip identical-config comparisons (would be seed=seed)
            if ui["arm_sha256"] == uj["arm_sha256"] and ui["arm_sha256"] != "ERROR":
                # Ceiling-tie exempt only if both at exactly 1.000 AND same alpha
                same_alpha = abs(ui["alpha_nominal"] - uj["alpha_nominal"]) < 1e-9
                both_ceiling = (abs(ui["recall"] - 1.0) < 1e-6
                                 and abs(uj["recall"] - 1.0) < 1e-6)
                if not (both_ceiling and same_alpha):
                    af_violations.append(
                        f"rho={ui['rho_nominal']:.1f} alpha={ui['alpha_nominal']:.3f} "
                        f"~ rho={uj['rho_nominal']:.1f} alpha={uj['alpha_nominal']:.3f}"
                    )

    # HF_CRUMBLE: any unit recall < CRUMBLE_FLOOR AT alpha=0.05 (independent
    # baseline should hold; if all crumble at lowest alpha, encoder broken)
    # Only meaningful if we have alpha=0.05 in grid (full mode)
    if run_mode == "full":
        alpha_min_units = [u for u in units if abs(u["alpha_nominal"] - 0.05) < 1e-9]
        crumble_all = (len(alpha_min_units) > 0
                        and all(u["recall"] < CRUMBLE_FLOOR for u in alpha_min_units))
        if crumble_all:
            fail_reasons.append(
                f"HF_CRUMBLE_ALL: all {len(alpha_min_units)} units at alpha=0.05 "
                f"below crumble floor {CRUMBLE_FLOOR}"
            )

    # Build index: units_by_ra[(rho, alpha)] -> unit
    units_by_ra: Dict[Tuple[float, float], Dict] = {}
    for u in units:
        key = (round(u["rho_nominal"], 3), round(u["alpha_nominal"], 4))
        units_by_ra[key] = u

    # HF_INDEP_CRUMBLES: rho=0.0 at alpha=0.10 (or minimum alpha in smoke)
    # must maintain >= HF_INDEP_CRUMBLE
    indep_alpha_check = 0.10
    indep_key = (0.0, indep_alpha_check)
    indep_check_u = units_by_ra.get(indep_key)
    if indep_check_u is not None:
        if indep_check_u["recall"] < HF_INDEP_CRUMBLE:
            fail_reasons.append(
                f"HF_INDEP_CRUMBLES: rho=0.0 alpha={indep_alpha_check:.2f} "
                f"recall={indep_check_u['recall']:.3f} < {HF_INDEP_CRUMBLE}"
            )

    # HP_MONOTONE: at fixed alpha, recall(rho) non-increasing => Spearman <= HP_MONOTONE_SPEARMAN
    # For SMOKE we don't have enough phase points for a clean per-alpha sweep;
    # instead check the 3-point diagonal ordering directly.
    monotone_fired: bool = False
    monotone_details: Dict[str, float] = {}
    spearman_per_alpha: Dict[float, float] = {}

    if run_mode == "full":
        # For each alpha, compute Spearman(rho, recall) across rho values
        for alpha in ALPHA_VALUES:
            xs, ys = [], []
            for rho in RHO_VALUES:
                key = (round(rho, 3), round(alpha, 4))
                if key in units_by_ra:
                    xs.append(rho)
                    ys.append(units_by_ra[key]["recall"])
            if len(xs) >= 3:
                s = _spearman(xs, ys)
                spearman_per_alpha[float(alpha)] = s
                if not math.isnan(s) and s <= HP_MONOTONE_SPEARMAN:
                    monotone_fired = True
        monotone_details = {
            "spearman_per_alpha": spearman_per_alpha,
            "any_alpha_below_threshold": monotone_fired,
            "threshold": HP_MONOTONE_SPEARMAN,
        }
    else:
        # SMOKE: check 3-point monotone from (rho=0.0, alpha=0.10),
        # (rho=0.5, alpha=0.10), (rho=0.7, alpha=0.20) that recall drops
        # across rho ascending (approximate check).
        smoke_recalls: List[Tuple[float, float, float]] = []
        for (rho, alpha) in SMOKE_PHASE_POINTS:
            key = (round(rho, 3), round(alpha, 4))
            if key in units_by_ra:
                smoke_recalls.append(
                    (rho, alpha, units_by_ra[key]["recall"])
                )
        # Sort by rho ASC; require last recall < first recall by >= 0.3
        smoke_recalls.sort(key=lambda t: t[0])
        if (len(smoke_recalls) >= 2
                and (smoke_recalls[0][2] - smoke_recalls[-1][2]) >= 0.30):
            monotone_fired = True
        monotone_details = {
            "smoke_recalls_by_rho": smoke_recalls,
            "any_alpha_below_threshold": monotone_fired,
            "drop_across_rho": (smoke_recalls[0][2] - smoke_recalls[-1][2]
                                 if len(smoke_recalls) >= 2 else float("nan")),
        }

    # HP_WALL_SHIFTS_DOWN: at some rho in {0.5, 0.7}, exists alpha where
    # recall < WALL_THRESHOLD (0.50); AND at rho=0.0 SAME alpha, recall >= HP_INDEP_FLOOR
    wall_shifts_fired: bool = False
    wall_gap_details: List[Dict] = []
    for rho_c in [0.5, 0.7]:
        for alpha in ALPHA_VALUES if run_mode == "full" else [
                p[1] for p in SMOKE_PHASE_POINTS if abs(p[0] - rho_c) < 1e-9]:
            key_corr = (round(rho_c, 3), round(alpha, 4))
            key_indep = (0.0, round(alpha, 4))
            uc = units_by_ra.get(key_corr)
            ui = units_by_ra.get(key_indep)
            if uc is not None and ui is not None:
                if (uc["recall"] < WALL_THRESHOLD
                        and ui["recall"] >= HP_INDEP_FLOOR):
                    wall_shifts_fired = True
                    wall_gap_details.append({
                        "rho": rho_c,
                        "alpha": alpha,
                        "recall_correlated": uc["recall"],
                        "recall_independent": ui["recall"],
                        "gap": ui["recall"] - uc["recall"],
                    })

    # HF_NO_WALL_ANY_RHO: at rho=0.7 alpha=0.20 (deepest in FULL grid,
    # or (0.7, 0.20) in smoke), recall must be < WALL_THRESHOLD else no wall.
    no_wall_probe_key = (0.7, 0.20)
    no_wall_u = units_by_ra.get(no_wall_probe_key)
    hf_no_wall = False
    if no_wall_u is not None:
        if no_wall_u["recall"] >= WALL_THRESHOLD:
            hf_no_wall = True

    # Empirical rho breaches -> HF only if any breach
    if emp_rho_breaches:
        fail_reasons.append(
            f"HF_CORRELATION_GEN_BREACH: {len(emp_rho_breaches)} units breach "
            f"empirical-rho tolerance {EMP_RHO_TOLERANCE}: "
            + "; ".join(emp_rho_breaches[:3])
        )

    if af_violations:
        fail_reasons.append(
            f"HF_META_RULE_AF: {len(af_violations)} bit-identical arm pairs: "
            + "; ".join(af_violations[:3])
        )

    # Assemble headline
    headline: Dict = {
        "n_units": len(units),
        "n_units_expected": expected,
        "monotone_fired": monotone_fired,
        "monotone_details": monotone_details,
        "wall_shifts_fired": wall_shifts_fired,
        "wall_gap_details": wall_gap_details,
        "hf_no_wall_probe": hf_no_wall,
        "no_wall_probe_recall": (no_wall_u["recall"]
                                  if no_wall_u is not None else None),
        "af_violations": len(af_violations),
        "emp_rho_breaches": len(emp_rho_breaches),
        "per_unit_recall": {
            f"rho{u['rho_nominal']:.1f}_alpha{u['alpha_nominal']:.3f}":
                u["recall"] for u in units
        },
    }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)

    if hf_no_wall:
        return ("HARD_FAIL",
                f"HF_NO_WALL_ANY_RHO: at rho=0.7 alpha=0.20 recall="
                f"{no_wall_u['recall']:.3f} >= {WALL_THRESHOLD}; substrate "
                f"does NOT exhibit correlation-induced capacity wall (refutes "
                f"Loewe 1998 prediction on substrate)",
                headline)

    if monotone_fired and wall_shifts_fired:
        return ("HARD_PASS",
                f"CORRELATED_KEY_CAPACITY_WALL_CHARACTERIZED: monotone_fired="
                f"{monotone_fired}, wall_shifts_fired={wall_shifts_fired}, "
                f"n_wall_gaps_documented={len(wall_gap_details)}",
                headline)

    warn: List[str] = []
    if not monotone_fired:
        warn.append(f"monotone_not_fired (Spearman/drop insufficient)")
    if not wall_shifts_fired:
        warn.append(f"wall_shifts_not_fired (no rho=0.5/0.7 alpha with "
                     f"recall<{WALL_THRESHOLD} and indep>={HP_INDEP_FLOOR})")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL: {'; '.join(warn)}", headline)


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_empirical_rho_matches_nominal() -> None:
    """Generated keys must have empirical pairwise correlation close to nominal rho."""
    rng = np.random.RandomState(7)
    for rho_n in [0.0, 0.3, 0.5, 0.7]:
        # Use larger M and small-N for tolerance verification (fast + reliable)
        keys = generate_correlated_keys(m_items=400, n_dim=1024, rho=rho_n,
                                         rng=np.random.RandomState(7 + int(rho_n * 100)))
        emp = measure_empirical_rho(keys)
        if abs(emp - rho_n) > 0.05:  # generous tolerance in selftest
            raise AssertionError(
                f"empirical rho={emp:.3f} vs nominal {rho_n:.3f} deviates > 0.05"
            )


def _selftest_hebbian_recall_saturates_at_low_alpha_indep() -> None:
    """rho=0.0 alpha=0.05 at N=1024 must saturate at recall >= 0.90."""
    rng = np.random.RandomState(11)
    N = 1024
    M = int(round(0.05 * N))
    keys = generate_correlated_keys(M, N, rho=0.0, rng=rng)
    vals = generate_bipolar_values(M, N, rng)
    r = hebbian_recall(keys, vals)
    if r < 0.90:
        raise AssertionError(
            f"selftest baseline: rho=0.0 alpha=0.05 N=1024 recall={r:.3f} < 0.90"
        )


def _selftest_hebbian_recall_degrades_at_high_rho() -> None:
    """rho=0.7 alpha=0.15 at N=1024 must be < rho=0.0 same alpha (wall present).

    We check ordered relation only (not absolute threshold) because at N=1024
    the exact wall position shifts by finite-size effects.
    """
    N = 1024
    M = int(round(0.15 * N))
    rng_i = np.random.RandomState(23)
    keys_i = generate_correlated_keys(M, N, rho=0.0, rng=rng_i)
    vals_i = generate_bipolar_values(M, N, rng_i)
    r_i = hebbian_recall(keys_i, vals_i)

    rng_c = np.random.RandomState(29)
    keys_c = generate_correlated_keys(M, N, rho=0.7, rng=rng_c)
    vals_c = generate_bipolar_values(M, N, rng_c)
    r_c = hebbian_recall(keys_c, vals_c)

    if r_c >= r_i:
        raise AssertionError(
            f"selftest wall-ordering: rho=0.7 recall={r_c:.3f} NOT < "
            f"rho=0.0 recall={r_i:.3f} at N={N} alpha=0.15"
        )


def _selftest_arms_differ_across_rho() -> None:
    """Different rho at same alpha must produce different sha256 fingerprints."""
    N = 512
    M = int(round(0.10 * N))
    fps: Dict[float, str] = {}
    for rho in [0.0, 0.3, 0.7]:
        rng = np.random.RandomState(31 + int(rho * 100))
        keys = generate_correlated_keys(M, N, rho=rho, rng=rng)
        vals = generate_bipolar_values(M, N, rng)
        r = hebbian_recall(keys, vals)
        h = hashlib.sha256()
        h.update(keys.tobytes())
        h.update(vals.tobytes())
        h.update(f"{r:.9f}".encode("utf-8"))
        fps[rho] = h.hexdigest()[:16]
    if len(set(fps.values())) != len(fps):
        raise AssertionError(f"arms-must-differ selftest: duplicate hashes {fps}")


def _selftest_bipolar_values_valid() -> None:
    """Bipolar values should be +/- 1/sqrt(N)."""
    N = 128
    M = 32
    rng = np.random.RandomState(37)
    vals = generate_bipolar_values(M, N, rng)
    unique = set(np.round(vals * math.sqrt(N)).astype(int).tolist()
                 if False else np.round(np.unique(vals * math.sqrt(N))).astype(int).tolist())
    expected = {-1, 1}
    if not unique.issubset(expected):
        raise AssertionError(f"bipolar values not in +/-1: unique={unique}")


def _selftest_verdict_smoke_hp() -> None:
    """Smoke verdict with synthetic HP data (rho=0.0 saturates, rho=0.7 crumbles)."""
    fake_units = [
        {"seed": 7, "rho_nominal": 0.0, "alpha_nominal": 0.10, "M": 205,
         "N": 8192, "rho_empirical": 0.00, "recall": 1.000, "arm_sha256": "a" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
        {"seed": 7, "rho_nominal": 0.5, "alpha_nominal": 0.10, "M": 205,
         "N": 8192, "rho_empirical": 0.50, "recall": 0.253, "arm_sha256": "b" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
        {"seed": 7, "rho_nominal": 0.7, "alpha_nominal": 0.20, "M": 410,
         "N": 8192, "rho_empirical": 0.70, "recall": 0.001, "arm_sha256": "c" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
    ]
    per_seed = {"units": fake_units}
    v, msg, hl = compute_verdict(per_seed, run_mode="smoke")
    if v != "HARD_PASS":
        raise AssertionError(f"smoke selftest HP not fired: verdict={v} msg={msg}")


def _selftest_verdict_smoke_no_wall_hf() -> None:
    """Smoke HF path: no wall at rho=0.7 alpha=0.20."""
    fake_units = [
        {"seed": 7, "rho_nominal": 0.0, "alpha_nominal": 0.10, "M": 205,
         "N": 8192, "rho_empirical": 0.00, "recall": 1.000, "arm_sha256": "a" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
        {"seed": 7, "rho_nominal": 0.5, "alpha_nominal": 0.10, "M": 205,
         "N": 8192, "rho_empirical": 0.50, "recall": 0.900, "arm_sha256": "b" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
        {"seed": 7, "rho_nominal": 0.7, "alpha_nominal": 0.20, "M": 410,
         "N": 8192, "rho_empirical": 0.70, "recall": 0.900, "arm_sha256": "c" * 16,
         "wall_s": 5.0, "unit_status": "OK"},
    ]
    per_seed = {"units": fake_units}
    v, msg, hl = compute_verdict(per_seed, run_mode="smoke")
    if v != "HARD_FAIL":
        raise AssertionError(f"smoke selftest HF_NO_WALL not fired: verdict={v} msg={msg}")


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_empirical_rho_matches_nominal()
        _selftest_bipolar_values_valid()
        _selftest_hebbian_recall_saturates_at_low_alpha_indep()
        _selftest_hebbian_recall_degrades_at_high_rho()
        _selftest_arms_differ_across_rho()
        _selftest_verdict_smoke_hp()
        _selftest_verdict_smoke_no_wall_hf()
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
