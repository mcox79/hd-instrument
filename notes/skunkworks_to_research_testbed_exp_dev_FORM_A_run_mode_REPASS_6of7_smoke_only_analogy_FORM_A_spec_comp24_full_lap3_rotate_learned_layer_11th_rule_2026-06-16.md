# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: DECISION 149d FORM-A run_mode RE-PASS DONE + 149e within-domain analogy FORM-A SPEC. STARK RESULT (corrects my own verdict-only triage; 19th rule): of the 7 "authorable" FORM-A candidates, 6 are SMOKE-mode (tier C, NOT load-bearing eligible) -- only within-domain analogy has full-mode backing. Plus a NEW 11th-rule flag: the analogy full-mode cell lap3_rotate uses LEARNED RotatE embeddings (not substrate-on-its-own) -> use comp24_analogical_at_l3 (clean substrate-internal) instead.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** FORM_A_run_mode_REPASS_6of7_smoke_analogy_spec_comp24_full_lap3_learned_11th_rule

## DECISION 149d -- FORM-A triage run_mode RE-PASS (corrects my verdict-only triage)
Re-passed each candidate's cell for run_mode + N + n_seeds (per DECISION 149a tiers A/B/C):
```
  1 within-domain analogy     SMOKE (analogy_map/relation_transfer) -> RE-BASE full (149e below)
  2 counterfactual cf-RPE     exp_counterfactual_axiom_exclusion/demo  SMOKE n=1          tier C
  3 audit-preserving B6xSQ2   exp_substrate_b6_x_sq2                   SMOKE N=512 n=2     tier C
  4 deletion-cert             exp_deletion_cert_refusal_joint/_zratio  SMOKE N=4096 n=2    tier C
  5 drift-kappa3              exp_a7_kappa3_drift / drift_kernel        SMOKE N=512 n=2    tier C
  6 composition L=10000       exp_substrate_capacity_composition_b2xb4  SMOKE N=512 n=2    tier C
  7 eviction-B6               exp_caching_eviction_cost_amortized       SMOKE N=512 n=2    tier C
```
RESULT: **6 of 7 candidates are SMOKE-mode (tier C -> NOT load-bearing eligible per DECISION 149a).** Only within-domain analogy has a full-mode path. (Note: deletion-cert ran smoke even at N=4096 -- run_mode=smoke is tier C regardless of N; smoke reduces scope/iterations beyond just N.)
- OWN-OUTPUT CORRECTION (19th rule): my FORM-A triage ranked these "authorable" by VERDICT ONLY -- it inherited exactly the smoke blind-spot DECISION 149 just made required. The honest re-passed backlog is MUCH smaller: 1 authorable + 6 needing full-mode reruns.
- PATH for the 6 tier-C: each cell's script supports RUN_MODE=full (cheap CPU); trigger full-mode reruns (Exp-Dev's lane, like the K10-20 rescue) -> IF they HARD_PASS full-mode, authorable; IF they deflate/fail, drop. Do NOT author any on smoke (load-bearing poison). Phase-A-tail; not Phase-B blocker.

## DECISION 149e -- within-domain analogy FORM-A SPEC (full-mode; + NEW 11th-rule flag)
Two full-mode analogy cells exist; they are NOT equivalent for substrate-on-its-own:
```
  exp_comp24_analogical_at_l3_cpu_v1  FULL HARD_PASS n=1  "within-domain A:B::C:D over deep L3 composites
     recovers target >=0.85, within 10pp of atomic -- relational binding + cleanup composes over composites"
     -> CLEAN SUBSTRATE-INTERNAL (FHRR/role-filler binding + cleanup; NO learned layer). USE THIS.
  exp_lap3_rotate_analogy_cpu_v1      FULL HARD_PASS n=1  "learned RotatE relation embeddings ... analogy
     works with a LEARNED relational codebook"
     -> 11th-RULE FLAG: relies on a LEARNED-vector codebook (RotatE), NOT substrate-on-its-own.
        EXCLUDE as the substrate-internal corroboration (it's the LLM-class/learned-layer path the
        11th rule + Goal-4 architectural bet deliberately does NOT take). Record as a learned-layer
        comparator at most; do NOT bind as the clean within-domain-analogy FORM-A.
```
SPEC (FORM-A new atom):
```
  NEW atom: math::T3/relational_analogy_binding
    description: A:B::C:D proportional analogy via relational role-filler binding + cleanup,
      composing over deep (L3) composite items; recovers target >=0.85 (within 10pp of atomic).
      Substrate-internal (no learned codebook).
    DEPENDS_ON: T2/role_filler_binding (or fhrr_bind) + T2_FAM/cleanup_retrieval
    corroboration: exp_comp24_analogical_at_l3 (FULL HARD_PASS, >=0.85, n=1) -- tier B
    type: capability-recall   |   3-of-3: cap-pres 1.0 + re-expressible (binding+cleanup) + closes within-domain-analogy gap
    (cross-domain analogy stays RETRACTED/DROPPED -- P9 confound; do NOT conflate.)
```

## Net
- FORM-A backlog under the tier discipline: 1 authorable NOW (within-domain analogy via comp24, tier B, substrate-internal) + 6 tier-C-smoke needing full-mode reruns (cheap) before eligibility. Smaller-but-true, hard -- the run_mode dimension cut the backlog from 7 to 1-authorable.
- Exp-Dev: (a) pre-check the within-domain analogy FORM-A (comp24 cell; confirm full-mode + >=0.85 + substrate-internal); (b) the 6 tier-C candidates -- full-mode reruns at your bandwidth (like the K10-20 rescue) decide their eligibility.
- Testbed: within-domain analogy FORM-A ratify on Exp-Dev pre-check; the 6 tier-C HELD pending full-mode.
- compositional_depth FORM-C (both dims) + PROMOTION #3: converged per DECISION 149c/f; I vet on ratify landing.

Tag: FORM_A_run_mode_REPASS_6of7_SMOKE_tier_C_not_load_bearing_only_within_domain_analogy_full_mode_authorable_comp24_substrate_internal_lap3_rotate_LEARNED_RotatE_11th_rule_EXCLUDE_relational_analogy_binding_FORM_A_spec_backlog_7_to_1_smaller_but_true -- SKUNKWORKS (Auditor)
