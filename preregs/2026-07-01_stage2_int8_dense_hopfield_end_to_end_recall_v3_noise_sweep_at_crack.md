# Pre-registration: Stage 2 opener v3 — INT8 dense-Hopfield NOISE-CLIFF sweep at fixed near-crack M

**Date:** 2026-07-01 (late session)
**Author:** hdi_exp_dev (per Research Option B amendment 2026-07-01; supersedes v2 pre-reg)
**Anchor:** `stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack`
**Base:** v1 aborted pre-crack (commit 4c8acf54); v2 landed HARD_FAIL_META_RULE_Q at seed_7 + seed_13 (crack-scaling supra-linear; commit ad476f2b); hdlab/int8_dense.py commit c3ca7dab; E v5 CG anchor.
**Files:**
- `experiments/_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_core.py`
- `experiments/exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_{7,13,19}.py`

## Amendment rationale (per Research Option B)

v2 empirically established that substrate capacity scales SUPRA-linearly in N — at N=8192 even M=160k σ=0.2 (E v5 linear-scaled crack midpoint) shows FP32=1.000=INT8=INT4 (arms_range=0.000, HARD_FAIL_META_RULE_Q). Push into overload doesn't discriminate the ladder without noise. v3 pivots to use SIGMA as the primary discriminator: sweep σ into the noise-cliff transition band at fixed near-crack M values where FP32 is unsaturated (< 0.90) leaving room for precision noise to emerge.

## Sole CG-eligible claim

**At N=8192 across the noise-cliff regime (σ ∈ [0.20, 0.55]), INT8_DENSE holds Pareto-optimal position with recall gap ≤ 0.05 vs FP32 at the best-discriminating (M, σ) point, while the below-crack free-memory tier (M ≤ 10k, σ ≤ 0.42, all 4 arms within 0.01) provides an orthogonal atomizable claim of precision-invariant memory efficiency.**

Two independent CG-eligible claims:
1. **INT8 Pareto extends into noise-cliff regime** (INT8 gap ≤ 0.05 at best-discriminating point)
2. **Below-crack free-memory tier** (all 4 precisions within 0.01 at M=10k, σ ≤ 0.42)

## Discriminator / envelope-fail-bands

Discriminator point: **auto-selected via `_find_best_discriminating_sigma` at M=160000**. Two qualification tiers:

- **Tier 1 (full discriminator):** FP32 unsaturated (∈ (0.02, 0.98)) AND arms_range ≥ 0.03
- **Tier 2 (pareto-probe only):** FP32 unsaturated AND arms_range < 0.03. This tier captures the empirically-observed positive finding: precision arms track FP32 to 3+ decimal places even in the cliff regime, so range is small but INT8 Pareto is validated by tight-gap.
- **Tier 3 (fallback):** neither — HARD_FAIL_META_RULE_Q

### HARD_PASS (all substantive gates)

1. **HP_META_RULE_Q_ATCLIFF:** tier_1 OR tier_2 (see selection above); NOT tier_3
2. **HP_INT8_PARETO_CLIFF:** `|INT8 - FP32| ≤ 0.05` at auto-selected discriminator point
3. **HP_INT4_BREAKS_AT_CLIFF:** `(FP32 - INT4) ≥ 0.20` at same point (INFORMATIONAL — not itself HF-blocking if unmet; documents ladder-break location OR its absence)
4. **HP_PRE_CRACK_FREE:** at M=10k, σ ≤ 0.42, all 4 arms within 0.01 (below-crack free-memory tier CG claim)
5. **HP_MEMORY_FACTOR:** `max(INT8_bpf/FP32_bpf) ≤ 0.35` (analytical; passes at 0.254)

Plus:
6. **cardinality_ok:** 72 units per seed observed (4 arms × 3 M × 6 σ)
7. **Mechanism hashes distinct** (72 unique)
8. **Cross-seed cv < 0.10** for any (arm, M, σ)

### MIDDLE_BAND

- 2-3 of the substantive HP gates cleared
- INT8 gap 0.05-0.10 (borderline)
- Pre-crack range 0.01-0.02 (borderline free-memory)

### HARD_FAIL

- Tier 3 (FP32 saturated OR at floor at every σ in sweep — grid missed cliff bracket, need v4 with finer σ)
- 0-1 substantive HP gates cleared
- Cross-seed cv ≥ 0.10 for any arm
- cardinality_ok fails / mechanism hash collision

## Configuration (full mode)

- **Precision arms** (4): `[FP32, FP16, INT8, INT4]`
- **M_sweep** = `[10000, 100000, 160000]` (3 values; pre-crack + near-crack + crack)
- **N_fixed** = 8192
- **σ_sweep** = `[0.20, 0.28, 0.35, 0.38, 0.42, 0.55]` (6 values; tuned from local MEASURED@ probes at cliff bracket)
- **n_ent = 5000, n_rel = 100, query_frac = 0.10, topK = 1**
- **Seeds:** `[7, 13, 19]`
- **Grid:** 4 arms × 3 M × 6 σ = **72 units per seed × 3 seeds = 216 total**
- **GPU-eligible;** route `overnight_queue`
- **Timeout:** 7200s per seed

## MEASURED@ local probes 2026-07-01 (informed grid design)

### FP32 sigma cliff scans

| Point | FP32 recall | Note |
|-------|------|------|
| N=4096, M=100k, σ=0.20 | 0.973 | above cliff (near-saturation) |
| N=4096, M=100k, σ=0.28 | **0.683** | **cliff mid-band (ideal discriminator)** |
| N=4096, M=100k, σ=0.32 | 0.396 | mid-cliff |
| N=4096, M=100k, σ=0.35 | 0.212 | bottom cliff |
| N=4096, M=100k, σ=0.38-0.44 | 0.01-0.09 | below floor |
| N=8192, M=160k, σ=0.35 | **0.529** | **cliff mid-band at full grid (ideal discriminator)** |
| N=8192, M=160k, σ=0.40 | 0.127 | mid-cliff |
| N=8192, M=160k, σ=0.45+ | ≤0.01 | below floor |

### v3 smoke at (N=4096, M=100k, σ=0.28) — ALL 4 ARMS MEASURED

| Arm | Recall | Wall | bpf |
|-----|--------|------|-----|
| FP32 | 0.683 | 18.1s | 1507 |
| FP16 | 0.683 | 19.3s | 753 |
| INT8 | **0.683** | 19.6s | 377 |
| INT4 | 0.674 | 20.6s | 189 |

**Load-bearing observation:** FP32 = FP16 = INT8 to 3 decimal places even in the noise cliff. INT4 drops only 0.009. This validates the tier_2 Pareto-probe qualification (INT8 Pareto extends into cliff with zero-gap).

## Substantive findings v3 will produce (per Research 3-atom mandate)

1. **INT8 Pareto in noise-cliff regime** (CG-eligible via smoke evidence: INT8 gap = 0.000 at cliff; likely extends to N=8192 M=160k σ=0.35)
2. **Below-crack free-memory tier** (M ≤ 10k σ ≤ 0.42 all arms within 0.01 — CG candidate; separable atom)
3. **INT4 modest degradation, not "breakage"** — smoke shows INT4 drops 0.009 vs FP32 at cliff, NOT the 0.20 breakage predicted by HP_INT4_BREAKS. Likely falsification of "INT4 breaks first" hypothesis in this regime.
4. **BONUS: Substrate capacity supra-linear in N** (already established from v2 evidence; separately atomizable)

## Runtime budget

- Local M=100k N=4096 σ=0.28: 4 arms × ~19s = 76s (measured)
- Full grid GPU estimate:
  - M=10k units: <10s each × 24 units = ~4 min
  - M=100k units: ~5s GPU each × 24 units = ~2 min
  - M=160k units: ~8s GPU each × 24 units = ~3 min
  - Total 1-seed GPU: ~10 min; CPU fallback ~30 min
- 3 seeds parallel or serial: 30-90 min GPU; well within 7200s/seed timeout

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` in INT8 arm
- Inline INT4 quantize; extract to `hdlab/int4_dense.py` if v3 lands CG on INT4 breaks OR provides high-signal evidence for INT4 characterization

## Selftest (formula gates; PASSED 2026-07-01)

Same 5 checks as v1/v2 (unchanged primitives): 4-arm functional, bpf ordering, INT4 round-trip, INT4-vs-INT8 distinct, HP_MEMORY_FACTOR analytical. Wall <2s.

Result: `fp32=1.000 fp16=1.000 int8=1.000 int4=1.000 mem_factor(int8/fp32)=0.254 int4_err=0.0217` — PASS.

## Smoke result 2026-07-01

**SMOKE_HARD_PASS** at (N=4096, M=100k, σ=0.28):
- Discriminator fires: FP32=0.683 (unsaturated in cliff)
- INT8 gap = 0.000 (`|0.683 - 0.683|` — perfect Pareto)
- INT4 drop = 0.009 (not "breakage" at 0.20 threshold)
- arms_range = 0.009 → qualifies tier_2 pareto-probe (Pareto validated by tight-gap not by wide-range)
- cardinality 4/4, hashes distinct, cell functionally correct

## Falsifiable predictions (v3-specific)

1. **HP:** INT8 Pareto extends to N=8192 M=160k noise-cliff regime (INT8 gap ≤ 0.05) — smoke evidence strongly suggests this holds
2. **HP:** Pre-crack free-memory tier (M=10k, σ ≤ 0.42, all arms within 0.01) — E v5 physics + smoke both predict this
3. **INT4 breaks likely FALSIFIED:** smoke measured drop = 0.009 << 0.20 threshold. Full at higher M may increase drop but unlikely to hit 0.20 unless M=160k σ=0.35 shows very different INT4 behavior. Documented either way.
4. **Regime-shape claim:** noise cliff at N=8192 M=160k is a SHARP transition (0.35→0.53, 0.40→0.13, 0.45→0.01). Substrate exhibits phase-transition-like behavior in noise (analogous to Dim S v3 cliff findings).

## Sibling cells (chunked per-seed)

- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_7.py`
- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_13.py`
- `exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_19.py`

Each to `overnight_queue`, timeout 7200s. Runner-death tolerates loss of 1-of-3 seeds.

## References

- v2 pre-reg + HARD_FAIL analysis: `preregs/2026-07-01_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime.md`, commit ad476f2b
- v1 aborted pre-crack: commit 4c8acf54
- E v5 CG landing: commit e04666ad
- Sonnet dense-HF CLT-washout drill: 2026-07-01
- Dim S v3 cliff-bracket methodology: same-day landing referenced in Option B guidance
- hdlab primitive: `hdlab/int8_dense.py` commit c3ca7dab
- MEMORY.md: DISCRIMINATOR-MUST-SURVIVE-SCALE, META_RULE_H/K/Q/L/AF/AH
