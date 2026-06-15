# Research (Director) -> Exp-Dev + Skunkworks: DECISION 100 -- PARALLEL DISPATCH: P3 Iter 4 STRICT-discovery on tier-corrected atoms + 5 Phase 4e operators (Exp-Dev; tests Claim 5 OPEN) + P2 atom-MERGE Phase 2 integral/lebesgue_integral + em_algorithm (Skunkworks; cross-validated merge spec)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~14:30
**Re:** USER direct dispatch "do it" on the two next priorities. Round-number DECISION 100.

## DECISION 100a -- P3 Iter 4 DISPATCH (Exp-Dev)

**Test the deepest remaining open empirical question: can the loop produce NEW STRICT edges via W-TYPE-SIG on the newly tier-corrected atoms + Phase 4e signatures?**

### Targets (9 candidate source atoms; freshly enabled for STRICT-discovery)

```
Tier-corrected atoms (DECISION 96; 84a RETRY HARD-PASS):
  gradient_descent T3 (was T1; corrected)
  newton_method    T3 (was T1; corrected)
  hessian          T2 (was T1; corrected)
  bayes_rule       T2 (was T1; corrected)
  
Phase 4e substrate-selected signatures (DECISION 99 ratified):
  expectation_variance  T1 (operator)
  measure_space         T1 (structure)
  banach_space          T1 (structure)
  random_variable       T1 (structure)
  eisner_parsing        T3 (operator)
```

### Mechanism

```
For each target source atom:
  Extract its relational pointers from self-model (derived_from / uses / computes /
  implemented_via / composed_of / computed_via / instance_of / specializes / ...)
  
For each pointer (source, edge_type, target):
  EXISTENCE-CHECK: does this edge already exist in substrate? (per DECISION 78 lesson)
  If YES: skip (already accounted for)
  If NO: candidate for W-TYPE-SIG STRICT-direction ratify
  
TIER-CHECK (per DECISION 96): does the tier-gradient now hold?
  source.tier > target.tier (correct foundational direction) -> STRICT-eligible
  Otherwise: PLAUSIBLE-tier (no tier gradient)

VERIFY-CHECK (per W-TYPE-SIG):
  Skunkworks adversarial vet per edge (STRICT/PLAUSIBLE/REJECT)
  Then Testbed atomic ratify of STRICT-class edges
```

### HARD-PASS criteria

- ≥ 1 GENUINELY NEW STRICT edge identified (post existence-check + tier-gradient verification + Skunkworks vet)
- ≥ 0 monotone violations on the new STRICT edges (per DECISION 96 tier-gradient now correct)
- capability_preservation = 1.0 maintained
- axiom_termination ≥ 217/217 (current baseline)

### HARD-FAIL criteria

- 0 new STRICT edges (Iter 3 saturation continues; substrate's STRICT-discovery does not generalize past initial tier-correction)
- ANY pre-check stack regression

### What this resolves

```
Claim 5 (autonomous generalization = Phase 3) currently OPEN:
  HARD-PASS Iter 4: substrate empirically generalizes (Claim 5 graduates to MEASURED)
                    Substrate-product positioning at 15/15 MEASURED + 0 open = COMPLETE
  HARD-FAIL Iter 4: substrate's autonomous STRICT discovery has additional structural
                    boundaries beyond tier-flatness; surface them for honest scope
```

### Compute path

```
Compute: Iter 3 was laptop-only viable per DECISION 75d (cached cosine over bge embeddings;
         no remote bge required for in-corpus candidates).
         
Iter 4 should be laptop-local if:
  - Targets are existing atoms (yes; 9 known atoms)
  - Candidates are existing atoms (likely; cached embeddings cover 26285 atoms)
  
Laptop-local OR remote-GPU at Exp-Dev's discretion based on the cached vs fresh-encode
question. If remote: needs substrate sync (laptop ahead by recent ratifications).

Cost: ~30-60 min Exp-Dev for the existence-check + vet-prep pass
      + ~15-30 min Skunkworks vet
      + ~15 min Testbed ratify (if HARD-PASS)
```

## DECISION 100b -- P2 Atom-MERGE Phase 2 DISPATCH (Skunkworks)

Per DECISION 85b Phase 2 sequencing (atom-MERGE workstream; pilot validated via svd merge per DECISION 86a):

### Targets

```
integral / lebesgue_integral:
  50 total edges across 2 id-forms
  Lower-stakes pair (Phase 2; second in queue after svd pilot)
  Skunkworks judges canonical (likely lebesgue_integral as fuller textbook name)
  
em_algorithm / expectation_maximization:
  41 total edges across 6 id-forms
  Higher complexity (6 id-forms); excellent stress-test for the merge procedure
  Skunkworks judges canonical (likely expectation_maximization as fuller textbook name)
  
Cross-validated by Phase 4e production scorer (DECISION 97c):
  Both pairs INDEPENDENTLY surfaced as merge candidates by the substrate-self-selection
  scorer (composite signal) AND the dedicated atom-MERGE workstream (textbook-similarity)
```

### Procedure

```
For each merge pair:
  1. Skunkworks chooses canonical atom (fuller textbook name)
  2. Audit all edges incident to either form (across all id-forms; namespace-aware)
  3. Identify which edges to:
     a. KEEP (canonical-direction edges)
     b. RE-POINT (non-canonical edges to repoint to canonical)
     c. DROP (self-loops; duplicates of canonical)
  4. Emit consolidated JSONL with per-edge action
  5. Pre-check via Exp-Dev's extended pre-check stack
  6. Testbed atomic execute + R3 rollback discipline

Pre-check stack gates (all 4 + corpus-scoped):
  - dangling references (all-rel-type hardened)
  - axiom-termination preserved
  - capability_preservation = 1.0
  - forward-walk reachability (operation-class-invariant)
  - corpus-scoped tier-monotone
```

### HARD-PASS

```
For each merge:
  - 0 dangling references post-merge
  - capability_preservation = 1.0
  - axiom_term preserved or improved
  - Substrate atom count -1 per merge (delete non-canonical)
  - Substrate relation count adjusted per re-point/drop arithmetic
```

### Cost

```
Skunkworks (audit + emit JSONL): ~1-2 hrs (more complex than svd pilot due to 2+6 id-forms)
Exp-Dev (pre-check verification): ~10-15 min each
Testbed (atomic ratify each): ~30 min each
Total: ~3-4 hrs across both merges (sequential or parallel per Skunkworks's choice)
```

## DECISION 100c -- Parallelization (P3 + P2 run independently)

```
Exp-Dev (P3 Iter 4):     existence-check on 9 source atoms; ~30-60 min
Skunkworks (P2 merges):  audit + emit integral + em_algorithm specs; ~1-2 hrs

These workstreams do NOT conflict:
  P3 reads substrate state + emits candidate edges
  P2 reads substrate state + emits merge specs
  No mutual mutations until Testbed dispatches arrive
  
Testbed: ratifies P3 STRICT edges (if any) and P2 merge specs (when delivered)
         in separate atomic batches; no conflict
```

## Substrate-product positioning at stake

```
HARD-PASS both P3 + P2:
  Claim 5 graduates OPEN -> MEASURED (substrate generalizes)
  Substrate-product positioning: 15/15 claims MEASURED + 0 OPEN = COMPLETE
  Atom-MERGE Phase 2 closes; merge procedure validated on 2 more pairs
  Bandwidth for Phase 3 (cosine_similarity; cleanup) opens

HARD-FAIL P3:
  Substrate's STRICT-discovery has additional boundary beyond tier-flatness
  Surface the new boundary; substrate-product positioning gains another scope claim
  Atom-MERGE Phase 2 still progresses (independent)
  
HARD-FAIL P2:
  Unlikely (svd pilot proved the procedure); rollback discipline catches regressions
  Surface the failure mode; refine procedure for cleanup-tier atom-MERGE (Phase 3)
```

## Session tally

98 cumulative decisions (round 100 with this commit + its broadcast). Substrate-product positioning at 15 claims; 14 measured + 1 open. **P3 Iter 4 will resolve the last OPEN claim either direction.**

## Cross-references

- USER direct dispatch ("do it" 14:30)
- DECISION 99 (substrate-product positioning final state; Claim 15 MEASURED): commit `f8957f3c`
- DECISION 96 (84a RETRY HARD-PASS; tier-gradient operational on 4 atoms): commit `8edf1321`
- DECISION 85b (atom-MERGE Phase 2 sequencing): commit `15fea6bd`
- DECISION 86a (svd MERGE PILOT; precedent for Phase 2): commit `2a2fa62a` + Testbed milestone
- DECISION 75d (Iter 3 laptop-only viability): commit `5ce52dec` + 76 follow-up

## Safety / invariants

- ASCII only
- 11th rule: both workstreams substrate-internal
- 18th rule: existence-check before claim (DECISION 78 lesson); pre-check stack before execute (DECISION 88/91/92/96 lessons)
- 19th rule: Skunkworks + Exp-Dev mutual cross-check ongoing
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 expected to PRESERVE across both workstreams

---

**Exp-Dev (Prover):** DECISION 100a DISPATCH -- P3 Iter 4 STRICT-discovery on the 9 source atoms (4 tier-corrected + 5 Phase 4e). Run existence-check + tier-gradient verification. Emit candidate STRICT edges (post-existence-check) for Skunkworks vet. ~30-60 min.

**Skunkworks (Auditor):** DECISION 100b DISPATCH -- P2 atom-MERGE Phase 2 specs for integral/lebesgue_integral + em_algorithm/expectation_maximization. Choose canonicals; audit edges across id-forms; emit consolidated JSONL per pair. ~1-2 hrs.

**Testbed (Integrator):** standby for both ratify queues (P3 STRICT edges + P2 merge specs) when delivered.

The session's substrate-product positioning has 1 OPEN claim. **P3 Iter 4 will close it either direction.** Round-number DECISION 100.

Tag: 100_PARALLEL_DISPATCH_ITER_4_STRICT_DISCOVERY_ON_TIER_CORRECTED_ATOMS_PLUS_ATOM_MERGE_PHASE_2 -- Research (Director)
