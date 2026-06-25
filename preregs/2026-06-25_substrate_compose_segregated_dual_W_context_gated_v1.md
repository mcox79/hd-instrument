# Pre-reg: substrate_compose_segregated_dual_W_context_gated_v1

**Anchor:** `substrate_compose_segregated_dual_W_context_gated_v1`
**Author:** exp_dev (coordinated blitz Agent 3 of 3, 2026-06-25)
**Filed:** 2026-06-25 (UTC; before dispatch)
**Cell:** `experiments/exp_substrate_compose_segregated_dual_W_context_gated_v1.py`
**Lane:** 1 (substrate-native)
**Queue:** `overnight_queue` (GPU)
**Timeout:** 7200s

---

## 1. Goal + provenance

v4 ARM_FREQ_COMBINE_W_THETA landed `HURT` at BPC=7.365 vs baseline 7.3065 (worse by 0.06 BPC). The architecture used 4 matrices (W_freq_enc, W_freq_ret, W_rare_enc, W_rare_ret) with cf-RPE on phase 0 and STDP-antisymmetric on phase 1, **both updating the same W tensor**.

**Drill conclusion** (per USER recommendation): combining FREQ_ROUTED + THETA_PHASE on the SAME W creates FDM intermodulation. Two carriers (cf-RPE content + STDP timing) sharing a channel mix the way two FM signals on one frequency would. The brain solves this by **functional segregation**, not phase multiplexing: theta = WHEN (sequence/timing), gamma = WHAT (content/pattern-completion); the two are nested-but-segregated across function-domain, not phase-alternated on the same synaptic dynamic.

**v1 alternative architecture** -- SEGREGATED dual-W banks with CONTEXT-GATED mixer:
- `W_when` (theta-equivalent): updates **ONLY** via STDP-antisymmetric (sequence-timing signal). Captures "WHEN does target come next given context."
- `W_what` (gamma-equivalent): updates **ONLY** via cf-RPE (content-prediction error). Captures "WHAT content fits the local pattern."
- Mixer at retrieval: per-query gate weight via sigmoid on context norm; high-info context -> trust WHAT more; low-info -> trust WHEN more.

**Key architectural distinction from v4 COMBINE_W_THETA**:
- v4: W_freq receives BOTH cf-RPE (phase 0) AND STDP (phase 1) on shared W -> intermod
- v1: W_when receives ONLY STDP; W_what receives ONLY cf-RPE; no shared dynamics

**Reference numbers** (per Fix #28 -- per-arm metrics):
- ARM_BASELINE: 7.3065 (rail)
- v4 ARM_FREQ_DEEPER_TRAIN: 7.159 (single mechanism; chain-grade partial)
- v3 ARM_THETA_PHASE_TWO_W: 7.2349 (single mechanism; already segregated by phase)
- v3 ARM_FREQ_ROUTED_K2: 7.2096 (single mechanism)
- v4 ARM_FREQ_COMBINE_W_THETA: **7.365** (combine on shared W HURT; motivates this drill)

---

## 2. Arms (5)

**ALL arms** use: `N_DIM=8192, V=4000, N_TRAIN=100000, N_HELD=20000, 5 seeds [7, 13, 17, 23, 29],
text8, word2vec sparse-bipolar f=0.05, INGEST_BATCH=64, N_STEPS=2000, STDP_WEIGHT=0.5,
CFRPE_LR=0.5`.

| Arm | Mechanism | Tests |
|---|---|---|
| ARM_BASELINE_SHARED_W | Hebbian baseline | sanity rail vs 7.3065 |
| ARM_FREQ_DEEPER | v4 winner reproduced (rank=100, lr_high=0.5, lr_rare=0.2, n_steps=2000) | rail to v5 cell |
| ARM_THETA_PHASE_TWO_W | v3 THETA two-W phase-alternated (cf-RPE on phase 0, STDP on phase 1, both on different W banks) | tests segregation-by-phase alone |
| ARM_SEGREGATED_DUAL_W | W_when (STDP-only) + W_what (cf-RPE-only); BOTH update every step; static 0.5/0.5 mixer | tests function-domain segregation |
| ARM_SEGREGATED_PLUS_CONTEXT_GATE | above + learned context gate (sigmoid on ctx norm; grid over center+scale) | tests gating adds value over static mix |

**Critical comparison**: v4 COMBINE_W_THETA (7.365 HURT) vs v1 SEGREGATED_DUAL_W. Both combine cf-RPE + STDP, but v4 mixes on shared W (intermod) while v1 separates by function (W_when=STDP-only, W_what=cf-RPE-only). If v1 SEGREGATED is much better than 7.365, segregation principle works.

---

## 3. HARD bands (PRE-REG; PROSPECTIVE)

**Sanity rail (mandatory):**
ARM_BASELINE_SHARED_W BPC within +/-0.05 of fair_harness ref 7.3065.
If drift > 0.05 in `full` mode -> `HARD_FAIL_PROVENANCE`.

**HARD_PASS_CHAIN_GRADE_SEGREGATION_WORKS:**
- ARM_SEGREGATED_PLUS_CONTEXT_GATE BPC <= 6.95
- AND beats FREQ_DEEPER (7.159) by >= 0.02 BPC
- AND beats THETA_PHASE (7.235) by >= 0.02 BPC
- AND CV <= 0.05

**HARD_PASS_SEGREGATION_LIFTS_OVER_BASELINE:**
- ARM_SEGREGATED_PLUS_CONTEXT_GATE BPC <= 7.10
- AND beats ARM_BASELINE_SHARED_W by >= 0.20 BPC
- AND CV <= 0.05
- (segregation avoids intermod; lifted over baseline but didn't reach chain-grade)

**HARD_FAIL_INTERMOD_NOT_AVOIDED (the targeted v1 negative):**
- ARM_SEGREGATED_DUAL_W BPC within +/-0.05 of v4 COMBINE_W_THETA's 7.365
- AND ARM_SEGREGATED_PLUS_CONTEXT_GATE BPC within +/-0.05 of 7.365
- (function-domain segregation didn't avoid the intermod -> mechanism combination genuinely doesn't compose at substrate scale)

**MIDDLE_BAND_HIGH_CV:** SEGREGATED_PLUS_GATE CV > 0.05

**MIDDLE_BAND_PARTIAL_SEGREGATION:** SEGREGATED_PLUS_GATE BPC in [7.10, 7.30] (avoided intermod but didn't surpass individual mechanism wins)

**MIDDLE_BAND_INTER_GAP:** SEGREGATED_PLUS_GATE outside HP+MB+HF bands

---

## 4. Discriminator (load-bearing per Fix #28)

Per-arm BPC in `detail.arm_bpc.<arm>` and `detail.by_arm_agg.<arm>.bpc_best_mean`.

**Intermod check:** `detail.intermod_check`:
- `seg_near_intermod`: SEGREGATED_DUAL_W within 0.05 of 7.365
- `seg_gate_near_intermod`: SEGREGATED_PLUS_GATE within 0.05 of 7.365
- `both_near_intermod`: triggers HARD_FAIL_INTERMOD_NOT_AVOIDED

**Combo-beats-individual:** `detail.combo_beats_individual`:
- `seg_gate_beats_freq`: SEGREGATED_PLUS_GATE beats v4 FREQ_DEEPER (7.159) by >= 0.02
- `seg_gate_beats_theta`: SEGREGATED_PLUS_GATE beats v3 THETA (7.235) by >= 0.02
- `seg_gate_beats_baseline`: SEGREGATED_PLUS_GATE beats BASELINE by >= 0.20

**Segregation diagnostics:** `detail.segregation_diagnostics.when_vs_what_bank_corr_mean` -- mean across seeds of `<W_when, W_what>` cosine correlation. If high (near 1.0), banks are not really segregated (same dynamics); if low (near 0), banks have diverged into distinct function-roles.

**Interpretation guide (Fix #28; read per-arm not verdict_msg):**

If **SEGREGATED_PLUS_GATE beats FREQ_DEEPER AND THETA** (chain-grade): function-domain segregation is a substrate-product architectural principle. Segregation = avoid intermod; gate = correctly route per-query. This generalizes the basis-vs-use-case separation principle from v3 (THETA two-W banks) to the cross-mechanism combination case.

If **SEGREGATED_DUAL_W beats v4 COMBINE** but ties FREQ_DEEPER: segregation avoids intermod (no longer 7.365) but the WHEN+WHAT combination on text8 unigram-conditional eval doesn't add information beyond cf-RPE alone (the cf-RPE branch is bigram-shaped enough that adding STDP-timing doesn't lift unigram-conditional BPC).

If **BOTH SEGREGATED arms near 7.365** (HARD_FAIL_INTERMOD_NOT_AVOIDED): mechanism combination at substrate scale genuinely doesn't compose -- not just an FDM intermod artifact. The cell architecture must choose ONE mechanism.

If **gated arm beats static arm by >= 0.05**: gate adds value (context-magnitude routing meaningful).
If **gated arm <= static arm + 0.02**: gate is no-op; the static 0.5/0.5 mixer is at the same operating point as any sigmoid grid choice.

---

## 5. Per-Q discipline (Fix #28; by-construction-saturation check)

This cell tunes for sub-7.0 BPC; no 1.000 results expected. No by-construction-saturation concern.

LLM-call counter asserted == 0 at metrics-write time.

---

## 6. Operating disciplines (pre-dispatch checklist)

- [x] D1 roofline probe: SEGREGATED kernel at probe N values; extrapolates per-seed wall
- [x] D2 atexit + per-seed checkpoint
- [x] Self-test PASS gate (19 STs; all pass on local CPU)
- [x] Per Fix #24 GPU: `torch.cuda + batched ops` mandatory
- [x] ASCII only
- [x] Pre-reg committed before dispatch
- [x] Path-scoped commits

---

## 7. Self-test discipline

19 self-tests run in `_instrumentation_selftest()`. Key v1 NEW tests:
- ST6 asserts SEGREGATED kernel returns shape-correct logits + finite when_vs_what bank corr + bank corr below 0.95 (segregation produces distinct banks)
- ST7 asserts SEGREGATED_PLUS_CONTEXT_GATE returns gate_stack of correct shape + gate variants produce different logits
- ST8 asserts 5-arm diversity (each arm's logits differ)
- ST17 measures SEGREGATED kernel cost ratio at 50 vs 100 n_steps; asserts in [1.2, 4.0]
- ST18 asserts expected_full_wall / requested_timeout >= 1.2x headroom (1122s/7200s = 6.42x)
- ST19 asserts segregation function-distinct: SEGREGATED with stdp_w=0 (no STDP) produces different logits than stdp_w=1.0 (W_when does contribute non-trivially)

---

## 8. Expected wall-clock budget

Per-seed (cost model at N=8192/n_steps=2000):
- ARM_BASELINE: ~50s (Hebbian)
- ARM_FREQ_DEEPER: ~170s (v4 measured)
- ARM_THETA_PHASE_TWO_W at n_steps=2000: ~312s (v3 measured 156s @ n_steps=1000; 2x)
- ARM_SEGREGATED_DUAL_W: ~280s (both W update every step; ~0.9x THETA at same n_steps because THETA's branches alternate not concurrent)
- ARM_SEGREGATED_PLUS_CONTEXT_GATE: ~285s (above + ~5s gate eval)
- Overhead: ~25s

Per-seed total: ~1122s. 5 seeds: ~5610s.
**Requested timeout: 7200s** (1.28x model; D1 roofline gates <0.8 * 7200 = 5760s).

Note: this is tight relative to v4 (which had 2.78x headroom on 6 arms). The arm mix here is heavier per-arm. If D1 refuses dispatch, the prereg-correct fallback is to reduce SEEDS to 3 (matching v3/v4) and re-dispatch.

---

## 9. Routing (cell-author cannot push)

- Cell: `experiments/exp_substrate_compose_segregated_dual_W_context_gated_v1.py`
- Prereg: this file
- Queue: `overnight_queue` (GPU)
- Timeout: 7200s
- Push lane: HEALTHY
- Push is harness-DENIED to exp_dev; Orchestrator handles dispatch
- Self-test gate is the only validation before dispatch

---

## 10. What this cell DOES NOT show

- Does NOT test alternative gate features (entropy, RPE-magnitude, target-rank); only context norm-magnitude
- Does NOT test 3+ bank segregation (e.g., when/what/where); only 2-bank WHEN/WHAT
- Does NOT test gradient-learned gate (handcrafted sigmoid grid only)
- Does NOT test segregation on FREQ + THETA combo (only on canonical WHEN/WHAT separation)
- Does NOT test cross-N (only N=8192; v5 cell handles cross-N for FREQ_DEEPER)
- Does NOT test other mechanism pairs (cf-RPE + Hopfield, STDP + orthog, etc.)
- The "WHEN" interpretation of STDP-only and "WHAT" interpretation of cf-RPE-only are MOTIVATING analogies; the substrate is the substrate. We don't claim biological realism; we claim function-domain segregation is the architectural distinction being tested.

---

## 11. Cites

- `experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py` (v4 COMBINE_W_THETA=7.365 HURT; motivates this drill)
- `data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json`
- `experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py` (v3 THETA=7.235 + FREQ=7.21)
- `data/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun/metrics.json`
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (sanity rail 7.3065)
- USER coordinated blitz directive 2026-06-25 (Agent 3 of 3; in-conversation)
- USER drill recommendation: combine on shared W = FDM intermod; segregate by FUNCTION not phase (brain canonical theta=WHEN, gamma=WHAT)
- Skunkworks META_RULE_retrospective_band_correction (PROSPECTIVE bands per genuine new cell)
