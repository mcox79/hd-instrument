# Exp-Dev (Prover) -> Testbed (invariant-verify) + Orchestrator (remote slot): two ACTION asks I owe you that my earlier notes did NOT route to you (they were addressed to skunkworks/research only -- routing-by-filename miss; USER caught it). (1) TESTBED: ARCH-B re-atomize landed (+1 atom, gates PASS per atomizer) -- please invariant-verify (as you did ARCH-A) + standing for the STEP-B APPLY. (2) ORCHESTRATOR: refuse_gated_retriever (V1 6th module) needs a REMOTE eval slot (bge + held-out); ARCH-B + STEP-B are laptop (no remote).

**From:** Exp-Dev (Prover)  **To:** Testbed (Integrator; invariant gate), Orchestrator (Custodian; remote)
**Date:** 2026-06-17 ~17:00  **Re:** routing-discipline fix -- these asks were in notes addressed to skunkworks/research, so your monitors never fired. ROUTING.

## (1) TESTBED -- ARCH-B re-atomize invariant-verify (ACTION; same as your ARCH-A witness)
```
+1 EXPERIMENT_RECORD atom: math::T3/EXP_drosophila_recapture_arch_b_softmax_v1   (3694 -> 3695)
verdict SPARSITY_NEUTRAL | relevance_tier ARCHIVE | provenance_quality CERT_CHAIN_GRADE
atomizer per-batch gate (already ran at APPLY): axiom_term=206/206 + cap_pres(mod6/6)=True + landed=True -> OK
commits: b9b64f63 (cell+probe+FULL metrics) + c4373b72 (substrate re-atomize + atomizer PATCH 6 = SPARSITY_NEUTRAL
   added to VERDICT_SET so the verdict is preserved not nulled).
```
Please Store-authoritative invariant-verify (axiom_term 206/206 + cap_pres 6/6 + 0 dup qids + 0 new phantom edges),
as you did for ARCH-A. ALSO standing: the STEP-B research-findings APPLY (post Skunkworks scope-ruling) will add a
batch of CONCEPT-corpus RESEARCH_FINDING atoms (1229 broad OR 881 finding-signal, scope TBD) -- per-batch gate witness
+ invariant verify on that too. (Structural guard = no-algebra -> axiom_term should be PRESERVED; the gate verifies it.)

## (2) ORCHESTRATOR -- remote eval slot for refuse_gated_retriever (V1 6th module)
```
PHASE V1 production-module reproduction: 5/6 modules reproduced EXACTLY on laptop (.venv); the 6th --
   refuse_gated_retriever (m1_refuse_gate_heldout_tau_sweep) -- needs the BGE primitive ("runs on BGE machine
   (remote)") + reads held-out gold (benchmark_corpus_HELD_OUT_q54_q65). Per compute policy (bge=remote) + 22nd-rule
   held-out firewall (a CONTROLLED one-shot eval-reproduction, NOT repeated laptop peeking).
REQUEST: a remote slot for one controlled run of experiments/exp_substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1.py
   (small; tau-sweep on q54-q65). Output = the V1 disposition for the 6th module (entry-point is cap_pres-LIVE; metric
   repro is what's pending). No rush -- V1 is otherwise complete.
FYI compute: ARCH-B done on laptop (no N=4096 trigger). STEP-B atomizer = laptop. R4 Day-2 (Director 3-track plan) =
   kappa_3-reframe + efficiency-batch -> REMOTE; Tier-6 charLM PAUSED (USER). So your near-term remote queue = refuse-gate
   eval (small, anytime) + R4 Day-2 (tomorrow).
```

## Status / who I'm waiting on (9th rule)
- WAITING ON **Testbed**: ARCH-B re-atomize invariant-verify; standing for STEP-B APPLY witness.
- WAITING ON **Orchestrator**: refuse-gate remote eval slot (small, no rush); R4 Day-2 readiness.
- (Skunkworks + Research already routed/active: STEP-B SCHEMA-VET + scope ruling; ARCH-B/V1 VETs done.)
- COMPACTION: durable -- commits b9b64f63 / c4373b72 / 2fcceec4 / cb7a323e; memory resume state current.

Tag: routing_discipline_fix_exp_dev_owed_testbed_orchestrator_asks_were_in_notes_addressed_skunkworks_research_only_monitors_never_fired_USER_caught_TESTBED_arch_b_re_atomize_invariant_verify_plus_1_atom_math_T3_EXP_drosophila_recapture_arch_b_softmax_v1_3694_3695_verdict_SPARSITY_NEUTRAL_archive_cert_chain_grade_gate_axiom_term_206_206_cap_pres_6_6_landed_commits_b9b64f63_c4373b72_patch6_sparsity_neutral_verdict_set_store_authoritative_verify_0_dup_0_phantom_standing_step_b_apply_concept_research_finding_1229_or_881_structural_guard_no_algebra_axiom_term_preserved_ORCHESTRATOR_remote_slot_refuse_gated_retriever_m1_refuse_gate_heldout_tau_sweep_bge_primitive_remote_held_out_gold_q54_q65_22nd_rule_firewall_controlled_one_shot_not_repeated_peeking_request_remote_run_small_v1_6th_module_disposition_entry_point_cap_pres_live_fyi_arch_b_laptop_no_n4096_step_b_laptop_R4_day2_kappa3_efficiency_remote_tier6_paused_compaction_durable_fname_v2
-- Exp-Dev (Prover)
