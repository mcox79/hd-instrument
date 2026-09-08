"""Scaffold-free witness for the board arm `spatial_extraction_precision` (exp_situation_model_qa_modern_v1).

Recomputes the arm from SOURCE (no landed-metrics read; writes nowhere) and asserts the owner-DONE
extract_spatial_and_causal SPATIAL win as scored on the board: the joint semantic Figure-Ground EXTRACTOR the LIVE
reader consumes (hdlab.joint_relation_frontend.joint_spatial_frames_ext, use_thematic=True) beats, on balanced
SpaceEval containment QA with HARD adjacent negatives,
  1. the incumbent-linear extractor (strongest floor)          -- CI-separated (the semantic TYPING is load-bearing),
  2. the no-semantics density/PROXIMITY floor                  -- CI-separated (proximity collapses on hard negatives),
  3. the info-free SHUFFLED-RELATION twin                      -- CI-separated (the extracted structure is load-bearing).
And an independent byte-faithfulness check: the arm's use_thematic=False base reproduces the SOLVED precision-QA
cell's `joint` accuracy EXACTLY (the landed hdlab extractor == the experiment extract_spatial minus the refuted
marginal machinery). If the SpaceEval gold is absent the arm degrades (model_acc=None) and this witness SKIPs
(asset-less safe). ~20s (parses SpaceEval train+trial twice: once via the arm, once via the SOLVED cell).
Run: .venv/Scripts/python.exe verification/test_board_spatial_extraction_precision.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402  (PYTHONHASHSEED=0 determinism -- reproducible parse)

P = F = 0


def ok(cond, name, detail=""):
    global P, F
    print(("  PASS " if cond else "  FAIL ") + name + ("  [%s]" % detail if detail else ""))
    P += bool(cond); F += (not cond)


def main():
    from experiments.exp_situation_model_qa_modern_v1 import board_spatial_extraction_precision_dimension
    row, _det = board_spatial_extraction_precision_dimension()   # full SpaceEval train+trial (the SOLVED population)
    if row.get("model_acc") is None:
        print("SKIP: SpaceEval gold unavailable (arm degraded) -- %s" % row.get("error", row.get("population")))
        return 0

    print("SPATIAL extraction TYPE-precision (SpaceEval train+trial, n=%d queries over %d docs)"
          % (row["n"], row["n_docs_scored"]))
    print("  ext(use_thematic=True)=%.4f  incumbent=%.4f  density=%.4f  twin=%.4f"
          % (row["model_acc"], row["strongest_floor"], row["density_floor_acc"], row["twin_acc"]))
    print("  ext-incumbent %s  ext-density %s  ext-twin %s"
          % (row["model_minus_strongest"], row["model_minus_density"], row["model_minus_twin"]))

    # 1. the win over the incumbent-linear floor is CI-separated
    ok(row["ci_sep_over_strongest"] and row["model_minus_strongest"][0] > 0,
       "ext beats incumbent-linear CI-sep", "d=%s" % row["model_minus_strongest"])
    # 2. the win over the density/proximity floor is CI-separated (and the floor collapsed on hard negatives)
    ok(row["ci_sep_over_density"] and row["model_minus_density"][0] > 0.30,
       "ext beats density/proximity floor CI-sep (+>0.30)", "d=%s" % row["model_minus_density"])
    ok(row["density_floor_acc"] < 0.30, "density floor COLLAPSES on hard negatives", "%.4f" % row["density_floor_acc"])
    # 3. the info-free shuffled-relation twin LOSES CI-separated
    ok(row["ci_sep_over_twin"] and row["twin_acc"] < row["model_acc"],
       "shuffled-relation twin LOSES CI-sep", "d=%s" % row["model_minus_twin"])
    # sanity: the win reproduces the SOLVED magnitude band (ext >= 0.57, incumbent floor ~chance)
    ok(row["model_acc"] >= 0.57, "ext TYPE-precision >= 0.57 (SOLVED ~0.57-0.59)", "%.4f" % row["model_acc"])

    # 4. byte-faithfulness: the arm's use_thematic=False base == the SOLVED precision-QA cell's `joint` (the landed
    #    hdlab extractor is byte-faithful to the experiment extract_spatial minus the refuted marginal machinery)
    base = row["ext_base_reproduces_solved"]
    import experiments.exp_joint_spatial_precision_qa_v1 as PQ
    ref = PQ.run(smoke=False)
    print("  SOLVED-cell joint=%.4f  arm ext_base=%.4f  (incumbent cell=%.4f arm=%.4f)"
          % (ref["accuracy"]["joint"], base["ext_base_acc"], ref["accuracy"]["incumbent"], base["incumbent_acc"]))
    ok(abs(base["ext_base_acc"] - ref["accuracy"]["joint"]) < 1e-4,
       "arm ext_base == SOLVED-cell joint (byte-faithful landed extractor)",
       "%.4f vs %.4f" % (base["ext_base_acc"], ref["accuracy"]["joint"]))
    ok(abs(base["incumbent_acc"] - ref["accuracy"]["incumbent"]) < 1e-4,
       "arm incumbent == SOLVED-cell incumbent", "%.4f vs %.4f" % (base["incumbent_acc"], ref["accuracy"]["incumbent"]))
    ok(base["ci_sep"] and base["delta"] > 0, "base (use_thematic=False) beats incumbent CI-sep", "d=%s" % base["delta"])

    print("\n[%d PASS / %d FAIL]" % (P, F))
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
