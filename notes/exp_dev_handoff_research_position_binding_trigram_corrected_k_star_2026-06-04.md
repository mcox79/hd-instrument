# exp_dev hand-off -- research: position-binding symmetric W trigram corrected K* mechanism

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** research note d:/AI/hd-instrument/notes/research_drill_position_binding_symmetric_w_trigram_explanation_2x_2026-06-04.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching any queue_add.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT
+ AUTONOMY only. Exp_dev determines anchor names, sweep grids, threshold formulas, queue
choice, and ETA autonomously. Do not encode those here.

---

## Anchor Candidates (rank-ordered)

### 1. K=3 Trigram Synthetic-Uniform Ablation (HIGHEST PRIORITY)

**Anchor pointer:** K=3 trigram at V=70 N=4096, corpus = synthetic uniform-random chars
(vs natural language corpus used in E1 HP run).

**Substrate-product reading:** If uniform-random chars FAIL (gap < 0.5 nats) while natural
language PASSES (confirmed by E1 HP, +1.291 nats), this CONFIRMS the corrected mechanism:
the substrate's trigram success is driven by Zipf demand deflation in natural language, not
by raw capacity exceeding K*=2.47. This narrows the product scope to natural-language-
distributed inputs and is actionable for capability claims.

**Tier hint:** CPU-feasible smoke run (N=512 first); full at N=4096. Expected wall: short.
ASCII-only in outputs per [[feedback-ascii-only-in-scripts]].

**Why now:** E1 HP with gap +1.291 nats is a strong signal but an unexplained one without
this ablation. The corrected mechanism (Zipf demand deflation) requires this ablation to
be confirmed, else the explanation is speculative.

---

### 2. K=3 Trigram V=512 Natural Language (BOUNDARY TEST)

**Anchor pointer:** Same position-binding + symmetric Hebbian write, but V=512 vocabulary
(word-level or expanded char set), K=3 trigram, N=4096.

**Substrate-product reading:** Corrected formula predicts HARD_FAIL (effective context demand
V_eff^2 ~ 45^2 = 2025 >> alpha_c*N = 565) because Zipf deflation is weaker at larger V.
If this fails as predicted, it validates K*_corr(V, N, rho, beta) formula as the correct
scaling law and confirms V=70 is in a special regime.

**Tier hint:** GPU or remote CPU. V=512 codebook at N=4096 is heavier than V=70.

**Why now:** Confirms that the corrected formula is a V-sensitive boundary, not a flat
expansion of the ceiling. Product implications: V=70 char-LM may be a sweet spot; larger
vocabularies may need sparsification.

---

### 3. K=4 Trigram at N=8192 Natural Language (CEILING EXTENSION)

**Anchor pointer:** K=4 (4-gram) char-LM at V=70 natural language, N=8192.

**Substrate-product reading:** Corrected formula predicts K*_corr ~ 3.97 at N=4096 and
~4.33 at N=8192. K=4 at N=8192 is near the borderline (predicted: MIDDLE_BAND or soft HP).
If HP, it confirms K*_corr extends to K=4 and the product roadmap includes 4-gram modeling.
If HF, the ceiling is confirmed at K=3 and sparsification is needed for K=4+.

**Tier hint:** GPU (N=8192 is heavier). Pre-reg envelope-fail bands per formula-selftests.

**Why now:** E1 HP opens the question of whether the ceiling is truly K~4 (corrected) or
still K~3 (conservative). K=4 at N=8192 is the decisive test for the corrected K*_corr
formula's K-dimension extension.

---

## Context Pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_position_binding_symmetric_w_trigram_explanation_2x_2026-06-04.md
- Prior task-complexity ceiling drill: d:/AI/hd-instrument/notes/research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md
- Prior position-binding translation drill: d:/AI/hd-instrument/notes/research_drill_delinguistification_position_binding_2x_2026-06-04.md
- E1 HP empirical result: check data/exp_BundleE_E1/metrics.json (path per [[feedback-metrics-path-exp-prefix]])
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

Exp_dev owns: anchor naming, sweep grids (eta, N values, seed counts), threshold formulas,
HP/MID/HF numerical bounds, queue selection, ETA, and all pre-reg specifics.

Orchestrator owns: cap_map updates after verdicts.

Research owns: corrected K*_corr formula derivation and Zipf-mechanism interpretation.

This hand-off is informational. Exp_dev proceeds autonomously within pause-gate check.

## Autonomy Declaration

Exp_dev has full autonomy to:
- Accept, modify, or reject any of the 3 anchor candidates
- Sequence them in any order
- Combine into a single batch or dispatch separately
- Determine smoke thresholds and full-run parameters independently
- Add additional anchors not listed here if strategically warranted

Do not treat this hand-off as a binding instruction list.
