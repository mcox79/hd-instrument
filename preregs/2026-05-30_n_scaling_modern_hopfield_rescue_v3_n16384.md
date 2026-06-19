# Prereg: n_scaling_modern_hopfield_rescue_v3_n16384

**Anchor:** `n_scaling_modern_hopfield_rescue_v3_n16384`
**Queue:** remote_cpu_queue (CPU diagnostic at N=16384)
**Script:** `experiments/exp_n_scaling_modern_hopfield_rescue_v3_n16384.py`
**Date:** 2026-05-30
**Lineage:** F4 (v1: INSTRUMENTATION_FAIL no seeds; v2: INSTRUMENTATION_FAIL no seeds; v3: DIAGNOSTIC incremental construction)

## Question

At N=16384, where does the substrate construction + store + retrieve pipeline crash? v1 (116s) and v2 (21s) both produced "No completed seeds" — they crashed BEFORE the first cell-write. v3 builds the substrate incrementally and emits per-step partials so even partial failure leaves actionable diagnostic data on disk.

## Diagnostic anchor purpose

**This is a diagnostic anchor — HARD_FAIL with explicit error info IS the desired scientific outcome.** The test is meant to FIND the bug; passing all 4 steps is a bonus.

## Configuration

- N (production): 16384 (PROT-018: `_n16384` binds)
- N (smoke): 1024
- Seed (production): 7
- Seed (smoke): 17
- M sweep (production, step 4 only): `[N/8, N/4, N/2, N]` = `[2048, 4096, 8192, 16384]` (SKIP 2N where v2 likely OOM'd)
- M sweep (smoke): `[N/4, N]` = `[256, 1024]`
- N_PROBE: 200; RECALL_THRESHOLD: 0.95

## 4 diagnostic steps

| Step | Purpose | Logged on success | Logged on failure |
|------|---------|-------------------|-------------------|
| 1. construct | Build codebook + zeros W; no facts stored | codebook bytes, W bytes, RAM | error_type, error_msg, traceback, fail_mem |
| 2. one_fact | Store M=1, retrieve, check single-fact recall | success bool, recall (0/1) | same |
| 3. quarter_n | Store M=N/4=4096 facts, measure recall | success bool, recall | same |
| 4. m_sweep | 1 seed across reduced M-sweep | per-M success+recall+mem | per-M error details |

Each step writes its own `partial_metrics_<step_name>.json` via PROT-021 checkpoint helper. If step1 fails, steps 2-4 are skipped (no point continuing); step4 only runs if step1-3 all succeed.

## Pre-registered bands (HARD: set BEFORE running)

| Outcome | Trigger |
|---------|---------|
| **HARD_PASS** | All 4 steps succeed AND `max_M_at_95_recall > 0` from step 4 |
| **HARD_FAIL** | ANY step crashes WITH explicit error info (this is the desired diagnostic outcome — finds the root cause) |
| **MIDDLE_BAND** | Steps 1-3 succeed but step 4 partially fails (some M-cells crash) |

The HF verdict_msg encodes the first failing step name + error_type + error_msg (first 200 chars), so the verdict_handler can route directly to the root cause.

## Formula self-tests (verified at module import)

1. `N_FULL == 16384` (PROT-018 binding)
2. M sweep length == 4 (no 2N) and equals `[2048, 4096, 8192, 16384]`
3. `compute_verdict({all steps success})` → contains `HARD_PASS`
4. `compute_verdict({step1 fails})` → contains `HARD_FAIL` and references step1
5. `compute_verdict({step4 partial})` → contains `MIDDLE_BAND`
6. `step2_one_fact(N=1024, seed=17, cpu)` returns success=True with recall in {0.0, 1.0}

## Smoke result (2026-05-30, CPU)

- Step 1: success=True (elapsed=0.02s)
- Step 2: success=True, recall=1.0 (elapsed=0.02s)
- Step 3: success=True (elapsed=0.03s)
- Step 4: M=256 recall=1.0; M=1024 recall=1.0
- Verdict: NSCALE_R_V3_HARD_PASS (expected at smoke N=1024)
- Total elapsed: 0.16s
- Non-zero metrics; not suspect; instrumentation gate PASS

## OOM check (CPU)

- N=16384 BSC codebook (49152 * 16384 floats float32) = 3.2GB
- W = 16384 * 16384 * 4 = 1.07GB
- M=N=16384 keys = 1.07GB
- Peak (codebook + W + keys + sims matmul outputs) ~6-7GB RSS
- CPU runner desktop has plenty of RAM headroom; CPU diagnostic is the right venue (no 8GB GPU constraint)

## Timeout estimate

Formula: `ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`

- smoke_wall_s = 0.16s (4 steps at N=1024)
- FULL_N / smoke_N = 16384 / 1024 = 16
- FULL_seeds / smoke_seeds = 1 / 1 = 1 (diagnostic uses single seed)
- scaling_exp = 2.0 (matrix-multiply dominant: codebook@out, store_facts batched)
- estimate = ceil(1.5 * 0.16 * 16^2.0 * 1) = ceil(61.4) = 62s

Smoke wall is unrealistically small (0.16s) because CPU at N=1024 is fast. Real CPU work at N=16384 will be far slower. Use empirical extrapolation from the v2 wall:
- v2 at N=16384 ran 21s before crashing. Step 4 (M-sweep at full N=16384) realistically needs ~600-1800s/M on CPU per M-point; 4 M-points ≈ 2400-7200s.
- Add steps 1-3 budget (~120s).
- Apply 1.5x safety margin.

Conservative estimate: **timeout=14400s (4h)** — within the per-experiment timeout cap. Below the hard upstream-push threshold of 14400s.

## Queue routing

- remote_cpu_queue (Tier B per role contract): N=16384 CPU diagnostic is genuinely slow but no GPU dependency, frees GPU for heavier work (sparse_w M_c-beat, Op D Phase 2, GPU baseline N=8192).
- ASCII-only structurally guaranteed by stdout reconfigure block.

## Next decisions by outcome

- **HARD_PASS** (all 4 steps OK + max_M identified): rare; would lift F4 directly with v3 result; cap_map row updates.
- **HARD_FAIL** with step1 fail (codebook construction): root cause = OOM at codebook build; rescue path is N=16384 codebook chunking or kerdock truncation.
- **HARD_FAIL** with step2 fail (single-fact store): root cause = store_facts_batched OOM at N=16384.
- **HARD_FAIL** with step3 fail (N/4 facts): root cause = store-loop OOM at scale.
- **HARD_FAIL** with step4 fail (M-sweep): root cause = per-M cell crash; partial recall data still actionable.
- **MIDDLE_BAND**: some step 4 cells succeed → partial max_M observation + actionable per-M error info.
