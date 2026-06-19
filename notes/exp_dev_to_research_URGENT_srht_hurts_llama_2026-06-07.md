# Exp-Dev -> Research: URGENT -- SRHT is COUNTERPRODUCTIVE on the production Llama encoder

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** SRHT next-steps test 2 (Llama-3.2-1B L15 left-pad)

## Headline: SRHT helps MiniLM but HURTS Llama. Do NOT start the SRHT engineering (Auth 3) on the production encoder.

Ran the production-encoder test you asked for (test 2). Same cycle-150 LiRA attack, SRHT passes {0,1,2,3}:

| SRHT passes | MiniLM ZKL(50) | Llama-3.2-1B L15 ZKL(50) |
|---|---|---|
| 0 | 0.41 | 0.22 |
| 1 | 0.24 | 0.45 |
| 2 | 0.175 | 0.57 |
| 3 | 0.175 | 0.58 |

**On Llama-L15 (the production encoder), SRHT MONOTONICALLY INCREASES leakage** (0.22 -> 0.58). The 1.74x improvement was a
MiniLM-specific artifact; it does NOT transfer to the real encoder -- it reverses.

## Implications
1. **Authorization 3 (3-5 day SRHT engineering) should be PAUSED/CANCELLED** -- SRHT degrades privacy on the production
   encoder. Building it would be wasted effort + would ship a regression.
2. The HIPAA absolute claim cannot be restored via SRHT. Path is now option 3 (qualified claim) OR a different mechanism.
3. Why opposite? Hypothesis: MiniLM (D=384) and Llama-L15 (D=2048) have different anisotropy structure; Hadamard mixing
   on Llama's representation spreads signal into a more uniform sign pattern the grounding attack exploits MORE. Worth a
   short R3-style diagnostic on Llama's eigenspectrum if you want the mechanism.

## Caveats (so you can weight this)
- Smoke n=200. Llama base ZKL=0.22 here vs cycle-151's reported 0.40 -- my left-pad/last-token setup may differ slightly
  from cycle-151's exact harness. Full run (n=1500) queued. BUT the DIRECTION (SRHT monotonically worse across 3 passes on
  Llama) is a strong clear signal unlikely to be noise.
- If you have the exact cycle-151 Llama harness, reconciling base ZKL (0.22 vs 0.40) would tighten this.

## Recommendation
Hold SRHT engineering. Decide between: (a) qualified privacy claim (~2-3x relative, rate-limit posture, drop absolute HIPAA),
or (b) a non-SRHT decorrelation mechanism. I can run the Llama eigenspectrum diagnostic next if useful.
