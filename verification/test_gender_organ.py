"""Witness -- the glass-box GENDER organ (leak-removal + the sparsity cap + propagation negative).

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (upstream organ).

Run: .venv/Scripts/python.exe verification/test_gender_organ.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_gender_organ_gum_v1 as GO


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        GO.self_test()
        oks.append(check("W0 organ spot-checks (Elizabeth->fem, businessman->masc, 'his mother'->fem, table->None)", True))
    except AssertionError as e:
        oks.append(check("W0 organ spot-checks", False, str(e)))

    o = GO.run()
    og = o["organ_glassbox_no_gold"]; go = o["gold_plus_organ"]; r = o["random_gender_control"]
    p = o["propagation"]; c = o["gender_coverage"]

    oks.append(check("W1 the glass-box organ MATCHES/BEATS the gold-Gender leak (no gold at inference)",
                     og["matches_or_beats_gold"] and og["delta_vs_gold"] >= -0.005,
                     "gold=%.4f organ=%.4f delta=%+.4f CI%s" % (o["gold_baseline_acc"], og["acc"], og["delta_vs_gold"], og["ci"])))
    oks.append(check("W2 where organ and gold both fire they AGREE ~100%%, and organ coverage >= gold",
                     c["agreement_where_both"] > 0.95 and c["organ_covers"] >= c["gold_covers"] - 0.001,
                     "agree=%.1f%% organ-cov=%.1f%% gold-cov=%.1f%% (n_both=%d)"
                     % (100 * c["agreement_where_both"], 100 * c["organ_covers"], 100 * c["gold_covers"], c["n_both"])))
    oks.append(check("W3 info-free RANDOM-gender control CRASHES (proves it is the RIGHT gender)",
                     not r["helps"] and r["delta_vs_gold"] < -0.05,
                     "random=%.4f delta=%+.4f" % (r["acc"], r["delta_vs_gold"])))
    oks.append(check("W4 CAP: gender is SPARSE on modern nominals (organ+gold both gender < 10%% of them)",
                     c["organ_covers"] < 0.10 and c["gold_covers"] < 0.10,
                     "organ genders %.1f%% / gold %.1f%% of nominals -> most are genuinely genderless" % (100 * c["organ_covers"], 100 * c["gold_covers"])))
    oks.append(check("W5 LOCATED NEGATIVE: confidence-gated coreferent gender propagation does NOT help (even gated)",
                     not p["ci_separated"] and p["delta_vs_organ"] <= 0.005,
                     "dev-best margin=%s organ+prop delta=%+.4f CI%s" % (p["dev_best_margin"], p["delta_vs_organ"], p["ci"])))

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
