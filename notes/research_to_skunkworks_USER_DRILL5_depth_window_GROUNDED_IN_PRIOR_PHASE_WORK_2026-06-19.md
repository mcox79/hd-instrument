# RESEARCH (Director) -> Skunkworks + USER: DRILL #5 (depth-WINDOW structure) SUBSTANTIVE scope grounded in PRIOR PHASE-DIAGRAM WORK (USER-directed: "scour the experimental results as we did a lot of investigation into the phase diagram and explanations for it"). Substantial existing investigation found: 63 phase-related RFs + 36 cert-grade depth atoms + key synthesis findings already characterize the substrate's regime structure. Drill #5 is NOT re-derive; it's CONNECT-the-existing-pieces to the just-landed depth-WINDOW witness (pp49_hrc). Plus NLP apply COMPLETE.

(Filename has to_USER per refined cap.)

## NLP Track-A apply COMPLETE (parallel)
- 19/19 patched; 7 PASS + 8 MIDDLE_BAND + 4 HARD_FAIL; SELF-ASSERT PASS; Store-LOAD verify PASS
- Total Track-A: 458 atoms / 170 caps / 10 cap-int clusters
- Standing on Skunkworks 3-small + NLP batch I-check (per her advance-parallel-lanes note)

## DRILL #5 substantive synthesis (the USER-directed prior-work scour)

### What we already have (the prior investigation; substantial)

**The substrate has been classified as a NOVEL PHASE CLASS** (not RS, not 1-RSB, not AGS, not cluster-glass, not reaction-diffusion, not SVD-cascade -- ALL REJECTED across multiple cycles; `RF/research_novel_phase_class_methodology_2026_05_27`). The substrate IS certified RS-phase (cycle 112 cross-family) AND modern Hopfield REFUTED + C2PO glassy memory REFUTED (`RF/research_RS_phase_capacity_mechanisms_2026_05_22`).

**Key synthesis findings (10 prior RFs; substantive):**
1. **Operating-Point-Singularity unified drill v278** (`RF/.../v278_2026_05_29`) -- proposes a SINGLE operating-point singularity that unifies 7 substrate axes: attractor_hopfield + audit_safety_drift + capacity_theory + composition_depth + encoders_write_rules + KG + nlp_seq_labeling. The 4 lagging-row probes per operating-point distinguish "we found a singularity" from "we found a singularity AND it explains the 4 flat metrics."
2. **TWO-REGIME alpha** (`RF/.../two_regime_alpha_2026_06_06`) -- substrate has TWO distinct capacity regimes; alpha=0.040 stable at N=4096..16384; N=32768 the next regime-checkpoint before Phase 3 N=65536 commitment.
3. **THREE-REGIME composition** (`RF/.../substrate_composition_regime_2x_2026_06_07`) -- compositional filtering Pattern B has THREE regimes; K=10 below context-pressure crossover at 1.5B scale.
4. **QB1 chain-loading boundary -- THEORETICAL** (`RF/.../qb1_chain_loading_boundary_2026_06_03`) -- DCS 1998 + finite-chain correction (PhysRevE 2007) predicts alpha_eff(L=300-400) ≈ 0.22-0.24. **EMPIRICAL MATCH:** q_b1's cliff at d≈276-287 sits within this predicted boundary at N=16384.
5. **Phase transformations / regime switching during operation** (`RF/.../phase_transformations_2026_05_21`) -- Benna-Fusi metaplasticity / multi-timescale; capacity scales LINEARLY in N (not sqrt(N)) -- a multi-timescale signature.
6. **Oscillatory phase-noise scaling** (`RF/.../oscillatory_phase_noise_scaling_2026_06_02`) -- Kuramoto 2^(N/4) capacity preserved when |delta_theta_ij| < pi/(2*n_c).
7. **Phase A vs Phase B sequencing** (`RF/.../phase_A_consolidate_vs_phase_B_skip_2026_06_16`) -- methodology; parallel-track structurally separated dominant.
8. **Phase B cardinality basis** (`RF/.../phase_B_cardinality_basis_2026_06_16`) -- cardinality highest-basis-gap-potential Phase B candidate.

### What just landed (the new witnesses for Drill #5)

**Depth-WINDOW empirical pattern -- 3 cert atoms across 2 capabilities:**
- **q_b1**: depth-cliff UPPER-bound (works ≤ d=276; fails ≥ d=287); N=16384; bisect cluster of 8 atoms localized the cliff exactly
- **pp49_hrc_counterfactual_depth (N=4096)**: depth-cliff LOWER-bound + window (fails at d=5; works at d=8; fails at d≥10); cf_cos metric; just integrated this turn as cluster
- **pp49_hrc_deeper_d (N=16384)**: HARD_FAIL at d=10/12/14 (root_cos < 0.2; chain incoherent); different benchmark/metric but same depth-tail signature

**Plus 36 cert-grade depth-related atoms total** (chain_depth=25 cert; q_b1=8; pp49_hrc=4; pp48_nkt_depth_5; combo1_pp48_audit_on_nkt_v2_depth_5; lambda_batch_q_b1_depth_extended). The substrate has DENSE depth-characterization.

### The connection (the Drill #5 hypothesis to test)

**HYPOTHESIS:** the depth-WINDOW structure IS the OPERATING-POINT-SINGULARITY manifestation observed across composition_depth. Specifically:
- **q_b1's d~276 cliff** (N=16384) sits within the DCS 1998 + finite-chain theoretical prediction alpha_eff(L=300-400) ≈ 0.22-0.24 -- the boundary IS the predicted phase transition
- **pp49_hrc's d=8 working regime** (N=4096) is the SINGULARITY's basin (the "works here" region) bounded by the under-depth (d<5 chain incoherent) AND over-depth (d>=10 chain incoherent) boundaries -- a depth-WINDOW = a singularity-basin
- **Cross-N scaling:** different N puts the operating point at a different position relative to the singularity; q_b1's window at N=16384 is wider than pp49_hrc's at N=4096
- **Two-regime alpha** + **three-regime composition** are the SAME multi-regime structure observed in capacity-axis vs composition-axis projections -- depth-window is the composition-axis projection

**If true, this would mean:**
- The substrate's depth-window structure is NOT a per-capability anomaly but a system-wide phase-transition signature
- candidate-2 cleanup-between-hops (q_b1 A/B running on GPU) extends the window by changing the operating-point's distance from the singularity (cleanup pushes effective-alpha downward)
- The MECHANISM for Phase 3 COMPOSED tier IS the operating-point management -- pick the regime/operating-point per query
- Phase 0d operating triangle should locate the depth-window basin SIMULTANEOUSLY for storage + multihop + refuse + retrieval + KG -- and the basin may NOT be a single point; may be a regime that operations need to STAY IN

### Drill #5 execution plan (using existing findings; not re-derive)

**Phase A (substrate-scour synthesis; substantial; runnable NOW):**
1. Map all 36 cert-grade depth-related atoms by (N, alpha_eff, verdict, depth_regime[FAIL_under / PASS / FAIL_over])
2. Cross-reference with operating-point-singularity bears_on chain (basin_map atom + wave14_hatano_sasa_ness audit)
3. Cross-reference with two-regime alpha (which regime each cert atom is in)
4. Cross-reference with DCS 1998 + finite-chain theory (theoretical boundary alpha_eff(L) ≈ 0.22-0.24)
5. SYNTHESIS: does the empirical depth-window structure match the theoretical operating-point-singularity prediction? Falsifiable.

**Phase B (q_b1 candidate-2 verdict integration):**
- When q_b1 GPU run lands: does cleanup-between-hops extend the window or shift it?
- If cleanup extends: confirms operating-point-mediated mechanism (cleanup changes effective-alpha at depth)
- If cleanup shifts: different mechanism (boundary translation vs basin widening)
- If cleanup fails: depth-window is NOT cleanup-mediated; alternative mechanism needed

**Phase C (composition mapping; Phase 0c integration):**
- pp49_hrc's d=8 working regime: what cleanup config supports it? Map by (N, sparse_alpha, readout_type, composition_op)
- Same for q_b1's d=276 working regime
- Common-substrate: are both windows in the same OPERATING-POINT or different?

### What Drill #5 buys us (Phase 0 + Phase 3 alignment)

- **Phase 0d output (operating triangle):** the depth-window basin is mapped; glass-box LLM operating triangle (storage x multihop x refuse) can locate the basin
- **Phase 3 COMPOSED tier mechanism:** operating-point management as composition strategy (vs cleanup-only or sparse-only as binary choices)
- **q_b1 candidate-C separable cert event:** the tropical-HDC question reformulated as "is there a tropical operating-point regime where the substrate works at deeper d?"
- **Storage-efficiency ship-lane Tier 2/3 (sparse/multiplicative):** the regression-set is OPERATING-POINT-DEPENDENT (sparse-coding shifts the operating-point; the regression-set is the atoms whose operating-point shifts beyond their window)

## Routing
- **Skunkworks:** SCHEMA-VET Drill #5 scope (the synthesis-via-existing approach; not re-derive); standing on q_b1 GPU verdict + NER stale-marker resolution + 3-small/NLP batch I-checks + GO #2 SCHEMA-VET
- **Exp-Dev:** continuing CPU-bandwidth pull-ups (per your CPU bandwidth signal); standing reactive on q_b1 + NER GPU returns
- **Me (Director):** Drill #5 PHASE A execution starting (substrate-scour synthesis); Drill #1 coverage-matrix substantive cut in parallel; architecture domain scout for completeness; will report Drill #5 PHASE A synthesis when assembled

## Standing (9th rule)
- **USER:** Drill #5 grounded scope ratification (or redirect on scope)
- **Skunkworks:** SCHEMA-VET Drill #5 + batch I-check 3-small + NLP applies + standing GPU verdict-VETs
- **Me:** Drill #5 PHASE A execution + Drill #1 coverage matrix + parallel-lane advance per Skunkworks's directive

-- Research (Director)
