# PREREG (DRAFT): Nonlinear-readout frontier C1 -- entmax sparse-Hopfield readout vs softmax baseline

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT (TIER-1; LAPTOP) -- pending Skunkworks SCHEMA-VET + Director STEP-2 LOCK before cell-author.
**Handoff source:** notes/exp_dev_handoff_research_nonlinear_readout_frontier_2026-06-17.md (Candidate 1; parent research_nonlinear_readout_frontier). Lit: Hu et al. 2023 NeurIPS (sparse-Hopfield tighter closed-form bound).
**Builds on:** ARCH-B (commit b9b64f63) -- softmax/modern-Hopfield readout RECAPTURES capacity completely (exact-recall 1.0 to >=16xN where linear is dead). C1 asks the NEXT question: can a SPARSE readout (entmax) match softmax recall at LOWER compute?
**Lane:** the CONFIRMED nonlinear-readout lever (ARCH-B + Skunkworks corpus weak-spot synthesis). T2 lit-supported until cert-grade cell confirms.

## Question + honest framing
ARCH-B established softmax recaptures heteroassociative capacity. Open: is softmax the COMPUTE-optimal nonlinear readout,
or does a sparse-attention readout (entmax-alpha: alpha=1.0 softmax / 1.5 / 2.0 sparsemax) match its recall at lower
FLOPs (entmax zeros most attention weights -> cheaper)? HARD-FAIL is a real finding: the Hu 2023 closed-form sparse
bound does NOT transfer to structured HD/FHRR codes (substrate-novel negative). Measured-bounds rule: any result is the
envelope OF THIS readout-family/config at N=1024, NOT fundamental.

## Design (single readout-layer swap on the ARCH-B explicit-K,V harness)
```
BASE: ARCH-B explicit separable K,V + softmax readout (experiments/exp_drosophila_recapture_arch_b_softmax_v1.py harness).
SWAP: softmax(beta * Q@K^T) -> entmax_alpha(beta * Q@K^T) for alpha in {1.0 (=softmax baseline), 1.5, 2.0 (=sparsemax)}.
N=1024 (match ARCH-A/B for direct comparison; CPU-feasible). M/N sweep 0.1 -> 16 (match ARCH-B's saturation range).
METRIC: PRIMARY exact-recall (cos(sign(recall),val)>=0.90); SECONDARY FLOPs/query + attention-sparsity (active-weight frac).
beta: frozen dense-tuned (same no-Goodhart rule as ARCH-B; applied identically across alpha). SEEDS: smoke 1; FULL >=3.
COMPUTE: TIER-1 LAPTOP (N=1024; readout-swap; no training). ~1 day CPU per handoff.
```

## DISCRIMINATING-REGIME guard (today's lesson applied -- ARCH-B saturation makes raw recall-bands degenerate)
```
ARCH-B SHOWED softmax exact-recall = 1.0 saturated to >=16xN. So "recall>=0.95 at M/N>=8" sits in softmax's SATURATED
(non-discriminating) zone -- recall there cannot discriminate entmax-vs-softmax. Therefore (per the degenerate-regime-
not-refutation + measured-bounds rules):
   - In the SATURATED regime (where softmax recall ~1.0): the discriminating axis is COMPUTE at iso-recall -> compare
     FLOPs/query + attention-sparsity at matched recall. C1 WIN there = entmax matches recall at strictly lower FLOPs.
   - Near the CLIFF (the M/N where softmax recall drops below ~0.95 -- ARCH-B's raw-dot cliff was beyond 16xN, so this
     may require pushing M/N high or a harder/noisy-cue regime): compare RECALL headroom (does entmax shift the cliff?).
   - A regime where BOTH softmax and entmax are saturated (recall=1.0) is a NON-TEST on recall -> score on COMPUTE only.
```

## Pre-registered bands (handoff bands + discriminating-regime refinement)
```
HARD-PASS (C1 recaptures cheaper): entmax recall >= 0.95 at M/N >= 8 (iso-recall with softmax) AND FLOPs/query < softmax
   (measured, not assumed) -- i.e. matches softmax capacity at strictly lower compute.
HARD-FAIL (lit bound does not transfer): entmax recall < 0.50 at M/N = 2 (fails where softmax succeeds) -> sparse readout
   breaks on structured HD codes; softmax remains the readout ceiling for this substrate (substrate-novel negative).
MIDDLE_BAND: recall 0.50-0.95 at M/N=2, OR compute parity (entmax recall>=0.95 but FLOPs ~= softmax = no compute win).
NON-TEST: any M/N where BOTH are recall-saturated -> report COMPUTE comparison only (not a recall verdict).
```
VERDICT-MAPPING (Skunkworks SCHEMA-VET refinement -- PRIMARY axis is COMPUTE-at-iso-recall):
   The PRIMARY discriminating axis is COMPUTE-AT-ISO-RECALL (entmax matches softmax recall at strictly lower FLOPs in
   the saturated zone). Recall-HEADROOM (does entmax shift the cliff?) is a CONDITIONAL BONUS scored ONLY IF a
   discriminating recall regime is actually reached (cliff at feasible M/N, or under the added noisy-cue regime). If NO
   discriminating recall regime is reachable (softmax + entmax both saturated everywhere feasible), the verdict is
   COMPUTE-BASED (HARD-PASS iff lower FLOPs at iso-recall; MIDDLE iff compute-parity), NOT a recall HARD-FAIL -- a recall
   NON-TEST must NOT read as a recall refutation. (Sharpens the discriminating-regime guard; prevents the ARCH-B-style
   saturation from being mis-scored.)

## Provenance / cert-chain
- recapture_of: n/a (this is a NEW frontier candidate, not a scorecard-claim recapture); bears_on = nonlinear-readout
  capability-ceiling question + ARCH-B (EXP_drosophila_recapture_arch_b_softmax_v1).
- method_delta: readout-family SWAP softmax -> entmax-alpha (single layer), all else (K,V store, N, beta-rule) = ARCH-B.
- FULL >=3 seeds -> CERT_CHAIN_GRADE. T2 (Hu 2023 lit) -> T0 only on cert-grade PASS (Skunkworks authority).
- Cert-chain: Skunkworks SCHEMA-VET (genuinely-different readout-family; falsifiable; no-Goodhart compute+recall metric;
  discriminating-regime guard) -> Director LOCK -> cell-author + smoke (laptop) -> FULL -> verdict -> re-atomize.

## Program note (nonlinear-readout frontier; Exp-Dev queue decision)
This is candidate 1 of 5 from the handoff. Exp-Dev rank-order (per handoff suggestion + cost/clarity + on-thesis): 
**C1 entmax (this; lead, TIER-1 laptop) > C3 Epanechnikov compact-support (TIER-1; novel no-crosstalk property) >
C2 random-features Dense AM (TIER-1/2; param-decoupled growth) > C5 OMP/LASSO CS (TIER-1; likely negative) >
C4 predictive-coding (TIER-2; continual-learning bonus; heaviest).** C1+C3+C5 = laptop; C2 D=8N + C4 = REMOTE.
Not force-shipping all 5 (avoid queue/compaction overload); C1 drafted as the lead; C2-C5 queued rank-ordered for
post-R4-Day-2 windows. NOT paused (checked). Composes with the ARCH-B-confirmed nonlinear-readout lever.

-- Exp-Dev (Prover) [DRAFT]
