# Pre-reg: exp_resonator_ksweep_reachability_v1

Author: hdi_exp_dev | Date: 2026-07-07 | Anchor: resonator_ksweep_reachability_v1

## Question
Follow-on to exp_resonator_verifier_readout_v1 (HARD_PASS) + notes/research_resonator_reachability_ceiling_2026-07-07.md.
At K=4 the resonator answer-reachability ceiling (oracle_any=0.806 at best T0) was shown to be a
RESTART-BUDGET problem, not a basin-measure wall: per-restart true-basin probability p_basin ~ 0.151
(backed out from oracle_any = 1-(1-p_basin)^R at R=10), so oracle_any->0.95 is reachable at ~R=19.
OPEN: does p_basin COLLAPSE at higher K (K5, K6) due to a fundamental basin-proliferation /
clustering-condensation / overlap-gap-property wall (the 4th-family recurrent-search mechanism that
falsified the CG_META self-margin law), or does it decline roughly geometrically (still a compute dial)?
This cell MEASURES the p_basin(K) trajectory K3->K4->K5->K6 to discriminate a fundamental WALL from a
compute BUDGET dial.

## Lever (ONLY K changes)
Glauber-dither + R=10 restart + verifier-readout decode HELD IDENTICAL to verifier_readout_v1
(decode_trial verbatim port; K is already a parameter). ONLY K_GRID changes: [3,4,5,6]. K3/K4 are
positive-control reproducers of the known oracle_any; K5/K6 are the new probe. N=4096, M=30, MAXIT=60,
R=10, full T0 sweep [0.0,0.10,0.20,0.35,0.50] all retained for comparability. Verifier read-out kept so
oracle_any (reachability) is measured cleanly, separated from aggregation loss.

## Measured per K (at best T0 by oracle_any)
- oracle_any (reachability ceiling at fixed R=10)
- p_basin = 1 - (1-oracle_any)^(1/R)  (per-restart true-basin probability)
- R_to_95: smallest R' with 1-(1-p_basin)^R' >= 0.95 (compute cost to lift reachability to 0.95)
HEADLINE: the p_basin(K) trajectory K3(~0.383)->K4(~0.151 known)->K5->K6.

## Bands (pre-registered BEFORE full; discriminator = p_basin at K6, research Prediction B)
- BUDGET (HARD-PASS): p_basin(K6) >= 0.05. Restarts still work; R_to_95(K6) modest (~R=60 lifts to 0.95);
  decline roughly geometric. No fundamental K-dependent wall through K6. Capability-positive: reachability
  is a compute dial.
- WALL (HARD-FAIL): p_basin(K6) < 0.01 (basin measure cratering toward clustering/condensation; no
  realistic R rescues) OR oracle_any(K6) < 0.10 despite R=10. CONFIRMS the CG_META-style
  basin-proliferation algorithmic wall at K*<=6. Honest negative; report faithfully, do not force a budget read.
- MIDDLE (MIDDLE_BAND): 0.01 <= p_basin(K6) < 0.05. Declining hard (super-geometric onset) but not fully
  collapsed; wall emerging, ambiguous; needs K7+ or higher R to localize K*.
- Geometric extrapolation of the KNOWN K3->K4 ratio predicts p_basin(K6)~0.024 = MIDDLE midpoint, so the
  bands BRACKET the null geometric-decline hypothesis on both sides.

## Positive control (Gate D -- reproduce prior chain-grade result AT TEST REGIME)
K3 best-T0 oracle_any in [0.95,1.00] (ref 0.992) AND K4 best-T0 oracle_any in [0.72,0.90] (ref 0.806).
Both MEASURED@data/exp_resonator_verifier_readout_v1/metrics.json (recomputed 2026-07-07:
K3=0.9917@T0=0.5, K4=0.8056@T0=0.5 -- match). If either reproducer falls outside tolerance the numpy port
diverged -> K5/K6 trajectory UNTRUSTED -> HARD_FAIL_POSITIVE_CONTROL.

## Integrity invariant (HARD_FAIL override)
verifier harvest <= oracle_any per arm (verifier can only pick from the R candidates it was given). Any
violation => reconstruction read-out bug => HARD_FAIL_INVARIANT.

## Formula self-test (PASS -- 7 checks)
phasor unit modulus; verifier true-tuple=1.0 / wrong-tuple<0.2 / argmax recovers truth when present;
p_basin(K4=0.806)=0.1512 & R_to_95=19; p_basin(K3=0.992)=0.3830 & R_to_95=7; oracle round-trip inverts p;
edge cases p=0/p=1; monotonicity (lower oracle -> lower p_basin -> larger R_to_95); K=1 decode recovers truth.

## Compute architecture
Class: (b) sequential-CPU with justification. decode_trial has genuine sequential dependency (coupled
alternating-projection, step it depends on it-1); it IS the mechanism under test (bit-faithful numpy port
of the GPU resonator). Inner cost ~ K^2 per MAXIT step. Relative to the K4-only parent (K in {3,4},
sum K^2=25), this cell (K in {3,4,5,6}, sum K^2=86) is ~3.4x heavier on glauber arms. Parent full wall
~1215s -> this full ~4200-4500s expected. Storage: no_storage (decode-only). No batching gain (sequential
recurrence; already R-batched inside decode_trial).

## SCHEMA-VET fields
- arms_differ_verified: true (META_RULE_AF; verifier winners != plurality winners on K4 T0=0.20; asserted
  in main() before verdict -- RuntimeError if bit-identical).
- final_metrics_atomicity: tmp_replace (write_metrics) + per-seed write_partial; resumable_seeds resume.
- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 4 K x 5 T0 = 60 glauber arms; verdict raises
  HARD_FAIL_CARDINALITY_META_RULE_H if len(per_seed) != 3 OR any seed lacks all 20 verifier arms.
- crlb_floor_computed / discriminator_reachability: bands bracket the geometric null (p_basin(K6)~0.024
  predicted); both WALL (<0.01) and BUDGET (>=0.05) outcomes are physically reachable. reachable = true.
- baseline_in_band / positive_control_arms: K3 oracle in [0.95,1.00], K4 in [0.72,0.90] (Gate D);
  deterministic single-shot baseline arm (T0=0, R=1) per K.
- discriminator survives scale: SMOKE runs at FULL N=4096 M=30 MAXIT=60 R=10 over the FULL K sweep
  [3,4,5,6] (only TR 120->30 and seeds ->[3] reduced). Reachability physics (basin measure) is the SAME at
  scale; discriminator = K-axis oracle_any spread >= 0.10 AND oracle_any(K6) < oracle_any(K3).
- HP_SCOPE: {p_basin_K6: [BUDGET_0.05, WALL_0.01, ORACLE_CRATER_0.10]}.
- calibration_check: default_ok_for_this_regime (reconstruction verifier is parameter-free argmax).
- functional_requirements: "measure per-restart basin probability across K" -> p_basin backout from
  oracle_any; no existing primitive maps to this.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true (_write_start_marker,
  _write_crash_metrics via except Exception with SystemExit/KeyboardInterrupt re-raised FIRST, _heartbeat).
- progress_logging: print_flush_true (+ per-arm heartbeat jsonl). Full wall < 1800s per seed segment but
  heartbeat+flush present regardless.
- cell_chunked: false (3-seed loop with per-seed write_partial + resumable_seeds checkpoint/resume).
- PAIRED trials: identical codebooks + true tuples across all arms within a seed (rng seeded by seed*100+K
  for books, seed*1000+K for trues).

## Smoke result (fresh, 2026-07-08; seed 3, TR=30, FULL N=4096 M=30 MAXIT=60 R=10, full K sweep [3,4,5,6])
Wall = 735.4 s. ALL GATES PASS:
- discriminator FIRED: K-axis oracle_any spread = 1.000 (need >= 0.10), declines = True.
- positive control (Gate D) REPRODUCED: K3 oracle_any = 1.000 in [0.95,1.00] (ref 0.992);
  K4 oracle_any = 0.867 in [0.72,0.90] (ref 0.806). numpy port matches GPU reference.
- integrity invariant: 0 verifier_le_oracle violations. arms_differ = True (verifier != plurality).
- trajectory: K3(orc=1.000,p_basin=1.000,R95=1) -> K4(0.867,0.1825,15) -> K5(0.000,0.000,inf) -> K6(0.000,0.000,inf).
Smoke's own verdict = HARD_FAIL WALL_FUNDAMENTAL (p_basin(K6)=0.000 < 0.01): this is the PRE-REGISTERED
WALL science outcome measured at full N (K5/K6 reachability craters to 0/30 hits, exactly as scoped), NOT a
smoke-gate failure. The full run confirms across seeds [3,7,13] at TR=120 with per-seed statistics.

## Dispatch
FULL -> remote_cpu_queue (CPU/numpy decode-only; no torch, small N=4096 -> no routing-gate rejection).
Seeds [3,7,13] (reuse VET seeds -> directly comparable). --allow-duplicate (nothing ran; prior partials cleared).
timeout: 14400 s (full est ~8825 s = 12x smoke wall for 4x TR x 3x seeds; 1.6x headroom -> capped at 14400).
