# Wave 11: LDPC-cleanup HDC — Design

Reference: substrate audit, 2026-05-18. Verdict: "Pentti Kanerva's
original sparse distributed memory is implicitly an ECC; explicit
BCH/LDPC-based HDC remains underexplored. Capacity guarantees inherited
from the code (Shannon-bound cleanup). Concretely interesting; underrated."

Closest published work:
- arXiv 2511.01838 *Efficient VSAs from Histogram Recovery* (2025)
- arXiv 2502.11487 NB-LDPC for processing-in-memory (hardware focus)

## The LDPC-cleanup idea

In a standard HDC system, "cleanup" means projecting a noisy hypervector
onto the nearest codebook entry (e.g., one of 256 byte atoms). With
random atoms this works probabilistically — Frady-Kleyko-Sommer 2018
gives capacity ≤ N / (2 · SNR_min).

**LDPC-cleanup replaces the random codebook with a structured one:**
Use the codewords of a Low-Density Parity-Check (LDPC) code as the
substrate vectors. Cleanup uses belief-propagation decoding to project
noisy outputs onto valid codewords. This inherits the LDPC code's
Shannon-bound recovery guarantees.

## Concrete design

Substrate parameters:
- Code: (n, k) LDPC with n = 4096 (matched to our current dim)
- Rate: k/n = 0.5 (k = 2048 information bits → 2^2048 codewords total)
- Atoms: pick 256 + K = 260 specific codewords as byte and position atoms
  (randomly chosen from the 2^k codeword space using a fixed seed)
- Substrate values: ±1 per bit (bipolar BSC-style)
- Binding: elementwise multiplication (XOR for ±1)
- Bundling: sum + sign (BSC-style)

**Key difference from BSC:** at READ TIME, instead of nearest-neighbor
search over the 260-atom codebook, run **belief propagation** on the
LDPC code's Tanner graph to find the nearest CODEWORD to the noisy
query. Then check which of our 260 specific atoms it matches.

Why this might help: belief propagation can correct bit errors that
exceed the random-codebook capacity. The LDPC code has known
error-correction capacity (Shannon-bound at the given rate).

## Implementation effort

Two sub-modules:

1. **LDPC code generation:** use `pyldpc` library or implement Gallager
   construction. Parity-check matrix H of shape (n-k, n). Generator
   matrix G of shape (k, n). Effort: ~2 days.

2. **Belief propagation decoder:** sum-product or min-sum algorithm on
   the Tanner graph. Effort: ~3 days for a working implementation;
   need to vectorize for batch inference.

Total: ~1 week.

## Crucial design subtlety

LDPC binding via elementwise multiplication does NOT preserve the
codeword property: if `c1` and `c2` are codewords, `c1 * c2` is generally
NOT a codeword. So bound atoms drift OUT of the codeword space.

**Two design choices:**

**A. Cleanup ONLY at the final byte prediction.** Internal binding /
bundling can drift; only when we do "what's the predicted byte?" do
we run BP to find the nearest codeword AMONG the 256 byte atoms.

**B. Re-project after every operation.** Run BP after every bind/bundle
to snap back to codeword space. More principled but more expensive.

For first prototype: choice A. Simpler and more aligned with how HDC
"cleanup" usually works (only at output, not internally).

## What we're testing

The hypothesis is: **does using LDPC-structured atoms improve cleanup
accuracy at higher SNR (= when W is well-trained)?**

If yes, expect:
- Lower test bpc at convergence (cleanup is sharper)
- Smaller W norm at convergence (less compensatory updating needed)

If no, the cleanup wasn't the bottleneck and LDPC structure just
constrains the codebook unnecessarily.

## Falsification

Best LDPC-BSC variant vs plain BSC (2.4817):
- Support if ≤ 2.46 (≥ 0.02 improvement)
- Reject if ≥ 2.50 (no improvement)
- LDPC is worth Phase B (re-project after operations) only if Phase A
  shows non-trivial improvement.

## Simplest first prototype (this commit)

Even simpler than the full design: **just measure cleanup accuracy
under controlled noise.** Build the LDPC code, generate 256 byte atoms
from it, add Gaussian noise, decode via BP, measure recovery rate.
Compare to random-codebook cleanup at the same SNR.

This is a unit test, not a full byte-LM experiment. If it shows the
expected capacity advantage, write the full LM experiment in a
follow-up.

Effort for the unit test: ~half day. Validates the path before
committing the full week to a byte-LM integration.
