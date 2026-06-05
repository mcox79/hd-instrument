# exp_dev hand-off -- research: substrate tier-emergent training tricks per LLM scale

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_tier_emergent_tricks_per_llm_scale_2x_2026-06-04.md
Pause state: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context only. exp_dev designs the sweep grids, threshold formulas, and queue routing autonomously.

---

## Anchor candidates (rank-ordered)

### 1. Tier-3 substrate-mediated LoRA routing (T3-A)
- Anchor pointer: Tier-3 substrate as LoRA adapter router
- Substrate-product reading: substrate W_s (Hebbian-updated, no backprop) routes across k=8 LoRA adapters at 1B scale; prevents router collapse that costs ~15-20% overhead in RL-router alternatives (ReMix arxiv 2603.10160)
- Tier hint: remote GPU (1B model fits 4060 Ti 16 GB in BF16 + LoRA)
- Why now: P_deflated=0.42 -- highest in this drill; addresses a documented pain point; 1h wall experiment; clean comparison available (substrate router vs learned linear router vs uniform mix)

### 2. Tier-2 substrate warmup (T2-A)
- Anchor pointer: Tier-2 Hebbian warmup -- Hebbian pre-warm then gradient transition for Pythia-160M class
- Substrate-product reading: Tyulmankov et al. 2024 (PLOS CB) establishes Hebbian = attention mechanistically; substrate warmup should reduce Adam optimizer step count by ~10% in early training phase
- Tier hint: remote CPU or remote GPU (160M model; fast)
- Why now: strongest theoretical bridge found in drill; P_deflated=0.35; cheapest test in the tier catalog (~1h wall on 4060 Ti or even CPU)

### 3. Tier-5 model-soup routing (T5-C) -- inference-time only
- Anchor pointer: Tier-5 substrate as model-soup glue -- task-embedding router across fine-tuned checkpoints
- Substrate-product reading: no training loop modification; substrate W_s routes across checkpoint ensemble at inference time; P_deflated=0.42; Souper-Model (arxiv 2511.13254) + Model Soups (arxiv 2203.05482) are the lit anchors
- Tier hint: cloud H100 inference evaluation (NOT training); piggybacks on existing 70B inference budget
- Why now: deployment-ready (inference-only); authorization check needed (per feedback-short-cloud-runs-preferred)

### 4. Tier-4 substrate as MoE gate (T4-A) -- CONDITIONAL
- Anchor pointer: Tier-4 substrate as MoE gating router at 8B scale
- Substrate-product reading: only cost-beneficial if substrate N < d_model; at N=8192 and d_model=4096 the gate is MORE expensive; must set N=2048 for cost parity; P_deflated=0.20 at N=8192 but 0.45 at N=2048
- Tier hint: cloud H100 (8B model); batch with other Tier-4 experiments
- Why now: conditional on N configuration decision; do NOT dispatch until N constraint resolved

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_tier_emergent_tricks_per_llm_scale_2x_2026-06-04.md
- Template: d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md

---

## Contract

exp_dev MUST:
- Pre-register HP/MID/HF bands per feedback-envelope-expansion-fail-bands before dispatching any anchor
- Verify queue name uniqueness pre-ship per feedback-ship-name-collision
- Use _n<N> suffix binding where N counts iterations per feedback-no-label-vs-honest-anchor-names
- For T4-A: confirm N < d_model before coding the gate; abort and surface to orchestrator if N >= d_model

## Autonomy declaration

exp_dev has full autonomy to: choose sweep grid values, write the experiment script, select queue routing (remote GPU vs cloud), set timeout formulas, write pre-reg cells. exp_dev does NOT need orchestrator approval for Tier-2 and Tier-3 anchors. Tier-4 cloud dispatch requires orchestrator confirmation per cost policy.
