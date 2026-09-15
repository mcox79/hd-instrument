"""Witness -- the close-out drill: the full-stack residual is the genuine glass-box floor (no cue lever left).

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (close-out).

Run: .venv/Scripts/python.exe verification/test_coref_closeout_drill.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_coref_closeout_drill_gum_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        C.self_test()
        oks.append(check("W0 full-stack self-test", True))
    except AssertionError as e:
        oks.append(check("W0 full-stack self-test", False, str(e)))

    o = C.run()
    r = o["residual_of_misses"]; t = o["topicality_lever"]
    frac = r["reachable_miss_class_frac"]

    oks.append(check("W1 the reachable-but-mispicked residual is DOMINATED by genuine same-gender ambiguity",
                     frac.get("same_gender_ambiguous", 0) > 0.5,
                     "same-gender ambiguous = %.2f of reachable misses (%s)" % (frac.get("same_gender_ambiguous", 0), r["reachable_miss_class"])))
    oks.append(check("W2 recency-over-topicality is a SMALL slice of reachable misses",
                     frac.get("recency_over_topicality", 0) < 0.2,
                     "recency_over_topicality = %.2f" % frac.get("recency_over_topicality", 0)))
    oks.append(check("W3 FLOOR: the topicality cue is NOT a lever (dev picks the baseline weight; delta ~0)",
                     not t["ci_separated"] and abs(t["delta"]) < 0.005,
                     "dev-best subject weight=%s (baseline %s) delta=%+.4f -> %s"
                     % (t["dev_best_subject_weight"], t["baseline_subject_weight"], t["delta"], t["verdict"])))

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


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
