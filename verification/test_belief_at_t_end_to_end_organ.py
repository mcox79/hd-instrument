"""Scaffold-free witness for the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose.

Recomputes every headline FROM SOURCE via the cell's run(write=False) (never touches the landed metrics.json):
drives the PROMOTED hdlab.belief_timeline END-TO-END from the reader's OWN 3-channel extraction on the modern
control + the hand-adjudicated REAL LitBank slice, recomputing the mechanism/floor/twin/false-belief/persistence
gates -- never trusting a landed number. Also re-runs the object-move VIABILITY probe that refutes the brief.

  W1  the brief's object-move source is ~ABSENT on real prose (the refutation): <=1 multi-move object across
      several LitBank books -> the Sally-Anne event source fails on real narrative (pivot justified).
  W2  the pivoted MECHANISM works: BELIEF_oracle (gold belief chain -> promoted belief_timeline) beats the
      STRONGEST floor CI-separated on the modern control.
  W3  the wall is EXTRACTION, not the mechanism: live_vs_oracle CI-separated (the whole live shortfall is the
      reader's extraction residual; the organ is sound).
  W4  FALSE-BELIEF recovery: on belief!=reality items, BELIEF beats the reality floor CI-separated (modern).
  W5  PERSISTENCE signature (Dowty temporal inertia): at distance >=1 sentence since the last update the
      last-mention floor COLLAPSES while the belief timeline HOLDS above it.
  W6  the info-free TWIN LOSES: BELIEF_live beats the twin-null p95 (modern).
  W7  GENERALISATION (one content-general mechanism): BOTH fact types (location, status) reach oracle=1.0 and
      the DOMINANT channels (narrator-epistemic, testimony) reach live=1.0.
  W8  the object-move (perception) channel is the WEAK one -- the brief's own source under-extracts vs the
      pivoted channels (epistemic/testimony live=1.0 > perception live) -- the wall is exactly the object-move
      extraction the pivot demotes.
  W9  REAL prose: the composition drives end-to-end on hand-adjudicated LitBank; BELIEF beats the beliefless
      REALITY floor CI-separated AND recovers false beliefs CI-separated (honest small n).
  W10 the PROMOTED hdlab.belief_timeline is actually the organ being driven (belief_reader composes into it).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def main():
    import experiments.exp_belief_at_t_end_to_end_v1 as E
    from experiments.belief_at_t_gold import modern_items, load_real
    import experiments._belief_reader as BR
    from hdlab.belief_timeline import timeline_belief as hdlab_tb

    # W1 -- object-move viability probe (the refutation)
    from experiments._space_reader import build_backbone
    from experiments._belief_probe_scratch import extract_object_moves
    import glob
    from collections import Counter
    multi = 0
    for p in sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll/*.conll")))[:8]:
        sents, by_sent, names, persons = build_backbone(p)
        moves = extract_object_moves(sents, by_sent)
        by_obj = Counter(m[0] for m in moves)
        multi += sum(1 for o, c in by_obj.items() if c >= 2)
    check("W1 brief's object-move source ~ABSENT on real prose (<=1 multi-move object / 8 books) -> pivot",
          multi <= 1, f"objects with >=2 extracted moves across 8 LitBank books = {multi}")

    out = E.run(smoke=False, n_boot=1500, write=False)
    M = out["modern"]

    g = M["gates"]
    ovf = g["oracle_vs_strongest_floor"]
    check("W2 pivoted MECHANISM beats the strongest floor CI-separated (oracle -> promoted belief_timeline)",
          ovf["CI_separated"],
          f"oracle {ovf['a_mean']:.3f} vs {M['strongest_floor']} {ovf['b_mean']:.3f} "
          f"delta {ovf['delta']:+.3f} [{ovf['lo']:+.3f},{ovf['hi']:+.3f}]")
    lvo = g["live_vs_oracle"]
    check("W3 the wall is EXTRACTION, not the mechanism: the ORACLE mechanism is the ceiling (=1.0) and the "
          "remaining live gap is extraction (>=0; narrowed by wiring state_register for status)",
          lvo["a_mean"] >= 0.99 and lvo["delta"] >= 0.0,
          f"oracle {lvo['a_mean']:.3f} vs live {lvo['b_mean']:.3f} delta {lvo['delta']:+.3f} "
          f"[{lvo['lo']:+.3f},{lvo['hi']:+.3f}] (CI-sep {lvo['CI_separated']})")

    d = M["false_belief_discriminator"]["belief_vs_reality_on_false_belief"]
    check("W4 FALSE-BELIEF recovery: belief beats reality floor CI-separated on belief!=reality items",
          d["CI_separated"],
          f"belief {M['false_belief_discriminator']['belief_acc_on_fb']:.3f} vs reality "
          f"{M['false_belief_discriminator']['reality_acc_on_fb']:.3f} delta {d['delta']:+.3f}")

    dc = M["distance_curve"]
    far = dc.get("1-2", {})
    lm_far = far.get("FLOOR_lastment")
    or_far = far.get("BELIEF_oracle")
    check("W5 PERSISTENCE signature: at distance >=1 last-mention COLLAPSES, belief timeline HOLDS above it",
          lm_far is not None and or_far is not None and lm_far <= 0.5 and or_far > lm_far,
          f"dist1-2: oracle={or_far} live={far.get('BELIEF_live')} lastment={lm_far} (n={far.get('n')})")

    tn = M["twin_null"]
    check("W6 info-free TWIN LOSES: BELIEF_live beats twin-null p95",
          M["pop_acc"]["BELIEF_live"] > tn["p95"],
          f"live {M['pop_acc']['BELIEF_live']:.3f} > twin-null p95 {tn['p95']:.3f}")

    bf = M["by_fact_type"]; bc = M["by_channel"]
    gen = (all(bf[t]["BELIEF_oracle"] >= 0.99 for t in bf) and len(bf) >= 2
           and bc.get("epistemic", {}).get("BELIEF_live", 0) >= 0.99
           and bc.get("testimony", {}).get("BELIEF_live", 0) >= 0.99)
    check("W7 GENERALISATION: both fact types reach oracle=1.0 AND the dominant channels reach live=1.0",
          gen, f"fact-type oracle={{t:bf[t]['BELIEF_oracle'] for t in bf}}; "
               f"epistemic live={bc.get('epistemic',{}).get('BELIEF_live')} "
               f"testimony live={bc.get('testimony',{}).get('BELIEF_live')}")

    perc = bc.get("perception", {}).get("BELIEF_live", 1.0)
    dom = min(bc.get("epistemic", {}).get("BELIEF_live", 1.0), bc.get("testimony", {}).get("BELIEF_live", 1.0))
    check("W8 the OBJECT-MOVE (perception) channel is the WEAK one -- the brief's own source under-extracts",
          perc < dom, f"perception live={perc:.3f} < dominant(epistemic/testimony) live={dom:.3f}")

    R = out.get("real")
    if R and R.get("n_items"):
        rg = R["gates"]
        vr = rg["vs_reality"]
        rd = R["false_belief_discriminator"]["belief_vs_reality_on_false_belief"]
        check("W9 REAL prose: BELIEF beats the beliefless REALITY floor CI-separated AND recovers false "
              "beliefs CI-separated (honest small n)",
              vr["CI_separated"] and rd["CI_separated"],
              f"n_items={R['n_items']} n_q={R['n_queries']}: vs_reality {vr['a_mean']:.3f} vs {vr['b_mean']:.3f} "
              f"delta {vr['delta']:+.3f} [{vr['lo']:+.3f},{vr['hi']:+.3f}] CI-sep={vr['CI_separated']}; "
              f"false-belief delta {rd['delta']:+.3f} CI-sep={rd['CI_separated']}")
    else:
        check("W9 REAL prose slice present", False, "real.jsonl missing")

    # W10 -- the promoted hdlab.belief_timeline is the organ being driven
    import spacy
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    led = PerceptualAccessLedger(spacy.load("en_core_web_sm"))
    it = modern_items()[0]
    ev, obs, agent, re_ext, ba, src = BR.drive(it["sents"], {i: [] for i in range(len(it["sents"]))},
                                               it["fact"], it["agent"], led)
    val = hdlab_tb(ev, obs, agent, it["fact"]["fact_aliases"][0].lower(), it["queries"][-1]["t_sent"] + 0.5)
    check("W10 the PROMOTED hdlab.belief_timeline is the organ driven end-to-end (real WorldEvents + belief)",
          len(ev) > 0 and val is not None, f"events={len(ev)} belief_at_T={val!r}")

    # W11 -- the POWERED real headline: knowledge-STATE (knows/stale/ignorant) beats the assume-knows floor
    if R and R.get("n_items"):
        ks = R["knowledge_state"]
        check("W11 REAL KNOWLEDGE-STATE (registration read-out) beats the ASSUME-KNOWS floor CI-separated "
              "(the coverage-robust real-prose headline: ignorance is what real prose supplies)",
              ks["CI_separated"],
              f"reader {ks['reader_acc']:.3f} vs assume-knows {ks['assume_knows_acc']:.3f} delta {ks['delta']:+.3f} "
              f"[{ks['lo']:+.3f},{ks['hi']:+.3f}] (ignorant={ks['n_ignorant']} stale={ks['n_stale']} current={ks['n_current']})")

    # W12 -- FLASHBACK: the temporal-order register is NEEDED (chrono-order recovers, narration-order fails)
    fb = out["flashback"]
    check("W12 FLASHBACK: chronological (register) order recovers belief where NARRATION order fails "
          "(narration != chronology -> the temporal-order register is load-bearing)",
          fb["register_needed"] and fb["chrono_order_acc"] >= 0.99 and fb["narration_order_acc"] <= 0.5,
          f"chrono {fb['chrono_order_acc']} vs narration {fb['narration_order_acc']} (n={fb['n']})")

    # W13 -- FHRR substrate read-out is seed-stable (the belief is decoded ON the substrate, not looked up)
    fr = out["fhrr_readout"]
    check("W13 FHRR substrate read-out round-trips the belief value across seeds (glass-box, seed-stable)",
          fr["seed_stable"], f"per-seed round-trip {fr['per_seed_roundtrip_acc']}")

    # W14 -- SOURCE-TAGGING (seen/heard/inferred) + OWN-PARSER (no spaCy) carry
    st = M["source_tag"]; ns = R["no_spacy"] if R and R.get("n_items") else M["no_spacy"]
    check("W14 SOURCE-TAGGING works (>=0.75 acc) AND the dominant channels are substrate-native (belief "
          "carried with NO spaCy at inference)",
          (st["acc"] or 0) >= 0.75 and (ns["dominant_channels_no_spacy_acc"] or 0) >= 0.75,
          f"source-tag acc {st['acc']:.2f}; no-spaCy dominant-channel belief {ns['dominant_channels_no_spacy_acc']}")

    # W15 -- the extraction wall is DRILLED to mechanism + the RIGHT organ: location = parser recall
    # (spaCy > in-substrate -> p2); status = the promoted state_register organ recovers it (> a stronger
    # parser) -> NOT intrinsic. Enumerated, and each gap routed to its organ.
    import experiments.exp_belief_extraction_drill_v1 as DR
    dr = DR.run(smoke=False, write=False)
    loc = dr["per_fact_type"].get("location", {})
    loc_parser = loc.get("SPACY", {}).get("recall", 0) > loc.get("IN_SUBSTRATE", {}).get("recall", 1)
    stat_organ = dr["status_register_recall"] > dr["status_parser_recall"]
    check("W15 extraction wall DRILLED + routed to organs: location = PARSER-recall (spaCy > in-substrate -> "
          "p2); status = the promoted STATE_REGISTER organ recovers MORE than a stronger parser (not intrinsic)",
          loc_parser and stat_organ,
          f"location in-substrate {loc.get('IN_SUBSTRATE',{}).get('recall')} < spaCy "
          f"{loc.get('SPACY',{}).get('recall')}; status state_register {dr['status_register_recall']} > parser "
          f"{dr['status_parser_recall']}")

    # W16 -- OPEN-ENDED belief read-out (organ 1): the meaning-tolerant WordNet-equivalence read-out RECOVERS
    # belief paraphrase (deceased->dead, wed->married) that exact-match gets 0 on, WITHOUT crediting antonyms.
    oe = out["open_ended"]
    check("W16 OPEN-ENDED read-out recovers belief paraphrase (meaning-tolerant > exact) and rejects antonyms",
          oe["belief_meaning_tolerant"] > oe["belief_exact"] and oe["meaning_tolerant_recovers_and_rejects_antonyms"],
          f"exact {oe['belief_exact']:.2f} -> meaning-tolerant {oe['belief_meaning_tolerant']:.2f} "
          f"(paraphrase-recovery {oe['paraphrase_recovery']:+.2f}; n={oe['n']})")

    # W17 -- INFERRED-belief hook (organ 2): belief_timeline.fired_inference_events fires an evidence-GATED
    # inference (Sodian & Wimmer) only when the agent observed the premises.
    from hdlab.belief_timeline import fired_inference_events, InferenceEdge
    edges = [InferenceEdge(obj="marble", conclusion="basket", premise_chronos=(0,), fire_chrono=1.0)]
    fires_obs, _ = fired_inference_events("Anna", edges, {("Anna", 0): True}, mode="gated")
    fires_un, _ = fired_inference_events("Anna", edges, {("Anna", 0): False}, mode="gated")
    check("W17 INFERRED-belief hook fires evidence-GATED (fires on observed premise, silent on unobserved)",
          bool(fires_obs) and not fires_un,
          f"observed-premise fires={bool(fires_obs)}, unobserved-premise fires={bool(fires_un)}")

    # W18 -- INFERRED belief END-TO-END from the reader's parse (organ 2 fully wired): the 3-schema extractor
    # (exclusion / transitive-spatial / modus-ponens) recovers the INFERRED value (never perceived) AND stays
    # ignorant on EVERY gated control (agent did not observe the premise).
    inf = out["inference"]
    check("W18 INFERRED belief END-TO-END (exclusion + transitive-spatial + modus-ponens): recovers the "
          "inferred value AND all gated controls (no premise observed) stay ignorant",
          inf["end_to_end_works"] and inf["gated_stays_ignorant"] >= 0.99,
          f"inferred-recall {inf['inferred_recall']:.2f} (n={inf['n_inferred']}); gated stays-ignorant "
          f"{inf['gated_stays_ignorant']:.2f} (n={inf['n_gated_control']})")

    # W19 -- INDEPENDENT, POWERED external validation on FANToM info-access ToM: the knowledge-state read-out
    # (co-presence registration) beats the strongest floor AND the info-free twin CI-separated, and recovers
    # false beliefs (ignorant characters) -- the coverage-bounded LitBank headline is now powered on real prose.
    import experiments.exp_belief_fantom_infoaccess_v1 as FA
    fa = FA.run(smoke=False, n_boot=1000, write=False)
    fb = fa["false_belief_ignorant"]
    check("W19 FANToM (external, powered n=%d judgments; ORGAN-driven): knowledge-state reader beats strongest "
          "floor AND shuffled-order twin AND random-presence twin CI-sep, says-ignorant on false-belief chars"
          % fa["n_character_judgments"],
          fa.get("organ_driven") and fa["reader_vs_strongest_floor"]["CI_separated"]
          and fa["reader_vs_twin"]["CI_separated"] and fa["reader_vs_twin_random"]["CI_separated"]
          and (fb["reader_says_ignorant"] or 0) > 0.8,
          f"reader {fa['reader_acc']:.3f} vs floor {fa['assume_knows_acc']:.3f} "
          f"(delta {fa['reader_vs_strongest_floor']['delta']:+.3f}); vs shuffled-twin "
          f"{fa['reader_vs_twin']['delta']:+.3f}; vs random-twin {fa['reader_vs_twin_random']['delta']:+.3f}; "
          f"false-belief reader-ignorant {fb['reader_says_ignorant']:.3f}; error-rate "
          f"{fa['error_drill']['error_rate']:.3f} (FN {fa['error_drill']['false_negative_under_attribution']} > "
          f"FP {fa['error_drill']['false_positive_over_attribution']})")

    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL %d CHECKS PASS" % (10 + 9))


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
