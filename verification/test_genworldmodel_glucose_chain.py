"""Witness -- the corrected chain on the RIGHT gold (GLUCOSE narrative causal-CHAIN cause-selection), a rigorous
LOCATED NEGATIVE that refutes the coalition-as-lever hypothesis on real narrative and identifies the
brain-foundational signal that DOES carry. On the >=3-candidate NON-ADJACENT coalition subset:
 * the ECHO explanatory-coherence COALITION does NOT beat the additive decision (coherence <= additive, in fact
   CI-separated BELOW) -- the coalition mechanism, proven on the constructed control, does not win on real
   narrative because the GENERATED candidate-candidate causal edges are too noisy/sparse;
 * the shuffled-edge twin does NOT lose (coherence <= twin_shuffled) -> the generated edges are NOT load-bearing
   (the edge-correctness wall, now confirmed on a chain gold, not just single-antecedent TellMeWhy);
 * the DOMINANT brain-foundational signal is TOPICAL content/participant connectivity (Trabasso & van den Broek
   causal-network connectivity; Collins-Loftus spreading activation): topical > additive > coherence -- the
   generative means-end + coalition machinery ADDS NOISE relative to associative connectivity;
 * the coalition mechanism is intact on the constructed control (so the refutation is about real-data edge
   QUALITY, not the mechanism in principle). This confirms, across TWO real golds, that the binding wall is
   generating CORRECT causal edges from text (the meaning-channel/knowledge foundation), not the decision layer.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_glucose_chain.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_glucose_chain_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 REFUTED on real narrative: the ECHO coherence-coalition does NOT beat the additive decision on the >=3-candidate coalition subset (coherence <= additive)",
        ov["coherence"] <= ov["additive"] + 0.005,
        "coherence %.3f vs additive %.3f (coh-additive %+.4f CI%s)" % (
            ov["coherence"], ov["additive"], cs["coherence_vs_additive"]["delta"], cs["coherence_vs_additive"]["ci"])))

    oks.append(check(
        "W2 the generated candidate-candidate causal edges are NOT load-bearing: coherence does NOT beat its own shuffled-edge twin (the edge-correctness wall, confirmed on a CHAIN gold)",
        ov["coherence"] <= ov["twin_shuffled"] + 0.005,
        "coherence %.3f vs shuffled-edge twin %.3f (coh-twin %+.4f CI%s)" % (
            ov["coherence"], ov["twin_shuffled"], cs["coherence_vs_twin_shuffled"]["delta"], cs["coherence_vs_twin_shuffled"]["ci"])))

    oks.append(check(
        "W3 the DOMINANT brain-foundational signal is TOPICAL content/participant connectivity (Trabasso; Collins-Loftus): topical > additive AND topical > coherence -- the generative means-end + coalition ADD NOISE",
        ov["topical"] > ov["additive"] and ov["topical"] > ov["coherence"],
        "topical %.3f > additive %.3f, coherence %.3f, coref %.3f (adjacency %.3f)" % (
            ov["topical"], ov["additive"], ov["coherence"], ov["coherence_coref"], ov["adjacency"])))

    oks.append(check(
        "W4 the coalition mechanism is intact on the CONSTRUCTED control (the refutation is about real-data edge QUALITY, not the mechanism in principle)",
        o["coalition_control"]["coherence_beats_additive"],
        "constructed coalition_beats_additive=%s" % o["coalition_control"]["coherence_beats_additive"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s  n_coalition_subset=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"], cs["n"]))
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
