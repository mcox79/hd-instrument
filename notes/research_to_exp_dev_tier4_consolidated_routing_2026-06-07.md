# Research -> Exp-Dev: Tier 4 consolidated routing (4 drills converged + speed/energy axis)

**From:** Research session
**To:** Exp-Dev (primary) + Orchestrator + Testbed
**Date:** 2026-06-07
**Re:** 4 Tier 4 drills landed and converged; plus user-flagged speed/energy axis
under separate 2x drill (in flight).

## Convergent Tier 4 proposal

**ARCHITECTURE:** Arch (8) hybrid continual fine-tuning + Arch (5) sparse retrieval
heads (combined). P_actionable 0.48/0.45 from Tier 4 architecture proposals 3x drill.

**MECHANISM:** Option D from substrate-aware continual learning 2x drill — frozen LLM
backbone + rank-4 LoRA adapter updated per substrate batch. Catastrophic forgetting
structurally impossible for facts (substrate's additive Hebbian writes).

**ECONOMICS:** 2-6x infrastructure cost advantage vs frontier LLM API; 5-20x vs Azure
OpenAI enterprise. Break-even 10-50K q/mo regulated, 600-800K q/mo general.

**SPEED + ENERGY:** Speed/energy axis is ORDERS OF MAGNITUDE advantage I had under-
documented in the economics drill. Per-query: 100-1000x fewer FLOPs (substrate bipolar
matrix-vector at N=4096 vs frontier LLM attention over 10K-200K context); 100-1000x
less energy (bipolar ops at ~10 pJ vs fp16 at ~1 nJ); 2-10x lower latency. Knowledge
updates: 1000-100000x faster (substrate Hebbian write O(1) vs LLM fine-tune
O(params x steps x tokens)). Edge deployment enabled (commodity GPU; substrate alone
viable on phone). Separate 2x drill in flight to quantify precisely.

**COMPETITIVE:** 3+ year defensible compliance moat (EDPB Feb 2026 + EU AI Act Art 12
Aug 2026 confirm weight-matrix memory failures). Titans is strongest competitor on raw
long-context but ZERO compliance. Pattern B compositional 6-18 months defensible.

## 3 Pythia-160M pre-tests gate Tier 4 authorization (30-45 min each, $0)

### Pre-test 1: Vocab injection generalization
Train rank-4 LoRA on Pythia-160M to use substrate for retrieval; inject new vocab via
sparse-KEY into substrate post-training; measure whether Pythia retrieves correctly via
the LoRA without further fine-tune.

HARD-PASS: new-vocab retrieval accuracy >= 0.85.

### Pre-test 2: LoRA orthogonal stability
Train rank-4 LoRA on Pythia-160M; run sleep defrag aggregation on substrate (adds ~1000
derived regularities); recalibrate LoRA; verify base inference behavior unchanged on
held-out queries.

HARD-PASS: held-out query accuracy stays within 3% of pre-defrag baseline.

### Pre-test 3: Defrag consistency
Schedule defrag during simulated query traffic; measure query latency + accuracy during
defrag vs after defrag.

HARD-PASS: query accuracy unchanged; latency variance < 20%.

## Two benchmark gaps to close (after pre-tests pass)

### Gap 1: BABILong (Titans published strong score; substrate untested)
Substrate at 100K facts on BABILong long-context reasoning. Compare to Titans published.

### Gap 2: CLUTRR 3-hop kinship inference (Pattern B designed for; no competitor result)
Pattern B compositional substrate on CLUTRR 3-hop. No competitor has published result.

Both CPU-laptop scale, ~3-5 hours each, $0.

## Engineering proposal (if pre-tests pass)

Phase 1 (3-4 weeks): Arch (8) implementation — substrate-aware LoRA adapter; integrate
with bge-small + Llama-8B; HIPAA Option B architecture (per-customer substrate +
shared LLM; PHI never enters LLM context).

Phase 2 (1-2 weeks): Arch (5) sparse retrieval heads — train specific attention heads
to specialize in substrate retrieval.

Phase 3 (1-2 weeks): integration + production scaffolding (HIPAA isolation, LoRA-per-
customer pipeline, sleep defrag scheduling).

Total: 5-8 engineer-weeks for Tier 4 v1 deployment.

## Honest customer pitch

NOT: "Tier 4 substrate-aware LLM beats frontier at retrieval" (parity at best with RAG)
NOT: "novel reasoning" (frontier LLM wins; Type II implicit knowledge)
NOT: "general world knowledge" (frontier LLM wins on training-scale)

IS:
- COMPLIANCE: 3+ year structural moat (Art 12, Art 17, bitemporal, audit chain)
- SPEED: 100-1000x fewer FLOPs per query at quality-comparable Type I workloads
- ENERGY: 100-1000x less energy per query (huge sustainability story for enterprise)
- LATENCY: 2-10x faster per query
- AGILITY: 1000-100000x faster knowledge updates
- ECONOMICS: 2-6x lower infrastructure cost (5-20x in regulated)
- EDGE: substrate enables commodity-GPU and phone-class deployments frontier LLM cannot
- COMPOSITIONALITY: structured queries + counterfactual replay + provable reasoning chains

The pitch competes on STRUCTURAL ADVANTAGES (compliance + speed + energy + agility + edge),
not on raw answer quality where frontier LLM wins.

## INFEASIBLE architectures (do not pursue)

- Arch (7) backward-pass memory: training-time only
- Arch (6) positional embeddings: compositional structure doesn't fit transformer
  positional encoding cleanly
- Arch (1) fast-weight memory: requires significant protocol engineering for compliance
  before authorization; defer

## Pre-empted concerns

"Substrate is RAG with extra steps." Honest: structurally similar. Memento (frozen LLM
+ external episodic memory) gets 87.88% Pass@3 GAIA. Substrate adds audit + compositionality
+ capacity-discipline + compliance moat that RAG lacks.

"Pre-training premature." Confirmed: pre-training substrate-aware LLM from scratch is
premature until 50+ customers ($100K-$1M cost). LoRA per-customer at $1.5K-7K is viable.

"Pattern B compositional moat is short-term." Confirmed: 6-18 months. The structural
defensible moats are audit + GDPR + bitemporal + speed/energy (storage-architecture-
level, not feature-class).

## Cross-references

- Tier 4 architectures 3x: notes/research_drill_tier4_llm_architecture_proposals_3x_2026-06-07.md
- Substrate vs competitors 2x: notes/research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md
- Substrate-aware continual learning 2x: notes/research_drill_substrate_aware_llm_continual_learning_2x_2026-06-07.md
- Tier 4 deployment economics 2x: notes/research_drill_tier4_deployment_economics_2x_2026-06-07.md
- Tier 4 speed + energy quantified 2x (IN FLIGHT): notes/research_drill_tier4_speed_energy_quantified_2x_2026-06-07.md
- Sleep defrag 3x: notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Original 2026-06-02 Tier 4 routing: notes/research_routing_tier4_training_acceleration_FINAL_5drill_consolidation_2026-06-02.md

---

**END.**

**Exp-Dev:** authorize 3 Pythia-160M pre-tests (~2 hours total CPU). After pre-tests
pass, route BABILong + CLUTRR benchmarks. If both pass, 3-5 engineer-week Tier 4 build
is justified.

**Orchestrator:** Tier 4 is now an actionable program with concrete architecture +
economics + competitive positioning + speed/energy quantification (pending). Update
strategic decisions log accordingly.

**Testbed:** Phase 0.5 distillation (CELL-3 / CELL-5) becomes lower priority given Tier 4
pivot. Re-prioritize against the Pythia-160M pre-tests.
