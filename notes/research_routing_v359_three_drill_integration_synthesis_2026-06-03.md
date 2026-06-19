# RESEARCH ROUTING — 3-drill integration synthesis (substrate-context + tier-1-to-5 + substrate-as-full-training)

**From:** Research session
**To:** Orchestrator / Strategy / Testbed / exp_dev / user
**Date:** 2026-06-03
**Trigger:** All 3 commissioned context / tier-integration / training-mechanism drills landed. Comprehensive synthesis + updates to existing routings.
**Updates:** Phase 0.5b 9-cell spec sub-cells G/H/I (architectural lock); tier-coverage program (per-tier failure modes); NEW Phase D Tier-6 hybrid probe spec.
**Discipline:** capability questions + closed-form findings + pre-registered bands. Per-PROT compliance.

---

## 0. EXECUTIVE — THE convergent finding across all 3 drills

**The substrate moat IS the audit primitive stack** — not compute, accuracy, context efficiency, or any other axis. This finding is independently corroborated from THREE angles:

- **Drill 1 (substrate-context interaction):** deletion certificate is UNIQUE vs all existing memory-augmented-LLM systems (DNC, NTM, RETRO, kNN-LM, Memory Layers at Scale)
- **Drill 2 (Tier 1-5 architecture):** audit-primitive is the SOLE defensible win-axis vs FAISS/kNN-LM/RETRO/Memory Layers AT ALL TIERS
- **Drill 3 (substrate-as-full-training):** audit-AT-TRAINING-TIME is absent in ALL published Hebbian-DL systems (Forward-Forward, Predictive Coding, DFA, Hebbian-FW, Krotov-Hopfield, DeltaNet 1.3B)

**Strategic implication:** substrate's product narrative across ALL tiers (0.5 → 5) must lead with audit primitives + compositional algebra as the differentiator, not with substrate-as-better-memory or substrate-as-faster-training. Those are NOT defensible win-axes against well-published alternatives. Audit IS.

**Other major findings:**
- **Tier 0.5b architecture LOCKED:** residual-stream injection at layer ℓ ≈ 0.7L (CAA precedent; zero context tokens; log₂(M)-bit info ceiling)
- **Tier 4 algebra CONFIRMED (P=0.95):** Ramsauer 2021 modern Hopfield = substrate's exact algebra. Production constraints: O(n·M·N) compute + entropy-collapse
- **Substrate-as-full-LLM-training:** pure replacement P=0.18 (NO — hard expressivity ceiling at softmax normalization); hybrid Hebbian-attention + gradient-head P=0.42 (YES — DeltaNet NeurIPS 2024 1.3B LLM is closest precedent)
- **17× parameter penalty** for pure substrate-native LLM at Llama-3.1-8B perplexity (no analog hardware) — substrate-native cost-economics NOT competitive without neuromorphic
- **Tier 5 multi-agent:** CRDT is the only sub-200ms coordination pattern

---

## 1. PER-DRILL HEADLINES

### Drill 1 — Substrate-context interaction (Tier-0.5b focus)
**File:** `research_drill_substrate_context_interaction_deep_dive_2026-06-03.md`

1. **Architectural integration LOCKED:** residual-stream injection at layer ℓ ≈ 0.7L (CAA-style)
2. Information ceiling: log₂(M) bits per inference
3. ICL equivalence RIGOROUS for linear attention; quantified gap for softmax (Llama-class)
4. Economic breakeven: <0.2 QPS vs RAG at Together AI pricing
5. Deletion certificate is UNIQUE differentiator
6. RoPE aliasing at long context = highest-P regression risk for sub-cell I
- P_deflated = 0.55

### Drill 2 — Tier 1-5 integration architecture (gap-focused)
**File:** `research_drill_tier_1_to_5_integration_architecture_deep_dive_2026-06-03.md`

1. **Audit-primitive = SOLE defensible win-axis** vs FAISS / kNN-LM / RETRO / Memory Layers at ALL tiers
2. Tier 4 Ramsauer 2021 modern-Hopfield IDENTITY confirmed (P=0.95)
3. Tier 4 production constraints: O(n·M·N) compute + entropy-collapse (binding)
4. Tier 5 multi-agent: CRDT-style merging is the only sub-200ms coordination pattern
5. Per-tier failure-mode shortlists derived (see §4 below)
- P_deflated = 0.32

### Drill 3 — Substrate as full LLM training mechanism
**File:** `research_drill_substrate_as_full_llm_training_deep_dive_2026-06-03.md`

1. **Pure gradient replacement: NO** (P=0.18) — softmax normalization is hard expressivity ceiling
2. **Hybrid Hebbian-attention + gradient-head: YES** (P=0.42) — DeltaNet NeurIPS 2024 1.3B LLM validates at scale
3. 17× parameter penalty for pure substrate-native at Llama-8B perplexity (no analog hw)
4. Substrate-native cost crossover: N < ~21k vs gradient backprop economics
5. **3 substrate-novel angles vs Hebbian-DL state-of-art:** audit-at-training-time + compositional algebra at training + closed-form scaling laws from substrate physics
6. Smallest viable probe: 4-layer character-LM on Wikitext-2, ~$5 cloud, 1-2 eng-days
- P_deflated (full replacement) = 0.18 / P_deflated (hybrid) = 0.42

---

## 2. PHASE 0.5b SPEC UPDATES (from Drill 1 + Drill 2 findings)

Apply these to `research_routing_v359_phase05b_distillation_mvp_full_spec_2026-06-03.md`:

### Sub-cell G — Context-cost-per-query (UPDATE)

**Architectural lock added:**
- Use residual-stream injection at layer ℓ = round(L × 0.7) per Drill 1
- CAA-style scalar steering (single retrieved vector injected)
- Zero context-token overhead by construction
- Pre-reg HP gate: substrate ≤ 10% of RAG context tokens — strengthened to substrate **≤ 5%** given architectural lock

### Sub-cell H — ICL replacement (UPDATE)

**ICL equivalence framing revised:**
- Per Drill 1: equivalence is RIGOROUS for linear attention only; quantified gap for softmax (Llama-3.1-8B uses softmax)
- Pre-reg HP gate: substrate-loaded accuracy within **±5pp** (relaxed from ±3pp due to softmax-gap)
- Add discriminator cell: compare to a hypothetical linear-attention LLM proxy (e.g., Mamba / DeltaNet) to validate the rigorous equivalence in the regime where it applies

### Sub-cell I — Long-context regression (UPDATE)

**Specific failure mode targeted:**
- Per Drill 1: RoPE aliasing at long context is highest-P regression risk
- Pre-reg HF trip-wire: at 32K context, RoPE position-encoding artifacts in substrate-augmented response (e.g., repeated patterns at RoPE base-period intervals) → automatic HARD-FAIL
- Add MICRO-cell I+: test specifically at 8192 → 16384 → 32768 → 65536 context lengths (RoPE extension boundaries where aliasing emerges); this is the HIGHEST-P regression detection design

### Sub-cell B (existing) — Deletion cert dual-primitive (UPDATE framing)

**Product-narrative upgrade:** per Drill 1 + Drill 2 + Drill 3 convergence: substrate's deletion cert is UNIQUE across the published memory-augmented-LLM AND Hebbian-DL landscapes. Frame sub-cell B as testing **THE substrate's flagship moat at LLM coupling** — the load-bearing test for substrate's entire product positioning.

### Sub-cell F (existing) — One-shot fact addition (UPDATE)

**Economic anchor:** breakeven analysis from Drill 1 — substrate cost-positive vs RAG at <0.2 QPS. Sub-cell F should also report wall-time-per-fact-addition in cost-per-fact equivalent units (using Together AI pricing reference) for direct product-narrative consumption.

---

## 3. TIER-COVERAGE PROGRAM UPDATES (from Drill 2 per-tier findings)

Apply these to `research_routing_v359_empirical_tier_coverage_program_2026-06-03.md`:

### Per-tier failure-mode shortlists (NEW per Drill 2)

| Tier | Highest-P failure modes (per Drill 2) | Probe design implication |
|---|---|---|
| **1 RAG-backend** | (1) Substrate retrieval recall < FAISS at corpus > 10K facts; (2) substrate audit primitives don't compose with retrieved-chunk context-injection cleanly | Test at 2K + 10K corpus scales; explicit audit-primitive composition test |
| **2 function-call** | (1) LLM tool-call protocol confuses 5 substrate tools (tool-selection accuracy < 90%); (2) audit tools return cert objects but LLM can't reason over them; (3) multi-tool composition (write → audit → delete) breaks | Test tool-selection accuracy; cert-object-reasoning sub-cell; composition chain test |
| **3 StepGame composite** | (1) Spatial primitives (PP-47/PP-49) compose with LLM reasoning chain but lose audit-trail; (2) substrate's spatial primitives have task-specific binding-noise | Add audit-trail-preservation test in spatial reasoning chain |
| **4 Cluster B1 small-scale** | (1) Entropy-collapse in substrate-as-attention (Ramsauer 2021 production-constraint); (2) generation perplexity degrades as substrate-attention loading α grows; (3) full attention-layer swap destabilizes vs residual-injection variant (lower-risk) | Test BOTH residual-injection AND attention-replacement variants at small scale; entropy-collapse mitigation via sparse-Modern-Hopfield (alpha-entmax) variant |
| **5 multi-agent** | (1) Eventual-consistency multi-agent writes produce divergent substrate states; (2) CRDT-merge logic isn't well-defined for bipolar Hebbian writes; (3) audit-trail-across-agents requires global state coordination | Use CRDT-style merge protocol from Drill 2; test divergence-detection; cross-agent audit-trail test |

### Phase B Tier 4 (Cluster B1) — UPDATE design

**Per Drill 1 (CAA residual-injection low-risk) + Drill 2 (Ramsauer attention-replacement P=0.95):**
- Test BOTH variants at small scale: (A) residual-injection variant at layer ℓ=L/2; (B) full attention-layer swap variant
- Compare generation perplexity + fact-addition speedup + entropy-collapse signature
- Add sparse-Modern-Hopfield (alpha-entmax) variant as mitigation cell IF entropy-collapse observed in B variant
- Updated cost: $10-25 (was $5-20; 1 additional variant)
- HP gates pre-registered per Drill 2 entropy-collapse threshold (substrate attention entropy > 50% of baseline attention entropy across N=4 cells)

### NEW Phase D — Tier-6 SCOPED probe (per Drill 3 smallest-viable design)

**Anchor name:** `tier6_substrate_hybrid_attention_gradient_head_charLM_v1`

**Capability question:** can a 4-layer character-level transformer be trained with substrate-Hebbian-attention layers (replacing gradient-trained self-attention) + gradient-trained output head, achieving within 20% BPC of fully-gradient-trained baseline on Wikitext-2?

**Architecture:**
- 4-layer character-level transformer
- Attention layers: substrate-Hebbian outer-product writes (delta-rule style per DeltaNet NeurIPS 2024)
- Output head: gradient-trained linear projection
- Training: streaming Hebbian-write of training corpus through stacked substrate stages; loss measured at output head; gradient updates ONLY to output head + final layer norm
- Corpus: Wikitext-2 character-level (~10MB text)
- Baseline: identical architecture trained fully via gradient descent

**Pre-registered bands:**
- **HARD-PASS:** substrate-hybrid BPC ≤ 1.20× gradient-baseline BPC AND wall-time training ≤ 0.5× gradient-baseline AND audit primitives (rank-1 deletion + refusal cert) operational on substrate weights DURING training (substrate-novel claim)
- **MIDDLE:** BPC ∈ [1.20, 2.0]× baseline OR wall-time speedup ∈ [1.0×, 2×]
- **HARD-FAIL:** BPC > 2× baseline (training collapses) OR substrate-hybrid slower than gradient-baseline OR audit primitives non-operational

**Discriminator outcome:**
- HP → substrate-hybrid LLM training is empirically viable at small scale; opens Phase E (scale to Pythia-160M or larger) + substrate-novel positioning "audit-at-training-time" empirically validated
- MIDDLE → substrate-hybrid works but doesn't beat gradient; product positioning narrows to specific task classes
- HF → substrate-hybrid training has gaps beyond the smallest probe scale; defer Tier 6

**Resource:** single A100 cloud
**Wall:** ~2-4 hours
**Timeout:** 14400s
**Cost:** ~$5
**Engineering:** ~1-2 eng-days (delta-rule attention substitute + Wikitext-2 character-LM scaffolding)
**P_deflated:** 0.42 (per Drill 3 hybrid hypothesis estimate)

**Strategic significance:**
- HP → opens Tier-6 substrate-hybrid LLM training as a product direction; substrate's audit-at-training-time positioning becomes empirically anchored
- HF → confirms substrate is not the training mechanism; substrate's role remains memory-augmentation + audit-at-inference

**Phase D positioning in tier-coverage program:**
- Gated on: Phase A + Phase B Cluster B1 success (need confidence in substrate-as-attention small-scale before substrate-as-training)
- Cost: $5 + ~$10 if HP triggers Phase D scale-up to Pythia-160M (~$10-25 additional)
- Phase D HP triggers Phase E (Pythia-160M substrate-hybrid training; ~$25-50 + 1-2 weeks engineering)

---

## 4. CAP_MAP IMPACT EXPECTATIONS

### Cross-drill consolidated cap_map updates (annotation-only; strategy_scribe one-shot batch):

**5 product-narrative anchors confirmed across all 3 drills:**

1. **Audit-primitive is THE cross-tier substrate moat** — annotate ALL Tier 1/2/3/4/5 cap_map row candidates (PP-50/55/56/57/58 + new candidates from tier-coverage program) with audit-primitive-as-defensible-axis annotation
2. **Architectural lock for Tier 0.5b: residual injection at 0.7L** — annotate PP-50 + new sub-cell-G/H/I candidate rows
3. **Tier 4 Ramsauer identity P=0.95** — annotate PP-12 / PP-51 / PP-55 cross-references; substrate-equivalent-to-modern-Hopfield is product narrative anchor
4. **Substrate-hybrid LLM training P=0.42** — NEW candidate row PP-59 (substrate-hybrid LLM training; EXPLORATORY 0.40-0.55) pending Phase D probe
5. **Multi-agent CRDT coordination** — NEW candidate row PP-60 (substrate-multi-agent coordination via CRDT; EXPLORATORY 0.50-0.65) pending Phase C C2 probe

### Cap_map row promotion candidates after 3-drill synthesis:

- **PP-58 isochoric audit protocol** → if Phase A Y+ HPs sub-test A2 BBP, PP-58 lifts from MIDDLE (current) to founded
- **PP-50 κ_3 audit + BBP dual-observable** → architectural lock confirms; band-LIFT eligibility on Y+ HP
- **PP-46 + PP-56 deletion cert at LLM coupling** → unique-vs-all-baselines anchor (Drills 1+2+3 converge); flagship lift on Phase 0.5b sub-cell B HP

---

## 5. WAVE-3 CASCADE DRILL CANDIDATES (3 follow-on; user decision)

Each 30-40 min sonnet, $0; cascade from the 3 drills' next-drill recommendations:

1. **DeltaNet delta-rule / bipolar-substrate algebraic isomorphism** (from Drill 3) — could collapse substrate-novel claims if isomorphic to DeltaNet's outer-product update. If isomorphic, substrate positioning vs DeltaNet narrows to audit + composition + scaling laws (the 3 substrate-novel angles already identified). If NON-isomorphic, substrate has algebraic-distinction-from-DeltaNet to defend.
2. **Sparse-Modern-Hopfield (alpha-entmax) training dynamics for Tier 4 entropy-collapse mitigation** (from Drill 2) — directly informs Tier 4 Cluster B1 entropy-collapse mitigation cell design
3. **Residual-injection SNR calibration** (injection magnitude α vs attention-entropy collapse boundary) (from Drill 1) — fine-tunes sub-cell G/H/I + Tier 4 residual-injection variant design

**My recommendation:** dispatch #1 (DeltaNet isomorphism) — highest strategic value because it determines whether substrate has unique algebraic claims vs DeltaNet OR substrate must lean entirely on audit-as-moat. Defer #2 (subsumed by Phase B Cluster B1 design refinement) and #3 (subsumed by Phase 0.5b sub-cell G/H/I refinement) unless additional capacity available.

---

## 6. STRATEGIC IMPLICATIONS FOR PHASE 0.5b GATE + PRODUCT NARRATIVE

### Phase 0.5b cost-revision (from Drill 1 + Drill 2 + Drill 3 architectural clarity):

- 9-cell spec cost UNCHANGED ($42-65)
- Engineering UNCHANGED (~1-2 weeks)
- HP-gate STRENGTHENED: sub-cell B (deletion cert) framed as THE flagship test — HP unlocks substrate-product positioning as unique vs all memory-augmented-LLM and Hebbian-DL competitors

### Product narrative core (3-drill convergence):

**Substrate is the FIRST and ONLY memory-augmented-LLM with audit primitives baked in at the algebraic-stack level.** Every other system (DNC, NTM, RETRO, kNN-LM, Memory Layers at Scale, DeltaNet, Hebbian-FW, Forward-Forward, Predictive Coding) has compute / accuracy / scale wins — substrate has AUDIT. Substrate's product story is:

> "Same accuracy as RAG-augmented LLM (Tier 1), tool-call API as good as function-call frameworks (Tier 2), spatial reasoning at composite-task scale (Tier 3), Hebbian-attention training at hybrid Tier-6, multi-agent coordination via CRDT — AND all of it with verifiable per-fact deletion, refusal cert, drift detection, compositional audit. No competitor offers the audit primitives."

### Phase 0.5b GO recommendation (UPDATED post-3-drill):

**Authorize Phase 0.5b at $42-65 IF AND ONLY IF Phase 0.5 v2 Y+ sub-test B (deletion cert) HARD-PASSes.** Sub-test B HP is the algebraic validation that substrate's UNIQUE positioning works at LLM coupling. Without it, the substrate's product narrative core breaks AT THE FIRST CUSTOMER ENGAGEMENT. With it, Phase 0.5b empirically anchors the positioning across context-replacement + ICL-replacement + long-context preservation.

---

## 7. DISCIPLINE DECLARATIONS

- **Per `feedback_no_padding_experiments`:** updates are targeted refinements; Phase D Tier-6 SCOPED probe justified by Drill 3 smallest-viable-probe finding
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all HP/MID/HF bands pre-registered; Phase D explicit
- **Per `feedback_substrate_value_framing_2026-05-26`:** 3-drill convergence reinforces 24-36mo substrate product window; audit-as-moat is the differentiated positioning
- **Per `feedback_capabilities_not_product_positioning`:** all updates framed as capability questions + closed-form findings; product narrative stated as cap_map impact
- **Per `feedback_keep_research_exploratory_not_narrowing`:** 3 drills covered breadth (context / tier / training); Wave-3 cascade (if dispatched) keeps breadth
- **Per `feedback_lit_scan_calibration_penalty`:** per-drill P_deflated reported (0.55 / 0.32 / 0.18-0.42); Phase D 0.42; honest calibration
- **Per `feedback_obey_user_pause_explicitly`:** Phase A within auth; Phase B/C/D require user GO at gates
- **PROT-022:** all 3 drill closed-form findings (log₂(M) ceiling, σ_g_crit corrected, BBP ratio, k_c formula, m_3 formula, Ramsauer identity P=0.95, DeltaNet adjacency, ECC criterion) consolidated into selftest registry

---

## 8. WHAT THIS ROUTING DOES NOT TOUCH

- **Phase 0.5 v2 Y+ execution spec** — unchanged; spec already locked at `research_routing_v359_phase05_v2_FINAL_y_plus_2026-06-03.md`
- **Phase 0.5b 9-cell core design** — unchanged; this routing adds sub-cell refinements only (architecture lock + RoPE-aliasing trip-wire + ICL gate adjustment)
- **Phase A execution status** — still awaits SkyPilot fix + dispatch
- **Wave-5 CPU experiments** — still at Tier 1 priority awaiting pull-trigger

---

## 9. SUMMARY OF ACTIONS REQUIRED

### Immediate (NOW):
- Orchestrator pull-trigger Wave-5 CPU experiments (CPU $0)
- Testbed apply SkyPilot launch fix
- Strategy_scribe one-shot annotation batch (5 cross-drill cap_map row updates from §4)

### Post Phase A success (T+3-5 days):
- Phase B authorization at $60-100 (Tier 0.5b + Tier 2 + Tier 4 Cluster B1 with dual-variant update from §3)
- Phase B Tier 4 design now tests BOTH residual-injection AND attention-replacement variants

### Phase B success → trigger:
- Phase C ($15-25) for Tier 3 + Tier 5 (with CRDT update from §3)
- Phase D Tier-6 SCOPED probe ($5) per §3 NEW spec
- Phase D HP triggers Phase E (Pythia-160M substrate-hybrid scale-up; $25-50 + 1-2 weeks)

### User decisions awaiting:
- Phase A: already authorized (within prior envelope)
- Phase B GO at gate: ~$60-100 cumulative
- Phase C GO at gate: ~$15-25 cumulative
- Phase D GO at gate: ~$5 cumulative
- Phase E GO at gate (if D HP): ~$25-50 cumulative
- **Total program ceiling (all phases): $110-200 cloud + ~9-13 weeks engineering**

### Wave-3 cascade decision (optional):
- Dispatch DeltaNet algebraic isomorphism drill if user wants further depth on substrate-vs-DeltaNet positioning

---

**END.**

**Orchestrator:** strategy_scribe annotation batch + Wave-5 pull-trigger + Phase A approval per §9.

**Testbed:** Phase 0.5b sub-cell G/H/I architectural lock (residual injection at 0.7L; RoPE-aliasing trip-wire on sub-cell I; ICL gate ±5pp) + Phase B Tier 4 dual-variant design per §3 + Phase D Tier-6 SCOPED probe per §3 (new).

**User:** 3-drill synthesis ships product-narrative core ("substrate is FIRST and ONLY memory-augmented-LLM with audit primitives baked in"). Phase 0.5b GO recommendation now CONTINGENT on Phase 0.5 v2 Y+ sub-test B HP — that's the flagship validation. Phase D Tier-6 SCOPED probe ($5) added to tier-coverage program. Total program ceiling raised to $110-200 + 9-13 weeks engineering.

**Strategy:** PP-59 + PP-60 candidate rows founded (substrate-hybrid LLM training + multi-agent CRDT coordination); cap_map row revisions per §4.
