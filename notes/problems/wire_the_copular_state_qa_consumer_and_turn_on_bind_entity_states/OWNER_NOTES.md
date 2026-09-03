---
owner_verdict: DONE
---

SUBMISSION -- wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states

STATUS: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO LLM at inference. NO hdlab written
(Q111; proposed diff below). Witnessed scaffold-free 9/9; problem_ledger --check clean.
REVERIFY: .venv/Scripts/python.exe verification/test_state_qa_consumer_organ.py     # 9/9 from source

WHAT IT DOES. The reader had a landed-but-OFF copular is-a/attribute capability (bind_entity_states ->
sm.state_register) with NO consumer -- it scored a live 0 on "what/who is X". I built the consumer: a
"state" QA dimension that routes "what/who is X" / "is X a Y" to the entity-state store (brain-faithful
copular-frame router) and reads the answer off sm.state_register -- never re-reading the text.

RESULT (UD-EWT copular gold, NON-CIRCULAR = gold from gold deprels, n=378 predicational clauses):
  qa_state MODEL = 0.7116, CI-sep +0.1402 [0.087,0.196] hw=0.055 nullp95=0.054 over the recomputed
  most-recent-noun floor (0.5714); info-free shuffle-holder twin (0.49) LOSES +0.209 CI-sep.
  Base reader OFF = 0/378 (the live can-fail zero). Router hit 1.000; ablate the frame -> 0.
  No-regression: the 4 scored dims byte-identical bind OFF vs ON (additive). qa_aggregate union
  lifts 0.315 -> 0.404 when the flag turns on. 19c LitBank live-fires: 527/530 (base reader = 0).

BOTH CHANGES ARE REQUIRED (coupled -- land together):
  CHANGE 1 (clears the bar): the consumer wire + flip bind_entity_states DEFAULT-ON. Net-positive on a
    consumed metric, additive, +~5ms/read -> satisfies no-default-off.
  CHANGE 2 (makes it accurate): adopt the label-robust upstream detector (robust_cop) on the
    entity-state route. Because the consumer is LOSSLESS (read-back|binding 0.996), this flows straight
    through: qa_state 0.712 -> 0.833 CI-sep, concentrated on is-a (pred_nom +0.184).
    OPTIMIZATION (modern-only): stack the arc-eager TREE -> 0.865 CI-sep (pred_nom 0.806->0.903).
    Route per-register (arc-eager is 19c-negative): 19c = July tree, modern = arc-eager.

HOW VS THE BRAIN / WHERE SIGNAL IS LOST. The consumer is at the brain's ceiling GIVEN the binding
(routing 1.0, read-back 0.996). The whole residual is UPSTREAM. Ranked further-optimization:
  1. CROSS-SENTENCE binding -- register keys the SURFACE token, so "what is Ahab" fails once he is "he".
     Fix: key on the coref entity (producer proved 0.43 of predications then cross-sentence answerable).
  2. Hardest-construction detection (equatives/clefts) -- needs register-native 19c parse/POS data.
  3. Identity copulas excluded (ident -> coref-merge, symmetric/CA3) -- filed follow-on.
  4. A small hand-annotated 19c copular gold -> a floor-separated 19c number (the one claim I can't make).

HONEST BOUND. The powered qa_state is MODERN (UD-EWT) -- the only place a non-circular is-a gold exists;
a LitBank state gold would be circular. On 19c I show COVERAGE (527/530), not a floor-separated score.

FILES. experiments/exp_situation_model_state_qa_v1.py (NEW: powered non-circular state-QA + controls +
waterfall + upstream-fix ladder + LitBank live-fires + board_state_dimension). experiments/
exp_situation_model_qa_v1.py (the wire: DIMENSIONS+state, copular-frame router, _answer_state,
build_state_questions, build_reader flips bind_entity_states=True, run() injects per_dimension['state']).
verification/test_state_qa_consumer_organ.py (NEW: 9/9 witness). REUSES verbatim: the owner-DONE
exp_copular_is_a_binding_readout_v1 (typed_gold/positional_floor/shuffle_twin/robust_cop), hdlab.
state_register, hdlab.copular_binding, hdlab.situation_reader. NO hdlab written.
