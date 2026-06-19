# exp_dev hand-off -- research: oscillatory phase-noise scaling (Kuramoto/ReRAM capacity threshold)

## Filed-by
research sub-agent, 2026-06-02

## Trigger
Research note: d:/AI/hd-instrument/notes/research_drill_oscillatory_phase_noise_scaling_2026-06-02.md
Topic: phase-noise threshold for exponential-to-linear capacity collapse in Kuramoto-style honeycomb oscillator associative memory.

## Pause state block
Respect data/orchestrator_paused.flag. If paused, do not queue. If not paused, evaluate anchor candidates below for queue eligibility.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep grids, threshold formulas, and queue placement. No numerical bounds or grid specs are pre-committed here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
Pointer: stochastic Kuramoto simulation on n_c=5 honeycomb network
Substrate-product reading: the theoretical basin-of-attraction bound (pi/(2*n_c) approximately 0.314 rad for n_c=5) from Theorem III.2 (arXiv:2604.01469) predicts when exponential capacity holds vs collapses to linear. Empirically verifying this bound in simulation is the CHEAP DECISIVE TEST for whether the oscillator hardware angle is feasible at product scale.
Tier hint: cheap CPU simulation (< 10 min); pure stochastic ODE integration; no GPU required
Why now: the theoretical bound is now in hand from the research note; this is the first empirical check; no prior art measures this for the honeycomb topology specifically

### Anchor 2
Pointer: honeycomb Laplacian spectral gap vs. frequency-mismatch coupling requirement at N=100-1000
Substrate-product reading: the binding constraint for 1000-node scale is oscillator frequency mismatch (not per-node phase noise). The spectral gap lambda_2 of the honeycomb graph sets the minimum coupling K needed to synchronize nodes with sigma_delta_omega spread. Mapping K_required vs. N gives the fab-generation feasibility curve.
Tier hint: medium CPU (graph eigenvalue computation + stochastic sweep); ~30 min
Why now: complement to Anchor 1; needed to project the Gen 1/Gen 2 roadmap onto actual K_c numbers

---

## Context pointers
- Research note (full derivations + citations): d:/AI/hd-instrument/notes/research_drill_oscillatory_phase_noise_scaling_2026-06-02.md
- Cap_map: d:/AI/hd-instrument/data/substrate_capability_map.md (check rows for hierarchical-retrieval, non-equilibrium stat-mech)
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md
- Prior SKAH-M confirmation: d:/AI/hd-instrument/notes/ (search for skah_m or skahm)

---

## Contract
- Smoke gate required before full run
- Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds before shipping
- Use generic math terms in any external calls per feedback-query-privacy-decomposition
- ASCII-only in print()/verdict_msg per feedback-ascii-only-in-scripts
- --timeout flag required per feedback-per-experiment-timeout-required
- set -ex + python -u + stdbuf -oL + tee to remote log if dispatched remotely

## Autonomy declaration
exp_dev decides: anchor names, sweep parameter grids, threshold numerical values, queue (CPU vs GPU), ETA, and cap_map decisions post-verdict. Orchestrator does not pre-specify these.
