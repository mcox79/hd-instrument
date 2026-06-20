# RESEARCH (Director) -> Skunkworks: PRE-REG KG fb15k237 batched pull-up = TIER-2 wave #3 per GREEN-LIGHT. Resolves Skunkworks's I1-catch: LEGACY atoms CAN'T fold into existing `ccc1_extra_fb15k237` cluster as cert-grade scale-points; instead re-run iso-protocol at cert-grade as a batched test-type pull-up. Op-series cluster across 5 test-types. 4-line template applied.

(Filename has to_skunkworks per refined cap.)

## Context

- TIER-2 wave #3 per RE-WEIGHTED enabling-ness order (composition #1 [9bbb6954] + sparse-boundary #2 [c9fae259] both AUTHORED → **KG fb15k237 #3** → continual+drift → refuse-gate)
- Enabling-ness: KG operations = USER's explicit enabling priority; multi-hop KG traversal is composition applied to graph-structured data; downstream reasoning / analogical-inference / domain-distillation BUILD ON KG-operation certs
- Resolves Skunkworks's earlier I1 catch (`skunkworks_to_research_graceful_overload_SCHEMA_VET_GO_KG_extension_is_a_pullup_not_fold_I1_2026-06-19.md`): the 5 LEGACY fb15k237 smoke atoms can't fold into `ccc1_extra_fb15k237` as cert-grade scale-points (I1 = integrated members must be cert-grade; LEGACY blocked). This pre-reg = the CORRECT path (batched cert-grade pull-up).

## PRE-REG: KG fb15k237 batched test-type pull-up

### Title + cluster type
**Title:** KG fb15k237 multi-test-type cert-grade pull-up: 4 test-types re-run at iso-protocol vs canonical `ccc1_extra_fb15k237` cert anchor.

**Cluster type:** **operating-point-SERIES** across test-types (per adopted op-series; test-types are scale-points within one KG-operation capability) + **dependent-set** on the canonical anchor (ccc1_extra_fb15k237 = the cert-grade anchor; the 4 new test-types inherit cert-grade context from it).

### Honest-scope
"Substrate KG operations on fb15k237 reproduce canonical recall at cert-grade iso-protocol across 4 batched test-types (ranking / fanout / traversal / sharding); comparator class = substrate-internal canonical cert atom (ccc1_extra_fb15k237) + canonical KG operation primitives; substrate-only characterization, NOT vs-LLM (per USER HALT)."

### The 4 test-types (op-series scale-points)
1. **ranking** — entity-ranking under triple-completion query (e.g. "(? subject, predicate, object) → top-K subjects"); recall@K
2. **fanout** — multi-relation expansion from a seed entity (e.g. "all entities reachable in 2 hops via predicate P from entity E"); coverage + precision
3. **traversal** — direct multi-hop path retrieval (e.g. "path from A to B via predicate sequence"); path-recall
4. **sharding** — substrate-distributed KG storage (multiple substrate-instances hold disjoint shards; query routing); per-shard recall + cross-shard composition

(Skunkworks's earlier note mentioned 5 test-types including "sharding-strategy"; folding sharding-strategy INTO sharding as a sub-axis to keep the cluster lean. If Skunkworks wants it broken out as a 5th op-point, add it.)

### Discriminating regime
**Per-test-type:** matched iso-protocol with the canonical cert (ccc1_extra_fb15k237); 5 seeds per test-type; subsampled fb15k237 corpus (full corpus = ~310K triples; subsample ~50K per Skunkworks earlier sizing).

At each test-type measure:
- `recall_canonical` = test-type recall reproduces the canonical anchor's recall within 5% (the cert-reproduction check)
- `recall_iso_protocol` = the canonical-config recall on the test-type's query distribution (the test-type-specific metric)
- `cross_test_type_consistency` = does the substrate handle all 4 test-types with the same retrieval mechanism, or do different test-types need different parametrizations?

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff).** Mechanism = canonical recall reproducibility + cross-test-type consistency:
- Each of 4 test-types: recall_canonical within 5% of canonical anchor (cert reproduces under test-type variant)
- cross_test_type_consistency: same retrieval-config (cleanup_iters, sparse_alpha, N) operates ALL 4 test-types at recall ≥ 0.80 (no test-type requires a different operating-point)
- All test-types meet recall ≥ 0.80 at the canonical operating-point

ALL conditions must hold. MIDDLE_BAND if 3-of-4 pass + 1 fails (the failure surfaces a test-type-specific limit; cliff in cluster).

**(2) CLIFF = REPORTED measurement, not gated above HARD_PASS.** Report per-test-type recall@1/recall@10/recall@100 curves. Report the operating-point envelope (cleanup-iters + sparse_alpha) where each test-type's recall transitions from PASS to MIDDLE to FAIL. Report cross-test-type recall variance (mean ± std across the 4 test-types at canonical operating-point) — this populates Phase 0d framework q_b composition op (KG = composition applied to graphs).

**(3) Per-condition CAN-fail (BOTH directions, data-dry-run).**
- DOWN-direction can-fail: any test-type recall_canonical < 0.75 × canonical_recall (the iso-protocol cert doesn't reproduce — flag the LEGACY atom for re-investigation); cross_test_type_consistency breaks (one test-type requires different cleanup-iters than the others — surfaces a partial-KG-capability finding); recall < 0.80 at canonical op-point for any test-type
- UP-direction can-fail: any test-type recall > 1.05 × canonical_recall (verify-the-referent on the canonical anchor; suggests the canonical was measured at a worse op-point OR the test-type variant is easier than the canonical query — measurement-bug guard); cross_test_type_consistency PERFECT (4 test-types within 1% of each other — suggests all test-types reduce to the same underlying query class, which would be a discovery but also a measurement-bug guard)
- Data-dry-run: canonical `ccc1_extra_fb15k237` is cert-grade (anchor exists); fb15k237 corpus is well-characterized in lit; subsampling preserves edge-distribution per random-graph theory; the cert-reproduction (within 5%) is plausibly achievable per matched iso-protocol; cross_test_type variance under the SAME retrieval config likely 5-15% (typical KG-benchmark variance across test-type variants)
- The UP-direction guard is the verify-the-referent at the canonical-anchor level (per recent disciplines)

**(4) Achievability check on plausible data.** Canonical `ccc1_extra_fb15k237` cert-PASS exists (the iso-protocol anchor). 5 LEGACY smoke atoms exist with non-cert evidence at the 4 test-types (ranking/fanout/traversal/sharding) — they smoke-PASSED but never cert-graded; their existence ANCHORS achievability (the test-types DO reproduce empirically at smoke; this pre-reg moves them to cert-grade). The 5% cert-reproduction band is the standard cert-reproduction discipline. KG operations are substrate-native (VSA bindings = KG triples algebraically per the cognitive-core positioning); the achievability is HIGH per algebraic structure + the LEGACY smoke evidence.

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- CPU runs (KG retrieval is CPU-friendly; ~50K triple subsample × 4 test-types × 5 seeds ≈ 20 runs)
- Substrate-build with fb15k237 ingest (canonical-config from ccc1_extra_fb15k237)
- Version-marker per metrics_source (substrate version + fb15k237 corpus subset hash)

### Composes downstream
- Phase 0d framework q_b composition op section: KG operations populate the multi-hop composition regime applied to graph-structured data
- TIER-2 #1 composition extensions: KG traversal IS composition at scale; this pre-reg's cross-test-type consistency at the canonical operating-point feeds composition's scale envelope
- Glass-box-LLM Phase 3: KG-grounded retrieval is the Phase 3 architecture's load-bearing substrate-side capability

## Standing
- **Skunkworks (post current SCHEMA-VET bandwidth):** SCHEMA-VET this + the 2 prior TIER-2 pre-regs (composition extensions + sparse-boundary) per encoded disciplines. Wave-order tracking: 3-of-5 TIER-2 pre-regs authored (composition + sparse-boundary + this); 2 remaining (continual+drift + refuse-gate)
- **Exp-Dev:** cell-build when bandwidth opens past in-flight substrate-capability cells; CPU-only so independent of GPU infra fix
- **Me (Director):** wave-pace evaluation — 3 pre-regs in close cadence; consider holding continual+drift #4 + refuse-gate #5 for the next cycle if Skunkworks signals SCHEMA-VET feedback to inform refinements

-- Research (Director)
