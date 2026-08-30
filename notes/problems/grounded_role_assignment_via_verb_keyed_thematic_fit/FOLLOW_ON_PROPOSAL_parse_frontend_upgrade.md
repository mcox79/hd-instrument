# FOLLOW-ON PROBLEM PROPOSAL (for the STRATEGY session to file; a solver may not open new problem folders, Q113)

**Proposed by:** the solver of `grounded_role_assignment_via_verb_keyed_thematic_fit`, 2026-08-30.
**Proposed slug:** `the_reader_parse_frontend_is_the_role_bottleneck_upgrade_the_structure_builder`
**Why this exists:** the grounded-role problem established, with power and controls, that role assignment is
dominated by STRUCTURE, not by the argument-plausibility (thematic-fit) signal the brief targeted. The
deployable win therefore lives in the PARSE FRONT-END, not the fit vector. This packages that redirect as a
ready-to-file brief. Strategy: lift sections 1-8 into a new `notes/problems/<slug>/PROBLEM.md`, set a priority,
and add the standing SOLVER OPERATING PROTOCOL block.

---

## THE EVIDENCE THAT MOTIVATES THIS (all measured in the grounded-role problem; re-verifiable)
- The live reader's role front-end COLLAPSES on non-canonical order: the migration measured 0.288; on the
  reader's own noisy front-end my weak-parser eval reproduces word-order 0.149 / graded_role 0.118 on the
  non-canonical (pre-verbal patient) subset (n=1224).
- A MODERN dependency parser (spaCy en_core_web_sm, substrate-native, NO LLM) scores structural roles at
  **0.9959 aggregate / 0.9915 balanced on non-canonical** (0.4% error) on modern UD-EWT
  (`exp_grounded_role_noisy_parse_v1.py`). It DOMINATES word order (0.94), the landed graded_role (0.90), and
  every thematic-fit gate variant.
- The thematic-fit gate is fenced as near-ceiling: most role information is STRUCTURAL, not noun-intrinsic
  (animacy-alone 0.54, best noun representation 0.65 -- a modest ceiling regardless of representation;
  reconciled against the field in `research_thematic_fit_ceiling_reconciliation_2026-08-30.md`). So the fit
  vector is NOT the lever; the parse is.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader works out "who did what to whom" from a weak, error-prone grammar front-end (an nltk-era shallow
parser). On any sentence that isn't plain subject-verb-object -- passives, fronting, relative clauses -- it
collapses (worse than a coin flip). A competent sentence-grammar reader gets who-did-what right ~99.6% of the
time on the same modern text. The fix is to give the reader a competent structure-builder, because that is
where "who did what" actually lives -- not in a cleverer guess from word meanings (we proved that is near a
modest ceiling).

## 2. WHY THIS ONE
It is the DOMINANT, evidence-backed fix for the non-canonical role collapse that a whole line of work
(McGuffey migration, `graded_role_assigner`, `grounded_role_assignment_via_verb_keyed_thematic_fit`) has been
chipping at with small gains. A modern parser closes it almost entirely (0.29 -> ~0.99 in isolation). Correct
roles on non-canonical order feed who-did-what, the situation model, coreference, and the QA capstone -- every
downstream reader number is currently paying the front-end's error.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION; READ THIS, it changes the target)
The brain does NOT parse post-hoc then second-guess. It builds structure INCREMENTALLY, integrating all cues
-- word order, morphology, AND thematic-fit plausibility -- DURING attachment, word by word (Lewis & Vasishth
2005 activation-based parsing; MacDonald constraint-based; Levy 2008 surprisal). This is PINNED and it is the
resolution of the grounded-role problem's central negative: a POST-HOC fit gate cannot separate "misleading
order" from "atypical agent" (irreducible tradeoff) because by then the parse is already committed; an
INCREMENTAL parser never commits to the wrong structure, because plausibility guides attachment in real time.
- **PINNED (replicate):** an incremental, predictive structure-builder with reliability/precision-weighted
  cue integration (Competition Model) -- order + voice morphology + filler-gap + thematic fit competing DURING
  parse, not after.
- **OUR-INVENTION / SUBSTITUTION (label honestly):** an off-the-shelf statistical dependency parser (spaCy) is
  a SUBSTITUTE for the brain's structure-builder, not a model of it. It is ADMISSIBLE (no LLM at inference) and
  it proves the achievable ceiling is high (0.996) -- but adopting it wholesale is the "reach for the
  convenient tool" move the mission warns against. Use spaCy as (a) the reference UPPER BOUND and (b) a
  pragmatic interim floor-raiser IF a quick deployable win is wanted; the mission-aligned build is the
  brain-faithful incremental parser, which is ALSO where thematic fit finally earns its keep the right way
  (integrated online), reusing the grounded-role problem's fit signal as one competition cue.

## 4. MEASURED vs INFERRED
- **MEASURED:** spaCy structural roles 0.9959 / 0.9915 balanced non-canonical in ISOLATION on modern UD-EWT;
  the weak front-end's collapse (0.118-0.288); the fit-vector ceiling (~0.65 noun-side).
- **INFERRED (you must measure):** that a better parse front-end, WIRED INTO THE LIVE READER, improves the
  END-TO-END who-did-what / situation-model numbers. An isolation win is a CONSTRUCTION PROOF; this project has
  repeatedly mistaken one for a capability (the phase gate warns exactly this). The downstream consumers
  (binder, situation model, coref) must be able to CONSUME the richer parse, or the isolation win does not land.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The verb-keyed grounded thematic-fit GATE (post-hoc override): fenced -- beats floors on non-canonical in the
  weak-parser regime but with an IRREDUCIBLE canonical tradeoff; it is a tie-breaker, not the lever.
- Richer / grounded / role-tuned FIT VECTORS (8 methods, 2 drills): fenced -- noun-side signal near a modest
  ceiling regardless of representation; no proven headroom over verb-conditioned GloVe. Do NOT re-open.
- The routing precision-fix to `graded_role_assigner` (override only on reliable strong markedness): CI-backed
  (+0.081 aggregate), COMPLEMENTARY and smaller; land it regardless, but it is not the dominant fix.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reproduce `exp_grounded_role_noisy_parse_v1.py` (spaCy 0.996 in isolation) and the weak-parser collapse
  (`exp_grounded_role_weak_parser_v1.py`).
- Read the live front-end (`exp_stated_entity_fate_reading_extractor_v1._load_or_build_frontend`,
  `exp_reader_vs_twoline_qasrl_power_v1.parse_and_align`) and what consumes its output
  (`hdlab.graded_role_assigner`, the binder, the situation-model eval `exp_wire_organs_endtoend_v1`).
- Confirm spaCy is substrate-native / permitted (no LLM at inference -- it is a statistical parser).

## 7. THE BAR (can-fail; CI-separated; measured END-TO-END, not in isolation)
- **PASS =** the upgraded parse front-end (brain-faithful incremental builder as the target; spaCy as the
  reference/interim), wired into the LIVE reader, beats the current front-end on the END-TO-END who-did-what /
  situation-model eval, CI-separated, WITHOUT regressing canonical order -- and specifically converts the
  non-canonical collapse (~0.29) toward the isolation ceiling (~0.9+). Info-free control: a scrambled-parse /
  permuted-attachment twin MUST lose. Strongest floor = the current live front-end recomputed on the same
  eval, plus the majority-role constant recomputed per subset.
- **A rigorous NEGATIVE is a full PASS:** if a competent parse helps in isolation but NOT end-to-end because the
  downstream consumers cannot use its richer structure, that is a real, high-value result -- name the exact
  integration gap (which consumer drops the information), enumerated. That is itself the next problem.

## 8. FILES AND ENTRY POINTS
- Consumes: `experiments/exp_grounded_role_noisy_parse_v1.py` (isolation ceiling), `exp_grounded_role_weak_parser_v1.py`
  (the collapse), the live front-end + `hdlab.graded_role_assigner` + the end-to-end situation-model eval.
- Build + validate in `experiments/` and `verification/`; propose the hdlab front-end swap as a diff (strategy
  lands it, Q111). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` (the parse-front-end entry: current
  = weak nltk shallow parser; SUBSTITUTION candidate = modern dependency parser; PINNED target = incremental
  cue-integrated structure-builder).

---

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md, to fold at integration)
The reader's PARSE FRONT-END is the measured bottleneck for who-did-what, not the role-assignment logic or the
thematic-fit vector. Current front-end = weak nltk-era shallow parser (non-canonical role ~0.29). A modern
dependency parser scores 0.996 in isolation (admissible; no LLM) -- the achievable ceiling is high and
structural. The brain-faithful target is an INCREMENTAL, cue-integrated (order + morphology + thematic fit)
predictive structure-builder (Lewis-Vasishth; MacDonald; Levy), which is where thematic fit belongs (online,
during attachment) rather than as a post-hoc override. Thematic-fit fit-vector work is fenced as near-ceiling.
