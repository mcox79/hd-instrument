# exp_dev hand-off -- research: conversation memory streaming consolidation hot-cold tiering 2x

**Filed:** 2026-06-11 by research sub-agent.

**Trigger:** 2x operational drill on multi-hour conversation memory mechanisms. Research note at
`notes/research_drill_conversation_memory_streaming_2x_2026-06-11.md`. Findings are
exp_dev-actionable: 3 Tier-0 local-CPU anchors (T0-A/B/C, <30 min wall, ~$0 each), 3 Tier-1
remote-CPU anchors, 1 Tier-2 remote-GPU anchor, with sequencing rule that gates higher tiers
on T0-A outcome.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

**Pause state:** check `data/orchestrator_paused.flag` before queue-add operations.

---

## Anchor candidates (rank-ordered by cost and readiness)

### 1. T0-A: ONLINE-STREAMING-10K (Tier-0 local CPU -- cheapest decisive test)

- Anchor pointer: research note Part V, T0-A; "Cheap decisive test" section
- Substrate-product reading: 10,000-turn synthetic conversation, D-ECR eviction, recall@1 at
  lag 100/500/1000/5000. This is the single gate for all downstream conversation-memory claims.
  If recall@1 > 0.85 at 1000-turn lag: product claim "handles multi-hour conversation" is
  empirically supportable. If < 0.60: capacity is the binding constraint before any claims.
- Tier hint: local CPU queue (pure numpy, no encoder). Wall < 10 min. Cost ~$0.
- Why now: cheapest definitive gate; blocks all other streaming consolidation experiments.
  D-ECR eviction already verified (cycle 229); this is first time tested at 10K-turn scale.

### 2. T0-B: LRU-VS-DECR-EVICTION (Tier-0 local CPU)

- Anchor pointer: research note Part IV Path 6 + Part V T0-B
- Substrate-product reading: same 10K-turn setup as T0-A; compare LRU vs D-ECR eviction at
  each lag depth. Determines whether access-pattern-aware eviction materially outperforms the
  current D-ECR baseline. If LRU > D-ECR by > 0.03 at 5000-turn lag: swap default eviction.
- Tier hint: local CPU queue. Wall < 15 min. Cost ~$0.
- Why now: pairs naturally with T0-A; both pure numpy, can run in same batch.

### 3. T0-C: TOPIC-BOUNDARY-DETECTOR (Tier-0 local CPU)

- Anchor pointer: research note Part IV Path 3 + Part V T0-C
- Substrate-product reading: inject known topic boundaries in synthetic turn sequence; test
  whether cosine-shift detector fires within +/-3 turns of true boundary. No recall test.
  This is the prerequisite for the topic-segmented consolidation path (Path 3).
- Tier hint: local CPU queue. Wall < 5 min. Cost ~$0.
- Why now: zero-cost; necessary before any topic-based consolidation experiment.

### 4. T1-A: HOT-COLD-TWO-W-TIER (Tier-1 remote CPU)

- Anchor pointer: research note Part IV Path 4 + Part V T1-A; MemOS MemLifecycle mapping
- Substrate-product reading: W_hot (small N) + W_cold (large N); access-frequency-driven
  promotion policy (EMA-based hotness signal); recall@1 at lag 100/1000/5000 from both tiers.
  HARD-PASS: hot-cold recall > single-W by > 0.05 AND latency < 2ms. If PASS: hot-cold tiering
  is the production architecture for multi-hour conversation; direct product shipping path.
- Tier hint: remote CPU queue (encoder needed). Wall ~45 min. Cost ~$1.
- Why now: gated on T0-A PASS; run after T0-A confirms baseline capacity is sufficient.

### 5. T1-B: DUAL-STORE-CLS (Tier-1 remote CPU)

- Anchor pointer: research note Part IV Path 9; CLS biology mapping
- Substrate-product reading: W_episodic (fast alpha) + W_semantic (slow alpha); separate
  retrieval for recent verbatim vs abstracted background. Tests biological CLS hypothesis
  in substrate. If W_semantic retrieves distinct content from W_episodic at 10K turns:
  opens dual-W conversation architecture.
- Tier hint: remote CPU queue. Wall ~30 min. Cost ~$0.50.
- Why now: biologically grounded; low cost; tests a novel mechanism.

### 6. T1-C: SUMMARY-ANCHOR (Tier-1 remote CPU + LLM API)

- Anchor pointer: research note Part IV Path 8 + Part V T1-C
- Substrate-product reading: every K_summary turns, LLM summary -> encoded anchor pattern ->
  reinforced write. Query at turn 1000 for facts from turns 1-100. HARD-PASS: > 0.80 key-fact
  recall via anchor mediation. This is the conversation-summary capability (Q5 in the task spec).
- Tier hint: remote CPU + LLM API call. Wall ~60 min. Cost ~$1.50.
- Why now: tests the highest-product-value path (conversation summary); gated on T0-C boundary
  detector working (topic anchors require reliable segmentation).

### 7. T2-A: ONLINE-VS-OFFLINE-BATCH (Tier-2 remote GPU -- definitive)

- Anchor pointer: research note Part IV Path 10 + Part V T2-A
- Substrate-product reading: 10,000-turn conversation with REAL encoder (Llama-3.2-1B + PCA
  whitening + real Wikipedia QA content). Three conditions: (1) pure online, (2) batch-consolidate
  every 500 turns, (3) idle-moment consolidation. HARD-PASS: online within 0.08 of offline-batch
  at 1000-turn lag = "zero-downtime always-on conversation memory" claim is locked.
  HARD-FAIL: online > 0.15 below offline = scheduled consolidation phase required.
- Tier hint: remote GPU queue. Wall ~2-4 hr. Cost ~$6-8.
- Why now: definitive product gate; run after T0+T1 confirm capacity and tier mechanisms work.
  DO NOT dispatch until T0-A shows recall >= 0.60 (if T0-A HARD-FAIL, T2-A is premature).

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_conversation_memory_streaming_2x_2026-06-11.md` -- this cycle's full
  drill output; all mechanism details, P_deflated, HARD-PASS/HARD-FAIL bands, citations
- `notes/research_drill_agentic_memory_layer_2x_2026-06-07.md` -- prior 2x drill; Pattern A-E
  agentic integration patterns; D-ECR eviction baseline reference
- `notes/substrate_capability_map.md` -- current cap_map; D-ECR eviction row, continual KV row
- `data/orchestrator_paused.flag` -- check before any queue-add

---

## Contract

exp_dev owns: anchor naming, N/M/K parameter selection, seed count, threshold band calibration,
queue routing (local/remote-CPU/remote-GPU), smoke gate design, full profile write, post-ship
remote verify, status_log entry.

Research owns: mechanism identification, P_deflated estimates, HARD-PASS/HARD-FAIL pre-registration,
field adjacency, citation verification.

---

## Autonomy declaration

exp_dev may dispatch T0-A, T0-B, T0-C immediately (local CPU, no cost, no pause gate).
T1 anchors require T0-A PASS (recall@1 >= 0.60 at 500-turn lag) before dispatch.
T2-A requires T0-A recall >= 0.60 AND T1-A run (hot-cold confirmed working).
If T0-A HARD-FAIL: file a routing note back to Research before any further dispatch.
