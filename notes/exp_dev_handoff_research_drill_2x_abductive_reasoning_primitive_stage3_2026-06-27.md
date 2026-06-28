# exp_dev hand-off — research: 2x drill abductive reasoning primitive (Stage 3)

**Filed-by:** research (Opus 4.7-1M)
**Date:** 2026-06-27
**Trigger:** USER 2x research drill request for Stage 3 abductive primitive
**Pause state:** check `data/orchestrator_paused.flag` before dispatch
**Source research note:** `notes/research_drill_2x_abductive_reasoning_primitive_stage3_2026-06-27.md`

Per [[feedback-no-experiment-design-in-prompts]]: this handoff provides ANCHOR POINTERS and brain-grounded mappings only. exp_dev OWNS cell design (arm structure, hardening, smoke harness, pre-reg bands within the brackets specified here).

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor #1 (TOP-REC; tier hint = chain-grade-eligible if HP)
- **Anchor pointer:** `abductive_bank_vmpfc_valuation_v1`
- **Substrate-product reading:** ranked candidate-hypothesis output with refuse-fire on ambiguity — directly enables M3 conversational AI "I have one clear answer" vs "I need clarification" distinction
- **P_deflated:** 0.42 (HARD_PASS likelihood)
- **Tier hint:** chain-grade-eligible if all HP conditions met (composes 4 prior chain-grade atoms + vmPFC valuation + Occam prior)
- **Why-now:** Stage 3 USER pivot active 2026-06-26; schema_driven_proof_step_inference_v1 prereg filed 2026-06-27 wants this primitive as a composing dependency; substrate has all parts (bayes_net HP, abduction_kernel HP, vmPFC selftest OK, refuse_gate primitive)
- **Brain mapping pointer:** Hippocampus generates candidates → vmPFC valuates (CITED@PMC5862740) → posterior-entropy refuse-gate (extends `hdlab/refuse_gate.py`)

### Anchor #2 (P_deflated=0.35)
- **Anchor pointer:** `abductive_diagnosis_medical_QMR_v1`
- **Substrate-product reading:** validates abductive primitive on canonical medical-diagnosis abduction task (CITED@Shwe-Heckerman QMR/INTERNIST); ranked diagnoses + unifying-vs-differential flag
- **Tier hint:** MEASURED_MECHANISM if HP (domain validation, not chain-grade by itself)
- **Why-now:** external-validation arm for #1; queue ONLY after #1 lands HP — provides P(externally-valid) evidence

### Anchor #3 (P_deflated=0.28)
- **Anchor pointer:** `abductive_phylogenetic_ancestral_reconstruction_v1`
- **Substrate-product reading:** cross-domain abduction stress-test (Felsenstein ML on substrate multi-hop)
- **Tier hint:** MEASURED_MECHANISM stretch-only
- **Why-now:** capacity-free stretch only; distant from M3 conversational goal but high cross-domain validation P_HP if substrate composes

---

## CONTEXT POINTERS (file paths, NOT summaries — exp_dev reads originals)

**Prior substrate atoms to inspect before design (CRITICAL — META_RULE_NO_HALLUCINATED_NUMBERS):**
- `data/exp_lap8_bayesian_fhrr_cpu_v1/metrics.json` — FHRR amp-Bayes HP, n=33 (Monty Hall / medical / spam)
- `data/exp_comp21_bayesian_at_l3_cpu_v1/metrics.json` — composite-hypothesis Bayes HP, L3=1.000
- `data/exp_stretch3_4_bayes_net_cpu_v1/metrics.json` — Bayes-net inference HP, posterior-match 0.987
- `data/exp_stretch4_1_bayes_net_learning_cpu_v1/metrics.json` — Bayes-net learning HP, struct-precision 0.95
- `data/exp_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1/metrics.json` — abduction kernel HP
- `data/exp_substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1/metrics.json` — confound-break methodology HP
- `data/exp_counterfactual_regret_comparison_vmpfc_v1/metrics.json` — vmPFC valuation SELFTEST_OK R²=0.975 (prototype for #1's vmPFC head)
- `data/exp_substrate_aaa1_bayesian_tier_overlay_cpu_v1/metrics.json` — **CAUTIONARY:** Bayesian HURT vs hard MAP (delta -0.025) on tier-prediction; informs HARD_PASS lift-over-hard-MAP gate

**Substrate code primitives to compose:**
- `hdlab/bayesian_inference.py` (318 lines): `bayes_update`, `bayes_update_categorical`, `map_estimate`, `EMMixture`
- `hdlab/refuse_gate.py` (130 lines): EXTEND with `refuse_on_posterior_entropy` mode
- `hdlab/multi_hop.py` (361 lines): for hypothesis-bank traversal
- `hdlab/binding.py`: HRR bind/unbind for observation-hypothesis pairing
- `hdlab/bundling.py`: weighted superposition for Bayesian model averaging

**Disciplines to enforce (load-bearing):**
- META_RULE_AA: BASELINE arms must be NON-abductive (BASELINE_MAJORITY_VOTE: closest-hypothesis-by-count; BASELINE_NEAREST_OBSERVATION: hypothesis nearest observation centroid; both NO likelihood, NO prior)
- META_RULE_AC/AE/AF/AG/AH per standard exp_dev discipline
- META_RULE_Q: any arm at 1.000 on n≥100 → halt + re-partition (likely leak)
- META_RULE_S: HARD_PASS on top-3 not top-1 (abduction is genuinely multi-valued)
- CARDINALITY_OK: declare expected_n_units, HARD_FAIL_CARDINALITY_BREACH
- DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full V_REL, NOT smoke at smoke-N (per USER 2026-06-26)
- compute-formulas-in-code: posterior entropy + Bayes-factor formulas inline, not in markdown
- BIAS-MASTER-CHECKLIST per `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` — especially bias-Q (suspect 1.000) and bias-S (band-calibration regime checks)

**Related prereg already filed (composes with):**
- `preregs/2026-06-27_schema_driven_proof_step_inference_v1.md` — schema-bank is structural sibling to hypothesis-bank; Tse-Morris frame applies
- `preregs/2026-06-27_edge_importance_v5_CFU_counterfactual_utility_v1.md` — counterfactual utility primitive

**Brain-mapping citations (verified web 2026-06-27):**
- Friston active inference (arxiv 2402.14460): VFE minimization IS abduction
- Yuille-Kersten 2006 TICS: analysis-by-synthesis is Peircean
- Hohwy 2013 Predictive Mind: hierarchical prediction-error = abduction
- vmPFC valuation hypothesis (PMC3707083; PMC5862740)
- MacKay Bayes-factor Occam (Information Theory ch.28)
- Gopnik causal blickets (PubMed 17087545); 2024 review WIREs Cog Sci 1678

---

## PRE-REG BAND BRACKETS (research-suggested; exp_dev finalizes)

For Anchor #1 `abductive_bank_vmpfc_valuation_v1`:
- **HARD_PASS:** top-1 ≥ 0.85 AND Spearman ρ ≥ 0.80 AND lift over BASELINE_MAJORITY_VOTE ≥ +0.20 AND lift over BASELINE_NEAREST_OBSERVATION ≥ +0.15 AND Occam lift ≥ +0.10 AND refuse-rate on uniform ≥ 0.80 / on concentrated ≤ 0.10 AND vmPFC R² ≥ 0.80 AND cv < 0.10
- **MIDDLE_BAND:** top-1 in [0.50, 0.85) OR lift in [0.05, 0.20) OR Occam lift in [0.02, 0.10)
- **HARD_FAIL:** top-1 < 0.50 OR lift < +0.05 OR Occam lift < +0.02 OR refuse uncalibrated OR cardinality breach

Suggested test bank: 10 candidate hypotheses with known ground-truth posterior {0.6, 0.2, 0.1, 0.05, 0.03, 0.01, 0.005, 0.003, 0.001, 0.001}; 30 observations per case; 100 cases × 5 seeds × 6 arms = 3000 inferences.

Estimated compute: ~2hr CPU smoke (with full V_REL pre-flight), ~4-6hr CPU full. NO GPU needed (matmul-light categorical Bayes + cleanup).

---

## CONTRACT

- exp_dev owns: cell design, arm details, hardening choices, smoke harness, pre-reg authorship in `preregs/`, smoke verification, ship via queue_add.sh per pause gate
- research owns: brain-mapping rationale + literature anchoring + cross-thread synthesis (this note + research_drill note)
- skunkworks owns: STRICT vet of HP/HF bands + verdict classification post-run + by-construction-saturation tiering
- Director (orchestrator): pause-gate + queue routing

## AUTONOMY DECLARATION

exp_dev has full autonomy over cell design within the brain-grounding constraints + pre-reg band brackets above. If exp_dev determines a different anchor (e.g., starts with #2 medical instead of #1 vmPFC) based on smoke results or capacity, that's exp_dev's call — log decision rationale.

If exp_dev determines all 3 anchors are blocked (substrate parts don't compose as research claims), file a pushback note to research within 2 cycles with the failure mode.

Tag: EXP_DEV_HANDOFF_ABDUCTIVE_PRIMITIVE_STAGE3_VMPFC_OCCAM_REFUSE_P_DEFLATED_0.42_THREE_ANCHORS
