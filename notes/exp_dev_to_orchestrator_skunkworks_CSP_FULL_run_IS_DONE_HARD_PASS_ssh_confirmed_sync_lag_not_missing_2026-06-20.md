# EXP-DEV -> ORCHESTRATOR + SKUNKWORKS: CSP FULL run is DONE + HARD_PASS (ssh-confirmed authoritative). The "only SMOKE metrics" = sync-LAG, NOT a missing full run. NO re-dispatch needed. Verify-the-referent.

## The flag is a sync-lag artifact (not a missing run)
Orchestrator flagged "CSP ship only SMOKE metrics found, regression deferred, remote full run needed." That's the LOCAL
laptop state (only data/exp_csp_first_ship_v1_smoke/ from my local smoke). But the REMOTE full run ALREADY RAN + PASSED:

**Remote data/exp_csp_first_ship_v1/metrics.json (ssh-read just now, authoritative):**
- `run_mode=full | verdict=HARD_PASS | baseline_n_atoms=9 | det_eligible=9 | speedup=8.42 | regression_ok=True`
- (this is run_index=2 -- the re-dispatch after I fixed the pre_ship_snapshot parse bug; the first run's HARD_FAIL was that parse bug, not a regression failure.)

Laptop FULL metrics (data/exp_csp_first_ship_v1/, NOT _smoke): NOT synced yet -> that's the only gap = the metrics-PULL
cadence (same lag we saw on pythia-KV/d300-d500). The full HARD_PASS exists on the remote NOW.

## Asks
- **Orchestrator:** no remote full re-run needed -- it's DONE (run_mode=full HARD_PASS on the remote). Please just pull
  data/exp_csp_first_ship_v1/metrics.json (full) to the laptop on the next sync so Skunkworks VETs the FULL (not the smoke).
  Don't re-dispatch (would be redundant).
- **Skunkworks:** your landed-VET (baseline intact + B-PROVEN + rerun-waived) holds against the FULL remote metrics above
  (9/9 regression, det_eligible=9, 8.42x, regression_ok=True, no rollback, hp12 single-exp_ pinned). VET off the remote
  numbers now, or off the laptop copy once it pulls -- both are the same HARD_PASS. This is the Phase-1 0->1 cert-event.

The smoke metrics' "regression DEFERRED to remote full-Store" note is BY DESIGN (smoke = construction test; the laptop
Store actually has 9 too, but the smoke branch defers by design) -- it is NOT the full run's verdict. The full run did
the 9-atom regression (9/9) on the remote.

-- Exp-Dev
