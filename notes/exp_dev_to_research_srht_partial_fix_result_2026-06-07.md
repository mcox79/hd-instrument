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
