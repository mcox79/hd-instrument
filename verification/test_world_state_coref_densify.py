"""Witness for `the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what`.

Scaffold-free: recomputes every claim FROM SOURCE (no metrics.json read). Covers the full brain-foundational
two-stage entity-binding densification of the mutable world-state register:

  [1] EntityBinder (Stage-1 dispatcher) -- all five routes: pleonastic-it filter, indexical (I/me/my->NARRATOR),
      anaphoric (he/she->cluster or abstain), object anaphora (it->salient theme), scope-out (we/you abstain).
  [2] world_state_register CORE (Stage-2 update) still faithful (the register mechanism the parent proved).
  [3] densify cell logic: blind tracks RAW STRINGS (fragments the entity); reader tracks CLUSTERS.
  [4] deixis/object cell logic: blind fragments the narrator (i,me); object 'it' relocates to its antecedent.
  [5] LitBank he/she headline (smoke, directional): reader-densified > blind on who-has-what; gold oracle == 1.0;
      the answer CHANGES at the transfer (change-point positive control).
  [6] MCScript2 object-anaphora build-across (smoke, directional): resolving 'it' RELOCATES transfers blind lost
      (who-has-what impact > 0), with the pleonastic filter active.

Run: .venv/Scripts/python.exe verification/test_world_state_coref_densify.py
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _p(name, ok):
    print("[%s] %s" % ("PASS" if ok else "FAIL", name), flush=True)
    return bool(ok)


def main():
    results = []

    # [1] EntityBinder -- the brain-foundational Stage-1 dispatcher, every route.
    from experiments.world_state_entity_binding import EntityBinder, NARRATOR
    results.append(_p("EntityBinder all routes (self_test)", __import__(
        "experiments.world_state_entity_binding", fromlist=["self_test"]).self_test() == 0))
    b = EntityBinder()
    ok_idx = (b.bind_participant("I")[0] == b.bind_participant("me")[0] == b.bind_participant("my")[0] == NARRATOR)
    results.append(_p("indexical I/me/my -> one narrator node", ok_idx))
    b2 = EntityBinder()
    _t0 = b2.bind_theme("it")            # pleonastic (no antecedent) -> abstain
    b2.bind_theme("cup")                 # nominal -> salient theme
    _t2 = b2.bind_theme("it")            # -> cup
    results.append(_p("object anaphora + pleonastic filter (it->cup only after antecedent)",
                      _t0[0] is None and _t2[0] == "cup"))
    results.append(_p("scope-out we/you abstain (never-confidently-wrong)",
                      b2.bind_participant("we")[0] is None and b2.bind_participant("you")[0] is None))
    he_k, he_r = b2.bind_participant("he", coref_cluster=None)
    results.append(_p("anaphoric he/she abstains when reader coref did not resolve", he_k is None))

    # [2] Stage-2 register core still faithful (the mechanism the parent proved 1.000 on gold).
    from hdlab.world_state_register import self_test as ws_selftest
    results.append(_p("world_state_register CORE (Stage-2 update) faithful", ws_selftest() == 0))

    # [3]/[4] cell self-tests (blind fragments; densified recovers).
    import experiments.exp_world_state_coref_densify_v1 as D
    import experiments.exp_world_state_deixis_object_v1 as X
    results.append(_p("densify cell: blind tracks strings / reader tracks clusters", D.self_test() == 0))
    results.append(_p("deixis/object cell: narrator fragments + object relocates", X.self_test() == 0))

    # [5] LitBank he/she headline (smoke, directional -- CI-separated headline is the full-run number in SOLVED.md).
    rd = D.run(mode="smoke", n_boot=400)
    ph = rd.get("pronoun_holder_subset") or {}
    lit_ok = (rd["n_queries"] > 0 and rd["gold_oracle"]["acc"] == 1.0
              and rd["reader"]["acc"] >= rd["blind"]["acc"] and rd.get("changed_frac", 0) >= 0.5)
    print("      LitBank smoke: blind=%.3f reader=%.3f gold=%.3f changed=%.2f he/she n=%s"
          % (rd["blind"]["acc"], rd["reader"]["acc"], rd["gold_oracle"]["acc"], rd.get("changed_frac", 0), ph.get("n")), flush=True)
    results.append(_p("LitBank: reader-densified >= blind, gold oracle == 1.0, change-point control fires", lit_ok))
    # on smoke the he/she subset may be tiny; assert blind==0 on it WHEN present (the coref-blind failure is total).
    if ph.get("n"):
        results.append(_p("LitBank he/she subset: blind register scores 0.000 (coref-blind cannot key a pronoun holder)",
                          ph["blind"]["acc"] == 0.0 and ph["reader"]["acc"] >= ph["blind"]["acc"]))

    # [6] MCScript2 object-anaphora build-across (smoke, directional).
    rx = X.run(mode="smoke")
    oa = rx["object_anaphora"]
    obj_ok = (oa["n_it_themes"] > 0 and (oa["who_has_what_impact_events"] or 0) > 0
              and (oa["coverage_it_resolvable"] or 0) > 0)
    print("      MCScript2 smoke: it_themes=%d resolvable_cov=%.2f impact=%d/%d"
          % (oa["n_it_themes"], oa["coverage_it_resolvable"] or 0, oa["who_has_what_impact_events"], oa["n_relocated_transfers"]), flush=True)
    results.append(_p("MCScript2: object anaphora relocates transfers blind lost (who-has-what impact > 0)", obj_ok))

    # [7] Object anaphora ACCURACY on REAL LitBank gold (smoke, directional): recency beats the random-twin NULL
    # and the first-mention floor and the reader's coref (which abstains on 'it'); subject-salience does NOT help.
    import experiments.exp_world_state_object_anaphora_gold_v1 as OA
    ro = OA.run(mode="smoke", n_boot=400)
    oa_ok = (ro["n_items"] > 0 and ro["recency"]["acc"] > ro["twin_random_null"]["p95"]
             and ro["recency"]["acc"] > ro["first"]["acc"] and ro["reader_coref_on_it"] == 0.0
             and ro["recency"]["acc"] >= ro["recency_nonumber"]["acc"]      # PINNED number-agreement helps
             and ro["recency"]["acc"] >= ro["salience"]["acc"])             # subject-salience does not help objects
    print("      Object-anaphora gold smoke: recency=%.3f (no-number=%.3f) first=%.3f salience=%.3f twin_p95=%.3f reader_it=%.1f"
          % (ro["recency"]["acc"], ro["recency_nonumber"]["acc"], ro["first"]["acc"], ro["salience"]["acc"], ro["twin_random_null"]["p95"], ro["reader_coref_on_it"]), flush=True)
    results.append(_p("Object anaphora on LitBank gold: recency > twin-NULL/first-floor, reader abstains, number-agreement helps, subject-salience does not", oa_ok))

    # [8] Ceiling-lift (smoke, directional): the landed brain-faithful graded retrieval (ACT-R + pool cleanup)
    # beats recency and hard-tier over the IDENTICAL candidate pool (isolated pick lift), and beats the reader's
    # current resolver -- quantifying that the register's he/she ceiling (0.5) can rise. Fair pick-only + upper bound.
    import experiments.exp_world_state_he_she_ceiling_v1 as CE
    rc = CE.run(mode="smoke", n_boot=400)
    al = rc["ALL_he_she_targets"]
    ce_ok = (al["n"] > 0 and al["graded"]["acc"] > al["recency"]["acc"] and al["graded"]["acc"] > al["hard_tier"]["acc"]
             and al["graded"]["acc"] > al["reader"]["acc"] and al["graded"]["acc"] > al["twin_null"]["p95"])
    print("      Ceiling-lift smoke (all he/she n=%d): reader=%.3f graded=%.3f recency=%.3f hard=%.3f"
          % (al["n"], al["reader"]["acc"], al["graded"]["acc"], al["recency"]["acc"], al["hard_tier"]["acc"]), flush=True)
    results.append(_p("Ceiling-lift: graded (ACT-R, landed) > recency AND > hard-tier AND > reader's current resolver", ce_ok))
    # confidence-abstain (#4): accuracy-when-committed RISES as the register abstains on high-entropy coref.
    abst = rc.get("abstain_lifts_precision", False)
    dr = rc.get("graded_residual_drill", {})
    print("      Confidence-abstain lifts precision=%s ; residual: dist wrong=%s vs right=%s (far-antecedent wall)"
          % (abst, dr.get("mean_dist_when_wrong"), dr.get("mean_dist_when_right")), flush=True)
    results.append(_p("Confidence-abstain: committing on low-entropy graded picks raises who-has-what precision (never-confidently-wrong)", bool(abst)))

    # [9] END-TO-END combined who-has-what (smoke): the FULL binder vs the coref-blind register on MCScript2 with
    # deterministic gold. blind is far below full/gold; object anaphora adds a CI-sep increment over blind+idx;
    # change-point fires; gold == 1.0 by construction.
    import experiments.exp_world_state_endtoend_whohaswhat_v1 as EE
    re = EE.run(mode="smoke", n_boot=400)
    ee_ok = (re["n_questions"] > 0 and re["gold"]["acc"] == 1.0 and re["full"]["acc"] > re["blind"]["acc"]
             and re["full_beats_blind_CIsep"] and re.get("changed_frac", 0) >= 0.5)
    print("      End-to-end smoke (n=%d Qs): blind=%.3f blind+idx=%.3f full=%.3f gold=%.3f (full-blind CI-sep %s)"
          % (re["n_questions"], re["blind"]["acc"], re["blind_idx"]["acc"], re["full"]["acc"], re["gold"]["acc"], re["full_beats_blind_CIsep"]), flush=True)
    results.append(_p("End-to-end who-has-what: full binder >> coref-blind (CI-sep), gold==1.0, change-point fires", ee_ok))

    # [10] GROUPING optimization: the he/she headroom is dominated by PRONOUN-CHAINING (gold >> gold_nom), NOT name
    # unification (aliaser barely beats surface) -- the ceiling-lift correction.
    import experiments.exp_world_state_grouping_optimize_v1 as GO
    rg = GO.run(mode="smoke", n_boot=300)
    go_ok = (rg["gold"]["acc"] > rg["gold_nom"]["acc"] > 0 and rg["gold"]["acc"] > rg["aliaser"]["acc"]
             and rg["aliaser"]["acc"] >= rg["surface"]["acc"]
             and (rg["gold"]["acc"] - rg["gold_nom"]["acc"]) > (rg["aliaser"]["acc"] - rg["surface"]["acc"]))
    print("      Grouping smoke: surface=%.3f aliaser=%.3f gold_nom=%.3f gold=%.3f (pronoun-chaining=%.3f > name-unif=%.3f)"
          % (rg["surface"]["acc"], rg["aliaser"]["acc"], rg["gold_nom"]["acc"], rg["gold"]["acc"],
             rg["gold"]["acc"] - rg["gold_nom"]["acc"], rg["aliaser"]["acc"] - rg["surface"]["acc"]), flush=True)
    results.append(_p("Grouping: he/she headroom is dominated by PRONOUN-CHAINING (gold>>gold_nom), not name unification", go_ok))

    # [11] DOWNSTREAM benefit: a who-has-what QA consumer answers far better off the densified register than blind.
    import experiments.exp_world_state_downstream_v1 as DS
    rds = DS.run(mode="smoke", n_boot=300)
    ds_ok = (rds.get("n_qa", 0) > 0 and rds["qa_densified"]["acc"] > rds["qa_blind"]["acc"])
    print("      Downstream smoke: who-has-what QA blind=%.3f -> densified=%.3f ; bridging false-flag blind=%s -> dens=%s"
          % (rds["qa_blind"]["acc"], rds["qa_densified"]["acc"], rds.get("blind_FALSE_impossible_flag_rate"),
             rds.get("densified_FALSE_impossible_flag_rate")), flush=True)
    results.append(_p("Downstream who-has-what QA consumer: densified register answers >> blind", ds_ok))

    # [12] POWERED bridging / impossible-action detection (balanced, injected violations): the coref-blind register
    # FALSE-flags possible actions (below the always-possible majority floor); densification fixes it.
    import experiments.exp_world_state_bridging_powered_v1 as BR
    rb = BR.run(mode="smoke", n_boot=300)
    br_ok = (rb["n_probes"] > 0 and rb["balanced_acc_densified"] > rb["balanced_acc_blind"]
             and rb["densified_false_flag_rate_on_VALID"] < rb["blind_false_flag_rate_on_VALID"]
             and rb["blind"]["acc"] < rb["majority_floor_always_possible"])
    print("      Powered bridging smoke: blind bal=%.3f dens bal=%.3f ; false-flag blind=%.3f->dens=%.3f ; blind acc %.3f < floor %.3f"
          % (rb["balanced_acc_blind"], rb["balanced_acc_densified"], rb["blind_false_flag_rate_on_VALID"],
             rb["densified_false_flag_rate_on_VALID"], rb["blind"]["acc"], rb["majority_floor_always_possible"]), flush=True)
    results.append(_p("Powered bridging: coref-blind FALSE-flags possible actions (below majority floor); densification fixes it", br_ok))

    # binder self-test now includes CONFIDENCE-ABSTAIN (defer on high-entropy coref) -- covered by check [1].
    n_ok = sum(results); n = len(results)
    print("\n[witness] %d/%d checks PASS" % (n_ok, n), flush=True)
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
