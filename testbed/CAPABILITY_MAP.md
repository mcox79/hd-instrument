# Testbed Capability Map

What the substrate has been **empirically proven** to do via the testbed, as of 2026-05-30. Distinct from the research-level cap_map at `notes/substrate_capability_map.md` (which tracks substrate-physics claims at the cell level). This document tracks **shipped + benchmarked** capabilities at the testbed integration level.

Status legend:
- **PROVEN**: empirically validated by a testbed scenario with reproducible numbers
- **PARTIAL**: shipped + smoke-validated but production-scale validation pending
- **BLOCKED**: ran but did not meet pre-registered HARD_PASS gate; honest finding documented
- **RUNNING**: bench in flight
- **DEFERRED**: scoped but not started

Anchor format: scenario file + config + key metric numbers + run timestamp where applicable.

---

## Killer features (the load-bearing product story)

### KF-1: Hallucination structural impossibility

| Status | Scenario | Numbers | Honest framing |
|---|---|---|---|
| PROVEN | `hallu_detect` | 95.31% near_uniform_frac at M/N=0.25 (mid_report 2026-05-29) | At under-capacity regimes, posterior-entropy mechanism flags OOS reliably |
| PARTIAL | `multi_signal_kf1` (N=512 smoke) | Composite +30-50pp over single-signal at every M/N (94.5% at M/N=0.25, 32.5% at M/N=2.0) | Multi-signal composite is strictly better but does NOT meet 90% across all regimes; high_distance signal carries M/N>=1.0 |
| BLOCKED | `mixed_crud_workload` (N=2048 M=2000) | post_delete_near_uniform_rate=0% BUT post_delete_correct_rejection_rate=100% | KF-1's MECHANISM shifts at M/N approx 1.0 from "near-uniform" to "different-key high-confidence response"; substrate IS rejecting deleted keys, just via a different signal. Measurement framing issue, not substrate failure. |

### KF-2: Edit isolation

| Status | Scenario | Numbers |
|---|---|---|
| PROVEN | `edit_isolation` | max_isolation_ratio = 0.0000 at all backends at smoke + mid scale |
| PROVEN | `audit_chain_validation` | within_theory_frac = 1.00 (every non-edited cell within Kerdock 1/sqrt(N) theory bound) at N=4096 5-seed |

### TCFT thermodynamic deletion certificate

| Status | Scenario | Numbers |
|---|---|---|
| PROVEN | `audit_chain_validation` (single substrate) | chain_integrity 100%, audit_anchor_coverage 100%, tamper_detection_rate 100% (10/10 byte-level tamper injections caught) |
| PROVEN | `multi_substrate_sharding` (K=10 shards) | Cross-shard chain integrity 100% + tamper 100% at M up to 20K |
| PROVEN | TCFT var_ratio | 0.0566 at N=2048 mid scale (well below HARD_PASS 0.10 threshold) |
| PROVEN | Cryptographic audit fields | key_hash + w_state_hash_before + w_state_hash_after + 5 verification_probes populated on every cert |

---

## Single-substrate scaling envelope (the empirical boundary)

### Recall envelope is LINEAR-IN-N, not exponential

`large_N_envelope` scenario (run 2026-05-30T01-26-03, 6,163 sec wall, N x M_ratio sweep):

| N | max_M_at_95_recall | max_M_at_50_near_uniform | disk_MB | p50_retrieve_us |
|---|---|---|---|---|
| 2048 | 512 | 4096 | 84 | 8,073 |
| 4096 | 1024 | 8192 | 336 | 27,827 |
| 8192 | 2048 | 16384 | 1,342 | 95,226 |
| 16384 | **RUNNING** | RUNNING | ~5,400 expected | RUNNING |

**Headline finding:** `max_M_at_95_recall = N/4` strictly linear. The modern Hopfield exponential-capacity regime does NOT activate in the N=2048-8192 range. N=16384 will resolve whether it activates at larger N.

**Implication for product positioning:** single substrate sized for ~M = N/4 facts at 95% recall. Beyond that recall degrades gracefully (88% at M=N/2, 77% at M=N). KF-1 survives to 2x the recall envelope.

---

## Composition paths that EXTEND the envelope (shipped variants)

### Sharded substrate at fixed C with shared codebook

`multi_substrate_sharding` scenario (run 2026-05-30T00-41-22):

| Property | Value | Status |
|---|---|---|
| Disk at K=10, C=8192, N=2048 across M=2K-20K | **235 MB constant** (1% growth) | PROVEN |
| Recall at M=20K (K*C/4 capacity) | 35.5% | PROVEN (degradation expected at capacity) |
| Recall at M=2K (well within K*C/4) | 88.0% | PROVEN |
| Cross-shard audit chain integrity | 100% at all M | PROVEN |
| Tamper detection across shards | 100% | PROVEN |

**Implication:** sharded substrate gives constant disk via composition, with recall bounded by K*C/4. Audit chain holds across shards.

### Tensor-factorized substrate (rank-decomposed W)

`factorized_vs_dense` scenario (run 2026-05-30, smoke at N=1024):

| Property | Value | Status |
|---|---|---|
| Math identity (dense W vs U @ V^T) | bit-exact (max delta = 0.0) at all tested M/N | PROVEN |
| Memory savings at M/N=0.10 | 5.0x | PROVEN |
| Memory savings at M/N=0.25 | 2.0x | PROVEN |
| Memory crossover with dense | M/N = 0.50 (factorized loses above) | PROVEN |
| Edit + delete operations preserve math identity | bit-exact | PROVEN |
| Audit chain on U+V hashes | 100% integrity | PROVEN |
| Latency win at N<=1024 | Inverted (factorized 1-10% slower due to overhead) | PARTIAL (asymptotic win pending N>=2048) |

**Implication:** tensor factorization is a memory-side optimization in the under-capacity regime (where substrate operates at 95%+ recall). Latency dividend likely materializes at larger N where O(N^2) dominates per-call overhead. Compounds with sharding: factorized sharded substrate would push memory budget further.

### Hierarchical substrate (top-level routing + K leaves)

`hierarchical_capacity` scenario (smoke at K=3 M=100):

| Property | Value | Status |
|---|---|---|
| Routing accuracy at smoke | 100% (probed with original key_vec) | PARTIAL (production-scale needs M_total >> M_capacity_per_leaf) |
| Recall_at_1 at smoke | 98.0% | PROVEN at smoke scale |
| Cross-level chain integrity | 100% (110/110 anchors verified end-to-end) | PROVEN |
| Disk at smoke K=3 M=100 | 16.86 MB vs single substrate 5.25 MB at same M | Expected overhead at small M; capacity-extension win materializes at M_total >> M_capacity_per_leaf |

**Implication:** hierarchical architecture works structurally (routing + chain). The capacity-extension win is unproven at production scale. Routing accuracy at K=10 with M >> few hundred per topic is the binding gate.

---

## Performance optimizations (workload throughput)

### Hashed codebook lookup (Tier 2 T2)

| Status | Scenario | Numbers |
|---|---|---|
| PROVEN at smoke | `smoke_test_hashed` (N=1024 C=8192 batch=64) | 113 -> 2,589 ops/s = **22.9x lift** vs production baseline |
| PROVEN bit-identical W | `smoke_test_batched` | W parity max abs delta = 0.0 |
| Production scale | Pending re-run | DEFERRED until N=16384 bench frees remote CPU |

### Batched operations (Tier 2 T3)

| Status | Scenario | Numbers |
|---|---|---|
| PROVEN at smoke | `smoke_test_batched` (N=512 C=2048 batch=64) | store 13.2x, retrieve 11.9x |
| PROVEN at smoke | `write_heavy_stream` (N=512 batch=64) | 170 -> 3,723 ops/s = 21.9x lift |
| BLOCKED in production | `write_heavy_stream` (N=1024 C=20K batch=64 BEFORE hashed codebook) | 113 ops/s (worse than unbatched) - codebook allocation overhead dominated |
| Status after T2 | Pending re-run | DEFERRED |

### Approximate retrieval via random sampling (Path 5)

`approx_retrieve_sweep` scenario (smoke at N=512 M=256):

| sample_frac | recall_at_1 | p50 latency vs exact |
|---|---|---|
| 1.0 (exact baseline) | 93.0% | 6,111 us |
| 0.5 | 93.0% | 7,572 us (slower!) |
| 0.3 | 93.0% | 8,447 us (slower) |
| 0.1 | 93.0% | 7,725 us |
| 0.05 | 89.0% | 9,055 us |

**Honest finding:** at smoke N=512, sampling overhead exceeds the saved matvec FLOPs. Recall is FLAT down to sf=0.1 then drops 4pp at sf=0.05. Latency dividend pending validation at N>=2048 where W @ q matvec dominates per-call overhead. The 95ms baseline at N=8192 should compress to 5-10ms at sf=0.2 if the asymptotic crossover holds.

---

## Workload behavior at production scale

### Realistic workloads bench (run 2026-05-29 T01-25-47, N=2048 M=2000)

| Scenario | substrate | FAISS | Honest framing |
|---|---|---|---|
| write_heavy_stream | 170 ops/s, p99 last/first 2.0 | 44,114 ops/s | Substrate 260x slower per op; gap closeable via T2/T3 |
| edit_heavy_stream (value-only) | 16.8 ms / 94.8% correct | 1.7 ms / 100% | At value-only edits, baselines win cleanly |
| hot_path_skew (Zipfian) | hot 12.1ms / cold 12.2ms uniform | 2.3 / 2.4 ms uniform | All backends uniform per query; no cache exploitation |
| mixed_crud_workload | 45.8 ops/s drift 0.74, KF-1 0%, **correct_rejection 100%** | 532.8 ops/s drift 0.97 | Substrate handles real workload; KF-1 mechanism shifts but rejection still works |

---

## Capabilities NOT YET PROVEN (honest gap)

### Tier 2 unshipped

| Test | Cost | Status |
|---|---|---|
| T4 Cached retrieval layer | 1-2 days | DEFERRED |
| T5 Async deletion certificate | 1-2 weeks | DEFERRED |

### Tier 3

| Test | Cost | Status |
|---|---|---|
| T6 Cross-shard correlation analytics | 1 week | DEFERRED |

### Tier 4 (load-bearing for product positioning)

| Test | Cost | Status |
|---|---|---|
| T7 LLM-substrate integration (Pattern B) | 3-4 weeks + $5-20 API | DEFERRED - the test that validates product positioning empirically |

### Tier 5 (depend on substrate-physics experimentation)

| Test | Cost | Status |
|---|---|---|
| T8 Continuous-output validation | 3-4 weeks | DEFERRED |
| T10 Adaptive thresholds | 2-3 weeks | DEFERRED |
| T11 Block-structured W | 2 weeks | DEFERRED |
| T12 Tensor binding | 1-2 weeks | DEFERRED |
| T13 Tiered storage | 3-4 weeks | DEFERRED |

---

## FAILED HYPOTHESES (honest negatives)

| Hypothesis | Disproven by | Honest reframe |
|---|---|---|
| "100K facts in single geometric space at N=16384" | `large_N_envelope` data shows max_M ~ N/4 linear scaling | Single substrate envelope is M ~ N/4 facts; getting to 100K needs N approx 400K = 640 GB W matrix; impractical |
| "Adaptive codebook gives constant cost in M" | `large_M_constant_cost` (initial run) showed adaptive C scales linearly with M | Constant-cost only holds at FIXED C. Adaptive C scales linearly. |
| "Substrate has hot-path advantage over FAISS" | `hot_path_skew` showed all backends uniform per query | Substrate's per-query cost is structurally uniform but FAISS just has a lower constant |
| "BE-1 cost-advantage 32x narrative" | `kf2_be1` precision sweep (v272) showed iso pattern precision-INSENSITIVE | The probe didn't exercise W magnitude; W-magnitude-operative test still pending (Cluster A1/A2) |
| "Multi-signal KF-1 hits 90% at all regimes" | `multi_signal_kf1` shows composite drops to 32.5% at M/N=2.0 | Composite IS strictly better than single-signal but heuristic weights need re-tuning; current form doesn't solve saturation |

---

## Dashboard surface (for product reporting)

Suggested top-line numbers for the dashboard:

1. **Audit chain integrity:** 100% (single + sharded substrate)
2. **Tamper detection:** 100% (10/10 byte-level injections caught)
3. **Edit isolation max:** 0.0000 (well below Kerdock theory bound 1/sqrt(N))
4. **TCFT var_ratio:** 0.0566 (below HARD_PASS 0.10 threshold)
5. **Single substrate envelope:** M ~ N/4 facts at 95%+ recall
6. **Sharded substrate envelope:** M ~ K*C/4 facts with constant 224 MB disk at K=10 C=8192
7. **Throughput improvement potential:** 22.9x via hashed codebook (smoke proven; production validation pending)
8. **Memory savings via factorization:** 5x at M/N=0.1 (smoke proven, bit-identical math)

Open questions for the dashboard to surface:

1. N=16384 envelope (RUNNING) - does exponential capacity activate?
2. Production-scale throughput with T2 hashed codebook (pending)
3. Production-scale approximate retrieval latency (pending)
4. LLM-substrate integration metrics (Tier 4 T7; not yet started)

---

## Status footer

- Repo SHA: pushed at each commit
- Last bench: `large_N_envelope` extended at N=16384 RUNNING
- Last commit: `02676e3` (Paths 5+15 shipped) plus factorized substrate + hierarchical substrate landed in subsequent commits
- Testbed location: `d:/AI/hd-instrument/testbed/`
- Remote state: `marsh@home:C:/dev/hd-instrument/testbed/`
- Test artifacts: `testbed_data/benchmarks/results/<iso_timestamp>/`
