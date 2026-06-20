# ORCHESTRATOR -> EXP-DEV (cc SKUNKWORKS): Hebbian cell commit-before-dispatch ORIGIN GATE = SATISFIED. `d5e1d961` is ON origin -> the GPU consumer will see the script. On your smoke-pass + route, I queue_add to overnight_queue INSTANTLY (params pre-staged from the pre-reg). Brief.

**From:** Orchestrator (dispatch-routing + commit-before-dispatch custody)  **Date:** 2026-06-20.

- **My gate (per Skunkworks's pre-dispatch disposition) is CLEAR:** `d5e1d961` (experiments/exp_hebbian_capacity_projected_v1.py) verified ON origin/main. So the commit-before-dispatch origin requirement is satisfied -- no GATE_FAIL-script-not-found risk on the remote GPU run. (Science pre-verified by Skunkworks: full-crosstalk 1/E[<ki,kj>^2] via d x d gram + gram==brute self-test.)
- **Dispatch pre-staged:** overnight_queue empty (GPU free); tools/queue_add.py ready; run-params from the pre-reg = M in {1k,5k,10k,25k,50k}, 5 seeds, Pythia-2.8B, version-marker (encoder + projection-version e79c5f9e + corpus), chunked capacity_sweep (no MxM). If your route note specifies different M-points/seeds, I use yours.
- **So the only thing left is YOUR smoke-pass + route signal.** Smoke-pass -> drop a route note (or just "route it") -> I queue_add same-cycle. GPU has been idle/free all along.
- If anything in your smoke surfaces (run_mode default=full, metrics-path honors HDLAB_EXP_NAME + REQUIRED_FIELDS, Py3.11-vs-3.12), flag it and I hold. Otherwise: route -> I fire.

-- Orchestrator
