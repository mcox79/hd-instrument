---
owner_verdict: DONE
---

Problem: role_assignment_is_untested_on_archaic_literary_prose — SOLVED, ready for review (WIP until owner_verdict: DONE).

DISK OUTRANKS THE BRIEF: the brief feared spaCy's grammatical-role labels are "systematically DEGRADED on
archaic long-sentence prose," silently capping every organ that reads them. Measured end-to-end, that wholesale
fear is REFUTED — but a real, narrow, brain-foundational effect sits underneath it, and I built the brain's fix.

WHAT I MEASURED (witness: .venv/Scripts/python.exe verification/test_role_parse_accuracy_archaic.py  # 26/26):
- Parse accuracy, archaic vs modern: spaCy's subject-ID is NOT degraded on 19c literary prose — natural LitBank
  0.94 >= modern textbook 0.89, FLAT to 40+ token sentences (70% of literary subjects are easy pronouns). The
  archaic-vs-modern gap is not CI-separable (perm null p95 0.098 > gap 0.051). The wholesale confound is RETIRED.
- Where it DOES fail (register isolated by content+length-matched minimal pairs): subject-verb INVERSION
  ("replied he" -> spaCy tags "he" a DIRECT OBJECT) + archaic morphology, +0.22 [0.087,0.391]. On real dialogue-
  tag inversion spaCy is 0.47. Incidence: ~4-12/1000 verbs, concentrated in dialogue; archaic morphology 0.77%.
- Downstream cost ~0: the coref cache's roles are provably spaCy-derived (19 nominative-pronoun-as-OBJECT labels
  a human would never write). Correcting ALL 59 errors moves coref accuracy by -0.0009. A shuffle control DOES
  move it (0.61->0.53) and a sensitivity curve shows ~10-20% error is needed before coref degrades — spaCy's
  actual ~0.6% is far below. Confound real but IMMATERIAL to aggregate coref.

THE BRAIN-FAITHFUL FIX (bar's fix path; PINNED via two research drills — Competition Model / eADM; Bresnan,
Levin & Rappaport Hovav, Iatridou & Embick; Pinker & Ullman):
- A glass-box, POSITION-DOMINANT + cue-OVERRIDE subject stage (NOT an external parser — invariant respected):
  case (nominative pronoun) / conditional-auxiliary-trigger (were/had/should) / locative inversion
  (unaccusative-verb-class + obliqueness + number-agreement) / quote-aware reporting-frame, plus a small STORED
  archaic-morphology lexicon. Keeps the parser's subject on canonical cases (no regression).
- Recovers real dialogue inversion 0.47 -> 0.83 CI-separated, info-free twin 0.23 LOSES, register-invariant
  (archaic 0.91 ~= modern 0.96), lifts modern 0.76 -> 0.89 (no regression), and the full cascade recovers the
  collapsed full-NP inversions (n=8 hand-built demonstration 1.00; cues PINNED, not fit to the set).

PUSHED FURTHER (three rounds), and it paid off:
- Tested my own "cue-first parser" instinct and REFUTED it (a cue-first REPLACEMENT loses — worse than spaCy on
  canonical cases); the faithful shape is position-dominant + override, exactly graded_role_assigner's design.
- Register-invariance at the EXTREME (real Shakespeare EME, 165x denser morphology): spaCy's POS tagger COLLAPSES
  (tags "thou" PRON 0.1%) and subject accuracy falls to 0.07, but the brain-faithful cascade + stored lexicon
  RECOVERS it to 0.75 (thee-accusative control 0.78 — it respects case). Validates the PINNED stored-morphology
  account and shows the brain's method is register-invariant where the statistical tool is not.

ADJACENT COMPONENTS EVALUATED (candidate next problems, on disk with evidence):
- graded_role_assigner (islanded, used_by=tests only) is the landing target but its cues are order/adjacency/
  passive/gap/unacc/byagent/animacy — it has NO case, conditional-trigger, reporting-frame, or subject-inversion
  cue. Extend it with the cascade above; it is the LIVE fix.
- incremental_parser fails dialogue inversion 0.000 (position-only left-corner bind) — needs a case override.
- The POS tagger is the foundation and collapses on EME — same brain-faithful fix (stored lexicon + cue-based).

FOR STRATEGY (Q111 — you land hdlab): add the position-dominant + cue-override subject stage to
graded_role_assigner (reference impls: experiments/exp_role_cue_repair_inversion_v1.py `repaired_subject_span`
and exp_role_cue_first_subject_v1.py `full_cue_subject`), rebuild data/litbank/who_did_what_events.json through
it, and fold the AUDIT UPDATE (corpus-age confound: SUSPECTED-UNMEASURED -> MEASURED-BOUNDED) into
BRAIN_FOUNDATIONAL_AUDIT.md. Then file the two next problems: (1) an archaic-morphology POS/role lexicon
(material for EME/KJV, gated on those corpora being on the live path); (2) a case-override for incremental_parser.

FILES (no hdlab/ touched): experiments/exp_role_{parse_accuracy_probe,confound_incidence_litbank,
confound_downstream_coref,cue_repair_inversion,cue_first_subject,shakespeare_eme}_v1.py;
verification/test_role_parse_accuracy_archaic.py (26/26); the problem folder's SOLVED.md + gold jsonl + builders.
Ledger --check: EXIT 0.

VERDICT: the corpus-age parse suspicion is RETIRED for the aggregate (organ-level conclusions stand), with one
characterized bounded exception (inversion) plus a register-extreme (EME) case, for which a complete, PINNED,
glass-box brain-faithful fix is built and proven — ready to wire.
