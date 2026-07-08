# Pre-reg: recall-ceiling capacity-vs-semantic decomposition (v1)

Anchor: `recall_ceiling_capacity_vs_semantic_decomp_v1`
Cell: `experiments/exp_recall_ceiling_capacity_vs_semantic_decomp_v1.py`
Date: 2026-07-08. Author: exp_dev. Type: DIAGNOSTIC / measurement (not a fix).

## Question
The concept-recall ceiling (~0.5 cos-to-target / argmax recall observed on the
migration encoder; backup 2026-07-08 line 29: "delta-W predictor caps at ~0.52
cos-to-target == the 0.507 concept-recall ceiling") has an UNDER-DETERMINED cause.
Decompose it: is it CAPACITY-bound (dimensionality N / code density / associative-
store crosstalk) or SEMANTIC-FIDELITY-bound (encoder teacher / objective quality)?
Output = which factor is load-bearing + the sensitivity of recall to each.

## Prior-work check (substrate-KB concept-query, USER-locked)
`bash tools/substrate_query.sh "concept recall ceiling capacity dimensionality vs
semantic encoder fidelity decomposition"` -> top hits: "Advantage 4:
Compositionality depth" cos=0.3545 (a drill NOTE, generic); "Dimensionality"
cos=0.3252 (a frame-potential prereg); `ghrr_vs_fhrr_triple_encoder_capacity_
directionality_cpu_v1` cos=0.3184 (MIDDLE_BAND, a capacity-directionality metric,
NOT a capacity-vs-semantic decomposition). NONE is a prior arc cell that
decomposes the recall ceiling into capacity-vs-semantic isolation arms.
GREP of experiments/*encoder* + *recall* + grep "0.507" over experiments/notes:
0.507 appears ONLY in the backup doc (a derived number, never a hardcoded metric);
no existing cell runs this factorial. GENUINELY NOVEL (not a rediscovery): the
capacity/semantic isolation-arm decomposition + capacity-saturation control is new.

## Model (clean synthetic; USER: smoke clean synthetic not substrate state)
V concepts have intrinsic meaning vectors m in R^256 with within-group correlation
rho (SEMANTIC crowding / near-dup). Encoder renders a meaning into an N-dim bipolar-
sign HD code via a fixed random projection W, with teacher-noise sigma_e (encoder /
objective quality). Recall = argmax cosine of an independently re-encoded query over
the V stored codes. Two observables: cos_to_target (fidelity, mirrors 0.507) and
argmax recall (discrete retrieval).

Physics that separates the hypotheses (verified in calibration + self-test):
- cos_to_target is set by sigma_e and is N-INVARIANT: capacity provably cannot buy
  encoder fidelity (a purely SEMANTIC ceiling).
- recall is N-recoverable up to an asymptote set by sigma_e/rho: N and encoder-
  fidelity TRADE OFF through the same argmax margin. A clean "capacity-only wins"
  regime is PHYSICALLY IMPOSSIBLE (capacity only binds when the encoder is imperfect,
  and then improving the encoder also helps). The decomposition measures the RELATIVE
  lever strength + capacity SATURATION at the operating point.

## Arms (6-arm factorial, run at 2 regimes)
FULL (N*, se*, rho*); CAP_IDEAL (N->N_high); SEM_IDEAL (se->se_lo, rho->0);
ORACLE (both ideal, ~1.0 positive control); SEM_FIDELITY_IDEAL (teacher only);
SEM_CORR_IDEAL (correlation only). gains vs FULL; D = semantic_gain - capacity_gain.

## HARD-PASS / HARD-FAIL bands (which-factor verdict; SYMMETRIC, both directions)
PRIMARY (faithful, well-provisioned N=4096, recall mid-band ~0.5):
- HARD_SEMANTIC iff D_primary >= +0.15 AND semantic_gain >= 0.20
- HARD_CAPACITY iff D_primary <= -0.15 AND capacity_gain >= 0.20
- else MIDDLE_BAND_MIXED
COS-TO-TARGET ceiling (the 0.507-matching metric): SEMANTIC iff
teacher_effect - N_effect >= 0.15 (capacity range across N sweep near 0).
CAPACITY-SATURATION credibility control (starved N=64, good encoder):
- require capacity_gain_starved >= 0.20 AND capacity_gain_starved >
  capacity_gain_provisioned (lever demonstrably FIRES when starved, SATURATES when
  provisioned); else HARD_FAIL_CAPACITY_LEVER_INERT (whole-cell untrusted -- a small
  primary capacity_gain would be uninterpretable).

## Telemetry-sensitivity (discriminator-must-be-telemetry-sensitive lesson)
Self-test asserts FULL recall is NOT bit-identical across seeds (0.517 != 0.590),
cos_to_target moves with sigma_e (d=0.391) but NOT with N (|d|=0.006). The
discriminator D is a function of the seed-varying FULL/CAP arms; not analytically
pinned. MEASURED@self-test (see below).

## Smoke result (multi-seed, 3 seeds, reduced scale N=2048 V=5000) -- FIRES BOTH BRANCHES
MEASURED@data/exp_recall_ceiling_capacity_vs_semantic_decomp_v1/metrics.json:
verdict HARD_SEMANTIC; FULL_recall=0.560; D=+0.334; sem_gain=+0.440
(fidelity=+0.440, corr=+0.229); cap_gain=+0.106; capacity-saturation control
cap_gain_starved=+0.547 > provisioned=+0.106 lever_fires=True; cos-to-target
N-effect=0.018 vs teacher-effect=+0.462 -> SEMANTIC; rank fidelity>corr>capacity;
slopes dR/dN=5.4e-05 (flat/saturated) dR/dSigmaE=-1.02 dR/dRho=-0.89.
Full-regime calibration MEASURED@scratchpad calib6: FULL 0.504, CAP_IDEAL 0.601
(+0.097), SEM_IDEAL 1.000 (+0.496), D_primary +0.399.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds x 2 regimes (5x2=10 full; 3x2=6
  smoke). Verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if n_units != expected.
- arms_differ_verified: true (sha256 over per-arm code matrices; self-test asserts
  all 6 primary-factorial hashes distinct).
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json; per-seed partials
  written atomically for resumability).
- except SystemExit: raise BEFORE except Exception (no bare/BaseException; grep-clean).
- crlb_n/a: "discrete argmax recall; no continuous-estimator noise floor. Capacity
  feasibility handled empirically by the starved positive-control regime, which locates
  the N-transition (recall binds only at N<128 for V=20000; operating N=4096 far above)."
- discriminator_reachability: true (measured D_primary +0.399 >> +0.15 threshold).
- baseline_in_band: true (FULL recall ~0.50-0.56 in (0.05, 0.95)).
- calibration_check: "default_ok_for_this_regime" (synthetic; all params calibrated
  offline; FULL lands mid-band by construction, verified).
- cell_chunked: false. Justification: cheap diagnostic (<~10 min full), and the
  CROSS-SEED aggregate (mean/cv of D, capacity-saturation comparison) IS the load-
  bearing output -- splitting seeds into sibling files would fragment the verdict.
  Durability provided by per-seed atomic partial writes (`_seed_<regime>_<seed>.json`)
  that make the run RESUMABLE after mid-run death (no seed lost).
- start_marker_written: true (_start_marker.json at main entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback).
- heartbeat_present: per-seed + per-sweep-point flushed progress lines (cadence
  <10s/line; no 60s silent gap).
- defensive_error_checking: "passed_all_4_patterns" (start-marker, crash-diag,
  progress heartbeat, resumable partials).
- progress_logging: "print_flush_true" (sys.stdout line-buffered + flush=True on
  every progress line; MANDATORY since timeout_s>=1800).
- baseline_saturation (META_RULE_AG): FULL in band; ORACLE saturates ~1.0 BY DESIGN
  (positive control, not a discriminator arm).

## Gate A-E (composition/sweep gates)
- sweep_alignment_verdict: ALIGNED (each swept param -- N, sigma_e, rho -- is the exact
  parameter its primitive experiences; no partition/routing indirection).
- discriminating_fraction: sigma_e sweep alone spans recall 1.0->0.20 across 8 points;
  >=0.30 of sweep points land in [0.30,0.70] (MEASURED in sensitivity_sweeps).
- composition_edges: none (single-hop sharded item-memory; no primitive->primitive edge).
- positive_control_arms: ORACLE (~1.0) + capacity-saturation starved regime (capacity
  lever fires) -- both verified in smoke.
- functional_requirements: (1) render a concept meaning into an HD code [encoder+quant];
  (2) recall the concept by argmax cleanup over the dictionary [sharded item-memory].
  Both are substrate-native primitives; no new mechanism.

## Compute architecture
Class: (c) mixed / CPU-acceptable. All matmul (encode = x@W then sign; cleanup =
q@codes.T then argmax), fully vectorized (no Python loop over concepts). Per-arm wall
1.9s@N=4096 / 7.1s@N=16384 (V=20000); total full ~5-10 min. GPU-batchable but per-point
<10s and total <15min, so CPU is acceptable; no GPU dependency. Storage strategy:
SHARDED item-memory (each code its own row; argmax cleanup) -- correct default for a
retrieval/capacity cell (no composition, no bundling). Route: remote_cpu_queue.

## Dispatch (exp_dev returns command; ORCHESTRATOR ships -- remote SCP not exp_dev)
`bash tools/orchestrator/queue_add.sh remote_cpu_queue recall_ceiling_capacity_vs_semantic_decomp_v1 experiments/exp_recall_ceiling_capacity_vs_semantic_decomp_v1.py preregs/2026-07-08_recall_ceiling_capacity_vs_semantic_decomp_v1.md 3600`
