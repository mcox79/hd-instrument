"""Witness -- PROTOTYPE of the REAL LEVER (owner: prototype the fix for the implicit cause->effect link,
brain-foundationally). Wired the LATENT curated meaning_foundation (200-d sense signatures, owner-DONE) live
into the confirmed structured carrier: role-structured, contrast-normalised (mean-centered), context-conditioned
concept matching over 100% brain-foundational glass-box-parsed roles. RIGOROUS LOCATED NEGATIVE, powered on pooled
TellMeWhy-GOAL (n=935):
  (W1) THE CURATED KNOWLEDGE IS NOT LOAD-BEARING -- the meaning-grounded cue ties its KNOWLEDGE-SHUFFLE twin
       (same words, scrambled curated meanings; +0.011 CI includes 0). The curated meanings add ~nothing over
       scrambled -> concept-SIMILARITY is the wrong KIND of knowledge for this lever.
  (W2) NO integrator lift (concept similarity does not help select the cause).
  (W3) does NOT recover the zero-overlap residual (0.143 vs base 0.546) -- the implicit link is not a
       concept-similarity relation.
  (W4) verdict: this is the SAME wall as cycle-24 (directed ATOMIC transition knowledge also not load-bearing),
       from the OTHER knowledge kind. Both CONTEXT-FREE knowledge forms (directed-causal ATOMIC + associative
       meaning_foundation) fail in the structured generative frame => the residual needs CONTEXT-CONDITIONED
       GENERATIVE simulation (predict THIS story's result-state; the recurrent world-model loop = the parent
       problem's main event, Q111), NOT more/better static knowledge. This CORRECTS the Q111 spec: "wire the
       meaning foundation" is insufficient (it is associative); the lever is a directed generative forward model.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_meaning_grounded_bridge.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_meaning_grounded_bridge_v1 as M


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = M.run(cap=3000)
    oks = []

    oks.append(check(
        "W1 the CURATED meaning knowledge is NOT load-bearing -- the meaning-grounded bridge ties its "
        "KNOWLEDGE-SHUFFLE twin (same words, scrambled curated meanings): concept-SIMILARITY is the wrong KIND "
        "of knowledge for the implicit cause->effect link",
        not (o["mground_vs_kshuf_twin"]["ci_sep"] and o["mground_vs_kshuf_twin"]["delta"] > 0),
        "solo mg %.3f vs know-shuffle twin %.3f (%+.4f CI%s); coverage %.2f (%d/%d curated keys)" % (
            o["solo_mground"], o["solo_kshuf"], o["mground_vs_kshuf_twin"]["delta"],
            o["mground_vs_kshuf_twin"]["ci"], o["coverage"], o["n_covered"], o["n_keys"])))

    oks.append(check(
        "W2 NO CI-sep integrator lift (concept similarity does not help select the cause)",
        not (o["mground_vs_base"]["ci_sep"] and o["mground_vs_base"]["delta"] > 0),
        "base %.3f +mg %.3f (%+.4f CI%s)" % (
            o["acc_base"], o["acc_with_mground"], o["mground_vs_base"]["delta"], o["mground_vs_base"]["ci"])))

    oks.append(check(
        "W3 does NOT recover the zero-overlap residual (concept similarity is not the implicit-link relation)",
        o["zov_mground_hit"] <= o["zov_base_hit"] + 0.02,
        "zero-overlap gold n=%d: mg %.3f vs base %.3f" % (
            o["n_zero_overlap_gold"], o["zov_mground_hit"], o["zov_base_hit"])))

    oks.append(check(
        "W4 verdict = the SAME wall as cycle-24 from the other knowledge kind: both CONTEXT-FREE knowledge forms "
        "(directed ATOMIC + associative meaning_foundation) fail -> the lever is CONTEXT-CONDITIONED GENERATIVE "
        "simulation (Q111), not more static knowledge",
        o["verdict"] in ("MEANING_BRIDGE_NO_LIFT_KNOWLEDGE_NOT_LOAD_BEARING",
                         "MEANING_BRIDGE_LIFTS_NOT_LOAD_BEARING")
        and not o["knowledge_load_bearing"], o["verdict"]))

    n = sum(oks)
    print("=" * 100)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 100)
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
