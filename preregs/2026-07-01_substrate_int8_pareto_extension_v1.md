# Pre-registration: INT8_DENSE Pareto EXTENSION v1

**Date:** 2026-07-01
**Author:** hdi_exp_dev (per Research a004a7e5 Wave-2 §1)
**Anchor:** `substrate_int8_pareto_extension_v1`
**Base commit:** E v5 CG landing at commit e04666ad (INT8=FP32 parity in
capacity crack M in {40k, 80k}, N=2048); hdlab primitive `hdlab/int8_dense.py`
shipped at commit c3ca7dab.
**Source:** `notes/research_phase_diagram_gap_analysis_wave2_2026-07-01.md` §1
**Files:**
- `experiments/_substrate_int8_pareto_extension_v1_core.py`
- `experiments/exp_substrate_int8_pareto_extension_v1_seed_{7,13,19}.py`

## Sole CG-eligible claim

**INT8_DENSE Pareto-dominates BFLOAT16_DENSE / BINARY_DENSE at multiple
regimes beyond the E v5 capacity crack anchor.** Specifically: across a
3-storage × 3-M × 3-N grid, INT8_DENSE holds Pareto-optimal position
(highest recall at lowest bytes-per-fact) at ≥2 of the 3 M points with
seed-consistency (cv < 0.08).

Alternative HP-mode: **regime-conditional storage recipe** — different arm
wins at different M (with seed consistency); still publishable as MB
(regime-conditional MM per Research note), but escalation to CG requires
the ≥2-of-3 dominance case.

## Discriminator / envelope-fail-bands

### HARD_PASS
All of:
1. INT8_DENSE is Pareto majority-winner at ≥2 of 3 M regimes (aggregating
   across the 3 N values via majority-vote per M)
2. Cross-seed recall_cv < 0.08 for INT8_DENSE at those winning M
3. META_RULE_Q at each M: at least one arm recall < 0.95 (regime discriminates)
4. cardinality_ok: 27 units per seed observed (3 arms × 3 M × 3 N)
5. All 27 mechanism_hashes distinct per seed
6. No cross-seed cv ≥ 0.10 for any storage arm at any (M, arm) — full grid

### MIDDLE_BAND
- **Crossover finding:** ≥2 distinct arms win at different M with seed
  consistency (regime-conditional storage recipe). Publishable as MM.
- INT8 Pareto-dominates at only 1 of 3 M
- Cv in [0.08, 0.10) at any winning (M, arm) that would otherwise HP

### HARD_FAIL
- BINARY_DENSE or BFLOAT16_DENSE wins Pareto at ≥2 of 3 M
  (contradicts E v5 CG finding — worth investigating separately)
- META_RULE_Q breach: every M point saturates (all arms ≥ 0.95 recall) —
  regime does not discriminate
- Any cross-seed cv ≥ 0.10 for any storage arm
- cardinality_ok fails (META_RULE_H HARD_FAIL_CARDINALITY_BREACH)
- Mechanism-hash collision (META_RULE_AX HARD_FAIL)

## Configuration (full mode)

- **Storage arms** (3): `[INT8_DENSE, BFLOAT16_DENSE, BINARY_DENSE]`
  - INT8_DENSE composes `hdlab.int8_dense.quantize_int8_dense` (META_RULE_AT
    per Research task requirement)
  - BFLOAT16_DENSE uses `torch.bfloat16` W-accumulate + query path
  - BINARY_DENSE uses `sign(W)` bit-packed (Tier-3 anchor consistent with E v5)
- **M_sweep** = `[10000, 20000, 40000]` (3 values)
  - M=10k: PRE-crack — higher recall floor, probes wire-cost only
  - M=20k: MID-crack — bytes/fact matters, INT8 lead expected to persist
  - M=40k: CG CALIBRATION ANCHOR from E v5 (in-crack; recall drops)
- **N_sweep** = `[2048, 4096, 8192]` (3 values)
  - N=2048: E v5 anchor calibration point
  - N=4096, N=8192: probes scaling of storage-arm dominance
- **n_ent = 5000, n_rel = 100, query_frac = 0.10, topK = 1**
- **Query noise:** 30% bipolar flip (same "CLEAN" baseline noise regime as E v5)
- **Seeds:** `[7, 13, 19]`
- **Grid:** 3 arms × 3 M × 3 N = **27 units per seed × 3 seeds = 81 total**
- **CPU-eligible** (numpy + torch cpu); route to `remote_cpu_queue`

## Smoke design (DISCRIMINATOR-MUST-SURVIVE-SCALE per META_RULE)

Smoke: **seed=7 at M=20000, N=4096 (single point).**

Rationale (Check-C variant of MUST-SURVIVE-SCALE):
- M=20k is the mid-crack regime where INT8's Pareto lead is the whole cell's
  point. If INT8 doesn't lead at (M=20k, N=4096) on seed_7, the full grid
  won't produce HP either.
- N=4096 is between the E v5 anchor (N=2048) and the high boundary (N=8192).
  Smoke at N=4096 verifies the arm implementation scales.
- Single-point smoke is small enough to run <60s on laptop CPU.

**Smoke tier map:**
- If INT8 recall > BFLOAT16 recall AND INT8 recall > BINARY recall at
  (M=20k, N=4096) → smoke HARD_PASS → dispatch full 3 seeds
- If BFLOAT16 or BINARY wins at smoke → smoke MIDDLE_BAND → dispatch full to
  probe regime-conditionality (still expected outcome)
- If all arms saturate (all ≥ 0.95) → smoke HARD_FAIL — abort dispatch (need
  different M/N for smoke; likely M=20k below crack for N=4096)
- If any arm errors / cardinality wrong → smoke HARD_FAIL — fix cell

## Selftest (formula gates)

Selftest verifies:
- All arm functions return recall in [0, 1]
- Bytes-per-fact analytical ordering: BINARY < INT8 < BFLOAT16 (correctness
  of storage-cost formulas)
- INT8_LEAD_TOLERANCE constant in (0, 0.05)
- Arms produce finite recalls at a tiny test grid (M=30, N=256)

Selftest wall time: <5 seconds. `--self-test` gate mandatory pre-dispatch.

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` composed in INT8_DENSE arm
  (`_ingest_and_query_int8`). See core file line invoking
  `W_int8, scale_row = quantize_int8_dense(Wf)`.

## Runtime budget

- Per E v5 timings: N=2048, M=40k+80k, 4 arms, 1 seed = ~2.4 s laptop CPU.
- Extrapolation to full: 27 units × ~1-5 s/unit (N-dependent scaling)
  × 3 seeds = ~3-8 min per full run on laptop CPU; remote CPU similar or
  slightly slower. Per-seed timeout: 900 s (15 min) is generous.

## Falsifiable predictions

- **HP:** INT8_DENSE Pareto-dominant at ≥2 of 3 M with cv<0.08
  (extends E v5 CG to regime-generalized recipe)
- **MB:** INT8 dominates at some M but not others (regime-conditional storage
  recipe; expected outcome if BFLOAT16 wins at PRE-crack M=10k where FP
  precision matters more relatively to storage)
- **HF:** BINARY or BFLOAT16 wins broadly (contradicts E v5 finding)

## References

- Research source: `notes/research_phase_diagram_gap_analysis_wave2_2026-07-01.md` §1
- E v5 pre-reg: `preregs/2026-07-01_substrate_bytes_per_fact_pareto_v5_int8_specialization.md`
- hdlab primitive: `hdlab/int8_dense.py` (commit c3ca7dab)
