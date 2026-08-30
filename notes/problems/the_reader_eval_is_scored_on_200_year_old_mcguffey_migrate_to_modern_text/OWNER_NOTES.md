---
owner_verdict: DONE
---

Problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text — SOLVED (self-graded EXCELLENT), WIP until owner_verdict: DONE.

WHAT IT IS: the reader's role/situation-model comprehension eval was still scored on ~200-year-old McGuffey
graded readers. I migrated it to modern annotated text, revalidated the reader organ, and quantified the
corpus-age delta. NO external LLM (invariant); gold is a transparent UD-deprel rule, not LLM-fabricated.

REVERIFY: .venv/Scripts/python.exe verification/test_mcguffey_migration.py   # 19/19 scaffold-free, all recomputed

WHAT I BUILT: a MODERN situation-model role eval from UD-EWT gold parse (genuinely modern 2000s web text) in the
McGuffey gold shape — 322 passages / 679 in-scope agent/patient queries, with canonical/non-canonical + role-
varying subsets. Ran the IDENTICAL reader pipeline on McGuffey vs modern under one scorer. Coref dimension is the
owner-DONE LitBank migration (cited).

HEADLINE (rigorous, mostly NEGATIVE = a full pass per the brief; disk OUTRANKS brief):
- McGUFFEY'S ROLE EVAL IS DEGENERATE: in-scope gold is 90.85% "agent" (both gold files: 0.889 / 0.937), so a
  trivial always-agent floor scores 0.908 and the celebrated organ (vargs 0.856) LOSES to it. The original eval
  was never gated against its strongest floor. (The brief's "0.517->0.742" is corrected to disk: 0.483->0.736,
  and it loses the strongest-floor test.)
- ON MODERN TEXT the current organ does NOT clear its floor (vargs 0.605 vs floor 0.676) and COLLAPSES on non-
  canonical order to 0.325 — below the coin-flip twin (CI-separated below floor). The corpus-age confound made
  numeric: McGuffey's ~0% non-canonical rate structurally hid it.
- COREF is already off McGuffey (owner-DONE): LitBank binder GRADED 0.328 vs RAND-twin 0.106 (twin loses CI);
  graded-ACT-R 0.775 vs incumbent 0.603.

BRAIN-FOUNDATIONAL DEPTH (3 literature drills, each CONFIRMED or CORRECTED the design):
- Localized the collapse: the front-end reads thematic roles off AUXILIARIES ("has/is/was") not the content verb.
- Passive-cue fix (proven): non-canonical 0.288 -> 0.559 CI-sep, voice-scrambled twin loses, canonical unhurt.
- LEARNED surface cues WALL on unseen constructions (0.05 on held-out inversion vs 0.23 for grounded fit) — the
  Competition Model's CONFLICT-VALIDITY predicts it exactly; a linear cue-sum reaches NEITHER domain, and the
  project had already measured that same flat-integrator net-negative.
- GROUNDED thematic-fit CLEARS the wall: non-canonical 0.688 vs surface 0.039 (passive 0.889, fronting 1.0),
  construction-independent. Drill PINS reliability-weighted / precision-weighted integration (Ernst&Banks 2002;
  Ohshiro/Angelaki/DeAngelis; Gibson noisy-channel 2013; Feldman&Friston precision=gain) — NOT a linear sum;
  fenced off two on-disk wrong approaches (scalar-over-fused = inert; margin-gating = HARD_FAIL).
- IMPLEMENTED the brain's actual mechanism and it RE-DERIVES an owner-DONE design: role = GRAMMATICAL FUNCTION
  (parse) + VOICE, not surface position. spaCy (an INDEPENDENT parser) solves passive 0.948 / inversion 0.731 /
  fronting 0.944 where position ~0. This matches the landed `graded_role_assigner` (position-dominant + structural
  override; "the cue-first replacement was self-refuted"; inversion 0.47->0.83, quotative live +0.253).
- CORRECTED TWO of my own errors: 87% of my "inversion wall" was my gold mislabeling existential-"there" pivots as
  agents (fixed at source); and inversion is a PARSE problem, not a thematic-fit one (thematic fit's real domain is
  only reversibles/ambiguity). Straggler decomposition: genuine inversion is 83% quotative (landed rule handles it).

HONEST BOUNDS: the modern migration is ROLE-focused — role on modern UD-EWT, coref on 19c LitBank (owner-DONE);
no single modern NARRATIVE corpus on the shelf has BOTH gold coref AND gold roles (measured: 46.6% of modern core-
args are pronouns, invisible to string-identity). Some deepening results are directional (per-construction eval is
construction-role confounded; small n). UD-EWT is web, not narrative.

FILES (no hdlab/ touched, Q111): experiments/exp_mcguffey_migrate_{build_modern_gold, revalidate, passive_cue_fix,
noncanon_by_type, cue_competition, learned_cue_transfer, learned_competition, precision_weighted,
grammatical_function, adjacency_audit, grounded_thematic_fit_poc, scoreboard}_v1.py; verification/
test_mcguffey_migration.py (19/19); data/eval_gold_mention_role_modern_ud_ewt_v1/; the problem-folder SOLVED.md +
WORKING_NOTE + research note.

FOR STRATEGY (you own hdlab, Q111): (1) swap the default role/situation-model eval to the modern UD-EWT gold;
retire McGuffey-as-primary (degenerate). (2) Land the BUILT-but-QUEUED locative/existential/expletive-"there"
subject-override into the live graded_role_assigner + rebuild the who-did-what cache. NEXT PROBLEMS seeded, all
dependency-linked: (A) FLAGSHIP — the reversible/ambiguous role residual: recruit grounded thematic-fit via a
route-conflict/surprisal GATE (architecture pinned, two wrong approaches fenced, sole invention = the reliability
estimator; shares the distributional_meaning_channel Priority-2 dependency; can-fail = structure solves clean
inversion with fit OFF, fit helps ONLY the reversible subset). (B) a both-gold modern NARRATIVE situation-model
gold (the 46.6%-pronoun coverage gap). (C) a grounded/learned animacy cue (its principle generalizes, its hard-
coded word list does not: fire-rate 0.71->0.12 on modern). AUDIT UPDATE + proposed diffs are in SOLVED.md.
