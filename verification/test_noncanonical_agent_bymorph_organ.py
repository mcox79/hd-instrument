"""Scaffold-free witness for grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads.

Recomputes the headline from source (experiments.exp_noncanonical_agent_bymorph_v1.run, FULL) and asserts:

W1  THE FIX: the by-phrase CASE-MORPHOLOGY cue (byhead) beats the LIVE agent competition on the CLEAN
    non-canonical slice (gold agent post-verbal, positional necessarily wrong) CI-separated.
W2  info-free twin (by-membership shuffled across candidates) LOSES CI-separated -> the STRUCTURAL by-signal is
    real, not "boost any candidate".
W3  NO canonical regress (the cue is gated to the passive-agent construction; canonical is left essentially
    byte-identical).
W4  LOCATED NEGATIVE: the WHITENED grounded selectional-fit cue TIES its info-free scrambled-meaning twin on
    non-canonical -> grounded meaning does NOT carry non-canonical role over structure+animacy (the brief's
    named mechanism is a full-PASS located negative).
W5  UPSTREAM: the participle+by-PP CONSTRUCTION gate is higher-PRECISION than is_passive_clause (far fewer
    canonical false-fires) while covering >= as many real passives -> the brain-foundational voice cue.

Run: .venv/Scripts/python.exe verification/test_noncanonical_agent_bymorph_organ.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_noncanonical_agent_bymorph_v1 as M


def main():
    print("witness: by-morphology cue fixes non-canonical who-did-what AGENT; grounded meaning is a located negative")
    m = M.run(smoke=False)
    ap = m["clean_agent_post"]; nc = m["byhead_fix"]["non_canonical_ALL"]
    cr = m["canonical_noregress"]; gn = m["grounded_selfit_negative"]; gc = m["upstream_gate_comparison"]

    print("  CLEAN non-canonical (agent post-verbal) n=%d: positional %.4f  baseline %.4f  +byhead %.4f"
          % (ap["n"], ap["positional"], ap["baseline"], ap["byhead"]))
    print("    byhead vs baseline %s" % ap["byhead_vs_baseline"])
    assert ap["byhead_vs_baseline"]["sep"], "W1 FAIL: byhead does not CI-beat the live baseline on the clean slice"
    assert ap["byhead"] > ap["baseline"] + 0.20, "W1 FAIL: byhead lift on the clean slice is implausibly small"
    print("  W1 PASS: byhead beats the live agent competition CI-sep on the clean non-canonical slice")

    print("    byhead vs info-free twin %s (twin acc %.4f)" % (ap["byhead_vs_twin"], ap["byhead_twin"]))
    assert ap["byhead_vs_twin"]["sep"], "W2 FAIL: byhead does not CI-beat its shuffled-by-membership twin"
    print("  W2 PASS: the info-free (shuffled by-membership) twin LOSES CI-sep -> the structural signal is real")

    print("  canonical no-regress n=%d: baseline %.4f byhead %.4f  vs_base %s"
          % (cr["n"], cr["baseline"], cr["byhead"], cr["byhead_vs_baseline"]))
    assert cr["byhead_vs_baseline"]["hi"] >= -0.005, "W3 FAIL: byhead CI-regresses canonical"
    print("  W3 PASS: no canonical regression (self-gated to the passive-agent construction)")

    print("  LOCATED NEGATIVE: selfit %.4f vs scrambled-meaning twin %.4f  %s"
          % (gn["selfit"], gn["twin_scrambled_meaning"], gn["selfit_vs_twin_scrambled"]))
    assert not gn["selfit_vs_twin_scrambled"]["sep"], "W4 FAIL: grounded selfit unexpectedly CI-beats its twin"
    print("  W4 PASS: whitened grounded selfit TIES its info-free twin -> grounded meaning is a located negative")

    pb = gc["participle_byPP"]; isp = gc["is_passive_clause"]
    print("  UPSTREAM gate: participle+byPP falsefire=%d vs is_passive falsefire=%d (canonical); agent-post %.4f vs %.4f"
          % (pb["fire_canonical_falsefire"], isp["fire_canonical_falsefire"], pb["agent_post_acc"], isp["agent_post_acc"]))
    assert pb["fire_canonical_falsefire"] < isp["fire_canonical_falsefire"], "W5 FAIL: construction gate not higher-precision"
    assert pb["agent_post_vs_baseline"]["sep"], "W5 FAIL: construction-gated byhead does not CI-beat baseline"
    print("  W5 PASS: the participle+by-PP construction gate is higher-precision than is_passive_clause")

    print("ALL CHECKS PASS (5/5)")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
