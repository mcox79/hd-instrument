# exp_dev hand-off -- research: Chain 3 Production Architecture (Drill 5 FINAL)

**Filed-by:** research sub-agent
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md
**Filed:** 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file identifies anchor candidates and
context pointers only. Experiment design is exp_dev's responsibility.

---

## Pause state

Experiments are subject to orchestrator pause gate (data/orchestrator_paused.flag).
Do not queue anchors if the flag file exists and orchestrator has not given explicit go.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): v1 K-Hop Smoke -- 3-Shard Binary Relay K=12
**Anchor pointer:** Cell 1 from research note Section 7
**Substrate-product reading:** The single test that falsifies or confirms the entire Chain 3
  production architecture. If cross-shard K-hop at K=12 fails with latency > 200 ms or routing
  errors > 0, the v1 build plan is blocked. If it passes (< 50 ms, 0 routing errors,
  coordinator < 500 LOC), GOLD 2.0 is empirically validated and v1 can start immediately.
**Tier hint:** CPU only; N=4,096; 3 shards; ~2h wall; $0 cost
**Why now:** Chain 3 GOLD findings are theoretically closed. This cell is the decisive
  empirical gate. Routing it first gets the most information per engineering hour.

Pre-reg bands (from research note Section 8):
  HARD-PASS: K=12 latency < 50 ms AND routing errors = 0 AND coordinator < 500 LOC
  MIDDLE-BAND: latency 50-200 ms (architecture works; needs v2 optimization)
  HARD-FAIL: latency > 200 ms OR routing errors > 0

---

### Anchor 2: LSH Two-Tier Fan-Out at S=100
**Anchor pointer:** Cell 2 from research note Section 7
**Substrate-product reading:** Validates that B_eff stays below 20 with LSH bucketing at
  S=100 shards. This is the architectural control lever for K_max (GOLD 3.0: SNR scales
  as 1/sqrt(B_eff * alpha)). If B_eff > 50, the v2 latency target (10 ms) is broken.
**Tier hint:** CPU; N=4,096; 100 shards; ~3h wall; $0 cost
**Why now:** Anchor 1 must complete first (validates routing layer that LSH sits above);
  Anchor 2 is the natural next gate in the v1->v2 progression.

Pre-reg bands:
  HARD-PASS: B_eff(recall=90%) < 20
  MIDDLE-BAND: B_eff 20-50 (LSH works but needs tuning)
  HARD-FAIL: B_eff > 50 (LSH degenerate; fan-out not controlled)

---

### Anchor 3: Sparse-KEY Intermediate Production Integration
**Anchor pointer:** Cell 3 from research note Section 7
**Substrate-product reading:** Empirically validates GOLD 4.0 (3.16x K_max improvement from
  sparse-KEY intermediates). Zero new code -- toggle alpha per hop using cycle 142 sparse-KEY.
  If K_max(sparse) < 1.1x K_max(dense), the primary mechanism behind v3 viability is not
  working in the real encoder.
**Tier hint:** CPU; 10 shards; ~4h wall; $0 cost
**Why now:** Can run in parallel with Anchor 2 (independent of LSH); depends only on
  Anchor 1 having confirmed routing layer correctness.

Pre-reg bands:
  HARD-PASS: success_rate(sparse, K=12) > 1.5x success_rate(dense, K=12)
  MIDDLE-BAND: 1.1x-1.5x (partial gain; some encoding mismatch)
  HARD-FAIL: K_max(sparse) < K_max(dense) (regression)

---

### Anchor 4: Hot-Shard Monitor Alert Validation
**Anchor pointer:** Cell 4 from research note Section 7
**Substrate-product reading:** Validates Component 6 (hot-shard read replicas) alerting
  infrastructure. Failure Mode 1 (hot-shard storm) is the most common production outage
  vector. Alert threshold calibration (10x median QPS) must be validated empirically.
**Tier hint:** CPU; 10 shards; ~1h wall; $0 cost
**Why now:** Lowest-priority of the 4 cells; can be queued after Anchors 1-3.

Pre-reg bands:
  HARD-PASS: alert fires within 30s of threshold breach; zero false positives on uniform traffic
  MIDDLE-BAND: alert fires > 60s (detection is slow but functional)
  HARD-FAIL: alert never fires despite 10x QPS imbalance

---

## Context pointers (file paths; not summaries)

- Research note (Drill 5): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md
- Prior drills:
    d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
    d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill2_2026-06-07.md
    d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
    d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill4_2026-06-07.md
- Phase 2 gold findings: d:/AI/hd-instrument/notes (see PHASE 2 5x CHAINS GOLD 2026-06-07.md in MEMORY.md index)
- Post-compaction brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07.md
- Cycle 142 sparse-KEY implementation: substrate codebase (alpha parameter per production line)
- Cycle 148 pseudoinverse lock: substrate codebase (write rule production-grade)

---

## Contract

This handoff transfers research findings to exp_dev for experiment design and queuing.
exp_dev owns: pre-reg parameter selection, script implementation, queue routing, smoke gates.
Research owns: theoretical basis, P_deflated estimates, hard-pass/hard-fail thresholds.
Thresholds above are from research note and are binding -- do not adjust ex-post.

## Autonomy declaration

exp_dev has full autonomy to:
  - Choose queue routing (CPU for all 4 cells; no GPU needed)
  - Set N (N=4,096 or N=8,192 for faster laptop runs; matches research note spec)
  - Sequence anchors 2-4 in any order after Anchor 1 completes
  - Combine Anchors 2+3 into a single run if they share infrastructure
  - Pause on any HARD-FAIL and escalate to orchestrator before continuing

exp_dev does NOT have autonomy to:
  - Change the HARD-FAIL thresholds without orchestrator/research sign-off
  - Run Anchor 2/3/4 before Anchor 1 completes (routing layer is a dependency)
  - Route to cloud GPU (these are CPU runs; cloud is not justified here)
