

## pasted by the owner 2026-09-13 11:09 (raw; strategy reads this)

SUBMISSION — problem: the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence

STATUS: SOLVED (core bar — excellent; upstream rungs — strong, with documented caveats). Solver deliverable
only: experiments/ + verification/ + SOLVED.md. NO hdlab writes — all hdlab changes are PROPOSED diffs (Q111).

WHAT LANDED (all glass-box, no external LLM at inference; witnesses green):
- Recovery arm (hypernym-consensus result-state inheritance + guarded affectedness admission, tau=0.35):
  recovers savage/victimize/oppress/maul; 65 residual verbs newly decided at Connotation-Frames human-gold
  precision 1.00, zero wrong-sign, zero neutral leaks; twin loses; board 24/24 held; whole-arithmetic
  independently validated 0.9323 >= landed 0.9276. Numbered located negative for the residue.
- Full-stack UPSTREAM (start-at-the-top, reuse BF organs): Rung 1 event-realization join (fully BF, reuses
  the pinned+previously-UNWIRED polarity_operator; realization-conditioned acc 0.375->0.95, CommitmentBank
  5/6). Rung 3 sense-in-context (BF; grounded_semantic_graph.select_sense; non-assault 3/3 abstain vs
  context-blind 0/3). Rung 2 prevent-complement (BF valuation; extraction BF-but-PARSER-GATED 7/10 -> the
  arc parser is the located bottleneck, a supervised stand-in whose BF successor is the attachment_arm).

REVERIFY (one chain, reproducible):
  .venv/Scripts/python.exe experiments/fetch_connotation_frames_v1.py && \
  .venv/Scripts/python.exe verification/test_fd_result_state_hypernym_arm.py && \
  .venv/Scripts/python.exe experiments/fetch_commitmentbank_v1.py && \
  .venv/Scripts/python.exe verification/test_harm_help_endstate_realization_join.py && \
  .venv/Scripts/python.exe verification/test_harm_help_prevent_complement.py && \
  .venv/Scripts/python.exe verification/test_harm_help_sense_in_context.py

INTEGRATE (top-down, on owner_verdict: DONE) + PRIORITY NEXT STEPS:
  1. Land the proposed diffs (Rung 1 realization join first — fully BF, biggest real-prose win); then measure
     the real-prose affected_entity number (scope c) — the one check a solver session cannot run.
  2. Open the arc-parser / attachment_arm heads rung as its own brief — the SHARED upstream lever.
  3. Rung 3 full integration (wire select_sense into endstate_valence_sign, drop consensus where context decides).
  4. Rung 4 manner-intensity -> grounded meaning channel (drilled located negative; not in any verb table).

AUDIT UPDATE: the landed harm/help arithmetic is now independently validated (0.928) against a human crowd
gold it does not consume — fold into BRAIN_FOUNDATIONAL_AUDIT §2b. Cross-solution flags: arc parser (heads
rung) + manner/intensity (grounded channel).

FULL DETAIL + proposed diffs: notes/problems/the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence/SOLVED.md
