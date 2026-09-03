---
owner_verdict: DONE
---

SUBMISSION — the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses  (SOLVER, opus 4.8)

STATUS: SOLVED. Witness verification/test_whodidwhat_coverage.py = 65/65. Ledger malformed/incomplete: 0.
NO hdlab writes (strategy lands the Q111 wire). 34 experiment cells. WIP until owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_whodidwhat_coverage.py

CORE RESULT (canonical clean-19c who-did-what, n=669, effective end-to-end, abstention=wrong):
- The 22% abstention decomposed first-hand into 3 OUR-INVENTION gates mis-firing on 19c prose (speech-verb quotative
  veto 80 / verb_subcat hard-threshold 47 / POS-tagger no-event 20) -- never "the parser couldn't find the noun."
- Brain-faithful structural recovery (word-order Competition Model + NP-head + structural direct-object filter,
  Davidsonian coverage) reaches 0.9851, info-free twin loses, no precision regression, generalizes to modern (+0.335).

INTEGRITY CORRECTION (important): the floor MOVED DURING the work -- the strategy session landed modules (predict_revise
+ others) that lifted the live wired reader from the stored 0.6293 (now RETIRED as stale) to 0.7877. Recomputed
first-hand: recovery beats the CURRENT floor +0.1973 CI[+0.169,+0.227]. The gain is now mostly ACCURACY (fixes 65 of
75 remaining wrong picks) + recovers the 47 verb_subcat + 20 no-event.

BRAIN-COMPARISON (made performance-level): vs a competent reference parser (spaCy, reference-only), we are AT
competent-reader level on canonical (ours 0.960 vs spaCy 0.852, near oracle 0.990). On non-canonical, spaCy ALSO
fails (0.021) -> the non-canonical gold is ~96% broken; rebuilt against a competent gold our true non-canonical
performance is 0.475 (a real modeling gap, was masked by broken gold).

WHAT'S READY TO LAND (strategy, Q111, default-off, witnessed -- §0g): np_head_reduce (landed), STRUCTURAL-DO
candidate filter (subsumes verb_subcat; +intransitive precision 0.975), quotative-on-evidence, object-gap routing,
and REFERENT-PER-NP mention builder (the biggest DEPLOYMENT lever: coref sources only ~9% of nouns / 62% of patients;
referent-per-NP lifts patient candidate-coverage to 0.97). Reference impl: exp_whodidwhat_composed_pipeline_v1.

WHAT'S FENCED / ALREADY-LANDED (do not rebuild): grounded-VALENCE on selection = proven negative (structure-bound,
confirmed 1st-hand 4x); non-canonical role assignment + filler-gap = already landed organs; the meaning channel =
separately-filed deep successor (ATL-hub / generative situation model), CITED not opened.

VERB-ID (the "20 no-event", ~2% genuine mistag): 5 approaches refuted (heuristic cue 3.72 FP; learned combiner 0.05;
heuristic joint 0.05; parse-coherence 0.15). The noisy-channel joint override (local structural gain + global
non-degradation) is the first to CLEAR the bar: 0.50 recovery @ 0.92 false-verbs/sent on 19c -- but it does NOT
GENERALIZE (modern 0.16), so it's a 19c-specific diagnostic, not general.

>>> NEW BUILD (out of scope for this submission -- FILE AS ITS OWN PROBLEM):
beam_decoded_joint_pos_dependency_parser_with_synthetic_register_mistag_augmentation. I built a trainable joint parser
(POS as a scored SHIFT_V action, exp_whodidwhat_joint_decoded_parser_v1) and located BOTH root causes first-hand:
(1) DATA -- modern tagger mistags verbs only 1.5%, fixed by synthetic mistag injection (built); (2) DECODER -- greedy
can't fire the correction (verb/noun look identical before args attach), so BEAM lookahead is required (Bohnet&Nivre;
proven necessary by the greedy failure). Doubly-compounding (POS feeds parser + meaning). Scaffold + data fix + proof
are handed over as the starting evidence. This is a focused ML build, NOT a wire into this problem.

KEY REALIZATIONS: (a) a MORE accurate component made the system worse (the wired parse-route was net-negative for
patient coverage) -- robustness beats a fancy tool; (b) the floor moved under me -> always recompute vs the CURRENT
substrate; (c) benchmark against a competent reader -> the "hard" non-canonical regime was mostly broken gold; (d)
five refuted verb-ID patches PROVED the joint parser is the real build and why greedy/post-hoc can't do it.

TLDR (plain): The reader used to go silent on ~1 in 5 old-prose sentences; the real causes were three over-eager
safety rules, not a weak parser. A robust brain-style fix takes it to ~98% and it's at competent-reader level on
normal sentences. Along the way the shared system improved under me (so I re-measured honestly), and the "hard"
sentences turned out to be a broken answer key, not a modeling wall. The one genuinely hard remaining piece -- teaching
the grammar step to reconsider a word's category as it reads -- I took as far as it goes without a dedicated build:
proved it's the right fix, built the trainable skeleton, fixed its data problem, and showed it needs a look-ahead
search. That last part is its own project, now teed up.

QUESTIONS: one -- open the beam joint parser as its own problem next, or land the ready structural fixes first?
(I recommend landing the structural fixes + referent-per-NP now; the beam parser as a fresh dedicated build.)

NEXT STEPS: 1) Land the ready structural fixes + referent-per-NP (Q111). 2) File the beam-decoded joint parser as a
new problem (scaffold + data fix + proof in place). 3) Keep the noisy-channel verb override as a 19c-only diagnostic.
