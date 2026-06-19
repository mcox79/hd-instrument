# Exp-Dev (Prover) -> Research (Director): DECISION 82 follow-up (ran on REMOTE GPU) -- the DECISION 79/81 cycle-cleanup PRESERVES the headline M4d held-out F1 EXACTLY (+0.0000 on BOTH q54-q65 and 56d; 20 edge-endpoints removed). Claim 14 capability_preservation now confirmed at the RETRIEVAL-F1 level, complementing the axiom-termination level (79a). 63rd honest signal (incl. a verify-before-asserting self-catch on a duplicate-atom resolver bug).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_82g_CLEANUP_PRESERVES_M4d_F1
**Cell:** experiments/exp_substrate_82g_m4d_post_cleanup_f1_effect_cpu_v1.py (committed). Ran on REMOTE GPU (ssh marsh@home; the verified compute path). Non-destructive: removed the 10 cleanup edges IN-MEMORY on the remote's pre-cleanup state; no substrate mutation.

## Result
M4d (beta=0.10) held-out F1, PRE-cleanup vs POST-cleanup (10 DEPENDS_ON edges removed in-memory; 20 endpoints):
```
q54-q65:  PRE=0.2721 | POST=0.2721 | delta +0.0000
56d:      PRE=0.2218 | POST=0.2218 | delta +0.0000
```
HARD_PASS: |delta| <= 0.01 on both. The 10 removed wrong-direction edges (cosine<->inner_product reverse, FFT/DFT, bayes/cond_prob, gradient family, fhrr DUAL re-type, etc.) were NOT retrieval-load-bearing for the held-out queries -- expected, since they are operator-foundational edges off the held-out neuroscience/concept gold paths.

## Significance
Claim 14 (substrate self-corrects its own graph) capability_preservation is now confirmed at TWO independent levels:
1. AXIOM-TERMINATION (79a pre-check + 81 post-ratify): 213/213 preserved; no atom loses grounding.
2. RETRIEVAL-F1 (this 82g): the headline M4d held-out metric is byte-identical pre/post cleanup.
So the first non-additive workstream removed wrong-direction debt with ZERO capability cost at both the soundness and the served-capability levels.

## Verify-before-asserting self-catch (19th rule; part of 63rd signal)
First 82g run reported delta +0.0000 but with n_removed=0 -- VACUOUS (a duplicate-atom resolver bug: cosine_similarity exists at BOTH T1 and T3, so a short->qualified resolver mismatched the edge endpoints). I caught it via the n_removed=0 telltale, switched to short-name-pair matching (robust to the duplicate), and re-ran -> 20 endpoints removed, real +0.0000. Reinforces the DECISION 81c atom-MERGE need (cosine_similarity T1/T3 duplicate keeps causing resolver mismatches).

## Compute note (USER directive: GPU accessible for experiments)
Ran on the remote GPU end-to-end (verified path). The remote's substrate state (pre-the-laptop-cleanup) was actually the CORRECT state for this PRE-vs-POST measurement (it still has the edges to remove). For experiments needing the laptop's POST-cleanup canonical state, a laptop->remote sync is still required (96-relation drift) -- offered, pending greenlight.

-- EXP-DEV (Prover)
