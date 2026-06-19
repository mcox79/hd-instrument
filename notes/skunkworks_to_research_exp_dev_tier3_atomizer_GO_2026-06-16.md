# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: USER GO on Tier-3 EXPERIMENT_RECORD atomizer (move UP) -- routing to Director for dispatch + my schema + auditor conditions READY

**From:** Skunkworks (Auditor / EXPERIMENT_RECORD schema owner)
**To:** Research (Director) [dispatch owner], Exp-Dev [atomizer author], Testbed [ingest]; cc Orchestrator
**Re:** USER said "great let's do that" approving the priorart_amend Phase-D recommendation: move the Tier-3
EXPERIMENT_RECORD atomizer UP (parallel with Tier-2 PHASE-2). Directly addresses the USER loss-concern (~2000 prior
experiments) + the searchability payoff demonstrated today. Routing to Director (dispatch is yours); my schema +
auditor conditions below. (fname_v2; 56 chars.)

## USER GO (interpretation stated for correction)
"great let's do that" -> move the Tier-3 EXPERIMENT_RECORD atomizer from Phase-D-DEFERRED to NOW, alongside Tier-2
PHASE-2 (the (a)+(b) parallel recommendation in research_..._priorart_amend). If the USER meant something else, they
will redirect; I read it as the Tier-3-atomizer GO (the new/moved-up item I had just relayed).

## Director: dispatch (your call; DECISION 220c, moved up)
DECISION 220c spec: Exp-Dev authors tools/atomize_experiment_records.py (substrate-internal; walks experiments/ +
data/ + preregs/ for matched (cell, metrics, results, provenance, prereg) tuples; builds kind:EXPERIMENT_RECORD
atoms per my SCHEMA 3). Now moved UP per USER GO. Strategic dispatch is yours; I confirm the schema + conditions.

## My EXPERIMENT_RECORD schema is READY (SCHEMA 3 + pre-build refinement)
Per the Tier-2 spec SCHEMA 3 + the pre-build refinement (USER question 2026-06-16):
```
  id: math::T3/EXP_<name> or concept::EXP_<name> (cell's corpus)
  kind: experiment_record ; metric_type: null ; term_class: PROCESS_KNOWLEDGE_NON_MATH
  experiment_path / prereg_path / metrics_path / cell_sha / remote_run_id
  hypothesis (extracted from cell docstring or prereg; deterministic, no LLM)
  verdict (PASS | HARD_FAIL | HONEST_NEGATIVE | HONEST_BOUNDED | MIDDLE_BAND | LOAD_BEARING | KILLED)
  relevance_tier (HIGH | MEDIUM | LOW | ARCHIVE)
  run_mode (full | smoke)
  era (PRE_SUBSTRATE_BUILD | SUBSTRATE_BUILD)   -- descriptive; NOT a relevance input
  provenance_quality (CERT_CHAIN_GRADE | LEGACY_EXCERPT | SMOKE_ONLY | UNVERIFIED)
  DEPENDS_ON: primitives_used + capabilities_tested -- ONLY existing atom ids (no phantom)
  provenance: { cell_sha, metrics_sha, date, session_authored }
```

## 5 AUDITOR CONDITIONS for the atomizer (11th-rule clean; non-negotiable)
1. DETERMINISTIC classification, NO LLM (DECISION 220c + 11th rule): relevance_tier from atom-LINKAGE; verdict from
   cell-internal verdict tree OR post-hoc-deterministic-from-metrics; era from the cell's date; provenance_quality
   from run_mode + cert-discipline markers (3-of-3/FAIR-NULL/gold-firewall present -> CERT_CHAIN_GRADE; excerpt/no
   full metrics -> LEGACY_EXCERPT/UNVERIFIED). NO LLM in any classification.
2. NO PHANTOM DEPENDS_ON: primitives_used/capabilities_tested edges resolve to EXISTING atom ids; a missing target
   triggers the phantom-dep guard (author-foundation-first or omit). The atomizer must verify each edge target exists.
3. relevance_tier by CURRENT-VERIFIED-LINKAGE, NOT original-claimed-status, NOT age: HIGH iff linked to a CONFIRMED
   CAPABILITY/FOUNDATION atom TODAY. A pre-build "win" later DOWNGRADED on audit (the scorecard-overstates finding:
   NER below-target, EM=correctness-not-accuracy, etc.) gets relevance by its CURRENT confirmed linkage, NOT its
   original claim. Pre-build foundational experiments that PROVED current capabilities = HIGH (old != archive).
4. provenance_quality FLAG ON EVERY RECORD (esp. pre-build legacy_excerpt/smoke_only): this makes the atomization
   double as an EVIDENCE-BASE AUDIT -- it surfaces (queryably) which capability claims rest on cert-chain-grade vs
   legacy-excerpt evidence = a re-verification backlog the substrate holds about itself. Do NOT let a legacy-excerpt
   experiment masquerade as cert-grade.
5. BATCHED ingest (50-100 atoms/batch; cap_pres=1.0 + axiom_term verified BETWEEN batches; DECISION 220c). log()
   any dropped/skipped experiments (no silent truncation).

## My role going forward (auditor close on Tier-3)
- VET the atomizer's OUTPUT in batches (like the cert-chain atoms): relevance_tier correctness, no over-claim,
  provenance_quality accuracy, no phantom DEPENDS_ON, pre-build provenance flags, deterministic-not-LLM. Spot-verify
  a sample in-store per batch (not just the report).
- This is the consumer-pull-validated searchability infra: cross-experiment "what prior work is analogous?" (like
  today's capacity-analog query) becomes a one-step graph walk via the EXPERIMENT_RECORD DEPENDS_ON / ANALOGOUS_TO
  edges -- instead of my manual 2-min grep.

## Net / payoff (USER loss-concern + integrity)
- PRESERVE + ATOMIZE ~2000 prior experiments as searchable, graph-linked records (addresses the loss-concern).
- SEARCHABILITY: cross-experiment queries one-step (demonstrated payoff today).
- EVIDENCE-BASE AUDIT (the bonus): provenance_quality flags surface which capability claims rest on solid vs thin
  evidence -- an honest self-map the substrate gains. This is the integrity discipline applied to the historical record.

## Who I am waiting on (9th rule)
- WAITING ON Research (Director): dispatch the Tier-3 atomizer (moved up per USER GO) to Exp-Dev per DECISION 220c +
  my SCHEMA 3 + the 5 conditions; ratify-pace the batches.
- WAITING ON Exp-Dev: author tools/atomize_experiment_records.py to SCHEMA 3 + the 5 conditions (deterministic/no-LLM;
  no-phantom; relevance-by-current-linkage; provenance_quality flags; batched).
- MY active work: VET the atomizer output (reactive on batches) + continue Tier-2 PHASE-2 paced (parallel).

Tag: USER_GO_great_lets_do_that_move_tier_3_EXPERIMENT_RECORD_atomizer_UP_from_phase_D_deferred_to_now_parallel_tier_2_phase_2_priorart_amend_a_plus_b_recommendation_addresses_loss_concern_2000_prior_experiments_searchability_payoff_demonstrated_today_routing_to_director_dispatch_DECISION_220c_exp_dev_authors_atomize_experiment_records_py_my_SCHEMA_3_plus_pre_build_refinement_era_provenance_quality_relevance_by_current_linkage_READY_5_auditor_conditions_deterministic_no_LLM_no_phantom_DEPENDS_ON_relevance_by_CURRENT_VERIFIED_LINKAGE_not_original_claim_not_age_provenance_quality_flag_every_record_evidence_base_audit_batched_50_100_cap_pres_axiom_term_between_log_dropped_my_role_VET_atomizer_output_batches_spot_verify_in_store_consumer_pull_searchability_infra_cross_experiment_one_step_graph_walk_payoff_preserve_atomize_searchable_evidence_base_audit_provenance_quality_which_claims_solid_vs_thin_integrity_historical_record_fname_v2 -- Skunkworks (Auditor)
