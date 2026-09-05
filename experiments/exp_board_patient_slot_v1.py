"""exp_board_patient_slot_v1 -- the PATIENT-slot who-did-what BOARD ARM (Step 0 of the top-down
integration pass; notes/INTEGRATION_PASS_PLAN.md).

WHY: the live board's who-did-what quiz (`exp_situation_model_qa_v1.build_events_questions`) asks
AGENT-only, and the LitBank patient/object gold is ~76%-oblique CONFOUNDED (multiple solvers flag it
INVALID). So the LANDED, DEFAULT-ON structure-first patient readout
(`hdlab.predicate_argument_frontend.structural_patient_pick`, +0.086 on clean UD) is INVISIBLE on the
board. This arm scores that live readout on the CLEAN UD-EWT structural gold (patient := gold `obj`
(active) / `nsubj:pass` (passive), off GOLD deprels) so the already-live gain becomes a scored board
dimension.

It REUSES the proven instrument `exp_valency_labeled_patient_v1` verbatim (its eval_split scores the
LANDED `structural_patient_pick` as `R_final` on the LIVE arc parser vs the frozen deployed floor
`R0_landed` + info-free twins + the gold-parse ceiling), and reshapes the LIVE-parser result into the
board's per_dimension row schema (model_acc / strongest_floor / twin_acc / model_minus_strongest[obs,lo,hi]
/ ci_sep_*), so it folds into `exp_situation_model_qa_v1.run()` exactly like the state/goal/affect arms.

Glass-box, NO external LLM, hdlab READ-only, clean UD gold (an admissible foundation corpus). ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_patient_slot_v1.py [--cap 150]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_valency_labeled_patient_v1 as VLP
import experiments.exp_whodidwhat_ud_structural_v1 as UD
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_patient_slot_v1"
_LIVE = "arc"   # the LIVE arc parser route (the reader's default parser); "arceager" is the opt-off variant


def board_patient_dimension(cap=None, seed=0):
    """A per_dimension board row (schema-matched to board_goal_dimension) scoring the LIVE, default-on
    structure-first PATIENT readout on the CLEAN UD-EWT gold. Returns (row, detail).

    model_acc          = R_final  (the LANDED structural_patient_pick, live arc parser)
    strongest_floor    = R0_landed (the frozen pre-upgrade deployed floor, 0.745)
    twin_acc           = twin_shufheads (info-free: random verb-head attachment)
    model_minus_*      = paired cluster-bootstrap CI [obs, lo, hi] over shared UD sentences
    ceiling (detail)   = ceiling_gold (gold parse + gold labels) -- the residual head-attachment gap
    """
    tagger = VLP.PosTagger.load(VLP.POS_ASSET)
    labeler = VLP.ArcLabeler.load(VLP.LAB_ASSET)
    arc = VLP.ArcParser.load(VLP.ARC_ASSET)
    from hdlab.arceager_parser import load_model, MODEL_PATH
    aeW = load_model(MODEL_PATH)
    sents = UD.load_ud(VLP.UD_TEST)
    if cap:
        sents = sents[:cap]
    H, _routes, _parsers = VLP.eval_split(sents, tagger, labeler, arc, aeW, seed=seed)
    h = H[_LIVE]
    model_m, model_hw = VLP._boot_ci(h["R_final"])
    floor_m, floor_hw = VLP._boot_ci(h["R0_landed"])
    twin_m, twin_hw = VLP._boot_ci(h["twin_shufheads"])
    ceil_m, ceil_hw = VLP._boot_ci(h["ceiling_gold"])
    ms = VLP._paired_ci(h["R_final"], h["R0_landed"])      # [obs, lo, hi]
    mt = VLP._paired_ci(h["R_final"], h["twin_shufheads"])
    n = sum(len(x) for x in h["R_final"])
    row = {
        "n": n, "model_acc": model_m,
        "overlap_floor": floor_m,
        "floor_accs": {"deployed_position_readout": floor_m},
        "strongest_floor_name": "deployed_position_readout",
        "strongest_floor": floor_m,
        "twin_acc": twin_m,
        "model_minus_strongest": ms,
        "model_minus_twin": mt,
        "ci_sep_over_strongest": bool(ms[1] is not None and ms[1] > 0),
        "ci_sep_over_twin": bool(mt[1] is not None and mt[1] > 0),
        "population": "clean UD-EWT test who-did-what PATIENT (gold obj/nsubj:pass off GOLD deprels), "
                      "live arc parser; LitBank patient gold is oblique-confounded/INVALID -> use this",
    }
    detail = {
        "n": n, "model_R_final": model_m, "model_ci_hw": model_hw,
        "floor_R0_landed": floor_m, "twin_shufheads": twin_m,
        "ceiling_gold_parse": ceil_m,
        "model_minus_floor": ms, "model_minus_twin": mt,
        "note": "PATIENT-slot board arm (Step 0). Reuses exp_valency_labeled_patient_v1.eval_split (R_final = "
                "the landed structural_patient_pick, live arc route). model beats the deployed position floor "
                "(the +0.086 clean-UD win, previously board-invisible) with a random-head twin LOSING; the "
                "residual to ceiling_gold is genuine head-attachment (the parser, a filed follow-on).",
    }
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=None, help="cap UD-EWT test sentences (None = full split)")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_patient_dimension(cap=(150 if a.self_test else a.cap))
    out_dir = get_output_dir(ANCHOR)                     # Q115: shared helper, not a hardcoded path
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("PATIENT-slot board arm (clean UD-EWT, live arc parser)  n=%d" % row["n"])
    print("  model_acc (landed structural_patient_pick) : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (deployed position readout): %.4f" % (row["strongest_floor"] or 0))
    print("  twin_acc (random-head, info-free)          : %.4f" % (row["twin_acc"] or 0))
    print("  ceiling (gold parse+labels)                : %.4f" % (detail["ceiling_gold_parse"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - twin  : %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
