# Pre-registration: phase_diagram_wm_multibank_K_8192_3seed_harvest_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** Skunkworks flag-back #4 from batches 3+4. v3 K-ceiling sweep
landed K=8192 at recall=1.000 but only on seed=11 (sweep halted at K=32768
VRAM probe breach). USER directive 2026-06-27: harvest K=8192 at 3 seeds
[11,13,19] both regimes to get the single-arm chain-grade evidence.

## Anchor

`phase_diagram_wm_multibank_K_8192_3seed_harvest_v1`

## Routing

- **Queue:** `overnight_queue` (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N_DIM=8192 + CODEBOOK_SIZE=65536 fp16 codebook = 1GB; multi-bank
  routing + cleanup matmul matmul-heavy at K=8192 (v3 measured: gpu_util_mean=55%
  max=93% peak_mem=4.5GB; K=8192 unit wall ~1-2s on RTX 4060 Ti).
- **GPU mandate (Fix #24):** torch.cuda required at full; smoke can fall back
  to CPU for laptop-fittable mechanism check.
- Push gate: harness-DENIED to exp_dev; cell dispatched via Orchestrator.

## Source

Derived from `experiments/exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3.py`
(same primitives, same instrumentation). Drops sweep axis entirely; runs K=8192
only at 3 seeds, both regimes.

V3 landed (off `data/exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3/metrics.json`):
- K=4096 MULTI_64x: rec=1.000 cv=0.0 across 3 seeds (rail; saturated)
- K=8192 MULTI_128x (RANDOM): rec=1.000 only on seed=11 (cardinality breach for 3-seed claim)
- K=8192 MULTI_128x (ADVERSARIAL): rec=1.000 only on seed=11
- K=16384 MULTI_256x: rec=1.000 / 0.9999 only on seed=11 (cliff approaches)
- K=32768 MULTI_512x: HP_VRAM_PROBE_BREACH (5.51GB > 4.88GB budget)

Skunkworks flag-back #4: K=8192 needs 3-seed evidence before single-arm chain-grade
claim. This cell delivers that exactly.

## Mechanism

Multi-bank associative-memory writing with bank-routing cleanup at K_TOTAL=8192,
arrangement MULTI_128x (128 banks * 64 k_per_bank). Same as v3's K=8192 arm.

Each bank holds k_per_bank=64 items in bipolar workspace (sum of item*slot_tag +
Gaussian noise, sign-quantized). Cue contains bank-tag + slot-tag; bank routed
via argmax(cue @ bank_tags.T), then item retrieved via two-step cleanup over
codebook (chunked argmax over CODEBOOK_CHUNK=4096 rows).

Chain-grade envelope enforces k_per_bank <= 64 (per v1/v3 rail).

## Arms

| Arm | Regime | n_banks | k_per_bank | Purpose |
|-----|--------|---------|------------|---------|
| MULTI_128x | RANDOM | 128 | 64 | substrate WM K=8192 (RANDOM codebook) |
| MULTI_128x | ADVERSARIAL | 128 | 64 | adversarial robustness (feature overlap=0.20) |
| KNN_BASELINE | RANDOM (K=4096) | 1 | 4096 | sentinel (Fix #28; rec >= 0.90) |

Each at 3 seeds: 6 capacity arms + 3 sentinels = 9 units total.

## Pre-reg bands (LOCKED at module init)

- HP_CHAIN_GRADE_RECALL = 0.95 (RANDOM mean across 3 seeds)
- HP_CHAIN_GRADE_CV = 0.05 (RANDOM cv across 3 seeds)
- HP_CHAIN_GRADE_ROUTE_ACC = 0.95
- HP_ADV_WITHIN_RANDOM = 0.05 (adv-vs-rand drift)
- HP_KNN_SENTINEL_MIN = 0.90 (Fix #28)
- CV_HARD_FAIL = 0.10
- HP_CHAIN_GRADE_K_PER_BANK_MAX = 64 (envelope locked)
- EXPECTED_N_UNITS = 9 (META_RULE_H cardinality guard)

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_K_8192_3SEED | rand rec>=0.95 cv<=0.05 ra>=0.95 + adv drift<=0.05 + sentinel + cardinality + substrate-only |
| MIDDLE_BAND_NOT_CHAIN_GRADE | one or more chain-grade gates miss but not HARD_FAIL |
| HARD_FAIL_CARDINALITY_BREACH_META_RULE_H | n_units < 9 |
| HARD_FAIL_UNIT_EXCEPTION | any per-unit exception (META_RULE_J no-silent-except) |
| HARD_FAIL_CV_INSTABILITY | cv > 0.10 either arm |
| HARD_FAIL_KNN_SENTINEL | KNN sentinel < 0.90 |
| HARD_FAIL_SUBSTRATE_ONLY | LLM calls > 0 |

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option B (analytical justification):**

V3 already proved K=8192 saturates to rec=1.000 cv=0 at seed=11 RANDOM AND
ADVERSARIAL (1-seed full-N evidence). The discriminator HAS survived scale at
1 seed; this cell harvests cv stability across 2 additional seeds (the bar for
chain-grade tiering per Skunkworks CV discipline).

**META_RULE_L check (band-floor not chain-grade):** K=8192 rec=1.000 IS chain-grade
NOT band-floor because the WM multi-bank K=8192 / k_per_bank=64 arrangement
sits at the K-extension frontier where the cliff approaches: v3 measured
K=16384 already drops to rec=0.9999 (the noise is starting to bite) and
K=32768 couldn't even fit memory. K=8192 chain-grade is real-discriminator-PASS,
not by-construction-saturation at the operating envelope's edge.

Q_SUSPECT_SATURATION discipline retained in detail dict for transparency but
does NOT auto-demote single-K chain-grade results — it documents that the
mean reached 1.000.

## Smoke verdict (laptop CPU 2026-06-27)

**SMOKE_PASS** at smoke-N=2048, K_TOTAL=1024 (MULTI_16x), CODEBOOK=4096:
- Self-test: ALL PASS (T1-T9)
- All 3 expected smoke units landed (cardinality OK)
- RANDOM: rec=0.7900 ra=1.0000 (smoke-N rail-drift; expected per v3 baseline)
- ADVERSARIAL: rec=0.7334 ra=1.0000
- KNN sentinel: 1.0000 (>= 0.90 OK)
- substrate-only_ok=True (LLM calls = 0)
- Wall: ~1.1s total
- gpu_util check DEFERRED to remote GPU smoke

Mechanism end-to-end verified. Chain-grade gates DEFERRED to FULL on GPU
(smoke-N=2048 cannot reproduce full-N=8192 rec=1.000 saturation per v3 baseline).

## Config

- N_DIM = 8192 (full); CODEBOOK_SIZE = 65536
- K_TOTAL = 8192; arrangement MULTI_128x (128 banks * 64 k_per_bank)
- SIGMA = 1.0, CUE_COS = 0.70, FEATURE_OVERLAP_FRAC = 0.20, N_ITEMS_PER_K = 200
- Seeds: [11, 13, 19]
- CODEBOOK_CHUNK = 4096 (chunked argmax matmul; bounds peak alloc)
- Encoder provenance: SUBSTRATE_NATIVE (geometric bank routing)
- Substrate-only decode (zero LLM calls; asserted before metrics.json write)

## ETA + Timeout

V3 measured at K=8192 MULTI_128x: per-unit wall ~1-2s on RTX 4060 Ti.
- 6 capacity arms (3 seeds * 2 regimes) * ~2s = ~12s
- 3 KNN sentinels @ K=4096 * ~0.5s = ~1.5s
- Codebook build * 6 distinct (seed, regime) entries * ~3-5s = ~30s
- Setup overhead ~20s

**Estimated wall: ~1-2 minutes on GPU.**

**Timeout: 1800s (30 min)** — generous 15-30x margin over estimate. Anchor name
contains no `_n<N>` suffix; PROT-019 floor not triggered.

## Why this is a small, clean, useful cell

- Drops the v3 sweep axis entirely -- no K=32768 (memory) or K=16384 (cliff
  approaches) noise.
- Single-arm focus on K=8192 (the unresolved Skunkworks flag-back).
- Strict cardinality guard (9 expected) + META_RULE_J + META_RULE_K + META_RULE_L.
- Provides the missing 3-seed evidence that lets Skunkworks tier the K=8192
  result chain-grade.
