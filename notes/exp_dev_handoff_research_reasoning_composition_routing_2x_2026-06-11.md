# exp_dev hand-off -- research: reasoning_composition_routing_2x

**Filed-by:** research sub-agent, 2026-06-11
**Trigger:** research_drill_reasoning_composition_routing_2x_2026-06-11.md delivered (Phase 3
  routing design mandate from Option 1 substrate-only deeper paths authorization).

**Pause state:** check data/orchestrator_paused.flag before dispatching any queue anchors.
  If paused: annotation bumps allowed; queue dispatch gated.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS
  only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
  anchor name, ETA, smoke profile, FULL profile.

---

## What research delivered

Phase 3 routing strategy: six-class problem-class taxonomy (deductive/probabilistic/causal/
counterfactual/temporal/analogical) mapped to substrate primitives (PP-343/PP-291/PP-307/PP-280/
PP-348/PP-275). Routing via substrate-as-classifier (prototype-bundle cosine matching from
slot-filled schema). Composition hierarchies for multi-mechanism chaining. DPEFE-iterative
routing as meta-reasoning layer. Multi-mechanism ensemble for ambiguous-class problems.

Research note path: d:/AI/hd-instrument/notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md

---

## Anchor candidates (rank-ordered)

### 1. PHASE3-ROUTING-ORACLE-T0 (CHEAPEST -- run first, TODAY)

**What:** 30-instance synthetic oracle. Hand-craft 5 slot-filled schemas per problem class
  (deductive/probabilistic/causal/counterfactual/temporal/analogical). Test substrate-as-
  classifier routing accuracy + primitive answer accuracy WITHOUT Phase 1+2 pipeline.

**Substrate-product reading:** decisive test for Phase 3 routing strategy INDEPENDENT of
  Phase 1+2 build. If routing_acc >= 0.75 and answer_acc >= 0.60, Phase 3 design is valid;
  Phase 1+2 integration becomes pipe-fitting. If either fails, Phase 3 prototype design
  needs revision BEFORE Phase 1+2 is completed -- massive time save.

**Tier hint:** local_cpu_queue, ~30 min, laptop. Pure substrate algebraic.

**HARD-PASS (Section 8 of research note):** routing_acc >= 0.75 (23/30), answer_acc >= 0.60
  (18/30), coverage >= 0.85 (26/30).

**Why now:** can run in PARALLEL with Phase 1+2 dep-parser build. Decoupled from Phase 1+2
  completion. Should run before Phase 3 integration to catch design errors early.

**Context:** research note Section 7 (cheapest decisive test) + Section 8 (HARD-PASS gates).

---

### 2. PHASE3-TEMPORAL-DOMINANT-TEST (next after Oracle)

**What:** Test the hypothesis that Class E (temporal/sequential) is the dominant class for
  MATH level-1 problems. On a sample of 10-15 hendrycks MATH level-1 instances, apply
  the Phase 3 routing classifier; measure what fraction route to Class E (temporal) vs
  Class A (deductive). If Class E > 0.60 of problems, temporal routing (PP-348 orchestrator
  + PP-343 per-step) should be the primary MATH path.

**Substrate-product reading:** MATH word-problems almost always involve multiple sequential
  steps with ordering constraints; temporal routing may be the dominant path, not pure
  algebraic deduction. This informs Phase 3+4 build priorities.

**Tier hint:** local_cpu_queue, ~1 hr, laptop. Manual inspection of routing outputs needed.

**HARD-PASS:** >= 0.60 of sampled MATH problems route to Class E (temporal) when using the
  constructed Phase 3 prototype classifier.

**Why now:** if temporal is dominant, Phase 3 build should prioritize PP-348 integration
  before PP-343 as the primary path.

**Context:** research note Section 3 Pattern 2 (Temporal -> Deductive composition) + Section 9
  cross-thread synthesis on PP-348 as underused asset.

---

### 3. DPEFE-REROUTE-RECOVERY-TEST (Phase 3 robustness)

**What:** Test DPEFE-iterative routing recovery. Deliberately mis-route 5 instances to the
  WRONG primitive class; apply DPEFE H=2 Bellman recovery; measure whether DPEFE finds the
  correct primitive within 2 rerouting attempts.

**Substrate-product reading:** DPEFE recovery is the meta-reasoning layer that makes Phase 3
  robust to initial mis-routing (which will happen on ambiguous schemas). Validates that PP-362
  generalizes from behavioral action selection to mechanism-class selection.

**Tier hint:** local_cpu_queue, ~1 hr, laptop.

**HARD-PASS:** recovery_rate >= 0.60 (3/5 instances correctly rerouted within 2 attempts).

**Why now:** validates DPEFE extension before Phase 4 integration. PP-362 already validated
  for behavioral actions (goal_reach=0.987); mechanism-class extension is the novel step.

**Context:** research note Section 6 (DPEFE-iterative routing) + Section 8 DPEFE HARD-PASS.

---

### 4. ENSEMBLE-COHERENCE-VOTE-TEST (Phase 3 ensemble)

**What:** Test multi-mechanism ensemble Option A (vote-by-result-coherence) on 10
  deliberately ambiguous-class schemas (e.g., "causal + temporal" or "probabilistic +
  deductive" mixed). Run both candidate primitives; whichever conclusion vector has
  higher codebook retrieval confidence wins; compare against human label.

**Substrate-product reading:** validates Option A ensemble before committing to the more
  expensive Option B/C. CODEGEN-SUBGOAL failure mode (context-unaware fixed decomposition)
  is the primary beneficiary; ensemble co-vote gives context-aware decomposition.

**Tier hint:** local_cpu_queue, ~1 hr, laptop.

**HARD-PASS:** agreement with human label >= 0.70 (7/10 instances).

**Why now:** needed before Phase 4 CODEGEN integration. If Option A fails, pivot to Option C
  (hierarchical verifier) before Phase 4 build.

**Context:** research note Section 5 (multi-mechanism ensemble) + Section 9 CODEGEN thread.

---

### 5. PHASE3-PHASE2-INTEGRATION-SMOKE (after Phase 1+2 completion)

**What:** Pipe Phase 2 construction grammar output (slot-filled schema) into Phase 3 routing
  classifier on 5 real hendrycks MATH level-1 instances. Verify end-to-end: NL input -> dep-
  parse -> slot-fill -> route -> primitive execute -> answer. No explicit HARD-PASS threshold
  pre-registered here (integration smoke; empirical results guide Phase 4).

**Substrate-product reading:** first end-to-end Phase 1+2+3 pipe test. Latent failures
  (misaligned schema slot format, prototype-to-primitive interface gaps) surface here before
  Phase 4 full build.

**Tier hint:** local_cpu_queue, ~2 hr, laptop.

**Why now:** only after Phase 1+2 dep-parser is passing HARD-PASS (UAS >= 0.85). Sequence
  after Phase 2 schema-match >= 0.50 precision gate.

**Context:** research note Section 3 (composition patterns) + OPTION_1 note Phase 3+4 design.

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md
- Option 1 authorization: d:/AI/hd-instrument/notes/research_to_exp_dev_OPTION_1_SUBSTRATE_ONLY_DEEPER_PATHS_2026-06-11.md
- NL extraction keystone: d:/AI/hd-instrument/notes/research_to_exp_dev_NL_EXTRACTION_KEYSTONE_PRIORITY_2026-06-11.md
- Sprint-3 temporal+contextual architecture: d:/AI/hd-instrument/notes/research_to_exp_dev_SPRINT3_TEMPORAL_CONTEXTUAL_ARCHITECTURE_2026-06-11.md
- Sprint-4 engineered wrapper: d:/AI/hd-instrument/notes/research_to_exp_dev_SPRINT4_ENGINEERED_WRAPPER_2026-06-11.md
- Strategy decisions (v3.1 primitives): d:/AI/hd-instrument/notes/strategy_decisions_2026-06-11.md
- Post-compaction brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-10_evening.md

---

## Contract section

Research has delivered the Phase 3 routing design. Exp-Dev owns ALL implementation decisions:
N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor naming, ETA, smoke
profile, full profile. Exp-Dev also decides sequencing across the 5 anchors above relative
to other active work (Phase 1+2 dep-parser, Sprint-4 engineering gates, promotion campaigns).

## Autonomy declaration

Exp-Dev is autonomous on all implementation choices. Research endorses the PHASE3-ROUTING-ORACLE-T0
as highest priority because it is decoupled from Phase 1+2 completion, cheap (~30 min), and
decisive (catches design errors before costly integration work). All other sequencing decisions
are exp_dev's to make.
