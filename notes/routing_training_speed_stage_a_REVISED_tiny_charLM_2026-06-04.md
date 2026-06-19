# Routing -- Training-speed Stage A REVISED (tiny char-LM with proper trick selection)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + Testbed (Testbed for later cloud stages)
**Date:** 2026-06-04 (REVISION of routing_training_speed_iterative_ladder_stage_a_tiny_charLM)
**Type:** Empirical Stage A with comprehensive design-space coverage from 3 design-space drills
**Source:** Three design-space drills landed 2026-06-04:
- research_drill_substrate_training_speed_design_space_2x
- research_drill_biological_precedents_animal_scales_substrate_2x
- research_drill_substrate_tier_emergent_tricks_per_llm_scale_2x

---

## REVISIONS from earlier Stage A routing

- **Speedup target deflated:** 10x+ -> 3-8x (realistic per Drill 1: 24x compound at 8B implies single-tier contributions are 1.5-3x; tiny char-LM substantially below that)
- **Trick selection comprehensive:** 11 specific tricks from 3-drill design space (not just "all our HP architectures")
- **Bio-architectural foundational tricks added:** DG expansion + STDP replay (Drill 2 high-ROI)
- **FastHebb 2024 GPU implementation path** noted as engineering accelerator
- **Composition axis taxonomy applied:** orthogonal-axis pairings (per shared-axis drill) prioritized

---

## Capability question

What wall-time speedup does substrate provide at TINY char-LM training scale (Wikitext-2; substrate-class N=4096-8192) using a COMPREHENSIVE substrate trick stack (universal-scale + bio-architectural + DeltaNet baseline), compared to standard 4-layer character-LM transformer baseline?

Target: 3-8x wall-time speedup to same target BPC (realistic per Drill 1 + Drill 3 per-trick estimates).

---

## Comprehensive trick stack (Stage A)

Eleven tricks selected from 3-drill design space, organized by axis (per shared-axis drill heterogeneous-pairing principle):

### Foundation (universal-scale; EXTENDS to all tiers per Drill 1)
- **T1: No-backprop Hebbian write** (~10^5x per-sample vs transformer; FastHebb 2024 GPU impl 70x available)
- **T2: Per-layer independent updates** (~4x depth latency; no backprop sync)
- **T4: Streaming Hebbian writes** (no batch coordination overhead)
- **T15: DeltaNet delta-rule attention** (Hebbian-attention layers; published 50% speedup at 1.3B)

### Capacity (W-modifying; HP at Bundle A)
- **T8: Drosophila sparse coding f=0.05** (~23x capacity gain per Willshaw-Buckingham)
- Position-binding for sequence representation (Bundle E E1 HP at trigram)

### Bio-architectural (Drill 2 high-ROI; NEW)
- **B1: DG expansion pattern separation** (preprocess input via N-fold expansion with f=0.005 sparsity; rodent precedent 20x expansion)
- **B2: STDP replay consolidation** (between training batches; iterate stored patterns with STDP-asymmetric update; offline consolidation)

### Heterogeneous task-axis (per shared-axis drill superadditive prediction)
- **cf-RPE** (task-supervised axis; Bundle A HP; W-modifying)
- **STDP-asymmetric** (temporal axis; Bundle E E2 HP at trigram with position-binding)

### Compositional (HP at 5-corpus aggregator today)
- **T7: Hierarchical aggregation** (multiple parallel substrate sub-models + meta-aggregator)

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_training_speed_stage_a_REVISED_comprehensive_v1_n8192`

**Cells:**

### Cell A-baseline: Standard char-LM transformer

- 4-layer character-LM transformer
- Wikitext-2 character-level corpus
- Train to convergence (target BPC per literature)
- Measure: wall-time to target BPC; per-sample compute
- Pure-gradient backprop standard training

### Cell A-substrate-minimal: Substrate-hybrid minimal (DeltaNet baseline)

- Substrate-Hebbian-attention layers (T1 + T15)
- Gradient-trained output head only
- Same Wikitext-2 character corpus
- Train to same target BPC
- Measure: wall-time to target BPC; per-sample compute
- Compare to A-baseline: SPEEDUP FACTOR primary metric
- **Pre-reg HP:** speedup >= 1.5x (DeltaNet published 50% at 1.3B; should hold at tiny scale)

### Cell A-substrate-foundation: Foundation + Capacity tricks

- T1 + T2 + T4 + T15 + T8 (Drosophila sparse) + position-binding
- Same task
- **Pre-reg HP:** speedup >= 2.5x

### Cell A-substrate-bio: Foundation + Capacity + Bio-architectural

- All Cell A-substrate-foundation tricks PLUS:
- B1: DG expansion (N-fold input expansion with f=0.005 sparse)
- B2: STDP replay consolidation (between batches; ~10% of training time on replay)
- **Pre-reg HP:** speedup >= 3.5x

### Cell A-substrate-comprehensive: ALL tricks heterogeneously combined

- All Cell A-substrate-bio tricks PLUS:
- cf-RPE (task axis) + STDP-asymmetric (temporal axis) — heterogeneous pairing per shared-axis drill
- T7 hierarchical aggregation (3 parallel sub-substrates over different corpus halves; substrate aggregator)
- **Pre-reg HP:** speedup >= 5x

### Optional Cell A-stress: Push for 10x

- Cell A-substrate-comprehensive PLUS:
- Modern Hopfield p=4 (if budget permits engineering)
- Iterated retrieval mode (Mode 4 per operating-modes drill)
- **Pre-reg HP:** speedup >= 8x

**Aggregate pre-reg:**

- **HARD-PASS:** at least one substrate cell achieves >= 3x speedup with BPC within 20% of baseline
- **MIDDLE:** speedup in [1.5x, 3x] across substrate cells
- **HARD-FAIL:** no substrate cell exceeds 1.5x speedup (substrate provides no meaningful training-speed advantage at tiny scale; methodology questioned)

## Resource

Local CPU + remote 4060 Ti (no cloud at Stage A)

## Cost ceiling

$0. Per-cell wall < 1h (target). Total Stage A wall: ~3-5h across 5-6 cells.

## P_deflated (per today's methodology)

**P_algebraic = 0.70**: trick catalog well-grounded across 3 drills; orthogonal-axis composition validated by ZeRO++ empirical

**P_implementation:**
- P_convergence = 0.55 (many architectures interacting; harder to converge cleanly than single primitive)
- P_budget = 0.85 (tiny model fits substrate-class easily)
- P_no_subsumption = 0.85 (most tricks W-modifying; DeltaNet has lit precedent)
- P_task_match = 0.65 (char-LM at tiny scale is well-validated)
- Joint P_implementation ~ 0.26

**P_joint = 0.70 * 0.26 ~ 0.18 for >= 5x speedup HP**
**P_joint = 0.70 * 0.40 ~ 0.28 for >= 3x speedup HP**

## Engineering scope

~6-8h:
- Wikitext-2 char-LM corpus + tokenization (reuse if exists)
- Standard char-LM transformer baseline (~2h)
- Substrate-Hebbian-attention layer (DeltaNet-class; FastHebb GPU impl if applicable; ~2h)
- DG expansion preprocessing (sparsify input to f=0.005; ~30 min)
- STDP replay consolidation phase (between batches; ~1h)
- cf-RPE + sparse + position-binding integration (reuse Bundle A/E scaffolds; ~1h)
- Hierarchical aggregator (reuse 5-corpus scaffold; ~1h)
- Wall-time measurement infrastructure + speedup factor calculation (~30 min)

## Strategic outcome

### If Cell A-comprehensive HP at >= 5x speedup

- Substrate's training-speed advantage EMPIRICALLY ANCHORED at tiny scale with realistic 5-10x
- Documents the working trick combination
- DISPATCH STAGE B (Pythia-160M with all Stage A tricks + tier-emergent additions)
- Product narrative: "substrate trains 5x+ faster at tiny scale; compound across tiers" validated

### If 3-5x speedup (MIDDLE-band)

- Real but modest speedup; identifies which tricks contribute most
- Iterate Stage A with refined trick selection before Stage B
- Document trick contribution attribution

### If < 3x speedup (HF)

- Substrate's training-speed claims need substantial reassessment at this scale
- Per pressure-test methodology: drill on WHY (which trick failed; which axes share gain)
- Don't escalate to Stage B until Stage A iteration produces meaningful speedup

---

## What this is (plain language)

Train Wikitext-2 character-LM five ways:
1. Standard transformer (baseline)
2. Substrate-hybrid minimal (just DeltaNet-class)
3. Substrate + foundation tricks (Hebbian + sparse + position-binding)
4. Substrate + bio-architectural (add DG expansion + STDP replay from biology)
5. Substrate comprehensive (heterogeneous task + temporal + capacity composition)

Measure wall-time to reach same target BPC. Compute speedup factor.

If substrate comprehensive cell achieves 5x+ faster: validates training-speed claim at tiny scale. Move up one tier (Pythia-160M).

Realistic target: 3-8x speedup per design-space drills. Not 10x; not 100x. Honest expectation.

---

## Future stages updated with realistic targets

### Stage B: Pythia-160M class (CONDITIONAL on Stage A HP)

- Apply ALL Stage A tricks PLUS tier-2-emergent: T13 residual hybrid + Hebbian warmup + per-layer bias correction + layer-aggregator early exit
- Realistic target: additional 1.3-1.8x speedup vs Stage A baseline equivalent (per Drill 3 individual trick contributions)
- Cumulative vs standard Pythia-160M training: ~5-15x (compound)
- Resource: remote 4060 Ti ($0); wall < 1h
- Pre-trained checkpoint test (Drill 1 recommendation)

### Stage C: Llama-3.2-1B class (CONDITIONAL on Stage B HP)

- Apply Stages A+B tricks PLUS tier-3-emergent: substrate-LoRA adapter routing (P=0.42) + fact-injection interface (P=0.45)
- Realistic target: ~10-20x compound vs standard Llama-3.2-1B training
- Resource: remote 4060 Ti (8GB fits 1B); wall < 1h
- $0 if fits remote; otherwise cheap cloud < 1h

### Stage D: Llama-3.1-8B class (CONDITIONAL on Stage C HP)

- Apply Stages A+B+C tricks PLUS **T12: substrate-MoE routing with deletion-cert** (flagship product target)
- Realistic target: ~24x compound vs standard Llama-3.1-8B training (per Drill 1)
- Resource: cloud H100 < 1h ~ $5-10
- Per user: keep cloud SHORT; iterate aggressively
- **THIS IS THE FLAGSHIP PRODUCT TIER** — substrate-MoE + deletion-cert is the unique offering

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed; Testbed informed for cloud stages
- Per [[feedback-cloud-only-when-absolutely-necessary]]: Stage A $0; Stages B-C strive for $0
- Per [[feedback-small-scale-first-methodology]]: Stage A at substrate-class; ladder up rungs in tight iterations
- Per [[feedback-short-cloud-runs-preferred]]: all stages target < 1h per individual run
- Per [[feedback-pressure-test-negative-findings]]: pre-reg HF triggers WHY-drill before proceeding
- Per [[feedback-no-padding-experiments]]: cells discriminate trick groups + speedup attribution
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF pre-reg with specific speedup thresholds
- ASCII-only

PROT-018: anchor uses `_n8192_v1` suffix
PROT-021: source=local CPU + remote 4060 Ti, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** REVISED Stage A is ~6-8h engineering + ~3-5h experiment wall total. $0 (local CPU + remote 4060 Ti). Reuses Bundle A + Bundle E + 5-corpus aggregator + DeltaNet-class scaffolds. Plus new bio-architectural primitives (DG expansion + STDP replay). Verdict drives Stage B dispatch + training-speed product narrative empirical validation with REALISTIC 3-8x target.

**Orchestrator + Testbed:** informed. Cap_map updates pending each stage outcome. Tier 4 substrate-MoE + deletion-cert is the FLAGSHIP product target at 8B.

**Research session:** holds for Stage A verdict + Drill 1+2+3 cap_map sub-property foundings; ships consolidated cap_map update on substrate training-speed empirical validation.
