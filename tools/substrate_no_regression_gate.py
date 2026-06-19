"""SKUNKWORKS: the REAL no-regression gate for the self-improvement loop (replaces the tautological
`capability_preservation=1.0` tag-check as the breadth-protection guarantee).

USER constraint (2026-06-13): "do not sacrifice overall capability just to artificially prove ability
in one area." A macro-F1-only gate FAILS this -- macro can hold while one axis collapses and another
spikes (the exact artificial-narrow trade). So this gate is PER-AXIS: it HARD-FAILs if the macro OR
*any individual axis* regresses beyond tolerance. Breadth is protected explicitly, not by construction.

DECOUPLED by design (lane discipline): this gate consumes the REAL benchmark output (tools/
substrate_benchmark.py -> scorecard schema {macro_f1, per_axis_f1{A..G}}). Testbed/Exp-Dev RUN the
benchmark on a stable index; this gate APPLIES the pass/fail decision. It does not reimplement a
benchmark and does not need the live index.

PROTOCOL for the real integrate (Testbed):
  1. run substrate_benchmark.py on the index -> BEFORE score (or use latest scorecard history entry)
  2. apply the collapse worklist on a COPY / via atomic shard swap
  3. run substrate_benchmark.py again -> AFTER score (--after after.json)
  4. this gate: HARD-FAIL if macro drop > macro_tol OR any axis drop > axis_tol -> if FAIL, do NOT swap in
PRE-REGISTERED: PASS iff macro_after >= macro_before - macro_tol AND for every axis
  axis_after >= axis_before - axis_tol. Else HARD-FAIL (lists offending axes). ASCII-only.

Usage:
  python tools/substrate_no_regression_gate.py --self-test
  python tools/substrate_no_regression_gate.py --after path/to/after_score.json [--macro-tol 0.005] [--axis-tol 0.03]
  (BEFORE defaults to the latest scorecard.json history entry; override with --before path.json)
"""
from __future__ import annotations
import sys, json, argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCORECARD = REPO / "data" / "substrate_index" / "bench_reports" / "scorecard.json"


def _score(obj: dict) -> tuple[float, dict]:
    """Accept a scorecard history entry OR a raw {macro_f1, per_axis_f1} dict."""
    macro = obj.get("macro_f1")
    axes = obj.get("per_axis_f1") or obj.get("axes_f1") or {}
    if macro is None or not axes:
        raise ValueError("score must carry macro_f1 + per_axis_f1")
    return float(macro), {k: float(v) for k, v in axes.items()}


BASELINE_FLOOR = 0.05  # below this, the baseline index is degraded/broken -> gating is meaningless


def _latest_baseline() -> dict:
    s = json.loads(SCORECARD.read_text())
    hist = s.get("history") or []
    if not hist:
        raise ValueError("no scorecard history for baseline")
    # pick the most recent NON-degenerate entry; gating against a ~0 (mid-rebuild/CPU-only) score
    # passes anything, so skip degraded entries.
    for h in reversed(hist):
        if (h.get("macro_f1") or 0) >= BASELINE_FLOOR:
            return h
    return hist[-1]  # all degraded; caller's gate() will return UNKNOWN_DEGRADED_BASELINE


def gate(before: dict, after: dict, macro_tol: float = 0.005, axis_tol: float = 0.03) -> dict:
    mb, ab = _score(before)
    ma, aa = _score(after)
    if mb < BASELINE_FLOOR:
        return {"verdict": "UNKNOWN_DEGRADED_BASELINE", "macro_before": mb,
                "reason": f"baseline macro {mb:.4f} < floor {BASELINE_FLOOR}; index looks degraded/"
                          f"mid-rebuild/CPU-only -- gating would pass anything. Need a clean stable "
                          f"pre-collapse run first.", "axis_rows": [], "failed_axes": []}
    macro_delta = ma - mb
    macro_ok = macro_delta >= -macro_tol
    axis_rows = []
    failed_axes = []
    for k in sorted(set(ab) | set(aa)):
        b = ab.get(k); a = aa.get(k)
        if b is None or a is None:
            axis_rows.append((k, b, a, None, "MISSING"))
            failed_axes.append(k)  # an axis appearing/disappearing is a regression risk
            continue
        d = a - b
        ok = d >= -axis_tol
        axis_rows.append((k, b, a, d, "ok" if ok else "REGRESSED"))
        if not ok:
            failed_axes.append(k)
    verdict = "PASS" if (macro_ok and not failed_axes) else "HARD_FAIL"
    return {"verdict": verdict, "macro_before": mb, "macro_after": ma,
            "macro_delta": round(macro_delta, 4), "macro_ok": macro_ok,
            "macro_tol": macro_tol, "axis_tol": axis_tol,
            "failed_axes": failed_axes, "axis_rows": axis_rows}


def _print(r: dict):
    print(f"=== NO-REGRESSION GATE: {r['verdict']} ===")
    if r["verdict"] == "UNKNOWN_DEGRADED_BASELINE":
        print(f"  {r['reason']}")
        return
    print(f"macro: {r['macro_before']:.4f} -> {r['macro_after']:.4f}  (delta {r['macro_delta']:+.4f}; "
          f"tol -{r['macro_tol']}) {'ok' if r['macro_ok'] else 'REGRESSED'}")
    print("per-axis (breadth protection -- ANY axis regression > tol = HARD_FAIL):")
    for k, b, a, d, st in r["axis_rows"]:
        ds = f"{d:+.3f}" if d is not None else "  -  "
        print(f"  {k}: {b} -> {a}  ({ds})  [{st}]")
    if r["failed_axes"]:
        print(f"REGRESSED axes: {r['failed_axes']}  -> do NOT integrate the collapse")
    else:
        print("no axis regressed -> breadth preserved; collapse is safe to integrate")


def _selftest():
    base = {"macro_f1": 0.72, "per_axis_f1": {"A": 0.66, "B": 0.5, "C": 0.8, "D": 0.6, "E": 0.7, "F": 0.85, "G": 0.6}}
    # 1) identical -> PASS
    assert gate(base, base)["verdict"] == "PASS"
    # 2) macro UP but one axis collapses -> HARD_FAIL (the USER-constraint case macro-only would miss)
    sneaky = {"macro_f1": 0.74, "per_axis_f1": {**base["per_axis_f1"], "B": 0.20, "C": 0.95}}
    r = gate(base, sneaky)
    assert r["verdict"] == "HARD_FAIL" and "B" in r["failed_axes"], r
    # 3) uniform tiny dip within tol -> PASS
    dip = {"macro_f1": 0.718, "per_axis_f1": {k: v - 0.01 for k, v in base["per_axis_f1"].items()}}
    assert gate(base, dip)["verdict"] == "PASS"
    # 4) macro drop beyond tol -> HARD_FAIL
    drop = {"macro_f1": 0.70, "per_axis_f1": base["per_axis_f1"]}
    assert gate(base, drop)["verdict"] == "HARD_FAIL"
    print("SELF-TEST PASS: per-axis gate catches the macro-up-but-axis-collapsed case (USER breadth constraint).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--before"); ap.add_argument("--after")
    ap.add_argument("--macro-tol", type=float, default=0.005)
    ap.add_argument("--axis-tol", type=float, default=0.03)
    a = ap.parse_args()
    if a.self_test:
        _selftest(); return
    before = json.loads(Path(a.before).read_text()) if a.before else _latest_baseline()
    if not a.after:
        # demo: gate the baseline against itself -> PASS, delta 0 (proves wiring to real scorecard)
        print("[demo] no --after given; gating latest scorecard baseline against itself")
        _print(gate(before, before, a.macro_tol, a.axis_tol)); return
    _print(gate(before, json.loads(Path(a.after).read_text()), a.macro_tol, a.axis_tol))


if __name__ == "__main__":
    main()
