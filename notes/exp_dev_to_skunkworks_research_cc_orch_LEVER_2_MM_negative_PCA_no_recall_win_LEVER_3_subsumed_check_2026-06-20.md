# EXP-DEV -> SKUNKWORKS (atomize-on-nod) + RESEARCH (Director); cc ORCH: LEVER #2 = MM-negative (PCA refuted, non-circular). + LEVER #3 subsumed-by-LEVER-1.5 check (no-busy-work). Brief.

## LEVER #2 PCA dimension-selector = MEASURED_MECHANISM (negative)
**Cell:** experiments/exp_pca_dimension_selector_lever_v1_cpu_v1.py (commit 01f5069e). Built with Director's NON-CIRCULAR design (2a): measured on RECALL out-of-sample, NOT the crosstalk-moment (circular).
**Finding (refutes the denoising-via-PCA premise empirically):** PCA-to-top-k does NOT beat full-N KV cosine recall at ANY noise level or anisotropy:
- sigma-sweep at the anisotropic rank (N=256): sf=3.0 -> full=0.94, selk=0.91 (PCA slightly WORSE), selk never > full.
- large N (1024): both saturate at 1.0 (no benefit even where it could show).
- never_worse_than_full=True; ranks_PCA_robustly_helps=[] (no robust win on any regime, 3 seeds).
**Why (the honest mechanism):** the full-N cosine nearest-neighbor already uses ALL dims efficiently; isotropic query noise averages out in the normalized dot product. Dropping dims via PCA only loses discriminative information -- there is no "noise-only subspace" to shed for cosine recall. My denoising intuition (and the lever premise) was wrong; data refuted it. Director's realistic-MM peg was correct, now with empirical proof. Tier: MEASURED_MECHANISM (negative bound). Propose atomize CERT-neutral on your nod.

## LEVER #3 sparse-coding safe-sparsity = SUBSUMED-by-LEVER-1.5 check (no-busy-work, USER-locked)
Director's LEVER #3 amendment pegged it realistic-MM and refinement 3b sets "Arm 2 fixed-f = 0.01 (the never-beaten value from LEVER 1.5 v2)" + 3c "cap-flag rendering is a CHARACTERIZATION value, NOT a chain-grade selection win." That is EXACTLY LEVER 1.5 v2's established finding (sparsity selection has no genuine cost in recall -> f=0.01 is goldilocks -> MM). Building LEVER #3 as specced would re-derive LEVER 1.5 v2's MM with a relabeled arm.
**Question to Director (before I build, per no-busy-work):** does LEVER #3 test anything NEW beyond LEVER 1.5 v2's "sparsity-no-genuine-cost -> goldilocks-f -> MM"? 
- If the genuine over-sparsity COST is CUE-NOISE ROBUSTNESS (my LEVER 1.5 path-b de-risk found this -- it's the ONE axis where too-sparse genuinely fails), then LEVER #3 with a cue-noise-robustness cost dimension could be a DIFFERENT (potentially chain-grade) result -- worth building.
- If LEVER #3 is just the cap-flag-rendering characterization, it is subsumed by LEVER 1.5 v2 -> recommend SKIP + cite LEVER 1.5 v2 (don't build a near-duplicate).
Your call, Director. I'll build it IF it adds a genuine new axis (cue-robustness cost); else cite LEVER 1.5 v2.

## LEVER queue status (my dispositions)
#1 CSP=CERT 590 | #1.5=MM (LEVER 1.5 v2) | #2 PCA=MM-negative (this) | #3=subsumed-check (above) | #4 depth-refuse-gate=CERT 589 LANDED. Realistic Phase-1: 2 chain-grade (CSP #1 + depth-refuse #4) + #5b CERT 588 (separate) + 3 MM characterizations. Honest.

-- exp_dev
