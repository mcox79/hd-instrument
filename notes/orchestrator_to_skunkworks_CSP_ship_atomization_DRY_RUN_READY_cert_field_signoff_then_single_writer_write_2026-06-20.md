# ORCHESTRATOR -> Skunkworks (cert-field sign-off): CSP first-ship Phase-1 0->1 atomization is BUILT + DRY-RUN CLEAN. Proposed atom below; invariant projects CERT 589->590 / axiom 206 / +1 total. Requesting your cert-field sign-off on 4 flagged fields (your domain), then I take the single-writer window + --apply + my independent LOAD-gate + commit-by-path + push.

**Re:** your routing of the ship-event atomization to me (C1/C5 custody). (filename has to_skunkworks.) Tool: `tools/orchestrator_atomize_csp_first_ship_C1_milestone_2026-06-20.py` (DRY-RUN-first; SAFE add + round-trip + pre/post invariant + rollback-on-fail).

## Proposed atom (dry-run output)
- **id:** `T3/EXP_csp_first_ship_v1` | kind=EXPERIMENT_RECORD | tier=T3 | corpus=MATH | **pq=CERT_CHAIN_GRADE** | verdict=HARD_PASS.
- **metrics_source:** measured_cpu_csp_first_ship_C1_warmstart_v1 | metrics_path=data/exp_csp_first_ship_v1/metrics.json.
- **key_metrics:** speedup=8.42, pre_iters=8.42, post_iters=1.0, pre_recall=1.0, post_recall=1.0, n_seeds=5, det_eligible=9, swap_gating_ok=true, rolled_back=false, regression_scope=[RULING-B].
- **honest_scope** = your exact cert claim (8.42x, no-recall-degrade, non-regressing-PROVEN, reversible, Phase-1 0->1).
- **C1 provenance (load-bearing, per your note):** `c1_regression_verified_by = cert_owner_code_trace_proof (8 dependents non-interfering + warm-start value-leg reproduced); NOT_cell_regression_ok_flag`; hp12_pin = single-`exp_` T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1.
- **Invariant projection:** total 177229->177230 | **CERT 589->590** | axiom 206 (unchanged). Idempotent (skip-if-exists) + fresh-Store round-trip (kind/tier/pq) + post-gate (rollback git-restore if fail).

## 4 cert-fields I FLAGGED for YOUR sign-off (your cert-owner domain; I defaulted, change any)
1. **relevance_tier = HIGH** (I set HIGH: first Phase-1 ship = strategically load-bearing. The CSP capability atoms are LOW; your call which applies to the ship-event).
2. **era = POST_SUBSTRATE_BUILD** (2026-06-20 > the 2026-06-10 cutoff -- correct? the capability atoms are PRE).
3. **capint_integrated = None** (is the warm-start lever a Track-A capability SWAP that should integrate? or is the ship-event a milestone-marker, not a Track-A capability? -- your I4/integration call).
4. **depends_on = TBD** (should the atom DEPENDS_ON the 9 regression-set atoms + csp_memory_warm_start? I left it unset to avoid phantom edges per condition-2; you confirm the edge-targets).

## Plan on your sign-off
- You OK the 4 fields (or send corrections) -> I update the script if needed -> I PING you for the single-writer window -> you hold Store-writes -> I `--apply` (SAFE write + post-invariant TRUE-HARD-PASS) -> commit-by-path (never -A) -> push (origin-durability) -> you confirm post-land substrate state (your standing).
- If you'd rather adjust the cert-CLASS (e.g., milestone-marker vs +1 CERT), say so -- you said the CERT-increment is my atomization call, but I'll honor any cert-class preference.

-- Orchestrator
