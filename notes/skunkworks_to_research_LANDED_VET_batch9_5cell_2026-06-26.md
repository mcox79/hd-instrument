# Skunkworks landed-VET batch 9 (5 cells) — 2026-06-26

Per-arm OFF-DATA independent recompute (no verdict_msg shortcuts) on 5 cells. A5-gated Store writes complete; commit `ade1bd58`.

**CERT 619 → 622 (+3).** Axiom 206 stable. cap_pres 6/6 stable. Total atoms 177429 → 177435 (+6 explicit additions). All 6 atoms survived fresh-load post-commit (no NULL-seam).

## Tier ruling summary

| # | Cell | Tier | CERT delta | Atom qualified-id |
|---|------|------|-----------|-------------------|
| 1 | `phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu` | **CHAIN_GRADE** | +1 | `math::T3/EXP_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu_chain_grade_rec_1p0000_cv_0_3seeds_alpha_4_h10x_substrate_only_v2b_OOM_rescue` |
| 2 | `edge_importance_v5_CFU_counterfactual_utility_v1` | **MEASURED_MECHANISM** | 0 | `math::T3/EXP_edge_importance_v5_CFU_counterfactual_utility_v1_measured_mechanism_first_fairness_passing_mechanism_in_family_sel_unretr_0p048_below_0p15` |
| 3 | `multihop_barrier1_M2_M3_M1_combined_5arm_v1` | **HONEST_NEGATIVE_INFRA_BUG (META RULE)** | 0 | `meta::T_methodology/META_RULE_CHAIN_GEN_FEASIBILITY_PRE_FLIGHT_for_multihop_chain_cells_max_depth_ge_5_disallow_filter_must_be_pre_dispatch_checked` |
| 4 | `gap3_cls_two_tier_HOPFIELD_consolidation_v1` | **HONEST_NEGATIVE_BY_CONSTRUCTION_SATURATION** | +1 | `math::T3/EXP_gap3_cls_two_tier_HOPFIELD_consolidation_v1_honest_negative_by_construction_saturation_n_dim_8192_n_cat_5_n_train_20_trivially_separable` |
| 5 | `stage3_hrr_involutive_systematic_generalization_v1` | **HONEST_NEGATIVE_MECHANISM_NULL** | +1 | `math::T3/EXP_stage3_hrr_involutive_systematic_generalization_v1_honest_negative_mechanism_null_hrr_inv_0p0067_eq_baseline_0p0067_eq_chance_plus_0p0017` |
| 5b | Stage 3 HRR guardrail META | discipline_meta | 0 | `meta::T_methodology/META_RULE_HRR_INVOLUTIVE_SYSTEMATIC_GENERALIZATION_REFUTED_AT_REGIME_n_dim_8192_n_entities_200_n_verbs_10_n_train_500_heldout_obj_frac_0p20_feature_overlap_protos` |

## Per-cell off-data recompute

### Cell 1 — multi-bank K=4 N=8192 v2c GPU → CHAIN_GRADE

Per-seed recall_at_1: `[1.0, 1.0, 1.0]` (seeds 11, 13, 19). Rederived rec_mean=1.0000, cv=0.0000 — matches cited.
- M_facts=32768 V_C=10240 alpha_N=4.0 headroom=10x N_DIM=8192 K_banks=4
- `_llm_forward_calls_at_inference = 0` (all seeds); substrate_only_ok=True
- GPU asserted (RTX 4060 Ti); peak_mem_mb=1929 (well under 8GB budget)
- HP_MB_REC_MIN >= 0.95 PASS; HP_MB_CV_MAX <= 0.05 PASS; EXPECTED_N_UNITS=3 PASS

**Q-discipline (by-construction-saturation check):** rec=1.0 IS at metric cap, but this is the PREDICTED band for the pre-registered mechanism — K=4 bank sharding at alpha=4 is the regime under test. v2b OOM at N=16384 demonstrated the mechanism CAN fail to even run; v2c rescues by halving N. The capacity claim is alpha-relative; alpha=4 headroom=10x preserves the prior K=8192 single-bank chain-grade band (`WM multibank K=8192 3-seed harvest CHAIN_GRADE` already in math corpus). This is an extension to the K=4-shard regime, not a free saturation pass.

### Cell 2 — edge_imp v5 CFU → MEASURED_MECHANISM (with miscite flag-back)

Per-seed CFU_LEAVE_ONE_OUT:
- `cor_importance_magnitude`: [0.01755, -0.03585, -0.02818] → mean -0.0155 (matches cited)
- `recall_old_RETRIEVED`: [0.795, 0.780, 0.775] → mean 0.7833 (matches cited 0.783)
- `recall_old_UNRETRIEVED`: [0.715, 0.740, 0.750] → mean 0.7350 (matches cited 0.735)
- **Rederived sel(retr-unretr) = 0.7833 - 0.7350 = +0.0483**

**MISCITE caught:** verdict_msg cites `sel=+0.037`. Rederived clean (retr-unretr)=+0.0483. Gap ~0.011. Candidate alternative formulas: median (0.040), trimmed mean, sel-vs-recent (0.0167), sel-lift-over-rand (+0.0700), sel-lift-retr (+0.0333). None reproduce 0.037 exactly.
- Disposition HOLDS regardless: both 0.037 and 0.0483 are well below the 0.15 PASS floor.
- **Flag-back to cell-author:** clarify `sel_unretr` formula in v6 or successor.

**Why MM not honest-negative:** v5 is the FIRST mechanism in the edge-importance family (v1/v2/v3) to PASS FAIRNESS with structural margin (cor=-0.0155 << 0.30 gate). Brain-grounded (Tonegawa optogenetic engram leave-one-out analog). Structurally orthogonal to magnitude by construction. Companion to existing HONEST_BOUND atom (`substrate's max sel_unretr asymmetry extractable from retrieval-trace alone` = +0.083 trace-only fairness-FAILING). v5 CFU establishes "fairness-PASSING importance signal max +0.0483 at v5 regime" as a companion bound — fairness-passing variant is structurally weaker than fairness-failing trace-only.

### Cell 3 — multihop_barrier1 → HONEST_NEGATIVE_INFRA_BUG (META RULE atomized)

All 3 seeds aborted at setup: `BLOCKING make_deep_chains: only 200/500 generated for V=200 disallow|=0 max_depth=8`. arms list EMPTY across all seeds. elapsed_s=0.732 total. Mechanism NEVER exercised.

- **Does NOT count as 6th Barrier 1 refutation.** Counter remains 5 mechanism-refutations + 1 infra-bug.
- Atomized as META RULE `CHAIN_GEN_FEASIBILITY_PRE_FLIGHT`: multi-hop / chain-based cells with max_depth >= 5 and disallow-filter MUST pre-flight feasibility (analytic OR tiny-N PoC arm OR graceful-degradation in-cell). Skunkworks SCHEMA-VET will reject pre-regs without one of these.

### Cell 4 — HOPFIELD consolidation → HONEST_NEGATIVE_BY_CONSTRUCTION_SATURATION

Per-arm (3 seeds: 11, 13, 19):
- ARM_BASELINE_HEBBIAN: [1.0, 1.0, 1.0] mean=1.0000 cone=[1.0, 1.0, 1.0]
- ARM_HEBBIAN_SLOW: [1.0, 1.0, 1.0] mean=1.0000 cone=[0.457, 0.458, 0.459]
- ARM_HOPFIELD_REPLAY_SLOW: [1.0, 1.0, 1.0] mean=1.0000 cone=[0.497, 0.490, 0.490]
- ARM_HOPFIELD_GENERATIVE_REPLAY: [1.0, 1.0, 1.0] mean=1.0000 cone=[0.408, 0.408, 0.407]

Rails violated: HF_BASELINE_MAX<=0.5 (baseline=1.0), lift_over_baseline=0, cone in [0.50, 0.95] (best=0.4922 below floor).

**Regime trivially separable at N_DIM=8192 / N_CAT=5 / N_TRAIN=20.** Even random Hebbian (no replay, no consolidation) gets 100% heldout. Hopfield mechanism cannot be discriminated from baseline at this regime.

Not a mechanism refutation — REGIME MISMATCH. Counts as honest_negative per cert-disposition framework (clean negative, not a bug, bound on regime not mechanism). Cell-author follow-up: increase N_CAT (5→50+), decrease N_DIM (8192→512/1024), increase noise, OR verify discriminator survives scale before full dispatch per USER #B 2026-06-26 feedback.

### Cell 5 — HRR involutive systematic generalization → HONEST_NEGATIVE_MECHANISM_NULL

Per-arm (3 seeds: 11, 13, 19):
- ARM_BASELINE: [0.00, 0.01, 0.01] mean=0.0067
- ARM_HRR_INVOLUTIVE: [0.00, 0.01, 0.01] mean=0.0067
- ARM_NEAREST_NEIGHBOR_INTERPOL: [0.00, 0.00, 0.00] mean=0.0000

chance_acc=0.005; HRR mean = baseline mean = chance + 0.0017. HRR composition adds ZERO signal over baseline.

**magnitude_coupling_cor per_seed: [0.0453, 0.1975, -0.0691] mean=0.0579** — LOW, rules out by-construction-saturation. The HRR mechanism is genuinely non-functional at this regime; not artificially saturated.

PASS bars: HP_heldout_floor>=0.50 FAIL (0.0067); HP_composition_lift_min>=0.10 FAIL (0.0067 over NN, 0.0017 over chance). HP_baseline_ceiling<=0.15 PASS. HP_baseline_no_leak=True PASS.

**Stage 3 compositional understanding implication:** HRR composition via unbind-chain on feature-overlap prototypes for systematic generalization (heldout-object prediction) is REFUTED at this regime. Stage 3 track needs a DIFFERENT composition mechanism. Candidates: schema-based composition (cortical column analog), multi-bank K-sharding with role-specific banks (extending atom 1 chain-grade), episodic-memory NN-attention with explicit role coercion, Hebbian-superposition with grounded role-filler binding.

Companion META RULE atomized (atom 6): future Stage 3 pre-regs must NOT propose ARM_HRR_INVOLUTIVE for heldout-object systematic-generalization at this regime band WITHOUT one of: (A) regime variant outside refuted band, (B) revival angle addressing unbind-chain failure mode, (C) external pretrained-encoder grounding.

## Cross-arc META atomization summary

- **META RULE atom 3:** `CHAIN_GEN_FEASIBILITY_PRE_FLIGHT` — applies to all multi-hop/chain cells max_depth>=5 with disallow-filter.
- **META RULE atom 6:** `HRR_INVOLUTIVE_SYSTEMATIC_GENERALIZATION_REFUTED_AT_REGIME` — Stage 3 composition pre-reg guardrail.

Both ratified by Skunkworks 2026-06-26 as CERT-neutral discipline_meta.

## Flag-backs to roles

- **Research (cell 2):** miscite of sel_unretr in verdict_msg (cited 0.037 vs rederived 0.0483 from per_seed mean). Disposition holds, but flag for v6 successor — clarify the sel formula. Possible: median, trimmed mean, sel-recent, sel-lift-over-rand. None reproduce 0.037 exactly.
- **Research (cell 3):** Barrier 1 counter stays at 5 mechanism-refutations + 1 infra-bug. Atomized META rule applies to YOUR next pre-reg for multi-hop work.
- **Research (cell 4):** by-construction-saturation regime; ratified honest-negative on REGIME, not mechanism. Hopfield consolidation needs a harder regime to be discriminated. Apply USER #B 2026-06-26 "discriminator must survive scale" — preview at full-N before dispatch.
- **Research (cell 5):** HRR involutive is OFF the table for Stage 3 systematic-gen at this regime band. META rule 6 will SCHEMA-VET reject future pre-regs in the refuted regime without revival angle.
- **cert_ledger_writer maintainer (testbed or infra):** two API contract bugs surfaced — (a) `cert_status='custom_meta'` rejected, valid values list does not include the META rule case (suggest add); (b) chain_grade row append checks `expected_post == live` AFTER Store flush already incremented live count, causing off-by-one rejection. Atom writes succeeded; ledger rows partially appended. Non-fatal but recommend hardening for Phase 3.

## Auto-mode tracking

- 5 cells reviewed in single batch under wall budget.
- A5 PRE/POST verified, fresh-load gate passed, path-scoped commit clean.
- Commit: `ade1bd58` (tools/skunkworks_atomize_landed_vet_batch9_5cell_2026-06-26.py + 5 Store partition + audit + ledger files).
- Heartbeat refreshed (skunkworks.timestamp).

— Skunkworks, 2026-06-26 ~landed-VET batch 9 complete. CERT 622/177435.
