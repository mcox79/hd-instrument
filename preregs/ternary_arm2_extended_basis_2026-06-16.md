# Prereg: ARM 2 ternary partial-symmetry vs EXTENDED RUNNABLE single-binder basis (REQUIRED-A, PATH A)

Date: 2026-06-16. Anchor: ternary_motif_phase_B_arm2_extended_basis_cpu_v1. Compute: REMOTE DESKTOP (heavy; USER policy).

## Question
Does corr(bundle(a,b),c) (the 2026-06-15 confirmed tier-2 partial-symmetric composition) close the REAL
math-scoped MOTIF-B families where ALL extended RUNNABLE single binders fail -- strengthening ARM 2 from the
5-op proxy to the ~8 implemented single-binder 3-ary ops? (Honest scope: the substrate's "38 ops" are
SIGNATURES; ~8 are runnable hypervector functions. This is the extended-runnable-basis check, NOT a 38-function
sweep. Composes with the prior signature-level 38-op vet + the difficulty-normalized universal-margin result.)

## Method
Per-effective-family generalization-split completion (3 c-roles + a-b swap + separate random target labels =
no leak), N=4096, n=3 seeds, REPS=24. SINGLES (8): xor3, conv3, bundle3, ghrr3, perm_idx3, xorperm3,
bundleperm3, convperm3. COMP target: corr_bundle = corr(bundle(a,b),c). Math-corpus-scoped MOTIF-B families
(5 effective; DFT-meta + 4 non-DFT).

## Pre-registered bands
- HARD-PASS: corr_bundle closes (>=0.80) where ALL 8 single-binders fail (<0.80), on >= majority (>=3) of 5
  effective families INCLUDING >=2 NON-DFT (the non-DFT-closure generality gate). Difficulty-normalized check:
  corr_bundle margin over best-of-8 > 0 in ALL families (universal advantage).
- MIDDLE_BAND: universal margin (corr beats best-of-8 everywhere) BUT absolute-closure cardinality-bounded
  (<majority close at the 0.80 bar; the DFT-meta higher-cardinality family closes only difficulty-matched).
- HARD-FAIL: corr_bundle does NOT beat best-of-8 (no partial-symmetry advantage over the extended basis).

## Integrity
Vector-native (bundle+corr; no graph-walk). No target-in-key leak (separate target labels). run_mode tier-A
(full, n>=3). compute_backend stamped. NOT load-bearing until Skunkworks BUILD VET (full-basis-equivalence +
non-DFT closure + difficulty-control). Smoke result confers ZERO verdict (run_mode asymmetry).
