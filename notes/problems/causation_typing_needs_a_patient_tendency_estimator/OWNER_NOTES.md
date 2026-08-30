---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — causation_typing_needs_a_patient_tendency_estimator            STATUS: SOLVED (WIP → owner DONE)
hdlab/ UNTOUCHED (proposed 4-cue diff, Q111). AWAITING owner_verdict: DONE.
REVERIFY:
  .venv/Scripts/python.exe verification/test_patient_tendency_estimator.py            -> 22/22  (constructed estimator)
  .venv/Scripts/python.exe verification/test_patient_tendency_realtext_modern.py       -> 8/8    (MODERN real-text serve)
  .venv/Scripts/python.exe verification/test_patient_tendency_generalization.py        -> 3/3    (brain-like generalization)
  .venv/Scripts/python.exe tools/problem_ledger.py --check                             -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
WHAT WAS BUILT: a glass-box PATIENT-TENDENCY estimator feeding the Wolff force-dynamic CAUSE/ENABLE typer,
resolving the one measured wall (tendency-ambiguous verbs, lexicon-capped at 0.500). FOUR force-dynamic cues,
combined as a Wolff patient-side FORCE SUM (PINNED: Wolff 2007 / Wolff & Barbey 2015; drill-validated):
  (1) affector-MAGNITUDE (proven first term, reused)  (2) patient-AFFORDANCE (core-physics disposition +
  in-sentence adjectives + negation)  (3) DIRECTIONAL/gravity (IS-A-grounded inclined-surface schema)
  (4) affector-LETTING role (Talmy causing-vs-letting, 4th cue, drill-grounded).

RESULT (CAUSE-vs-ENABLE on tendency-ambiguous verbs):
  • COMBINED n=40 (constructed minimal pairs, bootstrap 2000x): 1.000 [1.000,1.000] vs lexicon-only floor
    0.500 (+0.502 CI-sep) AND vs the PROVEN affector-magnitude-only term 0.675 (+0.327 CI-sep). Per-cue:
    +0.505/+0.504 on the magnitude-SILENT affordance/directional sets; +0.000 NOT_SEP where magnitude is
    present (honest — the first term already suffices there). HELD-OUT (fresh affectors/patients/cues) 1.000.
  • MODERN real-text (NOT McGuffey — age-confounded): n=13 verbatim MCScript2/UD-EWT, extraction given,
    solver-adjudicated → OUTPUT 7/7 on tendency cases vs lexicon-only 1/7; DEFERS 6/6 on agentive manipulation.
FLOORS: lexicon-only 0.500 (recomputed on-population) AND the proven affector-magnitude term 0.675 — both
  beaten CI-separated. Majority-class + oracle (1.000) also reported.
CONTROLS (each excludes something): info-free TWIN (permuted cue contributions) loses (full_lo 1.000 > p95
  0.625); null p95 0.650; per-term ABLATION (no single cue reaches full → they COMBINE); COMBINATION-RULE
  discriminator (CONFLICT set, minority cue rotating → force-sum 1.000 vs every winner-take-all rule 0.667,
  +0.337 CI-sep → the sum is ADDITIVE, not WTA); onset-cause NEGATIVE control (switch/trigger never ENABLE);
  weight-sweep min 1.000 over 27 configs; held-out generalization; positive-control minimal pairs the lexicon
  cannot (ball-vs-crate, down-vs-up, nudge-vs-shove, key-letting).
BRAIN-FOUNDATIONAL (2 drills, all cues PINNED): force-SUM + concordance read-out (Wolff 2007); patient
  disposition + gravity as force terms (Wolff & Song 2003); causing-vs-letting (Talmy 1988); combination is
  additive integration (proven). NEURAL ENABLE-vs-CAUSE dissociation = an honest GAP (UNPINNED). External
  grounding: affordance labile-half corroborated by CSKG CapableOf (13 patients, 0 contradictions), inert-half
  KB-absent = core physics; verb-gate DERIVED from the causative-inchoative alternation (VerbNet roll-51.3.1 +
  flow), not a hand-list; the inclined-surface schema IS-A-grounded (generalizes to novel grounds: knoll/ravine).
KEY REALIZATIONS: (1) isolate each cue → the added terms beat the proven term only where its cue is SILENT
  (coverage, not a better answer on the same input). (2) prove the COMBINATION RULE (additive vs WTA), not just
  the cues. (3) WordNet carries CATEGORY not DISPOSITION → measured, so affordance is core-physics, but IS-A
  grounding DOES generalize the taxonomic features (ground/physical). (4) LETTING is a different mechanism in
  kind (affector removes a restraint), not patient tendency — surfaced by reading the primary literature, not
  forcing the brief's frame. (5) real text forced two fixes the brief never mentioned: LEMMATIZATION (without
  it, abstains on 100% of real text) and brain-like GENERALIZATION via grounded conceptual features (not word
  lists — over-fires dropped 17→3/318 on UD-EWT).
AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md, causation entry): the tendency input is now a 4-cue additive
  force-dynamic estimator (magnitude+affordance+directional+letting); affordance labile-half CSKG-corroborated,
  inert-half core-physics; verb-gate causative-inchoative-derived; NEURAL ENABLE-vs-CAUSE dissociation = GAP.
PROPOSED hdlab DIFF (Q111 — do not land here): promote experiments/_patient_tendency.py as the tendency/role
  estimator feeding force_dynamic_type's missing patient-tendency bit; for a tendency-ambiguous verb + endstate
  reached, sign(patient_tendency_signal) → ENABLE/CAUSE, else keep the verb lexicon (abstain-to-lexicon is a
  feature). No change to graded_coref_pick / candidate_generator / hd_fact_store.
HONEST CAVEATS (withdraw first): the constructed 1.000 is a construction artifact — stand on held-out 1.000 +
  the n=13 modern point estimate (solver-adjudicated) + the generalization probe. NO labeled real-text accuracy
  at scale. On unfiltered web text the estimator is CONSERVATIVE (fires 0.9%) and correctly abstains on the
  figurative/agentive majority; the residual over-fires are WORD-SENSE/attachment errors → the next problem.
════════════════════════════════════════════════════════════════════════════════════════════════════
THE NEXT STEP (dispatch this): a glass-box WORD-SENSE / literal-vs-figurative gate + parse-based amod-ATTACHMENT
  for the force-dynamic reader, so it engages only on LITERAL, correctly-attached physical events. This is the
  brain's generalization mechanism (word-sense disambiguation + grounded simulation) and the DEMONSTRATED
  boundary of this estimator — every residual over-fire is a sense/attachment error. Convergent with the
  parent's `no_glass_box_verb_sense_disambiguation`. BAR: raise fire-PRECISION on unfiltered modern text (the
  UD-EWT generalization probe is the ready testbed) without losing the literal cases; info-free twin LOSING.
  ⚠️ This is a DIAGNOSIS + DIRECTION with strong evidence, NOT a proven solution — dispatch as a problem with
  its own bar/floors, not a known implementation. (Secondary: real-text accuracy at scale w/ a 2nd adjudicator;
  land the 4-cue diff.)
FILES: experiments/{_patient_tendency, exp_patient_tendency_estimator_v1, exp_patient_affordance_cskg_grounding_v1,
  exp_patient_tendency_realtext_modern_v1, exp_patient_tendency_generalization_udewt_v1}.py; verification/
  {test_patient_tendency_estimator, _realtext_modern, _generalization}.py; SOLVED.md + research note. hdlab/ UNTOUCHED.
TLDR: the reader could tell "caused" from "let happen" only from the verb, and coin-flipped on ambiguous verbs
  ("the wind opened the gate" vs "the key opened the gate"). I built the brain's way — add up force cues about
  the thing itself (how hard the push was, what it's physically like, which way gravity points) plus whether the
  actor removed a restraint (a key) or applied force (the wind). It's perfect on clean tests, beats even the
  previously-proven single cue where that cue is silent, works on real modern sentences (a heavy door → caused,
  a ball rolling down → let), and — importantly — I made it GENERALIZE the way the brain does (grounding words
  in concepts, so "ravine" works though it never saw it), not by memorizing word lists. It correctly stays quiet
  on figurative uses; the only remaining misses need knowing which sense of a word is meant — a real, separate
  brain skill (word-sense disambiguation), which is the next problem. QUESTIONS: none.
════════════════════════════════════════════════════════════════════════════════════════════════════
