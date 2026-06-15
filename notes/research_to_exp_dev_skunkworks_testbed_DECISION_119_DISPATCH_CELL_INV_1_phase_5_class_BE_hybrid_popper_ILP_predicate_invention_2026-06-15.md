# Research (Director) -> Exp-Dev + Skunkworks + Testbed: DECISION 119 -- USER AUTHORIZED CELL-CONCEPT-INVENTION-INV-1; first Phase 5 frontier test; Drill B Class B (Popper-style ILP predicate invention) + Class E (CELOE refinement) hybrid over 20 linear-algebra operator atoms; substrate validates via 4-gate pre-check + L6-PROOF; tests Claim 5b OPEN (autonomous discovery of structurally-new concepts); USER DECISION 68 strategic direction empirically tested; parallel with Phase 3 (independent workstream); Phase 4e Author-N hold UNAFFECTED (this is concept-invention not signature authoring)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~17:55
**Re:** USER authorization "do it" on DECISION 111b CELL-INV-1 dispatch (Phase 5 exploratory test).

## USER AUTHORIZATION

USER ruled "do it" on Phase 5 CELL-INV-1 dispatch. The substrate frontier per Drill B + the natural follow-through on USER's DECISION 68 strategic direction ("steer math basis toward enabling characteristics so substrate can TRULY support its own growth").

## DECISION 119a -- DISPATCH Exp-Dev: CELL-CONCEPT-INVENTION-INV-1

**Goal:** test whether substrate can host Class B + Class E hybrid concept-invention with sound-by-construction validation. Single decisive cell; ~1 CPU-hr.

### Cell design

```
CELL: experiments/exp_substrate_concept_invention_INV_1_popper_predicate_invention_linear_algebra_cpu_v1.py

INPUTS:
  1. 20 substrate operator atoms in math::T1/T2 linear-algebra group:
     T1 candidates: vector_space, inner_product, matrix, determinant, trace, 
                    transpose, eigenvalue_eigenvector, gradient, hessian, rank
     T2/T3 candidates: matrix_multiplication, matrix_addition, scalar_multiplication, 
                       dot_product, cross_product, outer_product, kronecker_product, 
                       svd, qr_decomposition, lu_decomposition
     Final selection: Exp-Dev confirms availability + tier-correctness from current substrate
  
  2. 10 positive + 10 negative compositional examples:
     Positives from PROVED edges (passing 4-gate); textbook-sound compositional relations
     Negatives from UNDECIDABLE class or randomly-permuted (not textbook-sound)

MECHANISM (Class B Popper-style ILP predicate invention):
  Higher-order metarules parameterize hypothesis space over predicate variables
  When no existing predicate satisfies a metarule slot, system invents a fresh 
  predicate symbol bound to discovered sub-program
  
  Popper "learning from failures" loop:
    1. Propose candidate predicate definition (compositional pattern; 2+ existing primitives)
    2. Test against positive examples (must entail)
    3. Test against negative examples (must NOT entail)
    4. If passes both: candidate invented predicate
    5. If fails: refine hypothesis space (eliminate or restrict scope)

VALIDATION (substrate sound-by-construction; 4-gate pre-check stack):
  Per candidate invented predicate:
    a. Materialize as candidate atom + proposed signature
    b. Run 4-gate pre-check:
       - Forward-walk reachability (must reach T1 axioms)
       - Corpus-scoped tier-monotone
       - Axiom termination (L6-PROOF backward-chain derivable)
       - Dangling all-rel-type hardened
    c. Verify capability_preservation = 1.0 maintained
    d. Route to Skunkworks for adversarial vet (STRICT/PLAUSIBLE/REJECT)

CONSTRAINTS (11th + 22nd rules):
  - NO LLM contact during invention loop (substrate-internal Popper logic)
  - NO held-out gold contact (q54-q65; 56d SHA 22d7eb01; 56d-v2 untouched)
  - ASCII only
```

### HARD-PASS criteria (per Drill B)

- >=3 invented predicates verify under 4-gate WITHOUT cap_pres regression
- Each verified predicate has provenance (derivation chain from example set)
- Each verified predicate is textbook-sound per Skunkworks vet (STRICT)

### HARD-FAIL criteria

- 0 invented predicates verify under 4-gate
- ANY single invented predicate fails capability_preservation (substrate refuses by 7th rule)
- Popper loop fails to converge in 1 CPU-hr (engineering bound)

### Substrate-product positioning at stake

```
HARD-PASS:
  Claim 5b graduates CANDIDATE -> MEASURED on Class B/E hybrid path
  Substrate gains FIRST 3-of-3 architecture empirical validation:
    - novel-primitive-introduction (Popper invents predicate symbols)
    - strict-consistency (4-gate validation refuses unsound)
    - provenance (each invention carries derivation chain)
  Program's strongest single result.

HARD-FAIL:
  Claim 5b stays OPEN with REFINED boundary characterization
  (e.g. "Popper ILP requires richer metarule set than current substrate hosts"
        or "L6-PROOF kernel rejects compositional predicates without further work")
  Substrate-product positioning gains precise Phase 5 scope refinement.

EITHER WAY: substrate-product positioning advances; the test is decisive.
```

### Cost + timing

- Exp-Dev engineering: ~30-45 min cell build + harness
- Popper loop runtime: ~1 CPU-hr (per Drill B estimate)
- Skunkworks vet per candidate: ~5-10 min each
- Testbed ratify (if HARD-PASS): ~15-30 min

Total: ~2-3 hrs HARD-PASS; ~1.5 hrs HARD-FAIL.

## DECISION 119b -- Parallel + holds UNAFFECTED

```
This dispatch operates IN PARALLEL with:
  - Testbed Phase 3 ratifies (Sub-batch 2 + Sub-batch 3 in flight)
  - Skunkworks Phase 4e Author-N voluntary hold (signature-quality workstream)
  
Does NOT affect:
  - Phase 4e signature authoring (concept-invention != signature authoring)
  - Phase 3 atom-MERGE workstreams (independent code path)
  - 4-gate pre-check stack (used but not modified)

Respects:
  - 11th rule (substrate-internal; no LLM in invention loop)
  - 18th rule (refuse what cannot be proven; 4-gate gates each invented predicate)
  - 22nd rule (no held-out gold contact)
  - Methodology rules FROZEN at 24
```

## DECISION 119c -- Skunkworks (adversarial vet standing)

**Skunkworks:** standing for adversarial vet of each candidate invented predicate that Exp-Dev's 4-gate passes. Pattern: STRICT (textbook-sound + relation-direction-correct) / PLAUSIBLE (textbook-sound but uncertain) / REJECT (semantically wrong).

Vet is BLIND to Exp-Dev's pre-check verdict (per 110a discipline; composes with Drill A finding). Vet from textbook semantics + atom structure alone.

## DECISION 119d -- Testbed (standby ratify)

**Testbed:** standby for ratify of HARD-PASS invented predicates (passing BOTH 4-gate + Skunkworks STRICT vet). Standard atomic-ratify + R3 verify + rollback discipline.

If 0 invented predicates pass: no ratify event; substrate refuses to mutate; HARD-FAIL.

## DECISION 119e -- USER DECISION 68 strategic context

```
USER directive (~09:00) "Math is the BASIS, not the end. Steer math basis toward 
substrate's own more fully-fledged ENABLING characteristics so it can TRULY 
support its own growth."

Empirical chain:
  Phase 3 retrieval EXHAUSTED (M4d in-distribution amplifier)
  Phase 4 self-model + member-growth operational (Claim 5a MEASURED via blind-audit)
  Phase 5 frontier scoped (Class B+E hybrid; substrate has VALIDATOR; needs candidate-GENERATOR)
  THIS dispatch: first empirical test of Class B candidate-GENERATOR over substrate VALIDATOR

~9 hours from USER strategic direction (~09:00) to first frontier test (~18:00+).
```

## Session tally

119 cumulative decisions. **101 honest signals.** Substrate-product positioning at 16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN. Audit-discipline at 18 instance types empirically MEASURED. Phase 5 frontier test in flight.

## Cross-references

- Drill B literature scan: `notes/research_concept_invention_mechanism_classes_2026-06-15.md`
- DECISION 111 positioning enhancement: commit `a0e2ed92`
- DECISION 118 3-quality-layers: commit `160f21ef`
- DECISION 68 originating USER strategic direction: commit `27b5ccd3`

## Safety / invariants

- ASCII only
- 11th rule: invention loop substrate-internal (Popper logic; no LLM)
- 18th rule: 4-gate refuses unsound inventions
- 19th rule: Skunkworks adversarial vet blind to Exp-Dev verdict (Drill A discipline composes)
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 expected to PRESERVE 
  (each candidate gated on 4-gate + cap_pres; substrate refuses if fails)

---

**Exp-Dev (Prover):** DECISION 119a DISPATCH -- build CELL-CONCEPT-INVENTION-INV-1 cell; select 20 linear-algebra operator atoms + 10 pos/10 neg compositional examples from PROVED edges; run Popper-style predicate invention loop; per candidate run 4-gate + cap_pres; route candidates to Skunkworks. ~1 CPU-hr. Report HARD-PASS (>=3 verified) / HARD-FAIL / engineering issues.

**Skunkworks (Auditor):** DECISION 119c standing vet -- adversarial textbook-grounded vet of each candidate Exp-Dev routes; STRICT/PLAUSIBLE/REJECT; BLIND to Exp-Dev's pre-check verdict per Drill A discipline.

**Testbed (Integrator):** DECISION 119d standby ratify -- atomic ratify of HARD-PASS predicates (passing both 4-gate + Skunkworks STRICT vet); standard R3 + rollback discipline.

**Sub-batch 2 + 3 ratifies continue uninterrupted in parallel.**

USER's DECISION 68 strategic direction empirically tested at substrate frontier. Either outcome strengthens substrate-product positioning: HARD-PASS demonstrates FIRST 3-of-3 architecture; HARD-FAIL refines Claim 5b scope precisely.

Tag: 119_DISPATCH_CELL_INV_1_PHASE_5_CLASS_BE_HYBRID_POPPER_ILP_PREDICATE_INVENTION_CLAIM_5B_FRONTIER_USER_DECISION_68_EMPIRICAL_TEST -- Research (Director)
