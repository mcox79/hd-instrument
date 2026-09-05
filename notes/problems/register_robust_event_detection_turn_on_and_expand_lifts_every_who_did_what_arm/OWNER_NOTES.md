---
owner_verdict: DONE
---

SUBMISSION — problem: register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm
status: SOLVED (WIP until owner_verdict: DONE)

BAR (verbatim): a register-robust event-detection turn-on (+ copula/light-verb/archaic recovery) with an FP-controlled
precision gate such that who-did-what coverage rises on the agent AND patient arms CI-separated, an info-free twin
LOSES, and NO other dimension regresses (each on its right instrument) — or a rigorous located NEGATIVE with the named
cause. Strategy lands the Q111 wire.

RESULT (MET, held-out-replicated). Board=16 LitBank docs, held-out=40 DISJOINT docs, doc-level bootstrap.
OPTIMIZED reader (corrected copula routing + predicate_recall) vs current:
  whole AGENT arm  0.7099 -> 0.8044 = +0.0945 CI[+0.0829,+0.1049] CI-sep (40 held-out; board +0.0667 CI-sep)
  whole PATIENT arm +0.0050 CI-sep
Two brain-faithful levers:
  • LEVER B (dominant) — COPULA silo-unification, a SORT-AWARE READOUT (no new firing): for a copula-gov predicate
    LEAD with the landed sm.entity_states HOLDER/PROPERTY. Copula HOLDER(agent) 0.09->0.63 held-out = +0.535
    CI[+0.481,+0.586] over base AND +0.56 over the deranged-state twin; PROPERTY(patient) 0.00->0.275 = +0.275 over
    base+twin. Both generalize.
  • LEVER A — predicate_recall (P6 open-class noisy-channel recovery, already wired default-OFF): held-out agent
    +0.0125 / patient +0.0050 CI-sep; beats the random-verbhood twin CI-sep. LAND SCOPED (causal_links over base
    events) — blanket recall regresses causal -0.0594 on the fixed qset; scoping -> byte-identical, gain retained.

HONESTY / KEY CORRECTION: an earlier draft "withdrew" the copula AGENT arm as non-generalizing — that was a
READOUT-ROUTING BUG in my own lever B (it preferred a spurious dynamic 'be'-event over the state holder). Fixed:
the landed copular organ identifies the holder at 0.63 (near the competent-reader oracle 0.71). Every "agent/be
withdrawn/marginal" phrase in the body is superseded (see the ⚠️ CORRECTION block).

CONTROLS: info-free twins x2 lose CI-sep (random-verbhood; deranged-state). NO-REGRESSION on every event-consuming
dim (coref byte-identical; temporal fixed-qset byte-identical; world_state 0 flips; bound_event_tokens 1/3641;
causal byte-identical AFTER scoping). FP ~1.0 extra events/sent, does not reach a who-did-what answer.

DRILLS (where we lose signal / exact brain mechanism / precise divergence): SIGNAL_LOSS_AND_BRAIN_MECHANISM_DRILL.md
+ 4 research drills. Signal-loss ladder vs a competent-reader oracle localizes the residual to ARGUMENT ATTACHMENT +
CAUSAL. Isolation proofs: causal cannot be fixed structurally (a PERFECT parse is WORSE; oracle participants don't
help) -> needs the meaning hub; open-class + copula-holder attachment -> the joint graded decoder (Viterbi argmax =
the zero-particle limit of the brain's belief-updating). Six holder prototypes + a Kimball closure bracketer all
under-performed the landed organ — because the "holder wall" was the routing bug, not a mechanism gap.

NEXT STEPS (PRIORITY):
  P1 LAND NOW (biggest gain, one-line, low risk): (a) sort-aware copula routing — lead with sm.entity_states for a
     copula-gov predicate; (b) predicate_recall ON, SCOPED (causal over base events). = the +0.09 agent-arm squeeze.
  P2 The JOINT GRADED DECODER (filed: upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior) — 3 payoffs
     proven: open-class 19c recovery, copula holder 0.63->0.77, open-class attachment 0.83->0.955.
  P3 The MEANING HUB for CAUSAL (candidate NEW problem to file) — implicit-causality + normality scorer; drop
     participant-overlap (empirically falsified). Retires the causal scoping workaround.
  P4 Unified sort-typed eventuality inventory (filed: the_assembled_reader_is_parallel_silos...) — the faithful form
     of lever B.

FILES: experiments/exp_event_detection_{crossarm_v1,crossarm_copula_v1,crossarm_full_v1,noregress_v1,causal_scope_v1,
state_noregress_v1,heldout_v1,copula_agent_v1,threshold_sweep_v1,structural_causal_v1,signal_ladder_v1,causal_oracle_v1,
holder_incremental_v1,subject_head_v1,closure_subject_v1,copula_corrected_v1,optimized_v1}.py;
verification/test_event_detection_crossarm_organ.py; SOLVED.md + BRAIN_MECHANISM_DRILL.md +
SIGNAL_LOSS_AND_BRAIN_MECHANISM_DRILL.md. No hdlab writes.
REVERIFY: .venv/Scripts/python.exe verification/test_event_detection_crossarm_organ.py   (7/7 PASS)
