#!/usr/bin/env python3
"""Scaffold-free witness for wire_the_context_gated_sense_read_into_the_live_meaning_path_and_measure.

Reproduces the two headlines with their controls, on the FULL modern populations (no cell scaffolding):
  POSITIVE  the LIVE WIRE (hdlab.underspecified_sense_reader.select_sense, what sm.select_sense binds) lifts WiC over
            the SENSE-BLIND reader (majority) CI-separated, with the info-free shuffled-context twin LOSING.
  NEGATIVE  the ONE live downstream sense-consuming decision (common-noun coref type-license) does NOT profit: the
            context-gating flip ceiling is small, the info-free twin flips AS MANY OR MORE (does not lose), and the
            controlled coref accuracy delta gated-minus-baseline has a CI that INCLUDES ZERO.
  LIVENESS  a real SituationReader.read() leaves sm.senses == [] (dormant), yet sm.select_sense fires when invoked.

Run: .venv/Scripts/python.exe verification/test_sense_wire_liveness_and_coref_negative.py
"""
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_sense_wire_wic_liveness_v1 as WIC
import experiments.exp_sense_gated_coref_divergence_v1 as DIV
import experiments.exp_sense_gated_natural_logic_probe_v1 as NLP
import experiments.exp_sense_gated_safe_bridge_write_v1 as BW
import experiments.exp_context_modulated_meaning_vector_probe_v1 as VEC
import experiments.exp_sense_wire_wic_param_sweep_v1 as SW
import experiments.exp_sense_gated_coref_board_native_v1 as BN
import experiments.exp_sense_wire_wic_grain_sweep_v1 as GR


def main():
    # ---- POSITIVE: live wire lifts WiC over sense-blind majority, twin loses ----
    w = WIC.run(smoke=False)["result"]
    wire = w["arms"]["WIRE_coarse"]["acc"]; maj = w["arms"]["FLOOR_majority"]["acc"]
    d_maj = w["WIRE_coarse_minus_majority"]; d_tw = w["WIRE_coarse_minus_twin"]
    assert wire > maj, "WIRE_coarse %.4f must beat sense-blind majority %.4f" % (wire, maj)
    assert d_maj["sep"], "WIRE-majority CI must separate (%s)" % d_maj
    assert d_tw["sep"], "info-free shuffled-context twin must LOSE (WIRE-twin %s)" % d_tw
    assert wire >= 0.70, "WIRE_coarse expected ~0.75 (got %.4f)" % wire

    # ---- LIVENESS + NEGATIVE: divergence gate ----
    g = DIV.run(smoke=False)
    a = g["part_A_liveness"]; c = g["part_C_flip_ceiling"]; d = g["part_D_coref_accuracy_delta"]
    assert a["sm_senses_empty_after_read"], "sm.senses must be [] after a real read (dormant premise)"
    assert a["select_sense_returns_when_invoked"], "sm.select_sense must fire when invoked"
    # the wire is ACTIVE (context diverges from MFS) but the coref consumer cannot profit:
    assert g["part_B_divergence"]["coarse_diverges_from_MFS_rate"] > 0.20, "context should diverge from MFS materially"
    assert c["flip_rate_over_pairs"] < 0.05, "type-license flip ceiling must be small (%s)" % c["flip_rate_over_pairs"]
    assert c["flips_twin_shuffled_context"] >= c["flips_total"], \
        "info-free twin must NOT lose (flips_twin %d >= flips_total %d)" % (
            c["flips_twin_shuffled_context"], c["flips_total"])
    lo = d["gated_minus_baseline"][1]; hi = d["gated_minus_baseline"][2]
    assert lo <= 0 <= hi, "coref gated-minus-baseline CI must INCLUDE zero (located negative): %s" % (
        d["gated_minus_baseline"],)
    # WiC positive is genuine discrimination, not a coarse-over-predicts-same artifact
    conf = w["sanity_confusion"]
    assert conf["specificity_accuracy_on_DIFFERENT_pairs"] > 0.6, \
        "WiC lift must hold on the hard gold-DIFFERENT pairs (specificity %s)" % conf

    # ---- NEGATIVE (2nd consumer): the DECISIVE natural-logic is-a is HURT (not helped) by context-gating ----
    nl = NLP.run(smoke=False)["result"]
    dgb = nl["GATED_minus_BASELINE"]
    assert not dgb["sep"], "context-gating the natural-logic is-a must NOT beat the union baseline CI-sep (%s)" % dgb
    assert dgb["delta"] <= 0, "context-gating the DECISIVE natural-logic is-a should not help (delta %s)" % dgb["delta"]

    # ---- OPPORTUNITY #1 safe bridge-writing: gated is SAFER than blind (precision CI-sep) but the safety is
    #      RESTRICTIVENESS not context (twin matches) and writing is NOT recovered (does not beat non-writing) ----
    bw = BW.run(smoke=False)["result"]
    assert bw["gated_minus_blind_P"]["sep"], "context-gated write must beat sense-blind on precision CI-sep (%s)" % (
        bw["gated_minus_blind_P"],)
    assert bw["gated_minus_nobridge_F"]["delta"] <= 0 or not bw["gated_minus_nobridge_F"]["sep"], \
        "writing should NOT be recovered (gated must not beat non-writing CI-sep): %s" % bw["gated_minus_nobridge_F"]
    assert not bw["gated_minus_twin_F"]["sep"], \
        "the safety gain must be RESTRICTIVENESS not context (twin should match gated on F): %s" % bw["gated_minus_twin_F"]

    # ---- OPPORTUNITY #3 context-modulated meaning VECTOR: carries context-driven sense signal (twin loses) ----
    vec = VEC.run(smoke=False)["result"]
    assert vec["GRADED_VECTOR_auc"] > vec["TYPE_BLIND_auc"] + 0.1, \
        "settled vector must beat the type-blind (unconditioned) vector: %s vs %s" % (
            vec["GRADED_VECTOR_auc"], vec["TYPE_BLIND_auc"])
    assert vec["GRADED_minus_TWIN_auc"]["sep"], \
        "the settled vector's discrimination must be CONTEXT-driven (twin loses): %s" % vec["GRADED_minus_TWIN_auc"]

    # ---- OPTIMIZATION (item 4): sweeping the pinned biased-competition params yields NO test lift -> the residual
    #      is upstream in the INPUT ENCODING, not the readout (dev-tuned best == default). ----
    sw = SW.run(smoke=False)["result"]
    assert abs(sw["test_tuned_minus_default"]["delta"]) < 0.01, \
        "readout param sweep should give ~no test lift (residual is the input, not the readout): %s" % (
            sw["test_tuned_minus_default"],)
    assert sw["twin_loses_at_tuned"], "twin must still lose at the tuned config: %s" % sw

    # ---- #1 BOARD-NATIVE coref: the located negative on the board's OWN number (not a proxy) ----
    bn = BN.run(smoke=False)["result"]
    assert not bn["gated_minus_blind"]["sep"], \
        "board-native gated-blind must have a CI through zero (located negative on the board's own metric): %s" % (
            bn["gated_minus_blind"],)
    assert bn["gated_minus_filter_off"]["delta"] <= 0 or not bn["gated_minus_filter_off"]["sep"], \
        "board-native: gating must not recover the filter above the live pick: %s" % bn["gated_minus_filter_off"]

    # ---- #3 GRAIN sweep: the current lexname commit is near-optimal; WordNet homonymy grain does NOT beat it ----
    gr = GR.run(smoke=False)["result"]
    assert gr["homonymy_minus_lexname"] <= 0.005, \
        "WordNet homonymy grain should not beat the current lexname commit (needs a real sense-group asset): %s" % gr

    print("WITNESS PASS")
    print("  #1 BOARD-NATIVE coref: filter_off=%.4f blind=%.4f GATED=%.4f -> gated-blind=%s (CI incl 0), gated-off=%s"
          % (bn["board_common_acc"]["filter_off_live_pick"], bn["board_common_acc"]["filter_blind"],
             bn["board_common_acc"]["filter_GATED"], bn["gated_minus_blind"]["delta"],
             bn["gated_minus_filter_off"]["delta"]))
    print("  #3 GRAIN: exact=%.4f lexname(current)=%.4f homonymy(D=%s)=%.4f -> lexname near-optimal (hom-lexname=%s)"
          % (gr["test_exact"], gr["test_lexname_current_wire"], gr["best_homonymy_D_devtuned"],
             gr["test_homonymy_tuned"], gr["homonymy_minus_lexname"]))
    print("  2ND CONSUMER natural-logic: GATED=%.4f vs union BASELINE=%.4f (d=%s) -> gating HURTS the decisive is-a"
          % (nl["arms"]["GATED_committed_sense"]["acc"], nl["arms"]["BASELINE_union_isa"]["acc"], dgb["delta"]))
    print("  OPTIMIZATION sweep: test default=%.4f tuned=%.4f (best=[g%s tk%s pw%s]) -> readout MAXED, residual is "
          "the input encoding (human WiC ~0.80)" % (sw["test_default_acc"], sw["test_tuned_acc"],
          sw["best_config_devtuned"]["gamma"], sw["best_config_devtuned"]["topk"],
          sw["best_config_devtuned"]["prior_weight"]))
    print("  OPP#1 safe-write: gated-blind P=%s (safer) BUT gated-nobridge F=%s (not recovered) + gated~twin F=%s "
          "(restrictiveness not context)" % (bw["gated_minus_blind_P"]["delta"],
          bw["gated_minus_nobridge_F"]["delta"], bw["gated_minus_twin_F"]["delta"]))
    print("  OPP#3 ctx-modulated VECTOR: GRADED AUC=%.4f vs blind %.4f, twin-loses=%s -> vector currency validated"
          % (vec["GRADED_VECTOR_auc"], vec["TYPE_BLIND_auc"], vec["GRADED_minus_TWIN_auc"]["sep"]))
    print("  POSITIVE  WiC live-wire: WIRE_coarse=%.4f vs sense-blind majority=%.4f  (d=%s sep=%s; twin-loses=%s)"
          % (wire, maj, d_maj["delta"], d_maj["sep"], d_tw["sep"]))
    print("  NEGATIVE  coref: flip_rate=%.4f, twin_flips=%d>=real=%d, gated-baseline=%s (CI incl 0)"
          % (c["flip_rate_over_pairs"], c["flips_twin_shuffled_context"], c["flips_total"], d["gated_minus_baseline"]))
    print("  LIVENESS  sm.senses empty after read=%s; select_sense fires when invoked=%s"
          % (a["sm_senses_empty_after_read"], a["select_sense_returns_when_invoked"]))
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
