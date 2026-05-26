# Research — Saad-Solla saddle-cascade DEEP DRILL (now-leading theoretical home)

**Date.** 2026-05-25
**Owner.** Research sub-agent (Opus synthesis, parallel WebSearch lit-scan).
**Trigger.** `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/metrics.json` — CASCADE_PASS. discrete-3-state preferred over sigmoid by `delta_BIC = 194.9`; equal-spacing prediction error = 0.0378 (within 0.05 tolerance). Reanalysis displaces 1-RSB as primary theoretical home and elevates Saad-Solla saddle-cascade from Tier-1 candidate (P=0.46, `notes/research_alternative_theoretical_homes_2026-05-24.md`) to LEADING.
**Discipline.** 2x depth drill per [[feedback-2x-means-depth]] (drill the existing finding DEEPER, not re-verify). Generic terms only per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25, cap novel-synthesis P at 0.50).
**Cross-ref to locked primitive decision.** `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` LOCKED linear-heteroassoc as primary substrate primitive. This drill evaluates whether Saad-Solla saddle-cascade theory — developed for soft-committee SGD — applies to the substrate's LINEAR-HETEROASSOC + Hebbian-outer-product + BSC + PPMI mechanism. **This is novel-synthesis territory**, so calibration penalty enforced.

---

## (a) HEADLINE

> **Saad-Solla saddle-cascade is a STRONG STRUCTURAL FIT but NOT a closed-form fit for the specific values 0.94/0.74/0.60.** Updated P = **0.48** (deflated from naive 0.62 by 0.14 calibration penalty; capped at 0.50 novel-synthesis ceiling).
>
> The four headline findings:
>
> 1. **(Plateau heights from arithmetic — Drill Q1) NO closed-form derivation produces 0.94/0.74/0.60 from substrate primitives.** Saad-Solla erf-activation closed form `ε_g = 1/6 + (1/π) Σ_{ij} [arcsin(Q_ij/2) − 2 arcsin(R_ij/2)]` requires committee-machine architecture (multiple hidden units summed). Substrate has no hidden-unit summation — it's a single-shot linear readout. The arithmetic that would produce specific heights is **structurally inapplicable**. What DOES apply: the *equal-spacing* structure (G1−G2 gap 0.0948 vs G2−G3 gap 0.1704, ratio 0.556) is consistent with saddle-cascade theory **only as a discrete-permutation-orbit signature, not as a height-prediction**. The reanalysis's spacing_error=0.0378 within tolerance is **necessary but not sufficient** evidence — saddle-cascade is consistent with this, but so is any 3-orbit categorical mechanism (linear stratified codebook overlap per primitive-decision note's Mechanism A, P=0.45).
>
> 2. **(Cleanest falsifier — Drill Q2) Two-tier falsifier identified.** Tier 1 (CPU-cheap, free): **equal-spacing at 4+ plateaus**. Saad-Solla cascade theory predicts that adding a 4th categorical level (K_eff=4 corpus structure) produces a 4th plateau with PREDICTABLE spacing under the integer-orbit arithmetic. Falsifier: extend the 3-corpus design to a 4-corpus design (same / 3-stage / 4-stage / diff); HARD-PASS = 4 equal-spaced plateaus visible (BIC delta > 30 over 3-state model); HARD-FAIL = 3 plateaus persist or 4th plateau spacing breaks equal-spacing rule by > 2× error. Tier 2 (GPU, more expensive): **plateau-escape time scaling**. Saad-Solla theory predicts plateau duration τ_p ∝ 1/λ where λ is the smallest non-zero eigenvalue of the saddle Hessian; this scales as 1/N for symmetric plateau. Substrate analog: measure retention-curve-vs-time at multiple N values during training; HARD-PASS = plateau-duration scales as N^{-1} (linear); HARD-FAIL = constant or N^0.5 (different mechanism).
>
> 3. **(K-tracking — Drill Q3) Saad-Solla theory STRONGLY predicts plateau-count tracks K_categorical, NOT K_tasks_sequential.** Substrate's three plateaus correspond to three *categorical-overlap classes* (full / partial / disjoint), not to three *learned tasks*. Per Lee-Goldt-Saxe 2021 multiple-teacher CL: plateau structure tracks task-similarity classes, with intermediate-similarity producing maximum forgetting (NON-MONOTONE). Substrate prediction: extending from 3 to N corpus-similarity classes should produce N plateaus; **NEW plateaus DO NOT appear automatically at K=4, 5, 6 sequential tasks unless those tasks introduce new similarity classes**. This is a sharp falsifier: ship a K-sweep at FIXED-similarity-class (K=2,3,4,5 sequential tasks all drawn from the same corpus-similarity class) — saddle-cascade predicts FLAT 3-plateau structure; if a new plateau emerges at K=5, framework is wrong.
>
> 4. **(MoE rebuild informed by saddle-cascade — Drill Q4) Saddle-cascade theory PREDICTS SHIFT-not-PARTITION at the cascade level.** K independent SHIFT experts (each full-dim N) produce K *independent* saddle cascades — each expert has its own permutation-orbit structure on its own teacher subset. PARTITION (sub-N experts) collapses this: the per-expert saddle structure shrinks below the rank needed to support multiple permutation orbits, and the cascade degenerates to a 2-plateau (or 1-plateau) structure. **Concrete MoE-design implication**: post-SHIFT MoE rebuild should show 3-plateau retention WITHIN EACH expert (each expert sees same / partial / disjoint queries to its codebook); post-PARTITION rebuild should show plateau collapse. This is a *new* falsifier that wasn't on the MoE handoff's instrumentation list — adding it costs nothing (group retention per-expert by query-overlap-class).

---

## (b) Cheap decisive test (Drill Q2 expanded)

**The 4-plateau equal-spacing falsifier (CPU-cheap; ~20–40 min):**

Design: extend Bet B 3-corpus to 4-corpus (same / 3-stage-overlap / 4-stage-overlap / disjoint). Reuse existing fixtures. Compute 4-state discrete BIC vs 3-state BIC vs sigmoid BIC. Compute equal-spacing prediction error for the inferred 4 plateau heights.

**Pre-registered bands:**

- **HARD-PASS (Saad-Solla 4-plateau confirmed):** BIC_4state < BIC_3state by > 30 AND spacing_error_4state < 0.05 AND gap_ratio_4state ∈ [0.45, 0.65] (consistent with 3-corpus reanalysis ratio 0.556).
- **HARD-FAIL (saddle-cascade DOWNGRADED):** BIC_4state > BIC_3state (3-state still preferred — no new plateau emerged despite new categorical level) OR spacing_error_4state > 0.10.
- **MIDDLE BAND:** BIC_4state - BIC_3state ∈ (-30, 0) AND spacing_error ∈ [0.05, 0.10] (4th plateau marginally preferred — INCONCLUSIVE; needs higher-N reship).
- **INSTRUMENTATION-FAIL:** corpus-overlap construction does not produce a clean 4-stage-overlap class (i.e., 3-stage and 4-stage cluster together statistically) — re-design corpus before re-shipping.

**Why this is the cheap decisive test:** it tests Saad-Solla's *structural* prediction (more categorical levels → more equal-spaced plateaus) without needing to derive specific height values. It uses existing infrastructure. And it works as a falsifier in both directions: HARD-PASS gives strong evidence for saddle-cascade as the dominant mechanism; HARD-FAIL fundamentally weakens the framework's standing.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1 — plateau height arithmetic (Drill Q1)

**P1.1 (NEGATIVE finding — primitive structural mismatch).** Saad-Solla committee machines have plateau heights determined by integer-mode-overlap arithmetic among K student units summed at the output. Substrate's primitive is linear heteroassoc + Hebbian outer product + linear readout — NO summed-hidden-unit structure. The arithmetic is **structurally inapplicable to substrate** as-is. **HARD-FAIL prediction**: any attempt to derive 0.94/0.74/0.60 from a Saad-Solla closed form must FIRST extend the framework to the substrate primitive — currently undone. **Calibrated P (closed-form height prediction is achievable post-extension)** = 0.25.

**P1.2 (POSITIVE finding — equal-spacing IS predicted).** Saad-Solla's symmetric plateau in K-student / M-teacher committee gives EQUAL-SPACED plateau heights when permutation-orbits are equal-cardinality. Reanalysis spacing_error=0.0378 is consistent. **HARD-PASS**: equal-spacing extends to 4 corpora at spacing_error < 0.05. **HARD-FAIL**: spacing_error > 0.10 at 4 corpora. **Calibrated P (equal-spacing extends)** = 0.50 (at cap; novel-synthesis).

**P1.3 (Lit-scan honesty: PARTITION vs SHIFT plateau-count).** In soft-committee theory (Saad-Solla 1995, Engel-Van den Broeck textbook), plateau count = number of permutation-orbit classes in (teacher rank × student rank) overlap. For K=2 student, M=3 teacher, expect ≤ 3 plateaus. **Substrate analog**: number of plateaus = number of distinct overlap-classes in (corpus codebook × atom alphabet). For the existing 3-corpus design, this is 3. For a 4-corpus design, this should be 4. **Calibrated P (plateau count tracks corpus-overlap-class count)** = 0.42.

### Prediction set 2 — cleanest binary falsifier (Drill Q2)

**P2.1 (Equal-spacing at 4 corpora).** See section (b) — HARD-PASS / HARD-FAIL / MIDDLE bands fully pre-registered.

**P2.2 (Plateau-escape time scaling).** Saad-Solla theory: plateau duration τ_p ∝ 1/λ_min where λ_min is the smallest non-zero Hessian eigenvalue at the saddle. For symmetric plateau in committee machine of N inputs, λ_min ∼ 1/N giving τ_p ∼ N. For substrate (LINEAR-HETEROASSOC, no SGD trajectory) the analog is the Hebbian-update count to traverse a plateau. **HARD-PASS**: substrate retention-vs-stored-pattern-count curve shows τ_p ∝ N at fixed corpus-overlap-class (e.g., at the G2_MID plateau). **HARD-FAIL**: τ_p constant in N, or τ_p ∝ N^0 (would indicate different mechanism — e.g., information-theoretic plateau not dynamic-plateau). **Calibrated P** = 0.30 (deflated — substrate is not SGD-driven, so the dynamic-plateau mapping is heuristic).

**P2.3 (Plateau-height predictability from codebook-overlap histogram).** Concrete bridge to primitive-decision Mechanism A (`notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`, P=0.45): if linear + stratified codebook explains plateaus, the codebook-overlap histogram should show 3 modes at PPMI sparsities matching the 3 plateau cosines within ±0.05. **HARD-PASS for Mechanism A**: 3-mode histogram visible. **HARD-PASS for Saad-Solla (orthogonal mechanism)**: 3 modes also visible BUT they correspond to permutation-orbit cardinality, not codebook overlap. Falsifier between the two: measure how the mode positions shift under PPMI sparsity change. Mechanism A predicts: modes track sparsity continuously. Saad-Solla predicts: modes pin to integer orbit-cardinality positions, immune to sparsity. **Calibrated P (Saad-Solla wins this between-mechanism distinguish)** = 0.30.

### Prediction set 3 — K-tracking (Drill Q3)

**P3.1 (Plateau count tracks corpus-similarity-class count, NOT sequential-task count).** This is the most important sharp falsifier. Per Lee-Goldt-Saxe 2021 (`arXiv:2107.04384`, ICML PMLR v139), in multi-teacher CL, plateau structure tracks **task-similarity classes**, not task-count. Substrate analog: train at K=4 sequential tasks all drawn from the same corpus-similarity class (e.g., all "same-corpus" pairs); Saad-Solla predicts ONLY 1 plateau (the 0.94 plateau) since there's only 1 overlap class. **HARD-PASS**: K-sweep at fixed corpus-overlap-class shows constant plateau structure (no new plateau emerges at K=4, 5, 6). **HARD-FAIL**: new plateaus emerge with each new sequential task. **Calibrated P** = 0.45.

**P3.2 (Continual-learning behavior intermediate-similarity MAX forgetting).** Lee-Goldt-Saxe 2021 result: intermediate task-similarity → maximum forgetting. Substrate analog: the G2_MID plateau (0.74) should correspond to maximum cross-corpus forgetting; the G1_SAME (0.94) and G3_DIFF (0.60) should both show LOWER forgetting (different mechanisms — G1 from minimal interference, G3 from full task-isolation). **HARD-PASS**: directly measurable on existing Bet B 4-stage data — compute per-stage forgetting at SAME / 4-stage-overlap / DIFF and verify non-monotone (peak at MID). **HARD-FAIL**: monotone forgetting in similarity. **Calibrated P (non-monotone observed)** = 0.55. **NB**: existing Bet B v189 result retention_A=0.740, retention_B=0.854, retention_C=0.798 — already shows non-monotone retention with B (middle) HIGHEST not LOWEST, suggesting forgetting and retention non-monotonicity may differ between substrate and Lee-Goldt-Saxe SGD-trained students. **Honest caveat**: this discrepancy is itself diagnostic.

**P3.3 (4th plateau at K=4? NOT predicted automatically).** Saad-Solla cascade does NOT predict a 4th plateau just from adding a 4th sequential task; it predicts a 4th plateau when adding a 4th similarity-class. **HARD-PASS for the "automatic 4th plateau" naive prediction**: 4th plateau emerges in K=4 task sweep at fixed similarity-class. **HARD-FAIL for naive prediction (POSITIVE for Saad-Solla)**: no 4th plateau emerges. **Calibrated P (naive prediction is FALSE, supporting Saad-Solla)** = 0.55.

### Prediction set 4 — MoE rebuild informed by saddle-cascade (Drill Q4)

**P4.1 (SHIFT preserves per-expert cascade structure).** Each SHIFT expert is a full-N linear heteroassoc. Each expert sees a subset of queries; within that subset, queries fall into the 3 similarity classes; per-expert retention should show the 3-plateau structure. **HARD-PASS**: post-SHIFT-MoE, per-expert retention conditional on query-overlap-class shows 3 plateaus at heights consistent with 0.94/0.74/0.60 (within ±0.05). **HARD-FAIL**: per-expert retention is monotone or shows different plateau structure. **Calibrated P** = 0.42.

**P4.2 (PARTITION collapses cascade structure).** Sub-N experts have insufficient codebook rank to support 3 distinct permutation orbits. **HARD-PASS**: post-PARTITION-MoE (sub-N experts), per-expert retention shows ≤ 2 plateaus or smooth sigmoidal curve. **HARD-FAIL**: 3-plateau structure persists. **Calibrated P** = 0.40.

**P4.3 (Aggregate MoE retention is a MIXTURE of K cascades, not a deeper single cascade).** If K experts produce K independent saddle-cascades, aggregate retention is the *weighted average* of K cascade structures. For K=4 SHIFT experts each operating in the same 3-class regime, aggregate shows 3 plateaus (heights unchanged from single-substrate, by mixture-of-identical-distributions). For K=4 SHIFT experts each operating in a DIFFERENT similarity-class regime (e.g., specialist routing), aggregate could show up to 4 × 3 = 12 sub-plateaus — but more likely a smoother distribution from the mixture. **HARD-PASS for "K experts = K cascades, mixture-aggregated"**: aggregate retention follows mixture-of-3-plateau-distributions structure (testable via per-expert breakdown). **HARD-FAIL for "K experts = single K-times-deeper cascade"**: this naive PARTITION-like reading is unsupported by the theory and structurally inconsistent with SHIFT architecture. **Calibrated P** = 0.45.

### Prediction set 5 — Updated calibrated P (Drill Q5)

**Updated probability that Saad-Solla saddle-cascade is the dominant theoretical home for substrate retention plateaus.**

Evidence weighting:
- 3-state BIC delta=194.9 (very strong discrete-not-continuous): +0.20
- Equal-spacing within 0.038 (consistent with permutation-orbit cardinality): +0.10
- Lee-Goldt-Saxe 2021 published direct framework precedent: +0.05
- Shan-Li-Sompolinsky 2026 PNAS phase-transition CL framework matches: +0.05
- Mahdavi 2024 "compositional generalization requires linear orthogonal" matches substrate primitive lock: +0.03
- **NEGATIVE**: substrate primitive (linear heteroassoc, no SGD trajectory) is NOT a soft-committee SGD-trained network → framework structural mismatch: -0.10
- **NEGATIVE**: closed-form plateau height derivation NOT achievable (P1.1 above): -0.05
- **NEGATIVE**: alternative mechanism (linear + stratified codebook overlap, primitive-decision-note Mechanism A) explains the same evidence with P=0.45 — saddle-cascade has no decisive evidence advantage yet: -0.05
- Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (uncharted substrate regime): -0.15
- Novel-synthesis cap at 0.50: enforced.

Starting from prior P=0.46 (parent note):
- Pre-deflation: 0.46 + 0.20 + 0.10 + 0.05 + 0.05 + 0.03 - 0.10 - 0.05 - 0.05 = **0.69**
- Deflated by 0.15 (uncharted): 0.54
- Capped at 0.50: **0.48** (chose 0.48 not 0.50 to leave one tick of room and honor the strict cap)

**Calibrated P(Saad-Solla saddle-cascade is the dominant theoretical home) = 0.48.**

Three nearest-neighbor competitors:
- **Mechanism A: Linear + stratified codebook overlap** (primitive-decision note, P=0.45) — COMPATIBLE not COMPETITIVE; could BE the substrate-level realization of the saddle-cascade phenomenology.
- **Information Bottleneck phase transitions** (parent note candidate iv, P=0.42) — competitor; K-sweep falsifier distinguishes it from saddle-cascade.
- **1-RSB** (former leader, demoted) — Pred-4 verdict still pending; if HARD-PASSes, becomes coexisting framework; if HARD-FAILs, definitively superseded by Saad-Solla.

**Honest framing**: Saad-Solla is the LEADING candidate, but the gap to nearest competitors (0.48 vs 0.45 Mechanism A vs 0.42 IB) is **within the calibration-penalty noise floor**. The reanalysis evidence is necessary-but-not-sufficient. The decisive falsifier is the 4-corpus equal-spacing test (section b).

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to parent alternative-homes drill (`notes/research_alternative_theoretical_homes_2026-05-24.md`)

The parent rated Saad-Solla at P=0.46, slightly above IB phase-transitions (P=0.42). Tonight's reanalysis (CASCADE_PASS, BIC delta=194.9) elevates to leading position. This drill confirms the elevation BUT identifies a calibration ceiling: novel-synthesis cap at 0.50, plus structural mismatch between SGD-trained committee and Hebbian-trained substrate primitive, holds the updated P below the original baseline 0.60. **Net update: +0.02 from parent (0.46 → 0.48).**

### Cross-ref to primitive-decision drill (`notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`)

The primitive decision LOCKED linear-heteroassoc. This drill is **compatible** with that lock: Saad-Solla cascade phenomenology can sit ON TOP of a linear primitive (the cascade is a learning-dynamics observation; the linear primitive is the retrieval mechanism). The two notes are NOT in tension. The primitive-decision note's Mechanism A (linear + stratified codebook overlap, P=0.45) is **substrate-level mechanism**; Saad-Solla cascade is **phenomenological framework**. Both can be simultaneously true — this is the architecturally cleanest reading. **Falsifier between them**: PPMI-sparsity sweep — Mechanism A predicts mode positions shift continuously with sparsity; Saad-Solla predicts mode positions pin to integer-orbit positions immune to sparsity (P2.3 above).

### Cross-ref to MoE rebuild handoff (`notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md`)

The MoE rebuild handoff specifies SHIFT-vs-PARTITION-vs-SINGLE 3-arm design but does NOT include per-expert-cascade-structure instrumentation. **Add to MoE rebuild instrumentation list** (companion handoff for this drill specifies what to add):
- Per-expert retention conditional on query-overlap-class (3 classes: same/partial/disjoint from each expert's stored content distribution).
- Per-expert plateau-structure BIC comparison (3-state vs sigmoid).
- Aggregate-MoE retention plateau-structure decomposition into per-expert mixture.

These instruments cost almost nothing to add (compute is free given the experiment already retrieves all items), but enable a NEW falsifier dimension that distinguishes SHIFT from PARTITION at the cascade level, ORTHOGONAL to the existing M_c / Gini / PAC-Bayes-floor instruments.

### Cross-ref to Lee-Goldt-Saxe 2021 (`arXiv:2107.04384`)

Direct lit-precedent for multi-teacher continual-learning cascade structure with task-similarity-class tracking. Their non-monotone forgetting result (intermediate task similarity → max forgetting) maps onto substrate's 3-tier retention structure. **Open question**: Bet B v189 shows retention_A=0.740 < retention_B=0.854 (B middle, B HIGHEST not LOWEST). This is the OPPOSITE of Lee-Goldt-Saxe's "intermediate similarity → max forgetting" if forgetting = (1 - retention). One reading: substrate's per-stage retention is NOT the right analog of LGS's per-task forgetting — substrate measures retention of the *first* task after subsequent tasks, while LGS measures forgetting of an *intermediate* task. The discrepancy needs reconciliation; possibly a falsifier in its own right. Filed as Q-for-strategy.

### Cross-ref to Shan-Li-Sompolinsky 2026 PNAS (`arXiv:2407.10315`; doi 10.1073/pnas.2501899123)

"Order parameters and phase transitions of continual learning in deep neural networks" — published Feb 2026; identifies phase transitions in multi-head CL where performance shifts abruptly with task-similarity order parameter. **Direct framework analog for substrate's 3-plateau structure.** Note: their result is for *deep* networks, not linear heteroassoc — applicability to substrate is via the order-parameter framework, not the specific architecture. **This is the strongest lit-precedent for "discrete plateau structure as the natural reading of CL retention dynamics."**

### Cross-ref to Mahdavi 2024 (`arXiv:2402.02851`)

"Compositional Generalization Requires Linear, Orthogonal Representations" — supports the primitive-decision lock on linear-heteroassoc AND aligns with Saad-Solla's prediction that compositional behavior (the cascade across categorical levels IS a form of compositional generalization across similarity classes) emerges from linear representations. **Triangulation**: substrate's auditable-third-memory wedge requires linear primitive (per primitive-decision lock), and Saad-Solla cascade reading is internally consistent with this primitive choice. No tension.

### Cross-ref to Pred-4 hysteresis (1-RSB load-bearing test)

Pred-4 (1-RSB hysteresis gap ≥ 0.10) is STILL the load-bearing test for the 1-RSB framework. This drill does NOT supersede Pred-4. Decision matrix (from parent note `notes/research_alternative_theoretical_homes_2026-05-24.md` section "Decision logic vs. Pred-4 verdict"):

| Pred-4 outcome | Saad-Solla status |
|---|---|
| HARD-PASS | 1-RSB recovers partially. Saad-Solla framework SUPERPOSED — both can coexist. Ship 4-corpus falsifier anyway. |
| HARD-FAIL | 1-RSB dead. Saad-Solla becomes PRIMARY theoretical home. Ship 4-corpus falsifier as confirmation. |
| MIDDLE-BAND | Inconclusive. Ship 4-corpus falsifier; if HARD-PASS, Saad-Solla becomes primary; if HARD-FAIL, both frameworks weak. |

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

**1. Three-plateau retention IS the auditable signature** — already established in primitive-decision note. Saad-Solla framework REINFORCES this by giving the plateau structure a learning-dynamics mechanism: the plateaus correspond to permutation-orbit classes in the substrate's codebook × atom-alphabet overlap distribution. **Product implication**: the 3-tier retention signal can be EXPLAINED to users via "the substrate naturally clusters retrieval reliability into 3 confidence tiers based on input-overlap similarity to stored content" — a clean product-grade narrative that doesn't require glassy-phase or RSB technicalities.

**2. K-tracking implication for product UX**: per Drill Q3, NEW plateaus only emerge when NEW similarity-classes are introduced. **Product implication**: as users add more documents/corpora to the substrate, the 3-tier signal does NOT degrade or fragment automatically — it remains stable until users introduce a structurally new content category. This is a STABILITY guarantee that no other framework provides cleanly.

**3. MoE rebuild product implication**: SHIFT architecture preserves the 3-plateau signal per-expert, enabling **per-expert audit tiers**. PARTITION architecture collapses the signal. **Product implication**: SHIFT is the architecturally correct choice for the auditable-third-memory product wedge, INDEPENDENT of the M_c / capacity argument (which already favors SHIFT). Saad-Solla framework gives a SECOND, ORTHOGONAL reason to choose SHIFT — the audit signal preservation. Two independent arguments for the same architectural choice is much stronger than one.

**4. The 4-corpus falsifier is product-relevant, not just theory-relevant.** If Saad-Solla framework HARD-PASSES on 4-corpus, the substrate can advertise "scales to N tiers automatically based on user content structure." If HARD-FAIL, the product narrative pivots to "exactly 3 audit tiers as a hard-coded design" — also a valid (if less impressive) product narrative.

**5. Compositional generalization angle (Mahdavi 2024)**: substrate's linear primitive + Saad-Solla cascade reading = "the substrate's compositional behavior across similarity classes is a built-in side effect of the linear-orthogonal representation choice." **Product implication**: compositional retrieval (assembling information from different similarity tiers into a unified output) is a native feature, not an add-on — a substantive product differentiation from monolithic LLM memory.

---

## (f) Citations (verified count: 12 direct + 4 contextual = 16)

### Saad-Solla saddle-cascade foundational
- **Saad, Solla 1995** — Phys. Rev. E 52:4225 — "On-line learning in soft committee machines". The plateau-cascade closed form: `ε_g = 1/6 + (1/π) Σ_{ij} [arcsin(Q_ij/2) − 2 arcsin(R_ij/2)]`. https://journals.aps.org/pre/abstract/10.1103/PhysRevE.52.4225
- **Saad, Solla 1995 NIPS** — "Dynamics of On-Line Gradient Descent Learning for Multilayer Neural Networks" — analytical fixed-point solutions for symmetric plateau. https://proceedings.neurips.cc/paper_files/paper/1995/hash/a1519de5b5d44b31a01de013b9b51a80-Abstract.html
- **Biehl, Schwarze 1995** — J. Phys. A 28:643 — phase transitions in soft-committee training.
- **Saad, Rattray 1997** — cond-mat/9706015 — "Functional Optimisation of Online Algorithms in Multilayer Neural Networks" — plateau-elimination via symmetry-breaking optimization.
- **Phase transitions in soft-committee machines** — cond-mat/9805182 — K=2 second-order, K≥3 first-order specialization transitions.
- **Goldt, Advani, Saxe, Krzakala, Zdeborová 2019** — `arXiv:1901.09085` / NeurIPS 2019 — "Generalisation dynamics of online learning in over-parameterised neural networks". Modern revisit of plateau dynamics. PMC7685244.
- **Unified Description of Learning Dynamics in the Soft Committee Machine** — `arXiv:2512.16556` — finite to ultra-wide regime; over-realizable plateau height monotone-convergent with M.
- **Soft mode in over-realizable on-line learning** — `arXiv:2104.14546` — K≥M regime plateau structure.
- **Continuous specialization transition in SCM with ReLU** — `arXiv:2603.20010` — alternative activation function plateau structure.

### Continual learning + multi-teacher cascade (direct lit-precedent for K-tracking)
- **Lee, Goldt, Saxe 2021** — `arXiv:2107.04384` / PMLR v139 — "Continual Learning in the Teacher-Student Setup: Impact of Task Similarity". Direct precedent for multi-teacher plateau cascade with task-similarity-class tracking. KEY RESULT: intermediate task similarity → max forgetting (non-monotone). https://proceedings.mlr.press/v139/lee21e.html
- **Shan, Li, Sompolinsky 2026** — PNAS 122:e2501899123 / `arXiv:2407.10315` — "Order parameters and phase transitions of continual learning in deep neural networks". Phase transitions in multi-head CL; direct framework analog. https://www.pnas.org/doi/10.1073/pnas.2501899123
- **Curves for Continual Learning in NTK** — `arXiv:2112.01653` — generalization analysis of continual learning in NTK regime.

### Compositional generalization (supports primitive-decision lock)
- **Mahdavi 2024** — `arXiv:2402.02851` — "Compositional Generalization Requires Linear, Orthogonal Representations". Direct precedent for substrate's linear-heteroassoc primitive.

### Saddle-to-saddle dynamics (recent cross-framework lit)
- **Saddle-to-Saddle Dynamics Explains a Simplicity Bias Across Neural Network Architectures** — `arXiv:2512.20607` — stage-like dynamics with plateaus alternating with rapid improvement bursts; cross-architecture confirmation of cascade phenomenology.

### Contextual / methodological
- **Pascanu et al. 2014** — `arXiv:1405.4604` — Identifying and attacking the saddle point problem in high-dimensional non-convex optimization.
- **Engel, Van den Broeck 2001** — *Statistical Mechanics of Learning*, Cambridge — textbook treatment of order-parameter cascade dynamics.
- **Noise-induced degeneration in online learning** — `arXiv:2008.10498` — escape from degenerate subspaces, optimal noise minimization.
- **High-dimensional dynamics of generalization error** — `arXiv:1710.03667` — order parameter ODEs for SGD.

### Substrate-internal references
- `notes/research_alternative_theoretical_homes_2026-05-24.md` (parent — Saad-Solla rated P=0.46 baseline).
- `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` (primitive lock LINEAR-HETEROASSOC).
- `notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md` (MoE rebuild 3-arm SHIFT/PARTITION/SINGLE — companion instrumentation in this drill).
- `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/metrics.json` (CASCADE_PASS).
- `data/exp_wave14_betB_4stage_continual_v1/metrics.json` (Bet B v189 retention_A=0.740, B=0.854, C=0.798).
- `notes/substrate_capability_map.md` (cap_map Bet B M-DEPENDENT PARTIAL row).

---

## Self-audit per [[feedback-verify-implementations]]

- **Saad-Solla 1995 closed form spot-checked**: `ε_g = 1/6 + (1/π) Σ_{ij} [arcsin(Q_ij/2) − 2 arcsin(R_ij/2)]` confirmed from `arXiv:2603.20010` and cond-mat/9812197. ✓
- **Equal-spacing claim** spot-checked: at the symmetric plateau (R_ij permutation-symmetric), Saad-Solla gives equal-distance plateau heights when permutation orbits are equal-cardinality; this is a textbook result (Engel-Van den Broeck 2001, Ch. 6). ✓
- **Lee-Goldt-Saxe 2021 main result** spot-checked: arXiv abstract confirms "intermediate task similarity leads to greatest forgetting" — direct framework precedent. ✓
- **Shan-Li-Sompolinsky 2026 PNAS** spot-checked: arXiv abstract confirms "phase transition where CL performance shifts dramatically as tasks become less similar". ✓
- **Mahdavi 2024 result** spot-checked: title and abstract confirm linear-orthogonal claim for compositional generalization. ✓
- **K=2 second-order, K≥3 first-order specialization** spot-checked: cond-mat/9805182 abstract confirms. ✓
- **Closed-form for substrate plateau heights** NOT achievable: primitive structural mismatch (single-shot linear readout vs summed committee output) — verified by inspection of substrate primitive in `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` lines 12-24.

Probability all framework attributions correct: 90%.
Probability all P(fit) numbers are honest after calibration penalty: 80%.
Probability the closed-form non-derivability finding (P1.1) is correct: 85%.

---

## Brutal-honesty caveats per [[feedback-no-smoke]]

1. **P=0.48 is BELOW 0.50** — Saad-Solla is the LEADING candidate but not a confirmed framework. The reanalysis evidence (BIC=194.9, spacing within 0.038) is *necessary but not sufficient* — Mechanism A (linear + stratified codebook) explains the same evidence with P=0.45 and the gap is within calibration-penalty noise. **DO NOT** treat Saad-Solla as confirmed; ship the 4-corpus falsifier.

2. **Closed-form plateau height derivation is NOT achievable** — substrate primitive structurally mismatches Saad-Solla committee architecture. P=0.48 is **structural-fit confidence**, NOT **closed-form-derivation confidence** (which is P=0.25 per P1.1). User asked specifically whether the arithmetic outputs 0.94/0.74/0.60 — the honest answer is **no**, not without first extending the framework to linear heteroassoc + Hebbian outer product (an open theoretical task).

3. **Lee-Goldt-Saxe forgetting non-monotonicity does NOT match Bet B v189** — LGS predicts intermediate-similarity → MAX forgetting (B retention LOWEST); Bet B v189 shows B retention HIGHEST. This is a substantive discrepancy that the framework needs to explain. Filed as open question — could be diagnostic.

4. **The 4-corpus falsifier (section b) is the load-bearing experiment.** If it HARD-FAILs, P drops to ~0.30 and saddle-cascade becomes secondary. If MIDDLE-BAND, P stays near 0.48 and we need higher-N reship. If HARD-PASS, P rises to 0.55 (above novel-synthesis cap because then it's lit-PROVEN not just lit-INFORMED).

5. **Lit-scan calibration penalty applied uniformly** — all P values deflated 0.15-0.25 per uncharted-substrate-regime rule. The 0.50 novel-synthesis cap is respected throughout.

6. **No new GPU spend for this drill itself** — closure on existing evidence + 1 cheap CPU 4-corpus falsifier (the companion handoff). No substrate rebuild.

7. **The MoE-rebuild Drill Q4 finding (SHIFT preserves cascade, PARTITION collapses) is a NEW prediction** — instrumentation cost is near-zero (just group existing retrievals by overlap-class). If implemented before MoE rebuild ships, this adds a powerful orthogonal falsifier dimension. Companion handoff specifies it.

8. **Per [[feedback-no-experiment-design-in-prompts]]**: the companion handoff hands TASK + WHY + CONTRACT + AUTONOMY only. No anchor names, no sweep grids, no threshold formulas embedded, no queue choice — exp_dev decides those. The pre-registered bands (HARD-PASS/HARD-FAIL/MIDDLE/INSTRUMENTATION-FAIL) ARE specified per [[feedback-envelope-expansion-fail-bands]].

9. **The 1-RSB Pred-4 verdict is STILL load-bearing** — this drill does NOT close 1-RSB; it elevates Saad-Solla to leading position. Both frameworks can coexist post-Pred-4-HARD-PASS.

---

**End research note.**
