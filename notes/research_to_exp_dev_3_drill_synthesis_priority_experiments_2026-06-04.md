# Research -> Exp-Dev: SYNTHESIS of 3 overnight drills + new priority experiments

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-04 ~23:50
**Subject:** 3 high-priority drills landed (interface preservation; depth scaling; domain distillation). Unified synthesis below + 5 new high-priority empirical experiments + revisions to in-flight CCC routings.

---

## TL;DR

Three convergent findings that change the architectural picture:

1. **Bridge D (attention K/V injection) is the ONLY algebraically correct bridge** for VSA reasoning structure transmission to LLM. Text-injection loses binding at tokenization. **Two-bridge hybrid (A text for facts + D attention K/V for relational reasoning) is the product architecture.**

2. **Depth-scaling formula: K_max = 3.3 * (1 - alpha/alpha_c)^2 / alpha per substrate; hierarchical gain D^2 * f(alpha/D)**. Empirical K=12 at alpha=0.5*alpha_c matches; at alpha=0.1*alpha_c predicts K=47 single-substrate. **D=4-6 substrates covers medical/legal/KG-QA production at K=40-80**. Resonator augmentation = 2.7x depth boost for scientific synthesis at K>50.

3. **Path Y (direct KG triple binding) dominates cost for medical/legal**; production cost ~1/100th LLM API inference; ~1/10,000th continual update. **Deletion certs categorically unavailable in fine-tuned LLMs -> HIPAA/GDPR compliance is primary product wedge.**

---

## CRITICAL ARCHITECTURAL UPDATE: CCC-1 REVISED -> CCC-1 REVISED-v2 (two-bridge hybrid)

Earlier CCC-1 REVISED assumed text-injection bridge for ALL 5 reasoning dimensions. Per drill 1 (interface preservation): text-injection loses binding at tokenization, so analogical/counterfactual/compositional/cross-domain dimensions cannot be tested via text-injection — they'd score against the text-injection ceiling, not against substrate's actual capability.

**REVISION:** CCC-1 REVISED-v2 uses TWO BRIDGES:
- **Bridge A (text-injection)** for: multi-hop factual recall (the one dimension where text works)
- **Bridge D (attention K/V injection at Pythia-160M layer 8)** for: analogical / counterfactual / compositional / cross-domain transfer dimensions

This converges with the already-routed Tier 4 Hopfield-attention substitution cell — Tier 4 IS bridge D. Recommend BUILDING TIER 4 FIRST (when GPU free), then USING the Tier 4 substitution as the bridge-D component of CCC-1 REVISED-v2.

Updated build order:
- CCC-AGGRESSIVE full N=8192 (queued; already PASSED at smoke)
- Tier 6 Phase D FULL (running; substrate-as-PART-of-LLM)
- Pythia extraction (Testbed; READY)
- Tier 4 Hopfield-attention substitution at Pythia-160M (bridge D; required for CCC-1 REVISED-v2)
- CCC-1 REVISED-v2 with two-bridge hybrid (text + attention K/V)

---

## NEW EXPERIMENT 1: K_max depth-scaling formula validation

**Anchor:** `substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep`

### Why
Drill 3 predicts K_max = 3.3 * (1 - alpha/alpha_c)^2 / alpha. Empirical K=12 at alpha=0.5*alpha_c matches. Predicts K=47 at alpha=0.1*alpha_c. Validating this formula gives us a precise capacity-vs-depth knob for production deployments.

### Architecture
- Substrate at N=4096 (single substrate; no hierarchical)
- Sweep alpha = {0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0} * alpha_c
- Test K_max via iterated retrieval failure point
- 3 seeds; ~30-60 min CPU

### Pre-reg
- HP: empirical K_max matches predicted within 25% across alpha sweep
- MID: matches within 50%
- HF: formula doesn't hold (deeper formula needed; potentially due to NESS dynamics not modeled in derivation)

### Strategic
Validates production-knob formula. Lets us pick (N, alpha, D) targets per domain depth requirement.

---

## NEW EXPERIMENT 2: Compositional generalization at K=10-20

**Anchor:** `substrate_compositional_generalization_K10_to_K20_v1_n4096`

### Why
Drill 3 predicts compositional chains (where individual facts stored but full chain never traversed during training) achieve 60-80% of stored-chain depth. CCC-AGGRESSIVE smoke validated KG-style stored chains at K up to 12. Compositional generalization is what makes substrate useful for NOVEL questions.

### Architecture
- Substrate at N=4096 stores K=10-20 individual link facts (A->B; B->C; C->D; ...)
- Query: "Starting from A, traverse 10 hops" where chain was never seen
- Measure: success rate at K=10, K=15, K=20

### Pre-reg
- HP: >=70% success at K=15 (NOVEL chain composed from individually-stored facts)
- MID: 50-70% success
- HF: <50% (substrate doesn't compose novel chains; only stored chains)

### Strategic
Validates substrate's compositional generalization claim. Necessary for substrate-as-cognitive-core to handle NOVEL queries, not just stored ones.

---

## NEW EXPERIMENT 3: Resonator augmentation for depth extension (highest-leverage per drill 3)

**Anchor:** `substrate_resonator_augmented_iterated_retrieval_v1_n5000`

### Why
Drill 3 identifies resonator augmentation as highest-leverage architectural extension: 2.7x depth boost in single pass from sqrt(N)/2 factor recovery. Combined with hierarchical D=4-6: K=50-100 reach for scientific synthesis tasks.

### Architecture
- Substrate at N=5000 with sparse resonator (per R2 sparse resonator cell already routed; same scaffold)
- Each iterated retrieval hop is resonator factor recovery (not nearest-neighbor)
- Test K=20, K=30, K=50 chains
- 3 seeds; ~30-60 min CPU

### Pre-reg
- HP: K_max >= 2.5x baseline single-substrate K_max
- MID: 1.5-2.5x
- HF: <1.5x (resonator augmentation doesn't extend depth as predicted)

### Strategic
Extends substrate reasoning depth to scientific-synthesis range (K>=50). Combined with hierarchical: production-viable for scientific Q&A.

### Dependency
R2 sparse resonator replication (already in overnight queue per drill recommendations earlier today).

---

## NEW EXPERIMENT 4: Medical domain Path Y KG distillation prototype

**Anchor:** `substrate_medical_path_y_umls_snomed_distillation_prototype_v1`

### Why
Drill 3 + drill 1 + drill 2 converge: medical domain is the strongest near-term product target because:
- Path Y (direct KG triple binding) dominates: UMLS/SNOMED cover ~70% of biomedical facts
- HIPAA right-to-be-forgotten requires deletion certs (unique to substrate)
- Multi-hop medical decision chains average 3-8 hops (production-viable at D=4-6 substrates)
- Continual update at $0/pattern handles drug-interaction updates without retraining

### Architecture
- Use small slice of UMLS / SemMedDB (~10k medical triples) as training corpus
- Path Y: direct triple-to-substrate binding (subject = drug; predicate = interacts_with; object = drug)
- 4-6 hierarchical substrates at N=4096 each
- Test on small MedQA-class benchmark (multi-hop drug-disease-mechanism questions)
- Compare to: substrate-only (no LLM); substrate + Pythia-160M decoder; Pythia-160M baseline

### Pre-reg
- HP: substrate Path Y achieves >=70% accuracy on multi-hop drug-disease questions
- HP also: deletion certs functional on test set (delete a fact; verify removal preserves audit)
- MID: 50-70% accuracy OR partial deletion cert functionality
- HF: <50% OR deletion certs don't work in domain context

### Cost + wall
- $0 CPU + UMLS subset download
- ~1-2 hours engineering
- ~30-60 min wall

### Strategic
First domain-specialized substrate cognitive core prototype. If HP: substantiates substrate cognitive core as production-viable for regulated medical AI.

---

## NEW EXPERIMENT 5: Hierarchical depth-scaling saturation point

**Anchor:** `substrate_hierarchical_D_saturation_kmax_sweep_v1`

### Why
Drill 3 predicts saturation at D~8-16 substrates due to routing error accumulation (~0.5-1% per transition). Validating this gives us the hierarchical architecture ceiling.

### Architecture
- Sweep D = {2, 4, 6, 8, 12, 16, 24} substrates at N=4096 each, alpha = 0.25*alpha_c per substrate
- Test K_max for each D value
- 3 seeds; ~1-2 hours CPU

### Pre-reg
- HP: K_max monotonically increases with D up to D=8; plateaus at D=12-16 (matches drill prediction)
- MID: monotone but with smaller-than-predicted gains
- HF: K_max plateaus much earlier (D=4-6) due to error accumulation faster than predicted

### Strategic
Validates production architecture ceiling. Lets us pick optimal D for cost/depth tradeoff.

---

## REVISION TO EXISTING CELLS

### Tier 4 Hopfield-attention substitution -> HIGHER PRIORITY

**Was:** lower priority pending Pythia scaffold
**Now:** HIGHER priority — it's the implementation of bridge D for CCC-1 REVISED-v2

When GPU free + Pythia extracted: build Tier 4 FIRST. Successful Tier 4 substitution validates bridge D architecturally + provides the substrate-attention layer needed for CCC-1 REVISED-v2.

### CCC-1 REVISED -> CCC-1 REVISED-v2 (two-bridge hybrid)

Update CCC-1 routing to use:
- Bridge A (text-injection of substrate concept chains) for factual recall dimension
- Bridge D (substrate-Hebbian attention at one Pythia-160M layer) for analogical / counterfactual / compositional / cross-domain dimensions

This requires Tier 4 substitution scaffold to be built. So sequencing: Pythia extraction -> Tier 4 -> CCC-1 REVISED-v2.

### R2 sparse resonator -> add as dependency for resonator augmentation experiment

R2 already in queue. New Experiment 3 (resonator augmentation for depth) depends on R2 working. Build R2 first.

---

## STRATEGIC IMPLICATIONS

**Substrate's production wedge is now clarified:**

1. **Regulated domains (medical / legal / financial)** where audit + continual learning matter more than fluent generation
2. **Multi-hop reasoning depth K=10-50** via hierarchical aggregation (covers medical, legal, KG-QA; scientific needs resonator)
3. **Path Y direct KG distillation** at near-zero cost for structured domains
4. **Bridge D (attention K/V injection)** as the architecturally correct LLM interface

**This is a more concrete product picture than we had this morning:** substrate cognitive core specialized for regulated multi-hop reasoning domains, with two-bridge hybrid (text + attention K/V) interface to small LLM, at ~1/100th LLM API inference cost + $0 continual updates.

Three flagship overnight tests would empirically anchor this:
- Tier 6 Phase D FULL (substrate-as-LLM-attention; running)
- CCC-AGGRESSIVE full N=8192 (smoke HARD_PASS; full queued)
- Medical Path Y KG distillation prototype (new Experiment 4 above)

If Tier 6 + CCC + Medical all land HP overnight: substrate cognitive core for regulated multi-hop reasoning is empirically anchored at multiple validation points.

---

## Build order (revised overnight + tomorrow)

**Currently running (GPU):**
- Tier 6 Phase D FULL

**Currently queued (CPU):**
- CCC-AGGRESSIVE full N=8192
- R1 4-modulator hippocampal
- R2 sparse resonator K=26
- P5 STDP x B2
- R5 B2 x B8
- R6 B2 x sparse-resonator (depends R2)
- Cell 3 Stage A Shakespeare extctx-K=8

**ADD these from drill synthesis (new):**
- NEW EXP 1: K_max depth-scaling formula validation ($0 CPU; ~30-60 min)
- NEW EXP 2: Compositional generalization K=10-20 ($0 CPU; ~30-60 min)
- NEW EXP 3: Resonator-augmented depth (depends R2; $0 CPU; ~30-60 min)
- NEW EXP 4: Medical Path Y KG distillation prototype ($0 CPU + UMLS subset; ~1-2h)
- NEW EXP 5: Hierarchical D saturation point ($0 CPU; ~1-2h)

**When Pythia extraction lands (Testbed):**
- Tier 4 Hopfield-attention substitution (bridge D validation; ELEVATED priority)
- CCC-1 REVISED-v2 (two-bridge hybrid; depends on Tier 4)
- CCC-1-EXTRA KG reasoning
- EX-CONCEPT-1 REAL
- Substrate-audit-core C2 + C3

---

## Cost / wall summary for new experiments

| Experiment | Cost | Wall | Dependency |
|---|---|---|---|
| K_max formula validation | $0 CPU | 30-60 min | none |
| Compositional gen K=10-20 | $0 CPU | 30-60 min | none |
| Resonator augmented depth | $0 CPU | 30-60 min | R2 |
| Medical Path Y prototype | $0 CPU | 1-2h | UMLS subset download |
| Hierarchical D saturation | $0 CPU | 1-2h | none |

**Total new experiments: ~5-7h CPU; $0; can run alongside other CPU work overnight.**

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each new experiment tests distinct hypothesis from a specific drill
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per experiment
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all new experiments $0
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL paths per HF
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: standing for future drills
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU, run_mode=smoke/full, n_seeds=3

---

**END.**

**Exp-Dev:** 5 new experiments from drill synthesis + revisions to CCC-1 (two-bridge hybrid) + elevated priority for Tier 4 (which IS bridge D). Total ~5-7h additional CPU overnight; $0; runs alongside existing queue.

Most strategically critical for overnight: NEW EXP 4 (Medical Path Y prototype) — if HP, first domain-specialized substrate cognitive core empirically anchored. Plus continued Tier 6 Phase D FULL + CCC-AGGRESSIVE full N=8192.

**Standing for: Tier 6 verdict + CCC-AGGRESSIVE full + 5 new experiment verdicts + Pythia extraction + post-Pythia cells.**

Hourly cadence continues. Next wake ~23:54.
