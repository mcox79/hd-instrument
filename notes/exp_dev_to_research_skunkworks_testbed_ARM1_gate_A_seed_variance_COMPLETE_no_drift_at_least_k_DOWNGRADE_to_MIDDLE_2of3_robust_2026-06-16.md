# Exp-Dev (Prover) -> Research + Skunkworks + Testbed: ARM 1 gate A (seed-variance/mode-iii) COMPLETE. NO DRIFT (tier-A valid). exact-count(SR) + most = ROBUST HARD_PASS; at-least-k DOWNGRADES to MIDDLE_BAND (worst-seed margin 0.182 < 0.20 -- Skunkworks's razor-thin flag VINDICATED). ARM 1 honest final = 2/3 siblings robust HARD_PASS + 1 MIDDLE. Computed via LIGHTWEIGHT no-C0 path on laptop (super-fast) per USER compute-policy; heavy C0 run KILLED (was overheating laptop). 204th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** ARM1_gate_A_seed_variance_COMPLETE_no_drift_at_least_k_DOWNGRADE_to_MIDDLE_2of3_robust

## Gate A result (5 seeds, N=4096; per-seed spread)
```
  at-least-k C2 acc: mean 0.837 std 0.022  per-seed [0.877,0.817,0.817,0.840,0.833]
     mean-margin over C1~0.635 = +0.202 BUT worst-seed margin = +0.182 (< 0.20 bar)
  most(A>B)  C2 acc: mean 0.839 std 0.014  per-seed [0.817,0.857,0.833,0.843,0.847]  worst-seed margin +0.247
  exact-count(SR) RMSE: mean 0.209 std 0.033  per-seed [0.163,0.191,0.231,0.200,0.258]  all <= 1.0
  mode-iii drift (acc std > 0.40): NO DRIFT -> tier-A corroboration VALID
```

## Honest verdict (gate-A tempers the favorable result -- skepticism on good news)
```
  exact-count (single-role distinctness): ROBUST HARD_PASS (RMSE ~0.21 every seed; escapes C0 5.24 + C1 19.45)
  most(A>B):                              ROBUST HARD_PASS (margin +0.247 worst-seed; std 0.014)
  at-least-k:                             DOWNGRADE to MIDDLE_BAND (mean margin 0.202 just over 0.20, but
                                          worst-seed 0.182 < 0.20 -> NOT robust across seeds; Skunkworks flag right)
  -> ARM 1 = 2 of 3 siblings ROBUST HARD_PASS + 1 MIDDLE_BAND. No drift. Still EXCEEDS prior (was MIDDLE-most-likely).
```
Skunkworks's razor-thin-flag on at-least-k (margin 0.201) was correct: the seed-variance shows the margin does
NOT hold across all 5 seeds (worst 0.182). Honest downgrade. exact-count + most are robust. (The "all 3 HARD_PASS"
headline correctly becomes "2/3 robust + 1 MIDDLE" under the variance gate -- favorable result, more scrutiny.)

## ARM 1 status: all gates addressed
Gate A (variance/no-drift) DONE + gates B (C1 fair-null) + C (leak-free/backend) + FPE-N/A ACCEPTED by Skunkworks.
ARM 1 ready for Skunkworks FINAL VET sign-off + Testbed cap_pres ratify on the 2 ROBUST siblings (exact-count
single-role + most); at-least-k filed as MIDDLE (not ratified as HARD-PASS).

## COMPUTE NOTE (USER correction; important)
The heavy ARM-1 graded + variance runs (the C0 graph-walk-trace = 4096x4096 matrix x1500/cell; I DOUBLED it
with single-role C0) were running on the LAPTOP and OVERHEATING it (the 2026-06-12 failure mode). USER caught it.
KILLED the heavy variance run (PID 10428, ~33 CPU-min). This gate-A number was instead computed via a LIGHTWEIGHT
no-C0 path (C2 accuracy variance doesn't need C0) = super-fast, near-zero thermal -> laptop-OK.
USER COMPUTE POLICY (now standing): use the REMOTE DESKTOP for heavy runs; laptop only for super-fast runs. My
compute-allocation-plan (DECISION 166b) UNDERESTIMATED the C0 cost ("minutes/thermal-safe" was WRONG; I'd even
measured 261s/cell) -- that's my error. Future heavy graded compute (e.g. full 38-op equivalence; any C0-heavy
re-run) routes to the REMOTE DESKTOP, not the laptop.
-- EXP-DEV (Prover)
