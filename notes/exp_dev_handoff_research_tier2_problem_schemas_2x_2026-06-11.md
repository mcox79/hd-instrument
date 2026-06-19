# exp_dev hand-off -- research: Tier-2 problem schemas 2x design

Filed-by: research sub-agent (Sonnet, 2x operational drill)
Date: 2026-06-11
Trigger: notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md
Urgency: HIGH -- frame-role binding is Priority-1 NL primitive; schema layer is
  the concrete design step between validated binding mechanics and 15 downstream tasks

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are
to be authored by exp_dev from the research note + cap_map context. Do NOT treat
the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: tier2_schema_retrieval_smoke_v1 (cheapest decisive test)

Anchor pointer: Research note Section 10 (Cheap Decisive Test) + Section 11 Prediction 1
Substrate-product reading: Implements the RT-1 (Rate-Time-Distance) schema as a Tier-2
bundle with 3 role atoms (RATE, TIME, DISTANCE). Tests whether substrate cleanup correctly
retrieves the schema from a 2-slot partial query across 20 test instances. This is the
single gate between "substrate has binding mechanics" and "substrate has a schema layer."
If this fails, the entire Tier-2 schema inventory is not deployable without architectural
changes.

Tier hint: CPU laptop, ~2 hours total. CHEAPEST. Must run first -- gates all other anchors.

Pre-reg bands:
  HARD_PASS: schema retrieval accuracy >= 90% (18/20 correct) with correct empty-slot
    identification AND convergence within 10 cleanup iterations
  MIDDLE_BAND: accuracy 70-89% (14-17/20) OR convergence 11-20 iterations
  HARD_FAIL: accuracy < 70% (< 14/20) OR cleanup oscillation without convergence

Why-now: This is a 2-hour CPU experiment gating the entire Tier-2 schema design.
It directly tests the core mechanism (Tier-2 schema bundle + partial retrieval) before
any engineering investment in the full 114-schema codebook.

---

### Anchor 2: tier2_schema_disambiguation_v1 (2-schema competitive cleanup)

Anchor pointer: Research note Section 10 (Extension) + Section 11 Prediction 3
Substrate-product reading: Adds RT-4 (Average Speed) schema alongside RT-1 in codebook.
20 additional test instances designed to route to RT-1 (10 instances) or RT-4 (10 instances)
based on trigger words ("average speed" vs "travels at X mph for Y hours"). Measures whether
competitive cleanup correctly disambiguates. This is the empirical test of multi-schema
overlay (Section 7).

Tier hint: CPU laptop, ~2 hours (can run in same session as Anchor 1 if Anchor 1 passes).
Gate: run only after Anchor 1 HARD_PASS.

Pre-reg bands:
  HARD_PASS: correct schema selection >= 80% (16/20) on disambiguation test
  MIDDLE_BAND: 60-79% correct (12-15/20)
  HARD_FAIL: < 60% correct (< 12/20; no better than random guess between 2 schemas)

---

### Anchor 3: tier2_domain_codebook_routing_v1 (domain context-binding)

Anchor pointer: Research note Section 5.3 + Section 11 Prediction 2
Substrate-product reading: Builds a small cross-domain codebook with 5 math schemas +
5 code schemas + 5 CS schemas (15 total). Tests whether a DOMAIN_SELECTOR context-binding
token correctly routes queries to the right domain codebook before schema retrieval.
50 test queries drawn equally from all three domains.

Tier hint: CPU laptop, ~3-4 hours (larger codebook; 50 test queries).
Gate: run after Anchor 1 and Anchor 2 both PASS.

Pre-reg bands:
  HARD_PASS: Domain routing accuracy >= 90% (45/50) with context-binding token present
  MIDDLE_BAND: 75-89% (37-44/50) with context-binding; at least 10% improvement over
    uncontextualized lookup (no domain token)
  HARD_FAIL: < 75% correct OR context-binding token adds < 5% improvement over baseline

---

### Anchor 4: tier2_cs_intent_routing_v1 (customer support smoke demo)

Anchor pointer: Research note Section 4 + Section 13.1
Substrate-product reading: Implements 10 customer support schemas from the CS inventory
(CS-1 Report Bug, CS-2 Missing Order, CS-6 Login Problem, CS-7 Billing Error, CS-9 Cancel,
CS-10 Refund, CS-14 How-To, CS-18 Escalation, CS-22 Fraud, CS-25 Legal/GDPR). Tests
routing accuracy on 30 customer support message samples (3 per schema). The ROUTING_TARGET
slot from the matched schema is the classification output.

This is the most directly productizable anchor: a zero-shot intent classifier for customer
support using only substrate schema retrieval, no LLM, no training.

Tier hint: CPU laptop, ~4-6 hours (text tokenization + codebook build + 30 queries).
Gate: run after Anchor 1 PASS (does not require Anchor 2 or 3 first).

Pre-reg bands:
  HARD_PASS: routing accuracy >= 85% (25/30 correct schema selection)
  MIDDLE_BAND: 70-84% (21-24/30)
  HARD_FAIL: < 70% (< 21/30); schema-based routing no better than keyword matching baseline

---

### Anchor 5: tier2_slot_count_scaling_v1 (3 vs 5 vs 7 slots)

Anchor pointer: Research note Section 11 Prediction 4
Substrate-product reading: Tests whether schema retrieval degrades gracefully as slot count
increases from 3 (RT-1) to 5 (RT-7 Rowing: STILL_SPEED, CURRENT_SPEED, UP, DOWN + AGENT)
to 7 (RT-2 Meeting: AGENT_A, RATE_A, AGENT_B, RATE_B, INITIAL_GAP, TIME_MEET + CONTEXT).
20 test instances per slot-count level; partial query uses floor(slots/2)+1 filled slots.

Tier hint: CPU laptop, ~3 hours.
Gate: run after Anchor 1 PASS.

Pre-reg bands:
  HARD_PASS: accuracy >= 80% at 5 slots AND >= 70% at 7 slots
  MIDDLE_BAND: accuracy >= 70% at 5 slots AND >= 60% at 7 slots
  HARD_FAIL: accuracy < 60% at 5 slots (catastrophic degradation before useful codebook size)

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md
- NL-understanding 3x drill context: d:/AI/hd-instrument/notes/ (search research_drill_*NL* most recent)
- Language/math overlap drill: d:/AI/hd-instrument/notes/ (search research_drill_*language_math*)
- Substrate v3.0 compositional cliff results: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_v3_compositional_cliff_crossed.md
- Cap_map (PP-346 context-binding row): d:/AI/hd-instrument/notes/substrate_capability_map.md
- Tier-2 NLQA design answer: d:/AI/hd-instrument/notes/research_to_exp_dev_TIER_2_NLQA_DESIGN_ANSWER_2026-06-09.md
- Sprint 1+2 substrate-native results: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_primitives_yes_integration_no_2026-06-10.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current
queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: Anchor 1 (tier2_schema_retrieval_smoke_v1) MUST run first.
It is the gate for all other anchors. Anchor 4 (CS intent routing) can run in parallel
with Anchor 2 after Anchor 1 passes, since it tests the same mechanism on a different
domain without requiring multi-schema disambiguation first.

PRIORITY ORDER:
  Anchor 1 (schema retrieval smoke) -> FIRST, no gate
  Anchor 4 (CS intent routing) -> second if Anchor 1 passes; most productizable
  Anchor 2 (disambiguation) -> second if Anchor 1 passes; gates multi-schema overlay
  Anchor 5 (slot count scaling) -> third; characterizes codebook size limits
  Anchor 3 (domain routing) -> last; requires more setup, less urgent

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing the specific test instances (word problem texts, code snippets, CS messages)
  used for each anchor; these can be hand-crafted or drawn from public datasets
- Choosing tokenization strategy for mapping natural language to atom sequences
- Choosing N (vector dimensionality) for the schema codebook experiments
- Writing experiment scripts that follow the feedback_metrics_required_fields_write_metrics.md convention
- Choosing local CPU vs remote CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Adding new schemas to the codebook inventory beyond the 114 defined in the research note
  without routing back to research
- Interpreting schema retrieval results as product claims before orchestrator review
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
