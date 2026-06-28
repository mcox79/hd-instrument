# exp_dev hand-off — research: long-context narrative coherence (>100 events) Stage 3

**Filed:** 2026-06-27 by research sub-agent (Opus 4.7 1M ctx)
**Trigger:** USER overnight 2x research drill, load-bearing M3 concern #3 (long-context narrative coherence); cell direction filed at `notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md`
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` at dispatch time
**Discipline:** Per [[feedback-no-experiment-design-in-prompts]] — anchor POINTERS only; exp_dev designs ALL of N_h/N_c/eta/K/seed-count/threshold-bands/queue/wall

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (TOP, P_deflated=0.45): `stage3_narrative_coherence_100event_5char_full_stack_v1`

- **Substrate-product reading:** integration test for Stage 3 — composes cortex_hippo_handoff (smoke HARD_PASS today seed 7) + sequence binding K=20 (chain-grade) + partition routing 10M (chain-grade @100k) + TWO_TIER generational W (HARD_PASS_PARTIAL drift_reduction=0.30) + event-boundary detector (cosine-shift) into a 100-event / 5-character narrative pipeline. Discriminator across 4 arms (FULL_STACK / NO_SEGMENT / FLAT_BASELINE / FORGET_EVERYTHING) on Q1 factual / Q2 coref / Q3 temporal / Q4 contradiction. The marquee M3-enabling cell of today's batch.
- **Tier hint:** likely local CPU or remote CPU; matmul-light (N_h=512, N_c=1024 per cortex_hippo handoff convention); no GPU requirement at this scale
- **Why now:** cortex_hippo_handoff smoke HARD_PASS LANDED today (M=400 FULL=1.000); all four primitives chain-grade; first true Stage-3 integration test; USER overnight priority

### ANCHOR 2 (P_deflated=0.40): `stage3_narrative_event_boundary_detector_only_v1`

- **Substrate-product reading:** de-risks the event-boundary primitive that ANCHOR 1 depends on. Cheaper cell; isolated test of cosine-shift detector vs ground-truth boundaries. ARM_FIXED_BUDGET baseline; ARM_LLM_SUMMARIZER ceiling.
- **Tier hint:** local CPU; <30 min wall
- **Why now:** dispatch FIRST before ANCHOR 1 — if boundary detection fails at substrate cosine geometry, ANCHOR 1 needs redesign (use position-fixed K=10 boundaries) before dispatch

### ANCHOR 3 (P_deflated=0.35; reserve): `stage3_narrative_coreference_routing_only_v1`

- **Substrate-product reading:** isolated test of coref-as-partition-routing primitive; 100 mention-pairs classified into 5 partitions. ARM_CO_OCCURRENCE baseline; ARM_SCHEMA_PRIMED uses ultrametric prior.
- **Tier hint:** local CPU; <30 min wall
- **Why now:** hold in reserve; dispatch only if ANCHOR 1 HARD_FAILs on HF3 (coref router collapses) OR if ANCHOR 2 fails (need coref-only fallback path)

---

## Recommended dispatch sequence

1. ANCHOR 2 first (de-risks boundary detector; ~30 min)
2. If ANCHOR 2 boundary_precision >= 0.75 AND boundary_recall >= 0.75: dispatch ANCHOR 1 (the integration test; ~60 min)
3. If ANCHOR 1 lands HARD_PASS: marquee Stage-3 deliverable; auto-promote per atom + hdlab/ primitive update
4. If ANCHOR 1 lands MIDDLE_BAND: per-arm diagnostic identifies binding-constraint primitive
5. If ANCHOR 1 lands HARD_FAIL: structural rethink + dispatch ANCHOR 3 as fallback

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md` — full research drill with HEADLINE / discriminator / HARD_PASS+HARD_FAIL bands / CRLB pre-validation / citations
- `notes/research_drill_2x_cortex_hippo_handoff_2026-06-27.md` — A1 mechanism that landed smoke HARD_PASS today; load-bearing for ANCHOR 1
- `data/exp_cortex_hippo_handoff_sparse_DG_dense_cortex_v1/metrics.json` — smoke FULL=1.000 / NO_REPLAY=0.0025 / DIRECT=1.000 / gap=+0.998 at M=400, seed 7
- `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` — partition routing chain-grade @100k=0.9697; reference for 5-partition variant
- `data/exp_gap4_two_tier_generational_W_v1/metrics.json` — TWO_TIER generational W drift reduction 0.30; reference for fact-update arm
- `notes/research_drill_conversation_memory_streaming_2x_2026-06-11.md` — prior raw-recall drill (orthogonal axis; this drill adds entity-coherence)
- `notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md` — sibling multi-bank cell (today's batch)
- `notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27.md` — sibling time-cell cell (today's batch); Q3 in ANCHOR 1 composes on this if it lands
- `notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md` — sibling ultrametric-schema cell; ANCHOR 3 ARM_SCHEMA_PRIMED uses this
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md` — substrate state + CERT 614 + cortex state for spawn context

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD_PASS + HARD_FAIL bands BEFORE smoke (already drafted in research note §FALSIFIABLE PREDICTIONS)
- Self-test per [[feedback-formula-selftests]]
- §9 CRLB pre-validation already drafted in research note
- Multi-seed FULL on smoke clearance per Fix #17
- META_RULE_AF arms-must-differ — enforced via `assertion arm_score_variance > 0.05` at smoke
- META_RULE_AH atomic-write — tmp+rename for all metrics.json
- META_RULE_K — smoke must FIRE discriminator (not just verify cell runs); the 20-event / 3-character smoke must show arm separation
- DISCRIMINATOR-MUST-SURVIVE-SCALE — for sweep-axis (event count K=[20, 50, 100]) use Check A (smoke at full-N=100 with single seed) OR Check C (preview arm at full N in smoke)
- Encoding mechanism EXPLICIT: cortex_hippo_handoff encodes via consolidation (sparse hippo h_i -> fixed projection P -> slow Hebbian update to dense cortex W_cortex)
- Queue routing per Tier A/B/C in `agents/exp_dev.md`; cell is numpy-eligible; if exp_dev routes to remote, must verify cell is actually GPU-using per Fix #24 (if not torch.cuda, route to remote_cpu not overnight_queue per q_f5 incident)
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code
- status_log entry per anchor with `plain_language` + `importance`

---

## Autonomy declaration

exp_dev decides ALL of:
- Anchor name (suggested above; substitute as needed)
- N_h / N_c / N_partition / N_seq dimensions
- M event count (suggested 100 full / 20 smoke)
- Number of characters (suggested 5 full / 3 smoke)
- eta_c slow Hebbian rate (suggested 0.005 per cortex_hippo handoff convention)
- K sequence-binding within-episode depth (suggested ≤20 per chain-grade ceiling)
- N_replay sleep-phase cycles (suggested 5 per cortex_hippo handoff smoke)
- Event-boundary detection theta (suggested tunable; 0.5-0.7 cosine threshold)
- Seed count (suggested 5 for full; 1 for smoke)
- Threshold bands (suggested from research note §FALSIFIABLE PREDICTIONS; exp_dev may tighten)
- Queue choice (recommend local CPU or remote_cpu_queue; not GPU)
- ETA estimates
- Smoke profile + FULL profile
- Whether to bundle ANCHOR 1 + ANCHOR 2 dispatch or sequence them

If exp_dev wants to substitute a different anchor from the three above (e.g., scale ANCHOR 1 to 200 events / 10 characters first vs proposed 100/5), that's exp_dev's call. Research stands behind the COMPOSITION as the load-bearing claim; specific scale parameters are exp_dev's domain.

---

## Filed by

Research sub-agent (Opus 4.7 1M ctx), 2026-06-27, post 2x drill on long-context narrative coherence. Hand-off auto-discoverable by exp_dev emergency-refill scan of `notes/exp_dev_handoff_*.md`.
