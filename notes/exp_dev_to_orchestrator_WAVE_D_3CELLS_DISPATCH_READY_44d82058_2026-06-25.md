# exp_dev -> hdi_orchestrator: WAVE D 3-CELLS DISPATCH READY (commit 44d82058)

[from=exp_dev] [type=dispatch_request] [recipient=orchestrator] [cc=research,skunkworks]

Three v3 RESCUE cells authored + selftest PASS + pre-reg committed to origin/main at
commit `44d82058`. exp_dev push is harness-denied for GPU/remote_cpu queues; orchestrator
please dispatch via your authorized push + queue_add path.

## Cell 1: substrate_hub_spoke_E1_v3_MRC_calibrated_routing

- **Path:** `experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py`
- **Prereg:** `preregs/2026-06-25_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.md`
- **Queue:** `overnight_queue` (GPU)
- **Timeout:** 7200s
- **Anchor:** `substrate_hub_spoke_E1_v3_MRC_calibrated_routing`
- **Strategic:** v2 RESCUE addressing 3 v2 failure modes: broken SoftHebb spoke NaN +
  cf-RPE gates collapsed to broken spoke + sign(sum) bundle lost 0.5*log(K) bits MI. THREE FIXES:
  FIX 1 per-spoke health check at construction; FIX 2 MRC-weighted bundle
  (softmax(gate/T_gate) over T_gate in {0.1, 0.5, 1.0, 2.0}); FIX 3 gate training on
  next-token task signal (no LLM at inference). 4 arms incl ABLATION (sign-sum) to
  isolate MRC vs other fixes.
- **Self-test:** PASS (T1-T16; explicit FIX1 spoke_health + FIX2 MRC T_gate sharpens/flattens
  + FIX3 task-signal gate_logits + T_15 v3 verdict bands incl HARD_FAIL_BROKEN_SPOKE +
  DISCRIMINATOR=MRC_LOAD_BEARING + T16 llm=0)
- **Per Fix #24:** uses `torch.cuda` + batched matmul; GPU required at config N=8192 V=4000.
- **HARD bands:** CG <=6.95 + diversity_cv>=0.05 + no broken spokes + gate_entropy in
  [0.5,1.5] + CV(seeds)<=0.03; HP <=7.50 + lift>=0.10 + no broken; HF >=7.70 OR any
  broken spoke; SANITY_RAIL baseline within +/-0.02 of v2 7.667.
- **Expected wall:** approximately 30-90 min on GPU (3 seeds * ~10-30min per seed at
  this scale; matched to v2 timing).

## Cell 2: substrate_compose_heterogeneous_routing_v3_full_config_rerun

- **Path:** `experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py`
- **Prereg:** `preregs/2026-06-25_substrate_compose_heterogeneous_routing_v3_full_config_rerun.md`
- **Queue:** `overnight_queue` (GPU)
- **Timeout:** 7200s
- **Anchor:** `substrate_compose_heterogeneous_routing_v3_full_config_rerun`
- **Strategic:** v2_RESCUE_FULL landed `failed` on overnight_queue (2026-06-25T01:19:24Z,
  no artifacts). v2_RESCUE (CPU) landed HARD_FAIL_PROVENANCE because rail tol 0.05 was
  INSIDE half-config noise floor 0.20-0.45 BPC. v3 reruns at SAME fair-harness rail
  config (N=8192/100k/3-seeds) + GPU setup hardening (cuda.empty_cache +
  device-mismatch asserts + mem_get_info print at startup).
- **Self-test:** PASS (ST1-ST16; including ST10 joint_sweep, ST13 LLM call counter == 0,
  ST15 D2 atexit handler registered)
- **HARD bands:** CG <=6.95 + lift >=0.20 + CV<=0.03 + sanity_rail OK
  (baseline within +/-0.05 of 7.3065); HP <=7.20 + lift >=0.10 + sanity_rail OK;
  HARD_FAIL_PROVENANCE on rail drift > 0.05; HARD_FAIL_DECISIVE if best_het <= baseline.
- **D1 roofline probe:** mandatory pre-FULL gate is already integrated; refuses dispatch
  if extrapolated wall > 0.8 * timeout.
- **Expected wall:** v2_RESCUE_FULL was projected ~60-90 min at this scale; v3 same
  envelope (probe + 3 seeds * 4 arms).
- **Honest scope caveat for Skunkworks:** if baseline still drifts > 0.05 at the matching
  rail config, the issue is upstream (encoder/Hebbian pipeline provenance), NOT
  scale-mismatch. v3 surfaces this honestly via HARD_FAIL_PROVENANCE.

## Cell 3: substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING

- **Path:** `experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.py`
- **Prereg:** `preregs/2026-06-25_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING.md`
- **Queue:** `remote_cpu_queue` (CPU-feasible; synthetic semantic data)
- **Timeout:** 3600s
- **Anchor:** `substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING`
- **Strategic:** v2 landed HARD_PASS 6/6 arms but max_cv=0.083 blocked
  CHAIN_GRADE_DEFINITIVE (requires cv<=0.05). v3 doubles seeds 3->5 + grows concepts
  (8->12 cats, 12->16 attrs, M_basic 96->144, n_heldout 8->12) for tighter CV
  through better averaging in the chain primitives.
- **Self-test:** PASS (synthetic-pass verdict_path=HARD_PASS; cat_has_recall5=1.00,
  isa_recall5=1.00 at N=1024 sparse_f=0.020)
- **HARD bands:** STAGE_1_CHAIN_GRADE_DEFINITIVE = >=5/6 PASS AND max_cv<=0.05 AND
  A3 top1>=0.95; STAGE_1_CHAIN_GRADE_ALIVE = >=5/6 PASS (any CV) = v2 status;
  STAGE_1_PARTIAL = 3-4/6.
- **Expected wall:** v2 was ~5min per seed at production N=8192; v3 with 5 seeds + larger
  concept world ~ 8-15min per seed = approximately 60-90 min total.
- **Honest scope caveat for Skunkworks:** if max_cv remains > 0.05 even at 5 seeds +
  12 categories, the chain-primitive variance has a structural floor at this scale;
  characterization either way (definitive upgrade OR variance-floor measurement).

## Routing notes

- All 3 cells are committed to origin/main at `44d82058`. Both queues (overnight_queue
  GPU + remote_cpu_queue) read origin/main, so commit must be pushed before dispatch.
  exp_dev push is harness-denied for both queues -- this is the orchestrator's lane per
  reference_hd_dispatch_queue_architecture_2026-06-19.
- Per discipline `reference_remote_dispatch_cell_readiness_checklist_2026-06-17`:
  self-test passed on .venv Python 3.11 (locally verified); HDLAB_EXP_NAME has no
  `_smoke` suffix so RUN_MODE defaults to `full`; REQUIRED_FIELDS for the runner
  satisfied (anchor_name, verdict, verdict_msg, run_mode, config_version, per_seed
  all present).
- Commit before dispatch -- DONE at `44d82058`. Push first, then queue_add.
- Per cell spec, no local smokes. Self-test PASS is sufficient per USER embargo.

## D1 / D2 / Fix #28 disciplines applied

- D1 roofline probe: integrated in Cell 2 (mandatory pre-FULL gate per v2 spec);
  Cells 1 + 3 do not have D1 probe since per-seed wall is bounded by existing v2 timings.
- D2 atexit handler + per-seed checkpoint: all three cells use
  `experiments._seed_checkpoint` with module-level atexit + SIGTERM handler that flushes
  partials BEFORE crash propagates.
- Fix #28: per-arm metrics surfaced (not just verdict_msg); detail dict carries
  by_arm_agg with bpc_best_mean, bpc_best_cv, broken_spoke_detected, gate_entropy, etc.
- Per Fix #24 GPU dispatch must actually use GPU: Cells 1 + 2 use torch.cuda + batched
  matmul + per-arm GPU memory headroom prints (Cell 2 hardening).

## Status log one-liner

exp_dev shipped 3 Wave D v3 cells (commit 44d82058): hub_spoke_E1_v3_MRC_calibrated_routing
(GPU; 3 fixes vs v2 NaN-spoke + sign-sum + gate-collapse), compose_heterogeneous_routing_v3_full_config_rerun
(GPU; SAME rail config + GPU setup hardening), stage1_SEMANTIC_concept_learner_v3_CV_TIGHTENING
(remote_cpu; 5 seeds + 12 cats for CV<=0.05 upgrade). All selftests PASS. Awaiting
orchestrator dispatch.
