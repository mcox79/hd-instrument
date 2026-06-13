# Exp-Dev -> Research: handoff#2 FEASIBILITY (proxy) -- partition-stratified smoke does NOT help; it HURTS. The OLD homogeneous smoke already predicts full (gap 0.067); current pipeline's z>=3 + blocklist appears to have ALREADY mitigated the jargon degradation premise (from 3 earlier iterations). True-P@30 review batches saved.

**From:** Exp-Dev -> Research  **Date:** 2026-06-12 Cycle 51. Feasibility pass on hand-off anchor #1 (smoke-to-full degradation).
NO LLM. Phase-2-light (numpy-only), MEASUREMENT-ONLY (proposals only; NO canonical atoms written). Laptop CPU.
**Cell:** exp_partition_stratified_smoke_gap_cpu_v1.py. **Metric:** JARGON-PATTERN P@30 PROXY (top-30 proposal is bona-fide iff
canonical_name is NOT substrate-meta-jargon). NOT true P@30 (which needs Research ACCEPT/REJECT) -- both top-30 batches saved to
data/substrate_index/bench_reports/partition_stratified_smoke_batches.json for your true-P@30 confirmation.

## Result (full mode: 30 stratified, 30 homogeneous, 1200-file full sample; 30 proposals each)
| smoke design | proxy P@30 | gap to full (0.800) |
|---|---|---|
| homogeneous (research_drill ONLY, the OLD smoke) | 0.733 | **0.067** |
| partition-stratified (5/partition x 6) | 0.433 | **0.367** |
- **stratification_helps = FALSE** (stratified gap 0.367 >> homogeneous gap 0.067).
- per-partition proxy P@30: research_drill 0.60, research_history 0.33, findings 0.25, results/decision/meta 0.00. **spread 0.60**.

## Findings (proxy; verify-before-build on a dispatch-deferred handoff)
1. **The premise appears STALE.** The handoff's motivating degradation (-0.17 to -0.44, full P@30 ~0.33) was from 3 EARLIER
   self-extension iterations. On the CURRENT pipeline, full-corpus proxy P@30 is HIGH (0.80) and the OLD homogeneous smoke
   already predicts it within 0.067. The current pipeline's META_JARGON_LEADING blocklist + z_count>=3 + SKIP_NEAR_MATCH (0.40)
   appear to have ALREADY mitigated the jargon mis-extraction the handoff targets.
2. **Stratification HURTS, mechanism identified.** Jargon is DIFFUSE -- per-file atom-IDs / capability-IDs / cycle-numbers /
   verdict-phrases that do NOT recur across files. The z>=3 cross-file recurrence filter WASHES IT OUT at scale (full 0.80,
   homogeneous-30 0.73). But at tiny 5-file-per-partition scale, jargon DOMINATES the few proposals (results/decision/meta
   partitions -> proxy 0.0), dragging the stratified smoke to 0.433 -- UNrepresentative of full. So stratifying the SMOKE makes
   it WORSE, not better, because the small per-stratum jargon spikes don't average out the way they do at full scale.
3. **The disaggregation insight HOLDS** (spread 0.60): partitions DO have very different content quality. But the right lever is
   NOT smoke-stratification -- it is the z>=3 recurrence filter that already handles diffuse jargon. A homogeneous smoke of
   sufficient size is already representative IF the deployment filter (z>=3) is the same.

## Honest caveats
- PROXY, not true P@30. The proxy = not-meta-jargon; it directly targets the handoff's blamed failure mode but is not Research
  ACCEPT/REJECT. Batches saved -- recommend you score the true P@30 on the 2x30 to confirm the proxy's direction.
- 1200-file full sample (not all 2524 non-drill files) for runtime; sample is partition-proportional-ish via union.

## Routing
- **Research:** anchor #1 (partition-stratified-smoke) is NOT supported by the proxy -- it hurts, and the premise looks
  mitigated by the current pipeline. Recommend: (a) confirm via true P@30 on the saved batches; (b) if confirmed, the
  methodology rule should be REFRAMED -- "diffuse jargon is handled by z>=3 recurrence; smoke must match the deployment FILTER,
  not the partition MIX" -- rather than "smoke must be partition-stratified". Anchor 2/3 (per-partition filters / held-out
  decoupling) likely unnecessary if the premise is stale.
- **Exp-Dev:** handoff #2 feasibility done (proxy). I did a feasibility measurement (not a canonical methodology decision)
  respecting the dispatch-gate; verify-before-build surfaced the stale premise. Awaiting your true-P@30 confirmation / re-scope.
