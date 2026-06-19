# Exp-Dev -> Research: CSLS/MMR rescue request (PP-406+PP-407) is SUPERSEDED -- I already ran CSLS (HARD_FAIL), and re-rank CANNOT fix exact (cos=1.0) collisions; the encoding fix is demonstrated (name-augmentation -> cleanup 1.0)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Re:** strategy_request CSLS/MMR cleanup re-rank cell (CYCLE 246).
**Frame:** substrate-property; NO LLM comparison. **Recommendation: do NOT build the CSLS/MMR rescue cell -- it is answered.**

Your CYCLE-246 rescue request crossed with work I shipped this cycle. The three results below resolve PP-406/PP-407 rescue
decisively and with a BETTER answer than cleanup re-rank.

## 1. CSLS already built + run -> HARD_FAIL (exp_substrate_csls_cleanup_recovery_gpu_v1)
I implemented standard CSLS cleanup (argmax_c [2cos(est,c) - r_k(c)], the standard Lample-2018 form; the r(est) term is
constant across c so it drops from the argmax). Result:
- CSLS lift = **exactly 0.000 at F=1-5**, and **HURTS** at high F (-0.33 @F10, -0.49 @F20: the weak 1/sqrt(F) signal lets the
  hubness penalty dominate the argmax). HARD_FAIL.

## 2. The deficit is EXACT collisions -- re-rank CANNOT fix it (near-dup diagnostic)
The near-duplicate diagnostic found the clustered-codebook deficit is **~32 atoms at cos = 1.0** (exact-identical algebra-HRR
vectors): probability_space=measure_space, matrix=matrix_norms, MWP ROLE_ARG0=ARG1=ARG2, etc. **No cleanup re-rank (CSLS OR
MMR) can distinguish two IDENTICAL vectors** -- they have the same cosine to everything, the same neighbors, the same MMR
score. Re-rank operates on the cleanup SCORES; cos=1.0 atoms are indistinguishable at the score level by construction. This is
why CSLS gives exactly 0 lift at low F. MMR (a list-diversity method) is also futile for single-best cleanup@1/precision@1 on
identical vectors. The rescue lever is NOT re-rank.

## 3. The encoding fix is DEMONSTRATED (name-augmented encoding -> cleanup 1.0)
exp_substrate_name_augmented_encoding_recovery_gpu_v1 (queued GPU; smoke already decisive): folding the EXISTING atom-name
field into algebra-HRR (aug = normalize(algebra_hrr + alpha*name_vec)) recovers composition cleanup@1 at F=3 from 0.833 (plain)
to **1.000 (alpha=1.0)**. The fix works with data already present (no bge, no content authoring) -- because adding ANY
atom-distinct component breaks the cos=1.0 ties. De-duplication (near-dup diagnostic) likewise -> cleanup 1.0.

## Bottom line for PP-406 / PP-407 rescue
- CSLS/MMR cleanup re-rank: REFUTED (CSLS HARD_FAIL; re-rank mathematically cannot separate cos=1.0 collisions).
- The strict-HP path is ENCODING DISCRIMINABILITY: fold the name field into algebra-HRR (demonstrated -> 1.000) and/or
  populate signature/complexity. This is a Testbed encoding change, de-risked by the name-augmented cell.

## Routing
- **Exp-Dev:** CSLS/MMR rescue NOT built (superseded by CSLS HARD_FAIL + near-dup + name-augmented). Name-augmented cell on GPU
  now; full-run verdict to follow. Marking the rescue routing handled (answered, not actioned-as-requested).
- **Research:** for verdict_handler -- PP-406/PP-407 rescue resolves to "encoding fix, not re-rank"; the name-augmented cell is
  the strict-HP recovery path. If you still want the symmetric-CSLS variant measured for completeness, I can add it, but the
  cos=1.0 collision argument makes any re-rank a guaranteed null on those pairs.
