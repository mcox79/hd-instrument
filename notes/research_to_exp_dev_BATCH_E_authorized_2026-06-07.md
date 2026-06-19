# Research -> Exp-Dev: Batch E AUTHORIZED -- 10 highest-leverage cells consolidated across all 5 drills

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~05:30
**Re:** 5 drill handoffs landed simultaneously (Drill 1 production deployment + Probe 2 adversarial + Drill 3 cross-domain round 5 + Drill 4 mean-pool tax + Drill 5 d_eff capacity ceiling theory)
**Subject:** User authorized consolidated Batch E. 10 cells; ~6-8h CPU sequential / ~3-4h parallel; $0. GPU runner restored (your OOM fix). High-leverage concentrated batch -- multiple cells could revise production architecture decisively.

---

## Why this is consolidated (not 5 separate batches)

5 drills delivered 23 total cells. Dispatching as 5 separate batches would create churn + dependency confusion. Batch E consolidates the **top-10 highest-leverage cells across all drills** into one coherent dispatch.

You retain full autonomy on:
- Ordering / parallelism / batching within the 10
- Numerical parameters per [[feedback-no-experiment-design-in-prompts]]
- HP/MID/HF thresholds per envelope-fail-band protocol
- Queue routing (GPU vs CPU per torch usage)
- Smoke profiles + full profiles

The rank ordering below is **recommended priority** based on cross-drill leverage analysis.

---

## TIER 1 -- Theoretical/empirical foundation (cells 1-5)

### Cell 1: CELL-MF-1 effective interaction order probe
- **Anchor pointer:** notes/exp_dev_handoff_research_cross_domain_round5_2026-06-07.md (Drill 3 #1)
- **Why now:** CHEAPEST DECISIVE TEST OF DAY. Adjudicates O(N) vs O(N^2) capacity scaling. RSB alpha_c=0.144N may already bind cap=122 at d_eff=91.6.
- **Wall:** 30 min CPU; algebraic sweep
- **Strategic value:** Either confirms fundamental limit (production forced to shard at 122) OR reveals 5-10x headroom (production architecture has more flexibility). Drill 1's 82K-shard federation count may need 5-10x revision based on outcome.

### Cell 2: Hebb vs perceptron write rule comparison
- **Anchor pointer:** notes/exp_dev_handoff_research_mean_pool_tax_investigation_2026-06-07.md (Drill 4 anchor D; TAX-1)
- **Why now:** LARGEST SINGLE UNREALIZED CAPACITY GAIN. Amit-Gutfreund-Sompolinsky 1985: pseudoinverse alpha_c~1.0 vs Hebb alpha_c~0.14 = ~7x for bipolar (substrate is bipolar). Algebraically grounded since 1985.
- **Wall:** ~30 min CPU; 2 cells
- **Strategic value:** Could match or exceed all today's compound axes combined. Today's "production-ready" framing depends critically on this not being broken.

### Cell 3: Alpha fine-sweep below 0.04
- **Anchor pointer:** Drill 4 anchor A; TAX-10
- **Why now:** EV=1.86 (highest in Drill 4). Cycle 130 found 20x at alpha=0.04 vs 5-7x at alpha=0.20; sweep didn't go below 0.04. ZERO architecture change required.
- **Wall:** CPU short
- **Strategic value:** If curve continues to rise: 2-4x more gain immediately.

### Cell 4: Padding side audit + capacity sweep
- **Anchor pointer:** Drill 4 anchor C; TAX-2
- **Why now:** EV=1.13; one-line fix (tokenizer.padding_side='left'). MAY ENTIRELY EXPLAIN cycle 138's "last-token raw=0" anomaly via PAD-token extraction (HuggingFace defaults right-padding; right-padding + last-token = extract PAD embeddings which are zero).
- **Wall:** 15 min CPU
- **Strategic value:** If true: cycle 138 comparison was apples-to-oranges (mean-pool of real tokens vs last-token of PAD tokens). Production encoder recipe may need revision.

### Cell 5: BGE-large capacity measurement
- **Anchor pointer:** notes/exp_dev_handoff_research_d_eff_capacity_ceiling_theory_2026-06-07.md (Drill 5 #1)
- **Why now:** Tests Drill 5 PRED-1 directly. Linear: cap in [140,165] = HP. Sublinear: cap <125 = HF.
- **Wall:** Encoder swap + full
- **Strategic value:** Falsifies or confirms cap ~ 1.33*d_eff Marchenko-Pastur theory. Directly informs production encoder choice.

---

## TIER 2 -- Production gates (cells 6-8)

### Cell 6: KF-1 paraphrase robustness battery
- **Anchor pointer:** notes/exp_dev_handoff_research_adversarial_divergence_2026-06-07.md (Probe 2 #1)
- **Why now:** TIER-1 URGENT per Probe 2. Critical adversarial production gate. Predicted AUC drop 0.977 -> 0.55-0.65 (barely above random) under back-translation. Script-kiddie accessible attack.
- **Wall:** 1 GPU-hour
- **Strategic value:** If HF (predicted): KF-1 alone insufficient for deployment; need hybrid (substrate + bigrams + NLI + paraphrase-aware).

### Cell 7: fp16 vs fp32 parity test across 6 capabilities
- **Anchor pointer:** Probe 2 #2
- **Why now:** TIER-2 HIGH. Production often fp16; PCA whitening drift. LVH #241 proved pipeline bugs exist. Quick measurement-hygiene check.
- **Wall:** Quick verification
- **Strategic value:** If fp16 differs significantly: all production metric claims need re-verification at production precision.

### Cell 8: P1 shard-split correctness under capacity overflow
- **Anchor pointer:** notes/exp_dev_handoff_research_production_deployment_architecture_2026-06-07.md (Drill 1 #1)
- **Why now:** Drill 1 production gate. d_eff=91.6 ceiling at cap=122 forces sharding from day 1. If shard-split fails: production sharding strategy must be redesigned.
- **Wall:** CPU <1h
- **Strategic value:** Blocks production deployment until passed.

---

## TIER 3 -- Low-cost high-EV taxes (cells 9-10)

### Cell 9: Metric M_max uncensor (50 -> 200)
- **Anchor pointer:** Drill 4 anchor B; TAX-6
- **Why now:** EV=1.82. Retroactive audit of prior saturation verdicts. Cycle 133 M=4 "saturation" at risk.
- **Wall:** 0.5 cells
- **Strategic value:** Validates or invalidates prior saturation verdicts (M=4, K=20, etc).

### Cell 10: HNSW ef_search calibration curve
- **Anchor pointer:** Drill 1 #3
- **Why now:** Certain failure at default ef_search (FAISS env discovery showed recall@1=0 at default). Production must pin ef_search >= 200.
- **Wall:** CPU <30 min
- **Strategic value:** Empirically grounds the production HNSW configuration; prevents certain failure mode.

---

## Total estimate

- Sequential CPU: ~6-8h
- Parallel (GPU runner restored per your OOM fix): ~3-4h
- Cost: $0 (no cloud cells in Batch E)

## Why each cell could revise the production story

| Cell HP outcome | Production story revision |
|---|---|
| Hebb->perceptron 7x | Compound math revised UP 7x; today's 600-1500x becomes 4200-10500x synthetic |
| Padding fix 1.5-3x | Cycle 138 encoder recipe re-interpreted; mean-pool tax narrative changes |
| CELL-MF-1 O(N^2) | Production sharding count drops 5-10x; 82K shards becomes 8-16K |
| BGE-large cap >150 | Linear d_eff theory confirmed; encoder upgrade path empirically validated |
| KF-1 paraphrase HP | Production hallucination guard survives script-kiddie attacks |
| Alpha <0.04 sweep | Additional 2-4x easy gain |

## Cross-references

- 5 drill handoffs (all in notes/ directory):
  - notes/exp_dev_handoff_research_production_deployment_architecture_2026-06-07.md (Drill 1)
  - notes/exp_dev_handoff_research_adversarial_divergence_2026-06-07.md (Probe 2)
  - notes/exp_dev_handoff_research_cross_domain_round5_2026-06-07.md (Drill 3)
  - notes/exp_dev_handoff_research_mean_pool_tax_investigation_2026-06-07.md (Drill 4)
  - notes/exp_dev_handoff_research_d_eff_capacity_ceiling_theory_2026-06-07.md (Drill 5)

- Research notes (full theoretical content):
  - notes/research_drill_production_deployment_architecture_2026-06-07.md
  - notes/research_drill_adversarial_substrate_divergence_2026-06-07.md
  - notes/research_drill_cross_domain_round5_2026-06-07.md
  - notes/research_drill_mean_pool_tax_investigation_2026-06-07.md
  - notes/research_drill_d_eff_capacity_ceiling_theory_2026-06-07.md

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds, queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. write_metrics() required fields. ASCII-only. Apply [[feedback-no-experiment-design-in-prompts]] -- this handoff names anchors + WHY + tier only.

13 other cells from the 5 drills are NOT in Batch E -- they're documented in each drill's individual handoff for future dispatch as cap_map priorities evolve.

## Autonomy

You may:
- Reorder cells by queue state / runner availability
- Parallelize across CPU/GPU lanes
- Skip cells if a prior cell's outcome makes them redundant (e.g., if padding fix HF and recipe re-interpreted, BGE-large measurement may need re-spec)
- Add adjacent cells from the 5 drill handoffs if a cell's outcome opens follow-ups

---

**END.**

**Exp-Dev:** Batch E authorized (10 cells; ~3-4h parallel; $0). Tier 1 (cells 1-5) is highest-leverage decisive; Tier 2 (cells 6-8) are production gates; Tier 3 (cells 9-10) are low-cost high-EV. CELL-MF-1 (cell 1) and Hebb->perceptron (cell 2) are the two most strategically important results -- their outcomes could revise today's entire production architecture.

**User:** Batch E (10 cells consolidated across all 5 drills) routed to Exp-Dev. $0; ~3-4h parallel. Multiple cells could revise production story by 10-100x AND clarify which architecture is right. Highest-priority cells: CELL-MF-1 interaction-order probe + Hebb->perceptron write rule + padding fix + BGE-large capacity + KF-1 paraphrase robustness.

**Orchestrator + Testbed:** Informational; Exp-Dev's lane.
