"""Skunkworks 2026-06-20 -- VERDICT-VET-layer SELF-CHECK: by-construction-SATURATION / can't-fail detector (read-only).

Encodes the recurring audit JUDGMENT caught by hand this session (pythia-KV HARD_PASS = recall=1.000 across all 90
cells / std=0.0 / no cliff -> the gate CANNOT fail -> tautology, not a discriminating capability). Per the
substrate-autonomy path "encode every audit judgment as a self-applied check," this mechanizes it: run it on a landed
metrics.json BEFORE cert-grading a PASS.

THE SIGNATURE (a non-discriminating PASS):
  (1) verdict is PASS-class (HARD_PASS / PASS), AND
  (2) the swept primary metric is pinned at an EXTREME (>= ceiling or <= floor) across ALL swept conditions, AND
  (3) ~zero spread across seeds/conditions (variance ~ 0), AND
  (4) no cliff / boundary was reached (the sweep never entered a failure regime).
=> FLAG: by-construction-saturation candidate -> TIER, do not cert-grade as a win; needs a discriminating regime
   (a can-fail leg). This is the can-fail discipline (a gate that cannot fail is a tautology) + the
   by-construction-saturation tiering discipline, made mechanical.

SCOPE (honest): v1 handles the recall/accuracy-SWEEP pattern (the recurring one: recall_by_sigma / recall_primary_* /
recall_s* arrays + max_seed_std + cliff_size). Other metric shapes = future work (it reports UNSCANNABLE, not PASS --
silence is not a green). Read-ONLY. ASCII.

Usage:
  python tools/skunkworks_saturation_canfail_check_v1.py <metrics.json>           # one file
  python tools/skunkworks_saturation_canfail_check_v1.py --scan data             # all data/*/metrics.json
  [--ceiling 0.999] [--floor 0.001] [--spread-eps 1e-6] [--json]
Exit 0 = no saturation flag; exit 3 = at least one FLAG (so it can gate a cert-grade step).
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PASS_VERDICTS = {"HARD_PASS", "PASS"}
# metric-name hints for the "primary swept metric" (recall/accuracy families)
METRIC_HINTS = ("recall", "accuracy", "acc", "f1", "auc", "precision")
# field-name hints that a cliff / capacity boundary was REACHED (non-null => a failure regime was found)
CLIFF_FIELDS = ("cliff_size", "cliff", "crosstalk_onset", "m_critical", "boundary", "k_max_at_recall_0.9")
# field-name hints for cross-seed/condition spread
STD_FIELDS = ("max_seed_std", "max_std", "std", "seed_std", "cv")


def _numeric_leaves(obj, hint_filter=None, _key=""):
    """Yield numeric leaf values; if hint_filter set, only under keys containing a hint (anywhere up the path)."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = (_key + "." + str(k)).lower()
            out += _numeric_leaves(v, hint_filter, kk)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out += _numeric_leaves(v, hint_filter, _key)
    elif isinstance(obj, bool):
        pass  # bool is an int subclass; skip
    elif isinstance(obj, (int, float)):
        if hint_filter is None or any(h in _key for h in hint_filter):
            out.append(float(obj))
    return out


def check_metrics(m, ceiling=0.999, floor=0.001, spread_eps=1e-6, min_sweep=20):
    verdict = str(m.get("verdict", "")).upper()
    detail = m.get("detail", m)  # some cells flatten
    # (1) PASS-class
    is_pass = verdict in PASS_VERDICTS
    # primary swept metric values (recall/accuracy family, from detail + per_unit)
    vals = _numeric_leaves(detail, METRIC_HINTS)
    vals += _numeric_leaves(m.get("per_unit", []), METRIC_HINTS)
    vals = [v for v in vals if 0.0 <= v <= 1.0]  # keep [0,1] metrics (recall/acc); drop counts
    if not vals:
        return {"scannable": False, "reason": "no recall/accuracy-family [0,1] metric found", "verdict": verdict}
    vmin, vmax = min(vals), max(vals)
    spread = vmax - vmin
    n = len(vals)
    # (2) pinned at an extreme across ALL conditions
    pinned_ceiling = vmin >= ceiling
    pinned_floor = vmax <= floor
    pinned = pinned_ceiling or pinned_floor
    # (3) ~zero spread across the swept values themselves + any reported std field
    std_vals = _numeric_leaves(detail, STD_FIELDS)
    reported_std0 = bool(std_vals) and max(std_vals) <= max(spread_eps, 1e-4)
    near_zero_spread = spread <= spread_eps
    # (4) no cliff reached (every cliff-ish field is null/None/0-with-a-no_cliff-flag)
    cliff_reached = False
    for cf in CLIFF_FIELDS:
        cv = detail.get(cf) if isinstance(detail, dict) else None
        if cv is not None and not (isinstance(cv, bool)) and cv != 0:
            cliff_reached = True
    no_cliff_flag = bool(detail.get("no_cliff_through_100k")) if isinstance(detail, dict) else False
    no_cliff = (not cliff_reached) or no_cliff_flag
    # DISCRIMINATOR (false-positive guard): only flag a CAPACITY/CLIFF PROBE that found no cliff while pinned --
    # NOT a small correctness/invariant check where 1.0 is the legitimate expected result (rollback/replay = 2-5
    # values at 1.0, no cliff-intent fields). A genuine non-discriminating capacity sweep EITHER declares a
    # cliff-intent field (cliff_size / no_cliff_through_* / m_critical present, even if null) OR is a large sweep.
    has_cliff_intent = False
    if isinstance(detail, dict):
        keys_lower = {str(k).lower() for k in detail.keys()}
        has_cliff_intent = any(any(cf in k for cf in CLIFF_FIELDS) for k in keys_lower) or \
                           any("no_cliff" in k for k in keys_lower)
    is_capacity_probe = has_cliff_intent or (n >= min_sweep)
    # FLAG: a PASS, pinned at extreme, ~zero spread, no failure regime reached, AND it's actually a capacity/cliff probe
    flag = is_pass and pinned and near_zero_spread and no_cliff and is_capacity_probe
    if is_pass and pinned and near_zero_spread and no_cliff and not is_capacity_probe:
        diag = ("pinned PASS but NOT a capacity/cliff probe (no cliff-intent field; n=%d < %d) -> looks like a "
                "correctness/invariant check where the extreme IS the expected result; not flagged" % (n, min_sweep))
    elif flag:
        diag = ("BY-CONSTRUCTION-SATURATION CANDIDATE: a capacity/cliff PROBE pinned at extreme with ~zero spread "
                "and no failure regime reached -> the gate cannot fail (non-discriminating). TIER, do not cert-grade; "
                "add a can-fail leg.")
    else:
        diag = "no saturation signature (has spread, a cliff, or is not a PASS)"
    return {
        "scannable": True, "flag": flag, "verdict": verdict, "is_pass": is_pass,
        "n_metric_values": n, "metric_min": round(vmin, 6), "metric_max": round(vmax, 6),
        "spread": round(spread, 6), "pinned_ceiling": pinned_ceiling, "pinned_floor": pinned_floor,
        "reported_std_zero": reported_std0, "near_zero_spread": near_zero_spread,
        "cliff_reached": cliff_reached, "no_cliff": no_cliff,
        "has_cliff_intent": has_cliff_intent, "is_capacity_probe": is_capacity_probe,
        "diagnosis": diag,
    }


def _load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="metrics.json file")
    ap.add_argument("--scan", help="directory to scan for */metrics.json")
    ap.add_argument("--ceiling", type=float, default=0.999)
    ap.add_argument("--floor", type=float, default=0.001)
    ap.add_argument("--spread-eps", type=float, default=1e-6)
    ap.add_argument("--min-sweep", type=int, default=20,
                    help="min #metric-values to treat a no-cliff-field PASS as a sweep (false-positive guard vs correctness-checks)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets = []
    if args.scan:
        targets = sorted(Path(args.scan).glob("*/metrics.json"))
    elif args.path:
        targets = [Path(args.path)]
    else:
        ap.error("provide a metrics.json path or --scan <dir>")

    results = []
    any_flag = False
    for t in targets:
        m = _load(t)
        if "_load_error" in m:
            results.append({"path": str(t), "scannable": False, "reason": m["_load_error"]})
            continue
        r = check_metrics(m, args.ceiling, args.floor, args.spread_eps, args.min_sweep)
        r["path"] = str(t)
        r["anchor"] = m.get("anchor_name", t.parent.name)
        results.append(r)
        if r.get("flag"):
            any_flag = True

    if args.json:
        print(json.dumps(results, indent=2))
        return 3 if any_flag else 0

    print("=" * 78)
    print("SATURATION / CAN'T-FAIL SELF-CHECK v1 (read-only) -- %d target(s)" % len(targets))
    print("-" * 78)
    for r in results:
        if not r.get("scannable", False):
            print("  [UNSCANNABLE] %s  (%s)" % (r.get("anchor", r["path"]), r.get("reason", "")))
            continue
        tag = "FLAG ***" if r.get("flag") else "ok  "
        print("  [%s] %s  verdict=%s vals=%d min=%.4f max=%.4f spread=%.6f no_cliff=%s std0=%s"
              % (tag, r.get("anchor"), r["verdict"], r["n_metric_values"], r["metric_min"],
                 r["metric_max"], r["spread"], r["no_cliff"], r["reported_std_zero"]))
        if r.get("flag"):
            print("       -> %s" % r["diagnosis"])
    print("-" * 78)
    print("RESULT:", "SATURATION FLAG(S) FOUND" if any_flag else "no saturation flags", "(exit %d)" % (3 if any_flag else 0))
    print("=" * 78)
    return 3 if any_flag else 0


if __name__ == "__main__":
    raise SystemExit(main())
