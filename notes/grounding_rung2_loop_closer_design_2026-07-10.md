# Grounding Rung-2: The Loop-Closer + Ingest Capability — Build Design — 2026-07-10 (Director)

**Purpose:** rung-1 (the concreteness cell) tests whether an exterior measured attribute GROUNDS (adds info over graph-alone for ATTRIBUTE prediction). But the ORIGINAL wall that started this whole arc was inductive RELATIONAL inference -- predict held-out EDGES, degree-invariantly -- the thing the additive code did degree-DEPENDENTLY (collapsed on the rare tail, LOW=-0.040). Rung-2 must CLOSE THE LOOP: does grounded geometry fix the ORIGINAL failure? This is the actual finish line of "make relational real." Build-ready the moment the concreteness FULL lands positive.

## The loop-closer claim (rung 2b -- THE priority)

Consolidating the ConceptNet graph WITH the exterior measured attribute(s) produces a geometry that improves HELD-OUT RELATIONAL inference (predict a withheld edge's target) DEGREE-INVARIANTLY -- where the additive/geometric code (same held-out task, same degree strata) collapsed on the low-degree tail.

This is distinct from rung-1: rung-1 predicts the ATTRIBUTE (concreteness); rung-2 predicts held-out RELATIONS, and asks whether GROUNDING THE GEOMETRY (anchoring it to exterior measured attributes during consolidation) makes relational inference degree-invariant. If yes -> grounding is the lever the code-swaps weren't, and the arc closes. If no -> grounding predicts attributes but does not transfer to relational inference (a real, bounded finding: attribute-grounding != relational-inference).

## The test (reuse the retest's EXACT relational-inference apparatus -- clean rematch)

- Held-out RELATION task: same as exp_grounding_additive_geometric_degree_control_retest_v1 (COMPLETABLE reach@1, degree strata LOW/MID/HIGH, degree-only popularity baseline, oracle-leak/codes_necessary check). Reuse it so the comparison to the code's failure (LOW=-0.040/MID=+0.085/HIGH=+0.264) is apples-to-apples.
- Arms: (1) GROUNDED consolidation geometry (graph + measured attributes, diffusion-with-restart) -> relational inference; (2) UNGROUNDED consolidation (graph alone) -> relational inference; (3) the additive code (the failed baseline); (4) degree-only popularity; (5) random.
- DECISION (pre-register both bands): HARD_PASS = grounded arm gives a relational-inference lift over ungrounded-graph-alone that SURVIVES the low-degree tail (LOW+MID gap >= material bar) AND beats popularity AND survives oracle-leak. HARD_FAIL = grounded ties ungrounded (grounding doesn't transfer to relational inference) OR tail-collapses (still degree-dependent) OR pop-recovers.
- THE KEY CONTRAST: does the grounded geometry's relational-inference LOW-stratum gap go POSITIVE (grounding fixes the tail) where the code's went NEGATIVE (-0.040)? That single number is the finish line.

## Fair-test controls (same lens; non-negotiable)
- The exterior attribute channel must be LOAD-BEARING for the RELATIONAL lift (ablate attributes -> relational lift collapses = grounding did the work, not consolidation alone). This is the rung-2 analog of the rung-1 ablation.
- Scrambled-attribute must-fail (permute attribute values -> relational lift vanishes).
- Degree strata + popularity baseline + oracle-leak (from the retest).
- Real ConceptNet graph; determined query (unique-successor filtering where needed, per the info-ceiling lesson).
- Collapse discriminator (effective-rank floor).

## Rung 2a (generalization -- run alongside/after): is grounding ATTRIBUTE-GENERAL?

Concreteness is one psycholinguistic dimension. Add a SECOND, genuinely-different measured attribute to confirm grounding isn't concreteness-specific:
- VALENCE/AROUSAL (Warriner et al. 2013, ~14k words, affective norms) -- emotional, orthogonal to perceptual concreteness. Same join-to-ConceptNet + fairness-gate structure.
- (later) Age-of-acquisition (Kuperman 2012), sensory-modality norms (Lynott-Connell).
- MULTI-ATTRIBUTE FUSION (the ball/rock "multiple senses that agree"): does grounding with concreteness + valence + AoA TOGETHER produce stronger/richer geometry than any single one? Direct test of the multi-independent-channel-agreement hypothesis. Each attribute = a "sense"; do they compose?

## Rung 2c (the capability -- the foundational build): a reusable GROUNDED-ATTRIBUTE-CHANNEL pipeline

Turn the one-off testbed into infrastructure -- the concrete form of "grounded ingest," the foundation the whole program rests on (substrate currently = pure symbol graph, ZERO grounded data):
1. INGEST a measured-attribute dataset joined to concepts (provenance-tracked testbed file, per the concreteness cell).
2. Auto-run the FAIRNESS GATE (F_triv < F_A < C; block if common-cause / no-headroom).
3. CONSOLIDATE it into the geometry (diffusion-with-restart, degree-invariant, anti-collapse).
4. Expose the grounded geometry as a QUERYABLE layer (attribute prediction + grounded relational inference).
This generalizes the concreteness cell from an experiment into a capability the substrate can repeat for any measured attribute -- the pipeline that finally puts grounded knowledge into a symbol-only substrate.

## Sequencing (2-hour drive)
- GATE: concreteness FULL must land POSITIVE (aggregate clears 0.05, tail holds, scrambled fires) before rung-2b is worth building -- if rung-1 grounding is null, rung-2 relational transfer is moot (fix rung-1 first).
- On positive rung-1 FULL: build rung-2b (the loop-closer) FIRST -- it is the finish line. Rung-2a (valence generalization) + rung-2c (capability) follow.
- If rung-1 FULL lands MIDDLE/negative: diagnose (is concreteness too weak a signal? try valence; or is the consolidation lift real but small -> more attributes / fusion). Do NOT abandon grounding on one attribute's smoke-miss.

## The honest finish-line statement
"Make relational real" closes IF: grounded geometry (consolidation anchored to exterior measured attributes) improves held-out RELATIONAL inference degree-invariantly -- turning the code's LOW=-0.040 tail-collapse into a positive tail lift. That is the single number rung-2b targets. Everything else (router, more attributes, the pipeline) is the build-out around that proof.
