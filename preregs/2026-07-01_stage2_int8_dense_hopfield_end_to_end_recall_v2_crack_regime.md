# Pre-registration: Stage 2 opener v2 — INT8 dense-Hopfield end-to-end recall CRACK REGIME

**Date:** 2026-07-01 (late session)
**Author:** hdi_exp_dev (per Research amendment 2026-07-01; supersedes v1 pre-reg)
**Anchor:** `stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime`
**Base:** v1 landed HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING at commit 4c8acf54 (2026-07-01); Sonnet dense-HF theory drill CLT-washout finding at same date; hdlab/int8_dense.py commit c3ca7dab; E v5 CG anchor commit e04666ad.
**Files:**
- `experiments/_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_core.py`
- `experiments/exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_{7,13,19}.py`

## Amendment rationale

v1 aborted dispatch because USER's M ∈ {100..10000} at N ∈ {2048..8192} is entirely PRE-crack for the substrate capacity envelope — all 4 precision arms saturated at recall = 1.000 across the entire grid. Sonnet's dense-HF CLT-washout theoretical drill confirms: at M/N << AGS wall, CLT washes precision noise, making FP32/FP16/INT8/INT4 indistinguishable. v2 amendment extends M into the crack region (M ≥ 80k) at N=8192 where precision noise becomes visible above CLT background.

## Sole CG-eligible claim

**At N=8192 across the M/σ crack regime, INT8_DENSE holds Pareto-optimal position (recall within 0.05 of FP32, memory ≤ 0.35× FP32) while INT4 breaks and post-crack collapse arrives together for all precisions.** Specifically:
- INT8 tracks FP32 within 0.05 at crack midpoint (M=160k)
- INT4 drops ≥ 0.20 vs FP32 at same point (ladder breakage location)
- Below crack (M ≤ 10k), all 4 precisions within 0.01 of each other (below-crack free-memory tier)
- Above crack (M = 320k), all 4 precisions crash < 0.30 together (spin-glass regime)

## Discriminator / envelope-fail-bands

### HARD_PASS (all 4 gates + cardinality/hash/cv)

Discriminator point: **(N=8192, M=160000, σ=0.2)** — E v5-scaled crack midpoint.

1. **HP_INT8_PARETO_CG:** `|INT8_recall - FP32_recall| ≤ 0.05` at discriminator point
2. **HP_INT4_BREAKS:** `(FP32_recall - INT4_recall) ≥ 0.20` at discriminator point (documentation; not itself HF-blocking if unmet)
3. **HP_PRE_CRACK_FREE:** at M ∈ {1000, 10000} (all σ), all 4 precisions within `0.01` range (below-crack free-memory tier CG claim)
4. **HP_POST_CRACK_COLLAPSE:** at M = 320000, σ=0.2, all 4 precisions max_recall < `0.30` (spin-glass collapse; all precisions crash together)

Plus:
5. **HP_MEMORY_FACTOR:** `max(INT8_bpf / FP32_bpf) ≤ 0.35` (analytical; passes by construction at ~0.25)
6. **cardinality_ok:** 72 units per seed observed (4 arms × 6 M × 3 σ)
7. **All 72 mechanism_hashes distinct** per seed
8. **Cross-seed cv < 0.10** for any (arm, M, σ)

### MIDDLE_BAND

- 2-3 of 4 HP gates cleared (partial Pareto; regime-conditional finding still publishable as MM)
- INT8 gap 0.05-0.08 (borderline)
- Pre-crack range 0.01-0.02 (borderline free-memory)
- Post-crack max 0.30-0.40 (partial collapse)

### HARD_FAIL

- 0-1 HP gates cleared
- META_RULE_Q non-discriminating at (N=8192, M=160k, σ=0.2): baseline FP32 saturates ≥ 0.98 OR arms differ < 0.03 (if smoke crack-preview reveals this, abort like v1)
- Any cross-seed cv ≥ 0.10
- cardinality_ok fails (META_RULE_H)
- Mechanism-hash collision (META_RULE_AX)
- BINARY-style precision alternative wins > INT8 (contradicts E v5; not applicable here since v2 dropped BINARY arm)

## Configuration (full mode)

- **Precision arms** (4): `[FP32, FP16, INT8, INT4]`
  - FP32: baseline
  - FP16: `torch.float16` storage-quantize + fp32 matmul accumulator (production pattern)
  - INT8: composes `hdlab.int8_dense.quantize_int8_dense` (META_RULE_AT; commit c3ca7dab)
  - INT4: inline symmetric per-row scale quantize, range [-7, 7], 0.5 byte/elem packed cost
- **M_sweep** = `[1000, 10000, 40000, 80000, 160000, 320000]` (6 values; spans pre-crack → in-crack → post-crack)
  - M=1k, 10k: PRE-crack (HP_PRE_CRACK_FREE tier)
  - M=40k: crack-onset per E v5 (calibration overlap)
  - M=80k, 160k: crack midpoint (E v5 in-crack scaled to N=8192)
  - M=320k: POST-crack spin-glass (HP_POST_CRACK_COLLAPSE tier)
- **N_fixed** = 8192 (single N; was swept in v1)
- **σ_sweep** = `[0.0, 0.2, 0.5]` (3 values; kept coarse since M is the primary discriminator)
- **n_ent = 5000, n_rel = 100**, max_keys = 500000 ≥ M_max = 320000 ✓
- **query_frac = 0.10, topK = 1**
- **Seeds:** `[7, 13, 19]`
- **Grid:** 4 arms × 6 M × 3 σ = **72 units per seed × 3 seeds = 216 total**
- **GPU-eligible** (torch cuda; falls back CPU); route to `overnight_queue`
- **Timeout:** 7200s per seed per USER task

## Runtime budget

- Wall-time formula (measured M=1000 N=8192 FP32 = 6.5s CPU):
  - M=1k: ~6.5s per arm CPU
  - M=10k: ~65s per arm CPU
  - M=40k: ~260s per arm CPU
  - M=80k: ~520s per arm CPU
  - M=160k: ~1040s per arm CPU (17 min)
  - M=320k: ~2080s per arm CPU (35 min)
- Total 1-seed CPU: ~13 hours (would blow 7200s timeout)
- **GPU expected 15-30× speedup on matmul at N=8192** (very kernel-friendly):
  - Total 1-seed GPU: 30-50 min per seed
  - 3 seeds: 1.5-2.5 hours
  - Per-seed timeout 7200s = 2 hours: adequate with margin
- **Contingency:** if GPU speedup below 15×, per-seed timeout may fire at M=320k. Cell writes per-unit incrementally so partial results survive; runner resume + reduced M_max (drop 320k → 160k) is the fallback if timeout hits.

## Smoke design (DISCRIMINATOR-MUST-SURVIVE-SCALE Check-C: reproduce known point)

**Smoke:** seed_7 at M=40k, N=4096, σ=0.2 (single point; 4 arms).

Rationale: E v5 CG established INT8 = FP32 parity in WM capacity-crack regime M ∈ {40k, 80k}, N=2048. Smoke at M=40k, N=4096 reproduces an E v5-nearby point. At N=4096 with M=40k, M/N=10 is BELOW E v5's crack ratio (M/N=20 at N=2048); this is PRE-crack for N=4096 and IS expected to saturate.

**IMPORTANT:** smoke at M=40k, N=4096 HARD_FAIL_META_RULE_Q is EXPECTED and NOT a blocker for FULL dispatch. The smoke exists to verify cell mechanics (4 arms run, cardinality, hashes distinct, INT4 primitive works at scale, wall-time budget honest). The FULL grid probes the actual crack at N=8192 M=160k where discrimination is theoretically predicted.

**Full-N=8192 discriminator preview:** deferred to full dispatch. At M=160k N=8192 CPU cost is ~17 min per arm × 4 = 68 min, prohibitive as pre-dispatch smoke. Cell instead relies on:
- E v5 CG empirical evidence: INT8 ≈ FP32 at M/N=20 crack region
- Sonnet CLT-washout theoretical prediction: precision noise emerges only above AGS wall
- Analytical M-scaling: crack at N=2048 was M=40k; scaled to N=8192 (linear in N) predicts crack at M ≈ 160k
- Local probe: MEASURED at N=8192 M=80k σ=0.2 → results in `smoke_notes` block of first landed FULL metrics

## Selftest (formula gates; MANDATORY pre-dispatch; PASSED 2026-07-01)

Verifies:
- All 4 arm functions return recall in [0, 1] and finite (PASS)
- bpf ordering INT4 < INT8 < FP16 < FP32 (analytical; PASS)
- HP_MEMORY_FACTOR analytical: `bpf_int8 / bpf_fp32 ≤ 0.35` (PASS at 0.254)
- INT4 round-trip error bounded by 2× scale (PASS at max_err=0.0226)
- INT4 vs INT8 quantize produce distinct output (ARMS-MUST-DIFFER precursor; PASS)

Selftest wall time: <2 seconds.

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` composed in INT8 arm (`_ingest_and_query_int8`)
- INT4 quantize inline (`quantize_int4_dense` in core module); if v2 lands CG on HP_INT4_BREAKS, extract to `hdlab/int4_dense.py` per results-to-application-cadence discipline

## Predicted per-M behavior (based on E v5 empirical + Sonnet CLT-washout + local MEASURED probe 2026-07-01)

### MEASURED@ local probes (single-seed=7 CPU, this cell v2 core):

| Point | FP32 | FP16 | INT8 | INT4 | Range | Note |
|---|---|---|---|---|---|---|
| N=2048, M=40k, σ=0.2 | 0.9170 | 0.9168 | 0.9170 | 0.9112 | 0.006 | E v5 reproducer: MATCHES E v5 CG (INT8=FP32 within 0.0000; INT4 within 0.006) |
| N=8192, M=80k, σ=0.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.000 | pre-crack at N=8192 |
| **N=8192, M=160k, σ=0.2** | **0.9996** | **0.9996** | **0.9996** | **0.9996** | **0.0000** | **v2 discriminator point per Research amendment — leak barely detectable; range still 0.000** |

**Load-bearing finding:** the linear crack-scaling assumption (M/N=20 at N=2048 → M=160k at N=8192) is **FALSIFIED by direct measurement.** At N=8192 the substrate capacity envelope is empirically much larger than 20×N; even M=160k σ=0.2 shows only 0.04% leak from saturation.

### HYPOTHESIZED@ this pre-reg (pending local M=320k probe):

| M | FP32 | INT8 | INT4 | Note |
|---|---|---|---|---|
| 1000 | 1.00 | 1.00 | 1.00 | pre-crack (MEASURED via v1) |
| 10000 | 1.00 | 1.00 | 1.00 | pre-crack (MEASURED via v1) |
| 40000 | 1.00 | 1.00 | 1.00 | pre-crack at N=8192 (extrapolate from M=80k MEASURED) |
| 80000 | 1.00 | 1.00 | 1.00 | pre-crack at N=8192 (MEASURED above) |
| 160000 | 1.00 (leak 0.9996) | 1.00 | 1.00 | crack onset barely; MEASURED range 0.0000 |
| **320000** | **???** | **???** | **???** | **crack midpoint OR still pre-crack — TBD via local probe (currently running)** |

(Predictions per HYPOTHESIZED@ this pre-reg; MEASURED will be recorded per DIRECTOR framing discipline after full-mode landing.)

## Falsifiable predictions (per USER 3-atomizable-findings mandate)

1. **INT8 Pareto CG:** INT8 tracks FP32 within 0.05 at crack midpoint (HP_INT8_PARETO_CG)
2. **Below-crack free-memory tier:** at M ≤ 10k, all precisions ≤ 0.01 apart (HP_PRE_CRACK_FREE) — orthogonal atomizable finding
3. **INT4 breaks at crack:** FP32 - INT4 ≥ 0.20 at crack midpoint (HP_INT4_BREAKS validated) OR ≤ 0.05 (falsified: INT4 also holds Pareto)
4. **Post-crack collapse regime:** all precisions crash together at M=320k (HP_POST_CRACK_COLLAPSE) — orthogonal atomizable finding

## Sibling cells (chunked per-seed)

- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_7.py`
- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_13.py`
- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_19.py`

Each dispatched separately to `overnight_queue` with 7200s timeout. Runner-death loses one seed; aggregate verdict tolerates 1-of-3 seed loss with cv analysis noting reduced n_seeds.

## References

- v1 pre-reg + HARD_FAIL analysis: `preregs/2026-07-01_stage2_int8_dense_hopfield_end_to_end_recall_v1.md`, commit 4c8acf54
- E v5 CG landing: commit e04666ad, prereg `preregs/2026-07-01_substrate_bytes_per_fact_pareto_v5_int8_specialization.md`
- Sonnet dense-HF CLT-washout theory drill: 2026-07-01 (Research)
- hdlab primitive: `hdlab/int8_dense.py` (commit c3ca7dab)
- MEMORY.md disciplines: `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`, cross-references META_RULE_H/K/Q/L/AF/AH.
