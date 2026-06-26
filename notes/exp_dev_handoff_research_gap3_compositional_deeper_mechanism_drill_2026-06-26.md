# exp_dev hand-off -- research: Gap 3 deeper mechanism drill

filed-by: research (Opus 4.7 1M)
date: 2026-06-26
trigger: USER deep drill on Gap 3 after 2 cells partial/HARD_FAIL; non-bundle mechanism classes identified
research note: d:/AI/hd-instrument/notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md

## Pause state

Check `data/orchestrator_paused.flag` before dispatch. If paused, queue these in `data/exp_dev_pending_dispatch.json` per [[feedback-obey-user-pause-explicitly]].

Per [[feedback-no-experiment-design-in-prompts]] -- research file CONTRACTS the anchors below as candidate cells; exp_dev does the actual cell-authoring (smoke + Fix #17 wall-time measurement + dispatch + REMOTE VERIFY).

## Anchor candidates (rank-ordered)

### ANCHOR 1 (rank-1; dispatch FIRST)

- anchor pointer: `gap3_modern_hopfield_prototype_attractor_v1`
- substrate-product reading: replaces linear-bundle prototype (Cell 1 HRR ceiling at 0.47) with non-linear softmax-beta-weighted attractor compression (Modern Hopfield / Krotov 2016 / Ramsauer 2020). 3-line code change to existing hdlab/iterative_attractor.py.
- tier hint: chain-grade-eligible if HARD_PASS; promotes Gap 3 cap_map from RED to GREEN
- why-now: prior Cell 1 ARM_FEATURE_BASED_SCHEMA +0.10 lift IS the signal schema-formation works structurally; HRR-bundle crosstalk caps at ~0.5; Modern-Hopfield non-linear basin-sharpening structurally addresses that ceiling
- prior P_solve_deflated: 0.45 (raw lit 0.70; -0.20 calibration; -0.05 prior modern_hopfield_xl collapse per Fix #28 memory)
- compute: 1.5 hr CPU at N=8192; 4 arms (BASELINE / HRR_BUNDLE_PROTOTYPE / MODERN_HOPFIELD_PROTOTYPE / MODERN_HOPFIELD_CONTINUOUS); 3 seeds [11, 13, 19]
- pre-reg bands:
  - HARD_PASS: MODERN_HOPFIELD_* >= 0.65 AND >= 1.35x HRR_BUNDLE_PROTOTYPE
  - HARD_FAIL: MODERN_HOPFIELD_* within 0.05 of HRR_BUNDLE_PROTOTYPE
  - MIDDLE_BAND [0.50, 0.65]: queue beta-sweep follow-up
- cross-cell rail: ARM_HRR_BUNDLE_PROTOTYPE must replicate Cell 1 ARM_FEATURE 0.47 within 0.03; if drift, abort + re-audit harness per Fix #28
- substrate-mine FIRST: search atoms for `modern_hopfield`, `dense_associative`, `krotov`; understand WHY prior modern_hopfield_xl collapsed (likely beta over-sharpening); avoid same beta region in sweep
- discriminator gate: 3-arm spread BASELINE / BUNDLE / HOPFIELD; if all converge within 5% the test is non-discriminating per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]] -- redesign

### ANCHOR 2 (rank-2; BUNDLED with Gap 4 TWO_TIER_GENERATIONAL hand-off)

- anchor pointer: `cls_replay_two_tier_unified_v1`
- substrate-product reading: hippocampus-cortex two-tier architecture closes BOTH Gap 4 long-term retention AND Gap 3 compositional generalization in one cell. Marquee biologically-grounded substrate-product story.
- tier hint: chain-grade-eligible if BOTH endpoints HARD_PASS; promotes BOTH Gap 3 AND Gap 4 cap_map rows
- why-now: composes the NREM drift_reduction proven_bound from last night with Gap 3 schema-extraction need; same architectural change (W_episodic + W_slow) serves both purposes
- prior P_solve_deflated: 0.40 (joint endpoint)
- compute: 4-5 hr CPU at N=8192; 4 arms (BASELINE / TWO_TIER_HEAVY_HITTER / CLS_BCM_HEBBIAN / TWO_TIER+CLS_BOTH); two endpoints per arm (retention + schema_gen); 3 seeds
- pre-reg bands:
  - HARD_PASS: Gap 3 heldout >= 0.55 AND Gap 4 retention >= 0.70 at cycle 5000. BOTH must pass.
  - HARD_FAIL: Either endpoint <= 0.30 -> mechanism does not generalize; refile as separate cells
  - MIDDLE_BAND: one endpoint passes, other partial -> queue mechanism-specific refinement
- cross-cell rail: BASELINE arm must replicate single-tier baselines on BOTH endpoints
- substrate-mine FIRST: existing TWO_TIER_GENERATIONAL hand-off from notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md provides design starting point
- dispatch order: ONLY after ANCHOR 1 verdict; do not waste compute if ANCHOR 1 HARD_PASSes (Gap 3 closed cheaper)

### ANCHOR 3 (rank-3; backup if 1 + 2 both HARD_FAIL)

- anchor pointer: `gap3_predictive_coding_hierarchy_v1`
- substrate-product reading: adds calibrated abstention via residual-driven refuse-gate; substrate refuses to generalize when prediction-error residual exceeds threshold. First auditable AI memory subsystem with explicit "don't extrapolate" signal.
- tier hint: chain-grade-eligible if HARD_PASS; specifically adds refuse-gate substrate-product value beyond Gap 3 closure
- why-now: substrate already has predictive_coding.py + refuse_gate.py; missing piece is hierarchical (L2 category-level) layer
- prior P_solve_deflated: 0.35 (raw lit 0.55; -0.20 calibration; novel-synthesis cap honored)
- compute: 2-3 hr CPU at N=8192; 3 arms (BASELINE / FLAT_PC / HIERARCHICAL_PC); 3 seeds
- pre-reg bands:
  - HARD_PASS: heldout-on-accept >= 0.70 AND accept-rate >= 0.60 AND ECE <= 0.05
  - HARD_FAIL: HIERARCHICAL_PC within 0.05 of FLAT_PC
  - MIDDLE_BAND: queue threshold-sweep for refuse-gate calibration
- substrate-mine FIRST: existing hdlab/predictive_coding.py and hdlab/refuse_gate.py
- dispatch order: AFTER ANCHOR 1 AND ANCHOR 2 verdicts

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md (research note with full mechanism analysis)
- d:/AI/hd-instrument/notes/research_gap3_compositional_5x_drill_2026-06-26.md (prior breadth scan; 18 candidates)
- d:/AI/hd-instrument/notes/research_gap4_continual_5x_drill_2026-06-26.md (NREM proven_bound; TWO_TIER architecture pre-design)
- d:/AI/hd-instrument/notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md (Gap 4 hand-off; bundle target for ANCHOR 2)
- d:/AI/hd-instrument/notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md (cone-preserving mechanism signature)
- d:/AI/hd-instrument/data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json (Cell 1 empirical anchor; MIDDLE_BAND)
- d:/AI/hd-instrument/data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json (Cell 2 empirical anchor; HARD_FAIL_CONFOUND)
- d:/AI/hd-instrument/hdlab/iterative_attractor.py (existing primitive; ANCHOR 1 modifies)
- d:/AI/hd-instrument/hdlab/continual.py (existing replay_cycle; ANCHOR 2 uses)
- d:/AI/hd-instrument/hdlab/predictive_coding.py (existing primitive; ANCHOR 3 hierarchical-extends)
- d:/AI/hd-instrument/hdlab/refuse_gate.py (existing primitive; ANCHOR 3 pairs with residual)

## Contract

Per [[feedback-no-experiment-design-in-prompts]]: research file proposes ANCHOR contracts (mechanism + discriminator + bands + cross-cell rails). exp_dev does cell-authoring (smoke + Fix #17 measurement + dispatch + REMOTE VERIFY). Cert-classification routes to Skunkworks per Fix #28 / [[feedback-fix28-recurring-skunkworks-correct-more-than-director]].

Per [[feedback-fix26-predispatch-verify-the-referent-gate]]: run `tools/predispatch_check.py <anchor>` before each anchor dispatch.

Per [[feedback-use-peek-arm-metrics-before-framing]]: post-verdict, use tools/peek_arm_metrics.py before cross-arm narrative.

## Autonomy declaration

exp_dev autonomy:
- Cell author: defer to exp_dev's discretion on file structure, smoke design, seed selection, exact code path
- Substrate-mine FIRST per [[feedback-substrate-mine-capacity-before-extrapolating]] before authoring
- All four bias-checklists (12+8 categories per [[feedback-experiment-bias-master-checklist]]) apply at cell-author stage
- Methodology-confound suspicion: if BASELINE drifts above 0.45 in ANCHOR 1, abort and re-audit harness
- Cross-cell convergence claims MUST verify per-arm metrics per Fix #28; do not infer from verdict_msg text

Research autonomy:
- HARD_FAIL of ANCHOR 1 + ANCHOR 2 -> Research re-drills; pivot from "mechanism missing" framing to "data-coverage / capacity-sweep" framing per Section 5 of research note
- MIDDLE_BAND of any ANCHOR -> Research drills the beta / cardinality / instances-per-category sweep design
- Per [[feedback-route-negatives-to-research]]: every HARD_FAIL routes to Research same-cycle for revival-angle drill
