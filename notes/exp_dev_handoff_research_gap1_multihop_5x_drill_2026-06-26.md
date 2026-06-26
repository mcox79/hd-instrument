# exp_dev hand-off — research: GAP 1 multi-hop reasoning 5x drill (22 candidates, top-5 dispatch)

**filed:** 2026-06-26
**trigger:** research drill `notes/research_gap1_multihop_5x_drill_2026-06-26.md` identified that all 5 substrate-native multi-hop attempts share the same FORWARD-ONLY HARD-DECISION CHAINING pathology. 9 disparate fields converge on the same meta-fix: replace per-hop one-shot argmax with bidirectional forward-backward refinement (LDPC sweep, RTS smoother) OR speculative-rollout-with-gating (VTE-MCTS) OR bond-truncated global closure (MPS) OR multi-hypothesis sampling (particle filter). Top-5 rank-ordered dispatch surfaces 5 candidates whose substrate-mappings carry zero new primitives.

**pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before shipping any anchor. If paused, this hand-off is read-only structural context for the orchestrator to pick up post-resume; do NOT ship to queue until the flag is cleared and the orchestrator/USER confirms.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and substrate-product readings; it does NOT prescribe cell-level experiment parameters. exp_dev owns the design call. The role of this file is to surface pre-registered HARD-PASS/HARD-FAIL bands so exp_dev can ship with confidence.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1, cross-field lit-anchored, lowest substrate-primitive distance)

**ANCHOR:** LDPC BIDIRECTIONAL forward-backward sum-product sweep over chain factor-graph.

- substrate-product reading: model chain as factor graph; variable nodes = hop-state vectors (one per hop); check nodes = relation-consistency constraints between adjacent variables (W-link must exist). LLR per-variable = log-ratio top-1 vs top-2 from cleanup output. Forward pass = sum-product hop-by-hop emitting LLRs; BACKWARD pass = same algorithm from endpoint to start; iterate forward-backward 3-5 sweeps until LLR convergence. Final argmax per variable. ZERO new primitives — uses existing cleanup with soft-output extraction.
- tier hint: TIER-2 (wiring change on existing pointer-chain + sum-product readout addition).
- why-now: highest P_deflated=0.45 across 22 candidates; bidirectional structurally addresses the forward-only pathology that all 5 refuted attempts share; lit anchor is 30-year-mature (MacKay-Neal 1996, Berrou-Glavieux 1993 turbo).
- pre-registered HARD-PASS: ARM_LDPC_BIDIR mean depth-5 >= 0.50 over 5 seeds at M=1000, V_C=200, V_P=10, K_set=20, N_DIM=8192; sd <= 0.06; ARM_LDPC_BIDIR > ARM_SOFT_FWD + 0.10 at paired-seed p < 0.05.
- pre-registered HARD-FAIL: ARM_LDPC_BIDIR mean depth-5 <= 0.25 (no detectable lift over baseline + 0.10 ceiling); OR LDPC adds <= 0.03 over SOFT_FWD (refutes bidirectional advantage).
- pre-registered MIDDLE_BAND (most-likely outcome under 0.20 calibration deflation): 0.30 <= ARM_LDPC_BIDIR < 0.50 (small-but-real bidirectional lift); follow-up with N1 RTS or N2 VTE.
- cost: ~2 hr CPU pre-flight + ~1-2 hr cell-author smoke (Fix #17). Single 5-arm cell combined with N1 (shared forward-pass infrastructure).
- risk class: structural-additive. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: synthetic_random_atoms_M1000_VC200_VP10_K20_N8192_seeds_0_to_4.

### ANCHOR 2 (RANK 2, complementary to ANCHOR 1, run in SAME cell)

**ANCHOR:** RAUCH-TUNG-STRIEBEL SMOOTHER forward x backward state-estimate product over chain.

- substrate-product reading: forward pass = pointer-chain v2 with PER-HOP COVARIANCE (substrate proxy = top-K=20 candidates + similarity scores treated as Gaussian-mixture). Backward pass = chain reversed from endpoint, using W^T (or learned reverse-relation atoms; substrate has bidirectional CERT atoms 587/588 sequence-binding), produces backward-marginal per hop. Smoothed estimate per hop = forward-marginal x backward-marginal (Gaussian conjugate product). Readout = argmax of smoothed per-hop. Brain analog: hippocampal reverse-replay (Foster-Wilson 2006) during sharp-wave ripples retroactively strengthens intermediates.
- tier hint: TIER-2 (no new primitive; reuses pointer-chain forward + reverse).
- why-now: P_deflated=0.45 (tied with C1); Kalman smoother is 60-year-mature with established super-additive lift over forward-only in SLAM/tracking. Substrate already has chain-grade sequence-binding for reverse direction.
- pre-registered HARD-PASS: ARM_RTS_SMOOTH mean depth-5 >= 0.50; sd <= 0.06; super-additive: ARM_RTS_SMOOTH > MAX(ARM_BASELINE, ARM_BACKWARD_ONLY) + 0.10.
- pre-registered HARD-FAIL: ARM_RTS_SMOOTH mean depth-5 <= 0.25; OR smoothed mean <= 1.05 x max(forward, backward) (no smoothing benefit).
- pre-registered MIDDLE_BAND: 0.30 <= ARM_RTS_SMOOTH < 0.50.
- cost: ~2-3 hr CPU; combined with ANCHOR 1 in single 5-arm cell to amortize forward-pass.
- risk class: structural-additive. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 1.

### ANCHOR 3 (RANK 3, dispatch CONDITIONAL on ANCHOR 1+2 outcomes)

**ANCHOR:** BG-GATED VTE-MCTS speculative-rollout chain planner.

- substrate-product reading: at each hop k, generate K_speculate=5 candidate continuations via top-K W-cleanup. For EACH candidate, run 2-step speculative further hops to get a chain-coherence score (substrate's c3 sequence-binding primitive scores chain plausibility; this is the BG-reward-prediction analog). Score = sum of speculative-hop margin scores. Commit the highest-scoring candidate; iterate. Brain analog: hippocampal theta-sweep VTE at choice points (Johnson-Redish 2007) + basal-ganglia thalamic disinhibition gating (Hazy-O'Reilly 2007). Substrate has sequence-binding primitive ready (CERT 587).
- tier hint: TIER-2/TIER-3 boundary (no new primitive but lookahead adds K_speculate-fold per-hop cost).
- why-now: dispatch ONLY if ANCHOR 1 (LDPC) AND ANCHOR 2 (RTS) deliver MIDDLE_BAND or HARD_FAIL — VTE adds a structurally distinct angle (speculative-rollout vs analytical-smoother).
- pre-registered HARD-PASS: ARM_VTE_MCTS mean depth-5 >= 0.55 (higher bar than C1/N1 because of compute cost); sd <= 0.06; > ARM_KBEAM + 0.10 (super-additive over simple K-beam).
- pre-registered HARD-FAIL: ARM_VTE_MCTS mean depth-5 <= 0.30; OR not super-additive over K-beam.
- pre-registered MIDDLE_BAND: 0.35-0.55.
- cost: ~3-4 hr CPU (lookahead-2 x K_speculate=5 x depth=5).
- risk class: structural-additive. LOW-MEDIUM.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 1.

### ANCHOR 4 (RANK 4, dispatch CONDITIONAL on ANCHOR 1-3 outcomes; structurally orthogonal)

**ANCHOR:** TENSOR-NETWORK MPS contraction with bond-dimension chi truncation over chain.

- substrate-product reading: stack of per-hop W matrices as MPS tensors (one tensor per hop, indexed by relation p_k); chain endpoint = MPS contraction starting from start-vector. KEY MOVE: per-hop SVD-truncate to keep top chi in {1, 8, 32} candidates. chi=1 = pointer-chain v2 = 0.145 baseline. chi=infinity = SR closure (2026-06-22 angle). chi=8/32 = memory-efficient SR with explicit accuracy-vs-storage knob.
- tier hint: TIER-2 (no new primitive; per-hop SVD is standard; the chi knob is the new control).
- why-now: dispatch ONLY if ANCHOR 1+2 HARD_FAIL (bidirectional refinement not enough) — MPS bond-truncation explores the CAPACITY axis instead. Also tested if ANCHOR 1+2 MIDDLE_BAND to see if bond-truncated SR adds another lift.
- pre-registered HARD-PASS: ARM_MPS_chi32 mean depth-5 >= 0.55; chi=32 > chi=8 > chi=1 monotone; chi-scaling lift observable.
- pre-registered HARD-FAIL: ARM_MPS_chi32 mean depth-5 <= 0.25; OR chi-scaling not monotone.
- pre-registered MIDDLE_BAND: 0.35-0.55.
- cost: ~2 hr CPU per chi level x 3 levels = ~6 hr.
- risk class: structural-additive. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples (chi-scan provides built-in sanity rail).
- corpus_provenance: as ANCHOR 1.

### ANCHOR 5 (RANK 5, dispatch LAST or as fallback)

**ANCHOR:** PARTICLE-FILTER sequential Monte Carlo over chain hypothesis-space.

- substrate-product reading: maintain N_particles=50, each a hypothesized chain trajectory (sequence of intermediate entities). Per hop: each particle does W-cleanup; particle weight updated by margin score; LOW-WEIGHT particles resampled from HIGH-WEIGHT (systematic-resample). Final readout = mode of particle endpoint distribution (or top-K consensus). N_particles=1 reduces to baseline; N=10 no-resample reduces to K-beam.
- tier hint: TIER-2 (SMC machinery is standard; substrate has cleanup + weight-update primitives).
- why-now: dispatch LAST or as fallback if RTS HARD_FAILs (RTS is the analytical limit; particle-filter is the sampling extension when distributions are non-Gaussian).
- pre-registered HARD-PASS: ARM_PARTICLE_FILTER mean depth-5 >= 0.55; super-additive over K-beam (resampling adds value).
- pre-registered HARD-FAIL: ARM_PARTICLE_FILTER mean depth-5 <= 0.30; OR resampling adds <= 0.03 over no-resample K-beam.
- pre-registered MIDDLE_BAND: 0.35-0.55.
- cost: ~3-4 hr CPU.
- risk class: structural-additive. MEDIUM (resampling tuning + particle-diversity collapse risk).
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 1.

### ANCHOR 6 (RANK rescue-pivot — ONLY IF TOP-5 ALL HARD_FAIL)

**ANCHOR:** DENSE-HOPFIELD-86 + SPARSE-BIPOLAR DICTIONARY per-hop primitive replacement.

- substrate-product reading: REPLACE the per-hop W cleanup primitive entirely. New primitive: dense-Hopfield energy E(x) = -sum_i exp(<x, atom_i> / T); per-hop = gradient descent on E (exponential capacity scaling, Krotov-Hopfield 2017). Sparse-bipolar dictionary (substrate-validated 20-300x bundle lift per reference_operational_findings_2026-06-23) gives orthogonal candidates. Target per-hop accuracy >= 0.90 (vs 0.69 current); depth-5 follows at 0.90^5 = 0.59.
- tier hint: TIER-1 (genuine primitive replacement; new operator).
- why-now: dispatch ONLY if top-5 ALL HARD_FAIL — the conclusion would be that per-hop primitive itself is the structural cap. Both dense-Hopfield and sparse-bipolar are substrate-validated chain-grade primitives, so combination is high-P.
- pre-registered HARD-PASS: per-hop accuracy >= 0.90 at production V_C=200; depth-5 >= 0.55.
- pre-registered HARD-FAIL: per-hop accuracy <= 0.75 (not enough lift over current 0.69 to fix depth-5).
- cost: ~6-8 hr (primitive replacement + integration); 1-2 cycle.
- risk class: structural-replacement. MEDIUM-HIGH (changes load-bearing primitive).
- lane: PRIMITIVE_REPLACEMENT_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 1.

---

## Recommended dispatch sequence

1. **IMMEDIATE (1 cycle, lowest-risk):** single 5-arm cell combining ANCHOR 1 (LDPC) + ANCHOR 2 (RTS) + the 3 sanity rails (BASELINE / SOFT_FWD / BACKWARD_ONLY). The bidirectional and smoother angles share forward-pass infrastructure — combine to amortize CPU.

2. **AFTER outcome:** if BOTH ANCHOR 1+2 MIDDLE_BAND or HARD_FAIL, dispatch ANCHOR 3 (VTE-MCTS) and ANCHOR 4 (MPS) in next cycle — these explore lookahead + bond-truncation as structurally distinct angles.

3. **CONDITIONAL:** ANCHOR 5 (particle-filter) dispatched only if ANCHOR 2 RTS HARD_FAILs (RTS analytical + particle-filter sampling are complementary).

4. **PIVOT:** if ALL of ANCHORs 1-5 HARD_FAIL, dispatch ANCHOR 6 (dense-Hopfield + sparse-bipolar primitive replacement).

---

## Context pointers (file paths, not summaries)

- Research drill: `d:/AI/hd-instrument/notes/research_gap1_multihop_5x_drill_2026-06-26.md`
- Prior multi-hop drills (NOT to re-cover):
  - `d:/AI/hd-instrument/notes/research_multihop_revival_5x_drill_2026-06-25.md` (compose-flyLSH + predictive-coding-ACC)
  - `d:/AI/hd-instrument/notes/research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md` (SR + TEM + theta-gamma)
  - `d:/AI/hd-instrument/notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` (soft-DFE + K-beam + PageRank)
  - `d:/AI/hd-instrument/notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md` (test-design biases pattern; READ FOR BIAS AUDIT)
- Cap_map: `d:/AI/hd-instrument/data/substrate_capability_map.md` (Gap 1 row)
- Pointer-chain v2 reference cell (BASELINE replication target): substrate runs at depth-5 mean 0.145, sd ~0.05.
- Production regime constants: V_C=200, V_P=10, K_set=20, n_chains=200, N_DIM=8192, M=1000.

---

## Contract section

- All 5 anchors carry pre-registered HARD-PASS + HARD-FAIL.
- Sanity rail (ARM_BASELINE reproduces 0.145 at depth-5 within +/-0.02) MANDATORY for every cell. If sanity rail fails, the cell is REJECTED before any anchor verdict is computed (test-design discipline per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]]).
- Per-arm metrics.json must be readable independently; verdict_msg framing must NOT propagate cross-arm narratives without per-arm metric verification (Fix #28).
- Cell-author smoke is MANDATORY before full dispatch (Fix #17 measurement; per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]] route via remote_cpu/orchestrator for N_DIM=8192 if cell is matmul-bound).
- Use `tools/peek_arm_metrics.py` before any tier/framing claim (per [[feedback-use-peek-arm-metrics-before-framing]]).
- Default UNDER-claim classification (per [[feedback-fix28-violation-count-internalize-harder]]); let Skunkworks tier UP.

## Autonomy declaration

exp_dev owns:
- Cell-author parameter selection (within pre-registered bands).
- Smoke vs full-run dispatch decision (per Fix #17 measurement-strict).
- Combine-into-one-cell vs separate-cells decision (recommend combined for ANCHOR 1+2; separate for ANCHOR 3+4 to isolate compute).
- Dispatch routing (local_cpu vs remote_cpu vs overnight_queue per Fix #24 GPU-must-use-GPU + Fix #14 spawn-budget <= 3 in-flight).
- Sanity-rail rejection logic (if BASELINE doesn't reproduce 0.145, REJECT the cell and re-author).

Research does NOT own:
- Cell parameters (defer to exp_dev).
- Dispatch timing (defer to orchestrator pause-state).
- Per-cell hyperparameter tuning (defer to exp_dev).
- Verdict classification (defer to Skunkworks per A5 role-separation).
