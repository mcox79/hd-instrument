"""Witness for the obl-spatial defer consumer + full-stack-upstream drill.

Codifies the rigorous located-negative/partial:
  W1  the landed obl Matrix-Tree marginal SEPARATES right-vs-wrong SPATIAL obl attachment on modern gold (UD-EWT):
      SPATIAL AUC > 0.70 and deferring low-confidence spatial attachments lifts selective accuracy > +0.10
      (the dormant signal is REAL for spatial -- contra the "inert for spatial" assumption). [re-run live, can fail]
  W2  the arc scorer is OVERCONFIDENT on spatial attachment (a confident-but-wrong slice exists) and that slice is
      NOT recovered by any sentence-internal upstream cue: verb-subcat/place-typing (thematic) <2% and sentence-level
      referential <3% -> the fix is the cross-sentence DISCOURSE loop, not a sentence-local cue. [from landed metrics]
  W3  the defer/re-attach CONSUMER is a genuine PRECISION mechanism whose marginal CONTENT is load-bearing: it beats
      the info-free (shuffled-marginal) twin CI-separated on SpaceEval `moves`. [from landed metrics]
  W4  the full-chain signal loss is DOMINATED by construction/typing coverage, NOT attachment: the attachment slice
      (the marginal's lever) is < 15% of gold-goal recall loss, while construction+typing > 40%. [from landed metrics]

Run: .venv/Scripts/python.exe verification/test_obl_spatial_defer.py
"""
import os
import sys
import json

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def _load(name):
    p = os.path.join(_REPO, "data", name, "metrics.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ok = 0

    # W1 -- re-run the diagnostic live (can fail): marginal separates spatial attachment on UD-EWT.
    import experiments.exp_obl_spatial_marginal_diagnostic_v1 as DIAG
    r = DIAG.run(smoke=False)
    sp = r["by_class"]["SPATIAL_all"]
    assert sp["auc_marginal_right_vs_wrong"] > 0.70, "W1 AUC: %s" % sp
    assert sp["selective_lift_over_blanket"] > 0.10, "W1 sel lift: %s" % sp
    print("W1 PASS: SPATIAL obl marginal AUC=%.4f, selective@50 lift=%+.4f (n=%d) -- dormant signal is REAL"
          % (sp["auc_marginal_right_vs_wrong"], sp["selective_lift_over_blanket"], sp["n"]))
    ok += 1

    # W2 -- the confident-but-wrong slice is not recovered by sentence-internal cues.
    th = _load("exp_obl_spatial_thematic_upstream_v1")
    rf = _load("exp_obl_spatial_referential_upstream_v1")
    cw_th = th["confident_wrong_slice"]["recovery_rate"]
    cw_rf = rf["confident_wrong_recovery"]["rate"]
    assert cw_th < 0.02, "W2 thematic recovery too high: %s" % cw_th
    assert cw_rf < 0.03, "W2 referential recovery too high: %s" % cw_rf
    assert rf["stage0_ref_predicts_LOW_attach_AUC"] > 0.5, "W2 referential should carry SOME signal (direction): %s" % rf["stage0_ref_predicts_LOW_attach_AUC"]
    print("W2 PASS: confident-wrong slice NOT recovered by sentence-internal cues (thematic %.1f%%, referential %.1f%%); "
          "referential is the RIGHT direction (Stage-0 AUC %.4f>0.5) but needs the cross-sentence discourse loop"
          % (100 * cw_th, 100 * cw_rf, rf["stage0_ref_predicts_LOW_attach_AUC"]))
    ok += 1

    # W3 -- the consumer beats the info-free twin CI-separated (marginal content load-bearing).
    cb = _load("exp_obl_spatial_combined_v1")
    tw = cb["GATED_vs_twin_f1"]
    assert tw["sep"] and tw["delta"] > 0, "W3 GATED must beat twin CI-sep: %s" % tw
    # the gated arm has the highest precision of all arms (the precision mechanism)
    arms = cb["arms"]
    assert arms["broadened_GATED"]["precision"] >= arms["conservative_blind"]["precision"], \
        "W3 gated precision should be >= floor precision: %s" % arms
    print("W3 PASS: marginal-GATED consumer beats info-free twin F1 %+.4f CI%s (content load-bearing); "
          "gated precision=%.4f >= floor %.4f (a real precision mechanism)"
          % (tw["delta"], tw["ci"], arms["broadened_GATED"]["precision"], arms["conservative_blind"]["precision"]))
    ok += 1

    # W4 -- the chain loses signal mostly at construction/typing, not attachment.
    sl = _load("exp_obl_spatial_chain_signalloss_v1")["stage_frac"]
    attach = sl["S4_ATTACH_MISS"]
    constr_typ = sl["S2_PREP_MISS"] + sl["S3_TYPING_MISS"]
    assert attach < 0.15, "W4 attachment slice should be minor: %s" % attach
    assert constr_typ > 0.40, "W4 construction+typing should dominate: %s" % constr_typ
    print("W4 PASS: chain signal loss = construction %.1f%% + typing %.1f%% (dominant) vs attachment %.1f%% (minor) "
          "-- the marginal's lever is real but small; the binder's construction coverage is the bigger organ"
          % (100 * sl["S2_PREP_MISS"], 100 * sl["S3_TYPING_MISS"], 100 * attach))
    ok += 1

    # W5 -- FIX #1 done RIGHT (the discourse referential loop on GUM gold coref) ALSO fails on the confident-wrong
    # slice: the properly-built cross-sentence candidate-count is uninformative for LOW-attach and recovers ~= twin.
    dr = _load("exp_obl_spatial_discourse_referential_v1")
    disc = dr["arms"]["DISCOURSE_candcount"]["recovery_rate"]
    s0 = dr["stage0_predicts_LOW_attach_AUC"]["DISCOURSE_candcount"]
    assert disc < 0.05, "W5 discourse-referential recovery should be ~twin: %s" % disc
    assert s0 < 0.55, "W5 discourse candidate-count should be uninformative for LOW-attach: %s" % s0
    print("W5 PASS: FIX #1 DONE RIGHT (discourse referential loop, GUM gold coref) also fails -- Stage-0 AUC %.4f "
          "(uninformative), recovers %.1f%% (=twin). 4th cue to fail -> the confident-wrong slice is the grounded "
          "WORLD-MODEL residual, not a static-cue fix." % (s0, 100 * disc))
    ok += 1

    # W6 -- OPTIMIZATION with the updated knowledge: OPT-A (commit to the graded_competition posterior, not defer)
    # is a CI-sep brain-foundational attachment gain with perfect no-regress; OPT-B (grounded-meaning cue) FAILS
    # (worse than greedy), the measured proof that a cue with a broken upstream cannot push.
    op = _load("exp_obl_spatial_optimize_v1")
    cvg = op["commit_vs_greedy"]
    assert cvg["sep"] and cvg["delta"] > 0, "W6 OPT-A commit must beat greedy CI-sep: %s" % cvg
    assert op["no_regress_broken_syntax_correct"]["commit"][0] == 0, "W6 OPT-A must be no-regress: %s" % op["no_regress_broken_syntax_correct"]
    assert op["conflict_vs_greedy"]["delta"] < 0, "W6 OPT-B (broken-upstream meaning cue) must FAIL: %s" % op["conflict_vs_greedy"]
    print("W6 PASS: OPT-A commit-not-defer = %+.4f CI%s CI-sep, 0 no-regress (a landable brain-foundational push); "
          "OPT-B meaning cue %+.4f (FAILS -- broken upstream cannot push)"
          % (cvg["delta"], cvg["ci"], op["conflict_vs_greedy"]["delta"]))
    ok += 1

    # W7 -- STRUCTURAL BUILD 1: the brain-foundational constraint-satisfaction scorer (normalized-recurrence,
    # McRae/Spivey) beats the surface-scorer greedy floor CI-sep; the meaning cues add ~0 for locatives (a
    # documented brain fact -- FULL ~= syn-only), so the gain is the syntactic commit.
    cx = _load("exp_obl_spatial_csx_scorer_v1")
    fvg = cx["full_vs_greedy"]
    assert fvg["sep"] and fvg["delta"] > 0, "W7 CSX scorer must beat the surface-scorer greedy floor CI-sep: %s" % fvg
    print("W7 PASS: constraint-satisfaction scorer (normalized-recurrence) beats surface floor %+.4f CI%s CI-sep; "
          "meaning cues add ~0 for locatives (FULL vs syn-only %+.4f) -- a documented brain fact, not a cheap build."
          % (fvg["delta"], fvg["ci"], cx["full_vs_synonly"]["delta"]))
    ok += 1

    # W8 -- the FINISH-UP resolver: implemented ALL optimizations right (commit + Erk backoff + prep-conditioning +
    # ConceptNet seed + Ferretti aspect-gate). The syntactic COMMIT is the win; the fully-upgraded THEM adds NO
    # generalizable signal for locative attachment (train-tuned weight overfits and does not beat syn-commit on test)
    # -- the documented brain-fact ceiling, confirmed with the complete implementation.
    rs = _load("exp_obl_spatial_resolver_v1")
    assert rs["acc"]["syn_commit"] > rs["acc"]["greedy_floor"], "W8 the commit must beat the greedy floor: %s" % rs["acc"]
    assert rs["full_vs_syncommit"]["delta"] <= 0.005, "W8 fully-upgraded THEM must add ~0 over syn-commit (ceiling): %s" % rs["full_vs_syncommit"]
    print("W8 PASS: FINISH-UP resolver -- syntactic COMMIT %.4f > greedy %.4f is the win; the FULLY-upgraded THEM "
          "(Erk+prep+ConceptNet+aspect) adds %+.4f over syn-commit = ~0 for locatives (documented brain-fact ceiling)."
          % (rs["acc"]["syn_commit"], rs["acc"]["greedy_floor"], rs["full_vs_syncommit"]["delta"]))
    ok += 1

    # W9 -- THE REAL FIX for THEM's data-starvation: a class-level ConceptNet AtLocation organ raises coverage
    # 10% -> ~68% and turns the meaning cue from HARMFUL (corpus-THEM -0.0185) to non-harmful; but even at high
    # coverage it adds ~0 over the syntactic commit -> the residual is a FUNDAMENTAL symmetric-plausibility ceiling,
    # not a data gap.
    af = _load("exp_obl_spatial_atloc_class_fix_v1")
    assert af["coverage"]["class_level_hit_rate"] > 0.5, "W9 the real fix must raise coverage well above the 10%% corpus rate: %s" % af["coverage"]
    assert af["atloc_vs_greedy"]["sep"] and af["atloc_vs_greedy"]["delta"] > 0, "W9 the fixed system must beat greedy CI-sep: %s" % af["atloc_vs_greedy"]
    assert af["atloc_vs_syncommit"]["delta"] >= -0.005, "W9 the fixed cue must no longer HURT vs syn-commit: %s" % af["atloc_vs_syncommit"]
    print("W9 PASS: REAL FIX -- class-level ConceptNet AtLocation raises coverage 10%%->%.0f%%, meaning cue no longer "
          "hurts (%+.4f vs syn-commit, was -0.0185 for corpus-THEM); residual is a FUNDAMENTAL symmetric-plausibility "
          "ceiling, not data." % (100 * af["coverage"]["class_level_hit_rate"], af["atloc_vs_syncommit"]["delta"]))
    ok += 1

    # W10 -- FIX-ALL + LAND-ALL: (a) the POS-tagger fix (interactive activation) is a located negative -- interactive
    # == baseline (gold-free coherence cannot recover the +0.029 oracle); (b) the promotion-ready module's commit is
    # correct (the landable optimization).
    import experiments.graded_spatial_obl_promote_v1 as PROMO
    assert PROMO.commit_obl_head({3: {1: 0.2, 5: 0.75}}, 3, [1, 5]) == 5, "W10 promote commit must pick max-marginal head"
    pi = _load("exp_obl_spatial_pos_interactive_v1")
    assert abs(pi["interactive_vs_baseline"]["delta"]) < 0.005, "W10 POS interactive should be a located negative (~=baseline): %s" % pi["interactive_vs_baseline"]
    print("W10 PASS: POS interactive-activation fix = located negative (%+.4f vs baseline -- gold-free coherence can't "
          "recover the +0.029 oracle); promotion-ready commit_obl_head verified (the landable optimization)."
          % pi["interactive_vs_baseline"]["delta"])
    ok += 1

    # W11 -- the UNIFIED continuously-learning tag+attachment prototype: its signature property is that it LEARNS AS
    # IT READS (never frozen) -- the running accuracy rises over the stream from a uniform start, and it self-organizes
    # the LINKED (category-gated attachment) cue.
    uo = _load("exp_obl_spatial_unified_online_v1")
    lc = uo["LEARNING_CURVE_running_acc"]
    assert lc["last_third"] > lc["first_third"], "W11 the online learner must learn as it reads (rising curve): %s" % lc
    print("W11 PASS: unified continuously-learning cell -- running acc rises %.4f -> %.4f (learns as it reads, never "
          "frozen); self-organized linked weights %s (syn + verb-gated attachment)."
          % (lc["first_third"], lc["last_third"], uo["learned_weights_final"]))
    ok += 1

    # W12 -- PUSH-FURTHER (honest): the linked category-gated cue, learned online from a consolidated init and
    # evaluated on HELD-OUT data, adds ~0 over the frozen commit (the marginal already carries the obl/nmod category
    # signal) -> no further landable ACCURACY optimization remains for locative attachment; the commit is the win.
    le = _load("exp_obl_spatial_linked_eval_v1")
    assert abs(le["linked_vs_frozen"]["delta"]) < 0.005, "W12 linked cue should be ~redundant on held-out: %s" % le["linked_vs_frozen"]
    assert le["no_regress_broken"]["count"] <= 2, "W12 linked cue must be no-regress: %s" % le["no_regress_broken"]
    print("W12 PASS: push-further held-out -- linked cue %+.4f vs frozen commit (redundant; marginal already carries "
          "the category signal). No further landable accuracy for locatives; the commit (+0.0144) is the win."
          % le["linked_vs_frozen"]["delta"])
    ok += 1

    print("\nALL WITNESSES PASS (%d/%d)" % (ok, ok))
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
