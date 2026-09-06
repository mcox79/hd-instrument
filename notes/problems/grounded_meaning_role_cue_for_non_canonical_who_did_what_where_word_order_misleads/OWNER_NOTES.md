---
owner_verdict: DONE
---

SUBMISSION — grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads
status: SOLVED (WIP until owner_verdict: DONE)

WHAT THE BRIEF ASKED: fix who-did-what on non-canonical clauses (passives/fronting) with a whitened
grounded selectional-fit "meaning" role cue in the live Competition-Model agent competition.

RESULT — two parts:
(1) LOCATED NEGATIVE on the brief's mechanism (the bar's sanctioned full PASS): I built the whitened,
    verb-keyed, self-gated grounded selectional-fit cue faithfully; it TIES its info-free twins on the
    non-canonical AGENT slice (real 0.512 vs scrambled 0.522, not CI-sep) — grounded meaning carries no
    role signal the competition's animacy cue doesn't already have. Confirms the independent fit-gate line.
(2) SOLVED a more brain-foundational way — a by-phrase CASE-MORPHOLOGY cue ("byhead"): reward candidates
    governed by the passive-agent preposition "by" through their whole NP (the live cue only saw a noun
    IMMEDIATELY after "by", missing "by the clerk"), gated by the participle+by-PP construction. Lifts the
    LIVE agent competition on the clean non-canonical slice 0.256 -> 0.689 (+0.4333 CI-sep), info-free twin
    loses, canonical untouched, on BOTH animate and inanimate agents. QA-SRL role-balanced gold (modern, no
    age confound), through the reader's own weak front-end.

BRAIN-FOUNDATIONAL: PINNED to the Competition Model (MacWhinney/Bates: case/adposition = top-validity cue)
    + eADM (case = actor-prominence). The grounded null is exactly noisy-channel theory (Gibson 2013): fit
    adds nothing once a reliable morphological marker is present. Tested a graded voice gate — worse; the
    boolean gate + softmax is the faithful, settled form.

END-TO-END (live board): wired byhead into the live LitBank who-did-what arm (n=1830) — NO material regress
    (-0.0005, CI incl 0; 1 answer changed; construction gate fires 4/1830). The board's gold asks about
    syntactic subjects, so it has ~no by-agent questions; it confirms SAFETY, and QA-SRL is the powered
    instrument. Safe to flip on.

IS IT AS GOOD AS THE BRAIN? On its home cases (real by-phrase passives) YES, nearly: byhead 0.784 vs a good
    parser's 0.874 on this data. The rest of the gap to brain-level who-did-what belongs to OTHER organs:
    the weak incremental PARSER (70.7% structural bulk + the by-marked residual) and COREF (the agentless
    tail). The role cue is the complete, correct piece; it sits on top of those.

NEXT MOVES (priority):
  (1) LAND byhead now — finished, safe, CI-backed (proposed hdlab diff in SOLVED.md).
  (2) BIG LEVER — build the brain's incremental cue-integrated PARSER
      (distributed_contextual_representations_into_the_parser). Highest-value remaining move for brain-level
      who-did-what; the role cue is already near its ceiling.
  (3) coref for the agentless tail; minor by-NP-head refinement. DON'T: graded voice weight (worse),
      grounded fit in the competition (located negative).

FILES: experiments/exp_grounded_selfit_role_cue_v1.py, exp_noncanonical_agent_bymorph_v1.py,
  exp_cmrole_agent_board_byhead_v1.py, exp_noncanonical_agent_parse_ceiling_v1.py;
  verification/test_noncanonical_agent_bymorph_organ.py (5/5), test_cmrole_agent_board_byhead_organ.py (2/2);
  notes/problems/<slug>/{SOLVED.md, RESEARCH_brain_foundational_case_morphology_role_cue.md}. NO hdlab/ (Q111).
REVERIFY: .venv/Scripts/python.exe verification/test_noncanonical_agent_bymorph_organ.py
       && .venv/Scripts/python.exe verification/test_cmrole_agent_board_byhead_organ.py
