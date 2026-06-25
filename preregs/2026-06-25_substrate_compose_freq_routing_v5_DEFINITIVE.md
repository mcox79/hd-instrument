# Pre-reg: substrate_compose_freq_routing_v5_DEFINITIVE

**Anchor:** `substrate_compose_freq_routing_v5_DEFINITIVE`
**Author:** exp_dev (coordinated blitz Agent 3 of 3, 2026-06-25)
**Filed:** 2026-06-25 (UTC; before dispatch)
**Cell:** `experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py`
**Lane:** 1 (substrate-native)
**Queue:** `overnight_queue` (GPU)
**Timeout:** 7200s (D1 roofline gates extrapolated wall to <0.8x = 5760s)

---

## 1. Goal + provenance

v4 ARM_FREQ_DEEPER_TRAIN landed `CHAIN_GRADE_PARTIAL` at BPC=7.159, CV=0.0029 (3 seeds [7,17,23], N=8192, n_steps=2000). v4 was the **first Stage 2 architectural win** but Skunkworks ruled NOT DEFINITIVE because:
- Only 3 seeds (tighter cv estimate desirable)
- Single config (N=8192 only); could be config-fragile
- Single knob-tune (deeper training); architectural advantage may not generalize

v5 converts to DEFINITIVE via:
1. **5 seeds** [7, 13, 17, 23, 29] (was 3)
2. **Cross-N replication**: same FREQ_DEEPER kernel at N_DIM=4096 as well as N=8192
3. **Upper-bound n_steps probe**: FREQ_DEEPER at n_steps=3000 at N=8192

**v4 reference numbers** (`data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json`):
- ARM_BASELINE: 7.3065 (rail OK; cv low)
- ARM_FREQ_V3_REPRO: 7.2096 (v3 reproduction perfect)
- ARM_FREQ_DEEPER_TRAIN: **7.159** (cv=0.0029)
- ARM_FREQ_BIGGER_RANK: 7.197
- ARM_FREQ_SHARPER_GRADIENT: 7.189
- ARM_FREQ_COMBINE_W_THETA: 7.365 (HURT; motivates v6 SEGREGATED cell)

---

## 2. Arms (5) -- apples-to-apples; cross-config replication

**ALL arms** use: `V=4000, N_TRAIN=100000, N_HELD=20000, 5 seeds [7, 13, 17, 23, 29],
text8, word2vec sparse-bipolar f=0.05, INGEST_BATCH=64, STDP_WEIGHT=0.5,
FREQ_LR_HIGH=0.5, FREQ_LR_RARE=0.2, FREQ_ROUTE_RANK=100`.

| Arm | N_DIM | n_steps | Type | Tests |
|---|---|---|---|---|
| ARM_BASELINE_N8192 | 8192 | n/a | Hebbian baseline | sanity rail; must match 7.3065 +/- 0.05 |
| ARM_FREQ_DEEPER_N8192 | 8192 | 2000 | FREQ k=2 | reproduce v4 7.159 +/- 0.05 at 5 seeds (primary) |
| ARM_BASELINE_N4096 | 4096 | n/a | Hebbian baseline | sanity rail at N=4096 (this cell establishes ref) |
| ARM_FREQ_DEEPER_N4096 | 4096 | 2000 | FREQ k=2 | cross-config replication; tests architectural advantage isn't N=8192-specific |
| ARM_FREQ_DEEPER_NSTEPS_3000 | 8192 | 3000 | FREQ k=2 | upper-bound of training-depth lever |

**Phase-diagram scan baked in**: 2 N values (8192, 4096) cross 2 n_steps values (2000, 3000) on the FREQ arm. Defines operating envelope around v4 winner.

---

## 3. HARD bands (PRE-REG; PROSPECTIVE per Skunkworks META_RULE_retrospective_band_correction)

v5 is a genuine new cell -- 5 seeds + cross-N replication is not a retrofit.

**Sanity rails (mandatory):**
- ARM_BASELINE_N8192 BPC within +/-0.05 of fair_harness ref 7.3065
- ARM_BASELINE_N4096 BPC finite AND lower than UNIGRAM (this cell establishes the ref)

**HARD_PASS_CHAIN_GRADE_DEFINITIVE** (the DEFINITIVE win):
- ARM_FREQ_DEEPER_N8192 BPC <= 7.20
- AND ARM_FREQ_DEEPER_N4096 beats ARM_BASELINE_N4096 by >= 0.10 BPC (cross-config replication)
- AND ARM_FREQ_DEEPER_N8192 beats ARM_BASELINE_N8192 by >= 0.10 BPC
- AND CV <= 0.03 across 5 seeds on ARM_FREQ_DEEPER_N8192
- AND both sanity rails pass

**HARD_PASS_SINGLE_CONFIG_REPLICATION** (5-seed replication of v4):
- ARM_FREQ_DEEPER_N8192 BPC <= 7.20
- AND beats ARM_BASELINE_N8192 by >= 0.10
- AND CV <= 0.05
- AND sanity rail ARM_BASELINE_N8192 OK
- (cross-N missed but main result replicated)

**HARD_FAIL_NULL_REPLICATION** (v4 was noise):
- ARM_FREQ_DEEPER_N8192 BPC >= 7.30

**MIDDLE_BAND_HIGH_CV:** ARM_FREQ_DEEPER_N8192 cv > 0.05

**MIDDLE_BAND_PARTIAL_REPLICATION:** ARM_FREQ_DEEPER_N8192 BPC in [7.20, 7.30]

**MIDDLE_BAND_INTER_GAP:** ARM_FREQ_DEEPER_N8192 outside HP+MB+HF bands

---

## 4. Discriminator (load-bearing per Fix #28)

Per-arm BPC in `detail.arm_bpc.<arm>` and `detail.by_arm_agg.<arm>.bpc_best_mean`.

**Cross-N check:** `detail.crossN_check`:
- `n8192_lift`: BASELINE_N8192 minus FREQ_DEEPER_N8192
- `n4096_lift`: BASELINE_N4096 minus FREQ_DEEPER_N4096
- `both_pass`: both lifts >= 0.10

**v4 replication check:** `detail.v4_replication_check.ok` (FREQ_DEEPER_N8192 within 0.05 of 7.159)

**n_steps upper-bound check:** `detail.nsteps_upper_bound_check`:
- `delta_2000_to_3000`: FREQ_DEEPER_N8192 minus FREQ_DEEPER_NSTEPS_3000
- `plateaued`: |delta| <= 0.02 (training is depth-saturated)

**Interpretation guide (Fix #28: read per-arm, not verdict_msg):**
- If `crossN_check.both_pass=True` AND `cv_seg_g <= 0.03` -> CHAIN_GRADE_DEFINITIVE (architecture works across configs)
- If `crossN_check.n8192_lift >= 0.10` but `n4096_lift < 0.10` -> single-config replication only (N=8192-specific; architecture may be config-fragile)
- If `v4_replication_check.ok=False` AND BPC in MB range -> v4 result was noise OR config-drift; cert-owner should investigate
- If `nsteps_upper_bound_check.plateaued=True` -> training depth is the only lever; more n_steps will not help
- If `nsteps_3000` BPC < `nsteps_2000` BPC by >= 0.05 -> training-depth lever has more room

---

## 5. Per-Q discipline (Fix #28; by-construction-saturation check)

This cell tunes around 7.159; we DO NOT expect any 1.000 results. Honest middle-of-band replication + cross-config test at production BPC. No by-construction-saturation concern.

LLM-call counter is asserted == 0 at metrics-write time.

---

## 6. Operating disciplines (pre-dispatch checklist)

- [x] D1 roofline probe: model claims per-seed = 50 + 170 + 13 + 43 + 255 + 25 = 556s; 5 seeds = 2780s; headroom vs 7200s = 2.59x (asserted in ST16)
- [x] D2 atexit + per-seed checkpoint
- [x] Self-test PASS gate (16 STs; all pass on local CPU)
- [x] Per Fix #24 GPU: `torch.cuda + batched ops` mandatory
- [x] ASCII only
- [x] Pre-reg committed before dispatch
- [x] Path-scoped commits

---

## 7. Self-test discipline

16 self-tests run in `_instrumentation_selftest()`:
- ST11 asserts 5-arm ARMS set + matching ARM_CONFIGS dict
- ST13 asserts 5 seeds in full + N values in {4096, 8192} + n_steps in {2000, 3000}
- ST14 asserts ARM_CONFIGS well-formed (type in {BASELINE, FREQ}; FREQ has freq_rank/lr_high/lr_rare/n_steps positive)
- ST15 measures actual freq-routed wall ratio at 50 vs 100 n_steps; asserts in [1.2, 4.0]
- ST16 asserts expected_full_wall / requested_timeout >= 1.3x headroom

These match the USER discipline `assert measured values match expected BEFORE dispatching full run`.

---

## 8. Expected wall-clock budget

Per-seed (cost model):
- ARM_BASELINE_N8192: ~50s (v3 measured Hebbian @ N=8192)
- ARM_FREQ_DEEPER_N8192: ~170s (v4 measured)
- ARM_BASELINE_N4096: ~13s (Hebbian scales N^2: 50 * (4096/8192)^2 = 12.5)
- ARM_FREQ_DEEPER_N4096: ~43s (FREQ scales ~N^2: 170 * 0.25 = 42.5)
- ARM_FREQ_DEEPER_NSTEPS_3000: ~255s (170 * 1.5)
- Overhead (encoder + corpus + ckpt): ~25s

Per-seed total: ~556s. 5 seeds: ~2780s.
With 1.5x safety: ~4170s. **Requested timeout: 7200s** (2.59x model; D1 roofline gates <0.8 * 7200 = 5760s).

Note: encoder is built per-N per-seed (2 N values means 2 word2vec re-projections per seed). The 25s overhead figure includes both encoder builds. Cost model conservative.

---

## 9. Routing (cell-author cannot push)

- Cell: `experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py`
- Prereg: this file
- Queue: `overnight_queue` (GPU)
- Timeout: 7200s
- Push lane: HEALTHY
- Push is harness-DENIED to exp_dev; Orchestrator handles dispatch via
  `tools/orchestrator/queue_add.sh overnight_queue ...` with HDLAB_QUEUE_ADD_ON_REMOTE
- Self-test gate is the only validation before dispatch (USER --smoke embargo)

---

## 10. What this cell DOES NOT show

- Does NOT test other knobs (rank/lr/architectural-composition); v4 already swept these
- Does NOT test V scaling
- Does NOT test corpus size scaling
- Cross-N at only TWO points (4096 + 8192); doesn't characterize full N curve
- The n_steps=3000 upper-bound arm is at N=8192 only
- Does NOT test the FREQ + THETA combination (v4 COMBINE; v6 SEGREGATED cell handles that drill)

---

## 11. Cites

- `experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py` (v4 base; ARM_FREQ_DEEPER_TRAIN=7.159 CHAIN_GRADE_PARTIAL)
- `data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json` (v4 measured numbers)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (sanity rail 7.3065)
- USER coordinated blitz directive 2026-06-25 (Agent 3 of 3; in-conversation)
- Skunkworks META_RULE_retrospective_band_correction (PROSPECTIVE bands required for genuine new cells)
