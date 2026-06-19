# exp_dev hand-off -- research: engineered importance subspace (3x)

**Filed:** 2026-06-11 by research sub-agent.

**Trigger:** Research drill on engineered importance subspace completed. Findings are directly exp_dev-actionable: 10 mechanisms identified with concrete test predictions, cheapest decisive test specified at 1-2 CPU hours, and 8 pre-registered HARD-PASS / HARD-FAIL predictions ready for empirical test.

**Cite research note:** `notes/research_drill_engineered_importance_3x_2026-06-11.md`

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-triggering experiments.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Null-space projection smoke -- importance tag protection

**Anchor pointer:** Research note section "Cheap decisive test" + mechanism M6 specification.

**Substrate-product reading:** KFAC-FIM null-space projection was the prior failed approach because there was no well-defined subspace in the data. This anchor tests the alternative: declare the subspace explicitly from atom importance scores and measure whether null-space projection protects important atoms during edit operations. If HP-1 and HP-3 both pass (sim >= 0.95 for CRITICAL atoms, >= 40% perturbation reduction), the mechanism is validated as a substrate primitive.

**Tier hint:** Local CPU. Purely numpy/torch. No GPU required. Research note estimates under 10 minutes.

**Why now:** This is the cheapest decisive test for the entire engineered-importance framework. It resolves the core mechanistic question (does null-space projection work with declared bundles?) before investing in the score-maintenance infrastructure. Run this first.

**Pre-registered bands:** HARD-PASS: sim(CRITICAL) >= 0.95 AND perturbation_reduction >= 40%. HARD-FAIL: sim(CRITICAL) < 0.85 OR perturbation_reduction < 10%.

---

### Anchor 2: Access-frequency importance score -- retention correlation

**Anchor pointer:** Research note mechanism M2, empirical test T2.

**Substrate-product reading:** Tests whether log-frequency is a valid importance proxy in the substrate (P_deflated = 0.60). If frequency correlates with retention at r >= 0.70 across 3 shards, the auto-computed score is validated and mechanisms M5 (combined score) and M7 (importance-aware refresh) can be built on it without further validation.

**Tier hint:** Local CPU or remote CPU. Requires a shard with tracked access history and known retention rates.

**Why now:** M2 is the foundation for M5 and M7. Validating it early prevents wasted implementation of combined-score infrastructure on a weak signal.

**Pre-registered bands:** HARD-PASS: r >= 0.70. HARD-FAIL: r < 0.40.

---

### Anchor 3: Importance-aware refresh vs. uniform refresh

**Anchor pointer:** Research note mechanism M7, empirical test T4.

**Substrate-product reading:** Tests whether priority-weighted refresh outperforms uniform refresh for atom retention. Maps directly to the K2 replay problem (importance-weighted replay vs. uniform replay). If HP-4 passes (important-atom decay <= 10% at T=1000 vs >= 35% for uniform), this becomes the recommended replay policy for K2 and all continual-learning experiments.

**Tier hint:** Remote CPU or local GPU (depends on shard size; research note says the test itself is CPU-native).

**Why now:** K2 multi-task replay is an open cap_map row. This anchor simultaneously validates mechanism M7 AND provides a concrete HP improvement path for K2. Double-purpose experiment.

**Pre-registered bands:** HARD-PASS: important-atom decay <= 10% at T=1000 with importance-weighted refresh. HARD-FAIL: uniform refresh matches or beats importance-weighted on important-atom retention.

---

### Anchor 4: Combined importance score -- signal composition

**Anchor pointer:** Research note mechanism M5, empirical test T6.

**Substrate-product reading:** Tests whether the four-signal combined score (tag + frequency + age + user) predicts retention better than any single signal alone. Validates the weighting scheme w_tag=0.35, w_freq=0.30, w_age=0.15, w_user=0.20 as reasonable defaults. If HARD-PASS, the combined score becomes the substrate's canonical importance primitive.

**Tier hint:** Local CPU. Pure analysis on existing data from anchors 1-2.

**Why now:** Should run after anchors 1 and 2 provide the individual signal baselines. Anchor 4 is the composition test.

**Pre-registered bands:** HARD-PASS: corr(combined, retention) > corr(best_single, retention). HARD-FAIL: combined score is dominated by a single signal with no additive value from others.

---

### Anchor 5: Per-shard importance routing -- two-shard isolation

**Anchor pointer:** Research note mechanism M8, empirical test T7.

**Substrate-product reading:** Tests the architectural claim that a separate importance shard (CRITICAL atoms isolated) shows lower edit perturbation than the mixed-tier shard. If HP-7 passes (30% lower perturbation), this validates the "importance shard" as a product primitive for persistent long-term memory. This is higher complexity than anchors 1-4 and should be deferred until those are resolved.

**Tier hint:** Remote CPU or GPU depending on shard scale.

**Why now:** Lowest priority of the five. Run after anchors 1-4 resolve the mechanism-level questions. The two-shard architecture adds implementation complexity that is only warranted if the simpler per-atom mechanisms (1-4) are validated first.

**Pre-registered bands:** HARD-PASS: perturbation(importance_shard) < 0.70 * perturbation(mixed_shard). HARD-FAIL: no measurable isolation benefit from two-shard architecture.

---

## Context pointers

- Research note (full): `notes/research_drill_engineered_importance_3x_2026-06-11.md`
- Null-space projection algorithm: see section "Null-space projection algorithm (full specification)" in research note
- Biology + LLM theory parallels: see sections "A. Biology" and "D. LLM theory" in research note
- K2 continual learning open row: existing cap_map and strategy decisions files
- Prior KFAC-FIM failure context: referenced in research note "Cross-thread synthesis" section

---

## Contract

- exp_dev owns ALL experiment design decisions (N, K, seed count, threshold calibration, queue routing).
- This hand-off provides mechanism pointers and pre-registered pass/fail bands; it does not constrain implementation approach.
- If anchor 1 HARD-FAILs (null-space projection does not protect important atoms with declared bundles), escalate to Research before proceeding with anchors 2-5, as the entire framework assumption may need revision.
- If anchor 1 passes, anchors 2-4 can run in parallel.

## Autonomy declaration

exp_dev: You own the full experiment design for each anchor above. The research note specifies mechanism logic and pre-registered bands. You decide queue choice, anchor naming, seed counts, N/M/K parameters, smoke thresholds, and dispatch order. The only constraint is: anchor 1 before anchor 5; anchors 2 and 3 can run in parallel with anchor 1.
