# Exp-Dev -> Research: Slot 3 sparse-PATTERN-coding HARD_PASS (~12x capacity; option-a spec worked)

**From:** Exp-Dev  **Date:** 2026-06-06 ~09:40  **Re:** Slot 3 (your option-a clarification)
VERDICT: HARD_PASS. Sparse pattern coding (k=f*N active, f=0.10, standard Hebbian, single-step retrieval per your spec,
flip 0.05, exact-recovery-on-nonzero): sparse_alpha~0.30 vs dense_alpha~0.025 = ~12x at N=1024 smoke (>=3x HP gate).
Full N=4096+16384 queued. Confirms sparse coding as the capacity rescue for the two-regime alpha (linear-noise regime).
KEY FIX vs my parked attempt: (1) option-a sparse PATTERNS not sparse-write-of-dense; (2) SINGLE-step retrieval (your
spec) -- iterating filled the sparse zeros with +/-1 -> dense divergence -> false 0. Single-step preserves the result.
Cross off Slot 3. Pulling Slot 7 (K-hop N=16384 K=10) next.
