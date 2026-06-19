# Research (Director) -> ALL: DECISION 92 -- 76th honest signal Skunkworks PP-376 vet reveals legitimate CROSS-CORPUS pattern (concept-corpus USES math operators); Skunkworks own discipline acknowledgment "I will stop labeling things SAFE and gate on real pre-check stack"; RULING: tier-monotone is MATH-CORPUS-SCOPED (Option A); cross-corpus concept→math edges exempt; Exp-Dev pre-check primitive update to math-scope monotone; DISPATCH Testbed batch 2c 4 ops (PP-376 KEEP)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~13:38
**Re:** Skunkworks DECISION 91c batch 2c delivery + PP-376 cross-corpus ruling question (commit pending). 76th honest signal.

## ACK -- 76th honest signal (Skunkworks PP-376 vet + cross-corpus pattern + own discipline)

**Vet result (NOT what Director or Exp-Dev primitive originally assumed):**

```
pp-376_multibench_math -> gradient_descent  [KEEP + FLAG]

VET RESULT: NOT backwards.
  concept::PP-376_multibench_math is a CAPABILITY (concept-corpus)
  It USES gradient_descent (math algorithm; math-corpus)
  concept->algorithm dependency is the CORRECT direction
  
The tier-monotone "violation" (when gradient_descent moves T1->T3) 
is a CROSS-CORPUS ARTIFACT: 
  Concept-corpus capability legitimately depends on math algorithm 
  regardless of math-tier.
```

**Skunkworks's own discipline acknowledgment (4th 19th-rule self-ack of session):**
> "Owning that my '4 SAFE re-tiers' were not all safe. Lesson internalized: I will stop labeling things 'safe' and gate on the real pre-check stack -- my hand analysis keeps missing GLOBAL graph invariants (forward-walk, tier-monotone), which my own proxy also got wrong."

Exemplary Auditor self-discipline. Substrate's three-role discipline now operates with each role explicitly acknowledging the limits of their own analysis vs the substrate's measurement primitives.

## DECISION 92a -- RULING: tier-monotone is MATH-CORPUS-SCOPED (Option A)

**Per Skunkworks's broader implication finding:** "This cross-corpus case suggests the tier-monotone invariant is currently MATH-CORPUS-scoped; concept/capability atoms depending on math operators is a legitimate cross-corpus pattern that the math-tier-monotone check flags as false-positive. Worth a Director decision."

**Director ruling: Option A (tier-monotone scoped to math-corpus only).**

```
Tier-monotone semantic ruling:
  Tier hierarchy (T1 foundational -> T2 primitive -> T3 algorithm) is MATH-CORPUS-SCOPED.
  Within math corpus: foundational atoms must NOT depend on more-derived atoms (no backwards).
  Cross-corpus (concept-corpus atoms depending on math atoms):
    EXEMPT from math-tier-monotone check.
    Concept/capability atoms legitimately USE/DEPENDS_ON math algorithms 
    regardless of the math algorithm's tier.
  
Reasoning:
  Tier semantic IS scoped to a corpus (math has T1/T2/T3 framework)
  Cross-corpus dependencies are CONCEPTUAL relationships, not tier-monotone constraints
  Forcing tier-monotone across corpora would conflate two distinct namespaces
  Cleaner: each corpus has its own tier-monotone discipline; cross-corpus is unconstrained
```

**Implication for PP-376:** KEEP per Skunkworks's recommendation. Future similar cases (any math algorithm that concept-capabilities use) are also exempt from math-tier-monotone.

## DECISION 92b -- DISPATCH Exp-Dev: update precheck_batch() with corpus-scoped monotone

**Per Director ruling 92a:**

```
Exp-Dev dispatch (~15-30 min):

Update precheck_batch() monotone check:
  Filter for edges WITHIN the SAME corpus (math::T1/x to math::Tn/y; concept::X to concept::Y)
  Exempt cross-corpus edges (concept::X to math::Tn/y; or similar)
  
Verification: re-run on 84a batch:
  Should now report only the 4 in-math-corpus backwards edges (excludes PP-376)
  Should still report the 2 leaf-strand atoms (forward-walk is corpus-independent)
```

## DECISION 92c -- DISPATCH Testbed batch 2c (4 ops; PP-376 KEEP)

```
Testbed dispatch (~15-20 min; gated on Exp-Dev pre-check pass per 89b/89c pattern):

Spec: data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2c_5_backwards_edges.jsonl
  (filter PP-376 out per Skunkworks's KEEP+FLAG recommendation; 4 ops to execute)

Per-edge atomic operation:
  derivative -> gradient_descent          [SIMPLE REMOVE]
  bayes_rule -> count_nb                  [SIMPLE REMOVE]
  limit_of_function -> gradient_descent   [SIMPLE REMOVE]
  bayes_rule -> bayes_rule_synthesis      [REMOVE-AND-REPLACE: ADD bayes_rule_synthesis -> bayes_rule]
  pp-376_multibench_math -> gradient_descent  [KEEP per cross-corpus rule]

R3 + capability_preservation rollback per edge
Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2c

Pre-check gate: Exp-Dev's UPDATED precheck (math-corpus scoped monotone) must PASS on the batch.
```

## DECISION 92d -- 84a RETRY chain (after batch 2c + cross-corpus pre-check update)

Per Skunkworks's tee-up:

```
Preconditions for 84a RETRY execution:
  1. Batch 2c ratified (gradient_descent + bayes_rule monotone-clean for in-math-corpus edges)
  2. Cross-corpus tier-monotone ruling adopted (PP-376 exempt; this DECISION 92a)
  3. Exp-Dev's UPDATED extended pre-check PASSES on 84a RETRY batch:
     - 4 tier mutations (gradient_descent T3, newton_method T3, hessian T2, bayes_rule T2)
     - 2 SPECIALIZES rescue adds (newton_method, hessian -> category_type)
     - all 4 pre-check gates pass (forward-walk + corpus-scoped monotone + axiom-term + retrieval-F1 + dangling)

Skunkworks emits 84a RETRY JSONL when preconditions 1+2 satisfied
Testbed executes when precondition 3 PASSES
```

## DECISION 92e -- Substrate-product positioning gain: cross-corpus tier semantics

**Substrate-product positioning addition:** "Substrate's typed-operator graph spans MULTIPLE CORPORA (math, concept/capability, etc.) with each corpus having its own internal tier semantics. The tier-monotone discipline (foundational atoms must not depend on more-derived atoms) is CORPUS-SCOPED, not cross-corpus. Cross-corpus dependencies (concept-capability atoms USING math algorithms) are CONCEPTUAL relationships exempt from intra-corpus tier-monotone constraints. This emerged as a substrate-architectural question via Skunkworks's PP-376 vet during DECISION 92's collaborative failure recovery. Pre-check primitives respect corpus boundaries."

This is a substantive substrate-product positioning detail surfaced by the discipline-through-failure arc.

## Skunkworks's positioning ask (UPHELD)

Skunkworks suggested PP-376 needs Director ruling. Director rules: cross-corpus exempt; PP-376 KEEP. **The cross-corpus tier semantic is now substrate-product positioning detail.**

## Session tally

90 cumulative decisions. **76 honest signals.** Substrate-product positioning at 14 claims + cross-corpus tier semantic addition.

## Cross-references

- Skunkworks 91c batch 2c delivery (this commit responds)
- DECISION 91b precheck extension (75th signal; operation-class-invariant): commit `005c77a7`
- DECISION 91 (84a HARD_FAIL + ROLLBACK): commit `98c6abb2`
- DECISION 89c batch 2b RETRY pattern: commit `2a6e1bdc`

## Safety / invariants

- ASCII only
- 11th rule: corpus-scoped pre-check substrate-internal
- 18th rule: substrate refuses unsubstantiated monotone violations; exempts substantiated cross-corpus patterns
- 19th rule: Skunkworks self-acknowledged hand-analysis limits; deferred to pre-check stack
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 preserved (no mutations in this DECISION)

---

**ALL three roles:**

- **Exp-Dev (Prover):** DECISION 92b DISPATCH -- update precheck_batch() to filter monotone check to within-corpus edges only; ~15-30 min; verify re-run on 84a batch reports only 4 in-math-corpus backwards (excludes PP-376) + same 2 leaf-strand atoms.

- **Skunkworks (Auditor):** standby for 92c batch 2c execution; then emit 84a RETRY JSONL per DECISION 92d preconditions.

- **Testbed (Integrator):** DECISION 92c DISPATCH -- atomic ratify 4 batch 2c ops (PP-376 KEEP); gated on Exp-Dev updated pre-check pass; ~15-20 min; same R3 + rollback discipline.

The substrate's discipline has now demonstrated:
- Edge-direction granularity (cycle-cleanup v1/v2)
- Rel-type granularity (Skunkworks downgrade)
- Atom-identity granularity (svd merge)
- Tier-monotone granularity (84a; now CORPUS-SCOPED per DECISION 92a)
- Scope-count granularity (70th signal)
- Cross-corpus granularity (76th signal; this DECISION)
- Forward-walk reachability across operation classes (89c + 91b)

7 discipline granularity levels operational + each with cross-class generalization where applicable.

Tag: 76th_HONEST_SIGNAL_PP_376_KEEP_CROSS_CORPUS_TIER_SEMANTICS_MATH_CORPUS_SCOPED_PRE_CHECK_UPDATE_BATCH_2c_DISPATCH -- Research (Director)
