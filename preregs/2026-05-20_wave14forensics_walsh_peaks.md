# Pre-registration: wave14forensics_walsh_peaks

Date: 2026-05-20
Status: Pre-registered, gated. Direct follow-up to XRD2_STRUCTURED_WINS_CLEAR.

## Why

wave14xrd_structured_keys validated: with Hadamard keys, W's WHT is a clean
diffraction pattern (SNR=10^7). This experiment asks the OPERATIONAL question:
can we identify WHICH Hadamard rows were used as keys, just by reading the
WHT peak locations?

This operationalizes substrate forensics. If yes -> capability:
  "Read out which keys were stored without queries"
  -> security implication (adversary reads stored keys from W alone)
  -> capability (memory dump primitive)

## Hypothesis

At K <= 200 (well below alpha_c*N=627): WHT peak identification recovers
>=95% of stored Hadamard key indices.
At K >= 1500: recovery degrades to <50% (peaks overlap, can't separate).

## Operational

N=4096. Hadamard codebook of N rows. Sweep K in {30, 100, 300, 627, 1000,
1500, 2000, 3000, 3500}. Per K: 5 seeds. For each, store K random Hadamard
rows as keys + random ±1 values. Compute WHT of W. Top-K column powers ->
predicted stored key indices. Recall = correct fraction.

## Cited mechanism

- Sylvester Hadamard matrix
- Walsh-Hadamard transform on Z_2^N Cayley graph
- Crystallography research agent (this session): WHT of W is the substrate
  diffraction pattern; Hadamard keys = crystalline; produce exact Bragg peaks

## Expected runtime

Smoke: ~3 sec
Full: ~5 min (FWHT N^2 = 4096*4096 log N ~ 2e8 ops per matrix; 9 K * 5 seeds
= 45 matrices)

## Verdict labels

- `PEAKS_FORENSICS_VALIDATED`: high recall at low K, low at high K
- `PEAKS_FORENSICS_LIMITED`: works at low K, high K untested
- `PEAKS_NO_FORENSICS`: fails even at low K (WHT doesn't separate stored keys)
- `PEAKS_PARTIAL`: somewhere in between
- `PEAKS_INCONCLUSIVE`: empty data

## What this enables

VALIDATED: substrate forensics capability operationalized. New row in cap_map:
"Read stored Hadamard keys from W alone via WHT". This is unique - no other
memory architecture (vector DB, KV cache, MLP weights) lets you do this.
