"""Witness -- deepening-cron cycle 1: GENERATE-DON'T-RETRIEVE for the causal edges (attack the edge-correctness
wall c), with a phase-diagram density-precision sweep. Findings: (1) high-density generated edges FLOOD the
coherence network and HURT; a precise operating point (swept tau) recovers -- the wall is a movable operating
point, not a ceiling; (2) at the optimum, GENERATED edges beat CSKG-RETRIEVAL edges (generate > retrieve
confirmed); (3) but still NOT CI-sep over the additive decision, because the class-level intuitive-theory
engines are precision-coverage-bound -> the residual is PARTICIPANT-BOUND, content-sensitive edges over the
(latent) meaning channel. The ECHO coalition mechanism stays intact.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_generative_edges.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_generative_edges_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(n=1500)
    sw = o["sweep"]; ov = o["overall"]
    flood = sw["d0_tau0.0"]; best = sw[o["best_config"]]
    oks = []

    oks.append(check(
        "W1 PHASE-DIAGRAM density-precision tradeoff: flooding with high-density generated edges HURTS, and a precise operating point (swept tau) RECOVERS it (a movable operating point, not a ceiling)",
        flood["density"] > 0.4 and best["acc"] > flood["acc"] + 0.03,
        "flood tau0: density %.3f acc %.3f -> best %s: density %.3f acc %.3f" % (
            flood["density"], flood["acc"], o["best_config"], best["density"], best["acc"])))

    oks.append(check(
        "W2 GENERATE > RETRIEVE at the optimum: generated-edge coherence beats CSKG-retrieval-edge coherence",
        ov["coh_gen"] > ov["coh_cskg"],
        "coh_GEN %.3f vs coh_CSKG %.3f (gen density %.3f vs cskg %.3f)" % (
            ov["coh_gen"], ov["coh_cskg"], o["gen_link_density"], o["cskg_link_density"])))

    oks.append(check(
        "W3 LOCATED NEGATIVE: even the best generated edges do NOT beat the additive decision CI-sep -- the class-level intuitive-theory engines are precision-coverage-bound (residual = participant-bound edges over the meaning channel)",
        not o["coh_gen_vs_additive"]["ci_sep"],
        "coh_gen %.3f vs additive %.3f (%s)" % (ov["coh_gen"], ov["additive"], o["coh_gen_vs_additive"]["ci"])))

    oks.append(check(
        "W4 the ECHO coalition mechanism stays intact (constructed control): signed-pairwise coherence beats additive-argmax where a coalition should win",
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
