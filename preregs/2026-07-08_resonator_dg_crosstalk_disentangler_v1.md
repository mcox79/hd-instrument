# Pre-reg: exp_resonator_dg_crosstalk_disentangler_v1

Author: hdi_exp_dev | Date: 2026-07-08 | Anchor: resonator_dg_crosstalk_disentangler_v1

## Question
CPU pre-check GATE (research note (c) secondary checks #1+#2) for the DG-front-end escape from the
skunkworks-confirmed K5/K6 resonator wall. Disentangle the two candidate readings of the wall BEFORE
any GPU spend: is the K5/K6 crater a CROSSTALK/SNR capacity cliff (Tsodyks-Feigelman; MOVES with N,
escapable by dimensional expansion) or a basin-COUNT proliferation (not obviously escapable by
expansion)? And does the DG mechanism port to complex FHRR at all?

## Levers / arms (paired true tuples within each K,seed)
- dense_N4096  : dense unit-phasor codebooks at N=4096 (baseline, the confirmed-negative regime)
- dense_Nexp   : dense unit-phasor codebooks at N=16384 (r=4 expansion; mechanistically-supported lever)
- sparse_Nexp  : DG-analog sparse-phasor codebooks at N=16384, top-2% by |z|, unit-phase survivors
                 (the RISKY sparsify lever)

## Measured (ORACLE unbind -- basin dynamics REMOVED, only codebook crosstalk remains)
For each true tuple: unbind factor 0 with the TRUE other factors, score all M codewords of factor 0.
- crosstalk_std_mean : std of the wrong-codeword scores (the Tsodyks-Feigelman crosstalk term)
- margin_mean        : true-score minus best-wrong-score (SNR headroom)
- oracle_recover_rate: fraction where the true codeword is the argmax
CHECK B (decorr port): correlated complex pair (input_cos ~ 0.8) -> expand+sparsify -> code_cos; gap.

## Bands (diagnostic gate; crlb_n/a -- the measured numbers ARE the deliverable)
- GATE_CLEAR_EXPANSION: crosstalk_std(dense_N4096)/crosstalk_std(dense_Nexp) >= 1.30 AND
  margin(dense_Nexp) > margin(dense_N4096). => expansion is a real SNR lever; PROCEED to escape smoke.
- GATE_DENY: expansion ratio < 1.30 OR margin not raised. => expansion unlikely to rescue; do NOT
  spend GPU.
- sparsify sub-state: VIABLE (margin >= 0.30) | MARGINAL | COLLAPSE (margin < 0.10; sparsify kills the
  K-way multiplicative binding support -> sparsify arm of the escape is expected-to-crater).
- decorr port: gap >= 0.15 => DG separation ports to complex FHRR.

## Formula self-test (PASS)
dense phasor unit modulus; sparse rate in [0.01,0.03]; oracle unbind recovers factor-0 truth (dense,
large margin); crosstalk_std falls with N and the 4x-N ratio is ~sqrt(4)=2 (THEORETICAL 1/sqrt(N)).

## Compute architecture
Class: (b) sequential-CPU with justification. Pure numpy diagnostic (oracle unbind = M x d matmul per
trial; no basin iteration). Wall < 60s at N_TRIALS=200 x 6 configs x 3 arms. No GPU needed by design
(this cell EXISTS to avoid GPU spend). Storage: no_storage.

## SCHEMA-VET fields
- arms_differ_verified: true (three arms' aggregate crosstalk-std signatures must be distinct;
  HARD_FAIL META_RULE_AF otherwise).
- final_metrics_atomicity: tmp_replace (write_metrics) + _write_crash_metrics.
- crlb_n/a: "diagnostic disentangler -- measures crosstalk std directly; no HP threshold on a substrate
  capability."
- discriminator: expansion must MOVE crosstalk_std across the N axis (ratio gate), else vacuous.
- calibration_check: default_ok_for_this_regime (oracle unbind is parameter-free).
- functional_requirements: "separate crosstalk-variance from basin-count as the wall mechanism" ->
  oracle-unbind isolates crosstalk (no basin dynamics); no prior primitive maps.
- crash_diagnostic_present: true (except Exception with SystemExit/KeyboardInterrupt re-raised first).
- progress_logging: print_flush_true (short cell).
- PAIRED: identical true tuples across the three arms within each (K, seed).

## Result (LANDED 2026-07-08, FULL, CPU; MEASURED@data/exp_resonator_dg_crosstalk_disentangler_v1/metrics.json)
Verdict = GATE_CLEAR_EXPANSION. Aggregated over K in {4,5}, seeds {3,7,13}, 200 trials:
- crosstalk_std: dense_N4096=0.0106 -> dense_Nexp=0.0054 (ratio 1.96x ~ sqrt(4)); sparse_Nexp=0.0002.
- oracle_margin: dense_N4096=0.977 -> dense_Nexp=0.989 (raised); sparse_Nexp=0.002 (COLLAPSE).
- oracle_recover_rate: dense arms 1.00; sparse arm ~0.00.
- decorr port: input_cos->code_cos gap=0.272 >= 0.15 (DG separation PORTS to complex FHRR).
Reading: expansion is a REAL crosstalk-SNR lever (Tsodyks-Feigelman CONFIRMED, 1/sqrt(N) scaling).
The naive top-2% sparsify COLLAPSES the K-way binding support (informative negative on the risky
lever) -> the escape cell's rescue rides on expansion-ALONE; sparsify kept only as an
in-pipeline informative-crater ablation.

## Dispatch
Ran LOCALLY as the pre-check gate (CPU, < 60s). No queue dispatch needed. Gate result feeds
exp_resonator_dg_frontend_ksweep_v1 (which is GPU).
