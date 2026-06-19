# Pre-registration: wave14s_chargeflip_forensics_v1

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14s_chargeflip_forensics_v1.py](../experiments/exp_wave14s_chargeflip_forensics_v1.py)
Priority source: [active_priorities.md](../notes/active_priorities.md) Bet 3 (E3)
Author: experiment_dev session, cycle 4

## Why

Bet 3 in `active_priorities.md` is the random-key forensics extension. The
substrate currently has 🟢-validated WHT-peak forensics for **structured**
keys (Hadamard) — `wave14walsh_peaks_extended` showed 100% recall at every
tested K up through K=4000. For **random** keys the established baseline
is naive SVD recovery: `wave14forensics_svd_recovery` results land at
cos(recovered_v, true_v) ≈ 0.09 at high K. The Bet 3 target is to close
that gap to cos ≥ 0.3 via iterative refinement.

Research R1 noted that iterative charge-flipping (Oszlanyi-Suto 2004) is
fundamentally a phase-retrieval algorithm — well-fitted to *forensics*
(find atoms given W) but ill-fitted to *erase* (find the side-effect
minimizer given a target). v1 implements the forensics use, which is
where the algorithm belongs.

## v1 implementation note (honesty)

"Charge-flipping" as the literal Oszlanyi-Suto algorithm assumes Fourier
amplitudes known + phases unknown. Our substrate has W fully known. The
v1 implementation is therefore the **iterative sign-projection refinement**
that is the morally-equivalent algorithm for our setting:
- Initialize from SVD top-K
- Alternate {±1} projection of v then k, recompute W_hat, refine residual
- This is what R1's "charge flipping in the substrate setting" reduces to
  on first iteration when target is known

If the v1 finding is interesting, v2 can layer in a true sparsity-in-some-
basis step (R1's Sayre-equation variant) to test whether classical
crystallographic charge flipping adds anything beyond sign projection.

## Hypothesis

Iterative sign-projection refinement of SVD recovery improves
cos(recovered_v, true_v) at high K (K ≥ 1000) by at least 0.2 absolute
over the SVD baseline, with a positive gain monotone in iteration count
until convergence.

## Multi-probe success criteria (all required for PASS)

At N=4096, K ∈ {50, 200, 500, 1000, 2000}, 3 seeds each:

1. SVD baseline mean cos at K=2000 < 0.15 (replicates the established
   gap; if not, the baseline isn't what the cap_map claims)
2. CF-from-SVD-init mean cos at K=2000 > SVD baseline + 0.20 (the target
   improvement)
3. Iteration-to-convergence count < 200 iters at all K (the algorithm is
   practical, not just theoretically correct)
4. CF alone (random init, no SVD) mean cos at K=2000 ≥ 0.10 (sanity:
   even without SVD warm start, CF should make some progress)
5. key-index recall@10 (top-10 recovered atoms by cos vs truth top-10) at
   K=500 ≥ 0.70 (most of the high-rank atoms recovered)

## Kill criterion

CF-from-SVD-init mean cos at K=2000 ≤ SVD baseline + 0.05 (less than
0.05 improvement = within seed noise of the SVD baseline). Means
iterative refinement adds nothing for random keys → random-key forensics
stays 🔬 at "SVD-only" capability; product story remains "auditable IFF
structured keys."

## Verdict labels (5)

- `CHARGEFLIP_FORENSICS_PASS` — all 5 criteria pass; CF closes the SVD gap
- `CHARGEFLIP_FORENSICS_MARGINAL` — passes criteria 1-3, recall@10 < 0.70
  (atoms partially recovered)
- `CHARGEFLIP_FORENSICS_NO_GAIN` — kill criterion triggered; CF ≈ SVD
- `CHARGEFLIP_NONCONVERGENT` — iter count > 200 at any K (algorithm impractical)
- `CHARGEFLIP_FORENSICS_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. `oracle.assert_in_range("svd_cos_low_K", svd_cos_at_K50, (0.5, 1.0))`
   — at low K, SVD must work well; if not, the comparison baseline is broken
2. `oracle.assert_in_range("cf_iter_count_smoke", smoke_iter_count, (1.0, 50.0))`
   — CF must converge within smoke iteration budget; if it loops without
   progress, algorithm bug
3. `oracle.assert_distinguishable("cf_vs_svd_smoke", cf_cos_smoke, svd_cos_smoke, min_gap=0.0)`
   — at smoke scale, CF and SVD must give measurably different cos (any
   gap; tightens to ≥0.20 in full mode)

## Pre-mortem (3 failure causes)

1. **SVD recovery is permutation-and-sign-ambiguous**; cos against truth
   requires Hungarian assignment + sign flip. Naive comparison gives ~0
   even when recovery is perfect. Mitigation: use scipy or hand-rolled
   bipartite matching on |cos| matrix, then flip signs to match. Smoke
   oracle 1 catches this.
2. **CF iteration doesn't improve over SVD because SVD is already at
   the rank-K limit of W**. For W = Σ v_i k_i^T with K random ±1 atoms,
   SVD top-K span IS the subspace spanned by the truth atoms. The
   improvement only comes from {±1}-projection. If atoms are nearly
   linearly dependent (high K close to N), SVD basis is rotated away from
   the truth atoms and {±1}-projection alone can't recover. Mitigation:
   verdict `CHARGEFLIP_FORENSICS_NO_GAIN` captures this; routes to
   genuine charge-flipping in some sparser basis as a follow-up.
3. **CF runaway**: bad initialization could send {±1}-projection into a
   spurious fixed point with poor cos to truth. Mitigation: report
   iter count + cos trajectory; oracle 2 catches runaway loops.

## Operational definition

- N=4096
- K ∈ {50, 200, 500, 1000, 2000} (the active_priorities recipe)
- seeds = [17, 23, 31] (3-seed; this is exploratory follow-up not a primary
  promotion test, so reduced from the playbook's 5-seed promotion-grade)
- W = Σ v_i k_i^T / N (Hebbian outer product, random ±1 keys/values)
- SVD baseline:
  - U, S, Vh = torch.linalg.svd(W, full_matrices=False)
  - V_svd = sign(U[:, :K]) ∈ {±1}^{N×K}
  - K_svd = sign(Vh[:K, :].T) ∈ {±1}^{N×K}
  - Hungarian-match V_svd columns to truth V columns (using |cos| matrix)
  - Sign-flip to maximize cos
- Iterative refinement (CF) — 100 iter budget, threshold 1e-4 change:
  - For iter t:
    - K_hat = sign(V_hat.T @ W)
    - V_hat = sign(W @ K_hat / (K_hat ** 2).sum(0))  — least-squares + sign
    - cos_change = mean cosine between V_hat[t] and V_hat[t-1]
    - if 1 - cos_change < 1e-4: stop
- "CF from SVD": V_hat init = V_svd, K_hat init = K_svd
- "CF random": V_hat init = random ±1, K_hat init = random ±1
- Metric: mean over columns of cos(V_hat_matched, V_true) per K

## Cited mechanism / sources

1. Oszlanyi, Suto (2004). "Ab initio structure solution by charge
   flipping." *Acta Cryst.* A60: 134-141. — Original algorithm; v1
   implements the morally-equivalent sign-projection refinement (see
   honesty note above).
2. Brachat et al. (2010). "Symmetric tensor decomposition." *Lin Alg
   Appl* 433. — Theoretical floor for K-atom decomposition: when K is
   well below rank capacity, decomposition is essentially unique up to
   permutation and sign.
3. wave14forensics_svd_recovery (own work): SVD-baseline result this
   experiment improves on.
4. Hungarian algorithm (Kuhn 1955): for permutation-matching recovered
   atoms to truth atoms.

## Expected runtime

- Smoke (N=512, K=20, 1 seed): ~3-6s on CPU
- Full (N=4096, K up to 2000, 3 seeds, 3 methods: SVD, CF-rand, CF-svd):
  estimated 3-8 min on workstation GPU. SVD at N=4096 is ~5s/call; ~15
  SVDs total. Iterative refinement ~50 iters × cheap matmul.

## What product decision this enables

- `PASS` → cap_map row "random-key forensics" upgrades from 🔬 → 🟢; the
  "auditable substrate" claim no longer requires structured keys.
- `NO_GAIN` → random-key forensics stays 🔬 at SVD-only; "auditable IFF
  structured keys" stands as a product caveat.
- `MARGINAL` → upgrade to 🟡 with caveat; routes to follow-up that drills
  why some atoms recover and others don't (capacity? key collision?).
