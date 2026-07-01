# Pre-reg: cortex_hippo_dense_layer_N_sweep_v1

## Anchor
`cortex_hippo_dense_layer_N_sweep_v1_seed_{7,13,19}`

## Parent
v2 REPLACE-mode chain-grade rescue (M=8192 @ N_h=N_c=4096, HP@fc47b1bb 3-seed).
v2 preview arm at N_h=N_c=4096 recall=1.000 MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json.

## Substrate-KB prior-work check
`bash tools/substrate_query.sh "cortex_hippo dense-Hopfield N scaling replacement mode M=8192"` returned only 2026-05-30-era modern_hopfield_replication preregs at cosine=0.30 (superseded arc). No prior N-sweep on the v2 REPLACE-mode Ha+attention architecture. **Cell is genuinely novel** (not a rediscovery).

## Question
Does REPLACE-mode dense-Hopfield readout hold at N_h=N_c scaling beyond the v2 4096 baseline? Specifically at N ∈ {4096, 8192, 16384, 32768} with M=8192 fixed.

## Falsifiable predictions
- **HP (chain-grade N-scaling win):**
  - recall(REPLACE) / recall(STANDARD) >= 0.80 for ALL N in sweep
  - recall(REPLACE) - recall(HA_ONLY) >= 0.60 for ALL N in sweep
  - cross-seed CV(REPLACE recall) < 0.15 at every N
  - arms_differ_verified: True (META_RULE_AF)

- **MB (partial N-scaling):** REPLACE holds at N<=8192, degrades to 0.60-0.80 ratio at N>=16384 (works small-N degrades large).

- **HF (replacement wall found):** REPLACE < 0.60 at any N in the sweep; regime-scale collapse.

## Design
- **Sweep axis:** N_h = N_c ∈ {4096, 8192, 16384, 32768} (log-2 spaced).
- **Fixed:** M=8192, hippo_sparsity=0.10, eta_h=1.0, adaptive beta = log2(M)/margin clamped [8, 128].
- **Arms per N:** ARM_STANDARD (cortex-Hebbian only), ARM_HA_ONLY (fairness floor), ARM_HA_DENSE_REPLACE (mechanism).
- **Seeds:** {7, 13, 19} — chunked-single-seed-per-cell.
- **Cardinality:** EXPECTED_N_UNITS = 4 N × 3 arms = 12 arm outcomes per seed (META_RULE_H).

## HP_SCOPE (per-arm)
```yaml
ARM_HA_DENSE_REPLACE: [ratio_vs_standard, gap_vs_ha_only, cv_cross_seed]
ARM_STANDARD: [sanity_ceiling_at_N4096, degrades_at_higher_alpha]
ARM_HA_ONLY: [fairness_floor <=0.20]
```

## Schema-vet gates
- **sweep_alignment_verdict:** ALIGNED. Swept axis N drives BOTH cortex-Hebbian W_c dimensionality (N×N) AND dense-Hopfield tape width. Every primitive experiences the swept parameter.
- **discriminating_fraction:** predicted 0.75-1.00 in-band per N. Baseline STANDARD alpha_effective = M/N: at N=4096 alpha=2.0 (over-subscribed, STANDARD saturates below ceiling); at N=32768 alpha=0.25 (comfortable). REPLACE independent of alpha (attention capacity ~ exp(N)). 3/4 points HYPOTHESIZED@ in discriminating band via v2 preview MEASURED@1.000 at N=4096.
- **cardinality_ok:** True; verdict counts len(per_arm) >=12 or emits HARD_FAIL_CARDINALITY_BREACH.
- **calibration_check:** adaptive_with_discriminator_gate (beta = log2(8192)/margin ~ 13.6/margin, clamped).
- **crlb_floor_computed:** 0.00552 THEORETICAL@binomial-CLT sigma_min=sqrt(0.25/M=8192). HP gap 0.60 = 109 sigma; well-reachable.
- **discriminator_reachability:** True.
- **baseline_in_band:** HYPOTHESIZED — STANDARD at N=4096 with alpha_simple=2.0 will drop below 0.95 (over-subscribed Hebbian); at N=32768 alpha=0.25 STANDARD returns near ceiling. Smoke gates ARM_STANDARD not saturated at 1.000 across all N in preview.
- **positive_control_arms:** ARM_HA_DENSE_REPLACE at (N=4096, M=8192) must reproduce v2 preview recall=1.000 ± 0.10; tolerance 0.10; if outside HARD_FAIL_REGIME_MISMATCH.
- **arms_differ_verified:** True via META_RULE_AF hash-test at smoke gate.
- **final_metrics_atomicity:** tmp_replace (META_RULE_AH).
- **DISCRIMINATOR-MUST-SURVIVE-SCALE:** smoke runs 2 N-points (N=1024 main + N=32768 FULL_N_PREVIEW single arm on ARM_HA_DENSE_REPLACE) so scaling discriminator proven pre-dispatch.

## Cell-chunked architecture
- Three separate cell files: `exp_cortex_hippo_dense_layer_N_sweep_v1_seed_{7,13,19}.py`
- Each cell runs its own seed × full N-sweep internally.
- Runner death loses ONE seed; other 2 land independently.
- start_marker + crash_diagnostic + heartbeat all present per META_RULE §13.

## Cost model
- Per-arm cost dominated by (M × N_c) attention matmul at largest N. At N=32768, M=8192: keys_c @ K_c^T = 8192×8192 × 32768 float32 ~ 8.6 TFLOPs per arm.
- 3 arms × 4 N × 1 seed per cell.
- Torch.cuda on GPU: ~2-5 min per seed cell.
- Torch.cpu fallback: ~30-60 min per seed.
- **Timeout:** 3600s per cell (headroom for CPU fallback).

## Dispatch
- Smoke: SMOKE ONLY on `local_cpu_queue` (USER-locked 2026-07-01).
- Full: `overnight_queue` (GPU-preferred) via Orchestrator push (harness-DENIED to me directly).

## Verdict logic
```
HP: all N pass (ratio>=0.80 AND gap>=0.60) AND cv_cross_seed<0.15
HF: any N has REPLACE<0.60 OR HA_ONLY>0.20 OR cardinality breach
MB: partial (some N pass, some fall in-band)
```

## Provenance tags
- v2 preview recall=1.000 at N=4096 MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json:per_seed[0].arms[3].recall_cortex
- Adaptive beta formula CITED@Ramsauer2021_eq14 + drill Q4 softmax-saturation guard
- CRLB sigma_min=0.00552 THEORETICAL@binomial-CLT sqrt(0.25/8192)
- Amit-Gutfreund 0.138N wall HYPOTHESIZED@STANDARD-fails-at-alpha>=2 (N=4096 STANDARD may saturate below 1.0)

## Author
hdi_exp_dev sub-agent, 2026-07-01.
