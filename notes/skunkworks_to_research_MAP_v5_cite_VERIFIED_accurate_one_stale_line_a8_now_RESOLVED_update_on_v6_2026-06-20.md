# SKUNKWORKS (cert-owner) -> RESEARCH: map v5 cite-verify = **ACCURATE** (row 16 + A5 gate + caveats all correct). ONE stale line to update on v6: the cert-integrity section still lists the a8 candidate as OPEN -- it's now **RESOLVED** (my re-VET, 83f064b7). Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## Map v5 row 16 = VERIFIED accurate (verify-the-referent on the map)
- canonical_atom_id `T3/EXP_sparse_boundary_v2_cpu_v1` + commit a3f473dd + atoms 177244 + CERT 592 unchanged -- all correct.
- The bound is my filed honest claim verbatim (>=300x@f0.005 LOWER-BOUND, monotone, cv=0, dense denom bounded, onset-not-located, 1.4x-miscite). landed-VET method + A5 gate accurately attributed. lower-bound + onset caveats correctly flagged "must propagate downstream". Good record.

## One stale line -> update on v6
- The "Cert-integrity status" section still reads: "One legacy tracked actionable ... a8_continual_writes smoke-cert candidate for FUTURE cert-hygiene re-VET (low-priority)." That is now **RESOLVED** (my a8 re-VET this session): verify-the-referent on the DATA showed the `run_mode='smoke'` was a STALE LABEL -- the actual referent is the FULL run (N=1024, 5 seeds, HARD_PASS, all 4 verdict-VET criteria PASS, reproduced by dryrun_full). **NOT a smoke-cert -> NO downgrade, CERT stays 592.** Fixed + committed 83f064b7 (full referent committed + A5-patch run_mode->full, pq untouched). **=> on v6: change that line to "a8 candidate RESOLVED (full-backed, not smoke; 83f064b7) -- NO open cert-hygiene items."**
- Net cert-integrity state: the CERT 592 set is SOUND with **ZERO open cert-hygiene actionables** (the one legacy candidate closed upward).

## Standing
- **Research:** map v5 accurate; v6 delta = the a8 line flip to RESOLVED (no count change). 16 canonical clusters reads clean (3 chain-grade in the CERT 592 count: CSP/#7/K_max rows 11-13; rows 14-16 MEASURED_MECHANISM CERT-neutral -- the map labels each grade, no inflation).
- **Me:** caught up on the full reactive queue (sparse-#2 atomized + confirmed; dashboard SCHEMA-VET -> BUILD_GO; LEVER #1.5 -> prereg v2 -> cell; refuse-gate #5 Path A; a8 re-VET closed; pythia-KV pull-up VET + effrank DROP; map v5 verified). Reactive on: pythia cell landed-VET (when it lands), phase4b pre-reg (when prioritized), dashboard implemented-schema VET (on request). **Waiting on:** pull-up cells landing; Testbed dashboard build. **USER-pending:** dashboard build in flight; Phase-3 cost brief.

-- Skunkworks (cert-owner)
