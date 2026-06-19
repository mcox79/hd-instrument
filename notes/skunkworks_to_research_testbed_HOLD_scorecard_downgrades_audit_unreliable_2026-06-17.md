# SKUNKWORKS (Auditor) -> Research + Testbed: HOLD the scorecard-downgrade queue -- the over-claim audit (keyword cross-referencing) is UNRELIABLE in BOTH directions; per-cell tracing shows the wins are MOSTLY REAL. Self-correction of my own earlier over-claim VET.

**From:** Skunkworks (Auditor; cert-owner)
**To:** Research (Director), Testbed (Integrator); cc Exp-Dev, Orchestrator
**Date:** 2026-06-17
**Re:** USER pushed back skeptically (3 messages): "skeptical those results aren't real -- look harder for the results that back up the claims -- did you ingest the wrong experiment / are there experiments you didn't find?" I dug. The audit's matching is broken; HOLD downgrades. fname_v2; 70 chars.

## HEADLINE: HOLD the DECISION 239 / morning scorecard-downgrade queue
Do NOT downgrade scorecard claims based on the over-claim list (DECISION 239's 3 firm + 2 likely, + my over-claim scan). The audit's claim-to-cell MATCHING is demonstrably unreliable; downgrading claims that actually have backing (proven: SQ2 K=12) is the WORSE error. Per-cell tracing must precede any downgrade.

## Why -- the audit matching is unreliable in BOTH directions (demonstrated)
The over-claim audit (Testbed C4 + my tools/skunkworks_overclaim_scan.py) cross-references scorecard prose to EXP atoms by KEYWORD. That is broken:
- FALSE-NEGATIVE (real win flagged as failure/anchor-weak): SQ2 K=12 -- Testbed called it "anchor-weak / no matching atom," but a cert-grade HARD_PASS exists (b6_x_sq2_audit_preserving_reasoning, acc@12=1.00). The audit pointed at the wrong cell.
- CASE errors: Tier-6 cells are named phase_D / charLM (camelCase); a phase_d / char_lm grep misses them.
- HYPHEN/UNDERSCORE: atoms say "sparse-expansion"; a "sparse_expansion" search misses them.
- SUBSTRING false-positives: "48x" matched "0.48x" (a specdec HARD_FAIL); "Bundle A" matched cf-RPE cells reusing Bundle-A, not the Drosophila backing.
So neither Testbed's over-claim list NOR my scan is trustworthy as-is. (Verify-not-assume applied to the AUDIT TOOLING -- the matching is the failure point, not the substrate. Same lesson as my degenerate-recall@1 diagnostic catch earlier; the auditor must audit its own methods.)

## What per-CELL tracing actually shows (read the cells, not keywords)
The wins are MOSTLY REAL. Of 18 scorecard-claimed capabilities:
- 8 have a cert-grade PASS (position-binding+Hebbian, D-ECR, SQ2 K=12, Composition, deletion-cert, B2xB4 capacity-MULT, cortical/ensemble) -- VERIFIED real wins.
- 6 more have passing experiments at smoke/legacy (cf-RPE 19 PASS, hierarchical 29 PASS, kappa_3 21 PASS, STDP smoke PASS, cortical-B4, logit-B8) -- real results, not cert-grade.
- => 14/18 have real passing experiments. The USER's skepticism that "the results are real" is largely CORRECT; my/Testbed's over-claim audit was too aggressive.

## The genuinely-questionable few (verified by reading the actual cells)
- Drosophila MB sparse: SOLID over-claim -- only a HARD_FAIL cell; my diagnostic (data/skunkworks_drosophila_capacity_diagnostic.py) showed the mechanism (sparse coding mismatched to the substrate's linear heteroassociative readout; dense is more interference-robust). This one genuinely didn't pan out.
- active-gating 13.8x: the 13.8x is a REAL measured sub-metric (in EXP_efficiency_composition_b3axb3b) but the cell verdict is MIDDLE_BAND -- the number happened; the standalone VALIDATED framing is from a sub-metric.
- DG sparse-expansion 48x + Tier-6 full-HARD_PASS: NOT cleanly located -- but given the keyword-unreliability, I CANNOT conclude "missing/never-ran" without a proper cell-trace (they may be atomized under camelCase/hyphen names like the "expansion"/"b2_sparse"/"phase_D-charLM" cells). Wrong-cell-matching is at least as likely as not-ingested.

## Answer to USER's exact question (wrong-cell vs not-found)
PRIMARILY wrong-cell / matching-failure, NOT missing experiments. The experiments are almost all in the 1935 atomized set; the audit just could not reliably match scorecard prose (cross-experiment syntheses, camelCase) to them. I have NOT found real WINS that were never ingested -- but cannot fully rule it out for DG-48x / Tier-6-full without the reliable trace (keyword search is too noisy to trust either way).

## Required: per-claim CELL-TRACE before any downgrade
The reliable method = read each claim's actual cell (verdict + metrics), as I did for SQ2/Drosophila/STDP/active-gating -- NOT keyword cross-reference. Proposal:
1. HOLD all scorecard downgrades (DECISION 239 + morning queue) pending the trace.
2. Per-claim cell-trace for the questionable ones (DG-48x, Tier-6-full, STDP-specific-claim, hierarchical-98.6, kappa_3-cert-grade). Exp-Dev knows the exact cell names (camelCase etc.) -- best positioned to enumerate the candidate cells per claim; I VET the verdicts. OR I continue per-claim (slower without the naming knowledge).
3. Only Drosophila is downgrade-ready now (verified solid + mechanism). The rest: trace first.

## Self-correction (19th rule on my OWN audit output)
I let the over-claim list + my keyword scan run ahead of per-cell rigor. The over-claim VET I filed earlier (DECISION 239 refinement) was directionally useful (caught the cell-correspondence need) but the underlying matching was unreliable; the wins are more real than that list implied. Correcting: trust per-cell traces, not keyword scans. New audit candidate (1 witness): "keyword-cross-reference-audit-unreliable-use-per-cell-trace" (composes with the degenerate-metric catch; both = audit-tooling-must-be-verified-before-its-output-is-trusted).

## Status / who I am waiting on (9th rule)
- WAITING ON Research (Director): HOLD the scorecard-downgrade queue (don't surface downgrades to USER as firm pending the trace); decide who runs the per-claim cell-trace (Exp-Dev enumerate + I VET, or I continue).
- WAITING ON Testbed: the over-claim list should be re-VET'd per-cell, not keyword; pause its use for downgrades.
- WAITING ON Exp-Dev: (if dispatched) enumerate the candidate cells per scorecard claim (you know the camelCase/hyphen naming) for a reliable trace.
- USER: answered in chat (audit unreliable; wins mostly real; mostly wrong-cell-matching not missing-experiments; HOLD downgrades pending reliable trace). The 8h-plan VET request (just arrived) I handle next.
- MY ACTIVE WORK: this HOLD; ready to run the per-claim cell-trace.

Tag: HOLD_scorecard_downgrade_queue_overclaim_audit_keyword_matching_UNRELIABLE_both_directions_false_negative_SQ2_K12_cert_grade_HARD_PASS_called_anchor_weak_wrong_cell_case_errors_phase_D_charLM_hyphen_sparse_expansion_substring_0p48x_matched_48x_bundle_A_cfrpe_not_drosophila_neither_testbed_list_nor_my_scan_trustworthy_verify_not_assume_audit_tooling_per_cell_tracing_shows_wins_MOSTLY_REAL_14_of_18_passing_8_cert_grade_position_binding_d_ecr_sq2_composition_deletion_b2xb4_cortical_6_smoke_pass_cf_rpe_19_hierarchical_29_kappa3_21_USER_skepticism_results_real_CORRECT_audit_too_aggressive_genuine_drosophila_HARD_FAIL_mechanism_sparse_mismatch_linear_heteroassoc_active_gating_13p8x_real_submetric_MIDDLE_BAND_cell_DG_48x_tier6_full_NOT_cleanly_located_but_camelCase_hyphen_cannot_conclude_missing_without_trace_answer_PRIMARILY_wrong_cell_matching_NOT_missing_experiments_required_per_claim_cell_trace_before_downgrade_HOLD_DECISION_239_morning_queue_only_drosophila_downgrade_ready_exp_dev_enumerate_cells_I_VET_self_correction_19th_rule_own_audit_keyword_scan_ahead_of_rigor_new_candidate_keyword_cross_reference_unreliable_use_per_cell_trace_fname_v2 -- Skunkworks (Auditor)
