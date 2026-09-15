"""Scaffold-free witness for who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde.

Runs the cell end-to-end (reads the who-did-what cache; no spaCy; ~15-35s) and asserts the located
negative's load-bearing, can-fail claims:

  W1  self-test (graded net + entropy; event-state channel fires + abstains; Bayesian-product fusion flips;
      positive control fires) passes.
  W2  the PREMISE reproduces FAITHFULLY via the parent harness (hdlab.coref loader): on the NOCHAIN-defined
      structurally-dominated bucket, the CHAIN arm's accuracy is ~0.48 (the brief's 0.481), ~0.29 of errors are
      structurally-dominated, and ~0.99 of wrong picks are confident (the entropy null). (Contradicts nothing;
      confirms the located residual is real, exactly as the brief states.)
  W3  the coherence next-mention PRIOR is DEAD on the composed (entity-maintenance) held-out bucket: its
      combined ORACLE ceiling is near-chance (<0.15 when it fires) AND, fused as a Bayesian product with the
      weight tuned on DEV for its best shot, it does NOT beat its own 20-shuffle INFO-FREE TWIN
      (prior-minus-twin band is NOT ABOVE). This reproduces the owner-DONE 2026-08-29 negative post-composition.
  W4  the DEEPER situation-model lever the prior negative named but never built -- a specific-discourse
      EVENT-STATE next-mention channel -- is ALSO near-chance on the bucket (oracle <0.20 when it fires), while
      the POSITIVE CONTROL confirms the coherence mechanism CAN move the metric on constructed pairs
      (selectional 8/8, implicit-causality 8/8; info-free twins at chance). => the mechanism works; the
      structurally-dominated bucket simply lacks the cases (the anti-typical Winograd core).

Deterministic. Reads data/litbank/who_did_what_events.json + the parent's LitBank CoNLL. ASCII only.
"""
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_coref_coherence_prior_on_chain_bucket_v1 as C


def main():
    checks = []

    # W1 -- unit invariants
    try:
        C.self_test()
        checks.append(("W1 self-test (net/entropy; event channel; fusion flips; positive control)", True, "unit checks pass"))
    except Exception as e:  # noqa
        checks.append(("W1 self-test", False, "raised %r" % e))
        return _report(checks)

    # end-to-end run (all 100 cache docs; parent-harness premise uses its 25 LitBank docs)
    out = C.cell(docs=None, n_boot=1000, seed=20260902)

    # W2 -- the premise reproduces faithfully via the parent harness (the brief's 0.481 / 0.294 / 0.995)
    pp = out["premise_reproduction_parent_harness"]
    w2 = (pp.get("acc_struct_dominated") is not None
          and 0.40 <= pp["acc_struct_dominated"] <= 0.56
          and 0.24 <= pp["frac_errors_struct_dominated"] <= 0.40
          and pp["frac_wrong_low_entropy"] >= 0.95
          and 380 <= pp["n_struct_dominated"] <= 520)
    checks.append(("W2 premise reproduces (parent harness): acc_dom~0.48, frac_err~0.29, confident~0.99", bool(w2),
                   "acc_dom=%s frac_err_dom=%s confident=%s n_dom=%s"
                   % (pp.get("acc_struct_dominated"), pp.get("frac_errors_struct_dominated"),
                      pp.get("frac_wrong_low_entropy"), pp.get("n_struct_dominated"))))

    # W3 -- the coherence prior is DEAD on the composed held-out bucket (oracle near-chance AND prior<=twin)
    orc = out["ORACLE_ceilings_on_TEST_bucket"]["combined"]["acc_when_applicable"] or 0.0
    twin_band = out["prior_minus_infofree_twin_paired"]["band"]
    w3 = (orc < 0.15) and (twin_band != "ABOVE")
    checks.append(("W3 coherence prior dead on chain bucket (oracle<0.15 AND prior does NOT beat info-free twin)", bool(w3),
                   "combined_oracle=%.4f prior_minus_twin=%s(%s) n_bucket=%d"
                   % (orc, out["prior_minus_infofree_twin_paired"]["delta"], twin_band, out["n_test_bucket"])))

    # W4 -- the deeper event-state situation-model lever is ALSO near-chance; positive control fires
    ev = out["ORACLE_ceilings_on_TEST_bucket"]["event_state"]["acc_when_applicable"] or 0.0
    pc = out["positive_control"]
    w4 = (ev < 0.20) and pc["selectional_prior_correct"] >= 7 and pc["ic_prior_correct"] == pc["ic_pairs"]
    checks.append(("W4 event-state lever near-chance (<0.20) AND positive control fires (mechanism works)", bool(w4),
                   "event_state_oracle=%.4f selectional=%d/8 ic=%d/8 verdict=%s"
                   % (ev, pc["selectional_prior_correct"], pc["ic_prior_correct"], out["verdict"])))

    # W5 -- WALL LOCALIZATION (gold-coref past-only ceiling, CLEAN person pool, MATCHED vs global topicality).
    # The load-bearing recoverable signal is GLOBAL TOPICALITY (captured by the chain); AND on genuine
    # person-vs-person cases a RICHER in-text representation BEATS topicality CI-separated (a buildable
    # situation-model lever) -- but bounded by a modest ceiling, the rest external world-knowledge. Can-fail:
    # FAILS if the pool-cleaning/matched comparison did not run or no in-text channel is CI-separated above.
    wl = out["wall_localization"]
    smp = out["situation_model_ceiling_PERSON_POOL"]
    freq_person = smp["frequency_control_oracle"]["acc_when_applicable"] or 0.0
    mp = smp["MATCHED_vs_frequency"]
    lever = bool(wl["in_text_semantic_lever_exists"]) and len(wl["channels_beating_topicality_CIsep"]) >= 1
    w5 = (freq_person > 0.40) and lever
    checks.append(("W5 wall localized: topicality load-bearing (captured) AND a richer in-text rep beats it CI-sep on the clean person pool (buildable lever)", bool(w5),
                   "person-pool frequency=%.3f | channels>topicality=%s | exact +%.3f%s context +%.3f%s"
                   % (freq_person, wl["channels_beating_topicality_CIsep"],
                      mp["exact_predicate"].get("delta", 0), mp["exact_predicate"].get("band", "-"),
                      mp["context_bow"].get("delta", 0), mp["context_bow"].get("band", "-"))))

    # W6 -- REALIZED lever (constructive redirect made live): the CORRECT mechanism (accumulated-entity content
    # channel = wiring the EXISTING animacy filter + situation-model accumulate) yields a marginal CI-separated
    # gain on the real animacy-filtered deployment, shuffled twin losing, no harm; AND it is NULL on the
    # animacy-polluted full pool (the animacy organ is a required gate). Can-fail: FAILS if no realized gain, or
    # if the twin is not beaten, or if the full pool is not null.
    rp = out["REALIZED_entity_lever_person_pool"]
    rf = out["REALIZED_entity_lever_full_pool"]
    dec = rp["channel_decomposition"]
    best_band = max((dec[k]["arm_minus_floor"] for k in ("content", "combined")), key=lambda a: a["delta"])
    realized_ok = (best_band["band"] == "ABOVE" and rp["arm_beats_twin"]
                   and rp["no_harm_non_dominated"]["delta"] >= -0.005
                   and rf["arm_minus_floor"]["band"] != "ABOVE")   # polluted pool shows NO positive gain (animacy is a required gate)
    checks.append(("W6 realized lever (existing organs): CORRECT mechanism gives a CI-sep gain on the animacy-filtered pool, twin loses, no harm; null on polluted pool", bool(realized_ok),
                   "person multi +%.4f %s (content +%.4f %s) twin %.4f beats=%s no-harm %.4f | full-pool delta %.4f"
                   % (dec["multi"]["arm_minus_floor"]["delta"], dec["multi"]["arm_minus_floor"]["band"],
                      dec["content"]["arm_minus_floor"]["delta"], dec["content"]["arm_minus_floor"]["band"],
                      rp["twin_mean_delta"], rp["arm_beats_twin"], rp["no_harm_non_dominated"]["delta"],
                      rf["arm_minus_floor"]["delta"])))

    # W7 -- THE WALL IS INTEGRATION, NOT MISSING INFO: the per-item COMBINED in-text oracle ceiling is far above
    # topicality (=> the discriminating info IS in the text; the wall is the nonlinear per-item GATE we lack).
    # Can-fail: FAILS if the combined ceiling ~= topicality (which would mean the in-text info is exhausted).
    cc = out["situation_model_ceiling_PERSON_POOL"]["COMBINED_in_text_ceiling"]
    comb = cc["combined_any_incl_topicality"] or 0.0
    topi = cc["topicality_alone"] or 0.0
    w7 = comb >= 0.75 and (comb - topi) >= 0.15
    checks.append(("W7 wall is INTEGRATION not missing-info: combined in-text oracle ceiling >> topicality (info IS in the text)", bool(w7),
                   "combined_ceiling=%.4f semantic_only=%.4f topicality=%.4f (gap +%.3f)"
                   % (comb, cc["combined_any_semantic_only"] or 0.0, topi, comb - topi)))

    # W8 -- THE IDEAL SOLUTION prototyped: a LEARNED glass-box cue-integrator beats the floor CI-separated on the
    # held-out person pool, shuffled-cue twin loses, and it beats the linear fusion (realizes more of the
    # integration lever). Can-fail: FAILS if the learned integrator is not CI-sep above the floor or the twin wins.
    il = out["IDEAL_learned_cue_integrator"]
    lmf = il["learned_minus_floor"]
    w8 = (lmf["band"] == "ABOVE" and il["beats_twin"] and lmf["delta"] >= il["linear_reference_delta"] - 0.005)
    checks.append(("W8 IDEAL learned cue-integrator: CI-sep gain over floor, twin loses, >= linear fusion (the buildable full-solution piece)", bool(w8),
                   "floor=%.4f -> learned=%.4f delta=%+.4f %s (linear ref +%.4f) twin_delta=%+.4f beats_twin=%s"
                   % (il["floor_acc"], il["learned_acc"], lmf["delta"], lmf["band"],
                      il["linear_reference_delta"], il["shuffled_cue_twin_minus_floor"]["delta"], il["beats_twin"])))

    return _report(checks)


def _report(checks):
    npass = sum(1 for _, ok, _ in checks if ok)
    print("\n==== WITNESS: %d/%d ====" % (npass, len(checks)))
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
