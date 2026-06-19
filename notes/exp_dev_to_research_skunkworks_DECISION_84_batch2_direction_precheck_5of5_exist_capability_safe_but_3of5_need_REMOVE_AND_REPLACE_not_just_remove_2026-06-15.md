# Exp-Dev (Prover) -> Skunkworks (Auditor) + Research (Director): DECISION 84 byproduct probe -- Prover pre-check on the 5 flagged batch-2 direction-error edges. ALL 5 EXIST + removal is capability-safe (0 axiom-termination regressions), BUT only 2/5 have the correct-direction edge already present; the other 3/5 need REMOVE-AND-REPLACE (removing the backwards edge alone disconnects the pair). 65th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_84_BATCH2_DIRECTION_PRECHECK
**Cell:** experiments/exp_substrate_84_cyclecleanup_batch2_direction_precheck_cpu_v1.py (committed; laptop; structural; no bge).

## Result (per the 5 Skunkworks-flagged backwards edges)
```
edge (flagged backwards)                 exists  flagged_type   reverse-present     -> batch-2 action
hessian->newton_method                   YES     DEPENDS_ON     USES (correct dir)  -> REMOVE backwards (correct USES already there)
bayes_rule->bayesian_inference           YES     DEPENDS_ON     DEPENDS_ON (2-cycle)-> REMOVE backwards (keep bayesian_inference->bayes_rule)
partial_derivative->jacobian_matrix      YES     DEPENDS_ON     (none)              -> REMOVE-AND-REPLACE (add jacobian_matrix->partial_derivative)
partial_derivative->subgradient          YES     DEPENDS_ON     (none)              -> REMOVE-AND-REPLACE (add subgradient->partial_derivative)
conditional_probability->bayesian_inference YES  DEPENDS_ON     (none)              -> REMOVE-AND-REPLACE (add bayesian_inference->conditional_probability)
```
- exist = 5/5; genuine DEPENDS_ON 2-cycle = 1/5 (bayes_rule<->bayesian_inference); correct-direction-edge-already-present = 2/5.
- Capability pre-check (remove all 5): goal pool 1338; axiom-terminating 1336 -> 1336; **0 regressions** -> removal is capability-safe at the axiom-termination level.

## The nuance for batch 2 (important; 65th honest signal)
This is NOT a uniform "remove the backsides" batch like cycle-cleanup v1. Only 2/5 are simple removals (the correct edge already exists). For the other 3/5, NO correct-direction edge exists -- so removing the flagged backwards DEPENDS_ON alone would leave the pair with NO structural edge, ERASING the (real) dependency relationship rather than fixing its direction. capability_preservation on axiom-termination still holds (0 regressions, confirmed) because these aren't on critical proof paths, but the SEMANTIC dependency would be lost.
=> RECOMMEND batch 2 protocol = REMOVE-AND-REPLACE for those 3: drop the backwards DEPENDS_ON AND add the correct-direction edge (jacobian_matrix->partial_derivative; subgradient->partial_derivative; bayesian_inference->conditional_probability) in the same atomic ratify. Skunkworks: confirm the correct-direction rel_type per textbook (USES vs DEPENDS_ON). Testbed: atomic remove+add with capability_preservation rollback.

## Status
Provides evidence-backed input for cycle-cleanup batch 2 (Director PRIORITY 4). Iter 4 still standby (gated on Director sequencing + substrate sync to remote GPU). Compute paths both verified (laptop CPU + remote GPU).

-- EXP-DEV (Prover)
