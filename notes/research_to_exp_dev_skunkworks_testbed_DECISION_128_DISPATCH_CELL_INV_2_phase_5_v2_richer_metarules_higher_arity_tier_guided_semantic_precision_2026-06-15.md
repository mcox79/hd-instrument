# Research (Director) -> Exp-Dev + Skunkworks + Testbed: DECISION 128 -- DISPATCH CELL-INV-2 Phase-5-v2 frontier test with richer Popper metarules (higher-arity 4+ component compositions + cross-relation patterns + tier-gradient-guided novelty) + semantic-label precision discipline (lessons from CELL-INV-1; reject loose-label even when entailment passes); tests Claim 5b OPEN at richer-generator level; USER "keep going" authorization

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~20:45
**Re:** USER "keep going" + DECISION 121e Phase-5-v2 lever (a) richer metarules.

## USER AUTHORIZATION

USER ruled "keep going" -- dispatching forward motion at substrate frontier. Phase-5-v2 is the natural follow-through on CELL-INV-1's GENERATOR-BOUND finding.

## DECISION 128a -- DISPATCH Exp-Dev CELL-CONCEPT-INVENTION-INV-2

**Goal:** test whether richer Popper metarules + semantic-label precision discipline yield genuinely-NOVEL certifiable predicates over the same substrate. Distinct from CELL-INV-1 by:
- Higher-arity compositions (4+ components, not just pair/triple)
- Cross-relation metarules (mix SPECIALIZES + USES + DEPENDS_ON)
- Tier-gradient-guided novelty (prefer compositions spanning tiers)
- Negative-example refinement (adversarial-search not just failure-to-entail)
- Semantic-label precision (loose rediscovery = PLAUSIBLE not STRICT)

### Cell design

```
CELL: experiments/exp_substrate_concept_invention_INV_2_richer_metarules_higher_arity_cpu_v1.py

INPUTS:
  1. 20 substrate operator atoms in math::T1/T2 linear-algebra group
     Same seed set as CELL-INV-1 for comparison (vector_space, inner_product, matrix, etc.)
     PLUS extension atoms for higher-arity coverage: tensor, covariance_matrix, kernel_method,
                                                     reproducing_kernel_hilbert_space, sigma_algebra,
                                                     measure, Lp_space (Exp-Dev selects from substrate)
     
  2. 10 positive + 10 negative compositional examples
     Same drawing pattern as CELL-INV-1 (PROVED edges + adversarial negatives)
     ADD: 5 SEMANTIC-PRECISION-NEGATIVES (loose-label cases like CELL-INV-1's pca_whitening 
                                          where component-set is approximate; reject these as 
                                          NEGATIVE not positive)

MECHANISM (richer Popper):
  Higher-arity metarules:
    M1: P[a + b] -> X (CELL-INV-1 baseline)
    M2: P[a + b + c] -> X (CELL-INV-1 baseline)
    M3: P[a + b + c + d] -> X (NEW; higher-arity)
    M4: P[a + b + c + d + e] -> X (NEW; higher-arity)
    
  Cross-relation metarules:
    M5: P[a USES b + b SPECIALIZES c] -> X (combine relation types)
    M6: P[a DEPENDS_ON b + b SHARES_MATH c] -> X
    
  Tier-gradient-guided:
    Prefer compositions spanning tiers (T1 + T2 + T3 mix vs single-tier)
    
  Negative-example refinement (adversarial):
    For each candidate predicate, search substrate for COUNTER-EXAMPLE atom that
    entails the predicate's components but textbook-contradicts the claimed concept
    (per 123 banach_space pattern; reject if candidate matches mis-authored atom)

VALIDATION (substrate sound-by-construction; same 4-gate stack):
  Per candidate invented predicate:
    a. Materialize as candidate atom + proposed signature
    b. Run 4-gate pre-check (forward-walk + tier-monotone + axiom-term + dangling)
    c. Verify capability_preservation = 1.0
    d. Route to Skunkworks for SEMANTIC-PRECISION-LEVEL vet (STRICT requires both 
       formal entailment AND tight semantic-label binding; loose = PLAUSIBLE)

CONSTRAINTS (11th + 22nd rules):
  - NO LLM contact during invention loop (substrate-internal richer Popper)
  - NO held-out gold contact
  - ASCII only
```

### HARD-PASS criteria (refined from CELL-INV-1)

- >=1 GENUINELY NOVEL predicate verifies under 4-gate
- Each verified novel predicate has TIGHT semantic-label binding (per Skunkworks STRICT criteria)
- 4-gate pass + cap_pres preserved + Skunkworks STRICT-vet PASS

### HARD-FAIL criteria

- 0 novel verifies (Claim 5b stays OPEN; refines further)
- Any single fails capability_preservation
- Popper non-convergence in 2 CPU-hr

### Substrate-product positioning at stake

```
HARD-PASS:
  Claim 5b graduates CANDIDATE -> MEASURED via richer-generator path
  FIRST 3-of-3 architecture empirically validated
  Substrate becomes the first published autonomous KG system to deliver 
  novel-primitive + strict-consistency + provenance
  Program's strongest single result

HARD-FAIL:
  Claim 5b stays OPEN with EVEN-MORE-PRECISE boundary
  Substrate's generator-gap proves harder than richer-metarules alone solves
  Phase-5-v3 path may require Lever (b) external truth source
  Substrate-product positioning gains precision either way
```

### Cost + timing

- Exp-Dev engineering: ~2-4 hrs cell build (higher-arity + cross-relation + adversarial-negatives)
- Popper loop runtime: ~1-2 CPU-hr (richer hypothesis space)
- Skunkworks vet per candidate: ~10-15 min (semantic-precision rubric)
- Testbed ratify (if HARD-PASS): ~15-30 min

Total: ~3-6 hrs end-to-end HARD-PASS; ~2-4 hrs HARD-FAIL.

## DECISION 128b -- Skunkworks vet rubric REFINED for CELL-INV-2

Per 119c rubric + 123 banach_space lesson + 121 generator-gap finding:

```
STRICT (richer-generator):
  (a) genuine NOVEL composition with TIGHT semantic-label binding
      (label matches the composition uniquely; not approximate)
  (b) Sound derivation chain from existing primitives
  (c) Entails positives + excludes negatives + excludes adversarial-counter-examples
  (d) Semantically meaningful (not formally-pass-semantically-vacuous)
  (e) Not rediscovery (component-set must not match existing atom under different label)

PLAUSIBLE:
  Coherent composition + sound derivation, but semantic-label binding loose 
  (multiple candidate names; or approximate match to existing concept)

REJECT:
  Any of: vacuous + circular + wrong-direction + entails-negative + trivial-fan-out 
  + label-mismatch + loose-rediscovery
  
NEW from CELL-INV-1 lessons:
  Loose-label rediscovery = REJECT (was PLAUSIBLE in 119c; now stricter)
  Wrong-component-set rediscovery = REJECT + flag mis-authored atom
```

## DECISION 128c -- Parallel + Phase 4e Author-N continues

```
This dispatch operates IN PARALLEL with:
  - Skunkworks's standing Phase 4e Author-N batches at bandwidth
  - mp_bulk_kl tier-duplicate hygiene (Skunkworks own queue)
  - Class C em-dash bulk cleanup (Skunkworks own queue)
  
No conflict (concept-invention != signature authoring).
```

## Session tally

128 cumulative decisions. **117 honest signals.** Substrate-product positioning at 16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN. Audit-discipline at 28 instance types empirically MEASURED. Phase-5-v2 frontier test in flight.

## Cross-references

- DECISION 121 CELL-INV-1 PARTIAL (precedent): commit `6e7ee313`
- DECISION 123 banach_space mis-authoring catch (semantic-precision lesson): commit `da9abcd4`
- DECISION 119c Skunkworks rubric (refined here for INV-2): prior commit
- DECISION 121e Phase-5-v2 lever (a) richer metarules: same as 121
- USER "keep going" authorization: this conversation

## Safety / invariants

- ASCII only
- 11th rule: invention loop substrate-internal (richer Popper; no LLM)
- 18th rule: 4-gate refuses + Skunkworks semantic-precision rubric refuses loose-labels
- 19th rule: 28 instance types empirical; semantic-precision rubric adds another layer
- 22nd rule preserved (no held-out gold contact per cell design)
- 100pct axiom termination + capability_preservation=1.0 expected to PRESERVE

---

**Exp-Dev (Prover):** DECISION 128a DISPATCH -- build CELL-CONCEPT-INVENTION-INV-2 at experiments/exp_substrate_concept_invention_INV_2_*.py; richer metarules (higher-arity + cross-relation + tier-guided) + adversarial-negatives + semantic-precision discipline; ~2-4 hrs engineering + 1-2 CPU-hr run.

**Skunkworks (Auditor):** DECISION 128b standing vet -- refined SEMANTIC-PRECISION rubric for each candidate; STRICT requires both formal entailment AND tight label binding; BLIND to Exp-Dev's pre-check verdict (Drill A discipline). Continue parallel Phase 4e + hygiene workstreams independent.

**Testbed (Integrator):** DECISION 128 -- standby ratify HARD-PASS predicates (passing both 4-gate + Skunkworks STRICT vet).

Tag: 128_DISPATCH_CELL_INV_2_PHASE_5_V2_RICHER_METARULES_HIGHER_ARITY_CROSS_RELATION_TIER_GUIDED_SEMANTIC_PRECISION_USER_KEEP_GOING -- Research (Director)
