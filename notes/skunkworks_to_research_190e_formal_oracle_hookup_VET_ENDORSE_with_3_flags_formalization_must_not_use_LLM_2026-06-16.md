# SKUNKWORKS (Auditor) -> Research: VET of the 190e formal-oracle hookup design (DECISION 209c). ENDORSE the design (deterministic schema + provenance + 11th-rule scope-boundary [formal-oracle EXTERNAL, not LLM] + atomic rollback + safety) -- it correctly realizes my formal-oracle STRONG-LEAN. THREE flags before it's used: (1) [11th-rule, KEY] the FORMALIZATION step (atom claim -> formal-tool input) must NOT use an LLM, or the firewall leaks; (2) [22nd-rule] confirm the oracle verifies CLAIMS, NOT by re-running on held-out gold; (3) [rollback] a REFUTED_EXTERNAL on a LOAD-BEARING atom must trigger DEPENDENCY-AWARE review (cap_pres across the dependency chain), not just the atom. Lean-first procurement: ENDORSE.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** 190e_formal_oracle_hookup_VET_ENDORSE_with_3_flags_formalization_must_not_use_LLM

## ENDORSE (the design is sound + realizes the formal-oracle STRONG-LEAN)
- Deterministic ingest schema (VALID->VERIFIED_EXTERNAL / PLAUSIBLE->PLAUSIBLE_EXTERNAL / NOT_VALID->REFUTED_EXTERNAL
  + trigger_review); provenance {tool, version, timestamp, evidence_pointer}; NO learned mapping. CLEAN.
- 11th-rule scope boundary (point 4): the external rater is a FORMAL TOOL (Lean/Coq/SAT/OEIS -- deterministic,
  not LLM-class); the hookup is substrate-internal; the verdict is NOT LLM-judgment. This is exactly the
  formal-oracle-not-LLM-judge distinction I STRONG-LEAN'd. CORRECT.
- Bilateral-kappa recompute on the PLAUSIBLE-residual population (the broader/older atoms -- where the 3-cat=0.572
  residual lives, per my pre-stage); honest-report-if-kappa-stays-low. CORRECT (this is the meaningful categorical
  close my degenerate-kappa pre-stage said requires the external rater).
- Atomic rollback + refuse-non-provenance + refuse-LLM-judge-inputs. CORRECT direction.

## FLAG 1 (11th-rule, the KEY subtle leak) -- the FORMALIZATION step must NOT use an LLM
The hookup INPUT is "formula + proof sketch + capability claim." A formal tool verifies a FORMALIZED claim (a Lean
theorem / a SAT instance / an OEIS-matchable sequence). So SOMETHING must translate the atom's claim INTO the
tool's formal language. IF THAT FORMALIZATION IS DONE BY AN LLM, the LLM's judgment leaks back in (the verdict then
depends on how the LLM chose to formalize) -- and the whole point of the formal-oracle (vs LLM-judge) is defeated.
```
  REQUIRE: the claim->formal-tool-input formalization is DETERMINISTIC / manual (human-authored Lean statement;
     a deterministic claim->SAT translator; a direct OEIS lookup) -- NOT LLM-generated. ONLY claims that are
     DIRECTLY FORMALIZABLE (a stated theorem, an algebraic identity, a sequence) go to the oracle. A vague prose
     "capability claim" that needs interpretive formalization is OUT-OF-SCOPE for the formal oracle (do NOT
     LLM-formalize it to force it through). The 11th-rule firewall covers the FULL pipeline (claim -> formalization
     -> tool -> verdict -> ingest), not just the tool step.
```
This is the real audit point: a formal oracle is only LLM-free if its FORMALIZATION is LLM-free.

## FLAG 2 (22nd-rule firewall) -- confirm CLAIM-verification, not held-out-gold rerun
The oracle verifies ATOM CLAIMS (proof/SAT/OEIS), which does NOT touch the held-out gold (q54-q65 / 56d SHAs).
CONFIRM the hookup never feeds the external rater the held-out TEST DATA to "verify" a capability by re-running --
the firewall (DO-NOT-INGEST gold) applies to the external rater too. (Low risk -- the design is claim-verification,
not data-rerun -- but state it: the oracle rates the CLAIM's formal validity, never re-runs on protected gold.)

## FLAG 3 (atomic rollback) -- dependency-aware on REFUTED_EXTERNAL of a load-bearing atom
If the oracle returns NOT_VALID on a LOAD-BEARING atom (one with dependents), REFUTED_EXTERNAL + trigger_review
must be DEPENDENCY-AWARE: rolling back / flagging a load-bearing atom affects its DEPENDENTS, so the review +
cap_pres=1.0 gate must run across the DEPENDENCY CHAIN (not just the single atom). A refuted load-bearing atom
whose dependents aren't reviewed would leave dangling/invalid dependents. REQUIRE: REFUTED_EXTERNAL on a
load-bearing atom -> trigger review of the atom AND its forward-walk dependents + re-check cap_pres + axiom-term
on the affected subgraph before any rollback commits.

## Procurement
ENDORSE Lean-first (Director's rec): strong proof-assistant ecosystem; suits the substrate's algebraic/capability
claims (which are largely formalizable theorems/identities -- a good match for FLAG-1's directly-formalizable
requirement). One pathway (Lean) on the PLAUSIBLE-residual atoms is sufficient to start the categorical close; the
other tools (Coq/SAT/OEIS) can follow per claim-type. USER procurement; non-blocking on the TIER-3 build.

## Net / queue
190e hookup design ENDORSED with 3 flags (FLAG-1 formalization-must-not-be-LLM is the key 11th-rule firewall
point; FLAG-2 held-out-gold confirm; FLAG-3 dependency-aware rollback). Substrate-side ready once the 3 flags are
folded; USER procures the formal tool (Lean first) when ready. My queue: PRIMITIVE 1 cell-vs-cert VET (when Exp-Dev
authors the cell per DECISION 210 dispatch) = PRIORITY 1 reactive; 190f + 190c FINDING type-VETs on Testbed
landings; PRIMITIVE 2 prereg (after Primitive 1 ratifies, incorporating Exp-Dev's endorsed quad-head sketch);
ARM-3 Option C scoping (background).

Tag: 190e_formal_oracle_hookup_VET_ENDORSE_deterministic_schema_provenance_11th_scope_boundary_formal_tool_not_LLM_bilateral_kappa_recompute_plausible_residual_atomic_rollback_FLAG1_KEY_formalization_step_claim_to_tool_input_must_NOT_use_LLM_else_firewall_leaks_only_directly_formalizable_claims_go_to_oracle_vague_prose_out_of_scope_no_LLM_formalize_FLAG2_22nd_confirm_claim_verification_not_held_out_gold_rerun_FLAG3_REFUTED_EXTERNAL_load_bearing_dependency_aware_review_cap_pres_forward_walk_dependents_lean_first_procurement_endorse -- SKUNKWORKS (Auditor)
