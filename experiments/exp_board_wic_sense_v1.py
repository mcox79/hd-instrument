"""exp_board_wic_sense_v1 -- the WiC / SENSE-DISCRIMINATION BOARD ARM (Step 0c of the top-down pass).

WHY: there is NO meaning/word-sense dimension on the live board today, so the entire latent MEANING cluster
(the curated foundation +0.0755, the rare-sense readout, precision-weighting, and the owner-DONE curated-
foundation wire that beats the live PPR select_sense reader +0.0633 CI-sep on WiC) cannot be SCORED at all.
This arm scores the meaning channel on the board's ONE live meaning-consumed instrument -- WiC via sense
selection -- so the meaning-wire's gain (and future meaning work) registers.

It REUSES the solver's proven stack `exp_wic_optimization_stack_v1.run` verbatim (CURATED taxonomic signatures +
shared-core coarsening vs the LIVE PPR select_sense reader on the SAME held-out WiC population) and reshapes it
into the board's per_dimension row schema (model_acc / strongest_floor / twin_acc / model_minus_strongest[obs,lo,hi]
/ ci_sep_*), so it folds into `exp_situation_model_qa_v1.run()` like the state/goal/affect/patient arms.

model = CURATED_coarse (the recommended landed stack) · strongest_floor = PPR (the CURRENT live select_sense
reader) · control = PPR_coarse (curated beats it at EQUAL coarsening -> isolates the curated KNOWLEDGE, not just
coarsening). Leak-free curated signatures (the frozen asset over-reports on WiC via synset.examples()). Residual
past ~0.664 to human 0.80 = deep contextualization = the §2 invariant-boundary owner decision.

Glass-box, NO external LLM (curated WordNet foundation = admissible static asset). ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_wic_sense_v1.py [--smoke]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_wic_optimization_stack_v1 as STACK
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_wic_sense_v1"


def board_wic_dimension(mode="full"):
    """A per_dimension board row (schema-matched to board_goal_dimension) scoring the curated+coarsening sense
    picker vs the LIVE PPR select_sense reader on WiC. Returns (row, detail)."""
    res = STACK.run(mode)
    arms = res["arms"]
    model = arms["CURATED_coarse"]["acc"]      # the recommended landed stack
    floor = arms["PPR"]["acc"]                 # the CURRENT live select_sense reader
    ctrl = arms["PPR_coarse"]["acc"]           # equal-coarsening control (isolates curated knowledge)
    vp = res["vs_PPR"]["CURATED_coarse"]       # {delta, lo, hi, sep} vs the live reader
    vc = res["CURATED_coarse_vs_PPR_coarse"]   # {delta, lo, hi, sep} at equal coarsening
    ms = [vp["delta"], vp["lo"], vp["hi"]]
    mt = [vc["delta"], vc["lo"], vc["hi"]]
    row = {
        "n": res["n"], "model_acc": model,
        "overlap_floor": floor,
        "floor_accs": {"live_ppr_select_sense": floor, "ppr_coarse_control": ctrl},
        "strongest_floor_name": "live_ppr_select_sense",
        "strongest_floor": floor,
        "twin_acc": ctrl,
        "model_minus_strongest": ms,
        "model_minus_twin": mt,
        "ci_sep_over_strongest": bool(vp.get("sep")),
        "ci_sep_over_twin": bool(vc.get("sep")),
        "population": "WiC dev+test sense discrimination via select_sense; leak-free curated taxonomic signatures "
                      "+ shared-core coarsening vs the LIVE PPR select_sense reader (the board's one live meaning metric)",
    }
    detail = {
        "n": res["n"], "majority_floor": res["floor"],
        "model_CURATED_coarse": model, "live_PPR": floor, "PPR_coarse": ctrl,
        "curated_exact": arms["CURATED"]["acc"], "ppr_exact": arms["PPR"]["acc"],
        "model_minus_live_PPR": ms, "model_minus_PPR_coarse": mt,
        "headline": res["headline"],
        "note": "WiC/sense board arm (Step 0c). Reuses exp_wic_optimization_stack_v1.run. model = curated "
                "taxonomic + shared-core coarsening; floor = the live PPR select_sense reader (beats it +0.0633 "
                "CI-sep); the PPR_coarse control isolates the curated KNOWLEDGE as the lever. select_sense is "
                "currently islanded (no read()-time consumer) -- this arm SCORES the meaning channel so wiring it "
                "live registers. Residual to human 0.80 = deep contextualization (the §2 owner decision).",
    }
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_wic_dimension(mode=("smoke" if (a.smoke or a.self_test) else "full"))
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("WiC / sense-discrimination board arm  n=%d  (majority floor %.3f)" % (row["n"], detail["majority_floor"]))
    print("  model_acc (curated + coarsening)          : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (LIVE PPR select_sense)   : %.4f" % (row["strongest_floor"] or 0))
    print("  control (PPR_coarse, equal coarsening)    : %.4f" % (row["twin_acc"] or 0))
    print("  model - live PPR  : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - PPR_coarse: %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
