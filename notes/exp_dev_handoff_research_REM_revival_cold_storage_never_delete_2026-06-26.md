# exp_dev hand-off — research: REM revival cold-storage (never delete, only relocate + combine)

**Filed by:** research (Opus 4.7)
**Filed at:** 2026-06-26
**Trigger:** USER reframe of Cell B HARD_FAIL_DESTROYS_OLDER (3 schedules); companion research note `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

**Cross-file relationship:** This hand-off SUPERSEDES the delete-anything frame in `notes/exp_dev_handoff_research_gap4_brain_selective_homeostasis_2026-06-26.md`. The selective-homeostasis anchors (M1-M5) remain valid as in-W_active selectivity primitives; this hand-off adds the ARCHITECTURAL anchor (cold storage) that decouples capacity-management from the W_active matrix entirely. If TWO_TIER (in flight) lands HARD-PASS, dispatch ANCHOR_1 (cold storage) as the natural three-tier extension. If TWO_TIER lands HARD-FAIL, dispatch ANCHOR_1 anyway as the architectural pivot away from in-W destructive operations.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, cheapest decisive, USER reframe direct test)

- **Pointer:** `cold_storage_two_tier_no_combine_v1`
- **Substrate-product reading:** Replace Cell B's `W *= 0.99` (in-place destructive downscale) with W_active + W_cold architecture: every J_migrate=500 cycles, weights with staleness>K AND importance<I MOVE from W_active to W_cold (exact copy, no decay in cold). W_active gets norm-normalization (not multiplicative downscale) to bound ||W_active||_F. Retrieval queries W_active first; on refuse-gate fire, queries W_cold; on cold-hit, promotes back to W_active. NEVER deletes any weight. Brain-fidelity MEDIUM (engram relocation analog); database-precedent VALIDATED (HotRAP LSM-tree). Single-cell decisive test of the USER reframe.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if produces recall_oldest >= 0.70 at J=10000 (vs Cell B baseline ~0.20).
- **Why now:** USER reframe is the natural revival for Cell B's HARD_FAIL; cheapest of the 5 cold-storage cells; tests the architecture frame in isolation before adding combination complexity. ~3-4 CPU-hr local OR ~1-2 hr remote GPU.
- **P_deflated:** 0.50.
- **Reference for design context:** `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md` Section 3 + Section 4 Cell 1 + Section 6 pre-reg bands.

### ANCHOR_2 (rank-2, adds brain-fidelity combination)

- **Pointer:** `cold_storage_plus_combination_v1`
- **Substrate-product reading:** ANCHOR_1 + every J_combine=2500 cycles, hierarchical scan of W_cold for pairs with cosine > 0.85; merge to centroid + write to W_schema with evidence weight. Source W_cold entries MARKED-AS-CONSOLIDATED (kept for audit) but no longer primary-retrieved. Implements the SEDM "merge-and-recycle, never-delete" primitive at substrate scale. Adds Tse-Morris paradigm probe (held-out schema-consistent test set) for novel-instance generalization.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if generates >= 50 schema atoms AND novel-instance recall lifts by >= 5pts when W_schema queried alongside W_active.
- **Why now:** ONLY-IF ANCHOR_1 lands MIDDLE_BAND or HARD-PASS. Adds the brain's actual long-term consolidation step; lit-precedent SEDM (arxiv 2509.09498). ~6-8 CPU-hr.
- **P_deflated:** 0.40 (combination noise risk).
- **Reference for design context:** `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md` Section 3 schema-combination subsection + Section 4 Cell 2.

### ANCHOR_3 (rank-3, full three-tier brain architecture; load-bearing)

- **Pointer:** `three_tier_W_active_W_cold_W_schema_v1`
- **Substrate-product reading:** ANCHOR_1 + ANCHOR_2 + composes with TWO_TIER (W_active=W_young; W_old becomes warm cortical-schema tier; W_cold is the long archive) + composes with STC tagging from selective-homeostasis drill (STC tag = "do NOT migrate to cold"). Full three-tier query: every retrieval combines W_active + W_cold (refuse-gate fallback) + W_schema (prior bias). Long horizon J=20000 cycles tests indefinite ingest with brain-fidelity architecture.
- **Tier hint:** chain-grade-eligible IF HARD-PASS at J=20000 with recall_oldest >= 0.80 AND ||W_active||_F bounded AND W_schema atoms support novel-instance recall >= 0.70.
- **Why now:** ONLY-IF ANCHOR_2 lands HARD-PASS. Load-bearing test for L2 glass-box-LLM continual-ingest moat. ~10-12 CPU-hr local OR ~3-4 hr remote GPU.
- **P_deflated:** 0.30 (composition risk over 3 mechanisms; ordering interactions).
- **Reference for design context:** `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md` Section 4 Cell 3 + Section 8 cross-thread synthesis.

### ANCHOR_4 (rank-4, simpler architectural fallback)

- **Pointer:** `substrate_as_archive_partition_routed_v1`
- **Substrate-product reading:** Use substrate's EXISTING chain-grade partition routing (K=4096) for time-partitioned ingest. Each "epoch" of ingest writes to partition[t // EPOCH_SIZE]; retrieval queries top-K partitions by similarity. Old partitions never deleted, never downscaled; routing handles capacity. Simpler architectural test: does substrate's existing routing primitives handle indefinite ingest without any explicit cold-storage mechanism?
- **Tier hint:** MEASURED_MECHANISM if HARD-PASS; chain-grade-eligible if routing latency stays sub-linear in #partitions at J=10000.
- **Why now:** Fallback if ANCHOR_1 lands HARD-FAIL. Tests if the existing routing primitive is sufficient without new architecture. ~2-3 CPU-hr; cheapest of the 5.
- **P_deflated:** 0.40.
- **Reference for design context:** `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md` Section 4 Cell 4.

### ANCHOR_5 (rank-5, STC + cold storage composition)

- **Pointer:** `STC_plus_cold_storage_v1`
- **Substrate-product reading:** Explicit composition with M5 STC from `notes/exp_dev_handoff_research_gap4_brain_selective_homeostasis_2026-06-26.md`. STC tag T[i,j] = "do not migrate." Cold storage migration policy: weights with T=False AND staleness>K AND importance<I move to W_cold. PRP capture from STC bounded-protein-pool marks weights permanently persistent (T=True forever). Highest brain-fidelity of the 5; tests joint mechanism with selective homeostasis drill.
- **Tier hint:** chain-grade-eligible IF HARD-PASS individually AND composes additively with NREM replay.
- **Why now:** ONLY-IF ANCHOR_1 HARD-PASS AND STC anchor from selective-homeostasis drill HARD-PASS. Composes two unproven mechanisms; lower joint P; only worth dispatching after individual validation. ~5-7 CPU-hr.
- **P_deflated:** 0.35.
- **Reference for design context:** `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md` Section 4 Cell 5.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_REM_revival_cold_storage_never_delete_2026-06-26.md`
- Parent selective-homeostasis drill: `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md`
- Parent selective-homeostasis hand-off: `notes/exp_dev_handoff_research_gap4_brain_selective_homeostasis_2026-06-26.md`
- Sibling TWO_TIER hand-off (in flight): `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md`
- TWO_TIER DISPATCHED status: `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`
- Brain CLS drill: `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`
- Cell A NREM replay (MIDDLE_BAND ledger entry): substrate cert_ledger.jsonl
- Cell B REM homeostasis HARD_FAIL_DESTROYS_OLDER (3 schedules): substrate cert_ledger.jsonl

---

## Contract

This hand-off file does NOT design experiments. Cell-author owns:
- Experiment design (hyperparameters K_threshold / I_threshold / J_migrate / J_combine / cosine_merge_threshold)
- Pre-reg envelope-fail-band derivation (per [[feedback-envelope-fail-bands]])
- Smoke test (per [[feedback-cell-author-smoke]]) — IMPORTANT: smoke MUST verify cold storage growth-rate prediction (linear, ~0.5 entries/cycle) AND W_active normalization stability BEFORE launching full ingest
- Harness wiring (META_M7 LM-eval not relevant; sequence-eval bands per substrate cert architecture C0-C6; multi-task discriminator with task-A/B/C labeled by ingest cycle)
- Post-ship REMOTE VERIFY (per [[feedback-post-ship-verify]])
- Self-test (per [[feedback-formula-selftests]])
- GPU dispatch route via hdi_orchestrator if N_DIM >= 8192 OR M >= 100k (per Fix #24)

Compute estimates are research's best guess; cell-author re-derives from harness reality.

---

## Autonomy declaration

This hand-off file is structural feed from research to exp_dev. exp_dev auto-discovers it on emergency-refill cycles (scan `notes/exp_dev_handoff_*.md` sorted by mtime). Research filing this file does NOT obligate exp_dev to ship in any specific order; exp_dev applies its own pause-flag check, queue-state inspection, GPU-routing rule (Fix #24), and pre-dispatch verify-the-referent gate (Fix #26) before picking up any anchor.

**Dispatch ordering recommendation**:

1. **First**: ANCHOR_1 cold_storage_two_tier_no_combine_v1 — cheapest decisive; tests the USER reframe in isolation.
2. **Conditional on ANCHOR_1 HARD-PASS or MIDDLE**: ANCHOR_2 cold_storage_plus_combination_v1 — adds brain-fidelity combination.
3. **Conditional on ANCHOR_2 HARD-PASS**: ANCHOR_3 three_tier — load-bearing for L2 moat.
4. **Conditional on ANCHOR_1 HARD-FAIL**: ANCHOR_4 substrate_as_archive_partition_routed — architectural fallback.
5. **Conditional on ANCHOR_1 HARD-PASS AND STC parent HARD-PASS**: ANCHOR_5 STC_plus_cold — joint composition test.

**Compose-with-in-flight ordering note**: TWO_TIER (in flight) and ANCHOR_1 are NOT redundant — TWO_TIER is W_young / W_old promotion (warm tier separation); ANCHOR_1 adds W_cold as a THIRD tier that handles the long tail with never-decay semantics. If TWO_TIER lands HARD-PASS, ANCHOR_1 extends it. If TWO_TIER lands HARD-FAIL, ANCHOR_1 provides an alternative architectural decomposition that may succeed where TWO_TIER did not.

**The USER reframe is mathematically sound and brain-grounded** (5 independent lit-precedents: Liu Neuron 2024, Yang Nature 2025, Li 2017 NComms, HotRAP arxiv 2402.02070, SEDM arxiv 2509.09498). This is exp_dev-actionable IMMEDIATELY; ANCHOR_1 is the cheapest decisive single cell to start.
