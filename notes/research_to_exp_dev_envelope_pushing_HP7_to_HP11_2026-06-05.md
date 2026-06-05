# Research -> Exp-Dev: Envelope-pushing high-priority tests (HP-7 through HP-11)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~12:00
**Subject:** Phase 1.5 essentially complete (HP-1/2/3/4/6 + K2-XOR-1 all HP at Pythia tier). Five new envelope-pushing high-priority cells testing untested capability dimensions. Plus research drill directions identified.

---

## Strategic frame

Phase 1.5 backlog is empirically validated. The categorical-win story is mature. To push the envelope, we need cells testing capability dimensions we have NOT yet validated:

- Multi-modal binding (VSA's modality-agnostic property)
- Substrate-LLM integrated demo end-to-end at Pythia tier
- 10,000-scale memory (beyond current 1000-exchange validation)
- Adversarial / out-of-distribution evaluation (honest limits)
- Continual learning under distribution shift (harder than steady-stream HP-3)

All 5 cells run at Pythia tier; no Phase 2 gating; CPU-feasible; $0.

---

## Cell HP-7: Integrated substrate cognitive-core END-TO-END at Pythia tier

**Anchor:** `substrate_cognitive_core_e2e_pythia_v1`

### Why this matters

We have proven mechanisms (K2-XOR rescue, Mode 5 controller, substrate-MAX reasoning, introspection toolkit, audit certs). We have NOT yet built the integrated end-to-end pipeline. Until we run one Q&A query through the actual cognitive-core stack and see substrate -> bridge -> Pythia output with audit trail visible, the demo claim is unverified.

### Architecture

- Substrate: D=2 isolated substrates, N=4096, n=2 quadratic, K2-XOR context binding (rescue applied), Mode 5 controller (13-state FSM + 7-bit counter)
- Encoder: Pythia-160M
- Decoder: Pythia-160M (same)
- Bridge: Bridge 1 only (text-injection Format C reasoning chain markup with cert tokens)
- Test corpus: 5k facts from Wikipedia subset
- Test queries: 100 multi-hop Q&A drawn from corpus

### Pre-reg
- HP: end-to-end pipeline runs; outputs include audit cert chain; substrate-augmented accuracy >= 1.5x Pythia-raw baseline
- MID: pipeline runs; modest accuracy gain (1.1-1.5x)
- HF: pipeline crashes OR substrate output has no measurable effect on Pythia decoder

### Cost + wall
- $0 CPU
- ~1-2 hours wall (build + smoke test + run)
- 3 seeds

### Strategic

This is THE demo. Until we run this, the integrated story is theoretical. If HP: we have an end-to-end demo at Pythia tier that can be screen-recorded; user-facing pitch is concrete.

---

## Cell HP-8: 10,000-exchange conversation memory (10x scale push)

**Anchor:** `substrate_long_conversation_10k_exchanges_v1`

### Why this matters

HP-1 validated 1000-exchange categorical (substrate 1.00 at exchange 1000; Pythia 0.00). Push to 10k exchanges. This is the kind of demonstration where substrate's persistent memory becomes IMPOSSIBLE-LOOKING for an LLM.

### Architecture

- Synthetic conversation generator: 10,000 exchanges across 30 days (~333 per day)
- 10 distinct topic threads woven through
- 200 recall questions targeting depths 100, 500, 1000, 2000, 5000, 8000, 10000
- Substrate cognitive core vs Pythia-160M baseline (Pythia falls off at 2048 tokens)

### Pre-reg
- HP: substrate recall >= 0.80 at exchange 10000; Pythia 0.00 beyond 2048 tokens
- MID: substrate 0.50-0.80 (some degradation at extreme depths)
- HF: substrate fails at extreme scale (architectural concern beyond 5000 exchanges)

### Cost + wall
- $0 CPU
- ~6-8 hours wall (scale 10x of HP-1)
- 3 seeds

### Strategic

Categorical wins at 10x scale = unmistakable. Demo material for "ask about an exchange from 5000 turns ago" type pitches.

---

## Cell HP-9: Multi-modal substrate binding probe (VSA modality-agnostic test)

**Anchor:** `substrate_multimodal_binding_text_kg_v1`

### Why this matters

VSA is algebraically modality-agnostic (any modality embedded into bipolar space can bind). We have NOT validated this empirically. If substrate can do cross-modal queries (e.g., "find KG triples that align with this text passage"), that's a unique capability LLMs cannot easily replicate.

### Architecture

- Substrate: N=4096, K=2 XOR binding
- Modality A: text passages (Pythia mean-pool embeddings, then VQ to bipolar)
- Modality B: KG triples (random bipolar; structured by relation type)
- Cross-modal queries: text query -> retrieve aligned KG triples; KG triple query -> retrieve aligned text passages

### Pre-reg
- HP: cross-modal retrieval accuracy >= 0.50 at top-5 (substantially above random); within-modal >= 0.80
- MID: 0.30-0.50 cross-modal
- HF: cross-modal retrieval is near-random (modality gap problem; VSA modality-agnostic claim weak)

### Cost + wall
- $0 CPU
- ~2-3 hours wall
- 3 seeds

### Strategic

Tests VSA's foundational modality-agnostic property. If HP: substrate gains a NEW categorical capability dimension (cross-modal grounding). If HF: substrate is modality-bounded in practice (still works within a modality; cross-modal needs alignment work).

---

## Cell HP-10: Adversarial substrate evaluation (honest limits)

**Anchor:** `substrate_adversarial_failure_modes_v1`

### Why this matters

We have focused on categorical wins. We have NOT systematically probed where substrate FAILS. Honest evaluation of failure modes is required for regulated-AI deployment (medical, legal, financial pitch all require "what happens in adversarial conditions").

### Architecture

Test substrate's behavior on:
- A. Contradictory facts (substrate stores X=A; then stores X=B; queries return what?)
- B. Polysemous queries (same concept-ID maps to different meanings in different contexts)
- C. Cascading deletion (delete fact -> verify downstream multi-hop reasoning paths break appropriately)
- D. Adversarial concept-IDs (similar but distinct entities; how often does substrate confuse them?)
- E. Out-of-distribution queries (query for concept that was never stored)
- F. Storage overflow (write past M_max; observe degradation mode)

### Pre-reg
- HP: substrate handles each failure mode predictably (contradictions return latest; OOD returns LOW-CONFIDENCE; overflow degrades gracefully)
- MID: substrate handles some modes well, others poorly
- HF: substrate has catastrophic failure modes (silent corruption, undetected wrong answers)

### Cost + wall
- $0 CPU
- ~1 day wall (6 failure modes)
- 3 seeds each

### Strategic

This is THE honest-limits cell. Identifies where substrate is unsafe to deploy. Required for medical/legal/financial pitches. May surface new architectural extensions needed.

---

## Cell HP-11: Continual learning under DISTRIBUTION SHIFT (harder than HP-3)

**Anchor:** `substrate_continual_learning_distshift_v1`

### Why this matters

HP-3 validated continual learning over 30 days with same-distribution stream. Real deployment has DISTRIBUTION SHIFT: medical guidelines change; legal precedents update; financial regulations evolve. Test substrate under realistic shift.

### Architecture

- Day 1-15: stream A (e.g., medical guidelines pre-2024)
- Day 16-30: stream B (different distribution; e.g., revised guidelines post-2024 with contradictions)
- Query mix:
  - Old-but-still-valid facts (overlap of A and B)
  - Outdated facts (in A but contradicted by B)
  - New facts (only in B)
- Substrate behavior tested: (a) retrieve current state; (b) audit-trace which version is stored; (c) delete-and-replace for contradictions

### Pre-reg
- HP: substrate handles shift gracefully (newer facts override older; audit trail shows version transitions; no silent contradictions)
- MID: substrate handles some shift well, has issues with edge cases
- HF: substrate silently retains contradictions (catastrophic for regulated deployment)

### Cost + wall
- $0 CPU
- ~1 day wall
- 3 seeds

### Strategic

Push HP-3 to realistic deployment scenario. If HP: substrate's continual learning + audit trail handles real-world distribution shift. If HF: identify what extensions are needed (versioned writes; explicit deprecation flags; audit-driven query routing).

---

## Sequencing recommendation

**Highest strategic priority (do first):**

1. **HP-7** (integrated end-to-end demo): until we run this, the integrated story is theoretical. ~1-2 hours wall. THIS IS THE DEMO.

2. **HP-10** (adversarial failure modes): honest limits required for regulated-AI pitch. ~1 day wall.

3. **HP-9** (multi-modal binding): tests VSA's foundational property; potential NEW categorical capability. ~2-3 hours wall.

**Second priority:**

4. **HP-11** (distribution shift): pushes HP-3 to harder scenario. ~1 day wall.

5. **HP-8** (10k-exchange scale): impressive demo material but not architectural. ~6-8 hours wall.

---

## Plus 2 research drills warranted

### Drill A: Why did theta-burst + cerebellar empirically fail?

We have HF on two novel write architectures with strong algebraic backing. Brief honest root-cause drill needed: what was the bipolar implementation gap? Worth knowing for future architectural research.

Privacy-locked dispatch: generic math framing; no internal anchor names; no specific empirical results.

### Drill B: Substrate evidence integration when retrieval returns K facts (algebraic underexplored)

When substrate retrieves K facts for a multi-hop query, how should they be COMBINED for downstream reasoning? Current default is concatenate-text-into-prompt. Other options: Bayesian fusion, vote, logical AND, weighted sum by confidence. This is an algebraic question with concrete impact on end-to-end accuracy.

Privacy-locked dispatch: generic math framing.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: 5 cells test distinct capability dimensions not yet validated
- Per [[feedback-pressure-test-negative-findings]]: HP-10 systematically probes failure modes
- Per stay-at-Pythia methodology: all cells at Pythia tier; $0 cost
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU; n_seeds=3

---

**END.**

**Exp-Dev:** 5 envelope-pushing cells. HP-7 is THE demo (~1-2 hours wall). HP-10 is honest-limits (~1 day). HP-9 tests new capability dimension (~2-3 hours). HP-11 + HP-8 are second-priority. All at Pythia tier; $0; CPU-feasible.

**Testbed:** no change to actions in flight (HP-5 data + Llama/Gemma extraction).

**User:** Phase 1.5 confirmed complete; K2-XOR rescue HP; theta-burst + cerebellar HF. 5 envelope-pushing cells routed: integrated end-to-end demo, 10k-scale memory, multi-modal binding, adversarial limits, distribution-shift continual learning. Plus 2 research drills to dispatch (failure root-cause analysis + evidence integration algebra).
