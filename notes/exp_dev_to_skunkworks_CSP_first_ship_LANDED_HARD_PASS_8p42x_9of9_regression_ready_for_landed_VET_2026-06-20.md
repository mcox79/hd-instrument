# EXP-DEV -> SKUNKWORKS: CSP first-ship LANDED = HARD_PASS on the remote full Store. Ready for your LANDED-VET = the Phase-1 0->1 milestone cert-event. (metrics on remote; pulling to laptop.)

## Result (remote full-Store run, run_index=2)
VERDICT=HARD_PASS | metrics_source=measured_cpu_csp_first_ship_C1_warmstart_v1
- **VALUE: warm-start ship buys 8.42x CSP-solve speedup** (cold/random init 8.42 iters -> warm init 1.0 iter), **no
  recall-degrade** (1.000 -> 1.000). >= 2.0 gate, clean.
- **REGRESSION (ruling B): 9/9 atoms found + 9 det-eligible (is_cert) + hp12 single-`exp_` pinned** -> regression_ok=True,
  rolled_back=False. The 6 non-CSP dependents reproduce-by-construction (deterministic + warm-start flag is a CSP-solve
  init path disjoint from theirs); the 3 csp_* mechanism atoms covered by the warm-start mechanism (this run).
- swap-gating OK (reversible additive flag); version-marker present; can-fail self-test passes.

## Note: first run was a HARD_FAIL from MY parse bug (caught + fixed, verify-the-referent)
run_index=1 returned HARD_FAIL with n_atoms=6/det_eligible=0 -- NOT a real regression failure: my read_baseline read the
snapshot under key "atoms" but the tool emits the 9 atoms under **"pre_ship_snapshot"** (+ top-level n_atoms/all_found).
Fixed the key -> 9/9 + det-eligible -> HARD_PASS. Committed the fix; re-dispatched (run_index=2 = the HARD_PASS above).
I confirmed it by reading the actual snapshot JSON structure (not assuming).

## For your LANDED-VET (the bar you set)
- 3 csp_* reproduce + 6 dependents per-dependent eligibility (static-disjoint + determinism; det_eligible=9 confirms
  is_cert across all 9) + the 1 representative re-run is the part I'd welcome your guidance on whether the in-cell
  det-eligibility + the warm-start-mechanism reproduction suffices, or you want an explicit subprocess re-run of one
  dependent baked in (I scoped (B) per-dependent; happy to add the 1 representative subprocess re-run if you want it
  in-cell rather than as your landed-VET step).
- speedup 8.42x >= 2.0 no-recall-degrade; hp12 single-exp_; swap-gating; version-marker; run the saturation self-check
  (fbd7078f) on the speedup/recall -- it's a genuine algorithmic speedup (warm init in-basin), not by-construction.

Metrics on the remote (data/exp_csp_first_ship_v1/metrics.json, mtime current); local pull on the next sync -> your
landed-VET off the local copy. This is the Phase-1 0->1 gate.

-- Exp-Dev
