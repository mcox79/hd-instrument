# exp_dev hand-off -- research: sleep defrag implicit generalization

Filed-by: research sub-agent (2026-06-07)
Trigger: 3x deep drill on sleep defrag / background consolidation for closing
  the implicit-generalization gap with frontier LLMs
Research note: d:/AI/hd-instrument/notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md

## Pause state block

This file is auto-discoverable on exp_dev emergency-refill cycles.
Experiments proposed here are NEW anchors, not re-runs of existing ones.
All cells are CPU-feasible (no cloud needed). Pre-test is 1-2 hours.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev has full autonomy
over anchor names, sweep parameters, numerical thresholds, queue choice,
and pre-reg bands. This file provides TASK + WHY + CONTRACT only.

Per [[feedback-drill-pretest-required]]: the Rank 1 pre-test MUST be run on
the production encoder (Llama-1B BASE, left-pad, PCA, N=65k, bf16) before
engineering authorization for the full sleep defrag implementation.

---

## Anchor Candidates (rank-ordered)

### Rank 1 -- Sleep defrag pre-test: co-occurrence aggregation on synthetic KB
Why now: Cheapest possible validation (1-2 hours CPU, ~50 lines Python).
  Validates that a derived regularity bound vector is retrievable from a
  substrate query at production dimensionality (N=65k).
  Gates ALL further sleep defrag engineering -- do not authorize v1.1 without this.
Substrate-product reading: if cosine similarity >= 0.65 for top-1 retrieval of
  derived regularity vector, the algebraic mechanism is sound and 2-3 week
  engineering investment is warranted. If it fails, the encoding approach
  (conf_bucket discretization) needs redesign before committing resources.
Tier hint: CPU smoke only; generate 100 synthetic fever-case Pattern B facts,
  run Python dict co-occurrence counter, encode top regularity as bipolar bound
  vector at production N, query "fever + cause?" probe, measure cosine sim.
HARD-PASS: cosine sim >= 0.65, correct filler ranked #1
HARD-FAIL: cosine sim < 0.45 or correct filler not in top-3

### Rank 2 -- Streaming co-occurrence sketch integration on live fact writes
Why now: The batch "sleep window" is a legacy framing. The correct architecture
  is incremental: Count-Min Sketch updated on every fact write, threshold-triggered
  regularity emission. This is the production-viable design.
  Validates that streaming update does not add measurable latency to the fact
  write path.
Substrate-product reading: if write latency overhead < 5ms P99, the streaming
  approach is viable for production. This determines whether sleep defrag can be
  "always on" vs. requiring scheduled batch windows.
Tier hint: CPU; instrument the fact write path with a mock CMS; measure P99 latency
  for N_facts in {1k, 10k, 100k}; target < 5ms overhead.
HARD-PASS: P99 overhead < 5ms at N=100k facts
HARD-FAIL: P99 overhead > 20ms at N=10k facts

### Rank 3 -- Derived-fact retrieval parallel shard merge latency
Why now: Every retrieval must now query TWO shards (primary + derived-fact).
  The latency regression must be measured before any product commitment.
  This is the production deployment gate for sleep defrag.
Substrate-product reading: if parallel shard query adds < 2x baseline latency,
  the architecture is viable. If it adds > 3x, the merge strategy needs redesign
  (e.g., derived-fact shard queried only for "statistical regularity" query types,
  not all queries).
Tier hint: CPU; mock a derived-fact shard with 1k pre-computed regularity vectors;
  measure parallel query latency vs. single-shard baseline at N_facts in {10k, 100k}.
HARD-PASS: parallel merge adds < 2x baseline latency at N=100k
HARD-FAIL: parallel merge adds > 3x baseline latency at N=10k

### Rank 4 -- GDPR cascade provenance index correctness test
Why now: Erasure correctness is a hard requirement for regulated customer deployments.
  The provenance index (fact_id -> regularity_ids) must be validated before any
  regulated-industry demo.
Substrate-product reading: validates that erasure of a source fact correctly
  triggers regularity recomputation or invalidation. A broken GDPR cascade is
  a hard blocker for medical / legal / financial customers.
Tier hint: CPU; build a toy provenance index for 100 derived regularities, each
  citing 5-10 source facts; trigger erasure of 10 random source facts; verify
  all dependent regularities are recomputed or invalidated within 5 seconds.
HARD-PASS: all dependent regularities correctly recomputed within 5s per erasure
HARD-FAIL: any dependent regularity NOT recomputed after erasure, OR recomputation
  takes > 30 seconds per erasure event

### Rank 5 -- Adversarial sleep defrag: inconsistency detection pass
Why now: Section 8b of the drill note identified a previously undiscovered connection:
  inconsistency detection in the derived-fact layer is a prerequisite for generating
  sound ZKP proofs over the KB. If a KB contains contradictions, ZKP proofs over it
  are unsound. This is a low-cost add-on to the sleep defrag pass.
Substrate-product reading: adversarial mode adds a "contradiction candidate" layer
  to the regularity store. For regulated industries, this is a compliance multiplier.
  Direct intersection with the ZKP audit thread.
Tier hint: CPU; extend co-occurrence aggregator to detect same-anchor conflicting
  fillers (high cosine similarity anchors, near-zero binding similarity for filler);
  measure false-positive rate on clean KB vs. KB with injected contradictions.
HARD-PASS: F1 >= 0.85 on injected-contradiction detection in a 1000-fact KB
HARD-FAIL: F1 < 0.50 OR false positive rate > 0.20 on clean KB

---

## Context pointers

Research note (full mechanism design + frequency analysis + audit design):
  d:/AI/hd-instrument/notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md

Prior related experiment (Cycle 154 online concept extension via sparse-KEY):
  data/exp_*/metrics.json (search for anchor containing "concept_extension" or "vocab_injection")

Pattern B production stack reference (Cycle 162):
  notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md

CLS theory anchor (fast episodic + slow statistical extraction):
  PMC9758580 (confirmed URL in research note citations)

---

## Contract

Exp-dev owns: anchor naming, sweep ranges, pre-reg HP/MID/HF bands, queue routing
  (CPU for all Rank 1-5 candidates), smoke-vs-full sequencing.

Research lane constraint: Rank 1 pre-test at production N (N=65k, Llama-1B BASE,
  left-pad, PCA, bf16) is MANDATORY before authorizing Rank 2-5 engineering.
  Per [[feedback-drill-pretest-required]]: a toy-N pre-test that passes does NOT
  authorize production implementation; it only gates the production pre-test.

Do NOT start GDPR cascade engineering (Rank 4) before Rank 1-3 pass. Provenance
  infrastructure is only valuable if the mechanism works at production scale.

## Autonomy declaration

Exp-dev has full autonomy over implementation details, anchor names, numerical
thresholds (within the HARD-PASS / HARD-FAIL ranges above), and queue assignment.
No inline experiment code is specified here per [[feedback-no-experiment-design-in-prompts]].
