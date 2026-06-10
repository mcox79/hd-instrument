# Research -> Exp-Dev: AGGRESSIVE BOUNDARY-PUSH BATCH (4 areas; full empirical assault)

**From:** Research  **Date:** 2026-06-10
**Re:** Aggressive empirical batch on 4 boundary-probe areas; push past minimum gates to characterize actual achievable ceiling

## Mandate

User: "Aggressive experiments moving on these 4 areas — understand how far we can push it short-term, open eyes on real potential."

Previous batches were minimum viable. This batch is AGGRESSIVE: stretch targets + multiple parallel anchors + standard benchmarks + characterization beyond HARD-PASS.

## AREA 1: EMBODIED AI (P=0.55) — aggressive push

### EMB-A1: Full Johnson 1987 image schema encoding (35+ schemas)
- Encode ALL of: CONTAINER, PATH, BALANCE, FORCE, UP-DOWN, PART-WHOLE, CENTER-PERIPHERY, NEAR-FAR, FRONT-BACK, IN-OUT, SOURCE-PATH-GOAL, ITERATION, OBJECT, COLLECTION, SPLITTING, MERGING, MATCHING, SCALE, ATTRACTION, BLOCKAGE, COUNTERFORCE, COMPULSION, RESTRAINT-REMOVAL, ENABLEMENT, DIVERSION, LINK, CYCLE, PROCESS, SUPERIMPOSITION, PROCESS, plus 5 more
- HARD-PASS: 30+ schemas substrate-retrievable with ≥0.85 fidelity

### EMB-A2: 100 conceptual metaphor encoding + composition
- Beyond 50 (boundary-probe target): GOOD-IS-UP, MORE-IS-UP, HAPPY-IS-UP, AFFECTION-IS-WARMTH, ARGUMENT-IS-WAR, LIFE-IS-A-JOURNEY, IDEAS-ARE-OBJECTS, UNDERSTANDING-IS-SEEING, THEORIES-ARE-BUILDINGS, TIME-IS-MONEY, ARGUMENT-IS-CONTAINER, plus 89 more (Lakoff & Johnson catalog)
- Test: abstract concept retrieval via metaphor binding at L=3 composition
- HARD-PASS: ≥0.80 retrieval on 100 abstract-domain queries

### EMB-A3: Glenberg-Kaschak action-sentence compatibility benchmark
- Substrate encodes sentence + motor-primitive shards
- Test: substrate predicts action-sentence compatibility (same direction = faster RT analog)
- HARD-PASS: substrate response-time-analog correlates with Glenberg human data ≥0.65

### EMB-A4: Conceptual Metaphor Identification (MetaNet/MetaBank benchmark)
- Standard NLP benchmark for metaphor detection
- Substrate uses image-schema codebook + metaphor binding
- HARD-PASS: F1 ≥ 0.65 on MetaNet (LLM baselines ~0.70-0.85)

### EMB-A5: Affordance prediction benchmark (Sapnet / iCub affordance datasets)
- Object-action pair retrieval
- HARD-PASS: ≥0.75 on held-out objects

### EMB-A6: Sim-embodiment full integration
- Substrate + virtual gridworld (PyGame)
- Substrate sees state, generates action via sensorimotor loop
- HARD-PASS: substrate solves navigation + manipulation on 10 procedurally-generated environments

## AREA 2: MULTI-AGENT (P=0.68) — aggressive push

### MA-A1: OpenSpiel game battery
- Substrate + classical Nash solver on 10 standard games (Kuhn poker, leduc poker, matrix games)
- HARD-PASS: substrate-hybrid matches MARL baseline on 7/10 games

### MA-A2: Hanabi cooperative play (Bard et al. 2020 benchmark)
- 2-agent cooperative card game; requires ToM
- Substrate ToM-depth-3 + PP-265 conventions + PP-288 common knowledge
- HARD-PASS: substrate cooperative score ≥ 18/25 (rule-based baseline; LLM ~15-22)

### MA-A3: Iterated Prisoner's Dilemma tournament (Axelrod-style)
- Substrate strategy + 50+ classical strategies
- HARD-PASS: substrate ranks top-10 in tournament

### MA-A4: Convention emergence with K=100 agents
- 100 agents coordinating via PP-265
- HARD-PASS: stable convention within 1000 rounds

### MA-A5: Mechanism design (single-item auction)
- Substrate encodes Vickrey/English/Dutch auction protocols
- HARD-PASS: incentive-compatible behavior on substrate-encoded mechanism

### MA-A6: Belief revision benchmark (Hadron / WSC analog)
- Substrate AGM applied to changing world; track belief consistency
- HARD-PASS: belief consistency ≥ 0.95 over 100 changes

### MA-A7: MARL replay buffer integration
- Substrate as CTDE state representation for MADDPG/QMIX
- HARD-PASS: MARL convergence improved with substrate state vs vanilla

## AREA 3: MOTIVATION (P=0.42) — aggressive push

### MOT-A1: Open-ended exploration on procedurally-generated environments
- Substrate curiosity drive (anomaly margin) on Minigrid procedurally-generated
- HARD-PASS: substrate covers ≥80% of state space vs random ≤30%

### MOT-A2: Klyubin empowerment maximization
- Substrate computes empowerment from binding-space geometry
- Action selection maximizes empowerment
- HARD-PASS: substrate-empowerment-agent maintains options ≥2x random baseline

### MOT-A3: Multi-objective drive arbitration on competitive environment
- Substrate balances curiosity + empowerment + mastery + social
- Test on 10 multi-task benchmarks (NetHack-mini, Crafter)
- HARD-PASS: substrate outperforms single-drive baselines on multi-task

### MOT-A4: Skill discovery via mastery drive (DIAYN-style)
- Substrate identifies repeatable skills via schema consolidation
- HARD-PASS: substrate discovers ≥10 distinct skills on continuous control

### MOT-A5: Self-model identity coherence over long sessions
- Substrate maintains self-representation across 1000+ interactions
- HARD-PASS: self-model coherence ≥0.85 after 1000 interactions

### MOT-A6: Curiosity-driven learning vs goal-driven (Schmidhuber comparison)
- Substrate with curiosity drive vs goal-only on multi-task benchmark
- HARD-PASS: curiosity-driven matches goal-driven on assigned tasks while exploring more

### MOT-A7: Emergent goal formation via anomaly + empowerment
- Substrate generates own goals from anomaly + empowerment signals
- HARD-PASS: emergent goals lead to skill development on benchmarks

## AREA 4: LEXICAL FLUENCY (P=0.40) — aggressive push

### LEX-A1: Tier-4 codebook scale 1M+ atoms
- Substrate Tier 4 at 10K vs 100K vs 1M vs 10M atoms
- HARD-PASS: 1M covers ≥99% token positions by Zipf

### LEX-A2: HumanEval code generation
- Substrate composes function shards + LLM emits via PP-225
- HARD-PASS: substrate-LLM hybrid pass@1 ≥ LLM-alone

### LEX-A3: MBPP (Mostly Basic Python Problems)
- Same architecture; harder benchmark
- HARD-PASS: substrate-LLM hybrid pass@1 ≥ LLM-alone with audit-chain bonus

### LEX-A4: Translation benchmarks (FLORES, WMT)
- Substrate Tier 0 (NSM primitives) + per-language Tier 1-3
- HARD-PASS: BLEU ≥ small multilingual LLM baseline

### LEX-A5: Formal document generation (legal/medical/financial)
- Substrate-LLM hybrid on regulated genre prompts
- Human eval: 50 prompts; substrate-hybrid vs LLM-alone
- HARD-PASS: ≥40% preference for substrate-hybrid (parity)
- STRETCH: ≥60% preference (decisive win in formal genre)

### LEX-A6: Subword composition (BPE-like via substrate)
- Substrate compositional Tier 4 generation for OOV
- HARD-PASS: OOV coverage ≥80% via composition

### LEX-A7: Audit-preserving generation
- Substrate composition + LLM emission with per-paragraph audit chain
- Verify: audit chain reconstructs choice logic for 100% of generated paragraphs

### LEX-A8: Substrate-Translation tier 0 invariance
- Same Tier 0 primitives across 5 languages
- HARD-PASS: cross-lingual semantic invariance ≥0.85 at Tier 0 layer

## SEQUENCING (aggressive parallel where possible)

### Sprint 1 (Week 1 — characterize baselines)
**Embodied:** EMB-A1 (full schema codebook) + EMB-A2 (100 metaphors)
**Multi-agent:** MA-A1 (OpenSpiel battery) + MA-A2 (Hanabi)
**Motivation:** MOT-A1 (exploration) + MOT-A2 (empowerment)
**Lexical:** LEX-A1 (codebook scale) + LEX-A2 (HumanEval)

Total: 8 parallel anchors; tests all 4 areas at decent depth

### Sprint 2 (Week 2 — push to benchmark parity)
**Embodied:** EMB-A4 (MetaNet) + EMB-A6 (sim-embodiment)
**Multi-agent:** MA-A3 (Axelrod tournament) + MA-A6 (belief revision)
**Motivation:** MOT-A3 (multi-objective) + MOT-A6 (curiosity-vs-goal)
**Lexical:** LEX-A5 (formal documents) + LEX-A7 (audit-preserving)

### Sprint 3 (Week 3-4 — stretch + integration)
**Embodied:** EMB-A3 (Glenberg-Kaschak) + EMB-A5 (affordance)
**Multi-agent:** MA-A4 (K=100) + MA-A7 (MARL integration)
**Motivation:** MOT-A4 (DIAYN) + MOT-A5 (identity) + MOT-A7 (emergent goals)
**Lexical:** LEX-A3 (MBPP) + LEX-A4 (translation) + LEX-A6 (subword) + LEX-A8 (Tier-0)

## Resource estimate

| Sprint | Total experiments | CPU-hr (laptop) | GPU-hr (home) |
|---|---|---|---|
| 1 | 8 | 20-40 | 6-12 (LEX-A2 only) |
| 2 | 8 | 30-50 | 6-12 (LEX-A5/A7) |
| 3 | 12 | 50-80 | 12-24 (multiple LEX + sim-embodiment) |

**Total ~28 experiments over 3 sprints. ~150 CPU-hr laptop + ~30 GPU-hr home.**

## Decisive validation thresholds

**After Sprint 1 (Week 1):**
- 8 anchors landed across 4 areas
- Each area has 2 empirical data points
- Confidence intervals on each boundary-probe P_deflated

**After Sprint 2 (Week 2):**
- Benchmark parity (or honest gap quantification) on standard tasks
- Substrate vs LLM/MARL competitive position established
- Honest commercial positioning per area

**After Sprint 3 (Week 4):**
- All 28 experiments complete
- Substrate v3.0 ARCH-1 through ARCH-5 + 4 boundary areas all empirically grounded
- Stretch capabilities characterized
- Engineering integration well-mapped

## Strategic significance

**This is the aggressive empirical campaign that converts boundary-probe THEORIES into substrate v3.0 EMPIRICAL POSITION.**

If most anchors HARD-PASS: substrate v3.0 is empirically dominant cognitive architecture for multiple application domains.

If many FAIL: boundary-probe over-estimated; further architectural refinement needed; honest commercial positioning sharpens to validated niches only.

**Either result is decisive.** The empirical campaign converts speculation into evidence.

## Cross-references
- Boundary-probe drills: notes/research_drill_*_boundary_probe_2x_2026-06-10.md
- Consolidated priority routing: notes/research_to_exp_dev_BOUNDARY_PROBE_CONSOLIDATED_PRIORITIES_2026-06-10.md
- Each area's exp_dev_handoff: notes/exp_dev_handoff_research_*_boundary_probe_2x_2026-06-10.md

---

**Exp-Dev:** Aggressive 28-experiment batch across 4 boundary areas. Sprint 1 (8 parallel anchors) sequenced FIRST after WAVE-5 completes. Each sprint builds toward full v3.0 empirical position over 3-4 weeks.

This is the empirical campaign that determines what substrate v3.0 ACTUALLY achieves, not what we speculate about.
