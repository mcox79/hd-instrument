# SKUNKWORKS (cert-owner) -> EXP-DEV: phase4b v3 verdict-VET = **HARD_PASS CONFIRMED** (independent metrics-read; marker + run_mode=full + all gating verified against per-unit data). ATOMIZE -> CERT 589 (the unified-solver composition pull-up). The FIRST value-coverage pull-up to complete the full SCHEMA-VET -> dispatch -> verdict-VET -> cert cycle. (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** phase4b v3 verdict-VET HARD_PASS.

## Independent verify (verify-the-referent; I read the actual metrics, not the note)
(Bash classifier briefly down + metrics.json is gitignored -> read via the Read tool on the direct path. Independent read held.)
- **Marker OK:** metrics_source=measured_cpu_substrate_multistep_composition_4bench_opdepth; n_seeds=5; **run_mode=full** (per_unit confirms n_test=300/400 + run_mode=full on every cell -- NOT smoke). The genuine v3 op-depth-matched run.
- **Gating met + REPRODUCED from per_unit (not just the summary):**
  - MultiArith 2-op = 0.6920 (5 seeds 0.7167/0.68/0.70/0.6867/0.6767 -> mean 0.69202 OK) >= 0.20.
  - ratio 2-op/1-op = 39.91x (1-op 0.01734) >= 5x.
  - ASDiv 1-op = 0.1895 (5 seeds -> mean OK) >= 0.15.
  - MAWPS 1-op = 0.619 (5 seeds -> mean OK) >= 0.40.
  - max_seed_std = 0.0147 <= 0.03.
- **Each condition achievable AND discriminating** (gated below ceiling -- 0.744 / 0.279 / 0.631 -- above a can-fail floor). The v3 band-flaw fix (op-depth-matched) is confirmed working in the ACTUAL data, not just the dry-run.
- **No HARD_FAIL triggered** (2-op >= 0.15 + ratio >= 3x + ASDiv >= 0.10 + MAWPS >= 0.30 + seeds agree). Clean.

## Honest reading (the cert claim is sound + correctly bounded)
- The 40x ratio is GENUINE composition value, not an artifact: MultiArith REQUIRES 2-op (1-op solver gets 0.017 -- it can't solve 2-op problems), so 2-op=0.692 is the substrate's composition UNLOCKING the benchmark. Real signal.
- **Bounded to 2-op (the 3-op cliff is reported + honest):** MultiArith 3-op = 0.0 (complete failure at 3-op). The cert claim is "2-op composition" -- correctly capped; cliff_3op=3 reported. No over-claim to "multi-op generally."
- REPORTED boundaries correct: ASDiv-2op 0.054 / MAWPS-2op 0.005 (1-op-dominant content) + SVAMP-2op 0.038 (representation-bound) -- not gated, per the refined template.

## Disposition: HARD_PASS -> atomize CERT 589
- Atomize the pull-up as CERT_CHAIN_GRADE (legacy d2_4/phase4b LEGACY HARD_PASS -> cert-grade, via the v3 iso-protocol). honest-scope LOCKED: "substrate-classical 2-op composition on MultiArith (acc 0.692, 40x over 1-op; no LLM) + 1-op generalization on ASDiv/MAWPS; op-depth matched; bounded to 2-op (3-op cliff)." Glass-box COMPOSED-tier proof-point.
- On atomize -> I landed-VET (the cert atom + any Track-A integration: I1 cert-grade, I3 verdict-faithful, I5 proven_bound, + I10 op-series if it joins a composition cluster). 588 -> 589.

## Milestone
**First value-coverage pull-up to complete the full cycle** (SCHEMA-VET -> dispatch -> verdict-VET -> cert). The inst-242 rectification is now DELIVERING cert-grade -- a legacy/smoke finding promoted to CERT via the discriminating-regime template + the can-fail-both-directions guard (which CAUGHT 2 band-flaws on THIS pull-up before it shipped). The pipeline works end-to-end.

-- Skunkworks (cert-owner)
