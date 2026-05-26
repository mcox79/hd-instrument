# Prereg — wave14_tropical_kerdock_N4_closed_form_v1

## Hypothesis

For the N=4 4-coset Kerdock codebook (16 codewords in {+/-1}^4), the
minimum pairwise tropical (max-plus) margin admits an exact closed-form
derivation. The closed form should match exhaustive enumeration to
floating-point precision.

This is the F-14 rescue path R2: analytical N=4 closed-form. R1 is the
4-coset variant with full symmetry at larger N (separate experiment).

## Pre-registered bands

- **HARD PASS** (`TROP_R2_CLOSED_FORM_VERIFIED`):
  - |empirical min margin - closed-form min margin| < 1e-6.
  - R2 confirmed as a structural rescue route for F-14.

- **HARD FAIL** (`TROP_R2_DISAGREE`):
  - |empirical - closed-form| > 1e-3.
  - Closed-form derivation is wrong; R2 rescue route fails.

- **MIDDLE BAND** (`TROP_R2_INCONCLUSIVE`):
  - Diff in [1e-6, 1e-3]; suspicious but not decisive.

## Design

- N = 4, K = 16 (4-coset Kerdock built by enumeration over GF(2)^2 sign
  diagonals applied to Sylvester Hadamard H_4).
- Exhaustive: all C(16, 2) = 120 pair margins computed.
- Closed-form prediction derived from the structure: in bipolar {+/-1}^N
  most pairs agree in some position (giving max(c+c') = 2, hence margin = 0),
  so the minimum over pairs is 0. (Negation pairs c' = -c give margin = 2,
  but they are NOT the minimum.)
- 1 cell, no seeds needed (deterministic).

ETA: ~5 sec wall (CPU). Conservative timeout 600 s.

## Citations

- F-14 cap_map row (tropical margin); R1/R2 rescue notes in
  notes/research_meta_map_and_adjacencies_*.md.
- Maclagan-Sturmfels "Introduction to Tropical Geometry" (2015).

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 600 s.
- Pure numpy + itertools.combinations (no CUDA, no torch deps).
