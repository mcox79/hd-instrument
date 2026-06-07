# exp_dev hand-off -- research: K-hop Noise Model Selection 2x Drill

**Filed-by:** research sub-agent
**Trigger:** notes/research_drill_khop_noise_model_selection_2x_2026-06-07.md
**Pause state:** Respect orchestrator_paused.flag before dispatching any queue item.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the concrete experiments;
this file provides the strategic context and anchor candidates only.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- Distractor Coherence Measurement (Cell A)
**Anchor pointer:** Measure c_d_empirical (distractor cosine coherence) on 100-shard test.
**Substrate-product reading:** If c_d < 0.20, confidence threshold alone is sufficient for
  v1/v2 production; if c_d > 0.35, semantic sharding must be added to v2 spec.
**Tier hint:** CPU smoke (2h). Priority: CRITICAL -- this is the load-bearing measurement
  for the entire K-hop production architecture.
**Why now:** Cycle 151 showed averaging and distractor models produce opposite K_max trends.
  This cell determines which regime applies to real substrate queries. All other v1/v2/v3
  architecture decisions (confidence threshold, semantic sharding, hub replication coverage)
  follow from this single measurement. Run before any v1 K-hop implementation begins.

HARD-PASS: c_d_empirical < 0.20 (random distractor; averaging with confidence threshold)
HARD-FAIL: c_d_empirical > 0.40 (coherent distractor; semantic sharding required)
MIDDLE-BAND: 0.20-0.40 (sparse-KEY + confidence threshold sufficient)

### Anchor 2 -- K_max Phase Diagram (Cell B)
**Anchor pointer:** Sweep K_max vs (p_d, c_d) grid at B=10, N=4096 synthetic shards.
**Substrate-product reading:** Empirically validate hybrid model formula
  K_max = (1-p_d)/(p_d*c_d). Phase diagram determines safe operating envelope.
**Tier hint:** CPU (3h). Run after Cell A for calibration context.
**Why now:** Pre-registers HARD-PASS/HF thresholds per drill note Section 6.2.

HARD-PASS (for analytics): K_max(p_d=0.9, c_d=0.0) > 15; K_max(p_d=0.9, c_d=0.3) < 4
HARD-FAIL: K_max(p_d=0.9, c_d=0.0) < 5 (random distractors causing collapse -- showstopper)

### Anchor 3 -- Mitigation 5 Validation (Cell C)
**Anchor pointer:** Measure K_max improvement from sparse-KEY + T=0.85 confidence threshold
  at simulated c_d=0.28, B=10. 3 configurations: dense/no-thresh, dense/thresh, sparse/thresh.
**Substrate-product reading:** If K_max(sparse+thresh) >= 12, no semantic sharding needed.
  This directly determines v2 complexity (2 months vs 2.5-3 months with semantic sharding).
**Tier hint:** CPU (4h). Run after Cell A + B.
**Why now:** Addresses the two-line configuration change (Component 4 + Component 2 update)
  that either resolves the distractor problem or triggers a more expensive structural fix.

HARD-PASS: K_max(Config C) / K_max(Config A) >= 5x AND K_max(Config C) >= 12
HARD-FAIL: K_max(Config C) < 8 (sparse-KEY insufficient; semantic sharding required)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_khop_noise_model_selection_2x_2026-06-07.md
- Chain 3 Drill 3 (noise model): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
- Chain 3 Drill 4 (sparse-KEY): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill4_2026-06-07.md
- Chain 3 Drill 5 FINAL (GOLD 5.0 spec): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md
- Prior handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_production_scaling_5x_chain3_drill1_2026-06-07.md

---

## Contract section

exp_dev is contracted to:
1. Design Cell A (distractor coherence measurement) as the first experiment
2. Report c_d_empirical and which regime bucket (< 0.20 / 0.20-0.35 / > 0.35)
3. Based on Cell A result, proceed to Cell B (phase diagram) or Cell C (mitigation validation)
4. Pre-register all HARD-PASS / HARD-FAIL thresholds as specified above BEFORE coding
5. Use N=1024-4096 (fast CPU) for all three cells; no GPU required

## Autonomy declaration

exp_dev owns all decisions about:
- Exact test setup (N, alpha, shard count within ranges specified)
- Implementation of synthetic distractor injection (c_d tuning)
- Confidence threshold calibration (T value within recommended T=0.70-0.90 range)
- Ordering of Cells A, B, C (Cell A first is the only constraint)

exp_dev does NOT own:
- Whether semantic sharding (Mitigation 3) is added to v2 spec (orchestrator/strategy decision)
- Revision of GOLD 5.0 production claims (orchestrator/verdict_handler decision)
- North-star demo scope (user/orchestrator decision)
