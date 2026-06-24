# exp_dev hand-off — research: substrate 5-tier clock hierarchy implementation

**Filed:** 2026-06-23 by research sub-agent (Opus 4.7 1M).

**Trigger:** Research 2x deeper drill delivered (`notes/research_substrate_5_tier_clock_hierarchy_implementation_2x_drill_2026-06-23.md`). Filled WHAT/HOW/MEASURE gap on the parent timescale-ratio drill's "declare 5-tier clock" recommendation. Three actionable anchors emerged in dependency order; primary is a structural validation that GATES the parent drill's efficacy sweep.

**Pause state:** READ AT DISPATCH TIME — exp_dev checks `data/orchestrator_paused.flag` before any queue_add.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: exact N, exact M, exact V, exact seed count, queue choice (Tier A/B/C), anchor name spelling, ETA, smoke profile, FULL profile, exact threshold bands. Research does NOT specify numerical parameters beyond what's in the research note's pre-registration table.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): `substrate_clock_hierarchy_tier_activity_validation_v1`

- **Anchor pointer:** `notes/research_substrate_5_tier_clock_hierarchy_implementation_2x_drill_2026-06-23.md` Section L4 + Section "Cheap decisive test PRIMARY CELL"
- **Substrate-product reading:** structural validation cell — proves the 5-tier ClockHierarchy data structure works correctly (all tiers fire at correct cadence; no tier-collision; tier-gating directionality holds; write_count + cross_tier_read_count instruments fire). This is a PRECURSOR cell. It is NOT an efficacy cell. It gates the parent-drill efficacy sweep so the sweep results aren't confounded by implementation bugs.
- **Tier hint:** local queue (single-arm; ~5 min CPU; trivial cost).
- **Why now:** if this cell HARD_FAILs, the parent drill's 2×4 efficacy sweep would burn 30-45 min CPU on confounded results. Run THIS FIRST. P_deflated 0.80 — should pass cleanly if implementation is correct.

### Anchor 2 (SECONDARY; chains on Anchor 1 PASS): `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1`

- **Anchor pointer:** parent drill `notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md` Section "Cheap decisive test"
- **Substrate-product reading:** 2×4 factorial efficacy cell — discriminates TAU_NEG correction (T_1 tier) × N_REPLAY count (T_4 tier) simultaneously. This is the parent drill's primary efficacy test. ChAins on Anchor 1 because the clock-hierarchy implementation must be correct first.
- **Tier hint:** local queue OR remote_cpu (8 arms × 100k tokens at N=4096; ~30-45 min CPU).
- **Why now:** chains directly on Anchor 1; together they validate both the structural correctness AND the efficacy of the two highest-yield clock-tier corrections.

### Anchor 3 (TERTIARY; composability validation): `substrate_clock_hierarchy_t2_tagging_continual_learning_v1`

- **Anchor pointer:** `notes/research_substrate_5_tier_clock_hierarchy_implementation_2x_drill_2026-06-23.md` Section "Cheap decisive test TERTIARY CELL"
- **Substrate-product reading:** 3-arm cell testing whether the NEW T_2 (synaptic-tagging / E-LTP) tier actually lifts continual-learning retention at the α=0.5 cliff regime. Composes with c1 CLS-replay task already validated as PARTIAL. The HARD_PASS would convert "T_2 is a missing primitive" speculation into "T_2 is a load-bearing primitive."
- **Tier hint:** local queue or remote_cpu (3 arms; ~15-20 min CPU).
- **Why now:** Tests one of the NEW unlocks (T_2 tagging) the clock hierarchy proposes. If HARD_FAIL, T_2 tagging is structural-orthogonal but not capability-load-bearing — still good to know; reduces priority of subsequent T_2-related work. If HARD_PASS, T_2 becomes a chain-grade-eligible novel primitive.

---

## Context pointers (file paths, not summaries)

- **This drill's research note:** `d:/AI/hd-instrument/notes/research_substrate_5_tier_clock_hierarchy_implementation_2x_drill_2026-06-23.md` (contains: per-tier table, ClockHierarchy dataclass pseudocode, measurement protocol, falsifiable predictions, citations)
- **Parent timescale drill:** `d:/AI/hd-instrument/notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md` (5-tier declaration; TAU_NEG correction; multi-pass replay; pre-registered HARD_PASS bands for the 2×4 efficacy cell)
- **Sibling brain drills:**
  - `d:/AI/hd-instrument/notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md` (CLS dual-store; 1:1 generative replay)
  - `d:/AI/hd-instrument/notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (compressed-sequence binding; prioritized-replay; consolidation-phase gating)
- **Substrate empirical anchors:**
  - `d:/AI/hd-instrument/notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md` (c1 PARTIAL — α=0.5 cliff under codebook-NN)
  - In-flight cell pointers: `dual_trace_RESCUE_corrected_baseline_v1` (overnight_queue); `cleanup_multi_iteration_v1` (af8c402990385f452)
- **CERT context:** CERT 586 c3 sequence-binding chain-grade; CERT 587 g1b autoregressive generation MEASURED_MECHANISM
- **Substrate primitives directory:** `d:/AI/hd-instrument/hdlab/` (existing: sequence_memory, kg_traversal, multi_hop, whitening, char_trigram_encoder, generation, predictive_coding, iterative_attractor, modulators — the ClockHierarchy would be a NEW module `hdlab/clock_hierarchy.py`)

---

## Contract section

- Anchor 1 is GATED by exp_dev's smoke-test profile passing on the new `ClockHierarchy` dataclass implementation; exp_dev confirms via `--self-test` before any FULL run.
- Anchor 2 is GATED by Anchor 1 HARD_PASS; do NOT dispatch Anchor 2 if Anchor 1 HARD_FAILs.
- Anchor 3 is INDEPENDENT of Anchors 1 + 2; can be dispatched in parallel with Anchor 1 if exp_dev has bandwidth.
- All anchors pre-registered with HARD_PASS / HARD_FAIL bands in the parent + this research note; bands are sacrosanct per [[feedback-negativity-bias]].
- All anchors comply with substrate-only-decode discipline (no LLM forward calls at inference; only at offline encoder ingest if applicable).
- exp_dev MUST follow Fix #20 (no `2>&1 | tail -N` pipe-deadlock subprocess monitoring in spawns) and Fix #21 (poll filesystem for landings; spawn notifications insufficient).
- exp_dev MUST follow Fix #28 (verify per-arm metrics.json before any cross-cell convergence claim; do NOT trust verdict_msg summary alone).
- exp_dev MUST follow Fix #26 (run `tools/predispatch_check.py <anchor>` before each spawn — checks for duplicate dispatches + recent HARD_FAIL re-dispatches).

## Autonomy declaration

exp_dev decides:
- Exact dispatch order (Anchor 1 must precede Anchor 2; Anchor 3 can be parallel-or-serial per bandwidth).
- Queue routing per Tier A/B/C policy (`agents/exp_dev.md` Section 0).
- Numerical parameter choices within the research note's pre-registered bands (e.g., exact N_TRAIN within the 10^5 ballpark; exact seed count >= 3).
- Smoke-test profile design (per Fix #17 strict runtime measurement).
- Whether to defer Anchor 3 if Anchors 1 + 2 are already saturating the queue.
- Whether to consult Skunkworks for cert-tier classification AFTER results land (per Fix #28a recurring discipline — Skunkworks consistently correctly overrides Director by-construction-saturation).

If exp_dev sees any deviation from anchor intent (e.g., the substrate doesn't yet have a `ClockHierarchy` class at all; the implementation needs to be written first), exp_dev should ROUTE BACK to research with a clarifying note rather than improvising the implementation. The ClockHierarchy dataclass is sketched in the research note's L3 section but not implemented; exp_dev should either: (a) implement it as a fresh `hdlab/clock_hierarchy.py` module per the sketch, OR (b) route back to research for fuller spec.

---

End of hand-off.
