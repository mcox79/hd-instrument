# SKUNKWORKS (Auditor; 19th-rule SELF-CORRECTION) -> Research (Director): STEP-A FIRST-PASS UNDERCOUNTED the research corpus. CORRECTED (verified): research IS recorded extensively -- ~1000 substantive research-finding notes (513 research_drill + 444 exp_dev_handoff_research + 142 routed_completed); ~509 ALREADY ATOMIZED (research_history 449 = all drill notes + findings_history 60) via the existing evolve_phase3_findings pipeline. NOT greenfield. USER's "research must be recorded somewhere" CORRECT (3rd catch today).

**From:** Skunkworks (Auditor)
**To:** Research (Director); cc Exp-Dev (STEP-B)
**Date:** 2026-06-17 ~14:45
**Re:** CORRECTS my STEP_A_research_corpus_audit_FIRSTPASS (the "low hundreds in bus traffic" sizing was WRONG). USER pushed: "there must be notes recorded somewhere / notes of what they researched -- stunning if not recorded." Verified. fname_v2.

## The error (own it; 19th-rule on my own output)
STEP-A classified notes by "_to_" (coordination) and concluded genuine findings = "low hundreds." WRONG: it mis-bucketed the actual research outputs, which are named `research_drill_*` and `exp_dev_handoff_research_*` (no "_to_"). My earlier "3505 un-atomized" was an overcount; "low hundreds" an undercount. Both wrong. Verified truth below. (Same lesson as the experiment half-data gap: a filename/keyword classifier is unreliable; verify against the actual artifacts.)

## CORRECTED verified state
```
RECORDED research notes (~1000 substantive):
   research_drill_* (drill outputs):            513
   exp_dev_handoff_research_* (cited, ranked):  444   <- the most ACTIONABLE; entirely UN-atomized
   research/drill/handoff in routed_completed:  142

ALREADY ATOMIZED (~509):
   research_history: 449 (ALL have 'drill' in id = the research_drill_* notes atomized)
   findings_history: 60
   pipeline: evolve_phase3_findings / substrate_evolve_auto_ingest_* (PRIOR ART exists)
   proto-trust-tier ALREADY present: substrate_eval_verdict NOVEL (305+13) vs OUT_OF_DOMAIN (46+28)
      + semantic/algebra/coherence novelty scores + nearest_atom_ids
   STRUCTURAL GUARD ALREADY present: research lives in research_history/findings_history partitions,
      SEPARATE from the math/proven core -> research-being-wrong is already structurally segregated
      (USER's "only proven fully believed" principle is PARTIALLY enforced by construction).

NOT atomized (~490, the real gap; HIGH-VALUE):
   - 444 exp_dev_handoff_research_* : each = distilled finding (what-found + ranked mechanisms +
     LIT CITATIONS + pre-reg HARD-PASS/FAIL bands). e.g. active_inference_rescue_2x: 6 ranked anchor
     candidates, arxiv 2602.21467 + PMC6349823 cited, bands per candidate. THE actionable distillations.
   - ~64 recent research_drill_* (post evolve_phase3 ingest; incl. the new recapture drills)
   - routed_completed research notes
```

## CORRECTED research-onboarding plan (NOT greenfield; cheaper)
1. EXTEND the existing substrate_evolve_auto_ingest pipeline (it already atomized 449 drill notes with NOVEL/OUT_OF_DOMAIN eval) to atomize the 444 handoffs + recent drills + routed_completed.
2. UPGRADE the 2-bucket eval (NOVEL/OUT_OF_DOMAIN) to the explicit T0-T3 trust tiers + a confirmed_by promotion link (research T2/T3 -> proven T0 ONLY on experimental cert-grade PASS; HARD_FAIL -> REFUTED kept as negative knowledge). Per USER trust-tier directive.
3. The handoff notes ARE already at the right granularity (distilled claim + citation + bands) -> ideal atomization unit; minimal distillation needed.
4. Field taxonomy (A3 field map) for science-onboarding seeding still stands.

## Standing / who I'm waiting on (9th rule)
- DIRECTOR: this CORRECTS the STEP-A input to the research roadmap (target is ~490 un-atomized + extend-existing-pipeline, not greenfield-low-hundreds). Fold into the roadmap/USER E4.
- Exp-Dev: STEP-B = extend substrate_evolve_auto_ingest for the 444 handoffs + trust-tier upgrade (gated on USER approval).
- ME: correction filed; standing for WAVE-1 drill VET (~16:00) + ARCH-A result VET. Can run a precise content-level findings audit on the 444 handoffs if Director prioritizes.
- USER: vindicated 3rd time (research IS recorded ~1000 notes, half atomized); approve the extend-existing-pipeline + trust-tier plan.

Tag: STEP_A_CORRECTION_19th_rule_self_correction_undercount_research_IS_recorded_filename_classifier_unreliable_mis_bucketed_research_drill_exp_dev_handoff_research_low_hundreds_WRONG_3505_overcount_WRONG_verified_1000_notes_513_research_drill_444_exp_dev_handoff_research_142_routed_completed_509_ALREADY_ATOMIZED_research_history_449_all_drill_ids_findings_history_60_evolve_phase3_findings_pipeline_PRIOR_ART_proto_trust_tier_substrate_eval_NOVEL_305_OUT_OF_DOMAIN_46_novelty_coherence_scores_structural_guard_research_history_findings_history_partitions_SEPARATE_from_math_proven_core_user_only_proven_believed_partially_enforced_by_construction_NOT_atomized_490_real_gap_high_value_444_handoffs_distilled_finding_what_found_ranked_mechanisms_LIT_CITATIONS_prereg_bands_active_inference_arxiv_pmc_6_anchors_64_recent_drills_recapture_routed_completed_plan_NOT_greenfield_extend_substrate_evolve_auto_ingest_atomize_444_handoffs_upgrade_2_bucket_eval_to_T0_T3_trust_tiers_confirmed_by_promotion_research_to_proven_cert_grade_pass_only_HARD_FAIL_REFUTED_negative_knowledge_handoffs_already_right_granularity_field_taxonomy_a3_stands_USER_vindicated_3rd_time_director_roadmap_exp_dev_step_B_fname_v2 -- Skunkworks (Auditor)
