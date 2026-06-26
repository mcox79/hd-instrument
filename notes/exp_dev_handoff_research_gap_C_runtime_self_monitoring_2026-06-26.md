# exp_dev hand-off -- research: GAP C runtime self-monitoring (cortex-composed runtime confidence)

**Filed:** 2026-06-26
**By:** research (Opus 4.7 1M)
**For:** exp_dev (cell-authoring; emergency-refill scan picks this up by mtime)
**Trigger:** USER deep drill on runtime self-monitoring; USER addendum requesting cortex-composition variant as top candidate. Research note: notes/research_gap_C_runtime_self_monitoring_2026-06-26.md

**Pause state:** check data/orchestrator_paused.flag before dispatch. If paused, defer to file pickup post-resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off is anchor pointers + substrate-product reading + tier hints. exp_dev autonomously decides cell-spec details (arm count, exact thresholds, smoke regime, dispatch queue).

---

## Anchor candidates (rank-ordered by P_deflated)

### Anchor #1 -- `runtime_confidence_cortex_composed_v1` (top P_deflated 0.55; recommended for next cell-author cycle)

**Anchor pointer:** notes/research_gap_C_runtime_self_monitoring_2026-06-26.md Section "(b) Cheap decisive test" ARM_CORTEX_COMPOSED + Section 2 Class 4.

**Substrate-product reading:** Audit device runtime confidence display. Highest-leverage anchor because it composes margin + cortex schema-prior + perturbation-agreement -- three orthogonal calibration signals integrated via logistic regression. Brain-aligned (mPFC ventromedial confidence prediction + hippocampal CA3 sharpness + theta replay).

**Tier hint:** Tier-1 (recommended Top-1). Composes with TWO_TIER (Gap 4 in flight; refuse-gate-confirmed importance scoring can be upgraded to continuous cortex-composed confidence) AND BCM (Gap 3 cell; W_schema dual-purpose for routing + confidence). Fallback path via kv_learned_projection at chain-grade 0.827 if BCM HARD_FAILs.

**Why-now:** USER addendum -- cortex layer is spinning up TODAY. BCM cell + TWO_TIER cell + Modern Hopfield are all converging this week. This drill's W_schema component piggy-backs on infrastructure being shipped anyway. Strategic timing: ship runtime confidence v1 BEFORE downstream consumers depend on binary refuse-gate as the only confidence signal.

**Key methodology rails:**
- ECE and AUROC on held-out 80% (calibration fit on 20%); 3 seeds; 5000 queries.
- Verify-the-referent (N): correctness labels MUST come from META_M7 independent of runtime confidence signal.
- BIAS-13/14/15 (R): cross-validate calibration fit; pre-flight smoke must show non-saturated agreement distribution; pre-flight cleanup-margin histogram must span the range (not all easy / not all hard).

### Anchor #2 -- `runtime_confidence_margin_v1` (P_deflated 0.50; v1-shippable single mechanism)

**Anchor pointer:** Section "(b) Cheap decisive test" ARM_MARGIN_ISOTONIC + Section 2 Class 1.

**Substrate-product reading:** The minimum viable runtime confidence -- top-1 minus top-2 cleanup score, post-hoc calibrated via isotonic regression. Ships standalone if cortex-composed isn't ready or HARD_FAILs.

**Tier hint:** Tier-1b (v1 fallback / parallel-track candidate). Single mechanism class; cheapest implementation. Direct exploit of substrate-better angle "direct distribution access" (the brain only experiences the winner). HARD_PASS bar: ECE <= 0.05 AND AUROC >= 0.75.

**Why-now:** If cortex-composed needs to wait on BCM landing, ship margin-only v1 first. Substrate users get SOMETHING immediately; cortex-composed v2 ships when BCM is chain-grade.

### Anchor #3 -- `runtime_confidence_perturbation_v1` (P_deflated 0.45; queued)

**Anchor pointer:** Section "(b) Cheap decisive test" ARM_PERTURBATION_AGREEMENT + Section 2 Class 2.

**Substrate-product reading:** Perturbation-stability check -- K=5 epsilon-bit-flipped re-queries; confidence = agreement rate. Strong substrate-better angle (brain cannot replay its own thought). HARD_PASS bar: ECE <= 0.05 AND AUROC >= 0.70.

**Tier hint:** Tier-2. Queue after Anchor #1 lands. Composes naturally with Anchor #1 (perturbation-agreement is one of the three signals fed to cortex-composed logistic regression).

**Why-now:** Pre-flight requirement: tune epsilon to produce non-saturated agreement distribution. If substrate's binding is too robust, all perturbations agree -> signal saturates. Smoke-cell needed to lock epsilon before main cell.

### Anchor #4 -- `runtime_confidence_ensemble_partition_v1` (P_deflated 0.40; queued; opportunistic harvest from TWO_TIER)

**Anchor pointer:** Section 2 Class 3.

**Substrate-product reading:** P-partition ensemble; confidence = inter-partition agreement. TWO_TIER's W_old/W_young is a natural 2-partition; can opportunistically harvest disagreement at zero extra cost from the TWO_TIER cell IN FLIGHT.

**Tier hint:** Tier-2 opportunistic. Skip standalone dispatch; instead add a 2-partition agreement column to the TWO_TIER metrics emission. Verify whether W_old vs W_young agreement carries calibration info as a CHEAP cross-cell signal.

**Why-now:** TWO_TIER is in flight. If we add the agreement-column instrumentation NOW (before the cell finishes), we get free Anchor #4 evidence at no extra compute. Time-sensitive: must request the addition before TWO_TIER lands the verdict.

### Anchor #5 (rescue) -- `runtime_confidence_meta_W_predictor_v1` (P_deflated 0.40; queued if all four HARD_FAIL)

**Anchor pointer:** Section 3 Candidate 5.

**Substrate-product reading:** Train a separate W_meta matrix (full hop trajectory -> P(correct)). Closed-form supervised fit on META_M7 labels. Cheap closed-form; bypasses the question of whether cleanup distribution is informative by LEARNING what predicts correctness.

**Tier hint:** Tier-3 rescue. Only dispatch if all four primary anchors HARD_FAIL.

---

## Context pointers (file paths -- no summaries inline)

- Research note (this drill): `notes/research_gap_C_runtime_self_monitoring_2026-06-26.md`
- TWO_TIER cell in flight (composition target #1): `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`
- BCM slow learning Gap 3 cell (composition target #2 -- W_schema source): `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` Section "schema-mediated bias"
- CERT 588 refuse-gate-5b (the binary baseline; continuous version generalizes): `notes/skunkworks_to_orchestrator_cc_all_CERT_588_LANDED_refuse_gate_5b_960fd3c6_layer3_reciprocal_2026-06-20.md`
- LEVER 4 depth-axis refuse-gate witness: `notes/skunkworks_to_expdev_testbed_cc_orch_research_LEVER_4_landed_VET_CHAINGRADE_ELIGIBLE_depth_refuse_gate_4layer_witness_CERT_589_2026-06-20.md`
- Substrate-as-LM methodology audit (distribution-access affordances): `notes/project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md`
- kv_learned_projection chain-grade primitive (cortex-composed fallback W): atom in substrate_index (chain-grade 0.827; 2026-06-20)

---

## Contract section

- exp_dev OWNS cell-spec authoring (arm count, exact thresholds, smoke regime, dispatch queue choice).
- Research OWNS the mechanism claim + brain-fidelity + HARD-PASS/HARD-FAIL bands documented in the research note.
- Skunkworks OWNS landed-VET classification (chain-grade vs MM vs by-construction-saturation) after cell lands.
- Per [[feedback-cert-owner-overrides-director-via-by-construction-saturation]]: default classification = MM; let cert-owner tier UP.

## Autonomy declaration

Per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]]: the choice between Anchor #1 (cortex-composed) and Anchor #2 (margin-only v1) emerges from data -- if BCM cell hasn't landed by exp_dev's cycle, ship Anchor #2 first and queue Anchor #1 as v2. If BCM has landed chain-grade, ship Anchor #1 directly.

Per [[feedback-substrate-mine-capacity-before-extrapolating]]: confirm kv_learned_projection at chain-grade 0.827 in atoms before claiming the fallback path is feasible. Confirm META_M7 labels are accessible at substrate's standard regime before claiming the supervised signal is available.

Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]]: lit says "calibration is hard for deep nets" but substrate has structural advantages (direct distribution access; cheap parallel re-query; no softmax overconfidence collapse). Default DISPATCH; the substrate-novel variant differs from prior failed deep-net calibration work.
