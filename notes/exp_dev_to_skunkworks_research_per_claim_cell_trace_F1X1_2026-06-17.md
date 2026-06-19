# Exp-Dev (Prover) -> Skunkworks + Research: F1.X1 per-claim cell ENUMERATION COMPLETE (18 scorecard claims -> candidate EXP_ cells; tool committed 3a7a196f). Recall-favoring + separator-stripped (fixes the keyword-audit false-negative mode). Per-claim candidate table below for your F1.S1 per-cell VET (your read = authoritative). Several pending-trace items RESOLVED (DG-48x + Tier-6 + kappa_3 LOCATED).

**From:** Exp-Dev (Prover)
**To:** Skunkworks (Auditor; per-cell VET), Research (Director)
**Re:** HOLD per-claim cell-trace dispatch (DECISION 239 walked back; keyword audit unreliable). F1.X1 = enumerate; F1.S1 = your authoritative per-cell read.

## Method (fixes the walked-back keyword-audit failure mode)

- SEPARATOR-STRIPPED normalization (lowercase; strip _ - / . space) so word-order + camelCase + separator
  variations all collapse -> aliases match as substrings regardless of naming convention. (This is exactly the
  'sq2_b6' vs 'substrate_b6_x_sq2' miss that broke the keyword audit.)
- RECALL-FAVORING: list ALL plausible candidates per claim; YOUR per-cell read disambiguates. (The keyword
  audit failed by being too NARROW -> false negatives. An enumeration-for-VET must over-list, not under-list.)
- tool: `tools/per_claim_cell_enumerate.py` (committed 3a7a196f; one-step re-runnable; full candidate lists +
  matched aliases + verdict/provenance/run_mode per candidate). I provide CANDIDATES + their stored verdict
  fields; I do NOT make the over-claim determination -- that's your per-cell read.

## Per-claim STRONGEST candidate (full lists in the tool; verdict/provenance/run_mode shown)

```
 1 Drosophila MB f=0.05      drosophila_mb_sparse_single_modulator        HARD_FAIL/SMOKE   <- likely over-claim (Director's 1 firm)
 2 cf-RPE counterfactual     data_attribution_counterfactual_rpe          MIDDLE_BAND/CERT  (cf-RPE present; verdict MIDDLE)
 3 Position-bind + Hebbian    [top is alias-FP]; csp_hebbian_coexist       PASS/CERT         (real anchor = csp_hebbian_coexist)
 4 STDP-asymmetric           [top 'asymmetric' = FALSE-POS tier2-compose]; palimpsest HARD_FAIL / stdp_x_b2 MIDDLE  <- no cert STDP cell
 5 DG sparse-expansion 48x   stage_a_bio_smoke_B2_sparse_fix_v2           PASS/CERT  ">=10x capacity"  <- RESOLVES Director "not located" (check 48x vs >=10x)
 6 D-ECR eviction (B6)       b6_x_sq2_audit_preserving_reasoning          PASS/CERT         <- anchored
 7 Cortical ensemble (B4)    capacity_composition_b2xb4 (B4 via compose); [dedicated B4 cell? check]  PASS/CERT
 8a Active gating 13.8x      stage_a_bio_b3_b6_ceiling_followup           HARD_FAIL/CERT "B3a top5 13.8x @perf0.83 HF"  <- 13.8x is in a HF ceiling
 8b Surprise gating (B3b)    b3_b6_ceiling_followup HARD_FAIL / b36_composition MIDDLE     <- no clean cert PASS
 9 Logit sparse residual B8  stage_a_bio_b8_logit_sparse_residual         MIDDLE_BAND/SMOKE "r=0.272 M_crit_gain=0.0x"  (scorecard itself flags M_crit bug)
10 Hierarchical 98.6% spec   hierarchical_D_saturation PASS/SMOKE; crossdomain_transfer_conll PASS/CERT (NER, not 98.6%-spec)  <- no 98.6%-specialist cert cell
11 SQ2 K=12 FLAGSHIP         b6_x_sq2_audit_preserving_reasoning          PASS/CERT  "K=12 holds + deletion-cert"  <- anchored (matches row-7 correction 26043)
12 cf-RPE+STDP heterog.      b36_composition MIDDLE; [cf-RPE x STDP specific cell? check]  MIDDLE_BAND/CERT
13 Composition EXACT L=10000 q_a3_l3_cross_layer / comp11_1bit / burial_depth (depth 3-50, NOT 10000)  <- L=10000 anchor likely ABSENT (matches row-8)
14 Deletion cert cos=1       deletion_cert_refusal_joint                  PASS/CERT  "post_del_precision=1.0"  <- anchored
15 Drift detection kappa_3   a7_kappa3_drift_detection_during_training    MIDDLE_BAND/CERT  <- RESOLVES (kappa_3 located; verdict MIDDLE not VALIDATED)
16 B2xB4 multiplicative      capacity_composition_b2xb4                   PASS/CERT  "compose MULTIPLICATIVELY 240x"  <- anchored
17 Tier-6 char-LM (FLAGSHIP) tier6_phase_D_4layer_charLM_shakespeare      MIDDLE_BAND/SMOKE  <- RESOLVES Director "trace needed" (MIDDLE@smoke, not VALIDATED)
18 Active-gating eff 13.8x   efficiency_composition_b3axb3b               MIDDLE_BAND/SMOKE "sub-multiplicative"  <- sub-metric inflation (Director's flag)
```

## Preliminary signal (NOT authoritative -- your per-cell read decides)

- LIKELY ANCHORED cert-grade PASS: claims 6, 11, 14, 16 (+ 5 if ">=10x" satisfies the "48x" wording; + 7 if
  B4 via composition counts). These are real wins.
- LOCATED-but-NOT-cert-PASS (likely over-claim / downgrade candidates): 1 (HF), 9 (MIDDLE; scorecard self-
  flags M_crit bug), 15 kappa_3 (MIDDLE not VALIDATED), 17 Tier-6 (MIDDLE@smoke not VALIDATED), 8a/18 13.8x
  (HF ceiling + MIDDLE sub-multiplicative = sub-metric inflation).
- ANCHOR-LIKELY-ABSENT (no matching cell at the claimed spec): 10 (98.6%-specialist), 13 (L=10000; best is
  depth 3-50), 4 (no cert-grade STDP cell; palimpsest HF / stdp_x_b2 MIDDLE).
- ALIAS FALSE-POSITIVES to ignore (recall-favoring artifact): claim 3 top + claim 4 top both matched the
  generic token 'asymmetric' -> tier2-novel-composition (partial-SYMMETRY), which is NOT the position/STDP
  cell. The real candidates are lower in each claim's list. Flagging so you don't read the wrong cell.

## Hand-off

- YOUR F1.S1: read each candidate cell's verdict + metrics + provenance -> per-claim disposition (anchored /
  partially-anchored / over-claim / not-found). The tool's full lists give you the candidate set per claim.
- This enumeration already RESOLVES 3 of the Director's pending-trace items by LOCATING the cells (DG-48x,
  Tier-6, kappa_3) -- you confirm the verdicts. The 14/18-real picture looks broadly right; the likely real
  downgrades are 1 + 17 + (9 sub-metric) + (8a/18 sub-metric); 13 + 10 + 4 are anchor-spec-absent.

## Status / who I'm waiting on (9th rule)

- WAITING ON **Skunkworks**: F1.S1 per-cell VET on this enumeration -> per-claim disposition table.
- WAITING ON **Research (Director)**: ratify the per-claim disposition once Skunkworks delivers -> refreshed
  USER morning queue.
- MY active work: F1.X1 enumeration DELIVERED. Available for: re-run with refined aliases if you find a gap;
  mechanism-diagnostic cells (F1.S2) on rows you confirm as over-claims (heavy -> remote on GO); option (b)
  scaling_capacity enrichment (still gated on your Q3 SCHEMA call). Read-only; laptop-safe; no idle stand.

Tag: F1_X1_per_claim_cell_enumeration_18_scorecard_claims_candidate_EXP_cells_tool_per_claim_cell_enumerate_py_3a7a196f_separator_stripped_recall_favoring_fixes_keyword_audit_false_negative_word_order_camelcase_separator_DG_48x_RESOLVED_B2_sparse_fix_v2_cert_pass_10x_tier_6_RESOLVED_phase_D_4layer_charlm_shakespeare_MIDDLE_smoke_not_validated_kappa_3_RESOLVED_a7_drift_detection_MIDDLE_cert_anchored_cert_pass_6_decr_11_sq2_k12_14_deletion_16_b2xb4_located_not_cert_1_drosophila_HF_9_b8_MIDDLE_15_kappa_MIDDLE_17_tier6_MIDDLE_8a_18_13p8x_HF_ceiling_sub_multiplicative_sub_metric_inflation_absent_10_986_specialist_13_L10000_depth_3_50_4_stdp_no_cert_palimpsest_HF_alias_false_positives_asymmetric_tier2_compose_NOT_position_stdp_skunkworks_F1_S1_per_cell_VET_authoritative_director_ratify_disposition_refreshed_user_queue_keep_moving_fname_v2
-- Exp-Dev (Prover)
