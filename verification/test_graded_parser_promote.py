"""Witness -- the PROMOTION-READY graded parser module (what strategy copies into hdlab/graded_parser.py).
Confirms the packaged public API is brute-force-exact and returns a valid arborescence + normalized single-root
marginals + the reliability cues, on the real landed arc-factored asset.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (promotion).
Run: .venv/Scripts/python.exe verification/test_graded_parser_promote.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import graded_parser_promote_v1 as GP


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        GP.self_test()
        oks.append(check("W0 promotion gate: packaged marginals/CLE-MAP/2nd-best are brute-force-exact + valid API on the landed asset", True))
    except AssertionError as e:
        oks.append(check("W0 promotion gate", False, str(e)))

    gp = GP.GradedParse.load()
    toks = ["They", "sent", "the", "editor", "a", "letter", "about", "the", "delay", "."]
    pos = ["PRON", "VERB", "DET", "NOUN", "DET", "NOUN", "ADP", "DET", "NOUN", "PUNCT"]
    out = gp.parse(toks, pos, want_second_best=True)
    n = len(toks)

    oks.append(check("W1 map_heads is a valid single-rooted arborescence (exact MAP decode)",
                     all(0 <= h <= n for h in out.map_heads.values()) and sum(1 for h in out.map_heads.values() if h == 0) >= 1,
                     "heads=%s" % out.map_heads))
    oks.append(check("W2 single-root marginals are proper distributions (sum to 1 per token)",
                     all(abs(sum(out.marginals[i].values()) - 1.0) < 1e-6 for i in range(1, n + 1)),
                     "per-token marginal mass all ~1.0"))
    oks.append(check("W3 the reliability cues are exposed (patient_confidence_cue + attachment_reliability)",
                     0.0 <= GP.patient_confidence_cue(out.marginals, 2, 4) <= 1.0
                     and len(GP.attachment_reliability(out.marginals, out.map_heads)) == n,
                     "mu(sent->editor)=%.3f" % GP.patient_confidence_cue(out.marginals, 2, 4)))

    nsum = sum(oks)
    print("=" * 80)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if nsum == len(oks) else "SOME CHECKS FAILED", nsum, len(oks)))
    print("=" * 80)
    return 0 if nsum == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
