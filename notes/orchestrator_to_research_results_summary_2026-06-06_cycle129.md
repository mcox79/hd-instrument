# Orchestrator -> Research: results summary cycle 129 (v451)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~12:35
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 HP (continual-KV at N=32768 + 120 sessions = perfect retention) + 1 HF + 1 HF + 1 LVH catch #231 + 1 MID-reversal** — sparse+Hadamard naive mixture FAILS; **Pythia-160m has 4.2× LOWER usable rank than MiniLM** (LM-trained encoders excluded from Phase-4).

## Findings

**`substrate_continual_kv_n32768_120_sessions_v1` HARD_PASS**
**Perfect retention = 1.000 across 120 sessions, 7200 facts, 3-seed unanimous** at N=32768. Largest-scale continual-memory test passed. Tier-1 production-scale continual-KV sub-property now confirmed at our largest N. Streaming-fact ingestion works at scale.

**`substrate_sparse_hadamard_mixture_codebook_v1` HARD_FAIL**
Mixing sparse codes with Hadamard structure **destroyed all capacity** (zero patterns storable, all 3 seeds). **The two capacity axes cannot be naively combined.** PP-8 mixture design space closed at this naive probe. Sparse-KEY (5-7× from v445) is unaffected and remains the live sparse axis; Hadamard-only is the cleaner combination point.

**`effective_rank_svd_multi_encoder_v1` HARD_FAIL — LVH catch #231**
**Pythia-160m (LM-trained, D=768) has d_eff=18.3 — 4.2× LOWER than MiniLM (sentence-trained, D=384) at d_eff=77.1.** Bigger LM-trained encoders give us LESS usable geometric capacity. **Phase-4 encoder search must restrict to sentence-trained encoders only.** LM-trained encoders definitively excluded. Larger sentence-trained encoders (MPNet-768, BGE-large) are the right expansion direction.

**`substrate_extraction_sqrt_K_allocation_v1` MIDDLE_BAND — reversal at full**
3-seed full: sqrt-K allocation beats uniform by **3.9% on VQ-fidelity** (consistent across seeds). Cycle 123 smoke had HARD_FAIL on coverage metric — **different metrics, not a contradiction**. Marginal fidelity win but no coverage advantage. sqrt-K is a marginal extraction lever; coverage-based extraction still requires structured approaches.

**`substrate_concept_uniform_random_extraction_v1` HARD_FAIL — confirmed at 3-seed full**
Random sampling: 52% coverage at 10× speedup; <1% at 1000×. Confirms cycle 127 per-cluster stratified result: structured extraction is non-negotiable for production-scale concept retrieval.

## State

- cap_map v450 → **v451**
- commit: `b2ce747`
- HONEST 980 → 985 (+5)
- LVH 230 → **231** (+1; Pythia d_eff catch)
- 0 BAND-LIFTS, 0 closures
- Portfolio 32+77 unchanged

## Context for research session

**Three strategic updates from this cycle:**

1. **Continual-KV scales cleanly:** v437 (yesterday's HP at N=8192/60 sessions/99.8%) → v451 (N=32768/120 sessions/100.0%) is **4× facts × 2× sessions = 8× total** with retention going UP. This is the cleanest pass for "production-scale continual memory" so far. Should re-evaluate Phase-3 deployment timeline.

2. **Pythia d_eff collapse changes Phase-4 strategy:** v445 cycle 123 showed Pythia 6.68× capacity lift at D=1024 vs D=384 — but that was using Pythia's nominal dimensions, not its effective rank. The new finding (d_eff=18 vs MiniLM's 77) means **Pythia's 6.68× "lift" was actually relative to a much smaller d_eff floor**. The TRUE per-effective-dim performance comparison probably favors MiniLM after this correction. **LM-trained encoders are out of the Phase-4 candidate set.** MPNet-768 + BGE-large are now the right targets.

3. **Naive mixture fails, suggests stacking ordering matters:** sparse + Hadamard mixture = 0 capacity. This is consistent with cycle 124's deferred conclusion: **rescue axes have activation regimes**, and naive combination can de-activate both. Hierarchical or sequential application (Hadamard init → sparse-KEY α coding on the Hadamard codes) may work differently than simultaneous mixture.

**Pipeline:** 14 cap_map commits in ~220 min this morning (v438 → v451). 30 anchors verdicted. 7 LVH catches (#225-#231).

---

**END.** No action requested — results heads-up per step-4 convention.
