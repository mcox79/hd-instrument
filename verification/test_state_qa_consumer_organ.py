"""Scaffold-free witness for wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states.

Drives the state-QA CONSUMER + the copular producer from SOURCE and asserts every headline. NO external LLM.
Glass-box. The consumer routes "what/who is X" / "is X a Y" to the entity-STATE dimension and reads the
is-a/attribute off sm.state_register (the landed, default-off bind_entity_states capability), and it is proven
CI-separated over the copular problem's VALIDATED most-recent-noun floor with the SHUFFLE-holder twin LOSING.

  W1  LIVE ZERO (can-fail): the base reader (bind_entity_states OFF) has no state register, so the state QA
      scores 0 on predicate complements -- the live zero the wire must beat.
  W2  POWERED qa_state: on the copular problem's NON-CIRCULAR UD-EWT predicational gold, the MODEL (route +
      state_register readout) beats the most-recent-noun floor CI-separated.
  W3  INFO-FREE TWIN LOSES: the shuffle-holder twin (the copular-validated info-free control) loses CI-sep.
  W4  ROUTER (brain-faithful copular frame): "what/who is X" / "is X a Y" -> state; the frame does NOT steal
      salience / coref-pronoun / where / believe; ablating the frame (router off) collapses the answer to 0.
  W5  NO-REGRESSION: bind_entity_states is ADDITIVE -- the 4 scored dims (events/coref/timeline/causal) are
      byte-identical on the CAPABLE reader with the flag OFF vs ON (so turning it on cannot regress them).
  W6  BOARD PICKUP: exp_situation_model_qa_v1.run emits per_dimension["state"] (auto-visible on the baseline
      board's Instrument A) with a CI, and aggregate_including_state shows a non-negative flag-on move.
  W7  WATERFALL: read-back GIVEN the binding ~= 1.0 -> the CONSUMER adds ~0 loss; the residual is UPSTREAM
      detection (the producer's mapped gap), which is where we still differ from the brain.
  W8  LIVE-FIRES on 19c prose: on real LitBank docs the consumer answers M>0 state questions the base reader
      could not (a coverage demonstration on the reading corpus; reader-derived gold -> not a floor claim).
  W9  BOTH REQUIRED CHANGES: the upstream-detection fix (robust_cop) lifts qa_state CI-sep through the consumer,
      and the arc-eager tree optimization adds CI-sep on top (label 0.71 -> robust_cop 0.83 -> arc-eager 0.87).

Run: .venv/Scripts/python.exe verification/test_state_qa_consumer_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_state_qa_v1 as STATE
import experiments.exp_situation_model_qa_v1 as QA
from hdlab.situation_reader import SituationReader
import experiments.exp_name_entity_clustering_v1 as NC
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

import json

FAILS = []
CAP = 1200   # UD-EWT sentences for the powered state measurement (CI-separates comfortably; ~20s)


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    res = STATE.run(cap=CAP, n_boot=1000)

    # W1 -- the live zero (base reader OFF).
    check("W1 live zero: base reader (bind OFF) scores 0 on state questions",
          res["base_reader_off_zero"] == 0.0,
          "off=%.4f (n_pred=%d)" % (res["base_reader_off_zero"], res["n_pred_clauses"]))

    # W2 -- powered qa_state CI-separated over the most-recent-noun floor.
    mf = res["model_vs_floor"]
    check("W2 qa_state beats the most-recent-noun floor CI-separated",
          mf["ci_sep"] and res["qa_state_model"] > res["positional_floor"],
          "model %.4f vs floor %.4f  d=%+.4f CI[%+.4f,%+.4f]" %
          (res["qa_state_model"], res["positional_floor"], mf["delta"], mf["lo"], mf["hi"]))

    # W3 -- shuffle-holder twin loses CI-separated.
    mt = res["model_vs_shuffle_twin"]
    check("W3 info-free shuffle-holder twin LOSES CI-separated",
          mt["ci_sep"] and res["qa_state_model"] > res["shuffle_holder_twin"],
          "model %.4f vs twin %.4f  d=%+.4f CI[%+.4f,%+.4f]" %
          (res["qa_state_model"], res["shuffle_holder_twin"], mt["delta"], mt["lo"], mt["hi"]))

    # W4 -- the brain-faithful copular-frame router.
    r_ok = (QA.route("What is Ahab ?") == "state" and QA.route("What is it ?") == "state"
            and QA.wh_ontology_route("What is Ahab ?") == "state")
    r_guard = (QA.route("Who is the main character ?") == "salience"
               and QA.route("Who is 'he' ?") != "state"
               and QA.route("Where is John ?") == "location"
               and QA.route("What does Mary believe ?") == "belief")
    check("W4 router: copular frame -> state; does not steal salience/coref/where/believe; ablation collapses",
          r_ok and r_guard and res["router_state_hit_rate"] > 0.98 and res["router_ablation"] == 0.0,
          "hit=%.3f ablation=%.3f" % (res["router_state_hit_rate"], res["router_ablation"]))

    # W5 -- NO-REGRESSION: the 4 scored dims byte-identical with the flag off vs on (additive).
    gaz = load_given_gazetteer()
    docs = [r["doc"] for r in json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"),
                                             encoding="utf-8"))][:5]

    def core(sm):
        return ([(e.global_idx, str(e.predicate), str(e.agent), str(e.patient), str(e.tense)) for e in sm.events],
                [(x.pronoun, x.resolved_cluster, x.sent_idx) for x in sm.coref_resolutions],
                [(y.get("lemma"), y.get("chrono_rank")) for y in (sm.timeline_order or [])],
                [(str(c.cause), str(c.outcome)) for c in sm.causal_links])
    nr_ok = True
    for d in docs:
        p = os.path.join(NC.CONLL_DIR, d + ".conll")
        if not os.path.exists(p):
            continue
        off = SituationReader(gaz=gaz, bind_entity_states=False).read(p)
        on = SituationReader(gaz=gaz, bind_entity_states=True).read(p)
        nr_ok &= (core(off) == core(on)) and (off.state_register is None) and (on.state_register is not None)
    check("W5 no-regression: 4 scored dims byte-identical bind OFF vs ON (flag is additive)", nr_ok)

    # W6 -- board pickup: run() emits per_dimension["state"] + a non-negative aggregate move.
    qres = QA.run(QA.load_docs(3), state_cap=800)
    sd = qres["per_dimension"].get("state")
    ais = qres.get("aggregate_including_state", {})
    board_ok = (sd is not None and sd.get("n", 0) > 30 and sd.get("ci_sep_over_strongest")
                and sd.get("ci_sep_over_twin") and sd["model_acc"] > sd["strongest_floor"]
                and ais.get("delta_from_turning_on", -1) >= 0)
    check("W6 board pickup: per_dimension['state'] row CI-sep + qa_aggregate non-negative flag-on move",
          board_ok, "state model=%s floor=%s twin=%s ; agg off %s -> on %s" %
          (sd and sd.get("model_acc"), sd and sd.get("strongest_floor"), sd and sd.get("twin_acc"),
           ais.get("flag_off"), ais.get("flag_on")))

    # W7 -- waterfall: read-back given the binding ~= 1.0 (consumer lossless; residual is upstream).
    w = res["waterfall"]
    check("W7 waterfall: read-back GIVEN the binding ~= 1.0 (consumer adds ~0 loss; residual is upstream)",
          w["readback_given_binding"] > 0.95,
          "brain~1.0 -> binding %.3f -> routing %.3f -> read-back|binding %.3f" %
          (w["binding_recall_upstream"], res["router_state_hit_rate"], w["readback_given_binding"]))

    # W8 -- live-fires on real 19c prose (coverage; base reader answers 0).
    cov = STATE.litbank_coverage(n_docs=8)
    check("W8 live-fires on 19c LitBank: the consumer answers state questions the base reader could not",
          cov["n_state_questions"] > 20 and cov["answered_roundtrip"] > 0,
          "answered %d/%d (roundtrip %.3f) over %d docs" %
          (cov["answered_roundtrip"], cov["n_state_questions"], cov["roundtrip_rate"], cov["n_docs"]))

    # W9 -- BOTH REQUIRED CHANGES, POST-LANDING. CHANGE 2 (robust_cop) is now the reader's DEFAULT entity-state
    # detection (situation_reader._read_entity_states unions the label path with robust_cop unconditionally), so the
    # +0.12 fix is BAKED INTO res["qa_state_model"] (the reader-default arm now == the robust_cop fix level; the
    # PRE-landing label-only 0.701 is no longer reachable through the live reader). Assert the LANDED reality: the
    # reader default IS at the robust_cop level (CI-sep over the floor), and the arc-eager tree optimization still
    # adds CI-sep on top. (Pre-landing this row read label 0.701 -> robust_cop 0.826 -> arc-eager 0.848, 9/9 --
    # the solver's submission proof; landing CHANGE 2 collapses the label/robust_cop distinction BY DESIGN.)
    uf = res["upstream_fix"]
    opt = STATE.optimize_upstream(cap=800, n_boot=1000)
    landed_at_fix = abs(res["qa_state_model"] - uf["qa_state_fix"]) < 0.02
    check("W9 robust_cop LANDED as the reader default (qa_state at the fix level, CI-sep over floor) + arc-eager on top",
          landed_at_fix and res["model_vs_floor"]["ci_sep"]
          and opt["arceager_vs_july"]["ci_sep"] and opt["qa_state_fix_arceager"] > opt["qa_state_fix_july"],
          "reader-default %.3f == robust_cop fix %.3f (LANDED) ; arc-eager %.3f (d=%+.3f CI-sep on top)" %
          (res["qa_state_model"], uf["qa_state_fix"],
           opt["qa_state_fix_arceager"], opt["arceager_vs_july"]["delta"]))

    print("\n==== STATE-QA CONSUMER WITNESS: %d/9 ====" % (9 - len(FAILS)), flush=True)
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)


if __name__ == "__main__":
    main()
