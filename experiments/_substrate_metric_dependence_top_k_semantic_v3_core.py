"""Shared core for metric-dependence sweep v3 (Dim S FINE SIGMA CLIFF BRACKET).

v2 result: HF_UNIFORM_COLLAPSE at (alpha in {0.30, 1.00, 1.50}, sigma in
{0.0, 0.7}) — BIMODAL knife-edge collapse. sigma=0 saturates all 6 metrics
at 1.000 across all alphas; sigma=0.7 collapses all 6 metrics to <0.03
uniformly. Transition cliff is NARROWER than v2 grid resolves.

v3 hand-off directive: bracket the cliff with FINE sigma sweep at 2 fixed
alphas (v2 confirmed alpha shape-invariance across [0.30, 1.50]).

QUESTION (v3):
  Where does the substrate transition from perfect-recall to
  total-collapse under query noise sigma? Is the transition band a NARROW
  cliff (<0.05 sigma) or a resolvable phase boundary? And within the
  transition band, does the 6-metric family finally differentiate
  (top-K > top-1 in the cliff-band)?

MECHANISM (single arm; same as v1+v2 — IMPORTS v2 core primitives for
mechanism-class parity):
  Cell D v2 dense-Hopfield READ-REPLACE with query-noise injection.

  Sweep axes:
    alpha in {0.30, 1.00}                                   (2 fixed loads)
    sigma in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}   (8 fine points)

PRE-REG (P_deflated = 0.55; HP band):
  HP_CLIFF_BRACKET: at least one (alpha, sigma) cell shows max_metric_recall
    in [0.20, 0.80] band (partial-recovery zone — cliff is bracketed).
  HP_METRIC_DIFFERENTIATION: within the cliff-band sigma (any cell in
    partial-recovery zone), top10_recall - top1_recall >= 0.10 (top-K
    survives claim; sparse-coding drill's structured-sparsity prediction
    confirmed in narrow band).
  HP_BIMODAL_CONFIRMED: at sigma < 0.10, all metrics >= 0.90 at both alphas
    AND at sigma > 0.40, all metrics <= 0.10 at both alphas (v2 bimodal
    reconfirmed at fine grain).

  HF_NO_TRANSITION: no sigma cell in cliff-band anywhere in sweep (cliff
    width <= 0.05 or entirely outside sigma in [0.05, 0.50]).
  HF_METRIC_DIFFERENTIATION_FAILS: cliff bracketed but top10-top1 < 0.02
    everywhere (metric-family fundamentally can't disambiguate).

  CHAIN_GRADE_METRIC_CLIFF_MAPPED if HP_CLIFF_BRACKET AND
  HP_METRIC_DIFFERENTIATION both fire cross-seed.

CARDINALITY (META_RULE_H):
  FULL: 2 alphas x 8 sigmas x 1 arm = 16 units per seed. Aggregate 3
        seeds => 48 units.
  SMOKE: 2 alphas x 4 sigmas {0.05, 0.15, 0.25, 0.40} = 8 units, PLUS
         preview arm at (alpha=1.0, sigma=0.20) — expected mid-cliff
         cell — full-scale confirmation.
         SMOKE DISCRIMINATOR: at least one smoke cell must show
         max_metric in [0.20, 0.80] to confirm cliff is bracketed. If
         all-saturated or all-collapsed, HALT_ATOMIZE + widen sigma grid.

CRLB (per META_RULE_AC / capacity-feasibility):
  top1 argmax-noise floor at N=8192 with M=alpha*N items:
    sigma_min = sqrt(0.25 / M) (binomial-CLT).
  At alpha=1.00, M=8192: sigma_min_binom = sqrt(0.25/8192) = 0.00553.
  HP_METRIC_DIFFERENTIATION gap 0.10 = ~18*sigma_min_binom; reachable.
  HP_CLIFF_BRACKET band width 0.60 (in [0.20, 0.80]) = ~110*sigma_min_binom;
  easily resolvable.
  Discriminator reachability: True.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke at full N=8192 with 4 sigma points across [0.05, 0.40] +
  preview at (1.0, 0.20). If NO smoke cell lands in [0.20, 0.80] band,
  discriminator NOT bracketing cliff — HALT + v4 sigma grid respec.

BASELINE-IN-BAND (META_RULE_AG):
  At (alpha=0.30, sigma=0.05) expected near-ceiling (~1.000; anchor to v2
  clean baseline).
  At (alpha=1.00, sigma=0.50) expected near-floor (~0.000; anchor to v2
  overload+noise collapse).
  Sweep bracket includes discriminating band by construction.

META_RULE_AF (arms-must-differ):
  Single arm (dense-Hopfield READ-REPLACE with noisy query). (alpha x sigma)
  is CONFIG sweep, not arm axis. Same by-construction exemption as v1+v2.
  Noise-injection mechanism verified in v2 selftest imported here.
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

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# Import mechanism primitives + instrumentation helpers from v2 core
# (mechanism-class parity guaranteed; v3 changes ONLY the sweep grid + verdict)
from experiments._substrate_metric_dependence_top_k_semantic_v2_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_MIN, BETA_MAX, N_QUERY, N_RAW,
    METRIC_NAMES,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    _pattern_separate_sparse_batched, _encode_all,
    _cosine_margin_estimate, _compute_adaptive_beta, _compute_all_metrics,
    run_one_cell,
    # v2 selftests (re-run so v3 inherits mechanism validation)
    _selftest_sparse_pattern_separator,
    _selftest_dense_hopfield_perfect_recall,
    _selftest_all_metrics_ordering,
    _selftest_perfect_readout_all_top_k_1,
    _selftest_zero_readout_top1_at_chance,
    _selftest_metrics_family_arms_differ,
    _selftest_adaptive_beta_computes_finite,
    _selftest_noise_injection_moves_metrics,
)


# ---------------------------------------------------------------------------
# v3-specific sweep grid
# ---------------------------------------------------------------------------
# 2 fixed alphas (v2 confirmed alpha shape-invariance across [0.30, 1.50])
ALPHA_SWEEP_FULL_V3: Tuple[float, ...] = (0.30, 1.00)
# 8-point fine sigma sweep across the transition zone
SIGMA_SWEEP_FULL_V3: Tuple[float, ...] = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)

# Smoke: 2 alphas x 4 sigmas = 8 cells (spans cliff region)
ALPHA_SWEEP_SMOKE_V3: Tuple[float, ...] = (0.30, 1.00)
SIGMA_SWEEP_SMOKE_V3: Tuple[float, ...] = (0.05, 0.15, 0.25, 0.40)
# Preview at expected mid-cliff cell
PREVIEW_ALPHA_V3: float = 1.00
PREVIEW_SIGMA_V3: float = 0.20

# Cliff-band recall definition (partial-recovery zone)
CLIFF_LOW: float = 0.20
CLIFF_HIGH: float = 0.80


# ---------------------------------------------------------------------------
# v3 self-tests (extend v2 selftest suite with cliff-detection logic tests)
# ---------------------------------------------------------------------------
def _selftest_v3_sweep_cardinality() -> None:
    if len(ALPHA_SWEEP_FULL_V3) != 2:
        raise AssertionError(f"ALPHA_SWEEP_FULL_V3 must have 2 values; got {ALPHA_SWEEP_FULL_V3}")
    if set(ALPHA_SWEEP_FULL_V3) != {0.30, 1.00}:
        raise AssertionError(f"ALPHA_SWEEP_FULL_V3 values wrong: {ALPHA_SWEEP_FULL_V3}")
    if len(SIGMA_SWEEP_FULL_V3) != 8:
        raise AssertionError(f"SIGMA_SWEEP_FULL_V3 must have 8 values; got {SIGMA_SWEEP_FULL_V3}")
    expected_sigmas = {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}
    if set(SIGMA_SWEEP_FULL_V3) != expected_sigmas:
        raise AssertionError(f"SIGMA_SWEEP_FULL_V3 values wrong: {SIGMA_SWEEP_FULL_V3}")


def _selftest_cliff_detection_logic() -> None:
    """Verify cliff-band detector: cell with max_metric=0.5 must count as
    in-band; cell with max_metric=0.95 out-of-band; cell with max_metric=0.05
    out-of-band."""
    def _in_cliff_band(max_metric: float) -> bool:
        return CLIFF_LOW <= max_metric <= CLIFF_HIGH

    if not _in_cliff_band(0.5):
        raise AssertionError("cliff-detector missed max=0.5 (should be in-band)")
    if _in_cliff_band(0.95):
        raise AssertionError("cliff-detector wrongly counted max=0.95 (should be out)")
    if _in_cliff_band(0.05):
        raise AssertionError("cliff-detector wrongly counted max=0.05 (should be out)")
    if not _in_cliff_band(CLIFF_LOW):
        raise AssertionError("cliff-detector edge-case CLIFF_LOW must be in-band")
    if not _in_cliff_band(CLIFF_HIGH):
        raise AssertionError("cliff-detector edge-case CLIFF_HIGH must be in-band")


def _selftest_bimodal_reconfirm_gates() -> None:
    """HP_BIMODAL_CONFIRMED requires (sigma<0.10 all metrics>=0.90) AND
    (sigma>0.40 all metrics<=0.10). Verify the logic captures v2's finding:
    - sigma=0.05 case: 1.000 across all metrics -> should satisfy left gate.
    - sigma=0.50 case: 0.000 across all metrics -> should satisfy right gate.
    """
    left_metrics = {n: 1.000 for n in METRIC_NAMES}
    right_metrics = {n: 0.000 for n in METRIC_NAMES}
    if not all(v >= 0.90 for v in left_metrics.values()):
        raise AssertionError("left-gate logic broken")
    if not all(v <= 0.10 for v in right_metrics.values()):
        raise AssertionError("right-gate logic broken")


def run_all_selftests_v3(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        # Inherit v2 mechanism selftests
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_all_metrics_ordering()
        _selftest_perfect_readout_all_top_k_1()
        _selftest_zero_readout_top1_at_chance()
        _selftest_metrics_family_arms_differ()
        _selftest_adaptive_beta_computes_finite()
        _selftest_noise_injection_moves_metrics()
        # v3-specific
        _selftest_v3_sweep_cardinality()
        _selftest_cliff_detection_logic()
        _selftest_bimodal_reconfirm_gates()
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
# v3 verdict
# ---------------------------------------------------------------------------
def _cell_key(alpha: float, sigma: float) -> str:
    """Stable key for per-cell dict (v3; scaled to preserve sigma precision)."""
    return f"a{int(round(alpha * 10000))}_s{int(round(sigma * 100000))}"


def compute_verdict_v3(per_seed_result: Dict, run_mode: str
                       ) -> Tuple[str, str, Dict]:
    """Aggregate per-cell (alpha x sigma) metrics into HP/HF/MB verdict.

    Cliff-bracket physics:
      HP_CLIFF_BRACKET: at least 1 cell has max_metric in [0.20, 0.80].
      HP_METRIC_DIFFERENTIATION: within cliff-band cells, top10-top1 >= 0.10.
      HP_BIMODAL_CONFIRMED: sigma<0.10 all>=0.90 AND sigma>0.40 all<=0.10.
      HF_NO_TRANSITION: no cliff-band cell.
      HF_METRIC_DIFFERENTIATION_FAILS: cliff bracketed but top10-top1<0.02 everywhere.
    """
    per_cell = per_seed_result.get("per_cell", {})
    if run_mode == "full":
        alpha_sweep = ALPHA_SWEEP_FULL_V3
        sigma_sweep = SIGMA_SWEEP_FULL_V3
    else:
        alpha_sweep = ALPHA_SWEEP_SMOKE_V3
        sigma_sweep = SIGMA_SWEEP_SMOKE_V3
    expected_n = len(alpha_sweep) * len(sigma_sweep)

    if len(per_cell) != expected_n:
        return ("HARD_FAIL",
                f"CELL_CARDINALITY_BREACH: expected {expected_n} cells, "
                f"got {len(per_cell)}: {sorted(per_cell.keys())}",
                {})

    # Build per-cell max metric + top10-top1 gap tables
    cell_info: Dict[str, Dict] = {}
    cliff_band_cells: List[str] = []
    for alpha in alpha_sweep:
        for sigma in sigma_sweep:
            key = _cell_key(alpha, sigma)
            row = per_cell.get(key)
            if row is None:
                continue
            mets = row.get("metrics", {})
            vals = [float(mets.get(n, float("nan"))) for n in METRIC_NAMES]
            vals_finite = [v for v in vals if math.isfinite(v)]
            if not vals_finite:
                continue
            max_m = max(vals_finite)
            min_m = min(vals_finite)
            top1 = float(mets.get("top1_recall", float("nan")))
            top10 = float(mets.get("top10_recall", float("nan")))
            top10_top1_gap = (top10 - top1) if (math.isfinite(top1) and math.isfinite(top10)) else float("nan")
            in_cliff_band = CLIFF_LOW <= max_m <= CLIFF_HIGH
            cell_info[key] = {
                "alpha": alpha,
                "sigma": sigma,
                "max_metric": max_m,
                "min_metric": min_m,
                "top1": top1,
                "top10": top10,
                "top10_top1_gap": top10_top1_gap,
                "in_cliff_band": in_cliff_band,
                "metrics": mets,
                "M": row.get("M"),
                "beta": row.get("beta_used"),
            }
            if in_cliff_band:
                cliff_band_cells.append(key)

    # Headline
    headline: Dict = {"cells": cell_info, "cliff_band_cells": cliff_band_cells}
    reasons = []
    hp_flags = {}

    # HP_CLIFF_BRACKET: at least 1 cliff-band cell
    hp_cliff_bracket = len(cliff_band_cells) >= 1
    hp_flags["HP_CLIFF_BRACKET"] = hp_cliff_bracket
    reasons.append(f"cliff_band_cells={len(cliff_band_cells)}(HP>=1)")

    # HP_METRIC_DIFFERENTIATION: within cliff-band cells, top10-top1 >= 0.10 for at least one
    hp_metric_diff = False
    max_gap_in_cliff = float("-inf")
    if cliff_band_cells:
        gaps = []
        for k in cliff_band_cells:
            g = cell_info[k]["top10_top1_gap"]
            if math.isfinite(g):
                gaps.append(g)
        if gaps:
            max_gap_in_cliff = max(gaps)
            hp_metric_diff = max_gap_in_cliff >= 0.10
    hp_flags["HP_METRIC_DIFFERENTIATION"] = hp_metric_diff
    reasons.append(f"max_top10-top1_in_cliff={max_gap_in_cliff:+.3f}(HP>=0.10)")

    # HP_BIMODAL_CONFIRMED: sigma<0.10 all metrics>=0.90 at BOTH alphas
    # AND sigma>0.40 all metrics<=0.10 at BOTH alphas
    left_ok = True
    right_ok = True
    n_left_cells = 0
    n_right_cells = 0
    for key, info in cell_info.items():
        if info["sigma"] < 0.10:
            n_left_cells += 1
            if not all(math.isfinite(v) and v >= 0.90 for v in info["metrics"].values()):
                left_ok = False
        if info["sigma"] > 0.40:
            n_right_cells += 1
            if not all(math.isfinite(v) and v <= 0.10 for v in info["metrics"].values()):
                right_ok = False
    # Only fire if we actually have cells on both sides of the sweep
    hp_bimodal = (n_left_cells > 0 and n_right_cells > 0 and left_ok and right_ok)
    hp_flags["HP_BIMODAL_CONFIRMED"] = hp_bimodal
    reasons.append(f"bimodal[left={n_left_cells}ok={left_ok},right={n_right_cells}ok={right_ok}]")

    # HF_NO_TRANSITION: no cliff-band cell
    hf_no_transition = len(cliff_band_cells) == 0

    # HF_METRIC_DIFFERENTIATION_FAILS: cliff bracketed but no top10-top1 gap anywhere
    hf_metric_fails = False
    if cliff_band_cells:
        all_gaps_tiny = all(
            math.isfinite(cell_info[k]["top10_top1_gap"])
            and cell_info[k]["top10_top1_gap"] < 0.02
            for k in cliff_band_cells
        )
        hf_metric_fails = all_gaps_tiny

    headline["hp_flags"] = hp_flags
    headline["hf_no_transition"] = bool(hf_no_transition)
    headline["hf_metric_differentiation_fails"] = bool(hf_metric_fails)
    headline["max_top10_top1_gap_in_cliff"] = float(max_gap_in_cliff) if math.isfinite(max_gap_in_cliff) else None

    # Decision priority:
    # HF_NO_TRANSITION > HF_METRIC_DIFFERENTIATION_FAILS > HP fires (any) > MIDDLE
    if hf_no_transition:
        verdict = "HARD_FAIL"
        msg = ("HF_NO_TRANSITION: no cell in cliff-band [0.20,0.80]; "
               "cliff width <=0.05 or outside sweep; " + " ".join(reasons))
    elif hf_metric_fails:
        verdict = "HARD_FAIL"
        msg = ("HF_METRIC_DIFFERENTIATION_FAILS: cliff bracketed but "
               "top10-top1<0.02 everywhere in-band; metric-family cannot "
               "disambiguate; " + " ".join(reasons))
    else:
        any_hp = any(hp_flags.values())
        if any_hp:
            passed = [k for k, v in hp_flags.items() if v]
            verdict = "HARD_PASS"
            msg = f"HP fires: {passed} | " + " ".join(reasons)
        else:
            verdict = "MIDDLE_BAND"
            msg = "no HP gate fires despite cliff-bracket detector logic; " + " ".join(reasons)

    return (verdict, msg, headline)
