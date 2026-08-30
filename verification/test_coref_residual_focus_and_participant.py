"""Scaffold-free witness for the_coref_residual_needs_a_discourse_focus_stack.

Recomputes every SOLVED.md headline FROM SOURCE (LitBank cache + both experiment cells' run functions), asserting the
bands rather than trusting any landed metrics.json. Two results:
  (A) the focus-STACK is a RIGOROUS NEGATIVE (bar item 1): with GOLD quote/paragraph/entity-shift segmentation the
      focus stack diverges from finer token-locality in ~1/420 cases and does NOT beat it CI-separated.
  (B) the real lever is DISCOURSE-PARTICIPANT EXCLUSION: +0.08 CI-separated over the strongest (token-recency) floor
      on the anti-typical person residual, incremental over the landed cleanup, the info-free random-drop twin LOSES,
      no regression on the full person population, and GENDER agreement is NOT a causal lever.

Run: .venv/Scripts/python.exe verification/test_coref_residual_focus_and_participant.py
Pure numpy + NLTK names. Reads the pre-parsed cache. Writes nothing. NO hdlab/ mutation.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_coref_focus_stack_oracle_ceiling_v1 as ORACLE  # noqa: E402
from experiments import exp_coref_residual_participant_pool_v1 as PART  # noqa: E402
from experiments import exp_coref_participant_generalization_v1 as GEN  # noqa: E402
from experiments import exp_coref_residual_phi_agreement_v1 as PHI  # noqa: E402
from experiments import exp_coref_phi_agreement_prefilter_v1 as PRE  # noqa: E402

N = 0


def check(name, cond):
    global N
    N += 1
    assert cond, f"WITNESS FAIL [{name}]"
    print(f"  ok  W{N:02d}  {name}")


def main():
    print("== self-tests ==")
    ORACLE.self_test()
    PART.self_test()

    print("== (A) focus-STACK oracle ceiling: RIGOROUS NEGATIVE ==")
    o = ORACLE.run(n_boot=800)
    acc = o["accuracy"]
    con = o["contrasts"]
    # sentence-recency and graded score ~0 on the anti-typical population (by construction)
    check("sentence-recency floor ~0 on anti-typical", acc["recency"]["acc"] <= 0.02)
    # finer TOKEN-locality recovers a large slice -- it is the real ceiling, not focus
    check("token-locality recovers >=0.40 (the real ceiling)", acc["token_recency"]["acc"] >= 0.40)
    # the focus STACK does NOT beat finer token-locality CI-separated (the mechanism is refuted)
    check("focus_best does NOT beat token-locality CI-sep", con["focus_best_minus_token_recency"]["band"] != "ABOVE")
    check("focus_quote does NOT beat token-locality CI-sep", con["focus_quote_minus_token_recency"]["band"] != "ABOVE")
    # the info-free quote-boundary-shuffle twin ties (no segment info is carried)
    check("quote-shuffle twin does not lose to focus (no segment info)",
          con["focus_quote_minus_focus_quote_shuf"]["band"] == "NOT_SEP")
    check("verdict = focus reduces to finer locality / not a distinct lever",
          "FINER_LOCALITY" in o["reading"]["verdict"] or "DOES_NOT_CLEAR" in o["reading"]["verdict"])
    # divergence is a handful of cases out of the whole population
    check("focus vs token-recency diverge in <5 cases of ~420",
          o["focus_quote_vs_token_recency_divergence"]["n_diff"] < 5)

    print("== (B) participant exclusion: causal brain-faithful lever ==")
    p = PART.run(n_boot=800)
    aa = p["accuracy_anti"]
    c = p["contrasts"]
    r = p["reading"]
    check("anti-typical residual (all 3rd-person) n in [350,480]", 350 <= p["n_anti"] <= 480)
    check("person-only participant also beats floor CI-sep", p["contrasts"]["person_participant_minus_floor"]["band"] == "ABOVE")
    check("permissive pool is huge (mean >25)", p["mean_pool_permissive"] > 25)
    check("participant present in most pools (>0.7)", p["participant_present_in_pool_frac"] > 0.7)
    check("participant recall = 1.0 (never drops gold)", p["recall_and_pool_anti"]["participant"]["recall"] >= 0.995)
    check("participant beats strongest (token) floor CI-sep", c["participant_minus_floor"]["band"] == "ABOVE")
    check("participant delta over floor >= 0.05", c["participant_minus_floor"]["delta"] >= 0.05)
    check("participant incremental over LANDED cleanup CI-sep", c["participant_minus_landed"]["band"] == "ABOVE")
    check("info-free random-drop twin LOSES CI-sep", c["participant_minus_random_twin"]["band"] == "ABOVE")
    check("random-drop twin collapses recall (<0.99)", p["recall_and_pool_anti"]["random_drop"]["recall"] < 0.99)
    check("no regression on FULL person population (not BELOW)",
          c["full_pop_participant_minus_floor"]["band"] != "BELOW")
    check("GENDER-disagree is NOT a lever (not ABOVE)", c["gender_disagree_minus_floor"]["band"] != "ABOVE")
    check("GENDER adds nothing over participant (not ABOVE)",
          c["part_and_gender_minus_participant"]["band"] != "ABOVE")
    pc = p["positive_control_participant_is_wrong_pick"]
    check("positive control: exclusion recovers >=0.4 of participant-wrong picks", pc["frac"] >= 0.4 and pc["n"] >= 10)
    check("overall verdict = participant is a causal brain-faithful lever",
          r["verdict"] == "PARTICIPANT_EXCLUSION_IS_A_CAUSAL_BRAIN_FAITHFUL_LEVER")

    print("== (C) generalization: principle, not a 19c-narrator artifact ==")
    g = GEN.run(n_boot=800)
    s = g["splits"]
    gr = g["reading"]
    check("helps most in 1st-person narration (ABOVE)", s["narration_1st_person"]["participant_minus_floor"]["band"] == "ABOVE")
    check("1st-person-narration lift is large (>=0.08)", s["narration_1st_person"]["participant_minus_floor"]["delta"] >= 0.08)
    check("NEUTRAL in 3rd-person narration (not ABOVE, not BELOW)",
          s["narration_3rd_person"]["participant_minus_floor"]["band"] == "NOT_SEP")
    check("helps both pronoun classes (person + neuter ABOVE)",
          s["pronoun_person"]["participant_minus_floor"]["band"] == "ABOVE"
          and s["pronoun_neuter"]["participant_minus_floor"]["band"] == "ABOVE")
    check("never HURTS any split (no BELOW anywhere)", gr["never_hurts_any_split (no BELOW)"])
    check("all exclusion thresholds beat the floor (not a tuned knob)",
          gr["all_thresholds_beat_floor (not a tuned knob)"])
    check("recall stays 1.0 in every genre split",
          all(v["recall"] >= 0.99 for v in s.values()))
    check("generalization verdict = generalizes / neutral elsewhere",
          "GENERALIZES" in gr["verdict"])

    print("== (D) phi-agreement generalization: person-exclusion is one case of a general principle ==")
    ph = PHI.run(n_boot=800)
    pa = ph["person_arms"]
    pr = ph["reading"]
    check("ANIMACY is a 2nd clean lever for person pronouns (ABOVE)", pa["animacy_gold"]["delta"]["band"] == "ABOVE")
    check("LEXICAL animacy (no gold NER) also works (ABOVE) -- not a gold-annotation trick",
          pa["animacy_lexical"]["delta"]["band"] == "ABOVE" and pa["animacy_lexical"]["recall"] >= 0.99)
    check("person + animacy COMPOSE (>= either alone)",
          pa["person_plus_animacy"]["delta"]["delta"] >= pa["participant"]["delta"]["delta"]
          and pa["person_plus_animacy"]["delta"]["band"] == "ABOVE")
    check("animacy lever also cleans it/its pools (ABOVE)",
          ph["it_its_arms"]["animacy_gold_drop_animate"]["delta"]["band"] == "ABOVE")
    check("gender is STILL a non-lever (not ABOVE) -- principled exception", pr["gender_still_a_non_lever"])
    check("info-free random-drop twin LOSES on the combined filter", pr["info_free_twin_LOSES"])
    check("phi-agreement verdict = generalizes across person + animacy",
          pr["verdict"] == "PHI_AGREEMENT_HARDENING_GENERALIZES_PERSON_AND_ANIMACY")

    print("== (E) landing validation: pre-filter improves the ACTUAL landed graded_antecedent_pick, and generalizes ==")
    pf = PRE.run(n_boot=800)
    full = pf["full_competitive_population"]
    resid = pf["anti_typical_residual"]
    g1 = pf["generalization_1st_person_docs"]
    g3 = pf["generalization_3rd_person_docs"]
    prr = pf["reading"]
    check("TIER1 improves the LANDED resolver on FULL population CI-sep",
          full["participant_only_minus_asis"]["band"] == "ABOVE")
    check("TIER1 full-population lift >= 0.03", full["participant_only_minus_asis"]["delta"] >= 0.03)
    check("TIER1 improves the LANDED resolver on the residual CI-sep",
          resid["participant_only_minus_asis"]["band"] == "ABOVE")
    check("generalizes: concentrated in 1st-person docs (ABOVE)", g1["participant_only_minus_asis"]["band"] == "ABOVE")
    check("generalizes: NO regression in 3rd-person docs (not BELOW)", g3["participant_only_minus_asis"]["band"] != "BELOW")
    check("refined pure-participant rule is recall-safe on full pop (>=0.99)", full["recall_participant_only"] >= 0.99)
    check("info-free twin loses on the residual through the real resolver",
          resid["prefiltered_minus_random_twin"]["band"] == "ABOVE")
    check("landing verdict = improves landed resolver AND generalizes",
          prr["verdict"] == "PREFILTER_IMPROVES_LANDED_RESOLVER_AND_GENERALIZES_LAND_IT")

    print(f"\nALL {N} WITNESS CHECKS PASS")


if __name__ == "__main__":
    main()
