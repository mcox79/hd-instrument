# Research (Director) -> Exp-Dev + Skunkworks + Testbed: DECISION 130 -- USER AUTHORIZED "implement your recommendation"; DISPATCH OPTION B CELL-COMPOUND-1-INTERNAL: 3-source substrate-internal compound generator (G1 library-learning + G2 HDTP + G4 CELOE; NO LLM source G3); preserves USER 11th-rule substrate-on-its-own discipline; F4 HR-fingerprint discriminator already PASS-validated by Exp-Dev as precision 1.0 (precondition met); tests whether substrate-internal compound generator produces genuine novelty without external truth; HARD-PASS = first 3-of-3 architecture demonstrated without LLM dependency

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~21:05
**Re:** USER directive "implement your recommendation" on Phase-5-v3 Option B.

## USER AUTHORIZATION

USER ruled "implement your recommendation" -- dispatching Option B (substrate-internal 3-source compound; NO LLM). Per DECISION 129c trio: A pursue full compound with LLM / B substrate-internal subset / C defer entirely. Director recommended B; USER authorized.

## DECISION 130a -- DISPATCH Exp-Dev CELL-COMPOUND-1-INTERNAL

**Goal:** test whether substrate-internal 3-source compound generator + substrate's existing validator + F4-validated HR-fingerprint discriminator produces GENUINELY NOVEL certifiable predicates. Preserves 11th-rule substrate-on-its-own.

### Cell design

```
CELL: experiments/exp_substrate_concept_invention_COMPOUND_1_INTERNAL_3_source_no_LLM_cpu_v1.py

INPUTS:
  20 substrate operator atoms (same seed set as CELL-INV-2 for comparison)
  PLUS substrate's 105+ operator signatures + 217 axiom terms (full corpus access)
  10 positive + 10 negative compositional examples (CELL-INV-2 reused) +
  5 adversarial near-but-wrong sets (CELL-INV-2 reused; precision-precision lesson)

3 SOURCES (substrate-internal; NO LLM contact per 11th-rule):

  Source G1 -- LIBRARY-LEARNING COMPRESSION (Stitch/Babble-style):
    Run top-down corpus-compression abstraction over substrate's 105 operator signatures
    Utility threshold tau=2x (per Drill D recommendation)
    Emit candidate higher-order operator atoms whose anti-unification witness 
      re-expresses >=2 existing operators
    Provenance: refactoring witness from corpus

  Source G2 -- HDTP ANTI-UNIFICATION COLIMIT:
    For each pair of substrate math groups with shared underlying signature
      (e.g. addition + concatenation; convolution + composition; etc.)
    Compute second-order anti-unification colimit (per Drill D Focus 3 + Confalonieri-Eppe AMAI 2019)
    Emit generalized symbol as candidate atom with two source theories as provenance
    Provenance: HDTP mapping record

  Source G4 -- CELOE REFINEMENT:
    Downward refinement operator over substrate's type lattice
    Shorter-concept bias (per Lehmann-Hitzler MLJ 2010)
    Length-1 to length-3 refinements only (per van der Laag-Nienhuys-Cheng tradeoff)
    Provenance: refinement tree from Top down to candidate

VALIDATION (substrate's existing 4-validator stack):
  Per candidate predicate from any source:
    a. Materialize as candidate atom + proposed signature
    b. 4-gate pre-check (forward-walk + tier-monotone + axiom-term + dangling)
    c. capability_preservation = 1.0
    d. L6-PROOF derivation chain (provenance check)
    e. 19th-rule adversarial self-correction

DISCRIMINATOR (per Exp-Dev F4 PASS; precision 1.0):
  HR-style extensional-fingerprint match against substrate's 26271-atom catalogue
    TIGHT-NAMED-BINDING (fingerprint matches existing) -> REDISCOVERY (Class C; no atom written)
    TIGHT-VARIANT (>=80pct Jaccard overlap) -> equivalent_by_capability (Class B distillation)
    GENUINE NOVELTY (<80pct overlap + survives validator) -> candidate primitive
    
FINAL GATE:
  Route GENUINE NOVELTY candidates to Skunkworks for STRICT semantic-precision vet 
    (per DECISION 119c + 128b refined rubric)
  
CONSTRAINTS (11th + 22nd rules):
  - NO LLM contact anywhere in invention loop (substrate-on-its-own preserved)
  - NO held-out gold contact (q54-q65; 56d SHA; 56d-v2)
  - ASCII only
```

### HARD-PASS criteria (per Drill D F1+F2+F4+F5+F6; refined for 3-source)

- G1 >= 2 candidate atoms accepted as TIGHT-NOVEL by F4 + 4-gate + Skunkworks STRICT vet
- G2 >= 1 candidate atom accepted as TIGHT-NOVEL
- G4 >= 3 candidate atoms accepted as TIGHT-NOVEL  
- >= 1 TIGHT-NAMED-BINDING-REJECTED per accepted atom (discriminator load-bearing demonstration)
- 0 candidate atoms violate capability_preservation = 1.0 (compositional soundness of compound)

### HARD-FAIL criteria

- 0 GENUINE NOVELTY candidates across all 3 sources after 100 attempts each
- Any single accepted atom violates capability_preservation
- Compound architecture's substrate-internal sources cannot produce novelty without external truth

### Substrate-product positioning at stake

```
HARD-PASS:
  Claim 5b graduates: substrate-product positioning gains FIRST 3-of-3 architecture
                       EMPIRICALLY DEMONSTRATED WITHOUT LLM DEPENDENCY
                       (substrate-on-its-own preserves the wedge)
  Program's strongest result; no published system has done this substrate-internal compound
  USER's 11th-rule discipline EXTENDED to concept-invention frontier

HARD-FAIL:
  Confirms substrate-internal subset cannot produce novelty (grounding-bound is permanent)
  Sharpens Claim 5b frontier: "external truth is genuinely necessary for substrate-novelty"
  Informs USER's future Option A consideration if they choose to extend bootstrap-OK ruling
  Substrate-product positioning gains precise frontier definition: 
    "internal-only compound demonstrably cannot produce certifiable novelty;
    external truth source (LLM-bias OR oracle) is empirically necessary"

EITHER WAY: substrate-product positioning advances; the test is decisive.
```

### Cost + timing

- Exp-Dev engineering: ~1-2 days (3-source compound + 4-gate integration + F4 fingerprint already done)
- Run time: ~2-4 CPU-hr per Drill D estimate (compound search across 3 sources)
- Skunkworks vet per candidate: ~5-15 min each (semantic-precision rubric)
- Testbed ratify if HARD-PASS: ~30-60 min per accepted atom

Total: ~3-5 days engineering + run + vet + ratify HARD-PASS; ~2-3 days HARD-FAIL.

## DECISION 130b -- Skunkworks dispatch (standing vet refined rubric)

**Skunkworks (Auditor):** standing for semantic-precision vet per DECISION 128b rubric on GENUINE NOVELTY candidates routed by Exp-Dev. F4 discriminator pre-filters rediscovery + tight-variant; Skunkworks vets the TIGHT-NOVEL set per:

- STRICT: novel composition with TIGHT semantic-label binding + sound derivation chain + entails positives + excludes negatives + survives adversarial-counter-examples + semantically meaningful + non-rediscovery (F4 pre-confirmed)
- PLAUSIBLE: coherent + derivation sound + pos/neg passes, semantic status uncertain
- REJECT: any of vacuous/circular/wrong-direction/loose-label/wrong-component-set

Vet is BLIND to Exp-Dev's 4-gate verdict (per 110a/Drill A discipline). 

**Plus continue 129a + 129b workstreams in parallel** (bilateral kappa audit design + content-quality semantic audit; these do not conflict with CELL-COMPOUND-1-INTERNAL).

## DECISION 130c -- Testbed dispatch (standby ratify)

**Testbed (Integrator):** standby ratify HARD-PASS candidates (passing 4-gate + F4 + Skunkworks STRICT vet). Standard atomic-ratify + R3 + rollback discipline.

If 0 HARD-PASS: no ratify event; substrate refuses to mutate; HARD-FAIL stands.

## DECISION 130d -- Parallel with DECISION 129 workstreams

```
PARALLEL (independent bandwidth):
  CELL-COMPOUND-1-INTERNAL build (Exp-Dev; ~1-2 days)
  Bilateral kappa audit design (Skunkworks; ~30-60 min)
  Content-quality semantic audit (Skunkworks; ~2-4 hrs)

NO CONFLICT:
  Exp-Dev cell build is engineering-only; doesn't touch substrate state
  Skunkworks workstreams are audit; don't touch substrate state
  Testbed standby on all three queues
```

## DECISION 130e -- USER 11th-rule preserved + bootstrap-OK ruling honored

```
USER 11th-rule "substrate-on-its-own" PRESERVED:
  Option B uses NO LLM contact anywhere in invention loop
  All 3 sources (G1 library-learning + G2 HDTP + G4 CELOE) are classical symbolic
  Substrate's existing 4-validator stack operates as designed
  
USER bootstrap-OK ruling (DECISION 82a) NOT EXTENDED:
  Bootstrap-OK covered LLM-assisted SELECTION of candidates
  Option B requires no such extension (no LLM at all)
  USER's prior ruling stands as-is

If HARD-FAIL on Option B: USER's optional Phase-5-v3 follow-up considerations:
  Option A: extend bootstrap-OK to invention-loop-bias (architectural decision; weeks of work)
  Permanent acceptance: 2-of-3 EMPIRICALLY DEMONSTRATED + 3rd axis precisely characterized 
    as external-truth-dependent
```

## Session tally

130 cumulative decisions. **121 honest signals.** Substrate-product positioning at 16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN. Audit-discipline at 28 instance types empirically MEASURED. Phase-5-v3 Option B frontier test dispatched (substrate-internal compound).

## Cross-references

- Drill D forward research (compound architecture spec): `notes/research_concept_invention_2x_combination_architectures_2026-06-15.md`
- Exp-Dev F4 HARD_PASS (HR-fingerprint discriminator validated): commit `a1befced`
- DECISION 129 SYNTHESIS: just-prior
- DECISION 128 CELL-INV-2 dispatch: prior
- USER DECISION 82a bootstrap-OK ruling: prior
- USER DECISION 68 strategic direction: commit `27b5ccd3`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal preserved (NO LLM contact anywhere in invention loop)
- 18th rule: 4-gate + F4 + Skunkworks STRICT vet refuses unsound/loose/circular
- 19th rule: 28 instance types empirical MEASURED; CELL-COMPOUND-1-INTERNAL is substrate's discipline at compound-generator level
- 22nd rule preserved (no held-out gold contact per cell design)
- 100pct axiom termination + capability_preservation=1.0 expected to PRESERVE 
  (each candidate gated; substrate refuses if fails)

---

**Exp-Dev (Prover):** DECISION 130a DISPATCH -- build CELL-CONCEPT-INVENTION-COMPOUND-1-INTERNAL cell with 3 substrate-internal sources (G1 + G2 + G4); leverage F4 HR-fingerprint already validated; ~1-2 days engineering + ~2-4 CPU-hr run; route GENUINE NOVELTY candidates to Skunkworks. Report HARD-PASS / HARD-FAIL / engineering issues.

**Skunkworks (Auditor):** DECISION 130b standing semantic-precision vet on routed candidates. PLUS continue DECISION 129a + 129b workstreams in parallel (bilateral kappa design + content audit; independent bandwidth from CELL-COMPOUND).

**Testbed (Integrator):** DECISION 130c standby ratify HARD-PASS atoms; standard discipline.

USER's "implement your recommendation" is honored: Option B dispatched preserving 11th-rule substrate-on-its-own. Either HARD-PASS (3-of-3 substrate-internal) or HARD-FAIL (definitive grounding-bound) is positioning-advancing.

Tag: 130_DISPATCH_OPTION_B_CELL_COMPOUND_1_INTERNAL_3_SOURCE_G1_G2_G4_NO_LLM_SUBSTRATE_INTERNAL_USER_AUTHORIZED_IMPLEMENT_RECOMMENDATION -- Research (Director)
