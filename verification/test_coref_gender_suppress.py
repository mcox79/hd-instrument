"""Witness -- the cumulative brain-foundational coref upgrade ladder + gender/suppress drills.

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (deepening).

Run: .venv/Scripts/python.exe verification/test_coref_gender_suppress.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_coref_gender_suppress_gum_v1 as X


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        X.self_test()
        oks.append(check("W0 base stack self-test", True))
    except AssertionError as e:
        oks.append(check("W0 base stack self-test", False, str(e)))

    o = X.run()
    L = o["upgrade_ladder"]; g = o["gender_inference_glass"]; r = o["gender_inference_random_control"]
    st = o["soften_suppress_struct_off"]; a = o["generic_suppress_attribution"]

    oks.append(check("W1 FULL STACK beats the LIVE incumbent CI-separated (cumulative brain-foundational gain)",
                     L["full_vs_incumbent_ci_sep"] and L["full_vs_incumbent_delta"] > 0.05,
                     "incumbent=%.4f -> full=%.4f delta=%+.4f CI%s"
                     % (L["live_incumbent"], L["plus_soften_suppress_FULL"], L["full_vs_incumbent_delta"], L["full_vs_incumbent_ci"])))
    oks.append(check("W2 UPGRADE: soften generic-suppress (drop never-subject STRUCT proxy) beats the base CI-separated",
                     st["ci_separated"] and st["delta"] > 0.01,
                     "base=%.4f -> soften=%.4f delta=%+.4f CI%s" % (o["base_stack_acc"], st["acc"], st["delta"], st["ci"])))
    oks.append(check("W3 FIDELITY: generic-suppress over-removes REAL common nouns (not quantifier junk) on modern gold",
                     a["common_frac"] > 0.8 and a["n_suppress_removed_gold"] > 20,
                     "%d removed: %d common / %d quantifier (%.0f%% common)"
                     % (a["n_suppress_removed_gold"], a["plain_common_noun"], a["quantifier"], 100 * a["common_frac"])))
    oks.append(check("W4 gender inference is DIRECTIONALLY right (recovers recall; info-free random-gender control HURTS)",
                     g["reach_final_glass"] > g["reach_final_base"] and not r["helps"] and r["delta"] < 0,
                     "recall %.4f->%.4f | random-gender delta=%+.4f (helps=%s)"
                     % (g["reach_final_base"], g["reach_final_glass"], r["delta"], r["helps"])))
    oks.append(check("W5 HONEST: title/kinship gender inference is a PARTIAL lever (not CI-separated on accuracy)",
                     not g["ci_separated"],
                     "gender-infer delta=%+.4f CI%s -- recovers recall but does not convert (needs a richer gender organ)"
                     % (g["delta"], g["ci"])))

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
