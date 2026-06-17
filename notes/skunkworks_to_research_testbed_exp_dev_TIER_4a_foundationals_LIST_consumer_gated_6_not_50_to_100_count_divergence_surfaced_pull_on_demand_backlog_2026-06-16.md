# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: TIER 4a foundationals LIST (DECISION 222b; +sparse_hopfield per 227). I applied the consumer-pull discipline (now Director-validated, DECISION 227) + the 92nd-candidate phantom-dep check (each entry must be formalizable-as-theorem AND have a REAL consumer) to my OWN list -- and per DECISION 222b's explicit instruction to surface count divergence: the CONSUMER-GATED count is ~6 (3 P2-gating + 3 clean-lineage), NOT ~50-100. The ~50-100 "cited foundationals" are mostly FLOATING (no current consumer) -> bulk-atomizing them IS the source-push anti-pattern my 4c assessment warns against. RECOMMENDATION: atomize the ~6 consumer-relevant NOW (CRT-pattern); keep the rest as a PULL-ON-DEMAND BACKLOG (searchable, git-preserved), pulled when a primitive needs them (CRT precedent). This makes 4a self-consistent with 4c's consumer-pull verdict.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TIER_4a_foundationals_LIST_consumer_gated_6_not_50_to_100_count_divergence_surfaced_pull_on_demand_backlog

## The count-divergence finding (surfaced per DECISION 222b instruction)
DECISION 222b: "if the actual cited-foundationals count diverges substantially from ~50-100, surface to Director for
USER scope adjustment." It does. Applying CONSUMER-GATING (atomize a foundational iff a CURRENT primitive DEPENDS_ON
it -- the consumer-pull model DECISION 227 just validated), the count is ~6, not ~50-100. The ~50-100 figure counts
foundationals CITED-SOMEWHERE; most have NO current consumer (= floating facts). Bulk-atomizing cited-but-unconsumed
foundationals is exactly the source-push anti-pattern (the 5510-Wikidata-84%-stale failure mode). So 4a should be
consumer-gated like CRT was, NOT a 50-100 bulk sweep. This is GOOD (the curation discipline working), not a shortfall.

## ATOMIZE NOW -- consumer-gated foundationals (Testbed: CRT-pattern; cap_pres=1.0 per batch)

### PRIORITY (hard P2 consumers; gate P2 STEP-9 DEPENDS_ON)
```
  1. sparse_hopfield_hu_santos   [P2 HEAD-3]   -- PRIORITY (gates P2 STEP-9)
     kind: primitive; tier: T2; corpus: math
     desc: sparse modern-Hopfield retrieval via entmax/alpha-entmax (sparse support; sharper basins; exact retrieval
           under a margin/sparsity condition; tolerates non-orthogonal/simplex-correlated codewords).
     refs: Hu et al. "On Sparse Modern Hopfield Model" (NeurIPS 2023); Santos et al. "Sparse and Structured Hopfield
           Networks" (arXiv:2402.13725, ICML 2024); entmax operator (Peters et al. 2019).
     RELATION (auditor precision -- NOT plain DEPENDS_ON): entmax GENERALIZES softmax (softmax = entmax at alpha=1)
           -> use RelationType.GENERALIZES: sparse_hopfield_hu_santos GENERALIZES modern_hopfield_ramsauer
           (equivalently modern_hopfield_ramsauer SPECIALIZES it). This is the softness-spectrum relation from the
           P2 distinctness analysis, stated precisely (NOT a dependency; a generalization).

  2. kymn_residue_resonator_ols  [P2 HEAD-4]   -- PRIORITY (gates P2 HEAD-4 / GATE-F)
     kind: primitive; tier: T2; corpus: math
     desc: residue resonator factorization via OLS/projection dynamics (Gram^-1 handles non-orthogonal residue
           codewords); the de-risked HEAD-4 recipe builds on this. LOG-SCALING is WITHIN-CAPACITY (Kymn) -- atom
           must state the within-capacity caveat (do NOT imply unconditional log-scaling; consistent with GATE-F).
     refs: Kymn et al. "Computing with Residue Numbers in High-Dimensional Representation" (arXiv:2311.04872).
     RELATION: USES T3/resonator_network_decoder + USES/COMPOSES T1/chinese_remainder_theorem (residue factorization).

  3. simplex_correlation_bound   [P1 B2 diagnosis + P2 HEAD-3/4]
     kind: primitive; tier: T1; corpus: math
     desc: regular-simplex geometry -- m equally-spaced unit vectors (or m residue phasor codewords) have pairwise
           correlation EXACTLY -1/(m-1). This is the codeword-non-orthogonality the OLS-Gram + sparse-Hopfield handle.
     refs: regular simplex / equiangular-set geometry (elementary linear algebra; exact identity, no external dep).
     RELATION: DEPENDS_ON none (terminal algebraic identity).
```

### CLEAN-LINEAGE (lower priority; CURRENTLY grounded via existing atoms/gates -- atomize for walkable lineage, NOT hard-gated)
```
  4. fractional_power_encoding   [P1/P2 continuous encoding]
     NOTE honest: P1 already grounds the single-channel kernel via T2/fhrr_bind + its own GATE-A (per my STEP-7 VET);
     so this is CLEAN-LINEAGE, not a hard DEPENDS_ON gap. Atomize for a precise FPE/VFA/SSP lineage atom.
     kind: primitive; tier: T2; corpus: math
     refs: Frady, Kleyko, Kymn, Olshausen, Sommer "Computing on Functions Using Randomized Vector Representations"
           (VFA; arXiv:2109.03429, 2021); Komer & Eliasmith SSPs (CogSci 2019).
     RELATION: USES T2/fhrr_bind (complex-exp representation).

  5. sinc_characteristic_function [P1 GATE-A]
     NOTE honest: P1 GATE-A already grounds this by measurement; clean-lineage atom.
     kind: primitive; tier: T1; corpus: math
     desc: E_{theta~U(-pi,pi)}[cos(d*theta)] = sin(pi d)/(pi d) = sinc(d) -- the characteristic function of the
           uniform base-phase distribution; the single-channel FPE similarity kernel.
     refs: characteristic function of the uniform distribution (elementary probability; exact identity).
     RELATION: DEPENDS_ON none (terminal identity); COMPOSES fractional_power_encoding (its kernel).

  6. O_xunb_cosine_identity      [distinctness-verification; 85th candidate]
     kind: primitive; tier: T1; corpus: math
     desc: elementwise-unbind-then-mean-inner-product equals the cosine algebra (the identity behind the O_xunb
           cert-miss: O_xunb is NOT a distinct competitor from O_corr). Consumer: the competitor-distinctness
           verification discipline (used in P1 STEP-7 + P2 HEAD distinctness analysis).
     refs: substrate-derived algebraic identity (85th audit-discipline instance).
     RELATION: DEPENDS_ON none (terminal identity).
```

## PULL-ON-DEMAND BACKLOG (do NOT bulk-atomize; pull when a primitive needs one)
The remaining ~50-100 cited foundationals (other Hopfield/VSA variants, OEIS sequences, Steinert-Threlkeld quantifier
theory, assorted info-theory/changepoint results cited in passing, etc.) have NO current consumer. Per the consumer-
pull verdict (DECISION 227) + the floating-fact gate, keep them as a SEARCHABLE BACKLOG LIST (git-preserved; grep-
findable) and PULL each as a primitive needs it (the CRT precedent: CRT was pulled when P1 needed it). This avoids the
source-push / 5510-stale failure mode AND gives the "substrate knows its foundations" outcome on-demand.

## Honest checks I applied to my own list (verify-not-assume; 92nd phantom-dep on the list itself)
- Each entry is FORMALIZABLE as a theorem/identity (not vague prose): sparse-retrieval bound; OLS resonator
  dynamics+convergence; -1/(m-1) exact identity; FPE-kernel = char-function theorem; sinc identity; O_xunb identity.
- Each entry has a REAL consumer named (P2 HEAD-3 / HEAD-4 / P1 diagnosis / distinctness discipline). The 3 clean-
  lineage entries are HONESTLY flagged as currently-grounded-via-existing-atoms (not hard gaps).
- No phantom edges: relations point only to atoms that exist (fhrr_bind, modern_hopfield_ramsauer, CRT, resonator_
  network_decoder all in store) OR are co-authored in this batch.

## Who I am gating / waiting on (9th rule)
- WAITING ON **Research (Director)**: confirm the consumer-gated scope (~6 now + pull-on-demand backlog) -- or
  direct broader if you/USER want more atomized (I'd flag those as lower-value-per-curation-discipline). Also: is
  the PULL-ON-DEMAND BACKLOG list itself something to record as a git-tracked file (searchable), per the Tier-C
  treatment?
- WAITING ON **Testbed**: atomize the ~6 per CRT-pattern when scope confirmed; sparse_hopfield_hu_santos + kymn_
  residue_resonator_ols PRIORITY (P2 STEP-9 dep). 66th-rule pre-receive on the batch. Note the GENERALIZES relation
  for sparse_hopfield (not DEPENDS_ON).
- MY active work: Tier-2 PHASE-1 atom specs next; P2 STEP-4 cell-vs-cert VET reactive when Exp-Dev's cell lands.

Tag: TIER_4a_foundationals_LIST_consumer_gated_count_divergence_surfaced_per_DECISION_222b_6_not_50_to_100_priority_sparse_hopfield_hu_santos_P2_HEAD3_GENERALIZES_modern_hopfield_ramsauer_entmax_generalizes_softmax_kymn_residue_resonator_ols_P2_HEAD4_within_capacity_caveat_USES_resonator_network_decoder_CRT_simplex_correlation_bound_minus_1_over_m_minus_1_T1_terminal_clean_lineage_fractional_power_encoding_VFA_frady_sommer_2109_03429_komer_eliasmith_SSP_USES_fhrr_bind_sinc_characteristic_function_uniform_dist_P1_GATE_A_O_xunb_cosine_identity_85th_candidate_distinctness_pull_on_demand_backlog_rest_50_100_no_consumer_floating_fact_git_searchable_CRT_precedent_consumer_pull_self_consistent_with_4c_no_phantom_edges_formalizable_check_applied_to_own_list -- SKUNKWORKS (Auditor)
