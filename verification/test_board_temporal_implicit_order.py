"""Scaffold-free witness for the board arm `temporal_implicit_order` (exp_situation_model_qa_modern_v1).

Recomputes the arm from SOURCE (the SOLVED cell exp_broaden_causal_order_final_v1.run recomputes from the cached mine
+ TRACIE gold; no landed-metrics read; this witness writes nowhere) and asserts the owner-DONE
grow_a_broad_causal_event_order_knowledge_store win as scored on the board: the BROADER tense-agnostic store (now LIVE
in hdlab.temporal_reasoner) beats, on TRACIE iid implicit-event before/after (paired clustered bootstrap over stories),
  1. the SEED store (177,800-pair tense-gated mine, same population)  -- CI-separated (the strongest floor),
  2. the abstain-majority floor                                       -- CI-separated,
  3. the info-free SHUFFLED-ORDER twin                                -- CI-separated (the extracted ORDER is load-bearing).
And confirms the broad store is the LIVE asset hdlab.temporal_reasoner._script_schema() consults. If the mine asset is
absent the arm degrades (model_acc=None) and this witness SKIPs (asset-less safe, the established pattern). ~10s.
Run: .venv/Scripts/python.exe verification/test_board_temporal_implicit_order.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

P = F = 0


def ok(cond, name, detail=""):
    global P, F
    print(("  PASS " if cond else "  FAIL ") + name + ("  [%s]" % detail if detail else ""))
    P += bool(cond); F += (not cond)


def main():
    from experiments.exp_situation_model_qa_modern_v1 import board_temporal_implicit_order_dimension
    row, _det = board_temporal_implicit_order_dimension()
    if row.get("model_acc") is None:
        print("SKIP: broad-store mine / TRACIE gold unavailable (arm degraded) -- %s"
              % row.get("error", row.get("population")))
        return 0

    print("TEMPORAL implicit-event ordering (TRACIE iid test, n=%d, paired clustered bootstrap over stories)" % row["n"])
    print("  broader=%.4f (cov %.3f)  seed=%.4f  abstain=%.4f  twin=%.4f"
          % (row["model_acc"], row["coverage"], row["strongest_floor"], row["abstain_floor_acc"], row["twin_acc"]))
    print("  broader-seed %s  broader-abstain %s  broader-twin %s"
          % (row["model_minus_strongest"], row["model_minus_abstain"], row["model_minus_twin"]))

    # 1. beats the SEED store (strongest floor) CI-separated
    ok(row["ci_sep_over_strongest"] and row["model_minus_strongest"][0] > 0,
       "broader store beats SEED CI-sep", "d=%s" % row["model_minus_strongest"])
    # 2. beats abstain-majority CI-separated
    ok(row["ci_sep_over_abstain"] and row["model_minus_abstain"][0] > 0,
       "broader store beats abstain-majority CI-sep", "d=%s" % row["model_minus_abstain"])
    # 3. the info-free shuffled-ORDER twin LOSES CI-separated
    ok(row["ci_sep_over_twin"] and row["twin_acc"] < row["model_acc"],
       "shuffled-order twin LOSES CI-sep", "d=%s" % row["model_minus_twin"])
    # coverage lever + magnitude band (SOLVED: 0.5655 @ cov 0.607 vs seed 0.5296)
    ok(row["coverage"] > 0.55, "coverage lever ~doubled (0.29 -> >0.55)", "%.4f" % row["coverage"])
    ok(0.55 <= row["model_acc"] <= 0.58, "broader acc in the SOLVED band (~0.5655)", "%.4f" % row["model_acc"])
    ok(abs(row["strongest_floor"] - 0.5296) < 0.01, "seed floor reproduces (~0.5296)", "%.4f" % row["strongest_floor"])
    # the win is LIVE (the broad store is what the temporal reasoner consults on the implicit branch)
    ok(row["live_broad_store_wired"] is True, "broad store is LIVE in hdlab.temporal_reasoner._script_schema()")

    print("\n[%d PASS / %d FAIL]" % (P, F))
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
