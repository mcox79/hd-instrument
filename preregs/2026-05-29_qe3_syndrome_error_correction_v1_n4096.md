# Pre-registration: qe3_syndrome_error_correction_v1_n4096

Date: 2026-05-29
Anchor: `qe3_syndrome_error_correction_v1_n4096`
Script: `experiments/exp_qe3_syndrome_error_correction_v1_n4096.py`
Queue: `overnight_queue` (GPU)
Timeout: 14400 s (PROT-019 floor for `_n4096`)
Parent: `kf2_isolation_proof_v2_n4096_audit`

## Scientific question

Quantum-error-correction analog: does Kerdock parity-check active correction
(syndrome measurement + masked re-retrieval on violation) reduce operational
error rate at borderline / over-capacity M_frac vs single-pass baseline retrieval?

## Configuration (FULL)

- N = 4096 (PROT-018 binding via `_n4096` suffix)
- Codebook: Kerdock 4-coset, C = 4*N = 16384 (parity-check structure leveraged)
- M_frac = 4.0 (borderline / over-capacity regime where errors are non-trivial)
- n_probes = 500 stored-key probes per cell
- Syndrome threshold = 0.95 (inner-product agreement on normalized codeword)
- Modes: baseline (single-pass argmax) and corrected (syndrome + masked re-retrieve)
- Seeds: [7, 17, 23] (3 seeds per spec)
- Total cells: 2 modes x 3 seeds = 6 cells

## Pre-registered envelope-fail-bands

Definitions: per-seed `delta_err = error_rate(baseline) - error_rate(corrected)`
(positive = correction helps).

- HARD_PASS: `delta_err >= 0.50` absolute on `>= 2/3` seeds.
- MIDDLE_BAND: `delta_err in [0.10, 0.50)` on `>= 2/3` seeds.
- HARD_FAIL: `delta_err < 0.10` on `>= 2/3` seeds.

## Formula self-tests (executed at import time)

1. C = 4 * N at N=4096 = 16384.
2. error rate identity: err = 1 - accuracy.
3. Verdict gates: HARD_PASS / HARD_FAIL / MIDDLE_BAND with synthetic per-seed cells.
4. Smoke baseline cell at N=1024 produces valid accuracy in [0, 1].
5. Smoke corrected cell at N=1024 produces valid accuracy + n_violations counter.
6. OOM pre-check: 4096^2 * 4 bytes < 6 GB.

## Timeout justification

- Parent kf2 v2_n4096_audit elapsed ~30 s for 25 cells.
- We run 6 cells with parity check + masked re-retrieve (~5 s/cell); ~30 s nominal.
- Safety 10x for codebook reuse + GPU cold-start + violation re-argmax: 300 s.
- PROT-019 floor for `_n4096` = 14400 s. We use the floor.

## Strategic disposition on each outcome

- HARD_PASS: Kerdock parity-check active correction is a new product feature
  (syndrome-driven self-healing retrieval) for the auditable memory layer.
- MIDDLE_BAND: characterize; consider as adjunct to deletion-cert + drift detection
  killer-features (not standalone product yet).
- HARD_FAIL: parity-check approach does not unlock product-grade error reduction;
  close the QEC-analog row in cap_map with negative result.
