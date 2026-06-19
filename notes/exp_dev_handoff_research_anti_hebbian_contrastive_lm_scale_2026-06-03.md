# exp_dev hand-off -- research: anti-Hebbian contrastive associative-memory rules at LM scale

**Filed-by:** research sub-agent, 2026-06-03
**Trigger:** d:/AI/hd-instrument/notes/research_drill_anti_hebbian_contrastive_transformer_scale_2026-06-03.md
**Pause state:** honor data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic framing only. Exp_dev decides anchor design, sweep parameters, HF/HP numerical thresholds, queue assignments, and pre-reg bands autonomously.

---

## ANCHOR CANDIDATES (rank-ordered)

### 1. Anti-Hebbian ablation in 4-primitive training loop (HIGHEST PRIORITY)
**Anchor pointer:** 4-primitive gradient-free training loop (outer-product write + anti-Hebbian contrastive + hierarchical recurrent retrieval + stacked independent-W) at N=128, character-level PTB or wikitext-2. Run two conditions: anti-Hebbian ON vs anti-Hebbian OFF. Measure BPC at steps 100, 200, 500; ||W||_2 per layer; retrieval accuracy on held-out 50-pattern probe.
**Substrate-product reading:** The research drill pre-registers: if BPC(ON) > BPC(OFF) + 0.5 at step 200, anti-Hebbian is the load-bearing failure mode (shared capacity budget depletion). If BPC(ON) <= BPC(OFF) + 0.2 and ||W||_2 < 10x initial, anti-Hebbian is healthy at this scale. This is the decision gate for whether to invest in anti-Hebbian mitigation before the full LM probe.
**Tier hint:** CPU smoke, N=128, <2h. NOT a GPU job at this scale.
**Why now:** Research drill identified anti-Hebbian as the riskiest primitive in the 4-primitive loop. This ablation directly isolates whether the risk is real at minimal scale before investing in the larger N=1024+ probe.

### 2. Spectral norm monitoring probe during anti-Hebbian training
**Anchor pointer:** Add per-layer ||W||_2 (or Hutchinson Tr(W^2)) monitoring to anchor 1. Log every 50 steps. Identify whether growth is sub-linear (healthy), power-law (approaching capacity cliff), or exponential (bipartite breakdown from correlated inputs).
**Substrate-product reading:** Research pre-registration: ||W||_2 > 100x initial within 200 steps = HARD-FAIL (bipartite breakdown confirmed). This observable is the substrate-native discriminator between failure modes 2a (capacity depletion, slower spectral growth) and 2b (correlated-input breakdown, faster). Cheap add-on to anchor 1 -- same run, second observable.
**Tier hint:** CPU, zero additional cost beyond anchor 1 (logged during same run).
**Why now:** Spectral monitoring is also a product-relevant feature (live drift detection). Validating it as a failure-mode discriminator adds product value beyond the experiment itself.

### 3. Tsodyks-Feigelman sparse coding mitigation trial (CONDITIONAL on anchor 1 MIDDLE-BAND result)
**Anchor pointer:** If anchor 1 returns MIDDLE-BAND (BPC plateau after step 300, ||W||_2 growing sub-exponentially), dispatch a follow-up probe with sparse coding enforced on hidden layer (k-winners-take-all, k = 5% of N=128 = 6-7 active units per layer). Same architecture + anti-Hebbian. Measure whether BPC plateau is eliminated.
**Substrate-product reading:** Research prediction: sparse coding with a=0.05 extends effective alpha_c from ~0.138 to ~3.4 (25x improvement). If the MIDDLE-BAND result is capacity-cliff driven, sparse coding should restore healthy BPC improvement. If BPC still plateaus under sparse coding, the failure mode is bipartite breakdown (2b) or gradient degeneration (2c), not capacity depletion (2a) -- which has different remediation paths.
**Tier hint:** CPU smoke, same scale as anchor 1. Conditional dispatch only.
**Why now:** Tsodyks-Feigelman is the mitigation with strongest published evidence. If anchor 1 is MIDDLE-BAND, this is the cheapest confirmatory follow-up.

---

## CONTEXT POINTERS

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_anti_hebbian_contrastive_transformer_scale_2026-06-03.md
- Prior full-pipeline research: d:/AI/hd-instrument/notes/research_drill_full_pipeline_substrate_native_training_deep_dive_2026-06-03.md
- Prior full-pipeline handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_full_pipeline_substrate_native_training_2026-06-03.md
- Substrate non-eq stat-mech: project_substrate_non_eq_stat_mech_class_2026-05-27.md (in memory)
- SKAH-M class confirmation: project_substrate_skahm_class_confirmed_2026-05-27.md (in memory)
- Cap map: d:/AI/hd-instrument/data/cap_map.md

---

## CONTRACT

The research drill has delivered: (a) confirmation that no published LM-scale anti-Hebbian precedent exists (5-6 order-of-magnitude gap), (b) three theoretically grounded failure modes with closed-form capacity formulas, (c) rank-ordered mitigation strategies by evidence quality, (d) pre-registered failure signatures (BPC, ||W||_2, retrieval accuracy) as cheap observables for the decisive test, (e) P_deflated estimates per calibration penalty protocol.

Key finding: anti-Hebbian capacity budget is SHARED with positive patterns (alpha_eff = (P+Q)/N), meaning the capacity cliff is hit at half the corpus size of positive-only writing. This is the highest-probability failure mode (P~0.60) and is directly testable at N=128 in <2h.

P_deflated(anti-Hebbian works at 4-layer LM scale without modification) = 0.22.
P_deflated(anti-Hebbian works with sparse-coding mitigation) = 0.38.

## AUTONOMY DECLARATION

Exp_dev retains full autonomy over: anchor naming, sweep parameters, HF/HP numerical threshold values, queue selection (CPU vs GPU), pre-reg band formulas, N choices, step counts, and all implementation details. The context pointers and anchor candidates above are strategic inputs only.
