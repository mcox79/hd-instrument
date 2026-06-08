# exp_dev hand-off -- research: hippocampal reverse replay DEEPER 3x (counterfactual planning engine)

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

The DEEPER 3x drill on hippocampal reverse replay (from the prior 5x natural analog series)
establishes three new engineering-ready mechanisms. The single most yielding sub-avenue is
theta-gamma multi-mode operation: the same substrate retrieval hardware supports three
distinct computational modes (retrieval / imagination / synthesis) controlled by a noise
parameter and input isolation. The zero-cost mode is already available (variable-threshold
retrieval as a dorsal-ventral analog). The noise-injection imagination mode requires a
one-line code change. The domain-crossover synthesis mode is a 3-5 day addition.

All tests below are CPU-only. None require cloud. Cheapest test (Test C) is 2-3 hours with
ZERO engineering changes -- just run existing substrate at different cosine thresholds.

---

## Anchor Candidates (rank-ordered by P_deflated x engineering cost ratio)

### 1. Test C -- Variable-threshold retrieval modes (HIGHEST PRIORITY; zero engineering)

Anchor pointer: HIPPOREPLAY-C1 (new; not yet queued)
Substrate-product reading: Run existing substrate at cosine thresholds 0.65, 0.75, 0.85
  on the same 50 queries. Measure precision@1, recall@5, and mean result set size. If
  threshold=0.85 achieves >= 95% precision@1 AND threshold=0.65 achieves >= 2x result
  set coverage, this becomes a zero-cost "precision vs exploratory mode" product feature
  grounded in dorsal-ventral hippocampal biology.
Tier hint: CPU laptop; 2-3 hours wall; no new code needed; runs on any existing benchmark
  query set (HotpotQA distractor or synthetic KB both work)
Why-now: Zero engineering, zero cost, immediately actionable. If HARD-PASS, ships in v1
  as a one-parameter customer-facing feature. No downside risk.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: threshold=0.85 precision@1 >= 0.95 AND threshold=0.65 result set size >= 2x
             threshold=0.85 result set size (exploratory mode genuinely expands coverage)
  HARD-FAIL: threshold degradation is monotonically noisy (lower threshold adds only
             spurious results without expanding useful coverage)
  MID-BAND: coverage expansion 1.3x-2x with some precision loss (requires per-query tuning
            rather than a universal setting)

---

### 2. Test A -- Noise injection for imagination mode (SECOND PRIORITY; one-line code change)

Anchor pointer: HIPPOREPLAY-A1 (new; not yet queued)
Substrate-product reading: Add epsilon_noise parameter to query path:
  q_noisy = q + epsilon * torch.randn_like(q); q_noisy /= q_noisy.norm()
  Run 20 imagination sessions with epsilon in {0, 0.05, 0.10, 0.20} on a 500-fact
  synthetic KB (two domains). Measure entity diversity (unique entities per session) and
  recall@1 degradation from epsilon=0.0 baseline.
  If HARD-PASS: imagination mode is a product-ready "exploratory retrieval" capability
  with neuroscience grounding (theta-gamma autonomous replay mode).
Tier hint: CPU laptop; 1-2 days including implementation; one-line change to query function
Why-now: Cheapest new capability with direct biological grounding. If HARD-PASS unlocks
  "imagination mode" customer feature. Complements Wish 1 counterfactual (HP cycle 175)
  with a prospective exploration analog.

Pre-reg bands:
  HARD-PASS: epsilon=0.10 entity diversity per session >= 3x epsilon=0.0 baseline AND
             recall@1 degradation at epsilon=0.10 <= 15%
  HARD-FAIL: epsilon=0.10 diversity < 1.5x baseline (noise does not enable exploratory mode)
             OR recall@1 degrades > 30% at epsilon=0.05 (noise too disruptive to be useful)
  MID-BAND: diversity 1.5x-3x with recall degradation 15-30%

---

### 3. Test D -- Schema-weighted Misra-Gries consolidation (THIRD PRIORITY)

Anchor pointer: HIPPOREPLAY-D1 (new; not yet queued)
Substrate-product reading: Add bridge-count-weighted counter update to Misra-Gries defrag.
  weight_i = base_weight * (1 + alpha * bridge_count_i / max_bridge_count)
  Write 1000 facts: half schema-consistent (connected to bridge-dense regions), half
  schema-inconsistent (< 3 bridge connections post-ingestion). Run defrag with and without
  schema-weight. Measure overnight bridge accumulation rate for each group.
  If HARD-PASS: "core knowledge consolidates faster" product claim enabled; directly
  complements the TMR priority gating HP from cycle 175.
Tier hint: CPU laptop; 1-2 days; 1-parameter extension to existing Misra-Gries
Why-now: Directly extends the TMR priority gating mechanism already validated (cycle 175,
  5.4x HP). Schema-weight is the automatic (data-driven) version of TMR's manual priority
  signal. Together they give a three-layer consolidation priority stack.

Pre-reg bands:
  HARD-PASS: schema-consistent entity consolidation >= 1.6x faster than schema-inconsistent
             under weighted Misra-Gries
  HARD-FAIL: < 1.1x consolidation rate difference (bridge count is not a schema proxy)
  MID-BAND: 1.1x-1.6x difference (effect exists but may require alpha tuning)

---

### 4. Test B -- Domain-crossover synthesis mode (FOURTH PRIORITY; 3-5 days)

Anchor pointer: HIPPOREPLAY-B1 (new; not yet queued)
Substrate-product reading: Accept two query vectors from different domains, form synthesis
  query q_synth = (q1 + q2) / ||(q1 + q2)||, run retrieval, evaluate output for semantic
  coherence. 10 held-out entity pairs across 5 domains, blind rater evaluation.
  If HARD-PASS: "analogical reasoning across knowledge domains" capability enabled.
  This is the substrate's "dreaming mode" -- finds bridges between disparate stored
  knowledge, with full audit trail. No LLM or RAG analog.
Tier hint: CPU laptop; 3-5 days; requires 1000-fact multi-domain KB and human evaluation
Why-now: Opens a new product capability class. Must wait for Test A HARD-PASS first
  (imagination mode must work before synthesis mode is worth pursuing). Sequence:
  Test C first (zero cost), then Test A, then Test B.

Pre-reg bands:
  HARD-PASS: >= 7/10 synthesis outputs rated "semantically coherent bridge" by blind rater
  HARD-FAIL: <= 3/10 rated coherent (synthesis is arbitrary at this KB size / N)
  MID-BAND: 4-6/10 coherent (some domain pairs work; needs domain-specific tuning)

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md
- Prior 5x hippocampal drill: d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
- Evening brief (empirical state): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Wish 1 counterfactual HP (cycle 175): see evening brief, Counterfactual do() row
- TMR HP (cycle 175, 5.4x): see evening brief, Natural analog empirical validation section
- cap_map (for placement): d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract section

Research has identified four pre-registered tests ordered by cost and prerequisite:
1. Test C (zero engineering, 2-3h) -> must pass before engineering resources committed
2. Test A (one-line change, 1-2d) -> runs after Test C confirms threshold response
3. Test D (1-param Misra-Gries, 1-2d) -> independent of A/C; can run in parallel
4. Test B (3-5d, human eval) -> requires Test A HARD-PASS as prerequisite

Multi-hop SR bank (Section 3.2 of research note): do NOT engineer until encoder ceiling
pre-test passes (per cycle 175 finding: encoder is the gating constraint, not K-hop
architecture). Flag this back to Research if encoder upgrade anchors are in queue.

REMI per-entity alpha decay (Section 3.3): medium-term; requires per-entity state
overhead. Not in current sprint scope.

---

## Autonomy declaration

exp_dev decides:
- Exact sweep grid for epsilon values in Test A
- Whether to combine Tests C and A in a single run (they are independent)
- Queue assignment (all CPU; local or remote_cpu_queue)
- Whether to use HotpotQA distractor or synthetic KB for Test C
- Exact human evaluation rubric for Test B (if Test A passes)
- Whether to pre-register delta_threshold as a confound in Test C

Research recommendation for ordering: C -> (A + D in parallel) -> B only if A HARD-PASS.
