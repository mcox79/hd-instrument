# PLAN (v3, brain-fidelity-VET-corrected) — build the missing semantic organ

Status: RECORDED 2026-08-05. v3 supersedes v2 after a HARD per-component brain-fidelity VET
(notes/brain_fidelity_vet_components.md, commit 6469e4899) triggered by C-A failing TWICE. The VET (USER-
directed: "vet the components hard against the brain faithful drill") proved C-A's FORMULATION — not its
implementation — was un-brain-faithful. This version fixes the formulation. Reference standard = the brain
drill (notes/brain_audit_affective_comprehension_mechanism.md); assets (notes/brain_audit_our_components_status.md);
design-VET (notes/design_vet_semantic_organ_plan.md).
USER mandate: prove EACH component, THEN the COMBINATION, fully brain-faithful, RIGHT-not-easy.

## 0. What the two C-A fails taught us (the formulation correction)
- The ATL semantic HUB is NOT missing (composed_encoder_v3 / concept_encoder exist, glass-box). What is
  missing is CONTEXT-CONDITIONED SENSE RESOLUTION = GROUNDING + CONTROL, and the AFFECT dimension.
- BAG-OF-WORDS CO-OCCURRENCE LACKS THE SENSE SIGNAL (MEASURED: supervised nearest-centroid handed the gold
  sense scored 0.5167=chance on masked bag-of-words, v2). The brain's sense signal is GROUNDING + SYNTAX/
  ARGUMENT-STRUCTURE + SITUATION (drill 1.4/2.2), not nearby-word counts.
- DISCRETE stored senses are un-brain-faithful (drill 1.2/2.1: graded, constructed per-instance). Use a
  CONTEXT-MODULATED GRADED concept read, not a sense inventory.
- SENSE RESOLUTION IS INSEPARABLE FROM CONTROL (drill 1.4/§4 recurrence): the hub alone gives only the
  DEFAULT sense; the contextually-correct sense is produced BY control under situation-model bias. =>
  MERGE C-A+C-B. And the CORRECT METRIC is DOWNSTREAM DIFFERENTIAL GROUNDING ("studied hard"->non-harm vs
  "hit hard"->harm), prior-clause-forced — NOT isolated 2AFC.
- Therefore BRIDGE-1 (appraisal/valence FROM TEXT) is the TRUE BLOCKING FOUNDATION: you cannot even SCORE
  the corrected sense-resolution component without producing a grounding/valence from a word-in-context.
  Build it FIRST.

## 1. Invariants (unchanged)
Glass-box; no external LLM at inference; NO borrowed embedding as the meaning organ (own inspectable
weights; borrowed=diagnostic-only then discarded); brain=reference standard; each component judged on its
OWN brain metric + an ERROR-BUDGET contract to its consumer; component-fidelity-first then a dedicated
assembly proof; every gain WIRED at land; reuse faithful assets (coref, appraisal-sim, predictive_coding,
composed_encoder_v3/concept_encoder, Component-3 frames) as spokes; select by brain-foundational-RIGHT; do
the hard BLOCKING thing.

## 2. Gate rules (unchanged, from the design-VET)
Real-mechanism FLOORS (no strawman); ERROR-BUDGET contract per gate (so all-pass predicts combination-pass);
held-out with DISJOINT cue vocabulary (no leakage); pre-register HARD-PASS+HARD-FAIL before running;
difficulty on; one variable; adversarial VET before advancing; WIRE-or-SHELVE at land.

## 3. Component build order (v3 — reformulated + reordered)

### FOUNDATION. BRIDGE-1 = context-conditioned GROUNDING (word-in-context -> appraisal/valence)  [BUILD FIRST]
- Brain analog: valuation/grounding spokes (drill 1.3) driven by CONTROL (1.4) under situation context.
- Why first: the corrected sense-resolution metric IS differential grounding; that requires producing a
  valence from a word-in-context, which needs this bridge. Also fixes the audit's hand-wave (appraisal-sim
  CONG is a HAND MAP from episode type, verified L74; it never reads appraisal from text; its synthetic
  1.000 is NOT a text number).
- Build: an EARNED, glass-box map from (target word, its CONTEXT) -> the appraisal-sim's input dims
  (congruence HURT/HELP/NEUTRAL, coping), which the FROZEN earned theta then values. CRITICAL: the context
  SIGNAL must be GROUNDING + SYNTAX/ARGUMENT-STRUCTURE (the syntactic governor / frame — reuse depparse +
  Component-3 frames), NOT bag-of-words (proven featureless). "hard" grounds differently under governor
  "studied" (manner) vs "hit" (force/harm).
- GATE (differential grounding, the drill's §6 test on the sense-override subset): on collision pairs with
  the disambiguator in a PRIOR clause, produce DIFFERENTIAL valence ("studied hard"->non-HARM vs "hit
  hard"->HARM) beating: (i) the single fixed-per-form table (current reader), (ii) a bag-of-words control
  (must FAIL — signal check), (iii) scrambled-valence control. WITNESS the sim theta (not a table) drives
  the value + generalize to unseen concepts. HARD-FAIL if only a per-form table works, if bag-of-words
  matches it, or if it must retrain theta.

### C-AB. Context-conditioned graded sense resolution (MERGED C-A + C-B)  [with/after BRIDGE-1]
- Brain analog: 1.2 hub (default, GRADED) + 1.4 semantic control (biased competition keyed to the running
  situation model), as ONE recurrent read — NOT a standalone discrete-sense inducer.
- Build: a context-MODULATED read of the existing hub (composed_encoder_v3/concept_encoder) — the same
  concept vector SHIFTED by a control step biased from verb-frame/argument-structure + situation + the
  BRIDGE-1 grounding. Graded, glass-box (inspectable what shifted the read). NO discrete prototype
  inventory; NO isolated 2AFC.
- GATE: DOWNSTREAM differential grounding (via BRIDGE-1) on prior-clause-forced collision items; a
  LOCAL-WINDOW-ONLY control MUST FAIL (kills the arm_c shortcut); a context-BLIND read MUST FAIL (kills the
  single-prototype floor). ERROR BUDGET: differential-grounding accuracy >= what C-C/C-D need.

### C-C. Sense-resolved VALENCE (retire resolve_valence_blind from the affect path)
- = BRIDGE-1 grounding on the C-AB context-resolved concept, feeding the appraisal-sim valuation.
- GATE: clears the audit's pinned failures — word-sense FPs (studied hard / a trick = non-HARM) AND the
  INERT-valence hard subset (must BEAT the scrambled-valence control the current reader does NOT). Value
  WITNESS (theta, not a table, drove each pick).

### C-D. Situation-model AFFECT dim + PREDICTION (isolate prediction from integration)
- Brain analog: 1.5 Zwaan event-indexing (per-protagonist affect/goal state, maintained via coref/hippo
  persistence) + 1.6 predictive coding (forward valence expectation before the next clause — REUSE
  hdlab/predictive_coding, do not island it).
- Build: extend situation_reader EventRecord with an affect dim (populated by C-C on sense-resolved
  concepts, bound to the coref protagonist-index) + a forward-prediction of next-clause valence.
- GATE (rewritten): TWO can-fails — (i) INTEGRATION (implicit dread from disjoint-vocab weak cues vs
  per-token pooling) AND (ii) PREDICTION-ISOLATING (forward-project to an UNSTATED outcome; a STATIC
  no-projection arm MUST FAIL while the predictive arm passes). Plus goal-owner persistence across a span
  with a distractor. This is the highest-priority gate rewrite (C-E depends on it).

### C-E-DETECT. ACC-style INCONGRUITY detector  [FIRST-CLASS gated component, was assumed]
- Brain analog: dorsal-ACC conflict monitoring (drill 1.8) — carries the drill's MODERATE-CONFIDENCE flag
  (ACC-for-irony inferred from adjacent literature, not irony-specific; hypothesis-gated).
- GATE: fires on C-D predicted-vs-surface valence mismatch with a real ROC vs a no-conflict control; must
  not fire on a charged, adequately-sized sincere set. A detector, not an irony content classifier.

### BRIDGE-2 + C-E. Irony as a BYPRODUCT via ToM  [BRIDGE-2 is a FIRST-CLASS gated build]
- BRIDGE-2: text mismatch context -> ToM nested-HRR belief-input contract (ToM takes structured belief
  bundles, not text — unbuilt; gate it separately).
- C-E: on C-E-DETECT firing, route through ToM (via BRIDGE-2) for intended-meaning reattribution.
- GATE: recovers the narrative-only irony arm_c MISSED (3/5) with 0 sincere FP, NO explicit-marker leak,
  as a BYPRODUCT (no dedicated irony surface features). CONDITIONAL on the C-D prediction gate passing.
  HARD-FAIL if a standalone surface classifier is needed (refutes the byproduct hypothesis -> re-route).

### PREREQ + C-F. Wire OOV frame-induction into production, THEN goal-owner selection
- PREREQ (verified unsequenced dependency): frame_primary_role falls OOV subj->AGENT in production
  (situation_reader self-test asserts cherished->AGENT). WIRE the offline OOV induction (Gleitman
  bootstrapping) into production BEFORE C-F.
- C-F: Component-5 selection fed by C-AB sense-resolved + OOV-wired frame roles + C-D affect/goal
  persistence + coref. GATE: ABLATION isolating the TYPING_MISS-bucket delta (14/38) to sense-resolved
  roles (not coref); beat ~0.32 end-to-end / 0.82 owner-ID with TYPING_MISS shrinking.

## 4. Assembly / combination proof (own phase)
BASELINE = the EXISTING BACKBONE (coref + situation_reader + positional roles + table valence) — backbone-
matched, NOT stripped (else the gain is coref not the organ). TEST spans sense-override / implicit-affect
[disjoint cue vocab] / irony [no marker leak] / goal-owner-across-span-with-distractor. HARD-PASS = >=15pts
absolute on IMPLICIT-AFFECT and GOAL-OWNER subsets; PER-SEAM ablation at every wiring seam (faithful parts
don't auto-compose). Carry P_deflated=0.45. HARD-FAIL <5pts on those two -> pinpoints the still-missing piece.

## 5. Process (every phase)
Design-gate before each full run; on every negative run the brain-fidelity element audit + "missing
component (esp. LEARNING)?" check; VET positives as hard as negatives, per-axis, triple-check load-bearing
data, verify on disk, READ THE CODE; resumable per-unit; local-only; git-commit after every bank; NO origin
push w/o USER auth; docs current every cycle.

## 6. NEXT ACTION (BEGIN)
Build BRIDGE-1 = context-conditioned grounding (word-in-context -> appraisal/valence), SIGNAL = syntactic
governor/frame + grounding (NOT bag-of-words), EARNED, judged by DIFFERENTIAL GROUNDING on prior-clause-
forced collision pairs (studied-hard->non-harm vs hit-hard->harm), bag-of-words control MUST fail. This is
the true blocking foundation; C-AB is tested THROUGH it. Reuse depparse + Component-3 frames + appraisal-sim.
