# Pre-reg: Continuous streaming inference (Strategy 10:03 v151 P5 Cap 3)

Throughput ratio = steady-state throughput / burn-in throughput across N=8192, M=200, burn=100, steady=200, n_blocks=3.

## Verdicts
- `STREAMING_CONTINUOUS_PASS` — ratio >= 0.9 (NESS robust).
- `STREAMING_DEGRADED` — 0.5 <= ratio < 0.9.
- `STREAMING_NESS_BREAKS` — ratio < 0.5.
