# exp_dev hand-off -- research: self-modification stability 5x drill

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_self_modification_5x_2026-06-10.md
Urgency: HIGH -- 5 concrete CPU-local tests gate all in-place modification designs;
  additive-only path is trivially safe and can be certified without any tests;
  homeostatic gate + sleep consolidation architecture enables the "improves with use"
  product claim on the NORTH STAR head-to-head benchmark

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions
below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: self_mod_homeostatic_gate_v1 (HOMEOSTATIC-GATE)

Anchor pointer: Research note Section 6 F2.1 + Section 8 HP1/HF1 + BCM sliding threshold
  (Section 1 A2); Kirkpatrick et al. 2017 EWC; Cooper and Bear 2012.
Substrate-product reading: Sequential in-place modification of substrate vectors is known
  to degrade via superimposed noise accumulation (ROME/MEMIT collapse at K~100 edits).
  A homeostatic gain gate -- modification rate alpha scaled by g(probe_accuracy) -- is
  predicted to maintain probe accuracy > 0.90 after 20 modification rounds. If this passes,
  it unlocks runtime learning from user interactions with a stability certificate. The
  product claim "substrate improves with use without degrading existing knowledge" depends
  on this gate working.
Tier hint: CPU-local laptop run. No GPU needed. Pure vector arithmetic + probe evaluation.
  1000-vector substrate, 20 modification rounds, 100-vector held-out probe set. Estimated
  wall time under 10 minutes.
Why-now: Current substrate is STATIC after initialization. No runtime learning. This is
  the cheapest gate-opener for a major capability class. Failure result is also informative
  (shifts to additive-only path which is also fast to certify).

Pre-reg bands:
  HARD-PASS: homeostatic gate maintains probe accuracy > 0.90 at round 20; ungated control
    degrades below 0.70 (confirming the problem is real and the gate works)
  MIDDLE-BAND: gate maintains 0.80-0.90 (partial; triggers threshold-tuning sub-anchor)
  HARD-FAIL: gate also degrades below 0.80 (gate design is wrong; pivot to additive-only)

### Anchor 2: self_mod_additive_only_cert_v1 (ADDITIVE-CERT)

Anchor pointer: Research note Section 5 point 2 + Section 8 HP3/HF3; Rusu et al. 2016
  Progressive Neural Networks; PackNet Mallya and Lazebnik 2018.
Substrate-product reading: Additive extension (add new vectors, never modify existing ones)
  is trivially stable for hyperdimensional stores because superposition is non-destructive
  by design. Certifying this as the BASELINE modification policy costs near-zero and
  immediately unlocks "substrate can be augmented at runtime." This is the no-risk path
  that should be verified first regardless of Anchor 1 outcome.
Tier hint: CPU-local. Verification only: insert 500 new vectors into a 1000-vector substrate,
  measure probe accuracy on the original 100-vector held-out set before and after. Pass
  criterion is no degradation (delta < 0.01). Takes under 2 minutes.
Why-now: This is the structural guarantee that should already be true. Verifying it
  explicitly closes a gap in the certified capability set. Required before any product
  claim about runtime augmentation.

Pre-reg bands:
  HARD-PASS: probe accuracy delta < 0.01 after 500 additive insertions
  MIDDLE-BAND: delta 0.01-0.05 (tolerable; note the interference pattern for large stores)
  HARD-FAIL: delta > 0.05 (additive extension is NOT safe; cross-contamination via nearest-
    neighbor interference; PackNet-style binary mask isolation required)

### Anchor 3: self_mod_noise_accumulation_probe_v1 (NOISE-PROBE)

Anchor pointer: Research note Section 5 E7 + Section 8 HP4/HF4; Yao et al. arXiv:2401.07453
  model editing collapse paper; superimposed noise accumulation (ICML 2025).
Substrate-product reading: Each sequential in-place modification adds residual contamination
  to unmodified vectors. The ROME/MEMIT collapse pattern shows this residual accumulates
  and crosses a collapse threshold at K~100 edits. For substrate: measure contamination
  spread at K = 10, 50, 100, 200, 500. This gives the safe modification budget M_safe
  without any homeostatic gate. If M_safe > 1000, in-place modification is safe within
  a session. If M_safe < 50, only additive extension or gated modification is viable.
Tier hint: CPU-local. Sequential single-vector modifications to a 1000-vector store,
  cosine distance measurement on unmodified vectors after each batch. Under 15 minutes.
Why-now: Anchors 1 and 2 need this baseline to interpret their results. The contamination
  spread result directly sets the engineering requirements for any homeostatic gate.

Pre-reg bands:
  HARD-PASS: contamination spread < 5% of store at K=100 (safe budget > 10% of store)
  MIDDLE-BAND: spread 5-20% at K=100 (partial; homeostatic gate is required for online use)
  HARD-FAIL: spread > 20% at K=50 (in-place modification is inherently destructive;
    only additive extension is viable for this substrate architecture)

### Anchor 4: self_mod_sleep_consolidation_v1 (SLEEP-GATE)

Anchor pointer: Research note Section 6 F2.7 + Section 8 HP2/HF2; Diekelmann and Born
  2010; Tononi and Cirelli 2014 synaptic homeostasis hypothesis.
Substrate-product reading: Write-ahead log + periodic consolidation pass (retain modifications
  with probe_delta > theta; discard others; batch apply in order of decreasing benefit)
  is predicted to maintain > 0.92 probe accuracy with < 30% modification rejection. This
  is the full runtime-learning architecture that supports the NORTH STAR "improves with use"
  product claim. Depends on Anchor 1 baseline and Anchor 3 noise measurement.
Tier hint: CPU-local. Requires write-ahead log infrastructure (trivial). Consolidation
  pass is a probe re-evaluation loop. Wall time under 20 minutes for 20 modification rounds.
Why-now: If Anchor 1 shows homeostatic gate works and Anchor 3 shows contamination is
  manageable, this anchor assembles the full architecture and provides the combined stability
  certificate. It is the direct predecessor to a product-facing "substrate learns from user
  queries" feature.

Pre-reg bands:
  HARD-PASS: sleep variant maintains > 0.92 probe accuracy at round 20 AND rejection
    rate < 30% (most proposed modifications are beneficial and accepted)
  MIDDLE-BAND: accuracy 0.85-0.92 OR rejection rate 30-70% (consolidation threshold
    needs recalibration)
  HARD-FAIL: accuracy < 0.80 OR rejection rate > 70% (modification generator is producing
    mostly harmful candidates; the upstream modification proposal mechanism needs redesign)

### Anchor 5: self_mod_property_gate_v1 (PROPERTY-GATE)

Anchor pointer: Research note Section 6 F2.4 + F2.10 + Section 8 HP5/HF5; type-safe
  transformations; git-versioned substrate.
Substrate-product reading: Property tests (norm bound check, binding associativity smoke,
  retrieval monotonicity check) run after each modification and trigger rollback on failure.
  Predicted to catch > 80% of modifications that degrade probe accuracy by > 0.05. This is
  the lowest-cost safety net that can be added to ANY modification architecture. If it works
  (catches > 80%), it should be added to all in-place modification paths as a backstop.
  If it does not work (catches < 20%), the primary safety gate must be probe-set evaluation.
Tier hint: CPU-local. Property tests take microseconds each. Run on the modification sequence
  from Anchor 3. No additional substrate work required.
Why-now: This anchor is almost free (runs on Anchor 3's data). It directly answers whether
  structural invariant checks are informative predictors of modification harm, which
  determines the engineering design of the full modification pipeline.

Pre-reg bands:
  HARD-PASS: property gates catch > 80% of modifications with probe_delta < -0.05
  MIDDLE-BAND: catch rate 40-80% (partial; supplement with probe evaluation)
  HARD-FAIL: catch rate < 20% (property tests are not informative; use probe evaluation
    as the only gate)

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_self_modification_5x_2026-06-10.md
- Prior handoff (ToM/social reasoning): d:/AI/hd-instrument/notes/exp_dev_handoff_research_HOL_meta_reasoning_biology_3x_2026-06-09.md
- Exp-Dev post-compaction brief (compositional cliff): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md
- Orchestrator post-compaction brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md
- North Star memory entry: C:/Users/marsh/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md

---

## Contract

This hand-off file was authored by the research sub-agent. Exp_dev MUST:
1. Read the research note at the context pointer above before designing any experiment.
2. Treat the anchor descriptions as ROUTING POINTERS, not implementation specs.
3. Apply pre-dispatch speed/harden/progress discipline before every dispatch
   (per feedback_pre_dispatch_speed_harden_progress_discipline.md).
4. Check data/orchestrator_paused.flag before queuing.
5. Run Anchor 2 (additive cert) first -- it is near-zero cost and gates the interpretation
   of all other anchors.
6. Run Anchor 3 (noise probe) second -- its result sets the engineering requirements for
   Anchors 1, 4, 5.

## Autonomy declaration

Exp_dev has full authority to order, batch, skip, or re-design anchors above within the
scope of the research note findings. Exp_dev does NOT need to return to research for
clarification before running Anchors 1-5. If ALL anchors hard-fail (unlikely but possible),
exp_dev should file a strategy_request note identifying the failure and requesting a
2x-drill on alternative substrate architectures before proceeding.
