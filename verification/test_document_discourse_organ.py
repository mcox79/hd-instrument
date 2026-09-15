"""Witness -- the DOCUMENT-level discourse organ (Centering salience + implicit-causality) for the two-valid residual.
Establishes the (refined) located negative: even at document level with high cue-coverage, discourse salience does
NOT discriminate the who-did-what patient on naturalistic gold -> the residual needs full coref + comprehensive IC
norms + world-knowledge, NOT a coarse top-down-salience prior.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (document organ).
Run: .venv/Scripts/python.exe verification/test_document_discourse_organ.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_document_discourse_organ_v1 as DD


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = DD.run(smoke=True)
    fp = o["full_plus_discourse"]; val = o["learned_cue_validities"]

    oks.append(check("W1 the document-aware chain runs end-to-end with real prior-sentence context",
                     o["n_test"] > 0 and o["n_train"] > 0,
                     "n_test=%d blanket=%.4f" % (o["n_test"], o["blanket_labeled_reader"])))
    oks.append(check("W2 the discourse cue has GOOD coverage (lemma-match links a candidate to a prior mention) -- so the null is NOT a coverage artifact",
                     o["discourse_cue_coverage"] > 0.4,
                     "discourse cue coverage %.3f" % o["discourse_cue_coverage"]))
    oks.append(check("W3 LOCATED NEGATIVE: the document discourse cue does NOT add over the sentence-level chain (naturalistic gold)",
                     not fp["discourse_adds_ci_separated"] and fp["delta_vs_sentence_level"] <= 0.01,
                     "discourse adds delta %s CI %s over sentence-level" % (fp["delta_vs_sentence_level"], fp["ci_vs_sentence"])))
    oks.append(check("W4 WHY: the discourse-salience cue has near-ZERO learned validity (Centering topical-continuity does not discriminate the patient here)",
                     val["disc_sal"] < 3 * 0.1 and val["syn"] > 5 * val["disc_sal"],
                     "disc_sal validity %.3f vs syn %.3f (ic %.3f) -> needs full coref + comprehensive IC + world-knowledge" % (val["disc_sal"], val["syn"], val["ic"])))

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
