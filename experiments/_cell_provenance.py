"""Shared metrics-PROVENANCE fields for experiment cells (Skunkworks metrics-provenance gate, 2026-06-17).

Makes "is this metrics.json the output of the run I think, via the path/method I require?" a FIELD CHECK, not an
inference. Every cell emits the same structured block so the cert gate + the dispatch one-true-test read it programmatically
(ending the stale / wrong-method / wrong-mode remote-vs-local inference that bit the team today).

Fields (the cert-owner 4-point gate + commit bonus):
  run_mode        -- full | smoke                                  (MODE; GATE-0)
  branch_path     -- which code path executed (cell-specific str)  (PATH)
  metrics_source  -- method that produced the numbers              (METHOD; METHOD-GATE)
  run_started_utc -- iso8601 at run start                          (IDENTITY/FRESHNESS: is this file from THIS run?)
  cell_commit     -- git short hash of the running cell            (which CODE produced it)

Deterministic; no LLM. ASCII-only.
"""
from __future__ import annotations
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def now_utc() -> str:
    """iso8601 UTC timestamp; capture at run start for run_started_utc."""
    return datetime.now(timezone.utc).isoformat()


def cell_commit() -> str:
    """Best-effort git short hash of the running cell (on the remote = the commit the runner actually pulled)."""
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(_REPO),
                              capture_output=True, text=True, timeout=5).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def provenance_fields(run_mode: str, branch_path: str, metrics_source: str, run_started_utc: str) -> dict:
    """The structured provenance block to spread into a cell's metrics dict."""
    return {"run_mode": run_mode, "branch_path": branch_path, "metrics_source": metrics_source,
            "run_started_utc": run_started_utc, "cell_commit": cell_commit()}


def gate0_self_check(run_mode: str, metrics_source: str, n_cells_declared: int, n_cells_emitted: int,
                     elapsed_s: float, is_smoke: bool) -> dict:
    """GATE-0 PRODUCER self-check (Skunkworks C2 self-certification engine, 2026-06-18; the substrate-autonomy path).

    The cell DETERMINISTICALLY self-attests, at the source, the GATE-0 conditions the cert layer would otherwise
    check post-hoc -- so an early-exit / smoke-default / cost-model run flags ITSELF, not only at cert time.
    Pairs with the atomizer's consumer-side gate0_field_check (defense-in-depth: GATE-0 at producer AND consumer).

    DETERMINISTIC hard checks (the catch surface):
      - n_cells_emitted == n_cells_declared   (early-exit / crashed-mid-grid -> emitted < declared)
      - run_mode == 'full' when not is_smoke   (run-mode-smoke-default ran synthetic/short)
      - metrics_source startswith 'measured_'  (cost-model / synthetic / null -> not measured)
    RECORDED (inspectable, NOT a hard gate -- a per-workload time model is not deterministic, per the
      gate0-plausibility-per-cell-WORKLOAD lesson: wall-time is a TELL not a GATE):
      - elapsed_s, n_cells_declared, n_cells_emitted  (so elapsed-per-cell is inspectable downstream)

    Returns a dict to spread into metrics under key 'gate0_self_check'. 11th-rule clean; no LLM; ASCII.
    """
    reasons = []
    if n_cells_emitted != n_cells_declared:
        reasons.append(f"n_cells_emitted({n_cells_emitted})!=n_cells_declared({n_cells_declared})_INCOMPLETE")
    if not is_smoke and str(run_mode) != "full":
        reasons.append(f"run_mode({run_mode})!=full_when_not_smoke")
    if not str(metrics_source or "").lower().startswith("measured_"):
        reasons.append(f"metrics_source({metrics_source})_not_measured_")
    return {
        "pass": len(reasons) == 0,
        "reasons": reasons,
        "n_cells_declared": n_cells_declared,
        "n_cells_emitted": n_cells_emitted,
        "elapsed_s": elapsed_s,
        "is_smoke": bool(is_smoke),
    }


def discrimination_self_check(discriminates: bool, reference_value, floor, ceiling, reason: str = "") -> dict:
    """DISCRIMINATION-REGIME self-check (Skunkworks B-epsilon self-cert engine, 2026-06-18; encodes
    degenerate-regime-not-refutation [audit lesson 79, CONFIRMED 7-witness] as a DETERMINISTIC self-applied gate).

    The CELL -- which alone knows its metric -- self-attests whether its regime DISCRIMINATES: the reference
    point measurably ABOVE the floor AND BELOW the ceiling (NOT saturated / collapsed / one-hot / under-stressed).
    A NON-discriminating regime is a NON_TEST, not a verdict: a PASS/HARD_FAIL on a metric that cannot
    discriminate is meaningless ("a measurement is a test only if its discriminating range covers reality").

    Pairs with the consumer-side discrimination_gate (the atomizer forces the effective verdict -> NON_TEST when
    discriminates==False). Generalizes the per-cell discrimination guard hand-written in A3/8a/refuse-gate into
    ONE shared producer-attest + consumer-enforce gate. 11th-rule clean; no LLM; ASCII.
    """
    return {"discriminates": bool(discriminates), "reference_value": reference_value,
            "floor": floor, "ceiling": ceiling, "reason": reason}


def baseline_cliff_self_check(baseline_low, baseline_high, works_threshold=0.5, cliff_drop=0.2,
                              reason: str = "") -> dict:
    """WORKING-BASELINE-CLIFF self-check (Skunkworks 3rd self-cert gate, 2026-06-18; encodes the B-delta v1 catch
    -- 'a lift over a FLOORED baseline is NOT a lever' -- as a DETERMINISTIC self-applied gate. REFINES the
    discrimination-regime gate [audit 79] specifically for LEVER / baseline-comparison claims).

    For a LEVER claim ('method X LIFTS capability over baseline B'), the lift is a real lever ONLY IF the
    comparison baseline B is a WORKING baseline WITH A CLIFF: it WORKS (recall/score > works_threshold) at the
    EASY end AND DEGRADES (drops >= cliff_drop) at the HARD end. Two ways a lever claim is actually a NON_TEST:
      - baseline FLOORED everywhere (never works): the 'lift' measures DENOISING / threshold-rescue, NOT the
        lever (the B-delta v1 noise-bug: linear=0 at ALL M -> nonlinear's lift was denoising-over-a-floor).
      - baseline never CLIFFS (works everywhere): no headroom for a lever to be demonstrated.

    The CELL -- which alone knows its metric -- passes its MEASURED baseline at the EASY end (baseline_low) and
    the HARD end (baseline_high); the gate DETERMINISTICALLY decides
        is_working_baseline_cliff = (low > works_threshold) AND ((low - high) >= cliff_drop).
    Pairs with the consumer-side baseline_cliff_gate (the atomizer forces the effective verdict -> NON_TEST when
    is_working_baseline_cliff==False). ADDITIVE + NON-RETROACTIVE: ONLY lever cells emit it (a non-lever cell has
    no comparison baseline), so nothing existing re-grades. COMPOSES with discrimination_self_check (discrimination
    = does the test discriminate at all; baseline-cliff = is the comparison baseline a working-baseline-with-a-cliff
    so the lift is a real lever). 11th-rule clean; no LLM; ASCII.
    """
    try:
        lo = float(baseline_low)
        hi = float(baseline_high)
        works = lo > float(works_threshold)
        cliffs = (lo - hi) >= float(cliff_drop)
        is_wbc = works and cliffs
    except (TypeError, ValueError):
        works = cliffs = is_wbc = False
    return {
        "is_working_baseline_cliff": bool(is_wbc),
        "baseline_low": baseline_low,
        "baseline_high": baseline_high,
        "works": bool(works),
        "cliffs": bool(cliffs),
        "works_threshold": works_threshold,
        "cliff_drop": cliff_drop,
        "reason": reason,
    }
