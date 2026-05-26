# Pre-registration: wave14forensics_svd_recovery

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14forensics_svd_recovery.py](../experiments/exp_wave14forensics_svd_recovery.py)

## Why

Crystallography research agent finding (this session): at K < N/(2 log N) ~
170 for N=4096, SVD + sign-quantization of W should recover stored keys and
values. This is both a CAPABILITY (memory dump from W) and a SECURITY finding
(adversary with W reads out content at low load).

## Hypothesis

For K < K* = N/(2 log N) ~ 170: max-cos-match between recovered candidates
and true (v_k, k_k) >= 0.5.
For K > 3*K* ~ 510: max-cos-match < 0.3 (noise floor).

## Operational

N=4096, K in {30, 60, 100, 150, 200, 300, 500, 800, 1500, 3000}, 5 seeds.
Build W; SVD W = U S V^T; take top-K columns of U as value candidates, top-K
rows of V^T as key candidates; sign-quantize; greedy match (max |cos|).

## Cited mechanism

- Hauptman & Karle phase problem (1950)
- Oszlanyi-Suto charge flipping (cond-mat/0308129) - we use simplified SVD
  variant; full charge-flipping is iterative refinement on top
- Carlini et al. cryptanalytic NN extraction (arXiv:2003.04884)
- Substrate research agent (this session)

## Expected runtime

Smoke: ~3 sec
Full: ~10-15 min on GPU (SVD of 4096x4096 x 5 seeds x 10 K values)

## Verdict labels

- `FORENSICS_RECOVERY_AT_LOW_K`: matches prediction (recovery below K*, not above)
- `FORENSICS_PARTIAL`: trend correct but recovery weaker than predicted
- `FORENSICS_NO_RECOVERY`: SVD+sign insufficient even below K*; iterative needed
- `FORENSICS_GRID_TOO_NARROW`: K range doesn't bracket K*
- `FORENSICS_INCONCLUSIVE`: empty data
