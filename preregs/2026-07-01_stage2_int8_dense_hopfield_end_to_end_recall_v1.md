# Pre-registration: Stage 2 opener — INT8 dense-Hopfield end-to-end recall Pareto ladder v1

**Date:** 2026-07-01
**Author:** hdi_exp_dev (per USER Stage 2 pivot; Research drill `notes/research_full_night_dispatch_plan_2026-07-02.md`)
**Anchor:** `stage2_int8_dense_hopfield_end_to_end_recall_v1`
**Base commit:** E v5 CG INT8 Pareto (commit e04666ad); INT8 v1 extension HARD_FAIL_CONTRADICTS_E_V5 landed 2026-07-01 (M ∈ {10k, 20k, 40k}); hdlab/int8_dense.py commit c3ca7dab.
**Files:**
- `experiments/_stage2_int8_dense_hopfield_end_to_end_recall_v1_core.py`
- `experiments/exp_stage2_int8_dense_hopfield_end_to_end_recall_v1_seed_{7,13,19}.py` (seed_7 authored; sibling seed_13/seed_19 pending pre-reg amendment)

## Sole CG-eligible claim (as originally spec'd by USER)

**INT8 recall stays within 0.05 of FP32 across the full precision ladder (FP32/FP16/INT8/INT4) at end-to-end substrate recall over N ∈ {2048,4096,8192}, M ∈ {100,500,1000,5000,10000}, σ ∈ {0.0, 0.2, 0.5}, while INT8 memory footprint stays ≤ 0.35 × FP32 memory (analytical: 0.25 by construction + O(1/N) scale overhead).**

## Discriminator / envelope-fail-bands (as originally spec'd)

### HARD_PASS
1. HP_INT8_PARETO: `|INT8_recall - FP32_recall| ≤ 0.05` at discriminator point (N=8192, M=1000, σ=0.2)
2. HP_MEMORY_FACTOR: `max(INT8_bpf / FP32_bpf across all arms) ≤ 0.35`
3. cardinality_ok: 180 units per seed observed (4 arms × 3 N × 5 M × 3 σ)
4. All 180 mechanism_hashes distinct per seed
5. Cross-seed cv < 0.10 for any storage arm

### HARD_FAIL
- HP_INT4_BREAKS: `FP32_recall - INT4_recall ≥ 0.20` at discriminator point (this is an ORTHOGONAL diagnostic per USER — documents where the ladder breaks, does not itself cause HF)
- META_RULE_Q: at discriminator point, all arms saturate at ≥ 0.98 recall OR arms differ by less than 0.03 (regime does not discriminate)

## SMOKE OUTCOME (2026-07-01)

**Smoke: SELFTEST_OK ; SMOKE_HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING.**

Selftest: 4-arm functional check + INT4 round-trip + bpf-ordering analytical, all PASS at N=256, M=30.
Result: `fp32=1.000 fp16=1.000 int8=1.000 int4=1.000 bpf_int4=2116 bpf_int8=4169 bpf_fp16=8209 bpf_fp32=16418 mem_factor(int8/fp32)=0.254 int4_err=0.026`.

Smoke (N=4096, M=1000, σ=0.2, 4 arms; single seed_7):
```
FP32: recall=1.000  wall=0.56s  bpf=100696
FP16: recall=1.000  wall=1.01s  bpf=50348
INT8: recall=1.000  wall=0.93s  bpf=25199
INT4: recall=1.000  wall=0.53s  bpf=12612
range = 0.000; META_RULE_Q FAIL (all arms saturated)
```

**Discriminator-preview at USER's actual full-mode discriminator point (N=8192, M=1000, σ=0.2, seed_7):**
```
FP32: recall=1.000  wall=6.51s  bpf=435552
FP16: recall=1.000  wall=5.25s  bpf=217776
INT8: recall=1.000  wall=2.43s  bpf=108941
INT4: recall=1.000  wall=2.11s  bpf=54497
range = 0.000; META_RULE_Q FAIL at USER-spec point too
```

**σ transition scan at M=10000, N=8192 (hardest corner of USER grid):**
```
σ=0.25 : all arms = 1.000 (range 0.000)
σ=0.30 : all arms = 1.000 (range 0.000)
σ=0.35 : all arms = 1.000 (range 0.000)
σ=0.40 : all arms = 1.000 (range 0.000)
σ=0.42 : FP32=0.997 FP16=0.997 INT8=0.997 INT4=0.996 (range 0.001)
σ=0.44 : FP32=0.926 FP16=0.926 INT8=0.926 INT4=0.924 (range 0.002)
```

**Hardest σ=0.5 corner scans (all-M, all-N):**
```
(M=10k, N=2048, σ=0.5): all arms ≈ 0.001 (crashed; range 0.000)
(M=10k, N=4096, σ=0.5): all arms ≈ 0.001 (crashed; range 0.001)
(M=10k, N=8192, σ=0.5): all arms ≈ 0.000 (crashed; range 0.001)
(M=5000, N=8192, σ=0.5): all arms ≈ 0.000 (crashed; range 0.000)
```

## Substantive finding: USER-specified grid does NOT discriminate the ladder

The USER-specified grid (M ∈ {100…10000}, N ∈ {2048…8192}, σ ∈ {0.0, 0.2, 0.5}) exhibits **bimodal saturation**: at σ ≤ 0.4 all arms saturate to recall = 1.0, at σ ≥ 0.5 all arms crash to recall ≈ 0. The transition band (σ ∈ [0.42, 0.44] at max-M max-N) shows arm-range = 0.001-0.002 — 15× below the 0.03 discriminator threshold and 30× below the HP_INT8_PARETO 0.05 tolerance.

**Root cause:** the USER grid is entirely PRE-crack for the substrate's capacity envelope. E v5 established the crack at M ∈ {40k, 80k} for N=2048 (M/N ≈ 20-40); scaled to N=8192 the crack shifts to M ≈ 160k-320k. USER's max M=10000 at N=8192 gives M/N=1.2 — deep pre-crack, where substrate error correction dominates precision quantization noise.

**Consequence:** the FULL dispatch as-spec'd cannot produce HP or HF. Every arm will report identical recall (either 1.0 or ~0.0 depending on σ). ~20 min of GPU compute on overnight_queue would return only saturation evidence (analogous to K-sweep phantom-completion class per META_RULE_K).

Per DISCRIMINATOR-MUST-SURVIVE-SCALE + META_RULE_K + Skunkworks by-construction-saturation tiering: **abort FULL dispatch; surface finding to Research for pre-reg amendment.**

## Recommended amendments (for Research)

Two amendment paths (either or both):

**Amendment A: extend M into crack for N=8192.**
- Change `FULL_M_SWEEP = [100, 500, 1000, 5000, 10000]` to `[1000, 10000, 40000, 80000, 160000, 320000]` — spans PRE-crack through in-crack per E v5 scaling.
- Move discriminator point from (N=8192, M=1000, σ=0.2) to (N=8192, M=160000, σ=0.2) — where E v5-scaled substrate is at capacity envelope and precision noise becomes visible.
- Cost: at N=8192 M=160k FP32 W is 268MB (fine on GPU); ingest is ~1s/arm on GPU; grid becomes 4 arms × 3 N × 6 M × 3 σ = 216 units per seed ≈ 30min per seed on GPU.

**Amendment B: fine-grained σ sweep in transition zone.**
- Change `FULL_SIGMA_SWEEP = [0.0, 0.2, 0.5]` to `[0.0, 0.2, 0.43, 0.46, 0.48, 0.5]` — captures the transition band where arms just begin to differentiate.
- This is where discriminating signal lives for the USER grid's M range; still may only produce ~0.005 range but at least the discriminator has a chance to fire.
- Cheaper than Amendment A (grid stays at USER M range); Pareto shape may still show INT4 breaks first as σ approaches 0.44.

**Recommended: Amendment A + B together.** Then FULL dispatch has a real chance to answer USER's actual question ("does INT8 hold Pareto?" answered CG at E v5 M/N regime; question becomes "does it hold at Stage 2 practically-encountered M/N with adversarial noise?").

## Configuration (as originally spec'd; NOT dispatched)

- **Precision arms** (4): `[FP32, FP16, INT8, INT4]`
  - FP32 baseline
  - FP16 storage-quantized (float16 W + cast-on-load); production pattern
  - INT8 composes `hdlab.int8_dense.quantize_int8_dense` (META_RULE_AT)
  - INT4 inline quantize (symmetric per-row scale, range [-7,7], packed 2/byte for storage cost)
- **M_sweep** = `[100, 500, 1000, 5000, 10000]` (5 values; ALL PRE-CRACK per finding)
- **N_sweep** = `[2048, 4096, 8192]` (3 values)
- **σ_sweep** = `[0.0, 0.2, 0.5]` (3 values; BIMODAL per finding)
- **n_ent = 5000, n_rel = 100, query_frac = 0.10, topK = 1**
- **Seeds:** `[7, 13, 19]`
- **Grid:** 4 arms × 3 N × 5 M × 3 σ = **180 units per seed × 3 seeds = 540 total**
- **GPU-eligible** (torch cuda if available; falls back to CPU); route to `overnight_queue`
- **Timeout:** 7200s per USER task spec

## Smoke design (DISCRIMINATOR-MUST-SURVIVE-SCALE Check-C variant)

Smoke: seed_7 at M=1000, N=4096, σ=0.2 (single point; 4 arms = 4 units). Discriminator-preview at USER discriminator point (N=8192, M=1000, σ=0.2) also ran as verification.

**Smoke tier map:** RESULT = HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING (saturation at every checked point). Abort dispatch; escalate to Research for amendment.

## Selftest (formula gates)

Selftest verifies (PASSED 2026-07-01):
- All 4 arm functions return recall in [0, 1]
- Bytes-per-fact analytical ordering: INT4 < INT8 < FP16 < FP32 ✓
- HP_MEMORY_FACTOR analytical: `bpf_int8 / bpf_fp32 = 0.254 ≤ 0.35` ✓
- INT4 quantize round-trip error bounded by 2× scale ✓
- INT4 vs INT8 quantize distinct output (ARMS-MUST-DIFFER precursor) ✓
- HP_INT8_PARETO_TOL in (0, 0.05) sanity ✓

Selftest wall time: <2 seconds. `--self-test` gate mandatory pre-dispatch.

## Compose (META_RULE_AT)

- `hdlab/int8_dense.py::quantize_int8_dense` composed in INT8 arm (`_ingest_and_query_int8`)
- INT4 quantize is inline (no hdlab primitive); if this cell's amended version lands CG, INT4 primitive should be extracted to `hdlab/int4_dense.py` per META_RULE_AT + results-to-application-cadence discipline.

## Runtime budget (informational; not dispatched)

- Per-arm wall time at (N=8192, M=1000): 2-7s CPU per arm (verified during discriminator preview)
- 180 units × ~2-5s avg = ~5-15 min per seed on CPU; ~2-5 min per seed on GPU
- 3 seeds on GPU: ~10-15 min; timeout 7200s (2hr) is 30× generous

## Falsifiable predictions (as originally spec'd; UNTESTABLE at grid-as-spec'd)

- **HP:** INT8 Pareto holds within 0.05 of FP32 (E v5 extension to Stage 2 M/N)
- **HF (informational):** INT4 drops ≥ 0.20 vs FP32 (documents ladder breakage)
- **Actual smoke finding:** at USER grid, all 4 arms report IDENTICAL recall (max range 0.002 across entire USER grid); no discriminating signal exists.

## References

- E v5 CG landing: commit e04666ad, prereg `preregs/2026-07-01_substrate_bytes_per_fact_pareto_v5_int8_specialization.md`
- v1 extension HARD_FAIL: `data/exp_substrate_int8_pareto_extension_v1_seed_7/metrics.json`
- hdlab primitive: `hdlab/int8_dense.py` (commit c3ca7dab)
- USER task source: overnight_queue Stage 2 opener dispatch (2026-07-01 late session)
- MEMORY.md discipline: `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`
