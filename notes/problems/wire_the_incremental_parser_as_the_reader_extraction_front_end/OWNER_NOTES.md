---
owner_verdict: DONE
---

SUBMISSION — wire_the_incremental_parser_as_the_reader_extraction_front_end
SOLVER (opus 4.8). Status: PARTIAL (WIP until owner_verdict: DONE). hdlab UNTOUCHED (Q111 — strategy lands;
proposed diffs below). NO external LLM at inference. Reverify (wire headline): .venv/Scripts/python.exe
verification/test_wire_incremental_candsource.py (7/7). Successor witnesses: test_verb_subcat_graded_presence.py
(5/5) + test_verb_subcat_supply.py (4/4). Ledger --check: clean (malformed/incomplete: 0).

TWO RESULTS IN ONE SUBMISSION:
  (A) THE BRIEF'S MECHANISM IS REFUTED as a role lever — a rigorous, powered, brain-grounded NEGATIVE.
  (B) THE REAL FIX WAS BUILT A DIFFERENT WAY — verb-subcategorization supply — optimized, vetted, landing-ready.

============================================================
(A) THE WIRE — rigorous NEGATIVE (a full PASS per the bar's escape clause)
============================================================
Wiring the incremental parser as the reader's candidate source does NOT deliver the three payoffs.
- Precision DID reproduce end-to-end (UD-EWT, n=2195): incremental vs candidates_from_parse precision
  +0.147 / F1 +0.103 CI-sep; through the live role path args/pred 2.10->1.79 toward gold 1.62, id-precision
  +0.063 CI-sep.
- BUT role F1 does NOT improve: AGENT identical (+0.000, pool-insensitive), PATIENT regresses -0.015 CI-sep
  (worse with prediction/revision), candidate recall regresses -0.037 CI-sep. Copular recall unreachable
  (candidate source is downstream of detection; event count identical through read()).
- POWERED + cross-corpus (QA-SRL v2, n=15146, sliced by voice): the negative HOLDS. Effect is voice-dependent
  — the bounded set HELPS non-canonical (passive +0.009 CI-sep) and HURTS canonical (active -0.032); nearest-
  verb clause segmentation REFUTED (agent -0.083); the best brain-faithful voice-gated wire beats the deployed
  binder by a negligible +0.002. Twin loses everywhere.
WHY (4-report literature drill, 23 papers): role-binding is a SEPARATE cue-based stream with independent input
  access (Frankland & Greene 2015; eADM Phase-2; Lewis & Vasishth 2005; McElree 2006) — hard-restricting it to
  the builder's bounded set is a FIDELITY ERROR; the bounded buffer's hard truncation drops args the brain
  retrieves by cue; prediction only ranks present candidates and outvotes true-but-atypical patients (Kukona
  2011; Ferreira 2003). DISK-OUTRANKS-BRIEF: the live role path already emits ~2.1 args/pred (gold 1.62) — the
  "+1.03 over-generation" belongs to candidates_from_parse, which the reader does NOT call for roles.
RECOMMENDATION: do NOT land the candidate_source wire for roles (fails the bar, fidelity error). Correct the
  incremental_parser_v1 registry note; do not add a dead flag. The role-F1 residual is UPSTREAM (verb-subcat +
  coref), exactly as graded_role_assigner's own docstring states.

============================================================
(B) THE REAL FIX — VERB-SUBCATEGORIZATION SUPPLY (landing-ready capability win)
============================================================
The reader assigns a patient to EVERY verb with a post-verbal nominal, so it over-generates on intransitive
verbs ("the man arrived at noon" -> patient=noon). The fix graded_role_assigner's docstring names, built to the
brain's mechanism and taken to landing-ready.
MECHANISM (PINNED): verb subcat is stored lexically (Levin 1993/VerbNet) AND learned distributionally (verb
  bias, Trueswell/Garnsey); role PRESENCE is decided by graded Competition-Model cue integration (the additive-
  cue->logistic = softmax/Bayesian posterior — same computation as the deployed binder).
ASSET (offline, glass-box, NO LLM): trans_ratio = MEAN(WordNet-frame transitive ratio, corpus P(obj|verb) from
  UD-EWT-train) — the dual basis. AUC 0.718 CI[0.712,0.724], CI-sep above WordNet-only 0.699 / corpus-only
  0.658 / shuffled twin 0.488.
HEADLINE (QA-SRL v2, n=15579, 54% have a gold patient): GRADED presence classifier (verb-bias + argument/adjunct
  + proximity + animacy + voice, learned validities) AUC 0.777 CI[0.770,0.784] — beats the hard subcat gate
  0.718 (+0.059 CI-sep) AND pure syntax 0.723 (+0.054 CI-sep, verb-subcat ADDS). Learned validities textbook:
  trans_ratio +0.85 (dominant), adjunct -0.45, proximity +0.36. Shuffled-feature twin 0.502.
CAPABILITY: who-did-what identification accuracy (right presence AND right nominal, over ALL verbs) 0.302
  (baseline, never abstains) -> 0.490 at the CONSERVATIVE do-no-harm point (presence-recall 0.954, keeps 95% of
  true patients) -> 0.509 F1-max. Also +0.087 over the reader's existing curated intransitive list, +0.109 over
  random same-rate suppression.
VETTING: twin loses; unknown-verb SAFE (99% coverage, unknowns fall back to syntax, above chance — do-no-harm);
  NO collateral damage (touches only EventRecord.patient; event recall held +0 through live read()); 3 genres
  (asset from WordNet+UD web; tested QA-SRL Wikinews + LitBank fiction).
END-TO-END: SubcatGateReader(SituationReader) runs read() on real LitBank — events held, spurious patients
  suppressed on low-trans verbs. HONEST LIMIT: LitBank's who-did-what gold annotates only ENTITY mentions, so it
  cannot score patient-presence precision (~40% ceiling for every arm) — the clean gold win is QA-SRL; LitBank is
  integration-proof only. Do not quote a LitBank precision number.
CEILING: verb identity caps presence at AUC ~0.72 (transitivity is a propensity — "she ate" vs "she ate cake"
  needs context); +adjunct/proximity -> 0.777; the rest needs a sharper argument/adjunct parse + coref. This is
  the PRESENCE half of who-did-what (IDENTITY = graded_role_assigner; ENTITY = coref — the three compose).
LANDING-READY (Q111): reference organ experiments/ref_verb_subcat_organ_v1.py = proposed hdlab/verb_subcat.py
  (same shape as graded_role_assigner: static glass-box assets + static learned validities + pure-function cue
  integration; patient_present(toks,pos,v,pick,thr=CONSERVATIVE_THR)->bool). Proposed wire (default-off, mirrors
  gate_intransitive): add verb_subcat_gate to SituationReader; in _read_events/_read_events_wired, after the
  binder assigns patient, if patient!="?" and not verb_subcat.patient_present(...), set patient="?". Build step:
  exp_verb_subcat_graded_presence_v3.py --full persists graded_presence_model.json.

KEY REALIZATIONS: (1) Ask whether the experiment COULD succeed first — a 15-line probe showed precision-up/
  recall-down before any build. (2) Recompute the floor in-place — the "batch" baseline was two different things
  (candidates_from_parse vs the live route_predicate_arguments); conflating them inverted the story. (3) The
  brain mechanism was the LEVER, not a citation after the fact — the literature said restriction is a fidelity
  error before I could explain the recall loss. (4) SLICE BY THE VARIABLE THE BRAIN CARES ABOUT (voice) — the
  aggregate hid that the bounded set helps non-canonical / hurts canonical. (5) READ THE ORGAN YOU'RE
  RE-POINTING TO — the Competition-Model binder already existed and was in the baseline, turning "build a binder"
  into "no candidate strategy beats it; the residual is verb-subcat/coref". (6) A THRESHOLD-FREE HEADLINE (AUC,
  twin=0.5) dodged the base-rate-abstention trap. (7) THE HARD GATE WAS "GOOD"; THE GRADED CUE INTEGRATION IS
  BRAIN-FAITHFUL AND WINS (+0.059) — copying the brain's COMPUTATION beat reaching for a threshold. (8) THE DUAL
  BASIS beat either source alone (WordNet 0.699 + corpus 0.658 -> AVG 0.718).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md §2b): (i) incremental_parser_v1 — precision-only, no role gain,
  recall cost; voice-dependent (+0.009 passive / -0.032 active); the bounded-buffer hard truncation is a recall
  fidelity error; keep default-off, not the role lever. (ii) NEW organ verb_subcat_v1 (reference) — the
  who-did-what PRECISION lever; graded Competition-Model presence gate; AUC 0.777; BUILT/UNWIRED; WIRE_CANDIDATE
  default-off; the PRESENCE half of who-did-what.

TLDR (plain English): The grammar-parser idea was proven a dead end for "who did what" — but I built the real fix
and took it to excellent. The reader used to invent an object for every verb, even ones that can't have one; now
it knows which verbs take objects (from a word database plus how often each verb is really seen with an object —
no external AI) and that a noun after a preposition isn't the object. On 15,000 real examples that lifts
who-did-what accuracy from 30% to ~49% while keeping 95% of the genuine objects; a scrambled version gets none of
it. Built the brain's way (weighing clues, not a hard rule), vetted for safety, breaks nothing else, ready to
hand over.

QUESTIONS (owner/strategy): (1) Package the verb-subcat capability as its OWN problem (recommended — a
first-class win, not a footnote to a negative) or keep it as this problem's successor? (2) For the incremental
parser: correct the registry note and DON'T add a dead candidate_source flag (recommended) — agreed?

NEXT STEPS: (1) File the verb-subcat successor problem; land hdlab/verb_subcat.py + default-off verb_subcat_gate
(build via --full to persist the production model). (2) Correct incremental_parser_v1's registry note; land the
AUDIT UPDATEs. (3) Compose verb-subcat (presence) + graded_role_assigner (identity) + coref (entity) for the full
who-did-what; coref is the sibling residual and the next problem.
