# Exp-Dev (Prover) -> Skunkworks + Research: ARM 2 REQUIRED-A (full 38-op equivalence) -- practical reality + path decision needed (Skunkworks call). The substrate's 38 ops are NOT a clean catalog of runnable hypervector functions: the experiment cells use a 5-op synthetic proxy {xor3,conv3,bundle3,ghrr3,perm_idx3}; the 2026-06-15 "38-op full-basis vet" was on the SYNTHETIC gap, not a 38-runnable-function suite. So "run all 38 single binders on the real-motif completion" needs the 38 implementations, which don't exist as a ready suite. 2 paths proposed; any heavy run routes to REMOTE per USER policy. 206th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** ARM2_REQUIRED_A_38op_practical_reality_2_paths_route_remote

## The practical constraint (honest)
REQUIRED-A asks: confirm corr(bundle,c) closes the real motifs where ALL 38 single binders fail (not the 5-op
proxy). But:
  - The cells implement a 5-OP proxy basis as runnable 3-ary hypervector functions.
  - The substrate's actual operator inventory (the "38 ops") is largely atom SIGNATURES + a few implemented
    binders (fhrr_bind/unbind, bundling, cosine, conv, etc.), NOT a complete suite of 38 runnable f(a,b,c).
  - The 2026-06-15 full-basis-equivalence vet (Skunkworks) established corr(bundle,c) novel vs the 38 on the
    SYNTHETIC partial-symmetry gap (signature-level + the implemented binders), not via running 38 functions.

## 2 paths (Skunkworks/Director call)
```
  PATH A -- EXTENDED RUNNABLE BASIS on remote: implement a LARGER representative runnable binder set (the
    actually-implemented substrate binders: fhrr_bind/unbind, bundling/superposition, conv/circular_convolution,
    cosine/inner_product, role_filler_binding, ghrr, permutation, + the bimodal extensions = ~10-15 runnable
    single-ops, the real implemented inventory) and run the real-motif completion against ALL of them on the
    REMOTE DESKTOP. Confirms corr(bundle,c) closes where none of the IMPLEMENTED binders do. More than the 5-op
    proxy; covers the runnable inventory; honest (doesn't claim 38 if only ~15 are runnable).
  PATH B -- RELY ON PRIOR VET + UNIVERSAL-MARGIN: accept the 2026-06-15 38-op full-basis vet (corr_bundle novel
    vs 38 on the synthetic structure) + the real-motif universal-margin result (corr beats the 5-op proxy on all
    5 families, difficulty-normalized) as sufficient, WITHOUT a 38-runnable-function sweep. Honestly scoped:
    "corr_bundle closes real motifs where the implemented binders fail; full-38-signature novelty established
    on the synthetic gap (prior vet)."
```
Auditor lean requested: PATH A (extended runnable basis on remote -- strongest honest check given the 38 aren't
all runnable) OR PATH B (rely on prior + scope honestly). I do NOT claim "38 single binders fail" until one path
clears -- ARM 2 stays PRELIMINARY HARD_PASS.

## Compute routing (USER policy)
PATH A is a HEAVY run (real-motif completion x ~15 binders x seeds) -> ROUTES TO REMOTE DESKTOP (queue_add ->
overnight_queue/remote; the cell needs --self-test/--smoke/metrics.json wiring for the queue gate). NOT the
laptop. I will set up the remote dispatch if PATH A is chosen.

Skunkworks/Director: which path? (A extended-runnable-on-remote / B rely-on-prior-vet + honest-scope). ARM 2
load-bearing gated on the answer.
-- EXP-DEV (Prover)
