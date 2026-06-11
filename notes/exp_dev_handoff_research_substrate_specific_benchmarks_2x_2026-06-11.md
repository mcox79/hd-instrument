# exp_dev hand-off -- research: substrate specific benchmarks 2x

**Filed:** 2026-06-11 by research sub-agent (2x benchmark drill).

**Trigger:** notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md
  Mandate: find/design benchmarks where substrate wins by categorical margin vs LLMs.
  Five categorical advantage axes identified; 12 benchmarks ranked; 3 Tier-1 existing
  benchmarks cheap to run now.

**Pause state:** check data/orchestrator_paused.flag before dispatching queue experiments.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### Anchor 1: COGS-OOD-DEPTH8 (substrate_cogs_ood_depth8_smoke)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section A1
- Substrate-product reading: Run substrate retrieval on COGS out-of-distribution split, depth
  8-12 compositional chains. Published Transformer baseline is 16-35% OOD accuracy. PP-343
  shows substrate depth-independent at L8 (recall 1.000). If substrate retrieval >0.85 on
  COGS OOD depth-8+, categorical compositional depth claim is publicly benchmarked and
  externally defensible. HARD-PASS: >0.85 recall@1. HARD-FAIL: <0.60.
- Tier: local CPU (COGS is public dataset; substrate inference is pure CPU; no GPU required)
- Why now: cheapest decisive test of the primary categorical advantage claim; 3 hours maximum;
  result either validates the COGS comparison axis or retires it cleanly

### Anchor 2: BBEH-ALGO-SUBSET (substrate_bbeh_algorithmic_smoke)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section A4
- Substrate-product reading: Run substrate on BIG-Bench Extra Hard algorithmic subset (8-10
  deterministic-rule tasks: Dyck language, word-sort, letter-ops). Published LLM baseline on
  BBEH: harmonic mean <10%. Substrate's algebraic rule execution should approach ceiling on
  purely-deterministic tasks. HARD-PASS: >0.85 on deterministic-rule tasks. HARD-FAIL: <0.55
  (implies substrate not encoding rules explicitly enough).
- Tier: local CPU (BBEH is public; deterministic-rule subset is small; fast inference)
- Why now: second cheapest decisive test; runs in parallel with COGS-OOD-DEPTH8; determines
  whether BIG-bench is a viable benchmark axis for the product narrative

### Anchor 3: HOTPOTQA-RETRIEVAL (substrate_hotpotqa_retrieval_gate)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section A2
- Substrate-product reading: Run substrate multi-hop retrieval on HotpotQA distractor setting.
  Published RAG SOTA: 59.72% EM, 74.10% F1 (2025). PP-226 private eval: +24.3pp over
  LazyGraphRAG. HotpotQA is the public replication target. HARD-PASS: >0.65 EM (retrieval
  only, no LLM generation). HARD-FAIL: <0.40 EM (multi-hop advantage narrower than PP-226).
  Important: substrate has no Wikipedia parametric memory; structural advantage is cleanly
  measured here without contamination confound.
- Tier: remote CPU (data loading 112K pairs; moderate memory for retrieval pass)
- Why now: converts private PP-226 claim to externally reproducible result; 4-8 hours

### Anchor 4: N-EDIT-AUDIT-BUILD (substrate_n_edit_audit_build)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section B6
- Substrate-product reading: Build N-Edit-Audit Benchmark. Generate graded fact dataset
  (N=100, 1K, 10K, 50K). For each N: insert all facts, make random subset of edits, then
  query current state + history + cert-verify. Measure: (a) current-state accuracy, (b)
  deleted-state inaccessibility, (c) cert-verify completeness. LLM baseline scores 0.000 on
  (b)+(c) by architectural impossibility (no addressable per-fact certificates in parametric
  weights). HARD-PASS: (b)+(c) both 1.000 at N=50K. HARD-FAIL: cert-verify <0.90 at N=1K.
  GDPR and EU AI Act Article 12 compliance framing applies.
- Tier: remote CPU (N=50K edit sequence; moderate but not GPU-required)
- Why now: establishes the strongest categorical claim (LLMs score 0 by construction, not by
  performance gap); direct compliance narrative for EU AI Act Article 12 (Aug 2026 deadline)

### Anchor 5: WRITE-LOCK-COMPARE (substrate_write_lock_llm_compare)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section B9
- Substrate-product reading: Extend PP-353 setup (substrate CORE 1.000, baseline 0.008) to
  include an explicit LLM RAG comparison baseline under adversarial PERIPHERY write load.
  Add: parametric LLM retrieval baseline that shares a unified embedding index with CORE and
  PERIPHERY. Measure CORE degradation under same adversarial load. HARD-PASS: substrate
  CORE 1.000, LLM baseline <0.05 (125x categorical gap replicated with external comparison).
  HARD-FAIL: substrate CORE <0.95 (regression from PP-353 result).
- Tier: local CPU (extends PP-353 existing setup; adds comparison baseline)
- Why now: PP-353 result already strong (1.000 vs 0.008); adding LLM comparison converts
  internal result to externally comparable benchmark; 1 day marginal cost

### Anchor 6: ANN-BENCHMARKS-THROUGHPUT (substrate_ann_benchmarks_integration)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section C10
- Substrate-product reading: Integrate substrate into ann-benchmarks.github.io protocol.
  Express internal 9532 q/s result in the published benchmark harness format. This converts
  the internal measurement to a third-party comparable result. HARD-PASS: >5000 q/s at
  recall >0.95 on 100K corpus in ann-benchmarks harness. HARD-FAIL: <1000 q/s (regression)
  or recall <0.90 (accuracy-speed tradeoff worse than expected).
- Tier: GPU (ann-benchmarks runs on GPU for fair comparison with FAISS GPU implementations)
- Why now: sub-ms throughput is the most tangible product claim; ann-benchmarks is the
  accepted standard harness; result directly addressable to competitors (FAISS, pgvectorscale)

### Anchor 7: MULTI-TENANT-ISOLATION (substrate_multi_tenant_isolation_bench)
- Anchor pointer: notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md, Section B7
- Substrate-product reading: Build multi-tenant isolation benchmark at M=10, M=100, M=1000
  tenants. Generate M independent fact spaces, cross-query, measure bleed rate per tenant.
  HARD-PASS: isolation 1.000 at M=100 (zero bleed). HARD-FAIL: isolation <0.99 at M=10.
  Algebraic isolation is exact by construction (per-tenant W); this benchmark verifies
  the construction works in practice.
- Tier: local CPU (algebraic binding operation; no GPU needed)
- Why now: direct GTM implication for enterprise multi-tenant deployments; 1 day build

---

## Context pointers (file paths, not summaries)

- notes/research_drill_substrate_specific_benchmarks_2x_2026-06-11.md -- full drill (THIS NOTE)
- notes/substrate_capability_map.md -- PP-343 (compositional depth), PP-226 (multi-hop),
  PP-228 (crypto audit), PP-352 (lifelong edit), PP-353 (write-lock), PP-344 (KEY-ROTATION)
- data/orchestrator_status_log.jsonl -- recent research_delivery entries for context
- notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md -- production-scale validation
  context (1M end-to-end, 9532 q/s, PP-353 1.000)

---

## Contract section

exp_dev owns ALL experiment design decisions including N, K, seeds, threshold bands, queue
routing, anchor naming, and ETA estimation. This hand-off is a CONTEXT TRANSFER, not an
instruction set.

## Autonomy declaration

exp_dev may: add benchmarks not listed here if they map cleanly to existing experimental
infrastructure and are decidable in <1 day; reorder anchors based on queue state; run
COGS-OOD-DEPTH8 and BBEH-ALGO-SUBSET in parallel (they are independent); defer ANN-BENCHMARKS
to next batch if GPU queue is full (local-CPU anchors take priority for speed of decision).

exp_dev may NOT: run HotpotQA before COGS-OOD-DEPTH8 (COGS is cheaper and determines
whether the compositional depth axis is viable -- it gates the NLP benchmark narrative);
skip the N-EDIT-AUDIT build (it is the strongest categorical claim and the compliance
narrative depends on it); substitute MMLU or HumanEval as comparison benchmarks (these are
LLM home-field benchmarks where substrate has no categorical advantage).
