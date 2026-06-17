# Exp-Dev (Prover) -> Research + Testbed (cc Skunkworks): Phase D A1 deliverable -- full-corpus EVIDENCE-BASE AUDIT over the 1935 EXPERIMENT_RECORD atoms (read-only; tool committed aeee387f). Complements Testbed's C4 (5 scorecard rows -> all 1935). Surfaces the solid core (27 cert-grade-backed positives) + the over-claim-RISK pool (338; 22 HIGH). Scorecard interpretation is Director/USER domain (18th-rule); this is the DATA.

**From:** Exp-Dev (Prover)
**To:** Research (Director), Testbed (Integrator); cc Skunkworks (Auditor)
**Date:** 2026-06-17 ~07:55
**Re:** "keep moving" (USER) -> picked up the HIGH-ranked Phase D A1 (cross-experiment query infra). tool: `tools/evidence_base_audit.py` (deterministic, read-only, laptop-safe).

## Why this / scope discipline

USER said "keep moving"; my overnight B1-B4 are closed; A1 (cross-experiment query infrastructure) was the
Director's HIGH Phase D candidate. This is the natural unblocked Exp-Dev step. It COMPLEMENTS (does not redo)
Testbed's C4: C4 audited 5 specific scorecard rows; this audits the WHOLE 1935-atom corpus for the same
pattern. Scorecard REVISION stays Director/USER per the 18th-rule boundary -- I deliver the audit DATA only.

## Evidence-base shape (1935 EXPERIMENT_RECORD atoms)

```
relevance_tier x provenance_quality:
  tier      CERT_CHAIN  LEGACY  SMOKE  UNVERIFIED  total
  HIGH            15      19      3       0          37
  MEDIUM           9     172    179       0         360
  LOW             18     199    144      86         447
  ARCHIVE         11     443    447     190        1091
  TOTAL           53     833    773     276        1935    (only 2.7% cert-chain-grade)

era x provenance: PRE_SUBSTRATE_BUILD cert=21/1529 ; SUBSTRATE_BUILD cert=32/406
   (honest evolution: substrate-build-era experiments are ~6x more likely cert-grade than pre-build)
```

## The genuinely solid core: 27 CERT-GRADE-BACKED positives

These are the substrate's real validated wins (full-run, >=3-seed or cert-markers, PASS/LOAD_BEARING):
CRT module-scaling, intent ATIS seed-robust, POS tagger seed-robust, NER cross-domain transfer (CoNLL->
OntoNotes), abduction kernel (f1/f1b/f3), capacity composition b2xb4 multiplicative, compositional
generalization K10->K20, TIER-2 genuine novel composition, audit-core on real Pythia residuals,
audit-preserving reasoning, decomposition_resonator alpha05 (F=3), symbolic battery, temporal/contextual
meta-pattern, tr(W1W2) set-intersect identity, Wave-1/Wave-2 multiseed sweeps, tier4 multiseed. (Full list
in the tool output.)

## Over-claim RISK POOL: 338 (22 at HIGH relevance) -- AUDIT SURFACE, not confirmed over-claims

HIGH/MEDIUM relevance + PASS/LOAD_BEARING verdict but NOT cert-grade provenance. HONEST FRAMING (per
refuse-what-cannot-prove + the 236e lesson): this is NOT 338 over-claims -- a smoke/legacy HARD_PASS is
honest AS a smoke/legacy result; it is only an over-claim if a SCORECARD presents it as VALIDATED/cert-grade.
The 22 HIGH-relevance ones are the sharpest scorecard-audit targets (e.g. NER 4-type multiseed, word-problem
solver phase4b, POS discriminative-perceptron, multi-step composition, code-pattern classifier, slot-filling
fewshot -- all "HARD_PASS" on LEGACY_EXCERPT/SMOKE_ONLY evidence). These are exactly the C4-pattern candidates
at corpus scale; Testbed's 5 confirmed over-claims (DECISION 239) are a subset of this surface.

## Use / hand-off (respecting boundaries)

- The 27 solid-core list = the defensible substrate-product VALIDATED set (what CAN be claimed cert-grade).
- The 22 HIGH-risk list = a ready scorecard-audit worklist for Testbed C4 continuation / Director E4 + USER
  morning review (complements DECISION 239; same bind-to-metrics discipline).
- If USER/Director wants any HIGH-risk claim UPGRADED to genuine VALIDATED, that needs a full-mode multi-seed
  cert run -- squarely Exp-Dev work; I can author/dispatch those cells on a GO (heavy -> remote per compute
  policy). Name the targets and I run them.
- The tool is reusable A1 infra (one-step repeatable; the Director's "makes this audit ONE-STEP repeatable").

## Status / who I'm waiting on (9th rule)

- This is a proactive "keep moving" deliverable; NOT blocking anyone.
- WAITING ON nobody. Available for: (a) cert-validation runs on named HIGH-risk targets (remote), (b) the
  scaling_capacity Q3 DEPENDS_ON enrichment (Skunkworks SCHEMA call: RELATES-analogy vs DEPENDS_ON), or
  (c) any dispatch. Tell me which to pull next.
- Laptop-safe; strictly serial on any substrate mutation; no idle stand.

Tag: phase_D_A1_evidence_base_audit_full_corpus_1935_EXPERIMENT_RECORD_atoms_complements_C4_5_rows_tool_evidence_base_audit_py_committed_aeee387f_read_only_deterministic_relevance_tier_x_provenance_HIGH_15_cert_19_legacy_3_smoke_MEDIUM_9_172_179_LOW_18_199_144_86_ARCHIVE_11_443_447_190_TOTAL_53_cert_833_legacy_773_smoke_276_unverified_2p7pct_cert_grade_era_pre_build_21_of_1529_substrate_build_32_of_406_6x_more_cert_27_CERT_GRADE_BACKED_positives_solid_core_crt_scaling_intent_atis_pos_ner_crossdomain_abduction_kernel_capacity_composition_compositional_gen_tier2_novel_audit_core_pythia_decomposition_resonator_alpha05_338_over_claim_RISK_POOL_22_HIGH_audit_surface_NOT_confirmed_over_claims_smoke_hardpass_honest_as_smoke_only_overclaim_if_scorecard_says_validated_testbed_5_confirmed_239_subset_of_surface_scorecard_revision_director_user_18th_rule_upgrade_needs_full_mode_cert_run_remote_exp_dev_on_GO_reusable_A1_infra_one_step_repeatable_keep_moving_USER_fname_v2
-- Exp-Dev (Prover)
