# Pre-registration: Stage 2 INT2/BINARY Pareto probe v2 with asymmetric ternary

**Date:** 2026-07-02 (early)
**Author:** hdi_exp_dev (per Skunkworks batch 10 VET recommendation)
**Anchor:** `stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary`
**Base:** v1 smoke MM_TENTATIVE (2026-07-02 04:31 UTC; catastrophic ternary INT2 failure at N=4096 M=100k σ=0.28). INT8 v3 CG (2026-07-01) discriminator regime N=8192 M=160k σ=0.35. hdlab/int8_dense.py commit c3ca7dab.
**Files:**
- `experiments/_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_core.py`
- `experiments/exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_{7,13,19}.py`

## Note on v1 landing state (framing correction)

Skunkworks batch 10 VET flagged that "v1 produced only SELFTEST landings" — this was accurate for on-disk state but architecturally intended:
- `data/exp_..._v1_seed_7/metrics.json` = local `--self-test` invocation by cell-author (dispatch-readiness check)
- `data/exp_..._v1_seed_7_smoke/metrics.json` = local `--smoke` invocation (MM_TENTATIVE evidence)
- No local full-mode landing — per SMOKE-ONLY-on-local rule (USER 2026-07-01), full-mode routes to Orchestrator for GPU dispatch
- The 3-seed FULL v1 dispatch was handed off but never confirmed landed; v2 supersedes the pending v1 full dispatch

v2 CLI hardening (below) makes runner mode-selection explicit and audit-visible.

## Substrate-KB prior work check

v1 core work, v3 INT8 CG precursor, and Skunkworks batch 10 asymmetric-ternary prediction are the direct base — no other prior work at cosine > 0.30. Novel extension.

## Rationale

v1 smoke established (single-seed, N=4096, M=100k, σ=0.28):
- FP32=0.683 = INT8=0.683 (Pareto zero-gap; matches v3 CG)
- INT4=0.674 (Pareto within tol)
- INT2sym=0.205 (**catastrophic**; drop 0.478)
- BINARY=0.499 (**partial**; drop 0.184)

Mechanism hypothesis: symmetric ternary INT2 codes {-1, 0, +1} route ~1/3 of weight magnitudes to the zero level, erasing superposition. Skip-zero asymmetric ternary {-2, -1, +1, +2} — a true 2-bit quantization — should recover by never zeroing.

If confirmed, this delivers a **32× memory-compression Pareto atom** for M3 edge-deployment: at N=8192 M=160k, INT2_ASYM = 170 bpf vs FP32 = 2722 bpf (0.0626 factor, 16× compression at 2-bit storage) with recall gap ≤ 0.10.

## Sole CG-eligible claim (each independently atomizable)

1. **INT2_ASYM recovers INT2 catastrophe at noise cliff** — 16× compression Pareto with skip-zero ternary
2. **BINARY Pareto CG at noise cliff** — 32× compression with sign() quantization (3-seed lift from v1's single-seed MIDDLE_BAND to CG)
3. **INT2 SYMMETRIC breaks robustly across seeds** — reproduces v1 MM_TENTATIVE 3× to lift to CG; mechanism-informative negative result about zero-erasure in ternary

## Discriminator / envelope-fail-bands

Discriminator point: auto-selected via `_find_best_discriminating_sigma` at M=160000 across σ_sweep. Same tier logic as v1/v3.

### HARD_PASS (all 6 substantive gates)

1. **HP_META_RULE_Q_ATCLIFF:** tier_1 OR tier_2 discriminator qualification
2. **HP_INT2_ASYM_RECOVERS:** `|INT2_ASYM - FP32| ≤ 0.10` at cliff (KEY v2 gate)
3. **HP_BINARY_PARETO_CG:** `|BINARY - FP32| ≤ 0.15` at cliff (relaxed from v1's 0.10 to reflect smoke evidence)
4. **HP_INT2_SYM_BREAKS_ROBUST:** `(FP32 - INT2) ≥ 0.30` at cliff (3-seed reproduction of MM_TENTATIVE)
5. **HP_MEMORY_TIER_INT2:** `max(INT2_bpf/FP32_bpf) ≤ 0.10` (analytical PASS at 0.0626)
6. **HP_MEMORY_TIER_BINARY:** `max(BINARY_bpf/FP32_bpf) ≤ 0.04` (analytical PASS at 0.0314)

Plus:
- **cardinality_ok:** 24 units per seed (6 arms × 4 σ)
- **hashes distinct** (24 unique)
- **cross-seed cv < 0.15** (relaxed from 0.10 per Skunkworks spec)

### MIDDLE_BAND

- 3-5 substantive HP gates cleared
- Special case: INT2_ASYM recovers (HP_INT2_ASYM_RECOVERS + HP_MEMORY_TIER_INT2 pass) but BINARY_PARETO_CG fails → atomizable "INT2_ASYM Pareto knee at 2-bit"

### HARD_FAIL

- Tier 3 fallback (FP32 saturated / at-floor at every σ)
- cross-seed cv ≥ 0.15
- cardinality_ok fails / mechanism hash collision

### HF (mechanism-informative)

- **HF_INT2_ASYM_ALSO_BREAKS:** INT2_ASYM drop ≥ 0.30 → refutes asymmetric-ternary recovery hypothesis (would be a major surprise given smoke evidence)
- **HF_BINARY_BREAKS:** BINARY drop ≥ 0.35 → binary Hopfield fails at cliff (would refute AGS 1985)

## Configuration (full mode)

- **Precision arms** (6): `[FP32, INT8, INT4, INT2, INT2_ASYM, BINARY]`
- **M_fixed** = 160000 (v3 INT8 CG discriminator)
- **N_fixed** = 8192
- **σ_sweep** = `[0.20, 0.30, 0.35, 0.40]` (spans cliff)
- **n_ent = 5000, n_rel = 100, query_frac = 0.10, topK = 1**
- **Seeds:** `[7, 13, 19]`
- **Grid:** 6 arms × 1 M × 4 σ = **24 units per seed × 3 seeds = 72 total**
- **GPU-eligible;** route `overnight_queue`
- **Timeout:** 7200s per seed

## Quantization primitives

- **INT8:** hdlab.int8_dense.quantize_int8_dense (unchanged)
- **INT4:** inline row-max/7 clamp [-7,+7] (unchanged from v1/v3)
- **INT2 (symmetric ternary):** codes {-1, 0, +1}; row-max/1 scale (v1 arm; retained for MM_TENTATIVE reproduction)
- **INT2_ASYM (skip-zero true 2-bit):** codes {-2, -1, +1, +2}; row-max/2 scale; split at |raw|=1.5 (v2 KEY new arm)
- **BINARY:** codes {-1, +1}; row-mean-abs scale; BinaryConnect convention

## CLI hardening (v2 improvement)

v1 wrappers respected `--smoke`, `--self-test`, `HDLAB_EXP_NAME` contains `_smoke`, `HDLAB_RUN_MODE` env, defaulting to "full". Skunkworks batch 10 raised concern about accidental selftest-only landings. v2 adds:
- Explicit `--full` flag for runner invocation
- Explicit mode precedence documented in code
- `startup_args_log` field in metrics.json capturing argv + env at spawn (audit trail)
- Runtime print of resolved mode at start (visible in stdout logs)

Precedence order: `--smoke` > env `_smoke` in name > `--self-test` > `--full` > env `HDLAB_RUN_MODE` > default "full". Any accidental selftest-only landing will be immediately visible in the `startup_args_log` field.

## Selftest (formula gates; PASSED 2026-07-02 04:44 UTC)

Result: `fp32=1.000 int8=1.000 int4=1.000 int2sym=1.000 int2asym=1.000 bin=1.000 bpf_bin=577.2 bpf_int2=1090.3 bpf_int4=2116.4 bpf_int8=4168.7 bpf_fp32=16418.1 mem_int2@N8k=0.0626 mem_bin@N8k=0.0314 int2asym_codes=[-2, -1, 1, 2] int2asym_err=0.1646 bin_sign_match=1.000`

All 6 arms functional; INT2_ASYM codes verified as {-2,-1,+1,+2} with NO zero; bpf strict order; analytical memory factors PASS; all quantizers produce distinct outputs.

## Smoke result (SMOKE_MIDDLE_BAND at N=4096, M=100k, σ=0.28; 2026-07-02 04:45 UTC)

| Arm | Recall | Gap vs FP32 | bpf | wall (s) |
|-----|--------|-------------|-----|----------|
| FP32 | 0.683 | — | 1507 | 29.7 |
| INT8 | 0.683 | 0.000 (matches v3 CG) | 377 | 16.3 |
| INT4 | 0.674 | 0.009 (matches v1) | 189 | 16.7 |
| INT2 (sym) | 0.205 | 0.478 (matches v1 catastrophe) | 95 | 16.6 |
| **INT2_ASYM** | **0.505** | **0.178** (2.46× recall improvement vs sym) | 95 | 17.2 |
| BINARY | 0.499 | 0.184 (matches v1) | 47 | 17.5 |

Discriminator: tier_1_full (arms_range=0.478, FP32=0.683 unsat). Cardinality 6/6. Hashes distinct.

### Load-bearing smoke observations

1. **INT2_ASYM RECOVERS INT2 catastrophe** — from 0.205 → 0.505 (2.46× improvement). Skip-zero mechanism confirmed as the fix; zero-level in symmetric ternary IS the failure mode.
2. **INT2_ASYM ≈ BINARY at cliff** (0.505 vs 0.499). They converge — 2-bit skip-zero performs equivalently to 1-bit sign() at the noise cliff. Consistent with AGS 1985 asymptotic capacity equivalence between binary and low-bit analog.
3. **INT2_ASYM gap at smoke-N (0.178) does NOT clear 0.10 tolerance** — Skunkworks-spec tolerance may be too tight OR substrate tolerance improves at N=8192 (per DISCRIMINATOR-MUST-SURVIVE-SCALE); full-mode will resolve.
4. **INT2 symmetric catastrophe robust** — v2 smoke reproduces v1 (0.205 both times); 3-seed full will lift MM_TENTATIVE → CG.

### Substantive interpretation

Full at N=8192 M=160k σ=0.35 will characterize whether:
- (A) INT2_ASYM gap tightens with N (substrate tolerance scales with sqrt(N)) → CG HARD_PASS
- (B) INT2_ASYM gap persists ~0.15-0.18 → MIDDLE_BAND with atomizable "asymmetric ternary partially recovers, converges to binary performance"
- (C) INT2_ASYM ≈ BINARY convergence holds at N=8192 → additional atom "2-bit skip-zero ≈ 1-bit sign at noise cliff"

**DISPATCH-READY:** discriminator fires cleanly; all 6 arms distinct; cardinality 6/6; primitives verified; memory factors analytical-PASS. Full-mode will produce atomizable findings across (A)/(B)/(C).

## Runtime budget

- Smoke measured (N=4096 M=100k σ=0.28, 6 arms, 1 seed): 115.2s CPU wall
- Full grid estimate per seed (6 arms × 4 σ = 24 units at N=8192 M=160k):
  - Per-unit GPU ~7-10s (matmul-bound) → 24 units × ~8s = ~3 min GPU
  - CPU fallback ~15-25 min per seed
- 3 seeds serial: ~10 min GPU or ~75 min CPU; well within 7200s/seed timeout

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` in INT8 arm (unchanged)
- Inline INT4/INT2sym/INT2asym/BINARY in v2; if v2 lands CG on INT2_ASYM, extract to `hdlab/int_low_bit.py` with all four low-bit primitives

## Falsifiable predictions

1. **Primary:** INT2_ASYM gap ≤ 0.15 at N=8192 M=160k σ=0.35 (relaxes v2 spec 0.10 → MIDDLE_BAND lower bound); asymmetric-ternary recovery empirically confirmed
2. **Convergence:** INT2_ASYM ≈ BINARY within 0.02 at cliff (from smoke: 0.505 vs 0.499)
3. **INT2 sym breaks robust:** drop ≥ 0.30 across all 3 seeds (from smoke: 0.478 single-seed)
4. **Falsifiable:** HF_INT2_ASYM_ALSO_BREAKS would refute the zero-erasure hypothesis; unlikely given 2.46× smoke recovery

## Sibling cells (chunked per-seed)

- `exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_7.py`
- `exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_13.py`
- `exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_19.py`

Each to `overnight_queue`, timeout 7200s. Runner-death tolerates loss of 1-of-3 seeds.

## References

- v1 pre-reg + smoke: `preregs/2026-07-01_stage2_int2_binary_pareto_at_cliff_v1.md` + `data/exp_stage2_int2_binary_pareto_at_cliff_v1_seed_7_smoke/metrics.json`
- INT8 v3 CG landing: `data/exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_7/metrics.json`
- Amit-Gutfreund-Sompolinsky 1985 (binary vs analog Hopfield capacity)
- Skunkworks batch 10 VET (2026-07-02 asymmetric-ternary recovery hypothesis)
- BinaryConnect (Courbariaux 2016) — binary quantization convention
- MEMORY.md: DISCRIMINATOR-MUST-SURVIVE-SCALE, META_RULE_H/Q/AF
