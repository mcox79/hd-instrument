# Pre-reg: Endpoint RM(1,16) projection (Strategy 09:45 PRIORITY C)

Test Research's prediction that ~25% terminal endpoints fall inside RM(1,16) subcode. Walsh-Hadamard transform projects each endpoint onto nearest RM(1,m) codeword; count fraction with Hamming distance <= d/2 = 2^15. N=65536, depth=50, K=100, n_starts=1000, 3 seeds.

## Verdicts
- `RM1M_25_PASS` — frac_within_d/2 in [0.15, 0.35] (~25% confirmed).
- `RM1M_FAIL_LOW` — frac < 0.15 (substrate avoids RM(1,16)).
- `RM1M_FAIL_HIGH` — frac > 0.35 (concentrates more than 25%).
