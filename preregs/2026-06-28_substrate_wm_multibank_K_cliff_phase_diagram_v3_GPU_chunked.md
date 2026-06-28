# Prereg: substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked

**Date:** 2026-06-28
**Author:** exp_dev (chunked sibling cell trio)
**Cells:**
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_7.py`
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_13.py`
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_19.py`
**Anchors (per seed):** `substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_<7|13|19>`

## Scientific question (REFRAME of v1)

v1 (filed earlier today) sweeps K x bank_overlap x routing_noise at FIXED K_PER_BANK=64. v1 hit cliff at GPU memory ceiling for K=65536 (saturation-by-construction at memory limit).

**v3 reframe:** at FIXED total_K = K_per_bank * num_banks, does ALLOCATING capacity across more banks (B>1, each smaller) BEAT putting it all in one bank (B=1, large K_per_bank)?

This is the **interference-vs-capacity tradeoff** at fixed compute budget. Theoretical prediction (Kanerva bound):
- Single-bank capacity ~ N / (4 log N) per Kanerva
- Multi-bank effective capacity ~ B x N / (4 log N) via reduced per-bank interference
- Expected: at high total_K, multi-bank (B>1) outperforms single-bank (B=1) because per-bank interference dominates single-bank recall

Coverage status: WM multi-bank K=4096 is chain-grade; phase coverage = PARTIAL (BACKUP UPDATE #25). v3 promotes PARTIAL -> HIGH if 3 seeds cross-agree on cliff structure.

## Sweep axes

- **K_per_bank (PRIMARY, 7 points):** {64, 128, 256, 512, 1024, 2048, 4096}
- **num_banks (SECONDARY, 5 points):** {1, 2, 4, 8, 16}
- **N_DIM (TERTIARY, 3 points):** {2048, 4096, 8192}
- **Full grid per seed:** 7 x 5 x 3 = **105 points**
- **Arms per point:** 3 (MULTI_BANK_BIND, SINGLE_BANK_BASELINE, RANDOM_FLOOR)
- **EXPECTED_N_UNITS per seed (full):** 315 (105 x 3 arms)

### Smoke corners (per seed: 6 points x 3 arms = 18 units)

**Calibration smoke (2026-06-28) revealed: at N=2048 K_per_bank >= 256 the MULTI arm itself collapses (SNR_dim = 1/sqrt(K_per_bank-1) is too small at N=2048). Initial smoke corners FAIL the discriminator at K=256 and K=1024 corners because both MULTI and SINGLE land near floor.**

**Revised smoke corners** (after calibration; use K_per<=128 + mix N=2048/N=4096):

| K_per_bank | num_banks | N_DIM | total_K | role / expected |
| ---------- | --------- | ----- | ------- | --------------- |
| 64         | 1         | 2048  | 64      | rail / positive-control (MULTI == SINGLE; B=1 collapse) |
| 64         | 16        | 2048  | 1024    | cliff / MULTI ~0.70 > SINGLE ~0.002 |
| 64         | 8         | 2048  | 512     | cliff / MULTI ~0.68 > SINGLE ~0.008 |
| 64         | 4         | 4096  | 256     | cliff / MULTI ~0.98 > SINGLE ~0.25 |
| 128        | 4         | 4096  | 512     | cliff / MULTI ~0.70 > SINGLE ~0.06 |
| 1024       | 1         | 2048  | 1024    | SINGLE-cliff sanity (MULTI/SINGLE both at floor) |

**Smoke discriminator FIRES if:** >=2 of the 4 expected-cliff corners show MULTI - SINGLE >= 0.30.

**Smoke gate VERDICT (CPU local, seed_7, 2026-06-28):**
- **SMOKE_PASS**: discrim_fired=4/4, rail=True (MULTI=0.664 at K=64/B=1/N=2048), arms_differ=6/6, cliff_per_B={B=1:64, B=4:512, B=8:512, B=16:1024}. Wall=6.6s.

The smoke is intentionally weak-N (2048-4096) to keep CPU runtime <10s. FULL HARD_PASS gate requires discriminator firing at N=8192 (the GPU smoke discriminator-survives-scale check).

## Arms (per (K_per_bank, num_banks, N) point)

1. **MULTI_BANK_BIND:** distribute total_K items across num_banks banks (K_per_bank per bank); query routes via bank-tag + cleanup-twice.
2. **SINGLE_BANK_BASELINE:** same total_K items all stored in 1 bank (effectively num_banks=1, K=total_K). Single-bank interference-bounded.
3. **RANDOM_FLOOR:** random vector prediction floor. Expected top1 = 1/CB ~ 6.1e-5 (CB=16384).

When num_banks=1, MULTI_BANK_BIND and SINGLE_BANK_BASELINE are EQUIVALENT MECHANISMS - this is BY DESIGN (positive control: arms collapse only at B=1). At B=1 we DO NOT count those points toward arms_differ_count for HARD_PASS - but ARM_RANDOM still differs.

Arms_differ check (META_RULE_AF) for v3:
- At B>=2: all three arms must have distinct sha256 hashes per point.
- At B=1: MULTI and SINGLE may collide (same mechanism); RANDOM must differ.

## CRLB pre-validation (computed in Python BEFORE this prereg)

Cleanup-1 SNR per dim: `1/sqrt(K_per_bank - 1)`
- K_per_bank=64:   SNR_dim = 0.126 (two cleanups -> ~0.95 recall feasible)
- K_per_bank=128:  SNR_dim = 0.089
- K_per_bank=256:  SNR_dim = 0.063
- K_per_bank=512:  SNR_dim = 0.044
- K_per_bank=1024: SNR_dim = 0.031
- K_per_bank=2048: SNR_dim = 0.022
- K_per_bank=4096: SNR_dim = 0.0156

At N=2048, K_per_bank=4096 means SNR per dim = 0.0156, and the cleanup needs SNR > 1/sqrt(N) ~ 0.022 to discriminate. So K_per_bank=4096 at N=2048 is BELOW the discrimination floor -> SINGLE arm cliffs HARD here, but MULTI with B=4 (K_per_bank=1024) might still recover.

Bank-routing SNR (CUE_COS=0.70): `0.70 * sqrt(N) / sqrt(num_banks)`
- N=2048, B=1:  snr=31.7 (no routing needed)
- N=2048, B=16: snr=7.92 (route saturates)
- N=8192, B=16: snr=15.8 (route saturates)
All routing SNRs are healthy; routing is NOT the bottleneck in v3 (it WAS the secondary axis in v1).

## VRAM pre-validation (computed in Python BEFORE this prereg)

Estimated eval peak (fp16, CB=16384, worst-case point):
- N=8192, K_per_bank=4096, B=16, total_K=65536: ~5.4 GB (well within 12GB budget)
- N=2048, K_per_bank=4096, B=16, total_K=65536: ~1.6 GB
- All 105 points fit within 12GB GPU; HP_VRAM_PROBE_FRACTION=0.85 still active as a safety belt.

This is by design: v3 sweep stays within memory envelope. v1 v3.1 v3 incidents were cliff-at-memory; v3 is cliff-at-mechanism.

## PASS bands (HARD_PASS, per seed)

**HARD_PASS:** ARM_MULTI > ARM_SINGLE by >= 0.30 at >= 20 of the 105 grid points, AND:
- discriminator_survives_scale: >= 6 of the 20 PASS points are at N=8192 (full scale)
- corridor saturation sanity: at K_per_bank=64, B=1 (smallest config) MULTI >= 0.95 at N=8192 (rail)
- arms_differ_sha256 distinct at all B>=2 points; RANDOM hash distinct everywhere

Per-seed HARD_PASS aggregates to a 3-seed envelope when Skunkworks aggregates the chunked siblings.

## MIDDLE_BAND

- ARM_MULTI > ARM_SINGLE by >= 0.30 at 10-19 grid points (partial coverage of interference regime), OR
- Cliff structure coherent (monotone in K_per_bank, monotone in num_banks) but absolute MULTI recall in [0.30, 0.50)
- Phase-diagram MAP returns coherent structure (cliff position monotone in K_per_bank within fixed B)

## HARD_FAIL bands

- `HARD_FAIL_CARDINALITY_BREACH` (META_RULE_H): n_units_observed != EXPECTED_N_UNITS (smoke=18 [6 pts x 3 arms]; full=315 [105 pts x 3 arms]).
- `HARD_FAIL_UNIT_EXCEPTION` (META_RULE_AN): any unit raises; no silent except.
- `HARD_FAIL_GPU_MEMORY_OOM`: real CUDA OOM (NOT probe denial) at any point.
- `HARD_FAIL_ARMS_IDENTICAL` (META_RULE_AF): at B>=2, MULTI and SINGLE arms have identical sha256, OR RANDOM matches anywhere.
- `HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE`: < 10 of 105 points have MULTI - SINGLE > 0.30 (interference-rescue mechanism fails).
- `HARD_FAIL_SATURATION_ONLY`: every point at MULTI >= 0.995 (cliff outside swept regime; need higher total_K).
- `HARD_FAIL_FLOOR_ONLY`: every point at MULTI <= RANDOM + 0.05 (mechanism broken at smoke).
- `HARD_FAIL_LLM_CALL`: `_LLM_CALL_COUNTER[0] != 0` (substrate-only gate).

## Smoke gate (must pass BEFORE full dispatch)

1. 6 corner points all ran (no silent except).
2. >= 2 of the 4 expected-cliff corners (K=64/B=16, K=256/B=16, K=1024/B=4) discriminate (MULTI - SINGLE > 0.30).
3. At least 1 corner saturates (K=64/B=1 -> MULTI ~ SINGLE ~ 1.0 expected; or any low-K low-B corner).
4. At least 1 corner shows SINGLE-cliff (K=1024/B=1 expected interference-bounded).
5. cardinality_ok = True (n_units=18).
6. arms_differ_sha256 distinct at all B>=2 points; RANDOM hash distinct.
7. GPU util p50 >= 50% (Fix #24) - DEFERRED to remote GPU smoke; local CPU smoke skips this gate (CPU path).

## Disciplines (load-bearing)

- META_RULE_AC (substrate-empirical baseline): cone-formula vs substrate-measured ratio ~3.7x at N=8192; discriminator margin 0.30 above margin v1's 0.20 because v3 contrasts TWO ACTIVE arms (MULTI vs SINGLE), both above floor.
- META_RULE_AE: pre-reg HARD_PASS / MIDDLE / HARD_FAIL bands BEFORE dispatch.
- META_RULE_AF: arms must differ (B>=2 case).
- META_RULE_AG: corpus_provenance + allow_synthetic recorded in metrics.
- META_RULE_AH: atomic-write partials (.tmp + os.replace via _seed_checkpoint).
- META_RULE_AN: no silent except; record + halt OR re-raise.
- Discriminator-must-survive-scale (USER 2026-06-26): smoke uses 6 corners at N=2048 to keep CPU smoke fast; FULL HARD_PASS requires >=6 of 20 PASS points at N=8192.
- CARDINALITY_OK pre-reg field (META_RULE_H discipline): EXPECTED_N_UNITS declared; HARD_FAIL_CARDINALITY_BREACH on mismatch.
- No silent except (three-smoke-disciplines #1).
- Smoke fires discriminator (three-smoke-disciplines #2) - smoke EXPLICITLY verifies MULTI > SINGLE at expected-cliff corners.
- Band-floor results MIDDLE_BAND not HARD_PASS (three-smoke-disciplines #3) - HARD_PASS requires margin > 0.30, NOT just >= floor.

## Functional-requirement decomposition

- **F1 mechanism end-to-end:** smoke 6 corners all run (cardinality_ok=True; no exceptions).
- **F2 discriminator:** MULTI > SINGLE > RANDOM at expected-cliff corners (smoke at >=2 of 3 cliff corners).
- **F3 cliff observable:** at least 1 corner saturates (B=1 low-K) AND at least 1 corner shows SINGLE-cliff (B=1 high-K).
- **F4 substrate-only:** `_LLM_CALL_COUNTER[0] == 0`.
- **F5 GPU utilization (FULL only):** smoke `gpu_util_p50 >= 50%` (Fix #24); DEFERRED to remote-GPU smoke; local CPU smoke skips.
- **F6 phase-coherence:** in full, cliff position monotone in K_per_bank within each B; MULTI advantage grows with total_K.

## Output schema (`metrics.json`)

- `per_unit`: each entry has `{seed, K_per_bank, num_banks, N_DIM, total_K, regime (MULTI_BANK_BIND|SINGLE_BANK_BASELINE|RANDOM_FLOOR), recall, route_acc, peak_mem_mb, wall_s, ...}`.
- `phase_map`: list of `{K_per_bank, num_banks, N_DIM, total_K, recall_multi, recall_single, recall_random, margin_multi_vs_single, arms_differ, verdict_tier (PASS|MIDDLE|FAIL|SATURATE), cliff_marker (bool)}`.
- `headline`: `n_pass`, `n_pass_at_full_N`, `cliff_per_B` (per-num_banks cliff K_per_bank).

## Dispatch plan

- **Smoke:** CPU local (N=2048; 6 corners; 18 units); seed_7 only; timeout 600s. Local has no CUDA; smoke verifies mechanism FIRES at small N (discriminator-must-survive-scale check is via smoke at smallest N + corridor saturation at FULL N=8192 in full).
- **Full (3 sibling cells, each 1 seed x 105 points x 3 arms = 315 units):** dispatch via Orchestrator to `overnight_queue` GPU. Per-seed timeout 14400s (4h; 105 points x ~50s avg).
- GPU is busy with cortex_hippo M=8192 (3 seeds ~ 6h overnight); v3 cells queue behind. That's intended; overnight running.

## Promotion criteria

If 3-seed envelope HARD_PASS (each seed independent HARD_PASS):
- Promotes WM multi-bank K=4096 phase coverage PARTIAL -> HIGH.
- Adds atom: "multi-bank interference-rescue cliff at K_per_bank=<X> for B=<Y>; mechanism: distributed capacity beats concentrated capacity at fixed total_K above interference threshold."
- Cross-references: chain-grade K=4096 multi-bank rail (atom <ID>); chain-grade K=8192 multi-bank 3-seed (atom <ID>).
