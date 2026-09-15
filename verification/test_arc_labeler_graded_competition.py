"""Scaffold-free witness: the arc labeler's fast-path lane[] feeds the LANDED graded_competition organ,
adding a calibrated gold-free uncertainty signal at ZERO output cost.

Problem: add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost (brain-foundational extension).

  G1  argmax(lane) == stock _predict_label byte-identical on held-out UD-EWT TEST arcs (MAP-optimality:
      the graded readout is a strict superset of the discrete one -> wiring it regresses NO consumer).
  G2  the label-distribution normalized ENTROPY (hdlab.graded_competition) flags labeling ERRORS gold-free:
      entropy(wrong) > entropy(right) CI-separated AND AUC(entropy->error) materially > 0.5, while the
      INFO-FREE twin (shuffled cue validities) AUC ~ 0.5 (LOSES). This is the same property the landed
      discrete_where_the_brain_is_graded organ validated for parser/role competition, now at the labeler.

Reruns NO landed cell; recomputes on held-out gold. NO LLM. numpy + pure-python.
Run: .venv/Scripts/python.exe verification/test_arc_labeler_graded_competition.py
"""
from __future__ import annotations
import os, sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_arc_labeler_graded_competition_v1 as G

PASS = 0; FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok; FAIL += (not ok)


if __name__ == "__main__":
    print("witness: arc-labeler graded competition readout (reuses hdlab.graded_competition)")
    r = G.run(max_sents=1500)   # writes its own metrics dir; returns the measured dict
    chk("G1 argmax(lane) == stock _predict_label byte-identical on held-out UD-EWT test",
        r["argmax_byte_identity_mismatches"] == 0,
        "%d mismatches / %d arcs" % (r["argmax_byte_identity_mismatches"], r["n_arcs"]))
    ent_lo = r["entropy_ci"][0]
    real_auc = r["auc_entropy_to_error"]; twin_auc = r["auc_infofree_twin_entropy_to_error"]
    chk("G2 label-uncertainty flags errors gold-free (entropy CI-sep>0, AUC>>0.5) and the info-free twin loses",
        ent_lo > 0.0 and real_auc >= 0.60 and abs(twin_auc - 0.5) < 0.05,
        "entropy wrong-right CI_lo=%+.4f | AUC entropy->err=%.4f | info-free twin AUC=%.4f | acc=%.4f"
        % (ent_lo, real_auc, twin_auc, r["label_accuracy"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    sys.exit(0 if FAIL == 0 else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
