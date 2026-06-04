# ROUTING — Multi-layer substrate integration probe (NEW capability dimension)

**From:** Research session
**To:** Orchestrator (primary), Testbed (engineering reference)
**Date:** 2026-06-04
**Status:** USER AUTHORIZED 2026-06-04 ($0 CPU; ~1-2h wall; dispatches after Experiment C rung 1 lands).

---

## What this is (plain language)

We have NEVER tested substrate observers attached at MULTIPLE LLM LAYERS SIMULTANEOUSLY. Previous designs (Hyperprobe, Experiment B/C) put substrate at ONE LLM layer. This routing introduces a NEW capability dimension: per-layer substrate observers running concurrently, each computing its own κ_2 / κ_3 / κ_4 fingerprint trajectory.

Hypothesis: different LLM layers encode different abstractions (early = syntactic, middle = semantic, late = compositional). Multi-layer substrate observers should reveal:
1. **Earlier predictive signal for training-phase changes** (different layers converge at different times)
2. **Layer-specific drift detection** (syntactic drift visible at early layers; semantic drift at middle; compositional drift at late)
3. **Per-layer deletion-certificate guarantees** (rank-1 edits at one layer don't affect other layers' fingerprints)

This is a complementary dimension to multi-channel orchestration:
- **Multi-channel** = K substrate primitives at ONE layer, each computing different quantities
- **Multi-layer** = K substrate observers (same primitive) at DIFFERENT layers, each computing layer-specific signals
- **Multi-channel × multi-layer** = K × L total substrate signals (full cross-product, future experiment)

---

## Sequencing — runs AFTER Experiment C rung 1 lands

This experiment should NOT dispatch until Experiment C rung 1 verdict (the single-layer multi-channel orchestration test). If single-layer multi-channel HARD-PASSes, multi-layer is a natural extension. If single-layer HF, the multi-layer design should be re-examined first (may have same failure mode).

Estimated dispatch sequence:
1. Experiment C rung 1 (~30 min) → land verdict
2. IF Experiment C HP at rung 1 → dispatch this multi-layer probe (~1-2h)
3. IF Experiment C MIDDLE / HF → hold multi-layer probe; iterate single-layer first

---

## Experiment design — multi-layer substrate observers at rung 1 scale

**Anchor name:** `substrate_multi_layer_observer_rung1_tinychar_v1_n4096`

**Resource:** local CPU
**Wall:** ~1-2 hours
**Cost:** $0

### Test architecture

Model: 4-layer transformer or LSTM tiny char-LM (~50-100k params; rung 1-2 scale)

Substrate observers attached at each layer:
- Layer 1 observer: computes κ_2 / κ_3 / κ_4_excess every 5 training steps
- Layer 2 observer: same
- Layer 3 observer: same
- Layer 4 observer: same

4 substrate fingerprint trajectories tracked through training (vs single-layer baseline at layer 4 only).

### Conditions (3-arm ablation)

- **Arm A (single-layer baseline):** substrate observer at layer 4 only
- **Arm B (multi-layer, no orchestration):** substrate observers at layers 1, 2, 3, 4; signals tracked but not combined for training
- **Arm C (multi-layer + orchestration):** substrate observers at layers 1, 2, 3, 4; per-layer signals weighted by learned σ_k(layer) precision; combined for training (small substrate-contributed loss term)

Each arm: 1000 training steps, 3 seeds.

### Measurements

Primary outcomes:
- **Predictive lead time per arm:** does substrate signal cross threshold N steps before validation-loss crosses corresponding threshold?
- **Per-layer fingerprint distinctness:** correlation matrix between layer-1 κ_3 trajectory and layer-4 κ_3 trajectory; lower correlation → more layer-specific information; higher correlation → redundant
- **Drift-class specificity:** introduce 2 types of held-out drift (syntactic perturbation at character level; semantic perturbation at word-pair level); measure which layer's κ_3 detects which drift class

Auxiliary measurements:
- Per-layer σ_k weight at convergence (for Arm C; reveals which layer the orchestrator weighted highest)
- Cross-layer correlation matrix (4×4) of κ_2 / κ_3 / κ_4 trajectories
- Final validation CE per arm

---

## Pre-registered HP / MID / HF bands

### HARD-PASS conditions (any 2 of 3 trigger HP)

**HP-1 (earlier predictive signal):**
- Arm B or Arm C gives predictive lead time ≥ 30% LONGER than Arm A baseline
- Across 3 seeds (3/3)

**HP-2 (layer-specific information):**
- Per-layer fingerprint correlation matrix shows OFF-DIAGONAL values < 0.5 (layers carry distinct information)
- Drift-class specificity: layer-1 detects syntactic drift before layer-4; layer-4 detects compositional drift before layer-1
- 3/3 seeds

**HP-3 (orchestration gain):**
- Arm C beats Arm B by ≥ 5% on validation CE AND by ≥ 5% on predictive lead time
- 3/3 seeds

### MIDDLE bands

- Earlier predictive signal: 10-30% LONGER lead time at Arm B or C
- Layer-specific information: off-diagonal correlations 0.5-0.7 (some redundancy)
- Orchestration gain: 2-5% gain at Arm C vs Arm B

### HARD-FAIL conditions (any 1 of 3 triggers HF)

**HF-1 (no layer-specific information):**
- Per-layer fingerprint correlation matrix off-diagonal > 0.85 (layers all give same signal)
- Multi-layer integration adds no new information
- Multi-layer dimension UNVALIDATED at this substrate-architecture

**HF-2 (Arm C collapses):**
- Arm C performs WORSE than Arm A baseline
- Multi-layer orchestration is actively harmful in this regime

**HF-3 (gradient pathology):**
- Multi-layer substrate contribution to loss causes gradient norm collapse OR explosion
- Engineering-pathology rather than capability-failure; iterate at rung 1

---

## Strategic outcomes

### If HP

- **New capability claim founded:** "Substrate provides depth-specific training signals via per-layer observers; multi-layer integration delivers earlier predictive lead time AND drift-class specificity"
- Multi-layer + multi-channel dimensions cross-product becomes natural Phase E candidate (16-32 channels × 4-32 layers)
- Per-layer deletion-certificate sub-capability becomes testable
- Connects to Hyperprobe's k-means-over-layers approach but with CONCURRENT observers rather than compressed sum-pool
- Strengthens "substrate-as-multi-channel-multi-layer training infrastructure" narrative

### If MIDDLE

- Layer-1 and layer-4 carry SOME distinct information but with redundancy
- Iterate at rung 1: try different layer spacing (e.g., {1, 4} vs {1, 2, 3, 4})
- Or different substrate primitives per layer (κ-based at early, counterfactual at middle, deletion at late)

### If HF

- Multi-layer dimension UNVALIDATED at substrate-architecture this scale
- Doesn't refute multi-channel claim (still validated separately by Experiment C)
- Strategic implication: substrate's training-integration value comes from multi-channel-at-one-layer, not from multi-layer-at-different-depths
- Either way, informative for the cap_map (narrows the integration design space)

---

## Engineering scope

Reuses the tiny char-LM scaffold from Experiment C rung 1 + adds:
- Forward hooks at all 4 layers (not just last layer)
- Per-layer substrate observer instances (parameterized; same primitive code)
- 3-arm condition switching (single-layer / multi-layer-tracked / multi-layer-orchestrated)
- Per-layer σ_k learnable parameter for Arm C
- Cross-layer correlation matrix logging

Estimated engineering effort: 2-4h additional on top of Experiment C scaffold. Most code is reused.

---

## Discipline declarations

- Per `feedback_routings_address_orchestrator_not_testbed`: orchestrator primary
- Per `feedback_small_scale_first_methodology`: rung 1 design; cloud is last validation pass
- Per `feedback_plain_language_experiment_tracking`: described by what it tests
- Per `feedback_brain_inspired`: multi-layer corresponds to brain's hierarchical cortical processing (different layers encode different abstractions)
- Per `feedback_no_padding_experiments`: tests a genuinely new dimension of substrate integration (multi-layer); not a redundant variant of multi-channel
- Per `feedback_keep_research_exploratory_not_narrowing`: opens a new design-space axis (multi-layer × multi-channel cross-product)
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands tied to 3 specific predictions

---

**END.**

**Orchestrator:** queue this routing for dispatch AFTER Experiment C rung 1 verdict lands. If Experiment C HP → escalate to this multi-layer probe. If Experiment C MIDDLE / HF → hold this routing pending design re-examination.

**Testbed:** engineering scope is incremental on top of Experiment C scaffold (~2-4h additional). No fresh scaffolding needed if Experiment C scaffold is built per shared-infrastructure pattern.

**Research session:** holds for sequential verdicts (Experiment C → multi-layer probe → cross-product Phase E candidate); ships capability-implication note based on outcome.
