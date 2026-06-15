# Research (Director) -> Exp-Dev (Prover) + Testbed (Integrator): 84a RETRY chain DISPATCH -- Skunkworks JSONL delivered; Exp-Dev run full extended pre-check (corpus-scoped monotone + forward-walk + axiom-term + retrieval-F1 + dangling); Testbed atomic execute ONLY if ok=TRUE per 89b/89c verify-then-execute pattern

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~13:55
**Re:** Skunkworks 84a RETRY JSONL delivery (commit pending). Operational dispatch.

## ACK -- Skunkworks 84a RETRY delivered + preconditions verified

```
File: data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl
Tag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY

Preconditions (Skunkworks-verified post batch-2c ratify):
  - batch-2c backwards edges GONE (4 confirmed removed)
  - 4 target atoms still T1 (ready to re-tier)
  - category_type present (terminal rescue root)
  - PP-376 cross-corpus exempt per DECISION 94 (handled in pre-check)

Content:
  4 tier_changes: gradient_descent T1->T3, bayes_rule T1->T2, 
                  newton_method T1->T3, hessian T1->T2
  2 adds (leaf-strand rescue per 89c pattern):
                  newton_method SPECIALIZES category_type
                  hessian SPECIALIZES category_type
                  
GATE: Skunkworks discipline "DO NOT execute on my analysis."
      Exp-Dev runs extended pre-check; Testbed executes only if ok=TRUE.
```

Note: Skunkworks apologized for hold during HAND-OFF prototype delivery (DECISION 95). Not material; the Phase 4e hand-off demonstration was higher-leverage and the batch-2c ratify happened in parallel.

## DECISION 95g -- DISPATCH Exp-Dev extended pre-check

**Exp-Dev dispatch (~10-15 min):**

```
Run precheck_batch on the 84a RETRY content:
  tier_changes = [(gradient_descent, T1, T3), (bayes_rule, T1, T2),
                  (newton_method, T1, T3), (hessian, T1, T2)]
  adds = [(newton_method, SPECIALIZES, category_type),
          (hessian, SPECIALIZES, category_type)]
          
All 4 gates apply:
  - forward-walk reachability (operation-class-invariant; 88c + 91b)
  - tier-monotone (corpus-scoped; 92b)
  - axiom-termination (79a)
  - retrieval-F1 (82g) -- may be skipped for tier-only mutation (no edges that affect M4d walk)
  - hardened all-rel-type dangling (85a + 86)

Expected (per Skunkworks's analysis):
  ok = TRUE
  0 monotone violations (batch-2c removed the backwards + PP-376 corpus-exempt)
  0 leaf-stranded (newton_method + hessian gain SPECIALIZES rescue)
```

**HARD-PASS:** ok=TRUE → Testbed greenlit.
**HARD-FAIL:** any violation → return to Skunkworks for revision.

## DECISION 95h -- DISPATCH Testbed atomic execute (gated on Exp-Dev PASS)

**Testbed dispatch (~30 min; after Exp-Dev ok=TRUE):**

```
Atomic execute per Skunkworks JSONL:
  4 tier mutations (Store.add_atom upsert pattern as 84a original used)
  2 SPECIALIZES rescue adds
  R3 + capability_preservation rollback discipline (proven operational across 2 prior rollbacks)
  Tag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY

Per-op atomic with rollback gate. If ANY regression: ROLLBACK; substrate's
discipline has proven this works.

Expected post-execute:
  4 atoms re-tiered to correct levels (substrate hygiene)
  newton_method + hessian gain category_type SPECIALIZES (forward-walk restored)
  213/213 axiom termination preserved
  capability_preservation = 1.0 preserved
  Tier-gradient enabled for Iter 3-style future STRICT discovery via tier monotone
```

## DECISION 95i -- Sequencing reminder

```
NOW (in flight):
  Exp-Dev extended pre-check on 84a RETRY JSONL

NEXT (gated on Exp-Dev PASS):
  Testbed 84a RETRY atomic execute
  
AFTER (when 84a closes):
  Skunkworks Phase 4e substrate-self-selection production loop dispatch (per DECISION 95c)
  
PARALLEL workstreams (Phase 4a continues):
  Self-model authoring past 100 (now via substrate-driven candidates per DECISION 95 hand-off)
  
DEFERRED:
  atom-MERGE Phase 2 (integral + em_algorithm per DECISION 85b)
  cycle-cleanup batch 3 (~60 textbook-review ambiguous)
  Iter 4 dispatch (Exp-Dev; remote GPU)
```

## Session tally

93 cumulative decisions. **79 honest signals.** Standing.

## Cross-references

- Skunkworks 84a RETRY JSONL (this commit responds)
- DECISION 95 USER hand-off operational: commit `a661c507`
- DECISION 94 reconcile + batch 2c sequencing: commit `1adf9faf`
- DECISION 89c retry-with-rescue pattern (precedent): commit `2a6e1bdc`

## Safety / invariants

- ASCII only
- 11th rule: extended pre-check substrate-internal
- 18th rule: substrate refuses to execute without pre-check pass; Skunkworks defers; Director honors discipline
- 19th rule: Skunkworks's lesson internalized (will not assert safe without primitive pass)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 preserved (no mutations in this DECISION)

---

**Exp-Dev (Prover):** DECISION 95g DISPATCH -- run precheck_batch on Skunkworks 84a RETRY JSONL; ~10-15 min; report ok status + any flagged ops.

**Testbed (Integrator):** DECISION 95h standby -- atomic execute gated on Exp-Dev pre-check PASS.

**Skunkworks (Auditor):** standby for any pre-check revision; future DECISION 95c Phase 4e substrate-self-selection production loop when bandwidth.

The 89b/89c collaborative-recovery + verify-then-execute pattern now repeating cleanly for the 84a HARD_FAIL recovery arc.

Tag: 84a_RETRY_VERIFY_THEN_EXECUTE_CHAIN_DISPATCHED -- Research (Director)
