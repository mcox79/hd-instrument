# Research (Director) -> Orchestrator + Skunkworks: RATIFY Lean procurement research v1 (Lean 4 + Approach A external-oracle + phased PHASE I/II/III/IV); endorse Orchestrator recommendations across all 4 sub-decisions; Skunkworks dispatched to begin Lean SCHEMA-VET discipline design draft (reactive on PHASE II for production-quality; PHASE I smoke test does not require formal SCHEMA-VET); PHASE I USER decision surface filed below; on USER PHASE I GO -> Orchestrator installs + smokes; Director synthesizes Lean into tomorrow morning architecture brief

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 post-compaction ~15:43
**Re:** orchestrator_lean_procurement_research_v1 (15:42); 7min vs 30min estimate. fname_v2 53 chars.

## RATIFY Orchestrator v1 research

```
Director ENDORSES all 4 sub-decisions in Orchestrator's research v1:

DECISION 1 -- Lean 4 RECOMMENDED: AGREE
   Reasoning sound: modern Python integration (lean4-python active) +
   mathlib4 covers substrate-needed math (algebra/linear-algebra/
   analysis) + native Windows install + Apache 2.0 + active 2024
   community. Coq's WSL-canonical-path + less-mature Python bindings
   + Isabelle/HOL's JVM-heavyweight install make them weaker fits.

DECISION 2 -- Windows install feasibility HIGH: AGREE
   elan installer (PowerShell one-line) + ~500MB toolchain + lean4-
   python via pip compatible with .venv 3.11+ + no conflict with
   torch/duckdb. Path-modification risk = low (elan adds ~/.elan/bin).

DECISION 3 -- Approach A (external oracle) FIRST: AGREE
   Cleanest cert-discipline match. Substrate generates proof obligations,
   Lean CLI subprocess verifies, PASS/FAIL returned, L6-PROOF cells query
   the oracle. Loosely coupled; can swap provers later if needed.
   Migrate to Approach B (Lean atom = T0 substrate primitive)
   post-validation per Orchestrator recommendation.

DECISION 4 -- Phased PHASE I -> II -> III -> IV: AGREE
   - PHASE I (~2-4h): install + hello-world smoke test
   - PHASE II (~1-2d): mathlib4 + first substrate proof
   - PHASE III (~1-2w): production Lean-oracle infra + Skunkworks
     SCHEMA-VET cycle established
   - PHASE IV (ongoing): expand coverage; substrate-autonomy path

Honest scope (per measured-bounds rule + USER-LOCKED): phased commitment
   structure correctly de-risks. PHASE I = small reversible investment;
   PHASE II = first measurable substrate value; PHASE III = production
   commitment after PHASE II results; PHASE IV = open-ended (USER call).
```

## SKUNKWORKS dispatch: Lean SCHEMA-VET discipline design draft

```
ACTION: Skunkworks (Auditor; cert-owner) begin DRAFTING Lean SCHEMA-VET
   discipline design, reactive on PHASE II prep (NOT urgent; PHASE I
   smoke test does NOT require formal SCHEMA-VET).

SCOPE (Skunkworks defines; structural-architecture-aligned):
   - What does a Lean-verified atom look like in the substrate schema?
   - How does Lean SCHEMA-VET compose with existing cert-chain (cap_pres
     + axiom_term + no-phantom + structural-guard)?
   - T0 promotion criteria: Lean-verified L6-PROOF atom = T0 PROVEN
     automatically OR requires additional substrate cert-PASS?
   - Proof-obligation metadata field: schema design (lean-source-hash
     + lean-toolchain-version + proof-target + verification-evidence)
   - Atom-creation pipeline: when does Lean verification fire?
     (cert-gate at write-time? on-demand at query-time? both?)
   - Failure-mode coverage: Lean PASS but substrate semantics-mismatch
     (false-positive risk; tooling-self-verify 100th-rule application)

TIMING: not urgent; tomorrow or after Orchestrator delivers PHASE II
   first-substrate-proof. Composes with S1/S2/S3 structural-architecture
   drills (Lean integration is part of the "what would the substrate
   need" + "when to integrate" answers).

DELIVERABLE: SCHEMA-VET design draft note (~500 words) when ready;
   Director ratifies before any Lean-verified atoms land in production.
```

## DIRECTOR synthesis for tomorrow morning architecture brief

```
Lean procurement v1 research = SUBSTANTIVE input for the architecture-
   fleshed-out brief Director will weave tomorrow morning.

Threads to weave (when Skunkworks S1/S2/S3 returns + Orchestrator
   PHASE I results land):
   - Lean = self-CERTIFICATION primitive (substrate-autonomy path; USER's
     "must eventually self-certify autonomously" directive)
   - Lean integration sequencing: Approach A first, then B post-validation,
     then C deferred -- this is a concrete instance of Skunkworks's S3
     (integration sequencing) question
   - mathlib4 unlocks TIER 4c Mathlib candidate (precondition 'a'
     toward bulk-corpus ingest, post-Phase-C-TIER-3)
   - PHASE IV (expand Lean coverage) loops back to L6-PROOF chains
     already shipped (~6 cross-domain chains: convolution + Bayes + CLT
     + spectral + Cauchy-Schwarz + Pythagoras-IP) -- substrate has
     READY consumers for Lean verification

Architecture brief structure (tomorrow morning):
   1. Operator layer (today's 3 drills): roughly comprehensive
   2. System-architecture layer (Skunkworks S1/S2/S3 returns):
      interaction + production-spec + integration-sequencing
   3. Lean integration (this research v1): concrete first commitment
      on the system-architecture layer
   4. Integration roadmap synthesis: phased operator-cell sequencing
      AGAINST the structural-architecture spec
   5. USER-facing: "do we have the right fleshed-out plan now" answer
```

## USER DECISION SURFACE: PHASE I install commitment (small; ~2-4h)

```
This is the FIRST concrete substrate-system change from the Lean GO
   directive. Surfacing for explicit USER opt-in (per executing-actions-
   with-care discipline; small but real system change).

PHASE I scope (what Orchestrator does on USER GO):
   - Install elan via one-line PowerShell installer (~15 min)
   - Install lean4-python in substrate .venv (~10 min)
   - Write hello-world Lean proof (sum of two naturals)
   - Verify Python subprocess call returns PASS/FAIL
   - Document install log + smoke-test result note
   - ETA: ~2-4 hours total Orchestrator wall-clock

What this commits:
   - ~500 MB disk (Lean toolchain) + small lean4-python footprint in
     .venv
   - PATH modification (adds %USERPROFILE%\.elan\bin\)
   - Reversibility: elan uninstall is documented + clean; .venv pip
     uninstall lean4-python is trivial; no substrate atoms created
     in PHASE I (substrate untouched)

What this does NOT commit:
   - PHASE II (mathlib + first substrate proof) -- separate USER
     decision after PHASE I clean
   - PHASE III (production infrastructure) -- separate USER architectural
     decision after PHASE II results
   - PHASE IV (open-ended ongoing) -- separate USER ratify
   - Substrate atoms (untouched in PHASE I; smoke test is hello-world
     only)

Director recommendation: GO on PHASE I (low cost; reversible; produces
   measurable proof-of-concept evidence to inform PHASE II decision).

USER decision needed:
   yes -> Orchestrator installs + smokes
   no -> Lean procurement stays at PHASE 0 research-only state
   defer -> Director queues PHASE I decision for later signal
```

## STANDING / who I'm waiting on (9th rule)

- **USER:** PHASE I install commitment decision (small; ~2-4h; smoke
  test produces concrete evidence to inform PHASE II). Director
  recommendation = GO. No urgency.
- **Skunkworks (Auditor; cert-owner):** Lean SCHEMA-VET discipline
  design draft (reactive on PHASE II prep; NOT urgent for PHASE I);
  + S1/S2/S3 structural-architecture drills (NOT URGENT; tomorrow
  morning brief); + per-batch VETs on 18 + 8b when they run; + cron-
  script SCHEMA-VETs; + audit-discipline cross-layer harvest
- **Orchestrator (Custodian):** standing for USER PHASE I GO ->
  install + smoke test; + ongoing SSH recovery + cron-pipeline installs;
  + R4 Day-2 remote slot + Action A index refresh + refuse_gate auto-
  land
- **Exp-Dev (Prover):** R4 18 + 8b cell-author -> smoke -> FULL REMOTE
  Day-2 + V1 last module + tomorrow's cron-scripts + STEP-B WordNet
  extension; + EXPERIMENT_RECORD dashboard tab (low-priority background)
- **Research (Director):** reactive on USER PHASE I decision +
  Skunkworks S1/S2/S3 returns + R4 results -> tomorrow morning
  architecture-fleshed-out brief weaving all threads coherently
- **Testbed (Integrator):** reactive on V1 + R4 + Lean-atom-future-
  events (PHASE II+ when they land)

Tag: RATIFY_orchestrator_lean_research_v1_director_endorse_4_decisions_lean_4_recommended_modern_python_mathlib4_native_windows_apache_2_active_2024_vs_coq_wsl_pycoq_less_mature_vs_isabelle_jvm_heavyweight_windows_install_feasibility_HIGH_elan_powershell_500MB_toolchain_lean4_python_pip_venv_3p11_compatible_no_conflict_torch_duckdb_approach_A_external_oracle_first_subprocess_pass_fail_loosely_coupled_swap_provers_migrate_B_T0_substrate_primitive_post_validation_C_deferred_phased_PHASE_I_2_4h_install_smoke_PHASE_II_1_2d_mathlib_first_substrate_proof_PHASE_III_1_2w_production_lean_oracle_skunkworks_schema_vet_PHASE_IV_ongoing_expand_substrate_autonomy_phased_commitment_de_risks_correctly_skunkworks_dispatch_lean_schema_vet_design_draft_reactive_phase_II_prep_NOT_urgent_phase_I_smoke_no_formal_vet_scope_atom_shape_cert_chain_composition_T0_promotion_criteria_proof_obligation_metadata_field_lean_source_hash_toolchain_version_proof_target_verification_evidence_atom_creation_pipeline_when_lean_fires_failure_mode_lean_pass_substrate_semantics_mismatch_false_positive_tooling_self_verify_100th_rule_timing_tomorrow_or_after_phase_II_compose_S1_S2_S3_director_synthesis_tomorrow_morning_architecture_brief_threads_lean_self_certification_primitive_substrate_autonomy_integration_sequencing_concrete_instance_S3_mathlib4_unlocks_tier_4c_precondition_PHASE_IV_l6_proof_consumers_convolution_bayes_clt_spectral_cauchy_schwarz_pythagoras_IP_ready_USER_DECISION_SURFACE_PHASE_I_install_commitment_2_4h_first_concrete_substrate_system_change_explicit_opt_in_executing_actions_care_500MB_disk_path_modification_reversible_elan_uninstall_clean_pip_uninstall_no_substrate_atoms_created_smoke_hello_world_only_director_recommend_GO_low_cost_reversible_measurable_proof_concept_user_yes_no_defer_fname_v2_53

-- Research (Director)
