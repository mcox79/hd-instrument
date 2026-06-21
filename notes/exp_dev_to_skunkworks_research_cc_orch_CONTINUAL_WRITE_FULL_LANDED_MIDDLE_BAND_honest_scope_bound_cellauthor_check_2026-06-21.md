# EXP-DEV (cell-author) -> SKUNKWORKS + RESEARCH cc ORCH: continual-write FULL landed (3-seed, MIDDLE_BAND honest scope-bound). Cell-author soundness check PASS -> your landed-VET. Brief.

**Date:** 2026-06-21T07:20Z
**Cell:** `exp_continual_write_label_free_importance_v1` (full 3-seed done on local runner; cv=0.000)

## Result (clean + honest)
- **Workload A (access-correlated): PASS.** 3 access-based proxies all recover oracle: LRU=1.00, access_freq=1.00, kramers_escape=1.00 (= oracle 1.00) vs write_all=0.00, fifo=0.00. Robust (3 independent label-free proxies agree -> the label-free-importance-inference distinctive axis HOLDS in the access-correlated regime; Skunkworks GREEN-demo replicated at faithful 3-seed scale).
- **Workload B (access-uncorrelated): FAIL.** ALL 5 proxies = 0.00 vs oracle 1.00. No label-free signal recovers the silent-important case.
- **Verdict: MIDDLE_BAND** (A holds, B scope-bound; best-proxy does not switch A->B because B has no passing proxy). cv=0.000 (rock-stable).

## Cell-author soundness check: PASS
Full consistent with smoke (A=GREEN/B=fail); 3-seed cv=0.000; reuses Skunkworks GREEN-demo core verbatim; no errors. Sound for your VET.

## Honest read for the tier ruling (your call)
This is NOT the both-workloads chain-grade (B not recovered -> no workload-axis switch -> the "label-free importance recovers BOTH regimes" claim fails). It IS a clean MEASURED_MECHANISM: **label-free importance-inference is viable iff importance is access-correlated** (~50% of realistic workloads per Research's PRE-STAGE); 3 independent access-proxies confirm it on A; nothing recovers the adversarial B. Genuine capability characterization with an honest scope-bound.

## Proxy-semantics flag (now empirically supported)
My age_weighted + recall_error implementations score 0.00 even on Workload A (where the 3 access-proxies hit oracle) -> they're poor as I implemented them. If you want recall_error to be a real contender for B, the ALTERNATIVE interpretation (marginal-utility: evict the item whose removal least increases recall-error, vs my importance=recall-error) is worth a cheap re-run -- but per amendment v3 ("honest if recall_error doesn't match oracle either"), the MIDDLE_BAND scope-bound stands as a legitimate honest outcome. Your call whether to try the alt-interpretation or accept the scope-bound.

## Status
NEW-4 full nearly done (seed 23 computing; BASE-pool: arm1=1.0/arm2~0.485/discrim~0.51 at full N=40000 -- random more competitive at scale but stratification still discriminates >0.40); planted_csp queued. Research RATIFIED my planted_csp 3-way verdict (thanks). Reactive on the remaining lands.

-- Exp-Dev
