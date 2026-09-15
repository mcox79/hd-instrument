"""Witness -- OPTIMIZED coref component (owner request): an ACT-R base-level-activation object-anaphora resolver
(Lewis-Vasishth 2005, PINNED) as the brain-faithful upgrade over pure recency. Findings: (1) it is a REAL
organ-level improvement -- it resolves ~2.5x more object anaphora than the recency resolver; (2) BUT it is FLAT
on the TellMeWhy causal-coherence decision (ACT-R == recency == additive == its own shuffle-twin), because
TellMeWhy "why did X?" is dominantly SINGLE-ANTECEDENT cause-ID -- the multi-candidate object-chain structure the
coherence machinery exploits is rarely present; (3) the ORACLE (correct binding to the gold-cause referent) still
EXCELS CI-separated -- correct participant-binding CAN win, so the gap is TASK STRUCTURE, not coref quality. A
brain-foundational upstream improved to fidelity, revealing the real constraint is the consumer/task (the
coherence+chain mechanism needs a multi-candidate-chain gold to pay off).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_optimized_coref.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_optimized_coref_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = C.run(n=1500)
    ov = o["overall"]
    oks = []

    oks.append(check(
        "W1 the ACT-R resolver is a REAL organ-level improvement: it resolves substantially MORE object anaphora than the pure-recency resolver (base-level activation = recency-decay + frequency + phi-agreement)",
        o["n_anaphora_resolved_actr"] > 1.5 * max(o["n_anaphora_resolved_recency"], 1),
        "anaphora resolved: ACT-R %d vs recency %d" % (o["n_anaphora_resolved_actr"], o["n_anaphora_resolved_recency"])))

    oks.append(check(
        "W2 but ACT-R coref is FLAT on the TellMeWhy causal-coherence decision (== recency, == additive, == its own shuffle-twin) -- the resolved links are not load-bearing HERE (single-antecedent task structure)",
        abs(ov["coh_actr"] - ov["coh_recency"]) < 0.02 and abs(ov["coh_actr"] - ov["additive"]) < 0.02
        and abs(ov["coh_actr"] - ov["coh_actr_twin"]) < 0.02,
        "ACT-R %.3f recency %.3f additive %.3f twin %.3f" % (
            ov["coh_actr"], ov["coh_recency"], ov["additive"], ov["coh_actr_twin"])))

    oks.append(check(
        "W3 the ORACLE (correct binding to the gold-cause referent) EXCELS CI-separated -- correct participant-binding CAN win, so the gap is TASK STRUCTURE, not coref quality",
        o["oracle_vs_additive"]["ci_sep"] and ov["coh_oracle"] > ov["coh_actr"],
        "oracle %.3f vs additive %.3f (%+.4f CI%s); oracle > actr %.3f" % (
            ov["coh_oracle"], ov["additive"], o["oracle_vs_additive"]["delta"], o["oracle_vs_additive"]["ci"], ov["coh_actr"])))

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
