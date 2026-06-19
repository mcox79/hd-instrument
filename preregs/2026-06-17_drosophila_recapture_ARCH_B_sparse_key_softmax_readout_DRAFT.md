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

## FRAMING for the Director (strategic; do NOT lock until ratified) + Skunkworks AUDIT CONSTRAINT (binding either way)
SKUNKWORKS SCHEMA-VET audit flag (binding under ANY framing): claim-1 = "Drosophila MB sparse f=0.05 gives a CAPACITY
BOOST" = a SPARSITY-ADVANTAGE claim. Therefore **sparse > dense MUST GATE the recapture VERDICT LABEL** -- NOT be a mere
scoping/secondary diagnostic. A softmax readout that helps sparse and dense EQUALLY is a real finding ("nonlinear
readout lifts capacity, SPARSITY-NEUTRAL") but it is NOT a recapture of the Drosophila SPARSITY claim. (This corrects
Exp-Dev's first draft, which had sparse-vs-dense as a scoping diagnostic; 19th-rule update -- Skunkworks is right: that
would let a trivial-softmax-pass be mis-credited as a sparse recapture.)

RECOMMENDED FRAMING = HYBRID (B-regime + A-gating), the two combined:
- **REGIME (from B):** evaluate at a pre-registered HIGH-LOAD M_test BEYOND the ARCH-A linear cliff (where ARCH-A
  linear exact-recall < 0.10) -- the regime where the linear readout failed, so any readout-enabled capacity is visible.
- **GATING (from A; Skunkworks-required):** the RECAPTURE label requires sparse-key(0.05) > dense-key(1.0) by +5pp at
  M_test (5/5 seeds) under the SAME frozen-beta softmax -- the sparsity advantage, which IS claim-1.
- Both must hold for HARD_PASS=RECAPTURE. If the capability appears but is sparsity-NEUTRAL (sparse ~= dense), that is
  filed honestly as "nonlinear readout lifts capacity (sparsity-neutral)" -- a real READOUT finding, claim-1 STAYS
  DOWNGRADED (NOT a Drosophila-sparse recapture). This is the only framing that faithfully tests claim-1 + cannot be
  gamed by a trivial softmax lookup.

(Pure A vs pure B is moot now: the audit constraint folds A's gating into B's regime. Director still owns whether to
also report the absolute-capability bar as a secondary headline; Exp-Dev recommends yes -- it cleanly separates "is the
limiter the readout" from "does sparsity specifically help".)

## Pre-registered bands (HYBRID framing + Skunkworks sparse>dense GATING; finalize on Director ratify + smoke)
```
M_test: pre-registered load where ARCH-A LINEAR exact-recall < 0.10 (smoke-confirm; candidate M=512 or higher).
beta: frozen by the dense-baseline-tuned rule, applied identically to all f_k (no per-f_k tuning).

HARD_PASS (RECAPTURE -- requires BOTH, the sparse>dense gate is Skunkworks-binding):
   (i) CAPABILITY: exact-recall(f_k=0.05, M_test) >= 0.90, 5/5 seeds, AND >= ARCH-A-linear(same M) + large margin; AND
   (ii) SPARSITY ADVANTAGE: exact-recall(f_k=0.05, M_test) >= exact-recall(f_k=1.0 dense, M_test) + 0.05, 5/5 seeds.
   -> claim-1 sparsity capacity-boost RECAPTURED via nonlinear readout. N=4096 confirm (Ask-4, REMOTE) before VALIDATED.

SPARSITY_NEUTRAL (capability exists but sparsity gives no edge -- NOT a Drosophila-sparse recapture):
   (i) holds [softmax lifts capacity beyond the linear cliff] BUT (ii) fails [sparse ~= dense, within +5pp].
   -> file honestly as "nonlinear readout lifts capacity (SPARSITY-NEUTRAL)" = a real READOUT finding (feeds the
   cross-cutting nonlinear-readout bet + held-out-retrieval track), but claim-1 Drosophila-sparse STAYS DOWNGRADED.

HONEST_BOUNDED: (i) fails [exact-recall(f_k=0.05, M_test) < 0.90 -- softmax does not recapture capacity at this load
   either] -> bounded; the linear readout is not the sole limiter; next fork = ARCH-C (Willshaw/thresholded) or method-bound.

DIAGNOSTIC (reported, does not gate): per-f_k x M exact-recall surface + per-bit-acc surface (shows WHERE the sparse and
   dense softmax cliffs sit + whether sparse shifts the cliff). Scopes the finding; the verdict LABEL is set by the gates above.
```

## Honest-recapture framing (per central discipline; point 5)
P(capability via softmax) is plausibly HIGHER than ARCH-A's 0.35 (the drill localized the limiter to the linear
readout), so SPARSITY_NEUTRAL (capability lifts but sparse ~= dense) is a live + likely outcome. But the SPARSITY-
SPECIFIC advantage (the actual claim-1) is genuinely uncertain. Per Skunkworks's binding constraint, only sparse>dense
earns the RECAPTURE label; a sparsity-neutral capability lift is filed as a READOUT finding (claim-1 stays downgraded).
All three outcomes (HARD_PASS / SPARSITY_NEUTRAL / HONEST_BOUNDED) are real findings. We TEST recapture; we do not
manufacture it (no per-f_k beta tuning; absolute bar + sparse>dense gate both pre-registered).

## Cert-chain next steps
1. ARCH-A result-VET clean (Skunkworks) + Director ratify ARCH-A verdict.
2. Director FRAMING call (A vs B; Exp-Dev recommends B).
3. Skunkworks SCHEMA-VET (method-genuinely-different = YES, readout axis; beta no-Goodhart rule; M_test pre-reg).
4. Director STEP-2 LOCK -> Exp-Dev cell-author + verification witness + smoke (locate softmax cliff / confirm M_test)
   -> FULL 5-seed (laptop N=1024) -> verdict -> (HARD_PASS) N=4096 REMOTE confirm -> re-atomize (Skunkworks populate-check).

-- Exp-Dev (Prover) [DRAFT]
