# Design-VET (adversarial): PLAN_grounded_semantic_organ_build.md

AUDIT-ONLY (Skunkworks). Pre-implementation adversarial design review. Deflationary.
Every code claim below was read off disk THIS pass (READ THE CODE not the label).
Verdict scale: SOUND / WEAK / WRONG, each with a concrete fix.

Reviewed: `notes/PLAN_grounded_semantic_organ_build.md`
Against: `notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`,
`notes/brain_audit_affective_comprehension_mechanism.md`,
`notes/brain_audit_our_components_status.md`, and the cited component code.

USER's three conditions this plan is held to: (1) prove EACH component works;
(2) prove the COMBINATION works; (3) stay fully brain-faithful; RIGHT things not easy ones.

---

## 0. LOAD-BEARING CORRECTION — the audit UNDER-counts existing assets (reverse label-mislabel)

The plan is built on the synthesis' claim (audit Component-8) that the ATL lexical-semantic
HUB and the predictive-coding layer are **"MISSING ENTIRELY"** and that "the only meaning
representation over actual text is `word_vector()` [hash-random]." **That is false on disk.**
The Component-8 grep searched for "word-sense / disambiguation" and correctly found no *WSD*;
it then over-generalized to "no ATL hub over text." Verified this pass, over TEXT, glass-box,
zero borrowed-embedding:

- `hdlab/random_indexing.py` — Sahlgren/Kanerva distributional semantics; forward-only Hebbian
  co-occurrence; `cosine(c_w1,c_w2)` reflects distributional similarity; explicit ATL-distributional analog.
- `hdlab/ppmi_sparse_encoder.py` — PPMI/SVD sparse concept encoder over `(sentence,label)` text; substrate-native.
- `hdlab/concept_encoder.py` — **competitive-Hebbian sparse-coding concept encoder, HARD_PASS**
  (cat_kitten_cos=0.492, seeds 11/17/23, N=4096) — extracted 2026-07-02; the "ATL-analog" the
  vwfa docstring names as its downstream.
- `hdlab/composed_encoder_v3.py` — VWFA(orthographic) + PPMI(ATL-hub) **N400-window late-combine**;
  registry `hdlab_encoder_cluster_vwfa_ppmi_composed_v3`, status `SHELVE/superseded_untouched_since_2026-07-03`.
- `hdlab/predictive_coding.py` — **WIRED** (Friston/Rao-Ballard residual-gated Hebbian, 9+ consumers).
  The synthesis calls predictive-valence "NONE/MISSING"; the *general* predictive-coding organ exists.

What is **genuinely** missing narrows to: (a) **sense-structure / polysemy** — every one of the
above gives ONE vector per surface form, so "studied hard" and "hit hard" collapse to the same
`c_hard`; (b) the **IFG/pMTG selection/control** step; (c) an **ACC-style incongruity detector**;
(d) the **affect dimension** in the situation model (verified: `EventRecord` = predicate/agent/
patient/tense/subj_role/obj_role, no valence field); (e) valence riding a *sense-resolved* concept.

Consequence for the plan: **C-A is not a from-scratch organ build; it is a targeted EXTENSION
(add sense-structure + control) of the shelved 2026-07-03 encoder cluster, reusing
`concept_encoder`/`predictive_coding` as the error-driven substrate.** Framing it as net-new both
risks re-deriving distributional similarity that `random_indexing` already does (the cross-arc
rediscovery pattern) AND sets a strawman floor (Section 1). Cross-arc overlap check: **C-A overlaps
HIGH with `hdlab_encoder_cluster_vwfa_ppmi_composed_v3` + `concept_encoder` — same ATL-hub concept;
treat as EXTENSION, not novel.**

---

## Axis 1 — C-A mechanism + can-fail floor. VERDICT: WEAK (rigged floor; solved sub-work re-derived)

Is the prescribed mechanism the ATL analog or a shortcut in disguise? The *prescription* (earned,
sense-structured, spoke-grounded, prediction-error-learned, NOT a single vector, NOT count-only) is
the right SHAPE and is genuinely distinguishable from a borrowed embedding — the line is drawable:
**glass-box, own-substrate co-occurrence/error-driven weights, inspectable per-dimension, no
GloVe/BERT tensor at inference.** `random_indexing`+`concept_encoder`+`predictive_coding` already
sit on the RIGHT side of that line, so "buildable glass-box without a transformer" = YES, proven.

But two problems:

1. **The CAN-FAIL floor (hash-random) is RIGGED.** `random_indexing` (real co-occurrence) beats
   hash-random trivially while STILL collapsing the two senses of "hard." So "beat hash-random on
   sense-distinction" is passable by any distributional encoder that does NOT solve sense — the
   discriminator does not fire on the actual failure mode. **Fix: floor = the existing
   single-prototype distributional encoder** (`random_indexing` / `composed_encoder_v3`) run on the
   SAME probe. HARD-PASS only if the sense-structured hub separates senses that the single-prototype
   encoder provably CANNOT. Hash-random stays as a sanity floor, never the discriminator.

2. **"Learned via hdlab/learner-style error-driven differentiation" is a category error.**
   Verified: `hdlab/learner` is a model-SELECTION engine (`learn(episodes, features,
   hypothesis_space_spec)`) over HAND-DECLARED atoms; it "cannot induce a semantic space" (the
   audit's own Component-7 finding, confirmed). It cannot induce senses. The plan hedges ("if not,
   build the minimal earned learner") but leads with the wrong tool. **Fix: name the actual
   error-driven substrate up front — `predictive_coding.py` (Rao-Ballard residual gate) +
   `concept_encoder` (competitive-Hebbian) — and induce sense clusters on top of THAT, not the MDL
   selector.**

Additional leakage trap on the C-A gate: if the sense-labeled probe is templated so the
sense-distinguishing context word doubles as the label cue, you measure the cue, not the hub.
**Fix: held-out probe with sense-distinguishing context vocabulary DISJOINT between fit and test.**

---

## Axis 2 — Sequencing. VERDICT: WEAK (skips a faithful measurement prerequisite; folds two missing organs)

C-A-first is defensible: everything downstream consumes sense-resolved concepts, so it is the true
blocking foundation, not hard-for-its-own-sake. Two faults:

- **A faithful prerequisite is skipped.** The plan ASSERTS "count-based content CAPPED" from a prior
  note rather than MEASURING it here against the on-disk encoders. That violates
  measure-don't-assert-the-ceiling and select-by-right-not-cheap-to-assert. **Fix: insert a
  MEASUREMENT cell (cheap, and the RIGHT first step): run `random_indexing`/`composed_encoder_v3`
  on the sense probe, show single-prototype collapses senses.** That IS the evidence motivating
  sense-structure AND sets the honest floor for Axis-1's gate. Do-the-hard-BLOCKING-thing does not
  forbid a cheap MEASUREMENT that de-risks the block; it forbids cheap direction-setting.

- **Two brain-necessary missing organs get no standalone slot.** Predictive-valence (1.6) and the
  ACC incongruity detector (1.8) are folded into C-D/C-E instead of sequenced+gated. They are the
  two pieces the synthesis itself names as MISSING; burying them inside larger components means
  neither gets its own can-fail proof (see Axis 6).

Building C-A from scratch when extendable assets exist IS hard-in-the-wrong-direction: the RIGHT
hard thing is sense-structure+control (genuinely missing), not re-deriving distributional similarity.

---

## Axis 3 — METRIC ADVERSARIAL CHECK (most important). VERDICT: WEAK across the board — gates prove SHAPE, not SUFFICIENCY

The single structural flaw: **every per-component gate is "beats floor / distinguishable"; none
specifies the accuracy the DOWNSTREAM consumer needs.** Gates are chosen to prove each component is
brain-SHAPED, not that it is ACCURATE ENOUGH to feed the next. That is exactly how all-components-
pass -> combination-fails-undetected. Per component:

- **C-A** — rigged floor (Axis 1). A hub can pass "distinguishable regions" at ~0.70 sense-accuracy
  and still be too noisy for C-D to integrate. **Rewrite: add an error-budget contract** — state the
  minimum sense-accuracy C-C/C-D require, and gate on THAT, not merely "> floor."

- **C-B** — "select correct sense above dominant-sense-always AND above C-A-without-control, must
  show situation-model (not local-window) context drives selection." SATURABLE: a local-window
  cue heuristic (the arm_c shortcut the plan says to avoid) passes "above dominant-sense-always"
  whenever the minimal pairs carry local disambiguators. The "must show situation-model drives it"
  clause is not OPERATIONALIZED. **Rewrite: minimal pairs where the disambiguating evidence lives
  ONLY in a PRIOR sentence (outside the local window); a local-window-only control MUST FAIL these
  while C-B passes.** Also make C-B genuine biased-competition (candidate senses under a top-down
  situation-model bias vector, mutual inhibition), not an argmax over hand cues — the current
  wording ("inspectable which cue drove the pick") is compatible with a heuristic (mechanism-WEAK).

- **C-C** — "beat scrambled-valence control." The scramble discriminator is GOOD (current reader is
  inert to it). But passing it only proves valence now depends on sense-resolved identity; it does
  NOT prove the appraisal-SIM produced the value. A per-sense hand table also beats scramble.
  **Rewrite: require a glass-box witness that the appraisal-sim theta (OFC-analog value signal)
  drives the valence, AND a generalization floor — a per-sense hand table as control that C-C must
  beat on UNSEEN concepts (the sim should generalize; a table cannot).** See Axis 4 for the
  unbridged reuse gap that makes C-C the highest-risk component.

- **C-D** — **the load-bearing gate rewrite.** "Recover dread beating per-token pooling" proves
  INTEGRATION, not PREDICTION. A better STATIC aggregator (Bayesian cue integration, no forward
  projection) beats naive per-token pooling too. The plan's own HARD-FAIL ("no better than pooling
  => not predictive") is a non-sequitur. Since "dread = forward prediction of a future negative
  event" is the whole brain claim — and C-E depends on the prediction being REAL — this must be
  isolated. **Rewrite: add a can-fail that isolates prediction — test items whose correct affect
  requires FORWARD projection to an UNSTATED future outcome; a static-integration-no-projection arm
  MUST FAIL them while the full arm passes.** Without this, "predictive" is unproven and C-E is
  built on sand.

- **C-E** — the BEST-designed gate (bans the explicit-sarcasm-marker leak that bit the prior irony
  eval; requires byproduct, no dedicated irony features). Two residual risks: (i) "byproduct" is
  only genuine if C-D's prediction is genuine — C-E validity is CONDITIONAL on the C-D rewrite;
  (ii) "0 sincere FPs" is cheap on a small/neutral sincere set. **Rewrite: sincere set must be
  affectively CHARGED (FPs actually possible) and adequately sized; and the mismatch signal must be
  shown to fire from C-D's forward prediction, not a re-labeled surface classifier smuggled in via
  the ToM-input extraction (Axis 4).**

- **C-F** — "beat ~0.32 e2e / 0.82 owner-ID, TYPING_MISS bucket shrinks." The TYPING_MISS
  decomposition is a good targeted discriminator, but "beat 0.32" is a low, aggregate-permissive
  bar that coref alone could move. **Rewrite: ablation — full stack vs same stack with C-A/C-B
  sense-resolution knocked out (roles from positional fallback); the TYPING_MISS delta must be
  attributable specifically to sense-resolved roles.** UNSEQUENCED DEPENDENCY: TYPING_MISS is
  dominated by OOV psych-verb typing, and verified `frame_primary_role` falls OOV subj -> AGENT in
  production (self-test asserts `cherished->AGENT`); the induced OOV path is offline-only. **C-F
  cannot move TYPING_MISS until the OOV induction is WIRED into the reader first — sequence that
  explicitly before C-F.**

### Axis 3b — assembly proof. VERDICT: WEAK (delta not isolated; half-guarded leakage)

- Could all pass and the combination still HARD-FAIL undetected? YES — the error-budget gap above is
  the mechanism, and it is undetected because each component is measured on its OWN favorable probe,
  never on the JOINT set with propagated upstream error. The plan's "integration checkpoints at each
  seam" is the right instinct but under-specified. **Fix: per-seam ablation + error-budget
  propagation, not just end-to-end pass/fail.**
- **Baseline is unfair in the wrong direction — it FLATTERS the new work.** Baseline = "table
  valence + positional roles." But the full stack ALSO inherits the WIRED coref + situation_reader
  backbone the baseline lacks, so the >=15pt gain could come from coref (already HARD_PASS), not from
  C-A..C-E. **Fix: baseline = existing backbone (coref + situation_reader + positional roles + table
  valence); the delta then isolates the NEW sense/affect organ, not re-measures coref's known win.**
- **Leakage: irony is guarded, implicit-affect is NOT.** If "dread" items are authored by picking
  melancholy/hollow/burden BECAUSE they connote dread, a model learns the 3-word surface signature,
  not integrate-then-predict — the SAME trap as the "sarcastically"-marker leak. **Fix: implicit-
  affect held-out items must use cue vocabulary DISJOINT from any tuning items (same discipline as
  irony).**
- The >=15pt threshold is inherited at P_deflated=0.45 (novel-synthesis cap) — carry that deflation;
  do not present the gate as a confident prediction.

---

## Axis 4 — Reuse vs island. VERDICT: coref SOUND; appraisal-sim WEAK (unbridged); ToM WEAK (unbridged); predictive_coding MISSED-REUSE

- **coref as persistence (C-D):** genuinely reused — bind affect to the coref-resolved
  protagonist-index. SOUND (coref verified faithful/HARD_PASS/WIRED).

- **appraisal-sim as text-valuation spoke (C-C): the load-bearing reuse, and the WEAKEST claim.**
  Verified off code: the sim's theta lives in a codebook space of **GIVEN discrete appraisal
  dimensions** — `CONGV`={HURT,HELP,NEUTRAL}, `COPV`={HIGH,LOW}, `VAL`={binary coh/rec} — all
  `rand_fhrr` atoms, and `ep["cong"]` is a HAND MAP `CONG[etype]` per episode. **The sim never
  derives appraisal from anything text-like; congruence/coping are HANDED to it.** Its theta is not
  even type-compatible with `word_vector` text space. So "route the sense-resolved concept into the
  appraisal-sim" hand-waves an ENTIRE appraisal-FROM-text encoder (text concept -> congruence/coping/
  target-coherence) that does not exist and is itself a hub+control job. The 1.000 is a SYNTHETIC
  no-text mechanism proof (the audit already flagged transfer untested; confirmed). **Answer to the
  pressure: NO — a sim trained on a discrete no-text world cannot score valence on sense-resolved
  TEXT concepts without an unbuilt appraisal-encoder bridge. Fix: build+gate that bridge as a
  first-class step (it is another instance of the missing organ, not free), and DO NOT inherit the
  synthetic 1.000 as a text number.**

- **ToM as irony reattributor (C-E): same class of unbridged gap.** Verified: ToM is a Sally-Anne
  nested-HRR false-belief solver whose input contract is STRUCTURED agent-partitioned belief bundles,
  not a text mismatch signal. "Route through the ToM organ for intended-meaning reattribution"
  assumes a belief-FROM-text extractor (character-stance/literal-meaning/situation -> nested-HRR)
  that does not exist. WEAK — same hand-wave as the appraisal-sim. **Fix: acknowledge C-E is blocked
  on a belief-extraction bridge, or build+gate it.**

- **`predictive_coding.py`: MISSED reuse.** It is WIRED and IS the forward-prediction/residual
  substrate C-D and C-E need. The plan doesn't mention it and risks a parallel build (islanding).
  **Fix: reuse it for the forward-valence-expectation and predicted-vs-surface mismatch.**

---

## Axis 5 — Brain-fidelity per component (SHAPE/POSITION/METRIC vs mechanism doc §1-2)

- **C-A:** SHAPE right IF sense-structured+spoke-grounded; POSITION right (feeds control); METRIC
  rigged floor (Axis 1). "prediction-error-learned" mis-assigns the mechanism to the MDL selector
  (fix: predictive_coding + competitive-Hebbian).
- **C-B:** SHAPE risk — "biased competition" wording is compatible with an argmax-over-cues
  heuristic, not Desimone-Duncan mutual-inhibition under top-down bias. METRIC saturable by
  local-window shortcut (Axis 3). Both fixable per the C-B rewrite.
- **C-C:** POSITION right (downstream valuation); SHAPE blocked on the unbridged appraisal-from-text
  encoder (Axis 4). METRIC good discriminator (scramble) but doesn't test the reuse (Axis 3).
- **C-D:** POSITION right — `EventRecord` (verified) is the correct empty home for the affect dim.
  SHAPE gap — prediction not isolated from integration (Axis 3, the key rewrite).
- **C-E:** "irony as byproduct" is faithful ONLY if C-D prediction is genuine AND no classifier is
  smuggled via ToM-input extraction. Conditional.
- **C-F:** direction faithful (frame-conditioned + persisted; consistent with verified
  `frame_primary_role` frame-primary win). Unsequenced dependency on wiring OOV induction (Axis 3).

---

## Axis 6 — Missing components. VERDICT: predictive-valence PARTIAL (fold+missed-reuse); ACC ASSUMED (WRONG)

- **Predictive-valence (1.6):** folded into C-D forward-projection, NOT isolated in a gate, AND
  misses reusing the WIRED `predictive_coding.py`. Half-addressed. Fix per Axes 3/4.
- **ACC incongruity detector (1.8): ASSUMED, not built.** The plan folds "mismatch signal" into C-E
  with no standalone component or gate. The mechanism doc itself flags ACC-for-irony as
  MODERATE-confidence / inference-from-adjacent-literature (NOT established) — the plan does not
  carry that deflation. **Fix: build the incongruity/conflict detector as its OWN gated component
  (predicted-vs-surface mismatch magnitude), carry the moderate-confidence flag, and let it be the
  thing that TRIGGERS C-E rather than an implicit sub-signal.**
- 9-subsystem coverage after correction: 1.1 wordform=`vwfa` (exists); 1.2 hub=exists
  (under-counted, extend); 1.3 spokes=appraisal-sim (unbridged); 1.4 control=C-B (building, OK);
  1.5 situation=`situation_reader` (home ready, needs affect dim); 1.6 prediction=`predictive_coding`
  (exists, UNDER-REUSED); 1.7 mentalizing=ToM (unbridged); 1.8 ACC=ASSUMED; 1.9 hippocampal=coref
  (reused, SOUND). Genuinely un-gated: 1.8-ACC. Under-reused: 1.6.

---

## TOP 3 ways this plan does the EASY thing instead of the RIGHT thing

1. **RIGGED FLOOR + re-deriving solved work (C-A).** Easy: beat a hash-random strawman and treat the
   ATL hub as MISSING. RIGHT: set the floor at the EXISTING single-prototype distributional encoder
   (`random_indexing`/`composed_encoder_v3`), prove the NEW mechanism (sense-structure + control)
   beats IT on sense-distinction, and reuse `concept_encoder`+`predictive_coding` as the error-driven
   substrate. More honest AND less work — the missing piece is sense+control, not the hub itself.

2. **GATES PROVE SHAPE, NOT SUFFICIENCY (no error budget).** Easy: every component passes an isolated
   "beats floor / distinguishable" metric on its own favorable probe. RIGHT: each gate carries an
   error-budget contract to its downstream consumer + the assembly does per-seam ablation, so
   all-pass actually PREDICTS combination-pass. This is the single change that closes the
   all-pass-but-combination-fails hole.

3. **HAND-WAVED REUSE BRIDGES (appraisal-sim & ToM).** Easy: declare "route the concept into the
   appraisal-sim" / "route through ToM" and inherit the synthetic 1.000 / HARD_PASS as text numbers.
   RIGHT: both organs take STRUCTURED input (given appraisal dims; nested-HRR belief bundles), not
   text — the text->structured extractor is itself the hard hub+control job. Build+gate those bridges
   as first-class steps, or state C-C/C-E are blocked on them; never inherit a no-text number as a
   text capability.

---

## Does the plan, AS CORRECTED, satisfy the USER's three conditions?

- **prove-each: NOT as-written (rigged C-A floor; C-B local-window-saturable; C-D proves integration
  not prediction; C-C doesn't test the reuse). CAN be satisfied as-corrected** (real-encoder floors;
  prior-sentence-only can-fail for C-B; prediction-isolating can-fail for C-D; appraisal-sim witness
  + generalization floor for C-C; error-budget contracts throughout).
- **prove-combination: NOT as-written (delta not isolated from the coref backbone; implicit-affect
  leakage unguarded; no per-seam ablation/error-propagation). CAN be satisfied as-corrected**
  (backbone baseline; disjoint-cue held-out on BOTH implicit-affect and irony; per-seam ablation;
  carry P=0.45 deflation).
- **fully-brain-faithful: DIRECTIONALLY yes, NOT fully as-written** — two reuse claims have
  unbridged text->structured extraction gaps and the ACC detector is assumed. **Fully faithful only
  if the appraisal-from-text and belief-from-text bridges are built+gated as their own steps
  (they are themselves the missing organ, not free) and the ACC detector is a gated component
  carrying its moderate-confidence flag.**

**Bottom line: the plan's DIRECTION is brain-foundational and worth pursuing, but as-written it would
pass its own gates while leaving the combination unproven and two reuse bridges hand-waved. It is
NOT yet the RIGHT-not-easy plan. Adopt the Section-0 correction (extend, don't rebuild; reuse
predictive_coding), rewrite the C-A and C-D gates, add error-budget contracts + a backbone baseline
+ disjoint-cue held-out, and make the ACC detector and the two extraction bridges first-class gated
steps. With those, it satisfies all three conditions.**

## Gates I would REWRITE (priority order)
1. **C-D** — isolate PREDICTION from integration (forward-projection-to-unstated-outcome can-fail;
   static-aggregator arm must fail). Highest priority: C-E depends on it.
2. **C-A** — floor = existing single-prototype distributional encoder, not hash-random; add
   downstream error-budget; disjoint-cue held-out probe.
3. **C-B** — prior-sentence-only disambiguation items; local-window control must fail.
4. **C-C** — appraisal-sim glass-box value witness + generalization-to-unseen-concept floor.
5. **New gate** — ACC incongruity detector as its own gated component (moderate-confidence flag).
6. **Assembly** — backbone baseline + per-seam ablation + disjoint-cue held-out on implicit-affect too.

## Disk paths cited
- Plan: `notes/PLAN_grounded_semantic_organ_build.md`
- Audits: `notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`,
  `notes/brain_audit_affective_comprehension_mechanism.md`,
  `notes/brain_audit_our_components_status.md`
- Existing ATL-hub / predictive assets (audit under-counted):
  `hdlab/random_indexing.py`, `hdlab/ppmi_sparse_encoder.py`, `hdlab/concept_encoder.py`,
  `hdlab/composed_encoder_v3.py`, `hdlab/vwfa.py`, `hdlab/predictive_coding.py`,
  registry row `hdlab_encoder_cluster_vwfa_ppmi_composed_v3` in `data/capability_registry.jsonl`
- Appraisal sim (synthetic, given-appraisal-dims): `experiments/exp_grounded_appraisal_sim_earned_v1.py`
  (`phi` L226, `train_theta` L267, `CONG` map L74, `CONGV/COPV/VAL` codebooks L117-119)
- Situation model (no affect field): `hdlab/situation_reader.py` (`EventRecord` L110-124)
- Frame roles (OOV->AGENT in prod): `hdlab/frame_induction.py` (`frame_primary_role` L337)
- Learner (selection over hand-declared atoms, cannot induce a space): `hdlab/learner/registry.py`,
  `hdlab/learner/core.py`
- Hash-random text vectors: `experiments/exp_construction_integration_relation_inference_v1.py`
  (`word_vector` L111)
