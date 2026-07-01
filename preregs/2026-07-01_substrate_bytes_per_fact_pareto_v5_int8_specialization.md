# Pre-registration: bytes_per_fact_pareto v5 INT8 SPECIALIZATION

**Date:** 2026-07-01
**Author:** hdi_exp_dev (per Skunkworks 920a9870 recommendation)
**Anchor:** `substrate_bytes_per_fact_pareto_v5`
**Base commit:** `e04666ad` (v4 M-ultra-extended landed MIDDLE_BAND;
per-arm metrics confirm INT8=FP32 recall parity within 0.001 at both
M=40k and M=80k, with INT8 at 0.25x FP32 bytes-per-fact)
**Files:**
- `experiments/_substrate_bytes_per_fact_pareto_v5_core.py`
- `experiments/exp_substrate_bytes_per_fact_pareto_v5_seed_{7,13,19}.py`

## Sole CG-eligible claim

**INT8 is Pareto-optimal in the M=40k-80k capacity crack.**

That is: at both M=40000 AND M=80000 (N_DIM_DENSE=2048, 5000 ent x 100 rel,
top1 recall with 30% bipolar query noise), INT8_DENSE achieves recall
statistically indistinguishable from FP32_DENSE (mean gap within 0.005) while
storing at most 0.30x the bytes-per-fact of FP32_DENSE, and this holds
consistently across seeds {7, 13, 19} (cross-seed cv < 0.10 on both arms).

No other arm claim is CG-eligible in v5. Other arms are:
- **FP32_DENSE**: positive-control baseline (required for the parity claim).
- **BINARY_DENSE**: Tier 3 anchor. BINARY recall must fall BELOW INT8 recall
  at both M so the tier ordering (Tier 1 FP32 ~ Tier 2 INT8 > Tier 3 BINARY)
  is empirically confirmed.
- **POSITIVE_CONTROL_NO_QUANT**: identity to FP32 path (invokes the same
  ingest+query function). Its recall must equal FP32 recall exactly per seed.
  Guards against unintended nondeterminism / accidental drift in the FP32
  code path.

## Discriminator / envelope-fail-bands

### HARD_PASS
All of:
1. `INT8_recall_mean >= FP32_recall_mean - 0.005` at M=40000
2. `INT8_recall_mean >= FP32_recall_mean - 0.005` at M=80000
3. `INT8_bytes_per_fact <= 0.30 * FP32_bytes_per_fact` at M=40000
4. `INT8_bytes_per_fact <= 0.30 * FP32_bytes_per_fact` at M=80000
5. `INT8_recall_cv < 0.10` and `FP32_recall_cv < 0.10` at both M
6. `BINARY_recall_mean < INT8_recall_mean` at both M (Tier 3 anchor)
7. `POSITIVE_CONTROL recall == FP32 recall` exactly per seed at both M
8. `cardinality_ok`: 4 arms x 2 M = 8 units per seed observed
9. Four mechanism_hashes distinct

### MIDDLE_BAND
- Gates 1+3 pass at M=40k but 2+4 fail at M=80k (partial claim), OR
- Gates 1+2+3+4 pass but cross-seed cv >= 0.10 at either M

### HARD_FAIL
- `INT8_recall_mean < FP32_recall_mean - 0.005` at either M
- Positive-control (identity) drift
- Cardinality breach

## Configuration (full mode)

- `N_DIM_DENSE = 2048`
- `M_sweep = [40000, 80000]`
- `n_ent = 5000`, `n_rel = 100`, `query_frac = 0.10`
- Query noise: 30% bipolar flip
- top1 recall
- Seeds: [7, 13, 19]
- Arms: [FP32_DENSE, INT8_DENSE, BINARY_DENSE, POSITIVE_CONTROL_NO_QUANT]
- 4 x 2 = 8 units per seed x 3 seeds = 24 total units
- CPU-eligible (numpy + torch cpu); route to `remote_cpu_queue`

## Smoke design (DISCRIMINATOR-MUST-SURVIVE-SCALE)

Smoke uses the SAME M_sweep and N_DIM as full to guarantee the parity claim is
testable at the exact regime where CG-eligibility lives. This is the correct
choice because:
- The claim is regime-specific (M=40k-80k capacity crack); a smaller-N smoke
  wouldn't verify anything about the sub-claim.
- Wall time at N=2048, M=80k, 4 arms is tractable on CPU (v4 seed_7 smoke ran
  in ~5-10 min per seed at similar config).

Smoke passes if seed_7 finishes at both M with per-arm recalls populated + the
INT8 vs FP32 parity + compression gates fire on the smoke seed.

## Cross-cell context

- v4 (`e04666ad`) landed MB with 7 arms; per-arm metrics show INT8=FP32 recall
  identical to 4 decimals at both M points. v5 strips to the 4 arms that
  isolate this sub-claim and adds a 3-seed cross-seed verification the v4 grid
  couldn't afford (v4 had per-seed 1x cross-seed check across 42 units).
- Per META_RULE_H: sweep-axis cardinality declared upfront (8 units/seed).
- Per META_RULE_Q ceiling saturation: NOT applicable to v5 because recall
  at M=40k and M=80k is far below 0.995 (v4 showed ~0.39 and ~0.12 at seed_7).

## Timeout justification

Formula: `timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`
Smoke and full use identical grid; smoke_seeds=1 full_seeds=1 (chunked per-file);
FULL_N==smoke_N so scaling factor = 1. Post-smoke, timeout = ceil(1.5 * smoke_wall_s).
Expected smoke wall: 5-15 min (v4 per-arm at M=80k was ~30-60s x 4 arms x 2 M = ~4-8 min).
Reasonable full timeout: 1800s (30 min) per seed file.

## Envelope-fail-bands (structural)

- If INT8 parity holds at M=40k only -> MIDDLE_BAND (partial claim)
- If INT8 parity fails at M=40k -> HARD_FAIL (sub-claim broken at even
  underload; v4 evidence would contradict)
- If cross-seed cv >= 0.10 at either M -> MIDDLE_BAND (v4 single-seed
  parity might not survive cross-seed noise)
- If POSITIVE_CONTROL drifts from FP32 -> HARD_FAIL identity-broken
- Anti-BIAS-13/14/15 (contamination/regime/mismatch): identical regime as v4;
  same encoder; deterministic query set per seed; no cross-seed data leakage.

## What HARD_PASS proves (and doesn't)

HARD_PASS proves: at this specific regime (N=2048, KG 5000x100, 30%
noise), INT8 dequantized inner-product retrieval matches FP32 within 0.005
recall while cutting storage 4x, robustly across 3 seeds. This is a
production-relevant compression claim: 4x memory reduction for zero recall
loss in the mid-capacity operating band.

HARD_PASS does NOT prove:
- Parity at other N_DIM (not tested)
- Parity at M outside [40k, 80k] (not tested)
- Parity under different noise models or non-uniform KG structure
- Anything about INT4, FP16, BFLOAT16, or sparse arms (v5 dropped them
  to sharpen the sub-claim)
