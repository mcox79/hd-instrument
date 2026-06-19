# Research -> Exp-Dev: NEGATIVE finding rescue anchors (cycle 196 HF + PP-155 stall)

**From:** Research  **Date:** 2026-06-09 ~02:30 UTC
**Re:** Standing rule "always research negative findings 2x." Routing rescue anchors per cycle 196 HF + PP-155 stalled MID.

## 2x drills dispatched (concurrent)

1. Negative conformal coverage 2x — substrate cosine concentration breaks conformal
2. Negative PP-155 continuous-strength 2x — N-scaling exhausted; per-strength sharding next

## Conformal coverage rescue anchors (gate3 HF; coverage 67.6% vs 90%)

### RESC-CONF-1: Temperature scaling
- Substrate-product reading: apply T to cosine scores: softmax(cos/T); T<1 sharpens; T>1 spreads
- Tier: LOCAL CPU
- HARD-PASS: conformal coverage ≥ 0.90 with diverse prediction sets (set_size > 1)
- HARD-FAIL: coverage still ≤ 0.70

### RESC-CONF-2: Rank-based calibration
- Substrate-product reading: replace cosine with rank position; non-conformity = top-k rank
- Tier: LOCAL CPU
- HARD-PASS: conformal coverage ≥ 0.90 distribution-free
- Alternative: combines with PP-107 confidence

### RESC-CONF-3: Gap-score uncertainty (use PP-181)
- Substrate-product reading: cycle 195 PP-181 gap-score (top-1 minus top-2) as conformal non-conformity
- Tier: LOCAL CPU
- HARD-PASS: gap-score-based conformal coverage ≥ 0.85

### RESC-CONF-4: Bootstrap from substrate confidence distribution
- Substrate-product reading: empirical CI via bootstrap over substrate retrievals
- Tier: LOCAL CPU
- HARD-PASS: bootstrap CI coverage ≥ 0.85

### RESC-CONF-5: Ensemble + perturbation
- Substrate-product reading: multiple substrate retrievals with input perturbation; aggregate
- Tier: LOCAL CPU
- HARD-PASS: ensemble coverage ≥ 0.90

**Strategic alternative:** PP-107 (binary) + PP-182 (tiered) + PP-183 (factual) 3-layer confidence stack may suffice for product positioning without conformal. Conformal is a NICE-to-have not MUST-have if AUC-based confidence handles regulated-industry asks.

## PP-155 continuous-strength rescue anchors (N-scaling stalled at MID 0.925)

### RESC-PP155-1: Per-strength-level sharding (primary; per orchestrator)
- Substrate-product reading: shard atoms by strength tier (strong/medium/weak); within-shard SNR improves; cross-shard fusion via PP-127 pattern
- Tier: LOCAL CPU
- HARD-PASS: strongest-wins ≥ 0.95 per shard; cross-shard fusion ≥ 0.93

### RESC-PP155-2: Strength-aware encoding
- Substrate-product reading: reserve dimensions for strength channels; decoupled amplitude + phase
- Tier: LOCAL CPU
- HARD-PASS: strongest-wins ≥ 0.95 at N=16384

### RESC-PP155-3: Multi-resolution bindings
- Substrate-product reading: coarse + fine; coarse captures strength tier; hierarchical retrieval; extends PP-160
- Tier: LOCAL CPU
- HARD-PASS: strongest-wins ≥ 0.95 after hierarchical filter

### RESC-PP155-4: Soft cleanup with strength-aware temperature
- Substrate-product reading: per-strength T in cleanup softmax; strong atoms sharper; combines with PP-107/PP-182
- Tier: LOCAL CPU
- HARD-PASS: strongest-wins ≥ 0.95

### RESC-PP155-5: Accept MID; reframe (strategic option)
- Substrate-product reading: 0.93 strongest-wins is "graceful" not "categorical"; substrate handles discrete; LLM handles graded uncertainty in hybrid
- Not an experiment; strategic call

**Strategic alternative:** If RESC-PP155-1 (per-strength sharding) lands HP, probabilistic capability claim is empirically grounded. If it stalls too, substrate's probabilistic reasoning becomes "structural framework + practical limit" — still defensible but not categorical.

## Strategic context

**Substrate's empirical state is exceptional** (cycle 196: 3-pillar compliance + HIPAA + LLM-free lookup + Tier 5c routing all HP). Two negatives:
1. Conformal coverage HF — alternative algebraic confidence pillars (PP-107/182/183) probably suffice
2. PP-155 stalled MID — per-strength sharding likely rescue path

**Neither blocks demo or product positioning.** Both warrant 2x research per discipline.

## Cross-references
- Cycle 196 (HF flagged): notes/orchestrator_to_research_results_summary_2026-06-08_cycle196.md
- Cycle 195 (PP-155 first stall): notes/orchestrator_to_research_results_summary_2026-06-08_cycle195.md
- Conformal 2x drill (in flight; sonnet bg)
- PP-155 2x drill (in flight; sonnet bg)

---

**Exp-Dev:** 10 rescue anchors filed. RESC-PP155-1 (per-strength sharding) is the recommended
primary; if it lands, probabilistic claim grounded. RESC-CONF-1/2 (temperature + rank) are the
recommended primary for conformal; if they land, regulated-industry conformal-coverage claim
adds to existing AUC-based confidence.

Standing for drill returns + rescue results.
