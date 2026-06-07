# exp_dev hand-off -- research: End-to-End Demo Pipeline Architecture (2x)

## Filed-by
Research sub-agent, 2026-06-07

## Trigger
Research note: notes/research_drill_demo_pipeline_architecture_2x_2026-06-07.md
Topic: 2x operational drill on integrating all validated components into shippable v1 demo

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
CPU-only anchors (A1) are not pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- GPU smoke, <10 min, unblocks 2.5 engineer-weeks)
Pointer: "Cheap decisive test" section of research note
Substrate-product reading: Validates that bge-small retrieval + Llama L15 KEY extraction +
  Qwen2.5-1.5B generation can all run in the same Python process on desktop GPU with
  correct outputs and total latency <5s. This is the MANDATORY pre-test before any
  engineering investment.
Tier hint: GPU; single warm-GPU run; no sweep needed; HARD-PASS/HARD-FAIL binary
Why-now: Nothing else in the demo engineering timeline is defensible until this passes.
  Format compatibility between components (3 conversions: float32 tensor, PCA projection,
  prompt string) is untested. One failed conversion = 1 day of debugging. This catches
  it in 10 minutes.
Task: Load bge-small + Llama-1B + Qwen2.5-1.5B in one process. Encode 5 synthetic facts.
  Query each with a paraphrase. Measure: (a) bge-small retrieval accuracy (correct fact
  in top-1), (b) Llama L15 -> PCA -> substrate W query accuracy (correct fact), (c)
  Qwen generates a 1-sentence answer grounded in the retrieved fact. Report per-component
  latency and total wall time.
  HARD-PASS: all 5 queries return correct fact from both retrievers; Qwen answer mentions
    the correct entity; total wall <5s.
  HARD-FAIL: any retriever returns wrong fact; OR total wall >10s on warm GPU.

### Anchor 2 (CPU, <30 min -- RSA accumulator + Merkle proof round-trip)
Pointer: T6 (audit trail collection) from research note; prior work in research_drill_v1_demo_pipeline_optimization_2x_2026-06-05.md
Substrate-product reading: Validates the GDPR erasure cert round-trip (add -> delete ->
  verify certificate) AND that Merkle proofs are retrievable by fact_id. These two
  together enable S3 (GDPR erasure) demo scenario.
Tier hint: CPU; ~30 min build, <1 min run; no GPU
Why-now: The RSA accumulator was validated algebraically in the prior drill but never
  implemented as running code. This is the first integration step for the audit trail.
Task: Implement RSA accumulator (~250 LOC) + Merkle tree (~100 LOC). Build a 20-fact
  KB. Delete 3 facts. Verify all 3 deletion certs. Retrieve 10 Merkle proofs by fact_id.
  Report: cert verification pass/fail per deletion; proof retrieval latency.
  HARD-PASS: all 3 deletion certs verify correctly; all 10 Merkle lookups correct; cert
    latency <1ms each; proof lookup <5ms each.
  HARD-FAIL: any cert verification fails (mathematical error in accumulator code).

### Anchor 3 (CPU, <20 min -- NER decomposition pre-test on 2-hop questions)
Pointer: T2 (query parsing pipeline) from research note; PRE-TEST A from morning brief
Substrate-product reading: Determines whether SpaCy NER entity extraction is sufficient
  for 2-hop question decomposition. If recall@2hop >=0.65 with NER-based entity bridge,
  T2 is implemented with SpaCy (simple, fast). If <0.65, T2 must use LLM decomp (adds
  200-400ms per query).
Tier hint: CPU; SpaCy inference; no GPU; batch of 20-50 sample questions
Why-now: T2 architecture decision blocks T3 integration (retrieval coordination depends
  on whether query is decomposed). Should resolve before Week 1 Day 2.
Task: Load SpaCy en_core_web_sm. Run entity extraction on 20-50 multi-hop questions
  from a public dataset (HotpotQA subset or synthetic). For each question, check if
  extracted entities map to any fact in a 500-fact test KB. Report: fraction of 2-hop
  questions where entity bridge retrieves both target facts; compare to single-hop baseline.
  HARD-PASS: entity bridge retrieves both target facts in >=65% of 2-hop questions.
  HARD-FAIL: entity bridge retrieves both facts in <40% of 2-hop questions (fall back
    to LLM decomp path).

---

## Context pointers

- Research note (this drill): notes/research_drill_demo_pipeline_architecture_2x_2026-06-07.md
- Prior pipeline optimization drill: notes/research_drill_v1_demo_pipeline_optimization_2x_2026-06-05.md
- Production architecture brief: notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md
- Benchmark suite note: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
- Empirical dependencies from morning brief: Pattern B Phase 0 SRL pre-test (in queue),
  manifold sweep (in queue), NER PRE-TEST A (in queue per morning brief)

---

## Contract

Anchors are ordered by unblocking value. A1 (smoke test) should run first; if it
HARD-FAILs, diagnose before running A2 or A3. A2 and A3 are independent of each other
and can run in parallel if A1 passes.

## Autonomy declaration

Exp_dev designs all sweep parameters, threshold formulas, script implementations, and
queue routing. This file provides task framing and empirical context only.
