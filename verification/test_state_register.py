"""Scaffold-free witness for the_situation_model_tracks_no_entity_state_history.

Asserts the load-bearing claims of the per-entity STATE-HISTORY register (spaCy LOCAL for the extraction
checks; landed metrics for the CI-separated aggregates):
  1. TRACKING CORE: binds a state to an entity over intervals; default-persists; closes only on an
     incompatible/antonym state (NEVER silently); the perfect 'had been X' does NOT auto-close (research:
     cancellable default); resultant state of a telic event; co-states are not mutually exclusive.
  2. EXTRACTION ADAPTER (glass-box, spaCy): copular / perfect / archaic BE-perfect / resultant extraction;
     wall-guards (conditional subject-aux inversion, 'if' irrealis, habitual, existential 'there has been X'
     all skipped); a 'be + participle' reads as a STATE not a double-counted event.
  3. LANDED AGGREGATES: construction gate PASS (register 1.000 vs strongest stateless floor CI-separated;
     BOTH info-free twins lose; empty register at chance; distance-robust); real-prose coverage + the
     entity-blind floor/twin at chance + supersede incidence.

Run: .venv/Scripts/python.exe verification/test_state_register.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.state_register as S
from experiments.state_register import StateRegister, extract_state_events, CURRENT, PRIOR, RESULT

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAIL: {name}"
    PASS += 1
    print(f"  ok: {name}")


def _metrics(anchor):
    with open(os.path.join(_REPO, "data", "exp_" + anchor, "metrics.json"), encoding="utf-8") as f:
        return json.load(f)


def _vals(evs, kind=None):
    return {(e["subj_head"], e["value"]) for e in evs if kind is None or e["kind"] == kind}


print("[1] TRACKING CORE: bind state to entity over intervals; default-persist; explicit-only closure")
reg = StateRegister().fold(["house", "she"],
                           [("state", "house", "grand", PRIOR, 1, 1),
                            ("state", "she", "ill", PRIOR, 1, 2)], n_clauses=6)
check("prior state binds to the right entity", reg.is_in_state("house", "grand", 5) is True)
check("a state is NOT mis-bound to the other entity", reg.is_in_state("she", "grand", 5) is None)
check("perfect 'had been X' does NOT auto-close (cancellable default)", reg.is_in_state("house", "grand", 5) is True)
check("had_been retrieves the prior state", "ill" in reg.had_been("she", 5))

reg = StateRegister().fold(["door"], [("state", "door", "locked", CURRENT, 1, 1),
                                      ("event", "door", "unlock", "unlocked", 3)], n_clauses=6)
check("an incompatible state CLOSES the prior one (supersession)", reg.is_in_state("door", "locked", 5) is False)
check("the new incompatible state holds", reg.is_in_state("door", "unlocked", 5) is True)
check("had_been still remembers the closed state", "locked" in reg.had_been("door", 5))

reg = StateRegister().fold(["door"], [("event", "door", "open", "open", 2)], n_clauses=5)
check("resultant state of a telic event is inferred", reg.is_in_state("door", "open", 4) is True)
check("the telic occurrence-fact is recorded (permanent)", len(reg.occurrences_of("door", 4)) == 1)

reg = StateRegister().fold(["he"], [("state", "he", "soldier", PRIOR, 1, 1),
                                    ("state", "he", "ill", CURRENT, 1, 2)], n_clauses=6)
check("co-states are NOT mutually exclusive (soldier + ill both hold)",
      reg.is_in_state("he", "soldier", 5) is True and reg.is_in_state("he", "ill", 5) is True)

reg = StateRegister().fold(["e"], [("state", "e", "grand", CURRENT, 1, 1)], n_clauses=22)
check("state persists across 20 filler clauses (maintained, not a local read)", reg.is_in_state("e", "grand", 21) is True)
check("incompatible() is explicit: ill/well incompatible, ill/soldier NOT",
      S.incompatible("ill", "well") and not S.incompatible("ill", "soldier"))

print("[2] EXTRACTION ADAPTER (glass-box spaCy): copular / perfect / resultant + wall-guards")
import spacy
nlp = spacy.load("en_core_web_sm")

e1 = extract_state_events(nlp, "The house had been grand. She had been ill.")
check("perfect 'had been X' -> PRIOR state", ("house", "grand") in _vals(e1) and all(e["aspect"] == PRIOR for e in e1))
e2 = extract_state_events(nlp, "Mr Grey was a soldier.")
check("copular 'was X' -> CURRENT state", any(v == "soldier" and e["aspect"] == CURRENT
      for e in e2 for v in [e["value"]]))
e3 = extract_state_events(nlp, "The vase was whole. Tom broke the vase.")
check("'was whole' is a STATE, 'broke' is a resultant EVENT (no double count)",
      ("vase", "whole") in _vals(e3, "state") and ("vase", "broken") in _vals(e3, "event"))
e4 = extract_state_events(nlp, "The door was locked.")
check("'be + participle' reads as a STATE, not a telic event", _vals(e4, "state") and not _vals(e4, "event"))
e5 = extract_state_events(nlp, "He had not been known to them.")
check("negation captured ('had not been known' -> pol -1, value 'known')",
      any(e["value"] == "known" and e["polarity"] == -1 for e in e5))
e6 = extract_state_events(nlp, "She was become a woman.")
check("archaic BE-perfect 'was become X' extracted", any(e["value"] == "woman" for e in e6))

check("wall: conditional inversion 'Had he been a soldier' SKIPPED",
      len(extract_state_events(nlp, "Had he been a soldier, he would have known.")) == 0)
check("wall: 'if X had been Y' irrealis SKIPPED",
      len(extract_state_events(nlp, "If he had been clean he would look well.")) == 0)
check("wall: habitual 'in the habit of' SKIPPED",
      len(extract_state_events(nlp, "He was in the habit of walking early.")) == 0)
check("wall: existential 'there has been X' SKIPPED",
      len(extract_state_events(nlp, "We know there has been a presentation.")) == 0)

print("[3] LANDED AGGREGATES reproduce the headline")
mQ = _metrics("state_register_query_v1")
check("construction gate PASS", mQ["gate"]["PASS"] is True)
check("register beats strongest stateless floor CI-separated",
      mQ["register"]["ci"][0] > mQ["strongest_floor_hi"])
check("info-free ENTITY-shuffle twin LOSES CI-separated", mQ["twin_entity_shuffle"]["loses_ci_sep"] is True)
check("info-free ORDER-shuffle twin LOSES CI-separated", mQ["twin_order_shuffle"]["loses_ci_sep"] is True)
check("EMPTY register scores at chance (not perfect) -> metric not gameable by emptiness",
      mQ["empty_register_arm"]["acc"] < 0.6)
_ps = mQ["per_structure"]
_floor_names = list(_ps["BIND"]["floors"].keys())
check("register is best-or-tied on every structure (never beaten by a floor)",
      all(_ps[st]["register"] >= max(_ps[st]["floors"].values()) for st in ("BIND", "RESULT", "SUPERSEDE")))
check("no single stateless floor handles all three (each floor fails >=1 structure vs register)",
      all(any(_ps[st]["floors"][k] < _ps[st]["register"] for st in ("BIND", "RESULT", "SUPERSEDE"))
          for k in _floor_names))
dist = mQ["distance_robustness_PERSIST"]
check("distance-robust: register flat 1.0 at K=20 while windowed floor collapses to 0",
      dist["20"]["register"] >= 0.99 and dist["20"]["windowed_W2"] <= 0.01)

mR = _metrics("state_register_real_prose_v1")
check("real-prose extraction coverage is measured (0 < cov < 1, coverage-bounded)",
      0.0 < mR["extraction"]["coverage_bound_vs_reference"] < 1.0)
check("real-prose entity-blind floor sits at chance (~0.5) -> task needs entity-bound state history",
      mR["entity_binding_query"]["entity_blind_recency_floor"]["acc"] < 0.6)
check("real-prose entity-shuffle twin loses (binding is load-bearing)",
      mR["entity_binding_query"]["entity_shuffle_twin"]["acc"] < 0.6)
check("real-prose supersede incidence is reported (honest bound on the closure channel)",
      "supersede_incidence_in_bound" in mR["state_history_isolation"])
check("the previously-DROPPED 'had been X' prior channel is now extracted+bound (n_prior_bound > 0)",
      mR["n_prior_bound"] > 0)

print("[4] SEMANTIC (ATL-hub) state matching + the three research guards")
from experiments.state_register import state_match
check("synonymy: query 'unwell' matches stored 'ill'", state_match("unwell", "ill", 1) == "MATCH")
check("scalar entailment: 'shattered' entails 'broken'/'damaged'",
      state_match("broken", "shattered", 1) == "MATCH" and state_match("damaged", "broken", 1) == "MATCH")
check("hypernym entailment: 'soldier' entails 'serviceman'", state_match("serviceman", "soldier", 1) == "MATCH")
check("guard-3 CONTRADICTORY: 'not alive' -> dead HOLDS", state_match("dead", "alive", -1) == "MATCH")
check("guard-3 CONTRARY: 'not tall' does NOT entail 'short'", state_match("short", "tall", -1) == "NONE")
check("guard-3 CONTRARY: 'not ill' does NOT entail 'well'", state_match("well", "ill", -1) == "NONE")
check("an antonym of a HELD state does not hold ('well' vs stored 'ill')", state_match("well", "ill", 1) == "NO")
check("incompatibility is by OPPOSING GROUP, not flat set (ill/unwell NOT incompatible, ill/well IS)",
      not S.incompatible("ill", "unwell") and S.incompatible("ill", "well"))
reg = StateRegister().fold(["x"], [("state", "x", "ill", PRIOR, 1, 1)], n_clauses=4)
check("is_in_state semantic: stored 'ill' answers 'unwell?' True and 'well?' False",
      reg.is_in_state("x", "unwell", 3, semantic=True) is True
      and reg.is_in_state("x", "well", 3, semantic=True) is False)
e_priv = extract_state_events(nlp, "He was a fake soldier.")
check("privative guard: 'a fake soldier' does NOT store the state", not any(x["kind"] == "state" for x in e_priv))
check("modal-perfect irrealis skipped ('he would have been a soldier')",
      len(extract_state_events(nlp, "He would have been a soldier.")) == 0)

mS = _metrics("state_register_semantic_v1")
check("semantic gate PASS", mS["gate"]["PASS"] is True)
check("guarded semantic beats exact-string CI-separated", mS["arms"]["guarded"]["ci"][0] > mS["arms"]["exact"]["ci"][1])
check("exact string recovers ~0 synonym queries; semantic recovers most",
      mS["setA_synonym_recall"]["exact"] < 0.1 and mS["setA_synonym_recall"]["guarded"] > 0.7)
check("the three guards are load-bearing (guarded > unguarded on the traps, CI-sep)",
      mS["setB_trap_accuracy"]["guarded_lo"] > mS["setB_trap_accuracy"]["unguarded_hi"])
check("info-free twin (shuffled stored) loses on the held set", mS["twin_shuffled_stored"]["acc"] < 0.6)

print("[5] SERVE: the register resolves state-denoting descriptions a stateless coref reader cannot")
import experiments.exp_state_register_serves_coref_v1 as SV
# hand case: 'the sick one' resolves to the ILL entity, not the most-recent mention
hand = {"entities": [("Anna", "f"), ("Ben", "m")],
        "events": [("state", "Anna", "ill", PRIOR, 1, 1), ("state", "Ben", "soldier", PRIOR, 1, 2)],
        "mentions": ["Anna", "Ben", "Ben"], "epithet_head": "sick", "epithet_gender": None, "gold": "Anna"}
check("serve resolves 'the sick one' to the ill entity (Anna), recency picks Ben",
      SV.resolve_serve(hand) == "Anna" and SV.resolve_recency(hand) == "Ben")
mV = _metrics("state_register_serves_coref_v1")
check("serve gate PASS", mV["gate"]["PASS"] is True)
check("serve beats the strongest stateless coref floor CI-separated",
      mV["serve"]["ci"][0] > mV["strongest_floor_hi"])
check("all stateless coref floors sit near chance (state is the only cue)",
      all(v["acc"] < 0.7 for v in mV["floors"].values()))
check("info-free state->entity twin loses CI-separated", mV["twin_state_entity_shuffle"]["loses_ci_sep"] is True)

print("[6] LIVE-ORGAN SERVE: the register improves the ACTUAL hdlab coref organ on state-decisive pronouns")
mL = _metrics("state_register_serves_live_coref_v1")
check("live-organ serve gate PASS", mL["gate"]["PASS"] is True)
check("register-served beats the LIVE hdlab coref organ CI-separated",
      mL["register_served"]["ci"][0] > mL["live_coref_organ"]["ci"][1])
check("the live coref organ is at chance on state-decisive same-gender pronouns (< 0.65)",
      mL["live_coref_organ"]["acc"] < 0.65)
check("info-free shuffled-states twin collapses to the live-organ level (loses CI-sep)",
      mL["twin_shuffled_states"]["loses_ci_sep"] is True)
check("the live coref organ genuinely resolves real-LitBank pronouns (baseline reported, n>0)",
      mL["real_litbank_live_coref_baseline"]["n_targets"] > 0)

print(f"\n[witness] {PASS}/{PASS} PASS")
