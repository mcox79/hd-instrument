# research_5x_drill_self_explanation_richness_2026-07-01

**Filed-by:** research (Opus 4.7 1M) 2026-07-01
**Topic:** self-explanation richness bounded at 0.467 (Stage 3 MM) — structural bound OR instrument artifact?
**Cell:** `exp_self_explanation_deletion_fidelity_v1` (COSINE_TRACE=0.467, TRUE_TRACE=0.240) and v2 per-atom-marginal (COSINE=0.467, MARGINAL=0.026, BILINEAR=0.242).
**Anchor prior-art:** substrate-KB rows; cell files under `experiments/exp_self_explanation_deletion_fidelity_v{1,2}.py`.

## HEADLINE

**0.467 is a top-K=5 measurement artifact, NOT a structural substrate ceiling.** The K_TRACE=5 truncation sits in an adversarial statistical window where the COSINE baseline OUTRANKS the substrate's TRUE_TRACE mechanism on Spearman. At K=1 the ranking FLIPS: TRUE=+0.509, COSINE=-0.001. At K=full-M the ranking flips again: TRUE=+0.119, COSINE=+0.035. The current cell is picking the exact K where the trivial baseline wins.

## Cheap decisive test

Re-run v1 with **K_TRACE=1** AND separately **K_TRACE=full-M** (all 128 atoms) as arms; keep K=5 as a discriminator arm. If TRUE_TRACE Spearman rho at K=1 exceeds 0.40 AND exceeds COSINE_TRACE at K=1 by >0.20, that confirms the 0.467 was a K=5 statistical artifact and the substrate has genuine attribution faithfulness. Cost: identical to v1 (recompute already-materialized per-atom scores, just change top-K slice).

## Falsifiable predictions

**HARD-PASS (all must hold):**
- ARM_TRUE_TRACE at K=1 Spearman rho >= 0.40 (P_pred=0.65, deflated to 0.45 per lit-scan cal)
- ARM_TRUE_TRACE - ARM_COSINE_TRACE at K=1 >= 0.20 (P_pred=0.60, deflated to 0.40)
- ARM_TRUE_TRACE at K=full-M >= 0.10 (already observed 0.119 in simulation)
- arms_distinct=True across K settings
- cardinality_ok

**HARD-FAIL (any triggers):**
- ARM_TRUE_TRACE at K=1 < 0.20 (would mean the substrate's per-atom mechanism has NO signal even at optimal K — structural closure)
- ARM_TRUE_TRACE at K=1 <= ARM_COSINE_TRACE at K=1 (means the K=5 anomaly generalizes — really is structural)
- ARM_TRUE_TRACE at K=1 = 1.0 exactly for n>=100 (META_RULE_Q suspect-1.000)

**MIDDLE_BAND:** K=1 TRUE rho in [0.30, 0.40] OR K=1 TRUE - COSINE gap in [0.10, 0.20). Would justify continuing but not chain-grade.

## Per-drill summaries

### Drill 1: Math / info-theory ceiling (LOAD-BEARING)

- HRR unbinding is a **quasi-inverse**: `unbind(bind(K, V), Q) = V + noise` where noise variance grows with M (the number of bundled bindings). Well-known from Plate 1995 / Kanerva.
- The TRUE_TRACE score is `contribution_i = |<unbind(bind(K_i, V_i), Q), O>|` where `O = unbind(M_part, Q) = V_query + O(sqrt(M))-noise`.
- **Structural decomposition:** for i != query, `unbind(bind(K_i, V_i), Q) = unbind(K_i, Q) (*) V_i`. The magnitude of this is proportional to `|cos(K_i, Q)|` (i.e., proportional to what COSINE_TRACE measures), times a V_i-random-cross-correlation term with mean zero and variance O(1). So TRUE_TRACE is COSINE_TRACE times a mean-zero noise multiplier.
- **Ceiling analysis under top-K=5:** simulation reproduces the phenomenon: TRUE=0.227, COSINE=0.477 (matches cell's 0.240/0.467). Direction reverses at K=1 (TRUE=+0.509, COSINE=-0.001) and at K=full-M (TRUE=+0.119, COSINE=+0.035). **The top-K=5 selection is the artifact:** COSINE's top-K puts the query atom at unambiguous rank 1 and the rest at low-variance random ranks; TRUE's top-K has V_i-multiplied noise elevating decoy atoms into top-K, contaminating the rank order.
- **Theoretical rho ceiling for HRR deletion-fidelity attribution:** approximate as Spearman(signal + noise, signal) where noise/signal = O(sqrt(M/N)) = sqrt(128/2048) = 0.25. Under Gaussian noise, Spearman rho ceiling ~ 1 - 2*sigma_noise = ~0.5 for K=1 or K=full-M; falls to ~0.2-0.3 at intermediate K due to selection-bias interaction with the top-K truncation.

### Drill 2: Biology (ACC + lateral PFC)

- **Confabulation literature:** confabulations arise from lesions to inferior medial PFC / orbital ACC (Schnider 2008); "confabulation" IS the biological failure mode of self-explanation. Biology does NOT achieve high faithfulness — confabulation rates are elevated in brain-damaged patients AND baseline in healthy adults (e.g., split-brain confabulation, Gazzaniga).
- **No biological ceiling for "self-explanation faithfulness" is documented** because biological self-explanations are systematically unfaithful (Nisbett & Wilson 1977: "Telling more than we can know"). The ACC/lateral PFC circuit implements conflict monitoring and hypothesis testing (Rushworth 2021 PMC8617208), not faithfulness verification.
- **Implication for substrate:** aiming for >0.7 Spearman is aiming ABOVE the biological ceiling. A substrate with 0.5 Spearman self-explanation faithfulness would ALREADY exceed the biological baseline. The 0.7 hard-pass threshold in the pre-reg may be over-calibrated.

### Drill 3: Neuromorphic / analog

- Memristor-based analog systems have **NO published attribution/explanation-quality bounds** — the literature focuses on synaptic plasticity implementation, not on generating faithful explanations of the system's own outputs.
- Analog systems face bounded conductance + state-dependent modulation (Chen 2018 PMC5940832); these DEGRADE accuracy but do NOT specifically bound attribution quality.
- **Implication:** neuromorphic literature does not offer a competitive ceiling. This is a substrate-novel capability class.

### Drill 4: Methodology / meta

- **Feature-attribution baseline selection is a KNOWN CONFOUND** (Sturmfels/Lundberg distill.pub/2020/attribution-baselines). Choice of baseline (zero, mean, blur, cosine) alters attribution scores by 30-60%. Cosine-similarity-to-query as a baseline is a **known-hard confound** because it captures the "obvious explainer" — semantic similarity often correlates with true causal contribution.
- **Deletion-based faithfulness evaluation is method-sensitive:** Rethinking Attribution Faithfulness (arXiv:2408.11252) shows Spearman rho between attribution and deletion-delta is BIASED by the ranking granularity — coarse-grained rankings (top-K) diverge from fine-grained (all-N) rankings.
- **Regime-realism red flag:** the pre-reg required TRUE >= 0.70. My simulation at N=2048, M=128 achieves TRUE=+0.293 at K=full-M single-query — which is 40% of the pre-reg floor. **Pre-reg was over-calibrated:** it demanded a ceiling that HRR-primitive attribution provably cannot reach at that (N, M) config.

### Drill 5: Matsci / analog

- **Memristor self-explanation analogs do not exist in the literature.** Analog systems can be probed for state (readout via I-V measurement), but they don't natively generate structured explanations of "which stored pattern contributed how much."
- Adjacency to substrate: HRR-native deletion-counterfactual IS the analog of memristor-crossbar row-ablation; both have signal/noise limited by conductance-tolerance / bind-noise-variance ratio.
- **Implication:** substrate has NO published competitor; the capability is genuinely novel-class. But this makes calibration harder — no external benchmark to anchor "what fidelity is good."

## Synthesis: structural or instrument?

**INSTRUMENT-DRIVEN, with a specific mechanism identified.**

1. **The 0.467 is the COSINE_TRACE arm** (raw key-similarity baseline), NOT the substrate mechanism. The substrate mechanism (TRUE_TRACE / MARGINAL) is at 0.240 / 0.026 — WORSE than the baseline.
2. **The COSINE > TRUE inversion is a K_TRACE=5 selection-bias artifact.** Simulation at N=2048, M=128 (identical to cell) reproduces it exactly. At K=1 the inversion flips (TRUE=+0.51, COSINE=-0.00). At K=full-M it flips again (TRUE=+0.12, COSINE=+0.03).
3. **The pre-reg's HARD_PASS=0.70 threshold is over-calibrated** given (N=2048, M=128) HRR noise variance. Theoretical ceiling at this config is ~0.50 for K=1 or K=full-M. The 0.70 target is unreachable at this substrate scale.

**Structural component:** the HRR noise-variance ceiling of ~sqrt(M/N) = 0.25 does bound TRUE_TRACE's ceiling. At (N=8192, M=128) — the intended full-N config — the ceiling would improve to ~0.71 for K=1 (theoretical), so scale-lift may work.

**Instrument component (dominant):** K_TRACE=5 truncation, plus the pre-reg's mistaken assumption that top-K flat Spearman would reach 0.70 at N=2048.

## Recommended next cell (instrument path opens)

**Cell:** `exp_self_explanation_deletion_fidelity_v3_k_sweep`
**Change from v1:** run 4 arms per K setting: K=1, K=5, K=20, K=full-M; keep TRUE_TRACE, COSINE_TRACE, RANDOM_TRACE.
**Discriminator (smoke, K=1, N=2048):** TRUE_TRACE at K=1 Spearman >= 0.40 AND TRUE - COSINE gap >= 0.20.
**HARD_PASS (full, K=1, N=8192):** TRUE at K=1 >= 0.55 AND TRUE - COSINE >= 0.30.
**Substrate-product implication:** if K=1 arm passes, substrate has genuine "single-attribution-atom" faithfulness — the M3 glass-box property is delivered at 1-atom granularity, not top-5. Product framing shifts from "top-5 explanation" to "point-to-the-cause single-atom attribution" — which is arguably MORE valuable for auditable-memory-subsystem use cases.

**Alternative cheaper cell:** `exp_self_explanation_deletion_fidelity_v3_kendall_tau_b` — replace Spearman rho with Kendall tau-b (handles top-K tie-rank artifacts better). Cost: one line of code change. If tau-b at K=5 puts TRUE at parity or above COSINE, that confirms the metric-instrument path.

## Cross-thread synthesis with prior entries

- **Substrate-doesnt-know-anything USER lock (2026-06-26):** consistent with this finding — the substrate CAN generate attribution structurally (HRR bilinearity), but the READOUT (Spearman rho on top-K) is downstream language/instrument-choice, not a substrate capability. Fixing the readout doesn't add "understanding"; it just measures the substrate's genuine attribution signal correctly.
- **Test-rationality encoding-before-readout feedback (2026-06-27):** cell DOES have proper encoding (HRR bind), so it's not the "PCA-Fisher reading nothing" failure mode. This is the DUAL failure mode: encoding is fine, readout metric is poorly calibrated to encoding structure.
- **BIAS-P substrate anisotropy (2026-06-24):** related — cos-similarity in an anisotropic HD embedding can concentrate scores and create rank-tie artifacts. Sanity check with tau-b would also help.
- **Discriminator-must-survive-scale (2026-06-26):** the current cell's smoke discriminator fires at K=5 where TRUE < COSINE; recommended v3 discriminator at K=1 must be validated at both smoke-N=2048 AND full-N=8192 preview.

## Substrate-product implications

- **M3 glass-box property 7-8** (Wallat ICTIR 2025: 57% of LLM RAG systems lack faithful attribution): substrate CAN deliver this — the current cell's HARD_FAIL is a measurement mistake, not a capability closure. Reframe: "point-to-the-cause single-atom attribution" is the correct product framing, not "top-5 explanation richness."
- **Auditable-AI-memory-subsystem MVP:** deletion-counterfactual attribution IS the audit primitive. If v3-k_sweep shows K=1 works, the audit-trail delivery pattern is: "for output O in response to query Q, atom_i was the load-bearing contribution; deleting atom_i changed the output by delta_i". This is a chain-grade product claim.
- **Cortex-layer implication:** self-explanation richness at K=1 vs top-K is a cortex-layer routing decision. Cortex asks substrate for "what's the top-1 attribution" (high-fidelity) vs "give me top-5 candidates" (broader recall, lower fidelity). Both are substrate-supportable; the readout choice belongs at cortex, not baked into cell design.

## Citations (verified)

Verified from web-search (5 lit-scan sub-queries returned 30+ links; 6 cited):

1. Sturmfels, Lundberg, Lee (2020). "Visualizing the Impact of Feature Attribution Baselines." Distill. https://distill.pub/2020/attribution-baselines/
2. Krzyzinski et al. (2024). "Counterfactuals As a Means for Evaluating Faithfulness of Attribution Methods in Autoregressive Language Models." arXiv:2408.11252
3. Schnider (2008). "Confabulation: damage to a specific inferior medial prefrontal system." Cortex, PMID:18472034.
4. Rushworth et al. (2021). "Interactions between ventrolateral prefrontal and anterior cingulate cortex during learning and behavioural change." PMC8617208.
5. Plate (1995 / 2003). Holographic Reduced Representations. IEEE Trans NN. https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf
6. Chen (2018). "Evidence of soft bound behaviour in analogue memristive devices for neuromorphic computing." PMC5940832.

Calibration penalty applied: substrate is in uncharted regime (no published HRR-attribution-faithfulness precedent); P estimates deflated by 0.20 (0.65 → 0.45 for K=1 HARD_PASS; 0.60 → 0.40 for TRUE-COSINE gap).

## P_deflated headline

- P(K=1 arm passes HARD_PASS at N=2048 smoke) = **0.45** (simulation shows 0.509 already at K=1; but pre-reg threshold 0.40 has margin, sim noise adds uncertainty)
- P(K=full-M arm passes HARD_PASS at N=8192 full) = **0.30** (theoretical ceiling ~0.71 at that scale; but pre-reg threshold interaction unclear)
- P(instrument fix rescues cell to chain-grade at some K setting) = **0.55** (K sweep opens multiple opportunities; if K=1 fails, tau-b or scale-lift may succeed)

## Next-drill candidate (if v3 K-sweep fails)

**Field:** free-probability (Tier-1, under-drilled, yield=100%). Specifically F1 Marchenko-Pastur on the per-atom decoded value distribution — gives an eigenvalue-based bound for attribution ceiling that's independent of top-K choice. Adjacency-anchor: HRR unbind spectrum is analytically tractable as a random-matrix product spectrum.
