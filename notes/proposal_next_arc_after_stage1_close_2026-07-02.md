# Proposal — Next arc after Stage 1 close

**Filed:** 2026-07-02 evening (session-close proposal)
**Status:** menu for USER strategic direction after Stage 1 essentially closes + cortex integration debt closed today
**Motivation:** USER asked "are we finished with Stage 1?" — answer is essentially yes, with DAG topology probe still confirming. Once done, we're at a natural inflection point.

---

## Where we are

**Stage 1 physics essentially complete:**
- Storage-strategy law CG_META promoted to SCALE_FREE_PHYSICS_LAW tier (2 anchors verified)
- Composition-depth verified L=1 through L=20 (linear chains)
- If DAG probe FULL confirms, promotes to TOPOLOGY_FREE tier (3rd axis)
- Foundational primitives (bind/unbind/bundle/cleanup) all CG'd
- Noise robustness validated at cortex boundary (σ=0.05-0.15)

**Stage 2 optimization work already substantially done** across recent arcs (INT8/INT4-falsified/INT2 quantization; cross-axis β; cleanup-latency operating curve; GPU-batching discipline).

**Stage 3 cortex integration debt CLOSED today:**
- M1.3-M1.8 all extracted to hdlab modules
- Composed via `Cortex.forward()` pipeline
- End-to-end integration test bit-identical HP at 3 seeds
- Noise-boundary variant validated
- M1.6 attention router integration in flight (final coverage gap)

**Stage 4 (LM equivalence) infrastructure exists:**
- `lm_eval_harness.py` + `token_vocab.py` + `bigram_gap_measurement.py` shipped 2026-06-30 (df8511e82)
- Still DEFERRED per USER-locked stage progression

---

## 4 candidate next arcs

### Option A — Extend cortex with new primitives (M1.9+)

Cortex M1 stack is 6 primitives. What's missing for M3 conversational glass-box?

- **M1.9 Planning primitive** — hierarchical goal decomposition; substrate-native STRIPS proven this session (stretch4_3 + stretch2_3 v2 CGs). Natural next step.
- **M1.10 Analogy primitive** — cross-domain analogy is HARD (analogy #6 HF closure this session). Would need K-shot from trained embeddings or inductive bias per that finding.
- **M1.11 Meta-cognitive readout** — the confidence-signal work belongs here as a cortex primitive (per D-decision this session; substrate can't self-detect uncertainty, cortex reads out).

Cost: ~1-2 weeks per primitive. Load-bearing for M3 conversational eval.

### Option B — Begin substrate-native LM path (Stage 4 authorized)

VRC paradigm CG earlier this session opened substrate-native LM eval framework. Language-ingest infra is on disk. Cortex integration debt closed today means we have a runtime.

- Cell 2: NLP fact store via VRC paradigm at real corpus scale
- Cell 3: EAP (Extraction-Aggregation-Prediction) evaluation
- Cell 4: substrate vs LLM head-to-head on VRC metrics
- Cell 5: commercial-scale substrate LM

Cost: ~2-4 weeks (blocked on stage progression discipline — USER 2026-06-26 said Stage 4 DEFERRED until Stage 3 mature; today's cortex work makes Stage 3 more mature but "how mature is enough" is your call).

### Option C — M4 substrate-as-experiment-director

The substrate has cortex primitives + confidence signals (option C activity/energy MB partial) + planning primitives. Can it direct its own experiments?

Sonnet drill filed EVALUATE-OUTCOME primitive as CG-P=0.45. Would need:
- Substrate-native experiment representation
- Substrate-native outcome prediction
- Substrate-native experiment scheduling
- Human-in-loop USER approval gate

Cost: ~1-3 months. This is where the substrate starts recursively improving itself. High-risk, high-reward.

### Option D — Stage 1 topology extensions + capacity ceilings

DAG topology probe currently in flight. If HP, natural next tests:
- Cyclic graph topologies (out of scope for this arc; would need loop-detection mechanism)
- Higher-order rules (rules over rules; second-order composition)
- Correlated-key composition (extends Löwe's α_c(ρ)≈0.138(1-ρ²) to compositional retrieval)
- Capacity ceilings at N=32768+ with cloud GPU (once-per-stage final push per USER 2026-07-01)

Cost: ~1-2 weeks per probe. Extends the physics-law META further but Stage 1 is already essentially closed.

---

## Recommendation

**Sequenced: A → B, with C parallel-planned.**

1. **First: Option A** — author 2-3 more cortex primitives (M1.9 planning + M1.11 meta-cognitive readout at minimum). These directly leverage today's cortex integration + address gaps flagged this session.

2. **Then: Option B** — with a matured cortex, Stage 4 language work becomes more grounded. Cell 2 (NLP fact store via VRC) is the natural entry point.

3. **Parallel: Option C planning** — draft the M4 architecture proposal now (separately from spawning it), so when USER wants to reason about experiment-director capability, we have concrete design ready.

**Rejecting: Option D** as primary arc. Stage 1 is essentially closed; extending it further past today's SCALE_FREE + TOPOLOGY_FREE (pending) is deep-diving-into-a-solved-problem. Better to build ON the physics law than extend it further.

**Alternative recommendation (if USER wants ambitious):** parallel Options A + B — extend cortex WHILE starting language ingest. Requires more sub-agent bandwidth but session evidence today (spawn limit raised to 5 + full-auto works well) suggests we can handle it.

---

## Decision matrix

| Option | Cost | P_CG per cell | Strategic value | Risk |
|---|---|---|---|---|
| A (more cortex) | 1-2 wk/primitive | 0.55 | High — unblocks M3 eval | Low |
| B (Stage 4 language) | 2-4 wk | 0.35 | Very high — M3 endpoint | Med — stage progression tension |
| C (M4 director) | 1-3 mo | 0.20 | Existential — substrate recursion | High — long timeline |
| D (Stage 1 extension) | 1-2 wk/probe | 0.60 | Low — Stage 1 already closed | Very low |

USER's call. Full-auto ready to fire whichever direction (or sequence) is chosen.
