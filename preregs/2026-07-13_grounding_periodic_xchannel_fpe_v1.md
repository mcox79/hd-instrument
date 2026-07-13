# Pre-reg: Periodic-table cross-channel grounding (Track-B build #1) -- grounding_periodic_xchannel_fpe_v1

Date: 2026-07-13
Author: exp_dev
Plan: notes/research_grounding_foundation_build_plan_2026-07-13.md (Phase 1, "Cheap decisive test")
Decision-level design: notes/grounding_anchor_design_first_testbed_2026-07-10.md
Cell: experiments/exp_grounding_periodic_xchannel_fpe_v1.py

## Question
Can a genuinely MEASURED, non-LLM numeric channel (Channel B) be VSA-wired into the
existing bind/bundle algebra (Channel A = the substrate-native KGStore relational
store) and produce a MEASURABLE inference gain over the pure-symbol baseline?

## Channels
- Channel A (relational, native): element -> (HAS_GROUP g, HAS_PERIOD p, HAS_BLOCK b),
  ingested into a REAL hdlab.kg_traversal.KGStore; element relational signatures built
  from the store's own bipolar E/R codebooks (bind = elementwise multiply, bundle = sum).
- Channel B (measured, exterior): atomic mass, electronegativity (Pauling), atomic radius,
  first ionization energy, melting point. CITED@CRC-Handbook/IUPAC standard reference data,
  periods 1-5 (H..Xe, 54 elements), NaN-masked where no standard Pauling EN (He/Ne/Ar).

## Encoding (the VSA wiring)
- FPE (FHRR): enc_k(v) = exp(1j * freqs_k * v), Gaussian base freqs, per property k.
  THEORETICAL@ cos-sim(enc(v1),enc(v2)) = mean_d cos(freqs*(v1-v2)) = exp(-s^2 dv^2/2).
  Bandwidth: freq_std s = 2.15 chosen so kernel decays 1.0 (dv=0) -> ~0.1 (dv=1) across the
  normalized [0,1] value range: exp(-s^2/2)=exp(-2.31)=0.099. calibration_check =
  default_ok_for_this_regime (analytically-set, not swept-for-pass).
- LEVEL (fallback, arXiv:2412.00488 robustness): spherical interpolation
  normalize(cos(t)*v_lo + sin(t)*v_hi), t=v*pi/2; cos-sim = cos((v1-v2)*pi/2), monotone.
- Both encodings SMOKED side by side (arms A_PLUS_B_FPE, A_PLUS_B_LEVEL).
- CLEANUP: CSim-style resonator (iterative interference subtraction) decoder, a first-class
  diagnostic arm alongside RAW single-unbind decode.

## Oracle + readout
Periodic law. Leave-one-out kNN in the consolidated geometry: predict a held-out element's
raw property value from a similarity-weighted average of all OTHER elements' true values
(no self, no leakage; the held-out target property is EXCLUDED from Channel B's bundle).
Skill = R^2 vs the mean baseline, averaged over the 5 target properties.

## Arms (7)
- MEAN: global-mean predictor (skill == 0 by construction).
- DEGREE: query-agnostic degree-weighted predictor (relational popularity floor).
- RANDOM: random-hypervector similarity (must-fail floor).
- A_ALONE: relational similarity only (Channel A; lam=0). THE ablation baseline.
- A_PLUS_B_FPE: relational fused with FPE attribute similarity (lam=1). HEADLINE.
- A_PLUS_B_LEVEL: relational fused with level-code attribute similarity.
- POSITIVE_ORACLE: kNN on RAW normalized other-features (grounding-is-winnable ceiling).

## Compute architecture
Class (b) sequential-CPU with justification: 54-element domain, all ops are 54x54 similarity
matrices + a 257-point decode grid; total wall << 10s even at n_dim=8192 x 5 seeds. No GPU
benefit (matmuls are tiny). Routes to remote_cpu_queue (CPU-native, torch). Storage strategy:
no_composition (single-hop kNN readout, not chained retrieval); sharded default N/A.

## Multi-seed + stratification
- FULL: n_dim=8192, seeds=[7,13,19,23,29]. Self-test: n_dim=2048, seeds=[7,13].
- Randomness (seed): FPE base freqs, level endpoints, roles, KGStore E/R codes, RANDOM arm.
  The periodic DATA + the leave-one-out split are DETERMINISTIC (no random split -> no
  PYTHONHASHSEED split-identity hazard).
- Difficulty strata: boundary = groups {1,2,17,18} or period 1 (table edges); interior = else.
  Reported per stratum (degree/boundary invariance).

## Pre-registered bands
HARD_PASS (ALL required; strictly above floor per META_RULE_L):
1. A_PLUS_B_FPE skill - A_ALONE skill >= 0.05 (Channel B load-bearing)
2. A_PLUS_B_FPE skill - RANDOM skill >= 0.10 AND A_PLUS_B_FPE > MEAN (== 0)
3. fpe_decay_spearman >= 0.90 (encoding does real metric work)
4. boundary_fpe >= interior_fpe - 0.15 AND boundary_fpe > 0 (degree/boundary invariant)
5. cleanup decode median rel-err <= 0.20 (numeric info recoverable after bundle size 5)

HARD_FAIL variants (classified separately; do NOT conflate):
- ENCODING_BROKEN: fpe_decay_spearman < 0.50 (wiring broken, not a grounding result)
- GROUNDING_NEGATIVE: A_ALONE ties/beats A_PLUS_B_FPE (numeric channel not exogenous)
- ORACLE_LEAK_VIA_SMOOTHNESS: interior_fpe > 0 but boundary_fpe <= 0
- DECODE reporting (independent of grounding verdict): raw decode median rel-err > 0.50 at
  bundle size 5 => DECODE_DEGRADATION; if cleanup rel-err <= 0.20 => cleanup recovers
  (report "DECODE_DEGRADATION_NEEDS_CLEANUP", NOT a grounding failure).

MIDDLE_BAND: no HARD_FAIL class fired but not all HARD_PASS gates cleared.

HP_SCOPE:
- A_PLUS_B_FPE: [b_beats_a, b_beats_floor, encoding_ok, degree_invariant, cleanup_fixes]
- A_ALONE: baseline only (no HP gates; must be above RANDOM floor per F.4).
- MEAN/DEGREE/RANDOM: floor arms (no HP gates).
- POSITIVE_ORACLE: positive control (must beat A_ALONE by >= 0.05 at self-test).

## SCHEMA-VET gate fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds * sum_t (n elements with property t known).
- effective_vs_nominal: no swept confounded param (lam ablation is 0 vs 1; both experienced fully).
- sweep_alignment_verdict: ALIGNED (ablation, not a nominal/effective sweep).
- discriminating_fraction: N/A (ablation cell, not a bracket sweep); A_ALONE pre-verified in band.
- composition_edges: relational-sig (bind/bundle) -> cosine sim; FPE (bind role, bundle) -> cosine
  sim; fusion = additive at similarity/readout level. verdict: SHAPE_MATCH (all cosine-space).
- positive_control_arms: POSITIVE_ORACLE (raw-feature kNN) must beat A_ALONE -> proves the
  B-beats-A bar is winnable at the test regime.
- functional_requirements: (1) encode a measured scalar as a composable hypervector -> FPE/level;
  (2) fuse with native relational algebra -> KGStore E/R bind/bundle + additive sim fusion;
  (3) infer a held-out measured value -> LOO kNN oracle; (4) recover the scalar after bundling
  -> resonator cleanup decoder.
- real_code_path_exercised: [KGStore, ingest_triples] (self-test constructs + ingests REAL store).
- substrate_signature_checked: [KGStore] with BASE/portable kwargs {n_ent,n_rel,n_dim,generator};
  NO version-specific init_entities (F.3 drift discipline).
- guard_baseline_validated: [B_BEATS_A_needs_nonfloor_A] (A_ALONE validated above RANDOM floor).
- baseline_in_band: A_ALONE checked 0.05 < skill < 0.95 at self-test (META_RULE_AG).
- crlb_n/a: "regression-skill (R^2) cell; no argmax capacity / Cramer-Rao noise floor applies."
- arms_differ_verified: true (per-arm concatenated prediction hashes; META_RULE_AF).
- final_metrics_atomicity: tmp_replace (META_RULE_AH).
- cell_chunked: false (single-file multi-seed; 5 seeds x seconds each, runner-death risk minimal).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: false
  (per-seed [progress] print_flush lines; total wall << 60s so a jsonl heartbeat is unnecessary).
- defensive_error_checking: "print_flush per-seed progress + start-marker + crash-diagnostic;
  heartbeat exempt (sub-minute wall)".
- progress_logging: print_flush_true.
- calibration_check: default_ok_for_this_regime (freq_std analytically set; see Encoding).

## Validity-preflight (VALIDITY_PREFLIGHT_MODE=enforce)
F.1 real_code_path, F.2/F.3 substrate_signature, F.4 guard_baseline_valid (ENFORCE) + the
original 4 (positive_control, metric_moves, full_gates_exercised, negative_control_margin) all
DECLARED and exercised in the self-test. Discriminator-fires asserts A+B_FPE - A_alone >=
0.03 at self-test scale (honest abort if the numeric channel is not load-bearing).

## Scope / honest deflation
Proves the GROUNDING MECHANISM in a small clean domain with a lawful oracle; transfer to the
messy 222k-triple KB is a separate later step (do not conflate). This is passive-exterior
(ingested measurements, layer-2), not active-intervention (layer-3) grounding. Channel A and B
are correlated (group-neighbors share properties); the claim is B is NOT DERIVABLE from A, and
the ablation is the operational test. P_deflated(HARD_PASS with cleanup/level fallback) = 0.45
(CITED@ plan Section per-phase deflation; naive FPE decode degrades after ~2 bundling steps).
