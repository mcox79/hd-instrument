# Research -> Exp-Dev: OVERNIGHT PRIORITY ITERATION (2026-06-04 ~23:00)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-04 ~23:00
**Subject:** User going to bed. Overnight priority iteration list. Build in priority order; cycle through; ship verdicts in batches. Continue 20-min cadence to status_log.

---

## TL;DR

Three flagship tests to land tonight (in priority order):

1. **Tier 6 Phase D full run** -- confirms or refutes substrate-intrinsic LLM training at 4-layer scale (smoke near-HP at 22:05)
2. **CCC-smoke REVISED** -- cheap architectural test of substrate-as-cognitive-core (analogical + counterfactual + transfer)
3. **CCC-1 REVISED** -- after Pythia extraction lands, smallest viable cognitive-core test at Pythia-160M tier with 5-dimension reasoning eval

Plus continuous backfill of bio-architectural primitives + composition cells.

---

## PRIORITY 1: GPU work (Tier 6 + Pythia + Tier 4)

### A. Tier 6 Phase D FULL RUN (highest priority; smoke already near-HP)

**Anchor:** `substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1`

- Configuration: D=256, T=64, 600 steps, 3 seeds (per smoke spec)
- Shakespeare char-LM corpus
- Substrate-Hebbian attention (vectorized causal-linear-attention) + bio-primitive stack + gradient output head
- Expected wall: ~3-4 hours GPU
- Pre-reg HP: BPC <= 1.20x baseline AND speedup >= 2.0x AND audit-during-training operational
- Smoke data: BPC 1.08x (PASS), speedup 1.98x (MIDDLE by a hair), audit operational
- Why important: confirms first empirical evidence for substrate-intrinsic LLM training at user-facing scale

### B. Pythia-160M residual extraction (Testbed action; queue at next cadence)

**Anchor:** `phase05_v1_pythia160m_residual_extract_v1`

- Testbed shipped READY script with TOKENIZERS_PARALLELISM=false (Llama v6/v7 fork-deadlock fix)
- 10k docs target; ~10-15 min wall expected
- HP at >=5000 residuals
- When npz lands -> unblocks CCC-1 REVISED + EX-CONCEPT-1 REAL + Tier 4 substitution

### C. Tier 4 Hopfield-attention substitution at Pythia-160M (when Pythia loaded)

**Anchor:** `substrate_tier4_hopfield_attention_substitution_pythia160m_4layer_v1`

- 500-step characterization of substrate-Hebbian attention at one Pythia-160M layer
- Pre-reg HP: entropy > 50% baseline + gradient ratio < 8x + ppl within 1.5x baseline
- ~30-60 min remote GPU OR ~$3-6 cloud H100
- 3 seeds

### D. Capacity scaling N=4096 / N=8192 (continuing run after v7 kill displacement)

- B2 x B4 x hierarchical full N=4096 + full N=8192
- Confirms multiplicative composition principle at higher dimensions
- ~few hours GPU each

---

## PRIORITY 2: CPU work (compositions + bio-architecture extensions)

### E. CCC-smoke REVISED ($0 CPU; ~15-20 min)

**Anchor:** `substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1`

Per `research_to_exp_dev_ccc_REVISED_relational_analogical_evaluation_2026-06-04.md`:

- Synthetic 5-domain hierarchical substrate at N=4096
- 4 sanity tests:
  - Basic pattern recall (>=80% HP)
  - Analogical completion (100 (A,R,B)(C,R,?) pairs; >=80% HP)
  - Counterfactual delta computation (100 "without X" queries; >=80% HP)
  - Cross-domain transfer (train on 4 domains; test on 5th; >=70% HP)
- HF: any of these <50%
- WHY-DRILL paths per cell in routing

### F. R1: 4-modulator hippocampal-tier rescue ($0 CPU; ~30-60 min)

**Anchor:** `substrate_4modulator_hippocampal_tier_rescue_v1_n4096`

Per `research_to_exp_dev_drill_recommended_experiments_audit_and_route_2026-06-04.md`:

- Extend cf-RPE single-modulator (DA analog) with 3 additional modulators (ACh, NA, 5HT analogs)
- Each gates writes independently; combined 4-modulator signal
- Pre-reg HP: >=1.5x performance vs single-modulator at substrate-class task
- Strategic: tests Tier 2 hippocampal-class transition (bio-scaling ladder)

### G. R2: Sparse resonator K=26 replication ($0 CPU; ~30-60 min)

**Anchor:** `substrate_sparse_resonator_replication_arxiv_2024_K26_v1_n5000`

- Replicate Frady-Sommer arXiv:2404.19126 sparse resonator at N=5000
- Sparse codebook f=0.02; K=26 factor recovery (alphabet)
- Pre-reg HP: >=85% accuracy within 50 iterations
- Strategic: extends substrate Mode 4 NC1 capacity beyond dense limit

### H. Cell 3: Stage A Shakespeare extctx-K=8 at N=8192 ($0 CPU + GPU mix; ~1-2 hours)

**Anchor:** `substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192`

Per `research_to_exp_dev_unblock_tier6_tier4_stageA_2026-06-04.md`:

- Full bio-primitive trick stack (B2 + position-binding + STDP + B6 + B4 + B3a + hierarchical)
- NO cf-RPE (drill: inverts for generative)
- Compare to Adam baseline on Shakespeare extctx-K=8 N=8192
- Pre-reg HP: >=3x wall-time speedup AND BPC within 20% of baseline
- WHY-DRILL on HF: substrate provides no training-speed advantage at this scale

### I. P5: STDP x B2 sequence composition ($0 CPU; ~15-20 min)

**Anchor:** `substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192`

Per Priority 1 compositions routing:

- Test if STDP-asymmetric sequence + B2 sparse-expansion compose multiplicatively
- IMPORTANT: P4 Position-binding x B2 HARD_FAIL today; this tests if STDP behaves differently
- Pre-reg HP: >=5x sequence-storage capacity vs dense+STDP at same N
- WHY-DRILL on HF: confirms NEW principle (sparsity is modality-specific; works for auto-assoc but not sequence)

### J. R5: B2 x B8 additive composition ($0 CPU; ~15-20 min)

- Tests D-RIP unification predicted ADDITIVE composition (same sparse axis)
- Pre-reg HP: combined capacity >=90% of additive prediction

### K. R6: B2 x sparse-resonator super-additive composition (depends on R2; $0 CPU; ~20-30 min)

- Tests D-RIP unification predicted SUPER-ADDITIVE composition (orthogonal sparse axes)
- Pre-reg HP: K_max >=1.5x best-single-primitive
- Strategic: empirical test of D-RIP framework's orthogonal-axis prediction

---

## PRIORITY 3: When Pythia extraction npz lands

### L. CCC-1 REVISED with 5-dimension reasoning eval ($10-30 cloud; ~6-10 hours)

**Anchor:** `substrate_cognitive_core_pythia160m_AGGRESSIVE_relational_eval_v1`

Per `research_to_exp_dev_ccc_REVISED_relational_analogical_evaluation_2026-06-04.md`:

- 5 evaluation dimensions:
  - 25% multi-hop factual recall (NQ multi-hop)
  - 25% **analogical reasoning (saturnMars/hyperprobe-dataset-analogy)** -- MOST DIAGNOSTIC
  - 15% counterfactual queries
  - 15% compositional generalization (novel-chain completion)
  - 20% cross-domain transfer
- Combined HP: avg accuracy >=50% AND substrate beats Pythia-160M on >=3 of 5 dimensions
- Strategic: THE smallest viable empirical test of substrate-as-cognitive-core

### M. CCC-1-EXTRA KG relational reasoning ($0 after Pythia extraction; ~30-60 min)

**Anchor:** `substrate_cognitive_core_pythia160m_KG_relational_v1`

- Wikidata subset (~50k triples) as training corpus
- Triple completion + multi-hop KG + analogical KG queries
- Substrate's natural strength (VSA bindings ARE KG triples)
- Strategic: most diagnostic for relational reasoning

### N. EX-CONCEPT-1 REAL ($0 after Pythia extraction; ~1-2 hours)

- VQ Pythia-160M activations (V=5000) -> concept IDs
- Substrate trains on concept-ID sequences with bio-primitive stack
- Compare to EX-CONCEPT-1 proxy V=5000 (MIDDLE today)
- Pre-reg HP: improves on proxy MIDDLE result

### O. Substrate-audit-core C2 + C3 at Pythia-160M ($0 after extraction; ~30-60 min)

- Substrate stores Pythia residuals
- C2 deletion cert algebraic test
- C3 drift detection kappa_3 test
- Tier-1 product anchor per hybrid C+D recovery plan

---

## PRIORITY 4: Lower-priority but worth running if CPU bandwidth

### P. CCC-2 substrate-only ceiling test ($0 CPU; ~20-30 min)

- Tests PATH B fundamental ceiling claim
- Substrate-only multi-hop on STRUCTURED Q&A (no language generation)
- Pre-reg HP: >=70% on structured queries

### Q. SQ4 Hebbian few-shot meta-learning ($0 CPU; ~30-60 min)

- Substrate W as meta-learner over few-shot tasks
- Pre-reg HP: >=2x acc vs random across novel tasks

### R. SQ7 two-substrate transfer ($0 CPU; ~30-60 min)

- Tests distributed intelligence: knowledge in substrate A queryable from substrate B
- Strategic: foundation for multi-substrate compositional systems

---

## NOT DOING (deferred per current priorities)

- Llama v8 (Testbed shipped diagnostic patch; user deferred until Pythia-first + substrate-intrinsic-LLM validated)
- C1/C2/C3 cornerstone at Llama-3.1-8B retry (deferred per hybrid C+D plan; 1B-scale validation first)
- Frontier-scale experiments (premature; need Pythia + Llama-3.2-1B tier validations first)

---

## Build order recommendation

**GPU lane (sequential):**
1. Tier 6 Phase D FULL (start NOW; ~3-4h)
2. Pythia extraction (Testbed queues; ~10-15 min when scheduled)
3. Tier 4 Pythia substitution (after Pythia loaded; ~30-60 min)
4. Capacity N=4096 / N=8192 (whenever GPU free; ~few hours each)
5. CCC-1 REVISED on cloud H100 (after Pythia extraction; ~6-10h)

**CPU lane (parallel; cycle through):**
1. CCC-smoke REVISED (~15-20 min; quickest architectural test)
2. R1 4-modulator (~30-60 min)
3. R2 sparse resonator K=26 (~30-60 min)
4. P5 STDP x B2 (~15-20 min)
5. R5 B2 x B8 (~15-20 min)
6. R6 B2 x sparse-resonator (after R2; ~20-30 min)
7. Cell 3 Stage A Shakespeare extctx-K=8 (~1-2h)
8. CCC-1-EXTRA KG (after Pythia extraction)
9. EX-CONCEPT-1 REAL (after Pythia extraction)
10. Substrate-audit-core C2 + C3 at Pythia-160M (after extraction)

**Lower priority backfill if bandwidth:**
- CCC-2 (~20-30 min)
- SQ4 meta-learning (~30-60 min)
- SQ7 two-substrate transfer (~30-60 min)

---

## Cadence + reporting

- Continue 20-min cadence to status_log
- Batch verdicts in research notes every ~30-60 min
- For LVH catches: surface immediately
- For HARD-FAIL on flagship tests (Tier 6 Phase D / CCC-1 REVISED): surface immediately
- For HARD-PASS on flagship tests: surface immediately + system protocol updates (scorecard / matrix)

---

## What gets us closer to user's strategic frame

User's frame (today): "substrate as cognitive core with small LLM as interface; reasoning + audit + continual learning as differentiators"

Highest signal cells:
- **Tier 6 Phase D FULL** (validates substrate-intrinsic LLM training at full scale)
- **CCC-smoke REVISED** (validates cognitive-core ARCHITECTURE at smallest scale; analogical / counterfactual / transfer)
- **CCC-1 REVISED** when Pythia lands (smallest viable EMPIRICAL test of substrate-as-cognitive-core at Pythia-160M tier with 5-dimension reasoning eval)
- **R1 4-modulator** (Tier 2 bio-scaling ladder transition)

If even 2-3 of these land HP overnight: substrate-as-cognitive-core architecture is empirically anchored.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Testbed + Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell tests distinct validated hypothesis
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF + WHY-DRILL paths per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: only CCC-1 REVISED + Tier 4 substitution need cloud; all else $0
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL paths included for all cells
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: standing protocol locked
- ASCII-only

---

**END.**

**Exp-Dev:** Overnight priority iteration. Build through CPU lane while GPU runs Tier 6 Phase D FULL. When Pythia extraction lands (Testbed): pivot CPU to EX-CONCEPT-1 + CCC-1-EXTRA + substrate-audit-core; pivot cloud to CCC-1 REVISED.

User is going to bed; expects substantive overnight progress. Surface flagship HARD-PASS / HARD-FAIL verdicts immediately to status_log.

**Standing for: Tier 6 Phase D FULL verdict; CCC-smoke REVISED verdict; R1 + R2 + R5 + R6 verdicts; Pythia extraction (Testbed) + CCC-1 REVISED build.**

**Research session:** standing on ~20-min cadence; will synthesize batches when verdicts arrive; will dispatch new drills only if compelling cap_map closure rescue or scope expansion warranted.
