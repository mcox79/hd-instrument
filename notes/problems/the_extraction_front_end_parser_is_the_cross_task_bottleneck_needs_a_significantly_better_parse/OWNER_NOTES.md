---
owner_verdict: DONE
---

SOLUTION SUBMISSION -- the_extraction_front_end_parser_is_the_cross_task_bottleneck_needs_a_significantly_better_parse

STATUS: SOLVED (witness verification/test_parser_improved_operator.py 8/8; problem_ledger --check clean;
WIP until owner_verdict: DONE). Solver: opus 4.8.

THE PROBLEM I WAS ASSIGNED: the reader's glass-box parser is the definitively-measured cross-task ceiling, but
it is NOT one job -- >=8 downstream needs each want a different property of the parse, and a year of work showed
fixing one breaks/fails to help another. Significantly improve the substrate's OWN glass-box parser so it serves
ALL its downstream needs at once (raise who-did-what CI-sep, hold a UD-EWT UAS gain, compound to a 2nd task, NOT
regress recall/POS/19c, report a confidence distribution) -- or locate precisely which need cannot be
co-satisfied and why. Multi-objective; glass-box; no external LLM at inference.

WHAT I BUILT + HEADLINE RESULT:
  * Arc-eager incremental parser + Zhang-Nivre RICH NON-LOCAL STRUCTURAL FEATURES, promoted to a loadable
    parse() operator: UD-EWT test UAS 0.775 -> 0.8421 gold-POS / 0.8053 pred-POS (+0.067/+0.061 over the live
    richfeat), seed-robust across 3 seeds (gain +0.024..+0.026 CI-sep).
  * CALIBRATED ABSTAIN/DROP signal built: ECE 0.153->0.026, risk-coverage rises (twin flat), abstained set
    concentrates errors 4.2x -- the "expose drops, don't confabulate" signal predict_revise needs.
  * Controls: info-free head-shuffle twin loses +0.20; shuffled-confidence twin ~0.50; global-beam training
    HARD_FAIL on disk (0.809 vs 0.811) and word-cluster features null (+0.0015) -- the ~0.81 ceiling is crossed
    ONLY by rich STRUCTURAL features (+0.024); residual to spaCy is a representation/domain gap.

THE CENTRAL RESULT (owner-driven re-center): a PRECISE, measured PARSER SERVICE SPEC. Reading all 9
brain-foundational consumers' submissions and MEASURING each one's head-dependence, one parser serves them all iff
it provides: (1) accurate UPOS (the universal floor), (2) verb lemma, (3) voice, (4) accurate 1-best PP-CHAIN
attachment (the SOLE high-precision head demand + the only measured ceiling, oracle-PP +0.10..+0.18), (5) a
calibrated abstain/drop signal. It does NOT need general who-did-what head-accuracy (the patient organ is
HEAD-INDEPENDENT and already label-free -- corrects my own earlier over-claim), dependency LABELS (harmful for
roles; wanted only by two argument-structure gates), or an n-best parse DISTRIBUTION (graded_competition builds
its own; MAP theorem). Coherent with the 19c wall: 93% of 19c who-did-what failures are PP-EMBEDDING -- the 19c
wall IS the PP-attachment signal.

HONEST SCOPE: general UAS improved (real, verified) but is NOT the load-bearing lever. Of the 5 spec levers, the
calibrated ABSTAIN is BUILT+witnessed; UPOS register-robustness and PP-CHAIN attachment are DATA-BOUNDED follow-on
problems (need gold target-register POS/parses, not on the shelf). So this is "improved substrate + precisely
specified + one lever built," not "fully optimized" -- and it does not claim to be.

NEXT STEPS FOR STRATEGY (full detail in SOLVED.md):
  A. INTEGRATE (on owner-DONE): re-verify 8/8 + ledger clean; land the 3 default-off wires -- (i) arc-eager+rich
     parse operator as hdlab/arceager_parser.py + asset arceager_dynamic_ud_ewt.npz behind a parser=arceager
     flag; (ii) attach_conf -> graded_competition (difficulty currency, N7); (iii) calibrated abstain ->
     predict_revise drop trigger -- AND ROUTE predicate_argument_frontend through the improved parser (this is
     where the parser gain lands: matrix-verb F1 +0.015, PP/oblique-role F1 +0.027, feeding world_state ARG2).
     NO label-free wire needed (the live patient organ hybrid_role_patient is already head-independent +
     label-free). Fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md sec.2b; register + WIRING_MAP.
  B. HOW TO REALIZE FULL GAINS: wires (i)-(iii) + the predarg routing are realizable NOW (measured). The FULL
     gains are DATA-BOUNDED -- file two follow-ons: #1 UPOS register-robustness, #2 PP-CHAIN attachment via
     register-native parse training; BOTH require gold target-register (19c/literary) POS+parses NOT on the shelf
     (self-training, word-clusters, global-search all refuted), so the path is DATA-acquisition + register-native
     training, not more tuning of this parser. Lower: targeted obj/obl/cop labeler for the two argument-structure
     gates only; default-on the graded role path; retire arc_labeler from roles; re-found the semantic_parser
     placeholder.
  DO NOT RE-OPEN (refuted): general-UAS->spaCy via global search / word-clusters; buried-subject regression
     (resolved by rich features); heads-into-patient-organ (hurts 19c); parser-distribution-as-accuracy (MAP).

FILES: experiments/exp_arceager_parser_operator_v1.py (+ model data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz),
exp_arceager_richfeat_transition_v1.py, exp_arceager_calibrated_abstain_v1.py, exp_parser_gap_decomp_v1.py,
exp_parser_multiobjective_v1.py, exp_parser_argument_attach_v1.py, exp_parser_through_real_organs_v1.py,
exp_predarg_frontend_organ_v1.py, exp_19c_signal_loss_v1.py, exp_19c_selection_failure_v1.py,
exp_19c_pp_attachment_prototype_v1.py, exp_tagger_prototype_19c_v1.py; verification/test_parser_improved_operator.py;
notes/problems/<slug>/{SOLVED.md, PARSER_SERVICE_SPEC_brain_foundational.md,
BRAIN_FOUNDATIONAL_CHAIN_first_step_fidelity.md, CONSUMER_FIDELITY_MAP.md, FINDINGS_disambiguation.md}. NO hdlab/ writes.
REVERIFY: .venv/Scripts/python.exe verification/test_parser_improved_operator.py

TLDR (plain English): the grammar-reader is genuinely better (77.5%->84.2%) and now flags its own uncertain
attachments 4x better than chance. The bigger result is a precise contract for what the nine downstream parts
need from it -- good part-of-speech tags, verb lemma, active/passive, correct "to/from/in/at..."-phrase
attachment, and honest uncertainty -- NOT a higher grammar score, grammatical labels, or competing parses.
Two-thirds of the parts don't use the parse tree for "who did what" at all. The one thing a better parser truly
buys (10-18 points) is preposition-phrase attachment, which is also exactly the 200-year-old-prose wall. I built
the uncertainty signal now; the tagging + PP-attachment levers need target-register training data and are the
top filed follow-ons.

QUESTIONS: none. Awaiting your verdict; nothing pushed or written to hdlab/.
