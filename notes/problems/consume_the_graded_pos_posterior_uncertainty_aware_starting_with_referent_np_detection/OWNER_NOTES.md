---
owner_verdict: DONE
---

SUBMISSION — consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection
STATUS: PARTIAL (a full-pass LOCATED NEGATIVE on the brief) + a deeper drill that found the REAL fix + a READY
optimization + one CLEAR next problem. WIP until owner_verdict: DONE. Glass-box, NO LLM, NO hdlab written (solver
scope; proposed diffs below). Ledger clean (malformed/incomplete: 0).

REVERIFY:
  .venv/Scripts/python.exe verification/test_structural_patient_optimization.py            # the WIN, 3/3
  .venv/Scripts/python.exe verification/test_graded_pos_consumption_located_negative.py     # the brief negative, 4/4

WHAT THE BRIEF ASKED vs WHAT'S TRUE (disk outranks the brief):
- Brief: consume the graded POS posterior in referent_per_np (PROPN vs NOUN) to fix who-did-what/coref.
- REFUTED on disk: referent introduction is PROPN<->NOUN-INVARIANT (0/3669 head diffs; both are in NOMINAL) and
  coref never reads UPOS. Soft-nominal recovery = +0.0000 to live who-did-what (twin LOSES). The only channel
  PROPN<->NOUN flips is ANIMACY, which -- even fed brain-foundationally -- is a subordinate cue in word-order-
  dominant English and does NOT beat the 1-best. A rigorous located negative = FULL PASS per the bar.

THE DEEP DRILL (owner: "something is wrong -- understand what"): TWO errors, both confirmed on a CLEAN instrument.
  (1) FIDELITY: our who-did-what is the brain's DAMAGED-BACKUP route -- flat cue/position selection, NO structure
      (route_predicate_arguments->hybrid_role_patient "takes NO arc heads"). The brain reads roles off the PARSE
      (subject/object) + verb-frame binding + VOICE remapping (Hagoort MUC; Levin-Rappaport-Hovav). This is exactly
      the algorithm agrammatic Broca's aphasics fall back to -- our precise failure profile. (hdi_research, cited.)
  (2) INSTRUMENT: the role-balanced gold I first measured on is CONFOUNDED -- crowd QA-SRL *question* voice, patients
      that are coref ANTECEDENTS not the surface argument, the reader's OWN parse stapled to the roles, an engineered
      62%-passive distribution, and cue weights TRAINED on it (circular). My iters 1-4 "meaning wall" was its artifact.

THE CLEAN TEST (UD-EWT gold relations; patient := obj|nsubj:pass + voice; non-circular):
  route                         patient (TEST / TRAIN)
  live HEURISTIC (cues+position)   0.673 / 0.730
  STRUCTURE-FIRST (our parser)     0.734 / 0.794     -> +0.06, buildable now
  STRUCT + heuristic fallback      0.760 / 0.806     -> +0.088 / +0.076  ** THE WIN **
  ceiling (perfect parse)          0.912 / 0.936     -> human-level; residual is PARSER quality

THE WIN (ready to land): structure-first PATIENT (read the object/promoted-subject off the parse's grammatical
relations + voice remapping; coordination/control sharing; heuristic fallback; AGENT kept as-is).
  - GENERALIZABLE: ZERO tuned parameters (grammatical relations + voice = universal grammar, not corpus-fit cue
    weights like the circular Competition Model). Proven on UD-EWT test AND train.
  - NO-REGRESS: wired through the LIVE reader on a real doc -> read completes, EVERY non-role output byte-stable
    (n_events / entities / coref_acc / causal / timeline / targets), only the patients change (126/219, the fix).
  Bodies: experiments/exp_structural_role_reader_v1.structural_roles + exp_structural_patient_noregress_v1.hybrid_patient.

>>> THE CLEAR NEXT PROBLEM TO FILE: improve_the_parser_verb_argument_attachment_for_who_did_what
  The remaining +0.15 (0.76 -> 0.91 ceiling) is ENTIRELY the parser's verb->argument attachment. Prototyped the
  brain-faithful post-hoc binder (verb-frame-guided binding, exp_parser_role_attachment_v1): it recovers only ~9% of
  the gap (+0.017); ignoring the parse COLLAPSES to 0.58 (the attachment is load-bearing); the bulk of misses are
  ~45% wrong-dependent + ~25% wrong-head -- genuine parse errors. THE IDEAL: a verb-frame-guided, LABELED dependency
  parser that binds arguments into valency slots DURING parsing (glass-box, incremental, NOT a batch LLM) -> reaches
  0.91. This is the genuine remaining who-did-what lever. Spec in WHAT_WAS_WRONG_structure_not_meaning.md.

PROPOSED hdlab CHANGE (Q111 -- strategy lands, default-safe, witness is the gate): in
hdlab/predicate_argument_frontend.route_predicate_arguments (already called with the parse `heads`), compute the
THEME/patient STRUCTURE-FIRST (verb's nominal dependents: object [active] / promoted subject [passive] via
robust_passive; coordination share; heuristic fallback when no core object). Keep the AGENT as-is. Re-verify the live
who-did-what on the board docs before default-on.

FILES (experiments/ + verification/ + own folder only; NO hdlab written):
  experiments/exp_whodidwhat_ud_structural_v1.py, exp_structural_role_reader_v1.py,
  exp_structural_patient_noregress_v1.py, exp_parser_role_attachment_v1.py (+ the earlier graded/chain cells)
  verification/test_structural_patient_optimization.py, test_graded_pos_consumption_located_negative.py
  notes/problems/<slug>/{SOLVED.md, WHAT_WAS_WRONG_structure_not_meaning.md, MECHANISM_DIFF_where_we_lose_signal.md,
                         CHAIN_SIGNAL_LOSS_TRACKER.md}

KEY REALIZATIONS: (a) read the CONSUMER before believing an error-share -- "PROPN<->NOUN=28% of tagger errors" never
reaches referent_per_np (both in NOMINAL). (b) A twin that LOSES while the arm ties the floor = a correct-but-
SUBORDINATE cue, not a broken one (animacy). (c) When results feel wrong, AUDIT THE RULER -- the who-did-what gold was
confounded + circular; the clean UD instrument inverted the conclusion from "meaning wall" to "structure/parser". (d)
The brain reads roles off STRUCTURE; flat cue-selection is the LESIONED route -- agrammatism is the tell.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md): who-did-what role assignment is the brain's STRUCTURAL route (parse ->
grammatical relations -> verb-frame binding -> voice remapping), NOT flat cue-competition; the live reader implements
the heuristic backup only. Structure-first patient is +0.088 on clean gold, no-regress. Flag the role-balanced gold
as an invalid instrument (confounded/circular); use the UD-EWT structural gold.

TLDR: The brief's idea (use ranked grammar-guesses to fix who-did-what) doesn't pay off -- I proved it and, drilling
into why, found the real problem: we decide "who was acted on" with the brain's damaged BACKUP trick (guess from word
order) instead of its real method (read it off the sentence's grammar). On a fair, clean answer key, reading it off
the grammar is ~8 points better, uses no tuned dials so it generalizes, and breaks nothing else in the reader -- ready
to switch on. To reach human level from there needs a better PARSER (attach each verb's subject/object correctly),
which is the clear next project I've scoped and pointed to in the docs.

QUESTIONS: none. NEXT STEPS: (1) land the structure-first patient (ready win, witness-gated); (2) FILE
improve_the_parser_verb_argument_attachment_for_who_did_what (the +0.15 parser-core lever); (3) re-base who-did-what
eval on the clean UD gold, never the confounded role-balanced gold.
