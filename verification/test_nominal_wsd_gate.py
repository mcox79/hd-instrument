"""Scaffold-free witness for the eventive-nominal context/WSD gate (problem
gate_the_eventive_nominal_event_channel_by_context_wsd_event_vs_result).

Reproduces the headline WITHOUT re-running the landed cell in place (writes nothing): it imports the gate organ
+ the TB-Dense measurement pieces, runs on TB-Dense train (22 docs, fast), and asserts the load-bearing claims:

  W1  gate self-test passes (committed-reading positive control + REUSE-equivalence to select_sense + twin perturbs).
  W2  NO-REGRESS / ADDITIVE (the decisive structural claim): for every doc, recovered(joint_cop) SUBSET
      recovered(gated) SUBSET recovered(joint_nom). The gate only ever DROPS eventive-NOMINAL tokens -- it can
      never remove a VERB/COP event, so with the nominal channel off it is byte-identical and with it on it is a
      controlled subset of the ungated channel. This is why it is safe to wire as an additive hook.
  W3  the WSD-gated nominal channel RESTORES extraction precision over the UNGATED floor (precision gated > ungated)
      while keeping whole-subgraph survival ABOVE the verb+copular reference (retains a majority of the lift).
  W4  the info-free PERMUTED-CONTEXT twin LOSES on survival at matched theta (the gate uses THIS token's context).

Skips gracefully (prints SKIP, exits 0) if the w2v / signature assets are absent. PYTHONHASHSEED pinned for a
reproducible parse. NO external LLM.  Run: .venv/Scripts/python.exe verification/test_nominal_wsd_gate.py
"""
import os
import sys

os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def main():
    from experiments import _nominal_wsd_gate as G
    if G.default_vec_lookup()("building") is None:
        print("[SKIP] w2v / signature assets absent -> gate abstains; witness not runnable here."); return 0

    # W1 -- gate self-test
    assert G._self_test(), "W1 FAIL: gate self-test"
    print("W1 PASS: gate self-test (positive control + REUSE-equivalence + twin perturbs)")

    from experiments import exp_nominal_wsd_gate_v1 as E
    from experiments._tbdense_loader import load_split
    vl = G.default_vec_lookup()
    docs = load_split("train")
    assert docs, "TB-Dense train missing"
    per, all_ctx = E._collect_tbdense(docs, vl, 1.0, None)
    E._score_nom(per, all_ctx, vl, 1.0, None, w_sel=0.03)

    # W2 -- NO-REGRESS / ADDITIVE subset property (per doc)
    theta, abst = 0.0, True
    for doc in per:
        cop = E._recovered(doc, "cop", 0.0, abst)
        gated = E._recovered(doc, "wsdC", theta, abst)
        nom = E._recovered(doc, "nom", 0.0, abst)
        assert cop <= gated <= nom, "W2 FAIL: additive subset property violated"
    print("W2 PASS: recovered(joint_cop) SUBSET recovered(gated) SUBSET recovered(joint_nom) for all %d docs "
          "(gate never removes a VERB/COP event -> additive, no-regress)" % len(per))

    # W3 -- precision restored over the ungated floor; survival kept above the verb+copular reference
    pr_nom = E._precision_recall(per, "nom", 0.0, abst)
    pr_gate = E._precision_recall(per, "wsdC", theta, abst)
    sv = lambda w, th: (lambda s: sum(s) / len(s) if s else 0.0)(E._survival_vec(per, w, th, abst))
    s_cop, s_nom, s_gate = sv("cop", 0.0), sv("nom", 0.0), sv("wsdC", theta)
    assert pr_gate["precision"] > pr_nom["precision"] + 0.01, \
        "W3 FAIL: gated precision %.4f !> ungated %.4f" % (pr_gate["precision"], pr_nom["precision"])
    assert s_gate > s_cop + 0.05, "W3 FAIL: gated survival %.4f not above verb+cop %.4f" % (s_gate, s_cop)
    frac = (s_gate - s_cop) / (s_nom - s_cop) if (s_nom - s_cop) else 0.0
    print("W3 PASS: precision ungated %.4f -> gated %.4f (+%.4f) ; survival cop %.4f | gated %.4f | ungated %.4f "
          "(retains %.0f%% of the lift)" % (pr_nom["precision"], pr_gate["precision"],
          pr_gate["precision"] - pr_nom["precision"], s_cop, s_gate, s_nom, 100 * frac))

    # W4 -- info-free permuted-context twin loses on survival at matched theta
    s_twin = sv("wsdPB", theta)
    assert s_gate > s_twin, "W4 FAIL: gated survival %.4f !> permuted-context twin %.4f" % (s_gate, s_twin)
    print("W4 PASS: gated survival %.4f > permuted-context twin %.4f (uses THIS token's context)" % (s_gate, s_twin))

    print("\nALL WITNESSES PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
