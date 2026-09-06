"""exp_board_byhead_agent_v1 -- the BY-AGENT (non-canonical who-did-what AGENT) board arm.

WHY: the landed `byhead` case-morphology cue (owner-DONE grounded_meaning_role_cue...) lifts the live
who-did-what AGENT competition on non-canonical/passive clauses ("the tea was poured by the WOMAN") on MODERN
QA-SRL 0.2556->0.6889, but the board's ONLY agent gold is 19c LitBank built from SYNTACTIC SUBJECTS (~no
by-agent questions), so the win is board-INVISIBLE (live != scored) -- the board even reads a −0.0016 gate
false-fire on archaic 'by oneself'. This arm scores it on the RIGHT (modern, register-balanced) instrument.

REUSES `exp_noncanonical_agent_bymorph_v1.run()` VERBATIM (the live-competition `pick` + byhead cue + the
shuffled-by-membership twin + `_boot`), reshaping its `byhead_fix.non_canonical_ALL` slice into the board's
per_dimension row schema so it folds into exp_situation_model_qa_v1.run() like the other arms. MODERN QA-SRL
(19c-clean). Glass-box, NO external LLM. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_byhead_agent_v1.py [--full]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_noncanonical_agent_bymorph_v1 as BY
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_byhead_agent_v1"


def board_byhead_agent_dimension(smoke=True):
    """A per_dimension board row scoring the LANDED byhead cue on the held-out non-canonical AGENT slice
    (QA-SRL) vs the live-competition baseline (no byhead) + the shuffled-by-membership twin. smoke=True caps to
    600 rows (the board default). Returns (row, detail)."""
    res = BY.run(smoke=smoke)
    slc = res["byhead_fix"]["non_canonical_ALL"]
    vb = slc["byhead_vs_baseline"]                          # {delta,lo,hi,sep,...} (byhead vs live baseline)
    vt = slc["byhead_vs_twin"]                              # byhead vs shuffled-by-membership twin
    row = {
        "n": int(slc["n"]),
        "model_acc": slc["byhead"],
        "overlap_floor": slc["baseline"],
        "floor_accs": {"live_competition_baseline": slc["baseline"], "positional": slc.get("positional"),
                       "byhead_twin": slc["byhead_twin"]},
        "strongest_floor_name": "live_competition_baseline",
        "strongest_floor": slc["baseline"],
        "twin_acc": slc["byhead_twin"],
        "model_minus_strongest": [vb["delta"], vb["lo"], vb["hi"]],
        "model_minus_twin": [vt["delta"], vt["lo"], vt["hi"]],
        "ci_sep_over_strongest": bool(vb["sep"]),
        "ci_sep_over_twin": bool(vt["sep"]),
        "population": "held-out non-canonical/passive who-did-what AGENT (QA-SRL, MODERN, role-balanced); the "
                      "LANDED byhead case-morphology cue in the live Competition-Model AGENT competition vs the "
                      "live baseline (no byhead) + the shuffled-by-membership info-free twin. The board's only agent "
                      "gold is 19c LitBank SYNTACTIC SUBJECTS (~no by-agent Qs) so byhead is board-INVISIBLE there; "
                      "this scores it on modern by-agent gold. Canonical no-regress (self-gated OFF).",
    }
    detail = {"smoke": smoke, "n": slc["n"], "baseline": slc["baseline"], "byhead": slc["byhead"],
              "byhead_twin": slc["byhead_twin"], "best_byhead_w": res.get("best_byhead_w"),
              "model_minus_baseline": vb, "model_minus_twin": vt,
              "canonical_byte_identical": res.get("canonical_noregress", {}).get("byte_identical"),
              "note": "reuses exp_noncanonical_agent_bymorph_v1.run() (the live competition + byhead cue + twin) "
                      "-- the same organ path landed into hdlab.graded_role_assigner.agent_supports."}
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="full rows (default: smoke=600)")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_byhead_agent_dimension(smoke=(not a.full))
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("BY-AGENT (byhead) board arm  n=%d  (%s)" % (row["n"], "full" if a.full else "smoke"))
    print("  model_acc (live competition + byhead) : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (baseline, no byhead) : %.4f" % (row["strongest_floor"] or 0))
    print("  twin (shuffled by-membership)         : %.4f" % (row["twin_acc"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - twin  : %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
