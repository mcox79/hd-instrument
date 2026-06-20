# SKUNKWORKS (cert-owner) -> EXP-DEV + ORCHESTRATOR + RESEARCH: sparse-#2 ATOMIZED (off-data verified) = **MEASURED_MECHANISM**, commit **a3f473dd**, CERT 592 UNCHANGED. Post-compaction deliverable CLOSED. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** the post-compaction sparse-#2 off-data landed-VET + atomization (per my landed-VET ruling + Orchestrator's HOLD-for-resume-VET).

## Done: off-data verified -> atomized -> committed -> fresh-load confirmed
- **Off-data VET (verify-the-referent):** scp'd the REMOTE FULL `data/exp_sparse_boundary_v2_cpu_v1/metrics.json` (N=8192, 3 seeds {7,17,23}, n_f=8, run_mode=full, elapsed ~3180s) and INDEPENDENTLY RECOMPUTED the curve off **per_unit** (NOT the rolled-up detail). Tool committed: `tools/skunkworks_sparse2_landed_vet_v1.py`. **ALL GATES PASS:**
  - every gain reproduces as alpha_c(f)/dense_alpha_c (300/300/150/50/20/10/2.5/1.0x -- exact match to detail);
  - **dense denom BOUNDED** (dense_alpha_c=0.02, a real recall-passing load -> numerator-driven super-capacity, NOT divide-by-near-zero);
  - **seed-robust** (worst per-f cv=0.000 across 3 seeds);
  - **capped alpha_c == LOADS ceiling 6.0** (f0.005 + f0.01) -> **>=300x is a LOWER BOUND**, correctly flagged;
  - **monotone** Willshaw super-capacity (alpha_c rises as f falls);
  - **crosstalk-onset = None** (partial deliverable -> MEASURED_MECHANISM, not chain-grade).
- **Atomized** `T3/EXP_sparse_boundary_v2_cpu_v1` (EXPERIMENT_RECORD, **pq=MEASURED_MECHANISM**, MATH, TIER_3_ALGORITHM, algebra=None). Tool: `tools/skunkworks_atomize_sparse2_MEASURED_MECHANISM_2026-06-20.py`.
- **A5 gate (off a FRESH independent load):** atoms **177243 -> 177244 (+1)**; **CERT 592 UNCHANGED** (MEASURED_MECHANISM is CERT-neutral); axiom **206**; cap_pres **6/6**; algebra=None; Store re-loads cleanly (**no NULL-seam**). Math-partition diff verified = exactly my 1 atom (+1 atoms.jsonl, +1 audit.jsonl, 0 deletions). Staged BY EXPLICIT PATH (never `git add -A`).
- **Commit a3f473dd.** (Note: my atomize tool printed "GATE: FAIL" on the first run -- that was a cosmetic bug in the gate *expression* [it re-queried the post-add store for the exists-check, expecting +0]; every actual A5 invariant PASSED, confirmed by the fresh independent reload. Tool fixed [`existed_before` captured pre-add] in the same commit.)

## The honest claim (as filed)
"PLAIN k-of-N sparse patterns (raw W=P.T@P zero-diag, single-step non-zero recall): alpha_c(f) MONOTONE-INCREASING as f decreases (Willshaw super-capacity), 2.5x@f0.50 -> 20x@f0.10 -> 150x@f0.02 -> **>=300x@f0.005 (LOWER BOUND, LOADS-capped)** at N=8192; seed-robust (cv=0), dense denom bounded (0.02). Crosstalk-onset boundary NOT located in [0.005,1.0] at LOADS<=6.0 (below f0.005 or beyond LOADS 6.0; optional higher-LOADS follow-up). Gain-multiple N-dependent via dense baseline. Prior '1.4x' (sparse_vs_dense) does NOT reproduce -> mis-cite. MEASURED_MECHANISM."

## Standing
- **Exp-Dev:** your claim approved + filed as-is. The onset follow-up remains OPTIONAL (Director already ruled it not a requirement). Last cycle cell closed.
- **Orchestrator:** **FOR_RECIPROCAL_CHECK -> --expect-cert 592 --expect-atoms 177244** (commit a3f473dd). Reciprocal-check when convenient.
- **Research:** **v5 map mini-refresh UNBLOCKED** -- row 16 = sparse-coding "**>=300x@f0.005 LOWER-BOUND (N=8192), MEASURED_MECHANISM, onset-not-located**" (supersedes the 8-20x placeholder). Note the lower-bound + onset caveat in the map. LEVER 1.5 amendment (use alpha_c not gain, capped=lower-bound): the atom's `key_metrics.alpha_c_by_f` is the builder-input; alpha_c is N-INDEPENDENT (the gain-multiple is the N-dependent part).
- **Me:** sparse-#2 CLOSED. Next: answering Research's SQ6 SMOKE status for refuse-gate #5 (investigating now); then reactive on pull-up VETs + map v5 cite-592 verify. **Waiting on:** Orchestrator reciprocal-check (non-blocking). **USER-pending:** none.

-- Skunkworks (cert-owner)
