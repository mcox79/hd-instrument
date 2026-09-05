"""exp_board_goal_hierarchy_v1 -- the GOAL-HIERARCHY multi-hop BOARD ARM (Step 0b of the top-down pass).

WHY: the live board's goal-why arm asks the IMMEDIATE purpose, and only ~4% of it is multi-hop, so the landed
goal-hierarchy GRAPH (and the incoming means-end contextual `_link_open_stack` edge) score 0.68->1.00 on the
authored plot battery but register NOTHING on the board (the board scores the flat register, not the graph). This
arm scores the multi-hop plot-structure readouts so the goal-graph landings become board-visible.

It REUSES the solver's proven instrument `exp_goal_hierarchy_qa_v1.eval_arms` on the authored plot battery and
reshapes the WHY-CHAIN (multi-hop superordinate) arm -- the primary multi-hop capability -- into the board's
per_dimension row schema; B (reinstatement over distance) + C (connectivity salience) are reported in detail.

model = graph.superordinate (multi-hop) · strongest_floor = flat_register.why (immediate purpose) · twin = the
shuffled-EDGES info-free null p95. Glass-box, NO external LLM. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_goal_hierarchy_v1.py
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_goal_hierarchy_qa_v1 as GHQ
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_goal_hierarchy_v1"


def board_goal_hierarchy_dimension(seed=20260904):
    """A per_dimension board row (schema-matched to board_goal_dimension) scoring the multi-hop why-chain
    (graph.superordinate) vs the flat-register immediate-purpose floor. Returns (row, detail)."""
    res = GHQ.eval_arms(GHQ._battery(), seed=seed)
    A = res["A_why_chain_superordinate"]
    ci = A["ci95_diff"] or {"lo": None, "hi": None, "mean": A["model_minus_floor"]}
    tw = A["twin_shuffled_edges_null"]["p95"]
    model = A["model"]; floor = A["floor"]
    ms = [ci.get("mean", A["model_minus_floor"]), ci.get("lo"), ci.get("hi")]
    row = {
        "n": A["n"], "model_acc": model,
        "overlap_floor": floor,
        "floor_accs": {"flat_register_why_immediate": floor, "shuffled_edges_twin_p95": tw},
        "strongest_floor_name": "flat_register_why_immediate",
        "strongest_floor": floor,
        "twin_acc": tw,
        "model_minus_strongest": ms,
        "model_minus_twin": [round((model - tw), 4) if (model is not None) else None, None, None],
        "ci_sep_over_strongest": bool(ci.get("lo") is not None and ci.get("lo") > 0),
        "ci_sep_over_twin": bool(model is not None and model > tw),
        "population": "authored plot-structure battery, multi-hop why-chain (graph.superordinate) vs the flat "
                      "register's immediate purpose; the board goal-why arm is only ~4% multi-hop (instrument gap)",
    }
    detail = {
        "A_why_chain": A,
        "B_reinstatement": res["B_reinstatement_over_distance"],
        "C_connectivity": res["C_connectivity_salience"],
        "structural_graph_accuracy": res["structural_graph_accuracy"],
        "note": "goal-hierarchy multi-hop board arm (Step 0b). Reuses exp_goal_hierarchy_qa_v1.eval_arms on the "
                "authored plot battery. model = graph.superordinate (multi-hop), floor = flat_register.why "
                "(immediate purpose), twin = shuffled-EDGES null p95. Makes the goal-graph organ + the means-end "
                "contextual edge board-visible (the live goal-why arm is register-scored + only ~4% multi-hop).",
    }
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.parse_args()
    t0 = time.time()
    row, detail = board_goal_hierarchy_dimension()
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("Goal-hierarchy multi-hop board arm  n=%d (why-chain items)" % row["n"])
    print("  model_acc (graph.superordinate, multi-hop): %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (flat register, immediate): %.4f" % (row["strongest_floor"] or 0))
    print("  twin (shuffled-edges null p95)            : %.4f" % (row["twin_acc"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  B reinstatement: model %.3f vs recency %.3f | C salience: model %.3f vs recency %.3f" % (
        detail["B_reinstatement"]["model"] or 0, detail["B_reinstatement"]["floor"] or 0,
        detail["C_connectivity"]["model"] or 0, detail["C_connectivity"]["floor"] or 0))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
