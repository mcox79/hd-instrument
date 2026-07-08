# Pre-reg: encoder_twohead_decoupled_store_retrieval_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_twohead_decoupled_store_retrieval_v1.py`
Anchor: `encoder_twohead_decoupled_store_retrieval_v1`
Trigger: the anchor-sweep payoff cell (`exp_encoder_distill_anchor_sweep_vicreg_decorr_v1`, commit 697df6a52)
MEASURED that NO scalar BGE-anchor arm gets both high superposition and high pointwise, but a decoupled-ORACLE
(decorrelated store code + BGE teacher retrieval) achieves both. This cell REPLACES the oracle with a real
TRAINED two-head architecture. Certified law: `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval`.

Prior-work check: substrate concept-query "two-head encoder decoupled store retrieval VICReg BGE" returned only
wordnet/framenet dictionary words (top hit "distillation" the noun at cosine 0.38, NOT a prior arc cell); no
existing `two_head`/`decouple` cell in experiments/. Genuinely novel (direct successor to the anchor-sweep cell).

## Question
The anchor-sweep ORACLE is an existence proof that PICKS two separate hand-made representations. Can a REAL
TRAINED two-head encoder -- a shared trunk feeding a VICReg-decorrelating STORE head and a BGE-distilling
RETRIEVAL head -- achieve BOTH high superposition recall AND high pointwise fidelity from ONE learned system,
or does the shared trunk force interference so neither head reaches target?

## Mechanism
Shared LINEAR bottleneck trunk feats = x @ W_trunk (Din=1024 -> H=512 < Din; the bottleneck FORCES the two
heads to read from the same compressed subspace -- without it a linear trunk imposes no constraint and heads
decouple trivially). Two linear heads:
- STORE head     z_store = feats @ W_store (N); loss = VICReg var-floor + off-diag covariance decorrelation.
- RETRIEVAL head z_ret   = feats @ W_ret   (N); loss = global/landmark RKD (match per-minibatch student
  pairwise-cosine matrix to BGE teacher; Gram-trick VICReg when B<=N, full cov when B>N).
Total (twohead) L = mu*L_var(z_store) + nu*L_cov(z_store) + lambda_d*L_rkd(z_ret); both heads' gradients flow
into the shared trunk (the interference test). mu=nu=lambda_d=1.0, gamma_var=1.0, lr=1e-3.

DESIGN NOTE (measured at smoke-gate design, tagged MEASURED@ below): a GELU trunk was tried FIRST and BROKE the
store head -- GELU's positive-output bias injects feature correlations that fight VICReg decorrelation,
collapsing store WTA superposition to 0.316 (below the random-projection 0.829 floor). The zero-mean LINEAR
trunk converges reliably; a zero-centered nonlinear trunk (tanh / centered features) is future work.

## Arms (6)
twohead_shared [HEADLINE] (shared trunk), twohead_split [CEILING] (independent trunk per head),
singlehead_distill [FRONTIER] (one code, RKD only = anchor-sweep distill_only), singlehead_native [FRONTIER]
(one code, VICReg only = anchor-sweep native_trained), teacher_bge [REF] (raw unit BGE), native_untrained [REF]
(random W + WTA, superposition ceiling).

## Metrics (uniform per arm)
- STORE metric = superposition recall@J on the WTA block code (3.125% sparsity) of the STORE code.
- RETRIEVAL metric = single-concept pointwise recall@alpha on the DENSE RETRIEVAL code (noisy source encoded
  THROUGH the head, argmax-cosine over the dict). Retrieval does NOT need sparsity; dense is its natural readout.
- CROSS-CHECKS (logged, not gating): store-head SC_dense (must NOT be forced BGE-like) + ret-head SP_wta (must
  NOT be forced decorrelated) -- confirm the two heads specialized.
- achieves_both = store SP_wta@J_OP(5) >= SP_HI AND ret SC_dense@alpha_OP(1.2) >= SC_HI.

## Pre-reg bands (envelope-fail; HEADLINE = twohead_shared)
SP_HI=0.83 (>= the decorrelated single-code frontier ~0.828; headroom to the 0.905 ceiling per META_RULE_L),
SC_HI=0.90 (approaching teacher 1.0), MIDDLE_TOL=0.05.
- `HARD_PASS_TRAINED_TWOHEAD_ACHIEVES_BOTH` = twohead_shared store SP_wta>=0.83 AND ret SC_dense>=0.90.
- `MIDDLE_ONE_HEAD_HITS` = exactly one head hits, the other within MIDDLE_TOL of its target.
- `HARD_FAIL_ONE_HEAD_FAR_MISS` = one head hits, the other misses by > MIDDLE_TOL.
- `HARD_FAIL_SHARED_TRUNK_NO_GAIN_OVER_SINGLE_CODE` = shared joint <= best single-head arm's joint (trunk
  sharing gained nothing over a single code).
- `HARD_FAIL_SHARED_TRUNK_INTERFERES_NEITHER_HEAD` = neither head hits (shared trunk forces collapse).
Enrichment (reported, not gating): twohead_split achieves_both (CEILING / interference-cost = split_SP - shared_SP);
and whether a single distilled/native code with DUAL READOUT already achieves both (a simpler solution surfaced).

## Compute architecture
Class (a) batched-GPU. Training matmul-heavy (per-iter RKD pairwise B x B + VICReg covariance over a minibatch +
trunk/2-head forwards); 4 trained arms x 5 seeds x hundreds of iters. Storage: no_composition/no_store
(encoder-geometry cell; per-concept codes evaluated by argmax-cosine cleanup, not a bundled store). FULL routes
to GPU (overnight_queue): N=4096, B=8192 > N gives a full-rank covariance estimate; cell auto-selects cuda.
SMOKE is CPU-local at N=2048 (linear trunk is fast on CPU; the shared-vs-split interference is an ARCHITECTURAL
property that fires at any N -- DISCRIMINATOR-MUST-SURVIVE-SCALE option B + N=2048 preview + N=1024 design probe).

SMOKE SCOPE LIMITATION (declared honestly): at smoke V=1500 the RETRIEVAL SC_dense metric SATURATES ~0.99 for
all trained arms (discriminating one noisy concept among 1500 is easy) -- the retrieval discriminator fires only
at FULL V=40000 (the anchor sweep showed the SP/SC bands widen with V: SP gap -0.561 at V=4000, -0.662 at
V=40000). Smoke fires the STORE (SP_wta) discriminator (spread 0.796-0.981, correctly ordered
native>twohead>teacher>distill) and the shared-vs-split interference; the retrieval-at-scale test is a FULL
question. This is the intended smoke->FULL handoff, not a masked saturation.

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = all-arm measurement)",
  "arms_differ_verified": true,
  "arms_differ_exempted": [],
  "arms_differ_note": "arm-name init salt added so twohead_split store branch (VICReg-only, indep params) does NOT draw bit-identical to singlehead_native; MEASURED distinct hashes at smoke.",
  "baseline_in_band": "singlehead_distill store SP_wta@J5 in (0.05,0.95); MEASURED smoke 0.796",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "retrieval recall + geometry cosines; no closed-form noise floor. Feasibility calibrated by the anchor-sweep MEASURED SP band 0.43-0.905 and SC band 0.655-1.0 at this exact regime.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime",
  "cell_chunked": false,
  "cell_chunked_justification": "follows anchor-sweep template (multi-seed single-cell with per-seed partial checkpoint+resume; each seed ~2.5min; runner-death loses only the in-progress seed, resumes from partial).",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "print_flush cadence <60s (per-arm SP/SC line + per-iter every iters//6 + per-seed [seed-done]); FULL est <30min; follows anchor-sweep template.",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (no swept axis; arms are architecture variants, each experiencing its own loss directly; no partition/effective-param indirection)",
  "discriminating_fraction": "smoke MEASURED STORE SP_wta spread 0.796-0.981 across arms (>30% of arms in a discriminating band; the store axis is the load-bearing discriminator). Retrieval SC discriminator fires at FULL V=40000 (declared smoke-scope limitation).",
  "positive_control_arms": "native_untrained reproduces the anchor-sweep zero-train WTA code (SP_wta@J5 MEASURED smoke 0.905 ~ 0.905 anchor-sweep); teacher_bge reproduces BGE (SC 1.0). singlehead_distill reproduces the anchor-sweep distill frontier (store SP 0.796, below the 0.83 decorrelation frontier).",
  "telemetry_sensitivity": "self-test asserts twohead_shared store SP_wta@J5 differs across seeds 7 vs 13 (not analytically pinned) AND singlehead_native SC_dense differs across seeds (SC is data-sensitive; it saturates only for well-distilled heads, the GOAL). MEASURED PASS.",
  "functional_requirements": "FR1 high superposition capacity (store head, VICReg decorrelation -> WTA block code); FR2 high single-concept pointwise fidelity (retrieval head, RKD BGE-distillation -> dense readout); FR3 both from ONE shared-trunk system (the interference test). Each FR maps to an existing chain-grade primitive (VICReg decorrelation certified +0.255; RKD distillation R1 of the deep-drill note; WTA superposition harness from the anchor-sweep cell)."
}
```

## Self-test + smoke (MEASURED)
- `--self-test` PASS (7 witnesses): valid_enc (teacher J1=1.000), telemetry-sensitivity (store SP + SC move
  across seeds), arms_differ (6 distinct store hashes), both_heads_train, wta_boosts (store WTA 0.876 >> dense
  0.119 -- decorrelation lever fires), heads_specialize (twohead retSC 0.995 > storeSC 0.915 -- heads are NOT
  the same code on the shared trunk), sc_noise.
  MEASURED@data/exp_encoder_twohead_decoupled_store_retrieval_v1 (self-test stdout).
- GELU-trunk broke the store head: shared+ret store SP 0.746, STORE-ONLY store SP 0.316 (< random 0.829).
  MEASURED@/tmp design-probe hp2/hp3 (N=1024 small BGE cache).
- LINEAR trunk (design probe, N=1024, H=512): shared+ret store SP 0.895, store-only 0.966, split 0.966; H=1024
  (no bottleneck) shared 0.958 ~ split 0.949 (heads decouple; bottleneck needed for a real test).
  MEASURED@/tmp design-probe hp3.
- SMOKE (N=2048, H=512, V=1500, B=1024, 150 iters, seeds 7/13/19; ~7.3 min CPU): verdict
  `HARD_PASS_TRAINED_TWOHEAD_ACHIEVES_BOTH`. All gates pass.
  MEASURED@data/exp_encoder_twohead_decoupled_store_retrieval_v1/metrics.json:
  - twohead_shared [HEADLINE]: store SP_wta@5 = 0.963 (cv 0.006), ret SC_dense@1.2 = 0.995 -> both=True (joint 1.105).
  - twohead_split [CEILING]: SP 0.978, SC 0.997 -> both; interference cost of sharing = 0.978-0.963 = 0.015 (mild).
  - singlehead_distill [FRONTIER]: SP 0.796 (MISSES store 0.83), SC 0.993 -> not both (RKD single code stays crowded).
  - singlehead_native [FRONTIER]: SP 0.981, SC 0.987 -> both (single VICReg code DUAL READOUT also achieves both;
    honest secondary finding -- but SC_dense saturates at smoke V=1500; whether a decorrelated DENSE code retains
    pointwise at FULL V=40000 is the key open FULL question, where the RKD retrieval head is expected to hold).
  - teacher_bge: SP_wta 0.884 (WTA decorrelates even BGE), SC 1.0. native_untrained: SP_wta 0.905.
  - cross-check: twohead_shared store-head SC_dense 0.964 (not forced BGE-like), ret-head SP_wta 0.963 (not forced
    decorrelated) -- heads specialized on the shared trunk.

## FULL dispatch (GPU overnight_queue; gated on Director go + pause lift)
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_twohead_decoupled_store_retrieval_v1 experiments/exp_encoder_twohead_decoupled_store_retrieval_v1.py preregs/encoder_twohead_decoupled_store_retrieval_v1.md 3600`
(runner invokes with `--run-mode full`; cell auto-selects cuda when available. Post-dispatch: verify landed
metrics.json run_mode==full + size (section 16 RUN_MODE VERIFICATION).)

ASCII-only. No unicode. No emojis. No em dashes.
