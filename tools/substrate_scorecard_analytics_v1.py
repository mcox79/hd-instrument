"""Scorecard analytics + cycle-close summary tool.

Reads scorecard.json + emits useful analytics:
  - Cycle-over-cycle deltas (macro + per-axis)
  - Best/worst phase per axis across history
  - Mechanism-class effectiveness (link mechanism_classes_shipped to delta)
  - Held-out vs tuned delta (if held-out entries present)
  - Trajectory data points for plotting

Useful for Research's cycle-close synthesis without manually grinding through
scorecard.json.

Output:
  - stdout summary
  - data/substrate_index/bench_reports/scorecard_analytics.json

Composes with scorecard_schema_v1 + monitor_cap_map_v1 + regression_baseline_check_v1.

NO LLM. Pure JSON aggregation. Milliseconds wall.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict


SCORECARD_PATH = Path("data/substrate_index/bench_reports/scorecard.json")
OUT_PATH = Path("data/substrate_index/bench_reports/scorecard_analytics.json")


def cycle_over_cycle_deltas(history: list) -> list:
    """Compute deltas between consecutive entries."""
    deltas = []
    for i in range(1, len(history)):
        prev = history[i - 1]
        cur = history[i]
        d = {
            "from_phase": prev.get("cycle_phase"),
            "to_phase": cur.get("cycle_phase"),
            "macro_delta": None,
            "per_axis_deltas": {},
            "mechanism_classes_introduced": cur.get("mechanism_classes_shipped", []),
        }
        pm = prev.get("macro_f1")
        cm = cur.get("macro_f1")
        if pm is not None and cm is not None:
            d["macro_delta"] = round(cm - pm, 4)
        for axis in (prev.get("per_axis_f1") or {}).keys() | (cur.get("per_axis_f1") or {}).keys():
            p = (prev.get("per_axis_f1") or {}).get(axis)
            c = (cur.get("per_axis_f1") or {}).get(axis)
            if p is not None and c is not None:
                d["per_axis_deltas"][axis] = round(c - p, 4)
        deltas.append(d)
    return deltas


def per_axis_best_worst(history: list, axes: list) -> dict:
    """For each axis, find the best and worst phase + value."""
    out = {}
    for axis in axes:
        vals = []
        for h in history:
            v = (h.get("per_axis_f1") or {}).get(axis)
            if v is not None:
                vals.append((v, h.get("cycle_phase"), h.get("cycle_id")))
        if not vals:
            continue
        best = max(vals, key=lambda t: t[0])
        worst = min(vals, key=lambda t: t[0])
        out[axis] = {
            "best_value": best[0], "best_phase": best[1], "best_cycle": best[2],
            "worst_value": worst[0], "worst_phase": worst[1], "worst_cycle": worst[2],
            "spread": round(best[0] - worst[0], 4),
        }
    return out


def mechanism_effectiveness(deltas: list) -> dict:
    """Link mechanism_classes_introduced to macro deltas to identify high-impact mechanisms."""
    contributions = defaultdict(list)
    for d in deltas:
        macro = d.get("macro_delta")
        if macro is None:
            continue
        mechs = d.get("mechanism_classes_introduced", [])
        if not mechs:
            continue
        # Attribute equal share of macro_delta to each mechanism (rough heuristic)
        per_mech = macro / len(mechs)
        for m in mechs:
            contributions[m].append(round(per_mech, 4))
    out = {}
    for m, vals in contributions.items():
        out[m] = {
            "n_phase_introductions": len(vals),
            "sum_macro_contribution": round(sum(vals), 4),
            "avg_macro_contribution": round(sum(vals) / len(vals), 4),
        }
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["sum_macro_contribution"]))


def held_out_vs_tuned(history: list) -> dict:
    """If both held-out and tuned entries exist, compute the Goodhart gap."""
    tuned = [h for h in history if not h.get("held_out") and h.get("macro_f1") is not None]
    held_out = [h for h in history if h.get("held_out") and h.get("macro_f1") is not None]
    if not tuned or not held_out:
        return {"available": False, "reason": "no held-out OR no tuned history rows"}
    latest_tuned = max(tuned, key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")))
    latest_held_out = max(held_out, key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")))
    return {
        "available": True,
        "tuned_phase": latest_tuned.get("cycle_phase"),
        "tuned_macro": latest_tuned.get("macro_f1"),
        "held_out_phase": latest_held_out.get("cycle_phase"),
        "held_out_macro": latest_held_out.get("macro_f1"),
        "goodhart_gap": round(latest_tuned["macro_f1"] - latest_held_out["macro_f1"], 4),
        "interpretation": (
            "goodhart_gap >0: tuned overestimates held-out; gap measures per-Q-tuning credit"
        ),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scorecard-path", default=str(SCORECARD_PATH))
    ap.add_argument("--output", default=str(OUT_PATH))
    args = ap.parse_args()

    sp = Path(args.scorecard_path)
    if not sp.exists():
        print(f"ERROR: scorecard not found at {sp}")
        sys.exit(2)
    scorecard = json.loads(sp.read_text(encoding="utf-8"))
    history = sorted(
        scorecard.get("history", []),
        key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")),
    )
    axes = scorecard.get("axes", [])

    print(f"=== Scorecard Analytics v1 ===")
    print(f"benchmark: {scorecard.get('benchmark_id')}")
    print(f"history rows: {len(history)}")
    print(f"axes: {axes}")
    if not history:
        print("WARNING: no history rows; nothing to analyze")
        return

    deltas = cycle_over_cycle_deltas(history)
    print(f"\n--- Cycle-over-cycle deltas ({len(deltas)}) ---")
    for d in deltas:
        macro_str = f"{d['macro_delta']:+.4f}" if d['macro_delta'] is not None else "n/a"
        print(f"  {d['from_phase']:30s} -> {d['to_phase']:30s}  macro {macro_str}")
        if d.get("mechanism_classes_introduced"):
            mc = ", ".join(d["mechanism_classes_introduced"][:3])
            if len(d["mechanism_classes_introduced"]) > 3:
                mc += f" (+{len(d['mechanism_classes_introduced']) - 3})"
            print(f"      mechanisms: {mc}")

    best_worst = per_axis_best_worst(history, axes)
    print(f"\n--- Per-axis best/worst across history ---")
    for axis, bw in best_worst.items():
        print(f"  {axis}: best {bw['best_value']:.4f} ({bw['best_phase']})  "
              f"worst {bw['worst_value']:.4f} ({bw['worst_phase']})  spread {bw['spread']:+.4f}")

    mech = mechanism_effectiveness(deltas)
    print(f"\n--- Mechanism effectiveness (top 8 by sum-macro-contribution) ---")
    for i, (m, info) in enumerate(list(mech.items())[:8], 1):
        print(f"  {i}. sum {info['sum_macro_contribution']:+.4f}  avg {info['avg_macro_contribution']:+.4f}  "
              f"n={info['n_phase_introductions']}  {m[:60]}")

    gap = held_out_vs_tuned(history)
    print(f"\n--- Held-out vs Tuned (Goodhart gap) ---")
    if gap["available"]:
        print(f"  tuned ({gap['tuned_phase']}):     macro {gap['tuned_macro']:.4f}")
        print(f"  held-out ({gap['held_out_phase']}): macro {gap['held_out_macro']:.4f}")
        print(f"  GOODHART GAP: {gap['goodhart_gap']:+.4f}")
    else:
        print(f"  not available: {gap['reason']}")

    out = {
        "scorecard_path": str(sp),
        "benchmark_id": scorecard.get("benchmark_id"),
        "history_row_count": len(history),
        "cycle_over_cycle_deltas": deltas,
        "per_axis_best_worst": best_worst,
        "mechanism_effectiveness_sorted": mech,
        "held_out_vs_tuned_goodhart_gap": gap,
    }
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)
    with op.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nfull JSON: {op}")


if __name__ == "__main__":
    main()
