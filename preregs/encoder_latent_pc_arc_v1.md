# Pre-registration: encoder-level latent predictive coding (JEPA) on ARC -- rep-quality lever #1

- Anchor: `encoder_latent_pc_arc_v1`
- Cell: `experiments/exp_encoder_latent_pc_arc_v1.py`
- Metrics: `data/exp_encoder_latent_pc_arc_v1/metrics.json`
- Spec source: `notes/encoder_representation_lever_ranking_2026-07-29.md` (lever #1 + section-3 measurement plan);
  founding diagnosis `notes/brain_foundational_component_analysis.md` components 1+2.
- Author: hdi_exp_dev, 2026-07-29. Status: LOCAL build + self-test PASS; FULL held for GPU (queued behind Track-A WM verdict).
- Prior-work check (USER-locked): `substrate_query.sh` top hits cosine 0.37-0.39 are research-DRILL notes
  describing JEPA/predictive-coding conceptually (research_drill_embodied_revival C8, realtime_multimodal_biology,
  fact_representation_rethink). NO prior experiment CELL implements an encoder-level latent-PC objective.
  This is the first BUILD of the concept; NOT a rediscovery.

## Question
Does an encoder-level latent-predictive-coding (JEPA) objective produce a RICHER representation than the
current MLM objective, at MATCHED training budget, judged purely on representation geometry (no WM module)?
This repairs the founding-diagnosis objective gap (static target -> stream/latent prediction) as a standalone
encoder lever, testable independently of and in parallel with the stateful-core WM gate.

## Mechanism (brain-faithful; invariant-respecting)
- JEPA latent prediction (I-JEPA/V-JEPA; Rao&Ballard 1999 / Friston 2005 predictive coding): mask contiguous
  target SPANS; predict the TARGET-span LATENT from the CONTEXT latent via a small predictor MLP. Everything
  stays in d-dim latent space -> OOM-free (NO [B,L,vocab] tensor anywhere; avoids the v5 causal-LM OOM class).
- Collapse guard (REQUIRED per lit): EMA/stop-grad target encoder (SimSiam-style, m=0.996) + VICReg variance
  floor (hinge on per-dim std >= gamma=1.0) + covariance/decorrelation term (off-diag cov -> 0, coef 0.04).
- Base encoder = the v2 TinyTransformer (imported from `exp_scale_meaning_learn_arc_heldout_v2.py`),
  learned from scratch under the latent-PC objective. NO borrowed vectors / LLM / GloVe / BGE anywhere.
- Temporal-contiguity ABLATION arm: wires the ALREADY-BANKED `hdlab/temporal_trace.py` (Foldiak slow-feature
  exponential trace) as a one-variable aux loss -- contiguous window runs form pseudo-documents; the current
  window's pooled latent is pulled toward the running trace of prior windows (slowness). LPC alone vs LPC+TC.

## Arms (matched budget: same tokens/steps/architecture; base-encoder params matched)
- ARM_LPC     : latent-PC alone. PRIMARY.
- ARM_LPC_TC  : latent-PC + temporal-contiguity. ABLATION (reported, not HP-gated).
- ARM_MLM     : current MLM baseline (v2 mlm_train), same steps/tokens/architecture. Known-good reference (29591 baseline 0.56-0.63 band).
- ARM_RANDOM  : random-init encoder (untrained). Floor.

## Independent rep-quality battery (frozen encoder; KB read-only, NEVER a training target)
1. graded_geometry_spearman : Spearman(encoder cosine, KB graded proximity {1-hop=3, 2-hop=2, far=1}) over
   held-out-NEW concepts. THE HEADLINE. Leak-proof (held-out has zero relational input; KB is diagnostic read).
2. heldout_probe_acc : frozen closed-form ridge linear probe (lexname supersense) trained on TRAIN concepts,
   tested on held-out-NEW. Linear + frozen head -> gains attributable to representation, not probe capacity.
3. relational_auc : per-query neighborhood AUC (reuses v2.relational_eval; text-alone arm = this encoder).
4. rep_std + mean_pairwise_cos (frozen-rep collapse witness) + training-time min target-embedding std (VICReg telemetry).

## Pre-registered bands (deflated per lit-scan calibration; section 3 of the ranking note)
- HARD_PASS = ARM_LPC graded_geometry beats ARM_MLM by >= +0.10 AND beats ARM_RANDOM by >= +0.15,
  in >= 1 of 2 seeds with the OTHER seed non-negative, AND held-out probe does NOT regress (>= MLM - 0.01),
  AND NO collapse (rep_std >= 0.02 AND training min_target_std >= 0.05).
- HARD_FAIL_NO_EFFECT = ARM_LPC ties BOTH MLM and RANDOM within +/-0.03 on graded_geometry.
- FAIL_BY_COLLAPSE = rep_std < 0.02 OR training min_target_std < 0.05 (variance collapsed) ->
  distinct diagnosis; mechanism class NOT refuted (retune VICReg/EMA or use --co-scaled).
- HARD_FAIL_UNDERPOWERED = graded-geometry min query count < 40.
- MIDDLE_BAND = real-but-below-band gain.
- ARM_LPC_TC reported as ablation delta (does temporal-contiguity add over LPC alone?).

## Compute architecture
- Class: (a) batched-GPU. Transformer training + batched encode are matmul-heavy; FULL runs CUDA+AMP.
  Local self-test = CPU (tiny). No sequential-CPU dependency.
- Storage strategy: no_storage / no_composition (this is encoder pretraining + frozen-rep geometry; no
  sharded/bundled atom table, no chained retrieval).
- OOM-free by construction: loss lives entirely in d-dim latent space; no vocab-sized logits tensor.

## SCHEMA-VET / cell-template compliance
- arms_differ_verified: True (self-test asserts all 4 held-out rep matrices bit-distinct via SHA-256).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace + per-seed write_partial).
- except-ordering: except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep gate PASS).
- crlb_n/a: this is a representation-geometry comparison (Spearman / probe-acc), not a noise-floor estimator;
  the empirical floor is witnessed by ARM_RANDOM (near-chance geometry) + the no-effect band.
- baseline_in_band: ARM_MLM graded_geometry expected in (0.05, 0.95) (cited 29591 band 0.56-0.63); ARM_RANDOM near floor.
- discriminator_survives_scale: (B) analytical -- the objective gap is architectural (stream vs static target),
  and the battery is NOT saturated: MLM ~0.56-0.63 leaves >0.10 headroom to HP-over-MLM; RANDOM near 0 gives
  >0.15 headroom to HP-over-RANDOM. Self-test at 40 steps is near-chance across arms (expected: proves machinery,
  not discrimination). NO smoke-saturation risk (no arm at ceiling).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 at FULL); verdict counts len(per_seed).
- calibration_check: default_ok_for_this_regime -- VICReg gamma=1.0 std-floor + off-diag cov + EMA m=0.996
  are literature-standard defaults; collapse telemetry (target_std per step) is logged so the guard is OBSERVED, not assumed.
- real_code_path: --self-test runs the REAL pipeline (v2 prepare_data + BPE + TinyTransformer + lpc_train +
  mlm_train + full battery) at N~16 tiny scale (SELFTEST_CFG). MEASURED@ self-test 2026-07-29:
  loss descends (pred 0.4419 -> 0.4007 LPC; 0.4402 -> 0.3990 LPC+TC), no collapse (min_target_std 1.0004),
  TC aux fired (tc 0.006-0.008), all 4 arms produced battery numbers, arms bit-distinct, cuda-safety audit params_on_device=True.
- defensive_error_checking: start-marker + crash-diagnostic + heartbeat + no silent except -> passed_all_4_patterns.
- progress_logging: print flush=True per train step + _heartbeat.jsonl (timeout_s >> 1800). REQUIRED (long GPU run).
- cell_chunked: False (per-arm x per-seed loop with per-seed write_partial; single cell handles both seeds).

## CUDA-device-safety (recurring bug class: WM.to(device) then cpu-Generator-used-with-cuda)
- Every module (online / target / predictor) .to(device); EMA target on device.
- EVERY torch.rand/randint/randperm/arange created with device= from ids.device. NO torch.Generator in the hot path
  (numpy default_rng only selects host-side window indices into a numpy array, then .to(device)).
- The ONLY host<->device crossing is the temporal_trace numpy primitive: explicit .detach().cpu().numpy() out,
  torch.from_numpy(...).to(device) back.
- `_cuda_safety_audit()` runs 2 end-to-end LPC+TC steps on the run device (cuda when present) and asserts finite
  loss + all params on-device BEFORE data prep, so the eventual GPU launch fails fast in seconds if a device bug exists
  rather than after the (expensive) data prep. On this CPU box cuda_tested=False; the identical device-routed step ran
  on CPU (params_on_device=True) and the static routing is documented above.

## Capacity-ratio watch
512d over ~130M tokens; SimSiam small-scale sensitivity finding (SCAN 1) says collapse risk is
capacity/data-ratio dependent. `--co-scaled` (d=256, L=4) is a pre-registered follow-up if FULL shows collapse
or over-capacity; the training-time min_target_std telemetry is the early-warning signal.

## Ready-to-launch (HELD for GPU; queued behind Track-A WM verdict)
FULL, GPU (overnight_queue), 2 seeds [7,13], 4 arms:
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_latent_pc_arc_v1 experiments/exp_encoder_latent_pc_arc_v1.py preregs/encoder_latent_pc_arc_v1.md <timeout_s>`
