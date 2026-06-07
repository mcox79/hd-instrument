# exp_dev hand-off -- research: Pattern B compositional storage feasibility (3x drill)

Filed-by: research sub-agent
Trigger: notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
Date: 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates
and context pointers only. exp_dev reads these and designs the experiment autonomously.

---

## Pause state block

Not currently paused. SRL pre-test anchors are CPU-only and cost-free. Proceed as normal
queue cadence.

---

## Anchor candidates (rank-ordered)

### Rank 1: SRL_pretest_domain_quality

Why now: This is the go/no-go gate for Option B (hybrid Pattern A + B). The research drill
identifies SRL domain accuracy as the single brittle dependency for Pattern B v1 feasibility.
Running this pre-test first (2-3 hours) converts a 4-5 week engineering bet into a
2-hour risk read. If it fails, Option A ships in 2-3 weeks. If it passes, Option B starts.

Anchor pointer: Pre-test 1 from research drill Section 9.
Substrate-product reading: SRL F1 >= 0.82 AND subject/object swap rate <= 5% is PASS;
  F1 < 0.78 OR swap rate > 8% is FAIL. 500 sentences, 50 manually labeled for ground truth.
Tier hint: CPU laptop, ~45 min human labeling + ~5 min AllenNLP or spaCy inference.
Hard-pass: argument F1 >= 0.85, swap rate <= 4%.
Hard-fail: argument F1 < 0.78, OR swap rate > 8%.

### Rank 2: pattern_b_counterfactual_schema_manual_smoke

Why now: Validates the bundle retrieval algebra at N=2048 for role-selective queries and
counterfactual substitution, using manually decomposed facts (bypasses SRL dependency).
This is the algebra-only test that isolates substrate capability from SRL quality.

Anchor pointer: Pre-tests 2 and 3 from research drill Section 9, combined into one run.
Substrate-product reading: 20 counterfactual substitutions + 20 schema-aware queries on
  50 manually decomposed facts; 4 bundles of ~12 items each (well under N=2048 capacity).
  Counterfactual PASS: >= 18/20 correct at cosine > 0.7.
  Schema-aware PASS: precision >= 0.85, recall >= 0.80.
Tier hint: CPU laptop, ~3-4 hours total (1 hour manual decomposition + 30 min scripting +
  run time negligible).
Hard-pass: counterfactual accuracy >= 0.92 AND schema precision >= 0.85.
Hard-fail: counterfactual accuracy < 0.80 OR schema precision < 0.75.

### Rank 3: pattern_b_bundle_capacity_sweep

Why now: The predicate_ratio_audit MID (cycle 155) showed retrieval degradation above 10%
occupancy. The research drill identifies that schema-aware queries can hit this threshold
at 25-45 item bundles. A capacity sweep maps the exact crossover point for this substrate.

Anchor pointer: Section 2.1 and Section 12.2 of research drill.
Substrate-product reading: sweep bundle size K from 5 to 64 at N=2048; measure cosine
  retrieval accuracy for role-selective queries as a function of K; find K_max where
  accuracy drops below 0.90.
Tier hint: CPU laptop, script-only, < 30 min run time.
Hard-pass: K_max >= 40 (confirms chunked bundle design is viable at N=2048).
Hard-fail: K_max < 25 (would require N=4096 for production-quality bundles).

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
Prior compositional drill: d:/AI/hd-instrument/notes/research_drill_substrate_llm_interface_compositional_structure_preservation_2x_2026-06-04.md
Cycle 153 causal validation context: see cap_map rows causal_counterfactual_replay,
  causal_intervention_isolation, causal_correlational_disambig (all HP).
Predicate ratio audit: cycle 155 MID result -- selectivity degradation above 10% occupancy.

---

## Contract section

The research drill establishes:
- Pattern B is algebraically sound and partially validated (cycle 153 causal results)
- SRL quality is the binding constraint for v1 feasibility
- Option B (hybrid) ships in 7-9 weeks if SRL pre-test passes; Option A in 2-3 weeks if not
- The north-star demo gains 5 new benchmark families (CaLM, CLadder, CompsRE, AnalogyQA,
  CLUTRR) with Pattern B; these are exactly the families where 1B LLMs score worst
- Counterfactual substitution accuracy is independent of SRL (algebra-only); already
  validated at 100% for causal subset

## Autonomy declaration

exp_dev designs the experiment scripts, chooses the SRL model, writes the manual annotation
schema, and sets up the bundle capacity sweep. No further research or orchestrator input
is needed before dispatching Rank 1 and Rank 2 anchors. Rank 3 (capacity sweep) can run
in parallel with Rank 1 as it is substrate-only with no SRL dependency.
