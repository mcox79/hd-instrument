"""Scaffold-free witness for stress_test_which_organ_wins_actually_generalize_on_held_out_text.

Recomputes the deep-rerun headline FROM SOURCE (the real LitBank who-did-what cache + the content_addressable
organ's OWN retrieval arms, imported verbatim), asserting the bands rather than trusting any metrics.json:

  (A) POSITIVE CONTROL -- the harness reproduces the organ's synthetic win: SEP_CA >> FLAT at load=32,p=0.7.
      (so any real-data null is a generalization gap, not a broken harness)
  (B) GENERALIZATION -- on the REAL LitBank per-entity population the organ's specific claim (SEP_CA beats
      FLAT) DOES NOT HOLD where entities carry <=3 events (87.3% of real entities): SEP_CA ties FLAT.
  (C) MECHANISM IS REAL BUT RARE -- at the high-fan tail (>=17 events) SEP_CA DOES beat FLAT and the counting
      floor CI-separated, and the info-free twin LOSES.
  (D) DG HURTS on identity-orthogonal real codes -- SEP_CA_DG < SEP_CA at the tail (a fix for a correlation
      problem this task does not have).

Run: .venv/Scripts/python.exe verification/test_generalize_retrieval_real_codes.py
Pure numpy + torch, CPU. Reads the pre-parsed cache. Writes nothing. NO hdlab/ mutation.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
import torch  # noqa: E402

from experiments import exp_generalize_retrieval_real_codes_v1 as G  # noqa: E402
from experiments import exp_content_addressable_register_retrieval_v1 as CAR  # noqa: E402

N = 0


def check(name, cond):
    global N
    N += 1
    assert cond, "WITNESS FAIL [%s]" % name
    print("  ok  W%02d  %s" % (N, name))


def _bin_records(by_bin_all, lbl, cb, d, p, cap, use_dg, seed0=5000):
    """Score up to `cap` entities of one event-count bin, sampled deterministically."""
    lst = by_bin_all[lbl]
    rng = np.random.default_rng(4242 + G.BIN_LABELS.index(lbl))  # deterministic per-bin (no built-in hash)
    if len(lst) > cap:
        sel = rng.choice(len(lst), size=cap, replace=False)
        lst = [lst[int(i)] for i in sel]
    return [G.score_entity(ev, cb, d, p, seed=seed0 + i, use_dg=use_dg) for i, (_, ev) in enumerate(lst)]


def main():
    print("== load real LitBank who-did-what + build codebooks ==")
    ents, verb_ct = G.load_entities()
    n_ev = sum(len(v) for v in ents.values())
    check("real cache: 28,569 gov_verb events, ~7,779 entities", n_ev == 28569 and 7000 <= len(ents) <= 8500)
    d = 128
    gen_t = torch.Generator().manual_seed(20260830)
    cb = G.build_codebooks(verb_ct, d, gen_t, correlated=False)

    # bucket
    by_bin = {lbl: [] for lbl in G.BIN_LABELS}
    for ekey, ev in ents.items():
        n = len(ev)
        for (lo, hi), lbl in zip(G.BINS, G.BIN_LABELS):
            if lo <= n <= hi:
                by_bin[lbl].append((ekey, ev)); break
    # the real operating point: 1-event entities dominate
    frac_le3 = (len(by_bin["1"]) + len(by_bin["2-3"])) / len(ents)
    check("real operating point: >=85%% of entities carry <=3 events", frac_le3 >= 0.85)

    gb = np.random.default_rng(1)

    print("== (A) positive control: harness reproduces the organ's synthetic win ==")
    res, _ = CAR.run_cell(128, 32, 0.0, 0.7, 101, 15)
    check("SEP_CA >> FLAT at synthetic load=32,p=0.7 (reproduces 0.99 headline)",
          res["SEP_CA"]["mean"] > res["FLAT"]["mean"] + 0.10 and res["SEP_CA"]["mean"] >= 0.90)

    print("== (B) generalization: SEP_CA does NOT beat FLAT at real low load (<=3 events) ==")
    lo_recs = _bin_records(by_bin, "1", cb, d, 0.7, 60, use_dg=False) + \
        _bin_records(by_bin, "2-3", cb, d, 0.7, 60, use_dg=False)
    sf_lo = G.bootstrap_paired(lo_recs, "SEP_CA", "FLAT", gb)
    sf_lo_delta = sf_lo["delta"]
    check("SEP_CA - FLAT collapses at real low load (delta < 0.10: an order of magnitude below the +0.94 synthetic headline)",
          sf_lo_delta < 0.10)
    check("FLAT is already near-perfect at <=3 events (>=0.95, leaving little headroom for SEP)",
          float(np.mean([r["FLAT"] for r in lo_recs])) >= 0.95)

    print("== (C) mechanism is real but rare: SEP_CA wins at the high-fan tail, twin loses ==")
    tail = _bin_records(by_bin, "17-63", cb, d, 0.7, 60, use_dg=True) + \
        _bin_records(by_bin, "64+", cb, d, 0.7, 60, use_dg=True)
    sf_hi = G.bootstrap_paired(tail, "SEP_CA", "FLAT", gb)
    sc_hi = G.bootstrap_paired(tail, "SEP_CA", "COUNTING", gb)
    st_hi = G.bootstrap_paired(tail, "SEP_CA", "SHUFFLED_KEYS", gb)
    check("SEP_CA beats FLAT CI-separated at the >=17-event tail", sf_hi["band"] == "ABOVE" and sf_hi["delta"] > 0.3)
    check("SEP_CA beats the counting floor CI-separated at the tail", sc_hi["band"] == "ABOVE")
    check("info-free twin (shuffled keys) LOSES at the tail", st_hi["band"] == "ABOVE")

    print("== (D) DG pattern-separation HURTS on identity-orthogonal real codes ==")
    dg_hi = G.bootstrap_paired(tail, "SEP_CA_DG", "SEP_CA", gb)
    check("SEP_CA_DG < SEP_CA at the tail (DG hurts orthogonal codes; not a fix for this task)",
          dg_hi["band"] == "BELOW")

    print("== (E) the SIMILAR-COMPETITOR gate: content under-determines on the RIGHT axis (research reframe) ==")
    from experiments import exp_generalize_retrieval_similar_competitor_gate_v1 as GATE  # noqa: E402
    gr = GATE.run(n_boot=800)
    check("similar-competitor ambiguous subset is LARGE on real text (>10k queries; not the sparse event-count regime)",
          gr["n_ambiguous_queries"] > 10000)
    check("content-only floor UNDER-DETERMINES on the ambiguous subset (<=0.75 -> gate=BUILD)",
          gr["content_only_floor"] <= 0.75 and gr["GATE"] == "BUILD")
    check("leak-free temporal-context beats its shuffled-context twin (recency carries real info)",
          gr["context_minus_shuffled_twin"] > 0.02)
    check("naive recency ALONE does not beat the content floor (value hinges on cue COMBINATION, not context alone)",
          gr["context_minus_content"]["band"] != "ABOVE" or gr["context_minus_content"]["delta"] < 0.10)
    check("cue-overload signature: content floor DROPS as competitor count rises",
          gr["strata_by_competitor_count"]["2"]["content_floor"] > gr["strata_by_competitor_count"]["5+"]["content_floor"])

    print("== (F) SECOND rerun: the CAUSATION TYPER cluster DOES NOT HOLD on real MAVEN-ERE causal relations ==")
    from experiments import exp_generalize_causation_typer_maven_ere_v1 as CAUS  # noqa: E402
    cr = CAUS.run(n_boot=800)
    check("large real causal population (>5000 annotated causal relations, vs the organs' n=13-42 minimal pairs)",
          cr["n_all"] > 5000)
    check("force-dynamic typer FIRES on a small minority of real causal relations (<0.25: input usually absent)",
          cr["fire_rate"] < 0.25)
    check("typer LOSES to the majority-class floor where it fires (CI-separated BELOW)",
          cr["typer_minus_majority"]["band"] == "BELOW")
    check("typer does NOT beat its own shuffled-lexicon twin (force signal ~ noise for the real distinction)",
          cr["typer_minus_twin"]["band"] != "ABOVE")
    check("verdict = DOES_NOT_HOLD (constructed 0.929/1.000 win does not survive on real annotated causation)",
          cr["VERDICT"] == "DOES_NOT_HOLD")

    print("== (G) causation reframe gate: the IMPLICIT event-type covariation route carries the missing signal ==")
    from experiments import exp_generalize_causation_implicit_covariation_gate_v1 as COV  # noqa: E402
    cg = COV.run(n_boot=800)
    check("implicit event-type covariation beats its OWN info-free twin (a REAL signal, unlike force-dynamics)",
          cg["covariation_minus_twin"]["band"] == "ABOVE")
    check("covariation beats the majority floor CI-separated (clears the pre-registered +0.05 next-problem HARD-PASS)",
          cg["covariation_minus_majority"]["band"] == "ABOVE" and cg["covariation_minus_majority"]["delta"] >= 0.05)
    check("covariation beats the force-dynamic typer CI-separated (the implicit route is the right primitive)",
          cg["covariation_minus_forcedynamic"]["band"] == "ABOVE")
    check("covariation carries signal on the ~84% subset where the force-dynamic typer never fires",
          cg["on_no_fire_subset"]["covariation_minus_majority"]["band"] == "ABOVE"
          and cg["on_no_fire_subset"]["covariation_minus_twin"]["band"] == "ABOVE")
    check("gate verdict = implicit covariation is the missing signal (names the next problem, empirically)",
          cg["VERDICT"] == "IMPLICIT_COVARIATION_IS_THE_MISSING_SIGNAL")

    print("== (H) THIRD rerun: the N400 content-PE event segmenter DOES NOT HOLD on real MCScript2 prose ==")
    from experiments import exp_generalize_n400_segmenter_mcscript_v1 as SEG  # noqa: E402
    sg = SEG.run("full", n_boot=800)
    m, c = sg["means"], sg["contrasts"]
    check("N400 content-PE boundary-F1 collapses on real prose (< 0.25 vs synthetic 0.987)",
          m["N400_content"]["mean"] < 0.25)
    check("N400 does NOT beat surface FORM_NOVELTY (the graded-content signal adds nothing over surface novelty)",
          c["n400_minus_form"]["band"] != "ABOVE")
    check("N400 LOSES to a rate-matched RANDOM detector (content-PE positions are misaligned with real seams)",
          c["n400_minus_random"]["band"] == "BELOW")
    check("N400 only weakly beats its own permuted-surprise twin (NOT CI-separated)",
          c["n400_minus_twin"]["band"] != "ABOVE")
    check("verdict = DOES_NOT_HOLD (synthetic clean-topic-jump win does not survive real event structure)",
          sg["VERDICT"] == "DOES_NOT_HOLD")

    print("== (I) FOURTH rerun: sparse SELECTIVE replay DOES NOT beat the uniform twin on a real cross-novel shift ==")
    from experiments import exp_generalize_consolidation_gutenberg_oldnew_v1 as CONS  # noqa: E402
    co = CONS.run("full", n_boot=800)
    check("the store experiences REAL interference (OLD retention drops after learning NEW -> a valid test)",
          co["means"]["sparse"]["selective"]["old_retained"] < co["means"]["sparse"]["selective"]["old_after1"] - 0.1)
    check("sparse SELECTIVE replay does NOT beat the info-free UNIFORM twin (the organ's headline claim fails)",
          co["sparse_selective_vs_uniform"]["band"] != "ABOVE")
    check("consolidation verdict = DOES_NOT_HOLD on the real cross-novel OLD/NEW split",
          co["VERDICT"] == "DOES_NOT_HOLD")
    check("DRILL: the brain-faithful NEED-based priority ALSO ties the uniform twin (negative is robust)",
          co["sparse_need_vs_uniform"]["band"] != "ABOVE")
    check("DRILL verdict = selective replay is genuinely no lever on real cross-domain data (not a priority-signal bug)",
          co["DRILL_VERDICT"] == "SELECTIVE_REPLAY_GENUINELY_NO_LEVER_ON_REAL_DATA")

    print("\nALL %d WITNESS CHECKS PASS" % N)


if __name__ == "__main__":
    main()
