# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 49 -- dispatch 3 foundational works in parallel with DECISION 38; substrate enrichment that directly strengthens M4d Phase 2 scaffolding

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~20:30
**Re:** USER authorized all three foundational work candidates. Substrate-internal; unblocked; composes with M4d.

## CONTEXT

While DECISION 38 (decisive H_M4 vs H_INGEST test) runs on remote, three substrate-internal foundational works are unblocked AND directly strengthen the typed-operator graph M4d will walk in Phase 2.

Per Drill A + Drill B synthesis:
- M4d (capability-graph walk) addresses 44pct of held-out failures (F1+F2 retrieval cluster)
- Foundation primitives + ingested atoms scaffold M4d (NOT dead weight)
- More edges in the graph = M4d has more to walk = better Phase 2 outcomes

DECISION 49 dispatches three parallel works that enrich the graph BEFORE Phase 2 M4d ships. Each work has clear HARD-PASS + falsifier + substrate-internal per 11th rule.

## DECISION 49a -- SHARES_MATH bridge authoring (Skunkworks)

**Goal:** Author 10-20 SHARES_MATH bridges between existing math foundation atoms; deepen the relational graph M4d will walk.

### Spec

1. **High-priority bridge candidates** (per Drill 1 + Drill A F3-partial atoms):
   - spectral_theorem <-> SVD
   - characteristic_function <-> discrete_fourier_transform
   - fourier_transform_signal <-> fourier_transform_probability
   - inner_product <-> bilinear_form (when symmetric positive definite)
   - measure_preserving_map <-> isomorphism_of_measure_spaces
   - hilbert_space <-> reproducing_kernel_hilbert_space
   - lie_group_action <-> covering_space_map
   - random_variable <-> measurable_function_to_R
   - convolution_theorem <-> circular_convolution
   - bayes_rule <-> conditional_probability
2. **Priority targets for Drill A F3-partial atoms** (Q60-G, Q61-A, Q64-G):
   - Find atoms substrate already has that are SHARES_MATH-related to the gold for these questions
   - Adding these bridges may close the F3 partial-deduction gap directly

3. **Output:** `data/substrate_index/skunkworks_shares_math_bridges_v1.jsonl` (Phase-4 ratification shape)

### Reservations

- **R1 (USER 11th rule):** substrate-internal; no LLM-assist
- **R2 (sound bridges):** each bridge must be PROVABLY-SHARES-MATH per CHTV-1; substrate refuses what cannot be proven (18th rule)
- **R3 (no false-merges):** bridge != PROVABLY_EQUIVALENT; bridges are weaker (math relationship, not type equivalence)
- **R4 (audit trail):** each bridge logs the math relationship (e.g. "SVD is spectral_theorem applied to A^T A; ranks/eigenvalues preserved")

### HARD-PASS / HARD-FAIL

- **HARD-PASS:** 10+ bridges authored + CHTV-1 verified + 0 false-PROVABLY_EQUIVALENT
- **HARD-FAIL 1:** <5 bridges produced (most candidates unsound at CHTV-1 check)
- **HARD-FAIL 2:** any false-PROVABLY_EQUIVALENT (sound bar violated)

### Cost

~30-60 min Skunkworks. Substrate-internal.

## DECISION 49b -- Abstraction analysis on 5510 wikidata atoms (Exp-Dev)

**Goal:** Run F2 abstraction tool on the 5510 newly-ingested wikidata atoms; identify SHARED_ABSTRACTION groups + special-case relationships.

### Spec

1. Run `tools/substrate_abstraction_ratio_v0.py` (or evolved) on the 5510 atoms ONLY (not full corpus)
2. Identify:
   - SHARED_ABSTRACTION groups (atoms sharing OUTPUT TYPE + OPERATION across topics)
   - INVERSE_PAIR candidates (atoms doing opposite operations)
   - THEOREM_LINKED relationships (atoms connected by proven theorems)
   - Special-case-of patterns (Cauchy-Schwarz -> Hölder; central_limit -> Lindeberg-Lévy; Brouwer -> Kakutani)
3. **Output:** SHARED_ABSTRACTION + INVERSE_PAIR groupings; per-pair derivation_present flag

### Reservations

- **R1 (USER 11th rule):** substrate-internal
- **R2 (3-mode taxonomy):** distinguish ATOM-REMOVING (Class A) + STRUCTURE-ADDING (Class B) per 20th rule; REFUSE what cannot be proven
- **R3 (Auditor PROVEN vs TENTATIVE split):** per DECISION 13 + Auditor F2 audit; same-output-type-only = TENTATIVE; same-operation = PROVEN

### HARD-PASS / HARD-FAIL

- **HARD-PASS:** 20+ SHARED_ABSTRACTION groups identified + 0 false-merges + 5+ INVERSE_PAIR + 3+ THEOREM_LINKED
- **HARD-FAIL 1:** <5 groups (corpus too sparse)
- **HARD-FAIL 2:** any false-merge (capability_preservation violated)

### Cost

~1 hr Exp-Dev. Runs on laptop. No bge required.

## DECISION 49c -- 14 qclass atoms ingest (Testbed + Skunkworks)

**Goal:** Close the 5133 missing-endpoint edges from INGEST_PHASE_6 by ingesting the 14 qclass atoms that the 5510 wikidata atoms depend on.

### Spec

1. **Skunkworks drafts** the 14 qclass atoms from `data/substrate_index/external/wikidata_action_api/qclass_whitelist_v1.json` (Exp-Dev's validated list)
2. **Testbed atomic ratifies** per Phase-4 pattern; the 5133 dangling DEPENDS_ON edges become complete
3. Each qclass atom: id `T1/wikidata_qclass_Qxxx`; algebra_dict with category (theorem-class, scientific_concept, etc.); SPECIALIZES path to category_type (one of the 46b foundation primitives)

### Reservations

- **R1 (USER 11th rule):** substrate-internal
- **R2 (foundation primitive grounding):** each qclass atom must SPECIALIZES category_type (the 46b primitive); preserves T0 bedrock chain
- **R3 (R2 held-out integrity):** verify no qclass label collides with held-out gold atom labels

### HARD-PASS / HARD-FAIL

- **HARD-PASS:** 14 qclass atoms ingested + 5133 missing-endpoint edges complete + capability_preservation preserved + axiom termination 213/213 maintained
- **HARD-FAIL 1:** <10 qclass atoms successfully ingested
- **HARD-FAIL 2:** any held-out gold contamination
- **HARD-FAIL 3:** axiom termination drops

### Cost

~30 min Skunkworks draft + ~30 min Testbed ratification. Substrate-internal.

## SEQUENCING

All three works run in PARALLEL (different lanes; no dependencies between them).

49a Skunkworks bridges + 49c Skunkworks qclass drafts can be sequenced or batched by Skunkworks.

49b Exp-Dev abstraction analysis is LANE-INDEPENDENT (laptop; no remote sync required; doesn't interfere with DECISION 38 remote run).

## What this unlocks for Phase 2 M4d

- 10-20 NEW SHARES_MATH bridges = denser graph for M4d to walk
- 20+ SHARED_ABSTRACTION groups identified on 5510 wikidata = more unification structure
- 5133 missing-endpoint edges completed = every wikidata atom has real grounding
- Substrate-product positioning: foundational depth empirically demonstrated, not just claimed

## What this DOESN'T affect

- DECISION 38 still in flight on remote (per DECISION 48 sync)
- Phase 2 sequencing decision still gated on DECISION 38 result
- Tier 1+2 production-verified UNAFFECTED
- 100pct axiom termination preserved (all three works are additive)
- capability_preservation = 1.0 invariant (all three works enforce R3 verify)

## DECISION 38 status check

3.5 hours of silence since 46c result. DECISION 48 sync was authorized at 16:55; if sync + measurement takes <30 min as Exp-Dev estimated, DECISION 38 should have landed by ~17:30. It hasn't.

Possible: Exp-Dev session was inactive this window OR remote sync hit safety-denied path again OR measurement is slow.

Director recommends: Exp-Dev re-check DECISION 48 sync status if reading this routing note; surface any new blocker via BLOCKER tag.

## Cross-references

- USER authorization: "Authorized for all" this turn
- Drill A failure taxonomy: this session inline
- Drill B Phase 2 reframe: this session inline
- DECISION 46c COMBINED: commits (`cce219c1` + earlier 21st honest finding)
- DECISION 48 Option A sync: commit `2f280cc9`
- Testbed 14-qclass offer: `notes/testbed_to_research_exp_dev_MILESTONE_DECISION_45_RATIFIED_*` (commit `934be79e`)

---

**Skunkworks + Exp-Dev + Testbed:** DECISION 49 three foundational works in PARALLEL (substrate-internal; unblocked by DECISION 38). 49a Skunkworks SHARES_MATH bridges (10-20; CHTV-verified sound; HARD-PASS 10+). 49b Exp-Dev abstraction analysis on 5510 wikidata atoms (laptop; F2 tool; HARD-PASS 20+ SHARED_ABSTRACTION + 0 false-merges). 49c Skunkworks + Testbed 14 qclass atoms ingest (closes 5133 missing-endpoint edges; SPECIALIZES category_type 46b primitive). All three enrich the typed-operator graph M4d Phase 2 will walk. Cost ~2-3 hours total across three lanes. Capability_preservation + axiom termination + held-out integrity all preserved.
