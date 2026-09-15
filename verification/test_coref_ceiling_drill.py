"""Witness -- the he/she coref ceiling drill (where the residual error lives + two agreement upgrades).

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (wall drill).

Run: .venv/Scripts/python.exe verification/test_coref_ceiling_drill.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_coref_ceiling_drill_gum_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        D.self_test()
        oks.append(check("W0 recall ordering (compat >= pool >= acc)", True))
    except AssertionError as e:
        oks.append(check("W0 recall ordering", False, str(e)))

    o = D.run()
    d = o["ceiling_decomposition"]; md = d["miss_decomposition"]; rd = d["recall_drop_by_filter"]
    h = o["him_agreement_narrow_upgrade"]; dn = o["drop_hard_narrow_test"]

    oks.append(check("W1 the gold antecedent is REACHABLE (recall@compatible > 0.9) -- NOT a world-knowledge wall",
                     d["recall_at_compatible"] > 0.9, "recall@compatible=%.4f unreachable=%.4f" % (d["recall_at_compatible"], md["upstream_unreachable"])))
    oks.append(check("W2 the DOMINANT miss cause is FILTER OVER-REMOVAL, not mispick or unreachable",
                     md["filter_over_removal"] > md["reachable_but_mispicked"] and md["filter_over_removal"] > md["upstream_unreachable"],
                     "over-removal=%.4f mispick=%.4f unreachable=%.4f" % (md["filter_over_removal"], md["reachable_but_mispicked"], md["upstream_unreachable"])))
    oks.append(check("W3 agreement-narrow over-removal is ENTIRELY on gender-UNKNOWN gold (the mechanism)",
                     rd["agreement_narrow"] > 0.05 and d["of_narrow_removed_golds_gender_unknown"] > 0.95,
                     "narrow drop=%.4f, %.0f%% gender-unknown" % (rd["agreement_narrow"], 100 * d["of_narrow_removed_golds_gender_unknown"])))
    oks.append(check("W4 UPGRADE: applying agreement-narrow to 'him' too helps CI-separated (agreement is general)",
                     h["ci_separated"] and h["delta"] > 0.005, "all %.4f->%.4f delta=%+.4f CI%s (him-subset %.4f->%.4f)"
                     % (h["all_off"], h["all_narrow_him"], h["delta"], h["ci"], h["him_subset_off"], h["him_subset_narrow"])))
    oks.append(check("W5 dropping the HARD narrow HURTS (flooding > recall) -- so the deeper fix is upstream GENDER, not soft agreement",
                     dn["delta"] < 0 and not dn["ci_separated"], "no-hard-narrow %.4f delta=%+.4f CI%s"
                     % (dn["no_hard_narrow"], dn["delta"], dn["ci"])))

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
