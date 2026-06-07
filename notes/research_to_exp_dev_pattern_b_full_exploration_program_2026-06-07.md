# Research -> Exp-Dev: Pattern B full exploration program

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** User directive: "full exploration of pattern b and we'll decide based on results"

## Program structure

Phase 0 (gate, $0, 3 hours): SRL pre-test (already routed separately).
Phase 1 (algebra validation, $0, 1-2 days CPU): 5 cells testing substrate capability.
Phase 2 (integration validation, $0-50, 1-3 days): 3 cells testing end-to-end behavior.
Phase 3 (user decision review): all results synthesized for A vs B decision.

Run Phase 0 first. If it HARD-FAILs, Pattern B is infeasible at v1 timeline and the
exploration stops; ship Option A. If Phase 0 HARD-PASSES or BORDERS, run Phase 1 cells
in parallel; Phase 2 starts once Phase 1's algebra is validated.

Each cell reports HARD-PASS / BORDER / HARD-FAIL via verdict_handler with multi-dim
acceptance criteria (retrieval F1, K-hop accuracy, KF-1 AUC, audit, perf in addition
to the cell-specific metric).

## Phase 1: algebra validation (5 cells, run in parallel after Phase 0)

### 1A: counterfactual substitution at scale

Test that substrate can substitute one filler in a stored fact and retrieve the
substituted version correctly without contaminating unrelated facts.

Method:
- Store 100, 500, 2000 facts in Pattern B form (manually decomposed; bypasses SRL)
- For each scale: substitute one filler in 20 randomly-chosen facts (e.g., replace
  "Marie Curie" with "Pierre Curie" in subject role); verify substrate retrieves the
  substituted form correctly
- Measure top-1 substitution recall AND contamination of unrelated facts (do other
  facts get spuriously altered)

HARD-PASS: substitution recall >= 95% AND contamination <= 1% AT 2000 facts.
BORDER: substitution recall 85-95% OR contamination 1-5%.
HARD-FAIL: substitution recall < 85% OR contamination > 5%.

Wall: 4-6 hours CPU.

### 1B: schema-aware compositional retrieval

Test that substrate can answer "find all facts where subject = X" type queries
algebraically (not by scanning).

Method:
- Store 500-1000 facts in Pattern B
- Issue 20 schema-aware queries at varying selectivity: rare subjects (1-5% of facts),
  common subjects (10-30% of facts), very common subjects (40%+ of facts)
- Measure recall@1, recall@10 per selectivity bucket

HARD-PASS: recall@10 >= 90% for selectivity 1-10%, recall@10 >= 70% for selectivity
20-40%, recall@10 >= 50% for selectivity 40%+.
BORDER: recall@10 in the 60-90% / 50-70% / 30-50% bands respectively.
HARD-FAIL: recall@10 below the border bottoms.

The predicate_ratio_audit MID from cycle 155 (92% at 5% selectivity, degrades < 80%
at 10%+) is the relevant prior. This cell verifies whether Pattern B compositional
retrieval matches or exceeds the predicate routing baseline.

Wall: 3-5 hours CPU.

### 1C: cross-domain analogy retrieval

Test that substrate can identify structurally analogous facts with different fillers.

Method:
- Store 200 facts with shared role structure but varied fillers
- For 20 query facts (different fillers, same structure), measure whether substrate
  retrieves the structurally-analogous-but-different-filler facts
- Example: query "X discovered Y" should return all "person discovered substance" facts

HARD-PASS: analogical retrieval recall >= 70% on the 20 queries.
BORDER: 50-70%.
HARD-FAIL: < 50%.

Wall: 2-3 hours CPU.

### 1D: bundle capacity vs K (items per bundle)

Identify the production K limit for Pattern B bundles.

Method:
- Vary K (items per bundle) from 5 to 50 in 5 steps
- For each K, measure end-to-end retrieval quality on a fixed query set
- Identify the knee point where quality starts degrading

HARD-PASS: identifies a K >= 20 with quality > 95% of K=10 baseline.
Document the production K limit; this informs the v1 storage projection.

Wall: 2-3 hours CPU.

### 1E: multi-step causal chain extension

Test that the cycle 153 single-step causal capability extends to multi-step chains.

Method:
- Construct 30 multi-step causal chains: "A caused B", "B caused C", "C caused D"
- Query "what did A ultimately cause" or "what caused D"
- Measure chain retrieval quality at K=2, K=3, K=4 steps

HARD-PASS: chain retrieval quality >= 80% at K=3, >= 65% at K=4.
BORDER: 60-80% at K=3, 45-65% at K=4.
HARD-FAIL: < 60% at K=3 or < 45% at K=4.

Wall: 2-3 hours CPU.

## Phase 2: integration validation (3 cells, sequential after Phase 1)

### 2A: end-to-end Pattern B benchmark head-to-head

Pick one benchmark from {CaLM, CLadder, CompsRE, AnalogyQA, CLUTRR} and run
substrate Pattern B + Llama-1B vs bare Llama-1B head-to-head.

Recommended: CaLM (counterfactual reasoning; small enough to run cheaply; aligned with
cycle 153 causal cluster strength).

Method:
- Run a 100-question pilot
- For substrate Pattern B + Llama-1B: query goes to SRL, decomposes into roles+fillers,
  substrate retrieves, Llama-1B generates answer conditioned on retrieval
- For bare Llama-1B: same query, no substrate

HARD-PASS: substrate beats bare Llama-1B by >= 15 percentage points absolute on the
benchmark metric.
BORDER: 5-15 pp absolute lift.
HARD-FAIL: < 5 pp lift OR substrate worse than bare.

Wall: 1 day CPU.

### 2B: hybrid routing test

Test that a mixed factual + structured query workload still works with hybrid Pattern A
+ Pattern B in production-realistic conditions.

Method:
- Mixed query workload: 50% factual recall (route to Pattern A), 30% schema-aware
  queries (route to Pattern B), 20% counterfactual queries (route to Pattern B)
- Measure end-to-end latency and quality on each query type
- Verify no regression on Pattern A factual queries

HARD-PASS: Pattern A factual quality unchanged from baseline; Pattern B query latency
overhead < 100 ms; no contamination between Pattern A and Pattern B storage.
BORDER: latency overhead 100-300 ms OR small (< 5%) regression on Pattern A factual
queries.
HARD-FAIL: latency overhead > 300 ms OR > 10% regression on factual queries.

Wall: 4-6 hours CPU.

### 2C: storage cost validation

Verify the projected ~100 MB overhead for 100K facts holds in practice.

Method:
- Store 10K facts in Pattern B
- Measure actual storage: concept vector cache size, role vocabulary, bundle storage
- Project to 100K facts and compare to Pattern A at 4-bit quantization

HARD-PASS: projected 100K storage within 50% of the 100 MB drill prediction.
BORDER: 1.5-3x drill prediction.
HARD-FAIL: > 3x drill prediction (storage projections were wrong).

Wall: 2-3 hours CPU.

## Phase 3: decision review

After Phases 1+2 complete, synthesize all results into a one-page decision document for
user review. The document should include:

- Phase 0 SRL result with F1 and swap rate numbers
- Phase 1 cells 1A-1E pass/fail with the specific numbers
- Phase 2 cells 2A-2C pass/fail with the specific numbers
- Updated P_actionable for Option B (currently 0.37)
- Recommendation: Option A (pure Pattern A) vs Option B (hybrid) vs Option D (scope-reduced
  Pattern B for specific capabilities only)

Decision rules for the synthesized recommendation:
- All Phase 1 + Phase 2 cells HARD-PASS: Option B strong recommendation (P_actionable
  > 0.65).
- Phase 1 mostly HARD-PASS, Phase 2 borderline: Option B with reduced scope or Option D
  (deploy Pattern B for the specific capabilities that worked).
- Phase 1 mostly BORDER: Option D (scope-reduced Pattern B for the capability classes
  that passed cleanly).
- Phase 1 mostly HARD-FAIL: Option A (Pattern B infeasible at v1; v2 research target).

## Methodology discipline reminders

All cells apply multi-dim acceptance criteria (per supplement note already on file).
A cell that passes its primary metric but degrades audit, ZKL, or K-hop is not a clean
win.

All cells use the two-encoder architecture (per this morning's correction):
- Substrate KEY (W matrix): Llama-3.2-1B L15 left-pad
- Filler embeddings (semantic similarity for filler reuse): MiniLM
- Role vectors: substrate-generated bipolar (fixed vocabulary)

Plain-language reporting in the final synthesis: lead with capability gain in real-world
terms, not internal anchor names. The decision document is for user review.

## Cross-references

- Pattern B 3x drill: notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
- Pattern B handoff: notes/exp_dev_handoff_research_pattern_b_compositional_storage_3x_2026-06-07.md
- SRL pre-test routing: notes/research_to_exp_dev_pattern_b_srl_pretest_authorize_2026-06-07.md
- Two-encoder correction: notes/research_to_exp_dev_URGENT_two_encoder_architecture_2026-06-07.md
- Cycle 153 causal cluster (partial Pattern B validation): notes/orchestrator_to_research_results_summary_2026-06-07_cycle153.md
- Multi-dim criteria: notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md
- Benchmark suite (Pattern B-relevant families): notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize the full Pattern B exploration program. Sequence Phase 0 first;
fork Phase 1 cells in parallel once Phase 0 passes; sequence Phase 2 after Phase 1; file
final synthesis after Phase 2. Apply decision rules autonomously through cell verdicts;
file the final synthesis document for user review when Phase 2 completes.
