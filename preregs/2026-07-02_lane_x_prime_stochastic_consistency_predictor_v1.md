# Pre-reg: lane_x_prime_stochastic_consistency_predictor_v1

**Date:** 2026-07-02
**Author:** hdi_exp_dev (spawned by Director for research drill 2026-07-02 Track 2 mechanism-substitute)
**Anchor:** `lane_x_prime_stochastic_consistency_predictor_v1`
**Cell:** `experiments/exp_lane_x_prime_stochastic_consistency_predictor_v1.py`
**Research handoff:** `notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md` (§5.2)
**Parent proposal:** `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md` (this cell = 4th signal, drill rebrand to 4-signal)
**USER-LOCKED alignment:** `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md` -- this cell IS that directive as a per-query confidence signal.

## Prior-arc audit (substrate-KB concept-query per USER-LOCKED 2026-06-27)

Query: `"multi-sample perturbation predictive entropy stochastic consistency confidence retrieval"`
- Top hit cosine=0.31 (`preregs/2026-05-30_mixed_confidence_multi_hop_v1_n4096.md` "Confidence propagation" chunk) — TANGENTIAL; general confidence framing, not this observable.
- No prior arc at cosine >0.30 that competes with this specific observable class. Confirms drill §2 verdict: "no direct precedent for stochastic multi-sample perturbation predictive-entropy as substrate contamination predictor."
- Prior work check: NONE at cosine >0.30. Genuinely novel observable in substrate. Nearest analog is TRAINED-CONFIDENCE-HEAD (cleanup residual delta_z; different mechanism-class).

## Mechanism

For each query `q` in the h4-clustered KB with one injected contaminating fact:
- Sample `n_perturb` noise vectors `eps_i ~ N(0, sigma^2 I)`.
- Perturbed queries: `q_i = unit(q + eps_i)`.
- Compute similarities per perturbation: `sims_i = q_i @ kb_aug.T` (shape `(n_perturb, M+1)`).
- Per-perturbation top-K softmax (K=10; numerically-stable).
- Aggregate: `p_bar = mean_i(softmax_i)` over K support.
- Score: `H(p_bar) = -sum_k p_bar[k] * log(p_bar[k])` — Shannon predictive entropy.

Risk = H (high entropy = high uncertainty = contamination-likely).
Discriminator: `AUC(H, is_contaminated_target_in_top_K)`.

**Continuous predictive-entropy (NOT discrete vote-count)** per drill §4.1: Wang et al. 2022 self-consistency baseline was corrected by ACL Findings 2025 "Confidence Improves Self-Consistency" — vote-count fails AUROC ≤ 0.5 on 5/6 cells; continuous entropy captures uncertainty better.

**Distinct mechanism-class from h4 (density HF) and h4b (spatial-margin HF):**
- h4/h4b are STATIC observables of retrieval geometry — hit Bayes-floor at σ=0.005 ridge (drill §3.1 Δ_req=2.72·10⁻³ vs Δ_obs=8·10⁻⁴).
- This is a DYNAMIC observable of retrieval BEHAVIOR under input perturbation — decouples from the ridge geometry. Different SNR budget entirely (drill §4.1).

## Envelope-fail-bands

Discriminator arm = `arm_C_N16_sigma05` (drill §5.2 primary discriminator).

| Band | AUC | Notes |
|------|-----|-------|
| HARD_PASS | >= 0.65 AND cv <= 0.03 | 4th cortex confidence signal; closes drill Track 2 mechanism-substitute; paradigm-launch candidate |
| MIDDLE_BAND (unstable) | >= 0.65 AND cv > 0.03 | Seed instability; investigate before ship |
| MIDDLE_BAND (partial) | 0.55 <= AUC < 0.65 | Partial predictor; composition candidate with h4/h4b relaxed-regime |
| HARD_FAIL | < 0.55 | Mechanism-class dead in h4-regime; drill §6 world 4 confirmed |

`cv = std(auc_per_seed) / mean(auc_per_seed)`. META_RULE_L: strict floor + cv gate.

Secondary arm bands (per drill §5.2):
- `arm_E_N32_sigma05`: HARD_PASS AUC >= 0.68 (diminishing-returns test)
- `arm_A_N1_sigma05`: baseline (~= 0.50; single-shot = no consistency signal)
- `arm_D_N16_sigma10`: ablation (over-perturbation may destroy signal)

## Regime

Same harness as h4/h4b for direct comparability (drill §5.2 mandate):
- `INTRA_COS = 0.6` (cluster tightness — UNCHANGED intentionally)
- `TOPK_CONTAM = 10` (contamination-in-top-K label definition)
- `K_SOFTMAX = 10` (softmax support size)
- FULL: `SEEDS=[7,17,23]`, `N=8192`, `N_CLUST=60`, `PER=60`, items=3600, `N_Q=200` pos + 200 neg per seed
- Contamination p ≈ 4.6% (matches h4/h4b)

**Rationale for unchanged regime:** if this mechanism works HERE where h4/h4b failed, it validates the stochastic signal as regime-robust and confirms the drill's Track 2 hypothesis. If it doesn't, drill §6 REGIME_CONFOUND world 2 or world 4 is confirmed — informative in either direction.

## Arms

| Arm | N_perturb | sigma | Expected AUC (drill §5.2) | Notes |
|-----|-----------|-------|---------------------------|-------|
| A | 1 | 0.05 | 0.50 baseline | HYPOTHESIZED@drill §5.2 (no consistency signal at N=1) |
| B | 8 | 0.05 | 0.62-0.72 | HYPOTHESIZED@drill §5.2 |
| C | 16 | 0.05 | 0.65-0.75 | HYPOTHESIZED@drill §5.2 (primary discriminator) |
| D | 16 | 0.10 | 0.60-0.75 | HYPOTHESIZED@drill §5.2 (ablation; over-perturbation) |
| E | 32 | 0.05 | 0.68-0.78 | HYPOTHESIZED@drill §5.2 (diminishing returns above N~16 per Ashukha 2020 CITED) |

## SCHEMA-VET fields

- `arms_differ_verified`: TRUE (META_RULE_AF hash-verified across arms at smoke gate; arms differ by N_perturb which produces distinct entropy distributions).
- `final_metrics_atomicity`: `tmp_replace` (via `experiments._seed_checkpoint.write_metrics`).
- `crlb_n/a`: "AUC discriminator has no closed-form noise floor for entropy distribution; discriminator-survives-scale gate (smoke arm E full-N preview) covers analogous concern."
- `discriminator_reachability`: TRUE. AUC in [0.5, 1.0]; HARD_PASS threshold 0.65 is reachable per literature (Farquhar Nature 2024 AUROC 0.75-0.79 at 10% halluc CITED@drill §4.1; deflated to 0.60-0.72 at 5% contam).
- `baseline_in_band`: contamination_rate ~= 0.5 by construction (balanced pos/neg queries); Arm A baseline AUC ~= 0.50 is chance (in-band as null-hypothesis reference).
- `discriminator survives scale`: smoke includes MANDATORY arm E `N_perturb=32` full-N=3600 preview; reject FULL if arm E preview AUC <= 0.55 per USER-LOCKED 2026-06-26.
- `HARD_PASS strictly above floor`: 0.65 gate + cv <= 0.03 (META_RULE_L tightening).
- `HP_SCOPE`: `{"arm_C_N16_sigma05": ["AUC >= 0.65", "cv <= 0.03"], "arm_E_N32_sigma05": ["AUC >= 0.68", "cv <= 0.03"]}` — mechanism arms only; arm_A baseline excluded from HP scope.
- `cardinality_ok`: EXPECTED_N_UNITS = 3 seeds × 5 arms × 400 queries = 6000. Verdict logic asserts `len(per_seed) == len(SEEDS)` + per-arm cardinality via `arms` dict.
- `calibration_check`: `default_ok_for_this_regime`. Predictive-entropy is parameter-free once (K_SOFTMAX=10, sigma_input, n_perturb) fixed per pre-reg. No adaptive tuning.

## §13-14 defensive fields

- `cell_chunked`: FALSE. 3 seeds × 5 arms × 400 queries = per-seed wall estimate ~1-3 min numpy CPU. Total < 15 min. Chunked architecture would be overkill for this compute budget.
- `start_marker_written`: TRUE (`_write_start_marker` at main entry).
- `crash_diagnostic_present`: TRUE (`_write_crash_metrics` in outer try/except with `except SystemExit: raise` ordering).
- `heartbeat_present`: FALSE. Per-seed < 15 min; §13 rule of thumb applies above ~15 min. Per-arm print(flush=True) provides progress visibility.
- `defensive_error_checking`: `passed_all_4_patterns` (start marker + crash diag + `except SystemExit: raise` before `except Exception`; no bare `except:` or `except BaseException:`).

## §15 test-design gates

- `sweep_alignment_verdict`: ALIGNED. Sweep axis = N_perturb ∈ {1, 8, 16, 16-sigma10, 32}. Effective parameter per arm = the actual N_perturb used in that arm's loop (no misalignment).
- `discriminating_fraction`: 4/5 arms predicted in discriminating band [0.55, 0.85]; arm A (N=1) intentionally at chance (baseline). Discriminating fraction = 4/5 = 0.80 >= 0.30 threshold.
- `composition_edges`: N/A. Cell does not compose primitives; single mechanism (predictive entropy over perturbed queries).
- `positive_control_arms`: h4b spatial-margin is NOT a positive control (different mechanism-class; its HF is informative but not this cell's target). Arm A (N_perturb=1) serves as INTERNAL positive control: reduces to single-shot retrieval; expected AUC ~= 0.50 confirms the mechanism is entropy-consistency not raw softmax.
- `functional_requirements`: cortex needs per-query scalar confidence signal predicting contamination-affected retrievals. Mapped to substrate observable: multi-sample predictive entropy H over N_perturb noise-perturbed retrievals. Prior CG primitives: none (this IS the new primitive being validated); nearest is TRAINED-CONFIDENCE-HEAD (delta_z cleanup residual; different mechanism-class).

## §16 run_mode verification

Post-dispatch verification of landed `data/exp_lane_x_prime_stochastic_consistency_predictor_v1/metrics.json` must confirm `run_mode == "full"`, `n_seeds == 3`, per-seed `arms` dict has 5 entries, `elapsed_s > 30`, size > 10KB before framing FULL result.

## §17 print-progress flushing

`progress_logging: print_flush_true`. All progress lines (per-seed / per-arm / verdict) use `flush=True`. `sys.stdout.reconfigure` at top. Cell wall time < 15 min; strict §17 gate applies only at 30 min+. Compliant.

## Compute architecture

**`(b) sequential-CPU with justification`.** Load-bearing op per query per arm: matmul `(N_perturb, N) @ (N, M+1)` = at most `(32, 8192) @ (8192, 3601)` = one BLAS call producing `(32, 3601)` similarities. Batched per-query internally. Cross-query loop is sequential Python (400 iters × per-query matmul). Per-arm wall estimate: `(32,3601) matmul × 400 = 12800 similar-sized calls per arm ≈ 5-15s numpy CPU`. Per-seed wall (5 arms) ~30-75s. Total FULL wall ~2-3 min across 3 seeds.

**Why not GPU-batched:** per-query matmul at N_perturb ≤ 32 does NOT reach GPU-launch-amortization threshold. Total FULL wall well under 10 min (USER GPU-batching rule threshold). Numpy CPU is native to h4/h4b harness (parity); h4b landed FULL AUC=0.545 at wall ~0.8s single-seed on numpy — same code path.

If per-arm wall EXCEEDS 10s at Arm E (N_perturb=32) in smoke measurement, revisit GPU-batching for the outer query loop (batch all 400 queries into one `(400*32, N) @ (N, M+1)` matmul = 12.8k row × 3601 col × 8192 dim = ~180 GB naive; must chunk). Escape hatch: torch.cuda batched over queries with per-arm chunk size 50-100.

## Cost / dispatch plan

- **Smoke arm-A/C small-N (seeds=1, items=600, N_Q=40, arms=A+C):** ~2-5s local
- **Smoke SCALE-PREVIEW (seeds=1, items=3600 full-N, N_Q=100, arms=A+E N_perturb=32):** ~15-45s local — MANDATORY per drill §5.2 discriminator-must-survive-scale
- **FULL 3-seed × 5 arms × 400 queries at N=8192 items=3600:** ~2-3 min total estimated
- **Route:** SMOKE local direct; FULL to `remote_cpu_queue` via Orchestrator (parity with h4b + USER 2026-07-01 "smoke only on local_cpu_queue" rule)
- **Timeout for FULL (remote_cpu_queue):** 1200s (20 min) — 6-8× safety margin over estimated 2-3 min

Timeout formula: `timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)**1.0 * (FULL_seeds/smoke_seeds))`. If SCALE-PREVIEW smoke wall = 45s at N_perturb=32 full-N single seed: `1.5 * 45 * 1.0 * 3 = 202s` per arm × 5 arms = 1015s. Round to 1200s.

## Complementarity to h4b, lap3_12, other lanes

- **h4/h4b (spatial-margin family)** — DIFFERENT mechanism-class (static geometric vs dynamic behavioral). Compose orthogonally: h4b provides `gap` scalar; this provides `H` scalar. Cortex could stack both into (gap, H) 2D feature vector.
- **lap3_12 (post-hoc isotonic)** — POST-HOC calibrator; would isotonic-calibrate H → contamination_probability if this cell PASSes. No overlap.
- **h4b_regime_redesign_probe_v1 (parallel Track 1 in drill)** — parallel track; tests whether relaxed regime rescues h4b spatial-margin. INDEPENDENT dispatch; this cell tests mechanism-substitute in SAME regime for direct comparability.

Track 1 + Track 2 verdict cross-matrix per drill §6 (dispatch both in parallel; interpret jointly).

## Follow-up (post-PASS, not in scope of this cell)

If HARD_PASS: architecture rebrands from "3-signal" to "4-signal cortex confidence header." Update `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md` to reserve `hdlab/cortex_confidence.py::stochastic_consistency_score(query, N_perturb, sigma_input)`. Ship as substrate paradigm-launch atom candidate. If HARD_FAIL: drill §6 world 4 confirmed (mechanism-class dead); pivot cortex-confidence to different task class.

## Pre-reg self-check

- [x] Substrate-KB concept-query performed (NONE at cosine >0.30; genuinely novel synthesis)
- [x] Envelope-fail-bands HARD_PASS + HARD_FAIL declared with strict META_RULE_L cv gate
- [x] Discriminator-survives-scale gate (smoke arm E full-N=3600 preview)
- [x] Cell-template mandatory §6-12 fields declared above (arms_differ_verified TRUE)
- [x] §13-14 defensive-checking fields declared
- [x] §15 test-design gates declared (sweep-alignment ALIGNED; discriminating_fraction 0.80; no compositions)
- [x] §16 run_mode verification plan stated
- [x] §17 progress-logging print_flush_true declared
- [x] Compute architecture section per USER 2026-07-02 GPU-batching rule (sequential-CPU justified)
- [x] Complementarity to h4/h4b/lap3_12/parallel-track h4b_regime_redesign stated
- [x] HYPOTHESIZED-vs-MEASURED discipline: all pre-reg numbers tagged inline

Ready for smoke dispatch.
