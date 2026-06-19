#!/usr/bin/env python3
"""Skunkworks 2026-06-19 -- atomize inst-242 + inst-243 (the rectification AUDIT_LESSONs).

DOGFOODS the SAFE template (add_audit_lesson_safely). Both lessons came out of the
USER-directed value-mining concern + the live PART_OF cert-integrity reconciliation.

SCHEMA-VET (Skunkworks): instances 242/243 free (max=241); all composes_with resolve
(inst-241, inst-80 verify-the-referent, inst-240 silent-loss) -- verified against the Store.

- inst-242: capability triage by cert-PROXIMITY not VALUE (high-value findings un-surfaced).
- inst-243: restore-to-prior-commit recovery reverts legitimate interventions + breaks
  dependent cert atoms (audit the git-window + reproduce-check; don't dismiss hygiene flags).

Run: --dry-run | --apply
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.atomize_audit_lesson_template_SAFE import add_audit_lesson_safely

VTR = "AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer"  # inst-80
PROT = ("AUDIT_concurrent_write_corruption_propagation_4_layer_protection_"
        "unique_tmp_sync_loadgate_explicit_staging_single_writer_window")  # inst-241


def inst242() -> Atom:
    return Atom(
        id=("AUDIT_capability_triage_by_cert_proximity_not_value_"
            "high_value_findings_unsurfaced_relevance_tier_unused"),
        name=("Capability triage by cert-PROXIMITY not VALUE: high-value findings "
              "(substrate-beats-LLM, coverage-guarantees, 6x-depth) left un-surfaced; "
              "relevance_tier signal unused"),
        description=(
            "Capability onboarding / Track-B pull-up was triaged by cert-PROXIMITY "
            "(cert-grade first, then closest-to-cert MEASURED_MECHANISM), NOT by "
            "capability-VALUE. Result: 447 MEDIUM+ relevance non-cert WINS (416 MEDIUM "
            "+ 31 HIGH, of 1148 total) were never surfaced -- including substrate "
            "BEATING small LLMs (NER span-F1 0.711 vs Qwen-0.5B 0.202 = +0.51; sentiment "
            ">=LLM at ~5000x speed), distribution-free conformal COVERAGE GUARANTEES + "
            "calibrated confidence (ECE<0.05), the resonator 6x reasoning-DEPTH extension "
            "(smoke), and the MiniLM/Pythia/Llama encoder-ingest (the glass-box-LLM "
            "foundation -- cert-grade but never synthesized as a strategic capability). "
            "The relevance_tier field (a value-signal the substrate already computes) was "
            "UNUSED in triage. Three compounding gaps: (1) relevance_tier ignored; "
            "(2) the 1148 treated as a bulk backfill-statistic (DRILL_C) not read "
            "individually for strategic value -- and the cert-owner's 'don't bulk-promote' "
            "ruling, while cert-correct, stopped short of 'value-mine them'; (3) no "
            "strategic-synthesis (even CERT-GRADE caps weren't grouped into capability-"
            "THEMES). FIX: rank pull-up/onboarding by capability-VALUE x cert-gap "
            "(relevance_tier + strategic-theme + head-to-head-significance), NOT cert-"
            "proximity; add a strategic-synthesis pass (group cert caps into themes). "
            "The substrate is usually MORE capable than the first-pass inventory implies "
            "(NEGATIVITY-BIAS-symmetric cuts UPWARD). Composes the USER-LOCKED 'scour the "
            "FULL breadth' directive + verify-the-referent at the capability-discovery level."
        ),
        kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            "provenance_quality": None, "instance_number": 242, "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "triage_by_cert_proximity_not_value_mine",
            "witnesses_count": 1,
            "first_witness": "value_scour_447_MEDIUM_plus_noncert_wins_2026-06-19",
            "composes_with": [VTR, PROT],
            "memory_references": [
                "feedback_director_intuitive_summary_must_scour_full_substrate_breadth_not_recent_session_arc_only_USER_2026-06-18"],
            "operational_rule": (
                "Triage capability pull-up/onboarding by VALUE x cert-gap: value = "
                "relevance_tier (HIGH/MEDIUM) + strategic-theme match + head-to-head-"
                "significance (beats-a-baseline). USE relevance_tier (it is already "
                "computed). Add a periodic strategic-synthesis pass grouping cert caps "
                "into capability-THEMES. Do NOT triage by cert-proximity alone."),
            "key_findings_surfaced": [
                "substrate_beats_Qwen0.5B_NER_+0.51_and_sentiment_5000x_faster",
                "distribution_free_conformal_coverage_guarantee_+_calibration_ECE<0.05",
                "resonator_6x_reasoning_depth_extension_smoke",
                "MiniLM_Pythia_Llama_encoder_ingest_glassbox_foundation_cert_grade"],
        },
    )


def inst243() -> Atom:
    return Atom(
        id=("AUDIT_restore_to_prior_commit_recovery_reverts_legitimate_interventions_"
            "audit_git_window_and_dependent_cert_atoms_dont_dismiss_hygiene_flags"),
        name=("Restore-to-prior-commit recovery reverts legitimate post-restore-point "
              "interventions + can break dependent cert atoms: audit the git-window + "
              "reproduce-check dependent cert atoms; don't dismiss graph-hygiene flags"),
        description=(
            "A corruption-recovery restore (`git checkout <clean-commit> -- <paths>`) "
            "reverts ALL changes on the restored paths after the restore-point -- "
            "including LEGITIMATE post-restore-point interventions, not just the "
            "corruption. The 2026-06-19 concept-partition restore (to 2e0b57c0) reverted "
            "EXACTLY 2 legitimate interventions (bounded because the restore was path-"
            "limited to concept/{atoms,relations}.jsonl): (1) ddabfdbc, the PART_OF "
            "2-level completion (+125 holonym edges) -- which BROKE a CERT_CHAIN_GRADE "
            "atom's claim (EXP_partof_broad_after HARD_PASS required PART_OF-2hop=0.82; "
            "the revert dropped it to 0.627 < its 0.7 bar -> the cert atom no longer "
            "reproduced on the substrate it was stored in); (2) f489d007, a phantom-edge "
            "cleanup -- the restore UNDID it, RE-INTRODUCING 3 dangling SUPERSEDES edges. "
            "The recovery verified cert-COUNT + loadability + TRUE-HARD-PASS but NOT "
            "substrate-STATE-completeness. CRITICAL TELL: the re-introduced phantom showed "
            "up as an H4 graph-hygiene SOFT-flag in the invariant-check and was UNDER-READ "
            "as 'pre-existing/harmless' by BOTH the custodian (Orchestrator) AND the "
            "cert-owner (Skunkworks) -- the flag was the canary, dismissed by two sessions. "
            "FIX: after a restore-to-prior-commit, (a) git-window-ARCHAEOLOGY (audit "
            "restore-target..corruption for legitimate interventions on the restored "
            "paths); (b) reproduce-check the dependent CERT atoms (do their claims still "
            "hold on the restored state?); (c) TRACE graph-hygiene SOFT-flags to a cause, "
            "do NOT dismiss them as benign. Remediation = re-apply the lost legitimate "
            "interventions (SEQUENCED single-writer windows + per-re-apply cert-consistency "
            "check, per the inst-241 single-writer-window discipline). Composes inst-241 "
            "(the recovery left exactly this state-completeness gap) + verify-the-referent "
            "at the substrate-STATE level."
        ),
        kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            "provenance_quality": None, "instance_number": 243, "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "restore_recovery_reverts_legit_work_needs_state_reconciliation",
            "witnesses_count": 3,
            "first_witness": "partof_completion_ddabfdbc_revert_broke_partof_broad_after_cert_2026-06-19",
            "composes_with": [PROT, VTR],
            "operational_rule": (
                "After a restore-to-prior-commit recovery: (a) audit the git-window "
                "(restore-target..corruption) for legitimate interventions on the restored "
                "paths; (b) reproduce-check dependent cert atoms; (c) trace graph-hygiene "
                "SOFT-flags to a cause (don't dismiss). Remediate by re-applying lost "
                "legitimate interventions in SEQUENCED single-writer windows + cert-"
                "consistency check each. Cert-count + loadability + TRUE-HARD-PASS is "
                "NECESSARY but NOT SUFFICIENT -- verify substrate-STATE-completeness."),
            "witnesses": [
                "ddabfdbc_PART_OF_completion_revert_broke_partof_broad_after_HARD_PASS",
                "f489d007_phantom_cleanup_revert_reintroduced_3_dangling_SUPERSEDES",
                "H4_graph_hygiene_softflag_underread_as_benign_by_orchestrator_AND_skunkworks"],
        },
    )


def main():
    atoms = [inst242(), inst243()]
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        for a in atoms:
            print(f"inst-{(a.metadata or {}).get('instance_number')}: {a.id[:70]} | tier={a.tier.value}")
        print("Use --dry-run or --apply.")
        return 0
    if "--dry-run" in sys.argv:
        for a in atoms:
            print(f"DRY: inst-{(a.metadata or {}).get('instance_number')} constructs OK; tier(value)={a.tier.value}; "
                  f"composes={(a.metadata or {}).get('composes_with')}")
        return 0
    ok_all = True
    for a in atoms:
        print("=" * 78)
        ok = add_audit_lesson_safely(
            a, source="skunkworks_rectification_2026-06-19",
            note=(f"inst-{(a.metadata or {}).get('instance_number')} rectification AUDIT_LESSON "
                  "(value-mining triage / restore-state-reconciliation); SCHEMA-VET PASS; "
                  "dogfoods the SAFE template."))
        ok_all = ok_all and ok
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
