# Research: Backburner ideas to revisit when we have something unequivocally valuable

**Filed by:** Research session
**Date:** 2026-06-05 ~18:30
**Context:** Per user 2026-06-05 ~18:00: "record all of these and revisit them later once we have something unequivocally valuable"
**Trigger:** 20-ambitious-ideas drill identified 12 ideas as PHASE-4 / PHASE-5 / BACKBURNER

---

## Purpose

These ideas were analyzed at 1x depth in the 20-ambitious-ideas drill (2026-06-05). Drill verdict for each was either:
- PURSUE-PHASE-4 (after HP-12 V1 demo lands; depends on infrastructure)
- BACKBURNER / PHASE-5 (depends on unsolved problems or major investments)
- NOT-WORTH (as stated; could revisit with different framing)

User wants them recorded but NOT actively pursued until we have shipped something categorically valuable (HP-12 V1 demo + Phase 4 TOP 5 validated).

---

## Phase 4 (after TOP 5 ships and HP-12 V1 demo lands)

### Idea 9: Personal substrate (on-device, privacy moat)
- N=4096-16384 fits in <400KB RAM
- Cert delete already validated
- Lit: MemGPT 2024; Chain of Awareness whitepaper 2025; on-device LLM trend
- **Revisit when:** HP-12 V1 demo + Phase 4 TOP 5 validate the commercial thesis; personal substrate becomes a natural consumer product extension
- Cost: ~30-40 days, $0 cloud
- Strategic value: HIGH for consumer market

### Idea 5: Substrate as external hippocampus (CLS analog)
- LLM = cortex; substrate = hippocampus
- Sleep cycles consolidate substrate -> LLM via distillation
- Lit: Hopfield-Fenchel-Young 2411.08590; ICLR 2025 AM workshop
- **Revisit when:** Idea 2 (working memory loop) validates the iterative substrate-LLM coupling pattern
- Cost: ~20-30 days, moderate cloud
- Strategic value: HIGH (foundational long-term architecture)

### Idea 11: Substrate as truth layer (fact-vs-fiction toggle)
- Cert verification + coverage check
- Adversarial substrate = second substrate instance
- Lit: Constitutional AI; EU AI Act + Akave 2024; attestable audits OpenReview 2025
- **Revisit when:** Idea 3 (hallucination detection) validates the per-token VQ grounding approach
- Cost: ~15-20 days
- Strategic value: HIGH for regulated AI

### Idea 13: Substrate as interpretability layer (activation storage)
- VQ compression of float32 activations is lossy
- Fidelity depends on compression ratio
- Lit: LRP4RAG 2408.15533; Anthropic circuits; activation patching
- **Revisit when:** Phase 4a encoder bottleneck infrastructure validates VQ quality at scale
- Cost: ~15-20 days
- Strategic value: MEDIUM-HIGH (solves major open AI problem)

### Idea 15: Substrate-native personal search (on-device, no server)
- Narrowed version of Idea 9
- Mathematical privacy (cert proves retrieval was local)
- Lit: MemoryOS; Chain of Awareness 2025
- **Revisit when:** Idea 9 personal substrate validates; this is a natural narrower use case
- Cost: ~20-30 days
- Strategic value: HIGH

### Idea 16: Adversarial substrate (multi-substrate red team)
- Three-substrate architecture
- Cert makes every decision auditable
- Lit: Constitutional AI; RLHF; EU AI Act compliance
- **Revisit when:** Phase 4 single-substrate scenarios validate; multi-substrate composition becomes the next step
- Cost: ~30-40 days
- Strategic value: HIGH

### Idea 7: Substrate-native program execution (VSA Lisp-machine)
- Turing-capable in principle (residue VSA per arxiv 2511.08767)
- Cleanup error limits recursion depth to K<=8 at N=4096
- Lit: VSA-Lisp arxiv 2511.08767; LARS-VSA 2405.14436
- **Revisit when:** Idea 1 (K-hop native reasoning) validates cleanup-error envelope; programs are extensions of reasoning chains
- Cost: ~10-15 days
- Strategic value: MEDIUM (advanced capability)

### Idea 19: Substrate-mediated LLM distillation (substrate goes autonomous)
- Works for factual retrieval; fails for generation + multi-step logical tasks
- Lit: Knowledge distillation lit
- **Revisit when:** Idea 8 (CoT cache with cert) validates pattern caching; distillation is the next step
- Cost: ~20-30 days
- Strategic value: MEDIUM

---

## Phase 5 / Backburner (depends on unsolved problems)

### Idea 6: LLM-to-LLM via shared substrate (concept-space comms)
- Shared codebook alignment across LLMs is unsolved
- User flagged: "this seems like something we could solve relatively easily"
- Lit: Multi-agent LLM lit; no direct VSA-mediated LLM-LLM paper
- **Revisit when:** Have a shipped substrate product to test the codebook-alignment hypothesis empirically
- Cost: ~25-35 days
- Strategic value: MEDIUM (could become HIGH if alignment is easy)
- **Note:** worth re-examining; user intuition suggests this is more tractable than drill flagged

### Idea 10: Federated civilization-scale substrates
- Cross-substrate codebook alignment is the open problem (same as Idea 6 at scale)
- Lit: Federated learning lit
- **Revisit when:** Idea 6 (LLM-to-LLM) validates codebook alignment; Phase 5 architecture
- Cost: ~100+ days
- Strategic value: HIGH (Phase 5)

### Idea 14: Substrate as world model for embodied agents
- Single-agent algebraically clean
- Multi-agent shares Idea 10's alignment problem
- Lit: Neural-symbolic world models; MemGPT 2024 agent memory
- **Revisit when:** Have a robotics/embodied partner OR Idea 10 federated alignment works
- Cost: ~20-30 days
- Strategic value: MEDIUM (could become HIGH with right partner)

### Idea 18: Substrate writes during LLM training (RETRO-style pretraining)
- Requires training-time architectural change
- Lit: RETRO (Borgeaud 2022); ATLAS; RAG (Lewis 2020)
- **Revisit when:** Phase 5 with much larger compute budget; substrate would augment frontier-scale pretraining
- Cost: ~50-100 days, $500-2000 cloud
- Strategic value: HIGH (long-term)

---

## NOT WORTH (as stated; might be revisited with different framing)

### Idea 12: Substrate-native mathematics (VSA theorem prover)
- FOL with nested quantifiers fails at cleanup depth > 3
- Lit: Smolensky 1990; Plate 1995; no successful VSA ATP in lit
- **Why NOT worth as stated:** algebraic limitations are fundamental for general theorem proving
- **Might revisit with different framing:**
  - Substrate-stored axioms + LLM-mediated proof search (NOT pure VSA proving)
  - Propositional-only theorem prover (no nested quantifiers)
  - Substrate as proof verifier (NOT prover); LLM proposes, substrate checks
- Cost: re-framing first; engineering 20+ days
- Strategic value: LOW as stated; could be HIGH with different framing

---

## User feedback to honor

Per user 2026-06-05 ~18:00:

> "Some I want to think more about — for instance, 'Shared codebook alignment across LLMs unsolved' this seems like something we could solve relatively easily. I think we should record all of these and revisit them later once we have something unequivocally valuable"

Action: This file IS that record. When HP-12 V1 demo ships + Phase 4 TOP 5 validates the commercial thesis, revisit this file. Decide which to promote to active development.

User specifically flagged Idea 6 (LLM-to-LLM concept-space comms) as potentially more tractable than drill assessed. Worth a dedicated revisit on the codebook-alignment problem when we're ready to attempt it.

---

## How to revisit (when ready)

1. Re-read this file + the 20-ambitious-ideas drill output
2. For each idea: check whether the dependency (other validated cell) has shipped
3. Re-assess strategic value given current state of the substrate-LLM product
4. Promote 1-3 ideas to active Phase 5 development
5. Update this file with revised assessments

---

## Discipline declarations

- Per user 2026-06-05 ~18:00: explicit "record + revisit later" methodology
- Per [[feedback-no-padding-experiments]]: not active routing; this is a strategic backlog
- Per [[feedback-substrate-value-framing-2026-05-26]]: focus on product-engineering work that ships; backlog the rest
- ASCII-only

---

**END.**

This file is the durable record. Will not be deleted; will be updated as backburnered ideas get revisited.
