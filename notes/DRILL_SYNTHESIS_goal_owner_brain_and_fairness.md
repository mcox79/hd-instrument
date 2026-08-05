# Drill synthesis — goal-owner: brain-foundation + test-fairness ruling (2026-08-05)

USER asked: drill (a) the brain-foundational aspects of what we're building, (b) the exact brain way, (c)
whether the TEST is fair. Three live-verified/audited drills + VET on disk. Sources:
- notes/research_brain_event_segmentation_2026-08-05.md (angle 1, live-verified)
- notes/drill_brain_goal_owner_flow.md (angle 2, live-verified, f57d8bf49)
- notes/testfairness_audit_goal_owner.md (angle 3, recomputed off disk, ff6f93a9a)
Director VET'd the load-bearing numbers on disk (all confirmed).

## RULING IN ONE LINE
The goal-owner TEST has NOT been fair -- the 0.32/0.64-0.71 numbers measure upstream syntactic-subject
resolution, NOT goal->owner binding (the C5 organ decided ~1 real item; it TIES recency exactly). AND the
pipeline uses LEXICAL/SYNTACTIC LOOKUPS in two places where the brain uses RELEVANCE-GATED / GENERATIVE
inference. Fix the TEST first (nothing downstream is measurable without it), then the two brain gaps.

## PART A -- IS THE TEST FAIR? NO (angle 3, VET-CONFIRMED on disk)
- METRIC INVALID: matches_gold = (resolver's outcome-sentence subject == miner's SYNTACTIC-SUBJECT gold).
  That is a subject-resolution agreement check, not goal->owner binding. A trivial "pick the goal-sentence
  subject" baseline scores ~100% by construction.
- ORGAN BARELY FIRES: candidate_divergence_rate = 0.0 (15-item) / 0.0588 (38-item) -> directed_goal_outcome
  _score changed the answer on ~1 genuine real-text item across both banks. role_seq is usually [GOAL,
  OUTCOME] on the SAME subject -> trivially scores 1.0.
- "BEATS RECENCY" IS FALSE (as-run): 15-item outcome_binding 0.6364 == recency 0.6364 EXACTLY,
  beats_recency=False, non_vacuous_scramble=False (vacuous discriminator). 38-item margin = +1 item.
- F1 MISLABEL: the docstring "extractor F1~0.64" is NOT this extractor's -- real extraction F1 on disk is
  0.23 (ungated) / 0.28 (gated_structural). Two agents independently caught this. DO NOT propagate 0.64.
- BANKS DEFECTIVE: gold wrong 7/38 (place-metonyms York/England, predicate-adj, vocative, tool-sense) +
  6/21 OOV; outcome_span is auto-extracted trailing text about a DIFFERENT character; foils contaminated
  (places/generics). Effective discriminating-N ~= 1 (38-bank) / ~=3 (OOV).
- NOT THE BRAIN'S TASK: sentence-local (goal+outcome one clause, one subject); never maintains a goal
  across a DISTRACTOR and binds the outcome to the goal-HOLDER. Tests lexical co-firing, not situation-model
  maintenance.

### Prior conclusions to RE-SCOPE / REJECT (this session + before)
1. "Real-text C5 binding ~0.64-0.71 = the organ works" -> RE-SCOPE (it's subject-resolution; organ decided 1).
2. "Beats recency on real text" -> FALSE as-run (ties exactly / +1 item).
3. Extractor "F1~0.64" -> UNVERIFIABLE; disk = 0.23-0.28.
4. Any outcome-POLARITY result from these banks -> REJECT (auto-extracted spans, 1 inverted OOV label).
5. The "0.32 end-to-end ceiling" I treated as THE goal-owner number -> NOT a fair goal-owner measurement.
6. KEEP but SCOPE: the hand-authored isolated-GIVEN-role cell (1.0 vs recency 0.043, non-vacuous) = a valid
   MECHANISM-EXISTS proof on GIVEN roles ONLY; does not transfer to real prose.

## PART B -- IS IT BRAIN-FOUNDATIONAL? ORDER yes; two LEXICAL shortcuts where the brain does gated/generative inference
- EVENT SEGMENTATION (angle 1): our extractor = one predicate/clause via POS tag, now extended to
  coordinated/participial/modal clauses. Correct on the DECOMPOSITION axis (Davidsonian multi-event/clause,
  VERIFIED) but MISSING the brain's unit = a PREDICTION-ERROR-GATED, persistently-updated situation-model
  DISCONTINUITY at multiple timescales (Zacks EST, Zwaan indexing, Baldassano). We OVER-SEGMENT: every valid
  verb -> event; the brain only creates a boundary when a Zwaan dimension (time/space/causation/goal/
  protagonist) SHIFTS. Cheap brain-faithful win: a RELEVANCE GATE (is_boundary from entity/causal/tense/
  spatial change) filtering existing extraction, reusing owned coref/causal/temporal readers. P=0.45.
- GOAL-OWNER FLOW (angle 2): pipeline ORDER (role->goal->outcome->owner) IS brain-faithful (matches the
  role-parse -> mentalizing goal-inference -> hippocampal/DMN binding -> ACC outcome-monitoring cascade;
  Trabasso causal-network validates the GOAL/Event/Outcome stage separation). SINGLE DIVERGENCE: goal-typing
  is LEXICALLY GATED (psych-verb -> GOAL) where the brain GENERATIVELY INFERS goals from action sequences
  with no goal-word (Trabasso goal-plans + TPJ/dmPFC mentalizing, VERIFIED). P=0.58. Also verified: the
  EXPERIENCER is NOT always the subject (flips for frighten/worry-class = object-experiencer; our
  subject-experiencer frame is one class only).
- CONVERGENCE: both gaps are the SAME CLASS -- a LEXICAL/SYNTACTIC LOOKUP where the brain does RELEVANCE-
  GATED / GENERATIVE inference -- and the same class as the OOV frame-induction problem (lexical table ->
  generative bootstrapping).

## PART C -- THE REFRAME + PRIORITY (measurement-first)
1. **BUILD A FAIR TEST FIRST** (nothing is measurable without it; a metric that ties a recency baseline is
   not trustworthy). Corrected design (angle 3): >=25 verified items, each protagonist P (goal) + a
   gender-matched DISTRACTOR D placed BETWEEN goal and outcome, outcome authored causally-tied to P but
   syntactically NEARER D (a real recency trap), verified owner+polarity gold, + a no-distractor control;
   NO auto-extracted outcome_spans. METRIC: score on the DIVERGENT subset only (where selection is actually
   exercised), gold = goal-HOLDER decoupled from the outcome-sentence subject; move OWNER_ID_ERROR out of
   the capability denominator. BASELINES (all three): goal-sentence-subject (construction ceiling),
   recency-to-outcome (trap FLOOR, must BEAT, floor<0.5), majority.
2. **Fix the biased survivor-set FIRST**: the event-extractor participial/dialogue gaps (2/3 done; #19 needs
   a better tagger -- spaCy not installed) so N isn't a biased survivor set.
3. **THEN the two brain gaps**, measured against the fair test: (a) RELEVANCE GATE on event extraction;
   (b) GENERATIVE goal-inference (goals from actions, not just psych-verbs) -- reuse/expand the learner
   (same class as OOV induction).

## Honest meta-note
The USER's instinct to drill was correct and load-bearing: it revealed we were measuring an UNFAIR test (the
goal-owner numbers were never real goal-owner measurements) AND building lexical shortcuts where the brain
does gated/generative inference. This is a course-correction, not a small fix. The session's WIRED substrate
gains (grounding/affect/OOV/coref -- all cert-green, backward-compat) stand; what must be rebuilt is the
goal-owner TEST + the two inference gaps. Deflate all prior goal-owner "numbers" accordingly.
