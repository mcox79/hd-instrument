# Alternative-cleanup-mechanism research drill (post att1 v1+v2 rejection)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7)
**Drill type:** Substrate-native alternatives to iterative-attractor cleanup
**Trigger:** att1 v1 (Ramsauer T={2,4,16}) + v2 (Krotov POLY/QUAD/EXP at M/N=0.098 below alpha_c) both HARD_FAIL with lift = -0.020 to 0.000 over argmax baseline. Iterative-attractor mechanism family TRULY NULL for substrate cleanup.
**Lit-scan calibration penalty:** applied (deflate raw P 0.15-0.25; cap novel-synthesis P at 0.50)
**Generic-terms-only queries** per query-privacy

---

## HEADLINE
Top-2 to dispatch: **(1) OMP / sparse-coding cleanup (residual-shrinkage; structurally orthogonal to similarity-iteration; P_deflated=0.45)** and **(2) Multi-bump CAN ensemble (K parallel init-conditions + vote; explicit lit-precedent for noise robustness; P_deflated=0.40)**. Iterative-attractor failed because argmax IS the zero-T limit of softmax-Hopfield; revival requires a DIFFERENT dynamics class, not parameter tweaks of the same class.

---

## CHEAP DECISIVE TEST (top candidate: OMP / sparse-coding cleanup)

**Premise:** cue `y = atom_i + noise` is modeled as `y = D·x + e`, where `D` is the (N x M) codebook-dictionary, `x` is 1-sparse (or k-sparse for compositional cues), `e` is Gaussian. OMP recovers `x` by iteratively (a) selecting the codebook column max-correlated with the current residual, (b) projecting `y` onto the span of selected columns via least-squares, (c) subtracting reconstruction from `y` to form a new residual.

**Why structurally different from att1:** att1 (iterative-attractor) maps `state -> renormalize(softmax(temp * state @ D.T) @ D)` -- a similarity-based fixed-point dynamics where state stays in the codebook-span and the energy landscape is unchanged. OMP explicitly tracks a SHRINKING RESIDUAL via least-squares projection -- the residual norm provably monotonically decreases; selected support grows; final reconstruction can be FAR from any single codebook entry's basin. This is a different operator class.

**Cell design:**
- N_DIM=512, M=200 (matches att1 v1 over-capacity regime), N_EVAL=200, seeds=[7,17,23], sigmas=[0.0, 0.5, 1.0, 1.5, 2.0]
- Arms:
  - ARGMAX_BASELINE (1-shot argmax over D.T @ y)
  - OMP_K1 (k=1; one residual step; should recover same as argmax in low-noise regime)
  - OMP_K2 (k=2; two greedy steps; tests whether k-sparse decomposition explains noisy cue better than single atom)
  - OMP_K4 (k=4; tests substrate's actual usage pattern -- cues are often noisy superpositions)
- Wall: ~30-60s laptop CPU (matrix ops only, no iteration).

**Decisive metric:** lift at sigma=1.50 over argmax baseline, across all seeds, in recall-at-1 (where "recall" = top-1 index in the recovered sparse support matches the planted atom).

**Pre-reg thresholds:**
- HARD_PASS: best_omp_lift >= +0.05 at sigma=1.50 (recall_harder), CV <= 0.30, conv frac = 1.0 across all 3 seeds
- HARD_FAIL: best_omp_lift <= -0.005 at sigma=1.50 (no benefit OR regression), OR conv frac < 0.8 (numerical instability)
- MIDDLE_BAND: lift in (-0.005, +0.05) -> route to deeper drill (different k regime, or coherence-controlled D)

---

## FALSIFIABLE PREDICTIONS

### Top candidate: OMP / sparse-coding cleanup

**Quantitative predictions at sigma=1.50, N=512, M=200 (matching att1 v1):**
1. OMP_K1 should approximately MATCH argmax (within +/- 0.01) -- this is the sanity check; if it DOESN'T match argmax, the implementation is wrong.
2. OMP_K2 should LIFT over argmax by at least +0.03 if the cue's effective sparsity is genuinely > 1 in noise regime (noise spreads cue energy across multiple codebook columns; OMP_K=2 captures the second-most-aligned column).
3. OMP_K4 lift should saturate or DECREASE vs OMP_K2 (over-sparsity hypothesis kicks in around k=mu(D)^-1 where mu = max-coherence; for random bipolar at N=512, M=200, mu ~ 0.1-0.15, so k_max ~ 6-10).

**Falsifiers (mechanism truly null):**
- HARD_FAIL: best OMP arm lift <= -0.005 vs argmax at sigma=1.50 (3 seeds). Means cue's energy at high noise is NOT decomposable into the codebook span -- noise dominates structural signal -- and residual-shrinkage offers nothing single-atom argmax doesn't already get.
- CONFOUND_FAIL: OMP_K1 deviates from argmax by > 0.01 -> implementation bug, NOT mechanism rejection.

**Implications if HARD_PASS:** unblocks n4 k-WTA-VQ ceiling at high noise; substrate codebook gets a NEW primitive (`omp_cleanup`) usable across n9/n10/p1; chain-grade extension probable at full M.

**Implications if HARD_FAIL:** the substrate's cue-to-codebook noise problem is structural -- noise at sigma=1.50 has effectively destroyed the codebook signal regardless of decoder; need to push UPSTREAM to encoder (whitening / lift to N=4096) rather than DOWNSTREAM at cleanup.

---

## RANK-ORDERED CANDIDATES (6 families)

### #1. OMP / sparse-coding cleanup (P_deflated=0.45)

**Mechanism:** greedy sparse recovery; treat noisy cue as `y = D x + e`; iteratively select max-correlated atom + project + subtract.

**Brain analog:** mid; cerebellar Marr-Albus theory does parallel sparse-fan-in (granule cells), but OMP itself is a signal-processing primitive (Mallat-Zhang 1993; Tropp-Gilbert 2007 RIP analysis).

**Substrate-native variant:** existing codebook IS the dictionary D; no new structure. Residual `r_t = y - D[:, S_t] @ x_t` where S_t = selected support, x_t = LS-projection. Stop at k=1,2,4 fixed-budget.

**Cell to test:** as in "cheap decisive test" above. ~30-60s laptop CPU.

**P_revival deflated:** 0.45. Raw P was 0.60 from sparse-recovery literature (RIP guarantees in N>>M log M regime are well-established); deflated 0.15 because: (a) substrate is in over-capacity regime M=200 with N=512 where RIP only holds in expectation, NOT uniformly; (b) noise at sigma=1.50 may have ||e|| > ||signal||, in which case OMP has no convergence guarantee.

**Cost:** ~30min impl + ~30min smoke. Laptop CPU. M=200 N=512 is sub-second per seed per arm; full sweep ~30s.

**Structural orthogonality to iterative-attractor:** HIGH. OMP's residual-shrinkage dynamics is fundamentally different from softmax-fixed-point iteration; success or failure here is INDEPENDENT of att1's outcome.

---

### #2. Multi-bump CAN ensemble cleanup (P_deflated=0.40)

**Mechanism:** K parallel cleanup-states initialized at perturbations of the cue; each evolves under softmax-attractor dynamics; final readout = mode/median of K final states. Multi-bump CAN literature (PLOS Comp Bio 2022; Frontiers 2025) shows K bumps reduce noise-driven drift across S-type and D-type noise.

**Brain analog:** strong; head-direction ring + grid-cell torus naturally have multiple bumps; cerebellar microzones provide K parallel processing units.

**Substrate-native variant:** K=4 or K=8 initial states `s_k = renormalize(y + epsilon_k)` where `epsilon_k ~ N(0, sigma_init * I)`; each runs att1-style softmax iteration for max_steps=4; final readout = `argmax(sum_k s_k @ D.T)`.

**Cell to test:** N_DIM=512, M=200, sigmas=[1.0, 1.5, 2.0], K_bump in {1, 4, 8}, sigma_init in {0.1, 0.3, 0.5}, seeds=[7,17,23]. ~5-10min CPU.

**P_revival deflated:** 0.40. Raw P was 0.55 from multi-bump literature deflated 0.15 because (a) substrate isn't continuous-manifold (codebook is discrete); (b) K-vote may still be trapped in same bad basin if cue is OUT of any basin.

**Cost:** ~30min impl on top of existing iterative_attractor.py; reuses 90% of code. ~5-10min smoke.

**Structural orthogonality to iterative-attractor:** MID. Same fixed-point dynamics per-bump, but ensemble-over-initializations is a different statistical operator. Not fully orthogonal -- a partial revival.

---

### #3. SDM radius-readout cleanup (P_deflated=0.35)

**Mechanism:** Kanerva SDM 1988; read activates ALL hard locations within Hamming/cosine radius r AND AVERAGES them. With M atoms in N=512, radius r ~ 0.7-0.8 cosine activates ~k*M atoms (k ~ 0.05-0.10 in HD); readout = mean of activated atoms.

**Brain analog:** distributed-memory model; Kanerva himself maps it to cerebellum (Albus-Marr).

**Substrate-native variant:** mostly already exists (n11 RI uses ternary indices); cleanup = `mean(D[ similarity(y, D) > r ])` instead of `argmax`.

**Cell to test:** N_DIM=512, M=200, sigmas=[1.0, 1.5, 2.0], radius r in {0.6, 0.7, 0.75, 0.8}, seeds=[7,17,23]. ~5min CPU.

**P_revival deflated:** 0.35. Raw P was 0.50 deflated 0.15. Risk: averaging may DESTROY the single-atom identity at high noise (signal averages to zero with surrounding noise atoms).

**Cost:** ~20min impl + ~5min smoke. Very cheap.

**Structural orthogonality to iterative-attractor:** MID. Different operator (mean-in-radius vs softmax-fixed-point), but still operates on the same similarity surface.

---

### #4. Hub-and-spoke 2-tier cleanup (P_deflated=0.30)

**Mechanism:** Patterson-Rogers ATL hub-and-spoke; noisy cue -> first cleanup to one of K hubs (K << M categorical anchors) -> hub identity selects M/K-sized subspace -> cleanup within subspace.

**Brain analog:** strong; semantic dementia evidence for ATL hub; oscillatory MEG evidence for hub-spoke dynamics.

**Substrate-native variant:** 2-stage. Stage 1: argmax over K hub-vectors (where hubs are learned via k-means or chain-grade-atom clustering on D). Stage 2: argmax over M/K atoms assigned to chosen hub. Reduces effective M per stage to sqrt(M) optimally.

**Cell to test:** N_DIM=512, M=200, K_hubs in {8, 16, 32}, hub_assignment via k-means on D, sigmas=[1.0, 1.5, 2.0], seeds=[7,17,23]. ~20min CPU.

**P_revival deflated:** 0.30. Hub-cleanup quality depends entirely on hub-discovery quality; in random codebooks (which substrate uses), hubs are random and don't compress noise. Real lift only if codebook has cluster structure.

**Cost:** ~1hr impl (need k-means + 2-stage cleanup wrapper). Mid effort.

**Structural orthogonality to iterative-attractor:** HIGH (different mechanism class), but leverage low because random-codebook regime doesn't reward hierarchy.

---

### #5. Bayesian MAP posterior cleanup (P_deflated=0.20)

**Mechanism:** cleanup = argmax_i [log P(cue | atom_i) + log P(atom_i)] where P(cue | atom) = N(atom, sigma^2) and P(atom_i) = usage-frequency or chain-grade-status.

**Brain analog:** mid; Bayesian-brain hypothesis (Knill, Friston, Pouget); brain combines priors with sensory likelihood.

**Substrate-native variant:** trivial extension of argmax; multiply similarity by log-prior weight per atom. Prior = (a) uniform [baseline = argmax], (b) chain-grade-atom-weighted, (c) recent-use-weighted.

**Cell to test:** N_DIM=512, M=200, prior in {uniform, chain-grade-weighted, recency-weighted}, sigmas=[1.0, 1.5, 2.0], seeds=[7,17,23]. ~5min CPU.

**P_revival deflated:** 0.20. Only helps if substrate has sharply non-uniform atom usage (which is somewhat true: chain-grade atoms are queried more) AND if the cleanup-failure mode is "wrong-but-plausible atom wins" (which is testable). Most realistically gives small lifts (0.01-0.03) not the 0.05 HARD_PASS threshold.

**Cost:** ~15min impl. Very cheap.

**Structural orthogonality to iterative-attractor:** LOW. Same argmax-similarity operator, just reweighted. Argmax IS uniform-prior MAP.

---

### #6. Reservoir-of-modules ensemble vote (P_deflated=0.20)

**Mechanism:** K small W matrices, each trained on a partition; cue -> K parallel cleanups -> majority vote on result.

**Brain analog:** strong; cerebellar microzones; cortical column ensembles.

**Substrate-native variant:** m1 modular cell already at MEASURED_MECHANISM tier. K=8 partitions of codebook; per-partition argmax cleanup; vote.

**Cell to test:** mostly already in m1 substrate; ~20min to extract cleanup-only smoke.

**P_revival deflated:** 0.20. m1 already explored this direction without chain-grade win; unlikely to flip with cleanup-only test.

**Cost:** ~30min repurposing existing m1 primitives.

**Structural orthogonality to iterative-attractor:** MID. Per-module is still argmax; ensemble adds vote-redundancy.

---

## CROSS-THREAD SYNTHESIS

**With prior META atom `meta::META_codebook_NN_cleanup_is_load_bearing_for_substrate_*`:** confirmed; cleanup remains the bottleneck across n4/n9/n10/p1. The att1 rejection narrows the failure mode: it's NOT that iterative refinement is needed -- it's that iterative refinement ON THE SAME ENERGY LANDSCAPE is insufficient. Revival must change the DYNAMICS CLASS (residual-shrinkage, ensemble-over-inits, or radius-averaging) or change the LANDSCAPE (encoder upstream of cleanup).

**With prior research drill `research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22`:** mech 5 (CAN attractors) tested via att1 v1+v2 -> rejected; the broad-drill correctly identified the family but the SPECIFIC variant (Ramsauer + Krotov) was the wrong member. Multi-bump CAN is the missing member.

**With prior negative `research_2x_revival_overnight_negatives_2026-06-23`:** that 2x drill correctly identified Krotov-dense as a revival angle (P=0.35); v2 cell ran it; full 3-seed result is now in -- rejected. The 2x analysis was right to dispatch, the experiment was right to run, the negative is informative: it RULES OUT iterative-attractor as a family, freeing capacity for the structurally-different OMP and multi-bump CAN.

**With existing primitives (`hdlab/iterative_attractor.py`):** the iterative_attractor primitive is now confirmed null for cleanup. Recommend: KEEP the code (it's correct; it may help in OTHER contexts like sequence-binding state evolution where argmax isn't the baseline), but ANNOTATE the docstring with the 2026-06-22 att1 v1+v2 HARD_FAIL finding so future cells don't re-attempt cleanup-via-this-primitive.

**With chain-grade primitives already shipped:** n11 RI ternary indices are conceptually closest to SDM-radius readout (#3); already in flight. Multi-bump CAN (#2) builds directly on existing iterative_attractor.py. OMP (#1) needs new dictionary-projection primitive but composes with existing codebook.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**If OMP cleanup HARD_PASSES (P=0.45):**
- n4 k-WTA-VQ regains a viable cleanup path at high noise -> unblocks Path A V_C=4096 ceiling
- n9 sparsemax-decode + OMP composition opens new compositional-decode capability (k-sparse decomposition of polysemous cues -- "Paris" cue could decode to both {capital, France} simultaneously)
- n10 whitening + OMP gives upper-bound on bigram-gap closure via downstream-only improvements
- p1 phase-action: OMP-residual gives an explicit notion of "phase margin" (residual norm = distance from any basin)
- New hdlab primitive: `omp_cleanup(query, codebook, k_max)` -- substrate-flat 2-function file
- META atom: `cleanup_is_residual_shrinkage_not_similarity_iteration` -- reframes the entire "cleanup is load-bearing" stance

**If OMP cleanup HARD_FAILS:**
- Cleanup-mechanism family rejected as a CLASS for current substrate regime (att1 + OMP cover the two major axes: fixed-point dynamics + residual-shrinkage)
- Conclusion: substrate's noise problem at sigma=1.50 is STRUCTURAL -- must be addressed upstream (encoder lift to N=4096; whitening; sparsified encoding)
- Refocus product roadmap on encoder-side improvements, deprioritize cleanup-side experimentation
- META atom: `cleanup_ceiling_at_argmax_is_information_theoretic_not_decoder_limited`

**If MIDDLE_BAND:** dispatch multi-bump CAN (#2) as orthogonal-axis follow-up before declaring family-rejection.

---

## CITATIONS (verified)

1. Saxena & Bartlett 2024 arXiv:2212.01196 "VSA Finite State Machines in Attractor Neural Networks" (broad-drill citation; confirmed iterative-attractor family for VSA)
2. Ramsauer et al. 2021 ICLR "Hopfield Networks Is All You Need" (modern-Hopfield softmax-attractor)
3. Krotov-Hopfield 2016 NeurIPS "Dense Associative Memory" (polynomial/exp interactions)
4. Multiple bumps in CAN: Faugeras et al. 2022 PLOS Comp Bio 1010547 + 2026 Frontiers Network Physiology 1693772 (multi-bump robustness lit-precedent)
5. Back to the Continuous Attractor: NeurIPS 2024 (S-type / D-type noise classification)
6. Population coding & self-organized ring attractors: PMC12615411 / Frontiers 2025 1693772
7. SDM Kanerva 1988 (Sparse Distributed Memory original); Wikipedia + grokipedia + emergentmind survey
8. SDM modified for noisy patterns: ResearchGate 221532762
9. Tropp & Gilbert 2007 + later (OMP under RIP; arxiv 1005.2249 sparse recovery under RIP)
10. OMP empirical analysis: IEEE 10207984 "Analysis of OMP in Practical Settings"
11. OMP teaching reference: Utah CS5140-S17 L17-OMP
12. Patterson-Rogers ATL hub-spoke: PLOS ONE pone.0169269 + multiple PMC reviews
13. Bayesian MAP / high-D inference: arxiv 1601.04650 "Statistical Mechanics of High-Dimensional Inference"
14. Cerebellar microzones: Springer 10.1007/s12311-018-0952-3 + PLOS Comp Bio 1011277 eyeblink

**Verified count: 14 sources spanning 6 candidate-mechanism families.**

---

## OPERATIONAL DRILL SUMMARY

- **Dispatch immediately:** OMP/sparse-coding cleanup (P=0.45, ~1hr impl+smoke, structurally orthogonal to att1)
- **Dispatch second (if OMP MIDDLE_BAND or as parallel):** Multi-bump CAN ensemble (P=0.40, ~40min impl+smoke, reuses iterative_attractor.py)
- **Annotate:** existing `hdlab/iterative_attractor.py` docstring with att1 v1+v2 HARD_FAIL finding so future cells don't re-attempt
- **Deprioritize:** Bayesian-MAP (#5) and reservoir-of-modules (#6) -- P_deflated 0.20 each
- **Reserve for future:** SDM radius-readout (#3, P=0.35) and hub-spoke 2-tier (#4, P=0.30) as orthogonal-axis follow-ups if #1+#2 both fail

**If #1 + #2 both HARD_FAIL:** the cleanup-family-rejection conclusion holds and substrate-product roadmap pivots to encoder-side upstream interventions per "Substrate-product implications if HARD_FAIL" branch above.
