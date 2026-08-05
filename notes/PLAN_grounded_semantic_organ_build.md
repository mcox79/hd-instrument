# PLAN (v2, design-VET-corrected) — build the missing semantic organ

Status: RECORDED 2026-08-05 (survived aggressive adversarial design-VET: notes/design_vet_semantic_organ_plan.md,
commit 7bc1acfd6; VET's load-bearing claims re-verified on disk by Director). This is the plan of record.
Sources: brain audit (notes/brain_audit_SYNTHESIS_missing_semantic_organ.md + mechanism + our-components).
USER mandate (2026-08-05): prove EACH component works, THEN prove the COMBINATION works, stay FULLY
brain-faithful, do the RIGHT things not the easy ones.

## 0. CORRECTED ASSET INVENTORY (the audit UNDER-counted; verified on disk)
We are NOT starting from scratch. EXISTING glass-box, own-substrate, no-borrowed-embedding assets over text:
- hdlab/random_indexing.py (Sahlgren/Kanerva distributional, Hebbian co-occurrence).
- hdlab/ppmi_sparse_encoder.py (PPMI/SVD sparse concept encoder over text).
- hdlab/concept_encoder.py (competitive-Hebbian sparse concept coder; HARD_PASS cat_kitten_cos=0.492).
- hdlab/composed_encoder_v3.py (VWFA + PPMI N400 late-combine; SHELVED/superseded 2026-07-03).
- hdlab/predictive_coding.py (Rao-Ballard residual-gated Hebbian; the forward-prediction substrate — REUSE, do not rebuild).
- FAITHFUL+WIRED: coreference_resolver (HARD_PASS). EARNED+ISLANDED: appraisal-sim (valuation), ToM (mentalizing).
GENUINELY MISSING (the real build surface, narrowed): (a) SENSE-STRUCTURE / polysemy — every existing
encoder gives ONE vector per surface form, so "studied hard"/"hit hard" collapse; (b) IFG/pMTG
CONTROL/selection; (c) an ACC-style INCONGRUITY detector; (d) the AFFECT dimension in situation_reader's
EventRecord (verified absent); (e) valence riding a SENSE-RESOLVED concept; (f) two TEXT->STRUCTURED
EXTRACTION BRIDGES (text->appraisal-input for the sim; text->belief-input for ToM) — both reuse organs
take STRUCTURED input, never text, so the bridges are unbuilt and load-bearing.
=> EXTEND, don't rebuild. C-A overlaps HIGH with concept_encoder + composed_encoder_v3 — treat as extension.

## 1. Invariants (non-negotiable)
Glass-box; no external LLM at inference; NO borrowed embedding as the meaning organ (our own weights,
inspectable per-dim; borrowed = diagnostic-only then discarded); brain = reference standard; each
component judged on its OWN brain metric + an ERROR-BUDGET CONTRACT to its consumer (not just "beats
floor"); COMPONENT-FIDELITY-FIRST then a dedicated assembly proof; every gain WIRED at land; reuse the
faithful assets as spokes; select by brain-foundational-RIGHT; do the hard BLOCKING thing.

## 2. Gate design rules (from the VET — every component obeys these)
- FLOOR = the strongest EXISTING mechanism, never a strawman (no hash-random floors). A shortcut/heuristic
  control MUST FAIL the gate the faithful mechanism passes.
- ERROR-BUDGET CONTRACT: each gate states the ACCURACY/NOISE its downstream consumer needs, so "all
  components pass" actually predicts "combination passes" (the VET's central fix).
- HELD-OUT with DISJOINT cue vocabulary between fit and test (no leakage — recall the "sarcastically"
  and the melancholy/hollow/burden 3-word-signature leaks; implicit-affect items MUST use disjoint cues).
- Pre-register HARD-PASS + HARD-FAIL bands BEFORE running; difficulty on; ONE variable; real baseline.
- Adversarial VET (independent recompute + shortcut hunt) before advancing. WIRE-or-SHELVE at land.

## 3. Component order (dependency-first) — each with brain mechanism, REWRITTEN gate, error budget

### C-A. SENSE-STRUCTURED lexical-semantic hub (EXTEND concept_encoder; reuse predictive_coding)
- Brain mechanism: ATL amodal concept space, learned by statistical convergence + PREDICTION-ERROR, with
  MULTIPLE co-active senses per form, groundable to spokes. Substrate = concept_encoder competitive-Hebbian
  + predictive_coding Rao-Ballard gate (NAMED — hdlab/learner is model-SELECTION over hand atoms, CANNOT
  induce a semantic space; do not miscite it).
- STEP 0 (the RIGHT first step, cheap MEASUREMENT — begins now): run the EXISTING encoders
  (random_indexing / composed_encoder_v3 / concept_encoder) on a sense-minimal-pair probe and MEASURE the
  single-prototype sense-collapse. This sets the HONEST floor (replaces the asserted "count caps") and
  proves the discriminator fires on the real failure mode.
- Build: induce sense-structure (multi-prototype / context-clustered senses per form, induced not
  hand-listed), error-driven via predictive_coding.
- GATE (rewritten): on a held-out sense-labeled probe with DISJOINT fit/test context vocab, the
  sense-structured hub separates the two senses of a polysemous form that the EXISTING single-prototype
  encoder provably CANNOT (floor = single-prototype encoder, not hash-random). ERROR BUDGET: sense-pick
  accuracy >= X (X set from what C-D needs; measured in Step 0, pre-registered). HARD-FAIL if it beats
  the single-prototype floor by < the budget, or if senses are hand-listed rather than induced.

### C-B. Semantic CONTROL / word-sense selection (IFG/pMTG) — real biased-competition
- Brain mechanism: biased competition (mutual inhibition, Desimone-Duncan) among C-A candidate senses,
  constrained by the SITUATION-MODEL context; controlled retrieval of the non-dominant sense; objective =
  contextual coherence not frequency. NOT argmax-over-local-cues.
- GATE (rewritten): context-minimal-pair items where the disambiguating evidence is ONLY IN A PRIOR
  SENTENCE (not the local window); a LOCAL-WINDOW-ONLY control MUST FAIL while C-B passes (kills the arm_c
  shortcut). Mechanism witness: inspectable mutual-inhibition dynamics, not a cue argmax. ERROR BUDGET:
  selection accuracy on prior-sentence items >= what C-C/C-D need. HARD-FAIL if a local-window heuristic
  matches it.

### BRIDGE-1 (NEW, gated). text -> appraisal-input encoder (feeds the appraisal-sim)
- Why: appraisal-sim's congruence/coping are HAND-MAPPED from episode type (CONG={BLOCK_HIGH:HURT,...},
  verified) — it NEVER reads appraisal from text, and its theta space is not type-compatible with the
  concept space. Reusing it for text valence REQUIRES this bridge; the synthetic 1.000 is NOT a text number.
- Build: map a sense-resolved concept (C-A/C-B) + its situation context to the sim's appraisal-dim input
  (congruence/coping), glass-box. GATE: bridge produces appraisal inputs that, fed to the FROZEN earned
  theta, recover valence on a held-out UNSEEN-concept set above a per-sense-hand-table control (proves the
  sim theta, not a table, drives the value) + generalizes to unseen concepts. HARD-FAIL if only a hand
  table works or if it needs to retrain theta.

### C-C. Sense-resolved VALENCE (retire resolve_valence_blind from the affect path)
- Build: valence = appraisal-sim (via BRIDGE-1) on the C-B sense-resolved concept.
- GATE (rewritten): clears the audit's pinned failures — word-sense FPs (studied hard / a trick = non-HARM)
  AND the INERT-valence hard subset (must beat the SCRAMBLED-valence control, which the current reader does
  NOT: confused-4 oracle==scrambled==0.75). Value WITNESS: show the sim theta (not a table) drove each pick.
  ERROR BUDGET: valence accuracy on sense-resolved concepts >= what C-D's integration needs.

### C-D. Situation-model AFFECT dim + PREDICTION (isolate prediction from integration) — load-bearing
- Brain mechanism: Zwaan event-indexing + per-protagonist affect/goal state, maintained (WM in-focus +
  coref persistence out-of-focus) and PREDICTIVE (forward valence expectation before the next clause;
  reuse predictive_coding).
- Build: extend EventRecord with an affect dim (populated by C-C on sense-resolved concepts, bound to the
  coref protagonist-index) + a forward-prediction of expected next-clause valence via predictive_coding.
- GATE (rewritten — the VET's #1): TWO can-fails, (i) INTEGRATION: recover implicit dread from multiple
  weak DISJOINT-vocab cues vs a per-token-pooling baseline; (ii) PREDICTION (the isolating one): forward-
  project to an UNSTATED outcome — a STATIC no-projection arm MUST FAIL while the full predictive arm
  passes (otherwise "dread = forward prediction" is unproven and C-E is built on sand). Plus goal-owner
  PERSISTENCE across a 2-3 sentence span with a distractor. ERROR BUDGET stated for C-E/C-F.

### C-E-DETECT (NEW, gated). ACC-style INCONGRUITY detector
- Brain mechanism: dorsal-ACC conflict-monitoring — detects predicted-vs-surface valence mismatch, TRIGGERS
  reinterpretation. (Carry the mechanism doc's MODERATE-CONFIDENCE flag: ACC-for-irony is inferred from
  adjacent literature, not irony-specific — so this is a hypothesis-gated component.)
- GATE: fires on predicted(C-D)-vs-surface mismatch above a threshold, with a real ROC vs a no-conflict
  control; must not fire on sincere (charged, adequately-sized sincere set). It is a DETECTOR, not a
  classifier of irony content.

### C-E. Irony as a BYPRODUCT (reuse ToM via BRIDGE-2)
- BRIDGE-2 (NEW, gated): text mismatch context -> ToM's nested-HRR belief-input contract (ToM takes
  structured belief bundles, not text — unbuilt). GATE the bridge separately.
- C-E build: on C-E-DETECT firing, route through ToM (via BRIDGE-2) for intended-meaning reattribution.
- GATE: recovers the narrative-only irony arm_c MISSED (3/5) with 0 sincere FP, NO explicit-marker leak,
  as a BYPRODUCT (no dedicated irony surface-cue features). HARD-FAIL if a standalone surface classifier is
  needed (refutes the byproduct hypothesis -> re-route). CONDITIONAL on the C-D prediction gate passing.

### PREREQ for C-F. WIRE OOV frame-induction into production FIRST
- Verified unsequenced dependency: frame_primary_role falls OOV subj->AGENT in production (situation_reader
  self-test asserts cherished->AGENT). TYPING_MISS cannot move until OOV induction (offline induce(),
  Gleitman bootstrapping) is WIRED into the production path. Do this before C-F.

### C-F. Goal-owner selection (Component-5) on the faithful stack
- Build: Component-5 fed by C-A/C-B sense-resolved + OOV-wired frame roles + C-D affect/goal persistence + coref.
- GATE (rewritten): ABLATION isolating the TYPING_MISS-bucket delta (dominant 14/38) specifically to
  sense-resolved roles (not coref) on the held-out C3-mined set; beat the ~0.32 end-to-end / 0.82 owner-ID
  with TYPING_MISS shrinking. HARD-FAIL if TYPING_MISS doesn't move.

## 4. Assembly / combination proof (own phase, VET-corrected)
- BASELINE = the EXISTING BACKBONE (coref + situation_reader + positional roles + table valence) — NOT a
  stripped baseline (else the >=15pt gain could be coref, not C-A..C-E). Fair, backbone-matched.
- TEST set spans (a) sense-override, (b) implicit affect [DISJOINT cue vocab, no 3-word signature leak],
  (c) irony [no marker leak], (d) goal-owner across span with distractor.
- HARD-PASS: >=15pts absolute on the IMPLICIT-AFFECT and GOAL-OWNER subsets (the two that provably need the
  situation-model layer). PER-SEAM ABLATION at every wiring seam (faithful parts don't auto-compose) — so
  an undetected error-budget gap surfaces. Carry P_deflated=0.45.
- HARD-FAIL / diagnostic: <5pts on implicit-affect+goal-owner -> pinpoints which of C-A/C-B vs C-D vs
  persistence is still missing.

## 5. Process (every phase)
Design-gate before each full run; on every negative run the brain-fidelity element audit + "missing
component (esp. LEARNING)?" check; VET positives as hard as negatives, per-axis, triple-check load-bearing
data, verify on disk, READ THE CODE; resumable per-unit; local-only; git-commit after every bank; NO
origin push w/o USER auth; docs current every cycle.

## 6. First action (BEGIN NOW)
C-A STEP 0 measurement cell: run existing encoders on a sense-minimal-pair probe, measure single-prototype
sense-collapse, set the honest floor + the C-A error budget. This is the RIGHT first step (measure the real
baseline before building; do not assume "count caps"). Everything downstream keys off this number.
