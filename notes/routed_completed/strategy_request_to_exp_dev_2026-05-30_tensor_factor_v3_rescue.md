# Strategy -> exp_dev routing -- 2026-05-30 -- tensor_factorized_w_envelope v3 rescue (F2 user-killed)

## Status

NOT-AUTO-DISPATCHED. Filed for orchestrator main-thread review and user next-batch decision.

## Background

`tensor_factorized_w_envelope_v2_n4096` was shipped in F-batch at commit ad30514 with intent to extend v1 envelope test (perfect ret=1.000 at M=N/8 sub-capacity) up the M-axis to test capacity-saturation behavior. Run was KILLED MID-RUN by user pause-action at ~10:30 ET. NO_METRICS reflects pause-action artifact, NOT runner crash or substrate failure.

Per dispatch context: PROT-021 `_seed_checkpoint` helper should have salvageable partials on disk at `C:\dev\hd-instrument\data\exp_tensor_factorized_w_envelope_v2_n4096\` per checkpoint design.

## Strategic context

v283 tensor-factorized W is a 🟢 candidate row at P=0.40-0.55 with explicit envelope-caveat ("FULL ENVELOPE TEST RECOMMENDED at M in {N, 2N, 4N, ~M_c} before further LIFT"). Sparse-W envelope v2 succeeded at M up to 2N (LIFT to 0.55-0.70 in v284). Tensor-factor is the orthogonal capacity-extension mechanism (low-rank vs sparse compression families); BOTH need M_c-band envelope testing to validate killer-feature capacity-extension framing.

The F2 v2 run was DESIGNED to answer this; the v2 envelope must complete (via checkpoint salvage or fresh v3 ship) to maintain co-equal pace with sparse-W.

## Task

ONE of:

**Option A: Checkpoint salvage (CHEAPEST, ~10min)**

1. Run PROT-021 checkpoint inspector against `exp_tensor_factorized_w_envelope_v2_n4096`.
2. Enumerate completed cells on disk: which (M, seed) pairs are complete vs partial.
3. If >=3 seeds at any M >= N/2 have complete cells: re-queue `tensor_factorized_w_envelope_v2_resume_n4096` with `--allow-duplicate` and `--resume-from-checkpoint` flags to fill ONLY missing cells.
4. Estimated cell coverage 50-80% salvageable depending on pause timing.

**Option B: Fresh v3 ship (FALLBACK, ~30min GPU FULL)**

1. Copy v2 script to `exp_tensor_factorized_w_envelope_v3_n4096.py`.
2. Same envelope config: M in {N, 2N, 4N, 8N} with N=4096; 5 seeds; sweep ranks r in {N/8, N/4, N/2, N}.
3. Verify pause-flag absent before ship; verify no user-pause expected in next ~30min window.
4. queue_add.sh to GPU queue.
5. REMOTE VERIFY post-ship.

## Why

Tensor-factorized W is a co-equal capacity-extension candidate to sparse-W. v2 envelope question (does tensor-factor work at M near M_c) is UNANSWERED due to interruption -- the question is open, the mechanism not refuted. Per [[feedback-rehabilitation-after-rejection]] interruption is not closure.

## Contract

- Pre-reg envelope-fail-bands per [[feedback-envelope-expansion-fail-bands]].
- Smoke gate before FULL (Option B only; Option A skips smoke since v2 partial cells already validate the design).
- Self-tests on any closed-form formulas per [[feedback-strategy-spec-formula-selftests]].
- Per-experiment `--timeout` per [[feedback-per-experiment-timeout-required]] (Option B; v2 was 30min GPU).

## Autonomy

Exp_dev decides:
- Option A vs Option B based on checkpoint salvage yield (if >=50% cells complete, prefer A).
- Whether to extend envelope past v2 ceiling (e.g., M=16N for M_c-beat test) -- if cheap enough.
- Smoke design (N=1024 or N=2048 with M=N or M=2N; very cheap).
- Queue choice (GPU FULL standard).

## NOT auto-shipping

Per user explicit no-refill directive on F-batch context (user paused then resumed; explicit pending decision on next-batch staging). Orchestrator surfaces to user.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
