# Pre-reg: substrate_compose_freq_routing_v4_hparam_sweep

**Anchor:** `substrate_compose_freq_routing_v4_hparam_sweep`
**Author:** exp_dev (Agent Teams teammate, spawn 2026-06-24)
**Filed:** 2026-06-24 (UTC; before dispatch)
**Cell:** `experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py`
**Lane:** 1 (substrate-native)
**Queue:** `overnight_queue` (GPU) -- matmul-heavy at N=8192
**Timeout:** 7200s (per USER cell spec; D1 roofline gates extrapolated wall to <0.8x = 5760s)

---

## 1. Goal + provenance

v3 ARM_FREQ_ROUTED_K2 landed MIDDLE_BAND at BPC=7.2096 (cv=0.0002), JUST 0.01 BPC
above the HARD_PASS bar of 7.20. v3 sanity rail passed (baseline 7.3065 matches
fair_harness ref). v3 provenance is clean.

This v4 cell is a focused **6-arm hparam sweep** around v3's best FREQ config
to push past the 7.20 cap and ideally toward the 6.95 chain-grade band.

**v3 reference numbers** (data/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun/metrics.json):
- ARM_BASELINE_FAIR_HARNESS: BPC=7.3065 (cv=0.0018)
- ARM_THETA_PHASE_TWO_W: BPC=7.2349 (cv=0.0019) -- lift 0.072 over baseline
- ARM_FREQ_ROUTED_K2: BPC=7.2096 (cv=0.0002) -- lift 0.097 over baseline (LEAD)
- ARM_ORTHOG_SUBSPACE: BPC=7.4315 (cv=0.0016) -- HURT
- elapsed_s = 1261s (3 seeds, 4 arms, N_DIM=8192)
- gpu_peak_mem_gb = 3.45

v3's FREQ config (the one being swept around): `freq_rank=100, lr_high=0.5,
lr_rare=0.2, n_steps=1000`.

---

## 2. Arms (6) -- apples-to-apples; one knob per arm

**ALL arms** use: `N_DIM=8192, V=4000, N_TRAIN=100000, N_HELD=20000, 3 seeds
[7, 17, 23], text8, word2vec sparse-bipolar f=0.05, INGEST_BATCH=64, STDP_WEIGHT=0.5`.

| Arm | freq_rank | lr_high | lr_rare | n_steps | Tests |
|---|---|---|---|---|---|
| ARM_BASELINE | n/a | n/a | n/a | n/a | sanity rail (Hebbian baseline; must match 7.3065 +/- 0.05) |
| ARM_FREQ_V3_REPRO | 100 | 0.5 | 0.2 | 1000 | reproduces v3 7.21 +/- 0.02 (within-cell reproducibility check) |
| ARM_FREQ_DEEPER_TRAIN | 100 | 0.5 | 0.2 | **2000** | more training closes the 0.01 gap? |
| ARM_FREQ_BIGGER_RANK | **200** | 0.5 | 0.2 | 1000 | more high-LR coverage helps? |
| ARM_FREQ_SHARPER_GRADIENT | 100 | **1.0** | 0.2 | 1000 | more aggressive plasticity on common tokens lifts? |
| ARM_FREQ_COMBINE_W_THETA | 100 | 0.5 | 0.2 | 1000 + theta_alphas=[0.3,0.5,0.7] | FREQ x THETA two-W composition (4 matrices) -- additive lift? |

The COMBINE arm uses a new kernel `build_logits_freq_combine_w_theta_gpu` (4
matrices: `W_freq_enc, W_freq_ret, W_rare_enc, W_rare_ret`) with phase-alternated
cf-RPE (encoding) and STDP-antisymmetric (retrieval) updates routed by token freq.
Readout is per-token routed by ITS freq class with alpha-mixed enc/ret logits.

---

## 3. HARD bands (PRE-REG; pass/fail symmetric per USER negativity-bias rule)

**Sanity rail (mandatory):**
ARM_BASELINE BPC within +/-0.05 of fair_harness ref 7.3065.
If drift > 0.05 in `full` mode -> `HARD_FAIL_PROVENANCE`.

**HARD_PASS_CHAIN_GRADE** (the chain-grade win):
- any FREQ-variant BPC <= 6.95
- AND beats ARM_BASELINE by >= 0.35 BPC
- AND CV <= 0.03
- AND sanity_rail OK

**HARD_PASS_CAP_BROKEN** (the targeted v4 win):
- any FREQ-variant BPC <= 7.20
- AND beats ARM_BASELINE by >= 0.10 BPC
- AND sanity_rail OK
- (no CV gate beyond the global CV_MAX=0.05 cap)

**HARD_FAIL_NOTUNING** (the targeted v4 negative):
- ALL 5 FREQ-variants within +/- 0.03 BPC of v3's reference 7.2096
- (tuning produced no movement; the 0.01 gap to HARD_PASS is not closable via
  these 4 knobs at this regime)

**HARD_FAIL_HURT:** all 5 FREQ-variants BPC >= baseline (heterogeneous HURTS at production scale)

**HARD_FAIL_DECISIVE:** all 5 FREQ-variants BPC >= 7.30 (frequency-routed cap is structural)

**MIDDLE_BAND_HIGH_CV:** best het arm CV > 0.05 (seed-unstable; not cert-graded even if mean passes)

**MIDDLE_BAND_PARTIAL_SIGNAL:** best het arm BPC in [7.20, 7.30] (sub-cap-breaking)

---

## 4. Discriminator (load-bearing per Fix #28)

Skunkworks (and any cert-owner) should READ PER-ARM METRICS, not verdict_msg,
when ruling on this cell. The verdict_msg includes the
`max_distance_from_v3` aggregate; per-arm BPC sits in `detail.by_arm_agg.<arm>.bpc_best_mean`.

- **If ARM_FREQ_DEEPER_TRAIN passes but ARM_FREQ_V3_REPRO doesn't** -> more training
  is the lever (could be hit at 3x or 4x N_STEPS but we don't test that here)
- **If ARM_FREQ_SHARPER_GRADIENT passes** -> learning rate is the lever
- **If ARM_FREQ_BIGGER_RANK passes** -> coverage is the lever (rank=200 is exposing more
  common-token paths to the high-LR route)
- **If ARM_FREQ_COMBINE_W_THETA shows ADDITIVE lift** (target BPC ~7.13 if the
  FREQ +0.097 and THETA +0.072 lifts both stack independently) -> architectural
  composition works; substantial Stage 2 finding
- **If ARM_FREQ_V3_REPRO is OUTSIDE 7.21 +/- 0.02** -> reproducibility FAIL; we
  cannot trust within-cell results until we understand the drift. (Recorded in
  `detail.v3_repro.ok = false` but does NOT block PASS verdicts -- it's a flag,
  not a gate.)

---

## 5. Per-Q discipline (Fix #28; by-construction-saturation check)

This cell is tuned around a 7.21 baseline; we DO NOT expect any 1.000 results.
This is honest middle-band hparam tuning at production-grade BPC. No
by-construction-saturation concern at this regime.

LLM-call counter is asserted == 0 at metrics-write time (`detail.llm_forward_calls_total`).

---

## 6. Operating disciplines (pre-dispatch checklist)

- [x] D1 roofline probe: model claims `per_seed_wall = 9.87 * freq_v3_unit + 25s`
      where freq_v3_unit at N=8192/100k = ~85s; full 3-seed wall = ~2592s.
      Headroom vs 7200s timeout = 2.78x (asserted in ST20 self-test).
- [x] D2 atexit + per-seed checkpoint via `experiments/_seed_checkpoint.py`
- [x] Self-test PASS gate (20 STs; all pass on local CPU; `--smoke` deferred per USER embargo)
- [x] Per Fix #24 GPU: `torch.cuda + batched ops` mandatory. v3 GPU peak was 3.45 GB;
      v4 with 4 W-matrices for COMBINE may peak ~6 GB (still well below 24 GB).
- [x] ASCII only
- [x] Pre-reg committed before dispatch
- [x] Path-scoped commits

---

## 7. Self-test discipline (per USER directive)

20 self-tests run in `_instrumentation_selftest()`. Key new v4 tests:
- **ST14** asserts the 6-arm ARMS set + matching `ARM_FREQ_CONFIGS` dict
- **ST17** asserts the new `build_logits_freq_combine_w_theta_gpu` produces
  valid alpha_stack with finite enc-ret bank correlations per route
- **ST18** measures actual freq-routed wall at n_steps=50 vs n_steps=100 and
  asserts the ratio is in [1.2, 4.0] (validates the 2x cost claim for
  ARM_FREQ_DEEPER_TRAIN). Local CPU run: 1.80-1.93x (in band).
- **ST20** asserts `expected_full_wall / requested_timeout >= 1.5x` headroom

These match the USER discipline `assert measured values match expected BEFORE
dispatching full run`.

---

## 8. Expected wall-clock budget

Per-seed (cost model):
- ARM_BASELINE: ~50s (v3 measured)
- ARM_FREQ_V3_REPRO: ~85s (v3 FREQ measured)
- ARM_FREQ_DEEPER_TRAIN: ~170s (2x v3 FREQ)
- ARM_FREQ_BIGGER_RANK: ~85s (same matmul cost)
- ARM_FREQ_SHARPER_GRADIENT: ~85s (same matmul cost)
- ARM_FREQ_COMBINE_W_THETA: ~170s (4 W matrices, ~2x v3 FREQ)
- Overhead (encoder build + corpus load + atexit + ckpt writes): ~25s

Per-seed total: ~670s. 3 seeds: ~2010s.
With 1.5x safety against unmodeled overhead: ~3015s.
**Requested timeout: 7200s** (2.4x model estimate; D1 roofline will refuse if
extrapolation exceeds 0.8 * 7200 = 5760s).

---

## 9. Routing (cell-author cannot push; routes via Orchestrator)

- Cell: `experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py`
- Prereg: this file
- Queue: `overnight_queue` (GPU)
- Timeout: 7200s
- Push lane: HEALTHY (USER reports verified after filter-repo + force-push earlier today)
- Push is harness-DENIED to exp_dev; Orchestrator handles the dispatch via
  `tools/orchestrator/queue_add.sh overnight_queue ...` with HDLAB_QUEUE_ADD_ON_REMOTE
- Self-test gate is the only validation before dispatch (USER --smoke embargo)
- Orchestrator runs `--smoke` skip via `--skip-smoke` flag

---

## 10. What this cell DOES NOT show

- Does NOT test joint multi-knob optima (only one-knob-at-a-time variants)
- Does NOT explore K>2 routing (e.g., 3-way freq tiers)
- Does NOT stack modern-Hopfield cleanup
- Does NOT verify the encoder is the bottleneck (separate cell)
- Does NOT test corpus size scaling
- Does NOT test V scaling
- Reproducibility-FAIL of ARM_FREQ_V3_REPRO would NOT block a passing verdict
  (recorded as a flag in `detail.v3_repro.ok`); cert-owner should weigh

---

## 11. Cites

- `experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py` (v3 base)
- `data/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun/metrics.json` (v3 numbers)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (sanity rail 7.3065)
- USER cell spec 2026-06-24 (in-conversation; recorded in exp_dev handoff)
