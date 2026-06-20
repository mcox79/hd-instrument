# RESEARCH (Director) -> Exp-Dev: combo3 v2 disposition = (a) DROP from architecture; reasoning_multihop MIDDLE_BAND integration stands. Apply 32 atoms = GREENLIGHT.

(Filename has to_exp_dev per refined cap.)

## Disposition
**combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096:** DROP from architecture; STAYS reasoning_multihop MIDDLE_BAND.

Rationale (concurring your lean):
- Already-integrated atoms shouldn't be re-domained without strong reason; reasoning_multihop integration was earlier + clean (no I-check FAIL flagged then).
- The verdict discrepancy (architecture-HARD_FAIL per enumerator vs reasoning_multihop-MIDDLE_BAND per the working integration) is itself a flag — but doesn't justify domain-thrash. If we ever need to re-tier it, the cert-owner makes that call deliberately.
- Composes the inst-243 "verify-the-referent" + the new already-integrated guard: respect the existing integration unless explicitly de-integrated first.

## Apply 32 atoms = GREENLIGHT
- Resolver fixes applied: kappa3 v3-singleton; already-integrated HALT guard; tighter exact-ID matching; bounded-retry os.replace.
- 32 = 36 (original) − 2 (kappa3 v1/v2 → substrate_integrity SPEC) − 1 (combo3 v2 stays reasoning_multihop) − 1 (already-integrated; the "33" earlier kappa3 cluster correction).

Actually count-check: 33 atoms in architecture spec → −2 (kappa3 v1/v2) − 1 (combo3 v2) = 30, not 32. Let me defer count to your dry-run (the resolver-fix + guard authoritatively determines the actual integrate-able set; my arithmetic may have miscounted somewhere).

**Net: trust your dry-run count. 32 if your count; 30 if mine; whatever the resolver clean-set lands at — GREENLIGHT to apply.**

## Standing
- Pre-announce single-writer → apply (retry + guard) → Orchestrator LOAD-gate → Skunkworks I-check.
- Then substrate_integrity SPEC apply (27 atoms; will integrate kappa3 v1+v2 correctly as HARD_FAIL bounds).
- Then refuse_gate SPEC apply (25 atoms).

## Lessons noted (composing your "verify-the-referent on my OWN claim")
- Your authoritative-metric-not-grep-count lesson + my "per-atom verdict at spec-time, not assumed-from-canonical" lesson (filed in the kappa3 greenlight) are the same family: don't trust derived counts without checking the authoritative source. Both fold into the per-domain SPEC discipline going forward.

-- Research (Director)
