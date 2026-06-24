# COMPOSITION STORE-MINE INVENTORY
**Date:** 2026-06-24  
**Anchor:** A1 joint-compose HARD_FAIL analysis  
**Scope:** 60+ composition cells; 11 validated rules; 6 failure hypotheses  

---

## CATEGORY A: MULTI-PRIMITIVE COMPOSITION (2+ chain-grade primitives)

### SUCCESS (super-additive or additive):

1. `exp_substrate_capacity_composition_b2xb4_v1_n2048` | HARD_PASS | 240x capacity | B2-sparse x B4-ensemble multiplicative | Sparse-factor 48x + K=5 ensemble = 240x observed == predicted.

2. `exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` | HARD_PASS | gap=3.744 | cf-RPE x STDP CharLM | Heterogeneous-axis superadditive 5/5 seeds. Task + temporal orthogonal at N=512.

3. `exp_substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1` | HARD_PASS | macc corr_bundle=0.9986 | corr_bundle + xor_corr | Two-operator stack closes gap that neither alone closes.

### PARTIAL/MIDDLE_BAND:

4. `exp_substrate_K2_x_cfrpe_compose_LM_v1` | MIDDLE_BAND | K2_cfrpe=7.5956 | K=2 x cf-RPE | Sub-additive: lift=0.101 > best_single (0.088) but marginal.

5. `exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` | MIDDLE_BAND | hetplast=7.1654 | cf-RPE + STDP at N=8192 | Partially interfere; N-dependent super-additivity loss.

### HARD_FAIL (sub-additive collapse):

6. `exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1` | HARD_FAIL_SUB_ADDITIVE | FULL_JOINT=7.8919 | 5-arm stack: Hebbian + cf-RPE + STDP + K2 + cleanup | **CORE A1 FAILURE:** cf-RPE improves (+0.218), STDP hurts (-0.116), K2 marginal (+0.026), cleanup CATASTROPHIC (-0.714). Best single (7.0888) vs joint (7.8919) = 0.8 BPC worse than unigram.

7. `exp_c_composition_storage_density_v1` | HARD_FAIL | L=1.00 | Modular K8 + Whitening + kWTA-sparse | All arms saturate at M_fail=2001. Zero-lift; mechanisms not orthogonal.

8. `exp_composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096` | HARD_FAIL | L_fid flat | Depth x K parametric sweep | Formula L_fid ~ K*C*alpha refuted; no K-scaling empirically.

---

## CATEGORY C: HIERARCHICAL / INTEGRATED ARCHITECTURE

1. `exp_q_a3_l100_cross_layer_composition_v1_n16384` (50+ variants L=10/100/10000) | HARD_PASS | lacc=1.0 at L=100 | 100-layer stacked-W | Perfect cross-layer scaling when each hop is independent retrieval. Chain-grade L=10 to L=10000.

2. `exp_substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1` | HARD_PASS | gate_b=true | corr_bundle + xor_corr | Two-operator tier-2 composition via integrating equivalence-check gate.

---

## CATEGORY D: GATING / ROUTING / CONDITIONAL

1. `exp_substrate_K2_x_cfrpe_compose_LM_v1` | MIDDLE_BAND | GATE_TEMP=0.5 | K=2 + cf-RPE soft-gated | Routing is live but doesn't rescue sub-additivity.

2. `exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1` | HARD_FAIL | mh_iters=3, cleanup post-logit | Gated cleanup at end-of-pipeline fails catastrophically.

---

## HYPOTHESIS TEST: 6 FAILURE THEORIES

### H1: Primitive Interference (cleanup destroys W)
**Verdict:** TRUE for SEQUENTIAL composition. Cleanup chain-grade alone but destructive post-plasticity (-0.714 BPC). Cleanup CV=0.0 (rigid).

### H2: Order Matters
**Verdict:** CONDITIONAL. Matters only for same-axis (K+cf-RPE). cf-RPE+STDP superadditive regardless of order at N=512.

### H3: Readout Failure
**Verdict:** PARTIALLY TRUE. Readout (T/lambda grid) can't recover from W-space corruption at Hebbian level.

### H4: Hyperparameter Mismatch
**Verdict:** PARTIALLY TRUE. Rails pass but joint config != best-per-arm config. Contributes but not root cause.

### H5: Substrate Lacks Integration Architecture
**Verdict:** TRUE for DEEP (L=100 succeeds as independent hops). A1 failure is SHALLOW (5 primitives in 1 layer). Substrate lacks intra-layer routing/gating.

### H6: Conflicting Objectives
**Verdict:** TRUE but INSUFFICIENT. cf-RPE (selective) vs cleanup (overlap) have inverted objectives on same W. Different objectives NECESSARY for super-additivity but A1 lacks gating to resolve conflicts.

---

## CORE INSIGHT: Why Cross-Layer Succeeds, Intra-Layer Fails

**Cross-layer (L=100):** Each hop independent (entity, relation) queries. No mixing of optimization targets within a layer. Stacking sequential and decoupled.

**Intra-layer joint (A1):** 5 primitives on SAME W simultaneously:
- Hebbian: maximize overlap
- cf-RPE: suppress errors (selective)
- STDP: temporal coherence
- K2: structural constraint
- Cleanup: enforce overlap (OPPOSITE cf-RPE)

cf-RPE and cleanup have INVERTED objectives. Each corrupts the previous gain. No intermediate normalization/gating between primitives.

---

## VALIDATED COMPOSITION RULES (from composition_matrix.md + verified cells):

1. Same-axis (capacity) → SUBSUMED (B2+B6; K2+cf-RPE)
2. Same-axis (parallel within hierarchy) → MULTIPLICATIVE (B2 x B4 = 125k patterns)
3. Heterogeneous (task + temporal) → SUPERADDITIVE at 3-5 seeds (cf-RPE x STDP; N-dependent)
4. Heterogeneous (sequence + sequence) → HP at trigram (position-binding + STDP)
5. **INPUT-REGIME-SPECIFICITY:** B3b + B6 single-stream SUBSUMED; mixed-stream SUPERADDITIVE
6. Efficiency same-axis-with-overlap → SUB-MULTIPLICATIVE (B3a x B3b = 16x)
7. **METRIC MUST MATCH AXIS:** capacity on M_crit; efficiency on wall-to-target; not BPC

---

## OPEN RESEARCH QUESTIONS

1. Does cf-RPE + STDP scale beyond N=512? (N=512 superadditive; N=8192 sub-additive)
2. Can gating rescue same-axis composition? (learned routing at intermediate layers)
3. Does intermediate layer-norm fix depth scaling? (composition_ceiling formula prediction)
4. Is cleanup chain-grade at INTERMEDIATE positions? (A1 tests only at end)
5. Can orthogonalization pre-processing rescue storage mechanisms? (sequential not joint application)

---

**Cell paths (actual Store locations):**
- /d/AI/hd-instrument/data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json
- /d/AI/hd-instrument/data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json
- /d/AI/hd-instrument/data/exp_q_a3_l100_cross_layer_composition_v1_n16384/metrics.json
- /d/AI/hd-instrument/data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json
- /d/AI/hd-instrument/data/exp_c_composition_storage_density_v1/metrics.json
- /d/AI/hd-instrument/notes/composition_matrix.md (11 rules)
