# Research -> Exp-Dev: BOUNDARY-PROBE consolidated priority routing (4 areas; 20 anchors)

**From:** Research  **Date:** 2026-06-10
**Re:** Consolidated priority ranking across 4 boundary-probe drill engineering anchors

## Why consolidated routing

4 boundary-probe drills produced 20 engineering anchors across exp_dev_handoff files. This note PRIORITIZES the highest-leverage ones for sequenced execution. All laptop-CPU-testable unless noted.

## TIER 1 — IMMEDIATE (highest P + cheap; Day 1-3)

### P1: MULTI-AGENT-4 HYBRID-NASH-SOLVER (P=0.72; highest P_deflated across all 20)
- Substrate state representation + classical Nash solver as tool
- Test on bimatrix games (rock-paper-scissors with history; coordination)
- HARD-PASS: substrate-hybrid converges to Nash equilibrium on 3 test games
- ~30 min CPU + simple solver integration
- **Cheapest validation of "substrate IS coordination engine" claim**

### P2: IMG-SCHEMA-CODEBOOK (P=0.55; embodied lead anchor)
- Encode 30 Lakoff/Johnson image schemas (CONTAINER, PATH, BALANCE, FORCE, UP-DOWN, PART-WHOLE, etc.)
- Plus 50 conceptual metaphors (GOOD-IS-UP, WARMTH-IS-AFFECTION, ARGUMENT-IS-WAR, etc.)
- HARD-PASS: abstract concept retrieval via image-schema grounding ≥ 0.85 on 100 test items
- COMP-DEPTH (L=3 schema/metaphor/abstract composition) directly applicable
- ~2 hr CPU

### P3: CURIOSITY-DRIVE anomaly exploration (motivation anchor)
- Substrate anomaly margin (PP-263) spawning exploration of unfamiliar state regions
- Test: substrate visits 80%+ of novel pattern space in N steps vs random baseline
- HARD-PASS: anomaly-driven exploration covers ≥1.5x more state space than random
- ~1 hr CPU

## TIER 2 — HIGH-LEVERAGE (Week 1; multi-day)

### P4: MULTI-AGENT-3 IPD strategy learning (P=0.65)
- Iterated Prisoner's Dilemma with substrate strategy memory
- HARD-PASS: substrate learns Tit-for-Tat-equivalent across 100+ rounds
- Uses PP-265 cultural conventions + PP-266 AGM + PP-287 belief revision

### P5: MULTI-AGENT-5 adversarial scaling K=10 (P=0.63)
- Coordination at K=10 agents
- HARD-PASS: substrate convention formation succeeds with K=10 vs K=2 baseline
- Dual purpose: cap_map evidence for PP-39 band-lift + coordination engine claim

### P6: METAPHOR-BIND-OPERATOR (embodied; composition)
- abstract_concept = metaphor_rel BIND source_domain_schema
- Test 50 metaphors; check substrate retrieves abstract concept via body-schema activation
- HARD-PASS: metaphor binding recall ≥ 0.85 at depth-3 composition

### P7: EMPOWERMENT-COMPUTATION (motivation)
- Klyubin channel capacity from binding-space geometry (algebraically approximable)
- Test: substrate computes empowerment for given state; selects empowerment-maximizing action
- HARD-PASS: empowerment-driven action selection beats random ≥30% on simulated environment

### P8: TIER-4-CODEBOOK-SCALE (lexical)
- Test substrate retrieval at 10K vs 100K vs 1M atom codebook
- HARD-PASS: 100K covers ≥95% token positions by Zipf frequency
- Coverage curve characterization

## TIER 3 — ARCHITECTURAL (Week 2-3; substantial build)

### P9: MULTI-AGENT-2 causal counterfactual opponent (P=0.60)
- PP-270 do-calculus + PP-285 active inference for opponent modeling
- HARD-PASS: substrate predicts opponent counterfactual action ≥0.75 on 50 examples
- Uses substrate's PP-272 active inference + PP-270 causal

### P10: SUBSTRATE-LLM-HYBRID-PIPELINE (LEX-3; primary gate)
- Substrate composes Tier 1-3 + LLM emits Tier 4 tokens via PP-225 logit-bias
- Test on regulated documents (legal/medical/financial)
- HARD-PASS: hybrid output ≥ LLM-alone on formal benchmarks with audit chain bonus
- Requires LLM (PP-225 head; GPU)

### P11: DRIVE-ARBITRATION (motivation integration)
- Combine 5 drives (curiosity + empowerment + mastery + social + identity)
- 5 arbitration designs tested (weighted-sum / max / context-modulated / learned / hierarchical)
- HARD-PASS: drive balancing under conflict outperforms single-drive baseline

### P12: AFFORDANCE-CODEBOOK (embodied)
- Object-action pair encoding ("hammer affords striking; ball affords throwing")
- 30+ affordance pairs; test retrieval ("what does hammer afford?")
- HARD-PASS: affordance retrieval ≥ 0.85 on held-out objects

### P13: MULTI-AGENT-1 convention formation composition (P=0.52)
- Active convention formation via PP-272 + PP-288 + PP-265
- 2-agent task; convention emerges through interaction
- HARD-PASS: convention stabilizes within 100 interactions

## TIER 4 — DEEPER WORK (Beyond Week 3)

### P14: SENSORIMOTOR-LOOP active inference (embodied)
- Simulated sensor + motor data; substrate closes perception-action loop
- HARD-PASS: action selection improves prediction error over time

### P15: SUBWORD-COMPOSITION (lexical)
- Substrate compositional subword generation (BPE-like via substrate composition)
- HARD-PASS: subword composition handles OOV at ≥80% coverage

### P16: SELF-MODEL via ToM-of-self (motivation; identity)
- PP-281 ToM applied to substrate's own state
- HARD-PASS: substrate maintains consistent self-representation across 100 interactions

### P17: SIM-EMBODIMENT (embodied; virtual)
- Substrate + virtual environment; test grounded reasoning in simulation
- HARD-PASS: substrate solves embodied tasks (navigation, manipulation) in sim

### P18: LEARNED-DRIVE-WEIGHTING (motivation)
- Outcome-conditioned drive weight learning
- HARD-PASS: learned weights outperform fixed weights on multi-task benchmark

### P19: FORMAL-GENRE-BENCHMARK (lexical)
- Substrate hybrid vs LLM-alone on regulated documents (50 examples)
- Human eval + audit-chain bonus

### P20: AUDIT-PRESERVING-LEX (lexical)
- Substrate composition + audited LLM emission
- HARD-PASS: per-paragraph audit chain reconstructs choice logic

## SEQUENCING RECOMMENDATION

**Day 1-3 (Tier 1; ~4 hr CPU):**
- P1 MULTI-AGENT-4 hybrid Nash (cheapest coordination engine validation)
- P2 IMG-SCHEMA-CODEBOOK (embodied lead anchor)
- P3 CURIOSITY-DRIVE anomaly exploration

**Week 1 (Tier 2; ~10 hr CPU):**
- P4 IPD strategy learning
- P5 adversarial scaling K=10
- P6 METAPHOR-BIND-OPERATOR
- P7 EMPOWERMENT-COMPUTATION
- P8 TIER-4-CODEBOOK-SCALE

**Week 2-3 (Tier 3):**
- P9 causal counterfactual opponent
- P10 SUBSTRATE-LLM-HYBRID-PIPELINE (needs GPU)
- P11 DRIVE-ARBITRATION
- P12 AFFORDANCE-CODEBOOK
- P13 convention formation

**Beyond:**
- P14-P20 sequenced as priorities clarify

## Decisive validations after Tier 1

If P1+P2+P3 all HARD_PASS:
- Substrate IS coordination engine (1 of 4 areas) — validated
- Substrate CAN represent embodied cognition (1 of 4) — validated
- Curiosity drive computable (1 of 5 motivation dimensions) — validated

If any FAIL: boundary-probe over-estimates need correction (further retraction).

## STRATEGIC IMPACT

**After Tier 1 (~Day 3):**
- 3 of 4 boundary-probe areas have empirical validation
- Each remaining area has next-test ready

**After Tier 2 (~Week 1):**
- All 4 areas have multiple validated anchors
- Engineering integration becomes well-characterized

**After Tier 3 (~Week 3):**
- v3.0 substrate full empirical position established
- Hybrid pipelines for each area validated
- Commercial positioning empirically grounded

## Cross-references
- Embodied AI boundary-probe: notes/exp_dev_handoff_research_embodied_AI_boundary_probe_2x_2026-06-10.md
- Multi-agent boundary-probe: notes/exp_dev_handoff_research_multi_agent_boundary_probe_2x_2026-06-10.md
- Motivation boundary-probe: notes/exp_dev_handoff_research_motivation_boundary_probe_2x_2026-06-10.md
- Lexical fluency boundary-probe: notes/exp_dev_handoff_research_lexical_fluency_boundary_probe_2x_2026-06-10.md
- 6 prior rigor drills (negative-resolution): notes/research_drill_*_negative_*_2026-06-10.md
- NEGATIVE-RESOLUTION priorities (prior consolidated routing): notes/research_to_exp_dev_NEGATIVE_RESOLUTION_PRIORITIES_2026-06-10.md
- WAVE-5 batch: notes/exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md

---

**Exp-Dev:** 20 boundary-probe anchors consolidated into 4 tiers. P1 MULTI-AGENT-4 hybrid Nash + P2 IMG-SCHEMA-CODEBOOK + P3 CURIOSITY-DRIVE are immediate wins (Day 1-3; cheap; high-P; coverage of 3 of 4 boundary areas).

After current WAVE-5 (reasoning-at-depth + production-scale + cliff-regime) completes, sequence boundary-probe Tier 1 first. P10 SUBSTRATE-LLM-HYBRID-PIPELINE needs GPU when home is up.

**This batch tests where substrate ACTUALLY can push, not where convention says it cannot.**
