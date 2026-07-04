# Encoder rescue plan — converged diagnosis (2026-07-04)

Synthesis of the FULL HARD_FAIL, the exp_dev diagnosis (a03cf07), and the brain drill (ad8b03).
Reconciles an apparent conflict between them and re-aims the USER-requested 5x rescue battery.

## Diagnosis: FAIR negative, root cause = the OBJECTIVE does not scale (not the sparsifier)

- **EVAL FAIRNESS = FAIR** (exp_dev, verified). All arms share the identical `_semantic_unit`/held-set/pair-rng/spearman; RANDOM_BLOCK=0.002 calibrates it; CHARPOS is ALSO k=128 sparse ternary (no structural edge; 2000-subset caveat = +0.012, immaterial). The negative is real — do not dismiss on fairness.
- **DENSE_SIGN (NO sparsifier) collapsed 0.825(smoke 3k) -> 0.368(full 178k).** So the failure is the LEARNED MAP / OBJECTIVE, not the block-STE sparsifier.
- **Not under-training:** train_diag (remote): BLOCK_K128 rkd_last=0.149 (vs smoke 0.061, ~2.4x higher floor), lr_last~1.5e-12 (fully decayed = converged). 128 teacher-draws/concept at full vs 9.6 at smoke (13x MORE) yet WORSE held generalization -> objective problem, not steps.
- **Mechanism (exp_dev):** RKD target is in-batch `x@x.T`, 512x512 over 160k concepts. In-batch pairwise coverage batch/V: smoke 6.4% -> full 0.32% (20x drop). Graded near-neighbor pairs (what spearman measures) co-occur in a batch ~1e-5/step -> graded geometry is NEVER supervised at scale; the map learns bulk near-orthogonality + NCE snap-to-top-1.

## Reconciliation: the brain drill's D1 premise was PARTIALLY FALSIFIED

The brain drill (rich-first-then-sparsify; no external teacher) is a correct PRINCIPLE, but its D1 rescue assumed DENSE geometry stays ~0.825 at scale and only sparsification breaks it. exp_dev's off-disk finding falsifies that: **DENSE (no sparsifier) also collapsed to 0.368.** So "form the rich geometry first, sparsify after" only works once the OBJECTIVE can form the rich geometry at scale — which it currently cannot. **Order of fix: (1) fix the objective so DENSE recovers to ~0.8 at scale, THEN (2) brain-style dense-first-then-sparsify.** The brain lens still holds — it also independently indicts our EXTERNAL teacher (BGE) vs the brain's internal self-teacher, which doubles as a violation of the locked "substrate standalone / no external LLM" anchor.

## The fork (Part B, running, locks it)
- **H-SCALE (lean ~90%):** DENSE collapses as V grows (3k->40k) on the LOCAL unit-normalized cache with the same objective -> genuine objective-scaling failure -> the global-objective fix below.
- **H-BUG (residual ~10%):** collapse is specific to the remote 177899 cache. Local 43905 cache IS unit-normalized (row-norm 0.99998). The remote 177899 norm is UNVERIFIED (my off-disk check hit a path error; retry). If Part B shows DENSE stays ~0.8 at V=40k locally -> escalate H-BUG on the remote cache (re-encode), NOT a global objective.

## 5x rescue battery (re-aimed at the OBJECTIVE; fire when Part B locks H-SCALE)
- **R1 (BUILD, lead) — global / landmark RKD objective.** Match each batch concept's code-vs-teacher cosine to a FIXED ~8k landmark/anchor frame (+ neighbor-clustered batches reusing the existing semi-hard mining) so graded geometry is supervised independent of random in-batch co-occurrence. **VALIDATE on the DENSE readout first (target DENSE recovers to ~0.8), THEN sparsify.** This is the concrete fix exp_dev recommended.
- **R2 — brain dense-first-then-sparsify sequencing (brain D1, post-R1).** Once R1 restores dense geometry, introduce sparsity by ANNEAL / competitive k-WTA readout AFTER geometry forms, never a step-0 hard bottleneck. (The drafted tau_b anneal / dense->sparse curriculum, now first-principles-justified; algebra-safe by construction since deployed code is always exact-argmax.)
- **R3 — internal self-teacher / wean off external BGE (brain D2 + substrate-standalone anchor).** EMA self-distillation + positives from the KB's own relational/gloss co-occurrence. Longer-term; resolves the locked-anchor tension; gated on corpus richness.
- **R4 — predictive / temporal-contiguity auxiliary over the relational graph (brain D3).** Hebbian/slowness signal pulling relation-path-adjacent concepts together; densifies the thin 1.6-atoms/entity signal; supplies R3's positives; teacher-free.
- **R5 — K=256 capacity-bound diagnostic.** Is 0.85 AT true 2% (K~82) physically reachable, or capacity-bound (0.85 only at 3.1% K=128)? One-shot probe; if capacity-bound it's a USER strategy call, not a fix.

**Sequencing:** R1 is the load-bearing build (do first, validate DENSE). R2 rides on R1. R3/R4 are the principled substrate-standalone direction to grow into. R5 is a cheap diagnostic to run alongside R1. Do NOT run the sparsifier-only levers standalone — their premise (dense geometry is fine) is falsified.
