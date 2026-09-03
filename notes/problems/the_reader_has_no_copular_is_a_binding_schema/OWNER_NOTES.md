---
owner_verdict: DONE
---

SUBMISSION -- the_reader_has_no_copular_is_a_binding_schema

STATUS: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO LLM at inference. NO hdlab/ written (Q111;
proposed diff in SOLVED.md). Twice witnessed; ledger clean.
REVERIFY: .venv/Scripts/python.exe verification/test_copular_is_a_binding_organ.py            # core 10/10
          .venv/Scripts/python.exe verification/test_copular_improvements_organ.py            # 5 improvements + end-to-end 6/6

WHAT IT DOES. Builds the is-a/attribute binding read-back the base reader lacked (base = 0/376 on predicate
complements). On 451 gold copular clauses (UD-EWT; nominal is-a + adjectival + identity) it answers "what/who is
X" at recall 0.672, CI-separated +0.1685 [0.114,0.217] over the most-recent-noun floor, info-free shuffle twin
LOSES +0.2195. THE FIX (label-robust copula-anchored detection) -> 0.818 (+0.146 CI-sep), gain concentrated on the
identity weak point (+0.247, itself CI-sep). Glass-box Higgins typing 0.969. Register-independent; no-regression
(state_register 11/11). REUSES the sibling's extract_entity_states + state_register (did not reinvent).

DEEP UNDERSTANDING (owner-directed). Process map + per-clause error taxonomy + brain-vs-us waterfall: the ~0.18
gap to the brain is DETECTION (parser tree/labeler on hard equatives), not binding. 6 full-text research drills
pin every mechanism (Higgins typing; CA3 symmetric identity; is-a = relation-extraction not similarity;
power-law salience; incremental parsing tested-negative for copular).

FIVE IMPROVEMENTS -- ALL BUILT + WITNESSED (6/6), on the arc-eager tree:
  1 arc-eager parse tree      -> labeled base binding 0.672->0.783 (+0.111 CI-sep), identity +0.055.
  2 is-a INHERITANCE          -> relation-extraction (Hearst UNION WordNet + traversal) recovers is-a 1.000 vs the
                                 distributional ceiling 0.694 (twin 0.500) -- the wall BREAKS by relation
                                 extraction, not similarity. The copula IS the read-time edge (arc-eager harvest,
                                 81% compose with the foundation).
  3 identity->coref merge     -> symmetric X==Y edges (hippocampal; Dijksterhuis 2024), 71 recorded.
  4 fuller typing + deferral  -> 0.9686 (no regression) + DEFERS 1.1% on the possessive ambiguity zone.
  5 power-law (ACT-R) salience-> brain-faithful decay; controlled topicality 1.000 vs the parser's 0.000.
END-TO-END READ-BACK composed: the fact binds to the CANONICAL entity, answerable via a cross-sentence mention
(later "he"/"the captain") = 0.384 of facts, token-only floor 0.

HONEST BOUNDS. The fix trades precision (0.77->0.62; high-precision label path is the landed default). Topicality
is a robustness fix (ties the parser on natural prose, wins only on rare inverted cases). Cross-sentence coverage
uses gold LitBank coref. The predicational/identity NEURAL dissociation is an extrapolation (I claim only the
surface-cue typing). Inheritance MECHANISM is proven; the harvested graph AT SCALE is routed (below).

NEXT STEPS TO MAXIMIZE PERFORMANCE (ranked by impact):
  1. LAND THE WIRE (Q111, default-off) WITH parser_arceager=True. Adds SituationModel.entity_states + the typed
     binding; routes predicational->state_register, identity->symmetric coref merge. This makes the LIVE reader
     answer "what is X" AND banks the arc-eager +0.111 base gain + identity +0.055. Biggest immediate lever.
  2. BUILD THE is-a INHERITANCE FOUNDATION (Hearst-harvest at scale) -- the deepest capability (doctor->person).
     Mechanism proven (1.000); needs the offline harvested graph (copula + such-as/appositive patterns UNION
     WordNet/ConceptNet). Routed to the knowledge-foundation effort (strategy's exp_dev hand-off) -- fund it there.
  3. REGISTER-NATIVE parse/POS data for the DETECTION residual (~13% hardest equatives/clefts) + 19c prose. The
     arc-eager tree does NOT move the 19c ceiling (owner caveat) -- route to the register-parse-data problem.
  4. COMPOSE THROUGH THE LITERAL read() + RUNTIME coref (run_match_or_allocate) so the cross-sentence read-back
     and identity->coref merge run live without gold coref.

FILES. experiments/: exp_copular_is_a_binding_readout_v1 (core+fix+typing), _register_and_noregress_v1,
_incremental_discourse_reader_v1 (arc-eager+power-law+identity+end-to-end), _arceager_parser_comparison_v1,
exp_isa_hearst_harvest_inheritance_v1, _fuller_typing_v1, _ideal_incremental_predictive_v1. verification/:
test_copular_is_a_binding_organ (10/10), test_copular_improvements_organ (6/6). notes/problems/<slug>/: SOLVED.md
+ IDEAL_architecture + 3 research drills + 5 persisted prototypes. NO hdlab written.
