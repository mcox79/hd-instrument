"""Witness -- the FULL brain-foundational who-did-what chain + the argument-role competition ORGAN.

Prototypes the end-to-end chain (tagger -> graded Matrix-Tree parser -> thematic fit -> argument-role competition
-> gated readout) and establishes the LOCATED NEGATIVE: sentence-internal top-down cues do NOT beat the strong
labeled reader (fusion ~ twin; discourse-cue validities near-zero), because the two-valid residual needs the
DOCUMENT-level discourse center + implicit-causality norms -- a distinct organ (WALLS_RESEARCHED_2026-09-07.md).

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (organ + full chain).

Run: .venv/Scripts/python.exe verification/test_full_brain_chain.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_full_brain_chain_v1 as FC


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = FC.run(smoke=True)
    fc = o["full_chain"]; tw = o["twin_shuffled_topdown_cues"]; val = o["learned_cue_validities"]
    cls = o["recovery_by_class"]

    oks.append(check("W1 the full chain runs END-TO-END (tagger->graded parser->thematic fit->argument-role organ->gated readout)",
                     "acc" in fc and o["n_test"] > 0 and o["n_train"] > 0,
                     "n_test=%d blanket=%.4f full-chain=%.4f" % (o["n_test"], o["blanket_labeled_reader"], fc["acc"])))
    oks.append(check("W2 LOCATED NEGATIVE: the sentence-internal top-down organ does NOT beat the strong labeled reader, and fusion ~ twin",
                     fc["delta_vs_blanket"] <= 0.005 and abs(fc["acc"] - tw["acc"]) < 0.02,
                     "full-chain delta %s (CI %s); twin delta %s -> the top-down cues are not load-bearing here" % (fc["delta_vs_blanket"], fc["ci"], tw["delta"])))
    oks.append(check("W3 WHY (learned cue validities): SYNTAX dominates; sentence-internal DISCOURSE cues (givenness/salience) are near-zero",
                     val["syn"] > 3 * max(val["new"], val["notsubj"], 1e-9),
                     "syn=%.3f givenness(new)=%.3f salience(notsubj)=%.3f postverb=%.3f -> two-valid are two GIVEN entities; sentence givenness is silent" % (val["syn"], val["new"], val["notsubj"], val["postverb"])))
    tv = cls.get("TWO_VALID", {"n": 1, "recovered": 0})
    oks.append(check("W4 the two-valid slice stays largely UNRECOVERED sentence-level -> it needs the DOCUMENT discourse center + IC norms (a distinct organ)",
                     tv["recovered"] / max(tv["n"], 1) < 0.35,
                     "two-valid recovered %d/%d (%.0f%%)" % (tv["recovered"], tv["n"], 100 * tv["recovered"] / max(tv["n"], 1))))

    n = sum(oks)
    print("=" * 80)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 80)
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
