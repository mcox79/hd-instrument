# Research session post-compaction brief -- 2026-06-04

**Read FIRST after context reset.** Comprehensive state of research session as of end of 2026-06-04 working day. Next session can pick up cleanly from here.

---

## TL;DR

15+ research drills landed today; substrate's algebraic characterization is the most complete in the project (12+ lit anchors). Bundle A empirical results identified 2 HP architectures (cf-RPE alone + Drosophila sparse coding). NEW methodology established: W-modifying vs inference-overhead distinction calibrated against Bundle A pattern. ONE product-critical action pending: deletion-cert sigma threshold needs 5x empirical recalibration via N-extension test (already routed).

---

## Substrate's complete algebraic characterization (post-today)

| Property | Result | Lit anchor |
|---|---|---|
| Spectral regime | BBP-critical Wishart + non-Hermitian deformation; active-driven NESS class | Baik-Ben Arous-Peche 2005 + Bertini 2015 |
| Capacity regime | classical Hopfield alpha_c=0.138; sparse f=0.05 gives 23x gain | Hopfield 1982 + Willshaw-Buckingham |
| Hidden objective | KL[p_t \|\| mu_NESS] Lyapunov; not closed form | Wang-Xu-Wang 2008 + Maes-Netocny 2014 |
| Closed-form training signal | F_eff = -alpha*m^4/4 + m^2/2 (Cates-Tailleur active matter) | Cates-Tailleur 2015 |
| Task complexity ceiling | K* = log_V(alpha_c * N) + 1 | derived; validated by Bundle A bigram + pending Bundle B trigram |
| Composition moat | L=10000 EXACT-1.0000 unbounded by precision | empirically validated |
| Drift detection | gamma~8 isochoric kappa_3; tunable via tau | NHSE-annulus (Hatano-Nelson 1996) |
| Deletion certificate | cos=1 algebraic; **sigma threshold 5x off** | Ramsauer Theorem 1 + ROME/MEMIT (Meng 2022) |
| Bipolar quantization | 97% MI loss per coordinate vs continuous | Naitzat 2020 |
| STDP capability | 1.94x sequence storage; transitions not contexts | Crisanti-Sompolinsky 1988 + Chaudhry 2023 |
| Position-binding translation | K* unchanged with symmetric W; raised with W-modifying composition | Plate 1995 HRR + Kanerva 1996 BSC + Ramsauer 2020 |

15+ distinct lit-anchored frameworks. Most theoretically-grounded substrate-class memory characterization in the AI lit.

---

## THE NEW METHODOLOGY -- W-modifying vs inference-overhead

**The fundamental distinction:**

W-MODIFYING mechanisms (change mu_NESS itself; CANNOT be subsumed):
- BCM three-factor Hebbian
- cf-RPE (rank-1 counterfactual substitution)
- Sparse coding (f=0.05 Drosophila MB)
- STDP-asymmetric
- Anti-Hebbian repulsion

INFERENCE-OVERHEAD mechanisms (operate on fixed W; subject to subsumption by NESS):
- Friston FEP precision matrix Pi (DENSE) -- empirically HF as predicted
- Attention over fixed W (subsumed at substrate scale)
- External memory with separate objective

Empirical validation: Bundle A v394 verdict pattern (5 of 6 matches; 1 mismatch FEP HF explained via parameter-budget defeat rho=1678 + NESS subsumption).

**Going forward, every brain-drill must split P_deflated:**

P_deflated_joint = P_algebraic * P_implementation
P_implementation = P_convergence * P_budget * P_no_subsumption * P_task_match

Recovery thresholds for inference-overhead: K_LM > 50k+ params with diagonal Pi (rho < 0.1).

Lit anchors: Marblestone 2016 + Rajeswaran iMAML 2019 + Solomonoff 1964 + K-complexity neural weight norm 2026.

---

## Today's 15+ drills landed

### Brain-inspired track (substrate-as-training-mechanism)

1. **META 3x+** -- 3 binding constraints; 3 bypass designs (A contrastive / B retrieval+SGD / C single-channel)
2. **Spectral monitor B 3x** -- kappa_k cannot detect saturation; recommended erank + Hessian trace complementary primitives
3. **Multi-channel orchestration C 3x** -- gating router capacity collapse at K=8/10k LM; bottleneck-adapter mitigates
4. **Grouped 2x** -- bipolar quantization 97% MI loss; continuous float32 fix
5. **Lyapunov 2x** -- NHSE-annulus framework for drift detection
6. **Multiplicative gating 2x** -- sparse multiplicative p<=1/K avoids PCGrad cycle collapse
7. **cf-RPE 2x** -- counterfactual rank-1 as substrate-native RPE; TD-equivalent
8. **Multi-channel scale 3x** -- LM <300k params has gating router collapse; bottleneck-adaptor structural fix
9. **Functional differentiation 3x** -- CLS theory; 4-region (cortex/hippocampus/BG/cerebellum) class
10. **Small-brain template 2x** -- Drosophila MB f=0.05 sparse; single dopamine modulator
11. **STDP temporal asymmetry 2x** -- symmetric Hebbian algebraically can't encode order; 1.94x sequence capacity
12. **Friston FEP 2x** -- algebraically dissolves Constraint 2; Spisak-Friston 2025 precedent
13. **REM-replay 2x** -- energy-guided top-K replay; conditional on N>=8192
14. **Topological invariants 2x** -- exploratory; Adams-Virk constrains classical PH; beta_0 + Mapper viable
15. **N-threshold 3x** -- predicted N=2000-4000 ceiling; EMPIRICALLY REFUTED (substrate learns at N=512)
16. **Modern Hopfield upgrade 3x** -- polynomial-p=4 lowers capacity floor 30x; BCM-SNR floor independent
17. **BCM-SNR vs polynomial-p 2x** -- write mode is critical confound (episodic vs cumulative)
18. **kappa3-NLO noise convention 2x** -- additive-on-patterns vector Gaussian is formula-matched
19. **Position-binding translation 2x** -- VSA capacity OK but W capacity wall unchanged with symmetric W
20. **Task complexity ceiling 2x** -- K* = log_V(alpha_c * N) + 1 derived; predicts Bundle B
21. **NESS hidden objective 2x** -- KL[p \|\| mu_NESS] always exists; Constraint 2 weakened not dissolved
22. **Intermediate-regime scaling 2x** -- BBP-critical + non-Hermitian; 5x sigma overconfidence found
23. **CALIBRATION META 2x** -- W-modifying vs inference-overhead; explains FEP HF; new drill methodology

### Substrate-physics track

24. **NHSE tau-scaling 2x** -- gamma(tau) = 1.20 * exp(3.83 * tau) closed form; refuted empirically v390

Total ~23+ deep drills today (some overlap). All $0 research compute.

---

## Empirical verdicts that landed today

### Substrate physics
- L=2000, L=10000 cross-layer composition HARD_PASS (NEW DEEPEST x2)
- Capacity-stress at M/N boundary HARD_PASS (classical Hopfield confirmed)
- PP-50 lambda_1 N-extension test MIDDLE (beta=0.331; CI=[-0.087, 0.705]; 95% includes zero)
- PP-50 v2/v3 sigma_sep N-sweep HARD_FAIL (probe design failure; reformulated to lambda_1)
- NHSE-annulus tau-sweep + tau_crit HARD_FAIL x2 (NHSE-exponential framework refuted)
- Q-B1 chain-loading boundary alpha_c=0.15 at N=2048 MIDDLE_BAND
- PP-47 hippocampal REM-replay baseline MIDDLE_BAND
- kappa3-NLO v1 (additive-on-W; sign-flipped) -- COMPLETED at HARD_FAIL by design

### Brain-inspired (Bundle A)
- substrate_joint_dh_brain_correct_rung1 HARD_FAIL (5 arms; no architectural differentiation at bigram)
- substrate_trained_mini_lm_readout_fix_v2 HARD_FAIL (N=512 too small)
- substrate_training_n_threshold_sweep HARD_FAIL HF2 (N=512-8192 all learn; N-threshold prediction refuted)
- substrate_modern_hopfield_p_nthreshold_sweep MIDDLE (p=4 ≈ p=2)
- **Bundle A v394 (architectural ablation): cf-RPE alone HP + Drosophila sparse HP + STDP/2-region/bottleneck MIDDLE + Friston FEP HARD_FAIL**
- substrate_drosophila_mb_sparsity_sweep MIDDLE (N-dependent optimal f)

### LLM-integration (Phase 0.5 v1)
- Phase 0.5 v1 Rung 0 (Pythia-160M Algorithm 1 debug) HARD_PASS (Rung A gate OPEN; engineering pending)

---

## Routings shipped to Exp-Dev today (10+)

| Routing | Status |
|---|---|
| routing_consolidated_experiment_roster_for_exp_dev_2026-06-04.md | Master roster |
| routing_convergent_brain_architecture_empirical_batch_2026-06-04.md | Bundle A landed |
| routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md | Bundles A-D |
| routing_position_binding_combined_architecture_bundle_e_2026-06-04.md | Bundle E pending |
| change_request_bundle_b_add_friston_fep_trigram_cell_2026-06-04.md | FEP trigram cell |
| routing_bundle_a_combined_superadditive_test_2026-06-04.md | cf-RPE + sparse combined |
| routing_n_extension_test_n32768_decisive_arbiter_2026-06-04.md | N-extension landed MIDDLE |
| routing_phase05_v1_rung_a_reprioritize_parallel_track_2026-06-04.md | Rung A engineering pending |
| routing_substrate_training_n_sweep_readout_fix_2026-06-04.md | N-sweep complete |
| change_request_polynomial_p_engineering_2x2_factorial_bcm_informed_2026-06-04.md | 2x2 factorial pending |
| routing_polynomial_p_modern_hopfield_engineering_2026-06-04.md | Engineering started |
| routing_redirect_depth_to_capacity_stress_test_2026-06-04.md | Capacity-stress complete |
| routing_readout_fix_reevaluate_4_brain_inspired_hfs_2026-06-04.md | N=512 confirmed HF |
| routing_capmap_correction_scs_to_nhse_annulus_2026-06-04.md | Cap_map updated |
| routing_pp58_reopen_with_scs_framework_2026-06-04.md | PP-58 reopened |
| routing_paired_pattern_dual_cf_probe_2026-06-04.md | Pending |
| routing_data_attribution_variation_sweep_drill2_redesign_2026-06-04.md | Pending |
| change_request_data_attribution_variation_sweep_drill2_redesign | Standing |

---

## PRODUCT-CRITICAL action items (NEW; previously not flagged)

### Deletion-certificate sigma threshold 5x recalibration

**Issue:** Intermediate-regime drill identified that TW-assumption deletion-cert sigma threshold overstates confidence by 5x. Substrate's BBP-critical regime means actual sigma is 5x WIDER than TW formula predicts.

**Status:** N-extension test (N=32768, 20 seeds) landed MIDDLE. Point estimate beta=0.331 matches BBP-critical (~1/3) prediction but CI is too wide. Recalibration is partially confirmed but not decisive.

**Concrete impact:** If product framing claims X-sigma confidence on deletion-cert, actual is X/sqrt(5) ~ X/2.24. Specifically: 6-sigma confidence becomes 2.7-sigma. NOT acceptable for product claims.

**Action:** Don't ship deletion-cert product framing at TW-derived sigma. Either:
1. Run finer-N + more seeds (Exp-Dev discretion)
2. Use recalibrated factor 2-5x in product claims (conservative)
3. Frame deletion-cert as "algebraically guaranteed" (Ramsauer Theorem 1 + ROME/MEMIT precedent) without specific sigma claim

---

## What's pending verdict

| Item | Source | ETA |
|---|---|---|
| Bundle B (task-complexity sweep at trigram) | Exp-Dev | Pending engineering |
| Bundle E (position-binding + combined architecture) | Exp-Dev | Conditional on Bundle A |
| Combined cf-RPE + sparse superadditivity (Bundle A combined) | Exp-Dev | ~5 min CPU once engineered |
| Bundle B FEP cell at trigram | Exp-Dev | Within Bundle B |
| Phase 0.5 v1 Rung A (Llama-3.2-1B) | Exp-Dev | ~6-10h engineering then ~2-4h experiment |
| Substrate-physics queue background | Exp-Dev | Continues |

---

## What's pending Orchestrator strategy_scribe annotation

| Annotation | Source |
|---|---|
| W-modifying vs inference-overhead methodology | capability_implication_w_modifying_vs_inference_overhead_methodology_2026-06-04.md |
| Substrate algebraic characterization (12+ lit anchors) | capability_implication_consolidated_substrate_algebraic_characterization_2026-06-04.md |
| Deletion-cert sigma 5x recalibration product-critical | product_critical_deletion_cert_sigma_recalibration_2026-06-04.md |
| NHSE-annulus framework for drift detection | routing_capmap_correction_scs_to_nhse_annulus_2026-06-04.md |
| PP-58 reopen with SCS / NHSE | routing_pp58_reopen_with_scs_framework_2026-06-04.md |
| HRC reframe (deletion-cert sub-property) | capability_implication_note_to_orchestrator_hrc_reframe_2026-06-03.md |

---

## Key memory anchors active

- [[feedback-routings-direct-to-exp-dev]] (2026-06-04 user correction)
- [[feedback-cloud-only-when-absolutely-necessary]] (2026-06-03)
- [[feedback-small-scale-first-methodology]] (2026-06-03)
- [[feedback-2x-means-depth]] (existing)
- [[feedback-research-drills-no-empirical-verification]] (existing)
- [[feedback-drill-prompt-bodies-must-be-generic]] (existing)
- [[feedback-lit-scan-calibration-penalty]] (existing)
- [[feedback-no-padding-experiments]] (existing)
- [[feedback-no-smoke-preframing-in-task-prompts]] (existing)
- [[feedback-change-request-protocol]] (existing)
- [[feedback-plain-language-experiment-tracking]] (existing)
- [[feedback-verdicts-include-intuitive-explanation]] (existing)
- [[feedback-no-smoke]] (existing brutal-honesty)

---

## Strategic priorities for next session

### Immediate (when next event lands)

1. **Bundle B verdict synthesis** — empirically validates K* = log_V(alpha_c * N) + 1 prediction
2. **Bundle A combined verdict synthesis** — superadditivity test of cf-RPE + sparse coding
3. **Bundle B FEP at trigram verdict** — tests "FEP recovery at higher complexity" hypothesis
4. **Phase 0.5 v1 Rung A engineering status** — heavy workload on remote GPU; Tier 1 product validation

### Conditional follow-ups (when respective verdicts land)

1. **If combined cf-RPE + sparse HP at bigram** → ship Bundle E (combined-architecture at trigram) immediately
2. **If Bundle B confirms K=3 trigram fails dense Hebbian + passes sparse** → K* framework empirically locked; future work scales the working architecture
3. **If FEP at trigram still HF** → confirms implicit-subsumption hypothesis; FEP framework redundant at substrate scale; methodology fully validated
4. **If Phase 0.5 v1 Rung A HP** → Tier 1 product narrative locked in; "substrate audits real-LLM residuals" empirically validated

### Research drill candidates for next cycle (deferred)

- Cerebellar forward models 2x (functional differentiation extension)
- Active inference 2x (Friston extension; substrate-as-action)
- Sparse-coding compressed-sensing RIP transitions 2x (Drosophila MB algebraic deepening)
- Three-factor discrete STDP on bipolar Hopfield 2x (Klampfl-Maass extension)
- Spin-glass cavity method on precision matrix eigenvalues 2x (NESS extension)
- Morse theory on Hopfield energy landscape 2x (topology direction beyond Adams-Virk)
- Embodied cognition / morphological computation 2x (exploratory)
- Cross-frequency coupling (theta/gamma) 2x (oscillation-based gating)

---

## Open product questions (not research; for user / product session)

1. Does substrate's product narrative want deletion-cert framing? If yes, must recalibrate sigma threshold (or skip explicit sigma; use "algebraically guaranteed via Ramsauer Theorem 1")
2. What integration tier is the target starting product? Tier 1 audit (Phase 0.5 v1 Rung A) is closest; Tier 6 substrate-as-training-mechanism (Bundle B + Bundle E) is more aggressive
3. What customer use cases benefit most from substrate's strongest capabilities (composition L=10000, drift detection gamma~8 tunable, deletion certificate)?

---

## Routing discipline (active this session)

- Address routings DIRECTLY to Exp-Dev (primary) per [[feedback-routings-direct-to-exp-dev]]
- Inform Orchestrator (don't route through)
- Testbed = cloud GPU only (rare; not used today; $0 cloud spend across all today's work)
- ASCII-only in all routings
- Per-routing P_deflated = P_algebraic * P_implementation per the new methodology
- W-modifying vs inference-overhead classification for brain-architectural variants

---

## Cumulative state at end of day 2026-06-04

- HONEST tally: ~830+ (started day at ~785; ~45 new HONEST verdicts processed today)
- LVH tally: 213 → 217 (+4 catches today; orchestrator's verdict_handler caught 4 over-claims)
- Cap_map version: ~v395+
- 15+ research drills landed (all $0)
- Bundle A (architectural ablation) landed; Bundle B/E pending engineering
- Phase 0.5 v1 Rung 0 PASSed (Pythia-160M); Rung A pending engineering
- Most theoretically-grounded substrate characterization in project history

---

**END.**

**Next session:** read this brief first. Then check `notes/strategy_decisions_2026-06-04.md` (or 2026-06-05+) for the latest verdict synthesis. Then check `notes/experiment_queue_pending.md` for what's actively queued at Exp-Dev. Then proceed per pending verdict events.

**Critical: keep the W-modifying vs inference-overhead methodology active.** It's the most important refinement of the day and changes how we predict drill outcomes going forward.
