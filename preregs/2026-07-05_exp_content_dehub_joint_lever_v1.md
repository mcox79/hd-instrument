# Pre-reg: exp_content_dehub_joint_lever_v1

**Filed:** 2026-07-05 by exp_dev. **Design source:** `notes/research_content_dehub_joint_lever_gen_encoder_2026-07-05.md`.
**Cell:** `experiments/exp_content_dehub_joint_lever_v1.py` + shared module `experiments/dehub_transforms.py`.
**Status after this filing:** SMOKE LANDED (local, 3-seed) -> HARD_FAIL at smoke scale (see Results). FULL staged, NOT dispatched.

## Question
Does ONE training-free content-embedding de-hub transform (Local Scaling, Zelnik-Manor & Perona 2004),
applied at each content space's INPUT + retrain-from-scratch (the untested application point; NOT the
post-hoc score rescore already shown partially phantom on the FROZEN locus), lift BOTH stuck capabilities:
(A) generalization rank-1 (filtered Hits@1 REAL-minus-SHUFFLED, schema-relation reframe harness) AND
(B) encoder retrieval-agreement (ret_agree10 vs the RAW BGE-large teacher, in-batch-RKD student)?
Shared-mechanism prior: cross-model hub rho=0.545, 49.4% vocab overlap (CITED@design note Section 1b).

## Design (reuse, don't rebuild)
- Shared transform module `dehub_transforms.py`: `local_scaling_embedding` (PRIMARY; exact eigen-embedding
  of the symmetric-normalized self-tuning affinity -> unit-normed feature matrix, cosine geometry = de-hubbed
  geometry; usable as bilinear-scorer feature input AND as an RKD Gram target Phi@Phi.T in [-1,1], same range
  as raw teacher Gram), `zca_whiten` (secondary), `abtt` (reference/weakest), `nk_gini` (hubness scalar).
  k=10 (CITED@note measured value + Nielsen/Macocco/Baroni 2024 SBERT analog; NOT tuned-for-pass).
- GEN side: reuse `exp_schema_relation_hitsatk_mrr_reframe_v1` functions verbatim (`build_split_scaled`,
  `encode_feature_matrix`, `fit_scorer_paired`, `score_scorer`, `filtered_ranks`, `rank_metrics`,
  `_filter_mask`). De-hub the OBJECT codebook Fo (where the FROZEN-slot content-baked hubness lives);
  subjects stay RAW (inductive novel-subject validity preserved; asymmetric projection maps 384-d subjects
  and r-d objects to the same df). Slot = FROZEN (primary; JOINT FULL-optional). Metric = filtered Hits@1
  REAL-minus-SHUFFLED; lift = LOCAL_SCALING rms minus CONTENT_RAW rms.
- ENC side: student INPUT stays RAW BGE (deployable); only the in-batch RKD TARGET geometry is de-hubbed
  (per-batch local scaling; tractable at FULL scale where a global 178k eigendecomposition is not). Compact
  in-batch-RKD loop reuses `v3._make_student`/`v3._block_ste`/`v3._encode_hard_block` + the EXACT in_batch
  RKD loss `((code_Gram - teacher_Gram)[off]^2)`; drops v3c semi-hard mining + best-ckpt selection (NOT the
  de-hub variable; identical across all arms). ret_agree10 measured by `v3._semantic_unit` VERBATIM (identical
  ship-metric definition). Lift = LOCAL_SCALING ret_agree10 minus CE_BASELINE ret_agree10, both REAL.
- SHUFFLED anti-phantom: gen = permuted labels (harness paired REAL/SHUFFLED); enc = permuted teacher-target
  control (within-batch identity permutation decorrelates student input from target).
- `synth_cross_domain_shared_hub` (joint-lever-specific POSITIVE control): two synthetic spaces (different
  dim, different generator seed) sharing a designed hub subset; the SAME transform, applied INDEPENDENTLY to
  each, must reduce Nk-Gini in BOTH.

## Bands (LOCKED; task contract)
- HARD-PASS = REAL-abs lift >= +0.05 on BOTH gen Hits@1 AND enc ret_agree10, SHUFFLED lift <= +0.03 both
  sides (anti-phantom), Nk-Gini reduced on both spaces + synth control fires.  HYPOTHESIZED@this prereg.
- HARD-FAIL = either side <= +0.02.
- MIDDLE = exactly one side clears +0.05 (report which) OR both in (+0.02, +0.05).
- MECHANISM GATE (SMOKE_GATE_FAIL if unmet): nk_gini(dehub) < nk_gini(raw) on BOTH content spaces AND
  synth_cross_domain both-reduced. Discriminator-fires proof.

## META-RULE compliance
arms_differ_verified (RAW vs LOCAL_SCALING object matrices + raw vs dehub Gram); final_metrics_atomicity=
tmp_replace; `except SystemExit: raise` before `except Exception` (no BaseException/bare); crlb n/a
(retrieval-agreement/rank transfer; bands are absolute-lift deltas); baseline_in_band gated (gen SHUFFLED
Hits@1 not saturated <0.95; enc CE_BASELINE REAL ret_agree10 in (0.05,0.95)); MULTI-SEED smoke (3 seeds; the
discriminator is a continuous per-query lift -> META_RULE_smoke_single_seed_inflates_AUC applies);
cardinality_ok (EXPECTED_N_UNITS gen+enc, counted, gated); progress_logging=print_flush_true;
calibration_check=adaptive_with_discriminator_gate. HP_SCOPE: {LOCAL_SCALING: [gen FROZEN Hits@1 rms lift,
enc ret_agree10 lift]}; ZCA/ABTT reference (reported, not HP); SHUFFLED anti-phantom; CONTENT_RAW/CE_BASELINE
paired baseline.

## Compute architecture
Mixed. GEN = batched (reframe FROZEN torch-bmm B=2 paired). ENC = torch MLP in-batch RKD; per-batch de-hub
eigh is O(B^3), B<=128 (trivial). SMOKE local CPU; FULL device=auto (cuda). No generative-LLM calls.

## Cardinality
EXPECTED_N_UNITS = gen(seeds x V-configs x rels x methods) + enc(seeds x methods x arms).
Smoke = 3x2x2x4 + 3x2x2 = 48 + 12 = 60. FULL = 3x2x2x4 + 3x2x2 = 60.

## FULL config (staged; NOT dispatched)
SEEDS=[7,13,19]; GEN_CONFIGS=[V300(M800), V1000(M800)]; GEN_DF=384, GEN_STEPS=2000; ENC teacher cache=
`bge_large_v2_name_177899_54f7cf6a.npz`, ENC_STEPS=1800, ENC_BATCH=128, held=10% (cap 20000),
ENC_FINAL_PAIRS=400000. Encoder FULL is the heavy leg (1.35 GB cache, 1800 steps x 4 arms x 3 seeds) ->
route via Orchestrator (GPU/remote_cpu; needs origin/main push, harness-denied to exp_dev).

## Results (SMOKE, local, 3-seed, 2026-07-05) -- MEASURED@data/exp_content_dehub_joint_lever_v1_smoke/metrics.json
- VERDICT = HARD_FAIL (joint lever falsified at smoke scale). 60/60 units, arms_differ=True, anti-phantom clean.
- MECHANISM FIRES: gen Nk-Gini(obj) 0.789->0.442 (44% de-hub); enc Nk-Gini 0.455->0.229 (50% de-hub);
  synth cross-domain both-reduced (A 0.322->0.184, B 0.319->0.193).
- NO CONVERSION: gen Hits@1 lift = +0.019 (std 0.004; AtLocation +0.017, CausesDesire +0.022; seed-noise
  dominated -- per-seed LS-minus-RAW {+0.05, 0.00, 0.00}/{+0.033, 0.00, +0.034}); enc ret_agree10 lift =
  +0.002 (per-seed {-0.0003, -0.008, +0.014}, net ~0). Dim-preserving references also null: ZCA -0.006,
  ABTT -0.003. Anti-phantom clean: gen shuf lift -0.003, enc shuf lift -0.003. enc baseline in-band (0.327).
- Note: the stratified AtLocation>CausesDesire prediction (design note 1e) did NOT hold (both ~0.02, within
  seed noise) -- consistent with the null.
- FULL-readiness: HOLD the heavy dual-harness FULL. Substantial geometric de-hub (Nk-Gini halved) converts
  to ~0 downstream lift on BOTH capabilities at smoke scale. Scale caveat (hubness worsens at larger V per
  note): the ONLY cheap scale-test worth running before the heavy encoder FULL is the GEN-side FULL alone
  (V-scan to 1000, ~7-10 min, reframe family) to see if the lift GROWS with V; escalate the encoder FULL
  only if it does. Director's routing call.
