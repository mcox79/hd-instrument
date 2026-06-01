# strategy_request_to_exp_dev v274 — kf1_hallu_rescue_v3 Kerdock-even-log2 rescue (BSC-substitution PRIMARY)

**Filed:** 2026-05-29 (v274 verdict_handler inline strategy).
**Trigger:** kf1_hallu_rescue_v3_n8192 FAILED wall_s=2.8 = Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION (131st LABEL-VS-HONEST catch sub-flavor continuation; matches v270 124th-126th + v271 127th-128th pattern). N=8192 log2=13 (odd) hits ValueError in `make_kerdock_4coset_codebook` (lines 159-172 of `exp_wave14y_erase_kerdock_v3.py` per v270 inspection).

## TASK

Rehabilitate KF-1 N-axis multi-N replication after Kerdock-even-log2 block at N=8192. KF-1 production-scale confirmation at N=4096 5-seed × 3-M_frac (v271 v2) STANDS load-bearing; v3 v274 attempt to extend to N=8192 BLOCKED by inherited Kerdock dependency. Need a Kerdock-safe N-axis extension to validate KF-1 N-stability (mandatory promotion gate per cap_map row).

## WHY

- v271 v2 N=4096 5-seed × 3-M_frac PRODUCTION-SCALE CONFIRMATION is load-bearing for KF-1 green 65-80% row status.
- N-axis multi-N replication is the standing promotion gate (single-N row → multi-N tick promotion).
- 6 anchors already blocked at N=8192 by Kerdock-even-log2 (v270 124th-126th + v271 127th-128th + v274 131st = 6 distinct anchors so far). Recurring pattern. Rescue must address the structural cause not per-anchor reroute.

## CONTRACT (cheapest-first sequencing per [[feedback-rescue-sketch-first-sequencing]])

### (a) PRIMARY / SUBSUMPTION 0-cost — BSC-codebook substitution at N=8192

- Ship `kf1_hallu_rescue_v4_n8192_bsc` (NEW anchor name; per PROT-018 N suffix is binding contract).
- Implementation: replace `make_kerdock_4coset_codebook(N=8192)` with the existing BSC codebook path (already used elsewhere in the codebase; Kerdock-safe at any log2). No new code; redirect imports.
- Smoke gate: N=1024 BSC + 1-seed [17] + 3 M_fracs (matching v271 v2 smoke protocol).
- FULL: N=8192 BSC + 5 seeds [7,17,23,31,41] + 3 M_fracs [0.25, 0.5, 1.0] (matching v271 v2 protocol exactly so KF-1 multi-N replication is apples-to-apples vs v271 N=4096).
- ETA: SCOPE = inference-only KF-1 ratio_to_uniform + above_thresh + near_uniform; ~1-2 GPU minutes per cell × 15 cells ≈ 15-30 min GPU FULL.
- PASS criterion (pre-reg): all 15 cells above_thresh_frac=0 AND 15/15 near_uniform_mean+max=True AND mean ratio_to_uniform > 3.0 (matching v271 v2 thresholds).

### (b) CHEAP ≤15min smoke — N=16384 Kerdock-safe even-log2=14 (CONTINGENT)

- ONLY if (a) returns MIDDLE_BAND or HARD_FAIL.
- Verify GPU memory budget for N=16384 BEFORE queue_add per [[feedback-ship-before-dependency-verified]] (CAP-8/COMPA chain burned 6h via silent missing-dependency).
- Same protocol as (a) but at N=16384 with original Kerdock codebook (log2=14 even, validator passes).

### (c) MEDIUM — Structural fix to make_kerdock_4coset_codebook (LONG-TERM, NOT THIS RESCUE)

- Per v270 structural-fix candidate-d.
- Modify `make_kerdock_4coset_codebook` to GRACEFULLY DOWNGRADE to nearest-even-log2 N (pad embedding) OR have script auto-route to nearest-even-N at queue-add time.
- Filed as STRATEGY-level architectural question for next strategy cycle, NOT verdict_handler autonomy.

## AUTONOMY

Exp_dev decides:
- Anchor name (`kf1_hallu_rescue_v4_n8192_bsc` is suggested; exp_dev may rename per PROT-018 binding-contract verification).
- Sweep grid (3 M_fracs + 5 seeds suggested; exp_dev confirms vs v271 v2 protocol).
- Pre-reg fail-bands beyond the (a) PASS criterion sketched above.
- Smoke gate pass/fail interpretation.
- Queue routing (GPU per [[feedback-gpu-first-for-depth-probes]] 5-seed×15-cell ≥ GPU threshold).
- Timeout per [[feedback-per-experiment-timeout-required]] formula.

Exp_dev does NOT decide:
- Whether to ship (a) before (b); cheapest-first sequencing is binding per [[feedback-rescue-sketch-first-sequencing]].
- Whether to escalate to (c); structural fix is STRATEGY-level not exp_dev autonomy.

## NOT-AUTONOMY (strategy-level)

- Promotion of KF-1 row to multi-N tick (✅) on this rescue's pass — strategy cycle reviews multi-N evidence as a portfolio decision.
- Decision to retroactively rerun the 6 prior Kerdock-blocked anchors (v270 124th-126th + v271 127th-128th + v274 131st) once (c) lands — strategy cycle batches the Kerdock-vulnerable backlog sweep.

## REFERENCES

- v270 decision log: 6-anchor consolidated Kerdock rescue routing.
- v271 v2 production-scale confirmation (load-bearing reference for v4 protocol).
- v273 routing file overnight refill plan (this rescue is OUT-OF-CLUSTER, not part of A/B/C/D/E TIER 1/2/3/4 allocation; ship in parallel with whatever TIER capacity allows; non-blocking).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
