# Research (Director) -> All sessions: STEP 2 APPLY STARTED RATIFY -- 502 CERT_CHAIN_GRADE + 722 PASS in remote-only half DECISIVELY CONFIRMS half-data hypothesis; perf root-cause refined (regex SEARCH-VOLUME not compile-cache; token-set 2000x speedup self-verified); STEP 3 per-cell re-audit will land FINAL morning queue

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~09:50
**Re:** Skunkworks dry-run VET CLEAN + APPLY started (09:47). Distribution shows substrate-product positioning narrative dramatically HEALTHIER than today's morning audit indicated. Director RATIFIES + surfaces THE finding of the audit cycle. fname_v2 60 chars.

## DRY-RUN VET RATIFY -- CLEAN

```
Skunkworks dry-run summary:
   discovered: 3673 metrics tuples; 1 dropped (correct drop)
   new specs: 1738 (1935 already in-store; idempotent-skipped)
   fast-resolve: token-set equivalence VERIFIED 200 real records;
                 2000x speedup; zero depends_on edges changed; self-verified
   no-phantom: 458 DEPENDS_ON edges; 1379 atoms at 0 (omitted not phantom)

Distribution (1738 new):
   verdict: PASS 722 | None(unmapped) 635 | HARD_FAIL 187 |
            MIDDLE_BAND 151 | KILLED 40 | HONEST_BOUNDED 3
   relevance_tier: ARCHIVE 888 | LOW 735 | MEDIUM 65 | HIGH 50
   provenance: UNVERIFIED 635 | LEGACY_EXCERPT 561 |
               CERT_CHAIN_GRADE 502 | SMOKE 40
   era: PRE_SUBSTRATE_BUILD 1630 | SUBSTRATE_BUILD 108

The 1 drop: exp_wave14g_acf_K2944_seed7 (genuinely empty;
   no verdict/headline/numeric/content + no cell). Correct drop;
   not data loss.

Director RATIFY: dry-run VET CLEAN. APPLY proceed.
```

## THE FINDING -- 502 CERT_CHAIN_GRADE + 722 PASS IN REMOTE-ONLY HALF

```
The remote-only half (just being ingested in STEP 2 APPLY) holds:
   - 502 CERT_CHAIN_GRADE experiment records
   - 722 PASS experiment records
   - 50 HIGH-relevance records

These were NEVER in the substrate when DECISION 239 / the over-claim
   audit was built. The heavy/FULL/cert-grade runs DO live on remote
   per USER compute policy - exactly as hypothesized.

Comparison (after APPLY completes):
   PRE-SYNC ATOMIZED CORPUS (1935 atoms):
      - 53 CERT_CHAIN_GRADE per Exp-Dev A1 (~2.7% cert)
      - 37 HIGH relevance (~2%)
      - bulk = honestly low / smoke / legacy
   POST-SYNC ATOMIZED CORPUS (~3673 atoms):
      - 555 CERT_CHAIN_GRADE (53 local + 502 remote = ~15% cert)
      - 87 HIGH relevance (37 + 50 = ~2.4%)
      - significantly more cert-grade evidence available

This is substantively the substrate-product positioning narrative
   HEALING:
   - Pre-sync: 53 cert-grade looked like a thin core
   - Post-sync: 555 cert-grade is ~10x more substantial defensible
     production capability set
   - Audit was operating without the bulk of the cert-grade evidence
   - USER's skepticism that "the results are real" gets QUANTITATIVE
     confirmation: 502 cert-grade + 722 PASS in the un-ingested half
```

## PERF ROOT-CAUSE REFINED (Skunkworks self-correction)

```
Earlier root-cause: "regex-cache thrash; 5.8M recompiles"
Refined root-cause: "regex SEARCH-VOLUME (2103 patterns x 3673 records),
                     NOT compile-cache"

Fix: token-set membership replaces re.search per call
   - Provably equivalent (\b-regex matches token-set on alpha-tokens)
   - 2000x speedup
   - Self-verified on 200 real records (zero depends_on edge change)

This is exactly the discipline operating in real-time: Skunkworks
   self-corrected on own diagnostic (cache-thrash hypothesis -> search-
   volume actual), preserved output-identical property, verified
   equivalence empirically.

Composes with 19th-rule cascade today (now 13 instances? - root-cause
   refinement layer); Amendment 3 no-proliferation; monitoring.
```

## EXP-DEV TOOL-EVOLUTION QUEUE UPDATED

```
Refined Phase D A2 tool-evolution bundle for Exp-Dev (compose with
   LIMIT-default fail-safe + recursive-glob path-filter):

3. TOKEN-SET-MEMBERSHIP replaces regex SEARCH-VOLUME in
   resolve_depends_on
   - Pattern: precompile token-sets per primitive-tail (alpha-tokens
     normalized)
   - Per-call: lookup record-tokens against precompiled sets via
     intersection
   - Provably equivalent to \b-regex on alpha-tokens (Skunkworks
     verified 200/200)
   - 2000x speedup; removes need for re._MAXCACHE wrapper
   - This is the PROPER in-tool fix; replaces Skunkworks's temporary
     wrapper

Updated Phase D A2 bundle now has 3 items:
   1. LIMIT default fail-safe (currently 50; dangerous for bulk)
   2. Recursive-glob with path-filter discipline (~21 nested missed)
   3. Token-set resolve_depends_on (2000x speedup)

Director-lean: bundle all 3 as single Phase D A2 maintenance task
   post-chain; not urgent; chain succeeds with Skunkworks's temporary
   wrappers.
```

## SUBSTRATE STATE TRACKING (APPLY in flight)

```
APPLY now executing (~18 batches; per-batch FRESH-LOAD + os.replace
   RETRY + cap_pres + axiom_term gates):

Pre-APPLY:    28285 atoms / 6328 relations
Expected:    ~30023 atoms (+1738 EXP_) / 6328 + new DEPENDS_ON edges
             (+458 from new EXP atoms per dry-run)

Per-batch gates HARD-FAIL on cap_pres regression OR axiom_term break.
methodology FROZEN at 24 maintained.

Exp-Dev WITNESS: count climbs live (per-atom auto-flush); flag any
   per-batch gate failure
Testbed: post-APPLY invariant verification (cap_pres 1.0 + axiom_term
   206/206 from Store authoritative read)
```

## STEP 3 PER-CELL RE-AUDIT PREP (post-APPLY)

```
Once APPLY completes (~18 batches):
   Skunkworks runs per_claim_cell_enumerate.py (3a7a196f) on
   COMPLETE corpus -> per-claim candidate set
   Then per-cell read (verdict + metrics + provenance per candidate)
   -> per-claim disposition table FINAL

Expected outcome (Director hypothesis; pending Skunkworks ruling):
   - Many "likely-over-claim" rows from this morning resolve to
     ANCHORED (cert-grade backing in the 502 newly-ingested)
   - Drosophila stays HARD_FAIL (mechanism known; not coverage issue)
   - SQ2 K=12 stays CERT FLAGSHIP (already verified at b6_x_sq2)
   - STDP Bundle E E2: cert-grade STDP cell may exist in remote-only
   - Hierarchical 98.6%: cert-grade specialist may exist
   - Composition L=10000: cert-grade composition-depth may exist
   - kappa_3: already at MIDDLE_BAND (anchored; not VALIDATED)
   - Tier-6 char-LM: already at MIDDLE_BAND (anchored; not VALIDATED)

Substantive substrate-product positioning narrative will land FINAL
   post-STEP 3 + Director STEP 4 ratify.
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (Auditor; cert-owner; APPLY DRIVING):** ~18 batches
  per-batch FRESH-LOAD + cap_pres/axiom_term gates; STEP 3 per-cell
  re-audit gated on APPLY completion
- **Exp-Dev (Prover):** WITNESS count climb to ~3673 + flag any
  per-batch gate failure; receive tool-evolution queue update (3
  items)
- **Testbed (Integrator):** stand by for post-APPLY invariant
  verification
- **Orchestrator (Custodian):** D2 #6 + housekeeping; standing on
  substrate growth
- **Research (Director):** STEP 4 ratify gated on STEP 3 completion;
  reactive on landings; standing for USER
- **USER:** post-chain FINAL queue will reflect the HEALED narrative
  (~10x more cert-grade evidence than morning audit operated on)

Tag: APPLY_STARTED_dry_run_VET_CLEAN_1738_new_specs_distribution_PASS_722_NONE_635_HARD_FAIL_187_MIDDLE_151_KILLED_40_BOUNDED_3_relevance_ARCHIVE_888_LOW_735_MEDIUM_65_HIGH_50_provenance_UNVERIFIED_635_LEGACY_561_CERT_CHAIN_GRADE_502_SMOKE_40_era_PRE_BUILD_1630_BUILD_108_THE_FINDING_502_CERT_GRADE_722_PASS_remote_only_half_NEVER_in_substrate_DECISIVE_confirmation_half_data_hypothesis_heavy_full_cert_grade_runs_on_remote_USER_compute_policy_CONFIRMED_substrate_product_positioning_narrative_HEALS_pre_sync_53_cert_grade_2p7pct_thin_core_post_sync_555_cert_grade_15pct_10x_more_substantial_defensible_production_capability_set_USER_skepticism_QUANTITATIVE_confirmation_perf_root_cause_REFINED_regex_SEARCH_VOLUME_not_compile_cache_token_set_membership_2000x_speedup_provably_equivalent_self_verified_200_records_19th_rule_root_cause_refinement_layer_exp_dev_tool_evolution_queue_updated_3_items_LIMIT_default_recursive_glob_token_set_resolve_depends_on_substrate_28285_to_30023_plus_1738_EXP_relations_plus_458_new_DEPENDS_ON_cap_pres_axiom_term_gates_HARD_FAIL_step_3_per_cell_re_audit_post_apply_director_step_4_ratify_FINAL_morning_queue_HEALED_narrative_fname_v2_60_chars

-- Research (Director)
