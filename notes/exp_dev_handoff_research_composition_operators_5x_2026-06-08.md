# exp_dev hand-off -- research: substrate composition operators (5x deep)

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_substrate_composition_operators_5x_2026-06-08.md
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

Substrate's 12 validated compositional primitives (bind/unbind/bundle/negate/permute/
bidirectional/reification-class/counterfactual) constitute an algebra equivalent in
expressivity to Datalog^{neg} over bounded fact universes. The research drill identified
five new composition operators that extend this ceiling. Three are actionable with
CPU-only pre-tests (no cloud needed): stochastic temperature sampling (1-param change
to cleanup memory), type-polymorphic operators (compose from existing P1+P6), and
probabilistic weighted binding (fractional binding via amplitude modulation, requires
real-valued representation extension). Higher-arity bindings (4-ary/5-ary) are
near-free from validated nested binding (PP-118 d=16). Aggregation (SUM/COUNT over
bundle subsets) requires probabilistic binding first.

The expressivity comparison confirms substrate >= Datalog^{neg}; the main gap to
probabilistic Datalog is the probabilistic weighted binding operator. Filling this
gap would make substrate the first VSA-based system to natively support both
audit-grade algebraic certificates AND probabilistic belief updating in the same
retrieval operation.

---

## Anchor candidates (rank-ordered by P_actionable x pre-test cost)

### 1. COMP-TEMP-1: stochastic sampling via cleanup temperature (HIGHEST PRIORITY)

Anchor pointer: COMP-TEMP-1 (new; not yet queued)
Substrate-product reading: enables probabilistic retrieval from stored fact bundles.
  Instead of argmax (deterministic), cleanup memory returns a sample proportional to
  binding amplitudes. Converts substrate from a retrieval oracle into a distribution
  sampler. Relevant for Monte Carlo inference, ensemble reasoning, and soft ranking.
Tier hint: Tier 3 laptop CPU; 1-parameter change to existing cleanup memory; ~10 min wall
Why-now: lowest engineering cost of any new operator; highest P_deflated (0.35); depends
  on no other anchor; immediate capability uplift.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: retrieval probability proportional to stored amplitude within 15% relative
    error across 10 amplitude levels at N=4096, K=5 facts
  HARD-FAIL: retrieval probability variance across seeds > 50% (cleanup is deterministic
    and cannot be temperature-modulated at current N)
  MID-BAND: correlation r in [0.7, 0.85] between amplitude and retrieval probability

Inputs: existing bipolar codebook N=4096; K=5 fact bundle with heterogeneous amplitudes;
  temperature sweep T in {0.1, 0.5, 1.0, 2.0}. No new data generation needed.

### 2. COMP-TYPOLY-1: type-polymorphic retrieval (INDEPENDENT OF #1)

Anchor pointer: COMP-TYPOLY-1 (new; not yet queued)
Substrate-product reading: demonstrates that the same bind/unbind operation handles
  typed entities (person vs company vs location) without code changes. Type-conditional
  retrieval shows substrate can filter by semantic type using only the algebraic codebook
  -- no schema, no type registry, just type vectors.
Tier hint: Tier 3 laptop CPU; compose from P1+P6; ~10 min wall
Why-now: zero new primitives; independent of other anchors; validates type-system framing
  for the enterprise KG product pitch.

Pre-reg bands:
  HARD-PASS: type-conditional retrieval precision > 90% at K=20 mixed-type facts (N=4096)
  HARD-FAIL: precision < 70% (type vectors insufficiently orthogonal at N=4096)
  MID-BAND: precision in [70%, 90%]

Inputs: 20 entities of 2 types (10 each); 2 type anchor vectors orthogonal in codebook;
  queries: type_A_query and type_B_query; measure precision of returned entities.

### 3. COMP-ARITY-1: 4-ary binding pre-test

Anchor pointer: COMP-ARITY-1 (new; not yet queued)
Substrate-product reading: 4-ary bindings (subject, relation, object, context) enable
  temporally or contextually qualified facts (Paris capital-of France since 987 AD;
  claim valid in jurisdiction EU). Directly relevant to the bitemporal + multi-tenant
  architecture already validated at the system level.
Tier hint: Tier 3 laptop CPU; compose from validated nested binding; ~15 min wall
Why-now: PP-118 already validates nested binding to d=16; 4-ary is d=4; pre-test should
  hard-pass immediately; gates the contextual-qualification product story.

Pre-reg bands:
  HARD-PASS: bind4 retrieval accuracy > 75% at K=5 4-ary facts (N=4096)
  HARD-FAIL: accuracy < 55% (unexpected interference at d=4 nesting)
  MID-BAND: accuracy in [55%, 75%]

Inputs: K=5 four-way facts; verify recovery of any one of the four components given
  the other three. Cost: compose from existing bind/unbind; no new code.

### 4. COMP-FRAC-1: fractional binding (amplitude-weighted) pre-test

Anchor pointer: COMP-FRAC-1 (new; not yet queued)
Substrate-product reading: probabilistic weighted binding upgrades binary membership test
  to continuous confidence scores. Enables Bayesian belief updating in retrieved facts,
  ranked retrieval by confidence, and soft reasoning ("probably true" vs "definitely true").
  This is the single highest-leverage extension to the current substrate algebra.
Tier hint: Tier 3 laptop CPU; requires real-valued representation (not bipolar); ~30 min
Why-now: gating operator for probabilistic Datalog expressivity class; all downstream
  analytics (Bayesian update, aggregation, probabilistic chain inference) depend on this.
  Must run before COMP-AGG-1.

Pre-reg bands:
  HARD-PASS: at N=4096 real-valued, sim(query, frac_bind(A,B,w)) is monotone in w with
    Pearson r > 0.90 across 50 evenly-spaced weight values in [0.05, 0.95]
  HARD-FAIL: non-monotone in more than 20% of weight values (bipolar discretization
    breaks fractional binding theory; path blocked)
  MID-BAND: r in [0.70, 0.90] (monotone but noisy; bipolar approximation may still work)

Step 2 (if MID-BAND or HARD-PASS): run bipolar approximation (round w * bind(A,B) to
  nearest bipolar vector); measure correlation drop. If Pearson r drops by < 0.10,
  bipolar fractional binding is viable.

### 5. COMP-AGG-1: aggregation over bundle subsets (depends on COMP-FRAC-1)

Anchor pointer: COMP-AGG-1 (new; queued after COMP-FRAC-1 validates)
Substrate-product reading: COUNT / SUM / AVG queries over stored fact bundles. Converts
  substrate from a retrieval engine into an analytics engine. "How many claims in region
  North?" "What is the average value of claims tagged high-risk?" These are queries no
  existing retrieval-augmented system can answer algebraically.
Tier hint: Tier 3 laptop CPU; ~20 min wall; requires COMP-FRAC-1 PASS first
Why-now: gate is COMP-FRAC-1; if fractional binding validates, aggregation is a
  straightforward extension; highest product impact of the aggregation-class operators.

Pre-reg bands:
  HARD-PASS: SUM query over 10 amplitude-encoded items with known values returns estimate
    within 15% of true sum at N=4096
  HARD-FAIL: SUM estimate error > 40% (indicates amplitude encoding does not linearly
    add under bundling)

---

## Context pointers (file paths)

Research note:
  d:/AI/hd-instrument/notes/research_drill_substrate_composition_operators_5x_2026-06-08.md

Related prior notes:
  d:/AI/hd-instrument/notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
  d:/AI/hd-instrument/notes/capability_implication_consolidated_substrate_algebraic_characterization_2026-06-04.md

Relevant PP validations:
  PP-108 binding_associativity (monoid structure confirmed)
  PP-111 hierarchical class-instance
  PP-112 set membership
  PP-115 one-shot relation transfer K=5 0.913
  PP-117 algebraic negation exact
  PP-118 nested bindings d=16
  PP-139 counterfactual do() with audit chain

System validation:
  cycle 175 -- counterfactual do() full audit chain
  cycle 180 -- bidirectional KG traversal

Capability map:
  d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract section

exp_dev owns:
- Final pre-reg bands (may tighten or loosen from research recommendations above)
- Queue assignment (all 5 anchors are Tier 3 laptop CPU; none need cloud)
- Execution order (suggested: COMP-TYPOLY-1 and COMP-TEMP-1 in parallel first; COMP-ARITY-1
  independent; COMP-FRAC-1 after first two complete; COMP-AGG-1 last, conditional on FRAC)
- Sweep parameters (N values, K values, temperature grid, weight spacing)
- Self-test per formula-selftests protocol

Research does NOT own:
- Experiment design details
- Code implementation
- Queue timing
- Verdict interpretation (orchestrator / verdict_handler owns)

---

## Autonomy declaration

exp_dev has full autonomy to:
- Refine pre-reg bands based on substrate codebook statistics and prior sweep results
- Run pre-tests in any order that respects the dependency graph (FRAC before AGG)
- Extend sweeps if mid-band results warrant deeper investigation
- Escalate back to research via notes/exp_dev_to_research_*.md if pre-test reveals
  unexpected behavior (e.g., COMP-FRAC-1 HARD-FAIL would block probabilistic path
  and warrant a research rescue drill)

Dependency graph summary:
  COMP-TYPOLY-1 -- independent
  COMP-TEMP-1 -- independent
  COMP-ARITY-1 -- independent
  COMP-FRAC-1 -- independent (runs after TYPOLY + TEMP to not block those)
  COMP-AGG-1 -- requires COMP-FRAC-1 PASS or MID-BAND (step 2 viable)
