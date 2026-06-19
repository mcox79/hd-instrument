# Pre-registration: wave14kerdock_hadamard

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14kerdock_hadamard.py](../experiments/exp_wave14kerdock_hadamard.py)

## Why

Agent 1 research (codebooks): Kerdock codes achieve Welch-bound coherence with
50-350x faster cleanup. The simplest possible Kerdock-like test: M=N=4096
Hadamard matrix (zero coherence, fully orthogonal) vs random +/-1 codebook.

If Hadamard gives meaningful K* gain over random, the materials prediction
("crystalline beats amorphous") holds. This is the lower-bound test before
investing in full Kerdock construction.

## Hypothesis

At fixed M=N=4096, Hadamard codebook gives K* >= 1.5x random codebook.

## Operational definition

- N=4096, M=4096 (square dictionary)
- Codebook 1: random +/-1 (M, N)
- Codebook 2: Sylvester Hadamard matrix (M, N) - exactly orthogonal
- Bundle K randomly-chosen codewords; rank all M by sim to bundle; top-K hits
- Sweep K in {50, 100, 200, 400, 600, 900, 1300, 2000, 3000}
- 5 seeds, 20 trials per (K, seed)
- K* via linear interp at recovery=0.5

## Cited mechanism

- Welch bound: |c_i . c_j| >= sqrt((M-N)/(N(M-1)))
- Hadamard matrices: Sylvester construction
- Random +/-1: coherence ~ sqrt(2 log(M)/N) ~ 0.064 at N=4096, M=N
- Hadamard: coherence = 0 (orthogonal rows)

## Expected runtime

Smoke (N=256): ~10 sec
Full (N=4096): ~5-10 min on GPU
