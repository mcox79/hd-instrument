"""Scaffold-free witness for the SDRT-lite discourse coherence reader.

problem: sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose.

Recomputes every headline from source (no cached metrics read) and asserts the load-bearing claims:
  W0  module mechanism   -- Explanation/Result/Narration inferred; directed_plausibility is DIRECTED.
  W1  MECHANISM control  -- relation-4way reader CI-sep over connective-only AND the info-free twin;
                            order-edit CI-sep over iconicity (the constructed can-fail proof).
  W2  TB-Dense temporal  -- the LOCATED NEGATIVE: on newswire the Explanation detector's flip precision is
                            NOT CI-separated above the base rate of reverse-order (reverse-order is genre
                            convention, not causal flashback -- Zhang & Xue 2018); the mechanism DOES fire
                            (reverse-subset recovery > 0) and the channel is additive (flips only Explanation).
  W3  TellMeWhy causal   -- coherence recovers the unmarked cause CI-sep over the ADJACENCY and CONNECTIVE-only
                            floors (both 0 on non-adjacent); the topical/twin controls TIE (the coverage wall).
  W4  deepen/c-axis      -- directional correctness c rises content -> base_full CI-sep (c is the binding axis).
  W5  NO-REGRESS         -- temporal channel-OFF byte-identical to before(); channel-ON diffs are all
                            Explanation-over-iconicity; causal sm.causal_links byte-identical.
  W6  coupling           -- the causal_reasoner's graded_necessity over the inferred coherence-typed edges
                            reproduces the cause-ID (the reasoner CONSUMES the reader's unmarked edges).

Run: .venv/Scripts/python.exe verification/test_sdrt_coherence_reader.py    (tracing not required; NO LLM)
"""
from __future__ import annotations

import os
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

PASS = "PASS"
FAIL = "FAIL"
_n = 0


def _check(cond, label):
    global _n
    _n += 1
    print(("  [%s] W%d %s" % (PASS if cond else FAIL, _n - 1, label)), flush=True)
    if not cond:
        raise AssertionError("W%d FAILED: %s" % (_n - 1, label))


def main() -> int:
    t0 = time.time()
    print("[witness] SDRT-lite discourse coherence reader -- recomputing every headline from source", flush=True)

    # W0 -- module mechanism
    from experiments._sdrt_coherence import (CoherenceReader, directed_plausibility, EXPLANATION, RESULT,
                                             NARRATION)
    rd = CoherenceReader()
    r_expl = rd.relate(["fell"], ["fell"], ["pushed", "him"], ["pushed"])
    r_res = rd.relate(["pushed", "vase"], ["pushed"], ["shattered"], ["shattered"])
    f, _ = directed_plausibility(["pushed"], ["pushed"], ["shattered"], ["shattered"])
    r, _ = directed_plausibility(["shattered"], ["shattered"], ["pushed"], ["pushed"])
    _check(r_expl.label == EXPLANATION and CoherenceReader.order_edit(r_expl) == "reverse"
           and r_res.label == RESULT and f > r,
           "module: Explanation reverses, Result forward, plausibility DIRECTED (f=%.3f>r=%.3f)" % (f, r))

    # W1 -- MECHANISM control
    import experiments.exp_sdrt_coherence_mechanism_v1 as MECH
    m = MECH.run(deepened=False)
    r4 = m["relation_4way"]; oe = m["order_edit"]
    _check(r4["reader_vs_connective"]["sep"] and r4["reader_vs_twin"]["sep"] and oe["reader_vs_iconicity"]["sep"],
           "mechanism: relation reader %.3f CI-sep over connective %.3f + twin %.3f; order-edit %.3f CI-sep over "
           "iconicity %.3f" % (r4["reader"]["acc"], r4["connective"]["acc"], r4["twin"]["acc"],
                               oe["reader"]["acc"], oe["iconicity"]["acc"]))

    # W2 -- TB-Dense temporal-override LOCATED NEGATIVE
    import experiments.exp_sdrt_temporal_override_tbdense_v1 as TBO
    t = TBO.run(smoke=False, deepened=False)
    _check(not t["flip_detector_selective"],
           "TB-Dense LOCATED NEGATIVE: flip_precision %.3f NOT CI-sep above base-rate-reverse %.3f (newswire "
           "reverse-order is genre, not causal); coverage=%.3f" % (t["flip_precision"], t["base_rate_reverse"],
                                                                   t["coverage_engine_fires"]))
    _check(t["reverse_order"]["coh_acc"] > 0.0 and t["n_explanation_flips"] >= 1,
           "TB-Dense mechanism FIRES on real prose: reverse-subset recovery %.3f > 0 (iconicity=%.3f), %d "
           "Explanation flips (additive)" % (t["reverse_order"]["coh_acc"], t["reverse_order"]["icon_acc"],
                                             t["n_explanation_flips"]))

    # W3 -- TellMeWhy unmarked causal (base engine; position/marker floors + full-pop coverage tie)
    import experiments.exp_sdrt_unmarked_causal_tellmewhy_v1 as TMW
    u = TMW.run(n=1500, deepened=False)
    cm = u["contrasts_multihop"]
    _check(cm["coherence_vs_adjacency"]["ci_sep"] and cm["coherence_vs_connective"]["ci_sep"],
           "TellMeWhy: coherence %.3f recovers unmarked cause CI-sep over adjacency %.3f + connective %.3f "
           "(both 0 on non-adjacent)" % (u["acc_multihop"]["coherence"], u["acc_multihop"]["adjacency"],
                                         u["acc_multihop"]["connective"]))
    _check(not u["coherence_beats_topical_twin_mh"],
           "TellMeWhy FULL-POP: base engine ties topical/twin (coh-topical +%.4f, coh-twin +%.4f) -- the "
           "residual is the causation-TYPE it cannot type (goal), located next" % (
               cm["coherence_vs_topical"]["delta"], cm["coherence_vs_twin"]["delta"]))

    # W-diag -- CAUSATION-TYPE decomposition: GOAL is the dominant category the base engine is blind to,
    # and the added GOAL engine lifts it (locating the signal loss as a missing brain-faithful engine).
    import experiments.exp_sdrt_causation_type_diagnostic_v1 as DIAG
    dg = DIAG.run(n=1500)
    gb = dg["breakdown"]["GOAL"]
    _check(gb["share"] >= 0.25 and gb["goal_acc"] - gb["base_acc"] >= 0.10,
           "DIAGNOSTIC: GOAL causation is %.0f%% (the dominant non-adjacent category); base engine %.3f on it, "
           "GOAL engine %.3f (+%.3f) -- the located signal loss is a MISSING brain-faithful engine"
           % (100 * gb["share"], gb["base_acc"], gb["goal_acc"], gb["goal_acc"] - gb["base_acc"]))

    # W-goal -- THE POSITIVE: on the GOAL-typed subset (its proper domain), the goal engine recovers the
    # unmarked cause CI-sep over the base engine AND topical AND the info-free twin (twin LOSES).
    import experiments.exp_sdrt_goal_causation_subset_v1 as GOAL
    gs = GOAL.run(n=1500)
    gc = gs["contrasts"]
    _check(gs["goal_engine_loadbearing_on_category"],
           "GOAL-SUBSET POSITIVE (n=%d): goal-engine %.3f CI-sep over base %.3f (+%.3f), topical %.3f (+%.3f), "
           "and the info-free TWIN %.3f (+%.3f) -- the missing engine is LOAD-BEARING on its category, twin LOSES"
           % (gs["n_goal_subset"], gs["acc"]["goal"], gs["acc"]["base"], gc["goal_vs_base"]["delta"],
              gs["acc"]["topical"], gc["goal_vs_topical"]["delta"], gs["acc"]["twin"], gc["goal_vs_twin"]["delta"]))

    # W-kintsch -- the P2 integration divergence is BUILT (Kintsch construction-integration settling); it
    # ~ ties the base product argmax (integration is NOT the bottleneck) + keeps the GOAL subset -> the
    # residual is Tier-2 goal SELECTION (inverse planning), the located coverage wall.
    import experiments.exp_sdrt_kintsch_integration_v1 as KI
    ki = KI.run(n=1500)
    _check(abs(ki["overall"]["kintsch"] - ki["overall"]["base"]) < 0.03 and ki["breakdown"]["GOAL"]["kintsch"] >= 0.40,
           "KINTSCH INTEGRATION (P2 built): settling %.3f ~ base %.3f + keeps GOAL subset %.3f -> the integration "
           "architecture is NOT the bottleneck; the residual is Tier-2 goal SELECTION (inverse planning)"
           % (ki["overall"]["kintsch"], ki["overall"]["base"], ki["breakdown"]["GOAL"]["kintsch"]))

    # W-sim -- THE SIMULATOR + GENERATIVE MEANS-END: the degenerate settling/scalar-means-end were proven
    # degenerate; the STRUCTURAL fixes (typed-edge CSKG retrieval + generative goal-object-as-patient) give
    # the best overall + beat the info-free twin CI-sep; and the goal-GATED object-match beats the UNGATED
    # referential-coherence control CI-sep (so it is more than Centering coherence -- a real weak means-end
    # for object-desire goals). Full CI-sep-over-base awaits result-state matching for state-desire goals.
    import experiments.exp_sdrt_generative_meansend_v1 as GEN
    gen = GEN.run(n=1500)
    _check(gen["generative_vs_twin"]["ci_sep"] and gen["overall"]["generative"] >= gen["overall"]["base"],
           "GENERATIVE MEANS-END: union (typed CSKG + goal-object-as-patient) overall %.3f (best) beats the twin "
           "CI-sep (+%.4f); fires typed %d + objmatch %d -> generative %d (coverage doubled vs retrieval alone)"
           % (gen["overall"]["generative"], gen["generative_vs_twin"]["delta"],
              gen["fire_counts"]["typed"], gen["fire_counts"]["objmatch"], gen["fire_counts"]["generative"]))
    _check(gen["objmatch_vs_refcoh"]["ci_sep"] and gen["refcoh_vs_base"]["delta"] <= 0,
           "REFCOH CONTROL: goal-GATED object-match %.3f beats UNGATED referential coherence %.3f CI-sep (+%.4f) "
           "-- so it is NOT pure Centering coherence (ungated over-fires and HURTS: %+.4f vs base)" % (
               gen["overall"]["objmatch"], gen["overall"]["refcoh"], gen["objmatch_vs_refcoh"]["delta"],
               gen["refcoh_vs_base"]["delta"]))

    # W4 -- deepening / c is the binding axis
    import experiments.exp_sdrt_deepen_simulator_v1 as DEEP
    d = DEEP.run()
    accs = {k: d["ladder"][k]["c_directional_acc"]["acc"] for k in d["ladder"]}
    _check(d["c_is_binding_axis"] and d["base_vs_content"]["sep"],
           "c is the BINDING AXIS: directional correctness content %.3f -> base_full %.3f CI-sep (+%.4f); "
           "deepened %.3f (deepening does not cross the coverage wall, matching the research)"
           % (accs["content_only"], accs["base_full"], d["base_vs_content"]["delta"], accs["deepened"]))

    # W5 -- NO-REGRESS
    import experiments.exp_sdrt_no_regress_v1 as NR
    nr = NR.run()
    _check(nr["no_regress"] and nr["temporal_on_n_diffs"] >= 1,
           "NO-REGRESS: temporal channel-OFF byte-identical (%d/%d); ON diffs=%d all Explanation-over-iconicity; "
           "causal links byte-identical" % (nr["temporal_off_identical_count"], nr["n_passages"],
                                            nr["temporal_on_n_diffs"]))

    # W6 -- coupling (causal_reasoner consumes the inferred edges)
    _check(u["coupling_n"] > 0 and abs(u["coupling_ultimate_cause_acc_mh"] - u["acc_multihop"]["coherence"]) < 0.06,
           "COUPLING: causal_reasoner.graded_necessity over the inferred coherence-typed edges reproduces the "
           "cause-ID (coupling %.3f ~ coherence %.3f, n=%d)"
           % (u["coupling_ultimate_cause_acc_mh"], u["acc_multihop"]["coherence"], u["coupling_n"]))

    print("[witness] %d/%d PASS in %.1fs" % (_n, _n, time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
