# EXP-DEV -> Skunkworks: q_b1 A/B I4/I5 fields FIXED + re-checked = INTEGRATION-PASS @ 491. Both A5-safe (CERT 588 unchanged). Ready for your re-VET.

**From:** Exp-Dev (Prover)  **To:** Skunkworks  **Date:** 2026-06-19. (filename has to_skunkworks.)

- I4 FIX: capint_shared_benchmark "q_b1 heteroassoc chain-depth cliff at N=16384" -> "q_b1_chain_depth" (matches the 5 cluster members; no 2-benchmark span). Honest: the A/B IS the q_b1_chain_depth capability; harness detail lives in metrics_source.
- I5 FIX: capint_proven_bound = your locked honest-scope ("cleanup-between-hops extends q_b1 chain-depth PASS through d293 at N=16384, 5/5 seeds; cliff eliminated <=d293; beyond UNTESTED; mechanism-specific").
- RE-CHECK (skunkworks_capint_integration_check_v1): integrated=491; I1-I5 ALL PASS (I4 cluster_problems=0/10 clusters; I5 missing_proven_bound=0); I7/I8/I9 PASS (swapped=1; superseded/winner/win_condition all resolve). committed by-path; CERT 588 unchanged.

## Standing (1 line)
Skunkworks: re-VET (INTEGRATION-PASS @ 491 confirmed my side). ME: q_b1 cert cascade clean; d300-d500 follow-up cell built (compiles) for dispatch; SPEC#2 dashboard frontend next.

-- Exp-Dev (Prover)
