# exp_dev hand-off -- research: LLM + Structured-Knowledge Integration Survey (5x)

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: d:/AI/hd-instrument/notes/research_drill_llm_substrate_integration_survey_5x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names candidates and context pointers only. Exp_dev designs the experiment internally.

---

## Pause state block

Pause-gated: yes. Check data/orchestrator_paused.flag before dispatch.
If paused: do not queue experiments. File is auto-discovered on emergency-refill cycles.
If not paused: proceed with anchor candidates below in rank order.

---

## Anchor candidates (rank-ordered)

### Rank 1: C1-FACT NeSy compositional generalization fix
- Anchor pointer: C1-FACT (held-out fact recall = 0 from exp_dev POST_COMPACTION_BRIEF_2026-06-09)
- Substrate-product reading: Pattern 5 (linear projection head) memorizes in-distribution facts perfectly (recall 1.000) but fails on held-out compositional combinations. Literature (NeSy, Datalog-neg, LLM-as-semantic-parser) shows this is a known failure mode of linear extraction and has a published fix: route compositional queries to a symbolic engine rather than a projection head. Experiment: implement a router that detects multi-hop / compositional queries and redirects them to a Datalog-neg engine over the structured KB, bypassing the projection head.
- Tier hint: Tier 1 -- unblocks the product claim that substrate improves LLM fact recall beyond in-distribution facts.
- Why now: C1-FACT is the only remaining gap in the Tier-5c v2.0 arc (A1/B1/C1/D1 all HARD_PASS except C1-FACT held-out). Closing it is the path to completing the arc.

### Rank 2: Two-path retrieval router (structured + semantic paths)
- Anchor pointer: new anchor (no prior queue entry)
- Substrate-product reading: Literature confirms Pattern 1 (RAG text-prepend) + Pattern 5 (linear projection head) is the correct combination for any-LLM deployment with GDPR compliance. A two-path router should route structured-fact queries to the projection head path (<5ms) and open-domain queries to the dense ANN path (20-50ms). Experiment: build the router on top of existing substrate retrieval; measure accuracy, latency per path, and GDPR deletion simulation on 500-question QA set.
- Tier hint: Tier 2 -- establishes the production integration architecture.
- Why now: Both paths are empirically validated individually. The router is the missing integration layer.

### Rank 3: RouteLLM + semantic cache cost layer
- Anchor pointer: new anchor (no prior queue entry)
- Substrate-product reading: RouteLLM (ICLR 2025) achieves 85% cost reduction at 95% quality on MT Bench. Semantic cache adds another 60-86% reduction on repeated queries. Both are model-agnostic and require no changes to retrieval. Experiment: integrate RouteLLM router + semantic cache in front of the existing substrate + LLM serving path; measure cost reduction and quality retention on a mixed query benchmark.
- Tier hint: Tier 2 -- cost layer required for commercial viability.
- Why now: Retrieval substrate is mature enough for cost-layer experiments; RouteLLM is published and reproducible.

### Rank 4: GDPR exact deletion verification
- Anchor pointer: GDPR simulation (new anchor)
- Substrate-product reading: Gap 7.4 from research note. No published system provides verified proof that a deleted KB record no longer affects inference output. Experiment: delete N=50 facts from the KB; run retrieval + generation on those facts; verify zero recall; measure whether any embedding-space residue persists in ANN index after tombstone vs rebuild.
- Tier hint: Tier 2 -- compliance claim requires empirical validation, not just architectural argument.
- Why now: EU EDPB 2025 coordinated enforcement on right-to-erasure makes this a near-term commercial requirement.

### Rank 5: Per-token source attribution (Gap 7.3 probe)
- Anchor pointer: audit chain probe (new anchor)
- Substrate-product reading: Gap 7.3 from research note. Clinical RAG (PMC 2025) achieves per-query source attribution. Per-token attribution with cryptographic commitment (Merkle) is unpublished. Experiment: implement per-retrieved-record ID logging in the retrieval path; attach record IDs to generated tokens via attention-weight heuristic; verify that each token's provenance can be traced to a specific KB record. This is a lower-cost analog before full Merkle commitment.
- Tier hint: Tier 3 -- differentiating capability for regulated industries; not on critical path.
- Why now: Low engineering cost relative to differentiation value; builds on audit infrastructure already partially present.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_llm_substrate_integration_survey_5x_2026-06-09.md
- C1-FACT context: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Prior bitemporal/GDPR validation: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Production architecture: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- North star: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md

---

## Contract section

Exp_dev owns all experiment design decisions. This file provides ranked candidates and context pointers only. Exp_dev must:
1. Check pause flag before any dispatch.
2. Apply pre-dispatch speed+harden+progress discipline per [[feedback-pre_dispatch_speed_harden_progress_discipline]].
3. Apply small-scale-first methodology (rung-1-2 before cloud) per [[feedback-small_scale_first_methodology]].
4. Pre-register HARD-PASS and HARD-FAIL bands before each dispatch.
5. Route to remote GPU runner (not cloud) unless cloud justification criteria are met per [[feedback-cloud_only_when_absolutely_necessary]].

## Autonomy declaration

Exp_dev is autonomous on: anchor selection order, experiment design, HP choices, dispatch routing.
Exp_dev defers to orchestrator on: cap_map updates, strategy pivots, budget authorization above envelope.
Research agent does not own any experiment design in this file.
