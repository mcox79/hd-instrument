# Pre-reg: exp_resonator_theta_gamma_peel_v1 (5x-drill #2, resonator K5/K6 wall)

Filed by: exp_dev | 2026-07-08 | cell: experiments/exp_resonator_theta_gamma_peel_v1.py

## Prior-work check
substrate_query "theta gamma sequential re-encoding phase slot peel deflation resonator factorization":
top hit `resonator_factorization_v1` cosine=0.3994 (MIDDLE_BAND, the vanilla multiplicative resonator),
then `deflation`/`reflation` (wordnet, not substrate), and `research_drill_integration_complete_3x`
(resonator-for-drive-selection, different task). NONE at cosine>0.30 is a theta-gamma SLOT re-encoding
of the resonator's factor-COUNT axis with peel-off deflation. Grep of experiments/: theta-gamma cells
exist only in COMPOSITION/LM contexts (`substrate_theta_gamma_nested_oscillation_LM_v1` HARD_FAIL +
brain-compensated variant); resonator cells never use phase-slotting. Candidate #2 in
notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md was flagged as "a bigger
re-encoding redesign, NOT built." Confirmed GENUINELY NOVEL adjacency (not a rediscovery).

## Mechanism under test
The K5/K6 wall is a REACHABILITY / convergence-dynamics wall (skunkworks-confirmed), NOT crosstalk-
capacity. Drill #1 (DG dimensional-expansion) HARD_FAILed -> crosstalk/N-expansion/DG-frontend levers
and larger restart-budget R are PROVEN DEAD. Escape (candidate #2, structurally-faithful): re-encode
the K role/filler bindings as a THETA-GAMMA SLOT SUPERPOSITION `s = sum_k r_k (*) x_k` (each item in its
own phase slot) and decode by K sequential 1-way unbind+cleanup with PEEL-OFF DEFLATION, instead of one
K-way joint multiplicative factorization. Converts M^K joint search -> K*M sequential searches. Changes
SEARCH DYNAMICS, not capacity.

## Arms (PAIRED: identical codebooks + true tuples across arms)
- `vanilla_oracle_any` : P(true tuple present among R=10 restart candidates), joint resonator, T0=0.50.
  Reachability CEILING (verifier-generous). Reproduces the wall in-run (positive control).
- `vanilla_verifier`   : R=10 verifier-selected exact-match accuracy (what vanilla ACHIEVES).
- `slot_nodeflate_acc` : slot superposition, per-slot single-shot unbind, NO deflation (ablation).
- `slot_peel_acc`      : slot superposition, single-shot sequential peel-off + deflation (THE ESCAPE, HEADLINE).
Comparison HANDICAPS the escape: slot_peel = 1 deterministic shot, no verifier; vanilla_oracle = R=10 + perfect oracle.

## Config
N=4096, M=30, MAXIT=60, R=10, T0_vanilla=0.50, K_GRID=[3,4,5,6], TR=120 full / 30 smoke,
SEEDS=[3,7,13] full / [3] smoke. EXPECTED_N_UNITS = seeds*K = 12 full / 4 smoke (cardinality_ok gate).

## Bands (pre-registered BEFORE full; no-smoke honest tiering)
- HARD-PASS: slot_peel_acc(K5) >= 0.30 AND slot_peel_acc(K6) >= 0.30 AND vanilla_oracle_any(K5) < 0.10.
- PARTIAL  : slot_peel_acc(K5) >= 0.30 AND slot_peel_acc(K6) < 0.30 (K5 rescued, K6 not).
- HARD-FAIL: slot_peel_acc(K5) < 0.30 (no rescue) -- honest negative (slotting does not deliver K-way capability here).
Integrity gates precede classification:
- G1 POSITIVE CONTROL (Gate D): vanilla reproduces wall at test regime -- K3 oracle in [0.95,1.00]
  (ref 0.992), K4 in [0.72,0.90] (ref 0.806), K5 < 0.10 (ref 0.000).
  MEASURED@data/exp_resonator_ksweep_reachability_v1/metrics.json. Fail -> HARD_FAIL (comparison void).
- G2 EXPANSION-INDEPENDENCE: slot N == vanilla N == 4096 (no r*N). Asserted in _selftest.
- G3 PEEL-OPERATOR: deflation preserves remaining K-1 binding exactly. Asserted in _selftest.

## baseline_in_band (META_RULE_AG) -- EXEMPTED
vanilla_oracle_any(K5)=(K6)=0 is the CONFIRMED firing failure under study (the paired baseline), NOT a
too-easy/saturation artifact. Vanilla is in-band at low K (K3~0.99, K4~0.81) proving a real K-gradient.
Discriminator = gap slot_peel - vanilla, maximal exactly when vanilla=0. Exemption rationale documented.

## Fairness caveat (pre-registered; do NOT over-claim)
The escape does NOT make the vanilla joint resonator converge at K5 -- it SIDESTEPS via re-encoding. The
finding is "the downstream CAPABILITY (K-way conjunctive binding + full recovery) is deliverable via
theta-gamma slot re-encoding where joint factorization is non-convergent," at the cost of additive slot
capacity (benign at K<=6/N=4096: SNR ~ sqrt(N/(K-1)) ~ 28). Deflation's marginal value is separately
UNPROVEN at this regime (slot_nodeflate also succeeds); stressing deflation (higher K / lower N) is drill #3.

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS gate in main)
- arms_differ_verified: true (slot_peel winners != vanilla winners at K5; META_RULE_AF)
- final_metrics_atomicity: tmp_replace (write_metrics + per-seed partials)
- discriminator_reachability: true (HP floor 0.30 reachable; escape lift measured)
- discriminator survives scale: smoke at FULL N=4096/M=30/K-grid (only TR+seeds reduced)
- positive_control_arms: vanilla K3/K4/K5 reproduce reachability refs at TEST regime (Gate D)
- crlb_n/a: "no quantitative CRLB threshold; escape gate is a paired accuracy-lift vs a firing failure"
- calibration_check: default_ok_for_this_regime (VERBATIM vanilla decode_trial port; seeds reused from reachability)
- paired_trials: true (identical codebooks + true tuples across all arms)
- cell_chunked: false (single-cell multi-seed; per-seed partials via _seed_checkpoint; runtime < 30min)
- start_marker_written: true ; crash_diagnostic_present: true ; heartbeat_present: true
- defensive_error_checking: passed_all_4_patterns
- progress_logging: print_flush_true (+ per-unit heartbeat) ; timeout_s < 1800 target
- Compute architecture: sequential-CPU justified -- VERBATIM numpy port of the CPU reachability
  instrument for paired comparability; vanilla decode already batched over R restarts; single T0 keeps
  wall-time modest; slot arm O(K) cheap matmuls. no_storage / no atoms.jsonl writes.

## SMOKE RESULT (MEASURED@data/exp_resonator_theta_gamma_peel_v1_smoke/metrics.json, seed 3, TR=30, full N)
verdict=HARD_PASS (ESCAPE_CONFIRMED). K3 van_orc=1.000 K4 van_orc=0.800 K5=0.000 K6=0.000 (wall reproduced);
slot_peel K3..K6 = 1.000/1.000/1.000/1.000 ; slot_nodeflate identical. escape lift(K5)=1.000 >= 0.30;
discriminator fired. Runtime 1m42s / seed -> full (3 seeds, TR=120) ~ 20min; timeout 2400s with margin.

## Dispatch
FULL -> remote_cpu_queue (numpy-CPU cell). timeout_s=2400.
