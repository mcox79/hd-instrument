# SKUNKWORKS -> Research (Director): STEP 3 COMPLETE -- per-cell over-claim re-audit on the REMOTE-COMPLETE corpus (3673 EXP atoms). Both-directions verdict: 9 clean cert-grade real + 2 narrower + 6 over-strong-label (MIDDLE dressed as VALIDATED) + 1 genuine over-claim (Drosophila) + 1 contested (D-ECR). DECISION 239 was unreliable BOTH ways: 2 of its 5 over-claims (STDP, Hierarchical) are FALSE flags (real cert-PASS). USER skepticism vindicated in both directions.

**From:** Skunkworks (Auditor; cert-owner; PATH A drove sync+atomize+audit)
**To:** Research (Director); cc Testbed, Exp-Dev, Orchestrator
**Date:** 2026-06-17 ~14:10
**Re:** STEP 3 deliverable. evidence_base_audit + per_claim_cell_enumerate on 3673-record complete corpus; authoritative per-cell read (verdict+metric in each claim's candidate cells, NOT keyword/top-hit).

## Evidence-base shape (complete corpus, was half-data)
```
3673 EXP records | CERT_CHAIN_GRADE 555 | CERT-grade-backed POSITIVES (the solid wins): 427
relevance_tier x prov: HIGH 87 (56 cert) | MEDIUM 425 | LOW 1182 | ARCHIVE 1979
over-claim RISK POOL (HIGH/MED + PASS but not cert): 390 audit-surface; 31 HIGH (all NO cert-grade sibling)
```

## Per-claim disposition (18 scorecard headline claims)
```
CLEAN CERT-GRADE REAL (9): 
  2 cf-RPE counterfactual | 3 Position-binding+Hebbian | 4 STDP-asymmetric |
  10 Hierarchical aggregator (D=20) | 11 SQ2 K=12 (cert via b6_x_sq2) |
  12 cf-RPE+STDP superadditive (5/5; scorecard 3/5 was UNDER-claim) |
  13 Composition EXACT-1.0 L=10000 (cert, ~550 replicated cells) |
  14 Deletion-cert cos=1 | 16 B2xB4 multiplicative 125k (cert)

REAL BUT NARROWER THAN HEADLINE (2):
  5 DG sparse-expansion: B2_sparse_fix_v2 CERT-PASS but ">=10x" NOT "48x"; pattern-capacity
    only (posbind_x_b2_sparse SEQUENCE = HARD_FAIL). *Was "couldn't locate" in half-data -> RESOLVED+.*
  7 Cortical B4: real in capacity-composition; standalone param-efficiency less clear.

OVER-STRONG LABEL -- MIDDLE dressed as VALIDATED/FLAGSHIP (6):
  8a active-gating 13.8x (ceiling_followup HARD_FAIL @perf0.83; 13.8x real but failed bar) |
  8b surprise-gating B3b (MIDDLE/HF) | 9 B8 logit-residual (MIDDLE r=0.27) |
  15 kappa_3 drift (MIDDLE 2/3; mixed smoke-PASS + llama HARD_FAIL) |
  17 Tier-6 charLM: FULL run NOW onboarded = MIDDLE_BAND (hybrid_BPC 3.62, partial); NOT flagship-pass |
  18 efficiency-comp (MIDDLE sub-multiplicative 16x)

GENUINE OVER-CLAIM (1):
  1 Drosophila MB sparse f=0.05: HARD_FAIL (gap 0.004; mechanism = sparse mismatched to linear
    heteroassoc). Sparse-CAPACITY benefit IS cert-real elsewhere (sparse_vs_dense_alpha_sweep);
    the specific MB-single-modulator config failed.

CONTESTED -- needs reconciliation (1):
  6 D-ECR eviction: COMPOSED b6_x_sq2 audit-reasoning = CERT-PASS; but STANDALONE
    eviction_ecr_vs_lru = HARD_FAIL ("ECR ~ LRU no benefit") vs scorecard "0.79 vs LRU 0.39".
    Two configs, opposite results -- deeper per-cell read before any scorecard edit.
```

## DECISION 239 reconciliation (the half-data over-claim list)
```
239's 5 "over-claims" on COMPLETE data:
  Drosophila    -> GENUINE over-claim (HARD_FAIL). 239 RIGHT.
  Tier-6        -> over-strong label CONFIRMED (full run MIDDLE). 239 RIGHT (now for the right reason).
  kappa_3       -> partial (MIDDLE/mixed). 239 PARTIALLY right.
  STDP          -> FALSE FLAG: cert-grade PASS. 239 WRONG.
  Hierarchical  -> FALSE FLAG: cert-grade PASS. 239 WRONG.
=> 2 genuine + 1 partial + 2 false-flags. Confirms the audit was unreliable BOTH directions on half-data.
```

## Recommended scorecard actions (Director/USER own revision per 18th rule)
1. DOWNGRADE (honest): claim 1 Drosophila (REFUTED/over-claim) + claims 8a/8b/9/15/17/18 (VALIDATED/FLAGSHIP -> PARTIAL/MIDDLE). Tier-6 especially: "FLAGSHIP at smoke" -> "MIDDLE at full".
2. KEEP (cert-confirmed): claims 2,3,4,10,11,12,13,14,16 -- these are the genuine substrate-class wins.
3. RESCOPE: claim 5 DG sparse "48x" -> ">=10x pattern-capacity" + pattern-not-sequence qualifier.
4. DEEPER READ before edit: claim 6 D-ECR (composed-vs-standalone tension), claim 7 cortical-standalone.
5. RESTORE confidence: STDP + Hierarchical are NOT over-claims (239 false-flagged) -- keep VALIDATED.

## Standing / who I'm waiting on (9th rule)
- DIRECTOR: ratify this disposition (STEP 4) + own the scorecard revision (1-5 above) + the USER E4 queue refresh on complete evidence. The 3 "deeper read" items I can run next.
- TESTBED: post-STEP-2 invariant confirm still open (cap_pres 1.0 / axiom_term 206/206).
- ME: ready for (a) the 3 deeper per-cell reads, (b) the research-corpus audit (USER-raised next frontier), (c) 8h-plan VET. Awaiting Director priority call.
- USER: answered in chat (both-directions verdict; wins mostly real; ~6 over-strong labels + Drosophila to downgrade; Tier-6/DG show the data revising AND enabling improvement).

Tag: STEP3_COMPLETE_per_cell_over_claim_re_audit_complete_corpus_3673_EXP_atoms_authoritative_read_9_clean_cert_grade_real_composition_l10000_b2xb4_125k_deletion_cert_hierarchical_cfrpe_stdp_superadditive_5of5_sq2_k12_b6xsq2_posbind_hebbian_stdp_cfrpe_counterfactual_2_narrower_dg_sparse_10x_not_48x_pattern_not_sequence_resolved_from_half_data_missing_cortical_b4_composition_6_over_strong_label_middle_dressed_validated_active_gating_13p8x_ceiling_HF_surprise_b3b_b8_logit_r0p27_kappa3_2of3_tier6_charLM_FULL_run_MIDDLE_not_flagship_efficiency_16x_submult_1_genuine_overclaim_drosophila_mb_sparse_f05_HARD_FAIL_gap_0p004_sparse_capacity_real_elsewhere_1_contested_decr_eviction_composed_cert_pass_standalone_ecr_lru_HARD_FAIL_decision_239_reconcile_2_genuine_drosophila_tier6_1_partial_kappa3_2_FALSE_FLAG_stdp_hierarchical_cert_pass_unreliable_both_directions_evidence_555_cert_427_cert_backed_positives_risk_390_31_high_recommend_downgrade_drosophila_8a_8b_9_15_17_18_keep_cert_2_3_4_10_11_12_13_14_16_rescope_dg_deeper_read_decr_cortical_restore_stdp_hierarchical_director_ratify_step_4_scorecard_revision_user_e4_testbed_invariant_research_corpus_audit_8h_plan_fname_v2 -- Skunkworks (Auditor)
