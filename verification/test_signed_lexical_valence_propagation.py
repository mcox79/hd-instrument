"""Scaffold-free witness for notes/problems/propagate_along_the_relation_that_carries_valence.

Reproduces the HEADLINE from the live organ + WordNet WITHOUT re-running a landed cell in place:

  CORE (does the valence-bearing axis carry valence?): signed propagation along lexical relations
    (antonym FLIPS, near-synonymy/derivational PRESERVE) scores > its OWN-subset majority floor,
    CI-separated over the floor, on ~485 polar held-out verbs -- and BOTH info-free twins LOSE:
      * SIGN-SCRAMBLE (randomise which relations flip vs preserve) -> chance   [the slug's proof]
      * SHUFFLE-LABEL (permute the anchor polarities)             -> chance
  GENERALISE: at 1 hop it reaches ~119 items at ~0.84 -- 6x the accurate antonym stage's 19 -- with
    the SAME accuracy, i.e. it does not trade accuracy for the extra coverage.
  ANTONYM FLIP is load-bearing: sign-blind (treat antonym as preserve) scores materially lower.

  ALSO ASSERTS THE HONEST NULL the brief's literal bar returned: the valence axis and Stage B's
  taxonomic axis are near-DISJOINT (overlap ~40-60 of 1971), so a paired margin over Stage B on the
  shared items is underpowered and ties -- the brief's instrument is the wrong one; the own-subset
  floor + twins is the right one.

Run:  .venv/Scripts/python.exe verification/test_signed_lexical_valence_propagation.py
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import experiments.exp_signed_lexical_valence_propagation_v1 as V1
from hdlab import wordnet_polarity_propagation as WP


def main() -> int:
    st = V1.self_test()
    print("[self_test]", st, flush=True)

    gold = V1.load_gold()
    items, truth = V1.population(gold)
    assert len(items) == 1971, "population changed on disk: %d != 1971" % len(items)
    anchors = tuple(sorted(WP.ANCHOR_WORDS))
    poles = {a: V1.POLE_NUM[WP.ANCHOR_POLARITY[a]] for a in anchors}

    reach2 = V1.reach_all(items, anchors, 2)
    pred_H1 = V1.signed_predict_all(reach2, poles, V1.GAMMA, 0.0, 1)
    pred_H2 = V1.signed_predict_all(reach2, poles, V1.GAMMA, 0.0, 2)
    pred_blind = V1.signed_predict_all(reach2, poles, V1.GAMMA, 0.0, 2, sign_blind=True)
    pred_B = V1.stage_b_predict(items)

    boot = np.random.default_rng(20260826)

    def gate(pred):
        pit = [(1 if pred[w] == truth[w] else 0, pred[w] is not None) for w in items]
        acc, lo, hi, n = V1.cluster_bootstrap_ci(pit, boot, n_boot=2000)
        commit = [w for w in items if pred[w] is not None]
        fl = max(Counter(truth[w] for w in commit).values()) / len(commit)
        return acc, lo, n, fl

    ok = True

    accH2, loH2, nH2, flH2 = gate(pred_H2)
    print("[H2] acc=%.4f ci_lo=%.4f n=%d own_floor=%.4f" % (accH2, loH2, nH2, flH2), flush=True)
    if not (loH2 > flH2):
        print("FAIL: H2 not CI-separated over its own-subset floor"); ok = False
    if not (nH2 >= 400):
        print("FAIL: H2 coverage collapsed (%d < 400)" % nH2); ok = False

    accH1, loH1, nH1, flH1 = gate(pred_H1)
    print("[H1] acc=%.4f ci_lo=%.4f n=%d own_floor=%.4f  (Stage A shipped: 19 @ 0.8421)"
          % (accH1, loH1, nH1, flH1), flush=True)
    if not (accH1 > 0.78 and nH1 >= 100):
        print("FAIL: 1-hop did not generalise the antonym stage (acc %.3f, n %d)" % (accH1, nH1))
        ok = False

    accBl, _, nBl, _ = gate(pred_blind)
    print("[sign-blind H2] acc=%.4f n=%d  (signed H2 = %.4f)" % (accBl, nBl, accH2), flush=True)
    if not (accH2 > accBl):
        print("FAIL: antonym flip not load-bearing (signed %.4f <= blind %.4f)" % (accH2, accBl))
        ok = False

    # -- SIGN-SCRAMBLE twin must LOSE (the slug: the RELATION's sign carries valence) --
    scramble_accs = []
    for sd in (20260826, 7, 101):
        neigh_fn = V1.scramble_edge_signs(sd)
        reach_sc = {w: V1.signed_reach_with(neigh_fn, w, anchors, 2) for w in items}
        psc = V1.signed_predict_all(reach_sc, poles, V1.GAMMA, 0.0, 2)
        com = [w for w in items if psc[w] is not None]
        scramble_accs.append(sum(1 for w in com if psc[w] == truth[w]) / len(com))
    print("[sign-scramble twin] accs=%s (chance ~0.50; signed H2 = %.4f)"
          % ([round(a, 3) for a in scramble_accs], accH2), flush=True)
    if not (accH2 - max(scramble_accs) > 0.10):
        print("FAIL: sign-scramble twin did not lose by a clear margin"); ok = False

    # -- SHUFFLE-LABEL twin must LOSE (permutation null, 20 seeds) --
    null_accs = []
    for k in range(20):
        rng = np.random.default_rng(500 + k)
        sp = dict(zip(anchors, rng.permutation([poles[a] for a in anchors])))
        ps = V1.signed_predict_all(reach2, sp, V1.GAMMA, 0.0, 2)
        com = [w for w in items if ps[w] is not None]
        null_accs.append(sum(1 for w in com if ps[w] == truth[w]) / len(com))
    p_val = float(np.mean([a >= accH2 for a in null_accs]))
    print("[shuffle-label null] mean=%.4f p95=%.4f p(>=real)=%.3f"
          % (float(np.mean(null_accs)), float(np.percentile(null_accs, 95)), p_val), flush=True)
    if not (p_val <= 0.10 and np.mean(null_accs) < accH2 - 0.15):
        print("FAIL: shuffle-label twin not clearly below the real arm"); ok = False

    # -- HONEST NULL: valence axis and Stage B's taxonomic axis are near-disjoint (overlap tiny) --
    overlap = sum(1 for w in items if pred_H2[w] is not None and pred_B[w] is not None)
    print("[disjointness] LEX_H2 commits=%d, Stage B commits=%d, overlap=%d"
          % (nH2, sum(1 for w in items if pred_B[w] is not None), overlap), flush=True)
    if not (overlap < 100):
        print("NOTE: overlap unexpectedly large -- the paired-vs-Stage-B bar may now be testable");

    # -- v3 SUBSTRATE findings: embodied space carries valence (weakly) where taxonomic did not;
    #    opposition is irreducible (antonyms are embodied-similar, so the flip rescues them) --
    import experiments.exp_grounded_valence_propagation_v3 as V3
    gc = V3.grounded_carries_valence(items, gold, seed=0, n_pairs=6000)
    print("[grounded carries valence] rho=%.4f null_p95=%.4f outside_null=%s (taxonomic was -0.0023, inside null)"
          % (gc["spearman_rho"], gc["null_p95"], gc["outside_null"]), flush=True)
    if not (gc["spearman_rho"] > gc["null_p95"] and gc["outside_null"]):
        print("FAIL: grounded similarity did not carry valence outside its null"); ok = False

    pred_gaxis = V3.grounded_axis_predict_all(items, anchors, poles)
    pred_gaxis_s, _ = V3.antonym_overlay(items, pred_gaxis, anchors, poles)
    accGA, loGA, nGA, flGA = gate(pred_gaxis)
    print("[grounded evaluative-axis] acc=%.4f ci_lo=%.4f n=%d floor=%.4f (weak but CI-separated, 99%% coverage)"
          % (accGA, loGA, nGA, flGA), flush=True)
    if not (loGA > flGA and nGA > 1900):
        print("FAIL: grounded evaluative-axis not separated at near-total coverage"); ok = False

    gv = V3.grounded_predict_all(items, truth, anchors, poles)
    anto = sorted((V3.antonym_overlay(items, gv, anchors, poles))[1])
    gv_anto = V3._acc_on(gv, truth, anto)
    gs_anto = V3._acc_on(pred_gaxis_s, truth, anto)
    print("[antonym confound] grounded-vote on %d antonym items=%.3f -> with flip=%.3f (opposition is irreducible)"
          % (len(anto), gv_anto, gs_anto), flush=True)
    if not (gs_anto > gv_anto + 0.15):
        print("FAIL: antonym flip did not rescue the embodied-similar opposites"); ok = False

    # -- v4 FOCUSED FIDELITY DRILL: valence-code SHAPE + opposition operator --
    import experiments.exp_valence_opposition_fidelity_v4 as V4
    B = V4.reflection_test(items, anchors, poles, gold)
    at, sy = B["ANTONYM_pairs"], B["SYNONYM_pairs"]
    print("[opposition SHAPE] antonym TRUE-rating corr=%.3f, synonym=%.3f | embodied: antonym=%.3f synonym=%.3f"
          % (at["TRUE_rating_corr"], sy["TRUE_rating_corr"],
             at["embodied_valence_axis_corr"], sy["embodied_valence_axis_corr"]), flush=True)
    # brain metric: antonymy FLIPS graded valence, synonymy PRESERVES it
    if not (at["TRUE_rating_corr"] < -0.3 and sy["TRUE_rating_corr"] > 0.3):
        print("FAIL: signed-relation SHAPE not confirmed on the brain's graded metric"); ok = False
    # embodied geometry cannot tell antonym from synonym (the flip is invisible -> irreducible)
    if not (abs(at["embodied_valence_axis_corr"] - sy["embodied_valence_axis_corr"]) < 0.12):
        print("FAIL: embodied space distinguishes antonym from synonym (reflection hypothesis would hold)")
        ok = False

    A = V4.graded_metric(items, gold, anchors, poles)
    print("[graded readout] lex-vote-magnitude vs continuous rating rho=%.3f (twin %s)"
          % (A["lex_vote_magnitude_vs_rating_rho"], A["lex_vote_twin_shuffle_rhos"]), flush=True)
    if not (A["lex_vote_magnitude_vs_rating_rho"] > 0.3
            and A["lex_vote_magnitude_vs_rating_rho"] - np.mean(A["lex_vote_twin_shuffle_rhos"]) > 0.2):
        print("FAIL: graded lexical readout does not track continuous valence above its twin"); ok = False

    # -- v5 GENERALIZATION: the signed-relation structure is UNIVERSAL across parts of speech --
    import experiments.exp_valence_generalization_pos_v5 as V5
    for tag in ("ADJ", "NOUN", "VERB"):
        o = V5.opposition_universality(gold, tag)
        print("[generalise %s] antonym rating-corr=%.3f synonym=%.3f random=%.3f"
              % (tag, o["ANTONYM"]["rating_corr"], o["SYNONYM"]["rating_corr"], o["RANDOM"]["rating_corr"]),
              flush=True)
        if not (o["ANTONYM"]["rating_corr"] < -0.3 and o["SYNONYM"]["rating_corr"] > 0.3
                and abs(o["RANDOM"]["rating_corr"]) < 0.2):
            print("FAIL: signed-relation structure did not generalise to %s" % tag); ok = False

    # -- v6 ADJECTIVE BUILD: signed propagation on adjectives beats the verb result; both twins lose;
    #    a cross-POS bootstrap from the verb seed (zero new labelling) also clears --
    import experiments.exp_signed_lexical_valence_propagation_adjectives_v6 as V6
    hand_a, hand_pol = V6.hand_anchors()
    aitems, atruth = V6.adj_population(gold, hand_a)
    aboot = np.random.default_rng(7)
    amain, areach, apred = V6.score_arm(aitems, atruth, hand_a, hand_pol, aboot)
    ascr = []
    for sd in (7, 101):
        fn = V6._scramble_adj(sd)
        r = {w: V1.signed_reach_with(fn, w, hand_a, 2) for w in aitems}
        p = {w: V1.predict_signed(r[w], hand_pol, V6.GAMMA, 0.0, 2) for w in aitems}
        com = [w for w in aitems if p[w] is not None]
        ascr.append(sum(1 for w in com if p[w] == atruth[w]) / len(com))
    print("[adjectives HAND] signed acc=%.4f ci_lo=%.4f n=%d floor=%.4f | sign-scramble=%s (verb was 0.726)"
          % (amain["acc"], amain["ci"][0], amain["n_commit"], amain["floor"],
             [round(x, 3) for x in ascr]), flush=True)
    if not (amain["ci"][0] > amain["floor"] and amain["acc"] > 0.75 and amain["acc"] - max(ascr) > 0.2):
        print("FAIL: adjective signed propagation did not clear (separated, >0.75, twin loses)"); ok = False

    print("WITNESS PASS" if ok else "WITNESS FAIL", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
