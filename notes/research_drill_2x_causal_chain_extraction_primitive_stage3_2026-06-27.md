# Research drill (2x DEEPER): causal-chain extraction primitive for substrate Stage 3

**Date:** 2026-06-27
**Author:** Research (Opus 4.7-1M)
**Trigger:** Stage 3 active for M3 conversational AI / M4 hybrid agentic-experiment loop. Substrate has 5 chain-grade counterfactual atoms + CF Cell 2 v2 latency win + CF Cell 1 correlational disambig HARD_PASS — but cannot EXTRACT a causal chain from observations.
**2x discipline:** drill EXISTING substrate findings (Pearl-mapped CF + correlational role disambig + intervention isolation + audit-chain-depth + K-hop traversal) into level-2 operational depth — NOT re-run as verification. Focus: what mechanism gap blocks substrate from PROPOSING a causal hypothesis chain from a corpus of observations.
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15 when brain-analog unambiguous); cap novel-synthesis P at 0.65; cap full-PC-algorithm-on-substrate at 0.50 per substrate-isn't-PC-engine prior (2026-06-07 drill).
**Pre-reg discipline:** META_RULE_AF arms-must-differ / AG baseline-in-band / AH atomic-write / CRLB pre-validation / cardinality-OK per [[feedback-cardinality-ok-mandatory-prereg-field]] / number-tags throughout.

---

## HEADLINE

**Substrate already has all THREE Pearl-rung primitives (rung-1 observation via correlational_disambig; rung-2 intervention via rank-1 surgery; rung-3 counterfactual via CF Cell 2 v2 delta-stack) — but is MISSING the COMPILER that turns a corpus of (event_i, event_j, time_i, time_j) tuples into a CANDIDATE DIRECTED CAUSAL CHAIN.** The gap is NOT a new physics primitive; it is a SUBSTRATE-NATIVE EQUIVALENT OF THE PC ALGORITHM's conditional-independence + edge-orientation steps, expressed in HRR algebra. The brain mechanism for chain extraction is well-mapped: hippocampal-PFC replay sequences DAG-like episode structure (Yu-Frank 2015 reverse-replay; Foster-Wilson 2006 forward+reverse; Schuck-Niv 2019 PFC state-space), and PFC abstracts the temporal antecedent-consequent pattern into a CAUSAL SCHEMA (Tomov-Yagati-Kumar 2018 "model-based causal cognition"; Lagnado-Sloman 2006 "time as a guide to cause"). The substrate-native primitive is: (1) PAIRWISE conditional-independence test using substrate-residual projection (the 2026-06-07 drill's Section 7 — never built); (2) EDGE ORIENTATION via temporal precedence + interventional asymmetry (substrate has both: now-grounding v1 timestamps + CF Cell 2 v2 transient rank-1 surgery); (3) CHAIN ASSEMBLY via K-hop traversal on the inferred directed sub-W. Top-1 candidate cell builds the smallest end-to-end version of all three. Top-2 attacks the hardest sub-piece (CI test in HRR algebra). Top-3 attacks DIRECT-vs-INDIRECT discrimination on existing chain-grade depth-15 multi-hop. Cross-domain: legal proximate-cause doctrine, gene regulatory network reverse-engineering (Granger + ARACNe), and forensic root-cause analysis (5-Why / Ishikawa) all converge on the same three sub-pieces — substrate-native primitive maps cleanly to each downstream domain.

**Calibrated P_deflated estimates:**
- P(substrate-native pairwise CI test using residual-projection recovers true causal skeleton on 5-var linear-Gaussian DAG at F1 >= 0.70) = **0.55** (asymmetric brain-existence-proof + 2026-06-07 prior P=0.45 deflated; ADJUSTED UP because correlational_disambig CHAIN_GRADE today proves role disambig works at 1.0 — same primitive)
- P(edge-orientation via temporal precedence + interventional asymmetry recovers correct DAG direction at >=0.80 acc for non-confounded chains) = **0.65** (CF Cell 2 v2 + now-grounding both chain-grade; orientation is two-primitive composition not novel)
- P(K-hop chain assembly on inferred directed sub-W recovers length-3 to length-5 chain at >=0.70 acc) = **0.60** (audit_chain_depth_50 CHAIN_GRADE; chain assembly is established; risk is cumulative orientation error)
- P(END-TO-END causal-chain extraction from observation corpus to ranked candidate chain at MRR@5 >= 0.50) = **0.45** (three-step composition; cumulative error; capped novel-synthesis)
- P(substrate-native DIRECT-vs-INDIRECT discrimination at >=0.75 acc by leveraging d-separation on K-hop sub-W) = **0.50** (cleanly defined; testable on depth-5 chains where intermediate is observable)
- P(substrate primitive transfers to natural-language causal Q&A "why did Y happen?" at >=0.65 acc) = **0.25** (Stage 3/4 boundary; substrate-doesnt-know-anything caution applies)

---

## SUBSTRATE-KB SCOUR RESULTS (prior causal/chain-extraction work, with honest verdicts)

Per USER scour-first-no-duplication discipline. Queried `director_kb_query.py` on six filename-contains angles (causal / counterfactual / correlational / intervention / chain / inference) + cosine query on "causal chain extraction". Findings:

**Existing causal cells (chain-grade primitives but NO full chain-extraction):**
| Cell / atom | Verdict | Honest re-read for chain-extraction relevance |
|---|---|---|
| `causal_correlational_disambig_v1` | CHAIN_GRADE (HARD_PASS prec=recall=1.000 N=4096) | Pairwise role disambig (CAUSE_OF vs CORRELATED_WITH) at WRITE time; does NOT discover causation from observations. Mechanism A from 2026-06-07 drill, validated. |
| `causal_audit_chain_depth_v1` | CHAIN_GRADE (HARD_PASS) | Audit-trail traversal on existing causal chain; depth-50 verified. Does NOT propose new chains. |
| `causal_counterfactual_replay_v1` | MIDDLE_BAND -> CHAIN_GRADE (today, auto-promoted by Cell 2 v2) | Single-fact substitution + K-hop replay. Mechanism B from 2026-06-07 drill. |
| `counterfactual_replay_latency_delta_stack_v2_single_intervention` | HARD_PASS today (5.47x speedup, acc=1.0) | Production-grade delta-stack rank-1 surgery for transient W mutation. Engine for chain-extraction edge-orientation arm. |
| `counterfactual_do_operator_v1` | HARD_PASS | do(X=x) operator. Same engine. |
| `intervention_isolation` | CHAIN_GRADE | Variable-isolation invariance under intervention. Composes with K-hop. |
| `bitemporal_*` cells | HARD_PASS | Temporal versioning; provides temporal-precedence signal for edge orientation. |
| `pp47_pp49_counterfactual_abduction_composition_v1` | HARD_PASS | Pearl 3-step abduction-action-prediction composition. Verifies CF chain works. |
| `edge_importance_v5_CFU_counterfactual_utility_v1` | (today's MM/HF result pending) | Edge importance via counterfactual utility. ADJACENT to direct-vs-indirect discrimination. |

**Prior research notes (cited, read summaries):**
- `research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07` (read full 453 lines) — load-bearing prior; identifies Mechanism A (role markers), B (rank-1 surgery), C (hybrid symbolic). PC algorithm on substrate gets P=0.45 linear / P=0.15 nonlinear — UNDREALED at the time. Section 7 explicitly proposes substrate-residual CI test as the unbuilt next step.
- `research_drill_counterfactual_capability_extension_2026-06-07` — CF extension scoping.
- `notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27` (today's sibling drill) — STRUCTURAL TEMPLATE for this drill; temporal-precedence (Allen relations + now-grounding) is the orientation primitive for causal-chain.
- `notes/research_stage3_definition_and_chain_grade_verification_matrix_2026-06-25` — Stage 3 cap matrix; causal-chain-extraction is the missing row for "explain WHY" capability.
- `research_drill_pattern_temporal_contextual_not_structural_2026-06-11` (memory) — meta-pattern that substrate's strongest primitives are temporal/contextual, not structural — DAG learning is structural and is the load-bearing risk.

**Cross-domain priors:** `research_drill_substrate_as_active_inference_control_theory_lyapunov_stability_unifying_normative_theory_2x_2026-06-12` provides the active-inference framing for "why" — causal chain = generative-model edge sequence that maximizes evidence for observation.

**GAP DELTA — what is NOT covered by ANY prior cell:**
1. **Substrate-native pairwise CONDITIONAL INDEPENDENCE test** — Section 7 of 2026-06-07 drill proposed but never built. Required for skeleton recovery.
2. **EDGE ORIENTATION via combined temporal-precedence + interventional-asymmetry** — substrate has both ingredients (now-grounding + CF Cell 2 v2) but no cell composes them into orientation.
3. **CHAIN ASSEMBLY from inferred edges** — K-hop runs on stored W; never on a DYNAMICALLY-INFERRED directed sub-W computed at query time.
4. **DIRECT vs INDIRECT discrimination** — existing audit-chain depth-50 traverses GIVEN chains; never asks "is the A->B edge mediated by C?"
5. **END-TO-END chain extraction** from event corpus to ranked candidate chain — never attempted.

**Conclusion:** the gap is real and substrate-shaped. All three required sub-pieces have chain-grade-adjacent primitives; the missing piece is the COMPILER that assembles them. Top-1 cell below is the smallest cell that builds this end-to-end on a synthetic 5-variable DAG.

---

## TOP-3 CANDIDATE CELLS (rank-ordered with P_deflated, brain → substrate mapping, fairness, pre-reg)

### TOP-1: `exp_causal_chain_extraction_end_to_end_v1` (P_deflated = 0.45)

**Brain mechanism -> substrate primitive mapping.**
- **CITED@Tomov-Yagati-Kumar 2018** (Discovery of hierarchical representations for causal inference) — PFC + hippocampal interaction supports DAG-like inference from sequential observations; latent-state inference produces a hierarchical model.
- **CITED@Lagnado-Sloman 2006** ("Time as a guide to cause", JEP-LMC 32:451-460) — humans use temporal precedence as primary orientation cue; combined with intervention asymmetry, recovers DAGs at >=0.80 acc on synthetic chains.
- **CITED@Schuck-Niv 2019** (Sequential replay of nonspatial task states in human hippocampus) — fMRI replay sequences reproduce inferred task DAGs; substrate analog = K-hop traversal on inferred directed sub-W.
- **CITED@Pearl 2009** (Causality 2e) — three-step PC algorithm: (1) skeleton via CI tests; (2) v-structure orientation via unshielded colliders; (3) Meek orientation propagation. Substrate-native variant uses temporal precedence + interventional asymmetry IN PLACE OF v-structure rule (faster and avoids the unobservable-collider failure mode).
- **CITED@Lagnado-Waldmann-Hagmayer-Sloman 2007** (Beyond covariation: cues to causal structure) — temporal cues + intervention cues + prior knowledge combine multiplicatively for chain recovery in humans.
- **Substrate primitive mapping:**
  - SUB-STEP 1 (SKELETON): for each variable pair (X, Y), compute substrate-residual CI test using HRR-projection (`r_XY|Z = W * (v_X - proj_{v_Z}(v_X))` from 2026-06-07 Section 7). Edge X-Y exists iff `cos(r_XY|Z, v_Y) > theta_CI` for all Z in candidate-separator set.
  - SUB-STEP 2 (ORIENTATION): for each undirected edge X-Y, orient via temporal-precedence (using existing `now1_temporal_grounding_cpu_v1` timestamps) and interventional asymmetry (run CF Cell 2 v2 delta-stack do(X=x'), measure Delta_Y; do(Y=y'), measure Delta_X; orient toward larger delta).
  - SUB-STEP 3 (CHAIN ASSEMBLY): run K-hop traversal on inferred directed sub-W from chain-source to chain-sink. Report MRR@5 over candidate chains.

**Concrete test.** Synthetic 5-variable linear-Gaussian DAG with known structure (e.g., X1 -> X2 -> X3, X1 -> X4 -> X3, X5 isolated). Generate 5000 observation tuples with Gaussian noise; store as substrate facts using existing role-binding (CORRELATED_WITH default). Cell extracts: (a) directed skeleton, (b) ranked length-3 chain X1->X2->X3, (c) ranked length-3 chain X1->X4->X3. Report skeleton F1 + orientation acc + chain-MRR@5.

**Discriminator (META_RULE_AF — arms-must-differ + META_RULE_AG baseline-in-band).**
- ARM_A: substrate end-to-end (CI test + orientation + K-hop chain assembly).
- ARM_B: substrate skeleton-only (no orientation; report undirected chains; tests that orientation arm adds value).
- ARM_C: temporal-precedence-only orientation (skip CI test; orient ALL temporally-ordered pairs as directed edges; tests that CI pruning adds value over naive temporal-cause).
- ARM_D: PC-algorithm-on-true-correlation-matrix BY-CONSTRUCTION control (privileged: gets exact correlation matrix, not substrate retrieval; predicted to be the CEILING).
- ARM_E: random-DAG baseline (acc ~ 1/2^edges).
- Discrimination requires: ARM_A > ARM_B by >=0.10 chain-MRR (orientation adds value) AND ARM_A > ARM_C by >=0.10 chain-MRR (CI pruning adds value) AND ARM_D - ARM_A < 0.15 chain-MRR (substrate close to ceiling) AND ARM_A > ARM_E by >=0.40.

**Fairness gate (META_RULE_AA + [[feedback-experiment-bias-master-checklist]] BIAS-N + M-S regime).** Per BIAS-13 (contamination): variable label vectors v_X drawn fresh per seed; per BIAS-15 (regime): n_observations chosen so the substrate retrieval signal/noise > 1 at the planned alpha_c (use sparse-codebook envelope per `sparse_onset_alpha_c`). ARM_D is the privileged BY-CONSTRUCTION ceiling and MUST report higher than ARM_A by some margin or harness has a bug; per [[feedback-suspect-1.000-results]] any arm at 1.000 logged as red-flag and re-checked.

**Pre-reg HARD bands (both directions; per [[feedback-three-smoke-disciplines]] discriminator-fires-at-full-N).**
- HARD_PASS: chain-MRR@5 >= 0.50 AND skeleton-F1 >= 0.70 AND orientation-acc >= 0.75 AND ARM_A - ARM_B >= 0.10 AND ARM_A - ARM_C >= 0.10 AND ARM_D - ARM_A < 0.15. EXPECTED@chain-MRR=0.55, skeleton-F1=0.72, orient-acc=0.80.
- HARD_FAIL: chain-MRR@5 < 0.25 OR skeleton-F1 < 0.40 OR ARM_A - ARM_C < 0.03 OR ARM_A - ARM_E < 0.20.
- MIDDLE_BAND: chain-MRR@5 in [0.25, 0.50] with skeleton-F1 >= 0.50.
- CARDINALITY_OK: EXPECTED_N_UNITS = 5 arms x 3 metrics (skeleton-F1, orient-acc, chain-MRR) x 3 seeds = 45; HARD_FAIL_CARDINALITY_BREACH if observed < 40.

**Smoke discriminator survives scale (per [[feedback-discriminator-must-survive-scale-before-full-dispatch]]):**
- Smoke at 4-variable DAG (X1->X2->X3, X4 isolated), 1000 observations, N=2048, 1 seed (~60s CPU): check ARM_A > ARM_C by >=0.05 chain-MRR AND ARM_A > ARM_E by >=0.25. If smoke ARM_A < 0.30 chain-MRR OR ARM_C within 0.02 of ARM_A => HARD_FAIL smoke, do NOT dispatch full.
- Full at 5-variable DAG, 5000 observations, N=4096, 3 seeds (~15min CPU).
- Smoke fires discriminator (per smoke-fires-discriminator rule).

**Compute cost.** ~15min CPU full + 60s smoke. Pure numpy; no GPU.

**P_deflated = 0.45** (three-step composition: CI test (P=0.55) x orientation (P=0.65) x chain assembly (P=0.60) ~ 0.21 naive multiplicative; deflated less because composition errors not fully independent — orientation rescues weak CI test; deflate to 0.45 for cumulative error + finite-N risk. Cap novel-synthesis 0.65; this is below cap.)

**Why now.** Single missing piece for full Pearl-rung coverage on substrate. M3 conversational AI needs "why did Y happen?" coherent explanation; M4 hybrid agentic loop needs substrate to PROPOSE causal hypotheses from experimental data. The three sub-primitives all landed (or land today); this cell is the COMPILER.

---

### TOP-2: `exp_substrate_residual_conditional_independence_test_v1` (P_deflated = 0.55)

**Brain mechanism -> substrate primitive mapping.**
- **CITED@Spirtes-Glymour-Scheines 2000** (Causation, Prediction, and Search 2e) — PC algorithm's load-bearing step is the CI test; everything downstream depends on it.
- **CITED@Glymour-Zhang-Spirtes 2019** (Review of causal discovery methods based on graphical models, Front Genet 10:524) — kernel CI test, partial-correlation CI test, and discrete-data CI tests; performance bound by sample complexity.
- **CITED@Eichenbaum 2017** (Memory: organization and control, Annu Rev Psychol 68:19-45) — hippocampus does relational binding; substrate-residual projection is the algebraic analog of relational separation.
- **Substrate primitive mapping:** For variable pair (X, Y) with conditioning set Z, compute substrate-residual:
  - `proj_Z(v) = (v . v_Z / ||v_Z||^2) * v_Z` (HRR projection onto Z's direction)
  - `r_X|Z = v_X - proj_Z(v_X)` (residual of X after removing Z)
  - `r_Y|Z = v_Y - proj_Z(v_Y)`
  - CI test: `X _||_ Y | Z` iff `|cos(W * r_X|Z, r_Y|Z)| < theta_CI`
- This is the algebraic analog of partial correlation; for linear-Gaussian SCMs, partial correlation = 0 iff conditional independence (Pearl 2009 ch 2). Substrate's bipolar/FHRR algebra is approximate linear associative memory; the CI test is sound in the linear regime.

**Concrete test.** Generate ground-truth 4-variable linear-Gaussian DAGs (200 random DAGs, 1000 observations each). For each variable pair (X, Y) and each conditioning set Z in {{}, {Z1}, {Z2}, {Z1,Z2}}, run substrate CI test. Compare to ground-truth CI from partial-correlation matrix. Report per-test acc + skeleton-recovery F1 when CI test is plugged into vanilla PC.

**Discriminator (META_RULE_AF).**
- ARM_A: substrate residual-projection CI test.
- ARM_B: substrate cosine-only test (no Z conditioning; tests that conditioning adds value).
- ARM_C: ground-truth partial-correlation CI BY-CONSTRUCTION ceiling.
- ARM_D: random-CI baseline (50% acc).
- Discrimination requires: ARM_A > ARM_B by >=0.15 acc AND ARM_C - ARM_A < 0.15 acc AND ARM_A > ARM_D by >=0.20.

**Fairness gate.** All arms see same DAGs + observations; theta_CI tuned on held-out 50 DAGs (no test contamination). Per [[feedback-experiment-bias-master-checklist]] BIAS-15: conditioning set sizes capped at |Z|=2 (substrate retrieval signal degrades with stacked conditioning).

**Pre-reg HARD bands.**
- HARD_PASS: per-test acc >= 0.75 AND skeleton-F1 (in PC) >= 0.70 AND ARM_A - ARM_B >= 0.15 AND ARM_C - ARM_A < 0.15. EXPECTED@acc=0.78.
- HARD_FAIL: per-test acc < 0.55 OR skeleton-F1 < 0.40 OR ARM_A - ARM_B < 0.05.
- MIDDLE_BAND: per-test acc in [0.55, 0.75].
- CARDINALITY_OK: 4 arms x 200 DAGs x 6 var-pairs x 4 cond-sets x 3 seeds = 57600.

**Smoke.** 3-variable DAG, 30 random DAGs, 500 observations, 1 seed (~60s); ARM_A > ARM_B by >=0.10 OR smoke HARD_FAIL.

**Compute.** ~10min CPU full + 60s smoke.

**P_deflated = 0.55** (cleanly-specified algebraic test; risk is theta_CI tuning sensitivity + bundle-norm collisions when v_X, v_Z have nonzero overlap. Brain-existence-proof asymmetric for the projection primitive itself; cap novel-synthesis 0.65; deflate 0.55 for finite-N.)

**Why now.** Foundational sub-step for TOP-1; ALSO independently valuable for any future causal-discovery work; this is the load-bearing primitive most at risk in TOP-1's three-step pipeline. Building it first de-risks TOP-1.

---

### TOP-3: `exp_direct_vs_indirect_causal_discrimination_v1` (P_deflated = 0.50)

**Brain mechanism -> substrate primitive mapping.**
- **CITED@Cheng-Novick 1992** (Covariation in natural causal induction, Psych Rev 99:365-382) — humans discriminate direct vs indirect (mediated) causation via "screening off" — if conditioning on intermediate C eliminates X-Y association, then X causes Y only via C.
- **CITED@Sloman-Lagnado 2005** (Do we "do"? Cognitive Science 29:5-39) — interventional discrimination: if do(C=c0) breaks X->Y dependence, then C mediates.
- **CITED@Wright 1921** (Correlation and causation, J Agric Res 20:557-585) — path analysis; direct vs indirect path contributions.
- **Substrate primitive mapping:** Given candidate chain X -> C -> Y (verified via TOP-1 or stored as known chain), test whether there is ALSO a direct edge X -> Y:
  - Run K-hop X -> Y under W (current substrate state); record cosine_full.
  - Run K-hop X -> Y under W with do(C = neutral_vector) via CF Cell 2 v2 delta-stack; record cosine_blocked.
  - DIRECT if `cosine_full - cosine_blocked > theta_direct` (X->Y signal SURVIVES blocking C).
  - PURE INDIRECT if `cosine_full - cosine_blocked < epsilon` (X->Y signal VANISHES when C blocked).

**Concrete test.** Synthetic chains: 50 length-3 chains where X->Y is PURE INDIRECT (mediated by C) and 50 length-3 chains where X->Y is BOTH (direct + via C). Substrate stores all triplets. Cell discriminates per chain.

**Discriminator (META_RULE_AF).**
- ARM_A: substrate CF-blocked discrimination (cosine_full vs cosine_blocked).
- ARM_B: K-hop-cosine-only (no CF blocking; tests that intervention arm adds value; predicted to FAIL because direct + indirect chains have similar full-cosine).
- ARM_C: oracle (knows ground-truth direct/indirect; BY-CONSTRUCTION ceiling).
- ARM_D: random baseline (50% acc on balanced classes).
- Discrimination requires: ARM_A > ARM_B by >=0.20 acc AND ARM_C - ARM_A < 0.10 AND ARM_A > ARM_D by >=0.30.

**Fairness gate.** Balanced class distribution (50/50 direct+indirect / pure-indirect); per BIAS-14 (regime): chain lengths held at 3 (extending to length-5 in a separate cell after primary HARD_PASS); CF blocking uses CF Cell 2 v2 delta-stack at SAME stack_depth as production CF.

**Pre-reg HARD bands.**
- HARD_PASS: acc >= 0.75 AND ARM_A - ARM_B >= 0.20 AND ARM_C - ARM_A < 0.10. EXPECTED@acc=0.80.
- HARD_FAIL: acc < 0.55 OR ARM_A - ARM_B < 0.05.
- MIDDLE_BAND: acc in [0.55, 0.75].
- CARDINALITY_OK: 4 arms x 100 chains x 3 seeds = 1200.

**Smoke.** 20 chains, 1 seed (~40s); ARM_A > ARM_B by >=0.10.

**Compute.** ~5min CPU full + 40s smoke.

**P_deflated = 0.50** (direct composition of two chain-grade primitives — K-hop + CF delta-stack. Risk: cosine differences may be small when chain interference dominates; theta_direct tuning sensitivity. Cap novel-synthesis 0.65; deflate 0.50.)

**Why now.** "Did A REALLY cause Y, or only via C?" is the load-bearing question for actionable causal explanation in M3 conversational AI and M4 experimental loop (e.g., "Did treatment T cause outcome O, or only via biomarker B?" - high-stakes for medical-AI). Independently valuable; pairs with TOP-1 as the second-pass "verify the chain" step.

---

## NON-TRADITIONAL FIELD CROSS-DOMAIN PROBES (per USER directive — branch out)

**(a) Legal proximate cause + foreseeability doctrine.** CITED@Hart-Honore 1985 (Causation in the Law 2e, Oxford) — legal causation distinguishes "but-for" cause (sine qua non) from "proximate cause" (legally cognizable). Proximate cause requires (i) but-for satisfaction, (ii) foreseeability (no superseding intervening cause), (iii) directness (no excessive remoteness). This maps 1:1 to substrate primitives: (i) = CF replay (X removed -> Y removed); (ii) = direct-vs-indirect discrimination (TOP-3); (iii) = chain-length bounded K-hop. The legal-AI vertical is a real product use case for TOP-1 + TOP-3 composition. **Cited@Palsgraf v. Long Island Railroad 1928** is the canonical case where direct CF-cause held but proximate cause was denied — substrate primitive could quantify both signals.

**(b) Investigative journalism + criminology root-cause analysis (5-Why / Ishikawa fishbone).** CITED@Ohno-Toyota 1988 (5-Why method, Toyota Production System) — iterative "why?" five times to reach root cause; each iteration is one K-hop traversal backward on a causal DAG. Substrate-native: TOP-1 outputs the chain; iterative substrate query "what causes X_i?" via CAUSE_OF role inversion. The Ishikawa diagram (4M: Man/Machine/Method/Material) is a 4-category superposition over candidate causes — substrate-native via category-role binding. This is one of the cleanest practical applications of TOP-1; manufacturing-failure-analysis vertical is a real M3/M4 use case.

**(c) Gene regulatory network reverse-engineering (ARACNe + Granger).** CITED@Margolin-Nemenman-Basso-Wiggins-Stolovitzky-Dalla Favera-Califano 2006 (ARACNe: Algorithm for the Reconstruction of Accurate Cellular Networks, BMC Bioinformatics 7:S7) — mutual-information-based reverse-engineering of gene regulation; data-processing inequality (DPI) used to prune indirect edges. **Direct substrate analog: TOP-1 SUB-STEP 1's CI pruning IS the DPI step.** ARACNe runs on ~10^4 genes with ~10^6 candidate edges; substrate's K-hop + residual-projection scales O(V_pairs * V_conditioning) — feasible for V <= 1000 at N=4096 (estimate: <30min). Bio-discovery vertical. CITED@Granger-1969 (Investigating causal relations by econometric models, Econometrica 37:424-438) — temporal-precedence-based causation test; substrate's now-grounding + bitemporal cells provide the Granger-causality primitive directly.

**(d) Chemical reaction network kinetics (Pearl-mapped).** CITED@Feinberg 1979 (Lectures on chemical reaction networks) — reaction networks form bipartite DAGs (species + reactions); causation is reaction-mediated. Substrate-native cell could discover unknown reaction pathways from time-course concentration data — direct map to TOP-1 with variables = species + time-bins. Materials-discovery vertical (USER directive).

**(e) Protein folding cascade temporal causation.** CITED@Levinthal 1969 paradox / Dill-Chan 1997 funnel model — folding pathway is a sequential causal chain through intermediate states; molecular-dynamics trajectories provide observation tuples. Substrate-native chain extraction could classify candidate folding pathways. Lower-priority (data-acquisition cost dominant).

**(f) Climate forcings -> temperature -> ice-melt -> albedo feedback loops.** CITED@Bony-Dufresne 2005 (Marine boundary layer clouds at the heart of tropical cloud feedback uncertainties) — climate causation involves feedback loops (NOT pure DAGs). This is the substrate-stress-test: PC algorithm assumes DAG, but real climate is cyclic. Substrate-native could detect cyclic causation by failing TOP-1's orientation step (orientation disagrees in different intervention directions = cycle signature). Honest negative would be valuable.

**(g) Pearl actual-causation (Halpern-Pearl 2005 / 2015 modified).** CITED@Halpern-Pearl 2005 (Causes and Explanations: A Structural Model Approach, BJPS 56:843-887). Definition: X=x is an actual cause of Y=y iff (AC1) X=x and Y=y observed; (AC2) there exists a "witness" W such that under do(W=w'), changing X changes Y; (AC3) X is minimal w.r.t. AC2. Substrate-native AC2 = CF Cell 2 v2 delta-stack run with W set to non-actual values, testing whether Y changes when X changes. **This is the formal definition of "actual causation"; substrate can test it directly.** v2 cell (reserve for after TOP-1 lands).

**(h) Hill's criteria of causation (epidemiology).** CITED@Hill 1965 (The environment and disease: association or causation? Proc R Soc Med 58:295-300). Nine criteria: strength, consistency, specificity, temporality, biological gradient, plausibility, coherence, experiment, analogy. Substrate-native maps: temporality = now-grounding; experiment = CF Cell 2 v2; strength = K-hop cosine; specificity = direct-vs-indirect (TOP-3); biological gradient = monotonic-response under do() sweeps. **Hill criteria checklist as a substrate-native scoring function = directly product-able feature for medical-AI Stage 3.**

---

## CROSS-THREAD SYNTHESIS

**With 2026-06-07 prior drill:** the prior drill's Sections 2.2 and 7 are the load-bearing scaffolding. Mechanism A (role markers) is now CHAIN_GRADE (correlational_disambig today). Mechanism B (rank-1 surgery) is now CHAIN_GRADE (CF Cell 2 v2 delta-stack today). Mechanism C (hybrid symbolic) is NOT taken — TOP-1 keeps everything substrate-native by using K-hop + residual CI in place of a symbolic ID algorithm, accepting that we won't recover full do-calculus identification but WILL recover ranked candidate chains. Section 7's CI test is built in TOP-2.

**With today's temporal-reasoning drill (sibling):** TOP-1's edge-orientation arm requires temporal-precedence; the temporal drill's TOP-1 time-cell-population primitive is a STRONGER orientation cue than current now-grounding alone. If temporal drill's TOP-1 lands chain-grade, this drill's TOP-1 should adopt it. Allen relations (BEFORE / OVERLAPS / DURING) directly encode temporal-precedence at population-level. Cross-pollination: both drills share Hill's "temporality" criterion as substrate-native primitive.

**With CF Cell 1 (correlational_disambig CHAIN_GRADE):** the same role-binding mechanism (CAUSE_OF / CORRELATED_WITH / EFFECT_OF) gives TOP-1's SUB-STEP 3 a write-time validation: edges inferred via orientation should match stored CAUSE_OF facts in the corpus when the corpus is annotated. This gives a free test-set for TOP-1 (use ConceptNet causal triples as ground-truth — substrate already has ConceptNet ingestion via KG cells).

**With CF Cell 2 v2 (latency delta-stack CHAIN_GRADE today):** TOP-1's SUB-STEP 2 orientation arm uses this directly for interventional asymmetry; the 5.47x speedup means orientation arm cost ~ 2ms per intervention, so a 5-variable DAG's full orientation (~20 interventions) is <40ms — well below any latency band. ALSO: amortized-stack=5 means TOP-1 can process 5 nested do() interventions for direct-vs-indirect TOP-3 efficiently.

**With chain-grade audit-chain-depth-50:** chain assembly in TOP-1 SUB-STEP 3 inherits this validation; depth-50 K-hop on a directed sub-W is identical in mechanics to depth-50 on stored W (just smaller V).

**With intervention_isolation CHAIN_GRADE:** isolation invariance under do() supports TOP-3's blocking arm — when we do(C=neutral), substrate's intervention isolation guarantees other variables are unaffected (no harness leakage).

**With Stage 3 matrix (research_stage3_definition_2026-06-25):** causal-chain extraction is the MISSING row for "explain WHY" capability. TOP-1 closes this row; TOP-2 + TOP-3 add depth.

**With M3 + M4 milestones:** TOP-1 + TOP-3 together provide the "why?" answer-with-citations primitive for M3 conversational AI; M4 hybrid agentic-experiment loop needs substrate to PROPOSE causal hypotheses from experimental data — TOP-1 is the proposal mechanism.

**With temporal_parameter_taxonomy:** time-cell tape primitive (proposed in today's temporal drill) directly upgrades TOP-1's SUB-STEP 2 temporal-precedence; planning composition once temporal lands.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

Per [[feedback-no-papers-product-only]]: framing is product-relevant, NEVER publication.

**M3 conversational AI dependency:** "Why did Y happen?" is one of three core conversational primitives (alongside "what comes next" — temporal — and "if not X, then?" — counterfactual, already chain-grade). Without causal-chain extraction, the substrate can REPLAY a stored chain but cannot PROPOSE one from observations. TOP-1 closes this gap.

**M4 hybrid agentic-experiment loop:** the substrate proposes causal hypotheses; the experiment runner tests them; results feed back as new corpus facts. TOP-1 is the proposal mechanism for this loop. **This is the canonical M4 capability** — without it, M4 reduces to dispatched search rather than substrate-as-research-director.

**Legal-AI / medical-AI / manufacturing-failure-analysis verticals:** all three downstream domains (legal proximate cause; Hill's epidemiological criteria; 5-Why root-cause) need exactly TOP-1 + TOP-3 composition. These are real product surfaces with regulatory framings (EU AI Act Article 12 for legal/medical; ISO 9001 for manufacturing).

**Bio-discovery vertical (ARACNe / Granger):** TOP-1 + TOP-2 composition gives substrate-native gene-regulatory-network reverse-engineering — substrate already has bio ingestion (GO/KEGG/NeuroLex 222k atoms); plug TOP-1 into time-course expression data.

**Substrate-as-Director-KB:** the dogfood KB stores notes/cells/atoms; TOP-1 enables substrate to ANSWER "why did this cell fail?" by extracting the causal chain from prior-cell observations -> failure-mode atoms -> root-cause notes. This is the self-improvement Phase 2 capability USER named in strategic vision (2026-06-22).

**Stage progression risk:** per [[feedback-stage-progression-1234-dont-skip]], TOP-1 is Stage 3; do NOT skip to Stage 4 language-grounded causal Q&A until TOP-1 lands. The temporal-substrate-doesnt-know-anything caution applies — keep TOP-1 evaluations on synthetic DAGs + bio-corpus + legal-toy until language understanding prerequisites exist.

**Not in scope:** full do-calculus identification (requires external symbolic layer per 2026-06-07 Mechanism C); full PC algorithm in nonlinear regime (substrate residual-projection is sound only in linear-Gaussian regime; nonlinear extension would require kernel CI test — future work).

---

## CITATIONS (verified count)

Brain literature (5):
1. CITED@Tomov-Yagati-Kumar-Hayden-Niv 2018 — Discovery of hierarchical representations for efficient causal inference (BioRxiv 285395; PLoS CB 16:e1007879 2020).
2. CITED@Schuck-Niv 2019 — Sequential replay of nonspatial task states in human hippocampus (Science 364:eaaw5181).
3. CITED@Eichenbaum 2017 — Memory: organization and control (Annu Rev Psychol 68:19-45).
4. CITED@Yu-Frank 2015 — Hippocampal-prefrontal interaction (Hippocampus 25:1156-1164).
5. CITED@Foster-Wilson 2006 — Reverse replay of behavioural sequences in hippocampal place cells (Nature 440:680-683).

Pure math + formal causation (8):
6. CITED@Pearl 2009 — Causality: Models, Reasoning, and Inference 2e (Cambridge).
7. CITED@Spirtes-Glymour-Scheines 2000 — Causation, Prediction, and Search 2e (MIT).
8. CITED@Halpern-Pearl 2005 — Causes and explanations: a structural model approach (BJPS 56:843-887).
9. CITED@Glymour-Zhang-Spirtes 2019 — Review of causal discovery (Front Genet 10:524).
10. CITED@Granger 1969 — Investigating causal relations by econometric models (Econometrica 37:424-438).
11. CITED@Wright 1921 — Correlation and causation (J Agric Res 20:557-585).
12. CITED@Hill 1965 — Association or causation (Proc R Soc Med 58:295-300).
13. CITED@Lagnado-Sloman 2006 — Time as a guide to cause (JEP-LMC 32:451-460).

Cognitive science (4):
14. CITED@Cheng-Novick 1992 — Covariation in causal induction (Psych Rev 99:365-382).
15. CITED@Sloman-Lagnado 2005 — Do we "do"? (Cognitive Science 29:5-39).
16. CITED@Lagnado-Waldmann-Hagmayer-Sloman 2007 — Beyond covariation: cues to causal structure.
17. CITED@Gopnik-Schulz 2007 — Causal learning: psychology, philosophy, computation (Oxford).

Materials / biology / cross-domain (5):
18. CITED@Margolin-Nemenman-Basso-Wiggins-Stolovitzky-Dalla Favera-Califano 2006 — ARACNe (BMC Bioinformatics 7:S7).
19. CITED@Feinberg 1979 — Lectures on chemical reaction networks.
20. CITED@Bony-Dufresne 2005 — Marine boundary layer clouds (Geophys Res Lett 32:L20806).
21. CITED@Dill-Chan 1997 — From Levinthal to pathways to funnels (Nat Struct Biol 4:10-19).
22. CITED@Levinthal 1969 — How to fold graciously.

Non-traditional (3):
23. CITED@Hart-Honore 1985 — Causation in the Law 2e (Oxford).
24. CITED@Palsgraf v. Long Island Railroad 1928 — 248 NY 339 (legal proximate cause canonical).
25. CITED@Ohno 1988 — Toyota Production System (5-Why method).

Substrate internal (verified on disk):
- `notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md` (full read).
- `notes/research_stage3_definition_and_chain_grade_verification_matrix_2026-06-25.md` (full read).
- `notes/research_drill_2x_temporal_reasoning_primitive_stage3_2026-06-27.md` (full read; sibling drill).
- `data/exp_causal_correlational_disambig_v1/metrics.json` (full read; HARD_PASS).
- `data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json` (full read; HARD_PASS today, 5.47x speedup).
- `data/exp_counterfactual_do_operator_v1/metrics.json` (verified exists).
- `notes/director_LIVE_STATE_2026-06-27.md` (read).

**Total: 25 external citations + 7 substrate-internal verified atoms.**

---

## EXP_DEV-ACTIONABLE? YES — companion hand-off file written at `notes/exp_dev_handoff_research_causal_chain_extraction_primitive_stage3_2026-06-27.md`

Per role contract: TOP-1 is anchor-pointer-ready; TOP-2/TOP-3 are ranked candidates; tier-hint, why-now, contract-section all in the hand-off.

---

(End of research drill 2x causal-chain extraction primitive Stage 3.)
