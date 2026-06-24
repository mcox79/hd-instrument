# exp_dev hand-off — research: composition collapse critical drill

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-24
**Trigger:** companion to `notes/research_composition_collapse_critical_drill_2026-06-24.md`
**Source negatives:**
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 HARD_FAIL_SUB_ADDITIVE)
- `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` (K=2 x cf-RPE HARD_FAIL)
- `data/exp_substrate_continual_learning_spectrum_v1/metrics.json` (CL spectrum HARD_FAIL forgetting=0.650)
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; if paused, hold

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off contains anchor candidates + context pointers + autonomy declaration. exp_dev OWNS cell design (smoke gate, pre-reg envelope, ship-via-queue_add).

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (PRIMARY) — `exp_substrate_compose_temperature_extended_grid_v1`

**Anchor pointer:** decisive test of logit-distribution-shape diagnosis at extended T-grid + β-sweep + MH-disabled
**Substrate-product reading:** confirms or refutes H3 (readout failure); cheapest path to either fix or pivot to H1/H4
**Tier hint:** MM (decisive single-hypothesis test); diagnostic, not chain-grade-graded
**Why-now:** the smoking gun is in A1's per-arm metrics — best_T flipped from 0.02 to 1.0 (50x) exactly when MH cleanup added, all 3 seeds, every lambda. Grid was capped at T=1.0. The grid maximum was insufficient. Single cell with extended grid + β-sweep decisively answers whether the failure is fixable readout-shape or deeper.
**Runtime estimate:** ~30min CPU local (no GPU needed for diagnostic)

**Pre-reg HARD bands (per research note L4 Prediction 1):**
- HARD_PASS: `ARM_FULL_JOINT_T_EXTENDED@T>=5.0` BPC <= 7.20 OR `ARM_FULL_JOINT_BETA_SWEEP@β<=2.0` BPC <= 7.10 (H3 confirmed)
- HARD_FAIL: BOTH `ARM_FULL_JOINT_T_EXTENDED@T<=50.0` BPC >= 7.50 AND `ARM_FULL_JOINT_BETA_SWEEP@β=0.5` BPC >= 7.20 (H3 refuted; pivot to H1/CELL 2)
- MIDDLE_BAND: BPC in [7.20, 7.50] at best extended-setting (logit-shape partial; gradient-conflict also contributes; investigate both)

**Instrumentation (suggested):**
- Per-arm at best (T, lambda): log post-MH logit entropy + KL(MH_logits || K2_logits)
- Log mh_cleanup_applied=True/False per arm (already in A1 cell schema)
- Log raw_bpc_at_T1_L1 across all extended-grid arms

### ANCHOR 2 (CONDITIONAL on Anchor 1 HARD_FAIL or MIDDLE_BAND) — `exp_substrate_pcgrad_cfrpe_stdp_v1`

**Anchor pointer:** test gradient-conflict diagnosis (H1) via PCGrad-style projection between cf-RPE and STDP plasticity updates
**Substrate-product reading:** if H3 refuted, validates H1 secondary mechanism; suggests either PCGrad or learned-routing fix
**Tier hint:** MM; chain-grade-eligible if `ARM_PCGRAD_CFRPE_STDP` BPC <= 7.05 (matches or beats CFRPE-only chain-grade 7.09)
**Why-now:** gated on Anchor 1 result; STDP empirically reverses cf-RPE -0.116 in 3/3 seeds — textbook PCGrad scenario
**Runtime estimate:** ~45min CPU local

**Pre-reg HARD bands:**
- HARD_PASS: `ARM_PCGRAD_CFRPE_STDP` BPC <= 7.05 (PCGrad rescues hetplast collapse)
- HARD_FAIL: `ARM_PCGRAD_CFRPE_STDP` BPC >= 7.20 (gradient projection doesn't help; conflict not first-order)
- MIDDLE_BAND: BPC in [7.05, 7.20] — PCGrad partial; investigate trained K=2 gate

### ANCHOR 3 (PARALLEL — sparse-bipolar amplitude audit, NO cell) — `audit_a1_codebook_amplitude`

**Anchor pointer:** read A1 cell's `make_sparse_bipolar_codebook` to check whether amplitudes are scaled (1/sqrt(f)=4.47) or raw +/-1
**Substrate-product reading:** if raw, all A1 arms inherit the 06-23 -17dB receiver penalty (constant across arms; doesn't explain FULL_JOINT differential but affects absolute lift)
**Tier hint:** AUDIT only; ~5min code-read
**Why-now:** parallel with Anchor 1; cheap; might reveal compounding mechanism
**Runtime estimate:** ~5min code read; no cell needed

**Audit criteria:**
- If amplitude scaled (1/sqrt(f)): no compounding sparse-bipolar penalty; ABSOLUTE A1 baseline (7.30 BPC) is calibrated
- If amplitude raw (+/-1): all A1 arms are -17dB receiver-SNR penalized; absolute baseline could be ~0.20-0.50 BPC better with amplitude scaling
- IF raw: file separate `exp_substrate_a1_amplitude_scaled_rerun_v1` cell

### ANCHOR 4 (DEFERRED — only if Anchors 1+2 BOTH HARD_FAIL) — `exp_substrate_shared_state_integration_v1`

**Anchor pointer:** test integration-architecture diagnosis (H5) via simultaneous gradient + shared-state register
**Substrate-product reading:** if H3+H1 refuted, motivates substrate-native cortical microcircuit primitive
**Tier hint:** novel-synthesis P_capped=0.40; chain-grade-eligible if shared-state arm exceeds best-single by >=0.10
**Why-now:** ONLY if Anchors 1+2 BOTH fail; deeper architectural intervention; defer until ruled in
**Runtime estimate:** ~2-4h CPU local OR remote_cpu_queue

**Pre-reg HARD bands:**
- HARD_PASS: `ARM_SHARED_STATE_INTEGRATION` BPC <= 6.95 (exceeds best-single by >=0.10)
- HARD_FAIL: `ARM_SHARED_STATE_INTEGRATION` BPC >= 7.20 (shared state doesn't help; revisit roadmap)

---

## Context pointers (file paths only; no summaries)

**Empirical (load-bearing):**
- `d:/AI/hd-instrument/data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 source negative; per-arm best_T smoking gun)
- `d:/AI/hd-instrument/data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` (K=2 + cf-RPE secondary negative)
- `d:/AI/hd-instrument/data/exp_substrate_continual_learning_spectrum_v1/metrics.json` (CL spectrum tertiary negative)
- `d:/AI/hd-instrument/data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (baseline rail 7.3065)
- `d:/AI/hd-instrument/data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json` (cfRPE 7.1052; hetPlast 7.1654 reference rails)
- `d:/AI/hd-instrument/data/exp_modern_hopfield_n_sweep_v1/metrics.json` (modern-Hopfield row 100 reference; MH source)

**Source code (existing implementations):**
- `d:/AI/hd-instrument/experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` (A1 cell; baseline for Anchor 1 — extend TEMP_GRID + add BETA_GRID)
- `d:/AI/hd-instrument/experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py` (encoder + K=2 base)
- `d:/AI/hd-instrument/experiments/_seed_checkpoint.py` (per-seed checkpoint scaffold to reuse)

**Research notes:**
- `d:/AI/hd-instrument/notes/research_composition_collapse_critical_drill_2026-06-24.md` (THIS drill; full L1-L5 + 3 ranked anchors + symmetric negativity check)
- `d:/AI/hd-instrument/notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter receiver framework; co-operating mechanism)
- `d:/AI/hd-instrument/notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md` (sparse-bipolar compose audit; 2x2 factorial)
- `d:/AI/hd-instrument/notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` (A1 anchor source; substrate-mining context)

**Hdlab/ primitives (existing; may need update):**
- `d:/AI/hd-instrument/hdlab/` — check for `modern_hopfield.py`; if exists, audit for β configurability; propose new `hdlab/soft_modern_hopfield.py` with β<=2 default for LM contexts (if Anchor 1 HARD_PASS)
- propose new `hdlab/compose_interface_audit.py` utility to verify upstream output distribution matches downstream input assumption

**Audit targets (cells currently in flight that may inherit the bug):**
- K-module heterogeneous compose cell abda9f08 — check if MH cleanup is in any arm; if yes, may inherit logit-shape mismatch
- Any other compose cell using modern-Hopfield + LM readout

---

## Contract

exp_dev OWNS:
- Pre-reg envelope per Anchor 1 HARD bands above (mandatory both directions)
- Smoke gate at N=512, M=50 before full N=8192 dispatch (per [[long-cells-must-checkpoint-resume-restartable]])
- Self-tests on: TEMP_GRID extension produces valid logits at T=50; BETA_GRID variation produces non-identity MH output at all β; MH-disabled arm equals K=2-baseline arm (sanity)
- ASCII-only, no emojis
- Per-seed checkpoint + restartable (use `experiments/_seed_checkpoint.py`)
- Commit prereg note + cell to origin/main BEFORE remote dispatch (if remote-routed)
- Post-ship REMOTE VERIFY: `python tools/peek_arm_metrics.py <anchor_name>` to confirm per-arm metrics before tier framing
- Apply `tools/predispatch_check.py <anchor>` before spawn (per Fix #26)
- Read per-arm metrics (NOT verdict_msg framing) before any cross-cell convergence claim (per Fix #28)

exp_dev does NOT:
- Re-design the hypothesis (research has set it; pre-reg is immutable post-dispatch)
- Skip the smoke gate
- Dispatch Anchor 4 (deferred) unless Anchors 1+2 BOTH HARD_FAIL

---

## Autonomy declaration

exp_dev decides:
- N_DIM for diagnostic (8192 matches A1; could reduce to 4096 for speed; recommended 8192 to match A1 conditions)
- Whether to bundle Anchor 1's three arms (T_EXTENDED + BETA_SWEEP + MH_DISABLED) into single mega-cell OR ship sequentially (recommended: single cell; arms share data + encoder + W)
- Whether Anchor 3 audit happens BEFORE Anchor 1 dispatch (recommended: yes; cheap; 5min)
- Routing queue (local_cpu_queue recommended; ~30min CPU; no GPU needed for diagnostic)
- Whether to include sweep over MH_ITERS (in addition to MH_BETA) — could be informative; recommended optional
- Smoke-gate criteria (suggest pipeline-validity PASS + non-identity MH at all tested β)

---

## Cert chain expectation

If Anchor 1 HARD_PASS:
- Atomize: `mh_high_beta_is_pattern_completion_not_lm_predictive_distribution_meta_2026-06-24` (META, chain-grade-eligible)
- Atomize: `compose_module_interface_assumption_audit_required_before_stacking_meta_2026-06-24` (META, general compose discipline)
- Atomize: `per_primitive_hyperparameter_tuning_does_not_transfer_to_compose_meta_2026-06-24` (HP-mismatch discipline)
- Add hdlab/ primitive: `hdlab/soft_modern_hopfield.py` (β<=2.0 default for LM contexts)
- Re-dispatch A1 cell with β=2.0 (or whatever Anchor 1 finds optimal); EXPECT BPC <= 7.05 (super-additive achievable)
- cap_map row `substrate_LM_compose_5_primitives_super_additive` upgrades from HARD_FAIL to MIDDLE_BAND
- Source research note `research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` gets POST-EXPERIMENTAL CORRECTION (A1 anchor framing was correct but MH β=8 was wrong default)

If Anchor 1 HARD_FAIL or MIDDLE_BAND → dispatch Anchor 2:

If Anchor 2 HARD_PASS:
- Atomize: `pcgrad_resolves_cfrpe_stdp_heterogeneous_plasticity_destructive_interference_meta_2026-06-24` (META, chain-grade-eligible)
- Add hdlab/ primitive: `hdlab/pcgrad_projection.py` (gradient surgery for substrate plasticity rules)
- cap_map row gets MIDDLE_BAND with H1 (gradient conflict) primary diagnosis

If Anchor 2 HARD_FAIL:
- Atomize: `gradient_projection_not_load_bearing_for_substrate_compose_failure_2026-06-24` (META, negative result)
- Route back to Research for re-drill on H5 architecture diagnosis
- Dispatch Anchor 4 (shared-state integration) with explicit P_capped=0.40 + 2-4h budget

If Anchor 1 MIDDLE_BAND:
- Atomize partial finding
- BOTH Anchor 2 + (optionally Anchor 3 amplitude audit) dispatched
- Likely composite fix: β-tune + PCGrad + amplitude-scaling

---

## Watch out for

- The A1 cell sets `MH_BETA = 8.0` hard-coded; the BETA_SWEEP arm needs to be a CONFIG variation, not a rebuild
- The TEMP_GRID extension to T=50 may surface numerical issues at exp(z/0.5) for large z; consider clipping logits to [-30, 30] before softmax
- The "MH_DISABLED" arm should literally be identity (no MH apply) — verify this exactly equals the K=2 baseline arm
- The cell takes ~30min CPU because the encoder load + corpus prep dominate; arms themselves are fast
- A1 cell uses CUDA when available; for this diagnostic CPU is fine (smaller arms)

---

*Hand-off filed 2026-06-24 by Research. Companion to research note. exp_dev auto-discovers via `notes/exp_dev_handoff_*.md` mtime sort.*
