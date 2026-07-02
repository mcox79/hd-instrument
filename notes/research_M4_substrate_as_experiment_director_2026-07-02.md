# Research Drill: M4 Substrate-as-Experiment-Director Architecture

**Filed:** 2026-07-02 (research Sonnet sub-agent)
**Authorization:** USER strategic-gap coverage, Rank 2 next-milestone planning
**Context:** M3 approaching structural completion (4-primitive cortex CG, 5th smoke HP; Stage 1 97% mapped; commercial scale CG). M4 = hybrid agentic experiment loop where substrate acts as research director. This drill maps what that means architecturally, what primitives exist vs. must be built, and what the feasibility timeline looks like.
**Calibration:** lit-scan deflation 0.20; novel-synthesis cap P=0.50; symmetric anti-negativity applied.

---

## HEADLINE

**P_deflated(M4 viable within 18-30 mo) = 0.22**

The timeline is ACHIEVABLE but harder than the framing suggests. The core obstacle is not algorithmic — it is a primitives gap. "Substrate-as-director" requires 5 capabilities the current substrate does not have in CG form: EVALUATE (compare cell outcomes), PLAN (generate multi-step experiment sequences), REFINE (iterate on failed designs), META-LEARN (update strategy from outcome history), and DISPATCH (translate strategy decisions into queue operations). Of these, only EVALUATE has partial M3 coverage (refuse-gate calibration, TWOTIER context retention). The 18-30 mo range assumes M3 is closed by ~mo 6 and M4 primitives ship in rapid succession — a rate not yet demonstrated for novel-architecture work. P_deflated = 0.22 reflects: ~45% that the primitives are buildable on substrate physics at the required depth, deflated 0.20 for lit-scan optimism, further constrained by the Stage 1→2→3→4 sequencing discipline (M4 sits at Stage 3/4 boundary; Stage 2 is not yet open).

---

## PART 1: WHAT SUBSTRATE-AS-RESEARCH-DIRECTOR MEANS CONCRETELY

### Current human Director role decomposed

The human Director (me, now) does 8 distinct function classes:

| Function class | Description | Substrate-native? |
|---|---|---|
| PERCEIVE | Read metrics.json, queue state, runner heartbeats | Requires I/O bridge; substrate does not do file reads |
| EVALUATE | Compare cell outcomes against pre-reg thresholds; tier verdicts | PARTIAL — refuse-gate + TWOTIER give confidence scoring; missing cross-cell comparison |
| PLAN | Generate new experiment cells from gaps in phase diagram | NOT PRESENT — requires forward-model of experiment space |
| DISPATCH | Write queue_add calls, pass anchors, set run_mode | NOT PRESENT — requires action generation + grounding |
| REFINE | Iterate on failed cells (debug, revise mechanism class) | NOT PRESENT — requires counterfactual reasoning |
| META-LEARN | Update strategy (director_plan.json) based on session outcomes | NOT PRESENT — requires online W-update from labeled decisions |
| SYNTHESIZE | Cross-cell synthesis, CG promotion decisions | PARTIAL — multihop depth CG, K-beam path-sum gives some chaining; no structured-evidence aggregation |
| COMMUNICATE | Write BACKUP docs, spawn Skunkworks VET prompts | Explicit language generation is Stage 4 |

### Honest scope of "substrate does it"

The M4 target is NOT that substrate does all 8 unassisted. M4 is a HYBRID agentic loop where:
- LLM (Claude) handles I/O, language generation, and high-level framing
- Substrate handles EVALUATE + PLAN fragment generation + SYNTHESIZE (the substrate-native primitives)
- The substrate's contribution is as a persistent memory + fast lookup + structured pattern-completion engine that biases the LLM toward prior experiment knowledge

Concretely: M4 substrate-as-director means the substrate can answer questions like "which phase-diagram axis has the lowest coverage?" (EVALUATE on atoms.jsonl encoding) and "given this failure mode, which prior recovery paths have CG grade?" (SYNTHESIZE via multihop on atom graph). The LLM then converts these substrate-retrieved recommendations into action.

This is much more tractable than "substrate writes the cell" and much more concrete than "substrate is the director in some abstract sense."

---

## PART 2: CG PORTFOLIO EVIDENCE PRO/CON

### Evidence PRO M4 viability

**Multihop depth CG (Atom 19, depth bracket (50,55]):** Substrate can chain 50+ sequential retrieval hops without loss below 0.5. This is the PLAN primitive's retrieval substrate — each hop is one "step of reasoning about experiment space." P_M4_relevance = 0.55 (multihop is over KB facts not over experiment design space, but the mechanism is identical).

**Cortex TWOTIER context retention CG (Atom 18, M1.5):** K=100 STM + K=4096 LTM allows substrate to retain a session's worth of experiment outcomes in working memory while continuing to retrieve from long-term KB. This is the META-LEARN primitive's memory scaffold. P_M4_relevance = 0.60 (context retention maps directly to "remember what happened in this session").

**Refuse-gate conformal calibration CG (Atom 15, M1.4):** Substrate can express calibrated confidence (accept/reject decision with coverage guarantee). This is the EVALUATE primitive's decision layer — substrate can flag "this outcome is anomalous vs. prior CGs." P_M4_relevance = 0.65 (calibration is directly the same operation whether applied to conversational inputs or cell outcomes).

**Attention router 4-class CG (Atom D, M1.6):** Substrate can route an input to one of 4 action classes. This is the DISPATCH primitive's action selection layer — "given this cell outcome, route to [PROMOTE_CG / VET_FURTHER / HARD_FAIL_CLOSE / REVIVE_DRILL]." P_M4_relevance = 0.50 (4 classes is a small action space; real director decisions are higher-cardinality).

**Commercial scale CG (LLN V_C=1M):** Substrate can hold the full experiment graph (atom count O(200k)) without capacity collapse. P_M4_relevance = 0.70 (this is a prerequisite, not a capability; it proves substrate can HOLD the M4 knowledge graph but not that it can reason over it).

**Löwe correlated-key capacity law (α_c(ρ) ≈ 0.138(1-ρ²)):** Substrate physics is now analytically characterized under correlated inputs — the EVALUATE primitive will routinely receive correlated cell outcomes (cells within the same arc share experimental design). Knowing the capacity law lets us predict when EVALUATE will saturate. P_M4_relevance = 0.60 (quantitative bound on a core failure mode).

**Role-slot summarization smoke HP (M1.7 5-primitive):** If M1.7 lands CG, it demonstrates substrate can maintain structured slot-filler representations (e.g., RESULT_OF(cell_anchor, outcome_grade)). This is the structured encoding needed for SYNTHESIZE. P_M4_relevance = 0.55 pending full run.

### Evidence AGAINST M4 viability

**Partition-oracle correction (Atom 11 amendment, 2026-07-01):** Substrate's apparent multi-hop "over-performance" at depth > 45 is a partition-oracle artifact (Markov floor r=0.006, fitted p=0.985). Without oracle, effective r → 0 and depth performance collapses. This matters for M4 because the PLAN primitive requires chaining experiment-design steps WITHOUT access to a known answer (no oracle). The partition-oracle finding directly predicts M4 PLAN will fail at depth > ~20 steps without structural intervention. P_PLAN_fails_without_intervention = 0.65.

**Forward model absent:** The human Director has a generative model of "what experiment would test X?" The substrate has NO forward-model primitive — it has only retrieval (what has been tested) not generation (what should be tested next). Forward models in the brain literature (Wolpert MOSAIC) require paired forward + inverse components with responsibility signals. Building this on substrate is Stage 3/4 work with no current cell candidates. P_forward_model_buildable_on_substrate = 0.30.

**Correlated-error amplification at multi-hop (2026-06-27 BP drill):** The belief-propagation drill established that substrate's chain mechanism fails at scale due to correlated-error amplification — no extrinsic-information separation. For M4's SYNTHESIZE primitive (aggregating evidence across ~50 cells), this is the same failure mode. The K-beam path-sum fix (P_CG = 0.40) would address it but is not yet CG. P_SYNTHESIZE_at_50_atoms_without_K_beam = 0.25.

**No online W-update mechanism:** META-LEARN requires updating the substrate's associative weights based on session outcomes. All current substrate primitives are OFFLINE trained (W written once, then read). The CLS replay continual learning cell (preregs/2026-06-22_cls_replay_continual_learning_smoke_v1.md) is the only candidate; it's a smoke preregistration, not CG. P_META_LEARN_substrate_native = 0.20.

**DISPATCH requires grounded action generation:** Translating a substrate-retrieved strategy fragment into a specific queue_add call (with correct anchor slug, run_mode, seed count) requires grounding to filesystem state. This is not a substrate primitive — it requires LLM integration as the grounding layer. Substrate can SELECT an action class; it cannot GROUND it. This is honest but means M4 is permanently hybrid (LLM cannot be fully excised from the dispatch loop).

---

## PART 3: RANKED M4 PRIMITIVE CANDIDATES

### Primitive 1: EVALUATE-OUTCOME (rank 1; highest leverage, M3-adjacent)

**What it is:** Given a cell outcome (anchor + metrics.json fields) and the pre-reg threshold set (from atoms.jsonl), substrate computes a confidence-weighted verdict: PROMOTE / HOLD / REVIVE / CLOSE.

**M3-dependency:** M1.4 (refuse-gate calibration) + M1.5 (TWOTIER context) must be CG. Both are CLOSED. EVALUATE-OUTCOME can begin NOW.

**Development cost:** LOW. This is essentially a retrieval-scored decision problem: retrieve the pre-reg atom for anchor X, compare observed fields against REQUIRED_FIELDS + threshold bands, apply refuse-gate to the outcome vector. Cell design would be: encode cell outcomes as VSA vectors (anchor_hash XOR metric_vector), retrieve matching pre-reg atom, score cosine against threshold bands, apply conformal coverage. Estimated 1-2 cells.

**Key discriminator:** Does EVALUATE-OUTCOME match human Skunkworks tier verdicts at >= 85% agreement on a held-out set of 30 landings? (Deflated P_CG = 0.45.)

**M4-payoff:** Direct — substrate-automated VET would eliminate the Skunkworks bottleneck for routine landings. This is the highest-ROI M4 primitive.

### Primitive 2: SYNTHESIZE-EVIDENCE (rank 2; enables PLAN; K-beam required)

**What it is:** Given a question "what do we know about axis X?" substrate traverses the atom graph to aggregate CG-grade atoms relevant to X, returns a ranked summary of findings with confidence weighting.

**M3-dependency:** K-beam path-sum cell (P_CG = 0.40, not yet dispatched) + commercial scale (CG) + TWOTIER (CG). K-beam is gating.

**Development cost:** MEDIUM-HIGH. Requires K-beam path-sum CG first (1 cell), then structured evidence aggregation cell (aggregation over atom attributes, not just chain retrieval). Estimated 3-4 cells.

**Key discriminator:** Given a synthetic "what do we know about capacity axis?" query, does substrate-retrieved synthesis match human research drill outputs at >= 70% content overlap? (Deflated P_CG = 0.30, given K-beam prerequisite.)

**M4-payoff:** Enables substrate to field research-drill-class questions autonomously. Cuts Sonnet drill load by ~40% for factual synthesis questions (vs. novel mechanism questions which still need external drill).

### Primitive 3: PLAN-FRAGMENT (rank 3; hardest; forward-model required)

**What it is:** Given a coverage gap (detected by SYNTHESIZE), substrate generates a candidate experiment specification fragment: which primitive to test, which arms, which discriminator.

**M3-dependency:** SYNTHESIZE-EVIDENCE (CG) + role-slot summarization (M1.7 CG) + a forward-model primitive (NOT YET DESIGNED). Forward-model is the hard gate.

**Development cost:** VERY HIGH. Forward-model is not in the current cell backlog. It requires:
(a) A generative component that produces experiment candidates (most naturally: LLM generates candidates conditioned on substrate-retrieved context)
(b) Substrate evaluates and ranks candidates against prior coverage (SYNTHESIZE substep)
(c) Selection via refuse-gate-style confidence cutoff

This decomposition makes PLAN-FRAGMENT a HYBRID primitive even in the M4 vision. The substrate cannot generate the candidate cell spec — LLM does that. Substrate ranks it.

**Key discriminator:** Given 5 LLM-generated cell specs for a coverage gap, does substrate select the one that human Director would select >= 70% of the time? (Deflated P_CG = 0.22.)

**M4-payoff:** If this lands CG, it constitutes the core "substrate-as-director" claim — substrate is guiding what gets tested. This is the load-bearing M4 capability. Without it, M4 is only automation of routine VET + evidence retrieval (useful but not the milestone vision).

### Primitive 4: META-LEARN-STRATEGY (rank 4; requires online update)

**What it is:** Substrate updates its internal weights based on the session's experiment outcomes, so future queries reflect learned success-rate patterns (e.g., "cells in the attention-router family have CG conversion rate 0.72; cells in the multihop-soft-chain family have CG conversion rate 0.28 — bias toward attention-router families").

**M3-dependency:** CLS replay (continual learning, preregs/2026-06-22) must CG. That smoke preregistration is NOT YET RUN.

**Development cost:** HIGH. CLS replay requires:
(a) Hippocampal fast-write W_hippo for new session outcomes
(b) Periodic offline NREM-replay consolidation into W_cortex
(c) Interference prevention (catastrophic forgetting discipline)

The fundamental physics here: online W-update at N=8192 with M existing memories requires careful capacity management. At the Löwe correlated-key law, session-level updates (O(100) new outcomes per session) into a substrate already at α ≈ 0.10 nominal load are SAFE (far from capacity wall) — but only if updates are decorrelated from existing atoms. Family-correlated experiment outcomes (all from same arc) violate this assumption. P_META_LEARN_safe = 0.35.

**Key discriminator:** After 3 sessions of meta-learning, does substrate's PLAN-FRAGMENT selection shift toward high-CG-rate families and away from low-CG-rate families? Requires full M4 stack to test.

**M4-payoff:** This is the "self-improving director" capability. Without it, M4 is a static expert system. With it, M4 improves over sessions — the beginning of the M5 trajectory.

### Primitive 5: DISPATCH-GROUND (rank 5; permanently hybrid; LLM does grounding)

**What it is:** Translate a substrate-selected action class (PROMOTE / REVIVE / DISPATCH_NEW) into a concrete filesystem operation (queue_add call, pre-reg file write, anchor slug).

**M3-dependency:** M1.6 attention router (CG) as action-selection layer. Grounding itself = LLM.

**Development cost:** LOW-MEDIUM for the LLM side, NOT SUBSTRATE-NATIVE. Substrate contributes action classification and template retrieval. LLM fills in slug, paths, seed counts from current filesystem state. This is a system-integration task, not a substrate-primitives task.

**Key discriminator:** Does the M4 pipeline (substrate selects action class + LLM grounds it) produce valid queue_add calls at >= 95% syntactic validity and >= 80% semantic correctness (right cell, right run_mode) on 20 test cases? P_CG = 0.55 — largely an engineering task once action-selection works.

---

## PART 4: M3→M4 TRANSITION SEQUENCING PLAN

### Phase 0 (M3 completion, now → ~mo 6): Close the M3 primitives
Required closures:
- M1.7 role-slot summarization (5th cortex CG)
- Deep-composition M1.4+M1.5+M1.6 stack test
- Commercial-M (M=100k-1M) closure
- Stage 2 optimization work (not yet open)

M4 is NOT viable until M3 is fully closed and Stage 2 begins. Skipping the sequencing discipline is the fastest path to wasted M4 cells that fail for Stage-2-prerequisite reasons.

### Phase 1 (mo 6-10): EVALUATE-OUTCOME primitive
- Ship EVALUATE-OUTCOME as a Stage 3 cell (this is Stage 3 work: substrate evaluating structured experiment outcomes is compositional understanding)
- Pre-reg: encode 30 cell outcomes as VSA vectors, retrieve pre-reg atoms, score against threshold bands, compare to Skunkworks verdicts
- Gate: 85% agreement on held-out 10 landings before declaring M4-primitive-1 CG
- Estimated timeline: 2-3 cells, 1-2 mo

### Phase 2 (mo 10-15): K-beam + SYNTHESIZE-EVIDENCE
- Dispatch K-beam path-sum cell (highest leverage for both M3 multihop and M4 SYNTHESIZE)
- If K-beam CG, build SYNTHESIZE-EVIDENCE as evidence-aggregation on atom graph
- Gate: synthesis outputs match human research drill summaries at 70% content overlap on 5 held-out queries
- Estimated timeline: 4-5 cells, 3-5 mo

### Phase 3 (mo 15-22): PLAN-FRAGMENT (hybrid)
- Design PLAN-FRAGMENT as substrate-ranks-LLM-generates architecture
- Requires M1.7 + SYNTHESIZE-EVIDENCE as prerequisites
- First test: 5-candidate ranking task (substrate picks best experiment design given coverage gap)
- Gate: 70% match with human Director selection on 20 test cases
- Estimated timeline: 5-8 cells (novel architecture, expect 2-3 failure-mode discoveries), 6-8 mo

### Phase 4 (mo 20-30): META-LEARN + full M4 integration
- CLS replay CG (if not already landed during Stage 2)
- Integrate EVALUATE + SYNTHESIZE + PLAN-FRAGMENT + META-LEARN into a single session loop
- Gate: substrate directs 3 experiment sessions without human Director intervention on strategic decisions (Director monitors, LLM grounds, substrate decides)
- Estimated timeline: 8-12 mo (integration complexity; first-of-kind for this architecture)

### Total estimated timeline to M4 viable: 20-26 mo from today
This OVERLAPS the 18-30 mo window but lands near the back end (mo 20-26 not mo 18). Compressing below mo 20 would require parallel M3/M4 work before M3 is closed, which the stage-progression discipline prohibits.

---

## PART 5: FALSIFIABLE PREDICTIONS

### Prediction 1: EVALUATE-OUTCOME CG is achievable within 3 cells
**Test:** Ship EVALUATE-OUTCOME cell with pre-reg. PASS bar = 85% Skunkworks-agreement on held-out 10 landings. This is the first M4-primitive closure.
**If HARD_FAIL:** Substrate cannot do cross-cell comparison even with M1.4+M1.5 CG — M4 viability drops from 0.22 to 0.10. If PASS: viability upgrades to 0.32.

### Prediction 2: K-beam path-sum will CG at the 5-hop benchmark (P_def = 0.40)
**Mechanism:** K-beam maintains K diverse candidate paths through hop steps, aggregates at end (particle filter analog). This avoids the correlated-error amplification failure mode diagnosed in the BP drill.
**If HARD_FAIL:** Both SYNTHESIZE-EVIDENCE and the multihop extreme-depth chain are blocked. The no-extrinsic-information-separation structural finding is MORE fundamental than K-beam fix. M4 viability drops to 0.12. If PASS: viability upgrades to 0.30.

### Prediction 3 (load-bearing): M4 is feasible WHEN substrate can compose a 20-primitive chain end-to-end without cortex intervention (the USER's suggested falsifiable criterion)
**Honest assessment:** PARTIAL. Chain length 20 is already within the multihop CG bracket (depth bracket (50,55] = CG). But "20-primitive experiment-design chain" is harder than "20-hop KB retrieval chain" because:
(a) Each primitive is a structured operation (not a simple entity lookup)
(b) The partition-oracle crutch is absent in experiment-design space
(c) The chain must be coherent (each step must constrain the next semantically)
The substrate is NOT ready for criterion (c) — structured coherence across semantic steps. That requires SYNTHESIZE-EVIDENCE + role-slot summarization, both of which are not yet CG. The correct falsifiable criterion is: **M4 is feasible when substrate achieves CG on EVALUATE-OUTCOME + SYNTHESIZE-EVIDENCE + PLAN-FRAGMENT-ranking.** All three must close; the 20-primitive-chain metric is necessary but not sufficient.

---

## PART 6: ARCHITECTURE SKETCH

```
M4 SUBSTRATE-AS-EXPERIMENT-DIRECTOR (hybrid; M3+LLM+substrate)

PERCEPTION LAYER (LLM)
  - Read metrics.json, queue.json, atoms.jsonl
  - Convert to structured event: (anchor, outcome_grade, axis_coverage_delta)
  - Feed to substrate EVALUATE port

SUBSTRATE LAYER (3 ports)
  EVALUATE port:
    encode event as VSA vector
    retrieve matching pre-reg atom
    refuse-gate score vs threshold bands
    output: {tier_recommendation, confidence, coverage_delta}

  SYNTHESIZE port (queries):
    receive axis-coverage-gap query
    K-beam traverse atom graph
    return: {top-k prior results, confidence weighting, coverage fraction}

  PLAN port (ranking only):
    receive: set of LLM-generated candidate cell specs (5-10)
    score each against: coverage gap size, prior CG rate for family, capacity estimate
    output: ranked candidates with substrate-confidence scores

LLM GROUNDING LAYER
  - Receive substrate PLAN output (ranked candidates + confidence)
  - Select top candidate
  - Ground to filesystem: write pre-reg, generate anchor slug, call queue_add
  - Monitor landing, route outcome back to EVALUATE port

META-LEARN LAYER (future, mo 20+)
  - After session: replay outcomes into W_hippo via CLS mechanism
  - Periodic offline consolidation into W_cortex
  - Update family-success-rate atoms in atoms.jsonl
```

The key architectural constraint: **LLM cannot be removed from PERCEPTION and GROUNDING even at M4 maturity**. The substrate's contribution is EVALUATE + SYNTHESIZE + PLAN-ranking. LLM handles I/O and grounding. This is not a limitation of the design — it is the correct hybrid architecture where substrate does what it is provably good at (fast associative retrieval, calibrated confidence, chained reasoning) and LLM does what it is good at (language parsing, action grounding, novel generation).

---

## SUMMARY

**P_deflated(M4 viable within 18-30 mo) = 0.22**

**Top 3 M4 primitives to build (ranked by feasibility x payoff):**

1. **EVALUATE-OUTCOME** (P_CG = 0.45): encode cell outcomes as VSA vectors, retrieve pre-reg atoms, apply refuse-gate verdict. M3-dependencies already closed. Start NOW in Stage 3. ~2-3 cells, ~2 mo. Highest-ROI M4 primitive; directly eliminates Skunkworks bottleneck for routine VET.

2. **SYNTHESIZE-EVIDENCE** (P_CG = 0.30): K-beam traversal over atom graph to aggregate evidence for axis-coverage queries. Requires K-beam CG first. ~4-5 cells, ~5 mo total including K-beam. Enables substrate to answer "what do we know about X?" in lieu of full Sonnet research drills.

3. **PLAN-FRAGMENT-ranking** (P_CG = 0.22): substrate ranks LLM-generated experiment candidates by coverage gap fit + family CG rate. Requires SYNTHESIZE + M1.7 role-slot. ~5-8 cells, ~8 mo. This is the load-bearing "substrate-as-director" claim — without it, M4 is only automation, not strategic direction.

**Key risks:**
- Partition-oracle correction predicts PLAN fails at depth > 20 steps without structural fix (K-beam or equivalent). Do not assume multihop depth CG translates to semantic chain.
- META-LEARN requires online W-update discipline not yet validated; CLS replay is smoke-preregistered only.
- Stage-progression constraint: M4 work cannot begin substantively until M3 + Stage 2 are closed (per USER-locked discipline). Effective M4 start = mo 6+, not today.

**M3→M4 transition gate:** M4 is viable when EVALUATE-OUTCOME + SYNTHESIZE-EVIDENCE + PLAN-FRAGMENT-ranking all CG. No single primitive is sufficient; the loop requires all three to close before substrate can substitute for human Director judgment on routine dispatch decisions.
