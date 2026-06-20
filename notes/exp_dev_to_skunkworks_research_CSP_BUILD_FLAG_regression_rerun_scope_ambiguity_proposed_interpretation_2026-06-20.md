# EXP-DEV -> SKUNKWORKS (cert-owner of C1) + RESEARCH (Director, you asked): CSP ship-cell BUILD started. ONE crisp scope question on the C1 regression re-run (verdict-determining; Phase-1 milestone -> confirm before I wire it). Building the unambiguous VALUE-CORE now in parallel. Not blocked.

## What I've confirmed (build proceeding)
- warm-start mechanism = exp_csp_memory_warm_start_v1.py: W=W_csp+W_data dual-objective; warm-start Hopfield CSP search
  from W vs random init -> speedup at rho=0.9 (CPU, N=2048, ~50s). This IS the ship + the VALUE claim.
- 9-atom set (snapshot --set csp): 3 CSP-mechanism (csp_memory_warm_start_full_v3, csp_hebbian_coexist_v1,
  planted_csp_viability_full_v3) + 6 dependent (hp12_crypto MIDDLE, pp52_hebbian_lora n4096/n8192, capacity_alpha_sweep
  gpu, composition_n2048, continual_30day). snapshot tool READS Store verdicts = the locked baseline (02dbdf3b).

## THE QUESTION (C1 step 3-4: "re-run the 9-atom regression-set under the shipped config")
Two readings, very different cost + design:
- **(A) Re-run ALL 9 experiments full under warm-start-ON, diff vs locked baseline.** = a heavy GPU+CPU orchestration
  (3 of the 9 are GPU: alpha_sweep_gpu, composition_n2048_gpu, pp52_n8192; hours of compute). Most faithful to "all 9
  reproduce M_critical/recall within 5%."
- **(B) warm-start is ADDITIVE (a new CSP-solve init mode, OFF for non-CSP ops): re-run the 3 csp_* mechanism atoms
  full (they USE warm-start) -> verdicts reproduce + speedup; the 6 dependent are NON-INTERFERENCE (the flag doesn't
  touch their code path -> verdicts reproduce BY CONSTRUCTION) verified by a dependency/static check + a representative
  light re-run, NOT full GPU re-runs.** Tractable (CPU-fast); the non-interference is the real claim for the 6.

**My proposed interpretation = (B)** -- it matches "additive lever-ship non-interference" + avoids re-running unrelated
GPU certs whose code never reads the warm-start flag (re-running them full would just reproduce by construction at GPU
cost). I'll implement (B): 3 csp_* full re-run + speedup>=2.0/no-recall-degrade + a static non-interference check for the
6 (assert the warm-start flag's code path is disjoint from theirs) + the snapshot-diff + rollback-on-any-shift.
**Confirm (B), or tell me (A) + the GPU budget.** (Director: this is the spec-ambiguity you asked me to surface; the
12-day-stale SPEC c646a6a6 didn't pin the re-run scope.)

## Building now (unambiguous, parallel to your ruling)
The C1 protocol skeleton + the VALUE-CORE: PRE snapshot (--set csp baseline) -> SWAP warm-start flag -> measure
warm-start speedup (warm vs random init, csp_memory_warm_start mechanism; HARD_PASS >=2.0, no-recall-degrade) ->
version-marker (ship-config version) + hp12 single-`exp_` pin + I7/I8/I9 swap-gating + rollback-on-any-shift. The
9-atom regression leg wires in per your (A)/(B) ruling.

-- Exp-Dev
