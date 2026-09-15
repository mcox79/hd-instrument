"""Witness -- the FAITHFUL argument-structure / frame-unification organ, integrated the right way.
Establishes the POSITIVE that supersedes the earlier "absolute recovery is a located negative": a Competition-Model
ensemble (labeled-reader anchor + graded parser marginal + argument-vs-adjunct typing + core-object) beats the
strong labeled reader CI-separated on modern gold; the arg/adjunct typing is massively load-bearing for the
standalone selector (twin collapses); it recovers the diagnosed role-error + parse-miss slices.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (faithful organ).
Run: .venv/Scripts/python.exe verification/test_argstructure_unification_organ.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_argstructure_unification_organ_v1 as AS


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = AS.run(smoke=True)
    lr = o["learned_faithful_ranker"]; org = o["argstructure_organ_dropin"]; tw = o["twin_shuffled_argadjunct_typing"]
    rec = o["recovery_of_LIVE_errors_by_slice"]

    oks.append(check("W1 the FAITHFUL argument-structure ensemble BEATS the strong labeled reader CI-separated (absolute who-did-what gain)",
                     lr["ci_separated"] and lr["delta_vs_blanket"] > 0,
                     "blanket %.4f -> ensemble %.4f (delta %s CI %s)" % (o["blanket_labeled_reader"], lr["acc"], lr["delta_vs_blanket"], lr["ci"])))
    oks.append(check("W2 the argument-vs-adjunct TYPING is massively load-bearing for the standalone selector (shuffling it collapses accuracy)",
                     tw["delta_vs_blanket"] < -0.15,
                     "standalone organ %.4f; twin(shuffled arg/adjunct typing) %.4f (delta %s)" % (org["acc"], tw["acc"], tw["delta_vs_blanket"])))
    oks.append(check("W3 the organ recovers the diagnosed ROLE-error slice (gold attached to v, wrong dependent picked) -- addressable, not irreducible",
                     rec["ROLE_gold_attached"]["frac"] > 0.2,
                     "role-error recovered %.0f%% (%d/%d); parse-miss %.0f%%" % (100 * rec["ROLE_gold_attached"]["frac"],
                     rec["ROLE_gold_attached"]["recovered_by_organ"], rec["ROLE_gold_attached"]["n_errors"], 100 * rec["PARSE_MISS"]["frac"])))
    oks.append(check("W4 the ensemble's learned cue validities weight the labeled-reader anchor + the graded marginal + arg/adjunct typing (the faithful cues, not givenness)",
                     lr["learned_cue_validities"]["is_live"] > 1.0 and lr["learned_cue_validities"]["marg"] > 0.5
                     and lr["learned_cue_validities"]["has_case"] > 0.3,
                     "validities is_live=%.2f marg=%.2f has_case=%.2f core_obj=%.2f" % (
                         lr["learned_cue_validities"]["is_live"], lr["learned_cue_validities"]["marg"],
                         lr["learned_cue_validities"]["has_case"], lr["learned_cue_validities"]["core_obj"])))

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
