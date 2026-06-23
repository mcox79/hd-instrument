# PRE-REG: cleanup_floor_M_scan_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_cleanup_floor_M_scan_v1.py`
**Anchor:** `cleanup_floor_M_scan_v1`
**Queue routing:** local_cpu_queue (numpy CPU; ~5min wall full)

## Role

META-INFORMER for cert ledger row 675:
`T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0`

Skunkworks tiered this META at MEASURED_MECHANISM (NOT chain-grade) because 3
branches remain untested. This cell closes BRANCH #2: M-scan at sigma=1.5.

NOT a chain-grade-candidate cell. Informer only -> status_log importance=MEDIUM.

## Motivation

- Parent N_DIM=512 M=200 sigma=1.5 -> argmax recall=0.023 (Shannon-floor regime).
- att1_v2_krotov_v1 at M=50 sigma=1.5 -> argmax=0.093 (4x lift over M=200).

So the Shannon-floor IS M-dependent at low M. This cell maps the M-knee.

## Cell design

Substrate-native HD codebook (random bipolar +/-1, L2-normalized; no encoder):
- N_DIM = 512 (fixed; matches parent rejection regime)
- M_sweep = [25, 50, 100, 200, 400] (under-capacity -> over-capacity)
- sigma_sweep = [1.0, 1.5, 2.0] (load-bearing high-noise regimes)
- N_EVAL = 200; seeds = {7, 17, 23}
- 1 arm only: ARGMAX_BASELINE (noise-floor characterization; not mechanism comparison)
- 9000 argmax operations total; pure numpy; <5min wall

## Decision rules (NOT HARD_PASS / HARD_FAIL bands)

This cell informs META-tiering; doesn't HARD_PASS/HARD_FAIL on its own.
Discriminator sigma = 1.5. M_LOW = 50, M_HIGH = 200.

| Decision | Trigger | META implication |
|---|---|---|
| META_DECISION_M_STRONG_DEP | recall(M=50, sigma=1.5) >= 0.30 AND recall(M=200, sigma=1.5) <= 0.05 | DOWNGRADE META framing to "9-family-at-M=200-and-up" |
| META_DECISION_M_INDEPENDENT | recall(M=50, sigma=1.5) <= 0.10 | STRENGTHEN META toward chain-grade tier (1/3 branches closed) |
| META_DECISION_KNEE_MIDDLE | between the two | ingest alpha_c-for-cleanup map as substrate-product-knowledge atom |
| HARD_FAIL | sigma=0 sanity recall < 0.99 for any (seed, M) | implementation bug (codebook L2-norm or argmax broken) |

## Sanity self-test (mandatory pre-dispatch)

- At sigma=0.0 ANY M: recall=1.000 (clean cue -> atom-recovery by construction)
- Codebook rows L2-normalized to unit norm (post-build assert)
- High-noise (sigma=20) recall <= 0.5 for any M (above 1/M random baseline)
- compute_verdict triplet (STRONG_DEP / INDEPENDENT / HARD_FAIL_SANITY) returns
  expected verdict on hand-built synthetic units (T4 / T5 / T6)
- _LLM_CALL_COUNTER == 0 after selftest (substrate-only-decode gate)

## Pre-flight discipline checklist

1. `tools/predispatch_check.py cleanup_floor_M_scan_v1` PROCEED (verified -- 0 prior landings, 0 prior atoms)
2. ASCII-only print + verdict_msg (verified locally)
3. Pre-reg note (this file) committed BEFORE dispatch (will commit before queue_add)
4. ship_name uniqueness: `cleanup_floor_M_scan_v1` is new (predispatch_check landings=0)
5. Per-seed checkpoint via `_seed_checkpoint` (write_partial_key per seed)
6. atexit + SIGTERM synthesizer to metrics.json (covers any kill mid-run)
7. REQUIRED_FIELDS verified in smoke metrics.json: verdict, verdict_msg, elapsed_s, summary

## Honest scope

- Substrate-native random bipolar codebook (NOT encoder-derived). Result probes
  the noise-floor of cosine-argmax cleanup vs codebook density at fixed N_DIM.
- N_DIM=512 only; M-dependence at other N_DIM untested in this cell.
- DOES NOT close branches #1 (N_DIM scaling) or #3 (encoder-derived keys) of the META.
- Wall <5min full; if HARD_FAIL on sigma=0 sanity, implementation bug -- not META data.

## Cites

- cert_ledger row 675 (META atom under measured_mechanism tier)
- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (att1 revival)
- att1_iterative_attractor_v2_krotov_v1 (M=50 sigma=1.5 argmax=0.093 data point)
- USER 2026-06-22 directive: "every negative -> 2x revival drill"
