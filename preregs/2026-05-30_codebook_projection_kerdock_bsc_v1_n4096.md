# Prereg: codebook_projection_kerdock_bsc_v1_n4096

Date: 2026-05-30
Anchor: codebook_projection_kerdock_bsc_v1_n4096
Script: experiments/exp_codebook_projection_kerdock_bsc_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding)

## Question

Op C (msg-1 T6): cross-codebook projection. Per msg-1 caveat ("depends
on substrate-physics analysis"), this is a SMOKE TEST of the simplest
projection: identity-mapping under shared dimensionality N=4096.

Substrate A: Kerdock codebook.
Substrate B: BSC codebook (random +/-1).
Same KEY/VAL indices stored in both. Query constructed in Kerdock space
(probe_keys_A); apply to W_B; decode in BSC space.

Does cross-codebook retrieval succeed?

## Pre-registered bands

- **HARD_PASS**: cross-codebook retrieval accuracy >= 0.75 AND
  `KF-2 max_iso on W_B <= 0.05` in >= 3/5 seeds.
- **HARD_FAIL**: cross-codebook retrieval accuracy <= 0.30
  (no cross-codebook coherence under identity projection).
- **MIDDLE_BAND**: otherwise.

## Scope caveat

Per msg-1, full Op C requires substrate-physics analytic argument.
HP at this smoke confirms a path forward worth deeper analysis;
HF closes the trivial-identity-projection branch but does not rule out
nontrivial algebraic projection paths.

## Sweep

- N=4096, M=128 facts
- Seeds: 5 ([7,17,23,31,41])
- Total cells: 5

Two codebooks built at N=4096:
- Kerdock 4-coset (substrate A)
- BSC random {-1, +1} (substrate B)

## Timeout estimate

14400s (4h). 5 cells * ~30s = 150s; ample.

## Memory footprint

2 codebooks at N=4096: 1.6GB. 2 W matrices: 128MB. Keys 16MB. Total
~1.8GB. Within 6GB cap.

## N-suffix

`_n4096` binds production N = 4096. Smoke runs at N=1024.
