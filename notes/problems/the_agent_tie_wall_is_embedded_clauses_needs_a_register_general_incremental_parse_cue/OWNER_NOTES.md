---
owner_verdict: DONE
---

SUBMISSION — problem: the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_incremental_parse_cue
status: SOLVED (WIP until owner_verdict: DONE)

BAR (verbatim): a glass-box, REGISTER-GENERAL incremental structure cue (NO trained parser, NO LLM)
entering graded_competition as ONE precision-weighted cue + recency-weighted Centering, beating the
current competition on the embedded/relative-clause agent slice CI-separated, shuffled-structure twin
LOSING, NO canonical regression, held-out replicated — or a located negative with a named cause.

RESULT (MET + generalizes): reused the landed register-general hdlab.incremental_parser (glass-box
left-corner subject bind — NOT the trained parser, which is HARMFUL OOD, corroborated by the adjacent
relcl SOLVED) as ONE self-gating precision-weighted cue in the landed AGENT graded_competition. Board
who-did-what AGENT, context-cued readout, embedded-clause nominative-vs-nominative TIE slice (LitBank 19c,
full P2 stack ON):
  tuned    0.6372 -> 0.7098  = +0.0726 CI[+0.0435,+0.0992] p<=0=0.000  (n_tie=317)
  held-out 0.6178 -> 0.6739  = +0.0562 CI[+0.0336,+0.0811]             (n_tie=552, never inspected)
  shuffled-structure twin LOSES CI-sep (+0.221/+0.203); canonical no-regress (+0.007/+0.004); whole-arm
  +0.019/+0.014 CI-sep. Witness test_cmrole_agent_struct_organ.py: ALL CHECKS PASS.

BRIEF WAS HALF-RIGHT: structure cue = the lever (confirmed, held-out); recency-weighted Centering =
REFUTED (fails tuned+held-out — matches the substrate's OWN salience_binder finding that recency is at
chance on hard cases; embedded clauses introduce a NEW subject so "continue previous subject" mispredicts).

EVERY LEVER RUN TO GROUND (can-fail, measured): eADM GRADED precision (distance/relativizer-gating) — no
gain, self-gating IS the right precision; weight-robust across struct_w {1.5,2.5,4.0}. MORE-brain-faithful
RC-POP revision (ungated AND gated who/whom/which) — REJECTED (net-neutral/negative; reproduces
incremental_parser's own "revision hurts clean prose"; gated reanalysis is the SEPARATE relcl organ, not the
general cue). THEMATIC-FIT / agentivity (owner-named next lever) — CLOSED (3 prior 19c prototypes + first-hand
agentivity both null vs twin; the tie residual is 89% character-vs-character where names carry no selectional
signature).

FIXED EVERY MECHANICAL LOSS + COMPOSED (tuned, directional): residual = ONE partition (n=92) 58.6% event-
detection + 40.2% competition + 1.1% readout. Detection -> flip ON the EXISTING default-OFF predicate_recall
organ = +0.0083 CI-sep whole-arm. Competition fragments -> gerund-possessive +0.0017, collective-human animacy
+0.0011. ALL composed = +0.0105 CI[+0.0059,+0.0152] CI-sep whole-arm. Tie remainder (+0.003, not sep) is
IRREDUCIBLE: character-vs-character genuine ambiguity + coref-miss (a different organ) — not a fixable cue here.

PROPOSED WIRE (Q111, strategy lands): add one `structure` cue to graded_role_assigner.agent_supports /
AGENT_VALIDITIES (self-gating, STRUCT_W~2.5; expose incremental_subject_before from incremental_parser).
Net-positive, patient byte-identical, held-out-replicated -> land ON. Do NOT add recency-Centering, RC-pop,
or thematic-fit (all closed with measured causes).

NEXT FOCUS (its own problem): register-robust EVENT DETECTION — 58.6% of the residual; already-prototyped
entry point (predicate_recall +0.008 CI-sep agent arm); full build = copula/light-verb/archaic recovery +
cross-arm turn-on analysis. Lifts EVERY who-did-what arm.

FILES: experiments/exp_cmrole_agent_{struct_v1,struct_opt_v1,struct_v2,thematic_v1,detect_v1,allfix_v1}.py;
verification/test_cmrole_agent_struct_organ.py; SOLVED.md. No hdlab writes.
REVERIFY: .venv/Scripts/python.exe verification/test_cmrole_agent_struct_organ.py
