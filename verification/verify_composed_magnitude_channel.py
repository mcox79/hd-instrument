"""Scaffold-free witness for the COMPOSED scalar-magnitude meaning channel + the word-class operation router.

Reproduces the two headline claims WITHOUT calling the experiments' run() (so it never overwrites a landed
metrics.json -- it imports the pure compute functions, which write nothing, and asserts on their returns):

  1. THE COMPOSED CHANNEL beats the strongest SINGLE sub-op AND the incumbent cosine CI-separated on the pooled
     multi-dimension magnitude recovery (dimension-routing + per-dim grounding), with the info-free twins losing,
     and the FPE-log substrate code preserves the Weber (scale-invariant) property on the real degrees + the
     comparator unbind decodes the log-ratio + the structure-free twin is flat.
  2. OPERATION ROUTING beats BOTH a gloss-only reader (misses gradable-adj magnitude) and a magnitude-only reader
     (destroys N/V similarity), with N/V read-outs identical under routing (no regression).

Run: .venv/Scripts/python.exe verification/verify_composed_magnitude_channel.py   (tracing-independent, ASCII-only)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_perclass_meaning_operations_v1 as V1
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP
import experiments.exp_adjective_intensity_ordering_v1 as INT
import experiments.exp_composed_magnitude_channel_v1 as CMC
import experiments.exp_operation_router_v1 as ROUT
import experiments.exp_composed_magnitude_comparison_v1 as CMP


def main():
    idf, _ = V1._global_idf()
    conc = V1.ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=True)
    war = V1.load_warriner(); concn = V1.load_concreteness()
    freq, aoa = INT.load_freq_aoa(); lanc = DEEP.load_lancaster_perceptual()
    needed = set(V1.all_wordnet_adjectives()) | set(war) | set(concn)
    for src in ("crowd", "wilkinson", "demelo"):
        import glob
        for path in glob.glob(os.path.join(CMC.DATA, src, "gold_rankings", "*.rankings")):
            s = INT.parse_scale(path)
            if s:
                needed |= {s[0], s[1]} | {t for _, t in s[2]}
    from experiments.exp_conceptual_meaning_channel_v1 import _load_bench, BENCH
    for bn, (p, k, i1, i2, isc) in BENCH.items():
        for w1, w2, *_ in _load_bench(p, k, i1, i2, isc):
            needed |= {w1, w2}
    needed |= {w for seeds in V1.DIM_SEEDS.values() for pr in seeds for w in pr}
    gv = V1.build_or_load_glove(needed)
    chan = CMC.ScalarMagnitudeChannel(gv, freq, lanc, d_sub=2048)

    # LIGHTWEIGHT reverify: assert the QUALITATIVE (CI-separated) claims in smoke mode -- fast, inline-appropriate.
    # The exact full-power headline numbers are the landed data/*/metrics.json (heavy runs, not re-run inline).
    # ---- CLAIM 1: composed channel + substrate ----
    t1 = CMC.t1_routed_recovery(chan, conc, war, concn, smoke=True)
    b_sub = t1["boot_COMPOSED_minus_strongest_subop"]; b_cos = t1["boot_COMPOSED_minus_cosine"]
    assert b_sub["ci_lo"] > 0, ("composed does not beat the strongest single sub-op CI-separated", b_sub)
    assert b_cos["ci_lo"] > 0, ("composed does not beat the incumbent cosine CI-separated", b_cos)
    assert t1["pooled_abs_rho"]["twin_random_axis"] < t1["pooled_abs_rho"]["COMPOSED_channel"], "random twin not losing"
    print("[witness] composed channel PASS: pooled COMPOSED=%.3f > strongest sub-op %s(%.3f) [+%.3f, ci_lo=%.3f] > cosine %.3f"
          % (t1["pooled_abs_rho"]["COMPOSED_channel"], t1["strongest_single_subop"],
             t1["pooled_abs_rho"][t1["strongest_single_subop"]], b_sub["margin"], b_sub["ci_lo"],
             t1["pooled_abs_rho"]["incumbent_cosine"]))

    t3 = CMC.t3_substrate_weber_on_real_degrees(chan, conc, smoke=True)
    assert t3["weber_preserved_on_real_degrees"], ("Weber not preserved on real degrees after linear->log", t3)
    assert t3["composed_code_samepole_decode_logratio_corr"] > 0.98, ("comparator unbind does not decode log-ratio", t3)
    assert t3["twin_is_flat"], ("structure-free FPE twin not flat", t3)
    print("[witness] substrate PASS: FPE-log Weber preserved (LOG ratio-CV=%.3f vs LINEAR %.3f); comparator decode corr=%.3f; twin flat"
          % (t3["LOG_fixed_ratio_CV"], t3["LINEAR_fixed_ratio_CV"], t3["composed_code_samepole_decode_logratio_corr"]))

    # ---- CLAIM 2: operation router ----
    sim = ROUT.similarity_by_class(gv, conc, chan, war)
    mag = ROUT.magnitude_by_gradability(chan, conc, war)
    readers = ROUT.router_end_to_end(sim, mag)
    grad = mag["gradable"]["boot_magnitude_minus_gloss"]
    assert grad["ci_lo"] > 0, ("routing gain on gradable-adj magnitude not CI-separated", grad)
    assert readers["routed"]["_mean_over_classes"] > readers["single_op"]["_mean_over_classes"], "routed !> gloss-only"
    assert readers["routed"]["_mean_over_classes"] > readers["magnitude_only"]["_mean_over_classes"], "routed !> magnitude-only"
    assert readers["routed"]["N_similarity"] == readers["single_op"]["N_similarity"], "N regression under routing"
    assert readers["routed"]["V_similarity"] == readers["single_op"]["V_similarity"], "V regression under routing"
    assert sim["N"]["magnitude_as_similarity_rho"] < sim["N"]["gloss_cosine_rho"], "magnitude op not shown to fail N similarity"
    print("[witness] router PASS: ROUTED mean=%.3f > gloss-only %.3f and > magnitude-only %.3f; gradable-adj magnitude +%.3f CI-sep; N/V no regression"
          % (readers["routed"]["_mean_over_classes"], readers["single_op"]["_mean_over_classes"],
             readers["magnitude_only"]["_mean_over_classes"], grad["margin"]))

    # ---- CLAIM 3: the composed channel is a COMPARISON system (distance effect) + congruity structure ----
    ta = CMP.test_a_comparison(chan, conc, war, smoke=True)
    assert ta["boot_composed_minus_cosine"]["ci_lo"] > 0, ("composed comparison does not beat cosine CI-sep", ta)
    assert ta["boot_composed_minus_random"]["ci_lo"] > 0, ("composed comparison does not beat random CI-sep", ta)
    assert ta["distance_effect_composed"]["far_minus_near"] > 0, ("no Moyer distance effect", ta)
    tb = CMP.test_b_congruity_from_pole(chan, conc, war, smoke=True)
    assert (tb["composed_congruity_AUC_same_over_cross"]
            > tb["INCUMBENT_gloss_cosine_AUC_same_over_cross"] + 0.1), ("no congruity structure over incumbent", tb)
    assert tb["same_pole_decode_logratio_corr"] > 0.9, ("same-pole comparator does not decode log-ratio", tb)
    print("[witness] comparison-system PASS: relative-comparison composed=%.3f > cosine=%.3f (+%.3f CI-sep); distance effect +%.3f; "
          "congruity AUC=%.3f vs incumbent %.3f"
          % (ta["composed_acc"], ta["cosine_acc"], ta["boot_composed_minus_cosine"]["margin"],
             ta["distance_effect_composed"]["far_minus_near"], tb["composed_congruity_AUC_same_over_cross"],
             tb["INCUMBENT_gloss_cosine_AUC_same_over_cross"]))

    print("\n[witness] ALL CHECKS PASS -- the composed magnitude channel (dimension-routed, per-dim grounded, oriented "
          "place code + FPE-log Weber comparator) beats every single sub-op + the incumbent cosine CI-separated, and "
          "the word-class operation router beats both a gloss-only and a magnitude-only reader with no N/V regression.")


if __name__ == "__main__":
    main()
