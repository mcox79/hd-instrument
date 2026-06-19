# RESEARCH ROUTING — Empirical tier-coverage program (Tier 0.5 → Tier 5)

**From:** Research session
**To:** Testbed / Orchestrator / exp_dev / user (cost-envelope approval)
**Date:** 2026-06-03
**Trigger:** User explicit ask — deploy remote CPU + GPU resources to empirically understand implications + capabilities across ALL tiers where feasible (not just lit-scan / algebraic analysis).
**Discipline:** capability questions + pre-registered HARD/MIDDLE/HF bands per tier probe; cell-design parameters specified where ready (Phase A); pre-spec'd where awaiting drill (Phase B/C). Per-PROT compliance.

---

## 0. EXECUTIVE — what executes when

**3-phase coordinated empirical program across Tiers 0.5 → 4 (Tier 5 deferred):**

| Phase | Tiers | Probes | Gating | Cost ceiling | Engineering | Status |
|---|---|---|---|---|---|---|
| **A** (FIRE NOW) | 0.5 Y+ / 1 / Wave-5 | Phase 0.5 v2 Y+ + Tier 1 RAG-baseline + 3 CPU decisives | None — independent of in-flight drill | $30-55 cloud | ~3 eng-days | READY |
| **B** (post-drill + post-A) | 0.5b / 2 / 4-small | Phase 0.5b 9-cell + Tier 2 function-call SCOPED + Tier 4 Cluster B1 SMALL-SCALE | Tier 0.5 Y+ HP + in-flight drill verdict + user GO | $60-100 cloud | ~3-4 weeks | PRE-SPEC'D |
| **C** (post-B) | 3 / 5 | Tier 3 StepGame SCOPED + Tier 5 multi-agent SCOPED | Phase B success + user GO | $15-25 cloud | ~2-3 weeks | DEFERRED |

**Total program cost ceiling:** $105-180 cloud + ~7-9 weeks engineering (parallelizable). User authorization requested at each Phase B/C gate.

**Tier-by-tier capability claim mapping** (from prior strategic analysis):

| Tier | Probe validates | Substrate product claim strength |
|---|---|---|
| 0.5 (Y+) | Audit primitives on live LLM residuals | "Live LLM audit layer" |
| 0.5b | Distillation pathway + context-replacement | "Third memory type" (load-bearing) |
| 1 | Substrate as RAG backend vs FAISS | "Better RAG with audit" |
| 2 | 5-method API as LLM tool-calls | "Structured query primitive" |
| 4-small | Attention-layer substrate-replacement | "Native architectural integration" (strongest claim if HP) |
| 3 | Composite spatial reasoning | "Compositional reasoning primitive" |
| 5 | Multi-agent shared substrate | "Shared coordination primitive" |

---

## 1. PHASE A — IMMEDIATE EMPIRICAL DEPLOYMENT (fires NOW, no drill dependency)

### A1 — Phase 0.5 v2 Y+ (Tier 0.5 audit primitives on live LLM)

**Status:** spec LOCKED at `research_routing_v359_phase05_v2_FINAL_y_plus_2026-06-03.md`. Awaits orchestrator dispatch + SkyPilot fix.

**Cost:** $30-50 cloud (primary $26-32 + auto-extensions $0-15).

**Coverage:** Tier 0.5 audit-primitive validation (κ_3 + BBP drift / dual-primitive deletion / depth-defensive refusal cert).

### A2 — Tier 1 RAG-baseline probe (substrate vs FAISS on bAbI)

**Anchor name:** `tier1_rag_baseline_substrate_vs_faiss_v1_pythia410m`

**Capability question:** does substrate (as RAG backend) achieve equivalent or better accuracy + latency + cost vs FAISS dense-retrieval baseline on standardized RAG benchmark (bAbI tasks 17-20)?

**Architecture:**
- Base LLM: Pythia-410M (small; cheap; local-runnable on RTX-4060-Ti)
- Retrieval corpus: bAbI tasks 17-20 supporting facts (~2000 atomic facts)
- Baseline: FAISS HNSW index over BERT-embedded facts; top-5 retrieval; prompt-injection of retrieved chunks
- Substrate variant: encode facts as bipolar VSA bind(subject, predicate, object); Hebbian-write to substrate W (N=4096; α≈0.5); query via probe-and-retrieve top-5
- Both variants serve identical bAbI 17-20 test sets (200 questions per task)
- 5 seeds

**Pre-registered bands:**
- **HARD-PASS:** substrate accuracy ≥ 0.95 × FAISS accuracy AND substrate retrieval latency ≤ FAISS latency × 2 AND substrate audit primitive (deletion cert) works on the RAG-stored facts
- **MIDDLE:** accuracy ∈ [0.85, 0.95] × FAISS OR latency 2-5× FAISS
- **HARD-FAIL:** accuracy < 0.80 × FAISS OR latency > 5× FAISS

**Resource:** LOCAL GPU (RTX-4060-Ti) OR cheap cloud T4 instance (~$2-5)
**Wall:** ~4-6 hr (4 bAbI tasks × 5 seeds × 2 variants)
**Timeout:** 7200s per cell
**Cost:** $0-5
**Engineering:** ~2-3 days (FAISS baseline scaffolding + substrate-as-RAG wrapper + bAbI evaluator)
**P_deflated:** 0.65 (substrate stores Wikipedia-class facts cleanly; bAbI 17-20 are well-characterized small RAG benchmarks)

**Strategic significance:**
- HARD-PASS: substrate empirically validated as RAG-backend drop-in replacement; Tier 1 capability locked; substrate's audit primitives become differentiator vs FAISS
- HARD-FAIL: substrate has RAG-specific limitations; product-narrative scope narrows

### A3 — Wave-5 3 CPU decisive experiments (already queued)

**Anchors:** at Tier 1 priority in `notes/experiment_queue_pending.md`:
- `pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384` (CPU ~2h)
- `pp58_bbp_spectral_gap_calibration_v1_n16384` (GPU ~30 min local)
- `pp49_hrc_depth_parity_discriminator_sweep_v1_n4096` (CPU ~5 min)

**Cost:** $0 (CPU + local GPU)

**Coverage:** discriminates substrate-physics regime questions that inform Tier 0.5 / Phase 0.5b / Tier 4 design choices.

### Phase A sequencing

```
T-0 (NOW)
├── Wave-5 CPU experiments fire (~2 hr)
├── Testbed applies SkyPilot launch fix
└── Engineering: Tier 1 RAG-baseline scaffolding starts (~2-3 days)

T+2h (Wave-5 verdicts processed + SkyPilot validated)
├── Phase 0.5 v2 Y+ Lambda H100 launch (1-2 day wall)
└── Tier 1 RAG-baseline engineering continues

T+2-3 days
├── Y+ verdicts land
├── Tier 1 RAG-baseline launches (local GPU OR cheap T4)
└── In-flight context-interaction drill should have landed by now

T+3-5 days
├── Tier 1 verdict
├── Y+ extension dispatches (if any)
└── Phase B gates evaluated based on Y+ + Tier 1 + drill outputs
```

---

## 2. PHASE B — POST-DRILL + POST-Y+ EMPIRICAL DEPLOYMENT

### B1 — Tier 0.5b distillation MVP (9-cell spec)

**Status:** full spec LOCKED at `research_routing_v359_phase05b_distillation_mvp_full_spec_2026-06-03.md`. Awaits user GO + Y+ verdict.

**Cost:** $42-65 cloud + 1-2 weeks engineering.

**Coverage:** Tier 0.5b distillation pathway + context-awareness (sub-cells G/H/I).

**Drill dependency:** in-flight context-interaction drill informs sub-cells G/H/I architectural integration choices.

### B2 — Tier 2 function-call SCOPED probe

**Anchor name:** `tier2_function_call_substrate_5method_api_pythia410m_v1`

**Capability question:** can substrate's 5-method API (write, query, delete, audit, refuse) be exposed as LLM tool-calls, and does substrate-augmented LLM correctly invoke the right tool for the right task with audit-primitive composability?

**Architecture:**
- Base LLM: Pythia-410M with tool-call fine-tuning capability OR Llama-3.2-3B
- 5 substrate tools exposed: `substrate_write(s, p, o)`, `substrate_query(q)`, `substrate_delete(fact_id)`, `substrate_audit(check)`, `substrate_refuse_check(prompt)`
- Tool-call protocol: structured JSON in/out per Anthropic / OpenAI function-call spec
- Test corpus: 500 multi-step queries requiring tool composition (e.g., "store these facts then check if there's a contradiction then delete one")
- Substrate state: N=4096 single-bank
- 5 seeds

**Pre-registered bands:**
- **HARD-PASS:** tool-call accuracy ≥ 0.90 across 500 queries (LLM picks correct tool ≥ 90% of time); tool-composition accuracy ≥ 0.80 on multi-step queries; audit primitives correctly invoked when relevant
- **MIDDLE:** tool-call ∈ [0.70, 0.90] OR composition ∈ [0.60, 0.80]
- **HARD-FAIL:** tool-call < 0.70 (LLM cannot reliably use substrate tools)

**Resource:** Local GPU OR cheap cloud (~$5-10)
**Wall:** ~6-8 hr (500 queries × 5 seeds with tool-call latency)
**Timeout:** 14400s per cell
**Cost:** $5-15
**Engineering:** ~3-4 days (tool-call wrapping of substrate API + test corpus design + LLM fine-tuning if base model doesn't support tools natively)
**P_deflated:** 0.55 (Pythia-410M tool-call capability is limited; Llama-3.2-3B more reliable; small-scale probe risks)

### B3 — Tier 4 Cluster B1 SMALL-SCALE probe (Hebbian-augmented mini-transformer)

**Anchor name:** `tier4_cluster_b1_substrate_attention_swap_pythia160m_v1`

**Capability question:** can ONE attention layer in a small transformer (Pythia-160M or GPT-Neo-125M) be replaced with substrate query without destabilizing generation, AND does the substrate-augmented variant achieve training-cost speedup on knowledge addition vs LoRA?

**Architecture:**
- Base model: Pythia-160M OR GPT-Neo-125M (smallest reasonable; cheap fine-tuning)
- Substrate replaces ONE attention layer (mid-stack, layer ℓ=L/2)
- Substrate holds K/V; query is the residual; output is weighted retrieval
- Fine-tune on Wikitext-2 small corpus to validate generation doesn't destabilize
- Then add 100 new facts via (a) LoRA fine-tuning, (b) substrate Hebbian writes
- Measure: fact-recall accuracy, wall time, generation perplexity on held-out Wikitext-2

**Pre-registered bands:**
- **HARD-PASS:** substrate-augmented perplexity within ±5% of baseline AND substrate fact-addition ≥ 95% recall AND ≥ 1000× wall-time speedup vs LoRA at equivalent accuracy
- **MIDDLE:** perplexity ∈ [1.05, 1.10] × baseline OR recall ∈ [0.70, 0.95] OR speedup 10-1000×
- **HARD-FAIL:** perplexity > 1.10 × baseline (substrate destabilizes generation) OR recall < 0.70 OR speedup < 10× (no operational advantage)

**Resource:** Cloud T4 or RTX 4090 (~$10-20)
**Wall:** ~1-3 days engineering + ~24 hr compute (fine-tuning + fact-addition + perplexity eval)
**Timeout:** 86400s per cell
**Cost:** $5-20 cloud
**Engineering:** ~1-3 days (substrate-as-attention-layer wrapping + fine-tuning scaffolding + LoRA baseline)
**P_deflated:** 0.40-0.50 (Tier 4 architectural integration novel; small-scale risks; depends on which integration architecture from drill)

**Drill dependency:** in-flight drill's sub-question 1 (integration architecture choices) directly informs B3 design.

### Phase B sequencing

```
Post Phase A complete + drill landed + user GO
├── B1 Phase 0.5b 9-cell dispatch (extends Y+ H100 if running; else new bootstrap)
├── B2 Tier 2 function-call probe (parallel; local or cheap cloud)
└── B3 Tier 4 Cluster B1 probe (parallel; cheap cloud)

Wall: ~2-3 weeks
Cost: $60-100 cumulative
```

---

## 3. PHASE C — DEFERRED EMPIRICAL DEPLOYMENT

### C1 — Tier 3 StepGame composite probe

**Anchor name:** `tier3_stepgame_substrate_spatial_composite_v1`

**Capability question:** does substrate's spatial primitives (PP-47 hippocampal place-field + PP-49 HRC counterfactual) compose into LLM-coupled reasoning chains on StepGame spatial-reasoning benchmark?

**Cost:** $5-10 cloud + 7-10 eng-days
**Gating:** Phase B B1 + B2 success
**Status:** spec available in prior LLM-integration program routing; pre-spec'd

### C2 — Tier 5 multi-agent SCOPED probe

**Anchor name:** `tier5_multi_agent_shared_substrate_2agent_pythia410m_v1`

**Capability question:** can 2 LLM agents share a substrate as external coordination memory, with consistent state visible to both + audit primitives working across agent boundaries?

**Architecture:** 2× Pythia-410M with shared substrate; tool-call protocol per Tier 2; coordination test corpus (e.g., turn-taking dialogue with substrate as shared context)
**Cost:** $5-15 cloud + 5-7 eng-days
**Gating:** Phase B B2 success (Tier 2 infrastructure required); user GO
**Status:** PRE-SPEC'D minimally; full spec on Phase C authorization

---

## 4. TIER COVERAGE MATRIX

After Phase A + B + C complete (assuming all-HP), substrate has empirical validation across:

| Tier | Probe | Status post-program | Cap_map row impact |
|---|---|---|---|
| 0 | (existing 32+77 substrate-only rows) | Already comprehensive | Pre-existing |
| 0.5 | Phase 0.5 v2 Y+ | empirical | 3 NEW Tier-7 row candidates (N1/N2/N3) |
| 0.5b | Phase 0.5b 9-cell | empirical | 3 NEW context-replacement row candidates |
| 1 | Tier 1 RAG-baseline | empirical | NEW Tier-1 RAG-backend row |
| 2 | Tier 2 function-call | empirical | NEW Tier-2 structured-API row |
| 3 | Tier 3 StepGame | empirical | NEW Tier-3 spatial-composite row |
| 4 | Tier 4 Cluster B1 small-scale | empirical | NEW Tier-4 attention-replacement row (small-scale; full-scale Cluster C deferred) |
| 5 | Tier 5 multi-agent 2-agent | empirical | NEW Tier-5 multi-agent row |

**Net cap_map portfolio growth:** 32+77 → 32+87+ (10+ new rows across 5 tier-bands).

**Framework reliability impact:** product-feature reliability 86-98% → 90-99% projected (cross-tier validation reduces uncertainty on individual claims).

---

## 5. WHAT'S NOT IN THIS PROGRAM

- **Tier 4 full Cluster C** (Llama-3-8B substrate-augmented) — $50-300; deferred per prior `research_routing_tier4_training_acceleration_FINAL_5drill_consolidation` recommendation (Phase 0.5b is the strategic substitute for Tier 4-lite full)
- **Tier 5 production multi-agent** — beyond 2-agent scoped probe
- **Hardware-acceleration empirical** (memristor / RRAM) — fab-cycle gated; ~2029 timeline per Wave-2 oscillatory drill
- **Cross-LLM probe-of-probe transfer** (Hyperprobe Tier-7 follow-on) — gated on Phase 0.5 success

---

## 6. COST AUTHORIZATION REQUEST

**Phase A:** $30-55 cloud (Y+ + RAG-baseline + Wave-5; all under prior auth). NO new user auth needed.

**Phase B:** $60-100 cloud (0.5b + Tier 2 + Tier 4-small). **USER GO needed at Phase B gate** (post Phase A success + drill landing).

**Phase C:** $15-25 cloud (Tier 3 + Tier 5 scoped). **USER GO needed at Phase C gate** (post Phase B success).

**Total program cost ceiling:** $105-180 cloud across 7-9 weeks.

Each phase under standing per-case threshold individually; cumulative cost surfaces for explicit user approval at gates.

---

## 7. DRILL DEPENDENCIES

In-flight context-interaction deep dive (`research_drill_substrate_context_interaction_deep_dive_2026-06-03.md` when landed) informs:
- B1 sub-cells G/H/I architectural integration choices
- B2 Tier 2 tool-call protocol design (substrate API surface)
- B3 Tier 4 small-scale architectural integration (residual injection vs attention-layer replacement)

Possible second-drill (tier-comparison) informs:
- B3 Tier 4 vs B2 Tier 2 capability-claim differentiation
- Per-tier failure mode taxonomy
- C1/C2 Tier 3 / Tier 5 design refinement

Phase A is INDEPENDENT of drills — fires NOW.

---

## 8. INTEGRATION CHECKLIST

### Phase A (READY TO EXECUTE)

- [ ] Orchestrator dispatches Wave-5 CPU experiments (already at Tier 1; pull-trigger only)
- [ ] Testbed applies SkyPilot launch fix
- [ ] Phase 0.5 v2 Y+ dispatches per FINAL spec
- [ ] Testbed scaffolding for Tier 1 RAG-baseline (FAISS index + bAbI evaluator + substrate-as-RAG wrapper)
- [ ] Tier 1 dispatches (local GPU primary; cheap T4 fallback)
- [ ] Cost tracker monitoring $0-55 ceiling
- [ ] Status_log entries per phase milestone

### Phase B (AWAITING Phase A success + drill + user GO)

- [ ] Phase 0.5b 9-cell engineering scaffolding (extends Phase 0.5 v2 bring-up)
- [ ] Tier 2 function-call tool-wrap of substrate API
- [ ] Tier 4 attention-layer-swap engineering (small-scale)
- [ ] Phase B cost tracker $60-100 ceiling
- [ ] User auth at Phase B gate

### Phase C (AWAITING Phase B success + user GO)

- [ ] Tier 3 StepGame substrate-augmented engineering
- [ ] Tier 5 multi-agent coordination scaffolding
- [ ] Phase C cost tracker $15-25 ceiling

---

## 9. DISCIPLINE DECLARATIONS

- **Capability questions only;** HP/MIDDLE/HARD-FAIL bands pre-registered per probe.
- **Per `feedback_no_padding_experiments`:** every probe justified by tier-coverage gap (no empirical work currently exists at that tier).
- **Per `feedback_substrate_value_framing_2026-05-26`:** empirical tier-coverage IS the product-engineering work; appropriate weighting given 24-36mo substrate window.
- **Per `feedback_pipeline_pacing`:** Phase A maintains queue depth via 3 parallel probes; Phase B/C extend.
- **Per `feedback_obey_user_pause_explicitly`:** Phase A within prior auth envelope; Phase B/C require explicit user GO.
- **Per `feedback_batch_cloud_experiments`:** Phase B Tier 0.5b shares Lambda H100 with Y+ if instance running; Tier 2 + Tier 4-small can ride local GPU or shared cloud bootstrap.
- **Per `feedback_short_cloud_runs_preferred`:** each individual probe under threshold; cumulative cost surfaces for explicit auth.
- **Per `feedback_testbed_progress_logging_and_restart`:** per-cell partial JSON for restart capability across all probes.
- **PROT-018:** all anchor names use explicit tier-prefix + `_v1` family.
- **PROT-022:** per-tier P_deflated estimates + closed-form HP gates where derivable.

---

## 10. PHASE 0.5b vs TIER 4 SMALL-SCALE STRATEGIC TRADE-OFF

The two are EMPIRICAL ALTERNATIVES with overlapping product-claim coverage:

| | Phase 0.5b distillation MVP | Tier 4 Cluster B1 small-scale |
|---|---|---|
| Substrate role | External memory (write at distill; read at inference via residual injection) | Internal architectural component (replaces attention layer) |
| LLM scale | Llama-3.1-8B (production) | Pythia-160M / GPT-Neo-125M (research-scale) |
| Cost | $42-65 | $5-20 |
| Engineering | 1-2 weeks | 1-3 days |
| Product-claim strength | "Third memory type" (load-bearing) | "Native architectural integration" (deepest coupling) |
| Risk | Sub-cell G/H/I context-cost gates may fail under wrong architecture | Generation destabilization; small-scale ≠ production |
| Substrate primitives tested | All 6 + multi-bank | Hebbian write + retrieval at attention layer |

**Recommendation:** run BOTH in Phase B (not as alternatives). They test orthogonal product claims at different LLM scales. Phase 0.5b validates at production LLM scale; Tier 4 small-scale validates the architectural integration mechanism that would scale to Llama-3.1-8B in a later Cluster C if both Phase B probes HP.

---

**END.**

**Testbed:** Phase A executes per integration checklist (§8). Tier 1 RAG-baseline engineering can start in parallel with Phase 0.5 v2 Y+ bring-up.

**Orchestrator:** 
1. Pull-trigger Wave-5 CPU experiments NOW
2. Approve testbed Phase A launches (Y+ + Tier 1)
3. Hold Phase B routing pickup pending Y+ + drill outputs + user GO at Phase B gate
4. Hold Phase C routing pickup pending Phase B success + user GO at Phase C gate

**User:** Phase A within standing auth ($30-55, prior-approved). Phase B ($60-100) requires GO at gate after Phase A + drill; Phase C ($15-25) requires GO at gate after Phase B. Total program ceiling $105-180 + 7-9 weeks engineering.
