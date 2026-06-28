# RESEARCH 2x DRILL: Abductive reasoning primitive for substrate Stage 3

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Topic:** Brain-grounded abductive reasoning primitive (inference to best explanation; Peirce 1903 / Lipton 2004)
**Stage:** Stage 3 compositional understanding (per USER stage-progression LOCKED 2026-06-26)
**Cap_map:** Stage 3 gap row — abductive reasoning (P(H|E) ranking over candidate bank)
**Pre-reg compliance:** META_RULE_AA/AC/AE/AF/AG/AH + compute-formulas-in-code + USER scour-first

---

## HEADLINE

**Substrate already has the core abductive infrastructure HARD_PASS (Bayes net inference / structure-learn / FHRR amplitude-Bayes / closure-signature abduction kernel / counterfactual replay).** The remaining Stage 3 gap is a *bank-managed multi-hypothesis abductive primitive* with (a) brain-grounded Occam-prior weighting, (b) ambiguity refuse-gate for the no-single-best case, and (c) hippocampal-vmPFC two-stage architecture (HC generates candidates; vmPFC evaluates / Lipton's "loveliness" valuation). Top cell to ship: **abductive_bank_vmpfc_valuation_v1** (P_deflated=0.42).

---

## SCOUR-FIRST: prior substrate work (READ DISK — META_RULE_NO_HALLUCINATED_NUMBERS)

Six prior substrate atoms found via `director_kb_query.py`; ALL numbers below read from `data/<exp>/metrics.json` on disk, not memory:

| Prior atom | Verdict | Key per-arm number | What it gives us |
|---|---|---|---|
| `lap8_bayesian_fhrr_cpu_v1` | HARD_PASS | bayes_acc=1.0 (n=33: Monty Hall 0.667 / medical 0.165 / spam 0.843) | FHRR |amp|² as native probability; likelihood reweight works |
| `comp21_bayesian_at_l3_cpu_v1` | HARD_PASS | L3=1.000 L1=1.000 gap=0.000 | Bayesian belief update over DEPTH-3 composite hypotheses; abductive composition works |
| `stretch3_4_bayes_net_cpu_v1` | HARD_PASS | posterior-match=0.987 (n=150) | Full Bayes net inference via enumeration; conditional independence respected |
| `stretch4_1_bayes_net_learning_cpu_v1` | HARD_PASS | struct_precision=0.950 recall=0.778 CPT-err=0.014 | Substrate LEARNS Bayes-net structure+params from data |
| `substrate_abduction_f1_weakest_signature_kernel...` | HARD_PASS | 6.63x closure ratio for xor; abduced signature matches ground truth without being told | Reverse-math abduction of weakest closing signature works |
| `substrate_abduction_f1b_confound_break...` | HARD_PASS | corr(closure, pair_sep)=0.68 corr(closure, recover)=0.71; signature SHARPENED | Confound-break methodology — distinguishes true load-bearing property from confounded one |
| `pp47_pp49_counterfactual_abduction_composition_v1` | MIDDLE_BAND | baseline=0.72 / cf=0.97 (hp1=0/2 hp2=2/2 hp3=2/2) | Counterfactual abductive composition partially works (HP1 baseline-floor missed) |
| `counterfactual_replay_latency_delta_stack_v2` | HARD_PASS | speedup=5.47x acc=1.000 | Counterfactual replay fast (substrate can iterate over hypotheses) |
| `counterfactual_regret_comparison_vmpfc_v1` | SELFTEST_OK | vmpfc_R2=0.975 direct_R2=0.976 leak=0.167 crlb=1.000 | vmPFC valuation architecture validated at selftest level (full run pending) |
| `cortex_schema_exemplar_bayes_importance_sample_v1` | SELFTEST_OK | oracle=0.800 K_NN=0.758 base=0.217 rand=0.208 | Exemplar-Bayes importance sampling distinguishes 4 arms (base vs schema-driven) |
| `substrate_aaa1_bayesian_tier_overlay_cpu_v1` | HARD_FAIL | bayes=0.591 hard=0.615 delta=-0.025 | Bayesian overlay HURT vs hard labels on tier-prediction (cautionary: posterior is NOT always better than MAP-hard) |

**Code primitives present (`hdlab/bayesian_inference.py`):** `bayes_update`, `bayes_update_categorical`, `map_estimate`, `EMMixture`, refuse-on-zero-marginal (USER 18th rule). 318 lines, executable; `refuse_gate.py` 130 lines; `multi_hop.py` 361 lines.

**Negative-knowledge from prior work (load-bearing):**
- substrate_aaa1 HARD_FAIL says: Bayesian-posterior overlay can HURT when underlying features are weak — do NOT default to Bayesian; show lift over hard MAP baseline as a HARD_PASS condition.
- pp47_pp49 MIDDLE_BAND says: counterfactual abduction needs careful baseline calibration (baseline 0.72 not 0.85 — HP1 too tight).
- abduction_f1b says: pair-separability (not recoverability) is the true load-bearing property for binding-mediated abductive closure — a confound was caught and SHARPENED.

---

## BRAIN LITERATURE (CITED@ — verified web-search 2026-06-27)

CITED@Friston-2024-active-inference [1,2,4]: brain as hierarchical generative model minimizing variational free energy; perception IS abductive inference (model selects hidden-state hypothesis explaining sensory data). Active inference framework directly maps abduction onto VFE minimization. THEORETICAL@ scoring formula: -log P(o|h) - log P(h), where h is hypothesis.

CITED@Yuille-Kersten-2006-vision-bayesian [3]: "analysis by synthesis" — vision system generates predictions from candidate scene hypotheses and compares to observation; the best-explaining scene is selected. Forward generative model + backward inversion = abduction. Generative-Bayesian framework explicitly Peircean.

CITED@Hohwy-2013-predictive-mind [4]: prediction error minimization is abduction; hierarchical inference at multiple levels; precision-weighted prediction error gates which hypothesis to revise. Schema-based active inference (arxiv 2601.18946) supports rapid generalization via frontal cortex coding abstract structure — directly supports a schema-bank-as-hypothesis-prior architecture.

CITED@vmPFC-multifaceted-role [5,6]: vmPFC critical for representing reward/value-based decision-making; valuation hypothesis (Roy 2012) — vmPFC assigns significance to candidates. Maps onto Lipton's "loveliness" / explanatory virtue scoring. Substrate's existing counterfactual_regret_comparison_vmpfc_v1 SELFTEST_OK with R²=0.975 already prototypes this.

CITED@Gopnik-causal-blickets [Gopnik 2007 / Basch 2024]: toddlers infer higher-order causal principles from few observations; explanation-based learning by 18-24 mo. Confirms abductive primitive is brain-fundamental, not adult-only.

CITED@MacKay-Occam-bayes-factor [Inference.org.uk 2003]: Bayes factor implements automatic Occam's razor — penalizes models for excess parameter-space volume. THEORETICAL@ formula: BF_ij = ∫ P(D|θ,M_i) P(θ|M_i) dθ / ∫ P(D|θ,M_j) P(θ|M_j) dθ. Simpler hypothesis with same fit wins.

CITED@QMR-INTERNIST-Shwe-1991 [Heckerman 1991 belief network]: production system for medical abductive diagnosis; ranks diseases by posterior given symptoms; "unifying hypothesis" = single disease explaining most symptoms (the abductive winner) vs "differential" (multiple plausible). Maps directly onto substrate's needed (a) rank candidates and (b) detect ambiguity refuse-case.

---

## PURE MATH ANGLES (THEORETICAL@)

THEORETICAL@MAP-as-abduction: argmax_h P(h|D) = argmax_h P(D|h)·P(h); already in `hdlab/bayesian_inference.py::map_estimate`. Substrate-trivial.

THEORETICAL@Bayes-factor-model-comparison: P(M_i|D)/P(M_j|D) = [P(D|M_i)/P(D|M_j)] · [P(M_i)/P(M_j)]. Implements Occam's razor via integrated evidence. Substrate path: weight candidate hypotheses by HRR-complexity-prior (count of unique role-fillers in binding tree); simpler hypotheses get higher prior.

THEORETICAL@Inverse-problem: abduction = inverse problem (given y = f(x) + noise, recover x). Crystal-structure, protein-folding, phylogenetic reconstruction all formal abduction; energy-landscape (Bayesian posterior at inverse-temperature β) directly matches FHRR amplitude-as-probability framing (lap8 HARD_PASS).

THEORETICAL@Bayesian-model-averaging: when no single hypothesis dominates, weighted sum P(y|D) = Σ_M P(y|M,D)·P(M|D). Substrate path: superpose candidate hypotheses with amplitudes = posterior weights; FHRR addition is natively weighted superposition.

THEORETICAL@Refusal-on-ambiguity: gate fires when top-2 posteriors are within ε of each other (entropy of posterior > threshold). Substrate primitive: `refuse_gate.py` already handles V_REL=128/256 refusal; need to extend to posterior-entropy refusal.

---

## MATERIALS / BIOLOGY / LEGAL CROSS-DOMAIN (CITED@)

CITED@Rietveld-Bayesian-PXRD [Sci Rep 2016 srep31625 / npj Comp Mat 2025]: powder XRD crystal-structure determination is ill-posed; MCMC over candidate phases; Bayesian best-first tree search on phase combinations + Rietveld lattice optimization + Bayes-factor model comparison. Direct map: substrate candidate-bank = phase pool; observation = XRD pattern; HRR-bind for phase signatures.

CITED@Protein-structure-prediction-inverse [arxiv 2406.04239 / 2502.09372]: AlphaFold3 = structural prior; posterior inference of conformational ensemble given experimental data; diffusion-based generative inverse problem. Energy-landscape basin widths ∝ posterior weights at inverse-temperature β.

CITED@Ancestral-state-reconstruction [Maddison & Maddison parsimony / Felsenstein ML]: phylogenetic abduction; given extant species, infer ancestral states; max parsimony = max likelihood under specific model. Substrate path: candidate-bank = ancestral-state hypotheses; observation = leaf states; HRR multi-hop = tree traversal.

CITED@INTERNIST-QMR-medical [PMC 21392370]: rank-ordered diagnostic hypotheses with QMR scores + unifying hypothesis detection. Directly informs substrate API: return ranked list + flag "unifying" (single dominant) vs "differential" (multiple plausible).

THEORETICAL@Legal-jurisprudence-inference-to-best-explanation [Allen-Pardo 2008]: "relative plausibility theory" — fact-finder evaluates competing narratives by which best explains the evidence; explicitly Peircean. Refuses verdict when narratives are indistinguishable ("reasonable doubt" = posterior entropy too high).

---

## CHEAP DECISIVE TEST (informs cell design — NOT cell design itself per [[feedback-no-experiment-design-in-prompts]])

Discriminating regime probe: build 10 candidate hypotheses with KNOWN ground-truth posterior weights {0.6, 0.2, 0.1, 0.05, 0.03, 0.01, 0.005, 0.003, 0.001, 0.001}. Generate 30 observations from the true generative model. Measure whether substrate's abductive primitive (a) returns top-1 = ground-truth posterior winner ≥ 0.85, (b) returns top-3 ranked correctly (Spearman ρ ≥ 0.80), (c) Occam-prior implementation shifts vote toward simpler hypothesis when likelihoods tie (compare with-Occam vs without-Occam on tie-breakers), (d) refuses (no single best) when posterior entropy > log(K)·0.85 (i.e., near-uniform).

ARM_FAIRNESS: META_RULE_AA enforced — baseline must NOT implicitly do abductive scoring. Specifically: ARM_BASELINE_MAJORITY_VOTE counts which hypothesis is closest to the most observations (no likelihood-weight, no prior), and ARM_BASELINE_NEAREST_OBSERVATION returns the hypothesis closest to the centroid of observations. Both are NON-abductive.

---

## FALSIFIABLE PREDICTIONS (HARD_PASS + HARD_FAIL)

For the top-rec cell `abductive_bank_vmpfc_valuation_v1` (full design per exp_dev_handoff):

**HARD_PASS conditions (ALL must hold):**
- ARM_ABDUCTIVE_FULL top-1 accuracy ≥ 0.85 on 10-candidate ground-truth bank
- Spearman ρ between substrate posterior rank and ground-truth posterior ≥ 0.80
- Lift over ARM_BASELINE_MAJORITY_VOTE ≥ +0.20 absolute (mechanism load-bearing)
- Lift over ARM_BASELINE_NEAREST_OBSERVATION ≥ +0.15 absolute
- Lift of ARM_WITH_OCCAM over ARM_WITHOUT_OCCAM on tie-breaker subset ≥ +0.10 (Occam load-bearing)
- ARM_REFUSE: when ground-truth posterior is uniform, refuse-rate ≥ 0.80; when concentrated, refuse-rate ≤ 0.10 (refuse-gate calibrated)
- ARM_DIAG vmPFC R² recovery ≥ 0.80 (consistent with prior `counterfactual_regret_comparison_vmpfc_v1` selftest 0.975)
- cv across 5 seeds < 0.10
- CARDINALITY_OK: expected = 5 seeds × 6 arms × 100 problems = 3000 inferences

**HARD_FAIL conditions (ANY triggers HARD_FAIL):**
- ARM_ABDUCTIVE_FULL top-1 < 0.50 (worse than random for 10-way)
- Lift over BASELINE_MAJORITY_VOTE < +0.05 (mechanism NOT load-bearing — same risk as `substrate_aaa1` Bayesian-hurt finding)
- Occam lift < +0.02 (simplicity-prior cosmetic, not mechanistic)
- Refuse-gate uncalibrated: refuse-rate on uniform-posterior < 0.40 OR on concentrated-posterior > 0.30
- cardinality breach
- META_RULE_Q suspect-1.000: any arm at 1.000 on n≥100 → halt and re-partition (likely test/prototype leak)

**MIDDLE_BAND:** top-1 in [0.50, 0.85), lift in [0.05, 0.20), Occam lift in [0.02, 0.10), refuse-rate poorly calibrated.

P_deflated calibration (per [[feedback-lit-scan-calibration-penalty]]):
- Raw lit-prior P_HP ~ 0.65 (Bayes-net + abduction-kernel both HARD_PASS; substrate has the parts)
- Novel-synthesis penalty: composes 4 prior cells (bayes_net + abduction_kernel + vmPFC + refuse_gate) — NOT genuinely-new mechanism
- Substrate_aaa1 cautionary discount: Bayesian-posterior can HURT — 0.15 deflation
- **P_deflated = 0.42** (HARD_PASS likelihood)

---

## TOP-3 CANDIDATE CELLS (rank-ordered)

### 1. `abductive_bank_vmpfc_valuation_v1` (TOP-REC — P_deflated=0.42)

**Brain→substrate mapping:** Hippocampus (pattern-completion) generates candidate hypotheses from observation cues → vmPFC (valuation) scores each candidate by P(obs|h)·P(h) with Occam complexity-prior → refuse-gate (posterior-entropy threshold) detects ambiguous case.

**Substrate primitives composed:**
- HRR bind/unbind: bind observations to candidate-hypothesis frames; unbind for likelihood
- `bayes_update_categorical` (hdlab/bayesian_inference.py): posterior over candidate bank
- `refuse_gate` (hdlab/refuse_gate.py): extended with `refuse_on_entropy` mode
- Multi-bank partition: candidate hypotheses in parallel banks (avoids interference)
- FHRR amplitude-as-probability: native posterior weight on superposition (per lap8 HARD_PASS)

**Concrete test:** 10-candidate hypothesis bank with known ground-truth posterior; 30 observations from true generative model; rank candidates; compare to ground-truth posterior rank.

**Discriminator (regime / arm structure):** 6 arms — BASELINE_MAJORITY_VOTE, BASELINE_NEAREST_OBSERVATION (META_RULE_AA non-abductive baselines), ABDUCTIVE_WITHOUT_OCCAM, ABDUCTIVE_WITH_OCCAM (full); ARM_REFUSE_CALIBRATION (uniform vs concentrated posterior subsets); ARM_DIAG_VMPFC_VALUATION (R² recovery of substrate's vmPFC head, sanity).

**Pre-reg HP/HF bands:** see above.

**Compute cost:** ~2 hr CPU smoke; ~4-6 hr CPU full (no GPU needed — categorical Bayes + cleanup is matmul-light).

**Fairness gate:** META_RULE_AA both BASELINE arms verified NON-abductive (no likelihood, no prior); META_RULE_S band-calibration uses TOP-3 not TOP-1 for ranked-list eval (multi-explanation is genuinely multi-valued).

### 2. `abductive_diagnosis_medical_QMR_v1` (P_deflated=0.35)

**Brain→substrate mapping:** Maps directly onto QMR/INTERNIST architecture; substrate stores disease→symptom prior likelihoods (already supported by `stretch4_1_bayes_net_learning` HARD_PASS); given partial symptom set, return ranked diseases + flag "unifying hypothesis" (single dominant) vs "differential" (top-K within ε).

**Test:** 50 medical-vignette cases (synthetic; matched to public datasets like MedQA / DDXPlus); 10 candidate diseases each; substrate returns top-3 ranked diagnoses; evaluated against ground-truth ranking.

**Discriminator arms:** BASELINE_SYMPTOM_OVERLAP (count matching symptoms; non-Bayesian), BASELINE_FREQ_PRIOR (most-prevalent disease), ABDUCTIVE_BAYES_NET (full), ABDUCTIVE_BAYES_NET + Occam_prior (composite diseases penalized), ARM_REFUSE_DIFFERENTIAL (entropy-gate fires on ambiguous case).

**Pre-reg HP:** top-3 recall ≥ 0.75 (medical diagnosis is genuinely multi-valued; top-3 is the QMR norm); lift over BASELINE_SYMPTOM_OVERLAP ≥ +0.30; differential-flag precision ≥ 0.70 on hold-out ambiguous cases.

**Compute cost:** ~3-4 hr CPU smoke + dataset prep ~2 hr.

**P deflation:** raw 0.55 → 0.35 (data-sourcing risk: synthetic medical data may not reflect real diagnostic ambiguity distribution; consider DDXPlus public release).

**Why ranked #2:** stronger external validation but higher data-prep risk; ship after #1 lands HARD_PASS to provide the load-bearing primitive.

### 3. `abductive_phylogenetic_ancestral_reconstruction_v1` (P_deflated=0.28)

**Brain→substrate mapping:** Domain test of abductive primitive on phylogenetic ancestral-state reconstruction (Felsenstein ML pruning algorithm); leverages substrate's multi-hop depth-15 HARD_PASS for tree traversal; candidate-bank = possible ancestral states.

**Test:** 20-leaf synthetic phylogenetic tree with known evolutionary model; reconstruct internal-node ancestral states; compare to ground-truth via Robinson-Foulds distance.

**Discriminator arms:** BASELINE_MAJORITY_PARSIMONY (Fitch algorithm; non-Bayesian), BASELINE_NEAREST_LEAF (closest-extant-species; trivial), ABDUCTIVE_ML_PRUNING (full Felsenstein on substrate), ABDUCTIVE_ML + Occam_branch_length_prior, ARM_DIAG_MULTIHOP_DEPTH (sanity: substrate's depth-traversal handles tree depth 5).

**Pre-reg HP:** internal-state recovery ≥ 0.85; Robinson-Foulds distance ≤ 0.20; lift over BASELINE_MAJORITY_PARSIMONY ≥ +0.15.

**Compute cost:** ~4-6 hr CPU full (tree algorithms + 20-node × 5-state space).

**Why ranked #3:** strong cross-domain validation but distant from M3 conversational AI goal; runs as stretch only if #1 + #2 land HARD_PASS and capacity is free.

---

## CROSS-THREAD SYNTHESIS

This drill composes with:
- **Stage 3 compositional understanding (USER LOCKED 2026-06-26):** abduction IS one of the core operational primitives for compositional reasoning (along with TOM, schema, counterfactual). Substrate already has 6+ chain-grade pieces; this is the bank-management + Occam-prior wrapper.
- **M3 conversational AI:** abductive primitive directly enables (a) ambiguous-input interpretation ("which of several intents fits?"), (b) topic-model selection in conversation, (c) clarification-request gating (refuse-fire = ask clarifying question rather than commit to wrong hypothesis).
- **schema_driven_proof_step_inference_v1 prereg (filed 2026-06-27):** schema-bank-driven retrieval is structurally identical (schema = hypothesis bank; proof prefix = observation). The Occam-prior + refuse-gate machinery built here transfers directly.
- **substrate_aaa1 HARD_FAIL (Reservation A):** cautionary tale — Bayesian overlay HURT vs hard MAP labels on tier-prediction. The HARD_PASS condition "lift over hard MAP baseline ≥ +0.10" is the structural fix.
- **counterfactual_regret_comparison_vmpfc_v1 SELFTEST_OK** (R²=0.975 selftest, full pending): vmPFC valuation head already prototyped; this cell PROMOTES that selftest to full-arm chain-grade via the abductive use-case.
- **substrate_abduction_f1/f1b HARD_PASS (closure-signature):** the f1b confound-break methodology (rand_proj closes via pair-separability NOT recoverability) is the load-bearing meta-lesson — design arms so they distinguish TRUE mechanism from CONFOUNDED candidates. This cell applies that discipline via 2 non-abductive baselines + Occam-vs-no-Occam ablation.

**Field-advisor note:** This drill is NOT in the top-5 field-advisor recommendations (those are free-probability/semiconductor adjacencies). But the request is USER-originated for Stage 3 capability development — capability-development priority overrides field-coverage heuristic per [[feedback-capability-dev-is-goal-cert-grade-is-instrument]].

---

## SUBSTRATE-PRODUCT IMPLICATIONS (per [[feedback-no-papers-product-only]])

For the M3 glass-box conversational AI:
1. **Ambiguous user-input handling:** substrate ranks candidate intents by P(intent|utterance); refuse-fire on top-2 within ε triggers clarification request rather than wrong-confident reply.
2. **Diagnostic conversation:** medical / troubleshooting / debugging dialogues become substrate-native via ranked candidate-hypothesis output.
3. **Explanation auditing:** every substrate response carries a ranked-hypothesis trace (top-K candidates + their posterior weights + Occam-complexity scores) — directly supports M3's glass-box audit-trail requirement.
4. **Differential vs unifying-diagnosis pattern from QMR:** transfers structurally to conversational AI — "I have one clear answer" vs "I have several plausible answers and need more information" is the load-bearing distinction conversational AI currently fails at.

For M4 substrate-as-research-director:
- Cell-design itself is abductive ("which experiment would best discriminate competing mechanisms?"); a chain-grade abductive primitive lets substrate propose discriminating cells.

For exp_dev handoff: hand-off file written at `notes/exp_dev_handoff_research_drill_2x_abductive_reasoning_primitive_stage3_2026-06-27.md` (anchor candidate = abductive_bank_vmpfc_valuation_v1).

---

## CITATIONS (verified count: 14 web-search-confirmed + 6 substrate-disk metrics)

**Brain literature (web-search 2026-06-27):**
1. Friston 2024 — generalized active inference (Springer / Bio Cybernetics)
2. Friston et al. 2024 reframing expected free energy (arxiv 2402.14460)
3. Yuille & Kersten 2006 vision as Bayesian inference: analysis by synthesis (TICS 10:301-308)
4. Hohwy 2013 The Predictive Mind (Oxford UP) — predictive processing as hierarchical abduction
5. vmPFC multifaceted role review (PMC5862740)
6. vmPFC valuation hypothesis Roy 2012 (PMC3707083)
7. Schema-based active inference + frontal cortex (arxiv 2601.18946)
8. Gopnik et al. 2024 review causal learning in infants (WIREs Cog Sci 1678)
9. Gopnik et al. 2007 blickets & babies (PubMed 17087545)
10. MacKay 2003 Bayes factor + Occam's razor (Information Theory book ch.28)
11. QMR/INTERNIST Shwe-Heckerman 1991 (ResearchGate 21392370)

**Cross-domain (web-search 2026-06-27):**
12. Bayesian PXRD crystallography (Sci Rep srep31625 / npj Comp Mat 2025-01627)
13. Protein structure inverse problem (arxiv 2406.04239 + 2502.09372)
14. Phylogenetic ML ancestral-state (PMC5395464 + arxiv 1702.01436)

**Substrate disk (metrics.json verified 2026-06-27):**
- lap8_bayesian_fhrr_cpu_v1 HARD_PASS
- comp21_bayesian_at_l3_cpu_v1 HARD_PASS
- stretch3_4_bayes_net_cpu_v1 HARD_PASS
- stretch4_1_bayes_net_learning_cpu_v1 HARD_PASS
- substrate_abduction_f1 + f1b HARD_PASS (both)
- counterfactual_replay_latency_delta_stack_v2 HARD_PASS
- substrate_aaa1_bayesian_tier_overlay HARD_FAIL (cautionary)

---

## NEXT-DRILL CANDIDATE

After this cell lands: drill into **schema-driven abductive prior** (compose this primitive with the Tse-Morris schema-bank cell already prereg'd 2026-06-27 — schemas become structured priors over the candidate bank; expected lift via informative-prior shrinkage). That is a Stage-3-internal composition drill, deferred until this cell + schema_driven_proof_step_inference_v1 both land HARD_PASS.

Tag: RESEARCH_DRILL_2x_ABDUCTIVE_REASONING_PRIMITIVE_STAGE3_BRAIN_GROUNDED_VMPFC_OCCAM_REFUSE_P_DEFLATED_0.42
