# RESEARCH ROUTING — LLM-integration program (consolidation + scheduling authorization)

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev / testbed
**Date:** 2026-06-02
**Trigger:** User explicit ask — surface Drill A/B PP-47 findings + Phase 0 routing back to strategy + auth orchestrator for experiment scheduling on the LLM-integration program; do research where necessary.
**Strategic context:** v334 cap_map at portfolio 32+71, HONEST 412, LABEL-VS-HONEST 201 (clean). Substrate's product narrative is empirically anchored across 4 dimensions at production N=32768 (audit-layer / composition+reasoning / safety+alignment primitives PP-48+PP-49 / streaming+real-time). The unresolved strategic gap is that ALL substrate confirmations to date are SUBSTRATE-ONLY tests — no LLM-integration testbed has fired.

---

## 0. EXECUTIVE — WHAT THIS ROUTING DOES

1. **Surfaces PP-47 Drill A finding to strategy** — the 0.879 Spearman ρ at v333 is ~100% encoding-kernel property, NOT Hopfield-retrieval property. Substrate's real spatial-coding contribution is the composition of place-field codes with substrate-novel primitives (PP-9 deletion + PP-48 NKT + PP-49 HRC + PP-46 GDPR cert). The Tier-6 LLM-integration testbed (StepGame flagship) must test these compositions, not just accuracy.

2. **Provides authorization to orchestrator for experiment scheduling** on a 4-phase LLM-integration program. Each phase has explicit HARD/MIDDLE/FAIL bands; each phase gates the next; total cost ~3-4 weeks engineering + ~$10-18 cloud.

3. **Adds 2 PP-48/PP-49 × PP-47 composition tests** to the Phase 0 substrate-only pre-checks (extending strategy's v334 priority #2 "PP-48 cross-application probe to PP-9/PP-46/PP-12 chain" to also cover PP-47 spatial codes).

4. **Routes 2 research drills currently in flight** (κ_3 mixing operational characterization for LLM-realistic ρ; Hyperdimensional Probe Tier-7 spec). Findings inform the program at next-cycle iteration.

---

## 1. PP-47 DRILL A FINDING — surfaced to strategy

### The decomposition

PP-47 (`hippocampal_place_field_full_v1_n4096`) confirmed mean_cosine=0.879, mean_spearman=0.879, mean_acc=1.000 at FULL N=4096 5-seed. Drill A (2x deep, algebraic + lit-scan) decomposed this:

- **The 0.879 Spearman ρ is ~100% explained by the encoding kernel itself** — top-K thresholding on Gaussian receptive fields produces a piecewise-linear (triangular) distance-similarity kernel. Patterns ξ_i and ξ_j ALREADY have ⟨ξ_i, ξ_j⟩/N decay with |i−j| BEFORE Hopfield W is applied.
- **Hopfield retrieval preserves what's already there; it doesn't create spatial structure.** Any system that preserves the encoding (top-k retrieval over raw patterns, vector DB with cosine similarity) would score ~0.879 on the same test.
- **The substrate's GENUINE spatial-coding contribution is the soft-CAN dial** (tunable between discrete-AM and CAN via P=PLACE_FRAC, K=K_LOCS — substrate-novel) **and the algebraic composition of place-field codes with substrate-novel primitives** (deletion cert, refusal cert, counterfactual abduction).

### What this means for the cap_map

Strategy's PP-47 row (0.55-0.70 EXPLORATORY with +0.05 calibration deflation) is correctly labeled "hippocampal place-field encoding" — the row reflects the substrate's CAPACITY for spatial coding. Drill A clarifies the row should NOT be over-extended to "the substrate has spatial cognition" without the composition tests below.

**Recommended cap_map annotation:** add caveat to PP-47 noting "ρ=0.879 is encoding-kernel-property; substrate's spatial-cognition CONTRIBUTION (vs vector DB equivalent) lives in the composition with PP-9 deletion cert / PP-48 NKT / PP-49 HRC / PP-46 — pending Phase-0 cross-application probe."

### What this means for the LLM-integration testbed

Drill B (2x deep, Tier-6 testbed design) identified the StepGame k=4 hop flagship test with a clean 30pp band (direct LLM ~40%, CoT ~60%, neural-symbolic ~85%). Drill A's decomposition finding requires the flagship test to include **substrate-novel sub-cells** explicitly:

- Spatial deletion cert sub-cell (substrate-unique)
- Spatial refusal cert sub-cell (substrate-unique)
- Counterfactual spatial reasoning sub-cell (substrate-unique)
- Soft-CAN dial sweep sub-cell (substrate-unique)

If the flagship test ONLY measures StepGame accuracy, the substrate will likely land in MIDDLE-BAND ("substrate matches RAG, no unique value"). The substrate-novel sub-cells are required to test the LOAD-BEARING product claim.

---

## 2. AUTHORIZATION FOR EXPERIMENT SCHEDULING — 4-phase LLM-integration program

Research **authorizes orchestrator/strategy/exp_dev to schedule** the following 4-phase program. Each phase gates the next; each has explicit HARD/MIDDLE/FAIL bands; per-PROT discipline declarations apply.

### Phase 0 — Substrate-only composition pre-checks (CPU, $0)

**Goal:** validate substrate-novel primitives compose with PP-47 place-field codes BEFORE any LLM-integration engineering.

**0a. PP-47 + PP-9 deletion-cert composition** (ALREADY FILED at `research_routing_pp47_deletion_cert_composition_2026-06-02.md`)
- Anchor: `pp47_deletion_cert_composition_v1`
- N=4096, 5-seed, ~15 min CPU
- 5 HARD-PASS conditions pre-registered; 5 HARD-FAIL trip-wires

**0b. NEW — PP-47 + PP-48 negative-knowledge tree composition** (this routing adds)
- Capability question: does the substrate encode a 3-level negative-knowledge tree of FORBIDDEN spatial locations via signed-AM + place-field codes + L3 composition, with per-level refusal cert?
- Algebraic basis: PP-47 place-field encoding + COMBO-2's PP-48 confirmed unanimous (l3_fid=1.0, b_rep=1.0, parity=0.0 at N=4096)
- Test: store K=204 positive locations + K_neg=64 forbidden locations as signed-AM at p=4 + L3 composition. Verify: positive retrieval preserved (cosine ≥ 0.80); forbidden retrieval actively repelled (anti-cosine ≤ -0.5); 3-level refusal cert generated per forbidden query
- Pre-registered HARD-PASS: positive_cos ≥ 0.80 AND forbidden_anti_cos ≤ -0.5 AND 3-level cert verifiable on ≥95% of forbidden queries
- Pre-registered HARD-FAIL: positive_cos < 0.50 OR forbidden_anti_cos > -0.20 OR cert verifiable < 70%
- Estimated wall: ~15-30 min CPU at N=4096 5-seed
- Anchor name pre-PROT-018: `pp47_pp48_negative_spatial_tree_v1`

**0c. NEW — PP-47 + PP-49 counterfactual abduction composition** (this routing adds)
- Capability question: does the substrate support Pearl L3 abductive counterfactual reasoning over spatial codes ("what would the agent infer if landmark Y had been at different location?"), using PP-47 + PP-49's confirmed counterfactual primitive?
- Test: store K=50 landmark-position pairs; for each, query counterfactual at shifted position; verify abductive reconstruction cosine ≥ 0.70
- Pre-registered HARD-PASS: counterfactual abduction cosine ≥ 0.70 across 5 seeds
- Pre-registered HARD-FAIL: counterfactual cosine < 0.40
- Estimated wall: ~20-30 min CPU at N=4096 5-seed
- Anchor name pre-PROT-018: `pp47_pp49_counterfactual_spatial_v1`

**Phase 0 gating logic:**
- ALL THREE (0a, 0b, 0c) HARD-PASS → unlocks Phase 1 with full substrate-novel sub-cell scope
- ANY HARD-FAIL → restrict Phase 1+ scope to substrate-novel primitives that PASSed; revisit product narrative for failed primitive
- MIDDLE BAND → re-test at N=8192 5-seed before Phase 1

**Total Phase 0 wall: ~1 hr CPU. $0 cloud. Decisive gating for the entire LLM-integration program.**

### Phase 1 — Tier-1 RAG-baseline (engineering 2-3 days, $0)

**Goal:** validate substrate matches FAISS-baseline on bAbI 17-20 (positional, induction, deduction, time) at < 100ms p99 latency. This is the plumbing derisk for the entire integration path.

**Capability question:** does the substrate operate as a drop-in vector-DB replacement for LLM RAG-class memory, with the substrate's 5-method API exposed as text/JSON interface (Tier-6A simplest)?

**HARD-PASS:** substrate accuracy on bAbI 17-20 within ±2pp of FAISS-RAG baseline AND latency p99 < 100ms AND audit cert verifiable on every retrieval

**HARD-FAIL:** substrate accuracy < FAISS by ≥10pp OR latency > 200ms OR cert verifiable < 80% — substrate-LLM coupling fundamentally broken, close program

**Inputs needed:** LLM choice (research recommends Llama-3-8B-Instruct via vLLM; fits 16GB VRAM at Q4_K_M), bAbI public dataset, existing PROT-018 framework

**Estimated cost:** $0 marginal (uses existing remote GPU; bAbI is public; engineering reuses substrate's existing API)

### Phase 2 — Tier-2 function-call generic (engineering 5-7 days, $5)

**Goal:** validate substrate's 5-method API (write/delete/query/health/certify) operates as JSON function-call tool with Llama-3-8B-Instruct, with multi-turn reasoning loops.

**Capability question:** can the LLM compose substrate primitives effectively to solve multi-step reasoning tasks? Does the function-call loop produce verifiable audit chains?

**HARD-PASS:** multi-turn function-call loop completes ≥95% of test tasks; substrate calls match LLM-reported reasoning ≥80%; audit chain verifiable per inference

**HARD-FAIL:** LLM cannot compose substrate primitives (calls random / off-target) OR function-call latency > 500ms per tool call

**Estimated cost:** $5 cloud (test corpus runs on Lambda)

### Phase 3 — Tier-6 flagship (engineering 7-10 days, $5-10)

**Goal:** decisive test of substrate's spatial-cognition + audit-primitive composition value-add for an LLM.

**Composite test design (per Drill A + Drill B):**

**Cell 3a — StepGame k=4 hop accuracy** (Drill B flagship):
- 4 arms: LLM-alone, LLM+vector-RAG, LLM+substrate (Tier-2 API), LLM+CoT
- 1000 test examples
- HARD-PASS: substrate-LLM ≥75% at k=4 AND ≥10pp over LLM+RAG

**Cell 3b — Spatial deletion cert sub-cell** (NEW per Drill A):
- After `substrate.delete_with_cert(location_X)`, verify downstream queries about X return "unknown" with cert chain replay verifiable
- HARD-PASS: ≥95% of post-delete queries respect deletion; cert chain verifiable
- HARD-FAIL: LLM still produces X-conditioned answers (substrate's #1 product moat broken)

**Cell 3c — Spatial refusal cert sub-cell** (NEW per Drill A + PP-49):
- Substrate refuses to encode forbidden coordinates; LLM verbalizes "I cannot store this because [cert reason]"
- HARD-PASS: 100% of forbidden-coordinate queries return refusal cert; LLM correctly verbalizes
- HARD-FAIL: LLM bypasses refusal or hallucinates a stored value

**Cell 3d — Counterfactual spatial reasoning sub-cell** (NEW per Drill A + PP-49):
- "What would the agent infer if landmark Y had been at different location (x', y')?"
- Compare CNDC counterfactual via substrate vs LLM-alone reasoning
- HARD-PASS: substrate-CNDC matches ground-truth counterfactual ≥90%; LLM-alone matches ≤70%

**Phase 3 gating:**
- ALL FOUR cells HARD-PASS → cap_map PP-47 row LIFT 0.55-0.70 → 0.75-0.90 (substrate-spatial-cognition validated as load-bearing product feature); Tier-6 stretch (BabyAI) authorized
- Cell 3a MIDDLE + Cells 3b-3d HARD-PASS → product narrative shifts to "auditable spatial memory with algebraic primitives" (not "better spatial reasoning"); still substantial product win
- Cell 3a HARD-FAIL → close Tier-6 spatial; retreat to Tier-1/2 generic substrate-as-RAG positioning

### Phase 4 — Tier-6 stretch + Tier-7 follow-on (defer, gated on Phase 3 PASS)

**Tier-6 stretch (BabyAI/MiniGrid):** engineering 15-20 days, $20-50. Only if Phase 3 HARD-PASSes.

**Tier-7 (Hyperdimensional Probe direct embedding-space coupling):** research drill currently in flight; spec will land within next cycle. Tier-7 is the deepest integration path AND most architecturally fragile — defer until Phase 3 confirms basic LLM-substrate coupling works.

---

## 3. PENDING RESEARCH DRILLS (results will inform program iteration)

Two research drills dispatched 2026-06-02 — findings will inform program at next iteration cycle:

### Drill — κ_3 mixing operational characterization for LLM patterns

**Trigger:** v334 I-10 MIDDLE — κ_3 fingerprint works at ρ≤0.1 but degrades at ρ≥0.2. LLM activation streams typically have ρ ∈ [0.15, 0.4] (topical clustering, attention-driven correlation, semantic relatedness from shared embedding space). This is exactly the regime where κ_3 fingerprint may fail in real LLM deployments.

**Key question:** does the κ_3 spectral-MAC primitive remain operationally useful when patterns are LLM activation streams, or does substrate need to drop κ_3 in favor of COMBO-3 bilinear primitives (correlation-agnostic per the v334 P9 cert)?

**Impact on program:** if κ_3 fails at LLM-realistic ρ, Cell 3 sub-cells that depend on κ_3 drift detection should be replaced with COMBO-3 trace-primitive equivalents. Affects Phase 3 cell 3b/3c (deletion / refusal cert audit primitives).

### Drill — Hyperdimensional Probe Tier-7 spec

**Trigger:** arXiv:2509.25045 (Sept 2025) — LLMs already have internal VSA-like representations decodable via hyperdimensional probe. Drill B flagged this as Tier-7 next-drill candidate.

**Key question:** what's the algebraic alignment between substrate's BSC bipolar codes and LLM residual-stream representations? Can substrate's free-Poisson identity transfer? Is Tier-7 (substrate directly reads LLM residual stream) feasible?

**Impact on program:** if Tier-7 algebraic alignment confirms, it BECOMES the flagship test (subsumes Tier-1+2 plumbing tests because it operates at full LLM bandwidth without function-call overhead). If alignment fails, Tier-7 stays parked; current 4-phase program is the path.

---

## 4. RESEARCH RECOMMENDATIONS FOR STRATEGY's v334 priorities

Strategy's v334 main-thread routing priorities (top 3 v334-new):
1. PP-48 + PP-49 production-N cross-N {8192, 16384} 5-seed
2. PP-48 cross-application probe to PP-9 / PP-46 / PP-12 chain
3. PP-49 counterfactual abduction stress test at production-N

**Research alignment:**
- Strategy priority #1 (cross-N) is correctly sequenced — confirms PP-48/PP-49 at production scale before substrate-novel-cell scoping
- Strategy priority #2 (cross-application probe) is exactly the Phase 0 cross-application test research is filing here (0a/0b/0c)
- Strategy priority #3 (counterfactual stress test) is Cell 0c in this routing

**Research recommendation:** fold Phase 0 (0a + 0b + 0c) into strategy's #2 priority. The three Phase 0 tests are substrate-only, cheap (~1 hr CPU total), and validate the cross-application composition claim that Phase 1+2+3 LLM-integration depends on. They should fire BEFORE the production-N cross-N (#1) and counterfactual stress test (#3), because if cross-application composition fails at N=4096, scaling to N=8192/16384 won't rescue it.

**Recommended strategy v335 priority sequence:**
1. Phase 0 (0a + 0b + 0c) substrate-only composition pre-checks (~1 hr CPU total)
2. PP-48 + PP-49 production-N cross-N {8192, 16384} 5-seed
3. PP-49 counterfactual abduction stress test at production-N
4. Phase 1 Tier-1 RAG-baseline (engineering 2-3 days; conditional on Phase 0 PASS)

---

## 5. DISCIPLINE DECLARATIONS

- **Capability questions only; HP/MIDDLE/FAIL bands pre-registered.** Strategy + exp_dev resolve cell design (anchor names full form, sweep grids, queue choice, timeout).
- **Pre-PROT-018 anchor-name `_n<N>` binding contract** for all new anchors (0b/0c).
- **ASCII-only print; per-experiment `--timeout`;** verbose tracing if remote-dispatched.
- **HARD-FAIL conditions explicit; MIDDLE BAND resolution paths specified.**
- **No padding:** each Phase 0 test validates ONE substrate-novel composition; no exploratory padding.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** do NOT pre-frame Phase 0 as "expected HARD-PASS"; pre-register the falsifying conditions explicitly.
- **Per `feedback_lit_scan_calibration_penalty`:** Phase 0 tests are compositions of confirmed primitives — no novel-synthesis cap applied; honest P estimates are 0.60+ for HARD-PASS based on component HARD-PASS confidence.
- **Per `feedback_batch_cloud_experiments`:** any cloud spend in Phase 1+2+3 batched single-bootstrap per phase.
- **Per `feedback_short_cloud_runs_preferred`:** Phase 1 ($0) and Phase 2 ($5) are below the standing per-case auth threshold; Phase 3 ($5-10) and Phase 4 ($20-50) need explicit user case-by-case auth before firing.

---

## 6. EXPERIMENT SCHEDULING AUTHORIZATION

**Research authorizes orchestrator to schedule:**

**IMMEDIATE (no user auth needed — substrate-only, $0):**
- Phase 0a `pp47_deletion_cert_composition_v1` (already filed; per existing `research_routing_pp47_deletion_cert_composition_2026-06-02.md`)
- Phase 0b `pp47_pp48_negative_spatial_tree_v1` (this routing adds)
- Phase 0c `pp47_pp49_counterfactual_spatial_v1` (this routing adds)
- Strategy v334 priority #1 cross-N {8192, 16384} for PP-48/PP-49

**NEAR-TERM (after Phase 0 PASS, no cloud — $0):**
- Phase 1 Tier-1 RAG-baseline (engineering 2-3 days; exp_dev designs cell from capability question + HARD bands above)

**MEDIUM-TERM (after Phase 1 PASS, low cloud — $5):**
- Phase 2 Tier-2 function-call generic (engineering 5-7 days)

**HIGH-VALUE (after Phase 2 PASS — REQUIRES USER PER-CASE AUTH):**
- Phase 3 Tier-6 flagship ($5-10 cloud)
- Phase 4 Tier-6 stretch + Tier-7 ($20-50+ cloud)

**Per `feedback_obey_user_pause_explicitly`:** orchestrator must NOT auto-dispatch any cloud spend; cloud Phase 3+ requires user explicit go/resume regardless of Phase 0/1/2 outcomes.

**Per `feedback_pipeline_pacing`:** if any CPU/GPU queue depleted, fire Phase 0 tests first (they're cheapest and most strategically load-bearing).

---

## 7. WHAT THIS ROUTING DOES NOT TOUCH

- COMBO-1 v3 redesign (filed separately; awaits exp_dev cell design)
- I-9 F4 M4-fixed MIDDLE rescue (filed by strategy v334; rescue sketches R1-R5)
- I-10 κ_3 mixing rescue (filed by strategy v334; pending κ_3-mixing-LLM drill)
- Wave 5 detail check on Cell 1 σ_TW MIDDLE (filed by testbed as theory-prereg-gap routing)
- Cap_map v334 → v335 transition (strategy owns)

These are tracked separately and proceed in parallel.

---

**END.** Orchestrator: please schedule Phase 0 (0a + 0b + 0c) IMMEDIATELY on next CPU queue refill; surface Phase 3+ to user for explicit per-case auth before firing. Strategy: please consider folding Phase 0 into v334 priority #2 cross-application probe queue. Findings from κ_3-mixing and Hyperdimensional Probe drills will update this routing at next iteration cycle.
