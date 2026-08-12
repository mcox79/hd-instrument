#!/usr/bin/env python3
"""Dispatch-time experiment guards: timeout-floor + smoke-profile/routing.

Two durable, code-computed guards so exp_dev/orchestrator stop eyeballing the
numbers that recur as firefights (2026-07-08 hardening pass, Testbed).

GUARD B -- suggest_timeout_seconds:
    Root cause it fixes: the prose timeout formula in exp_dev.md scaled ONLY on
    N and seeds. Multi-arm encoder FULLs hold N at production in smoke and scale
    V (1500->40000), iters (120->800), and batch B (768->8192) into the FULL --
    axes the old formula ignored -- so the estimate under-shot ~3-4x and the
    FULLs were killed at 60-90min when they needed ~3h. This computes the wall
    from ALL multiplicative work axes the caller declares, applies a margin, a
    per-cell-class FLOOR (the actual kill-preventer), and a hard cap.

GUARD E -- assess_smoke_profile:
    Root cause it fixes: heavy smokes run LOCAL for 25-40min (load a 1.3GB BGE
    cache + train per seed), tying up the machine + the director session for no
    preflight benefit -- a full run mislabeled 'smoke'. This flags a smoke whose
    estimated wall exceeds the local budget (~10min) and recommends SHRINK or
    ROUTE_REMOTE. It NEVER recommends shrinking below the discriminating scale:
    if a smoke cannot be BOTH fast AND discriminator-firing (the frontier control
    must still fail), it belongs on the remote queue, not local.

The cell-runtime companion (assert_discriminator_fires, VacuousSmokeError, atomic
write_metrics) lives in experiments/_seed_checkpoint.py.

Usage:
    python tools/exp_guard.py timeout --smoke-wall 100 \
        --axis iters:120:800 --axis batch:768:8192 --axis seeds:3:5 \
        --class trained_encoder
    python tools/exp_guard.py smoke --est-wall 2400 --heavy-load-gb 1.3 \
        --discriminator-requires-scale
    python tools/exp_guard.py selftest

Exit codes:
    0 = OK / recommendation printed
    2 = usage error
    3 = timeout estimate exceeds hard cap (BLOCK -- escalate scope to Strategy)

ASCII-only. No unicode, no em dashes.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List, Optional, Sequence, Tuple

# Per-cell-class timeout FLOOR (seconds). The floor -- not the point estimate --
# is what prevents the mid-sweep kill when the smoke wall is measured on a much
# lighter regime than the FULL. Keys are coarse cell classes; extend as needed.
CLASS_FLOOR_S: Dict[str, int] = {
    # multi-seed real-training encoder FULLs (VICReg/RKD, V>=10k, >=3 seeds,
    # multiple arms): measured to need ~3h -> floor at 3h.
    "trained_encoder": 10800,
    # multi-seed capacity / composition sweeps with matrix ops.
    "matrix_sweep": 5400,
    # generic multi-seed cell.
    "default": 1800,
    # cheap re-analysis / arithmetic-only.
    "light": 300,
}

HARD_CAP_S = 14400          # 4h: runs beyond this tie up the lone GPU a full day
LOCAL_SMOKE_BUDGET_S = 600  # 10 min: a smoke over this ties up local dev + session
HEAVY_LOAD_GB = 0.5         # a cache load >= this dominates smoke wall (can't shrink away)
DEFAULT_MARGIN = 1.5
ROUND_TO_S = 300            # round timeout up to the nearest 5 min


def suggest_timeout_seconds(
    smoke_wall_s: float,
    axes: Sequence[Tuple[str, float, float, float]],
    *,
    margin: float = DEFAULT_MARGIN,
    cell_class: str = "default",
    round_to: int = ROUND_TO_S,
    hard_cap_s: int = HARD_CAP_S,
) -> Dict[str, object]:
    """Estimate a FULL timeout from the smoke wall and declared work axes.

    axes: list of (name, smoke_val, full_val, exponent). Each contributes a
    multiplicative factor (full/smoke)**exponent to the work ratio. Declare the
    axes that genuinely multiply the run's work -- iters, batch, seeds, arms,
    and N (with an exponent per its matmul cost); an eval-dominated cell can pass
    V. Axes held constant between smoke and FULL contribute a factor of 1.0 and
    are safe to include or omit.

    Returns a dict with the estimate, the floored/capped value, the per-axis
    breakdown, and a `block` flag (True when the raw estimate exceeds hard_cap_s
    -- escalate scope to Strategy instead of shipping).
    """
    if smoke_wall_s <= 0:
        raise ValueError(f"smoke_wall_s must be > 0, got {smoke_wall_s}")
    floor_s = CLASS_FLOOR_S.get(cell_class)
    if floor_s is None:
        raise ValueError(
            f"unknown cell_class {cell_class!r}; known: {sorted(CLASS_FLOOR_S)}")

    work_ratio = 1.0
    breakdown: List[Dict[str, object]] = []
    for name, sv, fv, exp in axes:
        if sv <= 0:
            raise ValueError(f"axis {name!r} smoke_val must be > 0, got {sv}")
        factor = (float(fv) / float(sv)) ** float(exp)
        work_ratio *= factor
        breakdown.append({"axis": name, "smoke": sv, "full": fv,
                          "exp": exp, "factor": round(factor, 3)})

    raw = margin * smoke_wall_s * work_ratio
    block = raw > hard_cap_s
    # Apply floor, then round UP to round_to, then clamp to hard cap.
    floored = max(raw, floor_s)
    rounded = int(math.ceil(floored / round_to) * round_to)
    final = min(rounded, hard_cap_s)
    return {
        "smoke_wall_s": smoke_wall_s,
        "margin": margin,
        "cell_class": cell_class,
        "class_floor_s": floor_s,
        "work_ratio": round(work_ratio, 3),
        "raw_estimate_s": round(raw, 1),
        "floored_s": round(floored, 1),
        "timeout_s": final,
        "hard_cap_s": hard_cap_s,
        "block": block,
        "breakdown": breakdown,
    }


def assess_smoke_profile(
    est_smoke_wall_s: float,
    *,
    heavy_load_gb: float = 0.0,
    discriminator_requires_scale: bool = False,
    local_budget_s: int = LOCAL_SMOKE_BUDGET_S,
    heavy_gb_threshold: float = HEAVY_LOAD_GB,
) -> Dict[str, object]:
    """Recommend how to run a smoke: LOCAL_OK / SHRINK / ROUTE_REMOTE.

    A smoke is a FAST preflight (a few min). One that estimates over the local
    budget ties up local dev + the director session for no benefit.

    Decision (first match wins):
      1. est <= budget AND load < heavy threshold          -> LOCAL_OK
      2. discriminator_requires_scale OR heavy load         -> ROUTE_REMOTE
         (cannot be shrunk without going vacuous, or the heavy cache load
          dominates the wall so shrinking V/iters will not help)
      3. otherwise (over budget but shrinkable)             -> SHRINK

    NEVER recommends shrinking below the discriminating scale (guard A stays
    load-bearing): if fast-and-discriminating is impossible, route remote.
    """
    over_budget = est_smoke_wall_s > local_budget_s
    heavy = heavy_load_gb >= heavy_gb_threshold
    if not over_budget and not heavy:
        rec, reason = "LOCAL_OK", (
            f"est {est_smoke_wall_s:.0f}s <= budget {local_budget_s}s and load "
            f"{heavy_load_gb:.2f}GB < {heavy_gb_threshold}GB; run local")
    elif discriminator_requires_scale or heavy:
        why = []
        if discriminator_requires_scale:
            why.append("cannot shrink without going vacuous (guard A)")
        if heavy:
            why.append(f"heavy {heavy_load_gb:.2f}GB load dominates wall")
        rec, reason = "ROUTE_REMOTE", (
            f"est {est_smoke_wall_s:.0f}s over budget {local_budget_s}s and " +
            "; ".join(why) + "; ship smoke to remote_cpu_queue/overnight_queue, "
            "do NOT block local")
    else:
        rec, reason = "SHRINK", (
            f"est {est_smoke_wall_s:.0f}s over budget {local_budget_s}s but "
            "shrinkable (discriminator still fires smaller): cut V/iters/seeds "
            "to fit the budget")
    return {
        "recommendation": rec,
        "reason": reason,
        "est_smoke_wall_s": est_smoke_wall_s,
        "local_budget_s": local_budget_s,
        "heavy_load_gb": heavy_load_gb,
        "discriminator_requires_scale": discriminator_requires_scale,
    }


def _parse_axis(s: str) -> Tuple[str, float, float, float]:
    """Parse 'name:smoke:full[:exp]' -> (name, smoke, full, exp). exp default 1.0."""
    parts = s.split(":")
    if len(parts) not in (3, 4):
        raise argparse.ArgumentTypeError(
            f"axis {s!r} must be name:smoke:full[:exp]")
    name = parts[0]
    try:
        sv, fv = float(parts[1]), float(parts[2])
        exp = float(parts[3]) if len(parts) == 4 else 1.0
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"axis {s!r} numeric parse: {e}")
    return (name, sv, fv, exp)


def _selftest() -> int:
    # Timeout: the twoband-class miss -- N constant, V/iters/batch/seeds scale.
    r = suggest_timeout_seconds(
        100.0,
        [("iters", 120, 800, 1.0), ("batch", 768, 8192, 1.0),
         ("seeds", 3, 5, 1.0)],
        cell_class="trained_encoder")
    # work_ratio = 6.667 * 10.667 * 1.667 ~ 118.5; raw = 1.5*100*118.5 ~ 17775 > cap
    assert r["work_ratio"] > 100, f"T1 work_ratio={r['work_ratio']}"
    assert r["block"] is True, f"T1 expected block (raw>{HARD_CAP_S}): {r}"
    assert r["timeout_s"] == HARD_CAP_S, f"T1 timeout={r['timeout_s']}"
    # Floor bites when the point estimate is small.
    r2 = suggest_timeout_seconds(
        30.0, [("seeds", 3, 5, 1.0)], cell_class="trained_encoder")
    assert r2["timeout_s"] == 10800, f"T2 floor should bite: {r2['timeout_s']}"
    # Old-formula shape (N + seeds only) still works and rounds up.
    r3 = suggest_timeout_seconds(
        45.0, [("N", 1024, 4096, 1.5), ("seeds", 1, 5, 1.0)],
        cell_class="default")
    # raw = 1.5*45*8*5 = 2700; floor 1800 -> 2700; round_to 300 -> 2700
    assert r3["timeout_s"] == 2700, f"T3 timeout={r3['timeout_s']}"
    assert r3["block"] is False, "T3 should not block"
    print("[selftest] T1-T3 PASS: suggest_timeout_seconds (V/iters/batch axes, "
          "floor, cap, old-formula compat)")

    # Smoke profile: fast+light -> LOCAL_OK.
    s1 = assess_smoke_profile(120, heavy_load_gb=0.0)
    assert s1["recommendation"] == "LOCAL_OK", s1
    # Over budget, heavy cache -> ROUTE_REMOTE (the phase_traversal 1.3GB case).
    s2 = assess_smoke_profile(2400, heavy_load_gb=1.3)
    assert s2["recommendation"] == "ROUTE_REMOTE", s2
    # Over budget, discriminator needs scale -> ROUTE_REMOTE not SHRINK.
    s3 = assess_smoke_profile(900, heavy_load_gb=0.0,
                              discriminator_requires_scale=True)
    assert s3["recommendation"] == "ROUTE_REMOTE", s3
    # Over budget, light, shrinkable -> SHRINK.
    s4 = assess_smoke_profile(900, heavy_load_gb=0.0)
    assert s4["recommendation"] == "SHRINK", s4
    print("[selftest] T4-T7 PASS: assess_smoke_profile (LOCAL_OK/ROUTE_REMOTE/"
          "SHRINK; never shrinks below discriminating scale)")
    print("[selftest] ALL PASS")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Dispatch-time experiment guards.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("timeout", help="suggest a FULL timeout_s")
    pt.add_argument("--smoke-wall", type=float, required=True,
                    help="measured smoke wall seconds (elapsed_s)")
    pt.add_argument("--axis", type=_parse_axis, action="append", default=[],
                    metavar="name:smoke:full[:exp]",
                    help="a work axis; repeatable (e.g. iters:120:800, "
                         "batch:768:8192, seeds:3:5, N:1024:4096:1.5)")
    pt.add_argument("--class", dest="cell_class", default="default",
                    choices=sorted(CLASS_FLOOR_S),
                    help="cell class for the timeout floor")
    pt.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
    pt.add_argument("--json", action="store_true")

    ps = sub.add_parser("smoke", help="assess smoke profile / routing")
    ps.add_argument("--est-wall", type=float, required=True,
                    help="estimated smoke wall seconds")
    ps.add_argument("--heavy-load-gb", type=float, default=0.0,
                    help="size of any heavy cache/model load in GB")
    ps.add_argument("--discriminator-requires-scale", action="store_true",
                    help="smoke cannot shrink without going vacuous (guard A)")
    ps.add_argument("--json", action="store_true")

    sub.add_parser("selftest", help="run internal self-tests")

    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()

    if args.cmd == "timeout":
        if not args.axis:
            print("error: at least one --axis required", file=sys.stderr)
            return 2
        try:
            r = suggest_timeout_seconds(
                args.smoke_wall, args.axis, margin=args.margin,
                cell_class=args.cell_class)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(r, indent=2))
        else:
            print(f"timeout_s={r['timeout_s']}  (raw={r['raw_estimate_s']}s "
                  f"work_ratio={r['work_ratio']}x floor={r['class_floor_s']}s "
                  f"class={r['cell_class']})")
            for b in r["breakdown"]:
                print(f"    axis {b['axis']}: {b['smoke']}->{b['full']} "
                      f"^{b['exp']} = {b['factor']}x")
            if r["block"]:
                print(f"BLOCK: raw estimate {r['raw_estimate_s']}s exceeds hard "
                      f"cap {r['hard_cap_s']}s -- escalate scope to Strategy.")
        return 3 if r["block"] else 0

    if args.cmd == "smoke":
        r = assess_smoke_profile(
            args.est_wall, heavy_load_gb=args.heavy_load_gb,
            discriminator_requires_scale=args.discriminator_requires_scale)
        if args.json:
            print(json.dumps(r, indent=2))
        else:
            print(f"{r['recommendation']}: {r['reason']}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
