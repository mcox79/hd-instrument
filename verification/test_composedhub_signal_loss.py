"""Scaffold-free witness for upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub.

Reads the landed metrics.json of this problem's cells and asserts the load-bearing claims. Does NOT
re-run any cell (leaves landed records byte-identical). Run:
    .venv/Scripts/python.exe verification/test_composedhub_signal_loss.py
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    p = os.path.join(REPO, "data", name, "metrics.json")
    assert os.path.exists(p), "MISSING landed metrics: %s" % p
    with open(p, encoding="ascii") as f:
        return json.load(f)


def _sep(d):
    return d["ci_lo"] > 0 if "ci_lo" in d else d["ci"][0] > 0


def main():
    checks = []

    # ---- W1-W5: HELD-OUT signal-loss decomposition (QA-SRL, the mechanism proof) ----
    sl = _load("composedhub_signal_loss_v1")
    assert sl["hub_dim"] == 200 and sl["n_shared_pop"] > 2000, "held-out decomposition scale"
    L = sl["ladder"]; T = sl["twins"]
    assert L["headline_HUBIDEAL_vs_ORGAN"]["ci_lo"] > 0, "W1 hub beats spoke organ CI-sep"
    assert L["headline_HUBIDEAL_vs_ORGAN"]["delta"] > 0.06, "W1 headline >= ~0.076"
    checks.append(("W1 held-out HUB_IDEAL vs ORGAN", L["headline_HUBIDEAL_vs_ORGAN"]["delta"], "CI-SEP"))
    assert L["representational_loss_HUBCENTROID_vs_ORGAN"]["ci_lo"] > 0, "W2 representation is the lever CI-sep"
    checks.append(("W2 representational loss", L["representational_loss_HUBCENTROID_vs_ORGAN"]["delta"], "CI-SEP"))
    assert L["composition_loss_HUBIDEAL_vs_HUBCENTROID_agentcovered"]["ci_lo"] > 0, "W3 composition real (agent-covered)"
    assert L["precision_term_HUBIDEAL_vs_RAW"]["ci_lo"] > 0, "W4 precision earns its place"
    for tw in ("HUBIDEAL_vs_agent_shuffle", "HUBIDEAL_vs_verb_shuffle", "HUBIDEAL_vs_hub_shuffle"):
        assert T[tw]["ci_lo"] > 0, "W5 twin loses CI-sep: %s" % tw
    checks.append(("W5 all 3 held-out twins lose", T["HUBIDEAL_vs_hub_shuffle"]["delta"], "CI-SEP"))

    # ---- W6: POOL-SIZE sweep -- hub beats spoke at EVERY pool size (random distractors) ----
    ps = _load("composedhub_poolsize_sweep_v1")
    for k in ("2", "3", "10"):
        assert ps["sweep"][k]["ci"][0] > 0, "W6 hub beats spoke CI-sep at k=%s" % k
    checks.append(("W6 pool-size sweep hub>spoke at k=2/3/10", ps["sweep"]["3"]["delta"], "CI-SEP"))

    # ---- W7: cross-register GENERALIZATION -- hub transfers both directions ----
    g = _load("composedhub_generalize_v1")["results"]
    for reg in ("QASRL_modern", "LitBank_19c"):
        m = g[reg]["mrr"]
        assert m["HUB_cross"] > m["SPOKE"] * 1.5, "W7 cross-register hub transfer: %s" % reg
    checks.append(("W7 cross-register transfer both directions", None, "PASS"))

    # ---- W8: LIVE reader, BRAIN-FAITHFUL instrument (broad graded pre-activation) -- the live lift ----
    lb = _load("composedhub_livebroad_v1")
    assert lb["hub_dim"] == 200 and lb["n"] > 8000, "W8 live-broad at scale"
    hs = lb["contrasts"]["HUB_vs_SPOKE"]
    assert hs["ci"][0] > 0, "W8 live-broad hub beats spoke CI-sep"
    assert lb["contrasts"]["HUB_vs_hub_shuffle"]["ci"][0] > 0, "W8 live hub-shuffle twin loses CI-sep"
    assert lb["contrasts"]["HUB_vs_agent_shuffle"]["ci"][0] > 0, "W8 live agent-shuffle twin loses CI-sep"
    checks.append(("W8 LIVE (brain-faithful) hub>spoke, BOTH twins lose", hs["delta"], "CI-SEP"))

    # ---- W9: LIVE sentence-noun pool also CI-sep at power; error-flag AUC ns (disclosed secondary) ----
    lt = _load("composedhub_livetyped_v1")
    assert lt["FULL_pool"]["HUB_vs_SPOKE"]["ci"][0] > 0, "W9 live sentence-noun pool hub>spoke CI-sep at power"
    live = _load("composedhub_live_v1")
    hu = live["paired_contrasts"]["AUC__HUB_IDEAL_vs_ORGAN"]
    assert hu["sep"] == "ns", "W9 live error-FLAG AUC ns (disclosed: calibration metric, ambiguity-ceilinged)"
    assert abs(live["auc_by_predictor"]["ORGAN"]["auc"] - 0.65) < 0.03, "W9 ORGAN reproduces deployed organ AUC (no-regression)"
    checks.append(("W9 live sentence-noun pool hub>spoke CI-sep; error-flag ns", lt["FULL_pool"]["HUB_vs_SPOKE"]["delta"], "CI-SEP"))

    # ---- W10: CROSS-TASK deployment -- hub carries sense structure (WiC) ----
    wic = _load("composedhub_sense_readout_v1")
    assert wic["contrasts"]["HUB_vs_SPOKE"]["ci"][0] > 0, "W10 hub beats spoke on WiC sense discrimination CI-sep"
    assert wic["contrasts"]["HUB_vs_hub_shuffle"]["ci"][0] > 0, "W10 WiC shuffled-hub twin loses CI-sep"
    checks.append(("W10 cross-task WiC sense: hub>spoke, twin loses", wic["contrasts"]["HUB_vs_SPOKE"]["delta"], "CI-SEP"))

    # ---- W11: COVERAGE -- Resnik/Clark-Weir taxonomic backoff recovers the OOV tail ----
    rk = _load("composedhub_resnik_coverage_v1")
    assert rk["RESNIK_vs_NAIVE"]["ci"][0] > 0, "W11 Resnik beats naive-hypernym-average CI-sep (Clark-Weir)"
    assert rk["RESNIK_vs_RANDOM"]["ci"][0] > 0, "W11 Resnik beats random CI-sep"
    assert rk["RESNIK_vs_SHUFFLE"]["ci"][0] > 0, "W11 Resnik beats shuffle-class twin CI-sep"
    assert rk["coverage_recovered_frac"] > 0.9, "W11 recovers the OOV tail"
    checks.append(("W11 Resnik coverage backoff (beats naive/random/shuffle)", rk["RESNIK_vs_NAIVE"]["delta"], "CI-SEP"))

    # ---- W12: whole-chain optimization -- 2nd bound argument helps, 3rd+ saturates (bounded-tuple / P1 boundary) ----
    ma = _load("composedhub_multiarg_v1")
    assert ma["ladder"]["arg1_vs_centroid"]["ci"][0] > 0, "W12 agent composition CI-sep"
    assert ma["ladder"]["arg2_vs_arg1_on_2plus_covered"]["ci"][0] > 0, "W12 2nd argument helps (2+-covered) CI-sep"
    assert ma["ladder"]["argN_vs_arg2_3rd_plus"]["sep"] == "ns", "W12 3rd+ argument SATURATES (bounded-tuple ceiling)"
    assert ma["twins"]["HUBNarg_vs_arg_shuffle"]["ci"][0] > 0, "W12 wrong-argument twin loses CI-sep"
    checks.append(("W12 2-arg composition helps, 3rd+ saturates (P1 boundary)", ma["ladder"]["arg2_vs_arg1_on_2plus_covered"]["delta"], "CI-SEP"))

    # ---- W13: the FULL assembled brain-foundational predictor composes (each component earns its keep, twins lose) ----
    idf = _load("composedhub_ideal_full_v1")
    assert idf["ladder"]["R1_representation_HUB_vs_ORGAN"]["ci"][0] > 0, "W13 representation rung CI-sep"
    assert idf["ladder"]["R2_2argComposition_vs_HUB"]["ci"][0] > 0, "W13 composition rung CI-sep"
    assert idf["ladder"]["IDEAL_quality_vs_ORGAN"]["ci"][0] > 0, "W13 IDEAL vs ORGAN CI-sep"
    assert idf["twins"]["IDEAL_vs_arg_shuffle"]["ci"][0] > 0 and idf["twins"]["IDEAL_vs_hub_shuffle"]["ci"][0] > 0, "W13 both twins lose CI-sep"
    assert idf["coverage_extension"]["ideal_scoreable_frac"] > idf["coverage_extension"]["hub_scoreable_frac"], "W13 Resnik extends coverage"
    checks.append(("W13 IDEAL assembly composes (rep+comp CI-sep, twins lose)", idf["ladder"]["IDEAL_quality_vs_ORGAN"]["delta"], "CI-SEP"))

    print("PASS -- %d witness groups:" % len(checks))
    for name, val, verdict in checks:
        print("  %-54s %s  %s" % (name, ("%.4f" % val) if isinstance(val, float) else "-", verdict))
    print("\nHEADLINE (SOLVED): hub+composed-exemplar beats the spoke organ +%.4f held-out (2.4x) AND +%.4f"
          " on the LIVE reader (brain-faithful broad pre-activation, n=%d), all info-free twins losing;"
          " transfers to sense discrimination (WiC) + recovers the OOV coverage tail (Resnik)."
          % (L["headline_HUBIDEAL_vs_ORGAN"]["delta"], hs["delta"], lb["n"]))


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
