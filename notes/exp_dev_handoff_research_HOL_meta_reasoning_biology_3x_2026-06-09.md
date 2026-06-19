# exp_dev hand-off -- research: HOL meta-reasoning biology 3x drill

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: notes/research_drill_HOL_meta_reasoning_biology_3x_2026-06-09.md
Urgency: HIGH -- 8 concrete engineering anchors for extending substrate ToM depth from 2 to 4 and adding cultural-convention caching; directly enables NORTH STAR benchmark head-to-head claim on social reasoning latency

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: tom_depth_k_cross_tenant_v1 (TOM-DEPTH-K)

Anchor pointer: Research note Section 6.2 + Section 7, Anchor 1; Stiller-Dunbar 2005; Fagin et al. 1995 k-depth common knowledge.
Substrate-product reading: Extends confirmed depth-2 multi-tenant ToM (drill 8) to depth 4 via iterative cross-tenant join chain. Tests correct resolution of a false-belief variant requiring 3-4 nested belief levels. If latency at depth 4 is under 4x depth-1, substrate handles >98% of real-world social ToM workload without LLM.
Tier hint: CPU-local laptop run. No GPU needed. Iterative join extension to existing multi-tenant infra. Run first -- gates all downstream anchors.
Why-now: Depth 2 is confirmed and working. Biological literature establishes depth 4 as the practical ceiling for human ToM (Stiller-Dunbar 2005). Reaching depth 4 closes the gap between substrate capability and human-level social reasoning coverage.

Pre-reg bands:
  HARD-PASS: Depth-4 cross-tenant query correct on false-belief task AND latency < 4x depth-1
  MIDDLE-BAND: Correct but latency 4-10x depth-1 (triggers cultural-convention caching anchor)
  HARD-FAIL: Incorrect at depth 3 OR latency > 10x depth-1 (architecture revision required)

### Anchor 2: cultural_convention_schema_cache_v1 (CULTURAL-CONVENTIONS)

Anchor pointer: Research note Section 6.3-6.4 + Section 7, Anchor 2; Clark 1996; Schank-Abelson 1977 scripts.
Substrate-product reading: Populates a shared cultural-commons tenant with 20-50 standard social schemas (cooperative exchange, adversarial negotiation, authority hierarchy, peer collaboration, request-grant-refusal). Measures LLM invocation rate on a social-reasoning benchmark before and after schema loading. Target: >50% reduction in LLM calls for the schema-covered cases.
Tier hint: CPU-local laptop run. Schema design is offline work; schema retrieval is standard substrate query. Can run in parallel with Anchor 1.
Why-now: Biological System 1 handles >95% of everyday ToM via cached schemas (Kahneman 2011; Stanovich 1999). Without schema caching, substrate invokes LLM on all ToM queries by default. This is the highest-leverage latency reduction available without changing retrieval math.

Pre-reg bands:
  HARD-PASS: LLM invocation rate < 50% of baseline on 20-query social-reasoning test set while accuracy > 90% of full-LLM baseline
  MIDDLE-BAND: 50-80% of baseline invocation rate OR accuracy 80-90%
  HARD-FAIL: Invocation rate reduction < 20% OR accuracy drop > 15% relative

### Anchor 3: dual_process_routing_v1 (DUAL-PROCESS)

Anchor pointer: Research note Section 6.6 + Section 7, Anchor 3; Kahneman 2011; Nelson-Narens 1990 monitoring function.
Substrate-product reading: Adds a confidence-score-based routing layer: substrate returns result + confidence score; LLM invoked only if confidence < threshold. Threshold calibrated on held-out social-reasoning queries. Implements the biological System 1 / System 2 separation architecturally.
Tier hint: CPU-local. Requires confidence score on cross-tenant queries -- if cosine similarity already produced, routing logic is trivial. Builds on Anchor 2 (schema caching produces higher confidence scores for covered cases).
Why-now: Without explicit routing, even after schema caching, LLM is still the default path. Dual-process routing makes substrate the default path. This is the architectural expression of all compression mechanisms in the research note.

Pre-reg bands:
  HARD-PASS: LLM invocation rate < 20% on mixed benchmark while accuracy > 90% of full-LLM baseline
  MIDDLE-BAND: 20-40% invocation rate with > 85% accuracy
  HARD-FAIL: Accuracy drop > 15% relative when substrate handles System-1 cases

### Anchor 4: meta_substrate_self_index_v1 (META-SUBSTRATE)

Anchor pointer: Research note Section 6.7 + Section 7, Anchor 4; Nelson-Narens 1990.
Substrate-product reading: Second-level substrate instance over the first level's fact list, enabling "does substrate know X?" self-queries before LLM escalation. Measures accuracy of coverage predictions against oracle LLM answer quality.
Tier hint: CPU-local. Small N (fact count). Deferred until Anchors 1-3 are validated.
Why-now: Required for autonomous substrate-vs-LLM routing without human-tuned thresholds. Lower priority than Anchors 1-3; file here for pipeline visibility.

Pre-reg bands:
  HARD-PASS: Coverage assessment accuracy > 80% vs oracle
  HARD-FAIL: < 60% accuracy (no better than random routing)

### Anchor 5: tom_benchmark_suite_head_to_head_v1 (NORTH STAR benchmark)

Anchor pointer: Research note substrate-product implications, item 4; NORTH STAR note.
Substrate-product reading: Head-to-head benchmark: substrate + LLM system vs standalone LLM on ToM task suite (false-belief, director task, strange stories). Primary metric: latency for depth 1-2 cases (substrate should win by large margin); secondary metric: accuracy at depth 3-4 (should match or exceed LLM alone with schema caching). This is the v1 demo benchmark artifact.
Tier hint: CPU-local benchmark construction + evaluation. Deferred until Anchors 1-3 validated. Requires Anchors 1 and 2 as prerequisites.
Why-now: NORTH STAR requires empirical head-to-head. This anchor is the measurement instrument. File here so it is not forgotten when Anchors 1-3 complete.

Pre-reg bands:
  HARD-PASS: Substrate+LLM matches LLM-alone accuracy on depth 3-4 cases AND delivers >5x latency speedup on depth 1-2 cases
  HARD-FAIL: Accuracy gap > 10% relative at any depth (substrate+LLM weaker than LLM alone)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_HOL_meta_reasoning_biology_3x_2026-06-09.md
- Drill 8 multi-tenant basis: d:/AI/hd-instrument/notes/ (search "drill_8" or "multi-tenant ToM")
- NORTH STAR note: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- C1-FACT brief (fact-recall context): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Post-compaction brief (full system state): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md

---

## Contract

exp_dev owns:
- Anchor prioritization within this file (may reorder based on queue depth + runner availability)
- Experiment design details: cell grids, hyperparameter values, script structure
- Pre-reg envelope refinement from the bands above
- Go/no-go decision per pause gate

Research sub-agent provided:
- Ranked anchor candidates with substrate-product readings
- Pre-reg band proposals (NOT final -- exp_dev calibrates from cap_map context)
- Context pointers (file paths, not summaries)

---

## Autonomy declaration

exp_dev may dispatch Anchor 1 immediately if (a) pause gate is clear and (b) runner has CPU capacity.
Anchors 2-3 may be dispatched in parallel with or immediately after Anchor 1.
Anchors 4-5 should wait for Anchors 1-3 verdicts.
No authorization needed for CPU-local anchors under the standing experiment authorization.
