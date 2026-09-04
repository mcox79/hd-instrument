---
owner_verdict: DONE
---

SUBMISSION — problem: swap_the_positional_role_assigner_for_the_brain_foundational_competition_model
status: SOLVED (WIP until owner_verdict: DONE)

BAR (verbatim): a glass-box Competition-Model cue-competition role assigner (word-order + animacy +
voice + verb-frame; NO trained parser, NO LLM) such that with referent_per_np ON, the board's
who-did-what AGENT arm recovers to >= the pre-referent baseline CI-separated, patient (+0.336)
not regressed, info-free twin losing — or a located negative.

RESULT: MET, then pushed the whole chain. Board who-did-what AGENT accuracy (SITQA.build_events_
questions, LitBank 19c, load_docs(16), n=1830), referent_per_np ON:
  assigned fix (CM agent over the TRACKED/given set)  = 0.2519  vs baseline 0.2257
    -> +0.0262, doc-bootstrap 95% CI [+0.0018,+0.0510] — RECOVERED ABOVE the bar, CI-separated.
  regression it fixes (positional over the dense set) = 0.0410.
  PATIENT byte-identical (the +0.336 preserved by construction). Info-free twin loses (+0.09 CI-sep).

KEY MOVE (brief was HALF-right, refuted-then-completed): the rule-swap ALONE over the dense referent
set only reaches 0.082. The decisive variable is the CANDIDATE SET — the AGENT must compete over the
TRACKED/GIVEN discourse entities (Centering Cb->subject, Grosz 1995; DuBois 1987 Preferred Argument
Structure), NOT every NP head. This DECOUPLES agent (tracked) from patient (dense) — the same decouple
lesson as the parent problem. Reuses hdlab.graded_competition verbatim (adds the AGENT slot the
substrate lacked). Every claim replicates on 24 HELD-OUT docs never inspected (n=2887).

FULL OPTIMIZED STACK (each step a pinned brain mechanism; each generalizes on held-out; twin loses):
  0.041 regression -> 0.252 tracked-set fix -> 0.408 + subject pronouns (Centering: Cb is
  pronominalized) -> 0.422 + clause-local competition -> 0.690 + context-cued readout (cue-based
  retrieval, not last-event) -> 0.692 + CASE cue (nominative-only pronoun agents).
  Net vs a fair floor (0.317): +0.375, CI-separated, replicated held-out.

CONTROLS: info-free shuffled-supports twin (loses CI-sep at every step); CM-over-dense arm (0.082,
proves the SET decouple); patient signature byte-identical; gold-agent 79.4% tracked (matches the
~80% Centering figure); 70% pronoun scorer ceiling quantified; weight-robustness 0.211-0.229
(non-knife-edge); PARSER prototype (a trained arc parser LOSES OOD on 19c, CI-sep — vindicates the
cue competition and the no-trained-parser invariant). Scaffold-free witness 10/10.

PERFORMANCE vs BRAIN + WHERE SIGNAL IS LOST NOW (measured, at 0.69): a competent reader ~ceiling.
Of the remaining errors: 75% competition (hard nominative-vs-nominative ties in embedded/relative
clauses), 20% event detection (a different organ), 5% coref coverage.

NEXT BUILD (named in SOLVED.md §6b + NEXT STEPS #2): a REGISTER-GENERAL incremental parse as ONE
precision-weighted CUE in the competition (eADM: syntax down-weighted when unreliable), + recency-
weighted Centering — for the embedded-clause tie wall. NOT a trained parser (proven to lose OOD).

FILES: experiments/exp_cmrole_agent_{board,pronoun,clause,parser,readout,case}_v1.py;
verification/test_cmrole_agent_board_organ.py; SOLVED.md (proposed hdlab wire in §7). No hdlab writes.
REVERIFY: .venv/Scripts/python.exe verification/test_cmrole_agent_board_organ.py   (10/10)
