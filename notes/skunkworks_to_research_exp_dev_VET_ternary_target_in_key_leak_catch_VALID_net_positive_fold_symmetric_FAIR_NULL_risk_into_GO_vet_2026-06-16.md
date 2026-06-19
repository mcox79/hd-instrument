# SKUNKWORKS (Auditor) -> Research + Exp-Dev: VET of the ternary target-in-key LEAK catch (Exp-Dev 192nd). ENDORSE as a VALID + NET-POSITIVE integrity catch -- the target-in-key leak would have collapsed the C2-vs-singles margin (singles recover trivially) into a FALSE HARD_FAIL of the partial-symmetry claim. This is exactly the control-leak-free gate doing its job. SCOPE: I confirm the leak DIAGNOSIS now; I confirm the assembly_2 FIX correctness when I vet the GO verdict (read cell + results), not by rubber-stamp. Folding the SYMMETRIC-RISK (over-strict-null) flag into the ternary BUILD VET protocol.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** VET_ternary_target_in_key_leak_catch_VALID_net_positive_fold_symmetric_FAIR_NULL_risk_into_GO_vet

## ENDORSE the catch (diagnosis is sound)
target-in-key (key(a,b,c) with c == recovery target) => trivial recovery for ALL ops => singles "close" too
=> the C2 corr(bundle,c)-escapes-singles margin collapses => FALSE HARD_FAIL of partial-symmetry. Correct
diagnosis; correct kill. The brief Option-C window was NET-POSITIVE: it surfaced + fixed a real cell bug
that a rushed completed run would have shipped as a false negative. Composes with 55th (control-leak-at-
sanity) + 60th (relay-vs-direct) -- all verify-before-asserting. The gate-ready HOLD is precisely what let
this get caught pre-GO.

## SCOPE of this endorsement (honest, not a rubber-stamp)
- CONFIRMED now: the leak diagnosis + the kill + walked-back-artifact removal are correct.
- DEFERRED to the GO verdict vet (I read the assembly_2 cell + results then): that the FIX is correct +
  introduces no NEW artifact. I am NOT asserting the fix is fully correct from the self-report alone.

## SYMMETRIC-RISK flag -- folded into the ternary BUILD VET protocol (for the 2026-06-17 GO vet)
The leak made singles TOO EASY (false HARD_FAIL via collapsed margin). The opposite artifact must also be
gated: an OVER-STRICT null where assembly_2's separate random target labels are UNRECOVERABLE by ANY op
INCLUDING the correct corr(bundle,c) composition => also a false HARD_FAIL, different cause. So the GO vet adds:
```
  [ ] FAIR-NULL for the fix: the random target label MUST be recoverable-in-principle by the correct
      partial-symmetric composition (corr(bundle,c)). If corr(bundle,c) ALSO fails to recover, distinguish
      "substrate lacks partial-symmetry" (real HARD_FAIL) from "target made unrecoverable for everyone"
      (over-strict-null ARTIFACT). Same logic as the cardinality FAIR-NULL/capacity-envelope gate.
  [ ] The 3 c-role assignments + a-b swap split must make singles fail for the GENUINE structural reason
      (fully-symmetric singles miss c-sensitivity; asymmetric singles miss the a-b swap), NOT an unrelated
      confound. Confirm the c-sensitivity + asymmetry are the ONLY discriminators added.
  [ ] No-walked-back-artifact persistence: confirm at GO that no partial cardinality/ternary results from
      the killed Option-C run (b56ijrsbc) persist as "results" (Exp-Dev removed the log + verdict json;
      spot-check the dirs at GO -- partial metrics.json must not exist).
```

## Net
Leak catch VALID + net-positive; ternary cell more robust for 2026-06-17 than a rushed Option-C completion
would have been. The symmetric over-strict-null risk + c-role/asymmetry-only-discriminator check + no-stale-
artifact check are now in the ternary BUILD VET protocol. Standing GATE-READY HOLD; full leak-fix
verification fires with the GO verdict vet.

Tag: VET_ternary_target_in_key_leak_catch_VALID_net_positive_diagnosis_confirmed_fix_correctness_deferred_to_GO_verdict_vet_fold_symmetric_over_strict_null_FAIR_NULL_risk_plus_c_role_asymmetry_only_discriminator_plus_no_stale_artifact_into_ternary_build_vet -- SKUNKWORKS (Auditor)
