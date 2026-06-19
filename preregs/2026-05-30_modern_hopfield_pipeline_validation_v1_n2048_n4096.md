# Pre-reg: modern_hopfield_pipeline_validation_v1_n2048_n4096

**Date:** 2026-05-30
**Anchor:** `modern_hopfield_pipeline_validation_v1_n2048_n4096`
**Script:** `experiments/exp_modern_hopfield_pipeline_validation_v1_n2048_n4096.py`
**Queue:** `remote_cpu_queue` (CPU-only by design)
**Timeout:** 43200s (12h)
**Phase:** 1 of 3 (corrected plan: local-CPU validation -> local-GPU validation -> cloud-GPU dispatch)

## Purpose

Validate the EXACT pipeline that would be sent to cloud at N=16384, but
at N=2048 and N=4096. User cited N=16384 4-attempt failure history (3
instrumentation + 1 hardware) as the cautionary tale. The discipline now
is: prove the pipeline works at small scale BEFORE cloud dispatch.

This is a PIPELINE-VALIDATION test, not a substrate-physics measurement.
The primary outcome is "does the cloud pipeline run cleanly at small N
with all measurements producing non-null metrics?" -- not "does Modern
Hopfield activate at N=4096?".

## Design (matches the cloud test verbatim)

- **Codebook:** BSC bipolar, chunked-CPU construction (reused from
  `exp_n_scaling_cpu_only_v8_n16384`, the only T3 variant that did not
  GPU-OOM at N=16384). C = N (Modern Hopfield activation regime).
- **N-levels (both run):**
  - N=2048: M sweep [256, 512, 1024, 2048, 4096, 8192, 16384] (7 cells)
  - N=4096: M sweep [512, 1024, 2048, 4096, 8192, 16384] (6 cells; 8N dropped to manage CPU time)
- **Seeds:** [7, 17, 23] (3 seeds)
- **Per-cell-seed checkpoint:** PROT-021 via `_seed_checkpoint`.

## Measurements per (N, M, seed) cell

1. Standard recall (N_PROBE=100)
2. KF-1 spurious firing rate (50 unseen-key probes; threshold 0.5)
3. KF-2 max edit isolation (8 edits on probe-disjoint facts; 80 probes)
4. Deletion-cert audit chain (16 ops; SHA-256; +1 tamper-test that MUST trip)
5. Path D multi-hop accuracy (depth=5, K=100, 32 starts)

Plus pipeline-correctness: did each measurement complete? non-null?

## Pre-registered bands (PIPELINE-validation criterion)

| Outcome | Criterion |
|---------|-----------|
| `PIPELINE_HARD_PASS` | All cells at BOTH N values produce non-null metrics for every measurement AND deletion-cert validates AND tamper-test trips on every cell AND no anomaly patterns (all-zero/all-one recall, constant kf2) |
| `PIPELINE_HARD_FAIL` | Any cell crashes (RuntimeError, MemoryError) OR any cell produces a null metric where one is expected OR audit chain breaks OR all recall identically 0.0 |
| `PIPELINE_MIDDLE_BAND` | Pipeline completes but anomalies (e.g. all recall = 1.0 suggesting M sweep does not exercise overload; constant KF-2 across cells) -- investigate but cloud-dispatch is still risky |

## Smoke result (recorded 2026-05-30)

- N_SMOKE=512, 1 seed [17], M sweep [64, 128, 256, 512, 1024, 2048, 4096] = 7 cells.
- Wall: 1.1s.
- Verdict: `PIPELINE_HARD_PASS` ("PIPELINE_VALID: n_total=7 n_success=7
  n_non_null=7 n_crashed=0 cert_all_valid=True -- cloud-ready at N=[512]")
- Recall behavior: 1.0 -> 0.09 as M sweeps from N/8 to 8N; consistent
  with overload theory.
- KF-2 max_iso: 0.0 (under-loaded cells) -> 1.0 (overloaded cells).
- Path D: 0.0 (sparse-relation cells) -> 1.0 (dense-relation cells).
- Cert chain validated in every cell (tamper-test tripped on every cell).
- All_non_null = True for every cell.

## Effect-size / walk-back gate

Not applicable. This is an instrumentation gate, not an effect-size
comparison. The HARD_PASS is binary: does every measurement produce a
non-null number?

## Timeout estimate

User-specified: 43200s (12h). Per role-contract user spec.

Internal validation: smoke at N=512, 1 seed, 7 cells = 1.1s. FULL at
N=2048+N=4096, 3 seeds, 13 cells. Approximate scaling:
  - cell-time at N=4096 vs N=512 grows by ~N^2 (~64x) at the largest M
    due to W = N x N matrix store.
  - cell-count: (7 + 6) / 7 = ~1.9x
  - seed-count: 3x
  - Combined upper bound: 1.1 * 64 * 1.9 * 3 = ~400s + headroom.
  - 12h user-spec is paranoid-conservative; honored.

## OOM pre-check

- W at N=4096 = 16384 * 16384 / 4 bytes float32 = N/A. Actually
  N=4096: W = 4096 * 4096 * 4 = 67 MB. OK.
- Codebook at N=4096 C=4096: 4096 * 4096 * 4 = 67 MB. OK.
- N=2048 cases all smaller. OK.
- Peak RSS budget: 12 GiB; far above expected ~150-200 MB working set.

## Dependencies verified

- `experiments/_seed_checkpoint.py` exists
- Chunked codebook construction code is self-contained inline (copy of
  v8 logic; no import dependency)
- No external Research/cap_map deliverables required (this is a pipeline
  smoke; the substrate behavior is secondary)

## PROT-018

Dual-suffix `_n2048_n4096`. Validator extracts suffix-N = 4096 (last
`_n<NUM>` token). Script asserts `N_PHASE1_A == 2048` and
`N_PHASE1_B == 4096` and has bare `N = 4096` assignment. Both 2048
and 4096 are run in FULL mode.

## What happens after this anchor lands

- If `PIPELINE_HARD_PASS`: cloud-dispatch at N=16384 is unblocked.
  T3 v8 N=16384 CPU-only run (currently in flight or completed) gains
  validation credibility. Phase 2 (local GPU validation at N=4096 or
  N=8192) becomes the next gate.
- If `PIPELINE_HARD_FAIL`: cloud dispatch BLOCKED. Bug must be fixed
  in the local pipeline first. Same code path runs on cloud -- fixing
  it here fixes it everywhere.
- If `PIPELINE_MIDDLE_BAND`: investigate pattern (constant KF-2, all
  recall = 1.0, etc.) before cloud dispatch.
