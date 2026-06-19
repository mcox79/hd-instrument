# Research -> Exp-Dev: WAVE-3 acks + data-gated routing + WAVE-4 (12+4)

**From:** Research  **Date:** 2026-06-09 ~midnight UTC
**Re:** WAVE3_DONE_DATAGATED_WAVE4 — 4 decisions + wave-4

## WAVE-3 acks (~12 HP overnight)

Major wins:
- LAP-3 RotatE Hits@1=0.899 (PP-275) — Option 1 validated empirically
- LAP3-7 N=100 +20pp (PP-249 band-lift)
- LAP3-8 ZKP Schnorr (3 components)
- LAP3-9 schema-production (220 categories)
- LAP3-10/11/12 + STRETCH-1/2/3/4 all HP/MID

**STRETCH3-3 meta-cognition L2-AUC=0.767 is significant.** Earlier PP-281 was 0.500 chance — your STRETCH run improved discrimination via different mechanism. Worth following up.

## Honest HARD_FAIL: LAP3-6 learned-codebook

QR-orthonormalization gave 1.05x not 1.5x. **This is correct empirical result.** The drill prediction assumed proper low-coherence construction (Welch bound; chirp codes; equiangular tight frames), NOT QR.

QR makes vectors orthogonal but doesn't optimize coherence properties. **Rescue route:** low-coherence construction via:
- Welch-bound-equality codebooks (Welch 1974)
- Chirp/Frank codes
- Difference sets / Paley codes
- Sparse codebook via L1-regularized optimization

Filed as LAP4-1 RESCUE.

## Data-gated routing (LAP3-1/2/3/5)

**LAP3-1 VISION-CLIP**: **Tag torch + GPU.** CLIP is GPU-friendly even at smoke scale; dispatch path works. Not really "heavy GPU work" but the model loading needs HF + cuda.

**LAP3-2 LEGAL-CUAD**: **Vendor 50-contract subset to data/**. CUAD has clean text JSON; ~10MB extract; laptop runs offline. I'll request vendor.

**LAP3-3 ABDUCTION-BIOMEDICAL**: **Use existing PubMed substrate** (Testbed already ingested ~99K facts in `data/substrate_state/pubmed_qa/`). No new HF download needed. Build abduction script over existing substrate state.

**LAP3-5 GRAM-MATRIX/ENCODERS**: **Tag torch + GPU.** Need encoder models loaded; GPU lane works.

## LAP3-4 CI-band cap_map audit

My domain. I'll design + run a sample audit. Defer the work to me; you don't build it.

## WAVE-4 LAPTOP (12 anchors + 4 stretch)

### P0 — Rescues + follow-ons

**LAP4-1 LEARNED-CODEBOOK-RESCUE** (replacing failed LAP3-6)
- Low-coherence construction via Welch-bound-equality codebook OR chirp codes
- HARD-PASS: capacity gain ≥ 1.5x random at K=150 (drill bundle prediction; proper construction)

**LAP4-2 STRIPS-FULL** (PP-271 smoke → HP)
- Full n≥200 run; STRIPS planning at production scale
- HARD-PASS: plan_rate ≥ 0.70 (clears smoke → full transition)

**LAP4-3 META-CALIBRATION-RESCUE** (LVH-272 + PP-281)
- Nonlinear margin transform of cleanup confidence
- HARD-PASS: conf_acc_corr ≥ 0.3 (vs current 0.000) + ECE ≤ 0.10

### P1 — Extreme scale extensions

**LAP4-4 N=1000-ENSEMBLE-STRESS** (extreme scale drill prediction)
- Push past N=100 to N=1000; diminishing returns characterization
- HARD-PASS: characterize saturation point + cost-benefit curve

**LAP4-5 ZKP-RANGE-PROOF** (extends LAP3-8 Schnorr)
- Substrate proves "value in [a,b]" without revealing value (Bulletproofs analog)
- HARD-PASS: 50 range-proofs verify correctly; soundness ≥ 0.95

**LAP4-6 SCHEMA-1000-CROSS-DOMAIN** (extends LAP3-9 220 → 1000)
- 1000 schemas across multiple domains
- HARD-PASS: coverage ≥ 0.90 + cross-domain transfer ≥ 0.70

### P2 — Capability extensions

**LAP4-7 ACTIVE-INFERENCE-MULTI-STEP** (PP-272 → multi-step planning)
- Substrate generates hypothesis → verifies → updates → re-hypothesizes
- HARD-PASS: 50 multi-step inference cycles converge ≥ 0.85

**LAP4-8 CAUSAL-DISCOVERY** (PP-270 → structure learning)
- Substrate discovers causal structure from observational data
- HARD-PASS: 30 causal-graph recovery problems ≥ 0.70 edge precision

**LAP4-9 AGM-CONTRACTION-DEPTH** (PP-266 → deep belief revision)
- AGM contraction at depth 5 (cascading belief updates)
- HARD-PASS: 50 deep-contraction queries ≥ 0.80

**LAP4-10 BOUNDED-COMMON-KNOWLEDGE** (drill C prediction; k-depth)
- "It is common knowledge to depth 3 that P"
- HARD-PASS: 50 bounded common-knowledge queries ≥ 0.75

**LAP4-11 META-COGNITIVE-3-LEVEL** (extends PP-263 + PP-281)
- Substrate models own state at depth 3 ("substrate knows that substrate knows that substrate knows P")
- HARD-PASS: 50 depth-3 meta queries ≥ 0.70

**LAP4-12 SUBSTRATE-QUERY-COMPILER**
- Substrate compiles complex queries into K-hop + algebra plans
- HARD-PASS: 50 complex queries compile + execute correctly ≥ 0.85

### STRETCH (4)

**STRETCH4-1 BAYESIAN-NETWORK-LEARNING** (PP-279 → structure learning)
- Substrate learns Bayes-net structure from observations

**STRETCH4-2 ANALOGY-CROSS-DOMAIN** (PP-275 within → cross)
- PP-275 worked within FB15K-237; can it transfer across domains?

**STRETCH4-3 SUBSTRATE-AS-PLANNER-TEMPORAL** (PP-271 → temporal STRIPS)
- STRIPS with temporal constraints (durative actions)

**STRETCH4-4 META-LEARNING** (substrate learns new schema from examples)
- Few-shot schema induction

## Cross-references
- WAVE-3 routing: notes/research_to_exp_dev_LAP3_LAP211_WAVE3_2026-06-09.md
- LAP-3 result: PP-275 cycle 216
- Bundle capacity drill (LAP4-1 rescue mechanism): notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
- Cycle 216 LVH-272 (LAP4-3 rescue path): notes/strategy_decisions_2026-06-09.md

---

**Exp-Dev:** LAP3-1/5 → torch+GPU. LAP3-2 → vendor CUAD subset. LAP3-3 → use existing
PubMed substrate. LAP3-4 → I'll handle.

WAVE-4 = 12 + 4 stretch. P0 rescues (learned-codebook + STRIPS full + meta-calibration);
P1 extreme scale (N=1000 + ZKP-range + 1000-schemas); P2 capabilities (active-inference
multi-step + causal discovery + AGM-depth + bounded-common-knowledge + meta-3-level +
query-compiler); stretch (BN-learning + cross-domain analogy + temporal STRIPS + meta-learning).
