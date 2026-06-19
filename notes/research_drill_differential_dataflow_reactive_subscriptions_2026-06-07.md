# Engineering Reality Check: Differential Dataflow + Reactive Subscriptions

**Date:** 2026-06-07
**Trigger:** API design drill claimed reactive subscriptions are "tractable" with hand-waving scaling math. This drill pressure-tests that claim.
**Discipline:** Theory + engineering analysis only. No empirical verification. Calibration penalty applied (0.20-0.25 deflation; novel-synthesis P capped at 0.50).

---

## HEADLINE

The prior drill's 10% CPU utilization claim is wrong by 6.5x at 1K subscriptions and requires mandatory GPU batching above 10K subscriptions. The reactivity mechanism itself is straightforward (O(S) scan or sub-linear with HNSW). The cryptographic delivery path (Merkle proofs per match) is the genuine engineering differentiator -- no streaming DB ships this. Materialize's architecture offers reusable lessons on arrangements and SUBSCRIBE, but the vector-similarity + cryptography combination is not in its design space. The moat is NOT reactivity alone -- reactivity is commoditizable. The moat is the deterministic-write + cryptographic-provenance combination that makes delivery auditable. A competitor adding Materialize-style vector subscriptions without deterministic writes cannot replicate the provenance guarantee.

---

## 1. Differential Dataflow Basics

**What it is (McSherry et al., CIDR 2013):**

Differential Dataflow (DD) is an incremental view maintenance framework built on top of Timely Dataflow. It operates on *collections* -- multisets where elements carry a (data, time, multiplicity) triple. A negative multiplicity denotes a retraction. Operators (map, filter, reduce, join, iterate) are defined to emit only the *delta* of their output when input deltas arrive, not the full output.

Key data structure: the *arrangement*. An arrangement is a shared, indexed, immutable batch of (key, val, time, diff) tuples. Multiple operators can share a single arrangement without recomputing it. This is the core efficiency lever -- arrangements amortize index-build cost across all operators that need the same indexed view.

**Timely Dataflow underneath:**

Timely Dataflow provides progress tracking via *timestamps* and *frontiers* (sets of times that no future message will precede). When a frontier advances past time T, all operators can commit their T-state as final. This gives Timely its linearizability: operators process in timestamp order, but can run concurrently for different timestamps.

**Materialize's production use (2022+):**

Materialize (the company) commercializes DD+Timely. Their architecture splits into three logical components:

- **Storage (Persist):** durable, S3-backed totally-valued collections (pTVCs). All sources land here first. No upstream filtering -- full ingestion mandatory.
- **Adapter:** PostgreSQL wire-protocol front end; single `environmentd` process (acknowledged bottleneck under high connection volume).
- **Compute:** translates SQL into DD programs; maintains in-memory arrangements per cluster; emits diffs to Adapter.

**SUBSCRIBE (Materialize's subscription primitive):**

Materialize exposes `SUBSCRIBE` (formerly TAIL) which opens a streaming cursor over a materialized view. Each new diff (insert/delete/update) is pushed to the client. This is the closest existing production analog to the substrate subscription primitive. Key difference: SUBSCRIBE is over discrete relational results, not vector-similarity matches. Materialize has no built-in approximate similarity predicate.

---

## 2. Mapping Vector Subscriptions onto DD

**The relational framing:**

In DD terms, subscriptions are a collection `S = {(pattern_i, threshold_i, callback_id_i)}` and writes are a stream of facts `F = {(key_vec_j, value_j, time_j)}`. The materialized view we want to maintain is the join:

```
MATCHES = { (s_id, fact_id) : sim(pattern_i, key_vec_j) >= threshold_i }
```

When a new fact arrives (delta to F), DD needs to compute the delta to MATCHES -- i.e., which subscriptions now have a new match.

**The fundamental problem: similarity is not a join predicate DD can index natively.**

Standard DD join works on equality of keys. `sim(x, y) >= 0.80` is a predicate over the Cartesian product of two collections, not an equality key match. There is no free arrangement that makes this sub-linear without adding an external ANN index. This is not a limitation of DD per se -- it is the fundamental distinction between *discrete relational algebra* (which DD handles perfectly) and *continuous metric-space predicates* (which require geometric indices).

**The honest adaptation:**

To get sub-linear cost, substrate must maintain an ANN index over subscription patterns (not facts). On each new write (fact arrival), the system queries the ANN index for subscriptions whose pattern is close to the incoming fact key. This is a standard nearest-neighbor *query* (fact as query point, subscriptions as the indexed set). The ANN index answers: "which subscription patterns are within cos-distance (1 - 0.80) = 0.20 of this fact key?"

This is a *dual* to the usual vector DB query. Usually: index the facts, query with a pattern. Here: index the subscriptions, query with each incoming fact.

The DD framing then becomes:
- Subscriptions are an indexed arrangement (ANN index over patterns).
- Each new fact delta triggers an ANN lookup against that arrangement.
- The lookup returns the set of matching subscription IDs.
- DD propagates the delta downstream (invoke callbacks).

This is architecturally clean but requires the ANN index to support:
1. Incremental inserts (new subscription added at any time).
2. Incremental deletes (subscription cancelled).
3. Low-latency query (each write triggers one ANN query; must complete within write latency budget).

---

## 3. Index Strategy Comparison

### LSH (Locality-Sensitive Hashing)

**How it works for cos-similarity:** Project vectors onto random unit hyperplanes; hash the sign pattern. Vectors with cos-sim >= theta hash to the same bucket with probability proportional to `1 - arccos(theta)/pi`. For theta = 0.80, this is approximately 1 - 0.21 = 0.79 per hyperplane; L hash tables improve recall.

**Incremental cost:** O(L * d) per subscription insert (hash the pattern into L tables). O(L * d) per fact query (hash the fact, scan matching buckets). Expected bucket size ~ S / 2^k where k = hash bits. With k=16, L=20: expected scan size per query ~ 20 * S/65536 ~ 0.0003 * S.

**For S=1000:** ~0.3 subscription scans per write query. Near O(1).
**For S=10K:** ~3 scans. Still O(1).
**For S=100K:** ~30 scans. Fine.

**Problem:** False positive rate is non-negligible. For cos-sim threshold 0.80, LSH recall at k=16, L=20 is approximately 95-98% -- meaning 2-5% of true matches are missed. For a *subscription* system where missed delivery is a correctness violation (not just a quality degradation), this is unacceptable without a fallback verification step. Every candidate from LSH must be verified with exact cosine computation.

**Net LSH cost per write:** O(L * d) hash + O(candidates * d) verify. At S=100K with tight hash parameters, expected candidates ~ 50-200; verify cost ~ 200 * d FLOP. This is manageable but the false-negative risk must be acknowledged in the product contract.

**Verdict:** LSH is viable for high-S regimes where approximate delivery is acceptable. NOT suitable if subscription contract guarantees zero missed deliveries.

### HNSW (Hierarchical Navigable Small World)

**How it works:** Builds a multi-layer proximity graph. Layer 0 = all nodes; layer L = sparse long-range links. Query starts at top layer, greedy navigates down to layer 0. Achieves ~O(log S) expected query cost at high recall (95-99.9%).

**Incremental cost:** Each insert requires inserting the new node into the graph with M=16-32 neighbors per layer. Cost per insert: O(M * log S * d) for finding M nearest neighbors during construction. This is the expensive operation -- inserting a new subscription into HNSW at S=100K costs ~O(16 * 17 * 65536 FLOP) ~ 17.8 MFLOP. At subscription arrival rate << write rate, this is acceptable.

**Query cost per fact write:** O(ef * d * log S) where ef = exploration factor (default 50-200). At ef=100, d=65536, S=100K: ~100 * 17 * 65536 ~ 111 MFLOP per write query. This is the dominant cost and is *higher* than the naive linear scan at S=1000 (1000 * 65536 = 65 MFLOP).

Wait -- this requires correction. The query visits ef=100 *candidate nodes*, each requiring one cosine computation (d FLOP = 65536 FLOP). So query cost = 100 * 65536 = 6.55 MFLOP, independent of S. The log(S) factor describes graph traversal steps (not cosine computations at each step, which use stored dot products). Approximate traversal cost is O(ef * d) + O(log S * M) for graph hops with precomputed distances.

**For all S scales:** ~6.55 MFLOP per write with ef=100. At 100 writes/sec: 655 MFLOP/sec. On a modern CPU at ~100 GFLOP/s (SIMD): 6.5 ms/sec -- about 0.65% CPU utilization. This is actually good.

**HNSW failure modes (new 2024 finding):** Under high deletion + insertion volume, unreachable nodes accumulate in the graph. The MN-RU algorithm (arxiv 2407.07871) addresses this but adds implementation complexity. For subscription workloads where cancellation is common (subscriptions deleted), HNSW degradation is a real operational risk over long uptime without periodic graph rebuilds.

**Verdict:** HNSW is the right default for substrate's subscription index. Low query latency, high recall, incremental inserts. Requires monitoring for graph fragmentation under churn; periodic rebuild (offline, background) as mitigation. Not suitable for zero-missed-delivery contracts without exact re-verification pass, same as LSH.

### IVF (Inverted File Index / Cluster-Based)

**How it works:** K-means partition of vector space into C clusters. Each subscription is assigned to its nearest cluster centroid. Query: compute distance from fact key to all C centroids; select top nprobe clusters; scan all subscriptions in those clusters exactly.

**Query cost:** O(C * d + nprobe * S/C * d). With C=sqrt(S), nprobe=8: O(sqrt(S) * d + 8 * sqrt(S) * d) = O(9 * sqrt(S) * d).

**For S=1000:** 9 * 31 * 65536 ~ 18 MFLOP per write.
**For S=10K:** 9 * 100 * 65536 ~ 59 MFLOP per write.
**For S=100K:** 9 * 316 * 65536 ~ 186 MFLOP per write.

**Critical problem:** IVF requires static clusters. Adding a new subscription may require reassigning it to a cluster and potentially rebalancing. With online subscriptions arriving and departing frequently, cluster quality degrades. Mini-Batch K-Means can update centroids incrementally but this adds a background maintenance thread. More critically, at S < 10K, HNSW is faster with better recall. IVF becomes competitive at S >= 1M.

**Verdict:** IVF is not the right choice for substrate's subscription index at plausible S ranges (1K-100K). HNSW dominates at this scale. IVF is worth considering if subscriptions reach 1M+ and recall guarantees are relaxed.

---

## 4. Honest Scaling Math

The prior drill claimed: 1000 subs + 100 writes/sec = 100ms CPU/sec (10% utilization on one core). This is wrong. Here is the corrected analysis.

**Definitions:**
- d = 65536 (N = 65536, d = N for full inner product)
- write_rate = 100/sec (target)
- One cosine computation = d multiplies + d adds + 1 divide = ~2d + 1 FLOP ~ 131K FLOP
- CPU SIMD throughput (AVX-512 float32) ~ 200-500 GFLOP/s on one core (theoretical); practical streaming throughput with cache misses ~ 10-50 GFLOP/s

**Conservative practical estimate: 10 GFLOP/s (cache-miss-dominated for large d).**

### Naive scan (no index):

| S | Sims/sec | FLOP/sec | CPU fraction (10 GFLOP/s) |
|---|---|---|---|
| 1,000 | 100K | 13.1 GFLOP/s | 131% -- exceeds one core |
| 10,000 | 1M | 131 GFLOP/s | 13.1 cores |
| 100,000 | 10M | 1.31 TFLOP/s | 131 cores |

**The prior drill's 10% claim is wrong by 13x at S=1000.** At d=65536 and write_rate=100/sec, naive scan exhausts one core even at S=1000. The correction: for N=65536, one cosine costs ~131K FLOP (not ~65K as claimed; the prior estimate used FLOP=N rather than FLOP=2N+1). The practical bottleneck is memory bandwidth, not arithmetic. At d=65536 float32 = 256KB per vector, reading 1000 subscription vectors per write = 256 MB per write = 25.6 GB/s bandwidth at 100 writes/sec. This exceeds L3 cache bandwidth on commodity CPUs (typically 200-400 GB/s peak, but with competing memory loads ~ 50-100 GB/s effective).

**With HNSW index (ef=100, corrected):**

| S | FLOP/write (query) | FLOP/sec at 100 writes/s | CPU fraction |
|---|---|---|---|
| 1K | ~6.5 MFLOP | 650 MFLOP/s | 6.5% |
| 10K | ~6.5 MFLOP | 650 MFLOP/s | 6.5% |
| 100K | ~6.5 MFLOP | 650 MFLOP/s | 6.5% |
| 1M | ~6.5 MFLOP (+ log overhead) | ~700 MFLOP/s | 7% |

**HNSW changes the game completely.** With HNSW ef=100, the per-write cost is O(ef * d) regardless of S. This is the right architecture. The 10% utilization figure from the prior drill is numerically close to correct IF HNSW is already assumed. The prior drill did not say this explicitly -- it implied a naive scan cost of 100ms/sec, which was wrong by 13x without an index.

**GPU batching boundary:**

At write_rate = 1000/sec (production target, not 100/sec) and HNSW ef=100:
- 1000 * 6.5 MFLOP = 6.5 GFLOP/sec per shard
- CPU SIMD at 10 GFLOP/s practical: ~65% utilization -- marginal

At write_rate = 1000/sec with naive scan S=1000:
- 1000 * 1000 * 131K = 131 GFLOP/sec -- requires GPU

**GPU batching is mandatory at write_rate=1000/sec without HNSW, even at S=1000.** With HNSW, one CPU core handles up to ~1500 writes/sec at S=any (HNSW query cost is S-independent). This is the correct claim for v1 engineering.

---

## 5. Production Failure Modes with Mitigations

### Failure A: Subscription storm (write burst)

A write burst (e.g., 10K writes in 1 second during a bulk import) triggers O(10K) HNSW queries simultaneously. HNSW query is not trivially parallelizable at per-query level (graph traversal has data-dependent branching). The burst backlog depth = burst_writes * HNSW_query_latency. At 1ms per HNSW query (ef=100, d=65536, S=100K), 10K burst = 10 seconds of backlog on one thread.

**Mitigation:** Batch the HNSW queries across the burst. Compute the union of "which subscriptions match at least one write in this batch" using batched matrix multiply (fact_batch @ subscription_matrix). For a burst of B writes and S subscriptions with HNSW: B * S cosine computations as a (B x d) @ (d x S) matmul -- GPU-efficient. This converts a storm of serial HNSW queries into one GPU matmul. Cost: (B=10K) x (d=65536) x (S=100K) FLOP = 65 TFLOP -- feasible on one H100 in ~6.5 seconds, but a high-write system should never hold a 10K burst in a single batch; it should chunk at B=100-500.

### Failure B: Late-registration catch-up

A new subscriber registers and wants all *historical* writes since time T0 that match their pattern. The substrate's Merkle accumulator has all historical writes accessible by root hash traversal. Catch-up requires scanning all N_historical writes and computing cosine(pattern, key_vec_i) for each. At N_historical=10M writes: 10M * 131K FLOP = 1.31 PFLOP -- approximately 131 seconds on a 10 GFLOP/s CPU. This is not a streaming problem; it is a batch historical query.

**Mitigation A:** Rate-limit catch-up scans (background worker, 10% of CPU budget). Catch-up latency for 10M writes ~ 22 minutes. Acceptable for cold-start subscriptions.

**Mitigation B:** Build a secondary ANN index over historical fact keys. Query: "which historical facts match this new subscription pattern?" This inverts the direction again (index facts, query with subscription). HNSW over 10M facts: query cost O(ef * d) ~ 6.5 MFLOP, returning top-K matches. But this misses all matches, not just top-K -- need threshold scan, not top-K. For threshold scans over historical data, HNSW recall at the threshold boundary is ~ 95-98%; acceptable for catch-up if the product contract allows approximate historical delivery.

**Mitigation C (preferred):** Bootstrap from accumulator snapshot. At subscription registration time, issue an as_of(T_now) query that returns all writes since T0 matching the pattern, using a snapshot of the W matrix at T0. This is exact (no approximation) but expensive. Gate catch-up depth (e.g., max 30 days of history).

### Failure C: Pattern drift vs delivery correctness

The subscription pattern is a fixed vector registered at time T0. The substrate's W matrix evolves. A key question: does "matching" mean cosine(pattern, fact_key) >= threshold where fact_key is the incoming write's key vector, or where fact_key is the *current reconstructed embedding* of the concept?

The correct interpretation for the substrate's deterministic write semantics: fact_key is fixed at write time (it is the key vector bound during the write operation). The W matrix evolves to accommodate new writes, but each fact's key vector is immutable. Therefore:
- sim(pattern, key_vec_j) is fixed for all time once fact j is written.
- A subscription registered at T0 will correctly match all new writes whose key_vec exceeds threshold against the fixed pattern.
- Pattern drift (subscription becoming semantically stale over time) is a product-level concern, not a correctness bug.

**Mitigation:** Subscription TTL + resubscribe prompt. No engineering fix needed; product UX problem.

### Failure D: Threshold boundary flicker

A fact with sim ~ 0.800 (right at threshold) may be delivered, then if the threshold logic is re-evaluated (e.g., on subscription modification), the same fact could be re-delivered or excluded. This creates inconsistency in the delivery guarantee.

**Mitigation:** Hysteresis band. Deliver when sim > threshold + epsilon (e.g., 0.82). Include in "active match" until sim < threshold - epsilon (e.g., 0.78). The Merkle path for the fact is computed once and cached; re-delivery uses the cached path. This is a clean implementation boundary.

### Failure E: Subscription leak / zombie subscriptions

A subscriber registers, receives some callbacks, then goes offline. Without explicit cleanup, the subscription remains in the HNSW index indefinitely. At S=100K with 80% being zombies, actual recall is wasted on dead subscribers.

**Mitigation:** Heartbeat protocol. Each subscriber must confirm liveness every TTL (default 60s). Server-side tombstone on TTL expiry. HNSW deletion (with MN-RU fix for unreachable nodes). Combine with a background graph rebuild nightly to purge tombstoned nodes cleanly.

### Failure F: Multi-tenant isolation

Tenant A has 95K subscriptions; Tenant B has 5K. Tenant A's write burst fills the subscription dispatch queue and delays Tenant B's callback delivery.

**Mitigation:** Per-tenant HNSW index (isolated, not shared). Separate dispatch queue per tenant with per-tenant rate limits. Cross-tenant interference becomes impossible. Memory overhead: each HNSW index for S=100K subscriptions at d=65536 float32 ~ S * M * d * 4 bytes ~ 100K * 16 * 65536 * 4 bytes ~ 419 GB. This is not per-tenant; it is the HNSW graph storage for one tenant's 100K subscriptions.

Wait -- the HNSW graph stores neighbor pointers, not full vectors. The neighbor list: M=16 neighbors per node, 8 bytes per neighbor ID, 2 layers ~ 100K * 32 * 8 = 25.6 MB. The subscription vectors themselves: 100K * 65536 * 4 bytes = 26 GB per tenant. This is the dominant cost. Per-tenant isolation requires per-tenant vector storage. At 26 GB per tenant with 100K subscriptions each, multi-tenant isolation is memory-expensive.

**Revised mitigation:** Shared vector store with per-tenant namespace tags; per-tenant query filtering at the HNSW layer. Row-level tenant filtering on HNSW candidates before delivery. This is the Weaviate/Qdrant multi-tenancy pattern.

---

## 6. Three Delivery Alternatives Compared

### Alternative 1: Poll-based subscription

Client calls `get_matches_since(pattern, checkpoint_token, threshold)` periodically. Substrate returns all writes since `checkpoint_token` that match.

**Implementation cost:** Very low (v1 week 1). Uses existing query path.
**Latency:** Floor = poll interval. At 1-second polling, delivery latency median ~ 500ms. At 100ms polling, 10x CPU overhead for idle subscribers.
**Scalability:** Excellent. No server-side subscription state. Each poll is stateless.
**Cryptographic delivery:** Trivial -- include Merkle paths in poll response.
**Verdict:** Right choice for v1. Easy to implement. Becomes the fallback/compatibility mode for clients that cannot maintain persistent connections.

### Alternative 2: Change Data Capture (CDC) + client-side filter

Substrate emits a CDC stream of all writes (key_vec, value, Merkle_path, timestamp) over a message bus (Kafka/NATS). Clients subscribe to the CDC stream and apply their own cosine filter locally.

**Implementation cost:** Medium (need a reliable CDC stream, probably Kafka/NATS integration).
**Scalability:** Excellent for substrate (no per-subscription state). CDC fanout scales with Kafka partition count.
**Problem 1:** Bandwidth. Each write event includes the full key_vec (d=65536 float32 = 256KB) + Merkle path (~1-5KB) + value. At 1000 writes/sec: 256 MB/sec of write events per subscriber. Completely infeasible for high-N substrates.
**Problem 2:** Pushes cosine compute to client. Client must run SIMD-optimized cosine against their pattern for every write event. This is a significant client-side burden.
**Problem 3:** Privacy. Publishing all write key vectors to a shared CDC stream leaks the substrate's content to all subscribers. Multi-tenant use case is incompatible.
**Verdict:** Not suitable for production. CDC-style streaming works for low-d or low-volume substrates only. Privacy concern is a hard blocker.

### Alternative 3: WebSocket push (server-side matching)

Client registers `subscribe(pattern, threshold)` over WebSocket. Server maintains subscription state. Server pushes matches as they arrive.

**Implementation cost:** Medium-high (need WebSocket transport + subscription registry + HNSW index).
**Latency:** Minimum possible (~1-5ms from write to delivery at S=1K with HNSW).
**Server-side cost:** HNSW index (as analyzed above). This is the only alternative where substrate bears the matching compute.
**Cryptographic delivery:** Each push includes Merkle path. This is the differentiator -- no streaming DB does cryptographic delivery over WebSocket push.
**Verdict:** Right architecture for production. v2 target. The engineering cost is concentrated in the HNSW index maintenance and WebSocket reliability.

**Winner:** Poll for v1, WebSocket push for v2. CDC is not viable at production N.

---

## 7. Unconsidered Angles

**(a) Federated subscriptions across shards.** A subscription should match writes to *any* shard, not just the local shard. The delivery mechanism must collect matches from all shards and deduplicate. With per-shard HNSW indices, a single write triggers one HNSW query locally. A federated subscription requires routing the subscription pattern to all shards at registration time and aggregating match events. The aggregation layer is the hard problem: a write to shard 3 must know to deliver to a subscription registered on shard 1. This requires either (a) subscription broadcasting (register on all shards at cost O(K_shards)), or (b) a global subscription routing table. Option (a) is the correct first approach; option (b) is the Materialize Adapter pattern.

**(b) Compositional subscriptions (K-hop).** A subscriber wants to be notified when a *chain* of matches exists: fact A matches pattern_1, and fact A's value vector matches pattern_2. This requires a two-hop join in DD terms: `MATCHES_1 JOIN MATCHES_2 ON value_of(fact_1) ~ pattern_2`. This is a native DD operation if facts are stored as a DD collection. Cost scales with the cross-product of matches at each hop. For sparse subscriptions (few matches per pattern), this is tractable. For dense subscriptions (many matches), the join can explode. Pre-registered K-hop subscriptions need cardinality estimation.

**(c) Negation subscriptions.** A subscriber wants to be notified when *no* write matching a pattern has arrived in the last T minutes. This is a "absence of evidence" trigger. In DD, this requires maintaining the count of matches per subscription and triggering on transition from count > 0 to count = 0 (with time-windowing). Non-trivial: requires a windowed aggregation with negative diff propagation. This is the hardest subscription type to implement correctly.

**(d) Subscription explainability.** The Merkle path proves *that* a write occurred, but not *why* it matched the subscription. A "why" response would include the cosine score, the top contributing dimensions (feature attribution), and the write context. This is the difference between cryptographic verification and semantic explainability. Neither Materialize nor any existing streaming DB provides this. It is substrate-native if the key vectors are interpretable (e.g., via sparse coding).

**(e) Quorum subscriptions.** Notify when M of K patterns match the same write. This requires maintaining a per-write counters of matched subscriptions -- an aggregation over the match relation, not individual deliveries. In DD, this is a `count_by_fact_id` view with a threshold filter. Efficient; the hardest part is defining "same write" (by Merkle path / accumulator hash -- exact identity, which substrate has).

**(f) Subscription persistence across restarts.** HNSW is an in-memory index. Restart = rebuild from scratch. At S=100K subscriptions, HNSW rebuild cost ~ O(S * M * log S * d) FLOP -- dominated by the S*M*d = 100K * 16 * 65536 ~ 105 GFLOP. At 10 GFLOP/s ~ 10.5 seconds per rebuild. Acceptable if restarts are rare. Mitigation: serialize HNSW to disk (hnswlib supports this natively); cold start = 2-5 second deserialization rather than full rebuild.

**(g) Subscription delivery ordering guarantees.** If two writes arrive that match the same subscription, in what order are callbacks delivered? With a bounded per-subscription queue, FIFO ordering is easy. But with multi-threaded dispatch, callbacks for the same subscription could be dispatched out of order. The Merkle path includes the sequence number (implicit in the accumulator chain), so delivery with the Merkle path *contains* the ordering information -- the client can sort by accumulator position. This is a strong property not available in any streaming DB without cryptographic accumulators.

---

## 8. Engineering Roadmap

### v1: Minimum Viable Subscription (2-3 weeks Python)

**Architecture:** Single-node, in-process. Poll-based delivery. No server-side subscription state.

- Write path unchanged. After each write, scan active subscriptions linearly (O(S)).
- `subscribe(pattern, threshold)` stores (pattern_vec, threshold, callback_id) in an in-memory list.
- `get_matches_since(sub_id, cursor)` returns Merkle-path-included matches since `cursor`.
- Upper S limit: ~500 subscriptions before CPU saturation at write_rate=100/sec with d=65536. At N=1024 (development N), limit is ~50K subscriptions trivially.
- **Critical note:** v1 at N=65536 requires keeping S < 500 or write_rate < 10/sec. This is a real constraint the prior drill elided.
- Implementation: ~200 lines Python. Webhook delivery optional (add asyncio HTTP client).

**Estimated effort:** 2 weeks including delivery + Merkle path integration.

### v2: Production Scaling (6-8 weeks)

**Architecture:** HNSW index over subscription patterns. WebSocket/SSE push delivery. Per-shard deployment.

- `SubscriptionRegistry` backed by hnswlib (Python binding to C++ HNSW).
- Each write triggers HNSW query: `registry.query(fact_key, ef=100)` -> candidate subscription IDs.
- Verify candidates with exact cosine (remove false positives from HNSW approximation).
- Bounded per-subscription delivery queue (asyncio.Queue maxsize=1000).
- WebSocket push per subscription; backpressure via queue fullness check.
- HNSW periodic rebuild (background thread, nightly or on 10% zombie rate).
- Heartbeat protocol (60s TTL per subscription).
- Merkle path included in every delivery payload.

**Upper S limit:** ~100K subscriptions at write_rate=1000/sec with one CPU core for HNSW matching. Above 100K or above 1000 writes/sec: GPU-batched matmul for subscription matching.

**GPU batching trigger:** if S > 100K or write_rate > 1000/sec, switch to: batch writes at 10ms windows; compute (batch x d) @ (S x d).T as GPU matmul; threshold the result; dispatch callbacks for non-zero rows.

**Estimated effort:** 6-8 weeks (hnswlib integration + WebSocket reliability + backpressure + heartbeat + HNSW maintenance).

### v3: Enterprise Features (4-6 months)

- Federated subscriptions across shards (subscription broadcast + shard-local HNSW + central aggregation).
- K-hop compositional subscriptions (DD join over fact graph -- requires facts stored as DD collection, not just W matrix).
- Negation subscriptions (windowed absence detection -- needs time-windowed DD aggregation).
- Subscription persistence to disk (hnswlib serialize/deserialize + subscription metadata store).
- Multi-tenant isolation (per-tenant HNSW namespace, per-tenant queue quotas).
- Subscription explainability (cosine score + top-K contributing dimensions in delivery payload).
- Quorum subscriptions (per-write match counter in DD).

**Estimated effort:** 4-6 months for full v3. Each feature is independently shippable (2-4 weeks each).

---

## 9. Materialize Lessons for Substrate

**Lesson 1 -- Arrangements are the efficiency lever.** Materialize's core insight: share the indexed, sorted version of a collection across all operators that need it. For substrate, this means: if multiple subscriptions share a similar pattern region, a shared ANN index sub-tree serves all of them. HNSW naturally provides this -- nearby subscription patterns share graph neighbors and their search paths overlap. No explicit implementation required; HNSW gives it for free.

**Lesson 2 -- Control plane bottleneck is real.** Materialize's `environmentd` single-process control plane is acknowledged to bottleneck at high connection counts. Substrate's analogous bottleneck: the subscription registry process. At S=100K subscriptions with high churn (subscribe/unsubscribe events), the registry update path (HNSW insert/delete + metadata write) becomes the bottleneck. Materialize plans to split `environmentd`; substrate should plan for a distributed subscription registry at v3.

**Lesson 3 -- Storage-compute separation is mandatory for scale.** Materialize separates Persist (S3-backed storage) from Compute (in-memory DD). Substrate needs the same separation: the W matrix and accumulator live in Persist; the subscription HNSW index lives in Compute. Subscription state must be reconstructable from durable storage (subscription manifest in Persist) if the Compute node fails.

**Lesson 4 -- SUBSCRIBE is the right primitive, not polling.** Materialize's SUBSCRIBE cursor is their high-value streaming primitive. It is architecturally exactly what substrate's WebSocket push delivers. The difference: Materialize SUBSCRIBE is over relational diffs; substrate SUBSCRIBE is over similarity-triggered diffs with Merkle proofs. The transport and backpressure design can be directly borrowed from Materialize's implementation.

**Lesson 5 -- Backpressure is not optional.** Materialize's Timely Dataflow frontiers provide end-to-end flow control. Substrate's v2 subscription dispatch needs the same: if a subscriber's WebSocket buffer fills, the subscription queue must stop accepting new matches, not discard them silently. Silent discard violates the Merkle-provable delivery contract. The correct behavior: block the dispatch worker until queue drains (for slow subscribers) OR drop with an explicit "missed delivery" gap in the Merkle proof chain (for timed-out subscribers).

---

## 10. Brutal Honesty: Does the Moat Survive?

**The reactivity primitive alone is NOT a moat.**

Weaviate, Qdrant, Milvus, and Pinecone could each add HNSW-indexed change notification within a 3-6 month engineering effort. The core engineering is not novel: it is HNSW index over vectors + CDC stream + threshold filter + WebSocket push. This combination has zero patent protection and straightforward implementation. If a competitor prioritized it, it would ship.

**The CDC alternative analysis above showed that full-key-vector CDC is infeasible at d=65536 due to bandwidth.** This gives substrate a specific scaling advantage: the server-side HNSW matching *compresses* the delivery bandwidth from (S * d * write_rate) per subscriber to (match_rate * Merkle_path_size) per subscriber. At match_rate << write_rate (most writes don't match most subscriptions), this is a 100-1000x bandwidth reduction. This is a real efficiency advantage but not a moat -- a competitor with lower-d embeddings (d=1536, d=3072) can do CDC directly and avoid server-side matching.

**The actual moat is the deterministic write + cryptographic delivery combination.**

Substrate's unique properties that *cannot* be added to a competitor's stack without architectural surgery:

1. **Deterministic write semantics:** Every write to substrate produces a deterministic key vector (no sampling, no batch normalization, no model-version drift). This means the cosine(pattern, key_vec) is *stable* -- the same pattern always means the same thing relative to the same fact. Pinecone/Weaviate rely on embedding models that can be updated, making subscription patterns semantically unstable across model upgrades.

2. **Cryptographic delivery via Merkle accumulator:** The Merkle path proves (a) the fact was written, (b) when it was written relative to other facts, (c) the write was not tampered with. No streaming DB provides this. The governance-aware vector subscriptions paper (arxiv 2603.20833) gets close with policy enforcement but has no cryptographic delivery mechanism. Delivery + proof = auditable data contracts. This is the basis for EU AI Act Article 12 compliance use cases.

3. **Per-shard isolation with accumulator-root identity:** Each shard has its own cryptographic identity (accumulator root). A multi-shard subscription can verify that deliveries came from the claimed shard and were not mixed or substituted. No vector DB has shard-level cryptographic identity.

**Competitor decomposition:**

| Feature | Pinecone | Weaviate | Milvus | Substrate |
|---|---|---|---|---|
| Vector ANN query | Yes | Yes | Yes | Yes |
| Reactive notification | Partial (polling) | No | No | Yes (v2) |
| Threshold-based subscription | No | No | No | Yes |
| Cryptographic delivery | No | No | No | Yes |
| Deterministic writes | No | No | No | Yes |
| Shard identity | No | No | No | Yes |
| K-hop compositional subs | No | No | No | Yes (v3) |

The moat components that require architectural surgery to copy: (2), (3), and the deterministic-write property. Reactivity alone (row 2, 3) can be added to any system. The combination of reactivity + cryptographic + deterministic is the actual category-defining claim.

**Calibration-adjusted probability that reactivity alone is a durable category-defining feature:** P = 0.15 (deflated 0.25 from prior drill estimate of ~0.40).

**Calibration-adjusted probability that reactive + cryptographic + deterministic writes as a combined primitive is a durable category-defining feature:** P = 0.45 (capped at 0.50 per novel-synthesis rule; deflated 0.20 from raw estimate of 0.65).

---

## Cheap Decisive Test

**Test:** Implement naive scan subscription (linear O(S)) at N=65536. Measure actual CPU time per write at S=100, S=500, S=1000 with write_rate=100/sec. Compare to predicted values:
- S=100: ~13% CPU utilization (one core)
- S=500: ~65% CPU utilization (one core)
- S=1000: >100% CPU utilization (saturates one core)

If measured CPU is within 2x of prediction, the scaling model is validated and the HNSW transition point is confirmed at S~500 for N=65536.

**Runtime:** ~10 minutes CPU. Zero GPU. This validates the scaling model before any HNSW implementation work begins. If the naive scan is faster than predicted (due to SIMD vectorization + cache warmth), the HNSW transition point shifts right (higher S before saturation).

---

## Falsifiable Predictions

**HARD-PASS (confirms model):**
- Naive scan at S=1000, N=65536, write_rate=100/sec saturates one CPU core (>=90% utilization)
- HNSW at ef=100, S=100K, write_rate=100/sec uses <15% of one CPU core
- V1 poll-based subscription with S<500 and write_rate=10/sec delivers Merkle-path-included matches with <100ms latency

**HARD-FAIL (refutes model):**
- Naive scan at S=1000 uses <20% CPU (would mean the 6.5x scaling error in the prior drill was actually correct -- unexpected SIMD efficiency or cache behavior)
- HNSW at ef=100 uses >40% CPU at write_rate=100/sec and S=10K (would mean our HNSW query cost estimate is wrong by 6x)
- Merkle path generation per match takes >50ms (would make WebSocket push latency non-competitive with polling)

---

## Cross-Thread Synthesis

This drill is NOT in the core substrate-physics cap_map (thermodynamics, spin-glass, etc.). It is an engineering reality check on a product feature claim. Connection points:

- Cap row for retrieval fidelity: HNSW recall at threshold boundary (sim ~ 0.80 with tolerance +/- 0.02) connects to the cap_map row on retrieval accuracy. The 2-5% false negative rate from LSH (and ~1% from HNSW at ef=100) sets a precision floor for subscription guarantees that relates to the underlying retrieval fidelity claims.
- Cap row for deterministic write semantics: the stability of cosine(pattern, key_vec) across W matrix updates is only guaranteed under the substrate's pseudoinverse-update write protocol. Any stochasticity in the write path (e.g., gradient-based update instead of pseudoinverse) breaks the subscription guarantee.
- Phase 2 EU AI Act chain: the cryptographic delivery + Merkle provenance path connects to the Phase 2 ZKP soundness / regulatory-pull findings. Reactive subscriptions with Merkle proofs are a direct implementation primitive for AI Act Article 12 data provenance requirements.

---

## Substrate-Product Implications

1. **v1 must gate S < 500 at N=65536.** Do not ship reactive subscriptions without documenting the S<500 limit at production N. Above 500 subscriptions, naive scan saturates one core at write_rate=100/sec. This is a product constraint that must be in the API contract.

2. **HNSW is mandatory for v2.** The hnswlib library (Python/C++) provides a production-ready implementation. No custom implementation needed. Effort is integration + maintenance (heartbeat, TTL, rebuild scheduling) not algorithm development.

3. **Cryptographic delivery is the category-defining differentiator, not reactivity.** The product positioning should lead with "verifiable delivery" not "reactive subscriptions." Verifiable delivery is what competitors cannot easily add.

4. **Poll-first, push-later.** Ship poll-based subscriptions in v1 (2-3 weeks). This provides the product primitive for customer testing. Push-based WebSocket in v2 (6-8 weeks) is the production feature. This sequencing matches the engineering complexity ladder.

5. **EU AI Act Article 12 compliance path is direct.** The Merkle-path-per-delivery pattern directly satisfies the logging and provenance traceability requirements coming into force August 2026. This should be a named product feature, not a side effect.

---

## Citations

1. McSherry, Murray, Isaacs, Isard. "Differential Dataflow." CIDR 2013. https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf
2. McSherry et al. "Shared arrangements: practical inter-query sharing for streaming dataflows." VLDB 2020. https://dl.acm.org/doi/10.14778/3401960.3401974
3. Materialize, Inc. "The Software Architecture of Materialize." 2023. https://materialize.com/blog/materialize-architecture/
4. "Enhancing HNSW Index for Real-Time Updates: Addressing Unreachable Points and Performance Degradation." arXiv 2407.07871. https://arxiv.org/abs/2407.07871
5. "Index-based, High-dimensional, Cosine Threshold Querying with Optimality Guarantees." arXiv 1812.07695. https://arxiv.org/abs/1812.07695
6. "CANDY: A Benchmark for Continuous Approximate Nearest Neighbor Search with Dynamic Data Ingestion." arXiv 2406.19651. https://arxiv.org/abs/2406.19651
7. "SIVF: GPU-Resident IVF Index for Streaming Vector Search." arXiv 2601.11808. https://arxiv.org/abs/2601.11808
8. "Governance-Aware Vector Subscriptions for Multi-Agent Knowledge Ecosystems." arXiv 2603.20833. https://arxiv.org/abs/2603.20833
9. "Streaming Similarity Self-Join." arXiv 1601.04814. https://arxiv.org/abs/1601.04814
10. Malkov, Yashunin. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs." IEEE TPAMI 2020.

**Verified citations: 10**

---

## P Estimates (Calibration-Adjusted, Penalty Applied)

- P(naive scan model is correct within 2x): 0.85 -- well-grounded in standard FLOP accounting; minor uncertainty from SIMD efficiency
- P(HNSW ef=100 query cost model correct within 2x): 0.75 -- HNSW query cost analysis is established; uncertainty from cache behavior at d=65536
- P(reactivity alone is durable moat): 0.15 (deflated 0.25 from 0.40)
- P(reactive + cryptographic + deterministic is durable combined moat): 0.45 (capped 0.50, deflated 0.20)
- P(v1 poll-based with S<500 is correct S limit at N=65536): 0.80 -- based on bandwidth analysis; minor uncertainty from memory hierarchy effects

**P_deflated_overall = 0.45** (the novel-synthesis claim that the combined primitive is category-defining)

**Next-drill candidate:** The K-hop compositional subscription angle (angle (b) in Section 7) maps directly to the network-science / graph-theory tier-1 adjacency (expander graphs, spectral gap). A drill on "reactive graph queries over streaming vector databases" would cover both the compositional subscription engineering question and the cap_map graph-structure row.
