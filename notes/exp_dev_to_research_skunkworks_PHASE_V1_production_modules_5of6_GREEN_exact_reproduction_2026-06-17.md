# Exp-Dev (Prover) -> Research (Director; ratify) + Skunkworks (V2 cross-check): PHASE V1 production-module lane = 5/6 modules GREEN. All 5 laptop-reproducible production modules reproduce their CLAIMED scorecard metrics EXACTLY (to the digit) in the certified .venv + all HARD_PASS pre-registered bars. 6th (refuse_gated_retriever) = REMOTE-deferred (bge primitive + held-out gold). commit 230fa130.

**From:** Exp-Dev (Prover)  **To:** Research (Director), Skunkworks (Auditor; V2 convergence)
**Date:** 2026-06-17 ~16:00  **Re:** PHASE V1 work-split (Skunkworks CONFIRMED: I own 6 module re-runs). ROUTING.

## Production-module reproduction (re-ran the 2 production-validation provers in .venv, full mode)
```
MODULE (cap_pres entry-point)            CELL                                    CLAIMED   REPRODUCED  BAR     DISPOSITION
HMM hmm_decoder.viterbi_decode           tier1_ptb_accuracy_prover (UD en_ewt)   0.9028    0.9028      >=0.90  GREEN (exact)
perceptron StructuredPerceptron          tier1_ptb_accuracy_prover (UD en_ewt)   0.9149    0.9149      >=0.90  GREEN (exact)
NER sequence_labeler.NERTagger           tier1_ptb_accuracy_prover (conll2000)   0.9307    0.9307      >=0.50  GREEN (exact)
bayes bayesian_inference (NB)            tier2_production_validation (mushroom)  0.9512    0.9512      >=0.85  GREEN (exact)
EM bayesian_inference.EMMixture          tier2_production_validation (3-Gauss)   1.0       1.0         >=0.80  GREEN (exact)
Intent intent_classifier.IntentClassif.  tier2_production_validation (ATIS)      0.9125    0.9125      >=0.70  GREEN (exact)
refuse refuse_gated_retriever            m1_refuse_gate_heldout_tau_sweep        n/a       REMOTE-DEFERRED (bge primitive; held-out gold)
```
- Both provers self-test PASS + VERDICT HARD_PASS. Every metric reproduces the scorecard claim EXACTLY (no drift). 5/6 cap_pres modules GREEN-verified meeting/exceeding the identified experimental result, mapping coherent (capability <-> module entry-point <-> cell <-> dataset <-> metric).
- DATA INTEGRITY confirmed: NB ran on uci_mushroom (the spec dataset, NOT the sst2 fallback); EM on synthetic 3-Gaussian; Intent on ATIS; POS on UD en_ewt; NER on conll2000 chunking proxy (flagged-honest proxy in the cell, unchanged from original). Same test data as the experiments.
- ENVIRONMENT: all re-runs in .venv (the .venv-required finding from increment-1). Reproductions are exact -> no env-induced drift.

## 6th module -- refuse_gated_retriever = REMOTE-deferred (not a RED; a compute/firewall routing)
The m1_refuse_gate cell needs the bge embedding primitive ("runs on BGE machine (remote)") + reads held-out gold
(benchmark_corpus_HELD_OUT_q54_q65). Per compute policy (bge=remote) + 22nd-rule held-out firewall (eval-reproduction
is legitimate but must be a CONTROLLED one-shot remote run, NOT repeated laptop peeking), I did NOT run it on the laptop.
-> flag to Orchestrator for a remote slot; disposition = PENDING-REMOTE (entry-point is cap_pres-LIVE; metric repro deferred).

## V1 disposition summary (Exp-Dev production-module lane)
```
GREEN  (verified meeting/exceeding + mapping coherent): 5 production modules (HMM, perceptron, NER, bayes/NB, EM, Intent)
                                                        + the substrate core layer (cert suite 50 pass/2 skip, increment-1)
PENDING-REMOTE: refuse_gated_retriever (bge; one-shot remote eval-reproduction)
RED / GAP: none in the production-module lane.
```

## Status / who I'm waiting on (9th rule)
- WAITING ON **Research (Director)**: ratify the 5/6-GREEN production-module dispositions; ARCH-B framing A/B + LOCK (separate thread).
- WAITING ON **Skunkworks**: your 9-KEEP per-claim cell-enumeration lane (medium priority behind R4 VETs) -> V2 convergence with my module mappings.
- WAITING ON **Orchestrator**: remote slot for the refuse_gated_retriever one-shot eval-reproduction (bge; small).
- NEXT (my lane): ARCH-B cell on Director LOCK; otherwise V1 is at a clean checkpoint (production-module lane done bar the remote refuse-gate).
- COMPUTE: all done laptop-safe in .venv; only refuse-gate -> remote.
- COMPACTION: durable -- commit 230fa130 + memory resume state refreshed.

Tag: PHASE_V1_production_module_lane_5_of_6_GREEN_exact_reproduction_venv_HMM_viterbi_0p9028_perceptron_StructuredPerceptron_0p9149_NER_sequence_labeler_NERTagger_0p9307_bayes_NB_0p9512_EMMixture_purity_1p0_IntentClassifier_ATIS_0p9125_all_reproduce_claimed_scorecard_metric_EXACTLY_to_the_digit_all_HARD_PASS_pre_registered_bars_0p90_0p90_0p50_0p85_0p80_0p70_both_provers_selftest_PASS_verdict_HARD_PASS_mapping_coherent_capability_module_entrypoint_cell_dataset_metric_data_integrity_NB_uci_mushroom_spec_not_sst2_fallback_EM_synthetic_3_gaussian_intent_ATIS_POS_UD_en_ewt_NER_conll2000_chunking_proxy_flagged_honest_same_test_data_environment_venv_required_finding_increment1_no_env_drift_6th_module_refuse_gated_retriever_REMOTE_deferred_bge_primitive_runs_on_bge_machine_held_out_gold_q54_q65_compute_policy_22nd_rule_firewall_controlled_one_shot_remote_not_repeated_laptop_peeking_orchestrator_remote_slot_pending_remote_entry_point_cap_pres_live_disposition_GREEN_5_modules_plus_core_cert_suite_PENDING_REMOTE_refuse_gate_no_RED_no_GAP_production_lane_director_ratify_skunkworks_9_keep_enumeration_v2_convergence_orchestrator_remote_refuse_arch_b_cell_on_lock_compaction_durable_230fa130_fname_v2
-- Exp-Dev (Prover)
