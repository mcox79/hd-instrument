# exp_dev hand-off -- research: GAP 4 continual 5x drill (5000+ cycles with repair)

**Filed by:** research (Opus)
**Filed at:** 2026-06-26
**Trigger:** Director-initiated deep drill on GAP 4 long-term continual operation; companion to research note `notes/research_gap4_continual_5x_drill_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, highest yield, lowest substrate-distance)

- **Pointer:** `gap4_two_tier_generational_W_v1`
- **Substrate-product reading:** Add a SECOND W matrix (W_old, same dimensions as W) alongside the existing W. Periodically (every K_promote cycles) PROMOTE top-tau-fraction entries from W_young -> W_old by importance score; decay W_young after promotion. The architecture is convergent across 4 disparate fields (JVM generational GC; RocksDB LSM leveled compaction; immune-system germinal-center maturation; brain hippocampus-cortex consolidation) -- each independently arrived at the same factorization. Substrate has only single-tier today; this is the missing primitive ("promotion") for decade-scale continual operation.
- **Tier hint:** likely MEASURED_MECHANISM at first land (novel composition); chain-grade-eligible if HARD-PASS replicates at N_DIM=32768 production-scale in Phase 2.
- **Why now:** GAP 4 is L2-vision-critical (glass-box-LLM lifelong learner precondition); current substrate caps at ~200 cycles in production-anchor regime; Cell A NREM replay (already pending) provides REPLAY but no DESTINATION; TWO_TIER provides destination. Compute cheap (~3 CPU-hr). Decisive single-cell test against a8 anchor.
- **P_deflated:** 0.50 (cap on novel-synthesis applied).
- **Reference for design context:** `notes/research_gap4_continual_5x_drill_2026-06-26.md` Section "Cheap decisive test" + Prediction 1.

### ANCHOR_2 (rank-2, composes with rank-1 at trivial cost)

- **Pointer:** `gap4_bcm_metaplasticity_threshold_gate_v1`
- **Substrate-product reading:** BCM (Bienenstock-Cooper-Munro) sliding-threshold gating of new Hebbian writes -- per-weight theta_M = EWMA of |w|^2; writes above threshold trigger potentiation; writes below trigger depression. This is the metaplasticity layer the substrate doesn't have. Differs from SNAP (Cell B sibling) because the threshold ADAPTS to recent activity rather than being a static sigmoid. Substrate-native: W stats already computable.
- **Tier hint:** MEASURED_MECHANISM expected; cleanly composes with ANCHOR_1.
- **Why now:** Cost ~2 CPU-hr; predicted to multiplicatively extend TWO_TIER usable alpha.
- **P_deflated:** 0.40.

### ANCHOR_3 (rank-3, contingent path if ANCHOR_1 fails)

- **Pointer:** `gap4_neurogenesis_capacity_refresh_v1`
- **Substrate-product reading:** Periodically allocate FRESH N_DIM dimensions (W expansion); new patterns written exclusively to fresh dimensions for a maturation window; old patterns inhabit old dimensions. Biological analog: adult dentate gyrus neurogenesis (~700 cells/day in human; Aimone-Gage). Engineering analog: immune-system clonal expansion. Breaks the alpha-cliff by extending the denominator of alpha = M / N_DIM rather than managing M.
- **Tier hint:** MEASURED_MECHANISM if HARD-PASS.
- **Why now:** ONLY-IF ANCHOR_1 HARD-FAIL. Path divergence: TWO_TIER is "storage segregation"; neurogenesis is "capacity expansion." Two genuinely-different fix classes.
- **P_deflated:** 0.35.

### ANCHOR_4 (rank-4, generalizes ANCHOR_1)

- **Pointer:** `gap4_lsm_leveled_compaction_W_v1`
- **Substrate-product reading:** Generalize ANCHOR_1 from 2 tiers to 3+ tiers (W_L0 / W_L1 / W_L2 ...), with size-tiered or leveled merge strategy from RocksDB/LevelDB. Tests whether RocksDB's 5-7-level architecture (with its write-amplification vs read-latency tradeoff) buys further headroom beyond 2 tiers. ONLY-IF ANCHOR_1 HARD-PASS.
- **Tier hint:** MEASURED_MECHANISM.
- **P_deflated:** 0.35.

### ANCHOR_5 (rank-5, fundamentally different mechanism class -- theoretical anchor)

- **Pointer:** `gap4_lyapunov_OU_mean_reversion_v1`
- **Substrate-product reading:** Add a mean-reverting term to the W update rule: dW/dt = (Hebbian-update) - k*(W - W*) + noise, where W* is a slowly-updated prototype (long EWMA of W). Provably bounded drift (Ornstein-Uhlenbeck stationary distribution) under continual operation. No replay needed; one-line update modification. Provides theoretical anchor (Markov-chain stationary distribution; Doeblin coupling bound on mixing time).
- **Tier hint:** if HARD-PASS, candidate chain-grade by providing PROVABLE bounded forgetting (cert-grade theoretical result).
- **Why now:** orthogonal-mechanism class to ANCHOR_1 through 4 (mean-reversion vs segregation); cheap (~2 CPU-hr); analytically tractable.
- **P_deflated:** 0.35.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Companion brain CLS drill: `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`
- Companion brain SWR drill: `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md`
- Continual-learning architectural revival: `notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md`
- Gap-map transfer META: `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`
- Cell A NREM replay context: `notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md`
- Timeout-class disciplines (D1/D2 mandatory for long cells): `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md`
- Prior continual-write production anchor cert: refer to ledger row for `substrate_continual_kv_n32768_120_sessions`
- a8 baseline anchor: refer to ledger row for `exp_a8_continual_writes_no_catastrophic_forgetting_v1`

---

## Contract section

This hand-off is informational. Cell-author retains:
- experiment design authority (envelope-fail-bands, smoke design, harness wiring)
- pre-reg HARD-PASS / HARD-FAIL threshold authorship
- skip-smoke / smoke-yes decision per substrate-native vet
- dispatch queue selection (overnight_queue vs remote_cpu_queue) per Fix #24 GPU dispatch rules and runtime measurement strict (Fix #17)
- predispatch_check.py verify-the-referent gate (Fix #26)
- mandatory schema-vet + atexit partial-results + per-seed checkpoint for 5000-cycle horizon (D1/D2 from timeout drill)

Research role: literature provided; substrate-mapping articulated; ranked priority surfaced. Cell-author may RE-RANK based on substrate-state at pickup (queue depth, recent verdicts, fleet-waiting state).

---

## Autonomy declaration

Cell-author has FULL autonomy to:
- pick which of the 5 anchors to ship first (or alternate order)
- defer / skip any anchor that conflicts with current fleet priorities
- compose anchors differently than the research note suggests (e.g., TWO_TIER + neurogenesis hybrid)
- run smoke at smaller J than 5000 before full ingest to anchor wall-time estimate
- decide N_DIM (research note recommended 4096 for Phase 1; if production-scale needed first, choose 32768)
- refuse the entire drill if substrate-state at pickup contradicts the research's premise (e.g., if Cell A landed HARD-PASS in interval and a8 anchor is obsoleted)
- escalate to USER if any anchor exceeds expected compute envelope (>10 CPU-hr Phase 1).

Pre-registered HARD-FAIL routes (per research note Section "Prediction 4") provide the rescue paths if ANCHOR_1 fails.

---

-- Research (Opus). Hand-off filed structurally per [[feedback-15th-rule]] and exp_dev's hand-off autodiscovery on emergency-refill cycles.
