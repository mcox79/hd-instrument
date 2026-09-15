"""Witness -- deepening-cron cycle 2: binding generative causal edges to a SHARED RESOLVED PARTICIPANT to raise
precision. LOCATED NEGATIVE: surface content-noun participant-binding does NOT help -- it makes edges sparser
AND lower-accuracy, because in real narrative the shared participant is usually COREF-RESOLVED or a pronoun
(the causal chain shares the protagonist/an implicit entity, not a surface noun), so surface-overlap gating
kills real causal edges. The faithful participant-binding needs REAL coref (E3, NEEDS_ADAPTER) + the meaning
channel -- the same upstream dependency the whole arc converges on. The ECHO coalition mechanism stays intact.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_participant_bound_edges.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_participant_bound_edges_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(n=1500)
    sw = o["sweep"]; ov = o["overall"]
    bd = sw[o["best_bound"]]; un = sw[o["best_unbound"]]
    oks = []

    oks.append(check(
        "W1 surface participant-binding makes edges SPARSER (kills real causal edges whose shared entity is coref-resolved/pronominal, not a surface noun)",
        bd["density"] < un["density"],
        "bound density %.3f < unbound density %.3f" % (bd["density"], un["density"])))

    oks.append(check(
        "W2 LOCATED NEGATIVE: surface participant-binding does NOT raise precision -- bound accuracy <= unbound (the surface-noun proxy is the wrong participant signal)",
        bd["acc"] <= un["acc"] + 0.005,
        "bound acc %.3f vs unbound acc %.3f (binding_raises_precision=%s)" % (
            bd["acc"], un["acc"], o["binding_raises_precision"])))

    oks.append(check(
        "W3 bound edges do NOT beat the additive decision CI-sep on real data (the residual is REAL coref + the meaning channel, both latent/NEEDS_ADAPTER upstream)",
        not o["coh_bound_vs_additive"]["ci_sep"],
        "coh_bound %.3f vs additive %.3f (%s)" % (ov["coh_bound"], ov["additive"], o["coh_bound_vs_additive"]["ci"])))

    oks.append(check(
        "W4 the ECHO coalition mechanism stays intact (constructed control): signed-pairwise coherence still beats additive-argmax where a coalition should win",
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
