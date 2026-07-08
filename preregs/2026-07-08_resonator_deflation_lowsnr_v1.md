# Pre-reg: resonator_deflation_lowsnr_v1 (5x-drill #3: isolate the DEFLATION sub-lever at low SNR)

- anchor_name: resonator_deflation_lowsnr_v1
- script: experiments/exp_resonator_deflation_lowsnr_v1.py
- date: 2026-07-08
- lineage: exp_resonator_theta_gamma_peel_v1 (VET'd MEASURED_MECHANISM) -> drill #3 steer
- prior-work check: substrate_query top hit resonator_factorization_v1 (cosine=0.4316, MIDDLE_BAND,
  the base resonator); hits 2-3 are WordNet dictionary noise. Direct predecessors theta_gamma_peel_v1 /
  ksweep_reachability_v1 are this arc's cells. This drill is a NOVEL extension (isolate deflation
  sub-lever at low SNR), not a rediscovery.

## Question
The theta-gamma slot-peel escape has TWO sub-levers: SLOTTING (re-encode joint product as per-slot
superposition; decode by K sequential 1-way searches) and DEFLATION (subtract each resolved factor
from the residual before the next slot). The peel-cell VET found deflation NON-load-bearing at the
benign-SNR test regime (N=4096, K<=6, SNR ~ sqrt(N/(K-1)) ~ 28: slot_peel == slot_nodeflate == 1.000,
delta 0) because single-shot per-slot unbind already recovers every factor exactly. DRILL #3: does
deflation EARN ITS KEEP at a HARDER (low-SNR) regime, and if so at what SNR/K break-point?

## Design (SNR-sweep via K at fixed small N; PAIRED peel vs nodeflate)
- N = 256, M = 30, K_GRID = [16, 20, 24, 28]
- SNR(correct-codeword score) = signal(N) / crosstalk-std(sqrt((K-1)N/2)) = sqrt(2N/(K-1))
  - K16 -> 5.84 (benign control), K20 -> 5.19 (transition), K24 -> 4.72, K28 -> 4.35 (low-SNR discriminating)
- TR = 200 (full) / 60 (smoke); SEEDS = 8 full [3,7,13,21,42,101,202,303] / 2 smoke [3,7]
- PAIRED: identical books + slots + true tuples across BOTH arms per (seed,K)
- Arms:
  - slot_nodeflate_full : full-tuple exact-match acc, single-shot per-slot unbind, NO deflation (BASELINE)
  - slot_peel_full      : full-tuple exact-match acc, sequential peel-off + deflation (MECHANISM)
  - per-slot + positional diagnostics (deflation should lift LATER decode positions; nodeflate flat)
- HEADLINE: gap(K) = slot_peel_full(K) - slot_nodeflate_full(K); does gap GROW as SNR drops?

## Bands (deflation load-bearing at low SNR)
- HARD_PASS: gap(K24) >= 0.10 AND gap(K28) >= 0.10 AND gap(K28)>gap(K24)>gap(K20) (grows as SNR drops)
  AND gap(K16) < 0.05 (benign control: deflation non-load-bearing at benign SNR -- reproduces VET).
- PARTIAL: gap(K28) >= 0.10 but not clean monotone OR benign control also shows gap(K16) >= 0.05.
- HARD_FAIL: gap(K28) < 0.10 -- deflation NEVER load-bearing; slotting alone suffices (mechanism simplifies).

## Integrity gates
- G1 BENIGN CONTROL: nodeflate_full(K16) >= 0.95 AND gap(K16) < 0.05 (in-run reproduction of
  CITED@exp_resonator_theta_gamma_peel_v1 VET delta-0 benign finding).
- G2 baseline_in_band (META_RULE_AG): 0.05 < nodeflate_full < 0.95 at K24 AND K28 (discriminating cells).
- G3 TELEMETRY-SENSITIVITY (mandatory anti-tautology): metric MOVES under S-perturbation + peel != nodeflate
  at low SNR + accuracy varies across seeds. Asserted in _selftest.
- G4 DEFLATION INVARIANT: one clean deflation step preserves remaining K-1 binding exactly. Asserted in _selftest.

## Calibration (THEORETICAL@sqrt(2N/(K-1)) + calibration sim, 5 seeds TR=200 N=256)
- K16 SNR5.84 nodef=0.989 peel=0.998 gap=+0.009 (benign; deflation non-load-bearing)
- K20 SNR5.19 nodef=0.961 peel=0.995 gap=+0.034 (transition)
- K24 SNR4.72 nodef=0.804 peel=0.967 gap=+0.163 (IN BAND; deflation load-bearing)
- K28 SNR4.35 nodef=0.549 peel=0.900 gap=+0.351 (IN BAND; deflation strongly load-bearing)
- Predicted break-point: gap crosses 0.10 between K20 and K24 (SNR ~4.9-5.0).
- discriminating_fraction (points with nodeflate in [0.05,0.95]): K24,K28 = 2/4 = 0.50 (>= 0.30).
  K16/K20 are INTENTIONAL near-saturated benign/transition controls (AG-exempt, declared).

## SCHEMA-VET fields
- compute_architecture: (b) sequential-CPU with justification. numpy N=256; total wall << 30s;
  below 10s/phase-point batching threshold; peel decode is inherently sequential (slot k depends on
  residual from slot k-1). No torch. -> remote_cpu_queue.
- storage_strategy: no_storage / no_composition (factorization decode; no PartitionedStore writes).
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS)*len(K_GRID) = 8*4 = 32 (full).
- arms_differ_verified: true (peel preds != nodeflate preds at K28; hash-checked pre-verdict).
- arms_differ_exempted: none.
- final_metrics_atomicity: tmp_replace (write_metrics) + per-seed write_partial.
- crlb_floor_computed: SNR = sqrt(2N/(K-1)); per-slot argmax over M=30 -> full-tuple ~ perslot^K.
- crlb_formula_reference: SNR_score = N / sqrt((K-1)*N/2) = sqrt(2N/(K-1)); order-statistic argmax(M).
- discriminator_reachability: true. HP threshold gap>=0.10 reachable (sim gap 0.16 @K24, 0.35 @K28).
- baseline_in_band: true at discriminating cells K24/K28 (0.80, 0.55). K16/K20 declared benign controls.
- discriminator_survives_scale: full-N == smoke-N == 256 (only TR/seeds reduced in smoke).
- discriminator_fires_assertion: gap(K28) >= 0.10 AND gap(K28) > gap(K24) (smoke gate; META_RULE_K).
- calibration_check: default_ok_for_this_regime (SNR closed-form + calibration sim confirm band placement).
- HP_SCOPE: {slot_peel_full: [gap>=0.10 at K24/K28, monotone, benign-K16<0.05]; slot_nodeflate_full: [G1,G2 baseline]}.
- cell_chunked: false (single-cell multi-seed; wall << 1min; not a zombie-risk long cell).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: true.
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (+ heartbeat per unit).
- effective_vs_nominal_parameter_audit: swept K directly controls SNR each slot-unbind experiences
  (crosstalk = K-1 interferers); sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: discriminating_fraction 0.50 (K24,K28 in [0.05,0.95]); >= 0.30 OK.
- signal_shape_compatibility_audit: single primitive (slot unbind+cleanup); no cross-primitive edges. N/A.
- positive_control_arms: benign control K16 reproduces deflation-non-load-bearing (Gate D analog, in-run).
- functional_requirements: (1) recover K-way binding at low SNR -> per-slot unbind+cleanup; (2) isolate
  deflation contribution -> paired peel vs nodeflate on identical draws.

## Dispatch
- queue: remote_cpu_queue (numpy CPU cell; no torch; small-N passes routing-sanity gate).
- timeout_s: 600 (generous; measured smoke wall is seconds).
