# Brain-foundational fidelity scan -- the generative result-state world-model, all the way up

**problem:** build_the_generative_result_state_world_model | **date:** 2026-09-07 | **owner ask:** *"a 100%
brain-foundational fidelity scan of this component all the way up. How do we compare against the brain? Where
exactly are we losing signal?"*

**Method.** Two instruments. (1) An ORACLE LADDER (`experiments/exp_genworldmodel_signal_loss_ladder_v1.py`,
witness `verification/test_genworldmodel_signal_loss_ladder.py` 4/4) that grants each stage of the chain its
PERFECT (gold/oracle) version and measures the recovery on modern TellMeWhy non-adjacent (n=256, GOAL 92) --
the GAP between rungs IS the signal lost at that stage. (2) Per-stage RECALL diagnostics. All numbers below are
measured on disk, item-level; the brain descriptions are the PINNED/OUR-INVENTION verdicts from
`notes/BRAIN_FOUNDATIONAL_AUDIT.md` + the cited literature.

## The signal-loss ladder (where the signal goes)
```
R0 base (feed-forward silo, goal OFF) ........ 0.277
R1 + our surface means-end (objmatch) ........ 0.293   gap +0.016  <- what we currently add
R2 + a PERFECT goal simulator (incl multi-step) 0.441   gap +0.148  <- FORWARD-MODEL DEPTH (the dominant loss)
R3 + a PERFECT means-end for ALL causal types . 0.773   gap +0.332  <- the non-goal engines (physics/mental/affect)
R4 gold (the human answer) ................... 1.000   gap +0.227  <- extraction + selection + irreducible
```
Read it as a budget: of the +0.723 between our feed-forward base and the human ceiling, we currently capture
**+0.016**; a perfect GOAL forward-model would capture **+0.148 more** (~10x our current contribution); the
other causal engines +0.332; and +0.227 is extraction/selection/irreducible.

## The itemized brain-vs-us mechanism-diff (per stage, upstream -> the decision)

### Stage 1 -- Lexical/syntactic parse -> events + participants (EXTRACTION)
- **Brain (PINNED):** incremental, PREDICTIVE left-corner parsing (LIFG/pMTG) with roles assigned by the
  extended Argument Dependency Model (actor-first prominence, Bornkessel-Schlesewsky) -- top-down expectation
  constrains the parse as it reads.
- **Us:** spaCy arc-eager (greedy, HARD-COMMIT, feed-forward) -> verb-lemma events. The graded parser SOLVED
  built a globally-normalized replacement, but the front end feeding THIS rollout is still the greedy path.
- **Measured signal loss HERE: ~2% (NOT the bottleneck for this task).** Event-extraction recall = 0.98 on q,
  0.98 on the gold cause. TellMeWhy is clean, short, modern prose, so the parse is not where we lose signal --
  a genuine, and initially surprising, finding. (Contrast: SPACE measured 25-35% motion-event recall on harder
  prose; the extraction wall is real THERE, not on this gold.) Mechanism-diff (hard-commit vs predictive) is
  real but currently harmless for this task.

### Stage 2 -- Coreference / participant binding (who WANTS, who ACTS)
- **Brain (PINNED):** discourse referents (Heim/Kamp file-change semantics) maintained in the situation model;
  ATL/hippocampal binding keeps "the character who wanted X" identical to "the character who did Y".
- **Us:** the reader's coref (E3, NEEDS_ADAPTER) + a lenient, pronoun-permissive agent-binding check in the
  rollout (TellMeWhy is single-protagonist-dominated, so this rarely bites).
- **Measured signal loss HERE: small on this gold** (single-protagonist stories). Not separately isolated;
  folded into the +0.227 residual. Mechanism-diff: we bind by surface subject-head, not a resolved referent --
  a fidelity gap that would bite on multi-character prose.

### Stage 3 -- Goal-state extraction (the desideratum)
- **Brain (PINNED):** goal/intention representation (mPFC/vmPFC) + theory-of-mind inference (TPJ) recovering
  BOTH explicit and IMPLICIT goals.
- **Us:** `hdlab.goal_register` -- the PINNED Levin desiderative/intention/try matrix-verb lexicon (Tier-1
  explicit markers). HIGH fidelity for marked goals.
- **Measured signal loss HERE: ~11%.** Goal-detection recall on the gold cause = 0.89. The 11% miss is
  UNMARKED / IMPLICIT goals ("she grabbed her umbrella" implies wanting to stay dry) -- Tier-2 ToM inference we
  do not do. Mechanism-diff: lexical marker detection vs ToM goal INFERENCE.

### Stage 4 -- Result-state GENERATION (the forward model) -- THE DOMINANT LOSS
- **Brain (PINNED computation; UNPINNED neural impl):** the meaning of an action IS its result-state
  (Schank-Abelson RESULT), simulated forward over intuitive-theory engines with effectively INFINITE coverage
  because the link is COMPUTED, not stored -- intuitive physics (Battaglia-Tenenbaum mental simulation) +
  scripts/plans (Schank-Abelson) that chain MULTI-STEP (go-to-store -> at-store -> store-has-milk -> obtain).
- **Us:** `hdlab.world_state_register` (STRIPS GET/LOSE/TOGGLE) + `hdlab.possession_operators` (FrameNet) +
  VerbNet directed result predicates + `hdlab.force_dynamics_typer`. All SINGLE-STEP, resource-coded, sparse.
- **Measured signal loss HERE: +0.148 (the dominant recoverable gap).** The GOLD goal means-end is DIRECT
  (surface-reachable) for only 27%, SINGLE-STEP-VerbNet-coverable for 4%, and **MULTI-STEP plan for 68%**. Our
  single-step generator structurally cannot produce the 68%. This is the biggest, most brain-foundational gap:
  the brain's forward model is a rich, multi-step, generative simulator; ours is a sparse single-step lookup.
  Broadening the single-step lexicon (VerbNet directed, tested) does NOT help; a learned co-occurrence forward
  model (GEK, tested) is DIRECTIONLESS (scores "spill the milk" >= "buy the milk" for a milk goal) -> the wrong
  axis. **The fix is rollout DEPTH: a directed, multi-step plan/script rollout, not a bigger table.**

### Stage 5 -- The achievement CHECK (inverse planning: result-state |= goal-state?)
- **Brain (PINNED):** inverse planning / Bayesian ToM (Baker-Saxe-Tenenbaum) -- evaluate whether the simulated
  outcome achieves the goal-STATE; distinguish achieving from DEFEATING a goal.
- **Us:** a type-matched symbolic achievement check + DEFEAT suppression (a LOSE/negation on the goal object
  suppresses the boost). Brain-faithful in KIND, and it is what makes us DIRECTED where GEK is not.
- **Measured signal loss HERE: capped by Stage 4, not itself the bottleneck.** Where a result-state is
  generated, the check is correct (the top-down can-fail control: 10/12 vs the surface silo's 0/12). The check
  is only as good as the forward model feeding it.

### Stage 6 -- Cue INTEGRATION / selection (the competition)
- **Brain (PINNED):** weighted PARALLEL constraint satisfaction (McClelland-Rumelhart interactive activation;
  Kintsch construction-integration; Bates-MacWhinney Competition Model) -- cues combine ADDITIVELY with LEARNED
  validities and settle; a strong means-end cue can win even on a low-frequency/low-content candidate.
- **Us:** a MULTIPLICATIVE content-gated compose, score = content x (1 + physics + psych + goal). A low-content
  gold cause cannot be rescued by the goal boost (content ~ 0 -> the product stays ~ 0).
- **Measured signal loss HERE: ~25% of correct means-ends.** Even with a PERFECT goal boost, the argmax picks
  the gold cause only 75% of the time on the GOAL subset (oracle_goal = 0.75) -- base plausibility overrides
  the correct boost 25% of the time. Mechanism-diff: multiplicative content-gating vs additive
  learned-validity constraint satisfaction. This is a SECONDARY, more tractable brain-foundational fix (and the
  SDRT SOLVED already flagged the Kintsch settling as a no-op under uniform inhibition -- it needs signed,
  pairwise coherence, i.e. real constraint satisfaction).

### Stage 7 -- Top-down feedback into extraction (the RECURRENT LOOP)
- **Brain (PINNED):** predictive coding -- the situation model predicts and constrains every lower stage as it
  reads (Rao-Ballard; Friston; the N400 as forward semantic prediction-error, Rabovsky). This is the wall-map's
  dominant missing organ.
- **Us:** NOT wired live -- the reader is feed-forward silos. The rollout's expectation is demonstrated to
  disambiguate a case the silo cannot (the can-fail control) but it is not fed back into the live parse/extract.
- **Measured signal loss HERE: not separately quantified for this task** (extraction is already 0.98 here, so
  top-down would help LESS on this clean gold and MORE on harder prose / the who-did-what two-valid slice the
  parser SOLVED located). Mechanism-diff: the whole recurrent loop is absent live.

## Where we lose signal, ranked (the answer to the owner's question)
1. **Forward-model DEPTH (Stage 4): +0.148.** 68% of goal means-ends are multi-step plans our single-step
   generator cannot produce. The dominant, most brain-foundational gap. Fix = directed multi-step plan/script
   rollout over a curated foundation (NOT a bigger single-step lexicon, NOT co-occurrence).
2. **Cue INTEGRATION / selection (Stage 6): ~25% of correct means-ends overridden.** Multiplicative
   content-gating vs the brain's additive weighted constraint satisfaction. A tractable secondary fix.
3. **Goal INFERENCE (Stage 3): ~11%.** Unmarked/implicit goals need Tier-2 ToM, not lexical markers.
4. **The other causal ENGINES (Stage 3/R3 gap): +0.332.** The goal engine is only ~1/3 of the total means-end
   signal; physics/mental/affect means-ends each need their own generative engine (the causal reasoner's U8 is
   the class-level seed).
5. **Extraction (Stage 1) is NOT the bottleneck for this gold (0.98 recall)** -- a genuine finding; the
   extraction wall lives on harder prose, not clean modern TellMeWhy.

## SECOND PASS -- the PRECISE, orthogonal trace + a fidelity audit of EVERY component (owner: "double-check brain-foundationality of all components; figure out exactly where we're losing")
Instrument: `exp_genworldmodel_signal_loss_precise_v1.py` (witness `test_genworldmodel_signal_loss_precise.py`
5/5). The first-pass ladder lumped stages and scored extraction as "any event found (0.98)"; this pass isolates
each and audits the REUSED components (which the first pass took on trust). It CORRECTED one of my own
hypotheses.

### Exactly where the signal goes (measured, TellMeWhy non-adj n=256, GOAL 92)
- **Generation coverage, EXACT by hop-distance (the dominant residual):** the gold goal->action means-end is
  DIRECT (object/action reappears in q) **27%** / SINGLE_STEP (a directed result-state on q) **4%** / TWO_HOP
  (a 2-hop CSKG cause/enable bridge) **15%** / **DEEP_MULTISTEP (>2 hops -- a genuine plan/script) 51%.** Our
  mechanisms reach 46%; **51% is beyond a 2-hop reach.** This is the exact knowledge-depth wall, by distance.
- **Topical ranking (a CORRECTED finding):** I suspected the base's topical-content cue was a removable
  confound. It is NOT -- removing it CRASHES accuracy 0.277 -> 0.102 (-0.176 CI[-0.23,-0.12]); topical is the
  LOAD-BEARING default cue (associative spreading activation, Collins-Loftus, IS brain-faithful). BUT it is also
  the dominant ERROR source: **91% of the base's wrong picks are the max-topical NON-cause.** So the loss is not
  "topical is bad" -- it is "the generative means-end must OVERRIDE topical and cannot, exactly on the 51% DEEP
  slice where it is absent." Topical fills the vacuum the generative model leaves.
- **Extraction is NOT the loss point (tightened):** main-verb recall 0.98, goal-marker recall 0.89. The
  "goal object not present in q" (73%) is the MULTI-STEP phenomenon (the object legitimately isn't there --
  "wanted milk"/"went to the store"), not a parse failure. So for THIS gold the upstream parse is not where we lose.
- **Selection/integration:** even a correct means-end boost is overridden ~25% of the time by topical under the
  old multiplicative gate (first-pass oracle 0.75); the additive layer recovers part of it.
- **Irreducible:** ~9% of items have >1 gold cause (multi-cause / annotator latitude).

### Component brain-fidelity audit (ALL components; does the (in)fidelity leak signal HERE?)
| component | brain computation | PINNED / OUR-INVENTION | brain-faithful? | signal loss here |
|---|---|---|---|---|
| extraction (spaCy arc-eager) | incremental PREDICTIVE parse (LIFG/pMTG), eADM roles | OUR-INVENTION (greedy hard-commit) | NO in mechanism | ~2% (not the loss point on this gold) |
| coref / participant binding | discourse referents; ATL/hippocampal | PINNED | partial (surface-head, pronoun-lenient) | small (single-protagonist gold) |
| topical "content" cue | associative spreading activation (Collins-Loftus) | PINNED as a cue | PARTIAL -- right cue, WRONG ROLE (dominant ranker, not a weak prior) | load-bearing 0.277 BUT 91% of errors |
| physics/psych engines (U8) | Talmy force dynamics; appraisal; mental cascade | PINNED computation | YES in kind, class-level (coarse) | modest |
| goal_register | goal/intention (mPFC) + ToM | PINNED (Levin lexicon) | YES for marked, NO for implicit | 11% unmarked goals |
| world_state / possession_operators / VerbNet result-states | Schank-Abelson RESULT; lexical event structure | OUR-INVENTION (FrameNet/VerbNet-seeded) | YES in kind, SINGLE-STEP only | single-step coverage (8.7%) |
| **CSKG multi-step rollout knowledge** | generative script/plan SIMULATION | OUR-INVENTION | **NO -- RETRIEVAL over a static KB (the anti-pattern the brief names)** | reaches only TWO_HOP 15%; DEEP 51% beyond it |
| integration (additive constraint satisfaction) | interactive activation / Competition Model / Kintsch settling | PINNED | PARTIAL -- additive combine, not full settling w/ signed pairwise coherence | recovers selection partially |
| achievement check (inverse planning) | Baker-Saxe-Tenenbaum Bayesian ToM | PINNED | YES in kind (symbolic) | capped by generation |
| recurrent top-down loop | predictive coding (Rao-Ballard, Friston) | PINNED | NO -- absent live | the whole loop (not wired) |

### The two non-brain-foundational leaks the audit surfaced (beyond the known missing loop)
1. **CSKG is RETRIEVAL, not generation** -- my multi-step rollout rides on a static ConceptNet-derived KB, the
   exact "retrieve don't generate" architecture the problem exists to replace. It is a stopgap that reaches only
   the TWO_HOP 15%; the DEEP 51% needs a GENERATIVE plan/script model, not a bigger/denser KB traversal (a denser
   KB is a phase-diagram move that helps the traversal but does not change that traversal != simulation).
2. **Topical content is the right cue in the WRONG ROLE** -- brain-faithful as a prior, but here it is the
   dominant ranker and causes 91% of errors. The brain-faithful fix is not to remove it (load-bearing) but to let
   the generative means-end OVERRIDE it via proper constraint satisfaction -- which is why the integration fix
   AND the forward-model depth must land together (the interdependence).

## Verdict against the completion bar (checklist item 8)
The component is brain-foundational in KIND at Stages 3 (goal lexicon, PINNED), 4-check (inverse-planning
achievement, PINNED), and 5 (directed, not co-occurrence). It is NOT yet 100% brain-foundational at Stage 4
GENERATION (single-step vs the brain's multi-step generative simulator -- the +0.148), Stage 6 INTEGRATION
(multiplicative gate vs weighted constraint satisfaction -- the ~25%), and Stage 7 (the recurrent loop is not
live). The forward-model depth is the one that must be built to convey the brain function's full benefit; the
integration fix is a cheaper adjacent win; the recurrent loop is the shared program across all five consumers.
