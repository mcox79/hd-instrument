# Pre-reg: substrate_gen_lm_contextgate_depth_v5_n8192_gpu

Filed: 2026-07-08 (exp_dev). Cell: `experiments/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu.py`.
Forward-move after the skunkworks-CONFIRMED HARD_FAIL of `substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu`
(base cell, commit 0dd45e89e). Keeps the v4 corpus + RAW/CLEANUP/RESIDUAL arms BIT-FOR-BIT intact; ADDS a
brain-grounded CONTEXT-GATING arm + its firing control as a PAIRED comparison in the same run.

Prior-work check (substrate KB concept-query "context gating selective admission attend most recent relevance
thalamic input gate sequence noise" --schema-version v2: top-6 cosine 0.26-0.28, ALL BELOW the 0.30 threshold ->
no strong prior-arc match; top note hits are generation-architecture chunks (position-binding, long-form
generation), NOT context-slot gating. PLUS grep experiments/ + hdlab): closest prior mechanisms are (1)
`exp_surprise_gated_pool_charlm.py` -- Titans-style surprise gate on POOL WRITES (selective admission on the
WRITE side: which items enter memory), a DIFFERENT axis from gating which CONTEXT SLOTS feed a prediction; (2)
`exp_wave14_moe_attention_routing_v1.py` / `exp_wave14_moe_gating_sharpness_v1.py` -- MoE EXPERT routing/gating
(routing to experts, not sequence-context-slot selection); (3) `exp_a3_attention.py` -- an attention-modulator
precision/recall sweep (infra knob). NONE gates the K roll-bind context slots in the noise-compounding
generation readout. The CONTEXT_GATE arm (relevance-gated admission over the K context slots before
binding/readout, in the confirmed 1st-order noise-compounding regime) is genuinely NOVEL to this arc, not a
rediscovery. Cited as the failure-regime reference: the v4 HARD_FAIL numbers below.

## Capability question
v4 CONFIRMED genuine noise-compounding in a 1st-order Markov corpus (per-step reasoning degrades with depth,
dRAW=+0.362 MEASURED) and CONFIRMED that neither shallow CA3-cleanup (dCLEAN=+0.500, WORSE) nor deep
predict-residual-TD (dRES=+1.266, WORST) fixes it. The UNTESTED brain lever is CONTEXT-SELECTION / GATING: none
of the v4 arms GATE context. A 1st-order regime is exactly the regime gating rewards -- all context beyond the
most-recent (gap-1) token is PROVABLY conditionally-independent noise, so the optimal policy DISCARDS it. The
brain does NOT denoise-all-then-average; it GATES which context is admitted (thalamic relay gating,
basal-ganglia/PFC working-memory input-gating, selective attention -- SELECTIVE ADMISSION, not cleanup). This is
our named Stage-4 attention-routing / action-selection gap, so this arm doubles as a first probe of that gap.
Question: is admission-GATING the fix for noise-compounding where denoise/residual failed?

## v4 numbers (the confirmed HARD_FAIL, cited as the reference regime)
- dRAW = +0.362  MEASURED@d:/AI/hd-instrument/data/exp_substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu_smoke/metrics.json:curves
- dCLEAN = +0.500 MEASURED@ (same file) -- shallow cleanup makes it WORSE
- dRES = +1.266  MEASURED@ (same file) -- deep predict-residual-TD is WORST
- RAW curve {K1: 2.703, K2: 2.951, K3: 3.065} MEASURED@ (same file); bigram_bpc(oracle)=2.366, unigram_bpc=5.582

## Arms (7 total; v4's 5 kept intact + 2 new; per seed, per depth K in K_GRID)
- RAW_BIND_NO_CLEANUP   -- baseline (must degrade). Hebbian readout. [v4, unchanged]
- CLEANUP_PER_STEP      -- SHALLOW antidote (CA3 cleanup each step). Hebbian readout. [v4, unchanged]
- CLEANUP_SCRAMBLED     -- shallow firing control (random attractors). [v4, unchanged]
- PREDICT_RESIDUAL_TD   -- DEEP antidote (residual injection + delta/TD readout). [v4, unchanged]
- RESIDUAL_SCRAMBLED    -- deep firing control (prediction dims permuted). [v4, unchanged]
- CONTEXT_GATE          -- NEW: relevance-gated admission over the K roll-bind context slots BEFORE
                          binding/readout. Per-slot gate g_j learned from data by each slot's predictiveness
                          for the next token (per-slot lightweight Hebbian readout cosine; g = softmax(r/tau)).
                          gated_ctx = sum_j g_j * roll(cb[tok_j], j+1), normalized, then the SAME Hebbian
                          readout as RAW. The ONLY delta vs RAW is the multiplicative admission gate g
                          (isolated selection test). For a 1st-order source the gate concentrates on the
                          most-recent slot (gap-1) and starves the older noise slots. Pure selection -- NOT
                          cleanup-bearing (no att1 conv gate on this arm).
- CONTEXT_GATE_SCRAMBLED -- NEW firing control: identical gate-weight SPECTRUM, admission STRUCTURE-DESTROYED
                          (slot order permuted so the dominant admission weight leaves the most-recent slot;
                          rejection-sampled derangement, reversal fallback). Admits the WRONG (older/noise)
                          slots -> must NOT flatten. Any CONTEXT_GATE benefit that also appears here is a
                          magnitude/renorm artifact, not selection. At K=1 the permutation is identity so
                          scramble==gate==RAW-single-token (anchor); arms diverge only at K>=2.
Reference ladder: unigram(floor), bigram_count(ORACLE for 1st-order), trigram_count. [v4, unchanged]

## Pre-registered bands (bpc in BITS; best-temp ensemble; seed-averaged; K0=1, Kmax=max(K_GRID)=5 FULL)
- VALID-ONLY-IF dRAW = raw[Kmax]-raw[K0] > 0 (RAW still degrades; else INCONCLUSIVE -- the v3 trap).
- HARD_PASS = CONTEXT_GATE has dGATE = GATE[Kmax]-GATE[K0] <= 0 (bpc NON-INCREASING with depth) AND gap_gate =
  RAW[Kmax]-GATE[Kmax] >= 0.30 bits AND (gap_gate - gap_gate_scramble) >= 0.15 (firing control does NOT
  replicate). => SELECTION IS THE LEVER: noise-compounding FIXED by admission-gating where denoise/residual
  failed. (The same HARD_PASS test is applied to CLEANUP/RESIDUAL for the paired comparison; they are expected
  to HARD_FAIL as they did in v4. Verdict names WHICH arm(s) pass.)
- MIDDLE_BAND = CONTEXT_GATE (or another antidote) partially flattens (d < dRAW) but no full HARD_PASS.
- HARD_FAIL = no antidote (incl. CONTEXT_GATE) flattens (min over antidotes of d >= dRAW) => selection is NOT
  the lever either; escalate to next drill (disjoint-block context representation).
- HP_SCOPE: HARD_PASS gates apply ONLY to {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD, CONTEXT_GATE}; RAW + all three
  scramble arms are controls (no HARD_PASS gate inherited). The att1 conv>=0.80 health gate applies ONLY to
  cleanup-bearing antidotes (CLEANUP, RESIDUAL); CONTEXT_GATE is pure selection (no cleanup) so it carries no
  att1 gate.
- P: honestly uncertain but genuinely higher than the failed denoise arms -- selection is the theoretically
  correct lever for a 1st-order source (all older context is provable noise, so discarding it cannot hurt and
  the softmax concentrates admission on the useful slot). PRIMARY MIDDLE/FAIL mechanism: the gate is SOFT
  (softmax never fully zeroes the noise slots) and learned from finite data, so residual leakage of the older
  slots may keep dGATE > 0 (partial flatten -> MIDDLE_BAND). Value = the mechanism verdict (is admission-gating
  the noise-compounding fix), per Director.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID) = 3*7*4 = 84 FULL (1*7*3 = 21 smoke);
  verdict emits HARD_FAIL_CARDINALITY_BREACH if len(per_unit) < expected.
- discriminator_fires: dRAW>0 gate (META_RULE_K/AG) -- the explicit anti-INCONCLUSIVE gate. GATE-specific
  discriminator health: learned gate must concentrate on the most-recent slot (self-test asserts argmax g ==
  K-1, g[K-1] > 0.5 on a 1st-order corpus); g/relevance logged per (seed,K) in metrics gate_log.
- baseline_in_band: RAW between unigram(floor) and 0; degradation (dRAW>0) checked, not saturation. (v4
  MEASURED RAW top1 0.49-0.57, distinct 0.63 -- well inside band, not saturated.)
- discriminator_survives_scale: ANALYTICAL (option B). The 1/sqrt(K) superposition dilution (dRAW>0) is a ratio
  effect, dimension-INDEPENDENT -> survives N=8192. The gate's selection benefit is a slot-count / signal-ratio
  effect (admitting fewer, higher-relevance slots reduces the superposition denominator), also
  dimension-independent -> the gate-vs-raw gap survives N=8192 (smoke at N=1024 is a comparable lower bound).
- arms_differ_verified: True (SHA256 of the 7 depth curves; assert at main). Anchor overlaps (RAW/RESIDUAL/GATE/
  GATE_SCRAMBLED coincide at K=1) do NOT collide because the hash is over the full {K1,K2,K3,K5} curve.
- final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace).
- crlb_n/a: perplexity/bpc has no closed-form noise floor here; discriminator is arm-vs-arm dRAW, not an
  absolute threshold.
- calibration_check: default_ok_for_this_regime (CLEANUP_TEMP=4.0/ALPHA=0.5 att1-canonical [v4]; GATE_TAU=0.1
  logged + the gate-concentration self-test is the gate-health gate; g/relevance logged per unit).
- cell_chunked: false (single cell; per-seed checkpoint via _seed_checkpoint resumable_seeds).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering=True) + per-unit flush prints +
  per-gate flush prints + emit_heartbeat per unit. (Per-arm timeout target well under audit-cadence needs;
  heartbeat covers the audit need regardless.)
- run_mode_verify: expected FULL run_mode=full, size>5KB (84 units of per-arm data + gate_log); dispatcher must
  verify landed run_mode==full.

## Test-design gates (Section 15)
- effective_vs_nominal_parameter_audit: swept axis = depth K in {1,2,3,5}. Every primitive (RAW/CLEANUP/RESIDUAL/
  GATE encoders + Hebbian/TD readouts) experiences the SAME effective K (the literal window length); no
  partition-routing indirection. sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: RAW bpc lands 2.70-3.07 bits at K=1..3 (v4 MEASURED) -> perplexity
  ~6.5-8.4 on VOCAB=70, i.e. mid-band (not saturated at unigram floor 5.58 bpc, not at bigram-oracle 2.37 bpc).
  The discriminator is a DELTA (d per arm), not an absolute-accuracy band; all K points are in the
  discriminating delta-band by construction of the 1st-order corpus. discriminating_fraction: 1.0.
- composition_edges: gate encoder -> Hebbian readout: SHAPE_MATCH (gated bundle is a normalized (B,N) context,
  identical shape to RAW's; readout is the same W@ctx). No SHAPE_MISMATCH_no_adapter.
- positive_control_arms: RAW_BIND_NO_CLEANUP reproduces the v4 baseline at the SAME regime (this cell keeps v4's
  corpus + N/K/J/M_CTX bit-for-bit); RAW dRAW>0 at smoke is the reproduce-prior-CG positive control (must match
  v4's dRAW>0 sign, tolerance is sign not magnitude since smoke N=1024 vs v4-smoke N=1024 same). Regime-extension
  audit: NONE (identical regime to v4; SHAPE_MATCH).
- functional_requirements: (1) reproduce depth-degradation -> 1st-order corpus + RAW arm (dRAW>0 gate). (2)
  selective admission -> per-slot relevance gate over K roll-bind slots (NEW mechanism; brain-grounded thalamic/
  BG input-gating; no prior substrate primitive maps, so newly designed + self-tested). (3) firing control ->
  structure-destroyed admission ordering (permuted gate). (4) reference -> exact count-table ladder.

## Compute architecture
Class: batched-GPU. Gate learning = K lightweight per-slot Hebbian readouts (transient W_j, one at a time, freed
per slot) + fresh-batch cosine; gated encode = elementwise-scaled roll-bind bundle. All matmul-heavy, batched
over BATCH=64 windows. Justified sequential dependency (inherited from v4): residual arms' delta/TD readout is an
online self-correcting learner (W_m depends on W_{m-1} -- that IS the mechanism); intra-window K-step recurrence
sequential (K<=5). Storage strategy: no_storage / no_composition (in-memory codebook + W; no PartitionedStore).

## Dispatch
Smoke: local CPU (SMOKE-only-local, N=1024, 21 units). FULL: GPU (overnight_queue OR remote_cpu_queue as the
orchestrator judges by queue state; GPU-preferred -- matmul-heavy 7-arm cell at N=8192) via Orchestrator (exp_dev
cannot push). GATE: dRAW>0 must hold at smoke + gate-concentration self-test must pass before FULL is authorized.
Per-seed checkpoint (resumable_seeds) means a timeout re-dispatch resumes remaining seeds.
