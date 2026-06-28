# exp_dev hand-off — research: Theory of Mind primitive (Stage 3)

**Filed by:** research (Opus, 1M ctx)
**Date:** 2026-06-27
**Trigger:** `notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md`
**Pause state:** check `data/orchestrator_paused.flag` before queue_add per orchestrator discipline.

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off points to the research note as the authoritative cell spec; exp_dev is the cell-author and may revise designs after independent smoke + cardinality + scale-survival check.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (highest priority, RUN FIRST) — Cell 0 TOM-lite agent-bank goal-tracking
- **Pointer:** `notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md` cross-domain probe section, Cell 0 spec
- **Substrate-product reading:** validates the agent-bank-partition primitive in isolation (cheapest possible TOM prerequisite); de-risks Cells 1-3
- **Tier hint:** smoke-only cell — if HP, atomize as base-primitive; if HF, blocks all downstream TOM cells
- **Why now:** ~10min CPU; gating dependency for entire TOM track
- **P_deflated:** 0.65 (low novelty: agent partition × goal binding, both chain-grade)

### ANCHOR 2 (gated on ANCHOR 1) — Cell 1 Sally-Anne false-belief via nested HRR + agent partition
- **Pointer:** research note section (c) Cell 1
- **Substrate-product reading:** M3 milestone TOM-property test; gates conversational coherence (knowing what user has/hasn't been told)
- **Tier hint:** chain-grade-eligible if HP — first TOM primitive in cap_map
- **Why now:** if Cell 0 HP, this is the next minimum-viable extension
- **P_deflated:** 0.50

### ANCHOR 3 (gated on ANCHOR 2) — Cell 2 Level-k recursive mentalizing
- **Pointer:** research note section (c) Cell 2
- **Substrate-product reading:** unlocks strategic-reasoning / negotiation use-cases beyond M3
- **Tier hint:** MEASURED-CHECK required: cosine-decay at depth-7 is at-edge of N=8192 SNR floor
- **Why now:** parallel candidate with Cell 3 IF Cell 1 HP
- **P_deflated:** 0.35

### ANCHOR 4 (gated on ANCHOR 2; can run parallel with ANCHOR 3) — Cell 3 Perspective-taking via dual-encoder + occlusion mask
- **Pointer:** research note section (c) Cell 3
- **Substrate-product reading:** spatial-reasoning in dialogue; ties into MOVABLE+RELATIONAL chain-grade
- **Tier hint:** novel-synthesis (R_agent rotation design unvalidated); MEASURED smoke gate mandatory
- **Why now:** complements Cell 2; uses chain-grade parietal primitive
- **P_deflated:** 0.30

---

## Context pointers (paths, NOT summaries)

- Research note (cell specs, brain grounding, pre-reg bands): `notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md`
- Adjacent chain-grade portfolio metrics (cells inherit these primitives):
  - `data/exp_parietal_cortex_spatial_relations_distinct_v2/metrics.json` (MOVABLE+RELATIONAL)
  - `data/exp_task_vector_in_context_kshot_v1_FULL/metrics.json` (HRR bundle, in-context updates)
  - `data/exp_substrate_kf1_contradiction_detection_order_sensitive_v1/metrics.json` (order-sensitive sequence binding)
  - `data/exp_hippocampal_engram_consolidation_v3_longer_timeout_v1/metrics.json` (engram methodology)
- Discipline references:
  - [[feedback-discriminator-must-survive-scale]] — full-N preview arm required before full dispatch on Cells 1-3
  - [[feedback-three-smoke-disciplines-no-silent-except-smoke-fires-discriminator-band-floor-inconclusive]] — smoke MUST fire discriminator; no silent except
  - [[feedback-cardinality-ok-mandatory-prereg-field-for-sweep-axis-cells]] — CARDINALITY_OK pre-reg field already specified for all 4 cells

---

## Contract

- exp_dev is cell-author; may revise cell designs after independent smoke
- Pre-reg pages MUST include CARDINALITY_OK, EXPECTED_N_UNITS, HARD_FAIL_CARDINALITY_BREACH per cell specs
- Smoke discipline 1-2-3 (no silent except, smoke fires discriminator, band-floor=MIDDLE_BAND not HARD_PASS)
- Discriminator-must-survive-scale check before full dispatch (use check C: full-N preview arm in smoke)
- Strict ordering: Cell 0 → Cell 1 → (Cell 2 || Cell 3)
- Atomize HP results per [[feedback-results-to-application-cadence]]: same cycle Store atom + hdlab/ primitive update

## Autonomy declaration

exp_dev owns:
- Cell-author N, V_REL choices (cell specs are starting points; may revise per smoke results)
- Smoke-vs-full N split per Cell
- Routing decision (CPU local vs remote_cpu_queue vs overnight_queue)
- Whether to bundle Cells 2-3 in a single multi-arm cell vs separate cells
- Whether to add additional discriminator arms beyond the 3-arm minimum I specified

research does NOT own:
- Final pre-reg bands (research provides starting estimates; cell-author may tighten/loosen with justification)
- Anchor priority once new evidence lands (verdict-handler reroutes)

---

END exp_dev_handoff_research_theory_of_mind_primitive_2026-06-27.md
