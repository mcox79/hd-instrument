# exp_dev -> queue: Cap 12 ✅ E1 + E2 STRESS anchors (2026-05-24)

**Source**: orchestrator silent_idle emergency refill post-v175 promotion. verdict_handler pre-registered three stress gates per [[feedback-envelope-expansion-fail-bands]]; E1 + E2 ship now (E3 deferred — Paley already PERFECT_ISOMETRY kappa_n=0, picking a 5th appropriate family needs research thought).

**Pause flag**: ABSENT at dispatch time (verified via `ls data/orchestrator_paused.flag`).

**Routing schema**: Schema B (markdown table; parsed by dispatch.py `parse_queue_entries`).

| queue            | name                                     | script                                                       | prereg                                                          | timeout(s) |
|------------------|------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_mp_ks_noisy_substrate_v1          | experiments/exp_wave14_mp_ks_noisy_substrate_v1.py           | preregs/2026-05-24_wave14_mp_ks_noisy_substrate_v1.md           | 3600       |
| overnight_queue  | wave14_interp_family_N16384_v1           | experiments/exp_wave14_interp_family_N16384_v1.py            | preregs/2026-05-24_wave14_interp_family_N16384_v1.md            | 10800      |

## Per-anchor brief

**Anchor E1 — wave14_mp_ks_noisy_substrate_v1 (HIGH)**: Cap 12 ✅ E1 STRESS. Reuse the v175 tau-robustness anchor design but inject per-entry sign-flip noise (eta=0.10) into the codebook BEFORE MP-KS evaluation. 5 codebooks × 3 tau × N=1024 × 5 seeds. Tests whether the production-customer claim survives realistic depolarization noise. ETA 30-45 min, remote_cpu_queue. **HARD PASS**: >=4/5 at EACH tau under eta=0.10. **HARD FAIL**: 0/5 at ANY tau (Cap 12 reverts to 🟢). **MIDDLE BAND**: 1-3/5 at one or two tau values (✅ stays with noise-sensitivity annotation).

**Anchor E2 — wave14_interp_family_N16384_v1 (HIGH)**: Cap 12 ✅ E2 STRESS. Cross-family AMP-error predictor N-scaling: {Kerdock, SRHT, Hadamard} × {1024, 4096, 16384} × 5 alpha × 5 seeds = 225 (family, N, alpha, seed) tuples. Tests whether the v175 rho >= 0.700 finding survives to customer-scale N=16384, or was an N=1024 finite-N artifact. ETA 60-120 min, **overnight_queue (GPU)** per [[feedback-gpu-first-for-depth-probes]] — depth probe with N=16384 SVD and multi-cell sweep. **HARD PASS**: rho >= 0.50 at N=16384 on ALL 3 families AND max VAMP rel-err < 0.20. **HARD FAIL**: rho < 0.30 at N=16384 on ANY family (Cap 12 reverts to 🟢 with N-bound annotation). **MIDDLE BAND**: rho in [0.30, 0.50) at N=16384 on one family (✅ stays with N-scaling annotation).

## Smoke results

- E1: N=64 / 1-seed / 2-codebook (iid_gauss + srht) under eta=0.10. Self-test 9/9 passed. Smoke verdict INCONCLUSIVE via "missing codebooks" branch (expected — smoke uses only 2 of 5). At N=64 even iid_gauss got mis-routed (small-N noise sensitivity); full N=1024 is the discriminating run. Produced valid metrics.json with `eta=0.10` field.
- E2: N=64 / 1-seed / 2-family (srht + hadamard) × 3 alpha. Self-test 9/9 passed. Smoke verdict INCONCLUSIVE via "no N=16384 cells" branch (expected — N=64 smoke is structural only). Produced valid metrics.json with rho_per_family_N at N=64.

Both scripts include:
- `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top.
- env-var-driven `HDLAB_EXP_NAME` output directory.
- atomic `write_metrics` (`.tmp` + rename).
- Self-test runs at start of `run_main` / `run_smoke`.

## Kerdock t=7 N=16384 dependency (relevant to E2)

PRIMITIVE_POLY registry verified locally:
- t=5 (N=1024): polynomial 0b100101, codebook shape (4096, 1024) — VERIFIED.
- t=6 (N=4096): polynomial 0b1000011, codebook shape (16384, 4096) — VERIFIED.
- t=7 (N=16384): polynomial 0b10000011 in registry (patched in earlier this session per `notes/exp_dev_to_queue_emergency_refill_batch_3_2026-05-23.md` line 54). Local cold-build at N=16384 deferred to remote runner (memory + time). Earlier patch session SCP'd t=7 entry to remote BEFORE ship; assumed still on remote `experiments/exp_wave14y_erase_kerdock_v3.py`.

**Risk**: if remote `exp_wave14y_erase_kerdock_v3.py` lacks the t=7 entry, E2 fails at the first Kerdock@N=16384 cell with `ValueError: No primitive polynomial registered for GF(2^7)`. Mitigation: queue note flags this dependency; if E2 fails on this error, exp_dev re-patches remote.

## Pipeline implications

- Remote CPU queue: +1 (E1).
- Overnight queue: +1 (E2 on GPU).
- Queue-depth invariant per [[feedback-pipeline-pacing]] satisfied: depth >= 1 ahead on both queues for ~60-120 min.
- Last verdict 4m ago (INTERP_FAMILY_RM_PASS); orchestrator silent-idle watchdog triggered this emergency refill.

## Honest framing per [[feedback-no-smoke]]

These are STRESS tests of the Cap 12 ✅ promotion — designed to find the boundary, not to pad the claim. Both are real envelope-expansion gates with PASS, FAIL, and middle bands committed verbatim BEFORE running. If E1 fails, Cap 12 reverts to 🟢 clean-only. If E2 fails, Cap 12 reverts to 🟢 N-bound. Both are real risks: the v175 promotion was at threshold (rho=0.700 borderline); finite-N or noise-fragility are the two most plausible failure modes.

E3 deferred per dispatch note: Paley codebook has PERFECT_ISOMETRY kappa_n=0 at v174, so adding it as a 5th family would not discriminate (the predictor expects kappa_n divergence; a perfect-isometry family is a degenerate test). Picking an appropriate 5th family needs research thought rather than a quick-pick. Strategy / research can take this up post-E1/E2 verdict.

## PROT compliance

- Pause flag CLEARED (verified pre-dispatch).
- Both scripts: stdout reconfigure block at top; structural encoding handled per [[feedback-ascii-only-in-scripts]] OBSOLETED.
- Both preregs: HARD PASS / HARD FAIL / MIDDLE BAND verbatim.
- Formula self-test cells per [[feedback-strategy-spec-formula-selftests]]: 9 cells each = 18 total.
- Background execution per [[feedback-no-blocking-runs]].
- 2 status_log entries written (HIGH x2).
- Decision log appended via `tools/orchestrator/append_decision_log.py`.
