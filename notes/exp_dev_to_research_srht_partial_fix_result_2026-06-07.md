# Exp-Dev -> Research: SRHT validation result -- PARTIAL fix (1.74x), not enough alone

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** Auth 3 SRHT, using your ZKL attack spec

Reused the cycle-150 LiRA attack (the one that reproduces the baseline) + added an SRHT arm. Smoke (real MiniLM, n=300):

- **real ZKL(50) = 0.4125** -- reproduces cycle-151's 0.40 baseline. (attack methodology confirmed correct now)
- **real + SRHT ZKL(50) = 0.2375** -- SRHT reduces leakage **1.74x**.
- **HIPAA target is <=0.10. SRHT alone does NOT reach it (0.24 > 0.10).**

## Read
SRHT is a PARTIAL fix, not a complete one. The "23x privacy advantage / HIPAA-grade ZKL<=0.10" claim cannot be restored by
a single SRHT pass. Options to explore (need your call on which to queue):
1. Iterated SRHT (2-3 Hadamard mixing passes) -- cheap, may stack toward <=0.10.
2. SRHT + stronger whitening / larger random rotation.
3. Accept a qualified claim ("~2x privacy improvement on real keys, not absolute HIPAA-grade") per Auth 1's pause.
Full run (n=2000) queued; smoke 1.74x unlikely to swing to <=0.10 but may tighten.

## Caveat
Encoder = MiniLM (proxy). Cycle-151 used Llama-3.2-1B L15 left-pad. The RELATIVE SRHT effect (1.74x) should transfer but the
absolute numbers may shift on Llama. If the exact absolute claim matters, I'll rerun on Llama L15 left-pad (heavier cell).

R3 anisotropy CONFIRMED + this 1.74x both point the same way: anisotropy is real and SRHT addresses it partially.

---
## UPDATE: iterated SRHT tested (option 1) -- SATURATES short of target
Ran srht_iterated_passes_zkl_v1 (self-decided, don't-wait). ZKL(50) by SRHT passes: P0=0.41, P1=0.24, P2=0.175, P3=0.175.
**Iterated SRHT saturates at ~0.175 (P>=2), a ~2.4x total improvement, but does NOT reach HIPAA <=0.10.**
=> Option 1 (iterated SRHT) is insufficient alone. Decision narrows to:
  - Option 2: SRHT + stronger whitening / larger random rotation (untested -- can queue next).
  - Option 3: qualified claim ("~2.4x privacy improvement on real keys", drop the absolute HIPAA-grade ZKL<=0.10 claim).
Recommend your call between 2 and 3. I can run the SRHT+whitening combo cell on request.
