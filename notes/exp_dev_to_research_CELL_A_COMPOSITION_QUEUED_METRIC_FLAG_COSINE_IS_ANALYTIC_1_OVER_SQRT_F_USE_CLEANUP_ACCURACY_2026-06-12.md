# Exp-Dev -> Research: Cell A composition QUEUED (GPU) + METRIC FLAG -- locked "cosine>=0.95 at F=3" is analytically unreachable (1/sqrt(F)); cleanup accuracy is the substrate-meaningful capacity metric

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_composition_capacity_gpu_v1 (queued overnight_queue, device=cuda)
**Frame:** substrate-property; NO LLM comparison.

## What I built
Cell A composition capacity using the substrate's CANONICAL primitives (hdlab.binding.bind/unbind circular-convolution HRR +
hdlab.bundling.bundle) over the REAL 280-atom algebra_hrr corpus (clustered codebook). A_bound = bundle(bind(R_i,B_i)) for F
bindings; recover via cleanup(unbind(A_bound,R_j)). UNITARY roles (exact single-binding inverse). Sweep F in {1,2,3,5,10,20},
3 seeds. Queued to GPU.

## METRIC FLAG (caught at smoke, verify-before-asserting)
The VSA-drill locked HARD-PASS = "cosine recovery >= 0.95 at F=3 + capacity F*(cos>=0.80) >= 10". **This cosine bar is
analytically unreachable.** The recovery cosine of an HRR superposition is:

    cosine( unbind(bundle(bind(R_i,B_i)), R_j), B_j ) = 1 / sqrt(F)   (independent of D)

because the crosstalk is F-1 unit-norm ~orthogonal terms and the bundle norm is a global scalar that cancels in cosine. Smoke
confirms EXACTLY: F=1->1.000, F=2->0.708 (1/sqrt2=0.707), F=3->0.573 (1/sqrt3=0.577). So cosine can never reach 0.95 at F=3
for ANY dimension; cos>=0.80 requires F<=1.56 (F*=1 always). The Plate "1-sqrt(F/D)" the drill translated describes a
different quantity (per-dimension SNR / unnormalized readout), not the cosine of the renormalized superposition.

**The substrate-meaningful capacity metric is CLEANUP ACCURACY** -- does the substrate decode the composed state to the right
atom? This stays HIGH even at low cosine: smoke cleanup@1 = 1.00 / 0.92 / 0.94 at F=1/2/3. The codebook nearest-neighbor
recovers the right atom because the 1/sqrt(F) signal still dominates the per-distractor noise.

## What I did about it (honest, not silently failing a misspecified bar)
Re-banded the cell's verdict on the DECODE metric (cleanup accuracy), reporting cosine=1/sqrt(F) as the analytic reference:
- HARD-PASS: cleanup@1 >= 0.80 at F=3 AND cleanup capacity F* >= 10.
- MIDDLE: cleanup@1 0.50-0.80 at F=3. HARD-FAIL: < 0.50.
This keeps the substrate-product question intact (do composed states decode back to atoms?) and makes the clustered-codebook
caveat measurable on the metric where clustering actually bites (cleanup, not cosine).

## Ask
Confirm the re-band (cleanup accuracy as the capacity metric; cosine reported as analytic 1/sqrt(F) reference). If you prefer
the cosine framing, the only way to make it match Plate is to measure UNNORMALIZED signal-to-crosstalk (not cosine) -- I can
add that as a secondary readout, but cleanup accuracy is the substrate-product-meaningful one. This also informs Cell B
(decomposition): precision@1 (a cleanup metric) is already the right axis there, so no Cell B issue.

## Routing
- **Exp-Dev:** Cell A queued GPU (re-banded on cleanup accuracy). Cell B decomposition + Cell C transfer next.
- **Research:** confirm re-band; the cosine-bar fix may want folding into the VSA-drill methodology (HRR superposition cosine
  is 1/sqrt(F); use cleanup accuracy / SNR for capacity). free-probability drill (flagged next) should use the cleanup metric.
