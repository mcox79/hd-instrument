# PRE-REG: cleanup_floor_N_DIM_scan_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_cleanup_floor_N_DIM_scan_v1.py`
**Anchor:** `cleanup_floor_N_DIM_scan_v1`
**Queue routing:** local_cpu_queue (numpy CPU; <10min wall full)

## Role

META-INFORMER for cert ledger row 675:
`T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0`

Skunkworks tiered this META at MEASURED_MECHANISM (NOT chain-grade) because 3
branches remain untested. This cell closes BRANCH #1: N_DIM-scan at M=200 sigma in
{1.0, 1.5, 2.0}.

- Branch #2 (M-scan) just closed: META_DECISION_M_INDEPENDENT at sigma=1.5
  (cleanup_floor_M_scan_v1).
- Branch #3 (learned-encoder keys) remains open.

NOT a chain-grade-candidate cell. Informer only -> status_log importance=MEDIUM.

## Motivation

Hypothesis (concentration of measure): in higher N, random vectors are
nearer-orthogonal AND per-direction noise contribution to similarity scales as
1/sqrt(N). So a naive N_DIM lift should raise argmax recall mechanically.

Prior data:
- ENC1 cell tested N=4096 at M=200 only and ARM_DENSE_N4096 was 0.027
  (still below HARD_PASS=0.20).
- Parent N_DIM=512 M=200 sigma=1.5 -> argmax recall=0.023 (Shannon-floor regime).

This cell extends the sweep to N=8192 and N=16384 at M=200 to either find the
N-knee or strengthen the META further.

## Cell design

Substrate-native HD codebook (random bipolar +/-1, L2-normalized; no encoder):
- M = 200 (fixed; matches parent rejection regime)
- N_DIM_sweep = [512, 1024, 2048, 4096, 8192, 16384]
- sigma_sweep = [1.0, 1.5, 2.0] (load-bearing high-noise regimes)
- N_EVAL = 200; seeds = {7, 17, 23}
- 1 arm only: ARGMAX_BASELINE (noise-floor characterization; not mechanism comparison)
- 18 (N_DIM, sigma) cells x 3 seeds = 54 argmax operations + 6 sanity = 60 ops total
- Pure numpy; largest cell is N=16384 M=200 (200,16384) @ (16384,200) matmul
- <10min wall total

## Decision rules (NOT HARD_PASS / HARD_FAIL bands)

This cell informs META-tiering; doesn't HARD_PASS/HARD_FAIL on its own.
Discriminator sigma = 1.5. N_DIM_HIGH_A = 8192, N_DIM_HIGH_B = 16384.

| Decision | Trigger | META implication |
|---|---|---|
| META_DECISION_N_DIM_DEPENDENT | recall(N=8192, sigma=1.5) >= 0.20 OR recall(N=16384, sigma=1.5) >= 0.20 | DOWNGRADE META framing to "M=200 at N=512 specific" |
| META_DECISION_N_INDEPENDENT | recall(N=16384, sigma=1.5) < 0.10 | STRENGTHEN META toward chain-grade tier (2/3 branches closed; only encoder-keys remains) |
| META_DECISION_N_KNEE_MIDDLE | recall(N=16384, sigma=1.5) in [0.10, 0.20) | ingest recall-vs-N-DIM map as substrate-product-knowledge atom |
| HARD_FAIL | sigma=0 sanity recall < 0.99 for any (seed, N_DIM) | implementation bug (codebook L2-norm or argmax broken) |

## Sanity self-test (mandatory pre-dispatch)

- At sigma=0.0 ANY N_DIM: recall=1.000 (clean cue -> atom-recovery by construction)
- Codebook rows L2-normalized to unit norm (post-build assert)
- High-noise (sigma=20) recall <= 0.5 for any N_DIM (above 1/M random baseline)
- compute_verdict triplet (N_DIM_DEPENDENT / N_INDEPENDENT / HARD_FAIL_SANITY) returns
  expected verdict on hand-built synthetic units (T4 / T5 / T6)
- _LLM_CALL_COUNTER == 0 after selftest (substrate-only-decode gate)

## Pre-flight discipline checklist

1. `tools/predispatch_check.py cleanup_floor_N_DIM_scan_v1` PROCEED (verified -- 0 prior landings, 0 prior atoms)
2. ASCII-only print + verdict_msg (verified locally)
3. Pre-reg note (this file) committed BEFORE dispatch (will commit before queue_add)
4. ship_name uniqueness: `cleanup_floor_N_DIM_scan_v1` is new (predispatch_check landings=0)
5. Per-seed checkpoint via `_seed_checkpoint` (write_partial_key per seed)
6. atexit + SIGTERM synthesizer to metrics.json (covers any kill mid-run)
7. REQUIRED_FIELDS verified in smoke metrics.json: verdict, verdict_msg, elapsed_s, summary

## Honest scope

- Substrate-native random bipolar codebook (NOT encoder-derived). Result probes
  the noise-floor of cosine-argmax cleanup vs vector dimensionality at fixed M=200.
- M=200 only; N_DIM-dependence at other M untested in this cell (but M-INDEPENDENT
  result from branch #2 suggests robust extrapolation).
- DOES NOT close branch #3 (encoder-derived keys) of the META.
- Wall <10min full; if HARD_FAIL on sigma=0 sanity, implementation bug -- not META data.

## Cites

- cert_ledger row 675 (META atom under measured_mechanism tier)
- `preregs/2026-06-23_cleanup_floor_M_scan_v1.md` (branch #2 prereg)
- cleanup_floor_M_scan_v1 (branch #2 result: META_DECISION_M_INDEPENDENT)
- ENC1 ARM_DENSE_N4096 = 0.027 at M=200 sigma=1.5 (prior data point)
- USER 2026-06-22 directive: "every negative -> 2x revival drill"; this is the
  same META hardening discipline applied to substrate-side N-DIM scaling.
