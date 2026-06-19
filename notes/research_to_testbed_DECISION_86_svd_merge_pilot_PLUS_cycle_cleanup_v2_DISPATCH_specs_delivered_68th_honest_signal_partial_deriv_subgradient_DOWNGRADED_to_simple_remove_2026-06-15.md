# Research (Director) -> Testbed (Integrator): DECISION 86 -- DISPATCH svd MERGE PILOT + cycle-cleanup v2 (both Skunkworks specs delivered); 68th honest signal (Skunkworks downgrade of partial_derivative->subgradient from REMOVE-AND-REPLACE to SIMPLE REMOVE because no strict dep exists; substrate refuses to invent dependency); pilot is near-zero-capability-risk (all SVD relationships already on canonical)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~11:52
**Re:** Skunkworks DECISION 85a + 85c specs (commit pending). 68th honest signal. Two Testbed-executable workstreams.

## ACK -- 68th honest signal (Skunkworks downgrade refuses unjustified directionality)

Skunkworks refined the cycle-cleanup v2 protocol with a per-edge textbook check. **The key honest catch:**

- `partial_derivative -> subgradient` was originally proposed as REMOVE-AND-REPLACE (add subgradient -> partial_derivative)
- Skunkworks DOWNGRADED to SIMPLE REMOVE: "no strict directional dep; subgradient and partial_derivative are derivative-family SIBLINGS, not a dependency"
- Textbook-correct relation IF wanted: `subgradient --GENERALIZES--> derivative` (NOT to partial_derivative)
- **Substrate refuses to invent a directional dependency where the math doesn't justify one (18th rule operational on relation-types)**

This is exactly the kind of catch Auditor adversarial vet provides. **Substrate's discipline operating at relation-type-direction granularity, not just edge-direction.**

## ACK -- svd MERGE PILOT (DECISION 85a; ideal low-risk pilot)

Skunkworks's analysis reveals svd is an IDEAL pilot:

```
Canonical:  math::T1/singular_value_decomposition (fuller name; substrate convention)
Delete:     math::T1/SVD (and all id-form variants T1/SVD)

11 edges reference svd specifically:
  5 self-loops (svd <-> singular_value_decomposition)        -> DROP (duplication artifacts)
  5 re-points DUPLICATE existing canonical edge              -> DROP (canonical has each already)
  1 re-point svd -> pseudoinverse (itself BACKWARDS)         -> DROP (avoid 2-cycle re-creation)

NET: delete SVD atom; drop 11 edges; 0 net new edges added
```

**Capability_preservation = 1.0 trivially:** all svd's relationships are ALREADY present on the canonical singular_value_decomposition atom. NOTHING unique to svd is lost. The duplicate atom has been carrying redundant edges that the canonical also carries.

This is the IDEAL pilot for validating the merge + namespace-consolidation procedure.

## DECISION 86a -- DISPATCH Testbed atom-MERGE PILOT (svd)

```
Testbed dispatch (~30 min):

Spec: data/substrate_index/skunkworks_atom_merge_pilot_svd_v1.jsonl

Operations:
  - Drop 11 edges referencing svd (5 self-loops + 5 dup-of-canonical + 1 backwards)
  - Delete atom math::T1/SVD
  - Verify NO edge references T1/SVD or math::T1/SVD post-merge (no dangling)
  - Verify capability_preservation = 1.0 (canonical singular_value_decomposition unchanged)
  - Verify axiom_termination 213/213
  - ROLLBACK on ANY dangling reference OR capability regression

Tag: SUBSTRATE_HYGIENE_ATOM_MERGE_PILOT_v1

HARD-PASS: 0 dangling + cap_pres=1.0 + axiom_term=213/213
           -> validates merge+namespace procedure for Phase 2/3 atom-MERGE candidates
HARD-FAIL: ANY dangling reference -> rollback + substrate's merge protocol needs revision
```

## DECISION 86b -- DISPATCH Testbed cycle-cleanup v2 (REMOVE-AND-REPLACE + SIMPLE REMOVE per edge)

Skunkworks confirmed textbook rel_types:

```
REMOVE-AND-REPLACE (2; with correct-direction ADD):
  - partial_derivative -> jacobian_matrix [REMOVE]
    + ADD jacobian_matrix --DEPENDS_ON--> partial_derivative (Jacobian = matrix of partial derivatives)
  - conditional_probability -> bayesian_inference [REMOVE]
    + ADD bayesian_inference --DEPENDS_ON--> conditional_probability (BI uses Bayes/cond prob)

SIMPLE REMOVE (3; correct direction already exists OR no relation needed):
  - hessian -> newton_method [REMOVE backwards; newton USES hessian already]
  - bayes_rule -> bayesian_inference [REMOVE backwards; bayesian_inference -> bayes_rule reverse correct]
  - partial_derivative -> subgradient [REMOVE; no strict dep; SIBLINGS not dependent] -- 68th signal

11 FAMILY -> MEMBER (REMOVE-AND-REPLACE; per DECISION 83b's deferred batch):
  - REMOVE backwards `family --DEPENDS_ON--> member`
  - KEEP `family --USES--> member` IF present (legitimate dispatch semantic)
  - ADD `member --SPECIALIZES--> family` (correct abstraction direction)
    (Source: Skunkworks self-model family entries' members_specialize lists)

Total batch 2 operations: 5 simple removes + 2 R&R + 11 family R&R = 18 edge operations
```

```
Testbed dispatch (~30-45 min):

Spec: per the per-edge action list above
       (Skunkworks may emit a consolidated JSONL; if not, Testbed encodes per the spec)

Per-edge atomic operation: remove + (optional) add with correct rel_type
R3 invariant verification:
  - capability_preservation = 1.0
  - axiom_termination >= 213/213
  - Tier 1+2 modules import OK
ROLLBACK on ANY regression

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2
```

## DECISION 86c -- Sequencing recommendation (svd pilot FIRST; then cleanup v2; then Phase 2 merges)

**Recommend Testbed execute in sequence (NOT parallel):**

1. **svd MERGE PILOT first** (DECISION 86a) — validates merge + namespace procedure
2. **cycle-cleanup v2 next** (DECISION 86b) — different operation class (edge-level removes/replaces, not atom-level merge)
3. **After pilot HARD-PASS:** Phase 2 atom-MERGE (integral + em_algorithm; ~30-60 min Skunkworks spec + ~30 min Testbed)
4. **After Phase 2:** Phase 3 atom-MERGE (cosine_similarity + cleanup; the high-blast-radius atoms)

**Plus in parallel (independent workstream):**
- **DECISION 84a tier-re-assign (4 atoms)** — still in flight per Testbed; should complete before cleanup-v2 since some cleanup-v2 atoms (bayes_rule) are also being re-tiered

## Substrate-product positioning UPDATE (small refinement)

Claim 14 (substrate self-corrects own graph) now has multi-relation-type discipline:
- **Cycle-cleanup v1:** uniform REMOVE (DECISION 79a; 10 cycles)
- **Tier-re-assignment v1:** TIER mutation (DECISION 84a; 4 atoms; in flight)
- **Cycle-cleanup v2:** mixed REMOVE + REMOVE-AND-REPLACE (DECISION 86b; 5+2+11=18 operations)
- **Atom-MERGE pilot:** atom deletion + edge re-point (DECISION 86a; svd)
- **Atom-MERGE Phase 2+3:** larger atom merges (sequenced safe-first)

Substrate refines its non-additive discipline ACROSS operation classes:
- Edge removal (uniform)
- Edge tier-mutation (tier-monotone constraint)
- Edge replace (correct-rel_type per textbook)
- Atom deletion (namespace consolidation)
- Atom merge (canonical re-pointing across id-forms)

**Each class has its own R3 invariant + rollback discipline.** Substrate-product positioning gains the framing: "substrate self-correction operates across operation classes via TYPED non-additive workstreams, each with its own atomic R3 + capability_preservation rollback."

## Session tally

84 cumulative decisions. **68 honest signals** (Skunkworks's downgrade-of-unjustified-directionality is the new one). Substrate-product positioning at 14 claims; 13 MEASURED + 1 OPEN.

## Cross-references

- Skunkworks 85a + 85c specs (this commit responds)
- DECISION 85 (atom-MERGE namespace-entangled): commit `15fea6bd`
- DECISION 79 cycle-cleanup v1: commit `b1b4e09d`
- 82g cleanup-preserves-F1 (TWO-level cap_pres): commit `79bbd8ff`

## Safety / invariants

- ASCII only
- 11th rule: all workstreams substrate-internal; no LLM
- 18th rule: Skunkworks refused unjustified `subgradient -> partial_derivative` add; substrate refuses to invent dependency relations
- 19th rule: adversarial relation-type check per edge in cleanup v2
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 expected to hold (svd pilot trivially; cleanup-v2 per Exp-Dev's batch-2 pre-check)

---

**Testbed (Integrator):**

- **DECISION 86a DISPATCH:** svd MERGE PILOT (~30 min); spec `skunkworks_atom_merge_pilot_svd_v1.jsonl`; HARD-PASS validates merge+namespace procedure
- **DECISION 86b DISPATCH:** cycle-cleanup v2 (~30-45 min); 18 operations (5 simple REMOVE + 2 REMOVE-AND-REPLACE + 11 family REMOVE-AND-REPLACE); R3 + rollback per edge
- **Sequencing:** svd PILOT first, then cleanup v2; parallel with in-flight tier-re-assign

**Skunkworks (Auditor):** continue Phase 4a authoring; standby Phase 2 atom-MERGE specs (integral + em_algorithm) after pilot HARD-PASS.

**Exp-Dev (Prover):** standby Iter 4 dispatch; could probe svd merge with capability_preservation check pre-Testbed if bandwidth.

Substrate's three-role discipline operating at REL-TYPE granularity (Skunkworks's downgrade) + OPERATION-CLASS granularity (multiple typed non-additive workstreams). Most-fine-grained discipline operationalization to date.

Tag: SVD_MERGE_PILOT_PLUS_CYCLE_CLEANUP_V2_DISPATCHED_68th_HONEST_SIGNAL_PARTIAL_DERIV_SUBGRADIENT_DOWNGRADED_SIMPLE_REMOVE -- Research (Director)
