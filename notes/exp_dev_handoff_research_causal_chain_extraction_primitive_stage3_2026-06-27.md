# exp_dev hand-off - research: causal-chain extraction primitive Stage 3

**Filed by:** Research (Opus 4.7-1M)
**Trigger:** 2x research drill on causal-chain extraction primitive for substrate Stage 3 / M3 conversational AI / M4 hybrid agentic-experiment loop.
**Source research note:** `d:/AI/hd-instrument/notes/research_drill_2x_causal_chain_extraction_primitive_stage3_2026-06-27.md`
**Date:** 2026-06-27
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; defer ship if paused.

Per [[feedback-no-experiment-design-in-prompts]]: research proposes the candidate cells + brain-mapping + pre-reg bands; exp_dev OWNS the experiment-design details (smoke loop, harness wiring, prereg .md, fairness gate, atomic write template). The pre-reg bands below are the MINIMUM contract; exp_dev may refine within them but may not weaken HARD_PASS thresholds or remove fairness arms.

---

## ANCHOR CANDIDATES (rank-ordered)

### TOP-1 (recommended ship): `exp_causal_chain_extraction_end_to_end_v1`

- **Anchor pointer:** new cell, name `exp_causal_chain_extraction_end_to_end_v1`. File path: `experiments/exp_causal_chain_extraction_end_to_end_v1.py`.
- **Substrate-product reading:** end-to-end causal-chain extraction from observation corpus. Composes existing chain-grade primitives (correlational_disambig role markers + CF Cell 2 v2 delta-stack interventional asymmetry + now-grounding temporal precedence + K-hop chain assembly + audit-chain depth-50) into a substrate-native three-step PC-algorithm-equivalent. CLOSES the Stage 3 "explain WHY" gap; load-bearing for M3 / M4.
- **Tier hint:** chain-grade-eligible IF discriminator survives (per [[feedback-discriminator-must-survive-scale-before-full-dispatch]]). Substrate-product MOAT: pure substrate-native causal discovery + explanation; no external symbolic engine; unique vs LLM-based "causal reasoning" which is post-hoc rationalization.
- **Why now:** five Pearl-rung primitives now chain-grade today including CF Cell 2 v2 (5.47x speedup) and correlational_disambig — the COMPILER that turns these into chain extraction is the smallest remaining step. Sibling temporal-reasoning drill provides orientation primitives. M3 + M4 both depend on this.
- **Estimated compute:** ~15min CPU full + 60s smoke. Pure numpy.
- **Pre-reg contract (minimum):**
  - HARD_PASS: chain-MRR@5 >= 0.50 AND skeleton-F1 >= 0.70 AND orientation-acc >= 0.75 AND ARM_A - ARM_B (orient adds value) >= 0.10 AND ARM_A - ARM_C (CI pruning adds value) >= 0.10 AND ARM_D (PC-on-true-corr ceiling) - ARM_A < 0.15.
  - HARD_FAIL: chain-MRR@5 < 0.25 OR skeleton-F1 < 0.40 OR ARM_A - ARM_C < 0.03 OR ARM_A - ARM_E (random) < 0.20.
  - MIDDLE_BAND: chain-MRR@5 in [0.25, 0.50] with skeleton-F1 >= 0.50.
  - CARDINALITY_OK: EXPECTED_N_UNITS = 5 arms x 3 metrics x 3 seeds = 45; HARD_FAIL_CARDINALITY_BREACH if < 40.
  - Smoke discriminator: at 4-variable DAG, 1000 obs, N=2048, 1 seed, ARM_A - ARM_C >= 0.05 chain-MRR AND ARM_A - ARM_E >= 0.25 OR smoke HARD_FAIL (do not dispatch full).
  - META_RULE_AF arms-must-differ: A=full pipeline; B=skeleton-only; C=temporal-only; D=PC-on-true-corr ceiling; E=random.
  - META_RULE_AG baseline-in-band: ARM_E random baseline ~ 1/2^edges; if not, harness bug.
  - META_RULE_AH atomic-write: metrics.json via _seed_checkpoint write_metrics atomic-rename.
  - Number tags MEASURED@ / HYPOTHESIZED@ / CITED@ throughout docstring + verdict_msg.
- **Architecture (research-proposed; exp_dev refines):**
  - Synthetic 5-variable linear-Gaussian DAG (e.g. X1->X2->X3, X1->X4->X3, X5 isolated); 5000 observations with Gaussian noise.
  - N = 4096, sparse codebook within `sparse_onset_alpha_c` envelope.
  - Substrate facts: role-bound CORRELATED_WITH triples (subject, predicate, object) from observation tuples.
  - SUB-STEP 1 (skeleton via CI test): for each variable pair (X,Y), for Z in {{}, {Z_i}, {Z_i, Z_j} | |Z|<=2}, compute residual `r_X|Z = v_X - proj_Z(v_X)`, test `|cos(W * r_X|Z, r_Y|Z)| < theta_CI`. Edge X-Y exists iff CI fails for all Z.
  - SUB-STEP 2 (orientation): use now-grounding timestamps for temporal-precedence + CF Cell 2 v2 delta-stack for interventional asymmetry. Orient toward larger interventional delta. Tie-break by temporal-precedence.
  - SUB-STEP 3 (chain assembly): K-hop traversal on inferred directed sub-W; rank by cumulative cosine.
  - Output: directed skeleton + ranked length-3 chains + chain-MRR@5.

### TOP-2 (recommended ship after TOP-1; ALSO ship if TOP-1 smoke HARD_FAIL — de-risks the load-bearing sub-piece): `exp_substrate_residual_conditional_independence_test_v1`

- **Anchor pointer:** new cell, name `exp_substrate_residual_conditional_independence_test_v1`. File path: `experiments/exp_substrate_residual_conditional_independence_test_v1.py`.
- **Substrate-product reading:** standalone substrate-native CI test using HRR-residual projection. Foundation primitive for any future causal-discovery work. Section 7 of 2026-06-07 drill, finally built.
- **Tier hint:** MM-eligible if per-test acc in [0.55, 0.75]; chain-grade if acc >= 0.75 AND ARM_C ceiling within 0.15.
- **Why now:** sub-piece de-risking for TOP-1 + independently valuable. The CI test is the load-bearing primitive most at risk in TOP-1's three-step pipeline.
- **Estimated compute:** ~10min CPU full + 60s smoke.
- **Pre-reg contract (minimum):**
  - HARD_PASS: per-test acc >= 0.75 AND skeleton-F1 (PC plug-in) >= 0.70 AND ARM_A - ARM_B (Z conditioning adds value) >= 0.15 AND ARM_C (true partial-corr ceiling) - ARM_A < 0.15.
  - HARD_FAIL: per-test acc < 0.55 OR skeleton-F1 < 0.40 OR ARM_A - ARM_B < 0.05.
  - MIDDLE_BAND: per-test acc in [0.55, 0.75].
  - CARDINALITY_OK: 4 arms x 200 DAGs x 6 var-pairs x 4 cond-sets x 3 seeds = 57600.
  - Smoke: 3-var DAG, 30 random DAGs, 500 obs, 1 seed; ARM_A - ARM_B >= 0.10 OR smoke HARD_FAIL.
  - theta_CI tuned on held-out 50 DAGs (no test contamination per BIAS-13).
  - META_RULE_AF: A=substrate-residual-projection; B=substrate-cosine-only (no Z); C=true-partial-correlation ceiling; D=random.
  - META_RULE_AG / AH per TOP-1.

### TOP-3 (queue after TOP-1 + TOP-2): `exp_direct_vs_indirect_causal_discrimination_v1`

- **Anchor pointer:** new cell, name `exp_direct_vs_indirect_causal_discrimination_v1`. File path: `experiments/exp_direct_vs_indirect_causal_discrimination_v1.py`.
- **Substrate-product reading:** discriminate direct (X->Y AND X->C->Y) from pure-indirect (X->C->Y only) causal chains via CF Cell 2 v2 blocking on intermediate variable. Pairs with TOP-1 as second-pass verification.
- **Tier hint:** MM if acc in [0.55, 0.75]; chain-grade if acc >= 0.75 AND ARM_A - ARM_B >= 0.20.
- **Why now:** "Did A really cause Y or only via C?" is load-bearing for actionable legal-AI / medical-AI explanation (Hill's specificity criterion; proximate-cause foreseeability).
- **Estimated compute:** ~5min CPU full + 40s smoke.
- **Pre-reg contract (minimum):**
  - HARD_PASS: acc >= 0.75 AND ARM_A - ARM_B (CF blocking adds value over K-hop alone) >= 0.20 AND ARM_C (oracle ceiling) - ARM_A < 0.10.
  - HARD_FAIL: acc < 0.55 OR ARM_A - ARM_B < 0.05.
  - MIDDLE_BAND: acc in [0.55, 0.75].
  - CARDINALITY_OK: 4 arms x 100 chains x 3 seeds = 1200.
  - Balanced 50/50 direct+indirect / pure-indirect; chains length-3 (length-5 in v2).
  - CF blocking uses CF Cell 2 v2 delta-stack at SAME stack_depth as production CF.
  - META_RULE_AF: A=CF-blocked discrimination; B=K-hop-cosine-only; C=oracle; D=random.
  - META_RULE_AG / AH per TOP-1.

---

## CONTEXT POINTERS (file paths only; do not summarize)

- Research drill (this hand-off's source): `d:/AI/hd-instrument/notes/research_drill_2x_causal_chain_extraction_primitive_stage3_2026-06-27.md`
- 2026-06-07 prior causal/CF drill (Mechanisms A/B/C; Section 7 CI test proposal): `d:/AI/hd-instrument/notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md`
- Sibling temporal-reasoning drill (Allen relations as orientation cue): `d:/AI/hd-instrument/notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27.md`
- Stage 3 capability matrix: `d:/AI/hd-instrument/notes/research_stage3_definition_and_chain_grade_verification_matrix_2026-06-25.md`
- CF Cell 1 (correlational_disambig HARD_PASS, role-marker validation): `d:/AI/hd-instrument/data/exp_causal_correlational_disambig_v1/metrics.json`
- CF Cell 2 v2 (delta-stack latency HARD_PASS today, 5.47x speedup): `d:/AI/hd-instrument/data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json`
- Counterfactual do-operator (existing primitive): `d:/AI/hd-instrument/data/exp_counterfactual_do_operator_v1/metrics.json`
- Bias master checklist (M-S items for fairness gate): per MEMORY.md `feedback_experiment_bias_master_checklist_USER_2026-06-24`
- Smoke disciplines: per MEMORY.md `feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26`
- Discriminator-must-survive-scale: per MEMORY.md `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`
- Cardinality-OK pre-reg field rule: per MEMORY.md `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26`
- LIVE_STATE 2026-06-27 (current in-flight): `d:/AI/hd-instrument/notes/director_LIVE_STATE_2026-06-27.md`

---

## CONTRACT

- exp_dev OWNS: smoke loop, harness wiring, prereg .md file, fairness arm implementation, atomic-write template, self-test discipline, GPU/CPU routing (CPU only for these cells), queue dispatch.
- Research OWNS: brain-mapping, pre-reg HARD bands, fairness arm design, P_deflated estimates, citations, candidate ranking. ALL ABOVE.
- exp_dev MAY: refine arm details within pre-reg bands; adjust smoke regime if smoke discriminator doesn't survive at proposed regime (per discriminator-survives-scale); add additional sanity-check arms; tune theta_CI on held-out DAGs in TOP-2.
- exp_dev MUST NOT: weaken HARD_PASS thresholds; remove fairness arms (especially ARM_C ceiling control in TOP-1 + TOP-2; especially ARM_D random in TOP-3); skip CARDINALITY_OK declaration; skip META_RULE_AH atomic-write; allow theta_CI to be tuned on the test set.
- exp_dev MUST: predispatch_check before ship to confirm anchor not duplicating recent landings; post-ship REMOTE VERIFY per [[feedback-fix26-predispatch-verify-the-referent-gate]]; per-arm metrics re-read per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]] before classifying tier; suspect any arm at 1.000 per [[feedback-suspect-1.000-results]].

---

## AUTONOMY DECLARATION

Research autonomously decided: which fields to drill (brain causal-cognition + Pearl/Halpern formal causation + Lagnado/Sloman cog-sci + ARACNe/Granger bio + Hart-Honore legal + Hill epidemiology + Ohno root-cause + Wright path analysis); which candidates rank-1/2/3; which P_deflated values (per [[feedback-lit-scan-calibration-penalty]] novel-synthesis cap + asymmetric brain-existence-proof); which fairness arms; which HARD bands. exp_dev autonomously decides: when to dispatch (subject to pause flag + Director priority); implementation details within pre-reg bands; smoke regime if survival check fails; theta_CI tuning protocol within held-out-only constraint.

---

(End of exp_dev hand-off - research: causal-chain extraction primitive Stage 3.)
