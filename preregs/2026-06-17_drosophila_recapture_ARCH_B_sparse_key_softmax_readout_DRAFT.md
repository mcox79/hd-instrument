# PREREG (DRAFT): Drosophila-MB-sparse RECAPTURE -- ARCH-B sparse-key / dense-value / SOFTMAX (supra-linear) readout

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT -- bounded prep while Skunkworks result-VETs ARCH-A.
**GATED ON:** (1) ARCH-A result-VET clean; (2) Director strategic framing call (see "FRAMING QUESTION" below); (3) Skunkworks SCHEMA-VET; (4) Director STEP-2 LOCK -- before any cell-author.
**Drill source:** R1.1 Drosophila MB drill, conditional next fork "supra-linear selection step (softmax readout)".
**Recaptures:** scorecard claim 1 (Drosophila MB sparse f=0.05) -- STEP-4 GENUINE OVER-CLAIM (HARD_FAIL gap 0.004).
**Predecessor:** ARCH-A (sparse-key/dense-value/LINEAR readout) = MIDDLE_BAND, no robust recapture (commit 91336a55).
   ARCH-A localized the limiter to the LINEAR readout (per-bit-acc flat; sparse tracks dense across the whole cliff).
   ARCH-B replaces ONLY the readout with a supra-linear (softmax / modern-Hopfield) selection step.

## SCOPE (Director PROMOTED ARCH-B; final scope = USER E4 #13)
Director ratified ARCH-A MIDDLE_BAND + (converging with Skunkworks's corpus-wide weak-spot synthesis: LINEAR readout
= recurring capability ceiling) PROMOTED ARCH-B from "Drosophila conditional fork" to a candidate SUBSTRATE-WIDE
CROSS-CUTTING architectural experiment. The CORE design below (sparse-key / dense-value / softmax readout + the
framing question + beta no-Goodhart rule) is SCOPE-INVARIANT. Two scopes, USER decides (E4 #13):
- **(narrow) Drosophila-recapture-only:** the prereg below as-is (claim-1 recapture; smaller bet).
- **(wide) substrate-wide cross-cutting:** ADD test surfaces -- does softmax readout lift (a) charLM LM-hybrid
  (composes with R1.2), (b) real-encoder/projection cells (~24 cluster); AND a REGRESSION GUARD: no degradation on
  cert-grade EXACT/combinatorial flagships (composition L=10000, B2xB4, deletion-cert, multi-hop). Each surface =
  its own pre-registered band; the regression guard is a HARD gate (a readout change that lifts approximate tasks
  but regresses exact flagships is NOT a net win). Heavier -> some surfaces REMOTE (R4).
Either way the Drosophila recapture (below) is the anchor cell + lands first on laptop. I'll expand to the wide
surfaces only on USER E4 #13 = wide.

## Why ARCH-B is the right next fork (load-bearing from ARCH-A)
ARCH-A showed sparse-KEY gives no capacity gain THROUGH A LINEAR (superposition) readout: W=sum val key^T crosstalk
caps exact-recall at the alpha~0.25-0.5 cliff for ALL f_k. The drill's diagnosis: the MB uses sparse coding WITH a
nonlinear (winner-take-all-like) readout; the capacity comes from the COMBINATION. ARCH-B tests that combination.

## Design (genuinely different from ARCH-A on ONE axis: the readout)
```
SUBSTRATE: N=1024 dense bipolar (N=4096 confirm = separate before-VALIDATED gate, per Ask-4 -- REMOTE).
KEY:   TopK sparse bipolar, f_k in {0.05, 0.10, 0.20, 0.50, 1.00}. 1.00 = dense-key control; 0.05 = MB op point. (= ARCH-A)
VALUE: DENSE bipolar (+/-1), N-dim -- held dense to isolate the readout change. (= ARCH-A)
STORE: EXPLICIT separable memory: keep K (M,N) and V (M,N) as-is (NO linear superposition W). This is the
       architectural change -- a supra-linear readout needs access to individual stored keys.
READOUT (ARCH-B = the change): softmax attention / modern-Hopfield single step.
       scores  = beta * (K @ query)        # (M,) query-to-stored-key similarity
       weights = softmax(scores)           # (M,)
       recall  = sign(weights @ V)         # (N,) supra-linear (softmax) selection over values
       query = key_i (cued recall of the value stored with key_i).
BETA (no-Goodhart pre-registration): beta is FROZEN by a fixed rule = the beta maximizing the DENSE (f_k=1.0)
       exact-recall at the reference load M_test (tuned on the DENSE baseline ONLY, then applied IDENTICALLY to all
       f_k). NO per-f_k beta tuning (that would manufacture a sparse win). Report the beta + the dense-tuning curve.
M-GRID: smoke-located around the SOFTMAX exact-recall cliff (carry ARCH-A's empirical-cliff lesson: the softmax
       cliff likely sits at HIGHER M than the linear cliff; the smoke locates it, then fine-sample the transition).
SEEDS: smoke=1; FULL=5. COMPUTE: N=1024, explicit K,V (M,N) + softmax over M -> laptop super-fast.
PRIMARY metric = exact-recall (cos(sign(recall),val) >= 0.90), DECIDES verdict. SECONDARY = per-bit-acc (diagnostic
       only, no proxy substitution / Goodhart). (Carries ARCH-A REQ-1 anchor-rule + REQ-2 metric discipline.)
```

## FRAMING QUESTION for the Director (strategic; do NOT lock until ratified)
The original claim 1 is "sparse coding (f=0.05) achieves high capacity" -- NOT necessarily "sparse BEATS dense." Two
candidate PRIMARY bands; they answer different questions:

**(A) Sparsity-advantage framing** -- PRIMARY = sparse-key(0.05) vs dense-key(1.0) under the SAME softmax, at the
   pre-registered anchor M (dense softmax exact-recall ~0.5). HARD_PASS = +5pp. Tests "sparsity gives a capacity EDGE
   under nonlinear readout." STRICTER than the original claim; risks a false-negative if softmax makes both near-perfect.

**(B) Capability-recapture framing (RECOMMENDED)** -- PRIMARY = at a pre-registered HIGH-LOAD M_test BEYOND the ARCH-A
   linear cliff (where linear exact-recall < 0.10), does sparse-key(0.05)+softmax achieve exact-recall >= 0.90 (5/5
   seeds) AND substantially beat the ARCH-A linear baseline at the same M? This faithfully re-establishes the ORIGINAL
   capability ("the sparse-coding architecture, with its nonlinear readout, achieves high-capacity recall"). The
   sparse-vs-dense comparison (framing A) is reported as a DIAGNOSTIC to SCOPE the finding precisely + avoid a trivial
   softmax-lookup pass: "recapture is nonlinear-readout-enabled; sparsity {is / is not} required (dense-key {fails /
   also passes})." Avoids over-reaching beyond what the original claim asserted.

Exp-Dev recommends (B): it matches the original claim's semantic, avoids the framing-(A) over-reach, and the diagnostic
keeps it honest (no trivial-softmax-pass, sparsity role explicitly scoped). Director owns the call.

## Pre-registered bands (under recommended framing B; finalize on Director ratify + smoke)
```
M_test: pre-registered load where ARCH-A LINEAR exact-recall < 0.10 (smoke-confirm; candidate M=512 or higher).
HARD_PASS (RECAPTURE): exact-recall(f_k=0.05, M_test) >= 0.90, 5/5 seeds, AND >= ARCH-A-linear(same M) + large margin.
   -> capability recaptured via nonlinear readout. N=4096 confirm (Ask-4, REMOTE) REQUIRED before scorecard VALIDATED.
HONEST_BOUNDED: exact-recall(f_k=0.05, M_test) < 0.90 (softmax also fails to recapture at this load) -> bounded; the
   linear-readout ceiling is not the only limiter; next fork = ARCH-C (Willshaw / thresholded) or scope as method-bound.
DIAGNOSTIC (scopes, not gates): sparse-key vs dense-key under softmax at M_test + the per-f_k x M exact-recall surface;
   per-bit-acc surface. Reports whether sparsity is REQUIRED or softmax alone suffices (honest scope of the recapture).
```

## Honest-recapture framing (per central discipline; point 5)
P_recapture(absolute capacity via softmax) is plausibly HIGHER than ARCH-A's 0.35 (the drill localized the limiter to
the linear readout). BUT the SPARSITY-SPECIFIC advantage (framing A) is uncertain -- softmax may recapture capacity
with OR without sparsity. Either is a real finding: a framing-(B) HARD_PASS with dense-key-also-passing honestly
scopes the recapture as "nonlinear-readout-enabled, sparsity-not-required" -- still re-establishes the capability, with
precise scope. We TEST recapture; we do not manufacture it (no per-f_k beta tuning; absolute bar pre-registered).

## Cert-chain next steps
1. ARCH-A result-VET clean (Skunkworks) + Director ratify ARCH-A verdict.
2. Director FRAMING call (A vs B; Exp-Dev recommends B).
3. Skunkworks SCHEMA-VET (method-genuinely-different = YES, readout axis; beta no-Goodhart rule; M_test pre-reg).
4. Director STEP-2 LOCK -> Exp-Dev cell-author + verification witness + smoke (locate softmax cliff / confirm M_test)
   -> FULL 5-seed (laptop N=1024) -> verdict -> (HARD_PASS) N=4096 REMOTE confirm -> re-atomize (Skunkworks populate-check).

-- Exp-Dev (Prover) [DRAFT]
