---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — grounded_role_assignment_via_verb_keyed_thematic_fit    STATUS: PARTIAL (rigorous-negative + redirect; WIP → owner DONE)
hdlab/ UNTOUCHED (proposed diffs, Q111). Refutes the brief's premise and MAPS the real fix (parse front-end).
REVERIFY (one command reproduces every headline):
  .venv/Scripts/python.exe verification/test_grounded_role_gate_organ.py               -> 14/14
  .venv/Scripts/python.exe tools/problem_ledger.py --check                             -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
ASKED: build a verb-keyed grounded thematic-fit role assigner + conflict-recruitment GATE that overrides
  misleading word order only on conflict, beating word order AND the structural assigner on non-canonical
  without hurting canonical/reversible.

BUILT: the brain-faithful gate — a JOINT clause-level noisy-channel decision (Gibson/Bergen/Piantadosi 2013
  + MacWhinney Competition Model + McRae thematic fit): adopt the word-order reading unless the role-SWAP
  reading is plausible enough to beat a construction prior, waived by reliable passive morphology. No LLM.

RESULT — two regimes:
  * CLEAN-PARSE (modern UD-EWT core-arg gold, n=3591): the achievable non-canonical fix is STRUCTURAL ROUTING,
    NOT thematic fit — route_only (reliable-markedness override, no fit) 0.9858 beats word order +0.049
    [0.042,0.056] and graded_role +0.081 [0.072,0.091] CI-sep, canonical/reversible unregressed. Fit does NOT
    CI-separate from graded_role (gold parse removes the uncertainty fit resolves; graded_role hides an animacy
    cue). Brief premise REFUTED for clean parses — exactly as noisy-channel theory predicts (regime artifact).
  * WEAK-PARSER DEPLOYMENT (modern QA-SRL role-balanced gold via the reader's OWN noisy front-end; non-canonical
    n=1224): the fit gate DOES beat BOTH floors — word order 0.149 (+0.126 [0.102,0.149]) AND graded_role 0.118
    (+0.157 [0.130,0.186]) CI-sep, twin LOSING (+0.052); and GENERALISES to unseen pairs (+0.054 [0.003,0.107]
    vs structure). BUT REGRESSES canonical (0.655 vs 0.836); a full tau sweep shows the tradeoff is IRREDUCIBLE.
    So P1 (beat floors + no regression) FAILS; the bar's P2 rigorous-negative clause IS met, with power.

>> THE MAP TO THE REAL SOLUTION (the deliverable): the win is STRUCTURE, not the fit vector.
   1. A modern dependency parser (spaCy, substrate-native, NO LLM) scores structural roles 0.9959 / 0.9915
      balanced non-canonical in isolation — DOMINATES word order, graded_role, and every fit gate. The
      non-canonical collapse is a PARSE-QUALITY problem, not a thematic-fit problem.
   2. BRAIN-FAITHFUL TARGET = an INCREMENTAL, cue-integrated predictive structure-builder (Lewis-Vasishth;
      MacDonald; Levy) — order + morphology + thematic fit competing DURING attachment. This RELOCATES the
      thematic-fit work to where the brain puts it (online), resolving the exact canonical tradeoff the
      post-hoc gate could not. spaCy = OUR-SUBSTITUTION / reference ceiling + admissible interim, NOT a brain model.
   3. COMPLEMENTARY, landable now: routing precision-fix to graded_role_assigner (override only on reliable
      strong markedness): +0.081 aggregate, CI-sep, fit-independent.
   4. FENCED dead-ends (do not re-open): thematic-fit fit-vector work (near modest ceiling); post-hoc fit gate
      (irreducible tradeoff); fused-always / linear-sum / precision-weighted (hurt canonical).
   5. THE TRAP: measure END-TO-END on the live reader, not in isolation (the phase-gate warning).
   >> Packaged ready-to-file: notes/problems/<slug>/FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md (8-section brief;
      strategy lifts it into a new problem, Q113).

FLOORS: word order 0.9365 ALL / 0.022 balanced-noncanon; landed graded_role 0.9048 / 0.472; always-patient 0.958
  raw-noncanon (why the metric is BALANCED accuracy). null p95 route_only 0.5837.
CONTROLS: structure-shuffled TWIN loses CI-sep; FUSED-ALWAYS hurts canonical (gate not weight); ROUTING control
  isolates aggregate win as NOT fit; canonical+reversible no-regression split; noisy-channel CORRUPTION CURVE
  (gate-minus-structure gap grows monotonically as morphology is masked, twin never recovers — Gibson signature);
  independent derivation (gold roles vs surface-derived predictors — no circularity).

GENERALIZATION (fully reconciled, incl. a self-correction): 8 fit-vector methods + 2 research drills. CORRECTED
  an artifact of my own — an unbalanced classifier made GloVe look like chance; with a balanced classifier GloVe
  verb-conditioned generalises role to OOV nouns at 0.65 (my quick WordNet feature vector 0.57, LOST). Reconciled
  vs the field: 0.65 is consistent (thematic-fit ceiling ~0.6-0.7 for all reps). LOAD-BEARING: most role info is
  STRUCTURAL, not noun-intrinsic (animacy-alone 0.54) — the noun-side signal is near a modest ceiling regardless
  of representation. Grounded-feature headroom over embeddings is UNPROVEN; do not chase it.

BRAIN-FOUNDATIONAL: thematic fit is disambiguation-UNDER-UNCERTAINTY (Trueswell 1994; Gibson 2013), not
  override-certain-structure — a gold parse removes the uncertainty, so the clean-parse null is theory-predicted.
  AUDIT UPDATE: graded_role hides an animacy plausibility cue (score fit vs structure+animacy) and over-recruits
  its override on clean parses (false-fires 319/3353 canonical); the parse FRONT-END is the measured bottleneck.

HONEST LIMITS (withdraw first): thinnest = fit>twin on unseen pairs (+0.023, CI incl 0, doesn't survive).
  Sturdiest = weak-parser non-canonical wins (n=1224), the irreducible tradeoff (full sweep), routing +0.081
  (n=3591), spaCy 0.996. Self-rated STRONG (rigorous negative + redirect), not excellent SOLVED — the deployable
  win is the parser follow-on, a new problem.

FILES: experiments/{_grounded_role_data,_grounded_role_gate,_grounded_role_protofit,exp_grounded_role_baseline_v1,
  exp_grounded_role_opportunity_v1,exp_grounded_role_uncertainty_curve_v1,exp_grounded_role_gate_v1,
  exp_grounded_role_noisy_parse_v1,exp_grounded_role_weak_parser_v1,exp_grounded_role_protofit_generalize_v1,
  exp_grounded_role_knn_fit_v1,exp_grounded_role_feature_fit_v1}.py; verification/test_grounded_role_gate_organ.py
  (14/14); SOLVED.md + 3 research notes + FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md. hdlab/ UNTOUCHED.

TLDR: the reader gets "who did what" wrong on anything but plain word order. I built the brain's plausibility
  "gate" and tested it every way — and proved, with controls and against my own initial error, that word-meaning
  plausibility is NOT the lever: who-did-what lives mostly in sentence STRUCTURE, and a competent grammar reader
  (no AI model) nearly solves it (~99.6%) where the reader's weak one collapses (~29%). So the map to the real
  fix is clear and packaged: build the brain's incremental grammar-reader (which uses plausibility WHILE parsing,
  the right way), with a modern off-the-shelf parser as the proof the win is there. QUESTIONS: none.
════════════════════════════════════════════════════════════════════════════════════════════════════
