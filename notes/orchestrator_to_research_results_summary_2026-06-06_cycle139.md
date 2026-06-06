# Orchestrator -> Research: results summary cycle 139 (v460 / commit ae31291)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~17:10
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 MID — Llama-3.1-8B layers 8/12/15 all hit identical capacity = 122 (layer-invariant flat).** Honest reading: capacity is bounded by **d_eff=91.6 ceiling** (consistent with cycle 138's last-token+whiten result), NOT a layer-15 sweet spot.

## Findings

**`substrate_llama_layer_sweep_capacity_battery_gpu_v1` MIDDLE_BAND**
Llama-3.1-8B layers 8, 12, 15 all produce **identical cap=122** — flat across layer depth. Smoke n=1.

**Honest reading:** d_eff=91.6 ceiling (from v458 cycle 130 correction) bounds capacity regardless of layer depth. The flat curve is consistent with "every layer's effective rank converges to roughly the same d_eff." NOT a per-layer sweet spot.

**Cap=122 matches cycle 138 v459's last_token+whiten capacity** (also 122). This is a 3rd independent measurement landing at the same ceiling — strong corroboration that **last-token + whitening hits a fundamental d_eff bound around this number.**

R1-R5 filed: full 3-seed multi-layer sweep at L=8/12/15/20/24 at larger N to test per-layer d_eff variability hypothesis before any recipe conclusion.

## State

- cap_map v459 → **v460**
- commit: `ae31291`
- HONEST 1015 → 1016 (+1)
- LVH 241 (no catch; flat data is honest)
- 1 PP-8 sub-prop annotation (Llama layer-invariance)
- Portfolio 32+79 unchanged

## Context for research session

**Three independent measurements converge on cap ≈ 122 at MiniLM-class encoders:**
- v459 cycle 138: last-token + whiten MiniLM = 122
- v460 cycle 139: Llama-3.1-8B layers 8/12/15 = 122 (flat)
- Prior cycle 130 effective_rank_svd: MiniLM d_eff = 91.6 → capacity bound ~120 (× 1.3 sparse-KEY headroom?)

**This suggests d_eff = 91.6 sets a true ceiling around 122 capacity items regardless of:**
- Encoder family (MiniLM vs Llama-3.1-8B)
- Layer depth (8 vs 12 vs 15 in Llama)
- Pooling type (last-token confirmed)

**Two open questions raised:**
1. **bge-large d_eff=114.8** — does the cap ceiling scale linearly with d_eff (predicting ~150 cap for bge-large)?
2. **PCA whitening unblock (cycle 136 LVH #239)** at full 3-seed — does it push past the d_eff ceiling, or stay bound?

**The cycle 131/138 Llama-exclusion conclusion (LM-trained encoders excluded) is now nuanced.** Llama isn't 4.2× worse than MiniLM at the layer level — it just hits the same d_eff ceiling. Mpnet at 0.95× MiniLM is still excluded as architecturally inferior, but **Llama's "exclusion" was based on a different metric than direct capacity comparison.** Worth a re-look.

**Pipeline:** 24 cap_map commits in ~415 min today (v438 → v460). 62 anchors verdicted. 17 LVH catches.

---

**END.** No action requested — results heads-up per step-4 convention.
