# Pre-registration: primitive_1_residue_FPE_v1

**Date:** 2026-06-16
**Anchor:** primitive_1_residue_FPE_v1
**Queue:** overnight_queue
**N:** 4096, **Seeds:** 7,17,23, **bases:** 3,5,7,11

## Scientific question
TIER-3 PRIMITIVE 1: is residue-FPE a sound continuous-magnitude ENCODING primitive? Encode value x via Fractional
Power Encoding (complex exponent V^x=exp(i x theta)) with r coprime-base residue layering; decode within range.
Instantiates Skunkworks's RATIFIED prereg (DECISION 210) + the RATIFIED GATE-B structural split (DECISION 211/213:
B1 decodability is P1's; B2 efficient-resonator-decode is Primitive-2's domain). GATE-C (product-kernel base-
independence for continuous x + resolution/capacity envelope) is the genuine VERIFY-NOT-ASSUME open question; the
remote full-N run adjudicates it neutrally (no prejudge per Skunkworks STEP-4 flag).

## Pre-registered bands (tune-free; honest-negative per gate)

**HARD-PASS (PRIMITIVE_1_LOAD_BEARING):**
- GATE-A: max_d |measured_sim(d) - sinc(d)| <= TOL_A = 0.02 + 3*sqrt(1/N) (kernel matches closed-form)
- GATE-B1 decodability: coprime bases AND brute-force/CRT decode_acc >= 0.99 (encoding uniquely carries x)
- GATE-C1: product-kernel HOLDS (max_d |combined - product_of_per_base| <= TOL_C1 = 0.02 + 3*sqrt(1/N))
- GATE-C2 envelope reported as a function (resolution vs range/capacity)

**MIDDLE / HONEST-BOUNDED (HONEST_BOUNDED_C1_BREAKS):** GATE-A + B1 pass but GATE-C1 product-kernel BREAKS at full N
-> base independence fails for continuous x -> file integer-residue + single-channel-continuous BOUNDED (honest
scope); continuous-residue product-kernel NOT load-bearing.

**HARD-FAIL:** GATE-A kernel divergence (base-phase model wrong -> STOP) OR GATE-B1 decode_acc < 0.99 (encoding
range-bounded).

## Calibration rationale
TOL_A / TOL_C1 are finite-N fluctuation bands (3-sigma of the (1/N) Monte-Carlo kernel estimate); tune-free. The
GATE-C1 smoke break (err 0.75 at N=1024) is DIRECTIONAL only -- empirical (not algebraic, unlike 190a); the remote
full-N run adjudicates whether it is a finite-N artifact (resolves at scale -> HOLDS) or a genuine independence
break (-> HONEST-BOUNDED). LOG-SCALING DECODE (B2 efficient resonator) is OPEN and OUT OF SCOPE for Primitive-1
(Primitive-2's domain); residue-FPE's log-scaling ADVANTAGE is NOT claimed here.

## N-suffix section
Production N = 4096; GATE-A + B1 light (laptop-verified at smoke); GATE-C (C1 product-kernel sweep + C2 envelope
across bases x bandwidth x |codebook| x resolution) is the medium-heavy remote part.

## Timeout estimate
Smoke ~ 5s at N=1024 (GATE-A + B1 brute-force + GATE-C small). FULL: N=4096, seeds=3, bases=[3,5,7,11] (R=1155);
GATE-C grid + brute-force B1 over R codewords dominate.
formula: ceil(1.5 * 5 * (4096/1024)^1.5 * (1155/105)) ~ generous for the GATE-C sweep.
timeout_s = 7200
