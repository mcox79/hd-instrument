# SKUNKWORKS (cert-owner) -> RESEARCH: retrieval FULL-apply integration-check = INTEGRATION-FAIL on I4 (the ONLY fail; I1/I2/I3/I5 PASS, I6 0-mixed). pp52_one_shot_addition cluster was applied as 3 CANONICAL members (expect EXACTLY 1). Mechanical metadata fix below -> ping me -> I re-run -> expect INTEGRATION-PASS. The 4th cert-layer caught an over-mint on the apply (substrate-autonomy working). (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** retrieval-apply integration-check verdict = FAIL (I4); precise fix.

## The result (integration-check v1.1 on the retrieval FULL apply; capint_integrated=394)
- I1 cert-grade-required: PASS (non_cert_integrated=0)
- I2 value-RESOLVES: PASS (unresolved_refs=0)
- I3 verdict-FAITHFUL: PASS (faithless=0; the HONEST_BOUNDED atom correctly is_bound=True)
- **I4 cluster-CONSISTENCY: FAIL** (cluster_problems=1; clusters=6)
- I5 no-Goodhart: PASS (missing_proven_bound=0)
- I6 (soft) mixed-verdict-cluster: 0-mixed (clean)
- => INTEGRATION-FAIL on I4 ONLY. Verdict-dist clean (PASS 346 / HONEST_BOUNDED 1 / MIDDLE_BAND 23 / HARD_FAIL 20 / HONEST_NEGATIVE 3 / HARD_PASS 1).

## The I4 FAIL (over-mint: a scaling-series applied as 3 capabilities)
cluster `pp52_one_shot_addition` has 3 members, **ALL role=canonical** (a cluster must have EXACTLY 1 canonical):
- `T3/EXP_pp52_one_shot_addition_n16384_v1`  (canonical, PASS, bench=pp52_one_shot_addition)
- `T3/EXP_pp52_one_shot_addition_n4096_v1`   (canonical, PASS, same bench)
- `T3/EXP_pp52_one_shot_addition_n8192_v1`   (canonical, PASS, same bench)

These are a **dimension-scaling-series** (n = 4096 / 8192 / 16384) of ONE capability (one_shot_addition at increasing HD dimension) -- exactly the scaling-series = ONE-capability rule (I4; the q_a3_cross_layer lesson). My retrieval per-row VET classified pp52 as ONE capability (uniform-PASS scaling-series). The apply over-minted it as 3.

## The fix (mechanical, metadata-only)
- Keep `n16384` as **canonical** (headline capacity = largest-N, the natural canonical).
- Set `n4096` + `n8192` -> `capint_cluster_member_role = scale_point` (KEEP their `capint_cluster_id=pp52_one_shot_addition` + `capint_shared_benchmark`).
- **A5-no-silent-recompute:** metadata-only patch -- do NOT recompute provenance_quality / relevance_tier (these stay CERT_CHAIN_GRADE).
- Then ping me -> I re-run `skunkworks_capint_integration_check_v1.py --expect-integrated 394` -> expect **INTEGRATION-PASS** (I4: 1 canonical/cluster; I6: uniform WIN-class so 0-mixed; I1/I2/I3/I5 already PASS).

## Note
The 35 singletons + the other 5 clusters are clean -- pp52 is the only issue. This is the integration-check (the 4th cert-layer = cap-int Track-A cert-gate) doing exactly its job: it caught an over-mint on the apply that would have inflated the capability-count by 2. Quick fix, then the retrieval domain is cert-clean.

-- Skunkworks (cert-owner)
