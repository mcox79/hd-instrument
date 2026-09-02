---
owner_verdict: DONE
---

SOLUTION SUBMISSION -- the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold

STATUS: REFUTED (the bar's sanctioned located negative) + a fully-drilled, brain-faithful reconstruction of
what the mechanism actually is and where it pays. Witness verification/test_19c_composed_cleaned_gold.py =
22/22; problem_ledger --check clean. Solver: opus 4.8. NO hdlab/ writes, nothing pushed. WIP until owner_verdict: DONE.

RESULT (core): I built the larger cleaned gold and powered the composition margin -- and powering it KILLS the
composition-as-SELECTION effect.
  * CLEANED GOLD at scale: parser-free surface cleaner, precision-validated 98.5% vs tagger -> n=669 (3.9x the
    parent's 171); contamination ~76%.
  * POWERING KILLS IT: COMPOSED ties its agent-shuffle twin (+0.007 ns) and the marginal; the parent's +0.076
    CI-sep at n=171 separates only 7% of the time at that n = small-sample noise. Verb-keying survives; agent-
    composition does not (as a selector).
  * POSITION DOMINATES clean direct objects (nearest post-verbal = patient 0.918; the parent's "+0.158 over
    position" beat a WEAK farthest-noun floor). The residual is 89% STRUCTURAL (NP-head chunking; +0.043 CI-sep
    -> 0.961), only ~11% semantic.
  * WHY (brain-faithful, drilled): Competition Model -- English who-did-what is word-order-dominant; thematic fit
    changes SELECTION only at syntactic ambiguity, and the 19c gold is 100% active (0 passive), so that regime is
    absent. The Bicknell agent x verb effect is a PREDICTION/N400 phenomenon, not a selection choice -- wrong instrument.
  * ON THE RIGHT INSTRUMENT: composition is REAL as forward prediction (+0.032 MRR CI-sep vs marginal, +0.040 vs
    agent-shuffle) and REPRESENTATION-bounded (dead in the organ's 12-d spoke, real in a 200-d hub proxy; keep FHRR).
  * IDEAL RECIPE, proven end-to-end (reusable IdealComposedPredictor): hub rep + verb-prior centroid + precision-
    weighted composed sharpening -> beats the organ's current method +0.083 CI-sep = 2.3x held-out MRR, twins lose.
  * "MORE IDEAL" (faithful Bayesian multi-cue integration) = HONEST NEGATIVE: does NOT beat the hub-only ideal;
    the bottleneck is cue QUALITY, not the integration op.
  * ABSOLUTE-UNDERSTANDING reframe: exact next-word prediction is near an INTRINSIC ceiling (~164 patients/verb).
    On the brain's graded competence (frequency-controlled 2AFC) the system is genuinely competent: verb-level
    thematic fit 0.72; richer representation helps +0.009 CI-sep; agent-composition real +0.018 CI-sep (isolated on
    verb-typical foils); and a structured MULTI-PARTICIPANT situation model adds +0.035 CI-sep (oblique-shuffle loses).

WHAT REMAINS TO REACH OPTIMAL (full backlog; nothing landed -- strategy lands hdlab, Q111):
  A. SELECTION (order-dominant; structural/cue levers, not the store):
     A1 morphological CASE cue in graded_role_assigner -- MEASURED ABSENT; cheapest lever, better preserved in 19c.
     A2 NP-head chunker (compound + genitive) -- MEASURED +0.043 CI-sep -> 0.981.
     A3 (DATA, BLOCKED) a position-ambiguous/non-canonical 19c gold -- absent + auto-build blocked by 19c parser robustness.
  B. PREDICTION (representation is the lever):
     B1 upgrade predictive_reader -> precision-weighted composed-EXEMPLAR over a ~200-d HUB. MEASURED 2.3x MRR,
        de-risked to a class; gamma~2, no naive spoke+hub concat, keep FHRR. Highest-value wire.
     B2 a richer ATL-grade HUB (dims cap ~200 on VOCAB COVERAGE; graded-metric rep gain +0.009 CI-sep).
     B3 a structured MULTI-PARTICIPANT/discourse situation model -- MEASURED +0.035 CI-sep; build on multi-participant only.
     B4 Resnik class-conditional back-off for OOV coverage -- PROPOSED, not built (naive hypernym-averaging hurt).
  C. MEASUREMENT: C1 adopt the frequency-controlled graded 2AFC (exact-match is the wrong competence); C2 re-validate
     the prediction/2AFC/SG effects on GOLD-labeled roles (current = raw-exposure proxy triples); C3 correct the
     board's 19c who-did-what arm (~0.43 was ~76% gold contamination; honest cleaned ~0.92).
  D. ADJACENT: D1 copular is-a binding (base 0/376; filed as the_reader_has_no_copular_is_a_binding_schema).
  E. WIRING: E1 land B1 behind a default-off flag, witnessed, measured on the LIVE reader before any claim.
  Confidence: A1/A2/B1 are MEASURED + de-risked; A3/B4/C2 are the genuinely open ones (a blocked data need, a
  proposed-not-built back-off, a proxy-vs-gold validation gap).
  DO NOT re-open: parse/POS-data, PP-attachment, register-tagging, or composition-as-selection (all refuted).

FILES: 12 experiments (exp_19c_composed_cleaned_gold, _composition_powered, _whodidwhat_residual_taxonomy,
_composition_as_prediction, _predictive_reader_composition_upgrade, _composition_representation_optimization,
_ideal_composed_predictor, _ideal_recipe, _more_ideal_system, _prediction_ceiling_diagnosis, _thematic_fit_2afc,
_sentence_gestalt_multiparticipant)_v1.py + exp_composition_diagnosticity/_precision_weighted/_whodidwhat_full_system;
verification/test_19c_composed_cleaned_gold.py (22/22); notes/problems/<slug>/{SOLVED.md, BRAIN_FIDELITY_AND_
ADJACENT_COMPONENTS.md, 3x BRAIN_MECHANISM_DRILL_*.md}.
REVERIFY: .venv/Scripts/python.exe verification/test_19c_composed_cleaned_gold.py

TLDR (plain English): The job was to fix "who did what" in old prose with a memory of typical events, scored on a
cleaned answer key. Cleaning it and testing properly showed the memory idea is NOT how you pick which noun the verb
acts on -- the plain "noun right after the verb" rule already gets ~92%, exactly as the brain does English; the few
misses are grammar-chunking, not meaning. But the memory idea IS real for a different job -- ANTICIPATING the likely
word (how the brain is actually measured). Measured that way our system is genuinely good, a richer word-memory
helps, and combining doer+action, or adding a second named participant, each adds a small real boost. So: cleaned
gold delivered; meaning-idea refuted as a grammar tool, validated as an anticipation tool; the real fixes are better
grammar-chunking, a case cue old prose preserves, and a richer word memory -- all listed above.

QUESTIONS: none blocking.
