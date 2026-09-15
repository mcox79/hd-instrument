"""Witness -- deepening-cron cycle 3: PROTOTYPE THE UPSTREAM (coref-resolved participant binding) end-to-end by
CALLING the landed EntityBinder object-anaphora resolver, and show the mechanism EXCELS when the binding is
correct. Findings: (1) ORACLE participant-binding (share the GOLD-cause referent) beats the additive decision
CI-separated -- correct resolved-referent binding + the ECHO coherence decision DELIVER (excel/exceed proven);
(2) real recency-based object-anaphora resolution runs (it->antecedent) but is FLAT (== surface) because recency
is too weak to recover the causal-chain referent -- the residual is coref CORRECTNESS, closed by the full
ACT-R/Centering document coref (landed `event_centrality_coref`, needs document-level wiring, Q111); (3) NO
downstream regress. A brain-foundational mechanism starved by a weak upstream (recency vs full coref).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_resolved_referent_binding.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_resolved_referent_binding_v1 as R


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = R.run(n=1500)
    ov = o["overall"]
    oks = []

    oks.append(check(
        "W1 EXCEL/EXCEED PROVEN: ORACLE participant-binding (share the GOLD-cause referent) + the ECHO coherence decision BEATS the additive decision CI-separated -- correct resolved-referent binding delivers",
        o["oracle_vs_additive"]["ci_sep"] and ov["coh_oracle"] > ov["additive"],
        "oracle %.3f vs additive %.3f (%+.4f CI%s)" % (
            ov["coh_oracle"], ov["additive"], o["oracle_vs_additive"]["delta"], o["oracle_vs_additive"]["ci"])))

    oks.append(check(
        "W2 the UPSTREAM was prototyped end-to-end (real object-anaphora resolution ran, calling the landed EntityBinder), but recency resolution is FLAT (== surface) -- the residual is coref CORRECTNESS, not the mechanism",
        o["n_object_anaphora_resolved"] > 20 and abs(ov["coh_resolved"] - ov["coh_surface"]) < 0.02
        and ov["coh_oracle"] > ov["coh_resolved"],
        "obj-anaphora resolved %d; resolved %.3f == surface %.3f < oracle %.3f (the coref-quality gap)" % (
            o["n_object_anaphora_resolved"], ov["coh_resolved"], ov["coh_surface"], ov["coh_oracle"])))

    oks.append(check(
        "W3 NO downstream regress: resolved-referent binding does not drop below the unbound structural coherence",
        o["no_regress_vs_unbound"],
        "coh_resolved %.3f >= coh_unbound %.3f" % (ov["coh_resolved"], ov["coh_unbound"])))

    oks.append(check(
        "W4 the ECHO coalition mechanism stays intact (constructed control)",
        o["coalition_control"]["coherence_beats_additive"],
        "coalition control coherence_beats_additive=%s" % o["coalition_control"]["coherence_beats_additive"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED",
                                      n, len(oks), o["verdict"]))
    print("=" * 92)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
