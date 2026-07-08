# Pre-reg: substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu

Filed: 2026-07-08 (exp_dev). Cell: `experiments/exp_substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu.py`.
Corrected rebuild of `exp_substrate_gen_lm_perstep_cleanup_depth_v3` (INCONCLUSIVE: its 2nd-order corpus did
NOT reproduce context-hurts-with-depth; it never built the deep predict-residual arm).

Prior-work check (substrate KB concept-query "context depth generation noise compounding cleanup predict
residual TD bootstrap"): top hits cosine 0.28-0.29, all BELOW 0.30 threshold -> no strong prior-arc match; the
residual-injection + TD-bootstrap-readout composition is genuinely novel to the substrate arc (not a
rediscovery). The 4 prior context-depth cells are cited as the failure-regime reference, not the mechanism.

## Capability question
The substrate has a documented 3-HARD_FAIL/1-MIDDLE history where context makes next-token prediction WORSE
with depth (exp_n2_context_depth_hd_binding_v1: bpc 5.00->5.05->5.18 for K=1->2->3). Is that NOISE-COMPOUNDING
(fixable) or CAPACITY-CEILING (not)? And does the brain's DEEP antidote (predict-residual injection + TD/delta
self-correcting readout, per the predictive-coding + successor-representation lit-scan) beat the SHALLOW
antidote (per-step CA3 cleanup)?

## FIX 1 -- reproduce the failure first (SMOKE-must-reproduce-the-phenomenon)
Regime = **1st-ORDER Markov corpus** (true dependency window = 1 token). All context beyond K=1 is provably
conditionally-independent noise. RAW roll-bind superposition of K tokens dilutes the single useful (most-recent)
token to ~1/sqrt(K) of the normalized state -> bpc RISES monotonically with K (dRAW>0) BY CONSTRUCTION. This is
the cleanest possible PURE noise-compounding testbed and cleanly separates noise-compounding from capacity-
ceiling (which real text confounds). FIRST GATE (verdict): dRAW = raw[Kmax]-raw[K0] > 0 else INCONCLUSIVE +
re-spec (the exact v3 trap). MEASURED@smoke below.

## FIX 2 -- all 3 arms + 2 firing controls (v3 skipped the deep arm)
- RAW_BIND_NO_CLEANUP  -- baseline (must degrade). Hebbian readout.
- CLEANUP_PER_STEP      -- SHALLOW antidote (CA3 cleanup each step). Hebbian readout.
- CLEANUP_SCRAMBLED     -- shallow firing control (random attractors).
- PREDICT_RESIDUAL_TD   -- DEEP antidote: inject residual e=actual-predicted (predictive-coding/DPCM), CA3
                           cleanup retained, delta/TD self-correcting readout (successor-features gamma=0). At
                           K=1 reduces to RAW-single-token (c_0=0 -> pred=0 -> e=actual); diverges only at K>=2.
- RESIDUAL_SCRAMBLED    -- deep firing control (prediction dims permuted -> structure-destroyed residual).
Reference ladder: unigram(floor), bigram_count(ORACLE for 1st-order), trigram_count.

## Pre-registered bands (bpc in BITS; best-temp ensemble; seed-averaged; K0=1, Kmax)
- VALID-ONLY-IF dRAW > 0 (else INCONCLUSIVE).
- HARD_PASS = an antidote arm A in {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD} has d_A = A[Kmax]-A[K0] <= 0 (bpc
  non-increasing with depth) AND gap_A = RAW[Kmax]-A[Kmax] >= 0.30 bits AND (gap_A - gap_control) >= 0.15
  (matched firing control does NOT replicate) AND att1 healthy (converged_frac >= 0.80 for cleanup-bearing
  arms). Verdict names WHICH arm + whether DEEP beat SHALLOW (gap_res - gap_clean >= 0.15).
- MIDDLE_BAND = some antidote partially flattens (d_A < dRAW) but no HARD_PASS.
- HARD_FAIL = no antidote flattens (min(dCLEAN,dRES) >= dRAW) => CAPACITY CEILING; redirect disjoint-block.
  (both cleanup arms conv<0.50 => HARD_FAIL_ATT1_MALFUNCTION, confounded.)
- HP_SCOPE: HARD_PASS gates apply ONLY to {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD}; RAW + both scramble arms are
  controls (no HARD_PASS gate inherited).
- P_deflated ~0.25-0.30 (documented 3 HARD_FAIL + 1 MIDDLE on this family; MIDDLE/HARD_FAIL likely; the value
  is the mechanism decomposition, not a headline win). Primary HARD_FAIL mechanism for the deep arm: the
  ~0.507 concept-recall analog -- a frequently-wrong prediction injects a wrong-code residual noisier than the
  raw token.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID) = 3*5*4 = 60 FULL (15 smoke); verdict
  emits HARD_FAIL_CARDINALITY_BREACH if len(per_unit) < expected.
- discriminator_fires: dRAW>0 gate (META_RULE_K/AG) -- the explicit anti-INCONCLUSIVE gate.
- baseline_in_band: RAW between unigram(floor) and 0; degradation (dRAW>0) checked, not saturation.
- discriminator_survives_scale: ANALYTICAL (option B). 1/sqrt(K) superposition dilution is a ratio effect,
  dimension-INDEPENDENT, so dRAW>0 survives N=8192 (smoke at N=1024 is a stronger-degradation lower bound).
- arms_differ_verified: True (SHA256 of the 5 depth curves; assert at main).
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- crlb_n/a: perplexity/bpc has no closed-form noise floor here; discriminator is arm-vs-arm dRAW, not an
  absolute threshold.
- calibration_check: default_ok_for_this_regime (CLEANUP_TEMP=4.0/ALPHA=0.5 are att1-canonical; conv logged as
  gate; att1-malfunction branch guards the confound).
- cell_chunked: false (single cell; per-seed checkpoint via _seed_checkpoint).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering=True) + per-unit flush prints +
  emit_heartbeat per unit. (FULL timeout_s target < 1800 per-arm; heartbeat covers the audit need regardless.)
- run_mode_verify: expected FULL run_mode=full, size>5KB (60 units of per-arm data); dispatcher must verify.

## Compute architecture
Class: batched-GPU. All arms matmul-heavy (W@ctx readout, cleanup w@CB, delta-update outer). Justified
sequential dependency: the residual arms' delta/TD readout is an ONLINE self-correcting learner (W_m depends on
W_{m-1} -- that IS the mechanism); intra-window K-step recurrence sequential (K<=5). Everything else batched
over BATCH=64 windows. Storage strategy: no_storage / no_composition (in-memory codebook + W; no PartitionedStore).

## Functional requirements
1. Reproduce depth-degradation -> 1st-order corpus + RAW arm (dRAW>0 gate).
2. Shallow denoise-after -> CA3 iterative_attractor cleanup per step (existing primitive, torch-ported +
   selftest-matched to numpy ref).
3. Deep inject-less -> residual injection (bind/unbind = roll + vector residual) + delta/TD readout.
4. Firing controls -> scrambled attractors (shallow) + permuted prediction (deep).
5. Reference -> exact count-table ladder (unigram/bigram-oracle/trigram).

## Dispatch
Smoke: local CPU (SMOKE-only-local, N=1024). FULL: overnight_queue (GPU, N=8192) via Orchestrator (exp_dev
cannot push). GATE: dRAW>0 must hold at smoke before FULL is authorized.
