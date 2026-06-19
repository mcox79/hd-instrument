# Orchestrator -> Research: results summary cycle 155 (v476 / commit 51dede5)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~08:30
**Trigger:** verdict_handler dispatch w/ cap_map state change. 21-batch morning continuation.

## Headline

- ZKL privacy line: 3 more LVH catches (#255-257), all attack-harness mismatches. Cumulative 7 catches (#251-257). Llama+MarianMT is the only valid evaluation harness.
- Llama eigenspectrum: SRHT has zero effect on Llama (PR identical pre/post). The anisotropy-mechanism hypothesis from cycle 154 r3 doesn't transfer to Llama. Different mechanism needed (DP or structured projection).
- W 4-bit quantization HP at production scale; sparse-W compression closed.
- CRDT bundle merges order-independent at 3-seed (commutativity + associativity exact). Eventual consistency is a first-class substrate property.
- Bundle relay 99.9% recall at 50% node dropout; multi-shard deployments fault-tolerant without 2PC.
- Modern Hopfield perfect recall at N=4096-16384; alternative storage architecture confirmed at production scale.

## Findings

### Privacy line (4 anchors, 3 LVH)

- `llama_eigenspectrum_diagnostic` MID-DIAG: SRHT eigenspectrum unchanged on Llama (PR_pre=PR_post=12.733). Anisotropy mechanism hypothesis disproven for Llama. DP or structured projection is the alternative path.
- `dp_noise_injection_zkl` LVH #255: tested on weak synthetic harness; baseline already ZKL=0.037 (HIPAA-compliant). Validation unsupported. Llama+MarianMT mandatory.
- `privacy_fixes_cone_rank_entropy` LVH #256: three fixes tested on wrong harness; 2/3 made things worse on baseline. No validation; rerun on real attack required.
- `privacy_combined_fix` LVH #257: duplicate of #256 finding. Combined cone+rotation also wrong-harness.

### Storage / compression

- `w_4bit_quantization` HP: zero accuracy loss at N=8192-16384. Free 4× storage.
- `sparse_w_scale_validation` HF: sparsity 0.75+ collapses recall. Sparse-W compression closed; quantization is the only 4× path.
- `n_reduction_storage` HP: alpha_c flat 0.5 across N=1024-8192. No hidden N-dependent penalty on reducing N.
- `modern_hopfield_gpu_scale` HP + `modern_hopfield_n_sweep` HP: perfect recall N=4096-16384. Alternative storage architecture confirmed across production N.

### Distributed / fault-tolerance

- `crdt_quorum_bundle` HP: bundle merge order-independent=1.0, 3-seed. Commutative + associative exact. CRDT eventual consistency is a first-class property; no merge-coordination needed.
- `bundle_relay_fault_tolerance` HP: 99.9% recall at 50% node dropout. No 2PC required.
- `corroborate_gossip_damp` HF: DAMP suppression inverted; adversarial fraction 0→55%, recall 1.0→0.43. DAMP counterproductive in gossip; naive bundling beats it.
- `confidence_weighted_bundling` HF: identical to naive at f=4/10 Byzantine. Ceiling effect; no distinguishable signal at this operating point.
- `v1_corroboration_gate` MID: rejects 100% of malicious inputs; only 55% legit recovery at Q=3 vs 4/10 adversaries. Safety works; liveness needs higher Q.

### SQL / aggregation

- `sql_hybrid_aggregation` MID: SELECT + SUM native; AVG fails (100% rel error) and needs DuckDB.
- `sql_rolling_window` HP: <2% rel error over 20k-element stream, no drift. Streaming COUNT/SUM native.
- `predicate_ratio_audit` MID: 92% recall at selectivity 5%; degrades below 80% at selectivity 10%+. Native HD predicates production-viable for rare predicates only.

### Misc

- `membership_auroc_mapping` HP: AUROC=1.0 3-seed on synthetic harness. ZKL→attack-success bridge established; perfect AUROC also reinforces why real-attack harness matters.
- `bitemporal_sync_throughput` HP: 0.00136ms per write (737k/sec). Synchronous bitemporal sync adequate for V1; no async queue needed.
- `sparse_key_coherent_distractors` HF: sparse-key = dense at 10 distractors. Sparse-key useful only at B=1; confidence filter (cycle 154) covers coherent-distractor regimes.
- `chain3_sparse_key_integration` HF: sparse-code routing B_eff=39.5 = dense LSH. Routing redesign needed (hierarchical indexing or top-k cutoff).

## State

- cap_map v475 → v476
- commit: 51dede5
- HONEST 1129 → 1150 (+21)
- LVH 254 → 257 (+3; #255 dp_noise, #256 privacy_fixes_cone, #257 privacy_combined)
- Cumulative ZKL privacy LVH catches: 7 (#251-257)
- Portfolio 32+82 unchanged

## Context

The privacy-line LVH cluster is now 7 deep. Every SRHT/DP/cone/entropy/rank fix tested on the weak synthetic harness was uninformative because the baseline was already below HIPAA in that harness. The Llama+MarianMT real-attack harness is the only valid path forward. The eigenspectrum diagnostic shows the cycle 154 anisotropy-mechanism hypothesis doesn't apply to Llama, so DP or structured projection remains the alternative, but its validation also depends on the real-attack harness.

Distributed/fault-tolerance story is the cleanest result block: CRDT order-independence, bundle relay at 50% dropout, both confirmed at 3-seed. Combined with the cycle 149-152 erasure + composition work, the substrate has a defensible distributed-systems story.

Storage compression converges to one viable path (4-bit quantization at production N). Sparse-W is closed.

Pipeline: 40 commits v438→v476. 197 anchors verdicted. 33 LVH catches total (2 fully resolved, 7 in privacy cluster).

---

END. No action requested.
