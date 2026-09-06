"""exp_board_tom_v1 -- the THEORY-OF-MIND board arm (realizes the reasoning phase's first mentalizing system).

WHY: the reader gained a live ToM chain (owner-DONE chain_belief_and_goal..., hdlab/theory_of_mind.py,
sm.predict_action) -- predict an agent's action from what it BELIEVES x what it WANTS, acting off the BELIEVED
state so FALSE BELIEF falls out. But the board has NO ToM dimension, so this proven win is board-INVISIBLE
(live != scored). This arm scores it on the LOAD-BEARING discriminator: the BigToM FALSE-BELIEF belief-
prediction subset, where the reality-only floor is PROVABLY 0% (acting on truth fails when the agent's belief
is false), and both info-free twins (percept-shuffle, belief-shuffle) must lose.

REUSES `exp_tom_chain_belief_goal_action_v1.run()` VERBATIM (the landed theory_of_mind chain via the cell's
import, the reality-only floor, the twins, the paired-over-stories bootstrap), reshaping its
tasks.belief.FB gates into the board's per_dimension row schema so it folds into exp_situation_model_qa_v1.run()
like the other arms. MODERN gold (BigToM, Gandhi et al. 2023), 19c-clean. Glass-box, NO LLM at inference. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_tom_v1.py [--full]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_tom_chain_belief_goal_action_v1 as TOM
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_tom_v1"


def board_tom_dimension(smoke=True):
    """A per_dimension board row scoring the LANDED ToM chain's FALSE-BELIEF belief-prediction (BigToM) vs the
    reality-only floor (provably ~0% on false belief) + the harder of the two info-free twins. smoke=True keeps
    12 BigToM stories (the board default; the full number is the standalone --full run). Returns (row, detail)."""
    out = TOM.run(smoke=smoke)
    T = out["tasks"]["belief"]
    acc = T["acc"]
    gf = T["CHAIN_vs_FLOOR_FB"]                              # {delta, lo, hi, hw} on the FALSE-BELIEF subset
    tp, tb = T["CHAIN_vs_TWIN_PERCEPT_FB"], T["CHAIN_vs_TWIN_BELIEF_FB"]
    # report the HARDER (less-losing) twin as the binding info-free control
    if tp["delta"] <= tb["delta"]:
        twin_gate, twin_name, twin_acc = tp, "percept_shuffle", T["twin_percept_FB_acc"]
    else:
        twin_gate, twin_name, twin_acc = tb, "belief_shuffle", T["twin_belief_FB_acc"]
    row = {
        "n": int(out["n_FB"]),
        "model_acc": acc["CHAIN"]["FB"],
        "overlap_floor": acc["REALITY_FLOOR"]["FB"],
        "floor_accs": {"reality_only": acc["REALITY_FLOOR"]["FB"], "current_substrate_nofix": acc["CHAIN_NOFIX"]["FB"],
                       "twin_percept_shuffle": T["twin_percept_FB_acc"], "twin_belief_shuffle": T["twin_belief_FB_acc"]},
        "strongest_floor_name": "reality_only",
        "strongest_floor": acc["REALITY_FLOOR"]["FB"],
        "twin_acc": twin_acc,
        "model_minus_strongest": [gf["delta"], gf["lo"], gf["hi"]],
        "model_minus_twin": [twin_gate["delta"], twin_gate["lo"], twin_gate["hi"]],
        "ci_sep_over_strongest": bool(gf["lo"] > 0),
        "ci_sep_over_twin": bool(twin_gate["lo"] > 0),
        "population": (
            "BigToM (Gandhi et al. 2023, MODERN) FALSE-BELIEF belief-prediction subset; the LANDED "
            "hdlab.theory_of_mind chain (believes x wants -> action off the BELIEVED state) vs the "
            "reality-only floor (PROVABLY ~0% on false belief -- acting on truth fails) + the harder "
            f"info-free twin ({twin_name}). The board has NO ToM dim; this scores the reasoning phase's "
            f"first mentalizing system on its load-bearing discriminator. Overall belief-pred "
            f"CHAIN={acc['CHAIN']['overall']:.3f} vs floor 0.500."),
    }
    detail = {"smoke": smoke, "n_FB": out["n_FB"], "n_TB": out["n_TB"], "n_items": out["n_items"],
              "belief_CHAIN_overall": acc["CHAIN"]["overall"], "belief_FLOOR_overall": acc["REALITY_FLOOR"]["overall"],
              "belief_CHAIN_FB": acc["CHAIN"]["FB"], "belief_FLOOR_FB": acc["REALITY_FLOOR"]["FB"],
              "chain_vs_floor_FB": gf, "chain_vs_twin_FB": twin_gate, "binding_twin": twin_name,
              "note": "reuses exp_tom_chain_belief_goal_action_v1.run() -- the same chain landed into hdlab.theory_of_mind."}
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="full BigToM (default: smoke=12 stories)")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_tom_dimension(smoke=(not a.full))
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("THEORY-OF-MIND board arm (false-belief belief-prediction)  n_FB=%d  (%s)"
          % (row["n"], "full" if a.full else "smoke"))
    print("  model_acc (landed ToM chain, FB)  : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (reality-only, FB): %.4f" % (row["strongest_floor"] or 0))
    print("  twin (%-14s, FB)      : %.4f" % (detail["binding_twin"], row["twin_acc"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - twin  : %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("  (overall belief-pred CHAIN=%.3f vs floor 0.500)" % detail["belief_CHAIN_overall"])
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
