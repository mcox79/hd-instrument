# exp_dev hand-off — research: KB BOUNDED-CAPACITY architecture (Wave 3; USER green-lit with vetting protocol)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26: "this sounds great, and exactly what we need for this. do it, and carefully vet how it works the first few times until we trust it." Prior context: USER raised the substrate-balloon concern; research proposed TWO_TIER + partition + coarse-grain + eviction architecture; USER ratified.

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off and DO NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS. exp_dev authors cells. Pre-reg bands LOAD-BEARING.

## CRITICAL DEPENDENCIES (mandatory gates — do NOT dispatch until all met)

This Wave 3 build is GATED on three prior anchors landing HARD_PASS. Each is in flight or queued:

1. **Wave 2 KB ANCHOR 1.5 coverage extension** — must HARD_PASS (loaded ALL source classes; deterministic re-ingest preserved); currently in flight via spawned hdi_exp_dev agent
2. **Wave 2 KB ANCHOR 2 query interface** — must HARD_PASS (substrate-KB returns trusted results above confidence floor; refuses cleanly on unknowns)
3. **Wave 1 cortex_E_tensor_separate_importance_v1** (cortex Anchor 1) — must HARD_PASS (per-atom E[i] tensor is the LOAD-BEARING signal for the TWO_TIER promotion criterion); currently in flight via spawned hdi_exp_dev agent

If any of these HARD_FAILs, Wave 3 design must be revisited before dispatch. Specifically:
- If E-tensor HARD_FAILs → promotion criterion needs alternative signal (likely retrieval-count-based fallback; flag for research re-drill)
- If query HARD_FAILs → no validated query interface to test capacity behavior against; build cannot be vetted
- If coverage HARD_FAILs → KB doesn't yet contain enough info to need bounded-capacity machinery

## Pivot frame (mandatory; per USER ratification)

This is the bounded-capacity architecture for the substrate-director-KB. The KB is the LOAD-BEARING tool that post-compaction-me uses to recover state. If the KB balloons unbounded, we hit substrate capacity limits and degrade silently. If we evict too aggressively, post-compaction-me loses critical context.

The 12 no-lock-in principles from the original KB handoff `notes/exp_dev_handoff_research_substrate_director_kb_dogfood_2026-06-26.md` REMAIN LOAD-BEARING. Specifically:
- Principle 1: filesystem stays canonical (eviction from substrate ≠ deletion from filesystem)
- Principle 2: wipe-and-rebuild safe (any architectural change can be tested by full wipe + re-ingest)
- Principle 6: read-only from Director (Director never directly writes to bounded-capacity machinery)

## Anchor candidates (5 anchors; each shipped SEPARATELY for individual vetting per USER directive)

USER directive: "carefully vet how it works the first few times until we trust it." So we do NOT bundle these into one cell. Each ships separately, smoke-tested individually, composed only after individual verdicts. ANCHOR 5 (vetting infrastructure) ships FIRST and remains active across the others.

### ANCHOR 5 (SHIPS FIRST — vetting infrastructure): kb_dual_store_audit_v1

- **Anchor pointer:** new cell + new tool `tools/director_kb_audit.py`
- **Substrate-product reading:** "dual-store comparison harness — every Director query simultaneously hits substrate-KB AND filesystem-grep; results compared; any mismatch logged to `data/director_kb_audit_log.jsonl` with timestamp + query + substrate result + filesystem result + reason; capacity metrics logged (per-tier atom count + utilization fraction + last-promotion + last-eviction events)"
- **Why FIRST:** USER directive load-bearing. Without dual-store comparison, we have no way to validate the bounded-capacity machinery is preserving important info. This is the LOAD-BEARING SAFETY mechanism.
- **Tier hint:** INFRASTRUCTURE cell; success criterion OPERATIONAL not CERT-bands
- **Arms (2 mandatory):**
  - ARM_DUAL_STORE_MATCH (run 100 known queries; verify substrate result matches filesystem grep result on at least 95%; mismatches logged with diagnosis)
  - ARM_AUDIT_LOG_INTEGRITY (verify audit log writes are durable, jsonl-parseable, complete; no race conditions on concurrent ingest+query)
- **Pre-reg success:** 100 queries dual-store-run cleanly; ≥95% match on substrate vs filesystem; audit log complete + parseable; zero crashes on concurrent ingest+query
- **Cost:** ~2-3 hr build; runs continuously thereafter as a wrapper around query interface
- **DEPENDENCY:** Wave 2 ANCHOR 2 query HARD_PASS (need query interface to wrap)

### ANCHOR 1: kb_partition_by_source_class_v1

- **Anchor pointer:** new cell extending `hdlab/director_kb.py`; modifies schema config to add per-source-class partition tag
- **Substrate-product reading:** "separate W matrix per source class — notes-W / memory-W / metrics-W / cert-W. Each bounded individually (configurable per partition). Query type routes to correct partition via existing chain-grade partition_routing primitive. Memory partition (USER directives) gets oversized allocation per load-bearing status."
- **Tier hint:** INFRASTRUCTURE cell
- **Arms (3 mandatory):**
  - ARM_SINGLE_W_BASELINE (current Wave 2 state; single W per KB; sanity rail)
  - ARM_PARTITIONED_W_EQUAL_CAPACITY (4 partitions; equal capacity per partition; tests routing correctness)
  - ARM_PARTITIONED_W_MEMORY_OVERSIZED (memory partition 4x size; tests USER-directive load-bearing preservation)
- **Pre-reg success:** ARM_PARTITIONED queries route correctly to source-class partition ≥98% of the time; cross-partition leakage <2%; total atom capacity = sum-of-partition-capacities (no overhead); ARM_PARTITIONED preserves all queries that ARM_SINGLE answered above confidence floor
- **Pre-reg failure:** routing accuracy <90% (partition leakage) OR ARM_PARTITIONED loses queries ARM_SINGLE answered (capacity regression) → REJECT
- **Cost:** ~3-4 hr build; local_cpu
- **Vetting on first 3 runs:** ARM_DUAL_STORE_MATCH (ANCHOR 5) must pass ≥95% during first 3 query batches post-deployment. If dual-store match drops below 95%, ROLLBACK to single-W.

### ANCHOR 2: kb_two_tier_promotion_v1

- **Anchor pointer:** new cell composing on chain-grade `exp_gap4_two_tier_generational_W_v1` primitive
- **Substrate-product reading:** "fast-tier W holds last 48-72h of new atoms (bounded ~1000 atoms); slow-tier W holds long-term consolidated. Promotion criterion: (atom has been queried ≥2 times) OR (atom is USER_DIRECTIVE — always promote). New content → fast. Promoted content → slow. Unpromoted fast-tier content rotates out as fast-tier capacity fills. Promotion criterion USES cortex_E_tensor signal (the per-atom retrieval-hit EWMA from Wave 1 ANCHOR 1)."
- **Tier hint:** INFRASTRUCTURE cell composing on chain-grade
- **Arms (3 mandatory):**
  - ARM_NO_TWO_TIER_BASELINE (single bounded W with naive eviction; sanity rail — must reproduce Wave 2 KB)
  - ARM_TWO_TIER_USER_DIRECTIVE_ALWAYS_PROMOTE (USER memory always promoted; queried-≥2x also promoted; rest rotates)
  - ARM_TWO_TIER_E_TENSOR_GATED_PROMOTION (uses cortex E-tensor signal explicitly as promotion criterion)
- **Pre-reg success:** USER_DIRECTIVE atoms retained ≥99.5% across 100 simulated days of synthetic ingest+query churn; queried-twice atoms retained ≥95%; non-queried-non-USER atoms rotated out cleanly at fast-tier capacity boundary; recall on USER directives ≥99% via slow-tier query
- **Pre-reg failure:** USER directive lost from substrate (retention <99%) — REJECT; recall on queried-twice atoms <80% — investigate before composing
- **Cost:** ~4-5 hr build; local_cpu
- **Vetting on first 3 runs:** ANCHOR 5 dual-store match ≥95% AND zero USER_DIRECTIVE loss verified across first 3 days of operation. If USER_DIRECTIVE loss detected → IMMEDIATE ROLLBACK + research investigation.

### ANCHOR 3: kb_coarse_grain_at_promotion_v1

- **Anchor pointer:** new cell composing on chain-grade SEMANTIC concept learner + chain-grade HRR binding
- **Substrate-product reading:** "at fast→slow promotion, use SEMANTIC concept learner to identify cluster membership; collapse similar atoms (cluster size ≥3 AND within-cluster cosine ≥0.85 AND same source class) into representative + residual codes. Representative = SEMANTIC cluster centroid + USER_DIRECTIVE tag (if any cluster member is USER_DIRECTIVE, representative inherits the tag). Residual codes preserve per-source-file pointers. Querying the cluster returns the representative + list of source-file pointers."
- **Tier hint:** INFRASTRUCTURE cell composing on chain-grade
- **Arms (3 mandatory):**
  - ARM_NO_COARSE_GRAIN_BASELINE (ANCHOR 2 TWO_TIER without coarse-graining; sanity rail)
  - ARM_COARSE_GRAIN_AT_PROMOTION (proposed mechanism)
  - ARM_RANDOM_CLUSTER_COLLAPSE (control — random clusters of same size collapsed; tests whether SEMANTIC CRITERION matters vs "any clustering helps")
- **Pre-reg success:** capacity_used in slow-tier drops by ≥30% via coarse-graining; recall on clustered concepts ≥0.85 via representative; recall on unclustered concepts ≥0.90; source-file-pointer chain works (can recover specific source file from cluster query); USER_DIRECTIVE atoms never collapsed with non-USER atoms (separation preserved)
- **Pre-reg failure:** recall on clustered concepts <0.70 (collapse destroys info) OR USER_DIRECTIVE silently mixed with non-USER atoms — REJECT
- **Cost:** ~5-6 hr build; local_cpu
- **Vetting on first 3 runs:** every coarse-grain event logged with cluster members + representative + reason. First 3 weeks operate with VERBOSE audit (every coarse-grain triggers a notification for human review). USER reviews first ~50 coarse-grain events before silent operation enabled.

### ANCHOR 4: kb_time_decay_eviction_with_reingest_v1

- **Anchor pointer:** new cell + tool `tools/director_kb_reingest_on_demand.py`
- **Substrate-product reading:** "per-atom last-queried timestamp; atoms not queried in N days (initially N=90) get evicted from substrate index. Filesystem source preserved (Principle 1). Query interface: if substrate refuses with low confidence AND filesystem grep finds relevant atom, ingest cell re-fetches on demand and adds back to fast-tier. So evicted ≠ forgotten; eviction is DEMOTION to cold storage."
- **Tier hint:** INFRASTRUCTURE cell
- **Arms (3 mandatory):**
  - ARM_NO_EVICTION_BASELINE (ANCHOR 2 + ANCHOR 3 without eviction; sanity rail)
  - ARM_TIME_DECAY_EVICTION (proposed mechanism with N=90 day cutoff initially)
  - ARM_REINGEST_ON_DEMAND (control — verify evicted atom can be re-fetched when filesystem-grep falls back finds it)
- **Pre-reg success:** eviction reduces total atom count by ≥20% over 90 simulated days of operation; re-ingest-on-demand re-fetches evicted atom in ≤30 sec when queried; USER_DIRECTIVE atoms NEVER evicted (retention 100%); recently-queried atoms (last 30 days) retention ≥99%
- **Pre-reg failure:** USER_DIRECTIVE evicted (any loss) OR re-ingest fails (<90% success on evicted-then-queried atoms) OR retention regression on recent atoms — REJECT
- **Cost:** ~4-5 hr build; local_cpu + scheduled-task for daily eviction sweep
- **Vetting on first 3 runs:** every eviction event logged. First 3 weeks operate with eviction policy DISABLED — only the audit (which atoms WOULD be evicted) runs. USER reviews proposed-evictions list before enabling actual eviction.

## Dispatch sequence (sequential, NOT parallel, per USER vetting directive)

USER explicitly wants careful vetting. Each anchor lands and is vetted for ≥3 trial runs before the next ships. This is sequential, not parallel.

**Wave 3a (ships first — safety infrastructure):**
- ANCHOR 5 dual-store audit (~2-3 hr build); MUST PASS 100-query match-rate ≥95% before any of 1-4 ships

**Wave 3b (parallel; ships after 5 passes vetting):**
- ANCHOR 1 partition-by-source (~3-4 hr; can ship in parallel with ANCHOR 2 once 5 passes)
- ANCHOR 2 TWO_TIER (~4-5 hr; gates on Wave 1 cortex E-tensor HARD_PASS for promotion criterion)

**Wave 3c (after 1+2 pass 3 trial runs each):**
- ANCHOR 3 coarse-grain (~5-6 hr; composes on 1+2)

**Wave 3d (after 3 passes 3 trial runs):**
- ANCHOR 4 time-decay eviction (~4-5 hr; composes on 1+2+3); eviction DISABLED initially (only audit runs); USER reviews proposed evictions before enabling

Each wave step has VETTING GATE before next wave. Dual-store audit (ANCHOR 5) runs continuously across all waves — if any anchor causes match-rate drop below 95% or USER_DIRECTIVE loss, immediate rollback.

## Vetting protocol (USER directive load-bearing)

USER said: "carefully vet how it works the first few times until we trust it."

**For each new anchor going live:**

1. **First 3 batches of queries (≥100 each):** ANCHOR 5 dual-store audit ACTIVE; match rate logged per batch; mismatches investigated before next batch
2. **First 3 promotion events** (for ANCHOR 2): every promotion logged with reason; promoted atom verified to be correctly retrievable from slow-tier
3. **First 50 coarse-grain events** (for ANCHOR 3): every event logged with cluster members + representative; USER reviews sample before silent operation enabled
4. **First 3 weeks of eviction proposals** (for ANCHOR 4): eviction DISABLED — only audit runs; USER reviews proposed-evictions list before enabling actual eviction
5. **USER_DIRECTIVE retention check:** every wave step verifies USER directive atoms retained at 100%. If ANY USER directive is silently dropped, IMMEDIATE ROLLBACK to prior state (Principle 2 wipe-and-rebuild safety enables this).
6. **Human-readable health dashboard:** `tools/director_kb_health.py` shows per-tier capacity utilization + promotion rate + coarse-grain rate + eviction rate + dual-store match rate; USER can inspect at any time

**Rollback discipline:** since filesystem is always canonical (Principle 1) and wipe-and-rebuild is safe (Principle 2), ANY problematic anchor can be rolled back by wiping the substrate-KB W and re-ingesting via Wave 2 ANCHOR 1.5 baseline. No data loss possible.

## Context pointers

- Original KB handoff (load-bearing context): `notes/exp_dev_handoff_research_substrate_director_kb_dogfood_2026-06-26.md`
- 12 no-lock-in principles: in original handoff section "No-lock-in architecture principles"
- USER bounded-capacity ratification: this conversation 2026-06-26 verbatim
- Chain-grade primitives this composes on:
  - TWO_TIER generational W: `data/exp_gap4_two_tier_generational_W_v1/metrics.json` (HARD_PASS today)
  - Partition routing M=10M: `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json`
  - SEMANTIC concept learner: `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json` (chain-grade 5/6 arms)
  - Refuse-gate V_REL=256: chain-grade
  - HRR binding: `hdlab/binding.py` chain-grade
- Cortex E-tensor cell (Wave 1 dependency; in flight): `notes/exp_dev_handoff_research_first_wave_7_compositional_understanding_USER_GREENLIT_2026-06-26.md` ANCHOR 1
- Wave 2 KB anchors (in flight): query + coverage + continuous-ingest

## Contract

- All 5 anchors preserve the 12 no-lock-in principles. If any design violates, route back to research.
- ANCHOR 5 audit infrastructure SHIPS FIRST and remains active across all subsequent anchors.
- USER_DIRECTIVE atoms NEVER evicted, NEVER coarse-grained with non-USER atoms, ALWAYS retained ≥99.5%. Load-bearing across all anchors.
- Sequential vetting per USER directive: do NOT ship multiple anchors in parallel beyond the wave structure above.
- Cell-author smoke per Fix #17; pre-flight Fix #26.
- Dispatch GATED on Wave 2 KB anchors HARD_PASS + Wave 1 cortex E-tensor HARD_PASS. Do not dispatch ANY of these 5 anchors until BOTH dependencies are confirmed.
- text8 / BPC / bigram-gap NOT relevant evals; USER pivot in force.
- Default tier MIDDLE per Fix #28.

## Autonomy declaration

exp_dev owns: cell authoring within research-note guidance; smoke gates; arm-design refinements; queue routing.

exp_dev does NOT own:
- Skipping ANCHOR 5 audit infrastructure (load-bearing per USER directive)
- Parallel dispatch of ANCHORS 1-4 (USER explicitly directed sequential vetting)
- Bypassing the dependency gates (Wave 2 + Wave 1 cortex E-tensor must HARD_PASS first)
- Reducing USER_DIRECTIVE retention threshold below 99.5%
- Enabling eviction (ANCHOR 4) before 3-week audit period + USER review of proposed evictions
- Re-defining the 12 no-lock-in principles

USER explicitly green-lit this build 2026-06-26 with "carefully vet how it works the first few times until we trust it." Vetting protocol is load-bearing; do NOT skip steps.

---

-- Research (Opus 4.7-1M)
