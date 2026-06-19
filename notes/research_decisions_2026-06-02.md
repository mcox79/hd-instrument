
## negative_results_2x_review -- 2026-06-02 (research:sonnet, 2x review + prior session context)

**Trigger.** orchestrator dispatch per [[feedback-negative-results-2x-research]]; socket-error retry; 6 negative results from overnight CPU cycle 3-5.

**Outcome.** 6 reviewed: 4 DESIGN_FAULT rescues + 2 INSTRUMENTATION rescues; 0 genuine refutations; 0 CANNOT row additions.

**Rescue sequencing**: Tier 0 (in flight): tau_mem Q9 state-vector. Tier 1 (less than 1h CPU each): pp31c near-capacity redesign, timeseries_xor PROT-021 fix, signed-AM M_A sweep. Tier 2 (1-2h): graph_link per-edge keying. Tier 3 (deferred): chi_SG replica architecture.

**P_deflated range**: 0.32 (chi_SG) to 0.72 (timeseries INFRA). Cheapest rescue P=0.70 (pp31c).

**Note path.** notes/research_negative_results_review_2026-06-02.md
**Routing.** notes/research_to_strategy_negative_results_review_2026-06-02.md
**Next-drill candidate.** Per field_advisor: free-probability F4 free cumulants (Voiculescu kappa_n) or semiconductor D1 Glauber dynamics -- both Tier 1 candidates.

---

## 2026-06-02 Research drill batch (post-v342 GPU refill, priority-3 0-compute)

**Trigger.** User explicit priority-3 batch dispatch post-v342 GPU refill. 7 GPU anchors just shipped + completed; pending verdicts. All three drills 0-compute per [[feedback-research-drills-no-empirical-verification]].

**Drill 1 -- I-12 R2 kappa_3 N=16384 config-delta audit.**
- Note path: notes/research_i12_r2_kappa3_n16384_config_delta_audit_2026-06-02.md
- TL;DR: N=16384 anchors measure Hopfield-vs-block-GOE separation; N=32768 cloud measured Hopfield-vs-Hopfield+delta (delta-alpha sensitivity). DIFFERENT OBSERVABLES; no contradiction. Block-GOE noise floor dominates at low alpha at N=16384, collapsing sigma_sep.
- R3-A recommended: `kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` -- re-spec N=16384 with delta-alpha sensitivity protocol (alpha_base=0.05, delta_alphas={0.001, 0.01, 0.04}, n_probes=5000). GPU, ~5 min, $0. P_deflated=0.55.
- Closure: I-12 row NOT closed; observable-mismatch annotation pending.

**Drill 2 -- I-14 R2 implicit-Gram overcomplete theory audit.**
- Note path: notes/research_i14_r2_implicit_gram_overcomplete_theory_audit_2026-06-02.md
- TL;DR: I-14 HF at alpha=2.0 is GATE-SPEC BUG, not substrate failure. Measured kappa3_resc=11.02 EXACTLY matches MP-moment m_3(alpha=2) = 1+3*alpha+alpha^2 = 11.0. HP gate "within 5% of 1.0" is mis-normalized; should be "within 5% of m_3(alpha)". Existing combo1_v3 internal self-test (line 175) also has wrong assert value (asserts ~1.0 at alpha=0.5; correct value is m_3(0.5)=2.75).
- R3-A recommended: `combo1_p3_dam_implicit_gram_v4_corrected_gate_n8192_v1` -- gate normalization fix, re-run at alpha=2.0 N=8192. GPU, ~3 min, $0. P_deflated=0.70.
- Lock-in per [[feedback-strategy-spec-formula-selftests]]: add m_3(alpha) = 1 + 3*alpha + alpha^2 formula to self-test registry.
- Closure: I-14 closes as gate-spec bug if R3-A HP; alpha=1 (MP edge) avoided regardless.

**Drill 3 -- Phase 0 0c R2 K-bump (PP-47 x PP-49 baseline_cos).**
- Note path: notes/research_phase0_0c_r2_kbump_pp47xpp49_baseline_2026-06-02.md
- TL;DR: v341 K-bump hypothesis FALSIFIED by closed-form derivation. baseline_cos at K=50 is dominated by neighbor-overlap structure (sigma=2.0, PLACE_FRAC=0.30), not K count. K-bump leaves baseline_cos UNCHANGED at 0.66-0.72. Correct fix is PLACE_FRAC reduction.
- R3-A recommended: `pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1` -- PLACE_FRAC 0.30 -> 0.10, K=50 unchanged, N=4096 unchanged. CPU, ~5 min, $0. P_deflated=0.55.
- Closure: 0c row NOT closed; sparse-code R3-A pending; K-bump hypothesis annotated as refuted by derivation.

**Lit-scan calibration penalty applied** per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis P capped at 0.50 across all three. R3 P_deflated values: 0.55 / 0.70 / 0.55 (lit-precedent rigorous for I-14 m_3 formula and sparse-code Tsodyks-Sejnowski; deflated 0.15 each for substrate-specific composition).

**Cross-drill insight:** TWO of three drills (I-14 and 0c) revealed that the failing experiment was correctly measuring the substrate behavior; the FAILURE was in the gate/hypothesis specification, not the substrate. This is a 2nd-order LVH-adjacent pattern (label-vs-honest at the cap_map/research-routing level rather than at the verdict-message level). Suggests routing-spec audit cadence: when smoke runs show measured values that closely match analytic predictions, re-audit the HP gate before accepting HF as evidence against substrate.

**Routing.** All 3 routing files in notes/research_*_2026-06-02.md as specified. Commit batched (3 files + this decisions log append) deferred to main thread for push.

**Next-drill candidate.** None auto-fired; user explicit batch complete. Next standing cadence: research_routing_v342_band_lifts_addendum probes A-E remain priorities.
- [2026-06-02] memristor_rram_hardware: notes/research_drill_memristor_rram_2026-06-02.md | HEADLINE: P1+P5 analog-feasible (10x-100x energy); P3+P4 GPU-native; oscillator exponential-capacity track highest upside
- [2026-06-02] federated_unlearning_regulatory: notes/research_drill_federated_unlearning_2026-06-02.md | HEADLINE: algebraic rank-1 cert occupies distinct niche vs DP-SGD/SISA/ZK-SNARK; pre-standardization regulatory window open; federated cert gap confirmed; P_deflated=0.38
- reservoir-computing capability-family scope -> notes/research_drill_reservoir_computing_2026-06-02.md | HEADLINE: No RC/ESN system unifies audit primitives + compositional algebra + one-shot writes; triple gap confirmed; P_deflated=0.65
- 2026-06-02: free-probability RRAM noise drill -> notes/research_drill_free_probability_rram_noise_2026-06-02.md; phase boundary sigma_g^2=1/alpha-1; P_deflated=0.55; exp_dev handoff written
- [2026-06-02] oscillatory phase-noise scaling (Kuramoto/ReRAM): sigma_phi_crit=pi/(2*n_c)~0.314rad; freq mismatch binding; 2 fab gens to 1000-node => notes/research_drill_oscillatory_phase_noise_scaling_2026-06-02.md

2026-06-02 arrhenius-paradox-deep-drill: notes/research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md -- Unified Brot+CK+Rams-Baron theory; mu alpha-invariant (HARD-PASS < 0.05); alpha-dep barrier E_a ~ N*(alpha_c-alpha); isochoric analog = constant alpha; two-envelope hidden-coupling confirmed; P_deflated=0.38
