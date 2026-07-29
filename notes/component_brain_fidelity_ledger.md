# COMPONENT BRAIN-FIDELITY LEDGER — nail each component brain-faithful, then assemble (living doc)

**USER DIRECTIVE (2026-07-28, full-auto authorized):** stop task-chasing; go component-by-component, make EACH brain-faithful, judge each on the BRAIN's metric (NOT downstream task-win), THEN assemble. Root cause of repeated failures = we let a downstream task-metric judge components whose brain-faithfulness we never verified first ("brain-faithful LOSING = presumed impl-bug until proven structural" — we ignored this). This ledger is the tracking backbone for the FORMALIZE method [[project_formalize_deepbrain_analysis_then_comparison_accurate_duplication_method_2026-07-24]] applied SYSTEMATICALLY.

## THE METHOD (per component, in order)
1. **Deep-brain-analysis** — biology-first map of how the brain does this component (the drills do this).
2. **Comparison** — our impl vs brain, scored on SHAPE + POSITION + METRIC (not just "right function").
3. **Name the gap** — the specific fidelity deficit.
4. **Accurate-duplication** — build a brain-accurate, can-fail cell **judged on the BRAIN's metric** (below), not on whether it wins a downstream task.
5. **VET + iterate** — replicate across seeds; a brain-faithful build that loses the BRAIN metric is a real fail; one that loses only a downstream task but passes the brain metric is KEPT (composition problem, not component problem).
6. **Integration checkpoint** — faithful parts don't auto-compose; each component's fidelity spec includes its interface/handoff; assembly is its own phase with its own criteria.

**JUDGING SHIFT (the core change):** each component has a BRAIN METRIC = how closely it reproduces the brain's mechanism/behavior FOR THAT COMPONENT. That metric gates keep/kill — the downstream held-out-NEW task is only the FINAL assembly metric, not the per-component gate.

**Fidelity = algorithmic-level (Marr L2/L3):** right function + shape + role + metric. NOT neuron-level implementation. **Lurking alternative (hold live):** experience-poverty — if the bottleneck is data/experience richness not mechanism, component-fidelity won't save us; mechanism is what we control, but don't over-attribute every failure to fidelity.

---

## THE LEDGER (status: FAITHFUL / IMPROVING / PARTIAL / UNFAITHFUL / ABSENT)

| # | Component | Brain mechanism | Our impl | Gap (shape/pos/metric) | BRAIN METRIC (the per-component gate) | Status | FORMALIZE next |
|---|---|---|---|---|---|---|---|
| 1 | **Encoder OBJECTIVE** | Forward hierarchical predictive coding (Rao-Ballard/Friston); prediction-error is the learning signal | MLM bidirectional cloze | Wrong learning signal: bidirectional reconstruction, not forward-temporal prediction | Does training produce forward next-input predictivity that IMPROVES with depth/context (PE-driven), vs a static cloze fit? | UNFAITHFUL (but +0.44 forward structure already latent in MLM reps) | **Drill #3** resolves: real untried faithful lever (forward-temporal PC term) vs defer (objective not the bottleneck) |
| 2 | **Encoder ARCHITECTURE** | Sparse, recurrent, columnar cortex; mixed selectivity (Rigotti/Fusi) | Dense transformer (attention loosely brain-like) | Dense not sparse; no recurrence; no columns | Mixed-selectivity + sparse-coding statistics vs cortical population | PARTIAL | Deprioritized (deliberate; mechanism≠task-analog) — revisit only if reps plateau after readout/maintenance |
| 3 | **REPRESENTATION geometry** | Graded distributed semantic space; generalizes to novel | Learned from-scratch code (29591), held-out-NEW generalizes | Modest band (0.56-0.63); under-decoded | Held-out-NEW generalization + graded neighborhood structure | PARTIAL-FAITHFUL (banked) | It's READOUT-limited -> row 4; representation itself may be adequate |
| 4 | **READOUT / decoding** | Learned, plastic, NONLINEAR + attentional decoders on population codes | WAS fixed cosine-NN -> NOW learned bilinear/probe | Linear where brain is nonlinear+attentional; mean-pool order-blind | Calibration-first: known reader passes; role-GENERAL (not position) order decoding | IMPROVING (was UNFAITHFUL; learned-readout fix +0.038, cross-boundary +0.21 VET-pending) | **Drill #1** -> structure-preserving/attentional readout; gate = cross-boundary VET |
| 5 | **COMPREHENSION / situation-model construction** | Kintsch construction-integration; Zwaan event-indexing; role-general binding (Frankland-Greene) | Bag-of-contextualized-tokens (textbase); latent signal present | No explicit integrated, updatable situation model | Cross-boundary entity/state tracking on calibration-first instrument (known reader passes), role-general | UNFAITHFUL-as-mechanism; latent-capability VET-PENDING | Cross-boundary VET decides: readout (drill #1) if signal present, else maintenance (drill #2) |
| 6 | **WORKING MEMORY / active maintenance** | Persistent-activity / attractor / activity-silent WM (Wang, Stokes, Mongillo); PE-gated incremental update | NONE (flat 128-token window; static decode of a frozen rep) | ABSENT — no persistent state, no cross-window memory, no update mechanism | Multi-boundary incremental update; updating-cost at discontinuities; no forgetting of earlier entities | **ABSENT (the worst gap)** | **Drill #2** -> reuse DG episodic store as cross-window memory (gap-map item 5) |
| 7 | **GROUNDING** | Sensorimotor for CONCRETE (Barsalou); relational/propositional for ABSTRACT (via semantic net) | Sensorimotor (Lancaster) applied to ALL, incl. abstract science | Mis-applied: sensorimotor to abstract concepts | Concrete -> sensorimotor transfer; abstract -> relational-from-graph transfer | PARTIAL / mis-applied (sensorimotor SHELVED, HARD_FAIL) | Relational grounding for abstract concepts (on-deck; revive when reps/readout settle) |
| 8 | **REASONING** | CA3 attractor / pattern-completion; additive multi-constraint satisfaction | Verification-by-derivation reasoner (hdlab/reasoner.py) | Coverage-bound (only cleanly-derivable) | Constraint-satisfaction resolution scaling with #constraints brought to bear | FAITHFUL (banked 29537-70) | Coverage grows from better reps/readout; no component rebuild needed |
| 9 | **CONSOLIDATION / sleep** | Iterated interleaved SWR replay (CLS); Tse/Morris schema-gating; PE/surprise-budgeted replay | Single averaging op per cycle (mean/Kalman/retrieve-not-avg) | Wrong op-CLASS: once vs iterated; average-all vs selective-replay; ungated vs schema-gated | Interleaved OLD-vs-NEW retention (integrate new WITHOUT catastrophic forgetting) — averaging can't be tested on it | UNFAITHFUL; faithful version (cls_discrete_budget, HARD_PASS synthetic) ISLANDED | **Drill #4** -> wire the certified replay engine + surprise-budget + schema-gate (on-deck) |
| 10 | **LEARNING LOOP (read->extract->consolidate)** | CLS continual learning; hippocampal fast-write + cortical slow-consolidate | Loop plumbing works (sleep fires, controls behave); comprehension-EXTRACT unsolved | The "what to extract from reading" step | Sustained, comprehension-SPECIFIC gain from novel reading (vs scrambled/wrong-concept controls) | PARTIAL (CLS shape right; extract unsolved) | Follows comprehension (rows 5/6); loop v1-v6 all negative until comprehension lands |
| 11 | **FOUNDATION / knowledge** | Distributed semantic memory | Symbolic typed graph (1.24M edges), used as SEED/teacher | Symbolic-supplied, not distributed-native | Coverage + relational correctness as a teacher/target signal | FAITHFUL-for-role (supplied seed; learn rep downstream) | Adequate; no rebuild |

---

## EXECUTION SEQUENCE (by load-bearingness × cost)
1. **READOUT + COMPREHENSION (rows 4/5)** — LIVE frontier; cross-boundary VET in flight; cheap (learned head on frozen reps). Drill #1 designs the brain-faithful structure-preserving readout. **FIRST.**
2. **WORKING MEMORY / maintenance (row 6)** — the worst gap (ABSENT); the deeper fix once decoding is faithful. Drill #2. **SECOND.**
3. **OBJECTIVE (row 1)** — drill #3 gives a clear build-or-defer fork (don't burn GPU on another unfaithful objective; only build if there's a genuinely faithful untried forward-PC lever with headroom).
4. **CONSOLIDATION (row 9)** — drill #4 wiring design; on-deck (not current bottleneck).
5. **GROUNDING-abstract (row 7)** — on-deck; relational grounding when reps/readout settle.
6. **ASSEMBLY** — integration checkpoints as faithful components land; the held-out-NEW + conversational goal is the FINAL metric.

## STATUS TALLY (honest): FAITHFUL 2 (reasoning, foundation-for-role) | IMPROVING 1 (readout) | PARTIAL 4 (architecture, representation, grounding, loop) | UNFAITHFUL 2 (objective, consolidation) | ABSENT 1 (working memory). => most of the pipeline is NOT yet brain-faithful — the USER's assessment is correct.
