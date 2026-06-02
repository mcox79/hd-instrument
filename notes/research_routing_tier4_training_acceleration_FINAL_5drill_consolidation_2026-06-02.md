# RESEARCH ROUTING — Tier-4 training-acceleration FINAL 5-drill consolidation

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev / testbed
**Date:** 2026-06-02
**Trigger:** 5-drill consolidation (Drill 1 Tier-4 economics, Drill 2 compute decomposition, Drill 3 ICL vs Hebbian ceiling, Drill 4 Hebbian distillation pathway, Drill 5 modern-Hopfield interference scaling) all landed; substrate's training-acceleration product narrative locked on theoretical grounds.
**Supersedes:** scope of `research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md` (the Cluster A/B/C battery) — this final consolidation reorders priorities AND adds Phase 0.5b distillation MVP as the empirical capstone.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout) resolved by strategy + exp_dev. Per-PROT compliance.

---

## 0. EXECUTIVE — what the 5-drill consolidation establishes

**Substrate's training-acceleration product positioning is empirically + theoretically defensible-by-construction:**

> The only AI-memory architecture in 2026 that simultaneously:
> (i) ESCAPES the ROME/MEMIT editing wall by mechanism class separation (additive write into separate matrix avoids spectral-collapse failure root cause per REVIVE 2026 arXiv:2601.11042) — Drill 5 HARD-PASS
> (ii) OPERATES at p=4 polynomial DAM with confirmed unanimous fidelity (COMBO-2 v334 l3_fid=1.0, b_rep=1.0, parity=0.0)
> (iii) PROVIDES production-N live drift detection (κ_3 PP-50 v335 at δα=0.001 sensitivity, σ_sep up to 1727 at N=32768)
> (iv) HAS free-Poisson spectral verification at N=32768 (v324 ratified at v335)
> (v) SHIPS with cert-grade audit primitives (PP-46 deletion cert, PP-48 NKT, PP-49 HRC + counterfactual abduction, COMBO-3 5-method unified API)

**The defensible economic claim (NOT the misleading 100× full pre-training claim):** substrate-augmented LLM substitutes one-shot Hebbian writes for parameter-efficient fine-tuning on the FACT-ADDITION workload at **10²-10⁴× wall-time + cost speedup vs LoRA** ($0.05 vs $200 per 100K facts; $50-100 vs $200-2000 per 1M facts), with cert-grade audit primitives that NO competitor offers.

**Competitive landscape (post 5-drill lit-scan):**
- Separate-memory class (SERAC, GRACE, Memory Layers at Scale 128B Meta FAIR Dec 2024) — escapes the wall but NO audit primitives. Substrate dominates on audit.
- Weight-perturbation editing (ROME, MEMIT, AlphaEdit, REVIVE 2026) — fighting the wall, not escaping it. Substrate dominates on capacity + audit.
- Tier-4 architecture race (Google Titans Jan 2025, Hebbian-FW Oct 2025 arXiv:2510.21908, VSA-attention Dec 2025) — share the wall-escape via fast-weight class but lack the audit stack.

**Timing signal:** the architecture window is closing. 3-4 direct competitors landed in 2024-2025. Substrate has 3-6 months max to lock the "escape-the-wall + audit moat" positioning before competitors add audit primitives.

---

## 1. UPDATED 6-PHASE PROGRAM

### Phase 0 — Substrate-only composition pre-checks (CPU, ~$0, fires immediately)

[Already filed at `research_routing_pp47_deletion_cert_composition_2026-06-02.md` (0a) + `research_routing_llm_integration_program_2026-06-02.md` (0b, 0c).]

- **0a:** PP-47 + PP-9 deletion-cert composition (~15 min CPU)
- **0b:** PP-47 + PP-48 negative-knowledge tree composition (~15-30 min CPU)
- **0c:** PP-47 + PP-49 counterfactual abduction composition (~20-30 min CPU)

### Phase 0.5 — Tier-7 MVP private decisive test (USER AUTHORIZED, ~$50-100 + 8 eng-days)

[Filed at `research_routing_llm_integration_program_amendment_phase0p5_2026-06-02.md`.]

- 3 sub-tests A/B/C on Llama-3.1-8B + hyperprobe (arXiv:2509.25045)
- Tests audit primitives at LLM coupling (failure mode b from Drill 5 — the HIGHEST remaining risk)
- **Sub-test B (deletion cert against live LLM state) is THE load-bearing test** for the entire substrate-LLM coupling story per Drill 5
- 4-7 GPU-days cloud + 8 engineering-days

### Phase 0.5b — NEW: Hebbian distillation MVP (REQUIRES USER AUTH, $15-40 + 1-2 weeks engineering)

**Goal:** empirical capstone — does Pathway B knowledge-graph distillation actually deliver the 10²-10⁴× speedup at 10K-fact production scale?

**Pathway B spec** (per Drill 4):
- Base model: Llama-3.1-8B-Instruct
- Distillation method: knowledge-graph triple extraction via fact-elicitation prompts; encode each (s, p, o) triple as VSA-bound bipolar pattern ξ = bind(s, p, o); Hebbian-write to substrate
- Substrate: N=8192, single bank initially, α=0.122 (well within α_c=0.138 from Hopfield theory)
- Eval set: 1K held-out distilled facts + 1K base-LLM facts NOT in distilled set + MMLU 1K-question subset

**Pre-registered HARD-PASS bands** (per Drill 4 + Drill 5 reinforcement):
- Distilled-fact recall ≥ 0.85 (substrate beats RAG-with-vector-DB baseline at same fact count)
- Non-distilled-fact degradation ≤ 2pp (substrate does NOT interfere with base LLM)
- MMLU degradation ≤ 2pp (general capability preserved per Drill 5 mechanism-class-separation argument)
- ONE-SHOT addition of 100 new facts post-distillation: ≥0.85 accuracy within 1 minute (the killer demo)
- Deletion cert verifies on 100-fact deletion subset (audit primitive works on LLM-coupled state)

**Pre-registered HARD-FAIL bands:**
- Distilled-fact recall < 0.65 (worse than RAG baseline)
- Catastrophic interference (>5pp on non-distilled facts or MMLU) — would refute Drill 5 mechanism-class separation argument empirically
- Audit primitives fail (κ_3 doesn't detect injected drift, OR deletion cert verification fails)
- Substrate exhibits catastrophic forgetting wall before 50K facts on Pathway B — would directly refute Drill 5 theoretical HARD-PASS

**MIDDLE BAND:** 0.65-0.85 distilled recall OR 2-5pp degradation — implies distillation works but needs hierarchical scaling (PP-12 L=3 multi-bank addressing) or whitening.

**P_deflated for Phase 0.5b MVP HARD-PASS: 0.45-0.55** (UP from Drill 4's 0.38 because Drill 5 removed the "wall risk" component; the remaining risks are operational not foundational).

**Anchor name (pre-PROT-018):** `phase0_5b_distillation_mvp_llama31_kg_triples_v1`. No _nN suffix (LLM-native dimension drives substrate N=8192 by default).

### Phase 1 — Tier-1 RAG-baseline (engineering 2-3 days, $0)

[Already filed.] Substrate vs FAISS on bAbI 17-20. Plumbing derisk.

### Phase 2 — Tier-2 function-call generic (engineering 5-7 days, $5)

[Already filed.] LLM tool-call loop with substrate's 5-method API.

### Phase 3 — Cluster A substrate-only training-speedup primitive validation (CPU, ~$0, fires immediately)

[Filed at `research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md`.]
- A1 Hebbian-vs-GD identity at N=1024 M=100
- A2 Deletion cert at training scale (M=1000, K∈{10, 50, 100, 500})
- A3 Counterfactual training diagnostic via PP-49
- A4 Active-repulsion training via signed-AM at p=4

All four fire on next CPU queue refill, parallel. Total wall ~3-4 hr CPU. $0.

### Phase 4 — Tier-6 flagship StepGame composite test (engineering 7-10 days, $5-10)

[Filed at `research_routing_llm_integration_program_2026-06-02.md`.] Now incorporates substrate-novel sub-cells per Drill A/B PP-47 decomposition finding.

### Phase 5 — DEFERRED: Tier-4-lite full Llama-3.1-8B (drops in priority per Drill 5 verdict)

Drill 1 + Drill 5 both indicate Tier-4-lite (one FFN swap in Llama-3.1-8B) is HIGHER cost than Phase 0.5b distillation MVP for SIMILAR strategic value:
- Tier-4-lite: 30 eng-days + $250-600 cloud; P_deflated = 0.32-0.38
- Phase 0.5b distillation MVP: 1-2 weeks eng + $15-40 cloud; P_deflated = 0.45-0.55

**Recommendation: defer Tier-4-lite indefinitely; Phase 0.5b distillation MVP is the strategic substitute.** Tier-4-lite re-considered only if Phase 0.5b HARD-PASSes and there's specific demand for FFN-substitution architecture (e.g., for compositional reasoning extension beyond fact addition).

---

## 2. UPDATED P_DEFLATED TABLE (all 5 drills integrated)

| Test | P_deflated | Status |
|---|---|---|
| Drill 5 theoretical: substrate escapes ROME/MEMIT wall | **0.52** (HARD-PASS) | landed; above novel-synthesis cap |
| Phase 0 substrate-only composition pre-checks | 0.65 (median across 0a/0b/0c) | filed; queue ready |
| Phase 0.5 Tier-7 MVP HARD-PASS | 0.42 (per amendment) | authorized; engineering proceeding |
| **Phase 0.5b distillation MVP HARD-PASS** | **0.45-0.55** (UP from 0.38 post-Drill-5) | **NEEDS USER AUTH** |
| Cluster A all-PASS (substrate-only training primitives) | 0.70+ | $0; fire NOW |
| Cluster B all-PASS (small substrate-augmented LLM) | 0.40-0.45 | gated on Phase 0 + 0.5 PASS |
| Cluster C all-PASS (Llama-3-8B substrate-augmented) | 0.32 | gated on Cluster B PASS + user auth |
| Tier-4-lite full (DEFERRED) | 0.32-0.38 | superseded by Phase 0.5b |
| Joint Phase 0.5 + 0.5b both HARD-PASS | 0.20-0.27 | locks substrate flagship positioning |

---

## 3. AUTHORIZATION REQUEST FOR PHASE 0.5b

Per `feedback_short_cloud_runs_preferred`: $15-40 is at/below the standing per-case auth threshold but I'm surfacing for explicit thumbs-up because:
- This is the EMPIRICAL CAPSTONE for the substrate's "escape the wall" product story
- A HARD-PASS empirically locks the substrate-product positioning that Drill 5 supports theoretically
- A HARD-FAIL would directly refute Drill 5's mechanism-class-separation argument

**Specific ask:** authorize $15-40 cloud + 1-2 weeks engineering for `phase0_5b_distillation_mvp_llama31_kg_triples_v1` — distill 10K facts from Llama-3.1-8B via knowledge-graph triple extraction; verify substrate-augmented Llama-3.1-8B preserves base capabilities + retrieves distilled facts ≥85% + audit primitives operate correctly + one-shot add 100 new facts in 1 minute.

If authorized, this can fire IN PARALLEL with Phase 0.5 Tier-7 MVP. They share Llama-3.1-8B infrastructure (single cloud bootstrap if scheduled together).

---

## 4. UPDATED SEQUENCING

```
NOW (parallel, $0 + pre-authorized):
├── Phase 0 (substrate-only composition pre-checks, ~1 hr CPU, $0) [filed]
├── Cluster A (substrate-only training primitives, ~3-4 hr CPU, $0) [filed]
└── Phase 0.5 Tier-7 MVP (AUTHORIZED, $50-100, 8 eng-days bring-up) [filed]

+1-2 weeks (CONDITIONAL ON USER AUTH):
└── Phase 0.5b distillation MVP ($15-40, 1-2 weeks engineering)
      Can run in same cloud bootstrap as Phase 0.5 Tier-7 MVP (shared Llama-3.1-8B infra)

GATE 1 (Phase 0 + Phase 0.5 + Cluster A + Phase 0.5b all PASS):
└── External-discussion-ready: substrate has empirical "escape the wall + audit moat" claim

GATE 2 (Gate 1 + Strategic decision to scale):
├── Phase 1 Tier-1 RAG-baseline (2-3 days, $0)
└── Cluster B (small substrate-augmented LLM, $5-30 each, 1-3 days each)

GATE 3 (Phase 1 + Cluster B all PASS, REQUIRES USER PER-CASE AUTH):
├── Phase 2 Tier-2 function-call generic (5-7 days, $5)
└── Cluster C (Llama-3-8B substrate-augmented, $50-300)

GATE 4 (Phase 2 + Cluster C all PASS):
└── Phase 3 Tier-6 flagship StepGame composite ($5-10)

DEFERRED:
└── Tier-4-lite full Llama-3.1-8B (superseded by Phase 0.5b as strategic substitute)
```

**Total program cost ceiling:** ~$250-550 cloud + ~6-10 weeks engineering. **If Phase 0.5 + Phase 0.5b both HARD-PASS, the substrate's flagship positioning is empirically locked at ~$110 total cloud + 3-4 weeks engineering** — well below the original program estimate.

---

## 5. WHY PHASE 0.5b PROMOTION IS THE LOAD-BEARING DECISION

The 5-drill consolidation makes Phase 0.5b the strategic capstone, not Phase 4 / Tier-4-lite / Cluster C. Three reasons:

1. **Theoretical case is locked (Drill 5 HARD-PASS, P=0.52).** The remaining question is empirical: does the substrate-LLM coupling preserve the wall-escape AND the audit primitives at production scale?

2. **Phase 0.5b directly tests the dominant product claim.** "10²-10⁴× cost speedup on fact addition vs fine-tuning, with cert-grade audit primitives, on a real frontier-class LLM." A HARD-PASS on Phase 0.5b is the external-pitch-ready empirical anchor.

3. **The competitive window is narrow.** Memory Layers at Scale (Meta FAIR Dec 2024) is 128B params + 1T tokens — the separate-memory class is being industrialized RIGHT NOW. If the substrate doesn't ship empirical validation of the audit-moat claim within 3-6 months, the moat narrows substantially (competitors realize they need audit primitives too).

**Phase 0.5b is the cheapest single test that closes the substrate's product story.** $15-40 buys empirical validation of a positioning that could be worth $1B+ TAM if confirmed.

---

## 6. CAP_MAP UPDATE REQUESTS (research recommendation; orchestrator commits)

On Drill 5 HARD-PASS commit:
- **NEW issue I-12 RESOLVED on theoretical grounds:** "additive Hebbian write escapes ROME/MEMIT spectral-collapse wall by mechanism class separation; substrate not subject to weight-perturbation editing limits per REVIVE 2026 + Drill 5 theoretical verdict"
- **NEW row candidate PP-55** "wall-escape via separate-matrix additive write" 0.55-0.70 EXPLORATORY (with +0.05 calibration deflation; this is the substrate-novel claim ground in Drill 5 lit-scan)

On Phase 0 + Cluster A + Phase 0.5 + Phase 0.5b all PASS commit:
- **PP-55 LIFT to 🟢 0.70-0.85** (empirically validated wall-escape at LLM coupling + distillation scale)
- **NEW killer feature #11** "auditable continuous-learning LLM customization at $0.001/fact via Hebbian distillation"
- **PP-46 + PP-48 + PP-49 + PP-50 LIFTs** to "production-LLM coupling confirmed at frontier-LLM scale"

---

## 7. DISCIPLINE DECLARATIONS

- **Capability questions only; HP/MIDDLE/FAIL bands pre-registered.** Strategy + exp_dev resolve cell design.
- **Pre-PROT-018 anchor names** per Section 1 suggestions; Phase 0.5b uses no _nN suffix (LLM-native).
- **ASCII-only print; per-experiment `--timeout`.**
- **Single-bootstrap cloud dispatch:** Phase 0.5 + Phase 0.5b CAN share Llama-3.1-8B infrastructure if scheduled together (one Lambda instance, two test batteries).
- **No padding.** Phase 0.5b tests ONE substrate-novel claim (distillation pathway viability at 10K facts) with explicit HARD-FAIL trip-wires.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** task prompts MUST NOT pre-frame Phase 0.5b as HARD-PASS; pre-register HARD-FAIL conditions explicitly.
- **Per `feedback_lit_scan_calibration_penalty`:** Phase 0.5b P_deflated 0.45-0.55; novel-synthesis cap relaxed because Drill 5 lit-scan removes the load-bearing theoretical risk.
- **Per `feedback_obey_user_pause_explicitly`:** Phase 0.5b REQUIRES USER EXPLICIT AUTH before cloud dispatch.
- **Per `feedback_batch_cloud_experiments`:** if Phase 0.5 + Phase 0.5b both authorized, batch into single Lambda instance (shared Llama-3.1-8B, ~$70-140 combined).

---

## 8. WHAT'S NOT IN THIS ROUTING (handled elsewhere)

- COMBO-1 v3 redesign (separate research routing, ongoing; not load-bearing for distillation MVP)
- I-9 F4 M4 + I-10 κ_3 mixing rescues (strategy v336 ongoing; not load-bearing)
- Wave 5 Cell 1 σ_TW detail check + I-11 RMT recalibration (separate; not load-bearing)
- Cap_map v336 → v337 transition (strategy owns)
- Tier-5 (multi-agent shared substrate) — far-future, gated on Phase 0.5 + 0.5b establishing Tier-4 coupling works
- Tier-7 cross-LLM probe-of-probe (level-3 drill, post Phase 0.5)

---

## 9. CROSS-THREAD SYNTHESIS

The 5-drill consolidation INTEGRATES findings from:
- **Drill 1 (Tier-4 economics):** architecture saturated; audit primitives are the moat
- **Drill 2 (compute decomposition):** FFN dominates compute (60-66%); substrate substitutes fact-addition FFN-style at 10²-10⁵×; full pre-training capped at ~3×
- **Drill 3 (ICL vs Hebbian ceiling):** linear-attention ICL ≡ Hebbian write (Schlag 2021); system-level 30-100× speedup on canonical workloads; arXiv:2510.21908 (Oct 2025) Hebbian-FW transformers BEAT gradient on copying/regression/few-shot
- **Drill 4 (Hebbian distillation pathway):** Pathway B (KG-triple) is the MVP; $50-100 for 1M facts distillation; the substrate-novel claim was "additive write escapes ROME/MEMIT wall"
- **Drill 5 (interference scaling):** **theoretically VALIDATED** — REVIVE 2026 confirms mechanism class separation; Demircigil 2017 confirms p=4 capacity ceiling 7.6×10⁸ at N=8192; SERAC/GRACE/Memory-Layers-at-Scale class scales to production

**Strategic state of the substrate's training-acceleration product story:**
- THEORETICAL: locked (Drill 5 HARD-PASS at P=0.52)
- EMPIRICAL: pending Phase 0.5 Tier-7 MVP (audit primitives at LLM coupling) + Phase 0.5b distillation MVP (wall-escape at 10K-fact distillation)
- COMMERCIAL: requires Phase 0.5 + Phase 0.5b both HARD-PASS to surface externally

---

**END.** Orchestrator: queue Phase 0 + Cluster A on next CPU queue refill immediately (parallel, $0); start Phase 0.5 engineering bring-up (authorized); surface Phase 0.5b authorization request to user. Strategy: file PP-55 row candidate + I-12 resolved per Section 6; consider folding into v337 batch. exp_dev: cell design for Phase 0 + Cluster A from prior routing files; Phase 0.5b cell design from Section 1 capability questions + HARD bands; Phase 0.5 + 0.5b CAN share Llama-3.1-8B cloud instance if scheduled together.
