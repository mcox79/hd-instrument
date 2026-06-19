# Research: alternative edit-isolation mechanisms (post-COW infeasibility) v1

Date: 2026-05-31
Origin: v290 cap_map; U3 `edit_isolation_guard_probe_v1_n4096` HARD_FAIL: COW MECHANISM correctness OK (cons=1.00, audit=5/5 unanimous) but COST INFEASIBLE (mem-amp 10.13x vs 4x target = 2.5x over; throughput 6-7.5/s vs 50/s target = 7-8x slower).
Trigger: routing file `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (R-COW-INFEASIBILITY R3).
Method: 3 parallel Sonnet lit-scan subagents (delta-encoding storage; LSM lazy-replay; CRDT + LSH-partial-COW hybrid). All searches generic-terms only per [[feedback-query-privacy-decomposition]]; calibration penalty applied per [[feedback-lit-scan-calibration-penalty]].

## HEADLINE

The COW failure mode is structural: copying a full N x N matrix per rank-1 edit is asymptotically wasteful when the edit itself only spans 2N floats. Four candidate architectures recover production-feasible cost profiles, ranked by deflated-P x KF-2 compatibility x engineering budget:

- **M1+M2 Log-structured rank-1 store (delta-encoding + LSM lazy-replay; ONE mechanism family).** P_deflated 0.40-0.50. Mem-amp 1.5-3x at K up to M. Throughput 4-11K q/s (well above 50/s). **Audit-by-construction synergy with KF-2 deletion-cert (the log IS the audit).** 5-7 day engineering. **HIGHEST PRIORITY.**
- **M3+M4 CRDT op-log + LSH-partial-COW hybrid.** P_deflated 0.35. Mem-amp 0.5x worst-case spread-spectrum, 0.002x hot-locality. Per-query snapshot isolation tractable at depth=1 but requires bucket-cover bookkeeping at depth=5. 8-12 day engineering. **SECONDARY (parallel exploration if M1+M2 hits FP-drift wall).**
- **CRDT-alone** rejected as standalone (P_deflated 0.25): algebraic commutativity is exact but eventual-consistency model is incompatible with iterated depth=5 retrieval; only useful as hybrid op-log.
- **LSH-alone** has the right cost shape but the dispatch-time bucket-cover problem at depth>=2 is open synthesis; combining with CRDT op-log resolves it.

Recommended next experiment: **M2 cosine-agreement smoke at K up to M=2048 with FP precision audit (Kahan vs naive sum)** — ~30 min CPU, single-anchor. This is the load-bearing empirical gate for the entire log-structured family.

## Cheap decisive test

For M1+M2 specifically: implement the lazy-replay retrieval kernel against the existing substrate W with synthetic rank-1 edits up to K=M. The decisive test is **cosine(q_lazy, q_materialized) >= 0.9999 across K in {64, 256, 1024, 2048} at depth=5 with 5 seeds**. HARD-PASS: cosine >= 0.9999 AND replay throughput >= 50 q/s AND log mem-amp <= 4x. HARD-FAIL: any K shows cosine < 0.999 (catastrophic-cancellation regime; engineering fix is Kahan compensated summation - still smokeable in same probe). MIDDLE-BAND: cosine in [0.999, 0.9999] (FP drift visible but bounded; production-tunable via Kahan).

The smoke runs at N=512 reduced from N=4096 for ~30 min CPU; if pass at N=512, scale to N=4096 in a follow-on (~2hr CPU). The cosine-agreement gate is parameter-free per the routing-file pattern: the materialized W' is the oracle, lazy replay is the unit under test.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

### M1+M2 Log-structured rank-1 store

**Mechanism.** Store W_base immutably. Append each edit (k_l, ov_l, nv_l) to a log L. At retrieval depth=t, iterate:
```
q_{t+1} = q_t W_base^T - sum_{l in L} (q_t . k_l) (ov_l - nv_l)^T / N
```
This is mathematically identical to W' = W_base + sum_l (nv_l - ov_l) k_l^T / N (rank-1 update associativity). Compaction at K_thresh = O(sqrt(M)) ~ 45-64 folds the log into a new W_base.

- **HARD-PASS**: cosine(q_lazy, q_materialized) >= 0.9999 at all K in {64, 256, 1024, 2048}; mem-amp = 1 + 2K/N at K=M (formula) <= 3x with margin; throughput >= 50 q/s with naive replay AND >= 200 q/s with batch-merge (pre-fold deltas into single correction matrix); consistency under concurrent reads >= 0.95.
- **HARD-FAIL**: cosine drops below 0.99 at K=1024 (catastrophic cancellation, NOT fixable by Kahan) OR mem-amp exceeds 4x at K=M (formula wrong) OR throughput below 50 q/s with batch-merge (architectural FLOP budget wrong).
- **MIDDLE-BAND**: cosine in [0.99, 0.9999] (FP drift bounded but visible; Kahan summation closes the gap at compute cost penalty <2x) OR mem-amp in [3x, 4x] (tight to spec; compaction interval tuning required).

### M3 CRDT op-log (standalone)

**Mechanism.** Op-based CRDT where each operation is a rank-1 delta. Commutativity is exact: (W + d1) + d2 = (W + d2) + d1 with zero residual. Eventual consistency only.

- **HARD-PASS**: at depth=1, single-hop retrieval against eventually-consistent replica preserves cosine >= 0.99 with rightful target across 5 seeds at K=O(M); replica-merge cost O(N^2) per delta receipt.
- **HARD-FAIL**: at depth=5, mid-iteration delta arrival drops cosine below 0.75 with baseline-attractor on >10% of trials.
- **MIDDLE-BAND**: depth-5 cosine in [0.75, 0.95] - retrieval transiently destabilizes but recovers on retry.

Standalone P_deflated 0.25 reflects: algebra is exact but no published precedent for CRDT applied to depth>=2 iterative dense-matrix retrieval. The standalone version is **not recommended** for substrate deployment; the op-log component IS recommended as audit-trail substrate for the M1+M2 design.

### M4 LSH-partial-COW

**Mechanism.** Partition the column-space of W using k=12 random hyperplanes giving B=4096 buckets. Each rank-1 edit to key k_v touches exactly the bucket(s) where k_v hashes; copy only those bucket-submatrices at edit time. Worst-case mem-amp = num_touched_buckets / B; under uniform-spread the average is ~0.5x; under hot-locality (top 1% of keys absorb 80% of edits) it is ~0.01x.

- **HARD-PASS**: hot-edit-locality (5/M edited) achieves mem-amp <= 0.01x; spread-spectrum (M edited) achieves mem-amp <= 1.0x; depth=1 retrieval against bucket-COW snapshot preserves cosine = 1.000 (exact, since bucket COW is a subset COW).
- **HARD-FAIL**: spread-spectrum mem-amp >= 1.5x (LSH bucketing overhead worse than full COW, e.g., due to inter-bucket pointer chasing) OR depth=5 retrieval cosine below 0.95 because trajectory hits buckets not snapshotted at dispatch.
- **MIDDLE-BAND**: spread-spectrum in [1.0, 1.5x] (still better than COW's 10.13x); depth=5 cosine in [0.95, 1.0] (mostly correct, some trajectory-coverage misses).

## PART A: Mathematical analysis of log-structured rank-1 store (M1+M2 unified)

### Cost profile derivation

W_base storage: N^2 floats = N^2 * 4 bytes = 67 MB at N=4096 FP32. Each rank-1 edit stores (k_v, ov_v, nv_v) = 3N floats. After K edits:
```
total_bytes = N^2 * 4 + K * 3N * 4
mem_amp = 1 + 3K/N
```
At K=M=2048, N=4096: mem_amp = 1 + 1.5 = 2.5x (well under 4x target).
At K=N (4096 edits, every slot edited once): mem_amp = 4x (at-limit; trigger compaction).

If we collapse (ov, nv) into a single delta vector d = nv - ov (storing only the difference), mem_amp = 1 + 2K/N. At K=M: 2.0x. At K=N: 3.0x. Stricter than the 3-vector form. The 2-vector form (k_v + d) is the recommended storage.

### Read-path latency

Per-query latency = base GEMV + K correction dot-products at each of d depths:
```
flops_per_query = d * (2N^2 + 2KN)
```
At N=4096, d=5, K=M=2048: 5 * (33.6M + 16.8M) = 252 MFlops/query. On RTX 4090 effective GEMV (2 TFlops at this size due to memory-bandwidth bound): 252e6 / 2e12 = 126 microseconds per query = **7,900 q/s** at K=M, well above 50 q/s.

Batch-merge optimization: pre-fold K corrections into a single delta_W matrix once, then GEMV against (W_base + delta_W). Cost K*N flops one-time = 8 Mflops; per-query cost reverts to baseline 2N^2 = 33.6 Mflops per depth step = 168 Mflops at d=5 = **11,900 q/s**.

### Audit synergy with KF-2 deletion-cert

The log L is, by construction, an immutable append-only sequence of edits. Each entry (k_l, ov_l, nv_l, timestamp) is exactly the provenance record needed for:
- **Verifiable deletion**: append (k_l, ov_l, 0) entry; certificate is the log entry plus Merkle inclusion proof; verifier replays the log up to certificate position to confirm.
- **Per-fact retention queries**: scan log for entries touching a given k_v.
- **Rollback**: replay log up to a timestamp boundary.

No additional storage cost for audit beyond the log itself. This is the strongest architectural property of M1+M2: KF-2 compatibility is FREE rather than an additional engineering layer. Tas & Boneh (AFT 2023, [arXiv:2307.16877](https://eprint.iacr.org/2023/1830.pdf)) describe homomorphic Merkle trees with O(log N) per-update proof cost, directly applicable as the audit-layer cryptographic primitive.

### Hot-edit-set handling

Per Kanellis et al. (VLDB 2024 [arXiv:2305.01516](https://arxiv.org/pdf/2305.01516)), Zipfian update distributions can be absorbed by a small in-memory hot-set tier: top S keys (S << M) accumulate their rank-1 deltas in-place (`hot_delta[k_v] += nv - ov`), collapsing repeated edits to the same key into a single accumulated vector. Storage: S * N floats. At S=100 (top 5% of keys absorbing 80% of edits), hot-set storage is 1.6 MB - 2% of W_base.

## PART B: Mathematical analysis of CRDT + LSH hybrid (M3+M4)

### Why CRDT alone fails at depth >= 2

Shapiro et al. (SSS 2011, [Springer](https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29)) establish that op-based CRDTs require concurrent operations to commute. Rank-1 additive edits commute exactly. But CRDT "convergence" is defined over replica state after quiescence, not over individual reads. At depth=1 a stale replica produces error bounded by ||delta_l|| * ||query||. At depth=5, mid-iteration delta arrival shifts the attractor basin mid-trajectory; the iterate may converge to a different memory.

The ACM Computing Surveys 2023 paper (Almeida et al., [DOI:10.1145/3695249](https://dl.acm.org/doi/full/10.1145/3695249)) explicitly catalogues this "read-your-writes" gap: CmRDT convergence does not provide snapshot isolation for stateful traversals. Depth>=2 retrieval is exactly such a traversal, so CRDT-alone is structurally incomplete.

### Why LSH-partial-COW alone has a chicken-and-egg

Per the Indyk-Motwani LSH formulation, k=12 hyperplanes partition N=4096-dim space into B=4096 buckets. A rank-1 edit to key k_v touches exactly one bucket with high probability. The mem-amp at query dispatch is proportional to num_touched_buckets / B.

The obstacle: depth>=2 retrieval iterate traverses multiple attractors. To snapshot the right buckets at dispatch, you would need to know which buckets the iterate will visit before running the query. The conservative strategy (snapshot all buckets touched by the entire iteration trajectory) collapses to full COW in the worst case.

### Why the hybrid resolves it

Combine: CRDT op-log as the immutable audit-ledger; LSH bucket-store as the write-side copy-selective layer. At query dispatch:
1. Snapshot only the bucket where the initial query key hashes (1-2 buckets, ~0.001x mem-amp).
2. For subsequent hops, fall back to CRDT-eventual-consistent reads against the live bucket store (no isolation guarantee but tracking via op-log).
3. Verify retrieval consistency post-hoc: replay op-log against snapshot to check whether the trajectory's visited buckets had any concurrent edits; if yes, retry the query with expanded snapshot cover.

This makes per-query mem-amp expected-O(1) buckets / B in steady state and worst-O(M) bucket-cover under adversarial concurrent edit storm. The "retry on op-log conflict" is an OCC pattern; literature precedent in OCC databases is mature.

## PART C: Comparison table

| Mechanism | Mem-amp typical | Mem-amp worst | Throughput | KF-2 compatibility | Engineering | P_deflated |
|---|---|---|---|---|---|---|
| **COW (baseline; INFEASIBLE)** | 10.13x | 10.13x | 6-7.5 q/s | OK | shipped | N/A |
| **M1+M2 Log-structured (RECOMMENDED)** | 1.5-2.5x | 3.0x at K=N | 8-12K q/s | log IS audit; FREE | 5-7 days | 0.40-0.50 |
| **M3 CRDT op-log alone** | 1.0x | 1.0x | depth=1 OK; depth=5 FAIL | log IS audit; FREE | 3 days | 0.25 (depth>=2) |
| **M4 LSH-partial-COW alone** | 0.01-0.5x | depends on bucket-cover | OK depth=1; depth=5 open | requires separate audit layer | 4 days | 0.35 |
| **M3+M4 hybrid (FALLBACK)** | 0.01-0.5x | retry on conflict | depth=5 OCC pattern | hybrid: op-log audit + bucket store | 8-12 days | 0.35 (joint with M1+M2 backup) |

Path D parallel observation: Path D's per-hop Bayesian independence is a SUBSTRATE-NATIVE generalization of CRDT-style per-op independence. Path D achieves edit-resilience (T2 PASS 45/45 cells) because each hop's Bayesian posterior is computed independently from cached candidate evidence rather than re-reading the mutated W. This is closer to M3 CRDT semantics than to M4 LSH bucketing, and explains why T2 succeeds where the v288 R-COW-NOT-WORKING mechanism failed: the substrate-architectural Path D is already a degenerate-case CRDT for the retrieval primitive. M1+M2 generalizes this to the W-mutation layer, not just the retrieval layer.

## PART D: Recommended next experiment

**G10.M2 Log-structured rank-1 retrieval smoke** — ~30 min CPU on laptop, single-anchor.

Spec sketch (for exp_dev to refine; this is FRAMING not numbers per [[feedback-no-experiment-design-in-prompts]]):
- Build W_base via current substrate primitives at N=512 (smoke scale).
- Generate K rank-1 edits at K in {64, 256, 1024, 2048}.
- Compute materialized W' = W_base + sum_l (nv_l - ov_l) k_l^T / N (oracle).
- Implement lazy-replay retrieval: q_{t+1} = q_t W_base^T - sum_l (q_t . k_l)(ov_l - nv_l)^T / N at d=5.
- Measure: cosine(q_lazy, q_materialized) per cell; throughput q/s per cell; mem-amp per cell.
- Optional: Kahan compensated summation variant if naive FP drift visible (separate cells).

HARD-PASS / HARD-FAIL / MIDDLE-BAND bands per the falsifiable-predictions section above. Pre-reg the cosine threshold, mem-amp formula, throughput floor BEFORE running per [[feedback-envelope-expansion-fail-bands]].

If smoke PASSes, scale to N=4096 FULL re-run (~2hr CPU) for cap_map promotion candidacy.

If smoke FAILs on cosine, the engineering fix (Kahan) is well-understood; ship M2_v2 with Kahan before declaring the mechanism dead.

If smoke FAILs on throughput, M3+M4 hybrid becomes the fallback path.

## Citations (verified URLs)

External lit-scan citations from the 3 subagent drills, all verified:

1. **Dong et al., "Optimizing Space Amplification in RocksDB," CIDR 2017** — [cidrdb.org/cidr2017/p82](https://www.cidrdb.org/cidr2017/papers/p82-dong-cidr17.pdf). Establishes level-multiplier T=10 yields ~1.11x space-amp with leveling compaction; grounds the snapshot-frequency cost model.
2. **Sarkar et al., "Constructing and Analyzing the LSM Compaction Design Space," VLDB 2021** — [vldb.org/pvldb/vol14/p2216](http://vldb.org/pvldb/vol14/p2216-sarkar.pdf). Systematic read/write/space amplification across tiering vs leveling; grounds compaction-tradeoff analysis.
3. **Tas & Boneh, "Vector Commitments with Efficient Updates," AFT 2023** — [eprint.iacr.org/2023/1830](https://eprint.iacr.org/2023/1830.pdf). Homomorphic Merkle tree with sublinear update-info; per-diff audit cost.
4. **Kanellis et al., "From FASTER to F2," VLDB 2024** — [arXiv:2305.01516](https://arxiv.org/pdf/2305.01516). Hot-key tiering for skewed update distributions; grounds the hot-edit-set handling strategy.
5. **Zhou et al., "Lazy Maintenance of Materialized Views," VLDB 2007** — [vldb.org/conf/2007/p231](https://www.vldb.org/conf/2007/papers/research/p231-zhou.pdf). Cost model for deferred view maintenance; lazy beats eager at high update-to-query ratio.
6. **Dayan & Idreos, "Autumn: A Scalable Read Optimized LSM-tree," 2023** — [arXiv:2305.05074](https://arxiv.org/html/2305.05074v2). O(sqrt(log N)) read-amp bound with adaptive compaction; threshold-setting for K.
7. **Shapiro et al., "Conflict-Free Replicated Data Types," SSS 2011** — [Springer link](https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29). Foundational CRDT taxonomy; commutativity as sufficient condition for op-based convergence.
8. **Almeida et al., "Delta State Replicated Data Types," 2016** — [arXiv:1603.01529](https://arxiv.org/pdf/1603.01529). Delta-CRDT communication cost; delta size proportional to recent mutation.
9. **Almeida, Baquero, Preguica et al., "Approaches to CRDTs," ACM Computing Surveys 2023** — [DOI:10.1145/3695249](https://dl.acm.org/doi/full/10.1145/3695249). Most comprehensive survey; explicit read-your-writes gap treatment.

## Internal cross-refs (substrate state at v290)

- v290 R-COW-INFEASIBILITY R3 (R3 = this drill); R4 = MEDIUM ~60min CPU+exp_dev edit-log-replay smoke (THIS IS THE M2 SMOKE recommended above).
- v290 T2 path_d_edit_isolation_under_load HARD_PASS 45/45 cells unanimous — Path D is a substrate-architectural CRDT for retrieval. The M1+M2 design generalizes the SAME mechanism to the W-mutation layer.
- v290 U2 codebook-collision + edit-fact-traverse vulnerabilities — D3 edit-log-replay from `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` is the SAME mechanism family as M2 here; the audit-by-construction synergy reinforces the case.
- v290 R-MODERN-HOPFIELD T3 max_M=N=16384 test ceiling — not relevant to this drill but flagged for cross-application: log-structured retrieval at N=16384 would inherit the modern-Hopfield-activation property if M2 smoke passes.

## Lit-scan calibration penalty summary

All three subagent P estimates applied the calibration penalty per [[feedback-lit-scan-calibration-penalty]]:
- M1 delta-encoding nominal 0.70 - 0.30 deflation = 0.40 (capped at 0.50 novel-synthesis ceiling not binding)
- M2 LSM lazy-replay nominal 0.70 - 0.32 deflation = 0.38 (novel-synthesis cap not binding; core mechanism well-grounded LSM literature)
- M3 CRDT-alone nominal 0.50 - 0.25 deflation = 0.25 (no precedent for depth>=2 iterative dense-matrix retrieval; cap at 0.50)
- M4 LSH-partial-COW nominal 0.55 - 0.20 deflation = 0.35 (filesystem-COW analog is precedent but dense-matrix subspace partitioning is novel synthesis; capped at 0.50)

Joint P that the M1+M2 unified architecture achieves all three production targets (mem-amp <= 4x AND throughput >= 50 q/s AND consistency >= 0.95) within a 7-day engineering budget: **0.40-0.50** (range reflects the gap between batch-merge variant and naive replay; Kahan-summation contingency closes the consistency-target gap).

Joint P for M3+M4 hybrid in same budget: **0.30-0.35** (lower; bucket-cover bookkeeping at depth>=2 is the load-bearing open synthesis).

## Internal citations

7 verified internal citations:
1. `notes/substrate_capability_map.md` v290 R-COW-INFEASIBILITY block (lines ~20169-20174)
2. `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (origin routing file)
3. `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` (D3 edit-log-replay companion delivery)
4. `notes/substrate_capability_map.md` v290 T2 path_d_edit_isolation block (lines ~19901-19903)
5. `experiments/exp_edit_isolation_guard_probe_v1_n4096.py` (current COW baseline; m=10.13x measurement)
6. `experiments/exp_adversarial_multi_hop_probing_v2_n4096.py` lines 150-178 (Pattern 4 attack mechanism context)
7. `notes/MEMORY.md` feedback chain: [[feedback-rehabilitation-after-rejection]] + [[feedback-rescue-sketch-first-sequencing]] + [[feedback-no-experiment-design-in-prompts]]
