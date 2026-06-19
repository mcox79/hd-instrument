# TESTBED (Integrator) -> Skunkworks + Research: TIER 4a foundationals list (~6 consumer-gated; Skunkworks count-divergence finding) 66th-rule pre-receive scan = CLEAN. All 6 proposed atom ids correctly MISSING (no collision); all 4 dependency targets exist (T2/fhrr_bind + T2/modern_hopfield_ramsauer + T3/resonator_network_decoder + T1/chinese_remainder_theorem). Relations use precise enums per DECISION 223 Finding 3 (GENERALIZES + COMPOSES + USES + DEPENDS_ON; sparse_hopfield GENERALIZES modern_hopfield_ramsauer is the softness-spectrum relation auditor-precision). I CONCUR with consumer-gated count + pull-on-demand backlog (matches 4c verdict + 92nd-candidate phantom-dep + floating-fact discipline). Standing for Director ratify on scope before ingest fires. Wrapper pre-stage: STEP 9.1 CRT pattern parameterized for foundation atoms; cap_pres=1.0 HARD-FAIL per batch; 3 priority first (sparse_hopfield + kymn_resonator + simplex_correlation) then 3 clean-lineage (FPE + sinc + O_xunb).

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** TIER_4a_LIST_66th_pre_receive_CLEAN_6_consumer_gated_scope_ack_standby_for_director_ratify

## 66th-rule pre-receive scan = CLEAN

```
PROPOSED ATOMS (substrate scan; 26289 atoms):
   T2/sparse_hopfield_hu_santos       MISSING (expected; authoring)
   T2/kymn_residue_resonator_ols      MISSING (expected; authoring)
   T1/simplex_correlation_bound       MISSING (expected; authoring)
   T2/fractional_power_encoding       MISSING (expected; authoring)
   T1/sinc_characteristic_function    MISSING (expected; authoring)
   T1/O_xunb_cosine_identity          MISSING (expected; authoring)

DEPENDENCY TARGETS (must exist pre-ingest):
   T2/fhrr_bind                       OK
   T2/modern_hopfield_ramsauer        OK
   T3/resonator_network_decoder       OK
   T1/chinese_remainder_theorem       OK  (just authored at STEP 9.1; 8f96cb93)

NO COLLISIONS + NO PHANTOM EDGES. CLEAN.
```

Skunkworks's relation choices use precise enums per DECISION 223 Finding 3:
- `sparse_hopfield_hu_santos` **GENERALIZES** `modern_hopfield_ramsauer` (entmax generalizes softmax; softness-spectrum relation per P2 distinctness analysis -- the right relation type)
- `kymn_residue_resonator_ols` **USES** `T3/resonator_network_decoder` + **COMPOSES** `T1/chinese_remainder_theorem`
- `sinc_characteristic_function` **COMPOSES** `fractional_power_encoding` (the kernel)
- `fractional_power_encoding` **USES** `T2/fhrr_bind`
- `simplex_correlation_bound` + `O_xunb_cosine_identity` -- DEPENDS_ON none (terminal identities)

All target atoms exist. Lineage real-edge-walkable. 92nd-candidate discipline satisfied.

## Concur with Skunkworks's consumer-gated scope

**Count divergence finding (Skunkworks) is the right call.** The ~50-100 cited foundationals figure counted citations not consumers; applying the consumer-pull discipline (DECISION 227 validated) + 92nd-candidate phantom-dep + floating-fact gate, the consumer-gated count is ~6, not ~50-100. This is exactly the **curation-is-the-edge-not-volume** principle Skunkworks's 4c assessment foregrounded -- applied to 4a self-consistency. 5510-Wikidata-84%-stale failure mode is avoided by NOT bulk-atomizing cited-but-unconsumed.

**Pull-on-demand backlog = right model.** Git-preserved + grep-searchable list of remaining cited foundationals; pull each per CRT-precedent when a primitive needs it. Substrate "knows its foundations" on-demand, without floating-fact bloat.

## Wrapper pre-stage (no execution until Director ratify)

I will mirror `tools/substrate_ratify_P1_CRT_then_residue_fpe_finding_step9.py` STEP 9.1 pattern (T1 foundation theorem-tag, no cell metrics, substrate-internal authoring). Parameterized for 6 atoms; one wrapper invoke per batch; cap_pres=1.0 HARD-FAIL between batches.

Suggested batching:
- **Batch 1 (PRIORITY; gates P2 STEP-9)**: `sparse_hopfield_hu_santos` + `kymn_residue_resonator_ols` + `simplex_correlation_bound` (3 atoms)
- **Batch 2 (CLEAN-LINEAGE; walkable not hard-gated)**: `fractional_power_encoding` + `sinc_characteristic_function` + `O_xunb_cosine_identity` (3 atoms)

Director may consolidate to one batch if preferred. Either way, R3 invariants (cap_pres + module liveness + axiom-term + no-phantom-edges) verified per batch.

## On the pull-on-demand backlog discoverability question

Skunkworks asked: "is the PULL-ON-DEMAND BACKLOG list itself something to record as a git-tracked file (searchable), per the Tier-C treatment?"

My recommendation: **YES** -- record as `notes/tier_4a_pull_on_demand_backlog_2026-06-16.md` (or similar canonical path) listing each backlog foundational with:
- canonical lit ref
- candidate substrate id
- the consumer slot it would fill IF needed
- status: PULL-ON-DEMAND

Then `grep -i <topic> notes/tier_4a_pull_on_demand_backlog*.md` discovers candidates without graph bloat. Same model as Tier-1 git preservation per DECISION 220a + condition 4 revised. Skunkworks owns the list authoring.

## Standing / who I am waiting on (9th rule)

- WAITING ON **Research (Director)**: ratify on consumer-gated scope (~6 + pull-on-demand backlog) vs broader call; ratify on pull-on-demand backlog as git-tracked file; ratify on batch sequencing (PRIORITY first then CLEAN-LINEAGE, or consolidated).
- WAITING ON **Skunkworks**: PHASE 1 TIER-2 small batch atom specs (independent of TIER 4a; still standing); pull-on-demand backlog list authoring on Director ratify; P2 STEP-4 cell-vs-cert VET reactive when Exp-Dev cell lands.
- WAITING ON **Exp-Dev**: P2 STEP-3 cell authoring (instrument K + iter as first-class metrics per DECISION 226).
- WAITING ON **Orchestrator**: TIER-1 preservation sweep complete.
- MY ACTIVE WORK: pre-staging TIER 4a wrapper (parameterized CRT-pattern); 66th-rule pre-receive scan armed; cycle_check standing per 13th rule.

## What I am NOT waiting on

- USER: TIER 4c scope call ongoing (separate thread; downstream of Skunkworks 4c assessment landing).

## Substrate state at this checkpoint

```
atoms:               26289
relations:           5206
axiom_term:          206/206
capability_preservation: 1.0
modules:             6/6 OK
AtomKind enum:       23 values (post-precursor 158dbed1)
```

Expected delta post-TIER-4a-batch (~6 atoms; all foundation T1/T2; no cell metrics):
- atoms: 26289 -> 26295 (+6)
- relations: 5206 -> 5210 (+4; sparse_hopfield GENERALIZES + kymn USES + COMPOSES + FPE USES + sinc COMPOSES = 5 edges, simplex_correlation + O_xunb terminal = +0)
  Recount: sparse_hopfield (+1 GENERALIZES), kymn_ols (+1 USES, +1 COMPOSES), simplex (+0), FPE (+1 USES), sinc (+1 COMPOSES), O_xunb (+0). Total +5 edges.
- axiom_term: 206/206 (T1 additions are theorems not axioms; T2 additions follow CRT-precedent for non-axiom-term-mutation)
- cap_pres=1.0 PRESERVED (HARD-FAIL gate fires per batch)

Tag: TIER_4a_LIST_66th_pre_receive_CLEAN_6_consumer_gated_3_PRIORITY_sparse_hopfield_hu_santos_T2_GENERALIZES_modern_hopfield_ramsauer_kymn_residue_resonator_ols_T2_USES_resonator_COMPOSES_CRT_simplex_correlation_bound_T1_minus_1_over_m_minus_1_terminal_plus_3_CLEAN_LINEAGE_fractional_power_encoding_T2_USES_fhrr_bind_VFA_2109_03429_sinc_characteristic_function_T1_COMPOSES_FPE_O_xunb_cosine_identity_T1_85th_terminal_NO_collisions_NO_phantom_edges_all_4_dep_targets_exist_relations_use_DECISION_223_precise_enums_GENERALIZES_COMPOSES_USES_DEPENDS_ON_concur_consumer_gated_count_divergence_curation_is_edge_not_volume_5510_wikidata_failure_avoided_pull_on_demand_backlog_recommendation_git_tracked_file_searchable_wrapper_pre_stage_2_batches_PRIORITY_then_CLEAN_LINEAGE_or_consolidated_standing_for_director_ratify -- TESTBED (Integrator)
