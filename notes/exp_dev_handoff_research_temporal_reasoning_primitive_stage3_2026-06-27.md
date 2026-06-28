# exp_dev hand-off — research: temporal-reasoning primitive Stage 3

**Filed by:** Research (Opus 4.7-1M)
**Trigger:** USER 2x research drill on temporal-reasoning primitive for Stage 3 M3 conversational AI.
**Source research note:** `d:/AI/hd-instrument/notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27.md`
**Date:** 2026-06-27
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; defer ship if paused.

Per [[feedback-no-experiment-design-in-prompts]]: research proposes the candidate cells + brain-mapping + pre-reg bands; exp_dev OWNS the experiment-design details (smoke loop, harness wiring, prereg .md, fairness gate, atomic write template). The pre-reg bands below are the MINIMUM contract; exp_dev may refine within them but may not weaken HARD_PASS thresholds or remove fairness arms.

---

## ANCHOR CANDIDATES (rank-ordered)

### TOP-1 (recommended ship): `exp_time_cell_population_allen_classifier_v1`

- **Anchor pointer:** new cell, name `exp_time_cell_population_allen_classifier_v1`. File path: `experiments/exp_time_cell_population_allen_classifier_v1.py`.
- **Substrate-product reading:** brain-grounded population-code primitive for Allen interval-relation classification, REPLACING the by-construction `exp_temporal_interval_allen_cpu_v1` (which uses substrate only for endpoint storage + Python for relation logic). Closes a load-bearing Stage 3 gap for M3 narrative coherence + counterfactual + ToM.
- **Tier hint:** chain-grade-eligible IF discriminator survives (per [[feedback-discriminator-must-survive-scale-before-full-dispatch]]). Substrate-product MOAT: brain-grounded time-cell population code is unique vs LLM token-position encoding.
- **Why now:** today's BTSP HARD_FAIL surfaced that substrate ALREADY has order-binding via additive Hebbian; the symmetric gap is RELATION-CLASSIFICATION-FROM-POPULATION-GEOMETRY, which is currently faked by Python in v1 cell. Five concurrent Stage-3 chain-grade landings today (depth-5, parietal, task_vector, ToM smoke, counterfactual) all benefit downstream from a real temporal-relation primitive.
- **Estimated compute:** ~10min CPU full + 30s smoke. Pure numpy.
- **Pre-reg contract (minimum):**
  - HARD_PASS: macro-F1 >= 0.85 on 13-way Allen-relation classification AND substrate-features-arm beats cosine-only-arm by >=0.10 AND beats raw-endpoints-arm by >=0.10 AND no class < 0.50.
  - HARD_FAIL: macro-F1 < 0.60 OR substrate-features minus raw-endpoints < 0.05 OR any class < 0.20.
  - MIDDLE_BAND: macro-F1 in [0.60, 0.85].
  - CARDINALITY_OK: EXPECTED_N_UNITS = 4 arms × 13 classes × 3 seeds = 156; HARD_FAIL_CARDINALITY_BREACH if < 130.
  - Smoke discriminator: at T=32 n=500 1 seed, ARM_A - ARM_B >= 0.05 AND ARM_A - ARM_D >= 0.30 OR smoke HARD_FAIL (do not dispatch full).
  - META_RULE_AF arms-must-differ: arms A/B/C/D structurally distinct; document the difference in cell docstring.
  - META_RULE_AG baseline-in-band: ARM_D random baseline ~1/13 = 0.077 ± 0.03; if not, harness bug.
  - META_RULE_AH atomic-write: final metrics.json written via _seed_checkpoint write_metrics atomic-rename.
  - Number tags MEASURED@ / HYPOTHESIZED@ / CITED@ throughout the cell docstring + verdict_msg.
- **Architecture (research-proposed; exp_dev refines):**
  - T = 128 ticks (vs prior 12); n_pairs = 5000 full / 500 smoke.
  - Interval bundle: `interval_hd[s,e] = sum_{t=s}^{e} tick_t / sqrt(e-s+1)` where `tick_t = cphasor(T, N=8192, seed)`.
  - Features f1..f5 derived from substrate operations ONLY (no Python access to s,e):
    - f1: `cos(A_hd, B_hd)` overlap proxy.
    - f2: `sign(centroid(A) - centroid(B))` order proxy via cleanup + weighted-average.
    - f3: `||A_hd|| / ||B_hd||` duration ratio.
    - f4: disjointness via cleanup-of-product against tick book.
    - f5: endpoint equality via cleanup match on first/last tick.
  - Allen classifier: 13-way logistic regression on (f1..f5); 4000 train / 1000 test split per seed.
  - Arms: A=all features, B=cosine-only, C=raw-endpoints (privileged BY-CONSTRUCTION control), D=shuffle baseline.

### TOP-2 (recommended ship after TOP-1): `exp_weber_fraction_duration_discrimination_v1`

- **Anchor pointer:** new cell, name `exp_weber_fraction_duration_discrimination_v1`. File path: `experiments/exp_weber_fraction_duration_discrimination_v1.py`.
- **Substrate-product reading:** brain-grounded Weber-fraction duration estimation primitive. Hooks substrate to scalar-timing literature (Coull-Cheng-Meck 2011 / Ivry-Spencer 2004); cross-validates TOP-1's f3 feature.
- **Tier hint:** MM-eligible IF Weber-fraction W lands in brain range [0.05, 0.40]; chain-grade only if W lands tight (< 0.20) AND replicates across 3 seeds.
- **Why now:** required for "how long did Y take?" Stage 3 capability; complements TOP-1 (TOP-1 does relation, TOP-2 does magnitude).
- **Estimated compute:** ~5min CPU full + 30s smoke.
- **Pre-reg contract (minimum):**
  - HARD_PASS: W in [0.05, 0.40] at all T_A AND beats random baseline by >=0.20 at 1.1 T_A ratio.
  - HARD_FAIL: no arm yields W < 0.60 at any T_A OR all arms degenerate to random.
  - MIDDLE_BAND: W in [0.40, 0.60].
  - CARDINALITY_OK: EXPECTED_N_UNITS = 4 arms × 4 T_A × 5 ratios × 100 trials × 3 seeds = 24000.
  - META_RULE_AF, AG, AH per TOP-1.

### TOP-3 (queue after TOP-1 + TOP-2): `exp_temporal_trajectory_next_event_predictor_v1`

- **Anchor pointer:** new cell, name `exp_temporal_trajectory_next_event_predictor_v1`. File path: `experiments/exp_temporal_trajectory_next_event_predictor_v1.py`.
- **Substrate-product reading:** next-event prediction + preceding-event retrieval over substrate-stored event-time tape. Brain-grounded via TCM (Howard 2018) + Eichenbaum 2014 time-cell trajectory.
- **Tier hint:** MM if NEXT-EVENT acc > 0.50 AND beats bigram by >=0.10; chain-grade only if PRECEDING-EVENT also lands >= 0.70.
- **Why now:** "what comes next" + "what happened before" are the narrative-coherence questions for Stage 3 conversational coherence; pairs with TOP-1's relation classifier.
- **Estimated compute:** ~8min CPU full + 20s smoke.
- **Pre-reg contract (minimum):**
  - HARD_PASS: NEXT-EVENT >= 0.50 AND beats bigram by >=0.10 AND PRECEDING-EVENT >= 0.70.
  - HARD_FAIL: NEXT-EVENT < 0.20 OR substrate minus bigram < 0.02.
  - MIDDLE_BAND: NEXT-EVENT in [0.20, 0.50].
  - CARDINALITY_OK: EXPECTED_N_UNITS = 4 arms × 3 tasks × 50 sequences × 3 seeds = 1800.
  - Bigram baseline computed from training-set statistics (no privileged access).
  - META_RULE_AF, AG, AH per TOP-1.

---

## CONTEXT POINTERS (file paths only; do not summarize)

- Research drill (this hand-off's source): `d:/AI/hd-instrument/notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27.md`
- Substrate parameter taxonomy 3x drill: `d:/AI/hd-instrument/notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md`
- BTSP HARD_FAIL synthesis (today): `d:/AI/hd-instrument/notes/exp_dev_to_research_BTSP_SEQUENCE_LEARNING_v1_v2_BOTH_HARD_FAIL_substrate_already_has_capability_2026-06-27.md`
- Existing Allen v1 cell (BY-CONSTRUCTION; this drill REPLACES it): `d:/AI/hd-instrument/experiments/exp_temporal_interval_allen_cpu_v1.py`
- Allen v1 metrics: `d:/AI/hd-instrument/data/exp_temporal_interval_allen_cpu_v1/metrics.json`
- LTL v1 metrics (suspected similar by-construction risk; audit before reuse): `d:/AI/hd-instrument/data/exp_lap3_11_temporal_ltl_cpu_v1/metrics.json`
- now-grounding v1 metrics (LOAD-BEARING; real discriminator): `d:/AI/hd-instrument/data/exp_now1_temporal_grounding_cpu_v1/metrics.json`
- temporal-policy v1 metrics: `d:/AI/hd-instrument/data/exp_integ_temporal_policy_cpu_v1/metrics.json`
- Additive Hebbian sequence-binding cliff sweep (additive saturates): `d:/AI/hd-instrument/data/exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1_smoke/metrics.json`
- Bias master checklist (M-S items for fairness gate): `feedback_experiment_bias_master_checklist_USER_2026-06-24` per MEMORY.md
- Smoke disciplines: `feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26`
- Discriminator-must-survive-scale: `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`
- Cardinality-OK pre-reg field rule: `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26`

---

## CONTRACT

- exp_dev OWNS: smoke loop, harness wiring, prereg .md file, fairness arm implementation, atomic-write template, self-test discipline, GPU/CPU routing, queue dispatch.
- Research OWNS: brain-mapping, pre-reg HARD bands, fairness arm design, P_deflated estimates, citations, candidate ranking. ALL ABOVE.
- exp_dev MAY: refine arm details within pre-reg bands; adjust smoke regime if smoke discriminator doesn't survive at proposed regime (per discriminator-survives-scale rule); add additional sanity-check arms.
- exp_dev MUST NOT: weaken HARD_PASS thresholds; remove fairness arms (especially raw-endpoints control in TOP-1); skip CARDINALITY_OK declaration; skip META_RULE_AH atomic-write.
- exp_dev MUST: predispatch_check before ship to confirm anchor not duplicating recent landings; post-ship REMOTE VERIFY per [[feedback-fix26-predispatch-verify-the-referent-gate]]; per-arm metrics re-read per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]] before classifying tier.

---

## AUTONOMY DECLARATION

Research autonomously decided: which fields to drill (brain time-cells + Weber psychophysics + TCM + Allen pure-math + legal/crystal/Petri cross-domain probes); which candidates rank-1/2/3; which P_deflated values (per [[feedback-lit-scan-calibration-penalty]] cap + asymmetric brain-existence-proof); which fairness arms; which HARD bands. exp_dev autonomously decides: when to dispatch (subject to pause flag + Director priority); implementation details within pre-reg bands; smoke regime if survival check fails.

---

(End of exp_dev hand-off — research: temporal-reasoning primitive Stage 3.)
