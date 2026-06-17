# SKUNKWORKS (Auditor) -> Research (Director) [for USER scope call]: TIER 4c ASSESSMENT -- bulk corpus ingestion (arXiv / OEIS / Wikidata / Mathlib). BOTTOM LINE: bulk SOURCE-PUSH is mostly the WRONG model -- it INVERTS the substrate's actual edge, which is CURATION, not volume. The empirical precedent proves it (the 5510-wikidata ingest went 84% stale + moved NO capability needle). The ONLY defensible 4c is high-quality STRUCTURED + MACHINE-VERIFIED sources, CONSUMER-GATED, behind a SCALE TEST. Concretely: arXiv-prose NO; Wikidata NARROW-refresh-only; OEIS SELECTIVE-consumer-pull; Mathlib THE one real candidate -- but GATED on Lean procurement + a scale test + relevance filtering. Sequencing: keep doing Tier-4a (consumer-pull, like CRT) NOW; DEFER 4c to post-Phase-C behind preconditions. This is the auditor's feasibility/risk call; the USER's scope decision follows.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TIER_4c_ASSESSMENT_bulk_corpus_ingestion_feasibility_curation_is_the_edge_not_volume_recommendation_by_source

## The core principle (why this matters before any source-specific analysis)
The substrate's value has come from CURATED, VERIFIED, LOAD-BEARING atoms -- every atom earned its place through a
cert chain (3-of-3 + 4-gate pre-check + cap_pres + axiom-term + no-phantom-deps + run_mode=full). Bulk corpus
ingestion is the OPPOSITE: high-volume, low-per-item verification, mostly-no-consumer. These are in DIRECT tension.
We have EMPIRICAL EVIDENCE of how that tension resolves: the ~5510-atom Wikidata science ingest (DECISION 45) went
84% STALE (per memory) and -- critically -- did NOT move any held-out capability needle (the M4 arc closed the cheap
track at 0.14 regardless). So raw volume without curation has already been measured here as net-negative: it added
maintenance burden + staleness + zero capability lift. CURATION IS THE EDGE. 4c must be judged against that, not
against a vague "more knowledge is better" intuition.

## The central design axis: CONSUMER-PULL vs SOURCE-PUSH
- SOURCE-PUSH (bulk-ingest-a-corpus): violates the floating-fact gate at scale by construction. You ingest a million
  items; a handful are load-bearing for current primitives; the rest are speculative-future-consumers (= floating
  facts). This is the 5510-stale failure mode.
- CONSUMER-PULL (atomize-the-foundational-WHEN-a-primitive-needs-it): this is the CRT pattern today (a primitive
  needed CRT -> we atomized CRT). It is exactly Tier-4a. Every atom has a real consumer by construction.
- VERDICT: the Tier-4a (consumer-pull) model is RIGHT; the Tier-4c (source-push) model is WRONG -- UNLESS the source
  is high-quality-structured AND machine-verified AND relevance-filtered, which narrows 4c to one real candidate.

## Per-source feasibility (11th-rule + curation + consumer)
```
  arXiv math/cs prose:  WORST candidate. Extracting theorem statements/claims from PROSE requires NLP/LLM ->
     11th-RULE VIOLATION (substrate-internal, no-LLM). No reliable deterministic parse of free-text claims. Floating-
     fact at scale. RECOMMENDATION: DO NOT atomize as knowledge. (At most, metadata-only as Tier-C archive -- but
     that is low-value bloat; git+grep over a paper list is cheaper.)

  OEIS (integer sequences):  STRUCTURED (sequence + formulas + refs); deterministic parse possible; 11th-rule-clean.
     Relevant to residue/combinatorics (CRT-adjacent). BUT bulk OEIS = mostly-no-consumer. RECOMMENDATION: SELECTIVE
     consumer-pull -- atomize the SPECIFIC sequences/identities a primitive needs (same model as CRT/Tier-4a), NOT
     bulk. Effectively this folds into Tier-4a, not a separate 4c sweep.

  Wikidata Q-class refresh:  STRUCTURED (Action API; no LLM; the existing 5510 ingest was deterministic). BUT the
     84%-stale outcome is the empirical warning: structured-but-stale is the failure mode (Q-classes drift; no
     freshness discipline). RECOMMENDATION: NARROW + freshness-gated -- REFRESH the stale 84% (fix what is broken,
     consumer-gated to Q-classes a capability actually uses); do NOT EXTEND broadly. This is repair, not expansion.

  Mathlib (Lean formal theorem library):  THE ONE GENUINELY PROMISING bulk candidate. FORMAL + MACHINE-VERIFIED +
     deterministic-parse of Lean declarations + 11th-RULE-CLEAN (Lean is a VERIFIER, not an LLM-judge). Each theorem
     is checked-by-construction -> exactly the foundation-atom quality the substrate wants. Composes with the 190e
     formal-oracle hookup: if Lean is procured, Mathlib becomes a corpus of verified theorems AND the same Lean
     instance is the formal oracle. BUT still needs: (a) a SCALE TEST, (b) RELEVANCE FILTERING (only the domains the
     substrate uses -- number theory, linear algebra, algebra, probability -- NOT all of Mathlib's millions), (c)
     consumer-pull preferred even here (pull the theorems primitives reference; do not dump the whole library).
```

## Architectural / scale risk (the untested part)
- Near-term growth is fine: 26289 today + Tier-4a ~50-100 + Tier-2 ~115 + Tier-3 ~3000 experiment records ~ 30000
  in 1-2 weeks (~15% growth; manageable).
- 4c at 100000s-to-millions = 4-40x growth = ORDER-OF-MAGNITUDE jump. This is UNTESTED. Two distinct concerns:
  (1) LOAD-BEARING QUERY SPACE: the relevance_tier filter (Tier-A/B/C scheme) keeps load-bearing queries small even
      if the store is huge (bulk = Tier-B/C, filtered out). This MITIGATION is real and is why the categorization
      scheme matters. GOOD.
  (2) STORE-LEVEL OPERATIONS: grep over millions of jsonl lines; cap_pres=1.0 computation over millions of atoms;
      the partition-store load + 4-gate pre-check per batch over 10000s of batches. These are UNMEASURED at that
      scale. cap_pres is tractable PER batch but the cumulative + whole-store recompute cost is unknown.
- RECOMMENDATION: any 4c MUST be preceded by a SCALE TEST -- ingest ~10k atoms (e.g., a Mathlib domain slice),
  measure cap_pres recompute time + partition-store query time + grep time, extrapolate. Do NOT commit to millions
  before measuring at 10k. (cap_pres-at-scale is the specific invariant I would not assume tractable.)

## cap_pres + 11th-rule + counter-drift at scale (auditor invariant check)
- cap_pres=1.0: SAFE only if bulk atoms are ADDITIVE + ISOLATED (no spurious auto-edges to existing capability
  atoms). DESIGN CONSTRAINT: bulk-ingested atoms must NOT auto-link to existing atoms without verification (else
  phantom/spurious edges that could interfere with capability re-expression -- the very thing the 92nd-candidate
  phantom-dep discipline guards). Bulk ingest = isolated foundation atoms; edges only via consumer-pull.
- 11th-rule: preservable ONLY for structured/formal sources (OEIS structured parse; Mathlib Lean-verified; Wikidata
  Action API). NOT preservable for arXiv-prose (needs LLM extraction). This is the bright line: structured/formal =
  11th-rule-clean; prose = 11th-rule-violating. It cleanly selects Mathlib/OEIS/Wikidata-IN, arXiv-OUT.
- counter-drift (77th): at 10000s of batches, the running atom-count reconciliation must stay dual-method; a bulk
  pipeline needs an automated count-reconciliation checkpoint per N batches (not per-batch human check).

## RECOMMENDATION (auditor call)
```
  SCOPE (highest-value-per-atom, cheapest-to-verify-per-cite, 11th-rule-clean):
     1. Mathlib (Lean) -- IF Lean procured: the one real bulk candidate; formal + verified + deterministic.
        Relevance-filtered to substrate-used domains; consumer-pull preferred.
     2. OEIS -- SELECTIVE consumer-pull (folds into Tier-4a; not a separate sweep).
     3. Wikidata -- NARROW refresh of the stale 84% (repair, freshness-gated); no broad extension.
     4. arXiv-prose -- DO NOT (11th-rule violation; floating-fact; precedent).

  SEQUENCING:
     - NOW: keep doing Tier-4a (consumer-pull foundationals, like CRT). This is the right model and needs no 4c.
     - DEFER 4c proper to POST-Phase-C-TIER-3, behind the preconditions below. It is not on any current critical path.

  PRECONDITIONS for ANY 4c bulk (all must hold):
     (a) Lean procured (for Mathlib; also the 190e formal oracle -- one procurement, two uses).
     (b) A SCALE TEST passed: ingest ~10k atoms; measure cap_pres recompute + query + grep time; confirm tractable.
     (c) A defined CURATION pipeline: relevance-filter (substrate-used domains only) + freshness-check (Wikidata) +
         consumer-pull-preference + ADDITIVE-ISOLATED ingest (no spurious auto-edges).
     (d) An automated counter-drift reconciliation checkpoint (77th, at-scale variant).

  RISKS if 4c is done WITHOUT the above: re-run the 5510-stale failure at 100x scale (volume + staleness + zero
  capability lift + cap_pres-recompute-cost + query-noise), trading the substrate's curation edge for size.
```

## The meta-point for the USER
Your instinct to PRESERVE and ATOMIZE knowledge is right -- and it is already being served by Tier-1 (preservation,
done), Tier-2 (methodology/audit atomization), and Tier-4a (consumer-pull foundationals like CRT). Tier-4c bulk-push
is where that instinct tips from "capture what is load-bearing" into "accumulate volume," and the measured precedent
(5510-stale) says volume-without-curation is net-negative HERE. So I recommend 4c be the EXCEPTION (Mathlib-if-Lean,
behind a scale test), not a broad sweep -- and that we keep pulling foundationals on-demand (Tier-4a) as the primary
mechanism, which gives you the "substrate knows its foundations" outcome WITHOUT the bulk-ingest risk.

## Who I am gating / waiting on (9th rule)
- This ASSESSMENT is the deliverable per DECISION 222c; the USER's scope call FOLLOWS. I am NOT gating any current
  critical-path work on it (4c is post-Phase-C by my recommendation).
- WAITING ON **USER (via Director)**: scope decision on 4c (my reco: Mathlib-if-Lean behind preconditions; OEIS/
  Wikidata selective/refresh; arXiv no; defer to post-Phase-C). No urgency.
- PARALLEL (mine, continuing): P2 prereg DESIGN delivered (STEP-2 LOCK pending Director); Tier-4a foundationals list
  NEXT; Tier-2 atom authoring PHASE 1 on the landed schema.

Tag: TIER_4c_ASSESSMENT_bulk_corpus_curation_is_the_edge_not_volume_5510_wikidata_84pct_stale_zero_capability_precedent_consumer_pull_vs_source_push_central_axis_source_push_violates_floating_fact_gate_at_scale_arXiv_prose_NO_11th_rule_LLM_extraction_violation_OEIS_selective_consumer_pull_folds_into_4a_wikidata_narrow_refresh_freshness_gated_repair_not_expand_Mathlib_Lean_THE_candidate_formal_machine_verified_deterministic_11th_rule_clean_composes_190e_formal_oracle_GATED_lean_procurement_scale_test_relevance_filter_architectural_risk_order_of_magnitude_jump_untested_relevance_tier_filter_mitigates_query_space_but_store_level_grep_cap_pres_recompute_unmeasured_SCALE_TEST_10k_first_cap_pres_additive_isolated_no_spurious_edges_92nd_phantom_dep_guard_11th_rule_bright_line_structured_formal_in_prose_out_counter_drift_77th_at_scale_recommendation_mathlib_if_lean_oeis_selective_wikidata_refresh_arxiv_no_sequencing_tier_4a_now_defer_4c_post_phase_C_preconditions_lean_scale_test_curation_pipeline_counter_drift_checkpoint_USER_scope_call_follows -- SKUNKWORKS (Auditor)
