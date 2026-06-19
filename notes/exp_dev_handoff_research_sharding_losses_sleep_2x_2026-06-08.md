# exp_dev hand-off -- research: sharding losses + biology sleep 2x

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** Research drill on 5 sharding "losses" and biological sleep recovery mechanisms.
Research note: notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-modifying actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary (for context; exp_dev reads research note for detail)

The 5 sharding losses (inter-shard analogy, holistic context, cross-subject patterns,
higher-arity relations, set-of-subjects queries) have different tractability profiles.
Losses 3 and 5 (cross-subject patterns + set-of-subjects queries) are closable with
Mechanism B -- per-property inverted shard construction in sleep defrag -- which reuses
existing sleep-defrag primitive and VSA bundling, both validated. Loss 4 (higher-arity)
is closable via event-as-subject sharding using validated Pattern B d=10 (below d=16
ceiling). Losses 1 (analogy detection) and 2 (holistic context) are less tractable:
Loss 2 is a pseudo-loss (PP-126 scatter-gather already handles it); Loss 1 requires
role vocabulary normalization before structural signatures are useful.

---

## Anchor candidates (rank-ordered; exp_dev picks across queues per queue-depth directive)

### 1. Per-property inverted shard construction -- Mechanism B pre-test
  - Anchor pointer: research note Section "Loss 3 / Loss 5" + "Mechanism B" in cross-cutting.
  - Substrate-product reading: build per-property inverted shards during sleep defrag;
    verify that bundle of subject-ID vectors retrieves correct subject set for single-property
    category query. Closes Losses 3 and 5 simultaneously. Uses validated sleep-defrag scan
    (HP cycles 167+170) with new cross-shard collection phase.
  - Tier hint: local CPU (small-scale pre-test; 50-shard substrate; N=65536 production).
    Per [[feedback-small-scale-first-methodology]]: validate at tiny scale first.
  - Why now: HIGHEST PRIORITY. Cheapest mechanism (no new substrate primitives; builds on
    validated sleep defrag + VSA bundling). Closes two losses simultaneously. Research
    P_theoretical = 0.80; P_empirical = 0.60. The cheap decisive test in the research
    note specifies exactly this anchor at 50-shard scale.

### 2. Event shard Pattern B binding -- partial cue completion pre-test
  - Anchor pointer: research note Section "Loss 4 -- higher-arity relations" mechanism.
  - Substrate-product reading: store a 5-participant event fact using Pattern B at d=10
    binding depth (well below validated d=16 ceiling per PP-118 cycle 173). Test partial
    cue completion: given 2 of 5 participants as probe, retrieve all 5. Validates event
    shard strategy for Loss 4 (4+ arity relations).
  - Tier hint: local CPU. This is a ~1 hour CPU validation of Pattern B at the specific
    d=10 multi-participant configuration (d=16 was validated as general ceiling; d=10
    specific event-shard form needs direct test).
  - Why now: HIGH PRIORITY. Loss 4 (higher-arity relations) is the key new customer
    segment enabler (finance/healthcare/legal transaction data). P_theoretical = 0.75.
    If partial-cue completion fails at d=10, root cause is binding depth vs. participant
    count; easy to diagnose and adjust.

### 3. Shard structural signature for analogy detection -- role normalization pre-test
  - Anchor pointer: research note Section "Loss 1 -- inter-shard analogy detection"
    + "Mechanism A" in cross-cutting.
  - Substrate-product reading: compute per-shard structural signatures (role-filler-type
    bundles) for a small set of shards containing known-analogous entities. Measure cosine
    similarity between analogous pairs vs. dissimilar pairs. Gate: only proceed if role
    vocabulary is normalized across shards (if ingest uses consistent role labels).
    PRECONDITION: verify role vocabulary normalization in current ingest pipeline first.
  - Tier hint: local CPU. Signature computation is cheap; pairwise comparison is O(S^2)
    at S=10-20 test shards = trivial. The PRECONDITION check (role vocabulary audit) may
    be the larger task.
  - Why now: MEDIUM PRIORITY. P_deflated = 0.40 (below others). Do NOT dispatch before
    the role vocabulary precondition is verified -- signatures will be noise without it.
    Sequence: Anchor 1 first, then check role vocabulary, then Anchor 3.

### 4. Per-shard summary vector for cascade router integration
  - Anchor pointer: research note Section "Loss 2 -- holistic context" substrate mechanism.
  - Substrate-product reading: build per-shard summary vector (bundle of all fact vectors
    in the shard) during sleep defrag. Verify that cascade router querying the summary
    shard correctly identifies relevant member shards for a multi-entity query (vs. querying
    all shards). Latency test: summary-first routing reduces fanout at S=100 shards.
  - Tier hint: local CPU. S=100 shards at N=65536 is manageable locally; no GPU needed.
  - Why now: MEDIUM PRIORITY. Loss 2 is a pseudo-loss (PP-126 already handles it) but
    the summary vector is a useful routing optimization at larger S. Worth shipping as
    part of Anchor 1 implementation (same sleep-defrag scan, marginal cost).

### 5. Mechanism C pilot -- top-10 frequent 2-hop chain pre-computation
  - Anchor pointer: research note Section "Mechanism C -- cross-shard transitive chain
    extraction." Use Chain3 K-hop primitive (PP-11; HP K=12 recovery=0.987) in
    sleep-time pre-compute mode for the top-10 most frequent 2-hop paths.
  - Substrate-product reading: pre-compute 10 known 2-hop traversal paths (e.g., company ->
    CEO -> nationality) during a sleep defrag cycle. Store as derived chain facts. At
    query time verify these paths are answered in 1 shard access vs 2 Chain3 hops.
    Latency win should be ~2x. Quality test: derived chain fact cosine similarity vs
    runtime Chain3 result.
  - Tier hint: local CPU for the pre-compute pilot. Chain3 runtime comparison is existing
    infrastructure.
  - Why now: LOW-MEDIUM PRIORITY. Mechanism C reuses PP-11 which is validated; the sleep-time
    mode is a variant of existing K-hop. Chain quality filtering is the non-trivial piece --
    start with top-10 known paths to validate quality before exhaustive pre-compute.

---

## Context pointers (file paths)

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md
- Prior sleep defrag drill: d:/AI/hd-instrument/notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Sharding invariant (empirical): d:/AI/hd-instrument/notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- Sharding universal capacity: d:/AI/hd-instrument/notes/research_to_exp_dev_sharding_universal_capacity_primitive_2026-06-08.md
- Cap_map (PP-11 K-hop, PP-118 Pattern B, PP-126 parallel sub-query, PP-128 self-routing):
  d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract section

- This hand-off is auto-discoverable by exp_dev on refill cycles (scan notes/exp_dev_handoff_*.md by mtime)
- Anchor 1 (per-property inverted shard pre-test) is the recommended first dispatch
- Anchors 1 and 4 can share the same sleep-defrag scan pass (incremental cost for Anchor 4)
- Anchor 3 has a HARD PRECONDITION: role vocabulary normalization audit must pass first
- No anchor here requires cloud GPU; all are local CPU

## Autonomy declaration

exp_dev has full autonomy to:
- Select which anchors to dispatch and in which order
- Choose N, M, seed count, threshold bands per standard envelope-sizing discipline
- Decide whether Anchors 1 and 4 share a single dispatch or are separate
- Route any of these to remote_cpu_queue per Tier routing policy
- Defer or reorder based on current queue state and other pending priorities
