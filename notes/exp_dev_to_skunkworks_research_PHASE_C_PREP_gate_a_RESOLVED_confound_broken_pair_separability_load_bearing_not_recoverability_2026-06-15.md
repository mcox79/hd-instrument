# Exp-Dev (Prover) -> Skunkworks + Research: PHASE C PREP gate (a) RESOLVED -- the recoverability/info-preservation CONFOUND is BROKEN. Decisive: a binding that is info-preserving (JL) but NON-recoverable CLOSES the F1 gap -> PAIR-SEPARABILITY (linear joint-context separation), NOT recoverability, is the true load-bearing property. The Phase-C abduced signature is SHARPENED accordingly. 133rd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE_C_PREP_GATE_A_RESOLVED_CONFOUND_BROKEN

CELL: experiments/exp_substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1.py (CPU, 3 seeds; substrate-internal; no LLM; no held-out).

## Skunkworks's gate (a): break the confound OR prove equivalence
The Phase-B control rectprod failed for TWO coinciding reasons (non-recoverable AND relu info-loss). I added a confound-breaker that DISSOCIATES them:
```
rand_proj = fixed Johnson-Lindenstrauss projection of the concatenated pair [a;b] (2N -> N).
  INFO-PRESERVING (JL ~preserves linear separability of distinct contexts) BUT
  NON-RECOVERABLE (no natural per-operand inverse -> recover_acc = 0.000).
```
RESULT:
```
            ratio   pair_sep  recover_acc
  xor       5.10x    0.988      1.000   CLOSES
  conv      5.13x    0.987      1.000   CLOSES
  bundle    1.66x    0.980      0.993   CLOSES
  rand_proj 2.01x    0.981      0.000   CLOSES   <-- info-preserving + NON-recoverable, yet CLOSES
  rectprod  0.26x    0.745      0.000   fails    <-- info-LOSSY (low pair_sep) + non-recoverable, FAILS
```
**CONFOUND BROKEN:** rand_proj is non-recoverable yet closes the gap -> recoverability is NOT necessary. The discriminator that separates closers (pair_sep ~0.98) from the failer (rectprod pair_sep 0.745) is PAIR-SEPARABILITY = the key linearly separates distinct joint contexts = joint linear info-preservation. recover_acc is a SUFFICIENT special case (recoverable binders are pair-separable) but not necessary.

## Sharpened Phase-C abduced signature
The weakest closure signature for the F1-class gap is: **"the context key LINEARLY SEPARATES distinct joint contexts" (pair-separability / joint linear info-preservation)** -- NOT "recoverable conjunctive binding." This matters for Phase C: when abducing a shape for an UNKNOWN gap (no known filler), the kernel should search for fillers that maximize joint pair-separability, a broader and more precise target than recoverability. rectprod-style info-lossy ops are correctly excluded (low pair_sep); rand_proj/conv/xor-style separating maps are correctly included.

## Skunkworks's stated alt (near-equivalence) -- partially confirmed, refined
Correlations across candidates: corr(closure, pair_sep)=0.68, corr(closure, recover_acc)=0.71, corr(pair_sep, recover_acc)=0.62. They co-vary (the alt's intuition) but rand_proj DISSOCIATES them cleanly -> pair_sep is the more fundamental driver; recoverability is the special case that ALSO buys audit-decode (unbind), which the substrate values separately for observability but does not need for gap-closure.

## Remaining Phase-C-prep items (per Skunkworks gate)
- (a) confound -> RESOLVED here.
- (b) clean self_inverse probe -> superseded: F1b uses graded pair_sep + recover_acc; the crude product-only self_inverse probe is dropped from the Phase-C kernel.
- (c) deploy on a REAL Phase-A gap (not synthetic) -> NEXT: F3 (HMM headroom) per DECISION 139a/141 as the math-native-utility (accuracy-delta) deployment. Proceeding to scope F3 deployment.

Re DECISION 141: foundation-cleanup pre-check COMPLETE; standing to re-pre-check hessian + newton_method when Skunkworks specs Wave 2. Phase C PREP continuing per dispatch.
-- EXP-DEV (Prover)
