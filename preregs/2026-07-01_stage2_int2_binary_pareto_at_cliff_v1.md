# Pre-registration: Stage 2 INT2/BINARY Pareto probe at noise cliff regime v1

**Date:** 2026-07-01 (late session)
**Author:** hdi_exp_dev (per Sonnet Stage 2 Pareto drill Rank 1)
**Anchor:** `stage2_int2_binary_pareto_at_cliff_v1`
**Base:** INT8 v3 CG landing 2026-07-01 (HARD_PASS ALL_GATES at N=8192, M=160k, sigma=0.35, FP32=0.529 INT8=0.530 INT4=0.524 arms_range=0.006); hdlab/int8_dense.py commit c3ca7dab; E v5 CG anchor.
**Files:**
- `experiments/_stage2_int2_binary_pareto_at_cliff_v1_core.py`
- `experiments/exp_stage2_int2_binary_pareto_at_cliff_v1_seed_{7,13,19}.py`

## Substrate-KB prior work check

Substrate concept-query returned top hits at cosine=0.29 (weak): 2026-06-07 HOPFIELD-QUANT concept doc (proposed int8/int4 test, no INT2/binary). INT8 v3 CG landing today is the direct precursor — this cell EXTENDS the INT8 CG downward to INT2/binary, addressing the AGS 1985 binary-analog equivalence prediction empirically at the noise cliff regime. Genuinely novel; not a rediscovery.

## Rationale

INT8 v3 landed CG with INT8 Pareto zero-gap AND INT4 also within 0.006 of FP32 at the noise cliff regime (N=8192 M=160k sigma=0.35). The "INT4 breaks first" hypothesis was FALSIFIED. Amit-Gutfreund-Sompolinsky 1985 predicts binary Hopfield has 0.138N capacity vs 0.14N for analog — essentially equivalent (~1.4% difference). If INT2/binary also survive the noise cliff, Pareto memory-efficiency frontier extends 16x-32x below FP32 (huge M3 edge-deployment win). If INT2 fails but INT4 holds, Pareto knee is bracketed. Either outcome is atomizable.

## Sole CG-eligible claim (each independently atomizable)

1. **INT2 Pareto extends to noise-cliff regime** (INT2 gap ≤ 0.05 at best-discriminating point) — 16x compression Pareto atom
2. **BINARY Pareto extends to noise-cliff regime** (BINARY gap ≤ 0.10 at same) — 32x compression Pareto atom

## Discriminator / envelope-fail-bands

Discriminator point: **auto-selected via `_find_best_discriminating_sigma` at M=160000** (same logic as INT8 v3). Two qualification tiers:

- **Tier 1:** FP32 unsaturated (∈ (0.02, 0.98)) AND arms_range ≥ 0.03 (arms_range across 5 arms; MUCH more likely to fire than v3 because INT2 and BINARY expected to spread the ladder considerably)
- **Tier 2:** FP32 unsaturated AND arms_range < 0.03 (Pareto validated by tight-gap)
- **Tier 3:** fallback → HARD_FAIL_META_RULE_Q

### HARD_PASS (all substantive gates)

1. **HP_META_RULE_Q_ATCLIFF:** tier_1 OR tier_2
2. **HP_INT2_PARETO:** `|INT2 - FP32| ≤ 0.05` at auto-selected discriminator point
3. **HP_BINARY_PARETO:** `|BINARY - FP32| ≤ 0.10` at auto-selected discriminator point
4. **HP_MEMORY_TIER_INT2:** `max(INT2_bpf/FP32_bpf) ≤ 0.10` (16x compression; analytical PASS at 0.0626)
5. **HP_MEMORY_TIER_BINARY:** `max(BINARY_bpf/FP32_bpf) ≤ 0.04` (32x compression; analytical PASS at 0.0314)

Plus:
6. **cardinality_ok:** 40 units per seed observed (5 arms × 2 M × 4 σ)
7. **Mechanism hashes distinct** (40 unique)
8. **Cross-seed cv < 0.10**

### MIDDLE_BAND

- 2-4 of the substantive HP gates cleared
- INT2 CG (HP_INT2_PARETO passes) but BINARY breaks → "Pareto knee at 2-bit" MIDDLE band (still an atomizable finding: 16x compression is achievable, 32x is not)
- Or: BINARY CG but INT2 catastrophically fails (per smoke evidence: ternary clamp {-1, 0, +1} zeroes ~1/3 of weight magnitudes, whereas sign() preserves polarity — smoke measured INT2=0.205 vs BINARY=0.499 at N=4096)

### HARD_FAIL

- Tier 3 (FP32 saturated/at-floor at every σ; grid missed cliff)
- Cross-seed cv ≥ 0.10
- cardinality_ok fails / mechanism hash collision

### HF (mechanism-informative failures; not verdict-blocking but atomizable)

- **HF_INT2_BREAKS:** INT2 drops ≥ 0.20 vs FP32 → falsifies AGS 1985 at N=8192 (documented; likely fires per smoke evidence 0.478 drop at smoke-N)
- **HF_BINARY_BREAKS:** BINARY drops ≥ 0.30 vs FP32 → binary Hopfield falls at noise cliff

## Configuration (full mode)

- **Precision arms** (5): `[FP32, INT8, INT4, INT2, BINARY]`
- **M_sweep** = `[100000, 160000]` (2 values; near-crack + crack; N=8192)
- **N_fixed** = 8192
- **σ_sweep** = `[0.20, 0.30, 0.35, 0.40]` (4 values; spans cliff per INT8 v3 MEASURED@ probes)
- **n_ent = 5000, n_rel = 100, query_frac = 0.10, topK = 1**
- **Seeds:** `[7, 13, 19]`
- **Grid:** 5 arms × 2 M × 4 σ = **40 units per seed × 3 seeds = 120 total**
- **GPU-eligible;** route `overnight_queue`
- **Timeout:** 7200s per seed

## Quantization primitives

- **INT8:** hdlab.int8_dense.quantize_int8_dense (row-max scale; 8-bit) — commit c3ca7dab
- **INT4:** inline (row-max scale / 7.0; clamp to [-7, +7]; 4-bit) — from v3
- **INT2:** inline (row-max scale / 1.0; clamp to [-1, 0, +1]; effectively 1.58-bit ternary — the standard "INT2 hardware" implementation)
- **BINARY:** inline (row-mean-abs scale; sign() with zero→+1 tie-break; BinaryConnect 2016 convention)

## Selftest (formula gates; PASSED 2026-07-01 00:29 UTC)

Result: `fp32=1.000 int8=1.000 int4=1.000 int2=1.000 bin=1.000 bpf_bin=577.2 bpf_int2=1090.3 bpf_int4=2116.4 bpf_int8=4168.7 bpf_fp32=16418.1 mem_int2@N8k=0.0626 mem_bin@N8k=0.0314 int2_err=0.1464 bin_sign_match=1.000`

All 5 arms functional, bpf ordering strict (bin<int2<int4<int8<fp32), analytical memory factors at N=8192 M=160k PASS both gates (INT2=0.0626 ≤ 0.10; BINARY=0.0314 ≤ 0.04), INT2/BINARY/INT4 produce distinct outputs. Wall <2s.

## Smoke result 2026-07-01 00:31 UTC

**SMOKE_MIDDLE_BAND** at (N=4096, M=100k, σ=0.28) — cell functionally correct, discriminator fires cleanly, but Pareto claim NOT UNIVERSAL:

| Arm | Recall | Gap vs FP32 | bpf |
|-----|--------|-------------|-----|
| FP32 | 0.683 | — | 1507 |
| INT8 | 0.683 | 0.000 (Pareto-perfect, matches v3 CG) | 377 |
| INT4 | 0.674 | 0.009 (Pareto within v3 CG) | 189 |
| **INT2** | **0.205** | **0.478 (HF_INT2_BREAKS fires; catastrophic ternary failure)** | 95 |
| **BINARY** | **0.499** | **0.184 (MIDDLE band; sign() outperforms ternary)** | 47 |

Discriminator: tier_1_full (arms_range=0.478, FP32 unsat). Cardinality 5/5. Hashes distinct.

### Load-bearing smoke observations

1. **INT2 (symmetric ternary clamp) catastrophically fails** at smoke-N — the zero level in {-1, 0, +1} zeros out ~1/3 of weight magnitudes, destroying superposed pattern information. This is INFORMATIVE MECHANISM DATA: 2-bit quantization must be done as {-1.5, -0.5, +0.5, +1.5} asymmetric or {-1, +1} with 2 codes wasted, NOT as ternary.
2. **BINARY (sign) survives partially** — drop 0.184 is 0.116 above HP_BINARY_PARETO_TOL but 0.116 BELOW HF_BINARY_BREAKS_DELTA. Sign() preserves polarity everywhere; row-mean-abs scale carries just enough magnitude info. This matches AGS 1985 qualitatively — binary Hopfield operates but with degradation.
3. **Expected-order violation:** BINARY > INT2 (opposite of naive bit-precision expectation) — documents the ternary-vs-binary mechanism-class distinction, atomizable.

### Substantive interpretation

Full at N=8192 M=160k σ=0.35 will characterize whether:
- (A) INT2 catastrophic failure survives to full-N (likely per smoke) → HF_INT2_BREAKS confirmed; atomize as **"ternary quantization zeros too much magnitude; asymmetric 2-bit needed"**
- (B) BINARY partial survival persists (drop 0.10-0.30 range) → MIDDLE band with **"binary Hopfield operates at noise cliff with regime-limited degradation"** atom
- (C) Or scale-effects change the picture — full-N could compress the ladder further (substrate tolerance scales with N per DISCRIMINATOR-MUST-SURVIVE-SCALE)

**DISPATCH-READY:** smoke fires discriminator, primitives distinct, cardinality clean, memory factors analytical-PASS. Full-mode will produce atomizable findings whether (A), (B), or (C) holds.

## Runtime budget

- Smoke measured (N=4096 M=100k σ=0.28, 5 arms, 1 seed): **79.2s CPU wall**
- Full grid estimate per seed (5 arms × 2 M × 4 σ = 40 units at N=8192):
  - Per-unit GPU ~5-10s (matmul-bound) → 40 units × ~7s = ~5 min GPU
  - CPU fallback ~30 min per seed
- 3 seeds: 15 min GPU or ~90 min CPU; well within 7200s/seed timeout

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` in INT8 arm (unchanged from v3)
- Inline INT4/INT2/BINARY quantize; if v1 lands CG on INT2 OR BINARY, extract to `hdlab/int_low_bit.py` per META_RULE_AT

## Falsifiable predictions

1. **Prediction (per smoke evidence):** HF_INT2_BREAKS fires at N=8192 (INT2 drop ≥ 0.20); AGS 1985 binary-analog equivalence does NOT extend to symmetric ternary at noise cliff
2. **Prediction (per smoke evidence):** BINARY drop in [0.10, 0.30] at N=8192 → MIDDLE band, not HARD_PASS but not HARD_FAIL
3. **Alternate prediction (scale-tolerance argument):** At N=8192, substrate tolerance to ternary quantization noise may increase enough that INT2 recovers — sqrt(N)-scaling of margin could compress the ladder
4. **Substantive finding either way:** the ternary-vs-binary mechanism distinction is atomizable regardless of exact numerical outcome

## Sibling cells (chunked per-seed)

- `exp_stage2_int2_binary_pareto_at_cliff_v1_seed_7.py`
- `exp_stage2_int2_binary_pareto_at_cliff_v1_seed_13.py`
- `exp_stage2_int2_binary_pareto_at_cliff_v1_seed_19.py`

Each to `overnight_queue`, timeout 7200s. Runner-death tolerates loss of 1-of-3 seeds.

## References

- INT8 v3 CG landing (2026-07-01): `preregs/2026-07-01_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack.md` + `data/exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_7/metrics.json`
- Amit-Gutfreund-Sompolinsky 1985 (binary vs analog Hopfield capacity 0.138N vs 0.14N)
- BinaryConnect (Courbariaux 2016) — sign() with mean-abs scale binary quantization convention
- Sonnet Stage 2 Pareto drill Rank 1 (this cell's origin)
- hdlab primitive: `hdlab/int8_dense.py` commit c3ca7dab
- MEMORY.md: DISCRIMINATOR-MUST-SURVIVE-SCALE, META_RULE_H/Q/AF
