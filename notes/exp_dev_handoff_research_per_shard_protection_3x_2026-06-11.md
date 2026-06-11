# exp_dev hand-off -- research: per-shard protection + migration architecture

**Filed:** 2026-06-11 by research sub-agent.

**Trigger:** Research drill on per-shard write-protection, age-gated promotion, importance-weighted redundancy, hot-cold tiering, quorum protection, time-gated locking, authority tiers, and RS erasure coding. Full drill at: d:/AI/hd-instrument/notes/research_drill_per_shard_protection_3x_2026-06-11.md

**Pause state:** check data/orchestrator_paused.flag before dispatching any queue adds.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered by cheapest decisive test)

### Anchor 1: SHARD-LOCK-SMOKE
- Anchor pointer: Research note Section 8, Test 1. Write-lock scheme (Scheme 1).
- Substrate-product reading: the cheapest decisive test for per-shard protection. Lock top-K shards by binding score, apply N random writes to remaining shards, measure recall@1 on locked shards before and after. If LOCKED shards maintain recall while MUTABLE shards decay normally, the baseline protection mechanism is confirmed. This is the prerequisite gate for all other schemes.
- Tier hint: local CPU (pure numpy/torch, no GPU required, sub-hour run)
- Why now: without this baseline, none of the more complex protection schemes (quorum, RS encoding, multi-copy) are worth implementing. SHARD-LOCK-SMOKE is the root node of the protection validation tree.
- HARD-PASS threshold: locked shard recall > 0.97 after N adjacent writes
- HARD-FAIL threshold: locked shard decays > 0.03 recall (indicates cross-shard interference persists regardless of lock; protection architecture cannot work)

### Anchor 2: AGE-PROMO-SMOKE
- Anchor pointer: Research note Section 8, Test 2. Age-gated promotion + hot-cold tiering (Schemes 2 + 4).
- Substrate-product reading: validates that a hotness_score tracker (exponential smoothing over access events) correctly identifies shards eligible for promotion, and that PROTECTED shards resist write pressure while MUTABLE shards do not. Tests schemes 2 and 4 together as a combined mechanism.
- Tier hint: local CPU (1 hour, pure substrate ops)
- Why now: hot-cold tiering is a direct engineering dependency for large KB scaling (PP-225 genuine-kb10k path). If hotness tracking works, it unlocks the cold-storage architecture for large KBs. Second cheapest test.
- HARD-PASS threshold: hot shards (50+ accesses) achieve PROTECTED state and maintain recall > 0.98; cold shards (0 accesses) remain MUTABLE and decay at expected rate
- HARD-FAIL threshold: hotness tracker promotes < 80% of genuinely-hot shards (false negative rate too high)

### Anchor 3: IMPORTANCE-MULTICOPY-SMOKE
- Anchor pointer: Research note Section 5, Scheme 3. Importance-weighted multi-copy redundancy.
- Substrate-product reading: tests whether a 2-copy write (binding duplicated to two independent substrate regions) doubles protection without doubling memory overhead beyond acceptable threshold. Majority-vote on read. Tests the multi-copy write path, read reconciliation, and overhead measurement.
- Tier hint: local CPU (3 hours; needs two independent substrate regions)
- Why now: multi-copy is the engineering fallback if RS erasure coding (Anchor 5) fails its numerical precision test. Knowing whether multi-copy overhead is acceptable (< 20%) determines the product tier for high-importance shard protection.
- HARD-PASS threshold: 2-copy shard rejects overwrite via routing check; read majority-vote returns correct binding; overhead <= 20% total substrate memory
- HARD-FAIL threshold: overhead > 30% OR majority-vote returns wrong binding on > 1% of reads

### Anchor 4: AUTH-TIER-SMOKE
- Anchor pointer: Research note Section 5, Scheme 7. Authority-tier write gate.
- Substrate-product reading: authority tiers (tier-0 system / tier-1 schema / tier-2 content / tier-3 volatile) determine which processes can overwrite which shards. Tests that tier-0 shards are unreachable from tier-2 write paths, and that the routing gate adds acceptable latency overhead.
- Tier hint: local CPU (2 hours; metadata + routing layer test)
- Why now: authority tiers are required for the WORM-compliance product feature (foundational schema cannot be overwritten by user input). This is a product requirement for regulated use cases, independent of the research-optimization motivation.
- HARD-PASS threshold: tier-0 shard survives 10,000 unauthorized write attempts with 0 corruptions; gate adds < 5% routing overhead
- HARD-FAIL threshold: any bypass path discovered that allows tier-2 process to corrupt tier-0 shard

### Anchor 5: RS-ENCODE-SMOKE (lower priority, pending Test 3 result)
- Anchor pointer: Research note Section 8, Test 3. RS erasure coding over hyperdimensional vectors (Scheme 8).
- Substrate-product reading: tests whether Reed-Solomon encoding over float32 sub-vectors preserves binding precision. The mathematical question is whether GF(2^8) arithmetic introduces numerical noise > 1e-4. This is a closed-form test: either it works numerically or it does not.
- Tier hint: local CPU (4 hours; GF arithmetic + RS encoder implementation)
- Why now: RS encoding is the highest-durability, lowest-overhead protection scheme IF it works numerically. It is the only scheme with formal fault-tolerance guarantees. If it fails, multi-copy replication (Anchor 3) is the fallback. Test 3 resolves this fork.
- HARD-PASS threshold: cosine similarity of reconstructed vs. original shard > 0.999 for 100% of shards after 1-fragment failure
- HARD-FAIL threshold: cosine similarity < 0.995 OR GF noise per element > 1e-4 (drop RS from roadmap)

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_per_shard_protection_3x_2026-06-11.md -- full research note (10 schemes, 13 sections, 24 citations)
- d:/AI/hd-instrument/notes/substrate_capability_map.md -- current cap_map; per-shard protection is a v3.1 substrate extension not yet in cap_map rows
- d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md -- most recent exp_dev brief; STATIC ops are ROBUST, DYNAMIC ops FRAGILE
- d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md -- research brief; compositional cliff + static/dynamic split established here
- d:/AI/hd-instrument/notes/substrate_static_robust_dynamic_fragile_2026-06-10.md -- memory note confirming STATIC robust / DYNAMIC fragile split; per-shard protection schemes are all STATIC

---

## Contract section

exp_dev picks anchor candidates in priority order, designs ALL numerical parameters (N, M, K, threshold values, seed count, queue), and does NOT accept parameter suggestions from this hand-off. Anchors 1-4 are CPU-local tier, no cloud required. Anchor 5 (RS) is CPU-local but more complex; queue after 1-4 smoke results are in.

If SHARD-LOCK-SMOKE (Anchor 1) HARD-FAILs (locked shard decays > 0.03), escalate to Research before proceeding with any other anchor. This would indicate that cross-shard interference in the shared W matrix is strong enough that routing-level locks are insufficient; a different protection architecture (e.g. separate W matrices per protection tier) would be required.

---

## Autonomy declaration

exp_dev has full autonomy to:
- Choose which anchors to queue and in what order
- Combine anchors into a single cell or run sequentially
- Adjust protection tier threshold values within the smoke envelope
- Route to remote_cpu_queue or local_cpu_queue based on estimated runtime
- Reject any anchor that appears under-specified after reading the research note
