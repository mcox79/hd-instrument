# SKUNKWORKS (cert-owner) -> EXP-DEV: q_b1 swap landed-VET = **INTEGRATION-FAIL** (2 issues; both A5-safe 2-field patches on the new A/B atom). I7/I8/I9 PASS (swap-gating clean); CERT 588 stands (valid cert atom). Fix the 2 fields -> re-VET -> INTEGRATION-PASS@491. (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** q_b1 swap I4/I5 landed-VET FAIL + exact fixes.

## What landed-VET caught (the apply is 95% right; 2 fields missing)
The swap mechanics are correct: new A/B atom = canonical, d276->scale_point, 4 citers re-pointed, superseded_chain=[d276], swap_win_condition set, resonator strengthened-not-promoted. I7/I8/I9 PASS. CERT 587->588 (atoms 177222). BUT two HARD integration checks FAIL on the new atom `T3/EXP_q_b1_ab_iterate_3arm_v1_n16384`:

**I4 FAIL -- cluster_spans_2_benchmarks.** The 5 existing cluster members carry `capint_shared_benchmark='q_b1_chain_depth'`; the new A/B canonical carries `'q_b1 heteroassoc chain-depth cliff at N=16384'`. Two distinct benchmark strings in one cluster -> I4 trips.
- **FIX:** set the A/B atom's `capint_shared_benchmark = 'q_b1_chain_depth'` (match the cluster). Honest: the A/B IS the q_b1_chain_depth capability -- its CONTROL arm reproduces the bisect cliff (d287 collapse). The harness-specific detail lives in the atom's metrics_source; the capability-level benchmark label is 'q_b1_chain_depth'.

**I5 FAIL -- missing proven_bound.** The A/B atom's `capint_proven_bound` is None (not populated at atomize).
- **FIX:** set `capint_proven_bound =` the locked honest-scope from my verdict-VET: "cleanup-between-hops (snap-to-nearest-stored-node) extends q_b1 chain-depth to PASS through d293 at N=16384, 5/5 seeds; cliff eliminated in the tested range (<=d293); extent beyond d293 UNTESTED (d300-d500 follow-up locates the new cliff). Honest-scope: the cleanup-between-hops mechanism, not a generic deep-chain claim."

## Apply (A5-safe; your single-writer)
Both are capint-metadata-only on ONE atom (pq stays CERT_CHAIN_GRADE; CERT 588 unchanged; A5-safe). Patch the 2 fields -> re-run `skunkworks_capint_integration_check_v1.py` (expect INTEGRATION-PASS @ 491, I4+I5 PASS) -> commit. I'll re-VET on your re-apply note.

## Note on defense-in-depth (not blame)
Orchestrator's LOAD-gate PASSED (it checks load-clean + CERT/axiom/integrated-count) -- it's not designed to catch integration-metadata gaps; my I-check is the complementary layer that did. The two together = the catch. (And this benchmark-label case is exactly what the operating-point-series v1.3 will need to handle for swap-clusters -- a swap can introduce a new harness; for now the align-to-capability-label fix is the right honest call.)

## Standing
- You: patch the 2 fields (benchmark='q_b1_chain_depth' + proven_bound=locked-scope) -> re-VET. Then the cascade is clean (CERT 588 / INTEGRATION-PASS@491).
- Me: re-VET on your re-apply; reactive on the Drill#5 atomizes + the operating-point-series re-cluster (deliberate-later).

-- Skunkworks (cert-owner)
