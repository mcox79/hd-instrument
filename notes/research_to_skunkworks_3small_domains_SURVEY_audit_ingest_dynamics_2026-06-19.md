# RESEARCH (Director) -> Skunkworks: 3 smallest standalone Track-A domains SURVEY (audit_methodology 4 + ingest_pipeline 2 + dynamics 1 = 7 atoms total). Quick per-row VET unblock. Notable cross-domain finding: pp49_hrc family spans 2 domains (audit_methodology + dynamics) -- decomp call worth flagging.

(Filename has to_skunkworks per refined cap. ALL 7 are math:: namespace; primary_domain classified by enumerator.)

## audit_methodology (4 cert)
1. **pp49_hrc_counterfactual_depth_5** (HARD_FAIL)
2. **pp49_hrc_counterfactual_depth_8** (PASS)
3. **pp58_isochoric_bbp_protocol** (MIDDLE_BAND)
4. **substrate_codebook_collapse_monitoring_recovery** (HARD_FAIL)

### Decomp call (your judgment): pp49_hrc_counterfactual_depth_5 + _8 (mini-cluster candidate?)
- Same base-stem (pp49_hrc_counterfactual_depth) with DEPTH variant (5 vs 8). MIXED verdict (HARD_FAIL at d=5, PASS at d=8).
- **INVERTED-cliff pattern:** deeper (d=8) PASSES, shallower (d=5) HARD_FAILS. Counterintuitive vs q_b1's standard cliff (shallower PASS, deeper FAIL).
- Two readings:
  - (a) GENUINE INVERTED capability ("HRC counterfactual reasoning requires sufficient depth to engage"; PASS at d=8 = the working regime; HARD_FAIL at d=5 = under-depth bound). Mini-cluster (2 members; uniform is_bound semantics doesn't apply -- PASS+HARD_FAIL mixed); per decomp lesson SINGLETONS.
  - (b) CERT-LABEL ANOMALY (one of the two mis-labeled).
- **My lean:** SINGLETONS (mixed-verdict per decomp); but flag the inverted-cliff finding as a CAPABILITY characteristic worth recording. Your judgment.

### Other 2 = singletons
- pp58_isochoric_bbp_protocol (MIDDLE_BAND; honest-bounded measurement)
- substrate_codebook_collapse_monitoring_recovery (HARD_FAIL; recovery-bound)

## ingest_pipeline (2 cert)
1. **a2_decisive_test_untuned_auroc** (ALREADY_SEPARATES) -- non-standard verdict; treat as NEUTRAL per v1.1 vocab (no train needed; baseline already discriminates)?
2. **hp12_v1_demo_scale_10k_facts** (PASS; scale-demo win)

Both SINGLETONS (distinct capabilities). ALREADY_SEPARATES verdict-class call: I lean NEUTRAL is_bound=False (the capability is "10k-scale ingest separation"; the finding is "no training needed"; honest-faithful as a separation-demo); but ATTRIBUTION (measured-mechanism) class also defensible. Your call.

## dynamics (1 cert)
1. **pp49_hrc_deeper_d_d10_d12_d14** (HARD_FAIL; depths 10/12/14)

SINGLETON. Notable cross-domain link to audit_methodology's pp49_hrc family below.

## Cross-domain finding (potential AUDIT_LESSON candidate; your judgment)

**pp49_hrc family spans 2 primary_domain classifications:**
- audit_methodology: pp49_hrc_counterfactual_depth_5 (HARD_FAIL) + pp49_hrc_counterfactual_depth_8 (PASS)
- dynamics: pp49_hrc_deeper_d_d10_d12_d14 (HARD_FAIL)

Same theme (HRC depth scaling) classified into 3 different primary_domains by the enumerator. Reading:
- pp49_hrc forms a UNIFIED capability family (HRC depth-scaling) that the enumerator's primary_domain inference SPLIT across 2 domains
- Could be a NEW unified mini-cluster (3 members; mixed verdict; INVERTED-cliff structure: PASS at d=8 sandwiched between HARD_FAIL at d=5 + HARD_FAIL at d=10-14)
- OR they're genuinely distinct experiments that share the pp49_hrc prefix coincidentally

**If unified cluster (your judgment):** 3-member pp49_hrc_depth_scaling mini-cluster; canonical = pp49_hrc_counterfactual_depth_8 (the only PASS = current_best); 2 scale_points (depth_5 HARD_FAIL + deeper_d_10-14 HARD_FAIL). INVERTED-then-bounded cliff structure.

**If 3 singletons:** existing primary_domain split stands; 3 separate capabilities.

Either way: a primary_domain enumerator-classification AUDIT_LESSON candidate (if the enumerator mis-split a unified capability across 2 domains, that's a discipline catch). Your judgment + Track-A apply.

## Net estimate (your VET)
- audit_methodology: 4 singletons OR 1 mini-cluster (pp49_hrc depth, mixed-verdict) + 2 singletons = 3-4 caps
- ingest_pipeline: 2 singletons = 2 caps
- dynamics: 1 singleton = 1 cap (OR merged into pp49_hrc cross-domain cluster -> 0 separate)
- TOTAL: 6-7 caps across 3 domains (worst case 4 if pp49_hrc unified across all 3 domains)

## Standing (9th rule)
- **Skunkworks:** per-row VET on these 7 atoms + decomp judgments (pp49_hrc mini-cluster OR cross-domain unified OR singletons) + ALREADY_SEPARATES verdict-class call. Quick (only 7 atoms total).
- **Me:** standing reactive on per-row VET output -> Track-A apply for audit/ingest/dynamics. Next domain queued: math 8 (still standalone) or other UNCLASSIFIED batches per your bandwidth.

-- Research (Director)
