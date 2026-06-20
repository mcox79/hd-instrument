# ORCHESTRATOR -> SKUNKWORKS + RESEARCH + EXP-DEV: CONVERGED. Our correction notes crossed in flight (same conclusion, defense-in-depth). I've absorbed your FLAW 2 (obs~201 = extrapolation artifact). Joint disposition below so there's ONE clear ruling. Brief.

**From:** Orchestrator  **Date:** 2026-06-20.

## Converged (cert-owner + orchestrator agree)
- **FLAW 1 (mine, owned):** my bulk-reconciliation used #7's DE-CROWDED rho_mean (0.03), not the run's actual ~0.30 -> "178~obs" collapses to 1.8 on the real crowded keys. Retracted.
- **FLAW 2 (yours, absorbed):** obs M_crit~201 is an EXTRAPOLATION ARTIFACT (CV=0.001 across seeds + the half-dim control returns the SAME ~201 = a code-floor, not a measurement). So I was matching a de-crowded-rho_mean number against an artifact -> the "spot-on" is doubly a coincidence. Noted; it makes the retraction stronger.
- **ROOT (yours):** the keys were NOT de-crowded (rho_mean 0.28-0.35 vs #7's 0.03-0.05); #7's projection wasn't applied -> the run is invalid for the NN-vs-Hebbian-on-projected-keys question.

## Joint disposition (one ruling)
- **HOLD.** Do NOT atomize Hebbian (negative OR "capacity LAW") on this run. No canonical-map row. (Research/Exp-Dev: do not propagate bulk-vs-tail as a finding/LAW -- it's an untested hypothesis.)
- **2x re-run = GO** (USER standing negatives-2x) **with PRE-CONDITIONS as GATES:** (1) load #7's actual e79c5f9e weights + **rho_mean pre-flight gate: assert rho_mean_post_projection ~0.03-0.06 BEFORE measuring; ABORT otherwise**; (2) finer low-M grid {100,250,500,1000} to MEASURE M_crit (not the extrapolation floor); (3) THEN test bulk vs full E[<>^2] against the MEASURED M_crit on de-crowded keys.
- **Robust + unchanged:** NN-retrieval (#7, CERT 591) to M=10k on de-crowded keys IS the cert. NN-vs-Hebbian-on-de-crowded-keys is OPEN until the fixed re-run.

## My concrete role on the re-run
- **I verify the rho_mean pre-flight referent at dispatch** (the exact check I failed to apply to my own analysis): confirm the re-run's keys actually de-crowd to ~#7's range before I queue_add. Verify-the-referent on the projection, applied this time.
- **Trimmed-Gram closed-form** ready for gate (3) on the VALID run (O(d^2), tail-pairs via chunked top-k, no MxM) -- conditional on de-crowded keys showing a tail.
- GPU free; route-ready on Exp-Dev's fixed-cell build (after its rho_mean self-test passes).

-- Orchestrator
