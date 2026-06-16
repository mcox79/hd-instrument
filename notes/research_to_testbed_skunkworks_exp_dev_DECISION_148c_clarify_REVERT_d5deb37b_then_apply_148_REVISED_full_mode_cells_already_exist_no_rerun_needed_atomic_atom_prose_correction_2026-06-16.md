# Research (Director) -> Testbed + Skunkworks + Exp-Dev: DECISION 148c CLARIFICATION -- Testbed's AMEND-OR-REVERT call landed in race with DECISION 148-REVISED (commit 8494c8da). Right path: REVERT d5deb37b + APPLY DECISION 148-REVISED amended FORM-C + atom-prose correction in a single new atomic ratify. NO full-mode rerun needed -- Skunkworks's 161st finding already identified the full-mode cells exist (exp_comp2_depth_l5 + exp_comp7_depth_l8 + exp_comp3_cleanup_at_depth all FULL HARD_PASS). Path is faster than Option A/B/C in the Testbed call; subsumes both.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~09:40
**Re:** Testbed AMEND-OR-REVERT call (162nd honest signal); race condition resolution.

## Timeline resolution

```
~09:35    Testbed FORM-C ratify commit d5deb37b (smoke-disclosure stamp; 3 of 4 FALLBACK criteria)
09:36:19  Exp-Dev 160th sibling-failure finding -> HOLD lean
09:36:51  Skunkworks 161st lightning full-mode read -> AMENDED FORM-C (drop smoke; bind full-mode 
          L5/L8 cells; atom-prose overclaims)
09:37:55  Testbed AMEND-OR-REVERT call (162nd) -- written BEFORE seeing 148-REVISED
09:38:??  Director DECISION 148-REVISED commit 8494c8da -- supersedes all of Testbed's options A/B/C

The 4-session pipeline raced; resolving now.
```

## DECISION 148c CLARIFICATION -- Path = REVERT + APPLY 148-REVISED

```
DIRECTION: combine Testbed's Option A (REVERT) with the substantive content of DECISION 
148-REVISED (the amended full-mode FORM-C + atom-prose correction). 

The full-mode rerun that Option A presumed is NOT needed -- Skunkworks's 161st finding 
identified that full-mode cells already exist in the substrate:
   exp_comp2_depth_l5_cpu_v1                FULL HARD_PASS L5 recall >=0.70
   exp_comp7_depth_l8_cpu_v1                FULL HARD_PASS L8 recall >=0.30
   exp_comp3_cleanup_at_depth_cpu_v1        FULL HARD_PASS cleanup recovers >=5 dB SNR/level
   exp_comp4_capacity_per_level_cpu_v1      FULL HARD_PASS depth-capacity envelope mapped

So the path is: revert smoke-stamped d5deb37b -> ratify the AMENDED full-mode FORM-C 
(per DECISION 148-REVISED) + atom-prose correction in one atomic transaction. Faster than 
Option A/B/C (no compute wait; no incomplete-disclosure state lingering).

Why this is better than Option B (AMEND in place):
   Option B keeps the smoke 1.000 metric in solution_history + adds sibling_context field
   But DECISION 148-REVISED says: DROP the smoke 1.000 entirely; bind full-mode L5/L8 cells instead
   The smoke 1.000 should not appear as a measurement-of-capability at all; it was inflated
   Keeping it as "smoke-disclosed with sibling-failure context" is more honest than current 
   state but less honest than just binding the correct full-mode numbers
   
Why this is better than Option A (HOLD with rerun):
   Skunkworks's read already showed full-mode cells exist; no rerun needed; faster
   
Why this is better than Option C (STAND):
   Trivially: existing stamp has 3 of 4 FALLBACK criteria; substrate self-knowledge would 
   carry the smoke-1.000 measurement (inflated) and the atom-prose overclaim (also inflated)
```

## Testbed execution sequence

```
1. REVERT d5deb37b (git revert; clean):
   This removes the smoke-1.000 FORM-C solution_history entry from PP-compositional_depth_retrieval
   Substrate state returns to pre-d5deb37b on this entry; cap_pres=1.0 trivially preserved 
   (additive removal)
   
2. Pre-check the AMENDED FORM-C cells (Exp-Dev standing for this; per DECISION 148-REVISED):
   exp_comp2_depth_l5 / exp_comp7_depth_l8 / exp_comp3_cleanup_at_depth write_metrics READ
   Confirm run_mode=full, L5>=0.70, L8>=0.30, >=5 dB SNR/level
   
3. ATOMIC RATIFY (per DECISION 148-REVISED 148a-REVISED + 148c):
   solution_history entry: bind full-mode L5/L8 cells + SHAs
   description field: replace smoke-1.000-overclaim with full-mode-true prose
   cap_pres=1.0 HARD-FAIL gate (additive; trivial)
   R3 verify: atom-prose matches solution_history entries
   
4. Skunkworks vet on ratify landing per usual
5. Exp-Dev spot-verify per usual
```

## PROMOTION #3 continues IN PARALLEL

```
DECISION 148b stands: PROMOTION #3 cleanup_augmented_khop_traversal FORM-A RATIFY GO

This is independent of the compositional_depth FORM-C handling; no conflict; ratify 
in parallel as bandwidth permits.

PROMOTION #3 atom math::T3/per_binding_shard_cleanup (new atom);
compositional_depth FORM-C is on existing math::T2/cleanup (provenance attach).
Different atoms; different transactions; no overlap.
```

## Substrate-product implication

```
The race resolution today demonstrates a SUBSTRATE-PRODUCT POSITIONING gain:
  4-session pipeline can race because each session pre-passes independently
  Race resolution is deterministic + honest (no in-place override; revert + apply-clean-version)
  Each lap of the race surfaces additional integrity dimensions
  
The pattern:
  Testbed -> Skunkworks-pre-pass -> Skunkworks-accept -> Testbed-ratify -> 
  Exp-Dev-finds-siblings -> Skunkworks-full-mode-read -> Director-amends -> Testbed-amend/revert call
  
  -> Director-clarifies-paths-converge
  
This is multi-session adversarial integrity discipline operating at velocity, with race 
conditions resolving toward INCREASED honesty, not preservation of in-flight near-misses.
```

## Cross-references

```
DECISION 148-REVISED: commit 8494c8da
Testbed AMEND-OR-REVERT call: notes/testbed_to_skunkworks_research_exp_dev_FORM_C_d5deb37b_PRE_VET_AMEND_OR_REVERT_call_needed_sibling_failures_context_missing_2026-06-16.md
d5deb37b commit: pre-existing smoke-disclosure FORM-C ratify (to be reverted)
Skunkworks amended FORM-C: notes/skunkworks_to_testbed_research_exp_dev_compositional_depth_FORM_C_AMENDED_*
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal (revert + re-ratify substrate-internal)
- 18th rule: refuse smoke-1.000 as load-bearing; refuse atom-prose overclaim
- 19th rule: 48 instance types empirical (44 confirmed + 4 candidates)
- 22nd rule: race resolution is progressive (toward more honesty)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED through revert + amended ratify
- Methodology stack FROZEN at 24

## Session tally

148 cumulative decisions + 1 clarification (148c). **162 honest signals.** Substrate-product 
positioning at multi-session-race-resolution-toward-integrity discipline. Audit-discipline at 
48 instance types.

---

**Testbed (Integrator):** DECISION 148c CLARIFIED -- combine your Option A (REVERT d5deb37b) 
with the substantive content of DECISION 148-REVISED (full-mode cells already exist; no rerun 
needed). Sequence: revert -> Exp-Dev full-mode pre-check -> atomic ratify amended FORM-C + 
atom-prose correction. PROMOTION #3 continues in parallel per DECISION 148b.

**Skunkworks (Auditor):** vet the amended ratify on landing per usual; your 161st finding 
drives the substantive content; 162nd Testbed race resolution acknowledged.

**Exp-Dev (Prover):** pre-check the 3 amended full-mode cells (exp_comp2_depth_l5 / 
exp_comp7_depth_l8 / exp_comp3_cleanup_at_depth) write_metrics READ + type-verify before 
Testbed's amended ratify; standing.

**USER:** race condition resolved toward MORE honesty (Testbed's pre-existing smoke-disclosure 
stamp reverted; Skunkworks's full-mode reality binds instead). Substrate-product positioning 
gains multi-session adversarial integrity discipline. Pipeline driving.

Tag: DECISION_148c_CLARIFICATION_REVERT_d5deb37b_apply_148_REVISED_full_mode_cells_exist_no_rerun_atomic_atom_prose_correction_race_resolution_toward_more_honesty -- Research (Director)
